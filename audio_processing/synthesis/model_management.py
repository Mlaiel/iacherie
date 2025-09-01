"""🎵 Synthesis Model Management Engine - Advanced Model Lifecycle Management

This module provides comprehensive model management capabilities for synthesis
models including versioning, optimization, and distributed inference.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ LEGAL WARNING: Unauthorized use prohibited. Contact mlaiel@live.de for licensing.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import logging
import json
import pickle
import hashlib
import time
import threading
from abc import ABC, abstractmethod
from enum import Enum
import psutil
import gc
from collections import OrderedDict, defaultdict
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """
Model status enumeration."""

    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    OPTIMIZING = "optimizing"
    OPTIMIZED = "optimized"
    ERROR = "error"


class OptimizationType(Enum):
    """Model optimization types."""

    QUANTIZATION = "quantization"
    PRUNING = "pruning"
    DISTILLATION = "distillation"
    JIT_COMPILATION = "jit_compilation"
    TENSORRT = "tensorrt"
    ONNX = "onnx"


@dataclass
class ModelMetadata:
    """Metadata for synthesis models."""
    name: str
    version: str
    model_type: str
    architecture: str
    parameters: Dict[str, Any]
    training_data: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    creation_date: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    license: str = "proprietary"


@dataclass
class ModelConfig:
    """Configuration for model management."""
    model_dir: Path = Path("models/synthesis")
    cache_dir: Path = Path("cache/models")
    max_cache_size: int = 10  # Maximum number of models in cache
    auto_optimization: bool = True
    optimization_types: List[OptimizationType] = field(default_factory=lambda: [OptimizationType.JIT_COMPILATION])
    preload_models: List[str] = field(default_factory=list)
    gpu_memory_limit: float = 0.8  # Fraction of GPU memory to use
    distributed_backend: str = "nccl"
    model_serving_timeout: float = 30.0


class SynthesisModelManager:
    """Central manager for synthesis models with advanced lifecycle management."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.models: Dict[str, Dict[str, Any]] = {}
        self.model_cache: OrderedDict = OrderedDict()
        self.model_metadata: Dict[str, ModelMetadata] = {}
        self.model_status: Dict[str, ModelStatus] = {}
        
        # Threading and async
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Performance monitoring
        self.performance_monitor = ModelPerformanceMonitor()
        self.resource_monitor = ModelResourceMonitor()
        
        # Optimization managers
        self.quantization_manager = QuantizationManager(config)
        self.model_optimizer = ModelOptimizer(config)
        
        # Distributed inference
        self.distributed_manager = DistributedInference(config)
        
        # Initialize directories
        self._initialize_directories()
        
        # Load existing models
        self._discover_models()
        
        # Preload models if specified
        if config.preload_models:
            self._preload_models()
            
    def _initialize_directories(self) -> None:
        """
Initialize model and cache directories."""
        self.config.model_dir.mkdir(parents=True, exist_ok=True)
        self.config.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized model directories: {self.config.model_dir}, {self.config.cache_dir}")
        
    def _discover_models(self) -> None:
        """Discover existing models in model directory."""
        for model_path in self.config.model_dir.glob("*"):
            if model_path.is_dir():
                metadata_file = model_path / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata_dict = json.load(f)
                        
                        metadata = ModelMetadata(**metadata_dict)
                        self.model_metadata[metadata.name] = metadata
                        self.model_status[metadata.name] = ModelStatus.UNLOADED
                        
                        logger.info(f"Discovered model: {metadata.name} v{metadata.version}")
                    except Exception as e:
                        logger.error(f"Failed to load metadata for {model_path}: {e}")
                        
    def _preload_models(self) -> None:
        """Preload specified models."""
        for model_name in self.config.preload_models:
            try:
                self.load_model(model_name)
                logger.info(f"Preloaded model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to preload model {model_name}: {e}")
                
    def register_model(self, model: nn.Module, metadata: ModelMetadata,
                      save_to_disk: bool = True) -> None:
        """Register new synthesis model."""
        with self.lock:
            # Calculate checksum
            model_state = model.state_dict()
            checksum = self._calculate_model_checksum(model_state)
            metadata.checksum = checksum
            
            # Save metadata
            self.model_metadata[metadata.name] = metadata
            
            # Add to cache
            self.model_cache[metadata.name] = {
                'model': model,
                'metadata': metadata,
                'loaded_time': time.time(),
                'usage_count': 0
            }
            
            self.model_status[metadata.name] = ModelStatus.LOADED
            
            # Save to disk if requested
            if save_to_disk:
                self._save_model_to_disk(model, metadata)
                
            # Apply optimizations if enabled
            if self.config.auto_optimization:
                self._schedule_optimization(metadata.name)
                
            logger.info(f"Registered model: {metadata.name} v{metadata.version}")
            
    def load_model(self, model_name: str, version: str = None) -> nn.Module:
        """Load synthesis model by name and version."""
        with self.lock:
            # Check if already in cache
            if model_name in self.model_cache:
                model_info = self.model_cache[model_name]
                model_info['usage_count'] += 1
                
                # Move to end (most recently used)
                self.model_cache.move_to_end(model_name)
                
                return model_info['model']
                
            # Check if model exists
            if model_name not in self.model_metadata:
                raise ValueError(f"Model {model_name} not found")
                
            self.model_status[model_name] = ModelStatus.LOADING
            
            try:
                # Load from disk
                model = self._load_model_from_disk(model_name, version)
                metadata = self.model_metadata[model_name]
                
                # Add to cache
                self._add_to_cache(model_name, model, metadata)
                
                self.model_status[model_name] = ModelStatus.LOADED
                
                logger.info(f"Loaded model: {model_name}")
                return model
                
            except Exception as e:
                self.model_status[model_name] = ModelStatus.ERROR
                logger.error(f"Failed to load model {model_name}: {e}")
                raise
                
    def unload_model(self, model_name: str) -> None:
        """Unload model from cache."""
        with self.lock:
            if model_name in self.model_cache:
                del self.model_cache[model_name]
                self.model_status[model_name] = ModelStatus.UNLOADED
                
                # Trigger garbage collection
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
                logger.info(f"Unloaded model: {model_name}")
                
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get comprehensive model information."""
        if model_name not in self.model_metadata:
            raise ValueError(f"Model {model_name} not found")
            
        metadata = self.model_metadata[model_name]
        status = self.model_status[model_name]
        
        info = {
            'metadata': metadata.__dict__,
            'status': status.value,
            'in_cache': model_name in self.model_cache,
            'performance_metrics': self.performance_monitor.get_model_metrics(model_name)
        }
        
        if model_name in self.model_cache:
            cache_info = self.model_cache[model_name]
            info['cache_info'] = {
                'loaded_time': cache_info['loaded_time'],
                'usage_count': cache_info['usage_count']
            }
            
        return info
        
    def list_models(self, filter_tags: List[str] = None) -> List[Dict[str, Any]]:
        """List all available models with optional tag filtering."""
        models = []
        
        for name, metadata in self.model_metadata.items():
            if filter_tags:
                if not any(tag in metadata.tags for tag in filter_tags):
                    continue
                    
            model_info = {
                'name': metadata.name,
                'version': metadata.version,
                'model_type': metadata.model_type,
                'architecture': metadata.architecture,
                'status': self.model_status[name].value,
                'tags': metadata.tags,
                'creation_date': metadata.creation_date
            }
            models.append(model_info)
            
        return models
        
    def optimize_model(self, model_name: str, 
                      optimization_types: List[OptimizationType] = None) -> None:
        """
