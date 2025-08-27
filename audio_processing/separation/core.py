"""
Core separation engine providing the main interface for audio source separation.

This module contains the primary SeparationEngine class and configuration management
for the entire audio separation system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - Unauthorized use strictly prohibited
"""

import asyncio
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import torch
import librosa
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from ...core.config import get_settings
from ...core.exceptions import AudioProcessingError
from ...utils.logging import get_logger

logger = get_logger(__name__)


class SeparationModel(Enum):
    """Available separation model types."""
    SPLEETER = "spleeter"
    OPEN_UNMIX = "open_unmix"
    DEMUCS = "demucs"
    HYBRID = "hybrid"
    CUSTOM = "custom"


class SeparationQuality(Enum):
    """Quality levels for separation processing."""
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    STUDIO = "studio"


class OutputFormat(Enum):
    """Supported output audio formats."""
    WAV = "wav"
    FLAC = "flac"
    MP3 = "mp3"
    AAC = "aac"
    OGG = "ogg"


@dataclass
class SeparationConfig:
    """Configuration for audio separation operations."""
    
    # Model configuration
    model_type: SeparationModel = SeparationModel.DEMUCS
    quality: SeparationQuality = SeparationQuality.HIGH
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Audio parameters
    sample_rate: int = 44100
    bit_depth: int = 32
    channels: int = 2
    
    # Processing parameters
    chunk_size: int = 4096
    overlap: float = 0.25
    batch_size: int = 8
    max_duration: int = 600  # seconds
    
    # Output configuration
    output_format: OutputFormat = OutputFormat.WAV
    normalize: bool = True
    remove_silence: bool = False
    
    # Model paths
    model_cache_dir: Path = field(default_factory=lambda: Path("models/separation"))
    temp_dir: Path = field(default_factory=lambda: Path("/tmp/separation"))
    
    # Performance settings
    use_gpu: bool = True
    num_workers: int = 4
    memory_limit: int = 8192  # MB
    
    # Quality thresholds
    min_quality_score: float = 0.7
    silence_threshold: float = 0.001
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.use_gpu and not torch.cuda.is_available():
            logger.warning("GPU requested but not available, falling back to CPU")
            self.device = "cpu"
            self.use_gpu = False
        
        # Create directories
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)


