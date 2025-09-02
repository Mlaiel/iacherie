"""Platform Quality Validator - Multi-Platform Content Optimization System

Enterprise platform-specific quality validation and optimization system for 
maximizing content performance across different social media and content platforms.

Business Logic:
Platform analysis → Content optimization → Format compliance → 
Algorithm optimization → Engagement prediction → Performance recommendations

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import re
import hashlib
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class ContentPlatform(Enum):
    """
Supported content platforms"""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    MEDIUM = "medium"
    SUBSTACK = "substack"
    TWITCH = "twitch"
    DISCORD = "discord"
    CLUBHOUSE = "clubhouse"
    TELEGRAM = "telegram"


class ContentFormat(Enum):
    """Content format types"""

    VIDEO_SHORT = "video_short"  # < 60 seconds
    VIDEO_LONG = "video_long"   # > 60 seconds
    IMAGE_SINGLE = "image_single"
    IMAGE_CAROUSEL = "image_carousel"
    TEXT_POST = "text_post"
    STORY = "story"
    LIVE_STREAM = "live_stream"
    AUDIO_PODCAST = "audio_podcast"
    AUDIO_SHORT = "audio_short"
    BLOG_POST = "blog_post"
    NEWSLETTER = "newsletter"
    POLL = "poll"
    EVENT = "event"


class ValidationSeverity(Enum):
    """Validation issue severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class OptimizationCategory(Enum):
    """Optimization recommendation categories"""

    ALGORITHM = "algorithm"
    ENGAGEMENT = "engagement"
    DISCOVERY = "discovery"
    ACCESSIBILITY = "accessibility"
    MONETIZATION = "monetization"
    BRANDING = "branding"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"


@dataclass
class PlatformValidationIssue:
    """Individual platform validation issue"""
    issue_id: str
    platform: ContentPlatform
    severity: ValidationSeverity
    category: OptimizationCategory
    title: str
    description: str
    
    # Issue details
    affected_element: Optional[str] = None
    current_value: Optional[Any] = None
    recommended_value: Optional[Any] = None
    
    # Impact assessment
    impact_score: float = 0.0  # 0-100
    fix_difficulty: str = "medium"  # easy, medium, hard
    fix_priority: str = "medium"  # low, medium, high, critical
    
    # Recommendations
    fix_instructions: List[str] = field(default_factory=list)
    optimization_tips: List[str] = field(default_factory=list)
    
    # Metadata
    detection_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_rule: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
            'issue_id': self.issue_id,
            'platform': self.platform.value,
            'severity': self.severity.value,
            'category': self.category.value,
            'title': self.title,
            'description': self.description,
            'details': {
                'affected_element': self.affected_element,
                'current_value': self.current_value,
                'recommended_value': self.recommended_value
            },
            'impact': {
                'score': self.impact_score,
                'fix_difficulty': self.fix_difficulty,
                'fix_priority': self.fix_priority
            },
            'recommendations': {
                'fix_instructions': self.fix_instructions,
                'optimization_tips': self.optimization_tips
            },
            'metadata': {
                'detection_timestamp': self.detection_timestamp.isoformat(),
                'source_rule': self.source_rule
            }
        }


@dataclass
class PlatformOptimization:
    """Platform-specific optimization recommendation"""
    optimization_id: str
    platform: ContentPlatform
    category: OptimizationCategory
    title: str
    description: str
    
    # Optimization details
    current_score: float = 0.0  # Current performance score (0-100)
    potential_score: float = 0.0  # Potential score after optimization
    improvement_potential: float = 0.0  # Percentage improvement
    
    # Implementation
    implementation_steps: List[str] = field(default_factory=list)
    effort_required: str = "medium"  # low, medium, high
    time_to_implement: str = "medium"  # immediate, short, medium, long
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
    expected_benefits: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    
    # Algorithm considerations
    algorithm_factors: List[str] = field(default_factory=list)
    
    # Metadata
    priority_score: float = 0.0  # 0-100
    confidence: float = 0.8  # 0.0-1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'optimization_id': self.optimization_id,
            'platform': self.platform.value,
            'category': self.category.value,
            'title': self.title,
            'description': self.description,
            'performance': {
                'current_score': self.current_score,
                'potential_score': self.potential_score,
                'improvement_potential': self.improvement_potential
            },
            'implementation': {
                'steps': self.implementation_steps,
                'effort_required': self.effort_required,
                'time_to_implement': self.time_to_implement
            },
            'expected_outcomes': {
                'benefits': self.expected_benefits,
                'success_metrics': self.success_metrics
            },
            'algorithm_factors': self.algorithm_factors,
            'metadata': {
                'priority_score': self.priority_score,
                'confidence': self.confidence
            }
        }


