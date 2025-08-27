"""
Data Models - Professional Audio Format Conversion Models

Comprehensive data models and structures for audio format conversion system.
Provides type-safe interfaces and validation for all conversion operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

# Validation imports
from pydantic import BaseModel, validator, Field
import json


class AudioFormat(Enum):
    """Enumeration of supported audio formats"""
    WAV = "wav"
    FLAC = "flac"
    MP3 = "mp3"
    AAC = "aac"
    M4A = "m4a"
    OGG = "ogg"
    AIFF = "aiff"
    WMA = "wma"
    APE = "ape"
    OPUS = "opus"


class QualityLevel(Enum):
    """Quality level enumeration"""
    LOW = "low"
    STANDARD = "standard"
    HIGH = "high"
    PROFESSIONAL = "professional"
    ARCHIVAL = "archival"
    CUSTOM = "custom"


class ConversionPriority(Enum):
    """Conversion priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ProcessingStatus(Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AudioBuffer:
    """Audio buffer data structure"""
    data: np.ndarray
    sample_rate: int
    channels: int
    duration: float
    format: str
    bit_depth: Optional[int] = None
    
    def __post_init__(self):
        """Validate audio buffer after initialization"""
        if self.data is None or len(self.data) == 0:
            raise ValueError("Audio data cannot be empty")
        
        if self.sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        
        if self.channels <= 0:
            raise ValueError("Channel count must be positive")
        
        # Calculate duration if not provided
        if self.duration <= 0:
            if len(self.data.shape) == 1:
                self.duration = len(self.data) / self.sample_rate
            else:
                self.duration = self.data.shape[0] / self.sample_rate
    
    def get_size_bytes(self) -> int:
        """Get buffer size in bytes"""
        return self.data.nbytes
    
    def get_rms_level(self) -> float:
        """Get RMS level in dB"""
        rms = np.sqrt(np.mean(self.data ** 2))
        if rms > 0:
            return 20 * np.log10(rms)
        return -float('inf')
    
    def get_peak_level(self) -> float:
        """Get peak level in dB"""
        peak = np.max(np.abs(self.data))
        if peak > 0:
            return 20 * np.log10(peak)
        return -float('inf')


@dataclass
class FormatSpecification:
    """Audio format specification"""
    format: AudioFormat
    sample_rate: int
    bit_depth: int
    channels: int
    bitrate: Optional[int] = None
    encoding: Optional[str] = None
    subtype: Optional[str] = None
    
    # Format-specific parameters
    compression_level: Optional[int] = None
    variable_bitrate: bool = False
    joint_stereo: bool = False
    
    # Metadata support
    supports_metadata: bool = True
    supports_cover_art: bool = False
    
    def __post_init__(self):
        """Validate format specification"""
        if self.sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        
        if self.bit_depth <= 0:
            raise ValueError("Bit depth must be positive")
        
        if self.channels <= 0:
            raise ValueError("Channel count must be positive")
        
        # Validate format-specific constraints
        self._validate_format_constraints()
    
    def _validate_format_constraints(self):
        """Validate format-specific constraints"""
        if self.format == AudioFormat.MP3:
            if self.sample_rate > 48000:
                raise ValueError("MP3 sample rate cannot exceed 48kHz")
            if self.channels > 2:
                raise ValueError("MP3 supports maximum 2 channels")
        
        elif self.format == AudioFormat.FLAC:
            if self.sample_rate > 655350:
                raise ValueError("FLAC sample rate cannot exceed 655.35kHz")
            if self.bit_depth > 32:
                raise ValueError("FLAC bit depth cannot exceed 32 bits")
        
        # Add more format-specific validations as needed
    
    def is_lossless(self) -> bool:
        """Check if format is lossless"""
        lossless_formats = {AudioFormat.WAV, AudioFormat.FLAC, AudioFormat.AIFF}
        return self.format in lossless_formats
    
    def estimate_file_size(self, duration_seconds: float) -> int:
        """Estimate file size in bytes"""
        if self.bitrate:
            # Use bitrate if available (for lossy formats)
            return int((self.bitrate * 1000 * duration_seconds) / 8)
        else:
            # Calculate from PCM specs (for lossless formats)
            bytes_per_sample = self.bit_depth // 8
            samples_per_second = self.sample_rate * self.channels
            total_bytes = bytes_per_sample * samples_per_second * duration_seconds
            
            # Apply compression factor for lossless formats
            if self.format == AudioFormat.FLAC:
                return int(total_bytes * 0.6)  # Typical FLAC compression
            
            return int(total_bytes)


@dataclass
class QualityProfile:
    """Quality profile configuration"""
    name: str
    description: str
    quality_level: QualityLevel
    
    # Target specifications
    target_sample_rate: Optional[int] = None
    target_bit_depth: Optional[int] = None
    target_bitrate: Optional[int] = None
    
    # Quality constraints
    min_snr: Optional[float] = None  # dB
    max_thd: Optional[float] = None  # %
    max_file_size: Optional[int] = None  # bytes
    
    # Processing preferences
    prefer_lossless: bool = False
    allow_upsampling: bool = False
    normalize_audio: bool = False
    apply_dithering: bool = False
    
    # Platform-specific settings
    platform_optimizations: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate quality profile"""
        if not self.name:
            raise ValueError("Quality profile name cannot be empty")
        
        if self.min_snr and self.min_snr < 0:
            raise ValueError("Minimum SNR must be non-negative")
        
        if self.max_thd and (self.max_thd < 0 or self.max_thd > 100):
            raise ValueError("Maximum THD must be between 0 and 100 percent")


@dataclass
class ProcessingOptions:
    """Audio processing options and parameters"""
    
    # Normalization options
    normalize: bool = False
    normalization_type: str = "peak"  # peak, rms, lufs
    target_level: float = -3.0  # dB
    
    # Filtering options
    apply_highpass: bool = False
    highpass_frequency: float = 20.0  # Hz
    apply_lowpass: bool = False  
    lowpass_frequency: float = 20000.0  # Hz
    
    # Dynamic processing
    apply_limiter: bool = False
    limiter_threshold: float = -0.1  # dB
    apply_compressor: bool = False
    compressor_ratio: float = 2.0
    
    # Effects
    apply_reverb: bool = False
    reverb_room_size: float = 0.3
    apply_delay: bool = False
    delay_time: float = 0.25  # seconds
    
    # Format-specific processing
    dithering_enabled: bool = False
    dithering_type: str = "triangular"
    bit_depth_reduction: bool = False
    target_bit_depth: int = 16
    
    # Advanced options
    preserve_metadata: bool = True
    apply_content_protection: bool = False
    generate_fingerprint: bool = False
    
    # Processing pipeline
    custom_processor_chain: List[str] = field(default_factory=list)
    parallel_processing: bool = False
    max_processing_threads: int = 4
    
    def validate(self) -> List[str]:
        """Validate processing options and return any errors"""
        errors = []
        
        if self.target_level > 0:
            errors.append("Target level should be negative (in dB)")
        
        if self.highpass_frequency < 0 or self.highpass_frequency > 22050:
            errors.append("High-pass frequency out of valid range")
        
        if self.lowpass_frequency < 0 or self.lowpass_frequency > 96000:
            errors.append("Low-pass frequency out of valid range")
        
        if self.compressor_ratio < 1.0:
            errors.append("Compressor ratio must be >= 1.0")
        
        if self.target_bit_depth not in [8, 16, 24, 32]:
            errors.append("Target bit depth must be 8, 16, 24, or 32")
        
        return errors


class ConversionRequest(BaseModel):
    """
    Conversion request model with validation
    
    Comprehensive request structure for audio format conversion
    with full parameter validation and type safety.
    """
    
    # Input/Output specification
    input_path: Path
    output_path: Optional[Path] = None
    output_format: AudioFormat
    
    # Quality settings
    quality_profile: Optional[QualityProfile] = None
    format_specification: Optional[FormatSpecification] = None
    
    # Processing options
    processing_options: Optional[ProcessingOptions] = None
    
    # Conversion parameters
    priority: ConversionPriority = ConversionPriority.NORMAL
    timeout_seconds: int = 300
    retry_count: int = 0
    
    # Metadata handling
    preserve_metadata: bool = True
    enhance_metadata: bool = False
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Output options
    overwrite_existing: bool = False
    create_backup: bool = False
    streaming_optimized: bool = False
    
    # Validation options
    validate_input: bool = True
    validate_output: bool = True
    
    # Advanced options
    content_protection_level: str = "standard"
    generate_quality_report: bool = False
    callback_url: Optional[str] = None
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        arbitrary_types_allowed = True
        
    @validator('input_path')
    def validate_input_path(cls, v):
        """Validate input path exists"""
        if not v.exists():
            raise ValueError(f"Input file does not exist: {v}")
        return v
    
    @validator('output_path')
    def validate_output_path(cls, v, values):
        """Validate output path"""
        if v is None:
            # Generate output path from input
            input_path = values.get('input_path')
            output_format = values.get('output_format')
            if input_path and output_format:
                return input_path.with_suffix(f'.{output_format.value}')
        
        if v and v.exists() and not values.get('overwrite_existing', False):
            raise ValueError(f"Output file exists and overwrite not enabled: {v}")
        
        return v
    
    @validator('timeout_seconds')
    def validate_timeout(cls, v):
        """Validate timeout value"""
        if v <= 0:
            raise ValueError("Timeout must be positive")
        if v > 3600:  # 1 hour max
            raise ValueError("Timeout cannot exceed 1 hour")
        return v
    
    def get_estimated_processing_time(self) -> timedelta:
        """Estimate processing time based on request parameters"""
        # Basic estimation - in production, use machine learning models
        base_time = 30  # seconds
        
        # Factor in quality settings
        if self.quality_profile and self.quality_profile.quality_level == QualityLevel.ARCHIVAL:
            base_time *= 2
        
        # Factor in processing options
        if self.processing_options:
            if self.processing_options.apply_reverb or self.processing_options.apply_delay:
                base_time *= 1.5
        
        return timedelta(seconds=base_time)


@dataclass
class ConversionResult:
    """Conversion operation result with comprehensive information"""
    
    # Basic result information
    conversion_id: str
    success: bool
    
    # File information
    input_path: Optional[Path] = None
    output_path: Optional[Path] = None
    
    # Format information
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    format_specification: Optional[FormatSpecification] = None
    
    # Quality information
    quality_profile: Optional[QualityProfile] = None
    quality_metrics: Optional[Dict[str, float]] = None
    quality_score: float = 0.0
    
    # Processing information
    processing_time: Optional[timedelta] = None
    processing_info: Dict[str, Any] = field(default_factory=dict)
    conversion_info: Dict[str, Any] = field(default_factory=dict)
    
    # File statistics
    input_file_size: Optional[int] = None
    output_file_size: Optional[int] = None
    size_reduction_percent: float = 0.0
    compression_ratio: Optional[float] = None
    
    # Audio characteristics
    original_specs: Dict[str, Any] = field(default_factory=dict)
    converted_specs: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata information
    metadata_preserved: Optional[Dict[str, Any]] = None
    metadata_enhanced: bool = False
    
    # Quality assessment
    dynamic_range_preserved: float = 0.0
    frequency_response_accuracy: float = 0.0
    
    # Error information
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    # Validation results
    input_validation: Dict[str, Any] = field(default_factory=dict)
    output_validation: Dict[str, Any] = field(default_factory=dict)
    
    # Processing timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post-initialization processing"""
        if self.completed_at and self.started_at and not self.processing_time:
            self.processing_time = self.completed_at - self.started_at
        
        if self.input_file_size and self.output_file_size:
            if self.input_file_size > 0:
                self.size_reduction_percent = (
                    (self.input_file_size - self.output_file_size) / self.input_file_size * 100
                )
                self.compression_ratio = self.input_file_size / self.output_file_size
    
    def is_successful(self) -> bool:
        """Check if conversion was successful"""
        return self.success and self.error_message is None
    
    def has_warnings(self) -> bool:
        """Check if result has warnings"""
        return len(self.warnings) > 0
    
    def get_quality_grade(self) -> str:
        """Get quality grade based on metrics"""
        if self.quality_score >= 0.9:
            return "Excellent"
        elif self.quality_score >= 0.8:
            return "Very Good"
        elif self.quality_score >= 0.7:
            return "Good"
        elif self.quality_score >= 0.6:
            return "Fair"
        else:
            return "Poor"
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get processing summary"""
        return {
            'conversion_id': self.conversion_id,
            'success': self.success,
            'processing_time_seconds': self.processing_time.total_seconds() if self.processing_time else 0,
            'quality_score': self.quality_score,
            'quality_grade': self.get_quality_grade(),
            'size_reduction_percent': self.size_reduction_percent,
            'warnings_count': len(self.warnings),
            'has_errors': self.error_message is not None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization"""
        result_dict = {
            'conversion_id': self.conversion_id,
            'success': self.success,
            'input_path': str(self.input_path) if self.input_path else None,
            'output_path': str(self.output_path) if self.output_path else None,
            'input_format': self.input_format,
            'output_format': self.output_format,
            'quality_score': self.quality_score,
            'processing_time_seconds': self.processing_time.total_seconds() if self.processing_time else 0,
            'size_reduction_percent': self.size_reduction_percent,
            'compression_ratio': self.compression_ratio,
            'quality_metrics': self.quality_metrics,
            'processing_info': self.processing_info,
            'conversion_info': self.conversion_info,
            'warnings': self.warnings,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
        
        return result_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversionResult':
        """Create result from dictionary"""
        # Parse timestamps
        started_at = None
        if data.get('started_at'):
            started_at = datetime.fromisoformat(data['started_at'])
        
        completed_at = None
        if data.get('completed_at'):
            completed_at = datetime.fromisoformat(data['completed_at'])
        
        # Parse paths
        input_path = Path(data['input_path']) if data.get('input_path') else None
        output_path = Path(data['output_path']) if data.get('output_path') else None
        
        # Create processing time
        processing_time = None
        if data.get('processing_time_seconds'):
            processing_time = timedelta(seconds=data['processing_time_seconds'])
        
        return cls(
            conversion_id=data['conversion_id'],
            success=data['success'],
            input_path=input_path,
            output_path=output_path,
            input_format=data.get('input_format'),
            output_format=data.get('output_format'),
            quality_score=data.get('quality_score', 0.0),
            processing_time=processing_time,
            size_reduction_percent=data.get('size_reduction_percent', 0.0),
            compression_ratio=data.get('compression_ratio'),
            quality_metrics=data.get('quality_metrics', {}),
            processing_info=data.get('processing_info', {}),
            conversion_info=data.get('conversion_info', {}),
            warnings=data.get('warnings', []),
            error_message=data.get('error_message'),
            error_code=data.get('error_code'),
            started_at=started_at,
            completed_at=completed_at
        )


@dataclass
class BatchConversionRequest:
    """Batch conversion request for multiple files"""
    
    requests: List[ConversionRequest]
    batch_id: str = field(default_factory=lambda: f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # Batch processing options
    parallel_processing: bool = True
    max_concurrent: int = 4
    fail_fast: bool = False
    
    # Progress tracking
    progress_callback: Optional[Callable] = None
    
    # Output options
    organize_outputs: bool = False
    output_directory: Optional[Path] = None
    
    def __post_init__(self):
        """Validate batch request"""
        if not self.requests:
            raise ValueError("Batch request cannot be empty")
        
        if self.max_concurrent <= 0:
            raise ValueError("Max concurrent must be positive")
    
    def get_total_estimated_time(self) -> timedelta:
        """Get total estimated processing time"""
        if self.parallel_processing:
            # Estimate based on longest single conversion
            max_time = max(req.get_estimated_processing_time() for req in self.requests)
            # Add overhead for parallel processing
            return max_time * 1.2
        else:
            # Sum all individual times
            return sum([req.get_estimated_processing_time() for req in self.requests], timedelta())


@dataclass  
class BatchConversionResult:
    """Batch conversion result"""
    
    batch_id: str
    total_requests: int
    successful_conversions: int
    failed_conversions: int
    
    # Individual results
    results: List[ConversionResult] = field(default_factory=list)
    
    # Batch statistics
    total_processing_time: Optional[timedelta] = None
    average_quality_score: float = 0.0
    total_size_reduction: float = 0.0
    
    # Error summary
    error_summary: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate batch statistics"""
        if self.results:
            # Calculate averages
            quality_scores = [r.quality_score for r in self.results if r.success]
            if quality_scores:
                self.average_quality_score = sum(quality_scores) / len(quality_scores)
            
            # Calculate total size reduction
            total_input_size = sum(r.input_file_size or 0 for r in self.results)
            total_output_size = sum(r.output_file_size or 0 for r in self.results)
            
            if total_input_size > 0:
                self.total_size_reduction = (
                    (total_input_size - total_output_size) / total_input_size * 100
                )
            
            # Collect error summary
            for result in self.results:
                if not result.success and result.error_code:
                    self.error_summary[result.error_code] = (
                        self.error_summary.get(result.error_code, 0) + 1
                    )
    
    def get_success_rate(self) -> float:
        """Get conversion success rate"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_conversions / self.total_requests
    
    def get_summary(self) -> Dict[str, Any]:
        """Get batch processing summary"""
        return {
            'batch_id': self.batch_id,
            'total_requests': self.total_requests,
            'success_rate': self.get_success_rate(),
            'successful_conversions': self.successful_conversions,
            'failed_conversions': self.failed_conversions,
            'average_quality_score': self.average_quality_score,
            'total_size_reduction_percent': self.total_size_reduction,
            'total_processing_time_seconds': (
                self.total_processing_time.total_seconds() 
                if self.total_processing_time else 0
            ),
            'error_summary': self.error_summary
        }


# Export all models
__all__ = [
    # Enums
    'AudioFormat',
    'QualityLevel', 
    'ConversionPriority',
    'ProcessingStatus',
    
    # Data structures
    'AudioBuffer',
    'FormatSpecification',
    'QualityProfile',
    'ProcessingOptions',
    
    # Request/Response models
    'ConversionRequest',
    'ConversionResult',
    'BatchConversionRequest',
    'BatchConversionResult'
]
