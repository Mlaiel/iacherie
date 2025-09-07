"""SEO Metadata Optimizer - Advanced Search Engine Optimization

Comprehensive SEO optimization engine with AI-powered keyword analysis,
metadata generation, and multi-platform optimization strategies.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

import asyncio
import hashlib
import json
import logging
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import uuid4

import aiofiles
import aiohttp
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOPlatform(str, Enum):
    """SEO optimization platforms"""
    GOOGLE = "google"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WEBSITE = "website"
    BLOG = "blog"
    PODCAST = "podcast"
    MARKETPLACE = "marketplace"


class ContentType(str, Enum):
    """Content types for SEO optimization"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    AVATAR = "avatar"
    VOICE = "voice"
    MIXED_MEDIA = "mixed_media"


class SEOPriority(str, Enum):
    """SEO optimization priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LanguageCode(str, Enum):
    """Supported languages for SEO"""
    EN = "en"
    DE = "de"
    FR = "fr"
    AR = "ar"
    ES = "es"
    IT = "it"
    PT = "pt"
    RU = "ru"
    ZH = "zh"
    JA = "ja"
    KO = "ko"


class SEOOptimizationRequest(BaseModel):
    """SEO optimization request model"""
    content_id: str
    content_type: ContentType
    original_metadata: Dict[str, Any] = Field(default_factory=dict)
    target_platforms: List[SEOPlatform] = Field(default_factory=list)
    target_languages: List[LanguageCode] = Field(default_factory=list)
    target_audience: Dict[str, Any] = Field(default_factory=dict)
    business_category: str = ""
    monetization_type: str = Field(default="organic", regex="^(organic|paid|affiliate|sponsored)$")
    priority: SEOPriority = SEOPriority.MEDIUM
    competitor_analysis: bool = False
    trend_analysis: bool = True
    local_seo: bool = False
    geographic_targeting: List[str] = Field(default_factory=list)
    brand_guidelines: Dict[str, Any] = Field(default_factory=dict)


class KeywordData(BaseModel):
    """Keyword analysis data"""
    keyword: str
    search_volume: int = 0
    competition_level: str = Field(default="medium", regex="^(low|medium|high)$")
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    cost_per_click: Optional[float] = None
    trend_direction: str = Field(default="stable", regex="^(rising|stable|declining)$")
    long_tail_variants: List[str] = Field(default_factory=list)
    related_keywords: List[str] = Field(default_factory=list)
    seasonal_trends: Dict[str, float] = Field(default_factory=dict)
    platform_specific_data: Dict[SEOPlatform, Dict[str, Any]] = Field(default_factory=dict)


class SEOMetadata(BaseModel):
    """Optimized SEO metadata"""
    platform: SEOPlatform
    language: LanguageCode
    title: str = ""
    description: str = ""
    keywords: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    alt_text: str = ""
    caption: str = ""
    tags: List[str] = Field(default_factory=list)
    category: str = ""
    thumbnail_text: str = ""
    meta_title: str = ""
    meta_description: str = ""
    og_title: str = ""
    og_description: str = ""
    og_image: str = ""
    twitter_card: str = ""
    schema_markup: Dict[str, Any] = Field(default_factory=dict)
    custom_fields: Dict[str, str] = Field(default_factory=dict)
    optimization_score: float = Field(default=0.0, ge=0.0, le=1.0)


class SEOOptimizationResult(BaseModel):
    """Complete SEO optimization result"""
    content_id: str
    optimization_timestamp: datetime = Field(default_factory=datetime.utcnow)
    platform_metadata: Dict[SEOPlatform, SEOMetadata] = Field(default_factory=dict)
    keyword_analysis: List[KeywordData] = Field(default_factory=list)
    primary_keywords: List[str] = Field(default_factory=list)
    secondary_keywords: List[str] = Field(default_factory=list)
    long_tail_keywords: List[str] = Field(default_factory=list)
    content_recommendations: List[str] = Field(default_factory=list)
    platform_specific_tips: Dict[SEOPlatform, List[str]] = Field(default_factory=dict)
    performance_predictions: Dict[str, float] = Field(default_factory=dict)
    optimization_score: float = Field(default=0.0, ge=0.0, le=1.0)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))


class KeywordAnalyzer:
    """Advanced keyword analysis and research engine"""
    
    def __init__(self):
        # Industry keyword categories
        self.industry_keywords = {
            "music": ["music", "song", "artist", "album", "concert", "melody", "lyrics", "beat", "production", "studio"],
            "photography": ["photo", "camera", "lens", "portrait", "landscape", "editing", "lighting", "composition"],
            "video": ["video", "film", "cinema", "movie", "production", "editing", "cinematography", "director"],
            "technology": ["tech", "software", "app", "digital", "innovation", "AI", "programming", "development"],
            "lifestyle": ["lifestyle", "life", "daily", "routine", "tips", "advice", "wellness", "health"],
            "business": ["business", "entrepreneur", "startup", "marketing", "growth", "strategy", "leadership"]
        }
        
        # Platform-specific keyword modifiers
        self.platform_modifiers = {
            SEOPlatform.YOUTUBE: ["tutorial", "how to", "review", "unboxing", "vlog", "guide", "tips", "walkthrough"],
            SEOPlatform.INSTAGRAM: ["aesthetic", "style", "inspiration", "daily", "mood", "vibes", "lifestyle"],
            SEOPlatform.TIKTOK: ["viral", "trend", "challenge", "quick", "short", "hack", "secret", "trending"],
            SEOPlatform.LINKEDIN: ["professional", "career", "industry", "insights", "tips", "networking", "expertise"],
            SEOPlatform.TWITTER: ["news", "update", "thread", "opinion", "breaking", "analysis", "discussion"],
            SEOPlatform.PINTEREST: ["ideas", "inspiration", "diy", "recipe", "design", "creative", "beautiful"]
        }
    
    async def analyze_keywords(
        self, 
        base_content: str,
        content_type: ContentType,
        target_platforms: List[SEOPlatform],
        business_category: str = "",
        target_audience: Dict[str, Any] = None
    ) -> List[KeywordData]:
        """Comprehensive keyword analysis"""
        
        try:
            logger.info(f"Starting keyword analysis for content type: {content_type}")
            
            keywords = []
            
            # Extract base keywords from content
            base_keywords = await self._extract_base_keywords(base_content)
            
            # Generate platform-specific keywords
            for platform in target_platforms:
                platform_keywords = await self._generate_platform_keywords(
                    base_keywords, platform, content_type
                )
                keywords.extend(platform_keywords)
            
            # Add industry-specific keywords
            if business_category:
                industry_keywords = await self._generate_industry_keywords(
                    business_category, base_keywords
                )
                keywords.extend(industry_keywords)
            
            # Add audience-targeted keywords
            if target_audience:
                audience_keywords = await self._generate_audience_keywords(
                    target_audience, base_keywords
                )
                keywords.extend(audience_keywords)
            
            # Analyze keyword performance
            analyzed_keywords = []
            for keyword in set(keywords):
                keyword_data = await self._analyze_keyword_performance(keyword, target_platforms)
                analyzed_keywords.append(keyword_data)
            
            # Sort by relevance and performance
            analyzed_keywords.sort(key=lambda k: k.relevance_score, reverse=True)
            
            logger.info(f"Keyword analysis completed: {len(analyzed_keywords)} keywords analyzed")
            
            return analyzed_keywords[:50]  # Return top 50 keywords
            
        except Exception as e:
            logger.error(f"Keyword analysis failed: {str(e)}")
            return []
    
    async def _extract_base_keywords(self, content: str) -> List[str]:
        """Extract base keywords from content"""
        
        # Clean and tokenize content
        words = re.findall(r'\w+', content.lower())
        
        # Remove stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", 
            "has", "had", "do", "does", "did", "will", "would", "could", "should"
        }
        
        # Filter meaningful words
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # Generate n-grams
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
        
        # Combine and return unique keywords
        all_keywords = keywords + bigrams + trigrams
        return list(set(all_keywords))
    
    async def _generate_platform_keywords(
        self, 
        base_keywords: List[str], 
        platform: SEOPlatform,
        content_type: ContentType
    ) -> List[str]:
        """Generate platform-specific keywords"""
        
        platform_keywords = []
        modifiers = self.platform_modifiers.get(platform, [])
        
        # Combine base keywords with platform modifiers
        for keyword in base_keywords[:10]:  # Top 10 base keywords
            for modifier in modifiers[:3]:  # Top 3 modifiers
                platform_keywords.extend([
                    f"{modifier} {keyword}",
                    f"{keyword} {modifier}",
                    f"best {keyword}",
                    f"{keyword} guide",
                    f"{keyword} tips"
                ])
        
        # Add content-type specific keywords
        if content_type == ContentType.VIDEO:
            platform_keywords.extend([f"{kw} video" for kw in base_keywords[:5]])
        elif content_type == ContentType.AUDIO:
            platform_keywords.extend([f"{kw} audio" for kw in base_keywords[:5]])
        elif content_type == ContentType.IMAGE:
            platform_keywords.extend([f"{kw} photo" for kw in base_keywords[:5]])
        
        return platform_keywords
    
    async def _generate_industry_keywords(
        self, 
        business_category: str, 
        base_keywords: List[str]
    ) -> List[str]:
        """Generate industry-specific keywords"""
        
        industry_keywords = []
        category_keywords = self.industry_keywords.get(business_category.lower(), [])
        
        # Combine industry keywords with base keywords
        for industry_kw in category_keywords[:5]:
            for base_kw in base_keywords[:3]:
                industry_keywords.extend([
                    f"{industry_kw} {base_kw}",
                    f"{base_kw} {industry_kw}",
                    f"professional {base_kw}",
                    f"{base_kw} expert"
                ])
        
        return industry_keywords
    
    async def _generate_audience_keywords(
        self, 
        target_audience: Dict[str, Any], 
        base_keywords: List[str]
    ) -> List[str]:
        """Generate audience-targeted keywords"""
        
        audience_keywords = []
        
        # Age-based keywords
        age_group = target_audience.get("age_group", "")
        if "teen" in age_group.lower():
            audience_keywords.extend([f"teen {kw}" for kw in base_keywords[:3]])
        elif "young" in age_group.lower():
            audience_keywords.extend([f"millennial {kw}" for kw in base_keywords[:3]])
        
        # Interest-based keywords
        interests = target_audience.get("interests", [])
        for interest in interests[:3]:
            audience_keywords.extend([f"{interest} {kw}" for kw in base_keywords[:3]])
        
        # Location-based keywords
        location = target_audience.get("location", "")
        if location:
            audience_keywords.extend([f"{location} {kw}" for kw in base_keywords[:3]])
        
        return audience_keywords
    
    async def _analyze_keyword_performance(
        self, 
        keyword: str, 
        platforms: List[SEOPlatform]
    ) -> KeywordData:
        """Analyze individual keyword performance"""
        
        # Simulate keyword analysis (replace with real API calls)
        await asyncio.sleep(0.001)  # Simulate API delay
        
        # Generate realistic performance data
        search_volume = max(100, len(keyword) * 50 + hash(keyword) % 10000)
        competition_level = ["low", "medium", "high"][hash(keyword) % 3]
        relevance_score = min(1.0, (len(keyword.split()) * 0.2 + 0.6))
        
        # Generate platform-specific data
        platform_data = {}
        for platform in platforms:
            platform_data[platform] = {
                "popularity": hash(f"{keyword}_{platform}") % 100,
                "engagement_rate": min(1.0, (hash(f"{keyword}_{platform}") % 50) / 100),
                "competition": competition_level
            }
        
        return KeywordData(
            keyword=keyword,
            search_volume=search_volume,
            competition_level=competition_level,
            relevance_score=relevance_score,
            cost_per_click=max(0.1, (hash(keyword) % 500) / 100) if competition_level == "high" else None,
            trend_direction=["rising", "stable", "declining"][hash(keyword) % 3],
            long_tail_variants=await self._generate_long_tail_variants(keyword),
            related_keywords=await self._find_related_keywords(keyword),
            platform_specific_data=platform_data
        )
    
    async def _generate_long_tail_variants(self, keyword: str) -> List[str]:
        """Generate long-tail keyword variants"""
        
        variants = []
        prefixes = ["best", "how to", "why", "what is", "where to", "when to"]
        suffixes = ["guide", "tips", "review", "tutorial", "2025", "for beginners"]
        
        for prefix in prefixes[:2]:
            variants.append(f"{prefix} {keyword}")
        
        for suffix in suffixes[:2]:
            variants.append(f"{keyword} {suffix}")
        
        return variants
    
    async def _find_related_keywords(self, keyword: str) -> List[str]:
        """Find related keywords"""
        
        related = []
        words = keyword.split()
        
        if len(words) > 1:
            # Generate variations by swapping words
            related.append(" ".join(reversed(words)))
            
            # Generate synonyms (simplified)
            synonyms = {
                "best": "top", "guide": "tutorial", "tips": "advice",
                "review": "analysis", "how": "ways", "create": "make"
            }
            
            for word in words:
                if word in synonyms:
                    new_keyword = keyword.replace(word, synonyms[word])
                    related.append(new_keyword)
        
        return related[:5]


class MetadataGenerator:
    """Platform-specific metadata generation"""
    
    def __init__(self):
        # Platform character limits
        self.platform_limits = {
            SEOPlatform.YOUTUBE: {"title": 100, "description": 5000, "tags": 500},
            SEOPlatform.FACEBOOK: {"title": 85, "description": 155, "post": 63206},
            SEOPlatform.INSTAGRAM: {"caption": 2200, "hashtags": 30, "title": 125},
            SEOPlatform.TWITTER: {"text": 280, "title": 70},
            SEOPlatform.LINKEDIN: {"title": 150, "description": 160, "post": 3000},
            SEOPlatform.TIKTOK: {"caption": 150, "hashtags": 100, "title": 100}
        }
    
    async def generate_metadata(
        self, 
        platform: SEOPlatform,
        language: LanguageCode,
        keywords: List[KeywordData],
        original_metadata: Dict[str, Any],
        content_type: ContentType
    ) -> SEOMetadata:
        """Generate optimized metadata for specific platform"""
        
        try:
            logger.info(f"Generating metadata for {platform} in {language}")
            
            # Extract top keywords
            primary_keywords = [kw.keyword for kw in keywords[:3]]
            secondary_keywords = [kw.keyword for kw in keywords[3:8]]
            
            # Generate platform-specific content
            metadata = SEOMetadata(platform=platform, language=language)
            
            # Generate title
            metadata.title = await self._generate_title(
                platform, primary_keywords, original_metadata, language
            )
            
            # Generate description
            metadata.description = await self._generate_description(
                platform, primary_keywords, secondary_keywords, original_metadata, language
            )
            
            # Generate keywords and hashtags
            metadata.keywords = primary_keywords + secondary_keywords
            metadata.hashtags = await self._generate_hashtags(platform, keywords, language)
            
            # Generate platform-specific fields
            if platform == SEOPlatform.YOUTUBE:
                metadata.tags = await self._generate_youtube_tags(keywords)
                metadata.category = await self._determine_youtube_category(primary_keywords)
            
            elif platform == SEOPlatform.INSTAGRAM:
                metadata.caption = await self._generate_instagram_caption(
                    primary_keywords, original_metadata, language
                )
                metadata.alt_text = await self._generate_alt_text(
                    content_type, primary_keywords, language
                )
            
            elif platform == SEOPlatform.FACEBOOK:
                metadata.og_title = metadata.title
                metadata.og_description = metadata.description
                metadata.meta_title = await self._generate_meta_title(metadata.title)
                metadata.meta_description = await self._generate_meta_description(metadata.description)
            
            # Generate schema markup
            metadata.schema_markup = await self._generate_schema_markup(
                platform, content_type, metadata, original_metadata
            )
            
            # Calculate optimization score
            metadata.optimization_score = await self._calculate_optimization_score(
                platform, metadata, keywords
            )
            
            logger.info(f"Metadata generated for {platform}: Score {metadata.optimization_score:.2f}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata generation failed for {platform}: {str(e)}")
            return SEOMetadata(platform=platform, language=language)
    
    async def _generate_title(
        self, 
        platform: SEOPlatform,
        primary_keywords: List[str],
        original_metadata: Dict[str, Any],
        language: LanguageCode
    ) -> str:
        """Generate optimized title"""
        
        original_title = original_metadata.get("title", "")
        primary_keyword = primary_keywords[0] if primary_keywords else ""
        
        # Platform-specific title generation
        if platform == SEOPlatform.YOUTUBE:
            if primary_keyword and primary_keyword.lower() not in original_title.lower():
                title = f"{primary_keyword} | {original_title}"
            else:
                title = original_title
        elif platform == SEOPlatform.INSTAGRAM:
            title = f"✨ {primary_keyword} {original_title}"
        elif platform == SEOPlatform.TIKTOK:
            title = f"{primary_keyword} 🔥 {original_title}"
        elif platform == SEOPlatform.LINKEDIN:
            title = f"Professional {primary_keyword}: {original_title}"
        else:
            title = f"{primary_keyword} - {original_title}" if primary_keyword else original_title
        
        # Truncate to platform limits
        max_length = self.platform_limits.get(platform, {}).get("title", 100)
        return title[:max_length].strip()
    
    async def _generate_description(
        self,
        platform: SEOPlatform,
        primary_keywords: List[str],
        secondary_keywords: List[str],
        original_metadata: Dict[str, Any],
        language: LanguageCode
    ) -> str:
        """Generate optimized description"""
        
        original_description = original_metadata.get("description", "")
        
        # Build description components
        components = []
        
        # Hook/opening
        if primary_keywords:
            hook = f"Discover {primary_keywords[0]}"
            components.append(hook)
        
        # Original content
        if original_description:
            components.append(original_description)
        
        # Value proposition
        if secondary_keywords:
            value_prop = f"Learn about {', '.join(secondary_keywords[:2])}"
            components.append(value_prop)
        
        # Platform-specific additions
        if platform == SEOPlatform.YOUTUBE:
            components.append("👍 Like and subscribe for more content!")
        elif platform == SEOPlatform.INSTAGRAM:
            components.append("💫 Follow for daily inspiration")
        elif platform == SEOPlatform.LINKEDIN:
            components.append("Connect with me for professional insights")
        
        description = " ".join(components)
        
        # Truncate to platform limits
        max_length = self.platform_limits.get(platform, {}).get("description", 1000)
        return description[:max_length].strip()
    
    async def _generate_hashtags(
        self,
        platform: SEOPlatform,
        keywords: List[KeywordData],
        language: LanguageCode
    ) -> List[str]:
        """Generate platform-optimized hashtags"""
        
        hashtags = []
        
        # Convert keywords to hashtags
        for keyword in keywords[:15]:
            # Clean keyword for hashtag
            hashtag = re.sub(r'[^a-zA-Z0-9]', '', keyword.keyword.replace(' ', ''))
            if len(hashtag) > 2:
                hashtags.append(f"#{hashtag}")
        
        # Add platform-specific trending hashtags
        platform_hashtags = {
            SEOPlatform.INSTAGRAM: ["#instagood", "#photooftheday", "#instadaily"],
            SEOPlatform.TIKTOK: ["#fyp", "#viral", "#trending"],
            SEOPlatform.TWITTER: ["#breaking", "#news", "#thread"],
            SEOPlatform.LINKEDIN: ["#professional", "#career", "#business"]
        }
        
        if platform in platform_hashtags:
            hashtags.extend(platform_hashtags[platform])
        
        # Limit hashtags based on platform
        max_hashtags = 30 if platform == SEOPlatform.INSTAGRAM else 10
        return hashtags[:max_hashtags]
    
    async def _generate_youtube_tags(self, keywords: List[KeywordData]) -> List[str]:
        """Generate YouTube-specific tags"""
        
        tags = []
        for keyword in keywords[:12]:
            tags.append(keyword.keyword)
            # Add variations
            if ' ' in keyword.keyword:
                tags.extend(keyword.keyword.split())
        
        return list(set(tags))[:15]  # YouTube allows up to 15 tags
    
    async def _determine_youtube_category(self, keywords: List[str]) -> str:
        """Determine YouTube category based on keywords"""
        
        category_mapping = {
            "music": "Music",
            "education": "Education", 
            "entertainment": "Entertainment",
            "technology": "Science & Technology",
            "gaming": "Gaming",
            "sports": "Sports",
            "travel": "Travel & Events",
            "food": "Howto & Style",
            "news": "News & Politics"
        }
        
        for keyword in keywords:
            for key, category in category_mapping.items():
                if key in keyword.lower():
                    return category
        
        return "Entertainment"  # Default category
    
    async def _generate_instagram_caption(
        self,
        keywords: List[str],
        original_metadata: Dict[str, Any],
        language: LanguageCode
    ) -> str:
        """Generate Instagram caption"""
        
        caption_parts = []
        
        # Engaging hook
        if keywords:
            hook = f"✨ Amazing {keywords[0]} content!"
            caption_parts.append(hook)
        
        # Original content
        original_content = original_metadata.get("description", "")
        if original_content:
            caption_parts.append(original_content)
        
        # Call to action
        caption_parts.append("💫 What do you think? Let me know in the comments!")
        
        return "\n\n".join(caption_parts)
    
    async def _generate_alt_text(
        self,
        content_type: ContentType,
        keywords: List[str],
        language: LanguageCode
    ) -> str:
        """Generate accessibility alt text"""
        
        if content_type == ContentType.IMAGE:
            primary_keyword = keywords[0] if keywords else "image"
            return f"Image showing {primary_keyword}"
        elif content_type == ContentType.VIDEO:
            primary_keyword = keywords[0] if keywords else "video"
            return f"Video about {primary_keyword}"
        elif content_type == ContentType.AUDIO:
            primary_keyword = keywords[0] if keywords else "audio"
            return f"Audio content featuring {primary_keyword}"
        
        return "Media content"
    
    async def _generate_meta_title(self, title: str) -> str:
        """Generate HTML meta title"""
        return f"{title} | Ainflue Creator Platform"
    
    async def _generate_meta_description(self, description: str) -> str:
        """Generate HTML meta description"""
        meta_desc = description[:155]  # Meta description limit
        return f"{meta_desc}... | Discover amazing content on Ainflue"
    
    async def _generate_schema_markup(
        self,
        platform: SEOPlatform,
        content_type: ContentType,
        metadata: SEOMetadata,
        original_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate structured data schema markup"""
        
        schema = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": metadata.title,
            "description": metadata.description,
            "keywords": ", ".join(metadata.keywords),
            "author": {
                "@type": "Person",
                "name": original_metadata.get("creator", "Ainflue Creator")
            },
            "datePublished": datetime.utcnow().isoformat(),
            "publisher": {
                "@type": "Organization",
                "name": "Ainflue",
                "url": "https://ainflue.com"
            }
        }
        
        # Content-specific schema
        if content_type == ContentType.VIDEO:
            schema["@type"] = "VideoObject"
            schema["uploadDate"] = datetime.utcnow().isoformat()
            schema["duration"] = original_metadata.get("duration", "PT0M0S")
        elif content_type == ContentType.AUDIO:
            schema["@type"] = "AudioObject"
            schema["duration"] = original_metadata.get("duration", "PT0M0S")
        elif content_type == ContentType.IMAGE:
            schema["@type"] = "ImageObject"
            schema["width"] = original_metadata.get("width", 1920)
            schema["height"] = original_metadata.get("height", 1080)
        
        return schema
    
    async def _calculate_optimization_score(
        self,
        platform: SEOPlatform,
        metadata: SEOMetadata,
        keywords: List[KeywordData]
    ) -> float:
        """Calculate SEO optimization score"""
        
        score = 0.0
        max_score = 10.0
        
        # Title optimization (2 points)
        if metadata.title:
            score += 1.0
            if keywords and keywords[0].keyword.lower() in metadata.title.lower():
                score += 1.0
        
        # Description optimization (2 points)
        if metadata.description:
            score += 1.0
            if len(metadata.description) > 50:
                score += 1.0
        
        # Keywords optimization (2 points)
        if metadata.keywords:
            score += 1.0
            if len(metadata.keywords) >= 5:
                score += 1.0
        
        # Hashtags optimization (2 points)
        if metadata.hashtags:
            score += 1.0
            if len(metadata.hashtags) >= 5:
                score += 1.0
        
        # Platform-specific optimization (2 points)
        platform_limits = self.platform_limits.get(platform, {})
        
        # Title length optimization
        title_limit = platform_limits.get("title", 100)
        if metadata.title and len(metadata.title) <= title_limit:
            score += 1.0
        
        # Description length optimization
        desc_limit = platform_limits.get("description", 1000)
        if metadata.description and len(metadata.description) <= desc_limit:
            score += 1.0
        
        return min(score / max_score, 1.0)


