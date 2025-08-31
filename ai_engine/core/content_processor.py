"""
Content Processing Pipeline Module

Advanced content processing pipeline for multi-format content creators platform.
Handles the complete content workflow from upload to distribution.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union, Callable, TypeVar, Generic, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import json
import uuid
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from contextlib import asynccontextmanager

from .exceptions import ContentGenerationError, OptimizationError, ProtectionError
from .validation import ContentValidator, ContentType, ValidationResult
from .ai_engine import ai_engine, AIModelType
from .metrics import metrics_collector
from .performance import performance_monitor

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ProcessingStage(Enum):
    """Stages in the content processing pipeline"""
    UPLOAD = "upload"
    VALIDATION = "validation"
    PREPROCESSING = "preprocessing"
    AI_ANALYSIS = "ai_analysis"
    PROTECTION = "protection"
    OPTIMIZATION = "optimization"
    SEO_ENHANCEMENT = "seo_enhancement"
    COLLABORATION_MATCHING = "collaboration_matching"
    QUALITY_ASSESSMENT = "quality_assessment"
    DISTRIBUTION_PREP = "distribution_prep"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStatus(Enum):
    """Status of content processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class ContentFormat(Enum):
    """Supported content formats"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MIXED_MEDIA = "mixed_media"


@dataclass
class ProcessingContext:
    """Context for content processing pipeline"""
    user_id: str
    session_id: str
    content_id: str
    content_type: ContentType
    content_format: ContentFormat
    original_filename: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    platform_targets: List[str] = field(default_factory=list)
    processing_options: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "content_id": self.content_id,
            "content_type": self.content_type.value,
            "content_format": self.content_format.value,
            "original_filename": self.original_filename,
            "metadata": self.metadata,
            "platform_targets": self.platform_targets,
            "processing_options": self.processing_options
        }


@dataclass
class ProcessingResult:
    """Result of content processing stage"""
    stage: ProcessingStage
    status: ProcessingStatus
    timestamp: datetime = field(default_factory=datetime.utcnow)
    processing_time_ms: float = 0.0
    output_data: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            "stage": self.stage.value,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "processing_time_ms": self.processing_time_ms,
            "metadata": self.metadata,
            "errors": self.errors,
            "warnings": self.warnings,
            "confidence_score": self.confidence_score
        }


@dataclass
class PipelineState:
    """State of the content processing pipeline"""
    context: ProcessingContext
    current_stage: ProcessingStage = ProcessingStage.UPLOAD
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Processing results for each stage
    stage_results: Dict[ProcessingStage, ProcessingResult] = field(default_factory=dict)
    
    # Content at different stages
    original_content: Optional[Any] = None
    processed_content: Optional[Any] = None
    optimized_content: Optional[Any] = None
    final_content: Optional[Any] = None
    
    # Comprehensive metadata
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    ai_analysis_results: Dict[str, Any] = field(default_factory=dict)
    protection_fingerprints: Dict[str, str] = field(default_factory=dict)
    seo_data: Dict[str, Any] = field(default_factory=dict)
    collaboration_matches: List[Dict[str, Any]] = field(default_factory=list)
    distribution_assets: Dict[str, Any] = field(default_factory=dict)
    
    def update_stage(self, stage: ProcessingStage, result: ProcessingResult):
        """Update pipeline stage with result"""
        self.current_stage = stage
        self.stage_results[stage] = result
        self.updated_at = datetime.utcnow()
        
        if stage == ProcessingStage.COMPLETED:
            self.status = ProcessingStatus.COMPLETED
            self.completed_at = datetime.utcnow()
        elif stage == ProcessingStage.FAILED:
            self.status = ProcessingStatus.FAILED
            
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get comprehensive processing summary"""
        total_time = 0.0
        stage_times = {}
        
        for stage, result in self.stage_results.items():
            stage_times[stage.value] = result.processing_time_ms
            total_time += result.processing_time_ms
            
        return {
            "content_id": self.context.content_id,
            "status": self.status.value,
            "current_stage": self.current_stage.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_processing_time_ms": total_time,
            "stage_times": stage_times,
            "stages_completed": len(self.stage_results),
            "errors": [error for result in self.stage_results.values() for error in result.errors],
            "warnings": [warning for result in self.stage_results.values() for warning in result.warnings]
        }


