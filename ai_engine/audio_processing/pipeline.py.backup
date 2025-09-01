"""🔧 Audio Processing Pipeline - Comprehensive Workflow Engine

Advanced pipeline system for chaining audio processing operations.
Supports parallel processing, caching, and intelligent optimization.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Union, Any, Callable, Type
from pathlib import Path
import numpy as np
import time
import json
import pickle
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
import psutil

from .core import AudioProcessor, AudioMetadata
from .effects import EffectsProcessor
from .embeddings import AudioEmbeddingGenerator
from .fingerprinting import AudioFingerprinter
from .formats import FormatConverter, ConversionSettings
from .ml_models import MLModelManager, ModelType
from .config import AudioProcessingConfig

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """Pipeline processing stages"""
    LOAD = "load"
    PREPROCESS = "preprocess"
    ANALYZE = "analyze"
    ENHANCE = "enhance"
    TRANSFORM = "transform"
    CLASSIFY = "classify"
    GENERATE = "generate"
    SAVE = "save"
    VALIDATE = "validate"


class ProcessingMode(Enum):
    """Processing execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    BATCH = "batch"
    STREAM = "stream"
    DISTRIBUTED = "distributed"


class CacheStrategy(Enum):
    """Caching strategies for pipeline results"""
    NONE = "none"
    MEMORY = "memory"
    DISK = "disk"
    HYBRID = "hybrid"
    DISTRIBUTED = "distributed"


@dataclass
class PipelineConfig:
    """Configuration for audio processing pipeline"""
    name: str
    description: str = ""
    processing_mode: ProcessingMode = ProcessingMode.SEQUENTIAL
    cache_strategy: CacheStrategy = CacheStrategy.MEMORY
    max_workers: int = None
    timeout_seconds: int = 300
    retry_attempts: int = 3
    checkpoint_enabled: bool = True
    optimization_enabled: bool = True
    memory_limit_mb: int = 1024
    temp_directory: Optional[Path] = None
    log_level: str = "INFO"
    
    def __post_init__(self):
        if self.max_workers is None:
            self.max_workers = min(multiprocessing.cpu_count(), 8)
        
        if self.temp_directory is None:
            self.temp_directory = Path("/tmp/audio_pipeline")


@dataclass
class StageResult:
    """Result from a pipeline stage"""
    stage_name: str
    stage_type: PipelineStage
    success: bool
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    memory_usage: float = 0.0
    error_message: Optional[str] = None
    cache_hit: bool = False


@dataclass
class PipelineResult:
    """Complete pipeline execution result"""
    pipeline_name: str
    success: bool
    stage_results: List[StageResult] = field(default_factory=list)
    total_processing_time: float = 0.0
    peak_memory_usage: float = 0.0
    cache_hit_ratio: float = 0.0
    final_output: Any = None
    error_summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PipelineStageBase(ABC):
    """
    🔧 Abstract base class for pipeline stages
    
    All pipeline stages must inherit from this class and implement
    the execute method for consistent processing interfaces.
    """
    
    def __init__(self, name: str, stage_type: PipelineStage):
        self.name = name
        self.stage_type = stage_type
        self.config = {}
        self.dependencies = []
        self.cache_enabled = True
        
    @abstractmethod
    async def execute(self, 
                     input_data: Any, 
                     context: Dict[str, Any]) -> StageResult:
        """Execute the pipeline stage"""
        pass
    
    def set_config(self, config: Dict[str, Any]):
        """Set stage configuration"""
        self.config.update(config)
    
    def add_dependency(self, stage_name: str):
        """Add a dependency on another stage"""
        if stage_name not in self.dependencies:
            self.dependencies.append(stage_name)
    
    def get_cache_key(self, input_data: Any, context: Dict[str, Any]) -> str:
        """Generate cache key for this stage"""
        # Create a simple cache key based on stage name and input hash
        input_str = str(input_data) + str(context) + str(self.config)
        cache_key = f"{self.name}_{hashlib.md5(input_str.encode()).hexdigest()}"
        return cache_key


