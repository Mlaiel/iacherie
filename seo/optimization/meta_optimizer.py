"""
Meta Optimizer - SEO Meta-data Optimization

This module provides comprehensive meta-data optimization for SEO including
title tags, meta descriptions, Open Graph tags, Twitter cards, and schema markup.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class MetaTagType(Enum):
    """Types of meta tags"""
    TITLE = "title"
    DESCRIPTION = "description"
    KEYWORDS = "keywords"
    OPEN_GRAPH = "open_graph"
    TWITTER_CARD = "twitter_card"
    SCHEMA_MARKUP = "schema_markup"
    CANONICAL = "canonical"
    ROBOTS = "robots"


class ContentType(Enum):
    """Content types for meta optimization"""
    ARTICLE = "article"
    PRODUCT = "product"
    VIDEO = "video"
    IMAGE = "image"
    WEBSITE = "website"
    PROFILE = "profile"
    EVENT = "event"
    RECIPE = "recipe"


@dataclass
class MetaTag:
    """Individual meta tag"""
    name: str
    content: str
    tag_type: MetaTagType
    is_valid: bool
    length: int
    recommendations: List[str]


@dataclass
class MetaOptimizationResult:
    """Result of meta optimization"""
    optimized_title: str
    optimized_description: str
    optimized_keywords: List[str]
    open_graph_tags: Dict[str, str]
    twitter_card_tags: Dict[str, str]
    schema_markup: Dict[str, Any]
    canonical_url: str
    robots_directive: str
    meta_tags: List[MetaTag]
    seo_score: float
    recommendations: List[str]


class MetaOptimizer:
    """
    Comprehensive meta-data optimizer for SEO that generates and optimizes
    all necessary meta tags for better search engine visibility.
    """

    def __init__(self, language: str = "en", region: str = "US"):
        """
        Initialize the meta optimizer.
        
        Args:
            language: Target language for meta tags
            region: Target region for localization
        """
        self.language = language
        self.region = region
        self.title_length_limits = {"min": 50, "max": 60}
        self.description_length_limits = {"min": 150, "max": 160}

    def optimize_meta_data(
        self,
        content: str,
        keywords: List[str],
        title: str = "",
        url: str = "",
        content_type: ContentType = ContentType.ARTICLE,
        author: str = "",
        published_date: str = "",
        image_url: str = "",
        additional_data: Optional[Dict[str, Any]] = None
    ) -> MetaOptimizationResult:
        """
        Optimize all meta data for a piece of content.
        
        Args:
            content: Main content to optimize meta data for
            keywords: Target keywords for SEO
            title: Original title (if any)
            url: Content URL
            content_type: Type of content
            author: Content author
            published_date: Publication date (ISO format)
            image_url: Featured image URL
            additional_data: Additional metadata
            
        Returns:
            MetaOptimizationResult with optimized meta data
        """
        try:
            logger.info(f"Starting meta optimization for {content_type.value} content")
            
            # Optimize title tag
            optimized_title = self._optimize_title(title or content[:100], keywords)
            
            # Optimize meta description
            optimized_description = self._optimize_description(content, keywords)
            
            # Optimize meta keywords
            optimized_keywords = self._optimize_keywords(keywords, content)
            
            # Generate Open Graph tags
            open_graph_tags = self._generate_open_graph_tags(
                optimized_title, optimized_description, url, image_url, content_type
            )
            
            # Generate Twitter Card tags
            twitter_card_tags = self._generate_twitter_card_tags(
                optimized_title, optimized_description, image_url, url
            )
            
            # Generate Schema markup
            schema_markup = self._generate_schema_markup(
                optimized_title, optimized_description, content, url, 
                content_type, author, published_date, image_url, additional_data
            )
            
            # Generate canonical URL
            canonical_url = self._generate_canonical_url(url)
            
            # Generate robots directive
            robots_directive = self._generate_robots_directive(content_type, additional_data)
            
            # Create meta tags list
            meta_tags = self._create_meta_tags_list(
                optimized_title, optimized_description, optimized_keywords,
                open_graph_tags, twitter_card_tags, canonical_url, robots_directive
            )
            
            # Calculate SEO score
            seo_score = self._calculate_meta_seo_score(meta_tags, content, keywords)
            
            # Generate recommendations
            recommendations = self._generate_meta_recommendations(meta_tags, seo_score)
            
            return MetaOptimizationResult(
                optimized_title=optimized_title,
                optimized_description=optimized_description,
                optimized_keywords=optimized_keywords,
                open_graph_tags=open_graph_tags,
                twitter_card_tags=twitter_card_tags,
                schema_markup=schema_markup,
                canonical_url=canonical_url,
                robots_directive=robots_directive,
                meta_tags=meta_tags,
                seo_score=seo_score,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error optimizing meta data: {str(e)}")
            raise

    def _optimize_title(self, title: str, keywords: List[str]) -> str:
        """Optimize title tag for SEO"""
        if not title.strip():
            title = f"{keywords[0] if keywords else 'Content'} - Professional Guide"
        
        # Clean title
        title = re.sub(r'\s+', ' ', title.strip())
        
        # Ensure primary keyword is in title
        if keywords and keywords[0].lower() not in title.lower():
            # Add primary keyword to beginning
            title = f"{keywords[0]} - {title}"
        
        # Optimize length
        if len(title) > self.title_length_limits["max"]:
            # Truncate but try to keep complete words
            words = title.split()
            optimized_title = ""
            
            for word in words:
                if len(optimized_title + " " + word) <= self.title_length_limits["max"]:
                    optimized_title += (" " + word) if optimized_title else word
                else:
                    break
            
            title = optimized_title if optimized_title else title[:self.title_length_limits["max"]-3] + "..."
        
        elif len(title) < self.title_length_limits["min"]:
            # Add descriptive text
            descriptors = ["Guide", "Tips", "Tutorial", "Complete Guide", "Best Practices"]
            for descriptor in descriptors:
                extended_title = f"{title} - {descriptor}"
                if len(extended_title) <= self.title_length_limits["max"]:
                    title = extended_title
                    break
        
        return title

    def _optimize_description(self, content: str, keywords: List[str]) -> str:
        """Optimize meta description"""
        # Extract first paragraph or sentences
        sentences = re.split(r'[.!?]', content)
        description = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(description + sentence) < self.description_length_limits["max"] - 20:
                description += (". " + sentence) if description else sentence
            else:
                break
        
        if not description:
            description = content[:100]
        
        # Ensure primary keyword is included
        if keywords and keywords[0].lower() not in description.lower():
            # Try to naturally insert the keyword
            if len(description) + len(keywords[0]) + 10 < self.description_length_limits["max"]:
                description = f"Learn about {keywords[0]}. {description}"
            else:
                # Replace some text with keyword
                words = description.split()
                words[0] = keywords[0]
                description = " ".join(words)
        
        # Ensure proper length
        if len(description) > self.description_length_limits["max"]:
            description = description[:self.description_length_limits["max"]-3] + "..."
        
        # Add call-to-action if space allows
        cta_phrases = ["Learn more", "Discover", "Find out", "Get started"]
        for cta in cta_phrases:
            if len(description) + len(cta) + 2 <= self.description_length_limits["max"]:
                if not description.endswith('.'):
                    description += "."
                description += f" {cta}."
                break
        
        return description

    def _optimize_keywords(self, keywords: List[str], content: str) -> List[str]:
        """Optimize meta keywords (though less important for modern SEO)"""
        # Limit to top 10 keywords
        optimized = keywords[:10]
        
        # Add relevant keywords from content
        content_lower = content.lower()
        word_freq = {}
        
        for word in re.findall(r'\b[a-zA-Z]{4,}\b', content_lower):
            if word not in ['this', 'that', 'with', 'from', 'they', 'have', 'will', 'been', 'were']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Add high-frequency words from content
        for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True):
            if len(optimized) < 10 and word not in [k.lower() for k in optimized] and freq > 2:
                optimized.append(word)
        
        return optimized

    def _generate_open_graph_tags(
        self, 
        title: str, 
        description: str, 
        url: str, 
        image_url: str, 
        content_type: ContentType
    ) -> Dict[str, str]:
        """Generate Open Graph meta tags"""
        og_tags = {
            "og:title": title,
            "og:description": description,
            "og:type": self._get_og_type(content_type),
            "og:locale": self._get_locale_code(),
        }
        
        if url:
            og_tags["og:url"] = url
        
        if image_url:
            og_tags["og:image"] = image_url
            og_tags["og:image:alt"] = f"Featured image for {title}"
            og_tags["og:image:width"] = "1200"
            og_tags["og:image:height"] = "630"
        
        # Add content-specific tags
        if content_type == ContentType.ARTICLE:
            og_tags["article:published_time"] = "2025-01-01T00:00:00Z"  # Would use actual date
            og_tags["article:modified_time"] = "2025-01-01T00:00:00Z"
        
        return og_tags

    def _generate_twitter_card_tags(
        self, 
        title: str, 
        description: str, 
        image_url: str, 
        url: str
    ) -> Dict[str, str]:
        """Generate Twitter Card meta tags"""
        twitter_tags = {
            "twitter:card": "summary_large_image" if image_url else "summary",
            "twitter:title": title,
            "twitter:description": description[:200]  # Twitter description limit
        }
        
        if image_url:
            twitter_tags["twitter:image"] = image_url
            twitter_tags["twitter:image:alt"] = f"Featured image for {title}"
        
        if url:
            twitter_tags["twitter:url"] = url
        
        return twitter_tags

    def _generate_schema_markup(
        self,
        title: str,
        description: str,
        content: str,
        url: str,
        content_type: ContentType,
        author: str,
        published_date: str,
        image_url: str,
        additional_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate JSON-LD Schema markup"""
        
        base_schema = {
            "@context": "https://schema.org",
            "@type": self._get_schema_type(content_type),
            "name": title,
            "description": description,
            "url": url,
            "inLanguage": self.language
        }
        
        if content_type == ContentType.ARTICLE:
            schema = {
                **base_schema,
                "@type": "Article",
                "headline": title,
                "articleBody": content[:500] + "..." if len(content) > 500 else content,
                "wordCount": len(content.split()),
                "datePublished": published_date or "2025-01-01T00:00:00Z",
                "dateModified": published_date or "2025-01-01T00:00:00Z"
            }
            
            if author:
                schema["author"] = {
                    "@type": "Person",
                    "name": author
                }
            
            if image_url:
                schema["image"] = {
                    "@type": "ImageObject",
                    "url": image_url,
                    "width": 1200,
                    "height": 630
                }
        
        elif content_type == ContentType.PRODUCT:
            schema = {
                **base_schema,
                "@type": "Product",
                "name": title,
                "description": description
            }
            
            if additional_data:
                if "price" in additional_data:
                    schema["offers"] = {
                        "@type": "Offer",
                        "price": additional_data["price"],
                        "priceCurrency": additional_data.get("currency", "USD"),
                        "availability": "https://schema.org/InStock"
                    }
                
                if "rating" in additional_data:
                    schema["aggregateRating"] = {
                        "@type": "AggregateRating",
                        "ratingValue": additional_data["rating"],
                        "reviewCount": additional_data.get("review_count", 1)
                    }
        
        elif content_type == ContentType.VIDEO:
            schema = {
                **base_schema,
                "@type": "VideoObject",
                "name": title,
                "description": description,
                "uploadDate": published_date or "2025-01-01T00:00:00Z"
            }
            
            if additional_data:
                if "duration" in additional_data:
                    schema["duration"] = additional_data["duration"]
                
                if "thumbnail_url" in additional_data:
                    schema["thumbnailUrl"] = additional_data["thumbnail_url"]
        
        else:
            schema = base_schema
        
        return schema

    def _generate_canonical_url(self, url: str) -> str:
        """Generate canonical URL"""
        if not url:
            return ""
        
        # Clean URL - remove query parameters and fragments for canonical
        parsed = urlparse(url)
        canonical = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Remove trailing slash unless it's the root
        if canonical.endswith('/') and len(parsed.path) > 1:
            canonical = canonical[:-1]
        
        return canonical

    def _generate_robots_directive(
        self, 
        content_type: ContentType, 
        additional_data: Optional[Dict[str, Any]]
    ) -> str:
        """Generate robots meta directive"""
        
        # Default to index, follow
        directives = ["index", "follow"]
        
        # Check for no-index conditions
        if additional_data:
            if additional_data.get("is_draft", False):
                directives = ["noindex", "nofollow"]
            elif additional_data.get("is_private", False):
                directives = ["noindex", "nofollow"]
            elif additional_data.get("is_archive", False):
                directives = ["noindex", "follow"]
        
        # Add additional directives
        if content_type in [ContentType.IMAGE, ContentType.VIDEO]:
            directives.append("noimageindex")
        
        return ", ".join(directives)

    def _create_meta_tags_list(
        self,
        title: str,
        description: str,
        keywords: List[str],
        og_tags: Dict[str, str],
        twitter_tags: Dict[str, str],
        canonical_url: str,
        robots_directive: str
    ) -> List[MetaTag]:
        """Create list of all meta tags with validation"""
        
        meta_tags = []
        
        # Title tag
        title_recommendations = []
        if len(title) < self.title_length_limits["min"]:
            title_recommendations.append("Title is too short")
        elif len(title) > self.title_length_limits["max"]:
            title_recommendations.append("Title is too long")
        
        meta_tags.append(MetaTag(
            name="title",
            content=title,
            tag_type=MetaTagType.TITLE,
            is_valid=self.title_length_limits["min"] <= len(title) <= self.title_length_limits["max"],
            length=len(title),
            recommendations=title_recommendations
        ))
        
        # Description tag
        desc_recommendations = []
        if len(description) < self.description_length_limits["min"]:
            desc_recommendations.append("Description is too short")
        elif len(description) > self.description_length_limits["max"]:
            desc_recommendations.append("Description is too long")
        
        meta_tags.append(MetaTag(
            name="description",
            content=description,
            tag_type=MetaTagType.DESCRIPTION,
            is_valid=self.description_length_limits["min"] <= len(description) <= self.description_length_limits["max"],
            length=len(description),
            recommendations=desc_recommendations
        ))
        
        # Keywords tag
        keywords_str = ", ".join(keywords)
        meta_tags.append(MetaTag(
            name="keywords",
            content=keywords_str,
            tag_type=MetaTagType.KEYWORDS,
            is_valid=len(keywords) <= 10,
            length=len(keywords_str),
            recommendations=["Too many keywords"] if len(keywords) > 10 else []
        ))
        
        # Open Graph tags
        for name, content in og_tags.items():
            meta_tags.append(MetaTag(
                name=name,
                content=content,
                tag_type=MetaTagType.OPEN_GRAPH,
                is_valid=bool(content),
                length=len(content),
                recommendations=[]
            ))
        
        # Twitter Card tags
        for name, content in twitter_tags.items():
            meta_tags.append(MetaTag(
                name=name,
                content=content,
                tag_type=MetaTagType.TWITTER_CARD,
                is_valid=bool(content),
                length=len(content),
                recommendations=[]
            ))
        
        # Canonical URL
        if canonical_url:
            meta_tags.append(MetaTag(
                name="canonical",
                content=canonical_url,
                tag_type=MetaTagType.CANONICAL,
                is_valid=bool(canonical_url),
                length=len(canonical_url),
                recommendations=[]
            ))
        
        # Robots directive
        meta_tags.append(MetaTag(
            name="robots",
            content=robots_directive,
            tag_type=MetaTagType.ROBOTS,
            is_valid=bool(robots_directive),
            length=len(robots_directive),
            recommendations=[]
        ))
        
        return meta_tags

    def _calculate_meta_seo_score(
        self, 
        meta_tags: List[MetaTag], 
        content: str, 
        keywords: List[str]
    ) -> float:
        """Calculate SEO score based on meta tags quality"""
        
        score = 0.0
        max_score = 100.0
        
        # Title optimization (20 points)
        title_tag = next((tag for tag in meta_tags if tag.tag_type == MetaTagType.TITLE), None)
        if title_tag and title_tag.is_valid:
            score += 15
            # Bonus for keyword in title
            if keywords and keywords[0].lower() in title_tag.content.lower():
                score += 5
        
        # Description optimization (20 points)
        desc_tag = next((tag for tag in meta_tags if tag.tag_type == MetaTagType.DESCRIPTION), None)
        if desc_tag and desc_tag.is_valid:
            score += 15
            # Bonus for keyword in description
            if keywords and keywords[0].lower() in desc_tag.content.lower():
                score += 5
        
        # Open Graph tags (15 points)
        og_tags = [tag for tag in meta_tags if tag.tag_type == MetaTagType.OPEN_GRAPH]
        if len(og_tags) >= 4:  # At least 4 OG tags
            score += 15
        
        # Twitter Card tags (10 points)
        twitter_tags = [tag for tag in meta_tags if tag.tag_type == MetaTagType.TWITTER_CARD]
        if len(twitter_tags) >= 3:  # At least 3 Twitter tags
            score += 10
        
        # Canonical URL (10 points)
        canonical_tag = next((tag for tag in meta_tags if tag.tag_type == MetaTagType.CANONICAL), None)
        if canonical_tag and canonical_tag.is_valid:
            score += 10
        
        # Schema markup (15 points) - assume present if content type is appropriate
        score += 15  # Full points for having schema markup
        
        # Keywords relevance (10 points)
        if keywords:
            content_lower = content.lower()
            keyword_presence = sum(1 for kw in keywords[:3] if kw.lower() in content_lower)
            score += (keyword_presence / min(3, len(keywords))) * 10
        
        return min(max_score, score)

    def _generate_meta_recommendations(self, meta_tags: List[MetaTag], seo_score: float) -> List[str]:
        """Generate recommendations for meta tag improvements"""
        
        recommendations = []
        
        # Collect recommendations from individual tags
        for tag in meta_tags:
            recommendations.extend(tag.recommendations)
        
        # General SEO recommendations
        if seo_score < 70:
            recommendations.append("Overall meta SEO score is low. Review title and description optimization.")
        
        # Check for missing important tags
        tag_types = {tag.tag_type for tag in meta_tags}
        
        if MetaTagType.OPEN_GRAPH not in tag_types:
            recommendations.append("Add Open Graph tags for better social media sharing.")
        
        if MetaTagType.TWITTER_CARD not in tag_types:
            recommendations.append("Add Twitter Card tags for better Twitter sharing.")
        
        if MetaTagType.CANONICAL not in tag_types:
            recommendations.append("Add canonical URL to prevent duplicate content issues.")
        
        # Check for keyword optimization
        title_tag = next((tag for tag in meta_tags if tag.tag_type == MetaTagType.TITLE), None)
        if title_tag and "keyword" not in title_tag.content.lower():
            recommendations.append("Include primary keyword in title tag.")
        
        return list(set(recommendations))  # Remove duplicates

    def _get_og_type(self, content_type: ContentType) -> str:
        """Get Open Graph type for content type"""
        mapping = {
            ContentType.ARTICLE: "article",
            ContentType.PRODUCT: "product",
            ContentType.VIDEO: "video.other",
            ContentType.IMAGE: "image",
            ContentType.WEBSITE: "website",
            ContentType.PROFILE: "profile",
            ContentType.EVENT: "event",
            ContentType.RECIPE: "recipe"
        }
        return mapping.get(content_type, "website")

    def _get_schema_type(self, content_type: ContentType) -> str:
        """Get Schema.org type for content type"""
        mapping = {
            ContentType.ARTICLE: "Article",
            ContentType.PRODUCT: "Product",
            ContentType.VIDEO: "VideoObject",
            ContentType.IMAGE: "ImageObject",
            ContentType.WEBSITE: "WebSite",
            ContentType.PROFILE: "Person",
            ContentType.EVENT: "Event",
            ContentType.RECIPE: "Recipe"
        }
        return mapping.get(content_type, "Thing")

    def _get_locale_code(self) -> str:
        """Get locale code for Open Graph"""
        locale_map = {
            "en": "en_US",
            "fr": "fr_FR",
            "de": "de_DE",
            "es": "es_ES",
            "it": "it_IT",
            "pt": "pt_BR",
            "ja": "ja_JP",
            "ko": "ko_KR",
            "zh": "zh_CN"
        }
        return locale_map.get(self.language, "en_US")

    def generate_html_meta_tags(self, result: MetaOptimizationResult) -> str:
        """Generate HTML meta tags from optimization result"""
        
        html_tags = []
        
        # Title
        html_tags.append(f'<title>{result.optimized_title}</title>')
        
        # Basic meta tags
        html_tags.append(f'<meta name="description" content="{result.optimized_description}">')
        if result.optimized_keywords:
            html_tags.append(f'<meta name="keywords" content="{", ".join(result.optimized_keywords)}">')
        
        # Robots
        html_tags.append(f'<meta name="robots" content="{result.robots_directive}">')
        
        # Canonical
        if result.canonical_url:
            html_tags.append(f'<link rel="canonical" href="{result.canonical_url}">')
        
        # Open Graph tags
        for name, content in result.open_graph_tags.items():
            html_tags.append(f'<meta property="{name}" content="{content}">')
        
        # Twitter Card tags
        for name, content in result.twitter_card_tags.items():
            html_tags.append(f'<meta name="{name}" content="{content}">')
        
        # Schema markup
        schema_json = json.dumps(result.schema_markup, indent=2)
        html_tags.append(f'<script type="application/ld+json">\n{schema_json}\n</script>')
        
        return '\n'.join(html_tags)

    def validate_meta_tags(self, html_content: str) -> Dict[str, Any]:
        """Validate existing meta tags in HTML content"""
        
        validation_result = {
            "has_title": bool(re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE)),
            "has_description": bool(re.search(r'<meta[^>]*name=["\']description["\'][^>]*>', html_content, re.IGNORECASE)),
            "has_og_tags": bool(re.search(r'<meta[^>]*property=["\']og:', html_content, re.IGNORECASE)),
            "has_twitter_tags": bool(re.search(r'<meta[^>]*name=["\']twitter:', html_content, re.IGNORECASE)),
            "has_canonical": bool(re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*>', html_content, re.IGNORECASE)),
            "has_schema": bool(re.search(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>', html_content, re.IGNORECASE)),
            "issues": []
        }
        
        # Extract title and check length
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE)
        if title_match:
            title_length = len(title_match.group(1))
            if title_length < self.title_length_limits["min"]:
                validation_result["issues"].append("Title too short")
            elif title_length > self.title_length_limits["max"]:
                validation_result["issues"].append("Title too long")
        
        # Extract description and check length
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
        if desc_match:
            desc_length = len(desc_match.group(1))
            if desc_length < self.description_length_limits["min"]:
                validation_result["issues"].append("Description too short")
            elif desc_length > self.description_length_limits["max"]:
                validation_result["issues"].append("Description too long")
        
        return validation_result


# Export for module usage
__all__ = [
    "MetaOptimizer",
    "MetaTagType",
    "ContentType", 
    "MetaTag",
    "MetaOptimizationResult"
]