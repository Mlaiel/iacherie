"""
High-level services for audio separation orchestration.

This module provides business logic services that coordinate between
different separation models, processors, and utilities to deliver
complete separation workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - Unauthorized use strictly prohibited
License: Proprietary - Contact for licensing

 WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or modification is strictly
prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

from ...core.config import get_settings
from ...core.exceptions import AudioProcessingError, ServiceError
from ...utils.logging import get_logger
from .core import SeparationEngine, SeparationConfig, SeparationModel, SeparationQuality, OutputFormat
from .models import VocalSeparator, InstrumentSeparator, DrumSeparator, BassSeparator, SeparationResult, create_separator
from .processors import AudioProcessor, StemProcessor, QualityAnalyzer, ProcessingConfig, ProcessingResult
from .utils import AudioValidator, FormatConverter, MetadataExtractor, AudioMetadata, ValidationResult

logger = get_logger(__name__)


@dataclass
class SeparationRequest:
    """Request object for separation operations."""
    audio_path: Optional[Path] = None
    audio_data: Optional[np.ndarray] = None
    sample_rate: Optional[int] = None
    separation_types: List[str] = field(default_factory=lambda: ["vocal"])
    quality: SeparationQuality = SeparationQuality.HIGH
    output_format: OutputFormat = OutputFormat.WAV
    output_directory: Optional[Path] = None
    include_processing: bool = True
    include_analysis: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SeparationResponse:
    """Response object for separation operations."""
    success: bool
    request_id: str
    stems: Dict[str, np.ndarray] = field(default_factory=dict)
    output_files: Dict[str, Path] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class SeparationService:
    """Main service for audio separation orchestration."""
    
    def __init__(self, config: Optional[SeparationConfig] = None,
                 processing_config: Optional[ProcessingConfig] = None):
        self.config = config or SeparationConfig()
        self.processing_config = processing_config or ProcessingConfig()
        
        # Initialize components
        self.separation_engine = SeparationEngine(self.config)
        self.audio_processor = AudioProcessor(self.processing_config)
        self.stem_processor = StemProcessor(self.processing_config)
        self.quality_analyzer = QualityAnalyzer(self.processing_config)
        self.validator = AudioValidator()
        self.converter = FormatConverter()
        self.metadata_extractor = MetadataExtractor()
        
        # Service state
        self.active_requests: Dict[str, asyncio.Task] = {}
        self.request_counter = 0
        
        logger.info("SeparationService initialized")
    
    async def separate_audio(self, request: SeparationRequest) -> SeparationResponse:
        """Main entry point for audio separation."""
        # Generate unique request ID
        self.request_counter += 1
        request_id = f"sep_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.request_counter:04d}"
        
        logger.info(f"Starting separation request {request_id}")
        start_time = asyncio.get_event_loop().time()
        
        response = SeparationResponse(
            success=False,
            request_id=request_id
        )
        
        try:
            # Input validation and loading
            audio_data, sample_rate, validation_result = await self._prepare_audio_input(request)
            
            if validation_result and not validation_result.is_valid:
                response.errors.extend(validation_result.issues)
                return response
            
            # Extract metadata if requested
            if request.include_analysis and request.audio_path:
                metadata = await self.metadata_extractor.extract_comprehensive_metadata(request.audio_path)
                response.metadata.update(metadata)
            
            # Perform separation
            separation_results = await self._perform_separation(
                audio_data, sample_rate, request.separation_types
            )
            
            # Collect stems
            stems = {}
            for sep_type, result in separation_results.items():
                stems.update(result.source_stems)
                response.quality_metrics[sep_type] = result.quality_scores
            
            response.stems = stems
            
            # Apply post-processing if requested
            if request.include_processing and stems:
                processed_stems = await self.stem_processor.process(stems)
                
                # Replace with processed versions
                for stem_name, processing_result in processed_stems.items():
                    if processing_result and processing_result.processed_audio is not None:
                        response.stems[stem_name] = processing_result.processed_audio
                        
                        # Update quality metrics
                        if stem_name not in response.quality_metrics:
                            response.quality_metrics[stem_name] = {}
                        response.quality_metrics[stem_name].update(processing_result.quality_metrics)
            
            # Quality analysis if requested
            if request.include_analysis and response.stems:
                quality_analysis = await self.quality_analyzer.process(
                    stems=response.stems,
                    reference=audio_data
                )
                response.quality_metrics.update(quality_analysis)
            
            # Export stems if output directory specified
            if request.output_directory and response.stems:
                output_files = await self.converter.batch_convert(
                    audio_dict=response.stems,
                    sample_rate=sample_rate,
                    output_format=request.output_format,
                    output_directory=request.output_directory,
                    quality=request.quality
                )
                response.output_files = {k: v for k, v in output_files.items() if v is not None}
                
                # Export metadata
                if response.metadata:
                    metadata_path = request.output_directory / f"{request_id}_metadata.json"
                    await self.metadata_extractor.export_metadata(response.metadata, metadata_path)
            
            response.success = True
            response.processing_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Separation request {request_id} completed successfully in {response.processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Separation request {request_id} failed: {str(e)}")
            response.errors.append(str(e))
            response.processing_time = asyncio.get_event_loop().time() - start_time
        
        return response
    
    async def separate_audio_async(self, request: SeparationRequest) -> str:
        """Start asynchronous separation process."""
        request_id = f"async_sep_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.request_counter:04d}"
        self.request_counter += 1
        
        # Start separation task
        task = asyncio.create_task(self.separate_audio(request))
        self.active_requests[request_id] = task
        
        logger.info(f"Started async separation request {request_id}")
        return request_id
    
    async def get_separation_status(self, request_id: str) -> Dict[str, Any]:
        """Get status of separation request."""
        if request_id not in self.active_requests:
            return {"status": "not_found", "error": "Request ID not found"}
        
        task = self.active_requests[request_id]
        
        if task.done():
            try:
                result = await task
                # Clean up completed task
                del self.active_requests[request_id]
                
                return {
                    "status": "completed",
                    "success": result.success,
                    "processing_time": result.processing_time,
                    "stems_count": len(result.stems),
                    "output_files": list(result.output_files.keys()) if result.output_files else [],
                    "errors": result.errors,
                    "warnings": result.warnings
                }
            except Exception as e:
                del self.active_requests[request_id]
                return {"status": "failed", "error": str(e)}
        else:
            return {"status": "processing", "message": "Separation in progress"}
    
    async def _prepare_audio_input(self, request: SeparationRequest) -> Tuple[np.ndarray, int, Optional[ValidationResult]]:
        """Prepare and validate audio input."""
        validation_result = None
        
        if request.audio_path:
            # Load from file
            validation_result = await self.validator.validate_file(request.audio_path)
            
            if not validation_result.is_valid:
                raise AudioProcessingError(f"Invalid audio file: {', '.join(validation_result.issues)}")
            
            # Load audio data
            import librosa
            audio_data, sample_rate = librosa.load(str(request.audio_path), sr=None)
            
        elif request.audio_data is not None and request.sample_rate:
            # Use provided audio data
            audio_data = request.audio_data
            sample_rate = request.sample_rate
            
            # Validate audio data
            validation_issues = await self.validator.validate_audio_data(audio_data, sample_rate)
            if validation_issues:
                raise AudioProcessingError(f"Invalid audio data: {', '.join(validation_issues)}")
        
        else:
            raise AudioProcessingError("Either audio_path or (audio_data + sample_rate) must be provided")
        
        return audio_data, sample_rate, validation_result
    
    async def _perform_separation(self, audio: np.ndarray, sample_rate: int,
                                 separation_types: List[str]) -> Dict[str, SeparationResult]:
        """Perform the actual separation using specified types."""
        results = {}
        
        for sep_type in separation_types:
            try:
                logger.debug(f"Starting {sep_type} separation")
                
                # Create appropriate separator
                separator = create_separator(sep_type)
                
                # Load model if not already loaded
                if not separator.is_loaded:
                    await separator.load_model()
                
                # Perform separation
                result = await separator.separate(audio, sample_rate)
                results[sep_type] = result
                
                logger.debug(f"Completed {sep_type} separation in {result.processing_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Failed to perform {sep_type} separation: {str(e)}")
                # Create empty result for failed separation
                results[sep_type] = SeparationResult(
                    source_stems={f"{sep_type}_error": np.zeros_like(audio)},
                    quality_scores={f"{sep_type}_error": 0.0},
                    processing_time=0.0,
                    model_used=f"{sep_type}_failed",
                    sample_rate=sample_rate,
                    metadata={"error": str(e)}
                )
        
        return results
    
    async def cleanup_request(self, request_id: str) -> bool:
        """Clean up resources for a specific request."""
        if request_id in self.active_requests:
            task = self.active_requests[request_id]
            if not task.done():
                task.cancel()
            del self.active_requests[request_id]
            logger.info(f"Cleaned up request {request_id}")
            return True
        return False
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status and statistics."""



        return {
            "service": "SeparationService",
            "status": "running",
            "active_requests": len(self.active_requests),
            "total_requests_processed": self.request_counter,
            "supported_separation_types": ["vocal", "instrument", "drum", "bass"],
            "supported_formats": [f.value for f in OutputFormat],
            "quality_levels": [q.value for q in SeparationQuality],
            "timestamp": datetime.now().isoformat()
        }


