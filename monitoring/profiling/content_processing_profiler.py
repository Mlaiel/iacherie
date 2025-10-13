"""⚡ Content Processing Performance Profiler
===========================================

Advanced profiling system for multi-format content processing in the Creator Economy platform.
Provides real-time monitoring of video, audio, image processing, and format conversion optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import logging
import time
import psutil
import threading
import subprocess
import tempfile
import os
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import gc

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content types for specialized profiling"""
    
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    ANIMATION = "animation"
    INTERACTIVE = "interactive"


class ProcessingOperation(Enum):
    """Content processing operations"""
    
    ENCODING = "encoding"
    DECODING = "decoding"
    TRANSCODING = "transcoding"
    COMPRESSION = "compression"
    RESIZING = "resizing"
    FILTERING = "filtering"
    WATERMARKING = "watermarking"
    THUMBNAIL_GENERATION = "thumbnail_generation"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    FORMAT_CONVERSION = "format_conversion"
    METADATA_EXTRACTION = "metadata_extraction"


class ProcessingQuality(Enum):
    """Processing quality levels"""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"
    LOSSLESS = "lossless"


@dataclass
class ContentMetadata:
    """Content file metadata"""
    
    file_path: str
    content_type: ContentType
    file_size: int  # bytes
    duration: Optional[float] = None  # seconds for video/audio
    width: Optional[int] = None  # pixels for image/video
    height: Optional[int] = None  # pixels for image/video
    fps: Optional[float] = None  # frames per second for video
    bitrate: Optional[int] = None  # bits per second for video/audio
    sample_rate: Optional[int] = None  # Hz for audio
    channels: Optional[int] = None  # audio channels
    codec: Optional[str] = None
    format: Optional[str] = None
    color_depth: Optional[int] = None  # bits per pixel
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ProcessingMetrics:
    """Content processing performance metrics"""
    
    operation: ProcessingOperation
    content_type: ContentType
    input_metadata: ContentMetadata
    output_metadata: Optional[ContentMetadata]
    processing_time: float  # seconds
    cpu_usage: float  # percentage
    memory_usage: int  # MB
    disk_io_read: int  # MB
    disk_io_write: int  # MB
    quality_settings: ProcessingQuality
    throughput: float  # MB/s
    compression_ratio: Optional[float] = None
    quality_score: Optional[float] = None  # 0-100
    hardware_acceleration: bool = False
    parallel_threads: int = 1
    temp_files_created: int = 0
    temp_storage_used: int = 0  # MB
    error_count: int = 0
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        # Calculate throughput
        if self.processing_time > 0 and self.input_metadata.file_size > 0:
            self.throughput = (self.input_metadata.file_size / (1024 * 1024)) / self.processing_time
        
        # Calculate compression ratio
        if (self.output_metadata and 
            self.input_metadata.file_size > 0 and 
            self.output_metadata.file_size > 0):
            self.compression_ratio = self.input_metadata.file_size / self.output_metadata.file_size


