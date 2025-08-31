"""Multimedia Content Validators
Comprehensive validation for multimedia content integrity and quality

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer, Backend Senior Engineer, ML Engineer, 
              Database Administrator, Security Expert, Microservices Architect,
              Multimedia Processing Specialist, DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.
"""import asyncio
import logging
import mimetypes
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
import magic
import cv2
import numpy as np
from PIL import Image
import librosa
import soundfile as sf
import ffmpeg
from moviepy import VideoFileClip

from .formats import (
    ContentFormat, AudioFormat, VideoFormat, ImageFormat, 
    SupportedFormats, QualityLevel
)
from ..core.exceptions import ValidationError, UnsupportedFormatError
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ValidationRule:
    """Validation rule definition"""    name: str
    severity: str  # 'error', 'warning', 'info'
    description: str
    check_function: Optional[callable] = None
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of content validation"""    is_valid: bool
    content_path: Path
    content_type: ContentFormat
    file_size: int = 0
    detected_format: Optional[str] = None
    mime_type: Optional[str] = None
    
    # Validation results
    passed_rules: List[str] = field(default_factory=list)
    failed_rules: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # Technical metrics
    quality_score: float = 0.0
    integrity_score: float = 0.0
    security_score: float = 0.0
    
    # Detailed analysis
    metadata_valid: bool = True
    content_readable: bool = True
    format_consistent: bool = True
    no_corruption: bool = True
    no_malware: bool = True
    
    # Performance metrics
    validation_time: float = 0.0
    file_hash: Optional[str] = None
    
    # Additional info
    technical_details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class BaseValidator(ABC):
    """Abstract base class for content validators"""    
    def __init__(self):
        self.validation_rules = self._initialize_rules()
        
    @abstractmethod
    async def validate(self, content_path: Path) -> ValidationResult:
        """Validate content and return result"""        pass
    
    @abstractmethod
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """Check if validator supports format"""        pass
    
    @abstractmethod
    def _initialize_rules(self) -> List[ValidationRule]:
        """Initialize validation rules"""        pass
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _detect_mime_type(self, file_path: Path) -> Optional[str]:
        """Detect MIME type using multiple methods"""        # Try with python-magic first (more accurate)
        try:
            mime = magic.Magic(mime=True)
            return mime.from_file(str(file_path))
        except:
            pass
        
        # Fallback to mimetypes module
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type
    
    def _check_file_accessibility(self, file_path: Path) -> bool:
        """Check if file is accessible and readable"""        try:
            return file_path.exists() and file_path.is_file() and file_path.stat().st_size > 0
        except:
            return False


class AudioValidator(BaseValidator):
    """Professional audio content validator"""    
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """Check if validator supports audio format"""        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.AUDIO
        return SupportedFormats.is_audio_format(format_type)
    
    def _initialize_rules(self) -> List[ValidationRule]:
        """Initialize audio validation rules"""        return [
            ValidationRule(
                name="file_accessibility",
                severity="error",
                description="File must be accessible and readable"
            ),
            ValidationRule(
                name="format_support",
                severity="error",
                description="Audio format must be supported"
            ),
            ValidationRule(
                name="audio_loadable",
                severity="error",
                description="Audio file must be loadable by audio libraries"
            ),
            ValidationRule(
                name="duration_reasonable",
                severity="warning",
                description="Audio duration should be reasonable",
                parameters={"min_duration": 0.1, "max_duration": 7200}  # 2 hours max
            ),
            ValidationRule(
                name="sample_rate_valid",
                severity="warning",
                description="Sample rate should be standard",
                parameters={"valid_rates": [8000, 16000, 22050, 44100, 48000, 96000, 192000]}
            ),
            ValidationRule(
                name="no_clipping",
                severity="warning",
                description="Audio should not have significant clipping"
            ),
            ValidationRule(
                name="sufficient_dynamic_range",
                severity="info",
                description="Audio should have sufficient dynamic range",
                parameters={"min_dynamic_range": 10}  # dB
            ),
            ValidationRule(
                name="no_silence_only",
                severity="warning",
                description="Audio should not be complete silence"
            ),
            ValidationRule(
                name="metadata_consistent",
                severity="info",
                description="Metadata should be consistent with actual content"
            )
        ]
    
    async def validate(self, content_path: Path) -> ValidationResult:
        """Validate audio content"""        start_time = datetime.now()
        
        result = ValidationResult(
            is_valid=True,
            content_path=content_path,
            content_type=ContentFormat.AUDIO,
            file_size=content_path.stat().st_size if content_path.exists() else 0
        )
        
        # Calculate file hash
        if content_path.exists():
            result.file_hash = self._calculate_file_hash(content_path)
            result.mime_type = self._detect_mime_type(content_path)
        
        # Run validation rules
        for rule in self.validation_rules:
            try:
                passed = await self._check_rule(rule, content_path, result)
                if passed:
                    result.passed_rules.append(rule.name)
                else:
                    result.failed_rules.append(rule.name)
                    if rule.severity == "error":
                        result.errors.append(f"{rule.name}: {rule.description}")
                        result.is_valid = False
                    elif rule.severity == "warning":
                        result.warnings.append(f"{rule.name}: {rule.description}")
                        
            except Exception as e:
                logger.error(f"Rule {rule.name} failed with exception: {str(e)}")
                result.errors.append(f"{rule.name}: Exception during validation")
                if rule.severity == "error":
                    result.is_valid = False
        
        # Calculate scores
        result.quality_score = await self._calculate_quality_score(content_path, result)
        result.integrity_score = await self._calculate_integrity_score(result)
        result.security_score = await self._calculate_security_score(content_path, result)
        
        # Generate recommendations
        result.recommendations = await self._generate_recommendations(result)
        
        result.validation_time = (datetime.now() - start_time).total_seconds()
        return result
    
    async def _check_rule(self, rule: ValidationRule, content_path: Path, 
                         result: ValidationResult) -> bool:
        """Check individual validation rule"""        
        if rule.name == "file_accessibility":
            return self._check_file_accessibility(content_path)
        
        elif rule.name == "format_support":
            extension = content_path.suffix.lower().lstrip('.')
            return SupportedFormats.is_audio_format(extension)
        
        elif rule.name == "audio_loadable":
            try:
                audio, sr = librosa.load(str(content_path), sr=None, duration=1.0)
                result.content_readable = True
                result.detected_format = content_path.suffix.lower().lstrip('.')
                return len(audio) > 0
            except:
                result.content_readable = False
                return False
        
        elif rule.name == "duration_reasonable":
            try:
                duration = librosa.get_duration(filename=str(content_path))
                result.technical_details['duration'] = duration
                
                min_dur = rule.parameters.get("min_duration", 0.1)
                max_dur = rule.parameters.get("max_duration", 7200)
                
                return min_dur <= duration <= max_dur
            except:
                return False
        
        elif rule.name == "sample_rate_valid":
            try:
                audio, sr = librosa.load(str(content_path), sr=None, duration=1.0)
                result.technical_details['sample_rate'] = sr
                
                valid_rates = rule.parameters.get("valid_rates", [44100])
                return sr in valid_rates
            except:
                return False
        
        elif rule.name == "no_clipping":
            try:
                audio, sr = librosa.load(str(content_path), sr=None)
                clipping_threshold = 0.95
                clipped_samples = np.sum(np.abs(audio) > clipping_threshold)
                clipping_ratio = clipped_samples / len(audio)
                
                result.technical_details['clipping_ratio'] = float(clipping_ratio)
                return clipping_ratio < 0.01  # Less than 1% clipping
            except:
                return False
        
        elif rule.name == "sufficient_dynamic_range":
            try:
                audio, sr = librosa.load(str(content_path), sr=None)
                peak_amplitude = np.max(np.abs(audio))
                rms_amplitude = np.sqrt(np.mean(audio**2))
                
                if rms_amplitude > 0:
                    dynamic_range = 20 * np.log10(peak_amplitude / rms_amplitude)
                    result.technical_details['dynamic_range'] = float(dynamic_range)
                    
                    min_range = rule.parameters.get("min_dynamic_range", 10)
                    return dynamic_range >= min_range
                return False
            except:
                return False
        
        elif rule.name == "no_silence_only":
            try:
                audio, sr = librosa.load(str(content_path), sr=None)
                energy = np.mean(audio**2)
                result.technical_details['average_energy'] = float(energy)
                
                # Check if audio has sufficient energy (not complete silence)
                return energy > 1e-8
            except:
                return False
        
        elif rule.name == "metadata_consistent":
            try:
                # Load with librosa and soundfile to compare
                audio, sr = librosa.load(str(content_path), sr=None)
                
                # Try to load metadata with soundfile
                try:
                    info = sf.info(str(content_path))
                    duration_sf = info.duration
                    sr_sf = info.samplerate
                    
                    # Compare durations (allow 1% tolerance)
                    duration_librosa = len(audio) / sr
                    duration_diff = abs(duration_sf - duration_librosa) / max(duration_sf, duration_librosa)
                    
                    # Compare sample rates
                    sr_consistent = sr == sr_sf
                    
                    result.metadata_valid = duration_diff < 0.01 and sr_consistent
                    return result.metadata_valid
                except:
                    return True  # If can't check metadata, assume consistent
            except:
                return False
        
        return True
    
    async def _calculate_quality_score(self, content_path: Path, 
                                     result: ValidationResult) -> float:
        """Calculate overall audio quality score"""        try:
            audio, sr = librosa.load(str(content_path), sr=None)
            
            quality_factors = []
            
            # Sample rate quality (higher is generally better)
            sr_score = min(sr / 48000, 1.0)
            quality_factors.append(sr_score * 0.2)
            
            # Dynamic range quality
            dynamic_range = result.technical_details.get('dynamic_range', 0)
            dr_score = min(dynamic_range / 20, 1.0)
            quality_factors.append(dr_score * 0.3)
            
            # Clipping penalty
            clipping_ratio = result.technical_details.get('clipping_ratio', 0)
            clipping_score = max(0, 1.0 - clipping_ratio * 10)
            quality_factors.append(clipping_score * 0.2)
            
            # Signal-to-noise ratio estimation
            try:
                # Simple SNR estimation using spectral analysis
                stft = librosa.stft(audio)
                magnitude = np.abs(stft)
                noise_floor = np.percentile(magnitude, 5)  # Bottom 5% as noise estimate
                signal_level = np.percentile(magnitude, 95)  # Top 5% as signal
                
                if noise_floor > 0:
                    snr = 20 * np.log10(signal_level / noise_floor)
                    snr_score = min(snr / 60, 1.0)  # Normalize to 60dB
                    quality_factors.append(snr_score * 0.3)
            except:
                quality_factors.append(0.5)  # Default moderate score
            
            return sum(quality_factors)
            
        except:
            return 0.0
    
    async def _calculate_integrity_score(self, result: ValidationResult) -> float:
        """Calculate content integrity score"""        integrity_factors = []
        
        # File accessibility
        if result.content_readable:
            integrity_factors.append(0.3)
        
        # Format consistency
        if result.format_consistent:
            integrity_factors.append(0.2)
        
        # Metadata consistency
        if result.metadata_valid:
            integrity_factors.append(0.2)
        
        # No corruption indicators
        if result.no_corruption:
            integrity_factors.append(0.3)
        
        return sum(integrity_factors)
    
    async def _calculate_security_score(self, content_path: Path, 
                                      result: ValidationResult) -> float:
        """Calculate security score for audio file"""        security_factors = []
        
        # Basic file structure validation
        try:
            # Check if file loads without errors
            audio, sr = librosa.load(str(content_path), sr=None, duration=5.0)  # First 5 seconds
            security_factors.append(0.4)
        except:
            pass
        
        # File size reasonableness
        file_size = result.file_size
        if 1000 < file_size < 100_000_000:  # Between 1KB and 100MB
            security_factors.append(0.3)
        
        # Extension/MIME consistency
        extension = content_path.suffix.lower().lstrip('.')
        if result.mime_type:
            expected_mimes = SupportedFormats.AUDIO_FORMATS.get(
                AudioFormat(extension), 
                type('', (), {'mime_types': set()})()
            ).mime_types
            if any(mime in result.mime_type for mime in expected_mimes):
                security_factors.append(0.3)
        
        return sum(security_factors)
    
    async def _generate_recommendations(self, result: ValidationResult) -> List[str]:
        """Generate improvement recommendations"""        recommendations = []
        
        if not result.content_readable:
            recommendations.append("File appears to be corrupted or in an unsupported format")
        
        clipping_ratio = result.technical_details.get('clipping_ratio', 0)
        if clipping_ratio > 0.01:
            recommendations.append(f"Audio has {clipping_ratio*100:.1f}% clipping - consider using less aggressive compression")
        
        dynamic_range = result.technical_details.get('dynamic_range', 0)
        if dynamic_range < 10:
            recommendations.append("Audio has limited dynamic range - consider mastering with less compression")
        
        sample_rate = result.technical_details.get('sample_rate', 0)
        if sample_rate < 44100:
            recommendations.append("Consider using higher sample rate (44.1kHz or 48kHz) for better quality")
        
        duration = result.technical_details.get('duration', 0)
        if duration > 3600:  # 1 hour
            recommendations.append("Very long audio file - consider splitting for better handling")
        
        if result.quality_score < 0.5:
            recommendations.append("Overall audio quality is below average - consider re-encoding with better settings")
        
        return recommendations


class VideoValidator(BaseValidator):
    """Professional video content validator"""    
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """Check if validator supports video format"""        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.VIDEO
        return SupportedFormats.is_video_format(format_type)
    
    def _initialize_rules(self) -> List[ValidationRule]:
        """Initialize video validation rules"""        return [
            ValidationRule(
                name="file_accessibility",
                severity="error",
                description="File must be accessible and readable"
            ),
            ValidationRule(
                name="format_support",
                severity="error",
                description="Video format must be supported"
            ),
            ValidationRule(
                name="video_loadable",
                severity="error",
                description="Video file must be loadable by video libraries"
            ),
            ValidationRule(
                name="has_video_stream",
                severity="error",
                description="File must contain at least one video stream"
            ),
            ValidationRule(
                name="resolution_reasonable",
                severity="warning",
                description="Video resolution should be reasonable",
                parameters={"min_width": 32, "max_width": 7680, "min_height": 32, "max_height": 4320}
            ),
            ValidationRule(
                name="fps_reasonable",
                severity="warning",
                description="Frame rate should be reasonable",
                parameters={"min_fps": 1, "max_fps": 120}
            ),
            ValidationRule(
                name="duration_reasonable",
                severity="warning",
                description="Video duration should be reasonable",
                parameters={"min_duration": 0.1, "max_duration": 14400}  # 4 hours max
            ),
            ValidationRule(
                name="no_major_corruption",
                severity="error",
                description="Video should not have major corruption"
            ),
            ValidationRule(
                name="audio_video_sync",
                severity="warning",
                description="Audio and video streams should be synchronized"
            ),
            ValidationRule(
                name="consistent_framerate",
                severity="info",
                description="Frame rate should be consistent throughout"
            )
        ]
    
    async def validate(self, content_path: Path) -> ValidationResult:
        """Validate video content"""        start_time = datetime.now()
        
        result = ValidationResult(
            is_valid=True,
            content_path=content_path,
            content_type=ContentFormat.VIDEO,
            file_size=content_path.stat().st_size if content_path.exists() else 0
        )
        
        # Calculate file hash
        if content_path.exists():
            result.file_hash = self._calculate_file_hash(content_path)
            result.mime_type = self._detect_mime_type(content_path)
        
        # Run validation rules
        for rule in self.validation_rules:
            try:
                passed = await self._check_rule(rule, content_path, result)
                if passed:
                    result.passed_rules.append(rule.name)
                else:
                    result.failed_rules.append(rule.name)
                    if rule.severity == "error":
                        result.errors.append(f"{rule.name}: {rule.description}")
                        result.is_valid = False
                    elif rule.severity == "warning":
                        result.warnings.append(f"{rule.name}: {rule.description}")
                        
            except Exception as e:
                logger.error(f"Rule {rule.name} failed with exception: {str(e)}")
                result.errors.append(f"{rule.name}: Exception during validation")
                if rule.severity == "error":
                    result.is_valid = False
        
        # Calculate scores
        result.quality_score = await self._calculate_quality_score(content_path, result)
        result.integrity_score = await self._calculate_integrity_score(result)
        result.security_score = await self._calculate_security_score(content_path, result)
        
        # Generate recommendations
        result.recommendations = await self._generate_recommendations(result)
        
        result.validation_time = (datetime.now() - start_time).total_seconds()
        return result
    
    async def _check_rule(self, rule: ValidationRule, content_path: Path, 
                         result: ValidationResult) -> bool:
        """Check individual validation rule"""        
        if rule.name == "file_accessibility":
            return self._check_file_accessibility(content_path)
        
        elif rule.name == "format_support":
            extension = content_path.suffix.lower().lstrip('.')
            return SupportedFormats.is_video_format(extension)
        
        elif rule.name == "video_loadable":
            try:
                probe = ffmpeg.probe(str(content_path))
                result.content_readable = True
                result.detected_format = content_path.suffix.lower().lstrip('.')
                return True
            except:
                result.content_readable = False
                return False
        
        elif rule.name == "has_video_stream":
            try:
                probe = ffmpeg.probe(str(content_path))
                video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
                result.technical_details['video_stream_count'] = len(video_streams)
                return len(video_streams) > 0
            except:
                return False
        
        elif rule.name == "resolution_reasonable":
            try:
                probe = ffmpeg.probe(str(content_path))
                video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
                
                if video_streams:
                    stream = video_streams[0]
                    width = int(stream.get('width', 0))
                    height = int(stream.get('height', 0))
                    
                    result.technical_details['width'] = width
                    result.technical_details['height'] = height
                    
                    min_w = rule.parameters.get('min_width', 32)
                    max_w = rule.parameters.get('max_width', 7680)
                    min_h = rule.parameters.get('min_height', 32)
                    max_h = rule.parameters.get('max_height', 4320)
                    
                    return min_w <= width <= max_w and min_h <= height <= max_h
                return False
            except:
                return False
        
        elif rule.name == "fps_reasonable":
            try:
                probe = ffmpeg.probe(str(content_path))
                video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
                
                if video_streams:
                    stream = video_streams[0]
                    fps_str = stream.get('r_frame_rate', '0/1')
                    
                    if '/' in fps_str:
                        num, den = fps_str.split('/')
                        fps = float(num) / float(den) if float(den) != 0 else 0
                    else:
                        fps = float(fps_str)
                    
                    result.technical_details['fps'] = fps
                    
                    min_fps = rule.parameters.get('min_fps', 1)
                    max_fps = rule.parameters.get('max_fps', 120)
                    
                    return min_fps <= fps <= max_fps
                return False
            except:
                return False
        
        elif rule.name == "duration_reasonable":
            try:
                probe = ffmpeg.probe(str(content_path))
                duration = float(probe['format'].get('duration', 0))
                result.technical_details['duration'] = duration
                
                min_dur = rule.parameters.get('min_duration', 0.1)
                max_dur = rule.parameters.get('max_duration', 14400)
                
                return min_dur <= duration <= max_dur
            except:
                return False
        
        elif rule.name == "no_major_corruption":
            try:
                # Try to load a small sample of the video
                video_clip = VideoFileClip(str(content_path))
                
                # Check if we can get basic info
                duration = video_clip.duration
                if duration <= 0:
                    video_clip.close()
                    return False
                
                # Try to extract a frame from the middle
                try:
                    frame = video_clip.get_frame(duration / 2)
                    if frame is None or frame.size == 0:
                        video_clip.close()
                        return False
                except:
                    video_clip.close()
                    return False
                
                video_clip.close()
                result.no_corruption = True
                return True
                
            except:
                result.no_corruption = False
                return False
        
        elif rule.name == "audio_video_sync":
            try:
                probe = ffmpeg.probe(str(content_path))
                
                video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
                audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
                
                if video_streams and audio_streams:
                    video_duration = float(video_streams[0].get('duration', 0))
                    audio_duration = float(audio_streams[0].get('duration', 0))
                    
                    if video_duration > 0 and audio_duration > 0:
                        sync_diff = abs(video_duration - audio_duration)
                        result.technical_details['sync_difference'] = sync_diff
                        
                        # Allow up to 0.1 second difference
                        return sync_diff < 0.1
                
                return True  # No audio stream or can't check - assume synchronized
            except:
                return True
        
        elif rule.name == "consistent_framerate":
            try:
                # This is a simplified check - in practice, you'd need more sophisticated analysis
                probe = ffmpeg.probe(str(content_path))
                video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
                
                if video_streams:
                    stream = video_streams[0]
                    
                    # Check if r_frame_rate and avg_frame_rate are similar
                    r_frame_rate = stream.get('r_frame_rate', '0/1')
                    avg_frame_rate = stream.get('avg_frame_rate', '0/1')
                    
                    def parse_fps(fps_str):
                        if '/' in fps_str:
                            num, den = fps_str.split('/')
                            return float(num) / float(den) if float(den) != 0 else 0
                        return float(fps_str)
                    
                    r_fps = parse_fps(r_frame_rate)
                    avg_fps = parse_fps(avg_frame_rate)
                    
                    if r_fps > 0 and avg_fps > 0:
                        fps_diff = abs(r_fps - avg_fps) / max(r_fps, avg_fps)
                        result.technical_details['fps_consistency'] = 1.0 - fps_diff
                        
                        # Allow up to 5% difference
                        return fps_diff < 0.05
                
                return True
            except:
                return True
        
        return True
    
    async def _calculate_quality_score(self, content_path: Path, 
                                     result: ValidationResult) -> float:
        """Calculate overall video quality score"""        try:
            quality_factors = []
            
            # Resolution quality
            width = result.technical_details.get('width', 0)
            height = result.technical_details.get('height', 0)
            if width > 0 and height > 0:
                total_pixels = width * height
                # Normalize to 4K (3840x2160)
                resolution_score = min(total_pixels / (3840 * 2160), 1.0)
                quality_factors.append(resolution_score * 0.3)
            
            # Frame rate quality
            fps = result.technical_details.get('fps', 0)
            if fps > 0:
                fps_score = min(fps / 60, 1.0)  # Normalize to 60fps
                quality_factors.append(fps_score * 0.2)
            
            # Duration reasonableness
            duration = result.technical_details.get('duration', 0)
            if duration > 0:
                # Penalty for very short or very long videos
                if 1 <= duration <= 3600:  # 1 second to 1 hour is ideal
                    duration_score = 1.0
                elif duration < 1:
                    duration_score = duration
                else:
                    duration_score = max(0.5, 3600 / duration)
                quality_factors.append(duration_score * 0.2)
            
            # Synchronization quality
            sync_diff = result.technical_details.get('sync_difference', 0)
            sync_score = max(0, 1.0 - sync_diff * 10)  # Penalty for sync issues
            quality_factors.append(sync_score * 0.15)
            
            # Frame rate consistency
            fps_consistency = result.technical_details.get('fps_consistency', 1.0)
            quality_factors.append(fps_consistency * 0.15)
            
            return sum(quality_factors)
            
        except:
            return 0.0
    
    async def _calculate_integrity_score(self, result: ValidationResult) -> float:
        """Calculate content integrity score"""        integrity_factors = []
        
        # File accessibility
        if result.content_readable:
            integrity_factors.append(0.25)
        
        # Video streams present
        video_stream_count = result.technical_details.get('video_stream_count', 0)
        if video_stream_count > 0:
            integrity_factors.append(0.25)
        
        # No corruption
        if result.no_corruption:
            integrity_factors.append(0.35)
        
        # Format consistency
        if result.format_consistent:
            integrity_factors.append(0.15)
        
        return sum(integrity_factors)
    
    async def _calculate_security_score(self, content_path: Path, 
                                      result: ValidationResult) -> float:
        """Calculate security score for video file"""        security_factors = []
        
        # Basic file structure validation
        if result.content_readable:
            security_factors.append(0.4)
        
        # File size reasonableness
        file_size = result.file_size
        if 10000 < file_size < 5_000_000_000:  # Between 10KB and 5GB
            security_factors.append(0.3)
        
        # Extension/MIME consistency
        extension = content_path.suffix.lower().lstrip('.')
        if result.mime_type:
            expected_mimes = SupportedFormats.VIDEO_FORMATS.get(
                VideoFormat(extension), 
                type('', (), {'mime_types': set()})()
            ).mime_types
            if any(mime in result.mime_type for mime in expected_mimes):
                security_factors.append(0.3)
        
        return sum(security_factors)
    
    async def _generate_recommendations(self, result: ValidationResult) -> List[str]:
        """Generate improvement recommendations"""        recommendations = []
        
        if not result.content_readable:
            recommendations.append("Video file appears to be corrupted or in an unsupported format")
        
        width = result.technical_details.get('width', 0)
        height = result.technical_details.get('height', 0)
        if width < 720:
            recommendations.append("Consider using higher resolution for better quality (720p minimum recommended)")
        
        fps = result.technical_details.get('fps', 0)
        if fps < 24:
            recommendations.append("Frame rate is very low - consider using at least 24 fps for smooth playback")
        elif fps > 60:
            recommendations.append("Very high frame rate detected - consider if this is necessary for file size optimization")
        
        duration = result.technical_details.get('duration', 0)
        if duration > 7200:  # 2 hours
            recommendations.append("Very long video - consider splitting into segments for better handling")
        
        sync_diff = result.technical_details.get('sync_difference', 0)
        if sync_diff > 0.05:
            recommendations.append("Audio and video streams may be out of sync - consider re-encoding")
        
        if result.quality_score < 0.5:
            recommendations.append("Overall video quality is below average - consider re-encoding with better settings")
        
        return recommendations


class ImageValidator(BaseValidator):
    """Professional image content validator"""    
    def supports_format(self, format_type: Union[str, ContentFormat]) -> bool:
        """Check if validator supports image format"""        if isinstance(format_type, ContentFormat):
            return format_type == ContentFormat.IMAGE
        return SupportedFormats.is_image_format(format_type)
    
    def _initialize_rules(self) -> List[ValidationRule]:
        """Initialize image validation rules"""        return [
            ValidationRule(
                name="file_accessibility",
                severity="error",
                description="File must be accessible and readable"
            ),
            ValidationRule(
                name="format_support",
                severity="error",
                description="Image format must be supported"
            ),
            ValidationRule(
                name="image_loadable",
                severity="error",
                description="Image file must be loadable by image libraries"
            ),
            ValidationRule(
                name="resolution_reasonable",
                severity="warning",
                description="Image resolution should be reasonable",
                parameters={"min_width": 1, "max_width": 32768, "min_height": 1, "max_height": 32768}
            ),
            ValidationRule(
                name="aspect_ratio_reasonable",
                severity="warning",
                description="Aspect ratio should be reasonable",
                parameters={"min_ratio": 0.01, "max_ratio": 100}
            ),
            ValidationRule(
                name="color_depth_adequate",
                severity="info",
                description="Color depth should be adequate for content type"
            ),
            ValidationRule(
                name="no_major_corruption",
                severity="error",
                description="Image should not have major corruption"
            ),
            ValidationRule(
                name="metadata_valid",
                severity="info",
                description="Image metadata should be valid and consistent"
            ),
            ValidationRule(
                name="sufficient_quality",
                severity="info",
                description="Image should have sufficient visual quality"
            )
        ]
    
    async def validate(self, content_path: Path) -> ValidationResult:
        """Validate image content"""        start_time = datetime.now()
        
        result = ValidationResult(
            is_valid=True,
            content_path=content_path,
            content_type=ContentFormat.IMAGE,
            file_size=content_path.stat().st_size if content_path.exists() else 0
        )
        
        # Calculate file hash
        if content_path.exists():
            result.file_hash = self._calculate_file_hash(content_path)
            result.mime_type = self._detect_mime_type(content_path)
        
        # Run validation rules
        for rule in self.validation_rules:
            try:
                passed = await self._check_rule(rule, content_path, result)
                if passed:
                    result.passed_rules.append(rule.name)
                else:
                    result.failed_rules.append(rule.name)
                    if rule.severity == "error":
                        result.errors.append(f"{rule.name}: {rule.description}")
                        result.is_valid = False
                    elif rule.severity == "warning":
                        result.warnings.append(f"{rule.name}: {rule.description}")
                        
            except Exception as e:
                logger.error(f"Rule {rule.name} failed with exception: {str(e)}")
                result.errors.append(f"{rule.name}: Exception during validation")
                if rule.severity == "error":
                    result.is_valid = False
        
        # Calculate scores
        result.quality_score = await self._calculate_quality_score(content_path, result)
        result.integrity_score = await self._calculate_integrity_score(result)
        result.security_score = await self._calculate_security_score(content_path, result)
        
        # Generate recommendations
        result.recommendations = await self._generate_recommendations(result)
        
        result.validation_time = (datetime.now() - start_time).total_seconds()
        return result
    
    async def _check_rule(self, rule: ValidationRule, content_path: Path, 
                         result: ValidationResult) -> bool:
        """Check individual validation rule"""        
        if rule.name == "file_accessibility":
            return self._check_file_accessibility(content_path)
        
        elif rule.name == "format_support":
            extension = content_path.suffix.lower().lstrip('.')
            return SupportedFormats.is_image_format(extension)
        
        elif rule.name == "image_loadable":
            try:
                with Image.open(content_path) as image:
                    # Try to load the image
                    image.load()
                    result.content_readable = True
                    result.detected_format = image.format.lower() if image.format else content_path.suffix.lower().lstrip('.')
                    return True
            except:
                result.content_readable = False
                return False
        
        elif rule.name == "resolution_reasonable":
            try:
                with Image.open(content_path) as image:
                    width, height = image.size
                    result.technical_details['width'] = width
                    result.technical_details['height'] = height
                    
                    min_w = rule.parameters.get('min_width', 1)
                    max_w = rule.parameters.get('max_width', 32768)
                    min_h = rule.parameters.get('min_height', 1)
                    max_h = rule.parameters.get('max_height', 32768)
                    
                    return min_w <= width <= max_w and min_h <= height <= max_h
            except:
                return False
        
        elif rule.name == "aspect_ratio_reasonable":
            try:
                width = result.technical_details.get('width')
                height = result.technical_details.get('height')
                
                if width and height and height > 0:
                    aspect_ratio = width / height
                    result.technical_details['aspect_ratio'] = aspect_ratio
                    
                    min_ratio = rule.parameters.get('min_ratio', 0.01)
                    max_ratio = rule.parameters.get('max_ratio', 100)
                    
                    return min_ratio <= aspect_ratio <= max_ratio
                return False
            except:
                return False
        
        elif rule.name == "color_depth_adequate":
            try:
                with Image.open(content_path) as image:
                    mode = image.mode
                    result.technical_details['color_mode'] = mode
                    
                    # Check if color depth is adequate for the image type
                    adequate_modes = ['RGB', 'RGBA', 'L', 'LA', 'CMYK', 'YCbCr']
                    return mode in adequate_modes
            except:
                return False
        
        elif rule.name == "no_major_corruption":
            try:
                with Image.open(content_path) as image:
                    # Try to verify the image by loading all data
                    image.verify()
                    
                # Reopen for pixel access test (verify() closes the file)
                with Image.open(content_path) as image:
                    # Try to access pixel data
                    width, height = image.size
                    if width > 0 and height > 0:
                        # Sample a few pixels
                        try:
                            pixel = image.getpixel((0, 0))
                            pixel = image.getpixel((width//2, height//2))
                            result.no_corruption = True
                            return True
                        except:
                            result.no_corruption = False
                            return False
                    
                return False
            except:
                result.no_corruption = False
                return False
        
        elif rule.name == "metadata_valid":
            try:
                with Image.open(content_path) as image:
                    # Check EXIF data if present
                    exif_valid = True
                    if hasattr(image, 'getexif'):
                        try:
                            exif = image.getexif()
                            if exif:
                                # Basic EXIF validation
                                for key, value in exif.items():
                                    if not isinstance(key, int) or key < 0:
                                        exif_valid = False
                                        break
                        except:
                            exif_valid = False
                    
                    result.metadata_valid = exif_valid
                    return exif_valid
            except:
                result.metadata_valid = False
                return False
        
        elif rule.name == "sufficient_quality":
            try:
                with Image.open(content_path) as image:
                    # Convert to array for analysis
                    img_array = np.array(image.convert('RGB'))
                    
                    # Calculate basic quality metrics
                    
                    # 1. Sharpness (Laplacian variance)
                    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                    
                    # 2. Contrast (standard deviation)
                    contrast = np.std(gray)
                    
                    # 3. Brightness distribution
                    brightness_mean = np.mean(gray)
                    
                    result.technical_details['sharpness'] = float(laplacian_var)
                    result.technical_details['contrast'] = float(contrast)
                    result.technical_details['brightness'] = float(brightness_mean)
                    
                    # Quality thresholds (these are rough estimates)
                    sufficient_quality = (
                        laplacian_var > 100 and  # Reasonable sharpness
                        contrast > 20 and        # Reasonable contrast
                        10 < brightness_mean < 245  # Not too dark or bright
                    )
                    
                    return sufficient_quality
            except:
                return False
        
        return True
    
    async def _calculate_quality_score(self, content_path: Path, 
                                     result: ValidationResult) -> float:
        """Calculate overall image quality score"""        try:
            quality_factors = []
            
            # Resolution quality
            width = result.technical_details.get('width', 0)
            height = result.technical_details.get('height', 0)
            if width > 0 and height > 0:
                total_pixels = width * height
                # Normalize to 4K (3840x2160)
                resolution_score = min(total_pixels / (3840 * 2160), 1.0)
                quality_factors.append(resolution_score * 0.2)
            
            # Sharpness quality
            sharpness = result.technical_details.get('sharpness', 0)
            if sharpness > 0:
                sharpness_score = min(sharpness / 500, 1.0)  # Normalize
                quality_factors.append(sharpness_score * 0.3)
            
            # Contrast quality
            contrast = result.technical_details.get('contrast', 0)
            if contrast > 0:
                contrast_score = min(contrast / 64, 1.0)  # Normalize
                quality_factors.append(contrast_score * 0.2)
            
            # Brightness balance
            brightness = result.technical_details.get('brightness', 128)
            brightness_balance = 1.0 - abs(brightness - 128) / 128  # Best at middle gray
            quality_factors.append(brightness_balance * 0.15)
            
            # Aspect ratio reasonableness
            aspect_ratio = result.technical_details.get('aspect_ratio', 1.0)
            if 0.5 <= aspect_ratio <= 2.0:  # Common aspect ratios
                aspect_score = 1.0
            else:
                aspect_score = max(0.5, min(2.0, aspect_ratio) / max(aspect_ratio, 2.0))
            quality_factors.append(aspect_score * 0.15)
            
            return sum(quality_factors)
            
        except:
            return 0.0
    
    async def _calculate_integrity_score(self, result: ValidationResult) -> float:
        """Calculate content integrity score"""        integrity_factors = []
        
        # File accessibility
        if result.content_readable:
            integrity_factors.append(0.3)
        
        # No corruption
        if result.no_corruption:
            integrity_factors.append(0.4)
        
        # Metadata validity
        if result.metadata_valid:
            integrity_factors.append(0.2)
        
        # Format consistency
        if result.format_consistent:
            integrity_factors.append(0.1)
        
        return sum(integrity_factors)
    
    async def _calculate_security_score(self, content_path: Path, 
                                      result: ValidationResult) -> float:
        """Calculate security score for image file"""        security_factors = []
        
        # Basic file structure validation
        if result.content_readable and result.no_corruption:
            security_factors.append(0.5)
        
        # File size reasonableness
        file_size = result.file_size
        if 100 < file_size < 100_000_000:  # Between 100 bytes and 100MB
            security_factors.append(0.25)
        
        # Extension/MIME consistency
        extension = content_path.suffix.lower().lstrip('.')
        if result.mime_type:
            expected_mimes = SupportedFormats.IMAGE_FORMATS.get(
                ImageFormat(extension), 
                type('', (), {'mime_types': set()})()
            ).mime_types
            if any(mime in result.mime_type for mime in expected_mimes):
                security_factors.append(0.25)
        
        return sum(security_factors)
    
    async def _generate_recommendations(self, result: ValidationResult) -> List[str]:
        """Generate improvement recommendations"""        recommendations = []
        
        if not result.content_readable:
            recommendations.append("Image file appears to be corrupted or in an unsupported format")
        
        width = result.technical_details.get('width', 0)
        height = result.technical_details.get('height', 0)
        if width < 640 and height < 480:
            recommendations.append("Low resolution image - consider using higher resolution for better quality")
        
        sharpness = result.technical_details.get('sharpness', 0)
        if sharpness < 100:
            recommendations.append("Image appears to be blurry or low sharpness")
        
        contrast = result.technical_details.get('contrast', 0)
        if contrast < 20:
            recommendations.append("Image has low contrast - consider adjusting levels")
        
        brightness = result.technical_details.get('brightness', 128)
        if brightness < 50:
            recommendations.append("Image is very dark - consider brightening")
        elif brightness > 200:
            recommendations.append("Image is very bright - consider darkening")
        
        aspect_ratio = result.technical_details.get('aspect_ratio', 1.0)
        if aspect_ratio > 10 or aspect_ratio < 0.1:
            recommendations.append("Unusual aspect ratio detected - verify this is intentional")
        
        if result.quality_score < 0.5:
            recommendations.append("Overall image quality is below average - consider using better source or re-processing")
        
        return recommendations


class MediaValidator:
    """Universal multimedia content validator"""    
    def __init__(self):
        self.validators = {
            ContentFormat.AUDIO: AudioValidator(),
            ContentFormat.VIDEO: VideoValidator(),
            ContentFormat.IMAGE: ImageValidator()
        }
    
    async def validate(self, content_path: Path, 
                      content_type: Optional[Union[str, ContentFormat]] = None) -> ValidationResult:
        """Validate multimedia content"""        
        # Auto-detect content type if not provided
        if content_type is None:
            content_type = self._detect_content_type(content_path)
        
        if isinstance(content_type, str):
            content_type = ContentFormat(content_type.lower())
        
        # Get appropriate validator
        validator = self.validators.get(content_type)
        if validator is None:
            return ValidationResult(
                is_valid=False,
                content_path=content_path,
                content_type=content_type,
                errors=[f"No validator available for content type: {content_type}"]
            )
        
        # Perform validation
        return await validator.validate(content_path)
    
    def _detect_content_type(self, content_path: Path) -> ContentFormat:
        """Auto-detect content type from file extension"""        extension = content_path.suffix.lower().lstrip('.')
        format_enum = SupportedFormats.get_format_by_extension(extension)
        
        if format_enum:
            if isinstance(format_enum, AudioFormat):
                return ContentFormat.AUDIO
            elif isinstance(format_enum, VideoFormat):
                return ContentFormat.VIDEO
            elif isinstance(format_enum, ImageFormat):
                return ContentFormat.IMAGE
        
        raise UnsupportedFormatError(f"Unable to detect content type for extension: {extension}")
    
    async def batch_validate(self, content_paths: List[Path],
                           content_types: Optional[List[Union[str, ContentFormat]]] = None) -> List[ValidationResult]:
        """Validate multiple multimedia files"""        
        if content_types is None:
            content_types = [None] * len(content_paths)
        elif len(content_types) != len(content_paths):
            raise ValueError("content_types list must match content_paths list length")
        
        # Run validations concurrently
        tasks = []
        for path, content_type in zip(content_paths, content_types):
            task = self.validate(path, content_type)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = ValidationResult(
                    is_valid=False,
                    content_path=content_paths[i],
                    content_type=ContentFormat.IMAGE,  # Default
                    errors=[f"Validation exception: {str(result)}"]
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_validation_statistics(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Calculate validation statistics"""        stats = {
            'total_files': len(results),
            'valid_files': sum(1 for r in results if r.is_valid),
            'invalid_files': sum(1 for r in results if not r.is_valid),
            'files_with_warnings': sum(1 for r in results if r.warnings),
            'average_quality_score': 0.0,
            'average_integrity_score': 0.0,
            'average_security_score': 0.0,
            'content_type_distribution': {},
            'common_issues': {},
            'validation_time_total': sum(r.validation_time for r in results),
            'average_validation_time': 0.0
        }
        
        if results:
            # Average scores
            quality_scores = [r.quality_score for r in results if r.quality_score > 0]
            if quality_scores:
                stats['average_quality_score'] = sum(quality_scores) / len(quality_scores)
            
            integrity_scores = [r.integrity_score for r in results if r.integrity_score > 0]
            if integrity_scores:
                stats['average_integrity_score'] = sum(integrity_scores) / len(integrity_scores)
            
            security_scores = [r.security_score for r in results if r.security_score > 0]
            if security_scores:
                stats['average_security_score'] = sum(security_scores) / len(security_scores)
            
            # Average validation time
            stats['average_validation_time'] = stats['validation_time_total'] / len(results)
            
            # Content type distribution
            for result in results:
                content_type = result.content_type.value
                stats['content_type_distribution'][content_type] = stats['content_type_distribution'].get(content_type, 0) + 1
            
            # Common issues
            for result in results:
                for error in result.errors:
                    issue_type = error.split(':')[0]  # Get rule name
                    stats['common_issues'][issue_type] = stats['common_issues'].get(issue_type, 0) + 1
                
                for warning in result.warnings:
                    issue_type = warning.split(':')[0]  # Get rule name
                    stats['common_issues'][issue_type] = stats['common_issues'].get(issue_type, 0) + 1
        
        # Success rate
        stats['success_rate'] = stats['valid_files'] / stats['total_files'] if stats['total_files'] > 0 else 0
        
        return stats
    
    def get_supported_formats(self) -> Dict[ContentFormat, List[str]]:
        """Get all supported formats by content type"""        return {
            ContentFormat.AUDIO: [fmt.value for fmt in AudioFormat],
            ContentFormat.VIDEO: [fmt.value for fmt in VideoFormat],
            ContentFormat.IMAGE: [fmt.value for fmt in ImageFormat]
        }


# Convenience aliases
ContentValidator = MediaValidator
QualityValidator = MediaValidator
