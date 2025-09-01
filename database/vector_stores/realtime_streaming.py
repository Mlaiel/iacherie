"""Real-time Vector Streaming System

This module provides real-time vector streaming capabilities for live content protection,
instant fingerprinting, and immediate similarity matching for the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

WARNING: This code is proprietary to Fahed Mlaiel. Any unauthorized copying, modification, 
or distribution without explicit written permission is strictly prohibited and will result 
in legal action under German and international copyright law.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, AsyncGenerator
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import numpy as np
import aioredis
import websockets
from websockets.server import WebSocketServerProtocol
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
import torch
from concurrent.futures import ThreadPoolExecutor

from backend.core.config import get_settings
from backend.core.database import get_db_session
from backend.models.content_fingerprints import ContentFingerprint
from backend.models.protection_alerts import ProtectionAlert
from backend.utils.exceptions import StreamingError, VectorStoreError
from backend.utils.performance import measure_execution_time
from backend.utils.monitoring import MetricsCollector
from backend.utils.security import validate_streaming_token

from .vector_store_manager import VectorStoreManager
from .embedding_generator import EmbeddingGenerator
from .similarity_search import SimilaritySearchEngine

logger = logging.getLogger(__name__)
settings = get_settings()


class StreamingMode(Enum):
    """
Real-time streaming modes"""

    LIVE_AUDIO = "live_audio"
    LIVE_VIDEO = "live_video"
    BATCH_UPLOAD = "batch_upload"
    CONTINUOUS_MONITORING = "continuous_monitoring"


class StreamingPriority(Enum):
    """Streaming priority levels"""

    CRITICAL = "critical"  # < 100ms latency
    HIGH = "high"         # < 500ms latency
    MEDIUM = "medium"     # < 2s latency
    LOW = "low"          # < 10s latency


@dataclass
class StreamingConfig:
    """Configuration for real-time streaming"""
    mode: StreamingMode
    priority: StreamingPriority
    content_type: str
    user_id: int
    buffer_size: int = 1024
    chunk_duration: float = 1.0  # seconds
    overlap_ratio: float = 0.2
    similarity_threshold: float = 0.85
    enable_live_alerts: bool = True
    max_concurrent_streams: int = 100
    enable_gpu_acceleration: bool = True


@dataclass
class StreamChunk:
    """
Real-time stream chunk data"""
    chunk_id: str
    user_id: int
    content_type: str
    timestamp: datetime
    data: bytes
    metadata: Dict[str, Any]
    priority: StreamingPriority
    vector_embedding: Optional[np.ndarray] = None
    similarity_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LiveAlert:
    """
Real-time protection alert"""
    alert_id: str
    user_id: int
    content_type: str
    similarity_score: float
    matched_content_id: str
    detected_platform: str
    evidence_url: str
    timestamp: datetime
    confidence_level: float
    alert_severity: str


class RealTimeVectorStreaming:
    """
    Real-time vector streaming system for live content protection.
    
    Features:
    - Sub-second fingerprinting and matching
    - Real-time similarity search across platforms
    - Live streaming WebSocket support
    - GPU-accelerated processing
    - Instant alert generation
    - Multi-stream concurrent processing
    - Adaptive quality based on network conditions
    """
    
    def __init__(self):
        """
