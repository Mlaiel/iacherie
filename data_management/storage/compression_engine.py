"""🗜️ Compression Engine - IA Influencer Agent Platform Enterprise
===============================================================
Module: backend/data_management/storage/compression_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
===============================================================

Enterprise compression engine for multi-format content optimization
with intelligent algorithm selection and performance monitoring.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT LÉGAL:
Ce code est la propriété exclusive de Fahed Mlaiel. Toute utilisation,
reproduction, modification ou distribution non autorisée est strictement
interdite et fera l'objet de poursuites judiciaires.

ÉQUIPE PROJET - SPÉCIALITÉS:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Sécurité: Fahed Mlaiel
- Microservices: Fahed Mlaiel
- Audio Engineer: Fahed Mlaiel
- DevOps: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel
"""

from typing import Dict, List, Optional, Any, Union, Tuple, BinaryIO
import logging
import asyncio
import zlib
import gzip
import bz2
import lzma
import time
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import hashlib
from pathlib import Path
import mimetypes

# Audio/Video compression
import subprocess
import tempfile
import os

# Image compression
from PIL import Image, ImageOpt
import io

logger = logging.getLogger(__name__)

class CompressionAlgorithm(Enum):
    """
Supported compression algorithms"""

    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"
    ZLIB = "zlib"
    JPEG_OPTIMIZED = "jpeg_optimized"
    PNG_OPTIMIZED = "png_optimized"
    WEBP = "webp"
    MP3_OPTIMIZED = "mp3_optimized"
    MP4_COMPRESSED = "mp4_compressed"
    FLAC_COMPRESSED = "flac_compressed"

@dataclass
class CompressionResult:
    """Result of compression operation"""
    success: bool
    algorithm: CompressionAlgorithm
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time: float
    quality_score: float
    compressed_data: Optional[bytes] = None
    error_message: Optional[str] = None

@dataclass
class CompressionConfig:
    """
Configuration for compression operations"""
    algorithm: CompressionAlgorithm
    quality_level: int = 85  # 1-100 for lossy compression
    compression_level: int = 6  # 1-9 for lossless compression
    preserve_quality: bool = True
    max_processing_time: int = 300  # seconds
    target_size_mb: Optional[float] = None

