"""Conversion Analytics Engine
Format conversion tracking and optimization analytics.

This module provides comprehensive analytics for multimedia format conversions,
including conversion performance, quality analysis, and optimization insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

⚠️ COPYRIGHT PROTECTION ⚠️
This code is proprietary and confidential. Unauthorized use is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
from enum import Enum
from pathlib import Path
import hashlib
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class ConversionStatus(Enum):
    """Conversion operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ConversionRecord:
    """Single conversion operation record"""
    conversion_id: str
    source_format: str
    target_format: str
    source_file_path: str
    target_file_path: Optional[str] = None
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    
    # File metrics
    source_size: Optional[int] = None
    target_size: Optional[int] = None
    compression_ratio: Optional[float] = None
    
    # Quality metrics
    source_quality_score: Optional[float] = None
    target_quality_score: Optional[float] = None
    quality_retention: Optional[float] = None
    
    # Processing metrics
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    gpu_usage: Optional[float] = None
    
    # Status and results
    status: ConversionStatus = ConversionStatus.PENDING
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    # Configuration
    conversion_settings: Dict[str, Any] = field(default_factory=dict)
    
    def finalize(self) -> None:
        """Finalize conversion record"""
        if self.end_time and self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
        
        if self.source_size and self.target_size:
            self.compression_ratio = self.target_size / self.source_size
        
        if self.source_quality_score and self.target_quality_score:
            self.quality_retention = self.target_quality_score / self.source_quality_score

@dataclass
class ConversionAnalytics:
    """Conversion analytics summary"""
    analysis_period: Tuple[datetime, datetime]
    format_pair: Optional[Tuple[str, str]] = None
    
    # Volume metrics
    total_conversions: int = 0
    successful_conversions: int = 0
    failed_conversions: int = 0
    success_rate: float = 0.0
    
    # Performance metrics
    average_duration: float = 0.0
    median_duration: float = 0.0
    throughput: float = 0.0  # MB/s
    
    # Quality metrics
    average_quality_retention: float = 0.0
    average_compression_ratio: float = 0.0
    
    # Resource utilization
    average_cpu_usage: float = 0.0
    average_memory_usage: float = 0.0
    average_gpu_usage: float = 0.0
    
    # File size analytics
    average_source_size: float = 0.0
    average_target_size: float = 0.0
    size_reduction_percentage: float = 0.0
    
    # Trend analysis
    conversion_trend: List[Tuple[datetime, int]] = field(default_factory=list)
    performance_trend: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Top conversions
    most_common_conversions: List[Tuple[str, str, int]] = field(default_factory=list)
    problematic_conversions: List[Tuple[str, str, float]] = field(default_factory=list)
    
    # Optimization insights
    optimization_recommendations: List[str] = field(default_factory=list)


