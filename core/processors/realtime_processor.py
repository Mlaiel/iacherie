"""Realtime Processor Module - IA-Influencer-Agent Platform

Industrial-grade realtime processing engine for content creators and influencers.
Handles live streaming analysis, real-time content processing, and instant feedback.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Any unauthorized use, copying, 
distribution, or commercialization without explicit written permission is 
strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
================================================================================
"""
import asyncio
import logging
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import weakref
from collections import deque

# Real-time processing imports
try:
    import numpy as np
    import cv2
    REALTIME_VISION_AVAILABLE = True
except ImportError:
    REALTIME_VISION_AVAILABLE = False

try:
    import librosa
    import soundfile as sf
    REALTIME_AUDIO_AVAILABLE = True
except ImportError:
    REALTIME_AUDIO_AVAILABLE = False

# WebSocket and streaming
try:
    import websockets
    import asyncio_mqtt
    STREAMING_LIBS_AVAILABLE = True
except ImportError:
    STREAMING_LIBS_AVAILABLE = False

# Import processors for real-time analysis
from .audio_processor import AudioProcessor
from .video_processor import VideoProcessor  
from .image_processor import ImageProcessor
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)


class StreamType(str, Enum):
    """Types of real-time streams"""    VIDEO_STREAM = "video_stream"
    AUDIO_STREAM = "audio_stream"
    TEXT_STREAM = "text_stream"
    MIXED_MEDIA = "mixed_media"
    LIVE_BROADCAST = "live_broadcast"
    INTERACTIVE_SESSION = "interactive_session"
    GAMING_STREAM = "gaming_stream"
    EDUCATIONAL_STREAM = "educational_stream"
    MUSIC_STREAM = "music_stream"
    PODCAST_STREAM = "podcast_stream"


class ProcessingMode(str, Enum):
    """Real-time processing modes"""    LOW_LATENCY = "low_latency"
    HIGH_QUALITY = "high_quality"
    BALANCED = "balanced"
    ENERGY_EFFICIENT = "energy_efficient"
    ULTRA_FAST = "ultra_fast"


class StreamStatus(str, Enum):
    """Stream processing status"""    CONNECTING = "connecting"
    CONNECTED = "connected"
    PROCESSING = "processing"
    PAUSED = "paused"
    BUFFERING = "buffering"
    ERROR = "error"
    DISCONNECTED = "disconnected"
    TERMINATED = "terminated"


class AlertType(str, Enum):
    """Real-time alert types"""    QUALITY_ISSUE = "quality_issue"
    CONTENT_WARNING = "content_warning"
    PERFORMANCE_ISSUE = "performance_issue"
    TECHNICAL_ERROR = "technical_error"
    ENGAGEMENT_SPIKE = "engagement_spike"
    AUDIO_PROBLEM = "audio_problem"
    VIDEO_PROBLEM = "video_problem"
    CONTENT_VIOLATION = "content_violation"


@dataclass
class RealtimeProcessingConfig:
    """Configuration for real-time processing"""    # Processing parameters
    processing_mode: ProcessingMode = ProcessingMode.BALANCED
    target_latency_ms: int = 100
    max_latency_ms: int = 500
    buffer_size_ms: int = 200
    
    # Frame/chunk settings
    video_fps: int = 30
    video_resolution: tuple = (1920, 1080)
    audio_sample_rate: int = 44100
    audio_chunk_size: int = 1024
    
    # Quality settings
    enable_quality_monitoring: bool = True
    quality_check_interval: int = 5  # seconds
    min_quality_threshold: float = 0.7
    
    # Analytics
    enable_realtime_analytics: bool = True
    analytics_update_interval: int = 1  # seconds
    enable_sentiment_analysis: bool = True
    enable_engagement_tracking: bool = True
    
    # Alerts and notifications
    enable_alerts: bool = True
    alert_cooldown_seconds: int = 30
    enable_auto_corrections: bool = True
    
    # Performance optimization
    enable_adaptive_processing: bool = True
    cpu_usage_limit: float = 0.8
    memory_usage_limit: float = 0.8
    enable_gpu_acceleration: bool = True
    
    # Output and streaming
    enable_enhanced_output: bool = True
    output_format: str = "webm"
    streaming_bitrate: int = 2000  # kbps
    
    # WebSocket settings
    websocket_port: int = 8765
    max_connections: int = 100
    ping_interval: int = 20
    
    # Storage and recording
    enable_recording: bool = False
    recording_quality: str = "high"
    recording_format: str = "mp4"
    max_recording_duration: int = 3600  # 1 hour