Optimize model with specified techniques."""
        if optimization_types is None:
            optimization_types = self.config.optimization_types
            
        if model_name not in self.model_cache:
            self.load_model(model_name)
            
        with self.lock:
            self.model_status[model_name] = ModelStatus.OPTIMIZING
            
            try:
                model_info = self.model_cache[model_name]
                model = model_info['model']
                
                for opt_type in optimization_types:
                    if opt_type == OptimizationType.QUANTIZATION:
                        model = self.quantization_manager.quantize_model(model, model_name)
                    elif opt_type == OptimizationType.JIT_COMPILATION:
                        model = self._jit_compile_model(model)
                    elif opt_type == OptimizationType.PRUNING:
                        model = self._prune_model(model)
                    # Add other optimization types as needed
                    
                # Update cached model
                model_info['model'] = model
                self.model_status[model_name] = ModelStatus.OPTIMIZED
                
                logger.info(f"Optimized model {model_name} with {[opt.value for opt in optimization_types]}")
                
            except Exception as e:
                self.model_status[model_name] = ModelStatus.ERROR
                logger.error(f"Failed to optimize model {model_name}: {e}")
                raise
                
    def batch_inference(self, model_name: str, inputs: List[torch.Tensor]) -> List[torch.Tensor]:
        """Perform batch inference with automatic batching optimization."""
        if model_name not in self.model_cache:
            model = self.load_model(model_name)
        else:
            model = self.model_cache[model_name]['model']
            
        # Monitor performance
        start_time = time.time()
        
        # Perform inference
        model.eval()
        outputs = []
        
        with torch.no_grad():
            for batch_input in inputs:
                output = model(batch_input)
                outputs.append(output)
                
        # Update performance metrics
        inference_time = time.time() - start_time
        self.performance_monitor.record_inference(model_name, inference_time, len(inputs))
        
        return outputs
        
    async def async_inference(self, model_name: str, input_tensor: torch.Tensor) -> torch.Tensor:
        """
