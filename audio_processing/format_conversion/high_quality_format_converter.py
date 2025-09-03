"""🔄 High Quality Format Converter - Professional Multi-Format Conversion Service

Industrial-grade audio format conversion engine providing professional
quality format conversion with metadata preservation for enterprise workflows.

Created by: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ LEGAL WARNING & COPYRIGHT PROTECTION
=====================================
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, copying, modification, distribution, or commercialization
of this code WITHOUT explicit written permission is STRICTLY PROHIBITED
and will result in legal action under German and International copyright law.

For licensing inquiries: mlaiel@live.de

Team Expertise:
- Lead Developer AI & Machine Learning: Fahed Mlaiel
- Senior Backend Architecture: Advanced Python/FastAPI
- Audio Mastering Engineer: Professional Format Standards
- Codec Specialist: Advanced Compression & Quality Optimization
- Database Administrator: PostgreSQL & Vector Databases
- Security Engineer: Enterprise Security & Authentication
- Microservices Architect: Scalable Distributed Systems
- DevOps Engineer: CI/CD & Cloud Infrastructure
- IA Prompt Engineer: Advanced AI Model Training
"""

import asyncio
import logging
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import concurrent.futures
import time
import hashlib
import json
from io import BytesIO
import wave
import struct

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Professional audio format specifications."""
    # Uncompressed formats
    WAV_PCM = "wav_pcm"                    # PCM WAV (industry standard)
    AIFF_PCM = "aiff_pcm"                 # AIFF PCM (Apple standard)
    
    # Lossless compressed formats  
    FLAC = "flac"                         # Free Lossless Audio Codec
    ALAC = "alac"                         # Apple Lossless Audio Codec
    WV = "wavpack"                        # WavPack lossless
    
    # Lossy compressed formats
    MP3_320 = "mp3_320"                   # MP3 320 kbps VBR
    MP3_256 = "mp3_256"                   # MP3 256 kbps VBR
    AAC_256 = "aac_256"                   # AAC 256 kbps VBR
    OGG_Q8 = "ogg_q8"                     # OGG Vorbis quality 8
    OPUS_256 = "opus_256"                 # Opus 256 kbps
    
    # Professional broadcast formats
    BWF = "bwf"                           # Broadcast Wave Format
    RF64 = "rf64"                         # RF64 (extended WAV)
    CAF = "caf"                           # Core Audio Format
    
    # High-resolution formats
    DSD64 = "dsd64"                       # DSD 1-bit 2.8MHz
    DSD128 = "dsd128"                     # DSD 1-bit 5.6MHz


class SampleRate(Enum):
    """Professional sample rate specifications."""
    SR_44100 = 44100      # CD quality
    SR_48000 = 48000      # Professional standard
    SR_88200 = 88200      # High-res (2x CD)
    SR_96000 = 96000      # Professional high-res
    SR_176400 = 176400    # Ultra high-res (4x CD)
    SR_192000 = 192000    # Professional ultra high-res
    SR_352800 = 352800    # DSD conversion rate
    SR_384000 = 384000    # Maximum professional rate


class BitDepth(Enum):
    """Professional bit depth specifications."""
    BIT_16 = 16           # CD quality
    BIT_24 = 24           # Professional standard
    BIT_32_INT = 32       # 32-bit integer
    BIT_32_FLOAT = "32f"  # 32-bit float
    BIT_64_FLOAT = "64f"  # 64-bit float (internal processing)


class QualityProfile(Enum):
    """Conversion quality profiles."""
    ARCHIVAL = "archival"               # Maximum quality preservation
    MASTERING = "mastering"             # Mastering studio quality
    BROADCAST = "broadcast"             # Broadcast delivery quality
    STREAMING_HIGH = "streaming_high"   # High-quality streaming
    STREAMING_STANDARD = "streaming_standard" # Standard streaming
    MOBILE_OPTIMIZED = "mobile_optimized"     # Mobile device optimized


@dataclass
class FormatSpecification:
    """Detailed format specification."""
    format: AudioFormat
    sample_rate: SampleRate
    bit_depth: BitDepth
    channels: int = 2
    quality_profile: QualityProfile = QualityProfile.MASTERING
    encoding_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetadataInfo:
    """Comprehensive audio metadata."""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    date: Optional[str] = None
    genre: Optional[str] = None
    track_number: Optional[int] = None
    total_tracks: Optional[int] = None
    composer: Optional[str] = None
    performer: Optional[str] = None
    copyright: Optional[str] = None
    description: Optional[str] = None
    isrc: Optional[str] = None
    iswc: Optional[str] = None
    barcode: Optional[str] = None
    catalog_number: Optional[str] = None
    label: Optional[str] = None
    producer: Optional[str] = None
    engineer: Optional[str] = None
    mastered_by: Optional[str] = None
    studio: Optional[str] = None
    technical_info: Dict[str, Any] = field(default_factory=dict)
    custom_tags: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversionRequest:
    """Professional format conversion request."""
    audio_data: Union[np.ndarray, bytes, str]
    input_sample_rate: int
    target_specification: FormatSpecification
    preserve_metadata: bool = True
    apply_dithering: bool = True
    normalize_before_conversion: bool = False
    apply_noise_shaping: bool = True
    source_metadata: Optional[MetadataInfo] = None
    output_filename: Optional[str] = None


@dataclass
class ConversionResult:
    """Professional conversion result with quality analysis."""
    converted_audio: Union[np.ndarray, bytes]
    output_format: AudioFormat
    output_sample_rate: int
    output_bit_depth: Union[int, str]
    file_size_bytes: int
    conversion_time: float
    quality_metrics: Dict[str, float]
    metadata_preserved: Dict[str, Any]
    conversion_log: List[str]
    checksum: str
    compression_ratio: Optional[float] = None


class HighQualityFormatConverter:
    """Industrial-grade high-quality format conversion engine.
    
    Provides professional format conversion with metadata preservation,
    quality optimization, and enterprise-level performance.
    """
    
    def __init__(
        self,
        temp_dir: Optional[str] = None,
        max_concurrent_jobs: int = 4,
        enable_quality_analysis: bool = True,
        preserve_processing_history: bool = True
    ):
        """Initialize the professional format converter.
        
        Args:
            temp_dir: Temporary directory for processing
            max_concurrent_jobs: Maximum concurrent conversion jobs
            enable_quality_analysis: Enable detailed quality analysis
            preserve_processing_history: Preserve conversion history in metadata
        """
        self.temp_dir = Path(temp_dir) if temp_dir else Path.cwd() / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        self.max_concurrent_jobs = max_concurrent_jobs
        self.enable_quality_analysis = enable_quality_analysis
        self.preserve_processing_history = preserve_processing_history
        
        # Processing statistics
        self.stats = {
            "total_conversions": 0,
            "total_processing_time": 0.0,
            "formats_processed": {},
            "average_quality_score": 0.0,
            "total_data_processed_mb": 0.0
        }
        
        # Thread pool for concurrent processing
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_concurrent_jobs
        )
        
        # Format specifications and codec parameters
        self.format_configs = self._initialize_format_configs()
        
        logger.info(f"HighQualityFormatConverter initialized")
    
    def _initialize_format_configs(self) -> Dict[AudioFormat, Dict[str, Any]]:
        """Initialize format-specific configuration parameters."""
        return {
            AudioFormat.WAV_PCM: {
                "extension": ".wav",
                "subtype": "PCM_24",
                "supports_metadata": True,
                "lossless": True
            },
            AudioFormat.FLAC: {
                "extension": ".flac",
                "compression_level": 8,
                "supports_metadata": True,
                "lossless": True
            },
            AudioFormat.MP3_320: {
                "extension": ".mp3",
                "bitrate": 320,
                "vbr_quality": 0,
                "supports_metadata": True,
                "lossless": False
            },
            AudioFormat.AAC_256: {
                "extension": ".m4a",
                "bitrate": 256,
                "vbr_quality": 5,
                "supports_metadata": True,
                "lossless": False
            },
            AudioFormat.BWF: {
                "extension": ".wav",
                "subtype": "PCM_24",
                "broadcast_metadata": True,
                "supports_metadata": True,
                "lossless": True
            }
        }
    
    async def convert_audio(self, request: ConversionRequest) -> ConversionResult:
        """Perform professional format conversion.
        
        Args:
            request: Conversion request with specifications
            
        Returns:
            ConversionResult with converted audio and quality analysis
        """
        start_time = time.time()
        conversion_log = []
        
        try:
            # Load and validate input audio
            audio_data, original_sr, original_metadata = await self._load_audio_with_metadata(
                request.audio_data, request.input_sample_rate
            )
            conversion_log.append(f"Loaded audio: {audio_data.shape}, {original_sr}Hz")
            
            # Merge metadata
            final_metadata = self._merge_metadata(original_metadata, request.source_metadata)
            
            # Prepare processing chain
            processing_chain = await self._plan_conversion_chain(
                audio_data, original_sr, request
            )
            conversion_log.extend([f"Processing step: {step}" for step in processing_chain])
            
            # Execute conversion pipeline
            converted_audio, final_sr = await self._execute_conversion_pipeline(
                audio_data, original_sr, request, processing_chain
            )
            
            # Apply format-specific encoding
            output_data, output_metadata = await self._encode_to_target_format(
                converted_audio, final_sr, request.target_specification, final_metadata
            )
            
            # Calculate quality metrics
            quality_metrics = {}
            if self.enable_quality_analysis:
                quality_metrics = await self._analyze_conversion_quality(
                    audio_data, converted_audio, request
                )
            
            # Calculate file size and compression ratio
            file_size = len(output_data) if isinstance(output_data, bytes) else converted_audio.nbytes
            original_size = audio_data.nbytes
            compression_ratio = original_size / file_size if file_size > 0 else None
            
            # Generate checksum
            checksum = self._generate_checksum(output_data)
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self._update_stats(request.target_specification.format, processing_time, 
                             quality_metrics, original_size)
            
            result = ConversionResult(
                converted_audio=output_data,
                output_format=request.target_specification.format,
                output_sample_rate=final_sr,
                output_bit_depth=request.target_specification.bit_depth.value,
                file_size_bytes=file_size,
                conversion_time=processing_time,
                quality_metrics=quality_metrics,
                metadata_preserved=output_metadata,
                conversion_log=conversion_log,
                checksum=checksum,
                compression_ratio=compression_ratio
            )
            
            logger.info(
                f"Conversion completed in {processing_time:.2f}s: "
                f"{request.target_specification.format.value} "
                f"({file_size/1024/1024:.1f}MB)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            raise RuntimeError(f"Audio format conversion failed: {str(e)}")
    
    async def _load_audio_with_metadata(
        self, audio_input: Union[np.ndarray, bytes, str], declared_sr: int
    ) -> Tuple[np.ndarray, int, Dict[str, Any]]:
        """Load audio data with comprehensive metadata extraction."""
        
        def load_and_extract():
            metadata = {}
            
            if isinstance(audio_input, str):
                # Load from file path with metadata
                try:
                    audio_data, sr = librosa.load(audio_input, sr=None, mono=False, dtype=np.float64)
                    metadata = self._extract_file_metadata(audio_input)
                except Exception as e:
                    logger.warning(f"Failed to load {audio_input}: {e}")
                    raise
                    
            elif isinstance(audio_input, bytes):
                # Load from bytes
                audio_data, sr = sf.read(BytesIO(audio_input), dtype=np.float64)
                if audio_data.ndim == 2:
                    audio_data = audio_data.T
                metadata = {"source": "bytes_input"}
                
            elif isinstance(audio_input, np.ndarray):
                audio_data = audio_input.astype(np.float64)
                sr = declared_sr
                metadata = {"source": "numpy_array"}
                
            else:
                raise ValueError(f"Unsupported audio input type: {type(audio_input)}")
            
            # Ensure stereo for professional processing
            if audio_data.ndim == 1:
                audio_data = np.stack([audio_data, audio_data])
            elif audio_data.ndim == 2 and audio_data.shape[0] == 1:
                audio_data = np.stack([audio_data[0], audio_data[0]])
            
            # Add technical metadata
            metadata.update({
                "original_sample_rate": sr,
                "original_channels": audio_data.shape[0],
                "original_duration": audio_data.shape[1] / sr,
                "original_bit_depth": "float64",
                "original_format": "internal_processing"
            })
            
            return audio_data, sr, metadata
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, load_and_extract
        )
    
    def _extract_file_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from audio file."""
        metadata = {"filepath": filepath}
        
        try:
            # Try to extract metadata using mutagen (if available)
            try:
                import mutagen
                file_info = mutagen.File(filepath)
                if file_info:
                    for key, value in file_info.items():
                        if isinstance(value, list) and len(value) > 0:
                            metadata[key] = value[0]
                        else:
                            metadata[key] = value
            except ImportError:
                logger.debug("Mutagen not available for metadata extraction")
            
            # Extract basic file information
            file_path = Path(filepath)
            metadata.update({
                "filename": file_path.name,
                "file_size": file_path.stat().st_size,
                "file_extension": file_path.suffix.lower()
            })
            
        except Exception as e:
            logger.warning(f"Metadata extraction failed for {filepath}: {e}")
        
        return metadata
    
    def _merge_metadata(
        self, original: Dict[str, Any], additional: Optional[MetadataInfo]
    ) -> Dict[str, Any]:
        """Merge original and additional metadata."""
        merged = original.copy()
        
        if additional:
            metadata_dict = {
                "title": additional.title,
                "artist": additional.artist,
                "album": additional.album,
                "date": additional.date,
                "genre": additional.genre,
                "track_number": additional.track_number,
                "total_tracks": additional.total_tracks,
                "composer": additional.composer,
                "performer": additional.performer,
                "copyright": additional.copyright,
                "description": additional.description,
                "isrc": additional.isrc,
                "iswc": additional.iswc,
                "barcode": additional.barcode,
                "catalog_number": additional.catalog_number,
                "label": additional.label,
                "producer": additional.producer,
                "engineer": additional.engineer,
                "mastered_by": additional.mastered_by,
                "studio": additional.studio
            }
            
            # Add non-None values
            for key, value in metadata_dict.items():
                if value is not None:
                    merged[key] = value
            
            # Add technical and custom tags
            merged.update(additional.technical_info)
            merged.update(additional.custom_tags)
        
        return merged
    
    async def _plan_conversion_chain(
        self, audio: np.ndarray, sr: int, request: ConversionRequest
    ) -> List[str]:
        """Plan the optimal conversion processing chain."""
        
        def plan():
            chain = []
            
            target_spec = request.target_specification
            
            # Sample rate conversion
            if sr != target_spec.sample_rate.value:
                chain.append(f"resample_{sr}_to_{target_spec.sample_rate.value}")
            
            # Channel conversion
            if audio.shape[0] != target_spec.channels:
                if target_spec.channels == 1:
                    chain.append("stereo_to_mono")
                elif target_spec.channels == 2:
                    chain.append("mono_to_stereo")
            
            # Normalization
            if request.normalize_before_conversion:
                chain.append("loudness_normalization")
            
            # Bit depth conversion
            current_depth = "float64"
            target_depth = target_spec.bit_depth.value
            if current_depth != target_depth:
                chain.append(f"bit_depth_{current_depth}_to_{target_depth}")
                if request.apply_dithering and isinstance(target_depth, int):
                    chain.append("dithering")
                if request.apply_noise_shaping:
                    chain.append("noise_shaping")
            
            # Format encoding
            chain.append(f"encode_{target_spec.format.value}")
            
            return chain
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, plan
        )
    
    async def _execute_conversion_pipeline(
        self, 
        audio: np.ndarray, 
        sr: int, 
        request: ConversionRequest,
        processing_chain: List[str]
    ) -> Tuple[np.ndarray, int]:
        """Execute the conversion processing pipeline."""
        
        def process():
            current_audio = audio.copy()
            current_sr = sr
            
            for step in processing_chain:
                if step.startswith("resample_"):
                    # High-quality resampling
                    parts = step.split("_")
                    target_sr = int(parts[3])
                    current_audio = self._resample_audio(current_audio, current_sr, target_sr)
                    current_sr = target_sr
                    
                elif step == "stereo_to_mono":
                    # Professional stereo to mono conversion
                    current_audio = self._stereo_to_mono(current_audio)
                    
                elif step == "mono_to_stereo":
                    # Mono to stereo conversion
                    if current_audio.ndim == 1:
                        current_audio = np.stack([current_audio, current_audio])
                    
                elif step == "loudness_normalization":
                    # Apply loudness normalization
                    current_audio = self._apply_loudness_normalization(current_audio, current_sr)
                    
                elif step.startswith("bit_depth_"):
                    # Bit depth conversion
                    target_depth = request.target_specification.bit_depth.value
                    current_audio = self._convert_bit_depth(current_audio, target_depth)
                    
                elif step == "dithering":
                    # Apply professional dithering
                    current_audio = self._apply_dithering(
                        current_audio, request.target_specification.bit_depth.value
                    )
                    
                elif step == "noise_shaping":
                    # Apply noise shaping
                    current_audio = self._apply_noise_shaping(current_audio)
            
            return current_audio, current_sr
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, process
        )
    
    def _resample_audio(self, audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """High-quality audio resampling."""
        if orig_sr == target_sr:
            return audio
        
        # Use highest quality resampling
        resampled = np.array([
            librosa.resample(
                channel, orig_sr=orig_sr, target_sr=target_sr, 
                res_type='kaiser_best', fix=True
            )
            for channel in audio
        ])
        
        return resampled
    
    def _stereo_to_mono(self, audio: np.ndarray) -> np.ndarray:
        """Professional stereo to mono conversion with proper weighting."""
        if audio.ndim == 1:
            return audio
        
        # Apply proper L/R channel weighting
        mono = 0.5 * (audio[0] + audio[1])
        return mono
    
    def _apply_loudness_normalization(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply professional loudness normalization."""
        # Simple peak normalization for now (could integrate with LoudnessNormalizationEngine)
        max_val = np.abs(audio).max()
        if max_val > 0:
            normalized = audio / max_val * 0.95
        else:
            normalized = audio
        
        return normalized
    
    def _convert_bit_depth(self, audio: np.ndarray, target_depth: Union[int, str]) -> np.ndarray:
        """Convert audio to target bit depth."""
        if isinstance(target_depth, str):
            # Float formats
            if target_depth == "32f":
                return audio.astype(np.float32)
            elif target_depth == "64f":
                return audio.astype(np.float64)
        else:
            # Integer formats
            if target_depth == 16:
                # Convert to 16-bit integer
                max_val = 2**15 - 1
                return np.clip(audio * max_val, -max_val, max_val).astype(np.int16)
            elif target_depth == 24:
                # Convert to 24-bit (stored as 32-bit)
                max_val = 2**23 - 1
                return np.clip(audio * max_val, -max_val, max_val).astype(np.int32)
            elif target_depth == 32:
                # Convert to 32-bit integer
                max_val = 2**31 - 1
                return np.clip(audio * max_val, -max_val, max_val).astype(np.int32)
        
        return audio
    
    def _apply_dithering(self, audio: np.ndarray, bit_depth: Union[int, str]) -> np.ndarray:
        """Apply professional dithering for bit depth reduction."""
        if isinstance(bit_depth, str):
            return audio  # No dithering for float formats
        
        # Calculate quantization level
        max_val = 2**(bit_depth - 1) - 1
        quantization_step = 1.0 / max_val
        
        # Apply triangular dithering
        dither_amplitude = quantization_step
        dither_noise = np.random.triangular(
            -dither_amplitude, 0, dither_amplitude, audio.shape
        )
        
        return audio + dither_noise
    
    def _apply_noise_shaping(self, audio: np.ndarray) -> np.ndarray:
        """Apply noise shaping to push quantization noise to higher frequencies."""
        # Simple first-order noise shaping filter
        shaped = np.zeros_like(audio)
        error = np.zeros(audio.shape[0])
        
        for i in range(audio.shape[1]):
            for ch in range(audio.shape[0]):
                shaped[ch, i] = audio[ch, i] + error[ch]
                quantized = np.round(shaped[ch, i] * 32767) / 32767
                error[ch] = shaped[ch, i] - quantized
                shaped[ch, i] = quantized
        
        return shaped
    
    async def _encode_to_target_format(
        self, 
        audio: np.ndarray, 
        sr: int, 
        spec: FormatSpecification,
        metadata: Dict[str, Any]
    ) -> Tuple[Union[np.ndarray, bytes], Dict[str, Any]]:
        """Encode audio to target format with metadata preservation."""
        
        def encode():
            format_config = self.format_configs.get(spec.format, {})
            
            if spec.format in [AudioFormat.WAV_PCM, AudioFormat.BWF]:
                return self._encode_wav(audio, sr, spec, metadata, format_config)
            elif spec.format == AudioFormat.FLAC:
                return self._encode_flac(audio, sr, spec, metadata, format_config)
            elif spec.format in [AudioFormat.MP3_320, AudioFormat.MP3_256]:
                return self._encode_mp3(audio, sr, spec, metadata, format_config)
            elif spec.format == AudioFormat.AAC_256:
                return self._encode_aac(audio, sr, spec, metadata, format_config)
            else:
                # Fallback to WAV
                logger.warning(f"Format {spec.format} not implemented, using WAV")
                return self._encode_wav(audio, sr, spec, metadata, format_config)
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, encode
        )
    
    def _encode_wav(
        self, audio: np.ndarray, sr: int, spec: FormatSpecification, 
        metadata: Dict[str, Any], config: Dict[str, Any]
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Encode to WAV format with metadata."""
        
        # Prepare audio data
        if spec.bit_depth.value == 16:
            audio_data = (audio * 32767).astype(np.int16)
            sample_width = 2
            subtype = 'PCM_16'
        elif spec.bit_depth.value == 24:
            audio_data = (audio * 8388607).astype(np.int32)
            sample_width = 3
            subtype = 'PCM_24'
        else:
            audio_data = audio.astype(np.float32)
            sample_width = 4
            subtype = 'FLOAT'
        
        # Convert to interleaved format for WAV
        if audio_data.ndim == 2:
            interleaved = np.column_stack([audio_data[0], audio_data[1]])
        else:
            interleaved = audio_data
        
        # Create WAV bytes
        output = BytesIO()
        with sf.SoundFile(
            output, 'w', 
            samplerate=sr, 
            channels=spec.channels,
            subtype=subtype,
            format='WAV'
        ) as f:
            f.write(interleaved)
        
        output_bytes = output.getvalue()
        
        # Preserve metadata
        preserved_metadata = {
            "format": "WAV",
            "sample_rate": sr,
            "channels": spec.channels,
            "bit_depth": spec.bit_depth.value,
            "duration": len(audio_data[0]) / sr if audio_data.ndim == 2 else len(audio_data) / sr
        }
        preserved_metadata.update(metadata)
        
        return output_bytes, preserved_metadata
    
    def _encode_flac(
        self, audio: np.ndarray, sr: int, spec: FormatSpecification,
        metadata: Dict[str, Any], config: Dict[str, Any]
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Encode to FLAC format with metadata."""
        
        # Prepare audio data (FLAC supports up to 24-bit)
        if spec.bit_depth.value == 16:
            audio_data = (audio * 32767).astype(np.int16)
            subtype = 'PCM_16'
        else:
            audio_data = (audio * 8388607).astype(np.int32)
            subtype = 'PCM_24'
        
        # Convert to interleaved format
        if audio_data.ndim == 2:
            interleaved = np.column_stack([audio_data[0], audio_data[1]])
        else:
            interleaved = audio_data
        
        # Create FLAC bytes
        output = BytesIO()
        with sf.SoundFile(
            output, 'w',
            samplerate=sr,
            channels=spec.channels,
            subtype=subtype,
            format='FLAC'
        ) as f:
            f.write(interleaved)
        
        output_bytes = output.getvalue()
        
        preserved_metadata = {
            "format": "FLAC",
            "sample_rate": sr,
            "channels": spec.channels,
            "bit_depth": spec.bit_depth.value,
            "compression": "lossless",
            "duration": len(audio_data[0]) / sr if audio_data.ndim == 2 else len(audio_data) / sr
        }
        preserved_metadata.update(metadata)
        
        return output_bytes, preserved_metadata
    
    def _encode_mp3(
        self, audio: np.ndarray, sr: int, spec: FormatSpecification,
        metadata: Dict[str, Any], config: Dict[str, Any]
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Encode to MP3 format (placeholder - requires external encoder)."""
        
        # For now, return WAV as fallback
        logger.warning("MP3 encoding requires external library (pydub/ffmpeg)")
        return self._encode_wav(audio, sr, spec, metadata, config)
    
    def _encode_aac(
        self, audio: np.ndarray, sr: int, spec: FormatSpecification,
        metadata: Dict[str, Any], config: Dict[str, Any]
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Encode to AAC format (placeholder - requires external encoder)."""
        
        # For now, return WAV as fallback
        logger.warning("AAC encoding requires external library (pydub/ffmpeg)")
        return self._encode_wav(audio, sr, spec, metadata, config)
    
    async def _analyze_conversion_quality(
        self, original: np.ndarray, converted: np.ndarray, request: ConversionRequest
    ) -> Dict[str, float]:
        """Analyze conversion quality metrics."""
        
        def analyze():
            metrics = {}
            
            # Ensure same sample rate for comparison
            if original.shape != converted.shape:
                # Resample for comparison
                if original.shape[1] != converted.shape[1]:
                    min_len = min(original.shape[1], converted.shape[1])
                    orig_comp = original[:, :min_len]
                    conv_comp = converted[:, :min_len]
                else:
                    orig_comp = original
                    conv_comp = converted
            else:
                orig_comp = original
                conv_comp = converted
            
            # Signal-to-Noise Ratio
            diff = orig_comp - conv_comp
            signal_power = np.mean(orig_comp ** 2)
            noise_power = np.mean(diff ** 2)
            
            if noise_power > 0:
                snr_db = 10 * np.log10(signal_power / noise_power)
            else:
                snr_db = 100.0  # Perfect reconstruction
            
            metrics["snr_db"] = float(snr_db)
            
            # Total Harmonic Distortion + Noise (THD+N)
            fft_orig = np.fft.fft(orig_comp[0] if orig_comp.ndim == 2 else orig_comp)
            fft_conv = np.fft.fft(conv_comp[0] if conv_comp.ndim == 2 else conv_comp)
            
            # Simplified THD+N calculation
            fundamental_power = np.abs(fft_orig[:len(fft_orig)//10]).max()**2
            noise_harmonics_power = np.mean(np.abs(fft_orig - fft_conv)**2)
            
            if fundamental_power > 0:
                thd_n = np.sqrt(noise_harmonics_power / fundamental_power)
                thd_n_db = 20 * np.log10(thd_n + 1e-10)
            else:
                thd_n_db = -100.0
            
            metrics["thd_n_db"] = float(thd_n_db)
            
            # Frequency response correlation
            freq_corr = np.corrcoef(
                np.abs(fft_orig[:len(fft_orig)//2]).flatten(),
                np.abs(fft_conv[:len(fft_conv)//2]).flatten()
            )[0, 1]
            
            metrics["frequency_response_correlation"] = float(freq_corr)
            
            # Dynamic range preservation
            orig_dr = self._calculate_dynamic_range(orig_comp)
            conv_dr = self._calculate_dynamic_range(conv_comp)
            dr_preservation = 1.0 - abs(orig_dr - conv_dr) / max(orig_dr, 1.0)
            
            metrics["dynamic_range_preservation"] = float(dr_preservation)
            
            # Overall quality score
            quality_score = (
                min(1.0, (snr_db + 60) / 80) * 0.4 +  # SNR component
                min(1.0, (-thd_n_db + 40) / 60) * 0.3 +  # THD+N component
                freq_corr * 0.2 +  # Frequency response component
                dr_preservation * 0.1  # Dynamic range component
            )
            
            metrics["overall_quality"] = float(max(0.0, min(1.0, quality_score)))
            
            return metrics
        
        return await asyncio.get_event_loop().run_in_executor(
            self.executor, analyze
        )
    
    def _calculate_dynamic_range(self, audio: np.ndarray) -> float:
        """Calculate dynamic range of audio signal."""
        if audio.ndim == 2:
            signal = np.mean(audio, axis=0)
        else:
            signal = audio
        
        # Calculate RMS in sliding windows
        window_size = len(signal) // 100  # 1% of signal length
        if window_size < 1024:
            window_size = min(1024, len(signal))
        
        rms_values = []
        for i in range(0, len(signal) - window_size + 1, window_size // 4):
            window = signal[i:i + window_size]
            rms = np.sqrt(np.mean(window ** 2))
            if rms > 0:
                rms_values.append(20 * np.log10(rms))
        
        if len(rms_values) < 2:
            return 0.0
        
        return np.percentile(rms_values, 95) - np.percentile(rms_values, 10)
    
    def _generate_checksum(self, data: Union[np.ndarray, bytes]) -> str:
        """Generate SHA-256 checksum for data integrity."""
        if isinstance(data, np.ndarray):
            data_bytes = data.tobytes()
        else:
            data_bytes = data
        
        return hashlib.sha256(data_bytes).hexdigest()
    
    def _update_stats(
        self, format_type: AudioFormat, processing_time: float,
        quality_metrics: Dict[str, float], data_size_bytes: int
    ):
        """Update conversion statistics."""
        self.stats["total_conversions"] += 1
        self.stats["total_processing_time"] += processing_time
        
        # Update format statistics
        format_name = format_type.value
        if format_name not in self.stats["formats_processed"]:
            self.stats["formats_processed"][format_name] = 0
        self.stats["formats_processed"][format_name] += 1
        
        # Update quality statistics
        if "overall_quality" in quality_metrics:
            total_jobs = self.stats["total_conversions"]
            current_avg = self.stats["average_quality_score"]
            new_avg = (
                (current_avg * (total_jobs - 1) + quality_metrics["overall_quality"]) / total_jobs
            )
            self.stats["average_quality_score"] = new_avg
        
        # Update data processed
        self.stats["total_data_processed_mb"] += data_size_bytes / (1024 * 1024)
    
    async def batch_convert(
        self, requests: List[ConversionRequest]
    ) -> List[ConversionResult]:
        """Process multiple conversion requests concurrently."""
        
        batch_size = min(self.max_concurrent_jobs, len(requests))
        results = []
        
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.convert_audio(req) for req in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch conversion failed: {result}")
                    results.append(None)
                else:
                    results.append(result)
        
        return [r for r in results if r is not None]
    
    def get_supported_formats(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed information about supported formats."""
        return {
            format_enum.value: {
                **config,
                "sample_rates": [sr.value for sr in SampleRate],
                "bit_depths": [bd.value for bd in BitDepth],
                "quality_profiles": [qp.value for qp in QualityProfile]
            }
            for format_enum, config in self.format_configs.items()
        }
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get engine performance statistics."""
        return {
            **self.stats,
            "max_concurrent_jobs": self.max_concurrent_jobs,
            "enable_quality_analysis": self.enable_quality_analysis,
            "supported_formats": len(self.format_configs)
        }
    
    async def cleanup(self):
        """Cleanup resources and temporary files."""
        try:
            self.executor.shutdown(wait=True)
            
            # Clean temporary files
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            logger.info("HighQualityFormatConverter cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# Convenience functions for direct usage
async def convert_audio_format(
    audio_input: Union[np.ndarray, bytes, str],
    input_sample_rate: int,
    target_format: AudioFormat,
    target_sample_rate: SampleRate = SampleRate.SR_48000,
    target_bit_depth: BitDepth = BitDepth.BIT_24,
    quality_profile: QualityProfile = QualityProfile.MASTERING
) -> ConversionResult:
    """Professional audio format conversion function.
    
    Args:
        audio_input: Audio data (array, bytes, or file path)
        input_sample_rate: Input sample rate
        target_format: Target audio format
        target_sample_rate: Target sample rate
        target_bit_depth: Target bit depth
        quality_profile: Quality profile for conversion
        
    Returns:
        ConversionResult with converted audio and analysis
    """
    converter = HighQualityFormatConverter()
    try:
        target_spec = FormatSpecification(
            format=target_format,
            sample_rate=target_sample_rate,
            bit_depth=target_bit_depth,
            quality_profile=quality_profile
        )
        
        request = ConversionRequest(
            audio_data=audio_input,
            input_sample_rate=input_sample_rate,
            target_specification=target_spec
        )
        
        return await converter.convert_audio(request)
    finally:
        await converter.cleanup()


def create_format_converter(**kwargs) -> HighQualityFormatConverter:
    """Create a configured format converter instance."""
    return HighQualityFormatConverter(**kwargs)