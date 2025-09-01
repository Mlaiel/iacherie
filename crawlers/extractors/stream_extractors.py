"""Stream Extractors - Industrial IA Real-time Data Processing System
=================================================================

Ultra-advanced professional stream and real-time data extractors for live content processing.
Implements enterprise-grade streaming, live monitoring, and real-time extraction capabilities with AI.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""

import asyncio
import logging
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple, Set, AsyncGenerator, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor
import queue
import struct

# Import core extraction components
from .extraction_engine import BaseExtractor, ExtractionRequest, ExtractionResult, ExtractionStatus, ContentType

# Import third-party libraries conditionally
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

logger = logging.getLogger(__name__)


class StreamType(Enum):
    """
Stream type enumeration"""

    WEBSOCKET = "websocket"
    HTTP_STREAM = "http_stream"
    TCP_STREAM = "tcp_stream"
    AUDIO_STREAM = "audio_stream"
    VIDEO_STREAM = "video_stream"
    RSS_FEED = "rss_feed"
    LIVE_API = "live_api"
    REDIS_STREAM = "redis_stream"


@dataclass
class StreamMetadata:
    """Stream metadata container"""
    
    stream_id: str
    stream_type: StreamType
    source_url: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    total_messages: int = 0
    bytes_processed: int = 0
    error_count: int = 0
    is_active: bool = True
    connection_attempts: int = 0
    reconnection_count: int = 0
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamChunk:
    """
Stream data chunk container"""
    
    chunk_id: str
    stream_id: str
    timestamp: datetime
    data: bytes
    chunk_size: int
    chunk_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_final: bool = False


class BaseStreamExtractor(BaseExtractor):
    """
Base class for stream extractors"""
    
    def __init__(self, name: str, stream_type: StreamType):
        super().__init__(name)
        self.stream_type = stream_type
        self.max_chunk_size = 1024 * 1024  # 1MB
        self.buffer_size = 10 * 1024 * 1024  # 10MB
        self.reconnect_delay = 5.0
        self.max_reconnects = 10
        self.chunk_processors: List[Callable] = []
        self.active_streams: Dict[str, StreamMetadata] = {}
        
    async def start_stream(self, request: ExtractionRequest) -> str:
        """
Start streaming and return stream ID"""
        stream_id = self._generate_stream_id(request)
        
        metadata = StreamMetadata(
            stream_id=stream_id,
            stream_type=self.stream_type,
            source_url=request.source_url
        )
        
        self.active_streams[stream_id] = metadata
        
        # Start streaming task
        asyncio.create_task(self._stream_processor(request, stream_id))
        
        return stream_id
    
    async def stop_stream(self, stream_id: str) -> bool:
        """
Stop streaming"""
        if stream_id in self.active_streams:
            self.active_streams[stream_id].is_active = False
            return True
        return False
    
    async def get_stream_status(self, stream_id: str) -> Optional[StreamMetadata]:
        """
Get stream status"""
        return self.active_streams.get(stream_id)
    
    def _generate_stream_id(self, request: ExtractionRequest) -> str:
        """
Generate unique stream ID"""
        content = f"{request.source_url}_{request.request_id}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    @abstractmethod
    async def _stream_processor(self, request: ExtractionRequest, stream_id: str):
        """Main stream processing logic"""
        pass
    
    async def _process_chunk(self, chunk: StreamChunk) -> Optional[Dict[str, Any]]:
        """
Process individual stream chunk"""
        processed_data = {
            'chunk_id': chunk.chunk_id,
            'stream_id': chunk.stream_id,
            'timestamp': chunk.timestamp.isoformat(),
            'size': chunk.chunk_size,
            'index': chunk.chunk_index,
            'is_final': chunk.is_final
        }
        
        # Apply chunk processors
        for processor in self.chunk_processors:
            try:
                processed_data = await processor(chunk, processed_data)
            except Exception as e:
                self.logger.error(f"Chunk processor failed: {str(e)}")
        
        return processed_data
    
    def add_chunk_processor(self, processor: Callable):
        """Add chunk processor function"""
        self.chunk_processors.append(processor)


class WebSocketExtractor(BaseStreamExtractor):
    """