Asynchronous model inference."""
        loop = asyncio.get_event_loop()
        
        def sync_inference():
            if model_name not in self.model_cache:
                model = self.load_model(model_name)
            else:
                model = self.model_cache[model_name]['model']
                
            model.eval()
            with torch.no_grad():
                return model(input_tensor)
                
        return await loop.run_in_executor(self.executor, sync_inference)
        
    def _add_to_cache(self, model_name: str, model: nn.Module, metadata: ModelMetadata) -> None:
        """
Add model to cache with LRU eviction."""
        # Check cache size limit
        while len(self.model_cache) >= self.config.max_cache_size:
            # Remove least recently used model
            lru_name, _ = self.model_cache.popitem(last=False)
            self.model_status[lru_name] = ModelStatus.UNLOADED
            logger.info(f"Evicted model from cache: {lru_name}")
            
        # Add new model
        self.model_cache[model_name] = {
            'model': model,
            'metadata': metadata,
            'loaded_time': time.time(),
            'usage_count': 0
        }
        
    def _save_model_to_disk(self, model: nn.Module, metadata: ModelMetadata) -> None:
        """Save model and metadata to disk."""
        model_dir = self.config.model_dir / metadata.name
        model_dir.mkdir(exist_ok=True)
        
        # Save model state dict
        model_path = model_dir / "model.pth"
        torch.save(model.state_dict(), model_path)
        
        # Calculate file size
        metadata.file_size = model_path.stat().st_size
        
        # Save metadata
        metadata_path = model_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata.__dict__, f, indent=2)
            
        logger.info(f"Saved model to disk: {model_path}")
        
    def _load_model_from_disk(self, model_name: str, version: str = None) -> nn.Module:
        """Load model from disk storage."""
        model_dir = self.config.model_dir / model_name
        model_path = model_dir / "model.pth"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        # Load metadata to get architecture info
        metadata = self.model_metadata[model_name]
        
        # Create model instance (would need architecture registry in practice)
        model = self._create_model_from_metadata(metadata)
        
        # Load state dict
        state_dict = torch.load(model_path, map_location='cpu')
        model.load_state_dict(state_dict)
        
        return model
        
    def _create_model_from_metadata(self, metadata: ModelMetadata) -> nn.Module:
        """Create model instance from metadata (placeholder implementation)."""
        # This would need a proper model registry in practice
        # For now, return a dummy model
        class DummyModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = nn.Linear(100, 100)
                
            def forward(self, x):
                return self.linear(x)
                
        return DummyModel()
        
    def _calculate_model_checksum(self, state_dict: Dict) -> str:
        """
Calculate checksum of model state dict."""
        # Convert state dict to bytes and calculate SHA256
        serialized = pickle.dumps(state_dict)
        return hashlib.sha256(serialized).hexdigest()
        
    def _schedule_optimization(self, model_name: str) -> None:
        """
