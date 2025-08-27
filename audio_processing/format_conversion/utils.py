"""
Utility Functions - Professional Audio Format Conversion Utilities

Comprehensive utility functions for audio format conversion operations.
Provides file handling, compression analysis, and helper functions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import tempfile
import shutil
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import os
import stat
import time
from datetime import datetime
import mimetypes
import subprocess

# Audio processing imports
import numpy as np
import soundfile as sf
import librosa
import mutagen

# Compression and analysis
import zlib
import gzip
from collections import defaultdict

from ..core.config import AudioConfig
from ..core.exceptions import FileError, ConversionError
from .models import AudioFormat, FormatSpecification

logger = logging.getLogger(__name__)


class ConversionUtils:
    """
    Professional Conversion Utilities
    
    Advanced utility functions for audio conversion operations including
    format detection, parameter optimization, and conversion planning.
    """
    
    @staticmethod
    def detect_audio_format(file_path: Path) -> Optional[AudioFormat]:
        """
        Detect audio format from file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Detected AudioFormat or None
        """
        try:
            # Method 1: Extension-based detection
            extension = file_path.suffix.lower().lstrip('.')
            extension_mapping = {
                'wav': AudioFormat.WAV,
                'wave': AudioFormat.WAV,
                'flac': AudioFormat.FLAC,
                'mp3': AudioFormat.MP3,
                'aac': AudioFormat.AAC,
                'm4a': AudioFormat.M4A,
                'mp4': AudioFormat.M4A,
                'ogg': AudioFormat.OGG,
                'oga': AudioFormat.OGG,
                'aiff': AudioFormat.AIFF,
                'aif': AudioFormat.AIFF,
                'wma': AudioFormat.WMA,
                'ape': AudioFormat.APE,
                'opus': AudioFormat.OPUS
            }
            
            format_from_ext = extension_mapping.get(extension)
            
            # Method 2: Content-based detection using mutagen
            try:
                audio_file = mutagen.File(str(file_path))
                if audio_file:
                    file_type = type(audio_file).__name__
                    mutagen_mapping = {
                        'MP3': AudioFormat.MP3,
                        'FLAC': AudioFormat.FLAC,
                        'MP4': AudioFormat.M4A,
                        'OggVorbis': AudioFormat.OGG,
                        'WAVE': AudioFormat.WAV,
                        'AIFF': AudioFormat.AIFF
                    }
                    format_from_content = mutagen_mapping.get(file_type)
                    
                    # Prioritize content detection
                    if format_from_content:
                        return format_from_content
                        
            except Exception:
                pass
            
            # Method 3: MIME type detection
            try:
                mime_type, _ = mimetypes.guess_type(str(file_path))
                if mime_type:
                    mime_mapping = {
                        'audio/wav': AudioFormat.WAV,
                        'audio/x-wav': AudioFormat.WAV,
                        'audio/flac': AudioFormat.FLAC,
                        'audio/mpeg': AudioFormat.MP3,
                        'audio/mp3': AudioFormat.MP3,
                        'audio/aac': AudioFormat.AAC,
                        'audio/mp4': AudioFormat.M4A,
                        'audio/ogg': AudioFormat.OGG,
                        'audio/aiff': AudioFormat.AIFF,
                        'audio/x-aiff': AudioFormat.AIFF
                    }
                    format_from_mime = mime_mapping.get(mime_type)
                    if format_from_mime:
                        return format_from_mime
            except Exception:
                pass
            
            # Fallback to extension
            return format_from_ext
            
        except Exception as e:
            logger.warning(f"Format detection failed for {file_path}: {e}")
            return None
    
    @staticmethod
    def get_audio_specs(file_path: Path) -> Dict[str, Any]:
        """
        Get comprehensive audio file specifications
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with audio specifications
        """
        specs = {
            'format': None,
            'sample_rate': None,
            'channels': None,
            'duration': None,
            'bitrate': None,
            'bit_depth': None,
            'file_size': None,
            'codec': None,
            'metadata_available': False,
            'error': None
        }
        
        try:
            # Get file size
            if file_path.exists():
                specs['file_size'] = file_path.stat().st_size
            
            # Try mutagen first (comprehensive metadata)
            try:
                audio_file = mutagen.File(str(file_path))
                if audio_file and hasattr(audio_file, 'info'):
                    info = audio_file.info
                    specs['sample_rate'] = getattr(info, 'sample_rate', None)
                    specs['channels'] = getattr(info, 'channels', None)
                    specs['duration'] = getattr(info, 'length', None)
                    specs['bitrate'] = getattr(info, 'bitrate', None)
                    specs['bit_depth'] = getattr(info, 'bits_per_sample', None)
                    specs['metadata_available'] = bool(audio_file.tags)
                    
                    # Detect codec
                    codec_mapping = {
                        'MP3': 'mp3',
                        'FLAC': 'flac', 
                        'MP4': 'aac',
                        'OggVorbis': 'vorbis',
                        'WAVE': 'pcm',
                        'AIFF': 'pcm'
                    }
                    specs['codec'] = codec_mapping.get(type(audio_file).__name__)
            except Exception as e:
                specs['error'] = f"Mutagen failed: {e}"
            
            # Try soundfile if mutagen failed or incomplete
            if not specs['sample_rate']:
                try:
                    info = sf.info(str(file_path))
                    specs['sample_rate'] = info.samplerate
                    specs['channels'] = info.channels
                    specs['duration'] = info.frames / info.samplerate
                    specs['bit_depth'] = {
                        'PCM_16': 16,
                        'PCM_24': 24,
                        'PCM_32': 32,
                        'FLOAT': 32,
                        'DOUBLE': 64
                    }.get(info.subtype, None)
                except Exception as e:
                    if 'error' in specs:
                        specs['error'] += f"; Soundfile failed: {e}"
                    else:
                        specs['error'] = f"Soundfile failed: {e}"
            
            # Try librosa as last resort
            if not specs['sample_rate']:
                try:
                    y, sr = librosa.load(str(file_path), sr=None, duration=1.0)
                    specs['sample_rate'] = sr
                    specs['channels'] = 1 if len(y.shape) == 1 else y.shape[1]
                    
                    # Get full duration
                    duration = librosa.get_duration(filename=str(file_path))
                    specs['duration'] = duration
                except Exception as e:
                    if 'error' in specs:
                        specs['error'] += f"; Librosa failed: {e}"
                    else:
                        specs['error'] = f"Librosa failed: {e}"
            
            # Detect format
            specs['format'] = ConversionUtils.detect_audio_format(file_path)
            
            return specs
            
        except Exception as e:
            specs['error'] = f"Specification extraction failed: {e}"
            return specs
    
    @staticmethod
    def calculate_optimal_bitrate(audio_specs: Dict[str, Any], 
                                target_format: AudioFormat,
                                quality_preference: str = "high") -> int:
        """
        Calculate optimal bitrate for conversion
        
        Args:
            audio_specs: Source audio specifications
            target_format: Target format
            quality_preference: Quality preference (low, medium, high, extreme)
            
        Returns:
            Optimal bitrate in kbps
        """
        # Base bitrate recommendations by format and quality
        bitrate_table = {
            AudioFormat.MP3: {
                'low': 128,
                'medium': 192,
                'high': 256,
                'extreme': 320
            },
            AudioFormat.AAC: {
                'low': 96,
                'medium': 128,
                'high': 192,
                'extreme': 256
            },
            AudioFormat.OGG: {
                'low': 112,
                'medium': 160,
                'high': 224,
                'extreme': 320
            },
            AudioFormat.OPUS: {
                'low': 64,
                'medium': 96,
                'high': 128,
                'extreme': 192
            }
        }
        
        if target_format not in bitrate_table:
            return 192  # Default fallback
        
        base_bitrate = bitrate_table[target_format].get(quality_preference, 192)
        
        # Adjust based on source characteristics
        channels = audio_specs.get('channels', 2)
        sample_rate = audio_specs.get('sample_rate', 44100)
        source_bitrate = audio_specs.get('bitrate')
        
        # Channel adjustment
        if channels == 1:
            base_bitrate = int(base_bitrate * 0.7)  # Reduce for mono
        elif channels > 2:
            base_bitrate = int(base_bitrate * min(1.5, channels / 2))  # Increase for multichannel
        
        # Sample rate adjustment
        if sample_rate > 48000:
            base_bitrate = int(base_bitrate * 1.2)  # Increase for high sample rates
        elif sample_rate < 44100:
            base_bitrate = int(base_bitrate * 0.9)  # Reduce for low sample rates
        
        # Don't exceed source bitrate by more than 20% for lossy sources
        if source_bitrate and source_bitrate < 1000:  # Likely lossy source
            max_bitrate = int(source_bitrate * 1.2)
            base_bitrate = min(base_bitrate, max_bitrate)
        
        return base_bitrate
    
    @staticmethod 
    def estimate_conversion_complexity(source_specs: Dict[str, Any],
                                     target_format: AudioFormat,
                                     processing_options: Optional[Dict[str, Any]] = None) -> str:
        """
        Estimate conversion complexity level
        
        Args:
            source_specs: Source audio specifications
            target_format: Target format
            processing_options: Additional processing options
            
        Returns:
            Complexity level: 'low', 'medium', 'high', 'extreme'
        """
        complexity_score = 0
        
        # Base complexity by format conversion
        source_format = source_specs.get('format')
        
        # Same format = low complexity
        if source_format == target_format:
            complexity_score += 1
        
        # Lossless to lossless = medium
        elif (source_format in [AudioFormat.WAV, AudioFormat.FLAC, AudioFormat.AIFF] and
              target_format in [AudioFormat.WAV, AudioFormat.FLAC, AudioFormat.AIFF]):
            complexity_score += 2
        
        # Lossless to lossy = medium-high  
        elif (source_format in [AudioFormat.WAV, AudioFormat.FLAC, AudioFormat.AIFF] and
              target_format in [AudioFormat.MP3, AudioFormat.AAC, AudioFormat.OGG]):
            complexity_score += 3
        
        # Lossy to lossy = high (transcoding)
        elif (source_format in [AudioFormat.MP3, AudioFormat.AAC, AudioFormat.OGG] and
              target_format in [AudioFormat.MP3, AudioFormat.AAC, AudioFormat.OGG]):
            complexity_score += 4
        
        # Complex formats = high
        else:
            complexity_score += 4
        
        # Sample rate considerations
        sample_rate = source_specs.get('sample_rate', 44100)
        if sample_rate > 96000:
            complexity_score += 2
        elif sample_rate > 48000:
            complexity_score += 1
        
        # Channel considerations
        channels = source_specs.get('channels', 2)
        if channels > 8:
            complexity_score += 3
        elif channels > 2:
            complexity_score += 1
        
        # Duration considerations
        duration = source_specs.get('duration', 0)
        if duration > 3600:  # > 1 hour
            complexity_score += 2
        elif duration > 600:  # > 10 minutes
            complexity_score += 1
        
        # Processing options
        if processing_options:
            if processing_options.get('apply_reverb') or processing_options.get('apply_delay'):
                complexity_score += 2
            
            if processing_options.get('apply_compressor') or processing_options.get('apply_eq'):
                complexity_score += 1
            
            if processing_options.get('parallel_processing'):
                complexity_score += 1
        
        # Map score to complexity level
        if complexity_score <= 2:
            return 'low'
        elif complexity_score <= 4:
            return 'medium'
        elif complexity_score <= 7:
            return 'high'
        else:
            return 'extreme'
    
    @staticmethod
    def validate_conversion_compatibility(source_format: AudioFormat,
                                        target_format: AudioFormat,
                                        source_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate conversion compatibility and return warnings/recommendations
        
        Args:
            source_format: Source audio format
            target_format: Target audio format  
            source_specs: Source audio specifications
            
        Returns:
            Validation result with warnings and recommendations
        """
        validation = {
            'compatible': True,
            'quality_loss_expected': False,
            'warnings': [],
            'recommendations': [],
            'estimated_quality_retention': 1.0
        }
        
        # Format compatibility matrix
        lossy_formats = {AudioFormat.MP3, AudioFormat.AAC, AudioFormat.OGG, AudioFormat.OPUS, AudioFormat.WMA}
        lossless_formats = {AudioFormat.WAV, AudioFormat.FLAC, AudioFormat.AIFF}
        
        # Quality loss analysis
        if source_format in lossy_formats and target_format in lossy_formats:
            validation['quality_loss_expected'] = True
            validation['estimated_quality_retention'] = 0.85
            validation['warnings'].append("Converting between lossy formats will reduce quality")
            validation['recommendations'].append("Consider converting from original lossless source if available")
        
        elif source_format in lossless_formats and target_format in lossy_formats:
            validation['quality_loss_expected'] = True
            validation['estimated_quality_retention'] = 0.95
            validation['recommendations'].append("Choose highest quality settings for lossy encoding")
        
        # Sample rate compatibility
        sample_rate = source_specs.get('sample_rate')
        if sample_rate:
            if target_format == AudioFormat.MP3 and sample_rate > 48000:
                validation['warnings'].append("MP3 format may not support sample rates above 48kHz")
                validation['recommendations'].append("Consider resampling to 48kHz or using a different format")
            
            elif target_format in [AudioFormat.AAC, AudioFormat.M4A] and sample_rate > 96000:
                validation['warnings'].append("AAC format may have limited support for very high sample rates")
        
        # Channel compatibility
        channels = source_specs.get('channels', 2)
        if channels > 2:
            if target_format == AudioFormat.MP3:
                validation['warnings'].append("MP3 format only supports up to 2 channels (stereo)")
                validation['recommendations'].append("Consider using AAC or another format for multichannel audio")
            
            elif target_format == AudioFormat.OGG and channels > 8:
                validation['warnings'].append("OGG Vorbis may have limited support for more than 8 channels")
        
        # File size considerations
        file_size = source_specs.get('file_size')
        if file_size and file_size > 1024 * 1024 * 100:  # > 100MB
            if target_format in lossless_formats:
                validation['recommendations'].append("Large lossless files may benefit from compression (FLAC)")
            else:
                validation['recommendations'].append("Consider using variable bitrate encoding for large files")
        
        return validation


