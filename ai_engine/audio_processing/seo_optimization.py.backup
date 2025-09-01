"""SEO & Content Optimization Engine for Audio Content
Professional SEO analytics and optimization for content creators and influencers.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️ 
This code, concept, and intellectual property belongs exclusively to Fahed Mlaiel.
ANY unauthorized use, reproduction, distribution, or theft of this code/concept 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is 
STRICTLY PROHIBITED and will result in immediate legal action.
All rights reserved. Patent pending.
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import json
import numpy as np
from abc import ABC, abstractmethod
import re
from urllib.parse import urlparse, urljoin
import hashlib
import requests
from bs4 import BeautifulSoup
import spacy
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
from concurrent.futures import ThreadPoolExecutor
import yake
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content types for SEO optimization"""
    MUSIC = "music"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    VOICE_OVER = "voice_over"
    INTERVIEW = "interview"
    LIVE_STREAM = "live_stream"
    SOUND_EFFECT = "sound_effect"
    MEDITATION = "meditation"


class PlatformType(Enum):
    """Target platforms for optimization"""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    SOUNDCLOUD = "soundcloud"
    APPLE_MUSIC = "apple_music"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    BANDCAMP = "bandcamp"


class SEOMetric(Enum):
    """SEO performance metrics"""
    KEYWORD_DENSITY = "keyword_density"
    TITLE_OPTIMIZATION = "title_optimization"
    DESCRIPTION_QUALITY = "description_quality"
    TAG_RELEVANCE = "tag_relevance"
    ENGAGEMENT_POTENTIAL = "engagement_potential"
    DISCOVERABILITY = "discoverability"
    COMPETITION_LEVEL = "competition_level"
    TRENDING_ALIGNMENT = "trending_alignment"


@dataclass
class KeywordData:
    """Keyword analysis data"""
    keyword: str
    search_volume: int
    competition: float  # 0.0 to 1.0
    cpc: Optional[float] = None
    trend: Optional[str] = None
    related_keywords: List[str] = field(default_factory=list)
    difficulty: Optional[float] = None
    relevance_score: float = 0.0


@dataclass
class ContentMetadata:
    """Comprehensive content metadata"""
    title: str
    description: str
    tags: List[str]
    genre: Optional[str] = None
    duration: Optional[float] = None
    language: str = "en"
    artist_name: Optional[str] = None
    album_name: Optional[str] = None
    release_date: Optional[datetime] = None
    cover_art_url: Optional[str] = None
    explicit: bool = False
    collaborators: List[str] = field(default_factory=list)


@dataclass
class SEOAnalysisResult:
    """SEO analysis result"""
    overall_score: float  # 0-100
    metric_scores: Dict[SEOMetric, float]
    keywords: List[KeywordData]
    recommendations: List[str]
    optimized_title: Optional[str] = None
    optimized_description: Optional[str] = None
    optimized_tags: List[str] = field(default_factory=list)
    competition_analysis: Dict[str, Any] = field(default_factory=dict)
    trending_opportunities: List[str] = field(default_factory=list)


@dataclass
class PlatformOptimization:
    """Platform-specific optimization data"""
    platform: PlatformType
    optimized_metadata: ContentMetadata
    platform_specific_tips: List[str]
    hashtag_recommendations: List[str] = field(default_factory=list)
    posting_schedule: Optional[Dict[str, Any]] = None
    thumbnail_suggestions: List[str] = field(default_factory=list)