class SeparationEngine:
    """
    Advanced audio source separation engine using state-of-the-art AI models.
    
    Supports multiple separation models and provides high-quality stem extraction
    for professional music production and content creation.
    """
    
    def __init__(self, config: Optional[SeparationConfig] = None):
        """Initialize the separation engine."""
        self.config = config or SeparationConfig()
        self.models: Dict[str, Any] = {}
        self.is_initialized = False
        self._lock = threading.RLock()
        
        logger.info(f"Initializing SeparationEngine with {self.config.model_type.value}")
        
    async def initialize(self) -> None:
        """Initialize the separation models asynchronously."""
        if self.is_initialized:
            return
            
        async with asyncio.Lock():
            if self.is_initialized:
                return
                
            try:
                await self._load_models()
                self.is_initialized = True
                logger.info("SeparationEngine initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize separation engine: {e}")
                raise AudioProcessingError(f"Engine initialization failed: {e}")
    
    async def _load_models(self) -> None:
        """Load separation models based on configuration."""
        if self.config.model_type == SeparationModel.DEMUCS:
            await self._load_demucs_model()
        elif self.config.model_type == SeparationModel.SPLEETER:
            await self._load_spleeter_model()
        elif self.config.model_type == SeparationModel.OPEN_UNMIX:
            await self._load_openunmix_model()
        elif self.config.model_type == SeparationModel.HYBRID:
            await self._load_hybrid_models()
        else:
            raise ValueError(f"Unsupported model type: {self.config.model_type}")
    
    async def _load_demucs_model(self) -> None:
        """Load Demucs model for high-quality separation."""
        try:
            import demucs.api
            
            model_name = self._get_demucs_model_name()
            separator = demucs.api.Separator(
                model=model_name,
                device=self.config.device,
                progress=True
            )
            
            self.models['demucs'] = separator
            logger.info(f"Loaded Demucs model: {model_name}")
            
        except ImportError:
            logger.error("Demucs not installed. Install with: pip install demucs")
            raise AudioProcessingError("Demucs model not available")
        except Exception as e:
            logger.error(f"Failed to load Demucs model: {e}")
            raise
    
    async def _load_spleeter_model(self) -> None:
        """Load Spleeter model."""
        try:
            from spleeter.separator import Separator
            
            model_name = self._get_spleeter_model_name()
            separator = Separator(model_name)
            
            self.models['spleeter'] = separator
            logger.info(f"Loaded Spleeter model: {model_name}")
            
        except ImportError:
            logger.error("Spleeter not installed. Install with: pip install spleeter")
            raise AudioProcessingError("Spleeter model not available")
        except Exception as e:
            logger.error(f"Failed to load Spleeter model: {e}")
            raise
    
    async def _load_openunmix_model(self) -> None:
        """Load Open-Unmix model."""
        try:
            import openunmix
            
            device = torch.device(self.config.device)
            model = openunmix.umx.load_model(device=device)
            
            self.models['openunmix'] = model
            logger.info("Loaded Open-Unmix model")
            
        except ImportError:
            logger.error("Open-Unmix not installed")
            raise AudioProcessingError("Open-Unmix model not available")
        except Exception as e:
            logger.error(f"Failed to load Open-Unmix model: {e}")
            raise
    
    async def _load_hybrid_models(self) -> None:
        """Load multiple models for hybrid separation."""
        await self._load_demucs_model()
        await self._load_spleeter_model()
        logger.info("Loaded hybrid models")
    
    def _get_demucs_model_name(self) -> str:
        """Get appropriate Demucs model name based on quality."""
        quality_models = {
            SeparationQuality.DRAFT: "mdx",
            SeparationQuality.STANDARD: "mdx_extra",
            SeparationQuality.HIGH: "mdx_extra_q",
            SeparationQuality.STUDIO: "htdemucs"
        }
        return quality_models.get(self.config.quality, "mdx_extra")
    
    def _get_spleeter_model_name(self) -> str:
        """Get appropriate Spleeter model name."""
        return "spleeter:4stems-16kHz"
    
    async def separate(
        self,
        audio_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        stems: Optional[List[str]] = None
    ) -> Dict[str, Path]:
        """
        Separate audio into individual stems.
        
        Args:
            audio_path: Path to input audio file
            output_dir: Directory to save separated stems
            stems: Specific stems to extract (vocals, drums, bass, other)
            
        Returns:
            Dictionary mapping stem names to output file paths
        """
        if not self.is_initialized:
            await self.initialize()
        
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise AudioProcessingError(f"Audio file not found: {audio_path}")
        
        # Validate audio file
        await self._validate_audio_file(audio_path)
        
        # Set up output directory
        if output_dir is None:
            output_dir = audio_path.parent / f"{audio_path.stem}_separated"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Perform separation based on model type
        try:
            if self.config.model_type == SeparationModel.DEMUCS:
                return await self._separate_with_demucs(audio_path, output_dir, stems)
            elif self.config.model_type == SeparationModel.SPLEETER:
                return await self._separate_with_spleeter(audio_path, output_dir, stems)
            elif self.config.model_type == SeparationModel.HYBRID:
                return await self._separate_with_hybrid(audio_path, output_dir, stems)
            else:
                raise AudioProcessingError(f"Separation not implemented for {self.config.model_type}")
                
        except Exception as e:
            logger.error(f"Separation failed: {e}")
            raise AudioProcessingError(f"Audio separation failed: {e}")
    
    async def _validate_audio_file(self, audio_path: Path) -> None:
        """Validate audio file format and properties."""
        try:
            info = librosa.get_samplerate(str(audio_path))
            duration = librosa.get_duration(filename=str(audio_path))
            
            if duration > self.config.max_duration:
                raise AudioProcessingError(
                    f"Audio duration ({duration:.1f}s) exceeds maximum ({self.config.max_duration}s)"
                )
                
        except Exception as e:
            raise AudioProcessingError(f"Invalid audio file: {e}")
    
    async def _separate_with_demucs(
        self, 
        audio_path: Path, 
        output_dir: Path,
        stems: Optional[List[str]] = None
    ) -> Dict[str, Path]:
        """Separate audio using Demucs model."""
        separator = self.models['demucs']
        
        # Load and separate
        waveform, sr = librosa.load(str(audio_path), sr=self.config.sample_rate, mono=False)
        
        if waveform.ndim == 1:
            waveform = waveform.reshape(1, -1)
        
        # Run separation
        sources = separator(waveform)
        
        # Save stems
        stem_files = {}
        default_stems = ['vocals', 'drums', 'bass', 'other']
        target_stems = stems or default_stems
        
        for i, stem_name in enumerate(['drums', 'bass', 'other', 'vocals']):
            if stem_name in target_stems:
                output_path = output_dir / f"{stem_name}.{self.config.output_format.value}"
                
                # Save audio
                if i < len(sources):
                    stem_audio = sources[i].cpu().numpy()
                    if self.config.normalize:
                        stem_audio = self._normalize_audio(stem_audio)
                    
                    librosa.output.write_wav(
                        str(output_path),
                        stem_audio.T,
                        sr=self.config.sample_rate
                    )
                    stem_files[stem_name] = output_path
        
        return stem_files
    
    async def _separate_with_spleeter(
        self,
        audio_path: Path,
        output_dir: Path,
        stems: Optional[List[str]] = None
    ) -> Dict[str, Path]:
        """Separate audio using Spleeter model."""
        separator = self.models['spleeter']
        
        # Load audio
        waveform, sr = librosa.load(
            str(audio_path), 
            sr=self.config.sample_rate, 
            mono=False
        )
        
        # Separate
        sources = separator.separate(waveform)
        
        # Save stems
        stem_files = {}
        target_stems = stems or list(sources.keys())
        
        for stem_name, stem_audio in sources.items():
            if stem_name in target_stems:
                output_path = output_dir / f"{stem_name}.{self.config.output_format.value}"
                
                if self.config.normalize:
                    stem_audio = self._normalize_audio(stem_audio)
                
                librosa.output.write_wav(
                    str(output_path),
                    stem_audio,
                    sr=self.config.sample_rate
                )
                stem_files[stem_name] = output_path
        
        return stem_files
    
    async def _separate_with_hybrid(
        self,
        audio_path: Path,
        output_dir: Path,
        stems: Optional[List[str]] = None
    ) -> Dict[str, Path]:
        """Separate using hybrid approach with multiple models."""
        # Use Demucs for primary separation
        demucs_results = await self._separate_with_demucs(audio_path, output_dir, stems)
        
        # Enhance vocal separation with Spleeter
        if 'vocals' in demucs_results:
            spleeter_vocal = await self._enhance_vocal_separation(audio_path)
            if spleeter_vocal is not None:
                # Blend results for better vocal isolation
                enhanced_vocal = self._blend_vocal_sources(
                    demucs_results['vocals'],
                    spleeter_vocal
                )
                librosa.output.write_wav(
                    str(demucs_results['vocals']),
                    enhanced_vocal,
                    sr=self.config.sample_rate
                )
        
        return demucs_results
    
    async def _enhance_vocal_separation(self, audio_path: Path) -> Optional[np.ndarray]:
        """Enhance vocal separation using secondary model."""
        try:
            if 'spleeter' not in self.models:
                return None
            
            separator = self.models['spleeter']
            waveform, _ = librosa.load(str(audio_path), sr=self.config.sample_rate)
            sources = separator.separate(waveform)
            
            return sources.get('vocals')
        except Exception as e:
            logger.warning(f"Vocal enhancement failed: {e}")
            return None
    
    def _blend_vocal_sources(
        self, 
        primary_path: Path, 
        secondary_audio: np.ndarray
    ) -> np.ndarray:
        """Blend vocal sources from different models."""
        # Load primary vocal
        primary_audio, _ = librosa.load(str(primary_path), sr=self.config.sample_rate)
        
        # Simple weighted blend
        alpha = 0.7  # Weight for primary source
        blended = alpha * primary_audio + (1 - alpha) * secondary_audio
        
        return self._normalize_audio(blended)
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to prevent clipping."""
        if audio.max() == 0:
            return audio
        
        return audio / np.max(np.abs(audio)) * 0.95
    
    async def get_separation_info(self, audio_path: Union[str, Path]) -> Dict[str, Any]:
        """Get information about potential separation quality."""
        audio_path = Path(audio_path)
        
        try:
            # Load audio for analysis
            y, sr = librosa.load(str(audio_path), sr=self.config.sample_rate)
            
            # Analyze audio characteristics
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Estimate separation difficulty
            complexity = self._estimate_complexity(y, sr)
            
            return {
                'duration': float(duration),
                'sample_rate': int(sr),
                'channels': 1 if y.ndim == 1 else y.shape[0],
                'spectral_centroid': float(spectral_centroid),
                'tempo': float(tempo),
                'complexity': complexity,
                'recommended_quality': self._recommend_quality(complexity),
                'estimated_time': self._estimate_processing_time(duration, complexity)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze audio: {e}")
            return {'error': str(e)}
    
    def _estimate_complexity(self, audio: np.ndarray, sr: int) -> float:
        """Estimate separation complexity based on audio characteristics."""
        # Calculate various features
        spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr))
        zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio))
        
        # Normalize and combine features
        complexity = (
            (spectral_bandwidth / sr) * 0.4 +
            (spectral_rolloff / sr) * 0.3 +
            zero_crossing_rate * 0.3
        )
        
        return min(max(complexity, 0.0), 1.0)
    
    def _recommend_quality(self, complexity: float) -> SeparationQuality:
        """Recommend separation quality based on complexity."""
        if complexity < 0.3:
            return SeparationQuality.STANDARD
        elif complexity < 0.6:
            return SeparationQuality.HIGH
        else:
            return SeparationQuality.STUDIO
    
    def _estimate_processing_time(self, duration: float, complexity: float) -> float:
        """Estimate processing time in seconds."""
        base_ratio = {
            SeparationQuality.DRAFT: 0.5,
            SeparationQuality.STANDARD: 1.0,
            SeparationQuality.HIGH: 2.0,
            SeparationQuality.STUDIO: 4.0
        }
        
        ratio = base_ratio.get(self.config.quality, 2.0)
        complexity_factor = 1.0 + complexity
        
        return duration * ratio * complexity_factor
    
    async def cleanup(self) -> None:
        """Clean up resources and temporary files."""
        try:
            # Clear models
            self.models.clear()
            
            # Clean temporary directory
            if self.config.temp_dir.exists():
                import shutil
                shutil.rmtree(self.config.temp_dir, ignore_errors=True)
                self.config.temp_dir.mkdir(parents=True, exist_ok=True)
            
            self.is_initialized = False
            logger.info("SeparationEngine cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