@dataclass
class PlatformValidationResult:
    """Comprehensive platform validation result"""
    content_id: str
    platform: ContentPlatform
    content_format: ContentFormat
    overall_score: float  # 0-100
    
    # Issue breakdown
    total_issues: int = 0
    critical_issues: int = 0
    error_issues: int = 0
    warning_issues: int = 0
    info_issues: int = 0
    
    # Category scores
    algorithm_score: float = 0.0
    engagement_score: float = 0.0
    discovery_score: float = 0.0
    accessibility_score: float = 0.0
    monetization_score: float = 0.0
    branding_score: float = 0.0
    performance_score: float = 0.0
    compliance_score: float = 0.0
    
    # Validation issues and optimizations
    issues: List[PlatformValidationIssue] = field(default_factory=list)
    optimizations: List[PlatformOptimization] = field(default_factory=list)
    
    # Platform-specific metrics
    platform_specific_scores: Dict[str, float] = field(default_factory=dict)
    
    # Recommendations
    immediate_fixes: List[str] = field(default_factory=list)
    optimization_recommendations: List[str] = field(default_factory=list)
    long_term_improvements: List[str] = field(default_factory=list)
    
    # Analysis metadata
    validation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
    
    def add_issue(self, issue: PlatformValidationIssue):
        """
Add a validation issue"""
        self.issues.append(issue)
        self.total_issues += 1
        
        # Update issue counts by severity
        if issue.severity == ValidationSeverity.CRITICAL:
            self.critical_issues += 1
        elif issue.severity == ValidationSeverity.ERROR:
            self.error_issues += 1
        elif issue.severity == ValidationSeverity.WARNING:
            self.warning_issues += 1
        elif issue.severity == ValidationSeverity.INFO:
            self.info_issues += 1
    
    def add_optimization(self, optimization: PlatformOptimization):
        """
Add an optimization recommendation"""
        self.optimizations.append(optimization)
    
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[PlatformValidationIssue]:
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[PlatformValidationIssue]:
        """
Get issues by severity level"""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_category(self, category: OptimizationCategory) -> List[PlatformValidationIssue]:
        """
Get issues by category"""
        return [issue for issue in self.issues if issue.category == category]
    
    def get_top_optimizations(self, limit: int = 5) -> List[PlatformOptimization]:
        """
Get top optimization recommendations by priority"""
        sorted_optimizations = sorted(self.optimizations, 
                                    key=lambda x: x.priority_score, 
                                    reverse=True)
        return sorted_optimizations[:limit]
    
    def has_blocking_issues(self) -> bool:
        """
Check if there are blocking issues"""
        return self.critical_issues > 0 or self.error_issues > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content_id': self.content_id,
            'platform': self.platform.value,
            'content_format': self.content_format.value,
            'overall_score': self.overall_score,
            'issue_summary': {
                'total': self.total_issues,
                'critical': self.critical_issues,
                'error': self.error_issues,
                'warning': self.warning_issues,
                'info': self.info_issues
            },
            'category_scores': {
                'algorithm': self.algorithm_score,
                'engagement': self.engagement_score,
                'discovery': self.discovery_score,
                'accessibility': self.accessibility_score,
                'monetization': self.monetization_score,
                'branding': self.branding_score,
                'performance': self.performance_score,
                'compliance': self.compliance_score
            },
            'platform_specific_scores': self.platform_specific_scores,
            'issues': [issue.to_dict() for issue in self.issues],
            'optimizations': [opt.to_dict() for opt in self.optimizations],
            'recommendations': {
                'immediate_fixes': self.immediate_fixes,
                'optimization_recommendations': self.optimization_recommendations,
                'long_term_improvements': self.long_term_improvements
            },
            'metadata': {
                'validation_timestamp': self.validation_timestamp.isoformat(),
                'processing_time_ms': self.processing_time_ms
            }
        }


