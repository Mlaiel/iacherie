"""
Content Optimization Module - Advanced SEO Content Enhancement

Comprehensive content optimization system with AI-powered analysis, metadata enhancement,
structure optimization, and schema markup generation for maximum SEO performance.

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
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urljoin, urlparse

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
from ...utils.html_parser import HTMLParser
from ...ml.content_models import ContentQualityModel, ReadabilityModel
from ...integrations.schema_apis import SchemaAPIManager

logger = logging.getLogger(__name__)

class OptimizationLevel(Enum):
    """Content optimization levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContentFormat(Enum):
    """Content format types"""
    HTML = "html"
    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"
    JSON = "json"
    XML = "xml"

class SchemaType(Enum):
    """Schema.org markup types"""
    ARTICLE = "Article"
    BLOG_POST = "BlogPosting"
    MUSIC_RECORDING = "MusicRecording"
    MUSIC_ALBUM = "MusicAlbum"
    VIDEO = "VideoObject"
    AUDIO = "AudioObject"
    PERSON = "Person"
    ORGANIZATION = "Organization"
    CREATIVE_WORK = "CreativeWork"
    REVIEW = "Review"
    EVENT = "Event"
    PRODUCT = "Product"

@dataclass
class OptimizationSuggestion:
    """Content optimization suggestion"""
    type: str
    priority: int  # 1-10, 10 being highest
    description: str
    current_value: str
    suggested_value: str
    impact_score: float
    difficulty: str
    implementation_time: int  # in minutes
    reasoning: str

@dataclass
class ContentAnalysis:
    """Comprehensive content analysis results"""
    content_id: str
    content_type: str
    word_count: int
    character_count: int
    sentence_count: int
    paragraph_count: int
    heading_structure: Dict[str, Any]
    keyword_density: Dict[str, float]
    readability_score: float
    content_quality_score: float
    technical_score: float
    seo_score: float
    suggestions: List[OptimizationSuggestion]
    analyzed_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class MetadataOptimization:
    """Optimized metadata results"""
    title: str
    description: str
    keywords: List[str]
    og_tags: Dict[str, str]
    twitter_tags: Dict[str, str]
    canonical_url: str
    robots: str
    structured_data: Dict[str, Any]
    optimization_score: float

