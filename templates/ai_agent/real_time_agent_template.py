"""{{agent_name}} Real-time Agent Template for Ainflue Platform
{{agent_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
ML Engineer + Lead Dev IA Role: Real-time AI processing with streaming capabilities
"""

import logging
import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Union, Callable, AsyncIterator, Tuple
from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, asdict
import weakref
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue, Empty
import numpy as np

from fastapi import WebSocket, WebSocketDisconnect
import websockets
import redis.asyncio as redis
from pydantic import BaseModel, Field

from core.config import get_settings
from utils.exceptions import AgentError
from utils.metrics import MetricsCollector
from ai_models.base_agent import BaseAgent

logger = logging.getLogger(__name__)
settings = get_settings()


class RealTimeError(AgentError):
    """Real-time agent specific error"""
    pass


class StreamingMode(str, Enum):
    """Streaming processing modes"""
    CONTINUOUS = "continuous"
    BATCH = "batch"
    WINDOW = "window"
    EVENT_DRIVEN = "event_driven"


class ProcessingPriority(str, Enum):
    """Processing priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class DataFormat(str, Enum):
    """Supported data formats"""
    JSON = "json"
    BINARY = "binary"
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"


@dataclass
class StreamingConfig:
    """Configuration for streaming processing"""
    mode: StreamingMode = StreamingMode.CONTINUOUS
    batch_size: int = 100
    window_size: int = 1000
    window_overlap: float = 0.1
    max_latency_ms: int = 100
    buffer_size: int = 10000
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    auto_scale: bool = True
    max_workers: int = 4


@dataclass
class StreamingMetrics:
    """Metrics for streaming operations"""
    messages_processed: int = 0
    messages_dropped: int = 0
    average_latency_ms: float = 0.0
    throughput_per_second: float = 0.0
    buffer_utilization: float = 0.0
    error_rate: float = 0.0
    uptime_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StreamingData(BaseModel):
    """Data structure for streaming messages"""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: Any
    format: DataFormat
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class ConnectionManager:
    """WebSocket connection manager for real-time communication"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Accept WebSocket connection"""
        await websocket.accept()
        
        async with self._lock:
            self.active_connections[client_id] = websocket
            self.connection_metadata[client_id] = {
                'connected_at': datetime.now(timezone.utc),
                'message_count': 0,
                **(metadata or {})
            }
        
        logger.info(f"Client {client_id} connected")
    
    async def disconnect(self, client_id: str):
        """Remove connection"""
        async with self._lock:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            if client_id in self.connection_metadata:
                del self.connection_metadata[client_id]
        
        logger.info(f"Client {client_id} disconnected")
    
    async def send_personal_message(
        self,
        message: Union[str, Dict[str, Any]],
        client_id: str
    ) -> bool:
        """Send message to specific client"""
        try:
            if client_id in self.active_connections:
                websocket = self.active_connections[client_id]
                
                if isinstance(message, dict):
                    await websocket.send_json(message)
                else:
                    await websocket.send_text(message)
                
                # Update metadata
                if client_id in self.connection_metadata:
                    self.connection_metadata[client_id]['message_count'] += 1
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to send message to {client_id}: {e}")
            await self.disconnect(client_id)
            return False
    
    async def broadcast(self, message: Union[str, Dict[str, Any]]):
        """Broadcast message to all connected clients"""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                if isinstance(message, dict):
                    await websocket.send_json(message)
                else:
                    await websocket.send_text(message)
                
                # Update metadata
                if client_id in self.connection_metadata:
                    self.connection_metadata[client_id]['message_count'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to broadcast to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            'total_connections': len(self.active_connections),
            'connections': {
                client_id: metadata
                for client_id, metadata in self.connection_metadata.items()
            }
        }


