"""Platform-Specific Intent Recognition

Specialized intent recognition for platform-specific operations across
social media, streaming, and content distribution platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import re
import json

from .config import IntentRecognitionConfig
from .exceptions import PlatformIntentError

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms"""
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    DISCORD = "discord"


class PlatformIntentType(Enum):
    """Platform-specific intent types"""
    CONTENT_UPLOAD = "content_upload"
    ANALYTICS_REVIEW = "analytics_review"
    AUDIENCE_ENGAGEMENT = "audience_engagement"
    MONETIZATION_SETUP = "monetization_setup"
    PROMOTION_STRATEGY = "promotion_strategy"
    COLLABORATION_SEARCH = "collaboration_search"
    CONTENT_OPTIMIZATION = "content_optimization"
    CROSS_PLATFORM_SYNC = "cross_platform_sync"
    SCHEDULING_MANAGEMENT = "scheduling_management"
    HASHTAG_OPTIMIZATION = "hashtag_optimization"
    COMMUNITY_MANAGEMENT = "community_management"
    LIVE_STREAMING = "live_streaming"
    STORY_CREATION = "story_creation"
    PLAYLIST_MANAGEMENT = "playlist_management"
    ADVERTISING_CAMPAIGN = "advertising_campaign"


class ContentType(Enum):
    """Content types by platform"""
    AUDIO_TRACK = "audio_track"
    MUSIC_VIDEO = "music_video"
    PHOTO = "photo"
    VIDEO_POST = "video_post"
    STORY = "story"
    REEL = "reel"
    SHORT_VIDEO = "short_video"
    LIVE_STREAM = "live_stream"
    PODCAST_EPISODE = "podcast_episode"
    BLOG_POST = "blog_post"
    CAROUSEL_POST = "carousel_post"
    IGTV_VIDEO = "igtv_video"
    YOUTUBE_SHORT = "youtube_short"
    TIKTOK_VIDEO = "tiktok_video"
    TWITTER_THREAD = "twitter_thread"


@dataclass
class PlatformSpecification:
    """Platform-specific requirements and constraints"""
    
    # Content specifications
    max_file_size: int  # in MB
    supported_formats: List[str]
    max_duration: Optional[timedelta] = None
    min_duration: Optional[timedelta] = None
    aspect_ratios: List[str] = field(default_factory=list)
    
    # Text specifications
    max_caption_length: int = 0
    hashtag_limit: int = 0
    mention_limit: int = 0
    
    # Features
    supports_stories: bool = False
    supports_live_streaming: bool = False
    supports_scheduling: bool = False
    supports_analytics: bool = False
    supports_monetization: bool = False
    
    # API limitations
    api_rate_limits: Dict[str, int] = field(default_factory=dict)
    posting_frequency_limits: Dict[str, int] = field(default_factory=dict)


@dataclass
class PlatformIntentAnalysis:
    """Platform-specific intent analysis result"""
    
    # Identified platform and intent
    platform: Platform
    intent_type: PlatformIntentType
    content_type: Optional[ContentType] = None
    
    # Platform-specific context
    platform_features_used: List[str] = field(default_factory=list)
    optimization_opportunities: List[str] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)
    
    # Content requirements
    content_specifications: Optional[PlatformSpecification] = None
    recommended_posting_times: List[datetime] = field(default_factory=list)
    hashtag_suggestions: List[str] = field(default_factory=list)
    
    # Cross-platform considerations
    cross_platform_opportunities: List[Platform] = field(default_factory=list)
    adaptation_requirements: Dict[Platform, List[str]] = field(default_factory=dict)
    
    # Performance predictions
    estimated_reach: Dict[str, float] = field(default_factory=dict)
    engagement_predictions: Dict[str, float] = field(default_factory=dict)
    monetization_potential: float = 0.0
    
    # Recommendations
    platform_specific_tips: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    risk_warnings: List[str] = field(default_factory=list)


