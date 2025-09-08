"""Content Optimization Engine - Advanced Multi-Platform Content Optimization
=========================================================================

Consolidated optimization system providing comprehensive SEO optimization,
social media optimization, and quality enhancement for maximum reach and engagement.

Consolidates:
- SEO metadata optimization and search engine visibility (seo_metadata_optimizer.py)
- Social media platform optimization and engagement maximization (social_media_optimizer.py)
- Media quality optimization and performance enhancement (media_quality_optimizer.py)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary optimization system contains advanced algorithms and trade secrets
belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering  
- Commercial use without explicit written permission
- Algorithm extraction or optimization logic appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import json
import logging
import re
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from pathlib import Path

# AI and NLP imports with graceful fallbacks
try:
    import transformers
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logging.warning("Transformers not available - using basic text processing")

try:
    import nltk
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    logging.warning("NLTK not available - using basic text analysis")

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False
    logging.warning("TextBlob not available - using basic sentiment analysis")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    logging.warning("Requests not available - using basic HTTP functionality")

logger = logging.getLogger(__name__)


class OptimizationPlatform(Enum):
    """Target platforms for optimization"""
    # Search Engines
    GOOGLE = "google"
    BING = "bing"
    YAHOO = "yahoo"
    # Social Media
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    DISCORD = "discord"
    # Professional
    WEBSITE = "website"
    BLOG = "blog"
    PODCAST = "podcast"
    # Commerce
    MARKETPLACE = "marketplace"
    ECOMMERCE = "ecommerce"


class OptimizationType(Enum):
    """Type of optimization to perform"""
    SEO = "seo"
    SOCIAL_MEDIA = "social_media"
    QUALITY = "quality"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"


class ContentType(Enum):
    """Content types for optimization"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    PODCAST = "podcast"
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    PRODUCT = "product"
    LANDING_PAGE = "landing_page"


@dataclass
class OptimizationConfig:
    """Optimization configuration settings"""
    target_platforms: List[OptimizationPlatform] = field(default_factory=list)
    optimization_types: List[OptimizationType] = field(default_factory=list)
    target_audience: str = "general"
    target_keywords: List[str] = field(default_factory=list)
    max_keyword_density: float = 0.03
    min_content_score: float = 0.7
    enable_ai_suggestions: bool = True
    real_time_optimization: bool = True
    track_performance: bool = True


@dataclass
class SEOMetadata:
    """SEO metadata structure"""
    title: str
    description: str
    keywords: List[str]
    canonical_url: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    schema_markup: Optional[Dict[str, Any]] = None
    robots_meta: str = "index, follow"
    lang: str = "en"


@dataclass
class SocialMediaOptimization:
    """Social media optimization results"""
    platform: OptimizationPlatform
    optimized_content: str
    hashtags: List[str]
    optimal_posting_time: Optional[datetime] = None
    target_audience_tags: List[str] = field(default_factory=list)
    engagement_predictions: Dict[str, float] = field(default_factory=dict)
    platform_specific_features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityMetrics:
    """Content quality assessment metrics"""
    overall_score: float
    readability_score: float
    engagement_potential: float
    seo_score: float
    accessibility_score: float
    technical_quality: float
    content_uniqueness: float
    brand_alignment: float