class YouTubeValidator:
    """
YouTube-specific content validation"""
    
    def __init__(self):
        self.platform_requirements = self._initialize_youtube_requirements()
        self.algorithm_factors = self._initialize_algorithm_factors()
    
    def _initialize_youtube_requirements(self) -> Dict[str, Any]:
        """
Initialize YouTube platform requirements"""
        return {
            'title': {
                'min_length': 10,
                'max_length': 100,
                'optimal_length': 60
            },
            'description': {
                'min_length': 125,
                'max_length': 5000,
                'optimal_length': 250
            },
            'tags': {
                'min_count': 5,
                'max_count': 15,
                'optimal_count': 10
            },
            'thumbnail': {
                'required': True,
                'dimensions': '1280x720',
                'format': ['JPG', 'PNG'],
                'max_size_mb': 2
            },
            'video': {
                'min_duration': 60,  # seconds
                'max_duration': 43200,  # 12 hours
                'optimal_duration_range': (300, 600),  # 5-10 minutes
                'formats': ['MP4', 'MOV', 'AVI'],
                'max_size_gb': 256
            }
        }
    
    def _initialize_algorithm_factors(self) -> Dict[str, float]:
        """
Initialize YouTube algorithm ranking factors with weights"""
        return {
            'watch_time': 0.25,
            'click_through_rate': 0.20,
            'audience_retention': 0.20,
            'engagement_rate': 0.15,
            'session_duration': 0.10,
            'subscriber_growth': 0.05,
            'video_freshness': 0.05
        }
    
    def validate_youtube_content(self, content_data: Dict[str, Any], 
                                content_id: str) -> PlatformValidationResult:
        """
Validate content for YouTube"""
        result = PlatformValidationResult(
            content_id=content_id,
            platform=ContentPlatform.YOUTUBE,
            content_format=self._determine_youtube_format(content_data),
            overall_score=0.0
        )
        
        # Validate title
        self._validate_title(content_data, result)
        
        # Validate description
        self._validate_description(content_data, result)
        
        # Validate tags
        self._validate_tags(content_data, result)
        
        # Validate thumbnail
        self._validate_thumbnail(content_data, result)
        
        # Validate video specifications
        self._validate_video_specs(content_data, result)
        
        # Algorithm optimization analysis
        self._analyze_algorithm_optimization(content_data, result)
        
        # SEO optimization
        self._analyze_seo_optimization(content_data, result)
        
        # Monetization readiness
        self._analyze_monetization_readiness(content_data, result)
        
        # Calculate scores
        self._calculate_category_scores(result)
        self._calculate_overall_score(result)
        
        # Generate recommendations
        self._generate_youtube_recommendations(result)
        
        return result
    
    def _determine_youtube_format(self, content_data: Dict[str, Any]) -> ContentFormat:
        """
Determine YouTube content format"""
        duration = content_data.get('duration', 0)
        
        if duration <= 60:
            return ContentFormat.VIDEO_SHORT
        else:
            return ContentFormat.VIDEO_LONG
    
    def _validate_title(self, content_data: Dict[str, Any], 
                       result: PlatformValidationResult):
        """
Validate YouTube title"""
        title = content_data.get('title', '')
        reqs = self.platform_requirements['title']
        
        if not title:
            issue = PlatformValidationIssue(
                issue_id="youtube_title_missing",
                platform=ContentPlatform.YOUTUBE,
                severity=ValidationSeverity.CRITICAL,
                category=OptimizationCategory.DISCOVERY,
                title="Missing Title",
                description="Video title is required for YouTube uploads",
                affected_element="title",
                current_value=None,
                recommended_value="Add descriptive title",
                impact_score=90.0,
                fix_difficulty="easy",
                fix_priority="critical",
                fix_instructions=[
                    "Add a compelling, descriptive title",
                    "Include primary keywords",
                    "Keep within 60 characters for mobile optimization"
                ],
                source_rule="youtube_title_required"
            )
            result.add_issue(issue)
            return
        
        title_length = len(title)
        
        # Length validation
        if title_length < reqs['min_length']:
            issue = PlatformValidationIssue(
                issue_id="youtube_title_too_short",
                platform=ContentPlatform.YOUTUBE,
                severity=ValidationSeverity.WARNING,
                category=OptimizationCategory.DISCOVERY,
                title="Title Too Short",
                description=f"Title should be at least {reqs['min_length']} characters",
                affected_element="title",
                current_value=title_length,
                recommended_value=f"≥{reqs['min_length']} characters",
                impact_score=60.0,
                fix_difficulty="easy",
                fix_priority="medium",
                fix_instructions=[
                    "Expand title with more descriptive keywords",
                    "Add context or value proposition",
                    "Include emotional triggers or numbers"
                ],
                source_rule="youtube_title_length_min"
            )
            result.add_issue(issue)
        
        if title_length > reqs['max_length']:
            issue = PlatformValidationIssue(
                issue_id="youtube_title_too_long",
                platform=ContentPlatform.YOUTUBE,
                severity=ValidationSeverity.WARNING,
                category=OptimizationCategory.DISCOVERY,
                title="Title Too Long",
                description=f"Title should not exceed {reqs['max_length']} characters",
                affected_element="title",
                current_value=title_length,
                recommended_value=f"≤{reqs['max_length']} characters",
                impact_score=40.0,
                fix_difficulty="easy",
                fix_priority="medium",
                fix_instructions=[
                    "Shorten title while keeping key information",
                    "Remove unnecessary words",
                    "Focus on most important keywords"
                ],
                source_rule="youtube_title_length_max"
            )
            result.add_issue(issue)
        
        # Keyword optimization check
        if not self._has_keywords(title):
            optimization = PlatformOptimization(
                optimization_id="youtube_title_keywords",
                platform=ContentPlatform.YOUTUBE,
                category=OptimizationCategory.DISCOVERY,
                title="Improve Title Keywords",
                description="Add relevant keywords to improve discoverability",
                current_score=50.0,
                potential_score=80.0,
                improvement_potential=30.0,
                implementation_steps=[
                    "Research relevant keywords using YouTube search suggestions",
                    "Include primary keyword near the beginning",
                    "Add secondary keywords naturally"
                ],
                effort_required="low",
                time_to_implement="immediate",
                expected_benefits=[
                    "Better search ranking",
                    "Higher click-through rate",
                    "Improved discoverability"
                ],
                algorithm_factors=["search_ranking", "suggested_videos"],
                priority_score=75.0
            )
            result.add_optimization(optimization)
    
    def _validate_description(self, content_data: Dict[str, Any], 
                            result: PlatformValidationResult):
        """Validate YouTube description"""
        description = content_data.get('description', '')
        reqs = self.platform_requirements['description']
        
        if not description:
            issue = PlatformValidationIssue(
                issue_id="youtube_description_missing",
                platform=ContentPlatform.YOUTUBE,
                severity=ValidationSeverity.ERROR,
                category=OptimizationCategory.DISCOVERY,
                title="Missing Description",
                description="Video description is important for SEO and context",
                affected_element="description",
                impact_score=70.0,
                fix_difficulty="medium",
                fix_priority="high",
                fix_instructions=[
                    "Add detailed video description",
                    "Include relevant keywords",
                    "Add timestamps for long videos",
                    "Include social media links"
                ],
                source_rule="youtube_description_recommended"
            )
            result.add_issue(issue)
            return
        
        desc_length = len(description)
        
        # Length validation
        if desc_length < reqs['min_length']:
            issue = PlatformValidationIssue(
                issue_id="youtube_description_too_short",
                platform=ContentPlatform.YOUTUBE,
                severity=ValidationSeverity.WARNING,
                category=OptimizationCategory.DISCOVERY,
                title="Description Too Short",
                description=f"Description should be at least {reqs['min_length']} characters for better SEO",
                affected_element="description",
                current_value=desc_length,
                recommended_value=f"≥{reqs['min_length']} characters",
                impact_score=50.0,
                fix_difficulty="medium",
                fix_priority="medium",
                fix_instructions=[
                    "Expand description with more details",
                    "Add video summary and key points",
                    "Include relevant hashtags and links"
                ],
                source_rule="youtube_description_length_min"
            )
            result.add_issue(issue)
        
        # Check for links and CTAs
        if not self._has_links_or_ctas(description):
            optimization = PlatformOptimization(
                optimization_id="youtube_description_ctas",
                platform=ContentPlatform.YOUTUBE,
                category=OptimizationCategory.ENGAGEMENT,
                title="Add Call-to-Actions",
                description="Include CTAs and links to drive engagement",
                current_score=60.0,
                potential_score=85.0,
                improvement_potential=25.0,
                implementation_steps=[
                    "Add subscribe reminder",
                    "Include social media links",
                    "Add relevant website links",
                    "Include call-to-action for comments"
                ],
                effort_required="low",
                time_to_implement="immediate",
                expected_benefits=[
                    "Higher engagement rates",
                    "More subscribers",
                    "Increased traffic to other platforms"
                ],
                priority_score=70.0
            )
            result.add_optimization(optimization)
    
    def _validate_tags(self, content_data: Dict[str, Any], 
                      result: PlatformValidationResult):
        """Validate YouTube tags"""
        tags = content_data.get('tags', [])
        reqs = self.platform_requirements['tags']
        
        if not tags:
            issue = PlatformValidationIssue(
                issue_id="youtube_tags_missing",
                platform=ContentPlatform.YOUTUBE,
                severity=ValidationSeverity.WARNING,
                category=OptimizationCategory.DISCOVERY,
                title="Missing Tags",
                description="Tags help YouTube understand and categorize your content",
                affected_element="tags",
                impact_score=60.0,
                fix_difficulty="easy",
                fix_priority="medium",
                fix_instructions=[
                    "Add 5-10 relevant tags",
                    "Include both broad and specific keywords",
                    "Use YouTube's search suggestions for ideas"
                ],
                source_rule="youtube_tags_recommended"
            )
            result.add_issue(issue)
            return
        
        tag_count = len(tags)
        
        if tag_count < reqs['min_count']:
            issue = PlatformValidationIssue(
                issue_id="youtube_tags_too_few",
                platform=ContentPlatform.YOUTUBE,
                severity=ValidationSeverity.INFO,
                category=OptimizationCategory.DISCOVERY,
                title="Too Few Tags",
                description=f"Consider adding more tags (recommended: {reqs['optimal_count']})",
                affected_element="tags",
                current_value=tag_count,
                recommended_value=f"≥{reqs['min_count']} tags",
                impact_score=30.0,
                fix_difficulty="easy",
                fix_priority="low",
                fix_instructions=[
                    "Add more relevant keywords as tags",
                    "Include synonyms and related terms",
                    "Add category-specific tags"
                ],
                source_rule="youtube_tags_count_min"
            )
            result.add_issue(issue)
        
        if tag_count > reqs['max_count']:
            issue = PlatformValidationIssue(
                issue_id="youtube_tags_too_many",
                platform=ContentPlatform.YOUTUBE,
                severity=ValidationSeverity.INFO,
                category=OptimizationCategory.DISCOVERY,
                title="Too Many Tags",
                description=f"Too many tags may dilute relevance (recommended: {reqs['optimal_count']})",
                affected_element="tags",
                current_value=tag_count,
                recommended_value=f"≤{reqs['max_count']} tags",
                impact_score=20.0,
                fix_difficulty="easy",
                fix_priority="low",
                fix_instructions=[
                    "Keep only the most relevant tags",
                    "Focus on primary keywords",
                    "Remove overly broad or unrelated tags"
                ],
                source_rule="youtube_tags_count_max"
            )
            result.add_issue(issue)
    
    def _validate_thumbnail(self, content_data: Dict[str, Any], 
                          result: PlatformValidationResult):
        """Validate YouTube thumbnail"""
        thumbnail = content_data.get('thumbnail')
        reqs = self.platform_requirements['thumbnail']
        
        if not thumbnail:
            issue = PlatformValidationIssue(
                issue_id="youtube_thumbnail_missing",
                platform=ContentPlatform.YOUTUBE,
                severity=ValidationSeverity.CRITICAL,
                category=OptimizationCategory.DISCOVERY,
                title="Missing Custom Thumbnail",
                description="Custom thumbnails significantly improve click-through rates",
                affected_element="thumbnail",
                impact_score=85.0,
                fix_difficulty="medium",
                fix_priority="critical",
                fix_instructions=[
                    "Create custom thumbnail with 1280x720 resolution",
                    "Use bright colors and clear text",
                    "Include faces or emotional expressions",
                    "Ensure readability on mobile devices"
                ],
                source_rule="youtube_thumbnail_required"
            )
            result.add_issue(issue)
            return
        
        # Check thumbnail specifications
        if isinstance(thumbnail, dict):
            dimensions = thumbnail.get('dimensions', '')
            if dimensions != reqs['dimensions']:
                issue = PlatformValidationIssue(
                    issue_id="youtube_thumbnail_dimensions",
                    platform=ContentPlatform.YOUTUBE,
                    severity=ValidationSeverity.WARNING,
                    category=OptimizationCategory.PERFORMANCE,
                    title="Incorrect Thumbnail Dimensions",
                    description=f"Optimal thumbnail size is {reqs['dimensions']}",
                    affected_element="thumbnail_dimensions",
                    current_value=dimensions,
                    recommended_value=reqs['dimensions'],
                    impact_score=40.0,
                    fix_difficulty="medium",
                    fix_priority="medium",
                    fix_instructions=[
                        "Resize thumbnail to 1280x720 pixels",
                        "Maintain 16:9 aspect ratio",
                        "Ensure high quality at recommended size"
                    ],
                    source_rule="youtube_thumbnail_dimensions"
                )
                result.add_issue(issue)
    
    def _validate_video_specs(self, content_data: Dict[str, Any], 
                            result: PlatformValidationResult):
        """Validate video specifications"""
        duration = content_data.get('duration', 0)
        reqs = self.platform_requirements['video']
        
        if duration < reqs['min_duration']:
            issue = PlatformValidationIssue(
                issue_id="youtube_video_too_short",
                platform=ContentPlatform.YOUTUBE,
                severity=ValidationSeverity.WARNING,
                category=OptimizationCategory.ALGORITHM,
                title="Video Too Short",
                description="Longer videos tend to perform better for watch time",
                affected_element="duration",
                current_value=f"{duration} seconds",
                recommended_value=f"≥{reqs['min_duration']} seconds",
                impact_score=50.0,
                fix_difficulty="hard",
                fix_priority="medium",
                fix_instructions=[
                    "Add more valuable content to extend duration",
                    "Include detailed explanations or examples",
                    "Consider adding intro/outro sections"
                ],
                source_rule="youtube_video_duration_min"
            )
            result.add_issue(issue)
        
        # Optimal duration range
        optimal_min, optimal_max = reqs['optimal_duration_range']
        if not (optimal_min <= duration <= optimal_max):
            optimization = PlatformOptimization(
                optimization_id="youtube_video_duration_optimization",
                platform=ContentPlatform.YOUTUBE,
                category=OptimizationCategory.ALGORITHM,
                title="Optimize Video Duration",
                description=f"Consider {optimal_min//60}-{optimal_max//60} minute range for better performance",
                current_score=60.0,
                potential_score=80.0,
                improvement_potential=20.0,
                implementation_steps=[
                    "Plan content for optimal duration range",
                    "Add valuable content without padding",
                    "Structure content for better retention"
                ],
                effort_required="medium",
                time_to_implement="medium",
                expected_benefits=[
                    "Better watch time metrics",
                    "Improved algorithm ranking",
                    "Higher audience retention"
                ],
                algorithm_factors=["watch_time", "audience_retention"],
                priority_score=65.0
            )
            result.add_optimization(optimization)
    
    def _analyze_algorithm_optimization(self, content_data: Dict[str, Any], 
                                      result: PlatformValidationResult):
        """Analyze YouTube algorithm optimization"""
        # Check for engagement elements
        if not content_data.get('has_engagement_prompts', False):
            optimization = PlatformOptimization(
                optimization_id="youtube_engagement_prompts",
                platform=ContentPlatform.YOUTUBE,
                category=OptimizationCategory.ENGAGEMENT,
                title="Add Engagement Prompts",
                description="Include prompts for likes, comments, and subscriptions",
                current_score=50.0,
                potential_score=75.0,
                improvement_potential=25.0,
                implementation_steps=[
                    "Ask specific questions to encourage comments",
                    "Remind viewers to like and subscribe",
                    "Create polls or community posts",
                    "Respond to comments to boost engagement"
                ],
                effort_required="low",
                time_to_implement="immediate",
                expected_benefits=[
                    "Higher engagement rates",
                    "Better algorithm ranking",
                    "Increased subscriber growth"
                ],
                algorithm_factors=["engagement_rate", "comments", "likes"],
                priority_score=80.0
            )
            result.add_optimization(optimization)
        
        # Check for end screens and cards
        if not content_data.get('has_end_screens', False):
            optimization = PlatformOptimization(
                optimization_id="youtube_end_screens",
                platform=ContentPlatform.YOUTUBE,
                category=OptimizationCategory.ALGORITHM,
                title="Add End Screens",
                description="Use end screens to promote other videos and increase session duration",
                current_score=60.0,
                potential_score=85.0,
                improvement_potential=25.0,
                implementation_steps=[
                    "Add end screen promoting related videos",
                    "Include subscribe button in end screen",
                    "Promote playlists to increase session time",
                    "Use YouTube's end screen editor"
                ],
                effort_required="low",
                time_to_implement="immediate",
                expected_benefits=[
                    "Longer session duration",
                    "More video views",
                    "Better algorithm performance"
                ],
                algorithm_factors=["session_duration", "suggested_videos"],
                priority_score=70.0
            )
            result.add_optimization(optimization)
    
    def _analyze_seo_optimization(self, content_data: Dict[str, Any], 
                                result: PlatformValidationResult):
        """Analyze SEO optimization for YouTube"""
        # Check for keyword optimization
        title = content_data.get('title', '')
        description = content_data.get('description', '')
        
        if not self._has_target_keywords(title, description):
            optimization = PlatformOptimization(
                optimization_id="youtube_seo_keywords",
                platform=ContentPlatform.YOUTUBE,
                category=OptimizationCategory.DISCOVERY,
                title="Improve SEO Keywords",
                description="Optimize title and description with target keywords",
                current_score=40.0,
                potential_score=80.0,
                improvement_potential=40.0,
                implementation_steps=[
                    "Research high-volume, low-competition keywords",
                    "Include primary keyword in title and description",
                    "Add long-tail keywords naturally",
                    "Use keyword variations and synonyms"
                ],
                effort_required="medium",
                time_to_implement="short",
                expected_benefits=[
                    "Higher search rankings",
                    "Better discoverability",
                    "Increased organic traffic"
                ],
                algorithm_factors=["search_ranking", "discovery"],
                priority_score=85.0
            )
            result.add_optimization(optimization)
    
    def _analyze_monetization_readiness(self, content_data: Dict[str, Any], 
                                      result: PlatformValidationResult):
        """Analyze monetization readiness"""
        # Check for advertiser-friendly content
        if not content_data.get('advertiser_friendly', True):
            issue = PlatformValidationIssue(
                issue_id="youtube_advertiser_unfriendly",
                platform=ContentPlatform.YOUTUBE,
                severity=ValidationSeverity.WARNING,
                category=OptimizationCategory.MONETIZATION,
                title="Content May Not Be Advertiser-Friendly",
                description="Content should comply with YouTube's advertiser-friendly guidelines",
                affected_element="content_guidelines",
                impact_score=70.0,
                fix_difficulty="medium",
                fix_priority="high",
                fix_instructions=[
                    "Review YouTube's advertiser-friendly content guidelines",
                    "Remove or modify controversial content",
                    "Ensure content is suitable for all audiences",
                    "Add appropriate content warnings if needed"
                ],
                source_rule="youtube_advertiser_friendly"
            )
            result.add_issue(issue)
    
    def _calculate_category_scores(self, result: PlatformValidationResult):
        """Calculate category-specific scores"""
        # Algorithm score based on optimization factors
        result.algorithm_score = 100.0 - (result.critical_issues * 25 + result.error_issues * 15)
        
        # Engagement score based on engagement-related issues
        engagement_issues = len(result.get_issues_by_category(OptimizationCategory.ENGAGEMENT))
        result.engagement_score = max(0.0, 100.0 - (engagement_issues * 20))
        
        # Discovery score based on SEO and discoverability
        discovery_issues = len(result.get_issues_by_category(OptimizationCategory.DISCOVERY))
        result.discovery_score = max(0.0, 100.0 - (discovery_issues * 15))
        
        # Performance score based on technical specs
        performance_issues = len(result.get_issues_by_category(OptimizationCategory.PERFORMANCE))
        result.performance_score = max(0.0, 100.0 - (performance_issues * 10))
        
        # Monetization score
        monetization_issues = len(result.get_issues_by_category(OptimizationCategory.MONETIZATION))
        result.monetization_score = max(0.0, 100.0 - (monetization_issues * 25))
        
        # Compliance score
        compliance_issues = len(result.get_issues_by_category(OptimizationCategory.COMPLIANCE))
        result.compliance_score = max(0.0, 100.0 - (compliance_issues * 30))
    
    def _calculate_overall_score(self, result: PlatformValidationResult):
        """
Calculate overall platform score"""
        # Weight different categories
        weights = {
            'algorithm': 0.25,
            'discovery': 0.20,
            'engagement': 0.20,
            'performance': 0.15,
            'monetization': 0.10,
            'compliance': 0.10
        }
        
        weighted_score = (
            result.algorithm_score * weights['algorithm'] +
            result.discovery_score * weights['discovery'] +
            result.engagement_score * weights['engagement'] +
            result.performance_score * weights['performance'] +
            result.monetization_score * weights['monetization'] +
            result.compliance_score * weights['compliance']
        )
        
        # Apply penalty for critical issues
        penalty = result.critical_issues * 20 + result.error_issues * 10
        
        result.overall_score = max(0.0, weighted_score - penalty)
    
    def _generate_youtube_recommendations(self, result: PlatformValidationResult):
        """
Generate YouTube-specific recommendations"""
        # Immediate fixes for critical issues
        critical_issues = result.get_issues_by_severity(ValidationSeverity.CRITICAL)
        for issue in critical_issues:
            result.immediate_fixes.extend(issue.fix_instructions[:2])
        
        # Top optimization recommendations
        top_optimizations = result.get_top_optimizations(3)
        for opt in top_optimizations:
            result.optimization_recommendations.extend(opt.implementation_steps[:2])
        
        # Long-term improvements
        result.long_term_improvements = [
            "Build consistent upload schedule",
            "Develop series or playlists for better session duration",
            "Engage with community through comments and community posts",
            "Analyze analytics to understand audience preferences",
            "Collaborate with other creators in your niche"
        ]
    
    def _has_keywords(self, text: str) -> bool:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            "Develop series or playlists for better session duration",
            "Engage with community through comments and community posts",
            "Analyze analytics to understand audience preferences",
            "Collaborate with other creators in your niche"
        ]
    
    def _has_keywords(self, text: str) -> bool:
        """Check if text contains relevant keywords"""
        # Simple keyword check - could be enhanced with actual keyword analysis
        return len(text.split()) >= 3 and any(len(word) > 4 for word in text.split())
    
    def _has_links_or_ctas(self, text: str) -> bool:
        """
Check if description contains links or CTAs"""
        cta_patterns = [
            r'subscribe', r'like', r'comment', r'share', r'follow',
            r'http[s]?://', r'www\.', r'@\w+', r'#\w+'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in cta_patterns)
    
    def _has_target_keywords(self, title: str, description: str) -> bool:
        """
Check if content has optimized keywords"""
        combined_text = f"{title} {description}".lower()
        
        # Check for keyword density and variety
        words = combined_text.split()
        unique_words = set(words)
        
        # Simple heuristic: good keyword usage
        return len(unique_words) >= 10 and len(words) >= 20