class SEOMetadataOptimizer:
    """Main SEO metadata optimization engine"""
    
    def __init__(self):
        self.keyword_analyzer = KeywordAnalyzer()
        self.metadata_generator = MetadataGenerator()
        self.optimization_cache = {}
    
    async def optimize_content(self, request: SEOOptimizationRequest) -> SEOOptimizationResult:
        """Complete SEO optimization for content"""
        
        try:
            logger.info(f"Starting SEO optimization for content: {request.content_id}")
            
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self.optimization_cache:
                cached_result = self.optimization_cache[cache_key]
                if cached_result.expires_at > datetime.utcnow():
                    logger.info(f"Returning cached SEO optimization for: {request.content_id}")
                    return cached_result
            
            # Prepare content text for analysis
            content_text = await self._prepare_content_text(request.original_metadata)
            
            # Analyze keywords
            keywords = await self.keyword_analyzer.analyze_keywords(
                content_text,
                request.content_type,
                request.target_platforms,
                request.business_category,
                request.target_audience
            )
            
            # Generate metadata for each platform and language
            platform_metadata = {}
            
            for platform in request.target_platforms:
                for language in request.target_languages:
                    metadata = await self.metadata_generator.generate_metadata(
                        platform,
                        language,
                        keywords,
                        request.original_metadata,
                        request.content_type
                    )
                    platform_metadata[platform] = metadata
            
            # Categorize keywords
            primary_keywords = [kw.keyword for kw in keywords[:3]]
            secondary_keywords = [kw.keyword for kw in keywords[3:8]]
            long_tail_keywords = [kw.keyword for kw in keywords if len(kw.keyword.split()) >= 3]
            
            # Generate content recommendations
            recommendations = await self._generate_content_recommendations(
                keywords, request.content_type, request.target_platforms
            )
            
            # Generate platform-specific tips
            platform_tips = await self._generate_platform_tips(
                request.target_platforms, keywords, request.content_type
            )
            
            # Calculate overall optimization score
            optimization_score = await self._calculate_overall_score(
                platform_metadata, keywords, request
            )
            
            # Create result
            result = SEOOptimizationResult(
                content_id=request.content_id,
                platform_metadata=platform_metadata,
                keyword_analysis=keywords,
                primary_keywords=primary_keywords,
                secondary_keywords=secondary_keywords,
                long_tail_keywords=long_tail_keywords,
                content_recommendations=recommendations,
                platform_specific_tips=platform_tips,
                optimization_score=optimization_score
            )
            
            # Cache result
            self.optimization_cache[cache_key] = result
            
            logger.info(f"SEO optimization completed for: {request.content_id} - Score: {optimization_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"SEO optimization failed for {request.content_id}: {str(e)}")
            
            return SEOOptimizationResult(
                content_id=request.content_id,
                content_recommendations=[f"Optimization error: {str(e)}"],
                optimization_score=0.0
            )
    
    async def _prepare_content_text(self, metadata: Dict[str, Any]) -> str:
        """Prepare content text for keyword analysis"""
        
        text_parts = []
        
        # Extract text from various metadata fields
        for field in ["title", "description", "tags", "category", "keywords"]:
            if metadata.get(field):
                if isinstance(metadata[field], list):
                    text_parts.extend(metadata[field])
                else:
                    text_parts.append(str(metadata[field]))
        
        return " ".join(text_parts)
    
    async def _generate_content_recommendations(
        self,
        keywords: List[KeywordData],
        content_type: ContentType,
        platforms: List[SEOPlatform]
    ) -> List[str]:
        """Generate content optimization recommendations"""
        
        recommendations = []
        
        # Keyword-based recommendations
        if keywords:
            high_volume_keywords = [kw for kw in keywords if kw.search_volume > 1000]
            if high_volume_keywords:
                recommendations.append(f"Focus on high-volume keywords: {', '.join([kw.keyword for kw in high_volume_keywords[:3]])}")
            
            rising_keywords = [kw for kw in keywords if kw.trend_direction == "rising"]
            if rising_keywords:
                recommendations.append(f"Leverage trending keywords: {', '.join([kw.keyword for kw in rising_keywords[:3]])}")
        
        # Content-type specific recommendations
        if content_type == ContentType.VIDEO:
            recommendations.extend([
                "Create compelling thumbnails with text overlays",
                "Include keyword in the first 15 seconds of video",
                "Add closed captions for better accessibility"
            ])
        elif content_type == ContentType.AUDIO:
            recommendations.extend([
                "Create audiogram snippets for social media",
                "Provide detailed show notes with timestamps",
                "Include transcript for SEO benefits"
            ])
        elif content_type == ContentType.IMAGE:
            recommendations.extend([
                "Use descriptive filenames with keywords",
                "Optimize image dimensions for each platform",
                "Add comprehensive alt text"
            ])
        
        return recommendations
    
    async def _generate_platform_tips(
        self,
        platforms: List[SEOPlatform],
        keywords: List[KeywordData],
        content_type: ContentType
    ) -> Dict[SEOPlatform, List[str]]:
        """Generate platform-specific optimization tips"""
        
        platform_tips = {}
        
        for platform in platforms:
            tips = []
            
            if platform == SEOPlatform.YOUTUBE:
                tips.extend([
                    "Upload consistently at the same time",
                    "Create compelling thumbnails with 30% text maximum",
                    "Use end screens to promote other videos",
                    "Engage with comments within first 2 hours"
                ])
            elif platform == SEOPlatform.INSTAGRAM:
                tips.extend([
                    "Use 9-11 hashtags for optimal reach",
                    "Post stories regularly to boost engagement",
                    "Create Instagram Reels for increased visibility",
                    "Use location tags for local discovery"
                ])
            elif platform == SEOPlatform.TIKTOK:
                tips.extend([
                    "Hook viewers in the first 3 seconds",
                    "Use trending hashtags but limit to 3-5",
                    "Post 3-5 times per week consistently",
                    "Engage with comments and duets"
                ])
            else:
                tips.append("Optimize content for platform-specific audience")
            
            platform_tips[platform] = tips
        
        return platform_tips
    
    async def _calculate_overall_score(
        self,
        platform_metadata: Dict[SEOPlatform, SEOMetadata],
        keywords: List[KeywordData],
        request: SEOOptimizationRequest
    ) -> float:
        """Calculate overall SEO optimization score"""
        
        if not platform_metadata:
            return 0.0
        
        # Average platform scores
        platform_scores = [metadata.optimization_score for metadata in platform_metadata.values()]
        avg_platform_score = sum(platform_scores) / len(platform_scores)
        
        # Keyword quality score
        if keywords:
            avg_relevance = sum(kw.relevance_score for kw in keywords[:10]) / min(len(keywords), 10)
        else:
            avg_relevance = 0.0
        
        # Content completeness score
        completeness_score = 0.0
        if request.original_metadata.get("title"):
            completeness_score += 0.4
        if request.original_metadata.get("description"):
            completeness_score += 0.4
        if request.target_platforms:
            completeness_score += 0.2
        
        # Weight and combine scores
        overall_score = (avg_platform_score * 0.6) + (avg_relevance * 0.3) + (completeness_score * 0.1)
        
        return min(overall_score, 1.0)
    
    def _generate_cache_key(self, request: SEOOptimizationRequest) -> str:
        """Generate cache key for optimization request"""
        key_data = {
            "content_id": request.content_id,
            "content_type": request.content_type.value,
            "platforms": [p.value for p in request.target_platforms],
            "languages": [l.value for l in request.target_languages],
            "business_category": request.business_category
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()


# Factory function for easy usage
async def optimize_seo_metadata(
    content_id: str,
    content_type: ContentType,
    title: str = "",
    description: str = "",
    platforms: Optional[List[SEOPlatform]] = None,
    languages: Optional[List[LanguageCode]] = None,
    business_category: str = "",
    **kwargs
) -> SEOOptimizationResult:
    """Convenience function for SEO metadata optimization"""
    
    optimizer = SEOMetadataOptimizer()
    
    request = SEOOptimizationRequest(
        content_id=content_id,
        content_type=content_type,
        original_metadata={"title": title, "description": description, **kwargs},
        target_platforms=platforms or [SEOPlatform.GOOGLE, SEOPlatform.YOUTUBE, SEOPlatform.INSTAGRAM],
        target_languages=languages or [LanguageCode.EN],
        business_category=business_category
    )
    
    return await optimizer.optimize_content(request)


# Example usage
if __name__ == "__main__":
    async def demo():
        # Demo SEO optimization
        result = await optimize_seo_metadata(
            content_id="demo_123",
            content_type=ContentType.VIDEO,
            title="Amazing Music Production Tutorial",
            description="Learn how to create professional music with expert tips and techniques",
            platforms=[SEOPlatform.YOUTUBE, SEOPlatform.INSTAGRAM, SEOPlatform.TIKTOK],
            languages=[LanguageCode.EN, LanguageCode.DE],
            business_category="music",
            tags=["music", "production", "tutorial", "beats"]
        )
        
        print(f"Optimization Score: {result.optimization_score:.2f}")
        print(f"Primary Keywords: {result.primary_keywords}")
        print(f"Platform Metadata Generated: {len(result.platform_metadata)}")
        print(f"Recommendations: {result.content_recommendations}")
    
    asyncio.run(demo())