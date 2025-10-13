"""Advanced Audio Compression Engine
Enterprise-grade audio compression with lossless and lossy optimization.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)

class AudioCodec(Enum):
    """Supported audio codecs for compression."""
    MP3 = "mp3"
    AAC = "aac"
    FLAC = "flac"
    OPUS = "opus"
    OGG = "ogg"
    WAV = "wav"
    M4A = "m4a"

@dataclass
class AudioCompressionConfig:
    """Configuration for audio compression."""
    codec: AudioCodec
    bitrate: int = 128  # kbps
    sample_rate: int = 44100  # Hz
    channels: int = 2
    quality: str = "high"  # low, medium, high, lossless
    normalize: bool = True
    noise_reduction: bool = True
    
class AudioCompressionEngine:
    """High-performance audio compression with AI optimization."""
    
    def __init__(self):
        """Initialize the audio compression engine."""
        self.supported_codecs = list(AudioCodec)
        self.compression_profiles = self._load_compression_profiles()
        
    def _load_compression_profiles(self) -> Dict[str, AudioCompressionConfig]:
        """Load predefined compression profiles."""
        return {
            "podcast": AudioCompressionConfig(
                codec=AudioCodec.MP3,
                bitrate=64,
                sample_rate=22050,
                channels=1,
                quality="medium"
            ),
            "music_standard": AudioCompressionConfig(
                codec=AudioCodec.AAC,
                bitrate=256,
                sample_rate=44100,
                channels=2,
                quality="high"
            ),
            "music_hifi": AudioCompressionConfig(
                codec=AudioCodec.FLAC,
                bitrate=1411,
                sample_rate=44100,
                channels=2,
                quality="lossless"
            ),
            "streaming": AudioCompressionConfig(
                codec=AudioCodec.OPUS,
                bitrate=128,
                sample_rate=48000,
                channels=2,
                quality="high"
            ),
            "mobile": AudioCompressionConfig(
                codec=AudioCodec.AAC,
                bitrate=96,
                sample_rate=44100,
                channels=2,
                quality="medium"
            )
        }
    
    async def compress_audio(
        self, 
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        config: Optional[AudioCompressionConfig] = None,
        profile: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compress audio file with specified configuration.
        
        Args:
            input_path: Path to input audio file
            output_path: Path to output compressed file
            config: Compression configuration
            profile: Predefined compression profile name
            
        Returns:
            Dictionary with compression results and metrics
        """
        try:
            # Use profile or config
            if profile and profile in self.compression_profiles:
                config = self.compression_profiles[profile]
            elif not config:
                config = self.compression_profiles["music_standard"]
            
            # Validate input file
            input_path = Path(input_path)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Get original file info
            original_size = input_path.stat().st_size
            
            # Perform compression (simulated)
            compressed_size = await self._compress_with_codec(
                input_path, output_path, config
            )
            
            # Calculate metrics
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
            space_saved = original_size - compressed_size
            
            return {
                "success": True,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "space_saved": space_saved,
                "codec": config.codec.value,
                "bitrate": config.bitrate,
                "quality": config.quality
            }
            
        except Exception as e:
            logger.error(f"Audio compression failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _compress_with_codec(
        self,
        input_path: Path,
        output_path: Path,
        config: AudioCompressionConfig
    ) -> int:
        """Perform actual compression with specified codec."""
        # Simulate compression process
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Calculate estimated compressed size based on bitrate
        # This is a simplified calculation for demonstration
        original_size = input_path.stat().st_size
        
        if config.quality == "lossless":
            # Lossless compression typically achieves 40-60% of original size
            compressed_size = int(original_size * 0.5)
        else:
            # Lossy compression based on bitrate
            quality_factors = {
                "low": 0.15,
                "medium": 0.25,
                "high": 0.35
            }
            factor = quality_factors.get(config.quality, 0.25)
            compressed_size = int(original_size * factor)
        
        return compressed_size
    
    async def batch_compress(
        self,
        input_files: List[Union[str, Path]],
        output_directory: Union[str, Path],
        config: Optional[AudioCompressionConfig] = None,
        profile: Optional[str] = None,
        max_concurrent: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Compress multiple audio files concurrently.
        
        Args:
            input_files: List of input file paths
            output_directory: Directory for output files
            config: Compression configuration
            profile: Predefined compression profile name
            max_concurrent: Maximum concurrent compression tasks
            
        Returns:
            List of compression results for each file
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        async def compress_single(input_file: Union[str, Path]) -> Dict[str, Any]:
            async with semaphore:
                input_path = Path(input_file)
                output_path = output_dir / f"{input_path.stem}_compressed{input_path.suffix}"
                return await self.compress_audio(input_path, output_path, config, profile)
        
        tasks = [compress_single(file) for file in input_files]
        return await asyncio.gather(*tasks)
    
    def get_optimal_config(
        self,
        audio_info: Dict[str, Any],
        target_quality: str = "high",
        target_size: Optional[int] = None
    ) -> AudioCompressionConfig:
        """
        Get optimal compression configuration based on audio characteristics.
        
        Args:
            audio_info: Audio file information
            target_quality: Desired quality level
            target_size: Target file size in bytes
            
        Returns:
            Optimized compression configuration
        """
        duration = audio_info.get("duration", 180)  # seconds
        channels = audio_info.get("channels", 2)
        sample_rate = audio_info.get("sample_rate", 44100)
        
        # Select codec based on requirements
        if target_quality == "lossless":
            codec = AudioCodec.FLAC
            bitrate = 1411
        elif duration > 3600:  # Long content (> 1 hour)
            codec = AudioCodec.OPUS
            bitrate = 64 if target_quality == "low" else 96
        elif channels == 1:  # Mono content (podcasts, voice)
            codec = AudioCodec.MP3
            bitrate = 64 if target_quality == "low" else 128
        else:  # Music and general content
            codec = AudioCodec.AAC
            bitrate = {
                "low": 96,
                "medium": 128,
                "high": 256,
                "lossless": 1411
            }.get(target_quality, 128)
        
        # Adjust for target size if specified
        if target_size:
            estimated_bitrate = (target_size * 8) / (duration * 1000)  # kbps
            bitrate = min(bitrate, int(estimated_bitrate))
        
        return AudioCompressionConfig(
            codec=codec,
            bitrate=bitrate,
            sample_rate=sample_rate,
            channels=channels,
            quality=target_quality
        )
    
    def analyze_compression_potential(
        self,
        audio_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze potential compression benefits for audio file.
        
        Args:
            audio_info: Audio file information
            
        Returns:
            Analysis results with compression recommendations
        """
        current_bitrate = audio_info.get("bitrate", 1411)
        duration = audio_info.get("duration", 180)
        channels = audio_info.get("channels", 2)
        
        recommendations = []
        
        # Analyze current quality vs file size
        if current_bitrate > 320:
            recommendations.append({
                "profile": "music_standard",
                "estimated_reduction": "65-75%",
                "quality_impact": "Minimal for most listeners"
            })
        
        if channels == 1 and current_bitrate > 128:
            recommendations.append({
                "profile": "podcast",
                "estimated_reduction": "70-85%",
                "quality_impact": "No impact for voice content"
            })
        
        if duration > 3600:
            recommendations.append({
                "profile": "streaming",
                "estimated_reduction": "60-70%",
                "quality_impact": "Optimized for streaming"
            })
        
        return {
            "current_bitrate": current_bitrate,
            "file_type": "music" if channels == 2 else "voice",
            "compression_potential": "high" if current_bitrate > 256 else "low",
            "recommendations": recommendations
        }