class FileUtils:
    """
    Professional File Handling Utilities
    
    Advanced file operations for audio conversion including secure file handling,
    atomic operations, and comprehensive file management.
    """
    
    @staticmethod
    def create_secure_temp_file(suffix: str = '.tmp', prefix: str = 'audio_conv_') -> Path:
        """
        Create secure temporary file with proper permissions
        
        Args:
            suffix: File suffix
            prefix: File prefix
            
        Returns:
            Path to created temporary file
        """
        try:
            fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
            os.close(fd)  # Close file descriptor immediately
            
            temp_file = Path(temp_path)
            
            # Set restrictive permissions (owner read/write only)
            temp_file.chmod(stat.S_IRUSR | stat.S_IWUSR)
            
            return temp_file
            
        except Exception as e:
            logger.error(f"Failed to create secure temp file: {e}")
            raise FileError(f"Temporary file creation failed: {e}")
    
    @staticmethod
    def atomic_move(source: Path, destination: Path, overwrite: bool = False) -> bool:
        """
        Perform atomic file move operation
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing destination
            
        Returns:
            Success status
        """
        try:
            # Check if destination exists
            if destination.exists() and not overwrite:
                raise FileError(f"Destination file exists: {destination}")
            
            # Ensure destination directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Perform atomic move
            if source.parent == destination.parent:
                # Same directory - simple rename
                source.rename(destination)
            else:
                # Cross-directory - copy then delete
                shutil.copy2(str(source), str(destination))
                source.unlink()
            
            logger.debug(f"Atomic move completed: {source} -> {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Atomic move failed: {e}")
            return False
    
    @staticmethod
    def safe_remove(file_path: Path, secure_delete: bool = False) -> bool:
        """
        Safely remove file with optional secure deletion
        
        Args:
            file_path: Path to file to remove
            secure_delete: Whether to perform secure deletion
            
        Returns:
            Success status
        """
        try:
            if not file_path.exists():
                return True
            
            if secure_delete:
                # Perform secure deletion by overwriting with random data
                file_size = file_path.stat().st_size
                
                with open(file_path, 'r+b') as f:
                    # Overwrite with random data (3 passes)
                    for _ in range(3):
                        f.seek(0)
                        f.write(os.urandom(file_size))
                        f.flush()
                        os.fsync(f.fileno())
            
            # Remove file
            file_path.unlink()
            logger.debug(f"File removed: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"File removal failed: {e}")
            return False
    
    @staticmethod
    def calculate_file_hash(file_path: Path, algorithm: str = 'sha256') -> str:
        """
        Calculate file hash for integrity verification
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm (sha256, md5, sha1)
            
        Returns:
            Hex digest of file hash
        """
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                # Read in chunks to handle large files
                chunk_size = 64 * 1024  # 64KB chunks
                while chunk := f.read(chunk_size):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"Hash calculation failed: {e}")
            raise FileError(f"File hash calculation failed: {e}")
    
    @staticmethod
    def verify_file_integrity(file_path: Path, expected_hash: str, algorithm: str = 'sha256') -> bool:
        """
        Verify file integrity using hash comparison
        
        Args:
            file_path: Path to file
            expected_hash: Expected hash value
            algorithm: Hash algorithm used
            
        Returns:
            True if file integrity is verified
        """
        try:
            actual_hash = FileUtils.calculate_file_hash(file_path, algorithm)
            return actual_hash.lower() == expected_hash.lower()
            
        except Exception as e:
            logger.error(f"Integrity verification failed: {e}")
            return False
    
    @staticmethod
    def get_available_space(directory: Path) -> int:
        """
        Get available disk space in bytes
        
        Args:
            directory: Directory to check
            
        Returns:
            Available space in bytes
        """
        try:
            stat_result = shutil.disk_usage(str(directory))
            return stat_result.free
            
        except Exception as e:
            logger.error(f"Failed to get disk space: {e}")
            return 0
    
    @staticmethod
    def ensure_sufficient_space(directory: Path, required_bytes: int, safety_margin: float = 0.1) -> bool:
        """
        Ensure sufficient disk space with safety margin
        
        Args:
            directory: Directory to check
            required_bytes: Required space in bytes
            safety_margin: Safety margin as fraction (0.1 = 10%)
            
        Returns:
            True if sufficient space available
        """
        try:
            available = FileUtils.get_available_space(directory)
            required_with_margin = int(required_bytes * (1 + safety_margin))
            
            if available >= required_with_margin:
                return True
            else:
                logger.warning(f"Insufficient disk space: need {required_with_margin}, have {available}")
                return False
                
        except Exception as e:
            logger.error(f"Space check failed: {e}")
            return False
    
    @staticmethod
    def backup_file(file_path: Path, backup_dir: Optional[Path] = None) -> Optional[Path]:
        """
        Create backup copy of file
        
        Args:
            file_path: Original file path
            backup_dir: Backup directory (defaults to same directory)
            
        Returns:
            Path to backup file or None if failed
        """
        try:
            if not file_path.exists():
                return None
            
            # Determine backup directory
            if backup_dir is None:
                backup_dir = file_path.parent
            else:
                backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
            backup_path = backup_dir / backup_name
            
            # Create backup
            shutil.copy2(str(file_path), str(backup_path))
            
            logger.info(f"Backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return None


class CompressionUtils:
    """
    Audio Compression Analysis Utilities
    
    Advanced compression analysis and optimization utilities for
    audio format conversion with intelligent parameter selection.
    """
    
    @staticmethod
    def analyze_compression_potential(audio_data: np.ndarray, 
                                    sample_rate: int) -> Dict[str, float]:
        """
        Analyze audio compression potential and characteristics
        
        Args:
            audio_data: Audio data array
            sample_rate: Sample rate
            
        Returns:
            Compression analysis results
        """
        analysis = {
            'dynamic_range': 0.0,
            'spectral_complexity': 0.0,
            'temporal_complexity': 0.0,
            'silence_ratio': 0.0,
            'compression_difficulty': 0.0,
            'recommended_formats': []
        }
        
        try:
            # Dynamic range analysis
            rms = np.sqrt(np.mean(audio_data ** 2))
            peak = np.max(np.abs(audio_data))
            
            if rms > 0:
                analysis['dynamic_range'] = 20 * np.log10(peak / rms)
            
            # Spectral complexity (using spectral centroid variation)
            if len(audio_data) > sample_rate:  # At least 1 second
                spectral_centroids = librosa.feature.spectral_centroid(
                    y=audio_data, sr=sample_rate
                )[0]
                analysis['spectral_complexity'] = float(np.std(spectral_centroids) / np.mean(spectral_centroids))
            
            # Temporal complexity (zero crossing rate variation)
            zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
            if len(zcr) > 0:
                analysis['temporal_complexity'] = float(np.std(zcr))
            
            # Silence detection
            silence_threshold = 0.01  # -40 dB
            silence_samples = np.sum(np.abs(audio_data) < silence_threshold)
            analysis['silence_ratio'] = silence_samples / len(audio_data)
            
            # Overall compression difficulty
            difficulty_score = (
                (analysis['dynamic_range'] / 60.0) * 0.4 +
                analysis['spectral_complexity'] * 0.3 +
                analysis['temporal_complexity'] * 0.2 +
                (1 - analysis['silence_ratio']) * 0.1
            )
            analysis['compression_difficulty'] = float(np.clip(difficulty_score, 0.0, 1.0))
            
            # Format recommendations based on analysis
            if analysis['compression_difficulty'] < 0.3:
                analysis['recommended_formats'] = ['mp3', 'aac', 'ogg']
            elif analysis['compression_difficulty'] < 0.6:
                analysis['recommended_formats'] = ['aac', 'ogg', 'opus']
            else:
                analysis['recommended_formats'] = ['flac', 'aac', 'opus']
            
            return analysis
            
        except Exception as e:
            logger.error(f"Compression analysis failed: {e}")
            return analysis
    
    @staticmethod
    def optimize_lossy_parameters(audio_data: np.ndarray,
                                sample_rate: int,
                                target_format: AudioFormat,
                                quality_target: float = 0.9) -> Dict[str, Any]:
        """
        Optimize lossy compression parameters based on audio analysis
        
        Args:
            audio_data: Audio data array
            sample_rate: Sample rate
            target_format: Target lossy format
            quality_target: Target quality (0.0-1.0)
            
        Returns:
            Optimized parameters
        """
        params = {}
        
        try:
            # Analyze compression characteristics
            compression_analysis = CompressionUtils.analyze_compression_potential(
                audio_data, sample_rate
            )
            
            difficulty = compression_analysis['compression_difficulty']
            dynamic_range = compression_analysis['dynamic_range']
            
            if target_format == AudioFormat.MP3:
                # MP3 optimization
                if quality_target >= 0.95:
                    params['quality'] = 0  # Highest VBR quality
                    params['bitrate_mode'] = 'vbr'
                elif quality_target >= 0.85:
                    params['quality'] = 2
                    params['bitrate_mode'] = 'vbr'
                else:
                    params['bitrate'] = 192 if difficulty > 0.6 else 128
                    params['bitrate_mode'] = 'cbr'
                
                # Joint stereo for lower bitrates
                params['joint_stereo'] = params.get('bitrate', 320) < 192
                
            elif target_format == AudioFormat.AAC:
                # AAC optimization
                if quality_target >= 0.95:
                    params['bitrate'] = 256
                    params['profile'] = 'aac_lc'
                elif quality_target >= 0.85:
                    params['bitrate'] = 192
                    params['profile'] = 'aac_lc'
                else:
                    params['bitrate'] = 128
                    params['profile'] = 'aac_he' if sample_rate <= 48000 else 'aac_lc'
                
                # Bandwidth optimization
                if dynamic_range > 40:
                    params['bandwidth'] = min(20000, sample_rate // 2)
                else:
                    params['bandwidth'] = min(16000, sample_rate // 2)
                
            elif target_format == AudioFormat.OGG:
                # OGG Vorbis optimization
                quality_map = {
                    0.95: 8,  # ~256 kbps
                    0.85: 6,  # ~192 kbps
                    0.75: 4,  # ~128 kbps
                    0.65: 2   # ~96 kbps
                }
                
                for threshold, quality in sorted(quality_map.items(), reverse=True):
                    if quality_target >= threshold:
                        params['quality'] = quality
                        break
                else:
                    params['quality'] = 1
                
                # Adjust for difficult material
                if difficulty > 0.7:
                    params['quality'] = min(10, params.get('quality', 4) + 2)
            
            elif target_format == AudioFormat.OPUS:
                # Opus optimization
                if quality_target >= 0.95:
                    params['bitrate'] = 192
                elif quality_target >= 0.85:
                    params['bitrate'] = 128
                else:
                    params['bitrate'] = 96
                
                # Application type
                if sample_rate <= 16000:
                    params['application'] = 'voip'
                elif dynamic_range > 30:
                    params['application'] = 'audio'
                else:
                    params['application'] = 'restricted_lowdelay'
            
            return params
            
        except Exception as e:
            logger.error(f"Parameter optimization failed: {e}")
            return {}
    
    @staticmethod
    def estimate_compression_ratio(source_specs: Dict[str, Any],
                                 target_format: AudioFormat,
                                 target_params: Dict[str, Any]) -> float:
        """
        Estimate compression ratio for given parameters
        
        Args:
            source_specs: Source audio specifications
            target_format: Target format
            target_params: Target compression parameters
            
        Returns:
            Estimated compression ratio (source_size / target_size)
        """
        try:
            # Get source file size or estimate
            source_size = source_specs.get('file_size')
            duration = source_specs.get('duration', 0)
            sample_rate = source_specs.get('sample_rate', 44100)
            channels = source_specs.get('channels', 2)
            bit_depth = source_specs.get('bit_depth', 16)
            
            if not source_size and duration > 0:
                # Estimate uncompressed size
                bytes_per_sample = bit_depth // 8
                source_size = int(duration * sample_rate * channels * bytes_per_sample)
            
            if not source_size:
                return 1.0
            
            # Estimate target file size based on format and parameters
            if target_format in [AudioFormat.MP3, AudioFormat.AAC, AudioFormat.OGG, AudioFormat.OPUS]:
                # Lossy formats - estimate from bitrate
                bitrate = target_params.get('bitrate')
                
                if not bitrate:
                    # Estimate bitrate from quality settings
                    if target_format == AudioFormat.MP3:
                        quality = target_params.get('quality', 4)
                        bitrate = {0: 245, 2: 190, 4: 165, 6: 130, 9: 85}.get(quality, 192)
                    elif target_format == AudioFormat.OGG:
                        quality = target_params.get('quality', 5)
                        bitrate = quality * 32  # Rough approximation
                    else:
                        bitrate = 192  # Default
                
                if duration > 0:
                    target_size = int((bitrate * 1000 * duration) / 8)
                    return source_size / target_size if target_size > 0 else 1.0
                
            elif target_format == AudioFormat.FLAC:
                # FLAC compression typically 40-60% of original
                compression_level = target_params.get('compression_level', 5)
                compression_ratio = 0.6 - (compression_level / 10 * 0.2)  # 0.4-0.6
                target_size = source_size * compression_ratio
                return source_size / target_size
                
            elif target_format in [AudioFormat.WAV, AudioFormat.AIFF]:
                # Uncompressed formats
                return 1.0
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Compression ratio estimation failed: {e}")
            return 1.0


class ValidationUtils:
    """
    Audio Validation Utilities
    
    Comprehensive validation functions for audio files, formats,
    and conversion parameters.
    """
    
    @staticmethod
    def validate_audio_file(file_path: Path) -> Dict[str, Any]:
        """
        Comprehensive audio file validation
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Validation results
        """
        validation = {
            'valid': False,
            'readable': False,
            'format_detected': False,
            'specifications_available': False,
            'metadata_readable': False,
            'issues': [],
            'warnings': [],
            'file_info': {}
        }
        
        try:
            # Basic file checks
            if not file_path.exists():
                validation['issues'].append("File does not exist")
                return validation
            
            if not file_path.is_file():
                validation['issues'].append("Path is not a file")
                return validation
            
            file_size = file_path.stat().st_size
            if file_size == 0:
                validation['issues'].append("File is empty")
                return validation
            
            validation['file_info']['size_bytes'] = file_size
            
            # Format detection
            detected_format = ConversionUtils.detect_audio_format(file_path)
            if detected_format:
                validation['format_detected'] = True
                validation['file_info']['format'] = detected_format.value
            else:
                validation['warnings'].append("Could not detect audio format")
            
            # Read test with multiple libraries
            read_success = False
            
            # Try mutagen
            try:
                audio_file = mutagen.File(str(file_path))
                if audio_file:
                    read_success = True
                    validation['metadata_readable'] = bool(audio_file.tags)
                    
                    if hasattr(audio_file, 'info'):
                        info = audio_file.info
                        validation['file_info'].update({
                            'duration': getattr(info, 'length', None),
                            'sample_rate': getattr(info, 'sample_rate', None),
                            'channels': getattr(info, 'channels', None),
                            'bitrate': getattr(info, 'bitrate', None)
                        })
                        validation['specifications_available'] = True
            except Exception as e:
                validation['warnings'].append(f"Mutagen read failed: {e}")
            
            # Try soundfile
            if not read_success:
                try:
                    info = sf.info(str(file_path))
                    read_success = True
                    validation['file_info'].update({
                        'duration': info.frames / info.samplerate,
                        'sample_rate': info.samplerate,
                        'channels': info.channels
                    })
                    validation['specifications_available'] = True
                except Exception as e:
                    validation['warnings'].append(f"Soundfile read failed: {e}")
            
            # Try librosa as last resort
            if not read_success:
                try:
                    y, sr = librosa.load(str(file_path), duration=1.0)
                    if len(y) > 0:
                        read_success = True
                        validation['file_info']['sample_rate'] = sr
                        validation['specifications_available'] = True
                except Exception as e:
                    validation['warnings'].append(f"Librosa read failed: {e}")
            
            validation['readable'] = read_success
            
            if not read_success:
                validation['issues'].append("File is not readable by any audio library")
            
            # Overall validation
            validation['valid'] = (
                validation['readable'] and 
                validation['format_detected'] and
                len(validation['issues']) == 0
            )
            
            return validation
            
        except Exception as e:
            validation['issues'].append(f"Validation failed: {e}")
            return validation
    
    @staticmethod
    def validate_conversion_parameters(source_specs: Dict[str, Any],
                                     format_spec: FormatSpecification,
                                     processing_options: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Validate conversion parameters and return any issues
        
        Args:
            source_specs: Source audio specifications
            format_spec: Target format specification
            processing_options: Processing options
            
        Returns:
            List of validation issues
        """
        issues = []
        
        try:
            # Format specification validation
            if format_spec.sample_rate <= 0:
                issues.append("Invalid sample rate in format specification")
            
            if format_spec.channels <= 0:
                issues.append("Invalid channel count in format specification")
            
            if format_spec.bit_depth <= 0:
                issues.append("Invalid bit depth in format specification")
            
            # Source compatibility checks
            source_sample_rate = source_specs.get('sample_rate')
            source_channels = source_specs.get('channels')
            
            # Sample rate compatibility
            if source_sample_rate and format_spec.sample_rate > source_sample_rate * 2:
                issues.append("Target sample rate is suspiciously high compared to source")
            
            # Channel compatibility
            if source_channels and format_spec.channels > source_channels:
                if format_spec.channels > 2 and source_channels <= 2:
                    issues.append("Cannot create true multichannel from stereo/mono source")
            
            # Format-specific validations
            if format_spec.format == AudioFormat.MP3:
                if format_spec.sample_rate > 48000:
                    issues.append("MP3 does not support sample rates above 48kHz")
                
                if format_spec.channels > 2:
                    issues.append("MP3 does not support more than 2 channels")
                
                if format_spec.bitrate and (format_spec.bitrate < 32 or format_spec.bitrate > 320):
                    issues.append("MP3 bitrate out of valid range (32-320 kbps)")
            
            elif format_spec.format == AudioFormat.FLAC:
                if format_spec.sample_rate > 655350:
                    issues.append("FLAC sample rate exceeds maximum (655.35 kHz)")
                
                if format_spec.bit_depth > 32:
                    issues.append("FLAC bit depth exceeds maximum (32 bits)")
            
            # Processing options validation
            if processing_options:
                target_level = processing_options.get('target_level', -3.0)
                if target_level > 0:
                    issues.append("Target normalization level should be negative (in dB)")
                
                highpass_freq = processing_options.get('highpass_frequency', 0)
                if highpass_freq > format_spec.sample_rate / 2:
                    issues.append("High-pass frequency exceeds Nyquist frequency")
                
                lowpass_freq = processing_options.get('lowpass_frequency', 22050)
                if lowpass_freq > format_spec.sample_rate / 2:
                    issues.append("Low-pass frequency exceeds Nyquist frequency")
            
            return issues
            
        except Exception as e:
            issues.append(f"Parameter validation failed: {e}")
            return issues


# Export utility classes
__all__ = [
    'ConversionUtils',
    'FileUtils',
    'CompressionUtils',
    'ValidationUtils'
]
