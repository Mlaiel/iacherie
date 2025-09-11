"""Streaming Compression Engine
Real-time compression for live streaming and real-time applications.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, AsyncGenerator
from dataclasses import dataclass
from pathlib import Path
import time

logger = logging.getLogger(__name__)

@dataclass
class StreamingConfig:
    """Configuration for streaming compression."""
    format: str = "h264"
    bitrate: int = 2500  # kbps
    resolution: tuple = (1920, 1080)
    fps: int = 30
    keyframe_interval: int = 2  # seconds
    buffer_size: int = 10  # frames
    low_latency: bool = True

class StreamingCompressionEngine:
    """Real-time compression engine for streaming applications."""
    
    def __init__(self):
        """Initialize the streaming compression engine."""
        self.active_streams = {}
        self.compression_presets = self._load_streaming_presets()
        
    def _load_streaming_presets(self) -> Dict[str, StreamingConfig]:
        """Load predefined streaming compression presets."""
        return {
            "twitch_1080p": StreamingConfig(
                format="h264",
                bitrate=6000,
                resolution=(1920, 1080),
                fps=60,
                keyframe_interval=2,
                low_latency=True
            ),
            "youtube_live": StreamingConfig(
                format="h264",
                bitrate=4500,
                resolution=(1920, 1080),
                fps=30,
                keyframe_interval=2,
                low_latency=False
            ),
            "mobile_stream": StreamingConfig(
                format="h264",
                bitrate=1500,
                resolution=(1280, 720),
                fps=30,
                keyframe_interval=1,
                low_latency=True
            ),
            "low_bandwidth": StreamingConfig(
                format="h264",
                bitrate=800,
                resolution=(854, 480),
                fps=24,
                keyframe_interval=1,
                low_latency=True
            )
        }
    
    async def start_stream(
        self,
        stream_id: str,
        config: Optional[StreamingConfig] = None,
        preset: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a new streaming compression session.
        
        Args:
            stream_id: Unique identifier for the stream
            config: Streaming configuration
            preset: Predefined preset name
            
        Returns:
            Stream initialization result
        """
        try:
            # Use preset or config
            if preset and preset in self.compression_presets:
                config = self.compression_presets[preset]
            elif not config:
                config = self.compression_presets["youtube_live"]
            
            # Initialize stream context
            stream_context = {
                "config": config,
                "start_time": time.time(),
                "frame_count": 0,
                "buffer": [],
                "stats": {
                    "frames_processed": 0,
                    "frames_dropped": 0,
                    "average_latency": 0.0,
                    "bitrate_actual": 0,
                    "cpu_usage": 0.0
                }
            }
            
            self.active_streams[stream_id] = stream_context
            
            logger.info(f"Started streaming session {stream_id}")
            
            return {
                "success": True,
                "stream_id": stream_id,
                "config": config,
                "estimated_latency": self._estimate_latency(config)
            }
            
        except Exception as e:
            logger.error(f"Failed to start stream {stream_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_frame(
        self,
        stream_id: str,
        frame_data: bytes,
        timestamp: float
    ) -> Dict[str, Any]:
        """
        Process a single frame for streaming compression.
        
        Args:
            stream_id: Stream identifier
            frame_data: Raw frame data
            timestamp: Frame timestamp
            
        Returns:
            Processed frame result
        """
        if stream_id not in self.active_streams:
            return {
                "success": False,
                "error": "Stream not found"
            }
        
        try:
            context = self.active_streams[stream_id]
            config = context["config"]
            
            # Simulate frame processing
            processing_start = time.time()
            
            # Compress frame (simulated)
            compressed_frame = await self._compress_frame(
                frame_data, config, context
            )
            
            processing_time = time.time() - processing_start
            
            # Update statistics
            context["frame_count"] += 1
            context["stats"]["frames_processed"] += 1
            context["stats"]["average_latency"] = (
                context["stats"]["average_latency"] * 0.9 + 
                processing_time * 0.1
            )
            
            # Buffer management
            if len(context["buffer"]) >= config.buffer_size:
                context["buffer"].pop(0)
            
            context["buffer"].append({
                "data": compressed_frame,
                "timestamp": timestamp,
                "size": len(compressed_frame)
            })
            
            return {
                "success": True,
                "compressed_size": len(compressed_frame),
                "processing_time": processing_time,
                "buffer_level": len(context["buffer"]),
                "frame_number": context["frame_count"]
            }
            
        except Exception as e:
            logger.error(f"Frame processing failed for stream {stream_id}: {e}")
            context["stats"]["frames_dropped"] += 1
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _compress_frame(
        self,
        frame_data: bytes,
        config: StreamingConfig,
        context: Dict[str, Any]
    ) -> bytes:
        """Compress a single frame with streaming optimization."""
        # Simulate compression processing
        await asyncio.sleep(0.001)  # Simulate minimal processing time
        
        # Calculate compression based on config
        original_size = len(frame_data)
        
        # Streaming compression typically achieves higher compression ratios
        # due to temporal redundancy between frames
        if context["frame_count"] % (config.keyframe_interval * config.fps) == 0:
            # Keyframe - lower compression
            compression_ratio = 0.4
        else:
            # P-frame or B-frame - higher compression
            compression_ratio = 0.1
        
        compressed_size = int(original_size * compression_ratio)
        
        # Return simulated compressed data
        return b"compressed_frame_data" * (compressed_size // 20)
    
    async def get_stream_output(
        self,
        stream_id: str,
        chunk_size: int = 1024
    ) -> AsyncGenerator[bytes, None]:
        """
        Get streaming output as an async generator.
        
        Args:
            stream_id: Stream identifier
            chunk_size: Size of output chunks
            
        Yields:
            Compressed video chunks
        """
        if stream_id not in self.active_streams:
            return
        
        context = self.active_streams[stream_id]
        
        while stream_id in self.active_streams:
            # Wait for buffer to have data
            while len(context["buffer"]) == 0:
                await asyncio.sleep(0.01)
            
            # Get frame from buffer
            frame = context["buffer"].pop(0)
            
            # Yield frame data in chunks
            frame_data = frame["data"]
            for i in range(0, len(frame_data), chunk_size):
                chunk = frame_data[i:i + chunk_size]
                yield chunk
    
    def get_stream_stats(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive statistics for a stream."""
        if stream_id not in self.active_streams:
            return None
        
        context = self.active_streams[stream_id]
        current_time = time.time()
        duration = current_time - context["start_time"]
        
        # Calculate actual bitrate
        total_frames = context["stats"]["frames_processed"]
        if duration > 0 and total_frames > 0:
            actual_fps = total_frames / duration
            # Estimate bitrate based on frame processing
            estimated_bitrate = context["config"].bitrate * 0.9  # Simulated
        else:
            actual_fps = 0
            estimated_bitrate = 0
        
        return {
            "stream_id": stream_id,
            "duration": duration,
            "config": context["config"],
            "performance": {
                "frames_processed": context["stats"]["frames_processed"],
                "frames_dropped": context["stats"]["frames_dropped"],
                "actual_fps": actual_fps,
                "target_fps": context["config"].fps,
                "average_latency_ms": context["stats"]["average_latency"] * 1000,
                "buffer_level": len(context["buffer"]),
                "drop_rate": (
                    context["stats"]["frames_dropped"] / 
                    max(1, context["stats"]["frames_processed"] + context["stats"]["frames_dropped"])
                )
            },
            "quality": {
                "target_bitrate": context["config"].bitrate,
                "estimated_actual_bitrate": estimated_bitrate,
                "resolution": context["config"].resolution,
                "keyframe_interval": context["config"].keyframe_interval
            }
        }
    
    def _estimate_latency(self, config: StreamingConfig) -> float:
        """Estimate expected latency for configuration."""
        base_latency = 0.050  # 50ms base processing latency
        
        # Add latency based on configuration
        if config.low_latency:
            latency_factor = 1.0
        else:
            latency_factor = 2.0
        
        # Resolution impact
        pixels = config.resolution[0] * config.resolution[1]
        resolution_factor = pixels / (1920 * 1080)
        
        # FPS impact
        fps_factor = config.fps / 30.0
        
        estimated_latency = base_latency * latency_factor * resolution_factor * fps_factor
        
        return estimated_latency
    
    async def stop_stream(self, stream_id: str) -> Dict[str, Any]:
        """Stop and clean up a streaming session."""
        if stream_id not in self.active_streams:
            return {
                "success": False,
                "error": "Stream not found"
            }
        
        context = self.active_streams[stream_id]
        duration = time.time() - context["start_time"]
        
        # Get final statistics
        final_stats = self.get_stream_stats(stream_id)
        
        # Clean up
        del self.active_streams[stream_id]
        
        logger.info(f"Stopped streaming session {stream_id} after {duration:.2f}s")
        
        return {
            "success": True,
            "duration": duration,
            "final_stats": final_stats
        }
    
    def get_active_streams(self) -> List[str]:
        """Get list of active stream IDs."""
        return list(self.active_streams.keys())
    
    def get_preset_recommendations(
        self,
        target_platform: str,
        available_bandwidth: int,  # kbps
        hardware_capability: str = "medium"  # low, medium, high
    ) -> List[str]:
        """Get recommended presets based on constraints."""
        recommendations = []
        
        for preset_name, config in self.compression_presets.items():
            # Check bandwidth compatibility
            if config.bitrate <= available_bandwidth * 0.8:  # Leave 20% margin
                # Check hardware compatibility
                complexity_score = self._calculate_complexity_score(config)
                
                if hardware_capability == "high" or complexity_score <= 5:
                    recommendations.append(preset_name)
        
        # Sort by quality (higher bitrate generally means higher quality)
        recommendations.sort(
            key=lambda p: self.compression_presets[p].bitrate,
            reverse=True
        )
        
        return recommendations
    
    def _calculate_complexity_score(self, config: StreamingConfig) -> int:
        """Calculate encoding complexity score (1-10)."""
        score = 1
        
        # Resolution complexity
        pixels = config.resolution[0] * config.resolution[1]
        if pixels >= 1920 * 1080:
            score += 3
        elif pixels >= 1280 * 720:
            score += 2
        else:
            score += 1
        
        # FPS complexity
        if config.fps >= 60:
            score += 3
        elif config.fps >= 30:
            score += 2
        else:
            score += 1
        
        # Low latency adds complexity
        if config.low_latency:
            score += 2
        
        return min(10, score)