@dataclass
class OptimizationResult:
    """Complete optimization result"""
    content_id: str
    original_content: str
    optimized_content: str
    seo_metadata: SEOMetadata
    social_optimizations: List[SocialMediaOptimization]
    quality_metrics: QualityMetrics
    optimization_suggestions: List[str]
    performance_predictions: Dict[str, float]
    optimization_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SEOOptimizer:
    """Advanced SEO optimization and metadata generation"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.keyword_research_cache = {}
        self.schema_templates = {}
        
        if HAS_TRANSFORMERS:
            self._initialize_nlp_models()
        
        logger.info("🔍 SEO Optimizer initialized")
    
    def _initialize_nlp_models(self):
        """Initialize NLP models for content analysis"""
        try:
            # Would initialize actual models in production
            pass
        except Exception as e:
            logger.warning(f"Failed to initialize NLP models: {e}")
    
    async def optimize_seo_metadata(
        self, 
        content: str, 
        content_type: ContentType,
        target_keywords: Optional[List[str]] = None
    ) -> SEOMetadata:
        """Generate optimized SEO metadata"""
        try:
            # Extract or generate keywords
            keywords = target_keywords or await self._extract_keywords(content)
            
            # Generate SEO-optimized title
            title = await self._generate_seo_title(content, keywords, content_type)
            
            # Generate SEO-optimized description
            description = await self._generate_seo_description(content, keywords)
            
            # Generate Open Graph metadata
            og_title, og_description = await self._generate_og_metadata(title, description)
            
            # Generate Twitter Card metadata
            twitter_title, twitter_description = await self._generate_twitter_metadata(title, description)
            
            # Generate schema markup
            schema_markup = await self._generate_schema_markup(content, content_type)
            
            return SEOMetadata(
                title=title,
                description=description,
                keywords=keywords,
                og_title=og_title,
                og_description=og_description,
                twitter_title=twitter_title,
                twitter_description=twitter_description,
                schema_markup=schema_markup
            )
            
        except Exception as e:
            logger.error(f"SEO metadata optimization failed: {e}")
            return SEOMetadata(
                title=content[:60] if content else "Untitled",
                description=content[:160] if content else "No description",
                keywords=[]
            )
    
    async def _extract_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords from content"""
        if not content:
            return []
        
        # Simple keyword extraction (would use advanced NLP in production)
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Filter stop words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'can', 'may', 'might', 'must'}
        
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Count frequency and return top keywords
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top 10
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_keywords[:10]]
    
    async def _generate_seo_title(
        self, 
        content: str, 
        keywords: List[str], 
        content_type: ContentType
    ) -> str:
        """Generate SEO-optimized title"""
        if not content:
            return "Untitled Content"
        
        # Extract first sentence or paragraph as base
        sentences = content.split('.')
        base_title = sentences[0][:50] if sentences else content[:50]
        
        # Add primary keyword if not present
        if keywords and keywords[0].lower() not in base_title.lower():
            base_title = f"{keywords[0].title()} - {base_title}"
        
        # Ensure title length is optimal (50-60 characters)
        if len(base_title) > 60:
            base_title = base_title[:57] + "..."
        elif len(base_title) < 30:
            # Add context based on content type
            type_suffix = {
                ContentType.BLOG_POST: " - Complete Guide",
                ContentType.VIDEO: " - Watch Now",
                ContentType.PODCAST: " - Listen Now",
                ContentType.PRODUCT: " - Buy Online"
            }
            suffix = type_suffix.get(content_type, "")
            if len(base_title) + len(suffix) <= 60:
                base_title += suffix
        
        return base_title
    
    async def _generate_seo_description(self, content: str, keywords: List[str]) -> str:
        """Generate SEO-optimized meta description"""
        if not content:
            return "No description available"
        
        # Extract first few sentences
        sentences = content.split('.')
        description_base = '. '.join(sentences[:3])
        
        # Ensure optimal length (150-160 characters)
        if len(description_base) > 160:
            description_base = description_base[:157] + "..."
        elif len(description_base) < 120:
            # Add keywords naturally if space allows
            if keywords:
                keyword_phrase = f" Learn about {', '.join(keywords[:3])}."
                if len(description_base) + len(keyword_phrase) <= 160:
                    description_base += keyword_phrase
        
        return description_base
    
    async def _generate_og_metadata(self, title: str, description: str) -> Tuple[str, str]:
        """Generate Open Graph metadata"""
        # Optimize for social sharing
        og_title = title[:95] if len(title) > 95 else title  # Facebook limit
        og_description = description[:300] if len(description) > 300 else description
        
        return og_title, og_description
    
    async def _generate_twitter_metadata(self, title: str, description: str) -> Tuple[str, str]:
        """Generate Twitter Card metadata"""
        # Optimize for Twitter
        twitter_title = title[:70] if len(title) > 70 else title  # Twitter limit
        twitter_description = description[:200] if len(description) > 200 else description
        
        return twitter_title, twitter_description
    
    async def _generate_schema_markup(self, content: str, content_type: ContentType) -> Dict[str, Any]:
        """Generate structured data schema markup"""
        base_schema = {
            "@context": "https://schema.org/",
            "@type": "CreativeWork",
            "name": content[:100],
            "description": content[:200],
            "dateCreated": datetime.now(timezone.utc).isoformat(),
            "creator": {
                "@type": "Person",
                "name": "Content Creator"
            }
        }
        
        # Add type-specific schema
        if content_type == ContentType.BLOG_POST:
            base_schema["@type"] = "BlogPosting"
            base_schema["headline"] = content[:110]
        elif content_type == ContentType.VIDEO:
            base_schema["@type"] = "VideoObject"
            base_schema["uploadDate"] = datetime.now(timezone.utc).isoformat()
        elif content_type == ContentType.PODCAST:
            base_schema["@type"] = "PodcastEpisode"
        
        return base_schema


