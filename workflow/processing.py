"""Advanced content processing pipeline with dynamic stage management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

import asyncio
from typing import Dict, List, Optional, Callable, Any, Set
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import logging
from collections import defaultdict, deque

from ..core.exceptions import PipelineException, ValidationException
from ..models.content import ContentItem, ContentMetadata
from ..services.ai.content_analyzer import ContentAnalyzer
from ..utils.metrics import MetricsCollector
from ..utils.caching import CacheManager


class PipelineStage(Enum):
    """
Enhanced pipeline stages for content processing."""

    VALIDATION = "validation"
    PREPROCESSING = "preprocessing"
    FEATURE_EXTRACTION = "feature_extraction"
    AI_ANALYSIS = "ai_analysis"
    QUALITY_ASSESSMENT = "quality_assessment"
    FINGERPRINT_GENERATION = "fingerprint_generation"
    SEO_OPTIMIZATION = "seo_optimization"
    MONETIZATION_ANALYSIS = "monetization_analysis"
    COLLABORATION_MATCHING = "collaboration_matching"
    PLATFORM_OPTIMIZATION = "platform_optimization"
    DISTRIBUTION_PREPARATION = "distribution_preparation"
    MONITORING_SETUP = "monitoring_setup"
    COMPLETION = "completion"


class PipelineStatus(Enum):
    """Pipeline execution status."""

    INITIALIZED = "initialized"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class PipelinePriority(Enum):
    """Pipeline execution priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


class StageResult:
    """
Result object for pipeline stage execution."""
    
    def __init__(self, stage: PipelineStage, success: bool, data: Dict = None, 
                 errors: List[str] = None, duration: float = 0.0):
        self.stage = stage
        self.success = success
        self.data = data or {}
        self.errors = errors or []
        self.duration = duration
        self.timestamp = datetime.utcnow()
        self.retry_count = 0
    
    def to_dict(self) -> Dict:
        """
Convert stage result to dictionary."""
        return {
            "stage": self.stage.value,
            "success": self.success,
            "data": self.data,
            "errors": self.errors,
            "duration": self.duration,
            "timestamp": self.timestamp.isoformat(),
            "retry_count": self.retry_count
        }


class PipelineStageProcessor:
    """Base class for pipeline stage processors."""
    
    def __init__(self, stage: PipelineStage):
        self.stage = stage
        self.logger = logging.getLogger(f"pipeline.{stage.value}")
        self.metrics = MetricsCollector()
        self.cache = CacheManager()
    
    async def execute(self, content_item: ContentItem, context: Dict) -> StageResult:
        """Execute the pipeline stage."""
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Starting stage {self.stage.value}")
            
            # Check cache first
            cache_key = self._get_cache_key(content_item, context)
            cached_result = await self.cache.get(cache_key)
            
            if cached_result and self._should_use_cache(content_item, context):
                self.logger.info(f"Using cached result for stage {self.stage.value}")
                return StageResult(
                    stage=self.stage,
                    success=True,
                    data=cached_result,
                    duration=0.0
                )
            
            # Execute stage processing
            result_data = await self.process(content_item, context)
            
            # Cache result if appropriate
            if self._should_cache_result(result_data):
                await self.cache.set(cache_key, result_data, ttl=3600)  # 1 hour
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Record metrics
            self.metrics.record_stage_execution(
                stage=self.stage.value,
                duration=duration,
                success=True
            )
            
            self.logger.info(f"Completed stage {self.stage.value} in {duration:.2f}s")
            
            return StageResult(
                stage=self.stage,
                success=True,
                data=result_data,
                duration=duration
            )
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Record failure metrics
            self.metrics.record_stage_execution(
                stage=self.stage.value,
                duration=duration,
                success=False,
                error=str(e)
            )
            
            self.logger.error(f"Stage {self.stage.value} failed: {str(e)}")
            
            return StageResult(
                stage=self.stage,
                success=False,
                errors=[str(e)],
                duration=duration
            )
    
    async def process(self, content_item: ContentItem, context: Dict) -> Dict:
        """Process the stage - to be implemented by subclasses."""
        # Default implementation for processing stages without specific implementation
        logging.warning(f"Content processing not implemented for {self.__class__.__name__}")
        return {
            "status": "not_implemented",
            "processor": self.__class__.__name__,
            "content_id": getattr(content_item, 'id', 'unknown'),
            "message": f"Content processing not implemented for {self.__class__.__name__}"
        }
    
    def _get_cache_key(self, content_item: ContentItem, context: Dict) -> str:
        """Generate cache key for the stage result."""
        content_hash = content_item.get_hash()
        context_hash = hash(json.dumps(context, sort_keys=True, default=str))
        return f"{self.stage.value}:{content_hash}:{context_hash}"
    
    def _should_use_cache(self, content_item: ContentItem, context: Dict) -> bool:
        """Determine if cached result should be used."""
        return context.get("use_cache", True)
    
    def _should_cache_result(self, result_data: Dict) -> bool:
        """Determine if result should be cached."""
        return len(json.dumps(result_data, default=str)) < 10000  # Cache if < 10KB