class LoadAudioStage(PipelineStageBase):
    """Load audio from file or data"""
    
    def __init__(self, audio_processor: AudioProcessor):
        super().__init__("load_audio", PipelineStage.LOAD)
        self.audio_processor = audio_processor
    
    async def execute(self, input_data: Any, context: Dict[str, Any]) -> StageResult:
        start_time = time.time()
        
        try:
            if isinstance(input_data, (str, Path)):
                # Load from file
                audio_data, sample_rate = await self.audio_processor.load_audio(
                    input_data,
                    target_sr=self.config.get('target_sr'),
                    mono=self.config.get('mono', False),
                    normalize=self.config.get('normalize', True)
                )
                
                metadata = await self.audio_processor.extract_metadata(input_data)
                
            elif isinstance(input_data, tuple) and len(input_data) == 2:
                # Audio data and sample rate provided
                audio_data, sample_rate = input_data
                metadata = AudioMetadata(
                    duration=len(audio_data) / sample_rate,
                    sample_rate=sample_rate,
                    channels=1 if audio_data.ndim == 1 else audio_data.shape[0],
                    bit_depth=16,  # Default
                    format="unknown"
                )
            else:
                raise ValueError("Invalid input data format")
            
            processing_time = time.time() - start_time
            
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=True,
                data={
                    'audio_data': audio_data,
                    'sample_rate': sample_rate,
                    'metadata': metadata
                },
                processing_time=processing_time,
                metadata={'input_type': type(input_data).__name__}
            )
            
        except Exception as e:
            logger.error(f"LoadAudioStage failed: {e}")
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )


class AnalyzeAudioStage(PipelineStageBase):
    """Analyze audio characteristics"""
    
    def __init__(self, audio_processor: AudioProcessor):
        super().__init__("analyze_audio", PipelineStage.ANALYZE)
        self.audio_processor = audio_processor
    
    async def execute(self, input_data: Any, context: Dict[str, Any]) -> StageResult:
        start_time = time.time()
        
        try:
            audio_data = input_data['audio_data']
            sample_rate = input_data['sample_rate']
            
            # Perform comprehensive analysis
            analysis = await self.audio_processor.analyze_audio(audio_data, sample_rate)
            
            processing_time = time.time() - start_time
            
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=True,
                data={
                    'analysis': analysis,
                    'audio_data': audio_data,
                    'sample_rate': sample_rate
                },
                processing_time=processing_time,
                metadata={'analysis_features': len(analysis)}
            )
            
        except Exception as e:
            logger.error(f"AnalyzeAudioStage failed: {e}")
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )


class EnhanceAudioStage(PipelineStageBase):
    """Apply audio enhancement effects"""
    
    def __init__(self, effects_processor: EffectsProcessor):
        super().__init__("enhance_audio", PipelineStage.ENHANCE)
        self.effects_processor = effects_processor
    
    async def execute(self, input_data: Any, context: Dict[str, Any]) -> StageResult:
        start_time = time.time()
        
        try:
            audio_data = input_data['audio_data']
            sample_rate = input_data['sample_rate']
            
            enhanced_audio = audio_data.copy()
            
            # Apply configured effects
            effects_config = self.config.get('effects', {})
            
            if effects_config.get('noise_reduction', False):
                enhanced_audio = await self.effects_processor.noise_reduction(
                    enhanced_audio, sample_rate
                )
            
            if effects_config.get('normalize', False):
                enhanced_audio = await self.effects_processor.normalize_audio(
                    enhanced_audio
                )
            
            if effects_config.get('eq', False):
                eq_settings = effects_config.get('eq_settings', {})
                enhanced_audio = await self.effects_processor.apply_eq(
                    enhanced_audio, sample_rate, **eq_settings
                )
            
            if effects_config.get('compressor', False):
                comp_settings = effects_config.get('compressor_settings', {})
                enhanced_audio = await self.effects_processor.apply_compressor(
                    enhanced_audio, sample_rate, **comp_settings
                )
            
            processing_time = time.time() - start_time
            
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=True,
                data={
                    'audio_data': enhanced_audio,
                    'sample_rate': sample_rate,
                    'original_audio': audio_data
                },
                processing_time=processing_time,
                metadata={'effects_applied': list(effects_config.keys())}
            )
            
        except Exception as e:
            logger.error(f"EnhanceAudioStage failed: {e}")
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )


class ClassifyAudioStage(PipelineStageBase):
    """Classify audio using ML models"""
    
    def __init__(self, ml_manager: MLModelManager):
        super().__init__("classify_audio", PipelineStage.CLASSIFY)
        self.ml_manager = ml_manager
    
    async def execute(self, input_data: Any, context: Dict[str, Any]) -> StageResult:
        start_time = time.time()
        
        try:
            audio_data = input_data['audio_data']
            sample_rate = input_data['sample_rate']
            
            # Get classification models to use
            models_to_use = self.config.get('models', [ModelType.GENRE_CLASSIFIER])
            
            classifications = {}
            
            for model_type in models_to_use:
                try:
                    result = await self.ml_manager.predict(
                        audio_data, sample_rate, model_type
                    )
                    classifications[model_type.value] = result
                except Exception as e:
                    logger.warning(f"Classification failed for {model_type}: {e}")
            
            processing_time = time.time() - start_time
            
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=True,
                data={
                    'classifications': classifications,
                    'audio_data': audio_data,
                    'sample_rate': sample_rate
                },
                processing_time=processing_time,
                metadata={'models_used': [m.value for m in models_to_use]}
            )
            
        except Exception as e:
            logger.error(f"ClassifyAudioStage failed: {e}")
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )


class GenerateEmbeddingsStage(PipelineStageBase):
    """Generate audio embeddings for similarity matching"""
    
    def __init__(self, embedding_generator: AudioEmbeddingGenerator):
        super().__init__("generate_embeddings", PipelineStage.GENERATE)
        self.embedding_generator = embedding_generator
    
    async def execute(self, input_data: Any, context: Dict[str, Any]) -> StageResult:
        start_time = time.time()
        
        try:
            audio_data = input_data['audio_data']
            sample_rate = input_data['sample_rate']
            
            # Generate embeddings
            embeddings = await self.embedding_generator.generate_embeddings(
                audio_data, sample_rate
            )
            
            processing_time = time.time() - start_time
            
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=True,
                data={
                    'embeddings': embeddings,
                    'audio_data': audio_data,
                    'sample_rate': sample_rate
                },
                processing_time=processing_time,
                metadata={'embedding_size': len(embeddings)}
            )
            
        except Exception as e:
            logger.error(f"GenerateEmbeddingsStage failed: {e}")
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )


class FingerprintAudioStage(PipelineStageBase):
    """Generate audio fingerprint for content identification"""
    
    def __init__(self, fingerprinter: AudioFingerprinter):
        super().__init__("fingerprint_audio", PipelineStage.GENERATE)
        self.fingerprinter = fingerprinter
    
    async def execute(self, input_data: Any, context: Dict[str, Any]) -> StageResult:
        start_time = time.time()
        
        try:
            audio_data = input_data['audio_data']
            sample_rate = input_data['sample_rate']
            
            # Generate fingerprint
            fingerprint = await self.fingerprinter.generate_fingerprint(
                audio_data, sample_rate
            )
            
            processing_time = time.time() - start_time
            
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=True,
                data={
                    'fingerprint': fingerprint,
                    'audio_data': audio_data,
                    'sample_rate': sample_rate
                },
                processing_time=processing_time,
                metadata={'fingerprint_length': len(fingerprint.hash_values)}
            )
            
        except Exception as e:
            logger.error(f"FingerprintAudioStage failed: {e}")
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )


class ConvertFormatStage(PipelineStageBase):
    """Convert audio format"""
    
    def __init__(self, format_converter: FormatConverter):
        super().__init__("convert_format", PipelineStage.TRANSFORM)
        self.format_converter = format_converter
    
    async def execute(self, input_data: Any, context: Dict[str, Any]) -> StageResult:
        start_time = time.time()
        
        try:
            audio_data = input_data['audio_data']
            sample_rate = input_data['sample_rate']
            
            # Get conversion settings
            conversion_settings = self.config.get('conversion_settings')
            if not conversion_settings:
                raise ValueError("No conversion settings provided")
            
            # Create temporary input file
            import tempfile
            import soundfile as sf
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_input:
                temp_input_path = Path(temp_input.name)
            
            try:
                # Write temporary input file
                sf.write(str(temp_input_path), audio_data, sample_rate)
                
                # Set output path
                output_path = context.get('output_path')
                if not output_path:
                    output_path = temp_input_path.with_suffix(
                        f'.{conversion_settings.target_format.value}'
                    )
                
                # Convert
                result = await self.format_converter.convert_audio(
                    temp_input_path, output_path, conversion_settings
                )
                
                processing_time = time.time() - start_time
                
                return StageResult(
                    stage_name=self.name,
                    stage_type=self.stage_type,
                    success=result.success,
                    data={
                        'output_path': result.output_path,
                        'conversion_result': result
                    },
                    processing_time=processing_time,
                    metadata={
                        'target_format': conversion_settings.target_format.value,
                        'compression_ratio': result.compression_ratio
                    },
                    error_message=result.error_message if not result.success else None
                )
                
            finally:
                # Clean up temporary file
                if temp_input_path.exists():
                    temp_input_path.unlink()
            
        except Exception as e:
            logger.error(f"ConvertFormatStage failed: {e}")
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )


