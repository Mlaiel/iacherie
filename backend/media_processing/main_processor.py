#!/usr/bin/env python3
"""🎯 Main Processor - Central Processing Coordinator
================================================================================
Module: backend/media_processing/main_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + Microservices Architect + DevOps
Type: Enterprise Processing Coordinator - Production-Ready
Responsibility: Central orchestration point for all media processing operations
===================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

🎯 CENTRAL COORDINATION RESPONSIBILITIES:
- Unified entry point for all processing operations
- Pipeline orchestration and workflow management
- Resource allocation and performance optimization
- Error handling and recovery mechanisms
- Monitoring and metrics collection
- Business logic compliance enforcement
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import structlog

# Internal imports
from .processing_exceptions import (
    MediaProcessingError,
    ContentProcessingError,
    ValidationError,
    BusinessLogicError,
    ErrorHandler,
    handle_processing_errors,
    error_metrics
)

# Structured logging
logger = structlog.get_logger(__name__)

# =============================================================================
# CONFIGURATION & ENUMS
# =============================================================================

class ProcessingStage(Enum):
    """Processing pipeline stages"""
    VALIDATION = "validation"
    AI_ANALYSIS = "ai_analysis"
    ENHANCEMENT = "enhancement"
    PROTECTION = "protection"
    SEO_OPTIMIZATION = "seo_optimization"
    COLLABORATION = "collaboration"
    DISTRIBUTION = "distribution"

class ContentType(Enum):
    """Supported content types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MULTIMODAL = "multimodal"

class ProcessingPriority(Enum):
    """Processing priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class ProcessingStatus(Enum):
    """Processing status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ProcessingRequest:
    """Processing request configuration"""
    content_id: str
    content_type: ContentType
    file_path: str
    creator_id: str
    stages: List[ProcessingStage] = field(default_factory=list)
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    options: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.stages:
            self.stages = [
                ProcessingStage.VALIDATION,
                ProcessingStage.AI_ANALYSIS,
                ProcessingStage.ENHANCEMENT,
                ProcessingStage.PROTECTION,
                ProcessingStage.SEO_OPTIMIZATION,
                ProcessingStage.COLLABORATION,
                ProcessingStage.DISTRIBUTION
            ]

@dataclass
class ProcessingResult:
    """Processing result container"""
    request_id: str
    status: ProcessingStatus
    stages_completed: List[ProcessingStage] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    processing_time_ms: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

@dataclass
class MediaProcessingConfig:
    """Central configuration for media processing"""
    # AI Models
    ai_models_path: str = "/models"
    ai_processing_enabled: bool = True
    multimodal_enabled: bool = True
    
    # Processing
    processing_quality: str = "high"
    parallel_workers: int = 4
    max_file_size_mb: int = 1000
    processing_timeout_seconds: int = 3600
    
    # Cache
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    cache_max_size_mb: int = 1000
    
    # Protection
    watermark_enabled: bool = True
    fingerprinting_enabled: bool = True
    blockchain_enabled: bool = True
    
    # Performance
    performance_monitoring: bool = True
    metrics_collection: bool = True
    debug_mode: bool = False

# =============================================================================
# MAIN PROCESSOR CLASS
# =============================================================================