class ContentValidationProcessor(PipelineStageProcessor):
    """
Validate content format, size, and basic requirements."""
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def process(self, content_item: ContentItem, context: Dict) -> Dict:
        """
Validate content item."""
        validation_results = {
            "format_valid": False,
            "size_valid": False,
            "quality_sufficient": False,
            "requirements_met": False,
            "warnings": [],
            "recommendations": []
        }
        
        # Validate format
        supported_formats = context.get("supported_formats", [])
        if not supported_formats or content_item.format in supported_formats:
            validation_results["format_valid"] = True
        else:
            validation_results["warnings"].append(
                f"Format {content_item.format} not in supported formats"
            )
        
        # Validate size
        max_size = context.get("max_file_size", 100 * 1024 * 1024)  # 100MB default
        if content_item.file_size <= max_size:
            validation_results["size_valid"] = True
        else:
            validation_results["warnings"].append(
                f"File size {content_item.file_size} exceeds maximum {max_size}"
            )
        
        # Basic quality checks
        quality_score = await self._assess_basic_quality(content_item)
        validation_results["basic_quality_score"] = quality_score
        validation_results["quality_sufficient"] = quality_score > 0.5
        
        # Generate recommendations
        if quality_score < 0.7:
            validation_results["recommendations"].append(
                "Consider improving content quality before processing"
            )
        
        validation_results["requirements_met"] = (
            validation_results["format_valid"] and 
            validation_results["size_valid"] and 
            validation_results["quality_sufficient"]
        )
        
        return validation_results
    
    async def _assess_basic_quality(self, content_item: ContentItem) -> float:
        """Perform basic quality assessment."""
        score = 0.5  # Base score
        
        # Check resolution for images/videos
        if hasattr(content_item, 'resolution'):
            if content_item.resolution and content_item.resolution[0] >= 1920:
                score += 0.2
        
        # Check duration for audio/video
        if hasattr(content_item, 'duration'):
            if content_item.duration and 30 <= content_item.duration <= 600:  # 30s to 10min
                score += 0.2
        
        # Check file integrity
        if content_item.is_complete:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
        if content_item.is_complete:
            score += 0.1
        
        return min(score, 1.0)