class KeywordResearchEngine:
    """Advanced keyword research and analysis"""
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.nlp = self._load_nlp_model()
        self.keyword_extractor = yake.KeywordExtractor(
            lan="en",
            n=3,
            dedupLim=0.7,
            top=20
        )
        
    def _load_nlp_model(self):
        """Load NLP model for text analysis"""
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found, using basic analysis")
            return None
    
    async def research_keywords(self, 
                              seed_keywords: List[str],
                              content_type: ContentType,
                              target_platforms: List[PlatformType]) -> List[KeywordData]:
        """Research keywords for content optimization"""
        try:
            all_keywords = []
            
            # Extract keywords from seed
            extracted_keywords = await self._extract_related_keywords(seed_keywords)
            all_keywords.extend(extracted_keywords)
            
            # Get trending keywords by platform
            for platform in target_platforms:
                trending = await self._get_trending_keywords(platform, content_type)
                all_keywords.extend(trending)
            
            # Analyze keyword metrics
            analyzed_keywords = []
            for keyword in all_keywords:
                keyword_data = await self._analyze_keyword(keyword, content_type)
                if keyword_data:
                    analyzed_keywords.append(keyword_data)
            
            # Remove duplicates and sort by relevance
            unique_keywords = self._deduplicate_keywords(analyzed_keywords)
            unique_keywords.sort(key=lambda k: k.relevance_score, reverse=True)
            
            return unique_keywords[:50]  # Return top 50 keywords
            
        except Exception as e:
            logger.error(f"Keyword research failed: {e}")
            return []
    
    async def _extract_related_keywords(self, seed_keywords: List[str]) -> List[str]:
        """Extract related keywords using NLP"""
        try:
            related_keywords = set()
            
            for keyword in seed_keywords:
                # Use YAKE for keyword extraction
                keywords = self.keyword_extractor.extract_keywords(keyword)
                for kw, score in keywords:
                    if score < 0.1:  # Lower score = better keyword
                        related_keywords.add(kw.lower())
                
                # Use spaCy for semantic similarity if available
                if self.nlp:
                    doc = self.nlp(keyword)
                    for token in doc:
                        if token.pos_ in ['NOUN', 'ADJ'] and len(token.text) > 2:
                            related_keywords.add(token.lemma_.lower())
            
            return list(related_keywords)
            
        except Exception as e:
            logger.error(f"Related keyword extraction failed: {e}")
            return []
    
    async def _get_trending_keywords(self, 
                                   platform: PlatformType,
                                   content_type: ContentType) -> List[str]:
        """Get trending keywords for specific platform"""
        try:
            # Platform-specific trending keyword sources
            trending_sources = {
                PlatformType.YOUTUBE: self._get_youtube_trending,
                PlatformType.SPOTIFY: self._get_spotify_trending,
                PlatformType.TIKTOK: self._get_tiktok_trending,
                PlatformType.INSTAGRAM: self._get_instagram_trending,
                PlatformType.TWITTER: self._get_twitter_trending
            }
            
            if platform in trending_sources:
                return await trending_sources[platform](content_type)
            
            return []
            
        except Exception as e:
            logger.error(f"Trending keywords for {platform.value} failed: {e}")
            return []
    
    async def _get_youtube_trending(self, content_type: ContentType) -> List[str]:
        """Get YouTube trending keywords"""
        # In real implementation, use YouTube API
        music_trending = [
            "new music 2025", "viral song", "hit single", "music video",
            "cover song", "remix", "acoustic version", "live performance",
            "original song", "indie music", "pop music", "rock music"
        ]
        
        podcast_trending = [
            "podcast 2025", "interview", "discussion", "story telling",
            "true crime", "business podcast", "educational content",
            "motivational", "self improvement", "news analysis"
        ]
        
        trending_map = {
            ContentType.MUSIC: music_trending,
            ContentType.PODCAST: podcast_trending
        }
        
        return trending_map.get(content_type, music_trending)
    
    async def _get_spotify_trending(self, content_type: ContentType) -> List[str]:
        """Get Spotify trending keywords"""
        return [
            "playlist worthy", "chill vibes", "workout music", "study music",
            "road trip songs", "party playlist", "relaxing music", "focus music",
            "mood music", "seasonal music", "throwback", "feel good music"
        ]
    
    async def _get_tiktok_trending(self, content_type: ContentType) -> List[str]:
        """Get TikTok trending hashtags/keywords"""
        return [
            "viral sound", "trending audio", "challenge", "duet",
            "dance music", "meme sound", "funny audio", "emotional",
            "motivational", "inspiring", "relatable", "aesthetic"
        ]
    
    async def _get_instagram_trending(self, content_type: ContentType) -> List[str]:
        """Get Instagram trending keywords"""
        return [
            "behind the scenes", "studio session", "creative process",
            "artist life", "music creation", "inspiration", "collaboration",
            "new release", "coming soon", "exclusive", "limited edition"
        ]
    
    async def _get_twitter_trending(self, content_type: ContentType) -> List[str]:
        """Get Twitter trending topics"""
        return [
            "new music friday", "artist spotlight", "music discovery",
            "independent artist", "music industry", "streaming", "viral",
            "breakthrough artist", "music news", "album release"
        ]
    
    async def _analyze_keyword(self, keyword: str, content_type: ContentType) -> Optional[KeywordData]:
        """Analyze individual keyword metrics"""
        try:
            # Simulate keyword analysis (in real implementation, use SEO APIs)
            search_volume = self._estimate_search_volume(keyword, content_type)
            competition = self._estimate_competition(keyword)
            difficulty = self._estimate_difficulty(keyword)
            relevance = self._calculate_relevance(keyword, content_type)
            
            return KeywordData(
                keyword=keyword,
                search_volume=search_volume,
                competition=competition,
                difficulty=difficulty,
                relevance_score=relevance,
                related_keywords=await self._get_related_keywords(keyword)
            )
            
        except Exception as e:
            logger.error(f"Keyword analysis failed for '{keyword}': {e}")
            return None
    
    def _estimate_search_volume(self, keyword: str, content_type: ContentType) -> int:
        """Estimate search volume for keyword"""
        # Simplified estimation based on keyword characteristics
        base_volume = 1000
        
        # Adjust for keyword length
        if len(keyword.split()) == 1:
            base_volume *= 2
        elif len(keyword.split()) > 3:
            base_volume *= 0.5
        
        # Adjust for content type
        if content_type == ContentType.MUSIC:
            base_volume *= 1.5
        elif content_type == ContentType.PODCAST:
            base_volume *= 1.2
        
        # Add some randomness for realism
        import random
        variation = random.uniform(0.7, 1.3)
        
        return int(base_volume * variation)
    
    def _estimate_competition(self, keyword: str) -> float:
        """Estimate competition level for keyword"""
        # Simple heuristic based on keyword characteristics
        common_words = {'music', 'song', 'new', 'best', 'top', 'playlist'}
        
        keyword_words = set(keyword.lower().split())
        common_count = len(keyword_words.intersection(common_words))
        
        # More common words = higher competition
        competition = min(0.1 + (common_count * 0.2), 1.0)
        
        return competition
    
    def _estimate_difficulty(self, keyword: str) -> float:
        """Estimate SEO difficulty for keyword"""
        # Simplified difficulty estimation
        word_count = len(keyword.split())
        
        if word_count == 1:
            return 0.8  # Single words are usually difficult
        elif word_count == 2:
            return 0.6
        elif word_count == 3:
            return 0.4
        else:
            return 0.3  # Long-tail keywords are easier
    
    def _calculate_relevance(self, keyword: str, content_type: ContentType) -> float:
        """Calculate relevance score for content type"""
        relevance_keywords = {
            ContentType.MUSIC: {'music', 'song', 'artist', 'album', 'track', 'sound', 'audio', 'melody', 'rhythm', 'beat'},
            ContentType.PODCAST: {'podcast', 'episode', 'interview', 'discussion', 'talk', 'story', 'conversation', 'audio', 'listen'},
            ContentType.AUDIOBOOK: {'audiobook', 'book', 'story', 'narrator', 'chapter', 'listen', 'audio', 'reading'},
        }
        
        content_keywords = relevance_keywords.get(content_type, set())
        keyword_words = set(keyword.lower().split())
        
        overlap = len(keyword_words.intersection(content_keywords))
        total_words = len(keyword_words)
        
        if total_words == 0:
            return 0.0
        
        return overlap / total_words
    
    async def _get_related_keywords(self, keyword: str) -> List[str]:
        """Get related keywords for a given keyword"""
        try:
            if self.nlp:
                doc = self.nlp(keyword)
                related = []
                
                for token in doc:
                    if token.pos_ in ['NOUN', 'ADJ']:
                        # Get similar words (simplified)
                        if hasattr(token, 'similarity'):
                            related.append(token.lemma_)
                
                return related[:5]
            
            return []
            
        except Exception as e:
            logger.error(f"Related keywords extraction failed: {e}")
            return []
    
    def _deduplicate_keywords(self, keywords: List[KeywordData]) -> List[KeywordData]:
        """Remove duplicate keywords"""
        seen = set()
        unique_keywords = []
        
        for keyword_data in keywords:
            normalized = keyword_data.keyword.lower().strip()
            if normalized not in seen:
                seen.add(normalized)
                unique_keywords.append(keyword_data)
        
        return unique_keywords


