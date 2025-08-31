"""IA Influencer Agent - Creator-Specific Configurations
====================================================

Configuration settings and presets for different creator types,
optimized for their specific content and workflow requirements.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de
"""from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

from .specialized_services import CreatorType, ContentCategory


@dataclass
class CreatorConfigPreset:
    """Configuration preset for specific creator types"""    creator_type: CreatorType
    supported_formats: List[str]
    priority_algorithms: List[str]
    seo_optimization: Dict[str, Any]
    content_categories: List[ContentCategory]
    platform_preferences: List[str]
    monetization_features: Dict[str, bool]
    collaboration_features: Dict[str, bool]
    protection_level: str
    processing_optimization: Dict[str, Any]


class CreatorConfigurations:
    """Predefined configurations for different creator types"""    
    MUSICIAN_CONFIG = CreatorConfigPreset(
        creator_type=CreatorType.MUSICIAN,
        supported_formats=["mp3", "wav", "flac", "m4a", "aiff"],
        priority_algorithms=["audio_fingerprinting", "tempo_detection", "key_detection", "mood_analysis"],
        seo_optimization={
            "keywords_focus": ["music", "song", "artist", "genre", "tempo", "key"],
            "metadata_enhancement": True,
            "auto_tagging": True,
            "genre_classification": True
        },
        content_categories=[
            ContentCategory.SONG, ContentCategory.ALBUM, 
            ContentCategory.LIVE_PERFORMANCE, ContentCategory.MUSIC_VIDEO
        ],
        platform_preferences=["spotify", "apple_music", "youtube_music", "soundcloud", "bandcamp"],
        monetization_features={
            "royalty_tracking": True,
            "streaming_analytics": True,
            "licensing_management": True,
            "sync_opportunities": True
        },
        collaboration_features={
            "producer_matching": True,
            "vocalist_matching": True,
            "remix_opportunities": True,
            "live_performance_booking": True
        },
        protection_level="premium",
        processing_optimization={
            "audio_quality_priority": "high",
            "fingerprint_sensitivity": 0.85,
            "batch_processing": True,
            "real_time_analysis": True
        }
    )
    
    BLOGGER_CONFIG = CreatorConfigPreset(
        creator_type=CreatorType.BLOGGER,
        supported_formats=["txt", "md", "html", "docx", "pdf"],
        priority_algorithms=["text_analysis", "sentiment_analysis", "topic_modeling", "readability_scoring"],
        seo_optimization={
            "keywords_focus": ["article", "blog", "content", "writing", "topic", "niche"],
            "keyword_extraction": True,
            "semantic_analysis": True,
            "content_optimization": True
        },
        content_categories=[
            ContentCategory.ARTICLE, ContentCategory.TUTORIAL, 
            ContentCategory.REVIEW, ContentCategory.NEWS
        ],
        platform_preferences=["medium", "substack", "wordpress", "ghost", "linkedin"],
        monetization_features={
            "subscription_management": True,
            "sponsored_content": True,
            "affiliate_tracking": True,
            "newsletter_analytics": True
        },
        collaboration_features={
            "guest_posting": True,
            "content_syndication": True,
            "expert_interviews": True,
            "collaborative_articles": True
        },
        protection_level="standard",
        processing_optimization={
            "text_quality_priority": "high",
            "language_detection": True,
            "plagiarism_checking": True,
            "content_summarization": True
        }
    )
    
    PHOTOGRAPHER_CONFIG = CreatorConfigPreset(
        creator_type=CreatorType.PHOTOGRAPHER,
        supported_formats=["jpg", "jpeg", "png", "tiff", "raw", "dng", "cr2", "nef"],
        priority_algorithms=["image_fingerprinting", "object_detection", "style_analysis", "composition_analysis"],
        seo_optimization={
            "keywords_focus": ["photography", "photo", "image", "visual", "composition", "style"],
            "visual_tagging": True,
            "style_classification": True,
            "location_tagging": True
        },
        content_categories=[
            ContentCategory.PHOTO, ContentCategory.PORTFOLIO, 
            ContentCategory.ARTWORK, ContentCategory.DESIGN
        ],
        platform_preferences=["instagram", "pinterest", "behance", "flickr", "500px"],
        monetization_features={
            "print_sales": True,
            "stock_photography": True,
            "commissioned_work": True,
            "workshop_booking": True
        },
        collaboration_features={
            "model_booking": True,
            "venue_partnerships": True,
            "brand_collaborations": True,
            "exhibition_opportunities": True
        },
        protection_level="premium",
        processing_optimization={
            "image_quality_priority": "highest",
            "metadata_preservation": True,
            "watermark_detection": True,
            "duplicate_detection": True
        }
    )
    
    INFLUENCER_CONFIG = CreatorConfigPreset(
        creator_type=CreatorType.INFLUENCER,
        supported_formats=["mp4", "mov", "jpg", "jpeg", "png", "gif", "mp3"],
        priority_algorithms=["multi_modal_analysis", "engagement_prediction", "trend_detection", "audience_analysis"],
        seo_optimization={
            "keywords_focus": ["influencer", "social", "viral", "trending", "engagement", "brand"],
            "hashtag_optimization": True,
            "trend_alignment": True,
            "audience_targeting": True
        },
        content_categories=[
            ContentCategory.VLOG, ContentCategory.SHORT_VIDEO, 
            ContentCategory.PHOTO, ContentCategory.INTERVIEW
        ],
        platform_preferences=["instagram", "tiktok", "youtube", "twitter", "snapchat"],
        monetization_features={
            "brand_partnerships": True,
            "sponsored_content": True,
            "merchandise_sales": True,
            "fan_subscriptions": True
        },
        collaboration_features={
            "brand_matching": True,
            "cross_promotion": True,
            "event_partnerships": True,
            "product_collaborations": True
        },
        protection_level="premium",
        processing_optimization={
            "multi_format_support": True,
            "viral_potential_analysis": True,
            "engagement_optimization": True,
            "platform_specific_optimization": True
        }
    )
    
    COMEDIAN_CONFIG = CreatorConfigPreset(
        creator_type=CreatorType.COMEDIAN,
        supported_formats=["mp4", "mov", "mp3", "wav", "txt", "pdf"],
        priority_algorithms=["humor_analysis", "timing_analysis", "audience_reaction", "content_classification"],
        seo_optimization={
            "keywords_focus": ["comedy", "humor", "funny", "standup", "entertainment", "jokes"],
            "humor_tagging": True,
            "content_rating": True,
            "audience_appropriateness": True
        },
        content_categories=[
            ContentCategory.STANDUP, ContentCategory.SKETCH, 
            ContentCategory.MEME, ContentCategory.PARODY
        ],
        platform_preferences=["youtube", "instagram", "tiktok", "twitter", "twitch"],
        monetization_features={
            "show_booking": True,
            "merchandise_sales": True,
            "streaming_revenue": True,
            "corporate_gigs": True
        },
        collaboration_features={
            "comedy_partnerships": True,
            "roast_battles": True,
            "podcast_appearances": True,
            "venue_bookings": True
        },
        protection_level="standard",
        processing_optimization={
            "content_moderation": True,
            "timing_analysis": True,
            "audience_feedback": True,
            "performance_metrics": True
        }
    )
    
    PODCASTER_CONFIG = CreatorConfigPreset(
        creator_type=CreatorType.PODCASTER,
        supported_formats=["mp3", "wav", "m4a", "mp4", "mov"],
        priority_algorithms=["speech_analysis", "topic_extraction", "speaker_identification", "content_segmentation"],
        seo_optimization={
            "keywords_focus": ["podcast", "audio", "interview", "discussion", "topic", "episode"],
            "transcript_optimization": True,
            "topic_tagging": True,
            "speaker_identification": True
        },
        content_categories=[
            ContentCategory.INTERVIEW, ContentCategory.DOCUMENTARY,
            ContentCategory.TUTORIAL, ContentCategory.NEWS
        ],
        platform_preferences=["spotify", "apple_podcasts", "google_podcasts", "youtube", "anchor"],
        monetization_features={
            "sponsorship_management": True,
            "subscription_tiers": True,
            "merchandise_integration": True,
            "live_show_booking": True
        },
        collaboration_features={
            "guest_booking": True,
            "cross_podcast_promotion": True,
            "sponsor_matching": True,
            "network_partnerships": True
        },
        protection_level="standard",
        processing_optimization={
            "audio_quality_enhancement": True,
            "noise_reduction": True,
            "transcript_generation": True,
            "chapter_segmentation": True
        }
    )
    
    VIDEO_CREATOR_CONFIG = CreatorConfigPreset(
        creator_type=CreatorType.VIDEO_CREATOR,
        supported_formats=["mp4", "mov", "avi", "mkv", "webm", "m4v"],
        priority_algorithms=["video_analysis", "scene_detection", "object_tracking", "quality_assessment"],
        seo_optimization={
            "keywords_focus": ["video", "content", "creator", "youtube", "streaming", "entertainment"],
            "thumbnail_optimization": True,
            "title_optimization": True,
            "description_enhancement": True
        },
        content_categories=[
            ContentCategory.VLOG, ContentCategory.DOCUMENTARY,
            ContentCategory.TUTORIAL, ContentCategory.INTERVIEW
        ],
        platform_preferences=["youtube", "vimeo", "twitch", "instagram", "tiktok"],
        monetization_features={
            "ad_revenue": True,
            "channel_memberships": True,
            "super_chat": True,
            "brand_integrations": True
        },
        collaboration_features={
            "creator_collaborations": True,
            "brand_partnerships": True,
            "guest_appearances": True,
            "cross_platform_promotion": True
        },
        protection_level="premium",
        processing_optimization={
            "video_quality_priority": "high",
            "compression_optimization": True,
            "thumbnail_generation": True,
            "preview_generation": True
        }
    )
    
    ARTIST_CONFIG = CreatorConfigPreset(
        creator_type=CreatorType.ARTIST,
        supported_formats=["jpg", "jpeg", "png", "tiff", "pdf", "ai", "psd", "svg"],
        priority_algorithms=["artistic_analysis", "style_detection", "color_analysis", "composition_evaluation"],
        seo_optimization={
            "keywords_focus": ["art", "artist", "artwork", "creative", "design", "visual"],
            "style_classification": True,
            "color_palette_extraction": True,
            "technique_identification": True
        },
        content_categories=[
            ContentCategory.ARTWORK, ContentCategory.DESIGN,
            ContentCategory.PORTFOLIO, ContentCategory.PHOTO
        ],
        platform_preferences=["instagram", "behance", "artstation", "deviantart", "pinterest"],
        monetization_features={
            "art_sales": True,
            "commission_work": True,
            "print_on_demand": True,
            "gallery_representation": True
        },
        collaboration_features={
            "artist_collaborations": True,
            "gallery_partnerships": True,
            "brand_design_work": True,
            "exhibition_opportunities": True
        },
        protection_level="premium",
        processing_optimization={
            "high_resolution_support": True,
            "color_accuracy": True,
            "style_preservation": True,
            "metadata_retention": True
        }
    )
    
    @classmethod
    def get_config(cls, creator_type: CreatorType) -> CreatorConfigPreset:
        """Get configuration for specific creator type"""        configs = {
            CreatorType.MUSICIAN: cls.MUSICIAN_CONFIG,
            CreatorType.BLOGGER: cls.BLOGGER_CONFIG,
            CreatorType.PHOTOGRAPHER: cls.PHOTOGRAPHER_CONFIG,
            CreatorType.INFLUENCER: cls.INFLUENCER_CONFIG,
            CreatorType.COMEDIAN: cls.COMEDIAN_CONFIG,
            CreatorType.PODCASTER: cls.PODCASTER_CONFIG,
            CreatorType.VIDEO_CREATOR: cls.VIDEO_CREATOR_CONFIG,
            CreatorType.ARTIST: cls.ARTIST_CONFIG
        }
        
        return configs.get(creator_type, cls.INFLUENCER_CONFIG)  # Default fallback
    
    @classmethod
    def get_all_configs(cls) -> Dict[CreatorType, CreatorConfigPreset]:
        """Get all creator configurations"""        return {
            CreatorType.MUSICIAN: cls.MUSICIAN_CONFIG,
            CreatorType.BLOGGER: cls.BLOGGER_CONFIG,
            CreatorType.PHOTOGRAPHER: cls.PHOTOGRAPHER_CONFIG,
            CreatorType.INFLUENCER: cls.INFLUENCER_CONFIG,
            CreatorType.COMEDIAN: cls.COMEDIAN_CONFIG,
            CreatorType.PODCASTER: cls.PODCASTER_CONFIG,
            CreatorType.VIDEO_CREATOR: cls.VIDEO_CREATOR_CONFIG,
            CreatorType.ARTIST: cls.ARTIST_CONFIG
        }
    
    @classmethod
    def get_supported_formats_by_type(cls, creator_type: CreatorType) -> List[str]:
        """Get supported file formats for creator type"""        config = cls.get_config(creator_type)
        return config.supported_formats
    
    @classmethod
    def get_platform_preferences_by_type(cls, creator_type: CreatorType) -> List[str]:
        """Get platform preferences for creator type"""        config = cls.get_config(creator_type)
        return config.platform_preferences
    
    @classmethod
    def get_monetization_features_by_type(cls, creator_type: CreatorType) -> Dict[str, bool]:
        """Get monetization features for creator type"""        config = cls.get_config(creator_type)
        return config.monetization_features
    
    @classmethod
    def get_collaboration_features_by_type(cls, creator_type: CreatorType) -> Dict[str, bool]:
        """Get collaboration features for creator type"""        config = cls.get_config(creator_type)
        return config.collaboration_features


