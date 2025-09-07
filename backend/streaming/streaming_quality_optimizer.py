"""Streaming Quality Optimizer - Intelligent Quality Management System
===================================================================

Enterprise-grade streaming quality optimizer providing real-time quality monitoring,
adaptive bitrate streaming, intelligent quality adjustment, and performance optimization
for multi-platform streaming with AI-powered quality enhancement.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/streaming/streaming_quality_optimizer.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

BUSINESS LOGIC INTEGRATION:
Quality Analysis → Adaptive Optimization → Performance Monitoring → AI Enhancement → Quality Assurance
"""

import asyncio
import json
import uuid
import logging
import statistics
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from decimal import Decimal
import redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()
logger = logging.getLogger(__name__)


class QualityLevel(str, Enum):
    """Streaming quality levels."""
    ULTRA_LOW = "ultra_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA_HIGH = "ultra_high"
    AUTO = "auto"


class OptimizationType(str, Enum):
    """Types of quality optimization."""
    BITRATE = "bitrate"
    RESOLUTION = "resolution"
    FRAMERATE = "framerate"
    AUDIO_QUALITY = "audio_quality"
    LATENCY = "latency"
    ADAPTIVE = "adaptive"


class MetricType(str, Enum):
    """Quality metrics types."""
    BITRATE = "bitrate"
    RESOLUTION = "resolution"
    FRAMERATE = "framerate"
    LATENCY = "latency"
    PACKET_LOSS = "packet_loss"
    JITTER = "jitter"
    BUFFERING = "buffering"
    QUALITY_SCORE = "quality_score"


class OptimizationStrategy(str, Enum):
    """Quality optimization strategies."""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    AI_DRIVEN = "ai_driven"


@dataclass
class QualitySettings:
    """Quality settings configuration."""
    video_bitrate: int  # kbps
    audio_bitrate: int  # kbps
    resolution_width: int
    resolution_height: int
    framerate: int
    keyframe_interval: int
    encoding_preset: str
    adaptive_enabled: bool = True


@dataclass
class QualityMetrics:
    """Real-time quality metrics."""
    timestamp: datetime
    bitrate_current: float
    bitrate_target: float
    resolution_current: str
    framerate_current: float
    latency_ms: float
    packet_loss_percent: float
    jitter_ms: float
    buffering_events: int
    quality_score: float
    viewer_experience_score: float


@dataclass
class OptimizationResult:
    """Result of quality optimization."""
    optimization_id: str
    session_id: str
    optimization_type: OptimizationType
    previous_settings: QualitySettings
    optimized_settings: QualitySettings
    improvement_percentage: float
    quality_score_before: float
    quality_score_after: float
    applied_at: datetime
    success: bool
    warnings: List[str] = field(default_factory=list)


@dataclass
class AdaptiveProfile:
    """Adaptive streaming profile."""
    profile_id: str
    name: str
    min_bitrate: int
    max_bitrate: int
    resolutions: List[Tuple[int, int]]
    framerates: List[int]
    conditions: Dict[str, Any]
    priority: int


