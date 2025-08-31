"""IA Influencer Agent - Content Protection Performance Metrics
Specialized metrics collection for content fingerprinting and protection systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  AVERTISSEMENT LÉGAL STRICT ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
- Audio fingerprinting performance tracking
- Video content analysis metrics
- Image protection analytics
- Text plagiarism detection metrics
- Cross-platform monitoring
- Real-time accuracy measurement
- Processing speed optimization
- False positive/negative tracking
"""import asyncio
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import statistics

from backend.core.logging import get_logger
from backend.utils.redis_manager import RedisManager
from backend.utils.database import get_database_session
from .config import get_metrics_config

logger = get_logger(__name__)
metrics_config = get_metrics_config()


class ContentType(Enum):
    """Content types for protection metrics"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"


class FingerprintAlgorithm(Enum):
    """Fingerprinting algorithms"""    # Audio algorithms
    CHROMAPRINT = "chromaprint"
    SPECTRAL_HASH = "spectral_hash"
    MFCC = "mfcc"
    
    # Video algorithms
    PERCEPTUAL_HASH = "perceptual_hash"
    TEMPORAL_HASH = "temporal_hash"
    KEYFRAME_ANALYSIS = "keyframe_analysis"
    
    # Image algorithms
    DHASH = "dhash"
    PHASH = "phash"
    WAVELET_HASH = "wavelet_hash"
    
    # Text algorithms
    SHINGLE_HASH = "shingle_hash"
    SEMANTIC_HASH = "semantic_hash"
    SYNTACTIC_HASH = "syntactic_hash"


class MatchAccuracy(Enum):
    """Match accuracy classifications"""    TRUE_POSITIVE = "true_positive"
    FALSE_POSITIVE = "false_positive"
    TRUE_NEGATIVE = "true_negative"
    FALSE_NEGATIVE = "false_negative"


@dataclass
class FingerprintMetrics:
    """Fingerprint processing metrics"""    content_type: ContentType
    algorithm: FingerprintAlgorithm
    processing_time: float
    file_size: int
    duration: Optional[float]
    quality_score: float
    success: bool
    error_message: Optional[str]
    tenant_id: str
    timestamp: datetime


@dataclass
class MatchMetrics:
    """Content matching metrics"""    original_fingerprint_id: str
    matched_content_url: str
    similarity_score: float
    algorithm_used: FingerprintAlgorithm
    processing_time: float
    match_accuracy: Optional[MatchAccuracy]
    platform: str
    tenant_id: str
    timestamp: datetime


class ContentProtectionMetricsCollector:
    """    Specialized metrics collector for content protection systems
    
    Tracks fingerprinting performance, matching accuracy, and 
    protection effectiveness across all content types
    """    
    def __init__(self):
        self.redis_manager = RedisManager()
        self.logger = logger
        
        # Performance tracking windows
        self.processing_times = defaultdict(lambda: deque(maxlen=1000))
        self.accuracy_scores = defaultdict(lambda: deque(maxlen=1000))
        self.similarity_scores = defaultdict(lambda: deque(maxlen=1000))
        
        # Real-time counters
        self.total_fingerprints = defaultdict(int)
        self.successful_matches = defaultdict(int)
        self.false_positives = defaultdict(int)
        
        # Background tasks
        self.metrics_calculation_task = asyncio.create_task(
            self._calculate_performance_metrics()
        )
    
    async def track_fingerprint_creation(
        self,
        tenant_id: str,
        content_type: ContentType,
        algorithm: FingerprintAlgorithm,
        processing_time: float,
        file_size: int,
        duration: Optional[float],
        quality_score: float,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """Track fingerprint creation metrics"""        
        metrics = FingerprintMetrics(
            content_type=content_type,
            algorithm=algorithm,
            processing_time=processing_time,
            file_size=file_size,
            duration=duration,
            quality_score=quality_score,
            success=success,
            error_message=error_message,
            tenant_id=tenant_id,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Store metrics
        await self._store_fingerprint_metrics(metrics)
        
        # Update real-time tracking
        key = f"{tenant_id}:{content_type.value}:{algorithm.value}"
        self.processing_times[key].append(processing_time)
        self.total_fingerprints[key] += 1
        
        if success:
            self.accuracy_scores[key].append(quality_score)
        
        # Store in Redis for real-time access
        await self.redis_manager.list_push(
            f"fingerprint_metrics:{tenant_id}:{content_type.value}",
            json.dumps({
                "algorithm": algorithm.value,
                "processing_time": processing_time,
                "quality_score": quality_score,
                "success": success,
                "timestamp": metrics.timestamp.isoformat()
            }),
            expire=86400  # 24 hours
        )
    
    async def track_content_match(
        self,
        tenant_id: str,
        original_fingerprint_id: str,
        matched_content_url: str,
        similarity_score: float,
        algorithm_used: FingerprintAlgorithm,
        processing_time: float,
        platform: str,
        match_accuracy: Optional[MatchAccuracy] = None
    ) -> None:
        """Track content matching metrics"""        
        metrics = MatchMetrics(
            original_fingerprint_id=original_fingerprint_id,
            matched_content_url=matched_content_url,
            similarity_score=similarity_score,
            algorithm_used=algorithm_used,
            processing_time=processing_time,
            match_accuracy=match_accuracy,
            platform=platform,
            tenant_id=tenant_id,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Store metrics
        await self._store_match_metrics(metrics)
        
        # Update real-time tracking
        key = f"{tenant_id}:{algorithm_used.value}:{platform}"
        self.similarity_scores[key].append(similarity_score)
        
        if match_accuracy == MatchAccuracy.TRUE_POSITIVE:
            self.successful_matches[key] += 1
        elif match_accuracy == MatchAccuracy.FALSE_POSITIVE:
            self.false_positives[key] += 1
        
        # Store in Redis for real-time access
        await self.redis_manager.list_push(
            f"match_metrics:{tenant_id}:{platform}",
            json.dumps({
                "similarity_score": similarity_score,
                "algorithm": algorithm_used.value,
                "processing_time": processing_time,
                "accuracy": match_accuracy.value if match_accuracy else None,
                "timestamp": metrics.timestamp.isoformat()
            }),
            expire=86400  # 24 hours
        )
    
    async def get_fingerprinting_performance(
        self,
        tenant_id: str,
        content_type: Optional[ContentType] = None,
        time_range: str = "1h"
    ) -> Dict[str, Any]:
        """Get fingerprinting performance metrics"""        
        try:
            # Parse time range
            if time_range == "15m":
                start_time = datetime.now(timezone.utc) - timedelta(minutes=15)
            elif time_range == "1h":
                start_time = datetime.now(timezone.utc) - timedelta(hours=1)
            elif time_range == "24h":
                start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            elif time_range == "7d":
                start_time = datetime.now(timezone.utc) - timedelta(days=7)
            else:
                start_time = datetime.now(timezone.utc) - timedelta(hours=1)
            
            async with get_database_session() as session:
                # Build query based on content type filter
                content_filter = ""
                params = [tenant_id, start_time]
                
                if content_type:
                    content_filter = "AND content_type = $3"
                    params.append(content_type.value)
                
                result = await session.fetchrow(f"""                    SELECT 
                        COUNT(*) as total_fingerprints,
                        COUNT(CASE WHEN success = true THEN 1 END) as successful_fingerprints,
                        AVG(processing_time) as avg_processing_time,
                        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY processing_time) as p95_processing_time,
                        AVG(quality_score) as avg_quality_score,
                        MIN(processing_time) as min_processing_time,
                        MAX(processing_time) as max_processing_time
                    FROM fingerprint_metrics 
                    WHERE tenant_id = $1 AND timestamp >= $2 {content_filter}
                """, *params)
                
                # Get algorithm breakdown
                algorithm_stats = await session.fetch(f"""                    SELECT 
                        algorithm,
                        COUNT(*) as count,
                        AVG(processing_time) as avg_time,
                        AVG(quality_score) as avg_quality
                    FROM fingerprint_metrics 
                    WHERE tenant_id = $1 AND timestamp >= $2 {content_filter}
                    GROUP BY algorithm
                    ORDER BY count DESC
                """, *params)
                
                return {
                    "time_range": time_range,
                    "total_fingerprints": result["total_fingerprints"],
                    "success_rate": (
                        result["successful_fingerprints"] / max(result["total_fingerprints"], 1)
                    ),
                    "avg_processing_time": float(result["avg_processing_time"] or 0),
                    "p95_processing_time": float(result["p95_processing_time"] or 0),
                    "avg_quality_score": float(result["avg_quality_score"] or 0),
                    "min_processing_time": float(result["min_processing_time"] or 0),
                    "max_processing_time": float(result["max_processing_time"] or 0),
                    "algorithm_breakdown": [
                        {
                            "algorithm": row["algorithm"],
                            "count": row["count"],
                            "avg_processing_time": float(row["avg_time"]),
                            "avg_quality": float(row["avg_quality"])
                        }
                        for row in algorithm_stats
                    ],
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting fingerprinting performance: {e}")
            return {}
    
    async def get_matching_accuracy_metrics(
        self,
        tenant_id: str,
        platform: Optional[str] = None,
        time_range: str = "1h"
    ) -> Dict[str, Any]:
        """Get content matching accuracy metrics"""        
        try:
            # Parse time range
            if time_range == "15m":
                start_time = datetime.now(timezone.utc) - timedelta(minutes=15)
            elif time_range == "1h":
                start_time = datetime.now(timezone.utc) - timedelta(hours=1)
            elif time_range == "24h":
                start_time = datetime.now(timezone.utc) - timedelta(hours=24)
            elif time_range == "7d":
                start_time = datetime.now(timezone.utc) - timedelta(days=7)
            else:
                start_time = datetime.now(timezone.utc) - timedelta(hours=1)
            
            async with get_database_session() as session:
                # Build query based on platform filter
                platform_filter = ""
                params = [tenant_id, start_time]
                
                if platform:
                    platform_filter = "AND platform = $3"
                    params.append(platform)
                
                result = await session.fetchrow(f"""                    SELECT 
                        COUNT(*) as total_matches,
                        COUNT(CASE WHEN match_accuracy = 'true_positive' THEN 1 END) as true_positives,
                        COUNT(CASE WHEN match_accuracy = 'false_positive' THEN 1 END) as false_positives,
                        COUNT(CASE WHEN match_accuracy = 'true_negative' THEN 1 END) as true_negatives,
                        COUNT(CASE WHEN match_accuracy = 'false_negative' THEN 1 END) as false_negatives,
                        AVG(similarity_score) as avg_similarity_score,
                        AVG(processing_time) as avg_processing_time
                    FROM match_metrics 
                    WHERE tenant_id = $1 AND timestamp >= $2 {platform_filter}
                """, *params)
                
                # Calculate accuracy metrics
                true_positives = result["true_positives"]
                false_positives = result["false_positives"]
                true_negatives = result["true_negatives"]
                false_negatives = result["false_negatives"]
                
                total_classified = true_positives + false_positives + true_negatives + false_negatives
                
                if total_classified > 0:
                    accuracy = (true_positives + true_negatives) / total_classified
                    precision = true_positives / max(true_positives + false_positives, 1)
                    recall = true_positives / max(true_positives + false_negatives, 1)
                    f1_score = 2 * (precision * recall) / max(precision + recall, 0.001)
                else:
                    accuracy = precision = recall = f1_score = 0.0
                
                # Get platform breakdown
                platform_stats = await session.fetch(f"""                    SELECT 
                        platform,
                        COUNT(*) as total_matches,
                        AVG(similarity_score) as avg_similarity,
                        COUNT(CASE WHEN match_accuracy = 'true_positive' THEN 1 END) as true_positives
                    FROM match_metrics 
                    WHERE tenant_id = $1 AND timestamp >= $2 {platform_filter}
                    GROUP BY platform
                    ORDER BY total_matches DESC
                """, *params)
                
                return {
                    "time_range": time_range,
                    "total_matches": result["total_matches"],
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1_score,
                    "true_positives": true_positives,
                    "false_positives": false_positives,
                    "true_negatives": true_negatives,
                    "false_negatives": false_negatives,
                    "avg_similarity_score": float(result["avg_similarity_score"] or 0),
                    "avg_processing_time": float(result["avg_processing_time"] or 0),
                    "platform_breakdown": [
                        {
                            "platform": row["platform"],
                            "total_matches": row["total_matches"],
                            "avg_similarity": float(row["avg_similarity"]),
                            "true_positives": row["true_positives"]
                        }
                        for row in platform_stats
                    ],
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting matching accuracy metrics: {e}")
            return {}
    
    async def get_realtime_protection_status(
        self,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get real-time protection system status"""        
        try:
            # Get recent metrics from Redis
            fingerprint_data = await self.redis_manager.list_range(
                f"fingerprint_metrics:{tenant_id}:*",
                -100,  # Last 100 entries
                -1
            )
            
            match_data = await self.redis_manager.list_range(
                f"match_metrics:{tenant_id}:*",
                -100,  # Last 100 entries
                -1
            )
            
            # Calculate real-time statistics
            recent_fingerprints = len(fingerprint_data) if fingerprint_data else 0
            recent_matches = len(match_data) if match_data else 0
            
            # Processing speed analysis
            processing_times = []
            quality_scores = []
            
            if fingerprint_data:
                for entry in fingerprint_data[-20:]:  # Last 20 entries
                    try:
                        data = json.loads(entry)
                        processing_times.append(data["processing_time"])
                        if data["success"]:
                            quality_scores.append(data["quality_score"])
                    except:
                        continue
            
            avg_processing_time = statistics.mean(processing_times) if processing_times else 0
            avg_quality = statistics.mean(quality_scores) if quality_scores else 0
            
            # System health indicators
            health_score = 100.0
            
            if avg_processing_time > 5.0:  # Slow processing
                health_score -= 20
            if avg_quality < 0.8:  # Low quality
                health_score -= 15
            if recent_fingerprints == 0:  # No activity
                health_score -= 10
            
            return {
                "tenant_id": tenant_id,
                "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 60 else "critical",
                "health_score": health_score,
                "recent_fingerprints": recent_fingerprints,
                "recent_matches": recent_matches,
                "avg_processing_time": avg_processing_time,
                "avg_quality_score": avg_quality,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting real-time protection status: {e}")
            return {
                "tenant_id": tenant_id,
                "status": "error",
                "health_score": 0,
                "error": str(e)
            }
    
    async def _store_fingerprint_metrics(self, metrics: FingerprintMetrics) -> None:
        """Store fingerprint metrics in database"""        try:
            async with get_database_session() as session:
                await session.execute(
                    """                    INSERT INTO fingerprint_metrics 
                    (tenant_id, content_type, algorithm, processing_time, file_size, 
                     duration, quality_score, success, error_message, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """,
                    metrics.tenant_id,
                    metrics.content_type.value,
                    metrics.algorithm.value,
                    metrics.processing_time,
                    metrics.file_size,
                    metrics.duration,
                    metrics.quality_score,
                    metrics.success,
                    metrics.error_message,
                    metrics.timestamp
                )
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing fingerprint metrics: {e}")
    
    async def _store_match_metrics(self, metrics: MatchMetrics) -> None:
        """Store match metrics in database"""        try:
            async with get_database_session() as session:
                await session.execute(
                    """                    INSERT INTO match_metrics 
                    (tenant_id, original_fingerprint_id, matched_content_url, 
                     similarity_score, algorithm_used, processing_time, match_accuracy, 
                     platform, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """,
                    metrics.tenant_id,
                    metrics.original_fingerprint_id,
                    metrics.matched_content_url,
                    metrics.similarity_score,
                    metrics.algorithm_used.value,
                    metrics.processing_time,
                    metrics.match_accuracy.value if metrics.match_accuracy else None,
                    metrics.platform,
                    metrics.timestamp
                )
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing match metrics: {e}")
    
    async def _calculate_performance_metrics(self) -> None:
        """Background task to calculate and cache performance metrics"""        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Calculate aggregated metrics for all tenants
                await self._aggregate_tenant_metrics()
                
            except Exception as e:
                self.logger.error(f"Error in performance metrics calculation: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _aggregate_tenant_metrics(self) -> None:
        """Aggregate metrics for all tenants"""        try:
            async with get_database_session() as session:
                # Get list of active tenants
                tenants = await session.fetch(
                    """                    SELECT DISTINCT tenant_id 
                    FROM fingerprint_metrics 
                    WHERE timestamp >= NOW() - INTERVAL '1 hour'
                    """                )
                
                for tenant_row in tenants:
                    tenant_id = tenant_row["tenant_id"]
                    
                    # Calculate and cache aggregated metrics
                    performance_metrics = await self.get_fingerprinting_performance(
                        tenant_id, time_range="1h"
                    )
                    
                    accuracy_metrics = await self.get_matching_accuracy_metrics(
                        tenant_id, time_range="1h"
                    )
                    
                    # Cache in Redis
                    await self.redis_manager.set_json(
                        f"aggregated_protection_metrics:{tenant_id}",
                        {
                            "performance": performance_metrics,
                            "accuracy": accuracy_metrics,
                            "calculated_at": datetime.now(timezone.utc).isoformat()
                        },
                        expire=600  # 10 minutes
                    )
                    
        except Exception as e:
            self.logger.error(f"Error aggregating tenant metrics: {e}")
