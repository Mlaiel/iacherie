"""Content Pipeline Monitor - Specialized Monitoring for IA Influencer Agent Content Processing

Advanced monitoring system for multi-format content processing pipelines including
fingerprinting, AI analysis, protection, and monetization workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

⚠️  AVERTISSEMENT STRICT - PROPRIÉTÉ INTELLECTUELLE ⚠️
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute violation sera poursuivie selon les lois en vigueur.
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from collections import defaultdict, deque
import statistics

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_database_session
from ...core.config import Settings
from ...utils.cache import RedisCache
from ...ai.analysis.content_pipeline_ai import ContentPipelineAnalyzer


class ContentType(Enum):
    """Content type classification for IA Influencer Agent"""    AUDIO = "audio"          # Music files, podcasts, voice recordings
    VIDEO = "video"          # Video content, streams, recordings  
    IMAGE = "image"          # Photos, graphics, artwork
    TEXT = "text"            # Blog posts, social media content
    DOCUMENT = "document"    # PDFs, presentations, documents
    MIXED = "mixed"          # Multi-format content packages


class PipelineStage(Enum):
    """Content processing pipeline stages"""    UPLOAD = "upload"                    # Initial content upload
    VALIDATION = "validation"            # Content validation and preprocessing
    FINGERPRINTING = "fingerprinting"    # AI fingerprint generation
    AI_ANALYSIS = "ai_analysis"         # AI content analysis and tagging
    PROTECTION = "protection"           # Rights protection and licensing
    SEO_OPTIMIZATION = "seo_optimization" # SEO and metadata optimization
    COLLABORATION = "collaboration"      # Creator collaboration matching
    MONETIZATION = "monetization"       # Revenue tracking and optimization
    DISTRIBUTION = "distribution"       # Multi-platform distribution
    ANALYTICS = "analytics"             # Performance analytics


class PipelineStatus(Enum):
    """Pipeline execution status"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class ContentProcessingMetrics:
    """Metrics for content processing pipeline"""    content_id: str
    content_type: ContentType
    creator_id: str
    pipeline_stage: PipelineStage
    status: PipelineStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    processing_duration: Optional[float] = None
    file_size_mb: float = 0.0
    quality_score: float = 0.0
    ai_confidence: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""        data = {
            'content_id': self.content_id,
            'content_type': self.content_type.value,
            'creator_id': self.creator_id,
            'pipeline_stage': self.pipeline_stage.value,
            'status': self.status.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'processing_duration': self.processing_duration,
            'file_size_mb': self.file_size_mb,
            'quality_score': self.quality_score,
            'ai_confidence': self.ai_confidence,
            'error_message': self.error_message,
            'metadata': self.metadata
        }
        return data


@dataclass
class PipelinePerformanceSnapshot:
    """Pipeline performance snapshot"""    timestamp: datetime
    active_content_count: int
    pending_content_count: int
    processing_rate_per_minute: float
    average_processing_time: float
    success_rate_percentage: float
    error_rate_percentage: float
    throughput_mb_per_second: float
    ai_processing_efficiency: float
    fingerprinting_accuracy: float
    protection_effectiveness: float
    monetization_conversion_rate: float
    creator_satisfaction_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        data = {
            'timestamp': self.timestamp.isoformat(),
            'active_content_count': self.active_content_count,
            'pending_content_count': self.pending_content_count,
            'processing_rate_per_minute': self.processing_rate_per_minute,
            'average_processing_time': self.average_processing_time,
            'success_rate_percentage': self.success_rate_percentage,
            'error_rate_percentage': self.error_rate_percentage,
            'throughput_mb_per_second': self.throughput_mb_per_second,
            'ai_processing_efficiency': self.ai_processing_efficiency,
            'fingerprinting_accuracy': self.fingerprinting_accuracy,
            'protection_effectiveness': self.protection_effectiveness,
            'monetization_conversion_rate': self.monetization_conversion_rate,
            'creator_satisfaction_score': self.creator_satisfaction_score
        }
        return data


