"""
Creator Types Configuration - Enterprise Configuration Management
Enterprise configuration for creator type definitions and specialized settings

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


class CreatorCategory(str, Enum):
    """Creator category classifications"""
    ARTISTS = "artists"
    CONTENT_CREATORS = "content_creators"
    ENTERTAINERS = "entertainers"
    EDUCATORS = "educators"
    INFLUENCERS = "influencers"
    PROFESSIONALS = "professionals"


class CreatorSpecialization(str, Enum):
    """Creator specialization types"""
    # Musicians
    SOLO_ARTIST = "solo_artist"
    BAND_MEMBER = "band_member"
    PRODUCER = "producer"
    COMPOSER = "composer"
    SOUND_ENGINEER = "sound_engineer"
    
    # Content Creators
    BLOGGER = "blogger"
    VLOGGER = "vlogger"
    PODCASTER = "podcaster"
    NEWSLETTER_WRITER = "newsletter_writer"
    TECHNICAL_WRITER = "technical_writer"
    
    # Visual Artists
    PHOTOGRAPHER = "photographer"
    VIDEOGRAPHER = "videographer"
    GRAPHIC_DESIGNER = "graphic_designer"
    ANIMATOR = "animator"
    DIGITAL_ARTIST = "digital_artist"
    
    # Entertainers
    COMEDIAN = "comedian"
    ACTOR = "actor"
    DANCER = "dancer"
    MAGICIAN = "magician"
    STREAMER = "streamer"
    
    # Educators
    TEACHER = "teacher"
    TRAINER = "trainer"
    COACH = "coach"
    MENTOR = "mentor"
    ACADEMIC = "academic"


class CreatorExperienceLevel(str, Enum):
    """Creator experience levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"
    EXPERT = "expert"
    MASTER = "master"


class CreatorTier(str, Enum):
    """Creator tier classifications"""
    EMERGING = "emerging"
    GROWING = "growing"
    ESTABLISHED = "established"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    LEGENDARY = "legendary"


@dataclass
class CreatorTypeRequirements:
    """Requirements for specific creator type"""
    minimum_content_quality: str
    required_equipment: List[str]
    technical_skills: List[str]
    business_skills: List[str]
    portfolio_requirements: Dict[str, Any]
    verification_criteria: Dict[str, Any]


@dataclass
class CreatorTypeCapabilities:
    """Capabilities and features for creator type"""
    supported_formats: List[str]
    content_categories: List[str]
    monetization_options: List[str]
    collaboration_features: List[str]
    distribution_channels: List[str]
    ai_assistance_level: str


@dataclass
class CreatorTypeMetrics:
    """Performance metrics for creator type"""
    success_indicators: List[str]
    engagement_metrics: List[str]
    revenue_metrics: List[str]
    growth_metrics: List[str]
    quality_metrics: List[str]


