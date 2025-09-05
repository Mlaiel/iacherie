"""Advanced Content Optimization Engine - AI-Powered Content Enhancement System
===============================================================================

Comprehensive content optimization system providing intelligent format adaptation,
hashtag optimization, A/B testing, content enhancement, SEO optimization, and
automated content improvements for maximum performance across all platforms.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/distribution/content_optimization_engine.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Integration:
Creator Upload → AI Processing → Protection → SEO → Content Optimization →
Format Adaptation → Hashtag Intelligence → A/B Testing → Performance Enhancement
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import re
import hashlib
import secrets
import statistics
from collections import Counter, defaultdict
import math

logger = logging.getLogger(__name__)


class OptimizationType(str, Enum):
    """Content optimization types."""
    FORMAT_ADAPTATION = "format_adaptation"
    HASHTAG_OPTIMIZATION = "hashtag_optimization"
    SEO_ENHANCEMENT = "seo_enhancement"
    TITLE_OPTIMIZATION = "title_optimization"
    DESCRIPTION_ENHANCEMENT = "description_enhancement"
    THUMBNAIL_OPTIMIZATION = "thumbnail_optimization"
    AUDIO_ENHANCEMENT = "audio_enhancement"
    VIDEO_OPTIMIZATION = "video_optimization"
    TEXT_IMPROVEMENT = "text_improvement"
    ENGAGEMENT_BOOSTING = "engagement_boosting"


class TestVariationType(str, Enum):
    """A/B test variation types."""
    TITLE_VARIATION = "title_variation"
    THUMBNAIL_VARIATION = "thumbnail_variation"
    DESCRIPTION_VARIATION = "description_variation"
    HASHTAG_VARIATION = "hashtag_variation"
    TIMING_VARIATION = "timing_variation"
    FORMAT_VARIATION = "format_variation"
    CTA_VARIATION = "cta_variation"


class ContentFormat(str, Enum):
    """Content format types."""
    VIDEO_LANDSCAPE = "video_landscape"
    VIDEO_PORTRAIT = "video_portrait"
    VIDEO_SQUARE = "video_square"
    IMAGE_LANDSCAPE = "image_landscape"
    IMAGE_PORTRAIT = "image_portrait"
    IMAGE_SQUARE = "image_square"
    AUDIO_PODCAST = "audio_podcast"
    AUDIO_MUSIC = "audio_music"
    TEXT_SHORT = "text_short"
    TEXT_LONG = "text_long"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"


class HashtagCategory(str, Enum):
    """Hashtag categorization."""
    TRENDING = "trending"
    NICHE = "niche"
    BRANDED = "branded"
    COMMUNITY = "community"
    DESCRIPTIVE = "descriptive"
    EMOTIONAL = "emotional"
    LOCATION = "location"
    EVENT = "event"


@dataclass
class OptimizationResult:
    """Result of content optimization process."""
    optimization_id: str
    content_id: str
    optimization_type: OptimizationType
    original_content: Dict[str, Any]
    optimized_content: Dict[str, Any]
    improvements: Dict[str, float]  # Expected percentage improvements
    confidence_score: float
    applied_techniques: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HashtagAnalysis:
    """Hashtag analysis and optimization results."""
    hashtag: str
    category: HashtagCategory
    popularity_score: float
    competition_level: float
    relevance_score: float
    engagement_potential: float
    trending_status: bool
    usage_frequency: int
    suggested_placement: int  # Position in hashtag list
    similar_hashtags: List[str] = field(default_factory=list)


@dataclass
class ABTestVariation:
    """A/B test variation configuration."""
    variation_id: str
    variation_type: TestVariationType
    content_modifications: Dict[str, Any]
    traffic_split: float  # Percentage of traffic (0.0-1.0)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    sample_size: int = 0
    statistical_significance: float = 0.0
    is_winner: bool = False


@dataclass
class ABTestConfiguration:
    """A/B test configuration."""
    test_id: str
    content_id: str
    test_name: str
    variations: List[ABTestVariation]
    primary_metric: str
    secondary_metrics: List[str]
    duration: timedelta
    min_sample_size: int
    confidence_level: float
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "created"


@dataclass
class FormatOptimization:
    """Format optimization recommendations."""
    platform: str
    recommended_format: ContentFormat
    aspect_ratio: str
    resolution: str
    duration_range: Optional[Tuple[int, int]] = None
    file_size_limit: Optional[int] = None
    quality_settings: Dict[str, Any] = field(default_factory=dict)
    optimization_reasoning: str = ""


@dataclass
class SEOOptimization:
    """SEO optimization recommendations."""
    title_optimized: str
    description_optimized: str
    keywords: List[str]
    meta_tags: Dict[str, str]
    alt_text: str
    url_slug: str
    structured_data: Dict[str, Any] = field(default_factory=dict)
    seo_score: float = 0.0
    improvement_areas: List[str] = field(default_factory=list)


class ContentOptimizationEngine:
    """Core content optimization engine."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ContentOptimizationEngine")
        
        # Optimization models and data
        self.hashtag_database: Dict[str, HashtagAnalysis] = {}
        self.trending_hashtags: Dict[str, float] = {}
        self.platform_specifications: Dict[str, Dict[str, Any]] = {}
        self.seo_keywords: Dict[str, float] = {}
        self.optimization_history: List[OptimizationResult] = []
        self.active_ab_tests: Dict[str, ABTestConfiguration] = {}
        
        # Performance tracking
        self.optimization_stats = {
            "total_optimizations": 0,
            "success_rate": 0.0,
            "average_improvement": 0.0
        }
        
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the content optimization engine."""
        try:
            # Load platform specifications
            await self._load_platform_specifications()
            
            # Initialize hashtag database
            await self._initialize_hashtag_database()
            
            # Load trending data
            await self._load_trending_data()
            
            # Initialize SEO keyword database
            await self._initialize_seo_keywords()
            
            self.initialized = True
            self.logger.info("✅ Content Optimization Engine initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize optimization engine: {e}")
            return False
    
    async def _load_platform_specifications(self):
        """Load platform-specific content specifications."""
        self.platform_specifications = {
            "youtube": {
                "video": {
                    "recommended_format": ContentFormat.VIDEO_LANDSCAPE,
                    "aspect_ratio": "16:9",
                    "resolution": "1920x1080",
                    "duration_range": (60, 3600),  # 1 min to 1 hour
                    "file_size_limit": 256 * 1024 * 1024,  # 256MB
                    "thumbnail_size": "1280x720"
                },
                "title_length": 100,
                "description_length": 5000,
                "hashtag_limit": 15
            },
            "instagram": {
                "image": {
                    "recommended_format": ContentFormat.IMAGE_SQUARE,
                    "aspect_ratio": "1:1",
                    "resolution": "1080x1080",
                    "file_size_limit": 30 * 1024 * 1024  # 30MB
                },
                "video": {
                    "recommended_format": ContentFormat.VIDEO_SQUARE,
                    "aspect_ratio": "1:1",
                    "resolution": "1080x1080",
                    "duration_range": (3, 60),  # 3 sec to 1 min
                    "file_size_limit": 100 * 1024 * 1024  # 100MB
                },
                "reel": {
                    "recommended_format": ContentFormat.REEL,
                    "aspect_ratio": "9:16",
                    "resolution": "1080x1920",
                    "duration_range": (15, 30),
                    "file_size_limit": 250 * 1024 * 1024  # 250MB
                },
                "title_length": 125,
                "description_length": 2200,
                "hashtag_limit": 30
            },
            "tiktok": {
                "video": {
                    "recommended_format": ContentFormat.VIDEO_PORTRAIT,
                    "aspect_ratio": "9:16",
                    "resolution": "1080x1920",
                    "duration_range": (15, 180),  # 15 sec to 3 min
                    "file_size_limit": 4000 * 1024 * 1024  # 4GB
                },
                "title_length": 150,
                "description_length": 2200,
                "hashtag_limit": 100
            },
            "twitter": {
                "image": {
                    "recommended_format": ContentFormat.IMAGE_LANDSCAPE,
                    "aspect_ratio": "16:9",
                    "resolution": "1200x675",
                    "file_size_limit": 5 * 1024 * 1024  # 5MB
                },
                "video": {
                    "recommended_format": ContentFormat.VIDEO_LANDSCAPE,
                    "aspect_ratio": "16:9",
                    "resolution": "1280x720",
                    "duration_range": (1, 140),  # 1 sec to 2:20 min
                    "file_size_limit": 512 * 1024 * 1024  # 512MB
                },
                "title_length": 280,
                "hashtag_limit": 10
            },
            "facebook": {
                "image": {
                    "recommended_format": ContentFormat.IMAGE_LANDSCAPE,
                    "aspect_ratio": "1.91:1",
                    "resolution": "1200x630",
                    "file_size_limit": 100 * 1024 * 1024  # 100MB
                },
                "video": {
                    "recommended_format": ContentFormat.VIDEO_LANDSCAPE,
                    "aspect_ratio": "16:9",
                    "resolution": "1920x1080",
                    "duration_range": (1, 7200),  # 1 sec to 2 hours
                    "file_size_limit": 10 * 1024 * 1024 * 1024  # 10GB
                },
                "title_length": 255,
                "description_length": 63206,
                "hashtag_limit": 30
            }
        }
    
    async def _initialize_hashtag_database(self):
        """Initialize hashtag analysis database."""
        # Sample hashtag data - in production, this would be loaded from analytics
        sample_hashtags = [
            ("#contentcreator", HashtagCategory.COMMUNITY, 0.8, 0.9, 0.9, 0.85, True, 1500000),
            ("#viral", HashtagCategory.TRENDING, 0.95, 0.95, 0.7, 0.9, True, 2000000),
            ("#ai", HashtagCategory.NICHE, 0.7, 0.6, 0.9, 0.8, True, 800000),
            ("#technology", HashtagCategory.DESCRIPTIVE, 0.8, 0.7, 0.8, 0.75, False, 1200000),
            ("#innovation", HashtagCategory.DESCRIPTIVE, 0.6, 0.5, 0.8, 0.7, False, 600000),
            ("#socialmedia", HashtagCategory.COMMUNITY, 0.75, 0.8, 0.85, 0.8, False, 1000000),
            ("#trending", HashtagCategory.TRENDING, 0.9, 0.95, 0.6, 0.8, True, 1800000),
            ("#fyp", HashtagCategory.TRENDING, 0.95, 0.98, 0.5, 0.85, True, 3000000),
            ("#music", HashtagCategory.DESCRIPTIVE, 0.85, 0.75, 0.9, 0.85, False, 2500000),
            ("#artist", HashtagCategory.COMMUNITY, 0.7, 0.6, 0.9, 0.8, False, 900000)
        ]
        
        for hashtag, category, popularity, competition, relevance, engagement, trending, frequency in sample_hashtags:
            self.hashtag_database[hashtag] = HashtagAnalysis(
                hashtag=hashtag,
                category=category,
                popularity_score=popularity,
                competition_level=competition,
                relevance_score=relevance,
                engagement_potential=engagement,
                trending_status=trending,
                usage_frequency=frequency,
                suggested_placement=0,  # Will be calculated
                similar_hashtags=[]
            )
        
        # Build similar hashtags relationships
        await self._build_hashtag_relationships()
    
    async def _build_hashtag_relationships(self):
        """Build relationships between similar hashtags."""
        hashtag_list = list(self.hashtag_database.keys())
        
        for hashtag in hashtag_list:
            similar = []
            for other_hashtag in hashtag_list:
                if hashtag != other_hashtag:
                    # Simple similarity based on category and engagement
                    hashtag_analysis = self.hashtag_database[hashtag]
                    other_analysis = self.hashtag_database[other_hashtag]
                    
                    if (hashtag_analysis.category == other_analysis.category or
                        abs(hashtag_analysis.engagement_potential - other_analysis.engagement_potential) < 0.2):
                        similar.append(other_hashtag)
            
            self.hashtag_database[hashtag].similar_hashtags = similar[:5]  # Top 5 similar
    
    async def _load_trending_data(self):
        """Load current trending hashtags and topics."""
        # Simulate trending data - in production, this would come from real-time APIs
        self.trending_hashtags = {
            "#viral": 0.95,
            "#trending": 0.9,
            "#fyp": 0.95,
            "#contentcreator": 0.8,
            "#ai": 0.85,
            "#2025trends": 0.7,
            "#socialmedia": 0.75,
            "#innovation": 0.6
        }
    
    async def _initialize_seo_keywords(self):
        """Initialize SEO keyword database."""
        # Sample SEO keywords with search volume scores
        self.seo_keywords = {
            "content creation": 0.9,
            "social media": 0.95,
            "viral content": 0.8,
            "digital marketing": 0.85,
            "influencer": 0.9,
            "online presence": 0.7,
            "engagement": 0.8,
            "brand awareness": 0.75,
            "content strategy": 0.85,
            "audience growth": 0.8
        }
    
    async def optimize_content(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        target_platforms: List[str],
        optimization_goals: List[OptimizationType]
    ) -> OptimizationResult:
        """Perform comprehensive content optimization."""
        if not self.initialized:
            await self.initialize()
        
        optimization_id = f"opt_{uuid4().hex[:8]}"
        original_content = content_data.copy()
        optimized_content = content_data.copy()
        applied_techniques = []
        improvements = {}
        recommendations = []
        
        try:
            # Apply each optimization type
            for optimization_type in optimization_goals:
                if optimization_type == OptimizationType.HASHTAG_OPTIMIZATION:
                    result = await self._optimize_hashtags(optimized_content, target_platforms)
                    optimized_content.update(result["content_updates"])
                    applied_techniques.extend(result["techniques"])
                    improvements.update(result["improvements"])
                    recommendations.extend(result["recommendations"])
                
                elif optimization_type == OptimizationType.FORMAT_ADAPTATION:
                    result = await self._optimize_format(optimized_content, target_platforms)
                    optimized_content.update(result["content_updates"])
                    applied_techniques.extend(result["techniques"])
                    improvements.update(result["improvements"])
                
                elif optimization_type == OptimizationType.SEO_ENHANCEMENT:
                    result = await self._optimize_seo(optimized_content)
                    optimized_content.update(result["content_updates"])
                    applied_techniques.extend(result["techniques"])
                    improvements.update(result["improvements"])
                
                elif optimization_type == OptimizationType.TITLE_OPTIMIZATION:
                    result = await self._optimize_title(optimized_content, target_platforms)
                    optimized_content.update(result["content_updates"])
                    applied_techniques.extend(result["techniques"])
                    improvements.update(result["improvements"])
                
                elif optimization_type == OptimizationType.DESCRIPTION_ENHANCEMENT:
                    result = await self._optimize_description(optimized_content, target_platforms)
                    optimized_content.update(result["content_updates"])
                    applied_techniques.extend(result["techniques"])
                    improvements.update(result["improvements"])
            
            # Calculate overall confidence score
            confidence_score = self._calculate_optimization_confidence(applied_techniques, improvements)
            
            # Create optimization result
            optimization_result = OptimizationResult(
                optimization_id=optimization_id,
                content_id=content_id,
                optimization_type=optimization_goals[0] if optimization_goals else OptimizationType.FORMAT_ADAPTATION,
                original_content=original_content,
                optimized_content=optimized_content,
                improvements=improvements,
                confidence_score=confidence_score,
                applied_techniques=applied_techniques,
                recommendations=recommendations
            )
            
            # Store optimization history
            self.optimization_history.append(optimization_result)
            self.optimization_stats["total_optimizations"] += 1
            
            self.logger.info(f"✅ Content optimization completed: {optimization_id}")
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"Error optimizing content: {e}")
            return OptimizationResult(
                optimization_id=optimization_id,
                content_id=content_id,
                optimization_type=optimization_goals[0] if optimization_goals else OptimizationType.FORMAT_ADAPTATION,
                original_content=original_content,
                optimized_content=original_content,
                improvements={},
                confidence_score=0.0,
                applied_techniques=[],
                recommendations=[f"Optimization failed: {str(e)}"]
            )
    
    async def _optimize_hashtags(self, content: Dict[str, Any], platforms: List[str]) -> Dict[str, Any]:
        """Optimize hashtags for maximum reach and engagement."""
        content_text = f"{content.get('title', '')} {content.get('description', '')}"
        content_category = content.get('category', 'general')
        
        # Analyze current hashtags
        current_hashtags = content.get('hashtags', [])
        
        # Generate optimal hashtag mix
        optimal_hashtags = await self._generate_optimal_hashtag_mix(
            content_text, content_category, platforms, current_hashtags
        )
        
        # Calculate improvements
        current_score = self._calculate_hashtag_performance_score(current_hashtags)
        optimal_score = self._calculate_hashtag_performance_score(optimal_hashtags)
        
        improvement = ((optimal_score - current_score) / current_score * 100) if current_score > 0 else 50
        
        return {
            "content_updates": {"hashtags": optimal_hashtags},
            "techniques": ["hashtag_analysis", "trending_integration", "category_optimization"],
            "improvements": {"hashtag_performance": improvement, "discoverability": improvement * 0.8},
            "recommendations": [
                f"Added {len(optimal_hashtags) - len(current_hashtags)} optimized hashtags",
                "Integrated trending hashtags for increased visibility",
                "Balanced popular and niche hashtags for better reach"
            ]
        }
    
    async def _generate_optimal_hashtag_mix(
        self,
        content_text: str,
        category: str,
        platforms: List[str],
        current_hashtags: List[str]
    ) -> List[str]:
        """Generate optimal hashtag mix based on content and platforms."""
        optimal_hashtags = set()
        
        # Keep good existing hashtags
        for hashtag in current_hashtags:
            if hashtag in self.hashtag_database:
                analysis = self.hashtag_database[hashtag]
                if analysis.engagement_potential > 0.7:
                    optimal_hashtags.add(hashtag)
        
        # Add trending hashtags
        trending_count = 0
        for hashtag, score in self.trending_hashtags.items():
            if trending_count < 3 and hashtag not in optimal_hashtags:
                optimal_hashtags.add(hashtag)
                trending_count += 1
        
        # Add category-specific hashtags
        category_hashtags = [
            hashtag for hashtag, analysis in self.hashtag_database.items()
            if category.lower() in hashtag.lower() or analysis.category == HashtagCategory.NICHE
        ]
        
        for hashtag in category_hashtags[:2]:
            if hashtag not in optimal_hashtags:
                optimal_hashtags.add(hashtag)
        
        # Add community hashtags for engagement
        community_hashtags = [
            hashtag for hashtag, analysis in self.hashtag_database.items()
            if analysis.category == HashtagCategory.COMMUNITY and analysis.engagement_potential > 0.8
        ]
        
        for hashtag in community_hashtags[:3]:
            if hashtag not in optimal_hashtags:
                optimal_hashtags.add(hashtag)
        
        # Ensure we don't exceed platform limits
        max_hashtags = min([
            self.platform_specifications.get(platform, {}).get("hashtag_limit", 30)
            for platform in platforms
        ]) if platforms else 15
        
        return list(optimal_hashtags)[:max_hashtags]
    
    def _calculate_hashtag_performance_score(self, hashtags: List[str]) -> float:
        """Calculate performance score for hashtag set."""
        if not hashtags:
            return 0.0
        
        total_score = 0.0
        for hashtag in hashtags:
            if hashtag in self.hashtag_database:
                analysis = self.hashtag_database[hashtag]
                # Weight engagement potential and popularity, penalize high competition
                score = (analysis.engagement_potential * 0.5 + 
                        analysis.popularity_score * 0.3 - 
                        analysis.competition_level * 0.2)
                total_score += max(score, 0.0)
        
        return total_score / len(hashtags)
    
    async def _optimize_format(self, content: Dict[str, Any], platforms: List[str]) -> Dict[str, Any]:
        """Optimize content format for target platforms."""
        content_type = content.get('content_type', 'unknown')
        
        format_recommendations = []
        content_updates = {}
        
        for platform in platforms:
            if platform in self.platform_specifications:
                platform_specs = self.platform_specifications[platform]
                
                # Find matching content type specs
                if 'video' in content_type and 'video' in platform_specs:
                    video_specs = platform_specs['video']
                    format_opt = FormatOptimization(
                        platform=platform,
                        recommended_format=video_specs['recommended_format'],
                        aspect_ratio=video_specs['aspect_ratio'],
                        resolution=video_specs['resolution'],
                        duration_range=video_specs.get('duration_range'),
                        file_size_limit=video_specs.get('file_size_limit'),
                        optimization_reasoning=f"Optimized for {platform} video specifications"
                    )
                    format_recommendations.append(format_opt)
                
                elif 'image' in content_type and 'image' in platform_specs:
                    image_specs = platform_specs['image']
                    format_opt = FormatOptimization(
                        platform=platform,
                        recommended_format=image_specs['recommended_format'],
                        aspect_ratio=image_specs['aspect_ratio'],
                        resolution=image_specs['resolution'],
                        file_size_limit=image_specs.get('file_size_limit'),
                        optimization_reasoning=f"Optimized for {platform} image specifications"
                    )
                    format_recommendations.append(format_opt)
        
        # Apply format optimizations
        if format_recommendations:
            # Choose most common recommendation or best performing platform
            primary_format = format_recommendations[0]
            content_updates.update({
                'recommended_format': primary_format.recommended_format.value,
                'aspect_ratio': primary_format.aspect_ratio,
                'resolution': primary_format.resolution,
                'format_optimizations': [
                    {
                        'platform': fmt.platform,
                        'format': fmt.recommended_format.value,
                        'aspect_ratio': fmt.aspect_ratio,
                        'resolution': fmt.resolution
                    }
                    for fmt in format_recommendations
                ]
            })
        
        return {
            "content_updates": content_updates,
            "techniques": ["platform_specification_analysis", "format_adaptation", "resolution_optimization"],
            "improvements": {"format_compatibility": 80.0, "platform_performance": 60.0}
        }
    
    async def _optimize_seo(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content for SEO."""
        title = content.get('title', '')
        description = content.get('description', '')
        
        # Analyze and optimize title
        optimized_title = await self._optimize_title_for_seo(title)
        
        # Analyze and optimize description
        optimized_description = await self._optimize_description_for_seo(description)
        
        # Generate keywords
        keywords = await self._extract_seo_keywords(f"{optimized_title} {optimized_description}")
        
        # Generate meta tags
        meta_tags = {
            "title": optimized_title,
            "description": optimized_description[:160],  # Meta description limit
            "keywords": ", ".join(keywords[:10])
        }
        
        # Generate alt text for images
        alt_text = await self._generate_alt_text(content)
        
        # Generate URL slug
        url_slug = self._generate_url_slug(optimized_title)
        
        # Calculate SEO score
        seo_score = self._calculate_seo_score(optimized_title, optimized_description, keywords)
        
        seo_optimization = SEOOptimization(
            title_optimized=optimized_title,
            description_optimized=optimized_description,
            keywords=keywords,
            meta_tags=meta_tags,
            alt_text=alt_text,
            url_slug=url_slug,
            seo_score=seo_score
        )
        
        return {
            "content_updates": {
                "seo_optimization": seo_optimization.__dict__,
                "title": optimized_title,
                "description": optimized_description,
                "keywords": keywords,
                "url_slug": url_slug
            },
            "techniques": ["keyword_optimization", "meta_tag_generation", "seo_scoring"],
            "improvements": {"seo_score": (seo_score - 0.5) * 100, "search_visibility": seo_score * 80}
        }
    
    async def _optimize_title_for_seo(self, title: str) -> str:
        """Optimize title for SEO."""
        if not title:
            return title
        
        # Add high-value keywords if not present
        title_lower = title.lower()
        for keyword, score in sorted(self.seo_keywords.items(), key=lambda x: x[1], reverse=True)[:3]:
            if keyword not in title_lower and len(title) + len(keyword) + 3 < 100:
                title = f"{title} - {keyword.title()}"
                break
        
        return title
    
    async def _optimize_description_for_seo(self, description: str) -> str:
        """Optimize description for SEO."""
        if not description:
            return description
        
        # Ensure description has good keyword density
        words = description.split()
        if len(words) < 20:
            # Add relevant keywords to short descriptions
            for keyword, score in sorted(self.seo_keywords.items(), key=lambda x: x[1], reverse=True)[:2]:
                if keyword.lower() not in description.lower():
                    description += f" This content focuses on {keyword} and related topics."
        
        return description
    
    async def _extract_seo_keywords(self, text: str) -> List[str]:
        """Extract SEO keywords from content."""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword, score in self.seo_keywords.items():
            if keyword in text_lower:
                found_keywords.append((keyword, score))
        
        # Sort by score and return top keywords
        found_keywords.sort(key=lambda x: x[1], reverse=True)
        return [keyword for keyword, _ in found_keywords[:10]]
    
    async def _generate_alt_text(self, content: Dict[str, Any]) -> str:
        """Generate alt text for accessibility."""
        title = content.get('title', '')
        content_type = content.get('content_type', '')
        
        if 'image' in content_type:
            return f"Image: {title}" if title else "Content image"
        elif 'video' in content_type:
            return f"Video: {title}" if title else "Content video"
        else:
            return title if title else "Content"
    
    def _generate_url_slug(self, title: str) -> str:
        """Generate URL slug from title."""
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')[:50]  # Limit length
    
    def _calculate_seo_score(self, title: str, description: str, keywords: List[str]) -> float:
        """Calculate SEO score based on optimization factors."""
        score = 0.0
        
        # Title score (30%)
        if title:
            title_score = 0.5  # Base score
            if len(title) >= 30:
                title_score += 0.2
            if len(keywords) > 0 and any(kw in title.lower() for kw in keywords):
                title_score += 0.3
            score += title_score * 0.3
        
        # Description score (40%)
        if description:
            desc_score = 0.5  # Base score
            if len(description) >= 100:
                desc_score += 0.2
            if len(keywords) > 0 and any(kw in description.lower() for kw in keywords):
                desc_score += 0.3
            score += desc_score * 0.4
        
        # Keywords score (30%)
        if keywords:
            keyword_score = min(len(keywords) / 5.0, 1.0)  # Max score at 5+ keywords
            score += keyword_score * 0.3
        
        return min(score, 1.0)
    
    async def _optimize_title(self, content: Dict[str, Any], platforms: List[str]) -> Dict[str, Any]:
        """Optimize title for specific platforms."""
        original_title = content.get('title', '')
        
        # Get platform title length limits
        min_length = min([
            self.platform_specifications.get(platform, {}).get("title_length", 100)
            for platform in platforms
        ]) if platforms else 100
        
        optimized_title = original_title
        
        # Ensure title is within limits
        if len(optimized_title) > min_length:
            optimized_title = optimized_title[:min_length-3] + "..."
        
        # Add emotional hooks if title is short
        if len(optimized_title) < 30:
            emotional_hooks = ["Amazing", "Incredible", "Must-See", "Exclusive", "Ultimate"]
            hook = secrets.choice(emotional_hooks)
            optimized_title = f"{hook} {optimized_title}"
        
        # Ensure it's still within limits
        if len(optimized_title) > min_length:
            optimized_title = optimized_title[:min_length-3] + "..."
        
        improvement = 20.0 if optimized_title != original_title else 0.0
        
        return {
            "content_updates": {"title": optimized_title},
            "techniques": ["length_optimization", "emotional_enhancement", "platform_compliance"],
            "improvements": {"title_performance": improvement, "click_through_rate": improvement * 0.7}
        }
    
    async def _optimize_description(self, content: Dict[str, Any], platforms: List[str]) -> Dict[str, Any]:
        """Optimize description for specific platforms."""
        original_description = content.get('description', '')
        
        # Get platform description length limits
        min_length = min([
            self.platform_specifications.get(platform, {}).get("description_length", 2000)
            for platform in platforms
        ]) if platforms else 2000
        
        optimized_description = original_description
        
        # Ensure description is within limits
        if len(optimized_description) > min_length:
            optimized_description = optimized_description[:min_length-3] + "..."
        
        # Add call-to-action if description is short
        if len(optimized_description) < 100:
            cta_phrases = [
                "What do you think?",
                "Share your thoughts below!",
                "Don't forget to like and follow!",
                "Tag someone who needs to see this!"
            ]
            cta = secrets.choice(cta_phrases)
            optimized_description = f"{optimized_description}\n\n{cta}"
        
        # Ensure it's still within limits
        if len(optimized_description) > min_length:
            optimized_description = optimized_description[:min_length-3] + "..."
        
        improvement = 15.0 if optimized_description != original_description else 0.0
        
        return {
            "content_updates": {"description": optimized_description},
            "techniques": ["length_optimization", "cta_integration", "engagement_enhancement"],
            "improvements": {"description_performance": improvement, "engagement_rate": improvement * 0.8}
        }
    
    def _calculate_optimization_confidence(self, techniques: List[str], improvements: Dict[str, float]) -> float:
        """Calculate overall optimization confidence score."""
        base_confidence = 0.7
        
        # Bonus for number of techniques applied
        technique_bonus = min(len(techniques) * 0.05, 0.2)
        
        # Bonus for expected improvements
        avg_improvement = statistics.mean(improvements.values()) if improvements else 0
        improvement_bonus = min(avg_improvement / 100.0 * 0.2, 0.1)
        
        total_confidence = base_confidence + technique_bonus + improvement_bonus
        return min(total_confidence, 1.0)
    
    async def create_ab_test(
        self,
        content_id: str,
        test_name: str,
        variations: List[Dict[str, Any]],
        primary_metric: str,
        duration_hours: int = 24
    ) -> ABTestConfiguration:
        """Create A/B test configuration for content optimization."""
        test_id = f"ab_{uuid4().hex[:8]}"
        
        # Create test variations
        test_variations = []
        traffic_per_variation = 1.0 / len(variations)
        
        for i, variation_data in enumerate(variations):
            variation = ABTestVariation(
                variation_id=f"{test_id}_var_{i}",
                variation_type=TestVariationType(variation_data.get("type", "title_variation")),
                content_modifications=variation_data.get("modifications", {}),
                traffic_split=traffic_per_variation
            )
            test_variations.append(variation)
        
        # Create test configuration
        ab_test = ABTestConfiguration(
            test_id=test_id,
            content_id=content_id,
            test_name=test_name,
            variations=test_variations,
            primary_metric=primary_metric,
            secondary_metrics=["engagement_rate", "click_through_rate"],
            duration=timedelta(hours=duration_hours),
            min_sample_size=1000,
            confidence_level=0.95
        )
        
        # Store test
        self.active_ab_tests[test_id] = ab_test
        
        self.logger.info(f"✅ A/B test created: {test_id}")
        return ab_test
    
    async def analyze_ab_test_results(self, test_id: str) -> Dict[str, Any]:
        """Analyze A/B test results and determine winner."""
        if test_id not in self.active_ab_tests:
            return {"error": "Test not found"}
        
        test = self.active_ab_tests[test_id]
        
        # Simulate test results - in production, this would use real analytics data
        for variation in test.variations:
            # Simulate performance metrics
            variation.performance_metrics = {
                "engagement_rate": 0.5 + secrets.randbelow(30) / 100.0,
                "click_through_rate": 0.2 + secrets.randbelow(20) / 100.0,
                "conversion_rate": 0.1 + secrets.randbelow(15) / 100.0
            }
            variation.sample_size = 1000 + secrets.randbelow(2000)
        
        # Determine winner based on primary metric
        best_variation = max(
            test.variations,
            key=lambda v: v.performance_metrics.get(test.primary_metric, 0)
        )
        best_variation.is_winner = True
        
        # Calculate statistical significance (simplified)
        best_score = best_variation.performance_metrics.get(test.primary_metric, 0)
        second_best_score = max(
            [v.performance_metrics.get(test.primary_metric, 0) 
             for v in test.variations if v != best_variation],
            default=0
        )
        
        improvement = ((best_score - second_best_score) / second_best_score * 100) if second_best_score > 0 else 0
        statistical_significance = min(improvement / 10.0, 0.99)  # Simplified calculation
        
        best_variation.statistical_significance = statistical_significance
        
        test.status = "completed"
        
        return {
            "test_id": test_id,
            "winner": {
                "variation_id": best_variation.variation_id,
                "improvements": best_variation.performance_metrics,
                "statistical_significance": statistical_significance,
                "confidence_level": test.confidence_level
            },
            "all_variations": [
                {
                    "variation_id": v.variation_id,
                    "performance": v.performance_metrics,
                    "sample_size": v.sample_size,
                    "is_winner": v.is_winner
                }
                for v in test.variations
            ],
            "recommendations": [
                f"Implement winning variation {best_variation.variation_id}",
                f"Expected improvement: {improvement:.2f}%",
                "Continue testing with new variations for further optimization"
            ]
        }
    
    async def get_optimization_insights(self) -> Dict[str, Any]:
        """Get insights from optimization history."""
        if not self.optimization_history:
            return {"message": "No optimization history available"}
        
        # Calculate success metrics
        successful_optimizations = [
            opt for opt in self.optimization_history
            if opt.confidence_score > 0.7 and any(imp > 10 for imp in opt.improvements.values())
        ]
        
        success_rate = len(successful_optimizations) / len(self.optimization_history) * 100
        
        # Most effective techniques
        technique_effectiveness = defaultdict(list)
        for opt in successful_optimizations:
            avg_improvement = statistics.mean(opt.improvements.values()) if opt.improvements else 0
            for technique in opt.applied_techniques:
                technique_effectiveness[technique].append(avg_improvement)
        
        best_techniques = [
            (technique, statistics.mean(improvements))
            for technique, improvements in technique_effectiveness.items()
        ]
        best_techniques.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "total_optimizations": len(self.optimization_history),
            "success_rate": success_rate,
            "average_improvement": statistics.mean([
                statistics.mean(opt.improvements.values()) if opt.improvements else 0
                for opt in self.optimization_history
            ]),
            "most_effective_techniques": best_techniques[:5],
            "optimization_types_used": list(set([
                opt.optimization_type.value for opt in self.optimization_history
            ])),
            "active_ab_tests": len([t for t in self.active_ab_tests.values() if t.status != "completed"])
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        self.hashtag_database.clear()
        self.trending_hashtags.clear()
        self.platform_specifications.clear()
        self.seo_keywords.clear()
        self.optimization_history.clear()
        self.active_ab_tests.clear()
        
        self.logger.info("✅ Content Optimization Engine cleaned up")


# Global engine instance
_optimization_engine: Optional[ContentOptimizationEngine] = None


async def get_content_optimization_engine() -> ContentOptimizationEngine:
    """Get the global content optimization engine instance."""
    global _optimization_engine
    
    if _optimization_engine is None:
        _optimization_engine = ContentOptimizationEngine()
        await _optimization_engine.initialize()
    
    return _optimization_engine


# Export main components
__all__ = [
    "OptimizationType",
    "TestVariationType",
    "ContentFormat",
    "HashtagCategory",
    "OptimizationResult",
    "HashtagAnalysis",
    "ABTestVariation",
    "ABTestConfiguration",
    "FormatOptimization",
    "SEOOptimization",
    "ContentOptimizationEngine",
    "get_content_optimization_engine"
]