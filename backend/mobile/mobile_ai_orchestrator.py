"""Mobile AI Orchestrator
=======================

Mobile IA processing orchestrator for efficient AI content analysis,
mobile-optimized processing, and intelligent caching strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
import json
import uuid
import hashlib

logger = logging.getLogger(__name__)


class AIProcessingType(str, Enum):
    """Types of AI processing for mobile."""
    CONTENT_UNDERSTANDING = "content_understanding"
    QUALITY_ASSESSMENT = "quality_assessment"
    CLASSIFICATION = "classification"
    ENHANCEMENT = "enhancement"
    METADATA_EXTRACTION = "metadata_extraction"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    OBJECT_DETECTION = "object_detection"
    SPEECH_TO_TEXT = "speech_to_text"
    STYLE_ANALYSIS = "style_analysis"
    TREND_PREDICTION = "trend_prediction"


class AIModelSize(str, Enum):
    """AI model sizes for mobile optimization."""
    NANO = "nano"       # Ultra-lightweight for mobile inference
    MICRO = "micro"     # Lightweight mobile models
    SMALL = "small"     # Standard mobile models
    MEDIUM = "medium"   # High-quality mobile models
    LARGE = "large"     # Cloud processing only
    XLARGE = "xlarge"   # Premium cloud processing


class ProcessingPriority(str, Enum):
    """Processing priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    REAL_TIME = "real_time"


@dataclass
class MobileAISettings:
    """Mobile AI processing settings."""
    processing_types: List[AIProcessingType]
    model_size_preference: AIModelSize
    device_processing_enabled: bool = True
    cloud_processing_enabled: bool = True
    cache_results: bool = True
    real_time_processing: bool = False
    battery_efficient: bool = True
    network_aware: bool = True
    quality_threshold: float = 0.8
    max_processing_time_seconds: int = 30
    mobile_optimizations: List[str] = None

    def __post_init__(self):
        if self.mobile_optimizations is None:
            self.mobile_optimizations = [
                "model_quantization",
                "result_caching", 
                "batch_processing",
                "progressive_enhancement"
            ]


@dataclass
class AIProcessingRequest:
    """AI processing request for mobile."""
    request_id: str
    content_id: str
    creator_id: str
    creator_type: str
    content_type: str  # audio, video, image, text
    content_path: str
    mobile_device_id: str
    device_type: str
    network_type: str
    ai_settings: MobileAISettings
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    metadata: Dict[str, Any] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AIProcessingResult:
    """AI processing result."""
    request_id: str
    status: str  # processing, completed, failed, cached
    processing_results: Dict[AIProcessingType, Any]
    confidence_scores: Dict[AIProcessingType, float]
    processing_time_seconds: float
    models_used: Dict[AIProcessingType, str]
    cache_hit: bool
    mobile_optimized: bool
    battery_impact: float
    network_usage_mb: float
    device_processing_used: bool
    cloud_processing_used: bool
    error_message: Optional[str] = None
    completed_at: datetime = None

    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.utcnow()