@dataclass  
class StreamMetadata:
    """Metadata for a stream"""    stream_id: str
    stream_type: StreamType
    title: Optional[str] = None
    description: Optional[str] = None
    creator_id: Optional[str] = None
    creator_name: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    language: Optional[str] = None
    target_audience: Optional[str] = None
    content_rating: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    expected_duration: Optional[int] = None  # seconds


@dataclass
class StreamAnalytics:
    """Real-time stream analytics"""    # Engagement metrics
    viewer_count: int = 0
    peak_viewers: int = 0
    average_watch_time: float = 0.0
    engagement_rate: float = 0.0
    
    # Content metrics
    sentiment_score: float = 0.0
    sentiment_trend: str = "neutral"
    emotion_distribution: Dict[str, float] = field(default_factory=dict)
    
    # Quality metrics
    audio_quality: float = 0.0
    video_quality: float = 0.0
    overall_quality: float = 0.0
    
    # Performance metrics
    latency_ms: float = 0.0
    frame_drops: int = 0
    buffer_health: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    
    # Interaction metrics
    comments_per_minute: float = 0.0
    likes_per_minute: float = 0.0
    shares_count: int = 0
    
    # Technical metrics
    bitrate: float = 0.0
    resolution: tuple = (0, 0)
    fps: float = 0.0
    
    # Timestamps
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class StreamAlert:
    """Real-time alert"""    alert_id: str
    alert_type: AlertType
    severity: str  # low, medium, high, critical
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    suggested_actions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class StreamFrame:
    """Individual frame in a stream"""    frame_id: str
    timestamp: float
    frame_type: str  # video, audio, text, metadata
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_results: Dict[str, Any] = field(default_factory=dict)
    quality_score: Optional[float] = None


