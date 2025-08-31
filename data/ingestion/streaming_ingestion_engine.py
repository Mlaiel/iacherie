"""
Streaming Ingestion Engine
=========================

Professional real-time streaming ingestion engine for multi-format content processing.
Advanced WebSocket-based content streaming with chunk processing, real-time validation,
and intelligent buffering for enterprise-grade content ingestion pipelines.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

  INTELLECTUAL PROPERTY WARNING 
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

PROJECT TEAM SPECIALTIES:
- Lead Dev IA & ML Engineer: Advanced AI/ML algorithms and model integration
- Backend Senior Developer: Enterprise architecture and scalable systems
- DBA & Data Engineer: Database optimization and data pipeline management  
- Security Specialist: Content protection and security validation
- DevOps Engineer: Infrastructure automation and deployment
- Audio/Video Specialist: Multimedia processing and codec optimization
- Microservices Architect: Distributed systems and service orchestration
- IA Prompt Engineer: AI model fine-tuning and content analysis
"""

import asyncio
import logging
import json
import time
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, BinaryIO, Callable, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from pathlib import Path
import tempfile
import mimetypes
from concurrent.futures import ThreadPoolExecutor
import ssl
import gzip
import base64

import websockets
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed, WebSocketException
import aiofiles
import aiohttp
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, validator
import numpy as np
from PIL import Image
import cv2

from .content_ingestion_manager import ContentIngestionManager, IngestionRequest, IngestionResult
from .multi_format_processor import MultiFormatProcessor, ProcessingOptions
from .metadata_extractor import MetadataExtractor
from ..validators.content_validator import ContentValidator
from ..quality.data_quality_manager import DataQualityManager
from ...core.exceptions import IngestionError, ValidationError
from ...core.config import get_settings
from ...core.security.auth_manager import AuthManager


class StreamingMode(Enum):
    """Streaming ingestion modes"""
    PROGRESSIVE = "progressive"  # Progressive upload with processing
    REALTIME = "realtime"       # Real-time streaming processing
    BUFFERED = "buffered"       # Buffered streaming with optimization
    ADAPTIVE = "adaptive"       # Adaptive quality streaming


class StreamingQuality(Enum):
    """Streaming quality levels"""
    LOW = "low"          # 64kbps audio, 500kbps video
    STANDARD = "standard"  # 128kbps audio, 1Mbps video
    HIGH = "high"        # 256kbps audio, 2Mbps video
    ULTRA = "ultra"      # 320kbps audio, 4Mbps video


class StreamingPriority(IntEnum):
    """Streaming processing priority"""
    LOW = 1
    NORMAL = 3
    HIGH = 5
    URGENT = 7
    CRITICAL = 10


