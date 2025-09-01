"""🔄 Audio Format Conversion Module - Professional Multi-Format Engine

Advanced format conversion and quality optimization for the IA Influencer Agent platform.
Supports all major audio formats with quality preservation and optimization.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path
import numpy as np
import soundfile as sf
import librosa
from scipy import signal
from dataclasses import dataclass
from enum import Enum
import subprocess
import tempfile
import shutil

from .core import AudioProcessor, AudioMetadata
from .config import AudioProcessingConfig

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    AIFF = "aiff"
    WMA = "wma"


class QualityLevel(Enum):
    """Audio quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    LOSSLESS = "lossless"
    CUSTOM = "custom"


@dataclass
class ConversionSettings:
    """Audio conversion settings"""
    target_format: AudioFormat
    quality_level: QualityLevel = QualityLevel.HIGH
    sample_rate: Optional[int] = None
    bit_depth: Optional[int] = None
    bitrate: Optional[int] = None
    channels: Optional[int] = None
    normalize: bool = True
    apply_dithering: bool = True
    custom_parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_parameters is None:
            self.custom_parameters = {}


@dataclass
class ConversionResult:
    """Conversion operation result"""
    success: bool
    output_path: Optional[Path] = None
    original_size: Optional[int] = None
    converted_size: Optional[int] = None
    compression_ratio: Optional[float] = None
    quality_metrics: Dict[str, float] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None