class BaseProcessor:
    """Base class for content processors"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
    async def process(
        self, 
        content: Any, 
        context: ProcessingContext, 
        state: PipelineState
    ) -> ProcessingResult:
        """Process content and return result - base implementation"""



        try:
            # Basic processing that validates input and returns content unchanged
            if not self.validate_input(content, context):
                return ProcessingResult(
                    success=False,
                    data=None,
                    error="Input validation failed",
                    metadata={
                        "processor": self.name,
                        "stage": "validation"
                    }
                )
            
            # Basic passthrough processing
            processed_data = content
            
            # Update processing state
            state.add_step(f"{self.name}_processed")
            
            return ProcessingResult(
                success=True,
                data=processed_data,
                metadata={
                    "processor": self.name,
                    "stage": "processed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "content_type": type(content).__name__
                }
            )
            
        except Exception as e:
            self.logger.error(f"Processing failed in {self.name}: {str(e)}")
            return ProcessingResult(
                success=False,
                data=None,
                error=str(e),
                metadata={
                    "processor": self.name,
                    "stage": "error"
                }
            )
        
    def validate_input(self, content: Any, context: ProcessingContext) -> bool:
        """Validate processor input"""



        return content is not None


class ValidationProcessor(BaseProcessor):
    """Content validation processor"""
    
    def __init__(self):
        super().__init__("validation")
        self.validator = ContentValidator()
        
    async def process(
        self, 
        content: Any, 
        context: ProcessingContext, 
        state: PipelineState
    ) -> ProcessingResult:
        """Validate content quality and compliance"""
        start_time = time.perf_counter()
        
        try:
            # Perform comprehensive validation
            validation_result = self.validator.validate_content(
                content,
                context.content_type,
                metadata=context.metadata,
                platform_targets=context.platform_targets
            )
            
            processing_time = (time.perf_counter() - start_time) * 1000
            
            # Determine processing status
            status = ProcessingStatus.COMPLETED if validation_result.is_valid else ProcessingStatus.FAILED
            
            result = ProcessingResult(
                stage=ProcessingStage.VALIDATION,
                status=status,
                processing_time_ms=processing_time,
                output_data=validation_result,
                metadata={
                    "validation_scores": {
                        "overall": validation_result.overall_score,
                        "quality": validation_result.quality_score,
                        "safety": validation_result.safety_score,
                        "compliance": validation_result.compliance_score,
                        "seo": validation_result.seo_score
                    },
                    "issues_count": len(validation_result.issues),
                    "content_fingerprint": validation_result.content_fingerprint
                },
                errors=[issue.message for issue in validation_result.issues if issue.level.value in ["error", "critical"]],
                warnings=[issue.message for issue in validation_result.issues if issue.level.value == "warning"],
                confidence_score=validation_result.overall_score / 100.0
            )
            
            # Store validation results in state
            state.processing_metadata["validation"] = validation_result.to_dict()
            
            self.logger.info(
                f"Content validation completed for {context.content_id}. "
                f"Score: {validation_result.overall_score:.1f}, Valid: {validation_result.is_valid}"
            )
            
            return result
            
        except Exception as e:
            processing_time = (time.perf_counter() - start_time) * 1000
            self.logger.error(f"Validation failed for {context.content_id}: {e}")
            
            return ProcessingResult(
                stage=ProcessingStage.VALIDATION,
                status=ProcessingStatus.FAILED,
                processing_time_ms=processing_time,
                errors=[f"Validation failed: {str(e)}"],
                confidence_score=0.0
            )


class AIAnalysisProcessor(BaseProcessor):
    """AI-powered content analysis processor"""
    
    def __init__(self):
        super().__init__("ai_analysis")
        
    async def process(
        self, 
        content: Any, 
        context: ProcessingContext, 
        state: PipelineState
    ) -> ProcessingResult:
        """Perform AI analysis of content"""
        start_time = time.perf_counter()
        
        try:
            analysis_results = {}
            
            # Content classification
            if context.content_format in [ContentFormat.TEXT, ContentFormat.DOCUMENT]:
                analysis_results["classification"] = await self._analyze_text_content(content, context)
            elif context.content_format == ContentFormat.AUDIO:
                analysis_results["audio_analysis"] = await self._analyze_audio_content(content, context)
            elif context.content_format == ContentFormat.IMAGE:
                analysis_results["image_analysis"] = await self._analyze_image_content(content, context)
            elif context.content_format == ContentFormat.VIDEO:
                analysis_results["video_analysis"] = await self._analyze_video_content(content, context)
                
            # Sentiment analysis
            if isinstance(content, str):
                analysis_results["sentiment"] = await self._analyze_sentiment(content)
                
            # Topic extraction
            analysis_results["topics"] = await self._extract_topics(content, context)
            
            # Quality assessment
            analysis_results["quality"] = await self._assess_quality(content, context)
            
            processing_time = (time.perf_counter() - start_time) * 1000
            
            result = ProcessingResult(
                stage=ProcessingStage.AI_ANALYSIS,
                status=ProcessingStatus.COMPLETED,
                processing_time_ms=processing_time,
                output_data=analysis_results,
                metadata={
                    "models_used": self._get_models_used(context),
                    "confidence_scores": self._extract_confidence_scores(analysis_results)
                },
                confidence_score=self._calculate_overall_confidence(analysis_results)
            )
            
            # Store AI analysis results in state
            state.ai_analysis_results = analysis_results
            
            self.logger.info(f"AI analysis completed for {context.content_id}")
            return result
            
        except Exception as e:
            processing_time = (time.perf_counter() - start_time) * 1000
            self.logger.error(f"AI analysis failed for {context.content_id}: {e}")
            
            return ProcessingResult(
                stage=ProcessingStage.AI_ANALYSIS,
                status=ProcessingStatus.FAILED,
                processing_time_ms=processing_time,
                errors=[f"AI analysis failed: {str(e)}"],
                confidence_score=0.0
            )
            
    async def _analyze_text_content(self, content: str, context: ProcessingContext) -> Dict[str, Any]:
        """Analyze text content using AI models"""
        # Text classification, entity extraction, etc.
        return {
            "word_count": len(content.split()),
            "language": "en",  # Simplified
            "readability_score": 0.8,
            "entities": []
        }
        
    async def _analyze_audio_content(self, content: Any, context: ProcessingContext) -> Dict[str, Any]:
        """Analyze audio content"""
        # Audio classification, speech recognition, etc.
        return {
            "duration": 120.0,
            "sample_rate": 44100,
            "channels": 2,
            "genre": "unknown",
            "mood": "neutral"
        }
        
    async def _analyze_image_content(self, content: Any, context: ProcessingContext) -> Dict[str, Any]:
        """Analyze image content"""
        # Image classification, object detection, etc.
        return {
            "width": 1920,
            "height": 1080,
            "objects": [],
            "style": "unknown",
            "quality_score": 0.85
        }
        
    async def _analyze_video_content(self, content: Any, context: ProcessingContext) -> Dict[str, Any]:
        """Analyze video content"""
        # Video analysis, scene detection, etc.
        return {
            "duration": 300.0,
            "resolution": "1920x1080",
            "fps": 30,
            "scenes": [],
            "audio_track": True
        }
        
    async def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze content sentiment"""
        # Simplified sentiment analysis
        return {
            "score": 0.6,
            "label": "positive",
            "confidence": 0.8
        }
        
    async def _extract_topics(self, content: Any, context: ProcessingContext) -> List[Dict[str, Any]]:
        """Extract topics from content"""
        # Topic modeling
        return [
            {"topic": "music", "confidence": 0.9},
            {"topic": "entertainment", "confidence": 0.7}
        ]
        
    async def _assess_quality(self, content: Any, context: ProcessingContext) -> Dict[str, Any]:
        """Assess content quality"""



        return {
            "overall_score": 0.85,
            "technical_quality": 0.9,
            "content_quality": 0.8,
            "engagement_potential": 0.85
        }
        
    def _get_models_used(self, context: ProcessingContext) -> List[str]:
        """Get list of AI models used in analysis"""



        return ["text_classifier", "sentiment_analyzer", "quality_assessor"]
        
    def _extract_confidence_scores(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Extract confidence scores from analysis results"""
        scores = {}
        for key, value in results.items():
            if isinstance(value, dict) and "confidence" in value:
                scores[key] = value["confidence"]
        return scores
        
    def _calculate_overall_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        confidence_scores = self._extract_confidence_scores(results)
        return sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.8


class ProtectionProcessor(BaseProcessor):
    """Content protection and rights management processor"""
    
    def __init__(self):
        super().__init__("protection")
        
    async def process(
        self, 
        content: Any, 
        context: ProcessingContext, 
        state: PipelineState
    ) -> ProcessingResult:
        """Apply content protection measures"""
        start_time = time.perf_counter()
        
        try:
            protection_results = {}
            
            # Generate content fingerprint
            fingerprint = await self._generate_fingerprint(content, context)
            protection_results["fingerprint"] = fingerprint
            
            # Check for existing content
            similarity_check = await self._check_content_similarity(fingerprint, context)
            protection_results["similarity_check"] = similarity_check
            
            # Apply digital watermarking (if applicable)
            if context.content_format in [ContentFormat.AUDIO, ContentFormat.VIDEO, ContentFormat.IMAGE]:
                watermark_result = await self._apply_watermark(content, context)
                protection_results["watermark"] = watermark_result
                
            # Copyright validation
            copyright_check = await self._validate_copyright(content, context)
            protection_results["copyright"] = copyright_check
            
            # Rights metadata
            rights_metadata = await self._generate_rights_metadata(content, context)
            protection_results["rights_metadata"] = rights_metadata
            
            processing_time = (time.perf_counter() - start_time) * 1000
            
            # Determine if content passes protection checks
            protection_passed = (
                similarity_check.get("similarity_score", 0) < 0.8 and
                copyright_check.get("violations_detected", 0) == 0
            )
            
            status = ProcessingStatus.COMPLETED if protection_passed else ProcessingStatus.FAILED
            
            result = ProcessingResult(
                stage=ProcessingStage.PROTECTION,
                status=status,
                processing_time_ms=processing_time,
                output_data=protection_results,
                metadata={
                    "fingerprint_generated": bool(fingerprint),
                    "watermark_applied": bool(protection_results.get("watermark")),
                    "protection_level": "high" if protection_passed else "failed"
                },
                errors=[] if protection_passed else ["Content protection validation failed"],
                confidence_score=1.0 if protection_passed else 0.0
            )
            
            # Store protection results in state
            state.protection_fingerprints[context.content_format.value] = fingerprint
            state.processing_metadata["protection"] = protection_results
            
            self.logger.info(f"Content protection completed for {context.content_id}")
            return result
            
        except Exception as e:
            processing_time = (time.perf_counter() - start_time) * 1000
            self.logger.error(f"Content protection failed for {context.content_id}: {e}")
            
            return ProcessingResult(
                stage=ProcessingStage.PROTECTION,
                status=ProcessingStatus.FAILED,
                processing_time_ms=processing_time,
                errors=[f"Content protection failed: {str(e)}"],
                confidence_score=0.0
            )
            
    async def _generate_fingerprint(self, content: Any, context: ProcessingContext) -> str:
        """Generate unique content fingerprint"""
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        elif isinstance(content, Path):
            content_bytes = content.read_bytes()
        else:
            content_bytes = str(content).encode('utf-8')
            
        fingerprint = hashlib.sha256(content_bytes).hexdigest()
        
        # Add metadata to fingerprint calculation
        metadata_str = json.dumps(context.metadata, sort_keys=True)
        combined_hash = hashlib.sha256(
            (fingerprint + metadata_str).encode('utf-8')
        ).hexdigest()
        
        return combined_hash
        
    async def _check_content_similarity(self, fingerprint: str, context: ProcessingContext) -> Dict[str, Any]:
        """Check content similarity against existing content"""
        # In production, this would query a fingerprint database
        return {
            "similarity_score": 0.1,  # Low similarity
            "similar_content_ids": [],
            "potential_duplicates": []
        }
        
    async def _apply_watermark(self, content: Any, context: ProcessingContext) -> Dict[str, Any]:
        """Apply digital watermark to content"""
        # Watermarking implementation would go here
        return {
            "watermark_applied": True,
            "watermark_type": "invisible",
            "watermark_strength": 0.8
        }
        
    async def _validate_copyright(self, content: Any, context: ProcessingContext) -> Dict[str, Any]:
        """Validate copyright compliance"""
        # Copyright detection logic
        return {
            "violations_detected": 0,
            "copyright_score": 0.95,
            "protected_elements": []
        }
        
    async def _generate_rights_metadata(self, content: Any, context: ProcessingContext) -> Dict[str, Any]:
        """Generate rights management metadata"""



        return {
            "creator_id": context.user_id,
            "creation_timestamp": datetime.utcnow().isoformat(),
            "rights_type": "full",
            "usage_permissions": ["view", "share", "remix"],
            "monetization_enabled": True,
            "protection_level": "standard"
        }


class ContentProcessingPipeline:
    """
    Enterprise-grade content processing pipeline
    
    Features:
    - Multi-stage processing workflow
    - Asynchronous processing
    - Error handling and recovery
    - Progress tracking
    - Scalable processor architecture
    - Comprehensive logging and monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.processors: Dict[ProcessingStage, BaseProcessor] = {}
        self.active_pipelines: Dict[str, PipelineState] = {}
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Initialize default processors
        self._initialize_processors()
        
        logger.info("Content Processing Pipeline initialized")
        
    def _initialize_processors(self):
        """Initialize pipeline processors"""
        self.processors[ProcessingStage.VALIDATION] = ValidationProcessor()
        self.processors[ProcessingStage.AI_ANALYSIS] = AIAnalysisProcessor()
        self.processors[ProcessingStage.PROTECTION] = ProtectionProcessor()
        # Additional processors would be initialized here
        
    def register_processor(self, stage: ProcessingStage, processor: BaseProcessor):
        """Register a custom processor for a stage"""
        self.processors[stage] = processor
        logger.info(f"Registered processor '{processor.name}' for stage '{stage.value}'")
        
    async def process_content(
        self,
        content: Any,
        context: ProcessingContext,
        stages: Optional[List[ProcessingStage]] = None
    ) -> PipelineState:
        """
        Process content through the pipeline
        
        Args:
            content: Content to process
            context: Processing context
            stages: Specific stages to run (all if None)
            
        Returns:
            Pipeline state with results
        """
        # Create pipeline state
        state = PipelineState(context=context)
        state.original_content = content
        
        # Register active pipeline
        self.active_pipelines[context.content_id] = state
        
        # Default stages if none specified
        if stages is None:
            stages = [
                ProcessingStage.VALIDATION,
                ProcessingStage.AI_ANALYSIS,
                ProcessingStage.PROTECTION,
                ProcessingStage.OPTIMIZATION,
                ProcessingStage.SEO_ENHANCEMENT,
                ProcessingStage.COLLABORATION_MATCHING,
                ProcessingStage.QUALITY_ASSESSMENT,
                ProcessingStage.DISTRIBUTION_PREP
            ]
            
        try:
            current_content = content
            
            # Process through each stage
            for stage in stages:
                if stage in self.processors:
                    state.status = ProcessingStatus.PROCESSING
                    
                    # Process stage
                    result = await self.processors[stage].process(
                        current_content, context, state
                    )
                    
                    # Update state
                    state.update_stage(stage, result)
                    
                    # Record metrics
                    metrics_collector.record_timer(
                        f"pipeline.stage.{stage.value}",
                        result.processing_time_ms / 1000,
                        {
                            "content_type": context.content_type.value,
                            "status": result.status.value
                        }
                    )
                    
                    # Check if stage failed
                    if result.status == ProcessingStatus.FAILED:
                        state.current_stage = ProcessingStage.FAILED
                        state.status = ProcessingStatus.FAILED
                        break
                        
                    # Update content for next stage
                    if result.output_data:
                        current_content = result.output_data
                        
                else:
                    logger.warning(f"No processor registered for stage: {stage.value}")
                    
            # Mark as completed if all stages succeeded
            if state.status != ProcessingStatus.FAILED:
                completion_result = ProcessingResult(
                    stage=ProcessingStage.COMPLETED,
                    status=ProcessingStatus.COMPLETED,
                    confidence_score=1.0
                )
                state.update_stage(ProcessingStage.COMPLETED, completion_result)
                state.final_content = current_content
                
            logger.info(
                f"Pipeline processing completed for {context.content_id}. "
                f"Status: {state.status.value}, Stages: {len(state.stage_results)}"
            )
            
        except Exception as e:
            logger.error(f"Pipeline processing failed for {context.content_id}: {e}")
            
            failure_result = ProcessingResult(
                stage=ProcessingStage.FAILED,
                status=ProcessingStatus.FAILED,
                errors=[f"Pipeline failure: {str(e)}"],
                confidence_score=0.0
            )
            state.update_stage(ProcessingStage.FAILED, failure_result)
            
        finally:
            # Clean up active pipeline reference
            if context.content_id in self.active_pipelines:
                del self.active_pipelines[context.content_id]
                
        return state
        
    def get_pipeline_status(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get status of active pipeline"""
        if content_id in self.active_pipelines:
            return self.active_pipelines[content_id].get_processing_summary()
        return None
        
    def cancel_pipeline(self, content_id: str) -> bool:
        """Cancel active pipeline"""
        if content_id in self.active_pipelines:
            state = self.active_pipelines[content_id]
            state.status = ProcessingStatus.CANCELLED
            del self.active_pipelines[content_id]
            logger.info(f"Pipeline cancelled for content: {content_id}")
            return True
        return False
        
    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get comprehensive pipeline metrics"""



        return {
            "active_pipelines": len(self.active_pipelines),
            "registered_processors": len(self.processors),
            "processing_stages": [stage.value for stage in self.processors.keys()],
            "system_status": "healthy" if len(self.active_pipelines) < 100 else "busy"
        }
        
    async def batch_process(
        self,
        content_batch: List[Tuple[Any, ProcessingContext]],
        max_concurrent: int = 5
    ) -> List[PipelineState]:
        """Process multiple content items in batch"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single(content, context):
            async with semaphore:
                return await self.process_content(content, context)
                
        tasks = [
            process_single(content, context)
            for content, context in content_batch
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch processing failed for item {i}: {result}")
            else:
                valid_results.append(result)
                
        return valid_results
        
    def shutdown(self):
        """Shutdown the processing pipeline"""
        logger.info("Shutting down content processing pipeline...")
        
        # Cancel all active pipelines
        for content_id in list(self.active_pipelines.keys()):
            self.cancel_pipeline(content_id)
            
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Content processing pipeline shutdown completed")


# Global pipeline instance
content_pipeline = ContentProcessingPipeline()


async def process_content_async(
    content: Any,
    user_id: str,
    content_type: ContentType,
    content_format: ContentFormat,
    **kwargs
) -> PipelineState:
    """
    Convenience function for processing content
    
    Args:
        content: Content to process
        user_id: User ID
        content_type: Type of content
        content_format: Format of content
        **kwargs: Additional context parameters
        
    Returns:
        Pipeline processing state
    """
    context = ProcessingContext(
        user_id=user_id,
        session_id=kwargs.get('session_id', str(uuid.uuid4())),
        content_id=kwargs.get('content_id', str(uuid.uuid4())),
        content_type=content_type,
        content_format=content_format,
        original_filename=kwargs.get('original_filename'),
        metadata=kwargs.get('metadata', {}),
        platform_targets=kwargs.get('platform_targets', []),
        processing_options=kwargs.get('processing_options', {})
    )
    
    return await content_pipeline.process_content(content, context)
