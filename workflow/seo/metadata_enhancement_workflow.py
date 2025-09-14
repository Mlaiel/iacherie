"""Metadata Enhancement Workflow - Advanced metadata optimization for maximum SEO impact.

This module provides comprehensive metadata enhancement capabilities including dynamic title generation,
meta description optimization, schema markup implementation, and platform-specific metadata adaptation
for improved search visibility and click-through rates.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

import asyncio
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import quote


class MetadataType(Enum):
    """Types of metadata elements."""
    TITLE = "title"
    META_DESCRIPTION = "meta_description"
    OPEN_GRAPH = "open_graph"
    TWITTER_CARD = "twitter_card"
    SCHEMA_MARKUP = "schema_markup"
    CANONICAL_URL = "canonical_url"
    ROBOTS = "robots"
    HREFLANG = "hreflang"


class SchemaType(Enum):
    """Schema.org markup types."""
    ARTICLE = "Article"
    BLOG_POSTING = "BlogPosting"
    HOW_TO = "HowTo"
    PRODUCT = "Product"
    REVIEW = "Review"
    VIDEO_OBJECT = "VideoObject"
    MUSIC_RECORDING = "MusicRecording"
    ORGANIZATION = "Organization"
    PERSON = "Person"
    WEBSITE = "WebSite"


@dataclass
class MetadataFields:
    """Core metadata fields and specifications."""
    title: str = ""
    meta_description: str = ""
    keywords: List[str] = field(default_factory=list)
    canonical_url: str = ""
    robots: str = "index, follow"
    language: str = "en"
    region: str = "global"
    author: str = ""
    published_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None


@dataclass
class OpenGraphData:
    """Open Graph metadata for social media sharing."""
    title: str = ""
    description: str = ""
    image: str = ""
    url: str = ""
    type: str = "website"
    site_name: str = ""
    locale: str = "en_US"
    article_author: str = ""
    article_published_time: Optional[datetime] = None
    article_modified_time: Optional[datetime] = None


@dataclass
class TwitterCardData:
    """Twitter Card metadata for Twitter sharing."""
    card_type: str = "summary_large_image"
    title: str = ""
    description: str = ""
    image: str = ""
    site: str = ""
    creator: str = ""


@dataclass
class StructuredData:
    """Schema.org structured data markup."""
    schema_type: SchemaType
    properties: Dict[str, Any] = field(default_factory=dict)
    context: str = "https://schema.org"
    
    def to_json_ld(self) -> str:
        """Convert to JSON-LD format."""
        schema_dict = {
            "@context": self.context,
            "@type": self.schema_type.value,
            **self.properties
        }
        return json.dumps(schema_dict, indent=2, default=str)


@dataclass
class MetadataOptimizationResult:
    """Results from metadata optimization process."""
    optimized_metadata: MetadataFields
    open_graph: OpenGraphData
    twitter_card: TwitterCardData
    structured_data: List[StructuredData]
    platform_specific: Dict[str, Dict[str, Any]]
    optimization_score: float
    improvements: List[str]
    warnings: List[str]
    validation_results: Dict[str, bool]


class MetadataEnhancementWorkflow:
    """Advanced metadata enhancement workflow for comprehensive SEO optimization."""
    
    def __init__(self) -> None:
        """Initialize the metadata enhancement workflow."""
        self.title_generators = {
            "article": self._generate_article_titles,
            "tutorial": self._generate_tutorial_titles,
            "review": self._generate_review_titles,
            "listicle": self._generate_listicle_titles,
            "video": self._generate_video_titles,
            "music": self._generate_music_titles
        }
        
        self.schema_generators = {
            SchemaType.ARTICLE: self._generate_article_schema,
            SchemaType.BLOG_POSTING: self._generate_blog_schema,
            SchemaType.HOW_TO: self._generate_howto_schema,
            SchemaType.PRODUCT: self._generate_product_schema,
            SchemaType.REVIEW: self._generate_review_schema,
            SchemaType.VIDEO_OBJECT: self._generate_video_schema,
            SchemaType.MUSIC_RECORDING: self._generate_music_schema
        }
    
    async def execute(self, content_data: Dict[str, Any], config: Any) -> Dict[str, Any]:
        """Execute comprehensive metadata enhancement workflow.
        
        Args:
            content_data: Content information for metadata generation
            config: Workflow configuration
            
        Returns:
            Comprehensive metadata optimization results
        """
        try:
            # Extract content parameters
            content_text = content_data.get("content", "")
            title = content_data.get("title", "")
            description = content_data.get("description", "")
            target_keywords = content_data.get("target_keywords", [])
            content_type = content_data.get("content_type", "article")
            target_platforms = content_data.get("target_platforms", ["google"])
            language = getattr(config, "language", "en")
            region = getattr(config, "region", "global")
            
            # Step 1: Generate optimized title variations
            title_variations = await self._generate_optimized_titles(
                content_text, title, target_keywords, content_type
            )
            
            # Step 2: Create optimized meta description
            meta_description = await self._generate_meta_description(
                content_text, description, target_keywords
            )
            
            # Step 3: Build core metadata fields
            metadata_fields = await self._build_metadata_fields(
                title_variations[0] if title_variations else title,
                meta_description,
                target_keywords,
                content_data,
                language,
                region
            )
            
            # Step 4: Generate Open Graph data
            open_graph = await self._generate_open_graph_data(
                metadata_fields, content_data
            )
            
            # Step 5: Generate Twitter Card data
            twitter_card = await self._generate_twitter_card_data(
                metadata_fields, content_data
            )
            
            # Step 6: Create structured data markup
            structured_data = await self._generate_structured_data(
                content_data, metadata_fields, content_type
            )
            
            # Step 7: Platform-specific optimizations
            platform_specific = await self._generate_platform_specific_metadata(
                metadata_fields, target_platforms, content_type
            )
            
            # Step 8: Validate and score metadata
            validation_results = await self._validate_metadata(
                metadata_fields, open_graph, twitter_card, structured_data
            )
            
            optimization_score = self._calculate_optimization_score(
                metadata_fields, validation_results, structured_data
            )
            
            # Step 9: Generate improvements and warnings
            improvements, warnings = await self._analyze_metadata_quality(
                metadata_fields, open_graph, twitter_card, structured_data
            )
            
            # Create optimization result
            optimization_result = MetadataOptimizationResult(
                optimized_metadata=metadata_fields,
                open_graph=open_graph,
                twitter_card=twitter_card,
                structured_data=structured_data,
                platform_specific=platform_specific,
                optimization_score=optimization_score,
                improvements=improvements,
                warnings=warnings,
                validation_results=validation_results
            )
            
            return {
                "status": "completed",
                "score": optimization_score,
                "optimization_result": optimization_result,
                "title_variations": title_variations,
                "recommendations": improvements,
                "html_output": self._generate_html_output(optimization_result),
                "metrics": {
                    "title_length": len(metadata_fields.title),
                    "meta_description_length": len(metadata_fields.meta_description),
                    "schema_types": len(structured_data),
                    "validation_score": sum(validation_results.values()) / len(validation_results) * 100,
                    "platform_adaptations": len(platform_specific)
                }
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "score": 0.0,
                "recommendations": [],
                "metrics": {}
            }
    
    async def _generate_optimized_titles(
        self,
        content: str,
        current_title: str,
        keywords: List[str],
        content_type: str
    ) -> List[str]:
        """Generate optimized title variations."""
        titles = []
        
        primary_keyword = keywords[0] if keywords else ""
        
        # Use content-type specific generators
        if content_type in self.title_generators:
            generated_titles = await self.title_generators[content_type](
                content, current_title, primary_keyword
            )
            titles.extend(generated_titles)
        
        # Generic title patterns
        if primary_keyword:
            generic_titles = [
                f"{primary_keyword}: The Complete Guide",
                f"How to Master {primary_keyword} in 2025",
                f"The Ultimate {primary_keyword} Strategy",
                f"{primary_keyword} - Everything You Need to Know",
                f"Best {primary_keyword} Tips and Tricks"
            ]
            titles.extend(generic_titles)
        
        # Optimize current title if provided
        if current_title:
            optimized_current = self._optimize_existing_title(current_title, primary_keyword)
            titles.insert(0, optimized_current)
        
        # Filter and validate titles
        valid_titles = []
        for title in titles[:10]:  # Limit to top 10
            if self._is_valid_title(title):
                valid_titles.append(title)
        
        return valid_titles[:5]  # Return top 5 variations
    
    async def _generate_meta_description(
        self,
        content: str,
        current_description: str,
        keywords: List[str]
    ) -> str:
        """Generate optimized meta description."""
        primary_keyword = keywords[0] if keywords else ""
        
        # Extract key sentences from content
        sentences = self._extract_key_sentences(content)
        
        # Build description components
        description_parts = []
        
        # Add keyword-focused intro
        if primary_keyword:
            description_parts.append(f"Discover {primary_keyword}")
        
        # Add compelling content summary
        if sentences:
            summary = sentences[0][:80] + "..." if len(sentences[0]) > 80 else sentences[0]
            description_parts.append(summary)
        
        # Add call to action
        cta_options = [
            "Learn more now.",
            "Get expert insights.",
            "Start your journey today.",
            "Unlock the secrets.",
            "Master the fundamentals."
        ]
        description_parts.append(cta_options[0])
        
        # Combine and optimize
        description = " ".join(description_parts)
        
        # Ensure optimal length (150-160 characters)
        if len(description) > 160:
            description = description[:157] + "..."
        elif len(description) < 120 and current_description:
            # Use current description if generated is too short
            description = current_description[:160]
        
        return description
    
    async def _build_metadata_fields(
        self,
        title: str,
        meta_description: str,
        keywords: List[str],
        content_data: Dict[str, Any],
        language: str,
        region: str
    ) -> MetadataFields:
        """Build comprehensive metadata fields."""
        return MetadataFields(
            title=title,
            meta_description=meta_description,
            keywords=keywords,
            canonical_url=content_data.get("url", ""),
            robots="index, follow",
            language=language,
            region=region,
            author=content_data.get("author", ""),
            published_date=content_data.get("published_date"),
            modified_date=datetime.now()
        )
    
    async def _generate_open_graph_data(
        self,
        metadata: MetadataFields,
        content_data: Dict[str, Any]
    ) -> OpenGraphData:
        """Generate Open Graph metadata for social media sharing."""
        return OpenGraphData(
            title=metadata.title,
            description=metadata.meta_description,
            image=content_data.get("featured_image", ""),
            url=metadata.canonical_url,
            type=self._determine_og_type(content_data.get("content_type", "article")),
            site_name=content_data.get("site_name", "Ainflue Platform"),
            locale=f"{metadata.language}_{metadata.region}".replace("global", "US"),
            article_author=metadata.author,
            article_published_time=metadata.published_date,
            article_modified_time=metadata.modified_date
        )
    
    async def _generate_twitter_card_data(
        self,
        metadata: MetadataFields,
        content_data: Dict[str, Any]
    ) -> TwitterCardData:
        """Generate Twitter Card metadata."""
        return TwitterCardData(
            card_type="summary_large_image",
            title=metadata.title,
            description=metadata.meta_description,
            image=content_data.get("featured_image", ""),
            site=content_data.get("twitter_site", "@ainflue"),
            creator=content_data.get("twitter_creator", "")
        )
    
    async def _generate_structured_data(
        self,
        content_data: Dict[str, Any],
        metadata: MetadataFields,
        content_type: str
    ) -> List[StructuredData]:
        """Generate schema.org structured data markup."""
        structured_data = []
        
        # Determine primary schema type
        schema_type = self._determine_schema_type(content_type)
        
        # Generate primary schema
        if schema_type in self.schema_generators:
            primary_schema = await self.schema_generators[schema_type](
                content_data, metadata
            )
            structured_data.append(primary_schema)
        
        # Add organization schema
        organization_schema = await self._generate_organization_schema(content_data)
        structured_data.append(organization_schema)
        
        # Add website schema
        website_schema = await self._generate_website_schema(content_data)
        structured_data.append(website_schema)
        
        return structured_data
    
    async def _generate_platform_specific_metadata(
        self,
        metadata: MetadataFields,
        platforms: List[str],
        content_type: str
    ) -> Dict[str, Dict[str, Any]]:
        """Generate platform-specific metadata optimizations."""
        platform_metadata = {}
        
        for platform in platforms:
            if platform == "youtube":
                platform_metadata[platform] = {
                    "title_format": "Keyword | How-to | Benefit",
                    "description_length": "125 characters optimal",
                    "tags": metadata.keywords[:15],  # YouTube tag limit
                    "category": self._determine_youtube_category(content_type),
                    "thumbnail_text": metadata.keywords[0] if metadata.keywords else ""
                }
            
            elif platform == "instagram":
                platform_metadata[platform] = {
                    "caption_length": "125 characters optimal",
                    "hashtags": [f"#{kw.replace(' ', '')}" for kw in metadata.keywords[:30]],
                    "alt_text": metadata.meta_description[:100],
                    "location_tag": "Enable if relevant",
                    "story_format": "15-second attention grabber"
                }
            
            elif platform == "tiktok":
                platform_metadata[platform] = {
                    "title_hook": "First 3 seconds critical",
                    "hashtags": [f"#{kw.replace(' ', '')}" for kw in metadata.keywords[:5]],
                    "trending_sounds": "Use trending audio",
                    "caption_length": "100 characters max",
                    "challenge_tags": "Participate in trending challenges"
                }
            
            elif platform == "linkedin":
                platform_metadata[platform] = {
                    "headline": metadata.title,
                    "summary": metadata.meta_description,
                    "professional_tone": "Maintain business focus",
                    "hashtags": [f"#{kw.replace(' ', '')}" for kw in metadata.keywords[:5]],
                    "call_to_action": "Professional engagement focused"
                }
            
            elif platform == "facebook":
                platform_metadata[platform] = {
                    "title": metadata.title,
                    "description": metadata.meta_description,
                    "image_ratio": "1.91:1 recommended",
                    "video_length": "15-60 seconds optimal",
                    "engagement_focus": "Comments and shares priority"
                }
        
        return platform_metadata
    
    async def _validate_metadata(
        self,
        metadata: MetadataFields,
        open_graph: OpenGraphData,
        twitter_card: TwitterCardData,
        structured_data: List[StructuredData]
    ) -> Dict[str, bool]:
        """Validate metadata for SEO compliance."""
        validation_results = {}
        
        # Title validation
        validation_results["title_length_valid"] = 30 <= len(metadata.title) <= 60
        validation_results["title_has_keyword"] = len(metadata.keywords) > 0 and any(
            kw.lower() in metadata.title.lower() for kw in metadata.keywords
        )
        
        # Meta description validation
        validation_results["meta_desc_length_valid"] = 120 <= len(metadata.meta_description) <= 160
        validation_results["meta_desc_has_keyword"] = len(metadata.keywords) > 0 and any(
            kw.lower() in metadata.meta_description.lower() for kw in metadata.keywords
        )
        
        # Open Graph validation
        validation_results["og_title_present"] = bool(open_graph.title)
        validation_results["og_description_present"] = bool(open_graph.description)
        validation_results["og_image_present"] = bool(open_graph.image)
        
        # Twitter Card validation
        validation_results["twitter_card_type_valid"] = twitter_card.card_type in [
            "summary", "summary_large_image", "app", "player"
        ]
        validation_results["twitter_title_present"] = bool(twitter_card.title)
        
        # Structured data validation
        validation_results["schema_present"] = len(structured_data) > 0
        validation_results["schema_valid_json"] = all(
            self._validate_json_ld(schema.to_json_ld()) for schema in structured_data
        )
        
        # Canonical URL validation
        validation_results["canonical_url_valid"] = self._is_valid_url(metadata.canonical_url)
        
        return validation_results
    
    def _calculate_optimization_score(
        self,
        metadata: MetadataFields,
        validation_results: Dict[str, bool],
        structured_data: List[StructuredData]
    ) -> float:
        """Calculate overall metadata optimization score."""
        score = 0
        max_score = 100
        
        # Validation score (50 points)
        validation_score = sum(validation_results.values()) / len(validation_results) * 50
        score += validation_score
        
        # Title optimization (20 points)
        if 30 <= len(metadata.title) <= 60:
            score += 15
        if metadata.keywords and any(kw.lower() in metadata.title.lower() for kw in metadata.keywords):
            score += 5
        
        # Meta description optimization (20 points)
        if 120 <= len(metadata.meta_description) <= 160:
            score += 15
        if metadata.keywords and any(kw.lower() in metadata.meta_description.lower() for kw in metadata.keywords):
            score += 5
        
        # Structured data bonus (10 points)
        if len(structured_data) >= 2:
            score += 10
        elif len(structured_data) >= 1:
            score += 5
        
        return min(score, max_score)
    
    async def _analyze_metadata_quality(
        self,
        metadata: MetadataFields,
        open_graph: OpenGraphData,
        twitter_card: TwitterCardData,
        structured_data: List[StructuredData]
    ) -> Tuple[List[str], List[str]]:
        """Analyze metadata quality and generate improvements and warnings."""
        improvements = []
        warnings = []
        
        # Title analysis
        if len(metadata.title) < 30:
            improvements.append("Increase title length to 30-60 characters for better SEO")
        elif len(metadata.title) > 60:
            warnings.append("Title exceeds 60 characters and may be truncated in search results")
        
        # Meta description analysis
        if len(metadata.meta_description) < 120:
            improvements.append("Expand meta description to 120-160 characters for better SERP real estate")
        elif len(metadata.meta_description) > 160:
            warnings.append("Meta description exceeds 160 characters and may be truncated")
        
        # Keyword analysis
        if not metadata.keywords:
            improvements.append("Add target keywords to improve SEO relevance")
        elif len(metadata.keywords) > 10:
            warnings.append("Too many keywords may dilute SEO focus")
        
        # Open Graph analysis
        if not open_graph.image:
            improvements.append("Add Open Graph image for better social media sharing")
        
        # Twitter Card analysis
        if not twitter_card.creator:
            improvements.append("Add Twitter creator handle for better attribution")
        
        # Structured data analysis
        if len(structured_data) < 2:
            improvements.append("Add more structured data types for enhanced rich snippets")
        
        # URL analysis
        if not metadata.canonical_url:
            improvements.append("Add canonical URL to prevent duplicate content issues")
        
        return improvements, warnings
    
    def _generate_html_output(self, result: MetadataOptimizationResult) -> str:
        """Generate HTML output for metadata implementation."""
        html_parts = []
        
        # Basic meta tags
        html_parts.append(f'<title>{result.optimized_metadata.title}</title>')
        html_parts.append(f'<meta name="description" content="{result.optimized_metadata.meta_description}">')
        
        if result.optimized_metadata.keywords:
            keywords_str = ", ".join(result.optimized_metadata.keywords)
            html_parts.append(f'<meta name="keywords" content="{keywords_str}">')
        
        html_parts.append(f'<meta name="robots" content="{result.optimized_metadata.robots}">')
        html_parts.append(f'<meta name="language" content="{result.optimized_metadata.language}">')
        
        if result.optimized_metadata.canonical_url:
            html_parts.append(f'<link rel="canonical" href="{result.optimized_metadata.canonical_url}">')
        
        # Open Graph tags
        og = result.open_graph
        html_parts.extend([
            f'<meta property="og:title" content="{og.title}">',
            f'<meta property="og:description" content="{og.description}">',
            f'<meta property="og:type" content="{og.type}">',
            f'<meta property="og:url" content="{og.url}">',
            f'<meta property="og:site_name" content="{og.site_name}">',
            f'<meta property="og:locale" content="{og.locale}">'
        ])
        
        if og.image:
            html_parts.append(f'<meta property="og:image" content="{og.image}">')
        
        # Twitter Card tags
        tc = result.twitter_card
        html_parts.extend([
            f'<meta name="twitter:card" content="{tc.card_type}">',
            f'<meta name="twitter:title" content="{tc.title}">',
            f'<meta name="twitter:description" content="{tc.description}">'
        ])
        
        if tc.site:
            html_parts.append(f'<meta name="twitter:site" content="{tc.site}">')
        if tc.creator:
            html_parts.append(f'<meta name="twitter:creator" content="{tc.creator}">')
        if tc.image:
            html_parts.append(f'<meta name="twitter:image" content="{tc.image}">')
        
        # Structured data
        for schema in result.structured_data:
            html_parts.append(f'<script type="application/ld+json">{schema.to_json_ld()}</script>')
        
        return '\n'.join(html_parts)
    
    # Content-type specific title generators
    
    async def _generate_article_titles(self, content: str, current_title: str, keyword: str) -> List[str]:
        """Generate article-specific title variations."""
        titles = []
        if keyword:
            titles.extend([
                f"The Complete Guide to {keyword}",
                f"Understanding {keyword}: A Comprehensive Analysis",
                f"{keyword} Explained: Key Insights and Strategies",
                f"Everything You Need to Know About {keyword}",
                f"The Definitive {keyword} Resource"
            ])
        return titles
    
    async def _generate_tutorial_titles(self, content: str, current_title: str, keyword: str) -> List[str]:
        """Generate tutorial-specific title variations."""
        titles = []
        if keyword:
            titles.extend([
                f"How to Master {keyword}: Step-by-Step Guide",
                f"{keyword} Tutorial: From Beginner to Expert",
                f"Learn {keyword} in 10 Easy Steps",
                f"The Ultimate {keyword} Tutorial for 2025",
                f"Complete {keyword} Guide for Beginners"
            ])
        return titles
    
    async def _generate_review_titles(self, content: str, current_title: str, keyword: str) -> List[str]:
        """Generate review-specific title variations."""
        titles = []
        if keyword:
            titles.extend([
                f"{keyword} Review: Is It Worth It?",
                f"Honest {keyword} Review: Pros and Cons",
                f"{keyword} Analysis: Complete Breakdown",
                f"My Experience with {keyword}: Detailed Review",
                f"{keyword} vs Alternatives: Which Is Better?"
            ])
        return titles
    
    async def _generate_listicle_titles(self, content: str, current_title: str, keyword: str) -> List[str]:
        """Generate listicle-specific title variations."""
        titles = []
        if keyword:
            titles.extend([
                f"10 Best {keyword} Tips That Actually Work",
                f"7 Essential {keyword} Strategies for Success",
                f"15 {keyword} Hacks Every Expert Uses",
                f"Top 5 {keyword} Mistakes to Avoid",
                f"12 Proven {keyword} Techniques for 2025"
            ])
        return titles
    
    async def _generate_video_titles(self, content: str, current_title: str, keyword: str) -> List[str]:
        """Generate video-specific title variations."""
        titles = []
        if keyword:
            titles.extend([
                f"{keyword} - The Complete Video Guide",
                f"Watch: {keyword} Explained in 10 Minutes",
                f"{keyword} Tutorial: Video Walkthrough",
                f"LIVE: {keyword} Demonstration",
                f"{keyword} Behind the Scenes Video"
            ])
        return titles
    
    async def _generate_music_titles(self, content: str, current_title: str, keyword: str) -> List[str]:
        """Generate music-specific title variations."""
        titles = []
        if keyword:
            titles.extend([
                f"{keyword} - Original Track",
                f"{keyword} (Official Audio)",
                f"{keyword} - Instrumental Version",
                f"{keyword} Cover Song",
                f"{keyword} Remix - New Version"
            ])
        return titles
    
    # Schema generators
    
    async def _generate_article_schema(self, content_data: Dict[str, Any], metadata: MetadataFields) -> StructuredData:
        """Generate Article schema markup."""
        properties = {
            "headline": metadata.title,
            "description": metadata.meta_description,
            "author": {
                "@type": "Person",
                "name": metadata.author or "Ainflue Creator"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Ainflue Platform"
            },
            "datePublished": metadata.published_date.isoformat() if metadata.published_date else datetime.now().isoformat(),
            "dateModified": metadata.modified_date.isoformat() if metadata.modified_date else datetime.now().isoformat(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": metadata.canonical_url
            }
        }
        
        if content_data.get("featured_image"):
            properties["image"] = content_data["featured_image"]
        
        return StructuredData(SchemaType.ARTICLE, properties)
    
    async def _generate_blog_schema(self, content_data: Dict[str, Any], metadata: MetadataFields) -> StructuredData:
        """Generate BlogPosting schema markup."""
        properties = {
            "headline": metadata.title,
            "description": metadata.meta_description,
            "author": {
                "@type": "Person",
                "name": metadata.author or "Ainflue Creator"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Ainflue Platform"
            },
            "datePublished": metadata.published_date.isoformat() if metadata.published_date else datetime.now().isoformat(),
            "dateModified": metadata.modified_date.isoformat() if metadata.modified_date else datetime.now().isoformat(),
            "mainEntityOfPage": metadata.canonical_url,
            "blogPost": True
        }
        
        return StructuredData(SchemaType.BLOG_POSTING, properties)
    
    async def _generate_howto_schema(self, content_data: Dict[str, Any], metadata: MetadataFields) -> StructuredData:
        """Generate HowTo schema markup."""
        properties = {
            "name": metadata.title,
            "description": metadata.meta_description,
            "totalTime": "PT30M",  # Default 30 minutes
            "estimatedCost": {
                "@type": "MonetaryAmount",
                "currency": "USD",
                "value": "0"
            },
            "supply": [],
            "tool": [],
            "step": [
                {
                    "@type": "HowToStep",
                    "text": "Follow the comprehensive guide provided in the content"
                }
            ]
        }
        
        return StructuredData(SchemaType.HOW_TO, properties)
    
    async def _generate_product_schema(self, content_data: Dict[str, Any], metadata: MetadataFields) -> StructuredData:
        """Generate Product schema markup."""
        properties = {
            "name": metadata.title,
            "description": metadata.meta_description,
            "brand": {
                "@type": "Brand",
                "name": "Ainflue Platform"
            },
            "offers": {
                "@type": "Offer",
                "availability": "https://schema.org/InStock",
                "price": "0",
                "priceCurrency": "USD"
            }
        }
        
        return StructuredData(SchemaType.PRODUCT, properties)
    
    async def _generate_review_schema(self, content_data: Dict[str, Any], metadata: MetadataFields) -> StructuredData:
        """Generate Review schema markup."""
        properties = {
            "itemReviewed": {
                "@type": "Thing",
                "name": metadata.title
            },
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": "4.5",
                "bestRating": "5"
            },
            "author": {
                "@type": "Person",
                "name": metadata.author or "Ainflue Creator"
            },
            "reviewBody": metadata.meta_description
        }
        
        return StructuredData(SchemaType.REVIEW, properties)
    
    async def _generate_video_schema(self, content_data: Dict[str, Any], metadata: MetadataFields) -> StructuredData:
        """Generate VideoObject schema markup."""
        properties = {
            "name": metadata.title,
            "description": metadata.meta_description,
            "uploadDate": metadata.published_date.isoformat() if metadata.published_date else datetime.now().isoformat(),
            "duration": "PT10M",  # Default 10 minutes
            "thumbnailUrl": content_data.get("featured_image", ""),
            "contentUrl": metadata.canonical_url
        }
        
        return StructuredData(SchemaType.VIDEO_OBJECT, properties)
    
    async def _generate_music_schema(self, content_data: Dict[str, Any], metadata: MetadataFields) -> StructuredData:
        """Generate MusicRecording schema markup."""
        properties = {
            "name": metadata.title,
            "description": metadata.meta_description,
            "byArtist": {
                "@type": "MusicGroup",
                "name": metadata.author or "Ainflue Artist"
            },
            "duration": "PT3M30S",  # Default 3:30 minutes
            "recordingOf": {
                "@type": "MusicComposition",
                "name": metadata.title
            }
        }
        
        return StructuredData(SchemaType.MUSIC_RECORDING, properties)
    
    async def _generate_organization_schema(self, content_data: Dict[str, Any]) -> StructuredData:
        """Generate Organization schema markup."""
        properties = {
            "name": "Ainflue Platform",
            "url": "https://ainflue.com",
            "logo": "https://ainflue.com/logo.png",
            "sameAs": [
                "https://twitter.com/ainflue",
                "https://instagram.com/ainflue",
                "https://linkedin.com/company/ainflue"
            ]
        }
        
        return StructuredData(SchemaType.ORGANIZATION, properties)
    
    async def _generate_website_schema(self, content_data: Dict[str, Any]) -> StructuredData:
        """Generate WebSite schema markup."""
        properties = {
            "name": "Ainflue Platform",
            "url": "https://ainflue.com",
            "potentialAction": {
                "@type": "SearchAction",
                "target": "https://ainflue.com/search?q={search_term_string}",
                "query-input": "required name=search_term_string"
            }
        }
        
        return StructuredData(SchemaType.WEBSITE, properties)
    
    # Helper methods
    
    def _optimize_existing_title(self, title: str, keyword: str) -> str:
        """Optimize an existing title with keyword placement."""
        if not keyword or keyword.lower() in title.lower():
            return title
        
        # Try to naturally integrate keyword
        if len(title) + len(keyword) + 3 <= 60:  # Account for " - " separator
            return f"{keyword} - {title}"
        else:
            return title
    
    def _is_valid_title(self, title: str) -> bool:
        """Validate title format and length."""
        return 10 <= len(title) <= 60 and title.strip() != ""
    
    def _extract_key_sentences(self, content: str) -> List[str]:
        """Extract key sentences from content for meta description."""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        return sentences[:3]  # Return first 3 meaningful sentences
    
    def _determine_og_type(self, content_type: str) -> str:
        """Determine Open Graph type from content type."""
        type_mapping = {
            "article": "article",
            "blog": "article",
            "video": "video.other",
            "music": "music.song",
            "product": "product",
            "review": "article"
        }
        return type_mapping.get(content_type, "website")
    
    def _determine_schema_type(self, content_type: str) -> SchemaType:
        """Determine schema type from content type."""
        type_mapping = {
            "article": SchemaType.ARTICLE,
            "blog": SchemaType.BLOG_POSTING,
            "tutorial": SchemaType.HOW_TO,
            "review": SchemaType.REVIEW,
            "video": SchemaType.VIDEO_OBJECT,
            "music": SchemaType.MUSIC_RECORDING,
            "product": SchemaType.PRODUCT
        }
        return type_mapping.get(content_type, SchemaType.ARTICLE)
    
    def _determine_youtube_category(self, content_type: str) -> str:
        """Determine YouTube category from content type."""
        category_mapping = {
            "tutorial": "Education",
            "music": "Music",
            "review": "People & Blogs",
            "gaming": "Gaming",
            "tech": "Science & Technology",
            "lifestyle": "People & Blogs"
        }
        return category_mapping.get(content_type, "Entertainment")
    
    def _validate_json_ld(self, json_string: str) -> bool:
        """Validate JSON-LD format."""
        try:
            json.loads(json_string)
            return True
        except json.JSONDecodeError:
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        return bool(url and (url.startswith('http://') or url.startswith('https://')))