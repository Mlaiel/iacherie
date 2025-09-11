"""
Ainflue Platform - Audio Fingerprinting Monitor
===============================================

Advanced monitoring for AI-powered audio fingerprinting including
real-time fingerprint generation, similarity matching, copyright detection,
and performance optimization for content protection workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import hashlib
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)

class FingerprintType(Enum):
    """Types of audio fingerprints supported."""
    CHROMAPRINT = "chromaprint"
    ECHOPRINT = "echoprint"
    MUSICBRAINZ = "musicbrainz"
    CUSTOM_AI = "custom_ai"
    SPECTRAL_HASH = "spectral_hash"
    NEURAL_EMBEDDING = "neural_embedding"

class FingerprintQuality(Enum):
    """Quality levels for fingerprint generation."""
    LOW = "low"          # Fast, less accurate
    MEDIUM = "medium"    # Balanced speed/accuracy
    HIGH = "high"        # Slower, high accuracy
    ULTRA = "ultra"      # Maximum accuracy

class MatchConfidence(Enum):
    """Confidence levels for fingerprint matches."""
    EXACT = "exact"          # 95%+ similarity
    HIGH = "high"            # 85-94% similarity
    MEDIUM = "medium"        # 70-84% similarity
    LOW = "low"              # 50-69% similarity
    NO_MATCH = "no_match"    # <50% similarity

@dataclass
class FingerprintMetrics:
    """Metrics for fingerprint generation and matching."""
    fingerprint_id: str
    audio_file_id: str
    fingerprint_type: FingerprintType
    quality_level: FingerprintQuality
    generation_time_ms: float
    fingerprint_size_bytes: int
    generation_success: bool
    error_message: Optional[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class MatchResult:
    """Result of a fingerprint matching operation."""
    query_fingerprint_id: str
    matched_fingerprint_id: str
    similarity_score: float
    confidence: MatchConfidence
    match_time_ms: float
    audio_offset_seconds: float
    duration_matched_seconds: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class FingerprintDatabase:
    """Represents the fingerprint database state."""
    total_fingerprints: int
    database_size_mb: float
    index_size_mb: float
    last_optimization: datetime
    search_performance_ms: float

class AudioFingerprintingMonitor:
    """
    Enterprise-grade monitoring for audio fingerprinting workflows.
    
    Monitors:
    - Fingerprint generation performance and quality
    - Database operations and optimization
    - Real-time similarity matching
    - Copyright detection accuracy
    - System resource utilization
    - Performance trends and optimization opportunities
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.fingerprint_metrics: List[FingerprintMetrics] = []
        self.match_results: List[MatchResult] = []
        self.database_state = FingerprintDatabase(
            total_fingerprints=0,
            database_size_mb=0.0,
            index_size_mb=0.0,
            last_optimization=datetime.utcnow(),
            search_performance_ms=0.0
        )
        self.active_queries: Set[str] = set()
        self._initialize_thresholds()
        
        logger.info("Audio Fingerprinting Monitor initialized")
    
    def _initialize_thresholds(self):
        """Initialize performance thresholds."""
        self.thresholds = {
            'generation_time_warning_ms': 5000,
            'generation_time_critical_ms': 15000,
            'match_time_warning_ms': 1000,
            'match_time_critical_ms': 5000,
            'success_rate_warning': 0.95,
            'success_rate_critical': 0.90,
            'database_size_warning_mb': 10000,
            'database_size_critical_mb': 50000,
            'similarity_threshold_copyright': 0.85,
            'max_concurrent_queries': 100
        }
    
    async def record_fingerprint_generation(self, audio_file_id: str, 
                                          fingerprint_type: FingerprintType,
                                          quality_level: FingerprintQuality,
                                          generation_time_ms: float,
                                          fingerprint_data: bytes,
                                          success: bool = True,
                                          error_message: Optional[str] = None) -> str:
        """Record fingerprint generation metrics."""
        fingerprint_id = str(uuid.uuid4())
        
        metrics = FingerprintMetrics(
            fingerprint_id=fingerprint_id,
            audio_file_id=audio_file_id,
            fingerprint_type=fingerprint_type,
            quality_level=quality_level,
            generation_time_ms=generation_time_ms,
            fingerprint_size_bytes=len(fingerprint_data),
            generation_success=success,
            error_message=error_message
        )
        
        self.fingerprint_metrics.append(metrics)
        
        # Update database state
        if success:
            self.database_state.total_fingerprints += 1
            self.database_state.database_size_mb += len(fingerprint_data) / (1024 * 1024)
        
        # Check for performance issues
        await self._check_generation_performance(metrics)
        
        logger.info(f"Fingerprint generation recorded: {fingerprint_id} "
                   f"({fingerprint_type.value}, {generation_time_ms:.1f}ms)")
        
        return fingerprint_id
    
    async def record_fingerprint_match(self, query_fingerprint_id: str,
                                     matched_fingerprint_id: str,
                                     similarity_score: float,
                                     match_time_ms: float,
                                     audio_offset_seconds: float = 0.0,
                                     duration_matched_seconds: float = 0.0) -> str:
        """Record fingerprint matching results."""
        confidence = self._determine_match_confidence(similarity_score)
        
        match_result = MatchResult(
            query_fingerprint_id=query_fingerprint_id,
            matched_fingerprint_id=matched_fingerprint_id,
            similarity_score=similarity_score,
            confidence=confidence,
            match_time_ms=match_time_ms,
            audio_offset_seconds=audio_offset_seconds,
            duration_matched_seconds=duration_matched_seconds
        )
        
        self.match_results.append(match_result)
        
        # Update search performance
        self._update_search_performance(match_time_ms)
        
        # Check for copyright detection
        if similarity_score >= self.thresholds['similarity_threshold_copyright']:
            await self._trigger_copyright_alert(match_result)
        
        logger.info(f"Fingerprint match recorded: {similarity_score:.3f} confidence "
                   f"({confidence.value}, {match_time_ms:.1f}ms)")
        
        return str(uuid.uuid4())  # Match record ID
    
    def _determine_match_confidence(self, similarity_score: float) -> MatchConfidence:
        """Determine match confidence based on similarity score."""
        if similarity_score >= 0.95:
            return MatchConfidence.EXACT
        elif similarity_score >= 0.85:
            return MatchConfidence.HIGH
        elif similarity_score >= 0.70:
            return MatchConfidence.MEDIUM
        elif similarity_score >= 0.50:
            return MatchConfidence.LOW
        else:
            return MatchConfidence.NO_MATCH
    
    def _update_search_performance(self, match_time_ms: float):
        """Update running average of search performance."""
        if hasattr(self, '_search_times'):
            self._search_times.append(match_time_ms)
            if len(self._search_times) > 1000:
                self._search_times = self._search_times[-1000:]
        else:
            self._search_times = [match_time_ms]
        
        self.database_state.search_performance_ms = statistics.mean(self._search_times)
    
    async def _check_generation_performance(self, metrics: FingerprintMetrics):
        """Check fingerprint generation performance and alert if needed."""
        if not metrics.generation_success:
            logger.error(f"Fingerprint generation failed: {metrics.error_message}")
            return
        
        if metrics.generation_time_ms > self.thresholds['generation_time_critical_ms']:
            logger.warning(f"Critical: Fingerprint generation took {metrics.generation_time_ms:.1f}ms "
                          f"for {metrics.fingerprint_type.value}")
        elif metrics.generation_time_ms > self.thresholds['generation_time_warning_ms']:
            logger.warning(f"Warning: Slow fingerprint generation {metrics.generation_time_ms:.1f}ms "
                          f"for {metrics.fingerprint_type.value}")
    
    async def _trigger_copyright_alert(self, match_result: MatchResult):
        """Trigger copyright detection alert."""
        logger.warning(f"Potential copyright match detected: {match_result.similarity_score:.3f} "
                      f"similarity between {match_result.query_fingerprint_id} and "
                      f"{match_result.matched_fingerprint_id}")
        
        # In production, this would integrate with alerting system
        alert_data = {
            'type': 'copyright_detection',
            'similarity_score': match_result.similarity_score,
            'confidence': match_result.confidence.value,
            'timestamp': match_result.timestamp.isoformat(),
            'query_fingerprint': match_result.query_fingerprint_id,
            'matched_fingerprint': match_result.matched_fingerprint_id
        }
    
    def get_fingerprinting_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive fingerprinting statistics."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_fingerprints = [
            m for m in self.fingerprint_metrics
            if m.timestamp >= cutoff_time
        ]
        
        recent_matches = [
            m for m in self.match_results
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_fingerprints and not recent_matches:
            return {"message": f"No fingerprinting activity in last {hours} hours"}
        
        # Generation statistics
        successful_generations = [m for m in recent_fingerprints if m.generation_success]
        generation_times = [m.generation_time_ms for m in successful_generations]
        
        # Match statistics
        match_times = [m.match_time_ms for m in recent_matches]
        similarity_scores = [m.similarity_score for m in recent_matches]
        
        # Confidence distribution
        confidence_counts = {}
        for confidence in MatchConfidence:
            confidence_counts[confidence.value] = len([
                m for m in recent_matches if m.confidence == confidence
            ])
        
        # Type distribution
        type_counts = {}
        for fp_type in FingerprintType:
            type_counts[fp_type.value] = len([
                m for m in recent_fingerprints if m.fingerprint_type == fp_type
            ])
        
        return {
            'period_hours': hours,
            'generation_stats': {
                'total_generated': len(recent_fingerprints),
                'successful_generations': len(successful_generations),
                'success_rate': len(successful_generations) / len(recent_fingerprints) if recent_fingerprints else 0,
                'avg_generation_time_ms': statistics.mean(generation_times) if generation_times else 0,
                'max_generation_time_ms': max(generation_times) if generation_times else 0,
                'type_distribution': type_counts
            },
            'matching_stats': {
                'total_matches': len(recent_matches),
                'avg_match_time_ms': statistics.mean(match_times) if match_times else 0,
                'max_match_time_ms': max(match_times) if match_times else 0,
                'avg_similarity_score': statistics.mean(similarity_scores) if similarity_scores else 0,
                'confidence_distribution': confidence_counts,
                'copyright_detections': len([m for m in recent_matches 
                                           if m.similarity_score >= self.thresholds['similarity_threshold_copyright']])
            },
            'database_stats': {
                'total_fingerprints': self.database_state.total_fingerprints,
                'database_size_mb': self.database_state.database_size_mb,
                'index_size_mb': self.database_state.index_size_mb,
                'avg_search_time_ms': self.database_state.search_performance_ms,
                'last_optimization': self.database_state.last_optimization.isoformat()
            }
        }
    
    def get_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get performance trends over multiple days."""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Group metrics by day
        daily_stats = defaultdict(lambda: {
            'generations': [],
            'matches': [],
            'generation_times': [],
            'match_times': []
        })
        
        for metrics in self.fingerprint_metrics:
            if metrics.timestamp >= cutoff_time:
                day_key = metrics.timestamp.date().isoformat()
                daily_stats[day_key]['generations'].append(metrics)
                if metrics.generation_success:
                    daily_stats[day_key]['generation_times'].append(metrics.generation_time_ms)
        
        for match in self.match_results:
            if match.timestamp >= cutoff_time:
                day_key = match.timestamp.date().isoformat()
                daily_stats[day_key]['matches'].append(match)
                daily_stats[day_key]['match_times'].append(match.match_time_ms)
        
        trends = {}
        for day, stats in daily_stats.items():
            trends[day] = {
                'total_generations': len(stats['generations']),
                'successful_generations': len(stats['generation_times']),
                'avg_generation_time_ms': statistics.mean(stats['generation_times']) if stats['generation_times'] else 0,
                'total_matches': len(stats['matches']),
                'avg_match_time_ms': statistics.mean(stats['match_times']) if stats['match_times'] else 0,
                'copyright_detections': len([m for m in stats['matches'] 
                                           if m.similarity_score >= self.thresholds['similarity_threshold_copyright']])
            }
        
        return {
            'period_days': days,
            'daily_trends': trends,
            'overall_trends': {
                'total_fingerprints_generated': sum(len(stats['generations']) for stats in daily_stats.values()),
                'total_matches_performed': sum(len(stats['matches']) for stats in daily_stats.values()),
                'avg_daily_generations': statistics.mean([len(stats['generations']) for stats in daily_stats.values()]) if daily_stats else 0,
                'avg_daily_matches': statistics.mean([len(stats['matches']) for stats in daily_stats.values()]) if daily_stats else 0
            },
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def optimize_database(self) -> Dict[str, Any]:
        """Simulate database optimization and return results."""
        start_time = datetime.utcnow()
        
        # Simulate optimization process
        await asyncio.sleep(0.1)  # Simulate work
        
        old_size = self.database_state.database_size_mb
        old_index_size = self.database_state.index_size_mb
        
        # Simulate compression and index optimization
        self.database_state.database_size_mb *= 0.85  # 15% compression
        self.database_state.index_size_mb *= 0.90    # 10% index optimization
        self.database_state.last_optimization = datetime.utcnow()
        
        optimization_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        logger.info(f"Database optimization completed in {optimization_time:.1f}ms")
        
        return {
            'optimization_time_ms': optimization_time,
            'database_size_reduction_mb': old_size - self.database_state.database_size_mb,
            'index_size_reduction_mb': old_index_size - self.database_state.index_size_mb,
            'compression_ratio': self.database_state.database_size_mb / old_size if old_size > 0 else 1,
            'new_database_size_mb': self.database_state.database_size_mb,
            'new_index_size_mb': self.database_state.index_size_mb,
            'optimization_timestamp': self.database_state.last_optimization.isoformat()
        }
    
    def clear_old_metrics(self, days: int = 30):
        """Clear metrics older than specified days."""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        old_fingerprint_count = len(self.fingerprint_metrics)
        old_match_count = len(self.match_results)
        
        self.fingerprint_metrics = [
            m for m in self.fingerprint_metrics
            if m.timestamp >= cutoff_time
        ]
        
        self.match_results = [
            m for m in self.match_results
            if m.timestamp >= cutoff_time
        ]
        
        logger.info(f"Cleared {old_fingerprint_count - len(self.fingerprint_metrics)} "
                   f"fingerprint metrics and {old_match_count - len(self.match_results)} "
                   f"match results older than {days} days")

# Global fingerprinting monitor instance
audio_fingerprinting_monitor = AudioFingerprintingMonitor()

# Export main components
__all__ = [
    'AudioFingerprintingMonitor',
    'FingerprintMetrics',
    'MatchResult',
    'FingerprintDatabase',
    'FingerprintType',
    'FingerprintQuality',
    'MatchConfidence',
    'audio_fingerprinting_monitor'
]