"""
Emerging Formats Module for Ainflue Platform
Next-generation multimedia format support and detection

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel - All Rights Reserved
"""

from typing import Dict, List, Optional, Union, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class FormatMaturity(Enum):
    """Format maturity levels"""
    EXPERIMENTAL = "experimental"
    DRAFT = "draft"
    CANDIDATE = "candidate"
    STABLE = "stable"
    DEPRECATED = "deprecated"


class AdoptionLevel(Enum):
    """Industry adoption levels"""
    RESEARCH = "research"
    EARLY_ADOPTER = "early_adopter"
    GROWING = "growing"
    MAINSTREAM = "mainstream"
    UBIQUITOUS = "ubiquitous"


@dataclass
class FormatFeatures:
    """Advanced format features"""
    hdr_support: bool = False
    wide_color_gamut: bool = False
    alpha_channel: bool = False
    layers_support: bool = False
    animation_support: bool = False
    lossless_mode: bool = False
    progressive_encoding: bool = False
    roi_encoding: bool = False  # Region of Interest
    adaptive_quality: bool = False
    metadata_embedding: bool = False


@dataclass
class PerformanceMetrics:
    """Format performance characteristics"""
    compression_ratio: float = 0.0
    encoding_speed: float = 0.0  # relative to reference
    decoding_speed: float = 0.0
    quality_score: float = 0.0  # PSNR/SSIM based
    memory_usage: float = 0.0  # relative to reference
    complexity_score: int = 0  # 1-10 scale


@dataclass
class EmergingFormat:
    """Emerging multimedia format definition"""
    format_id: str
    name: str
    description: str
    format_type: str  # video, audio, image, container
    maturity: FormatMaturity
    adoption: AdoptionLevel
    specification_version: str
    specification_url: str
    standardization_body: str
    first_release: str
    latest_update: str
    
    # Technical specifications
    mime_types: List[str] = field(default_factory=list)
    file_extensions: List[str] = field(default_factory=list)
    magic_bytes: Optional[bytes] = None
    features: Optional[FormatFeatures] = None
    performance: Optional[PerformanceMetrics] = None
    
    # Ecosystem information
    primary_sponsor: str = ""
    major_supporters: List[str] = field(default_factory=list)
    competing_formats: List[str] = field(default_factory=list)
    supersedes_formats: List[str] = field(default_factory=list)
    
    # Implementation status
    encoder_availability: Dict[str, str] = field(default_factory=dict)
    decoder_availability: Dict[str, str] = field(default_factory=dict)
    browser_support: Dict[str, str] = field(default_factory=dict)
    platform_support: Dict[str, str] = field(default_factory=dict)
    
    # Licensing and patents
    license_type: str = ""
    patent_status: str = ""
    royalty_free: bool = True
    
    # Market information
    major_adopters: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    advantages: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)