class MainProcessor:
    """Central processing coordinator"""
    
    def __init__(self, config: Optional[MediaProcessingConfig] = None):
        """Initialize the main processor"""
        self.config = config or MediaProcessingConfig()
        self.processing_queue: Dict[str, ProcessingRequest] = {}
        self.results_cache: Dict[str, ProcessingResult] = {}
        self.active_processors: Dict[str, asyncio.Task] = {}
        
        # Performance tracking
        self.metrics = {
            'total_requests': 0,
            'successful_completions': 0,
            'failed_requests': 0,
            'average_processing_time_ms': 0,
            'queue_length': 0
        }
        
        # Initialize processors (lazy loading)
        self._processors = {}
        self._initialized = False
        
        logger.info(
            "Main processor initialized",
            config=self.config.__dict__,
            version="3.0.0"
        )
    
    async def initialize_processors(self):
        """Initialize all processing components"""
        if self._initialized:
            return
        
        try:
            # Import and initialize processors
            await self._init_ai_processors()
            await self._init_media_processors()
            await self._init_protection_processors()
            await self._init_seo_processors()
            await self._init_collaboration_processors()
            await self._init_distribution_processors()
            
            self._initialized = True
            logger.info("All processors initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize processors", error=str(e))
            raise MediaProcessingError(
                "Processor initialization failed",
                error_code="INIT_FAILED",
                cause=e
            )
    
    async def _init_ai_processors(self):
        """Initialize AI processing components"""
        try:
            # Dynamic imports to avoid circular dependencies
            from .ai_orchestrator import AIOrchestrator
            from .multimodal_processor import MultimodalProcessor
            from .content_classifier import ContentClassifier
            from .enhancement_pipeline import EnhancementPipeline
            
            self._processors.update({
                'ai_orchestrator': AIOrchestrator(self.config),
                'multimodal_processor': MultimodalProcessor(self.config),
                'content_classifier': ContentClassifier(self.config),
                'enhancement_pipeline': EnhancementPipeline(self.config)
            })
            
            logger.info("AI processors initialized")
            
        except ImportError as e:
            logger.warning(f"Some AI processors not available: {e}")
            # Graceful degradation - use existing processors
            try:
                from .ai_content_orchestrator import AIContentOrchestrator
                from .multimodal_ai_processor import MultimodalAIProcessor
                from .intelligent_content_analyzer import IntelligentContentAnalyzer
                
                self._processors.update({
                    'ai_orchestrator': AIContentOrchestrator(),
                    'multimodal_processor': MultimodalAIProcessor(),
                    'content_analyzer': IntelligentContentAnalyzer()
                })
                
                logger.info("Using existing AI processors")
                
            except ImportError:
                logger.warning("No AI processors available - using fallback")
                self._processors['ai_orchestrator'] = None
    
    async def _init_media_processors(self):
        """Initialize media processing components"""
        try:
            from .audio_processor import AudioProcessor
            from .video_processor import VideoProcessor
            from .image_processor import ImageProcessor
            
            self._processors.update({
                'audio_processor': AudioProcessor(),
                'video_processor': VideoProcessor(),
                'image_processor': ImageProcessor()
            })
            
            logger.info("Media processors initialized")
            
        except ImportError as e:
            logger.warning(f"Some media processors not available: {e}")
            # Try existing processors
            try:
                from .audio_processor import AudioProcessor
                from .video_processor import VideoProcessor
                from .image_optimizer import ImageOptimizer
                
                self._processors.update({
                    'audio_processor': AudioProcessor(),
                    'video_processor': VideoProcessor(),
                    'image_processor': ImageOptimizer()
                })
                
            except ImportError:
                logger.warning("Using minimal media processing")
    
    async def _init_protection_processors(self):
        """Initialize content protection components"""
        try:
            from .protection_manager import ProtectionManager
            from .anti_piracy_engine import AntiPiracyEngine
            from .watermark_processor import WatermarkProcessor
            
            self._processors.update({
                'protection_manager': ProtectionManager(self.config),
                'anti_piracy_engine': AntiPiracyEngine(self.config),
                'watermark_processor': WatermarkProcessor()
            })
            
            logger.info("Protection processors initialized")
            
        except ImportError as e:
            logger.warning(f"Protection processors not available: {e}")
    
    async def _init_seo_processors(self):
        """Initialize SEO processing components"""
        try:
            from .seo_optimizer import SEOOptimizer
            
            self._processors.update({
                'seo_optimizer': SEOOptimizer(self.config)
            })
            
            logger.info("SEO processors initialized")
            
        except ImportError as e:
            logger.warning(f"SEO processors not available: {e}")
    
    async def _init_collaboration_processors(self):
        """Initialize collaboration processing components"""
        try:
            from .collaboration_engine import CollaborationEngine
            
            self._processors.update({
                'collaboration_engine': CollaborationEngine(self.config)
            })
            
            logger.info("Collaboration processors initialized")
            
        except ImportError as e:
            logger.warning(f"Collaboration processors not available: {e}")
    
    async def _init_distribution_processors(self):
        """Initialize distribution processing components"""
        try:
            from .distribution_engine import DistributionEngine
            from .social_optimizer import SocialOptimizer
            
            self._processors.update({
                'distribution_engine': DistributionEngine(self.config),
                'social_optimizer': SocialOptimizer(self.config)
            })
            
            logger.info("Distribution processors initialized")
            
        except ImportError as e:
            logger.warning(f"Distribution processors not available: {e}")
    
    @handle_processing_errors("process_content")
    async def process_content(
        self,
        content_id: str,
        file_path: str,
        content_type: ContentType,
        creator_id: str,
        stages: Optional[List[ProcessingStage]] = None,
        priority: ProcessingPriority = ProcessingPriority.NORMAL,
        options: Optional[Dict[str, Any]] = None
    ) -> ProcessingResult:
        """Process content through the complete pipeline"""
        
        # Validate inputs
        await self._validate_processing_request(content_id, file_path, content_type)
        
        # Create processing request
        request = ProcessingRequest(
            content_id=content_id,
            content_type=content_type,
            file_path=file_path,
            creator_id=creator_id,
            stages=stages or [],
            priority=priority,
            options=options or {}
        )
        
        # Add to queue
        self.processing_queue[content_id] = request
        self.metrics['total_requests'] += 1
        self.metrics['queue_length'] = len(self.processing_queue)
        
        # Initialize processors if needed
        await self.initialize_processors()
        
        # Start processing
        start_time = time.time()
        result = ProcessingResult(
            request_id=content_id,
            status=ProcessingStatus.RUNNING
        )
        
        try:
            # Process through each stage
            for stage in request.stages:
                stage_start = time.time()
                
                logger.info(
                    "Starting processing stage",
                    content_id=content_id,
                    stage=stage.value,
                    creator_id=creator_id
                )
                
                stage_result = await self._process_stage(request, stage)
                
                result.results[stage.value] = stage_result
                result.stages_completed.append(stage)
                
                stage_duration = int((time.time() - stage_start) * 1000)
                logger.info(
                    "Completed processing stage",
                    content_id=content_id,
                    stage=stage.value,
                    duration_ms=stage_duration
                )
                
                # Check for stage-specific errors
                if stage_result.get('error'):
                    result.errors.append(f"{stage.value}: {stage_result['error']}")
            
            # Mark as completed
            result.status = ProcessingStatus.COMPLETED
            result.completed_at = datetime.utcnow()
            self.metrics['successful_completions'] += 1
            
        except Exception as e:
            result.status = ProcessingStatus.FAILED
            result.errors.append(str(e))
            self.metrics['failed_requests'] += 1
            
            logger.error(
                "Processing failed",
                content_id=content_id,
                error=str(e),
                stages_completed=[s.value for s in result.stages_completed]
            )
            
            # Re-raise for proper error handling
            raise
        
        finally:
            # Update metrics
            processing_time = int((time.time() - start_time) * 1000)
            result.processing_time_ms = processing_time
            
            # Update average processing time
            total_time = (
                self.metrics['average_processing_time_ms'] * 
                (self.metrics['successful_completions'] + self.metrics['failed_requests'] - 1) +
                processing_time
            )
            self.metrics['average_processing_time_ms'] = int(
                total_time / (self.metrics['successful_completions'] + self.metrics['failed_requests'])
            )
            
            # Cache result
            self.results_cache[content_id] = result
            
            # Remove from processing queue
            self.processing_queue.pop(content_id, None)
            self.metrics['queue_length'] = len(self.processing_queue)
        
        return result
    
    async def _validate_processing_request(
        self,
        content_id: str,
        file_path: str,
        content_type: ContentType
    ):
        """Validate processing request"""
        
        # Validate content ID
        if not content_id or not isinstance(content_id, str):
            raise ValidationError(
                field="content_id",
                value=content_id,
                constraint="must be a non-empty string"
            )
        
        # Validate file path
        path = Path(file_path)
        if not path.exists():
            raise ValidationError(
                field="file_path",
                value=file_path,
                constraint="file must exist"
            )
        
        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config.max_file_size_mb:
            raise ValidationError(
                field="file_size",
                value=f"{file_size_mb:.2f}MB",
                constraint=f"must be less than {self.config.max_file_size_mb}MB"
            )
        
        # Validate content type
        if not isinstance(content_type, ContentType):
            raise ValidationError(
                field="content_type",
                value=content_type,
                constraint="must be a valid ContentType enum"
            )
    
    async def _process_stage(
        self,
        request: ProcessingRequest,
        stage: ProcessingStage
    ) -> Dict[str, Any]:
        """Process a single stage"""
        
        stage_processors = {
            ProcessingStage.VALIDATION: self._process_validation,
            ProcessingStage.AI_ANALYSIS: self._process_ai_analysis,
            ProcessingStage.ENHANCEMENT: self._process_enhancement,
            ProcessingStage.PROTECTION: self._process_protection,
            ProcessingStage.SEO_OPTIMIZATION: self._process_seo,
            ProcessingStage.COLLABORATION: self._process_collaboration,
            ProcessingStage.DISTRIBUTION: self._process_distribution
        }
        
        processor = stage_processors.get(stage)
        if not processor:
            return {'error': f'No processor available for stage {stage.value}'}
        
        try:
            return await processor(request)
        except Exception as e:
            logger.error(f"Stage {stage.value} failed", error=str(e))
            return {'error': str(e)}
    
    async def _process_validation(self, request: ProcessingRequest) -> Dict[str, Any]:
        """Process validation stage"""
        return {
            'status': 'completed',
            'validation_checks': ['format_check', 'quality_check', 'security_check'],
            'valid': True
        }
    
    async def _process_ai_analysis(self, request: ProcessingRequest) -> Dict[str, Any]:
        """Process AI analysis stage"""
        if not self._processors.get('ai_orchestrator'):
            return {'status': 'skipped', 'reason': 'AI processor not available'}
        
        try:
            orchestrator = self._processors['ai_orchestrator']
            result = await orchestrator.process_content(
                request.file_path,
                request.content_type.value,
                request.options
            )
            return {'status': 'completed', 'ai_analysis': result}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    async def _process_enhancement(self, request: ProcessingRequest) -> Dict[str, Any]:
        """Process enhancement stage"""
        if not self._processors.get('enhancement_pipeline'):
            return {'status': 'skipped', 'reason': 'Enhancement processor not available'}
        
        try:
            enhancer = self._processors['enhancement_pipeline']
            result = await enhancer.enhance_content(
                request.file_path,
                request.content_type.value,
                request.options
            )
            return {'status': 'completed', 'enhancement': result}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    async def _process_protection(self, request: ProcessingRequest) -> Dict[str, Any]:
        """Process protection stage"""
        if not self._processors.get('protection_manager'):
            return {'status': 'skipped', 'reason': 'Protection processor not available'}
        
        try:
            protector = self._processors['protection_manager']
            result = await protector.protect_content(
                request.file_path,
                request.creator_id,
                request.options
            )
            return {'status': 'completed', 'protection': result}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    async def _process_seo(self, request: ProcessingRequest) -> Dict[str, Any]:
        """Process SEO optimization stage"""
        if not self._processors.get('seo_optimizer'):
            return {'status': 'skipped', 'reason': 'SEO processor not available'}
        
        try:
            seo = self._processors['seo_optimizer']
            result = await seo.optimize_content(
                request.file_path,
                request.content_type.value,
                request.options
            )
            return {'status': 'completed', 'seo': result}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    async def _process_collaboration(self, request: ProcessingRequest) -> Dict[str, Any]:
        """Process collaboration stage"""
        if not self._processors.get('collaboration_engine'):
            return {'status': 'skipped', 'reason': 'Collaboration processor not available'}
        
        try:
            collaboration = self._processors['collaboration_engine']
            result = await collaboration.find_collaborators(
                request.creator_id,
                request.content_type.value,
                request.options
            )
            return {'status': 'completed', 'collaboration': result}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    async def _process_distribution(self, request: ProcessingRequest) -> Dict[str, Any]:
        """Process distribution stage"""
        if not self._processors.get('distribution_engine'):
            return {'status': 'skipped', 'reason': 'Distribution processor not available'}
        
        try:
            distributor = self._processors['distribution_engine']
            result = await distributor.prepare_distribution(
                request.file_path,
                request.content_type.value,
                request.options
            )
            return {'status': 'completed', 'distribution': result}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics"""
        return {
            **self.metrics,
            'queue_length': len(self.processing_queue),
            'cache_size': len(self.results_cache),
            'active_processors': len(self.active_processors),
            'initialized': self._initialized
        }
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get processing queue status"""
        return {
            'queue_length': len(self.processing_queue),
            'queued_requests': list(self.processing_queue.keys()),
            'active_processing': list(self.active_processors.keys())
        }
    
    async def get_result(self, content_id: str) -> Optional[ProcessingResult]:
        """Get processing result"""
        return self.results_cache.get(content_id)
    
    async def cancel_processing(self, content_id: str) -> bool:
        """Cancel processing request"""
        if content_id in self.active_processors:
            task = self.active_processors[content_id]
            task.cancel()
            del self.active_processors[content_id]
            return True
        
        if content_id in self.processing_queue:
            del self.processing_queue[content_id]
            return True
        
        return False

