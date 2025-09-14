"""SEO Implementation - Professional SEO Optimization System

Advanced SEO implementation for the Ainflue platform providing comprehensive
search engine optimization, content discoverability, and organic growth strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class SEOStrategy(Enum):
    """SEO strategy types"""
    CONTENT_OPTIMIZATION = "content_optimization"
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    TECHNICAL_SEO = "technical_seo"
    LOCAL_SEO = "local_seo"
    SOCIAL_SEO = "social_seo"
    VIDEO_SEO = "video_seo"
    IMAGE_SEO = "image_seo"
    VOICE_SEARCH_OPTIMIZATION = "voice_search_optimization"


class ContentType(Enum):
    """Content types for SEO optimization"""
    BLOG_POST = "blog_post"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    SOCIAL_POST = "social_post"
    PRODUCT_PAGE = "product_page"
    LANDING_PAGE = "landing_page"
    PROFILE_PAGE = "profile_page"


class SEOPriority(Enum):
    """SEO optimization priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class KeywordAnalysis:
    """Keyword analysis result"""
    keyword: str
    search_volume: int
    competition_level: float
    difficulty_score: float
    relevance_score: float
    opportunity_score: float
    suggested_usage: str  # primary, secondary, long_tail
    related_keywords: List[str] = field(default_factory=list)


@dataclass
class SEOAudit:
    """SEO audit result"""
    audit_id: str
    content_id: str
    content_type: ContentType
    overall_score: float
    technical_score: float
    content_score: float
    keyword_score: float
    performance_score: float
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    audit_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SEOOptimization:
    """SEO optimization result"""
    optimization_id: str
    content_id: str
    creator_id: str
    strategies_applied: List[SEOStrategy]
    keywords_optimized: List[KeywordAnalysis]
    technical_improvements: Dict[str, Any]
    content_improvements: Dict[str, Any]
    performance_impact: Dict[str, float]
    optimization_score: float
    estimated_traffic_increase: float
    completion_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SEOResult:
    """SEO operation result"""
    operation_id: str
    content_id: str
    creator_id: str
    success: bool
    audit: Optional[SEOAudit] = None
    optimization: Optional[SEOOptimization] = None
    processing_time: float = 0.0
    error_message: Optional[str] = None