class SEOAnalyzer:
    """Comprehensive SEO analysis engine"""
    
    def __init__(self, keyword_engine: KeywordResearchEngine):
        self.keyword_engine = keyword_engine
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        
    async def analyze_content_seo(self,
                                metadata: ContentMetadata,
                                content_type: ContentType,
                                target_platforms: List[PlatformType]) -> SEOAnalysisResult:
        """Perform comprehensive SEO analysis"""
        try:
            # Research keywords
            seed_keywords = [metadata.title] + metadata.tags
            if metadata.artist_name:
                seed_keywords.append(metadata.artist_name)
            
            keywords = await self.keyword_engine.research_keywords(
                seed_keywords, content_type, target_platforms
            )
            
            # Analyze different SEO aspects
            metric_scores = {}
            
            # Title optimization
            metric_scores[SEOMetric.TITLE_OPTIMIZATION] = self._analyze_title(
                metadata.title, keywords
            )
            
            # Description quality
            metric_scores[SEOMetric.DESCRIPTION_QUALITY] = self._analyze_description(
                metadata.description, keywords
            )
            
            # Tag relevance
            metric_scores[SEOMetric.TAG_RELEVANCE] = self._analyze_tags(
                metadata.tags, keywords
            )
            
            # Keyword density
            metric_scores[SEOMetric.KEYWORD_DENSITY] = self._analyze_keyword_density(
                metadata, keywords
            )
            
            # Engagement potential
            metric_scores[SEOMetric.ENGAGEMENT_POTENTIAL] = await self._analyze_engagement_potential(
                metadata, content_type
            )
            
            # Discoverability
            metric_scores[SEOMetric.DISCOVERABILITY] = self._analyze_discoverability(
                metadata, keywords, target_platforms
            )
            
            # Calculate overall score
            overall_score = sum(metric_scores.values()) / len(metric_scores)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                metadata, metric_scores, keywords
            )
            
            # Generate optimizations
            optimized_title = self._optimize_title(metadata.title, keywords)
            optimized_description = self._optimize_description(metadata.description, keywords)
            optimized_tags = self._optimize_tags(metadata.tags, keywords)
            
            # Competition analysis
            competition_analysis = await self._analyze_competition(
                metadata, keywords, target_platforms
            )
            
            # Trending opportunities
            trending_opportunities = self._identify_trending_opportunities(
                keywords, target_platforms
            )
            
            return SEOAnalysisResult(
                overall_score=overall_score,
                metric_scores=metric_scores,
                keywords=keywords,
                recommendations=recommendations,
                optimized_title=optimized_title,
                optimized_description=optimized_description,
                optimized_tags=optimized_tags,
                competition_analysis=competition_analysis,
                trending_opportunities=trending_opportunities
            )
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
            return SEOAnalysisResult(
                overall_score=0.0,
                metric_scores={},
                keywords=[],
                recommendations=[f"Analysis failed: {str(e)}"]
            )
    
    def _analyze_title(self, title: str, keywords: List[KeywordData]) -> float:
        """Analyze title optimization"""
        if not title:
            return 0.0
        
        score = 0.0
        
        # Length check (optimal: 50-60 characters)
        if 40 <= len(title) <= 70:
            score += 25
        elif 30 <= len(title) <= 80:
            score += 15
        else:
            score += 5
        
        # Keyword inclusion
        title_lower = title.lower()
        high_value_keywords = [k for k in keywords if k.relevance_score > 0.7][:5]
        
        for keyword_data in high_value_keywords:
            if keyword_data.keyword.lower() in title_lower:
                score += 15
        
        # Engagement factors
        engagement_words = ['new', 'exclusive', 'premiere', 'official', 'live', 'remix', 'cover']
        for word in engagement_words:
            if word in title_lower:
                score += 10
                break
        
        # Avoid keyword stuffing
        word_count = len(title.split())
        if word_count > 10:
            score -= 10
        
        return min(score, 100.0)
    
    def _analyze_description(self, description: str, keywords: List[KeywordData]) -> float:
        """Analyze description quality"""
        if not description:
            return 0.0
        
        score = 0.0
        
        # Length check (optimal: 150-300 characters)
        if 100 <= len(description) <= 400:
            score += 30
        elif 50 <= len(description) <= 500:
            score += 20
        else:
            score += 10
        
        # Keyword inclusion with natural density
        desc_lower = description.lower()
        keyword_matches = 0
        
        for keyword_data in keywords[:10]:  # Check top 10 keywords
            if keyword_data.keyword.lower() in desc_lower:
                keyword_matches += 1
        
        keyword_density = keyword_matches / max(len(keywords[:10]), 1)
        if 0.2 <= keyword_density <= 0.6:
            score += 30
        elif keyword_density > 0.6:
            score += 10  # Penalize keyword stuffing
        else:
            score += 20
        
        # Sentiment analysis
        try:
            sentiment = self.sentiment_analyzer(description[:512])[0]  # Limit text length
            if sentiment['label'] == 'POSITIVE' and sentiment['score'] > 0.7:
                score += 20
            elif sentiment['label'] == 'NEGATIVE' and sentiment['score'] > 0.7:
                score -= 10
        except Exception:
            pass
        
        # Call-to-action presence
        cta_phrases = ['listen', 'subscribe', 'follow', 'share', 'comment', 'like']
        for phrase in cta_phrases:
            if phrase in desc_lower:
                score += 10
                break
        
        return min(score, 100.0)
    
    def _analyze_tags(self, tags: List[str], keywords: List[KeywordData]) -> float:
        """Analyze tag relevance"""
        if not tags:
            return 0.0
        
        score = 0.0
        
        # Tag count (optimal: 5-15 tags)
        if 5 <= len(tags) <= 15:
            score += 25
        elif 3 <= len(tags) <= 20:
            score += 15
        else:
            score += 5
        
        # Keyword alignment
        keyword_set = {k.keyword.lower() for k in keywords}
        tag_matches = 0
        
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in keyword_set:
                tag_matches += 1
            
            # Check for partial matches
            for keyword in keyword_set:
                if keyword in tag_lower or tag_lower in keyword:
                    tag_matches += 0.5
                    break
        
        tag_relevance = tag_matches / len(tags)
        if tag_relevance >= 0.5:
            score += 35
        elif tag_relevance >= 0.3:
            score += 25
        else:
            score += 10
        
        # Tag diversity
        unique_concepts = len(set(tag.lower() for tag in tags))
        if unique_concepts == len(tags):  # All unique
            score += 20
        elif unique_concepts >= len(tags) * 0.8:
            score += 15
        else:
            score += 5
        
        # Avoid over-optimization
        total_chars = sum(len(tag) for tag in tags)
        if total_chars > 200:  # Potential spam
            score -= 20
        
        return min(score, 100.0)
    
    def _analyze_keyword_density(self, metadata: ContentMetadata, keywords: List[KeywordData]) -> float:
        """Analyze overall keyword density"""
        # Combine all text content
        all_text = f"{metadata.title} {metadata.description} {' '.join(metadata.tags)}"
        
        if not all_text.strip():
            return 0.0
        
        text_lower = all_text.lower()
        words = text_lower.split()
        total_words = len(words)
        
        if total_words == 0:
            return 0.0
        
        keyword_occurrences = 0
        for keyword_data in keywords[:20]:  # Check top 20 keywords
            keyword_words = keyword_data.keyword.lower().split()
            
            # Count exact matches
            for i in range(len(words) - len(keyword_words) + 1):
                if words[i:i+len(keyword_words)] == keyword_words:
                    keyword_occurrences += 1
        
        density = keyword_occurrences / total_words
        
        # Optimal density: 2-5%
        if 0.02 <= density <= 0.05:
            return 100.0
        elif 0.01 <= density <= 0.08:
            return 80.0
        elif density < 0.01:
            return 40.0  # Under-optimized
        else:
            return 20.0  # Over-optimized
    
    async def _analyze_engagement_potential(self, 
                                          metadata: ContentMetadata,
                                          content_type: ContentType) -> float:
        """Analyze potential for engagement"""
        score = 0.0
        
        # Title engagement factors
        title_lower = metadata.title.lower()
        engaging_words = [
            'new', 'exclusive', 'premiere', 'first', 'breaking', 'viral',
            'amazing', 'incredible', 'shocking', 'secrets', 'behind'
        ]
        
        for word in engaging_words:
            if word in title_lower:
                score += 10
        
        # Emotional words in description
        if metadata.description:
            emotional_words = [
                'love', 'passion', 'amazing', 'incredible', 'beautiful',
                'powerful', 'moving', 'inspiring', 'uplifting', 'emotional'
            ]
            
            desc_lower = metadata.description.lower()
            for word in emotional_words:
                if word in desc_lower:
                    score += 5
        
        # Content type specific factors
        if content_type == ContentType.MUSIC:
            music_engagement = [
                'live', 'acoustic', 'remix', 'cover', 'collaboration',
                'featuring', 'ft.', 'duet'
            ]
            
            combined_text = f"{metadata.title} {metadata.description}".lower()
            for term in music_engagement:
                if term in combined_text:
                    score += 15
        
        # Artist recognition (simplified)
        if metadata.artist_name:
            # Popular artist patterns (simplified check)
            if len(metadata.artist_name.split()) == 1:  # Single name artists tend to be established
                score += 20
        
        # Release timing
        if metadata.release_date:
            days_since_release = (datetime.now() - metadata.release_date).days
            if days_since_release <= 7:  # New release
                score += 25
            elif days_since_release <= 30:
                score += 15
        
        return min(score, 100.0)
    
    def _analyze_discoverability(self, 
                               metadata: ContentMetadata,
                               keywords: List[KeywordData],
                               platforms: List[PlatformType]) -> float:
        """Analyze content discoverability"""
        score = 0.0
        
        # Long-tail keyword usage
        long_tail_keywords = [k for k in keywords if len(k.keyword.split()) >= 3]
        if long_tail_keywords:
            score += 30
        
        # Genre specificity
        if metadata.genre:
            score += 15
            
            # Niche genres may have less competition
            niche_genres = ['ambient', 'experimental', 'folk', 'indie', 'acoustic']
            if metadata.genre.lower() in niche_genres:
                score += 10
        
        # Multi-platform optimization
        platform_specific_score = len(platforms) * 10
        score += min(platform_specific_score, 30)
        
        # Unique content indicators
        unique_indicators = ['original', 'exclusive', 'unreleased', 'premiere']
        combined_text = f"{metadata.title} {metadata.description}".lower()
        
        for indicator in unique_indicators:
            if indicator in combined_text:
                score += 15
                break
        
        # Low competition keywords
        low_competition_keywords = [k for k in keywords if k.competition < 0.5]
        if low_competition_keywords:
            competition_bonus = min(len(low_competition_keywords) * 5, 25)
            score += competition_bonus
        
        return min(score, 100.0)
    
    def _generate_recommendations(self, 
                                metadata: ContentMetadata,
                                metric_scores: Dict[SEOMetric, float],
                                keywords: List[KeywordData]) -> List[str]:
        """Generate SEO improvement recommendations"""
        recommendations = []
        
        # Title recommendations
        if metric_scores.get(SEOMetric.TITLE_OPTIMIZATION, 0) < 70:
            recommendations.append("Optimize title length (40-70 characters) and include primary keywords")
            
            top_keywords = [k.keyword for k in keywords[:3]]
            recommendations.append(f"Consider including these high-value keywords in title: {', '.join(top_keywords)}")
        
        # Description recommendations
        if metric_scores.get(SEOMetric.DESCRIPTION_QUALITY, 0) < 70:
            recommendations.append("Improve description with natural keyword inclusion and call-to-action")
            recommendations.append("Aim for 150-300 character description length")
        
        # Tag recommendations
        if metric_scores.get(SEOMetric.TAG_RELEVANCE, 0) < 70:
            recommendations.append("Use more relevant tags based on keyword research")
            
            suggested_tags = [k.keyword for k in keywords[:10] if k.relevance_score > 0.6]
            if suggested_tags:
                recommendations.append(f"Consider these tags: {', '.join(suggested_tags[:5])}")
        
        # Keyword density recommendations
        if metric_scores.get(SEOMetric.KEYWORD_DENSITY, 0) < 50:
            recommendations.append("Increase keyword usage naturally throughout title, description, and tags")
        elif metric_scores.get(SEOMetric.KEYWORD_DENSITY, 0) > 80:
            recommendations.append("Reduce keyword density to avoid over-optimization penalties")
        
        # Engagement recommendations
        if metric_scores.get(SEOMetric.ENGAGEMENT_POTENTIAL, 0) < 60:
            recommendations.append("Add more engaging elements like 'new', 'exclusive', or emotional words")
            recommendations.append("Include call-to-action phrases in description")
        
        # Discoverability recommendations
        if metric_scores.get(SEOMetric.DISCOVERABILITY, 0) < 60:
            recommendations.append("Target long-tail keywords for better discoverability")
            recommendations.append("Consider niche-specific optimization for less competitive keywords")
        
        # General recommendations
        if not metadata.genre:
            recommendations.append("Add genre information to improve categorization")
        
        if len(metadata.tags) < 5:
            recommendations.append("Add more relevant tags (aim for 8-12 tags)")
        
        return recommendations
    
    def _optimize_title(self, original_title: str, keywords: List[KeywordData]) -> str:
        """Generate optimized title"""
        if not keywords:
            return original_title
        
        # Get top keywords
        top_keywords = [k for k in keywords[:3] if k.relevance_score > 0.7]
        
        if not top_keywords:
            return original_title
        
        # Create optimized title
        primary_keyword = top_keywords[0].keyword
        
        # If primary keyword not in title, try to incorporate it
        if primary_keyword.lower() not in original_title.lower():
            # Try to prepend or append keyword naturally
            if len(f"{primary_keyword} - {original_title}") <= 70:
                return f"{primary_keyword} - {original_title}"
            elif len(f"{original_title} - {primary_keyword}") <= 70:
                return f"{original_title} - {primary_keyword}"
        
        return original_title
    
    def _optimize_description(self, original_description: str, keywords: List[KeywordData]) -> str:
        """Generate optimized description"""
        if not original_description:
            # Create basic description from keywords
            top_keywords = [k.keyword for k in keywords[:5]]
            return f"Listen to this amazing audio featuring: {', '.join(top_keywords)}. Don't forget to like and share!"
        
        # Add keywords naturally if missing
        desc_lower = original_description.lower()
        missing_keywords = [k.keyword for k in keywords[:3] 
                          if k.relevance_score > 0.8 and k.keyword.lower() not in desc_lower]
        
        if missing_keywords:
            keyword_addition = f" Features: {', '.join(missing_keywords[:2])}"
            optimized = original_description + keyword_addition
        else:
            optimized = original_description
        
        # Ensure call-to-action
        cta_phrases = ['listen', 'subscribe', 'follow', 'share', 'comment', 'like']
        has_cta = any(phrase in optimized.lower() for phrase in cta_phrases)
        
        if not has_cta:
            optimized += " Listen and share your thoughts!"
        
        return optimized
    
    def _optimize_tags(self, original_tags: List[str], keywords: List[KeywordData]) -> List[str]:
        """Generate optimized tags"""
        optimized_tags = list(original_tags)
        
        # Add missing high-value keywords as tags
        existing_tags_lower = [tag.lower() for tag in original_tags]
        
        for keyword_data in keywords[:15]:
            if (keyword_data.relevance_score > 0.6 and 
                keyword_data.keyword.lower() not in existing_tags_lower and
                len(optimized_tags) < 15):
                optimized_tags.append(keyword_data.keyword)
        
        return optimized_tags
    
    async def _analyze_competition(self, 
                                 metadata: ContentMetadata,
                                 keywords: List[KeywordData],
                                 platforms: List[PlatformType]) -> Dict[str, Any]:
        """Analyze competition for keywords and content"""
        try:
            high_competition = [k for k in keywords if k.competition > 0.7]
            medium_competition = [k for k in keywords if 0.4 <= k.competition <= 0.7]
            low_competition = [k for k in keywords if k.competition < 0.4]
            
            return {
                'high_competition_keywords': [k.keyword for k in high_competition],
                'medium_competition_keywords': [k.keyword for k in medium_competition],
                'low_competition_keywords': [k.keyword for k in low_competition],
                'recommended_strategy': self._recommend_competition_strategy(
                    high_competition, medium_competition, low_competition
                ),
                'niche_opportunities': [k.keyword for k in low_competition if k.search_volume > 500]
            }
            
        except Exception as e:
            logger.error(f"Competition analysis failed: {e}")
            return {}
    
    def _recommend_competition_strategy(self, 
                                     high_comp: List[KeywordData],
                                     medium_comp: List[KeywordData],
                                     low_comp: List[KeywordData]) -> str:
        """Recommend competition strategy"""
        if len(low_comp) > 5:
            return "Focus on low-competition keywords for quick wins"
        elif len(medium_comp) > len(high_comp):
            return "Target medium-competition keywords with strong content"
        else:
            return "High competition detected - focus on long-tail keywords and niche targeting"
    
    def _identify_trending_opportunities(self, 
                                       keywords: List[KeywordData],
                                       platforms: List[PlatformType]) -> List[str]:
        """Identify trending keyword opportunities"""
        trending = []
        
        # Look for keywords with high search volume but low competition
        opportunities = [
            k for k in keywords 
            if k.search_volume > 1000 and k.competition < 0.5
        ]
        
        for opportunity in opportunities[:5]:
            trending.append(f"Opportunity: '{opportunity.keyword}' - High volume ({opportunity.search_volume}), Low competition ({opportunity.competition:.2f})")
        
        return trending