Advanced WebSocket stream extractor"""
    
    def __init__(self):
        super().__init__("WebSocketExtractor", StreamType.WEBSOCKET)
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for WebSocket stream"""
        if not HAS_WEBSOCKETS:
            return False
        
        if request.source_url:
            return request.source_url.startswith(('ws://', 'wss://'))
        
        return False
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """
Start WebSocket extraction"""
        try:
            stream_id = await self.start_stream(request)
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.RUNNING,
                extracted_data={'stream_id': stream_id, 'type': 'websocket_stream'},
                metadata={'stream': self.active_streams[stream_id]},
                content_type=ContentType.STREAM,
                processing_time=0
            )
            
        except Exception as e:
            self.logger.error(f"WebSocket extraction failed: {str(e)}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e)
            )
    
    async def _stream_processor(self, request: ExtractionRequest, stream_id: str):
        """Process WebSocket stream"""
        if not HAS_WEBSOCKETS:
            return
        
        metadata = self.active_streams[stream_id]
        reconnect_count = 0
        
        while metadata.is_active and reconnect_count < self.max_reconnects:
            try:
                metadata.connection_attempts += 1
                
                # Connect to WebSocket
                headers = request.headers or {}
                async with websockets.connect(
                    request.source_url,
                    extra_headers=headers,
                    timeout=30
                ) as websocket:
                    
                    self.logger.info(f"WebSocket connected: {stream_id}")
                    chunk_index = 0
                    
                    # Process messages
                    async for message in websocket:
                        if not metadata.is_active:
                            break
                        
                        # Create chunk
                        chunk = StreamChunk(
                            chunk_id=f"{stream_id}_{chunk_index}",
                            stream_id=stream_id,
                            timestamp=datetime.utcnow(),
                            data=message.encode() if isinstance(message, str) else message,
                            chunk_size=len(message) if isinstance(message, str) else len(message),
                            chunk_index=chunk_index
                        )
                        
                        # Process chunk
                        processed = await self._process_chunk(chunk)
                        
                        # Update metadata
                        metadata.total_messages += 1
                        metadata.bytes_processed += chunk.chunk_size
                        metadata.last_activity = datetime.utcnow()
                        
                        chunk_index += 1
                    
                    # Clean exit
                    break
                    
            except websockets.exceptions.WebSocketException as e:
                self.logger.warning(f"WebSocket error: {str(e)}")
                metadata.error_count += 1
                reconnect_count += 1
                
                if reconnect_count < self.max_reconnects:
                    await asyncio.sleep(self.reconnect_delay)
                    metadata.reconnection_count += 1
                
            except Exception as e:
                self.logger.error(f"WebSocket processing error: {str(e)}")
                break
        
        # Mark stream as inactive
        metadata.is_active = False
        self.logger.info(f"WebSocket stream ended: {stream_id}")


