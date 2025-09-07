"""Mobile Metadata Optimization Engine

Advanced mobile metadata optimization system for enhancing content discoverability
and engagement across mobile platforms with AI-powered metadata generation,
SEO optimization, and mobile-specific metadata formatting.

Business Logic Integration: Mobile Content → IA Processing → Protection → SEO → Metadata Optimization → Distribution

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
import time
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid


logger = logging.getLogger(__name__)


class MobileMetadataType(Enum):
    """Mobile metadata types for optimization"""
    TITLE = "title"
    DESCRIPTION = "description"
    TAGS = "tags"
    KEYWORDS = "keywords"
    HASHTAGS = "hashtags"
    CAPTIONS = "captions"
    SCHEMA_MARKUP = "schema_markup"
    OG_TAGS = "og_tags"
    TWITTER_CARDS = "twitter_cards"
    MOBILE_APP_TAGS = "mobile_app_tags"


class MetadataOptimizationStrategy(Enum):
    """Metadata optimization strategies for mobile"""
    SEO_FOCUSED = "seo_focused"
    ENGAGEMENT_MAXIMIZED = "engagement_maximized"
    ACCESSIBILITY_ENHANCED = "accessibility_enhanced"
    PLATFORM_OPTIMIZED = "platform_optimized"
    VIRAL_POTENTIAL = "viral_potential"
    CONVERSION_ORIENTED = "conversion_oriented"


class MobileMetadataFormat(Enum):
    """Mobile metadata formats"""
    JSON_LD = "json_ld"
    MICRODATA = "microdata"
    RDF = "rdf"
    OG_PROTOCOL = "og_protocol"
    TWITTER_CARDS = "twitter_cards"
    MOBILE_APP_TAGS = "mobile_app_tags"
    AMP_METADATA = "amp_metadata"


@dataclass
class MobileMetadataConfiguration:
    """Mobile metadata optimization configuration"""
    optimization_strategy: MetadataOptimizationStrategy
    metadata_types: List[MobileMetadataType]
    output_formats: List[MobileMetadataFormat]
    target_platforms: List[str]
    mobile_device_types: List[str]
    language_codes: List[str] = None
    seo_optimization: bool = True
    accessibility_optimization: bool = True
    schema_markup_generation: bool = True
    mobile_app_optimization: bool = True
    social_media_optimization: bool = True
    local_seo_optimization: bool = True
    voice_search_optimization: bool = True
    amp_optimization: bool = True
    pwa_optimization: bool = True
    max_title_length: int = 60
    max_description_length: int = 160
    max_keywords_count: int = 10
    max_hashtags_count: int = 30
    
    def __post_init__(self):
        if self.language_codes is None:
            self.language_codes = ["en"]


@dataclass
class MobileMetadataRequest:
    """Mobile metadata optimization request"""
    request_id: str
    content_id: str
    content_type: str
    content_title: str
    content_description: str
    content_url: str
    creator_id: str
    creator_type: str
    content_category: str
    original_metadata: Dict[str, Any]
    mobile_config: MobileMetadataConfiguration
    target_audience: Dict[str, Any] = None
    geographic_targeting: List[str] = None
    publish_date: Optional[datetime] = None
    priority: str = "normal"
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())
        if self.target_audience is None:
            self.target_audience = {}
        if self.geographic_targeting is None:
            self.geographic_targeting = []
        if self.publish_date is None:
            self.publish_date = datetime.utcnow()


@dataclass
class OptimizedMetadata:
    """Optimized metadata for mobile platforms"""
    metadata_type: MobileMetadataType
    optimized_content: str
    original_content: str
    optimization_score: float
    mobile_optimizations: List[str]
    seo_keywords: List[str]
    readability_score: float
    engagement_potential: float


@dataclass
class MobileMetadataResult:
    """Mobile metadata optimization result"""
    request_id: str
    success: bool
    processing_time_ms: int
    battery_usage_percent: float
    network_usage_mb: float
    optimization_score: float
    optimized_metadata: Dict[MobileMetadataType, OptimizedMetadata]
    schema_markup: Dict[str, Any]
    og_tags: Dict[str, str]
    twitter_cards: Dict[str, str]
    mobile_app_tags: Dict[str, str]
    amp_metadata: Dict[str, Any]
    seo_insights: Dict[str, Any]
    accessibility_enhancements: List[str]
    mobile_optimizations: List[str]
    platform_specific_metadata: Dict[str, Dict[str, Any]]
    analytics_data: Dict[str, Any]
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class MobileMetadataOptimizer:
    """Mobile Metadata Optimization Engine
    
    Advanced mobile metadata optimization system for enhancing content discoverability
    and engagement across mobile platforms.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Mobile optimization settings
        self.mobile_optimizations = {
            "battery_aware": self.config.get("enable_battery_optimization", True),
            "network_adaptive": self.config.get("enable_network_adaptation", True),
            "offline_capable": self.config.get("enable_offline_metadata", True),
            "real_time": self.config.get("enable_real_time_optimization", True),
            "cache_enabled": self.config.get("enable_metadata_cache", True)
        }
        
        # Metadata processing engines - placeholders for future integration
        self.seo_analyzer = None        # SEOAnalyzer()
        self.keyword_extractor = None   # KeywordExtractor()
        self.readability_analyzer = None # ReadabilityAnalyzer()
        self.sentiment_analyzer = None   # SentimentAnalyzer()
        self.schema_generator = None     # SchemaGenerator()
        
        # Mobile-specific analyzers
        self.mobile_seo_analyzer = None     # MobileSEOAnalyzer()
        self.accessibility_checker = None   # AccessibilityChecker()
        self.voice_search_optimizer = None  # VoiceSearchOptimizer()
        
        # Performance tracking
        self.optimization_metrics = {
            "total_requests": 0,
            "successful_optimizations": 0,
            "cache_hits": 0,
            "average_optimization_score": 0.0,
            "battery_optimizations": 0,
            "network_adaptations": 0,
            "average_processing_time": 0.0
        }
        
        self.logger.info("Mobile Metadata Optimizer initialized")
    
    async def optimize_metadata(self, request: MobileMetadataRequest) -> MobileMetadataResult:
        """
        Main entry point for mobile metadata optimization.
        
        Args:
            request: Mobile metadata optimization request
            
        Returns:
            MobileMetadataResult: Comprehensive metadata optimization results
        """
        start_time = time.time()
        self.optimization_metrics["total_requests"] += 1
        
        self.logger.info(f"Starting mobile metadata optimization for content {request.content_id}")
        
        try:
            # Initialize result
            result = MobileMetadataResult(
                request_id=request.request_id,
                success=False,
                processing_time_ms=0,
                battery_usage_percent=0.0,
                network_usage_mb=0.0,
                optimization_score=0.0,
                optimized_metadata={},
                schema_markup={},
                og_tags={},
                twitter_cards={},
                mobile_app_tags={},
                amp_metadata={},
                seo_insights={},
                accessibility_enhancements=[],
                mobile_optimizations=[],
                platform_specific_metadata={},
                analytics_data={}
            )
            
            # Validate request
            validation_errors = await self._validate_metadata_request(request)
            if validation_errors:
                result.error_message = "; ".join(validation_errors)
                self.logger.error(f"Metadata optimization request validation failed: {result.error_message}")
                return result
            
            # Apply mobile-specific optimizations
            await self._apply_mobile_optimizations(request, result)
            
            # Core metadata optimization pipeline
            await self._optimize_title(request, result)
            await self._optimize_description(request, result)
            await self._optimize_keywords(request, result)
            await self._optimize_hashtags(request, result)
            await self._generate_schema_markup(request, result)
            await self._generate_og_tags(request, result)
            await self._generate_twitter_cards(request, result)
            await self._generate_mobile_app_tags(request, result)
            await self._generate_amp_metadata(request, result)
            await self._apply_seo_optimizations(request, result)
            await self._apply_accessibility_enhancements(request, result)
            await self._generate_platform_specific_metadata(request, result)
            
            # Calculate optimization scores
            await self._calculate_optimization_scores(request, result)
            
            # Generate analytics data
            await self._generate_analytics_data(request, result)
            
            result.success = True
            self.optimization_metrics["successful_optimizations"] += 1
            
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = int(processing_time)
            self.optimization_metrics["average_processing_time"] = (
                (self.optimization_metrics["average_processing_time"] * (self.optimization_metrics["total_requests"] - 1) + 
                 processing_time) / self.optimization_metrics["total_requests"]
            )
            
            self.logger.info(f"Mobile metadata optimization completed for {request.content_id} in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            self.logger.error(f"Mobile metadata optimization failed: {str(e)}")
            return MobileMetadataResult(
                request_id=request.request_id,
                success=False,
                processing_time_ms=int((time.time() - start_time) * 1000),
                battery_usage_percent=0.0,
                network_usage_mb=0.0,
                optimization_score=0.0,
                optimized_metadata={},
                schema_markup={},
                og_tags={},
                twitter_cards={},
                mobile_app_tags={},
                amp_metadata={},
                seo_insights={},
                accessibility_enhancements=[],
                mobile_optimizations=[],
                platform_specific_metadata={},
                analytics_data={},
                error_message=str(e)
            )
    
    async def _validate_metadata_request(self, request: MobileMetadataRequest) -> List[str]:
        """Validate mobile metadata optimization request."""
        errors = []
        
        if not request.content_title.strip():
            errors.append("Content title is required")
        
        if not request.content_description.strip():
            errors.append("Content description is required")
        
        if not request.content_url:
            errors.append("Content URL is required")
        
        if not request.mobile_config.metadata_types:
            errors.append("At least one metadata type is required")
        
        return errors
    
    async def _apply_mobile_optimizations(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Apply mobile-specific optimizations."""
        self.logger.debug(f"Applying mobile optimizations for {request.content_id}")
        
        optimizations = []
        
        # Battery optimization
        if self.mobile_optimizations["battery_aware"]:
            optimizations.extend([
                "battery_efficient_processing",
                "cached_metadata_lookups",
                "optimized_regex_patterns"
            ])
            result.battery_usage_percent = 0.1
            self.optimization_metrics["battery_optimizations"] += 1
        
        # Network optimization
        if self.mobile_optimizations["network_adaptive"]:
            optimizations.extend([
                "compressed_metadata_transfer",
                "adaptive_quality_metadata",
                "minimal_network_requests"
            ])
            result.network_usage_mb = 0.2
            self.optimization_metrics["network_adaptations"] += 1
        
        result.mobile_optimizations = optimizations
        
        self.logger.debug(f"Applied {len(optimizations)} mobile optimizations")
    
    async def _optimize_title(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Optimize title for mobile platforms."""
        self.logger.debug(f"Optimizing title for {request.content_id}")
        
        original_title = request.content_title
        optimized_title = original_title.strip()
        
        # Mobile title optimizations
        mobile_optimizations = []
        seo_keywords = []
        
        # Length optimization for mobile
        max_length = request.mobile_config.max_title_length
        if len(optimized_title) > max_length:
            optimized_title = optimized_title[:max_length-3] + "..."
            mobile_optimizations.append("mobile_length_optimization")
        
        # Add creator type context
        if request.creator_type and request.creator_type not in optimized_title.lower():
            if len(optimized_title) + len(request.creator_type) + 3 <= max_length:
                optimized_title = f"{optimized_title} | {request.creator_type.title()}"
                mobile_optimizations.append("creator_context_addition")
        
        # Extract SEO keywords
        words = re.findall(r'\b\w+\b', optimized_title.lower())
        seo_keywords = [word for word in words if len(word) > 3][:5]
        
        # Calculate optimization scores
        optimization_score = min(100.0, len(seo_keywords) * 15 + (70 if len(optimized_title) <= max_length else 40))
        readability_score = 100.0 - abs(len(optimized_title) - 45) * 2  # Optimal around 45 chars
        engagement_potential = min(95.0, len(seo_keywords) * 18 + (80 if "mobile" in optimized_title.lower() else 60))
        
        # Create optimized metadata object
        optimized_metadata = OptimizedMetadata(
            metadata_type=MobileMetadataType.TITLE,
            optimized_content=optimized_title,
            original_content=original_title,
            optimization_score=optimization_score,
            mobile_optimizations=mobile_optimizations,
            seo_keywords=seo_keywords,
            readability_score=readability_score,
            engagement_potential=engagement_potential
        )
        
        result.optimized_metadata[MobileMetadataType.TITLE] = optimized_metadata
        
        self.logger.debug(f"Title optimization completed with score: {optimization_score:.1f}")
    
    async def _optimize_description(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Optimize description for mobile platforms."""
        self.logger.debug(f"Optimizing description for {request.content_id}")
        
        original_description = request.content_description
        optimized_description = original_description.strip()
        
        mobile_optimizations = []
        seo_keywords = []
        
        # Length optimization for mobile
        max_length = request.mobile_config.max_description_length
        if len(optimized_description) > max_length:
            # Smart truncation at sentence boundary
            sentences = optimized_description.split('. ')
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence + ". ") <= max_length - 3:
                    truncated += sentence + ". "
                else:
                    break
            optimized_description = truncated.rstrip(". ") + "..."
            mobile_optimizations.append("smart_truncation")
        
        # Add mobile call-to-action
        cta_phrases = {
            "musician": "Listen now on mobile!",
            "blogger": "Read more on your mobile device!",
            "photographer": "View gallery on mobile!",
            "influencer": "Follow for mobile updates!",
            "comedian": "Watch comedy on mobile!"
        }
        
        cta = cta_phrases.get(request.creator_type, "Discover on mobile!")
        if cta.lower() not in optimized_description.lower() and len(optimized_description) + len(cta) + 1 <= max_length:
            optimized_description += " " + cta
            mobile_optimizations.append("mobile_cta_addition")
        
        # Extract SEO keywords
        words = re.findall(r'\b\w+\b', optimized_description.lower())
        seo_keywords = [word for word in words if len(word) > 3 and word.isalpha()][:8]
        
        # Calculate optimization scores
        optimization_score = min(100.0, len(seo_keywords) * 10 + (80 if len(optimized_description) <= max_length else 50))
        readability_score = 100.0 - abs(len(optimized_description) - 120) * 1.5  # Optimal around 120 chars
        engagement_potential = min(95.0, len(seo_keywords) * 12 + (85 if any(cta_word in optimized_description.lower() for cta_word in ["now", "discover", "watch", "listen"]) else 65))
        
        # Create optimized metadata object
        optimized_metadata = OptimizedMetadata(
            metadata_type=MobileMetadataType.DESCRIPTION,
            optimized_content=optimized_description,
            original_content=original_description,
            optimization_score=optimization_score,
            mobile_optimizations=mobile_optimizations,
            seo_keywords=seo_keywords,
            readability_score=readability_score,
            engagement_potential=engagement_potential
        )
        
        result.optimized_metadata[MobileMetadataType.DESCRIPTION] = optimized_metadata
        
        self.logger.debug(f"Description optimization completed with score: {optimization_score:.1f}")
    
    async def _optimize_keywords(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Optimize keywords for mobile SEO."""
        self.logger.debug(f"Optimizing keywords for {request.content_id}")
        
        # Extract base keywords from title and description
        text_content = f"{request.content_title} {request.content_description}".lower()
        words = re.findall(r'\b\w+\b', text_content)
        
        # Filter and rank keywords
        keyword_candidates = [word for word in words if len(word) > 3 and word.isalpha()]
        keyword_frequency = {}
        for word in keyword_candidates:
            keyword_frequency[word] = keyword_frequency.get(word, 0) + 1
        
        # Sort by frequency and select top keywords
        sorted_keywords = sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)
        base_keywords = [kw[0] for kw in sorted_keywords[:5]]
        
        # Add mobile-specific keywords
        mobile_keywords = ["mobile", "app", "smartphone", "tablet"]
        
        # Add creator-type specific keywords
        creator_keywords = {
            "musician": ["music", "audio", "song", "artist", "streaming"],
            "blogger": ["blog", "article", "content", "writing", "read"],
            "photographer": ["photo", "image", "photography", "visual", "gallery"],
            "influencer": ["social", "influence", "lifestyle", "community", "follow"],
            "comedian": ["comedy", "funny", "humor", "entertainment", "laugh"]
        }
        
        type_keywords = creator_keywords.get(request.creator_type, [])
        
        # Add content category keywords
        category_keywords = []
        if request.content_category:
            category_keywords = [request.content_category.lower(), f"{request.content_category.lower()}_content"]
        
        # Combine and optimize keywords
        all_keywords = base_keywords + mobile_keywords + type_keywords + category_keywords
        unique_keywords = list(set(all_keywords))[:request.mobile_config.max_keywords_count]
        
        mobile_optimizations = [
            "mobile_keyword_integration",
            "creator_specific_keywords",
            "category_based_keywords",
            "frequency_based_ranking"
        ]
        
        # Calculate optimization scores
        optimization_score = min(100.0, len(unique_keywords) * 8 + (90 if "mobile" in unique_keywords else 70))
        readability_score = 95.0  # Keywords are inherently readable
        engagement_potential = min(95.0, len(unique_keywords) * 9 + (85 if request.creator_type in str(unique_keywords) else 65))
        
        # Create optimized metadata object
        optimized_metadata = OptimizedMetadata(
            metadata_type=MobileMetadataType.KEYWORDS,
            optimized_content=", ".join(unique_keywords),
            original_content=", ".join(base_keywords),
            optimization_score=optimization_score,
            mobile_optimizations=mobile_optimizations,
            seo_keywords=unique_keywords,
            readability_score=readability_score,
            engagement_potential=engagement_potential
        )
        
        result.optimized_metadata[MobileMetadataType.KEYWORDS] = optimized_metadata
        
        self.logger.debug(f"Keywords optimization completed with {len(unique_keywords)} keywords")
    
    async def _optimize_hashtags(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Optimize hashtags for mobile social platforms."""
        self.logger.debug(f"Optimizing hashtags for {request.content_id}")
        
        # Base hashtags from keywords
        keywords_metadata = result.optimized_metadata.get(MobileMetadataType.KEYWORDS)
        base_tags = keywords_metadata.seo_keywords if keywords_metadata else []
        
        # Convert to hashtags
        hashtags = [f"#{tag}" for tag in base_tags if not tag.startswith('#')]
        
        # Add mobile-specific hashtags
        mobile_hashtags = ["#mobile", "#mobileapp", "#smartphone", "#mobilecontent"]
        
        # Add platform-specific hashtags based on target platforms
        platform_hashtags = []
        for platform in request.mobile_config.target_platforms:
            if "instagram" in platform.lower():
                platform_hashtags.extend(["#instagram", "#insta", "#mobilegram"])
            elif "tiktok" in platform.lower():
                platform_hashtags.extend(["#tiktok", "#tiktokmobile", "#viral"])
            elif "youtube" in platform.lower():
                platform_hashtags.extend(["#youtube", "#youtubemobile", "#video"])
            elif "twitter" in platform.lower():
                platform_hashtags.extend(["#twitter", "#tweet", "#mobilesocial"])
        
        # Add creator-type hashtags
        creator_hashtags = {
            "musician": ["#music", "#musician", "#audio", "#song", "#artist"],
            "blogger": ["#blog", "#blogger", "#content", "#writing", "#article"],
            "photographer": ["#photography", "#photographer", "#photo", "#visual", "#gallery"],
            "influencer": ["#influencer", "#social", "#lifestyle", "#community", "#influence"],
            "comedian": ["#comedy", "#comedian", "#funny", "#humor", "#entertainment"]
        }
        
        type_hashtags = creator_hashtags.get(request.creator_type, [])
        
        # Combine and optimize
        all_hashtags = hashtags + mobile_hashtags + platform_hashtags + type_hashtags
        unique_hashtags = list(set(all_hashtags))[:request.mobile_config.max_hashtags_count]
        
        mobile_optimizations = [
            "mobile_hashtag_generation",
            "platform_specific_hashtags",
            "creator_type_hashtags",
            "engagement_optimized_hashtags"
        ]
        
        # Calculate optimization scores
        optimization_score = min(100.0, len(unique_hashtags) * 3 + (90 if "#mobile" in unique_hashtags else 70))
        readability_score = 90.0  # Hashtags are generally readable
        engagement_potential = min(95.0, len(unique_hashtags) * 3.5 + (85 if any("#viral" in tag or "#trending" in tag for tag in unique_hashtags) else 65))
        
        # Create optimized metadata object
        optimized_metadata = OptimizedMetadata(
            metadata_type=MobileMetadataType.HASHTAGS,
            optimized_content=" ".join(unique_hashtags),
            original_content=" ".join(hashtags),
            optimization_score=optimization_score,
            mobile_optimizations=mobile_optimizations,
            seo_keywords=[tag.replace("#", "") for tag in unique_hashtags],
            readability_score=readability_score,
            engagement_potential=engagement_potential
        )
        
        result.optimized_metadata[MobileMetadataType.HASHTAGS] = optimized_metadata
        
        self.logger.debug(f"Hashtags optimization completed with {len(unique_hashtags)} hashtags")
    
    async def _generate_schema_markup(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Generate schema markup for mobile optimization."""
        self.logger.debug(f"Generating schema markup for {request.content_id}")
        
        if not request.mobile_config.schema_markup_generation:
            return
        
        # Base schema structure
        schema = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": result.optimized_metadata.get(MobileMetadataType.TITLE, {}).optimized_content or request.content_title,
            "description": result.optimized_metadata.get(MobileMetadataType.DESCRIPTION, {}).optimized_content or request.content_description,
            "url": request.content_url,
            "creator": {
                "@type": "Person",
                "name": f"Creator {request.creator_id}",
                "creatorType": request.creator_type
            },
            "dateCreated": request.publish_date.isoformat(),
            "dateModified": datetime.utcnow().isoformat(),
            "keywords": result.optimized_metadata.get(MobileMetadataType.KEYWORDS, {}).seo_keywords or [],
            "inLanguage": request.mobile_config.language_codes[0] if request.mobile_config.language_codes else "en",
            "mobileOptimized": True,
            "accessibilityFeature": ["alternativeText", "captions", "transcript"],
            "audience": {
                "@type": "Audience",
                "audienceType": "mobile users"
            }
        }
        
        # Content-type specific schema
        if request.content_type == "video":
            schema.update({
                "@type": "VideoObject",
                "encodingFormat": "video/mp4",
                "embedUrl": f"{request.content_url}/embed",
                "uploadDate": request.publish_date.isoformat(),
                "thumbnailUrl": f"{request.content_url}/thumbnail.jpg"
            })
        elif request.content_type == "audio":
            schema.update({
                "@type": "AudioObject",
                "encodingFormat": "audio/mpeg",
                "duration": "PT5M",  # Placeholder duration
                "contentUrl": request.content_url
            })
        elif request.content_type == "image":
            schema.update({
                "@type": "ImageObject",
                "encodingFormat": "image/jpeg",
                "contentUrl": request.content_url,
                "width": "1200",
                "height": "630"
            })
        elif request.content_type == "text":
            schema.update({
                "@type": "Article",
                "articleBody": request.content_description,
                "wordCount": len(request.content_description.split())
            })
        
        # Mobile-specific enhancements
        schema["mobileCompatible"] = True
        schema["mobileFriendly"] = True
        
        # Add geographic data if available
        if request.geographic_targeting:
            schema["locationCreated"] = {
                "@type": "Place",
                "name": request.geographic_targeting[0]
            }
        
        result.schema_markup = schema
        result.mobile_optimizations.append("schema_markup_generation")
        
        self.logger.debug("Schema markup generation completed")
    
    async def _generate_og_tags(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Generate Open Graph tags for mobile sharing."""
        self.logger.debug(f"Generating OG tags for {request.content_id}")
        
        og_tags = {
            "og:title": result.optimized_metadata.get(MobileMetadataType.TITLE, {}).optimized_content or request.content_title,
            "og:description": result.optimized_metadata.get(MobileMetadataType.DESCRIPTION, {}).optimized_content or request.content_description,
            "og:url": request.content_url,
            "og:type": self._get_og_type(request.content_type),
            "og:image": f"{request.content_url}/og-image.jpg",
            "og:image:width": "1200",
            "og:image:height": "630",
            "og:site_name": "Ainflue Mobile",
            "og:locale": request.mobile_config.language_codes[0] if request.mobile_config.language_codes else "en_US"
        }
        
        # Content-type specific OG tags
        if request.content_type == "video":
            og_tags.update({
                "og:video": request.content_url,
                "og:video:type": "video/mp4",
                "og:video:width": "1280",
                "og:video:height": "720"
            })
        elif request.content_type == "audio":
            og_tags.update({
                "og:audio": request.content_url,
                "og:audio:type": "audio/mpeg"
            })
        
        # Mobile-specific OG tags
        og_tags["og:mobile_optimized"] = "true"
        
        result.og_tags = og_tags
        result.mobile_optimizations.append("og_tags_generation")
        
        self.logger.debug("OG tags generation completed")
    
    async def _generate_twitter_cards(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Generate Twitter Cards metadata for mobile sharing."""
        self.logger.debug(f"Generating Twitter Cards for {request.content_id}")
        
        # Determine card type based on content
        card_type = "summary_large_image"
        if request.content_type == "video":
            card_type = "player"
        elif request.content_type == "audio":
            card_type = "player"
        
        twitter_cards = {
            "twitter:card": card_type,
            "twitter:title": result.optimized_metadata.get(MobileMetadataType.TITLE, {}).optimized_content or request.content_title,
            "twitter:description": result.optimized_metadata.get(MobileMetadataType.DESCRIPTION, {}).optimized_content or request.content_description,
            "twitter:image": f"{request.content_url}/twitter-image.jpg",
            "twitter:image:alt": f"Mobile content by {request.creator_type}",
            "twitter:site": "@ainflue_mobile",
            "twitter:creator": f"@creator_{request.creator_id}"
        }
        
        # Player card specific tags
        if card_type == "player":
            twitter_cards.update({
                "twitter:player": f"{request.content_url}/player",
                "twitter:player:width": "1280",
                "twitter:player:height": "720",
                "twitter:player:stream": request.content_url
            })
        
        result.twitter_cards = twitter_cards
        result.mobile_optimizations.append("twitter_cards_generation")
        
        self.logger.debug("Twitter Cards generation completed")
    
    async def _generate_mobile_app_tags(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Generate mobile app-specific tags."""
        self.logger.debug(f"Generating mobile app tags for {request.content_id}")
        
        if not request.mobile_config.mobile_app_optimization:
            return
        
        mobile_app_tags = {
            "apple-mobile-web-app-capable": "yes",
            "apple-mobile-web-app-status-bar-style": "default",
            "apple-mobile-web-app-title": result.optimized_metadata.get(MobileMetadataType.TITLE, {}).optimized_content or request.content_title,
            "mobile-web-app-capable": "yes",
            "application-name": "Ainflue Mobile",
            "msapplication-TileColor": "#000000",
            "theme-color": "#000000",
            "viewport": "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"
        }
        
        # iOS app store links
        if any("ios" in device.lower() for device in request.mobile_config.mobile_device_types):
            mobile_app_tags.update({
                "apple-itunes-app": "app-id=123456789",
                "apple-touch-icon": f"{request.content_url}/apple-touch-icon.png"
            })
        
        # Android app store links
        if any("android" in device.lower() for device in request.mobile_config.mobile_device_types):
            mobile_app_tags.update({
                "google-play-app": "app-id=com.ainflue.mobile",
                "android-app": "com.ainflue.mobile"
            })
        
        result.mobile_app_tags = mobile_app_tags
        result.mobile_optimizations.append("mobile_app_tags_generation")
        
        self.logger.debug("Mobile app tags generation completed")
    
    async def _generate_amp_metadata(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Generate AMP (Accelerated Mobile Pages) metadata."""
        self.logger.debug(f"Generating AMP metadata for {request.content_id}")
        
        if not request.mobile_config.amp_optimization:
            return
        
        amp_metadata = {
            "amp-version": "1.0",
            "amp-boilerplate": True,
            "amp-custom": True,
            "canonical": request.content_url,
            "amp-url": f"{request.content_url}/amp",
            "structured-data": result.schema_markup
        }
        
        # Content-specific AMP components
        if request.content_type == "video":
            amp_metadata["amp-components"] = ["amp-video", "amp-youtube"]
        elif request.content_type == "audio":
            amp_metadata["amp-components"] = ["amp-audio", "amp-soundcloud"]
        elif request.content_type == "image":
            amp_metadata["amp-components"] = ["amp-img", "amp-carousel"]
        
        result.amp_metadata = amp_metadata
        result.mobile_optimizations.append("amp_metadata_generation")
        
        self.logger.debug("AMP metadata generation completed")
    
    async def _apply_seo_optimizations(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Apply SEO optimizations for mobile search."""
        self.logger.debug(f"Applying SEO optimizations for {request.content_id}")
        
        seo_insights = {
            "title_seo_score": 0.0,
            "description_seo_score": 0.0,
            "keywords_density": 0.0,
            "mobile_friendliness": 100.0,
            "structured_data_score": 90.0 if result.schema_markup else 0.0,
            "social_sharing_score": 85.0 if result.og_tags else 0.0,
            "recommendations": []
        }
        
        # Calculate title SEO score
        title_metadata = result.optimized_metadata.get(MobileMetadataType.TITLE)
        if title_metadata:
            seo_insights["title_seo_score"] = title_metadata.optimization_score
            if title_metadata.optimization_score < 70:
                seo_insights["recommendations"].append("Optimize title for better mobile SEO")
        
        # Calculate description SEO score
        desc_metadata = result.optimized_metadata.get(MobileMetadataType.DESCRIPTION)
        if desc_metadata:
            seo_insights["description_seo_score"] = desc_metadata.optimization_score
            if desc_metadata.optimization_score < 70:
                seo_insights["recommendations"].append("Improve description for mobile search")
        
        # Calculate keyword density
        keywords_metadata = result.optimized_metadata.get(MobileMetadataType.KEYWORDS)
        if keywords_metadata:
            keyword_count = len(keywords_metadata.seo_keywords)
            total_words = len(f"{request.content_title} {request.content_description}".split())
            seo_insights["keywords_density"] = (keyword_count / total_words) * 100 if total_words > 0 else 0
        
        # Mobile-specific SEO recommendations
        if request.mobile_config.voice_search_optimization:
            seo_insights["recommendations"].append("Content optimized for voice search queries")
        
        if request.mobile_config.local_seo_optimization and request.geographic_targeting:
            seo_insights["recommendations"].append("Local SEO optimization applied")
        
        result.seo_insights = seo_insights
        result.mobile_optimizations.append("seo_optimization")
        
        self.logger.debug("SEO optimizations applied")
    
    async def _apply_accessibility_enhancements(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Apply accessibility enhancements for mobile users."""
        self.logger.debug(f"Applying accessibility enhancements for {request.content_id}")
        
        if not request.mobile_config.accessibility_optimization:
            return
        
        accessibility_enhancements = [
            "alt_text_optimization",
            "aria_label_generation",
            "screen_reader_compatibility",
            "high_contrast_support",
            "keyboard_navigation_support",
            "voice_control_compatibility"
        ]
        
        # Content-specific accessibility features
        if request.content_type == "video":
            accessibility_enhancements.extend([
                "video_captions_support",
                "audio_descriptions",
                "sign_language_interpretation"
            ])
        elif request.content_type == "audio":
            accessibility_enhancements.extend([
                "audio_transcription",
                "visual_audio_indicators",
                "subtitle_support"
            ])
        elif request.content_type == "image":
            accessibility_enhancements.extend([
                "descriptive_alt_text",
                "image_descriptions",
                "visual_impairment_support"
            ])
        
        result.accessibility_enhancements = accessibility_enhancements
        result.mobile_optimizations.append("accessibility_enhancement")
        
        self.logger.debug(f"Applied {len(accessibility_enhancements)} accessibility enhancements")
    
    async def _generate_platform_specific_metadata(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Generate platform-specific metadata."""
        self.logger.debug(f"Generating platform-specific metadata for {request.content_id}")
        
        platform_metadata = {}
        
        for platform in request.mobile_config.target_platforms:
            if "youtube" in platform.lower():
                platform_metadata["youtube"] = {
                    "category": "22",  # People & Blogs
                    "tags": result.optimized_metadata.get(MobileMetadataType.KEYWORDS, {}).seo_keywords or [],
                    "privacy": "public",
                    "mobile_optimized": True,
                    "shorts_eligible": True
                }
            elif "instagram" in platform.lower():
                platform_metadata["instagram"] = {
                    "caption": result.optimized_metadata.get(MobileMetadataType.DESCRIPTION, {}).optimized_content or "",
                    "hashtags": result.optimized_metadata.get(MobileMetadataType.HASHTAGS, {}).seo_keywords or [],
                    "location": request.geographic_targeting[0] if request.geographic_targeting else None,
                    "mobile_optimized": True,
                    "stories_ready": True,
                    "reels_ready": True
                }
            elif "tiktok" in platform.lower():
                platform_metadata["tiktok"] = {
                    "description": result.optimized_metadata.get(MobileMetadataType.DESCRIPTION, {}).optimized_content or "",
                    "hashtags": result.optimized_metadata.get(MobileMetadataType.HASHTAGS, {}).seo_keywords or [],
                    "effects_enabled": True,
                    "music_sync": True,
                    "mobile_optimized": True
                }
            elif "twitter" in platform.lower():
                platform_metadata["twitter"] = {
                    "tweet_text": result.optimized_metadata.get(MobileMetadataType.TITLE, {}).optimized_content or "",
                    "hashtags": result.optimized_metadata.get(MobileMetadataType.HASHTAGS, {}).seo_keywords or [],
                    "thread_support": True,
                    "mobile_optimized": True
                }
        
        result.platform_specific_metadata = platform_metadata
        result.mobile_optimizations.append("platform_specific_metadata")
        
        self.logger.debug(f"Platform-specific metadata generated for {len(platform_metadata)} platforms")
    
    async def _calculate_optimization_scores(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Calculate overall optimization scores."""
        self.logger.debug(f"Calculating optimization scores for {request.content_id}")
        
        # Collect individual scores
        scores = []
        for metadata in result.optimized_metadata.values():
            scores.append(metadata.optimization_score)
        
        # Calculate weighted average
        if scores:
            result.optimization_score = sum(scores) / len(scores)
        else:
            result.optimization_score = 0.0
        
        # Apply bonuses for additional optimizations
        bonus_score = 0.0
        if result.schema_markup:
            bonus_score += 5.0
        if result.og_tags:
            bonus_score += 3.0
        if result.twitter_cards:
            bonus_score += 3.0
        if result.mobile_app_tags:
            bonus_score += 4.0
        if result.accessibility_enhancements:
            bonus_score += 5.0
        
        result.optimization_score = min(100.0, result.optimization_score + bonus_score)
        
        # Update metrics
        self.optimization_metrics["average_optimization_score"] = (
            (self.optimization_metrics["average_optimization_score"] * (self.optimization_metrics["total_requests"] - 1) + 
             result.optimization_score) / self.optimization_metrics["total_requests"]
        )
        
        self.logger.debug(f"Optimization score calculated: {result.optimization_score:.1f}")
    
    async def _generate_analytics_data(self, request: MobileMetadataRequest, result: MobileMetadataResult):
        """Generate analytics data for metadata optimization."""
        analytics = {
            "optimization_id": result.request_id,
            "content_id": request.content_id,
            "creator_id": request.creator_id,
            "optimization_score": result.optimization_score,
            "metadata_types_optimized": len(result.optimized_metadata),
            "mobile_optimizations_count": len(result.mobile_optimizations),
            "seo_enhancements": bool(result.seo_insights),
            "accessibility_enhancements": len(result.accessibility_enhancements),
            "platform_adaptations": len(result.platform_specific_metadata),
            "schema_markup_generated": bool(result.schema_markup),
            "social_sharing_optimized": bool(result.og_tags and result.twitter_cards),
            "mobile_app_optimized": bool(result.mobile_app_tags),
            "amp_optimized": bool(result.amp_metadata),
            "processing_time_ms": result.processing_time_ms,
            "battery_efficiency": 100 - result.battery_usage_percent,
            "network_efficiency": 100 - result.network_usage_mb,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result.analytics_data = analytics
    
    def _get_og_type(self, content_type: str) -> str:
        """Get Open Graph type for content type."""
        mapping = {
            "video": "video.other",
            "audio": "music.song",
            "image": "article",
            "text": "article"
        }
        return mapping.get(content_type, "website")
    
    async def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get mobile metadata optimization performance metrics."""
        return {
            "optimization_metrics": self.optimization_metrics,
            "mobile_optimizations": self.mobile_optimizations,
            "timestamp": datetime.utcnow().isoformat()
        }


# Factory function for creating mobile metadata optimizer
def create_mobile_metadata_optimizer(config: Optional[Dict[str, Any]] = None) -> MobileMetadataOptimizer:
    """
    Factory function to create a mobile metadata optimizer with mobile-specific optimizations.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        MobileMetadataOptimizer: Configured mobile metadata optimizer
    """
    return MobileMetadataOptimizer(config)


# Export key classes and functions
__all__ = [
    "MobileMetadataOptimizer",
    "MobileMetadataRequest", 
    "MobileMetadataResult",
    "OptimizedMetadata",
    "MobileMetadataConfiguration",
    "MobileMetadataType",
    "MetadataOptimizationStrategy",
    "MobileMetadataFormat",
    "create_mobile_metadata_optimizer"
]