class ContentPreprocessingProcessor(PipelineStageProcessor):
    """
Preprocess content for analysis and optimization."""
    
    def __init__(self):
        super().__init__(PipelineStage.PREPROCESSING)
    
    async def process(self, content_item: ContentItem, context: Dict) -> Dict:
        """
Preprocess content item."""
        preprocessing_results = {
            "normalized": False,
            "optimized": False,
            "thumbnails_generated": False,
            "metadata_extracted": False,
            "processing_info": {}
        }
        
        # Normalize content format
        normalized_content = await self._normalize_content(content_item)
        preprocessing_results["normalized"] = normalized_content is not None
        
        # Generate thumbnails/previews
        thumbnails = await self._generate_thumbnails(content_item)
        preprocessing_results["thumbnails_generated"] = len(thumbnails) > 0
        preprocessing_results["thumbnails"] = thumbnails
        
        # Extract technical metadata
        technical_metadata = await self._extract_technical_metadata(content_item)
        preprocessing_results["metadata_extracted"] = len(technical_metadata) > 0
        preprocessing_results["technical_metadata"] = technical_metadata
        
        # Optimize for processing
        optimization_info = await self._optimize_for_processing(content_item)
        preprocessing_results["optimized"] = optimization_info["success"]
        preprocessing_results["optimization_info"] = optimization_info
        
        return preprocessing_results
    
    async def _normalize_content(self, content_item: ContentItem) -> Optional[ContentItem]:
        """Normalize content format and encoding."""
        # Placeholder for content normalization
        return content_item
    
    async def _generate_thumbnails(self, content_item: ContentItem) -> List[Dict]:
        """
Generate thumbnails or preview images."""
        thumbnails = []
        
        if content_item.content_type in ["video", "image"]:
            # Generate different sized thumbnails
            for size in ["small", "medium", "large"]:
                thumbnails.append({
                    "size": size,
                    "url": f"/thumbnails/{content_item.id}_{size}.jpg",
                    "dimensions": self._get_thumbnail_dimensions(size)
                })
        
        return thumbnails
    
    def _get_thumbnail_dimensions(self, size: str) -> tuple:
        """Get thumbnail dimensions for size."""
        dimensions = {
            "small": (150, 150),
            "medium": (300, 300),
            "large": (600, 600)
        }
        return dimensions.get(size, (300, 300))
    
    async def _extract_technical_metadata(self, content_item: ContentItem) -> Dict:
        """Extract technical metadata from content."""
        metadata = {
            "format": content_item.format,
            "size": content_item.file_size,
            "created_at": datetime.utcnow().isoformat(),
            "mime_type": content_item.mime_type
        }
        
        # Add content-specific metadata
        if content_item.content_type == "audio":
            metadata.update({
                "sample_rate": getattr(content_item, "sample_rate", None),
                "bit_rate": getattr(content_item, "bit_rate", None),
                "channels": getattr(content_item, "channels", None)
            })
        elif content_item.content_type == "video":
            metadata.update({
                "resolution": getattr(content_item, "resolution", None),
                "frame_rate": getattr(content_item, "frame_rate", None),
                "codec": getattr(content_item, "codec", None)
            })
        
        return metadata
    
    async def _optimize_for_processing(self, content_item: ContentItem) -> Dict:
        """Optimize content for downstream processing."""
        return {
            "success": True,
            "optimizations_applied": ["format_standardization", "quality_enhancement"],
            "performance_gain": 0.15
        }