class HTTPStreamExtractor(BaseStreamExtractor):
    """Advanced HTTP stream extractor for chunked content"""
    
    def __init__(self):
        super().__init__("HTTPStreamExtractor", StreamType.HTTP_STREAM)
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for HTTP stream"""
        if not HAS_AIOHTTP:
            return False
        
        if request.source_url:
            return request.source_url.startswith(('http://', 'https://'))
        
        return False
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """
Start HTTP stream extraction"""
        try:
            stream_id = await self.start_stream(request)
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.RUNNING,
                extracted_data={'stream_id': stream_id, 'type': 'http_stream'},
                metadata={'stream': self.active_streams[stream_id]},
                content_type=ContentType.STREAM,
                processing_time=0
            )
            
        except Exception as e:
            self.logger.error(f"HTTP stream extraction failed: {str(e)}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e)
            )
    
    async def _stream_processor(self, request: ExtractionRequest, stream_id: str):
        """Process HTTP stream"""
        if not HAS_AIOHTTP:
            return
        
        metadata = self.active_streams[stream_id]
        
        try:
            headers = {
                'User-Agent': 'IA-Influencer-Agent/1.0',
                'Accept': '*/*',
                'Cache-Control': 'no-cache'
            }
            headers.update(request.headers or {})
            
            timeout = aiohttp.ClientTimeout(total=None, sock_read=30)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(request.source_url, headers=headers) as response:
                    
                    if response.status >= 400:
                        raise aiohttp.ClientError(f"HTTP {response.status}")
                    
                    chunk_index = 0
                    
                    # Process chunks
                    async for chunk_data in response.content.iter_chunked(self.max_chunk_size):
                        if not metadata.is_active:
                            break
                        
                        # Create chunk
                        chunk = StreamChunk(
                            chunk_id=f"{stream_id}_{chunk_index}",
                            stream_id=stream_id,
                            timestamp=datetime.utcnow(),
                            data=chunk_data,
                            chunk_size=len(chunk_data),
                            chunk_index=chunk_index
                        )
                        
                        # Process chunk
                        processed = await self._process_chunk(chunk)
                        
                        # Update metadata
                        metadata.total_messages += 1
                        metadata.bytes_processed += chunk.chunk_size
                        metadata.last_activity = datetime.utcnow()
                        
                        chunk_index += 1
                    
                    # Mark final chunk
                    if chunk_index > 0:
                        final_chunk = StreamChunk(
                            chunk_id=f"{stream_id}_final",
                            stream_id=stream_id,
                            timestamp=datetime.utcnow(),
                            data=b'',
                            chunk_size=0,
                            chunk_index=chunk_index,
                            is_final=True
                        )
                        await self._process_chunk(final_chunk)
                        
        except Exception as e:
            self.logger.error(f"HTTP stream processing error: {str(e)}")
            metadata.error_count += 1
        
        # Mark stream as inactive
        metadata.is_active = False
        self.logger.info(f"HTTP stream ended: {stream_id}")


class AudioStreamExtractor(BaseStreamExtractor):
    """Advanced audio stream extractor"""
    
    def __init__(self):
        super().__init__("AudioStreamExtractor", StreamType.AUDIO_STREAM)
        self.sample_rate = 44100
        self.channels = 2
        self.chunk_duration = 1.0  # seconds
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for audio stream"""
        if not HAS_PYAUDIO:
            return False
        
        return request.metadata.get('stream_type') == 'audio'
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """
Start audio stream extraction"""
        try:
            stream_id = await self.start_stream(request)
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.RUNNING,
                extracted_data={'stream_id': stream_id, 'type': 'audio_stream'},
                metadata={'stream': self.active_streams[stream_id]},
                content_type=ContentType.AUDIO,
                processing_time=0
            )
            
        except Exception as e:
            self.logger.error(f"Audio stream extraction failed: {str(e)}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e)
            )
    
    async def _stream_processor(self, request: ExtractionRequest, stream_id: str):
        """Process audio stream"""
        if not HAS_PYAUDIO:
            return
        
        metadata = self.active_streams[stream_id]
        
        try:
            audio = pyaudio.PyAudio()
            
            # Configure audio stream
            chunk_size = int(self.sample_rate * self.chunk_duration)
            
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=chunk_size
            )
            
            chunk_index = 0
            
            while metadata.is_active:
                try:
                    # Read audio data
                    audio_data = stream.read(chunk_size)
                    
                    # Create chunk
                    chunk = StreamChunk(
                        chunk_id=f"{stream_id}_{chunk_index}",
                        stream_id=stream_id,
                        timestamp=datetime.utcnow(),
                        data=audio_data,
                        chunk_size=len(audio_data),
                        chunk_index=chunk_index,
                        metadata={
                            'sample_rate': self.sample_rate,
                            'channels': self.channels,
                            'duration': self.chunk_duration,
                            'format': 'int16'
                        }
                    )
                    
                    # Process chunk
                    processed = await self._process_chunk(chunk)
                    
                    # Update metadata
                    metadata.total_messages += 1
                    metadata.bytes_processed += chunk.chunk_size
                    metadata.last_activity = datetime.utcnow()
                    
                    chunk_index += 1
                    
                except Exception as e:
                    self.logger.error(f"Audio chunk processing error: {str(e)}")
                    metadata.error_count += 1
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
        except Exception as e:
            self.logger.error(f"Audio stream error: {str(e)}")
            metadata.error_count += 1
        
        # Mark stream as inactive
        metadata.is_active = False
        self.logger.info(f"Audio stream ended: {stream_id}")


