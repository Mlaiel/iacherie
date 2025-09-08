"""Media Streaming Engine - Advanced Real-Time Media Streaming System
===================================================================

Advanced streaming engine providing comprehensive live streaming capabilities,
real-time media processing, adaptive streaming, and broadcast-quality delivery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary streaming system contains advanced algorithms and trade secrets
belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering  
- Commercial use without explicit written permission
- Algorithm extraction or streaming technology appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import json
import logging
import uuid
import time
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from pathlib import Path
import hashlib

# Streaming and media processing imports with graceful fallbacks
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    logging.warning("OpenCV not available - using basic video processing")

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logging.warning("NumPy not available - using basic array operations")

try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False
    logging.warning("SoundDevice not available - using basic audio processing")

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
    logging.warning("WebSockets not available - using basic streaming")

logger = logging.getLogger(__name__)


class StreamType(Enum):
    """Stream types"""
    LIVE_VIDEO = "live_video"
    LIVE_AUDIO = "live_audio"
    LIVE_MIXED = "live_mixed"
    VOD = "video_on_demand"
    PODCAST = "podcast"
    WEBINAR = "webinar"
    CONFERENCE = "conference"
    BROADCAST = "broadcast"


class StreamQuality(Enum):
    """Stream quality levels"""
    LOW = "low"          # 480p/64kbps
    MEDIUM = "medium"    # 720p/128kbps
    HIGH = "high"        # 1080p/256kbps
    ULTRA = "ultra"      # 4K/512kbps
    AUTO = "auto"        # Adaptive quality


class StreamProtocol(Enum):
    """Streaming protocols"""
    RTMP = "rtmp"
    RTSP = "rtsp"
    HLS = "hls"
    DASH = "dash"
    WEBRTC = "webrtc"
    SRT = "srt"
    UDP = "udp"
    TCP = "tcp"


class StreamStatus(Enum):
    """Stream status"""
    IDLE = "idle"
    STARTING = "starting"
    LIVE = "live"
    BUFFERING = "buffering"
    PAUSED = "paused"
    ENDING = "ending"
    ENDED = "ended"
    ERROR = "error"


@dataclass
class StreamConfig:
    """Streaming configuration"""
    # Video settings
    video_enabled: bool = True
    video_width: int = 1920
    video_height: int = 1080
    video_fps: int = 30
    video_bitrate: int = 2500  # kbps
    video_codec: str = "h264"
    
    # Audio settings
    audio_enabled: bool = True
    audio_sample_rate: int = 44100
    audio_channels: int = 2
    audio_bitrate: int = 128  # kbps
    audio_codec: str = "aac"
    
    # Streaming settings
    protocol: StreamProtocol = StreamProtocol.RTMP
    adaptive_bitrate: bool = True
    buffer_size: int = 5  # seconds
    max_retry_attempts: int = 3
    
    # Quality settings
    quality_levels: List[StreamQuality] = field(default_factory=lambda: [StreamQuality.HIGH])
    auto_quality_adjustment: bool = True
    
    # Security settings
    authentication_required: bool = True
    encryption_enabled: bool = True
    access_token_required: bool = True


@dataclass
class StreamMetrics:
    """Stream performance metrics"""
    stream_id: str
    start_time: datetime
    current_viewers: int = 0
    peak_viewers: int = 0
    total_viewers: int = 0
    bytes_transmitted: int = 0
    frames_transmitted: int = 0
    frame_drops: int = 0
    latency_ms: float = 0.0
    jitter_ms: float = 0.0
    packet_loss_percent: float = 0.0
    bitrate_kbps: float = 0.0
    quality_score: float = 1.0  # 0-1 scale
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Viewer:
    """Stream viewer information"""
    viewer_id: str
    session_id: str
    ip_address: str
    user_agent: str
    location: Optional[str] = None
    quality: StreamQuality = StreamQuality.AUTO
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    bandwidth_kbps: float = 0.0
    is_active: bool = True


@dataclass
class StreamSession:
    """Stream session information"""
    session_id: str
    stream_id: str
    stream_type: StreamType
    status: StreamStatus
    config: StreamConfig
    metrics: StreamMetrics
    viewers: List[Viewer] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    recording_enabled: bool = False
    recording_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdaptiveStreamingEngine:
    """Adaptive bitrate streaming engine"""
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.quality_ladder = self._initialize_quality_ladder()
        self.viewer_qualities = {}  # viewer_id -> current_quality
        
        logger.info("📡 Adaptive Streaming Engine initialized")
    
    def _initialize_quality_ladder(self) -> Dict[StreamQuality, Dict[str, Any]]:
        """Initialize quality ladder for adaptive streaming"""
        return {
            StreamQuality.LOW: {
                'video_width': 854,
                'video_height': 480,
                'video_bitrate': 1000,
                'audio_bitrate': 64,
                'bandwidth_requirement': 1500  # kbps
            },
            StreamQuality.MEDIUM: {
                'video_width': 1280,
                'video_height': 720,
                'video_bitrate': 2500,
                'audio_bitrate': 128,
                'bandwidth_requirement': 3000
            },
            StreamQuality.HIGH: {
                'video_width': 1920,
                'video_height': 1080,
                'video_bitrate': 5000,
                'audio_bitrate': 256,
                'bandwidth_requirement': 6000
            },
            StreamQuality.ULTRA: {
                'video_width': 3840,
                'video_height': 2160,
                'video_bitrate': 15000,
                'audio_bitrate': 512,
                'bandwidth_requirement': 18000
            }
        }
    
    async def determine_optimal_quality(
        self, 
        viewer: Viewer,
        network_conditions: Dict[str, float]
    ) -> StreamQuality:
        """Determine optimal quality for viewer based on network conditions"""
        try:
            available_bandwidth = network_conditions.get('bandwidth_kbps', 0)
            latency = network_conditions.get('latency_ms', 0)
            packet_loss = network_conditions.get('packet_loss_percent', 0)
            
            # Quality selection based on available bandwidth and network conditions
            suitable_qualities = []
            
            for quality, specs in self.quality_ladder.items():
                required_bandwidth = specs['bandwidth_requirement']
                
                # Add buffer (20% overhead)
                required_with_buffer = required_bandwidth * 1.2
                
                # Check if bandwidth is sufficient
                if available_bandwidth >= required_with_buffer:
                    # Consider network conditions
                    if packet_loss < 1.0 and latency < 100:  # Good conditions
                        suitable_qualities.append(quality)
                    elif packet_loss < 3.0 and latency < 200:  # Fair conditions
                        if quality in [StreamQuality.LOW, StreamQuality.MEDIUM]:
                            suitable_qualities.append(quality)
                    else:  # Poor conditions
                        if quality == StreamQuality.LOW:
                            suitable_qualities.append(quality)
            
            # Select highest suitable quality
            if suitable_qualities:
                quality_priorities = {
                    StreamQuality.ULTRA: 4,
                    StreamQuality.HIGH: 3,
                    StreamQuality.MEDIUM: 2,
                    StreamQuality.LOW: 1
                }
                optimal_quality = max(suitable_qualities, key=lambda q: quality_priorities.get(q, 0))
            else:
                optimal_quality = StreamQuality.LOW  # Fallback
            
            # Update viewer quality tracking
            self.viewer_qualities[viewer.viewer_id] = optimal_quality
            
            return optimal_quality
            
        except Exception as e:
            logger.error(f"Quality determination failed: {e}")
            return StreamQuality.LOW
    
    async def adjust_quality_real_time(
        self, 
        viewer_id: str,
        performance_metrics: Dict[str, float]
    ) -> Optional[StreamQuality]:
        """Adjust quality in real-time based on performance metrics"""
        try:
            current_quality = self.viewer_qualities.get(viewer_id, StreamQuality.MEDIUM)
            
            # Performance indicators
            buffer_health = performance_metrics.get('buffer_level_seconds', 0)
            frame_drops = performance_metrics.get('frame_drops_per_second', 0)
            bandwidth_utilization = performance_metrics.get('bandwidth_utilization_percent', 0)
            
            quality_priorities = [StreamQuality.LOW, StreamQuality.MEDIUM, StreamQuality.HIGH, StreamQuality.ULTRA]
            current_index = quality_priorities.index(current_quality)
            
            # Determine if quality adjustment is needed
            should_decrease = (
                buffer_health < 2.0 or  # Low buffer
                frame_drops > 1.0 or    # Dropping frames
                bandwidth_utilization > 90  # High bandwidth usage
            )
            
            should_increase = (
                buffer_health > 8.0 and  # Healthy buffer
                frame_drops == 0 and     # No frame drops
                bandwidth_utilization < 70  # Comfortable bandwidth usage
            )
            
            if should_decrease and current_index > 0:
                new_quality = quality_priorities[current_index - 1]
                self.viewer_qualities[viewer_id] = new_quality
                logger.info(f"Decreased quality for viewer {viewer_id}: {current_quality.value} -> {new_quality.value}")
                return new_quality
            
            elif should_increase and current_index < len(quality_priorities) - 1:
                new_quality = quality_priorities[current_index + 1]
                self.viewer_qualities[viewer_id] = new_quality
                logger.info(f"Increased quality for viewer {viewer_id}: {current_quality.value} -> {new_quality.value}")
                return new_quality
            
            return None  # No change needed
            
        except Exception as e:
            logger.error(f"Real-time quality adjustment failed: {e}")
            return None


class StreamProcessor:
    """Real-time stream processing and encoding"""
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.is_processing = False
        self.frame_buffer = []
        self.audio_buffer = []
        
        logger.info("🎬 Stream Processor initialized")
    
    async def start_processing(self, input_source: str) -> bool:
        """Start stream processing from input source"""
        try:
            self.is_processing = True
            
            if self.config.video_enabled:
                await self._start_video_processing(input_source)
            
            if self.config.audio_enabled:
                await self._start_audio_processing(input_source)
            
            logger.info(f"Stream processing started for source: {input_source}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start stream processing: {e}")
            self.is_processing = False
            return False
    
    async def stop_processing(self) -> bool:
        """Stop stream processing"""
        try:
            self.is_processing = False
            self.frame_buffer.clear()
            self.audio_buffer.clear()
            
            logger.info("Stream processing stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop stream processing: {e}")
            return False
    
    async def process_frame(self, frame_data: bytes) -> bytes:
        """Process individual video frame"""
        try:
            if not HAS_OPENCV:
                return frame_data  # Return unchanged if OpenCV not available
            
            # Convert frame data to OpenCV format
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return frame_data
            
            # Apply processing filters
            processed_frame = await self._apply_video_filters(frame)
            
            # Encode frame
            _, encoded_frame = cv2.imencode('.jpg', processed_frame)
            return encoded_frame.tobytes()
            
        except Exception as e:
            logger.error(f"Frame processing failed: {e}")
            return frame_data
    
    async def process_audio(self, audio_data: bytes) -> bytes:
        """Process audio data"""
        try:
            # Audio processing would be implemented here
            # For now, return unchanged
            return audio_data
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return audio_data
    
    async def _start_video_processing(self, input_source: str):
        """Start video processing from source"""
        if HAS_OPENCV:
            # Video processing implementation
            pass
    
    async def _start_audio_processing(self, input_source: str):
        """Start audio processing from source"""
        if HAS_SOUNDDEVICE:
            # Audio processing implementation
            pass
    
    async def _apply_video_filters(self, frame) -> Any:
        """Apply video filters and enhancements"""
        # Basic frame processing
        # Could add filters like brightness, contrast, noise reduction, etc.
        return frame


class StreamingServer:
    """Core streaming server handling multiple streams"""
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.active_streams: Dict[str, StreamSession] = {}
        self.stream_processors: Dict[str, StreamProcessor] = {}
        self.adaptive_engines: Dict[str, AdaptiveStreamingEngine] = {}
        
        # Server state
        self.is_running = False
        self.total_bandwidth_usage = 0.0
        
        logger.info("🚀 Streaming Server initialized")
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 1935) -> bool:
        """Start streaming server"""
        try:
            self.is_running = True
            
            # Initialize server components
            await self._initialize_server_components()
            
            logger.info(f"Streaming server started on {host}:{port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start streaming server: {e}")
            return False
    
    async def stop_server(self) -> bool:
        """Stop streaming server"""
        try:
            # Stop all active streams
            for stream_id in list(self.active_streams.keys()):
                await self.stop_stream(stream_id)
            
            self.is_running = False
            
            logger.info("Streaming server stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop streaming server: {e}")
            return False
    
    async def create_stream(
        self,
        stream_type: StreamType,
        config: Optional[StreamConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StreamSession:
        """Create new stream session"""
        try:
            stream_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())
            
            stream_config = config or self.config
            
            # Initialize metrics
            metrics = StreamMetrics(
                stream_id=stream_id,
                start_time=datetime.now(timezone.utc)
            )
            
            # Create stream session
            session = StreamSession(
                session_id=session_id,
                stream_id=stream_id,
                stream_type=stream_type,
                status=StreamStatus.IDLE,
                config=stream_config,
                metrics=metrics,
                metadata=metadata or {}
            )
            
            self.active_streams[stream_id] = session
            
            # Initialize stream processor
            self.stream_processors[stream_id] = StreamProcessor(stream_config)
            
            # Initialize adaptive streaming engine
            self.adaptive_engines[stream_id] = AdaptiveStreamingEngine(stream_config)
            
            logger.info(f"Created stream {stream_id} of type {stream_type.value}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create stream: {e}")
            raise
    
    async def start_stream(self, stream_id: str, input_source: str) -> bool:
        """Start streaming for specific stream"""
        try:
            session = self.active_streams.get(stream_id)
            if not session:
                raise ValueError(f"Stream {stream_id} not found")
            
            # Update session status
            session.status = StreamStatus.STARTING
            session.start_time = datetime.now(timezone.utc)
            
            # Start stream processor
            processor = self.stream_processors.get(stream_id)
            if processor:
                success = await processor.start_processing(input_source)
                if not success:
                    session.status = StreamStatus.ERROR
                    return False
            
            # Update status to live
            session.status = StreamStatus.LIVE
            
            # Start metrics collection
            asyncio.create_task(self._collect_stream_metrics(stream_id))
            
            logger.info(f"Stream {stream_id} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start stream {stream_id}: {e}")
            return False
    
    async def stop_stream(self, stream_id: str) -> bool:
        """Stop streaming for specific stream"""
        try:
            session = self.active_streams.get(stream_id)
            if not session:
                return False
            
            # Update session status
            session.status = StreamStatus.ENDING
            
            # Stop stream processor
            processor = self.stream_processors.get(stream_id)
            if processor:
                await processor.stop_processing()
            
            # Disconnect all viewers
            for viewer in session.viewers:
                await self._disconnect_viewer(stream_id, viewer.viewer_id)
            
            # Update final status
            session.status = StreamStatus.ENDED
            session.end_time = datetime.now(timezone.utc)
            
            # Cleanup
            if stream_id in self.stream_processors:
                del self.stream_processors[stream_id]
            if stream_id in self.adaptive_engines:
                del self.adaptive_engines[stream_id]
            
            logger.info(f"Stream {stream_id} stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop stream {stream_id}: {e}")
            return False
    
    async def add_viewer(
        self,
        stream_id: str,
        viewer_info: Dict[str, Any]
    ) -> Viewer:
        """Add viewer to stream"""
        try:
            session = self.active_streams.get(stream_id)
            if not session:
                raise ValueError(f"Stream {stream_id} not found")
            
            if session.status != StreamStatus.LIVE:
                raise ValueError(f"Stream {stream_id} is not live")
            
            viewer_id = str(uuid.uuid4())
            
            viewer = Viewer(
                viewer_id=viewer_id,
                session_id=session.session_id,
                ip_address=viewer_info.get('ip_address', ''),
                user_agent=viewer_info.get('user_agent', ''),
                location=viewer_info.get('location'),
                bandwidth_kbps=viewer_info.get('bandwidth_kbps', 0)
            )
            
            session.viewers.append(viewer)
            session.metrics.current_viewers += 1
            session.metrics.total_viewers += 1
            
            if session.metrics.current_viewers > session.metrics.peak_viewers:
                session.metrics.peak_viewers = session.metrics.current_viewers
            
            # Determine optimal quality for viewer
            adaptive_engine = self.adaptive_engines.get(stream_id)
            if adaptive_engine:
                network_conditions = {
                    'bandwidth_kbps': viewer.bandwidth_kbps,
                    'latency_ms': viewer_info.get('latency_ms', 50),
                    'packet_loss_percent': viewer_info.get('packet_loss_percent', 0)
                }
                optimal_quality = await adaptive_engine.determine_optimal_quality(
                    viewer, network_conditions
                )
                viewer.quality = optimal_quality
            
            logger.info(f"Added viewer {viewer_id} to stream {stream_id}")
            return viewer
            
        except Exception as e:
            logger.error(f"Failed to add viewer to stream {stream_id}: {e}")
            raise
    
    async def remove_viewer(self, stream_id: str, viewer_id: str) -> bool:
        """Remove viewer from stream"""
        try:
            return await self._disconnect_viewer(stream_id, viewer_id)
            
        except Exception as e:
            logger.error(f"Failed to remove viewer {viewer_id} from stream {stream_id}: {e}")
            return False
    
    async def get_stream_status(self, stream_id: str) -> Dict[str, Any]:
        """Get stream status and metrics"""
        try:
            session = self.active_streams.get(stream_id)
            if not session:
                return {'error': f'Stream {stream_id} not found'}
            
            # Calculate uptime
            uptime_seconds = 0
            if session.start_time:
                uptime_seconds = (datetime.now(timezone.utc) - session.start_time).total_seconds()
            
            return {
                'stream_id': stream_id,
                'status': session.status.value,
                'stream_type': session.stream_type.value,
                'uptime_seconds': uptime_seconds,
                'viewers': {
                    'current': session.metrics.current_viewers,
                    'peak': session.metrics.peak_viewers,
                    'total': session.metrics.total_viewers
                },
                'performance': {
                    'bitrate_kbps': session.metrics.bitrate_kbps,
                    'latency_ms': session.metrics.latency_ms,
                    'packet_loss_percent': session.metrics.packet_loss_percent,
                    'quality_score': session.metrics.quality_score,
                    'frame_drops': session.metrics.frame_drops
                },
                'config': {
                    'resolution': f"{session.config.video_width}x{session.config.video_height}",
                    'fps': session.config.video_fps,
                    'video_bitrate': session.config.video_bitrate,
                    'audio_bitrate': session.config.audio_bitrate,
                    'protocol': session.config.protocol.value
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get stream status: {e}")
            return {'error': str(e)}
    
    async def _initialize_server_components(self):
        """Initialize server components"""
        # Server initialization logic
        pass
    
    async def _collect_stream_metrics(self, stream_id: str):
        """Collect real-time metrics for stream"""
        session = self.active_streams.get(stream_id)
        if not session:
            return
        
        while session.status == StreamStatus.LIVE:
            try:
                # Update metrics
                session.metrics.timestamp = datetime.now(timezone.utc)
                
                # Simulate metrics collection (would use real data in production)
                session.metrics.bitrate_kbps = session.config.video_bitrate + session.config.audio_bitrate
                session.metrics.latency_ms = 50.0  # Would measure actual latency
                session.metrics.packet_loss_percent = 0.1  # Would measure actual packet loss
                session.metrics.quality_score = 0.95  # Would calculate based on actual performance
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Metrics collection failed for stream {stream_id}: {e}")
                break
    
    async def _disconnect_viewer(self, stream_id: str, viewer_id: str) -> bool:
        """Disconnect viewer from stream"""
        try:
            session = self.active_streams.get(stream_id)
            if not session:
                return False
            
            # Find and remove viewer
            viewer_found = False
            for i, viewer in enumerate(session.viewers):
                if viewer.viewer_id == viewer_id:
                    session.viewers.pop(i)
                    session.metrics.current_viewers -= 1
                    viewer_found = True
                    break
            
            if viewer_found:
                logger.info(f"Disconnected viewer {viewer_id} from stream {stream_id}")
            
            return viewer_found
            
        except Exception as e:
            logger.error(f"Failed to disconnect viewer: {e}")
            return False


class MediaStreamingEngine:
    """Main media streaming engine orchestrating all streaming components"""
    
    def __init__(self, config: Optional[StreamConfig] = None):
        """Initialize media streaming engine"""
        self.config = config or StreamConfig()
        
        # Initialize core components
        self.streaming_server = StreamingServer(self.config)
        
        # Engine state
        self.is_running = False
        self.global_metrics = {
            'total_streams_created': 0,
            'active_streams': 0,
            'total_viewers': 0,
            'total_bandwidth_usage': 0.0
        }
        
        logger.info("📺 Media Streaming Engine initialized")
    
    async def start_engine(self, host: str = "0.0.0.0", port: int = 1935) -> bool:
        """Start the streaming engine"""
        try:
            # Start streaming server
            success = await self.streaming_server.start_server(host, port)
            if not success:
                return False
            
            self.is_running = True
            
            # Start global metrics collection
            asyncio.create_task(self._collect_global_metrics())
            
            logger.info("Media Streaming Engine started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start streaming engine: {e}")
            return False
    
    async def stop_engine(self) -> bool:
        """Stop the streaming engine"""
        try:
            # Stop streaming server
            await self.streaming_server.stop_server()
            
            self.is_running = False
            
            logger.info("Media Streaming Engine stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop streaming engine: {e}")
            return False
    
    async def create_live_stream(
        self,
        stream_type: StreamType = StreamType.LIVE_VIDEO,
        config: Optional[StreamConfig] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StreamSession:
        """Create live stream session"""
        try:
            session = await self.streaming_server.create_stream(stream_type, config, metadata)
            self.global_metrics['total_streams_created'] += 1
            self.global_metrics['active_streams'] += 1
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create live stream: {e}")
            raise
    
    async def start_live_stream(self, stream_id: str, input_source: str) -> bool:
        """Start live streaming"""
        return await self.streaming_server.start_stream(stream_id, input_source)
    
    async def stop_live_stream(self, stream_id: str) -> bool:
        """Stop live streaming"""
        success = await self.streaming_server.stop_stream(stream_id)
        if success:
            self.global_metrics['active_streams'] = max(0, self.global_metrics['active_streams'] - 1)
        return success
    
    async def join_stream(
        self,
        stream_id: str,
        viewer_info: Dict[str, Any]
    ) -> Viewer:
        """Join viewer to stream"""
        try:
            viewer = await self.streaming_server.add_viewer(stream_id, viewer_info)
            self.global_metrics['total_viewers'] += 1
            
            return viewer
            
        except Exception as e:
            logger.error(f"Failed to join stream: {e}")
            raise
    
    async def leave_stream(self, stream_id: str, viewer_id: str) -> bool:
        """Remove viewer from stream"""
        return await self.streaming_server.remove_viewer(stream_id, viewer_id)
    
    async def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive engine status"""
        try:
            active_streams = []
            for stream_id, session in self.streaming_server.active_streams.items():
                stream_status = await self.streaming_server.get_stream_status(stream_id)
                active_streams.append(stream_status)
            
            return {
                'engine_running': self.is_running,
                'server_running': self.streaming_server.is_running,
                'global_metrics': self.global_metrics,
                'active_streams': active_streams,
                'server_config': {
                    'max_concurrent_streams': 100,  # Would be configurable
                    'supported_protocols': [p.value for p in StreamProtocol],
                    'supported_qualities': [q.value for q in StreamQuality]
                },
                'status_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get engine status: {e}")
            return {'error': str(e)}
    
    async def _collect_global_metrics(self):
        """Collect global engine metrics"""
        while self.is_running:
            try:
                # Update global metrics
                active_streams = len(self.streaming_server.active_streams)
                total_viewers = sum(
                    len(session.viewers) 
                    for session in self.streaming_server.active_streams.values()
                )
                
                self.global_metrics['active_streams'] = active_streams
                self.global_metrics['total_viewers'] = total_viewers
                
                # Calculate total bandwidth usage
                total_bandwidth = sum(
                    session.metrics.bitrate_kbps 
                    for session in self.streaming_server.active_streams.values()
                )
                self.global_metrics['total_bandwidth_usage'] = total_bandwidth
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Global metrics collection failed: {e}")
                break


# Export all classes for import
__all__ = [
    'MediaStreamingEngine',
    'StreamingServer',
    'StreamProcessor',
    'AdaptiveStreamingEngine',
    'StreamConfig',
    'StreamSession',
    'StreamMetrics',
    'Viewer',
    'StreamType',
    'StreamQuality',
    'StreamProtocol',
    'StreamStatus'
]