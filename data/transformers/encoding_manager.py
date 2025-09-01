"""Encoding Manager - Professional encoding optimization for IA Influencer Agent Platform
======================================================================================

Advanced encoding optimization and codec management for creator content workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json
import time

logger = logging.getLogger(__name__)


class EncodingProfile(Enum):
    """
Encoding profiles for different use cases."""

    WEB_OPTIMIZED = "web_optimized"
    MOBILE_OPTIMIZED = "mobile_optimized"
    STREAMING_OPTIMIZED = "streaming_optimized"
    ARCHIVE_QUALITY = "archive_quality"
    SOCIAL_MEDIA = "social_media"
    BROADCAST_QUALITY = "broadcast_quality"
    CUSTOM = "custom"


class CodecType(Enum):
    """Codec types."""

    VIDEO_H264 = "h264"
    VIDEO_H265 = "h265"
    VIDEO_VP9 = "vp9"
    VIDEO_AV1 = "av1"
    AUDIO_AAC = "aac"
    AUDIO_MP3 = "mp3"
    AUDIO_OPUS = "opus"
    AUDIO_VORBIS = "vorbis"


@dataclass
class EncodingSettings:
    """Encoding configuration settings."""
    profile: EncodingProfile = EncodingProfile.WEB_OPTIMIZED
    video_codec: Optional[CodecType] = None
    audio_codec: Optional[CodecType] = None
    
    # Video settings
    video_bitrate: Optional[int] = None
    video_quality: Optional[int] = None  # CRF value
    video_preset: Optional[str] = None
    video_profile: Optional[str] = None
    
    # Audio settings
    audio_bitrate: Optional[int] = None
    audio_quality: Optional[int] = None
    audio_sample_rate: Optional[int] = None
    audio_channels: Optional[int] = None
    
    # Advanced settings
    two_pass_encoding: bool = False
    hardware_acceleration: bool = True
    optimize_for_streaming: bool = False
    target_file_size: Optional[int] = None
    
    # Platform-specific optimizations
    youtube_optimized: bool = False
    instagram_optimized: bool = False
    tiktok_optimized: bool = False
    web_optimized: bool = False


@dataclass
class EncodingResult:
    """
