"""
Real-time Converter - Live content transformation for IA Influencer Agent Platform
=================================================================================

Advanced real-time content conversion and streaming transformation system
for live creator workflows and instant content processing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Callable, AsyncIterator
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import websockets

logger = logging.getLogger(__name__)


class StreamType(Enum):
    """Real-time stream types."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"


class ConversionMode(Enum):
    """Real-time conversion modes."""
    LIVE_STREAM = "live_stream"
    BUFFERED = "buffered"
    CHUNK_BASED = "chunk_based"
    FRAME_BY_FRAME = "frame_by_frame"
    LOW_LATENCY = "low_latency"


class QualityPreset(Enum):
    """Quality presets for real-time conversion."""
    ULTRA_LOW_LATENCY = "ultra_low_latency"  # <50ms
    LOW_LATENCY = "low_latency"              # <200ms
    BALANCED = "balanced"                     # <500ms
    HIGH_QUALITY = "high_quality"           # <1000ms
    MAXIMUM_QUALITY = "maximum_quality"     # >1000ms


@dataclass
class StreamConfiguration:
    """Configuration for real-time stream processing."""
    stream_type: StreamType = StreamType.VIDEO
    mode: ConversionMode = ConversionMode.BUFFERED
    quality_preset: QualityPreset = QualityPreset.BALANCED
    
    # Buffer settings
    buffer_size: int = 1024 * 1024  # 1MB
    chunk_size: int = 64 * 1024     # 64KB
    max_buffer_time: float = 2.0    # seconds
    
    # Quality settings
    target_bitrate: Optional[int] = None
    target_resolution: Optional[str] = None
    target_fps: Optional[int] = None
    
    # Performance settings
    max_latency_ms: float = 500.0
    enable_hardware_acceleration: bool = True
    parallel_processing: bool = True
    
    # Format settings
    input_format: Optional[str] = None
    output_format: str = "mp4"
    codec_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Advanced settings
    adaptive_quality: bool = True
    error_correction: bool = True
    packet_loss_tolerance: float = 0.05


@dataclass
class StreamMetrics:
    """Metrics for stream processing."""
    stream_id: str
    start_time: float = field(default_factory=time.time)
    
    # Throughput metrics
    bytes_processed: int = 0
    chunks_processed: int = 0
    frames_processed: int = 0
    
    # Timing metrics
    average_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    
    # Quality metrics
    quality_score: float = 0.0
    error_rate: float = 0.0
    packet_loss_rate: float = 0.0
    
    # Performance metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    gpu_usage: float = 0.0
    
    # Status flags
    is_active: bool = True
    has_errors: bool = False
    
    def update_latency(self, latency_ms: float):
        """Update latency metrics."""
        self.average_latency_ms = (
            (self.average_latency_ms * self.chunks_processed + latency_ms) /
            (self.chunks_processed + 1)
        )
        self.max_latency_ms = max(self.max_latency_ms, latency_ms)
        self.min_latency_ms = min(self.min_latency_ms, latency_ms)


@dataclass
class StreamChunk:
    """Individual chunk of streaming data."""
    id: str
    stream_id: str
    timestamp: float
    data: bytes
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Processing info
    chunk_type: str = "data"  # data, header, metadata
    sequence_number: int = 0
    is_keyframe: bool = False
    
    # Quality info
    quality_level: int = 0
    compression_ratio: float = 0.0
    
    # Status
    processed: bool = False
    error_message: Optional[str] = None