class StreamingQualityRecord(Base):
    """SQLAlchemy model for streaming quality optimization records."""
    __tablename__ = "streaming_quality_optimization"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(50), nullable=False, index=True)
    creator_id = Column(String(50), nullable=False, index=True)
    optimization_id = Column(String(50), unique=True, nullable=False)
    optimization_type = Column(String(30), nullable=False)
    strategy = Column(String(20), nullable=False)
    previous_settings = Column(JSON, nullable=False)
    optimized_settings = Column(JSON, nullable=False)
    quality_metrics_before = Column(JSON)
    quality_metrics_after = Column(JSON)
    improvement_percentage = Column(Float)
    success = Column(Boolean, nullable=False)
    applied_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class StreamingQualityOptimizer:
    """Advanced streaming quality optimization engine.
    
    Provides intelligent quality management with adaptive bitrate streaming,
    real-time quality monitoring, and AI-powered optimization.
    """
    
    def __init__(self, redis_client: Any, db_session: Session):
        """Initialize the streaming quality optimizer."""
        self.redis_client = redis_client
        self.db_session = db_session
        self.active_optimizations: Dict[str, Dict[str, Any]] = {}
        self.quality_profiles: Dict[str, AdaptiveProfile] = {}
        self.optimization_strategies: Dict[OptimizationStrategy, Callable] = {}
        self.is_running = False
        
        # Quality thresholds
        self.quality_thresholds = {
            "min_quality_score": 0.7,
            "max_latency_ms": 2000,
            "max_packet_loss_percent": 1.0,
            "max_jitter_ms": 50,
            "min_bitrate_efficiency": 0.8
        }
        
        # Initialize optimization strategies
        self._initialize_strategies()
        
    async def initialize(self):
        """Initialize the optimizer and start monitoring."""
        self.is_running = True
        logger.info("Streaming Quality Optimizer initialized")
        
        # Load quality profiles
        await self._load_quality_profiles()
        
        # Start background tasks
        asyncio.create_task(self._quality_monitor())
        asyncio.create_task(self._adaptive_optimizer())
        asyncio.create_task(self._metrics_collector())
        
    def _initialize_strategies(self):
        """Initialize optimization strategies."""
        self.optimization_strategies = {
            OptimizationStrategy.CONSERVATIVE: self._conservative_optimization,
            OptimizationStrategy.BALANCED: self._balanced_optimization,
            OptimizationStrategy.AGGRESSIVE: self._aggressive_optimization,
            OptimizationStrategy.AI_DRIVEN: self._ai_driven_optimization
        }
    
    async def start_quality_optimization(
        self,
        session_id: str,
        creator_id: str,
        initial_settings: QualitySettings,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    ) -> bool:
        """Start quality optimization for a streaming session."""
        try:
            optimization_id = str(uuid.uuid4())
            
            # Store optimization context
            self.active_optimizations[session_id] = {
                "optimization_id": optimization_id,
                "creator_id": creator_id,
                "strategy": strategy,
                "current_settings": initial_settings,
                "start_time": datetime.now(timezone.utc),
                "metrics_history": [],
                "optimizations_applied": []
            }
            
            # Start quality monitoring for this session
            asyncio.create_task(self._monitor_session_quality(session_id))
            
            logger.info(f"Started quality optimization for session {session_id} with strategy {strategy.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start quality optimization for {session_id}: {e}")
            return False
    
    async def stop_quality_optimization(self, session_id: str) -> bool:
        """Stop quality optimization for a streaming session."""
        try:
            if session_id in self.active_optimizations:
                context = self.active_optimizations[session_id]
                
                # Generate final report
                await self._generate_optimization_report(session_id, context)
                
                # Remove from active optimizations
                del self.active_optimizations[session_id]
                
                logger.info(f"Stopped quality optimization for session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to stop quality optimization for {session_id}: {e}")
            return False
    
    async def optimize_quality(
        self,
        session_id: str,
        current_metrics: QualityMetrics,
        optimization_type: OptimizationType = OptimizationType.ADAPTIVE
    ) -> Optional[OptimizationResult]:
        """Perform quality optimization based on current metrics."""
        try:
            if session_id not in self.active_optimizations:
                return None
            
            context = self.active_optimizations[session_id]
            strategy = context["strategy"]
            current_settings = context["current_settings"]
            
            # Analyze current quality
            quality_analysis = await self._analyze_quality_metrics(current_metrics)
            
            # Determine if optimization is needed
            if not self._should_optimize(quality_analysis, current_metrics):
                return None
            
            # Apply optimization strategy
            optimizer = self.optimization_strategies.get(strategy)
            if not optimizer:
                return None
            
            optimized_settings = await optimizer(
                current_settings, 
                current_metrics, 
                quality_analysis,
                optimization_type
            )
            
            # Calculate improvement
            improvement = await self._calculate_improvement(
                current_settings,
                optimized_settings,
                current_metrics
            )
            
            # Create optimization result
            optimization_id = str(uuid.uuid4())
            result = OptimizationResult(
                optimization_id=optimization_id,
                session_id=session_id,
                optimization_type=optimization_type,
                previous_settings=current_settings,
                optimized_settings=optimized_settings,
                improvement_percentage=improvement,
                quality_score_before=current_metrics.quality_score,
                quality_score_after=await self._predict_quality_score(optimized_settings, current_metrics),
                applied_at=datetime.now(timezone.utc),
                success=True
            )
            
            # Update context
            context["current_settings"] = optimized_settings
            context["optimizations_applied"].append(result)
            
            # Store in database
            await self._store_optimization_record(result, context)
            
            logger.info(f"Applied quality optimization {optimization_id} for session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to optimize quality for {session_id}: {e}")
            return None
    
    async def get_quality_metrics(self, session_id: str) -> Optional[QualityMetrics]:
        """Get current quality metrics for a session."""
        try:
            metrics_data = await self.redis_client.get(f"quality_metrics_{session_id}")
            if metrics_data:
                metrics_dict = json.loads(metrics_data)
                return QualityMetrics(**metrics_dict)
            return None
        except Exception as e:
            logger.error(f"Failed to get quality metrics for {session_id}: {e}")
            return None
    
    async def get_optimization_history(self, session_id: str) -> List[OptimizationResult]:
        """Get optimization history for a session."""
        try:
            if session_id in self.active_optimizations:
                return self.active_optimizations[session_id]["optimizations_applied"]
            return []
        except Exception as e:
            logger.error(f"Failed to get optimization history for {session_id}: {e}")
            return []
    
    async def create_adaptive_profile(
        self,
        profile: AdaptiveProfile
    ) -> bool:
        """Create a new adaptive streaming profile."""
        try:
            self.quality_profiles[profile.profile_id] = profile
            
            # Store in Redis
            await self.redis_client.hset(
                "quality_profiles",
                profile.profile_id,
                json.dumps(asdict(profile))
            )
            
            logger.info(f"Created adaptive profile {profile.profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create adaptive profile: {e}")
            return False
    
    async def _analyze_quality_metrics(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """Analyze quality metrics to determine optimization needs."""
        analysis = {
            "overall_score": metrics.quality_score,
            "latency_issue": metrics.latency_ms > self.quality_thresholds["max_latency_ms"],
            "packet_loss_issue": metrics.packet_loss_percent > self.quality_thresholds["max_packet_loss_percent"],
            "jitter_issue": metrics.jitter_ms > self.quality_thresholds["max_jitter_ms"],
            "bitrate_efficiency": metrics.bitrate_current / metrics.bitrate_target if metrics.bitrate_target > 0 else 0,
            "buffering_frequency": metrics.buffering_events,
            "viewer_experience": metrics.viewer_experience_score
        }
        
        # Determine primary issues
        issues = []
        if analysis["latency_issue"]:
            issues.append("high_latency")
        if analysis["packet_loss_issue"]:
            issues.append("packet_loss")
        if analysis["jitter_issue"]:
            issues.append("network_instability")
        if analysis["bitrate_efficiency"] < self.quality_thresholds["min_bitrate_efficiency"]:
            issues.append("bitrate_inefficiency")
        if analysis["buffering_frequency"] > 5:
            issues.append("frequent_buffering")
        
        analysis["primary_issues"] = issues
        analysis["optimization_needed"] = len(issues) > 0 or analysis["overall_score"] < self.quality_thresholds["min_quality_score"]
        
        return analysis
    
    def _should_optimize(self, analysis: Dict[str, Any], metrics: QualityMetrics) -> bool:
        """Determine if optimization should be applied."""
        return analysis.get("optimization_needed", False)
    
    async def _conservative_optimization(
        self,
        current_settings: QualitySettings,
        metrics: QualityMetrics,
        analysis: Dict[str, Any],
        optimization_type: OptimizationType
    ) -> QualitySettings:
        """Apply conservative optimization strategy."""
        optimized = QualitySettings(**asdict(current_settings))
        
        # Make small adjustments
        if "high_latency" in analysis["primary_issues"]:
            optimized.video_bitrate = max(optimized.video_bitrate * 0.9, 500)
        
        if "packet_loss" in analysis["primary_issues"]:
            optimized.framerate = max(optimized.framerate * 0.9, 15)
        
        if "bitrate_inefficiency" in analysis["primary_issues"]:
            optimized.video_bitrate = min(optimized.video_bitrate * 1.1, 5000)
        
        return optimized
    
    async def _balanced_optimization(
        self,
        current_settings: QualitySettings,
        metrics: QualityMetrics,
        analysis: Dict[str, Any],
        optimization_type: OptimizationType
    ) -> QualitySettings:
        """Apply balanced optimization strategy."""
        optimized = QualitySettings(**asdict(current_settings))
        
        # Moderate adjustments based on issues
        if "high_latency" in analysis["primary_issues"]:
            optimized.video_bitrate = max(optimized.video_bitrate * 0.8, 500)
            optimized.keyframe_interval = min(optimized.keyframe_interval * 1.2, 60)
        
        if "packet_loss" in analysis["primary_issues"]:
            optimized.framerate = max(optimized.framerate * 0.8, 15)
            optimized.video_bitrate = max(optimized.video_bitrate * 0.85, 500)
        
        if "network_instability" in analysis["primary_issues"]:
            optimized.adaptive_enabled = True
            optimized.video_bitrate = max(optimized.video_bitrate * 0.85, 500)
        
        if "frequent_buffering" in analysis["primary_issues"]:
            optimized.video_bitrate = max(optimized.video_bitrate * 0.75, 500)
            if optimized.resolution_height > 720:
                optimized.resolution_height = 720
                optimized.resolution_width = 1280
        
        return optimized
    
    async def _aggressive_optimization(
        self,
        current_settings: QualitySettings,
        metrics: QualityMetrics,
        analysis: Dict[str, Any],
        optimization_type: OptimizationType
    ) -> QualitySettings:
        """Apply aggressive optimization strategy."""
        optimized = QualitySettings(**asdict(current_settings))
        
        # Significant adjustments for performance
        if analysis["overall_score"] < 0.6:
            # Dramatic quality reduction
            optimized.video_bitrate = max(optimized.video_bitrate * 0.5, 500)
            optimized.resolution_height = min(optimized.resolution_height, 720)
            optimized.resolution_width = min(optimized.resolution_width, 1280)
            optimized.framerate = min(optimized.framerate, 30)
        
        elif "high_latency" in analysis["primary_issues"]:
            optimized.video_bitrate = max(optimized.video_bitrate * 0.6, 500)
            optimized.encoding_preset = "ultrafast"
        
        return optimized
    
    async def _ai_driven_optimization(
        self,
        current_settings: QualitySettings,
        metrics: QualityMetrics,
        analysis: Dict[str, Any],
        optimization_type: OptimizationType
    ) -> QualitySettings:
        """Apply AI-driven optimization strategy."""
        # Placeholder for AI-driven optimization
        # In a real implementation, this would use ML models to predict optimal settings
        
        optimized = QualitySettings(**asdict(current_settings))
        
        # AI-based optimization logic would go here
        # For now, use a hybrid approach
        if metrics.viewer_experience_score < 0.7:
            # Focus on viewer experience
            optimized.video_bitrate = max(optimized.video_bitrate * 0.85, 500)
            optimized.adaptive_enabled = True
        
        return optimized
    
    async def _calculate_improvement(
        self,
        previous_settings: QualitySettings,
        optimized_settings: QualitySettings,
        current_metrics: QualityMetrics
    ) -> float:
        """Calculate expected improvement percentage."""
        # Simplified improvement calculation
        bitrate_improvement = (optimized_settings.video_bitrate - previous_settings.video_bitrate) / previous_settings.video_bitrate
        return abs(bitrate_improvement) * 100
    
    async def _predict_quality_score(
        self,
        settings: QualitySettings,
        current_metrics: QualityMetrics
    ) -> float:
        """Predict quality score for given settings."""
        # Placeholder for quality score prediction
        # In a real implementation, this would use ML models
        return min(current_metrics.quality_score * 1.1, 1.0)
    
    async def _monitor_session_quality(self, session_id: str):
        """Monitor quality for a specific session."""
        while session_id in self.active_optimizations:
            try:
                # Collect quality metrics
                metrics = await self._collect_quality_metrics(session_id)
                if metrics:
                    # Store metrics
                    await self._store_quality_metrics(session_id, metrics)
                    
                    # Add to history
                    context = self.active_optimizations[session_id]
                    context["metrics_history"].append(metrics)
                    
                    # Keep only last 100 metrics
                    if len(context["metrics_history"]) > 100:
                        context["metrics_history"] = context["metrics_history"][-100:]
                    
                    # Check if optimization is needed
                    analysis = await self._analyze_quality_metrics(metrics)
                    if analysis["optimization_needed"]:
                        await self.optimize_quality(session_id, metrics)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Quality monitoring error for {session_id}: {e}")
                await asyncio.sleep(10)
    
    async def _collect_quality_metrics(self, session_id: str) -> Optional[QualityMetrics]:
        """Collect real-time quality metrics for a session."""
        # Placeholder for actual metrics collection
        # In a real implementation, this would collect from streaming infrastructure
        
        return QualityMetrics(
            timestamp=datetime.now(timezone.utc),
            bitrate_current=2500.0,
            bitrate_target=3000.0,
            resolution_current="1080p",
            framerate_current=30.0,
            latency_ms=150.0,
            packet_loss_percent=0.2,
            jitter_ms=10.0,
            buffering_events=1,
            quality_score=0.85,
            viewer_experience_score=0.82
        )
    
    async def _store_quality_metrics(self, session_id: str, metrics: QualityMetrics):
        """Store quality metrics in Redis."""
        try:
            metrics_dict = asdict(metrics)
            metrics_dict["timestamp"] = metrics.timestamp.isoformat()
            
            await self.redis_client.setex(
                f"quality_metrics_{session_id}",
                300,  # 5 minutes TTL
                json.dumps(metrics_dict)
            )
        except Exception as e:
            logger.error(f"Failed to store quality metrics: {e}")
    
    async def _store_optimization_record(self, result: OptimizationResult, context: Dict[str, Any]):
        """Store optimization record in database."""
        try:
            record = StreamingQualityRecord(
                session_id=result.session_id,
                creator_id=context["creator_id"],
                optimization_id=result.optimization_id,
                optimization_type=result.optimization_type.value,
                strategy=context["strategy"].value,
                previous_settings=asdict(result.previous_settings),
                optimized_settings=asdict(result.optimized_settings),
                improvement_percentage=result.improvement_percentage,
                success=result.success
            )
            
            self.db_session.add(record)
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Failed to store optimization record: {e}")
    
    async def _load_quality_profiles(self):
        """Load quality profiles from storage."""
        try:
            profiles = await self.redis_client.hgetall("quality_profiles")
            for profile_id, profile_data in profiles.items():
                try:
                    profile_dict = json.loads(profile_data)
                    profile = AdaptiveProfile(**profile_dict)
                    self.quality_profiles[profile_id] = profile
                except Exception as e:
                    logger.error(f"Failed to load profile {profile_id}: {e}")
        except Exception as e:
            logger.error(f"Failed to load quality profiles: {e}")
    
    async def _quality_monitor(self):
        """Background quality monitoring."""
        while self.is_running:
            try:
                # Monitor all active sessions
                for session_id in list(self.active_optimizations.keys()):
                    metrics = await self.get_quality_metrics(session_id)
                    if metrics and metrics.quality_score < 0.6:
                        logger.warning(f"Low quality detected in session {session_id}: {metrics.quality_score}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Quality monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _adaptive_optimizer(self):
        """Background adaptive optimization."""
        while self.is_running:
            try:
                # Check for sessions that need adaptive optimization
                for session_id, context in self.active_optimizations.items():
                    if len(context["metrics_history"]) >= 5:
                        recent_metrics = context["metrics_history"][-5:]
                        avg_quality = statistics.mean([m.quality_score for m in recent_metrics])
                        
                        if avg_quality < 0.7:
                            latest_metrics = context["metrics_history"][-1]
                            await self.optimize_quality(session_id, latest_metrics, OptimizationType.ADAPTIVE)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Adaptive optimizer error: {e}")
                await asyncio.sleep(60)
    
    async def _metrics_collector(self):
        """Collect overall optimization metrics."""
        while self.is_running:
            try:
                metrics = {
                    "active_optimizations": len(self.active_optimizations),
                    "quality_profiles": len(self.quality_profiles),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                await self.redis_client.setex(
                    "quality_optimizer_metrics",
                    300,  # 5 minutes TTL
                    json.dumps(metrics)
                )
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                await asyncio.sleep(30)
    
    async def _generate_optimization_report(self, session_id: str, context: Dict[str, Any]):
        """Generate optimization report for a session."""
        try:
            report = {
                "session_id": session_id,
                "optimization_id": context["optimization_id"],
                "strategy": context["strategy"].value,
                "duration": (datetime.now(timezone.utc) - context["start_time"]).total_seconds(),
                "total_optimizations": len(context["optimizations_applied"]),
                "final_quality_score": context["metrics_history"][-1].quality_score if context["metrics_history"] else 0,
                "average_quality": statistics.mean([m.quality_score for m in context["metrics_history"]]) if context["metrics_history"] else 0
            }
            
            # Store report
            await self.redis_client.setex(
                f"optimization_report_{session_id}",
                86400,  # 24 hours TTL
                json.dumps(report)
            )
            
        except Exception as e:
            logger.error(f"Failed to generate optimization report: {e}")
    
    async def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get current optimization metrics."""
        try:
            metrics_data = await self.redis_client.get("quality_optimizer_metrics")
            if metrics_data:
                return json.loads(metrics_data)
            return {}
        except Exception as e:
            logger.error(f"Failed to get optimization metrics: {e}")
            return {}
    
    async def shutdown(self):
        """Gracefully shutdown the optimizer."""
        self.is_running = False
        
        # Stop optimization for all active sessions
        for session_id in list(self.active_optimizations.keys()):
            await self.stop_quality_optimization(session_id)
        
        logger.info("Streaming Quality Optimizer shutting down")


async def create_streaming_quality_optimizer(
    redis_client: Any, 
    db_session: Session
) -> StreamingQualityOptimizer:
    """Factory function to create and initialize the optimizer."""
    optimizer = StreamingQualityOptimizer(redis_client, db_session)
    await optimizer.initialize()
    return optimizer