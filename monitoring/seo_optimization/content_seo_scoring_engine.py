"""
Content SEO Scoring Engine - Enterprise Content SEO Analysis & Optimization

This module implements comprehensive content SEO scoring for the Ainflue platform,
providing real-time SEO analysis, content optimization recommendations, and automated SEO scoring.

Author: Fahed Mlaiel
Role: Lead Dev IA + SEO Expert + Content Strategist + ML Engineer
Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import requests
from urllib.parse import urlparse
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of content for SEO analysis"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    REEL = "reel"

class SEOScoreCategory(Enum):
    """SEO scoring categories"""
    TECHNICAL_SEO = "technical_seo"
    CONTENT_QUALITY = "content_quality"
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    METADATA_OPTIMIZATION = "metadata_optimization"
    SOCIAL_SIGNALS = "social_signals"
    PERFORMANCE_METRICS = "performance_metrics"
    ACCESSIBILITY = "accessibility"
    MOBILE_OPTIMIZATION = "mobile_optimization"

class OptimizationPriority(Enum):
    """SEO optimization priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class SEOMetrics:
    """SEO metrics for content"""
    title_score: float
    description_score: float
    keyword_density: float
    readability_score: float
    meta_tag_score: float
    image_alt_score: float
    url_structure_score: float
    internal_linking_score: float
    content_length_score: float
    freshness_score: float

@dataclass
class ContentSEOAnalysis:
    """Comprehensive SEO analysis for content"""
    content_id: str
    content_type: ContentType
    overall_seo_score: float
    category_scores: Dict[str, float]
    seo_metrics: SEOMetrics
    keyword_analysis: Dict[str, Any]
    optimization_recommendations: List[Dict[str, Any]]
    competitive_analysis: Dict[str, Any]
    trend_alignment: float
    social_seo_signals: Dict[str, Any]
    performance_prediction: Dict[str, Any]
    last_analyzed: datetime

@dataclass
class SEOOptimization:
    """SEO optimization recommendation"""
    optimization_id: str
    content_id: str
    category: SEOScoreCategory
    priority: OptimizationPriority
    recommendation: str
    implementation_steps: List[str]
    expected_impact: float
    effort_required: str
    automation_possible: bool
    tools_required: List[str]
    success_metrics: List[str]