class PlatformOptimizations:
    """Platform-specific optimization settings"""    
    PLATFORM_SPECS = {
        "spotify": {
            "audio_formats": ["mp3", "wav", "flac"],
            "quality_requirements": {"bitrate": 320, "sample_rate": 44100},
            "metadata_fields": ["title", "artist", "album", "genre", "bpm", "key"],
            "content_guidelines": {"explicit_content_allowed": True, "max_duration": 600}
        },
        "youtube": {
            "video_formats": ["mp4", "mov", "avi"],
            "quality_requirements": {"resolution": "1080p", "fps": 30, "bitrate": 8000},
            "thumbnail_specs": {"size": "1280x720", "format": "jpg"},
            "content_guidelines": {"family_friendly_preferred": True, "max_duration": 43200}
        },
        "instagram": {
            "image_formats": ["jpg", "jpeg", "png"],
            "video_formats": ["mp4", "mov"],
            "quality_requirements": {"aspect_ratios": ["1:1", "4:5", "9:16"], "max_size": "100MB"},
            "content_guidelines": {"vertical_preferred": True, "max_duration": 60}
        },
        "tiktok": {
            "video_formats": ["mp4", "mov"],
            "quality_requirements": {"aspect_ratio": "9:16", "resolution": "1080x1920", "fps": 30},
            "content_guidelines": {"vertical_only": True, "max_duration": 180, "trending_sounds": True}
        },
        "medium": {
            "text_formats": ["md", "html", "txt"],
            "image_formats": ["jpg", "jpeg", "png", "gif"],
            "quality_requirements": {"reading_time": "5-15 minutes", "word_count": "1000-3000"},
            "content_guidelines": {"professional_tone": True, "citations_encouraged": True}
        },
        "behance": {
            "image_formats": ["jpg", "jpeg", "png", "gif"],
            "video_formats": ["mp4", "mov"],
            "quality_requirements": {"high_resolution": True, "portfolio_quality": True},
            "content_guidelines": {"creative_work_only": True, "project_documentation": True}
        }
    }
    
    @classmethod
    def get_platform_specs(cls, platform: str) -> Dict[str, Any]:
        """Get specifications for specific platform"""        return cls.PLATFORM_SPECS.get(platform, {})
    
    @classmethod
    def get_optimal_formats_for_platform(cls, platform: str) -> List[str]:
        """Get optimal file formats for platform"""        specs = cls.get_platform_specs(platform)
        formats = []
        
        if "audio_formats" in specs:
            formats.extend(specs["audio_formats"])
        if "video_formats" in specs:
            formats.extend(specs["video_formats"])
        if "image_formats" in specs:
            formats.extend(specs["image_formats"])
        if "text_formats" in specs:
            formats.extend(specs["text_formats"])
            
        return formats