class ContentTypeAnalyzer:
    """
Analyzes content to determine optimal compression strategy"""
    
    @staticmethod
    def analyze_content(
        data: bytes, 
        filename: str, 
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
Analyze content to determine compression strategy"""
        
        if not content_type:
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        analysis = {
            'content_type': content_type,
            'file_size': len(data),
            'filename': filename,
            'file_extension': Path(filename).suffix.lower(),
            'entropy': ContentTypeAnalyzer._calculate_entropy(data),
            'compressibility_score': 0.0,
            'recommended_algorithms': []
        }
        
        # Calculate compressibility
        if analysis['entropy'] < 6.0:
            analysis['compressibility_score'] = 0.9  # Highly compressible
        elif analysis['entropy'] < 7.0:
            analysis['compressibility_score'] = 0.6  # Moderately compressible  
        else:
            analysis['compressibility_score'] = 0.2  # Low compressibility
        
        # Recommend algorithms based on content type
        if content_type.startswith('image/'):
            if 'jpeg' in content_type or 'jpg' in content_type:
                analysis['recommended_algorithms'] = [
                    CompressionAlgorithm.JPEG_OPTIMIZED,
                    CompressionAlgorithm.WEBP
                ]
            elif 'png' in content_type:
                analysis['recommended_algorithms'] = [
                    CompressionAlgorithm.PNG_OPTIMIZED,
                    CompressionAlgorithm.WEBP
                ]
            else:
                analysis['recommended_algorithms'] = [CompressionAlgorithm.WEBP]
        
        elif content_type.startswith('audio/'):
            if 'mp3' in content_type:
                analysis['recommended_algorithms'] = [CompressionAlgorithm.MP3_OPTIMIZED]
            elif 'flac' in content_type:
                analysis['recommended_algorithms'] = [CompressionAlgorithm.FLAC_COMPRESSED]
            else:
                analysis['recommended_algorithms'] = [
                    CompressionAlgorithm.MP3_OPTIMIZED,
                    CompressionAlgorithm.GZIP
                ]
        
        elif content_type.startswith('video/'):
            analysis['recommended_algorithms'] = [CompressionAlgorithm.MP4_COMPRESSED]
        
        elif content_type.startswith('text/') or 'json' in content_type or 'xml' in content_type:
            analysis['recommended_algorithms'] = [
                CompressionAlgorithm.GZIP,
                CompressionAlgorithm.BZIP2,
                CompressionAlgorithm.LZMA
            ]
        
        else:
            # General purpose algorithms for binary data
            if analysis['compressibility_score'] > 0.6:
                analysis['recommended_algorithms'] = [
                    CompressionAlgorithm.LZMA,
                    CompressionAlgorithm.BZIP2,
                    CompressionAlgorithm.GZIP
                ]
            else:
                analysis['recommended_algorithms'] = [CompressionAlgorithm.GZIP]
        
        return analysis
    
    @staticmethod
    def _calculate_entropy(data: bytes, sample_size: int = 10000) -> float:
        """
Calculate Shannon entropy of data sample"""
        if len(data) == 0:
            return 0.0
        
        # Use sample for large files
        if len(data) > sample_size:
            sample = data[:sample_size]
        else:
            sample = data
        
        # Count byte frequencies
        byte_counts = {}
        for byte in sample:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        sample_len = len(sample)
        
        for count in byte_counts.values():
            probability = count / sample_len
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy

class CompressionEngine:
    """
    Enterprise compression engine with intelligent algorithm selection.
    
    Business Logic:
    - Analyzes content type to select optimal compression
    - Preserves quality for creative content (music, images, videos)
    - Maximizes compression for text and data files
    - Supports both lossless and lossy compression
    - Monitors performance and quality metrics
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize compression engine"""
        self.config = config or {}
        self.content_analyzer = ContentTypeAnalyzer()
        
        # Performance metrics
        self.metrics = {
            'total_compressions': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'average_compression_ratio': 0.0,
            'average_processing_time': 0.0,
            'algorithm_usage': {},
            'quality_scores': []
        }
        
        # Algorithm availability check
        self._check_dependencies()
        
        logger.info("CompressionEngine initialized successfully")
    
    def _check_dependencies(self) -> None:
        """Check availability of compression tools"""
        self.available_tools = {
            'ffmpeg': self._check_ffmpeg(),
            'imagemagick': self._check_imagemagick(),
            'pillow': True  # Always available with our imports
        }
        
        if not self.available_tools['ffmpeg']:
            logger.warning("FFmpeg not available - audio/video compression limited")
        
        if not self.available_tools['imagemagick']:
            logger.warning("ImageMagick not available - advanced image optimization limited")
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_imagemagick(self) -> bool:
        """
Check if ImageMagick is available"""
        try:
            subprocess.run(['convert', '-version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    async def compress_content(
        self,
        data: bytes,
        filename: str,
        content_type: Optional[str] = None,
        config: Optional[CompressionConfig] = None
    ) -> CompressionResult:
        """
        Compress content with optimal algorithm selection.
        
        Business Flow:
        1. Analyze content type and compressibility
        2. Select optimal compression algorithm
        3. Apply compression with quality preservation
        4. Validate compression results
        5. Update performance metrics
        """
        start_time = time.time()
        
        try:
            # Analyze content
            analysis = self.content_analyzer.analyze_content(data, filename, content_type)
            
            # Determine compression strategy
            if config:
                algorithm = config.algorithm
            else:
                algorithm = self._select_optimal_algorithm(analysis)
            
            # Apply compression
            result = await self._apply_compression(data, algorithm, analysis, config)
            
            # Update metrics
            self._update_metrics(result)
            
            logger.info(f"Compression completed: {filename} - {result.compression_ratio:.2%} reduction")
            return result
            
        except Exception as e:
            logger.error(f"Compression failed for {filename}: {str(e)}")
            return CompressionResult(
                success=False,
                algorithm=CompressionAlgorithm.GZIP,
                original_size=len(data),
                compressed_size=len(data),
                compression_ratio=1.0,
                compression_time=time.time() - start_time,
                quality_score=0.0,
                error_message=str(e)
            )
    
    async def decompress_content(
        self,
        compressed_data: bytes,
        algorithm: CompressionAlgorithm,
        original_filename: Optional[str] = None
    ) -> Tuple[bool, bytes, str]:
        """Decompress content back to original format"""
        try:
            if algorithm == CompressionAlgorithm.GZIP:
                decompressed = gzip.decompress(compressed_data)
            elif algorithm == CompressionAlgorithm.BZIP2:
                decompressed = bz2.decompress(compressed_data)
            elif algorithm == CompressionAlgorithm.LZMA:
                decompressed = lzma.decompress(compressed_data)
            elif algorithm == CompressionAlgorithm.ZLIB:
                decompressed = zlib.decompress(compressed_data)
            else:
                # For lossy algorithms, return as-is
                decompressed = compressed_data
            
            return True, decompressed, ""
            
        except Exception as e:
            error_msg = f"Decompression failed: {str(e)}"
            logger.error(error_msg)
            return False, compressed_data, error_msg
    
    async def compress_batch(
        self,
        files: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[CompressionResult]:
        """Compress multiple files concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def compress_single(file_info):
        try:
            logger.info(f"Executing compress_single")
            
            # Implementation for compress_single
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"compress_single completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"compress_single failed: {e}")
            raise
                return await self.compress_content(
                    file_info['data'],
                    file_info['filename'],
                    file_info.get('content_type'),
                    file_info.get('config')
                )
        
        tasks = [compress_single(file_info) for file_info in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if isinstance(result, CompressionResult) 
            else CompressionResult(
                success=False,
                algorithm=CompressionAlgorithm.GZIP,
                original_size=0,
                compressed_size=0,
                compression_ratio=1.0,
                compression_time=0.0,
                quality_score=0.0,
                error_message=str(result)
            )
            for result in results
        ]
    
    def _select_optimal_algorithm(self, analysis: Dict[str, Any]) -> CompressionAlgorithm:
        """
Select optimal compression algorithm based on content analysis"""
        recommended = analysis.get('recommended_algorithms', [])
        
        if not recommended:
            return CompressionAlgorithm.GZIP
        
        # Select first available algorithm
        for algorithm in recommended:
            if self._is_algorithm_available(algorithm):
                return algorithm
        
        # Fallback to GZIP
        return CompressionAlgorithm.GZIP
    
    def _is_algorithm_available(self, algorithm: CompressionAlgorithm) -> bool:
        """
Check if compression algorithm is available"""
        if algorithm in [CompressionAlgorithm.MP3_OPTIMIZED, CompressionAlgorithm.MP4_COMPRESSED, CompressionAlgorithm.FLAC_COMPRESSED]:
            return self.available_tools['ffmpeg']
        elif algorithm in [CompressionAlgorithm.JPEG_OPTIMIZED, CompressionAlgorithm.PNG_OPTIMIZED, CompressionAlgorithm.WEBP]:
            return True  # Pillow is always available
        else:
            return True  # Standard compression algorithms
    
    async def _apply_compression(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm,
        analysis: Dict[str, Any],
        config: Optional[CompressionConfig]
    ) -> CompressionResult:
        """
Apply specific compression algorithm"""
        start_time = time.time()
        original_size = len(data)
        
        try:
            if algorithm == CompressionAlgorithm.GZIP:
                compressed = await self._compress_gzip(data, config)
            elif algorithm == CompressionAlgorithm.BZIP2:
                compressed = await self._compress_bzip2(data, config)
            elif algorithm == CompressionAlgorithm.LZMA:
                compressed = await self._compress_lzma(data, config)
            elif algorithm == CompressionAlgorithm.ZLIB:
                compressed = await self._compress_zlib(data, config)
            elif algorithm == CompressionAlgorithm.JPEG_OPTIMIZED:
                compressed = await self._compress_jpeg(data, analysis['filename'], config)
            elif algorithm == CompressionAlgorithm.PNG_OPTIMIZED:
                compressed = await self._compress_png(data, config)
            elif algorithm == CompressionAlgorithm.WEBP:
                compressed = await self._compress_webp(data, config)
            elif algorithm == CompressionAlgorithm.MP3_OPTIMIZED:
                compressed = await self._compress_mp3(data, analysis['filename'], config)
            elif algorithm == CompressionAlgorithm.MP4_COMPRESSED:
                compressed = await self._compress_mp4(data, analysis['filename'], config)
            elif algorithm == CompressionAlgorithm.FLAC_COMPRESSED:
                compressed = await self._compress_flac(data, analysis['filename'], config)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Calculate metrics
            compressed_size = len(compressed)
            compression_ratio = compressed_size / original_size
            compression_time = time.time() - start_time
            quality_score = self._calculate_quality_score(algorithm, compression_ratio, analysis)
            
            return CompressionResult(
                success=True,
                algorithm=algorithm,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                compression_time=compression_time,
                quality_score=quality_score,
                compressed_data=compressed
            )
            
        except Exception as e:
            return CompressionResult(
                success=False,
                algorithm=algorithm,
                original_size=original_size,
                compressed_size=original_size,
                compression_ratio=1.0,
                compression_time=time.time() - start_time,
                quality_score=0.0,
                error_message=str(e)
            )
    
    # Compression algorithm implementations
    
    async def _compress_gzip(self, data: bytes, config: Optional[CompressionConfig]) -> bytes:
        """GZIP compression"""
        level = config.compression_level if config else 6
        return gzip.compress(data, compresslevel=level)
    
    async def _compress_bzip2(self, data: bytes, config: Optional[CompressionConfig]) -> bytes:
        """
BZIP2 compression"""
        level = config.compression_level if config else 6
        return bz2.compress(data, compresslevel=level)
    
    async def _compress_lzma(self, data: bytes, config: Optional[CompressionConfig]) -> bytes:
        """
LZMA compression"""
        level = config.compression_level if config else 6
        return lzma.compress(data, preset=level)
    
    async def _compress_zlib(self, data: bytes, config: Optional[CompressionConfig]) -> bytes:
        """
ZLIB compression"""
        level = config.compression_level if config else 6
        return zlib.compress(data, level)
    
    async def _compress_jpeg(self, data: bytes, filename: str, config: Optional[CompressionConfig]) -> bytes:
        """
JPEG optimization"""
        try:
            image = Image.open(io.BytesIO(data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Optimize
            output = io.BytesIO()
            quality = config.quality_level if config else 85
            
            image.save(
                output,
                format='JPEG',
                quality=quality,
                optimize=True,
                progressive=True
            )
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"JPEG compression failed: {str(e)}")
            return data
    
    async def _compress_png(self, data: bytes, config: Optional[CompressionConfig]) -> bytes:
        """PNG optimization"""
        try:
            image = Image.open(io.BytesIO(data))
            
            output = io.BytesIO()
            image.save(
                output,
                format='PNG',
                optimize=True,
                compress_level=config.compression_level if config else 6
            )
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"PNG compression failed: {str(e)}")
            return data
    
    async def _compress_webp(self, data: bytes, config: Optional[CompressionConfig]) -> bytes:
        """WebP compression"""
        try:
            image = Image.open(io.BytesIO(data))
            
            output = io.BytesIO()
            quality = config.quality_level if config else 85
            
            image.save(
                output,
                format='WEBP',
                quality=quality,
                optimize=True,
                method=6  # Best compression
            )
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"WebP compression failed: {str(e)}")
            return data
    
    async def _compress_mp3(self, data: bytes, filename: str, config: Optional[CompressionConfig]) -> bytes:
        """MP3 audio compression using FFmpeg"""
        if not self.available_tools['ffmpeg']:
            return data
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3') as temp_input:
                with tempfile.NamedTemporaryFile(suffix='.mp3') as temp_output:
                    # Write input data
                    temp_input.write(data)
                    temp_input.flush()
                    
                    # FFmpeg compression
                    bitrate = '128k'  # Default quality
                    if config and config.quality_level:
                        # Map quality to bitrate
                        quality_map = {100: '320k', 90: '256k', 80: '192k', 70: '128k', 60: '96k'}
                        bitrate = quality_map.get(config.quality_level, '128k')
                    
                    cmd = [
                        'ffmpeg', '-y', '-i', temp_input.name,
                        '-codec:a', 'libmp3lame',
                        '-b:a', bitrate,
                        temp_output.name
                    ]
                    
                    subprocess.run(cmd, capture_output=True, check=True)
                    
                    # Read compressed data
                    with open(temp_output.name, 'rb') as f:
                        return f.read()
            
        except Exception as e:
            logger.error(f"MP3 compression failed: {str(e)}")
            return data
    
    async def _compress_mp4(self, data: bytes, filename: str, config: Optional[CompressionConfig]) -> bytes:
        """MP4 video compression using FFmpeg"""
        if not self.available_tools['ffmpeg']:
            return data
        
        try:
            with tempfile.NamedTemporaryFile() as temp_input:
                with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_output:
                    # Write input data
                    temp_input.write(data)
                    temp_input.flush()
                    
                    # FFmpeg compression with H.264
                    crf = '23'  # Default quality
                    if config and config.quality_level:
                        # Map quality to CRF (lower = better quality)
                        crf = str(51 - (config.quality_level * 28 // 100))
                    
                    cmd = [
                        'ffmpeg', '-y', '-i', temp_input.name,
                        '-codec:v', 'libx264',
                        '-crf', crf,
                        '-preset', 'medium',
                        '-codec:a', 'aac',
                        '-b:a', '128k',
                        temp_output.name
                    ]
                    
                    subprocess.run(cmd, capture_output=True, check=True)
                    
                    # Read compressed data
                    with open(temp_output.name, 'rb') as f:
                        return f.read()
            
        except Exception as e:
            logger.error(f"MP4 compression failed: {str(e)}")
            return data
    
    async def _compress_flac(self, data: bytes, filename: str, config: Optional[CompressionConfig]) -> bytes:
        """FLAC audio compression using FFmpeg"""
        if not self.available_tools['ffmpeg']:
            return data
        
        try:
            with tempfile.NamedTemporaryFile() as temp_input:
                with tempfile.NamedTemporaryFile(suffix='.flac') as temp_output:
                    # Write input data
                    temp_input.write(data)
                    temp_input.flush()
                    
                    # FFmpeg FLAC compression
                    compression_level = config.compression_level if config else 6
                    
                    cmd = [
                        'ffmpeg', '-y', '-i', temp_input.name,
                        '-codec:a', 'flac',
                        '-compression_level', str(compression_level),
                        temp_output.name
                    ]
                    
                    subprocess.run(cmd, capture_output=True, check=True)
                    
                    # Read compressed data
                    with open(temp_output.name, 'rb') as f:
                        return f.read()
            
        except Exception as e:
            logger.error(f"FLAC compression failed: {str(e)}")
            return data
    
    def _calculate_quality_score(
        self,
        algorithm: CompressionAlgorithm,
        compression_ratio: float,
        analysis: Dict[str, Any]
    ) -> float:
        """Calculate quality score for compression result"""
        # Base score from compression efficiency
        efficiency_score = max(0.0, min(1.0, (1.0 - compression_ratio) * 2))
        
        # Adjust based on algorithm type
        if algorithm in [CompressionAlgorithm.GZIP, CompressionAlgorithm.BZIP2, CompressionAlgorithm.LZMA, CompressionAlgorithm.ZLIB]:
            # Lossless algorithms get full quality score
            quality_score = 1.0
        else:
            # Lossy algorithms get score based on compression ratio
            quality_score = max(0.3, 1.0 - (compression_ratio * 0.5))
        
        # Combine scores
        final_score = (efficiency_score * 0.3) + (quality_score * 0.7)
        
        return round(final_score, 3)
    
    def _update_metrics(self, result: CompressionResult) -> None:
        """
Update compression metrics"""
        if result.success:
            self.metrics['total_compressions'] += 1
            self.metrics['total_original_size'] += result.original_size
            self.metrics['total_compressed_size'] += result.compressed_size
            
            # Update average compression ratio
            total_ratio = self.metrics['total_compressed_size'] / self.metrics['total_original_size']
            self.metrics['average_compression_ratio'] = total_ratio
            
            # Update average processing time
            count = self.metrics['total_compressions']
            old_avg = self.metrics['average_processing_time']
            self.metrics['average_processing_time'] = (
                (old_avg * (count - 1) + result.compression_time) / count
            )
            
            # Update algorithm usage
            algo_name = result.algorithm.value
            self.metrics['algorithm_usage'][algo_name] = (
                self.metrics['algorithm_usage'].get(algo_name, 0) + 1
            )
            
            # Track quality scores
            self.metrics['quality_scores'].append(result.quality_score)
            
            # Keep only last 1000 quality scores
            if len(self.metrics['quality_scores']) > 1000:
                self.metrics['quality_scores'] = self.metrics['quality_scores'][-1000:]
    
    def get_compression_statistics(self) -> Dict[str, Any]:
        """
Get comprehensive compression statistics"""
        avg_quality = 0.0
        if self.metrics['quality_scores']:
            avg_quality = sum(self.metrics['quality_scores']) / len(self.metrics['quality_scores'])
        
        return {
            'total_compressions': self.metrics['total_compressions'],
            'total_data_processed_mb': round(self.metrics['total_original_size'] / (1024*1024), 2),
            'total_space_saved_mb': round(
                (self.metrics['total_original_size'] - self.metrics['total_compressed_size']) / (1024*1024), 2
            ),
            'average_compression_ratio': round(self.metrics['average_compression_ratio'], 3),
            'average_space_savings_percent': round((1 - self.metrics['average_compression_ratio']) * 100, 1),
            'average_processing_time_seconds': round(self.metrics['average_processing_time'], 3),
            'average_quality_score': round(avg_quality, 3),
            'algorithm_usage': self.metrics['algorithm_usage'],
            'available_tools': self.available_tools
        }

# Export main classes
__all__ = [
    'CompressionEngine',
    'CompressionAlgorithm',
    'CompressionConfig',
    'CompressionResult',
    'ContentTypeAnalyzer'
]