Schedule model optimization in background."""
        def optimize():
            try:
                self.optimize_model(model_name)
            except Exception as e:
                logger.error(f"Background optimization failed for {model_name}: {e}")
                
        self.executor.submit(optimize)
        
    def _jit_compile_model(self, model: nn.Module) -> torch.jit.ScriptModule:
        """JIT compile model for performance."""
        try:
            # Create example input (would need proper input shape in practice)
            example_input = torch.randn(1, 100)
            traced_model = torch.jit.trace(model, example_input)
            return traced_model
        except Exception as e:
            logger.warning(f"JIT compilation failed: {e}")
            return model
            
    def _prune_model(self, model: nn.Module) -> nn.Module:
        """Prune model to reduce size."""
        try:
            import torch.nn.utils.prune as prune
            
            # Global magnitude pruning (example)
            parameters_to_prune = []
            for module in model.modules():
                if isinstance(module, (nn.Linear, nn.Conv1d, nn.Conv2d)):
                    parameters_to_prune.append((module, 'weight'))
                    
            if parameters_to_prune:
                prune.global_unstructured(parameters_to_prune, pruning_method=prune.L1Unstructured, amount=0.2)
                
                # Remove pruning reparameterization
                for module, param_name in parameters_to_prune:
                    prune.remove(module, param_name)
                    
            return model
        except Exception as e:
            logger.warning(f"Model pruning failed: {e}")
            return model


class ModelVersionController:
    """Version control system for synthesis models."""
    
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.versions: Dict[str, List[str]] = defaultdict(list)
        self._discover_versions()
        
    def _discover_versions(self) -> None:
        """
Discover existing model versions."""
        for model_path in self.model_dir.glob("*"):
            if model_path.is_dir():
                version_file = model_path / "version.txt"
                if version_file.exists():
                    with open(version_file, 'r') as f:
                        version = f.read().strip()
                    self.versions[model_path.name].append(version)
                    
    def create_version(self, model_name: str, model: nn.Module, 
                      version: str, changelog: str = "") -> None:
        """Create new version of model."""
        version_dir = self.model_dir / model_name / f"v{version}"
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        model_path = version_dir / "model.pth"
        torch.save(model.state_dict(), model_path)
        
        # Save version info
        version_info = {
            'version': version,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'changelog': changelog,
            'model_path': str(model_path)
        }
        
        version_info_path = version_dir / "version.json"
        with open(version_info_path, 'w') as f:
            json.dump(version_info, f, indent=2)
            
        # Update version list
        self.versions[model_name].append(version)
        self.versions[model_name].sort()
        
        logger.info(f"Created version {version} for model {model_name}")
        
    def get_versions(self, model_name: str) -> List[str]:
        """Get all versions of a model."""
        return sorted(self.versions.get(model_name, []))
        
    def get_latest_version(self, model_name: str) -> Optional[str]:
        """
Get latest version of a model."""
        versions = self.get_versions(model_name)
        return versions[-1] if versions else None
        
    def load_version(self, model_name: str, version: str) -> Dict[str, Any]:
        """
Load specific version of model."""
        version_dir = self.model_dir / model_name / f"v{version}"
        version_info_path = version_dir / "version.json"
        
        if not version_info_path.exists():
            raise ValueError(f"Version {version} of model {model_name} not found")
            
        with open(version_info_path, 'r') as f:
            version_info = json.load(f)
            
        return version_info
        
    def compare_versions(self, model_name: str, version1: str, version2: str) -> Dict[str, Any]:
        """Compare two versions of a model."""
        v1_info = self.load_version(model_name, version1)
        v2_info = self.load_version(model_name, version2)
        
        # Load model states for comparison
        v1_state = torch.load(v1_info['model_path'], map_location='cpu')
        v2_state = torch.load(v2_info['model_path'], map_location='cpu')
        
        # Compare parameter counts
        v1_params = sum(p.numel() for p in v1_state.values())
        v2_params = sum(p.numel() for p in v2_state.values())
        
        # Compare model sizes
        v1_size = Path(v1_info['model_path']).stat().st_size
        v2_size = Path(v2_info['model_path']).stat().st_size
        
        comparison = {
            'version1': version1,
            'version2': version2,
            'parameter_difference': v2_params - v1_params,
            'size_difference': v2_size - v1_size,
            'changelog_v1': v1_info.get('changelog', ''),
            'changelog_v2': v2_info.get('changelog', ''),
            'timestamp_v1': v1_info['timestamp'],
            'timestamp_v2': v2_info['timestamp']
        }
        
        return comparison


class ModelOptimizer:
    """
