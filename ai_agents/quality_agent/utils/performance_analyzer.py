"""
Performance Analyzer - Advanced Content Performance Analysis Engine

Comprehensive performance analysis system for content optimization and metrics calculation.
Provides detailed performance insights, bottleneck detection, and optimization recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from pathlib import Path
import psutil
import statistics

try:
    from core.exceptions import PerformanceError, AnalysisError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    PerformanceError, AnalysisError = globals().get('PerformanceError, AnalysisError', Exception)
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...utils.system_monitor import SystemMonitor
from ...utils.content_profiler import ContentProfiler
from ...monitoring.metrics_collector import MetricsCollector
from ...database.models.performance import PerformanceReport, PerformanceMetric
from ..quality_agent import ContentType

logger = logging.getLogger(__name__)

class PerformanceCategory(Enum):
    """Performance analysis categories"""
    PROCESSING_SPEED = "processing_speed"
    MEMORY_USAGE = "memory_usage"
    STORAGE_EFFICIENCY = "storage_efficiency"
    NETWORK_PERFORMANCE = "network_performance"
    CONTENT_DELIVERY = "content_delivery"
    USER_EXPERIENCE = "user_experience"
    SCALABILITY = "scalability"
    OPTIMIZATION = "optimization"

class MetricType(Enum):
    """Types of performance metrics"""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    BANDWIDTH = "bandwidth"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    CACHE_HIT_RATE = "cache_hit_rate"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"

class PerformanceLevel(Enum):
    """Performance quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    metric_id: str
    metric_type: MetricType
    category: PerformanceCategory
    name: str
    value: float
    unit: str
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    trend: Optional[str] = None  # improving, stable, degrading
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class PerformanceBottleneck:
    """Identified performance bottleneck"""
    bottleneck_id: str
    category: PerformanceCategory
    severity: str  # critical, high, medium, low
    title: str
    description: str
    impact_score: float  # 0-100
    affected_metrics: List[str]
    root_cause: str
    recommendations: List[str]
    estimated_improvement: float
    fix_complexity: str  # low, medium, high
    fix_effort: str  # minutes, hours, days
    priority_score: float
    evidence: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""
    recommendation_id: str
    category: PerformanceCategory
    title: str
    description: str
    expected_improvement: Dict[str, float]  # metric -> improvement percentage
    implementation_steps: List[str]
    prerequisites: List[str]
    estimated_effort: str
    difficulty_level: str
    roi_score: float
    risk_level: str
    testing_requirements: List[str]
    success_metrics: List[str]

