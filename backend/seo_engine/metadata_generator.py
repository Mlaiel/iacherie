"""Metadata Generator - AI-Powered SEO Metadata Generation Engine

Advanced metadata generation system for creating optimized meta tags, schema markup,
and structured data to maximize search engine visibility and performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class MetadataType(Enum):
    """Types of metadata to generate"""
    TITLE_TAG = "title_tag"
    META_DESCRIPTION = "meta_description"
    META_KEYWORDS = "meta_keywords"
    OPEN_GRAPH = "open_graph"
    TWITTER_CARDS = "twitter_cards"
    SCHEMA_MARKUP = "schema_markup"
    CANONICAL_URL = "canonical_url"
    ROBOTS_META = "robots_meta"


class SchemaType(Enum):
    """Types of schema markup"""
    ARTICLE = "Article"
    BLOG_POSTING = "BlogPosting"
    PRODUCT = "Product"
    ORGANIZATION = "Organization"
    PERSON = "Person"
    VIDEO_OBJECT = "VideoObject"
    IMAGE_OBJECT = "ImageObject"
    FAQ_PAGE = "FAQPage"
    HOW_TO = "HowTo"
    REVIEW = "Review"
    EVENT = "Event"
    LOCAL_BUSINESS = "LocalBusiness"


@dataclass
class MetaTags:
    """Complete meta tags structure"""
    title: str
    description: str
    keywords: List[str]
    canonical_url: str
    robots: str
    author: Optional[str] = None
    viewport: str = "width=device-width, initial-scale=1.0"
    charset: str = "UTF-8"
    language: str = "en"


@dataclass
class OpenGraphTags:
    """Open Graph meta tags for social sharing"""
    title: str
    description: str
    type: str = "article"
    url: Optional[str] = None
    image: Optional[str] = None
    image_alt: Optional[str] = None
    site_name: Optional[str] = None
    locale: str = "en_US"


@dataclass
class TwitterCardTags:
    """Twitter Card meta tags"""
    card: str = "summary_large_image"
    title: str = ""
    description: str = ""
    image: Optional[str] = None
    site: Optional[str] = None
    creator: Optional[str] = None


@dataclass
class SchemaMarkup:
    """Schema.org structured data"""
    schema_type: SchemaType
    data: Dict[str, Any]
    context: str = "https://schema.org"


@dataclass
class GeneratedMetadata:
    """Complete generated metadata package"""
    meta_tags: MetaTags
    open_graph: OpenGraphTags
    twitter_cards: TwitterCardTags
    schema_markups: List[SchemaMarkup]
    html_output: str
    json_ld_output: str
    performance_prediction: Dict[str, float]
    recommendations: List[str]


class MetadataGenerator:
    """AI-powered SEO metadata generation engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.site_name = self.config.get('site_name', 'Ainflue')
        self.default_author = self.config.get('default_author', 'Ainflue Team')
        self.base_url = self.config.get('base_url', 'https://ainflue.com')
        self.twitter_handle = self.config.get('twitter_handle', '@ainflue')
        self.default_image = self.config.get('default_image', f'{self.base_url}/images/default-og.jpg')
        
        # Length limits for different platforms
        self.limits = {
            'title_tag': {'min': 30, 'max': 60, 'optimal': 55},
            'meta_description': {'min': 120, 'max': 160, 'optimal': 155},
            'og_title': {'max': 95},
            'og_description': {'max': 300},
            'twitter_title': {'max': 70},
            'twitter_description': {'max': 200}
        }
        
        # Common schema templates
        self.schema_templates = self._initialize_schema_templates()
        
        logger.info("MetadataGenerator initialized with AI-powered generation")
    
    async def generate_metadata(
        self,
        content: str,
        target_keywords: List[str],
        content_type: str = "article",
        url_path: Optional[str] = None,
        images: Optional[List[str]] = None,
        author: Optional[str] = None,
        publish_date: Optional[datetime] = None
    ) -> GeneratedMetadata:
        """Generate comprehensive metadata for content"""
        try:
            logger.info(f"Generating metadata for {content_type} content")
            
            # Extract content insights
            content_insights = await self._analyze_content(content, target_keywords)
            
            # Generate meta tags
            meta_tags = await self._generate_meta_tags(
                content_insights, target_keywords, url_path
            )
            
            # Generate Open Graph tags
            open_graph = await self._generate_open_graph(
                content_insights, target_keywords, url_path, images
            )
            
            # Generate Twitter Card tags
            twitter_cards = await self._generate_twitter_cards(
                content_insights, target_keywords, images
            )
            
            # Generate schema markup
            schema_markups = await self._generate_schema_markup(
                content_insights, content_type, target_keywords,
                author or self.default_author, publish_date, url_path
            )
            
            # Generate HTML output
            html_output = await self._generate_html_output(
                meta_tags, open_graph, twitter_cards
            )
            
            # Generate JSON-LD output
            json_ld_output = await self._generate_json_ld_output(schema_markups)
            
            # Predict performance
            performance_prediction = await self._predict_metadata_performance(
                meta_tags, open_graph, twitter_cards, schema_markups
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                meta_tags, open_graph, twitter_cards, content_insights
            )
            
            result = GeneratedMetadata(
                meta_tags=meta_tags,
                open_graph=open_graph,
                twitter_cards=twitter_cards,
                schema_markups=schema_markups,
                html_output=html_output,
                json_ld_output=json_ld_output,
                performance_prediction=performance_prediction,
                recommendations=recommendations
            )
            
            logger.info("Metadata generation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Metadata generation failed: {e}")
            raise
    
    async def _analyze_content(
        self,
        content: str,
        target_keywords: List[str]
    ) -> Dict[str, Any]:
        """Analyze content to extract insights for metadata generation"""
        # Extract first paragraph for description
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        first_paragraph = paragraphs[0] if paragraphs else ""
        
        # Extract headings
        headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', content, re.IGNORECASE)
        main_heading = headings[0] if headings else ""
        
        # Count words and estimate reading time
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)  # Assuming 200 words per minute
        
        # Extract key phrases (simplified)
        sentences = re.split(r'[.!?]+', content)
        key_phrases = []
        for sentence in sentences[:5]:  # First 5 sentences
            words = sentence.split()
            if 5 <= len(words) <= 15:  # Reasonable phrase length
                key_phrases.append(sentence.strip())
        
        # Identify content topics
        topics = await self._extract_topics(content, target_keywords)
        
        return {
            'first_paragraph': first_paragraph,
            'main_heading': main_heading,
            'word_count': word_count,
            'reading_time': reading_time,
            'key_phrases': key_phrases,
            'topics': topics,
            'headings': headings
        }
    
    async def _extract_topics(self, content: str, target_keywords: List[str]) -> List[str]:
        """Extract main topics from content"""
        topics = set(target_keywords)
        
        # Simple topic extraction based on word frequency
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = {}
        
        for word in words:
            if word not in ['that', 'this', 'with', 'from', 'they', 'have', 'been', 'will', 'would', 'could']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most frequent words as topics
        frequent_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        topics.update([word for word, freq in frequent_words if freq >= 3])
        
        return list(topics)[:15]
    
    async def _generate_meta_tags(
        self,
        content_insights: Dict[str, Any],
        target_keywords: List[str],
        url_path: Optional[str] = None
    ) -> MetaTags:
        """Generate standard HTML meta tags"""
        # Generate title
        title = await self._generate_title(content_insights, target_keywords)
        
        # Generate description
        description = await self._generate_description(content_insights, target_keywords)
        
        # Generate keywords
        keywords = target_keywords + content_insights['topics'][:10]
        
        # Generate canonical URL
        canonical_url = f"{self.base_url}{url_path}" if url_path else self.base_url
        
        # Generate robots directive
        robots = "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
        
        return MetaTags(
            title=title,
            description=description,
            keywords=keywords,
            canonical_url=canonical_url,
            robots=robots,
            author=self.default_author
        )
    
    async def _generate_title(
        self,
        content_insights: Dict[str, Any],
        target_keywords: List[str]
    ) -> str:
        """Generate optimized title tag"""
        if not target_keywords:
            base_title = content_insights.get('main_heading', 'Content')
            return f"{base_title} | {self.site_name}"
        
        primary_keyword = target_keywords[0]
        
        # Template-based title generation
        templates = [
            f"{primary_keyword.title()} - Complete Guide | {self.site_name}",
            f"How to {primary_keyword.title()} | {self.site_name}",
            f"{primary_keyword.title()}: Tips & Strategies | {self.site_name}",
            f"Best {primary_keyword.title()} Guide | {self.site_name}",
            f"{primary_keyword.title()} Explained | {self.site_name}"
        ]
        
        # Choose title that fits length requirements
        for template in templates:
            if self.limits['title_tag']['min'] <= len(template) <= self.limits['title_tag']['max']:
                return template
        
        # Fallback: truncate if necessary
        title = templates[0]
        if len(title) > self.limits['title_tag']['max']:
            title = title[:self.limits['title_tag']['max']-3] + "..."
        
        return title
    
    async def _generate_description(
        self,
        content_insights: Dict[str, Any],
        target_keywords: List[str]
    ) -> str:
        """Generate optimized meta description"""
        primary_keyword = target_keywords[0] if target_keywords else "content"
        
        # Use first paragraph if available and suitable
        first_paragraph = content_insights.get('first_paragraph', '')
        if first_paragraph and self.limits['meta_description']['min'] <= len(first_paragraph) <= self.limits['meta_description']['max']:
            return first_paragraph
        
        # Generate description from templates
        templates = [
            f"Learn everything about {primary_keyword} with our comprehensive guide. "
            f"Get expert tips, strategies, and actionable insights for better results.",
            
            f"Discover the best {primary_keyword} techniques and proven strategies. "
            f"Step-by-step tutorials and expert advice for optimal performance.",
            
            f"Complete {primary_keyword} resource with practical examples and tips. "
            f"Master the essentials and achieve better results today."
        ]
        
        # Choose description that fits length requirements
        for template in templates:
            if self.limits['meta_description']['min'] <= len(template) <= self.limits['meta_description']['max']:
                return template
        
        # Fallback: adjust first template
        description = templates[0]
        if len(description) > self.limits['meta_description']['max']:
            description = description[:self.limits['meta_description']['max']-3] + "..."
        
        return description
    
    async def _generate_open_graph(
        self,
        content_insights: Dict[str, Any],
        target_keywords: List[str],
        url_path: Optional[str] = None,
        images: Optional[List[str]] = None
    ) -> OpenGraphTags:
        """Generate Open Graph meta tags for social sharing"""
        # Generate OG title (shorter than regular title)
        og_title = await self._generate_og_title(content_insights, target_keywords)
        
        # Generate OG description
        og_description = await self._generate_og_description(content_insights, target_keywords)
        
        # Determine OG image
        og_image = images[0] if images else self.default_image
        og_image_alt = f"{target_keywords[0] if target_keywords else 'Content'} image"
        
        # Generate OG URL
        og_url = f"{self.base_url}{url_path}" if url_path else None
        
        return OpenGraphTags(
            title=og_title,
            description=og_description,
            url=og_url,
            image=og_image,
            image_alt=og_image_alt,
            site_name=self.site_name
        )
    
    async def _generate_og_title(
        self,
        content_insights: Dict[str, Any],
        target_keywords: List[str]
    ) -> str:
        """Generate Open Graph title"""
        if not target_keywords:
            return content_insights.get('main_heading', 'Content')
        
        primary_keyword = target_keywords[0]
        
        templates = [
            f"{primary_keyword.title()}: Complete Guide",
            f"How to Master {primary_keyword.title()}",
            f"Ultimate {primary_keyword.title()} Tips",
            f"Best {primary_keyword.title()} Strategies"
        ]
        
        # Choose title that fits OG length requirements
        for template in templates:
            if len(template) <= self.limits['og_title']['max']:
                return template
        
        # Fallback
        return f"{primary_keyword.title()}"
    
    async def _generate_og_description(
        self,
        content_insights: Dict[str, Any],
        target_keywords: List[str]
    ) -> str:
        """Generate Open Graph description"""
        primary_keyword = target_keywords[0] if target_keywords else "content"
        
        templates = [
            f"Comprehensive guide to {primary_keyword} with expert tips and strategies. "
            f"Learn proven techniques for better results.",
            
            f"Everything you need to know about {primary_keyword}. "
            f"Step-by-step tutorials and practical advice from experts."
        ]
        
        # Choose description that fits OG length requirements
        for template in templates:
            if len(template) <= self.limits['og_description']['max']:
                return template
        
        return templates[0][:self.limits['og_description']['max']-3] + "..."
    
    async def _generate_twitter_cards(
        self,
        content_insights: Dict[str, Any],
        target_keywords: List[str],
        images: Optional[List[str]] = None
    ) -> TwitterCardTags:
        """Generate Twitter Card meta tags"""
        # Generate Twitter title
        twitter_title = await self._generate_twitter_title(content_insights, target_keywords)
        
        # Generate Twitter description
        twitter_description = await self._generate_twitter_description(content_insights, target_keywords)
        
        # Determine Twitter image
        twitter_image = images[0] if images else self.default_image
        
        return TwitterCardTags(
            title=twitter_title,
            description=twitter_description,
            image=twitter_image,
            site=self.twitter_handle,
            creator=self.twitter_handle
        )
    
    async def _generate_twitter_title(
        self,
        content_insights: Dict[str, Any],
        target_keywords: List[str]
    ) -> str:
        """Generate Twitter Card title"""
        if not target_keywords:
            return content_insights.get('main_heading', 'Content')
        
        primary_keyword = target_keywords[0]
        
        templates = [
            f"{primary_keyword.title()} Guide",
            f"How to {primary_keyword.title()}",
            f"{primary_keyword.title()} Tips",
            f"Best {primary_keyword.title()}"
        ]
        
        # Choose title that fits Twitter length requirements
        for template in templates:
            if len(template) <= self.limits['twitter_title']['max']:
                return template
        
        return f"{primary_keyword.title()}"
    
    async def _generate_twitter_description(
        self,
        content_insights: Dict[str, Any],
        target_keywords: List[str]
    ) -> str:
        """Generate Twitter Card description"""
        primary_keyword = target_keywords[0] if target_keywords else "content"
        
        templates = [
            f"Learn {primary_keyword} with our comprehensive guide. Expert tips and strategies for better results.",
            f"Master {primary_keyword} with step-by-step tutorials and practical advice from experts."
        ]
        
        # Choose description that fits Twitter length requirements
        for template in templates:
            if len(template) <= self.limits['twitter_description']['max']:
                return template
        
        return templates[0][:self.limits['twitter_description']['max']-3] + "..."
    
    async def _generate_schema_markup(
        self,
        content_insights: Dict[str, Any],
        content_type: str,
        target_keywords: List[str],
        author: str,
        publish_date: Optional[datetime] = None,
        url_path: Optional[str] = None
    ) -> List[SchemaMarkup]:
        """Generate schema.org structured data markup"""
        schema_markups = []
        
        # Determine primary schema type
        if content_type in ['article', 'blog', 'post']:
            schema_type = SchemaType.BLOG_POSTING
        elif content_type == 'product':
            schema_type = SchemaType.PRODUCT
        elif content_type == 'video':
            schema_type = SchemaType.VIDEO_OBJECT
        elif content_type == 'faq':
            schema_type = SchemaType.FAQ_PAGE
        elif content_type == 'howto':
            schema_type = SchemaType.HOW_TO
        else:
            schema_type = SchemaType.ARTICLE
        
        # Generate primary schema
        primary_schema = await self._generate_primary_schema(
            schema_type, content_insights, target_keywords, author, publish_date, url_path
        )
        schema_markups.append(primary_schema)
        
        # Generate organization schema
        org_schema = await self._generate_organization_schema()
        schema_markups.append(org_schema)
        
        # Generate additional schemas based on content
        if content_insights.get('word_count', 0) > 1000:
            # Add Article schema for long-form content
            article_schema = await self._generate_article_schema(
                content_insights, target_keywords, author, publish_date, url_path
            )
            schema_markups.append(article_schema)
        
        return schema_markups
    
    async def _generate_primary_schema(
        self,
        schema_type: SchemaType,
        content_insights: Dict[str, Any],
        target_keywords: List[str],
        author: str,
        publish_date: Optional[datetime] = None,
        url_path: Optional[str] = None
    ) -> SchemaMarkup:
        """Generate primary schema markup"""
        base_data = {
            "@type": schema_type.value,
            "headline": content_insights.get('main_heading', target_keywords[0] if target_keywords else 'Content'),
            "author": {
                "@type": "Person",
                "name": author
            },
            "publisher": {
                "@type": "Organization",
                "name": self.site_name,
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{self.base_url}/images/logo.png"
                }
            }
        }
        
        # Add URL if available
        if url_path:
            base_data["url"] = f"{self.base_url}{url_path}"
        
        # Add publish date if available
        if publish_date:
            base_data["datePublished"] = publish_date.isoformat()
            base_data["dateModified"] = datetime.now().isoformat()
        
        # Add word count and reading time
        if content_insights.get('word_count'):
            base_data["wordCount"] = content_insights['word_count']
        
        if content_insights.get('reading_time'):
            base_data["timeRequired"] = f"PT{content_insights['reading_time']}M"
        
        # Add keywords
        if target_keywords:
            base_data["keywords"] = target_keywords
        
        # Schema-specific additions
        if schema_type == SchemaType.BLOG_POSTING:
            base_data["blogPost"] = True
            base_data["articleSection"] = target_keywords[0] if target_keywords else "General"
        
        elif schema_type == SchemaType.HOW_TO:
            # Add basic how-to structure
            base_data["totalTime"] = f"PT{content_insights.get('reading_time', 5)}M"
            base_data["supply"] = []
            base_data["tool"] = []
            base_data["step"] = []
        
        return SchemaMarkup(
            schema_type=schema_type,
            data=base_data
        )
    
    async def _generate_organization_schema(self) -> SchemaMarkup:
        """Generate organization schema markup"""
        org_data = {
            "@type": "Organization",
            "name": self.site_name,
            "url": self.base_url,
            "logo": {
                "@type": "ImageObject",
                "url": f"{self.base_url}/images/logo.png"
            },
            "sameAs": [
                f"https://twitter.com/{self.twitter_handle.replace('@', '')}",
                f"https://facebook.com/{self.site_name.lower()}",
                f"https://linkedin.com/company/{self.site_name.lower()}"
            ]
        }
        
        return SchemaMarkup(
            schema_type=SchemaType.ORGANIZATION,
            data=org_data
        )
    
    async def _generate_article_schema(
        self,
        content_insights: Dict[str, Any],
        target_keywords: List[str],
        author: str,
        publish_date: Optional[datetime] = None,
        url_path: Optional[str] = None
    ) -> SchemaMarkup:
        """Generate article schema markup"""
        article_data = {
            "@type": "Article",
            "headline": content_insights.get('main_heading', target_keywords[0] if target_keywords else 'Article'),
            "author": {
                "@type": "Person",
                "name": author
            },
            "publisher": {
                "@type": "Organization",
                "name": self.site_name
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"{self.base_url}{url_path}" if url_path else self.base_url
            }
        }
        
        if publish_date:
            article_data["datePublished"] = publish_date.isoformat()
            article_data["dateModified"] = datetime.now().isoformat()
        
        if target_keywords:
            article_data["about"] = target_keywords[0]
            article_data["keywords"] = target_keywords
        
        return SchemaMarkup(
            schema_type=SchemaType.ARTICLE,
            data=article_data
        )
    
    def _initialize_schema_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize common schema templates"""
        return {
            "article": {
                "@type": "Article",
                "headline": "",
                "author": {"@type": "Person", "name": ""},
                "publisher": {"@type": "Organization", "name": self.site_name},
                "datePublished": "",
                "dateModified": ""
            },
            "product": {
                "@type": "Product",
                "name": "",
                "description": "",
                "brand": {"@type": "Brand", "name": self.site_name},
                "offers": {
                    "@type": "Offer",
                    "price": "",
                    "priceCurrency": "USD"
                }
            },
            "video": {
                "@type": "VideoObject",
                "name": "",
                "description": "",
                "thumbnailUrl": "",
                "uploadDate": "",
                "duration": ""
            }
        }
    
    async def _generate_html_output(
        self,
        meta_tags: MetaTags,
        open_graph: OpenGraphTags,
        twitter_cards: TwitterCardTags
    ) -> str:
        """Generate complete HTML meta tags output"""
        html_parts = []
        
        # Basic meta tags
        html_parts.extend([
            f'<meta charset="{meta_tags.charset}">',
            f'<meta name="viewport" content="{meta_tags.viewport}">',
            f'<meta name="language" content="{meta_tags.language}">',
            f'<title>{meta_tags.title}</title>',
            f'<meta name="description" content="{meta_tags.description}">',
            f'<meta name="keywords" content="{", ".join(meta_tags.keywords)}">',
            f'<meta name="author" content="{meta_tags.author}">',
            f'<meta name="robots" content="{meta_tags.robots}">',
            f'<link rel="canonical" href="{meta_tags.canonical_url}">'
        ])
        
        # Open Graph tags
        html_parts.extend([
            f'<meta property="og:title" content="{open_graph.title}">',
            f'<meta property="og:description" content="{open_graph.description}">',
            f'<meta property="og:type" content="{open_graph.type}">',
            f'<meta property="og:site_name" content="{open_graph.site_name}">',
            f'<meta property="og:locale" content="{open_graph.locale}">'
        ])
        
        if open_graph.url:
            html_parts.append(f'<meta property="og:url" content="{open_graph.url}">')
        
        if open_graph.image:
            html_parts.extend([
                f'<meta property="og:image" content="{open_graph.image}">',
                f'<meta property="og:image:alt" content="{open_graph.image_alt}">'
            ])
        
        # Twitter Card tags
        html_parts.extend([
            f'<meta name="twitter:card" content="{twitter_cards.card}">',
            f'<meta name="twitter:title" content="{twitter_cards.title}">',
            f'<meta name="twitter:description" content="{twitter_cards.description}">'
        ])
        
        if twitter_cards.site:
            html_parts.append(f'<meta name="twitter:site" content="{twitter_cards.site}">')
        
        if twitter_cards.creator:
            html_parts.append(f'<meta name="twitter:creator" content="{twitter_cards.creator}">')
        
        if twitter_cards.image:
            html_parts.append(f'<meta name="twitter:image" content="{twitter_cards.image}">')
        
        return '\n'.join(html_parts)
    
    async def _generate_json_ld_output(self, schema_markups: List[SchemaMarkup]) -> str:
        """Generate JSON-LD structured data output"""
        json_ld_objects = []
        
        for schema in schema_markups:
            json_ld_object = {
                "@context": schema.context,
                **schema.data
            }
            json_ld_objects.append(json_ld_object)
        
        if len(json_ld_objects) == 1:
            json_output = json.dumps(json_ld_objects[0], indent=2)
        else:
            json_output = json.dumps({
                "@context": "https://schema.org",
                "@graph": json_ld_objects
            }, indent=2)
        
        return f'<script type="application/ld+json">\n{json_output}\n</script>'
    
    async def _predict_metadata_performance(
        self,
        meta_tags: MetaTags,
        open_graph: OpenGraphTags,
        twitter_cards: TwitterCardTags,
        schema_markups: List[SchemaMarkup]
    ) -> Dict[str, float]:
        """Predict metadata performance impact"""
        scores = {}
        
        # Title optimization score
        title_length = len(meta_tags.title)
        if self.limits['title_tag']['min'] <= title_length <= self.limits['title_tag']['max']:
            title_score = 100
        else:
            title_score = max(0, 100 - abs(title_length - self.limits['title_tag']['optimal']) * 2)
        scores['title_optimization'] = title_score
        
        # Description optimization score
        desc_length = len(meta_tags.description)
        if self.limits['meta_description']['min'] <= desc_length <= self.limits['meta_description']['max']:
            desc_score = 100
        else:
            desc_score = max(0, 100 - abs(desc_length - self.limits['meta_description']['optimal']) * 2)
        scores['description_optimization'] = desc_score
        
        # Social sharing optimization
        social_score = 85  # Base score for having OG and Twitter tags
        if open_graph.image:
            social_score += 10
        if twitter_cards.image:
            social_score += 5
        scores['social_optimization'] = min(100, social_score)
        
        # Schema markup score
        schema_score = len(schema_markups) * 25  # 25 points per schema type
        scores['structured_data'] = min(100, schema_score)
        
        # Overall prediction
        overall_performance = sum(scores.values()) / len(scores)
        scores['overall_seo_impact'] = round(overall_performance, 1)
        
        # Predict specific improvements
        scores['click_through_rate_improvement'] = round(overall_performance * 0.3, 1)
        scores['search_ranking_boost'] = round(overall_performance * 0.2, 1)
        scores['social_engagement_increase'] = round(social_score * 0.4, 1)
        
        return scores
    
    async def _generate_recommendations(
        self,
        meta_tags: MetaTags,
        open_graph: OpenGraphTags,
        twitter_cards: TwitterCardTags,
        content_insights: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Title optimization recommendations
        title_length = len(meta_tags.title)
        if title_length < self.limits['title_tag']['min']:
            recommendations.append(
                f"Title is too short ({title_length} chars). Consider expanding to {self.limits['title_tag']['optimal']} characters for better SEO."
            )
        elif title_length > self.limits['title_tag']['max']:
            recommendations.append(
                f"Title is too long ({title_length} chars). Shorten to under {self.limits['title_tag']['max']} characters to avoid truncation."
            )
        
        # Description optimization recommendations
        desc_length = len(meta_tags.description)
        if desc_length < self.limits['meta_description']['min']:
            recommendations.append(
                f"Meta description is too short ({desc_length} chars). Expand to {self.limits['meta_description']['optimal']} characters for better click-through rates."
            )
        elif desc_length > self.limits['meta_description']['max']:
            recommendations.append(
                f"Meta description is too long ({desc_length} chars). Shorten to under {self.limits['meta_description']['max']} characters to avoid truncation."
            )
        
        # Image recommendations
        if not open_graph.image or open_graph.image == self.default_image:
            recommendations.append(
                "Add a custom, high-quality image for better social media sharing and engagement."
            )
        
        # Keyword recommendations
        if len(meta_tags.keywords) < 5:
            recommendations.append(
                "Consider adding more relevant keywords to improve topical relevance and discoverability."
            )
        elif len(meta_tags.keywords) > 15:
            recommendations.append(
                "Too many keywords may dilute focus. Consider focusing on 10-15 most relevant keywords."
            )
        
        # Content-specific recommendations
        if content_insights.get('word_count', 0) > 2000:
            recommendations.append(
                "For long-form content, consider adding FAQ schema markup to increase chances of featured snippets."
            )
        
        if not content_insights.get('headings'):
            recommendations.append(
                "Add structured headings (H1, H2, H3) to improve content organization and SEO."
            )
        
        return recommendations


# Export main class
__all__ = ['MetadataGenerator', 'GeneratedMetadata', 'MetaTags', 'OpenGraphTags', 'TwitterCardTags', 'SchemaMarkup', 'MetadataType', 'SchemaType']