class SocialMediaOptimizer:
    """Platform-specific social media optimization"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.platform_specs = self._initialize_platform_specs()
        self.hashtag_research_cache = {}
        
        logger.info("📱 Social Media Optimizer initialized")
    
    def _initialize_platform_specs(self) -> Dict[OptimizationPlatform, Dict[str, Any]]:
        """Initialize platform-specific specifications"""
        return {
            OptimizationPlatform.INSTAGRAM: {
                'max_text_length': 2200,
                'max_hashtags': 30,
                'optimal_hashtags': 11,
                'image_aspect_ratios': ['1:1', '4:5', '9:16'],
                'video_length_limits': {'feed': 60, 'stories': 15, 'reels': 90},
                'optimal_posting_times': [8, 12, 17, 19, 21]
            },
            OptimizationPlatform.TIKTOK: {
                'max_text_length': 300,
                'max_hashtags': 20,
                'optimal_hashtags': 5,
                'video_aspect_ratio': '9:16',
                'video_length_limits': {'standard': 180, 'max': 600},
                'optimal_posting_times': [6, 10, 19, 20, 21]
            },
            OptimizationPlatform.YOUTUBE: {
                'title_max_length': 100,
                'description_max_length': 5000,
                'max_tags': 15,
                'thumbnail_aspect_ratio': '16:9',
                'optimal_posting_times': [14, 15, 16, 17, 18, 19, 20]
            },
            OptimizationPlatform.TWITTER: {
                'max_text_length': 280,
                'max_hashtags': 10,
                'optimal_hashtags': 2,
                'image_aspect_ratios': ['16:9', '1:1'],
                'video_length_limits': {'standard': 140, 'premium': 10800},
                'optimal_posting_times': [8, 12, 17, 18, 19]
            },
            OptimizationPlatform.LINKEDIN: {
                'max_text_length': 3000,
                'max_hashtags': 10,
                'optimal_hashtags': 5,
                'image_aspect_ratios': ['1.91:1', '1:1'],
                'video_length_limits': {'standard': 600, 'max': 900},
                'optimal_posting_times': [7, 8, 9, 17, 18]
            },
            OptimizationPlatform.FACEBOOK: {
                'max_text_length': 63206,
                'optimal_text_length': 125,
                'image_aspect_ratios': ['1.91:1', '1:1'],
                'video_length_limits': {'standard': 240, 'max': 14400},
                'optimal_posting_times': [13, 15, 21]
            }
        }
    
    async def optimize_for_platform(
        self, 
        content: str, 
        platform: OptimizationPlatform,
        content_type: ContentType = ContentType.SOCIAL_POST
    ) -> SocialMediaOptimization:
        """Optimize content for specific social media platform"""
        try:
            platform_spec = self.platform_specs.get(platform, {})
            
            # Optimize text content
            optimized_text = await self._optimize_text_for_platform(content, platform, platform_spec)
            
            # Generate platform-specific hashtags
            hashtags = await self._generate_platform_hashtags(content, platform)
            
            # Determine optimal posting time
            optimal_time = await self._determine_optimal_posting_time(platform)
            
            # Generate audience tags
            audience_tags = await self._generate_audience_tags(content, platform)
            
            # Predict engagement
            engagement_predictions = await self._predict_platform_engagement(
                optimized_text, platform, hashtags
            )
            
            # Get platform-specific features
            platform_features = await self._get_platform_specific_features(platform, content_type)
            
            return SocialMediaOptimization(
                platform=platform,
                optimized_content=optimized_text,
                hashtags=hashtags,
                optimal_posting_time=optimal_time,
                target_audience_tags=audience_tags,
                engagement_predictions=engagement_predictions,
                platform_specific_features=platform_features
            )
            
        except Exception as e:
            logger.error(f"Social media optimization failed for {platform.value}: {e}")
            return SocialMediaOptimization(
                platform=platform,
                optimized_content=content,
                hashtags=[]
            )
    
    async def _optimize_text_for_platform(
        self, 
        content: str, 
        platform: OptimizationPlatform,
        platform_spec: Dict[str, Any]
    ) -> str:
        """Optimize text content for platform specifications"""
        if not content:
            return ""
        
        max_length = platform_spec.get('max_text_length', 1000)
        optimal_length = platform_spec.get('optimal_text_length')
        
        # Trim to max length if needed
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        # Platform-specific optimizations
        if platform == OptimizationPlatform.TWITTER:
            # Optimize for Twitter's character limit and engagement
            if len(content) > 240:  # Leave room for hashtags
                content = content[:237] + "..."
        
        elif platform == OptimizationPlatform.INSTAGRAM:
            # Add line breaks for better readability
            content = self._add_instagram_formatting(content)
        
        elif platform == OptimizationPlatform.LINKEDIN:
            # Professional tone optimization
            content = self._optimize_for_professional_tone(content)
        
        elif platform == OptimizationPlatform.TIKTOK:
            # Optimize for younger audience and trends
            content = self._optimize_for_tiktok_trends(content)
        
        return content
    
    def _add_instagram_formatting(self, content: str) -> str:
        """Add Instagram-friendly formatting"""
        # Add line breaks after sentences for readability
        formatted = content.replace('. ', '.\n\n')
        return formatted
    
    def _optimize_for_professional_tone(self, content: str) -> str:
        """Optimize content for professional LinkedIn audience"""
        # Replace casual words with professional alternatives
        professional_replacements = {
            'awesome': 'excellent',
            'cool': 'impressive',
            'stuff': 'content',
            'guys': 'team',
            'hey': 'hello'
        }
        
        for casual, professional in professional_replacements.items():
            content = re.sub(r'\b' + casual + r'\b', professional, content, flags=re.IGNORECASE)
        
        return content
    
    def _optimize_for_tiktok_trends(self, content: str) -> str:
        """Optimize content for TikTok trends and younger audience"""
        # Add trending elements (simplified)
        if not any(emoji in content for emoji in ['🔥', '💯', '✨', '🚀']):
            content += " 🔥"
        
        return content
    
    async def _generate_platform_hashtags(
        self, 
        content: str, 
        platform: OptimizationPlatform
    ) -> List[str]:
        """Generate platform-specific hashtags"""
        platform_spec = self.platform_specs.get(platform, {})
        max_hashtags = platform_spec.get('max_hashtags', 10)
        optimal_hashtags = platform_spec.get('optimal_hashtags', 5)
        
        # Extract potential hashtags from content
        content_words = re.findall(r'\b\w+\b', content.lower())
        
        # Platform-specific trending hashtags (would fetch from APIs in production)
        trending_hashtags = {
            OptimizationPlatform.INSTAGRAM: ['photography', 'art', 'design', 'lifestyle', 'creative'],
            OptimizationPlatform.TIKTOK: ['fyp', 'viral', 'trending', 'creative', 'fun'],
            OptimizationPlatform.TWITTER: ['news', 'breaking', 'update', 'thread', 'discussion'],
            OptimizationPlatform.LINKEDIN: ['professional', 'career', 'business', 'networking', 'growth'],
            OptimizationPlatform.YOUTUBE: ['subscribe', 'tutorial', 'howto', 'review', 'tips']
        }
        
        platform_hashtags = trending_hashtags.get(platform, [])
        
        # Combine content-based and platform-specific hashtags
        hashtags = []
        
        # Add content-based hashtags
        for word in content_words[:3]:
            if len(word) > 3:
                hashtags.append(f"#{word}")
        
        # Add platform-specific hashtags
        for hashtag in platform_hashtags[:optimal_hashtags-len(hashtags)]:
            hashtags.append(f"#{hashtag}")
        
        return hashtags[:optimal_hashtags]
    
    async def _determine_optimal_posting_time(self, platform: OptimizationPlatform) -> Optional[datetime]:
        """Determine optimal posting time for platform"""
        platform_spec = self.platform_specs.get(platform, {})
        optimal_hours = platform_spec.get('optimal_posting_times', [12])
        
        # Get next optimal time
        now = datetime.now(timezone.utc)
        today_hours = [now.replace(hour=hour, minute=0, second=0, microsecond=0) for hour in optimal_hours]
        
        # Find next optimal time
        future_times = [t for t in today_hours if t > now]
        if future_times:
            return min(future_times)
        else:
            # Next day's first optimal time
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=optimal_hours[0], minute=0, second=0, microsecond=0)
    
    async def _generate_audience_tags(self, content: str, platform: OptimizationPlatform) -> List[str]:
        """Generate audience targeting tags"""
        # Simplified audience detection based on content
        audience_keywords = {
            'business': ['entrepreneurs', 'professionals', 'business-owners'],
            'creative': ['artists', 'designers', 'creators'],
            'tech': ['developers', 'tech-enthusiasts', 'innovators'],
            'lifestyle': ['lifestyle-enthusiasts', 'wellness', 'self-improvement']
        }
        
        tags = []
        content_lower = content.lower()
        
        for category, audience_list in audience_keywords.items():
            if any(keyword in content_lower for keyword in [category, f"{category}s"]):
                tags.extend(audience_list[:2])
        
        return tags[:5]
    
    async def _predict_platform_engagement(
        self, 
        content: str, 
        platform: OptimizationPlatform, 
        hashtags: List[str]
    ) -> Dict[str, float]:
        """Predict engagement metrics for platform"""
        # Simplified engagement prediction
        content_score = min(len(content) / 100, 1.0)
        hashtag_score = min(len(hashtags) / 10, 1.0)
        
        base_engagement = (content_score + hashtag_score) / 2
        
        # Platform-specific multipliers
        platform_multipliers = {
            OptimizationPlatform.TIKTOK: 1.5,
            OptimizationPlatform.INSTAGRAM: 1.2,
            OptimizationPlatform.YOUTUBE: 1.0,
            OptimizationPlatform.TWITTER: 0.8,
            OptimizationPlatform.LINKEDIN: 0.7,
            OptimizationPlatform.FACEBOOK: 0.6
        }
        
        multiplier = platform_multipliers.get(platform, 1.0)
        
        return {
            'likes': base_engagement * multiplier * 1000,
            'shares': base_engagement * multiplier * 100,
            'comments': base_engagement * multiplier * 50,
            'reach': base_engagement * multiplier * 5000,
            'engagement_rate': base_engagement * multiplier * 0.05
        }
    
    async def _get_platform_specific_features(
        self, 
        platform: OptimizationPlatform, 
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Get platform-specific optimization features"""
        features = {}
        
        if platform == OptimizationPlatform.INSTAGRAM:
            features = {
                'story_highlights': True,
                'reels_optimization': True,
                'shopping_tags': content_type == ContentType.PRODUCT,
                'location_tags': True
            }
        elif platform == OptimizationPlatform.YOUTUBE:
            features = {
                'thumbnail_optimization': True,
                'chapter_markers': content_type == ContentType.VIDEO,
                'end_screens': True,
                'cards': True
            }
        elif platform == OptimizationPlatform.TIKTOK:
            features = {
                'trending_sounds': True,
                'effects_optimization': True,
                'duet_collaboration': True
            }
        
        return features