class RealtimeStream:
    """    🎥 REALTIME STREAM HANDLER
    
    Manages individual real-time streams with processing and analytics.
    """    
    def __init__(
        self,
        stream_id: str,
        stream_type: StreamType,
        metadata: StreamMetadata,
        config: RealtimeProcessingConfig,
        processor_instances: Dict[str, Any]
    ):
        self.stream_id = stream_id
        self.stream_type = stream_type
        self.metadata = metadata
        self.config = config
        self.processors = processor_instances
        
        self.logger = logging.getLogger(f"{__name__}.RealtimeStream.{stream_id}")
        
        # Stream state
        self.status = StreamStatus.CONNECTING
        self.connected_at: Optional[datetime] = None
        self.last_frame_time = 0.0
        
        # Processing buffers
        self.video_buffer = deque(maxlen=30)  # 1 second at 30fps
        self.audio_buffer = deque(maxlen=100)  # Audio chunks
        self.text_buffer = deque(maxlen=50)   # Text messages
        
        # Analytics and monitoring
        self.analytics = StreamAnalytics()
        self.alerts: List[StreamAlert] = []
        self.frame_count = 0
        self.processing_times = deque(maxlen=100)
        
        # WebSocket connections
        self.websocket_clients = set()
        self.websocket_server = None
        
        # Async tasks
        self.processing_task: Optional[asyncio.Task] = None
        self.analytics_task: Optional[asyncio.Task] = None
        self.quality_monitor_task: Optional[asyncio.Task] = None
        
        # Performance tracking
        self.performance_metrics = {
            "frames_processed": 0,
            "frames_dropped": 0,
            "average_latency": 0.0,
            "peak_latency": 0.0,
            "cpu_usage": 0.0,
            "memory_usage": 0.0
        }
    
    async def start(self) -> bool:
        """Start stream processing"""        try:
            self.logger.info(f"Starting stream {self.stream_id}")
            
            # Start WebSocket server
            if self.config.websocket_port:
                await self._start_websocket_server()
            
            # Start processing tasks
            self.processing_task = asyncio.create_task(self._processing_loop())
            self.analytics_task = asyncio.create_task(self._analytics_loop())
            self.quality_monitor_task = asyncio.create_task(self._quality_monitor_loop())
            
            self.status = StreamStatus.CONNECTED
            self.connected_at = datetime.now()
            
            self.logger.info(f"Stream {self.stream_id} started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Stream start failed: {e}")
            self.status = StreamStatus.ERROR
            return False
    
    async def stop(self):
        """Stop stream processing"""        try:
            self.status = StreamStatus.DISCONNECTED
            
            # Cancel tasks
            tasks = [self.processing_task, self.analytics_task, self.quality_monitor_task]
            for task in tasks:
                if task and not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*[t for t in tasks if t], return_exceptions=True)
            
            # Close WebSocket server
            if self.websocket_server:
                self.websocket_server.close()
                await self.websocket_server.wait_closed()
            
            self.logger.info(f"Stream {self.stream_id} stopped")
            
        except Exception as e:
            self.logger.error(f"Stream stop failed: {e}")
    
    async def process_frame(self, frame_data: Any, frame_type: str) -> Dict[str, Any]:
        """Process a single frame"""        start_time = time.time()
        
        try:
            frame_id = f"{self.stream_id}_{self.frame_count}"
            frame = StreamFrame(
                frame_id=frame_id,
                timestamp=start_time,
                frame_type=frame_type,
                data=frame_data
            )
            
            # Route to appropriate processor
            processing_result = {}
            
            if frame_type == "video" and self.processors.get("video"):
                processing_result = await self._process_video_frame(frame)
            elif frame_type == "audio" and self.processors.get("audio"):
                processing_result = await self._process_audio_frame(frame)
            elif frame_type == "text" and self.processors.get("text"):
                processing_result = await self._process_text_frame(frame)
            
            # Update frame with results
            frame.processing_results = processing_result
            frame.quality_score = processing_result.get("quality_score")
            
            # Add to appropriate buffer
            if frame_type == "video":
                self.video_buffer.append(frame)
            elif frame_type == "audio":
                self.audio_buffer.append(frame)
            elif frame_type == "text":
                self.text_buffer.append(frame)
            
            # Update metrics
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)
            self.frame_count += 1
            self.performance_metrics["frames_processed"] += 1
            
            # Check latency
            latency_ms = processing_time * 1000
            if latency_ms > self.config.max_latency_ms:
                await self._handle_latency_issue(latency_ms)
            
            # Broadcast to WebSocket clients
            if self.websocket_clients:
                await self._broadcast_frame_update(frame)
            
            return {
                "success": True,
                "frame_id": frame_id,
                "processing_time": processing_time,
                "quality_score": frame.quality_score,
                "results": processing_result
            }
            
        except Exception as e:
            self.logger.error(f"Frame processing failed: {e}")
            self.performance_metrics["frames_dropped"] += 1
            
            return {
                "success": False,
                "error_message": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def _process_video_frame(self, frame: StreamFrame) -> Dict[str, Any]:
        """Process video frame"""        try:
            video_processor = self.processors["video"]
            
            # Prepare video data
            if isinstance(frame.data, np.ndarray):
                # Direct numpy array
                video_data = frame.data
            else:
                # Convert to numpy array if needed
                video_data = np.array(frame.data)
            
            # Process with video processor
            # Note: This would need adaptation for real-time use
            result = await video_processor.analyze_video_content(
                video_data=video_data,
                options={
                    "real_time": True,
                    "quality_check": True,
                    "fast_mode": self.config.processing_mode == ProcessingMode.ULTRA_FAST
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Video frame processing failed: {e}")
            return {"error": str(e)}
    
    async def _process_audio_frame(self, frame: StreamFrame) -> Dict[str, Any]:
        """Process audio frame"""        try:
            audio_processor = self.processors["audio"]
            
            # Process with audio processor
            result = await audio_processor.analyze_audio_content(
                audio_data=frame.data,
                sample_rate=self.config.audio_sample_rate,
                options={
                    "real_time": True,
                    "chunk_size": self.config.audio_chunk_size,
                    "quality_check": True
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Audio frame processing failed: {e}")
            return {"error": str(e)}
    
    async def _process_text_frame(self, frame: StreamFrame) -> Dict[str, Any]:
        """Process text frame"""        try:
            text_processor = self.processors["text"]
            
            # Process with text processor
            result = await text_processor.analyze_text(
                text=frame.data,
                options={
                    "real_time": True,
                    "sentiment_analysis": self.config.enable_sentiment_analysis,
                    "fast_mode": True
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Text frame processing failed: {e}")
            return {"error": str(e)}
    
    async def _processing_loop(self):
        """Main processing loop"""        while self.status in [StreamStatus.CONNECTED, StreamStatus.PROCESSING]:
            try:
                # Adaptive processing based on buffer health
                await self._adaptive_processing()
                
                # Small delay to prevent CPU overload
                await asyncio.sleep(0.001)  # 1ms
                
            except Exception as e:
                self.logger.error(f"Processing loop error: {e}")
                await asyncio.sleep(0.1)
    
    async def _analytics_loop(self):
        """Analytics update loop"""        while self.status in [StreamStatus.CONNECTED, StreamStatus.PROCESSING]:
            try:
                await self._update_analytics()
                await asyncio.sleep(self.config.analytics_update_interval)
                
            except Exception as e:
                self.logger.error(f"Analytics loop error: {e}")
                await asyncio.sleep(5)
    
    async def _quality_monitor_loop(self):
        """Quality monitoring loop"""        while self.status in [StreamStatus.CONNECTED, StreamStatus.PROCESSING]:
            try:
                await self._monitor_quality()
                await asyncio.sleep(self.config.quality_check_interval)
                
            except Exception as e:
                self.logger.error(f"Quality monitor error: {e}")
                await asyncio.sleep(10)
    
    async def _adaptive_processing(self):
        """Adaptive processing based on current conditions"""        try:
            # Check buffer health
            video_buffer_health = len(self.video_buffer) / self.video_buffer.maxlen
            audio_buffer_health = len(self.audio_buffer) / self.audio_buffer.maxlen
            
            # Adjust processing mode based on conditions
            if video_buffer_health > 0.9 or audio_buffer_health > 0.9:
                # Buffers are getting full - speed up processing
                if self.config.processing_mode != ProcessingMode.ULTRA_FAST:
                    self.config.processing_mode = ProcessingMode.ULTRA_FAST
                    await self._create_alert(
                        AlertType.PERFORMANCE_ISSUE,
                        "high",
                        "High buffer usage detected - switched to ultra-fast mode"
                    )
            elif video_buffer_health < 0.3 and audio_buffer_health < 0.3:
                # Buffers are low - can use higher quality
                if self.config.processing_mode == ProcessingMode.ULTRA_FAST:
                    self.config.processing_mode = ProcessingMode.BALANCED
            
        except Exception as e:
            self.logger.error(f"Adaptive processing failed: {e}")
    
    async def _update_analytics(self):
        """Update real-time analytics"""        try:
            current_time = time.time()
            
            # Calculate processing metrics
            if self.processing_times:
                avg_processing_time = sum(self.processing_times) / len(self.processing_times)
                self.analytics.latency_ms = avg_processing_time * 1000
            
            # Calculate frame rate
            if self.frame_count > 0 and self.connected_at:
                elapsed_time = (datetime.now() - self.connected_at).total_seconds()
                self.analytics.fps = self.frame_count / elapsed_time if elapsed_time > 0 else 0
            
            # Quality metrics from recent frames
            recent_video_frames = list(self.video_buffer)[-10:]  # Last 10 frames
            if recent_video_frames:
                quality_scores = [
                    f.quality_score for f in recent_video_frames 
                    if f.quality_score is not None
                ]
                if quality_scores:
                    self.analytics.video_quality = sum(quality_scores) / len(quality_scores)
            
            # Update sentiment from text frames
            recent_text_frames = list(self.text_buffer)[-20:]  # Last 20 messages
            if recent_text_frames:
                sentiment_scores = []
                for frame in recent_text_frames:
                    sentiment = frame.processing_results.get("sentiment_analysis", {})
                    if sentiment.get("compound_score") is not None:
                        sentiment_scores.append(sentiment["compound_score"])
                
                if sentiment_scores:
                    self.analytics.sentiment_score = sum(sentiment_scores) / len(sentiment_scores)
                    
                    # Determine trend
                    if len(sentiment_scores) >= 2:
                        recent_avg = sum(sentiment_scores[-5:]) / min(5, len(sentiment_scores))
                        older_avg = sum(sentiment_scores[:-5]) / max(1, len(sentiment_scores) - 5)
                        
                        if recent_avg > older_avg + 0.1:
                            self.analytics.sentiment_trend = "improving"
                        elif recent_avg < older_avg - 0.1:
                            self.analytics.sentiment_trend = "declining"
                        else:
                            self.analytics.sentiment_trend = "stable"
            
            # Update overall quality
            quality_components = [
                self.analytics.video_quality,
                self.analytics.audio_quality
            ]
            quality_components = [q for q in quality_components if q > 0]
            
            if quality_components:
                self.analytics.overall_quality = sum(quality_components) / len(quality_components)
            
            # Update timestamp
            self.analytics.last_updated = datetime.now()
            
            # Broadcast analytics to WebSocket clients
            if self.websocket_clients:
                await self._broadcast_analytics_update()
            
        except Exception as e:
            self.logger.error(f"Analytics update failed: {e}")
    
    async def _monitor_quality(self):
        """Monitor stream quality and create alerts"""        try:
            # Check overall quality
            if self.analytics.overall_quality < self.config.min_quality_threshold:
                await self._create_alert(
                    AlertType.QUALITY_ISSUE,
                    "medium",
                    f"Overall quality below threshold: {self.analytics.overall_quality:.2f}"
                )
            
            # Check latency
            if self.analytics.latency_ms > self.config.max_latency_ms:
                await self._create_alert(
                    AlertType.PERFORMANCE_ISSUE,
                    "high",
                    f"High latency detected: {self.analytics.latency_ms:.1f}ms"
                )
            
            # Check frame drops
            drop_rate = (
                self.performance_metrics["frames_dropped"] / 
                max(1, self.performance_metrics["frames_processed"])
            )
            
            if drop_rate > 0.05:  # More than 5% frame drops
                await self._create_alert(
                    AlertType.PERFORMANCE_ISSUE,
                    "high",
                    f"High frame drop rate: {drop_rate:.1%}"
                )
            
        except Exception as e:
            self.logger.error(f"Quality monitoring failed: {e}")
    
    async def _create_alert(
        self,
        alert_type: AlertType,
        severity: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Create and broadcast an alert"""        try:
            # Check cooldown
            recent_alerts = [
                a for a in self.alerts
                if a.alert_type == alert_type and 
                (datetime.now() - a.timestamp).total_seconds() < self.config.alert_cooldown_seconds
            ]
            
            if recent_alerts:
                return  # Skip duplicate alert
            
            alert = StreamAlert(
                alert_id=str(uuid.uuid4()),
                alert_type=alert_type,
                severity=severity,
                message=message,
                details=details or {}
            )
            
            self.alerts.append(alert)
            
            # Broadcast to WebSocket clients
            if self.websocket_clients:
                await self._broadcast_alert(alert)
            
            self.logger.warning(f"Alert created: {alert.message}")
            
        except Exception as e:
            self.logger.error(f"Alert creation failed: {e}")
    
    async def _handle_latency_issue(self, latency_ms: float):
        """Handle high latency"""        try:
            if self.config.enable_auto_corrections:
                # Auto-adjust processing mode
                if latency_ms > self.config.max_latency_ms * 2:
                    self.config.processing_mode = ProcessingMode.ULTRA_FAST
                elif latency_ms > self.config.max_latency_ms * 1.5:
                    self.config.processing_mode = ProcessingMode.LOW_LATENCY
            
        except Exception as e:
            self.logger.error(f"Latency handling failed: {e}")
    
    async def _start_websocket_server(self):
        """Start WebSocket server for real-time communication"""        try:
            if not STREAMING_LIBS_AVAILABLE:
                self.logger.warning("WebSocket libraries not available")
                return
            
            async def handle_client(websocket, path):
                self.websocket_clients.add(websocket)
                try:
                    # Send initial analytics
                    await websocket.send(json.dumps({
                        "type": "analytics",
                        "data": self.analytics.__dict__
                    }))
                    
                    # Keep connection alive
                    await websocket.wait_closed()
                finally:
                    self.websocket_clients.discard(websocket)
            
            self.websocket_server = await websockets.serve(
                handle_client,
                "localhost",
                self.config.websocket_port + hash(self.stream_id) % 1000
            )
            
        except Exception as e:
            self.logger.error(f"WebSocket server start failed: {e}")
    
    async def _broadcast_frame_update(self, frame: StreamFrame):
        """Broadcast frame update to WebSocket clients"""        try:
            if not self.websocket_clients:
                return
            
            frame_data = {
                "type": "frame_update",
                "data": {
                    "frame_id": frame.frame_id,
                    "timestamp": frame.timestamp,
                    "frame_type": frame.frame_type,
                    "quality_score": frame.quality_score,
                    "processing_results": frame.processing_results
                }
            }
            
            disconnected_clients = set()
            for client in self.websocket_clients:
                try:
                    await client.send(json.dumps(frame_data, default=str))
                except:
                    disconnected_clients.add(client)
            
            # Remove disconnected clients
            self.websocket_clients -= disconnected_clients
            
        except Exception as e:
            self.logger.error(f"Frame broadcast failed: {e}")
    
    async def _broadcast_analytics_update(self):
        """Broadcast analytics update to WebSocket clients"""        try:
            if not self.websocket_clients:
                return
            
            analytics_data = {
                "type": "analytics_update",
                "data": self.analytics.__dict__
            }
            
            disconnected_clients = set()
            for client in self.websocket_clients:
                try:
                    await client.send(json.dumps(analytics_data, default=str))
                except:
                    disconnected_clients.add(client)
            
            self.websocket_clients -= disconnected_clients
            
        except Exception as e:
            self.logger.error(f"Analytics broadcast failed: {e}")
    
    async def _broadcast_alert(self, alert: StreamAlert):
        """Broadcast alert to WebSocket clients"""        try:
            if not self.websocket_clients:
                return
            
            alert_data = {
                "type": "alert",
                "data": alert.__dict__
            }
            
            disconnected_clients = set()
            for client in self.websocket_clients:
                try:
                    await client.send(json.dumps(alert_data, default=str))
                except:
                    disconnected_clients.add(client)
            
            self.websocket_clients -= disconnected_clients
            
        except Exception as e:
            self.logger.error(f"Alert broadcast failed: {e}")


class RealtimeProcessor:
    """    ⚡ ENTERPRISE REALTIME PROCESSOR
    
    Industrial-grade real-time processing engine with ultra-low latency,
    adaptive quality, and comprehensive monitoring capabilities.
    """    
    def __init__(
        self,
        db_session,
        redis_client,
        config: Optional[RealtimeProcessingConfig] = None
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.config = config or RealtimeProcessingConfig()
        self.logger = logging.getLogger(f"{__name__}.RealtimeProcessor")
        
        # Individual processors
        self.audio_processor: Optional[AudioProcessor] = None
        self.video_processor: Optional[VideoProcessor] = None
        self.image_processor: Optional[ImageProcessor] = None
        self.text_processor: Optional[TextProcessor] = None
        
        # Stream management
        self._active_streams: Dict[str, RealtimeStream] = {}
        self._stream_registry = weakref.WeakValueDictionary()
        
        # Performance monitoring
        self._global_metrics = {
            "total_streams": 0,
            "active_streams": 0,
            "total_frames_processed": 0,
            "average_latency": 0.0,
            "cpu_usage": 0.0,
            "memory_usage": 0.0
        }
        
        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        self._initialized = False
        self._shutdown_event = asyncio.Event()
        
        if not REALTIME_VISION_AVAILABLE:
            self.logger.warning("Real-time vision processing not available")
        
        if not REALTIME_AUDIO_AVAILABLE:
            self.logger.warning("Real-time audio processing not available")
        
        if not STREAMING_LIBS_AVAILABLE:
            self.logger.warning("Streaming libraries not available")
    
    async def initialize(self) -> bool:
        """Initialize the real-time processor"""        try:
            # Initialize individual processors
            self.audio_processor = AudioProcessor(
                db_session=self.db_session,
                redis_client=self.redis_client
            )
            await self.audio_processor.initialize()
            
            self.video_processor = VideoProcessor(
                db_session=self.db_session,
                redis_client=self.redis_client
            )
            await self.video_processor.initialize()
            
            self.image_processor = ImageProcessor(
                db_session=self.db_session,
                redis_client=self.redis_client
            )
            await self.image_processor.initialize()
            
            self.text_processor = TextProcessor(
                db_session=self.db_session,
                redis_client=self.redis_client
            )
            await self.text_processor.initialize()
            
            # Start background tasks
            self._monitoring_task = asyncio.create_task(self._monitor_system())
            self._cleanup_task = asyncio.create_task(self._cleanup_inactive_streams())
            
            self._initialized = True
            self.logger.info("✅ Real-time processor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize real-time processor: {e}")
            return False
    
    async def create_stream(
        self,
        stream_type: StreamType,
        metadata: StreamMetadata,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Create a new real-time stream
        
        Args:
            stream_type: Type of stream to create
            metadata: Stream metadata
            options: Additional options
            
        Returns:
            Stream creation result
        """        try:
            if not self._initialized:
                await self.initialize()
            
            # Create stream
            stream_id = metadata.stream_id
            
            # Prepare processor instances
            processor_instances = {
                "audio": self.audio_processor,
                "video": self.video_processor,
                "image": self.image_processor,
                "text": self.text_processor
            }
            
            # Create stream instance
            stream = RealtimeStream(
                stream_id=stream_id,
                stream_type=stream_type,
                metadata=metadata,
                config=self.config,
                processor_instances=processor_instances
            )
            
            # Start stream
            success = await stream.start()
            
            if success:
                self._active_streams[stream_id] = stream
                self._stream_registry[stream_id] = stream
                self._global_metrics["total_streams"] += 1
                self._global_metrics["active_streams"] = len(self._active_streams)
                
                self.logger.info(f"Created stream {stream_id}")
                
                return {
                    "success": True,
                    "stream_id": stream_id,
                    "websocket_port": self.config.websocket_port + hash(stream_id) % 1000,
                    "analytics_endpoint": f"/streams/{stream_id}/analytics",
                    "status": stream.status.value
                }
            else:
                return {
                    "success": False,
                    "error_message": "Failed to start stream"
                }
                
        except Exception as e:
            self.logger.error(f"Stream creation failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def process_stream_frame(
        self,
        stream_id: str,
        frame_data: Any,
        frame_type: str
    ) -> Dict[str, Any]:
        """        Process a frame in a real-time stream
        
        Args:
            stream_id: Stream identifier
            frame_data: Frame data
            frame_type: Type of frame (video, audio, text)
            
        Returns:
            Processing result
        """        try:
            if stream_id not in self._active_streams:
                return {
                    "success": False,
                    "error_message": "Stream not found"
                }
            
            stream = self._active_streams[stream_id]
            
            # Process frame
            result = await stream.process_frame(frame_data, frame_type)
            
            # Update global metrics
            self._global_metrics["total_frames_processed"] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Stream frame processing failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def get_stream_analytics(self, stream_id: str) -> Dict[str, Any]:
        """Get real-time analytics for a stream"""        try:
            if stream_id not in self._active_streams:
                return {
                    "success": False,
                    "error_message": "Stream not found"
                }
            
            stream = self._active_streams[stream_id]
            
            return {
                "success": True,
                "stream_id": stream_id,
                "analytics": stream.analytics.__dict__,
                "performance_metrics": stream.performance_metrics,
                "alerts": [alert.__dict__ for alert in stream.alerts[-10:]],  # Last 10 alerts
                "status": stream.status.value
            }
            
        except Exception as e:
            self.logger.error(f"Stream analytics retrieval failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def stop_stream(self, stream_id: str) -> Dict[str, Any]:
        """Stop a real-time stream"""        try:
            if stream_id not in self._active_streams:
                return {
                    "success": False,
                    "error_message": "Stream not found"
                }
            
            stream = self._active_streams[stream_id]
            await stream.stop()
            
            # Remove from active streams
            del self._active_streams[stream_id]
            self._global_metrics["active_streams"] = len(self._active_streams)
            
            return {
                "success": True,
                "message": "Stream stopped successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Stream stop failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def list_active_streams(self) -> Dict[str, Any]:
        """List all active streams"""        try:
            streams = []
            
            for stream_id, stream in self._active_streams.items():
                streams.append({
                    "stream_id": stream_id,
                    "stream_type": stream.stream_type.value,
                    "status": stream.status.value,
                    "connected_at": stream.connected_at.isoformat() if stream.connected_at else None,
                    "frame_count": stream.frame_count,
                    "analytics": {
                        "viewer_count": stream.analytics.viewer_count,
                        "quality": stream.analytics.overall_quality,
                        "latency": stream.analytics.latency_ms
                    }
                })
            
            return {
                "success": True,
                "streams": streams,
                "total_count": len(streams)
            }
            
        except Exception as e:
            self.logger.error(f"Stream listing failed: {e}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def get_global_metrics(self) -> Dict[str, Any]:
        """Get global real-time processing metrics"""        return {
            "success": True,
            "metrics": self._global_metrics,
            "config": self.config.__dict__,
            "system_info": {
                "realtime_vision_available": REALTIME_VISION_AVAILABLE,
                "realtime_audio_available": REALTIME_AUDIO_AVAILABLE,
                "streaming_libs_available": STREAMING_LIBS_AVAILABLE
            }
        }
    
    async def _monitor_system(self):
        """Monitor system performance"""        while not self._shutdown_event.is_set():
            try:
                # Calculate average latency across all streams
                all_latencies = []
                for stream in self._active_streams.values():
                    if stream.analytics.latency_ms > 0:
                        all_latencies.append(stream.analytics.latency_ms)
                
                if all_latencies:
                    self._global_metrics["average_latency"] = sum(all_latencies) / len(all_latencies)
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                self.logger.error(f"System monitoring failed: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_inactive_streams(self):
        """Clean up inactive streams"""        while not self._shutdown_event.is_set():
            try:
                current_time = datetime.now()
                inactive_streams = []
                
                for stream_id, stream in self._active_streams.items():
                    # Check if stream is inactive
                    if stream.status in [StreamStatus.DISCONNECTED, StreamStatus.ERROR]:
                        if stream.connected_at:
                            inactive_duration = (current_time - stream.connected_at).total_seconds()
                            if inactive_duration > 300:  # 5 minutes
                                inactive_streams.append(stream_id)
                
                # Clean up inactive streams
                for stream_id in inactive_streams:
                    await self.stop_stream(stream_id)
                    self.logger.info(f"Cleaned up inactive stream {stream_id}")
                
                await asyncio.sleep(60)  # Cleanup every minute
                
            except Exception as e:
                self.logger.error(f"Stream cleanup failed: {e}")
                await asyncio.sleep(120)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the real-time processor"""        health_status = {
            "status": "healthy" if self._initialized else "not_initialized",
            "realtime_vision_available": REALTIME_VISION_AVAILABLE,
            "realtime_audio_available": REALTIME_AUDIO_AVAILABLE,
            "streaming_libs_available": STREAMING_LIBS_AVAILABLE,
            "active_streams": len(self._active_streams),
            "global_metrics": self._global_metrics,
            "config": self.config.__dict__
        }
        
        # Check individual processors
        processors_health = {}
        for name, processor in [
            ("audio", self.audio_processor),
            ("video", self.video_processor),
            ("image", self.image_processor),
            ("text", self.text_processor)
        ]:
            if processor:
                processors_health[name] = await processor.health_check()
        
        health_status["processors"] = processors_health
        
        return health_status
    
    async def shutdown(self):
        """Gracefully shutdown the real-time processor"""        try:
            self._shutdown_event.set()
            
            # Stop all active streams
            for stream_id in list(self._active_streams.keys()):
                await self.stop_stream(stream_id)
            
            # Cancel background tasks
            tasks = [self._monitoring_task, self._cleanup_task]
            for task in tasks:
                if task and not task.done():
                    task.cancel()
            
            await asyncio.gather(*[t for t in tasks if t], return_exceptions=True)
            
            # Shutdown individual processors
            processors = [
                self.audio_processor,
                self.video_processor,
                self.image_processor,
                self.text_processor
            ]
            
            for processor in processors:
                if processor:
                    await processor.shutdown()
            
            self.logger.info("Real-time processor shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Shutdown failed: {e}")


async def create_realtime_processor(
    db_session,
    redis_client,
    config: Optional[Dict[str, Any]] = None
) -> RealtimeProcessor:
    """    Factory function to create and initialize a real-time processor
    
    Args:
        db_session: Database session
        redis_client: Redis client
        config: Configuration dictionary
        
    Returns:
        Initialized RealtimeProcessor instance
    """    # Create config from dict if provided
    processor_config = None
    if config:
        processor_config = RealtimeProcessingConfig(**{
            k: v for k, v in config.items() 
            if k in RealtimeProcessingConfig.__dataclass_fields__
        })
    
    # Create processor
    processor = RealtimeProcessor(
        db_session=db_session,
        redis_client=redis_client,
        config=processor_config
    )
    
    # Initialize
    await processor.initialize()
    
    return processor