class BatchProcessor:
    """Service for batch processing multiple audio files."""
    
    def __init__(self, separation_service: SeparationService,
                 max_concurrent: int = 4):
        self.separation_service = separation_service
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def process_batch(self, file_paths: List[Path],
                          separation_types: List[str] = None,
                          output_directory: Optional[Path] = None,
                          quality: SeparationQuality = SeparationQuality.HIGH,
                          output_format: OutputFormat = OutputFormat.WAV) -> Dict[str, SeparationResponse]:
        """Process multiple files in batch."""
        separation_types = separation_types or ["vocal"]
        results = {}
        
        # Create tasks for all files
        tasks = []
        for file_path in file_paths:
            request = SeparationRequest(
                audio_path=file_path,
                separation_types=separation_types,
                quality=quality,
                output_format=output_format,
                output_directory=output_directory / file_path.stem if output_directory else None,
                include_processing=True,
                include_analysis=True
            )
            
            task = self._process_single_file(request, file_path.name)
            tasks.append(task)
        
        # Execute with concurrency limit
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for i, (file_path, result) in enumerate(zip(file_paths, batch_results)):
            if isinstance(result, Exception):
                logger.error(f"Batch processing failed for {file_path}: {str(result)}")
                results[file_path.name] = SeparationResponse(
                    success=False,
                    request_id=f"batch_error_{i}",
                    errors=[str(result)]
                )
            else:
                results[file_path.name] = result
        
        return results
    
    async def _process_single_file(self, request: SeparationRequest, filename: str) -> SeparationResponse:
        """Process a single file with semaphore control."""
        async with self.semaphore:
            logger.debug(f"Processing batch file: {filename}")
            return await self.separation_service.separate_audio(request)
    
    async def process_directory(self, directory_path: Path,
                               file_patterns: List[str] = None,
                               **kwargs) -> Dict[str, SeparationResponse]:
        """Process all audio files in a directory."""
        file_patterns = file_patterns or ["*.wav", "*.mp3", "*.flac", "*.aac", "*.ogg"]
        
        # Find all matching files
        audio_files = []
        for pattern in file_patterns:
            audio_files.extend(directory_path.glob(pattern))
        
        if not audio_files:
            logger.warning(f"No audio files found in {directory_path}")
            return {}
        
        logger.info(f"Found {len(audio_files)} audio files for batch processing")
        
        return await self.process_batch(audio_files, **kwargs)