class StreamingBuffer:
    """High-performance streaming data buffer"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._buffer: List[StreamingData] = []
        self._lock = asyncio.Lock()
        self._not_empty = asyncio.Condition(self._lock)
        self._not_full = asyncio.Condition(self._lock)
        self._closed = False
    
    async def put(self, item: StreamingData, timeout: Optional[float] = None) -> bool:
        """Add item to buffer"""
        async with self._not_full:
            # Wait for space if buffer is full
            if len(self._buffer) >= self.max_size:
                if timeout is None:
                    await self._not_full.wait()
                else:
                    try:
                        await asyncio.wait_for(self._not_full.wait(), timeout)
                    except asyncio.TimeoutError:
                        return False
            
            if self._closed:
                return False
            
            # Add to buffer (priority queue simulation)
            if item.priority == ProcessingPriority.CRITICAL:
                self._buffer.insert(0, item)
            elif item.priority == ProcessingPriority.HIGH:
                # Insert after other critical items
                insert_pos = 0
                while (insert_pos < len(self._buffer) and 
                       self._buffer[insert_pos].priority == ProcessingPriority.CRITICAL):
                    insert_pos += 1
                self._buffer.insert(insert_pos, item)
            else:
                self._buffer.append(item)
            
            self._not_empty.notify()
            return True
    
    async def get(self, timeout: Optional[float] = None) -> Optional[StreamingData]:
        """Get item from buffer"""
        async with self._not_empty:
            # Wait for item if buffer is empty
            while not self._buffer and not self._closed:
                if timeout is None:
                    await self._not_empty.wait()
                else:
                    try:
                        await asyncio.wait_for(self._not_empty.wait(), timeout)
                    except asyncio.TimeoutError:
                        return None
            
            if self._buffer:
                item = self._buffer.pop(0)
                self._not_full.notify()
                return item
            
            return None
    
    async def get_batch(self, batch_size: int, timeout: Optional[float] = None) -> List[StreamingData]:
        """Get batch of items from buffer"""
        batch = []
        
        async with self._lock:
            # Get available items up to batch_size
            available = min(batch_size, len(self._buffer))
            for _ in range(available):
                if self._buffer:
                    batch.append(self._buffer.pop(0))
            
            if batch:
                self._not_full.notify_all()
        
        return batch
    
    def size(self) -> int:
        """Get current buffer size"""
        return len(self._buffer)
    
    def is_full(self) -> bool:
        """Check if buffer is full"""
        return len(self._buffer) >= self.max_size
    
    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        return len(self._buffer) == 0
    
    async def close(self):
        """Close buffer"""
        async with self._lock:
            self._closed = True
            self._not_empty.notify_all()
            self._not_full.notify_all()


class {{agent_name}}RealTimeAgent(BaseAgent):
    """{{agent_description}}
    
    Real-time AI agent providing:
    - WebSocket-based real-time communication
    - High-throughput streaming data processing
    - Adaptive latency optimization
    - Priority-based message handling
    - Auto-scaling processing workers
    - Real-time metrics and monitoring
    - Event-driven architecture
    - Fault tolerance and recovery
    """
    
    def __init__(
        self,
        model_config: Dict[str, Any],
        streaming_config: Optional[StreamingConfig] = None,
        redis_client: Optional[redis.Redis] = None
    ):
        super().__init__(model_config)
        
        self.streaming_config = streaming_config or StreamingConfig()
        self.redis_client = redis_client
        
        # Core components
        self.connection_manager = ConnectionManager()
        self.streaming_buffer = StreamingBuffer(self.streaming_config.buffer_size)
        self.metrics = StreamingMetrics()
        
        # Processing control
        self._processing_tasks: List[asyncio.Task] = []
        self._is_running = False
        self._start_time = None
        
        # Thread pool for CPU-intensive tasks
        self._thread_pool = ThreadPoolExecutor(
            max_workers=self.streaming_config.max_workers
        )
        
        # Metrics tracking
        self._last_metrics_update = time.time()
        self._processed_count = 0
        self._latency_samples = []
    
    async def initialize(self):
        """Initialize the real-time agent"""
        try:
            await super().initialize()
            
            # Initialize Redis connection if provided
            if self.redis_client:
                await self.redis_client.ping()
            
            # Start processing workers
            await self._start_processing_workers()
            
            self._is_running = True
            self._start_time = time.time()
            
            logger.info("Real-time agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Real-time agent initialization failed: {e}")
            raise RealTimeError(f"Initialization failed: {str(e)}")
    
    async def process_stream(
        self,
        data_stream: AsyncIterator[Any],
        output_callback: Optional[Callable] = None
    ) -> AsyncIterator[Any]:
        """Process continuous data stream"""
        try:
            async for raw_data in data_stream:
                # Convert to StreamingData
                streaming_data = StreamingData(
                    data=raw_data,
                    format=self._detect_data_format(raw_data),
                    timestamp=datetime.now(timezone.utc)
                )
                
                # Add to processing buffer
                await self.streaming_buffer.put(streaming_data)
                
                # Process based on mode
                if self.streaming_config.mode == StreamingMode.CONTINUOUS:
                    # Continuous processing handled by workers
                    continue
                elif self.streaming_config.mode == StreamingMode.BATCH:
                    # Batch processing
                    if self.streaming_buffer.size() >= self.streaming_config.batch_size:
                        batch = await self.streaming_buffer.get_batch(
                            self.streaming_config.batch_size
                        )
                        results = await self._process_batch(batch)
                        
                        if output_callback:
                            for result in results:
                                await output_callback(result)
                        
                        for result in results:
                            yield result
                
        except Exception as e:
            logger.error(f"Stream processing error: {e}")
            raise RealTimeError(f"Stream processing failed: {str(e)}")
    
    async def handle_websocket(
        self,
        websocket: WebSocket,
        client_id: str,
        message_handler: Optional[Callable] = None
    ):
        """Handle WebSocket connection"""
        await self.connection_manager.connect(websocket, client_id)
        
        try:
            while True:
                # Receive message
                try:
                    message = await websocket.receive_text()
                    data = json.loads(message)
                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError:
                    await self.connection_manager.send_personal_message(
                        {"error": "Invalid JSON format"}, client_id
                    )
                    continue
                
                # Process message
                start_time = time.time()
                
                try:
                    if message_handler:
                        result = await message_handler(data, client_id)
                    else:
                        result = await self._process_websocket_message(data, client_id)
                    
                    # Send response
                    response = {
                        "id": str(uuid4()),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "result": result,
                        "processing_time_ms": (time.time() - start_time) * 1000
                    }
                    
                    await self.connection_manager.send_personal_message(response, client_id)
                    
                    # Update metrics
                    self._update_latency_metrics(time.time() - start_time)
                    
                except Exception as e:
                    logger.error(f"Message processing error: {e}")
                    await self.connection_manager.send_personal_message(
                        {
                            "error": "Processing failed",
                            "message": str(e)
                        },
                        client_id
                    )
        
        except WebSocketDisconnect:
            pass
        finally:
            await self.connection_manager.disconnect(client_id)
    
    async def broadcast_update(self, data: Any, target_clients: Optional[List[str]] = None):
        """Broadcast update to connected clients"""
        message = {
            "type": "update",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        
        if target_clients:
            for client_id in target_clients:
                await self.connection_manager.send_personal_message(message, client_id)
        else:
            await self.connection_manager.broadcast(message)
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        current_time = time.time()
        
        if self._start_time:
            self.metrics.uptime_seconds = current_time - self._start_time
        
        # Calculate throughput
        time_diff = current_time - self._last_metrics_update
        if time_diff > 0:
            self.metrics.throughput_per_second = self._processed_count / time_diff
        
        # Calculate average latency
        if self._latency_samples:
            self.metrics.average_latency_ms = (
                sum(self._latency_samples) / len(self._latency_samples)
            ) * 1000
            # Keep only recent samples
            self._latency_samples = self._latency_samples[-1000:]
        
        # Buffer utilization
        self.metrics.buffer_utilization = (
            self.streaming_buffer.size() / self.streaming_config.buffer_size
        )
        
        # Reset counters
        self._processed_count = 0
        self._last_metrics_update = current_time
        
        return {
            "metrics": self.metrics.to_dict(),
            "connections": self.connection_manager.get_connection_stats(),
            "buffer_status": {
                "size": self.streaming_buffer.size(),
                "max_size": self.streaming_config.buffer_size,
                "is_full": self.streaming_buffer.is_full()
            },
            "config": asdict(self.streaming_config)
        }
    
    async def _start_processing_workers(self):
        """Start background processing workers"""
        for i in range(self.streaming_config.max_workers):
            task = asyncio.create_task(
                self._processing_worker(f"worker-{i}")
            )
            self._processing_tasks.append(task)
        
        logger.info(f"Started {len(self._processing_tasks)} processing workers")
    
    async def _processing_worker(self, worker_id: str):
        """Background worker for processing streaming data"""
        logger.info(f"Processing worker {worker_id} started")
        
        try:
            while self._is_running:
                # Get data from buffer
                data = await self.streaming_buffer.get(timeout=1.0)
                
                if data is None:
                    continue
                
                start_time = time.time()
                
                try:
                    # Process the data
                    result = await self._process_streaming_data(data)
                    
                    # Store or broadcast result
                    if result:
                        await self._handle_processing_result(result, data)
                    
                    # Update metrics
                    self._processed_count += 1
                    self._update_latency_metrics(time.time() - start_time)
                    
                except Exception as e:
                    logger.error(f"Worker {worker_id} processing error: {e}")
                    self.metrics.error_rate += 1
        
        except Exception as e:
            logger.error(f"Worker {worker_id} crashed: {e}")
        finally:
            logger.info(f"Processing worker {worker_id} stopped")
    
    async def _process_streaming_data(self, data: StreamingData) -> Any:
        """Process individual streaming data item"""
        try:
            # Check latency requirements
            processing_time = (
                datetime.now(timezone.utc) - data.timestamp
            ).total_seconds() * 1000
            
            if processing_time > self.streaming_config.max_latency_ms:
                logger.warning(f"Data exceeds latency threshold: {processing_time}ms")
                self.metrics.messages_dropped += 1
                return None
            
            # Format-specific processing
            if data.format == DataFormat.JSON:
                return await self._process_json_data(data)
            elif data.format == DataFormat.TEXT:
                return await self._process_text_data(data)
            elif data.format == DataFormat.AUDIO:
                return await self._process_audio_data(data)
            elif data.format == DataFormat.IMAGE:
                return await self._process_image_data(data)
            else:
                return await self._process_generic_data(data)
                
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            raise
    
    async def _process_json_data(self, data: StreamingData) -> Any:
        """Process JSON data"""
        try:
            # Run AI processing on the data
            result = await self.predict(data.data)
            
            return {
                "id": str(data.id),
                "result": result,
                "format": data.format.value,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"JSON data processing failed: {e}")
            raise
    
    async def _process_text_data(self, data: StreamingData) -> Any:
        """Process text data"""
        try:
            # Text-specific AI processing
            result = await self.predict({"text": data.data})
            
            return {
                "id": str(data.id),
                "result": result,
                "format": data.format.value,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Text data processing failed: {e}")
            raise
    
    async def _process_audio_data(self, data: StreamingData) -> Any:
        """Process audio data"""
        try:
            # Audio-specific processing (transcription, analysis, etc.)
            result = await self._run_in_thread(self._process_audio_sync, data.data)
            
            return {
                "id": str(data.id),
                "result": result,
                "format": data.format.value,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Audio data processing failed: {e}")
            raise
    
    async def _process_image_data(self, data: StreamingData) -> Any:
        """Process image data"""
        try:
            # Image-specific processing (computer vision, analysis, etc.)
            result = await self._run_in_thread(self._process_image_sync, data.data)
            
            return {
                "id": str(data.id),
                "result": result,
                "format": data.format.value,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Image data processing failed: {e}")
            raise
    
    async def _process_generic_data(self, data: StreamingData) -> Any:
        """Process generic data"""
        try:
            # Generic AI processing
            result = await self.predict(data.data)
            
            return {
                "id": str(data.id),
                "result": result,
                "format": data.format.value,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Generic data processing failed: {e}")
            raise
    
    async def _process_websocket_message(
        self,
        message: Dict[str, Any],
        client_id: str
    ) -> Any:
        """Process WebSocket message"""
        message_type = message.get("type", "predict")
        
        if message_type == "predict":
            data = message.get("data")
            return await self.predict(data)
        
        elif message_type == "batch_predict":
            batch_data = message.get("batch", [])
            results = []
            for item in batch_data:
                result = await self.predict(item)
                results.append(result)
            return results
        
        elif message_type == "get_metrics":
            return await self.get_real_time_metrics()
        
        else:
            raise ValueError(f"Unknown message type: {message_type}")
    
    async def _handle_processing_result(self, result: Any, original_data: StreamingData):
        """Handle processing result (store, broadcast, etc.)"""
        try:
            # Store in Redis if available
            if self.redis_client:
                key = f"realtime_result:{original_data.id}"
                await self.redis_client.setex(
                    key,
                    3600,  # 1 hour TTL
                    json.dumps(result, default=str)
                )
            
            # Broadcast to relevant clients
            await self.broadcast_update(result)
            
        except Exception as e:
            logger.error(f"Result handling failed: {e}")
    
    async def _process_batch(self, batch: List[StreamingData]) -> List[Any]:
        """Process batch of streaming data"""
        tasks = []
        for data in batch:
            task = asyncio.create_task(self._process_streaming_data(data))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None results
        valid_results = [
            result for result in results
            if result is not None and not isinstance(result, Exception)
        ]
        
        return valid_results
    
    async def _run_in_thread(self, func: Callable, *args) -> Any:
        """Run CPU-intensive function in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._thread_pool, func, *args)
    
    def _process_audio_sync(self, audio_data: Any) -> Any:
        """Synchronous audio processing"""
        # Implement audio processing logic here
        # This is a placeholder
        return {"type": "audio_analysis", "status": "processed"}
    
    def _process_image_sync(self, image_data: Any) -> Any:
        """Synchronous image processing"""
        # Implement image processing logic here
        # This is a placeholder
        return {"type": "image_analysis", "status": "processed"}
    
    def _detect_data_format(self, data: Any) -> DataFormat:
        """Detect data format"""
        if isinstance(data, dict):
            return DataFormat.JSON
        elif isinstance(data, str):
            return DataFormat.TEXT
        elif isinstance(data, bytes):
            return DataFormat.BINARY
        else:
            return DataFormat.JSON  # Default
    
    def _update_latency_metrics(self, latency_seconds: float):
        """Update latency metrics"""
        self._latency_samples.append(latency_seconds)
        
        # Keep only recent samples to manage memory
        if len(self._latency_samples) > 10000:
            self._latency_samples = self._latency_samples[-5000:]
    
    async def shutdown(self):
        """Gracefully shutdown the agent"""
        try:
            self._is_running = False
            
            # Cancel processing tasks
            for task in self._processing_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self._processing_tasks:
                await asyncio.gather(*self._processing_tasks, return_exceptions=True)
            
            # Close buffer
            await self.streaming_buffer.close()
            
            # Shutdown thread pool
            self._thread_pool.shutdown(wait=True)
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Real-time agent shutdown completed")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")


# Factory function
def create_realtime_agent(
    model_config: Dict[str, Any],
    streaming_config: Optional[StreamingConfig] = None,
    redis_url: Optional[str] = None
) -> {{agent_name}}RealTimeAgent:
    """Create real-time agent instance"""
    
    redis_client = None
    if redis_url:
        redis_client = redis.from_url(redis_url)
    
    return {{agent_name}}RealTimeAgent(
        model_config=model_config,
        streaming_config=streaming_config,
        redis_client=redis_client
    )


# Export agent class
__all__ = [
    'RealTimeError',
    'StreamingMode',
    'ProcessingPriority',
    'DataFormat',
    'StreamingConfig',
    'StreamingMetrics',
    'StreamingData',
    'ConnectionManager',
    'StreamingBuffer',
    '{{agent_name}}RealTimeAgent',
    'create_realtime_agent'
]