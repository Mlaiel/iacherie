"""
Edge Inference Optimizer - Edge Computing Inference Optimization for Mobile and IoT
Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade edge inference optimization for mobile devices and IoT platforms.
Optimized for low-latency, low-power content processing for creators.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import time
import psutil
import platform
from datetime import datetime
import numpy as np

@dataclass
class EdgeDeviceProfile:
    """Edge device hardware profile."""
    device_id: str
    device_type: str  # "mobile", "tablet", "iot", "edge_server", "raspberry_pi"
    cpu_cores: int
    cpu_frequency: float  # GHz
    memory_gb: float
    storage_gb: float
    gpu_available: bool
    gpu_memory_mb: int
    npu_available: bool  # Neural Processing Unit
    power_budget_watts: float
    battery_powered: bool
    network_bandwidth_mbps: float
    os_type: str  # "android", "ios", "linux", "windows"
    supported_frameworks: List[str]
    optimization_level: str  # "aggressive", "balanced", "conservative"

@dataclass
class ModelOptimization:
    """Model optimization configuration and results."""
    optimization_id: str
    original_model_size: int
    optimized_model_size: int
    compression_ratio: float
    quantization_type: str  # "int8", "int4", "fp16", "dynamic"
    pruning_ratio: float
    knowledge_distillation_applied: bool
    inference_latency_ms: float
    accuracy_retention: float
    memory_usage_mb: float
    power_consumption_watts: float
    optimization_techniques: List[str]

@dataclass
class InferenceRequest:
    """Edge inference request."""
    request_id: str
    model_id: str
    input_data: Any
    input_format: str  # "audio", "image", "text", "video"
    priority: str  # "high", "medium", "low"
    max_latency_ms: float
    quality_threshold: float
    device_constraints: Dict[str, Any]
    caching_enabled: bool
    batch_processing: bool

@dataclass
class InferenceResult:
    """Edge inference result."""
    request_id: str
    prediction: Any
    confidence_score: float
    processing_time_ms: float
    memory_used_mb: float
    energy_consumed_mj: float  # millijoules
    cache_hit: bool
    model_version: str
    optimization_applied: str
    device_utilization: Dict[str, float]

class EdgeInferenceOptimizer:
    """
    Advanced edge inference optimizer for mobile and IoT deployment.
    
    Features:
    - Device-specific model optimization (quantization, pruning, distillation)
    - Adaptive inference scheduling based on device resources
    - Power-aware inference with battery optimization
    - Dynamic model switching based on device capabilities
    - Intelligent caching and prefetching
    - Network-aware inference with cloud fallback
    - Multi-modal content processing optimization
    - Real-time performance monitoring and adaptation
    """
    
    def __init__(self, edge_cache_dir: str = "edge_cache/"):
        self.logger = logging.getLogger(__name__)
        self.edge_cache_dir = Path(edge_cache_dir)
        self.edge_cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Device profiles and optimized models
        self.device_profiles = {}
        self.optimized_models = {}
        self.inference_cache = {}
        
        # Performance monitoring
        self.performance_metrics = {}
        self.resource_monitors = {}
        
        # Optimization strategies
        self.optimization_strategies = {
            "mobile": {
                "quantization": "int8",
                "pruning_ratio": 0.3,
                "batch_size": 1,
                "memory_limit_mb": 512,
                "power_awareness": True,
                "cache_size_mb": 128
            },
            "iot": {
                "quantization": "int4",
                "pruning_ratio": 0.5,
                "batch_size": 1,
                "memory_limit_mb": 64,
                "power_awareness": True,
                "cache_size_mb": 32
            },
            "edge_server": {
                "quantization": "fp16",
                "pruning_ratio": 0.1,
                "batch_size": 8,
                "memory_limit_mb": 2048,
                "power_awareness": False,
                "cache_size_mb": 512
            }
        }
        
        # Creator-specific optimizations
        self.creator_optimizations = {
            "musician": {
                "input_preprocessing": ["spectral_optimization", "temporal_compression"],
                "model_architectures": ["lightweight_transformer", "mobilenet_audio"],
                "output_postprocessing": ["confidence_thresholding", "result_caching"]
            },
            "photographer": {
                "input_preprocessing": ["image_resizing", "color_space_optimization"],
                "model_architectures": ["efficientnet_mobile", "mobilevit"],
                "output_postprocessing": ["nms_optimization", "result_visualization"]
            },
            "blogger": {
                "input_preprocessing": ["text_tokenization", "length_optimization"],
                "model_architectures": ["distilbert", "mobile_bert"],
                "output_postprocessing": ["language_detection", "sentiment_caching"]
            }
        }
        
    async def profile_edge_device(self, device_info: Dict[str, Any]) -> EdgeDeviceProfile:
        """Profile edge device capabilities and constraints."""
        try:
            # Get system information
            cpu_count = psutil.cpu_count(logical=True)
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            
            # Detect device type based on specs
            device_type = self._detect_device_type(device_info, cpu_count, memory_info.total)
            
            # Check GPU availability (mock detection)
            gpu_available = device_info.get("gpu", False)
            gpu_memory = device_info.get("gpu_memory_mb", 0)
            
            # Check NPU availability (mock detection)
            npu_available = device_info.get("npu", False)
            
            # Estimate power budget
            power_budget = self._estimate_power_budget(device_type, cpu_count, gpu_available)
            
            # Detect network capabilities
            network_bandwidth = device_info.get("network_bandwidth_mbps", 100.0)
            
            # Get supported frameworks
            supported_frameworks = self._detect_supported_frameworks(device_info.get("os", "linux"))
            
            profile = EdgeDeviceProfile(
                device_id=device_info.get("device_id", f"device_{int(time.time())}"),
                device_type=device_type,
                cpu_cores=cpu_count,
                cpu_frequency=psutil.cpu_freq().max / 1000 if psutil.cpu_freq() else 2.0,  # GHz
                memory_gb=memory_info.total / (1024**3),
                storage_gb=disk_info.total / (1024**3),
                gpu_available=gpu_available,
                gpu_memory_mb=gpu_memory,
                npu_available=npu_available,
                power_budget_watts=power_budget,
                battery_powered=device_info.get("battery_powered", True),
                network_bandwidth_mbps=network_bandwidth,
                os_type=device_info.get("os", platform.system().lower()),
                supported_frameworks=supported_frameworks,
                optimization_level=device_info.get("optimization_level", "balanced")
            )
            
            # Store profile
            self.device_profiles[profile.device_id] = profile
            
            self.logger.info(f"Device profiled: {profile.device_id} ({profile.device_type})")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error profiling edge device: {e}")
            raise
    
    async def optimize_model_for_edge(
        self,
        model_id: str,
        target_device: EdgeDeviceProfile,
        optimization_config: Dict[str, Any] = None
    ) -> ModelOptimization:
        """Optimize model for specific edge device."""
        try:
            optimization_id = f"opt_{model_id}_{target_device.device_id}_{int(time.time())}"
            
            # Get device-specific optimization strategy
            strategy = self.optimization_strategies.get(target_device.device_type, 
                                                      self.optimization_strategies["mobile"])
            
            if optimization_config:
                strategy.update(optimization_config)
            
            # Simulate model loading and analysis
            await asyncio.sleep(0.1)
            original_size = 50 * 1024 * 1024  # 50MB mock model
            
            # Apply quantization
            quantization_type = strategy.get("quantization", "int8")
            size_after_quantization = await self._apply_quantization(
                original_size, quantization_type, target_device
            )
            
            # Apply pruning
            pruning_ratio = strategy.get("pruning_ratio", 0.3)
            size_after_pruning = await self._apply_pruning(
                size_after_quantization, pruning_ratio, target_device
            )
            
            # Apply knowledge distillation if beneficial
            kd_applied = await self._should_apply_knowledge_distillation(target_device)
            size_after_kd = size_after_pruning
            if kd_applied:
                size_after_kd = await self._apply_knowledge_distillation(
                    size_after_pruning, target_device
                )
            
            final_size = size_after_kd
            compression_ratio = original_size / final_size
            
            # Estimate performance metrics
            inference_latency = await self._estimate_inference_latency(
                final_size, target_device, strategy
            )
            
            accuracy_retention = await self._estimate_accuracy_retention(
                quantization_type, pruning_ratio, kd_applied
            )
            
            memory_usage = await self._estimate_memory_usage(final_size, target_device)
            power_consumption = await self._estimate_power_consumption(target_device, inference_latency)
            
            # Create optimization result
            optimization = ModelOptimization(
                optimization_id=optimization_id,
                original_model_size=original_size,
                optimized_model_size=final_size,
                compression_ratio=compression_ratio,
                quantization_type=quantization_type,
                pruning_ratio=pruning_ratio,
                knowledge_distillation_applied=kd_applied,
                inference_latency_ms=inference_latency,
                accuracy_retention=accuracy_retention,
                memory_usage_mb=memory_usage,
                power_consumption_watts=power_consumption,
                optimization_techniques=self._get_applied_techniques(
                    quantization_type, pruning_ratio, kd_applied
                )
            )
            
            # Store optimized model
            self.optimized_models[f"{model_id}_{target_device.device_id}"] = optimization
            
            # Save optimized model to cache
            await self._cache_optimized_model(optimization, target_device)
            
            self.logger.info(f"Model optimized for edge: {optimization_id} "
                           f"({compression_ratio:.2f}x compression)")
            
            return optimization
            
        except Exception as e:
            self.logger.error(f"Error optimizing model for edge: {e}")
            raise
    
    async def execute_edge_inference(
        self,
        request: InferenceRequest,
        device_profile: EdgeDeviceProfile
    ) -> InferenceResult:
        """Execute optimized inference on edge device."""
        try:
            start_time = time.time()
            
            # Check cache first
            cache_key = self._generate_cache_key(request, device_profile)
            cached_result = self.inference_cache.get(cache_key)
            
            if cached_result and request.caching_enabled:
                self.logger.debug(f"Cache hit for request: {request.request_id}")
                return self._create_cached_result(cached_result, request.request_id)
            
            # Select optimized model
            model_key = f"{request.model_id}_{device_profile.device_id}"
            optimization = self.optimized_models.get(model_key)
            
            if not optimization:
                # Optimize model on-demand
                optimization = await self.optimize_model_for_edge(
                    request.model_id, device_profile
                )
            
            # Monitor resources before inference
            initial_resources = await self._monitor_device_resources(device_profile)
            
            # Execute inference with optimizations
            prediction, confidence = await self._execute_optimized_inference(
                request, optimization, device_profile
            )
            
            # Monitor resources after inference
            final_resources = await self._monitor_device_resources(device_profile)
            
            processing_time = (time.time() - start_time) * 1000  # ms
            
            # Calculate resource usage
            memory_used = final_resources["memory_used"] - initial_resources["memory_used"]
            energy_consumed = await self._calculate_energy_consumption(
                processing_time, device_profile, optimization
            )
            
            # Create result
            result = InferenceResult(
                request_id=request.request_id,
                prediction=prediction,
                confidence_score=confidence,
                processing_time_ms=processing_time,
                memory_used_mb=memory_used,
                energy_consumed_mj=energy_consumed,
                cache_hit=False,
                model_version=optimization.optimization_id,
                optimization_applied=optimization.quantization_type,
                device_utilization={
                    "cpu_usage": final_resources["cpu_usage"],
                    "memory_usage": final_resources["memory_usage"],
                    "gpu_usage": final_resources.get("gpu_usage", 0.0)
                }
            )
            
            # Cache result if beneficial
            if request.caching_enabled and confidence > request.quality_threshold:
                self.inference_cache[cache_key] = result
            
            # Update performance metrics
            await self._update_performance_metrics(request, result, device_profile)
            
            self.logger.debug(f"Edge inference completed: {request.request_id} "
                            f"({processing_time:.2f}ms, {confidence:.3f} confidence)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing edge inference: {e}")
            raise
    
    async def adaptive_model_switching(
        self,
        device_profile: EdgeDeviceProfile,
        performance_requirements: Dict[str, float],
        available_models: List[str]
    ) -> str:
        """Adaptively switch models based on device state and requirements."""
        try:
            # Monitor current device state
            current_resources = await self._monitor_device_resources(device_profile)
            
            # Score available models
            model_scores = {}
            
            for model_id in available_models:
                model_key = f"{model_id}_{device_profile.device_id}"
                optimization = self.optimized_models.get(model_key)
                
                if not optimization:
                    continue
                
                # Calculate composite score
                score = await self._calculate_model_score(
                    optimization, current_resources, performance_requirements
                )
                
                model_scores[model_id] = score
            
            # Select best model
            if model_scores:
                best_model = max(model_scores.items(), key=lambda x: x[1])[0]
                
                self.logger.info(f"Adaptive model selection: {best_model} "
                               f"(score: {model_scores[best_model]:.3f})")
                
                return best_model
            
            # Fallback to first available model
            return available_models[0] if available_models else None
            
        except Exception as e:
            self.logger.error(f"Error in adaptive model switching: {e}")
            return available_models[0] if available_models else None
    
    async def optimize_inference_pipeline(
        self,
        device_profile: EdgeDeviceProfile,
        creator_type: str,
        content_types: List[str]
    ) -> Dict[str, Any]:
        """Optimize entire inference pipeline for creator-specific workflows."""
        try:
            creator_optimizations = self.creator_optimizations.get(creator_type, {})
            
            pipeline_config = {
                "preprocessing": {
                    "techniques": creator_optimizations.get("input_preprocessing", []),
                    "parallel_processing": device_profile.cpu_cores > 4,
                    "batch_size": 1 if device_profile.device_type == "mobile" else 4,
                    "memory_optimization": True
                },
                "inference": {
                    "preferred_architectures": creator_optimizations.get("model_architectures", []),
                    "quantization": self._get_optimal_quantization(device_profile),
                    "pruning_enabled": device_profile.memory_gb < 4.0,
                    "gpu_acceleration": device_profile.gpu_available,
                    "npu_acceleration": device_profile.npu_available
                },
                "postprocessing": {
                    "techniques": creator_optimizations.get("output_postprocessing", []),
                    "result_caching": True,
                    "confidence_filtering": True,
                    "output_compression": device_profile.network_bandwidth_mbps < 50
                },
                "scheduling": {
                    "priority_queue": True,
                    "power_aware": device_profile.battery_powered,
                    "thermal_management": device_profile.device_type == "mobile",
                    "background_processing": device_profile.memory_gb > 2.0
                }
            }
            
            # Apply content-specific optimizations
            for content_type in content_types:
                content_optimizations = await self._get_content_optimizations(
                    content_type, device_profile
                )
                pipeline_config[f"{content_type}_optimizations"] = content_optimizations
            
            # Estimate pipeline performance
            estimated_performance = await self._estimate_pipeline_performance(
                pipeline_config, device_profile
            )
            
            pipeline_result = {
                "pipeline_id": f"pipeline_{creator_type}_{device_profile.device_id}_{int(time.time())}",
                "configuration": pipeline_config,
                "estimated_performance": estimated_performance,
                "creator_type": creator_type,
                "device_profile": device_profile.device_id,
                "optimization_level": device_profile.optimization_level,
                "created_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Inference pipeline optimized for {creator_type} on {device_profile.device_type}")
            return pipeline_result
            
        except Exception as e:
            self.logger.error(f"Error optimizing inference pipeline: {e}")
            raise
    
    def _detect_device_type(self, device_info: Dict[str, Any], cpu_count: int, memory_bytes: int) -> str:
        """Detect device type based on hardware specs."""
        memory_gb = memory_bytes / (1024**3)
        
        if device_info.get("device_type"):
            return device_info["device_type"]
        
        if memory_gb < 1.0 and cpu_count <= 4:
            return "iot"
        elif memory_gb < 4.0 and cpu_count <= 8:
            return "mobile"
        elif memory_gb < 8.0:
            return "tablet"
        else:
            return "edge_server"
    
    def _estimate_power_budget(self, device_type: str, cpu_count: int, gpu_available: bool) -> float:
        """Estimate power budget in watts."""
        base_power = {
            "iot": 2.0,
            "mobile": 5.0,
            "tablet": 10.0,
            "edge_server": 50.0
        }
        
        power = base_power.get(device_type, 10.0)
        power += cpu_count * 1.5  # Additional power per core
        
        if gpu_available:
            power += 15.0 if device_type == "edge_server" else 5.0
        
        return power
    
    def _detect_supported_frameworks(self, os_type: str) -> List[str]:
        """Detect supported ML frameworks."""
        frameworks = ["pytorch_mobile", "tensorflow_lite"]
        
        if os_type == "android":
            frameworks.extend(["nnapi", "vulkan"])
        elif os_type == "ios":
            frameworks.extend(["coreml", "metal"])
        elif os_type in ["linux", "windows"]:
            frameworks.extend(["onnx", "tensorrt", "openvino"])
        
        return frameworks
    
    async def _apply_quantization(
        self, 
        model_size: int, 
        quantization_type: str, 
        device: EdgeDeviceProfile
    ) -> int:
        """Apply quantization optimization."""
        await asyncio.sleep(0.02)  # Simulate quantization time
        
        reduction_ratios = {
            "fp32": 1.0,
            "fp16": 0.5,
            "int8": 0.25,
            "int4": 0.125
        }
        
        ratio = reduction_ratios.get(quantization_type, 0.25)
        return int(model_size * ratio)
    
    async def _apply_pruning(self, model_size: int, pruning_ratio: float, device: EdgeDeviceProfile) -> int:
        """Apply pruning optimization."""
        await asyncio.sleep(0.03)  # Simulate pruning time
        return int(model_size * (1.0 - pruning_ratio))
    
    async def _should_apply_knowledge_distillation(self, device: EdgeDeviceProfile) -> bool:
        """Determine if knowledge distillation should be applied."""
        # Apply KD for very resource-constrained devices
        return device.memory_gb < 2.0 or device.device_type == "iot"
    
    async def _apply_knowledge_distillation(self, model_size: int, device: EdgeDeviceProfile) -> int:
        """Apply knowledge distillation."""
        await asyncio.sleep(0.05)  # Simulate distillation time
        return int(model_size * 0.7)  # Additional 30% reduction
    
    async def _estimate_inference_latency(
        self, 
        model_size: int, 
        device: EdgeDeviceProfile,
        strategy: Dict[str, Any]
    ) -> float:
        """Estimate inference latency in milliseconds."""
        # Base latency calculation
        base_latency = model_size / (1024 * 1024) * 2.0  # 2ms per MB (rough estimate)
        
        # Device-specific adjustments
        cpu_factor = 2.0 / device.cpu_frequency  # Adjust for CPU speed
        memory_factor = 1.0 if device.memory_gb > 2.0 else 1.5  # Memory pressure
        
        # GPU acceleration
        if device.gpu_available and strategy.get("use_gpu", True):
            base_latency *= 0.3  # 70% reduction with GPU
        
        # NPU acceleration
        if device.npu_available:
            base_latency *= 0.5  # 50% reduction with NPU
        
        return base_latency * cpu_factor * memory_factor
    
    async def _estimate_accuracy_retention(
        self, 
        quantization_type: str, 
        pruning_ratio: float, 
        kd_applied: bool
    ) -> float:
        """Estimate accuracy retention after optimizations."""
        base_accuracy = 1.0
        
        # Quantization impact
        quantization_impact = {
            "fp32": 0.0,
            "fp16": 0.01,
            "int8": 0.03,
            "int4": 0.08
        }
        
        base_accuracy -= quantization_impact.get(quantization_type, 0.03)
        
        # Pruning impact
        base_accuracy -= pruning_ratio * 0.1
        
        # Knowledge distillation can actually improve retained accuracy
        if kd_applied:
            base_accuracy += 0.02
        
        return max(0.0, min(1.0, base_accuracy))
    
    async def _estimate_memory_usage(self, model_size: int, device: EdgeDeviceProfile) -> float:
        """Estimate memory usage in MB."""
        # Model loading + inference buffer + overhead
        base_memory = model_size / (1024 * 1024)  # Convert to MB
        inference_buffer = base_memory * 0.5  # 50% additional for inference
        overhead = 50.0  # 50MB overhead
        
        return base_memory + inference_buffer + overhead
    
    async def _estimate_power_consumption(self, device: EdgeDeviceProfile, latency_ms: float) -> float:
        """Estimate power consumption in watts."""
        # Base power consumption based on device type
        base_power = {
            "iot": 1.0,
            "mobile": 3.0,
            "tablet": 5.0,
            "edge_server": 15.0
        }.get(device.device_type, 3.0)
        
        # Scale by inference duration
        duration_seconds = latency_ms / 1000.0
        
        return base_power * duration_seconds
    
    def _get_applied_techniques(
        self, 
        quantization_type: str, 
        pruning_ratio: float, 
        kd_applied: bool
    ) -> List[str]:
        """Get list of applied optimization techniques."""
        techniques = []
        
        if quantization_type != "fp32":
            techniques.append(f"quantization_{quantization_type}")
        
        if pruning_ratio > 0:
            techniques.append(f"pruning_{pruning_ratio:.1f}")
        
        if kd_applied:
            techniques.append("knowledge_distillation")
        
        return techniques
    
    async def _monitor_device_resources(self, device: EdgeDeviceProfile) -> Dict[str, float]:
        """Monitor current device resource usage."""
        try:
            # Get current system metrics
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            resources = {
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "memory_used": memory.used / (1024 * 1024),  # MB
                "memory_available": memory.available / (1024 * 1024)  # MB
            }
            
            # Mock GPU usage if available
            if device.gpu_available:
                resources["gpu_usage"] = np.random.uniform(10, 30)  # Mock GPU usage
            
            return resources
            
        except Exception as e:
            self.logger.warning(f"Error monitoring resources: {e}")
            return {"cpu_usage": 0, "memory_usage": 0, "memory_used": 0}

# Example usage and testing
async def main():
    """Example usage of EdgeInferenceOptimizer."""
    optimizer = EdgeInferenceOptimizer()
    
    # Mock device information
    device_info = {
        "device_id": "mobile_device_001",
        "device_type": "mobile",
        "gpu": True,
        "gpu_memory_mb": 512,
        "battery_powered": True,
        "network_bandwidth_mbps": 25.0,
        "os": "android",
        "optimization_level": "aggressive"
    }
    
    # Profile device
    device_profile = await optimizer.profile_edge_device(device_info)
    print(f"Device profiled: {device_profile.device_type} with {device_profile.memory_gb:.1f}GB RAM")
    
    # Optimize model for edge
    optimization = await optimizer.optimize_model_for_edge(
        "musician-audio-classifier", device_profile
    )
    print(f"Model optimized: {optimization.compression_ratio:.2f}x compression, "
          f"{optimization.inference_latency_ms:.1f}ms latency")
    
    # Create inference request
    request = InferenceRequest(
        request_id="req_001",
        model_id="musician-audio-classifier",
        input_data=np.random.randn(1, 128, 256),  # Mock audio spectrogram
        input_format="audio",
        priority="high",
        max_latency_ms=100.0,
        quality_threshold=0.8,
        device_constraints={"max_memory_mb": 256},
        caching_enabled=True,
        batch_processing=False
    )
    
    # Execute edge inference
    result = await optimizer.execute_edge_inference(request, device_profile)
    print(f"Inference completed: {result.processing_time_ms:.1f}ms, "
          f"confidence: {result.confidence_score:.3f}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())