class CreatorTypesSettings:
    """Creator types configuration settings"""
    
    def __init__(self):
        # Creator Type Definitions
        self.creator_types = {
            "musicians": {
                "category": CreatorCategory.ARTISTS,
                "specializations": [
                    CreatorSpecialization.SOLO_ARTIST,
                    CreatorSpecialization.BAND_MEMBER,
                    CreatorSpecialization.PRODUCER,
                    CreatorSpecialization.COMPOSER,
                    CreatorSpecialization.SOUND_ENGINEER
                ],
                "requirements": CreatorTypeRequirements(
                    minimum_content_quality="320kbps audio, stereo",
                    required_equipment=["DAW", "Audio Interface", "Microphone", "Headphones"],
                    technical_skills=["Audio Recording", "Mixing", "Basic Mastering", "File Management"],
                    business_skills=["Copyright Understanding", "Licensing", "Marketing", "Social Media"],
                    portfolio_requirements={
                        "minimum_tracks": 3,
                        "demo_quality": "professional",
                        "genre_consistency": True,
                        "original_content": True
                    },
                    verification_criteria={
                        "identity_verification": True,
                        "rights_verification": True,
                        "quality_assessment": True,
                        "technical_review": True
                    }
                ),
                "capabilities": CreatorTypeCapabilities(
                    supported_formats=["mp3", "wav", "flac", "aac", "mp4"],
                    content_categories=["Music", "Audio", "Video", "Live Performances"],
                    monetization_options=["Streaming", "Licensing", "Merchandise", "Live Events", "Royalties"],
                    collaboration_features=["Remixes", "Features", "Producer Partnerships", "Band Formation"],
                    distribution_channels=["Spotify", "Apple Music", "YouTube", "SoundCloud", "Bandcamp"],
                    ai_assistance_level="advanced"
                ),
                "metrics": CreatorTypeMetrics(
                    success_indicators=["Stream Count", "Downloads", "Fan Growth", "Revenue"],
                    engagement_metrics=["Plays", "Shares", "Comments", "Playlist Adds"],
                    revenue_metrics=["Streaming Revenue", "Licensing Fees", "Merchandise Sales"],
                    growth_metrics=["Follower Growth", "Monthly Listeners", "Geographic Reach"],
                    quality_metrics=["Audio Quality Score", "Production Value", "Originality Score"]
                )
            },
            
            "bloggers": {
                "category": CreatorCategory.CONTENT_CREATORS,
                "specializations": [
                    CreatorSpecialization.BLOGGER,
                    CreatorSpecialization.NEWSLETTER_WRITER,
                    CreatorSpecialization.TECHNICAL_WRITER
                ],
                "requirements": CreatorTypeRequirements(
                    minimum_content_quality="Grade 8 readability, 500+ words",
                    required_equipment=["Computer", "Internet", "Writing Software"],
                    technical_skills=["Writing", "SEO", "Basic HTML", "Content Management"],
                    business_skills=["Content Strategy", "Audience Building", "Email Marketing", "Analytics"],
                    portfolio_requirements={
                        "minimum_posts": 5,
                        "writing_quality": "professional",
                        "niche_expertise": True,
                        "original_content": True
                    },
                    verification_criteria={
                        "identity_verification": True,
                        "writing_samples": True,
                        "niche_knowledge": True,
                        "plagiarism_check": True
                    }
                ),
                "capabilities": CreatorTypeCapabilities(
                    supported_formats=["markdown", "html", "pdf", "docx", "txt"],
                    content_categories=["Articles", "Tutorials", "Reviews", "News", "Opinion Pieces"],
                    monetization_options=["Advertising", "Affiliate Marketing", "Subscriptions", "Courses"],
                    collaboration_features=["Guest Posts", "Content Partnerships", "Cross Promotion"],
                    distribution_channels=["Personal Blog", "Medium", "LinkedIn", "Newsletter Platforms"],
                    ai_assistance_level="standard"
                ),
                "metrics": CreatorTypeMetrics(
                    success_indicators=["Page Views", "Subscribers", "Engagement Rate", "Revenue"],
                    engagement_metrics=["Comments", "Shares", "Time on Page", "Return Visitors"],
                    revenue_metrics=["Ad Revenue", "Affiliate Commissions", "Subscription Income"],
                    growth_metrics=["Subscriber Growth", "Traffic Growth", "Social Media Following"],
                    quality_metrics=["Readability Score", "SEO Score", "Engagement Quality"]
                )
            },
            
            "photographers": {
                "category": CreatorCategory.ARTISTS,
                "specializations": [
                    CreatorSpecialization.PHOTOGRAPHER,
                    CreatorSpecialization.DIGITAL_ARTIST
                ],
                "requirements": CreatorTypeRequirements(
                    minimum_content_quality="2048x2048 minimum, high resolution",
                    required_equipment=["Camera", "Lenses", "Editing Software", "Computer"],
                    technical_skills=["Photography", "Photo Editing", "Color Theory", "Composition"],
                    business_skills=["Portfolio Management", "Client Relations", "Pricing", "Licensing"],
                    portfolio_requirements={
                        "minimum_images": 10,
                        "image_quality": "professional",
                        "style_consistency": True,
                        "technical_excellence": True
                    },
                    verification_criteria={
                        "identity_verification": True,
                        "portfolio_review": True,
                        "technical_assessment": True,
                        "rights_verification": True
                    }
                ),
                "capabilities": CreatorTypeCapabilities(
                    supported_formats=["jpeg", "png", "tiff", "raw", "webp"],
                    content_categories=["Photography", "Digital Art", "Stock Images", "Portfolio"],
                    monetization_options=["Stock Sales", "Print Sales", "Licensing", "NFTs", "Commissions"],
                    collaboration_features=["Model Partnerships", "Brand Collaborations", "Event Coverage"],
                    distribution_channels=["Instagram", "Behance", "Stock Sites", "Gallery Websites"],
                    ai_assistance_level="enhanced"
                ),
                "metrics": CreatorTypeMetrics(
                    success_indicators=["Sales", "Downloads", "Portfolio Views", "Client Bookings"],
                    engagement_metrics=["Likes", "Comments", "Shares", "Portfolio Views"],
                    revenue_metrics=["Stock Revenue", "Commission Income", "Print Sales"],
                    growth_metrics=["Follower Growth", "Portfolio Expansion", "Client Base Growth"],
                    quality_metrics=["Technical Quality", "Artistic Merit", "Commercial Viability"]
                )
            },
            
            "influencers": {
                "category": CreatorCategory.INFLUENCERS,
                "specializations": [
                    CreatorSpecialization.INFLUENCER,
                    CreatorSpecialization.CONTENT_CREATOR
                ],
                "requirements": CreatorTypeRequirements(
                    minimum_content_quality="High engagement rate, consistent posting",
                    required_equipment=["Smartphone/Camera", "Editing Apps", "Lighting Equipment"],
                    technical_skills=["Content Creation", "Video Editing", "Social Media Management"],
                    business_skills=["Brand Partnerships", "Audience Engagement", "Personal Branding"],
                    portfolio_requirements={
                        "minimum_followers": 1000,
                        "engagement_rate": "3%+",
                        "content_consistency": True,
                        "niche_authority": True
                    },
                    verification_criteria={
                        "identity_verification": True,
                        "follower_verification": True,
                        "engagement_verification": True,
                        "content_quality_review": True
                    }
                ),
                "capabilities": CreatorTypeCapabilities(
                    supported_formats=["jpeg", "png", "mp4", "mov", "stories"],
                    content_categories=["Lifestyle", "Fashion", "Technology", "Entertainment", "Education"],
                    monetization_options=["Sponsored Content", "Affiliate Marketing", "Brand Partnerships", "Merchandise"],
                    collaboration_features=["Brand Campaigns", "Influencer Networks", "Cross Promotion"],
                    distribution_channels=["Instagram", "TikTok", "YouTube", "Twitter", "Snapchat"],
                    ai_assistance_level="advanced"
                ),
                "metrics": CreatorTypeMetrics(
                    success_indicators=["Follower Count", "Engagement Rate", "Brand Partnerships", "Revenue"],
                    engagement_metrics=["Likes", "Comments", "Shares", "Story Views", "Saves"],
                    revenue_metrics=["Sponsored Post Revenue", "Affiliate Commissions", "Merchandise Sales"],
                    growth_metrics=["Follower Growth", "Reach Growth", "Engagement Growth"],
                    quality_metrics=["Content Quality", "Audience Quality", "Brand Alignment"]
                )
            },
            
            "comedians": {
                "category": CreatorCategory.ENTERTAINERS,
                "specializations": [
                    CreatorSpecialization.COMEDIAN,
                    CreatorSpecialization.ENTERTAINER
                ],
                "requirements": CreatorTypeRequirements(
                    minimum_content_quality="Professional audio/video quality",
                    required_equipment=["Microphone", "Camera", "Editing Software"],
                    technical_skills=["Performance", "Timing", "Content Creation", "Audience Engagement"],
                    business_skills=["Show Booking", "Merchandise", "Social Media", "Audience Building"],
                    portfolio_requirements={
                        "minimum_content": 5,
                        "performance_quality": "professional",
                        "originality": True,
                        "audience_appeal": True
                    },
                    verification_criteria={
                        "identity_verification": True,
                        "performance_review": True,
                        "originality_check": True,
                        "audience_feedback": True
                    }
                ),
                "capabilities": CreatorTypeCapabilities(
                    supported_formats=["mp4", "mp3", "mov", "wav"],
                    content_categories=["Stand-up", "Sketches", "Podcasts", "Live Performances"],
                    monetization_options=["Show Tickets", "Streaming Specials", "Merchandise", "Podcasts"],
                    collaboration_features=["Comedy Partnerships", "Writing Collaborations", "Tour Coordination"],
                    distribution_channels=["YouTube", "Netflix", "Podcast Platforms", "Social Media"],
                    ai_assistance_level="standard"
                ),
                "metrics": CreatorTypeMetrics(
                    success_indicators=["Show Attendance", "Video Views", "Subscriber Growth", "Revenue"],
                    engagement_metrics=["Laughs per Minute", "Audience Retention", "Comments", "Shares"],
                    revenue_metrics=["Ticket Sales", "Streaming Revenue", "Merchandise Sales"],
                    growth_metrics=["Audience Growth", "Show Bookings", "Social Media Following"],
                    quality_metrics=["Performance Quality", "Originality Score", "Audience Satisfaction"]
                )
            }
        }
        
        # Creator Type Settings
        self.type_verification_enabled = True
        self.tier_progression_enabled = True
        self.specialization_tracking = True
        self.cross_type_collaboration = True
        
        # Performance Settings
        self.metrics_calculation_interval = "daily"
        self.tier_evaluation_interval = "monthly"
        self.quality_assessment_frequency = "weekly"
        
        # Business Logic Settings
        self.automatic_tier_promotion = True
        self.creator_matching_enabled = True
        self.recommendation_system_enabled = True
        self.analytics_tracking_enabled = True
    
    def get_creator_type_config(self, creator_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific creator type"""
        return self.creator_types.get(creator_type)
    
    def get_supported_specializations(self, creator_type: str) -> List[CreatorSpecialization]:
        """Get supported specializations for creator type"""
        config = self.get_creator_type_config(creator_type)
        return config.get("specializations", []) if config else []
    
    def get_creator_requirements(self, creator_type: str) -> Optional[CreatorTypeRequirements]:
        """Get requirements for creator type"""
        config = self.get_creator_type_config(creator_type)
        return config.get("requirements") if config else None
    
    def get_creator_capabilities(self, creator_type: str) -> Optional[CreatorTypeCapabilities]:
        """Get capabilities for creator type"""
        config = self.get_creator_type_config(creator_type)
        return config.get("capabilities") if config else None
    
    def validate_creator_type(self, creator_type: str) -> bool:
        """Validate if creator type is supported"""
        return creator_type in self.creator_types
    
    def get_all_creator_types(self) -> List[str]:
        """Get all supported creator types"""
        return list(self.creator_types.keys())
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete creator types configuration"""
        errors = []
        
        for creator_type, config in self.creator_types.items():
            if "requirements" not in config:
                errors.append(f"Creator type '{creator_type}' missing requirements")
            if "capabilities" not in config:
                errors.append(f"Creator type '{creator_type}' missing capabilities")
            if "metrics" not in config:
                errors.append(f"Creator type '{creator_type}' missing metrics")
        
        return errors


# Global creator types settings instance
creator_types_settings = CreatorTypesSettings()

__all__ = [
    "CreatorTypesSettings",
    "creator_types_settings",
    "CreatorCategory",
    "CreatorSpecialization", 
    "CreatorExperienceLevel",
    "CreatorTier",
    "CreatorTypeRequirements",
    "CreatorTypeCapabilities",
    "CreatorTypeMetrics"
]