class MetadataOptimizer:
    """
    Advanced metadata optimization engine.
    
    Features:
    - AI-powered title and description generation
    - Keyword-optimized metadata creation
    - Social media tag optimization
    - Canonical URL management
    - Robot directives optimization
    - Schema markup generation
    - Multi-language metadata support
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Components
        self.text_analyzer = TextAnalyzer()
        self.content_quality_model = None
        self.schema_api = SchemaAPIManager()
        
        # Configuration
        self.title_max_length = 60
        self.description_max_length = 160
        self.keywords_max_count = 10
        
        # Optimization patterns
        self.title_patterns = {
            'blog_post': [
                "{keyword} - {title}",
                "{title} | {brand}",
                "How to {action} - {keyword} Guide",
                "{number} {keyword} {tips/strategies/methods}"
            ],
            'music_track': [
                "{artist} - {title} ({genre})",
                "{title} by {artist} | {album}",
                "Listen to {title} - {artist}"
            ],
            'video': [
                "{title} - {creator}",
                "{keyword} Tutorial: {title}",
                "{title} | {duration} Video"
            ]
        }
        
        self.description_patterns = {
            'blog_post': [
                "Learn about {keyword} in this comprehensive guide. Discover {benefits} and get actionable tips.",
                "{keyword} explained: {summary}. Perfect for {audience}.",
                "Everything you need to know about {keyword}. {call_to_action}."
            ],
            'music_track': [
                "Listen to {title} by {artist}. {genre} music from {album}. {description}",
                "{artist}'s latest {genre} track: {title}. {mood} music perfect for {occasion}."
            ]
        }
        
    async def initialize(self):
        """Initialize metadata optimizer"""



        try:
            # Initialize text analyzer
            await self.text_analyzer.initialize()
            
            # Initialize content quality model
            self.content_quality_model = ContentQualityModel()
            await self.content_quality_model.load_model()
            
            # Initialize schema API
            await self.schema_api.initialize()
            
            logger.info("Metadata Optimizer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Metadata Optimizer: {e}")
            raise SEOError(f"Metadata Optimizer initialization failed: {e}")
    
    async def optimize_metadata(
        self,
        content_data: Dict[str, Any],
        target_keywords: List[str],
        content_type: str = "article",
        brand_name: str = "",
        optimization_level: OptimizationLevel = OptimizationLevel.ADVANCED
    ) -> MetadataOptimization:
        """
        Optimize metadata for maximum SEO performance.
        
        Args:
            content_data: Content information including title, content, etc.
            target_keywords: Primary keywords to optimize for
            content_type: Type of content (article, music, video, etc.)
            brand_name: Brand/company name
            optimization_level: Level of optimization to apply
        
        Returns:
            Optimized metadata package
        """



        try:
            current_title = content_data.get('title', '')
            current_description = content_data.get('description', '')
            content_text = content_data.get('content', '')
            
            # Generate optimized title
            optimized_title = await self._generate_optimized_title(
                current_title, content_text, target_keywords, content_type, brand_name
            )
            
            # Generate optimized description
            optimized_description = await self._generate_optimized_description(
                current_description, content_text, target_keywords, content_type
            )
            
            # Optimize keywords
            optimized_keywords = await self._optimize_keywords(
                target_keywords, content_text, content_type
            )
            
            # Generate Open Graph tags
            og_tags = await self._generate_og_tags(
                optimized_title, optimized_description, content_data
            )
            
            # Generate Twitter Card tags
            twitter_tags = await self._generate_twitter_tags(
                optimized_title, optimized_description, content_data
            )
            
            # Generate canonical URL
            canonical_url = await self._generate_canonical_url(content_data)
            
            # Generate robots directive
            robots = await self._generate_robots_directive(content_data, optimization_level)
            
            # Generate structured data
            structured_data = await self._generate_structured_data(
                content_data, content_type, optimized_title, optimized_description
            )
            
            # Calculate optimization score
            optimization_score = await self._calculate_metadata_score(
                optimized_title, optimized_description, optimized_keywords,
                target_keywords, content_type
            )
            
            return MetadataOptimization(
                title=optimized_title,
                description=optimized_description,
                keywords=optimized_keywords,
                og_tags=og_tags,
                twitter_tags=twitter_tags,
                canonical_url=canonical_url,
                robots=robots,
                structured_data=structured_data,
                optimization_score=optimization_score
            )
            
        except Exception as e:
            logger.error(f"Metadata optimization error: {e}")
            raise SEOError(f"Metadata optimization failed: {e}")
    
    async def _generate_optimized_title(
        self,
        current_title: str,
        content: str,
        keywords: List[str],
        content_type: str,
        brand_name: str
    ) -> str:
        """Generate SEO-optimized title"""



        try:
            if not keywords:
                return current_title[:self.title_max_length]
            
            primary_keyword = keywords[0]
            
            # Analyze current title
            title_analysis = await self.text_analyzer.analyze_title_seo(
                current_title, primary_keyword
            )
            
            # If current title is already good, optimize it minimally
            if title_analysis['seo_score'] > 0.8:
                optimized_title = await self._refine_existing_title(
                    current_title, primary_keyword, brand_name
                )
            else:
                # Generate new title using patterns
                optimized_title = await self._generate_new_title(
                    content, keywords, content_type, brand_name
                )
            
            # Ensure optimal length
            if len(optimized_title) > self.title_max_length:
                optimized_title = await self._truncate_title_smartly(
                    optimized_title, primary_keyword
                )
            
            return optimized_title
            
        except Exception as e:
            logger.error(f"Title optimization error: {e}")
            return current_title[:self.title_max_length]
    
    async def _generate_optimized_description(
        self,
        current_description: str,
        content: str,
        keywords: List[str],
        content_type: str
    ) -> str:
        """Generate SEO-optimized meta description"""



        try:
            if not keywords:
                return current_description[:self.description_max_length]
            
            primary_keyword = keywords[0]
            
            # Extract key information from content
            content_summary = await self.text_analyzer.generate_summary(
                content, max_sentences=2
            )
            
            # Identify key benefits/features
            key_points = await self.text_analyzer.extract_key_points(content)
            
            # Generate description using patterns
            if content_type in self.description_patterns:
                patterns = self.description_patterns[content_type]
                pattern = patterns[0]  # Use first pattern for now
                
                # Fill pattern variables
                description = pattern.format(
                    keyword=primary_keyword,
                    summary=content_summary,
                    benefits=', '.join(key_points[:3]),
                    audience='users interested in ' + primary_keyword,
                    call_to_action='Read more to learn everything you need to know.'
                )
            else:
                # Generic description generation
                description = f"Learn about {primary_keyword}. {content_summary}"
            
            # Ensure optimal length and keyword inclusion
            description = await self._optimize_description_length(
                description, primary_keyword, keywords[1:3] if len(keywords) > 1 else []
            )
            
            return description
            
        except Exception as e:
            logger.error(f"Description optimization error: {e}")
            return current_description[:self.description_max_length]
    
    async def _optimize_keywords(
        self,
        target_keywords: List[str],
        content: str,
        content_type: str
    ) -> List[str]:
        """Optimize keyword list for meta keywords tag"""



        try:
            # Analyze keyword relevance to content
            keyword_scores = {}
            
            for keyword in target_keywords:
                relevance_score = await self.text_analyzer.calculate_keyword_relevance(
                    keyword, content
                )
                keyword_scores[keyword] = relevance_score
            
            # Sort by relevance
            sorted_keywords = sorted(
                keyword_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Take top keywords up to max count
            optimized_keywords = [
                keyword for keyword, score in sorted_keywords[:self.keywords_max_count]
            ]
            
            return optimized_keywords
            
        except Exception as e:
            logger.error(f"Keywords optimization error: {e}")
            return target_keywords[:self.keywords_max_count]
    
    async def _generate_og_tags(
        self,
        title: str,
        description: str,
        content_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate Open Graph tags"""



        try:
            og_tags = {
                'og:title': title,
                'og:description': description,
                'og:type': self._map_content_type_to_og_type(content_data.get('type', 'article')),
                'og:url': content_data.get('url', ''),
                'og:site_name': content_data.get('site_name', ''),
                'og:locale': content_data.get('language', 'en_US')
            }
            
            # Add image if available
            if 'image' in content_data:
                og_tags.update({
                    'og:image': content_data['image'],
                    'og:image:alt': content_data.get('image_alt', title),
                    'og:image:width': content_data.get('image_width', '1200'),
                    'og:image:height': content_data.get('image_height', '630')
                })
            
            # Add video-specific tags
            if content_data.get('type') == 'video':
                og_tags.update({
                    'og:video': content_data.get('video_url', ''),
                    'og:video:type': content_data.get('video_type', 'video/mp4'),
                    'og:video:width': content_data.get('video_width', '1280'),
                    'og:video:height': content_data.get('video_height', '720')
                })
            
            # Add audio-specific tags
            if content_data.get('type') == 'audio':
                og_tags.update({
                    'og:audio': content_data.get('audio_url', ''),
                    'og:audio:type': content_data.get('audio_type', 'audio/mp3')
                })
            
            return {k: v for k, v in og_tags.items() if v}
            
        except Exception as e:
            logger.error(f"OpenGraph tags generation error: {e}")
            return {'og:title': title, 'og:description': description}
    
    async def _generate_twitter_tags(
        self,
        title: str,
        description: str,
        content_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate Twitter Card tags"""



        try:
            # Determine card type
            if 'video' in content_data:
                card_type = 'player'
            elif 'image' in content_data:
                card_type = 'summary_large_image'
            else:
                card_type = 'summary'
            
            twitter_tags = {
                'twitter:card': card_type,
                'twitter:title': title[:70],  # Twitter title limit
                'twitter:description': description[:200],  # Twitter description limit
                'twitter:site': content_data.get('twitter_site', ''),
                'twitter:creator': content_data.get('twitter_creator', '')
            }
            
            # Add image tags
            if 'image' in content_data:
                twitter_tags.update({
                    'twitter:image': content_data['image'],
                    'twitter:image:alt': content_data.get('image_alt', title)
                })
            
            # Add video tags
            if card_type == 'player' and 'video' in content_data:
                twitter_tags.update({
                    'twitter:player': content_data.get('video_player_url', ''),
                    'twitter:player:width': content_data.get('video_width', '1280'),
                    'twitter:player:height': content_data.get('video_height', '720')
                })
            
            return {k: v for k, v in twitter_tags.items() if v}
            
        except Exception as e:
            logger.error(f"Twitter tags generation error: {e}")
            return {'twitter:card': 'summary', 'twitter:title': title}
    
    def _map_content_type_to_og_type(self, content_type: str) -> str:
        """Map content type to Open Graph type"""
        mapping = {
            'article': 'article',
            'blog_post': 'article',
            'music_track': 'music.song',
            'music_album': 'music.album',
            'video': 'video.other',
            'podcast': 'video.other',
            'profile': 'profile',
            'product': 'product',
            'event': 'event'
        }
        return mapping.get(content_type, 'website')


class ContentStructureOptimizer:
    """
    Advanced content structure optimization engine.
    
    Features:
    - Heading hierarchy optimization
    - Paragraph structure analysis
    - Keyword distribution optimization
    - Internal linking suggestions
    - Content flow improvement
    - Readability enhancement
    - Schema markup integration
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Components
        self.text_analyzer = TextAnalyzer()
        self.html_parser = HTMLParser()
        self.readability_model = None
        
        # Configuration
        self.ideal_paragraph_length = 150  # words
        self.max_sentence_length = 25  # words
        self.heading_keyword_density = 0.8  # 80% of headings should contain keywords
        
    async def initialize(self):
        """Initialize content structure optimizer"""



        try:
            await self.text_analyzer.initialize()
            await self.html_parser.initialize()
            
            # Initialize readability model
            self.readability_model = ReadabilityModel()
            await self.readability_model.load_model()
            
            logger.info("Content Structure Optimizer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Content Structure Optimizer: {e}")
            raise SEOError(f"Content Structure Optimizer initialization failed: {e}")
    
    async def optimize_title(
        self,
        content_data: Dict[str, Any],
        target_keywords: List[str]
    ) -> Dict[str, Any]:
        """Optimize content title for SEO"""



        try:
            current_title = content_data.get('title', '')
            content_text = content_data.get('content', '')
            
            if not current_title:
                # Generate title from content
                suggested_titles = await self._generate_title_suggestions(
                    content_text, target_keywords
                )
                return {
                    'current_title': '',
                    'optimized_title': suggested_titles[0] if suggested_titles else 'Untitled',
                    'alternatives': suggested_titles[1:6],
                    'optimization_notes': [
                        'No title provided, generated from content analysis',
                        f'Optimized for primary keyword: {target_keywords[0] if target_keywords else "N/A"}'
                    ]
                }
            
            # Analyze current title
            title_analysis = await self._analyze_title_structure(
                current_title, target_keywords, content_text
            )
            
            # Generate optimization suggestions
            suggestions = await self._generate_title_optimization_suggestions(
                current_title, title_analysis, target_keywords
            )
            
            # Create optimized version
            optimized_title = await self._apply_title_optimizations(
                current_title, suggestions, target_keywords
            )
            
            return {
                'current_title': current_title,
                'optimized_title': optimized_title,
                'analysis': title_analysis,
                'suggestions': suggestions,
                'improvement_score': await self._calculate_title_improvement_score(
                    current_title, optimized_title, target_keywords
                )
            }
            
        except Exception as e:
            logger.error(f"Title optimization error: {e}")
            raise SEOError(f"Title optimization failed: {e}")
    
    async def optimize_structure(
        self,
        content_data: Dict[str, Any],
        target_keywords: List[str]
    ) -> Dict[str, Any]:
        """Optimize overall content structure"""



        try:
            content_text = content_data.get('content', '')
            content_format = content_data.get('format', 'html')
            
            # Parse and analyze current structure
            if content_format == 'html':
                structure_analysis = await self._analyze_html_structure(
                    content_text, target_keywords
                )
            else:
                structure_analysis = await self._analyze_text_structure(
                    content_text, target_keywords
                )
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_structure_suggestions(
                structure_analysis, target_keywords
            )
            
            # Create optimized structure
            optimized_content = await self._apply_structure_optimizations(
                content_text, optimization_suggestions, content_format
            )
            
            # Generate heading recommendations
            heading_recommendations = await self._generate_heading_recommendations(
                structure_analysis, target_keywords
            )
            
            # Analyze paragraph structure
            paragraph_analysis = await self._analyze_paragraph_structure(content_text)
            
            # Generate internal linking suggestions
            internal_link_suggestions = await self._generate_internal_link_suggestions(
                content_text, target_keywords
            )
            
            return {
                'current_structure': structure_analysis,
                'optimized_content': optimized_content,
                'optimization_suggestions': optimization_suggestions,
                'heading_recommendations': heading_recommendations,
                'paragraph_analysis': paragraph_analysis,
                'internal_link_suggestions': internal_link_suggestions,
                'readability_improvement': await self._calculate_readability_improvement(
                    content_text, optimized_content
                ),
                'seo_improvement_score': await self._calculate_structure_seo_improvement(
                    structure_analysis, optimization_suggestions
                )
            }
            
        except Exception as e:
            logger.error(f"Structure optimization error: {e}")
            raise SEOError(f"Structure optimization failed: {e}")
    
    async def _analyze_html_structure(
        self,
        html_content: str,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """Analyze HTML content structure"""



        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract headings
            headings = []
            for level in range(1, 7):
                for heading in soup.find_all(f'h{level}'):
                    headings.append({
                        'level': level,
                        'text': heading.get_text().strip(),
                        'has_keyword': any(kw.lower() in heading.get_text().lower() for kw in keywords)
                    })
            
            # Extract paragraphs
            paragraphs = []
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                if text:
                    paragraphs.append({
                        'text': text,
                        'word_count': len(text.split()),
                        'sentence_count': len(re.split(r'[.!?]+', text)),
                        'has_keyword': any(kw.lower() in text.lower() for kw in keywords)
                    })
            
            # Analyze images
            images = []
            for img in soup.find_all('img'):
                images.append({
                    'src': img.get('src', ''),
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'has_alt': bool(img.get('alt')),
                    'alt_has_keyword': any(kw.lower() in (img.get('alt', '')).lower() for kw in keywords)
                })
            
            # Analyze links
            links = []
            for link in soup.find_all('a'):
                href = link.get('href', '')
                text = link.get_text().strip()
                if text:
                    links.append({
                        'href': href,
                        'text': text,
                        'is_external': href.startswith(('http://', 'https://')) and not any(domain in href for domain in ['localhost', '127.0.0.1']),
                        'has_keyword': any(kw.lower() in text.lower() for kw in keywords)
                    })
            
            return {
                'headings': headings,
                'paragraphs': paragraphs,
                'images': images,
                'links': links,
                'heading_hierarchy_valid': self._validate_heading_hierarchy([h['level'] for h in headings]),
                'keyword_distribution': await self._analyze_keyword_distribution(html_content, keywords),
                'content_length': len(soup.get_text().strip().split()),
                'structure_score': await self._calculate_structure_score(headings, paragraphs, keywords)
            }
            
        except Exception as e:
            logger.error(f"HTML structure analysis error: {e}")
            return {'error': str(e)}
    
    def _validate_heading_hierarchy(self, heading_levels: List[int]) -> bool:
        """Validate heading hierarchy (no skipped levels)"""
        if not heading_levels:
            return False
        
        # Should start with H1
        if heading_levels[0] != 1:
            return False
        
        # Check for gaps in hierarchy
        unique_levels = sorted(set(heading_levels))
        for i in range(len(unique_levels) - 1):
            if unique_levels[i + 1] - unique_levels[i] > 1:
                return False
        
        return True


class LinkBuilder:
    """
    Advanced link building and internal linking optimization.
    
    Features:
    - Internal linking opportunities
    - Anchor text optimization
    - Link authority distribution
    - Related content discovery
    - Link structure analysis
    - Contextual linking suggestions
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Components
        self.text_analyzer = TextAnalyzer()
        
        # Configuration
        self.max_internal_links_per_page = 10
        self.ideal_anchor_text_length = 4  # words
        
    async def initialize(self):
        """Initialize link builder"""



        try:
            await self.text_analyzer.initialize()
            
            logger.info("Link Builder initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Link Builder: {e}")
            raise SEOError(f"Link Builder initialization failed: {e}")
    
    async def build_content_links(
        self,
        content_data: Dict[str, Any],
        related_content: List[Dict[str, Any]],
        target_keywords: List[str]
    ) -> Dict[str, Any]:
        """Build optimized internal links for content"""



        try:
            content_text = content_data.get('content', '')
            
            # Find linking opportunities
            linking_opportunities = await self._find_linking_opportunities(
                content_text, related_content, target_keywords
            )
            
            # Optimize anchor texts
            optimized_anchors = await self._optimize_anchor_texts(
                linking_opportunities, target_keywords
            )
            
            # Distribute link authority
            authority_distribution = await self._calculate_link_authority_distribution(
                linking_opportunities, related_content
            )
            
            # Generate contextual suggestions
            contextual_suggestions = await self._generate_contextual_link_suggestions(
                content_text, related_content, target_keywords
            )
            
            return {
                'linking_opportunities': linking_opportunities,
                'optimized_anchors': optimized_anchors,
                'authority_distribution': authority_distribution,
                'contextual_suggestions': contextual_suggestions,
                'total_suggested_links': len(linking_opportunities),
                'link_optimization_score': await self._calculate_link_optimization_score(
                    linking_opportunities, optimized_anchors
                )
            }
            
        except Exception as e:
            logger.error(f"Link building error: {e}")
            raise SEOError(f"Link building failed: {e}")
