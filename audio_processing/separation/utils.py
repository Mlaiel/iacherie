"""Utility functions and classes for audio separation operations.

This module provides essential utilities for validation, format conversion,
metadata handling, and audio file operations within the separation pipeline.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - Unauthorized use strictly prohibited
License: Proprietary - Contact for licensing

⚠️ WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or modification is strictly
prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import hashlib
import logging
import mimetypes
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any, BinaryIO
from dataclasses import dataclass
from datetime import datetime
import json
import numpy as np
import librosa
import soundfile as sf
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON
import magic

from ...core.config import get_settings
from ...core.exceptions import AudioProcessingError, ValidationError
from ...utils.logging import get_logger
from .core import OutputFormat, SeparationQuality

logger = get_logger(__name__)


@dataclass
class AudioMetadata:
    """Container for audio file metadata."""    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    bit_depth: Optional[int] = None
    bitrate: Optional[int] = None
    format: Optional[str] = None
    file_size: Optional[int] = None
    creation_date: Optional[datetime] = None
    fingerprint: Optional[str] = None
    custom_tags: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Result of audio validation operations."""    is_valid: bool
    file_format: str
    sample_rate: int
    channels: int
    duration: float
    file_size: int
    issues: List[str]
    metadata: AudioMetadata


class AudioValidator:
    """Professional audio file validation and format detection."""    
    SUPPORTED_FORMATS = {
        'wav': ['audio/wav', 'audio/x-wav', 'audio/wave'],
        'flac': ['audio/flac', 'audio/x-flac'],
        'mp3': ['audio/mpeg', 'audio/mp3'],
        'ogg': ['audio/ogg', 'application/ogg'],
        'aac': ['audio/aac', 'audio/mp4', 'audio/x-m4a'],
        'm4a': ['audio/mp4', 'audio/x-m4a'],
        'aiff': ['audio/aiff', 'audio/x-aiff']
    }
    
    QUALITY_THRESHOLDS = {
        SeparationQuality.DRAFT: {'min_sample_rate': 22050, 'min_bit_depth': 16},
        SeparationQuality.STANDARD: {'min_sample_rate': 44100, 'min_bit_depth': 16},
        SeparationQuality.HIGH: {'min_sample_rate': 48000, 'min_bit_depth': 24},
        SeparationQuality.STUDIO: {'min_sample_rate': 96000, 'min_bit_depth': 32}
    }
    
    def __init__(self, max_file_size: int = 500 * 1024 * 1024):  # 500MB default
        self.max_file_size = max_file_size
        self.magic = magic.Magic(mime=True)
        
    async def validate_file(self, file_path: Union[str, Path]) -> ValidationResult:
        """Validate audio file comprehensively."""        file_path = Path(file_path)
        issues = []
        
        try:
            # Basic file checks
            if not file_path.exists():
                return ValidationResult(
                    is_valid=False,
                    file_format="unknown",
                    sample_rate=0,
                    channels=0,
                    duration=0.0,
                    file_size=0,
                    issues=["File does not exist"],
                    metadata=AudioMetadata()
                )
            
            file_size = file_path.stat().st_size
            
            # Size validation
            if file_size == 0:
                issues.append("File is empty")
            elif file_size > self.max_file_size:
                issues.append(f"File too large: {file_size / (1024*1024):.1f}MB > {self.max_file_size / (1024*1024):.1f}MB")
            
            # MIME type detection
            mime_type = self.magic.from_file(str(file_path))
            file_format = self._detect_format_from_mime(mime_type)
            
            if file_format == "unknown":
                # Fallback to extension
                file_format = self._detect_format_from_extension(file_path.suffix)
                if file_format == "unknown":
                    issues.append(f"Unsupported file format: {mime_type}")
            
            # Audio analysis
            try:
                audio_info = sf.info(str(file_path))
                sample_rate = audio_info.samplerate
                channels = audio_info.channels
                duration = audio_info.duration
                
                # Additional format validation
                if channels < 1 or channels > 8:
                    issues.append(f"Invalid channel count: {channels}")
                
                if sample_rate < 8000 or sample_rate > 192000:
                    issues.append(f"Invalid sample rate: {sample_rate}Hz")
                    
                if duration <= 0:
                    issues.append("Audio has no duration")
                elif duration > 3600:  # 1 hour limit
                    issues.append(f"Audio too long: {duration:.1f}s > 3600s")
                
            except Exception as e:
                issues.append(f"Cannot read audio data: {str(e)}")
                sample_rate = 0
                channels = 0
                duration = 0.0
            
            # Extract metadata
            metadata = await self._extract_metadata(file_path)
            
            # Audio content validation
            if not issues:
                content_issues = await self._validate_audio_content(file_path)
                issues.extend(content_issues)
            
            is_valid = len(issues) == 0
            
            return ValidationResult(
                is_valid=is_valid,
                file_format=file_format,
                sample_rate=sample_rate,
                channels=channels,
                duration=duration,
                file_size=file_size,
                issues=issues,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Validation failed for {file_path}: {str(e)}")
            return ValidationResult(
                is_valid=False,
                file_format="unknown",
                sample_rate=0,
                channels=0,
                duration=0.0,
                file_size=0,
                issues=[f"Validation error: {str(e)}"],
                metadata=AudioMetadata()
            )
    
    async def validate_audio_data(self, audio: np.ndarray, sample_rate: int) -> List[str]:
        """Validate audio numpy array."""        issues = []
        
        try:
            # Basic array validation
            if not isinstance(audio, np.ndarray):
                issues.append("Audio data must be numpy array")
                return issues
            
            if audio.size == 0:
                issues.append("Audio array is empty")
                return issues
            
            # Check for invalid values
            if np.isnan(audio).any():
                issues.append("Audio contains NaN values")
            
            if np.isinf(audio).any():
                issues.append("Audio contains infinite values")
            
            # Dynamic range check
            if np.max(np.abs(audio)) == 0:
                issues.append("Audio is completely silent")
            elif np.max(np.abs(audio)) > 10:
                issues.append("Audio values exceed reasonable range (>10)")
            
            # Clipping detection
            clipping_threshold = 0.99
            clipped_samples = np.sum(np.abs(audio) >= clipping_threshold)
            clipping_ratio = clipped_samples / len(audio)
            
            if clipping_ratio > 0.001:  # 0.1% threshold
                issues.append(f"Audio is clipped ({clipping_ratio*100:.2f}% of samples)")
            
            # DC offset check
            dc_offset = np.mean(audio)
            if abs(dc_offset) > 0.1:
                issues.append(f"Significant DC offset detected: {dc_offset:.3f}")
            
            # Sample rate validation
            if sample_rate < 8000 or sample_rate > 192000:
                issues.append(f"Invalid sample rate: {sample_rate}Hz")
            
            return issues
            
        except Exception as e:
            logger.error(f"Audio data validation failed: {str(e)}")
            return [f"Validation error: {str(e)}"]
    
    def _detect_format_from_mime(self, mime_type: str) -> str:
        """Detect audio format from MIME type."""        for format_name, mime_types in self.SUPPORTED_FORMATS.items():
            if mime_type.lower() in [mt.lower() for mt in mime_types]:
                return format_name
        return "unknown"
    
    def _detect_format_from_extension(self, extension: str) -> str:
        """Detect format from file extension."""        ext = extension.lower().lstrip('.')
        if ext in self.SUPPORTED_FORMATS:
            return ext
        
        # Common extension mappings
        extension_mapping = {
            'wave': 'wav',
            'm4a': 'aac',
            'mp4': 'aac',
            'oga': 'ogg'
        }
        
        return extension_mapping.get(ext, "unknown")
    
    async def _extract_metadata(self, file_path: Path) -> AudioMetadata:
        """Extract comprehensive metadata from audio file."""        try:
            metadata = AudioMetadata()
            
            # Basic file info
            stat = file_path.stat()
            metadata.file_size = stat.st_size
            metadata.creation_date = datetime.fromtimestamp(stat.st_ctime)
            
            # Audio format info
            try:
                info = sf.info(str(file_path))
                metadata.sample_rate = info.samplerate
                metadata.channels = info.channels
                metadata.duration = info.duration
                metadata.format = info.format
                
                # Estimate bit depth from subtype
                if 'PCM_16' in info.subtype:
                    metadata.bit_depth = 16
                elif 'PCM_24' in info.subtype:
                    metadata.bit_depth = 24
                elif 'PCM_32' in info.subtype or 'FLOAT' in info.subtype:
                    metadata.bit_depth = 32
                
            except Exception as e:
                logger.warning(f"Could not extract audio info: {str(e)}")
            
            # Tag extraction using mutagen
            try:
                mutagen_file = MutagenFile(str(file_path))
                if mutagen_file is not None:
                    # Common tags
                    metadata.title = self._get_tag_value(mutagen_file, ['TIT2', 'TITLE', '\xa9nam'])
                    metadata.artist = self._get_tag_value(mutagen_file, ['TPE1', 'ARTIST', '\xa9ART'])
                    metadata.album = self._get_tag_value(mutagen_file, ['TALB', 'ALBUM', '\xa9alb'])
                    metadata.genre = self._get_tag_value(mutagen_file, ['TCON', 'GENRE', '\xa9gen'])
                    
                    # Year extraction
                    year_tag = self._get_tag_value(mutagen_file, ['TDRC', 'DATE', '\xa9day'])
                    if year_tag:
                        try:
                            metadata.year = int(str(year_tag)[:4])
                        except (ValueError, TypeError):
                            pass
                    
                    # Bitrate
                    if hasattr(mutagen_file, 'info') and hasattr(mutagen_file.info, 'bitrate'):
                        metadata.bitrate = mutagen_file.info.bitrate
            
            except Exception as e:
                logger.warning(f"Could not extract metadata tags: {str(e)}")
            
            # Generate audio fingerprint
            try:
                metadata.fingerprint = await self._generate_fingerprint(file_path)
            except Exception as e:
                logger.warning(f"Could not generate fingerprint: {str(e)}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return AudioMetadata()
    
    def _get_tag_value(self, mutagen_file, tag_names: List[str]) -> Optional[str]:
        """Get tag value from mutagen file with fallbacks."""        for tag_name in tag_names:
            if tag_name in mutagen_file:
                value = mutagen_file[tag_name]
                if isinstance(value, list) and len(value) > 0:
                    return str(value[0])
                elif value:
                    return str(value)
        return None
    
    async def _generate_fingerprint(self, file_path: Path) -> str:
        """Generate audio fingerprint for duplicate detection."""        try:
            # Load audio for fingerprinting
            audio, sr = librosa.load(str(file_path), sr=22050, duration=30)  # First 30 seconds
            
            # Generate spectral features
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=12)
            
            # Create feature vector
            features = np.concatenate([
                np.mean(chroma, axis=1),
                np.mean(mfcc, axis=1)
            ])
            
            # Hash the features
            feature_hash = hashlib.md5(features.tobytes()).hexdigest()
            
            return feature_hash
            
        except Exception as e:
            logger.warning(f"Fingerprint generation failed: {str(e)}")
            return hashlib.md5(str(file_path).encode()).hexdigest()
    
    async def _validate_audio_content(self, file_path: Path) -> List[str]:
        """Validate actual audio content."""        issues = []
        
        try:
            # Load audio data for analysis
            audio, sr = librosa.load(str(file_path), sr=None, duration=10)  # First 10 seconds
            
            # Content validation
            content_issues = await self.validate_audio_data(audio, sr)
            issues.extend(content_issues)
            
            # Additional content checks
            
            # Frequency analysis
            freqs, psd = librosa.core.spectrum._welch(audio, nperseg=2048)
            
            # Check for suspicious frequency patterns
            if np.sum(psd) == 0:
                issues.append("Audio appears to be completely silent")
            
            # Check for mono compatibility in stereo files
            if audio.ndim == 2:
                correlation = np.corrcoef(audio[0], audio[1])[0, 1]
                if not np.isnan(correlation) and correlation > 0.99:
                    issues.append("Stereo file appears to be mono (channels are identical)")
            
        except Exception as e:
            issues.append(f"Content analysis failed: {str(e)}")
        
        return issues


class FormatConverter:
    """Professional audio format converter with quality preservation."""    
    def __init__(self):
        self.conversion_profiles = self._setup_conversion_profiles()
        
    def _setup_conversion_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Setup conversion profiles for different output formats."""        return {
            OutputFormat.WAV.value: {
                'format': 'WAV',
                'subtype': 'PCM_24',  # High quality default
                'endian': 'FILE'
            },
            OutputFormat.FLAC.value: {
                'format': 'FLAC',
                'subtype': 'PCM_24',
                'compression_level': 5  # Balanced compression
            },
            'mp3_high': {
                'format': 'mp3',
                'bitrate': '320k',
                'quality': 0
            },
            'mp3_standard': {
                'format': 'mp3',
                'bitrate': '192k', 
                'quality': 2
            }
        }
    
    async def convert_audio(self, audio: np.ndarray, sample_rate: int,
                          output_format: OutputFormat, 
                          output_path: Optional[Path] = None,
                          quality: SeparationQuality = SeparationQuality.HIGH) -> Union[bytes, Path]:
        """Convert audio to specified format."""        try:
            # Validate input
            validator = AudioValidator()
            validation_issues = await validator.validate_audio_data(audio, sample_rate)
            
            if validation_issues:
                logger.warning(f"Audio validation issues: {validation_issues}")
                # Continue with conversion but log issues
            
            # Get conversion profile
            profile = self.conversion_profiles.get(output_format.value, 
                                                 self.conversion_profiles[OutputFormat.WAV.value])
            
            # Apply quality adjustments
            profile = self._adjust_profile_for_quality(profile, quality)
            
            # Normalize audio if needed
            if np.max(np.abs(audio)) > 1.0:
                audio = audio / np.max(np.abs(audio)) * 0.95
                logger.warning("Audio normalized to prevent clipping")
            
            # Convert format
            if output_path:
                # Write to file
                await self._write_audio_file(audio, sample_rate, output_path, profile)
                return output_path
            else:
                # Return as bytes
                audio_bytes = await self._convert_to_bytes(audio, sample_rate, profile)
                return audio_bytes
                
        except Exception as e:
            logger.error(f"Format conversion failed: {str(e)}")
            raise AudioProcessingError(f"Conversion error: {str(e)}")
    
    async def batch_convert(self, audio_dict: Dict[str, np.ndarray], 
                          sample_rate: int, output_format: OutputFormat,
                          output_directory: Path,
                          quality: SeparationQuality = SeparationQuality.HIGH) -> Dict[str, Path]:
        """Convert multiple audio files in batch."""        output_directory.mkdir(parents=True, exist_ok=True)
        results = {}
        
        for name, audio in audio_dict.items():
            try:
                # Generate output filename
                safe_name = self._sanitize_filename(name)
                output_path = output_directory / f"{safe_name}.{output_format.value}"
                
                # Convert
                await self.convert_audio(
                    audio=audio,
                    sample_rate=sample_rate,
                    output_format=output_format,
                    output_path=output_path,
                    quality=quality
                )
                
                results[name] = output_path
                logger.info(f"Converted {name} to {output_path}")
                
            except Exception as e:
                logger.error(f"Failed to convert {name}: {str(e)}")
                results[name] = None
        
        return results
    
    def _adjust_profile_for_quality(self, profile: Dict[str, Any], 
                                   quality: SeparationQuality) -> Dict[str, Any]:
        """Adjust conversion profile based on quality setting."""        adjusted_profile = profile.copy()
        
        quality_settings = {
            SeparationQuality.DRAFT: {'bit_depth': 16, 'compression': 8},
            SeparationQuality.STANDARD: {'bit_depth': 16, 'compression': 5},
            SeparationQuality.HIGH: {'bit_depth': 24, 'compression': 3},
            SeparationQuality.STUDIO: {'bit_depth': 32, 'compression': 0}
        }
        
        settings = quality_settings.get(quality, quality_settings[SeparationQuality.HIGH])
        
        # Adjust bit depth
        if 'subtype' in adjusted_profile:
            if settings['bit_depth'] == 16:
                adjusted_profile['subtype'] = adjusted_profile['subtype'].replace('24', '16').replace('32', '16')
            elif settings['bit_depth'] == 32:
                adjusted_profile['subtype'] = adjusted_profile['subtype'].replace('24', '32').replace('16', '32')
        
        # Adjust compression
        if 'compression_level' in adjusted_profile:
            adjusted_profile['compression_level'] = settings['compression']
        
        return adjusted_profile
    
    async def _write_audio_file(self, audio: np.ndarray, sample_rate: int,
                               output_path: Path, profile: Dict[str, Any]) -> None:
        """Write audio to file with specified profile."""        try:
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write using soundfile
            sf.write(
                str(output_path),
                audio.T if audio.ndim > 1 else audio,  # soundfile expects (frames, channels)
                sample_rate,
                **{k: v for k, v in profile.items() if k in ['format', 'subtype', 'endian']}
            )
            
            logger.debug(f"Audio written to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to write audio file: {str(e)}")
            raise AudioProcessingError(f"File write error: {str(e)}")
    
    async def _convert_to_bytes(self, audio: np.ndarray, sample_rate: int,
                               profile: Dict[str, Any]) -> bytes:
        """Convert audio to bytes in specified format."""        try:
            import io
            
            # Create in-memory buffer
            buffer = io.BytesIO()
            
            # Write to buffer
            sf.write(
                buffer,
                audio.T if audio.ndim > 1 else audio,
                sample_rate,
                format=profile.get('format', 'WAV'),
                subtype=profile.get('subtype', 'PCM_24')
            )
            
            # Get bytes
            buffer.seek(0)
            audio_bytes = buffer.read()
            buffer.close()
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Failed to convert to bytes: {str(e)}")
            raise AudioProcessingError(f"Bytes conversion error: {str(e)}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for cross-platform compatibility."""        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        
        # Ensure not empty
        if not filename.strip():
            filename = "audio"
        
        return filename.strip()


class MetadataExtractor:
    """Advanced metadata extraction and management."""    
    def __init__(self):
        self.extractors = {
            'basic': self._extract_basic_metadata,
            'technical': self._extract_technical_metadata,
            'musical': self._extract_musical_metadata,
            'fingerprint': self._extract_fingerprint_data
        }
    
    async def extract_comprehensive_metadata(self, file_path: Path,
                                           extract_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Extract comprehensive metadata from audio file."""        extract_types = extract_types or ['basic', 'technical', 'musical', 'fingerprint']
        metadata = {}
        
        for extract_type in extract_types:
            if extract_type in self.extractors:
                try:
                    type_metadata = await self.extractors[extract_type](file_path)
                    metadata[extract_type] = type_metadata
                except Exception as e:
                    logger.error(f"Failed to extract {extract_type} metadata: {str(e)}")
                    metadata[extract_type] = {"error": str(e)}
        
        # Add extraction timestamp
        metadata['extracted_at'] = datetime.now().isoformat()
        
        return metadata
    
    async def _extract_basic_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract basic file and tag metadata."""        metadata = {}
        
        # File info
        stat = file_path.stat()
        metadata['file'] = {
            'path': str(file_path),
            'name': file_path.name,
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
        
        # Audio format info
        try:
            info = sf.info(str(file_path))
            metadata['audio'] = {
                'duration_seconds': round(info.duration, 3),
                'duration_formatted': self._format_duration(info.duration),
                'sample_rate': info.samplerate,
                'channels': info.channels,
                'format': info.format,
                'subtype': info.subtype
            }
        except Exception as e:
            metadata['audio'] = {'error': str(e)}
        
        # Tags
        try:
            mutagen_file = MutagenFile(str(file_path))
            if mutagen_file:
                metadata['tags'] = {
                    'title': self._get_tag(mutagen_file, ['TIT2', 'TITLE', '\xa9nam']),
                    'artist': self._get_tag(mutagen_file, ['TPE1', 'ARTIST', '\xa9ART']),
                    'album': self._get_tag(mutagen_file, ['TALB', 'ALBUM', '\xa9alb']),
                    'album_artist': self._get_tag(mutagen_file, ['TPE2', 'ALBUMARTIST', 'aART']),
                    'genre': self._get_tag(mutagen_file, ['TCON', 'GENRE', '\xa9gen']),
                    'year': self._get_tag(mutagen_file, ['TDRC', 'DATE', '\xa9day']),
                    'track_number': self._get_tag(mutagen_file, ['TRCK', 'TRACKNUMBER', 'trkn']),
                    'total_tracks': self._get_tag(mutagen_file, ['TRCK', 'TOTALTRACKS', 'trkn']),
                    'composer': self._get_tag(mutagen_file, ['TCOM', 'COMPOSER', '\xa9wrt'])
                }
        except Exception as e:
            metadata['tags'] = {'error': str(e)}
        
        return metadata
    
    async def _extract_technical_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract technical audio analysis metadata."""        try:
            # Load audio for analysis
            audio, sr = librosa.load(str(file_path), sr=None, duration=60)  # First minute
            
            # Basic stats
            metadata = {
                'audio_stats': {
                    'max_amplitude': float(np.max(np.abs(audio))),
                    'rms_level': float(np.sqrt(np.mean(audio ** 2))),
                    'peak_db': float(20 * np.log10(np.max(np.abs(audio))) if np.max(np.abs(audio)) > 0 else -100),
                    'rms_db': float(20 * np.log10(np.sqrt(np.mean(audio ** 2))) if np.sqrt(np.mean(audio ** 2)) > 0 else -100),
                    'dc_offset': float(np.mean(audio)),
                    'zero_crossings': int(np.sum(np.diff(np.sign(audio)) != 0))
                }
            }
            
            # Clipping detection
            clipping_threshold = 0.99
            clipped_samples = np.sum(np.abs(audio) >= clipping_threshold)
            metadata['clipping'] = {
                'samples_clipped': int(clipped_samples),
                'percentage_clipped': float(clipped_samples / len(audio) * 100)
            }
            
            # Dynamic range analysis
            window_size = int(0.1 * sr)  # 100ms windows
            rms_windows = []
            for i in range(0, len(audio) - window_size, window_size):
                window_rms = np.sqrt(np.mean(audio[i:i + window_size] ** 2))
                if window_rms > 0:
                    rms_windows.append(20 * np.log10(window_rms))
            
            if rms_windows:
                metadata['dynamics'] = {
                    'dynamic_range_db': float(max(rms_windows) - min(rms_windows)),
                    'loudest_window_db': float(max(rms_windows)),
                    'quietest_window_db': float(min(rms_windows)),
                    'average_loudness_db': float(np.mean(rms_windows))
                }
            
            # Frequency analysis
            freqs, psd = librosa.core.spectrum._welch(audio, nperseg=2048)
            
            # Frequency bands energy
            bands = [
                ('sub_bass', 20, 60),
                ('bass', 60, 250),
                ('low_mid', 250, 500),
                ('mid', 500, 2000),
                ('upper_mid', 2000, 4000),
                ('presence', 4000, 8000),
                ('brilliance', 8000, 16000)
            ]
            
            band_energies = {}
            total_energy = np.sum(psd)
            
            for band_name, low_freq, high_freq in bands:
                band_mask = (freqs >= low_freq) & (freqs < high_freq)
                band_energy = np.sum(psd[band_mask])
                band_energies[band_name] = float(band_energy / total_energy if total_energy > 0 else 0)
            
            metadata['frequency_bands'] = band_energies
            
            # Spectral characteristics
            spectral_centroid = float(np.sum(freqs * psd) / total_energy if total_energy > 0 else 0)
            spectral_rolloff = freqs[np.where(np.cumsum(psd) >= 0.85 * total_energy)[0][0]] if total_energy > 0 else 0
            
            metadata['spectral'] = {
                'centroid_hz': spectral_centroid,
                'rolloff_hz': float(spectral_rolloff),
                'bandwidth_hz': float(np.sqrt(np.sum(((freqs - spectral_centroid) ** 2) * psd) / total_energy) if total_energy > 0 else 0)
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Technical metadata extraction failed: {str(e)}")
            return {'error': str(e)}
    
    async def _extract_musical_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract musical analysis metadata."""        try:
            # Load audio
            audio, sr = librosa.load(str(file_path), sr=22050, duration=120)  # First 2 minutes
            
            metadata = {}
            
            # Tempo and rhythm analysis
            try:
                tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
                metadata['rhythm'] = {
                    'tempo_bpm': float(tempo),
                    'beat_count': len(beats),
                    'rhythm_strength': float(np.std(np.diff(beats)))
                }
            except Exception as e:
                metadata['rhythm'] = {'error': str(e)}
            
            # Key and pitch analysis
            try:
                chroma = librosa.feature.chroma_cqt(y=audio, sr=sr)
                # Simple key estimation (very basic)
                key_profile = np.mean(chroma, axis=1)
                dominant_key = np.argmax(key_profile)
                key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                
                metadata['harmony'] = {
                    'estimated_key': key_names[dominant_key],
                    'key_strength': float(key_profile[dominant_key]),
                    'chroma_energy_distribution': key_profile.tolist()
                }
            except Exception as e:
                metadata['harmony'] = {'error': str(e)}
            
            # Timbral features
            try:
                mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
                spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
                spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
                zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)
                
                metadata['timbre'] = {
                    'mfcc_mean': np.mean(mfcc, axis=1).tolist(),
                    'spectral_centroid_mean': float(np.mean(spectral_centroid)),
                    'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                    'zero_crossing_rate_mean': float(np.mean(zero_crossing_rate)),
                    'brightness': float(np.mean(spectral_centroid) / sr * 2)  # Normalized brightness
                }
            except Exception as e:
                metadata['timbre'] = {'error': str(e)}
            
            # Energy and dynamics
            try:
                rms_energy = librosa.feature.rms(y=audio)
                onset_frames = librosa.onset.onset_detect(y=audio, sr=sr)
                
                metadata['energy'] = {
                    'average_energy': float(np.mean(rms_energy)),
                    'energy_variance': float(np.var(rms_energy)),
                    'onset_density': float(len(onset_frames) / (len(audio) / sr)),
                    'attack_rate': float(len(onset_frames))
                }
            except Exception as e:
                metadata['energy'] = {'error': str(e)}
            
            return metadata
            
        except Exception as e:
            logger.error(f"Musical metadata extraction failed: {str(e)}")
            return {'error': str(e)}
    
    async def _extract_fingerprint_data(self, file_path: Path) -> Dict[str, Any]:
        """Extract audio fingerprint and identification data."""        try:
            # Load audio for fingerprinting
            audio, sr = librosa.load(str(file_path), sr=22050, duration=30)
            
            # Generate multiple types of fingerprints
            fingerprints = {}
            
            # Chroma-based fingerprint
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
            chroma_hash = hashlib.md5(chroma.tobytes()).hexdigest()
            fingerprints['chroma'] = chroma_hash
            
            # MFCC-based fingerprint
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=12)
            mfcc_hash = hashlib.md5(mfcc.tobytes()).hexdigest()
            fingerprints['mfcc'] = mfcc_hash
            
            # Spectral features fingerprint
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
            spectral_features = np.concatenate([spectral_centroid.flatten(), spectral_rolloff.flatten()])
            spectral_hash = hashlib.md5(spectral_features.tobytes()).hexdigest()
            fingerprints['spectral'] = spectral_hash
            
            # Combined fingerprint
            combined_features = np.concatenate([
                np.mean(chroma, axis=1),
                np.mean(mfcc, axis=1),
                [np.mean(spectral_centroid), np.mean(spectral_rolloff)]
            ])
            combined_hash = hashlib.md5(combined_features.tobytes()).hexdigest()
            fingerprints['combined'] = combined_hash
            
            # File-based hash for exact duplicate detection
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            fingerprints['file'] = file_hash
            
            return {
                'fingerprints': fingerprints,
                'feature_vector': combined_features.tolist(),
                'generation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Fingerprint extraction failed: {str(e)}")
            return {'error': str(e)}
    
    def _get_tag(self, mutagen_file, tag_names: List[str]) -> Optional[str]:
        """Get tag value with multiple fallbacks."""        for tag_name in tag_names:
            if tag_name in mutagen_file:
                value = mutagen_file[tag_name]
                if isinstance(value, list) and len(value) > 0:
                    return str(value[0])
                elif value:
                    return str(value)
        return None
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    async def export_metadata(self, metadata: Dict[str, Any], 
                            output_path: Path, format: str = 'json') -> None:
        """Export metadata to file."""        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
        elif format.lower() == 'yaml':
            import yaml
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        logger.info(f"Metadata exported to {output_path}")


# Utility functions
async def validate_and_convert_audio(input_path: Union[str, Path],
                                   output_format: OutputFormat = OutputFormat.WAV,
                                   quality: SeparationQuality = SeparationQuality.HIGH) -> Tuple[ValidationResult, Optional[Path]]:
    """Convenience function to validate and convert audio."""    input_path = Path(input_path)
    
    # Validate
    validator = AudioValidator()
    validation_result = await validator.validate_file(input_path)
    
    if not validation_result.is_valid:
        return validation_result, None
    
    # Convert if needed
    if validation_result.file_format != output_format.value:
        try:
            # Load audio
            audio, sr = librosa.load(str(input_path), sr=None)
            
            # Convert
            converter = FormatConverter()
            output_path = input_path.parent / f"{input_path.stem}_converted.{output_format.value}"
            
            await converter.convert_audio(
                audio=audio,
                sample_rate=sr,
                output_format=output_format,
                output_path=output_path,
                quality=quality
            )
            
            return validation_result, output_path
            
        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            return validation_result, None
    
    return validation_result, input_path


def calculate_audio_similarity(audio1: np.ndarray, audio2: np.ndarray, 
                             method: str = 'spectral') -> float:
    """Calculate similarity between two audio signals."""    try:
        # Ensure same length
        min_len = min(len(audio1), len(audio2))
        a1 = audio1[:min_len]
        a2 = audio2[:min_len]
        
        if method == 'correlation':
            # Cross-correlation
            correlation = np.corrcoef(a1, a2)[0, 1]
            return abs(correlation) if not np.isnan(correlation) else 0.0
            
        elif method == 'spectral':
            # Spectral similarity
            stft1 = librosa.stft(a1)
            stft2 = librosa.stft(a2)
            
            mag1 = np.abs(stft1)
            mag2 = np.abs(stft2)
            
            # Cosine similarity
            mag1_flat = mag1.flatten()
            mag2_flat = mag2.flatten()
            
            dot_product = np.dot(mag1_flat, mag2_flat)
            norm1 = np.linalg.norm(mag1_flat)
            norm2 = np.linalg.norm(mag2_flat)
            
            if norm1 > 0 and norm2 > 0:
                return dot_product / (norm1 * norm2)
            else:
                return 0.0
                
        elif method == 'mfcc':
            # MFCC-based similarity
            mfcc1 = librosa.feature.mfcc(y=a1, sr=22050, n_mfcc=12)
            mfcc2 = librosa.feature.mfcc(y=a2, sr=22050, n_mfcc=12)
            
            # Dynamic time warping distance
            from scipy.spatial.distance import euclidean
            from fastdtw import fastdtw
            
            distance, _ = fastdtw(mfcc1.T, mfcc2.T, dist=euclidean)
            
            # Convert distance to similarity (0-1 range)
            max_possible_distance = np.sqrt(12) * min(mfcc1.shape[1], mfcc2.shape[1])
            similarity = max(0, 1 - (distance / max_possible_distance))
            
            return similarity
        
        else:
            raise ValueError(f"Unknown similarity method: {method}")
            
    except Exception as e:
        logger.error(f"Similarity calculation failed: {str(e)}")
        return 0.0
