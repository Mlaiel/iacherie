"""
Audio Transformer - Professional audio processing for IA Influencer Agent Platform
===================================================================================

Advanced audio transformation, conversion, and enhancement capabilities
for creators' audio content workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
import os
import tempfile
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json
import time
import subprocess
import wave
import numpy as np

try:
    import librosa
    import soundfile as sf
    import essentia.standard as es
    from scipy import signal
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logging.warning("Audio processing libraries not available. Some features may be limited.")

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats."""
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    WMA = "wma"


class AudioQuality(Enum):
    """Audio quality presets."""
    LOW = "low"          # 128 kbps
    MEDIUM = "medium"    # 192 kbps
    HIGH = "high"        # 256 kbps
    LOSSLESS = "lossless"  # Original quality
    CUSTOM = "custom"    # Custom settings


class AudioCodec(Enum):
    """Audio codecs."""
    MP3_LAME = "libmp3lame"
    AAC = "aac"
    FLAC = "flac"
    VORBIS = "libvorbis"
    OPUS = "libopus"


@dataclass
class AudioSettings:
    """Audio processing settings."""
    format: AudioFormat = AudioFormat.MP3
    quality: AudioQuality = AudioQuality.HIGH
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    bitrate: Optional[int] = None
    codec: Optional[AudioCodec] = None
    normalize: bool = False
    noise_reduction: bool = False
    enhance_bass: bool = False
    enhance_treble: bool = False
    fade_in: float = 0.0
    fade_out: float = 0.0
    custom_filters: Optional[List[str]] = None


@dataclass
class AudioMetadata:
    """Audio file metadata."""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    track: Optional[int] = None
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    bitrate: Optional[int] = None
    format: Optional[str] = None
    codec: Optional[str] = None
    size: Optional[int] = None