class VideoStreamExtractor(BaseStreamExtractor):
    """Advanced video stream extractor"""
    
    def __init__(self):
        super().__init__("VideoStreamExtractor", StreamType.VIDEO_STREAM)
        self.fps = 30
        self.frame_width = 640
        self.frame_height = 480
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for video stream"""
        if not HAS_OPENCV:
            return False
        
        return request.metadata.get('stream_type') == 'video'
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """
Start video stream extraction"""
        try:
            stream_id = await self.start_stream(request)
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.RUNNING,
                extracted_data={'stream_id': stream_id, 'type': 'video_stream'},
                metadata={'stream': self.active_streams[stream_id]},
                content_type=ContentType.VIDEO,
                processing_time=0
            )
            
        except Exception as e:
            self.logger.error(f"Video stream extraction failed: {str(e)}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e)
            )
    
    async def _stream_processor(self, request: ExtractionRequest, stream_id: str):
        """Process video stream"""
        if not HAS_OPENCV:
            return
        
        metadata = self.active_streams[stream_id]
        
        try:
            # Open video source
            source = request.metadata.get('video_source', 0)  # Default to webcam
            cap = cv2.VideoCapture(source)
            
            if not cap.isOpened():
                raise RuntimeError(f"Cannot open video source: {source}")
            
            # Configure capture
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            chunk_index = 0
            frame_interval = 1.0 / self.fps
            
            while metadata.is_active:
                try:
                    # Read frame
                    ret, frame = cap.read()
                    
                    if not ret:
                        break
                    
                    # Encode frame
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_data = buffer.tobytes()
                    
                    # Create chunk
                    chunk = StreamChunk(
                        chunk_id=f"{stream_id}_{chunk_index}",
                        stream_id=stream_id,
                        timestamp=datetime.utcnow(),
                        data=frame_data,
                        chunk_size=len(frame_data),
                        chunk_index=chunk_index,
                        metadata={
                            'width': self.frame_width,
                            'height': self.frame_height,
                            'fps': self.fps,
                            'format': 'jpeg',
                            'frame_number': chunk_index
                        }
                    )
                    
                    # Process chunk
                    processed = await self._process_chunk(chunk)
                    
                    # Update metadata
                    metadata.total_messages += 1
                    metadata.bytes_processed += chunk.chunk_size
                    metadata.last_activity = datetime.utcnow()
                    
                    chunk_index += 1
                    
                    # Frame rate control
                    await asyncio.sleep(frame_interval)
                    
                except Exception as e:
                    self.logger.error(f"Video frame processing error: {str(e)}")
                    metadata.error_count += 1
            
            # Cleanup
            cap.release()
            
        except Exception as e:
            self.logger.error(f"Video stream error: {str(e)}")
            metadata.error_count += 1
        
        # Mark stream as inactive
        metadata.is_active = False
        self.logger.info(f"Video stream ended: {stream_id}")


class RedisStreamExtractor(BaseStreamExtractor):
    """Advanced Redis stream extractor"""
    
    def __init__(self):
        super().__init__("RedisStreamExtractor", StreamType.REDIS_STREAM)
        self.redis_client = None
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for Redis stream"""
        if not HAS_REDIS:
            return False
        
        return request.metadata.get('stream_type') == 'redis'
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """
Start Redis stream extraction"""
        try:
            # Initialize Redis client
            redis_config = request.metadata.get('redis_config', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                decode_responses=True
            )
            
            stream_id = await self.start_stream(request)
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.RUNNING,
                extracted_data={'stream_id': stream_id, 'type': 'redis_stream'},
                metadata={'stream': self.active_streams[stream_id]},
                content_type=ContentType.STREAM,
                processing_time=0
            )
            
        except Exception as e:
            self.logger.error(f"Redis stream extraction failed: {str(e)}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e)
            )
    
    async def _stream_processor(self, request: ExtractionRequest, stream_id: str):
        """Process Redis stream"""
        if not HAS_REDIS or not self.redis_client:
            return
        
        metadata = self.active_streams[stream_id]
        stream_name = request.metadata.get('stream_name', 'default_stream')
        consumer_group = request.metadata.get('consumer_group', 'extractors')
        consumer_name = f"extractor_{stream_id}"
        
        try:
            # Create consumer group if not exists
            try:
                self.redis_client.xgroup_create(stream_name, consumer_group, id='0', mkstream=True)
            except redis.exceptions.ResponseError:
                pass  # Group already exists
            
            chunk_index = 0
            
            while metadata.is_active:
                try:
                    # Read from stream
                    messages = self.redis_client.xreadgroup(
                        consumer_group,
                        consumer_name,
                        {stream_name: '>'},
                        count=10,
                        block=1000  # 1 second timeout
                    )
                    
                    for stream, msgs in messages:
                        for msg_id, fields in msgs:
                            if not metadata.is_active:
                                break
                            
                            # Create chunk
                            chunk = StreamChunk(
                                chunk_id=f"{stream_id}_{chunk_index}",
                                stream_id=stream_id,
                                timestamp=datetime.utcnow(),
                                data=json.dumps(fields).encode(),
                                chunk_size=len(json.dumps(fields)),
                                chunk_index=chunk_index,
                                metadata={
                                    'redis_stream': stream.decode() if isinstance(stream, bytes) else stream,
                                    'message_id': msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                                    'fields': fields
                                }
                            )
                            
                            # Process chunk
                            processed = await self._process_chunk(chunk)
                            
                            # Acknowledge message
                            self.redis_client.xack(stream_name, consumer_group, msg_id)
                            
                            # Update metadata
                            metadata.total_messages += 1
                            metadata.bytes_processed += chunk.chunk_size
                            metadata.last_activity = datetime.utcnow()
                            
                            chunk_index += 1
                    
                except redis.exceptions.ConnectionError as e:
                    self.logger.error(f"Redis connection error: {str(e)}")
                    metadata.error_count += 1
                    await asyncio.sleep(self.reconnect_delay)
                    
                except Exception as e:
                    self.logger.error(f"Redis stream processing error: {str(e)}")
                    metadata.error_count += 1
            
        except Exception as e:
            self.logger.error(f"Redis stream error: {str(e)}")
            metadata.error_count += 1
        
        # Mark stream as inactive
        metadata.is_active = False
        self.logger.info(f"Redis stream ended: {stream_id}")