class ContentPipelineMonitor:
    """    Advanced content pipeline monitoring for IA Influencer Agent platform.
    
    Monitors multi-format content processing including:
    - Audio fingerprinting and analysis
    - Video content protection
    - Image rights management
    - Text content optimization
    - AI-powered content enhancement
    - Creator collaboration workflows
    - Monetization pipeline performance
    """    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.cache = RedisCache()
        self.ai_analyzer = ContentPipelineAnalyzer()
        
        # Pipeline tracking
        self.active_pipelines: Dict[str, ContentProcessingMetrics] = {}
        self.pipeline_history: deque = deque(maxlen=10000)  # Keep last 10k pipeline runs
        self.performance_snapshots: deque = deque(maxlen=1440)  # 24 hours of minutes
        
        # Performance thresholds for IA Influencer Agent
        self.thresholds = {
            'audio_processing_time_seconds': 30.0,     # Max time for audio fingerprinting
            'video_processing_time_seconds': 120.0,    # Max time for video analysis
            'image_processing_time_seconds': 10.0,     # Max time for image fingerprinting
            'text_processing_time_seconds': 5.0,       # Max time for text analysis
            'ai_confidence_minimum': 0.85,             # Minimum AI confidence score
            'fingerprinting_accuracy_minimum': 0.95,   # Minimum fingerprinting accuracy
            'pipeline_success_rate_minimum': 0.98,     # Minimum success rate
            'creator_satisfaction_minimum': 4.0        # Minimum creator satisfaction (1-5 scale)
        }
        
        # Content type specific configurations
        self.content_configs = {
            ContentType.AUDIO: {
                'max_file_size_mb': 500,
                'supported_formats': ['mp3', 'wav', 'flac', 'aac', 'm4a'],
                'ai_models': ['audio_fingerprint', 'music_genre', 'audio_quality'],
                'processing_stages': [
                    PipelineStage.UPLOAD, PipelineStage.VALIDATION, 
                    PipelineStage.FINGERPRINTING, PipelineStage.AI_ANALYSIS,
                    PipelineStage.PROTECTION, PipelineStage.SEO_OPTIMIZATION,
                    PipelineStage.MONETIZATION, PipelineStage.DISTRIBUTION
                ]
            },
            ContentType.VIDEO: {
                'max_file_size_mb': 2000,
                'supported_formats': ['mp4', 'avi', 'mov', 'wmv', 'flv'],
                'ai_models': ['video_fingerprint', 'scene_detection', 'content_moderation'],
                'processing_stages': [
                    PipelineStage.UPLOAD, PipelineStage.VALIDATION,
                    PipelineStage.FINGERPRINTING, PipelineStage.AI_ANALYSIS,
                    PipelineStage.PROTECTION, PipelineStage.SEO_OPTIMIZATION,
                    PipelineStage.COLLABORATION, PipelineStage.MONETIZATION,
                    PipelineStage.DISTRIBUTION
                ]
            },
            ContentType.IMAGE: {
                'max_file_size_mb': 100,
                'supported_formats': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'],
                'ai_models': ['image_fingerprint', 'object_detection', 'style_analysis'],
                'processing_stages': [
                    PipelineStage.UPLOAD, PipelineStage.VALIDATION,
                    PipelineStage.FINGERPRINTING, PipelineStage.AI_ANALYSIS,
                    PipelineStage.PROTECTION, PipelineStage.SEO_OPTIMIZATION,
                    PipelineStage.MONETIZATION, PipelineStage.DISTRIBUTION
                ]
            },
            ContentType.TEXT: {
                'max_file_size_mb': 10,
                'supported_formats': ['txt', 'md', 'html', 'json'],
                'ai_models': ['text_fingerprint', 'sentiment_analysis', 'topic_modeling'],
                'processing_stages': [
                    PipelineStage.UPLOAD, PipelineStage.VALIDATION,
                    PipelineStage.FINGERPRINTING, PipelineStage.AI_ANALYSIS,
                    PipelineStage.PROTECTION, PipelineStage.SEO_OPTIMIZATION,
                    PipelineStage.COLLABORATION, PipelineStage.MONETIZATION,
                    PipelineStage.DISTRIBUTION
                ]
            }
        }
        
        self.logger.info("Content Pipeline Monitor initialized for IA Influencer Agent")
    
    async def start_pipeline_monitoring(self, content_id: str, content_type: ContentType, 
                                      creator_id: str, metadata: Dict[str, Any] = None) -> None:
        """Start monitoring a new content processing pipeline"""        try:
            pipeline_metrics = ContentProcessingMetrics(
                content_id=content_id,
                content_type=content_type,
                creator_id=creator_id,
                pipeline_stage=PipelineStage.UPLOAD,
                status=PipelineStatus.PENDING,
                start_time=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            self.active_pipelines[content_id] = pipeline_metrics
            
            # Cache pipeline start
            await self.cache.set(
                f"pipeline:{content_id}:status",
                json.dumps(pipeline_metrics.to_dict()),
                expire=3600
            )
            
            self.logger.info(f"Started pipeline monitoring for content {content_id} (type: {content_type.value})")
            
        except Exception as e:
            self.logger.error(f"Error starting pipeline monitoring: {e}")
            raise
    
    async def update_pipeline_stage(self, content_id: str, stage: PipelineStage, 
                                  status: PipelineStatus, quality_score: float = 0.0,
                                  ai_confidence: float = 0.0, error_message: str = None) -> None:
        """Update pipeline stage and status"""        try:
            if content_id not in self.active_pipelines:
                self.logger.warning(f"Pipeline {content_id} not found in active pipelines")
                return
            
            pipeline = self.active_pipelines[content_id]
            pipeline.pipeline_stage = stage
            pipeline.status = status
            pipeline.quality_score = quality_score
            pipeline.ai_confidence = ai_confidence
            pipeline.error_message = error_message
            
            # Calculate processing duration if completed or failed
            if status in [PipelineStatus.COMPLETED, PipelineStatus.FAILED]:
                pipeline.end_time = datetime.utcnow()
                pipeline.processing_duration = (
                    pipeline.end_time - pipeline.start_time
                ).total_seconds()
            
            # Update cache
            await self.cache.set(
                f"pipeline:{content_id}:status",
                json.dumps(pipeline.to_dict()),
                expire=3600
            )
            
            # Check for performance issues
            await self._check_pipeline_performance(pipeline)
            
            self.logger.info(
                f"Updated pipeline {content_id} to stage {stage.value} with status {status.value}"
            )
            
        except Exception as e:
            self.logger.error(f"Error updating pipeline stage: {e}")
            raise
    
    async def complete_pipeline(self, content_id: str, final_quality_score: float = 0.0,
                              monetization_data: Dict[str, Any] = None) -> None:
        """Complete pipeline monitoring and archive metrics"""        try:
            if content_id not in self.active_pipelines:
                self.logger.warning(f"Pipeline {content_id} not found in active pipelines")
                return
            
            pipeline = self.active_pipelines[content_id]
            pipeline.status = PipelineStatus.COMPLETED
            pipeline.end_time = datetime.utcnow()
            pipeline.processing_duration = (
                pipeline.end_time - pipeline.start_time
            ).total_seconds()
            pipeline.quality_score = final_quality_score
            
            if monetization_data:
                pipeline.metadata.update(monetization_data)
            
            # Archive completed pipeline
            self.pipeline_history.append(pipeline)
            
            # Remove from active pipelines
            del self.active_pipelines[content_id]
            
            # Store in database for historical analysis
            await self._store_pipeline_metrics(pipeline)
            
            # Run AI analysis on completed pipeline
            await self._analyze_pipeline_performance(pipeline)
            
            self.logger.info(f"Completed pipeline monitoring for content {content_id}")
            
        except Exception as e:
            self.logger.error(f"Error completing pipeline: {e}")
            raise
    
    async def _check_pipeline_performance(self, pipeline: ContentProcessingMetrics) -> None:
        """Check pipeline performance against thresholds"""        try:
            content_config = self.content_configs.get(pipeline.content_type, {})
            
            # Check processing time thresholds
            if pipeline.processing_duration:
                threshold_key = f"{pipeline.content_type.value}_processing_time_seconds"
                max_time = self.thresholds.get(threshold_key, 60.0)
                
                if pipeline.processing_duration > max_time:
                    await self._send_performance_alert(
                        pipeline,
                        f"Slow processing: {pipeline.processing_duration:.1f}s > {max_time}s threshold"
                    )
            
            # Check AI confidence
            if pipeline.ai_confidence > 0 and pipeline.ai_confidence < self.thresholds['ai_confidence_minimum']:
                await self._send_performance_alert(
                    pipeline,
                    f"Low AI confidence: {pipeline.ai_confidence:.2f} < {self.thresholds['ai_confidence_minimum']}"
                )
            
            # Check quality score
            if pipeline.quality_score > 0 and pipeline.quality_score < 0.7:
                await self._send_performance_alert(
                    pipeline,
                    f"Low quality score: {pipeline.quality_score:.2f}"
                )
                
        except Exception as e:
            self.logger.error(f"Error checking pipeline performance: {e}")
    
    async def _send_performance_alert(self, pipeline: ContentProcessingMetrics, message: str) -> None:
        """Send performance alert for pipeline issues"""        try:
            alert_data = {
                'alert_type': 'pipeline_performance',
                'content_id': pipeline.content_id,
                'content_type': pipeline.content_type.value,
                'creator_id': pipeline.creator_id,
                'pipeline_stage': pipeline.pipeline_stage.value,
                'message': message,
                'timestamp': datetime.utcnow().isoformat(),
                'severity': 'warning'
            }
            
            # Store alert
            await self.cache.lpush(
                "pipeline:alerts",
                json.dumps(alert_data)
            )
            
            self.logger.warning(f"Pipeline performance alert: {message}")
            
        except Exception as e:
            self.logger.error(f"Error sending performance alert: {e}")
    
    async def _store_pipeline_metrics(self, pipeline: ContentProcessingMetrics) -> None:
        """Store pipeline metrics in database for historical analysis"""        try:
            async with get_database_session() as session:
                await session.execute(text("""                    INSERT INTO content_pipeline_metrics 
                    (content_id, content_type, creator_id, pipeline_stage, status,
                     start_time, end_time, processing_duration, file_size_mb,
                     quality_score, ai_confidence, error_message, metadata)
                    VALUES (:content_id, :content_type, :creator_id, :pipeline_stage, :status,
                            :start_time, :end_time, :processing_duration, :file_size_mb,
                            :quality_score, :ai_confidence, :error_message, :metadata)
                """), {
                    'content_id': pipeline.content_id,
                    'content_type': pipeline.content_type.value,
                    'creator_id': pipeline.creator_id,
                    'pipeline_stage': pipeline.pipeline_stage.value,
                    'status': pipeline.status.value,
                    'start_time': pipeline.start_time,
                    'end_time': pipeline.end_time,
                    'processing_duration': pipeline.processing_duration,
                    'file_size_mb': pipeline.file_size_mb,
                    'quality_score': pipeline.quality_score,
                    'ai_confidence': pipeline.ai_confidence,
                    'error_message': pipeline.error_message,
                    'metadata': json.dumps(pipeline.metadata)
                })
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing pipeline metrics: {e}")
    
    async def _analyze_pipeline_performance(self, pipeline: ContentProcessingMetrics) -> None:
        """Run AI analysis on pipeline performance"""        try:
            # Analyze pipeline efficiency
            efficiency_score = await self.ai_analyzer.analyze_pipeline_efficiency(pipeline.to_dict())
            
            # Generate optimization recommendations
            recommendations = await self.ai_analyzer.generate_optimization_recommendations(
                pipeline.content_type, pipeline.processing_duration, pipeline.quality_score
            )
            
            # Store AI insights
            insights_data = {
                'content_id': pipeline.content_id,
                'efficiency_score': efficiency_score,
                'recommendations': recommendations,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            await self.cache.set(
                f"pipeline:{pipeline.content_id}:ai_insights",
                json.dumps(insights_data),
                expire=7200  # 2 hours
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing pipeline performance: {e}")
    
    async def get_pipeline_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive pipeline analytics"""        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get recent pipelines
            recent_pipelines = [
                p for p in self.pipeline_history 
                if p.start_time >= cutoff_time
            ]
            
            if not recent_pipelines:
                return {"error": "No pipeline data available"}
            
            # Calculate analytics by content type
            analytics_by_type = {}
            for content_type in ContentType:
                type_pipelines = [p for p in recent_pipelines if p.content_type == content_type]
                if type_pipelines:
                    analytics_by_type[content_type.value] = self._calculate_type_analytics(type_pipelines)
            
            # Overall analytics
            processing_times = [p.processing_duration for p in recent_pipelines if p.processing_duration]
            quality_scores = [p.quality_score for p in recent_pipelines if p.quality_score > 0]
            ai_confidences = [p.ai_confidence for p in recent_pipelines if p.ai_confidence > 0]
            
            success_count = sum(1 for p in recent_pipelines if p.status == PipelineStatus.COMPLETED)
            total_count = len(recent_pipelines)
            
            overall_analytics = {
                'total_pipelines': total_count,
                'success_rate': (success_count / total_count * 100) if total_count > 0 else 0,
                'average_processing_time': statistics.mean(processing_times) if processing_times else 0,
                'average_quality_score': statistics.mean(quality_scores) if quality_scores else 0,
                'average_ai_confidence': statistics.mean(ai_confidences) if ai_confidences else 0,
                'analytics_by_content_type': analytics_by_type,
                'active_pipelines_count': len(self.active_pipelines),
                'analysis_period_hours': hours
            }
            
            return overall_analytics
            
        except Exception as e:
            self.logger.error(f"Error getting pipeline analytics: {e}")
            return {"error": str(e)}
    
    def _calculate_type_analytics(self, pipelines: List[ContentProcessingMetrics]) -> Dict[str, Any]:
        """Calculate analytics for specific content type"""        processing_times = [p.processing_duration for p in pipelines if p.processing_duration]
        quality_scores = [p.quality_score for p in pipelines if p.quality_score > 0]
        ai_confidences = [p.ai_confidence for p in pipelines if p.ai_confidence > 0]
        
        success_count = sum(1 for p in pipelines if p.status == PipelineStatus.COMPLETED)
        total_count = len(pipelines)
        
        return {
            'pipeline_count': total_count,
            'success_rate': (success_count / total_count * 100) if total_count > 0 else 0,
            'average_processing_time': statistics.mean(processing_times) if processing_times else 0,
            'max_processing_time': max(processing_times) if processing_times else 0,
            'min_processing_time': min(processing_times) if processing_times else 0,
            'average_quality_score': statistics.mean(quality_scores) if quality_scores else 0,
            'average_ai_confidence': statistics.mean(ai_confidences) if ai_confidences else 0
        }
    
    async def get_creator_analytics(self, creator_id: str, days: int = 7) -> Dict[str, Any]:
        """Get analytics for specific creator"""        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Get creator's pipelines
            creator_pipelines = [
                p for p in self.pipeline_history 
                if p.creator_id == creator_id and p.start_time >= cutoff_time
            ]
            
            if not creator_pipelines:
                return {"message": "No pipeline data for creator"}
            
            # Calculate creator-specific metrics
            content_type_distribution = {}
            for pipeline in creator_pipelines:
                content_type = pipeline.content_type.value
                content_type_distribution[content_type] = content_type_distribution.get(content_type, 0) + 1
            
            success_count = sum(1 for p in creator_pipelines if p.status == PipelineStatus.COMPLETED)
            total_count = len(creator_pipelines)
            
            processing_times = [p.processing_duration for p in creator_pipelines if p.processing_duration]
            quality_scores = [p.quality_score for p in creator_pipelines if p.quality_score > 0]
            
            creator_analytics = {
                'creator_id': creator_id,
                'analysis_period_days': days,
                'total_content_processed': total_count,
                'success_rate': (success_count / total_count * 100) if total_count > 0 else 0,
                'content_type_distribution': content_type_distribution,
                'average_processing_time': statistics.mean(processing_times) if processing_times else 0,
                'average_quality_score': statistics.mean(quality_scores) if quality_scores else 0,
                'most_used_content_type': max(content_type_distribution.items(), key=lambda x: x[1])[0] if content_type_distribution else None
            }
            
            return creator_analytics
            
        except Exception as e:
            self.logger.error(f"Error getting creator analytics: {e}")
            return {"error": str(e)}
    
    async def get_real_time_pipeline_status(self) -> Dict[str, Any]:
        """Get real-time status of all active pipelines"""        try:
            active_status = {}
            for content_id, pipeline in self.active_pipelines.items():
                active_status[content_id] = {
                    'content_type': pipeline.content_type.value,
                    'creator_id': pipeline.creator_id,
                    'current_stage': pipeline.pipeline_stage.value,
                    'status': pipeline.status.value,
                    'elapsed_time': (datetime.utcnow() - pipeline.start_time).total_seconds(),
                    'quality_score': pipeline.quality_score,
                    'ai_confidence': pipeline.ai_confidence
                }
            
            # Calculate summary statistics
            total_active = len(self.active_pipelines)
            processing_count = sum(1 for p in self.active_pipelines.values() 
                                 if p.status == PipelineStatus.PROCESSING)
            pending_count = sum(1 for p in self.active_pipelines.values() 
                              if p.status == PipelineStatus.PENDING)
            failed_count = sum(1 for p in self.active_pipelines.values() 
                             if p.status == PipelineStatus.FAILED)
            
            summary = {
                'total_active_pipelines': total_active,
                'processing_count': processing_count,
                'pending_count': pending_count,
                'failed_count': failed_count,
                'active_pipelines': active_status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting real-time pipeline status: {e}")
            return {"error": str(e)}


async def create_content_pipeline_monitor(settings: Settings) -> ContentPipelineMonitor:
    """Factory function to create content pipeline monitor"""    return ContentPipelineMonitor(settings)