class FormatConverter:
    """
    🔄 Professional Audio Format Converter
    
    Advanced multi-format conversion engine featuring:
    - Support for all major audio formats
    - Quality-preserving conversion algorithms
    - Batch processing capabilities
    - Automatic quality optimization
    - Lossless conversion when possible
    """
    
    def __init__(self, 
                 config: Optional[AudioProcessingConfig] = None,
                 ffmpeg_path: Optional[str] = None):
        self.config = config or AudioProcessingConfig()
        self.audio_processor = AudioProcessor(config)
        self.ffmpeg_path = ffmpeg_path or "ffmpeg"
        
        # Quality presets
        self.quality_presets = self._init_quality_presets()
        
        # Check for external tools
        self._check_external_tools()
        
        logger.info("FormatConverter initialized")
    
    def _init_quality_presets(self) -> Dict[QualityLevel, Dict[AudioFormat, Dict[str, Any]]]:
        """Initialize quality presets for different formats"""
        return {
            QualityLevel.LOW: {
                AudioFormat.MP3: {"bitrate": 128, "quality": "5"},
                AudioFormat.AAC: {"bitrate": 128, "quality": "5"},
                AudioFormat.OGG: {"bitrate": 128, "quality": "3"},
                AudioFormat.WAV: {"bit_depth": 16},
                AudioFormat.FLAC: {"compression_level": 8}
            },
            QualityLevel.MEDIUM: {
                AudioFormat.MP3: {"bitrate": 192, "quality": "2"},
                AudioFormat.AAC: {"bitrate": 192, "quality": "2"},
                AudioFormat.OGG: {"bitrate": 192, "quality": "5"},
                AudioFormat.WAV: {"bit_depth": 16},
                AudioFormat.FLAC: {"compression_level": 5}
            },
            QualityLevel.HIGH: {
                AudioFormat.MP3: {"bitrate": 320, "quality": "0"},
                AudioFormat.AAC: {"bitrate": 320, "quality": "0"},
                AudioFormat.OGG: {"bitrate": 320, "quality": "8"},
                AudioFormat.WAV: {"bit_depth": 24},
                AudioFormat.FLAC: {"compression_level": 3}
            },
            QualityLevel.LOSSLESS: {
                AudioFormat.FLAC: {"compression_level": 0},
                AudioFormat.WAV: {"bit_depth": 24},
                AudioFormat.AIFF: {"bit_depth": 24}
            }
        }
    
    def _check_external_tools(self):
        """Check availability of external conversion tools"""
        try:
            # Check FFmpeg
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                self.has_ffmpeg = True
                logger.info("FFmpeg available for format conversion")
            else:
                self.has_ffmpeg = False
                logger.warning("FFmpeg not available - limited format support")
                
        except Exception as e:
            self.has_ffmpeg = False
            logger.warning(f"FFmpeg check failed: {e}")
    
    async def convert_audio(self,
                          input_path: Union[str, Path],
                          output_path: Union[str, Path],
                          settings: ConversionSettings) -> ConversionResult:
        """
        Convert audio file to target format
        
        Args:
            input_path: Path to input audio file
            output_path: Path for output file
            settings: Conversion settings
            
        Returns:
            ConversionResult with operation details
        """
        import time
        start_time = time.time()
        
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            # Validate input file
            if not input_path.exists():
                return ConversionResult(
                    success=False,
                    error_message=f"Input file not found: {input_path}"
                )
            
            # Get original file size
            original_size = input_path.stat().st_size
            
            # Load audio data
            audio_data, sample_rate = await self.audio_processor.load_audio(
                input_path,
                target_sr=settings.sample_rate,
                mono=(settings.channels == 1) if settings.channels else False,
                normalize=settings.normalize
            )
            
            # Apply quality optimizations
            if settings.quality_level != QualityLevel.CUSTOM:
                audio_data = await self._apply_quality_optimizations(
                    audio_data, sample_rate, settings
                )
            
            # Convert format
            success = await self._perform_conversion(
                audio_data, sample_rate, output_path, settings
            )
            
            if not success:
                return ConversionResult(
                    success=False,
                    error_message="Conversion failed"
                )
            
            # Calculate metrics
            converted_size = output_path.stat().st_size if output_path.exists() else None
            compression_ratio = (
                original_size / converted_size if converted_size else None
            )
            
            processing_time = time.time() - start_time
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                input_path, output_path
            )
            
            return ConversionResult(
                success=True,
                output_path=output_path,
                original_size=original_size,
                converted_size=converted_size,
                compression_ratio=compression_ratio,
                quality_metrics=quality_metrics,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            return ConversionResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    async def _apply_quality_optimizations(self,
                                         audio_data: np.ndarray,
                                         sample_rate: int,
                                         settings: ConversionSettings) -> np.ndarray:
        """Apply quality-based audio optimizations"""
        try:
            optimized = audio_data.copy()
            
            # Apply dithering for bit depth reduction
            if settings.apply_dithering and settings.bit_depth:
                optimized = await self._apply_dithering(
                    optimized, target_bits=settings.bit_depth
                )
            
            # Apply anti-aliasing filter before downsampling
            if settings.sample_rate and settings.sample_rate < sample_rate:
                optimized = await self._apply_anti_aliasing_filter(
                    optimized, sample_rate, settings.sample_rate
                )
            
            # Apply format-specific optimizations
            if settings.target_format in [AudioFormat.MP3, AudioFormat.AAC, AudioFormat.OGG]:
                optimized = await self._optimize_for_lossy_compression(optimized)
            
            return optimized
            
        except Exception as e:
            logger.error(f"Quality optimization failed: {e}")
            return audio_data
    
    async def _apply_dithering(self, 
                             audio_data: np.ndarray, 
                             target_bits: int) -> np.ndarray:
        """Apply dithering for bit depth reduction"""
        try:
            if target_bits >= 24:
                return audio_data  # No dithering needed
            
            # Calculate quantization noise level
            quantization_noise_level = 1.0 / (2 ** target_bits)
            
            # Generate triangular dither noise
            dither_noise = np.random.triangular(
                -quantization_noise_level,
                0,
                quantization_noise_level,
                size=audio_data.shape
            )
            
            # Add dither and quantize
            dithered = audio_data + dither_noise
            
            # Quantize to target bit depth
            max_value = 2 ** (target_bits - 1) - 1
            quantized = np.round(dithered * max_value) / max_value
            
            return np.clip(quantized, -1.0, 1.0)
            
        except Exception as e:
            logger.error(f"Dithering failed: {e}")
            return audio_data
    
    async def _apply_anti_aliasing_filter(self,
                                        audio_data: np.ndarray,
                                        original_sr: int,
                                        target_sr: int) -> np.ndarray:
        """Apply anti-aliasing filter before downsampling"""
        try:
            # Design low-pass filter with cutoff at Nyquist of target sample rate
            nyquist = original_sr / 2
            cutoff = (target_sr / 2) * 0.95  # 95% of target Nyquist
            
            # Design Butterworth filter
            order = 6  # Higher order for better stopband attenuation
            b, a = signal.butter(order, cutoff / nyquist, btype='low')
            
            # Apply filter
            filtered = signal.filtfilt(b, a, audio_data)
            
            return filtered
            
        except Exception as e:
            logger.error(f"Anti-aliasing filter failed: {e}")
            return audio_data
    
    async def _optimize_for_lossy_compression(self, audio_data: np.ndarray) -> np.ndarray:
        """Optimize audio for lossy compression formats"""
        try:
            # Apply subtle pre-emphasis to improve perceptual quality
            # This helps preserve high-frequency content in lossy compression
            pre_emphasis_factor = 0.97
            
            if len(audio_data) > 1:
                pre_emphasized = np.zeros_like(audio_data)
                pre_emphasized[0] = audio_data[0]
                pre_emphasized[1:] = (
                    audio_data[1:] - pre_emphasis_factor * audio_data[:-1]
                )
                
                return pre_emphasized
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Lossy compression optimization failed: {e}")
            return audio_data
    
    async def _perform_conversion(self,
                                audio_data: np.ndarray,
                                sample_rate: int,
                                output_path: Path,
                                settings: ConversionSettings) -> bool:
        """Perform the actual format conversion"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            target_format = settings.target_format
            
            # Get format-specific parameters
            format_params = self._get_format_parameters(settings)
            
            if target_format in [AudioFormat.WAV, AudioFormat.AIFF]:
                # Direct conversion for uncompressed formats
                return await self._convert_to_uncompressed(
                    audio_data, sample_rate, output_path, format_params
                )
            
            elif target_format == AudioFormat.FLAC:
                # FLAC conversion
                return await self._convert_to_flac(
                    audio_data, sample_rate, output_path, format_params
                )
            
            elif self.has_ffmpeg and target_format in [
                AudioFormat.MP3, AudioFormat.AAC, AudioFormat.OGG, AudioFormat.M4A
            ]:
                # Use FFmpeg for compressed formats
                return await self._convert_with_ffmpeg(
                    audio_data, sample_rate, output_path, settings, format_params
                )
            
            else:
                # Fallback to basic conversion
                return await self._convert_basic(
                    audio_data, sample_rate, output_path, target_format
                )
                
        except Exception as e:
            logger.error(f"Format conversion failed: {e}")
            return False
    
    def _get_format_parameters(self, settings: ConversionSettings) -> Dict[str, Any]:
        """Get format-specific parameters from settings"""
        format_params = {}
        
        # Get preset parameters
        if settings.quality_level in self.quality_presets:
            preset = self.quality_presets[settings.quality_level]
            if settings.target_format in preset:
                format_params.update(preset[settings.target_format])
        
        # Override with custom parameters
        if settings.custom_parameters:
            format_params.update(settings.custom_parameters)
        
        # Override with specific settings
        if settings.bitrate:
            format_params['bitrate'] = settings.bitrate
        if settings.bit_depth:
            format_params['bit_depth'] = settings.bit_depth
        
        return format_params
    
    async def _convert_to_uncompressed(self,
                                     audio_data: np.ndarray,
                                     sample_rate: int,
                                     output_path: Path,
                                     format_params: Dict[str, Any]) -> bool:
        """Convert to uncompressed formats (WAV, AIFF)"""
        try:
            bit_depth = format_params.get('bit_depth', 16)
            
            # Determine subtype
            if bit_depth == 16:
                subtype = 'PCM_16'
            elif bit_depth == 24:
                subtype = 'PCM_24'
            elif bit_depth == 32:
                subtype = 'PCM_32'
            else:
                subtype = 'PCM_16'  # Default
            
            # Write file
            sf.write(
                str(output_path),
                audio_data,
                sample_rate,
                subtype=subtype
            )
            
            logger.debug(f"Converted to {output_path.suffix.upper()} with {bit_depth}-bit depth")
            return True
            
        except Exception as e:
            logger.error(f"Uncompressed conversion failed: {e}")
            return False
    
    async def _convert_to_flac(self,
                             audio_data: np.ndarray,
                             sample_rate: int,
                             output_path: Path,
                             format_params: Dict[str, Any]) -> bool:
        """Convert to FLAC format"""
        try:
            # FLAC conversion using soundfile
            sf.write(
                str(output_path),
                audio_data,
                sample_rate,
                format='FLAC',
                subtype='PCM_24'  # FLAC supports up to 24-bit
            )
            
            logger.debug(f"Converted to FLAC")
            return True
            
        except Exception as e:
            logger.error(f"FLAC conversion failed: {e}")
            return False
    
    async def _convert_with_ffmpeg(self,
                                 audio_data: np.ndarray,
                                 sample_rate: int,
                                 output_path: Path,
                                 settings: ConversionSettings,
                                 format_params: Dict[str, Any]) -> bool:
        """Convert using FFmpeg for compressed formats"""
        try:
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                temp_wav_path = Path(temp_wav.name)
            
            try:
                # Write temporary WAV
                sf.write(str(temp_wav_path), audio_data, sample_rate)
                
                # Build FFmpeg command
                cmd = [self.ffmpeg_path, '-i', str(temp_wav_path)]
                
                # Add format-specific options
                if settings.target_format == AudioFormat.MP3:
                    cmd.extend(['-codec:a', 'libmp3lame'])
                    if 'bitrate' in format_params:
                        cmd.extend(['-b:a', f"{format_params['bitrate']}k"])
                    if 'quality' in format_params:
                        cmd.extend(['-q:a', str(format_params['quality'])])
                
                elif settings.target_format == AudioFormat.AAC:
                    cmd.extend(['-codec:a', 'aac'])
                    if 'bitrate' in format_params:
                        cmd.extend(['-b:a', f"{format_params['bitrate']}k"])
                
                elif settings.target_format == AudioFormat.OGG:
                    cmd.extend(['-codec:a', 'libvorbis'])
                    if 'bitrate' in format_params:
                        cmd.extend(['-b:a', f"{format_params['bitrate']}k"])
                    if 'quality' in format_params:
                        cmd.extend(['-q:a', str(format_params['quality'])])
                
                # Add sample rate if specified
                if settings.sample_rate:
                    cmd.extend(['-ar', str(settings.sample_rate)])
                
                # Add channel configuration
                if settings.channels:
                    cmd.extend(['-ac', str(settings.channels)])
                
                # Output file
                cmd.extend(['-y', str(output_path)])  # -y to overwrite
                
                # Execute FFmpeg
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    logger.debug(f"FFmpeg conversion successful: {settings.target_format.value}")
                    return True
                else:
                    logger.error(f"FFmpeg conversion failed: {result.stderr}")
                    return False
                
            finally:
                # Clean up temporary file
                if temp_wav_path.exists():
                    temp_wav_path.unlink()
                    
        except Exception as e:
            logger.error(f"FFmpeg conversion failed: {e}")
            return False
    
    async def _convert_basic(self,
                           audio_data: np.ndarray,
                           sample_rate: int,
                           output_path: Path,
                           target_format: AudioFormat) -> bool:
        """Basic conversion fallback"""
        try:
            # Use soundfile for basic conversion
            format_map = {
                AudioFormat.WAV: 'WAV',
                AudioFormat.FLAC: 'FLAC',
                AudioFormat.AIFF: 'AIFF',
                AudioFormat.OGG: 'OGG'
            }
            
            sf_format = format_map.get(target_format)
            if sf_format:
                sf.write(
                    str(output_path),
                    audio_data,
                    sample_rate,
                    format=sf_format
                )
                return True
            else:
                logger.error(f"Unsupported format for basic conversion: {target_format}")
                return False
                
        except Exception as e:
            logger.error(f"Basic conversion failed: {e}")
            return False
    
    async def _calculate_quality_metrics(self,
                                       input_path: Path,
                                       output_path: Path) -> Dict[str, float]:
        """Calculate quality metrics by comparing input and output"""
        try:
            metrics = {}
            
            # Load both files
            original, sr1 = librosa.load(str(input_path), sr=None)
            converted, sr2 = librosa.load(str(output_path), sr=None)
            
            # Ensure same sample rate for comparison
            if sr1 != sr2:
                converted = librosa.resample(converted, orig_sr=sr2, target_sr=sr1)
            
            # Ensure same length
            min_length = min(len(original), len(converted))
            original = original[:min_length]
            converted = converted[:min_length]
            
            # Calculate SNR
            noise = original - converted
            signal_power = np.mean(original ** 2)
            noise_power = np.mean(noise ** 2)
            
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
                metrics['snr_db'] = float(snr)
            
            # Calculate THD+N (simplified)
            if signal_power > 0:
                thd_n = np.sqrt(noise_power / signal_power) * 100
                metrics['thd_n_percent'] = float(thd_n)
            
            # Calculate correlation
            correlation = np.corrcoef(original, converted)[0, 1]
            metrics['correlation'] = float(correlation)
            
            # Calculate PESQ-like metric (simplified)
            mse = np.mean((original - converted) ** 2)
            if mse > 0:
                psnr = 20 * np.log10(1.0 / np.sqrt(mse))
                metrics['psnr_db'] = float(psnr)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Quality metrics calculation failed: {e}")
            return {}
    
    async def batch_convert(self,
                          input_files: List[Path],
                          output_directory: Path,
                          settings: ConversionSettings,
                          preserve_structure: bool = True) -> List[ConversionResult]:
        """Convert multiple files in batch"""
        try:
            results = []
            output_directory.mkdir(parents=True, exist_ok=True)
            
            for input_file in input_files:
                # Determine output filename
                if preserve_structure:
                    relative_path = input_file.relative_to(
                        input_file.parent.parent if input_file.parent.parent.exists() 
                        else input_file.parent
                    )
                    output_path = output_directory / relative_path.with_suffix(
                        f'.{settings.target_format.value}'
                    )
                else:
                    output_path = output_directory / f"{input_file.stem}.{settings.target_format.value}"
                
                # Create output directory if needed
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Convert file
                result = await self.convert_audio(input_file, output_path, settings)
                results.append(result)
                
                # Log progress
                if result.success:
                    logger.info(f"Converted: {input_file.name} -> {output_path.name}")
                else:
                    logger.error(f"Failed to convert: {input_file.name} - {result.error_message}")
            
            successful = sum(1 for r in results if r.success)
            logger.info(f"Batch conversion completed: {successful}/{len(results)} successful")
            
            return results
            
        except Exception as e:
            logger.error(f"Batch conversion failed: {e}")
            return []


class QualityOptimizer:
    """
    ⚡ Advanced Audio Quality Optimizer
    
    Intelligent quality optimization system:
    - Automatic quality assessment
    - Format-specific optimizations
    - Bitrate recommendations
    - Quality vs. size optimization
    - Perceptual quality enhancement
    """
    
    def __init__(self, config: Optional[AudioProcessingConfig] = None):
        self.config = config or AudioProcessingConfig()
        self.audio_processor = AudioProcessor(config)
        
        logger.info("QualityOptimizer initialized")
    
    async def optimize_quality_settings(self,
                                      audio_data: np.ndarray,
                                      sample_rate: int,
                                      target_format: AudioFormat,
                                      target_size_mb: Optional[float] = None,
                                      min_quality_score: float = 0.8) -> ConversionSettings:
        """
        Automatically optimize conversion settings for best quality
        
        Args:
            audio_data: Input audio samples
            sample_rate: Sample rate
            target_format: Target audio format
            target_size_mb: Target file size in MB (optional)
            min_quality_score: Minimum acceptable quality score
            
        Returns:
            Optimized conversion settings
        """
        try:
            # Analyze audio characteristics
            audio_analysis = await self._analyze_audio_characteristics(
                audio_data, sample_rate
            )
            
            # Determine optimal settings based on analysis
            settings = ConversionSettings(target_format=target_format)
            
            # Optimize sample rate
            settings.sample_rate = self._optimize_sample_rate(
                sample_rate, audio_analysis
            )
            
            # Optimize bit depth
            settings.bit_depth = self._optimize_bit_depth(
                target_format, audio_analysis
            )
            
            # Optimize bitrate for lossy formats
            if target_format in [AudioFormat.MP3, AudioFormat.AAC, AudioFormat.OGG]:
                settings.bitrate = await self._optimize_bitrate(
                    audio_data, sample_rate, target_format, 
                    target_size_mb, min_quality_score
                )
                settings.quality_level = QualityLevel.CUSTOM
            
            # Set quality level for lossless formats
            elif target_format in [AudioFormat.FLAC, AudioFormat.WAV]:
                settings.quality_level = QualityLevel.LOSSLESS
            
            logger.info(f"Optimized settings for {target_format.value}: "
                       f"SR={settings.sample_rate}, BD={settings.bit_depth}, "
                       f"BR={settings.bitrate}")
            
            return settings
            
        except Exception as e:
            logger.error(f"Quality optimization failed: {e}")
            # Return default high-quality settings
            return ConversionSettings(
                target_format=target_format,
                quality_level=QualityLevel.HIGH
            )
    
    async def _analyze_audio_characteristics(self,
                                           audio_data: np.ndarray,
                                           sample_rate: int) -> Dict[str, Any]:
        """Analyze audio characteristics for optimization"""
        try:
            analysis = {}
            
            # Spectral analysis
            stft = librosa.stft(audio_data, hop_length=1024)
            magnitude = np.abs(stft)
            
            # Bandwidth analysis
            freqs = librosa.fft_frequencies(sr=sample_rate)
            spectral_energy = np.mean(magnitude, axis=1)
            
            # Find effective bandwidth (frequency below which 95% of energy is contained)
            cumulative_energy = np.cumsum(spectral_energy)
            total_energy = cumulative_energy[-1]
            bandwidth_idx = np.where(cumulative_energy >= 0.95 * total_energy)[0]
            
            if len(bandwidth_idx) > 0:
                effective_bandwidth = freqs[bandwidth_idx[0]]
            else:
                effective_bandwidth = sample_rate / 2
            
            analysis['effective_bandwidth'] = effective_bandwidth
            
            # Dynamic range
            analysis['dynamic_range'] = 20 * np.log10(
                np.percentile(np.abs(audio_data), 99) / 
                (np.percentile(np.abs(audio_data), 1) + 1e-10)
            )
            
            # Peak level
            analysis['peak_level'] = 20 * np.log10(np.max(np.abs(audio_data)) + 1e-10)
            
            # RMS level
            analysis['rms_level'] = 20 * np.log10(np.sqrt(np.mean(audio_data ** 2)) + 1e-10)
            
            # Spectral centroid (brightness)
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(
                y=audio_data, sr=sample_rate
            ))
            analysis['spectral_centroid'] = spectral_centroid
            
            # Zero crossing rate (indication of noisiness)
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio_data))
            analysis['zero_crossing_rate'] = zcr
            
            return analysis
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {}
    
    def _optimize_sample_rate(self,
                             original_sr: int,
                             analysis: Dict[str, Any]) -> int:
        """Optimize sample rate based on audio characteristics"""
        try:
            effective_bandwidth = analysis.get('effective_bandwidth', original_sr / 2)
            
            # Rule-based sample rate optimization
            if effective_bandwidth <= 8000:  # Telephone quality
                return 16000
            elif effective_bandwidth <= 11000:  # AM radio quality
                return 22050
            elif effective_bandwidth <= 15000:  # FM radio quality
                return 32000
            elif effective_bandwidth <= 20000:  # CD quality threshold
                return 44100
            else:  # High-resolution audio
                return max(48000, original_sr)
                
        except Exception:
            return original_sr
    
    def _optimize_bit_depth(self,
                          target_format: AudioFormat,
                          analysis: Dict[str, Any]) -> int:
        """Optimize bit depth based on dynamic range and format"""
        try:
            dynamic_range = analysis.get('dynamic_range', 96)  # Default to 16-bit range
            
            if target_format in [AudioFormat.WAV, AudioFormat.FLAC, AudioFormat.AIFF]:
                # Lossless formats - choose based on dynamic range
                if dynamic_range > 120:  # > 20-bit range
                    return 24
                elif dynamic_range > 96:  # > 16-bit range
                    return 20
                else:
                    return 16
            else:
                # Lossy formats - 16-bit is usually sufficient
                return 16
                
        except Exception:
            return 16  # Safe default
    
    async def _optimize_bitrate(self,
                              audio_data: np.ndarray,
                              sample_rate: int,
                              target_format: AudioFormat,
                              target_size_mb: Optional[float],
                              min_quality_score: float) -> int:
        """Optimize bitrate for lossy formats"""
        try:
            duration = len(audio_data) / sample_rate
            
            # If target size is specified, calculate required bitrate
            if target_size_mb:
                target_bits = target_size_mb * 8 * 1024 * 1024
                required_bitrate = int(target_bits / duration / 1000)  # kbps
                
                # Clamp to reasonable range
                min_bitrate = 64  # Minimum quality
                max_bitrate = 320  # Maximum for most formats
                
                return max(min_bitrate, min(max_bitrate, required_bitrate))
            
            # Otherwise, choose based on audio characteristics
            # This is a simplified approach - real optimization would use psychoacoustic models
            
            if target_format == AudioFormat.MP3:
                # MP3 bitrate recommendations
                if sample_rate >= 44100:
                    return 320  # High quality
                elif sample_rate >= 32000:
                    return 256
                else:
                    return 192
            
            elif target_format == AudioFormat.AAC:
                # AAC is more efficient than MP3
                if sample_rate >= 44100:
                    return 256  # Equivalent to 320 kbps MP3
                elif sample_rate >= 32000:
                    return 192
                else:
                    return 128
            
            elif target_format == AudioFormat.OGG:
                # Vorbis quality levels (approximately)
                if sample_rate >= 44100:
                    return 256
                elif sample_rate >= 32000:
                    return 192
                else:
                    return 128
            
            else:
                return 256  # Default high quality
                
        except Exception as e:
            logger.error(f"Bitrate optimization failed: {e}")
            return 256  # Safe default
    
    async def assess_conversion_quality(self,
                                      original_path: Path,
                                      converted_path: Path) -> Dict[str, float]:
        """Assess quality of converted audio"""
        try:
            # Load both files
            original, sr1 = librosa.load(str(original_path), sr=None)
            converted, sr2 = librosa.load(str(converted_path), sr=None)
            
            # Align for comparison
            if sr1 != sr2:
                converted = librosa.resample(converted, orig_sr=sr2, target_sr=sr1)
            
            min_length = min(len(original), len(converted))
            original = original[:min_length]
            converted = converted[:min_length]
            
            quality_metrics = {}
            
            # Signal-to-noise ratio
            noise = original - converted
            signal_power = np.mean(original ** 2)
            noise_power = np.mean(noise ** 2)
            
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
                quality_metrics['snr_db'] = float(snr)
                
                # Convert SNR to quality score (0-1)
                quality_metrics['quality_score'] = min(1.0, max(0.0, (snr - 20) / 40))
            
            # Spectral similarity
            stft_orig = np.abs(librosa.stft(original))
            stft_conv = np.abs(librosa.stft(converted))
            
            # Ensure same shape
            min_frames = min(stft_orig.shape[1], stft_conv.shape[1])
            stft_orig = stft_orig[:, :min_frames]
            stft_conv = stft_conv[:, :min_frames]
            
            # Calculate spectral correlation
            spectral_corr = np.corrcoef(
                stft_orig.flatten(), 
                stft_conv.flatten()
            )[0, 1]
            
            if not np.isnan(spectral_corr):
                quality_metrics['spectral_similarity'] = float(spectral_corr)
            
            # Perceptual quality (simplified PESQ-like metric)
            if 'snr_db' in quality_metrics and 'spectral_similarity' in quality_metrics:
                perceptual_quality = (
                    0.7 * quality_metrics['quality_score'] +
                    0.3 * quality_metrics['spectral_similarity']
                )
                quality_metrics['perceptual_quality'] = float(perceptual_quality)
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return {}
    
    def recommend_settings_for_use_case(self, use_case: str) -> ConversionSettings:
        """Recommend conversion settings for specific use cases"""
        
        use_case_settings = {
            "streaming": ConversionSettings(
                target_format=AudioFormat.AAC,
                quality_level=QualityLevel.MEDIUM,
                bitrate=192,
                sample_rate=44100
            ),
            "podcast": ConversionSettings(
                target_format=AudioFormat.MP3,
                quality_level=QualityLevel.MEDIUM,
                bitrate=128,
                sample_rate=22050,
                channels=1  # Mono for speech
            ),
            "music_distribution": ConversionSettings(
                target_format=AudioFormat.FLAC,
                quality_level=QualityLevel.LOSSLESS,
                sample_rate=44100,
                bit_depth=24
            ),
            "mobile_app": ConversionSettings(
                target_format=AudioFormat.AAC,
                quality_level=QualityLevel.MEDIUM,
                bitrate=128,
                sample_rate=44100
            ),
            "web_background": ConversionSettings(
                target_format=AudioFormat.OGG,
                quality_level=QualityLevel.LOW,
                bitrate=96,
                sample_rate=22050
            ),
            "archival": ConversionSettings(
                target_format=AudioFormat.WAV,
                quality_level=QualityLevel.LOSSLESS,
                sample_rate=96000,
                bit_depth=24
            )
        }
        
        return use_case_settings.get(
            use_case.lower(),
            ConversionSettings(
                target_format=AudioFormat.MP3,
                quality_level=QualityLevel.HIGH
            )
        )
