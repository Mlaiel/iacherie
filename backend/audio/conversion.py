"""🔄 Audio Conversion Module - Professional Format Conversion & Transcoding

Advanced audio format conversion, metadata preservation, quality optimization, and batch processing
for the IA Influencer Agent platform.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import soundfile as sf
import librosa
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import io


class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    FLAC = "flac"
    MP3 = "mp3"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    AIFF = "aiff"
    WMA = "wma"


@dataclass
class ConversionSettings:
    """Audio conversion configuration"""
    target_format: AudioFormat
    sample_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    channels: Optional[int] = None
    bitrate: Optional[int] = None  # For compressed formats
    quality: float = 0.9  # 0.0 to 1.0


@dataclass
class ConversionResult:
    """Audio conversion result"""
    converted_data: bytes
    original_format: AudioFormat
    target_format: AudioFormat
    metadata: Dict[str, Any]
    quality_metrics: Dict[str, float]
    file_size_reduction: float


class AudioConverter:
    """🔄 Professional Audio Format Converter"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.supported_formats = {
            AudioFormat.WAV: {"lossy": False, "max_bitrate": None},
            AudioFormat.FLAC: {"lossy": False, "max_bitrate": None},
            AudioFormat.MP3: {"lossy": True, "max_bitrate": 320},
            AudioFormat.AAC: {"lossy": True, "max_bitrate": 256},
            AudioFormat.OGG: {"lossy": True, "max_bitrate": 500}
        }
    
    def convert(self, audio_data: np.ndarray, 
                source_format: AudioFormat,
                settings: ConversionSettings,
                sample_rate: int = 44100) -> ConversionResult:
        """Convert audio to target format"""
        # Prepare audio data
        processed_audio = self._prepare_audio(audio_data, settings, sample_rate)
        
        # Convert to target format
        converted_data = self._encode_audio(processed_audio, settings, sample_rate)
        
        # Extract metadata
        metadata = self._extract_metadata(audio_data, sample_rate)
        
        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(audio_data, processed_audio)
        
        # Calculate file size reduction
        original_size = len(audio_data.tobytes())
        converted_size = len(converted_data)
        size_reduction = (original_size - converted_size) / original_size * 100
        
        return ConversionResult(
            converted_data=converted_data,
            original_format=source_format,
            target_format=settings.target_format,
            metadata=metadata,
            quality_metrics=quality_metrics,
            file_size_reduction=size_reduction
        )
    
    def _prepare_audio(self, audio_data: np.ndarray, 
                      settings: ConversionSettings, 
                      current_sample_rate: int) -> np.ndarray:
        """Prepare audio for conversion"""
        processed = audio_data.copy()
        
        # Resample if needed
        if settings.sample_rate and settings.sample_rate != current_sample_rate:
            processed = librosa.resample(
                processed, 
                orig_sr=current_sample_rate, 
                target_sr=settings.sample_rate
            )
        
        # Convert to mono/stereo if needed
        if settings.channels:
            if settings.channels == 1 and processed.ndim > 1:
                # Convert to mono
                processed = np.mean(processed, axis=0)
            elif settings.channels == 2 and processed.ndim == 1:
                # Convert to stereo
                processed = np.array([processed, processed])
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(processed))
        if max_val > 1.0:
            processed = processed / max_val
        
        return processed
    
    def _encode_audio(self, audio_data: np.ndarray, 
                     settings: ConversionSettings,
                     sample_rate: int) -> bytes:
        """Encode audio to target format"""
        buffer = io.BytesIO()
        
        # Use soundfile for basic encoding
        subtype = self._get_soundfile_subtype(settings)
        
        try:
            sf.write(
                buffer, 
                audio_data, 
                sample_rate, 
                format=settings.target_format.value.upper(),
                subtype=subtype
            )
            return buffer.getvalue()
        except Exception as e:
            # Fallback to WAV
            self.logger.warning(f"Encoding failed, falling back to WAV: {e}")
            buffer = io.BytesIO()
            sf.write(buffer, audio_data, sample_rate, format='WAV')
            return buffer.getvalue()
    
    def _get_soundfile_subtype(self, settings: ConversionSettings) -> Optional[str]:
        """Get soundfile subtype for format"""
        subtype_map = {
            AudioFormat.WAV: 'PCM_16' if not settings.bit_depth else f'PCM_{settings.bit_depth}',
            AudioFormat.FLAC: 'PCM_16',
            AudioFormat.OGG: 'VORBIS'
        }
        return subtype_map.get(settings.target_format)
    
    def _extract_metadata(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extract audio metadata"""
        duration = len(audio_data) / sample_rate
        
        return {
            "duration": duration,
            "sample_rate": sample_rate,
            "channels": 1 if audio_data.ndim == 1 else audio_data.shape[0],
            "samples": len(audio_data),
            "bit_depth": "float32",
            "file_size": len(audio_data.tobytes())
        }
    
    def _calculate_quality_metrics(self, original: np.ndarray, converted: np.ndarray) -> Dict[str, float]:
        """Calculate conversion quality metrics"""
        # Ensure same length for comparison
        min_length = min(len(original), len(converted))
        orig_trimmed = original[:min_length]
        conv_trimmed = converted[:min_length]
        
        # Signal-to-noise ratio
        mse = np.mean((orig_trimmed - conv_trimmed) ** 2)
        snr = 10 * np.log10(np.mean(orig_trimmed ** 2) / (mse + 1e-10))
        
        # Correlation
        correlation = np.corrcoef(orig_trimmed, conv_trimmed)[0, 1] if len(orig_trimmed) > 1 else 1.0
        
        # Dynamic range preservation
        orig_dr = 20 * np.log10(np.max(np.abs(orig_trimmed)) / (np.percentile(np.abs(orig_trimmed), 10) + 1e-10))
        conv_dr = 20 * np.log10(np.max(np.abs(conv_trimmed)) / (np.percentile(np.abs(conv_trimmed), 10) + 1e-10))
        dr_preservation = 1.0 - abs(orig_dr - conv_dr) / orig_dr if orig_dr > 0 else 1.0
        
        return {
            "snr_db": float(snr),
            "correlation": float(correlation) if not np.isnan(correlation) else 1.0,
            "dynamic_range_preservation": float(dr_preservation)
        }


class FormatValidator:
    """✅ Audio Format Validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_format(self, audio_data: bytes, expected_format: AudioFormat) -> Dict[str, Any]:
        """Validate audio format"""
        try:
            # Try to read with soundfile
            buffer = io.BytesIO(audio_data)
            info = sf.info(buffer)
            
            return {
                "valid": True,
                "format": info.format,
                "subtype": info.subtype,
                "sample_rate": info.samplerate,
                "channels": info.channels,
                "duration": info.duration
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }


class MetadataPreserver:
    """📋 Audio Metadata Preservation"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def preserve_metadata(self, source_metadata: Dict[str, Any], 
                         converted_audio: bytes) -> bytes:
        """Preserve metadata in converted audio"""
        # Simplified metadata preservation
        # In practice, would use format-specific metadata libraries
        return converted_audio
    
    def extract_metadata(self, audio_file_path: str) -> Dict[str, Any]:
        """Extract metadata from audio file"""
        try:
            info = sf.info(audio_file_path)
            return {
                "format": info.format,
                "subtype": info.subtype,
                "sample_rate": info.samplerate,
                "channels": info.channels,
                "duration": info.duration,
                "frames": info.frames
            }
        except Exception as e:
            self.logger.error(f"Failed to extract metadata: {e}")
            return {}


class BatchConverter:
    """📦 Batch Audio Conversion"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.converter = AudioConverter()
    
    def convert_batch(self, audio_files: List[Tuple[np.ndarray, AudioFormat]], 
                     settings: ConversionSettings) -> List[ConversionResult]:
        """Convert multiple audio files"""
        results = []
        
        for i, (audio_data, source_format) in enumerate(audio_files):
            try:
                result = self.converter.convert(audio_data, source_format, settings)
                results.append(result)
                self.logger.info(f"Converted file {i+1}/{len(audio_files)}")
            except Exception as e:
                self.logger.error(f"Failed to convert file {i+1}: {e}")
                # Add failed result
                results.append(ConversionResult(
                    converted_data=b'',
                    original_format=source_format,
                    target_format=settings.target_format,
                    metadata={},
                    quality_metrics={},
                    file_size_reduction=0.0
                ))
        
        return results


class QualityMaintainer:
    """🎯 Audio Quality Maintenance"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def optimize_conversion_settings(self, audio_data: np.ndarray, 
                                   target_format: AudioFormat,
                                   quality_target: float = 0.9) -> ConversionSettings:
        """Optimize conversion settings for quality target"""
        # Analyze audio characteristics
        complexity = self._analyze_audio_complexity(audio_data)
        
        # Recommend settings based on complexity and target
        if target_format in [AudioFormat.WAV, AudioFormat.FLAC]:
            # Lossless formats
            return ConversionSettings(
                target_format=target_format,
                sample_rate=44100,
                bit_depth=16 if complexity < 0.7 else 24
            )
        else:
            # Lossy formats
            bitrate = self._recommend_bitrate(complexity, quality_target)
            return ConversionSettings(
                target_format=target_format,
                sample_rate=44100,
                bitrate=bitrate,
                quality=quality_target
            )
    
    def _analyze_audio_complexity(self, audio_data: np.ndarray) -> float:
        """Analyze audio complexity for optimization"""
        # Calculate spectral characteristics
        stft = librosa.stft(audio_data)
        magnitude = np.abs(stft)
        
        # Spectral variance as complexity measure
        spectral_variance = np.var(magnitude)
        normalized_complexity = min(spectral_variance / 1000000, 1.0)
        
        return float(normalized_complexity)
    
    def _recommend_bitrate(self, complexity: float, quality_target: float) -> int:
        """Recommend bitrate based on complexity and quality target"""
        base_bitrate = 128
        
        # Adjust for complexity
        complexity_multiplier = 1.0 + complexity
        
        # Adjust for quality target
        quality_multiplier = quality_target * 2
        
        recommended_bitrate = int(base_bitrate * complexity_multiplier * quality_multiplier)
        
        # Clamp to reasonable range
        return min(max(recommended_bitrate, 64), 320)


class FormatDetector:
    """🔍 Audio Format Detection"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def detect_format(self, audio_data: bytes) -> AudioFormat:
        """Detect audio format from data"""
        # Check common format signatures
        if audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:12]:
            return AudioFormat.WAV
        elif audio_data.startswith(b'fLaC'):
            return AudioFormat.FLAC
        elif audio_data.startswith(b'ID3') or audio_data.startswith(b'\xff\xfb'):
            return AudioFormat.MP3
        elif audio_data.startswith(b'OggS'):
            return AudioFormat.OGG
        else:
            # Default to WAV
            return AudioFormat.WAV


class TranscodingEngine:
    """⚙️ Advanced Audio Transcoding Engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.converter = AudioConverter()
        self.validator = FormatValidator()
        self.quality_maintainer = QualityMaintainer()
    
    def transcode(self, input_data: bytes, 
                 target_format: AudioFormat,
                 quality_level: str = "high") -> ConversionResult:
        """Perform intelligent audio transcoding"""
        # Detect input format
        format_detector = FormatDetector()
        source_format = format_detector.detect_format(input_data)
        
        # Load audio data
        buffer = io.BytesIO(input_data)
        audio_data, sample_rate = sf.read(buffer)
        
        # Optimize conversion settings
        quality_targets = {"low": 0.6, "medium": 0.8, "high": 0.95}
        quality_target = quality_targets.get(quality_level, 0.8)
        
        settings = self.quality_maintainer.optimize_conversion_settings(
            audio_data, target_format, quality_target
        )
        
        # Perform conversion
        result = self.converter.convert(audio_data, source_format, settings, sample_rate)
        
        return result


__all__ = [
    'AudioConverter', 'FormatValidator', 'MetadataPreserver', 'BatchConverter',
    'QualityMaintainer', 'FormatDetector', 'TranscodingEngine', 'ConversionSettings'
]