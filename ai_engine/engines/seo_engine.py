"""
SEO Engine - AI-Powered Search Engine Optimization

Advanced SEO optimization specifically designed for content creators:
- Musicians: Optimize for music discovery, streaming platforms
- Bloggers: Content SEO, keyword optimization, readability
- Photographers: Image SEO, portfolio optimization
- Comedians: Video SEO, social media optimization
- Multi-format creators: Cross-platform SEO strategies

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

 WARNING: This code is the intellectual property of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import hashlib
from urllib.parse import quote
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer

# Optional imports with fallbacks
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False

try:
    import yake
    YAKE_AVAILABLE = True
except ImportError:
    YAKE_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SEOMetadata:
    """SEO metadata for content"""
    title: str
    description: str
    keywords: List[str]
    tags: List[str]
    canonical_url: str = ""
    meta_title: str = ""
    meta_description: str = ""
    alt_text: str = ""
    structured_data: Dict[str, Any] = field(default_factory=dict)
    social_media_tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class PlatformOptimization:
    """Platform-specific SEO optimization"""
    platform: str
    title: str
    description: str
    tags: List[str]
    hashtags: List[str]
    optimal_posting_time: str
    content_format: str
    engagement_tips: List[str]


class SEOEngine:
    """
    AI-powered SEO engine for content creator optimization.
    
    Provides comprehensive SEO strategies for different creator types:
    - Content analysis and keyword extraction
    - Platform-specific optimization
    - Technical SEO recommendations
    - Performance tracking and improvement suggestions
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize SEO engine with configuration"""
        self.config = config or {}
        
        # Initialize NLP tools
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
        
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Platform-specific configurations
        self.platform_configs = {
            'youtube': {
                'title_max_length': 100,
                'description_max_length': 5000,
                'tags_max_count': 500,
                'optimal_keywords': 10,
                'thumbnail_required': True
            },
            'instagram': {
                'caption_max_length': 2200,
                'hashtags_max_count': 30,
                'hashtags_optimal': 11,
                'story_duration': 15
            },
            'tiktok': {
                'caption_max_length': 300,
                'hashtags_max_count': 100,
                'video_duration_optimal': 60,
                'trending_hashtags_weight': 0.7
            },
            'spotify': {
                'track_title_max_length': 100,
                'album_description_max_length': 1500,
                'genre_tags_max': 3,
                'playlist_optimization': True
            },
            'twitter': {
                'tweet_max_length': 280,
                'hashtags_max_count': 2,
                'thread_optimization': True,
                'media_impact': 0.8
            },
            'facebook': {
                'post_optimal_length': 80,
                'description_max_length': 2000,
                'video_captions_required': True,
                'link_preview_optimization': True
            }
        }
        
        logger.info("SEOEngine initialized successfully")
    
    async def optimize_content_metadata(
        self,
        analysis_result: Dict[str, Any],
        content_type: str,
        metadata: Dict[str, Any]
    ) -> SEOMetadata:
        """Generate SEO-optimized metadata for content"""
        
        logger.info(f"Optimizing metadata for {content_type} content")
        
        try:
            # Extract key information from analysis
            content_themes = analysis_result.get('themes', [])
            content_sentiment = analysis_result.get('sentiment', 'neutral')
            content_quality = analysis_result.get('quality_score', 5.0)
            
            # Generate optimized title
            optimized_title = await self._generate_seo_title(
                content_themes, content_type, metadata, content_sentiment
            )
            
            # Generate optimized description
            optimized_description = await self._generate_seo_description(
                analysis_result, content_type, metadata
            )
            
            # Extract and optimize keywords
            keywords = await self._extract_seo_keywords(
                analysis_result, content_type, metadata
            )
            
            # Generate tags
            tags = await self._generate_content_tags(
                keywords, content_themes, content_type
            )
            
            # Generate structured data
            structured_data = await self._generate_structured_data(
                analysis_result, content_type, metadata
            )
            
            # Generate social media tags
            social_tags = await self._generate_social_media_tags(
                optimized_title, optimized_description, content_type
            )
            
            seo_metadata = SEOMetadata(
                title=optimized_title,
                description=optimized_description,
                keywords=keywords,
                tags=tags,
                meta_title=await self._generate_meta_title(optimized_title),
                meta_description=await self._generate_meta_description(optimized_description),
                structured_data=structured_data,
                social_media_tags=social_tags
            )
            
            logger.info(f"SEO metadata optimization completed")
            return seo_metadata
            
        except Exception as e:
            logger.error(f"Error optimizing content metadata: {str(e)}")
            raise
    
    async def generate_platform_optimizations(
        self,
        seo_metadata: SEOMetadata,
        keywords: List[str],
        content_type: str
    ) -> Dict[str, PlatformOptimization]:
        """Generate platform-specific optimizations"""
        
        logger.info("Generating platform-specific optimizations")
        
        optimizations = {}
        
        for platform, config in self.platform_configs.items():
            try:
                optimization = await self._optimize_for_platform(
                    platform, seo_metadata, keywords, content_type, config
                )
                optimizations[platform] = optimization
                
            except Exception as e:
                logger.error(f"Error optimizing for {platform}: {str(e)}")
                continue
        
        logger.info(f"Generated optimizations for {len(optimizations)} platforms")
        return optimizations
    
    async def _generate_seo_title(
        self,
        themes: List[str],
        content_type: str,
        metadata: Dict[str, Any],
        sentiment: str
    ) -> str:
        """Generate SEO-optimized title"""
        
        # Base title from metadata or themes
        base_title = metadata.get('title', '')
        if not base_title and themes:
            base_title = themes[0].title()
        
        # Content type specific optimization
        if content_type == 'audio':
            # Music SEO optimization
            artist = metadata.get('artist', '')
            genre = metadata.get('genre', '')
            if artist:
                optimized_title = f"{base_title} - {artist}"
                if genre:
                    optimized_title += f" | {genre} Music"
            else:
                optimized_title = f"{base_title} | Original Music"
                
        elif content_type == 'video':
            # Video SEO optimization
            if 'comedy' in themes or 'funny' in base_title.lower():
                optimized_title = f"{base_title} | Funny Video"
            elif 'tutorial' in themes or 'how to' in base_title.lower():
                optimized_title = f"How to: {base_title} | Tutorial"
            else:
                optimized_title = f"{base_title} | Video Content"
                
        elif content_type == 'image':
            # Image/Photography SEO
            if 'portrait' in themes:
                optimized_title = f"{base_title} | Portrait Photography"
            elif 'landscape' in themes:
                optimized_title = f"{base_title} | Landscape Photography"
            else:
                optimized_title = f"{base_title} | Photography"
                
        elif content_type == 'text':
            # Blog/Text SEO
            if len(base_title.split()) < 4:
                # Expand short titles
                main_theme = themes[0] if themes else 'Content'
                optimized_title = f"Complete Guide to {base_title} | {main_theme}"
            else:
                optimized_title = base_title
                
        else:
            optimized_title = base_title
        
        # Ensure title is not too long (60 chars for Google)
        if len(optimized_title) > 60:
            optimized_title = optimized_title[:57] + "..."
        
        return optimized_title
    
    async def _generate_seo_description(
        self,
        analysis_result: Dict[str, Any],
        content_type: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Generate SEO-optimized description"""
        
        base_description = metadata.get('description', '')
        themes = analysis_result.get('themes', [])
        keywords = analysis_result.get('keywords', [])
        
        if not base_description:
            # Generate description from analysis
            if content_type == 'audio':
                description_template = "Experience this original {genre} track featuring {themes}. Perfect for {mood} moments and {audience}."
                description = description_template.format(
                    genre=metadata.get('genre', 'music'),
                    themes=' and '.join(themes[:2]),
                    mood=analysis_result.get('mood', 'relaxing'),
                    audience=analysis_result.get('target_audience', 'music lovers')
                )
            elif content_type == 'video':
                description_template = "Watch this engaging {type} video about {themes}. {call_to_action}"
                description = description_template.format(
                    type=metadata.get('video_type', 'content'),
                    themes=', '.join(themes[:3]),
                    call_to_action="Don't forget to like and subscribe!"
                )
            elif content_type == 'image':
                description_template = "Stunning {style} photography capturing {subject}. {technical_details}"
                description = description_template.format(
                    style=metadata.get('style', 'artistic'),
                    subject=', '.join(themes[:2]),
                    technical_details=f"Shot with {metadata.get('camera', 'professional equipment')}"
                )
            elif content_type == 'text':
                description_template = "Comprehensive guide covering {topics}. Learn about {keywords} and master {skills}."
                description = description_template.format(
                    topics=', '.join(themes[:3]),
                    keywords=', '.join(keywords[:5]),
                    skills=themes[0] if themes else 'the subject'
                )
            else:
                description = f"Quality {content_type} content featuring {', '.join(themes[:3])}"
        else:
            description = base_description
        
        # Optimize description length for SEO (155-160 chars for meta description)
        if len(description) > 155:
            description = description[:152] + "..."
        
        return description
    
    async def _extract_seo_keywords(
        self,
        analysis_result: Dict[str, Any],
        content_type: str,
        metadata: Dict[str, Any]
    ) -> List[str]:
        """Extract and optimize keywords for SEO"""
        
        keywords = set()
        
        # Add keywords from analysis
        if 'keywords' in analysis_result:
            keywords.update(analysis_result['keywords'])
        
        # Add themes as keywords
        if 'themes' in analysis_result:
            keywords.update(analysis_result['themes'])
        
        # Add metadata keywords
        if 'tags' in metadata:
            keywords.update(metadata['tags'])
        
        # Add content type specific keywords
        content_keywords = {
            'audio': ['music', 'song', 'track', 'audio', 'sound'],
            'video': ['video', 'watch', 'content', 'visual'],
            'image': ['photo', 'image', 'picture', 'photography', 'visual'],
            'text': ['article', 'blog', 'guide', 'tutorial', 'content']
        }
        
        if content_type in content_keywords:
            keywords.update(content_keywords[content_type])
        
        # Filter and rank keywords
        filtered_keywords = []
        for keyword in keywords:
            if (len(keyword) > 2 and 
                keyword.lower() not in self.stop_words and
                not keyword.isdigit()):
                filtered_keywords.append(keyword.lower())
        
        # Remove duplicates and limit to top 15 keywords
        unique_keywords = list(set(filtered_keywords))[:15]
        
        return unique_keywords
    
    async def _generate_content_tags(
        self,
        keywords: List[str],
        themes: List[str],
        content_type: str
    ) -> List[str]:
        """Generate content tags for categorization"""
        
        tags = set()
        
        # Add keywords as tags
        tags.update(keywords)
        
        # Add themes as tags
        tags.update([theme.lower().replace(' ', '') for theme in themes])
        
        # Add content type tags
        type_tags = {
            'audio': ['music', 'audio', 'sound', 'track'],
            'video': ['video', 'visual', 'content', 'media'],
            'image': ['photo', 'image', 'visual', 'art'],
            'text': ['article', 'blog', 'writing', 'content']
        }
        
        if content_type in type_tags:
            tags.update(type_tags[content_type])
        
        # Convert to list and limit
        tag_list = list(tags)[:20]
        
        return tag_list
    
    async def _generate_structured_data(
        self,
        analysis_result: Dict[str, Any],
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate structured data markup"""
        
        base_structured_data = {
            "@context": "https://schema.org",
            "name": metadata.get('title', 'Content'),
            "description": metadata.get('description', ''),
            "creator": {
                "@type": "Person",
                "name": metadata.get('creator', 'Creator')
            },
            "dateCreated": datetime.now(timezone.utc).isoformat(),
            "inLanguage": analysis_result.get('language', 'en')
        }
        
        # Content type specific structured data
        if content_type == 'audio':
            structured_data = {
                **base_structured_data,
                "@type": "AudioObject",
                "genre": metadata.get('genre', ''),
                "duration": metadata.get('duration', ''),
                "encodingFormat": metadata.get('format', 'audio/mpeg')
            }
        elif content_type == 'video':
            structured_data = {
                **base_structured_data,
                "@type": "VideoObject",
                "duration": metadata.get('duration', ''),
                "encodingFormat": metadata.get('format', 'video/mp4'),
                "thumbnailUrl": metadata.get('thumbnail', '')
            }
        elif content_type == 'image':
            structured_data = {
                **base_structured_data,
                "@type": "ImageObject",
                "width": metadata.get('width', ''),
                "height": metadata.get('height', ''),
                "encodingFormat": metadata.get('format', 'image/jpeg')
            }
        elif content_type == 'text':
            structured_data = {
                **base_structured_data,
                "@type": "Article",
                "wordCount": analysis_result.get('word_count', 0),
                "articleSection": ', '.join(analysis_result.get('themes', [])[:3])
            }
        else:
            structured_data = {
                **base_structured_data,
                "@type": "CreativeWork"
            }
        
        return structured_data
    
    async def _generate_social_media_tags(
        self,
        title: str,
        description: str,
        content_type: str
    ) -> Dict[str, str]:
        """Generate social media meta tags"""
        
        social_tags = {
            # Open Graph tags
            'og:title': title,
            'og:description': description,
            'og:type': self._get_og_type(content_type),
            
            # Twitter Card tags
            'twitter:card': 'summary_large_image',
            'twitter:title': title,
            'twitter:description': description
        }
        
        return social_tags
    
    def _get_og_type(self, content_type: str) -> str:
        """Get Open Graph type for content"""
        
        og_types = {
            'audio': 'music.song',
            'video': 'video.other',
            'image': 'article',  # Images usually accompany articles
            'text': 'article'
        }
        
        return og_types.get(content_type, 'article')
    
    async def _generate_meta_title(self, title: str) -> str:
        """Generate meta title tag"""
        # Meta title should be slightly different from H1 title
        return f"{title} | IA-Influencer-Agent"
    
    async def _generate_meta_description(self, description: str) -> str:
        """Generate meta description tag"""
        # Ensure meta description is within limits
        if len(description) > 160:
            return description[:157] + "..."
        return description
    
    async def _optimize_for_platform(
        self,
        platform: str,
        seo_metadata: SEOMetadata,
        keywords: List[str],
        content_type: str,
        config: Dict[str, Any]
    ) -> PlatformOptimization:
        """Optimize content for specific platform"""
        
        # Platform-specific title optimization
        platform_title = await self._optimize_platform_title(
            platform, seo_metadata.title, config
        )
        
        # Platform-specific description optimization
        platform_description = await self._optimize_platform_description(
            platform, seo_metadata.description, config
        )
        
        # Generate platform-specific hashtags
        hashtags = await self._generate_platform_hashtags(
            platform, keywords, content_type, config
        )
        
        # Generate platform-specific tags
        platform_tags = await self._generate_platform_tags(
            platform, seo_metadata.tags, config
        )
        
        # Get optimal posting time
        optimal_time = await self._get_optimal_posting_time(platform, content_type)
        
        # Generate engagement tips
        engagement_tips = await self._generate_engagement_tips(platform, content_type)
        
        return PlatformOptimization(
            platform=platform,
            title=platform_title,
            description=platform_description,
            tags=platform_tags,
            hashtags=hashtags,
            optimal_posting_time=optimal_time,
            content_format=await self._get_optimal_content_format(platform, content_type),
            engagement_tips=engagement_tips
        )
    
    async def _optimize_platform_title(
        self,
        platform: str,
        title: str,
        config: Dict[str, Any]
    ) -> str:
        """Optimize title for specific platform"""
        
        max_length = config.get('title_max_length', 100)
        
        if len(title) > max_length:
            return title[:max_length-3] + "..."
        
        # Platform-specific title formatting
        if platform == 'youtube':
            # YouTube titles should be descriptive and clickable
            return f"{title} [2025]"
        elif platform == 'tiktok':
            # TikTok titles should be engaging and trendy
            return f" {title} #Trending"
        elif platform == 'instagram':
            # Instagram titles should be visually appealing
            return f" {title}"
        
        return title
    
    async def _optimize_platform_description(
        self,
        platform: str,
        description: str,
        config: Dict[str, Any]
    ) -> str:
        """Optimize description for specific platform"""
        
        max_length = config.get('description_max_length', 2000)
        
        if len(description) > max_length:
            description = description[:max_length-3] + "..."
        
        # Platform-specific description formatting
        if platform == 'youtube':
            # YouTube descriptions should include timestamps and links
            return f"{description}\n\n Subscribe for more content!\n Let us know what you think in the comments!"
        elif platform == 'instagram':
            # Instagram descriptions should include call-to-actions
            return f"{description}\n\n Double tap if you love this!\n DM us for collaborations!"
        elif platform == 'tiktok':
            # TikTok descriptions should be short and engaging
            return f"{description} What do you think? "
        
        return description
    
    async def _generate_platform_hashtags(
        self,
        platform: str,
        keywords: List[str],
        content_type: str,
        config: Dict[str, Any]
    ) -> List[str]:
        """Generate platform-specific hashtags"""
        
        hashtags = []
        max_hashtags = config.get('hashtags_max_count', 30)
        
        # Convert keywords to hashtags
        for keyword in keywords:
            hashtag = f"#{keyword.replace(' ', '').replace('-', '').lower()}"
            hashtags.append(hashtag)
        
        # Platform-specific trending hashtags
        platform_hashtags = {
            'instagram': ['#content', '#creator', '#inspiration', '#art', '#creative'],
            'tiktok': ['#fyp', '#viral', '#trending', '#content', '#creator'],
            'twitter': ['#content', '#creator'],  # Twitter recommends fewer hashtags
            'youtube': [],  # YouTube uses tags differently
        }
        
        if platform in platform_hashtags:
            hashtags.extend(platform_hashtags[platform])
        
        # Content type specific hashtags
        content_hashtags = {
            'audio': ['#music', '#audio', '#song', '#track'],
            'video': ['#video', '#content', '#watch'],
            'image': ['#photography', '#photo', '#art', '#visual'],
            'text': ['#blog', '#article', '#writing', '#content']
        }
        
        if content_type in content_hashtags:
            hashtags.extend(content_hashtags[content_type])
        
        # Remove duplicates and limit
        unique_hashtags = list(dict.fromkeys(hashtags))[:max_hashtags]
        
        return unique_hashtags
    
    async def _generate_platform_tags(
        self,
        platform: str,
        tags: List[str],
        config: Dict[str, Any]
    ) -> List[str]:
        """Generate platform-specific tags"""
        
        max_tags = config.get('tags_max_count', 50)
        
        # Platform-specific tag optimization
        platform_tags = tags.copy()
        
        if platform == 'youtube':
            # YouTube tags should be specific and searchable
            platform_tags.extend(['content creator', 'original content', 'quality content'])
        elif platform == 'spotify':
            # Spotify tags should be genre-focused
            platform_tags.extend(['independent', 'original music', 'new artist'])
        
        return platform_tags[:max_tags]
    
    async def _get_optimal_posting_time(self, platform: str, content_type: str) -> str:
        """Get optimal posting time for platform"""
        
        # General optimal posting times based on research
        optimal_times = {
            'instagram': {
                'weekdays': '11:00-13:00, 19:00-21:00',
                'weekends': '10:00-12:00, 14:00-16:00'
            },
            'tiktok': {
                'weekdays': '06:00-09:00, 19:00-21:00',
                'weekends': '09:00-11:00, 19:00-21:00'
            },
            'youtube': {
                'weekdays': '14:00-16:00, 19:00-21:00',
                'weekends': '09:00-11:00, 14:00-16:00'
            },
            'twitter': {
                'weekdays': '09:00-10:00, 19:00-20:00',
                'weekends': '12:00-13:00'
            },
            'facebook': {
                'weekdays': '15:00-16:00, 20:00-21:00',
                'weekends': '12:00-14:00'
            }
        }
        
        return optimal_times.get(platform, {}).get('weekdays', '19:00-21:00')
    
    async def _get_optimal_content_format(self, platform: str, content_type: str) -> str:
        """Get optimal content format for platform"""
        
        format_recommendations = {
            'youtube': {
                'video': '16:9 aspect ratio, 1080p minimum',
                'audio': 'Upload with static image or visualizer',
                'image': 'Create slideshow video',
                'text': 'Create educational video'
            },
            'instagram': {
                'image': '1:1 square or 4:5 portrait',
                'video': '9:16 vertical for Reels',
                'audio': 'Create visualizer video',
                'text': 'Carousel post with quotes'
            },
            'tiktok': {
                'video': '9:16 vertical, 15-60 seconds',
                'audio': 'Add to trending sounds',
                'image': 'Create slideshow with music',
                'text': 'Text-overlay videos'
            }
        }
        
        return format_recommendations.get(platform, {}).get(content_type, 'Standard format')
    
    async def _generate_engagement_tips(self, platform: str, content_type: str) -> List[str]:
        """Generate platform-specific engagement tips"""
        
        general_tips = [
            "Post consistently at optimal times",
            "Engage with your audience in comments",
            "Use relevant hashtags strategically",
            "Create high-quality, original content",
            "Collaborate with other creators"
        ]
        
        platform_tips = {
            'youtube': [
                "Create compelling thumbnails",
                "Use end screens and cards",
                "Optimize video titles for search",
                "Add closed captions for accessibility"
            ],
            'instagram': [
                "Use Instagram Stories regularly",
                "Create visually appealing content",
                "Partner with micro-influencers",
                "Utilize Instagram Reels for better reach"
            ],
            'tiktok': [
                "Jump on trending sounds and challenges",
                "Keep videos under 30 seconds for better retention",
                "Use trending hashtags strategically",
                "Create content that encourages duets"
            ]
        }
        
        tips = general_tips.copy()
        if platform in platform_tips:
            tips.extend(platform_tips[platform])
        
        return tips[:8]  # Limit to 8 tips