Encoding operation result."""
    success: bool
    input_file: str
    output_file: str
    encoding_time: float
    input_size: int
    output_size: int
    compression_ratio: float
    quality_score: Optional[float] = None
    bitrate_achieved: Optional[int] = None
    settings_used: Optional[EncodingSettings] = None
    error_message: Optional[str] = None
    warnings: Optional[List[str]] = None


class EncodingManager:
    """
    Professional encoding manager for the IA Influencer Agent Platform.
    
    Provides intelligent encoding optimization and codec management
    for creator content workflows.
    """
    
    def __init__(
        self,
        enable_gpu: bool = True,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize encoding manager.
        
        Args:
            enable_gpu: Enable GPU acceleration
            config: Configuration options
        """
        self.enable_gpu = enable_gpu
        self.config = config or {}
        
        # Initialize encoding profiles
        self.encoding_profiles = self._init_encoding_profiles()
        
        # Codec capabilities
        self.codec_capabilities = self._init_codec_capabilities()
        
        # Platform specifications
        self.platform_specs = self._init_platform_specs()
        
        # Hardware detection
        self.hardware_info = self._detect_hardware()
        
        logger.info(f"EncodingManager initialized (GPU: {enable_gpu})")
    
    def _init_encoding_profiles(self) -> Dict[str, EncodingSettings]:
        """Initialize predefined encoding profiles."""
        profiles = {}
        
        # Web optimized profile
        profiles[EncodingProfile.WEB_OPTIMIZED.value] = EncodingSettings(
            profile=EncodingProfile.WEB_OPTIMIZED,
            video_codec=CodecType.VIDEO_H264,
            audio_codec=CodecType.AUDIO_AAC,
            video_bitrate=2500,
            video_quality=23,
            video_preset="medium",
            video_profile="high",
            audio_bitrate=128,
            audio_sample_rate=44100,
            audio_channels=2,
            optimize_for_streaming=True,
            web_optimized=True
        )
        
        # Mobile optimized profile
        profiles[EncodingProfile.MOBILE_OPTIMIZED.value] = EncodingSettings(
            profile=EncodingProfile.MOBILE_OPTIMIZED,
            video_codec=CodecType.VIDEO_H264,
            audio_codec=CodecType.AUDIO_AAC,
            video_bitrate=1000,
            video_quality=26,
            video_preset="fast",
            video_profile="baseline",
            audio_bitrate=96,
            audio_sample_rate=44100,
            audio_channels=2,
            optimize_for_streaming=True
        )
        
        # Streaming optimized profile
        profiles[EncodingProfile.STREAMING_OPTIMIZED.value] = EncodingSettings(
            profile=EncodingProfile.STREAMING_OPTIMIZED,
            video_codec=CodecType.VIDEO_H264,
            audio_codec=CodecType.AUDIO_AAC,
            video_bitrate=3000,
            video_quality=21,
            video_preset="veryfast",
            video_profile="high",
            audio_bitrate=160,
            audio_sample_rate=48000,
            audio_channels=2,
            two_pass_encoding=False,
            optimize_for_streaming=True
        )
        
        # Archive quality profile
        profiles[EncodingProfile.ARCHIVE_QUALITY.value] = EncodingSettings(
            profile=EncodingProfile.ARCHIVE_QUALITY,
            video_codec=CodecType.VIDEO_H265,
            audio_codec=CodecType.AUDIO_AAC,
            video_bitrate=8000,
            video_quality=18,
            video_preset="slow",
            video_profile="main",
            audio_bitrate=256,
            audio_sample_rate=48000,
            audio_channels=2,
            two_pass_encoding=True
        )
        
        # Social media profile
        profiles[EncodingProfile.SOCIAL_MEDIA.value] = EncodingSettings(
            profile=EncodingProfile.SOCIAL_MEDIA,
            video_codec=CodecType.VIDEO_H264,
            audio_codec=CodecType.AUDIO_AAC,
            video_bitrate=1500,
            video_quality=24,
            video_preset="medium",
            video_profile="high",
            audio_bitrate=128,
            audio_sample_rate=44100,
            audio_channels=2,
            optimize_for_streaming=True
        )
        
        # Broadcast quality profile
        profiles[EncodingProfile.BROADCAST_QUALITY.value] = EncodingSettings(
            profile=EncodingProfile.BROADCAST_QUALITY,
            video_codec=CodecType.VIDEO_H264,
            audio_codec=CodecType.AUDIO_AAC,
            video_bitrate=15000,
            video_quality=16,
            video_preset="slow",
            video_profile="high",
            audio_bitrate=320,
            audio_sample_rate=48000,
            audio_channels=2,
            two_pass_encoding=True
        )
        
        return profiles
    
    def _init_codec_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Initialize codec capabilities and features."""
        return {
            CodecType.VIDEO_H264.value: {
                "quality_range": (0, 51),
                "presets": ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
                "profiles": ["baseline", "main", "high", "high10", "high422", "high444"],
                "hardware_support": ["nvidia", "intel", "amd"],
                "streaming_friendly": True,
                "compression_efficiency": 0.7
            },
            CodecType.VIDEO_H265.value: {
                "quality_range": (0, 51),
                "presets": ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
                "profiles": ["main", "main10", "main444"],
                "hardware_support": ["nvidia", "intel"],
                "streaming_friendly": True,
                "compression_efficiency": 0.85
            },
            CodecType.VIDEO_VP9.value: {
                "quality_range": (0, 63),
                "presets": [],
                "profiles": ["profile0", "profile1", "profile2", "profile3"],
                "hardware_support": ["intel"],
                "streaming_friendly": True,
                "compression_efficiency": 0.8
            },
            CodecType.VIDEO_AV1.value: {
                "quality_range": (0, 63),
                "presets": [],
                "profiles": ["main", "high", "professional"],
                "hardware_support": [],
                "streaming_friendly": True,
                "compression_efficiency": 0.9
            },
            CodecType.AUDIO_AAC.value: {
                "bitrate_range": (8, 320),
                "sample_rates": [8000, 16000, 22050, 44100, 48000, 96000],
                "channels": [1, 2, 6, 8],
                "profiles": ["lc", "he", "he-v2"],
                "compression_efficiency": 0.8
            },
            CodecType.AUDIO_MP3.value: {
                "bitrate_range": (32, 320),
                "sample_rates": [8000, 16000, 22050, 44100, 48000],
                "channels": [1, 2],
                "profiles": [],
                "compression_efficiency": 0.7
            },
            CodecType.AUDIO_OPUS.value: {
                "bitrate_range": (6, 510),
                "sample_rates": [8000, 12000, 16000, 24000, 48000],
                "channels": [1, 2, 8],
                "profiles": [],
                "compression_efficiency": 0.9
            }
        }
    
    def _init_platform_specs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific encoding specifications."""
        return {
            "youtube": {
                "video_codecs": ["h264", "h265"],
                "audio_codecs": ["aac", "mp3"],
                "max_bitrate": {
                    "1080p": 8000,
                    "720p": 5000,
                    "480p": 2500
                },
                "recommended_fps": [24, 30, 60],
                "max_file_size": 12 * 1024 * 1024 * 1024,  # 12GB
                "aspect_ratios": ["16:9", "4:3", "1:1", "9:16"]
            },
            "instagram": {
                "video_codecs": ["h264"],
                "audio_codecs": ["aac"],
                "max_bitrate": {
                    "1080p": 3500,
                    "720p": 2500,
                    "480p": 1000
                },
                "recommended_fps": [30],
                "max_file_size": 4 * 1024 * 1024 * 1024,  # 4GB
                "aspect_ratios": ["1:1", "9:16", "16:9", "4:5"]
            },
            "tiktok": {
                "video_codecs": ["h264"],
                "audio_codecs": ["aac", "mp3"],
                "max_bitrate": {
                    "1080p": 2000,
                    "720p": 1500,
                    "480p": 1000
                },
                "recommended_fps": [30],
                "max_file_size": 287 * 1024 * 1024,  # 287MB
                "aspect_ratios": ["9:16", "1:1"]
            },
            "twitter": {
                "video_codecs": ["h264"],
                "audio_codecs": ["aac"],
                "max_bitrate": {
                    "1080p": 5000,
                    "720p": 3000,
                    "480p": 1500
                },
                "recommended_fps": [30, 60],
                "max_file_size": 512 * 1024 * 1024,  # 512MB
                "aspect_ratios": ["16:9", "1:1", "9:16"]
            }
        }
    
    def _detect_hardware(self) -> Dict[str, Any]:
        """Detect available hardware acceleration."""
        hardware_info = {
            "gpu_available": False,
            "gpu_type": None,
            "cpu_cores": 1,
            "memory_gb": 1
        }
        
        try:
            import psutil
            hardware_info["cpu_cores"] = psutil.cpu_count()
            hardware_info["memory_gb"] = psutil.virtual_memory().total // (1024**3)
            
            # Try to detect GPU
            try:
                import subprocess
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                    capture_output=True, text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    hardware_info["gpu_available"] = True
                    hardware_info["gpu_type"] = "nvidia"
            except:
                pass
            
        except ImportError:
            pass
        
        return hardware_info
    
    async def optimize_encoding(
        self,
        input_file: str,
        target_profile: Union[str, EncodingProfile],
        output_file: Optional[str] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> EncodingResult:
        """
        Optimize encoding for specific profile.
        
        Args:
            input_file: Input file path
            target_profile: Target encoding profile
            output_file: Output file path
            custom_settings: Custom encoding settings
            
        Returns:
            Encoding result
        """
        start_time = time.time()
        
        try:
            # Get base settings
            if isinstance(target_profile, str):
                settings = self.encoding_profiles.get(target_profile)
            else:
                settings = self.encoding_profiles.get(target_profile.value)
            
            if not settings:
                raise ValueError(f"Unknown encoding profile: {target_profile}")
            
            # Apply custom settings
            if custom_settings:
                for key, value in custom_settings.items():
                    if hasattr(settings, key):
                        setattr(settings, key, value)
            
            # Optimize settings based on hardware
            optimized_settings = await self._optimize_for_hardware(settings)
            
            # Generate output path if not provided
            if not output_file:
                input_path = Path(input_file)
                output_file = str(input_path.parent / f"{input_path.stem}_optimized{input_path.suffix}")
            
            # Perform encoding
            result = await self._perform_encoding(input_file, output_file, optimized_settings)
            
            # Calculate metrics
            encoding_time = time.time() - start_time
            result.encoding_time = encoding_time
            result.settings_used = optimized_settings
            
            return result
            
        except Exception as e:
            logger.error(f"Encoding optimization failed: {str(e)}")
            return EncodingResult(
                success=False,
                input_file=input_file,
                output_file=output_file or "",
                encoding_time=time.time() - start_time,
                input_size=0,
                output_size=0,
                compression_ratio=0.0,
                error_message=str(e)
            )
    
    async def optimize_for_platform(
        self,
        input_file: str,
        platform: str,
        resolution: str = "1080p",
        output_file: Optional[str] = None
    ) -> EncodingResult:
        """
        Optimize encoding for specific platform.
        
        Args:
            input_file: Input file path
            platform: Target platform (youtube, instagram, tiktok, etc.)
            resolution: Target resolution
            output_file: Output file path
            
        Returns:
            Encoding result
        """
        try:
            platform_spec = self.platform_specs.get(platform.lower())
            if not platform_spec:
                raise ValueError(f"Unknown platform: {platform}")
            
            # Get platform-specific settings
            max_bitrate = platform_spec["max_bitrate"].get(resolution, 2500)
            video_codec = platform_spec["video_codecs"][0]
            audio_codec = platform_spec["audio_codecs"][0]
            
            # Create optimized settings
            custom_settings = {
                "video_codec": CodecType(video_codec),
                "audio_codec": CodecType(audio_codec),
                "video_bitrate": max_bitrate,
                "optimize_for_streaming": True
            }
            
            # Add platform-specific flags
            if platform.lower() == "youtube":
                custom_settings["youtube_optimized"] = True
            elif platform.lower() == "instagram":
                custom_settings["instagram_optimized"] = True
            elif platform.lower() == "tiktok":
                custom_settings["tiktok_optimized"] = True
            
            # Use appropriate base profile
            base_profile = EncodingProfile.SOCIAL_MEDIA
            if platform.lower() == "youtube":
                base_profile = EncodingProfile.STREAMING_OPTIMIZED
            
            return await self.optimize_encoding(
                input_file=input_file,
                target_profile=base_profile,
                output_file=output_file,
                custom_settings=custom_settings
            )
            
        except Exception as e:
            logger.error(f"Platform optimization failed: {str(e)}")
            return EncodingResult(
                success=False,
                input_file=input_file,
                output_file=output_file or "",
                encoding_time=0.0,
                input_size=0,
                output_size=0,
                compression_ratio=0.0,
                error_message=str(e)
            )
    
    async def analyze_encoding_efficiency(
        self,
        input_file: str,
        test_profiles: Optional[List[EncodingProfile]] = None
    ) -> Dict[str, Any]:
        """
        Analyze encoding efficiency across different profiles.
        
        Args:
            input_file: Input file to analyze
            test_profiles: Profiles to test (default: all)
            
        Returns:
            Analysis results
        """
        try:
            if not test_profiles:
                test_profiles = list(EncodingProfile)
            
            results = {}
            input_size = Path(input_file).stat().st_size
            
            for profile in test_profiles:
                try:
                    # Create temporary output file
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
                        temp_output = tmp_file.name
                    
                    # Test encoding
                    result = await self.optimize_encoding(
                        input_file=input_file,
                        target_profile=profile,
                        output_file=temp_output
                    )
                    
                    if result.success:
                        results[profile.value] = {
                            "encoding_time": result.encoding_time,
                            "compression_ratio": result.compression_ratio,
                            "output_size": result.output_size,
                            "quality_score": result.quality_score,
                            "efficiency_score": self._calculate_efficiency_score(result)
                        }
                    
                    # Clean up temp file
                    try:
                        Path(temp_output).unlink()
                    except:
                        pass
                    
                except Exception as e:
                    logger.warning(f"Failed to test profile {profile.value}: {e}")
                    continue
            
            # Find best profile
            best_profile = None
            best_score = 0
            
            for profile, metrics in results.items():
                if metrics["efficiency_score"] > best_score:
                    best_score = metrics["efficiency_score"]
                    best_profile = profile
            
            return {
                "input_file": input_file,
                "input_size": input_size,
                "tested_profiles": len(results),
                "results": results,
                "recommended_profile": best_profile,
                "best_efficiency_score": best_score
            }
            
        except Exception as e:
            logger.error(f"Encoding efficiency analysis failed: {str(e)}")
            return {"error": str(e)}
    
    def get_encoding_recommendations(
        self,
        use_case: str,
        content_type: str = "video",
        target_quality: str = "high"
    ) -> Dict[str, Any]:
        """
        Get encoding recommendations based on use case.
        
        Args:
            use_case: Use case (streaming, archive, social, web, mobile)
            content_type: Content type (video, audio)
            target_quality: Target quality level
            
        Returns:
            Encoding recommendations
        """
        recommendations = {
            "streaming": {
                "profile": EncodingProfile.STREAMING_OPTIMIZED,
                "codecs": {"video": CodecType.VIDEO_H264, "audio": CodecType.AUDIO_AAC},
                "settings": {"optimize_for_streaming": True, "two_pass_encoding": False}
            },
            "archive": {
                "profile": EncodingProfile.ARCHIVE_QUALITY,
                "codecs": {"video": CodecType.VIDEO_H265, "audio": CodecType.AUDIO_AAC},
                "settings": {"two_pass_encoding": True, "video_quality": 18}
            },
            "social": {
                "profile": EncodingProfile.SOCIAL_MEDIA,
                "codecs": {"video": CodecType.VIDEO_H264, "audio": CodecType.AUDIO_AAC},
                "settings": {"optimize_for_streaming": True, "video_bitrate": 1500}
            },
            "web": {
                "profile": EncodingProfile.WEB_OPTIMIZED,
                "codecs": {"video": CodecType.VIDEO_H264, "audio": CodecType.AUDIO_AAC},
                "settings": {"web_optimized": True, "optimize_for_streaming": True}
            },
            "mobile": {
                "profile": EncodingProfile.MOBILE_OPTIMIZED,
                "codecs": {"video": CodecType.VIDEO_H264, "audio": CodecType.AUDIO_AAC},
                "settings": {"video_preset": "fast", "video_bitrate": 1000}
            }
        }
        
        base_rec = recommendations.get(use_case, recommendations["web"])
        
        # Adjust for quality level
        quality_adjustments = {
            "low": {"video_quality": 28, "video_bitrate_factor": 0.6},
            "medium": {"video_quality": 25, "video_bitrate_factor": 0.8},
            "high": {"video_quality": 21, "video_bitrate_factor": 1.0},
            "ultra": {"video_quality": 18, "video_bitrate_factor": 1.5}
        }
        
        quality_adj = quality_adjustments.get(target_quality, quality_adjustments["high"])
        
        return {
            "use_case": use_case,
            "content_type": content_type,
            "target_quality": target_quality,
            "recommended_profile": base_rec["profile"],
            "recommended_codecs": base_rec["codecs"],
            "recommended_settings": {**base_rec["settings"], **quality_adj},
            "hardware_optimization": self.hardware_info["gpu_available"]
        }
    
    async def _optimize_for_hardware(self, settings: EncodingSettings) -> EncodingSettings:
        """Optimize settings based on available hardware."""
        optimized = settings
        
        # GPU optimization
        if self.enable_gpu and self.hardware_info["gpu_available"]:
            if self.hardware_info["gpu_type"] == "nvidia":
                # Use NVENC if available
                if settings.video_codec == CodecType.VIDEO_H264:
                    optimized.hardware_acceleration = True
                elif settings.video_codec == CodecType.VIDEO_H265:
                    optimized.hardware_acceleration = True
            
            # Adjust preset for GPU encoding
            if optimized.hardware_acceleration:
                preset_mapping = {
                    "veryslow": "slow",
                    "slower": "medium",
                    "slow": "medium",
                    "medium": "fast",
                    "fast": "fast",
                    "faster": "faster",
                    "veryfast": "faster",
                    "superfast": "fastest",
                    "ultrafast": "fastest"
                }
                if optimized.video_preset in preset_mapping:
                    optimized.video_preset = preset_mapping[optimized.video_preset]
        
        # CPU optimization
        cpu_cores = self.hardware_info["cpu_cores"]
        if cpu_cores <= 2:
            # Low-end CPU: use faster presets
            if optimized.video_preset in ["veryslow", "slower", "slow"]:
                optimized.video_preset = "medium"
        elif cpu_cores >= 8:
            # High-end CPU: can use slower presets for better quality
            if optimized.video_preset == "fast":
                optimized.video_preset = "medium"
        
        # Memory optimization
        memory_gb = self.hardware_info["memory_gb"]
        if memory_gb < 4:
            # Low memory: disable two-pass encoding
            optimized.two_pass_encoding = False
        
        return optimized
    
    async def _perform_encoding(
        self,
        input_file: str,
        output_file: str,
        settings: EncodingSettings
    ) -> EncodingResult:
        """Perform the actual encoding operation."""
        try:
            # This would integrate with actual encoding tools (FFmpeg, etc.)
            # For now, we'll simulate the encoding process
            
            input_size = Path(input_file).stat().st_size
            
            # Simulate encoding based on settings
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Calculate simulated output size based on compression
            codec_efficiency = self.codec_capabilities.get(
                settings.video_codec.value if settings.video_codec else "h264", {}
            ).get("compression_efficiency", 0.7)
            
            estimated_output_size = int(input_size * (1 - codec_efficiency))
            compression_ratio = (input_size - estimated_output_size) / input_size
            
            # Simulate quality score
            quality_score = 85.0  # Simulated quality score
            
            return EncodingResult(
                success=True,
                input_file=input_file,
                output_file=output_file,
                encoding_time=0.0,  # Will be set by caller
                input_size=input_size,
                output_size=estimated_output_size,
                compression_ratio=compression_ratio,
                quality_score=quality_score,
                bitrate_achieved=settings.video_bitrate
            )
            
        except Exception as e:
            logger.error(f"Encoding operation failed: {str(e)}")
            return EncodingResult(
                success=False,
                input_file=input_file,
                output_file=output_file,
                encoding_time=0.0,
                input_size=0,
                output_size=0,
                compression_ratio=0.0,
                error_message=str(e)
            )
    
    def _calculate_efficiency_score(self, result: EncodingResult) -> float:
        """Calculate encoding efficiency score."""
        try:
            # Score based on compression ratio, quality, and speed
            compression_score = min(result.compression_ratio * 100, 100)
            quality_score = result.quality_score or 50
            
            # Speed score (inverse of encoding time, normalized)
            speed_score = max(0, 100 - (result.encoding_time * 10))
            
            # Weighted average
            efficiency_score = (compression_score * 0.4 + quality_score * 0.4 + speed_score * 0.2)
            
            return min(100, max(0, efficiency_score))
            
        except Exception:
            return 0.0


class CodecOptimizer:
    """
Codec-specific optimization utilities."""
    
    def __init__(self, encoding_manager: Optional[EncodingManager] = None):
        self.encoding_manager = encoding_manager or EncodingManager()
    
    def get_optimal_codec(
        self,
        content_type: str,
        use_case: str,
        hardware_acceleration: bool = True
    ) -> CodecType:
        """
Get optimal codec for specific requirements."""
        codec_recommendations = {
            "video": {
                "streaming": CodecType.VIDEO_H264,
                "archive": CodecType.VIDEO_H265,
                "web": CodecType.VIDEO_H264,
                "mobile": CodecType.VIDEO_H264,
                "social": CodecType.VIDEO_H264
            },
            "audio": {
                "streaming": CodecType.AUDIO_AAC,
                "archive": CodecType.AUDIO_AAC,
                "web": CodecType.AUDIO_AAC,
                "mobile": CodecType.AUDIO_AAC,
                "social": CodecType.AUDIO_AAC
            }
        }
        
        return codec_recommendations.get(content_type, {}).get(
            use_case, 
            CodecType.VIDEO_H264 if content_type == "video" else CodecType.AUDIO_AAC
        )


class QualityManager:
    """Quality management and optimization."""
    
    def __init__(self, encoding_manager: Optional[EncodingManager] = None):
        self.encoding_manager = encoding_manager or EncodingManager()
    
    def calculate_optimal_bitrate(
        self,
        resolution: str,
        fps: int,
        content_complexity: str = "medium"
    ) -> int:
        """Calculate optimal bitrate for given parameters."""
        base_bitrates = {
            "480p": 1000,
            "720p": 2500,
            "1080p": 5000,
            "1440p": 10000,
            "2160p": 20000
        }
        
        base_bitrate = base_bitrates.get(resolution, 2500)
        
        # Adjust for FPS
        fps_factor = fps / 30.0
        
        # Adjust for content complexity
        complexity_factors = {
            "low": 0.7,      # Static content, low motion
            "medium": 1.0,   # Normal content
            "high": 1.4,     # High motion, complex scenes
            "ultra": 1.8     # Gaming, very high motion
        }
        
        complexity_factor = complexity_factors.get(content_complexity, 1.0)
        
        optimal_bitrate = int(base_bitrate * fps_factor * complexity_factor)
        
        return optimal_bitrate
    
    def get_quality_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get quality presets for different use cases."""
        return {
            "draft": {
                "description": "Fast encoding for drafts and previews",
                "video_quality": 30,
                "video_preset": "ultrafast",
                "two_pass": False
            },
            "balanced": {
                "description": "Balanced quality and speed",
                "video_quality": 23,
                "video_preset": "medium",
                "two_pass": False
            },
            "high_quality": {
                "description": "High quality for final outputs",
                "video_quality": 20,
                "video_preset": "slow",
                "two_pass": True
            },
            "archival": {
                "description": "Maximum quality for archival",
                "video_quality": 16,
                "video_preset": "veryslow",
                "two_pass": True
            }
        }