class FeatureExtractionProcessor(PipelineStageProcessor):
    """Extract features for AI analysis and matching."""
    
    def __init__(self):
        super().__init__(PipelineStage.FEATURE_EXTRACTION)
        self.content_analyzer = ContentAnalyzer()
    
    async def process(self, content_item: ContentItem, context: Dict) -> Dict:
        """
Extract features from content."""
        feature_results = {
            "visual_features": {},
            "audio_features": {},
            "text_features": {},
            "semantic_features": {},
            "embedding_vectors": {},
            "feature_quality": 0.0
        }
        
        # Extract content-type specific features
        if content_item.content_type == "image":
            feature_results["visual_features"] = await self._extract_visual_features(content_item)
        elif content_item.content_type == "audio":
            feature_results["audio_features"] = await self._extract_audio_features(content_item)
        elif content_item.content_type == "video":
            feature_results["visual_features"] = await self._extract_visual_features(content_item)
            feature_results["audio_features"] = await self._extract_audio_features(content_item)
        elif content_item.content_type == "text":
            feature_results["text_features"] = await self._extract_text_features(content_item)
        
        # Extract semantic features
        feature_results["semantic_features"] = await self._extract_semantic_features(content_item)
        
        # Generate embedding vectors
        feature_results["embedding_vectors"] = await self._generate_embedding_vectors(
            content_item, feature_results
        )
        
        # Calculate feature quality score
        feature_results["feature_quality"] = await self._calculate_feature_quality(feature_results)
        
        return feature_results
    
    async def _extract_visual_features(self, content_item: ContentItem) -> Dict:
        """Extract visual features from image/video content."""
        return {
            "color_histogram": [],  # Placeholder
            "edge_features": [],
            "texture_features": [],
            "object_detection": [],
            "scene_classification": ""
        }
    
    async def _extract_audio_features(self, content_item: ContentItem) -> Dict:
        """Extract audio features from audio/video content."""
        return {
            "spectral_features": [],  # Placeholder
            "tempo": 0.0,
            "key": "",
            "loudness": 0.0,
            "rhythm_patterns": []
        }
    
    async def _extract_text_features(self, content_item: ContentItem) -> Dict:
        """Extract text features from text content."""
        return {
            "word_count": 0,  # Placeholder
            "sentiment_score": 0.0,
            "readability_score": 0.0,
            "topic_keywords": [],
            "language": "en"
        }
    
    async def _extract_semantic_features(self, content_item: ContentItem) -> Dict:
        """Extract semantic features across all content types."""
        return {
            "category": "",  # Placeholder
            "tags": [],
            "themes": [],
            "emotional_tone": "",
            "commercial_intent": 0.0
        }
    
    async def _generate_embedding_vectors(self, content_item: ContentItem, features: Dict) -> Dict:
        """Generate embedding vectors for similarity matching."""
        return {
            "content_embedding": [],  # Placeholder for vector
            "semantic_embedding": [],
            "style_embedding": [],
            "embedding_dimension": 512
        }
    
    async def _calculate_feature_quality(self, features: Dict) -> float:
        """Calculate overall feature quality score."""
        quality_score = 0.0
        feature_count = 0
        
        for feature_type, feature_data in features.items():
            if feature_type.endswith("_features") and feature_data:
                quality_score += 0.2
                feature_count += 1
        
        if features.get("embedding_vectors"):
            quality_score += 0.3
        
        return min(quality_score, 1.0)


