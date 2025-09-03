"""Meta Generator - SEO Meta Tags Generation Service

Advanced meta tags generation service that leverages the existing metadata generator
for comprehensive meta tag creation and optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

# Import from existing SEO engine
from ....seo_engine.metadata_generator import (
    MetadataGenerator as BaseMetadataGenerator,
    GeneratedMetadata,
    MetaTags,
    OpenGraphTags,
    TwitterCardTags,
    SchemaMarkup,
    MetadataType
)

logger = logging.getLogger(__name__)


@dataclass
class MetaGenerationRequest:
    """Request for meta tag generation"""
    content: str
    target_keywords: List[str]
    title: Optional[str] = None
    description: Optional[str] = None
    url_path: Optional[str] = None
    images: Optional[List[str]] = None
    metadata_types: List[MetadataType] = None


@dataclass
class MetaGenerationResult:
    """Result of meta tag generation"""
    meta_tags: MetaTags
    open_graph: Optional[OpenGraphTags] = None
    twitter_cards: Optional[TwitterCardTags] = None
    schema_markup: Optional[SchemaMarkup] = None
    html_output: str = ""
    timestamp: datetime = None


class MetaGenerator:
    """Analytics-integrated meta tags generation service"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        # Set default config values for the base generator
        base_config = {
            'base_url': self.config.get('base_url', 'https://example.com'),
            'default_author': self.config.get('default_author', 'Fahed Mlaiel'),
            **self.config
        }
        self.base_generator = BaseMetadataGenerator(config=base_config)
        logger.info("Analytics MetaGenerator service initialized")
    
    async def generate_meta_tags(self, request: MetaGenerationRequest) -> MetaGenerationResult:
        """
        Generate comprehensive meta tags
        
        Args:
            request: Meta generation request parameters
            
        Returns:
            MetaGenerationResult: Generated meta tags and markup
        """
        try:
            # Use existing metadata generator
            metadata = await self.base_generator.generate_metadata(
                content=request.content,
                target_keywords=request.target_keywords,
                content_type="article",  # Default content type
                url_path=request.url_path,
                images=request.images,
                author=None,  # Will use default
                publish_date=None  # Current time will be used
            )
            
            result = MetaGenerationResult(
                meta_tags=metadata.meta_tags,
                open_graph=metadata.open_graph,
                twitter_cards=metadata.twitter_cards,
                schema_markup=metadata.schema_markups[0] if metadata.schema_markups else None,
                html_output=metadata.html_output,
                timestamp=datetime.now()
            )
            
            logger.info("Meta tags generation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Meta tags generation failed: {str(e)}")
            raise
    
    async def generate_basic_meta(self, title: str, description: str, keywords: List[str]) -> MetaTags:
        """
        Generate basic meta tags quickly
        
        Args:
            title: Page title
            description: Meta description
            keywords: Target keywords
            
        Returns:
            MetaTags: Basic meta tags
        """
        try:
            content = f"Title: {title}\nDescription: {description}"
            
            request = MetaGenerationRequest(
                content=content,
                target_keywords=keywords,
                title=title,
                description=description,
                metadata_types=[MetadataType.TITLE_TAG, MetadataType.META_DESCRIPTION]
            )
            
            result = await self.generate_meta_tags(request)
            return result.meta_tags
            
        except Exception as e:
            logger.error(f"Basic meta generation failed: {str(e)}")
            raise
    
    async def generate_social_meta(self, title: str, description: str, image_url: str) -> Dict[str, Any]:
        """
        Generate social media meta tags (Open Graph & Twitter Cards)
        
        Args:
            title: Social media title
            description: Social media description
            image_url: Featured image URL
            
        Returns:
            Dict containing Open Graph and Twitter Cards data
        """
        try:
            content = f"Title: {title}\nDescription: {description}"
            
            request = MetaGenerationRequest(
                content=content,
                target_keywords=[],
                title=title,
                description=description,
                images=[image_url],
                metadata_types=[MetadataType.OPEN_GRAPH, MetadataType.TWITTER_CARDS]
            )
            
            result = await self.generate_meta_tags(request)
            
            return {
                'open_graph': {
                    'title': result.open_graph.title if result.open_graph else title,
                    'description': result.open_graph.description if result.open_graph else description,
                    'image': result.open_graph.image if result.open_graph else image_url,
                    'type': result.open_graph.type if result.open_graph else 'website'
                },
                'twitter_cards': {
                    'card': result.twitter_cards.card if result.twitter_cards else 'summary_large_image',
                    'title': result.twitter_cards.title if result.twitter_cards else title,
                    'description': result.twitter_cards.description if result.twitter_cards else description,
                    'image': result.twitter_cards.image if result.twitter_cards else image_url
                }
            }
            
        except Exception as e:
            logger.error(f"Social meta generation failed: {str(e)}")
            raise
    
    async def validate_meta_tags(self, meta_tags: MetaTags) -> Dict[str, bool]:
        """
        Validate meta tags for SEO compliance
        
        Args:
            meta_tags: Meta tags to validate
            
        Returns:
            Dict with validation results
        """
        validation_results = {
            'title_length_ok': 30 <= len(meta_tags.title) <= 60,
            'description_length_ok': 120 <= len(meta_tags.description) <= 155,
            'has_keywords': bool(meta_tags.keywords),
            'has_canonical': bool(meta_tags.canonical_url),
            'robots_directive_ok': 'noindex' not in meta_tags.robots.lower()
        }
        
        return validation_results