class MobileAIOrchestrator:
    """Mobile IA processing orchestrator."""

    def __init__(self):
        self.ai_processors = self._initialize_ai_processors()
        self.model_registry = self._initialize_model_registry()
        self.cache_manager = self._initialize_cache_manager()
        self.device_capabilities = self._initialize_device_capabilities()
        
        self.active_requests: Dict[str, AIProcessingRequest] = {}
        self.processing_results: Dict[str, AIProcessingResult] = {}
        self.performance_metrics: Dict[str, Any] = {}

    def _initialize_ai_processors(self) -> Dict[AIProcessingType, Any]:
        """Initialize AI processors for different content types."""
        return {
            AIProcessingType.CONTENT_UNDERSTANDING: self._create_content_processor(),
            AIProcessingType.QUALITY_ASSESSMENT: self._create_quality_processor(),
            AIProcessingType.CLASSIFICATION: self._create_classification_processor(),
            AIProcessingType.ENHANCEMENT: self._create_enhancement_processor(),
            AIProcessingType.METADATA_EXTRACTION: self._create_metadata_processor(),
            AIProcessingType.SENTIMENT_ANALYSIS: self._create_sentiment_processor(),
            AIProcessingType.OBJECT_DETECTION: self._create_object_processor(),
            AIProcessingType.SPEECH_TO_TEXT: self._create_stt_processor(),
            AIProcessingType.STYLE_ANALYSIS: self._create_style_processor(),
            AIProcessingType.TREND_PREDICTION: self._create_trend_processor()
        }

    def _initialize_model_registry(self) -> Dict[AIModelSize, Dict[str, Any]]:
        """Initialize mobile-optimized AI model registry."""
        return {
            AIModelSize.NANO: {
                "content_understanding": {"model": "nano_content_v1", "size_mb": 5, "accuracy": 0.75},
                "quality_assessment": {"model": "nano_quality_v1", "size_mb": 3, "accuracy": 0.70},
                "classification": {"model": "nano_classify_v1", "size_mb": 4, "accuracy": 0.72}
            },
            AIModelSize.MICRO: {
                "content_understanding": {"model": "micro_content_v1", "size_mb": 15, "accuracy": 0.82},
                "quality_assessment": {"model": "micro_quality_v1", "size_mb": 10, "accuracy": 0.80},
                "classification": {"model": "micro_classify_v1", "size_mb": 12, "accuracy": 0.85}
            },
            AIModelSize.SMALL: {
                "content_understanding": {"model": "small_content_v1", "size_mb": 50, "accuracy": 0.88},
                "quality_assessment": {"model": "small_quality_v1", "size_mb": 35, "accuracy": 0.87},
                "classification": {"model": "small_classify_v1", "size_mb": 40, "accuracy": 0.90}
            },
            AIModelSize.MEDIUM: {
                "content_understanding": {"model": "medium_content_v1", "size_mb": 150, "accuracy": 0.92},
                "quality_assessment": {"model": "medium_quality_v1", "size_mb": 100, "accuracy": 0.91},
                "classification": {"model": "medium_classify_v1", "size_mb": 120, "accuracy": 0.94}
            },
            AIModelSize.LARGE: {
                "content_understanding": {"model": "large_content_v1", "size_mb": 500, "accuracy": 0.95},
                "quality_assessment": {"model": "large_quality_v1", "size_mb": 350, "accuracy": 0.94},
                "classification": {"model": "large_classify_v1", "size_mb": 400, "accuracy": 0.96}
            }
        }

    def _initialize_cache_manager(self) -> Dict[str, Any]:
        """Initialize mobile AI cache management."""
        return {
            "cache_storage": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_size_mb": 0,
            "max_cache_size_mb": 100,  # Configurable
            "cache_ttl_hours": 24
        }

    def _initialize_device_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Initialize device capability detection."""
        return {
            "ios": {
                "neural_engine": True,
                "gpu_acceleration": True,
                "max_model_size_mb": 200,
                "preferred_formats": ["coreml", "onnx"]
            },
            "android": {
                "neural_engine": False,
                "gpu_acceleration": True,
                "max_model_size_mb": 150,
                "preferred_formats": ["tflite", "onnx"]
            },
            "web": {
                "neural_engine": False,
                "gpu_acceleration": False,
                "max_model_size_mb": 50,
                "preferred_formats": ["tfjs", "wasm"]
            }
        }

    async def process_content_mobile(self, request: AIProcessingRequest) -> AIProcessingResult:
        """Process content with mobile-optimized AI."""
        try:
            logger.info(f"Starting mobile AI processing for request {request.request_id}")
            
            # Register request
            self.active_requests[request.request_id] = request
            
            # Check cache first
            cache_key = await self._generate_cache_key(request)
            cached_result = await self._check_cache(cache_key)
            
            if cached_result:
                logger.info(f"Cache hit for request {request.request_id}")
                cached_result.request_id = request.request_id
                cached_result.cache_hit = True
                self.processing_results[request.request_id] = cached_result
                return cached_result
            
            # Determine optimal processing strategy
            processing_strategy = await self._determine_processing_strategy(request)
            
            # Initialize result
            result = AIProcessingResult(
                request_id=request.request_id,
                status="processing",
                processing_results={},
                confidence_scores={},
                processing_time_seconds=0.0,
                models_used={},
                cache_hit=False,
                mobile_optimized=True,
                battery_impact=0.0,
                network_usage_mb=0.0,
                device_processing_used=False,
                cloud_processing_used=False
            )
            
            # Execute processing
            start_time = datetime.utcnow()
            
            for processing_type in request.ai_settings.processing_types:
                processing_result = await self._execute_ai_processing(
                    request, processing_type, processing_strategy
                )
                
                result.processing_results[processing_type] = processing_result["result"]
                result.confidence_scores[processing_type] = processing_result["confidence"]
                result.models_used[processing_type] = processing_result["model_used"]
                
                # Update usage flags
                if processing_result["device_used"]:
                    result.device_processing_used = True
                if processing_result["cloud_used"]:
                    result.cloud_processing_used = True
            
            # Calculate metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.processing_time_seconds = processing_time
            result.status = "completed"
            
            # Estimate battery and network impact
            result.battery_impact = await self._estimate_battery_impact(request, result)
            result.network_usage_mb = await self._estimate_network_usage(request, result)
            
            # Cache result if enabled
            if request.ai_settings.cache_results:
                await self._cache_result(cache_key, result)
            
            # Store result
            self.processing_results[request.request_id] = result
            
            # Update performance metrics
            await self._update_performance_metrics(request, result)
            
            logger.info(f"Mobile AI processing completed for {request.request_id} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Mobile AI processing failed for {request.request_id}: {e}")
            
            # Create error result
            error_result = AIProcessingResult(
                request_id=request.request_id,
                status="failed",
                processing_results={},
                confidence_scores={},
                processing_time_seconds=0.0,
                models_used={},
                cache_hit=False,
                mobile_optimized=False,
                battery_impact=0.0,
                network_usage_mb=0.0,
                device_processing_used=False,
                cloud_processing_used=False,
                error_message=str(e)
            )
            
            self.processing_results[request.request_id] = error_result
            return error_result
        
        finally:
            # Clean up active request
            if request.request_id in self.active_requests:
                del self.active_requests[request.request_id]

    async def _determine_processing_strategy(self, request: AIProcessingRequest) -> Dict[str, Any]:
        """Determine optimal processing strategy for mobile device."""
        device_caps = self.device_capabilities.get(request.device_type, {})
        strategy = {
            "use_device": False,
            "use_cloud": True,
            "model_size": AIModelSize.SMALL,
            "batch_processing": False,
            "progressive_enhancement": False
        }
        
        # Device capability assessment
        if request.ai_settings.device_processing_enabled and device_caps.get("neural_engine"):
            strategy["use_device"] = True
            strategy["model_size"] = AIModelSize.MEDIUM
        
        # Network condition adaptations
        if request.network_type in ["2g", "limited"]:
            strategy["use_cloud"] = False
            strategy["use_device"] = True
            strategy["model_size"] = AIModelSize.NANO
        elif request.network_type == "3g":
            strategy["model_size"] = AIModelSize.MICRO
        
        # Battery optimization
        if request.ai_settings.battery_efficient:
            if strategy["model_size"] in [AIModelSize.LARGE, AIModelSize.XLARGE]:
                strategy["model_size"] = AIModelSize.MEDIUM
            strategy["batch_processing"] = True
        
        # Real-time requirements
        if request.ai_settings.real_time_processing:
            strategy["use_device"] = True
            strategy["model_size"] = AIModelSize.SMALL
            strategy["progressive_enhancement"] = True
        
        return strategy

    async def _execute_ai_processing(self, request: AIProcessingRequest, 
                                   processing_type: AIProcessingType,
                                   strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific AI processing type."""
        try:
            processor = self.ai_processors.get(processing_type)
            if not processor:
                raise ValueError(f"No processor available for {processing_type}")
            
            # Select model based on strategy
            model_info = self._select_model(processing_type, strategy["model_size"])
            
            # Execute processing based on strategy
            if strategy["use_device"] and self._can_process_on_device(request, model_info):
                # On-device processing
                result = await self._process_on_device(
                    request, processing_type, model_info
                )
                device_used = True
                cloud_used = False
            else:
                # Cloud processing
                result = await self._process_on_cloud(
                    request, processing_type, model_info
                )
                device_used = False
                cloud_used = True
            
            return {
                "result": result["data"],
                "confidence": result["confidence"],
                "model_used": model_info["model"],
                "device_used": device_used,
                "cloud_used": cloud_used
            }
            
        except Exception as e:
            logger.error(f"AI processing failed for {processing_type}: {e}")
            return {
                "result": None,
                "confidence": 0.0,
                "model_used": "none",
                "device_used": False,
                "cloud_used": False,
                "error": str(e)
            }

    def _select_model(self, processing_type: AIProcessingType, model_size: AIModelSize) -> Dict[str, Any]:
        """Select appropriate model for processing type and size."""
        models = self.model_registry.get(model_size, {})
        processing_key = processing_type.value
        
        # Try exact match first
        if processing_key in models:
            return models[processing_key]
        
        # Fall back to general model if available
        general_models = ["content_understanding", "classification", "quality_assessment"]
        for general in general_models:
            if general in models:
                return models[general]
        
        # Default fallback
        return {"model": "default_mobile_v1", "size_mb": 10, "accuracy": 0.75}

    def _can_process_on_device(self, request: AIProcessingRequest, model_info: Dict[str, Any]) -> bool:
        """Check if processing can be done on device."""
        device_caps = self.device_capabilities.get(request.device_type, {})
        max_size = device_caps.get("max_model_size_mb", 50)
        
        return (
            model_info["size_mb"] <= max_size and
            request.ai_settings.device_processing_enabled
        )

    async def _process_on_device(self, request: AIProcessingRequest, 
                               processing_type: AIProcessingType,
                               model_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process content on mobile device."""
        # Simulate on-device processing
        await asyncio.sleep(0.5)  # Simulate processing time
        
        return {
            "data": await self._generate_mock_result(processing_type, request.content_type, "device"),
            "confidence": model_info["accuracy"] * 0.95  # Slightly lower for mobile
        }

    async def _process_on_cloud(self, request: AIProcessingRequest, 
                              processing_type: AIProcessingType,
                              model_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process content on cloud."""
        # Simulate cloud processing
        await asyncio.sleep(1.0)  # Simulate network + processing time
        
        return {
            "data": await self._generate_mock_result(processing_type, request.content_type, "cloud"),
            "confidence": model_info["accuracy"]
        }

    async def _generate_mock_result(self, processing_type: AIProcessingType, 
                                  content_type: str, platform: str) -> Dict[str, Any]:
        """Generate mock AI processing results."""
        base_result = {
            "processing_type": processing_type.value,
            "content_type": content_type,
            "platform": platform,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if processing_type == AIProcessingType.CONTENT_UNDERSTANDING:
            base_result.update({
                "main_topic": "content_analysis",
                "themes": ["creativity", "entertainment", "quality"],
                "complexity_score": 0.75,
                "engagement_potential": 0.82
            })
        elif processing_type == AIProcessingType.QUALITY_ASSESSMENT:
            base_result.update({
                "overall_quality": 0.85,
                "technical_quality": 0.88,
                "creative_quality": 0.82,
                "improvement_suggestions": ["enhance_audio", "optimize_pacing"]
            })
        elif processing_type == AIProcessingType.CLASSIFICATION:
            base_result.update({
                "primary_category": "entertainment",
                "secondary_categories": ["music", "creative"],
                "genre": "electronic",
                "style": "modern"
            })
        elif processing_type == AIProcessingType.METADATA_EXTRACTION:
            base_result.update({
                "title": "Auto-generated title",
                "description": "Auto-generated description",
                "tags": ["mobile", "ai", "content"],
                "duration_seconds": 120
            })
        
        return base_result

    async def _generate_cache_key(self, request: AIProcessingRequest) -> str:
        """Generate cache key for request."""
        # Create content hash
        content_hash = hashlib.sha256(request.content_path.encode()).hexdigest()[:16]
        
        # Include relevant parameters
        cache_data = {
            "content_hash": content_hash,
            "processing_types": sorted([pt.value for pt in request.ai_settings.processing_types]),
            "model_size": request.ai_settings.model_size_preference.value,
            "quality_threshold": request.ai_settings.quality_threshold
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()[:32]

    async def _check_cache(self, cache_key: str) -> Optional[AIProcessingResult]:
        """Check if result is cached."""
        cache_storage = self.cache_manager["cache_storage"]
        
        if cache_key in cache_storage:
            cached_entry = cache_storage[cache_key]
            
            # Check if cache is still valid
            cache_time = cached_entry["timestamp"]
            ttl_hours = self.cache_manager["cache_ttl_hours"]
            
            if datetime.utcnow() - cache_time < timedelta(hours=ttl_hours):
                self.cache_manager["cache_hits"] += 1
                return cached_entry["result"]
            else:
                # Remove expired cache
                del cache_storage[cache_key]
        
        self.cache_manager["cache_misses"] += 1
        return None

    async def _cache_result(self, cache_key: str, result: AIProcessingResult) -> None:
        """Cache processing result."""
        cache_storage = self.cache_manager["cache_storage"]
        
        # Check cache size limit
        if self.cache_manager["cache_size_mb"] > self.cache_manager["max_cache_size_mb"]:
            await self._cleanup_cache()
        
        # Store result
        cache_storage[cache_key] = {
            "result": result,
            "timestamp": datetime.utcnow(),
            "size_estimate_mb": 0.1  # Estimate
        }
        
        self.cache_manager["cache_size_mb"] += 0.1

    async def _cleanup_cache(self) -> None:
        """Clean up old cache entries."""
        cache_storage = self.cache_manager["cache_storage"]
        
        # Remove oldest entries
        sorted_entries = sorted(
            cache_storage.items(),
            key=lambda x: x[1]["timestamp"]
        )
        
        # Remove oldest 25%
        remove_count = len(sorted_entries) // 4
        for cache_key, _ in sorted_entries[:remove_count]:
            del cache_storage[cache_key]
            self.cache_manager["cache_size_mb"] -= 0.1

    async def _estimate_battery_impact(self, request: AIProcessingRequest, 
                                     result: AIProcessingResult) -> float:
        """Estimate battery impact of processing."""
        base_impact = 0.1  # Base 0.1% battery drain
        
        if result.device_processing_used:
            base_impact *= 3  # Device processing uses more battery
        
        if result.cloud_processing_used:
            base_impact *= 1.5  # Network usage
        
        return min(base_impact, 5.0)  # Cap at 5%

    async def _estimate_network_usage(self, request: AIProcessingRequest, 
                                    result: AIProcessingResult) -> float:
        """Estimate network usage in MB."""
        if not result.cloud_processing_used:
            return 0.0
        
        # Estimate based on content type and processing
        base_usage = {
            "audio": 2.0,
            "video": 5.0,
            "image": 1.0,
            "text": 0.1
        }
        
        content_usage = base_usage.get(request.content_type, 1.0)
        processing_multiplier = len(request.ai_settings.processing_types) * 0.5
        
        return content_usage * processing_multiplier

    async def _update_performance_metrics(self, request: AIProcessingRequest, 
                                        result: AIProcessingResult) -> None:
        """Update performance metrics."""
        creator_id = request.creator_id
        
        if creator_id not in self.performance_metrics:
            self.performance_metrics[creator_id] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_processing_time": 0.0,
                "cache_hit_rate": 0.0,
                "average_confidence": 0.0,
                "device_processing_rate": 0.0,
                "battery_impact_total": 0.0
            }
        
        metrics = self.performance_metrics[creator_id]
        metrics["total_requests"] += 1
        
        if result.status == "completed":
            metrics["successful_requests"] += 1
            metrics["total_processing_time"] += result.processing_time_seconds
            
            # Update confidence average
            avg_confidence = sum(result.confidence_scores.values()) / len(result.confidence_scores)
            current_avg = metrics["average_confidence"]
            count = metrics["successful_requests"]
            metrics["average_confidence"] = ((current_avg * (count - 1)) + avg_confidence) / count
        
        metrics["cache_hit_rate"] = (
            self.cache_manager["cache_hits"] / 
            (self.cache_manager["cache_hits"] + self.cache_manager["cache_misses"])
        )
        
        if result.device_processing_used:
            device_count = sum(1 for r in self.processing_results.values() if r.device_processing_used)
            metrics["device_processing_rate"] = device_count / metrics["total_requests"]
        
        metrics["battery_impact_total"] += result.battery_impact

    # Placeholder processor creation methods
    def _create_content_processor(self): return None
    def _create_quality_processor(self): return None
    def _create_classification_processor(self): return None
    def _create_enhancement_processor(self): return None
    def _create_metadata_processor(self): return None
    def _create_sentiment_processor(self): return None
    def _create_object_processor(self): return None
    def _create_stt_processor(self): return None
    def _create_style_processor(self): return None
    def _create_trend_processor(self): return None

    # Public API methods
    async def get_processing_status(self, request_id: str) -> Optional[AIProcessingResult]:
        """Get processing status for request."""
        return self.processing_results.get(request_id)

    async def cancel_processing(self, request_id: str) -> bool:
        """Cancel active processing."""
        if request_id in self.active_requests:
            del self.active_requests[request_id]
            return True
        return False

    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        return {
            "cache_hits": self.cache_manager["cache_hits"],
            "cache_misses": self.cache_manager["cache_misses"],
            "hit_rate": (
                self.cache_manager["cache_hits"] / 
                max(1, self.cache_manager["cache_hits"] + self.cache_manager["cache_misses"])
            ),
            "cache_size_mb": self.cache_manager["cache_size_mb"],
            "cached_entries": len(self.cache_manager["cache_storage"])
        }

    async def get_performance_metrics(self, creator_id: str) -> Dict[str, Any]:
        """Get performance metrics for creator."""
        return self.performance_metrics.get(creator_id, {})

    async def clear_cache(self) -> bool:
        """Clear all cached results."""
        self.cache_manager["cache_storage"].clear()
        self.cache_manager["cache_size_mb"] = 0
        return True

    async def optimize_for_device(self, device_type: str, ai_settings: MobileAISettings) -> MobileAISettings:
        """Optimize AI settings for specific device."""
        device_caps = self.device_capabilities.get(device_type, {})
        optimized_settings = MobileAISettings(**asdict(ai_settings))
        
        # Adjust model size based on device capabilities
        max_size_mb = device_caps.get("max_model_size_mb", 50)
        
        if max_size_mb < 50:
            optimized_settings.model_size_preference = AIModelSize.NANO
        elif max_size_mb < 100:
            optimized_settings.model_size_preference = AIModelSize.MICRO
        elif max_size_mb < 200:
            optimized_settings.model_size_preference = AIModelSize.SMALL
        
        # Enable device processing if supported
        if device_caps.get("neural_engine"):
            optimized_settings.device_processing_enabled = True
        
        return optimized_settings

    async def get_supported_processing_types(self, creator_type: str) -> List[AIProcessingType]:
        """Get supported processing types for creator type."""
        creator_types_mapping = {
            "musician": [
                AIProcessingType.CONTENT_UNDERSTANDING,
                AIProcessingType.QUALITY_ASSESSMENT,
                AIProcessingType.CLASSIFICATION,
                AIProcessingType.SENTIMENT_ANALYSIS,
                AIProcessingType.ENHANCEMENT
            ],
            "blogger": [
                AIProcessingType.CONTENT_UNDERSTANDING,
                AIProcessingType.SENTIMENT_ANALYSIS,
                AIProcessingType.CLASSIFICATION,
                AIProcessingType.METADATA_EXTRACTION
            ],
            "photographer": [
                AIProcessingType.OBJECT_DETECTION,
                AIProcessingType.STYLE_ANALYSIS,
                AIProcessingType.QUALITY_ASSESSMENT,
                AIProcessingType.ENHANCEMENT,
                AIProcessingType.CLASSIFICATION
            ],
            "influencer": [
                AIProcessingType.CONTENT_UNDERSTANDING,
                AIProcessingType.SENTIMENT_ANALYSIS,
                AIProcessingType.TREND_PREDICTION,
                AIProcessingType.OBJECT_DETECTION,
                AIProcessingType.SPEECH_TO_TEXT
            ],
            "comedian": [
                AIProcessingType.CONTENT_UNDERSTANDING,
                AIProcessingType.SENTIMENT_ANALYSIS,
                AIProcessingType.SPEECH_TO_TEXT,
                AIProcessingType.QUALITY_ASSESSMENT
            ]
        }
        
        return creator_types_mapping.get(creator_type, list(AIProcessingType))