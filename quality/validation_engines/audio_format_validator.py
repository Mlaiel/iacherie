"""
Audio Format Validator module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Audio Format Validator - Ainflue Audio Platform
=============================================

Professional audio format validation and quality assurance framework.
Demonstrates Audio Engineer + ML Engineer + DBA expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import os
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import yaml
import numpy as np
import pandas as pd
import librosa
import soundfile as sf
import mutagen
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from mutagen.mp4 import MP4
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import signal, stats
from scipy.fftpack import fft
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats"""
    MP3 = "mp3"
    FLAC = "flac"
    WAV = "wav"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    OPUS = "opus"
    WMA = "wma"


class AudioQuality(Enum):
    """Audio quality levels"""
    LOSSY_LOW = "lossy_low"      # < 128 kbps
    LOSSY_MEDIUM = "lossy_medium" # 128-192 kbps
    LOSSY_HIGH = "lossy_high"    # 192-320 kbps
    LOSSLESS = "lossless"        # FLAC, WAV
    HIGH_RESOLUTION = "high_res"  # > 48kHz, > 16bit


class ValidationStatus(Enum):
    """Validation result status"""
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"
    CORRUPTED = "corrupted"


class AudioStandard(Enum):
    """Audio quality standards"""
    BROADCAST = "broadcast"      # Professional broadcast standards
    STREAMING = "streaming"      # Streaming platform standards
    MASTERING = "mastering"     # Mastering standards
    PODCAST = "podcast"         # Podcast standards
    MOBILE = "mobile"           # Mobile device optimization