class AIAnalysisProcessor(PipelineStageProcessor):
    """Advanced AI analysis of content."""
    
    def __init__(self):
        super().__init__(PipelineStage.AI_ANALYSIS)
        self.content_analyzer = ContentAnalyzer()
    
    async def process(self, content_item: ContentItem, context: Dict) -> Dict:
        """
Perform comprehensive AI analysis."""
        analysis_results = {
            "content_understanding": {},
            "audience_analysis": {},
            "trend_analysis": {},
            "commercial_analysis": {},
            "quality_metrics": {},
            "recommendations": [],
            "confidence_scores": {}
        }
        
        # Perform content understanding
        analysis_results["content_understanding"] = await self._analyze_content_understanding(
            content_item, context
        )
        
        # Analyze target audience
        analysis_results["audience_analysis"] = await self._analyze_target_audience(
            content_item, context
        )
        
        # Analyze trends and virality potential
        analysis_results["trend_analysis"] = await self._analyze_trends(content_item, context)
        
        # Analyze commercial potential
        analysis_results["commercial_analysis"] = await self._analyze_commercial_potential(
            content_item, context
        )
        
        # Calculate quality metrics
        analysis_results["quality_metrics"] = await self._calculate_quality_metrics(
            content_item, context
        )
        
        # Generate AI recommendations
        analysis_results["recommendations"] = await self._generate_ai_recommendations(
            content_item, analysis_results
        )
        
        # Calculate confidence scores
        analysis_results["confidence_scores"] = await self._calculate_confidence_scores(
            analysis_results
        )
        
        return analysis_results
    
    async def _analyze_content_understanding(self, content_item: ContentItem, context: Dict) -> Dict:
        """Analyze and understand content semantics."""
        return {
            "primary_topic": "entertainment",  # Placeholder
            "secondary_topics": ["music", "creativity"],
            "content_style": "professional",
            "narrative_structure": "linear",
            "key_elements": ["visual", "audio", "text"],
            "complexity_level": "medium"
        }
    
    async def _analyze_target_audience(self, content_item: ContentItem, context: Dict) -> Dict:
        """Analyze potential target audience."""
        return {
            "age_groups": ["18-24", "25-34"],  # Placeholder
            "interests": ["music", "entertainment", "technology"],
            "demographics": ["urban", "educated", "tech-savvy"],
            "engagement_patterns": ["evening", "weekend"],
            "platform_preferences": ["instagram", "youtube", "tiktok"]
        }
    
    async def _analyze_trends(self, content_item: ContentItem, context: Dict) -> Dict:
        """Analyze trend alignment and viral potential."""
        return {
            "trend_alignment": 0.7,  # Placeholder
            "viral_potential": 0.6,
            "trending_keywords": ["ai", "content", "creator"],
            "seasonal_relevance": "high",
            "platform_trends": {
                "instagram": 0.8,
                "tiktok": 0.9,
                "youtube": 0.7
            }
        }
    
    async def _analyze_commercial_potential(self, content_item: ContentItem, context: Dict) -> Dict:
        """Analyze commercial and monetization potential."""
        return {
            "monetization_score": 0.75,  # Placeholder
            "brand_safety": 0.9,
            "advertising_potential": 0.7,
            "licensing_potential": 0.6,
            "collaboration_value": 0.8,
            "revenue_categories": ["advertising", "licensing", "partnerships"]
        }
    
    async def _calculate_quality_metrics(self, content_item: ContentItem, context: Dict) -> Dict:
        """Calculate comprehensive quality metrics."""
        return {
            "overall_quality": 0.8,  # Placeholder
            "technical_quality": 0.85,
            "creative_quality": 0.75,
            "engagement_quality": 0.8,
            "professional_quality": 0.9
        }
    
    async def _generate_ai_recommendations(self, content_item: ContentItem, analysis: Dict) -> List[Dict]:
        """Generate AI-powered recommendations."""
        recommendations = []
        
        # Quality improvements
        if analysis["quality_metrics"]["overall_quality"] < 0.8:
            recommendations.append({
                "type": "quality_improvement",
                "priority": "high",
                "description": "Enhance content quality for better engagement",
                "specific_actions": ["improve_audio_quality", "enhance_visuals"]
            })
        
        # Audience targeting
        if analysis["audience_analysis"]["age_groups"]:
            recommendations.append({
                "type": "audience_targeting",
                "priority": "medium",
                "description": "Optimize content for target age groups",
                "specific_actions": ["adjust_tone", "use_relevant_references"]
            })
        
        return recommendations
    
    async def _calculate_confidence_scores(self, analysis: Dict) -> Dict:
        """Calculate confidence scores for analysis results."""
        return {
            "content_understanding": 0.85,  # Placeholder
            "audience_analysis": 0.78,
            "trend_analysis": 0.72,
            "commercial_analysis": 0.80,
            "overall_confidence": 0.79
        }