class AudioTransformer:
    """
    Professional audio transformation engine for the IA Influencer Agent Platform.
    
    Provides advanced audio processing, conversion, and enhancement capabilities
    optimized for creator content workflows.
    """
    
    def __init__(
        self,
        enable_gpu: bool = True,
        config: Optional[Dict[str, Any]] = None,
        temp_dir: Optional[str] = None
    ):
        """
        Initialize audio transformer.
        
        Args:
            enable_gpu: Enable GPU acceleration if available
            config: Configuration options
            temp_dir: Temporary directory for processing
        """
        self.enable_gpu = enable_gpu
        self.config = config or {}
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "audio_transform"
        
        # Create temp directory
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Quality presets
        self.quality_presets = {
            AudioQuality.LOW: {"bitrate": 128, "sample_rate": 44100},
            AudioQuality.MEDIUM: {"bitrate": 192, "sample_rate": 44100},
            AudioQuality.HIGH: {"bitrate": 256, "sample_rate": 44100},
            AudioQuality.LOSSLESS: {"bitrate": None, "sample_rate": None}
        }
        
        # Codec mappings
        self.codec_mapping = {
            AudioFormat.MP3: AudioCodec.MP3_LAME,
            AudioFormat.AAC: AudioCodec.AAC,
            AudioFormat.FLAC: AudioCodec.FLAC,
            AudioFormat.OGG: AudioCodec.VORBIS,
        }
        
        # Check FFmpeg availability
        self.ffmpeg_available = self._check_ffmpeg()
        
        logger.info(f"AudioTransformer initialized (GPU: {enable_gpu}, FFmpeg: {self.ffmpeg_available})")
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available."""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("FFmpeg not found. Some audio features may be limited.")
            return False
    
    async def transform(self, request) -> Any:
        """
        Transform audio based on request configuration.
        
        Args:
            request: Transformation request with audio settings
            
        Returns:
            TransformationResult with processing metrics
        """
        start_time = time.time()
        
        try:
            # Parse request
            input_path = Path(request.input_path)
            settings = self._parse_audio_settings(request)
            
            # Generate output path
            output_path = self._generate_output_path(input_path, settings, request.output_path)
            
            # Get input metadata
            input_metadata = await self.get_metadata(str(input_path))
            input_size = input_path.stat().st_size
            
            # Perform transformation
            if settings.format == AudioFormat.FLAC or settings.quality == AudioQuality.LOSSLESS:
                result_path = await self._convert_lossless(input_path, output_path, settings)
            else:
                result_path = await self._convert_lossy(input_path, output_path, settings)
            
            # Apply enhancements if requested
            if request.enhance_quality:
                result_path = await self._enhance_audio(result_path, settings)
            
            # Get output metadata
            output_metadata = await self.get_metadata(str(result_path))
            output_size = result_path.stat().st_size
            
            # Calculate metrics
            compression_ratio = (input_size - output_size) / input_size if input_size > 0 else 0.0
            quality_score = await self._calculate_quality_score(str(input_path), str(result_path))
            
            return type('TransformationResult', (), {
                'success': True,
                'output_path': str(result_path),
                'input_size': input_size,
                'output_size': output_size,
                'compression_ratio': compression_ratio,
                'quality_score': quality_score,
                'metadata': {
                    'input': input_metadata.__dict__,
                    'output': output_metadata.__dict__,
                    'settings': settings.__dict__
                },
                'processing_time': time.time() - start_time
            })()
            
        except Exception as e:
            logger.error(f"Audio transformation failed: {str(e)}")
            return type('TransformationResult', (), {
                'success': False,
                'error_message': str(e),
                'processing_time': time.time() - start_time
            })()
    
    async def convert(
        self,
        input_path: str,
        output_path: str,
        format: Union[str, AudioFormat] = AudioFormat.MP3,
        quality: Union[str, AudioQuality] = AudioQuality.HIGH,
        **kwargs
    ) -> bool:
        """
        Convert audio file to specified format and quality.
        
        Args:
            input_path: Input audio file path
            output_path: Output audio file path
            format: Target audio format
            quality: Output quality level
            **kwargs: Additional settings
            
        Returns:
            Success status
        """
        settings = AudioSettings(
            format=format if isinstance(format, AudioFormat) else AudioFormat(format),
            quality=quality if isinstance(quality, AudioQuality) else AudioQuality(quality),
            **kwargs
        )
        
        try:
            input_file = Path(input_path)
            output_file = Path(output_path)
            
            if settings.quality == AudioQuality.LOSSLESS:
                await self._convert_lossless(input_file, output_file, settings)
            else:
                await self._convert_lossy(input_file, output_file, settings)
            
            return True
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {str(e)}")
            return False
    
    async def enhance(
        self,
        input_path: str,
        output_path: str,
        enhancement_options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Enhance audio quality using AI and signal processing.
        
        Args:
            input_path: Input audio file path
            output_path: Output audio file path
            enhancement_options: Enhancement configuration
            
        Returns:
            Success status
        """
        try:
            if not AUDIO_LIBS_AVAILABLE:
                logger.warning("Audio enhancement requires librosa and essentia")
                return False
            
            # Load audio
            audio, sr = librosa.load(input_path, sr=None)
            
            # Apply enhancements
            enhanced_audio = await self._apply_enhancements(audio, sr, enhancement_options or {})
            
            # Save enhanced audio
            sf.write(output_path, enhanced_audio, sr)
            
            return True
            
        except Exception as e:
            logger.error(f"Audio enhancement failed: {str(e)}")
            return False
    
    async def get_metadata(self, file_path: str) -> AudioMetadata:
        """
        Extract comprehensive audio metadata.
        
        Args:
            file_path: Audio file path
            
        Returns:
            AudioMetadata object
        """
        try:
            metadata = AudioMetadata()
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                return metadata
            
            metadata.size = file_path_obj.stat().st_size
            
            if AUDIO_LIBS_AVAILABLE:
                try:
                    # Use librosa for basic info
                    audio, sr = librosa.load(file_path, sr=None)
                    metadata.duration = len(audio) / sr
                    metadata.sample_rate = sr
                    metadata.channels = 1 if audio.ndim == 1 else audio.shape[0]
                    
                except Exception as e:
                    logger.warning(f"Could not extract metadata with librosa: {e}")
            
            # Try FFprobe for detailed metadata
            if self.ffmpeg_available:
                try:
                    result = subprocess.run([
                        "ffprobe", "-v", "quiet", "-print_format", "json",
                        "-show_format", "-show_streams", file_path
                    ], capture_output=True, text=True, check=True)
                    
                    probe_data = json.loads(result.stdout)
                    format_info = probe_data.get("format", {})
                    stream_info = probe_data.get("streams", [{}])[0]
                    
                    # Extract metadata
                    tags = format_info.get("tags", {})
                    metadata.title = tags.get("title")
                    metadata.artist = tags.get("artist") or tags.get("ARTIST")
                    metadata.album = tags.get("album") or tags.get("ALBUM")
                    metadata.genre = tags.get("genre") or tags.get("GENRE")
                    
                    if tags.get("date") or tags.get("DATE"):
                        try:
                            metadata.year = int((tags.get("date") or tags.get("DATE"))[:4])
                        except:
                            pass
                    
                    metadata.duration = float(format_info.get("duration", 0))
                    metadata.bitrate = int(format_info.get("bit_rate", 0))
                    metadata.format = format_info.get("format_name")
                    metadata.codec = stream_info.get("codec_name")
                    metadata.sample_rate = int(stream_info.get("sample_rate", 0))
                    metadata.channels = int(stream_info.get("channels", 0))
                    
                except Exception as e:
                    logger.warning(f"Could not extract metadata with ffprobe: {e}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return AudioMetadata()
    
    async def _convert_lossless(
        self,
        input_path: Path,
        output_path: Path,
        settings: AudioSettings
    ) -> Path:
        """Convert audio with lossless quality."""
        if not self.ffmpeg_available:
            raise RuntimeError("FFmpeg required for lossless conversion")
        
        cmd = [
            "ffmpeg", "-i", str(input_path),
            "-c:a", self.codec_mapping.get(settings.format, AudioCodec.FLAC).value,
            "-y", str(output_path)
        ]
        
        if settings.sample_rate:
            cmd.extend(["-ar", str(settings.sample_rate)])
        
        if settings.channels:
            cmd.extend(["-ac", str(settings.channels)])
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg conversion failed: {stderr.decode()}")
        
        return output_path
    
    async def _convert_lossy(
        self,
        input_path: Path,
        output_path: Path,
        settings: AudioSettings
    ) -> Path:
        """Convert audio with lossy compression."""
        if not self.ffmpeg_available:
            raise RuntimeError("FFmpeg required for audio conversion")
        
        # Get quality settings
        quality_settings = self.quality_presets.get(settings.quality, {})
        bitrate = settings.bitrate or quality_settings.get("bitrate", 192)
        sample_rate = settings.sample_rate or quality_settings.get("sample_rate", 44100)
        
        cmd = [
            "ffmpeg", "-i", str(input_path),
            "-c:a", self.codec_mapping.get(settings.format, AudioCodec.MP3_LAME).value,
            "-b:a", f"{bitrate}k",
            "-ar", str(sample_rate),
            "-y", str(output_path)
        ]
        
        if settings.channels:
            cmd.extend(["-ac", str(settings.channels)])
        
        # Add audio filters
        filters = []
        if settings.normalize:
            filters.append("loudnorm")
        
        if settings.fade_in > 0:
            filters.append(f"afade=t=in:ss=0:d={settings.fade_in}")
        
        if settings.fade_out > 0:
            filters.append(f"afade=t=out:st={settings.fade_out}")
        
        if settings.custom_filters:
            filters.extend(settings.custom_filters)
        
        if filters:
            cmd.extend(["-af", ",".join(filters)])
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg conversion failed: {stderr.decode()}")
        
        return output_path
    
    async def _enhance_audio(
        self,
        audio_path: Path,
        settings: AudioSettings
    ) -> Path:
        """Enhance audio quality using advanced processing."""
        if not AUDIO_LIBS_AVAILABLE:
            logger.warning("Audio enhancement requires additional libraries")
            return audio_path
        
        try:
            # Load audio
            audio, sr = librosa.load(str(audio_path), sr=None)
            
            # Apply enhancements
            enhanced_audio = await self._apply_enhancements(audio, sr, {
                'noise_reduction': settings.noise_reduction,
                'enhance_bass': settings.enhance_bass,
                'enhance_treble': settings.enhance_treble,
                'normalize': settings.normalize
            })
            
            # Create enhanced file path
            enhanced_path = audio_path.parent / f"{audio_path.stem}_enhanced{audio_path.suffix}"
            
            # Save enhanced audio
            sf.write(str(enhanced_path), enhanced_audio, sr)
            
            return enhanced_path
            
        except Exception as e:
            logger.error(f"Audio enhancement failed: {str(e)}")
            return audio_path
    
    async def _apply_enhancements(
        self,
        audio: np.ndarray,
        sample_rate: int,
        options: Dict[str, Any]
    ) -> np.ndarray:
        """Apply audio enhancements."""
        enhanced = audio.copy()
        
        try:
            # Noise reduction
            if options.get('noise_reduction', False):
                enhanced = self._reduce_noise(enhanced, sample_rate)
            
            # Bass enhancement
            if options.get('enhance_bass', False):
                enhanced = self._enhance_bass(enhanced, sample_rate)
            
            # Treble enhancement
            if options.get('enhance_treble', False):
                enhanced = self._enhance_treble(enhanced, sample_rate)
            
            # Normalization
            if options.get('normalize', False):
                enhanced = librosa.util.normalize(enhanced)
            
        except Exception as e:
            logger.error(f"Enhancement processing failed: {str(e)}")
            return audio
        
        return enhanced
    
    def _reduce_noise(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply noise reduction."""
        try:
            # Simple spectral gating approach
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            
            # Estimate noise floor
            noise_floor = np.percentile(magnitude, 10)
            
            # Apply soft gating
            gate_factor = 0.1
            mask = magnitude > noise_floor * (1 + gate_factor)
            
            # Apply mask with soft transitions
            filtered_stft = stft * mask
            
            return librosa.istft(filtered_stft)
            
        except Exception as e:
            logger.error(f"Noise reduction failed: {str(e)}")
            return audio
    
    def _enhance_bass(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Enhance bass frequencies."""
        try:
            # Low-shelf filter for bass enhancement
            from scipy.signal import butter, filtfilt
            
            nyquist = sample_rate / 2
            low_freq = 100 / nyquist  # 100 Hz cutoff
            
            b, a = butter(2, low_freq, btype='low')
            bass = filtfilt(b, a, audio)
            
            # Mix with original with emphasis
            return audio + 0.3 * bass
            
        except Exception as e:
            logger.error(f"Bass enhancement failed: {str(e)}")
            return audio
    
    def _enhance_treble(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Enhance treble frequencies."""
        try:
            # High-shelf filter for treble enhancement
            from scipy.signal import butter, filtfilt
            
            nyquist = sample_rate / 2
            high_freq = 5000 / nyquist  # 5 kHz cutoff
            
            b, a = butter(2, high_freq, btype='high')
            treble = filtfilt(b, a, audio)
            
            # Mix with original with emphasis
            return audio + 0.2 * treble
            
        except Exception as e:
            logger.error(f"Treble enhancement failed: {str(e)}")
            return audio
    
    async def _calculate_quality_score(self, input_path: str, output_path: str) -> Optional[float]:
        """Calculate audio quality score comparing input and output."""
        try:
            if not AUDIO_LIBS_AVAILABLE:
                return None
            
            # Load both files
            original, sr1 = librosa.load(input_path, sr=None)
            processed, sr2 = librosa.load(output_path, sr=None)
            
            # Resample if needed
            if sr1 != sr2:
                processed = librosa.resample(processed, orig_sr=sr2, target_sr=sr1)
            
            # Ensure same length
            min_len = min(len(original), len(processed))
            original = original[:min_len]
            processed = processed[:min_len]
            
            # Calculate similarity metrics
            correlation = np.corrcoef(original, processed)[0, 1]
            
            # Calculate spectral similarity
            stft_orig = np.abs(librosa.stft(original))
            stft_proc = np.abs(librosa.stft(processed))
            
            spectral_similarity = np.mean(
                1 - np.abs(stft_orig - stft_proc) / (stft_orig + stft_proc + 1e-8)
            )
            
            # Combined quality score
            quality_score = (correlation * 0.6 + spectral_similarity * 0.4) * 100
            
            return max(0.0, min(100.0, quality_score))
            
        except Exception as e:
            logger.error(f"Quality score calculation failed: {str(e)}")
            return None
    
    def _parse_audio_settings(self, request) -> AudioSettings:
        """Parse transformation request into audio settings."""
        settings = AudioSettings()
        
        if hasattr(request, 'target_format') and request.target_format:
            settings.format = AudioFormat(request.target_format)
        
        if hasattr(request, 'quality') and request.quality:
            if hasattr(request.quality, 'value'):
                settings.quality = AudioQuality(request.quality.value)
            else:
                settings.quality = AudioQuality(request.quality)
        
        if hasattr(request, 'options') and request.options:
            options = request.options
            settings.sample_rate = options.get('sample_rate')
            settings.channels = options.get('channels')
            settings.bitrate = options.get('bitrate')
            settings.normalize = options.get('normalize', False)
            settings.noise_reduction = options.get('noise_reduction', False)
            settings.enhance_bass = options.get('enhance_bass', False)
            settings.enhance_treble = options.get('enhance_treble', False)
            settings.fade_in = options.get('fade_in', 0.0)
            settings.fade_out = options.get('fade_out', 0.0)
            settings.custom_filters = options.get('custom_filters')
        
        return settings
    
    def _generate_output_path(
        self,
        input_path: Path,
        settings: AudioSettings,
        requested_output: Optional[str] = None
    ) -> Path:
        """Generate output file path."""
        if requested_output:
            return Path(requested_output)
        
        # Generate based on input and settings
        output_name = f"{input_path.stem}_{settings.quality.value}.{settings.format.value}"
        return input_path.parent / output_name
    
    async def cleanup(self):
        """Cleanup temporary files and resources."""
        try:
            # Clean temp directory
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            logger.info("AudioTransformer cleanup completed")
            
        except Exception as e:
            logger.error(f"AudioTransformer cleanup failed: {str(e)}")


class AudioConverter:
    """Simplified audio converter interface."""
    
    def __init__(self, transformer: Optional[AudioTransformer] = None):
        self.transformer = transformer or AudioTransformer()
    
    async def convert(
        self,
        input_path: str,
        output_path: str,
        format: str = "mp3",
        quality: str = "high"
    ) -> bool:
        """Convert audio file."""
        return await self.transformer.convert(input_path, output_path, format, quality)


class AudioEnhancer:
    """Simplified audio enhancer interface."""
    
    def __init__(self, transformer: Optional[AudioTransformer] = None):
        self.transformer = transformer or AudioTransformer()
    
    async def enhance(
        self,
        input_path: str,
        output_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Enhance audio quality."""
        return await self.transformer.enhance(input_path, output_path, options)
