"""
Streaming Audio Configuration Module for IA-Influencer Agent Platform
====================================================================

Professional streaming audio configuration for real-time processing and distribution.
Supports multiple streaming protocols, adaptive bitrates, and platform optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
 STRICT COPYRIGHT WARNING 
This code and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple, NamedTuple
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class StreamingProtocol(Enum):
    """Streaming protocols"""
    HTTP_LIVE_STREAMING = "hls"         # Apple HLS
    DASH = "dash"                       # MPEG-DASH
    SMOOTH_STREAMING = "smooth"         # Microsoft Smooth Streaming
    RTMP = "rtmp"                       # Real-Time Messaging Protocol
    RTSP = "rtsp"                       # Real-Time Streaming Protocol
    WEBRTC = "webrtc"                   # Web Real-Time Communication
    ICECAST = "icecast"                 # Icecast streaming
    SHOUTCAST = "shoutcast"             # SHOUTcast streaming


class AdaptiveBitrateStrategy(Enum):
    """Adaptive bitrate strategies"""
    CONSERVATIVE = "conservative"        # Prefer stability over quality
    BALANCED = "balanced"               # Balance quality and stability
    AGGRESSIVE = "aggressive"           # Prefer quality over stability
    BANDWIDTH_AWARE = "bandwidth_aware" # Optimize for available bandwidth
    DEVICE_AWARE = "device_aware"       # Optimize for device capabilities


class StreamingQuality(Enum):
    """Streaming quality levels"""
    ULTRA_LOW = "ultra_low"             # 32-64 kbps
    LOW = "low"                         # 64-96 kbps
    STANDARD = "standard"               # 128-160 kbps
    HIGH = "high"                       # 192-256 kbps
    ULTRA_HIGH = "ultra_high"           # 320+ kbps
    LOSSLESS = "lossless"               # Lossless streaming


class BufferingStrategy(Enum):
    """Audio buffering strategies"""
    MINIMAL = "minimal"                 # Minimal buffering, low latency
    STANDARD = "standard"               # Standard buffering
    AGGRESSIVE = "aggressive"           # Large buffer, stable playback
    ADAPTIVE = "adaptive"               # Adaptive buffer sizing
    PREDICTIVE = "predictive"           # ML-based buffer prediction


class NetworkCondition(Enum):
    """Network condition types"""
    EXCELLENT = "excellent"             # >10 Mbps, <50ms latency
    GOOD = "good"                      # 1-10 Mbps, 50-150ms latency
    FAIR = "fair"                      # 256kbps-1Mbps, 150-300ms latency
    POOR = "poor"                      # <256kbps, >300ms latency
    UNSTABLE = "unstable"              # Highly variable conditions


@dataclass
class StreamingEndpoint:
    """Streaming endpoint configuration"""
    name: str
    url: str
    protocol: StreamingProtocol
    backup_url: Optional[str] = None
    auth_required: bool = False
    auth_token: Optional[str] = None
    max_concurrent_streams: int = 100
    geographical_restrictions: List[str] = field(default_factory=list)


@dataclass
class BitrateProfile:
    """Bitrate profile for adaptive streaming"""
    name: str
    bitrate_kbps: int
    sample_rate: int
    channels: int
    codec: str
    quality_level: StreamingQuality
    target_devices: List[str] = field(default_factory=list)
    network_requirements: NetworkCondition = NetworkCondition.GOOD


@dataclass
class BufferingConfig:
    """Audio buffering configuration"""
    initial_buffer_duration_ms: int = 2000
    target_buffer_duration_ms: int = 5000
    max_buffer_duration_ms: int = 10000
    rebuffer_threshold_ms: int = 500
    buffer_health_threshold: float = 0.3
    enable_prebuffering: bool = True
    chunk_duration_ms: int = 1000


@dataclass
class NetworkAdaptationConfig:
    """Network adaptation configuration"""
    bandwidth_estimation_enabled: bool = True
    bandwidth_probe_interval_ms: int = 5000
    quality_adaptation_enabled: bool = True
    quality_switch_threshold: float = 0.2
    downgrade_threshold_ratio: float = 0.8
    upgrade_threshold_ratio: float = 1.2
    stability_requirement_ms: int = 10000


class StreamingAudioConfig:
    """
    Comprehensive streaming audio configuration manager
    
    Manages all aspects of audio streaming including protocols, adaptive bitrates,
    buffering strategies, and network optimization.
    """
    
    def __init__(self):
        """Initialize streaming audio configuration"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core streaming configuration
        self._primary_protocol = StreamingProtocol.HTTP_LIVE_STREAMING
        self._fallback_protocols = [StreamingProtocol.DASH, StreamingProtocol.RTMP]
        self._adaptive_strategy = AdaptiveBitrateStrategy.BALANCED
        self._buffering_strategy = BufferingStrategy.ADAPTIVE
        
        # Configuration objects
        self.buffering_config = BufferingConfig()
        self.network_adaptation = NetworkAdaptationConfig()
        
        # Bitrate profiles for adaptive streaming
        self._bitrate_profiles = self._initialize_bitrate_profiles()
        
        # Streaming endpoints
        self._streaming_endpoints = {}
        
        # Platform-specific configurations
        self._platform_configs = self._initialize_platform_configs()
        
        # Protocol-specific settings
        self._protocol_configs = self._initialize_protocol_configs()
        
        # Quality ladders for different use cases
        self._quality_ladders = self._initialize_quality_ladders()
        
        self.logger.info("StreamingAudioConfig initialized successfully")
    
    def _initialize_bitrate_profiles(self) -> Dict[str, BitrateProfile]:
        """Initialize standard bitrate profiles"""



        return {
            "ultra_low_mobile": BitrateProfile(
                name="Ultra Low (Mobile)",
                bitrate_kbps=32,
                sample_rate=22050,
                channels=1,
                codec="aac",
                quality_level=StreamingQuality.ULTRA_LOW,
                target_devices=["mobile", "2g_network"],
                network_requirements=NetworkCondition.POOR
            ),
            "low_mobile": BitrateProfile(
                name="Low (Mobile)",
                bitrate_kbps=64,
                sample_rate=44100,
                channels=2,
                codec="aac",
                quality_level=StreamingQuality.LOW,
                target_devices=["mobile", "3g_network"],
                network_requirements=NetworkCondition.FAIR
            ),
            "standard_quality": BitrateProfile(
                name="Standard Quality",
                bitrate_kbps=128,
                sample_rate=44100,
                channels=2,
                codec="aac",
                quality_level=StreamingQuality.STANDARD,
                target_devices=["mobile", "desktop", "tablet"],
                network_requirements=NetworkCondition.GOOD
            ),
            "high_quality": BitrateProfile(
                name="High Quality",
                bitrate_kbps=192,
                sample_rate=44100,
                channels=2,
                codec="aac",
                quality_level=StreamingQuality.HIGH,
                target_devices=["desktop", "tablet", "smart_tv"],
                network_requirements=NetworkCondition.GOOD
            ),
            "premium_quality": BitrateProfile(
                name="Premium Quality",
                bitrate_kbps=256,
                sample_rate=48000,
                channels=2,
                codec="aac",
                quality_level=StreamingQuality.HIGH,
                target_devices=["desktop", "audiophile_devices"],
                network_requirements=NetworkCondition.EXCELLENT
            ),
            "ultra_high_quality": BitrateProfile(
                name="Ultra High Quality",
                bitrate_kbps=320,
                sample_rate=48000,
                channels=2,
                codec="aac",
                quality_level=StreamingQuality.ULTRA_HIGH,
                target_devices=["desktop", "audiophile_devices"],
                network_requirements=NetworkCondition.EXCELLENT
            ),
            "lossless_quality": BitrateProfile(
                name="Lossless Quality",
                bitrate_kbps=1411,  # CD quality
                sample_rate=44100,
                channels=2,
                codec="flac",
                quality_level=StreamingQuality.LOSSLESS,
                target_devices=["audiophile_devices", "studio_monitors"],
                network_requirements=NetworkCondition.EXCELLENT
            )
        }
    
    def _initialize_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific streaming configurations"""



        return {
            "spotify": {
                "preferred_protocols": [StreamingProtocol.HTTP_LIVE_STREAMING],
                "supported_codecs": ["ogg", "aac", "mp3"],
                "bitrate_profiles": ["standard_quality", "high_quality", "premium_quality"],
                "max_bitrate": 320,
                "loudness_normalization": True,
                "crossfade_support": True,
                "gapless_playback": True,
                "offline_caching": True,
                "cdn_endpoints": [
                    "https://audio-sp-sjc.pscdn.co",
                    "https://audio4-fa723077.ap-south-1.elb.amazonaws.com"
                ]
            },
            "apple_music": {
                "preferred_protocols": [StreamingProtocol.HTTP_LIVE_STREAMING],
                "supported_codecs": ["aac", "alac"],
                "bitrate_profiles": ["standard_quality", "high_quality", "lossless_quality"],
                "max_bitrate": 256,
                "spatial_audio_support": True,
                "atmos_support": True,
                "lossless_streaming": True,
                "cdn_endpoints": [
                    "https://amp-api.music.apple.com",
                    "https://play.itunes.apple.com"
                ]
            },
            "youtube_music": {
                "preferred_protocols": [StreamingProtocol.DASH, StreamingProtocol.HTTP_LIVE_STREAMING],
                "supported_codecs": ["aac", "opus"],
                "bitrate_profiles": ["low_mobile", "standard_quality", "high_quality"],
                "max_bitrate": 256,
                "adaptive_streaming": True,
                "video_sync_required": False,
                "cdn_endpoints": [
                    "https://r1---sn-p5qs7n7l.googlevideo.com",
                    "https://r2---sn-p5qlsn7s.googlevideo.com"
                ]
            },
            "tidal": {
                "preferred_protocols": [StreamingProtocol.HTTP_LIVE_STREAMING],
                "supported_codecs": ["aac", "flac", "mqa"],
                "bitrate_profiles": ["high_quality", "ultra_high_quality", "lossless_quality"],
                "max_bitrate": 1411,
                "mqa_support": True,
                "hi_res_streaming": True,
                "exclusive_mode": True
            },
            "soundcloud": {
                "preferred_protocols": [StreamingProtocol.HTTP_LIVE_STREAMING],
                "supported_codecs": ["mp3", "opus"],
                "bitrate_profiles": ["standard_quality", "high_quality"],
                "max_bitrate": 256,
                "continuous_playback": True,
                "social_features": True,
                "cdn_endpoints": [
                    "https://cf-media.sndcdn.com",
                    "https://ec-media.soundcloud.com"
                ]
            },
            "twitch": {
                "preferred_protocols": [StreamingProtocol.HTTP_LIVE_STREAMING, StreamingProtocol.RTMP],
                "supported_codecs": ["aac", "mp3"],
                "bitrate_profiles": ["standard_quality", "high_quality"],
                "max_bitrate": 160,
                "low_latency_mode": True,
                "chat_integration": True,
                "vod_support": True
            },
            "discord": {
                "preferred_protocols": [StreamingProtocol.WEBRTC],
                "supported_codecs": ["opus"],
                "bitrate_profiles": ["low_mobile", "standard_quality"],
                "max_bitrate": 128,
                "voice_activity_detection": True,
                "noise_suppression": True,
                "echo_cancellation": True,
                "real_time_processing": True
            }
        }
    
    def _initialize_protocol_configs(self) -> Dict[StreamingProtocol, Dict[str, Any]]:
        """Initialize protocol-specific configurations"""



        return {
            StreamingProtocol.HTTP_LIVE_STREAMING: {
                "name": "HTTP Live Streaming (HLS)",
                "segment_duration": 6.0,
                "playlist_window_size": 3,
                "supported_codecs": ["aac", "mp3"],
                "chunk_format": "ts",
                "encryption_support": True,
                "adaptive_bitrate": True,
                "latency": "medium",
                "browser_support": "excellent",
                "mobile_support": "excellent"
            },
            StreamingProtocol.DASH: {
                "name": "Dynamic Adaptive Streaming (DASH)",
                "segment_duration": 2.0,
                "adaptation_set_switching": True,
                "supported_codecs": ["aac", "mp3", "opus"],
                "chunk_format": "mp4",
                "encryption_support": True,
                "adaptive_bitrate": True,
                "latency": "medium",
                "browser_support": "good",
                "mobile_support": "good"
            },
            StreamingProtocol.WEBRTC: {
                "name": "Web Real-Time Communication",
                "supported_codecs": ["opus", "g722", "pcmu", "pcma"],
                "encryption_mandatory": True,
                "adaptive_bitrate": True,
                "latency": "ultra_low",
                "jitter_buffer": True,
                "packet_loss_recovery": True,
                "browser_support": "excellent",
                "mobile_support": "excellent"
            },
            StreamingProtocol.RTMP: {
                "name": "Real-Time Messaging Protocol",
                "supported_codecs": ["aac", "mp3"],
                "chunk_size": 4096,
                "encryption_support": False,
                "adaptive_bitrate": False,
                "latency": "low",
                "browser_support": "poor",
                "mobile_support": "poor",
                "server_push": True
            },
            StreamingProtocol.ICECAST: {
                "name": "Icecast Streaming",
                "supported_codecs": ["mp3", "ogg", "aac"],
                "metadata_support": True,
                "mount_points": True,
                "listener_limits": True,
                "encryption_support": True,
                "adaptive_bitrate": False,
                "latency": "medium",
                "browser_support": "good",
                "relay_support": True
            }
        }
    
    def _initialize_quality_ladders(self) -> Dict[str, List[str]]:
        """Initialize quality ladders for different use cases"""



        return {
            "music_streaming": [
                "ultra_low_mobile",
                "low_mobile",
                "standard_quality",
                "high_quality",
                "premium_quality",
                "ultra_high_quality"
            ],
            "podcast_streaming": [
                "ultra_low_mobile",
                "low_mobile",
                "standard_quality",
                "high_quality"
            ],
            "live_streaming": [
                "low_mobile",
                "standard_quality",
                "high_quality",
                "premium_quality"
            ],
            "audiophile_streaming": [
                "high_quality",
                "premium_quality",
                "ultra_high_quality",
                "lossless_quality"
            ],
            "voice_chat": [
                "ultra_low_mobile",
                "low_mobile",
                "standard_quality"
            ],
            "gaming_audio": [
                "low_mobile",
                "standard_quality",
                "high_quality"
            ]
        }
    
    def get_protocol_config(self, protocol: StreamingProtocol) -> Dict[str, Any]:
        """
        Get configuration for specific streaming protocol
        
        Args:
            protocol: Streaming protocol
            
        Returns:
            Protocol configuration
        """



        return self._protocol_configs.get(protocol, {})
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """
        Get platform-specific streaming configuration
        
        Args:
            platform: Platform name
            
        Returns:
            Platform configuration
        """



        return self._platform_configs.get(platform.lower(), {})
    
    def get_bitrate_profile(self, profile_name: str) -> Optional[BitrateProfile]:
        """
        Get bitrate profile by name
        
        Args:
            profile_name: Profile name
            
        Returns:
            Bitrate profile or None if not found
        """



        return self._bitrate_profiles.get(profile_name)
    
    def create_adaptive_ladder(self, 
                             use_case: str,
                             network_conditions: List[NetworkCondition],
                             target_devices: List[str]) -> List[BitrateProfile]:
        """
        Create adaptive bitrate ladder for specific requirements
        
        Args:
            use_case: Use case for the streaming
            network_conditions: Expected network conditions
            target_devices: Target device types
            
        Returns:
            List of bitrate profiles forming the ladder
        """



        try:
            # Get base quality ladder for use case
            base_ladder = self._quality_ladders.get(use_case, self._quality_ladders["music_streaming"])
            
            # Filter profiles based on network conditions and devices
            suitable_profiles = []
            
            for profile_name in base_ladder:
                profile = self._bitrate_profiles.get(profile_name)
                if not profile:
                    continue
                
                # Check network compatibility
                network_compatible = any(
                    self._is_network_compatible(profile.network_requirements, condition)
                    for condition in network_conditions
                )
                
                # Check device compatibility
                device_compatible = not target_devices or any(
                    device in profile.target_devices 
                    for device in target_devices
                )
                
                if network_compatible and (device_compatible or not profile.target_devices):
                    suitable_profiles.append(profile)
            
            # Sort by bitrate (ascending)
            suitable_profiles.sort(key=lambda p: p.bitrate_kbps)
            
            # Ensure we have at least 2 profiles for adaptation
            if len(suitable_profiles) < 2:
                # Add fallback profiles
                fallback_profiles = [
                    self._bitrate_profiles["standard_quality"],
                    self._bitrate_profiles["low_mobile"]
                ]
                for fallback in fallback_profiles:
                    if fallback and fallback not in suitable_profiles:
                        suitable_profiles.append(fallback)
                
                suitable_profiles.sort(key=lambda p: p.bitrate_kbps)
            
            return suitable_profiles[:6]  # Limit to 6 profiles max
            
        except Exception as e:
            self.logger.error(f"Adaptive ladder creation failed: {e}")
            return [self._bitrate_profiles["standard_quality"]]
    
    def _is_network_compatible(self, 
                             required_condition: NetworkCondition,
                             available_condition: NetworkCondition) -> bool:
        """Check if network condition is compatible"""
        condition_hierarchy = {
            NetworkCondition.POOR: 1,
            NetworkCondition.FAIR: 2,
            NetworkCondition.GOOD: 3,
            NetworkCondition.EXCELLENT: 4,
            NetworkCondition.UNSTABLE: 1  # Treat as poor
        }
        
        required_level = condition_hierarchy.get(required_condition, 2)
        available_level = condition_hierarchy.get(available_condition, 2)
        
        return available_level >= required_level
    
    def recommend_streaming_protocol(self, 
                                   use_case: str,
                                   target_latency: str = "medium",
                                   device_support: List[str] = None) -> StreamingProtocol:
        """
        Recommend optimal streaming protocol
        
        Args:
            use_case: Streaming use case
            target_latency: Target latency (ultra_low, low, medium, high)
            device_support: Required device support
            
        Returns:
            Recommended streaming protocol
        """



        try:
            device_support = device_support or ["browser", "mobile"]
            
            # Real-time communication use cases
            if "voice" in use_case.lower() or "chat" in use_case.lower():
                if target_latency == "ultra_low":
                    return StreamingProtocol.WEBRTC
            
            # Gaming audio
            if "gaming" in use_case.lower():
                if target_latency in ["ultra_low", "low"]:
                    return StreamingProtocol.WEBRTC
                else:
                    return StreamingProtocol.HTTP_LIVE_STREAMING
            
            # Live streaming
            if "live" in use_case.lower():
                if target_latency == "ultra_low":
                    return StreamingProtocol.WEBRTC
                elif target_latency == "low":
                    return StreamingProtocol.RTMP
                else:
                    return StreamingProtocol.HTTP_LIVE_STREAMING
            
            # Music and podcast streaming
            if any(keyword in use_case.lower() for keyword in ["music", "podcast", "audio"]):
                if "browser" in device_support and "mobile" in device_support:
                    return StreamingProtocol.HTTP_LIVE_STREAMING
                elif "browser" in device_support:
                    return StreamingProtocol.DASH
            
            # Default recommendation
            return StreamingProtocol.HTTP_LIVE_STREAMING
            
        except Exception as e:
            self.logger.error(f"Protocol recommendation failed: {e}")
            return StreamingProtocol.HTTP_LIVE_STREAMING
    
    def create_streaming_config(self, 
                              use_case: str,
                              platform: Optional[str] = None,
                              network_conditions: Optional[List[NetworkCondition]] = None,
                              target_devices: Optional[List[str]] = None,
                              latency_requirement: str = "medium") -> Dict[str, Any]:
        """
        Create complete streaming configuration
        
        Args:
            use_case: Streaming use case
            platform: Target platform
            network_conditions: Expected network conditions
            target_devices: Target device types
            latency_requirement: Latency requirement
            
        Returns:
            Complete streaming configuration
        """



        try:
            # Set defaults
            network_conditions = network_conditions or [NetworkCondition.GOOD, NetworkCondition.FAIR]
            target_devices = target_devices or ["browser", "mobile"]
            
            # Get platform-specific configuration if specified
            platform_config = {}
            if platform:
                platform_config = self.get_platform_config(platform)
            
            # Recommend streaming protocol
            recommended_protocol = self.recommend_streaming_protocol(
                use_case, latency_requirement, target_devices
            )
            
            # Override with platform preference if available
            if platform_config and "preferred_protocols" in platform_config:
                recommended_protocol = StreamingProtocol(platform_config["preferred_protocols"][0])
            
            # Create adaptive bitrate ladder
            bitrate_ladder = self.create_adaptive_ladder(
                use_case, network_conditions, target_devices
            )
            
            # Configure buffering based on latency requirement
            buffer_config = self._get_buffer_config_for_latency(latency_requirement)
            
            # Configure network adaptation
            adaptation_config = self._get_adaptation_config_for_use_case(use_case)
            
            return {
                "use_case": use_case,
                "platform": platform,
                "streaming_protocol": recommended_protocol.value,
                "fallback_protocols": [proto.value for proto in self._fallback_protocols],
                "bitrate_ladder": [
                    {
                        "name": profile.name,
                        "bitrate_kbps": profile.bitrate_kbps,
                        "sample_rate": profile.sample_rate,
                        "channels": profile.channels,
                        "codec": profile.codec,
                        "quality_level": profile.quality_level.value
                    }
                    for profile in bitrate_ladder
                ],
                "buffering_config": buffer_config,
                "network_adaptation": adaptation_config,
                "protocol_settings": self.get_protocol_config(recommended_protocol),
                "platform_settings": platform_config,
                "adaptive_strategy": self._adaptive_strategy.value,
                "quality_ladder": self._quality_ladders.get(use_case, []),
                "cdn_configuration": self._get_cdn_config(platform, network_conditions),
                "security_settings": self._get_security_config(recommended_protocol),
                "monitoring_config": self._get_monitoring_config()
            }
            
        except Exception as e:
            self.logger.error(f"Streaming config creation failed: {e}")
            return {"error": str(e)}
    
    def _get_buffer_config_for_latency(self, latency_requirement: str) -> Dict[str, Any]:
        """Get buffer configuration for latency requirement"""
        if latency_requirement == "ultra_low":
            return {
                "initial_buffer_duration_ms": 100,
                "target_buffer_duration_ms": 500,
                "max_buffer_duration_ms": 1000,
                "rebuffer_threshold_ms": 50,
                "strategy": BufferingStrategy.MINIMAL.value
            }
        elif latency_requirement == "low":
            return {
                "initial_buffer_duration_ms": 500,
                "target_buffer_duration_ms": 1500,
                "max_buffer_duration_ms": 3000,
                "rebuffer_threshold_ms": 200,
                "strategy": BufferingStrategy.STANDARD.value
            }
        elif latency_requirement == "medium":
            return {
                "initial_buffer_duration_ms": self.buffering_config.initial_buffer_duration_ms,
                "target_buffer_duration_ms": self.buffering_config.target_buffer_duration_ms,
                "max_buffer_duration_ms": self.buffering_config.max_buffer_duration_ms,
                "rebuffer_threshold_ms": self.buffering_config.rebuffer_threshold_ms,
                "strategy": BufferingStrategy.ADAPTIVE.value
            }
        else:  # high latency tolerance
            return {
                "initial_buffer_duration_ms": 5000,
                "target_buffer_duration_ms": 10000,
                "max_buffer_duration_ms": 20000,
                "rebuffer_threshold_ms": 1000,
                "strategy": BufferingStrategy.AGGRESSIVE.value
            }
    
    def _get_adaptation_config_for_use_case(self, use_case: str) -> Dict[str, Any]:
        """Get network adaptation configuration for use case"""
        base_config = {
            "bandwidth_estimation_enabled": self.network_adaptation.bandwidth_estimation_enabled,
            "quality_adaptation_enabled": self.network_adaptation.quality_adaptation_enabled,
            "bandwidth_probe_interval_ms": self.network_adaptation.bandwidth_probe_interval_ms
        }
        
        if "voice" in use_case.lower() or "chat" in use_case.lower():
            base_config.update({
                "quality_switch_threshold": 0.1,  # More sensitive for voice
                "stability_requirement_ms": 5000,  # Faster adaptation
                "downgrade_threshold_ratio": 0.9
            })
        elif "music" in use_case.lower():
            base_config.update({
                "quality_switch_threshold": 0.3,  # Less sensitive for music
                "stability_requirement_ms": 15000,  # More stable
                "upgrade_threshold_ratio": 1.5
            })
        
        return base_config
    
    def _get_cdn_config(self, 
                       platform: Optional[str],
                       network_conditions: List[NetworkCondition]) -> Dict[str, Any]:
        """Get CDN configuration"""
        config = {
            "edge_caching_enabled": True,
            "cache_duration_seconds": 3600,
            "geographic_distribution": True,
            "failover_enabled": True
        }
        
        if platform:
            platform_config = self.get_platform_config(platform)
            if "cdn_endpoints" in platform_config:
                config["primary_endpoints"] = platform_config["cdn_endpoints"][:2]
                config["backup_endpoints"] = platform_config["cdn_endpoints"][2:4]
        
        # Adjust based on network conditions
        if NetworkCondition.POOR in network_conditions:
            config.update({
                "aggressive_caching": True,
                "compression_enabled": True,
                "prefetch_enabled": True
            })
        
        return config
    
    def _get_security_config(self, protocol: StreamingProtocol) -> Dict[str, Any]:
        """Get security configuration for protocol"""
        protocol_config = self.get_protocol_config(protocol)
        
        return {
            "encryption_enabled": protocol_config.get("encryption_support", False),
            "token_authentication": True,
            "referer_checking": True,
            "ip_restriction_enabled": False,
            "rate_limiting_enabled": True,
            "max_concurrent_connections": 100,
            "drm_protection": False  # Would be enabled for premium content
        }
    
    def _get_monitoring_config(self) -> Dict[str, Any]:
        """Get streaming monitoring configuration"""



        return {
            "quality_monitoring_enabled": True,
            "bandwidth_monitoring_enabled": True,
            "buffer_health_monitoring": True,
            "error_tracking_enabled": True,
            "performance_analytics": True,
            "real_time_metrics": True,
            "alerting_enabled": True,
            "metrics_retention_days": 30
        }
    
    def add_streaming_endpoint(self, endpoint: StreamingEndpoint) -> bool:
        """
        Add streaming endpoint
        
        Args:
            endpoint: Streaming endpoint configuration
            
        Returns:
            Success status
        """



        try:
            self._streaming_endpoints[endpoint.name] = endpoint
            self.logger.info(f"Added streaming endpoint: {endpoint.name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add streaming endpoint: {e}")
            return False
    
    def get_streaming_endpoints(self) -> Dict[str, StreamingEndpoint]:
        """Get all streaming endpoints"""



        return self._streaming_endpoints.copy()
    
    def validate_streaming_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate streaming configuration
        
        Args:
            config: Streaming configuration to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        is_valid = True
        
        try:
            # Validate required fields
            required_fields = ["use_case", "streaming_protocol", "bitrate_ladder"]
            for field in required_fields:
                if field not in config:
                    errors.append(f"Missing required field: {field}")
                    is_valid = False
            
            # Validate bitrate ladder
            if "bitrate_ladder" in config:
                ladder = config["bitrate_ladder"]
                if not isinstance(ladder, list) or len(ladder) == 0:
                    errors.append("Bitrate ladder must be a non-empty list")
                    is_valid = False
                else:
                    # Check for ascending bitrates
                    bitrates = [profile.get("bitrate_kbps", 0) for profile in ladder]
                    if bitrates != sorted(bitrates):
                        errors.append("Bitrate ladder should be in ascending order")
                        is_valid = False
            
            # Validate protocol
            if "streaming_protocol" in config:
                try:
                    StreamingProtocol(config["streaming_protocol"])
                except ValueError:
                    errors.append(f"Invalid streaming protocol: {config['streaming_protocol']}")
                    is_valid = False
            
            # Validate buffer configuration
            if "buffering_config" in config:
                buffer_config = config["buffering_config"]
                if isinstance(buffer_config, dict):
                    initial = buffer_config.get("initial_buffer_duration_ms", 0)
                    target = buffer_config.get("target_buffer_duration_ms", 0)
                    maximum = buffer_config.get("max_buffer_duration_ms", 0)
                    
                    if not (0 < initial <= target <= maximum):
                        errors.append("Buffer durations must satisfy: 0 < initial <= target <= maximum")
                        is_valid = False
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            is_valid = False
        
        return is_valid, errors
    
    def estimate_bandwidth_requirements(self, 
                                      bitrate_ladder: List[BitrateProfile],
                                      concurrent_streams: int = 1,
                                      overhead_factor: float = 1.2) -> Dict[str, Any]:
        """
        Estimate bandwidth requirements for streaming
        
        Args:
            bitrate_ladder: List of bitrate profiles
            concurrent_streams: Number of concurrent streams
            overhead_factor: Overhead factor for protocol and network
            
        Returns:
            Bandwidth requirements analysis
        """



        try:
            requirements = {}
            
            for profile in bitrate_ladder:
                base_bandwidth = profile.bitrate_kbps
                total_bandwidth = base_bandwidth * concurrent_streams * overhead_factor
                
                requirements[profile.name] = {
                    "bitrate_kbps": profile.bitrate_kbps,
                    "bandwidth_per_stream_kbps": base_bandwidth * overhead_factor,
                    "total_bandwidth_kbps": total_bandwidth,
                    "total_bandwidth_mbps": total_bandwidth / 1000,
                    "quality_level": profile.quality_level.value,
                    "network_requirement": profile.network_requirements.value
                }
            
            # Calculate ranges
            min_bandwidth = min(req["total_bandwidth_kbps"] for req in requirements.values())
            max_bandwidth = max(req["total_bandwidth_kbps"] for req in requirements.values())
            
            return {
                "profiles": requirements,
                "bandwidth_range_kbps": {
                    "minimum": min_bandwidth,
                    "maximum": max_bandwidth,
                    "adaptive_range": max_bandwidth - min_bandwidth
                },
                "concurrent_streams": concurrent_streams,
                "overhead_factor": overhead_factor,
                "recommendations": self._get_bandwidth_recommendations(min_bandwidth, max_bandwidth)
            }
            
        except Exception as e:
            self.logger.error(f"Bandwidth estimation failed: {e}")
            return {"error": str(e)}
    
    def _get_bandwidth_recommendations(self, min_kbps: float, max_kbps: float) -> List[str]:
        """Get bandwidth optimization recommendations"""
        recommendations = []
        
        if max_kbps > 1000:  # > 1 Mbps
            recommendations.append("Consider CDN usage for high-bandwidth streams")
            recommendations.append("Implement aggressive caching for popular content")
        
        if (max_kbps - min_kbps) > 500:  # Large adaptive range
            recommendations.append("Wide adaptive range allows good quality adaptation")
            recommendations.append("Consider more granular quality levels")
        
        if min_kbps < 100:  # Very low minimum
            recommendations.append("Ultra-low bandwidth support enables global accessibility")
            
        return recommendations
    
    def export_config(self) -> Dict[str, Any]:
        """Export complete streaming configuration"""



        try:
            return {
                "primary_protocol": self._primary_protocol.value,
                "fallback_protocols": [proto.value for proto in self._fallback_protocols],
                "adaptive_strategy": self._adaptive_strategy.value,
                "buffering_strategy": self._buffering_strategy.value,
                "buffering_config": {
                    "initial_buffer_duration_ms": self.buffering_config.initial_buffer_duration_ms,
                    "target_buffer_duration_ms": self.buffering_config.target_buffer_duration_ms,
                    "max_buffer_duration_ms": self.buffering_config.max_buffer_duration_ms,
                    "rebuffer_threshold_ms": self.buffering_config.rebuffer_threshold_ms,
                    "buffer_health_threshold": self.buffering_config.buffer_health_threshold,
                    "enable_prebuffering": self.buffering_config.enable_prebuffering,
                    "chunk_duration_ms": self.buffering_config.chunk_duration_ms
                },
                "network_adaptation": {
                    "bandwidth_estimation_enabled": self.network_adaptation.bandwidth_estimation_enabled,
                    "bandwidth_probe_interval_ms": self.network_adaptation.bandwidth_probe_interval_ms,
                    "quality_adaptation_enabled": self.network_adaptation.quality_adaptation_enabled,
                    "quality_switch_threshold": self.network_adaptation.quality_switch_threshold,
                    "downgrade_threshold_ratio": self.network_adaptation.downgrade_threshold_ratio,
                    "upgrade_threshold_ratio": self.network_adaptation.upgrade_threshold_ratio,
                    "stability_requirement_ms": self.network_adaptation.stability_requirement_ms
                },
                "bitrate_profiles": {
                    name: {
                        "name": profile.name,
                        "bitrate_kbps": profile.bitrate_kbps,
                        "sample_rate": profile.sample_rate,
                        "channels": profile.channels,
                        "codec": profile.codec,
                        "quality_level": profile.quality_level.value,
                        "target_devices": profile.target_devices,
                        "network_requirements": profile.network_requirements.value
                    }
                    for name, profile in self._bitrate_profiles.items()
                },
                "streaming_endpoints": {
                    name: {
                        "name": endpoint.name,
                        "url": endpoint.url,
                        "protocol": endpoint.protocol.value,
                        "backup_url": endpoint.backup_url,
                        "auth_required": endpoint.auth_required,
                        "max_concurrent_streams": endpoint.max_concurrent_streams,
                        "geographical_restrictions": endpoint.geographical_restrictions
                    }
                    for name, endpoint in self._streaming_endpoints.items()
                },
                "platform_configs": self._platform_configs,
                "protocol_configs": {
                    protocol.value: config for protocol, config in self._protocol_configs.items()
                },
                "quality_ladders": self._quality_ladders
            }
        except Exception as e:
            self.logger.error(f"Config export failed: {e}")
            return {}