class RealtimeProcessor:
    """Service for real-time audio separation processing."""
    
    def __init__(self, separation_service: SeparationService,
                 buffer_size: int = 4096,
                 overlap: float = 0.25):
        self.separation_service = separation_service
        self.buffer_size = buffer_size
        self.overlap = overlap
        self.hop_size = int(buffer_size * (1 - overlap))
        
        # Streaming state
        self.is_streaming = False
        self.audio_buffer = np.array([])
        self.sample_rate = 44100
        self.separators = {}
        self.callbacks = {}
        
    async def start_streaming(self, separation_types: List[str],
                            sample_rate: int = 44100,
                            callback: Optional[Callable] = None) -> None:
        """Start real-time streaming separation."""
        if self.is_streaming:
            raise ServiceError("Streaming already active")
        
        self.sample_rate = sample_rate
        self.is_streaming = True
        
        # Initialize separators
        for sep_type in separation_types:
            separator = create_separator(sep_type)
            await separator.load_model()
            self.separators[sep_type] = separator
        
        if callback:
            self.callbacks['default'] = callback
            
        logger.info(f"Started real-time streaming with {separation_types}")
    
    async def process_audio_chunk(self, audio_chunk: np.ndarray) -> Dict[str, np.ndarray]:
        """Process a chunk of audio in real-time."""
        if not self.is_streaming:
            raise ServiceError("Streaming not active")
        
        # Add to buffer
        self.audio_buffer = np.concatenate([self.audio_buffer, audio_chunk])
        
        results = {}
        
        # Process full buffers
        while len(self.audio_buffer) >= self.buffer_size:
            # Extract buffer
            buffer = self.audio_buffer[:self.buffer_size]
            
            # Process with each separator
            for sep_type, separator in self.separators.items():
                try:
                    result = await separator.separate(buffer, self.sample_rate)
                    
                    # Extract main stem (simplified for real-time)
                    if result.source_stems:
                        main_stem_name = list(result.source_stems.keys())[0]
                        results[sep_type] = result.source_stems[main_stem_name]
                    
                except Exception as e:
                    logger.error(f"Real-time separation failed for {sep_type}: {str(e)}")
                    results[sep_type] = np.zeros_like(buffer)
            
            # Advance buffer
            self.audio_buffer = self.audio_buffer[self.hop_size:]
            
            # Call callbacks
            for callback in self.callbacks.values():
                try:
                    await callback(results)
                except Exception as e:
                    logger.error(f"Callback failed: {str(e)}")
        
        return results
    
    async def stop_streaming(self) -> None:
        """Stop real-time streaming."""
        self.is_streaming = False
        self.audio_buffer = np.array([])
        self.separators.clear()
        self.callbacks.clear()
        
        logger.info("Stopped real-time streaming")
    
    def add_callback(self, name: str, callback: Callable) -> None:
        """Add callback for processed audio."""
        self.callbacks[name] = callback
    
    def remove_callback(self, name: str) -> None:
        """Remove callback."""
        if name in self.callbacks:
            del self.callbacks[name]
    
    def get_streaming_status(self) -> Dict[str, Any]:
        """Get real-time streaming status."""



        return {
            "is_streaming": self.is_streaming,
            "buffer_size": self.buffer_size,
            "hop_size": self.hop_size,
            "sample_rate": self.sample_rate,
            "active_separators": list(self.separators.keys()),
            "buffer_fill": len(self.audio_buffer),
            "callbacks_count": len(self.callbacks)
        }


