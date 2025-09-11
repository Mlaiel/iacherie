"""
🔄 FORMAT CONVERSION MATRIX - ENTERPRISE ARCHITECTURE
====================================================

Intelligent format conversion matrix and optimization engine for Ainflue Platform
AI-powered conversion path finding with quality and performance optimization

**Expert Implementation:**
- ML Engineer: AI conversion optimization and quality preservation
- Backend Senior: High-performance conversion pipelines
- Audio Engineer: Professional audio conversion standards
- Performance Engineer: Conversion speed and resource optimization

**Features:** Optimal path finding, Quality preservation, Performance optimization
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Tuple, Any, Set
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import time
import heapq
from collections import defaultdict

# ML and optimization libraries
try:
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import dijkstra
    import networkx as nx
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError as e:
    logging.warning(f"Conversion optimization dependencies not available: {e}")

from .audio_formats import AudioFormat, AudioFormatProcessor
from .video_formats import VideoFormat, VideoFormatProcessor
from .image_formats import ImageFormat, ImageFormatProcessor

logger = logging.getLogger(__name__)

class ConversionQuality(Enum):
    """Conversion quality levels"""
    FAST = "fast"           # Fastest conversion, lower quality
    BALANCED = "balanced"   # Balanced speed and quality
    HIGH = "high"          # High quality, slower conversion
    LOSSLESS = "lossless"  # Lossless conversion when possible
    CUSTOM = "custom"      # Custom parameters

class ConversionPriority(Enum):
    """Conversion optimization priority"""
    SPEED = "speed"         # Optimize for conversion speed
    QUALITY = "quality"     # Optimize for output quality
    SIZE = "size"          # Optimize for file size
    COMPATIBILITY = "compatibility"  # Optimize for compatibility

@dataclass
class ConversionPath:
    """Represents a conversion path between formats"""
    source_format: str
    target_format: str
    intermediate_steps: List[str]
    estimated_time: float
    quality_loss: float
    file_size_ratio: float
    complexity_score: float
    converter_class: str
    conversion_params: Dict[str, Any]

@dataclass
class ConversionMetrics:
    """Conversion performance metrics"""
    conversion_time: float
    quality_score: float
    compression_ratio: float
    success_rate: float
    average_processing_speed: float  # MB/s
    resource_usage: Dict[str, float]

class OptimalPathFinder:
    """AI-powered optimal conversion path finder"""
    
    def __init__(self):
        # Conversion capabilities matrix
        self.conversion_matrix = self._build_conversion_matrix()
        
        # Performance metrics for different conversion paths
        self.performance_metrics = self._load_performance_metrics()
        
        # Quality preservation scores for conversions
        self.quality_matrix = self._build_quality_matrix()
        
        # Conversion complexity scores
        self.complexity_matrix = self._build_complexity_matrix()
    
    def _build_conversion_matrix(self) -> Dict[str, Dict[str, float]]:
        """Build the base conversion capability matrix"""
        # This matrix represents direct conversion capabilities
        # 1.0 = direct conversion possible, 0.0 = not possible, 0.5 = possible but suboptimal
        
        matrix = defaultdict(lambda: defaultdict(float))
        
        # Audio conversions
        audio_formats = ['mp3', 'flac', 'wav', 'aac', 'ogg', 'opus', 'm4a', 'wma']
        for src in audio_formats:
            for dst in audio_formats:
                if src == dst:
                    matrix[src][dst] = 1.0  # Identity
                elif src in ['flac', 'wav'] and dst in ['mp3', 'aac', 'ogg']:
                    matrix[src][dst] = 0.9  # Lossless to lossy
                elif src in ['mp3', 'aac', 'ogg'] and dst in ['flac', 'wav']:
                    matrix[src][dst] = 0.6  # Lossy to lossless (not ideal)
                else:
                    matrix[src][dst] = 0.8  # General audio conversion
        
        # Video conversions
        video_formats = ['mp4', 'webm', 'mov', 'avi', 'mkv', 'flv', 'wmv']
        for src in video_formats:
            for dst in video_formats:
                if src == dst:
                    matrix[src][dst] = 1.0
                elif src == 'mp4' or dst == 'mp4':
                    matrix[src][dst] = 0.9  # MP4 is widely supported
                elif src in ['mov', 'avi'] and dst in ['webm', 'mkv']:
                    matrix[src][dst] = 0.8  # Good compatibility
                else:
                    matrix[src][dst] = 0.7  # General video conversion
        
        # Image conversions
        image_formats = ['jpeg', 'png', 'webp', 'avif', 'heif', 'gif', 'bmp', 'tiff']
        for src in image_formats:
            for dst in image_formats:
                if src == dst:
                    matrix[src][dst] = 1.0
                elif src in ['png', 'bmp', 'tiff'] and dst in ['jpeg', 'webp', 'avif']:
                    matrix[src][dst] = 0.9  # Lossless to lossy
                elif src in ['jpeg', 'webp'] and dst in ['png', 'tiff']:
                    matrix[src][dst] = 0.7  # Lossy to lossless
                else:
                    matrix[src][dst] = 0.8  # General image conversion
        
        return matrix
    
    def _load_performance_metrics(self) -> Dict[str, ConversionMetrics]:
        """Load historical performance metrics for conversions"""
        # In production, this would load from a database of actual conversion metrics
        # For now, we'll use estimated values based on format complexity
        
        metrics = {}
        
        # Audio conversion metrics (estimated)
        audio_conversions = [
            ('flac', 'mp3', ConversionMetrics(2.5, 0.85, 0.15, 0.98, 50.0, {'cpu': 0.6, 'memory': 0.3})),
            ('wav', 'mp3', ConversionMetrics(2.0, 0.88, 0.12, 0.99, 60.0, {'cpu': 0.5, 'memory': 0.3})),
            ('mp3', 'aac', ConversionMetrics(3.0, 0.82, 0.95, 0.96, 40.0, {'cpu': 0.7, 'memory': 0.4})),
            ('flac', 'opus', ConversionMetrics(3.5, 0.90, 0.20, 0.97, 45.0, {'cpu': 0.8, 'memory': 0.4})),
        ]
        
        # Video conversion metrics (estimated)
        video_conversions = [
            ('mov', 'mp4', ConversionMetrics(15.0, 0.92, 0.80, 0.95, 20.0, {'cpu': 0.9, 'memory': 0.7})),
            ('avi', 'webm', ConversionMetrics(20.0, 0.88, 0.70, 0.93, 15.0, {'cpu': 0.95, 'memory': 0.8})),
            ('mp4', 'webm', ConversionMetrics(18.0, 0.90, 0.75, 0.94, 18.0, {'cpu': 0.9, 'memory': 0.75})),
        ]
        
        # Image conversion metrics (estimated)
        image_conversions = [
            ('png', 'jpeg', ConversionMetrics(0.5, 0.85, 0.30, 0.99, 200.0, {'cpu': 0.3, 'memory': 0.2})),
            ('jpeg', 'webp', ConversionMetrics(0.8, 0.90, 0.75, 0.98, 150.0, {'cpu': 0.4, 'memory': 0.3})),
            ('png', 'avif', ConversionMetrics(2.0, 0.95, 0.50, 0.96, 100.0, {'cpu': 0.7, 'memory': 0.5})),
            ('tiff', 'png', ConversionMetrics(1.2, 0.98, 0.60, 0.99, 120.0, {'cpu': 0.5, 'memory': 0.4})),
        ]
        
        # Populate metrics dictionary
        for src, dst, metric in audio_conversions + video_conversions + image_conversions:
            metrics[f"{src}_to_{dst}"] = metric
        
        return metrics
    
    def _build_quality_matrix(self) -> Dict[str, Dict[str, float]]:
        """Build quality preservation matrix for conversions"""
        quality_matrix = defaultdict(lambda: defaultdict(lambda: 0.5))
        
        # Audio quality preservation
        audio_quality = {
            ('flac', 'wav'): 1.0,    # Lossless to lossless
            ('wav', 'flac'): 1.0,   # Lossless to lossless
            ('flac', 'mp3'): 0.85,  # Lossless to lossy
            ('wav', 'mp3'): 0.88,   # Lossless to lossy
            ('mp3', 'aac'): 0.80,   # Lossy to lossy
            ('mp3', 'flac'): 0.60,  # Lossy to lossless (can't recover quality)
        }
        
        # Video quality preservation
        video_quality = {
            ('mov', 'mp4'): 0.95,   # Similar containers
            ('avi', 'mp4'): 0.90,   # Good conversion
            ('mp4', 'webm'): 0.88,  # Different codecs
            ('flv', 'mp4'): 0.85,   # Older to modern format
        }
        
        # Image quality preservation
        image_quality = {
            ('png', 'tiff'): 1.0,   # Lossless to lossless
            ('bmp', 'png'): 1.0,    # Lossless to lossless
            ('png', 'jpeg'): 0.85,  # Lossless to lossy
            ('jpeg', 'webp'): 0.90, # Lossy to modern lossy
            ('png', 'webp'): 0.95,  # Lossless to modern
            ('tiff', 'jpeg'): 0.82, # Lossless to lossy
        }
        
        # Populate quality matrix
        for (src, dst), quality in {**audio_quality, **video_quality, **image_quality}.items():
            quality_matrix[src][dst] = quality
        
        return quality_matrix
    
    def _build_complexity_matrix(self) -> Dict[str, Dict[str, float]]:
        """Build conversion complexity matrix"""
        complexity_matrix = defaultdict(lambda: defaultdict(lambda: 0.5))
        
        # Complexity scores (0.0 = simple, 1.0 = very complex)
        complexity_scores = {
            # Audio complexity
            ('mp3', 'mp3'): 0.0,    # No conversion
            ('wav', 'mp3'): 0.2,    # Simple lossy encoding
            ('flac', 'mp3'): 0.3,   # Lossless to lossy
            ('mp3', 'flac'): 0.7,   # Lossy to lossless (complex)
            ('aac', 'opus'): 0.6,   # Lossy to lossy (different algorithms)
            
            # Video complexity
            ('mp4', 'mp4'): 0.0,    # No conversion
            ('mov', 'mp4'): 0.3,    # Container change
            ('avi', 'webm'): 0.8,   # Format and codec change
            ('flv', 'mp4'): 0.7,    # Legacy to modern
            ('mkv', 'mov'): 0.6,    # Container conversion
            
            # Image complexity
            ('png', 'png'): 0.0,    # No conversion
            ('jpeg', 'png'): 0.2,   # Simple format change
            ('png', 'webp'): 0.4,   # Modern format conversion
            ('tiff', 'avif'): 0.8,  # Complex modern conversion
            ('gif', 'mp4'): 0.9,    # Animation to video (very complex)
        }
        
        for (src, dst), complexity in complexity_scores.items():
            complexity_matrix[src][dst] = complexity
        
        return complexity_matrix
    
    def find_optimal_path(self, source_format: str, target_format: str,
                         priority: ConversionPriority = ConversionPriority.BALANCED,
                         quality_threshold: float = 0.8) -> ConversionPath:
        """Find optimal conversion path using AI optimization"""
        
        # Handle direct conversion
        if source_format == target_format:
            return ConversionPath(
                source_format=source_format,
                target_format=target_format,
                intermediate_steps=[],
                estimated_time=0.0,
                quality_loss=0.0,
                file_size_ratio=1.0,
                complexity_score=0.0,
                converter_class=self._get_converter_class(source_format),
                conversion_params={}
            )
        
        # Check for direct conversion capability
        direct_capability = self.conversion_matrix[source_format][target_format]
        if direct_capability > 0.7:  # Good direct conversion available
            return self._create_direct_conversion_path(source_format, target_format, priority)
        
        # Find multi-step conversion path
        return self._find_multi_step_path(source_format, target_format, priority, quality_threshold)
    
    def _create_direct_conversion_path(self, source_format: str, target_format: str,
                                     priority: ConversionPriority) -> ConversionPath:
        """Create direct conversion path"""
        
        # Get metrics
        metric_key = f"{source_format}_to_{target_format}"
        metrics = self.performance_metrics.get(metric_key)
        
        if metrics:
            estimated_time = metrics.conversion_time
            quality_loss = 1.0 - metrics.quality_score
            file_size_ratio = metrics.compression_ratio
        else:
            # Estimate metrics
            estimated_time = self._estimate_conversion_time(source_format, target_format)
            quality_loss = 1.0 - self.quality_matrix[source_format][target_format]
            file_size_ratio = self._estimate_file_size_ratio(source_format, target_format)
        
        complexity_score = self.complexity_matrix[source_format][target_format]
        converter_class = self._get_converter_class(source_format)
        conversion_params = self._get_optimal_params(source_format, target_format, priority)
        
        return ConversionPath(
            source_format=source_format,
            target_format=target_format,
            intermediate_steps=[],
            estimated_time=estimated_time,
            quality_loss=quality_loss,
            file_size_ratio=file_size_ratio,
            complexity_score=complexity_score,
            converter_class=converter_class,
            conversion_params=conversion_params
        )
    
    def _find_multi_step_path(self, source_format: str, target_format: str,
                            priority: ConversionPriority, quality_threshold: float) -> ConversionPath:
        """Find optimal multi-step conversion path using graph algorithms"""
        
        # Build conversion graph
        graph = self._build_conversion_graph()
        
        # Find all possible paths
        possible_paths = self._find_all_paths(graph, source_format, target_format, max_depth=3)
        
        # Score and rank paths
        scored_paths = []
        for path in possible_paths:
            score = self._score_conversion_path(path, priority, quality_threshold)
            if score > 0:  # Valid path
                scored_paths.append((score, path))
        
        if not scored_paths:
            # Fallback to direct conversion even if suboptimal
            return self._create_direct_conversion_path(source_format, target_format, priority)
        
        # Select best path
        best_score, best_path = max(scored_paths, key=lambda x: x[0])
        
        return self._create_multi_step_conversion_path(best_path, priority)
    
    def _build_conversion_graph(self) -> nx.DiGraph:
        """Build directed graph of conversion capabilities"""
        graph = nx.DiGraph()
        
        for src_format, dst_formats in self.conversion_matrix.items():
            for dst_format, capability in dst_formats.items():
                if capability > 0.1:  # Only include viable conversions
                    weight = 1.0 / capability  # Lower weight = better conversion
                    graph.add_edge(src_format, dst_format, weight=weight, capability=capability)
        
        return graph
    
    def _find_all_paths(self, graph: nx.DiGraph, source: str, target: str, max_depth: int) -> List[List[str]]:
        """Find all possible conversion paths with depth limit"""
        try:
            # Use NetworkX to find all simple paths
            all_paths = list(nx.all_simple_paths(graph, source, target, cutoff=max_depth))
            return all_paths
        except nx.NetworkXNoPath:
            return []
    
    def _score_conversion_path(self, path: List[str], priority: ConversionPriority, 
                             quality_threshold: float) -> float:
        """Score a conversion path based on priority and constraints"""
        
        if len(path) < 2:
            return 0.0
        
        # Calculate path metrics
        total_time = 0.0
        total_quality_loss = 0.0
        total_complexity = 0.0
        current_quality = 1.0
        
        for i in range(len(path) - 1):
            src, dst = path[i], path[i + 1]
            
            # Time estimation
            step_time = self._estimate_conversion_time(src, dst)
            total_time += step_time
            
            # Quality degradation (multiplicative)
            step_quality = self.quality_matrix[src][dst]
            current_quality *= step_quality
            
            # Complexity accumulation
            step_complexity = self.complexity_matrix[src][dst]
            total_complexity += step_complexity
        
        total_quality_loss = 1.0 - current_quality
        
        # Check quality threshold
        if current_quality < quality_threshold:
            return 0.0  # Path doesn't meet quality requirements
        
        # Score based on priority
        if priority == ConversionPriority.SPEED:
            score = 1.0 / (1.0 + total_time)  # Prefer faster conversions
        elif priority == ConversionPriority.QUALITY:
            score = current_quality  # Prefer higher quality
        elif priority == ConversionPriority.SIZE:
            # Estimate based on format characteristics
            size_score = self._estimate_size_optimization(path)
            score = size_score
        else:  # BALANCED
            # Weighted combination
            time_score = 1.0 / (1.0 + total_time * 0.1)
            quality_score = current_quality
            complexity_score = 1.0 / (1.0 + total_complexity)
            
            score = 0.4 * quality_score + 0.3 * time_score + 0.3 * complexity_score
        
        return score
    
    def _create_multi_step_conversion_path(self, path: List[str], 
                                         priority: ConversionPriority) -> ConversionPath:
        """Create ConversionPath object for multi-step conversion"""
        
        source_format = path[0]
        target_format = path[-1]
        intermediate_steps = path[1:-1]
        
        # Calculate total metrics
        total_time = 0.0
        total_quality_loss = 0.0
        total_complexity = 0.0
        current_quality = 1.0
        total_size_ratio = 1.0
        
        for i in range(len(path) - 1):
            src, dst = path[i], path[i + 1]
            
            step_time = self._estimate_conversion_time(src, dst)
            total_time += step_time
            
            step_quality = self.quality_matrix[src][dst]
            current_quality *= step_quality
            
            step_complexity = self.complexity_matrix[src][dst]
            total_complexity += step_complexity
            
            step_size_ratio = self._estimate_file_size_ratio(src, dst)
            total_size_ratio *= step_size_ratio
        
        total_quality_loss = 1.0 - current_quality
        
        converter_class = self._get_converter_class(source_format)
        conversion_params = self._get_optimal_params(source_format, target_format, priority)
        
        return ConversionPath(
            source_format=source_format,
            target_format=target_format,
            intermediate_steps=intermediate_steps,
            estimated_time=total_time,
            quality_loss=total_quality_loss,
            file_size_ratio=total_size_ratio,
            complexity_score=total_complexity,
            converter_class=converter_class,
            conversion_params=conversion_params
        )
    
    def _estimate_conversion_time(self, source_format: str, target_format: str) -> float:
        """Estimate conversion time based on format complexity"""
        
        # Base times by media type (seconds per MB)
        base_times = {
            ('audio', 'audio'): 0.1,
            ('video', 'video'): 1.0,
            ('image', 'image'): 0.05,
        }
        
        src_type = self._get_media_type(source_format)
        dst_type = self._get_media_type(target_format)
        
        base_time = base_times.get((src_type, dst_type), 0.5)
        
        # Complexity multiplier
        complexity = self.complexity_matrix[source_format][target_format]
        multiplier = 1.0 + complexity * 2.0
        
        return base_time * multiplier
    
    def _estimate_file_size_ratio(self, source_format: str, target_format: str) -> float:
        """Estimate file size change ratio"""
        
        # Compression efficiency by format
        compression_efficiency = {
            # Audio formats (relative to WAV)
            'wav': 1.0,
            'flac': 0.6,
            'mp3': 0.1,
            'aac': 0.12,
            'ogg': 0.15,
            'opus': 0.08,
            'm4a': 0.12,
            
            # Video formats (relative to uncompressed)
            'avi': 0.8,
            'mov': 0.7,
            'mp4': 0.6,
            'webm': 0.5,
            'mkv': 0.65,
            'flv': 0.4,
            
            # Image formats (relative to BMP)
            'bmp': 1.0,
            'tiff': 0.8,
            'png': 0.3,
            'jpeg': 0.1,
            'webp': 0.08,
            'avif': 0.05,
            'heif': 0.06,
            'gif': 0.2,
        }
        
        src_efficiency = compression_efficiency.get(source_format, 0.5)
        dst_efficiency = compression_efficiency.get(target_format, 0.5)
        
        return dst_efficiency / src_efficiency if src_efficiency > 0 else 1.0
    
    def _estimate_size_optimization(self, path: List[str]) -> float:
        """Estimate size optimization score for a conversion path"""
        if len(path) < 2:
            return 1.0
        
        source_format = path[0]
        target_format = path[-1]
        
        size_ratio = self._estimate_file_size_ratio(source_format, target_format)
        
        # Score based on size reduction (lower ratio = better score)
        if size_ratio < 1.0:
            score = 1.0 / size_ratio  # Reward size reduction
        else:
            score = 1.0 / (1.0 + size_ratio - 1.0)  # Penalize size increase
        
        return min(score, 2.0)  # Cap the score
    
    def _get_media_type(self, format_name: str) -> str:
        """Get media type for format"""
        audio_formats = {'mp3', 'flac', 'wav', 'aac', 'ogg', 'opus', 'm4a', 'wma'}
        video_formats = {'mp4', 'webm', 'mov', 'avi', 'mkv', 'flv', 'wmv'}
        image_formats = {'jpeg', 'png', 'webp', 'avif', 'heif', 'gif', 'bmp', 'tiff'}
        
        if format_name in audio_formats:
            return 'audio'
        elif format_name in video_formats:
            return 'video'
        elif format_name in image_formats:
            return 'image'
        else:
            return 'unknown'
    
    def _get_converter_class(self, format_name: str) -> str:
        """Get appropriate converter class for format"""
        media_type = self._get_media_type(format_name)
        
        converter_map = {
            'audio': 'AudioFormatProcessor',
            'video': 'VideoFormatProcessor',
            'image': 'ImageFormatProcessor',
            'unknown': 'UniversalConverter'
        }
        
        return converter_map.get(media_type, 'UniversalConverter')
    
    def _get_optimal_params(self, source_format: str, target_format: str,
                          priority: ConversionPriority) -> Dict[str, Any]:
        """Get optimal conversion parameters based on priority"""
        
        media_type = self._get_media_type(source_format)
        params = {}
        
        if media_type == 'audio':
            if priority == ConversionPriority.SPEED:
                params = {'quality': 'medium', 'threads': 'auto', 'preset': 'fast'}
            elif priority == ConversionPriority.QUALITY:
                params = {'quality': 'high', 'bitrate': 'vbr', 'preset': 'slow'}
            elif priority == ConversionPriority.SIZE:
                params = {'quality': 'low', 'bitrate': 'cbr_low', 'optimize': True}
            else:  # BALANCED
                params = {'quality': 'medium', 'bitrate': 'vbr', 'preset': 'medium'}
        
        elif media_type == 'video':
            if priority == ConversionPriority.SPEED:
                params = {'preset': 'ultrafast', 'crf': 28, 'threads': 'auto'}
            elif priority == ConversionPriority.QUALITY:
                params = {'preset': 'slow', 'crf': 18, 'profile': 'high'}
            elif priority == ConversionPriority.SIZE:
                params = {'preset': 'medium', 'crf': 32, 'optimize_size': True}
            else:  # BALANCED
                params = {'preset': 'medium', 'crf': 23, 'profile': 'main'}
        
        elif media_type == 'image':
            if priority == ConversionPriority.SPEED:
                params = {'quality': 80, 'optimize': False, 'progressive': False}
            elif priority == ConversionPriority.QUALITY:
                params = {'quality': 95, 'optimize': True, 'progressive': True}
            elif priority == ConversionPriority.SIZE:
                params = {'quality': 60, 'optimize': True, 'strip_metadata': True}
            else:  # BALANCED
                params = {'quality': 85, 'optimize': True, 'progressive': False}
        
        return params

class ConversionMatrix:
    """Main conversion matrix interface"""
    
    def __init__(self):
        self.path_finder = OptimalPathFinder()
        self.audio_processor = AudioFormatProcessor()
        self.video_processor = VideoFormatProcessor()
        self.image_processor = ImageFormatProcessor()
        
        # Conversion cache
        self.path_cache = {}
        self.performance_cache = {}
    
    def find_optimal_path(self, source_format: str, target_format: str,
                         priority: ConversionPriority = ConversionPriority.BALANCED,
                         quality_threshold: float = 0.8) -> ConversionPath:
        """Find optimal conversion path with caching"""
        
        # Check cache
        cache_key = f"{source_format}_{target_format}_{priority.value}_{quality_threshold}"
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]
        
        # Find path
        path = self.path_finder.find_optimal_path(
            source_format, target_format, priority, quality_threshold
        )
        
        # Cache result
        self.path_cache[cache_key] = path
        
        return path
    
    def get_conversion_matrix(self) -> Dict[str, Dict[str, float]]:
        """Get the full conversion capability matrix"""
        return dict(self.path_finder.conversion_matrix)
    
    def get_supported_conversions(self, source_format: str, 
                                min_capability: float = 0.7) -> List[str]:
        """Get list of supported target formats for source format"""
        conversions = self.path_finder.conversion_matrix[source_format]
        return [fmt for fmt, capability in conversions.items() 
                if capability >= min_capability]
    
    def estimate_conversion_time(self, source_format: str, target_format: str,
                               file_size_mb: float = 10.0) -> float:
        """Estimate conversion time for given file size"""
        path = self.find_optimal_path(source_format, target_format)
        base_time = path.estimated_time
        return base_time * file_size_mb
    
    def get_quality_preservation_score(self, source_format: str, 
                                     target_format: str) -> float:
        """Get quality preservation score for conversion"""
        path = self.find_optimal_path(source_format, target_format, 
                                    ConversionPriority.QUALITY)
        return 1.0 - path.quality_loss
    
    def get_recommended_formats_for_use_case(self, use_case: str) -> Dict[str, str]:
        """Get recommended target formats for specific use cases"""
        recommendations = {
            'web_streaming': {
                'audio': 'aac',
                'video': 'mp4',
                'image': 'webp'
            },
            'mobile_app': {
                'audio': 'aac',
                'video': 'mp4',
                'image': 'webp'
            },
            'social_media': {
                'audio': 'mp3',
                'video': 'mp4',
                'image': 'jpeg'
            },
            'archival': {
                'audio': 'flac',
                'video': 'mkv',
                'image': 'tiff'
            },
            'email_attachment': {
                'audio': 'mp3',
                'video': 'mp4',
                'image': 'jpeg'
            },
            'professional_editing': {
                'audio': 'wav',
                'video': 'mov',
                'image': 'tiff'
            }
        }
        
        return recommendations.get(use_case, {
            'audio': 'mp3',
            'video': 'mp4', 
            'image': 'jpeg'
        })
    
    def update_performance_metrics(self, source_format: str, target_format: str,
                                 actual_metrics: ConversionMetrics):
        """Update performance metrics based on actual conversion results"""
        metric_key = f"{source_format}_to_{target_format}"
        self.path_finder.performance_metrics[metric_key] = actual_metrics
        
        # Clear related cache entries
        cache_keys_to_remove = [key for key in self.path_cache.keys() 
                              if key.startswith(f"{source_format}_{target_format}")]
        for key in cache_keys_to_remove:
            del self.path_cache[key]
    
    def get_conversion_statistics(self) -> Dict[str, Any]:
        """Get conversion matrix statistics"""
        matrix = self.path_finder.conversion_matrix
        
        total_conversions = sum(len(dst_formats) for dst_formats in matrix.values())
        direct_conversions = sum(1 for dst_formats in matrix.values() 
                               for capability in dst_formats.values() 
                               if capability > 0.8)
        
        avg_capability = np.mean([capability for dst_formats in matrix.values() 
                                for capability in dst_formats.values() 
                                if capability > 0])
        
        return {
            'total_format_pairs': total_conversions,
            'direct_conversions': direct_conversions,
            'average_capability': avg_capability,
            'cache_size': len(self.path_cache),
            'performance_metrics_count': len(self.path_finder.performance_metrics)
        }

# Module exports for enterprise integration
__all__ = [
    'ConversionMatrix',
    'OptimalPathFinder',
    'ConversionPath',
    'ConversionMetrics',
    'ConversionQuality',
    'ConversionPriority'
]