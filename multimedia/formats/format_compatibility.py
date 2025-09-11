"""
Format Compatibility Management System
Cross-format compatibility analysis and optimization for Ainflue Platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class CompatibilityLevel(Enum):
    """Compatibility levels between formats"""
    PERFECT = "perfect"  # No loss of features or quality
    EXCELLENT = "excellent"  # Minimal loss, all major features preserved
    GOOD = "good"  # Some feature loss but acceptable quality
    FAIR = "fair"  # Significant feature loss or quality degradation
    POOR = "poor"  # Major limitations or quality issues
    INCOMPATIBLE = "incompatible"  # Cannot convert or major data loss


class ConversionComplexity(Enum):
    """Complexity levels for format conversions"""
    TRIVIAL = "trivial"  # Direct copy or simple remux
    SIMPLE = "simple"  # Basic conversion, no re-encoding
    MODERATE = "moderate"  # Re-encoding required but straightforward
    COMPLEX = "complex"  # Multiple steps, quality considerations
    VERY_COMPLEX = "very_complex"  # Requires specialized tools/algorithms


@dataclass
class CompatibilityResult:
    """Result of compatibility analysis"""
    source_format: str
    target_format: str
    compatibility_level: CompatibilityLevel
    conversion_complexity: ConversionComplexity
    quality_loss_percentage: float  # 0-100%
    supported_features: List[str]
    lost_features: List[str]
    conversion_time_factor: float  # Multiplier vs real-time
    file_size_factor: float  # Multiplier vs source size
    notes: List[str]
    recommendations: List[str]


@dataclass
class FormatProfile:
    """Comprehensive format profile for compatibility analysis"""
    name: str
    category: str  # video, audio, image, container
    codec: str
    container: str
    features: Set[str]
    quality_range: Tuple[int, int]  # 1-10 scale
    compression_efficiency: int  # 1-10 scale
    hardware_support: bool
    streaming_optimized: bool
    open_source: bool
    patent_free: bool
    web_compatible: bool
    mobile_optimized: bool
    professional_grade: bool


class FormatCompatibilityMatrix:
    """Comprehensive format compatibility analysis system"""
    
    def __init__(self):
        self.format_profiles: Dict[str, FormatProfile] = {}
        self.compatibility_cache: Dict[Tuple[str, str], CompatibilityResult] = {}
        self.conversion_rules: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self._initialize_format_profiles()
        self._initialize_conversion_rules()
    
    def _initialize_format_profiles(self):
        """Initialize comprehensive format profiles"""
        
        # Video Formats
        self.format_profiles["h264_mp4"] = FormatProfile(
            name="H.264/MP4",
            category="video",
            codec="h264",
            container="mp4",
            features={"hardware_decode", "streaming", "editing", "subtitles", "chapters"},
            quality_range=(6, 9),
            compression_efficiency=8,
            hardware_support=True,
            streaming_optimized=True,
            open_source=False,
            patent_free=False,
            web_compatible=True,
            mobile_optimized=True,
            professional_grade=True
        )
        
        self.format_profiles["h265_mp4"] = FormatProfile(
            name="H.265/MP4",
            category="video",
            codec="h265",
            container="mp4",
            features={"hardware_decode", "streaming", "editing", "subtitles", "chapters", "hdr", "4k", "8k"},
            quality_range=(7, 10),
            compression_efficiency=9,
            hardware_support=True,
            streaming_optimized=True,
            open_source=False,
            patent_free=False,
            web_compatible=True,
            mobile_optimized=True,
            professional_grade=True
        )
        
        self.format_profiles["av1_mp4"] = FormatProfile(
            name="AV1/MP4",
            category="video",
            codec="av1",
            container="mp4",
            features={"streaming", "editing", "subtitles", "chapters", "hdr", "4k", "8k"},
            quality_range=(8, 10),
            compression_efficiency=10,
            hardware_support=True,
            streaming_optimized=True,
            open_source=True,
            patent_free=True,
            web_compatible=True,
            mobile_optimized=False,
            professional_grade=True
        )
        
        self.format_profiles["vp9_webm"] = FormatProfile(
            name="VP9/WebM",
            category="video",
            codec="vp9",
            container="webm",
            features={"streaming", "editing", "subtitles", "hdr", "4k"},
            quality_range=(7, 9),
            compression_efficiency=8,
            hardware_support=True,
            streaming_optimized=True,
            open_source=True,
            patent_free=True,
            web_compatible=True,
            mobile_optimized=False,
            professional_grade=False
        )
        
        # Audio Formats
        self.format_profiles["aac_mp4"] = FormatProfile(
            name="AAC/MP4",
            category="audio",
            codec="aac",
            container="mp4",
            features={"streaming", "editing", "metadata", "surround"},
            quality_range=(6, 9),
            compression_efficiency=8,
            hardware_support=True,
            streaming_optimized=True,
            open_source=False,
            patent_free=False,
            web_compatible=True,
            mobile_optimized=True,
            professional_grade=True
        )
        
        self.format_profiles["opus_webm"] = FormatProfile(
            name="Opus/WebM",
            category="audio",
            codec="opus",
            container="webm",
            features={"streaming", "low_latency", "metadata"},
            quality_range=(8, 10),
            compression_efficiency=9,
            hardware_support=False,
            streaming_optimized=True,
            open_source=True,
            patent_free=True,
            web_compatible=True,
            mobile_optimized=True,
            professional_grade=False
        )
        
        self.format_profiles["flac"] = FormatProfile(
            name="FLAC",
            category="audio",
            codec="flac",
            container="flac",
            features={"lossless", "metadata", "editing"},
            quality_range=(10, 10),
            compression_efficiency=6,
            hardware_support=False,
            streaming_optimized=False,
            open_source=True,
            patent_free=True,
            web_compatible=True,
            mobile_optimized=False,
            professional_grade=True
        )
        
        self.format_profiles["mp3"] = FormatProfile(
            name="MP3",
            category="audio",
            codec="mp3",
            container="mp3",
            features={"streaming", "metadata", "universal_support"},
            quality_range=(4, 7),
            compression_efficiency=6,
            hardware_support=True,
            streaming_optimized=True,
            open_source=False,
            patent_free=False,
            web_compatible=True,
            mobile_optimized=True,
            professional_grade=False
        )
        
        # Image Formats
        self.format_profiles["jpeg"] = FormatProfile(
            name="JPEG",
            category="image",
            codec="jpeg",
            container="jpeg",
            features={"metadata", "universal_support", "progressive"},
            quality_range=(3, 8),
            compression_efficiency=6,
            hardware_support=True,
            streaming_optimized=False,
            open_source=True,
            patent_free=True,
            web_compatible=True,
            mobile_optimized=True,
            professional_grade=False
        )
        
        self.format_profiles["webp"] = FormatProfile(
            name="WebP",
            category="image",
            codec="webp",
            container="webp",
            features={"transparency", "animation", "lossless", "metadata"},
            quality_range=(6, 9),
            compression_efficiency=8,
            hardware_support=False,
            streaming_optimized=False,
            open_source=True,
            patent_free=True,
            web_compatible=True,
            mobile_optimized=True,
            professional_grade=False
        )
        
        self.format_profiles["avif"] = FormatProfile(
            name="AVIF",
            category="image",
            codec="av1",
            container="avif",
            features={"transparency", "animation", "lossless", "hdr", "metadata"},
            quality_range=(7, 10),
            compression_efficiency=9,
            hardware_support=True,
            streaming_optimized=False,
            open_source=True,
            patent_free=True,
            web_compatible=True,
            mobile_optimized=True,
            professional_grade=True
        )
        
        self.format_profiles["png"] = FormatProfile(
            name="PNG",
            category="image",
            codec="png",
            container="png",
            features={"transparency", "lossless", "metadata"},
            quality_range=(10, 10),
            compression_efficiency=4,
            hardware_support=True,
            streaming_optimized=False,
            open_source=True,
            patent_free=True,
            web_compatible=True,
            mobile_optimized=True,
            professional_grade=True
        )
    
    def _initialize_conversion_rules(self):
        """Initialize format conversion rules and compatibility matrix"""
        
        # Video conversions
        self.conversion_rules[("h264_mp4", "h265_mp4")] = {
            "compatibility": CompatibilityLevel.EXCELLENT,
            "complexity": ConversionComplexity.MODERATE,
            "quality_loss": 5.0,
            "time_factor": 3.0,
            "size_factor": 0.7,
            "notes": ["Improved compression efficiency", "Better quality at same bitrate"],
            "recommendations": ["Use for 4K+ content", "Consider encoding time"]
        }
        
        self.conversion_rules[("h265_mp4", "h264_mp4")] = {
            "compatibility": CompatibilityLevel.GOOD,
            "complexity": ConversionComplexity.MODERATE,
            "quality_loss": 15.0,
            "time_factor": 2.0,
            "size_factor": 1.4,
            "notes": ["Better compatibility", "Larger file size"],
            "recommendations": ["Use for older devices", "Maintain higher bitrate"]
        }
        
        self.conversion_rules[("h264_mp4", "av1_mp4")] = {
            "compatibility": CompatibilityLevel.EXCELLENT,
            "complexity": ConversionComplexity.COMPLEX,
            "quality_loss": 3.0,
            "time_factor": 8.0,
            "size_factor": 0.6,
            "notes": ["Significant compression gains", "Very slow encoding"],
            "recommendations": ["Use for archival", "Consider hardware encoders"]
        }
        
        self.conversion_rules[("h264_mp4", "vp9_webm")] = {
            "compatibility": CompatibilityLevel.GOOD,
            "complexity": ConversionComplexity.MODERATE,
            "quality_loss": 10.0,
            "time_factor": 4.0,
            "size_factor": 0.8,
            "notes": ["Open source alternative", "Good web compatibility"],
            "recommendations": ["Use for web streaming", "Test browser support"]
        }
        
        # Audio conversions
        self.conversion_rules[("flac", "aac_mp4")] = {
            "compatibility": CompatibilityLevel.GOOD,
            "complexity": ConversionComplexity.SIMPLE,
            "quality_loss": 20.0,
            "time_factor": 0.5,
            "size_factor": 0.3,
            "notes": ["Lossy conversion from lossless", "Significant size reduction"],
            "recommendations": ["Use high bitrate", "Consider use case"]
        }
        
        self.conversion_rules[("mp3", "opus_webm")] = {
            "compatibility": CompatibilityLevel.EXCELLENT,
            "complexity": ConversionComplexity.SIMPLE,
            "quality_loss": 5.0,
            "time_factor": 0.3,
            "size_factor": 0.7,
            "notes": ["Better quality at lower bitrate", "Modern codec"],
            "recommendations": ["Use for streaming", "Check browser support"]
        }
        
        self.conversion_rules[("aac_mp4", "mp3")] = {
            "compatibility": CompatibilityLevel.FAIR,
            "complexity": ConversionComplexity.SIMPLE,
            "quality_loss": 25.0,
            "time_factor": 0.4,
            "size_factor": 1.2,
            "notes": ["Double lossy compression", "Universal compatibility"],
            "recommendations": ["Avoid if possible", "Use original source"]
        }
        
        # Image conversions
        self.conversion_rules[("png", "webp")] = {
            "compatibility": CompatibilityLevel.EXCELLENT,
            "complexity": ConversionComplexity.SIMPLE,
            "quality_loss": 0.0,
            "time_factor": 0.2,
            "size_factor": 0.6,
            "notes": ["Lossless conversion possible", "Significant size reduction"],
            "recommendations": ["Use lossless WebP", "Fallback for older browsers"]
        }
        
        self.conversion_rules[("jpeg", "avif")] = {
            "compatibility": CompatibilityLevel.EXCELLENT,
            "complexity": ConversionComplexity.SIMPLE,
            "quality_loss": 0.0,
            "time_factor": 0.3,
            "size_factor": 0.5,
            "notes": ["Better compression", "Next-gen format"],
            "recommendations": ["Use for modern browsers", "Provide JPEG fallback"]
        }
        
        self.conversion_rules[("webp", "jpeg")] = {
            "compatibility": CompatibilityLevel.GOOD,
            "complexity": ConversionComplexity.SIMPLE,
            "quality_loss": 15.0,
            "time_factor": 0.1,
            "size_factor": 1.5,
            "notes": ["Universal compatibility", "Transparency loss"],
            "recommendations": ["Check for transparency", "Use high quality"]
        }
    
    def analyze_compatibility(self, source_format: str, target_format: str) -> CompatibilityResult:
        """Analyze compatibility between two formats"""
        
        # Check cache first
        cache_key = (source_format, target_format)
        if cache_key in self.compatibility_cache:
            return self.compatibility_cache[cache_key]
        
        # Get format profiles
        source_profile = self.format_profiles.get(source_format)
        target_profile = self.format_profiles.get(target_format)
        
        if not source_profile or not target_profile:
            result = CompatibilityResult(
                source_format=source_format,
                target_format=target_format,
                compatibility_level=CompatibilityLevel.INCOMPATIBLE,
                conversion_complexity=ConversionComplexity.VERY_COMPLEX,
                quality_loss_percentage=100.0,
                supported_features=[],
                lost_features=[],
                conversion_time_factor=0.0,
                file_size_factor=0.0,
                notes=["Format not recognized"],
                recommendations=["Use supported formats"]
            )
            self.compatibility_cache[cache_key] = result
            return result
        
        # Same format
        if source_format == target_format:
            result = CompatibilityResult(
                source_format=source_format,
                target_format=target_format,
                compatibility_level=CompatibilityLevel.PERFECT,
                conversion_complexity=ConversionComplexity.TRIVIAL,
                quality_loss_percentage=0.0,
                supported_features=list(source_profile.features),
                lost_features=[],
                conversion_time_factor=0.0,
                file_size_factor=1.0,
                notes=["No conversion needed"],
                recommendations=["Direct copy"]
            )
            self.compatibility_cache[cache_key] = result
            return result
        
        # Check for explicit conversion rules
        if cache_key in self.conversion_rules:
            rule = self.conversion_rules[cache_key]
            result = CompatibilityResult(
                source_format=source_format,
                target_format=target_format,
                compatibility_level=rule["compatibility"],
                conversion_complexity=rule["complexity"],
                quality_loss_percentage=rule["quality_loss"],
                supported_features=list(source_profile.features & target_profile.features),
                lost_features=list(source_profile.features - target_profile.features),
                conversion_time_factor=rule["time_factor"],
                file_size_factor=rule["size_factor"],
                notes=rule["notes"],
                recommendations=rule["recommendations"]
            )
            self.compatibility_cache[cache_key] = result
            return result
        
        # Calculate compatibility based on profiles
        result = self._calculate_compatibility(source_profile, target_profile)
        self.compatibility_cache[cache_key] = result
        return result
    
    def _calculate_compatibility(self, 
                               source_profile: FormatProfile, 
                               target_profile: FormatProfile) -> CompatibilityResult:
        """Calculate compatibility based on format profiles"""
        
        # Different categories are generally incompatible
        if source_profile.category != target_profile.category:
            return CompatibilityResult(
                source_format=source_profile.name,
                target_format=target_profile.name,
                compatibility_level=CompatibilityLevel.INCOMPATIBLE,
                conversion_complexity=ConversionComplexity.VERY_COMPLEX,
                quality_loss_percentage=100.0,
                supported_features=[],
                lost_features=list(source_profile.features),
                conversion_time_factor=0.0,
                file_size_factor=0.0,
                notes=["Different media categories"],
                recommendations=["Use format of same category"]
            )
        
        # Calculate feature compatibility
        common_features = source_profile.features & target_profile.features
        lost_features = source_profile.features - target_profile.features
        feature_retention = len(common_features) / len(source_profile.features) if source_profile.features else 1.0
        
        # Calculate quality compatibility
        source_quality_avg = sum(source_profile.quality_range) / 2
        target_quality_avg = sum(target_profile.quality_range) / 2
        quality_ratio = target_quality_avg / source_quality_avg if source_quality_avg > 0 else 1.0
        
        # Calculate compatibility level
        compatibility_score = (feature_retention * 0.4 + 
                             min(quality_ratio, 1.0) * 0.3 + 
                             (target_profile.compression_efficiency / 10) * 0.3)
        
        if compatibility_score >= 0.9:
            compatibility_level = CompatibilityLevel.PERFECT
        elif compatibility_score >= 0.8:
            compatibility_level = CompatibilityLevel.EXCELLENT
        elif compatibility_score >= 0.7:
            compatibility_level = CompatibilityLevel.GOOD
        elif compatibility_score >= 0.5:
            compatibility_level = CompatibilityLevel.FAIR
        else:
            compatibility_level = CompatibilityLevel.POOR
        
        # Estimate conversion complexity
        complexity = ConversionComplexity.MODERATE
        if source_profile.codec == target_profile.codec:
            complexity = ConversionComplexity.SIMPLE
        elif target_profile.compression_efficiency > source_profile.compression_efficiency + 2:
            complexity = ConversionComplexity.COMPLEX
        
        # Estimate quality loss
        quality_loss = max(0, (source_quality_avg - target_quality_avg) / source_quality_avg * 100)
        if lost_features:
            quality_loss += len(lost_features) * 5  # 5% per lost feature
        
        # Estimate conversion factors
        efficiency_ratio = target_profile.compression_efficiency / source_profile.compression_efficiency
        time_factor = 2.0 / efficiency_ratio if efficiency_ratio < 1 else efficiency_ratio
        size_factor = 1.0 / efficiency_ratio
        
        # Generate notes and recommendations
        notes = []
        recommendations = []
        
        if quality_loss > 20:
            notes.append("Significant quality loss expected")
            recommendations.append("Consider higher quality settings")
        
        if lost_features:
            notes.append(f"Features lost: {', '.join(lost_features)}")
            recommendations.append("Check if lost features are required")
        
        if target_profile.compression_efficiency > source_profile.compression_efficiency:
            notes.append("Better compression efficiency")
            recommendations.append("Good choice for storage/bandwidth")
        
        if not target_profile.web_compatible and source_profile.web_compatible:
            notes.append("Loss of web compatibility")
            recommendations.append("Consider web-compatible alternative")
        
        return CompatibilityResult(
            source_format=source_profile.name,
            target_format=target_profile.name,
            compatibility_level=compatibility_level,
            conversion_complexity=complexity,
            quality_loss_percentage=min(quality_loss, 100.0),
            supported_features=list(common_features),
            lost_features=list(lost_features),
            conversion_time_factor=time_factor,
            file_size_factor=size_factor,
            notes=notes,
            recommendations=recommendations
        )
    
    def find_best_target_format(self, 
                               source_format: str,
                               requirements: Dict[str, Any]) -> List[Tuple[str, CompatibilityResult]]:
        """Find best target formats based on requirements"""
        
        source_profile = self.format_profiles.get(source_format)
        if not source_profile:
            return []
        
        candidates = []
        
        # Filter by category
        category_filter = requirements.get("category", source_profile.category)
        
        for format_name, profile in self.format_profiles.items():
            if profile.category != category_filter:
                continue
            
            if format_name == source_format:
                continue
            
            # Check requirements
            if requirements.get("web_compatible") and not profile.web_compatible:
                continue
            
            if requirements.get("mobile_optimized") and not profile.mobile_optimized:
                continue
            
            if requirements.get("patent_free") and not profile.patent_free:
                continue
            
            if requirements.get("hardware_support") and not profile.hardware_support:
                continue
            
            # Analyze compatibility
            compatibility = self.analyze_compatibility(source_format, format_name)
            
            # Apply scoring based on requirements
            score = self._score_compatibility(compatibility, requirements)
            
            candidates.append((format_name, compatibility, score))
        
        # Sort by score (highest first)
        candidates.sort(key=lambda x: x[2], reverse=True)
        
        # Return top candidates
        return [(name, compat) for name, compat, score in candidates[:10]]
    
    def _score_compatibility(self, 
                           compatibility: CompatibilityResult, 
                           requirements: Dict[str, Any]) -> float:
        """Score compatibility result based on requirements"""
        score = 0.0
        
        # Base compatibility score
        compatibility_scores = {
            CompatibilityLevel.PERFECT: 100,
            CompatibilityLevel.EXCELLENT: 90,
            CompatibilityLevel.GOOD: 70,
            CompatibilityLevel.FAIR: 50,
            CompatibilityLevel.POOR: 20,
            CompatibilityLevel.INCOMPATIBLE: 0
        }
        score += compatibility_scores[compatibility.compatibility_level]
        
        # Quality loss penalty
        score -= compatibility.quality_loss_percentage * 0.5
        
        # Conversion time penalty (if speed is important)
        if requirements.get("speed_important", False):
            score -= (compatibility.conversion_time_factor - 1.0) * 10
        
        # File size bonus/penalty
        size_preference = requirements.get("size_preference", "smaller")
        if size_preference == "smaller" and compatibility.file_size_factor < 1.0:
            score += (1.0 - compatibility.file_size_factor) * 20
        elif size_preference == "larger" and compatibility.file_size_factor > 1.0:
            score += (compatibility.file_size_factor - 1.0) * 20
        
        # Feature preservation bonus
        required_features = set(requirements.get("required_features", []))
        supported_features = set(compatibility.supported_features)
        
        if required_features.issubset(supported_features):
            score += 20
        else:
            missing = len(required_features - supported_features)
            score -= missing * 10
        
        return max(0.0, score)
    
    def get_conversion_path(self, 
                          source_format: str, 
                          target_format: str) -> List[Tuple[str, str]]:
        """Find optimal conversion path between formats"""
        
        if source_format == target_format:
            return []
        
        # Direct conversion available
        if (source_format, target_format) in self.conversion_rules:
            return [(source_format, target_format)]
        
        # Find indirect path through intermediate formats
        # For simplicity, try through common intermediate formats
        intermediate_candidates = ["h264_mp4", "aac_mp4", "jpeg", "png"]
        
        for intermediate in intermediate_candidates:
            if intermediate == source_format or intermediate == target_format:
                continue
            
            if ((source_format, intermediate) in self.conversion_rules and 
                (intermediate, target_format) in self.conversion_rules):
                return [(source_format, intermediate), (intermediate, target_format)]
        
        # No path found
        return []
    
    def analyze_batch_compatibility(self, 
                                  format_pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Analyze compatibility for multiple format pairs"""
        
        results = {}
        summary = {
            "total_pairs": len(format_pairs),
            "perfect_compatibility": 0,
            "excellent_compatibility": 0,
            "good_compatibility": 0,
            "fair_compatibility": 0,
            "poor_compatibility": 0,
            "incompatible": 0,
            "average_quality_loss": 0.0,
            "average_conversion_time": 0.0
        }
        
        total_quality_loss = 0.0
        total_conversion_time = 0.0
        
        for source, target in format_pairs:
            compatibility = self.analyze_compatibility(source, target)
            results[f"{source}->{target}"] = compatibility
            
            # Update summary
            if compatibility.compatibility_level == CompatibilityLevel.PERFECT:
                summary["perfect_compatibility"] += 1
            elif compatibility.compatibility_level == CompatibilityLevel.EXCELLENT:
                summary["excellent_compatibility"] += 1
            elif compatibility.compatibility_level == CompatibilityLevel.GOOD:
                summary["good_compatibility"] += 1
            elif compatibility.compatibility_level == CompatibilityLevel.FAIR:
                summary["fair_compatibility"] += 1
            elif compatibility.compatibility_level == CompatibilityLevel.POOR:
                summary["poor_compatibility"] += 1
            else:
                summary["incompatible"] += 1
            
            total_quality_loss += compatibility.quality_loss_percentage
            total_conversion_time += compatibility.conversion_time_factor
        
        if format_pairs:
            summary["average_quality_loss"] = total_quality_loss / len(format_pairs)
            summary["average_conversion_time"] = total_conversion_time / len(format_pairs)
        
        return {
            "results": results,
            "summary": summary
        }
    
    def export_compatibility_matrix(self) -> Dict[str, Any]:
        """Export complete compatibility matrix"""
        matrix = {}
        
        format_names = list(self.format_profiles.keys())
        
        for source in format_names:
            matrix[source] = {}
            for target in format_names:
                if source == target:
                    matrix[source][target] = "perfect"
                else:
                    compatibility = self.analyze_compatibility(source, target)
                    matrix[source][target] = compatibility.compatibility_level.value
        
        return {
            "compatibility_matrix": matrix,
            "format_profiles": {
                name: {
                    "category": profile.category,
                    "codec": profile.codec,
                    "container": profile.container,
                    "features": list(profile.features),
                    "quality_range": profile.quality_range,
                    "compression_efficiency": profile.compression_efficiency,
                    "web_compatible": profile.web_compatible,
                    "mobile_optimized": profile.mobile_optimized,
                    "patent_free": profile.patent_free
                }
                for name, profile in self.format_profiles.items()
            },
            "conversion_rules_count": len(self.conversion_rules)
        }


# Global compatibility matrix instance
format_compatibility = FormatCompatibilityMatrix()


# Export main classes and functions
__all__ = [
    'CompatibilityLevel',
    'ConversionComplexity',
    'CompatibilityResult',
    'FormatProfile',
    'FormatCompatibilityMatrix',
    'format_compatibility'
]