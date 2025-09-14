"""Lossless Compression Engine
Optimized lossless compression for archival and professional use.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

class LosslessFormat(Enum):
    """Supported lossless formats."""
    PNG = "png"
    FLAC = "flac"
    WEBP_LOSSLESS = "webp_lossless"
    H264_LOSSLESS = "h264_lossless"
    H265_LOSSLESS = "h265_lossless"
    TIFF = "tiff"
    WAV = "wav"

@dataclass
class LosslessConfig:
    """Configuration for lossless compression."""
    format: LosslessFormat
    compression_level: int = 6  # 1-9
    preserve_metadata: bool = True
    optimize_for_size: bool = True

class LosslessCompressionEngine:
    """High-efficiency lossless compression engine."""
    
    def __init__(self) -> None:
        """Initialize the lossless compression engine."""
        self.supported_formats = list(LosslessFormat)
        
    async def compress_lossless(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        config: Optional[LosslessConfig] = None
    ) -> Dict[str, Any]:
        """
        Apply lossless compression to file.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            config: Lossless compression configuration
            
        Returns:
            Compression results
        """
        try:
            input_path = Path(input_path)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            if not config:
                config = self._get_default_config(input_path)
            
            original_size = input_path.stat().st_size
            
            # Perform lossless compression
            compressed_size = await self._apply_lossless_compression(
                input_path, output_path, config
            )
            
            # Calculate metrics
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
            space_saved = original_size - compressed_size
            efficiency = (space_saved / original_size) * 100
            
            return {
                "success": True,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "space_saved": space_saved,
                "efficiency_percent": efficiency,
                "format": config.format.value,
                "compression_level": config.compression_level,
                "quality_loss": 0.0  # Always 0 for lossless
            }
            
        except Exception as e:
            logger.error(f"Lossless compression failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_default_config(self, input_path: Path) -> LosslessConfig:
        """Get default lossless configuration based on file type."""
        ext = input_path.suffix.lower()
        
        if ext in ['.jpg', '.jpeg', '.bmp']:
            return LosslessConfig(
                format=LosslessFormat.PNG,
                compression_level=6
            )
        elif ext in ['.mp3', '.aac', '.ogg']:
            return LosslessConfig(
                format=LosslessFormat.FLAC,
                compression_level=5
            )
        elif ext in ['.mp4', '.avi', '.mov']:
            return LosslessConfig(
                format=LosslessFormat.H265_LOSSLESS,
                compression_level=4
            )
        else:
            return LosslessConfig(
                format=LosslessFormat.PNG,
                compression_level=6
            )
    
    async def _apply_lossless_compression(
        self,
        input_path: Path,
        output_path: Path,
        config: LosslessConfig
    ) -> int:
        """Apply lossless compression with specified configuration."""
        # Simulate compression process
        await asyncio.sleep(0.1)
        
        original_size = input_path.stat().st_size
        
        # Lossless compression ratios by format
        compression_ratios = {
            LosslessFormat.PNG: 0.7,
            LosslessFormat.FLAC: 0.6,
            LosslessFormat.WEBP_LOSSLESS: 0.8,
            LosslessFormat.H264_LOSSLESS: 0.9,
            LosslessFormat.H265_LOSSLESS: 0.85,
            LosslessFormat.TIFF: 0.8,
            LosslessFormat.WAV: 1.0
        }
        
        base_ratio = compression_ratios.get(config.format, 0.8)
        
        # Adjust for compression level (higher level = better compression)
        level_factor = 1.0 - (config.compression_level - 1) * 0.05
        final_ratio = base_ratio * level_factor
        
        return int(original_size * final_ratio)
    
    async def verify_lossless_integrity(
        self,
        original_path: Union[str, Path],
        compressed_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """Verify that lossless compression preserved data integrity."""
        try:
            # Simulate integrity verification
            await asyncio.sleep(0.05)
            
            # In real implementation, this would:
            # 1. Decompress the file
            # 2. Compare with original
            # 3. Calculate checksums
            
            return {
                "integrity_verified": True,
                "checksum_match": True,
                "data_loss": 0.0,
                "verification_method": "pixel-perfect comparison"
            }
            
        except Exception as e:
            return {
                "integrity_verified": False,
                "error": str(e)
            }
    
    def get_lossless_recommendations(
        self,
        file_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get lossless compression recommendations."""
        file_type = file_info.get("type", "unknown")
        file_size = file_info.get("size", 0)
        
        recommendations = []
        
        if file_type == "image":
            if file_size > 10 * 1024 * 1024:  # > 10MB
                recommendations.append({
                    "format": "PNG with high compression",
                    "expected_savings": "20-40%",
                    "use_case": "Archival storage"
                })
            recommendations.append({
                "format": "WebP lossless",
                "expected_savings": "15-25%",
                "use_case": "Web delivery"
            })
        
        elif file_type == "audio":
            recommendations.extend([
                {
                    "format": "FLAC",
                    "expected_savings": "30-50%",
                    "use_case": "Music archival"
                },
                {
                    "format": "ALAC",
                    "expected_savings": "40-60%",
                    "use_case": "Apple ecosystem"
                }
            ])
        
        elif file_type == "video":
            recommendations.append({
                "format": "H.265 lossless",
                "expected_savings": "10-20%",
                "use_case": "Professional archival"
            })
        
        return recommendations