# Factory functions for service creation
def create_separation_service(config: Optional[Dict[str, Any]] = None) -> SeparationService:
    """Factory function to create configured separation service."""
    if config:
        separation_config = SeparationConfig(**config.get('separation', {}))
        processing_config = ProcessingConfig(**config.get('processing', {}))
    else:
        separation_config = SeparationConfig()
        processing_config = ProcessingConfig()
    
    return SeparationService(separation_config, processing_config)


def create_batch_processor(separation_service: Optional[SeparationService] = None,
                          max_concurrent: int = 4) -> BatchProcessor:
    """Factory function to create batch processor."""
    if separation_service is None:
        separation_service = create_separation_service()
    
    return BatchProcessor(separation_service, max_concurrent)


def create_realtime_processor(separation_service: Optional[SeparationService] = None,
                            buffer_size: int = 4096,
                            overlap: float = 0.25) -> RealtimeProcessor:
    """Factory function to create real-time processor."""
    if separation_service is None:
        separation_service = create_separation_service()
    
    return RealtimeProcessor(separation_service, buffer_size, overlap)


# Service registry for dependency injection
class ServiceRegistry:
    """Registry for managing separation service instances."""
    
    _instances = {}
    
    @classmethod
    def register(cls, name: str, service: Any) -> None:
        """Register a service instance."""
        cls._instances[name] = service
        logger.debug(f"Registered service: {name}")
    
    @classmethod
    def get(cls, name: str) -> Any:
        """Get a registered service instance."""
        if name not in cls._instances:
            raise ServiceError(f"Service not registered: {name}")
        return cls._instances[name]
    
    @classmethod
    def unregister(cls, name: str) -> bool:
        """Unregister a service instance."""
        if name in cls._instances:
            del cls._instances[name]
            logger.debug(f"Unregistered service: {name}")
            return True
        return False
    
    @classmethod
    def list_services(cls) -> List[str]:
        """List all registered services."""



        return list(cls._instances.keys())
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered services."""
        cls._instances.clear()
        logger.debug("Cleared all registered services")


# Default service instances
def setup_default_services() -> None:
    """Setup default service instances in registry."""
    # Main separation service
    separation_service = create_separation_service()
    ServiceRegistry.register("separation", separation_service)
    
    # Batch processor
    batch_processor = create_batch_processor(separation_service)
    ServiceRegistry.register("batch", batch_processor)
    
    # Real-time processor
    realtime_processor = create_realtime_processor(separation_service)
    ServiceRegistry.register("realtime", realtime_processor)
    
    logger.info("Default services registered in ServiceRegistry")