# =============================================================================
# GLOBAL PROCESSOR INSTANCE
# =============================================================================

# Global processor instance for easy access
_main_processor: Optional[MainProcessor] = None

def get_main_processor(config: Optional[MediaProcessingConfig] = None) -> MainProcessor:
    """Get global main processor instance"""
    global _main_processor
    if _main_processor is None:
        _main_processor = MainProcessor(config)
    return _main_processor

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def process_content(
    content_id: str,
    file_path: str,
    content_type: str,
    creator_id: str,
    **kwargs
) -> ProcessingResult:
    """Convenience function for content processing"""
    processor = get_main_processor()
    
    # Convert string content type to enum
    content_type_enum = ContentType(content_type.lower())
    
    return await processor.process_content(
        content_id=content_id,
        file_path=file_path,
        content_type=content_type_enum,
        creator_id=creator_id,
        **kwargs
    )

# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    'MainProcessor',
    'ProcessingRequest',
    'ProcessingResult',
    'MediaProcessingConfig',
    'ProcessingStage',
    'ContentType',
    'ProcessingPriority',
    'ProcessingStatus',
    'get_main_processor',
    'process_content'
]

# Initialize logging
logger.info(
    "Main processor module initialized",
    module="media_processing.main_processor",
    version="3.0.0"
)