@dataclass
class PerformanceAnalysisResult:
    """Complete performance analysis result"""
    analysis_id: str
    content_id: str
    content_type: ContentType
    analysis_timestamp: datetime
    overall_performance_score: float
    performance_level: PerformanceLevel
    category_scores: Dict[PerformanceCategory, float]
    metrics: List[PerformanceMetric]
    bottlenecks: List[PerformanceBottleneck]
    recommendations: List[OptimizationRecommendation]
    benchmark_comparison: Dict[str, Any]
    trend_analysis: Dict[str, Any]
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class PerformanceAnalyzer:
    """
    Advanced Performance Analyzer for comprehensive content performance evaluation.
    
    Features:
    - Multi-dimensional performance analysis
    - Real-time performance monitoring
    - Bottleneck detection and analysis
    - Optimization recommendations
    - Performance trend analysis
    - Benchmark comparison
    - Scalability assessment
    - Resource utilization analysis
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.system_monitor = SystemMonitor()
        self.content_profiler = ContentProfiler()
        self.metrics_collector = MetricsCollector()
        
        # Performance baselines and thresholds
        self.performance_baselines = self._load_performance_baselines()
        self.performance_thresholds = self._load_performance_thresholds()
        
        # Analysis cache and history
        self.analysis_cache = {}
        self.performance_history = {}
        
        # Monitoring state
        self.active_monitors = {}
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("PerformanceAnalyzer initialized successfully")

    async def analyze_performance(
        self,
        content_id: str,
        content_path: str,
        content_type: ContentType,
        analysis_categories: Optional[List[PerformanceCategory]] = None,
        baseline_comparison: bool = True,
        include_recommendations: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PerformanceAnalysisResult:
        """
        Perform comprehensive performance analysis of content.
        
        Args:
            content_id: Unique identifier for the content
            content_path: Path to content file
            content_type: Type of content being analyzed
            analysis_categories: Specific categories to analyze
            baseline_comparison: Whether to compare against baselines
            include_recommendations: Whether to generate optimization recommendations
            metadata: Additional content metadata
            
        Returns:
            PerformanceAnalysisResult: Complete performance analysis
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting performance analysis for {content_id}")
            
            analysis_id = f"perf_analysis_{uuid.uuid4().hex[:8]}"
            
            # Determine analysis categories
            categories = analysis_categories or list(PerformanceCategory)
            
            # Collect performance metrics
            metrics = await self._collect_performance_metrics(
                content_path, content_type, categories, metadata
            )
            
            # Calculate category scores
            category_scores = await self._calculate_category_scores(metrics, categories)
            
            # Calculate overall performance score
            overall_score = await self._calculate_overall_performance_score(
                category_scores, content_type
            )
            
            # Determine performance level
            performance_level = self._determine_performance_level(overall_score)
            
            # Detect bottlenecks
            bottlenecks = await self._detect_performance_bottlenecks(
                metrics, category_scores, content_type
            )
            
            # Generate optimization recommendations
            recommendations = []
            if include_recommendations:
                recommendations = await self._generate_optimization_recommendations(
                    metrics, bottlenecks, category_scores, content_type
                )
                
            # Benchmark comparison
            benchmark_comparison = {}
            if baseline_comparison:
                benchmark_comparison = await self._compare_with_benchmarks(
                    content_type, category_scores, overall_score, metrics
                )
                
            # Trend analysis
            trend_analysis = await self._analyze_performance_trends(
                content_id, metrics, category_scores
            )
            
            # Create analysis result
            result = PerformanceAnalysisResult(
                analysis_id=analysis_id,
                content_id=content_id,
                content_type=content_type,
                analysis_timestamp=datetime.now(timezone.utc),
                overall_performance_score=overall_score,
                performance_level=performance_level,
                category_scores=category_scores,
                metrics=metrics,
                bottlenecks=bottlenecks,
                recommendations=recommendations,
                benchmark_comparison=benchmark_comparison,
                trend_analysis=trend_analysis,
                processing_time=time.time() - start_time,
                metadata=metadata or {}
            )
            
            # Cache result
            self.analysis_cache[analysis_id] = result
            
            # Update performance history
            await self._update_performance_history(content_id, result)
            
            self.logger.info(
                f"Performance analysis completed for {content_id}: "
                f"Score: {overall_score:.1f}, Level: {performance_level.value}, "
                f"Bottlenecks: {len(bottlenecks)}, Processing time: {result.processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Performance analysis failed for {content_id}: {str(e)}")
            raise PerformanceError(f"Performance analysis failed: {str(e)}")

    async def _collect_performance_metrics(
        self,
        content_path: str,
        content_type: ContentType,
        categories: List[PerformanceCategory],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[PerformanceMetric]:
        """Collect performance metrics for all categories"""
        
        all_metrics = []
        
        try:
            for category in categories:
                category_metrics = await self._collect_category_metrics(
                    content_path, content_type, category, metadata
                )
                all_metrics.extend(category_metrics)
                
        except Exception as e:
            self.logger.warning(f"Metric collection failed for some categories: {str(e)}")
            
        return all_metrics

    async def _collect_category_metrics(
        self,
        content_path: str,
        content_type: ContentType,
        category: PerformanceCategory,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[PerformanceMetric]:
        """Collect metrics for a specific performance category"""
        
        metrics = []
        
        try:
            if category == PerformanceCategory.PROCESSING_SPEED:
                metrics.extend(await self._collect_processing_speed_metrics(
                    content_path, content_type
                ))
                
            elif category == PerformanceCategory.MEMORY_USAGE:
                metrics.extend(await self._collect_memory_usage_metrics(
                    content_path, content_type
                ))
                
            elif category == PerformanceCategory.STORAGE_EFFICIENCY:
                metrics.extend(await self._collect_storage_efficiency_metrics(
                    content_path, content_type
                ))
                
            elif category == PerformanceCategory.CONTENT_DELIVERY:
                metrics.extend(await self._collect_content_delivery_metrics(
                    content_path, content_type, metadata
                ))
                
            elif category == PerformanceCategory.USER_EXPERIENCE:
                metrics.extend(await self._collect_user_experience_metrics(
                    content_path, content_type, metadata
                ))
                
            elif category == PerformanceCategory.SCALABILITY:
                metrics.extend(await self._collect_scalability_metrics(
                    content_path, content_type
                ))
                
        except Exception as e:
            self.logger.warning(f"Category metric collection failed for {category.value}: {str(e)}")
            
        return metrics

    async def _collect_processing_speed_metrics(
        self,
        content_path: str,
        content_type: ContentType
    ) -> List[PerformanceMetric]:
        """Collect processing speed metrics"""
        
        metrics = []
        
        try:
            # Measure content loading time
            load_start = time.time()
            
            if content_type in [ContentType.AUDIO, ContentType.MUSIC]:
                # Audio loading performance
                try:
                    import librosa
                    y, sr = librosa.load(content_path)
                    load_time = time.time() - load_start
                    
                    metrics.append(PerformanceMetric(
                        metric_id=f"audio_load_time_{uuid.uuid4().hex[:8]}",
                        metric_type=MetricType.LATENCY,
                        category=PerformanceCategory.PROCESSING_SPEED,
                        name="Audio Load Time",
                        value=load_time,
                        unit="seconds",
                        threshold_warning=5.0,
                        threshold_critical=10.0,
                        metadata={"file_size": Path(content_path).stat().st_size, "duration": len(y) / sr}
                    ))
                    
                    # Calculate processing throughput
                    duration = len(y) / sr
                    if load_time > 0:
                        throughput = duration / load_time
                        
                        metrics.append(PerformanceMetric(
                            metric_id=f"audio_throughput_{uuid.uuid4().hex[:8]}",
                            metric_type=MetricType.THROUGHPUT,
                            category=PerformanceCategory.PROCESSING_SPEED,
                            name="Audio Processing Throughput",
                            value=throughput,
                            unit="seconds_audio/second_processing",
                            target_value=10.0,  # 10x real-time
                            metadata={"audio_duration": duration, "processing_time": load_time}
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Audio processing metrics failed: {str(e)}")
                    
            elif content_type == ContentType.IMAGE:
                # Image loading performance
                try:
                    from PIL import Image
                    image = Image.open(content_path)
                    load_time = time.time() - load_start
                    
                    metrics.append(PerformanceMetric(
                        metric_id=f"image_load_time_{uuid.uuid4().hex[:8]}",
                        metric_type=MetricType.LATENCY,
                        category=PerformanceCategory.PROCESSING_SPEED,
                        name="Image Load Time",
                        value=load_time,
                        unit="seconds",
                        threshold_warning=2.0,
                        threshold_critical=5.0,
                        metadata={"image_size": f"{image.width}x{image.height}", "file_size": Path(content_path).stat().st_size}
                    ))
                    
                    # Calculate pixel processing rate
                    total_pixels = image.width * image.height
                    if load_time > 0:
                        pixel_rate = total_pixels / load_time
                        
                        metrics.append(PerformanceMetric(
                            metric_id=f"image_pixel_rate_{uuid.uuid4().hex[:8]}",
                            metric_type=MetricType.THROUGHPUT,
                            category=PerformanceCategory.PROCESSING_SPEED,
                            name="Image Pixel Processing Rate",
                            value=pixel_rate,
                            unit="pixels/second",
                            metadata={"total_pixels": total_pixels, "processing_time": load_time}
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Image processing metrics failed: {str(e)}")
                    
            elif content_type in [ContentType.TEXT, ContentType.BLOG]:
                # Text processing performance
                try:
                    with open(content_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    load_time = time.time() - load_start
                    
                    word_count = len(text.split())
                    
                    metrics.append(PerformanceMetric(
                        metric_id=f"text_load_time_{uuid.uuid4().hex[:8]}",
                        metric_type=MetricType.LATENCY,
                        category=PerformanceCategory.PROCESSING_SPEED,
                        name="Text Load Time",
                        value=load_time,
                        unit="seconds",
                        threshold_warning=1.0,
                        threshold_critical=3.0,
                        metadata={"word_count": word_count, "char_count": len(text)}
                    ))
                    
                    # Calculate text processing rate
                    if load_time > 0:
                        word_rate = word_count / load_time
                        
                        metrics.append(PerformanceMetric(
                            metric_id=f"text_word_rate_{uuid.uuid4().hex[:8]}",
                            metric_type=MetricType.THROUGHPUT,
                            category=PerformanceCategory.PROCESSING_SPEED,
                            name="Text Processing Rate",
                            value=word_rate,
                            unit="words/second",
                            target_value=10000.0,  # 10k words per second
                            metadata={"word_count": word_count, "processing_time": load_time}
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Text processing metrics failed: {str(e)}")
                    
        except Exception as e:
            self.logger.warning(f"Processing speed metrics collection failed: {str(e)}")
            
        return metrics

    async def _collect_memory_usage_metrics(
        self,
        content_path: str,
        content_type: ContentType
    ) -> List[PerformanceMetric]:
        """Collect memory usage metrics"""
        
        metrics = []
        
        try:
            # Get system memory info
            memory_info = psutil.virtual_memory()
            
            # Baseline memory usage
            baseline_memory = memory_info.used
            
            # Load content and measure memory increase
            process = psutil.Process()
            memory_before = process.memory_info().rss
            
            # Simulate content processing
            if content_type in [ContentType.AUDIO, ContentType.MUSIC]:
                try:
                    import librosa
                    y, sr = librosa.load(content_path)
                    memory_after = process.memory_info().rss
                    
                    memory_usage = memory_after - memory_before
                    
                    metrics.append(PerformanceMetric(
                        metric_id=f"audio_memory_usage_{uuid.uuid4().hex[:8]}",
                        metric_type=MetricType.MEMORY_USAGE,
                        category=PerformanceCategory.MEMORY_USAGE,
                        name="Audio Memory Usage",
                        value=memory_usage / (1024 * 1024),  # MB
                        unit="MB",
                        threshold_warning=500.0,  # 500MB
                        threshold_critical=1000.0,  # 1GB
                        metadata={"duration": len(y) / sr, "sample_rate": sr}
                    ))
                    
                    # Calculate memory efficiency (MB per second of audio)
                    duration = len(y) / sr
                    if duration > 0:
                        memory_efficiency = (memory_usage / (1024 * 1024)) / duration
                        
                        metrics.append(PerformanceMetric(
                            metric_id=f"audio_memory_efficiency_{uuid.uuid4().hex[:8]}",
                            metric_type=MetricType.MEMORY_USAGE,
                            category=PerformanceCategory.MEMORY_USAGE,
                            name="Audio Memory Efficiency",
                            value=memory_efficiency,
                            unit="MB/second",
                            target_value=10.0,  # 10MB per second max
                            metadata={"duration": duration, "memory_usage_mb": memory_usage / (1024 * 1024)}
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Audio memory metrics failed: {str(e)}")
                    
            # System memory utilization
            memory_utilization = memory_info.percent
            
            metrics.append(PerformanceMetric(
                metric_id=f"system_memory_util_{uuid.uuid4().hex[:8]}",
                metric_type=MetricType.MEMORY_USAGE,
                category=PerformanceCategory.MEMORY_USAGE,
                name="System Memory Utilization",
                value=memory_utilization,
                unit="percent",
                threshold_warning=80.0,
                threshold_critical=95.0,
                metadata={"total_memory_gb": memory_info.total / (1024**3), "available_gb": memory_info.available / (1024**3)}
            ))
            
        except Exception as e:
            self.logger.warning(f"Memory usage metrics collection failed: {str(e)}")
            
        return metrics

    async def _collect_storage_efficiency_metrics(
        self,
        content_path: str,
        content_type: ContentType
    ) -> List[PerformanceMetric]:
        """Collect storage efficiency metrics"""
        
        metrics = []
        
        try:
            file_path = Path(content_path)
            file_size = file_path.stat().st_size
            
            # File size metric
            metrics.append(PerformanceMetric(
                metric_id=f"file_size_{uuid.uuid4().hex[:8]}",
                metric_type=MetricType.DISK_IO,
                category=PerformanceCategory.STORAGE_EFFICIENCY,
                name="File Size",
                value=file_size / (1024 * 1024),  # MB
                unit="MB",
                metadata={"file_path": str(file_path), "file_extension": file_path.suffix}
            ))
            
            # Compression efficiency (if applicable)
            if content_type in [ContentType.AUDIO, ContentType.MUSIC]:
                try:
                    import librosa
                    y, sr = librosa.load(content_path)
                    duration = len(y) / sr
                    
                    # Calculate bitrate
                    bitrate = (file_size * 8) / duration if duration > 0 else 0
                    
                    metrics.append(PerformanceMetric(
                        metric_id=f"audio_bitrate_{uuid.uuid4().hex[:8]}",
                        metric_type=MetricType.BANDWIDTH,
                        category=PerformanceCategory.STORAGE_EFFICIENCY,
                        name="Audio Bitrate",
                        value=bitrate,
                        unit="bits/second",
                        target_value=256000,  # 256 kbps target
                        metadata={"duration": duration, "file_size_bytes": file_size}
                    ))
                    
                    # Storage efficiency (seconds per MB)
                    if file_size > 0:
                        storage_efficiency = duration / (file_size / (1024 * 1024))
                        
                        metrics.append(PerformanceMetric(
                            metric_id=f"audio_storage_efficiency_{uuid.uuid4().hex[:8]}",
                            metric_type=MetricType.DISK_IO,
                            category=PerformanceCategory.STORAGE_EFFICIENCY,
                            name="Audio Storage Efficiency",
                            value=storage_efficiency,
                            unit="seconds/MB",
                            metadata={"duration": duration, "file_size_mb": file_size / (1024 * 1024)}
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Audio storage metrics failed: {str(e)}")
                    
            elif content_type == ContentType.IMAGE:
                try:
                    from PIL import Image
                    image = Image.open(content_path)
                    
                    total_pixels = image.width * image.height
                    
                    # Bytes per pixel
                    if total_pixels > 0:
                        bytes_per_pixel = file_size / total_pixels
                        
                        metrics.append(PerformanceMetric(
                            metric_id=f"image_bytes_per_pixel_{uuid.uuid4().hex[:8]}",
                            metric_type=MetricType.DISK_IO,
                            category=PerformanceCategory.STORAGE_EFFICIENCY,
                            name="Image Bytes per Pixel",
                            value=bytes_per_pixel,
                            unit="bytes/pixel",
                            target_value=3.0,  # 3 bytes per pixel for RGB
                            metadata={"width": image.width, "height": image.height, "total_pixels": total_pixels}
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Image storage metrics failed: {str(e)}")
                    
            # Disk I/O performance
            disk_usage = psutil.disk_usage(file_path.parent)
            disk_utilization = (disk_usage.used / disk_usage.total) * 100
            
            metrics.append(PerformanceMetric(
                metric_id=f"disk_utilization_{uuid.uuid4().hex[:8]}",
                metric_type=MetricType.DISK_IO,
                category=PerformanceCategory.STORAGE_EFFICIENCY,
                name="Disk Utilization",
                value=disk_utilization,
                unit="percent",
                threshold_warning=80.0,
                threshold_critical=95.0,
                metadata={"total_gb": disk_usage.total / (1024**3), "free_gb": disk_usage.free / (1024**3)}
            ))
            
        except Exception as e:
            self.logger.warning(f"Storage efficiency metrics collection failed: {str(e)}")
            
        return metrics

    async def _collect_user_experience_metrics(
        self,
        content_path: str,
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[PerformanceMetric]:
        """Collect user experience performance metrics"""
        
        metrics = []
        
        try:
            # Content loading time (simulated)
            load_time = await self._simulate_content_load_time(content_path, content_type)
            
            # User perceived performance based on content type
            if content_type in [ContentType.AUDIO, ContentType.MUSIC]:
                # Audio UX metrics
                metrics.append(PerformanceMetric(
                    metric_id=f"audio_load_time_{uuid.uuid4().hex[:8]}",
                    metric_type=MetricType.LATENCY,
                    category=PerformanceCategory.USER_EXPERIENCE,
                    name="Audio Load Time",
                    value=load_time,
                    unit="seconds",
                    threshold_warning=3.0,
                    threshold_critical=8.0,
                    metadata={"content_type": content_type.value}
                ))
                
                # Audio quality impact on UX
                try:
                    import librosa
                    y, sr = librosa.load(content_path)
                    
                    # Estimate perceived quality
                    rms = np.mean(librosa.feature.rms(y=y))
                    quality_score = min(rms * 100, 100)
                    
                    metrics.append(PerformanceMetric(
                        metric_id=f"audio_quality_ux_{uuid.uuid4().hex[:8]}",
                        metric_type=MetricType.THROUGHPUT,
                        category=PerformanceCategory.USER_EXPERIENCE,
                        name="Audio Quality UX Score",
                        value=quality_score,
                        unit="score",
                        target_value=80.0,
                        metadata={"rms_level": rms}
                    ))
                    
                except Exception as e:
                    self.logger.warning(f"Audio UX quality metrics failed: {str(e)}")
                    
            elif content_type == ContentType.IMAGE:
                # Image UX metrics
                metrics.append(PerformanceMetric(
                    metric_id=f"image_load_time_{uuid.uuid4().hex[:8]}",
                    metric_type=MetricType.LATENCY,
                    category=PerformanceCategory.USER_EXPERIENCE,
                    name="Image Load Time",
                    value=load_time,
                    unit="seconds",
                    threshold_warning=2.0,
                    threshold_critical=5.0,
                    metadata={"content_type": content_type.value}
                ))
                
                try:
                    from PIL import Image
                    image = Image.open(content_path)
                    
                    # Image size impact on UX
                    total_pixels = image.width * image.height
                    ux_score = min(total_pixels / 2000000, 1.0) * 100  # 2MP as reference
                    
                    metrics.append(PerformanceMetric(
                        metric_id=f"image_quality_ux_{uuid.uuid4().hex[:8]}",
                        metric_type=MetricType.THROUGHPUT,
                        category=PerformanceCategory.USER_EXPERIENCE,
                        name="Image Quality UX Score",
                        value=ux_score,
                        unit="score",
                        target_value=70.0,
                        metadata={"resolution": f"{image.width}x{image.height}"}
                    ))
                    
                except Exception as e:
                    self.logger.warning(f"Image UX quality metrics failed: {str(e)}")
                    
            elif content_type in [ContentType.TEXT, ContentType.BLOG]:
                # Text UX metrics
                metrics.append(PerformanceMetric(
                    metric_id=f"text_load_time_{uuid.uuid4().hex[:8]}",
                    metric_type=MetricType.LATENCY,
                    category=PerformanceCategory.USER_EXPERIENCE,
                    name="Text Load Time",
                    value=load_time,
                    unit="seconds",
                    threshold_warning=1.0,
                    threshold_critical=3.0,
                    metadata={"content_type": content_type.value}
                ))
                
                try:
                    with open(content_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        
                    # Readability impact on UX
                    word_count = len(text.split())
                    
                    # Simple readability score (words per minute reading)
                    reading_time = word_count / 200  # 200 WPM average
                    ux_score = max(0, 100 - (reading_time - 5) * 2) if reading_time > 5 else 100
                    
                    metrics.append(PerformanceMetric(
                        metric_id=f"text_readability_ux_{uuid.uuid4().hex[:8]}",
                        metric_type=MetricType.THROUGHPUT,
                        category=PerformanceCategory.USER_EXPERIENCE,
                        name="Text Readability UX Score",
                        value=ux_score,
                        unit="score",
                        target_value=75.0,
                        metadata={"word_count": word_count, "estimated_reading_time": reading_time}
                    ))
                    
                except Exception as e:
                    self.logger.warning(f"Text UX readability metrics failed: {str(e)}")
                    
        except Exception as e:
            self.logger.warning(f"User experience metrics collection failed: {str(e)}")
            
        return metrics

    async def _simulate_content_load_time(self, content_path: str, content_type: ContentType) -> float:
        """Simulate content loading time based on file size and type"""



        
        try:
            file_size = Path(content_path).stat().st_size
            
            # Base loading time factors by content type
            base_factors = {
                ContentType.TEXT: 0.001,      # Very fast
                ContentType.IMAGE: 0.01,      # Fast
                ContentType.AUDIO: 0.05,      # Medium
                ContentType.VIDEO: 0.1,       # Slower
                ContentType.MUSIC: 0.05,      # Medium
                ContentType.BLOG: 0.002       # Fast
            }
            
            base_factor = base_factors.get(content_type, 0.05)
            
            # Simulate network and processing delays
            simulated_time = (file_size / (1024 * 1024)) * base_factor + 0.1  # Base 100ms overhead
            
            return min(simulated_time, 30.0)  # Cap at 30 seconds
            
        except Exception:
            return 1.0  # Default 1 second

    async def _calculate_category_scores(
        self,
        metrics: List[PerformanceMetric],
        categories: List[PerformanceCategory]
    ) -> Dict[PerformanceCategory, float]:
        """Calculate performance scores for each category"""
        
        category_scores = {}
        
        for category in categories:
            category_metrics = [m for m in metrics if m.category == category]
            
            if not category_metrics:
                category_scores[category] = 50.0  # Default neutral score
                continue
                
            scores = []
            
            for metric in category_metrics:
                # Calculate metric score based on thresholds and targets
                if metric.threshold_critical and metric.value >= metric.threshold_critical:
                    score = 0.0  # Critical threshold exceeded
                elif metric.threshold_warning and metric.value >= metric.threshold_warning:
                    score = 30.0  # Warning threshold exceeded
                elif metric.target_value:
                    # Score based on how close to target
                    if metric.metric_type in [MetricType.LATENCY]:
                        # Lower is better for latency
                        score = max(0, 100 - (metric.value / metric.target_value) * 50)
                    else:
                        # Higher is better for throughput, etc.
                        score = min(100, (metric.value / metric.target_value) * 100)
                else:
                    score = 70.0  # Default good score
                    
                scores.append(score * metric.confidence)
                
            # Weight average of metric scores
            category_scores[category] = statistics.mean(scores) if scores else 50.0
            
        return category_scores

    async def _calculate_overall_performance_score(
        self,
        category_scores: Dict[PerformanceCategory, float],
        content_type: ContentType
    ) -> float:
        """Calculate weighted overall performance score"""
        
        # Category weights based on content type
        default_weights = {
            PerformanceCategory.PROCESSING_SPEED: 0.25,
            PerformanceCategory.MEMORY_USAGE: 0.15,
            PerformanceCategory.STORAGE_EFFICIENCY: 0.15,
            PerformanceCategory.CONTENT_DELIVERY: 0.20,
            PerformanceCategory.USER_EXPERIENCE: 0.20,
            PerformanceCategory.SCALABILITY: 0.05
        }
        
        # Adjust weights based on content type
        if content_type in [ContentType.AUDIO, ContentType.MUSIC]:
            default_weights[PerformanceCategory.PROCESSING_SPEED] = 0.30
            default_weights[PerformanceCategory.STORAGE_EFFICIENCY] = 0.20
            default_weights[PerformanceCategory.USER_EXPERIENCE] = 0.25
            
        elif content_type == ContentType.IMAGE:
            default_weights[PerformanceCategory.STORAGE_EFFICIENCY] = 0.25
            default_weights[PerformanceCategory.CONTENT_DELIVERY] = 0.25
            default_weights[PerformanceCategory.USER_EXPERIENCE] = 0.25
            
        elif content_type in [ContentType.TEXT, ContentType.BLOG]:
            default_weights[PerformanceCategory.PROCESSING_SPEED] = 0.35
            default_weights[PerformanceCategory.USER_EXPERIENCE] = 0.30
            default_weights[PerformanceCategory.CONTENT_DELIVERY] = 0.20
            
        # Calculate weighted score
        total_weight = 0
        weighted_sum = 0
        
        for category, score in category_scores.items():
            weight = default_weights.get(category, 0.1)
            weighted_sum += score * weight
            total_weight += weight
            
        return weighted_sum / max(total_weight, 1.0) if total_weight > 0 else 50.0

    def _determine_performance_level(self, overall_score: float) -> PerformanceLevel:
        """Determine performance level from overall score"""
        
        if overall_score >= 90:
            return PerformanceLevel.EXCELLENT
        elif overall_score >= 75:
            return PerformanceLevel.GOOD
        elif overall_score >= 60:
            return PerformanceLevel.ACCEPTABLE
        elif overall_score >= 40:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL

    async def _detect_performance_bottlenecks(
        self,
        metrics: List[PerformanceMetric],
        category_scores: Dict[PerformanceCategory, float],
        content_type: ContentType
    ) -> List[PerformanceBottleneck]:
        """Detect performance bottlenecks from metrics"""
        
        bottlenecks = []
        
        try:
            # Check for critical metrics
            for metric in metrics:
                if (metric.threshold_critical and metric.value >= metric.threshold_critical):
                    bottleneck = PerformanceBottleneck(
                        bottleneck_id=f"bottleneck_{uuid.uuid4().hex[:8]}",
                        category=metric.category,
                        severity="critical",
                        title=f"Critical {metric.name}",
                        description=f"{metric.name} ({metric.value:.2f} {metric.unit}) exceeds critical threshold ({metric.threshold_critical:.2f} {metric.unit})",
                        impact_score=95.0,
                        affected_metrics=[metric.metric_id],
                        root_cause=f"High {metric.metric_type.value} in {metric.category.value}",
                        recommendations=[
                            f"Optimize {metric.category.value.replace('_', ' ')} to reduce {metric.name}",
                            f"Target value should be below {metric.threshold_critical:.2f} {metric.unit}",
                            "Consider performance optimization techniques"
                        ],
                        estimated_improvement=30.0,
                        fix_complexity="high",
                        fix_effort="hours",
                        priority_score=100.0,
                        evidence={"metric_value": metric.value, "threshold": metric.threshold_critical}
                    )
                    bottlenecks.append(bottleneck)
                    
            # Check for poor category scores
            for category, score in category_scores.items():
                if score < 40:  # Poor category performance
                    category_metrics = [m for m in metrics if m.category == category]
                    
                    bottleneck = PerformanceBottleneck(
                        bottleneck_id=f"bottleneck_{uuid.uuid4().hex[:8]}",
                        category=category,
                        severity="high",
                        title=f"Poor {category.value.replace('_', ' ').title()} Performance",
                        description=f"{category.value.replace('_', ' ').title()} performance score ({score:.1f}) is significantly below acceptable levels",
                        impact_score=80.0,
                        affected_metrics=[m.metric_id for m in category_metrics],
                        root_cause=f"Multiple performance issues in {category.value.replace('_', ' ')}",
                        recommendations=[
                            f"Review all {category.value.replace('_', ' ')} metrics",
                            "Implement category-specific optimizations",
                            "Monitor performance trends over time"
                        ],
                        estimated_improvement=25.0,
                        fix_complexity="medium",
                        fix_effort="hours",
                        priority_score=score,  # Lower score = higher priority
                        evidence={"category_score": score, "metrics_count": len(category_metrics)}
                    )
                    bottlenecks.append(bottleneck)
                    
            # Sort bottlenecks by priority
            bottlenecks.sort(key=lambda x: x.priority_score, reverse=True)
            
        except Exception as e:
            self.logger.warning(f"Bottleneck detection failed: {str(e)}")
            
        return bottlenecks

    async def _generate_optimization_recommendations(
        self,
        metrics: List[PerformanceMetric],
        bottlenecks: List[PerformanceBottleneck],
        category_scores: Dict[PerformanceCategory, float],
        content_type: ContentType
    ) -> List[OptimizationRecommendation]:
        """Generate performance optimization recommendations"""
        
        recommendations = []
        
        try:
            # Generate recommendations based on bottlenecks
            for bottleneck in bottlenecks:
                if bottleneck.category == PerformanceCategory.PROCESSING_SPEED:
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"opt_rec_{uuid.uuid4().hex[:8]}",
                        category=bottleneck.category,
                        title="Optimize Processing Speed",
                        description="Improve content processing performance through algorithmic and resource optimizations",
                        expected_improvement={"processing_time": -25.0, "throughput": 30.0},
                        implementation_steps=[
                            "Profile current processing pipeline",
                            "Identify computational bottlenecks",
                            "Implement parallel processing where possible",
                            "Optimize algorithms and data structures",
                            "Consider hardware upgrades if needed"
                        ],
                        prerequisites=["Performance profiling tools", "Development environment"],
                        estimated_effort="2-5 days",
                        difficulty_level="medium",
                        roi_score=75.0,
                        risk_level="low",
                        testing_requirements=["Performance benchmarks", "Regression testing"],
                        success_metrics=["Reduced processing time", "Increased throughput"]
                    )
                    recommendations.append(recommendation)
                    
                elif bottleneck.category == PerformanceCategory.MEMORY_USAGE:
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"opt_rec_{uuid.uuid4().hex[:8]}",
                        category=bottleneck.category,
                        title="Optimize Memory Usage",
                        description="Reduce memory consumption and improve memory efficiency",
                        expected_improvement={"memory_usage": -30.0, "memory_efficiency": 25.0},
                        implementation_steps=[
                            "Analyze memory usage patterns",
                            "Implement memory pooling",
                            "Optimize data structures",
                            "Add memory cleanup routines",
                            "Consider streaming for large content"
                        ],
                        prerequisites=["Memory profiling tools", "Understanding of memory management"],
                        estimated_effort="1-3 days",
                        difficulty_level="medium",
                        roi_score=80.0,
                        risk_level="medium",
                        testing_requirements=["Memory leak testing", "Load testing"],
                        success_metrics=["Reduced memory footprint", "Better memory efficiency"]
                    )
                    recommendations.append(recommendation)
                    
                elif bottleneck.category == PerformanceCategory.STORAGE_EFFICIENCY:
                    recommendation = OptimizationRecommendation(
                        recommendation_id=f"opt_rec_{uuid.uuid4().hex[:8]}",
                        category=bottleneck.category,
                        title="Improve Storage Efficiency",
                        description="Optimize file sizes and storage utilization",
                        expected_improvement={"file_size": -20.0, "storage_efficiency": 25.0},
                        implementation_steps=[
                            "Analyze current compression settings",
                            "Implement better compression algorithms",
                            "Optimize file formats",
                            "Add storage cleanup routines",
                            "Consider cloud storage optimization"
                        ],
                        prerequisites=["Storage analysis tools", "Compression libraries"],
                        estimated_effort="1-2 days",
                        difficulty_level="low",
                        roi_score=85.0,
                        risk_level="low",
                        testing_requirements=["File integrity testing", "Compression ratio analysis"],
                        success_metrics=["Reduced file sizes", "Better compression ratios"]
                    )
                    recommendations.append(recommendation)
                    
            # Add general recommendations based on content type
            if content_type in [ContentType.AUDIO, ContentType.MUSIC]:
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"opt_rec_{uuid.uuid4().hex[:8]}",
                    category=PerformanceCategory.PROCESSING_SPEED,
                    title="Audio Processing Optimization",
                    description="Optimize audio processing pipeline for better performance",
                    expected_improvement={"audio_processing_time": -30.0, "audio_quality": 10.0},
                    implementation_steps=[
                        "Implement audio streaming",
                        "Use hardware-accelerated audio processing",
                        "Optimize audio codecs",
                        "Implement audio caching",
                        "Consider parallel audio processing"
                    ],
                    prerequisites=["Audio processing libraries", "Hardware acceleration support"],
                    estimated_effort="3-7 days",
                    difficulty_level="high",
                    roi_score=90.0,
                    risk_level="medium",
                    testing_requirements=["Audio quality testing", "Performance benchmarking"],
                    success_metrics=["Faster audio processing", "Maintained audio quality"]
                ))
                
        except Exception as e:
            self.logger.warning(f"Optimization recommendation generation failed: {str(e)}")
            
        return recommendations

    def _load_performance_baselines(self) -> Dict[str, Dict[str, float]]:
        """Load performance baselines for comparison"""



        
        return {
            "audio": {
                "load_time_baseline": 2.0,  # seconds
                "processing_throughput_baseline": 10.0,  # 10x real-time
                "memory_usage_baseline": 100.0,  # MB
                "storage_efficiency_baseline": 60.0  # seconds per MB
            },
            "video": {
                "load_time_baseline": 5.0,
                "processing_throughput_baseline": 2.0,
                "memory_usage_baseline": 500.0,
                "storage_efficiency_baseline": 10.0
            },
            "image": {
                "load_time_baseline": 1.0,
                "pixel_processing_rate_baseline": 1000000.0,  # 1M pixels/sec
                "memory_usage_baseline": 50.0,
                "bytes_per_pixel_baseline": 3.0
            },
            "text": {
                "load_time_baseline": 0.5,
                "word_processing_rate_baseline": 10000.0,  # 10k words/sec
                "memory_usage_baseline": 10.0,
                "readability_baseline": 75.0
            }
        }

    def _load_performance_thresholds(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Load performance thresholds for different metrics"""



        
        return {
            "audio": {
                "load_time": {"warning": 5.0, "critical": 10.0},
                "memory_usage": {"warning": 500.0, "critical": 1000.0},
                "processing_throughput": {"target": 10.0}
            },
            "video": {
                "load_time": {"warning": 10.0, "critical": 20.0},
                "memory_usage": {"warning": 1000.0, "critical": 2000.0}
            },
            "image": {
                "load_time": {"warning": 2.0, "critical": 5.0},
                "memory_usage": {"warning": 200.0, "critical": 500.0}
            },
            "text": {
                "load_time": {"warning": 1.0, "critical": 3.0},
                "memory_usage": {"warning": 50.0, "critical": 100.0}
            }
        }

    async def _compare_with_benchmarks(
        self,
        content_type: ContentType,
        category_scores: Dict[PerformanceCategory, float],
        overall_score: float,
        metrics: List[PerformanceMetric]
    ) -> Dict[str, Any]:
        """Compare performance with industry benchmarks"""
        
        benchmark_comparison = {
            "content_type": content_type.value,
            "overall_score": overall_score,
            "benchmark_comparisons": {},
            "performance_ranking": "unknown"
        }
        
        try:
            content_baselines = self.performance_baselines.get(content_type.value.lower(), {})
            
            for metric in metrics:
                metric_name = metric.name.lower().replace(" ", "_")
                baseline_key = f"{metric_name}_baseline"
                
                if baseline_key in content_baselines:
                    baseline_value = content_baselines[baseline_key]
                    
                    if metric.metric_type == MetricType.LATENCY:
                        # Lower is better for latency
                        performance_ratio = baseline_value / max(metric.value, 0.001)
                    else:
                        # Higher is better for throughput, efficiency
                        performance_ratio = metric.value / max(baseline_value, 0.001)
                        
                    comparison_status = "exceeds" if performance_ratio > 1.1 else \
                                     "meets" if performance_ratio > 0.9 else "below"
                                     
                    benchmark_comparison["benchmark_comparisons"][metric_name] = {
                        "current_value": metric.value,
                        "baseline_value": baseline_value,
                        "performance_ratio": performance_ratio,
                        "status": comparison_status
                    }
                    
            # Determine overall ranking
            if overall_score >= 90:
                benchmark_comparison["performance_ranking"] = "excellent"
            elif overall_score >= 75:
                benchmark_comparison["performance_ranking"] = "above_average"
            elif overall_score >= 60:
                benchmark_comparison["performance_ranking"] = "average"
            elif overall_score >= 40:
                benchmark_comparison["performance_ranking"] = "below_average"
            else:
                benchmark_comparison["performance_ranking"] = "poor"
                
        except Exception as e:
            self.logger.warning(f"Benchmark comparison failed: {str(e)}")
            
        return benchmark_comparison

    async def _analyze_performance_trends(
        self,
        content_id: str,
        metrics: List[PerformanceMetric],
        category_scores: Dict[PerformanceCategory, float]
    ) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        
        trend_analysis = {
            "content_id": content_id,
            "trend_period": "recent",
            "overall_trend": "stable",
            "category_trends": {},
            "metric_trends": {},
            "significant_changes": []
        }
        
        try:
            # Get historical data if available
            historical_data = self.performance_history.get(content_id, [])
            
            if len(historical_data) >= 2:
                # Analyze trends from historical data
                recent_scores = [entry["overall_score"] for entry in historical_data[-5:]]
                
                if len(recent_scores) >= 3:
                    # Simple trend analysis
                    first_half = recent_scores[:len(recent_scores)//2]
                    second_half = recent_scores[len(recent_scores)//2:]
                    
                    first_avg = statistics.mean(first_half)
                    second_avg = statistics.mean(second_half)
                    
                    if second_avg > first_avg * 1.05:
                        trend_analysis["overall_trend"] = "improving"
                    elif second_avg < first_avg * 0.95:
                        trend_analysis["overall_trend"] = "degrading"
                    else:
                        trend_analysis["overall_trend"] = "stable"
                        
                # Analyze category trends
                for category in category_scores:
                    category_history = []
                    for entry in historical_data[-5:]:
                        if "category_scores" in entry and category.value in entry["category_scores"]:
                            category_history.append(entry["category_scores"][category.value])
                            
                    if len(category_history) >= 2:
                        recent_trend = "stable"
                        if category_history[-1] > category_history[0] * 1.1:
                            recent_trend = "improving"
                        elif category_history[-1] < category_history[0] * 0.9:
                            recent_trend = "degrading"
                            
                        trend_analysis["category_trends"][category.value] = recent_trend
                        
        except Exception as e:
            self.logger.warning(f"Performance trend analysis failed: {str(e)}")
            
        return trend_analysis

    async def _update_performance_history(
        self,
        content_id: str,
        analysis_result: PerformanceAnalysisResult
    ) -> None:
        """Update performance history for trend analysis"""



        
        try:
            if content_id not in self.performance_history:
                self.performance_history[content_id] = []
                
            history_entry = {
                "timestamp": analysis_result.analysis_timestamp.isoformat(),
                "overall_score": analysis_result.overall_performance_score,
                "performance_level": analysis_result.performance_level.value,
                "category_scores": {cat.value: score for cat, score in analysis_result.category_scores.items()},
                "bottleneck_count": len(analysis_result.bottlenecks),
                "processing_time": analysis_result.processing_time
            }
            
            self.performance_history[content_id].append(history_entry)
            
            # Keep only last 100 entries per content
            if len(self.performance_history[content_id]) > 100:
                self.performance_history[content_id] = self.performance_history[content_id][-100:]
                
        except Exception as e:
            self.logger.warning(f"Performance history update failed: {str(e)}")

class MetricsCalculator:
    """
    Specialized metrics calculator for performance analysis.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def calculate_performance_metrics(
        self,
        content_path: str,
        content_type: ContentType,
        operation: str = "load"
    ) -> Dict[str, float]:
        """Calculate basic performance metrics for content"""



        
        try:
            metrics = {}
            
            # Time the operation
            start_time = time.time()
            
            if operation == "load":
                # Measure loading performance
                if content_type in [ContentType.AUDIO, ContentType.MUSIC]:
                    try:
                        import librosa
                        y, sr = librosa.load(content_path)
                        metrics["duration"] = len(y) / sr
                    except Exception as e:
                        self.logger.warning(f"Audio loading failed: {str(e)}")
                        
                elif content_type == ContentType.IMAGE:
                    try:
                        from PIL import Image
                        image = Image.open(content_path)
                        metrics["resolution"] = image.width * image.height
                    except Exception as e:
                        self.logger.warning(f"Image loading failed: {str(e)}")
                        
                elif content_type in [ContentType.TEXT, ContentType.BLOG]:
                    try:
                        with open(content_path, 'r', encoding='utf-8') as f:
                            text = f.read()
                        metrics["word_count"] = len(text.split())
                    except Exception as e:
                        self.logger.warning(f"Text loading failed: {str(e)}")
                        
            load_time = time.time() - start_time
            
            # Basic metrics
            metrics.update({
                "load_time": load_time,
                "file_size": Path(content_path).stat().st_size,
                "load_speed": Path(content_path).stat().st_size / max(load_time, 0.001)  # bytes/sec
            })
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Metrics calculation failed: {str(e)}")
            return {"error": str(e)}

    async def calculate_efficiency_score(
        self,
        metrics: Dict[str, float],
        content_type: ContentType
    ) -> float:
        """Calculate efficiency score from metrics"""



        
        try:
            efficiency_factors = []
            
            # File size efficiency
            if "file_size" in metrics:
                file_size_mb = metrics["file_size"] / (1024 * 1024)
                
                if content_type in [ContentType.AUDIO, ContentType.MUSIC] and "duration" in metrics:
                    # MB per minute
                    efficiency = metrics["duration"] / 60 / max(file_size_mb, 0.001)
                    efficiency_factors.append(min(efficiency / 2, 1.0) * 100)  # 2 min/MB is good
                    
                elif content_type == ContentType.IMAGE and "resolution" in metrics:
                    # Pixels per MB
                    efficiency = metrics["resolution"] / max(file_size_mb, 0.001)
                    efficiency_factors.append(min(efficiency / 1000000, 1.0) * 100)  # 1M pixels/MB is good
                    
            # Loading speed efficiency
            if "load_time" in metrics and "file_size" in metrics:
                load_speed_mbps = (metrics["file_size"] / (1024 * 1024)) / max(metrics["load_time"], 0.001)
                efficiency_factors.append(min(load_speed_mbps / 10, 1.0) * 100)  # 10 MB/s is good
                
            return statistics.mean(efficiency_factors) if efficiency_factors else 50.0
            
        except Exception as e:
            self.logger.error(f"Efficiency score calculation failed: {str(e)}")
            return 0.0
