"""
Ainflue Platform - Multimedia Formats - Emerging Formats Support
Support for next-generation and emerging multimedia formats

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.1.0 Enterprise
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class EmergingFormatCategory(Enum):
    """Categories of emerging formats"""
    VIDEO_CODEC = "video_codec"
    AUDIO_CODEC = "audio_codec"
    IMAGE_FORMAT = "image_format"
    CONTAINER_FORMAT = "container_format"
    IMMERSIVE_FORMAT = "immersive_format"
    METADATA_FORMAT = "metadata_format"


class AdoptionStatus(Enum):
    """Adoption status of emerging formats"""
    EXPERIMENTAL = "experimental"
    DRAFT_STANDARD = "draft_standard"
    EARLY_ADOPTION = "early_adoption"
    LIMITED_SUPPORT = "limited_support"
    GROWING_SUPPORT = "growing_support"
    MAINSTREAM = "mainstream"


class TechnicalMaturity(Enum):
    """Technical maturity level"""
    PROOF_OF_CONCEPT = "proof_of_concept"
    ALPHA = "alpha"
    BETA = "beta"
    RELEASE_CANDIDATE = "release_candidate"
    STABLE = "stable"
    MATURE = "mature"


@dataclass
class SupportStatus:
    """Support status for platforms and tools"""
    browsers: Dict[str, str] = field(default_factory=dict)  # browser -> version
    os_support: Dict[str, str] = field(default_factory=dict)  # os -> version
    hardware_support: List[str] = field(default_factory=list)
    software_tools: List[str] = field(default_factory=list)
    streaming_platforms: List[str] = field(default_factory=list)


@dataclass
class PerformanceMetrics:
    """Performance metrics for emerging formats"""
    compression_ratio: Optional[float] = None
    encoding_speed_factor: Optional[float] = None  # relative to baseline
    decoding_speed_factor: Optional[float] = None
    quality_score: Optional[float] = None  # 0-100
    bandwidth_efficiency: Optional[float] = None
    memory_usage_factor: Optional[float] = None


@dataclass
class EmergingFormat:
    """Emerging multimedia format information"""
    format_id: str = ""
    name: str = ""
    description: str = ""
    category: EmergingFormatCategory = EmergingFormatCategory.VIDEO_CODEC
    adoption_status: AdoptionStatus = AdoptionStatus.EXPERIMENTAL
    technical_maturity: TechnicalMaturity = TechnicalMaturity.ALPHA
    
    # Technical specifications
    mime_types: List[str] = field(default_factory=list)
    file_extensions: List[str] = field(default_factory=list)
    specifications: Dict[str, Any] = field(default_factory=dict)
    
    # Support and compatibility
    support_status: SupportStatus = field(default_factory=SupportStatus)
    backwards_compatible: bool = False
    fallback_formats: List[str] = field(default_factory=list)
    
    # Performance and features
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    key_features: List[str] = field(default_factory=list)
    improvements_over: List[str] = field(default_factory=list)
    
    # Standardization and governance
    standards_body: str = ""
    specification_url: str = ""
    reference_implementation: str = ""
    license_type: str = ""
    patent_status: str = ""
    
    # Timeline and roadmap
    first_draft_date: Optional[str] = None
    standardization_date: Optional[str] = None
    expected_adoption_date: Optional[str] = None
    deprecation_risk: str = "low"  # low, medium, high
    
    # Usage recommendations
    recommended_use_cases: List[str] = field(default_factory=list)
    not_recommended_for: List[str] = field(default_factory=list)
    migration_path: Dict[str, str] = field(default_factory=dict)


class EmergingFormatsManager:
    """Professional emerging formats management and tracking system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize emerging formats manager"""
        self.config = config or {}
        self.formats: Dict[str, EmergingFormat] = {}
        self.format_aliases: Dict[str, str] = {}
        self.tracking_enabled = self.config.get('tracking_enabled', True)
        
        # Initialize with current emerging formats
        self._initialize_video_formats()
        self._initialize_audio_formats()
        self._initialize_image_formats()
        self._initialize_immersive_formats()
        self._initialize_container_formats()
    
    def _initialize_video_formats(self) -> None:
        """Initialize emerging video formats"""
        try:
            # VVC (Versatile Video Coding)
            vvc = EmergingFormat(
                format_id="vvc",
                name="VVC/H.266",
                description="Versatile Video Coding - next generation after HEVC",
                category=EmergingFormatCategory.VIDEO_CODEC,
                adoption_status=AdoptionStatus.EARLY_ADOPTION,
                technical_maturity=TechnicalMaturity.STABLE,
                mime_types=["video/vvc", "video/h266"],
                file_extensions=[".vvc", ".266"],
                specifications={
                    "max_resolution": "16K",
                    "bit_depth": "8-16",
                    "chroma_subsampling": ["4:2:0", "4:2:2", "4:4:4"],
                    "color_spaces": ["bt709", "bt2020", "bt2100"]
                },
                support_status=SupportStatus(
                    software_tools=["FFmpeg (experimental)", "x266", "VTM"],
                    hardware_support=["Upcoming 2025+ chips"]
                ),
                performance_metrics=PerformanceMetrics(
                    compression_ratio=1.3,  # 30% better than HEVC
                    encoding_speed_factor=0.3,  # Much slower encoding
                    quality_score=95,
                    bandwidth_efficiency=1.3
                ),
                key_features=[
                    "50% bitrate reduction vs HEVC",
                    "Enhanced HDR support",
                    "Improved parallel processing",
                    "Better error resilience"
                ],
                improvements_over=["h265", "av1"],
                standards_body="ITU-T/ISO",
                specification_url="https://www.itu.int/rec/T-REC-H.266",
                license_type="patent_encumbered",
                patent_status="encumbered",
                first_draft_date="2020-07",
                standardization_date="2020-07",
                expected_adoption_date="2025-2027",
                recommended_use_cases=[
                    "next_gen_streaming",
                    "8k_content", 
                    "bandwidth_constrained",
                    "premium_quality"
                ],
                not_recommended_for=[
                    "real_time_encoding",
                    "legacy_devices",
                    "immediate_deployment"
                ]
            )
            self.register_format(vvc)
            
            # LCEVC (Low Complexity Enhancement Video Coding)
            lcevc = EmergingFormat(
                format_id="lcevc",
                name="LCEVC",
                description="Low Complexity Enhancement Video Coding",
                category=EmergingFormatCategory.VIDEO_CODEC,
                adoption_status=AdoptionStatus.LIMITED_SUPPORT,
                technical_maturity=TechnicalMaturity.STABLE,
                mime_types=["video/lcevc"],
                file_extensions=[".lcevc"],
                specifications={
                    "enhancement_layer": True,
                    "base_codecs": ["h264", "h265", "av1"],
                    "complexity_reduction": "90%"
                },
                support_status=SupportStatus(
                    software_tools=["MPEG-5 encoders", "V-Nova Perseus"],
                    streaming_platforms=["Limited OTT support"]
                ),
                performance_metrics=PerformanceMetrics(
                    compression_ratio=1.2,
                    encoding_speed_factor=2.0,  # Much faster
                    quality_score=85,
                    bandwidth_efficiency=1.2
                ),
                key_features=[
                    "Enhancement layer approach",
                    "Low complexity encoding",
                    "Works with existing codecs",
                    "Reduced computational requirements"
                ],
                standards_body="MPEG",
                license_type="patent_encumbered",
                standardization_date="2020",
                expected_adoption_date="2024-2026",
                recommended_use_cases=[
                    "mobile_streaming",
                    "low_power_devices",
                    "live_streaming",
                    "hybrid_enhancement"
                ]
            )
            self.register_format(lcevc)
            
        except Exception as e:
            logger.error(f"Error initializing video formats: {e}")
    
    def _initialize_audio_formats(self) -> None:
        """Initialize emerging audio formats"""
        try:
            # xHE-AAC (Extended High Efficiency AAC)
            xhe_aac = EmergingFormat(
                format_id="xhe_aac",
                name="xHE-AAC",
                description="Extended High Efficiency AAC with MPEG-D DRC",
                category=EmergingFormatCategory.AUDIO_CODEC,
                adoption_status=AdoptionStatus.GROWING_SUPPORT,
                technical_maturity=TechnicalMaturity.STABLE,
                mime_types=["audio/usac"],
                file_extensions=[".usac"],
                specifications={
                    "bitrate_range": "12-256 kbps",
                    "sample_rates": ["16000", "24000", "32000", "48000"],
                    "channels": "1-7.1",
                    "dynamic_range_control": True
                },
                support_status=SupportStatus(
                    software_tools=["Fraunhofer FDK-AAC", "FFmpeg"],
                    streaming_platforms=["DAB+", "DRM+"]
                ),
                performance_metrics=PerformanceMetrics(
                    compression_ratio=1.3,
                    quality_score=90,
                    bandwidth_efficiency=1.3
                ),
                key_features=[
                    "Ultra-low bitrate support",
                    "Enhanced spectral band replication",
                    "Dynamic range control",
                    "Backwards compatible with AAC"
                ],
                standards_body="MPEG",
                license_type="patent_encumbered",
                expected_adoption_date="2024-2025",
                recommended_use_cases=[
                    "mobile_streaming",
                    "podcast_distribution",
                    "voice_content",
                    "bandwidth_constrained"
                ]
            )
            self.register_format(xhe_aac)
            
            # LC3 (Low Complexity Communication Codec)
            lc3 = EmergingFormat(
                format_id="lc3",
                name="LC3",
                description="Low Complexity Communication Codec for Bluetooth",
                category=EmergingFormatCategory.AUDIO_CODEC,
                adoption_status=AdoptionStatus.GROWING_SUPPORT,
                technical_maturity=TechnicalMaturity.STABLE,
                mime_types=["audio/lc3"],
                file_extensions=[".lc3"],
                specifications={
                    "bitrate_range": "160-345 kbps",
                    "frame_duration": ["7.5ms", "10ms"],
                    "sample_rates": ["8000", "16000", "24000", "32000", "48000"],
                    "channels": "1-2"
                },
                support_status=SupportStatus(
                    hardware_support=["Bluetooth LE Audio devices"],
                    software_tools=["Google liblc3", "Open source implementations"]
                ),
                performance_metrics=PerformanceMetrics(
                    compression_ratio=1.5,
                    encoding_speed_factor=3.0,
                    quality_score=85,
                    bandwidth_efficiency=1.5
                ),
                key_features=[
                    "Low latency encoding",
                    "Better quality than SBC",
                    "Power efficient",
                    "Designed for Bluetooth LE Audio"
                ],
                standards_body="Bluetooth SIG",
                license_type="open",
                patent_status="clear",
                standardization_date="2022",
                expected_adoption_date="2024-2025",
                recommended_use_cases=[
                    "bluetooth_audio",
                    "hearing_aids",
                    "wireless_earbuds",
                    "low_latency_communication"
                ]
            )
            self.register_format(lc3)
            
        except Exception as e:
            logger.error(f"Error initializing audio formats: {e}")
    
    def _initialize_image_formats(self) -> None:
        """Initialize emerging image formats"""
        try:
            # JPEG XL
            jpeg_xl = EmergingFormat(
                format_id="jpeg_xl",
                name="JPEG XL",
                description="Next-generation image format with excellent compression",
                category=EmergingFormatCategory.IMAGE_FORMAT,
                adoption_status=AdoptionStatus.LIMITED_SUPPORT,
                technical_maturity=TechnicalMaturity.STABLE,
                mime_types=["image/jxl"],
                file_extensions=[".jxl"],
                specifications={
                    "max_resolution": "1073741824x1073741824",
                    "bit_depth": "1-32",
                    "color_spaces": ["sRGB", "P3", "Rec2020", "etc."],
                    "animation_support": True,
                    "progressive_decoding": True
                },
                support_status=SupportStatus(
                    browsers={"Safari": "17+"},
                    software_tools=["ImageMagick", "GIMP", "XnView"]
                ),
                performance_metrics=PerformanceMetrics(
                    compression_ratio=1.6,  # 60% smaller than JPEG
                    encoding_speed_factor=0.8,
                    decoding_speed_factor=1.2,
                    quality_score=95
                ),
                key_features=[
                    "60% smaller than JPEG",
                    "Lossless JPEG transcoding",
                    "Progressive decoding",
                    "Animation support",
                    "Wide color gamut"
                ],
                backwards_compatible=True,
                fallback_formats=["webp", "jpeg"],
                standards_body="ISO/IEC",
                specification_url="https://jpeg.org/jpegxl/",
                license_type="open",
                patent_status="clear",
                standardization_date="2021",
                expected_adoption_date="2025-2026",
                recommended_use_cases=[
                    "web_images",
                    "photo_archival",
                    "high_quality_photos",
                    "animation_replacement_gif"
                ],
                not_recommended_for=[
                    "immediate_web_deployment",
                    "legacy_systems"
                ]
            )
            self.register_format(jpeg_xl)
            
            # AVIF (AV1 Image File Format)
            avif = EmergingFormat(
                format_id="avif",
                name="AVIF",
                description="AV1 Image File Format based on AV1 video codec",
                category=EmergingFormatCategory.IMAGE_FORMAT,
                adoption_status=AdoptionStatus.GROWING_SUPPORT,
                technical_maturity=TechnicalMaturity.STABLE,
                mime_types=["image/avif"],
                file_extensions=[".avif"],
                specifications={
                    "max_resolution": "65536x65536",
                    "bit_depth": "8-12",
                    "chroma_subsampling": ["4:4:4", "4:2:2", "4:2:0"],
                    "animation_support": True,
                    "alpha_support": True
                },
                support_status=SupportStatus(
                    browsers={
                        "Chrome": "85+",
                        "Firefox": "93+",
                        "Safari": "16+"
                    },
                    software_tools=["ImageMagick", "libavif", "Squoosh"]
                ),
                performance_metrics=PerformanceMetrics(
                    compression_ratio=1.5,  # 50% smaller than JPEG
                    encoding_speed_factor=0.4,  # Slow encoding
                    quality_score=90
                ),
                key_features=[
                    "50% smaller than JPEG",
                    "Based on AV1 codec",
                    "HDR support",
                    "Animation support",
                    "Growing browser support"
                ],
                fallback_formats=["webp", "jpeg"],
                standards_body="AOMedia",
                license_type="open",
                patent_status="clear",
                standardization_date="2019",
                expected_adoption_date="2024-2025",
                recommended_use_cases=[
                    "modern_web",
                    "mobile_apps",
                    "high_quality_images",
                    "bandwidth_optimization"
                ]
            )
            self.register_format(avif)
            
        except Exception as e:
            logger.error(f"Error initializing image formats: {e}")
    
    def _initialize_immersive_formats(self) -> None:
        """Initialize immersive and VR/AR formats"""
        try:
            # Immersive Video Format
            immersive_video = EmergingFormat(
                format_id="immersive_video",
                name="Immersive Video",
                description="360-degree and VR video format standard",
                category=EmergingFormatCategory.IMMERSIVE_FORMAT,
                adoption_status=AdoptionStatus.EARLY_ADOPTION,
                technical_maturity=TechnicalMaturity.BETA,
                specifications={
                    "projection_types": ["equirectangular", "cubemap", "fisheye"],
                    "stereoscopic": True,
                    "spatial_audio": True,
                    "interactive_elements": True
                },
                support_status=SupportStatus(
                    software_tools=["Unity", "Unreal Engine", "A-Frame"],
                    streaming_platforms=["YouTube VR", "Facebook 360"]
                ),
                key_features=[
                    "360-degree video",
                    "Spatial audio",
                    "Multiple projection types",
                    "Interactive hotspots"
                ],
                standards_body="MPEG",
                expected_adoption_date="2025-2027",
                recommended_use_cases=[
                    "vr_content",
                    "immersive_experiences",
                    "virtual_tours",
                    "training_simulations"
                ]
            )
            self.register_format(immersive_video)
            
        except Exception as e:
            logger.error(f"Error initializing immersive formats: {e}")
    
    def _initialize_container_formats(self) -> None:
        """Initialize emerging container formats"""
        try:
            # CMAF (Common Media Application Format)
            cmaf = EmergingFormat(
                format_id="cmaf",
                name="CMAF",
                description="Common Media Application Format for streaming",
                category=EmergingFormatCategory.CONTAINER_FORMAT,
                adoption_status=AdoptionStatus.GROWING_SUPPORT,
                technical_maturity=TechnicalMaturity.STABLE,
                mime_types=["video/mp4"],
                file_extensions=[".cmaf", ".mp4"],
                specifications={
                    "streaming_protocols": ["DASH", "HLS"],
                    "low_latency": True,
                    "chunked_transfer": True
                },
                support_status=SupportStatus(
                    streaming_platforms=["AWS", "Azure", "Cloudflare"],
                    software_tools=["FFmpeg", "Shaka Packager"]
                ),
                key_features=[
                    "Unified streaming format",
                    "Low latency streaming",
                    "Simplified workflow",
                    "Cross-platform compatibility"
                ],
                standards_body="MPEG",
                license_type="open",
                standardization_date="2018",
                expected_adoption_date="2024-2025",
                recommended_use_cases=[
                    "live_streaming",
                    "ott_platforms",
                    "low_latency_streaming",
                    "multi_device_delivery"
                ]
            )
            self.register_format(cmaf)
            
        except Exception as e:
            logger.error(f"Error initializing container formats: {e}")
    
    def register_format(self, format_info: EmergingFormat) -> bool:
        """Register a new emerging format"""
        try:
            self.formats[format_info.format_id] = format_info
            logger.info(f"Registered emerging format: {format_info.name} ({format_info.format_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error registering format: {e}")
            return False
    
    def get_format(self, format_id: str) -> Optional[EmergingFormat]:
        """Get emerging format information"""
        try:
            if format_id in self.formats:
                return self.formats[format_id]
            
            if format_id in self.format_aliases:
                return self.formats[self.format_aliases[format_id]]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting format: {e}")
            return None
    
    def search_formats(
        self,
        category: Optional[EmergingFormatCategory] = None,
        adoption_status: Optional[AdoptionStatus] = None,
        maturity: Optional[TechnicalMaturity] = None,
        features: Optional[List[str]] = None
    ) -> List[EmergingFormat]:
        """Search emerging formats by criteria"""
        try:
            results = []
            
            for format_info in self.formats.values():
                # Filter by category
                if category and format_info.category != category:
                    continue
                
                # Filter by adoption status
                if adoption_status and format_info.adoption_status != adoption_status:
                    continue
                
                # Filter by maturity
                if maturity and format_info.technical_maturity != maturity:
                    continue
                
                # Filter by features
                if features:
                    if not any(feature in format_info.key_features for feature in features):
                        continue
                
                results.append(format_info)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching formats: {e}")
            return []
    
    def get_adoption_timeline(self) -> Dict[str, List[str]]:
        """Get adoption timeline for emerging formats"""
        try:
            timeline = {}
            
            for format_info in self.formats.values():
                if format_info.expected_adoption_date:
                    year = format_info.expected_adoption_date.split('-')[0]
                    if year not in timeline:
                        timeline[year] = []
                    timeline[year].append(format_info.format_id)
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error getting adoption timeline: {e}")
            return {}
    
    def assess_readiness(self, format_id: str, use_case: str) -> Dict[str, Any]:
        """Assess readiness of format for specific use case"""
        try:
            format_info = self.get_format(format_id)
            if not format_info:
                return {"ready": False, "reason": "Format not found"}
            
            assessment = {
                "ready": False,
                "readiness_score": 0,
                "factors": {},
                "recommendations": []
            }
            
            # Technical maturity (0-30 points)
            maturity_scores = {
                TechnicalMaturity.PROOF_OF_CONCEPT: 5,
                TechnicalMaturity.ALPHA: 10,
                TechnicalMaturity.BETA: 15,
                TechnicalMaturity.RELEASE_CANDIDATE: 25,
                TechnicalMaturity.STABLE: 30,
                TechnicalMaturity.MATURE: 30
            }
            maturity_score = maturity_scores.get(format_info.technical_maturity, 0)
            assessment["factors"]["technical_maturity"] = maturity_score
            
            # Adoption status (0-25 points)
            adoption_scores = {
                AdoptionStatus.EXPERIMENTAL: 5,
                AdoptionStatus.DRAFT_STANDARD: 8,
                AdoptionStatus.EARLY_ADOPTION: 12,
                AdoptionStatus.LIMITED_SUPPORT: 15,
                AdoptionStatus.GROWING_SUPPORT: 20,
                AdoptionStatus.MAINSTREAM: 25
            }
            adoption_score = adoption_scores.get(format_info.adoption_status, 0)
            assessment["factors"]["adoption_status"] = adoption_score
            
            # Support availability (0-25 points)
            support_score = 0
            if format_info.support_status.software_tools:
                support_score += 10
            if format_info.support_status.hardware_support:
                support_score += 10
            if format_info.support_status.browsers:
                support_score += 5
            assessment["factors"]["support_availability"] = min(support_score, 25)
            
            # Use case alignment (0-20 points)
            use_case_score = 0
            if use_case in format_info.recommended_use_cases:
                use_case_score = 20
            elif use_case not in format_info.not_recommended_for:
                use_case_score = 10
            assessment["factors"]["use_case_alignment"] = use_case_score
            
            # Calculate total score
            total_score = sum(assessment["factors"].values())
            assessment["readiness_score"] = total_score
            
            # Determine readiness
            if total_score >= 70:
                assessment["ready"] = True
                assessment["recommendations"].append("Format is ready for production use")
            elif total_score >= 50:
                assessment["recommendations"].append("Format is suitable for pilot projects")
            elif total_score >= 30:
                assessment["recommendations"].append("Format is suitable for experimentation")
            else:
                assessment["recommendations"].append("Format not recommended for current use")
            
            # Add specific recommendations
            if format_info.technical_maturity in [TechnicalMaturity.ALPHA, TechnicalMaturity.BETA]:
                assessment["recommendations"].append("Wait for stable release")
            
            if format_info.adoption_status == AdoptionStatus.EXPERIMENTAL:
                assessment["recommendations"].append("Consider waiting for broader adoption")
            
            if format_info.fallback_formats:
                assessment["recommendations"].append(f"Implement fallback to: {', '.join(format_info.fallback_formats)}")
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing readiness: {e}")
            return {"ready": False, "reason": str(e)}
    
    def get_migration_plan(
        self,
        from_format: str,
        to_format: str
    ) -> Dict[str, Any]:
        """Get migration plan between formats"""
        try:
            target_format = self.get_format(to_format)
            if not target_format:
                return {"feasible": False, "reason": "Target format not found"}
            
            migration_plan = {
                "feasible": True,
                "complexity": "medium",
                "phases": [],
                "considerations": [],
                "timeline": "6-12 months",
                "risks": []
            }
            
            # Check if there's a defined migration path
            if from_format in target_format.migration_path:
                migration_plan["phases"] = [
                    "Assessment and planning",
                    "Tool and infrastructure setup",
                    "Pilot conversion",
                    "Gradual rollout",
                    "Full migration"
                ]
            else:
                migration_plan["phases"] = [
                    "Format analysis",
                    "Custom migration tool development",
                    "Testing and validation",
                    "Phased migration",
                    "Legacy format deprecation"
                ]
                migration_plan["complexity"] = "high"
                migration_plan["timeline"] = "12-18 months"
            
            # Add considerations based on format characteristics
            if target_format.technical_maturity in [TechnicalMaturity.ALPHA, TechnicalMaturity.BETA]:
                migration_plan["considerations"].append("Target format still in development")
                migration_plan["risks"].append("Format specification may change")
            
            if target_format.adoption_status == AdoptionStatus.EXPERIMENTAL:
                migration_plan["considerations"].append("Limited ecosystem support")
                migration_plan["risks"].append("Potential for format abandonment")
            
            if not target_format.backwards_compatible:
                migration_plan["considerations"].append("Full content re-encoding required")
                migration_plan["complexity"] = "high"
            
            return migration_plan
            
        except Exception as e:
            logger.error(f"Error getting migration plan: {e}")
            return {"feasible": False, "reason": str(e)}


# Export main classes
__all__ = [
    'EmergingFormatsManager',
    'EmergingFormat',
    'SupportStatus',
    'PerformanceMetrics',
    'EmergingFormatCategory',
    'AdoptionStatus',
    'TechnicalMaturity'
]