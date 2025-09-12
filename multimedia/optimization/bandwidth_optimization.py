"""
Ainflue Platform - Multimedia Optimization - Bandwidth Optimization
Professional bandwidth optimization for multimedia content delivery

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.1.0 Enterprise
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    """Network connection types"""
    FIBER = "fiber"
    BROADBAND = "broadband"
    WIFI = "wifi"
    MOBILE_5G = "mobile_5g"
    MOBILE_4G = "mobile_4g"
    MOBILE_3G = "mobile_3g"
    SATELLITE = "satellite"
    DIAL_UP = "dial_up"


class QualityLevel(Enum):
    """Quality levels for adaptive streaming"""
    AUTO = "auto"
    ULTRA_HIGH = "ultra_high"  # 4K
    HIGH = "high"              # 1080p
    MEDIUM = "medium"          # 720p
    LOW = "low"               # 480p
    VERY_LOW = "very_low"     # 240p


@dataclass
class BandwidthProfile:
    """Bandwidth profile configuration"""
    connection_type: ConnectionType
    download_speed: int  # Mbps
    upload_speed: int    # Mbps
    latency: int        # ms
    packet_loss: float  # percentage
    stability: float    # 0-1 (1 = very stable)
    data_cap: Optional[int] = None  # GB per month


@dataclass
class AdaptiveSettings:
    """Adaptive streaming settings"""
    min_bitrate: int = 500      # kbps
    max_bitrate: int = 8000     # kbps
    initial_bitrate: int = 2000 # kbps
    buffer_size: int = 30       # seconds
    quality_levels: List[QualityLevel] = field(default_factory=list)
    enable_quality_switching: bool = True
    aggressive_switching: bool = False


class BandwidthOptimizer:
    """Professional bandwidth optimization system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize bandwidth optimizer"""
        self.config = config or {}
        self.connection_profiles = self._initialize_connection_profiles()
        self.quality_presets = self._initialize_quality_presets()
        self.adaptive_algorithms = self._initialize_adaptive_algorithms()
        
    def _initialize_connection_profiles(self) -> Dict[ConnectionType, BandwidthProfile]:
        """Initialize standard connection profiles"""
        return {
            ConnectionType.FIBER: BandwidthProfile(
                connection_type=ConnectionType.FIBER,
                download_speed=1000,
                upload_speed=1000,
                latency=5,
                packet_loss=0.01,
                stability=0.99
            ),
            ConnectionType.BROADBAND: BandwidthProfile(
                connection_type=ConnectionType.BROADBAND,
                download_speed=100,
                upload_speed=20,
                latency=20,
                packet_loss=0.1,
                stability=0.95
            ),
            ConnectionType.WIFI: BandwidthProfile(
                connection_type=ConnectionType.WIFI,
                download_speed=50,
                upload_speed=10,
                latency=30,
                packet_loss=0.5,
                stability=0.85
            ),
            ConnectionType.MOBILE_5G: BandwidthProfile(
                connection_type=ConnectionType.MOBILE_5G,
                download_speed=200,
                upload_speed=50,
                latency=20,
                packet_loss=0.2,
                stability=0.90
            ),
            ConnectionType.MOBILE_4G: BandwidthProfile(
                connection_type=ConnectionType.MOBILE_4G,
                download_speed=50,
                upload_speed=10,
                latency=50,
                packet_loss=1.0,
                stability=0.80,
                data_cap=50
            ),
            ConnectionType.MOBILE_3G: BandwidthProfile(
                connection_type=ConnectionType.MOBILE_3G,
                download_speed=5,
                upload_speed=1,
                latency=200,
                packet_loss=2.0,
                stability=0.70,
                data_cap=10
            ),
            ConnectionType.SATELLITE: BandwidthProfile(
                connection_type=ConnectionType.SATELLITE,
                download_speed=25,
                upload_speed=3,
                latency=600,
                packet_loss=0.5,
                stability=0.75,
                data_cap=100
            )
        }
    
    def _initialize_quality_presets(self) -> Dict[QualityLevel, Dict[str, Any]]:
        """Initialize quality level presets"""
        return {
            QualityLevel.ULTRA_HIGH: {
                "video_bitrate": 8000,  # kbps
                "audio_bitrate": 320,
                "resolution": (3840, 2160),
                "framerate": 60,
                "codec": "h265"
            },
            QualityLevel.HIGH: {
                "video_bitrate": 5000,
                "audio_bitrate": 192,
                "resolution": (1920, 1080),
                "framerate": 30,
                "codec": "h264"
            },
            QualityLevel.MEDIUM: {
                "video_bitrate": 2500,
                "audio_bitrate": 128,
                "resolution": (1280, 720),
                "framerate": 30,
                "codec": "h264"
            },
            QualityLevel.LOW: {
                "video_bitrate": 1000,
                "audio_bitrate": 96,
                "resolution": (854, 480),
                "framerate": 25,
                "codec": "h264"
            },
            QualityLevel.VERY_LOW: {
                "video_bitrate": 500,
                "audio_bitrate": 64,
                "resolution": (426, 240),
                "framerate": 15,
                "codec": "h264"
            }
        }
    
    def _initialize_adaptive_algorithms(self) -> Dict[str, Dict[str, Any]]:
        """Initialize adaptive streaming algorithms"""
        return {
            "conservative": {
                "buffer_threshold_up": 15,    # seconds
                "buffer_threshold_down": 5,   # seconds
                "quality_increase_delay": 3,  # seconds
                "quality_decrease_immediate": True,
                "max_quality_jumps": 1
            },
            "aggressive": {
                "buffer_threshold_up": 10,
                "buffer_threshold_down": 3,
                "quality_increase_delay": 1,
                "quality_decrease_immediate": True,
                "max_quality_jumps": 2
            },
            "battery_optimized": {
                "buffer_threshold_up": 20,
                "buffer_threshold_down": 8,
                "quality_increase_delay": 5,
                "quality_decrease_immediate": False,
                "max_quality_jumps": 1,
                "prefer_lower_quality": True
            }
        }
    
    async def detect_connection_type(self) -> ConnectionType:
        """Detect user's connection type"""
        try:
            # Simplified connection detection
            # In production, would use actual network measurement
            speed_test_result = await self._perform_speed_test()
            latency = await self._measure_latency()
            
            if speed_test_result["download"] > 500:
                return ConnectionType.FIBER
            elif speed_test_result["download"] > 50:
                return ConnectionType.BROADBAND
            elif speed_test_result["download"] > 20 and latency < 50:
                return ConnectionType.WIFI
            elif speed_test_result["download"] > 100 and latency < 30:
                return ConnectionType.MOBILE_5G
            elif speed_test_result["download"] > 10:
                return ConnectionType.MOBILE_4G
            elif speed_test_result["download"] > 1:
                return ConnectionType.MOBILE_3G
            else:
                return ConnectionType.SATELLITE
                
        except Exception as e:
            logger.error(f"Error detecting connection type: {e}")
            return ConnectionType.BROADBAND  # Default fallback
    
    async def _perform_speed_test(self) -> Dict[str, float]:
        """Perform network speed test"""
        try:
            # Simplified speed test simulation
            # In production, would perform actual bandwidth measurement
            return {
                "download": 50.0,  # Mbps
                "upload": 10.0,    # Mbps
                "ping": 30.0       # ms
            }
            
        except Exception as e:
            logger.error(f"Error performing speed test: {e}")
            return {"download": 10.0, "upload": 2.0, "ping": 100.0}
    
    async def _measure_latency(self) -> float:
        """Measure network latency"""
        try:
            # Simplified latency measurement
            start_time = time.time()
            # Simulate network round trip
            await asyncio.sleep(0.03)  # 30ms simulation
            end_time = time.time()
            
            return (end_time - start_time) * 1000  # Convert to milliseconds
            
        except Exception as e:
            logger.error(f"Error measuring latency: {e}")
            return 100.0  # Default 100ms
    
    async def optimize_for_bandwidth(
        self,
        content_path: str,
        target_connection: Optional[ConnectionType] = None,
        preserve_quality: bool = False
    ) -> Dict[str, Any]:
        """Optimize content for specific bandwidth constraints"""
        try:
            if target_connection is None:
                target_connection = await self.detect_connection_type()
            
            profile = self.connection_profiles[target_connection]
            
            # Calculate optimal settings
            available_bandwidth = profile.download_speed * 1000  # Convert to kbps
            recommended_bitrate = int(available_bandwidth * 0.8)  # Use 80% of available bandwidth
            
            # Select appropriate quality level
            optimal_quality = self._select_optimal_quality(recommended_bitrate, preserve_quality)
            quality_settings = self.quality_presets[optimal_quality]
            
            optimization_settings = {
                "target_connection": target_connection.value,
                "available_bandwidth": available_bandwidth,
                "recommended_bitrate": recommended_bitrate,
                "optimal_quality": optimal_quality.value,
                "video_settings": {
                    "bitrate": min(quality_settings["video_bitrate"], recommended_bitrate - quality_settings["audio_bitrate"]),
                    "resolution": quality_settings["resolution"],
                    "framerate": quality_settings["framerate"],
                    "codec": quality_settings["codec"]
                },
                "audio_settings": {
                    "bitrate": quality_settings["audio_bitrate"],
                    "codec": "aac"
                },
                "adaptive_streaming": self._generate_adaptive_settings(profile)
            }
            
            return optimization_settings
            
        except Exception as e:
            logger.error(f"Error optimizing for bandwidth: {e}")
            raise
    
    def _select_optimal_quality(
        self,
        available_bitrate: int,
        preserve_quality: bool = False
    ) -> QualityLevel:
        """Select optimal quality level based on available bitrate"""
        try:
            quality_levels = [
                (QualityLevel.ULTRA_HIGH, 8000),
                (QualityLevel.HIGH, 5000),
                (QualityLevel.MEDIUM, 2500),
                (QualityLevel.LOW, 1000),
                (QualityLevel.VERY_LOW, 500)
            ]
            
            if preserve_quality:
                # Try to maintain higher quality when possible
                for quality, required_bitrate in quality_levels:
                    if available_bitrate >= required_bitrate * 1.2:  # 20% buffer
                        return quality
            else:
                # Conservative approach - ensure smooth streaming
                for quality, required_bitrate in quality_levels:
                    if available_bitrate >= required_bitrate * 1.5:  # 50% buffer
                        return quality
            
            return QualityLevel.VERY_LOW  # Fallback
            
        except Exception as e:
            logger.error(f"Error selecting optimal quality: {e}")
            return QualityLevel.LOW
    
    def _generate_adaptive_settings(
        self,
        profile: BandwidthProfile
    ) -> AdaptiveSettings:
        """Generate adaptive streaming settings for connection profile"""
        try:
            max_bitrate = int(profile.download_speed * 1000 * 0.8)  # 80% of available bandwidth
            min_bitrate = max(500, int(max_bitrate * 0.1))  # At least 10% or 500kbps
            initial_bitrate = int(max_bitrate * 0.3)  # Start conservatively
            
            # Adjust buffer size based on connection stability
            buffer_size = 30  # Default
            if profile.stability < 0.8:
                buffer_size = 45  # Larger buffer for unstable connections
            elif profile.stability > 0.95:
                buffer_size = 15  # Smaller buffer for stable connections
            
            # Select appropriate quality levels
            available_qualities = []
            for quality, settings in self.quality_presets.items():
                if settings["video_bitrate"] + settings["audio_bitrate"] <= max_bitrate:
                    available_qualities.append(quality)
            
            return AdaptiveSettings(
                min_bitrate=min_bitrate,
                max_bitrate=max_bitrate,
                initial_bitrate=initial_bitrate,
                buffer_size=buffer_size,
                quality_levels=available_qualities,
                enable_quality_switching=True,
                aggressive_switching=profile.stability > 0.9
            )
            
        except Exception as e:
            logger.error(f"Error generating adaptive settings: {e}")
            return AdaptiveSettings()
    
    async def monitor_bandwidth_usage(
        self,
        session_id: str,
        duration: int = 300  # 5 minutes
    ) -> Dict[str, Any]:
        """Monitor bandwidth usage during streaming session"""
        try:
            monitoring_data = {
                "session_id": session_id,
                "duration": duration,
                "start_time": time.time(),
                "bandwidth_samples": [],
                "quality_changes": [],
                "buffer_events": [],
                "average_bitrate": 0,
                "peak_bitrate": 0,
                "total_data_consumed": 0
            }
            
            # Simulate bandwidth monitoring
            sample_interval = 5  # seconds
            samples = duration // sample_interval
            
            current_bitrate = 2000  # Start with 2Mbps
            total_bits = 0
            
            for i in range(samples):
                # Simulate bandwidth fluctuation
                bandwidth_sample = {
                    "timestamp": time.time(),
                    "current_bitrate": current_bitrate,
                    "buffer_level": 15 + (i % 10),  # Simulate buffer level
                    "quality_level": "medium"
                }
                
                monitoring_data["bandwidth_samples"].append(bandwidth_sample)
                total_bits += current_bitrate * sample_interval
                
                # Simulate quality adaptation
                if i % 20 == 0 and i > 0:  # Quality change every 100 seconds
                    old_quality = bandwidth_sample["quality_level"]
                    new_quality = "high" if current_bitrate < 3000 else "medium"
                    
                    if old_quality != new_quality:
                        monitoring_data["quality_changes"].append({
                            "timestamp": time.time(),
                            "from_quality": old_quality,
                            "to_quality": new_quality,
                            "reason": "bandwidth_adaptation"
                        })
                        
                        current_bitrate = 3000 if new_quality == "high" else 2000
                
                await asyncio.sleep(0.1)  # Small delay to simulate real monitoring
            
            # Calculate statistics
            bitrates = [sample["current_bitrate"] for sample in monitoring_data["bandwidth_samples"]]
            monitoring_data["average_bitrate"] = sum(bitrates) / len(bitrates) if bitrates else 0
            monitoring_data["peak_bitrate"] = max(bitrates) if bitrates else 0
            monitoring_data["total_data_consumed"] = total_bits / 8 / 1024 / 1024  # Convert to MB
            
            return monitoring_data
            
        except Exception as e:
            logger.error(f"Error monitoring bandwidth usage: {e}")
            raise
    
    async def predict_bandwidth_requirements(
        self,
        content_metadata: Dict[str, Any],
        viewing_pattern: str = "normal"
    ) -> Dict[str, Any]:
        """Predict bandwidth requirements for content"""
        try:
            duration = content_metadata.get("duration", 3600)  # Default 1 hour
            resolution = content_metadata.get("resolution", (1920, 1080))
            has_audio = content_metadata.get("has_audio", True)
            
            # Base bitrate calculation based on resolution
            base_video_bitrate = self._calculate_base_bitrate(resolution)
            audio_bitrate = 128 if has_audio else 0
            total_bitrate = base_video_bitrate + audio_bitrate
            
            # Adjust for viewing pattern
            pattern_multipliers = {
                "casual": 0.8,      # Lower quality acceptable
                "normal": 1.0,      # Standard quality
                "critical": 1.5,    # High quality required
                "professional": 2.0  # Maximum quality
            }
            
            adjusted_bitrate = total_bitrate * pattern_multipliers.get(viewing_pattern, 1.0)
            
            # Calculate total data consumption
            total_data_mb = (adjusted_bitrate * duration) / 8 / 1024  # Convert to MB
            
            # Generate recommendations for different connection types
            recommendations = {}
            for conn_type, profile in self.connection_profiles.items():
                available_bandwidth = profile.download_speed * 1000  # kbps
                
                if adjusted_bitrate <= available_bandwidth * 0.8:
                    quality = "excellent"
                elif adjusted_bitrate <= available_bandwidth:
                    quality = "good"
                elif adjusted_bitrate <= available_bandwidth * 1.5:
                    quality = "acceptable_with_buffering"
                else:
                    quality = "poor"
                
                recommendations[conn_type.value] = {
                    "quality": quality,
                    "recommended_bitrate": min(adjusted_bitrate, int(available_bandwidth * 0.8)),
                    "estimated_buffering": max(0, (adjusted_bitrate - available_bandwidth) / available_bandwidth * 100),
                    "data_usage_mb": total_data_mb
                }
            
            return {
                "content_metadata": content_metadata,
                "viewing_pattern": viewing_pattern,
                "predicted_requirements": {
                    "total_bitrate_kbps": adjusted_bitrate,
                    "video_bitrate_kbps": base_video_bitrate,
                    "audio_bitrate_kbps": audio_bitrate,
                    "total_data_mb": total_data_mb,
                    "duration_seconds": duration
                },
                "connection_recommendations": recommendations,
                "optimization_suggestions": self._generate_optimization_suggestions(total_bitrate, resolution)
            }
            
        except Exception as e:
            logger.error(f"Error predicting bandwidth requirements: {e}")
            raise
    
    def _calculate_base_bitrate(self, resolution: Tuple[int, int]) -> int:
        """Calculate base video bitrate for resolution"""
        try:
            width, height = resolution
            pixels = width * height
            
            # Bitrate calculation based on pixel count
            if pixels >= 3840 * 2160:  # 4K
                return 8000
            elif pixels >= 1920 * 1080:  # 1080p
                return 5000
            elif pixels >= 1280 * 720:   # 720p
                return 2500
            elif pixels >= 854 * 480:    # 480p
                return 1000
            else:  # 240p and below
                return 500
                
        except Exception as e:
            logger.error(f"Error calculating base bitrate: {e}")
            return 2000  # Default
    
    def _generate_optimization_suggestions(
        self,
        current_bitrate: int,
        resolution: Tuple[int, int]
    ) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        try:
            if current_bitrate > 5000:
                suggestions.append("Consider reducing bitrate for better compatibility")
            
            if resolution[0] > 1920:
                suggestions.append("4K content may require high-speed connections")
            
            if current_bitrate < 1000:
                suggestions.append("Very low bitrate may impact visual quality")
            
            suggestions.extend([
                "Enable adaptive streaming for optimal experience",
                "Consider multiple quality levels for different devices",
                "Implement progressive download for better user experience"
            ])
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating optimization suggestions: {e}")
            return ["Enable adaptive streaming for optimal experience"]


# Export main classes
__all__ = [
    'BandwidthOptimizer',
    'BandwidthProfile',
    'AdaptiveSettings',
    'ConnectionType',
    'QualityLevel'
]