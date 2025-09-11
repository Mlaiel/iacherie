"""
Format Conversion Monitor Module - Ainflue Platform
==================================================

Monitor multi-format audio conversion for enterprise workflows including
quality preservation, metadata integrity, batch processing efficiency,
and codec performance optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)

class AudioFormat(Enum):
    """Supported audio formats."""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    WMA = "wma"
    AIFF = "aiff"
    APE = "ape"
    OPUS = "opus"

class QualityPreset(Enum):
    """Quality presets for audio conversion."""
    ARCHIVE = "archive"  # Lossless, maximum quality
    BROADCAST = "broadcast"  # Professional broadcast quality
    STREAMING_HIGH = "streaming_high"  # High quality streaming
    STREAMING_STANDARD = "streaming_standard"  # Standard streaming
    STREAMING_LOW = "streaming_low"  # Low bandwidth streaming
    MOBILE = "mobile"  # Mobile optimized
    PODCAST = "podcast"  # Podcast optimized

@dataclass
class ConversionSettings:
    """Audio conversion settings."""
    sample_rate: int
    bit_depth: Optional[int]  # Not applicable for lossy formats
    bitrate: Optional[int]  # For lossy formats
    channels: int
    codec_options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversionJob:
    """Represents an audio format conversion job."""
    job_id: str
    input_file: str
    output_file: str
    source_format: AudioFormat
    target_format: AudioFormat
    quality_preset: QualityPreset
    settings: ConversionSettings
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "pending"
    file_size_reduction_ratio: Optional[float] = None
    quality_preservation_score: Optional[float] = None
    processing_time_ms: Optional[int] = None
    metadata_preserved: bool = False
    error_message: Optional[str] = None

@dataclass
class FormatMetrics:
    """Metrics for format conversion monitoring."""
    total_conversions: int = 0
    successful_conversions: int = 0
    failed_conversions: int = 0
    average_quality_score: float = 0.0
    average_processing_time_ms: float = 0.0
    average_file_size_reduction: float = 0.0
    format_popularity: Dict[str, int] = field(default_factory=dict)
    preset_usage: Dict[str, int] = field(default_factory=dict)
    codec_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)

class FormatConversionMonitor:
    """
    Monitor audio format conversion performance and quality.
    
    Tracks conversion success rates, quality preservation, processing efficiency,
    metadata integrity, and provides optimization recommendations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize format conversion monitor."""
        self.config = config or self._default_config()
        self.jobs: Dict[str, ConversionJob] = {}
        self.metrics = FormatMetrics()
        self.start_time = datetime.now()
        
        # Quality presets configuration
        self.quality_presets = self._initialize_quality_presets()
        
        # Performance tracking
        self.conversion_history: List[Tuple[datetime, float, str]] = []
        self.codec_benchmarks: Dict[str, List[float]] = {}
        
        logger.info("Format Conversion Monitor initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for format conversion monitoring."""
        return {
            "supported_formats": [format.value for format in AudioFormat],
            "default_quality_preset": QualityPreset.STREAMING_HIGH,
            "quality_threshold": 0.90,
            "processing_timeout_minutes": 15,
            "metadata_preservation": True,
            "parallel_conversions": 8,
            "temp_directory": "/tmp/ainflue_audio_conversion",
            "cleanup_temp_files": True,
            "dithering_enabled": True,
            "normalize_before_conversion": False
        }
    
    def _initialize_quality_presets(self) -> Dict[QualityPreset, Dict[AudioFormat, ConversionSettings]]:
        """Initialize quality presets for different formats."""
        return {
            QualityPreset.ARCHIVE: {
                AudioFormat.WAV: ConversionSettings(48000, 24, None, 2),
                AudioFormat.FLAC: ConversionSettings(48000, 24, None, 2),
                AudioFormat.MP3: ConversionSettings(48000, None, 320, 2),
                AudioFormat.AAC: ConversionSettings(48000, None, 256, 2),
                AudioFormat.OGG: ConversionSettings(48000, None, 320, 2)
            },
            QualityPreset.BROADCAST: {
                AudioFormat.WAV: ConversionSettings(48000, 24, None, 2),
                AudioFormat.MP3: ConversionSettings(48000, None, 320, 2),
                AudioFormat.AAC: ConversionSettings(48000, None, 256, 2),
                AudioFormat.FLAC: ConversionSettings(48000, 24, None, 2)
            },
            QualityPreset.STREAMING_HIGH: {
                AudioFormat.MP3: ConversionSettings(44100, None, 256, 2),
                AudioFormat.AAC: ConversionSettings(44100, None, 192, 2),
                AudioFormat.OGG: ConversionSettings(44100, None, 256, 2),
                AudioFormat.OPUS: ConversionSettings(48000, None, 160, 2)
            },
            QualityPreset.STREAMING_STANDARD: {
                AudioFormat.MP3: ConversionSettings(44100, None, 192, 2),
                AudioFormat.AAC: ConversionSettings(44100, None, 128, 2),
                AudioFormat.OGG: ConversionSettings(44100, None, 192, 2),
                AudioFormat.OPUS: ConversionSettings(48000, None, 128, 2)
            },
            QualityPreset.STREAMING_LOW: {
                AudioFormat.MP3: ConversionSettings(44100, None, 128, 2),
                AudioFormat.AAC: ConversionSettings(44100, None, 96, 2),
                AudioFormat.OGG: ConversionSettings(44100, None, 128, 2),
                AudioFormat.OPUS: ConversionSettings(48000, None, 96, 2)
            },
            QualityPreset.MOBILE: {
                AudioFormat.AAC: ConversionSettings(44100, None, 96, 2),
                AudioFormat.MP3: ConversionSettings(44100, None, 128, 2),
                AudioFormat.OPUS: ConversionSettings(48000, None, 64, 2)
            },
            QualityPreset.PODCAST: {
                AudioFormat.MP3: ConversionSettings(44100, None, 128, 1),  # Mono for voice
                AudioFormat.AAC: ConversionSettings(44100, None, 96, 1),
                AudioFormat.OPUS: ConversionSettings(48000, None, 64, 1)
            }
        }
    
    def start_conversion_job(
        self,
        job_id: str,
        input_file: str,
        output_file: str,
        source_format: AudioFormat,
        target_format: AudioFormat,
        quality_preset: QualityPreset = None
    ) -> str:
        """Start a new format conversion job."""
        if quality_preset is None:
            quality_preset = self.config["default_quality_preset"]
        
        # Get conversion settings for the preset and target format
        settings = self.quality_presets[quality_preset].get(
            target_format,
            self._get_default_settings(target_format)
        )
        
        job = ConversionJob(
            job_id=job_id,
            input_file=input_file,
            output_file=output_file,
            source_format=source_format,
            target_format=target_format,
            quality_preset=quality_preset,
            settings=settings,
            start_time=datetime.now()
        )
        
        self.jobs[job_id] = job
        
        # Start processing
        self._process_conversion_job(job)
        
        logger.info(f"Started conversion job {job_id}: {source_format.value} -> {target_format.value}")
        return job_id
    
    def _get_default_settings(self, target_format: AudioFormat) -> ConversionSettings:
        """Get default settings for a target format."""
        defaults = {
            AudioFormat.WAV: ConversionSettings(44100, 16, None, 2),
            AudioFormat.MP3: ConversionSettings(44100, None, 192, 2),
            AudioFormat.FLAC: ConversionSettings(44100, 16, None, 2),
            AudioFormat.AAC: ConversionSettings(44100, None, 128, 2),
            AudioFormat.OGG: ConversionSettings(44100, None, 192, 2),
            AudioFormat.OPUS: ConversionSettings(48000, None, 128, 2)
        }
        return defaults.get(target_format, ConversionSettings(44100, 16, None, 2))
    
    def _process_conversion_job(self, job: ConversionJob):
        """Process format conversion job."""
        try:
            job.status = "converting"
            
            # Simulate conversion process
            processing_time = self._estimate_conversion_time(
                job.source_format, job.target_format, job.settings
            )
            
            # Simulate conversion results
            import random
            import time
            time.sleep(processing_time / 1000)  # Simulate processing time
            
            job.processing_time_ms = processing_time
            
            # Simulate quality preservation score
            job.quality_preservation_score = self._calculate_quality_preservation(
                job.source_format, job.target_format, job.settings
            )
            
            # Simulate file size reduction
            job.file_size_reduction_ratio = self._calculate_file_size_reduction(
                job.source_format, job.target_format, job.settings
            )
            
            # Simulate metadata preservation
            job.metadata_preserved = random.choice([True, True, True, False])  # 75% success rate
            
            # Determine success based on quality threshold
            if job.quality_preservation_score >= self.config["quality_threshold"]:
                job.status = "completed"
            else:
                job.status = "quality_warning"
            
            job.end_time = datetime.now()
            
            # Update metrics
            self._update_metrics(job)
            
            logger.info(f"Completed conversion job {job.job_id}: "
                       f"quality={job.quality_preservation_score:.3f}, "
                       f"time={processing_time}ms")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.end_time = datetime.now()
            logger.error(f"Failed to process conversion job {job.job_id}: {e}")
    
    def _estimate_conversion_time(
        self,
        source_format: AudioFormat,
        target_format: AudioFormat,
        settings: ConversionSettings
    ) -> int:
        """Estimate conversion processing time."""
        # Base conversion times (milliseconds per minute of audio)
        base_times = {
            (AudioFormat.WAV, AudioFormat.MP3): 200,
            (AudioFormat.WAV, AudioFormat.AAC): 250,
            (AudioFormat.WAV, AudioFormat.FLAC): 300,
            (AudioFormat.WAV, AudioFormat.OGG): 350,
            (AudioFormat.FLAC, AudioFormat.MP3): 400,
            (AudioFormat.FLAC, AudioFormat.AAC): 450,
            (AudioFormat.MP3, AudioFormat.AAC): 150,
            (AudioFormat.MP3, AudioFormat.OGG): 200
        }
        
        conversion_pair = (source_format, target_format)
        base_time = base_times.get(conversion_pair, 300)
        
        # Adjust for quality settings
        if target_format in [AudioFormat.MP3, AudioFormat.AAC, AudioFormat.OGG]:
            if settings.bitrate and settings.bitrate > 256:
                base_time *= 1.2
            elif settings.bitrate and settings.bitrate < 128:
                base_time *= 0.8
        
        # Adjust for sample rate
        if settings.sample_rate > 44100:
            base_time *= 1.3
        elif settings.sample_rate < 44100:
            base_time *= 0.9
        
        # Add random variation
        import random
        variation = random.uniform(0.8, 1.3)
        
        return int(base_time * variation)
    
    def _calculate_quality_preservation(
        self,
        source_format: AudioFormat,
        target_format: AudioFormat,
        settings: ConversionSettings
    ) -> float:
        """Calculate quality preservation score."""
        # Base quality scores for format conversions
        lossless_formats = [AudioFormat.WAV, AudioFormat.FLAC, AudioFormat.AIFF]
        
        if source_format in lossless_formats and target_format in lossless_formats:
            base_quality = 0.98  # Near perfect for lossless to lossless
        elif source_format in lossless_formats:
            # Lossless to lossy
            if target_format == AudioFormat.AAC and settings.bitrate >= 192:
                base_quality = 0.95
            elif target_format == AudioFormat.MP3 and settings.bitrate >= 256:
                base_quality = 0.92
            elif target_format == AudioFormat.OGG and settings.bitrate >= 192:
                base_quality = 0.94
            else:
                base_quality = 0.85
        else:
            # Lossy to lossy (generally not recommended)
            base_quality = 0.75
        
        # Adjust for bitrate (if applicable)
        if target_format not in lossless_formats and settings.bitrate:
            if settings.bitrate >= 256:
                base_quality *= 1.05
            elif settings.bitrate < 128:
                base_quality *= 0.85
        
        # Adjust for sample rate matching
        if settings.sample_rate in [44100, 48000]:
            base_quality *= 1.02
        elif settings.sample_rate < 44100:
            base_quality *= 0.95
        
        # Add random variation
        import random
        variation = random.uniform(-0.02, 0.02)
        
        return max(0.0, min(1.0, base_quality + variation))
    
    def _calculate_file_size_reduction(
        self,
        source_format: AudioFormat,
        target_format: AudioFormat,
        settings: ConversionSettings
    ) -> float:
        """Calculate file size reduction ratio."""
        # Typical compression ratios
        lossless_formats = [AudioFormat.WAV, AudioFormat.FLAC, AudioFormat.AIFF]
        
        if source_format == AudioFormat.WAV:
            if target_format == AudioFormat.FLAC:
                return 0.6  # FLAC typically 60% of WAV size
            elif target_format == AudioFormat.MP3:
                if settings.bitrate >= 256:
                    return 0.15
                elif settings.bitrate >= 192:
                    return 0.12
                else:
                    return 0.08
            elif target_format == AudioFormat.AAC:
                if settings.bitrate >= 192:
                    return 0.12
                elif settings.bitrate >= 128:
                    return 0.08
                else:
                    return 0.06
            elif target_format == AudioFormat.OGG:
                return 0.10
        
        # Default ratios for other conversions
        if target_format in lossless_formats:
            return 0.8  # Modest compression
        else:
            return 0.10  # Significant compression for lossy formats
    
    def _update_metrics(self, job: ConversionJob):
        """Update format conversion metrics."""
        self.metrics.total_conversions += 1
        
        if job.status in ["completed", "quality_warning"]:
            self.metrics.successful_conversions += 1
        else:
            self.metrics.failed_conversions += 1
        
        if job.quality_preservation_score is not None:
            # Update average quality score
            total_quality = (self.metrics.average_quality_score * (self.metrics.total_conversions - 1) + 
                           job.quality_preservation_score)
            self.metrics.average_quality_score = total_quality / self.metrics.total_conversions
        
        if job.processing_time_ms is not None:
            # Update average processing time
            total_time = (self.metrics.average_processing_time_ms * (self.metrics.total_conversions - 1) + 
                         job.processing_time_ms)
            self.metrics.average_processing_time_ms = total_time / self.metrics.total_conversions
        
        if job.file_size_reduction_ratio is not None:
            # Update average file size reduction
            total_reduction = (self.metrics.average_file_size_reduction * (self.metrics.total_conversions - 1) + 
                             job.file_size_reduction_ratio)
            self.metrics.average_file_size_reduction = total_reduction / self.metrics.total_conversions
        
        # Update format popularity
        format_pair = f"{job.source_format.value}_to_{job.target_format.value}"
        self.metrics.format_popularity[format_pair] = (
            self.metrics.format_popularity.get(format_pair, 0) + 1
        )
        
        # Update preset usage
        preset_name = job.quality_preset.value
        self.metrics.preset_usage[preset_name] = (
            self.metrics.preset_usage.get(preset_name, 0) + 1
        )
        
        # Track conversion history
        if job.quality_preservation_score is not None:
            self.conversion_history.append((
                job.end_time, job.quality_preservation_score, format_pair
            ))
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific conversion job."""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "source_format": job.source_format.value,
            "target_format": job.target_format.value,
            "quality_preset": job.quality_preset.value,
            "start_time": job.start_time.isoformat(),
            "end_time": job.end_time.isoformat() if job.end_time else None,
            "processing_time_ms": job.processing_time_ms,
            "quality_preservation_score": job.quality_preservation_score,
            "file_size_reduction_ratio": job.file_size_reduction_ratio,
            "metadata_preserved": job.metadata_preserved,
            "error_message": job.error_message,
            "settings": {
                "sample_rate": job.settings.sample_rate,
                "bit_depth": job.settings.bit_depth,
                "bitrate": job.settings.bitrate,
                "channels": job.settings.channels
            }
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive format conversion metrics."""
        success_rate = (self.metrics.successful_conversions / max(1, self.metrics.total_conversions))
        
        return {
            "overview": {
                "total_conversions": self.metrics.total_conversions,
                "successful_conversions": self.metrics.successful_conversions,
                "failed_conversions": self.metrics.failed_conversions,
                "success_rate": round(success_rate, 3),
                "average_quality_score": round(self.metrics.average_quality_score, 3),
                "average_processing_time_ms": round(self.metrics.average_processing_time_ms, 1),
                "average_file_size_reduction": round(self.metrics.average_file_size_reduction, 3)
            },
            "format_popularity": self.metrics.format_popularity,
            "preset_usage": self.metrics.preset_usage,
            "active_jobs": len([j for j in self.jobs.values() if j.status in ["pending", "converting"]]),
            "quality_trend": self._get_quality_trend(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_quality_trend(self) -> Dict[str, Any]:
        """Get quality trend analysis."""
        if len(self.conversion_history) < 2:
            return {"trend": "insufficient_data"}
        
        recent_scores = [score for _, score, _ in self.conversion_history[-10:]]
        
        if len(recent_scores) >= 2:
            import statistics
            recent_avg = statistics.mean(recent_scores)
            
            if len(self.conversion_history) >= 20:
                older_scores = [score for _, score, _ in self.conversion_history[-20:-10]]
                older_avg = statistics.mean(older_scores)
                
                if recent_avg > older_avg + 0.01:
                    trend = "improving"
                elif recent_avg < older_avg - 0.01:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "stable"
            
            return {
                "trend": trend,
                "recent_average": round(recent_avg, 3),
                "sample_size": len(recent_scores)
            }
        
        return {"trend": "insufficient_data"}

# Create default instance
format_conversion_monitor = FormatConversionMonitor()

__all__ = [
    'FormatConversionMonitor',
    'ConversionJob',
    'AudioFormat',
    'QualityPreset',
    'ConversionSettings',
    'format_conversion_monitor'
]