"""Adaptive Compression Engine with AI Intelligence
Dynamic compression optimization based on content analysis.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content type for adaptive compression."""
    PHOTO = "photo"
    GRAPHICS = "graphics"
    SCREENSHOT = "screenshot"
    ARTWORK = "artwork"
    MUSIC = "music"
    SPEECH = "speech"
    PODCAST = "podcast"
    MOVIE = "movie"
    ANIMATION = "animation"
    DOCUMENTARY = "documentary"

@dataclass
class AdaptiveCompressionResult:
    """Result of adaptive compression analysis."""
    recommended_format: str
    recommended_quality: int
    estimated_size: int
    confidence_score: float
    reasoning: str

class AdaptiveCompressionEngine:
    """AI-driven adaptive compression with content analysis."""
    
    def __init__(self) -> None:
        """Initialize the adaptive compression engine."""
        self.content_analyzers = self._initialize_analyzers()
        
    def _initialize_analyzers(self) -> Dict[str, Any]:
        """Initialize content analysis models."""
        return {
            "image_classifier": self._create_image_classifier(),
            "audio_classifier": self._create_audio_classifier(),
            "video_classifier": self._create_video_classifier()
        }
    
    def _create_image_classifier(self) -> Any:
        """Create image content classifier."""
        # Placeholder for actual ML model
        return {"model": "image_classifier_v1"}
    
    def _create_audio_classifier(self) -> Any:
        """Create audio content classifier."""
        # Placeholder for actual ML model
        return {"model": "audio_classifier_v1"}
    
    def _create_video_classifier(self) -> Any:
        """Create video content classifier."""
        # Placeholder for actual ML model
        return {"model": "video_classifier_v1"}
    
    async def analyze_and_compress(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        target_size: Optional[int] = None,
        quality_priority: str = "balanced"  # quality, size, speed
    ) -> Dict[str, Any]:
        """
        Analyze content and apply optimal compression.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            target_size: Target file size in bytes
            quality_priority: Optimization priority
            
        Returns:
            Compression results with analysis details
        """
        try:
            input_path = Path(input_path)
            
            # Analyze content type
            content_analysis = await self._analyze_content(input_path)
            
            # Get optimal compression settings
            compression_config = await self._get_optimal_config(
                content_analysis, target_size, quality_priority
            )
            
            # Apply compression
            result = await self._apply_compression(
                input_path, output_path, compression_config
            )
            
            return {
                "success": True,
                "content_type": content_analysis["type"],
                "confidence": content_analysis["confidence"],
                "compression_config": compression_config,
                "result": result,
                "reasoning": compression_config["reasoning"]
            }
            
        except Exception as e:
            logger.error(f"Adaptive compression failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _analyze_content(self, input_path: Path) -> Dict[str, Any]:
        """Analyze content to determine optimal compression approach."""
        file_ext = input_path.suffix.lower()
        
        if file_ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
            return await self._analyze_image_content(input_path)
        elif file_ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
            return await self._analyze_audio_content(input_path)
        elif file_ext in ['.mp4', '.avi', '.mov', '.webm', '.mkv']:
            return await self._analyze_video_content(input_path)
        else:
            return {
                "type": "unknown",
                "confidence": 0.0,
                "characteristics": {}
            }
    
    async def _analyze_image_content(self, input_path: Path) -> Dict[str, Any]:
        """Analyze image content characteristics."""
        # Simulate AI-based image analysis
        await asyncio.sleep(0.05)
        
        # Mock analysis results
        characteristics = {
            "has_transparency": False,
            "color_complexity": "high",
            "edge_density": "medium",
            "noise_level": "low",
            "compression_artifacts": False
        }
        
        # Determine content type based on characteristics
        if characteristics["edge_density"] == "high":
            content_type = ContentType.GRAPHICS
        elif characteristics["color_complexity"] == "low":
            content_type = ContentType.SCREENSHOT
        else:
            content_type = ContentType.PHOTO
        
        return {
            "type": content_type.value,
            "confidence": 0.85,
            "characteristics": characteristics
        }
    
    async def _analyze_audio_content(self, input_path: Path) -> Dict[str, Any]:
        """Analyze audio content characteristics."""
        # Simulate AI-based audio analysis
        await asyncio.sleep(0.03)
        
        characteristics = {
            "dynamic_range": "high",
            "frequency_distribution": "full_spectrum",
            "speech_ratio": 0.2,
            "music_ratio": 0.8,
            "noise_level": "low"
        }
        
        # Determine content type
        if characteristics["speech_ratio"] > 0.7:
            content_type = ContentType.SPEECH
        elif characteristics["music_ratio"] > 0.6:
            content_type = ContentType.MUSIC
        else:
            content_type = ContentType.PODCAST
        
        return {
            "type": content_type.value,
            "confidence": 0.90,
            "characteristics": characteristics
        }
    
    async def _analyze_video_content(self, input_path: Path) -> Dict[str, Any]:
        """Analyze video content characteristics."""
        # Simulate AI-based video analysis
        await asyncio.sleep(0.10)
        
        characteristics = {
            "motion_intensity": "medium",
            "scene_complexity": "high",
            "color_variance": "high",
            "temporal_redundancy": "medium",
            "has_fast_motion": False
        }
        
        # Determine content type
        if characteristics["motion_intensity"] == "high":
            content_type = ContentType.MOVIE
        elif characteristics["scene_complexity"] == "low":
            content_type = ContentType.ANIMATION
        else:
            content_type = ContentType.DOCUMENTARY
        
        return {
            "type": content_type.value,
            "confidence": 0.78,
            "characteristics": characteristics
        }
    
    async def _get_optimal_config(
        self,
        content_analysis: Dict[str, Any],
        target_size: Optional[int],
        quality_priority: str
    ) -> Dict[str, Any]:
        """Determine optimal compression configuration."""
        content_type = content_analysis["type"]
        characteristics = content_analysis["characteristics"]
        
        # Define compression strategies per content type
        strategies = {
            ContentType.PHOTO.value: {
                "format": "jpeg",
                "quality": 85,
                "reasoning": "Natural photos benefit from JPEG compression"
            },
            ContentType.GRAPHICS.value: {
                "format": "png",
                "quality": 95,
                "reasoning": "Graphics with sharp edges need lossless compression"
            },
            ContentType.SCREENSHOT.value: {
                "format": "webp",
                "quality": 80,
                "reasoning": "Screenshots compress well with WebP"
            },
            ContentType.MUSIC.value: {
                "format": "aac",
                "bitrate": 256,
                "reasoning": "Music requires high bitrate for quality"
            },
            ContentType.SPEECH.value: {
                "format": "opus",
                "bitrate": 64,
                "reasoning": "Speech compresses efficiently with Opus"
            },
            ContentType.MOVIE.value: {
                "format": "h264",
                "bitrate": 5000,
                "reasoning": "Movies need balanced compression for streaming"
            },
            ContentType.ANIMATION.value: {
                "format": "h265",
                "bitrate": 3000,
                "reasoning": "Animation compresses well with HEVC"
            }
        }
        
        base_config = strategies.get(content_type, {
            "format": "auto",
            "quality": 80,
            "reasoning": "Default balanced compression"
        })
        
        # Adjust based on priority
        if quality_priority == "quality":
            if "quality" in base_config:
                base_config["quality"] = min(95, base_config["quality"] + 10)
            if "bitrate" in base_config:
                base_config["bitrate"] = int(base_config["bitrate"] * 1.5)
        elif quality_priority == "size":
            if "quality" in base_config:
                base_config["quality"] = max(60, base_config["quality"] - 15)
            if "bitrate" in base_config:
                base_config["bitrate"] = int(base_config["bitrate"] * 0.7)
        
        # Adjust for target size
        if target_size:
            base_config["target_size"] = target_size
            base_config["reasoning"] += f" (target size: {target_size} bytes)"
        
        return base_config
    
    async def _apply_compression(
        self,
        input_path: Path,
        output_path: Path,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply the determined compression configuration."""
        # Simulate compression application
        await asyncio.sleep(0.05)
        
        original_size = input_path.stat().st_size
        
        # Estimate compressed size based on configuration
        if config.get("format") in ["jpeg", "webp", "aac", "h264"]:
            compression_ratio = 0.3
        elif config.get("format") in ["png", "flac", "h265"]:
            compression_ratio = 0.5
        else:
            compression_ratio = 0.4
        
        # Adjust for quality/bitrate
        quality = config.get("quality", 80)
        compression_ratio *= (quality / 100.0)
        
        compressed_size = int(original_size * compression_ratio)
        
        # Apply target size constraint
        target_size = config.get("target_size")
        if target_size and compressed_size > target_size:
            compressed_size = target_size
        
        return {
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": original_size / compressed_size,
            "format_used": config.get("format", "auto"),
            "settings_used": config
        }
    
    async def batch_adaptive_compress(
        self,
        input_files: List[Union[str, Path]],
        output_directory: Union[str, Path],
        target_size_per_file: Optional[int] = None,
        quality_priority: str = "balanced"
    ) -> List[Dict[str, Any]]:
        """Apply adaptive compression to multiple files."""
        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        for input_file in input_files:
            input_path = Path(input_file)
            output_path = output_dir / f"{input_path.stem}_adaptive{input_path.suffix}"
            
            result = await self.analyze_and_compress(
                input_path, output_path, target_size_per_file, quality_priority
            )
            results.append(result)
        
        return results
    
    def get_compression_recommendations(
        self,
        file_info: Dict[str, Any],
        use_case: str = "web"
    ) -> List[Dict[str, Any]]:
        """Get compression recommendations for a file."""
        file_type = file_info.get("type", "unknown")
        file_size = file_info.get("size", 0)
        
        recommendations = []
        
        if use_case == "web":
            if file_type == "image":
                recommendations.extend([
                    {
                        "strategy": "WebP conversion",
                        "estimated_savings": "25-35%",
                        "quality_impact": "Minimal",
                        "browser_support": "95%+"
                    },
                    {
                        "strategy": "AVIF conversion",
                        "estimated_savings": "40-50%",
                        "quality_impact": "None",
                        "browser_support": "75%+"
                    }
                ])
            elif file_type == "video":
                recommendations.append({
                    "strategy": "H.265 encoding",
                    "estimated_savings": "30-40%",
                    "quality_impact": "Minimal",
                    "compatibility": "Modern devices"
                })
        
        elif use_case == "mobile":
            recommendations.append({
                "strategy": "Aggressive compression",
                "estimated_savings": "50-70%",
                "quality_impact": "Moderate",
                "benefit": "Faster loading on mobile"
            })
        
        return recommendations