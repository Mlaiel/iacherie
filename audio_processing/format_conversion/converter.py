"""Audio Format Converter - Core Conversion Engine

Professional multi-format audio conversion system with advanced quality preservation,
batch processing, and intelligent optimization capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import numpy as np
import soundfile as sf
import librosa
from scipy import signal
from scipy.signal import butter, filtfilt, resample
import subprocess
import json

from ..core.config import AudioConfig
from ..core.exceptions import (
    ConversionError,
    UnsupportedFormatError,
    QualityError
)
from ..core.monitoring import MetricsCollector
from ..core.security import SecurityManager
from .models import (
    ConversionRequest,
    ConversionResult,
    FormatSpecification,
    QualityProfile,
    ProcessingOptions
)
from .config import ConversionConfig
from .formats import FormatRegistry
from .quality import QualityController
from .metadata import MetadataManager

logger = logging.getLogger(__name__)


class AudioFormatConverter:
    """    Professional Audio Format Converter
    
    Ultra-advanced conversion engine supporting all major audio formats with:
    - Professional quality preservation algorithms
    - Intelligent batch processing capabilities
    - Advanced metadata handling and preservation
    - Content protection and rights management
    - Real-time quality monitoring and optimization
    """    
    def __init__(self, 
                 config: Optional[ConversionConfig] = None,
                 metrics: Optional[MetricsCollector] = None):
        """Initialize the audio format converter"""        self.config = config or ConversionConfig()
        self.metrics = metrics or MetricsCollector()
        self.format_registry = FormatRegistry()
        self.quality_controller = QualityController()
        self.metadata_manager = MetadataManager()
        self.security_manager = SecurityManager()
        
        # Initialize processing resources
        self.thread_executor = ThreadPoolExecutor(max_workers=self.config.max_threads)
        self.process_executor = ProcessPoolExecutor(max_workers=self.config.max_processes)
        
        # Cache for optimized settings
        self._optimization_cache: Dict[str, Dict] = {}
        
        # Initialize conversion engines
        self._init_conversion_engines()
    
    def _init_conversion_engines(self) -> None:
        """Initialize specialized conversion engines"""        self.engines = {
            'lossless': self._create_lossless_engine(),
            'lossy': self._create_lossy_engine(), 
            'professional': self._create_professional_engine(),
            'streaming': self._create_streaming_engine()
        }
    
    def _create_lossless_engine(self) -> 'LosslessEngine':
        """Create engine for lossless format conversions"""        from .engines.lossless import LosslessEngine
        return LosslessEngine(self.config)
    
    def _create_lossy_engine(self) -> 'LossyEngine':
        """Create engine for lossy format conversions"""        from .engines.lossy import LossyEngine
        return LossyEngine(self.config)
    
    def _create_professional_engine(self) -> 'ProfessionalEngine':
        """Create engine for professional format conversions"""        from .engines.professional import ProfessionalEngine
        return ProfessionalEngine(self.config)
    
    def _create_streaming_engine(self) -> 'StreamingEngine':
        """Create engine for streaming format conversions"""        from .engines.streaming import StreamingEngine
        return StreamingEngine(self.config)
    
    async def convert_audio(self, 
                          request: ConversionRequest) -> ConversionResult:
        """        Convert audio file to specified format with professional quality
        
        Args:
            request: Conversion request with all parameters
            
        Returns:
            ConversionResult with detailed processing information
        """        start_time = datetime.now()
        conversion_id = self._generate_conversion_id()
        
        try:
            # Validate request
            await self._validate_request(request)
            
            # Load and analyze input audio
            audio_data, sample_rate, metadata = await self._load_audio_with_metadata(
                request.input_path
            )
            
            # Select optimal conversion engine
            engine = await self._select_conversion_engine(request, audio_data, sample_rate)
            
            # Optimize conversion parameters
            optimized_params = await self._optimize_conversion_parameters(
                request, audio_data, sample_rate, metadata
            )
            
            # Execute conversion
            converted_data, conversion_info = await engine.convert(
                audio_data, sample_rate, metadata, optimized_params
            )
            
            # Apply post-processing
            final_data = await self._apply_post_processing(
                converted_data, optimized_params
            )
            
            # Save converted audio
            output_path = await self._save_converted_audio(
                final_data, optimized_params, metadata, request.output_path
            )
            
            # Calculate quality metrics
            quality_metrics = await self.quality_controller.calculate_metrics(
                audio_data, final_data, sample_rate, optimized_params.target_sample_rate
            )
            
            # Generate conversion result
            result = ConversionResult(
                conversion_id=conversion_id,
                success=True,
                output_path=output_path,
                format_specification=optimized_params.format_spec,
                quality_profile=optimized_params.quality_profile,
                quality_metrics=quality_metrics,
                processing_time=datetime.now() - start_time,
                conversion_info=conversion_info,
                metadata_preserved=metadata
            )
            
            # Record metrics
            await self.metrics.record_conversion_success(result)
            
            return result
            
        except Exception as e:
            error_result = ConversionResult(
                conversion_id=conversion_id,
                success=False,
                error_message=str(e),
                processing_time=datetime.now() - start_time
            )
            
            await self.metrics.record_conversion_failure(error_result)
            logger.error(f"Conversion {conversion_id} failed: {e}")
            
            return error_result
    
    async def convert_batch(self, 
                          requests: List[ConversionRequest]) -> List[ConversionResult]:
        """        Convert multiple audio files with intelligent batch processing
        
        Args:
            requests: List of conversion requests
            
        Returns:
            List of conversion results
        """        batch_id = self._generate_batch_id()
        start_time = datetime.now()
        
        logger.info(f"Starting batch conversion {batch_id} with {len(requests)} files")
        
        try:
            # Organize requests by similarity for optimization
            organized_requests = await self._organize_batch_requests(requests)
            
            # Process in optimized batches
            results = []
            for batch in organized_requests:
                batch_results = await self._process_batch_chunk(batch)
                results.extend(batch_results)
            
            # Compile batch statistics
            success_count = sum(1 for r in results if r.success)
            failure_count = len(results) - success_count
            
            logger.info(f"Batch {batch_id} completed: {success_count} success, {failure_count} failures")
            
            return results
            
        except Exception as e:
            logger.error(f"Batch conversion {batch_id} failed: {e}")
            return [
                ConversionResult(
                    conversion_id=f"{batch_id}_{i}",
                    success=False,
                    error_message=f"Batch processing failed: {e}",
                    processing_time=datetime.now() - start_time
                )
                for i, _ in enumerate(requests)
            ]
    
    async def get_optimal_format(self, 
                               input_path: Path,
                               use_case: str = "general") -> FormatSpecification:
        """        Analyze audio and recommend optimal format for specific use case
        
        Args:
            input_path: Path to input audio file
            use_case: Target use case (streaming, archival, professional, etc.)
            
        Returns:
            Optimal format specification
        """        # Load and analyze audio
        audio_data, sample_rate, metadata = await self._load_audio_with_metadata(input_path)
        
        # Analyze audio characteristics
        audio_analysis = await self._analyze_audio_characteristics(
            audio_data, sample_rate
        )
        
        # Get use case requirements
        use_case_requirements = self._get_use_case_requirements(use_case)
        
        # Calculate optimal format
        optimal_format = await self._calculate_optimal_format(
            audio_analysis, use_case_requirements, metadata
        )
        
        return optimal_format
    
    async def estimate_conversion_time(self, 
                                     request: ConversionRequest) -> timedelta:
        """        Estimate conversion time based on audio characteristics and system load
        
        Args:
            request: Conversion request
            
        Returns:
            Estimated conversion time
        """        # Analyze input file size and format
        file_stats = await self._analyze_file_stats(request.input_path)
        
        # Get system load metrics
        system_load = await self.metrics.get_system_load()
        
        # Calculate time estimate based on historical data
        base_time = self._calculate_base_conversion_time(file_stats, request)
        load_factor = self._calculate_load_factor(system_load)
        
        estimated_time = base_time * load_factor
        
        return estimated_time
    
    # Private methods for internal processing
    
    def _generate_conversion_id(self) -> str:
        """Generate unique conversion identifier"""        return f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{np.random.randint(1000, 9999)}"
    
    def _generate_batch_id(self) -> str:
        """Generate unique batch identifier"""        return f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{np.random.randint(1000, 9999)}"
    
    async def _validate_request(self, request: ConversionRequest) -> None:
        """Validate conversion request parameters"""        if not request.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {request.input_path}")
        
        if not self.format_registry.is_format_supported(request.output_format):
            raise UnsupportedFormatError(f"Output format not supported: {request.output_format}")
        
        # Additional validations...
    
    async def _load_audio_with_metadata(self, 
                                      input_path: Path) -> Tuple[np.ndarray, int, Dict]:
        """Load audio file with complete metadata extraction"""        try:
            # Try multiple loading methods for maximum compatibility
            audio_data, sample_rate = await self._load_audio_robust(input_path)
            
            # Extract metadata
            metadata = await self.metadata_manager.extract_metadata(input_path)
            
            return audio_data, sample_rate, metadata
            
        except Exception as e:
            raise ConversionError(f"Failed to load audio file {input_path}: {e}")
    
    async def _load_audio_robust(self, input_path: Path) -> Tuple[np.ndarray, int]:
        """Load audio with multiple fallback methods"""        methods = [
            self._load_with_soundfile,
            self._load_with_librosa,
            self._load_with_ffmpeg
        ]
        
        last_error = None
        for method in methods:
            try:
                return await method(input_path)
            except Exception as e:
                last_error = e
                continue
        
        raise ConversionError(f"All audio loading methods failed. Last error: {last_error}")
    
    async def _load_with_soundfile(self, input_path: Path) -> Tuple[np.ndarray, int]:
        """Load audio using soundfile library"""        data, sr = sf.read(str(input_path))
        return data, sr
    
    async def _load_with_librosa(self, input_path: Path) -> Tuple[np.ndarray, int]:
        """Load audio using librosa library"""        data, sr = librosa.load(str(input_path), sr=None, mono=False)
        return data, sr
    
    async def _load_with_ffmpeg(self, input_path: Path) -> Tuple[np.ndarray, int]:
        """Load audio using FFmpeg as fallback"""        with tempfile.NamedTemporaryFile(suffix='.wav') as temp_file:
            # Convert to WAV using FFmpeg
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-f', 'wav', temp_file.name, '-y'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            await process.wait()
            
            if process.returncode != 0:
                raise ConversionError("FFmpeg conversion failed")
            
            # Load converted file
            data, sr = sf.read(temp_file.name)
            return data, sr
    
    async def _select_conversion_engine(self, 
                                      request: ConversionRequest,
                                      audio_data: np.ndarray,
                                      sample_rate: int) -> Any:
        """Select optimal conversion engine based on requirements"""        # Analyze audio characteristics
        is_high_quality = sample_rate >= 48000 or audio_data.dtype == np.float64
        is_professional = request.quality_profile.name in ['professional', 'mastering']
        
        # Select engine based on requirements
        if is_professional:
            return self.engines['professional']
        elif request.output_format in ['wav', 'flac', 'aiff']:
            return self.engines['lossless']
        elif request.streaming_optimized:
            return self.engines['streaming']
        else:
            return self.engines['lossy']
    
    async def _optimize_conversion_parameters(self,
                                            request: ConversionRequest,
                                            audio_data: np.ndarray,
                                            sample_rate: int,
                                            metadata: Dict) -> 'OptimizedParameters':
        """Optimize conversion parameters based on audio analysis"""        from .optimization import ParameterOptimizer
        
        optimizer = ParameterOptimizer(self.config)
        return await optimizer.optimize(request, audio_data, sample_rate, metadata)
    
    async def _apply_post_processing(self,
                                   audio_data: np.ndarray,
                                   params: 'OptimizedParameters') -> np.ndarray:
        """Apply post-processing effects and optimizations"""        processed_data = audio_data.copy()
        
        # Apply processing chain based on parameters
        if params.apply_normalization:
            processed_data = await self._normalize_audio(processed_data)
        
        if params.apply_limiter:
            processed_data = await self._apply_limiter(processed_data)
        
        if params.apply_dithering:
            processed_data = await self._apply_dithering(processed_data, params.target_bit_depth)
        
        return processed_data
    
    async def _save_converted_audio(self,
                                  audio_data: np.ndarray,
                                  params: 'OptimizedParameters',
                                  metadata: Dict,
                                  output_path: Path) -> Path:
        """Save converted audio with metadata preservation"""        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save audio data
            sf.write(
                str(output_path),
                audio_data,
                params.target_sample_rate,
                subtype=params.format_spec.subtype
            )
            
            # Inject metadata
            await self.metadata_manager.inject_metadata(output_path, metadata)
            
            return output_path
            
        except Exception as e:
            raise ConversionError(f"Failed to save converted audio: {e}")
    
    # Additional utility methods...
    
    async def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply audio normalization"""        peak = np.max(np.abs(audio_data))
        if peak > 0:
            return audio_data / peak * 0.95
        return audio_data
    
    async def _apply_limiter(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply soft limiter to prevent clipping"""        # Simple soft limiter implementation
        threshold = 0.95
        ratio = 0.1
        
        mask = np.abs(audio_data) > threshold
        limited_data = audio_data.copy()
        
        limited_data[mask] = threshold + (audio_data[mask] - threshold) * ratio
        
        return limited_data
    
    async def _apply_dithering(self, audio_data: np.ndarray, bit_depth: int) -> np.ndarray:
        """Apply dithering for bit depth reduction"""        if bit_depth >= 24:
            return audio_data
        
        # Add shaped dithering noise
        noise_level = 1.0 / (2 ** bit_depth)
        dither_noise = np.random.triangular(-noise_level, 0, noise_level, audio_data.shape)
        
        return audio_data + dither_noise


class ConversionEngine:
    """    Advanced Conversion Engine Manager
    
    Manages multiple specialized conversion engines and provides
    intelligent routing and optimization capabilities.
    """    
    def __init__(self, config: ConversionConfig):
        """Initialize conversion engine manager"""        self.config = config
        self.converters = {}
        self.load_balancer = self._create_load_balancer()
        
    async def process_conversion(self, 
                               request: ConversionRequest) -> ConversionResult:
        """Process conversion request through optimal engine"""        # Select optimal converter
        converter = await self._select_converter(request)
        
        # Execute conversion
        return await converter.convert_audio(request)
    
    def _create_load_balancer(self) -> 'LoadBalancer':
        """Create load balancer for conversion engines"""        from .load_balancing import LoadBalancer
        return LoadBalancer(self.config)
    
    async def _select_converter(self, request: ConversionRequest) -> AudioFormatConverter:
        """Select optimal converter based on request and system load"""        return await self.load_balancer.get_optimal_converter(request)


class BatchConverter:
    """    Professional Batch Audio Converter
    
    Optimized for high-volume batch processing with intelligent
    resource management and parallel processing capabilities.
    """    
    def __init__(self, 
                 config: ConversionConfig,
                 max_concurrent: int = 4):
        """Initialize batch converter"""        self.config = config
        self.max_concurrent = max_concurrent
        self.converter = AudioFormatConverter(config)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def convert_directory(self,
                              input_dir: Path,
                              output_dir: Path,
                              output_format: str,
                              recursive: bool = True) -> List[ConversionResult]:
        """Convert all audio files in directory"""        # Find all audio files
        audio_files = await self._find_audio_files(input_dir, recursive)
        
        # Create conversion requests
        requests = [
            ConversionRequest(
                input_path=file,
                output_path=output_dir / f"{file.stem}.{output_format}",
                output_format=output_format
            )
            for file in audio_files
        ]
        
        # Process batch
        return await self.converter.convert_batch(requests)
    
    async def _find_audio_files(self, 
                              directory: Path, 
                              recursive: bool = True) -> List[Path]:
        """Find all supported audio files in directory"""        audio_extensions = self.config.supported_input_formats
        audio_files = []
        
        pattern = "**/*" if recursive else "*"
        
        for ext in audio_extensions:
            files = list(directory.glob(f"{pattern}.{ext}"))
            audio_files.extend(files)
        
        return sorted(audio_files)


# Export main classes
__all__ = [
    'AudioFormatConverter',
    'ConversionEngine', 
    'BatchConverter'
]