class RealtimeConverter:
    """
    Real-time content converter for the IA Influencer Agent Platform.
    
    Provides low-latency streaming transformation capabilities for live
    content creation and instant processing workflows.
    """
    
    def __init__(
        self,
        config: Optional[StreamConfiguration] = None,
        transformer_registry: Optional[Dict[str, Callable]] = None
    ):
        """
        Initialize real-time converter.
        
        Args:
            config: Stream configuration
            transformer_registry: Available transformers
        """
        self.config = config or StreamConfiguration()
        self.transformer_registry = transformer_registry or {}
        
        # Active streams
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.stream_metrics: Dict[str, StreamMetrics] = {}
        
        # Processing queues
        self.input_queue = asyncio.Queue(maxsize=1000)
        self.output_queue = asyncio.Queue(maxsize=1000)
        self.priority_queue = asyncio.PriorityQueue(maxsize=100)
        
        # Worker pools
        self.thread_executor = ThreadPoolExecutor(max_workers=4)
        
        # Control flags
        self.is_running = False
        self.shutdown_requested = False
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        logger.info("RealtimeConverter initialized")
    
    async def start_stream(
        self,
        stream_id: str,
        source: Union[str, AsyncIterator[bytes]],
        destination: Union[str, Callable],
        config: Optional[StreamConfiguration] = None
    ) -> bool:
        """
        Start a real-time conversion stream.
        
        Args:
            stream_id: Unique stream identifier
            source: Input source (file, URL, or async iterator)
            destination: Output destination (file, URL, or callback)
            config: Stream-specific configuration
            
        Returns:
            Success status
        """



        try:
            if stream_id in self.active_streams:
                raise ValueError(f"Stream already active: {stream_id}")
            
            stream_config = config or self.config
            
            # Initialize stream
            stream_info = {
                "id": stream_id,
                "source": source,
                "destination": destination,
                "config": stream_config,
                "start_time": time.time(),
                "status": "starting"
            }
            
            self.active_streams[stream_id] = stream_info
            self.stream_metrics[stream_id] = StreamMetrics(stream_id=stream_id)
            
            # Start processing pipeline
            await self._start_processing_pipeline(stream_id)
            
            stream_info["status"] = "active"
            logger.info(f"Stream started: {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start stream {stream_id}: {str(e)}")
            return False
    
    async def stop_stream(self, stream_id: str) -> bool:
        """
        Stop a real-time conversion stream.
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            Success status
        """



        try:
            if stream_id not in self.active_streams:
                return False
            
            # Mark for shutdown
            self.active_streams[stream_id]["status"] = "stopping"
            
            # Wait for pipeline to finish
            await asyncio.sleep(0.1)  # Allow current chunks to process
            
            # Clean up
            del self.active_streams[stream_id]
            if stream_id in self.stream_metrics:
                self.stream_metrics[stream_id].is_active = False
            
            logger.info(f"Stream stopped: {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop stream {stream_id}: {str(e)}")
            return False
    
    async def process_chunk(
        self,
        stream_id: str,
        chunk: StreamChunk,
        transformation: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> StreamChunk:
        """
        Process individual chunk with transformation.
        
        Args:
            stream_id: Stream identifier
            chunk: Input chunk
            transformation: Transformation type
            parameters: Transformation parameters
            
        Returns:
            Processed chunk
        """
        start_time = time.time()
        
        try:
            # Get transformer
            transformer = self.transformer_registry.get(transformation)
            if not transformer:
                raise ValueError(f"Unknown transformation: {transformation}")
            
            # Apply transformation
            if asyncio.iscoroutinefunction(transformer):
                result_data = await transformer(
                    data=chunk.data,
                    metadata=chunk.metadata,
                    **(parameters or {})
                )
            else:
                result_data = transformer(
                    data=chunk.data,
                    metadata=chunk.metadata,
                    **(parameters or {})
                )
            
            # Create result chunk
            result_chunk = StreamChunk(
                id=f"{chunk.id}_processed",
                stream_id=stream_id,
                timestamp=time.time(),
                data=result_data if isinstance(result_data, bytes) else chunk.data,
                metadata=chunk.metadata.copy(),
                chunk_type=chunk.chunk_type,
                sequence_number=chunk.sequence_number,
                processed=True
            )
            
            # Update metrics
            latency_ms = (time.time() - start_time) * 1000
            if stream_id in self.stream_metrics:
                self.stream_metrics[stream_id].update_latency(latency_ms)
                self.stream_metrics[stream_id].chunks_processed += 1
            
            return result_chunk
            
        except Exception as e:
            logger.error(f"Chunk processing failed: {str(e)}")
            chunk.error_message = str(e)
            chunk.processed = False
            return chunk
    
    async def create_adaptive_stream(
        self,
        stream_id: str,
        source: Union[str, AsyncIterator[bytes]],
        quality_levels: List[Dict[str, Any]],
        bandwidth_callback: Callable[[], float]
    ) -> bool:
        """
        Create adaptive quality stream that adjusts based on conditions.
        
        Args:
            stream_id: Stream identifier
            source: Input source
            quality_levels: Available quality configurations
            bandwidth_callback: Function to get current bandwidth
            
        Returns:
            Success status
        """



        try:
            # Create adaptive configuration
            adaptive_config = StreamConfiguration(
                mode=ConversionMode.CHUNK_BASED,
                adaptive_quality=True,
                quality_preset=QualityPreset.BALANCED
            )
            
            # Start base stream
            success = await self.start_stream(
                stream_id=stream_id,
                source=source,
                destination=self._adaptive_output_handler,
                config=adaptive_config
            )
            
            if success:
                # Start quality adaptation
                asyncio.create_task(
                    self._adaptive_quality_controller(
                        stream_id, quality_levels, bandwidth_callback
                    )
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to create adaptive stream: {str(e)}")
            return False
    
    async def enable_real_time_effects(
        self,
        stream_id: str,
        effects: List[Dict[str, Any]]
    ) -> bool:
        """
        Enable real-time effects processing on stream.
        
        Args:
            stream_id: Stream identifier
            effects: List of effects to apply
            
        Returns:
            Success status
        """



        try:
            if stream_id not in self.active_streams:
                return False
            
            stream_info = self.active_streams[stream_id]
            stream_info["effects"] = effects
            
            # Create effects pipeline
            pipeline = EffectsPipeline(effects)
            stream_info["effects_pipeline"] = pipeline
            
            logger.info(f"Real-time effects enabled for stream: {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable effects: {str(e)}")
            return False
    
    async def get_stream_status(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get current stream status and metrics."""
        if stream_id not in self.active_streams:
            return None
        
        stream_info = self.active_streams[stream_id]
        metrics = self.stream_metrics.get(stream_id)
        
        return {
            "id": stream_id,
            "status": stream_info["status"],
            "uptime": time.time() - stream_info["start_time"],
            "config": stream_info["config"].__dict__,
            "metrics": metrics.__dict__ if metrics else {},
            "performance": await self.performance_monitor.get_metrics()
        }
    
    async def optimize_for_latency(
        self,
        stream_id: str,
        target_latency_ms: float
    ) -> bool:
        """
        Optimize stream configuration for target latency.
        
        Args:
            stream_id: Stream identifier
            target_latency_ms: Target latency in milliseconds
            
        Returns:
            Success status
        """



        try:
            if stream_id not in self.active_streams:
                return False
            
            stream_info = self.active_streams[stream_id]
            config = stream_info["config"]
            
            # Adjust configuration for latency
            if target_latency_ms < 100:
                config.quality_preset = QualityPreset.ULTRA_LOW_LATENCY
                config.mode = ConversionMode.LOW_LATENCY
                config.buffer_size = 32 * 1024  # 32KB
                config.chunk_size = 8 * 1024   # 8KB
            elif target_latency_ms < 300:
                config.quality_preset = QualityPreset.LOW_LATENCY
                config.mode = ConversionMode.CHUNK_BASED
                config.buffer_size = 64 * 1024  # 64KB
                config.chunk_size = 16 * 1024  # 16KB
            else:
                config.quality_preset = QualityPreset.BALANCED
                config.mode = ConversionMode.BUFFERED
            
            config.max_latency_ms = target_latency_ms
            
            logger.info(f"Stream optimized for {target_latency_ms}ms latency: {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Latency optimization failed: {str(e)}")
            return False
    
    async def _start_processing_pipeline(self, stream_id: str):
        """Start the processing pipeline for a stream."""



        try:
            stream_info = self.active_streams[stream_id]
            config = stream_info["config"]
            
            # Create processing tasks based on mode
            if config.mode == ConversionMode.LIVE_STREAM:
                asyncio.create_task(self._live_stream_processor(stream_id))
            elif config.mode == ConversionMode.BUFFERED:
                asyncio.create_task(self._buffered_processor(stream_id))
            elif config.mode == ConversionMode.CHUNK_BASED:
                asyncio.create_task(self._chunk_processor(stream_id))
            elif config.mode == ConversionMode.FRAME_BY_FRAME:
                asyncio.create_task(self._frame_processor(stream_id))
            elif config.mode == ConversionMode.LOW_LATENCY:
                asyncio.create_task(self._low_latency_processor(stream_id))
            
        except Exception as e:
            logger.error(f"Pipeline start failed: {str(e)}")
    
    async def _live_stream_processor(self, stream_id: str):
        """Process live stream with minimal buffering."""



        try:
            stream_info = self.active_streams[stream_id]
            source = stream_info["source"]
            
            if isinstance(source, str):
                # URL or file source
                async for data in self._read_from_source(source):
                    if stream_info["status"] != "active":
                        break
                    
                    # Create chunk
                    chunk = StreamChunk(
                        id=f"{stream_id}_{int(time.time() * 1000)}",
                        stream_id=stream_id,
                        timestamp=time.time(),
                        data=data
                    )
                    
                    # Process immediately
                    await self.input_queue.put(chunk)
            
        except Exception as e:
            logger.error(f"Live stream processing failed: {str(e)}")
    
    async def _buffered_processor(self, stream_id: str):
        """Process stream with buffering for stability."""



        try:
            stream_info = self.active_streams[stream_id]
            config = stream_info["config"]
            buffer = bytearray()
            
            while stream_info["status"] == "active":
                # Fill buffer
                data = await self._read_chunk_from_source(stream_info["source"])
                if not data:
                    break
                
                buffer.extend(data)
                
                # Process when buffer is full
                if len(buffer) >= config.buffer_size:
                    chunk_data = bytes(buffer[:config.chunk_size])
                    buffer = buffer[config.chunk_size:]
                    
                    chunk = StreamChunk(
                        id=f"{stream_id}_{int(time.time() * 1000)}",
                        stream_id=stream_id,
                        timestamp=time.time(),
                        data=chunk_data
                    )
                    
                    await self.input_queue.put(chunk)
            
        except Exception as e:
            logger.error(f"Buffered processing failed: {str(e)}")
    
    async def _chunk_processor(self, stream_id: str):
        """Process stream in fixed-size chunks."""



        try:
            stream_info = self.active_streams[stream_id]
            config = stream_info["config"]
            sequence = 0
            
            while stream_info["status"] == "active":
                # Read chunk
                data = await self._read_chunk_from_source(
                    stream_info["source"], 
                    config.chunk_size
                )
                
                if not data:
                    break
                
                chunk = StreamChunk(
                    id=f"{stream_id}_chunk_{sequence}",
                    stream_id=stream_id,
                    timestamp=time.time(),
                    data=data,
                    sequence_number=sequence
                )
                
                await self.input_queue.put(chunk)
                sequence += 1
            
        except Exception as e:
            logger.error(f"Chunk processing failed: {str(e)}")
    
    async def _frame_processor(self, stream_id: str):
        """Process stream frame by frame."""



        try:
            stream_info = self.active_streams[stream_id]
            frame_count = 0
            
            # This would integrate with video processing libraries
            # For now, simulate frame processing
            while stream_info["status"] == "active":
                await asyncio.sleep(1/30)  # 30 FPS simulation
                
                # Simulate frame data
                frame_data = b"frame_data_" + str(frame_count).encode()
                
                chunk = StreamChunk(
                    id=f"{stream_id}_frame_{frame_count}",
                    stream_id=stream_id,
                    timestamp=time.time(),
                    data=frame_data,
                    chunk_type="frame",
                    sequence_number=frame_count,
                    is_keyframe=(frame_count % 30 == 0)
                )
                
                await self.input_queue.put(chunk)
                frame_count += 1
            
        except Exception as e:
            logger.error(f"Frame processing failed: {str(e)}")
    
    async def _low_latency_processor(self, stream_id: str):
        """Process stream with ultra-low latency optimizations."""



        try:
            stream_info = self.active_streams[stream_id]
            config = stream_info["config"]
            
            # Use smaller chunks and immediate processing
            config.chunk_size = min(config.chunk_size, 4096)  # 4KB max
            
            while stream_info["status"] == "active":
                data = await self._read_chunk_from_source(
                    stream_info["source"],
                    config.chunk_size
                )
                
                if not data:
                    break
                
                # Process immediately without queuing
                chunk = StreamChunk(
                    id=f"{stream_id}_{int(time.time() * 1000000)}",  # microsecond precision
                    stream_id=stream_id,
                    timestamp=time.time(),
                    data=data
                )
                
                # Direct processing for minimal latency
                await self._process_chunk_direct(chunk)
            
        except Exception as e:
            logger.error(f"Low latency processing failed: {str(e)}")
    
    async def _adaptive_quality_controller(
        self,
        stream_id: str,
        quality_levels: List[Dict[str, Any]],
        bandwidth_callback: Callable[[], float]
    ):
        """Control adaptive quality based on conditions."""



        try:
            current_quality_index = len(quality_levels) // 2  # Start with medium quality
            
            while stream_id in self.active_streams:
                # Get current conditions
                bandwidth = bandwidth_callback()
                metrics = self.stream_metrics.get(stream_id)
                
                if metrics:
                    # Adjust quality based on latency and bandwidth
                    if metrics.average_latency_ms > 1000 or bandwidth < 1000000:  # 1Mbps
                        # Reduce quality
                        current_quality_index = max(0, current_quality_index - 1)
                    elif metrics.average_latency_ms < 200 and bandwidth > 5000000:  # 5Mbps
                        # Increase quality
                        current_quality_index = min(len(quality_levels) - 1, current_quality_index + 1)
                    
                    # Apply quality settings
                    quality_config = quality_levels[current_quality_index]
                    await self._apply_quality_settings(stream_id, quality_config)
                
                await asyncio.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            logger.error(f"Adaptive quality control failed: {str(e)}")
    
    async def _adaptive_output_handler(self, chunk: StreamChunk):
        """Handle output for adaptive streams."""
        # This would route output based on current quality level
        pass
    
    async def _read_from_source(self, source: str) -> AsyncIterator[bytes]:
        """Read data from source asynchronously."""
        # This would implement actual source reading
        # For simulation, yield dummy data
        for i in range(100):
            yield f"data_chunk_{i}".encode()
            await asyncio.sleep(0.01)
    
    async def _read_chunk_from_source(self, source: Any, size: int = 1024) -> bytes:
        """Read specific chunk size from source."""
        # Simulate reading from source
        await asyncio.sleep(0.01)
        return f"chunk_data_{int(time.time() * 1000)}".encode()[:size]
    
    async def _process_chunk_direct(self, chunk: StreamChunk):
        """Process chunk directly without queuing."""
        # Direct processing for ultra-low latency
        chunk.processed = True
        chunk.timestamp = time.time()
    
    async def _apply_quality_settings(self, stream_id: str, quality_config: Dict[str, Any]):
        """Apply quality settings to stream."""
        if stream_id in self.active_streams:
            config = self.active_streams[stream_id]["config"]
            
            for key, value in quality_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)


class EffectsPipeline:
    """Real-time effects processing pipeline."""
    
    def __init__(self, effects: List[Dict[str, Any]]):
        self.effects = effects
        self.enabled = True
    
    async def apply_effects(self, chunk: StreamChunk) -> StreamChunk:
        """Apply effects to chunk."""
        if not self.enabled:
            return chunk
        
        processed_chunk = chunk
        
        for effect in self.effects:
            effect_type = effect.get("type")
            parameters = effect.get("parameters", {})
            
            # Apply effect based on type
            if effect_type == "blur":
                processed_chunk = await self._apply_blur(processed_chunk, parameters)
            elif effect_type == "filter":
                processed_chunk = await self._apply_filter(processed_chunk, parameters)
            # Add more effects as needed
        
        return processed_chunk
    
    async def _apply_blur(self, chunk: StreamChunk, params: Dict[str, Any]) -> StreamChunk:
        """Apply blur effect."""
        # Simulate blur processing
        chunk.metadata["effects_applied"] = chunk.metadata.get("effects_applied", [])
        chunk.metadata["effects_applied"].append("blur")
        return chunk
    
    async def _apply_filter(self, chunk: StreamChunk, params: Dict[str, Any]) -> StreamChunk:
        """Apply filter effect."""
        # Simulate filter processing
        chunk.metadata["effects_applied"] = chunk.metadata.get("effects_applied", [])
        chunk.metadata["effects_applied"].append("filter")
        return chunk


class PerformanceMonitor:
    """Performance monitoring for real-time processing."""
    
    def __init__(self):
        self.metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "gpu_usage": 0.0,
            "network_io": 0.0,
            "disk_io": 0.0
        }
    
    async def get_metrics(self) -> Dict[str, float]:
        """Get current performance metrics."""



        try:
            import psutil
            
            self.metrics["cpu_usage"] = psutil.cpu_percent()
            self.metrics["memory_usage"] = psutil.virtual_memory().percent
            
            # Network I/O
            net_io = psutil.net_io_counters()
            self.metrics["network_io"] = net_io.bytes_sent + net_io.bytes_recv
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.metrics["disk_io"] = disk_io.read_bytes + disk_io.write_bytes
            
        except ImportError:
            pass
        
        return self.metrics.copy()


class StreamingWebSocketHandler:
    """WebSocket handler for real-time streaming."""
    
    def __init__(self, converter: RealtimeConverter):
        self.converter = converter
        self.active_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
    
    async def handle_connection(self, websocket, path):
        """Handle WebSocket connection."""



        try:
            connection_id = f"ws_{int(time.time() * 1000)}"
            self.active_connections[connection_id] = websocket
            
            async for message in websocket:
                await self._process_websocket_message(connection_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
    
    async def _process_websocket_message(self, connection_id: str, message: str):
        """Process incoming WebSocket message."""



        try:
            data = json.loads(message)
            command = data.get("command")
            
            if command == "start_stream":
                # Start real-time stream
                stream_id = data.get("stream_id")
                await self.converter.start_stream(
                    stream_id=stream_id,
                    source=self._websocket_source_generator(connection_id),
                    destination=self._websocket_output_handler(connection_id)
                )
            
            elif command == "stop_stream":
                stream_id = data.get("stream_id")
                await self.converter.stop_stream(stream_id)
                
        except Exception as e:
            logger.error(f"WebSocket message processing failed: {str(e)}")
    
    async def _websocket_source_generator(self, connection_id: str) -> AsyncIterator[bytes]:
        """Generate data from WebSocket connection."""
        websocket = self.active_connections.get(connection_id)
        if not websocket:
            return
        
        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    yield message
                elif isinstance(message, str):
                    yield message.encode()
        except websockets.exceptions.ConnectionClosed:
            pass
    
    async def _websocket_output_handler(self, connection_id: str):
        """Handle output to WebSocket connection."""
        def send_to_websocket(chunk: StreamChunk):
            websocket = self.active_connections.get(connection_id)
            if websocket:
                asyncio.create_task(websocket.send(chunk.data))
        
        return send_to_websocket
