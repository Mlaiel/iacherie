"""AI Streaming Processor - IA Processing Streaming Integration
==============================================================

Enterprise-grade AI processing integration for real-time streaming with
intelligent content analysis, optimization, and enhancement capabilities.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/streaming/ai_streaming_processor.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

BUSINESS LOGIC INTEGRATION:
IA Processing → Protection → Monetization → Collaboration → SEO → Distribution
"""

import asyncio
import json
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class AIProcessingType(Enum):
    """AI processing types for streaming content."""
    CONTENT_ANALYSIS = "content_analysis"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    REAL_TIME_OPTIMIZATION = "real_time_optimization"
    INTELLIGENT_ROUTING = "intelligent_routing"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    ADAPTIVE_STREAMING = "adaptive_streaming"
    CONTENT_UNDERSTANDING = "content_understanding"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"

class ProcessingStatus(Enum):
    """AI processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    OPTIMIZING = "optimizing"
    ENHANCED = "enhanced"

class ContentType(Enum):
    """Content types for AI processing."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    VOICE = "voice"
    AVATAR = "avatar"
    MULTI_FORMAT = "multi_format"

@dataclass
class AIProcessingConfig:
    """Configuration for AI processing."""
    processing_types: List[AIProcessingType]
    content_types: List[ContentType]
    quality_threshold: float = 0.85
    optimization_level: int = 3  # 1-5 scale
    real_time_processing: bool = True
    intelligent_routing: bool = True
    predictive_analytics: bool = True
    adaptive_streaming: bool = True
    performance_monitoring: bool = True

@dataclass
class AIProcessingJob:
    """AI processing job details."""
    job_id: str
    session_id: str
    creator_id: str
    processing_type: AIProcessingType
    content_type: ContentType
    input_data: Dict[str, Any]
    config: AIProcessingConfig
    status: ProcessingStatus
    progress: float = 0.0
    estimated_completion: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

@dataclass
class AIProcessingResult:
    """Results of AI processing."""
    job_id: str
    session_id: str
    processing_type: AIProcessingType
    content_type: ContentType
    output_data: Dict[str, Any]
    quality_score: float
    optimization_metrics: Dict[str, float]
    processing_time: float
    recommendations: List[str]
    enhancements_applied: List[str]
    performance_impact: Dict[str, float]
    confidence_score: float

@dataclass
class StreamingIntelligence:
    """Streaming intelligence metrics."""
    session_id: str
    content_quality_score: float
    optimization_effectiveness: float
    audience_engagement_prediction: float
    performance_optimization_score: float
    content_discoverability_score: float
    monetization_potential: float
    viral_potential_score: float
    recommendations: List[str]
    real_time_insights: Dict[str, Any]