Advanced model optimization techniques."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        
    def optimize_for_inference(self, model: nn.Module, input_shape: Tuple[int, ...]) -> nn.Module:
        """
Optimize model specifically for inference."""
        optimized_model = model
        
        # Set to evaluation mode
        optimized_model.eval()
        
        # Freeze all parameters
        for param in optimized_model.parameters():
            param.requires_grad = False
            
        # Apply optimizations based on config
        if OptimizationType.JIT_COMPILATION in self.config.optimization_types:
            optimized_model = self._jit_optimize(optimized_model, input_shape)
            
        if OptimizationType.QUANTIZATION in self.config.optimization_types:
            optimized_model = self._quantize_for_inference(optimized_model)
            
        return optimized_model
        
    def _jit_optimize(self, model: nn.Module, input_shape: Tuple[int, ...]) -> torch.jit.ScriptModule:
        """
Apply JIT compilation optimization."""
        try:
            example_input = torch.randn(*input_shape)
            traced_model = torch.jit.trace(model, example_input)
            
            # Optimize traced model
            traced_model = torch.jit.optimize_for_inference(traced_model)
            
            return traced_model
        except Exception as e:
            logger.warning(f"JIT optimization failed: {e}")
            return model
            
    def _quantize_for_inference(self, model: nn.Module) -> nn.Module:
        """Apply quantization for inference optimization."""
        try:
            # Dynamic quantization
            quantized_model = torch.quantization.quantize_dynamic(
                model, {nn.Linear}, dtype=torch.qint8
            )
            return quantized_model
        except Exception as e:
            logger.warning(f"Quantization failed: {e}")
            return model


class QuantizationManager:
    """Specialized quantization management."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        
    def quantize_model(self, model: nn.Module, model_name: str,
                      quantization_type: str = "dynamic") -> nn.Module:
        """Quantize model with specified method."""
        if quantization_type == "dynamic":
            return self._dynamic_quantization(model)
        elif quantization_type == "static":
            return self._static_quantization(model, model_name)
        elif quantization_type == "qat":
            return self._quantization_aware_training(model)
        else:
            raise ValueError(f"Unknown quantization type: {quantization_type}")
            
    def _dynamic_quantization(self, model: nn.Module) -> nn.Module:
        """Apply dynamic quantization."""
        quantized_model = torch.quantization.quantize_dynamic(
            model, 
            {nn.Linear, nn.Conv1d, nn.Conv2d}, 
            dtype=torch.qint8
        )
        logger.info("Applied dynamic quantization")
        return quantized_model
        
    def _static_quantization(self, model: nn.Module, model_name: str) -> nn.Module:
        """Apply static quantization with calibration."""
        # This would require calibration data in practice
        logger.warning("Static quantization not fully implemented")
        return model
        
    def _quantization_aware_training(self, model: nn.Module) -> nn.Module:
        """Apply quantization-aware training."""
        # This would require retraining in practice
        logger.warning("QAT not fully implemented")
        return model


class DistributedInference:
    """Distributed model inference across multiple devices."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.devices = self._get_available_devices()
        self.model_shards: Dict[str, List[nn.Module]] = {}
        
    def _get_available_devices(self) -> List[torch.device]:
        """
Get list of available devices."""
        devices = [torch.device('cpu')]
        
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                devices.append(torch.device(f'cuda:{i}'))
                
        return devices
        
    def shard_model(self, model: nn.Module, model_name: str, 
                   num_shards: int = None) -> None:
        """
Shard model across available devices."""
        if num_shards is None:
            num_shards = min(len(self.devices), 4)  # Reasonable default
            
        # Simple layer-wise sharding (would be more sophisticated in practice)
        layers = list(model.children())
        shard_size = len(layers) // num_shards
        
        shards = []
        for i in range(num_shards):
            start_idx = i * shard_size
            end_idx = (i + 1) * shard_size if i < num_shards - 1 else len(layers)
            
            shard_layers = layers[start_idx:end_idx]
            shard = nn.Sequential(*shard_layers)
            
            # Move shard to appropriate device
            device = self.devices[i % len(self.devices)]
            shard = shard.to(device)
            
            shards.append(shard)
            
        self.model_shards[model_name] = shards
        logger.info(f"Sharded model {model_name} into {num_shards} parts")
        
    def distributed_inference(self, model_name: str, input_tensor: torch.Tensor) -> torch.Tensor:
        """Perform distributed inference across shards."""
        if model_name not in self.model_shards:
            raise ValueError(f"Model {model_name} not sharded for distributed inference")
            
        shards = self.model_shards[model_name]
        current_output = input_tensor
        
        # Pass through each shard
        for i, shard in enumerate(shards):
            device = next(shard.parameters()).device
            current_output = current_output.to(device)
            
            with torch.no_grad():
                current_output = shard(current_output)
                
        return current_output


