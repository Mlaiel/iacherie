"""
Platform-Specific Format Management System
Platform-optimized multimedia format handling for Ainflue Platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms"""
    WEB = "web"
    MOBILE_IOS = "mobile_ios"
    MOBILE_ANDROID = "mobile_android"
    DESKTOP_WINDOWS = "desktop_windows"
    DESKTOP_MACOS = "desktop_macos"
    DESKTOP_LINUX = "desktop_linux"
    TV_ANDROID = "tv_android"
    TV_SMART = "tv_smart"
    GAMING_CONSOLE = "gaming_console"
    SOCIAL_MEDIA = "social_media"
    STREAMING_SERVICES = "streaming_services"
    PROFESSIONAL_TOOLS = "professional_tools"


class OptimizationLevel(Enum):
    """Format optimization levels"""
    BASIC = "basic"
    STANDARD = "standard"
    OPTIMIZED = "optimized"
    MAXIMUM = "maximum"


@dataclass
class PlatformFormat:
    """Platform-specific format specification"""
    platform: Platform
    category: str  # video, audio, image
    primary_formats: List[str]
    fallback_formats: List[str]
    optimization_level: OptimizationLevel
    
    # Technical constraints
    max_resolution: str
    max_bitrate: int  # kbps
    max_file_size: int  # MB
    max_duration: int  # seconds, 0 = unlimited
    
    # Quality settings
    recommended_quality: int  # 1-10 scale
    compression_profile: str
    encoding_preset: str
    
    # Feature support
    supports_hdr: bool
    supports_dolby_vision: bool
    supports_transparency: bool
    supports_animation: bool
    supports_subtitles: bool
    supports_multiple_audio: bool
    
    # Performance characteristics
    hardware_acceleration: bool
    battery_optimized: bool
    bandwidth_adaptive: bool
    offline_capable: bool
    
    # Platform-specific requirements
    platform_requirements: Dict[str, Any] = field(default_factory=dict)
    distribution_requirements: Dict[str, Any] = field(default_factory=dict)