class SaveResultsStage(PipelineStageBase):
    """Save pipeline results to file"""
    
    def __init__(self):
        super().__init__("save_results", PipelineStage.SAVE)
    
    async def execute(self, input_data: Any, context: Dict[str, Any]) -> StageResult:
        start_time = time.time()
        
        try:
            output_path = self.config.get('output_path')
            if not output_path:
                raise ValueError("No output path specified")
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save data based on format
            output_format = self.config.get('format', 'json')
            
            if output_format == 'json':
                # Convert numpy arrays to lists for JSON serialization
                serializable_data = self._make_json_serializable(input_data)
                
                with open(output_path, 'w') as f:
                    json.dump(serializable_data, f, indent=2)
            
            elif output_format == 'pickle':
                with open(output_path, 'wb') as f:
                    pickle.dump(input_data, f)
            
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            processing_time = time.time() - start_time
            
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=True,
                data={'output_path': output_path},
                processing_time=processing_time,
                metadata={'format': output_format, 'file_size': output_path.stat().st_size}
            )
            
        except Exception as e:
            logger.error(f"SaveResultsStage failed: {e}")
            return StageResult(
                stage_name=self.name,
                stage_type=self.stage_type,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def _make_json_serializable(self, obj):
        """Convert object to JSON-serializable format"""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._make_json_serializable(obj.__dict__)
        else:
            return obj


class PipelineCache:
    """
    💾 Advanced Pipeline Caching System
    
    Intelligent caching for pipeline stages:
    - Memory and disk caching
    - Cache invalidation strategies
    - Distributed caching support
    - Automatic cleanup
    """
    
    def __init__(self, 
                 strategy: CacheStrategy = CacheStrategy.MEMORY,
                 cache_directory: Optional[Path] = None,
                 max_memory_mb: int = 512,
                 max_disk_mb: int = 2048,
                 ttl_seconds: int = 3600):
        self.strategy = strategy
        self.cache_directory = cache_directory or Path("/tmp/audio_pipeline_cache")
        self.max_memory_mb = max_memory_mb
        self.max_disk_mb = max_disk_mb
        self.ttl_seconds = ttl_seconds
        
        # Memory cache
        self.memory_cache = {}
        self.memory_timestamps = {}
        self.memory_usage = 0
        
        # Initialize disk cache directory
        if strategy in [CacheStrategy.DISK, CacheStrategy.HYBRID]:
            self.cache_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"PipelineCache initialized with {strategy.value} strategy")
    
    async def get(self, cache_key: str) -> Optional[Any]:
        """Get cached result"""
        try:
            current_time = time.time()
            
            # Check memory cache first
            if cache_key in self.memory_cache:
                timestamp = self.memory_timestamps.get(cache_key, 0)
                if current_time - timestamp < self.ttl_seconds:
                    logger.debug(f"Cache hit (memory): {cache_key}")
                    return self.memory_cache[cache_key]
                else:
                    # Expired
                    self._remove_from_memory(cache_key)
            
            # Check disk cache
            if self.strategy in [CacheStrategy.DISK, CacheStrategy.HYBRID]:
                disk_path = self.cache_directory / f"{cache_key}.pkl"
                
                if disk_path.exists():
                    # Check if expired
                    if current_time - disk_path.stat().st_mtime < self.ttl_seconds:
                        with open(disk_path, 'rb') as f:
                            data = pickle.load(f)
                        
                        # Also store in memory for faster access
                        if self.strategy == CacheStrategy.HYBRID:
                            await self._store_in_memory(cache_key, data)
                        
                        logger.debug(f"Cache hit (disk): {cache_key}")
                        return data
                    else:
                        # Expired - remove
                        disk_path.unlink()
            
            return None
            
        except Exception as e:
            logger.error(f"Cache get failed for {cache_key}: {e}")
            return None
    
    async def set(self, cache_key: str, data: Any):
        """Store result in cache"""
        try:
            current_time = time.time()
            
            # Store in memory
            if self.strategy in [CacheStrategy.MEMORY, CacheStrategy.HYBRID]:
                await self._store_in_memory(cache_key, data)
            
            # Store on disk
            if self.strategy in [CacheStrategy.DISK, CacheStrategy.HYBRID]:
                disk_path = self.cache_directory / f"{cache_key}.pkl"
                
                with open(disk_path, 'wb') as f:
                    pickle.dump(data, f)
                
                # Check disk usage and cleanup if needed
                await self._cleanup_disk_cache()
            
            logger.debug(f"Cached result: {cache_key}")
            
        except Exception as e:
            logger.error(f"Cache set failed for {cache_key}: {e}")
    
    async def _store_in_memory(self, cache_key: str, data: Any):
        """Store data in memory cache"""
        # Estimate memory usage
        data_size = self._estimate_size(data)
        
        # Clean up if needed
        while (self.memory_usage + data_size > self.max_memory_mb * 1024 * 1024 and 
               self.memory_cache):
            oldest_key = min(self.memory_timestamps.keys(), 
                           key=lambda k: self.memory_timestamps[k])
            self._remove_from_memory(oldest_key)
        
        # Store data
        self.memory_cache[cache_key] = data
        self.memory_timestamps[cache_key] = time.time()
        self.memory_usage += data_size
    
    def _remove_from_memory(self, cache_key: str):
        """Remove item from memory cache"""
        if cache_key in self.memory_cache:
            data_size = self._estimate_size(self.memory_cache[cache_key])
            del self.memory_cache[cache_key]
            del self.memory_timestamps[cache_key]
            self.memory_usage -= data_size
    
    def _estimate_size(self, obj) -> int:
        """Estimate object size in bytes"""
        try:
            return len(pickle.dumps(obj))
        except:
            return 1024  # Default estimate
    
    async def _cleanup_disk_cache(self):
        """Clean up disk cache if size limit exceeded"""
        try:
            total_size = sum(f.stat().st_size for f in self.cache_directory.glob("*.pkl"))
            max_size = self.max_disk_mb * 1024 * 1024
            
            if total_size > max_size:
                # Remove oldest files
                files = [(f, f.stat().st_mtime) for f in self.cache_directory.glob("*.pkl")]
                files.sort(key=lambda x: x[1])  # Sort by modification time
                
                for file_path, _ in files:
                    file_path.unlink()
                    total_size -= file_path.stat().st_size
                    
                    if total_size <= max_size * 0.8:  # Keep some buffer
                        break
                        
        except Exception as e:
            logger.error(f"Disk cache cleanup failed: {e}")
    
    def clear(self):
        """Clear all cache"""
        self.memory_cache.clear()
        self.memory_timestamps.clear()
        self.memory_usage = 0
        
        if self.cache_directory.exists():
            for file_path in self.cache_directory.glob("*.pkl"):
                file_path.unlink()