class InstagramValidator:
    """Instagram-specific content validation"""
    
    def __init__(self):
        self.platform_requirements = self._initialize_instagram_requirements()
    
    def _initialize_instagram_requirements(self) -> Dict[str, Any]:
        """
Initialize Instagram platform requirements"""
        return {
            'caption': {
                'max_length': 2200,
                'optimal_length': 150,
                'hashtag_limit': 30
            },
            'image': {
                'min_resolution': '600x600',
                'optimal_resolution': '1080x1080',
                'aspect_ratios': ['1:1', '4:5', '16:9'],
                'formats': ['JPG', 'PNG']
            },
            'video': {
                'max_duration': 60,  # seconds for feed posts
                'min_duration': 3,
                'formats': ['MP4', 'MOV'],
                'max_size_mb': 100
            },
            'stories': {
                'duration': 15,  # seconds
                'resolution': '1080x1920',
                'aspect_ratio': '9:16'
            }
        }
    
    def validate_instagram_content(self, content_data: Dict[str, Any], 
                                 content_id: str) -> PlatformValidationResult:
        """
Validate content for Instagram"""
        result = PlatformValidationResult(
            content_id=content_id,
            platform=ContentPlatform.INSTAGRAM,
            content_format=self._determine_instagram_format(content_data),
            overall_score=0.0
        )
        
        # Validate caption
        self._validate_caption(content_data, result)
        
        # Validate hashtags
        self._validate_hashtags(content_data, result)
        
        # Validate visual content
        if content_data.get('content_type') == 'image':
            self._validate_image_specs(content_data, result)
        elif content_data.get('content_type') == 'video':
            self._validate_video_specs(content_data, result)
        
        # Engagement optimization
        self._analyze_engagement_optimization(content_data, result)
        
        # Algorithm optimization
        self._analyze_instagram_algorithm(content_data, result)
        
        # Calculate scores
        self._calculate_category_scores(result)
        self._calculate_overall_score(result)
        
        # Generate recommendations
        self._generate_instagram_recommendations(result)
        
        return result
    
    def _determine_instagram_format(self, content_data: Dict[str, Any]) -> ContentFormat:
        """
Determine Instagram content format"""
        content_type = content_data.get('content_type', 'image')
        is_story = content_data.get('is_story', False)
        
        if is_story:
            return ContentFormat.STORY
        elif content_type == 'video':
            return ContentFormat.VIDEO_SHORT
        elif content_data.get('is_carousel', False):
            return ContentFormat.IMAGE_CAROUSEL
        else:
            return ContentFormat.IMAGE_SINGLE
    
    def _validate_caption(self, content_data: Dict[str, Any], 
                         result: PlatformValidationResult):
        """
Validate Instagram caption"""
        caption = content_data.get('caption', '')
        reqs = self.platform_requirements['caption']
        
        if not caption:
            issue = PlatformValidationIssue(
                issue_id="instagram_caption_missing",
                platform=ContentPlatform.INSTAGRAM,
                severity=ValidationSeverity.WARNING,
                category=OptimizationCategory.ENGAGEMENT,
                title="Missing Caption",
                description="Captions help with engagement and discoverability",
                affected_element="caption",
                impact_score=60.0,
                fix_difficulty="easy",
                fix_priority="medium",
                fix_instructions=[
                    "Add engaging caption that tells a story",
                    "Include relevant hashtags",
                    "Ask questions to encourage comments"
                ],
                source_rule="instagram_caption_recommended"
            )
            result.add_issue(issue)
            return
        
        caption_length = len(caption)
        
        if caption_length > reqs['max_length']:
            issue = PlatformValidationIssue(
                issue_id="instagram_caption_too_long",
                platform=ContentPlatform.INSTAGRAM,
                severity=ValidationSeverity.WARNING,
                category=OptimizationCategory.ENGAGEMENT,
                title="Caption Too Long",
                description=f"Caption exceeds {reqs['max_length']} character limit",
                affected_element="caption",
                current_value=caption_length,
                recommended_value=f"≤{reqs['max_length']} characters",
                impact_score=30.0,
                fix_difficulty="easy",
                fix_priority="medium",
                fix_instructions=[
                    "Shorten caption while keeping key message",
                    "Move some content to comments",
                    "Use line breaks for better readability"
                ],
                source_rule="instagram_caption_length_max"
            )
            result.add_issue(issue)
    
    def _validate_hashtags(self, content_data: Dict[str, Any], 
                          result: PlatformValidationResult):
        """Validate Instagram hashtags"""
        caption = content_data.get('caption', '')
        hashtags = re.findall(r'#\w+', caption)
        hashtag_count = len(hashtags)
        reqs = self.platform_requirements['caption']
        
        if hashtag_count == 0:
            issue = PlatformValidationIssue(
                issue_id="instagram_hashtags_missing",
                platform=ContentPlatform.INSTAGRAM,
                severity=ValidationSeverity.WARNING,
                category=OptimizationCategory.DISCOVERY,
                title="Missing Hashtags",
                description="Hashtags are crucial for discoverability on Instagram",
                affected_element="hashtags",
                impact_score=70.0,
                fix_difficulty="easy",
                fix_priority="high",
                fix_instructions=[
                    "Add 10-15 relevant hashtags",
                    "Mix popular and niche hashtags",
                    "Use location-based hashtags if relevant"
                ],
                source_rule="instagram_hashtags_recommended"
            )
            result.add_issue(issue)
        
        elif hashtag_count > reqs['hashtag_limit']:
            issue = PlatformValidationIssue(
                issue_id="instagram_hashtags_too_many",
                platform=ContentPlatform.INSTAGRAM,
                severity=ValidationSeverity.ERROR,
                category=OptimizationCategory.DISCOVERY,
                title="Too Many Hashtags",
                description=f"Instagram limits hashtags to {reqs['hashtag_limit']} per post",
                affected_element="hashtags",
                current_value=hashtag_count,
                recommended_value=f"≤{reqs['hashtag_limit']} hashtags",
                impact_score=80.0,
                fix_difficulty="easy",
                fix_priority="high",
                fix_instructions=[
                    f"Remove {hashtag_count - reqs['hashtag_limit']} hashtags",
                    "Keep only the most relevant hashtags",
                    "Move some hashtags to comments"
                ],
                source_rule="instagram_hashtags_limit"
            )
            result.add_issue(issue)
        
        # Hashtag optimization
        if hashtag_count < 10:
            optimization = PlatformOptimization(
                optimization_id="instagram_hashtag_optimization",
                platform=ContentPlatform.INSTAGRAM,
                category=OptimizationCategory.DISCOVERY,
                title="Optimize Hashtag Usage",
                description="Use more hashtags to maximize discoverability",
                current_score=50.0,
                potential_score=80.0,
                improvement_potential=30.0,
                implementation_steps=[
                    "Research trending hashtags in your niche",
                    "Use a mix of popular and niche hashtags",
                    "Include location-based hashtags",
                    "Analyze competitor hashtag strategies"
                ],
                effort_required="low",
                time_to_implement="immediate",
                expected_benefits=[
                    "Better discoverability",
                    "Increased reach",
                    "More engagement from new audiences"
                ],
                priority_score=75.0
            )
            result.add_optimization(optimization)
    
    def _validate_image_specs(self, content_data: Dict[str, Any], 
                            result: PlatformValidationResult):
        """Validate Instagram image specifications"""
        image_data = content_data.get('image', {})
        reqs = self.platform_requirements['image']
        
        resolution = image_data.get('resolution', '')
        if resolution and resolution != reqs['optimal_resolution']:
            issue = PlatformValidationIssue(
                issue_id="instagram_image_resolution",
                platform=ContentPlatform.INSTAGRAM,
                severity=ValidationSeverity.INFO,
                category=OptimizationCategory.PERFORMANCE,
                title="Suboptimal Image Resolution",
                description=f"Optimal resolution is {reqs['optimal_resolution']}",
                affected_element="image_resolution",
                current_value=resolution,
                recommended_value=reqs['optimal_resolution'],
                impact_score=25.0,
                fix_difficulty="medium",
                fix_priority="low",
                fix_instructions=[
                    "Resize image to 1080x1080 pixels",
                    "Maintain high quality during resize",
                    "Consider different aspect ratios for variety"
                ],
                source_rule="instagram_image_resolution"
            )
            result.add_issue(issue)
    
    def _analyze_engagement_optimization(self, content_data: Dict[str, Any], 
                                       result: PlatformValidationResult):
        """Analyze engagement optimization for Instagram"""
        caption = content_data.get('caption', '')
        
        # Check for engagement prompts
        if not self._has_engagement_prompts(caption):
            optimization = PlatformOptimization(
                optimization_id="instagram_engagement_prompts",
                platform=ContentPlatform.INSTAGRAM,
                category=OptimizationCategory.ENGAGEMENT,
                title="Add Engagement Prompts",
                description="Include prompts to encourage likes, comments, and saves",
                current_score=50.0,
                potential_score=80.0,
                improvement_potential=30.0,
                implementation_steps=[
                    "Ask questions in captions",
                    "Prompt users to share their experiences",
                    "Create content that encourages saves",
                    "Use Instagram stickers in stories"
                ],
                effort_required="low",
                time_to_implement="immediate",
                expected_benefits=[
                    "Higher engagement rates",
                    "Better algorithm reach",
                    "Increased follower interaction"
                ],
                priority_score=85.0
            )
            result.add_optimization(optimization)
    
    def _analyze_instagram_algorithm(self, content_data: Dict[str, Any], 
                                   result: PlatformValidationResult):
        """Analyze Instagram algorithm optimization"""
        # Check for optimal posting elements
        if not content_data.get('has_strong_first_line', False):
            optimization = PlatformOptimization(
                optimization_id="instagram_first_line",
                platform=ContentPlatform.INSTAGRAM,
                category=OptimizationCategory.ALGORITHM,
                title="Optimize First Line",
                description="Make the first line of caption compelling to increase engagement",
                current_score=60.0,
                potential_score=85.0,
                improvement_potential=25.0,
                implementation_steps=[
                    "Start with hook or intriguing statement",
                    "Ask compelling question in first line",
                    "Use emojis strategically",
                    "Avoid starting with generic phrases"
                ],
                effort_required="low",
                time_to_implement="immediate",
                expected_benefits=[
                    "Higher completion rates",
                    "Better algorithm performance",
                    "Increased engagement"
                ],
                algorithm_factors=["engagement_rate", "completion_rate"],
                priority_score=75.0
            )
            result.add_optimization(optimization)
    
    def _has_engagement_prompts(self, caption: str) -> bool:
        """Check if caption contains engagement prompts"""
        prompt_patterns = [
            r'\?', r'comment', r'share', r'tag', r'thoughts',
            r'what do you think', r'let me know', r'tell me'
        ]
        
        caption_lower = caption.lower()
        return any(re.search(pattern, caption_lower) for pattern in prompt_patterns)


