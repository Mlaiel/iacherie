"""Stream Processor - Real-time streaming and processing for IA Influencer Agent Platform
=======================================================================================

Advanced real-time streaming engine providing low-latency processing, adaptive streaming,
and intelligent buffering for creator workflows and live content delivery.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import queue
import threading
from collections import deque
import statistics
import hashlib

logger = logging.getLogger(__name__)


class StreamType(Enum):
    """Types of supported streams."""
    
    AUDIO = "audio"
    VIDEO = "video"
    DATA = "data"
    MIXED = "mixed"


class StreamingProtocol(Enum):
    """Supported streaming protocols."""
    
    RTMP = "rtmp"
    HLS = "hls"
    DASH = "dash"
    WEBRTC = "webrtc"
    SRT = "srt"
    RTSP = "rtsp"
    UDP = "udp"
    TCP = "tcp"


class StreamQuality(Enum):
    """Stream quality levels."""
    
    AUTO = "auto"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"
    ADAPTIVE = "adaptive"


class StreamState(Enum):
    """Stream processing states."""
    
    INITIALIZING = "initializing"
    BUFFERING = "buffering"
    STREAMING = "streaming"
    PAUSED = "paused"
    RECONNECTING = "reconnecting"
    STOPPED = "stopped"
    ERROR = "error"


class BufferingStrategy(Enum):
    """Buffering strategies for stream processing."""
    
    MINIMAL = "minimal"        # Lowest latency, higher risk
    BALANCED = "balanced"      # Balance latency and stability
    STABLE = "stable"          # Prioritize stability
    ADAPTIVE = "adaptive"      # Dynamically adjust


@dataclass
class StreamMetrics:
    """Real-time stream metrics."""
    
    bitrate_current: float = 0.0
    bitrate_average: float = 0.0
    latency_ms: float = 0.0
    jitter_ms: float = 0.0
    packet_loss: float = 0.0
    fps_current: float = 0.0
    fps_target: float = 0.0
    buffer_health: float = 0.0  # 0-100%
    quality_score: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class StreamChunk:
    """Stream data chunk."""
    
    chunk_id: str
    data: bytes
    timestamp: float
    sequence_number: int
    chunk_type: StreamType
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    quality_level: Optional[StreamQuality] = None
    checksum: Optional[str] = None


@dataclass
class StreamConfiguration:
    """Configuration for stream processing."""
    
    stream_id: str
    stream_type: StreamType
    protocol: StreamingProtocol = StreamingProtocol.RTMP
    quality: StreamQuality = StreamQuality.AUTO
    target_bitrate: Optional[int] = None
    max_bitrate: Optional[int] = None
    min_bitrate: Optional[int] = None
    buffer_size_ms: int = 3000  # 3 seconds default
    chunk_size_ms: int = 100    # 100ms chunks
    max_latency_ms: int = 500   # Maximum acceptable latency
    adaptive_streaming: bool = True
    error_recovery: bool = True
    buffering_strategy: BufferingStrategy = BufferingStrategy.BALANCED
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamSession:
    """Active stream session data."""
    
    session_id: str
    config: StreamConfiguration
    state: StreamState = StreamState.INITIALIZING
    start_time: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    metrics: StreamMetrics = field(default_factory=StreamMetrics)
    buffer: deque = field(default_factory=deque)
    error_count: int = 0
    reconnect_count: int = 0
    total_chunks_processed: int = 0
    total_data_processed: int = 0


class StreamProcessor:
    """Real-time stream processing engine."""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize stream processor with configuration."""
        self.config = config or {}
        self.max_concurrent_streams = self.config.get("max_concurrent_streams", 50)
        self.default_buffer_size = self.config.get("default_buffer_size_ms", 3000)
        
        # Stream management
        self.active_streams = {}
        self.stream_processors = {}
        self.stream_lock = threading.Lock()
        
        # Performance monitoring
        self.global_metrics = {
            "active_streams": 0,
            "total_streams_processed": 0,
            "average_latency": 0.0,
            "total_data_processed": 0,
            "error_rate": 0.0
        }
        
        # Background tasks
        self.monitoring_task = None
        self.cleanup_task = None
        self.running = False
        
        logger.info("StreamProcessor initialized")
    
    async def start(self) -> None:
        """Start the stream processor."""
        if self.running:
            logger.warning("StreamProcessor already running")
            return
        
        self.running = True
        
        # Start background tasks
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("StreamProcessor started")
    
    async def stop(self) -> None:
        """Stop the stream processor."""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel background tasks
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        # Stop all active streams
        stream_ids = list(self.active_streams.keys())
        for stream_id in stream_ids:
            await self.stop_stream(stream_id)
        
        logger.info("StreamProcessor stopped")
    
    async def create_stream(self, config: StreamConfiguration) -> bool:
        """
        Create a new stream session.
        
        Args:
            config: Stream configuration
            
        Returns:
            True if stream was created successfully
        """
        try:
            if len(self.active_streams) >= self.max_concurrent_streams:
                logger.warning(f"Maximum streams ({self.max_concurrent_streams}) reached")
                return False
            
            # Validate configuration
            if not await self._validate_stream_config(config):
                return False
            
            # Create stream session
            session = StreamSession(
                session_id=f"{config.stream_id}_{int(time.time() * 1000)}",
                config=config
            )
            
            # Initialize stream processor
            processor = StreamChunkProcessor(config, session)
            
            with self.stream_lock:
                self.active_streams[config.stream_id] = session
                self.stream_processors[config.stream_id] = processor
                self.global_metrics["active_streams"] = len(self.active_streams)
            
            # Start stream processing
            asyncio.create_task(self._process_stream(config.stream_id))
            
            logger.info(f"Stream {config.stream_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create stream {config.stream_id}: {str(e)}")
            return False
    
    async def process_chunk(self, stream_id: str, chunk: StreamChunk) -> bool:
        """
        Process a chunk of stream data.
        
        Args:
            stream_id: Stream identifier
            chunk: Data chunk to process
            
        Returns:
            True if chunk was processed successfully
        """
        try:
            with self.stream_lock:
                if stream_id not in self.active_streams:
                    logger.warning(f"Stream {stream_id} not found")
                    return False
                
                session = self.active_streams[stream_id]
                processor = self.stream_processors[stream_id]
            
            # Validate chunk
            if not await self._validate_chunk(chunk):
                return False
            
            # Process chunk
            success = await processor.process_chunk(chunk)
            
            if success:
                # Update session metrics
                session.last_activity = time.time()
                session.total_chunks_processed += 1
                session.total_data_processed += len(chunk.data)
                
                # Update global metrics
                self.global_metrics["total_data_processed"] += len(chunk.data)
            
            return success
            
        except Exception as e:
            logger.error(f"Chunk processing failed for stream {stream_id}: {str(e)}")
            await self._handle_stream_error(stream_id, str(e))
            return False
    
    async def stop_stream(self, stream_id: str) -> Dict[str, Any]:
        """
        Stop a stream session.
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            Stream session statistics
        """
        try:
            with self.stream_lock:
                if stream_id not in self.active_streams:
                    return {"error": "Stream not found"}
                
                session = self.active_streams[stream_id]
                processor = self.stream_processors[stream_id]
                
                # Calculate session statistics
                duration = time.time() - session.start_time
                avg_bitrate = (session.total_data_processed * 8) / duration if duration > 0 else 0
                
                stats = {
                    "stream_id": stream_id,
                    "duration": duration,
                    "chunks_processed": session.total_chunks_processed,
                    "data_processed": session.total_data_processed,
                    "average_bitrate": avg_bitrate,
                    "error_count": session.error_count,
                    "reconnect_count": session.reconnect_count,
                    "final_metrics": session.metrics
                }
                
                # Cleanup
                del self.active_streams[stream_id]
                del self.stream_processors[stream_id]
                self.global_metrics["active_streams"] = len(self.active_streams)
            
            # Stop processor
            await processor.stop()
            
            logger.info(f"Stream {stream_id} stopped")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to stop stream {stream_id}: {str(e)}")
            return {"error": str(e)}
    
    async def get_stream_status(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a stream."""
        with self.stream_lock:
            if stream_id not in self.active_streams:
                return None
            
            session = self.active_streams[stream_id]
            
            return {
                "stream_id": stream_id,
                "state": session.state.value,
                "uptime": time.time() - session.start_time,
                "chunks_processed": session.total_chunks_processed,
                "data_processed": session.total_data_processed,
                "error_count": session.error_count,
                "metrics": {
                    "bitrate": session.metrics.bitrate_current,
                    "latency": session.metrics.latency_ms,
                    "buffer_health": session.metrics.buffer_health,
                    "quality_score": session.metrics.quality_score
                }
            }
    
    async def get_all_streams_status(self) -> List[Dict[str, Any]]:
        """Get status of all active streams."""
        statuses = []
        
        with self.stream_lock:
            for stream_id in self.active_streams.keys():
                status = await self.get_stream_status(stream_id)
                if status:
                    statuses.append(status)
        
        return statuses
    
    async def adjust_stream_quality(self, stream_id: str, quality: StreamQuality) -> bool:
        """Adjust stream quality dynamically."""
        try:
            with self.stream_lock:
                if stream_id not in self.active_streams:
                    return False
                
                session = self.active_streams[stream_id]
                processor = self.stream_processors[stream_id]
            
            # Update configuration
            session.config.quality = quality
            
            # Apply quality adjustment
            await processor.adjust_quality(quality)
            
            logger.info(f"Stream {stream_id} quality adjusted to {quality.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to adjust quality for stream {stream_id}: {str(e)}")
            return False
    
    async def _validate_stream_config(self, config: StreamConfiguration) -> bool:
        """Validate stream configuration."""
        if not config.stream_id:
            logger.error("Stream ID is required")
            return False
        
        if config.stream_id in self.active_streams:
            logger.error(f"Stream {config.stream_id} already exists")
            return False
        
        if config.buffer_size_ms <= 0:
            logger.error("Buffer size must be positive")
            return False
        
        if config.chunk_size_ms <= 0:
            logger.error("Chunk size must be positive")
            return False
        
        return True
    
    async def _validate_chunk(self, chunk: StreamChunk) -> bool:
        """Validate stream chunk."""
        if not chunk.chunk_id:
            return False
        
        if not chunk.data:
            return False
        
        if chunk.timestamp <= 0:
            return False
        
        # Validate checksum if provided
        if chunk.checksum:
            calculated_checksum = hashlib.md5(chunk.data).hexdigest()
            if calculated_checksum != chunk.checksum:
                logger.warning(f"Checksum mismatch for chunk {chunk.chunk_id}")
                return False
        
        return True
    
    async def _process_stream(self, stream_id -> None: str) -> None:
        """Main stream processing loop."""
        try:
            with self.stream_lock:
                session = self.active_streams.get(stream_id)
                processor = self.stream_processors.get(stream_id)
            
            if not session or not processor:
                return
            
            session.state = StreamState.STREAMING
            
            # Main processing loop
            while self.running and stream_id in self.active_streams:
                # Update metrics
                await self._update_stream_metrics(stream_id)
                
                # Check for errors and handle recovery
                await self._check_stream_health(stream_id)
                
                # Adaptive quality adjustment
                if session.config.adaptive_streaming:
                    await self._adaptive_quality_control(stream_id)
                
                await asyncio.sleep(0.1)  # 100ms monitoring interval
            
        except Exception as e:
            logger.error(f"Stream processing error for {stream_id}: {str(e)}")
            await self._handle_stream_error(stream_id, str(e))
    
    async def _update_stream_metrics(self, stream_id -> None: str) -> None:
        """Update stream metrics."""
        try:
            with self.stream_lock:
                session = self.active_streams.get(stream_id)
                processor = self.stream_processors.get(stream_id)
            
            if not session or not processor:
                return
            
            # Get current metrics from processor
            current_metrics = await processor.get_metrics()
            session.metrics = current_metrics
            
        except Exception as e:
            logger.error(f"Failed to update metrics for stream {stream_id}: {str(e)}")
    
    async def _check_stream_health(self, stream_id -> None: str) -> None:
        """Check stream health and handle issues."""
        try:
            with self.stream_lock:
                session = self.active_streams.get(stream_id)
            
            if not session:
                return
            
            # Check for timeout
            time_since_activity = time.time() - session.last_activity
            if time_since_activity > 30.0:  # 30 seconds timeout
                logger.warning(f"Stream {stream_id} inactive for {time_since_activity:.1f}s")
                await self._handle_stream_timeout(stream_id)
                return
            
            # Check latency
            if session.metrics.latency_ms > session.config.max_latency_ms:
                logger.warning(f"High latency detected for stream {stream_id}: {session.metrics.latency_ms}ms")
                await self._handle_high_latency(stream_id)
            
            # Check buffer health
            if session.metrics.buffer_health < 20.0:  # Less than 20% buffer
                logger.warning(f"Low buffer health for stream {stream_id}: {session.metrics.buffer_health}%")
                await self._handle_low_buffer(stream_id)
            
        except Exception as e:
            logger.error(f"Health check failed for stream {stream_id}: {str(e)}")
    
    async def _adaptive_quality_control(self, stream_id -> None: str) -> None:
        """Adaptive quality control based on stream conditions."""
        try:
            with self.stream_lock:
                session = self.active_streams.get(stream_id)
                processor = self.stream_processors.get(stream_id)
            
            if not session or not processor:
                return
            
            if session.config.quality != StreamQuality.ADAPTIVE:
                return
            
            # Determine optimal quality based on conditions
            current_quality = await processor.get_current_quality()
            optimal_quality = await self._calculate_optimal_quality(session)
            
            if optimal_quality != current_quality:
                await processor.adjust_quality(optimal_quality)
                logger.info(f"Stream {stream_id} quality auto-adjusted to {optimal_quality.value}")
            
        except Exception as e:
            logger.error(f"Adaptive quality control failed for stream {stream_id}: {str(e)}")
    
    async def _calculate_optimal_quality(self, session: StreamSession) -> StreamQuality:
        """Calculate optimal quality based on stream conditions."""
        metrics = session.metrics
        
        # Quality decision based on multiple factors
        quality_score = 0
        
        # Latency factor (lower latency = higher score)
        if metrics.latency_ms < 100:
            quality_score += 3
        elif metrics.latency_ms < 200:
            quality_score += 2
        elif metrics.latency_ms < 500:
            quality_score += 1
        
        # Buffer health factor
        if metrics.buffer_health > 80:
            quality_score += 2
        elif metrics.buffer_health > 50:
            quality_score += 1
        
        # Packet loss factor
        if metrics.packet_loss < 0.01:  # Less than 1%
            quality_score += 2
        elif metrics.packet_loss < 0.05:  # Less than 5%
            quality_score += 1
        
        # Map score to quality level
        if quality_score >= 6:
            return StreamQuality.ULTRA
        elif quality_score >= 4:
            return StreamQuality.HIGH
        elif quality_score >= 2:
            return StreamQuality.MEDIUM
        else:
            return StreamQuality.LOW
    
    async def _handle_stream_error(self, stream_id -> None: str, error_message -> None: str) -> None:
        """Handle stream errors."""
        try:
            with self.stream_lock:
                session = self.active_streams.get(stream_id)
            
            if not session:
                return
            
            session.error_count += 1
            session.state = StreamState.ERROR
            
            logger.error(f"Stream {stream_id} error: {error_message}")
            
            # Attempt recovery if enabled
            if session.config.error_recovery and session.error_count < 5:
                await self._attempt_stream_recovery(stream_id)
            else:
                logger.error(f"Stream {stream_id} exceeded error threshold, stopping")
                await self.stop_stream(stream_id)
            
        except Exception as e:
            logger.error(f"Error handling failed for stream {stream_id}: {str(e)}")
    
    async def _attempt_stream_recovery(self, stream_id -> None: str) -> None:
        """Attempt to recover a failed stream."""
        try:
            with self.stream_lock:
                session = self.active_streams.get(stream_id)
            
            if not session:
                return
            
            session.reconnect_count += 1
            session.state = StreamState.RECONNECTING
            
            logger.info(f"Attempting recovery for stream {stream_id} (attempt {session.reconnect_count})")
            
            # Simulated recovery process
            await asyncio.sleep(1.0)
            
            session.state = StreamState.STREAMING
            logger.info(f"Stream {stream_id} recovery successful")
            
        except Exception as e:
            logger.error(f"Recovery failed for stream {stream_id}: {str(e)}")
            session.state = StreamState.ERROR
    
    async def _handle_stream_timeout(self, stream_id -> None: str) -> None:
        """Handle stream timeout."""
        logger.warning(f"Stream {stream_id} timed out")
        await self._handle_stream_error(stream_id, "Stream timeout")
    
    async def _handle_high_latency(self, stream_id -> None: str) -> None:
        """Handle high latency situation."""
        # Reduce quality to improve latency
        await self.adjust_stream_quality(stream_id, StreamQuality.LOW)
    
    async def _handle_low_buffer(self, stream_id -> None: str) -> None:
        """Handle low buffer situation."""
        with self.stream_lock:
            session = self.active_streams.get(stream_id)
        
        if session:
            session.state = StreamState.BUFFERING
            # Would implement buffer recovery logic here
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while self.running:
            try:
                # Update global metrics
                await self._update_global_metrics()
                
                # Cleanup inactive sessions
                await self._cleanup_inactive_sessions()
                
                await asyncio.sleep(5.0)  # 5 second monitoring interval
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {str(e)}")
                await asyncio.sleep(1.0)
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self.running:
            try:
                # Cleanup old stream data
                await self._cleanup_old_data()
                
                await asyncio.sleep(60.0)  # 1 minute cleanup interval
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {str(e)}")
                await asyncio.sleep(10.0)
    
    async def _update_global_metrics(self) -> None:
        """Update global performance metrics."""
        try:
            with self.stream_lock:
                active_count = len(self.active_streams)
                
                if active_count > 0:
                    # Calculate average latency
                    total_latency = sum(
                        session.metrics.latency_ms for session in self.active_streams.values()
                    )
                    avg_latency = total_latency / active_count
                    
                    # Calculate error rate
                    total_errors = sum(
                        session.error_count for session in self.active_streams.values()
                    )
                    total_chunks = sum(
                        session.total_chunks_processed for session in self.active_streams.values()
                    )
                    error_rate = total_errors / max(total_chunks, 1)
                    
                    self.global_metrics.update({
                        "active_streams": active_count,
                        "average_latency": avg_latency,
                        "error_rate": error_rate
                    })
                else:
                    self.global_metrics["active_streams"] = 0
            
        except Exception as e:
            logger.error(f"Failed to update global metrics: {str(e)}")
    
    async def _cleanup_inactive_sessions(self) -> None:
        """Cleanup inactive sessions."""
        current_time = time.time()
        inactive_streams = []
        
        with self.stream_lock:
            for stream_id, session in self.active_streams.items():
                # Mark streams inactive for more than 5 minutes
                if current_time - session.last_activity > 300:
                    inactive_streams.append(stream_id)
        
        # Stop inactive streams
        for stream_id in inactive_streams:
            logger.info(f"Cleaning up inactive stream: {stream_id}")
            await self.stop_stream(stream_id)
    
    async def _cleanup_old_data(self) -> None:
        """Cleanup old data and free memory."""
        # Would implement memory cleanup logic here
        pass
    
    def get_global_metrics(self) -> Dict[str, Any]:
        """Get global stream processing metrics."""
        return self.global_metrics.copy()


class StreamChunkProcessor:
    """Processor for individual stream chunks."""
    
    def __init__(self, config -> None: StreamConfiguration, session -> None: StreamSession) -> None:
        """Initialize chunk processor."""
        self.config = config
        self.session = session
        self.current_quality = config.quality
        self.buffer = deque(maxlen=100)  # Circular buffer for chunks
        self.metrics_history = deque(maxlen=60)  # 1 minute of metrics at 1Hz
        
        logger.debug(f"StreamChunkProcessor initialized for {config.stream_id}")
    
    async def process_chunk(self, chunk: StreamChunk) -> bool:
        """Process a single chunk."""
        try:
            start_time = time.time()
            
            # Add to buffer
            self.buffer.append(chunk)
            
            # Update chunk metadata
            chunk.processing_time = time.time() - start_time
            chunk.quality_level = self.current_quality
            
            # Update session buffer
            self.session.buffer.append(chunk)
            
            # Maintain buffer size
            max_buffer_chunks = self.config.buffer_size_ms // self.config.chunk_size_ms
            while len(self.session.buffer) > max_buffer_chunks:
                self.session.buffer.popleft()
            
            # Update metrics
            await self._update_chunk_metrics(chunk)
            
            return True
            
        except Exception as e:
            logger.error(f"Chunk processing failed: {str(e)}")
            return False
    
    async def adjust_quality(self, quality -> None: StreamQuality) -> None:
        """Adjust processing quality."""
        self.current_quality = quality
        logger.debug(f"Quality adjusted to {quality.value}")
    
    async def get_current_quality(self) -> StreamQuality:
        """Get current quality setting."""
        return self.current_quality
    
    async def get_metrics(self) -> StreamMetrics:
        """Get current processing metrics."""
        try:
            # Calculate current metrics
            current_time = time.time()
            
            # Calculate bitrate from recent chunks
            recent_chunks = [
                chunk for chunk in self.buffer
                if current_time - chunk.timestamp < 5.0  # Last 5 seconds
            ]
            
            if recent_chunks:
                total_data = sum(len(chunk.data) for chunk in recent_chunks)
                time_span = max(0.1, current_time - min(chunk.timestamp for chunk in recent_chunks))
                current_bitrate = (total_data * 8) / time_span  # bits per second
            else:
                current_bitrate = 0.0
            
            # Calculate buffer health
            buffer_target = self.config.buffer_size_ms // self.config.chunk_size_ms
            buffer_current = len(self.session.buffer)
            buffer_health = min(100.0, (buffer_current / buffer_target) * 100) if buffer_target > 0 else 0.0
            
            # Calculate latency (simplified)
            if recent_chunks:
                latest_chunk = max(recent_chunks, key=lambda c: c.timestamp)
                latency = (current_time - latest_chunk.timestamp) * 1000  # Convert to milliseconds
            else:
                latency = 0.0
            
            # Quality score based on various factors
            quality_score = self._calculate_quality_score(current_bitrate, latency, buffer_health)
            
            metrics = StreamMetrics(
                bitrate_current=current_bitrate,
                bitrate_average=self._calculate_average_bitrate(),
                latency_ms=latency,
                jitter_ms=self._calculate_jitter(),
                packet_loss=self._calculate_packet_loss(),
                fps_current=self._calculate_current_fps(),
                fps_target=30.0,  # Default target
                buffer_health=buffer_health,
                quality_score=quality_score,
                timestamp=current_time
            )
            
            # Store metrics history
            self.metrics_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {str(e)}")
            return StreamMetrics()
    
    async def _update_chunk_metrics(self, chunk -> None: StreamChunk) -> None:
        """Update metrics based on processed chunk."""
        # Would update detailed chunk-level metrics here
        pass
    
    def _calculate_average_bitrate(self) -> float:
        """Calculate average bitrate from metrics history."""
        if not self.metrics_history:
            return 0.0
        
        return statistics.mean(m.bitrate_current for m in self.metrics_history)
    
    def _calculate_jitter(self) -> float:
        """Calculate jitter from recent chunks."""
        if len(self.buffer) < 2:
            return 0.0
        
        # Calculate timestamp differences
        timestamps = [chunk.timestamp for chunk in self.buffer]
        timestamps.sort()
        
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        
        if len(intervals) < 2:
            return 0.0
        
        # Jitter is the standard deviation of intervals
        return statistics.stdev(intervals) * 1000  # Convert to milliseconds
    
    def _calculate_packet_loss(self) -> float:
        """Calculate packet loss percentage."""
        if len(self.buffer) < 2:
            return 0.0
        
        # Simplified packet loss calculation based on sequence numbers
        sequences = [chunk.sequence_number for chunk in self.buffer if chunk.sequence_number >= 0]
        sequences.sort()
        
        if len(sequences) < 2:
            return 0.0
        
        expected_count = sequences[-1] - sequences[0] + 1
        actual_count = len(sequences)
        
        if expected_count <= actual_count:
            return 0.0
        
        return ((expected_count - actual_count) / expected_count) * 100
    
    def _calculate_current_fps(self) -> float:
        """Calculate current frames per second."""
        if not self.buffer:
            return 0.0
        
        # Count chunks in the last second
        current_time = time.time()
        recent_chunks = [
            chunk for chunk in self.buffer
            if current_time - chunk.timestamp < 1.0
        ]
        
        return len(recent_chunks)
    
    def _calculate_quality_score(self, bitrate: float, latency: float, buffer_health: float) -> float:
        """Calculate overall quality score."""
        # Normalize factors to 0-1 scale
        bitrate_score = min(1.0, bitrate / 5000000)  # Normalize to 5 Mbps
        latency_score = max(0.0, 1.0 - (latency / 1000))  # Normalize to 1 second
        buffer_score = buffer_health / 100.0
        
        # Weighted average
        quality_score = (bitrate_score * 0.4 + latency_score * 0.4 + buffer_score * 0.2)
        
        return quality_score
    
    async def stop(self) -> None:
        """Stop chunk processor."""
        self.buffer.clear()
        self.metrics_history.clear()
        logger.debug("StreamChunkProcessor stopped")


# Export all classes for module imports
__all__ = [
    "StreamProcessor",
    "StreamChunkProcessor",
    "StreamType",
    "StreamingProtocol",
    "StreamQuality",
    "StreamState",
    "BufferingStrategy",
    "StreamMetrics",
    "StreamChunk",
    "StreamConfiguration",
    "StreamSession"
]

logger.info("Stream processor module loaded successfully")