class ModelCache:
    """Advanced caching system for models."""
    
    def __init__(self, max_size: int = 10, cache_dir: Path = None):
        self.max_size = max_size
        self.cache_dir = cache_dir or Path("cache/models")
        self.cache: OrderedDict = OrderedDict()
        self.access_counts: Dict[str, int] = defaultdict(int)
        self.last_access: Dict[str, float] = {}
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def get(self, key: str) -> Optional[nn.Module]:
        """Get model from cache."""
        if key in self.cache:
            # Update access statistics
            self.access_counts[key] += 1
            self.last_access[key] = time.time()
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            
            return self.cache[key]
            
        return None
        
    def put(self, key: str, model: nn.Module) -> None:
        """
Put model in cache."""
        if key in self.cache:
            # Update existing entry
            self.cache[key] = model
            self.cache.move_to_end(key)
        else:
            # Add new entry
            if len(self.cache) >= self.max_size:
                # Evict least recently used
                lru_key, lru_model = self.cache.popitem(last=False)
                logger.info(f"Evicted model from cache: {lru_key}")
                
            self.cache[key] = model
            
        # Update statistics
        self.access_counts[key] = 1
        self.last_access[key] = time.time()
        
    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
        self.access_counts.clear()
        self.last_access.clear()
        
        # Force garbage collection
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
    def get_statistics(self) -> Dict[str, Any]:
        """
Get cache statistics."""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': self._calculate_hit_rate(),
            'access_counts': dict(self.access_counts),
            'memory_usage': self._estimate_memory_usage()
        }
        
    def _calculate_hit_rate(self) -> float:
        """
Calculate cache hit rate."""
        total_accesses = sum(self.access_counts.values())
        cache_hits = len([k for k in self.access_counts.keys() if k in self.cache])
        
        return cache_hits / total_accesses if total_accesses > 0 else 0.0
        
    def _estimate_memory_usage(self) -> int:
        """
Estimate memory usage of cached models."""
        total_size = 0
        
        for model in self.cache.values():
            for param in model.parameters():
                total_size += param.numel() * param.element_size()
                
        return total_size


class PreloadManager:
    """
Manager for preloading models based on usage patterns."""
    
    def __init__(self, model_manager: SynthesisModelManager):
        self.model_manager = model_manager
        self.usage_history: Dict[str, List[float]] = defaultdict(list)
        self.preload_threshold = 0.7  # Confidence threshold for preloading
        
    def record_usage(self, model_name: str) -> None:
        """
Record model usage for pattern learning."""
        current_time = time.time()
        self.usage_history[model_name].append(current_time)
        
        # Keep only recent history (last 24 hours)
        cutoff_time = current_time - 24 * 3600
        self.usage_history[model_name] = [
            t for t in self.usage_history[model_name] if t > cutoff_time
        ]
        
    def predict_next_models(self, top_k: int = 3) -> List[str]:
        """
Predict next models likely to be used."""
        current_time = time.time()
        model_scores = {}
        
        for model_name, timestamps in self.usage_history.items():
            if not timestamps:
                continue
                
            # Calculate usage frequency
            recent_usage = [t for t in timestamps if current_time - t < 3600]  # Last hour
            frequency_score = len(recent_usage) / 60  # Usage per minute
            
            # Calculate recency score
            last_usage = max(timestamps)
            recency_score = 1.0 / (1.0 + (current_time - last_usage) / 3600)
            
            # Combined score
            model_scores[model_name] = frequency_score * recency_score
            
        # Sort by score and return top_k
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        return [name for name, score in sorted_models[:top_k] if score > self.preload_threshold]
        
    def auto_preload(self) -> None:
        """
Automatically preload predicted models."""
        predicted_models = self.predict_next_models()
        
        for model_name in predicted_models:
            try:
                if model_name not in self.model_manager.model_cache:
                    self.model_manager.load_model(model_name)
                    logger.info(f"Auto-preloaded model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to auto-preload model {model_name}: {e}")


