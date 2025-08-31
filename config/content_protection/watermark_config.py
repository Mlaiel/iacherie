"""Watermark Configuration Module
=============================

Professional watermarking configuration for content protection and ownership verification.
Supports invisible watermarks, robust embedding, and extraction algorithms.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  COPYRIGHT WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import os
from datetime import datetime


class WatermarkType(str, Enum):
    """Types of watermarks."""    INVISIBLE = "invisible"
    SEMI_VISIBLE = "semi_visible"
    VISIBLE = "visible"
    ROBUST = "robust"
    FRAGILE = "fragile"


class WatermarkAlgorithm(str, Enum):
    """Watermarking algorithms by content type."""    # Audio watermarking
    ECHO_HIDING = "echo_hiding"
    PHASE_CODING = "phase_coding"
    SPREAD_SPECTRUM = "spread_spectrum"
    LSB_AUDIO = "lsb_audio"
    DCT_AUDIO = "dct_audio"
    
    # Video watermarking
    DCT_VIDEO = "dct_video"
    DWT_VIDEO = "dwt_video"
    SVD_VIDEO = "svd_video"
    MOTION_VECTOR = "motion_vector"
    FRAME_BASED = "frame_based"
    
    # Image watermarking
    LSB_IMAGE = "lsb_image"
    DCT_IMAGE = "dct_image"
    DWT_IMAGE = "dwt_image"
    SVD_IMAGE = "svd_image"
    BLIND_WATERMARK = "blind_watermark"
    
    # Text watermarking
    SYNONYM_SUBSTITUTION = "synonym_substitution"
    SENTENCE_STRUCTURE = "sentence_structure"
    WHITE_SPACE = "white_space"
    UNICODE_STEGANOGRAPHY = "unicode_steganography"
    SEMANTIC_WATERMARK = "semantic_watermark"


class EmbeddingStrength(str, Enum):
    """Watermark embedding strength levels."""    MINIMAL = "minimal"      # Barely detectable
    LOW = "low"             # Light embedding
    MEDIUM = "medium"       # Balanced
    HIGH = "high"           # Strong embedding
    MAXIMUM = "maximum"     # Maximum robustness


@dataclass
class WatermarkPayload:
    """Watermark payload configuration."""    owner_id: str
    content_id: str
    timestamp: datetime
    copyright_info: str
    license_type: str
    custom_data: Dict[str, Any] = field(default_factory=dict)
    expiry_date: Optional[datetime] = None
    usage_restrictions: List[str] = field(default_factory=list)


@dataclass
class AudioWatermarkConfig:
    """Audio watermarking configuration."""    algorithm: WatermarkAlgorithm = WatermarkAlgorithm.SPREAD_SPECTRUM
    watermark_type: WatermarkType = WatermarkType.INVISIBLE
    embedding_strength: EmbeddingStrength = EmbeddingStrength.MEDIUM
    sample_rate: int = 44100
    bit_depth: int = 16
    frame_size: int = 1024
    overlap_ratio: float = 0.5
    frequency_range: Tuple[int, int] = (1000, 8000)  # Hz
    psychoacoustic_masking: bool = True
    snr_threshold_db: float = 40.0
    imperceptibility_threshold: float = 0.95
    robustness_level: str = "high"
    enable_synchronization: bool = True
    redundancy_factor: int = 3


@dataclass
class VideoWatermarkConfig:
    """Video watermarking configuration."""    algorithm: WatermarkAlgorithm = WatermarkAlgorithm.DCT_VIDEO
    watermark_type: WatermarkType = WatermarkType.INVISIBLE
    embedding_strength: EmbeddingStrength = EmbeddingStrength.MEDIUM
    frame_selection: str = "keyframes"  # all, keyframes, random, adaptive
    spatial_domain: bool = False
    frequency_domain: bool = True
    block_size: Tuple[int, int] = (8, 8)
    embedding_regions: List[str] = field(default_factory=lambda: ["luminance", "chrominance"])
    motion_compensation: bool = True
    temporal_synchronization: bool = True
    psnr_threshold_db: float = 35.0
    ssim_threshold: float = 0.95
    capacity_bits_per_frame: int = 64
    error_correction_enabled: bool = True


@dataclass
class ImageWatermarkConfig:
    """Image watermarking configuration."""    algorithm: WatermarkAlgorithm = WatermarkAlgorithm.DWT_IMAGE
    watermark_type: WatermarkType = WatermarkType.INVISIBLE
    embedding_strength: EmbeddingStrength = EmbeddingStrength.MEDIUM
    color_space: str = "YUV"  # RGB, YUV, HSV, LAB
    transform_domain: str = "DWT"  # DCT, DWT, SVD
    wavelet_type: str = "haar"  # haar, daubechies, biorthogonal
    decomposition_levels: int = 3
    embedding_coefficients: List[str] = field(default_factory=lambda: ["LL", "LH", "HL"])
    adaptive_embedding: bool = True
    texture_analysis: bool = True
    edge_detection: bool = True
    psnr_threshold_db: float = 40.0
    ssim_threshold: float = 0.98
    ncc_threshold: float = 0.9


@dataclass
class TextWatermarkConfig:
    """Text watermarking configuration."""    algorithm: WatermarkAlgorithm = WatermarkAlgorithm.SYNONYM_SUBSTITUTION
    watermark_type: WatermarkType = WatermarkType.INVISIBLE
    embedding_strength: EmbeddingStrength = EmbeddingStrength.LOW
    language: str = "en"
    preserve_semantics: bool = True
    preserve_syntax: bool = True
    preserve_readability: bool = True
    min_text_length: int = 100
    synonym_database: str = "wordnet"
    sentence_selection_ratio: float = 0.3
    word_selection_ratio: float = 0.1
    context_preservation: bool = True
    grammatical_correctness: bool = True
    style_consistency: bool = True


@dataclass
class RobustnessConfig:
    """Watermark robustness configuration."""    enable_attack_resistance: bool = True
    compression_resistance: bool = True
    noise_resistance: bool = True
    geometric_resistance: bool = True
    temporal_resistance: bool = True
    collusion_resistance: bool = True
    supported_attacks: List[str] = field(default_factory=lambda: [
        "jpeg_compression", "mp3_compression", "gaussian_noise",
        "salt_pepper_noise", "rotation", "scaling", "cropping",
        "filtering", "resampling", "echo", "pitch_shifting"
    ])
    attack_simulation_enabled: bool = True
    robustness_testing_enabled: bool = True
    minimum_robustness_score: float = 0.8


@dataclass
class SecurityConfig:
    """Watermark security configuration."""    encryption_algorithm: str = "AES-256-GCM"
    key_derivation_function: str = "PBKDF2"
    key_length_bits: int = 256
    salt_length_bytes: int = 32
    iterations: int = 100000
    enable_key_rotation: bool = True
    key_rotation_interval_days: int = 90
    secure_key_storage: bool = True
    tamper_detection: bool = True
    digital_signature_enabled: bool = True
    signature_algorithm: str = "RSA-PSS"
    certificate_validation: bool = True


@dataclass
class ExtractionConfig:
    """Watermark extraction configuration."""    enable_blind_detection: bool = True
    enable_informed_detection: bool = True
    detection_threshold: float = 0.8
    correlation_threshold: float = 0.7
    bit_error_rate_threshold: float = 0.1
    false_positive_rate_threshold: float = 0.01
    synchronization_enabled: bool = True
    template_matching: bool = True
    statistical_analysis: bool = True
    machine_learning_detection: bool = True
    confidence_scoring: bool = True


@dataclass
class QualityAssessmentConfig:
    """Quality assessment configuration."""    enable_quality_metrics: bool = True
    perceptual_quality_enabled: bool = True
    objective_quality_enabled: bool = True
    subjective_quality_enabled: bool = False
    quality_metrics: List[str] = field(default_factory=lambda: [
        "PSNR", "SSIM", "MSE", "LPIPS", "VMAF"
    ])
    min_quality_score: float = 0.9
    quality_degradation_threshold: float = 0.05
    automatic_parameter_tuning: bool = True
    quality_monitoring: bool = True


class WatermarkConfig:
    """    Professional watermark configuration manager.
    Provides industrial-grade configuration for content watermarking and protection.
    """    
    def __init__(self):
        # General watermarking settings
        self.enable_watermarking: bool = True
        self.default_watermark_type: WatermarkType = WatermarkType.INVISIBLE
        self.default_embedding_strength: EmbeddingStrength = EmbeddingStrength.MEDIUM
        self.multi_layer_watermarking: bool = True
        self.adaptive_watermarking: bool = True
        
        # Content type configurations
        self.audio = AudioWatermarkConfig()
        self.video = VideoWatermarkConfig()
        self.image = ImageWatermarkConfig()
        self.text = TextWatermarkConfig()
        
        # System configurations
        self.robustness = RobustnessConfig()
        self.security = SecurityConfig()
        self.extraction = ExtractionConfig()
        self.quality_assessment = QualityAssessmentConfig()
        
        # Payload management
        self.default_payload: Optional[WatermarkPayload] = None
        self.payload_templates: Dict[str, WatermarkPayload] = {}
        
        # Performance settings
        self.max_concurrent_operations: int = 20
        self.processing_timeout_seconds: int = 300
        self.memory_limit_gb: int = 4
        self.enable_gpu_acceleration: bool = True
        self.batch_processing_enabled: bool = True
        self.batch_size: int = 10
        
        # Load environment configurations
        self._load_from_environment()
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""        # General settings
        self.enable_watermarking = os.getenv("WATERMARK_ENABLED", "true").lower() == "true"
        
        watermark_type = os.getenv("WATERMARK_DEFAULT_TYPE", "invisible")
        self.default_watermark_type = WatermarkType(watermark_type)
        
        embedding_strength = os.getenv("WATERMARK_DEFAULT_STRENGTH", "medium")
        self.default_embedding_strength = EmbeddingStrength(embedding_strength)
        
        # Performance settings
        self.max_concurrent_operations = int(os.getenv("WATERMARK_MAX_CONCURRENT", "20"))
        self.processing_timeout_seconds = int(os.getenv("WATERMARK_TIMEOUT", "300"))
        self.memory_limit_gb = int(os.getenv("WATERMARK_MEMORY_LIMIT", "4"))
        self.enable_gpu_acceleration = os.getenv("WATERMARK_GPU_ENABLED", "true").lower() == "true"
        
        # Audio settings
        self.audio.snr_threshold_db = float(os.getenv("WATERMARK_AUDIO_SNR_THRESHOLD", "40.0"))
        self.audio.imperceptibility_threshold = float(os.getenv("WATERMARK_AUDIO_IMPERCEPTIBILITY", "0.95"))
        
        # Video settings
        self.video.psnr_threshold_db = float(os.getenv("WATERMARK_VIDEO_PSNR_THRESHOLD", "35.0"))
        self.video.ssim_threshold = float(os.getenv("WATERMARK_VIDEO_SSIM_THRESHOLD", "0.95"))
        
        # Image settings
        self.image.psnr_threshold_db = float(os.getenv("WATERMARK_IMAGE_PSNR_THRESHOLD", "40.0"))
        self.image.ssim_threshold = float(os.getenv("WATERMARK_IMAGE_SSIM_THRESHOLD", "0.98"))
        
        # Security settings
        self.security.key_length_bits = int(os.getenv("WATERMARK_KEY_LENGTH", "256"))
        self.security.key_rotation_interval_days = int(os.getenv("WATERMARK_KEY_ROTATION_DAYS", "90"))
        
        # Quality settings
        self.quality_assessment.min_quality_score = float(os.getenv("WATERMARK_MIN_QUALITY", "0.9"))
    
    def create_payload(self, owner_id: str, content_id: str, **kwargs) -> WatermarkPayload:
        """Create a watermark payload with specified parameters."""        return WatermarkPayload(
            owner_id=owner_id,
            content_id=content_id,
            timestamp=datetime.now(),
            copyright_info=kwargs.get("copyright_info", f"© {datetime.now().year} {owner_id}"),
            license_type=kwargs.get("license_type", "All Rights Reserved"),
            custom_data=kwargs.get("custom_data", {}),
            expiry_date=kwargs.get("expiry_date"),
            usage_restrictions=kwargs.get("usage_restrictions", [])
        )
    
    def get_content_config(self, content_type: str) -> Dict[str, Any]:
        """Get watermarking configuration for specific content type."""        content_configs = {
            "audio": self.audio,
            "video": self.video,
            "image": self.image,
            "text": self.text
        }
        
        config = content_configs.get(content_type.lower())
        if not config:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        return {
            "content_type": content_type,
            "content_config": config.__dict__,
            "robustness": self.robustness.__dict__,
            "security": self.security.__dict__,
            "extraction": self.extraction.__dict__,
            "quality_assessment": self.quality_assessment.__dict__
        }
    
    def get_algorithm_config(self, algorithm: WatermarkAlgorithm) -> Dict[str, Any]:
        """Get configuration for specific watermarking algorithm."""        algorithm_configs = {
            # Audio algorithms
            WatermarkAlgorithm.ECHO_HIDING: {
                "echo_delay_ms": 50,
                "echo_amplitude": 0.1,
                "mixing_ratio": 0.05
            },
            WatermarkAlgorithm.PHASE_CODING: {
                "phase_difference": 0.5,
                "segment_length": 2048,
                "overlap": 1024
            },
            WatermarkAlgorithm.SPREAD_SPECTRUM: {
                "spreading_factor": 100,
                "chip_rate": 1000,
                "pseudorandom_sequence": True
            },
            
            # Video algorithms
            WatermarkAlgorithm.DCT_VIDEO: {
                "block_size": self.video.block_size,
                "quantization_factor": 10,
                "embedding_strength": 0.1
            },
            WatermarkAlgorithm.DWT_VIDEO: {
                "wavelet": "haar",
                "levels": 3,
                "coefficients": ["LL", "LH"]
            },
            
            # Image algorithms
            WatermarkAlgorithm.DCT_IMAGE: {
                "block_size": (8, 8),
                "quantization_table": "standard",
                "embedding_strength": 0.1
            },
            WatermarkAlgorithm.DWT_IMAGE: {
                "wavelet": self.image.wavelet_type,
                "levels": self.image.decomposition_levels,
                "coefficients": self.image.embedding_coefficients
            },
            
            # Text algorithms
            WatermarkAlgorithm.SYNONYM_SUBSTITUTION: {
                "synonym_database": self.text.synonym_database,
                "selection_ratio": self.text.word_selection_ratio,
                "context_window": 5
            },
            WatermarkAlgorithm.SENTENCE_STRUCTURE: {
                "transformation_types": ["passive_active", "clause_order"],
                "preservation_score": 0.9
            }
        }
        
        return algorithm_configs.get(algorithm, {})
    
    def optimize_for_imperceptibility(self) -> None:
        """Optimize configuration for maximum imperceptibility."""        self.default_embedding_strength = EmbeddingStrength.MINIMAL
        
        # Audio optimization
        self.audio.embedding_strength = EmbeddingStrength.MINIMAL
        self.audio.snr_threshold_db = 45.0
        self.audio.imperceptibility_threshold = 0.98
        self.audio.psychoacoustic_masking = True
        
        # Video optimization
        self.video.embedding_strength = EmbeddingStrength.MINIMAL
        self.video.psnr_threshold_db = 40.0
        self.video.ssim_threshold = 0.98
        
        # Image optimization
        self.image.embedding_strength = EmbeddingStrength.MINIMAL
        self.image.psnr_threshold_db = 45.0
        self.image.ssim_threshold = 0.99
        self.image.adaptive_embedding = True
        
        # Text optimization
        self.text.embedding_strength = EmbeddingStrength.MINIMAL
        self.text.preserve_semantics = True
        self.text.preserve_readability = True
        self.text.word_selection_ratio = 0.05
    
    def optimize_for_robustness(self) -> None:
        """Optimize configuration for maximum robustness."""        self.default_embedding_strength = EmbeddingStrength.HIGH
        
        # Audio optimization
        self.audio.embedding_strength = EmbeddingStrength.HIGH
        self.audio.redundancy_factor = 5
        self.audio.robustness_level = "maximum"
        
        # Video optimization
        self.video.embedding_strength = EmbeddingStrength.HIGH
        self.video.error_correction_enabled = True
        self.video.temporal_synchronization = True
        
        # Image optimization
        self.image.embedding_strength = EmbeddingStrength.HIGH
        self.image.decomposition_levels = 4
        
        # Text optimization
        self.text.embedding_strength = EmbeddingStrength.MEDIUM
        self.text.sentence_selection_ratio = 0.5
        
        # Robustness settings
        self.robustness.enable_attack_resistance = True
        self.robustness.compression_resistance = True
        self.robustness.geometric_resistance = True
        self.robustness.minimum_robustness_score = 0.9
    
    def set_security_level(self, level: str) -> None:
        """Set security configuration level."""        if level == "basic":
            self.security.key_length_bits = 128
            self.security.iterations = 50000
            self.security.enable_key_rotation = False
        elif level == "standard":
            self.security.key_length_bits = 256
            self.security.iterations = 100000
            self.security.enable_key_rotation = True
            self.security.key_rotation_interval_days = 90
        elif level == "high":
            self.security.key_length_bits = 256
            self.security.iterations = 200000
            self.security.enable_key_rotation = True
            self.security.key_rotation_interval_days = 30
            self.security.tamper_detection = True
            self.security.digital_signature_enabled = True
        else:
            raise ValueError(f"Unsupported security level: {level}")
    
    def validate_configuration(self) -> List[str]:
        """Validate current configuration and return any issues."""        issues = []
        
        # Validate performance settings
        if self.max_concurrent_operations <= 0:
            issues.append("Max concurrent operations must be positive")
        
        if self.processing_timeout_seconds <= 0:
            issues.append("Processing timeout must be positive")
        
        if self.memory_limit_gb <= 0:
            issues.append("Memory limit must be positive")
        
        # Validate quality thresholds
        if not 0.0 <= self.quality_assessment.min_quality_score <= 1.0:
            issues.append("Min quality score must be between 0.0 and 1.0")
        
        # Validate audio settings
        if self.audio.snr_threshold_db <= 0:
            issues.append("Audio SNR threshold must be positive")
        
        if not 0.0 <= self.audio.imperceptibility_threshold <= 1.0:
            issues.append("Audio imperceptibility threshold must be between 0.0 and 1.0")
        
        # Validate video settings
        if self.video.psnr_threshold_db <= 0:
            issues.append("Video PSNR threshold must be positive")
        
        if not 0.0 <= self.video.ssim_threshold <= 1.0:
            issues.append("Video SSIM threshold must be between 0.0 and 1.0")
        
        # Validate image settings
        if self.image.psnr_threshold_db <= 0:
            issues.append("Image PSNR threshold must be positive")
        
        if not 0.0 <= self.image.ssim_threshold <= 1.0:
            issues.append("Image SSIM threshold must be between 0.0 and 1.0")
        
        # Validate security settings
        if self.security.key_length_bits not in [128, 256, 512]:
            issues.append("Key length must be 128, 256, or 512 bits")
        
        if self.security.iterations < 10000:
            issues.append("Key derivation iterations should be at least 10,000")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""        return {
            "enable_watermarking": self.enable_watermarking,
            "default_watermark_type": self.default_watermark_type,
            "default_embedding_strength": self.default_embedding_strength,
            "multi_layer_watermarking": self.multi_layer_watermarking,
            "adaptive_watermarking": self.adaptive_watermarking,
            "max_concurrent_operations": self.max_concurrent_operations,
            "processing_timeout_seconds": self.processing_timeout_seconds,
            "memory_limit_gb": self.memory_limit_gb,
            "enable_gpu_acceleration": self.enable_gpu_acceleration,
            "batch_processing_enabled": self.batch_processing_enabled,
            "batch_size": self.batch_size,
            "audio": self.audio.__dict__,
            "video": self.video.__dict__,
            "image": self.image.__dict__,
            "text": self.text.__dict__,
            "robustness": self.robustness.__dict__,
            "security": self.security.__dict__,
            "extraction": self.extraction.__dict__,
            "quality_assessment": self.quality_assessment.__dict__
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'WatermarkConfig':
        """Create configuration from dictionary."""        config = cls()
        
        # Load basic settings
        if "enable_watermarking" in config_dict:
            config.enable_watermarking = config_dict["enable_watermarking"]
        if "default_watermark_type" in config_dict:
            config.default_watermark_type = WatermarkType(config_dict["default_watermark_type"])
        if "default_embedding_strength" in config_dict:
            config.default_embedding_strength = EmbeddingStrength(config_dict["default_embedding_strength"])
        
        # Load scalar settings
        scalar_fields = [
            "multi_layer_watermarking", "adaptive_watermarking",
            "max_concurrent_operations", "processing_timeout_seconds",
            "memory_limit_gb", "enable_gpu_acceleration",
            "batch_processing_enabled", "batch_size"
        ]
        
        for field in scalar_fields:
            if field in config_dict:
                setattr(config, field, config_dict[field])
        
        # Load component configurations
        component_map = {
            "audio": config.audio,
            "video": config.video,
            "image": config.image,
            "text": config.text,
            "robustness": config.robustness,
            "security": config.security,
            "extraction": config.extraction,
            "quality_assessment": config.quality_assessment
        }
        
        for key, component in component_map.items():
            if key in config_dict:
                for attr_key, attr_value in config_dict[key].items():
                    setattr(component, attr_key, attr_value)
        
        return config
