"""Model Factory and Registry for IA Influencer Agent Platform
Centralized model management and orchestration system

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
⚠️  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Development Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security
- Microservices + Audio + DevOps + IA Prompt Engineer
Email: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Type, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json

from .audio_models import AudioFeatureExtractor, AudioEnhancer, AudioProtector
from .video_models import VideoProcessor, VideoAnalyzer, VideoProtector
from .image_models import ImageFeatureExtractor, ImageEnhancer, ImageProtector
from .text_models import TextAnalyzer, ContentGenerator
from .protection_models import UniversalFingerprintEngine, CopyrightDetector
from .business_intelligence_models import TrendPredictor, CollaborationMatcher

from ..core.base_models import BaseAIModel, ModelConfig, ModelType, ModelProvider, ProcessingResult


class ModelCategory(Enum):
    """
Model category classifications"""

    CONTENT_PROCESSING = "content_processing"
    CONTENT_PROTECTION = "content_protection"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    CONTENT_GENERATION = "content_generation"
    ANALYTICS = "analytics"
    OPTIMIZATION = "optimization"


@dataclass
class ModelRegistry:
    """Model registration information"""
    model_class: Type[BaseAIModel]
    category: ModelCategory
    supported_types: List[ModelType]
    description: str
    version: str
    capabilities: List[str]
    dependencies: List[str]
    resource_requirements: Dict[str, Any]


class ModelOrchestrator:
    """
    Central orchestrator for all AI models in the platform
    Manages model lifecycle, load balancing, and intelligent routing
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.registered_models: Dict[str, ModelRegistry] = {}
        self.active_models: Dict[str, BaseAIModel] = {}
        self.model_stats: Dict[str, Dict[str, Any]] = {}
        self.load_balancer = ModelLoadBalancer()
        self._register_core_models()
    
    def _register_core_models(self):
        """
Register all core models"""
        
        # Audio Models
        self.register_model(
            "audio_feature_extractor",
            ModelRegistry(
                model_class=AudioFeatureExtractor,
                category=ModelCategory.CONTENT_PROCESSING,
                supported_types=[ModelType.AUDIO_MODEL, ModelType.AUDIO_FINGERPRINT],
                description="Advanced audio feature extraction and analysis",
                version="1.0.0",
                capabilities=[
                    "audio_analysis", "genre_classification", "mood_detection",
                    "quality_assessment", "fingerprinting", "tempo_detection"
                ],
                dependencies=["librosa", "torch", "torchaudio"],
                resource_requirements={"memory": "2GB", "cpu_cores": 2}
            )
        )
        
        # Video Models
        self.register_model(
            "video_processor",
            ModelRegistry(
                model_class=VideoProcessor,
                category=ModelCategory.CONTENT_PROCESSING,
                supported_types=[ModelType.VIDEO_MODEL, ModelType.VIDEO_ANALYSIS],
                description="Comprehensive video processing and analysis",
                version="1.0.0",
                capabilities=[
                    "scene_detection", "object_recognition", "face_detection",
                    "quality_assessment", "motion_analysis", "content_classification"
                ],
                dependencies=["opencv-python", "torch", "torchvision"],
                resource_requirements={"memory": "4GB", "cpu_cores": 4, "gpu": "optional"}
            )
        )
        
        # Image Models
        self.register_model(
            "image_feature_extractor",
            ModelRegistry(
                model_class=ImageFeatureExtractor,
                category=ModelCategory.CONTENT_PROCESSING,
                supported_types=[ModelType.IMAGE_MODEL, ModelType.IMAGE_RECOGNITION],
                description="Advanced image analysis and feature extraction",
                version="1.0.0",
                capabilities=[
                    "object_detection", "face_recognition", "quality_assessment",
                    "style_classification", "composition_analysis", "aesthetic_scoring"
                ],
                dependencies=["opencv-python", "PIL", "imagehash", "torch"],
                resource_requirements={"memory": "3GB", "cpu_cores": 2}
            )
        )
        
        # Text Models
        self.register_model(
            "text_analyzer",
            ModelRegistry(
                model_class=TextAnalyzer,
                category=ModelCategory.CONTENT_PROCESSING,
                supported_types=[ModelType.TEXT_MODEL, ModelType.SENTIMENT_ANALYSIS],
                description="Comprehensive text analysis and NLP processing",
                version="1.0.0",
                capabilities=[
                    "sentiment_analysis", "entity_extraction", "language_detection",
                    "quality_assessment", "topic_modeling", "readability_analysis"
                ],
                dependencies=["transformers", "spacy", "nltk", "torch"],
                resource_requirements={"memory": "4GB", "cpu_cores": 2}
            )
        )
        
        self.register_model(
            "content_generator",
            ModelRegistry(
                model_class=ContentGenerator,
                category=ModelCategory.CONTENT_GENERATION,
                supported_types=[ModelType.TEXT_GENERATION],
                description="Advanced content generation and optimization",
                version="1.0.0",
                capabilities=[
                    "text_generation", "seo_optimization", "content_enhancement",
                    "multilingual_support", "style_adaptation", "quality_optimization"
                ],
                dependencies=["transformers", "torch", "openai"],
                resource_requirements={"memory": "6GB", "cpu_cores": 4}
            )
        )
        
        # Protection Models
        self.register_model(
            "universal_fingerprint_engine",
            ModelRegistry(
                model_class=UniversalFingerprintEngine,
                category=ModelCategory.CONTENT_PROTECTION,
                supported_types=[ModelType.CONTENT_PROTECTION, ModelType.COPYRIGHT_DETECTION],
                description="Universal content fingerprinting for all media types",
                version="1.0.0",
                capabilities=[
                    "multi_modal_fingerprinting", "perceptual_hashing", "structural_analysis",
                    "semantic_fingerprinting", "temporal_signatures", "cross_platform_matching"
                ],
                dependencies=["librosa", "opencv-python", "imagehash", "numpy"],
                resource_requirements={"memory": "3GB", "cpu_cores": 3}
            )
        )
        
        self.register_model(
            "copyright_detector",
            ModelRegistry(
                model_class=CopyrightDetector,
                category=ModelCategory.CONTENT_PROTECTION,
                supported_types=[ModelType.COPYRIGHT_DETECTION, ModelType.WATERMARK_DETECTION],
                description="Advanced copyright detection and legal analysis",
                version="1.0.0",
                capabilities=[
                    "copyright_matching", "legal_analysis", "risk_assessment",
                    "database_integration", "automated_monitoring", "compliance_checking"
                ],
                dependencies=["requests", "asyncio", "datetime"],
                resource_requirements={"memory": "2GB", "cpu_cores": 2, "network": "required"}
            )
        )
        
        # Business Intelligence Models
        self.register_model(
            "trend_predictor",
            ModelRegistry(
                model_class=TrendPredictor,
                category=ModelCategory.BUSINESS_INTELLIGENCE,
                supported_types=[ModelType.TREND_ANALYSIS],
                description="Advanced trend prediction and market analysis",
                version="1.0.0",
                capabilities=[
                    "trend_prediction", "momentum_analysis", "opportunity_assessment",
                    "competition_analysis", "content_recommendations", "timing_optimization"
                ],
                dependencies=["sklearn", "torch", "pandas", "numpy"],
                resource_requirements={"memory": "4GB", "cpu_cores": 3}
            )
        )
        
        self.register_model(
            "collaboration_matcher",
            ModelRegistry(
                model_class=CollaborationMatcher,
                category=ModelCategory.BUSINESS_INTELLIGENCE,
                supported_types=[ModelType.COLLABORATION_MATCHING],
                description="Intelligent creator collaboration matching",
                version="1.0.0",
                capabilities=[
                    "creator_matching", "compatibility_analysis", "audience_analysis",
                    "revenue_prediction", "collaboration_optimization", "success_modeling"
                ],
                dependencies=["sklearn", "numpy", "pandas"],
                resource_requirements={"memory": "3GB", "cpu_cores": 2}
            )
        )
    
    def register_model(self, model_id: str, registry: ModelRegistry):
        """Register a new model"""
        self.registered_models[model_id] = registry
        self.model_stats[model_id] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "last_used": None,
            "status": "registered"
        }
        self.logger.info(f"Registered model: {model_id}")
    
    async def get_model(self, model_id: str, config: Optional[ModelConfig] = None) -> BaseAIModel:
        """Get or create model instance"""
        if model_id not in self.registered_models:
            raise ValueError(f"Model {model_id} not registered")
        
        # Check if model is already active
        if model_id in self.active_models:
            return self.active_models[model_id]
        
        # Create new model instance
        registry = self.registered_models[model_id]
        
        if config is None:
            config = ModelConfig(
                name=model_id,
                provider=ModelProvider.LOCAL,
                model_type=registry.supported_types[0]
            )
        
        try:
            model_instance = registry.model_class(config)
            await model_instance.connect()
            
            self.active_models[model_id] = model_instance
            self.model_stats[model_id]["status"] = "active"
            
            self.logger.info(f"Created and activated model: {model_id}")
            return model_instance
            
        except Exception as e:
            self.model_stats[model_id]["status"] = "failed"
            self.logger.error(f"Failed to create model {model_id}: {e}")
            raise
    
    async def process_request(self, model_id: str, data: Any, **kwargs) -> ProcessingResult:
        """Process request through specified model"""
        start_time = datetime.now()
        
        try:
            # Get model instance
            model = await self.get_model(model_id)
            
            # Process request
            result = await model.process(data, **kwargs)
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_model_stats(model_id, True, processing_time)
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_model_stats(model_id, False, processing_time)
            
            return ProcessingResult(
                success=False,
                data=None,
                error_message=str(e),
                processing_time=processing_time
            )
    
    def _update_model_stats(self, model_id: str, success: bool, processing_time: float):
        """
Update model statistics"""
        stats = self.model_stats[model_id]
        
        stats["total_requests"] += 1
        if success:
            stats["successful_requests"] += 1
        else:
            stats["failed_requests"] += 1
        
        # Update average response time
        current_avg = stats["average_response_time"]
        total_requests = stats["total_requests"]
        stats["average_response_time"] = (current_avg * (total_requests - 1) + processing_time) / total_requests
        
        stats["last_used"] = datetime.now()
    
    async def route_request(self, content_type: str, operation: str, data: Any, **kwargs) -> ProcessingResult:
        """Intelligently route request to appropriate model"""
        
        # Routing logic based on content type and operation
        routing_map = {
            ("audio", "analyze"): "audio_feature_extractor",
            ("audio", "protect"): "universal_fingerprint_engine",
            ("video", "analyze"): "video_processor",
            ("video", "protect"): "universal_fingerprint_engine",
            ("image", "analyze"): "image_feature_extractor",
            ("image", "enhance"): "image_feature_extractor",
            ("image", "protect"): "universal_fingerprint_engine",
            ("text", "analyze"): "text_analyzer",
            ("text", "generate"): "content_generator",
            ("text", "protect"): "universal_fingerprint_engine",
            ("content", "fingerprint"): "universal_fingerprint_engine",
            ("content", "copyright_check"): "copyright_detector",
            ("business", "trend_analysis"): "trend_predictor",
            ("business", "collaboration"): "collaboration_matcher"
        }
        
        model_id = routing_map.get((content_type.lower(), operation.lower()))
        
        if not model_id:
            raise ValueError(f"No model available for {content_type}/{operation}")
        
        return await self.process_request(model_id, data, **kwargs)
    
    async def batch_process(self, requests: List[Dict[str, Any]]) -> List[ProcessingResult]:
        """Process multiple requests in parallel"""
        tasks = []
        
        for request in requests:
            model_id = request.get("model_id")
            content_type = request.get("content_type")
            operation = request.get("operation")
            data = request.get("data")
            kwargs = request.get("kwargs", {})
            
            if model_id:
                task = self.process_request(model_id, data, **kwargs)
            elif content_type and operation:
                task = self.route_request(content_type, operation, data, **kwargs)
            else:
                # Create failed result for invalid request
                task = asyncio.create_task(asyncio.coroutine(lambda: ProcessingResult(
                    success=False,
                    data=None,
                    error_message="Invalid request format"
                ))())
            
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(ProcessingResult(
                    success=False,
                    data=None,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_model_stats(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Get model statistics"""
        if model_id:
            return self.model_stats.get(model_id, {})
        return self.model_stats
    
    def get_registered_models(self) -> Dict[str, ModelRegistry]:
        """
Get all registered models"""
        return self.registered_models
    
    def get_models_by_category(self, category: ModelCategory) -> Dict[str, ModelRegistry]:
        """
Get models by category"""
        return {
            model_id: registry
            for model_id, registry in self.registered_models.items()
            if registry.category == category
        }
    
    def get_models_by_capability(self, capability: str) -> Dict[str, ModelRegistry]:
        """
Get models by capability"""
        return {
            model_id: registry
            for model_id, registry in self.registered_models.items()
            if capability in registry.capabilities
        }
    
    async def shutdown_model(self, model_id: str):
        """
Shutdown specific model"""
        if model_id in self.active_models:
            model = self.active_models[model_id]
            if hasattr(model, 'shutdown'):
                await model.shutdown()
            del self.active_models[model_id]
            self.model_stats[model_id]["status"] = "shutdown"
            self.logger.info(f"Shutdown model: {model_id}")
    
    async def shutdown_all_models(self):
        """Shutdown all active models"""
        shutdown_tasks = []
        for model_id in list(self.active_models.keys()):
            shutdown_tasks.append(self.shutdown_model(model_id))
        
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        self.logger.info("All models shutdown")


class ModelLoadBalancer:
    """Load balancer for model instances"""
    
    def __init__(self):
        self.model_instances: Dict[str, List[BaseAIModel]] = {}
        self.current_index: Dict[str, int] = {}
    
    def add_instance(self, model_id: str, instance: BaseAIModel):
        """
Add model instance to load balancer"""
        if model_id not in self.model_instances:
            self.model_instances[model_id] = []
            self.current_index[model_id] = 0
        
        self.model_instances[model_id].append(instance)
    
    def get_instance(self, model_id: str) -> Optional[BaseAIModel]:
        """Execute business logic for {func_name}"""
                try:
                    logger.info(f"Executing {func_name}")
            
                    # Input validation
                    if data is None:
                        raise ValueError("Input data is required")
            
                    # Initialize execution context
                    execution_start = datetime.utcnow()
            
                    # Core business logic execution
                    result = {
                        "status": "success",
                        "data": data,
                        "processed_at": execution_start.isoformat(),
                        "function": "{func_name}"
                    }
            
                    # Apply business rules if available
                    if hasattr(self, 'business_rules'):
                        for rule in self.business_rules:
                            result = self._apply_business_rule(result, rule)
            
                    # Log execution metrics
                    execution_time = (datetime.utcnow() - execution_start).total_seconds()
                    result["execution_time"] = execution_time
            
                    logger.info(f"{func_name} completed successfully in {execution_time:.3f}s")
                    return result
            
                except Exception as e:
                    logger.error(f"{func_name} failed: {e}")
                    raise
Get next available instance using round-robin"""
        if model_id not in self.model_instances or not self.model_instances[model_id]:
            return None
        
        instances = self.model_instances[model_id]
        current_idx = self.current_index[model_id]
        
        instance = instances[current_idx]
        
        # Update index for next request
        self.current_index[model_id] = (current_idx + 1) % len(instances)
        
        return instance
    
    def remove_instance(self, model_id: str, instance: BaseAIModel):
        """
Remove instance from load balancer"""
        if model_id in self.model_instances:
            try:
                self.model_instances[model_id].remove(instance)
                # Reset index if needed
                if not self.model_instances[model_id]:
                    self.current_index[model_id] = 0
                elif self.current_index[model_id] >= len(self.model_instances[model_id]):
                    self.current_index[model_id] = 0
            except ValueError:
                pass  # Instance not in list


class ModelFactory:
    """
Factory for creating model instances"""
    
    @staticmethod
    def create_model(model_type: ModelType, config: ModelConfig) -> BaseAIModel:
        """
Create model instance based on type"""
        
        model_map = {
            ModelType.AUDIO_MODEL: AudioFeatureExtractor,
            ModelType.AUDIO_FINGERPRINT: AudioFeatureExtractor,
            ModelType.VIDEO_MODEL: VideoProcessor,
            ModelType.VIDEO_ANALYSIS: VideoAnalyzer,
            ModelType.IMAGE_MODEL: ImageFeatureExtractor,
            ModelType.IMAGE_RECOGNITION: ImageFeatureExtractor,
            ModelType.TEXT_MODEL: TextAnalyzer,
            ModelType.TEXT_GENERATION: ContentGenerator,
            ModelType.CONTENT_PROTECTION: UniversalFingerprintEngine,
            ModelType.COPYRIGHT_DETECTION: CopyrightDetector,
            ModelType.TREND_ANALYSIS: TrendPredictor,
            ModelType.COLLABORATION_MATCHING: CollaborationMatcher
        }
        
        model_class = model_map.get(model_type)
        if not model_class:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        return model_class(config)
    
    @staticmethod
    def create_optimized_config(model_type: ModelType, use_case: str) -> ModelConfig:
        """Create optimized configuration for specific use case"""
        
        base_configs = {
            ModelType.AUDIO_MODEL: ModelConfig(
                name=f"audio_model_{use_case}",
                provider=ModelProvider.LOCAL,
                model_type=model_type,
                max_tokens=4096,
                timeout=30,
                enable_caching=True
            ),
            ModelType.TEXT_GENERATION: ModelConfig(
                name=f"text_gen_{use_case}",
                provider=ModelProvider.OPENAI,
                model_type=model_type,
                max_tokens=8192,
                temperature=0.7,
                timeout=60,
                enable_caching=True
            )
        }
        
        return base_configs.get(model_type, ModelConfig(
            name=f"{model_type.value}_{use_case}",
            provider=ModelProvider.LOCAL,
            model_type=model_type
        ))


# Global model orchestrator instance
model_orchestrator = ModelOrchestrator()

# Export key components
__all__ = [
    'ModelCategory',
    'ModelRegistry',
    'ModelOrchestrator',
    'ModelLoadBalancer',
    'ModelFactory',
    'model_orchestrator'
]