Initialize real-time streaming system"""
        self.config = {}
        self.active_streams: Dict[str, StreamingConfig] = {}
        self.stream_buffers: Dict[str, List[StreamChunk]] = {}
        self.websocket_connections: Dict[str, WebSocketServerProtocol] = {}
        
        # Core components
        self.vector_manager = VectorStoreManager()
        self.embedding_generator = EmbeddingGenerator()
        self.similarity_engine = SimilaritySearchEngine()
        
        # Performance tracking
        self.metrics_collector = MetricsCollector()
        self.processing_stats = {
            "total_chunks_processed": 0,
            "average_processing_time": 0.0,
            "alerts_generated": 0,
            "active_streams_count": 0
        }
        
        # Redis for real-time caching
        self.redis_client = None
        
        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(max_workers=settings.STREAMING_WORKERS)
        
        logger.info("Initialized RealTimeVectorStreaming system")
    
    async def initialize(self) -> None:
        """Initialize streaming system and connections"""
        try:
            # Initialize core components
            await self.vector_manager.initialize()
            await self.embedding_generator.initialize()
            await self.similarity_engine.initialize()
            
            # Connect to Redis for real-time caching
            self.redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            logger.info("Real-time streaming system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize streaming system: {str(e)}")
            raise StreamingError(f"Initialization failed: {str(e)}")
    
    @measure_execution_time
    async def start_stream(
        self,
        stream_id: str,
        config: StreamingConfig,
        websocket: Optional[WebSocketServerProtocol] = None
    ) -> bool:
        """
        Start a new real-time streaming session
        
        Args:
            stream_id: Unique stream identifier
            config: Streaming configuration
            websocket: Optional WebSocket connection for real-time updates
            
        Returns:
            Success status
        """
        try:
            # Validate stream limits
            if len(self.active_streams) >= config.max_concurrent_streams:
                raise StreamingError("Maximum concurrent streams reached")
            
            # Validate user permissions
            if not await self._validate_streaming_permissions(config.user_id, config.mode):
                raise StreamingError("Insufficient permissions for streaming")
            
            # Initialize stream
            self.active_streams[stream_id] = config
            self.stream_buffers[stream_id] = []
            
            if websocket:
                self.websocket_connections[stream_id] = websocket
            
            # Start processing task
            asyncio.create_task(self._process_stream(stream_id))
            
            # Update metrics
            self.processing_stats["active_streams_count"] += 1
            
            # Send confirmation
            if websocket:
                await websocket.send(json.dumps({
                    "type": "stream_started",
                    "stream_id": stream_id,
                    "status": "active",
                    "timestamp": datetime.now().isoformat()
                }))
            
            logger.info(f"Started streaming session: {stream_id} for user {config.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start stream {stream_id}: {str(e)}")
            return False
    
    @measure_execution_time
    async def process_chunk(
        self,
        stream_id: str,
        chunk_data: bytes,
        metadata: Dict[str, Any] = None
    ) -> Optional[List[LiveAlert]]:
        """
        Process incoming stream chunk in real-time
        
        Args:
            stream_id: Stream identifier
            chunk_data: Raw chunk data
            metadata: Optional metadata
            
        Returns:
            List of generated alerts if any
        """
        try:
            if stream_id not in self.active_streams:
                raise StreamingError(f"Stream {stream_id} not found")
            
            config = self.active_streams[stream_id]
            
            # Create chunk object
            chunk = StreamChunk(
                chunk_id=f"{stream_id}_{datetime.now().timestamp()}",
                user_id=config.user_id,
                content_type=config.content_type,
                timestamp=datetime.now(timezone.utc),
                data=chunk_data,
                metadata=metadata or {},
                priority=config.priority
            )
            
            # Add to buffer
            self.stream_buffers[stream_id].append(chunk)
            
            # Process chunk based on priority
            if config.priority == StreamingPriority.CRITICAL:
                return await self._process_chunk_critical(chunk, config)
            elif config.priority == StreamingPriority.HIGH:
                return await self._process_chunk_high(chunk, config)
            else:
                # Queue for batch processing
                await self._queue_chunk_processing(chunk, config)
                return []
            
        except Exception as e:
            logger.error(f"Failed to process chunk for stream {stream_id}: {str(e)}")
            return []
    
    async def _process_chunk_critical(
        self,
        chunk: StreamChunk,
        config: StreamingConfig
    ) -> List[LiveAlert]:
        """Process chunk with critical priority (< 100ms)"""
        start_time = datetime.now()
        alerts = []
        
        try:
            # Fast embedding generation
            if config.content_type == "audio":
                embedding = await self._fast_audio_embedding(chunk.data)
            elif config.content_type == "video":
                embedding = await self._fast_video_embedding(chunk.data)
            elif config.content_type == "image":
                embedding = await self._fast_image_embedding(chunk.data)
            else:
                embedding = await self._fast_text_embedding(chunk.data.decode('utf-8'))
            
            chunk.vector_embedding = embedding
            
            # Immediate similarity search using cache
            similar_results = await self._cached_similarity_search(
                config.content_type,
                embedding,
                threshold=config.similarity_threshold
            )
            
            # Generate alerts for high similarity matches
            for result in similar_results:
                if result["similarity_score"] >= config.similarity_threshold:
                    alert = await self._generate_live_alert(chunk, result, config)
                    alerts.append(alert)
            
            # Send real-time update via WebSocket
            if chunk.user_id in self.websocket_connections:
                await self._send_realtime_update(chunk.user_id, chunk, alerts)
            
            # Update performance metrics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            await self._update_processing_metrics(processing_time, len(alerts))
            
            return alerts
            
        except Exception as e:
            logger.error(f"Critical chunk processing failed: {str(e)}")
            return []
    
    async def _process_chunk_high(
        self,
        chunk: StreamChunk,
        config: StreamingConfig
    ) -> List[LiveAlert]:
        """Process chunk with high priority (< 500ms)"""
        start_time = datetime.now()
        alerts = []
        
        try:
            # Generate high-quality embedding
            embedding = await self.embedding_generator.generate_embedding(
                content_type=config.content_type,
                data=chunk.data,
                model_quality="standard"
            )
            
            chunk.vector_embedding = embedding
            
            # Perform similarity search across multiple stores
            similar_results = await self.similarity_engine.search_similar_content(
                content_type=config.content_type,
                query_vector=embedding,
                limit=20,
                threshold=config.similarity_threshold
            )
            
            # Process results and generate alerts
            for result in similar_results:
                if result.similarity_score >= config.similarity_threshold:
                    alert = await self._generate_live_alert(chunk, result, config)
                    alerts.append(alert)
            
            # Cache results for future searches
            await self._cache_search_results(chunk, similar_results)
            
            # Send updates
            if chunk.user_id in self.websocket_connections:
                await self._send_realtime_update(chunk.user_id, chunk, alerts)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            await self._update_processing_metrics(processing_time, len(alerts))
            
            return alerts
            
        except Exception as e:
            logger.error(f"High priority chunk processing failed: {str(e)}")
            return []
    
    async def _fast_audio_embedding(self, audio_data: bytes) -> np.ndarray:
        """Generate fast audio embedding for critical processing"""
        try:
            # Use lightweight audio features for speed
            import io
            import soundfile as sf
            
            # Convert bytes to audio array
            audio_array, sr = sf.read(io.BytesIO(audio_data))
            
            # Extract MFCC features (fast)
            mfccs = librosa.feature.mfcc(y=audio_array, sr=sr, n_mfcc=13)
            
            # Create embedding from statistics
            embedding = np.concatenate([
                np.mean(mfccs, axis=1),
                np.std(mfccs, axis=1),
                np.max(mfccs, axis=1),
                np.min(mfccs, axis=1)
            ])
            
            # Pad or truncate to fixed size
            target_size = 512
            if len(embedding) < target_size:
                embedding = np.pad(embedding, (0, target_size - len(embedding)))
            else:
                embedding = embedding[:target_size]
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Fast audio embedding failed: {str(e)}")
            return np.zeros(512, dtype=np.float32)
    
    async def _fast_video_embedding(self, video_data: bytes) -> np.ndarray:
        """Generate fast video embedding for critical processing"""
        try:
            # Extract keyframes and create embeddings
            import io
            import tempfile
            
            # Save to temporary file for OpenCV
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
                tmp_file.write(video_data)
                tmp_file.flush()
                
                # Extract single frame
                cap = cv2.VideoCapture(tmp_file.name)
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    # Resize and normalize
                    frame = cv2.resize(frame, (224, 224))
                    frame = frame.astype(np.float32) / 255.0
                    
                    # Simple CNN-like features
                    embedding = np.mean(frame, axis=(0, 1))  # Color histograms
                    embedding = np.concatenate([
                        embedding,
                        np.std(frame, axis=(0, 1)),
                        np.histogram(frame.flatten(), bins=50)[0]
                    ])
                    
                    # Normalize to 512 dimensions
                    if len(embedding) < 512:
                        embedding = np.pad(embedding, (0, 512 - len(embedding)))
                    else:
                        embedding = embedding[:512]
                    
                    os.unlink(tmp_file.name)
                    return embedding.astype(np.float32)
            
            return np.zeros(512, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Fast video embedding failed: {str(e)}")
            return np.zeros(512, dtype=np.float32)
    
    async def _fast_image_embedding(self, image_data: bytes) -> np.ndarray:
        """Generate fast image embedding for critical processing"""
        try:
            # Convert bytes to image
            image = Image.open(io.BytesIO(image_data))
            image = image.convert('RGB')
            image = image.resize((224, 224))
            
            # Convert to numpy array
            img_array = np.array(image).astype(np.float32) / 255.0
            
            # Extract statistical features
            embedding = np.concatenate([
                np.mean(img_array, axis=(0, 1)),  # Color means
                np.std(img_array, axis=(0, 1)),   # Color stds
                np.histogram(img_array.flatten(), bins=100)[0]  # Histogram
            ])
            
            # Normalize to 512 dimensions
            if len(embedding) < 512:
                embedding = np.pad(embedding, (0, 512 - len(embedding)))
            else:
                embedding = embedding[:512]
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Fast image embedding failed: {str(e)}")
            return np.zeros(512, dtype=np.float32)
    
    async def _fast_text_embedding(self, text: str) -> np.ndarray:
        """Generate fast text embedding for critical processing"""
        try:
            # Simple TF-IDF like features for speed
            from collections import Counter
            import re
            
            # Clean and tokenize
            words = re.findall(r'\w+', text.lower())
            word_counts = Counter(words)
            
            # Create simple embedding based on word statistics
            total_words = len(words)
            unique_words = len(word_counts)
            avg_word_length = np.mean([len(word) for word in words]) if words else 0
            
            # Character frequency features
            char_counts = Counter(text.lower())
            char_freqs = [char_counts.get(chr(i), 0) for i in range(ord('a'), ord('z') + 1)]
            
            # Combine features
            embedding = np.array([
                total_words, unique_words, avg_word_length,
                len(text), text.count(' '), text.count('.'),
                text.count('!'), text.count('?'), text.count(',')
            ] + char_freqs)
            
            # Pad to 512 dimensions
            if len(embedding) < 512:
                embedding = np.pad(embedding, (0, 512 - len(embedding)))
            else:
                embedding = embedding[:512]
            
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Fast text embedding failed: {str(e)}")
            return np.zeros(512, dtype=np.float32)
    
    async def _cached_similarity_search(
        self,
        content_type: str,
        query_vector: np.ndarray,
        threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Perform cached similarity search for speed"""
        try:
            # Generate cache key
            vector_hash = hash(query_vector.tobytes())
            cache_key = f"similarity:{content_type}:{vector_hash}:{threshold}"
            
            # Check Redis cache first
            cached_results = await self.redis_client.get(cache_key)
            if cached_results:
                return json.loads(cached_results)
            
            # Perform search if not cached
            search_results = await self.similarity_engine.search_similar_content(
                content_type=content_type,
                query_vector=query_vector,
                limit=10,
                threshold=threshold
            )
            
            # Convert to serializable format
            results = []
            for result in search_results:
                results.append({
                    "content_id": result.content_id,
                    "similarity_score": float(result.similarity_score),
                    "content_type": result.content_type,
                    "metadata": result.metadata
                })
            
            # Cache results for 60 seconds
            await self.redis_client.setex(cache_key, 60, json.dumps(results))
            
            return results
            
        except Exception as e:
            logger.error(f"Cached similarity search failed: {str(e)}")
            return []
    
    async def _generate_live_alert(
        self,
        chunk: StreamChunk,
        similarity_result: Dict[str, Any],
        config: StreamingConfig
    ) -> LiveAlert:
        """Generate live protection alert"""
        try:
            alert = LiveAlert(
                alert_id=f"alert_{chunk.chunk_id}_{similarity_result['content_id']}",
                user_id=chunk.user_id,
                content_type=chunk.content_type,
                similarity_score=similarity_result["similarity_score"],
                matched_content_id=similarity_result["content_id"],
                detected_platform="unknown",  # To be determined by crawler
                evidence_url="",  # To be set by evidence collection
                timestamp=datetime.now(timezone.utc),
                confidence_level=min(similarity_result["similarity_score"] * 1.2, 1.0),
                alert_severity=self._determine_alert_severity(similarity_result["similarity_score"])
            )
            
            # Store alert in database
            await self._store_alert(alert)
            
            # Update metrics
            self.processing_stats["alerts_generated"] += 1
            
            return alert
            
        except Exception as e:
            logger.error(f"Failed to generate live alert: {str(e)}")
            return None
    
    async def _send_realtime_update(
        self,
        user_id: int,
        chunk: StreamChunk,
        alerts: List[LiveAlert]
    ) -> None:
        """Send real-time update via WebSocket"""
        try:
            stream_id = None
            for sid, config in self.active_streams.items():
                if config.user_id == user_id:
                    stream_id = sid
                    break
            
            if stream_id and stream_id in self.websocket_connections:
                websocket = self.websocket_connections[stream_id]
                
                update_data = {
                    "type": "chunk_processed",
                    "chunk_id": chunk.chunk_id,
                    "timestamp": chunk.timestamp.isoformat(),
                    "alerts_count": len(alerts),
                    "alerts": [
                        {
                            "alert_id": alert.alert_id,
                            "similarity_score": alert.similarity_score,
                            "matched_content_id": alert.matched_content_id,
                            "severity": alert.alert_severity,
                            "confidence": alert.confidence_level
                        }
                        for alert in alerts
                    ]
                }
                
                await websocket.send(json.dumps(update_data))
                
        except Exception as e:
            logger.error(f"Failed to send real-time update: {str(e)}")
    
    async def stop_stream(self, stream_id: str) -> bool:
        """Stop streaming session"""
        try:
            if stream_id not in self.active_streams:
                return False
            
            # Clean up stream data
            del self.active_streams[stream_id]
            self.stream_buffers.pop(stream_id, None)
            
            # Close WebSocket if exists
            if stream_id in self.websocket_connections:
                websocket = self.websocket_connections[stream_id]
                await websocket.send(json.dumps({
                    "type": "stream_stopped",
                    "stream_id": stream_id,
                    "timestamp": datetime.now().isoformat()
                }))
                await websocket.close()
                del self.websocket_connections[stream_id]
            
            # Update metrics
            self.processing_stats["active_streams_count"] -= 1
            
            logger.info(f"Stopped streaming session: {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop stream {stream_id}: {str(e)}")
            return False
    
    async def get_stream_stats(self, stream_id: str) -> Dict[str, Any]:
        """Get streaming session statistics"""
        try:
            if stream_id not in self.active_streams:
                return {}
            
            config = self.active_streams[stream_id]
            buffer = self.stream_buffers.get(stream_id, [])
            
            return {
                "stream_id": stream_id,
                "user_id": config.user_id,
                "content_type": config.content_type,
                "mode": config.mode.value,
                "priority": config.priority.value,
                "chunks_processed": len(buffer),
                "alerts_generated": sum(1 for chunk in buffer if chunk.similarity_results),
                "average_similarity": np.mean([
                    max(result["similarity_score"] for result in chunk.similarity_results)
                    for chunk in buffer if chunk.similarity_results
                ]) if buffer else 0.0,
                "duration_seconds": (
                    datetime.now(timezone.utc) - buffer[0].timestamp
                ).total_seconds() if buffer else 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get stream stats for {stream_id}: {str(e)}")
            return {}
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global streaming system statistics"""
        return {
            "active_streams": len(self.active_streams),
            "total_chunks_processed": self.processing_stats["total_chunks_processed"],
            "average_processing_time_ms": self.processing_stats["average_processing_time"],
            "alerts_generated": self.processing_stats["alerts_generated"],
            "system_health": await self._check_system_health()
        }
    
    def _determine_alert_severity(self, similarity_score: float) -> str:
        """Determine alert severity based on similarity score"""
        if similarity_score >= 0.95:
            return "critical"
        elif similarity_score >= 0.90:
            return "high"
        elif similarity_score >= 0.85:
            return "medium"
        else:
            return "low"
    
    async def _validate_streaming_permissions(self, user_id: int, mode: StreamingMode) -> bool:
        """Validate user permissions for streaming"""
        try:
            # Check user subscription level, API limits, etc.
            # This would integrate with your user management system
            return True  # Simplified for now
            
        except Exception as e:
            logger.error(f"Permission validation failed for user {user_id}: {str(e)}")
            return False
    
    async def _queue_chunk_processing(self, chunk: StreamChunk, config: StreamingConfig) -> None:
        """Queue chunk for batch processing"""
        try:
            # Add to processing queue for background handling
            queue_data = {
                "chunk_id": chunk.chunk_id,
                "stream_id": f"{config.user_id}_{config.content_type}",
                "priority": config.priority.value,
                "timestamp": chunk.timestamp.isoformat()
            }
            
            await self.redis_client.lpush("chunk_processing_queue", json.dumps(queue_data))
            
        except Exception as e:
            logger.error(f"Failed to queue chunk processing: {str(e)}")
    
    async def _cache_search_results(
        self,
        chunk: StreamChunk,
        results: List[Dict[str, Any]]
    ) -> None:
        """Cache search results for future use"""
        try:
            cache_key = f"search_results:{chunk.chunk_id}"
            cache_data = {
                "chunk_id": chunk.chunk_id,
                "timestamp": chunk.timestamp.isoformat(),
                "results": results
            }
            
            # Cache for 5 minutes
            await self.redis_client.setex(cache_key, 300, json.dumps(cache_data, default=str))
            
        except Exception as e:
            logger.error(f"Failed to cache search results: {str(e)}")
    
    async def _store_alert(self, alert: LiveAlert) -> None:
        """Store alert in database"""
        try:
            async with get_db_session() as session:
                db_alert = ProtectionAlert(
                    alert_id=alert.alert_id,
                    user_id=alert.user_id,
                    content_type=alert.content_type,
                    similarity_score=alert.similarity_score,
                    matched_content_id=alert.matched_content_id,
                    detected_platform=alert.detected_platform,
                    evidence_url=alert.evidence_url,
                    confidence_level=alert.confidence_level,
                    alert_severity=alert.alert_severity,
                    created_at=alert.timestamp
                )
                
                session.add(db_alert)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Failed to store alert: {str(e)}")
    
    async def _update_processing_metrics(self, processing_time: float, alerts_count: int) -> None:
        """Update processing performance metrics"""
        try:
            self.processing_stats["total_chunks_processed"] += 1
            
            # Update average processing time
            total_chunks = self.processing_stats["total_chunks_processed"]
            current_avg = self.processing_stats["average_processing_time"]
            new_avg = ((current_avg * (total_chunks - 1)) + processing_time) / total_chunks
            self.processing_stats["average_processing_time"] = new_avg
            
            # Send metrics to monitoring system
            await self.metrics_collector.record_metric(
                "streaming_processing_time",
                processing_time,
                {"content_type": "mixed", "alerts_generated": alerts_count}
            )
            
        except Exception as e:
            logger.error(f"Failed to update processing metrics: {str(e)}")
    
    async def _check_system_health(self) -> str:
        """Check overall system health"""
        try:
            # Check Redis connection
            redis_healthy = await self.redis_client.ping()
            
            # Check vector store health
            vector_health = await self.vector_manager.get_health_status()
            
            # Check processing performance
            avg_time = self.processing_stats["average_processing_time"]
            performance_healthy = avg_time < 1000  # < 1 second average
            
            if redis_healthy and vector_health and performance_healthy:
                return "healthy"
            elif redis_healthy and vector_health:
                return "degraded"
            else:
                return "unhealthy"
                
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return "unhealthy"
    
    async def _process_stream(self, stream_id: str) -> None:
        """Background stream processing task"""
        try:
            config = self.active_streams[stream_id]
            buffer = self.stream_buffers[stream_id]
            
            while stream_id in self.active_streams:
                try:
                    # Process buffered chunks
                    if buffer:
                        chunk = buffer.pop(0)
                        
                        if config.priority in [StreamingPriority.MEDIUM, StreamingPriority.LOW]:
                            # Process with full quality
                            embedding = await self.embedding_generator.generate_embedding(
                                content_type=config.content_type,
                                data=chunk.data,
                                model_quality="high"
                            )
                            
                            chunk.vector_embedding = embedding
                            
                            # Comprehensive similarity search
                            results = await self.similarity_engine.search_similar_content(
                                content_type=config.content_type,
                                query_vector=embedding,
                                limit=50,
                                threshold=config.similarity_threshold
                            )
                            
                            # Generate alerts if needed
                            alerts = []
                            for result in results:
                                if result.similarity_score >= config.similarity_threshold:
                                    alert = await self._generate_live_alert(chunk, result, config)
                                    if alert:
                                        alerts.append(alert)
                            
                            # Send updates if WebSocket connected
                            if stream_id in self.websocket_connections:
                                await self._send_realtime_update(config.user_id, chunk, alerts)
                    
                    # Wait before next processing cycle
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Stream processing error for {stream_id}: {str(e)}")
                    await asyncio.sleep(1.0)
            
        except Exception as e:
            logger.error(f"Stream processing task failed for {stream_id}: {str(e)}")
        finally:
            # Cleanup on exit
            await self.stop_stream(stream_id)
    
    async def close(self) -> None:
        """Close streaming system and cleanup"""
        try:
            # Stop all active streams
            for stream_id in list(self.active_streams.keys()):
                await self.stop_stream(stream_id)
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            logger.info("Real-time streaming system closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing streaming system: {str(e)}")
