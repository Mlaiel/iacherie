"""Platform Optimization Configuration Module for IA-Influencer Agent Platform
===========================================================================

Multi-platform audio optimization configuration for content creators and influencers.
Provides specialized audio processing profiles for different streaming platforms,
social media, and content distribution networks.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
⚠️ STRICT COPYRIGHT WARNING ⚠️
This code and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""import logging
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
import numpy as np

logger = logging.getLogger(__name__)


class StreamingPlatform(Enum):
    """Supported streaming and content platforms"""    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    YOUTUBE_MUSIC = "youtube_music"
    AMAZON_MUSIC = "amazon_music"
    TIDAL = "tidal"
    DEEZER = "deezer"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    TWITCH = "twitch"
    DISCORD = "discord"
    PODCAST_APPLE = "podcast_apple"
    PODCAST_SPOTIFY = "podcast_spotify"
    PODCAST_GOOGLE = "podcast_google"


class ContentType(Enum):
    """Content type optimization"""    MUSIC_TRACK = "music_track"
    PODCAST_EPISODE = "podcast_episode"
    AUDIOBOOK_CHAPTER = "audiobook_chapter"
    SOCIAL_MEDIA_CLIP = "social_media_clip"
    ADVERTISEMENT = "advertisement"
    BACKGROUND_MUSIC = "background_music"
    VOICE_OVER = "voice_over"
    SOUND_EFFECT = "sound_effect"
    LIVE_STREAM = "live_stream"
    SHORT_FORM_VIDEO = "short_form_video"


class LoudnessStandard(Enum):
    """International loudness standards"""    EBU_R128 = "ebu_r128"          # -23 LUFS (Europe)
    ATSC_A85 = "atsc_a85"          # -24 LUFS (North America)
    ARIB_TR_B32 = "arib_tr_b32"    # -24 LUFS (Japan)
    ITU_R_BS1770 = "itu_r_bs1770"  # International standard
    SPOTIFY = "spotify_custom"      # -14 LUFS
    YOUTUBE = "youtube_custom"      # -13 LUFS
    APPLE = "apple_custom"          # -16 LUFS
    TIKTOK = "tiktok_custom"        # -9 LUFS


@dataclass
class PlatformAudioProfile:
    """Audio processing profile for specific platform"""    platform: StreamingPlatform
    content_type: ContentType
    
    # Format specifications
    preferred_format: str = "mp3"
    fallback_formats: List[str] = field(default_factory=lambda: ["aac", "wav"])
    sample_rate: int = 44100
    bit_depth: int = 16
    bitrate_kbps: int = 320
    channels: int = 2
    
    # Loudness and dynamics
    target_lufs: float = -14.0
    max_peak_dbfs: float = -1.0
    loudness_range_lu: Tuple[float, float] = (-3.0, 3.0)
    dynamic_range_db: float = 12.0
    
    # Processing parameters
    apply_loudness_normalization: bool = True
    apply_peak_limiting: bool = True
    apply_eq_optimization: bool = True
    apply_stereo_enhancement: bool = False
    apply_compression: bool = False
    
    # Platform-specific optimizations
    optimize_for_mobile: bool = False
    optimize_for_streaming: bool = True
    enable_gapless_playback: bool = False
    enable_crossfade: bool = False
    
    # Quality settings
    quality_preset: str = "standard"  # draft, standard, high, broadcast
    encoding_complexity: int = 5  # 0-10 scale
    psychoacoustic_model: str = "advanced"
    
    # Metadata requirements
    required_metadata: List[str] = field(default_factory=list)
    optional_metadata: List[str] = field(default_factory=list)
    
    # Content restrictions
    max_duration_seconds: Optional[int] = None
    min_duration_seconds: Optional[int] = None
    max_file_size_mb: Optional[float] = None
    
    # Distribution settings
    auto_publish: bool = False
    schedule_release: bool = False
    enable_analytics: bool = True
    monetization_enabled: bool = True


@dataclass
class SocialMediaOptimization:
    """Social media specific audio optimization"""    platform: StreamingPlatform
    
    # Attention grabbing settings
    enhance_first_seconds: float = 3.0
    boost_vocals: bool = True
    reduce_background_noise: bool = True
    apply_voice_clarity: bool = True
    
    # Engagement optimization
    optimize_hook_timing: bool = True
    enhance_rhythm_section: bool = True
    apply_punch_compression: bool = True
    boost_bass_frequencies: bool = False
    
    # Platform algorithm optimization
    target_engagement_metrics: List[str] = field(default_factory=lambda: ["retention", "shares"])
    optimize_for_discovery: bool = True
    enable_viral_factors: bool = True
    
    # Technical optimizations
    reduce_latency: bool = True
    optimize_for_autoplay: bool = True
    ensure_loop_compatibility: bool = False


class PlatformOptimizationConfig:
    """Platform-specific audio optimization configuration manager"""    
    def __init__(self):
        self.platform_profiles = self._initialize_platform_profiles()
        self.social_optimizations = self._initialize_social_optimizations()
        self.custom_profiles = {}
        
    def _initialize_platform_profiles(self) -> Dict[str, PlatformAudioProfile]:
        """Initialize default platform audio profiles"""        profiles = {}
        
        # Spotify Profile
        profiles[StreamingPlatform.SPOTIFY.value] = PlatformAudioProfile(
            platform=StreamingPlatform.SPOTIFY,
            content_type=ContentType.MUSIC_TRACK,
            preferred_format="ogg",
            fallback_formats=["mp3", "aac"],
            sample_rate=44100,
            bit_depth=16,
            bitrate_kbps=320,
            target_lufs=-14.0,
            max_peak_dbfs=-1.0,
            apply_loudness_normalization=True,
            enable_gapless_playback=True,
            quality_preset="high",
            required_metadata=["title", "artist", "album", "genre", "isrc"],
            monetization_enabled=True
        )
        
        # YouTube Music Profile
        profiles[StreamingPlatform.YOUTUBE_MUSIC.value] = PlatformAudioProfile(
            platform=StreamingPlatform.YOUTUBE_MUSIC,
            content_type=ContentType.MUSIC_TRACK,
            preferred_format="aac",
            sample_rate=48000,
            bitrate_kbps=256,
            target_lufs=-13.0,
            apply_compression=True,
            optimize_for_streaming=True,
            required_metadata=["title", "artist", "description"],
            enable_analytics=True
        )
        
        # Apple Music Profile
        profiles[StreamingPlatform.APPLE_MUSIC.value] = PlatformAudioProfile(
            platform=StreamingPlatform.APPLE_MUSIC,
            content_type=ContentType.MUSIC_TRACK,
            preferred_format="aac",
            sample_rate=48000,
            bit_depth=16,
            bitrate_kbps=256,
            target_lufs=-16.0,
            max_peak_dbfs=-1.0,
            psychoacoustic_model="advanced",
            enable_gapless_playback=True,
            required_metadata=["title", "artist", "album", "isrc", "copyright"]
        )
        
        # TikTok Profile
        profiles[StreamingPlatform.TIKTOK.value] = PlatformAudioProfile(
            platform=StreamingPlatform.TIKTOK,
            content_type=ContentType.SHORT_FORM_VIDEO,
            preferred_format="aac",
            sample_rate=44100,
            bitrate_kbps=128,
            target_lufs=-9.0,
            max_duration_seconds=180,
            min_duration_seconds=15,
            optimize_for_mobile=True,
            apply_stereo_enhancement=True,
            quality_preset="standard"
        )
        
        # Instagram Profile
        profiles[StreamingPlatform.INSTAGRAM.value] = PlatformAudioProfile(
            platform=StreamingPlatform.INSTAGRAM,
            content_type=ContentType.SOCIAL_MEDIA_CLIP,
            preferred_format="aac",
            sample_rate=44100,
            bitrate_kbps=128,
            target_lufs=-12.0,
            max_duration_seconds=90,
            optimize_for_mobile=True,
            apply_compression=True,
            enable_crossfade=True
        )
        
        # YouTube Profile
        profiles[StreamingPlatform.YOUTUBE.value] = PlatformAudioProfile(
            platform=StreamingPlatform.YOUTUBE,
            content_type=ContentType.MUSIC_TRACK,
            preferred_format="aac",
            sample_rate=48000,
            bitrate_kbps=192,
            target_lufs=-13.0,
            optimize_for_streaming=True,
            enable_analytics=True,
            required_metadata=["title", "description", "tags"]
        )
        
        # Podcast Profiles
        profiles[StreamingPlatform.PODCAST_SPOTIFY.value] = PlatformAudioProfile(
            platform=StreamingPlatform.PODCAST_SPOTIFY,
            content_type=ContentType.PODCAST_EPISODE,
            preferred_format="mp3",
            sample_rate=44100,
            bitrate_kbps=128,
            channels=1,  # Mono for speech
            target_lufs=-19.0,
            apply_voice_clarity=True,
            reduce_background_noise=True,
            required_metadata=["title", "description", "episode_number"]
        )
        
        # Twitch Stream Profile
        profiles[StreamingPlatform.TWITCH.value] = PlatformAudioProfile(
            platform=StreamingPlatform.TWITCH,
            content_type=ContentType.LIVE_STREAM,
            preferred_format="aac",
            sample_rate=48000,
            bitrate_kbps=160,
            target_lufs=-18.0,
            reduce_latency=True,
            optimize_for_streaming=True,
            apply_compression=True
        )
        
        return profiles
    
    def _initialize_social_optimizations(self) -> Dict[str, SocialMediaOptimization]:
        """Initialize social media specific optimizations"""        optimizations = {}
        
        # TikTok optimization
        optimizations[StreamingPlatform.TIKTOK.value] = SocialMediaOptimization(
            platform=StreamingPlatform.TIKTOK,
            enhance_first_seconds=2.0,
            boost_vocals=True,
            optimize_hook_timing=True,
            enhance_rhythm_section=True,
            apply_punch_compression=True,
            boost_bass_frequencies=True,
            target_engagement_metrics=["retention", "shares", "saves"],
            optimize_for_discovery=True,
            enable_viral_factors=True,
            optimize_for_autoplay=True,
            ensure_loop_compatibility=True
        )
        
        # Instagram optimization
        optimizations[StreamingPlatform.INSTAGRAM.value] = SocialMediaOptimization(
            platform=StreamingPlatform.INSTAGRAM,
            enhance_first_seconds=3.0,
            boost_vocals=True,
            apply_voice_clarity=True,
            optimize_hook_timing=True,
            target_engagement_metrics=["retention", "likes", "comments"],
            optimize_for_discovery=True,
            optimize_for_autoplay=True
        )
        
        return optimizations
    
    def get_platform_profile(self, platform: Union[StreamingPlatform, str], 
                           content_type: Optional[ContentType] = None) -> PlatformAudioProfile:
        """Get audio processing profile for specific platform"""        platform_key = platform.value if isinstance(platform, StreamingPlatform) else platform
        
        if platform_key in self.custom_profiles:
            return self.custom_profiles[platform_key]
        elif platform_key in self.platform_profiles:
            profile = self.platform_profiles[platform_key]
            
            # Modify profile if different content type requested
            if content_type and content_type != profile.content_type:
                profile = self._adapt_profile_for_content_type(profile, content_type)
            
            return profile
        else:
            logger.warning(f"No profile found for platform: {platform_key}")
            return self._get_default_profile()
    
    def _adapt_profile_for_content_type(self, base_profile: PlatformAudioProfile, 
                                      content_type: ContentType) -> PlatformAudioProfile:
        """Adapt platform profile for different content type"""        adapted_profile = base_profile.__class__(**base_profile.__dict__)
        adapted_profile.content_type = content_type
        
        if content_type == ContentType.PODCAST_EPISODE:
            adapted_profile.channels = 1  # Mono for speech
            adapted_profile.target_lufs = -19.0
            adapted_profile.apply_voice_clarity = True
            adapted_profile.reduce_background_noise = True
            adapted_profile.bitrate_kbps = 128
        
        elif content_type == ContentType.SHORT_FORM_VIDEO:
            adapted_profile.target_lufs = -12.0
            adapted_profile.apply_compression = True
            adapted_profile.enhance_first_seconds = 3.0
            adapted_profile.optimize_for_mobile = True
        
        elif content_type == ContentType.LIVE_STREAM:
            adapted_profile.reduce_latency = True
            adapted_profile.optimize_for_streaming = True
            adapted_profile.buffer_size_ms = 20
        
        return adapted_profile
    
    def _get_default_profile(self) -> PlatformAudioProfile:
        """Get default fallback audio profile"""        return PlatformAudioProfile(
            platform=StreamingPlatform.SPOTIFY,  # Use Spotify as default
            content_type=ContentType.MUSIC_TRACK,
            preferred_format="mp3",
            sample_rate=44100,
            bit_depth=16,
            bitrate_kbps=320,
            target_lufs=-14.0,
            quality_preset="standard"
        )
    
    def get_social_optimization(self, platform: Union[StreamingPlatform, str]) -> Optional[SocialMediaOptimization]:
        """Get social media optimization settings for platform"""        platform_key = platform.value if isinstance(platform, StreamingPlatform) else platform
        return self.social_optimizations.get(platform_key)
    
    def create_custom_profile(self, profile_name: str, base_platform: StreamingPlatform, 
                            modifications: Dict[str, Any]) -> PlatformAudioProfile:
        """Create custom platform profile based on existing profile"""        base_profile = self.get_platform_profile(base_platform)
        
        # Create modified profile
        profile_dict = base_profile.__dict__.copy()
        profile_dict.update(modifications)
        
        custom_profile = PlatformAudioProfile(**profile_dict)
        self.custom_profiles[profile_name] = custom_profile
        
        logger.info(f"Created custom profile: {profile_name}")
        return custom_profile
    
    def get_multi_platform_strategy(self, platforms: List[StreamingPlatform]) -> Dict[str, Any]:
        """Get optimized strategy for multi-platform distribution"""        profiles = [self.get_platform_profile(platform) for platform in platforms]
        
        # Find common optimal settings
        common_sample_rate = self._find_optimal_sample_rate(profiles)
        common_format = self._find_optimal_format(profiles)
        target_lufs_range = self._calculate_lufs_range(profiles)
        
        return {
            "recommended_master_format": common_format,
            "recommended_sample_rate": common_sample_rate,
            "target_lufs_range": target_lufs_range,
            "platforms": {
                platform.value: self.get_platform_profile(platform).__dict__
                for platform in platforms
            },
            "processing_order": self._optimize_processing_order(platforms),
            "quality_validation": self._get_quality_checks(profiles)
        }
    
    def _find_optimal_sample_rate(self, profiles: List[PlatformAudioProfile]) -> int:
        """Find optimal sample rate for multi-platform distribution"""        sample_rates = [profile.sample_rate for profile in profiles]
        # Use highest common sample rate
        return max(set(sample_rates), key=sample_rates.count)
    
    def _find_optimal_format(self, profiles: List[PlatformAudioProfile]) -> str:
        """Find optimal master format for multi-platform distribution"""        formats = [profile.preferred_format for profile in profiles]
        format_counts = {fmt: formats.count(fmt) for fmt in set(formats)}
        
        # Prefer lossless formats if available, otherwise most common
        if "flac" in format_counts:
            return "flac"
        elif "wav" in format_counts:
            return "wav"
        else:
            return max(format_counts, key=format_counts.get)
    
    def _calculate_lufs_range(self, profiles: List[PlatformAudioProfile]) -> Tuple[float, float]:
        """Calculate optimal LUFS range for all platforms"""        lufs_values = [profile.target_lufs for profile in profiles]
        return (min(lufs_values), max(lufs_values))
    
    def _optimize_processing_order(self, platforms: List[StreamingPlatform]) -> List[str]:
        """Optimize processing order based on platform requirements"""        # Sort by quality requirements (highest first)
        platform_priority = {
            StreamingPlatform.TIDAL: 1,
            StreamingPlatform.APPLE_MUSIC: 2,
            StreamingPlatform.SPOTIFY: 3,
            StreamingPlatform.YOUTUBE_MUSIC: 4,
            StreamingPlatform.SOUNDCLOUD: 5,
            StreamingPlatform.YOUTUBE: 6,
            StreamingPlatform.INSTAGRAM: 7,
            StreamingPlatform.TIKTOK: 8
        }
        
        sorted_platforms = sorted(platforms, 
                                key=lambda p: platform_priority.get(p, 999))
        
        return [platform.value for platform in sorted_platforms]
    
    def _get_quality_checks(self, profiles: List[PlatformAudioProfile]) -> Dict[str, Any]:
        """Get quality validation checks for multi-platform distribution"""        return {
            "peak_levels": [profile.max_peak_dbfs for profile in profiles],
            "lufs_targets": [profile.target_lufs for profile in profiles],
            "dynamic_range_requirements": [profile.dynamic_range_db for profile in profiles],
            "format_compatibility": list(set(profile.preferred_format for profile in profiles))
        }
    
    def validate_content_for_platform(self, audio_metadata: Dict[str, Any], 
                                    platform: StreamingPlatform) -> Dict[str, Any]:
        """Validate audio content against platform requirements"""        profile = self.get_platform_profile(platform)
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check duration limits
        if profile.max_duration_seconds and audio_metadata.get("duration", 0) > profile.max_duration_seconds:
            validation_results["errors"].append(
                f"Duration exceeds platform limit: {profile.max_duration_seconds}s"
            )
            validation_results["valid"] = False
        
        if profile.min_duration_seconds and audio_metadata.get("duration", 0) < profile.min_duration_seconds:
            validation_results["errors"].append(
                f"Duration below platform minimum: {profile.min_duration_seconds}s"
            )
            validation_results["valid"] = False
        
        # Check file size
        if profile.max_file_size_mb and audio_metadata.get("file_size_mb", 0) > profile.max_file_size_mb:
            validation_results["errors"].append(
                f"File size exceeds platform limit: {profile.max_file_size_mb}MB"
            )
            validation_results["valid"] = False
        
        # Check required metadata
        missing_metadata = []
        for required_field in profile.required_metadata:
            if required_field not in audio_metadata or not audio_metadata[required_field]:
                missing_metadata.append(required_field)
        
        if missing_metadata:
            validation_results["errors"].append(
                f"Missing required metadata: {', '.join(missing_metadata)}"
            )
            validation_results["valid"] = False
        
        # Add recommendations
        if audio_metadata.get("lufs", 0) != profile.target_lufs:
            validation_results["recommendations"].append(
                f"Consider adjusting loudness to {profile.target_lufs} LUFS for optimal platform performance"
            )
        
        if audio_metadata.get("format") != profile.preferred_format:
            validation_results["recommendations"].append(
                f"Consider using {profile.preferred_format} format for better platform compatibility"
            )
        
        return validation_results


# Global configuration instance
platform_optimization_config = PlatformOptimizationConfig()

# Export commonly used functions
def get_platform_profile(platform: Union[StreamingPlatform, str]) -> PlatformAudioProfile:
    """Get audio processing profile for platform"""    return platform_optimization_config.get_platform_profile(platform)

def get_multi_platform_strategy(platforms: List[StreamingPlatform]) -> Dict[str, Any]:
    """Get optimized strategy for multi-platform distribution"""    return platform_optimization_config.get_multi_platform_strategy(platforms)

def validate_content_for_platform(audio_metadata: Dict[str, Any], 
                                platform: StreamingPlatform) -> Dict[str, Any]:
    """Validate audio content against platform requirements"""    return platform_optimization_config.validate_content_for_platform(audio_metadata, platform)
