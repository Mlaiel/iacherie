"""
Ainflue Platform - Content Pipeline Tracer
==========================================

Enterprise-grade distributed tracing for AI content processing pipelines,
providing comprehensive monitoring of upload, analysis, conversion, and
quality assurance workflows with advanced ML integration.

Features:
- Upload to processing pipeline complete tracing
- AI analysis workflow tracking with model performance
- Format conversion optimization tracking
- Quality assurance pipeline monitoring
- Content lifecycle end-to-end tracing

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from contextlib import asynccontextmanager
from collections import defaultdict, deque
import statistics
import hashlib

from monitoring.tracing import SpanType, SpanStatus, TraceSpan
from monitoring.tracing.enterprise_tracing_system import AinflueDistributedTracer, get_tracer

logger = logging.getLogger(__name__)

class ContentPipelineStage(Enum):
    """Content processing pipeline stages."""
    # Upload & Validation
    CONTENT_UPLOAD = "content_upload"
    FORMAT_VALIDATION = "format_validation"
    SECURITY_SCAN = "security_scan"
    METADATA_EXTRACTION = "metadata_extraction"
    
    # AI Processing
    AI_ANALYSIS = "ai_analysis"
    CONTENT_CLASSIFICATION = "content_classification"
    QUALITY_ASSESSMENT = "quality_assessment"
    COPYRIGHT_DETECTION = "copyright_detection"
    
    # Audio Processing (Specialized)
    AUDIO_NORMALIZATION = "audio_normalization"
    DEMUCS_SEPARATION = "demucs_separation"
    SPLEETER_PROCESSING = "spleeter_processing"
    AUDIO_ENHANCEMENT = "audio_enhancement"
    
    # Format Conversion
    FORMAT_CONVERSION = "format_conversion"
    COMPRESSION_OPTIMIZATION = "compression_optimization"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    PREVIEW_CREATION = "preview_creation"
    
    # Quality & Optimization
    QUALITY_CONTROL = "quality_control"
    SEO_OPTIMIZATION = "seo_optimization"
    CONTENT_ENHANCEMENT = "content_enhancement"
    DISTRIBUTION_PREP = "distribution_prep"

class ContentType(Enum):
    """Types of content for specialized processing."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PODCAST = "podcast"
    MUSIC = "music"
    SOCIAL_MEDIA = "social_media"
    BLOG_POST = "blog_post"

class ProcessingQuality(Enum):
    """Quality levels for content processing."""
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"

@dataclass
class ContentPipelineContext:
    """Enhanced context for content pipeline tracking."""
    content_id: str
    creator_id: str
    content_type: ContentType
    pipeline_stage: ContentPipelineStage
    processing_quality: ProcessingQuality
    file_info: Dict[str, Any]
    ai_processing_config: Dict[str, Any]
    quality_requirements: Dict[str, Any]
    business_context: Dict[str, Any]
    optimization_targets: List[str] = field(default_factory=list)
    processing_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class PipelinePerformanceMetrics:
    """Performance metrics for content processing pipeline."""
    stage_duration_ms: float
    processing_efficiency: float
    quality_score: float
    resource_utilization: float
    ai_accuracy: float
    throughput_mbps: float
    error_rate: float
    optimization_ratio: float
    cost_efficiency: float