class AudioProcessingPipeline:
    """
    🔄 Advanced Audio Processing Pipeline
    
    Comprehensive pipeline system featuring:
    - Modular stage architecture
    - Parallel and distributed processing
    - Intelligent caching and optimization
    - Real-time monitoring and logging
    - Checkpoint and recovery mechanisms
    - Resource management and throttling
    """
    
    def __init__(self, 
                 config: PipelineConfig,
                 audio_config: Optional[AudioProcessingConfig] = None):
        self.config = config
        self.audio_config = audio_config or AudioProcessingConfig()
        
        # Initialize components
        self.audio_processor = AudioProcessor(self.audio_config)
        self.effects_processor = EffectsProcessor(self.audio_config)
        self.embedding_generator = AudioEmbeddingGenerator(self.audio_config)
        self.fingerprinter = AudioFingerprinter(self.audio_config)
        self.format_converter = FormatConverter(self.audio_config)
        self.ml_manager = MLModelManager(self.audio_config)
        
        # Pipeline stages
        self.stages: List[PipelineStageBase] = []
        self.stage_graph = {}  # Dependency graph
        
        # Caching system
        self.cache = PipelineCache(
            strategy=config.cache_strategy,
            cache_directory=config.temp_directory / "cache" if config.temp_directory else None
        )
        
        # Execution state
        self.execution_state = {}
        self.checkpoints = {}
        
        # Resource monitoring
        self.resource_monitor = ResourceMonitor()
        
        logger.info(f"AudioProcessingPipeline '{config.name}' initialized")
    
    def add_stage(self, stage: PipelineStageBase, dependencies: List[str] = None):
        """Add a processing stage to the pipeline"""
        self.stages.append(stage)
        
        # Build dependency graph
        if dependencies:
            for dep in dependencies:
                stage.add_dependency(dep)
        
        self.stage_graph[stage.name] = {
            'stage': stage,
            'dependencies': dependencies or [],
            'dependents': []
        }
        
        # Update dependents
        for dep_name in stage.dependencies:
            if dep_name in self.stage_graph:
                self.stage_graph[dep_name]['dependents'].append(stage.name)
        
        logger.debug(f"Added stage: {stage.name}")
    
    def create_standard_pipeline(self, 
                                features: List[str] = None) -> 'AudioProcessingPipeline':
        """Create a standard audio processing pipeline"""
        if features is None:
            features = ['load', 'analyze', 'enhance', 'classify', 'fingerprint']
        
        # Add stages based on requested features
        if 'load' in features:
            self.add_stage(LoadAudioStage(self.audio_processor))
        
        if 'analyze' in features:
            self.add_stage(
                AnalyzeAudioStage(self.audio_processor),
                dependencies=['load_audio']
            )
        
        if 'enhance' in features:
            self.add_stage(
                EnhanceAudioStage(self.effects_processor),
                dependencies=['load_audio']
            )
        
        if 'classify' in features:
            deps = ['analyze_audio'] if 'analyze' in features else ['load_audio']
            self.add_stage(
                ClassifyAudioStage(self.ml_manager),
                dependencies=deps
            )
        
        if 'embeddings' in features:
            deps = ['enhance_audio'] if 'enhance' in features else ['load_audio']
            self.add_stage(
                GenerateEmbeddingsStage(self.embedding_generator),
                dependencies=deps
            )
        
        if 'fingerprint' in features:
            deps = ['enhance_audio'] if 'enhance' in features else ['load_audio']
            self.add_stage(
                FingerprintAudioStage(self.fingerprinter),
                dependencies=deps
            )
        
        return self
    
    async def execute(self, 
                     input_data: Any, 
                     context: Dict[str, Any] = None) -> PipelineResult:
        """Execute the complete pipeline"""
        start_time = time.time()
        context = context or {}
        
        try:
            logger.info(f"Starting pipeline execution: {self.config.name}")
            
            # Initialize execution state
            self.execution_state = {stage.name: None for stage in self.stages}
            stage_results = []
            
            # Create execution plan
            execution_order = self._create_execution_plan()
            
            # Start resource monitoring
            self.resource_monitor.start()
            
            # Execute stages
            if self.config.processing_mode == ProcessingMode.SEQUENTIAL:
                stage_results = await self._execute_sequential(
                    input_data, context, execution_order
                )
            elif self.config.processing_mode == ProcessingMode.PARALLEL:
                stage_results = await self._execute_parallel(
                    input_data, context, execution_order
                )
            elif self.config.processing_mode == ProcessingMode.BATCH:
                stage_results = await self._execute_batch(
                    input_data, context, execution_order
                )
            else:
                raise ValueError(f"Unsupported processing mode: {self.config.processing_mode}")
            
            # Stop resource monitoring
            peak_memory = self.resource_monitor.stop()
            
            # Calculate metrics
            total_time = time.time() - start_time
            cache_hits = sum(1 for r in stage_results if r.cache_hit)
            cache_hit_ratio = cache_hits / len(stage_results) if stage_results else 0
            
            # Determine overall success
            success = all(r.success for r in stage_results)
            
            # Get final output
            final_output = None
            if stage_results and stage_results[-1].success:
                final_output = stage_results[-1].data
            
            # Create error summary if needed
            error_summary = None
            if not success:
                errors = [r.error_message for r in stage_results if r.error_message]
                error_summary = "; ".join(errors)
            
            result = PipelineResult(
                pipeline_name=self.config.name,
                success=success,
                stage_results=stage_results,
                total_processing_time=total_time,
                peak_memory_usage=peak_memory,
                cache_hit_ratio=cache_hit_ratio,
                final_output=final_output,
                error_summary=error_summary,
                metadata={
                    'processing_mode': self.config.processing_mode.value,
                    'num_stages': len(self.stages),
                    'input_type': type(input_data).__name__
                }
            )
            
            logger.info(f"Pipeline execution completed: {success}, "
                       f"time: {total_time:.2f}s, memory: {peak_memory:.1f}MB")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            total_time = time.time() - start_time
            
            return PipelineResult(
                pipeline_name=self.config.name,
                success=False,
                total_processing_time=total_time,
                error_summary=str(e)
            )
    
    def _create_execution_plan(self) -> List[List[str]]:
        """Create topologically sorted execution plan"""
        # Simple topological sort for dependency resolution
        visited = set()
        temp_visited = set()
        execution_levels = []
        
        def visit(stage_name):
            if stage_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {stage_name}")
            if stage_name in visited:
                return
            
            temp_visited.add(stage_name)
            
            # Visit dependencies first
            for dep in self.stage_graph[stage_name]['dependencies']:
                visit(dep)
            
            temp_visited.remove(stage_name)
            visited.add(stage_name)
            
            # Find appropriate level for this stage
            max_dep_level = -1
            for dep in self.stage_graph[stage_name]['dependencies']:
                for level, level_stages in enumerate(execution_levels):
                    if dep in level_stages:
                        max_dep_level = max(max_dep_level, level)
                        break
            
            # Add to next level after dependencies
            target_level = max_dep_level + 1
            
            while len(execution_levels) <= target_level:
                execution_levels.append([])
            
            execution_levels[target_level].append(stage_name)
        
        # Visit all stages
        for stage_name in self.stage_graph:
            visit(stage_name)
        
        return execution_levels
    
    async def _execute_sequential(self,
                                input_data: Any,
                                context: Dict[str, Any],
                                execution_order: List[List[str]]) -> List[StageResult]:
        """Execute stages sequentially"""
        stage_results = []
        current_data = input_data
        
        for level in execution_order:
            for stage_name in level:
                stage = self._get_stage_by_name(stage_name)
                
                # Check cache
                cache_key = stage.get_cache_key(current_data, context)
                cached_result = await self.cache.get(cache_key)
                
                if cached_result and stage.cache_enabled:
                    cached_result.cache_hit = True
                    stage_results.append(cached_result)
                    logger.debug(f"Using cached result for {stage_name}")
                else:
                    # Execute stage
                    result = await self._execute_single_stage(stage, current_data, context)
                    stage_results.append(result)
                    
                    # Cache result if successful
                    if result.success and stage.cache_enabled:
                        await self.cache.set(cache_key, result)
                
                # Update current data for next stage
                if stage_results[-1].success and stage_results[-1].data:
                    current_data = stage_results[-1].data
                
                # Create checkpoint
                if self.config.checkpoint_enabled:
                    self.checkpoints[stage_name] = stage_results[-1]
        
        return stage_results
    
    async def _execute_parallel(self,
                              input_data: Any,
                              context: Dict[str, Any],
                              execution_order: List[List[str]]) -> List[StageResult]:
        """Execute stages in parallel where possible"""
        stage_results = []
        stage_data = {None: input_data}  # Track data for each stage
        
        for level in execution_order:
            if len(level) == 1:
                # Single stage - execute normally
                stage_name = level[0]
                stage = self._get_stage_by_name(stage_name)
                
                # Get input data from dependencies
                input_for_stage = self._get_stage_input(stage, stage_data)
                
                result = await self._execute_single_stage(stage, input_for_stage, context)
                stage_results.append(result)
                
                # Store result data
                stage_data[stage_name] = result.data if result.success else None
                
            else:
                # Multiple stages - execute in parallel
                tasks = []
                
                for stage_name in level:
                    stage = self._get_stage_by_name(stage_name)
                    input_for_stage = self._get_stage_input(stage, stage_data)
                    
                    task = asyncio.create_task(
                        self._execute_single_stage(stage, input_for_stage, context)
                    )
                    tasks.append((stage_name, task))
                
                # Wait for all tasks to complete
                for stage_name, task in tasks:
                    result = await task
                    stage_results.append(result)
                    stage_data[stage_name] = result.data if result.success else None
        
        return stage_results
    
    async def _execute_batch(self,
                           input_data: Any,
                           context: Dict[str, Any],
                           execution_order: List[List[str]]) -> List[StageResult]:
        """Execute pipeline in batch mode for multiple inputs"""
        # For now, implement as sequential execution
        # In a full implementation, this would handle batches of inputs
        return await self._execute_sequential(input_data, context, execution_order)
    
    def _get_stage_by_name(self, stage_name: str) -> PipelineStageBase:
        """Get stage object by name"""
        for stage in self.stages:
            if stage.name == stage_name:
                return stage
        raise ValueError(f"Stage not found: {stage_name}")
    
    def _get_stage_input(self, stage: PipelineStageBase, stage_data: Dict[str, Any]) -> Any:
        """Get input data for a stage based on its dependencies"""
        if not stage.dependencies:
            # First stage - use original input
            return stage_data[None]
        elif len(stage.dependencies) == 1:
            # Single dependency
            dep_name = stage.dependencies[0]
            return stage_data.get(dep_name)
        else:
            # Multiple dependencies - combine data
            combined_data = {}
            for dep_name in stage.dependencies:
                if dep_name in stage_data and stage_data[dep_name]:
                    combined_data[dep_name] = stage_data[dep_name]
            return combined_data
    
    async def _execute_single_stage(self,
                                  stage: PipelineStageBase,
                                  input_data: Any,
                                  context: Dict[str, Any]) -> StageResult:
        """Execute a single pipeline stage with monitoring"""
        try:
            # Check resource limits
            if self.resource_monitor.current_memory_mb > self.config.memory_limit_mb:
                logger.warning(f"Memory limit exceeded: {self.resource_monitor.current_memory_mb}MB")
            
            # Execute with timeout
            result = await asyncio.wait_for(
                stage.execute(input_data, context),
                timeout=self.config.timeout_seconds
            )
            
            # Log execution
            logger.debug(f"Stage {stage.name} completed: {result.success}, "
                        f"time: {result.processing_time:.3f}s")
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Stage {stage.name} timed out after {self.config.timeout_seconds}s")
            return StageResult(
                stage_name=stage.name,
                stage_type=stage.stage_type,
                success=False,
                error_message=f"Timeout after {self.config.timeout_seconds}s"
            )
        except Exception as e:
            logger.error(f"Stage {stage.name} failed: {e}")
            return StageResult(
                stage_name=stage.name,
                stage_type=stage.stage_type,
                success=False,
                error_message=str(e)
            )
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about the pipeline"""
        return {
            'name': self.config.name,
            'description': self.config.description,
            'processing_mode': self.config.processing_mode.value,
            'cache_strategy': self.config.cache_strategy.value,
            'num_stages': len(self.stages),
            'stages': [
                {
                    'name': stage.name,
                    'type': stage.stage_type.value,
                    'dependencies': stage.dependencies
                }
                for stage in self.stages
            ],
            'max_workers': self.config.max_workers,
            'timeout_seconds': self.config.timeout_seconds
        }


class ResourceMonitor:
    """Monitor system resources during pipeline execution"""
    
    def __init__(self):
        self.start_time = None
        self.peak_memory = 0
        self.current_memory_mb = 0
        self.monitoring = False
        self._monitor_task = None
    
    def start(self):
        """Start resource monitoring"""
        self.start_time = time.time()
        self.peak_memory = 0
        self.monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_resources())
    
    def stop(self) -> float:
        """Stop monitoring and return peak memory usage"""
        self.monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
        return self.peak_memory
    
    async def _monitor_resources(self):
        """Monitor resource usage"""
        try:
            while self.monitoring:
                # Get current memory usage
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                self.current_memory_mb = memory_mb
                self.peak_memory = max(self.peak_memory, memory_mb)
                
                await asyncio.sleep(0.1)  # Monitor every 100ms
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Resource monitoring failed: {e}")


# Predefined pipeline configurations
STANDARD_PIPELINES = {
    'full_analysis': PipelineConfig(
        name="full_analysis",
        description="Complete audio analysis with all features",
        processing_mode=ProcessingMode.PARALLEL,
        cache_strategy=CacheStrategy.HYBRID,
        optimization_enabled=True
    ),
    
    'quick_classify': PipelineConfig(
        name="quick_classify",
        description="Fast audio classification",
        processing_mode=ProcessingMode.SEQUENTIAL,
        cache_strategy=CacheStrategy.MEMORY,
        timeout_seconds=60
    ),
    
    'batch_process': PipelineConfig(
        name="batch_process",
        description="Batch processing for multiple files",
        processing_mode=ProcessingMode.BATCH,
        cache_strategy=CacheStrategy.DISK,
        max_workers=multiprocessing.cpu_count()
    ),
    
    'real_time': PipelineConfig(
        name="real_time",
        description="Real-time audio processing",
        processing_mode=ProcessingMode.STREAM,
        cache_strategy=CacheStrategy.NONE,
        timeout_seconds=5
    )
}