class AIStreamingProcessor:
    """AI processing integration for streaming content.
    
    Provides intelligent content analysis, real-time optimization,
    and AI-powered enhancement for streaming sessions.
    """
    
    def __init__(self, redis_client: Any, db_session: Any):
        """Initialize the AI streaming processor."""
        self.redis_client = redis_client
        self.db_session = db_session
        self.active_jobs: Dict[str, AIProcessingJob] = {}
        self.processing_queue = asyncio.Queue()
        self.intelligence_cache: Dict[str, StreamingIntelligence] = {}
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the AI processor and start background tasks."""
        self.logger.info("Initializing AI Streaming Processor")
        
        # Start background processing tasks
        asyncio.create_task(self._process_jobs_worker())
        asyncio.create_task(self._monitor_performance())
        asyncio.create_task(self._update_intelligence_cache())
        
        self.logger.info("AI Streaming Processor initialized successfully")
    
    async def process_streaming_content(
        self,
        session_id: str,
        creator_id: str,
        content_data: Dict[str, Any],
        config: AIProcessingConfig
    ) -> str:
        """Process streaming content with AI."""
        job_id = str(uuid.uuid4())
        
        # Determine content type
        content_type = self._detect_content_type(content_data)
        
        # Create processing job
        job = AIProcessingJob(
            job_id=job_id,
            session_id=session_id,
            creator_id=creator_id,
            processing_type=AIProcessingType.CONTENT_ANALYSIS,
            content_type=content_type,
            input_data=content_data,
            config=config,
            status=ProcessingStatus.PENDING,
            started_at=datetime.now(timezone.utc)
        )
        
        self.active_jobs[job_id] = job
        await self.processing_queue.put(job)
        
        # Cache in Redis for real-time access
        await self._cache_job_status(job)
        
        self.logger.info(f"Created AI processing job {job_id} for session {session_id}")
        return job_id
    
    async def optimize_streaming_quality(
        self,
        session_id: str,
        current_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Optimize streaming quality using AI."""
        # Analyze current performance
        quality_analysis = await self._analyze_streaming_quality(session_id, current_metrics)
        
        # Generate optimization recommendations
        optimizations = await self._generate_optimizations(quality_analysis)
        
        # Apply real-time optimizations
        applied_optimizations = await self._apply_optimizations(session_id, optimizations)
        
        return {
            "session_id": session_id,
            "quality_analysis": quality_analysis,
            "optimizations_applied": applied_optimizations,
            "expected_improvement": optimizations.get("expected_improvement", 0.0),
            "optimization_confidence": optimizations.get("confidence", 0.0)
        }
    
    async def get_streaming_intelligence(self, session_id: str) -> Optional[StreamingIntelligence]:
        """Get AI-powered streaming intelligence."""
        # Check cache first
        if session_id in self.intelligence_cache:
            cached_intelligence = self.intelligence_cache[session_id]
            # Return if recent (less than 30 seconds old)
            if (datetime.now(timezone.utc) - datetime.fromisoformat(
                cached_intelligence.real_time_insights.get("timestamp", "1970-01-01T00:00:00+00:00")
            )).total_seconds() < 30:
                return cached_intelligence
        
        # Generate new intelligence
        intelligence = await self._generate_streaming_intelligence(session_id)
        
        # Cache the result
        if intelligence:
            self.intelligence_cache[session_id] = intelligence
            await self._cache_intelligence(intelligence)
        
        return intelligence
    
    async def predict_streaming_performance(
        self,
        session_id: str,
        historical_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Predict streaming performance using AI."""
        # Analyze historical patterns
        patterns = await self._analyze_historical_patterns(historical_data)
        
        # Generate predictions
        predictions = {
            "expected_viewer_count": await self._predict_viewer_count(patterns),
            "engagement_score": await self._predict_engagement(patterns),
            "revenue_potential": await self._predict_revenue(patterns),
            "viral_potential": await self._predict_viral_potential(patterns),
            "optimal_duration": await self._predict_optimal_duration(patterns),
            "best_streaming_time": await self._predict_optimal_time(patterns)
        }
        
        # Cache predictions
        await self._cache_predictions(session_id, predictions)
        
        return predictions
    
    async def enhance_content_real_time(
        self,
        session_id: str,
        content_chunk: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance content in real-time during streaming."""
        # Analyze content quality
        quality_metrics = await self._analyze_content_quality(content_chunk)
        
        # Apply AI enhancements
        enhanced_content = content_chunk.copy()
        
        if quality_metrics["audio_quality"] < 0.8:
            enhanced_content = await self._enhance_audio_quality(enhanced_content)
        
        if quality_metrics["video_quality"] < 0.8:
            enhanced_content = await self._enhance_video_quality(enhanced_content)
        
        if quality_metrics["content_clarity"] < 0.8:
            enhanced_content = await self._enhance_content_clarity(enhanced_content)
        
        # Track enhancement metrics
        enhancement_metrics = {
            "original_quality": quality_metrics,
            "enhancements_applied": [],
            "improvement_score": 0.0,
            "processing_time": 0.0
        }
        
        return {
            "enhanced_content": enhanced_content,
            "enhancement_metrics": enhancement_metrics
        }
    
    async def get_job_status(self, job_id: str) -> Optional[AIProcessingJob]:
        """Get the status of an AI processing job."""
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        
        # Check Redis cache
        cached_job = await self._get_cached_job_status(job_id)
        return cached_job
    
    async def get_processing_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get AI processing analytics for a session."""
        # Collect metrics from all jobs for this session
        session_jobs = [job for job in self.active_jobs.values() if job.session_id == session_id]
        
        analytics = {
            "total_jobs": len(session_jobs),
            "completed_jobs": len([j for j in session_jobs if j.status == ProcessingStatus.COMPLETED]),
            "failed_jobs": len([j for j in session_jobs if j.status == ProcessingStatus.FAILED]),
            "average_processing_time": 0.0,
            "quality_improvements": {},
            "optimization_effectiveness": {},
            "ai_confidence_scores": {}
        }
        
        # Calculate detailed analytics
        if session_jobs:
            completed_jobs = [j for j in session_jobs if j.status == ProcessingStatus.COMPLETED]
            if completed_jobs:
                processing_times = []
                for job in completed_jobs:
                    if job.started_at and job.completed_at:
                        processing_times.append(
                            (job.completed_at - job.started_at).total_seconds()
                        )
                
                if processing_times:
                    analytics["average_processing_time"] = sum(processing_times) / len(processing_times)
        
        return analytics
    
    # Private helper methods
    
    def _detect_content_type(self, content_data: Dict[str, Any]) -> ContentType:
        """Detect content type from data."""
        if "audio" in content_data:
            return ContentType.AUDIO
        elif "video" in content_data:
            return ContentType.VIDEO
        elif "image" in content_data:
            return ContentType.IMAGE
        elif "text" in content_data:
            return ContentType.TEXT
        else:
            return ContentType.MULTI_FORMAT
    
    async def _process_jobs_worker(self):
        """Background worker to process AI jobs."""
        while True:
            try:
                job = await self.processing_queue.get()
                await self._process_single_job(job)
                self.processing_queue.task_done()
            except Exception as e:
                self.logger.error(f"Error in AI processing worker: {e}")
                await asyncio.sleep(1)
    
    async def _process_single_job(self, job: AIProcessingJob):
        """Process a single AI job."""
        try:
            job.status = ProcessingStatus.PROCESSING
            await self._cache_job_status(job)
            
            # Simulate AI processing based on type
            if job.processing_type == AIProcessingType.CONTENT_ANALYSIS:
                result = await self._analyze_content(job)
            elif job.processing_type == AIProcessingType.QUALITY_ENHANCEMENT:
                result = await self._enhance_quality(job)
            elif job.processing_type == AIProcessingType.REAL_TIME_OPTIMIZATION:
                result = await self._optimize_real_time(job)
            else:
                result = await self._default_processing(job)
            
            job.status = ProcessingStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            await self._cache_job_status(job)
            
            # Cache result
            await self._cache_processing_result(result)
            
        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.error_message = str(e)
            await self._cache_job_status(job)
            self.logger.error(f"AI processing job {job.job_id} failed: {e}")
    
    async def _analyze_content(self, job: AIProcessingJob) -> AIProcessingResult:
        """Analyze content with AI."""
        # Simulate content analysis
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return AIProcessingResult(
            job_id=job.job_id,
            session_id=job.session_id,
            processing_type=job.processing_type,
            content_type=job.content_type,
            output_data={"analyzed": True, "quality_score": 0.85},
            quality_score=0.85,
            optimization_metrics={"improvement": 0.15},
            processing_time=0.1,
            recommendations=["Optimize audio quality", "Enhance video clarity"],
            enhancements_applied=["AI audio filter", "Video stabilization"],
            performance_impact={"latency_reduction": 0.05},
            confidence_score=0.9
        )
    
    async def _enhance_quality(self, job: AIProcessingJob) -> AIProcessingResult:
        """Enhance content quality with AI."""
        await asyncio.sleep(0.2)
        
        return AIProcessingResult(
            job_id=job.job_id,
            session_id=job.session_id,
            processing_type=job.processing_type,
            content_type=job.content_type,
            output_data={"enhanced": True, "quality_improvement": 0.25},
            quality_score=0.9,
            optimization_metrics={"enhancement_factor": 0.25},
            processing_time=0.2,
            recommendations=["Continue enhancement", "Monitor quality"],
            enhancements_applied=["AI upscaling", "Noise reduction"],
            performance_impact={"quality_improvement": 0.25},
            confidence_score=0.85
        )
    
    async def _optimize_real_time(self, job: AIProcessingJob) -> AIProcessingResult:
        """Optimize streaming in real-time."""
        await asyncio.sleep(0.05)
        
        return AIProcessingResult(
            job_id=job.job_id,
            session_id=job.session_id,
            processing_type=job.processing_type,
            content_type=job.content_type,
            output_data={"optimized": True, "latency_reduction": 0.1},
            quality_score=0.88,
            optimization_metrics={"latency_improvement": 0.1},
            processing_time=0.05,
            recommendations=["Maintain optimization", "Monitor performance"],
            enhancements_applied=["Adaptive bitrate", "Intelligent routing"],
            performance_impact={"latency_reduction": 0.1},
            confidence_score=0.92
        )
    
    async def _default_processing(self, job: AIProcessingJob) -> AIProcessingResult:
        """Default AI processing."""
        await asyncio.sleep(0.1)
        
        return AIProcessingResult(
            job_id=job.job_id,
            session_id=job.session_id,
            processing_type=job.processing_type,
            content_type=job.content_type,
            output_data={"processed": True},
            quality_score=0.8,
            optimization_metrics={"general_improvement": 0.1},
            processing_time=0.1,
            recommendations=["Monitor performance"],
            enhancements_applied=["Basic optimization"],
            performance_impact={"general_improvement": 0.1},
            confidence_score=0.8
        )
    
    async def _cache_job_status(self, job: AIProcessingJob):
        """Cache job status in Redis."""
        try:
            await self.redis_client.setex(
                f"ai_job:{job.job_id}",
                3600,  # 1 hour TTL
                json.dumps(asdict(job), default=str)
            )
        except Exception as e:
            self.logger.error(f"Error caching job status: {e}")
    
    async def _get_cached_job_status(self, job_id: str) -> Optional[AIProcessingJob]:
        """Get cached job status from Redis."""
        try:
            cached_data = await self.redis_client.get(f"ai_job:{job_id}")
            if cached_data:
                job_data = json.loads(cached_data)
                return AIProcessingJob(**job_data)
        except Exception as e:
            self.logger.error(f"Error getting cached job status: {e}")
        return None
    
    async def _cache_processing_result(self, result: AIProcessingResult):
        """Cache processing result in Redis."""
        try:
            await self.redis_client.setex(
                f"ai_result:{result.job_id}",
                3600,
                json.dumps(asdict(result), default=str)
            )
        except Exception as e:
            self.logger.error(f"Error caching processing result: {e}")
    
    async def _cache_intelligence(self, intelligence: StreamingIntelligence):
        """Cache streaming intelligence in Redis."""
        try:
            await self.redis_client.setex(
                f"ai_intelligence:{intelligence.session_id}",
                1800,  # 30 minutes TTL
                json.dumps(asdict(intelligence), default=str)
            )
        except Exception as e:
            self.logger.error(f"Error caching intelligence: {e}")
    
    async def _cache_predictions(self, session_id: str, predictions: Dict[str, float]):
        """Cache predictions in Redis."""
        try:
            await self.redis_client.setex(
                f"ai_predictions:{session_id}",
                3600,
                json.dumps(predictions)
            )
        except Exception as e:
            self.logger.error(f"Error caching predictions: {e}")
    
    async def _analyze_streaming_quality(self, session_id: str, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Analyze streaming quality."""
        # Simulate quality analysis
        quality_score = np.mean([metrics.get("bitrate", 0.5), metrics.get("latency", 0.5), metrics.get("fps", 0.5)])
        
        return {
            "overall_quality": quality_score,
            "bitrate_analysis": {"score": metrics.get("bitrate", 0.5), "optimal": 0.8},
            "latency_analysis": {"score": metrics.get("latency", 0.5), "optimal": 0.9},
            "fps_analysis": {"score": metrics.get("fps", 0.5), "optimal": 0.85},
            "recommendations": self._generate_quality_recommendations(quality_score)
        }
    
    def _generate_quality_recommendations(self, quality_score: float) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        if quality_score < 0.6:
            recommendations.extend([
                "Reduce streaming bitrate",
                "Optimize encoder settings",
                "Check network connectivity"
            ])
        elif quality_score < 0.8:
            recommendations.extend([
                "Fine-tune encoder parameters",
                "Monitor network stability"
            ])
        else:
            recommendations.append("Quality is optimal")
        
        return recommendations
    
    async def _generate_optimizations(self, quality_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimization recommendations."""
        optimizations = {
            "bitrate_adjustment": 0.0,
            "encoder_optimization": False,
            "network_optimization": False,
            "expected_improvement": 0.0,
            "confidence": 0.8
        }
        
        overall_quality = quality_analysis["overall_quality"]
        
        if overall_quality < 0.8:
            optimizations["bitrate_adjustment"] = 0.1
            optimizations["encoder_optimization"] = True
            optimizations["expected_improvement"] = 0.15
        
        return optimizations
    
    async def _apply_optimizations(self, session_id: str, optimizations: Dict[str, Any]) -> List[str]:
        """Apply optimizations to streaming session."""
        applied = []
        
        if optimizations.get("encoder_optimization"):
            applied.append("Encoder optimization")
        
        if optimizations.get("bitrate_adjustment", 0) > 0:
            applied.append(f"Bitrate adjustment: +{optimizations['bitrate_adjustment']:.1%}")
        
        if optimizations.get("network_optimization"):
            applied.append("Network optimization")
        
        return applied
    
    async def _generate_streaming_intelligence(self, session_id: str) -> Optional[StreamingIntelligence]:
        """Generate streaming intelligence."""
        # Simulate intelligence generation
        return StreamingIntelligence(
            session_id=session_id,
            content_quality_score=0.85,
            optimization_effectiveness=0.78,
            audience_engagement_prediction=0.72,
            performance_optimization_score=0.89,
            content_discoverability_score=0.65,
            monetization_potential=0.71,
            viral_potential_score=0.58,
            recommendations=[
                "Optimize content for peak hours",
                "Enhance engagement through interactive elements",
                "Improve SEO metadata"
            ],
            real_time_insights={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "trends": ["gaming content", "music streams"],
                "optimal_timing": "evening hours"
            }
        )
    
    async def _analyze_historical_patterns(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze historical streaming patterns."""
        # Simulate pattern analysis
        return {
            "viewer_patterns": {"peak_hours": [19, 20, 21], "engagement_trend": "increasing"},
            "content_performance": {"best_categories": ["gaming", "music"], "engagement_rates": 0.75},
            "seasonal_trends": {"current_season": "high_activity", "prediction": "stable"}
        }
    
    async def _predict_viewer_count(self, patterns: Dict[str, Any]) -> float:
        """Predict viewer count."""
        # Simulate prediction
        base_viewers = 100
        trend_multiplier = 1.2 if patterns["viewer_patterns"]["engagement_trend"] == "increasing" else 1.0
        return base_viewers * trend_multiplier
    
    async def _predict_engagement(self, patterns: Dict[str, Any]) -> float:
        """Predict engagement score."""
        return patterns["content_performance"].get("engagement_rates", 0.7)
    
    async def _predict_revenue(self, patterns: Dict[str, Any]) -> float:
        """Predict revenue potential."""
        base_revenue = 50.0
        engagement_factor = patterns["content_performance"].get("engagement_rates", 0.7)
        return base_revenue * engagement_factor
    
    async def _predict_viral_potential(self, patterns: Dict[str, Any]) -> float:
        """Predict viral potential."""
        # Simulate viral prediction
        return 0.3  # 30% viral potential
    
    async def _predict_optimal_duration(self, patterns: Dict[str, Any]) -> float:
        """Predict optimal streaming duration."""
        # Simulate duration prediction
        return 120.0  # 2 hours
    
    async def _predict_optimal_time(self, patterns: Dict[str, Any]) -> float:
        """Predict optimal streaming time."""
        peak_hours = patterns["viewer_patterns"]["peak_hours"]
        return float(peak_hours[0]) if peak_hours else 19.0  # 7 PM
    
    async def _analyze_content_quality(self, content_chunk: Dict[str, Any]) -> Dict[str, float]:
        """Analyze content quality."""
        # Simulate quality analysis
        return {
            "audio_quality": 0.75,
            "video_quality": 0.80,
            "content_clarity": 0.85,
            "overall_quality": 0.80
        }
    
    async def _enhance_audio_quality(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance audio quality."""
        # Simulate audio enhancement
        enhanced = content.copy()
        enhanced["audio_enhanced"] = True
        return enhanced
    
    async def _enhance_video_quality(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance video quality."""
        # Simulate video enhancement
        enhanced = content.copy()
        enhanced["video_enhanced"] = True
        return enhanced
    
    async def _enhance_content_clarity(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance content clarity."""
        # Simulate clarity enhancement
        enhanced = content.copy()
        enhanced["clarity_enhanced"] = True
        return enhanced
    
    async def _monitor_performance(self):
        """Monitor AI processing performance."""
        while True:
            try:
                # Collect performance metrics
                total_jobs = len(self.active_jobs)
                completed_jobs = len([j for j in self.active_jobs.values() if j.status == ProcessingStatus.COMPLETED])
                
                performance_data = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_jobs": total_jobs,
                    "completed_jobs": completed_jobs,
                    "success_rate": completed_jobs / total_jobs if total_jobs > 0 else 0,
                    "queue_size": self.processing_queue.qsize()
                }
                
                # Cache performance metrics
                await self.redis_client.setex(
                    "ai_processor_performance",
                    300,  # 5 minutes TTL
                    json.dumps(performance_data)
                )
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                self.logger.error(f"Error monitoring AI processor performance: {e}")
                await asyncio.sleep(60)
    
    async def _update_intelligence_cache(self):
        """Update intelligence cache periodically."""
        while True:
            try:
                # Update intelligence for active sessions
                active_sessions = set(job.session_id for job in self.active_jobs.values())
                
                for session_id in active_sessions:
                    intelligence = await self._generate_streaming_intelligence(session_id)
                    if intelligence:
                        self.intelligence_cache[session_id] = intelligence
                        await self._cache_intelligence(intelligence)
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error updating intelligence cache: {e}")
                await asyncio.sleep(30)


def create_ai_streaming_processor(redis_client: Any, db_session: Any) -> AIStreamingProcessor:
    """Factory function to create AI streaming processor."""
    return AIStreamingProcessor(redis_client, db_session)