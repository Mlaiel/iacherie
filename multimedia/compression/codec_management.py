"""Codec Management System
Enterprise codec management and compatibility handling.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Set
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

class CodecType(Enum):
    """Types of codecs."""
    AUDIO = "audio"
    VIDEO = "video"
    CONTAINER = "container"

@dataclass
class CodecInfo:
    """Codec information and capabilities."""
    name: str
    codec_type: CodecType
    extensions: List[str]
    mime_types: List[str]
    quality_range: tuple  # (min, max)
    compression_efficiency: float  # 0-1 scale
    encoding_speed: str  # slow, medium, fast
    hardware_acceleration: bool
    platform_support: Dict[str, bool]
    license_type: str  # free, proprietary, patent_encumbered
    description: str

class CodecManager:
    """Enterprise codec management system."""
    
    def __init__(self):
        """Initialize the codec manager."""
        self.codecs = self._initialize_codec_database()
        self.compatibility_matrix = self._build_compatibility_matrix()
        
    def _initialize_codec_database(self) -> Dict[str, CodecInfo]:
        """Initialize the codec database with supported codecs."""
        codecs = {}
        
        # Audio Codecs
        codecs["mp3"] = CodecInfo(
            name="MP3",
            codec_type=CodecType.AUDIO,
            extensions=[".mp3"],
            mime_types=["audio/mpeg"],
            quality_range=(32, 320),
            compression_efficiency=0.7,
            encoding_speed="fast",
            hardware_acceleration=True,
            platform_support={
                "web": True,
                "mobile": True,
                "desktop": True,
                "smart_tv": True
            },
            license_type="patent_encumbered",
            description="MPEG Audio Layer III - Universal audio codec"
        )
        
        codecs["aac"] = CodecInfo(
            name="AAC",
            codec_type=CodecType.AUDIO,
            extensions=[".aac", ".m4a"],
            mime_types=["audio/aac", "audio/mp4"],
            quality_range=(64, 320),
            compression_efficiency=0.8,
            encoding_speed="medium",
            hardware_acceleration=True,
            platform_support={
                "web": True,
                "mobile": True,
                "desktop": True,
                "smart_tv": True
            },
            license_type="patent_encumbered",
            description="Advanced Audio Coding - High-quality audio codec"
        )
        
        codecs["opus"] = CodecInfo(
            name="Opus",
            codec_type=CodecType.AUDIO,
            extensions=[".opus"],
            mime_types=["audio/opus"],
            quality_range=(8, 512),
            compression_efficiency=0.9,
            encoding_speed="medium",
            hardware_acceleration=False,
            platform_support={
                "web": True,
                "mobile": True,
                "desktop": True,
                "smart_tv": False
            },
            license_type="free",
            description="Modern audio codec optimized for internet streaming"
        )
        
        codecs["flac"] = CodecInfo(
            name="FLAC",
            codec_type=CodecType.AUDIO,
            extensions=[".flac"],
            mime_types=["audio/flac"],
            quality_range=(0, 8),  # Compression levels
            compression_efficiency=0.5,  # Lossless
            encoding_speed="medium",
            hardware_acceleration=False,
            platform_support={
                "web": True,
                "mobile": True,
                "desktop": True,
                "smart_tv": False
            },
            license_type="free",
            description="Free Lossless Audio Codec"
        )
        
        # Video Codecs
        codecs["h264"] = CodecInfo(
            name="H.264/AVC",
            codec_type=CodecType.VIDEO,
            extensions=[".mp4", ".m4v"],
            mime_types=["video/mp4", "video/h264"],
            quality_range=(18, 51),  # CRF values
            compression_efficiency=0.7,
            encoding_speed="medium",
            hardware_acceleration=True,
            platform_support={
                "web": True,
                "mobile": True,
                "desktop": True,
                "smart_tv": True
            },
            license_type="patent_encumbered",
            description="Advanced Video Coding - Most widely supported video codec"
        )
        
        codecs["h265"] = CodecInfo(
            name="H.265/HEVC",
            codec_type=CodecType.VIDEO,
            extensions=[".mp4", ".m4v", ".hevc"],
            mime_types=["video/mp4", "video/hevc"],
            quality_range=(18, 51),
            compression_efficiency=0.85,
            encoding_speed="slow",
            hardware_acceleration=True,
            platform_support={
                "web": False,
                "mobile": True,
                "desktop": True,
                "smart_tv": True
            },
            license_type="patent_encumbered",
            description="High Efficiency Video Coding - Next-gen compression"
        )
        
        codecs["av1"] = CodecInfo(
            name="AV1",
            codec_type=CodecType.VIDEO,
            extensions=[".mp4", ".webm"],
            mime_types=["video/mp4", "video/webm"],
            quality_range=(0, 63),
            compression_efficiency=0.9,
            encoding_speed="slow",
            hardware_acceleration=True,
            platform_support={
                "web": True,
                "mobile": False,
                "desktop": True,
                "smart_tv": False
            },
            license_type="free",
            description="AOMedia Video 1 - Royalty-free next-gen codec"
        )
        
        codecs["vp9"] = CodecInfo(
            name="VP9",
            codec_type=CodecType.VIDEO,
            extensions=[".webm"],
            mime_types=["video/webm"],
            quality_range=(0, 63),
            compression_efficiency=0.8,
            encoding_speed="slow",
            hardware_acceleration=True,
            platform_support={
                "web": True,
                "mobile": True,
                "desktop": True,
                "smart_tv": False
            },
            license_type="free",
            description="Google VP9 - Open-source video codec"
        )
        
        return codecs
    
    def _build_compatibility_matrix(self) -> Dict[str, Dict[str, float]]:
        """Build codec compatibility matrix."""
        # Compatibility scores between codecs (0-1, higher is better)
        return {
            "mp3": {"aac": 0.8, "opus": 0.6, "flac": 0.4},
            "aac": {"mp3": 0.8, "opus": 0.7, "flac": 0.5},
            "h264": {"h265": 0.9, "av1": 0.7, "vp9": 0.6},
            "h265": {"h264": 0.9, "av1": 0.8, "vp9": 0.6},
            "av1": {"h265": 0.8, "h264": 0.7, "vp9": 0.8},
            "vp9": {"av1": 0.8, "h264": 0.6, "h265": 0.6}
        }
    
    def get_codec_info(self, codec_name: str) -> Optional[CodecInfo]:
        """Get information about a specific codec."""
        return self.codecs.get(codec_name.lower())
    
    def list_codecs_by_type(self, codec_type: CodecType) -> List[CodecInfo]:
        """List all codecs of a specific type."""
        return [codec for codec in self.codecs.values() 
                if codec.codec_type == codec_type]
    
    def find_compatible_codecs(
        self,
        source_codec: str,
        target_platform: str = "web",
        license_preference: Optional[str] = None
    ) -> List[tuple]:
        """
        Find compatible codecs for conversion.
        
        Args:
            source_codec: Source codec name
            target_platform: Target platform
            license_preference: Preferred license type
            
        Returns:
            List of (codec_name, compatibility_score) tuples
        """
        source_codec = source_codec.lower()
        if source_codec not in self.codecs:
            return []
        
        compatible_codecs = []
        source_type = self.codecs[source_codec].codec_type
        
        for codec_name, codec_info in self.codecs.items():
            if codec_info.codec_type != source_type:
                continue
            
            # Check platform support
            if not codec_info.platform_support.get(target_platform, False):
                continue
            
            # Check license preference
            if (license_preference and 
                codec_info.license_type != license_preference):
                continue
            
            # Calculate compatibility score
            compatibility = self.compatibility_matrix.get(source_codec, {}).get(
                codec_name, 0.5
            )
            
            # Boost score for efficiency and speed
            efficiency_boost = codec_info.compression_efficiency * 0.2
            speed_boost = {"fast": 0.1, "medium": 0.05, "slow": 0.0}[
                codec_info.encoding_speed
            ]
            
            final_score = compatibility + efficiency_boost + speed_boost
            
            compatible_codecs.append((codec_name, final_score))
        
        # Sort by compatibility score
        compatible_codecs.sort(key=lambda x: x[1], reverse=True)
        
        return compatible_codecs
    
    def recommend_codec(
        self,
        use_case: str,
        media_type: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Recommend optimal codec for specific use case.
        
        Args:
            use_case: Use case (web, mobile, streaming, archive, etc.)
            media_type: Type of media (audio, video)
            constraints: Additional constraints
            
        Returns:
            Recommended codec name
        """
        constraints = constraints or {}
        codec_type = CodecType.AUDIO if media_type == "audio" else CodecType.VIDEO
        
        candidates = self.list_codecs_by_type(codec_type)
        
        # Filter by platform support
        if use_case in ["web", "mobile", "desktop", "smart_tv"]:
            candidates = [c for c in candidates 
                         if c.platform_support.get(use_case, False)]
        
        # Filter by license if specified
        license_pref = constraints.get("license")
        if license_pref:
            candidates = [c for c in candidates if c.license_type == license_pref]
        
        # Filter by hardware acceleration if needed
        if constraints.get("hardware_acceleration"):
            candidates = [c for c in candidates if c.hardware_acceleration]
        
        if not candidates:
            return None
        
        # Score candidates based on use case
        scored_candidates = []
        
        for codec in candidates:
            score = 0.0
            
            # Base score from compression efficiency
            score += codec.compression_efficiency * 0.4
            
            # Use case specific scoring
            if use_case == "web":
                # Prioritize broad support and efficiency
                if codec.name in ["H.264/AVC", "VP9", "AAC", "MP3"]:
                    score += 0.3
            elif use_case == "mobile":
                # Prioritize efficiency and hardware acceleration
                score += 0.2 if codec.hardware_acceleration else 0.0
                score += codec.compression_efficiency * 0.2
            elif use_case == "streaming":
                # Prioritize efficiency and encoding speed
                speed_scores = {"fast": 0.3, "medium": 0.2, "slow": 0.1}
                score += speed_scores[codec.encoding_speed]
            elif use_case == "archive":
                # Prioritize quality and future compatibility
                if codec.license_type == "free":
                    score += 0.2
                if codec.name in ["FLAC", "AV1", "H.265/HEVC"]:
                    score += 0.3
            
            scored_candidates.append((codec.name.lower().replace("/", "").replace(".", ""), score))
        
        # Return best candidate
        if scored_candidates:
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            return scored_candidates[0][0]
        
        return None
    
    def validate_codec_support(
        self,
        codec_name: str,
        target_platforms: List[str]
    ) -> Dict[str, Any]:
        """Validate codec support across platforms."""
        codec = self.get_codec_info(codec_name)
        if not codec:
            return {
                "valid": False,
                "error": f"Unknown codec: {codec_name}"
            }
        
        platform_support = {}
        unsupported_platforms = []
        
        for platform in target_platforms:
            supported = codec.platform_support.get(platform, False)
            platform_support[platform] = supported
            
            if not supported:
                unsupported_platforms.append(platform)
        
        return {
            "valid": len(unsupported_platforms) == 0,
            "codec": codec.name,
            "platform_support": platform_support,
            "unsupported_platforms": unsupported_platforms,
            "fallback_recommendations": self._get_fallback_recommendations(
                codec_name, unsupported_platforms
            ) if unsupported_platforms else []
        }
    
    def _get_fallback_recommendations(
        self,
        codec_name: str,
        unsupported_platforms: List[str]
    ) -> List[Dict[str, Any]]:
        """Get fallback codec recommendations for unsupported platforms."""
        recommendations = []
        
        for platform in unsupported_platforms:
            compatible = self.find_compatible_codecs(codec_name, platform)
            
            if compatible:
                best_codec = compatible[0][0]
                codec_info = self.get_codec_info(best_codec)
                
                recommendations.append({
                    "platform": platform,
                    "recommended_codec": best_codec,
                    "codec_name": codec_info.name,
                    "compatibility_score": compatible[0][1],
                    "reason": f"Better platform support for {platform}"
                })
        
        return recommendations
    
    def get_encoding_presets(self, codec_name: str) -> Dict[str, Any]:
        """Get encoding presets for a specific codec."""
        codec = self.get_codec_info(codec_name)
        if not codec:
            return {}
        
        if codec.codec_type == CodecType.AUDIO:
            return self._get_audio_presets(codec_name)
        elif codec.codec_type == CodecType.VIDEO:
            return self._get_video_presets(codec_name)
        
        return {}
    
    def _get_audio_presets(self, codec_name: str) -> Dict[str, Any]:
        """Get audio encoding presets."""
        codec = self.get_codec_info(codec_name)
        min_quality, max_quality = codec.quality_range
        
        if codec_name in ["mp3", "aac"]:
            return {
                "low": {"bitrate": min_quality, "vbr": False},
                "medium": {"bitrate": (min_quality + max_quality) // 2, "vbr": True},
                "high": {"bitrate": max_quality, "vbr": True},
                "voice": {"bitrate": 64, "mono": True},
                "music": {"bitrate": 256, "stereo": True}
            }
        elif codec_name == "opus":
            return {
                "low": {"bitrate": 64, "application": "voip"},
                "medium": {"bitrate": 128, "application": "audio"},
                "high": {"bitrate": 256, "application": "restricted_lowdelay"},
                "voice": {"bitrate": 32, "application": "voip"},
                "music": {"bitrate": 192, "application": "audio"}
            }
        elif codec_name == "flac":
            return {
                "fast": {"compression_level": 0},
                "medium": {"compression_level": 5},
                "slow": {"compression_level": 8}
            }
        
        return {}
    
    def _get_video_presets(self, codec_name: str) -> Dict[str, Any]:
        """Get video encoding presets."""
        if codec_name in ["h264", "h265"]:
            return {
                "ultrafast": {"preset": "ultrafast", "crf": 28},
                "fast": {"preset": "fast", "crf": 23},
                "medium": {"preset": "medium", "crf": 23},
                "slow": {"preset": "slow", "crf": 20},
                "veryslow": {"preset": "veryslow", "crf": 18},
                "streaming": {"preset": "fast", "tune": "zerolatency", "crf": 25},
                "archive": {"preset": "slow", "crf": 18, "two_pass": True}
            }
        elif codec_name in ["av1", "vp9"]:
            return {
                "fast": {"cpu_used": 8, "crf": 30},
                "medium": {"cpu_used": 4, "crf": 25},
                "slow": {"cpu_used": 1, "crf": 20},
                "archive": {"cpu_used": 0, "crf": 15, "two_pass": True}
            }
        
        return {}
    
    def analyze_codec_trends(self) -> Dict[str, Any]:
        """Analyze codec adoption trends and recommendations."""
        audio_codecs = self.list_codecs_by_type(CodecType.AUDIO)
        video_codecs = self.list_codecs_by_type(CodecType.VIDEO)
        
        # Calculate platform coverage
        platforms = ["web", "mobile", "desktop", "smart_tv"]
        
        codec_scores = {}
        
        for codec in audio_codecs + video_codecs:
            platform_score = sum(codec.platform_support.get(p, 0) for p in platforms) / len(platforms)
            
            # Future-proofing score
            future_score = 1.0 if codec.license_type == "free" else 0.7
            
            # Technology score
            tech_score = codec.compression_efficiency
            
            overall_score = (platform_score * 0.4 + future_score * 0.3 + tech_score * 0.3)
            
            codec_scores[codec.name] = {
                "overall_score": overall_score,
                "platform_coverage": platform_score,
                "future_proof": future_score,
                "efficiency": tech_score,
                "recommendation": "adopt" if overall_score > 0.8 else "consider" if overall_score > 0.6 else "avoid"
            }
        
        return {
            "codec_rankings": dict(sorted(codec_scores.items(), key=lambda x: x[1]["overall_score"], reverse=True)),
            "emerging_codecs": [name for name, score in codec_scores.items() if score["future_proof"] == 1.0],
            "legacy_codecs": [name for name, score in codec_scores.items() if score["recommendation"] == "avoid"],
            "recommendations": {
                "audio": {
                    "web": "AAC or Opus",
                    "mobile": "AAC",
                    "streaming": "Opus",
                    "archive": "FLAC"
                },
                "video": {
                    "web": "H.264 with VP9 fallback",
                    "mobile": "H.264 or H.265",
                    "streaming": "H.264 with low latency",
                    "archive": "AV1 or H.265"
                }
            }
        }