class ContentSEOScoringEngine:
    """
    Enterprise content SEO scoring engine for Ainflue platform.
    
    Features:
    - Real-time SEO analysis and scoring
    - Multi-platform SEO optimization
    - Keyword optimization recommendations
    - Content quality assessment
    - Competitive SEO analysis
    - Automated optimization suggestions
    - Performance prediction
    - Trend alignment analysis
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize SEO scoring engine"""
        self.config = config or {}
        self.content_analyses: Dict[str, ContentSEOAnalysis] = {}
        self.seo_optimizations: List[SEOOptimization] = []
        self.keyword_database: Dict[str, Dict[str, Any]] = {}
        self.competitive_data: Dict[str, Any] = {}
        
        # SEO scoring weights and thresholds
        self.scoring_weights = {
            SEOScoreCategory.TECHNICAL_SEO: 0.20,
            SEOScoreCategory.CONTENT_QUALITY: 0.25,
            SEOScoreCategory.KEYWORD_OPTIMIZATION: 0.20,
            SEOScoreCategory.METADATA_OPTIMIZATION: 0.15,
            SEOScoreCategory.SOCIAL_SIGNALS: 0.10,
            SEOScoreCategory.PERFORMANCE_METRICS: 0.10
        }
        
        # Initialize scoring engine
        self._initialize_seo_engine()
        logger.info("Content SEO Scoring Engine initialized")
    
    def _initialize_seo_engine(self) -> None:
        """Initialize SEO scoring engine components"""
        try:
            # Setup keyword analysis tools
            self._setup_keyword_analysis()
            
            # Initialize content quality analyzers
            self._setup_content_analyzers()
            
            # Setup competitive analysis
            self._setup_competitive_analysis()
            
            # Initialize trend analysis
            self._setup_trend_analysis()
            
            logger.info("SEO scoring engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SEO engine: {e}")
            raise
    
    def _setup_keyword_analysis(self) -> None:
        """Setup keyword analysis tools"""
        self.keyword_tools = {
            "tfidf_vectorizer": TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 3)
            ),
            "keyword_density_threshold": 0.03,  # 3% max density
            "keyword_prominence_factor": 2.0,
            "semantic_similarity_threshold": 0.7
        }
        
        # Common SEO keywords and their weights
        self.seo_keywords = {
            "high_value": {
                "creator": 1.0, "content": 1.0, "viral": 0.9, "trending": 0.9,
                "influencer": 0.8, "engagement": 0.8, "social": 0.7
            },
            "medium_value": {
                "video": 0.6, "audio": 0.6, "platform": 0.5, "audience": 0.5,
                "followers": 0.5, "likes": 0.4, "shares": 0.4
            },
            "platform_specific": {
                "instagram": 0.6, "tiktok": 0.6, "youtube": 0.6, "twitter": 0.5,
                "linkedin": 0.5, "facebook": 0.4
            }
        }
    
    def _setup_content_analyzers(self) -> None:
        """Setup content quality analyzers"""
        self.content_analyzers = {
            "readability_formulas": ["flesch_kincaid", "gunning_fog", "smog"],
            "content_length_targets": {
                ContentType.VIDEO: {"min": 60, "optimal": 300, "max": 600},  # seconds
                ContentType.AUDIO: {"min": 120, "optimal": 600, "max": 1800},
                ContentType.TEXT: {"min": 300, "optimal": 800, "max": 2000},  # words
                ContentType.IMAGE: {"min": 50, "optimal": 150, "max": 300}   # description words
            },
            "quality_indicators": {
                "originality_threshold": 0.8,
                "engagement_rate_threshold": 0.05,
                "completion_rate_threshold": 0.7
            }
        }
    
    def _setup_competitive_analysis(self) -> None:
        """Setup competitive SEO analysis"""
        self.competitive_config = {
            "competitor_tracking_limit": 50,
            "keyword_overlap_threshold": 0.3,
            "content_similarity_threshold": 0.6,
            "performance_benchmark_period": 30  # days
        }
    
    def _setup_trend_analysis(self) -> None:
        """Setup trend analysis for SEO"""
        self.trend_config = {
            "trending_keywords_refresh": 3600,  # seconds
            "trend_weight_decay": 0.9,  # daily decay
            "trend_adoption_threshold": 0.6,
            "seasonal_adjustment": True
        }
    
    async def analyze_content_seo(self, content_id: str, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze content SEO and generate comprehensive scoring
        
        Args:
            content_id: Content identifier
            content_data: Content metadata and text
            
        Returns:
            Comprehensive SEO analysis and recommendations
        """
        try:
            # Extract content information
            content_type = ContentType(content_data.get("content_type", "text"))
            
            # Perform SEO analysis
            seo_metrics = await self._analyze_seo_metrics(content_data)
            
            # Calculate category scores
            category_scores = await self._calculate_category_scores(content_data, seo_metrics)
            
            # Analyze keywords
            keyword_analysis = await self._analyze_keywords(content_data)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(content_data, seo_metrics, category_scores)
            
            # Perform competitive analysis
            competitive_analysis = await self._perform_competitive_analysis(content_data, keyword_analysis)
            
            # Analyze trend alignment
            trend_alignment = await self._analyze_trend_alignment(content_data)
            
            # Analyze social SEO signals
            social_signals = await self._analyze_social_seo_signals(content_data)
            
            # Predict performance
            performance_prediction = await self._predict_seo_performance(seo_metrics, category_scores)
            
            # Calculate overall SEO score
            overall_score = await self._calculate_overall_seo_score(category_scores)
            
            # Create comprehensive analysis
            analysis = ContentSEOAnalysis(
                content_id=content_id,
                content_type=content_type,
                overall_seo_score=overall_score,
                category_scores=category_scores,
                seo_metrics=seo_metrics,
                keyword_analysis=keyword_analysis,
                optimization_recommendations=recommendations,
                competitive_analysis=competitive_analysis,
                trend_alignment=trend_alignment,
                social_seo_signals=social_signals,
                performance_prediction=performance_prediction,
                last_analyzed=datetime.now()
            )
            
            self.content_analyses[content_id] = analysis
            
            result = {
                "content_id": content_id,
                "overall_seo_score": overall_score,
                "grade": self._get_seo_grade(overall_score),
                "category_scores": category_scores,
                "top_recommendations": recommendations[:5],
                "keyword_optimization": keyword_analysis,
                "competitive_position": competitive_analysis.get("position", "unknown"),
                "trend_alignment": trend_alignment,
                "improvement_potential": self._calculate_improvement_potential(category_scores),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"SEO analysis completed for {content_id}: {overall_score:.3f} score, {len(recommendations)} recommendations")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze content SEO for {content_id}: {e}")
            return {"error": str(e)}
    
    async def _analyze_seo_metrics(self, content_data: Dict[str, Any]) -> SEOMetrics:
        """Analyze individual SEO metrics"""
        # Title analysis
        title = content_data.get("title", "")
        title_score = self._score_title_seo(title)
        
        # Description analysis
        description = content_data.get("description", "")
        description_score = self._score_description_seo(description)
        
        # Keyword density analysis
        content_text = self._extract_content_text(content_data)
        keyword_density = self._calculate_keyword_density(content_text)
        
        # Readability analysis
        readability_score = self._calculate_readability_score(content_text)
        
        # Meta tag analysis
        meta_tags = content_data.get("meta_tags", {})
        meta_tag_score = self._score_meta_tags(meta_tags)
        
        # Image alt text analysis
        images = content_data.get("images", [])
        image_alt_score = self._score_image_alt_texts(images)
        
        # URL structure analysis
        url = content_data.get("url", "")
        url_structure_score = self._score_url_structure(url)
        
        # Internal linking analysis
        links = content_data.get("internal_links", [])
        internal_linking_score = self._score_internal_linking(links)
        
        # Content length analysis
        content_length_score = self._score_content_length(content_data)
        
        # Content freshness analysis
        created_date = content_data.get("created_date", datetime.now())
        freshness_score = self._score_content_freshness(created_date)
        
        return SEOMetrics(
            title_score=title_score,
            description_score=description_score,
            keyword_density=keyword_density,
            readability_score=readability_score,
            meta_tag_score=meta_tag_score,
            image_alt_score=image_alt_score,
            url_structure_score=url_structure_score,
            internal_linking_score=internal_linking_score,
            content_length_score=content_length_score,
            freshness_score=freshness_score
        )
    
    def _score_title_seo(self, title: str) -> float:
        """Score title SEO optimization"""
        if not title:
            return 0.0
        
        score = 0.0
        
        # Length check (50-60 characters optimal)
        if 50 <= len(title) <= 60:
            score += 0.3
        elif 40 <= len(title) <= 70:
            score += 0.2
        else:
            score += 0.1
        
        # Keyword presence
        title_lower = title.lower()
        keyword_score = 0.0
        for category, keywords in self.seo_keywords.items():
            for keyword, weight in keywords.items():
                if keyword in title_lower:
                    keyword_score += weight * 0.1
        
        score += min(keyword_score, 0.4)
        
        # Title structure (capitalization, punctuation)
        if title[0].isupper():  # Starts with capital
            score += 0.1
        
        if not title.endswith(('.', '!', '?')):  # No ending punctuation for titles
            score += 0.1
        
        # Avoid keyword stuffing
        words = title_lower.split()
        unique_words = set(words)
        if len(unique_words) / len(words) > 0.8:  # Good word diversity
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_description_seo(self, description: str) -> float:
        """Score description SEO optimization"""
        if not description:
            return 0.0
        
        score = 0.0
        
        # Length check (150-160 characters optimal for meta description)
        if 150 <= len(description) <= 160:
            score += 0.3
        elif 120 <= len(description) <= 180:
            score += 0.2
        else:
            score += 0.1
        
        # Keyword presence
        desc_lower = description.lower()
        keyword_score = 0.0
        for category, keywords in self.seo_keywords.items():
            for keyword, weight in keywords.items():
                if keyword in desc_lower:
                    keyword_score += weight * 0.05
        
        score += min(keyword_score, 0.3)
        
        # Call to action presence
        cta_words = ["watch", "see", "learn", "discover", "find", "get", "join", "follow"]
        if any(word in desc_lower for word in cta_words):
            score += 0.2
        
        # Readability
        sentences = description.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        if 10 <= avg_sentence_length <= 20:  # Optimal sentence length
            score += 0.2
        
        return min(score, 1.0)
    
    def _extract_content_text(self, content_data: Dict[str, Any]) -> str:
        """Extract text content for analysis"""
        text_parts = []
        
        # Title and description
        text_parts.append(content_data.get("title", ""))
        text_parts.append(content_data.get("description", ""))
        
        # Transcription for video/audio
        if "transcription" in content_data:
            text_parts.append(content_data["transcription"])
        
        # Captions
        if "captions" in content_data:
            text_parts.extend(content_data["captions"])
        
        # Hashtags
        if "hashtags" in content_data:
            text_parts.extend(content_data["hashtags"])
        
        return " ".join(text_parts).strip()
    
    def _calculate_keyword_density(self, content_text: str) -> float:
        """Calculate keyword density"""
        if not content_text:
            return 0.0
        
        text_lower = content_text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        total_words = len(words)
        
        if total_words == 0:
            return 0.0
        
        # Count high-value keywords
        keyword_count = 0
        for category, keywords in self.seo_keywords.items():
            for keyword in keywords:
                keyword_count += text_lower.count(keyword)
        
        return keyword_count / total_words
    
    def _calculate_readability_score(self, content_text: str) -> float:
        """Calculate readability score (simplified Flesch Reading Ease)"""
        if not content_text:
            return 0.0
        
        sentences = content_text.split('.')
        words = content_text.split()
        syllables = self._count_syllables(content_text)
        
        if len(sentences) == 0 or len(words) == 0:
            return 0.0
        
        # Simplified Flesch Reading Ease
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Normalize to 0-1 scale (90-100 = very easy = 1.0, 0-30 = very difficult = 0.0)
        normalized_score = max(0, min(100, score)) / 100
        
        return normalized_score
    
    def _count_syllables(self, text: str) -> int:
        """Count syllables in text (simplified)"""
        vowels = 'aeiouy'
        syllables = 0
        
        for word in text.lower().split():
            word = re.sub(r'[^a-z]', '', word)
            if word:
                syllable_count = 0
                prev_was_vowel = False
                
                for char in word:
                    is_vowel = char in vowels
                    if is_vowel and not prev_was_vowel:
                        syllable_count += 1
                    prev_was_vowel = is_vowel
                
                # Adjust for silent e
                if word.endswith('e') and syllable_count > 1:
                    syllable_count -= 1
                
                syllables += max(1, syllable_count)
        
        return syllables
    
    def _score_meta_tags(self, meta_tags: Dict[str, str]) -> float:
        """Score meta tags optimization"""
        score = 0.0
        
        # Essential meta tags
        essential_tags = ["description", "keywords", "author", "viewport"]
        
        for tag in essential_tags:
            if tag in meta_tags and meta_tags[tag]:
                score += 0.2
        
        # Open Graph tags for social sharing
        og_tags = ["og:title", "og:description", "og:image", "og:type"]
        og_score = 0.0
        
        for tag in og_tags:
            if tag in meta_tags and meta_tags[tag]:
                og_score += 0.05
        
        score += og_score
        
        return min(score, 1.0)
    
    def _score_image_alt_texts(self, images: List[Dict[str, Any]]) -> float:
        """Score image alt text optimization"""
        if not images:
            return 1.0  # No images = no penalty
        
        total_images = len(images)
        images_with_alt = 0
        alt_quality_score = 0.0
        
        for image in images:
            alt_text = image.get("alt_text", "")
            if alt_text:
                images_with_alt += 1
                
                # Score alt text quality
                if 50 <= len(alt_text) <= 150:  # Good length
                    alt_quality_score += 0.5
                
                # Contains descriptive words
                descriptive_words = ["showing", "featuring", "displaying", "contains", "depicts"]
                if any(word in alt_text.lower() for word in descriptive_words):
                    alt_quality_score += 0.3
        
        coverage_score = images_with_alt / total_images
        avg_quality_score = alt_quality_score / max(images_with_alt, 1)
        
        return (coverage_score * 0.7) + (avg_quality_score * 0.3)
    
    def _score_url_structure(self, url: str) -> float:
        """Score URL structure for SEO"""
        if not url:
            return 0.5  # Neutral score for missing URL
        
        score = 0.0
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # URL length (shorter is better)
        if len(url) <= 100:
            score += 0.3
        elif len(url) <= 150:
            score += 0.2
        else:
            score += 0.1
        
        # Uses hyphens instead of underscores
        if '-' in path and '_' not in path:
            score += 0.2
        
        # Contains keywords
        path_lower = path.lower()
        keyword_score = 0.0
        for category, keywords in self.seo_keywords.items():
            for keyword in keywords:
                if keyword in path_lower:
                    keyword_score += 0.1
        
        score += min(keyword_score, 0.3)
        
        # No special characters
        if re.match(r'^[a-zA-Z0-9\-/]+$', path):
            score += 0.2
        
        return min(score, 1.0)
    
    def _score_internal_linking(self, links: List[str]) -> float:
        """Score internal linking strategy"""
        if not links:
            return 0.5  # Neutral for no links
        
        score = 0.0
        
        # Number of internal links (3-5 is optimal)
        link_count = len(links)
        if 3 <= link_count <= 5:
            score += 0.4
        elif 1 <= link_count <= 7:
            score += 0.3
        else:
            score += 0.1
        
        # Link diversity (different domains/sections)
        unique_domains = set()
        for link in links:
            parsed = urlparse(link)
            unique_domains.add(parsed.netloc or "internal")
        
        diversity_score = min(len(unique_domains) / max(link_count, 1), 1.0)
        score += diversity_score * 0.3
        
        # Descriptive anchor text (would need additional data)
        score += 0.3  # Placeholder
        
        return min(score, 1.0)
    
    def _score_content_length(self, content_data: Dict[str, Any]) -> float:
        """Score content length optimization"""
        content_type = ContentType(content_data.get("content_type", "text"))
        targets = self.content_analyzers["content_length_targets"].get(content_type, {})
        
        if not targets:
            return 0.5  # Neutral for unknown type
        
        # Determine actual length based on content type
        if content_type in [ContentType.VIDEO, ContentType.AUDIO]:
            actual_length = content_data.get("duration", 0)  # seconds
        else:
            content_text = self._extract_content_text(content_data)
            actual_length = len(content_text.split())  # words
        
        min_length = targets["min"]
        optimal_length = targets["optimal"]
        max_length = targets["max"]
        
        if optimal_length * 0.8 <= actual_length <= optimal_length * 1.2:
            return 1.0
        elif min_length <= actual_length <= max_length:
            return 0.7
        elif actual_length >= min_length * 0.5:
            return 0.5
        else:
            return 0.2
    
    def _score_content_freshness(self, created_date: datetime) -> float:
        """Score content freshness"""
        if isinstance(created_date, str):
            created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
        
        days_old = (datetime.now() - created_date).days
        
        # Freshness decay function
        if days_old <= 1:
            return 1.0
        elif days_old <= 7:
            return 0.9
        elif days_old <= 30:
            return 0.7
        elif days_old <= 90:
            return 0.5
        elif days_old <= 365:
            return 0.3
        else:
            return 0.1
    
    async def _calculate_category_scores(self, content_data: Dict[str, Any], seo_metrics: SEOMetrics) -> Dict[str, float]:
        """Calculate SEO scores by category"""
        scores = {}
        
        # Technical SEO
        scores[SEOScoreCategory.TECHNICAL_SEO.value] = (
            seo_metrics.url_structure_score * 0.3 +
            seo_metrics.meta_tag_score * 0.3 +
            seo_metrics.image_alt_score * 0.2 +
            seo_metrics.internal_linking_score * 0.2
        )
        
        # Content Quality
        scores[SEOScoreCategory.CONTENT_QUALITY.value] = (
            seo_metrics.readability_score * 0.4 +
            seo_metrics.content_length_score * 0.3 +
            seo_metrics.freshness_score * 0.3
        )
        
        # Keyword Optimization
        keyword_score = min(seo_metrics.keyword_density / self.keyword_tools["keyword_density_threshold"], 1.0)
        scores[SEOScoreCategory.KEYWORD_OPTIMIZATION.value] = (
            keyword_score * 0.5 +
            seo_metrics.title_score * 0.3 +
            seo_metrics.description_score * 0.2
        )
        
        # Metadata Optimization
        scores[SEOScoreCategory.METADATA_OPTIMIZATION.value] = (
            seo_metrics.title_score * 0.4 +
            seo_metrics.description_score * 0.4 +
            seo_metrics.meta_tag_score * 0.2
        )
        
        # Social Signals (placeholder - would integrate with social APIs)
        social_engagement = content_data.get("social_engagement", 0.5)
        scores[SEOScoreCategory.SOCIAL_SIGNALS.value] = social_engagement
        
        # Performance Metrics (placeholder - would integrate with analytics)
        performance_metrics = content_data.get("performance_metrics", 0.5)
        scores[SEOScoreCategory.PERFORMANCE_METRICS.value] = performance_metrics
        
        return scores
    
    async def _analyze_keywords(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze keyword optimization"""
        content_text = self._extract_content_text(content_data)
        
        if not content_text:
            return {"primary_keywords": [], "keyword_density": 0.0}
        
        # Extract keywords using TF-IDF
        try:
            tfidf_matrix = self.keyword_tools["tfidf_vectorizer"].fit_transform([content_text])
            feature_names = self.keyword_tools["tfidf_vectorizer"].get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            keyword_scores = list(zip(feature_names, tfidf_scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            top_keywords = keyword_scores[:20]
            
        except Exception as e:
            logger.warning(f"TF-IDF analysis failed: {e}")
            # Fallback to simple word frequency
            words = re.findall(r'\b\w+\b', content_text.lower())
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Filter short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Analyze keyword density
        keyword_density = self._calculate_keyword_density(content_text)
        
        # Identify SEO keyword opportunities
        seo_opportunities = []
        for category, keywords in self.seo_keywords.items():
            for keyword, weight in keywords.items():
                if keyword not in content_text.lower():
                    seo_opportunities.append({
                        "keyword": keyword,
                        "category": category,
                        "weight": weight,
                        "opportunity_score": weight * 0.8
                    })
        
        # Sort opportunities by score
        seo_opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        return {
            "primary_keywords": [kw[0] for kw in top_keywords[:10]],
            "keyword_scores": dict(top_keywords[:10]),
            "keyword_density": keyword_density,
            "seo_opportunities": seo_opportunities[:10],
            "keyword_distribution": self._analyze_keyword_distribution(content_text)
        }
    
    def _analyze_keyword_distribution(self, content_text: str) -> Dict[str, Any]:
        """Analyze keyword distribution throughout content"""
        # Simplified keyword distribution analysis
        sections = content_text.split('\n')
        
        distribution = {
            "title_presence": 0.0,
            "beginning_presence": 0.0,
            "middle_presence": 0.0,
            "end_presence": 0.0,
            "even_distribution": 0.0
        }
        
        if sections:
            # Check title/first section
            if len(sections) > 0:
                title_keywords = sum(1 for keyword in self.seo_keywords["high_value"] if keyword in sections[0].lower())
                distribution["title_presence"] = min(title_keywords / 3, 1.0)
            
            # Check distribution across sections
            total_sections = len(sections)
            if total_sections > 3:
                beginning = total_sections // 3
                middle = total_sections // 3
                end = total_sections - beginning - middle
                
                for section_type, section_count in [("beginning", beginning), ("middle", middle), ("end", end)]:
                    keyword_count = 0
                    for i in range(section_count):
                        if section_type == "beginning":
                            section_text = sections[i]
                        elif section_type == "middle":
                            section_text = sections[beginning + i]
                        else:
                            section_text = sections[beginning + middle + i]
                        
                        for keyword in self.seo_keywords["high_value"]:
                            if keyword in section_text.lower():
                                keyword_count += 1
                    
                    distribution[f"{section_type}_presence"] = min(keyword_count / 5, 1.0)
        
        return distribution
    
    async def _generate_optimization_recommendations(self, content_data: Dict[str, Any], seo_metrics: SEOMetrics, category_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate SEO optimization recommendations"""
        recommendations = []
        
        # Title optimization
        if seo_metrics.title_score < 0.7:
            recommendations.append({
                "category": SEOScoreCategory.METADATA_OPTIMIZATION.value,
                "priority": OptimizationPriority.HIGH.value,
                "recommendation": "Optimize title for SEO",
                "details": "Improve title length (50-60 chars), add target keywords, ensure proper capitalization",
                "current_score": seo_metrics.title_score,
                "potential_improvement": 0.8 - seo_metrics.title_score
            })
        
        # Description optimization
        if seo_metrics.description_score < 0.7:
            recommendations.append({
                "category": SEOScoreCategory.METADATA_OPTIMIZATION.value,
                "priority": OptimizationPriority.HIGH.value,
                "recommendation": "Optimize meta description",
                "details": "Improve description length (150-160 chars), add call-to-action, include target keywords",
                "current_score": seo_metrics.description_score,
                "potential_improvement": 0.8 - seo_metrics.description_score
            })
        
        # Keyword density optimization
        if seo_metrics.keyword_density < 0.01:
            recommendations.append({
                "category": SEOScoreCategory.KEYWORD_OPTIMIZATION.value,
                "priority": OptimizationPriority.MEDIUM.value,
                "recommendation": "Increase keyword density",
                "details": "Add more relevant keywords throughout content, target 1-3% keyword density",
                "current_score": seo_metrics.keyword_density,
                "potential_improvement": 0.03 - seo_metrics.keyword_density
            })
        elif seo_metrics.keyword_density > 0.05:
            recommendations.append({
                "category": SEOScoreCategory.KEYWORD_OPTIMIZATION.value,
                "priority": OptimizationPriority.MEDIUM.value,
                "recommendation": "Reduce keyword stuffing",
                "details": "Decrease keyword density to avoid penalties, use synonyms and related terms",
                "current_score": seo_metrics.keyword_density,
                "potential_improvement": seo_metrics.keyword_density - 0.03
            })
        
        # Readability optimization
        if seo_metrics.readability_score < 0.6:
            recommendations.append({
                "category": SEOScoreCategory.CONTENT_QUALITY.value,
                "priority": OptimizationPriority.MEDIUM.value,
                "recommendation": "Improve content readability",
                "details": "Use shorter sentences, simpler words, better paragraph structure",
                "current_score": seo_metrics.readability_score,
                "potential_improvement": 0.8 - seo_metrics.readability_score
            })
        
        # Meta tags optimization
        if seo_metrics.meta_tag_score < 0.8:
            recommendations.append({
                "category": SEOScoreCategory.TECHNICAL_SEO.value,
                "priority": OptimizationPriority.HIGH.value,
                "recommendation": "Add missing meta tags",
                "details": "Include essential meta tags: description, keywords, author, viewport, Open Graph tags",
                "current_score": seo_metrics.meta_tag_score,
                "potential_improvement": 1.0 - seo_metrics.meta_tag_score
            })
        
        # Image alt text optimization
        if seo_metrics.image_alt_score < 0.8:
            recommendations.append({
                "category": SEOScoreCategory.TECHNICAL_SEO.value,
                "priority": OptimizationPriority.MEDIUM.value,
                "recommendation": "Add alt text to images",
                "details": "Include descriptive alt text for all images (50-150 characters)",
                "current_score": seo_metrics.image_alt_score,
                "potential_improvement": 1.0 - seo_metrics.image_alt_score
            })
        
        # Content length optimization
        if seo_metrics.content_length_score < 0.7:
            recommendations.append({
                "category": SEOScoreCategory.CONTENT_QUALITY.value,
                "priority": OptimizationPriority.MEDIUM.value,
                "recommendation": "Optimize content length",
                "details": "Adjust content length to optimal range for content type",
                "current_score": seo_metrics.content_length_score,
                "potential_improvement": 0.9 - seo_metrics.content_length_score
            })
        
        # URL structure optimization
        if seo_metrics.url_structure_score < 0.7:
            recommendations.append({
                "category": SEOScoreCategory.TECHNICAL_SEO.value,
                "priority": OptimizationPriority.LOW.value,
                "recommendation": "Improve URL structure",
                "details": "Use descriptive URLs with keywords, hyphens instead of underscores, keep URLs short",
                "current_score": seo_metrics.url_structure_score,
                "potential_improvement": 0.9 - seo_metrics.url_structure_score
            })
        
        # Sort recommendations by priority and potential improvement
        priority_order = {
            OptimizationPriority.CRITICAL.value: 4,
            OptimizationPriority.HIGH.value: 3,
            OptimizationPriority.MEDIUM.value: 2,
            OptimizationPriority.LOW.value: 1
        }
        
        recommendations.sort(key=lambda x: (
            priority_order.get(x["priority"], 0),
            x.get("potential_improvement", 0)
        ), reverse=True)
        
        return recommendations
    
    async def _perform_competitive_analysis(self, content_data: Dict[str, Any], keyword_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform competitive SEO analysis"""
        # Placeholder for competitive analysis
        # In a real implementation, this would compare against competitor content
        
        primary_keywords = keyword_analysis.get("primary_keywords", [])
        
        competitive_analysis = {
            "competitors_analyzed": 5,  # Placeholder
            "keyword_competition": {
                "high_competition": [kw for kw in primary_keywords[:3]],
                "medium_competition": [kw for kw in primary_keywords[3:6]],
                "low_competition": [kw for kw in primary_keywords[6:10]]
            },
            "content_gap_analysis": {
                "missing_topics": ["trending_content", "viral_strategies", "audience_engagement"],
                "underutilized_keywords": primary_keywords[5:10],
                "opportunities": ["long_tail_keywords", "semantic_keywords", "local_seo"]
            },
            "competitive_position": "competitive",  # Would be calculated based on actual analysis
            "market_share_estimate": 0.15,  # Placeholder
            "improvement_opportunities": [
                "Target long-tail keywords",
                "Improve content depth",
                "Enhance social signals"
            ]
        }
        
        return competitive_analysis
    
    async def _analyze_trend_alignment(self, content_data: Dict[str, Any]) -> float:
        """Analyze alignment with current SEO trends"""
        # Placeholder for trend analysis
        # In a real implementation, this would check against current trending keywords/topics
        
        content_text = self._extract_content_text(content_data).lower()
        
        # Check for trending elements
        trending_elements = [
            "ai", "artificial intelligence", "machine learning", "viral", "trending",
            "social media", "content creator", "influencer", "engagement", "community"
        ]
        
        trend_score = 0.0
        for element in trending_elements:
            if element in content_text:
                trend_score += 0.1
        
        # Check for content freshness
        created_date = content_data.get("created_date", datetime.now())
        if isinstance(created_date, str):
            created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
        
        freshness_bonus = max(0, 1 - (datetime.now() - created_date).days / 30)
        trend_score += freshness_bonus * 0.3
        
        return min(trend_score, 1.0)
    
    async def _analyze_social_seo_signals(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze social SEO signals"""
        social_signals = {
            "social_shares": content_data.get("social_shares", 0),
            "social_mentions": content_data.get("social_mentions", 0),
            "social_engagement_rate": content_data.get("social_engagement_rate", 0.0),
            "social_platforms": content_data.get("social_platforms", []),
            "social_seo_score": 0.0
        }
        
        # Calculate social SEO score
        shares_score = min(social_signals["social_shares"] / 100, 1.0)
        mentions_score = min(social_signals["social_mentions"] / 50, 1.0)
        engagement_score = social_signals["social_engagement_rate"]
        platform_diversity = min(len(social_signals["social_platforms"]) / 5, 1.0)
        
        social_seo_score = (shares_score * 0.3 + mentions_score * 0.3 + 
                           engagement_score * 0.3 + platform_diversity * 0.1)
        
        social_signals["social_seo_score"] = social_seo_score
        
        return social_signals
    
    async def _predict_seo_performance(self, seo_metrics: SEOMetrics, category_scores: Dict[str, float]) -> Dict[str, Any]:
        """Predict SEO performance based on current metrics"""
        # Calculate overall performance prediction
        technical_weight = 0.3
        content_weight = 0.4
        keyword_weight = 0.3
        
        predicted_ranking = (
            category_scores.get(SEOScoreCategory.TECHNICAL_SEO.value, 0.5) * technical_weight +
            category_scores.get(SEOScoreCategory.CONTENT_QUALITY.value, 0.5) * content_weight +
            category_scores.get(SEOScoreCategory.KEYWORD_OPTIMIZATION.value, 0.5) * keyword_weight
        )
        
        # Predict traffic improvement
        current_score = sum(category_scores.values()) / len(category_scores)
        traffic_improvement = max(0, (predicted_ranking - current_score) * 100)
        
        # Predict time to see results
        improvement_needed = 1.0 - predicted_ranking
        time_to_results = int(30 + (improvement_needed * 60))  # 30-90 days
        
        return {
            "predicted_ranking_score": predicted_ranking,
            "traffic_improvement_percentage": traffic_improvement,
            "time_to_results_days": time_to_results,
            "confidence_level": 0.75,
            "key_factors": [
                "Content quality improvements",
                "Technical SEO optimizations",
                "Keyword optimization"
            ]
        }
    
    async def _calculate_overall_seo_score(self, category_scores: Dict[str, float]) -> float:
        """Calculate overall SEO score"""
        weighted_score = 0.0
        
        for category, weight in self.scoring_weights.items():
            score = category_scores.get(category.value, 0.5)
            weighted_score += score * weight
        
        return min(weighted_score, 1.0)
    
    def _get_seo_grade(self, score: float) -> str:
        """Get SEO grade based on score"""
        if score >= 0.9:
            return "A+"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B"
        elif score >= 0.6:
            return "C"
        elif score >= 0.5:
            return "D"
        else:
            return "F"
    
    def _calculate_improvement_potential(self, category_scores: Dict[str, float]) -> Dict[str, Any]:
        """Calculate improvement potential"""
        total_potential = 0.0
        category_potential = {}
        
        for category, score in category_scores.items():
            potential = 1.0 - score
            category_potential[category] = potential
            total_potential += potential
        
        # Identify top improvement areas
        sorted_potential = sorted(category_potential.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_improvement_potential": total_potential,
            "category_potential": category_potential,
            "top_improvement_areas": [area[0] for area in sorted_potential[:3]],
            "quick_wins": [area[0] for area in sorted_potential if area[1] > 0.3]
        }
    
    def get_content_seo_analysis(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get SEO analysis for specific content"""
        analysis = self.content_analyses.get(content_id)
        return asdict(analysis) if analysis else None
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current SEO monitoring status"""
        return {
            "total_content_analyzed": len(self.content_analyses),
            "total_optimizations": len(self.seo_optimizations),
            "average_seo_score": sum(a.overall_seo_score for a in self.content_analyses.values()) / max(len(self.content_analyses), 1),
            "keyword_database_size": len(self.keyword_database),
            "last_updated": datetime.now().isoformat()
        }


# Example usage and testing
if __name__ == "__main__":
    async def test_seo_scoring() -> None:
        """Test SEO scoring functionality"""
        engine = ContentSEOScoringEngine()
        
        # Test content data
        content_data = {
            "content_type": "video",
            "title": "How to Create Viral Content on Social Media - Complete Guide 2025",
            "description": "Learn the secrets to creating viral content that gets millions of views. This comprehensive guide covers all platforms including TikTok, Instagram, and YouTube.",
            "transcription": "Welcome to this complete guide on creating viral content. In this video, we'll explore the strategies that top content creators use to reach millions of people. We'll cover topics like audience engagement, trending hashtags, and content optimization for maximum reach.",
            "hashtags": ["#viral", "#contentcreator", "#socialmedia", "#trending"],
            "url": "https://ainflue.com/guides/viral-content-creation-2025",
            "meta_tags": {
                "description": "Complete guide to creating viral content on social media platforms",
                "keywords": "viral content, social media, content creator, engagement",
                "author": "Ainflue Team"
            },
            "images": [
                {"alt_text": "Content creator filming video showing viral content strategies"},
                {"alt_text": "Social media analytics dashboard displaying engagement metrics"}
            ],
            "internal_links": [
                "https://ainflue.com/tools/hashtag-generator",
                "https://ainflue.com/analytics/engagement-tracker"
            ],
            "duration": 420,  # 7 minutes
            "created_date": datetime.now(),
            "social_shares": 250,
            "social_mentions": 75,
            "social_engagement_rate": 0.08,
            "social_platforms": ["instagram", "tiktok", "youtube", "twitter"]
        }
        
        # Analyze SEO
        analysis = await engine.analyze_content_seo("content_001", content_data)
        print(f"SEO Analysis: {analysis}")
        
        # Get detailed analysis
        detailed_analysis = engine.get_content_seo_analysis("content_001")
        print(f"Detailed Analysis: {detailed_analysis}")
        
        # Get monitoring status
        status = engine.get_monitoring_status()
        print(f"Monitoring Status: {status}")
    
    # Run test
    asyncio.run(test_seo_scoring())