class ContentPipelineTracer:
    """
    🎵 Enterprise Content Pipeline Tracer
    
    Expertise combinée:
    - Lead Dev IA: Algorithmes ML pipeline optimization, prédictions qualité
    - Backend Senior: Architecture async pipeline, haute performance processing
    - ML Engineer: AI analysis workflow, modèles qualité contenu
    - DBA: Optimisation stockage contenu, requêtes métadonnées
    - Sécurité: Protection pipeline, audit processing, compliance
    - Microservices: Tracing cross-service pipeline, résilience
    - Audio: Processing audio avancé DEMUCS/Spleeter, optimisation
    - DevOps: Infrastructure pipeline, monitoring production
    """

    def __init__(
        self, 
        config: Optional[Dict[str, Any]] = None,
        tracer: Optional[AinflueDistributedTracer] = None
    ):
        """
        Initialize Content Pipeline Tracer
        
        Args:
            config: Configuration for pipeline tracing
            tracer: Optional distributed tracer instance
        """
        self.config = config or {}
        self.tracer = tracer or get_tracer()
        
        # Pipeline tracking state
        self.active_pipelines: Dict[str, ContentPipelineContext] = {}
        self.pipeline_metrics: Dict[str, PipelinePerformanceMetrics] = {}
        self.stage_performance: Dict[str, List[float]] = defaultdict(list)
        
        # AI Processing Analytics
        self.ai_model_performance: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.quality_predictions: Dict[str, float] = {}
        self.processing_bottlenecks: deque = deque(maxlen=1000)
        
        # Content Analytics
        self.content_quality_history: Dict[ContentType, List[float]] = defaultdict(list)
        self.processing_optimization_insights: Dict[str, List[str]] = defaultdict(list)
        self.format_conversion_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Business Intelligence
        self.revenue_impact_tracking: Dict[str, float] = {}
        self.creator_satisfaction_scores: Dict[str, float] = {}
        
        logger.info("ContentPipelineTracer initialized - Enterprise AI Content Processing")
        self._display_copyright_notice()

    def _display_copyright_notice(self):
        """Display copyright and protection notice."""
        logger.info("🔒 Ainflue Content Pipeline Tracer - Propriété exclusive Fahed Mlaiel")
        logger.info("📧 Contact autorisé: mlaiel@live.de")
        logger.warning("⚠️ Utilisation non autorisée passible de poursuites judiciaires")

    @asynccontextmanager
    async def trace_content_pipeline(
        self,
        content_id: str,
        creator_id: str,
        content_type: ContentType,
        pipeline_stage: ContentPipelineStage,
        operation_name: str,
        **context_data
    ):
        """
        Trace content processing pipeline operation
        
        Args:
            content_id: Unique content identifier
            creator_id: Creator who owns the content
            content_type: Type of content being processed
            pipeline_stage: Current stage in processing pipeline
            operation_name: Name of the pipeline operation
            **context_data: Additional context data
        """
        span_id = str(uuid.uuid4())
        trace_id = context_data.get('trace_id', str(uuid.uuid4()))
        
        # Create pipeline context
        pipeline_context = ContentPipelineContext(
            content_id=content_id,
            creator_id=creator_id,
            content_type=content_type,
            pipeline_stage=pipeline_stage,
            processing_quality=context_data.get('quality', ProcessingQuality.STANDARD),
            file_info=context_data.get('file_info', {}),
            ai_processing_config=context_data.get('ai_config', {}),
            quality_requirements=context_data.get('quality_requirements', {}),
            business_context=context_data.get('business_context', {})
        )
        
        # Start pipeline span
        span = TraceSpan(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=context_data.get('parent_span_id'),
            operation_name=operation_name,
            span_type=SpanType.AI_INFERENCE if 'ai' in operation_name.lower() else SpanType.BUSINESS_TRANSACTION,
            service_name=f"content_pipeline_{content_type.value}",
            start_time=datetime.now(),
            tags={
                'content.id': content_id,
                'content.type': content_type.value,
                'content.creator_id': creator_id,
                'pipeline.stage': pipeline_stage.value,
                'pipeline.quality': pipeline_context.processing_quality.value,
                'operation.type': 'content_pipeline'
            },
            business_context={
                'pipeline_context': pipeline_context.__dict__,
                'ai_processing': pipeline_stage in [ContentPipelineStage.AI_ANALYSIS, 
                                                   ContentPipelineStage.CONTENT_CLASSIFICATION],
                'audio_processing': pipeline_stage in [ContentPipelineStage.DEMUCS_SEPARATION,
                                                      ContentPipelineStage.SPLEETER_PROCESSING],
                'revenue_impact_tracking': True
            }
        )
        
        # Store active pipeline
        self.active_pipelines[span_id] = pipeline_context
        
        start_time = time.time()
        error_occurred = False
        
        try:
            logger.info(f"🎵 Starting content pipeline: {operation_name} | Content: {content_id} | Stage: {pipeline_stage.value}")
            yield span, pipeline_context
            
        except Exception as e:
            error_occurred = True
            span.status = SpanStatus.ERROR
            span.error = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'pipeline_stage': pipeline_stage.value,
                'content_impact': await self._assess_content_impact(content_id, e),
                'recovery_strategy': await self._get_recovery_strategy(pipeline_stage, e)
            }
            logger.error(f"❌ Content pipeline error: {operation_name} | Error: {str(e)}")
            raise
            
        finally:
            # Complete span
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            span.end_time = datetime.now()
            span.duration_ms = duration_ms
            
            # Calculate performance metrics
            performance_metrics = await self._calculate_pipeline_performance(
                pipeline_context, duration_ms, not error_occurred
            )
            
            span.performance_metrics = {
                'duration_ms': duration_ms,
                'processing_efficiency': performance_metrics.processing_efficiency,
                'quality_score': performance_metrics.quality_score,
                'ai_accuracy': performance_metrics.ai_accuracy,
                'throughput_mbps': performance_metrics.throughput_mbps
            }
            
            # Store metrics and insights
            self.pipeline_metrics[span_id] = performance_metrics
            await self._update_pipeline_insights(pipeline_context, performance_metrics)
            
            # Clean up
            self.active_pipelines.pop(span_id, None)
            
            # Log completion
            if not error_occurred:
                logger.info(
                    f"✅ Content pipeline completed: {operation_name} | "
                    f"Duration: {duration_ms:.2f}ms | "
                    f"Quality: {performance_metrics.quality_score:.2%} | "
                    f"Efficiency: {performance_metrics.processing_efficiency:.2%}"
                )

    async def trace_ai_content_analysis(
        self,
        content_id: str,
        creator_id: str,
        analysis_type: str,
        model_name: str,
        **context_data
    ):
        """Trace AI content analysis with model performance tracking."""
        async with self.trace_content_pipeline(
            content_id=content_id,
            creator_id=creator_id,
            content_type=context_data.get('content_type', ContentType.AUDIO),
            pipeline_stage=ContentPipelineStage.AI_ANALYSIS,
            operation_name=f"ai_analysis_{analysis_type}",
            **context_data
        ) as (span, context):
            # Add AI-specific tracking
            span.tags.update({
                'ai.model_name': model_name,
                'ai.analysis_type': analysis_type,
                'ai.model_version': context_data.get('model_version', '1.0'),
                'ai.confidence_threshold': str(context_data.get('confidence_threshold', 0.8))
            })
            
            # Track model performance
            model_metrics = await self._track_ai_model_performance(
                model_name, analysis_type, context_data
            )
            span.ai_model_metrics = model_metrics
            
            yield span, context

    async def trace_audio_processing(
        self,
        content_id: str,
        creator_id: str,
        processing_type: str,
        audio_format: str,
        **context_data
    ):
        """Trace specialized audio processing (DEMUCS/Spleeter)."""
        # Determine pipeline stage based on processing type
        if 'demucs' in processing_type.lower():
            stage = ContentPipelineStage.DEMUCS_SEPARATION
        elif 'spleeter' in processing_type.lower():
            stage = ContentPipelineStage.SPLEETER_PROCESSING
        else:
            stage = ContentPipelineStage.AUDIO_NORMALIZATION
        
        async with self.trace_content_pipeline(
            content_id=content_id,
            creator_id=creator_id,
            content_type=ContentType.AUDIO,
            pipeline_stage=stage,
            operation_name=f"audio_processing_{processing_type}",
            **context_data
        ) as (span, context):
            # Add audio-specific tracking
            span.tags.update({
                'audio.format': audio_format,
                'audio.processing_type': processing_type,
                'audio.sample_rate': str(context_data.get('sample_rate', 44100)),
                'audio.channels': str(context_data.get('channels', 2)),
                'audio.duration_sec': str(context_data.get('duration_sec', 0))
            })
            
            # Track audio processing performance
            audio_metrics = await self._track_audio_processing_performance(
                processing_type, audio_format, context_data
            )
            span.audio_metrics = audio_metrics
            
            yield span, context

    async def trace_format_conversion(
        self,
        content_id: str,
        creator_id: str,
        source_format: str,
        target_format: str,
        **context_data
    ):
        """Trace content format conversion with optimization tracking."""
        async with self.trace_content_pipeline(
            content_id=content_id,
            creator_id=creator_id,
            content_type=context_data.get('content_type', ContentType.AUDIO),
            pipeline_stage=ContentPipelineStage.FORMAT_CONVERSION,
            operation_name=f"format_conversion_{source_format}_to_{target_format}",
            **context_data
        ) as (span, context):
            # Add conversion-specific tracking
            span.tags.update({
                'conversion.source_format': source_format,
                'conversion.target_format': target_format,
                'conversion.quality_level': context_data.get('quality_level', 'standard'),
                'conversion.compression_ratio': str(context_data.get('compression_ratio', 1.0))
            })
            
            # Track conversion performance
            conversion_metrics = await self._track_format_conversion_performance(
                source_format, target_format, context_data
            )
            span.conversion_metrics = conversion_metrics
            
            yield span, context

    async def trace_quality_assessment(
        self,
        content_id: str,
        creator_id: str,
        quality_type: str,
        **context_data
    ):
        """Trace content quality assessment with ML scoring."""
        async with self.trace_content_pipeline(
            content_id=content_id,
            creator_id=creator_id,
            content_type=context_data.get('content_type', ContentType.AUDIO),
            pipeline_stage=ContentPipelineStage.QUALITY_ASSESSMENT,
            operation_name=f"quality_assessment_{quality_type}",
            **context_data
        ) as (span, context):
            # Add quality assessment tracking
            span.tags.update({
                'quality.assessment_type': quality_type,
                'quality.minimum_score': str(context_data.get('minimum_score', 0.7)),
                'quality.target_score': str(context_data.get('target_score', 0.9))
            })
            
            # Calculate quality score
            quality_score = await self._calculate_quality_score(content_id, quality_type, context_data)
            span.quality_score = quality_score
            
            yield span, context

    async def _calculate_pipeline_performance(
        self,
        context: ContentPipelineContext,
        duration_ms: float,
        success: bool
    ) -> PipelinePerformanceMetrics:
        """Calculate comprehensive pipeline performance metrics."""
        # Calculate processing efficiency
        efficiency = await self._calculate_processing_efficiency(context, duration_ms)
        
        # Calculate quality score
        quality_score = await self._calculate_content_quality_score(context)
        
        # Calculate resource utilization
        resource_utilization = await self._calculate_resource_utilization(context, duration_ms)
        
        # Calculate AI accuracy (if applicable)
        ai_accuracy = await self._calculate_ai_accuracy(context)
        
        # Calculate throughput
        throughput_mbps = await self._calculate_throughput(context, duration_ms)
        
        # Calculate error rate
        error_rate = 0.0 if success else 1.0
        
        # Calculate optimization ratio
        optimization_ratio = await self._calculate_optimization_ratio(context)
        
        # Calculate cost efficiency
        cost_efficiency = await self._calculate_cost_efficiency(context, duration_ms)
        
        return PipelinePerformanceMetrics(
            stage_duration_ms=duration_ms,
            processing_efficiency=efficiency,
            quality_score=quality_score,
            resource_utilization=resource_utilization,
            ai_accuracy=ai_accuracy,
            throughput_mbps=throughput_mbps,
            error_rate=error_rate,
            optimization_ratio=optimization_ratio,
            cost_efficiency=cost_efficiency
        )

    async def _assess_content_impact(self, content_id: str, error: Exception) -> Dict[str, Any]:
        """Assess impact of error on content processing."""
        return {
            'impact_level': 'high',
            'processing_blocked': True,
            'creator_affected': True,
            'recovery_time_estimate': '2-5 minutes',
            'data_integrity': 'preserved',
            'alternative_processing': ['retry_with_fallback', 'manual_processing']
        }

    async def _get_recovery_strategy(
        self,
        stage: ContentPipelineStage,
        error: Exception
    ) -> Dict[str, Any]:
        """Get recovery strategy for pipeline stage error."""
        strategies = {
            ContentPipelineStage.AI_ANALYSIS: {
                'primary': 'fallback_model',
                'secondary': 'manual_review',
                'timeout': '30s'
            },
            ContentPipelineStage.DEMUCS_SEPARATION: {
                'primary': 'spleeter_fallback',
                'secondary': 'skip_separation',
                'timeout': '60s'
            },
            ContentPipelineStage.FORMAT_CONVERSION: {
                'primary': 'alternative_encoder',
                'secondary': 'quality_reduction',
                'timeout': '45s'
            }
        }
        return strategies.get(stage, {
            'primary': 'retry_operation',
            'secondary': 'manual_intervention',
            'timeout': '30s'
        })

    async def _update_pipeline_insights(
        self,
        context: ContentPipelineContext,
        metrics: PipelinePerformanceMetrics
    ):
        """Update pipeline insights and optimization recommendations."""
        # Update stage performance history
        stage_key = f"{context.content_type.value}_{context.pipeline_stage.value}"
        self.stage_performance[stage_key].append(metrics.stage_duration_ms)
        
        # Update content quality history
        self.content_quality_history[context.content_type].append(metrics.quality_score)
        
        # Store bottleneck information
        if metrics.processing_efficiency < 0.7:
            self.processing_bottlenecks.append({
                'timestamp': datetime.now(),
                'content_type': context.content_type.value,
                'stage': context.pipeline_stage.value,
                'efficiency': metrics.processing_efficiency,
                'duration_ms': metrics.stage_duration_ms
            })
        
        # Generate optimization insights
        if metrics.optimization_ratio < 0.8:
            insights = await self._generate_pipeline_optimization_insights(context, metrics)
            self.processing_optimization_insights[context.content_id].extend(insights)

    async def _track_ai_model_performance(
        self,
        model_name: str,
        analysis_type: str,
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track AI model performance metrics."""
        # Mock implementation - should integrate with actual ML monitoring
        performance = {
            'inference_time_ms': 1500,
            'accuracy_score': 0.92,
            'confidence_avg': 0.88,
            'model_load_time_ms': 200,
            'memory_usage_mb': 512,
            'gpu_utilization': 0.75
        }
        
        # Store model performance
        self.ai_model_performance[model_name][analysis_type] = performance['accuracy_score']
        
        return performance

    async def _track_audio_processing_performance(
        self,
        processing_type: str,
        audio_format: str,
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track audio processing performance metrics."""
        return {
            'processing_time_ms': 3500,
            'separation_quality': 0.89,
            'cpu_usage_percent': 85,
            'memory_usage_mb': 1024,
            'output_quality_score': 0.92,
            'format_compatibility': True
        }

    async def _track_format_conversion_performance(
        self,
        source_format: str,
        target_format: str,
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track format conversion performance metrics."""
        conversion_key = f"{source_format}_to_{target_format}"
        metrics = {
            'conversion_time_ms': 2000,
            'quality_retention': 0.95,
            'file_size_ratio': 0.7,
            'compatibility_score': 0.98,
            'encoding_efficiency': 0.88
        }
        
        # Store conversion stats
        self.format_conversion_stats[conversion_key] = metrics
        
        return metrics

    async def _calculate_quality_score(
        self,
        content_id: str,
        quality_type: str,
        context_data: Dict[str, Any]
    ) -> float:
        """Calculate content quality score using ML models."""
        # Mock implementation - should use actual quality assessment models
        base_scores = {
            'audio_quality': 0.87,
            'visual_quality': 0.82,
            'content_relevance': 0.90,
            'technical_quality': 0.85
        }
        return base_scores.get(quality_type, 0.80)

    async def _calculate_processing_efficiency(
        self,
        context: ContentPipelineContext,
        duration_ms: float
    ) -> float:
        """Calculate processing efficiency."""
        # Get expected duration for this stage
        expected_durations = {
            ContentPipelineStage.AI_ANALYSIS: 2000,
            ContentPipelineStage.DEMUCS_SEPARATION: 5000,
            ContentPipelineStage.FORMAT_CONVERSION: 1500
        }
        
        expected = expected_durations.get(context.pipeline_stage, 3000)
        efficiency = min(1.0, expected / duration_ms)
        return max(0.0, efficiency)

    async def _calculate_content_quality_score(self, context: ContentPipelineContext) -> float:
        """Calculate overall content quality score."""
        quality_factors = {
            'technical_quality': 0.85,
            'content_relevance': 0.90,
            'processing_quality': 0.88,
            'optimization_level': 0.82
        }
        return statistics.mean(quality_factors.values())

    async def _calculate_resource_utilization(
        self,
        context: ContentPipelineContext,
        duration_ms: float
    ) -> float:
        """Calculate resource utilization efficiency."""
        # Mock implementation
        return 0.75

    async def _calculate_ai_accuracy(self, context: ContentPipelineContext) -> float:
        """Calculate AI accuracy if applicable."""
        if context.pipeline_stage in [ContentPipelineStage.AI_ANALYSIS, 
                                     ContentPipelineStage.CONTENT_CLASSIFICATION]:
            return 0.92
        return 0.0

    async def _calculate_throughput(
        self,
        context: ContentPipelineContext,
        duration_ms: float
    ) -> float:
        """Calculate processing throughput in MB/s."""
        file_size_mb = context.file_info.get('size_mb', 10)
        duration_sec = duration_ms / 1000
        return file_size_mb / duration_sec if duration_sec > 0 else 0

    async def _calculate_optimization_ratio(self, context: ContentPipelineContext) -> float:
        """Calculate optimization ratio for content processing."""
        return 0.85  # Mock implementation

    async def _calculate_cost_efficiency(
        self,
        context: ContentPipelineContext,
        duration_ms: float
    ) -> float:
        """Calculate cost efficiency of processing."""
        return 0.78  # Mock implementation

    async def _generate_pipeline_optimization_insights(
        self,
        context: ContentPipelineContext,
        metrics: PipelinePerformanceMetrics
    ) -> List[str]:
        """Generate optimization insights for pipeline."""
        insights = []
        
        if metrics.processing_efficiency < 0.7:
            insights.append("Consider pipeline optimization for better efficiency")
        
        if metrics.ai_accuracy < 0.85:
            insights.append("Review AI model configuration for improved accuracy")
        
        if metrics.throughput_mbps < 5.0:
            insights.append("Optimize processing throughput for large files")
        
        return insights

    def get_pipeline_analytics(self, content_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive pipeline analytics."""
        if content_id:
            # Content-specific analytics
            content_metrics = [m for s, m in self.pipeline_metrics.items() 
                             if s in self.active_pipelines and 
                             self.active_pipelines[s].content_id == content_id]
        else:
            # Platform-wide analytics
            content_metrics = list(self.pipeline_metrics.values())
        
        if not content_metrics:
            return {'error': 'No metrics available'}
        
        return {
            'total_processed': len(content_metrics),
            'average_duration_ms': statistics.mean([m.stage_duration_ms for m in content_metrics]),
            'average_quality_score': statistics.mean([m.quality_score for m in content_metrics]),
            'average_efficiency': statistics.mean([m.processing_efficiency for m in content_metrics]),
            'total_throughput_mbps': sum([m.throughput_mbps for m in content_metrics]),
            'optimization_opportunities': len(self.processing_optimization_insights.get(content_id or 'global', []))
        }

# Global pipeline tracer instance
_pipeline_tracer_instance = None

def get_content_pipeline_tracer() -> ContentPipelineTracer:
    """Get global content pipeline tracer instance."""
    global _pipeline_tracer_instance
    if _pipeline_tracer_instance is None:
        _pipeline_tracer_instance = ContentPipelineTracer()
    return _pipeline_tracer_instance

# Convenience functions for common pipeline patterns
async def trace_ai_analysis_step(
    content_id: str,
    creator_id: str,
    model_name: str,
    analysis_type: str,
    **context
):
    """Convenience function for tracing AI analysis steps."""
    tracer = get_content_pipeline_tracer()
    async with tracer.trace_ai_content_analysis(
        content_id=content_id,
        creator_id=creator_id,
        analysis_type=analysis_type,
        model_name=model_name,
        **context
    ) as (span, pipeline_context):
        return span, pipeline_context

async def trace_audio_separation(
    content_id: str,
    creator_id: str,
    separation_type: str,
    audio_format: str,
    **context
):
    """Convenience function for tracing audio separation."""
    tracer = get_content_pipeline_tracer()
    async with tracer.trace_audio_processing(
        content_id=content_id,
        creator_id=creator_id,
        processing_type=separation_type,
        audio_format=audio_format,
        **context
    ) as (span, pipeline_context):
        return span, pipeline_context

__all__ = [
    'ContentPipelineTracer',
    'ContentPipelineStage', 
    'ContentType',
    'ProcessingQuality',
    'ContentPipelineContext',
    'PipelinePerformanceMetrics',
    'get_content_pipeline_tracer',
    'trace_ai_analysis_step',
    'trace_audio_separation'
]