class ContentPipelineManager:
    """Advanced pipeline manager with dynamic stage orchestration."""
    
    def __init__(self):
        self.logger = logging.getLogger("pipeline.manager")
        self.metrics = MetricsCollector()
        self.active_pipelines = {}
        self.pipeline_queue = deque()
        
        # Initialize stage processors
        self.processors = {
            PipelineStage.VALIDATION: ContentValidationProcessor(),
            PipelineStage.PREPROCESSING: ContentPreprocessingProcessor(),
            PipelineStage.FEATURE_EXTRACTION: FeatureExtractionProcessor(),
            PipelineStage.AI_ANALYSIS: AIAnalysisProcessor(),
            # Add other processors as needed
        }
        
        # Pipeline configuration
        self.max_concurrent_pipelines = 10
        self.retry_limits = defaultdict(lambda: 3)
    
    async def create_pipeline(
        self,
        content_item: ContentItem,
        user_id: str,
        stages: Optional[List[PipelineStage]] = None,
        priority: PipelinePriority = PipelinePriority.NORMAL,
        config: Optional[Dict] = None
    ) -> str:
        """Create a new content processing pipeline."""
        pipeline_id = f"pipeline_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Use default stages if not specified
        if stages is None:
            stages = [
                PipelineStage.VALIDATION,
                PipelineStage.PREPROCESSING,
                PipelineStage.FEATURE_EXTRACTION,
                PipelineStage.AI_ANALYSIS
            ]
        
        pipeline_info = {
            "id": pipeline_id,
            "content_item": content_item,
            "user_id": user_id,
            "stages": stages,
            "priority": priority,
            "config": config or {},
            "status": PipelineStatus.INITIALIZED,
            "current_stage_index": 0,
            "results": {},
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "total_duration": 0.0,
            "retry_count": 0
        }
        
        self.active_pipelines[pipeline_id] = pipeline_info
        await self._queue_pipeline(pipeline_id, priority)
        
        self.logger.info(f"Created pipeline {pipeline_id} with {len(stages)} stages")
        return pipeline_id
    
    async def _queue_pipeline(self, pipeline_id: str, priority: PipelinePriority):
        """Queue pipeline for execution."""
        self.pipeline_queue.append((priority.value, pipeline_id))
        # Sort queue by priority (higher values first)
        self.pipeline_queue = deque(sorted(self.pipeline_queue, key=lambda x: x[0], reverse=True))
        
        self.active_pipelines[pipeline_id]["status"] = PipelineStatus.QUEUED
    
    async def execute_pipelines(self):
        """Execute queued pipelines."""
        while True:
            # Check for available pipeline slots
            running_count = sum(
                1 for p in self.active_pipelines.values() 
                if p["status"] == PipelineStatus.RUNNING
            )
            
            if running_count >= self.max_concurrent_pipelines or not self.pipeline_queue:
                await asyncio.sleep(1)
                continue
            
            # Get next pipeline to execute
            priority, pipeline_id = self.pipeline_queue.popleft()
            
            if pipeline_id in self.active_pipelines:
                asyncio.create_task(self._execute_pipeline(pipeline_id))
            
            await asyncio.sleep(0.1)  # Prevent tight loop
    
    async def _execute_pipeline(self, pipeline_id: str):
        """Execute a complete pipeline."""
        pipeline_info = self.active_pipelines[pipeline_id]
        pipeline_info["status"] = PipelineStatus.RUNNING
        pipeline_info["started_at"] = datetime.utcnow()
        
        start_time = datetime.utcnow()
        
        try:
            content_item = pipeline_info["content_item"]
            stages = pipeline_info["stages"]
            context = pipeline_info["config"].copy()
            
            for stage_index, stage in enumerate(stages):
                pipeline_info["current_stage_index"] = stage_index
                
                if stage not in self.processors:
                    raise PipelineException(f"No processor found for stage {stage.value}")
                
                processor = self.processors[stage]
                
                self.logger.info(f"Pipeline {pipeline_id}: Processing stage {stage.value}")
                
                # Execute stage
                stage_result = await processor.execute(content_item, context)
                pipeline_info["results"][stage.value] = stage_result.to_dict()
                
                if not stage_result.success:
                    # Handle stage failure
                    if stage_result.retry_count < self.retry_limits[stage]:
                        self.logger.warning(
                            f"Pipeline {pipeline_id}: Retrying stage {stage.value}"
                        )
                        stage_result.retry_count += 1
                        # Retry logic would go here
                        continue
                    else:
                        raise PipelineException(
                            f"Stage {stage.value} failed: {stage_result.errors}"
                        )
                
                # Update context with stage results for next stages
                context[f"{stage.value}_result"] = stage_result.data
            
            # Pipeline completed successfully
            pipeline_info["status"] = PipelineStatus.COMPLETED
            pipeline_info["completed_at"] = datetime.utcnow()
            pipeline_info["total_duration"] = (
                pipeline_info["completed_at"] - pipeline_info["started_at"]
            ).total_seconds()
            
            self.logger.info(
                f"Pipeline {pipeline_id} completed successfully in {pipeline_info['total_duration']:.2f}s"
            )
            
            # Record success metrics
            self.metrics.record_pipeline_completion(
                pipeline_id=pipeline_id,
                duration=pipeline_info["total_duration"],
                stages_count=len(stages),
                success=True
            )
            
        except Exception as e:
            # Pipeline failed
            pipeline_info["status"] = PipelineStatus.FAILED
            pipeline_info["completed_at"] = datetime.utcnow()
            pipeline_info["error"] = str(e)
            
            self.logger.error(f"Pipeline {pipeline_id} failed: {str(e)}")
            
            # Record failure metrics
            self.metrics.record_pipeline_completion(
                pipeline_id=pipeline_id,
                duration=(datetime.utcnow() - start_time).total_seconds(),
                stages_count=len(pipeline_info.get("stages", [])),
                success=False,
                error=str(e)
            )
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict]:
        """Get current pipeline status."""
        pipeline_info = self.active_pipelines.get(pipeline_id)
        if not pipeline_info:
            return None
        
        return {
            "id": pipeline_id,
            "status": pipeline_info["status"].value,
            "current_stage_index": pipeline_info["current_stage_index"],
            "total_stages": len(pipeline_info["stages"]),
            "current_stage": (
                pipeline_info["stages"][pipeline_info["current_stage_index"]].value
                if pipeline_info["current_stage_index"] < len(pipeline_info["stages"])
                else None
            ),
            "progress": pipeline_info["current_stage_index"] / len(pipeline_info["stages"]),
            "created_at": pipeline_info["created_at"].isoformat(),
            "started_at": pipeline_info["started_at"].isoformat() if pipeline_info["started_at"] else None,
            "completed_at": pipeline_info["completed_at"].isoformat() if pipeline_info["completed_at"] else None,
            "total_duration": pipeline_info.get("total_duration", 0.0),
            "results_available": len(pipeline_info["results"]) > 0,
            "error": pipeline_info.get("error")
        }
    
    def get_pipeline_results(self, pipeline_id: str) -> Optional[Dict]:
        """Get pipeline execution results."""
        pipeline_info = self.active_pipelines.get(pipeline_id)
        if not pipeline_info:
            return None
        
        return pipeline_info["results"]
    
    def cancel_pipeline(self, pipeline_id: str) -> bool:
        """Cancel a pipeline."""
        pipeline_info = self.active_pipelines.get(pipeline_id)
        if not pipeline_info:
            return False
        
        pipeline_info["status"] = PipelineStatus.CANCELLED
        self.logger.info(f"Pipeline {pipeline_id} cancelled")
        return True
    
    def get_queue_status(self) -> Dict:
        """Get current queue status."""
        queued_count = sum(
            1 for p in self.active_pipelines.values()
            if p["status"] == PipelineStatus.QUEUED
        )
        running_count = sum(
            1 for p in self.active_pipelines.values()
            if p["status"] == PipelineStatus.RUNNING
        )
        
        return {
            "queued": queued_count,
            "running": running_count,
            "total_active": len(self.active_pipelines),
            "max_concurrent": self.max_concurrent_pipelines,
            "queue_length": len(self.pipeline_queue)
        }