class ModelPerformanceMonitor:
    """Monitor model performance metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        
    def record_inference(self, model_name: str, inference_time: float, batch_size: int) -> None:
        """
Record inference performance."""
        self.metrics[model_name]['inference_times'].append(inference_time)
        self.metrics[model_name]['batch_sizes'].append(batch_size)
        
        # Calculate throughput
        throughput = batch_size / inference_time if inference_time > 0 else 0
        self.metrics[model_name]['throughputs'].append(throughput)
        
    def get_model_metrics(self, model_name: str) -> Dict[str, Any]:
        """
Get performance metrics for model."""
        if model_name not in self.metrics:
            return {}
            
        model_metrics = self.metrics[model_name]
        
        return {
            'avg_inference_time': np.mean(model_metrics['inference_times']) if model_metrics['inference_times'] else 0,
            'avg_throughput': np.mean(model_metrics['throughputs']) if model_metrics['throughputs'] else 0,
            'total_inferences': len(model_metrics['inference_times'])
        }
        
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
Get all performance metrics."""
        return {model_name: self.get_model_metrics(model_name) for model_name in self.metrics.keys()}


class ModelResourceMonitor:
    """
Monitor system resources used by models."""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.resource_history = defaultdict(list)
        
    def start_monitoring(self) -> None:
        """
Start resource monitoring."""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self) -> None:
        """
Stop resource monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            
    def _monitor_loop(self) -> None:
        """
Resource monitoring loop."""
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent()
                self.resource_history['cpu'].append(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.resource_history['memory_percent'].append(memory.percent)
                self.resource_history['memory_used'].append(memory.used)
                
                # GPU memory (if available)
                if torch.cuda.is_available():
                    gpu_memory = torch.cuda.memory_allocated()
                    self.resource_history['gpu_memory'].append(gpu_memory)
                    
                time.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                time.sleep(1.0)
                
    def get_current_resources(self) -> Dict[str, Any]:
        """Get current resource usage."""
        resources = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_used': psutil.virtual_memory().used
        }
        
        if torch.cuda.is_available():
            resources['gpu_memory'] = torch.cuda.memory_allocated()
            resources['gpu_memory_cached'] = torch.cuda.memory_cached()
            
        return resources


class ModelMonitor:
    """
High-level model monitoring orchestrator."""
    
    def __init__(self, model_manager: SynthesisModelManager):
        self.model_manager = model_manager
        self.performance_monitor = ModelPerformanceMonitor()
        self.resource_monitor = ModelResourceMonitor()
        self.preload_manager = PreloadManager(model_manager)
        
        # Start monitoring
        self.resource_monitor.start_monitoring()
        
    def get_system_status(self) -> Dict[str, Any]:
        """
Get comprehensive system status."""
        return {
            'models': {
                'total_registered': len(self.model_manager.model_metadata),
                'loaded_in_cache': len(self.model_manager.model_cache),
                'cache_size_limit': self.model_manager.config.max_cache_size
            },
            'performance': self.performance_monitor.get_all_metrics(),
            'resources': self.resource_monitor.get_current_resources(),
            'predictions': self.preload_manager.predict_next_models()
        }
        
    def shutdown(self) -> None:
        """
Shutdown monitoring systems."""
        self.resource_monitor.stop_monitoring()
        logger.info("Model monitoring shutdown complete")