class LiveAPIExtractor(BaseStreamExtractor):
    """Advanced live API extractor for polling-based streams"""
    
    def __init__(self):
        super().__init__("LiveAPIExtractor", StreamType.LIVE_API)
        self.poll_interval = 5.0  # seconds
        
    async def can_handle(self, request: ExtractionRequest) -> bool:
        """Check if request is for live API"""
        if not HAS_AIOHTTP:
            return False
        
        return request.metadata.get('stream_type') == 'live_api'
    
    async def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """
Start live API extraction"""
        try:
            stream_id = await self.start_stream(request)
            
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.RUNNING,
                extracted_data={'stream_id': stream_id, 'type': 'live_api'},
                metadata={'stream': self.active_streams[stream_id]},
                content_type=ContentType.STREAM,
                processing_time=0
            )
            
        except Exception as e:
            self.logger.error(f"Live API extraction failed: {str(e)}")
            return ExtractionResult(
                request_id=request.request_id,
                status=ExtractionStatus.FAILED,
                error=str(e)
            )
    
    async def _stream_processor(self, request: ExtractionRequest, stream_id: str):
        """Process live API stream via polling"""
        if not HAS_AIOHTTP:
            return
        
        metadata = self.active_streams[stream_id]
        self.poll_interval = request.metadata.get('poll_interval', self.poll_interval)
        
        try:
            headers = {
                'User-Agent': 'IA-Influencer-Agent/1.0',
                'Accept': 'application/json',
            }
            headers.update(request.headers or {})
            
            chunk_index = 0
            last_data_hash = None
            
            async with aiohttp.ClientSession() as session:
                while metadata.is_active:
                    try:
                        # Poll API
                        async with session.get(request.source_url, headers=headers) as response:
                            if response.status >= 400:
                                raise aiohttp.ClientError(f"HTTP {response.status}")
                            
                            data = await response.text()
                            
                            # Check if data changed
                            data_hash = hashlib.md5(data.encode()).hexdigest()
                            if data_hash == last_data_hash:
                                await asyncio.sleep(self.poll_interval)
                                continue
                            
                            last_data_hash = data_hash
                            
                            # Create chunk
                            chunk = StreamChunk(
                                chunk_id=f"{stream_id}_{chunk_index}",
                                stream_id=stream_id,
                                timestamp=datetime.utcnow(),
                                data=data.encode(),
                                chunk_size=len(data),
                                chunk_index=chunk_index,
                                metadata={
                                    'api_url': request.source_url,
                                    'response_status': response.status,
                                    'content_type': response.headers.get('content-type'),
                                    'data_hash': data_hash
                                }
                            )
                            
                            # Process chunk
                            processed = await self._process_chunk(chunk)
                            
                            # Update metadata
                            metadata.total_messages += 1
                            metadata.bytes_processed += chunk.chunk_size
                            metadata.last_activity = datetime.utcnow()
                            
                            chunk_index += 1
                        
                        # Wait before next poll
                        await asyncio.sleep(self.poll_interval)
                        
                    except Exception as e:
                        self.logger.error(f"API polling error: {str(e)}")
                        metadata.error_count += 1
                        await asyncio.sleep(self.poll_interval)
            
        except Exception as e:
            self.logger.error(f"Live API stream error: {str(e)}")
            metadata.error_count += 1
        
        # Mark stream as inactive
        metadata.is_active = False
        self.logger.info(f"Live API stream ended: {stream_id}")