class SEOImplementation:
    """
    Advanced SEO Implementation for Ainflue Platform
    
    Provides comprehensive SEO optimization including keyword research,
    content optimization, technical SEO, and performance tracking.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # SEO configuration
        self.target_languages = self.config.get("target_languages", ["en", "es", "fr", "de"])
        self.target_regions = self.config.get("target_regions", ["US", "UK", "CA", "AU"])
        self.seo_update_frequency = self.config.get("seo_update_frequency", "weekly")
        
        # SEO databases
        self.seo_audits: Dict[str, SEOAudit] = {}
        self.seo_optimizations: Dict[str, SEOOptimization] = {}
        self.keyword_database: Dict[str, List[KeywordAnalysis]] = {}
        
        # SEO optimization engines
        self.content_optimizers = {
            ContentType.BLOG_POST: self._optimize_blog_post_seo,
            ContentType.VIDEO: self._optimize_video_seo,
            ContentType.AUDIO: self._optimize_audio_seo,
            ContentType.IMAGE: self._optimize_image_seo,
            ContentType.SOCIAL_POST: self._optimize_social_post_seo,
            ContentType.PRODUCT_PAGE: self._optimize_product_page_seo,
            ContentType.LANDING_PAGE: self._optimize_landing_page_seo,
            ContentType.PROFILE_PAGE: self._optimize_profile_page_seo
        }
        
        # SEO audit engines
        self.audit_engines = {
            "technical": self._audit_technical_seo,
            "content": self._audit_content_seo,
            "keywords": self._audit_keyword_seo,
            "performance": self._audit_performance_seo
        }
        
        # Keyword research tools
        self.keyword_tools = {
            "research": self._research_keywords,
            "analysis": self._analyze_keyword_difficulty,
            "clustering": self._cluster_keywords,
            "intent": self._analyze_search_intent
        }
        
        # SEO best practices database
        self.seo_best_practices = {
            "title_length": {"min": 30, "max": 60},
            "description_length": {"min": 120, "max": 160},
            "heading_structure": {"h1": 1, "h2": "3-5", "h3": "unlimited"},
            "keyword_density": {"min": 0.5, "max": 2.5},
            "internal_links": {"min": 2, "recommended": 5},
            "image_alt_text": {"required": True, "length": {"max": 125}},
            "page_speed": {"target": 3.0, "critical": 5.0}
        }
        
        # Platform-specific SEO requirements
        self.platform_seo_requirements = {
            "youtube": {
                "title_length": 100,
                "description_length": 5000,
                "tags_count": 15,
                "thumbnail_required": True,
                "closed_captions": True
            },
            "google": {
                "featured_snippets": True,
                "schema_markup": True,
                "mobile_friendly": True,
                "page_speed": True
            },
            "instagram": {
                "hashtags_count": 30,
                "alt_text": True,
                "caption_length": 2200,
                "location_tags": True
            },
            "tiktok": {
                "hashtags_count": 4,
                "caption_length": 150,
                "trending_sounds": True,
                "trending_hashtags": True
            }
        }
        
        # Performance metrics
        self.metrics = {
            "content_optimized": 0,
            "audits_performed": 0,
            "keywords_researched": 0,
            "average_seo_score": 0.0,
            "average_optimization_time": 0.0,
            "traffic_improvement": 0.0,
            "ranking_improvements": 0
        }
    
    async def optimize_content_seo(
        self,
        content_id: str,
        creator_id: str,
        content_data: Dict[str, Any],
        seo_goals: Optional[Dict[str, Any]] = None
    ) -> SEOResult:
        """
        Optimize content for search engines
        
        Args:
            content_id: Content identifier
            creator_id: Creator identifier
            content_data: Content data to optimize
            seo_goals: SEO optimization goals
            
        Returns:
            SEO optimization result
        """
        operation_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            goals = seo_goals or {}
            content_type = ContentType(content_data.get("content_type", "blog_post"))
            
            self.logger.info(f"Starting SEO optimization: {content_id} - Type: {content_type.value}")
            
            # Step 1: Perform SEO Audit
            audit = await self._perform_seo_audit(content_id, content_data, content_type)
            
            # Step 2: Research Keywords
            target_keywords = goals.get("target_keywords", [])
            if not target_keywords:
                target_keywords = await self._auto_research_keywords(content_data, creator_id)
            
            keyword_analysis = await self._analyze_keywords(target_keywords, content_data)
            
            # Step 3: Optimize Content
            content_optimizer = self.content_optimizers.get(content_type, self._optimize_generic_content_seo)
            content_improvements = await content_optimizer(content_data, keyword_analysis, goals)
            
            # Step 4: Technical SEO Improvements
            technical_improvements = await self._apply_technical_seo_improvements(
                content_data, content_type, goals
            )
            
            # Step 5: Performance Optimization
            performance_improvements = await self._optimize_seo_performance(
                content_data, audit, goals
            )
            
            # Step 6: Calculate Optimization Impact
            optimization_score = self._calculate_optimization_score(
                audit, content_improvements, technical_improvements
            )
            
            estimated_traffic_increase = self._estimate_traffic_increase(
                audit, optimization_score, keyword_analysis
            )
            
            # Step 7: Create Optimization Result
            optimization = SEOOptimization(
                optimization_id=str(uuid.uuid4()),
                content_id=content_id,
                creator_id=creator_id,
                strategies_applied=self._determine_applied_strategies(
                    content_improvements, technical_improvements
                ),
                keywords_optimized=keyword_analysis,
                technical_improvements=technical_improvements,
                content_improvements=content_improvements,
                performance_impact=performance_improvements,
                optimization_score=optimization_score,
                estimated_traffic_increase=estimated_traffic_increase
            )
            
            # Store optimization data
            self.seo_audits[content_id] = audit
            self.seo_optimizations[content_id] = optimization
            self.keyword_database[content_id] = keyword_analysis
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics["content_optimized"] += 1
            self.metrics["audits_performed"] += 1
            self.metrics["keywords_researched"] += len(keyword_analysis)
            self.metrics["average_seo_score"] = (
                (self.metrics["average_seo_score"] * (self.metrics["content_optimized"] - 1) + optimization_score) /
                self.metrics["content_optimized"]
            )
            self.metrics["average_optimization_time"] = (
                (self.metrics["average_optimization_time"] * (self.metrics["content_optimized"] - 1) + processing_time) /
                self.metrics["content_optimized"]
            )
            self.metrics["traffic_improvement"] += estimated_traffic_increase
            
            result = SEOResult(
                operation_id=operation_id,
                content_id=content_id,
                creator_id=creator_id,
                success=True,
                audit=audit,
                optimization=optimization,
                processing_time=processing_time
            )
            
            self.logger.info(f"SEO optimization completed: {content_id} in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            error_result = SEOResult(
                operation_id=operation_id,
                content_id=content_id,
                creator_id=creator_id,
                success=False,
                processing_time=processing_time,
                error_message=str(e)
            )
            
            self.logger.error(f"SEO optimization failed: {content_id} - {str(e)}")
            
            return error_result
    
    async def _perform_seo_audit(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        content_type: ContentType
    ) -> SEOAudit:
        """Perform comprehensive SEO audit"""
        audit_id = str(uuid.uuid4())
        
        # Run all audit engines
        technical_score = await self.audit_engines["technical"](content_data)
        content_score = await self.audit_engines["content"](content_data)
        keyword_score = await self.audit_engines["keywords"](content_data)
        performance_score = await self.audit_engines["performance"](content_data)
        
        # Calculate overall score
        overall_score = (technical_score + content_score + keyword_score + performance_score) / 4
        
        # Identify issues and recommendations
        issues = await self._identify_seo_issues(content_data, {
            "technical": technical_score,
            "content": content_score,
            "keywords": keyword_score,
            "performance": performance_score
        })
        
        recommendations = await self._generate_seo_recommendations(content_data, issues)
        
        return SEOAudit(
            audit_id=audit_id,
            content_id=content_id,
            content_type=content_type,
            overall_score=overall_score,
            technical_score=technical_score,
            content_score=content_score,
            keyword_score=keyword_score,
            performance_score=performance_score,
            issues=issues,
            recommendations=recommendations
        )
    
    async def _audit_technical_seo(self, content_data: Dict[str, Any]) -> float:
        """Audit technical SEO aspects"""
        score = 1.0
        penalties = 0.0
        
        # Check meta tags
        if not content_data.get("meta_title"):
            penalties += 0.2
        elif len(content_data.get("meta_title", "")) > self.seo_best_practices["title_length"]["max"]:
            penalties += 0.1
        
        if not content_data.get("meta_description"):
            penalties += 0.2
        elif len(content_data.get("meta_description", "")) > self.seo_best_practices["description_length"]["max"]:
            penalties += 0.1
        
        # Check URL structure
        url = content_data.get("url", "")
        if not self._is_seo_friendly_url(url):
            penalties += 0.1
        
        # Check heading structure
        if not self._has_proper_heading_structure(content_data):
            penalties += 0.15
        
        # Check schema markup
        if not content_data.get("schema_markup"):
            penalties += 0.1
        
        # Check mobile friendliness
        if not content_data.get("mobile_friendly", True):
            penalties += 0.2
        
        return max(0.0, score - penalties)
    
    async def _audit_content_seo(self, content_data: Dict[str, Any]) -> float:
        """Audit content SEO quality"""
        score = 1.0
        penalties = 0.0
        
        content = content_data.get("content", "")
        word_count = len(content.split())
        
        # Check content length
        if word_count < 300:
            penalties += 0.2
        elif word_count < 500:
            penalties += 0.1
        
        # Check readability
        readability_score = self._calculate_readability_score(content)
        if readability_score < 60:
            penalties += 0.15
        
        # Check internal links
        internal_links = len(content_data.get("internal_links", []))
        if internal_links < self.seo_best_practices["internal_links"]["min"]:
            penalties += 0.1
        
        # Check image optimization
        images = content_data.get("images", [])
        images_without_alt = [img for img in images if not img.get("alt_text")]
        if images_without_alt:
            penalties += 0.1 * (len(images_without_alt) / max(1, len(images)))
        
        return max(0.0, score - penalties)
    
    async def _audit_keyword_seo(self, content_data: Dict[str, Any]) -> float:
        """Audit keyword optimization"""
        score = 1.0
        penalties = 0.0
        
        content = content_data.get("content", "")
        title = content_data.get("meta_title", "")
        
        # Check if primary keyword is in title
        primary_keyword = content_data.get("primary_keyword", "")
        if primary_keyword and primary_keyword.lower() not in title.lower():
            penalties += 0.2
        
        # Check keyword density
        if primary_keyword:
            keyword_density = self._calculate_keyword_density(content, primary_keyword)
            optimal_density = self.seo_best_practices["keyword_density"]
            
            if keyword_density < optimal_density["min"] or keyword_density > optimal_density["max"]:
                penalties += 0.15
        
        # Check keyword in meta description
        meta_description = content_data.get("meta_description", "")
        if primary_keyword and primary_keyword.lower() not in meta_description.lower():
            penalties += 0.1
        
        # Check keyword in headings
        headings = content_data.get("headings", [])
        has_keyword_in_heading = any(
            primary_keyword.lower() in heading.lower() for heading in headings
        )
        if primary_keyword and not has_keyword_in_heading:
            penalties += 0.1
        
        return max(0.0, score - penalties)
    
    async def _audit_performance_seo(self, content_data: Dict[str, Any]) -> float:
        """Audit performance-related SEO factors"""
        score = 1.0
        penalties = 0.0
        
        # Check page speed
        page_speed = content_data.get("page_speed", 3.0)
        if page_speed > self.seo_best_practices["page_speed"]["critical"]:
            penalties += 0.3
        elif page_speed > self.seo_best_practices["page_speed"]["target"]:
            penalties += 0.15
        
        # Check image optimization
        images = content_data.get("images", [])
        large_images = [img for img in images if img.get("size", 0) > 500000]  # 500KB
        if large_images:
            penalties += 0.1 * (len(large_images) / max(1, len(images)))
        
        # Check HTTPS
        if not content_data.get("https", True):
            penalties += 0.2
        
        # Check core web vitals
        core_vitals = content_data.get("core_web_vitals", {})
        if core_vitals.get("lcp", 0) > 2.5:  # Largest Contentful Paint
            penalties += 0.1
        if core_vitals.get("fid", 0) > 100:  # First Input Delay
            penalties += 0.1
        if core_vitals.get("cls", 0) > 0.1:  # Cumulative Layout Shift
            penalties += 0.1
        
        return max(0.0, score - penalties)
    
    async def _auto_research_keywords(
        self,
        content_data: Dict[str, Any],
        creator_id: str
    ) -> List[str]:
        """Automatically research relevant keywords"""
        
        # Extract keywords from content
        content = content_data.get("content", "")
        title = content_data.get("title", "")
        
        # Use simple keyword extraction (in production, would use advanced NLP)
        words = re.findall(r'\b\w+\b', (title + " " + content).lower())
        word_freq = {}
        
        for word in words:
            if len(word) > 3:  # Ignore short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top words as potential keywords
        potential_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Generate keyword phrases
        keywords = []
        for word, freq in potential_keywords[:10]:
            keywords.append(word)
            
            # Add related phrases
            if freq > 2:
                keywords.append(f"{word} {creator_id.split('_')[0] if '_' in creator_id else 'tips'}")
                keywords.append(f"best {word}")
                keywords.append(f"how to {word}")
        
        return keywords[:20]  # Return top 20 keywords
    
    async def _analyze_keywords(
        self,
        keywords: List[str],
        content_data: Dict[str, Any]
    ) -> List[KeywordAnalysis]:
        """Analyze keywords for SEO potential"""
        
        keyword_analyses = []
        
        for keyword in keywords:
            analysis = KeywordAnalysis(
                keyword=keyword,
                search_volume=self._estimate_search_volume(keyword),
                competition_level=self._estimate_competition_level(keyword),
                difficulty_score=self._calculate_keyword_difficulty(keyword),
                relevance_score=self._calculate_relevance_score(keyword, content_data),
                opportunity_score=0.0,  # Will be calculated
                suggested_usage="secondary",
                related_keywords=self._generate_related_keywords(keyword)
            )
            
            # Calculate opportunity score
            analysis.opportunity_score = (
                (analysis.search_volume / 10000) * 0.3 +
                (1 - analysis.competition_level) * 0.3 +
                (1 - analysis.difficulty_score) * 0.2 +
                analysis.relevance_score * 0.2
            )
            
            # Determine suggested usage
            if analysis.opportunity_score > 0.8:
                analysis.suggested_usage = "primary"
            elif analysis.opportunity_score > 0.6:
                analysis.suggested_usage = "secondary"
            else:
                analysis.suggested_usage = "long_tail"
            
            keyword_analyses.append(analysis)
        
        # Sort by opportunity score
        keyword_analyses.sort(key=lambda x: x.opportunity_score, reverse=True)
        
        return keyword_analyses
    
    def _estimate_search_volume(self, keyword: str) -> int:
        """Estimate search volume for keyword"""
        # Simple estimation based on keyword characteristics
        base_volume = 1000
        
        # Longer keywords typically have lower volume
        length_factor = max(0.1, 1 - (len(keyword.split()) - 1) * 0.2)
        
        # Common words have higher volume
        common_words = ["how", "best", "top", "guide", "tips", "tutorial"]
        common_factor = 1.5 if any(word in keyword.lower() for word in common_words) else 1.0
        
        return int(base_volume * length_factor * common_factor)
    
    def _estimate_competition_level(self, keyword: str) -> float:
        """Estimate competition level for keyword (0-1)"""
        # Simple estimation
        word_count = len(keyword.split())
        
        # Shorter keywords typically have higher competition
        if word_count == 1:
            return 0.9
        elif word_count == 2:
            return 0.7
        elif word_count == 3:
            return 0.5
        else:
            return 0.3
    
    def _calculate_keyword_difficulty(self, keyword: str) -> float:
        """Calculate keyword ranking difficulty (0-1)"""
        # Simple calculation based on keyword characteristics
        competition = self._estimate_competition_level(keyword)
        commercial_intent = 0.5 if any(word in keyword.lower() for word in ["buy", "price", "cheap", "best"]) else 0.2
        
        return (competition * 0.7) + (commercial_intent * 0.3)
    
    def _calculate_relevance_score(self, keyword: str, content_data: Dict[str, Any]) -> float:
        """Calculate keyword relevance to content"""
        content = content_data.get("content", "").lower()
        title = content_data.get("title", "").lower()
        
        keyword_lower = keyword.lower()
        
        # Check presence in title and content
        title_match = 1.0 if keyword_lower in title else 0.0
        content_match = 1.0 if keyword_lower in content else 0.0
        
        # Check word overlap
        keyword_words = set(keyword_lower.split())
        content_words = set(content.split())
        overlap = len(keyword_words.intersection(content_words)) / len(keyword_words)
        
        return (title_match * 0.4) + (content_match * 0.3) + (overlap * 0.3)
    
    def _generate_related_keywords(self, keyword: str) -> List[str]:
        """Generate related keywords"""
        related = []
        
        # Add variations
        related.append(f"{keyword} guide")
        related.append(f"{keyword} tips")
        related.append(f"best {keyword}")
        related.append(f"how to {keyword}")
        related.append(f"{keyword} tutorial")
        
        return related[:5]
    
    # Content type specific optimizers
    
    async def _optimize_blog_post_seo(
        self,
        content_data: Dict[str, Any],
        keyword_analysis: List[KeywordAnalysis],
        goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize blog post for SEO"""
        
        primary_keyword = keyword_analysis[0] if keyword_analysis else None
        
        improvements = {
            "title_optimization": await self._optimize_title(content_data, primary_keyword),
            "meta_description_optimization": await self._optimize_meta_description(content_data, primary_keyword),
            "heading_optimization": await self._optimize_headings(content_data, keyword_analysis),
            "content_optimization": await self._optimize_content_body(content_data, keyword_analysis),
            "internal_linking": await self._optimize_internal_links(content_data),
            "image_optimization": await self._optimize_images(content_data),
            "schema_markup": await self._add_schema_markup(content_data, "Article")
        }
        
        return improvements
    
    async def _optimize_video_seo(
        self,
        content_data: Dict[str, Any],
        keyword_analysis: List[KeywordAnalysis],
        goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize video content for SEO"""
        
        primary_keyword = keyword_analysis[0] if keyword_analysis else None
        
        improvements = {
            "title_optimization": await self._optimize_video_title(content_data, primary_keyword),
            "description_optimization": await self._optimize_video_description(content_data, keyword_analysis),
            "tags_optimization": await self._optimize_video_tags(content_data, keyword_analysis),
            "thumbnail_optimization": await self._optimize_video_thumbnail(content_data),
            "captions_optimization": await self._optimize_video_captions(content_data, keyword_analysis),
            "chapters_optimization": await self._optimize_video_chapters(content_data, keyword_analysis),
            "schema_markup": await self._add_schema_markup(content_data, "VideoObject")
        }
        
        return improvements
    
    async def _optimize_audio_seo(
        self,
        content_data: Dict[str, Any],
        keyword_analysis: List[KeywordAnalysis],
        goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize audio content for SEO"""
        
        primary_keyword = keyword_analysis[0] if keyword_analysis else None
        
        improvements = {
            "title_optimization": await self._optimize_title(content_data, primary_keyword),
            "description_optimization": await self._optimize_audio_description(content_data, keyword_analysis),
            "transcript_optimization": await self._optimize_audio_transcript(content_data, keyword_analysis),
            "tags_optimization": await self._optimize_audio_tags(content_data, keyword_analysis),
            "episode_notes": await self._optimize_episode_notes(content_data, keyword_analysis),
            "schema_markup": await self._add_schema_markup(content_data, "PodcastEpisode")
        }
        
        return improvements
    
    async def _optimize_image_seo(
        self,
        content_data: Dict[str, Any],
        keyword_analysis: List[KeywordAnalysis],
        goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize image content for SEO"""
        
        primary_keyword = keyword_analysis[0] if keyword_analysis else None
        
        improvements = {
            "filename_optimization": await self._optimize_image_filename(content_data, primary_keyword),
            "alt_text_optimization": await self._optimize_image_alt_text(content_data, primary_keyword),
            "caption_optimization": await self._optimize_image_caption(content_data, keyword_analysis),
            "title_attribute": await self._optimize_image_title(content_data, primary_keyword),
            "surrounding_content": await self._optimize_surrounding_content(content_data, keyword_analysis),
            "schema_markup": await self._add_schema_markup(content_data, "ImageObject")
        }
        
        return improvements
    
    async def _optimize_social_post_seo(
        self,
        content_data: Dict[str, Any],
        keyword_analysis: List[KeywordAnalysis],
        goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize social media post for SEO"""
        
        improvements = {
            "hashtag_optimization": await self._optimize_hashtags(content_data, keyword_analysis),
            "caption_optimization": await self._optimize_social_caption(content_data, keyword_analysis),
            "mention_optimization": await self._optimize_mentions(content_data),
            "timing_optimization": await self._optimize_posting_time(content_data),
            "engagement_optimization": await self._optimize_engagement_factors(content_data)
        }
        
        return improvements
    
    async def _optimize_generic_content_seo(
        self,
        content_data: Dict[str, Any],
        keyword_analysis: List[KeywordAnalysis],
        goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generic SEO optimization"""
        
        primary_keyword = keyword_analysis[0] if keyword_analysis else None
        
        improvements = {
            "title_optimization": await self._optimize_title(content_data, primary_keyword),
            "description_optimization": await self._optimize_meta_description(content_data, primary_keyword),
            "content_optimization": await self._optimize_content_body(content_data, keyword_analysis),
            "basic_schema": await self._add_schema_markup(content_data, "WebPage")
        }
        
        return improvements
    
    # Helper optimization methods
    
    async def _optimize_title(self, content_data: Dict[str, Any], primary_keyword: Optional[KeywordAnalysis]) -> Dict[str, Any]:
        """Optimize title for SEO"""
        current_title = content_data.get("title", "")
        
        if not primary_keyword:
            return {"current": current_title, "optimized": current_title, "changes": []}
        
        keyword = primary_keyword.keyword
        
        # Generate optimized title
        if keyword.lower() not in current_title.lower():
            optimized_title = f"{keyword.title()}: {current_title}"
        else:
            optimized_title = current_title
        
        # Ensure title length is optimal
        max_length = self.seo_best_practices["title_length"]["max"]
        if len(optimized_title) > max_length:
            optimized_title = optimized_title[:max_length-3] + "..."
        
        changes = []
        if optimized_title != current_title:
            changes.append(f"Added primary keyword '{keyword}'")
            if len(optimized_title) != len(current_title):
                changes.append("Adjusted title length for SEO")
        
        return {
            "current": current_title,
            "optimized": optimized_title,
            "changes": changes,
            "keyword_included": keyword.lower() in optimized_title.lower()
        }
    
    async def _optimize_meta_description(self, content_data: Dict[str, Any], primary_keyword: Optional[KeywordAnalysis]) -> Dict[str, Any]:
        """Optimize meta description for SEO"""
        current_description = content_data.get("meta_description", "")
        
        if not primary_keyword:
            return {"current": current_description, "optimized": current_description, "changes": []}
        
        keyword = primary_keyword.keyword
        
        # Generate optimized description
        if not current_description:
            optimized_description = f"Discover everything about {keyword}. Professional insights and tips to help you succeed."
        elif keyword.lower() not in current_description.lower():
            optimized_description = f"{keyword.title()} - {current_description}"
        else:
            optimized_description = current_description
        
        # Ensure description length is optimal
        max_length = self.seo_best_practices["description_length"]["max"]
        if len(optimized_description) > max_length:
            optimized_description = optimized_description[:max_length-3] + "..."
        
        changes = []
        if optimized_description != current_description:
            changes.append(f"Added primary keyword '{keyword}'")
            changes.append("Optimized description length")
        
        return {
            "current": current_description,
            "optimized": optimized_description,
            "changes": changes,
            "keyword_included": keyword.lower() in optimized_description.lower()
        }
    
    def _calculate_keyword_density(self, content: str, keyword: str) -> float:
        """Calculate keyword density percentage"""
        if not content or not keyword:
            return 0.0
        
        words = content.lower().split()
        keyword_lower = keyword.lower()
        
        # Count exact matches and partial matches
        exact_matches = content.lower().count(keyword_lower)
        word_count = len(words)
        
        if word_count == 0:
            return 0.0
        
        return (exact_matches / word_count) * 100
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate content readability score (simplified Flesch score)"""
        if not content:
            return 0.0
        
        sentences = content.split('.')
        words = content.split()
        syllables = sum(self._count_syllables(word) for word in words)
        
        if len(sentences) == 0 or len(words) == 0:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        # Simplified Flesch Reading Ease formula
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        return max(0.0, min(100.0, score))
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllables = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllables += 1
            previous_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and syllables > 1:
            syllables -= 1
        
        return max(1, syllables)  # Every word has at least one syllable
    
    async def get_seo_analytics(self, creator_id: Optional[str] = None) -> Dict[str, Any]:
        """Get SEO analytics for creator or platform"""
        
        if creator_id:
            # Creator-specific analytics
            creator_optimizations = [
                opt for opt in self.seo_optimizations.values()
                if opt.creator_id == creator_id
            ]
            
            if not creator_optimizations:
                return {"message": "No SEO data available for this creator"}
            
            avg_score = sum(opt.optimization_score for opt in creator_optimizations) / len(creator_optimizations)
            total_traffic_increase = sum(opt.estimated_traffic_increase for opt in creator_optimizations)
            
            return {
                "creator_id": creator_id,
                "total_optimizations": len(creator_optimizations),
                "average_seo_score": avg_score,
                "total_estimated_traffic_increase": total_traffic_increase,
                "optimization_history": [
                    {
                        "content_id": opt.content_id,
                        "score": opt.optimization_score,
                        "traffic_increase": opt.estimated_traffic_increase,
                        "strategies": [s.value for s in opt.strategies_applied],
                        "date": opt.completion_timestamp.isoformat()
                    }
                    for opt in sorted(creator_optimizations, key=lambda x: x.completion_timestamp, reverse=True)[:10]
                ]
            }
        else:
            # Platform-wide analytics
            return {
                "platform_metrics": self.metrics,
                "seo_performance": {
                    "total_content_optimized": self.metrics["content_optimized"],
                    "average_seo_score": self.metrics["average_seo_score"],
                    "total_traffic_improvement": self.metrics["traffic_improvement"],
                    "optimization_efficiency": "high"
                },
                "keyword_insights": {
                    "total_keywords_researched": self.metrics["keywords_researched"],
                    "keyword_database_size": len(self.keyword_database),
                    "trending_keywords": self._get_trending_keywords()
                },
                "optimization_trends": {
                    "most_optimized_content_types": self._get_content_type_distribution(),
                    "popular_seo_strategies": self._get_strategy_distribution(),
                    "improvement_areas": self._identify_improvement_areas()
                }
            }
    
    def _get_trending_keywords(self) -> List[str]:
        """Get trending keywords from optimization data"""
        all_keywords = []
        for keywords in self.keyword_database.values():
            all_keywords.extend([k.keyword for k in keywords if k.opportunity_score > 0.7])
        
        # Count frequency
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        # Return top trending keywords
        trending = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, freq in trending[:10]]
    
    def _get_content_type_distribution(self) -> Dict[str, int]:
        """Get distribution of optimized content types"""
        type_counts = {}
        for audit in self.seo_audits.values():
            content_type = audit.content_type.value
            type_counts[content_type] = type_counts.get(content_type, 0) + 1
        
        return type_counts
    
    def _get_strategy_distribution(self) -> Dict[str, int]:
        """Get distribution of applied SEO strategies"""
        strategy_counts = {}
        for optimization in self.seo_optimizations.values():
            for strategy in optimization.strategies_applied:
                strategy_name = strategy.value
                strategy_counts[strategy_name] = strategy_counts.get(strategy_name, 0) + 1
        
        return strategy_counts