class PlatformSpecificIntentProcessor:
    """
    Platform-specific intent recognition and analysis system
    
    Provides specialized processing for platform-specific operations:
    - Platform identification from context
    - Platform-specific intent classification
    - Content requirement analysis
    - Cross-platform optimization suggestions
    - Platform compliance checking
    """
    
    def __init__(self, config: IntentRecognitionConfig):
        self.config = config
        self.platform_patterns = self._initialize_platform_patterns()
        self.platform_specs = self._initialize_platform_specifications()
        self.intent_patterns = self._initialize_intent_patterns()
        self.optimization_rules = self._load_optimization_rules()
    
    def _initialize_platform_patterns(self) -> Dict[Platform, re.Pattern]:
        """Initialize platform detection patterns"""
        return {
            Platform.SPOTIFY: re.compile(
                r'\b(spotify|streaming|playlist|album|track|artist)\b', re.IGNORECASE
            ),
            Platform.INSTAGRAM: re.compile(
                r'\b(instagram|insta|ig|story|stories|reel|reels|igtv)\b', re.IGNORECASE
            ),
            Platform.YOUTUBE: re.compile(
                r'\b(youtube|yt|video|vlog|subscriber|monetization|shorts)\b', re.IGNORECASE
            ),
            Platform.TIKTOK: re.compile(
                r'\b(tiktok|tt|short video|viral|fyp|for you|trend)\b', re.IGNORECASE
            ),
            Platform.TWITTER: re.compile(
                r'\b(twitter|tweet|retweet|thread|hashtag|trending)\b', re.IGNORECASE
            ),
            Platform.SOUNDCLOUD: re.compile(
                r'\b(soundcloud|sc|audio|track|mix|upload)\b', re.IGNORECASE
            ),
            Platform.TWITCH: re.compile(
                r'\b(twitch|stream|streaming|live|chat|follower)\b', re.IGNORECASE
            ),
            Platform.PATREON: re.compile(
                r'\b(patreon|subscription|tier|supporter|creator)\b', re.IGNORECASE
            )
        }
    
    def _initialize_platform_specifications(self) -> Dict[Platform, PlatformSpecification]:
        """Initialize platform-specific specifications"""
        return {
            Platform.SPOTIFY: PlatformSpecification(
                max_file_size=100,  # MB
                supported_formats=["mp3", "wav", "flac", "m4a"],
                min_duration=timedelta(seconds=30),
                max_duration=timedelta(minutes=30),
                max_caption_length=0,
                hashtag_limit=0,
                supports_analytics=True,
                supports_monetization=True,
                api_rate_limits={"uploads": 100, "metadata": 1000}
            ),
            
            Platform.INSTAGRAM: PlatformSpecification(
                max_file_size=100,  # MB for video
                supported_formats=["jpg", "png", "mp4", "mov"],
                max_duration=timedelta(minutes=60),  # for IGTV
                aspect_ratios=["1:1", "4:5", "9:16", "16:9"],
                max_caption_length=2200,
                hashtag_limit=30,
                mention_limit=20,
                supports_stories=True,
                supports_live_streaming=True,
                supports_scheduling=True,
                supports_analytics=True,
                supports_monetization=True,
                posting_frequency_limits={"posts": 25, "stories": 100}
            ),
            
            Platform.YOUTUBE: PlatformSpecification(
                max_file_size=256000,  # MB (256GB)
                supported_formats=["mp4", "mov", "avi", "wmv", "flv", "webm"],
                max_duration=timedelta(hours=12),
                aspect_ratios=["16:9", "9:16"],
                max_caption_length=5000,
                hashtag_limit=15,
                supports_live_streaming=True,
                supports_scheduling=True,
                supports_analytics=True,
                supports_monetization=True,
                api_rate_limits={"uploads": 6, "metadata": 10000}
            ),
            
            Platform.TIKTOK: PlatformSpecification(
                max_file_size=72,  # MB
                supported_formats=["mp4", "mov", "mpeg", "mpg", "avi"],
                min_duration=timedelta(seconds=3),
                max_duration=timedelta(minutes=10),
                aspect_ratios=["9:16"],
                max_caption_length=150,
                hashtag_limit=100,
                supports_analytics=True,
                supports_monetization=True,
                posting_frequency_limits={"videos": 3}
            ),
            
            Platform.TWITTER: PlatformSpecification(
                max_file_size=512,  # MB for video
                supported_formats=["jpg", "png", "gif", "mp4", "mov"],
                max_duration=timedelta(minutes=2, seconds=20),
                max_caption_length=280,
                hashtag_limit=2,  # recommended
                supports_live_streaming=True,
                supports_analytics=True,
                api_rate_limits={"tweets": 300, "retweets": 300}
            )
        }
    
    def _initialize_intent_patterns(self) -> Dict[PlatformIntentType, re.Pattern]:
        """Initialize intent type patterns"""
        return {
            PlatformIntentType.CONTENT_UPLOAD: re.compile(
                r'\b(upload|post|publish|share|release|drop)\b', re.IGNORECASE
            ),
            PlatformIntentType.ANALYTICS_REVIEW: re.compile(
                r'\b(analytics|stats|metrics|performance|insights|data)\b', re.IGNORECASE
            ),
            PlatformIntentType.AUDIENCE_ENGAGEMENT: re.compile(
                r'\b(engage|interaction|comment|like|follow|audience)\b', re.IGNORECASE
            ),
            PlatformIntentType.MONETIZATION_SETUP: re.compile(
                r'\b(monetize|revenue|earnings|ads|sponsorship|income)\b', re.IGNORECASE
            ),
            PlatformIntentType.HASHTAG_OPTIMIZATION: re.compile(
                r'\b(hashtag|tags|trending|discover|reach)\b', re.IGNORECASE
            ),
            PlatformIntentType.SCHEDULING_MANAGEMENT: re.compile(
                r'\b(schedule|timing|when to post|best time|automate)\b', re.IGNORECASE
            ),
            PlatformIntentType.CROSS_PLATFORM_SYNC: re.compile(
                r'\b(cross-platform|sync|multiple platforms|everywhere)\b', re.IGNORECASE
            )
        }
    
    def _load_optimization_rules(self) -> Dict[Platform, Dict[str, Any]]:
        """Load platform-specific optimization rules"""
        return {
            Platform.INSTAGRAM: {
                "best_posting_times": [
                    {"day": "monday", "hours": [6, 10, 19]},
                    {"day": "tuesday", "hours": [6, 10, 19]},
                    {"day": "wednesday", "hours": [6, 10, 19]},
                    {"day": "thursday", "hours": [6, 10, 19]},
                    {"day": "friday", "hours": [6, 10, 19]}
                ],
                "content_strategies": {
                    "photo": ["high_quality", "consistent_filter", "story_behind"],
                    "video": ["first_3_seconds_hook", "captions", "trending_audio"],
                    "story": ["interactive_elements", "behind_scenes", "polls"]
                },
                "hashtag_strategy": {
                    "total_hashtags": 25,
                    "mix": {"popular": 5, "medium": 15, "niche": 5}
                }
            },
            
            Platform.YOUTUBE: {
                "best_posting_times": [
                    {"day": "tuesday", "hours": [14, 15, 16]},
                    {"day": "wednesday", "hours": [14, 15, 16]},
                    {"day": "thursday", "hours": [14, 15, 16]}
                ],
                "content_strategies": {
                    "video": ["compelling_thumbnail", "seo_title", "detailed_description"],
                    "shorts": ["vertical_format", "quick_hook", "trending_music"]
                },
                "seo_optimization": {
                    "title_length": 60,
                    "description_keywords": 3,
                    "tags_count": 10
                }
            },
            
            Platform.TIKTOK: {
                "best_posting_times": [
                    {"day": "tuesday", "hours": [6, 10, 19]},
                    {"day": "wednesday", "hours": [6, 10, 19]},
                    {"day": "thursday", "hours": [6, 10, 19]}
                ],
                "content_strategies": {
                    "video": ["hook_first_3_seconds", "trending_sounds", "jump_cuts"],
                    "trends": ["current_challenges", "popular_effects", "viral_sounds"]
                },
                "algorithm_optimization": {
                    "watch_time": "critical",
                    "completion_rate": "very_important",
                    "shares": "important"
                }
            }
        }
    
    def analyze_platform_intent(
        self,
        message_text: str,
        user_profile: Dict[str, Any],
        conversation_context: Dict[str, Any],
        explicit_platform: Optional[str] = None
    ) -> PlatformIntentAnalysis:
        """
        Analyze platform-specific intent with comprehensive context
        
        Args:
            message_text: User's message
            user_profile: User profile with platform information
            conversation_context: Conversation context
            explicit_platform: Explicitly mentioned platform
            
        Returns:
            PlatformIntentAnalysis: Comprehensive platform intent analysis
        """
        try:
            # Identify target platform
            platform = self._identify_platform(message_text, user_profile, explicit_platform)
            
            # Identify intent type
            intent_type = self._identify_intent_type(message_text, platform)
            
            # Identify content type
            content_type = self._identify_content_type(message_text, platform, user_profile)
            
            # Get platform specifications
            platform_specs = self.platform_specs.get(platform)
            
            # Analyze platform features usage
            features_used = self._analyze_platform_features(message_text, platform)
            
            # Generate optimization opportunities
            optimization_opportunities = self._generate_optimization_opportunities(
                platform, intent_type, user_profile
            )
            
            # Check compliance requirements
            compliance_requirements = self._check_compliance_requirements(
                platform, content_type, user_profile
            )
            
            # Generate recommendations
            recommendations = self._generate_platform_recommendations(
                platform, intent_type, content_type, user_profile
            )
            
            # Analyze cross-platform opportunities
            cross_platform_analysis = self._analyze_cross_platform_opportunities(
                platform, content_type, user_profile
            )
            
            # Predict performance
            performance_predictions = self._predict_platform_performance(
                platform, content_type, user_profile
            )
            
            return PlatformIntentAnalysis(
                platform=platform,
                intent_type=intent_type,
                content_type=content_type,
                platform_features_used=features_used,
                optimization_opportunities=optimization_opportunities,
                compliance_requirements=compliance_requirements,
                content_specifications=platform_specs,
                recommended_posting_times=self._get_optimal_posting_times(platform),
                hashtag_suggestions=self._generate_hashtag_suggestions(platform, content_type),
                cross_platform_opportunities=cross_platform_analysis["opportunities"],
                adaptation_requirements=cross_platform_analysis["adaptations"],
                estimated_reach=performance_predictions["reach"],
                engagement_predictions=performance_predictions["engagement"],
                monetization_potential=performance_predictions["monetization"],
                platform_specific_tips=recommendations["tips"],
                optimization_suggestions=recommendations["optimizations"],
                risk_warnings=recommendations["warnings"]
            )
            
        except Exception as e:
            logger.error(f"Platform intent analysis failed: {e}")
            raise PlatformIntentError(f"Analysis failed: {e}")
    
    def _identify_platform(
        self,
        message_text: str,
        user_profile: Dict[str, Any],
        explicit_platform: Optional[str] = None
    ) -> Platform:
        """Identify target platform from message and context"""
        
        if explicit_platform:
            try:
                return Platform(explicit_platform.lower())
            except ValueError:
                pass
        
        # Check message text for platform mentions
        text_lower = message_text.lower()
        platform_scores = {}
        
        for platform, pattern in self.platform_patterns.items():
            matches = len(pattern.findall(text_lower))
            if matches > 0:
                platform_scores[platform] = matches
        
        if platform_scores:
            return max(platform_scores, key=platform_scores.get)
        
        # Fallback to user's primary platform
        user_platforms = user_profile.get("platforms", [])
        if user_platforms:
            primary_platform = user_platforms[0].lower()
            try:
                return Platform(primary_platform)
            except ValueError:
                pass
        
        # Default to Instagram for general social media content
        return Platform.INSTAGRAM
    
    def _identify_intent_type(
        self,
        message_text: str,
        platform: Platform
    ) -> PlatformIntentType:
        """Identify the specific intent type for the platform"""
        
        text_lower = message_text.lower()
        intent_scores = {}
        
        for intent_type, pattern in self.intent_patterns.items():
            matches = len(pattern.findall(text_lower))
            if matches > 0:
                intent_scores[intent_type] = matches
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        # Platform-specific default intents
        platform_defaults = {
            Platform.SPOTIFY: PlatformIntentType.CONTENT_UPLOAD,
            Platform.INSTAGRAM: PlatformIntentType.CONTENT_UPLOAD,
            Platform.YOUTUBE: PlatformIntentType.CONTENT_UPLOAD,
            Platform.TIKTOK: PlatformIntentType.CONTENT_UPLOAD,
            Platform.TWITTER: PlatformIntentType.AUDIENCE_ENGAGEMENT
        }
        
        return platform_defaults.get(platform, PlatformIntentType.CONTENT_UPLOAD)
    
    def _identify_content_type(
        self,
        message_text: str,
        platform: Platform,
        user_profile: Dict[str, Any]
    ) -> Optional[ContentType]:
        """Identify the content type based on message and platform"""
        
        text_lower = message_text.lower()
        
        # Content type keywords
        content_keywords = {
            ContentType.AUDIO_TRACK: ["song", "track", "music", "audio", "album"],
            ContentType.MUSIC_VIDEO: ["music video", "mv", "video"],
            ContentType.PHOTO: ["photo", "picture", "image", "pic"],
            ContentType.VIDEO_POST: ["video", "clip", "footage"],
            ContentType.STORY: ["story", "stories"],
            ContentType.REEL: ["reel", "reels"],
            ContentType.SHORT_VIDEO: ["short", "shorts", "brief"],
            ContentType.LIVE_STREAM: ["live", "streaming", "broadcast"],
            ContentType.PODCAST_EPISODE: ["podcast", "episode", "audio show"]
        }
        
        # Score content types
        content_scores = {}
        for content_type, keywords in content_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                content_scores[content_type] = score
        
        if content_scores:
            identified_type = max(content_scores, key=content_scores.get)
            
            # Validate content type for platform
            if self._is_content_type_supported(platform, identified_type):
                return identified_type
        
        # Platform-specific defaults based on user type
        creator_type = user_profile.get("creator_type", "")
        
        if platform == Platform.SPOTIFY:
            return ContentType.AUDIO_TRACK
        elif platform == Platform.INSTAGRAM:
            if creator_type == "photographer":
                return ContentType.PHOTO
            else:
                return ContentType.VIDEO_POST
        elif platform == Platform.YOUTUBE:
            return ContentType.VIDEO_POST
        elif platform == Platform.TIKTOK:
            return ContentType.SHORT_VIDEO
        
        return None
    
    def _is_content_type_supported(self, platform: Platform, content_type: ContentType) -> bool:
        """Check if content type is supported by platform"""
        
        platform_content_support = {
            Platform.SPOTIFY: [ContentType.AUDIO_TRACK, ContentType.PODCAST_EPISODE],
            Platform.INSTAGRAM: [
                ContentType.PHOTO, ContentType.VIDEO_POST, ContentType.STORY,
                ContentType.REEL, ContentType.LIVE_STREAM, ContentType.IGTV_VIDEO
            ],
            Platform.YOUTUBE: [
                ContentType.VIDEO_POST, ContentType.LIVE_STREAM, ContentType.YOUTUBE_SHORT
            ],
            Platform.TIKTOK: [ContentType.SHORT_VIDEO, ContentType.TIKTOK_VIDEO],
            Platform.TWITTER: [
                ContentType.PHOTO, ContentType.VIDEO_POST, ContentType.LIVE_STREAM,
                ContentType.TWITTER_THREAD
            ]
        }
        
        supported_types = platform_content_support.get(platform, [])
        return content_type in supported_types
    
    def _analyze_platform_features(self, message_text: str, platform: Platform) -> List[str]:
        """Analyze which platform features are mentioned or implied"""
        
        features_used = []
        text_lower = message_text.lower()
        
        # Platform-specific feature keywords
        feature_keywords = {
            Platform.INSTAGRAM: {
                "stories": ["story", "stories", "24 hours"],
                "reels": ["reel", "reels", "short video"],
                "igtv": ["igtv", "long video"],
                "shopping": ["shop", "product", "shopping", "tag"],
                "live": ["live", "broadcast", "streaming"],
                "hashtags": ["hashtag", "tags", "#"]
            },
            Platform.YOUTUBE: {
                "shorts": ["shorts", "short video"],
                "community": ["community", "poll", "post"],
                "premieres": ["premiere", "scheduled"],
                "chapters": ["chapters", "timestamp"],
                "cards": ["cards", "end screen"],
                "monetization": ["monetize", "ads", "revenue"]
            },
            Platform.TIKTOK: {
                "duets": ["duet", "collaboration"],
                "effects": ["effect", "filter"],
                "sounds": ["sound", "audio", "music"],
                "challenges": ["challenge", "trend"],
                "live": ["live", "streaming"]
            }
        }
        
        platform_features = feature_keywords.get(platform, {})
        for feature, keywords in platform_features.items():
            if any(keyword in text_lower for keyword in keywords):
                features_used.append(feature)
        
        return features_used
    
    def _generate_optimization_opportunities(
        self,
        platform: Platform,
        intent_type: PlatformIntentType,
        user_profile: Dict[str, Any]
    ) -> List[str]:
        """Generate platform-specific optimization opportunities"""
        
        opportunities = []
        
        # General platform optimizations
        if platform == Platform.INSTAGRAM:
            opportunities.extend([
                "Use Instagram Reels for higher reach",
                "Optimize Stories with interactive elements",
                "Leverage hashtag research for discovery",
                "Post during peak engagement hours"
            ])
        elif platform == Platform.YOUTUBE:
            opportunities.extend([
                "Create eye-catching thumbnails",
                "Optimize video titles for SEO",
                "Use end screens for subscriber growth",
                "Create YouTube Shorts for viral potential"
            ])
        elif platform == Platform.TIKTOK:
            opportunities.extend([
                "Use trending sounds and effects",
                "Participate in current challenges",
                "Hook viewers in first 3 seconds",
                "Cross-promote on other platforms"
            ])
        
        # Intent-specific optimizations
        if intent_type == PlatformIntentType.MONETIZATION_SETUP:
            opportunities.extend([
                "Meet platform monetization requirements",
                "Set up creator fund eligibility",
                "Explore brand partnership opportunities"
            ])
        elif intent_type == PlatformIntentType.AUDIENCE_ENGAGEMENT:
            opportunities.extend([
                "Respond to comments promptly",
                "Use platform-specific engagement features",
                "Create community-driven content"
            ])
        
        return opportunities
    
    def _check_compliance_requirements(
        self,
        platform: Platform,
        content_type: Optional[ContentType],
        user_profile: Dict[str, Any]
    ) -> List[str]:
        """Check platform compliance requirements"""
        
        requirements = []
        
        # General platform requirements
        platform_requirements = {
            Platform.INSTAGRAM: [
                "Follow community guidelines",
                "Respect copyright for music use",
                "Disclose sponsored content with #ad"
            ],
            Platform.YOUTUBE: [
                "Comply with monetization policies",
                "Follow copyright guidelines",
                "Age-appropriate content ratings"
            ],
            Platform.TIKTOK: [
                "Original or licensed audio only",
                "Follow community guidelines",
                "Age-appropriate content"
            ]
        }
        
        requirements.extend(platform_requirements.get(platform, []))
        
        # Business account specific requirements
        if user_profile.get("account_type") == "business":
            requirements.extend([
                "Business information accuracy",
                "Terms of service compliance",
                "Privacy policy requirements"
            ])
        
        return requirements
    
    def _generate_platform_recommendations(
        self,
        platform: Platform,
        intent_type: PlatformIntentType,
        content_type: Optional[ContentType],
        user_profile: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate comprehensive platform recommendations"""
        
        tips = []
        optimizations = []
        warnings = []
        
        # Platform-specific tips
        if platform == Platform.INSTAGRAM:
            tips.extend([
                "Maintain consistent visual brand",
                "Use high-quality images and videos",
                "Engage with your community regularly",
                "Share behind-the-scenes content"
            ])
            
            if content_type == ContentType.REEL:
                optimizations.extend([
                    "Use trending audio for better reach",
                    "Add captions for accessibility",
                    "Include call-to-action in description"
                ])
        
        elif platform == Platform.YOUTUBE:
            tips.extend([
                "Upload consistently on schedule",
                "Create compelling thumbnails",
                "Write detailed video descriptions",
                "Engage with comments section"
            ])
            
            warnings.extend([
                "Avoid copyright strikes",
                "Meet monetization thresholds",
                "Follow content policies strictly"
            ])
        
        # Creator type specific recommendations
        creator_type = user_profile.get("creator_type", "")
        if creator_type == "musician":
            tips.extend([
                "Share creation process content",
                "Tease new releases strategically",
                "Collaborate with other artists"
            ])
        
        return {
            "tips": tips,
            "optimizations": optimizations,
            "warnings": warnings
        }
    
    def _analyze_cross_platform_opportunities(
        self,
        primary_platform: Platform,
        content_type: Optional[ContentType],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze cross-platform distribution opportunities"""
        
        opportunities = []
        adaptations = {}
        
        # Content type cross-platform compatibility
        if content_type == ContentType.VIDEO_POST:
            opportunities.extend([
                Platform.YOUTUBE, Platform.INSTAGRAM, Platform.TIKTOK, Platform.TWITTER
            ])
            
            adaptations = {
                Platform.YOUTUBE: ["Add intro/outro", "Longer format", "SEO optimization"],
                Platform.INSTAGRAM: ["Square format option", "Add to Stories", "IGTV version"],
                Platform.TIKTOK: ["Shorten to under 3 minutes", "Add trending audio", "Vertical format"],
                Platform.TWITTER: ["Under 2:20 duration", "Add engaging tweet", "Thread context"]
            }
        
        elif content_type == ContentType.AUDIO_TRACK:
            opportunities.extend([
                Platform.SPOTIFY, Platform.SOUNDCLOUD, Platform.YOUTUBE, Platform.INSTAGRAM
            ])
            
            adaptations = {
                Platform.SPOTIFY: ["Professional distribution", "Playlist pitching"],
                Platform.SOUNDCLOUD: ["Direct upload", "Community engagement"],
                Platform.YOUTUBE: ["Create visualizer video", "Audio-only upload"],
                Platform.INSTAGRAM: ["Story snippet", "Reel with visualization"]
            }
        
        # Remove primary platform from opportunities
        if primary_platform in opportunities:
            opportunities.remove(primary_platform)
        
        return {
            "opportunities": opportunities,
            "adaptations": adaptations
        }
    
    def _predict_platform_performance(
        self,
        platform: Platform,
        content_type: Optional[ContentType],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """Predict performance metrics for platform content"""
        
        follower_count = user_profile.get("total_followers", 1000)
        engagement_rate = user_profile.get("engagement_rate", 0.03)
        
        # Platform-specific performance multipliers
        platform_multipliers = {
            Platform.INSTAGRAM: {"reach": 0.15, "engagement": 0.03},
            Platform.YOUTUBE: {"reach": 0.25, "engagement": 0.05},
            Platform.TIKTOK: {"reach": 0.4, "engagement": 0.08},
            Platform.TWITTER: {"reach": 0.1, "engagement": 0.02}
        }
        
        multipliers = platform_multipliers.get(platform, {"reach": 0.1, "engagement": 0.02})
        
        estimated_reach = {
            "organic": follower_count * multipliers["reach"],
            "total": follower_count * multipliers["reach"] * 1.5,
            "viral_potential": follower_count * multipliers["reach"] * 3
        }
        
        engagement_predictions = {
            "likes": estimated_reach["organic"] * engagement_rate,
            "comments": estimated_reach["organic"] * engagement_rate * 0.1,
            "shares": estimated_reach["organic"] * engagement_rate * 0.05,
            "saves": estimated_reach["organic"] * engagement_rate * 0.03
        }
        
        # Monetization potential (simplified)
        monetization_potential = 0.0
        if follower_count > 1000:
            base_rate = 0.01  # $0.01 per follower base rate
            monetization_potential = follower_count * base_rate * engagement_rate * 10
        
        return {
            "reach": estimated_reach,
            "engagement": engagement_predictions,
            "monetization": monetization_potential
        }
    
    def _get_optimal_posting_times(self, platform: Platform) -> List[datetime]:
        """Get optimal posting times for platform"""
        
        optimization_rules = self.optimization_rules.get(platform, {})
        posting_times = optimization_rules.get("best_posting_times", [])
        
        optimal_times = []
        today = datetime.now().date()
        
        for time_rule in posting_times:
            day_name = time_rule.get("day", "monday")
            hours = time_rule.get("hours", [12])
            
            # Calculate next occurrence of this day
            days_ahead = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(day_name)
            target_date = today + timedelta(days=days_ahead)
            
            for hour in hours:
                optimal_time = datetime.combine(target_date, datetime.min.time().replace(hour=hour))
                optimal_times.append(optimal_time)
        
        return sorted(optimal_times)[:5]  # Return next 5 optimal times
    
    def _generate_hashtag_suggestions(
        self,
        platform: Platform,
        content_type: Optional[ContentType]
    ) -> List[str]:
        """Generate platform-appropriate hashtag suggestions"""
        
        hashtags = []
        
        # Platform-specific hashtag strategies
        if platform == Platform.INSTAGRAM:
            if content_type == ContentType.PHOTO:
                hashtags.extend([
                    "#photography", "#photooftheday", "#instagood", "#picoftheday"
                ])
            elif content_type == ContentType.REEL:
                hashtags.extend([
                    "#reels", "#trending", "#viral", "#explore"
                ])
            elif content_type == ContentType.MUSIC_VIDEO:
                hashtags.extend([
                    "#music", "#newmusic", "#artist", "#musicvideo"
                ])
        
        elif platform == Platform.TIKTOK:
            hashtags.extend([
                "#fyp", "#foryou", "#trending", "#viral", "#tiktok"
            ])
            
            if content_type == ContentType.SHORT_VIDEO:
                hashtags.extend([
                    "#content", "#creative", "#original"
                ])
        
        elif platform == Platform.YOUTUBE:
            # YouTube uses tags rather than hashtags, but similar concept
            if content_type == ContentType.MUSIC_VIDEO:
                hashtags.extend([
                    "#music", "#newmusic", "#musicvideo", "#artist"
                ])
        
        return hashtags[:15]  # Limit to reasonable number
    
    def get_platform_best_practices(self, platform: Platform) -> Dict[str, Any]:
        """Get comprehensive best practices for platform"""
        
        optimization_rules = self.optimization_rules.get(platform, {})
        platform_specs = self.platform_specs.get(platform)
        
        best_practices = {
            "content_guidelines": optimization_rules.get("content_strategies", {}),
            "posting_schedule": optimization_rules.get("best_posting_times", []),
            "technical_specs": {
                "max_file_size": f"{platform_specs.max_file_size}MB" if platform_specs else "Unknown",
                "supported_formats": platform_specs.supported_formats if platform_specs else [],
                "aspect_ratios": platform_specs.aspect_ratios if platform_specs else []
            },
            "engagement_tips": self._get_engagement_tips(platform),
            "monetization_requirements": self._get_monetization_requirements(platform)
        }
        
        return best_practices
    
    def _get_engagement_tips(self, platform: Platform) -> List[str]:
        """Get platform-specific engagement tips"""
        
        tips = {
            Platform.INSTAGRAM: [
                "Use Instagram Stories daily",
                "Respond to comments within 2 hours",
                "Use relevant hashtags consistently",
                "Post high-quality visual content",
                "Share behind-the-scenes content"
            ],
            Platform.YOUTUBE: [
                "Upload on a consistent schedule",
                "Create compelling thumbnails",
                "Write detailed descriptions",
                "Use end screens and cards",
                "Engage with comments regularly"
            ],
            Platform.TIKTOK: [
                "Post during peak hours",
                "Use trending sounds and effects",
                "Hook viewers in first 3 seconds",
                "Participate in challenges",
                "Duet with popular content"
            ]
        }
        
        return tips.get(platform, [])
    
    def _get_monetization_requirements(self, platform: Platform) -> Dict[str, Any]:
        """Get platform-specific monetization requirements"""
        
        requirements = {
            Platform.INSTAGRAM: {
                "followers": 1000,
                "content_type": "Professional account required",
                "additional": ["Creator Fund eligibility", "Brand partnership tools"]
            },
            Platform.YOUTUBE: {
                "subscribers": 1000,
                "watch_hours": 4000,
                "additional": ["AdSense account", "Community guidelines compliance"]
            },
            Platform.TIKTOK: {
                "followers": 1000,
                "age_requirement": 18,
                "additional": ["Creator Fund application", "Consistent posting"]
            }
        }
        
        return requirements.get(platform, {})