class PlatformQualityValidator:
    """
Enterprise platform quality validation system"""
    
    def __init__(self):
        self.youtube_validator = YouTubeValidator()
        self.instagram_validator = InstagramValidator()
        # Additional platform validators can be added here
    
    def validate_platform_quality(self, content_data: Dict[str, Any],
                                 platform: ContentPlatform,
                                 content_id: str = "unknown") -> PlatformValidationResult:
        """Validate content quality for specific platform"""
        start_time = datetime.now(timezone.utc)
        
        try:
            if platform == ContentPlatform.YOUTUBE:
                result = self.youtube_validator.validate_youtube_content(content_data, content_id)
            elif platform == ContentPlatform.INSTAGRAM:
                result = self.instagram_validator.validate_instagram_content(content_data, content_id)
            else:
                # Generic validation for unsupported platforms
                result = self._generic_platform_validation(content_data, platform, content_id)
            
        except Exception as e:
            logger.error(f"Platform validation error for {platform.value}: {e}")
            result = PlatformValidationResult(
                content_id=content_id,
                platform=platform,
                content_format=ContentFormat.TEXT_POST,
                overall_score=0.0
            )
            
            error_issue = PlatformValidationIssue(
                issue_id="validation_error",
                platform=platform,
                severity=ValidationSeverity.CRITICAL,
                category=OptimizationCategory.PERFORMANCE,
                title="Validation Error",
                description=f"Error during platform validation: {str(e)}",
                impact_score=100.0,
                fix_difficulty="hard",
                fix_priority="critical"
            )
            result.add_issue(error_issue)
        
        # Finalize result
        end_time = datetime.now(timezone.utc)
        result.processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return result
    
    def _generic_platform_validation(self, content_data: Dict[str, Any],
                                   platform: ContentPlatform,
                                   content_id: str) -> PlatformValidationResult:
        """Generic validation for unsupported platforms"""
        result = PlatformValidationResult(
            content_id=content_id,
            platform=platform,
            content_format=ContentFormat.TEXT_POST,
            overall_score=75.0  # Default score for basic content
        )
        
        # Basic content validation
        if not content_data.get('title') and not content_data.get('content'):
            issue = PlatformValidationIssue(
                issue_id="generic_content_missing",
                platform=platform,
                severity=ValidationSeverity.CRITICAL,
                category=OptimizationCategory.COMPLIANCE,
                title="Missing Content",
                description="Content must have title or body text",
                impact_score=90.0,
                fix_difficulty="easy",
                fix_priority="critical",
                fix_instructions=["Add content title or body text"],
                source_rule="generic_content_required"
            )
            result.add_issue(issue)
        
        return result
    
    def batch_validate_platforms(self, content_data: Dict[str, Any],
                                platforms: List[ContentPlatform],
                                content_id: str = "unknown") -> List[PlatformValidationResult]:
        """Validate content for multiple platforms"""
        results = []
        
        for platform in platforms:
            result = self.validate_platform_quality(content_data, platform, content_id)
            results.append(result)
        
        return results
    
    def get_platform_comparison(self, results: List[PlatformValidationResult]) -> Dict[str, Any]:
        """
Compare validation results across platforms"""
        if not results:
            return {}
        
        platform_scores = {}
        platform_issues = {}
        platform_optimizations = {}
        
        for result in results:
            platform_name = result.platform.value
            platform_scores[platform_name] = result.overall_score
            platform_issues[platform_name] = result.total_issues
            platform_optimizations[platform_name] = len(result.optimizations)
        
        # Find best and worst platforms
        best_platform = max(platform_scores.items(), key=lambda x: x[1])
        worst_platform = min(platform_scores.items(), key=lambda x: x[1])
        
        # Calculate average score
        avg_score = sum(platform_scores.values()) / len(platform_scores)
        
        return {
            'platform_scores': platform_scores,
            'platform_issues': platform_issues,
            'platform_optimizations': platform_optimizations,
            'best_platform': {
                'platform': best_platform[0],
                'score': best_platform[1]
            },
            'worst_platform': {
                'platform': worst_platform[0],
                'score': worst_platform[1]
            },
            'average_score': avg_score,
            'total_platforms': len(results),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def get_optimization_summary(self, results: List[PlatformValidationResult]) -> Dict[str, Any]:
        """
Get optimization summary across platforms"""
        all_optimizations = []
        category_counts = {}
        
        for result in results:
            all_optimizations.extend(result.optimizations)
        
        # Count optimizations by category
        for opt in all_optimizations:
            category = opt.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Get top optimizations across all platforms
        top_optimizations = sorted(all_optimizations, 
                                 key=lambda x: x.priority_score, 
                                 reverse=True)[:10]
        
        return {
            'total_optimizations': len(all_optimizations),
            'optimizations_by_category': category_counts,
            'top_optimizations': [opt.to_dict() for opt in top_optimizations],
            'average_priority_score': sum(opt.priority_score for opt in all_optimizations) / len(all_optimizations) if all_optimizations else 0,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