@dataclass
class ProcessingBottleneck:
    """Content processing bottleneck detection"""
    
    bottleneck_type: str
    severity: str  # low, medium, high, critical
    description: str
    affected_operation: ProcessingOperation
    content_type: ContentType
    performance_impact: float  # percentage
    optimization_suggestions: List[str]
    hardware_recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class ContentProcessingProfiler:
    """
    Advanced Content Processing Performance Profiler
    
    Provides comprehensive profiling for content processing with focus on:
    - Multi-format content processing monitoring
    - Hardware utilization tracking
    - Format conversion optimization
    - Quality vs performance analysis
    - Processing pipeline bottleneck detection
    """
    
    def __init__(
        self,
        enable_hardware_monitoring: bool = True,
        enable_disk_io_monitoring: bool = True,
        sampling_interval: float = 0.5,
        max_history_size: int = 5000,
        temp_directory: Optional[str] = None
    ):
        """
        Initialize Content Processing Profiler
        
        Args:
            enable_hardware_monitoring: Enable CPU/Memory monitoring
            enable_disk_io_monitoring: Enable disk I/O tracking
            sampling_interval: Metrics collection interval in seconds
            max_history_size: Maximum number of metrics to keep
            temp_directory: Directory for temporary files monitoring
        """
        self.enable_hardware_monitoring = enable_hardware_monitoring
        self.enable_disk_io_monitoring = enable_disk_io_monitoring
        self.sampling_interval = sampling_interval
        self.max_history_size = max_history_size
        self.temp_directory = temp_directory or tempfile.gettempdir()
        
        # Metrics storage
        self.processing_metrics: deque = deque(maxlen=max_history_size)
        self.bottlenecks: deque = deque(maxlen=max_history_size)
        
        # Active processing sessions
        self.active_sessions: Dict[str, Dict] = {}
        self.session_lock = threading.Lock()
        
        # Hardware monitoring
        self.hardware_stats: Dict[str, Any] = {}
        
        # Prometheus metrics
        self._setup_prometheus_metrics()
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # FFmpeg and processing tools availability
        self.ffmpeg_available = self._check_ffmpeg_availability()
        self.opencv_available = self._check_opencv_availability()
        
        logger.info("ContentProcessingProfiler initialized - FFmpeg: %s, OpenCV: %s",
                   self.ffmpeg_available, self.opencv_available)
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for monitoring"""
        
        self.processing_time_histogram = Histogram(
            'content_processing_time_seconds',
            'Content processing time',
            ['operation', 'content_type', 'quality']
        )
        
        self.throughput_gauge = Gauge(
            'content_processing_throughput_mbps',
            'Content processing throughput in MB/s',
            ['operation', 'content_type']
        )
        
        self.cpu_utilization_gauge = Gauge(
            'content_processing_cpu_percent',
            'CPU utilization during content processing',
            ['operation']
        )
        
        self.memory_usage_gauge = Gauge(
            'content_processing_memory_mb',
            'Memory usage during content processing',
            ['operation']
        )
        
        self.compression_ratio_gauge = Gauge(
            'content_compression_ratio',
            'Content compression ratio',
            ['content_type', 'operation']
        )
        
        self.bottleneck_counter = Counter(
            'content_processing_bottlenecks_total',
            'Total content processing bottlenecks',
            ['bottleneck_type', 'severity']
        )
        
        self.error_counter = Counter(
            'content_processing_errors_total',
            'Total content processing errors',
            ['operation', 'content_type']
        )
    
    def _check_ffmpeg_availability(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_opencv_availability(self) -> bool:
        """Check if OpenCV is available"""
        try:
            import cv2
            return True
        except ImportError:
            return False
    
    def _get_file_metadata(self, file_path: str, content_type: ContentType) -> ContentMetadata:
        """Extract metadata from content file"""
        try:
            stat_info = os.stat(file_path)
            file_size = stat_info.st_size
            
            metadata = ContentMetadata(
                file_path=file_path,
                content_type=content_type,
                file_size=file_size
            )
            
            # Extract format-specific metadata
            if content_type in [ContentType.VIDEO, ContentType.AUDIO] and self.ffmpeg_available:
                metadata = self._extract_ffmpeg_metadata(file_path, metadata)
            elif content_type == ContentType.IMAGE and self.opencv_available:
                metadata = self._extract_image_metadata(file_path, metadata)
            
            return metadata
            
        except Exception as e:
            logger.error("Error extracting metadata from %s: %s", file_path, e)
            return ContentMetadata(
                file_path=file_path,
                content_type=content_type,
                file_size=0
            )
    
    def _extract_ffmpeg_metadata(self, file_path: str, metadata: ContentMetadata) -> ContentMetadata:
        """Extract metadata using FFmpeg"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return metadata
            
            data = json.loads(result.stdout)
            
            # Extract format information
            if 'format' in data:
                format_info = data['format']
                metadata.duration = float(format_info.get('duration', 0))
                metadata.bitrate = int(format_info.get('bit_rate', 0))
                metadata.format = format_info.get('format_name', '')
            
            # Extract stream information
            if 'streams' in data:
                for stream in data['streams']:
                    codec_type = stream.get('codec_type')
                    
                    if codec_type == 'video':
                        metadata.width = int(stream.get('width', 0))
                        metadata.height = int(stream.get('height', 0))
                        metadata.fps = eval(stream.get('r_frame_rate', '0')) if stream.get('r_frame_rate') else 0
                        metadata.codec = stream.get('codec_name', '')
                    
                    elif codec_type == 'audio':
                        metadata.sample_rate = int(stream.get('sample_rate', 0))
                        metadata.channels = int(stream.get('channels', 0))
                        if not metadata.codec:
                            metadata.codec = stream.get('codec_name', '')
            
            return metadata
            
        except Exception as e:
            logger.error("Error extracting FFmpeg metadata: %s", e)
            return metadata
    
    def _extract_image_metadata(self, file_path: str, metadata: ContentMetadata) -> ContentMetadata:
        """Extract image metadata using OpenCV"""
        try:
            import cv2
            
            image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            if image is not None:
                metadata.height, metadata.width = image.shape[:2]
                metadata.color_depth = image.dtype.itemsize * 8
                if len(image.shape) > 2:
                    metadata.channels = image.shape[2]
                
                # Detect format from file extension
                _, ext = os.path.splitext(file_path)
                metadata.format = ext.lower()[1:] if ext else 'unknown'
            
            return metadata
            
        except Exception as e:
            logger.error("Error extracting image metadata: %s", e)
            return metadata
    
    def _get_hardware_stats(self) -> Dict[str, Any]:
        """Get current hardware utilization stats"""
        if not self.enable_hardware_monitoring:
            return {}
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            stats = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_mb': memory.used // (1024 * 1024),
                'memory_available_mb': memory.available // (1024 * 1024),
                'timestamp': datetime.now()
            }
            
            # Disk I/O stats if enabled
            if self.enable_disk_io_monitoring:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    stats.update({
                        'disk_read_mb': disk_io.read_bytes // (1024 * 1024),
                        'disk_write_mb': disk_io.write_bytes // (1024 * 1024),
                        'disk_read_count': disk_io.read_count,
                        'disk_write_count': disk_io.write_count
                    })
            
            return stats
            
        except Exception as e:
            logger.error("Error getting hardware stats: %s", e)
            return {}
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Content processing background monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("Content processing background monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Update hardware stats
                self.hardware_stats = self._get_hardware_stats()
                
                # Analyze for bottlenecks
                self._detect_bottlenecks()
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                logger.error("Error in monitoring loop: %s", e)
                time.sleep(1.0)
    
    def start_processing_profiling(
        self,
        input_file: str,
        operation: ProcessingOperation,
        content_type: ContentType,
        quality_settings: ProcessingQuality = ProcessingQuality.MEDIUM,
        session_id: Optional[str] = None
    ) -> str:
        """
        Start profiling a content processing operation
        
        Args:
            input_file: Path to input file
            operation: Type of processing operation
            content_type: Type of content being processed
            quality_settings: Processing quality level
            session_id: Optional session identifier
        
        Returns:
            session_id: Unique identifier for this profiling session
        """
        if session_id is None:
            session_id = f"{operation.value}_{content_type.value}_{int(time.time() * 1000)}"
        
        # Extract input metadata
        input_metadata = self._get_file_metadata(input_file, content_type)
        
        # Get initial hardware stats
        initial_stats = self._get_hardware_stats()
        
        session_data = {
            'operation': operation,
            'content_type': content_type,
            'input_metadata': input_metadata,
            'quality_settings': quality_settings,
            'start_time': time.time(),
            'initial_stats': initial_stats,
            'temp_files_created': 0,
            'temp_storage_used': 0,
            'warnings': [],
            'error_count': 0
        }
        
        with self.session_lock:
            self.active_sessions[session_id] = session_data
        
        logger.debug("Started processing profiling session: %s", session_id)
        return session_id
    
    def add_warning(self, session_id: str, warning: str):
        """Add a warning to the processing session"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['warnings'].append(warning)
    
    def increment_error_count(self, session_id: str):
        """Increment error count for the session"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['error_count'] += 1
    
    def track_temp_file(self, session_id: str, file_path: str):
        """Track temporary file creation"""
        with self.session_lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session['temp_files_created'] += 1
                
                try:
                    file_size = os.path.getsize(file_path) // (1024 * 1024)  # MB
                    session['temp_storage_used'] += file_size
                except:
                    pass
    
    def end_processing_profiling(
        self,
        session_id: str,
        output_file: Optional[str] = None,
        quality_score: Optional[float] = None,
        hardware_acceleration: bool = False,
        parallel_threads: int = 1
    ) -> ProcessingMetrics:
        """
        End profiling session and return metrics
        
        Args:
            session_id: Session identifier
            output_file: Path to output file (if any)
            quality_score: Quality assessment score (0-100)
            hardware_acceleration: Whether hardware acceleration was used
            parallel_threads: Number of parallel threads used
        
        Returns:
            ProcessingMetrics: Complete processing metrics
        """
        with self.session_lock:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session_data = self.active_sessions.pop(session_id)
        
        end_time = time.time()
        processing_time = end_time - session_data['start_time']
        
        # Get final hardware stats
        final_stats = self._get_hardware_stats()
        
        # Calculate hardware utilization
        cpu_usage = 0.0
        memory_usage = 0
        disk_io_read = 0
        disk_io_write = 0
        
        if session_data['initial_stats'] and final_stats:
            cpu_usage = final_stats.get('cpu_percent', 0)
            memory_usage = final_stats.get('memory_used_mb', 0)
            
            if self.enable_disk_io_monitoring:
                initial_read = session_data['initial_stats'].get('disk_read_mb', 0)
                initial_write = session_data['initial_stats'].get('disk_write_mb', 0)
                final_read = final_stats.get('disk_read_mb', 0)
                final_write = final_stats.get('disk_write_mb', 0)
                
                disk_io_read = max(0, final_read - initial_read)
                disk_io_write = max(0, final_write - initial_write)
        
        # Extract output metadata if output file exists
        output_metadata = None
        if output_file and os.path.exists(output_file):
            output_metadata = self._get_file_metadata(output_file, session_data['content_type'])
        
        # Create metrics object
        metrics = ProcessingMetrics(
            operation=session_data['operation'],
            content_type=session_data['content_type'],
            input_metadata=session_data['input_metadata'],
            output_metadata=output_metadata,
            processing_time=processing_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_io_read=disk_io_read,
            disk_io_write=disk_io_write,
            quality_settings=session_data['quality_settings'],
            throughput=0.0,  # Will be calculated in __post_init__
            quality_score=quality_score,
            hardware_acceleration=hardware_acceleration,
            parallel_threads=parallel_threads,
            temp_files_created=session_data['temp_files_created'],
            temp_storage_used=session_data['temp_storage_used'],
            error_count=session_data['error_count'],
            warnings=session_data['warnings']
        )
        
        # Store metrics
        self.processing_metrics.append(metrics)
        
        # Update Prometheus metrics
        self.processing_time_histogram.labels(
            operation=metrics.operation.value,
            content_type=metrics.content_type.value,
            quality=metrics.quality_settings.value
        ).observe(metrics.processing_time)
        
        self.throughput_gauge.labels(
            operation=metrics.operation.value,
            content_type=metrics.content_type.value
        ).set(metrics.throughput)
        
        self.cpu_utilization_gauge.labels(
            operation=metrics.operation.value
        ).set(metrics.cpu_usage)
        
        self.memory_usage_gauge.labels(
            operation=metrics.operation.value
        ).set(metrics.memory_usage)
        
        if metrics.compression_ratio:
            self.compression_ratio_gauge.labels(
                content_type=metrics.content_type.value,
                operation=metrics.operation.value
            ).set(metrics.compression_ratio)
        
        if metrics.error_count > 0:
            self.error_counter.labels(
                operation=metrics.operation.value,
                content_type=metrics.content_type.value
            ).inc(metrics.error_count)
        
        logger.info("Processing profiling completed for %s: %.2fs, %.1f MB/s",
                   session_id, metrics.processing_time, metrics.throughput)
        
        return metrics
    
    def _detect_bottlenecks(self):
        """Detect performance bottlenecks in content processing"""
        if len(self.processing_metrics) < 3:
            return
        
        recent_metrics = list(self.processing_metrics)[-10:]  # Last 10 operations
        
        # Analyze processing time trends by operation
        operations_data = defaultdict(list)
        for metric in recent_metrics:
            operations_data[metric.operation].append(metric)
        
        for operation, metrics_list in operations_data.items():
            if len(metrics_list) < 2:
                continue
            
            processing_times = [m.processing_time for m in metrics_list]
            avg_processing_time = statistics.mean(processing_times)
            
            # Check for slow processing
            if avg_processing_time > 30.0:  # 30 seconds threshold
                bottleneck = ProcessingBottleneck(
                    bottleneck_type="slow_processing",
                    severity="high" if avg_processing_time > 60.0 else "medium",
                    description=f"Average {operation.value} time is {avg_processing_time:.1f}s",
                    affected_operation=operation,
                    content_type=metrics_list[0].content_type,
                    performance_impact=min(100, (avg_processing_time / 10.0) * 20),
                    optimization_suggestions=[
                        "Enable hardware acceleration",
                        "Increase parallel processing threads",
                        "Use lower quality settings for preview",
                        "Implement progressive processing"
                    ],
                    hardware_recommendations=[
                        "Upgrade to SSD storage",
                        "Add more RAM",
                        "Use GPU acceleration",
                        "Optimize CPU with more cores"
                    ]
                )
                self._record_bottleneck(bottleneck)
            
            # Check for low throughput
            throughputs = [m.throughput for m in metrics_list if m.throughput > 0]
            if throughputs:
                avg_throughput = statistics.mean(throughputs)
                
                if avg_throughput < 5.0:  # 5 MB/s threshold
                    bottleneck = ProcessingBottleneck(
                        bottleneck_type="low_throughput",
                        severity="medium",
                        description=f"Low {operation.value} throughput: {avg_throughput:.1f} MB/s",
                        affected_operation=operation,
                        content_type=metrics_list[0].content_type,
                        performance_impact=min(100, (10.0 / avg_throughput) * 20),
                        optimization_suggestions=[
                            "Optimize I/O operations",
                            "Use batch processing",
                            "Implement streaming processing",
                            "Reduce unnecessary file operations"
                        ],
                        hardware_recommendations=[
                            "Use faster storage (NVMe SSD)",
                            "Increase network bandwidth",
                            "Optimize disk I/O patterns",
                            "Use RAID configuration"
                        ]
                    )
                    self._record_bottleneck(bottleneck)
        
        # Check current hardware utilization
        if self.hardware_stats:
            cpu_percent = self.hardware_stats.get('cpu_percent', 0)
            memory_percent = self.hardware_stats.get('memory_percent', 0)
            
            # High CPU utilization
            if cpu_percent > 90:
                bottleneck = ProcessingBottleneck(
                    bottleneck_type="high_cpu_utilization",
                    severity="high",
                    description=f"CPU utilization is {cpu_percent:.1f}%",
                    affected_operation=ProcessingOperation.ENCODING,  # Most common
                    content_type=ContentType.VIDEO,  # Most CPU intensive
                    performance_impact=cpu_percent - 70,
                    optimization_suggestions=[
                        "Reduce parallel processing threads",
                        "Use hardware acceleration",
                        "Lower processing quality temporarily",
                        "Implement processing queue"
                    ],
                    hardware_recommendations=[
                        "Upgrade to more CPU cores",
                        "Improve CPU cooling",
                        "Use dedicated processing servers"
                    ]
                )
                self._record_bottleneck(bottleneck)
            
            # High memory utilization
            if memory_percent > 85:
                bottleneck = ProcessingBottleneck(
                    bottleneck_type="high_memory_utilization",
                    severity="high" if memory_percent > 95 else "medium",
                    description=f"Memory utilization is {memory_percent:.1f}%",
                    affected_operation=ProcessingOperation.ENCODING,
                    content_type=ContentType.VIDEO,
                    performance_impact=memory_percent - 70,
                    optimization_suggestions=[
                        "Process smaller chunks",
                        "Implement streaming processing",
                        "Clear temporary files more frequently",
                        "Reduce concurrent operations"
                    ],
                    hardware_recommendations=[
                        "Add more RAM",
                        "Use swap file optimization",
                        "Distribute processing across nodes"
                    ]
                )
                self._record_bottleneck(bottleneck)
    
    def _record_bottleneck(self, bottleneck: ProcessingBottleneck):
        """Record a detected bottleneck"""
        self.bottlenecks.append(bottleneck)
        
        # Update Prometheus counter
        self.bottleneck_counter.labels(
            bottleneck_type=bottleneck.bottleneck_type,
            severity=bottleneck.severity
        ).inc()
        
        logger.warning("Content processing bottleneck detected: %s (%s severity)",
                      bottleneck.description, bottleneck.severity)
    
    def get_optimization_recommendations(
        self,
        operation: Optional[ProcessingOperation] = None,
        content_type: Optional[ContentType] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> List[Dict[str, Any]]:
        """
        Get content processing optimization recommendations
        
        Args:
            operation: Specific operation to analyze
            content_type: Specific content type to analyze
            time_window: Time window for analysis
        
        Returns:
            List of optimization recommendations
        """
        cutoff_time = datetime.now() - time_window
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.processing_metrics
            if (m.timestamp >= cutoff_time and
                (operation is None or m.operation == operation) and
                (content_type is None or m.content_type == content_type))
        ]
        
        if not recent_metrics:
            return []
        
        recommendations = []
        
        # Analyze processing time vs quality
        quality_performance = defaultdict(list)
        for metric in recent_metrics:
            quality_performance[metric.quality_settings].append(metric.processing_time)
        
        if len(quality_performance) > 1:
            # Find optimal quality/performance balance
            quality_efficiency = {}
            for quality, times in quality_performance.items():
                avg_time = statistics.mean(times)
                # Simple efficiency score: lower time is better
                quality_efficiency[quality] = 1.0 / avg_time if avg_time > 0 else 0
            
            best_quality = max(quality_efficiency.keys(), key=lambda x: quality_efficiency[x])
            recommendations.append({
                'type': 'quality_optimization',
                'priority': 'medium',
                'description': f'Optimal quality setting appears to be {best_quality.value}',
                'suggestions': [
                    f'Use {best_quality.value} quality for better performance',
                    'Implement adaptive quality based on content',
                    'Consider user preference vs performance trade-offs'
                ],
                'expected_improvement': 'Up to 40% processing time reduction'
            })
        
        # Analyze hardware acceleration usage
        hw_accel_metrics = [m for m in recent_metrics if m.hardware_acceleration]
        non_hw_accel_metrics = [m for m in recent_metrics if not m.hardware_acceleration]
        
        if hw_accel_metrics and non_hw_accel_metrics:
            hw_avg_time = statistics.mean([m.processing_time for m in hw_accel_metrics])
            non_hw_avg_time = statistics.mean([m.processing_time for m in non_hw_accel_metrics])
            
            if non_hw_avg_time > hw_avg_time * 1.5:  # 50% slower without HW accel
                recommendations.append({
                    'type': 'hardware_acceleration',
                    'priority': 'high',
                    'description': f'Hardware acceleration reduces processing time by {((non_hw_avg_time / hw_avg_time - 1) * 100):.0f}%',
                    'suggestions': [
                        'Enable hardware acceleration for all operations',
                        'Use GPU-optimized codecs',
                        'Implement automatic fallback to SW if HW fails'
                    ],
                    'expected_improvement': f'{((non_hw_avg_time / hw_avg_time - 1) * 100):.0f}% faster processing'
                })
        
        # Analyze parallel processing efficiency
        threading_data = defaultdict(list)
        for metric in recent_metrics:
            threading_data[metric.parallel_threads].append(metric.processing_time)
        
        if len(threading_data) > 1:
            # Find optimal thread count
            thread_efficiency = {}
            for threads, times in threading_data.items():
                avg_time = statistics.mean(times)
                # Efficiency considers both time and thread count
                thread_efficiency[threads] = threads / avg_time if avg_time > 0 else 0
            
            optimal_threads = max(thread_efficiency.keys(), key=lambda x: thread_efficiency[x])
            current_threads = statistics.mode([m.parallel_threads for m in recent_metrics])
            
            if optimal_threads != current_threads:
                recommendations.append({
                    'type': 'parallel_processing',
                    'priority': 'medium',
                    'description': f'Optimal thread count is {optimal_threads} vs current {current_threads}',
                    'suggestions': [
                        f'Use {optimal_threads} threads for processing',
                        'Implement dynamic thread scaling',
                        'Monitor CPU core utilization'
                    ],
                    'expected_improvement': f'{((thread_efficiency[optimal_threads] / thread_efficiency[current_threads] - 1) * 100):.0f}% efficiency gain'
                })
        
        return recommendations
    
    def get_performance_summary(
        self,
        operation: Optional[ProcessingOperation] = None,
        content_type: Optional[ContentType] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """
        Get performance summary for content processing
        
        Args:
            operation: Specific operation to analyze
            content_type: Specific content type to analyze
            time_window: Time window for analysis
        
        Returns:
            Performance summary dictionary
        """
        cutoff_time = datetime.now() - time_window
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.processing_metrics
            if (m.timestamp >= cutoff_time and
                (operation is None or m.operation == operation) and
                (content_type is None or m.content_type == content_type))
        ]
        
        if not recent_metrics:
            return {'error': 'No metrics available'}
        
        # Calculate statistics
        processing_times = [m.processing_time for m in recent_metrics]
        throughputs = [m.throughput for m in recent_metrics if m.throughput > 0]
        cpu_usages = [m.cpu_usage for m in recent_metrics if m.cpu_usage > 0]
        compression_ratios = [m.compression_ratio for m in recent_metrics if m.compression_ratio]
        
        summary = {
            'time_window': str(time_window),
            'total_operations': len(recent_metrics),
            'operations_analyzed': len(set(m.operation for m in recent_metrics)),
            'content_types_processed': len(set(m.content_type for m in recent_metrics)),
            'performance_metrics': {
                'avg_processing_time': statistics.mean(processing_times),
                'p95_processing_time': statistics.quantiles(processing_times, n=20)[18] if len(processing_times) >= 20 else max(processing_times),
                'total_errors': sum(m.error_count for m in recent_metrics),
                'total_warnings': sum(len(m.warnings) for m in recent_metrics)
            }
        }
        
        if throughputs:
            summary['performance_metrics'].update({
                'avg_throughput': statistics.mean(throughputs),
                'max_throughput': max(throughputs)
            })
        
        if cpu_usages:
            summary['performance_metrics'].update({
                'avg_cpu_usage': statistics.mean(cpu_usages),
                'max_cpu_usage': max(cpu_usages)
            })
        
        if compression_ratios:
            summary['performance_metrics'].update({
                'avg_compression_ratio': statistics.mean(compression_ratios),
                'best_compression_ratio': max(compression_ratios)
            })
        
        # Hardware acceleration statistics
        hw_accel_count = len([m for m in recent_metrics if m.hardware_acceleration])
        summary['hardware_acceleration'] = {
            'usage_percentage': (hw_accel_count / len(recent_metrics)) * 100,
            'operations_with_hw_accel': hw_accel_count
        }
        
        # Quality distribution
        quality_dist = defaultdict(int)
        for metric in recent_metrics:
            quality_dist[metric.quality_settings.value] += 1
        summary['quality_distribution'] = dict(quality_dist)
        
        # Recent bottlenecks
        recent_bottlenecks = [b for b in self.bottlenecks if b.timestamp >= cutoff_time]
        summary['bottlenecks'] = {
            'total_count': len(recent_bottlenecks),
            'by_severity': {
                severity: len([b for b in recent_bottlenecks if b.severity == severity])
                for severity in ['low', 'medium', 'high', 'critical']
            }
        }
        
        return summary
    
    def export_metrics(self, format_type: str = 'json') -> str:
        """
        Export processing metrics in specified format
        
        Args:
            format_type: Export format ('json', 'csv')
        
        Returns:
            Formatted metrics data
        """
        if format_type.lower() == 'json':
            data = {
                'processing_metrics': [
                    {
                        'operation': m.operation.value,
                        'content_type': m.content_type.value,
                        'processing_time': m.processing_time,
                        'throughput': m.throughput,
                        'cpu_usage': m.cpu_usage,
                        'memory_usage': m.memory_usage,
                        'quality_settings': m.quality_settings.value,
                        'hardware_acceleration': m.hardware_acceleration,
                        'parallel_threads': m.parallel_threads,
                        'compression_ratio': m.compression_ratio,
                        'error_count': m.error_count,
                        'timestamp': m.timestamp.isoformat()
                    }
                    for m in self.processing_metrics
                ],
                'bottlenecks': [
                    {
                        'type': b.bottleneck_type,
                        'severity': b.severity,
                        'description': b.description,
                        'affected_operation': b.affected_operation.value,
                        'content_type': b.content_type.value,
                        'performance_impact': b.performance_impact,
                        'timestamp': b.timestamp.isoformat()
                    }
                    for b in self.bottlenecks
                ]
            }
            return json.dumps(data, indent=2)
        
        elif format_type.lower() == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow([
                'timestamp', 'operation', 'content_type', 'processing_time',
                'throughput', 'cpu_usage', 'memory_usage', 'quality_settings',
                'hardware_acceleration', 'parallel_threads', 'compression_ratio',
                'error_count'
            ])
            
            # Write data
            for m in self.processing_metrics:
                writer.writerow([
                    m.timestamp.isoformat(),
                    m.operation.value,
                    m.content_type.value,
                    m.processing_time,
                    m.throughput,
                    m.cpu_usage,
                    m.memory_usage,
                    m.quality_settings.value,
                    m.hardware_acceleration,
                    m.parallel_threads,
                    m.compression_ratio,
                    m.error_count
                ])
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")


# Context manager for easy profiling
class ProcessingProfiler:
    """Context manager for content processing profiling"""
    
    def __init__(
        self,
        profiler: ContentProcessingProfiler,
        input_file: str,
        operation: ProcessingOperation,
        content_type: ContentType,
        quality_settings: ProcessingQuality = ProcessingQuality.MEDIUM
    ):
        self.profiler = profiler
        self.input_file = input_file
        self.operation = operation
        self.content_type = content_type
        self.quality_settings = quality_settings
        self.session_id: Optional[str] = None
    
    def __enter__(self):
        self.session_id = self.profiler.start_processing_profiling(
            input_file=self.input_file,
            operation=self.operation,
            content_type=self.content_type,
            quality_settings=self.quality_settings
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session_id:
            return self.profiler.end_processing_profiling(self.session_id)
        return None
    
    def add_warning(self, warning: str):
        if self.session_id:
            self.profiler.add_warning(self.session_id, warning)
    
    def increment_error_count(self):
        if self.session_id:
            self.profiler.increment_error_count(self.session_id)
    
    def track_temp_file(self, file_path: str):
        if self.session_id:
            self.profiler.track_temp_file(self.session_id, file_path)


# Factory function for creating profiler instances
def create_content_processing_profiler(
    enable_hardware_monitoring: bool = True,
    enable_disk_io_monitoring: bool = True,
    start_monitoring: bool = True
) -> ContentProcessingProfiler:
    """
    Factory function to create and configure Content Processing Profiler
    
    Args:
        enable_hardware_monitoring: Enable CPU/Memory monitoring
        enable_disk_io_monitoring: Enable disk I/O tracking
        start_monitoring: Start background monitoring immediately
    
    Returns:
        Configured ContentProcessingProfiler instance
    """
    profiler = ContentProcessingProfiler(
        enable_hardware_monitoring=enable_hardware_monitoring,
        enable_disk_io_monitoring=enable_disk_io_monitoring
    )
    
    if start_monitoring:
        profiler.start_monitoring()
    
    return profiler


if __name__ == "__main__":
    # Example usage
    import tempfile
    
    # Create profiler
    profiler = create_content_processing_profiler()
    
    # Example: Profile video transcoding
    with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_input:
        # Write dummy data to temp file
        temp_input.write(b'dummy video data')
        temp_input.flush()
        
        with ProcessingProfiler(
            profiler=profiler,
            input_file=temp_input.name,
            operation=ProcessingOperation.TRANSCODING,
            content_type=ContentType.VIDEO,
            quality_settings=ProcessingQuality.HIGH
        ) as session:
            
            # Simulate processing
            time.sleep(2.0)
            
            # Add some warnings
            session.add_warning("High CPU usage detected")
            
            # Track temp file creation
            session.track_temp_file("/tmp/temp_frame.jpg")
    
    # Get performance summary
    summary = profiler.get_performance_summary()
    print("Performance Summary:", json.dumps(summary, indent=2))
    
    # Get optimization recommendations
    recommendations = profiler.get_optimization_recommendations()
    print("Optimization Recommendations:", json.dumps(recommendations, indent=2))
    
    # Stop monitoring
    profiler.stop_monitoring()