class QualityOptimizer:
    """Content quality assessment and optimization"""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.quality_models = {}
        
        logger.info("⭐ Quality Optimizer initialized")
    
    async def assess_content_quality(
        self, 
        content: str, 
        content_type: ContentType
    ) -> QualityMetrics:
        """Assess comprehensive content quality"""
        try:
            # Calculate individual quality metrics
            readability = await self._assess_readability(content)
            engagement_potential = await self._assess_engagement_potential(content)
            seo_score = await self._assess_seo_quality(content)
            accessibility = await self._assess_accessibility(content, content_type)
            technical_quality = await self._assess_technical_quality(content, content_type)
            uniqueness = await self._assess_content_uniqueness(content)
            brand_alignment = await self._assess_brand_alignment(content)
            
            # Calculate overall score
            overall_score = (
                readability * 0.15 +
                engagement_potential * 0.20 +
                seo_score * 0.15 +
                accessibility * 0.10 +
                technical_quality * 0.15 +
                uniqueness * 0.15 +
                brand_alignment * 0.10
            )
            
            return QualityMetrics(
                overall_score=overall_score,
                readability_score=readability,
                engagement_potential=engagement_potential,
                seo_score=seo_score,
                accessibility_score=accessibility,
                technical_quality=technical_quality,
                content_uniqueness=uniqueness,
                brand_alignment=brand_alignment
            )
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return QualityMetrics(
                overall_score=0.5,
                readability_score=0.5,
                engagement_potential=0.5,
                seo_score=0.5,
                accessibility_score=0.5,
                technical_quality=0.5,
                content_uniqueness=0.5,
                brand_alignment=0.5
            )
    
    async def _assess_readability(self, content: str) -> float:
        """Assess content readability"""
        if not content:
            return 0.0
        
        # Simple readability assessment
        sentences = content.split('.')
        words = content.split()
        
        if len(sentences) == 0:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        # Optimal range: 15-20 words per sentence
        if 15 <= avg_words_per_sentence <= 20:
            readability = 1.0
        elif avg_words_per_sentence < 15:
            readability = 0.8 + (avg_words_per_sentence / 15) * 0.2
        else:
            readability = max(0.2, 1.0 - (avg_words_per_sentence - 20) / 20)
        
        return min(readability, 1.0)
    
    async def _assess_engagement_potential(self, content: str) -> float:
        """Assess content engagement potential"""
        if not content:
            return 0.0
        
        engagement_indicators = {
            'questions': len(re.findall(r'\?', content)),
            'exclamations': len(re.findall(r'!', content)),
            'call_to_action': len(re.findall(r'\b(click|share|comment|like|subscribe|follow)\b', content, re.IGNORECASE)),
            'emotional_words': len(re.findall(r'\b(amazing|incredible|awesome|fantastic|love|hate|fear|joy)\b', content, re.IGNORECASE))
        }
        
        # Calculate engagement score
        score = 0.0
        score += min(engagement_indicators['questions'] / 3, 0.25)  # Questions boost engagement
        score += min(engagement_indicators['exclamations'] / 2, 0.15)  # Excitement
        score += min(engagement_indicators['call_to_action'] / 2, 0.30)  # CTAs
        score += min(engagement_indicators['emotional_words'] / 5, 0.30)  # Emotional connection
        
        return min(score, 1.0)
    
    async def _assess_seo_quality(self, content: str) -> float:
        """Assess SEO quality of content"""
        if not content:
            return 0.0
        
        seo_factors = {
            'length': len(content),
            'keywords': len(set(re.findall(r'\b\w+\b', content.lower()))),
            'headings': len(re.findall(r'\n#+\s', content)),  # Markdown headings
            'links': len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content))
        }
        
        score = 0.0
        
        # Content length (optimal: 300-2000 words)
        word_count = len(content.split())
        if 300 <= word_count <= 2000:
            score += 0.3
        elif word_count < 300:
            score += (word_count / 300) * 0.3
        else:
            score += max(0.1, 0.3 - (word_count - 2000) / 5000)
        
        # Keyword diversity
        score += min(seo_factors['keywords'] / 100, 0.25)
        
        # Structure (headings)
        score += min(seo_factors['headings'] / 5, 0.25)
        
        # External links
        score += min(seo_factors['links'] / 3, 0.2)
        
        return min(score, 1.0)
    
    async def _assess_accessibility(self, content: str, content_type: ContentType) -> float:
        """Assess content accessibility"""
        if not content:
            return 0.0
        
        accessibility_score = 0.5  # Base score
        
        # Text-based accessibility
        if content_type in [ContentType.TEXT, ContentType.BLOG_POST]:
            # Check for proper structure
            if re.search(r'\n#+\s', content):  # Has headings
                accessibility_score += 0.2
            
            # Check for descriptive text
            if len(content.split()) > 50:  # Sufficient content
                accessibility_score += 0.2
        
        # Image accessibility would check for alt text
        elif content_type == ContentType.IMAGE:
            accessibility_score += 0.3  # Assume alt text will be added
        
        # Video accessibility would check for captions
        elif content_type == ContentType.VIDEO:
            accessibility_score += 0.3  # Assume captions will be added
        
        return min(accessibility_score, 1.0)
    
    async def _assess_technical_quality(self, content: str, content_type: ContentType) -> float:
        """Assess technical quality of content"""
        if not content:
            return 0.0
        
        technical_score = 0.5  # Base score
        
        # Grammar and spelling (simplified check)
        errors = len(re.findall(r'\b(teh|adn|thier|thier|recieve|seperate)\b', content, re.IGNORECASE))
        grammar_score = max(0, 1.0 - errors / 10)
        technical_score += grammar_score * 0.3
        
        # Formatting quality
        if content_type in [ContentType.TEXT, ContentType.BLOG_POST]:
            # Check for proper punctuation
            sentence_endings = len(re.findall(r'[.!?]', content))
            sentences = len(content.split('.'))
            if sentences > 0 and sentence_endings / sentences > 0.8:
                technical_score += 0.2
        
        return min(technical_score, 1.0)
    
    async def _assess_content_uniqueness(self, content: str) -> float:
        """Assess content uniqueness and originality"""
        if not content:
            return 0.0
        
        # Simple uniqueness assessment (would use plagiarism detection in production)
        word_count = len(set(content.lower().split()))
        total_words = len(content.split())
        
        if total_words == 0:
            return 0.0
        
        uniqueness_ratio = word_count / total_words
        return min(uniqueness_ratio * 1.2, 1.0)  # Boost for word diversity
    
    async def _assess_brand_alignment(self, content: str) -> float:
        """Assess brand alignment and consistency"""
        if not content:
            return 0.0
        
        # Simplified brand alignment assessment
        professional_indicators = len(re.findall(r'\b(professional|quality|expert|premium|excellence)\b', content, re.IGNORECASE))
        brand_score = min(professional_indicators / 3, 1.0)
        
        return max(brand_score, 0.5)  # Minimum brand alignment score


