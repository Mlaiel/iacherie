"""Compression Profile Manager
Predefined compression profiles for different use cases and platforms.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import json
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

class Platform(Enum):
    """Supported platforms for compression optimization."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    WEB = "web"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    STREAMING = "streaming"
    ARCHIVE = "archive"

@dataclass
class CompressionProfile:
    """Compression profile definition."""
    name: str
    description: str
    platform: Optional[Platform]
    media_type: str  # audio, video, image
    format: str
    quality: Union[int, str]
    additional_settings: Dict[str, Any]
    use_cases: List[str]
    estimated_savings: str
    quality_impact: str

class CompressionProfileManager:
    """Manager for compression profiles and platform optimizations."""
    
    def __init__(self):
        """Initialize the profile manager."""
        self.profiles = self._load_default_profiles()
        self.custom_profiles = {}
        
    def _load_default_profiles(self) -> Dict[str, CompressionProfile]:
        """Load default compression profiles."""
        profiles = {}
        
        # Audio profiles
        profiles["audio_podcast"] = CompressionProfile(
            name="Podcast Optimized",
            description="Optimized for voice content and long-form audio",
            platform=None,
            media_type="audio",
            format="mp3",
            quality=64,
            additional_settings={
                "channels": 1,
                "sample_rate": 22050,
                "normalize": True,
                "noise_reduction": True
            },
            use_cases=["podcasts", "audiobooks", "voice recordings"],
            estimated_savings="70-80%",
            quality_impact="Minimal for speech"
        )
        
        profiles["audio_music_streaming"] = CompressionProfile(
            name="Music Streaming",
            description="Balanced quality for music streaming services",
            platform=Platform.STREAMING,
            media_type="audio",
            format="aac",
            quality=256,
            additional_settings={
                "channels": 2,
                "sample_rate": 44100,
                "variable_bitrate": True
            },
            use_cases=["music streaming", "radio", "background music"],
            estimated_savings="60-70%",
            quality_impact="Minimal for most listeners"
        )
        
        # Video profiles
        profiles["video_youtube_1080p"] = CompressionProfile(
            name="YouTube 1080p",
            description="Optimized for YouTube 1080p uploads",
            platform=Platform.YOUTUBE,
            media_type="video",
            format="h264",
            quality="high",
            additional_settings={
                "resolution": (1920, 1080),
                "bitrate": 8000,
                "fps": 30,
                "audio_codec": "aac",
                "audio_bitrate": 128
            },
            use_cases=["youtube uploads", "content creation", "tutorials"],
            estimated_savings="40-60%",
            quality_impact="Minimal"
        )
        
        profiles["video_social_vertical"] = CompressionProfile(
            name="Social Media Vertical",
            description="Optimized for vertical social media content",
            platform=Platform.TIKTOK,
            media_type="video",
            format="h264",
            quality="medium",
            additional_settings={
                "resolution": (1080, 1920),
                "bitrate": 2500,
                "fps": 30,
                "max_duration": 60
            },
            use_cases=["tiktok", "instagram stories", "reels"],
            estimated_savings="50-70%",
            quality_impact="Low"
        )
        
        # Image profiles
        profiles["image_web_modern"] = CompressionProfile(
            name="Modern Web",
            description="Next-gen formats for modern web browsers",
            platform=Platform.WEB,
            media_type="image",
            format="avif",
            quality=85,
            additional_settings={
                "progressive": True,
                "optimize": True,
                "fallback_format": "webp"
            },
            use_cases=["websites", "web apps", "e-commerce"],
            estimated_savings="50-70%",
            quality_impact="None"
        )
        
        profiles["image_social_square"] = CompressionProfile(
            name="Social Media Square",
            description="Square format for social media posts",
            platform=Platform.INSTAGRAM,
            media_type="image",
            format="jpeg",
            quality=80,
            additional_settings={
                "resize": (1080, 1080),
                "progressive": True,
                "strip_metadata": True
            },
            use_cases=["instagram posts", "facebook posts", "social sharing"],
            estimated_savings="30-50%",
            quality_impact="Minimal"
        )
        
        return profiles
    
    def get_profile(self, profile_name: str) -> Optional[CompressionProfile]:
        """Get compression profile by name."""
        profile = self.profiles.get(profile_name)
        if not profile:
            profile = self.custom_profiles.get(profile_name)
        return profile
    
    def get_profiles_by_platform(self, platform: Platform) -> List[CompressionProfile]:
        """Get all profiles optimized for a specific platform."""
        platform_profiles = []
        
        for profile in self.profiles.values():
            if profile.platform == platform:
                platform_profiles.append(profile)
                
        for profile in self.custom_profiles.values():
            if profile.platform == platform:
                platform_profiles.append(profile)
                
        return platform_profiles
    
    def get_profiles_by_media_type(self, media_type: str) -> List[CompressionProfile]:
        """Get all profiles for a specific media type."""
        media_profiles = []
        
        for profile in self.profiles.values():
            if profile.media_type == media_type:
                media_profiles.append(profile)
                
        for profile in self.custom_profiles.values():
            if profile.media_type == media_type:
                media_profiles.append(profile)
                
        return media_profiles
    
    def create_custom_profile(
        self,
        name: str,
        description: str,
        media_type: str,
        format: str,
        quality: Union[int, str],
        additional_settings: Dict[str, Any],
        platform: Optional[Platform] = None,
        use_cases: Optional[List[str]] = None,
        estimated_savings: str = "Unknown",
        quality_impact: str = "Unknown"
    ) -> CompressionProfile:
        """Create a custom compression profile."""
        profile = CompressionProfile(
            name=name,
            description=description,
            platform=platform,
            media_type=media_type,
            format=format,
            quality=quality,
            additional_settings=additional_settings,
            use_cases=use_cases or [],
            estimated_savings=estimated_savings,
            quality_impact=quality_impact
        )
        
        self.custom_profiles[name] = profile
        return profile
    
    def save_custom_profiles(self, file_path: Union[str, Path]) -> bool:
        """Save custom profiles to file."""
        try:
            profiles_data = {}
            for name, profile in self.custom_profiles.items():
                profile_dict = asdict(profile)
                if profile_dict['platform']:
                    profile_dict['platform'] = profile_dict['platform'].value
                profiles_data[name] = profile_dict
            
            with open(file_path, 'w') as f:
                json.dump(profiles_data, f, indent=2)
            
            logger.info(f"Saved {len(profiles_data)} custom profiles to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save custom profiles: {e}")
            return False
    
    def load_custom_profiles(self, file_path: Union[str, Path]) -> bool:
        """Load custom profiles from file."""
        try:
            with open(file_path, 'r') as f:
                profiles_data = json.load(f)
            
            for name, profile_dict in profiles_data.items():
                if profile_dict['platform']:
                    profile_dict['platform'] = Platform(profile_dict['platform'])
                else:
                    profile_dict['platform'] = None
                    
                profile = CompressionProfile(**profile_dict)
                self.custom_profiles[name] = profile
            
            logger.info(f"Loaded {len(profiles_data)} custom profiles from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load custom profiles: {e}")
            return False
    
    def recommend_profile(
        self,
        media_type: str,
        target_platform: Optional[Platform] = None,
        use_case: Optional[str] = None,
        file_size: Optional[int] = None
    ) -> List[CompressionProfile]:
        """Recommend compression profiles based on criteria."""
        candidates = self.get_profiles_by_media_type(media_type)
        
        # Filter by platform if specified
        if target_platform:
            platform_matches = [p for p in candidates if p.platform == target_platform]
            if platform_matches:
                candidates = platform_matches
        
        # Filter by use case if specified
        if use_case:
            use_case_matches = [p for p in candidates if use_case.lower() in [uc.lower() for uc in p.use_cases]]
            if use_case_matches:
                candidates = use_case_matches
        
        # Sort by estimated savings (prioritize higher savings)
        candidates.sort(key=lambda p: self._parse_savings_percentage(p.estimated_savings), reverse=True)
        
        return candidates[:3]  # Return top 3 recommendations
    
    def _parse_savings_percentage(self, savings_str: str) -> float:
        """Parse savings percentage from string."""
        try:
            # Extract number from strings like "50-70%" or "60%"
            import re
            numbers = re.findall(r'\d+', savings_str)
            if numbers:
                # If range, take the average
                if len(numbers) >= 2:
                    return (int(numbers[0]) + int(numbers[1])) / 2
                else:
                    return int(numbers[0])
            return 0
        except:
            return 0
    
    def get_platform_requirements(self, platform: Platform) -> Dict[str, Any]:
        """Get technical requirements for a specific platform."""
        requirements = {
            Platform.YOUTUBE: {
                "video": {
                    "max_file_size": "256GB",
                    "max_duration": "12 hours",
                    "recommended_formats": ["MP4", "MOV"],
                    "recommended_codecs": ["H.264", "H.265"],
                    "max_resolution": "8K",
                    "recommended_bitrates": {
                        "1080p": "8 Mbps",
                        "4K": "35-45 Mbps"
                    }
                },
                "audio": {
                    "recommended_codec": "AAC",
                    "recommended_bitrate": "128 kbps",
                    "sample_rate": "44.1 kHz or 48 kHz"
                }
            },
            Platform.INSTAGRAM: {
                "video": {
                    "max_file_size": "4GB",
                    "max_duration": {
                        "feed": "60 seconds",
                        "stories": "15 seconds",
                        "reels": "90 seconds"
                    },
                    "aspect_ratios": {
                        "feed": "1:1 to 4:5",
                        "stories": "9:16",
                        "reels": "9:16"
                    },
                    "recommended_resolution": {
                        "feed": "1080x1080",
                        "stories": "1080x1920",
                        "reels": "1080x1920"
                    }
                },
                "image": {
                    "max_file_size": "30MB",
                    "recommended_resolution": "1080x1080",
                    "aspect_ratios": "1:1 to 4:5"
                }
            },
            Platform.TIKTOK: {
                "video": {
                    "max_file_size": "287MB",
                    "max_duration": "10 minutes",
                    "aspect_ratio": "9:16",
                    "recommended_resolution": "1080x1920",
                    "recommended_bitrate": "2-4 Mbps",
                    "recommended_fps": "30 fps"
                }
            }
        }
        
        return requirements.get(platform, {})
    
    def validate_profile_for_platform(
        self,
        profile: CompressionProfile,
        platform: Platform
    ) -> Dict[str, Any]:
        """Validate if a profile meets platform requirements."""
        requirements = self.get_platform_requirements(platform)
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # This would contain actual validation logic
        # For now, return a basic validation
        if profile.media_type not in requirements:
            validation_result["warnings"].append(
                f"No specific requirements found for {profile.media_type} on {platform.value}"
            )
        
        return validation_result