@dataclass
class AudioMetadata:
    """Audio file metadata"""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    bit_depth: Optional[int] = None
    format: Optional[str] = None
    codec: Optional[str] = None
    file_size: Optional[int] = None
    created_date: Optional[datetime] = None
    encoder: Optional[str] = None
    custom_tags: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AudioAnalysis:
    """Audio quality analysis results"""
    file_path: str
    format: AudioFormat
    metadata: AudioMetadata
    technical_metrics: Dict[str, float] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    spectral_analysis: Dict[str, Any] = field(default_factory=dict)
    dynamic_range: Dict[str, float] = field(default_factory=dict)
    frequency_response: Dict[str, Any] = field(default_factory=dict)
    distortion_analysis: Dict[str, float] = field(default_factory=dict)
    noise_analysis: Dict[str, float] = field(default_factory=dict)
    compliance_check: Dict[str, bool] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Audio validation result"""
    file_path: str
    status: ValidationStatus
    quality_level: AudioQuality
    audio_analysis: AudioAnalysis
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    compliance_score: float = 0.0
    overall_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class AudioFormatValidator:
    """
    Professional audio format validation and quality assurance system
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        self.config_path = Path(config_path) if config_path else Path("config/audio_validation.yaml")
        self.config = self._load_config()
        self.database_path = Path("data/audio_validation.db")
        self.validation_history: List[ValidationResult] = []
        self.quality_standards: Dict[AudioStandard, Dict] = {}
        self._initialize_database()
        self._load_quality_standards()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load validation configuration"""
        default_config = {
            "supported_formats": ["mp3", "flac", "wav", "aac", "ogg", "m4a", "opus"],
            "quality_thresholds": {
                "min_sample_rate": 44100,
                "min_bit_depth": 16,
                "min_bitrate": 128,
                "max_file_size_mb": 100,
                "max_duration_minutes": 60,
                "min_dynamic_range_db": 6,
                "max_thd_percent": 1.0,
                "max_noise_floor_db": -60
            },
            "analysis": {
                "fft_size": 2048,
                "hop_length": 512,
                "frequency_bands": [20, 60, 250, 500, 1000, 2000, 4000, 8000, 16000],
                "analyze_full_file": False,
                "analysis_duration": 30  # seconds
            },
            "compliance": {
                "check_metadata": True,
                "require_tags": ["title", "artist"],
                "check_loudness": True,
                "loudness_standard": "LUFS-23",
                "peak_threshold": -1.0
            },
            "optimization": {
                "suggest_improvements": True,
                "auto_tag_correction": False,
                "generate_waveforms": True,
                "generate_spectrograms": False
            }
        }
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config

    def _initialize_database(self) -> None:
        """Initialize SQLite database for validation history"""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audio_validations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    file_hash TEXT,
                    format TEXT,
                    status TEXT,
                    quality_level TEXT,
                    sample_rate INTEGER,
                    bit_depth INTEGER,
                    bitrate INTEGER,
                    duration REAL,
                    channels INTEGER,
                    file_size INTEGER,
                    compliance_score REAL,
                    overall_score REAL,
                    validation_date TEXT,
                    errors TEXT,
                    warnings TEXT,
                    recommendations TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    validation_id INTEGER,
                    metric_name TEXT,
                    metric_value REAL,
                    metric_unit TEXT,
                    FOREIGN KEY (validation_id) REFERENCES audio_validations (id)
                )
            """)

    def _load_quality_standards(self) -> None:
        """Load audio quality standards"""
        self.quality_standards = {
            AudioStandard.BROADCAST: {
                "sample_rate": 48000,
                "bit_depth": 24,
                "loudness": -23,  # LUFS
                "peak": -1.0,     # dBFS
                "dynamic_range": 20,
                "frequency_response": {"20-20000": {"tolerance": 0.5}}
            },
            AudioStandard.STREAMING: {
                "sample_rate": 44100,
                "bit_depth": 16,
                "loudness": -14,  # LUFS
                "peak": -1.0,
                "dynamic_range": 8,
                "formats": ["mp3", "aac", "ogg"]
            },
            AudioStandard.MASTERING: {
                "sample_rate": 96000,
                "bit_depth": 24,
                "dynamic_range": 25,
                "peak": -0.1,
                "formats": ["flac", "wav"]
            },
            AudioStandard.PODCAST: {
                "sample_rate": 44100,
                "bit_depth": 16,
                "loudness": -16,
                "peak": -3.0,
                "mono_acceptable": True
            }
        }

    async def validate_audio_file(self, file_path: str, standard: Optional[AudioStandard] = None) -> ValidationResult:
        """Validate single audio file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return ValidationResult(
                file_path=str(file_path),
                status=ValidationStatus.ERROR,
                quality_level=AudioQuality.LOSSY_LOW,
                audio_analysis=AudioAnalysis(str(file_path), AudioFormat.MP3, AudioMetadata()),
                validation_errors=["File not found"]
            )
        
        logger.info(f"Validating audio file: {file_path}")
        
        try:
            # Extract metadata
            metadata = await self._extract_metadata(file_path)
            
            # Determine format
            audio_format = AudioFormat(file_path.suffix.lower().lstrip('.'))
            
            # Perform audio analysis
            analysis = await self._analyze_audio(file_path, audio_format, metadata)
            
            # Run validation checks
            validation_result = await self._run_validation_checks(file_path, analysis, standard)
            
            # Store results
            await self._store_validation_result(validation_result)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Audio validation failed: {e}")
            return ValidationResult(
                file_path=str(file_path),
                status=ValidationStatus.ERROR,
                quality_level=AudioQuality.LOSSY_LOW,
                audio_analysis=AudioAnalysis(str(file_path), AudioFormat.MP3, AudioMetadata()),
                validation_errors=[str(e)]
            )

    async def _extract_metadata(self, file_path: Path) -> AudioMetadata:
        """Extract comprehensive audio metadata"""
        metadata = AudioMetadata()
        
        try:
            # Use mutagen for metadata extraction
            audio_file = mutagen.File(file_path)
            
            if audio_file is not None:
                # Common tags
                metadata.title = audio_file.get('TIT2', [None])[0] if isinstance(audio_file, ID3) else audio_file.get('TITLE', [None])[0]
                metadata.artist = audio_file.get('TPE1', [None])[0] if isinstance(audio_file, ID3) else audio_file.get('ARTIST', [None])[0]
                metadata.album = audio_file.get('TALB', [None])[0] if isinstance(audio_file, ID3) else audio_file.get('ALBUM', [None])[0]
                
                # Technical metadata
                if hasattr(audio_file, 'info'):
                    info = audio_file.info
                    metadata.duration = getattr(info, 'length', None)
                    metadata.bitrate = getattr(info, 'bitrate', None)
                    metadata.sample_rate = getattr(info, 'sample_rate', None)
                    metadata.channels = getattr(info, 'channels', None)
                    
                    # Format-specific metadata
                    if isinstance(audio_file, MP3):
                        metadata.format = "MP3"
                        metadata.codec = f"MP3 Layer {info.layer}"
                    elif isinstance(audio_file, FLAC):
                        metadata.format = "FLAC"
                        metadata.bit_depth = getattr(info, 'bits_per_sample', None)
                    elif isinstance(audio_file, WAVE):
                        metadata.format = "WAV"
                        metadata.bit_depth = getattr(info, 'bits_per_sample', None)
                    elif isinstance(audio_file, MP4):
                        metadata.format = "AAC/MP4"
                        metadata.codec = getattr(info, 'codec', None)
            
            # File system metadata
            stat = file_path.stat()
            metadata.file_size = stat.st_size
            metadata.created_date = datetime.fromtimestamp(stat.st_ctime)
            
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
        
        return metadata

    async def _analyze_audio(self, file_path: Path, audio_format: AudioFormat, metadata: AudioMetadata) -> AudioAnalysis:
        """Perform comprehensive audio analysis"""
        analysis = AudioAnalysis(
            file_path=str(file_path),
            format=audio_format,
            metadata=metadata
        )
        
        try:
            # Load audio data with librosa
            duration = self.config["analysis"]["analysis_duration"]
            y, sr = librosa.load(file_path, duration=duration if not self.config["analysis"]["analyze_full_file"] else None)
            
            # Basic technical metrics
            analysis.technical_metrics = {
                "actual_sample_rate": sr,
                "actual_duration": len(y) / sr,
                "rms_energy": float(np.sqrt(np.mean(y**2))),
                "peak_amplitude": float(np.max(np.abs(y))),
                "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y))),
                "spectral_centroid": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
                "spectral_rolloff": float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))),
                "spectral_bandwidth": float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
            }
            
            # Dynamic range analysis
            analysis.dynamic_range = await self._analyze_dynamic_range(y, sr)
            
            # Frequency response analysis
            analysis.frequency_response = await self._analyze_frequency_response(y, sr)
            
            # Distortion analysis
            analysis.distortion_analysis = await self._analyze_distortion(y, sr)
            
            # Noise analysis
            analysis.noise_analysis = await self._analyze_noise(y, sr)
            
            # Quality metrics
            analysis.quality_metrics = await self._calculate_quality_metrics(y, sr, analysis)
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            analysis.technical_metrics["error"] = str(e)
        
        return analysis

    async def _analyze_dynamic_range(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Analyze dynamic range characteristics"""
        try:
            # Calculate peak and RMS levels
            peak_db = 20 * np.log10(np.max(np.abs(y)) + 1e-10)
            rms_db = 20 * np.log10(np.sqrt(np.mean(y**2)) + 1e-10)
            
            # Dynamic range (peak to RMS ratio)
            dynamic_range = peak_db - rms_db
            
            # Crest factor
            crest_factor = np.max(np.abs(y)) / (np.sqrt(np.mean(y**2)) + 1e-10)
            crest_factor_db = 20 * np.log10(crest_factor)
            
            # Loudness range (approximation)
            # Divide into segments and calculate range
            segment_length = sr * 3  # 3-second segments
            segments = [y[i:i+segment_length] for i in range(0, len(y), segment_length)]
            segment_rms = [np.sqrt(np.mean(seg**2)) for seg in segments if len(seg) > sr]
            
            if segment_rms:
                loudness_range = 20 * np.log10(max(segment_rms) / (min(segment_rms) + 1e-10))
            else:
                loudness_range = 0
            
            return {
                "peak_db": float(peak_db),
                "rms_db": float(rms_db),
                "dynamic_range_db": float(dynamic_range),
                "crest_factor_db": float(crest_factor_db),
                "loudness_range_db": float(loudness_range)
            }
            
        except Exception as e:
            logger.error(f"Dynamic range analysis failed: {e}")
            return {"error": str(e)}

    async def _analyze_frequency_response(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze frequency response characteristics"""
        try:
            # Calculate FFT
            fft_size = self.config["analysis"]["fft_size"]
            Y = np.fft.fft(y[:fft_size] if len(y) >= fft_size else y, n=fft_size)
            freqs = np.fft.fftfreq(fft_size, 1/sr)
            
            # Get magnitude spectrum
            magnitude = np.abs(Y[:fft_size//2])
            freqs = freqs[:fft_size//2]
            
            # Calculate power in frequency bands
            bands = self.config["analysis"]["frequency_bands"]
            band_power = {}
            
            for i in range(len(bands) - 1):
                low_freq = bands[i]
                high_freq = bands[i + 1]
                
                # Find frequency indices
                low_idx = np.argmin(np.abs(freqs - low_freq))
                high_idx = np.argmin(np.abs(freqs - high_freq))
                
                # Calculate average power in band
                band_magnitude = magnitude[low_idx:high_idx]
                band_power[f"{low_freq}-{high_freq}Hz"] = float(np.mean(band_magnitude**2))
            
            # Find dominant frequency
            dominant_freq_idx = np.argmax(magnitude)
            dominant_frequency = float(freqs[dominant_freq_idx])
            
            # Calculate spectral characteristics
            spectral_centroid = float(np.sum(freqs * magnitude) / np.sum(magnitude))
            spectral_spread = float(np.sqrt(np.sum(((freqs - spectral_centroid) ** 2) * magnitude) / np.sum(magnitude)))
            
            return {
                "band_power": band_power,
                "dominant_frequency": dominant_frequency,
                "spectral_centroid": spectral_centroid,
                "spectral_spread": spectral_spread,
                "frequency_range": [float(freqs[0]), float(freqs[-1])]
            }
            
        except Exception as e:
            logger.error(f"Frequency response analysis failed: {e}")
            return {"error": str(e)}

    async def _analyze_distortion(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Analyze harmonic distortion"""
        try:
            # Simple THD estimation using harmonic analysis
            # This is a simplified approach - professional analysis would be more complex
            
            # Find fundamental frequency
            fft_data = np.fft.fft(y[:sr])  # Analyze first second
            freqs = np.fft.fftfreq(len(fft_data), 1/sr)
            magnitude = np.abs(fft_data)
            
            # Find peak (fundamental)
            positive_freqs = freqs[:len(freqs)//2]
            positive_magnitude = magnitude[:len(magnitude)//2]
            
            fundamental_idx = np.argmax(positive_magnitude[20:])  # Ignore very low frequencies
            fundamental_freq = positive_freqs[fundamental_idx + 20]
            fundamental_magnitude = positive_magnitude[fundamental_idx + 20]
            
            # Look for harmonics
            harmonic_power = 0
            for harmonic in range(2, 6):  # 2nd to 5th harmonics
                harmonic_freq = fundamental_freq * harmonic
                if harmonic_freq < sr / 2:  # Nyquist limit
                    harmonic_idx = np.argmin(np.abs(positive_freqs - harmonic_freq))
                    harmonic_power += positive_magnitude[harmonic_idx] ** 2
            
            # Calculate THD
            if fundamental_magnitude > 0:
                thd_ratio = np.sqrt(harmonic_power) / fundamental_magnitude
                thd_percent = thd_ratio * 100
            else:
                thd_percent = 0
            
            return {
                "thd_percent": float(thd_percent),
                "fundamental_frequency": float(fundamental_freq),
                "harmonic_distortion_ratio": float(thd_ratio) if fundamental_magnitude > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Distortion analysis failed: {e}")
            return {"error": str(e)}

    async def _analyze_noise(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """Analyze noise characteristics"""
        try:
            # Find quiet sections for noise floor estimation
            frame_length = sr // 10  # 100ms frames
            frames = [y[i:i+frame_length] for i in range(0, len(y), frame_length)]
            frame_rms = [np.sqrt(np.mean(frame**2)) for frame in frames if len(frame) == frame_length]
            
            if frame_rms:
                # Assume noise floor is the 10th percentile of RMS values
                noise_floor = np.percentile(frame_rms, 10)
                noise_floor_db = 20 * np.log10(noise_floor + 1e-10)
                
                # Signal-to-noise ratio
                signal_rms = np.sqrt(np.mean(y**2))
                snr_db = 20 * np.log10(signal_rms / (noise_floor + 1e-10))
            else:
                noise_floor_db = -60  # Default
                snr_db = 40  # Default
            
            return {
                "noise_floor_db": float(noise_floor_db),
                "snr_db": float(snr_db),
                "estimated_noise_level": float(noise_floor_db)
            }
            
        except Exception as e:
            logger.error(f"Noise analysis failed: {e}")
            return {"error": str(e)}

    async def _calculate_quality_metrics(self, y: np.ndarray, sr: int, analysis: AudioAnalysis) -> Dict[str, float]:
        """Calculate overall quality metrics"""
        try:
            quality_score = 100.0  # Start with perfect score
            
            # Deduct for poor dynamic range
            dynamic_range = analysis.dynamic_range.get("dynamic_range_db", 0)
            if dynamic_range < self.config["quality_thresholds"]["min_dynamic_range_db"]:
                quality_score -= (self.config["quality_thresholds"]["min_dynamic_range_db"] - dynamic_range) * 2
            
            # Deduct for high distortion
            thd = analysis.distortion_analysis.get("thd_percent", 0)
            if thd > self.config["quality_thresholds"]["max_thd_percent"]:
                quality_score -= (thd - self.config["quality_thresholds"]["max_thd_percent"]) * 10
            
            # Deduct for high noise floor
            noise_floor = analysis.noise_analysis.get("noise_floor_db", -60)
            if noise_floor > self.config["quality_thresholds"]["max_noise_floor_db"]:
                quality_score -= (noise_floor - self.config["quality_thresholds"]["max_noise_floor_db"]) * 0.5
            
            # Deduct for clipping
            peak_amplitude = analysis.technical_metrics.get("peak_amplitude", 0)
            if peak_amplitude >= 0.99:  # Near clipping
                quality_score -= 20
            
            quality_score = max(0, min(100, quality_score))
            
            return {
                "overall_quality_score": float(quality_score),
                "dynamic_range_score": float(max(0, 100 - abs(dynamic_range - 20) * 2)),
                "distortion_score": float(max(0, 100 - thd * 20)),
                "noise_score": float(max(0, 100 + noise_floor + 60)),  # -60dB = 100 score
                "clipping_score": float(max(0, 100 - (peak_amplitude - 0.95) * 500)) if peak_amplitude > 0.95 else 100
            }
            
        except Exception as e:
            logger.error(f"Quality metrics calculation failed: {e}")
            return {"error": str(e)}

    async def _run_validation_checks(self, file_path: Path, analysis: AudioAnalysis, standard: Optional[AudioStandard]) -> ValidationResult:
        """Run comprehensive validation checks"""
        result = ValidationResult(
            file_path=str(file_path),
            status=ValidationStatus.VALID,
            quality_level=AudioQuality.LOSSY_MEDIUM,
            audio_analysis=analysis
        )
        
        try:
            # Check file format support
            if analysis.format.value not in self.config["supported_formats"]:
                result.validation_errors.append(f"Unsupported format: {analysis.format.value}")
                result.status = ValidationStatus.ERROR
            
            # Check technical requirements
            metadata = analysis.metadata
            
            if metadata.sample_rate and metadata.sample_rate < self.config["quality_thresholds"]["min_sample_rate"]:
                result.validation_warnings.append(f"Low sample rate: {metadata.sample_rate}Hz")
            
            if metadata.bitrate and metadata.bitrate < self.config["quality_thresholds"]["min_bitrate"]:
                result.validation_warnings.append(f"Low bitrate: {metadata.bitrate}kbps")
            
            if metadata.file_size and metadata.file_size > self.config["quality_thresholds"]["max_file_size_mb"] * 1024 * 1024:
                result.validation_warnings.append(f"Large file size: {metadata.file_size / (1024*1024):.1f}MB")
            
            if metadata.duration and metadata.duration > self.config["quality_thresholds"]["max_duration_minutes"] * 60:
                result.validation_warnings.append(f"Long duration: {metadata.duration/60:.1f} minutes")
            
            # Quality level determination
            result.quality_level = self._determine_quality_level(analysis)
            
            # Compliance checks for specific standards
            if standard:
                result.compliance_check = await self._check_compliance(analysis, standard)
                result.compliance_score = sum(result.compliance_check.values()) / len(result.compliance_check) * 100
            
            # Overall score
            quality_metrics = analysis.quality_metrics
            result.overall_score = quality_metrics.get("overall_quality_score", 0)
            
            # Generate recommendations
            result.recommendations = await self._generate_recommendations(analysis, result)
            
            # Update status based on findings
            if result.validation_errors:
                result.status = ValidationStatus.ERROR
            elif result.validation_warnings:
                result.status = ValidationStatus.WARNING
            
        except Exception as e:
            result.validation_errors.append(f"Validation failed: {e}")
            result.status = ValidationStatus.ERROR
        
        return result

    def _determine_quality_level(self, analysis: AudioAnalysis) -> AudioQuality:
        """Determine audio quality level"""
        metadata = analysis.metadata
        
        # Check for lossless formats
        if analysis.format in [AudioFormat.FLAC, AudioFormat.WAV]:
            if metadata.sample_rate and metadata.sample_rate > 48000:
                return AudioQuality.HIGH_RESOLUTION
            return AudioQuality.LOSSLESS
        
        # For lossy formats, check bitrate
        if metadata.bitrate:
            if metadata.bitrate >= 192:
                return AudioQuality.LOSSY_HIGH
            elif metadata.bitrate >= 128:
                return AudioQuality.LOSSY_MEDIUM
            else:
                return AudioQuality.LOSSY_LOW
        
        return AudioQuality.LOSSY_MEDIUM

    async def _check_compliance(self, analysis: AudioAnalysis, standard: AudioStandard) -> Dict[str, bool]:
        """Check compliance with audio standards"""
        compliance = {}
        standard_spec = self.quality_standards.get(standard, {})
        metadata = analysis.metadata
        
        # Sample rate compliance
        if "sample_rate" in standard_spec:
            compliance["sample_rate"] = metadata.sample_rate == standard_spec["sample_rate"]
        
        # Bit depth compliance
        if "bit_depth" in standard_spec:
            compliance["bit_depth"] = metadata.bit_depth == standard_spec["bit_depth"]
        
        # Dynamic range compliance
        if "dynamic_range" in standard_spec:
            dr = analysis.dynamic_range.get("dynamic_range_db", 0)
            compliance["dynamic_range"] = dr >= standard_spec["dynamic_range"]
        
        # Peak level compliance
        if "peak" in standard_spec:
            peak_db = analysis.dynamic_range.get("peak_db", 0)
            compliance["peak_level"] = peak_db <= standard_spec["peak"]
        
        # Format compliance
        if "formats" in standard_spec:
            compliance["format"] = analysis.format.value in standard_spec["formats"]
        
        return compliance

    async def _generate_recommendations(self, analysis: AudioAnalysis, result: ValidationResult) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Quality-based recommendations
        if result.overall_score < 70:
            recommendations.append("Consider re-encoding with higher quality settings")
        
        # Format recommendations
        if analysis.format == AudioFormat.MP3 and analysis.metadata.bitrate and analysis.metadata.bitrate < 192:
            recommendations.append("Increase MP3 bitrate to at least 192kbps for better quality")
        
        # Dynamic range recommendations
        dr = analysis.dynamic_range.get("dynamic_range_db", 0)
        if dr < 10:
            recommendations.append("Audio appears heavily compressed - consider reducing dynamic range compression")
        
        # Distortion recommendations
        thd = analysis.distortion_analysis.get("thd_percent", 0)
        if thd > 1.0:
            recommendations.append("High harmonic distortion detected - check recording chain and encoding settings")
        
        # Noise recommendations
        noise_floor = analysis.noise_analysis.get("noise_floor_db", -60)
        if noise_floor > -50:
            recommendations.append("High noise floor detected - consider noise reduction processing")
        
        # Metadata recommendations
        if self.config["compliance"]["check_metadata"]:
            missing_tags = []
            for required_tag in self.config["compliance"]["require_tags"]:
                if not getattr(analysis.metadata, required_tag, None):
                    missing_tags.append(required_tag)
            
            if missing_tags:
                recommendations.append(f"Add missing metadata tags: {', '.join(missing_tags)}")
        
        return recommendations

    async def _store_validation_result(self, result -> None: ValidationResult) -> None:
        """Store validation result in database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                # Calculate file hash
                file_hash = hashlib.md5(Path(result.file_path).read_bytes()).hexdigest()
                
                # Insert main validation record
                cursor = conn.execute("""
                    INSERT INTO audio_validations 
                    (file_path, file_hash, format, status, quality_level, sample_rate, bit_depth, 
                     bitrate, duration, channels, file_size, compliance_score, overall_score, 
                     validation_date, errors, warnings, recommendations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.file_path,
                    file_hash,
                    result.audio_analysis.format.value,
                    result.status.value,
                    result.quality_level.value,
                    result.audio_analysis.metadata.sample_rate,
                    result.audio_analysis.metadata.bit_depth,
                    result.audio_analysis.metadata.bitrate,
                    result.audio_analysis.metadata.duration,
                    result.audio_analysis.metadata.channels,
                    result.audio_analysis.metadata.file_size,
                    result.compliance_score,
                    result.overall_score,
                    result.timestamp.isoformat(),
                    json.dumps(result.validation_errors),
                    json.dumps(result.validation_warnings),
                    json.dumps(result.recommendations)
                ))
                
                validation_id = cursor.lastrowid
                
                # Insert quality metrics
                for metric_name, metric_value in result.audio_analysis.quality_metrics.items():
                    if isinstance(metric_value, (int, float)):
                        conn.execute("""
                            INSERT INTO quality_metrics (validation_id, metric_name, metric_value, metric_unit)
                            VALUES (?, ?, ?, ?)
                        """, (validation_id, metric_name, metric_value, "score"))
                
        except Exception as e:
            logger.error(f"Failed to store validation result: {e}")

    async def validate_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, Any]:
        """Validate all audio files in a directory"""
        directory = Path(directory_path)
        
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        audio_extensions = {f".{fmt}" for fmt in self.config["supported_formats"]}
        
        # Find audio files
        if recursive:
            audio_files = []
            for ext in audio_extensions:
                audio_files.extend(directory.rglob(f"*{ext}"))
        else:
            audio_files = [f for f in directory.iterdir() if f.suffix.lower() in audio_extensions]
        
        logger.info(f"Found {len(audio_files)} audio files in {directory}")
        
        # Validate each file
        results = []
        for file_path in audio_files:
            try:
                result = await self.validate_audio_file(str(file_path))
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to validate {file_path}: {e}")
        
        # Generate summary
        summary = self._generate_directory_summary(results)
        
        return {
            "directory": str(directory),
            "total_files": len(audio_files),
            "validated_files": len(results),
            "summary": summary,
            "results": results
        }

    def _generate_directory_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate summary for directory validation"""
        if not results:
            return {}
        
        status_counts = {}
        quality_counts = {}
        format_counts = {}
        
        total_score = 0
        total_compliance = 0
        
        for result in results:
            # Count statuses
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count quality levels
            quality = result.quality_level.value
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
            
            # Count formats
            format_name = result.audio_analysis.format.value
            format_counts[format_name] = format_counts.get(format_name, 0) + 1
            
            # Accumulate scores
            total_score += result.overall_score
            total_compliance += result.compliance_score
        
        return {
            "status_distribution": status_counts,
            "quality_distribution": quality_counts,
            "format_distribution": format_counts,
            "average_score": total_score / len(results),
            "average_compliance": total_compliance / len(results),
            "validation_passed": status_counts.get("valid", 0),
            "validation_warnings": status_counts.get("warning", 0),
            "validation_errors": status_counts.get("error", 0)
        }

    async def get_validation_history(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get validation history from database"""
        with sqlite3.connect(self.database_path) as conn:
            if file_path:
                cursor = conn.execute(
                    "SELECT * FROM audio_validations WHERE file_path = ? ORDER BY validation_date DESC",
                    (file_path,)
                )
            else:
                cursor = conn.execute("SELECT * FROM audio_validations ORDER BY validation_date DESC LIMIT 100")
            
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


# Global instance
audio_format_validator = AudioFormatValidator()

# Convenience functions
async def validate_audio(file_path -> None: str, standard -> None: Optional[str] = None) -> None:
    """Validate audio file"""
    audio_standard = AudioStandard(standard) if standard else None
    return await audio_format_validator.validate_audio_file(file_path, audio_standard)

async def validate_audio_directory(directory_path -> None: str, recursive -> None: bool = True) -> None:
    """Validate all audio files in directory"""
    return await audio_format_validator.validate_directory(directory_path, recursive)

async def check_broadcast_compliance(file_path -> None: str) -> None:
    """Check broadcast standard compliance"""
    return await audio_format_validator.validate_audio_file(file_path, AudioStandard.BROADCAST)

if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        file_path = "sample_audio.wav"
        result = await validate_audio(file_path, "broadcast")
        print(f"Validation Status: {result.status.value}")
        print(f"Quality Level: {result.quality_level.value}")
        print(f"Overall Score: {result.overall_score:.1f}")
    
    asyncio.run(main())