"""Platform Specific Validator - Platform-Optimized Validation System
==================================================================

Industrial-grade platform-specific validation system for the IA Influencer
Agent Platform, providing specialized validation rules and optimization
recommendations for major content platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited

Platform Validation Capabilities:
- YouTube validation rules and SEO optimization
- Instagram/TikTok specs compliance and engagement optimization
- Spotify audio requirements and metadata validation
- LinkedIn professional standards and content guidelines
- Cross-platform optimization recommendations
- Platform-specific monetization rules enforcement
- API compliance validation and rate limiting
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import re

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported platform types."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SPOTIFY = "spotify"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    TWITCH = "twitch"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"

class ValidationCategory(Enum):
    """Platform validation categories."""
    TECHNICAL_SPECS = "technical_specs"
    CONTENT_GUIDELINES = "content_guidelines"
    MONETIZATION_RULES = "monetization_rules"
    SEO_OPTIMIZATION = "seo_optimization"
    ENGAGEMENT_OPTIMIZATION = "engagement_optimization"
    API_COMPLIANCE = "api_compliance"
    ACCESSIBILITY = "accessibility"

class ComplianceLevel(Enum):
    """Compliance levels."""
    FULLY_COMPLIANT = "fully_compliant"
    MOSTLY_COMPLIANT = "mostly_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"

@dataclass
class PlatformSpecification:
    """Platform specification details."""
    platform: PlatformType
    specification_type: str
    requirement: str
    current_value: Any
    expected_value: Any
    is_compliant: bool
    severity: str = "medium"
    recommendation: Optional[str] = None

@dataclass
class PlatformValidationResult:
    """Platform-specific validation result."""
    platform: PlatformType
    overall_compliance: ComplianceLevel
    compliance_score: float
    specifications: List[PlatformSpecification] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    monetization_eligible: bool = False
    estimated_performance: Dict[str, float] = field(default_factory=dict)
    platform_specific_metrics: Dict[str, Any] = field(default_factory=dict)
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validation_duration_ms: int = 0

class PlatformSpecificValidator:
    """Platform-specific validation system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize platform-specific validator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.platform_specs = self._load_platform_specifications()
        
        # Validator settings
        self.strict_validation = self.config.get('strict_validation', False)
        self.enable_optimization = self.config.get('enable_optimization', True)
        self.check_monetization = self.config.get('check_monetization', True)
        
        logger.info("PlatformSpecificValidator initialized")
    
    def _load_platform_specifications(self) -> Dict[PlatformType, Dict[str, Any]]:
        """Load platform-specific specifications.
        
        Returns:
            Dictionary of platform specifications
        """
        return {
            PlatformType.YOUTUBE: {
                'technical_specs': {
                    'max_file_size_gb': 256,
                    'max_duration_hours': 12,
                    'supported_formats': ['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm', '3gpp'],
                    'min_resolution': (426, 240),
                    'max_resolution': (7680, 4320),  # 8K
                    'supported_aspect_ratios': ['16:9', '4:3', '1:1', '9:16'],
                    'recommended_bitrate': {'1080p': 8000, '720p': 5000, '480p': 2500},
                    'audio_codec': ['aac', 'mp3'],
                    'audio_bitrate': {'min': 128, 'recommended': 384}
                },
                'content_guidelines': {
                    'title_max_length': 100,
                    'description_max_length': 5000,
                    'tags_max_count': 500,
                    'thumbnail_required': True,
                    'end_screen_recommended': True,
                    'cards_recommended': True
                },
                'seo_optimization': {
                    'title_keywords': True,
                    'description_keywords': True,
                    'tags_relevance': True,
                    'thumbnail_optimization': True,
                    'closed_captions': True,
                    'chapters_recommended': True
                },
                'monetization_rules': {
                    'min_watch_hours': 4000,
                    'min_subscribers': 1000,
                    'content_type_restrictions': ['family_friendly', 'advertiser_friendly'],
                    'copyright_claims_allowed': 3,
                    'community_strikes_max': 0
                }
            },
            
            PlatformType.INSTAGRAM: {
                'technical_specs': {
                    'photo_max_size_mb': 30,
                    'video_max_size_mb': 4000,
                    'video_max_duration': {'feed': 60, 'stories': 15, 'reels': 90, 'igtv': 3600},
                    'supported_formats': {
                        'photo': ['jpg', 'png', 'gif'],
                        'video': ['mp4', 'mov']
                    },
                    'aspect_ratios': {
                        'feed': ['1:1', '4:5', '16:9'],
                        'stories': ['9:16'],
                        'reels': ['9:16']
                    },
                    'min_resolution': {'width': 320, 'height': 320},
                    'max_resolution': {'width': 1440, 'height': 1440}
                },
                'content_guidelines': {
                    'caption_max_length': 2200,
                    'hashtags_max_count': 30,
                    'hashtags_recommended_count': 5,
                    'mentions_max_count': 20,
                    'alt_text_recommended': True
                },
                'engagement_optimization': {
                    'hashtag_strategy': 'mixed',
                    'posting_time_optimization': True,
                    'story_highlights': True,
                    'user_generated_content': True,
                    'call_to_action': True
                }
            },
            
            PlatformType.TIKTOK: {
                'technical_specs': {
                    'max_file_size_mb': 4000,
                    'max_duration': 600,  # 10 minutes
                    'min_duration': 3,
                    'supported_formats': ['mp4', 'mov', 'webm'],
                    'aspect_ratio': '9:16',
                    'min_resolution': (540, 960),
                    'recommended_resolution': (1080, 1920),
                    'frame_rate': {'min': 23, 'max': 60}
                },
                'content_guidelines': {
                    'caption_max_length': 4000,
                    'hashtags_max_count': 100,
                    'hashtags_recommended': {'trending': 3, 'niche': 5},
                    'duet_enabled': True,
                    'stitch_enabled': True
                },
                'engagement_optimization': {
                    'trending_sounds': True,
                    'effects_usage': True,
                    'text_overlay': True,
                    'quick_cuts': True,
                    'vertical_format': True
                }
            },
            
            PlatformType.SPOTIFY: {
                'technical_specs': {
                    'max_file_size_mb': 200,
                    'supported_formats': ['mp3', 'wav', 'flac', 'm4a', 'ogg'],
                    'sample_rate': [44100, 48000],
                    'bit_depth': [16, 24],
                    'channels': [1, 2],  # Mono or stereo
                    'bitrate': {'min': 96, 'recommended': 320}
                },
                'content_guidelines': {
                    'title_max_length': 100,
                    'description_max_length': 4000,
                    'episode_number_required': True,
                    'season_number_optional': True,
                    'explicit_content_marking': True
                },
                'metadata_requirements': {
                    'artist_name': True,
                    'album_title': True,
                    'track_title': True,
                    'genre': True,
                    'release_date': True,
                    'cover_art': True,
                    'copyright_info': True
                }
            },
            
            PlatformType.LINKEDIN: {
                'content_guidelines': {
                    'post_max_length': 3000,
                    'article_max_length': 125000,
                    'hashtags_max_count': 5,
                    'hashtags_recommended': 3,
                    'professional_tone': True,
                    'business_relevant': True
                },
                'engagement_optimization': {
                    'industry_keywords': True,
                    'thought_leadership': True,
                    'professional_insights': True,
                    'network_building': True,
                    'skill_demonstration': True
                }
            }
        }
    
    async def validate_platform_compliance(self, content_data: Dict[str, Any],
                                         platform: PlatformType,
                                         validation_categories: Optional[List[ValidationCategory]] = None) -> PlatformValidationResult:
        """Validate content compliance for specific platform.
        
        Args:
            content_data: Content data and metadata
            platform: Target platform
            validation_categories: Specific categories to validate
            
        Returns:
            PlatformValidationResult with compliance details
        """
        start_time = datetime.now(timezone.utc)
        
        logger.info(f"Validating content for {platform.value}")
        
        try:
            # Get platform specifications
            if platform not in self.platform_specs:
                return PlatformValidationResult(
                    platform=platform,
                    overall_compliance=ComplianceLevel.UNKNOWN,
                    compliance_score=0.0,
                    optimization_suggestions=[f"Platform {platform.value} not supported"],
                    validation_duration_ms=int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                )
            
            platform_spec = self.platform_specs[platform]
            
            # Default validation categories
            if validation_categories is None:
                validation_categories = [
                    ValidationCategory.TECHNICAL_SPECS,
                    ValidationCategory.CONTENT_GUIDELINES,
                    ValidationCategory.SEO_OPTIMIZATION
                ]
            
            # Perform validations
            specifications = []
            
            for category in validation_categories:
                category_specs = await self._validate_category(
                    content_data, platform_spec, category, platform
                )
                specifications.extend(category_specs)
            
            # Calculate compliance score
            if specifications:
                compliant_specs = sum(1 for spec in specifications if spec.is_compliant)
                compliance_score = compliant_specs / len(specifications)
            else:
                compliance_score = 1.0
            
            # Determine overall compliance level
            overall_compliance = self._determine_compliance_level(compliance_score, specifications)
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(
                specifications, platform, content_data
            )
            
            # Check monetization eligibility
            monetization_eligible = await self._check_monetization_eligibility(
                content_data, platform, compliance_score
            )
            
            # Estimate platform performance
            estimated_performance = self._estimate_platform_performance(
                content_data, platform, compliance_score, specifications
            )
            
            # Collect platform-specific metrics
            platform_metrics = self._collect_platform_metrics(
                content_data, platform, specifications
            )
            
            end_time = datetime.now(timezone.utc)
            validation_duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return PlatformValidationResult(
                platform=platform,
                overall_compliance=overall_compliance,
                compliance_score=compliance_score,
                specifications=specifications,
                optimization_suggestions=optimization_suggestions,
                monetization_eligible=monetization_eligible,
                estimated_performance=estimated_performance,
                platform_specific_metrics=platform_metrics,
                validated_at=start_time,
                validation_duration_ms=validation_duration_ms
            )
            
        except Exception as e:
            logger.error(f"Platform validation failed for {platform.value}: {e}")
            end_time = datetime.now(timezone.utc)
            validation_duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return PlatformValidationResult(
                platform=platform,
                overall_compliance=ComplianceLevel.UNKNOWN,
                compliance_score=0.0,
                optimization_suggestions=[f"Validation failed: {str(e)}"],
                validation_duration_ms=validation_duration_ms
            )
    
    async def _validate_category(self, content_data: Dict[str, Any],
                               platform_spec: Dict[str, Any],
                               category: ValidationCategory,
                               platform: PlatformType) -> List[PlatformSpecification]:
        """Validate specific category for platform.
        
        Args:
            content_data: Content data
            platform_spec: Platform specifications
            category: Validation category
            platform: Platform type
            
        Returns:
            List of platform specifications with validation results
        """
        specifications = []
        category_name = category.value
        
        if category_name not in platform_spec:
            return specifications
        
        category_specs = platform_spec[category_name]
        
        if category == ValidationCategory.TECHNICAL_SPECS:
            specifications.extend(await self._validate_technical_specs(
                content_data, category_specs, platform
            ))
        
        elif category == ValidationCategory.CONTENT_GUIDELINES:
            specifications.extend(await self._validate_content_guidelines(
                content_data, category_specs, platform
            ))
        
        elif category == ValidationCategory.SEO_OPTIMIZATION:
            specifications.extend(await self._validate_seo_optimization(
                content_data, category_specs, platform
            ))
        
        elif category == ValidationCategory.MONETIZATION_RULES:
            specifications.extend(await self._validate_monetization_rules(
                content_data, category_specs, platform
            ))
        
        elif category == ValidationCategory.ENGAGEMENT_OPTIMIZATION:
            specifications.extend(await self._validate_engagement_optimization(
                content_data, category_specs, platform
            ))
        
        return specifications
    
    async def _validate_technical_specs(self, content_data: Dict[str, Any],
                                      specs: Dict[str, Any],
                                      platform: PlatformType) -> List[PlatformSpecification]:
        """Validate technical specifications."""
        specifications = []
        
        # File size validation
        if 'file_size' in content_data and 'max_file_size_mb' in specs:
            file_size_mb = content_data['file_size'] / (1024 * 1024)
            max_size_mb = specs['max_file_size_mb']
            is_compliant = file_size_mb <= max_size_mb
            
            specifications.append(PlatformSpecification(
                platform=platform,
                specification_type='file_size',
                requirement=f"File size must be ≤ {max_size_mb}MB",
                current_value=f"{file_size_mb:.1f}MB",
                expected_value=f"≤ {max_size_mb}MB",
                is_compliant=is_compliant,
                severity="error" if not is_compliant else "info",
                recommendation="Compress file to reduce size" if not is_compliant else None
            ))
        
        # Duration validation
        if 'duration' in content_data and 'max_duration' in specs:
            duration = content_data['duration']
            
            if isinstance(specs['max_duration'], dict):
                # Multiple duration limits (e.g., Instagram)
                content_type = content_data.get('content_type', 'feed')
                max_duration = specs['max_duration'].get(content_type, specs['max_duration'].get('feed', 3600))
            else:
                max_duration = specs['max_duration']
            
            is_compliant = duration <= max_duration
            
            specifications.append(PlatformSpecification(
                platform=platform,
                specification_type='duration',
                requirement=f"Duration must be ≤ {max_duration}s",
                current_value=f"{duration}s",
                expected_value=f"≤ {max_duration}s",
                is_compliant=is_compliant,
                severity="error" if not is_compliant else "info",
                recommendation="Reduce video length" if not is_compliant else None
            ))
        
        # Format validation
        if 'format' in content_data and 'supported_formats' in specs:
            file_format = content_data['format'].lower()
            supported_formats = specs['supported_formats']
            
            if isinstance(supported_formats, dict):
                # Format by content type
                content_type = content_data.get('content_type', 'video')
                supported = supported_formats.get(content_type, [])
            else:
                supported = supported_formats
            
            is_compliant = file_format in supported
            
            specifications.append(PlatformSpecification(
                platform=platform,
                specification_type='format',
                requirement=f"Format must be one of: {', '.join(supported)}",
                current_value=file_format,
                expected_value=', '.join(supported),
                is_compliant=is_compliant,
                severity="error" if not is_compliant else "info",
                recommendation=f"Convert to {supported[0]} format" if not is_compliant and supported else None
            ))
        
        # Resolution validation
        if 'resolution' in content_data and any(key in specs for key in ['min_resolution', 'max_resolution']):
            resolution = content_data['resolution']
            
            if 'min_resolution' in specs:
                min_res = specs['min_resolution']
                min_compliant = (resolution['width'] >= min_res[0] and 
                               resolution['height'] >= min_res[1])
                
                specifications.append(PlatformSpecification(
                    platform=platform,
                    specification_type='min_resolution',
                    requirement=f"Minimum resolution: {min_res[0]}x{min_res[1]}",
                    current_value=f"{resolution['width']}x{resolution['height']}",
                    expected_value=f"≥ {min_res[0]}x{min_res[1]}",
                    is_compliant=min_compliant,
                    severity="warning" if not min_compliant else "info",
                    recommendation="Increase resolution" if not min_compliant else None
                ))
        
        return specifications
    
    async def _validate_content_guidelines(self, content_data: Dict[str, Any],
                                         specs: Dict[str, Any],
                                         platform: PlatformType) -> List[PlatformSpecification]:
        """Validate content guidelines."""
        specifications = []
        
        # Title length validation
        if 'title' in content_data and 'title_max_length' in specs:
            title = content_data['title']
            max_length = specs['title_max_length']
            is_compliant = len(title) <= max_length
            
            specifications.append(PlatformSpecification(
                platform=platform,
                specification_type='title_length',
                requirement=f"Title must be ≤ {max_length} characters",
                current_value=f"{len(title)} characters",
                expected_value=f"≤ {max_length} characters",
                is_compliant=is_compliant,
                severity="warning" if not is_compliant else "info",
                recommendation="Shorten title" if not is_compliant else None
            ))
        
        # Description length validation
        if 'description' in content_data and 'description_max_length' in specs:
            description = content_data['description']
            max_length = specs['description_max_length']
            is_compliant = len(description) <= max_length
            
            specifications.append(PlatformSpecification(
                platform=platform,
                specification_type='description_length',
                requirement=f"Description must be ≤ {max_length} characters",
                current_value=f"{len(description)} characters",
                expected_value=f"≤ {max_length} characters",
                is_compliant=is_compliant,
                severity="warning" if not is_compliant else "info",
                recommendation="Shorten description" if not is_compliant else None
            ))
        
        # Hashtags validation
        if 'hashtags' in content_data and 'hashtags_max_count' in specs:
            hashtags = content_data['hashtags']
            max_count = specs['hashtags_max_count']
            is_compliant = len(hashtags) <= max_count
            
            specifications.append(PlatformSpecification(
                platform=platform,
                specification_type='hashtags_count',
                requirement=f"Hashtags must be ≤ {max_count}",
                current_value=f"{len(hashtags)} hashtags",
                expected_value=f"≤ {max_count} hashtags",
                is_compliant=is_compliant,
                severity="warning" if not is_compliant else "info",
                recommendation="Remove excess hashtags" if not is_compliant else None
            ))
        
        # Thumbnail requirement
        if 'thumbnail_required' in specs and specs['thumbnail_required']:
            has_thumbnail = content_data.get('thumbnail') is not None
            
            specifications.append(PlatformSpecification(
                platform=platform,
                specification_type='thumbnail',
                requirement="Thumbnail is required",
                current_value="Present" if has_thumbnail else "Missing",
                expected_value="Present",
                is_compliant=has_thumbnail,
                severity="warning" if not has_thumbnail else "info",
                recommendation="Add custom thumbnail" if not has_thumbnail else None
            ))
        
        return specifications
    
    async def _validate_seo_optimization(self, content_data: Dict[str, Any],
                                       specs: Dict[str, Any],
                                       platform: PlatformType) -> List[PlatformSpecification]:
        """Validate SEO optimization requirements."""
        specifications = []
        
        # Title keywords
        if specs.get('title_keywords') and 'title' in content_data:
            title = content_data['title']
            has_keywords = len(title.split()) >= 3  # Simple heuristic
            
            specifications.append(PlatformSpecification(
                platform=platform,
                specification_type='title_keywords',
                requirement="Title should contain relevant keywords",
                current_value="Present" if has_keywords else "Insufficient",
                expected_value="Present",
                is_compliant=has_keywords,
                severity="info",
                recommendation="Add relevant keywords to title" if not has_keywords else None
            ))
        
        # Description keywords
        if specs.get('description_keywords') and 'description' in content_data:
            description = content_data['description']
            has_keywords = len(description.split()) >= 10  # Simple heuristic
            
            specifications.append(PlatformSpecification(
                platform=platform,
                specification_type='description_keywords',
                requirement="Description should contain relevant keywords",
                current_value="Present" if has_keywords else "Insufficient",
                expected_value="Present",
                is_compliant=has_keywords,
                severity="info",
                recommendation="Add more descriptive keywords" if not has_keywords else None
            ))
        
        # Closed captions
        if specs.get('closed_captions'):
            has_captions = content_data.get('captions') is not None
            
            specifications.append(PlatformSpecification(
                platform=platform,
                specification_type='closed_captions',
                requirement="Closed captions recommended for accessibility",
                current_value="Present" if has_captions else "Missing",
                expected_value="Present",
                is_compliant=has_captions,
                severity="info",
                recommendation="Add closed captions" if not has_captions else None
            ))
        
        return specifications
    
    async def _validate_monetization_rules(self, content_data: Dict[str, Any],
                                         specs: Dict[str, Any],
                                         platform: PlatformType) -> List[PlatformSpecification]:
        """Validate monetization rules."""
        specifications = []
        
        # Channel requirements (for YouTube)
        if platform == PlatformType.YOUTUBE:
            # Watch hours requirement
            if 'channel_watch_hours' in content_data and 'min_watch_hours' in specs:
                watch_hours = content_data['channel_watch_hours']
                min_hours = specs['min_watch_hours']
                is_compliant = watch_hours >= min_hours
                
                specifications.append(PlatformSpecification(
                    platform=platform,
                    specification_type='watch_hours',
                    requirement=f"Minimum {min_hours} watch hours required",
                    current_value=f"{watch_hours} hours",
                    expected_value=f"≥ {min_hours} hours",
                    is_compliant=is_compliant,
                    severity="error" if not is_compliant else "info",
                    recommendation="Increase content engagement" if not is_compliant else None
                ))
            
            # Subscriber requirement
            if 'channel_subscribers' in content_data and 'min_subscribers' in specs:
                subscribers = content_data['channel_subscribers']
                min_subs = specs['min_subscribers']
                is_compliant = subscribers >= min_subs
                
                specifications.append(PlatformSpecification(
                    platform=platform,
                    specification_type='subscribers',
                    requirement=f"Minimum {min_subs} subscribers required",
                    current_value=f"{subscribers} subscribers",
                    expected_value=f"≥ {min_subs} subscribers",
                    is_compliant=is_compliant,
                    severity="error" if not is_compliant else "info",
                    recommendation="Focus on subscriber growth" if not is_compliant else None
                ))
        
        # Content type restrictions
        if 'content_type_restrictions' in specs:
            content_rating = content_data.get('content_rating', 'general')
            allowed_ratings = specs['content_type_restrictions']
            is_compliant = content_rating in allowed_ratings
            
            specifications.append(PlatformSpecification(
                platform=platform,
                specification_type='content_rating',
                requirement=f"Content must be: {', '.join(allowed_ratings)}",
                current_value=content_rating,
                expected_value=', '.join(allowed_ratings),
                is_compliant=is_compliant,
                severity="error" if not is_compliant else "info",
                recommendation="Ensure content is advertiser-friendly" if not is_compliant else None
            ))
        
        return specifications
    
    async def _validate_engagement_optimization(self, content_data: Dict[str, Any],
                                              specs: Dict[str, Any],
                                              platform: PlatformType) -> List[PlatformSpecification]:
        """Validate engagement optimization requirements."""
        specifications = []
        
        # Hashtag strategy
        if specs.get('hashtag_strategy') and 'hashtags' in content_data:
            hashtags = content_data['hashtags']
            has_strategy = len(hashtags) >= 3  # Simple check
            
            specifications.append(PlatformSpecification(
                platform=platform,
                specification_type='hashtag_strategy',
                requirement="Use strategic hashtag mix",
                current_value=f"{len(hashtags)} hashtags",
                expected_value="Strategic mix recommended",
                is_compliant=has_strategy,
                severity="info",
                recommendation="Use mix of trending and niche hashtags" if not has_strategy else None
            ))
        
        # Call to action
        if specs.get('call_to_action'):
            description = content_data.get('description', '')
            has_cta = any(word in description.lower() for word in ['subscribe', 'like', 'comment', 'share'])
            
            specifications.append(PlatformSpecification(
                platform=platform,
                specification_type='call_to_action',
                requirement="Include call-to-action",
                current_value="Present" if has_cta else "Missing",
                expected_value="Present",
                is_compliant=has_cta,
                severity="info",
                recommendation="Add call-to-action in description" if not has_cta else None
            ))
        
        return specifications
    
    def _determine_compliance_level(self, compliance_score: float,
                                  specifications: List[PlatformSpecification]) -> ComplianceLevel:
        """Determine overall compliance level."""
        if compliance_score >= 0.95:
            return ComplianceLevel.FULLY_COMPLIANT
        elif compliance_score >= 0.8:
            return ComplianceLevel.MOSTLY_COMPLIANT
        elif compliance_score >= 0.6:
            return ComplianceLevel.PARTIALLY_COMPLIANT
        else:
            return ComplianceLevel.NON_COMPLIANT
    
    def _generate_optimization_suggestions(self, specifications: List[PlatformSpecification],
                                         platform: PlatformType,
                                         content_data: Dict[str, Any]) -> List[str]:
        """Generate platform-specific optimization suggestions."""
        suggestions = []
        
        # Add suggestions from failed specifications
        for spec in specifications:
            if not spec.is_compliant and spec.recommendation:
                suggestions.append(spec.recommendation)
        
        # Platform-specific general suggestions
        if platform == PlatformType.YOUTUBE:
            suggestions.extend([
                "Optimize video thumbnail for click-through rate",
                "Add end screens and cards for viewer retention",
                "Use relevant keywords in title and description"
            ])
        
        elif platform == PlatformType.INSTAGRAM:
            suggestions.extend([
                "Use trending and niche hashtags mix",
                "Post during optimal engagement hours",
                "Create engaging story highlights"
            ])
        
        elif platform == PlatformType.TIKTOK:
            suggestions.extend([
                "Use trending sounds and effects",
                "Keep content vertical (9:16)",
                "Add text overlay for accessibility"
            ])
        
        elif platform == PlatformType.SPOTIFY:
            suggestions.extend([
                "Include detailed episode descriptions",
                "Add high-quality cover art",
                "Optimize audio quality to 320kbps"
            ])
        
        # Remove duplicates and limit suggestions
        return list(set(suggestions))[:5]
    
    async def _check_monetization_eligibility(self, content_data: Dict[str, Any],
                                            platform: PlatformType,
                                            compliance_score: float) -> bool:
        """Check if content is eligible for monetization."""
        if not self.check_monetization:
            return False
        
        # Basic compliance requirement
        if compliance_score < 0.8:
            return False
        
        # Platform-specific monetization checks
        if platform == PlatformType.YOUTUBE:
            # Check channel requirements
            watch_hours = content_data.get('channel_watch_hours', 0)
            subscribers = content_data.get('channel_subscribers', 0)
            
            return watch_hours >= 4000 and subscribers >= 1000
        
        elif platform == PlatformType.INSTAGRAM:
            # Check for business account and follower count
            followers = content_data.get('follower_count', 0)
            is_business = content_data.get('is_business_account', False)
            
            return is_business and followers >= 1000
        
        elif platform == PlatformType.TIKTOK:
            # Check for creator fund eligibility
            followers = content_data.get('follower_count', 0)
            return followers >= 10000
        
        else:
            # Default to compliance score
            return compliance_score >= 0.9
    
    def _estimate_platform_performance(self, content_data: Dict[str, Any],
                                     platform: PlatformType,
                                     compliance_score: float,
                                     specifications: List[PlatformSpecification]) -> Dict[str, float]:
        """Estimate content performance on platform."""
        base_performance = compliance_score
        
        # Adjust based on platform-specific factors
        performance_factors = {
            'reach_potential': base_performance,
            'engagement_potential': base_performance,
            'monetization_potential': 0.0,
            'viral_potential': base_performance * 0.8
        }
        
        # Platform-specific adjustments
        if platform == PlatformType.YOUTUBE:
            # SEO optimized content performs better on YouTube
            seo_specs = [s for s in specifications if 'keyword' in s.specification_type]
            if seo_specs and all(s.is_compliant for s in seo_specs):
                performance_factors['reach_potential'] *= 1.2
        
        elif platform == PlatformType.TIKTOK:
            # Trending elements boost viral potential
            if content_data.get('uses_trending_sounds'):
                performance_factors['viral_potential'] *= 1.5
        
        elif platform == PlatformType.INSTAGRAM:
            # High-quality visuals perform better
            if content_data.get('visual_quality_score', 0) > 0.8:
                performance_factors['engagement_potential'] *= 1.3
        
        # Monetization potential
        if compliance_score >= 0.9:
            performance_factors['monetization_potential'] = min(1.0, compliance_score * 1.1)
        
        # Normalize values
        return {k: min(1.0, v) for k, v in performance_factors.items()}
    
    def _collect_platform_metrics(self, content_data: Dict[str, Any],
                                 platform: PlatformType,
                                 specifications: List[PlatformSpecification]) -> Dict[str, Any]:
        """Collect platform-specific metrics."""
        metrics = {
            'total_specifications': len(specifications),
            'compliant_specifications': sum(1 for s in specifications if s.is_compliant),
            'critical_issues': sum(1 for s in specifications if not s.is_compliant and s.severity == 'error'),
            'warnings': sum(1 for s in specifications if not s.is_compliant and s.severity == 'warning'),
            'platform_optimized': len([s for s in specifications if s.is_compliant]) > len(specifications) * 0.8
        }
        
        # Platform-specific metrics
        if platform == PlatformType.YOUTUBE:
            metrics.update({
                'seo_optimized': any('keyword' in s.specification_type and s.is_compliant for s in specifications),
                'monetization_ready': content_data.get('channel_watch_hours', 0) >= 4000
            })
        
        elif platform == PlatformType.INSTAGRAM:
            metrics.update({
                'hashtag_optimized': len(content_data.get('hashtags', [])) <= 30,
                'visual_optimized': content_data.get('aspect_ratio') in ['1:1', '4:5', '9:16']
            })
        
        return metrics

# Export main classes and functions
__all__ = [
    'PlatformSpecificValidator',
    'PlatformType',
    'ValidationCategory',
    'ComplianceLevel',
    'PlatformSpecification',
    'PlatformValidationResult'
]