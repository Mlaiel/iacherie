"""
Ainflue Platform - Multimedia Optimization - Adaptive Streaming Optimization
Professional adaptive streaming optimization for multimedia delivery

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.1.0 Enterprise
"""

import asyncio
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class StreamingProtocol(Enum):
    """Adaptive streaming protocols"""
    HLS = "hls"        # HTTP Live Streaming
    DASH = "dash"      # Dynamic Adaptive Streaming
    SMOOTH = "smooth"  # Microsoft Smooth Streaming
    CMAF = "cmaf"      # Common Media Application Format


@dataclass
class StreamingProfile:
    """Streaming quality profile"""
    name: str
    bitrate: int        # kbps
    resolution: tuple   # (width, height)
    framerate: int      # fps
    codec: str
    audio_bitrate: int  # kbps


class AdaptiveStreamingOptimizer:
    """Professional adaptive streaming optimization system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize adaptive streaming optimizer"""
        self.config = config or {}
        self.streaming_profiles = self._initialize_streaming_profiles()
        
    def _initialize_streaming_profiles(self) -> List[StreamingProfile]:
        """Initialize standard streaming profiles"""
        return [
            StreamingProfile("4K", 8000, (3840, 2160), 30, "h265", 192),
            StreamingProfile("1080p", 5000, (1920, 1080), 30, "h264", 128),
            StreamingProfile("720p", 2500, (1280, 720), 30, "h264", 96),
            StreamingProfile("480p", 1000, (854, 480), 25, "h264", 64),
            StreamingProfile("360p", 600, (640, 360), 25, "h264", 48),
            StreamingProfile("240p", 300, (426, 240), 15, "h264", 32)
        ]
    
    async def generate_adaptive_manifest(
        self,
        content_path: str,
        protocol: StreamingProtocol = StreamingProtocol.HLS
    ) -> Dict[str, Any]:
        """Generate adaptive streaming manifest"""
        try:
            manifest = {
                "protocol": protocol.value,
                "version": "1.0",
                "profiles": [],
                "segments": [],
                "duration": 120,  # seconds
                "target_duration": 10  # segment duration
            }
            
            for profile in self.streaming_profiles:
                manifest["profiles"].append({
                    "name": profile.name,
                    "bandwidth": profile.bitrate * 1000,  # Convert to bps
                    "resolution": f"{profile.resolution[0]}x{profile.resolution[1]}",
                    "codecs": f"{profile.codec},aac",
                    "playlist_url": f"{profile.name.lower()}/playlist.m3u8"
                })
            
            return manifest
            
        except Exception as e:
            logger.error(f"Error generating adaptive manifest: {e}")
            raise
    
    async def optimize_for_device(
        self,
        device_info: Dict[str, Any],
        network_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize streaming for specific device and network"""
        try:
            device_capabilities = device_info.get("capabilities", {})
            screen_resolution = device_info.get("screen_resolution", (1920, 1080))
            available_bandwidth = network_conditions.get("bandwidth_kbps", 5000)
            
            # Select appropriate profiles based on constraints
            suitable_profiles = []
            for profile in self.streaming_profiles:
                # Check if device can handle resolution
                if (profile.resolution[0] <= screen_resolution[0] * 1.2 and
                    profile.resolution[1] <= screen_resolution[1] * 1.2):
                    
                    # Check if bandwidth can support profile
                    total_bitrate = profile.bitrate + profile.audio_bitrate
                    if total_bitrate <= available_bandwidth * 0.8:  # 80% safety margin
                        suitable_profiles.append(profile)
            
            optimization = {
                "recommended_profiles": [p.name for p in suitable_profiles],
                "initial_quality": suitable_profiles[0].name if suitable_profiles else "240p",
                "max_quality": suitable_profiles[-1].name if suitable_profiles else "720p",
                "adaptive_algorithm": self._select_adaptive_algorithm(network_conditions),
                "buffer_settings": self._calculate_buffer_settings(network_conditions)
            }
            
            return optimization
            
        except Exception as e:
            logger.error(f"Error optimizing for device: {e}")
            raise
    
    def _select_adaptive_algorithm(self, network_conditions: Dict[str, Any]) -> str:
        """Select appropriate adaptive algorithm"""
        try:
            stability = network_conditions.get("stability", 0.8)
            latency = network_conditions.get("latency_ms", 50)
            
            if stability > 0.9 and latency < 30:
                return "aggressive"  # Quick quality changes
            elif stability < 0.7 or latency > 100:
                return "conservative"  # Slow quality changes
            else:
                return "balanced"  # Standard adaptation
                
        except Exception as e:
            logger.error(f"Error selecting adaptive algorithm: {e}")
            return "balanced"
    
    def _calculate_buffer_settings(self, network_conditions: Dict[str, Any]) -> Dict[str, int]:
        """Calculate optimal buffer settings"""
        try:
            stability = network_conditions.get("stability", 0.8)
            bandwidth_variability = network_conditions.get("variability", 0.2)
            
            if stability < 0.7 or bandwidth_variability > 0.3:
                return {
                    "initial_buffer": 20,    # seconds
                    "max_buffer": 60,       # seconds
                    "rebuffer_threshold": 3  # seconds
                }
            elif stability > 0.9:
                return {
                    "initial_buffer": 5,
                    "max_buffer": 30,
                    "rebuffer_threshold": 1
                }
            else:
                return {
                    "initial_buffer": 10,
                    "max_buffer": 45,
                    "rebuffer_threshold": 2
                }
                
        except Exception as e:
            logger.error(f"Error calculating buffer settings: {e}")
            return {"initial_buffer": 10, "max_buffer": 45, "rebuffer_threshold": 2}


# Export main classes
__all__ = [
    'AdaptiveStreamingOptimizer',
    'StreamingProfile',
    'StreamingProtocol'
]