class ChunkStatus(Enum):
    """Chunk processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATED = "validated"


@dataclass
class StreamingChunk:
    """Individual streaming chunk data"""
    chunk_id: str
    sequence_number: int
    data: bytes
    chunk_size: int
    checksum: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: ChunkStatus = ChunkStatus.PENDING
    processing_time: Optional[float] = None
    validation_result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamingSession:
    """Streaming session management"""
    session_id: str
    user_id: str
    websocket: WebSocketServerProtocol
    content_type: str
    filename: str
    total_size: Optional[int] = None
    mode: StreamingMode = StreamingMode.PROGRESSIVE
    quality: StreamingQuality = StreamingQuality.STANDARD
    priority: StreamingPriority = StreamingPriority.NORMAL
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    chunks_received: int = 0
    chunks_processed: int = 0
    bytes_received: int = 0
    bytes_processed: int = 0
    processing_stage: str = "initializing"
    is_active: bool = True
    buffer: List[StreamingChunk] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    last_error: Optional[str] = None


@dataclass
class StreamingResult:
    """Streaming processing result"""
    session_id: str
    success: bool
    content_id: Optional[str] = None
    total_chunks: int = 0
    processed_chunks: int = 0
    failed_chunks: int = 0
    total_bytes: int = 0
    processing_time: float = 0.0
    average_chunk_time: float = 0.0
    throughput_mbps: float = 0.0
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    validation_results: List[Dict[str, Any]] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    final_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class StreamingConfiguration(BaseModel):
    """Streaming engine configuration"""
    
    # WebSocket settings
    host: str = Field(default="0.0.0.0", description="WebSocket server host")
    port: int = Field(default=8765, description="WebSocket server port")
    max_connections: int = Field(default=1000, description="Maximum concurrent connections")
    connection_timeout: int = Field(default=300, description="Connection timeout in seconds")
    
    # Chunk processing
    chunk_size: int = Field(default=1048576, description="Default chunk size (1MB)")
    max_chunk_size: int = Field(default=10485760, description="Maximum chunk size (10MB)")
    buffer_size: int = Field(default=100, description="Maximum chunks in buffer")
    processing_threads: int = Field(default=10, description="Number of processing threads")
    
    # Quality settings
    enable_compression: bool = Field(default=True, description="Enable chunk compression")
    enable_encryption: bool = Field(default=True, description="Enable data encryption")
    enable_validation: bool = Field(default=True, description="Enable chunk validation")
    
    # Performance tuning
    batch_processing_size: int = Field(default=10, description="Chunks per batch")
    adaptive_quality: bool = Field(default=True, description="Enable adaptive quality")
    realtime_processing: bool = Field(default=True, description="Enable real-time processing")
    
    # Security
    require_authentication: bool = Field(default=True, description="Require user authentication")
    max_file_size: int = Field(default=1073741824, description="Maximum file size (1GB)")
    allowed_content_types: List[str] = Field(
        default=["audio/*", "video/*", "image/*", "text/*", "application/pdf"],
        description="Allowed MIME types"
    )
    
    @validator('chunk_size')
    def validate_chunk_size(cls, v):
        if v < 1024 or v > 10485760:  # 1KB to 10MB
            raise ValueError("Chunk size must be between 1KB and 10MB")
        return v


class StreamingIngestionEngine:
    """
    Professional streaming ingestion engine for real-time content processing.
    
    Features:
    - WebSocket-based streaming upload
    - Chunk-based processing with validation
    - Real-time quality monitoring
    - Adaptive streaming quality
    - Concurrent session management
    - Enterprise security and authentication
    """
    
    def __init__(self, 
                 db_session: AsyncSession,
                 redis_client: Redis,
                 content_manager: ContentIngestionManager,
                 auth_manager: AuthManager,
                 config: Optional[StreamingConfiguration] = None):
        """
        Initialize streaming ingestion engine.
        
        Args:
            db_session: Database session
            redis_client: Redis client for session management
            content_manager: Content ingestion manager
            auth_manager: Authentication manager
            config: Streaming configuration
        """
        self.db_session = db_session
        self.redis = redis_client
        self.content_manager = content_manager
        self.auth_manager = auth_manager
        self.config = config or StreamingConfiguration()
        self.logger = logging.getLogger(__name__)
        
        # Session management
        self.active_sessions: Dict[str, StreamingSession] = {}
        self.session_lock = asyncio.Lock()
        
        # Processing components
        self.processor = MultiFormatProcessor()
        self.metadata_extractor = MetadataExtractor()
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.processing_threads)
        
        # Server state
        self.server = None
        self.is_running = False
        
        # Performance monitoring
        self.session_metrics: Dict[str, List[float]] = {}
        self.global_metrics = {
            'total_sessions': 0,
            'active_sessions': 0,
            'total_bytes_processed': 0,
            'average_throughput': 0.0,
            'uptime_start': datetime.now(timezone.utc)
        }
        
        # Settings
        self.settings = get_settings()
    
    async def start_server(self) -> bool:
        """
        Start WebSocket streaming server.
        
        Returns:
            bool: True if server started successfully
        """



        try:
            if self.is_running:
                self.logger.warning("Streaming server already running")
                return True
            
            # SSL context for secure connections
            ssl_context = None
            if self.config.enable_encryption:
                ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                # Configure SSL context (in production, use proper certificates)
            
            # Start WebSocket server
            self.server = await websockets.serve(
                self._handle_websocket_connection,
                self.config.host,
                self.config.port,
                ssl=ssl_context,
                max_size=self.config.max_chunk_size,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.is_running = True
            self.global_metrics['uptime_start'] = datetime.now(timezone.utc)
            
            self.logger.info(f"Streaming server started on {self.config.host}:{self.config.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start streaming server: {str(e)}")
            return False
    
    async def stop_server(self):
        """Stop WebSocket streaming server"""



        try:
            if not self.is_running:
                return
            
            # Close all active sessions
            async with self.session_lock:
                for session in list(self.active_sessions.values()):
                    await self._close_session(session.session_id, "server_shutdown")
            
            # Stop server
            if self.server:
                self.server.close()
                await self.server.wait_closed()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            self.is_running = False
            self.logger.info("Streaming server stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping streaming server: {str(e)}")
    
    async def _handle_websocket_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new WebSocket connection"""
        client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
        session_id = None
        
        try:
            self.logger.info(f"New WebSocket connection from {client_ip}")
            
            # Authenticate connection
            session_id = await self._authenticate_connection(websocket)
            if not session_id:
                await websocket.close(code=4001, reason="Authentication failed")
                return
            
            # Handle session communication
            await self._handle_session_communication(websocket, session_id)
            
        except ConnectionClosed:
            self.logger.info(f"WebSocket connection closed: {client_ip}")
        except WebSocketException as e:
            self.logger.error(f"WebSocket error for {client_ip}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error handling connection {client_ip}: {str(e)}")
        finally:
            # Cleanup session
            if session_id:
                await self._close_session(session_id, "connection_closed")
    
    async def _authenticate_connection(self, websocket: WebSocketServerProtocol) -> Optional[str]:
        """
        Authenticate WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            
        Returns:
            str: Session ID if authenticated, None otherwise
        """



        try:
            if not self.config.require_authentication:
                # Create anonymous session
                return str(uuid.uuid4())
            
            # Wait for authentication message
            auth_message = await asyncio.wait_for(
                websocket.recv(), 
                timeout=self.config.connection_timeout
            )
            
            auth_data = json.loads(auth_message)
            
            # Validate authentication
            token = auth_data.get('token')
            if not token:
                await websocket.send(json.dumps({
                    'type': 'auth_error',
                    'message': 'Authentication token required'
                }))
                return None
            
            # Verify token with auth manager
            user_info = await self.auth_manager.verify_token(token)
            if not user_info:
                await websocket.send(json.dumps({
                    'type': 'auth_error',
                    'message': 'Invalid authentication token'
                }))
                return None
            
            # Create authenticated session
            session_id = str(uuid.uuid4())
            
            # Initialize session
            await self._create_session(
                session_id=session_id,
                user_id=user_info['user_id'],
                websocket=websocket,
                session_data=auth_data
            )
            
            # Send authentication success
            await websocket.send(json.dumps({
                'type': 'auth_success',
                'session_id': session_id,
                'user_id': user_info['user_id']
            }))
            
            return session_id
            
        except asyncio.TimeoutError:
            self.logger.warning("Authentication timeout")
            return None
        except json.JSONDecodeError:
            self.logger.warning("Invalid authentication message format")
            return None
        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return None
    
    async def _create_session(self, session_id: str, user_id: str, 
                            websocket: WebSocketServerProtocol, 
                            session_data: Dict[str, Any]) -> StreamingSession:
        """Create new streaming session"""
        async with self.session_lock:
            session = StreamingSession(
                session_id=session_id,
                user_id=user_id,
                websocket=websocket,
                content_type=session_data.get('content_type', 'auto'),
                filename=session_data.get('filename', f'stream_{session_id}'),
                total_size=session_data.get('total_size'),
                mode=StreamingMode(session_data.get('mode', 'progressive')),
                quality=StreamingQuality(session_data.get('quality', 'standard')),
                priority=StreamingPriority(session_data.get('priority', 3)),
                metadata=session_data.get('metadata', {})
            )
            
            self.active_sessions[session_id] = session
            self.global_metrics['total_sessions'] += 1
            self.global_metrics['active_sessions'] = len(self.active_sessions)
            
            # Store session in Redis for persistence
            await self._store_session_in_redis(session)
            
            self.logger.info(f"Created streaming session {session_id} for user {user_id}")
            return session
    
    async def _handle_session_communication(self, websocket: WebSocketServerProtocol, session_id: str):
        """Handle WebSocket communication for a session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        try:
            while session.is_active:
                # Receive message
                message = await websocket.recv()
                
                # Handle different message types
                if isinstance(message, bytes):
                    # Binary chunk data
                    await self._handle_chunk_data(session, message)
                else:
                    # JSON control message
                    await self._handle_control_message(session, message)
                
                # Update activity timestamp
                session.last_activity = datetime.now(timezone.utc)
                
        except ConnectionClosed:
            self.logger.info(f"Session {session_id} connection closed")
        except Exception as e:
            self.logger.error(f"Session {session_id} communication error: {str(e)}")
            session.error_count += 1
            session.last_error = str(e)
    
    async def _handle_chunk_data(self, session: StreamingSession, chunk_data: bytes):
        """Handle binary chunk data"""



        try:
            # Create chunk object
            chunk = StreamingChunk(
                chunk_id=str(uuid.uuid4()),
                sequence_number=session.chunks_received,
                data=chunk_data,
                chunk_size=len(chunk_data),
                checksum=hashlib.sha256(chunk_data).hexdigest()
            )
            
            # Update session metrics
            session.chunks_received += 1
            session.bytes_received += len(chunk_data)
            
            # Validate chunk if enabled
            if self.config.enable_validation:
                validation_result = await self._validate_chunk(session, chunk)
                chunk.validation_result = validation_result
                
                if not validation_result.get('valid', True):
                    chunk.status = ChunkStatus.FAILED
                    await self._send_error_message(session, "chunk_validation_failed", 
                                                 validation_result.get('errors', []))
                    return
            
            # Add to session buffer
            session.buffer.append(chunk)
            chunk.status = ChunkStatus.PENDING
            
            # Process chunk based on mode
            if session.mode == StreamingMode.REALTIME:
                # Process immediately
                asyncio.create_task(self._process_chunk_async(session, chunk))
            elif session.mode == StreamingMode.BUFFERED:
                # Process in batches
                if len(session.buffer) >= self.config.batch_processing_size:
                    await self._process_chunk_batch(session)
            elif session.mode == StreamingMode.PROGRESSIVE:
                # Queue for processing
                asyncio.create_task(self._process_chunk_async(session, chunk))
            
            # Send acknowledgment
            await self._send_chunk_ack(session, chunk)
            
            # Check if upload complete
            if (session.total_size and 
                session.bytes_received >= session.total_size):
                await self._finalize_session(session)
            
        except Exception as e:
            self.logger.error(f"Error handling chunk data: {str(e)}")
            session.error_count += 1
            await self._send_error_message(session, "chunk_processing_error", [str(e)])
    
    async def _handle_control_message(self, session: StreamingSession, message: str):
        """Handle JSON control messages"""



        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'upload_start':
                await self._handle_upload_start(session, data)
            elif message_type == 'upload_complete':
                await self._handle_upload_complete(session, data)
            elif message_type == 'upload_pause':
                await self._handle_upload_pause(session, data)
            elif message_type == 'upload_resume':
                await self._handle_upload_resume(session, data)
            elif message_type == 'upload_cancel':
                await self._handle_upload_cancel(session, data)
            elif message_type == 'get_status':
                await self._send_session_status(session)
            elif message_type == 'configure_quality':
                await self._handle_quality_configuration(session, data)
            else:
                self.logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            self.logger.warning("Invalid JSON control message")
        except Exception as e:
            self.logger.error(f"Error handling control message: {str(e)}")
    
    async def _process_chunk_async(self, session: StreamingSession, chunk: StreamingChunk):
        """Process chunk asynchronously"""



        try:
            start_time = time.time()
            chunk.status = ChunkStatus.PROCESSING
            
            # Run processing in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            processing_result = await loop.run_in_executor(
                self.thread_pool,
                self._process_chunk_sync,
                session,
                chunk
            )
            
            chunk.processing_time = time.time() - start_time
            session.chunks_processed += 1
            session.bytes_processed += chunk.chunk_size
            
            if processing_result.get('success', False):
                chunk.status = ChunkStatus.COMPLETED
            else:
                chunk.status = ChunkStatus.FAILED
                session.error_count += 1
            
            # Send processing update
            await self._send_processing_update(session, chunk, processing_result)
            
        except Exception as e:
            chunk.status = ChunkStatus.FAILED
            chunk.processing_time = time.time() - start_time if 'start_time' in locals() else 0
            session.error_count += 1
            self.logger.error(f"Chunk processing failed: {str(e)}")
    
    def _process_chunk_sync(self, session: StreamingSession, chunk: StreamingChunk) -> Dict[str, Any]:
        """Synchronous chunk processing (runs in thread pool)"""



        try:
            # Decompress if needed
            chunk_data = chunk.data
            if self.config.enable_compression:
                try:
                    chunk_data = gzip.decompress(chunk_data)
                except:
                    pass  # Data might not be compressed
            
            # Process based on content type
            processing_result = {
                'success': True,
                'chunk_id': chunk.chunk_id,
                'processed_size': len(chunk_data),
                'metadata': {}
            }
            
            # Content-specific processing
            if session.content_type.startswith('image/'):
                processing_result.update(self._process_image_chunk(chunk_data))
            elif session.content_type.startswith('audio/'):
                processing_result.update(self._process_audio_chunk(chunk_data))
            elif session.content_type.startswith('video/'):
                processing_result.update(self._process_video_chunk(chunk_data))
            elif session.content_type.startswith('text/'):
                processing_result.update(self._process_text_chunk(chunk_data))
            
            return processing_result
            
        except Exception as e:
            return {
                'success': False,
                'chunk_id': chunk.chunk_id,
                'error': str(e)
            }
    
    def _process_image_chunk(self, chunk_data: bytes) -> Dict[str, Any]:
        """Process image chunk data"""



        try:
            # Try to load as image
            import io
            image = Image.open(io.BytesIO(chunk_data))
            
            return {
                'format': image.format,
                'size': image.size,
                'mode': image.mode,
                'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
            }
        except Exception as e:
            return {'error': f"Image processing failed: {str(e)}"}
    
    def _process_audio_chunk(self, chunk_data: bytes) -> Dict[str, Any]:
        """Process audio chunk data"""



        try:
            # Basic audio chunk validation
            # In a full implementation, this would use librosa or similar
            return {
                'chunk_size': len(chunk_data),
                'audio_format': 'detected'  # Placeholder for format detection
            }
        except Exception as e:
            return {'error': f"Audio processing failed: {str(e)}"}
    
    def _process_video_chunk(self, chunk_data: bytes) -> Dict[str, Any]:
        """Process video chunk data"""



        try:
            # Basic video chunk validation
            return {
                'chunk_size': len(chunk_data),
                'video_format': 'detected'  # Placeholder for format detection
            }
        except Exception as e:
            return {'error': f"Video processing failed: {str(e)}"}
    
    def _process_text_chunk(self, chunk_data: bytes) -> Dict[str, Any]:
        """Process text chunk data"""



        try:
            # Decode text
            text = chunk_data.decode('utf-8')
            
            return {
                'char_count': len(text),
                'word_count': len(text.split()),
                'encoding': 'utf-8',
                'has_special_chars': any(ord(c) > 127 for c in text)
            }
        except Exception as e:
            return {'error': f"Text processing failed: {str(e)}"}
    
    async def _validate_chunk(self, session: StreamingSession, chunk: StreamingChunk) -> Dict[str, Any]:
        """Validate chunk data"""



        try:
            validation_result = {'valid': True, 'errors': []}
            
            # Size validation
            if chunk.chunk_size > self.config.max_chunk_size:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Chunk size {chunk.chunk_size} exceeds maximum {self.config.max_chunk_size}")
            
            # Sequence validation
            expected_sequence = session.chunks_received
            if chunk.sequence_number != expected_sequence:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Invalid sequence number: expected {expected_sequence}, got {chunk.sequence_number}")
            
            # Content type validation
            if session.content_type != 'auto':
                # Validate against expected content type
                pass  # Implement MIME type validation
            
            return validation_result
            
        except Exception as e:
            return {'valid': False, 'errors': [f"Validation error: {str(e)}"]}
    
    async def _send_chunk_ack(self, session: StreamingSession, chunk: StreamingChunk):
        """Send chunk acknowledgment"""



        try:
            ack_message = {
                'type': 'chunk_ack',
                'chunk_id': chunk.chunk_id,
                'sequence_number': chunk.sequence_number,
                'status': chunk.status.value,
                'timestamp': chunk.timestamp.isoformat()
            }
            
            await session.websocket.send(json.dumps(ack_message))
            
        except Exception as e:
            self.logger.error(f"Error sending chunk acknowledgment: {str(e)}")
    
    async def _send_processing_update(self, session: StreamingSession, 
                                    chunk: StreamingChunk, 
                                    processing_result: Dict[str, Any]):
        """Send processing update to client"""



        try:
            update_message = {
                'type': 'processing_update',
                'chunk_id': chunk.chunk_id,
                'status': chunk.status.value,
                'processing_time': chunk.processing_time,
                'result': processing_result,
                'session_progress': {
                    'chunks_processed': session.chunks_processed,
                    'chunks_received': session.chunks_received,
                    'bytes_processed': session.bytes_processed,
                    'bytes_received': session.bytes_received
                }
            }
            
            await session.websocket.send(json.dumps(update_message))
            
        except Exception as e:
            self.logger.error(f"Error sending processing update: {str(e)}")
    
    async def _send_error_message(self, session: StreamingSession, 
                                error_type: str, 
                                errors: List[str]):
        """Send error message to client"""



        try:
            error_message = {
                'type': 'error',
                'error_type': error_type,
                'errors': errors,
                'session_id': session.session_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            await session.websocket.send(json.dumps(error_message))
            
        except Exception as e:
            self.logger.error(f"Error sending error message: {str(e)}")
    
    async def _finalize_session(self, session: StreamingSession):
        """Finalize streaming session and create final content"""



        try:
            session.processing_stage = "finalizing"
            
            # Combine all chunks into final content
            final_content = await self._combine_chunks(session)
            
            if final_content:
                # Create ingestion request
                ingestion_request = IngestionRequest(
                    user_id=session.user_id,
                    file_data=final_content,
                    filename=session.filename,
                    content_type=session.content_type,
                    metadata=session.metadata,
                    priority=session.priority.value,
                    ai_analysis_enabled=True,
                    protection_enabled=True
                )
                
                # Process through content manager
                ingestion_result = await self.content_manager.ingest_content(ingestion_request)
                
                # Create streaming result
                streaming_result = StreamingResult(
                    session_id=session.session_id,
                    success=ingestion_result.success,
                    content_id=ingestion_result.content_id,
                    total_chunks=session.chunks_received,
                    processed_chunks=session.chunks_processed,
                    failed_chunks=session.chunks_received - session.chunks_processed,
                    total_bytes=session.bytes_received,
                    processing_time=time.time() - session.created_at.timestamp(),
                    quality_metrics=ingestion_result.quality_metrics.__dict__ if ingestion_result.quality_metrics else {},
                    final_metadata=ingestion_result.metadata
                )
                
                # Send completion message
                await self._send_session_complete(session, streaming_result)
                
            else:
                await self._send_error_message(session, "finalization_failed", ["Could not combine chunks"])
            
        except Exception as e:
            self.logger.error(f"Session finalization failed: {str(e)}")
            await self._send_error_message(session, "finalization_error", [str(e)])
    
    async def _combine_chunks(self, session: StreamingSession) -> Optional[bytes]:
        """Combine all session chunks into final content"""



        try:
            # Sort chunks by sequence number
            sorted_chunks = sorted(session.buffer, key=lambda c: c.sequence_number)
            
            # Combine chunk data
            combined_data = b''
            for chunk in sorted_chunks:
                if chunk.status == ChunkStatus.COMPLETED:
                    combined_data += chunk.data
            
            return combined_data if combined_data else None
            
        except Exception as e:
            self.logger.error(f"Error combining chunks: {str(e)}")
            return None
    
    async def _send_session_complete(self, session: StreamingSession, result: StreamingResult):
        """Send session completion message"""



        try:
            completion_message = {
                'type': 'session_complete',
                'session_id': session.session_id,
                'success': result.success,
                'content_id': result.content_id,
                'statistics': {
                    'total_chunks': result.total_chunks,
                    'processed_chunks': result.processed_chunks,
                    'failed_chunks': result.failed_chunks,
                    'total_bytes': result.total_bytes,
                    'processing_time': result.processing_time,
                    'throughput_mbps': result.throughput_mbps
                },
                'quality_metrics': result.quality_metrics
            }
            
            await session.websocket.send(json.dumps(completion_message))
            
        except Exception as e:
            self.logger.error(f"Error sending completion message: {str(e)}")
    
    async def _close_session(self, session_id: str, reason: str):
        """Close streaming session"""



        try:
            async with self.session_lock:
                session = self.active_sessions.get(session_id)
                if not session:
                    return
                
                session.is_active = False
                
                # Close WebSocket connection
                if not session.websocket.closed:
                    await session.websocket.close(code=1000, reason=reason)
                
                # Remove from active sessions
                del self.active_sessions[session_id]
                self.global_metrics['active_sessions'] = len(self.active_sessions)
                
                # Remove from Redis
                await self._remove_session_from_redis(session_id)
                
                self.logger.info(f"Closed session {session_id}: {reason}")
                
        except Exception as e:
            self.logger.error(f"Error closing session {session_id}: {str(e)}")
    
    async def _store_session_in_redis(self, session: StreamingSession):
        """Store session data in Redis"""



        try:
            session_data = {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'content_type': session.content_type,
                'filename': session.filename,
                'created_at': session.created_at.isoformat(),
                'metadata': session.metadata
            }
            
            await self.redis.setex(
                f"streaming_session:{session.session_id}",
                3600,  # 1 hour expiry
                json.dumps(session_data)
            )
            
        except Exception as e:
            self.logger.error(f"Error storing session in Redis: {str(e)}")
    
    async def _remove_session_from_redis(self, session_id: str):
        """Remove session data from Redis"""



        try:
            await self.redis.delete(f"streaming_session:{session_id}")
        except Exception as e:
            self.logger.error(f"Error removing session from Redis: {str(e)}")
    
    async def get_active_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get active streaming sessions.
        
        Args:
            user_id: Filter by user ID (optional)
            
        Returns:
            List of active session information
        """



        try:
            sessions = []
            
            async with self.session_lock:
                for session in self.active_sessions.values():
                    if user_id is None or session.user_id == user_id:
                        session_info = {
                            'session_id': session.session_id,
                            'user_id': session.user_id,
                            'content_type': session.content_type,
                            'filename': session.filename,
                            'mode': session.mode.value,
                            'quality': session.quality.value,
                            'priority': session.priority.value,
                            'created_at': session.created_at.isoformat(),
                            'last_activity': session.last_activity.isoformat(),
                            'chunks_received': session.chunks_received,
                            'chunks_processed': session.chunks_processed,
                            'bytes_received': session.bytes_received,
                            'bytes_processed': session.bytes_processed,
                            'processing_stage': session.processing_stage,
                            'error_count': session.error_count
                        }
                        sessions.append(session_info)
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Error getting active sessions: {str(e)}")
            return []
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed session status"""



        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return None
            
            # Calculate progress percentage
            progress_percentage = 0.0
            if session.total_size and session.total_size > 0:
                progress_percentage = (session.bytes_received / session.total_size) * 100
            
            # Calculate throughput
            elapsed_time = (datetime.now(timezone.utc) - session.created_at).total_seconds()
            throughput_mbps = (session.bytes_received / (1024 * 1024)) / max(elapsed_time, 1)
            
            return {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'is_active': session.is_active,
                'processing_stage': session.processing_stage,
                'progress': {
                    'chunks_received': session.chunks_received,
                    'chunks_processed': session.chunks_processed,
                    'bytes_received': session.bytes_received,
                    'bytes_processed': session.bytes_processed,
                    'progress_percentage': progress_percentage
                },
                'performance': {
                    'throughput_mbps': throughput_mbps,
                    'elapsed_time': elapsed_time,
                    'error_count': session.error_count,
                    'last_error': session.last_error
                },
                'configuration': {
                    'mode': session.mode.value,
                    'quality': session.quality.value,
                    'priority': session.priority.value,
                    'content_type': session.content_type,
                    'filename': session.filename
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting session status: {str(e)}")
            return None
    
    async def get_server_metrics(self) -> Dict[str, Any]:
        """Get server performance metrics"""



        try:
            uptime = (datetime.now(timezone.utc) - self.global_metrics['uptime_start']).total_seconds()
            
            return {
                'server_status': 'running' if self.is_running else 'stopped',
                'uptime_seconds': uptime,
                'active_sessions': self.global_metrics['active_sessions'],
                'total_sessions': self.global_metrics['total_sessions'],
                'total_bytes_processed': self.global_metrics['total_bytes_processed'],
                'average_throughput': self.global_metrics['average_throughput'],
                'configuration': {
                    'max_connections': self.config.max_connections,
                    'chunk_size': self.config.chunk_size,
                    'processing_threads': self.config.processing_threads,
                    'buffer_size': self.config.buffer_size
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting server metrics: {str(e)}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on streaming engine"""



        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'components': {}
            }
            
            # Check server status
            health_status['components']['server'] = {
                'status': 'healthy' if self.is_running else 'unhealthy',
                'port': self.config.port,
                'active_connections': len(self.active_sessions)
            }
            
            # Check Redis connection
            try:
                await self.redis.ping()
                health_status['components']['redis'] = {'status': 'healthy'}
            except Exception as e:
                health_status['components']['redis'] = {'status': 'unhealthy', 'error': str(e)}
                health_status['status'] = 'degraded'
            
            # Check thread pool
            health_status['components']['thread_pool'] = {
                'status': 'healthy',
                'max_workers': self.config.processing_threads,
                'active_threads': self.thread_pool._threads if hasattr(self.thread_pool, '_threads') else 0
            }
            
            return health_status
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }


# Export classes
__all__ = [
    'StreamingIngestionEngine',
    'StreamingConfiguration',
    'StreamingSession',
    'StreamingChunk',
    'StreamingResult',
    'StreamingMode',
    'StreamingQuality',
    'StreamingPriority',
    'ChunkStatus'
]