class PlatformSpecificOptimizer:
    """Platform-specific optimization engine"""
    
    def __init__(self, seo_analyzer: SEOAnalyzer):
        self.seo_analyzer = seo_analyzer
        
        # Platform-specific configurations
        self.platform_configs = {
            PlatformType.YOUTUBE: {
                'title_length': (40, 60),
                'description_length': (150, 1000),
                'tags_count': (8, 12),
                'hashtag_limit': 15
            },
            PlatformType.SPOTIFY: {
                'title_length': (20, 50),
                'description_length': (100, 300),
                'tags_count': (3, 8),
                'playlist_keywords': True
            },
            PlatformType.SOUNDCLOUD: {
                'title_length': (30, 70),
                'description_length': (100, 500),
                'tags_count': (5, 15),
                'genre_important': True
            },
            PlatformType.TIKTOK: {
                'title_length': (20, 40),
                'description_length': (50, 150),
                'hashtags_critical': True,
                'trending_sounds': True
            },
            PlatformType.INSTAGRAM: {
                'title_length': (30, 50),
                'description_length': (100, 300),
                'hashtags_count': (20, 30),
                'story_optimization': True
            }
        }
    
    async def optimize_for_platform(self,
                                   metadata: ContentMetadata,
                                   platform: PlatformType,
                                   keywords: List[KeywordData]) -> PlatformOptimization:
        """Optimize content for specific platform"""
        try:
            config = self.platform_configs.get(platform, {})
            
            # Platform-specific metadata optimization
            optimized_metadata = self._optimize_metadata_for_platform(
                metadata, platform, config, keywords
            )
            
            # Generate platform-specific tips
            tips = self._generate_platform_tips(platform, metadata, keywords)
            
            # Generate hashtag recommendations
            hashtags = self._generate_hashtags(platform, keywords, metadata)
            
            # Generate posting schedule
            schedule = self._generate_posting_schedule(platform)
            
            # Generate thumbnail suggestions
            thumbnails = self._generate_thumbnail_suggestions(platform, metadata)
            
            return PlatformOptimization(
                platform=platform,
                optimized_metadata=optimized_metadata,
                platform_specific_tips=tips,
                hashtag_recommendations=hashtags,
                posting_schedule=schedule,
                thumbnail_suggestions=thumbnails
            )
            
        except Exception as e:
            logger.error(f"Platform optimization for {platform.value} failed: {e}")
            return PlatformOptimization(
                platform=platform,
                optimized_metadata=metadata,
                platform_specific_tips=[f"Optimization failed: {str(e)}"]
            )
    
    def _optimize_metadata_for_platform(self,
                                       metadata: ContentMetadata,
                                       platform: PlatformType,
                                       config: Dict[str, Any],
                                       keywords: List[KeywordData]) -> ContentMetadata:
        """Optimize metadata for specific platform"""
        optimized = ContentMetadata(
            title=metadata.title,
            description=metadata.description,
            tags=metadata.tags[:],  # Copy tags
            genre=metadata.genre,
            duration=metadata.duration,
            language=metadata.language,
            artist_name=metadata.artist_name,
            album_name=metadata.album_name,
            release_date=metadata.release_date,
            cover_art_url=metadata.cover_art_url,
            explicit=metadata.explicit,
            collaborators=metadata.collaborators[:]
        )
        
        # Platform-specific title optimization
        title_range = config.get('title_length', (30, 60))
        if len(optimized.title) < title_range[0] or len(optimized.title) > title_range[1]:
            optimized.title = self._adjust_title_length(
                optimized.title, title_range, keywords, platform
            )
        
        # Platform-specific description optimization
        desc_range = config.get('description_length', (100, 300))
        if len(optimized.description) < desc_range[0] or len(optimized.description) > desc_range[1]:
            optimized.description = self._adjust_description_length(
                optimized.description, desc_range, keywords, platform
            )
        
        # Platform-specific tag optimization
        tags_range = config.get('tags_count', (5, 12))
        if len(optimized.tags) < tags_range[0]:
            optimized.tags.extend(self._get_additional_tags(keywords, tags_range[0] - len(optimized.tags)))
        elif len(optimized.tags) > tags_range[1]:
            optimized.tags = optimized.tags[:tags_range[1]]
        
        return optimized
    
    def _adjust_title_length(self,
                           title: str,
                           length_range: Tuple[int, int],
                           keywords: List[KeywordData],
                           platform: PlatformType) -> str:
        """Adjust title length for platform requirements"""
        min_len, max_len = length_range
        
        if len(title) < min_len:
            # Add relevant keyword to extend
            relevant_keywords = [k.keyword for k in keywords[:3] if k.relevance_score > 0.7]
            for keyword in relevant_keywords:
                if keyword.lower() not in title.lower():
                    extended_title = f"{title} - {keyword}"
                    if len(extended_title) <= max_len:
                        return extended_title
        
        elif len(title) > max_len:
            # Truncate while preserving key information
            if ' - ' in title:
                main_part = title.split(' - ')[0]
                if min_len <= len(main_part) <= max_len:
                    return main_part
            
            # Truncate at word boundary
            words = title.split()
            truncated = ''
            for word in words:
                if len(truncated + ' ' + word) <= max_len - 3:
                    truncated += (' ' + word if truncated else word)
                else:
                    break
            
            return truncated + '...' if truncated else title[:max_len-3] + '...'
        
        return title
    
    def _adjust_description_length(self,
                                 description: str,
                                 length_range: Tuple[int, int],
                                 keywords: List[KeywordData],
                                 platform: PlatformType) -> str:
        """Adjust description length for platform requirements"""
        min_len, max_len = length_range
        
        if len(description) < min_len:
            # Extend with keyword-rich content
            extensions = [
                f"Keywords: {', '.join([k.keyword for k in keywords[:3]])}",
                "Don't forget to like, share, and subscribe!",
                f"Perfect for fans of {keywords[0].keyword if keywords else 'great music'}",
            ]
            
            for extension in extensions:
                extended = f"{description} {extension}"
                if len(extended) >= min_len:
                    return extended[:max_len]
        
        elif len(description) > max_len:
            # Truncate at sentence boundary if possible
            sentences = description.split('. ')
            truncated = ''
            
            for sentence in sentences:
                test_length = len(truncated + sentence + '. ')
                if test_length <= max_len - 10:
                    truncated += (sentence + '. ' if truncated else sentence + '. ')
                else:
                    break
            
            return truncated.strip() or description[:max_len-3] + '...'
        
        return description
    
    def _get_additional_tags(self, keywords: List[KeywordData], count: int) -> List[str]:
        """Get additional tags from keywords"""
        additional_tags = []
        
        for keyword_data in keywords:
            if len(additional_tags) >= count:
                break
            
            if keyword_data.relevance_score > 0.5 and len(keyword_data.keyword) <= 20:
                additional_tags.append(keyword_data.keyword)
        
        return additional_tags
    
    def _generate_platform_tips(self,
                              platform: PlatformType,
                              metadata: ContentMetadata,
                              keywords: List[KeywordData]) -> List[str]:
        """Generate platform-specific optimization tips"""
        tips = []
        
        if platform == PlatformType.YOUTUBE:
            tips.extend([
                "Create eye-catching thumbnail with high contrast colors",
                "Use timestamps in description for longer content",
                "Engage viewers in first 15 seconds",
                "Include relevant keywords in video filename",
                "Add end screens and cards for engagement"
            ])
        
        elif platform == PlatformType.SPOTIFY:
            tips.extend([
                "Target playlist curators with relevant genre tags",
                "Release on Fridays for maximum exposure",
                "Create artist playlist to showcase your style",
                "Use Spotify Canvas for visual appeal",
                "Submit to Spotify editorial playlists 4+ weeks in advance"
            ])
        
        elif platform == PlatformType.SOUNDCLOUD:
            tips.extend([
                "Engage with community through comments and reposts",
                "Use high-quality waveform visualization",
                "Enable downloading for increased engagement",
                "Post consistently to build following",
                "Collaborate with other SoundCloud artists"
            ])
        
        elif platform == PlatformType.TIKTOK:
            tips.extend([
                "Hook viewers in first 3 seconds",
                "Use trending sounds and hashtags",
                "Post when your audience is most active",
                "Create content that encourages duets/responses",
                "Keep videos between 15-60 seconds for best performance"
            ])
        
        elif platform == PlatformType.INSTAGRAM:
            tips.extend([
                "Use Stories to tease upcoming releases",
                "Post behind-the-scenes content regularly",
                "Use Instagram Reels for short music clips",
                "Engage with comments within first hour",
                "Cross-promote on IGTV for longer content"
            ])
        
        return tips
    
    def _generate_hashtags(self,
                         platform: PlatformType,
                         keywords: List[KeywordData],
                         metadata: ContentMetadata) -> List[str]:
        """Generate platform-specific hashtags"""
        hashtags = []
        
        # Base hashtags from keywords
        for keyword_data in keywords[:10]:
            # Convert to hashtag format
            hashtag = '#' + keyword_data.keyword.replace(' ', '').replace('-', '').lower()
            if len(hashtag) <= 30 and hashtag not in hashtags:
                hashtags.append(hashtag)
        
        # Platform-specific hashtags
        if platform == PlatformType.TIKTOK:
            hashtags.extend(['#fyp', '#foryou', '#viral', '#trending'])
        
        elif platform == PlatformType.INSTAGRAM:
            hashtags.extend(['#music', '#newmusic', '#artist', '#instamusic'])
        
        elif platform == PlatformType.TWITTER:
            hashtags.extend(['#NowPlaying', '#MusicMonday', '#NewMusicFriday'])
        
        # Genre-specific hashtags
        if metadata.genre:
            genre_hashtag = f"#{metadata.genre.lower().replace(' ', '')}"
            hashtags.append(genre_hashtag)
            
            # Add related genre hashtags
            genre_related = {
                'pop': ['#popsong', '#popmusic', '#mainstream'],
                'rock': ['#rockmusic', '#alternative', '#indie'],
                'electronic': ['#edm', '#electronicmusic', '#synth'],
                'hip-hop': ['#hiphop', '#rap', '#beats'],
                'jazz': ['#jazzmusic', '#smooth', '#instrumental']
            }
            
            related = genre_related.get(metadata.genre.lower(), [])
            hashtags.extend(related[:3])
        
        # Remove duplicates and limit based on platform
        unique_hashtags = list(dict.fromkeys(hashtags))  # Preserve order
        
        platform_limits = {
            PlatformType.INSTAGRAM: 30,
            PlatformType.TIKTOK: 15,
            PlatformType.TWITTER: 10,
            PlatformType.LINKEDIN: 5
        }
        
        limit = platform_limits.get(platform, 20)
        return unique_hashtags[:limit]
    
    def _generate_posting_schedule(self, platform: PlatformType) -> Dict[str, Any]:
        """Generate optimal posting schedule for platform"""
        schedules = {
            PlatformType.YOUTUBE: {
                'best_days': ['Friday', 'Saturday', 'Sunday'],
                'best_times': ['14:00-16:00', '18:00-20:00'],
                'frequency': '1-2 times per week',
                'notes': 'Friday releases perform well, weekend uploads get more views'
            },
            
            PlatformType.INSTAGRAM: {
                'best_days': ['Tuesday', 'Wednesday', 'Thursday'],
                'best_times': ['11:00-13:00', '17:00-19:00'],
                'frequency': '1-2 times per day',
                'notes': 'Post when your audience is most active, use Stories daily'
            },
            
            PlatformType.TIKTOK: {
                'best_days': ['Tuesday', 'Thursday', 'Sunday'],
                'best_times': ['06:00-10:00', '19:00-23:00'],
                'frequency': '1-4 times per day',
                'notes': 'Consistent posting is key, morning and evening peak times'
            },
            
            PlatformType.TWITTER: {
                'best_days': ['Wednesday', 'Thursday'],
                'best_times': ['09:00-10:00', '18:00-19:00'],
                'frequency': '3-5 times per day',
                'notes': 'Tweet during commute hours, engage in real-time'
            }
        }
        
        return schedules.get(platform, {
            'best_days': ['Tuesday', 'Wednesday', 'Thursday'],
            'best_times': ['12:00-14:00', '18:00-20:00'],
            'frequency': 'Daily',
            'notes': 'Adjust based on your audience analytics'
        })
    
    def _generate_thumbnail_suggestions(self,
                                      platform: PlatformType,
                                      metadata: ContentMetadata) -> List[str]:
        """Generate thumbnail/visual suggestions"""
        suggestions = []
        
        if platform == PlatformType.YOUTUBE:
            suggestions.extend([
                "Use bright, contrasting colors to stand out",
                "Include text overlay with main keyword",
                "Show emotional expressions or action",
                "Maintain consistent branding across thumbnails",
                "Use 1280x720 resolution for best quality"
            ])
        
        elif platform == PlatformType.SPOTIFY:
            suggestions.extend([
                "Create square album artwork (3000x3000px)",
                "Ensure artwork looks good at small sizes",
                "Use genre-appropriate color schemes",
                "Include artist name if not well-known",
                "Keep design clean and readable"
            ])
        
        elif platform == PlatformType.INSTAGRAM:
            suggestions.extend([
                "Use vertical video format (9:16) for Reels",
                "Create visually appealing cover images",
                "Maintain consistent aesthetic across posts",
                "Use brand colors and fonts",
                "Add captions or subtitles to videos"
            ])
        
        return suggestions


# Factory function for complete SEO system
async def create_seo_system(api_keys: Optional[Dict[str, str]] = None) -> Tuple[KeywordResearchEngine, SEOAnalyzer, PlatformSpecificOptimizer]:
    """Create complete SEO optimization system"""
    if api_keys is None:
        api_keys = {}
    
    keyword_engine = KeywordResearchEngine(api_keys)
    seo_analyzer = SEOAnalyzer(keyword_engine)
    platform_optimizer = PlatformSpecificOptimizer(seo_analyzer)
    
    return keyword_engine, seo_analyzer, platform_optimizer


# Convenience function for quick SEO analysis
async def quick_seo_analysis(
    title: str,
    description: str,
    tags: List[str],
    content_type: ContentType = ContentType.MUSIC,
    target_platforms: List[PlatformType] = None
) -> SEOAnalysisResult:
    """Perform quick SEO analysis"""
    if target_platforms is None:
        target_platforms = [PlatformType.YOUTUBE, PlatformType.SPOTIFY]
    
    metadata = ContentMetadata(
        title=title,
        description=description,
        tags=tags
    )
    
    _, seo_analyzer, _ = await create_seo_system()
    
    return await seo_analyzer.analyze_content_seo(
        metadata, content_type, target_platforms
    )