class EmergingFormatsRegistry:
    """
    Registry and tracker for emerging multimedia formats
    Monitors next-generation formats for Ainflue platform adoption
    """
    
    def __init__(self):
        self.formats: Dict[str, EmergingFormat] = {}
        self.format_timeline: Dict[str, List[str]] = {}
        self._initialize_emerging_formats()
    
    def _initialize_emerging_formats(self):
        """Initialize registry with current emerging formats"""
        
        # JPEG XL - Next-generation image format
        jpeg_xl_features = FormatFeatures(
            hdr_support=True,
            wide_color_gamut=True,
            alpha_channel=True,
            layers_support=False,
            animation_support=True,
            lossless_mode=True,
            progressive_encoding=True,
            roi_encoding=True,
            adaptive_quality=True,
            metadata_embedding=True
        )
        
        jpeg_xl_performance = PerformanceMetrics(
            compression_ratio=0.6,  # 40% better than JPEG
            encoding_speed=0.8,
            decoding_speed=1.2,
            quality_score=0.95,
            memory_usage=1.1,
            complexity_score=7
        )
        
        jpeg_xl = EmergingFormat(
            format_id="jpeg_xl",
            name="JPEG XL",
            description="Next-generation image codec with excellent compression and features",
            format_type="image",
            maturity=FormatMaturity.STABLE,
            adoption=AdoptionLevel.EARLY_ADOPTER,
            specification_version="ISO/IEC 18181",
            specification_url="https://jpeg.org/jpegxl/",
            standardization_body="ISO/IEC JTC 1/SC 29/WG 1",
            first_release="2021-03-30",
            latest_update="2022-01-01",
            mime_types=["image/jxl"],
            file_extensions=[".jxl"],
            magic_bytes=b'\xff\x0a',
            features=jpeg_xl_features,
            performance=jpeg_xl_performance,
            primary_sponsor="Google",
            major_supporters=["Cloudflare", "Facebook", "Adobe"],
            competing_formats=["avif", "webp", "heif"],
            supersedes_formats=["jpeg", "png"],
            encoder_availability={
                "libjxl": "reference implementation",
                "imagemagick": "beta support",
                "gimp": "plugin available"
            },
            decoder_availability={
                "libjxl": "reference implementation",
                "chrome": "experimental flag",
                "firefox": "experimental flag"
            },
            browser_support={
                "chrome": "experimental (flag required)",
                "firefox": "experimental (flag required)",
                "safari": "not supported",
                "edge": "experimental (flag required)"
            },
            platform_support={
                "windows": "library available",
                "macos": "library available",
                "linux": "library available",
                "android": "library available",
                "ios": "library available"
            },
            license_type="BSD-3-Clause",
            patent_status="royalty-free",
            royalty_free=True,
            major_adopters=["Cloudflare", "SmugMug"],
            use_cases=[
                "web images",
                "photo archival",
                "professional photography",
                "responsive images"
            ],
            advantages=[
                "Superior compression efficiency",
                "Lossless and lossy modes",
                "Wide color gamut support",
                "Progressive encoding",
                "Animation support"
            ],
            limitations=[
                "Limited browser support",
                "Encoding complexity",
                "Large decoder size",
                "New format adoption challenges"
            ]
        )
        self.register_format(jpeg_xl)
        
        # VVC (Versatile Video Coding) - H.266
        vvc_features = FormatFeatures(
            hdr_support=True,
            wide_color_gamut=True,
            alpha_channel=False,
            layers_support=True,
            animation_support=False,
            lossless_mode=True,
            progressive_encoding=True,
            roi_encoding=True,
            adaptive_quality=True,
            metadata_embedding=True
        )
        
        vvc_performance = PerformanceMetrics(
            compression_ratio=0.5,  # 50% better than H.265
            encoding_speed=0.3,     # Much slower encoding
            decoding_speed=0.7,
            quality_score=0.98,
            memory_usage=1.5,
            complexity_score=9
        )
        
        vvc = EmergingFormat(
            format_id="vvc",
            name="Versatile Video Coding (H.266)",
            description="Next-generation video codec with exceptional compression",
            format_type="video",
            maturity=FormatMaturity.STABLE,
            adoption=AdoptionLevel.RESEARCH,
            specification_version="ITU-T H.266",
            specification_url="https://www.itu.int/rec/T-REC-H.266",
            standardization_body="ITU-T VCEG",
            first_release="2020-07-06",
            latest_update="2022-06-01",
            mime_types=["video/h266", "video/vvc"],
            file_extensions=[".266", ".vvc"],
            magic_bytes=None,
            features=vvc_features,
            performance=vvc_performance,
            primary_sponsor="Fraunhofer HHI",
            major_supporters=["Ericsson", "Huawei", "Qualcomm", "Samsung"],
            competing_formats=["av1", "h265"],
            supersedes_formats=["h265", "h264"],
            encoder_availability={
                "vvenc": "Fraunhofer reference encoder",
                "x266": "in development",
                "ffmpeg": "experimental support"
            },
            decoder_availability={
                "vvdec": "Fraunhofer reference decoder",
                "ffmpeg": "experimental support"
            },
            browser_support={
                "chrome": "not supported",
                "firefox": "not supported",
                "safari": "not supported",
                "edge": "not supported"
            },
            platform_support={
                "windows": "experimental",
                "macos": "experimental",
                "linux": "experimental",
                "android": "not supported",
                "ios": "not supported"
            },
            license_type="FRAND",
            patent_status="patent-encumbered",
            royalty_free=False,
            major_adopters=[],
            use_cases=[
                "8K video streaming",
                "professional video production",
                "broadcast television",
                "video archival"
            ],
            advantages=[
                "Exceptional compression efficiency",
                "8K and beyond support",
                "Advanced HDR support",
                "Scalable video coding",
                "Screen content coding"
            ],
            limitations=[
                "Very high complexity",
                "Patent licensing required",
                "No hardware support yet",
                "Limited software support"
            ]
        )
        self.register_format(vvc)
        
        # EVC (Essential Video Coding)
        evc_features = FormatFeatures(
            hdr_support=True,
            wide_color_gamut=True,
            alpha_channel=False,
            layers_support=True,
            animation_support=False,
            lossless_mode=False,
            progressive_encoding=True,
            roi_encoding=True,
            adaptive_quality=True,
            metadata_embedding=True
        )
        
        evc_performance = PerformanceMetrics(
            compression_ratio=0.65,  # Better than H.264
            encoding_speed=0.6,
            decoding_speed=0.8,
            quality_score=0.88,
            memory_usage=1.2,
            complexity_score=6
        )
        
        evc = EmergingFormat(
            format_id="evc",
            name="Essential Video Coding",
            description="Royalty-free video codec by Samsung",
            format_type="video",
            maturity=FormatMaturity.STABLE,
            adoption=AdoptionLevel.EARLY_ADOPTER,
            specification_version="ISO/IEC 23094-1",
            specification_url="https://www.iso.org/standard/74427.html",
            standardization_body="ISO/IEC JTC 1/SC 29",
            first_release="2020-08-01",
            latest_update="2021-12-01",
            mime_types=["video/evc"],
            file_extensions=[".evc"],
            magic_bytes=None,
            features=evc_features,
            performance=evc_performance,
            primary_sponsor="Samsung",
            major_supporters=["LG", "Kakao"],
            competing_formats=["av1", "h265", "vvc"],
            supersedes_formats=["h264"],
            encoder_availability={
                "evc_encoder": "Samsung reference encoder",
                "ffmpeg": "experimental support"
            },
            decoder_availability={
                "evc_decoder": "Samsung reference decoder",
                "ffmpeg": "experimental support"
            },
            browser_support={
                "chrome": "not supported",
                "firefox": "not supported",
                "safari": "not supported",
                "edge": "not supported"
            },
            platform_support={
                "windows": "experimental",
                "macos": "experimental",
                "linux": "experimental",
                "android": "Samsung devices",
                "ios": "not supported"
            },
            license_type="Royalty-free",
            patent_status="royalty-free",
            royalty_free=True,
            major_adopters=["Samsung"],
            use_cases=[
                "mobile video streaming",
                "smart TV applications",
                "video conferencing",
                "OTT streaming"
            ],
            advantages=[
                "Royalty-free licensing",
                "Good compression efficiency",
                "Lower complexity than VVC",
                "Mobile-optimized"
            ],
            limitations=[
                "Limited ecosystem support",
                "Not as efficient as VVC or AV1",
                "Samsung-centric development",
                "Limited hardware support"
            ]
        )
        self.register_format(evc)
        
        # HEIF (High Efficiency Image Format)
        heif_features = FormatFeatures(
            hdr_support=True,
            wide_color_gamut=True,
            alpha_channel=True,
            layers_support=True,
            animation_support=True,
            lossless_mode=True,
            progressive_encoding=False,
            roi_encoding=False,
            adaptive_quality=False,
            metadata_embedding=True
        )
        
        heif_performance = PerformanceMetrics(
            compression_ratio=0.5,  # 50% better than JPEG
            encoding_speed=0.7,
            decoding_speed=0.9,
            quality_score=0.90,
            memory_usage=1.0,
            complexity_score=5
        )
        
        heif = EmergingFormat(
            format_id="heif",
            name="High Efficiency Image Format",
            description="Container format based on HEVC for images",
            format_type="image",
            maturity=FormatMaturity.STABLE,
            adoption=AdoptionLevel.GROWING,
            specification_version="ISO/IEC 23008-12",
            specification_url="https://www.iso.org/standard/66067.html",
            standardization_body="ISO/IEC JTC 1/SC 29",
            first_release="2015-06-01",
            latest_update="2017-12-01",
            mime_types=["image/heif", "image/heic"],
            file_extensions=[".heif", ".heic"],
            magic_bytes=b'\x00\x00\x00\x20ftypheic',
            features=heif_features,
            performance=heif_performance,
            primary_sponsor="Apple",
            major_supporters=["Nokia", "Canon"],
            competing_formats=["jpeg_xl", "avif", "webp"],
            supersedes_formats=["jpeg"],
            encoder_availability={
                "libheif": "reference implementation",
                "imagemagick": "full support",
                "ffmpeg": "full support"
            },
            decoder_availability={
                "libheif": "reference implementation",
                "imagemagick": "full support",
                "ffmpeg": "full support"
            },
            browser_support={
                "chrome": "not supported",
                "firefox": "not supported",
                "safari": "full support",
                "edge": "not supported"
            },
            platform_support={
                "windows": "Windows 10+",
                "macos": "macOS 10.13+",
                "linux": "library available",
                "android": "Android 10+",
                "ios": "iOS 11+"
            },
            license_type="FRAND",
            patent_status="patent-encumbered",
            royalty_free=False,
            major_adopters=["Apple", "Google Photos", "WhatsApp"],
            use_cases=[
                "mobile photography",
                "photo storage",
                "image sequences",
                "HDR photography"
            ],
            advantages=[
                "Excellent compression",
                "Image sequences support",
                "Rich metadata support",
                "HDR and wide color gamut",
                "Apple ecosystem integration"
            ],
            limitations=[
                "Patent licensing required",
                "Limited browser support",
                "Encoding complexity",
                "Not web-native"
            ]
        )
        self.register_format(heif)
        
        # LCEVC (Low Complexity Enhancement Video Coding)
        lcevc_features = FormatFeatures(
            hdr_support=True,
            wide_color_gamut=True,
            alpha_channel=False,
            layers_support=True,
            animation_support=False,
            lossless_mode=False,
            progressive_encoding=True,
            roi_encoding=False,
            adaptive_quality=True,
            metadata_embedding=True
        )
        
        lcevc_performance = PerformanceMetrics(
            compression_ratio=0.75,  # Enhancement layer approach
            encoding_speed=1.2,      # Lower complexity
            decoding_speed=1.1,
            quality_score=0.85,
            memory_usage=0.9,
            complexity_score=4
        )
        
        lcevc = EmergingFormat(
            format_id="lcevc",
            name="Low Complexity Enhancement Video Coding",
            description="Enhancement layer video codec for efficient streaming",
            format_type="video",
            maturity=FormatMaturity.STABLE,
            adoption=AdoptionLevel.EARLY_ADOPTER,
            specification_version="ISO/IEC 23094-2",
            specification_url="https://www.iso.org/standard/74429.html",
            standardization_body="ISO/IEC JTC 1/SC 29",
            first_release="2020-08-01",
            latest_update="2021-06-01",
            mime_types=["video/lcevc"],
            file_extensions=[".lcevc"],
            magic_bytes=None,
            features=lcevc_features,
            performance=lcevc_performance,
            primary_sponsor="V-Nova",
            major_supporters=["Sony", "BBC"],
            competing_formats=["h265", "av1", "vvc"],
            supersedes_formats=[],
            encoder_availability={
                "v-nova_encoder": "V-Nova reference encoder"
            },
            decoder_availability={
                "v-nova_decoder": "V-Nova reference decoder"
            },
            browser_support={
                "chrome": "not supported",
                "firefox": "not supported", 
                "safari": "not supported",
                "edge": "not supported"
            },
            platform_support={
                "windows": "SDK available",
                "macos": "SDK available",
                "linux": "SDK available",
                "android": "SDK available",
                "ios": "SDK available"
            },
            license_type="Proprietary",
            patent_status="patent-encumbered",
            royalty_free=False,
            major_adopters=["BBC", "Sony Pictures"],
            use_cases=[
                "live streaming",
                "low-latency applications",
                "mobile streaming",
                "broadcast enhancement"
            ],
            advantages=[
                "Very low complexity",
                "Enhancement layer approach",
                "Backward compatibility",
                "Low latency encoding"
            ],
            limitations=[
                "Proprietary technology",
                "Limited ecosystem",
                "Patent licensing required",
                "Not widely adopted"
            ]
        )
        self.register_format(lcevc)
        
        # Opus Audio Codec (still emerging in some contexts)
        opus_features = FormatFeatures(
            hdr_support=False,
            wide_color_gamut=False,
            alpha_channel=False,
            layers_support=False,
            animation_support=False,
            lossless_mode=False,
            progressive_encoding=False,
            roi_encoding=False,
            adaptive_quality=True,
            metadata_embedding=True
        )
        
        opus_performance = PerformanceMetrics(
            compression_ratio=0.6,  # Better than MP3/AAC
            encoding_speed=1.5,
            decoding_speed=2.0,
            quality_score=0.95,
            memory_usage=0.8,
            complexity_score=3
        )
        
        opus = EmergingFormat(
            format_id="opus",
            name="Opus Audio Codec",
            description="Modern audio codec for internet applications",
            format_type="audio",
            maturity=FormatMaturity.STABLE,
            adoption=AdoptionLevel.GROWING,
            specification_version="RFC 6716",
            specification_url="https://tools.ietf.org/rfc/rfc6716.txt",
            standardization_body="IETF",
            first_release="2012-09-11",
            latest_update="2017-11-15",
            mime_types=["audio/opus"],
            file_extensions=[".opus"],
            magic_bytes=b'OpusHead',
            features=opus_features,
            performance=opus_performance,
            primary_sponsor="Xiph.Org Foundation",
            major_supporters=["Mozilla", "Google", "Skype"],
            competing_formats=["aac", "mp3", "vorbis"],
            supersedes_formats=["vorbis", "speex"],
            encoder_availability={
                "libopus": "reference implementation",
                "ffmpeg": "full support",
                "gstreamer": "full support"
            },
            decoder_availability={
                "libopus": "reference implementation",
                "ffmpeg": "full support",
                "all_major_browsers": "native support"
            },
            browser_support={
                "chrome": "full support",
                "firefox": "full support",
                "safari": "iOS 11+, macOS 10.13+",
                "edge": "full support"
            },
            platform_support={
                "windows": "full support",
                "macos": "full support",
                "linux": "full support",
                "android": "Android 5.0+",
                "ios": "iOS 11+"
            },
            license_type="BSD",
            patent_status="royalty-free",
            royalty_free=True,
            major_adopters=["WhatsApp", "Discord", "Spotify", "YouTube"],
            use_cases=[
                "web audio",
                "voice chat applications",
                "music streaming",
                "real-time communication"
            ],
            advantages=[
                "Excellent quality at low bitrates",
                "Variable bitrate support",
                "Low latency mode",
                "Royalty-free",
                "Wide browser support"
            ],
            limitations=[
                "Limited legacy device support",
                "Not supported in some embedded systems",
                "Newer format adoption challenges"
            ]
        )
        self.register_format(opus)
    
    def register_format(self, format_info: EmergingFormat):
        """Register an emerging format"""
        self.formats[format_info.format_id] = format_info
        
        # Update timeline
        year = format_info.first_release[:4]
        if year not in self.format_timeline:
            self.format_timeline[year] = []
        self.format_timeline[year].append(format_info.format_id)
        
        logger.info(f"Registered emerging format: {format_info.name} ({format_info.format_id})")
    
    def get_format(self, format_id: str) -> Optional[EmergingFormat]:
        """Get emerging format by ID"""
        return self.formats.get(format_id)
    
    def get_formats_by_type(self, format_type: str) -> List[EmergingFormat]:
        """Get formats by type (video, audio, image, container)"""
        return [
            fmt for fmt in self.formats.values()
            if fmt.format_type == format_type
        ]
    
    def get_formats_by_maturity(self, maturity: FormatMaturity) -> List[EmergingFormat]:
        """Get formats by maturity level"""
        return [
            fmt for fmt in self.formats.values()
            if fmt.maturity == maturity
        ]
    
    def get_formats_by_adoption(self, adoption: AdoptionLevel) -> List[EmergingFormat]:
        """Get formats by adoption level"""
        return [
            fmt for fmt in self.formats.values()
            if fmt.adoption == adoption
        ]
    
    def get_royalty_free_formats(self) -> List[EmergingFormat]:
        """Get all royalty-free emerging formats"""
        return [
            fmt for fmt in self.formats.values()
            if fmt.royalty_free
        ]
    
    def get_web_ready_formats(self) -> List[EmergingFormat]:
        """Get formats with some browser support"""
        web_ready = []
        for fmt in self.formats.values():
            has_browser_support = any(
                "support" in status.lower() or "experimental" in status.lower()
                for status in fmt.browser_support.values()
            )
            if has_browser_support:
                web_ready.append(fmt)
        return web_ready
    
    def get_production_ready_formats(self) -> List[EmergingFormat]:
        """Get formats ready for production use"""
        return [
            fmt for fmt in self.formats.values()
            if (fmt.maturity in {FormatMaturity.STABLE, FormatMaturity.CANDIDATE} and
                fmt.adoption in {AdoptionLevel.GROWING, AdoptionLevel.MAINSTREAM})
        ]
    
    def compare_formats(self, format_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Compare multiple emerging formats"""
        comparison = {}
        
        for format_id in format_ids:
            fmt = self.get_format(format_id)
            if not fmt:
                continue
            
            comparison[format_id] = {
                "name": fmt.name,
                "type": fmt.format_type,
                "maturity": fmt.maturity.value,
                "adoption": fmt.adoption.value,
                "royalty_free": fmt.royalty_free,
                "performance": {
                    "compression_ratio": fmt.performance.compression_ratio if fmt.performance else 0,
                    "quality_score": fmt.performance.quality_score if fmt.performance else 0,
                    "encoding_speed": fmt.performance.encoding_speed if fmt.performance else 0
                },
                "browser_support_count": sum(
                    1 for status in fmt.browser_support.values()
                    if "support" in status.lower()
                ),
                "platform_support_count": sum(
                    1 for status in fmt.platform_support.values()
                    if status and "not supported" not in status.lower()
                ),
                "advantages_count": len(fmt.advantages),
                "limitations_count": len(fmt.limitations)
            }
        
        return comparison
    
    def get_format_recommendations(
        self,
        use_case: str,
        priority: str = "quality"  # quality, compatibility, performance, licensing
    ) -> List[EmergingFormat]:
        """Get format recommendations for specific use case"""
        candidates = []
        
        for fmt in self.formats.values():
            if use_case.lower() in [uc.lower() for uc in fmt.use_cases]:
                candidates.append(fmt)
        
        if not candidates:
            return []
        
        # Sort by priority
        if priority == "quality":
            return sorted(
                candidates,
                key=lambda f: f.performance.quality_score if f.performance else 0,
                reverse=True
            )
        elif priority == "compatibility":
            return sorted(
                candidates,
                key=lambda f: sum(
                    1 for status in f.platform_support.values()
                    if status and "not supported" not in status.lower()
                ),
                reverse=True
            )
        elif priority == "performance":
            return sorted(
                candidates,
                key=lambda f: f.performance.encoding_speed if f.performance else 0,
                reverse=True
            )
        elif priority == "licensing":
            royalty_free = [f for f in candidates if f.royalty_free]
            patent_encumbered = [f for f in candidates if not f.royalty_free]
            return royalty_free + patent_encumbered
        
        return candidates
    
    def get_format_timeline(self) -> Dict[str, List[Dict[str, str]]]:
        """Get chronological timeline of format releases"""
        timeline = {}
        
        for year, format_ids in sorted(self.format_timeline.items()):
            timeline[year] = []
            for format_id in format_ids:
                fmt = self.formats[format_id]
                timeline[year].append({
                    "id": format_id,
                    "name": fmt.name,
                    "type": fmt.format_type,
                    "sponsor": fmt.primary_sponsor
                })
        
        return timeline
    
    def get_adoption_trends(self) -> Dict[str, Dict[str, int]]:
        """Get adoption trends across formats"""
        trends = {
            "by_type": {},
            "by_maturity": {},
            "by_adoption": {},
            "by_licensing": {}
        }
        
        for fmt in self.formats.values():
            # By type
            fmt_type = fmt.format_type
            trends["by_type"][fmt_type] = trends["by_type"].get(fmt_type, 0) + 1
            
            # By maturity
            maturity = fmt.maturity.value
            trends["by_maturity"][maturity] = trends["by_maturity"].get(maturity, 0) + 1
            
            # By adoption
            adoption = fmt.adoption.value
            trends["by_adoption"][adoption] = trends["by_adoption"].get(adoption, 0) + 1
            
            # By licensing
            licensing = "royalty_free" if fmt.royalty_free else "patent_encumbered"
            trends["by_licensing"][licensing] = trends["by_licensing"].get(licensing, 0) + 1
        
        return trends
    
    def export_registry(self, file_path: Path) -> bool:
        """Export emerging formats registry to JSON"""
        try:
            registry_data = {
                "formats": {},
                "timeline": self.format_timeline,
                "export_timestamp": datetime.now().isoformat(),
                "total_formats": len(self.formats)
            }
            
            for format_id, fmt in self.formats.items():
                format_data = {
                    "format_id": fmt.format_id,
                    "name": fmt.name,
                    "description": fmt.description,
                    "format_type": fmt.format_type,
                    "maturity": fmt.maturity.value,
                    "adoption": fmt.adoption.value,
                    "specification_version": fmt.specification_version,
                    "specification_url": fmt.specification_url,
                    "standardization_body": fmt.standardization_body,
                    "first_release": fmt.first_release,
                    "latest_update": fmt.latest_update,
                    "mime_types": fmt.mime_types,
                    "file_extensions": fmt.file_extensions,
                    "primary_sponsor": fmt.primary_sponsor,
                    "major_supporters": fmt.major_supporters,
                    "competing_formats": fmt.competing_formats,
                    "supersedes_formats": fmt.supersedes_formats,
                    "encoder_availability": fmt.encoder_availability,
                    "decoder_availability": fmt.decoder_availability,
                    "browser_support": fmt.browser_support,
                    "platform_support": fmt.platform_support,
                    "license_type": fmt.license_type,
                    "patent_status": fmt.patent_status,
                    "royalty_free": fmt.royalty_free,
                    "major_adopters": fmt.major_adopters,
                    "use_cases": fmt.use_cases,
                    "advantages": fmt.advantages,
                    "limitations": fmt.limitations
                }
                
                if fmt.features:
                    format_data["features"] = {
                        "hdr_support": fmt.features.hdr_support,
                        "wide_color_gamut": fmt.features.wide_color_gamut,
                        "alpha_channel": fmt.features.alpha_channel,
                        "layers_support": fmt.features.layers_support,
                        "animation_support": fmt.features.animation_support,
                        "lossless_mode": fmt.features.lossless_mode,
                        "progressive_encoding": fmt.features.progressive_encoding,
                        "roi_encoding": fmt.features.roi_encoding,
                        "adaptive_quality": fmt.features.adaptive_quality,
                        "metadata_embedding": fmt.features.metadata_embedding
                    }
                
                if fmt.performance:
                    format_data["performance"] = {
                        "compression_ratio": fmt.performance.compression_ratio,
                        "encoding_speed": fmt.performance.encoding_speed,
                        "decoding_speed": fmt.performance.decoding_speed,
                        "quality_score": fmt.performance.quality_score,
                        "memory_usage": fmt.performance.memory_usage,
                        "complexity_score": fmt.performance.complexity_score
                    }
                
                registry_data["formats"][format_id] = format_data
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Emerging formats registry exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export emerging formats registry: {e}")
            return False


# Global emerging formats registry instance
emerging_formats_registry = EmergingFormatsRegistry()


async def get_emerging_formats_registry() -> EmergingFormatsRegistry:
    """Get the global emerging formats registry instance"""
    return emerging_formats_registry


if __name__ == "__main__":
    # Test emerging formats registry
    registry = EmergingFormatsRegistry()
    
    print("Emerging Formats Overview:")
    print(f"Total formats: {len(registry.formats)}")
    
    print("\nRoyalty-free formats:")
    royalty_free = registry.get_royalty_free_formats()
    for fmt in royalty_free:
        print(f"- {fmt.name} ({fmt.format_type})")
    
    print("\nProduction-ready formats:")
    production_ready = registry.get_production_ready_formats()
    for fmt in production_ready:
        print(f"- {fmt.name} (Maturity: {fmt.maturity.value}, Adoption: {fmt.adoption.value})")
    
    print("\nWeb-ready formats:")
    web_ready = registry.get_web_ready_formats()
    for fmt in web_ready:
        support_count = sum(
            1 for status in fmt.browser_support.values()
            if "support" in status.lower()
        )
        print(f"- {fmt.name} ({support_count}/4 browsers)")