class ConversionTracker:
    """Main conversion tracking system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Data storage
        self.conversion_records: Dict[str, ConversionRecord] = {}
        self.completed_conversions: deque = deque(maxlen=self.config.get('max_records', 10000))
        
        # Real-time tracking
        self.active_conversions: Dict[str, ConversionRecord] = {}
        
        # Performance tracking
        self.performance_history: deque = deque(maxlen=1000)
        
    async def start_conversion_tracking(self, source_file: str, target_format: str,
                                      conversion_settings: Optional[Dict[str, Any]] = None) -> str:
        """Start tracking a new conversion operation"""
        try:
            # Generate conversion ID
            conversion_id = self._generate_conversion_id(source_file, target_format)
            
            # Detect source format
            source_format = self._detect_format(source_file)
            
            # Create conversion record
            record = ConversionRecord(
                conversion_id=conversion_id,
                source_format=source_format,
                target_format=target_format,
                source_file_path=source_file,
                conversion_settings=conversion_settings or {}
            )
            
            # Get source file metrics
            await self._analyze_source_file(record)
            
            # Store record
            self.conversion_records[conversion_id] = record
            self.active_conversions[conversion_id] = record
            
            self.logger.info(f"Started tracking conversion {conversion_id}: {source_format} -> {target_format}")
            return conversion_id
            
        except Exception as e:
            self.logger.error(f"Failed to start conversion tracking: {e}")
            raise
    
    async def update_conversion_progress(self, conversion_id -> None: str, 
                                       status -> None: ConversionStatus,
                                       progress_data -> None: Optional[Dict[str, Any]] = None) -> None:
        """Update conversion progress"""
        try:
            if conversion_id not in self.conversion_records:
                self.logger.warning(f"Conversion {conversion_id} not found")
                return
            
            record = self.conversion_records[conversion_id]
            record.status = status
            
            if progress_data:
                # Update resource usage
                if 'cpu_usage' in progress_data:
                    record.cpu_usage = progress_data['cpu_usage']
                if 'memory_usage' in progress_data:
                    record.memory_usage = progress_data['memory_usage']
                if 'gpu_usage' in progress_data:
                    record.gpu_usage = progress_data['gpu_usage']
                
                # Update warnings
                if 'warnings' in progress_data:
                    record.warnings.extend(progress_data['warnings'])
            
            # Handle completion or failure
            if status in [ConversionStatus.COMPLETED, ConversionStatus.FAILED, ConversionStatus.CANCELLED]:
                await self._finalize_conversion(record, status, progress_data)
            
        except Exception as e:
            self.logger.error(f"Failed to update conversion progress: {e}")
    
    async def _finalize_conversion(self, record -> None: ConversionRecord, status -> None: ConversionStatus,
                                 completion_data -> None: Optional[Dict[str, Any]] = None) -> None:
        """Finalize conversion tracking"""
        try:
            record.end_time = datetime.now()
            record.status = status
            
            if completion_data:
                # Update final data
                if 'target_file_path' in completion_data:
                    record.target_file_path = completion_data['target_file_path']
                if 'error_message' in completion_data:
                    record.error_message = completion_data['error_message']
            
            # Analyze target file if successful
            if status == ConversionStatus.COMPLETED and record.target_file_path:
                await self._analyze_target_file(record)
            
            # Finalize calculations
            record.finalize()
            
            # Move to completed conversions
            self.completed_conversions.append(record)
            
            # Remove from active tracking
            if record.conversion_id in self.active_conversions:
                del self.active_conversions[record.conversion_id]
            
            # Update performance history
            await self._update_performance_history(record)
            
            self.logger.info(f"Finalized conversion {record.conversion_id}: {status.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to finalize conversion: {e}")
    
    def _generate_conversion_id(self, source_file: str, target_format: str) -> str:
        """Generate unique conversion ID"""
        content = f"{source_file}_{target_format}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _detect_format(self, file_path: str) -> str:
        """Detect file format from extension"""
        return Path(file_path).suffix.lower().lstrip('.')
    
    async def _analyze_source_file(self, record -> None: ConversionRecord) -> None:
        """Analyze source file properties"""
        try:
            file_path = Path(record.source_file_path)
            
            if file_path.exists():
                record.source_size = file_path.stat().st_size
                
                # TODO: Integrate with quality assessment modules
                # This would use the quality metrics from other analytics modules
                record.source_quality_score = 0.8  # Placeholder
            
        except Exception as e:
            self.logger.error(f"Source file analysis failed: {e}")
    
    async def _analyze_target_file(self, record -> None: ConversionRecord) -> None:
        """Analyze target file properties"""
        try:
            if not record.target_file_path:
                return
            
            file_path = Path(record.target_file_path)
            
            if file_path.exists():
                record.target_size = file_path.stat().st_size
                
                # TODO: Integrate with quality assessment modules
                record.target_quality_score = 0.75  # Placeholder
            
        except Exception as e:
            self.logger.error(f"Target file analysis failed: {e}")
    
    async def _update_performance_history(self, record -> None: ConversionRecord) -> None:
        """Update performance tracking history"""
        try:
            if record.duration and record.source_size:
                throughput = (record.source_size / (1024 * 1024)) / record.duration  # MB/s
                
                self.performance_history.append({
                    'timestamp': record.end_time,
                    'duration': record.duration,
                    'throughput': throughput,
                    'format_pair': (record.source_format, record.target_format),
                    'success': record.status == ConversionStatus.COMPLETED
                })
            
        except Exception as e:
            self.logger.error(f"Performance history update failed: {e}")
    
    async def get_conversion_analytics(self, period_hours: int = 24,
                                     format_pair: Optional[Tuple[str, str]] = None) -> ConversionAnalytics:
        """Get conversion analytics for specified period"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=period_hours)
            
            # Filter conversions
            conversions = [
                conv for conv in self.completed_conversions
                if start_time <= conv.start_time <= end_time
            ]
            
            if format_pair:
                conversions = [
                    conv for conv in conversions
                    if (conv.source_format, conv.target_format) == format_pair
                ]
            
            # Initialize analytics
            analytics = ConversionAnalytics(
                analysis_period=(start_time, end_time),
                format_pair=format_pair
            )
            
            if not conversions:
                return analytics
            
            # Calculate metrics
            await self._calculate_volume_metrics(conversions, analytics)
            await self._calculate_performance_metrics(conversions, analytics)
            await self._calculate_quality_metrics(conversions, analytics)
            await self._calculate_resource_metrics(conversions, analytics)
            await self._calculate_size_metrics(conversions, analytics)
            await self._calculate_trends(conversions, analytics)
            await self._generate_optimization_insights(conversions, analytics)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Conversion analytics calculation failed: {e}")
            return ConversionAnalytics(analysis_period=(start_time, end_time))
    
    async def _calculate_volume_metrics(self, conversions -> None: List[ConversionRecord],
                                      analytics -> None: ConversionAnalytics) -> None:
        """Calculate volume-based metrics"""
        try:
            analytics.total_conversions = len(conversions)
            analytics.successful_conversions = sum(
                1 for conv in conversions if conv.status == ConversionStatus.COMPLETED
            )
            analytics.failed_conversions = analytics.total_conversions - analytics.successful_conversions
            
            if analytics.total_conversions > 0:
                analytics.success_rate = analytics.successful_conversions / analytics.total_conversions
            
        except Exception as e:
            self.logger.error(f"Volume metrics calculation failed: {e}")
    
    async def _calculate_performance_metrics(self, conversions -> None: List[ConversionRecord],
                                           analytics -> None: ConversionAnalytics) -> None:
        """Calculate performance metrics"""
        try:
            successful_conversions = [
                conv for conv in conversions if conv.status == ConversionStatus.COMPLETED
            ]
            
            if not successful_conversions:
                return
            
            # Duration metrics
            durations = [conv.duration for conv in successful_conversions if conv.duration]
            if durations:
                analytics.average_duration = np.mean(durations)
                analytics.median_duration = np.median(durations)
            
            # Throughput calculation
            throughputs = []
            for conv in successful_conversions:
                if conv.duration and conv.source_size:
                    throughput = (conv.source_size / (1024 * 1024)) / conv.duration  # MB/s
                    throughputs.append(throughput)
            
            if throughputs:
                analytics.throughput = np.mean(throughputs)
            
        except Exception as e:
            self.logger.error(f"Performance metrics calculation failed: {e}")
    
    async def _calculate_quality_metrics(self, conversions -> None: List[ConversionRecord],
                                       analytics -> None: ConversionAnalytics) -> None:
        """Calculate quality-related metrics"""
        try:
            successful_conversions = [
                conv for conv in conversions if conv.status == ConversionStatus.COMPLETED
            ]
            
            # Quality retention
            quality_retentions = [
                conv.quality_retention for conv in successful_conversions
                if conv.quality_retention is not None
            ]
            if quality_retentions:
                analytics.average_quality_retention = np.mean(quality_retentions)
            
            # Compression ratio
            compression_ratios = [
                conv.compression_ratio for conv in successful_conversions
                if conv.compression_ratio is not None
            ]
            if compression_ratios:
                analytics.average_compression_ratio = np.mean(compression_ratios)
            
        except Exception as e:
            self.logger.error(f"Quality metrics calculation failed: {e}")
    
    async def _calculate_resource_metrics(self, conversions -> None: List[ConversionRecord],
                                        analytics -> None: ConversionAnalytics) -> None:
        """Calculate resource utilization metrics"""
        try:
            # CPU usage
            cpu_usages = [conv.cpu_usage for conv in conversions if conv.cpu_usage is not None]
            if cpu_usages:
                analytics.average_cpu_usage = np.mean(cpu_usages)
            
            # Memory usage
            memory_usages = [conv.memory_usage for conv in conversions if conv.memory_usage is not None]
            if memory_usages:
                analytics.average_memory_usage = np.mean(memory_usages)
            
            # GPU usage
            gpu_usages = [conv.gpu_usage for conv in conversions if conv.gpu_usage is not None]
            if gpu_usages:
                analytics.average_gpu_usage = np.mean(gpu_usages)
            
        except Exception as e:
            self.logger.error(f"Resource metrics calculation failed: {e}")
    
    async def _calculate_size_metrics(self, conversions -> None: List[ConversionRecord],
                                    analytics -> None: ConversionAnalytics) -> None:
        """Calculate file size metrics"""
        try:
            successful_conversions = [
                conv for conv in conversions if conv.status == ConversionStatus.COMPLETED
            ]
            
            # Source size
            source_sizes = [conv.source_size for conv in successful_conversions if conv.source_size]
            if source_sizes:
                analytics.average_source_size = np.mean(source_sizes) / (1024 * 1024)  # MB
            
            # Target size
            target_sizes = [conv.target_size for conv in successful_conversions if conv.target_size]
            if target_sizes:
                analytics.average_target_size = np.mean(target_sizes) / (1024 * 1024)  # MB
            
            # Size reduction
            if analytics.average_source_size > 0:
                analytics.size_reduction_percentage = (
                    (analytics.average_source_size - analytics.average_target_size) / 
                    analytics.average_source_size * 100
                )
            
        except Exception as e:
            self.logger.error(f"Size metrics calculation failed: {e}")
    
    async def _calculate_trends(self, conversions -> None: List[ConversionRecord],
                              analytics -> None: ConversionAnalytics) -> None:
        """Calculate trend analysis"""
        try:
            # Group conversions by hour
            hourly_counts = defaultdict(int)
            hourly_performance = defaultdict(list)
            
            for conv in conversions:
                hour = conv.start_time.replace(minute=0, second=0, microsecond=0)
                hourly_counts[hour] += 1
                
                if conv.duration and conv.status == ConversionStatus.COMPLETED:
                    hourly_performance[hour].append(conv.duration)
            
            # Conversion trend
            analytics.conversion_trend = sorted(hourly_counts.items())
            
            # Performance trend
            performance_trend = []
            for hour, durations in hourly_performance.items():
                if durations:
                    avg_duration = np.mean(durations)
                    performance_trend.append((hour, avg_duration))
            
            analytics.performance_trend = sorted(performance_trend)
            
        except Exception as e:
            self.logger.error(f"Trend calculation failed: {e}")
    
    async def _generate_optimization_insights(self, conversions -> None: List[ConversionRecord],
                                            analytics -> None: ConversionAnalytics) -> None:
        """Generate optimization recommendations"""
        try:
            recommendations = []
            
            # Analyze conversion patterns
            format_pairs = defaultdict(int)
            format_failures = defaultdict(int)
            
            for conv in conversions:
                pair = (conv.source_format, conv.target_format)
                format_pairs[pair] += 1
                
                if conv.status != ConversionStatus.COMPLETED:
                    format_failures[pair] += 1
            
            # Most common conversions
            analytics.most_common_conversions = [
                (source, target, count) 
                for (source, target), count in sorted(format_pairs.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Problematic conversions
            problematic = []
            for pair, failures in format_failures.items():
                total = format_pairs[pair]
                failure_rate = failures / total if total > 0 else 0
                if failure_rate > 0.1:  # More than 10% failure rate
                    problematic.append((pair[0], pair[1], failure_rate))
            
            analytics.problematic_conversions = sorted(problematic, key=lambda x: x[2], reverse=True)
            
            # Generate recommendations
            if analytics.success_rate < 0.9:
                recommendations.append("Investigate conversion failures - success rate below 90%")
            
            if analytics.average_duration > 300:  # More than 5 minutes
                recommendations.append("Optimize conversion performance - average duration is high")
            
            if analytics.average_cpu_usage > 90:
                recommendations.append("Consider load balancing - high CPU usage detected")
            
            if analytics.average_quality_retention < 0.8:
                recommendations.append("Review quality settings - significant quality loss detected")
            
            if analytics.size_reduction_percentage < 10:
                recommendations.append("Optimize compression settings for better file size reduction")
            
            # Format-specific recommendations
            for source, target, failure_rate in analytics.problematic_conversions:
                recommendations.append(
                    f"Review {source} to {target} conversion - {failure_rate:.1%} failure rate"
                )
            
            analytics.optimization_recommendations = recommendations
            
        except Exception as e:
            self.logger.error(f"Optimization insights generation failed: {e}")


class FormatAnalyzer:
    """Format-specific conversion analysis"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
        
        # Format compatibility matrix
        self.compatibility_matrix = {
            'mp4': ['avi', 'mov', 'mkv', 'webm', 'flv'],
            'mp3': ['wav', 'flac', 'aac', 'ogg'],
            'jpg': ['png', 'webp', 'bmp', 'tiff'],
            'png': ['jpg', 'webp', 'bmp', 'gif'],
            # Add more format mappings
        }
    
    async def analyze_format_performance(self, conversions: List[ConversionRecord]) -> Dict[str, Any]:
        """Analyze performance by format pairs"""
        try:
            format_performance = defaultdict(lambda: {
                'count': 0,
                'success_rate': 0.0,
                'average_duration': 0.0,
                'average_compression': 0.0,
                'average_quality_retention': 0.0
            })
            
            for conv in conversions:
                pair = (conv.source_format, conv.target_format)
                stats = format_performance[pair]
                
                stats['count'] += 1
                
                if conv.status == ConversionStatus.COMPLETED:
                    stats['success_rate'] += 1
                    
                    if conv.duration:
                        stats['average_duration'] += conv.duration
                    
                    if conv.compression_ratio:
                        stats['average_compression'] += conv.compression_ratio
                    
                    if conv.quality_retention:
                        stats['average_quality_retention'] += conv.quality_retention
            
            # Calculate averages
            for pair, stats in format_performance.items():
                if stats['count'] > 0:
                    stats['success_rate'] /= stats['count']
                    stats['average_duration'] /= stats['count']
                    stats['average_compression'] /= stats['count']
                    stats['average_quality_retention'] /= stats['count']
            
            return dict(format_performance)
            
        except Exception as e:
            self.logger.error(f"Format performance analysis failed: {e}")
            return {}
    
    async def recommend_optimal_formats(self, source_format: str, requirements: Dict[str, Any]) -> List[str]:
        """Recommend optimal target formats based on requirements"""
        try:
            recommendations = []
            compatible_formats = self.compatibility_matrix.get(source_format, [])
            
            # Analyze requirements
            priority_quality = requirements.get('quality_priority', False)
            priority_size = requirements.get('size_priority', False)
            priority_speed = requirements.get('speed_priority', False)
            target_platforms = requirements.get('platforms', [])
            
            # Score formats based on requirements
            format_scores = {}
            
            for target_format in compatible_formats:
                score = 0
                
                # Quality scoring (simplified)
                if priority_quality:
                    if target_format in ['flac', 'wav', 'png', 'tiff']:
                        score += 3
                    elif target_format in ['mp4', 'aac', 'jpg']:
                        score += 2
                
                # Size scoring
                if priority_size:
                    if target_format in ['webp', 'hevc', 'aac', 'opus']:
                        score += 3
                    elif target_format in ['mp4', 'mp3', 'jpg']:
                        score += 2
                
                # Speed scoring
                if priority_speed:
                    if target_format in ['mp4', 'jpg', 'mp3']:
                        score += 3
                    elif target_format in ['png', 'wav']:
                        score += 1
                
                # Platform compatibility
                if target_platforms:
                    platform_compatibility = self._check_platform_compatibility(target_format, target_platforms)
                    score += platform_compatibility * 2
                
                format_scores[target_format] = score
            
            # Sort by score and return top recommendations
            sorted_formats = sorted(format_scores.items(), key=lambda x: x[1], reverse=True)
            recommendations = [fmt for fmt, score in sorted_formats[:5] if score > 0]
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Format recommendation failed: {e}")
            return []
    
    def _check_platform_compatibility(self, format_name: str, platforms: List[str]) -> int:
        """Check format compatibility with specified platforms"""
        compatibility_score = 0
        
        platform_support = {
            'web': ['mp4', 'webm', 'mp3', 'aac', 'jpg', 'png', 'webp'],
            'mobile': ['mp4', 'mp3', 'aac', 'jpg', 'png'],
            'desktop': ['mp4', 'avi', 'mov', 'mp3', 'wav', 'flac', 'jpg', 'png', 'bmp'],
            'social_media': ['mp4', 'mp3', 'jpg', 'png'],
        }
        
        for platform in platforms:
            if platform in platform_support and format_name in platform_support[platform]:
                compatibility_score += 1
        
        return compatibility_score


class CompressionAnalytics:
    """Compression-specific analytics"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logger.getChild(self.__class__.__name__)
    
    async def analyze_compression_efficiency(self, conversions: List[ConversionRecord]) -> Dict[str, Any]:
        """Analyze compression efficiency across conversions"""
        try:
            compression_data = {
                'by_format': defaultdict(list),
                'by_size_range': defaultdict(list),
                'overall_stats': {}
            }
            
            compression_ratios = []
            quality_retentions = []
            
            for conv in conversions:
                if conv.compression_ratio and conv.status == ConversionStatus.COMPLETED:
                    # By format
                    format_pair = (conv.source_format, conv.target_format)
                    compression_data['by_format'][format_pair].append(conv.compression_ratio)
                    
                    # By size range
                    if conv.source_size:
                        size_mb = conv.source_size / (1024 * 1024)
                        size_range = self._get_size_range(size_mb)
                        compression_data['by_size_range'][size_range].append(conv.compression_ratio)
                    
                    compression_ratios.append(conv.compression_ratio)
                    
                    if conv.quality_retention:
                        quality_retentions.append(conv.quality_retention)
            
            # Calculate overall statistics
            if compression_ratios:
                compression_data['overall_stats'] = {
                    'average_compression_ratio': np.mean(compression_ratios),
                    'median_compression_ratio': np.median(compression_ratios),
                    'best_compression_ratio': np.min(compression_ratios),
                    'worst_compression_ratio': np.max(compression_ratios),
                    'compression_consistency': 1.0 - np.std(compression_ratios)
                }
            
            if quality_retentions:
                compression_data['overall_stats']['average_quality_retention'] = np.mean(quality_retentions)
            
            # Calculate format-specific averages
            format_averages = {}
            for format_pair, ratios in compression_data['by_format'].items():
                if ratios:
                    format_averages[format_pair] = {
                        'average_ratio': np.mean(ratios),
                        'count': len(ratios)
                    }
            
            compression_data['format_averages'] = format_averages
            
            return compression_data
            
        except Exception as e:
            self.logger.error(f"Compression efficiency analysis failed: {e}")
            return {}
    
    def _get_size_range(self, size_mb: float) -> str:
        """Categorize file size into ranges"""
        if size_mb < 1:
            return "< 1MB"
        elif size_mb < 10:
            return "1-10MB"
        elif size_mb < 100:
            return "10-100MB"
        elif size_mb < 1000:
            return "100MB-1GB"
        else:
            return "> 1GB"