class ContentOptimizationEngine:
    """Main content optimization engine orchestrating all optimization components"""
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        """Initialize content optimization engine"""
        self.config = config or OptimizationConfig(
            target_platforms=[OptimizationPlatform.GOOGLE, OptimizationPlatform.INSTAGRAM],
            optimization_types=[OptimizationType.SEO, OptimizationType.SOCIAL_MEDIA, OptimizationType.QUALITY]
        )
        
        # Initialize component optimizers
        self.seo_optimizer = SEOOptimizer(self.config)
        self.social_optimizer = SocialMediaOptimizer(self.config)
        self.quality_optimizer = QualityOptimizer(self.config)
        
        # Optimization cache and analytics
        self.optimization_cache = {}
        self.performance_history = []
        
        logger.info("🚀 Content Optimization Engine initialized")
    
    async def optimize_content_comprehensive(
        self, 
        content: str,
        content_type: ContentType = ContentType.TEXT,
        target_platforms: Optional[List[OptimizationPlatform]] = None,
        custom_config: Optional[OptimizationConfig] = None
    ) -> OptimizationResult:
        """Comprehensive content optimization across all dimensions"""
        try:
            content_id = str(uuid.uuid4())
            config = custom_config or self.config
            platforms = target_platforms or config.target_platforms
            
            # Parallel optimization execution
            optimization_tasks = []
            
            # SEO optimization
            if OptimizationType.SEO in config.optimization_types:
                optimization_tasks.append(
                    self.seo_optimizer.optimize_seo_metadata(content, content_type, config.target_keywords)
                )
            
            # Quality assessment
            if OptimizationType.QUALITY in config.optimization_types:
                optimization_tasks.append(
                    self.quality_optimizer.assess_content_quality(content, content_type)
                )
            
            # Execute base optimizations
            base_results = await asyncio.gather(*optimization_tasks, return_exceptions=True)
            
            seo_metadata = base_results[0] if len(base_results) > 0 and not isinstance(base_results[0], Exception) else SEOMetadata(title="", description="", keywords=[])
            quality_metrics = base_results[1] if len(base_results) > 1 and not isinstance(base_results[1], Exception) else QualityMetrics(0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
            
            # Social media optimizations for each platform
            social_optimizations = []
            if OptimizationType.SOCIAL_MEDIA in config.optimization_types:
                social_tasks = [
                    self.social_optimizer.optimize_for_platform(content, platform, content_type)
                    for platform in platforms if platform in [
                        OptimizationPlatform.INSTAGRAM, OptimizationPlatform.TIKTOK,
                        OptimizationPlatform.YOUTUBE, OptimizationPlatform.TWITTER,
                        OptimizationPlatform.LINKEDIN, OptimizationPlatform.FACEBOOK
                    ]
                ]
                
                if social_tasks:
                    social_results = await asyncio.gather(*social_tasks, return_exceptions=True)
                    social_optimizations = [
                        result for result in social_results
                        if not isinstance(result, Exception)
                    ]
            
            # Generate optimization suggestions
            suggestions = await self._generate_optimization_suggestions(
                content, seo_metadata, social_optimizations, quality_metrics
            )
            
            # Predict performance
            performance_predictions = await self._predict_content_performance(
                content, seo_metadata, social_optimizations, quality_metrics
            )
            
            # Create optimized content version
            optimized_content = await self._create_optimized_content(
                content, seo_metadata, quality_metrics
            )
            
            # Compile comprehensive result
            result = OptimizationResult(
                content_id=content_id,
                original_content=content,
                optimized_content=optimized_content,
                seo_metadata=seo_metadata,
                social_optimizations=social_optimizations,
                quality_metrics=quality_metrics,
                optimization_suggestions=suggestions,
                performance_predictions=performance_predictions
            )
            
            # Cache result
            self.optimization_cache[content_id] = result
            
            logger.info(f"Comprehensive optimization completed for content {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Comprehensive optimization failed: {e}")
            return OptimizationResult(
                content_id=str(uuid.uuid4()),
                original_content=content,
                optimized_content=content,
                seo_metadata=SEOMetadata(title="", description="", keywords=[]),
                social_optimizations=[],
                quality_metrics=QualityMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                optimization_suggestions=[],
                performance_predictions={}
            )
    
    async def _generate_optimization_suggestions(
        self,
        content: str,
        seo_metadata: SEOMetadata,
        social_optimizations: List[SocialMediaOptimization],
        quality_metrics: QualityMetrics
    ) -> List[str]:
        """Generate actionable optimization suggestions"""
        suggestions = []
        
        # SEO suggestions
        if quality_metrics.seo_score < 0.7:
            suggestions.append("Improve SEO by adding more relevant keywords naturally throughout the content")
            
        if len(seo_metadata.keywords) < 5:
            suggestions.append("Research and include more targeted keywords for better search visibility")
        
        # Quality suggestions
        if quality_metrics.readability_score < 0.7:
            suggestions.append("Improve readability by using shorter sentences and simpler language")
        
        if quality_metrics.engagement_potential < 0.6:
            suggestions.append("Add more engaging elements like questions, calls-to-action, or emotional language")
        
        if quality_metrics.accessibility_score < 0.7:
            suggestions.append("Enhance accessibility with proper headings, alt text, and clear structure")
        
        # Social media suggestions
        for social_opt in social_optimizations:
            if len(social_opt.hashtags) < 3:
                suggestions.append(f"Add more relevant hashtags for {social_opt.platform.value} to increase discoverability")
        
        # Content length suggestions
        word_count = len(content.split())
        if word_count < 300:
            suggestions.append("Consider expanding content to at least 300 words for better SEO performance")
        elif word_count > 2000:
            suggestions.append("Consider breaking long content into multiple pieces for better engagement")
        
        return suggestions
    
    async def _predict_content_performance(
        self,
        content: str,
        seo_metadata: SEOMetadata,
        social_optimizations: List[SocialMediaOptimization],
        quality_metrics: QualityMetrics
    ) -> Dict[str, float]:
        """Predict content performance across platforms"""
        predictions = {}
        
        # Base performance prediction
        base_score = quality_metrics.overall_score
        
        # SEO performance prediction
        seo_score = (
            len(seo_metadata.keywords) / 10 * 0.3 +
            len(seo_metadata.description) / 160 * 0.3 +
            quality_metrics.seo_score * 0.4
        )
        predictions['search_visibility'] = min(seo_score, 1.0)
        
        # Social media performance predictions
        total_social_engagement = 0
        for social_opt in social_optimizations:
            platform_engagement = social_opt.engagement_predictions.get('engagement_rate', 0)
            total_social_engagement += platform_engagement
            predictions[f'{social_opt.platform.value}_engagement'] = platform_engagement
        
        if social_optimizations:
            predictions['avg_social_engagement'] = total_social_engagement / len(social_optimizations)
        
        # Overall content score
        predictions['overall_success_probability'] = (
            base_score * 0.4 +
            predictions.get('search_visibility', 0) * 0.3 +
            predictions.get('avg_social_engagement', 0) * 0.3
        )
        
        return predictions
    
    async def _create_optimized_content(
        self,
        original_content: str,
        seo_metadata: SEOMetadata,
        quality_metrics: QualityMetrics
    ) -> str:
        """Create optimized version of content"""
        optimized = original_content
        
        # Add SEO improvements if quality is low
        if quality_metrics.seo_score < 0.7:
            # Add primary keyword to beginning if not present
            if seo_metadata.keywords and seo_metadata.keywords[0].lower() not in optimized.lower()[:100]:
                optimized = f"{seo_metadata.keywords[0].title()}: {optimized}"
        
        # Improve readability if needed
        if quality_metrics.readability_score < 0.7:
            # Add paragraph breaks for long texts
            if len(optimized) > 500 and '\n\n' not in optimized:
                sentences = optimized.split('. ')
                if len(sentences) > 3:
                    mid_point = len(sentences) // 2
                    optimized = '. '.join(sentences[:mid_point]) + '.\n\n' + '. '.join(sentences[mid_point:])
        
        return optimized
    
    async def batch_optimize_content(
        self, 
        content_batch: List[Dict[str, Any]]
    ) -> List[OptimizationResult]:
        """Batch optimization for multiple content pieces"""
        try:
            tasks = [
                self.optimize_content_comprehensive(
                    content=item.get('content', ''),
                    content_type=ContentType(item.get('content_type', 'text')),
                    target_platforms=[OptimizationPlatform(p) for p in item.get('platforms', ['google'])]
                )
                for item in content_batch
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = [
                result for result in results 
                if not isinstance(result, Exception)
            ]
            
            logger.info(f"Batch optimization completed: {len(valid_results)}/{len(content_batch)} successful")
            return valid_results
            
        except Exception as e:
            logger.error(f"Batch optimization failed: {e}")
            return []
    
    async def get_optimization_analytics(
        self, 
        time_range: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Get optimization analytics and performance insights"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - time_range
            
            # Filter cached optimizations by time range
            recent_optimizations = [
                opt for opt in self.optimization_cache.values()
                if start_time <= opt.optimization_timestamp <= end_time
            ]
            
            if not recent_optimizations:
                return {'error': 'No optimization data available for the specified time range'}
            
            # Calculate analytics
            total_optimizations = len(recent_optimizations)
            avg_quality_score = sum(opt.quality_metrics.overall_score for opt in recent_optimizations) / total_optimizations
            avg_seo_score = sum(opt.quality_metrics.seo_score for opt in recent_optimizations) / total_optimizations
            
            # Platform distribution
            platform_counts = {}
            for opt in recent_optimizations:
                for social_opt in opt.social_optimizations:
                    platform = social_opt.platform.value
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            # Top suggestions
            all_suggestions = []
            for opt in recent_optimizations:
                all_suggestions.extend(opt.optimization_suggestions)
            
            suggestion_counts = {}
            for suggestion in all_suggestions:
                suggestion_counts[suggestion] = suggestion_counts.get(suggestion, 0) + 1
            
            top_suggestions = sorted(suggestion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'summary': {
                    'total_optimizations': total_optimizations,
                    'average_quality_score': avg_quality_score,
                    'average_seo_score': avg_seo_score,
                    'platform_distribution': platform_counts,
                    'top_optimization_suggestions': [suggestion for suggestion, count in top_suggestions]
                },
                'performance_trends': {
                    'quality_improvement': 'stable',  # Would calculate actual trends
                    'seo_improvement': 'improving',
                    'engagement_trends': 'positive'
                }
            }
            
        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            return {'error': str(e)}


# Backward compatibility classes for existing imports
class SEOMetadataOptimizer_Legacy:
    """Legacy wrapper for SEO optimizer"""
    def __init__(self, *args, **kwargs):
        config = OptimizationConfig()
        self.optimizer = SEOOptimizer(config)


class SocialMediaOptimizer_Legacy:
    """Legacy wrapper for social media optimizer"""
    def __init__(self, *args, **kwargs):
        config = OptimizationConfig()
        self.optimizer = SocialMediaOptimizer(config)


class MediaQualityOptimizer_Legacy:
    """Legacy wrapper for quality optimizer"""
    def __init__(self, *args, **kwargs):
        config = OptimizationConfig()
        self.optimizer = QualityOptimizer(config)


# Export all classes for consolidated import
__all__ = [
    'ContentOptimizationEngine',
    'SEOOptimizer',
    'SocialMediaOptimizer',
    'QualityOptimizer',
    'OptimizationConfig',
    'SEOMetadata',
    'SocialMediaOptimization',
    'QualityMetrics',
    'OptimizationResult',
    'OptimizationPlatform',
    'OptimizationType',
    'ContentType',
    # Legacy compatibility
    'SEOMetadataOptimizer_Legacy',
    'SocialMediaOptimizer_Legacy',
    'MediaQualityOptimizer_Legacy'
]