# Stream processing utilities
class StreamBuffer:
    """Thread-safe circular buffer for stream data"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.buffer = []
        self.lock = threading.Lock()
        self.current_index = 0
        
    def add(self, chunk: StreamChunk):
        """
Add chunk to buffer"""
        with self.lock:
            if len(self.buffer) >= self.max_size:
                # Remove oldest chunk
                self.buffer.pop(0)
            
            self.buffer.append(chunk)
            self.current_index += 1
    
    def get_latest(self, count: int = 10) -> List[StreamChunk]:
        """
Get latest chunks"""
        with self.lock:
            return self.buffer[-count:] if count <= len(self.buffer) else self.buffer.copy()
    
    def get_range(self, start_index: int, end_index: int) -> List[StreamChunk]:
        """
Get chunks in range"""
        with self.lock:
            filtered = [chunk for chunk in self.buffer 
                       if start_index <= chunk.chunk_index <= end_index]
            return sorted(filtered, key=lambda x: x.chunk_index)
    
    def clear(self):
        """
Clear buffer"""
        with self.lock:
            self.buffer.clear()
            self.current_index = 0


class StreamManager:
    """
Manager for multiple stream extractors"""
    
    def __init__(self):
        self.extractors: Dict[StreamType, BaseStreamExtractor] = {}
        self.buffers: Dict[str, StreamBuffer] = {}
        self.active_streams: Set[str] = set()
        
    def register_extractor(self, extractor: BaseStreamExtractor):
        """
Register stream extractor"""
        self.extractors[extractor.stream_type] = extractor
        
        # Add buffer processor
        async def buffer_processor(chunk: StreamChunk, processed_data: Dict) -> Dict:
            if chunk.stream_id not in self.buffers:
                self.buffers[chunk.stream_id] = StreamBuffer()
            
            self.buffers[chunk.stream_id].add(chunk)
            return processed_data
        
        extractor.add_chunk_processor(buffer_processor)
    
    async def start_stream(self, request: ExtractionRequest) -> Optional[str]:
        """
Start stream with appropriate extractor"""
        # Determine stream type
        stream_type = self._detect_stream_type(request)
        
        if stream_type not in self.extractors:
            return None
        
        extractor = self.extractors[stream_type]
        
        if not await extractor.can_handle(request):
            return None
        
        stream_id = await extractor.start_stream(request)
        self.active_streams.add(stream_id)
        
        return stream_id
    
    async def stop_stream(self, stream_id: str) -> bool:
        """
Stop stream"""
        for extractor in self.extractors.values():
            if await extractor.stop_stream(stream_id):
                self.active_streams.discard(stream_id)
                return True
        return False
    
    def get_stream_buffer(self, stream_id: str) -> Optional[StreamBuffer]:
        """
Get stream buffer"""
        return self.buffers.get(stream_id)
    
    def _detect_stream_type(self, request: ExtractionRequest) -> Optional[StreamType]:
        """
Detect stream type from request"""
        if request.metadata.get('stream_type'):
            try:
                return StreamType(request.metadata['stream_type'])
            except ValueError:
                pass
        
        if request.source_url:
            if request.source_url.startswith(('ws://', 'wss://')):
                return StreamType.WEBSOCKET
            elif request.source_url.startswith(('http://', 'https://')):
                return StreamType.HTTP_STREAM
        
        return None


# Register default stream extractors
def register_default_stream_extractors():
    """
Register all default stream extractors"""
    manager = StreamManager()
    
    manager.register_extractor(WebSocketExtractor())
    manager.register_extractor(HTTPStreamExtractor())
    manager.register_extractor(AudioStreamExtractor())
    manager.register_extractor(VideoStreamExtractor())
    manager.register_extractor(RedisStreamExtractor())
    manager.register_extractor(LiveAPIExtractor())
    
    return manager


# Global stream manager instance
stream_manager = register_default_stream_extractors()


__all__ = [
    'StreamType',
    'StreamMetadata',
    'StreamChunk',
    'BaseStreamExtractor',
    'WebSocketExtractor',
    'HTTPStreamExtractor',
    'AudioStreamExtractor',
    'VideoStreamExtractor',
    'RedisStreamExtractor',
    'LiveAPIExtractor',
    'StreamBuffer',
    'StreamManager',
    'stream_manager',
    'register_default_stream_extractors'
]