class PlatformFormatRegistry:
    """Platform-specific format registry and optimization system"""
    
    def __init__(self):
        self.platform_formats: Dict[Platform, Dict[str, PlatformFormat]] = {}
        self._initialize_platform_formats()
    
    def _initialize_platform_formats(self):
        """Initialize platform-specific format configurations"""
        
        # Web Platform Formats
        self._register_web_formats()
        
        # Mobile Platform Formats
        self._register_mobile_formats()
        
        # Desktop Platform Formats
        self._register_desktop_formats()
        
        # TV and Streaming Formats
        self._register_tv_formats()
        
        # Social Media Platform Formats
        self._register_social_media_formats()
        
        # Professional Platform Formats
        self._register_professional_formats()
    
    def _register_web_formats(self):
        """Register web platform formats"""
        web_formats = {}
        
        # Web Video
        web_formats["video"] = PlatformFormat(
            platform=Platform.WEB,
            category="video",
            primary_formats=["mp4", "webm"],
            fallback_formats=["ogv"],
            optimization_level=OptimizationLevel.OPTIMIZED,
            max_resolution="4K",
            max_bitrate=8000,
            max_file_size=500,
            max_duration=0,  # Unlimited
            recommended_quality=7,
            compression_profile="high",
            encoding_preset="medium",
            supports_hdr=True,
            supports_dolby_vision=False,
            supports_transparency=False,
            supports_animation=True,
            supports_subtitles=True,
            supports_multiple_audio=True,
            hardware_acceleration=True,
            battery_optimized=True,
            bandwidth_adaptive=True,
            offline_capable=True,
            platform_requirements={
                "codecs": ["h264", "vp9", "av1"],
                "containers": ["mp4", "webm"],
                "streaming": ["hls", "dash"],
                "drm": ["widevine", "playready", "fairplay"]
            },
            distribution_requirements={
                "cdn_optimized": True,
                "progressive_download": True,
                "adaptive_streaming": True,
                "thumbnail_generation": True
            }
        )
        
        # Web Audio
        web_formats["audio"] = PlatformFormat(
            platform=Platform.WEB,
            category="audio",
            primary_formats=["mp3", "aac", "opus"],
            fallback_formats=["ogg"],
            optimization_level=OptimizationLevel.STANDARD,
            max_resolution="N/A",
            max_bitrate=320,
            max_file_size=50,
            max_duration=0,
            recommended_quality=7,
            compression_profile="standard",
            encoding_preset="medium",
            supports_hdr=False,
            supports_dolby_vision=False,
            supports_transparency=False,
            supports_animation=False,
            supports_subtitles=False,
            supports_multiple_audio=True,
            hardware_acceleration=False,
            battery_optimized=True,
            bandwidth_adaptive=True,
            offline_capable=True,
            platform_requirements={
                "codecs": ["mp3", "aac", "opus"],
                "sample_rates": [44100, 48000],
                "channels": ["mono", "stereo", "5.1"]
            }
        )
        
        # Web Images
        web_formats["image"] = PlatformFormat(
            platform=Platform.WEB,
            category="image",
            primary_formats=["webp", "avif", "jpeg"],
            fallback_formats=["png", "gif"],
            optimization_level=OptimizationLevel.MAXIMUM,
            max_resolution="8K",
            max_bitrate=0,
            max_file_size=10,
            max_duration=0,
            recommended_quality=8,
            compression_profile="high",
            encoding_preset="slow",
            supports_hdr=True,
            supports_dolby_vision=False,
            supports_transparency=True,
            supports_animation=True,
            supports_subtitles=False,
            supports_multiple_audio=False,
            hardware_acceleration=False,
            battery_optimized=True,
            bandwidth_adaptive=True,
            offline_capable=True,
            platform_requirements={
                "responsive_images": True,
                "lazy_loading": True,
                "webp_support": True,
                "avif_support": True
            }
        )
        
        self.platform_formats[Platform.WEB] = web_formats
    
    def _register_mobile_formats(self):
        """Register mobile platform formats"""
        
        # iOS Mobile
        ios_formats = {}
        ios_formats["video"] = PlatformFormat(
            platform=Platform.MOBILE_IOS,
            category="video",
            primary_formats=["mp4", "mov"],
            fallback_formats=["m4v"],
            optimization_level=OptimizationLevel.OPTIMIZED,
            max_resolution="4K",
            max_bitrate=6000,
            max_file_size=200,
            max_duration=0,
            recommended_quality=7,
            compression_profile="high",
            encoding_preset="medium",
            supports_hdr=True,
            supports_dolby_vision=True,
            supports_transparency=False,
            supports_animation=True,
            supports_subtitles=True,
            supports_multiple_audio=True,
            hardware_acceleration=True,
            battery_optimized=True,
            bandwidth_adaptive=True,
            offline_capable=True,
            platform_requirements={
                "codecs": ["h264", "h265"],
                "hdr_formats": ["hdr10", "dolby_vision"],
                "app_store_compliance": True
            }
        )
        
        # Android Mobile
        android_formats = {}
        android_formats["video"] = PlatformFormat(
            platform=Platform.MOBILE_ANDROID,
            category="video",
            primary_formats=["mp4", "webm"],
            fallback_formats=["3gp"],
            optimization_level=OptimizationLevel.OPTIMIZED,
            max_resolution="4K",
            max_bitrate=5000,
            max_file_size=150,
            max_duration=0,
            recommended_quality=6,
            compression_profile="main",
            encoding_preset="fast",
            supports_hdr=True,
            supports_dolby_vision=False,
            supports_transparency=False,
            supports_animation=True,
            supports_subtitles=True,
            supports_multiple_audio=True,
            hardware_acceleration=True,
            battery_optimized=True,
            bandwidth_adaptive=True,
            offline_capable=True,
            platform_requirements={
                "codecs": ["h264", "vp9", "av1"],
                "android_compliance": True,
                "play_store_requirements": True
            }
        )
        
        self.platform_formats[Platform.MOBILE_IOS] = ios_formats
        self.platform_formats[Platform.MOBILE_ANDROID] = android_formats
    
    def _register_desktop_formats(self):
        """Register desktop platform formats"""
        
        # Windows Desktop
        windows_formats = {}
        windows_formats["video"] = PlatformFormat(
            platform=Platform.DESKTOP_WINDOWS,
            category="video",
            primary_formats=["mp4", "mkv", "wmv"],
            fallback_formats=["avi"],
            optimization_level=OptimizationLevel.STANDARD,
            max_resolution="8K",
            max_bitrate=50000,
            max_file_size=5000,
            max_duration=0,
            recommended_quality=8,
            compression_profile="high",
            encoding_preset="medium",
            supports_hdr=True,
            supports_dolby_vision=True,
            supports_transparency=False,
            supports_animation=True,
            supports_subtitles=True,
            supports_multiple_audio=True,
            hardware_acceleration=True,
            battery_optimized=False,
            bandwidth_adaptive=False,
            offline_capable=True,
            platform_requirements={
                "codecs": ["h264", "h265", "av1", "vp9"],
                "directx_support": True,
                "windows_media_foundation": True
            }
        )
        
        self.platform_formats[Platform.DESKTOP_WINDOWS] = windows_formats
    
    def _register_tv_formats(self):
        """Register TV and streaming platform formats"""
        
        # Streaming Services
        streaming_formats = {}
        streaming_formats["video"] = PlatformFormat(
            platform=Platform.STREAMING_SERVICES,
            category="video",
            primary_formats=["mp4"],
            fallback_formats=["mkv"],
            optimization_level=OptimizationLevel.MAXIMUM,
            max_resolution="8K",
            max_bitrate=25000,
            max_file_size=0,  # Unlimited for streaming
            max_duration=0,
            recommended_quality=9,
            compression_profile="high",
            encoding_preset="slow",
            supports_hdr=True,
            supports_dolby_vision=True,
            supports_transparency=False,
            supports_animation=True,
            supports_subtitles=True,
            supports_multiple_audio=True,
            hardware_acceleration=True,
            battery_optimized=False,
            bandwidth_adaptive=True,
            offline_capable=True,
            platform_requirements={
                "codecs": ["h264", "h265", "av1"],
                "hdr_formats": ["hdr10", "hdr10+", "dolby_vision"],
                "audio_formats": ["aac", "dolby_atmos", "dts"],
                "drm_required": True,
                "multi_bitrate": True
            }
        )
        
        self.platform_formats[Platform.STREAMING_SERVICES] = streaming_formats
    
    def _register_social_media_formats(self):
        """Register social media platform formats"""
        
        social_formats = {}
        social_formats["video"] = PlatformFormat(
            platform=Platform.SOCIAL_MEDIA,
            category="video",
            primary_formats=["mp4"],
            fallback_formats=["mov"],
            optimization_level=OptimizationLevel.OPTIMIZED,
            max_resolution="4K",
            max_bitrate=8000,
            max_file_size=4000,  # 4GB typical limit
            max_duration=600,  # 10 minutes typical
            recommended_quality=7,
            compression_profile="high",
            encoding_preset="fast",
            supports_hdr=False,
            supports_dolby_vision=False,
            supports_transparency=False,
            supports_animation=True,
            supports_subtitles=True,
            supports_multiple_audio=False,
            hardware_acceleration=True,
            battery_optimized=True,
            bandwidth_adaptive=True,
            offline_capable=False,
            platform_requirements={
                "codecs": ["h264"],
                "square_aspect_ratios": True,
                "vertical_video": True,
                "auto_captions": True,
                "thumbnail_generation": True
            },
            distribution_requirements={
                "fast_upload": True,
                "auto_compression": True,
                "multiple_resolutions": True,
                "preview_generation": True
            }
        )
        
        self.platform_formats[Platform.SOCIAL_MEDIA] = social_formats
    
    def _register_professional_formats(self):
        """Register professional tools formats"""
        
        professional_formats = {}
        professional_formats["video"] = PlatformFormat(
            platform=Platform.PROFESSIONAL_TOOLS,
            category="video",
            primary_formats=["prores", "dnxhr", "exr"],
            fallback_formats=["mov", "mxf"],
            optimization_level=OptimizationLevel.BASIC,  # Preserve quality
            max_resolution="8K+",
            max_bitrate=200000,  # Very high for professional
            max_file_size=0,  # Unlimited
            max_duration=0,
            recommended_quality=10,
            compression_profile="lossless",
            encoding_preset="slow",
            supports_hdr=True,
            supports_dolby_vision=True,
            supports_transparency=True,
            supports_animation=True,
            supports_subtitles=True,
            supports_multiple_audio=True,
            hardware_acceleration=False,  # Software precision preferred
            battery_optimized=False,
            bandwidth_adaptive=False,
            offline_capable=True,
            platform_requirements={
                "codecs": ["prores", "dnxhr", "uncompressed"],
                "color_profiles": ["rec709", "rec2020", "log"],
                "bit_depths": ["10bit", "12bit", "16bit"],
                "metadata_preservation": True
            }
        )
        
        self.platform_formats[Platform.PROFESSIONAL_TOOLS] = professional_formats
    
    def get_platform_formats(self, platform: Platform) -> Dict[str, PlatformFormat]:
        """Get all formats for a platform"""
        return self.platform_formats.get(platform, {})
    
    def get_platform_format(self, platform: Platform, category: str) -> Optional[PlatformFormat]:
        """Get specific format for platform and category"""
        platform_formats = self.get_platform_formats(platform)
        return platform_formats.get(category)
    
    def get_optimal_format(self, platform: Platform, category: str, constraints: Dict[str, Any] = None) -> Optional[str]:
        """Get optimal format for platform with constraints"""
        platform_format = self.get_platform_format(platform, category)
        if not platform_format:
            return None
        
        # Apply constraints if provided
        if constraints:
            max_size = constraints.get("max_file_size")
            if max_size and max_size < platform_format.max_file_size:
                # Prefer more compressed formats
                return platform_format.fallback_formats[0] if platform_format.fallback_formats else platform_format.primary_formats[-1]
            
            max_bitrate = constraints.get("max_bitrate")
            if max_bitrate and max_bitrate < platform_format.max_bitrate:
                # Use fallback formats for lower bitrate
                return platform_format.fallback_formats[0] if platform_format.fallback_formats else platform_format.primary_formats[-1]
        
        return platform_format.primary_formats[0]
    
    def get_cross_platform_formats(self, platforms: List[Platform], category: str) -> List[str]:
        """Get formats compatible across multiple platforms"""
        if not platforms:
            return []
        
        # Get formats for first platform
        common_formats = set()
        first_platform_format = self.get_platform_format(platforms[0], category)
        if first_platform_format:
            common_formats.update(first_platform_format.primary_formats)
            common_formats.update(first_platform_format.fallback_formats)
        
        # Find intersection with other platforms
        for platform in platforms[1:]:
            platform_format = self.get_platform_format(platform, category)
            if platform_format:
                platform_formats = set(platform_format.primary_formats + platform_format.fallback_formats)
                common_formats &= platform_formats
            else:
                common_formats = set()  # No common formats if platform not supported
                break
        
        return list(common_formats)
    
    def get_platform_constraints(self, platform: Platform, category: str) -> Dict[str, Any]:
        """Get platform-specific constraints"""
        platform_format = self.get_platform_format(platform, category)
        if not platform_format:
            return {}
        
        return {
            "max_resolution": platform_format.max_resolution,
            "max_bitrate": platform_format.max_bitrate,
            "max_file_size": platform_format.max_file_size,
            "max_duration": platform_format.max_duration,
            "recommended_quality": platform_format.recommended_quality,
            "supports_hdr": platform_format.supports_hdr,
            "supports_transparency": platform_format.supports_transparency,
            "hardware_acceleration": platform_format.hardware_acceleration,
            "platform_requirements": platform_format.platform_requirements
        }
    
    def recommend_encoding_settings(self, platform: Platform, category: str, quality_priority: str = "balanced") -> Dict[str, Any]:
        """Recommend encoding settings for platform"""
        platform_format = self.get_platform_format(platform, category)
        if not platform_format:
            return {}
        
        settings = {
            "format": platform_format.primary_formats[0],
            "compression_profile": platform_format.compression_profile,
            "encoding_preset": platform_format.encoding_preset,
            "quality": platform_format.recommended_quality
        }
        
        # Adjust based on quality priority
        if quality_priority == "speed":
            settings["encoding_preset"] = "ultrafast"
            settings["quality"] = max(1, platform_format.recommended_quality - 2)
        elif quality_priority == "quality":
            settings["encoding_preset"] = "slow"
            settings["quality"] = min(10, platform_format.recommended_quality + 1)
        elif quality_priority == "size":
            settings["quality"] = max(1, platform_format.recommended_quality - 1)
            settings["compression_profile"] = "high"
        
        # Add platform-specific optimizations
        if platform_format.hardware_acceleration:
            settings["hardware_acceleration"] = True
        
        if platform_format.battery_optimized:
            settings["power_efficient"] = True
        
        return settings
    
    def validate_platform_compliance(self, platform: Platform, file_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate file compliance with platform requirements"""
        platform_format = self.get_platform_format(platform, file_specs.get("category", "video"))
        if not platform_format:
            return {"compliant": False, "reason": "Platform not supported"}
        
        issues = []
        warnings = []
        
        # Check file size
        if file_specs.get("file_size", 0) > platform_format.max_file_size > 0:
            issues.append(f"File size {file_specs['file_size']}MB exceeds limit {platform_format.max_file_size}MB")
        
        # Check bitrate
        if file_specs.get("bitrate", 0) > platform_format.max_bitrate:
            issues.append(f"Bitrate {file_specs['bitrate']}kbps exceeds limit {platform_format.max_bitrate}kbps")
        
        # Check duration
        if platform_format.max_duration > 0 and file_specs.get("duration", 0) > platform_format.max_duration:
            issues.append(f"Duration {file_specs['duration']}s exceeds limit {platform_format.max_duration}s")
        
        # Check format support
        file_format = file_specs.get("format", "").lower()
        supported_formats = platform_format.primary_formats + platform_format.fallback_formats
        if file_format not in supported_formats:
            issues.append(f"Format {file_format} not supported. Supported: {supported_formats}")
        
        # Check codec support
        if "codec" in file_specs:
            required_codecs = platform_format.platform_requirements.get("codecs", [])
            if required_codecs and file_specs["codec"] not in required_codecs:
                warnings.append(f"Codec {file_specs['codec']} may not be optimal. Recommended: {required_codecs}")
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "recommendations": self.recommend_encoding_settings(platform, file_specs.get("category", "video"))
        }
    
    def export_platform_matrix(self) -> Dict[str, Any]:
        """Export comprehensive platform compatibility matrix"""
        matrix = {}
        
        for platform, formats in self.platform_formats.items():
            platform_data = {}
            for category, format_info in formats.items():
                platform_data[category] = {
                    "primary_formats": format_info.primary_formats,
                    "fallback_formats": format_info.fallback_formats,
                    "max_resolution": format_info.max_resolution,
                    "max_bitrate": format_info.max_bitrate,
                    "max_file_size": format_info.max_file_size,
                    "optimization_level": format_info.optimization_level.value,
                    "features": {
                        "hdr": format_info.supports_hdr,
                        "transparency": format_info.supports_transparency,
                        "hardware_acceleration": format_info.hardware_acceleration,
                        "battery_optimized": format_info.battery_optimized
                    }
                }
            matrix[platform.value] = platform_data
        
        return matrix


# Global registry instance
platform_formats = PlatformFormatRegistry()


# Export main classes and functions
__all__ = [
    'Platform',
    'OptimizationLevel',
    'PlatformFormat',
    'PlatformFormatRegistry',
    'platform_formats'
]