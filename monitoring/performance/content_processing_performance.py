"""
⚠️ CONFIDENTIEL - IA Chérie Creator Platform ⚠️

Content Processing Performance Monitor - Enterprise Performance Monitoring
Advanced performance monitoring for AI content processing and multimedia workflows

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import time
import asyncio
import os
import psutil
import threading
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import json
import statistics
from prometheus_client import Gauge, Counter, Histogram, Summary
import torch
import numpy as np
from PIL import Image
import cv2
import librosa
import subprocess
import tempfile
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ContentProcessingMetrics:
    """Content processing performance metrics"""
    process_id: str
    content_type: str  # image, video, audio, text, document
    file_size_bytes: int
    processing_stage: str  # upload, validation, conversion, ai_analysis, protection
    start_time: datetime
    end_time: datetime
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    cpu_usage_percent: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    gpu_usage_percent: Optional[float] = None
    gpu_memory_mb: Optional[float] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    quality_score: Optional[float] = None
    creator_id: Optional[str] = None

@dataclass
class MLInferenceMetrics:
    """ML model inference performance metrics"""
    model_name: str
    model_version: str
    inference_type: str  # classification, detection, generation, embedding
    input_shape: Tuple[int, ...]
    batch_size: int
    inference_time_ms: float
    preprocessing_time_ms: float
    postprocessing_time_ms: float
    total_time_ms: float
    gpu_utilized: bool
    memory_usage_mb: float
    confidence_score: Optional[float] = None
    timestamp: datetime = None

@dataclass
class MediaConversionMetrics:
    """Media conversion performance metrics"""
    conversion_id: str
    source_format: str
    target_format: str
    source_size_bytes: int
    target_size_bytes: int
    source_resolution: Optional[Tuple[int, int]] = None
    target_resolution: Optional[Tuple[int, int]] = None
    bitrate_kbps: Optional[int] = None
    fps: Optional[float] = None
    duration_seconds: Optional[float] = None
    conversion_time_ms: float
    compression_ratio: float
    quality_loss_percent: float
    timestamp: datetime = None

@dataclass
class ContentQualityMetrics:
    """Content quality assessment metrics"""
    content_id: str
    content_type: str
    quality_score: float  # 0-100
    resolution_score: float
    clarity_score: float
    noise_level: float
    artifact_count: int
    recommendations: List[str]
    assessment_time_ms: float
    timestamp: datetime

class ContentProcessingPerformance:
    """
    Enterprise-grade content processing performance monitor
    Tracks AI model inference, media conversion, and quality assessment performance
    """
    
    def __init__(self,
                 gpu_monitoring: bool = True,
                 quality_assessment: bool = True,
                 detailed_profiling: bool = True):
        """
        Initialize content processing performance monitor
        
        Args:
            gpu_monitoring: Enable GPU monitoring if available
            quality_assessment: Enable content quality assessment
            detailed_profiling: Enable detailed performance profiling
        """
        self.gpu_monitoring = gpu_monitoring
        self.quality_assessment = quality_assessment
        self.detailed_profiling = detailed_profiling
        
        # GPU availability check
        self.gpu_available = torch.cuda.is_available() if gpu_monitoring else False
        self.gpu_count = torch.cuda.device_count() if self.gpu_available else 0
        
        # Metrics storage
        self.processing_metrics: deque = deque(maxlen=10000)
        self.ml_metrics: deque = deque(maxlen=10000)
        self.conversion_metrics: deque = deque(maxlen=5000)
        self.quality_metrics: deque = deque(maxlen=5000)
        
        # Performance tracking
        self.active_processes: Dict[str, Dict] = {}
        self.model_performance: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.processing_queue_size: Dict[str, int] = defaultdict(int)
        
        # Resource usage tracking
        self.resource_usage_history: deque = deque(maxlen=1000)
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        # Monitoring state
        self.monitoring_active = False
        self._monitoring_task = None
        
        # Supported formats
        self.supported_formats = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf']
        }
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.processing_duration_histogram = Histogram(
            'content_processing_duration_seconds',
            'Content processing duration',
            ['content_type', 'stage', 'success'],
            buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0]
        )
        
        self.ml_inference_histogram = Histogram(
            'ml_inference_duration_seconds',
            'ML model inference duration',
            ['model_name', 'inference_type', 'gpu_used'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
        )
        
        self.media_conversion_histogram = Histogram(
            'media_conversion_duration_seconds',
            'Media conversion duration',
            ['source_format', 'target_format'],
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
        )
        
        self.content_quality_gauge = Gauge(
            'content_quality_score',
            'Content quality score',
            ['content_type']
        )
        
        self.gpu_utilization_gauge = Gauge(
            'gpu_utilization_percent',
            'GPU utilization percentage',
            ['gpu_id']
        )
        
        self.gpu_memory_gauge = Gauge(
            'gpu_memory_usage_mb',
            'GPU memory usage in MB',
            ['gpu_id']
        )
        
        self.processing_queue_gauge = Gauge(
            'content_processing_queue_size',
            'Content processing queue size',
            ['content_type']
        )
        
        self.file_size_histogram = Histogram(
            'content_file_size_bytes',
            'Content file size distribution',
            ['content_type'],
            buckets=[1024, 10240, 102400, 1048576, 10485760, 104857600, 1073741824]  # 1KB to 1GB
        )
    
    def start_content_processing(self, 
                               content_type: str,
                               file_size: int,
                               processing_stage: str,
                               creator_id: Optional[str] = None) -> str:
        """Start tracking content processing"""
        process_id = self._generate_process_id()
        
        self.active_processes[process_id] = {
            'content_type': content_type,
            'file_size': file_size,
            'stage': processing_stage,
            'start_time': datetime.utcnow(),
            'creator_id': creator_id,
            'cpu_start': psutil.cpu_percent(),
            'memory_start': psutil.virtual_memory().used / (1024 * 1024)
        }
        
        # Update queue size
        self.processing_queue_size[content_type] += 1
        self.processing_queue_gauge.labels(content_type=content_type).set(
            self.processing_queue_size[content_type]
        )
        
        # Record file size
        self.file_size_histogram.labels(content_type=content_type).observe(file_size)
        
        logger.info(f"Started processing {content_type} content: {process_id}")
        return process_id
    
    def end_content_processing(self,
                             process_id: str,
                             success: bool = True,
                             error_message: Optional[str] = None,
                             quality_score: Optional[float] = None) -> ContentProcessingMetrics:
        """End tracking content processing"""
        if process_id not in self.active_processes:
            logger.warning(f"Process ID not found: {process_id}")
            return None
        
        process_data = self.active_processes[process_id]
        end_time = datetime.utcnow()
        duration_ms = (end_time - process_data['start_time']).total_seconds() * 1000
        
        # Get current resource usage
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)
        
        # GPU metrics if available
        gpu_usage = None
        gpu_memory = None
        if self.gpu_available:
            gpu_usage, gpu_memory = self._get_gpu_metrics()
        
        metrics = ContentProcessingMetrics(
            process_id=process_id,
            content_type=process_data['content_type'],
            file_size_bytes=process_data['file_size'],
            processing_stage=process_data['stage'],
            start_time=process_data['start_time'],
            end_time=end_time,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
            cpu_usage_percent=cpu_usage,
            memory_usage_mb=memory_usage - process_data['memory_start'],
            gpu_usage_percent=gpu_usage,
            gpu_memory_mb=gpu_memory,
            quality_score=quality_score,
            creator_id=process_data['creator_id']
        )
        
        # Store metrics
        self.processing_metrics.append(metrics)
        
        # Update Prometheus metrics
        self.processing_duration_histogram.labels(
            content_type=process_data['content_type'],
            stage=process_data['stage'],
            success=str(success)
        ).observe(duration_ms / 1000)
        
        # Update queue size
        self.processing_queue_size[process_data['content_type']] -= 1
        self.processing_queue_gauge.labels(content_type=process_data['content_type']).set(
            self.processing_queue_size[process_data['content_type']]
        )
        
        # Clean up
        del self.active_processes[process_id]
        
        logger.info(f"Completed processing {process_data['content_type']}: {duration_ms:.1f}ms")
        return metrics
    
    def track_ml_inference(self,
                          model_name: str,
                          model_version: str,
                          inference_type: str,
                          input_shape: Tuple[int, ...],
                          batch_size: int = 1) -> 'MLInferenceTracker':
        """Context manager for tracking ML inference"""
        return MLInferenceTracker(self, model_name, model_version, inference_type, input_shape, batch_size)
    
    def record_ml_inference_metrics(self, metrics: MLInferenceMetrics):
        """Record ML inference metrics"""
        self.ml_metrics.append(metrics)
        
        # Store in model-specific history
        model_key = f"{metrics.model_name}:{metrics.model_version}"
        self.model_performance[model_key].append(metrics)
        
        # Update Prometheus metrics
        self.ml_inference_histogram.labels(
            model_name=metrics.model_name,
            inference_type=metrics.inference_type,
            gpu_used=str(metrics.gpu_utilized)
        ).observe(metrics.inference_time_ms / 1000)
    
    def track_media_conversion(self,
                             source_format: str,
                             target_format: str,
                             source_size: int) -> 'MediaConversionTracker':
        """Context manager for tracking media conversion"""
        return MediaConversionTracker(self, source_format, target_format, source_size)
    
    def record_media_conversion_metrics(self, metrics: MediaConversionMetrics):
        """Record media conversion metrics"""
        self.conversion_metrics.append(metrics)
        
        # Update Prometheus metrics
        self.media_conversion_histogram.labels(
            source_format=metrics.source_format,
            target_format=metrics.target_format
        ).observe(metrics.conversion_time_ms / 1000)
    
    def assess_content_quality(self, content_path: str, content_type: str) -> ContentQualityMetrics:
        """Assess content quality"""
        start_time = time.time()
        content_id = hashlib.md5(content_path.encode()).hexdigest()[:12]
        
        quality_score = 0.0
        resolution_score = 0.0
        clarity_score = 0.0
        noise_level = 0.0
        artifact_count = 0
        recommendations = []
        
        try:
            if content_type == 'image':
                quality_score, resolution_score, clarity_score, noise_level, artifact_count, recommendations = \
                    self._assess_image_quality(content_path)
            elif content_type == 'video':
                quality_score, resolution_score, clarity_score, noise_level, artifact_count, recommendations = \
                    self._assess_video_quality(content_path)
            elif content_type == 'audio':
                quality_score, resolution_score, clarity_score, noise_level, artifact_count, recommendations = \
                    self._assess_audio_quality(content_path)
            
        except Exception as e:
            logger.error(f"Error assessing content quality: {e}")
            quality_score = 50.0  # Default neutral score
            recommendations = ["Quality assessment failed"]
        
        assessment_time_ms = (time.time() - start_time) * 1000
        
        metrics = ContentQualityMetrics(
            content_id=content_id,
            content_type=content_type,
            quality_score=quality_score,
            resolution_score=resolution_score,
            clarity_score=clarity_score,
            noise_level=noise_level,
            artifact_count=artifact_count,
            recommendations=recommendations,
            assessment_time_ms=assessment_time_ms,
            timestamp=datetime.utcnow()
        )
        
        self.quality_metrics.append(metrics)
        
        # Update Prometheus metrics
        self.content_quality_gauge.labels(content_type=content_type).set(quality_score)
        
        return metrics
    
    def _assess_image_quality(self, image_path: str) -> Tuple[float, float, float, float, int, List[str]]:
        """Assess image quality"""
        recommendations = []
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return 0.0, 0.0, 0.0, 100.0, 0, ["Failed to load image"]
        
        height, width = image.shape[:2]
        
        # Resolution score
        pixel_count = height * width
        if pixel_count >= 1920 * 1080:  # Full HD or higher
            resolution_score = 100.0
        elif pixel_count >= 1280 * 720:  # HD
            resolution_score = 80.0
        elif pixel_count >= 640 * 480:  # SD
            resolution_score = 60.0
        else:
            resolution_score = 40.0
            recommendations.append("Consider higher resolution")
        
        # Clarity score (using Laplacian variance)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        clarity_score = min(100.0, laplacian_var / 10.0)  # Normalize
        
        if clarity_score < 50:
            recommendations.append("Image appears blurry")
        
        # Noise level (standard deviation of pixel values)
        noise_level = np.std(gray)
        
        if noise_level > 50:
            recommendations.append("High noise level detected")
        
        # Artifact detection (simplified)
        artifact_count = 0
        # Check for compression artifacts using DCT
        try:
            # Simple compression artifact detection
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Count small, square-like contours (potential compression artifacts)
            for contour in contours:
                area = cv2.contourArea(contour)
                if 10 < area < 100:  # Small artifacts
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.8 < aspect_ratio < 1.2:  # Square-like
                        artifact_count += 1
        except:
            pass
        
        if artifact_count > 50:
            recommendations.append("Compression artifacts detected")
        
        # Overall quality score
        quality_score = (resolution_score * 0.3 + clarity_score * 0.4 + 
                        (100 - min(100, noise_level)) * 0.2 + 
                        (100 - min(100, artifact_count)) * 0.1)
        
        return quality_score, resolution_score, clarity_score, noise_level, artifact_count, recommendations
    
    def _assess_video_quality(self, video_path: str) -> Tuple[float, float, float, float, int, List[str]]:
        """Assess video quality"""
        recommendations = []
        
        try:
            # Use OpenCV to analyze video
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return 0.0, 0.0, 0.0, 100.0, 0, ["Failed to load video"]
            
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Resolution score
            pixel_count = width * height
            if pixel_count >= 1920 * 1080:
                resolution_score = 100.0
            elif pixel_count >= 1280 * 720:
                resolution_score = 80.0
            else:
                resolution_score = 60.0
                recommendations.append("Consider higher resolution")
            
            # Frame rate assessment
            if fps < 24:
                recommendations.append("Low frame rate detected")
            elif fps > 60:
                recommendations.append("Very high frame rate may be unnecessary")
            
            # Sample frames for quality analysis
            sample_frames = min(10, frame_count // 10)  # Sample 10 frames or every 10th frame
            clarity_scores = []
            noise_levels = []
            
            for i in range(sample_frames):
                frame_idx = i * (frame_count // sample_frames)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Clarity (Laplacian variance)
                    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                    clarity_scores.append(min(100.0, laplacian_var / 10.0))
                    
                    # Noise level
                    noise_levels.append(np.std(gray))
            
            cap.release()
            
            # Average metrics
            clarity_score = np.mean(clarity_scores) if clarity_scores else 50.0
            noise_level = np.mean(noise_levels) if noise_levels else 0.0
            
            if clarity_score < 50:
                recommendations.append("Video appears blurry")
            
            if noise_level > 50:
                recommendations.append("High noise level in video")
            
            # Artifact count (simplified)
            artifact_count = max(0, int((100 - clarity_score) / 10))
            
            # Overall quality score
            quality_score = (resolution_score * 0.4 + clarity_score * 0.4 + 
                           (100 - min(100, noise_level)) * 0.2)
            
            return quality_score, resolution_score, clarity_score, noise_level, artifact_count, recommendations
            
        except Exception as e:
            logger.error(f"Error assessing video quality: {e}")
            return 50.0, 50.0, 50.0, 50.0, 0, ["Video quality assessment failed"]
    
    def _assess_audio_quality(self, audio_path: str) -> Tuple[float, float, float, float, int, List[str]]:
        """Assess audio quality"""
        recommendations = []
        
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=None)
            
            # Sample rate score
            if sr >= 44100:
                resolution_score = 100.0
            elif sr >= 22050:
                resolution_score = 80.0
            else:
                resolution_score = 60.0
                recommendations.append("Consider higher sample rate")
            
            # Dynamic range (clarity proxy)
            dynamic_range = np.max(y) - np.min(y)
            clarity_score = min(100.0, dynamic_range * 100)
            
            if clarity_score < 50:
                recommendations.append("Low dynamic range detected")
            
            # Noise level (RMS of signal)
            rms = np.sqrt(np.mean(y**2))
            noise_level = rms * 100
            
            if noise_level > 50:
                recommendations.append("High noise level in audio")
            
            # Clipping detection
            clipping_threshold = 0.95
            clipped_samples = np.sum(np.abs(y) > clipping_threshold)
            artifact_count = clipped_samples
            
            if artifact_count > len(y) * 0.01:  # More than 1% clipped
                recommendations.append("Audio clipping detected")
            
            # Overall quality score
            quality_score = (resolution_score * 0.3 + clarity_score * 0.4 + 
                           (100 - min(100, noise_level)) * 0.2 + 
                           (100 - min(100, artifact_count / len(y) * 1000)) * 0.1)
            
            return quality_score, resolution_score, clarity_score, noise_level, artifact_count, recommendations
            
        except Exception as e:
            logger.error(f"Error assessing audio quality: {e}")
            return 50.0, 50.0, 50.0, 50.0, 0, ["Audio quality assessment failed"]
    
    def _get_gpu_metrics(self) -> Tuple[Optional[float], Optional[float]]:
        """Get GPU utilization and memory usage"""
        if not self.gpu_available:
            return None, None
        
        try:
            # Use nvidia-ml-py if available, otherwise fall back to nvidia-smi
            import pynvml
            pynvml.nvmlInit()
            
            # Get first GPU metrics
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            
            # GPU utilization
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpu_usage = utilization.gpu
            
            # Memory usage
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_memory = memory_info.used / (1024 * 1024)  # Convert to MB
            
            # Update Prometheus metrics
            self.gpu_utilization_gauge.labels(gpu_id='0').set(gpu_usage)
            self.gpu_memory_gauge.labels(gpu_id='0').set(gpu_memory)
            
            return gpu_usage, gpu_memory
            
        except ImportError:
            # Fall back to nvidia-smi
            try:
                result = subprocess.run([
                    'nvidia-smi', '--query-gpu=utilization.gpu,memory.used',
                    '--format=csv,noheader,nounits'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    gpu_usage, memory_used = result.stdout.strip().split(', ')
                    return float(gpu_usage), float(memory_used)
            except:
                pass
        except:
            pass
        
        return None, None
    
    def _generate_process_id(self) -> str:
        """Generate unique process ID"""
        import uuid
        return str(uuid.uuid4())[:12]
    
    def get_processing_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get processing performance summary"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [m for m in self.processing_metrics if m.start_time >= cutoff_time]
        
        if not recent_metrics:
            return {'message': 'No processing data available'}
        
        # Group by content type
        by_type = defaultdict(list)
        for metric in recent_metrics:
            by_type[metric.content_type].append(metric)
        
        summary = {
            'time_period_hours': hours,
            'total_processed': len(recent_metrics),
            'success_rate': len([m for m in recent_metrics if m.success]) / len(recent_metrics) * 100,
            'by_content_type': {}
        }
        
        for content_type, metrics_list in by_type.items():
            durations = [m.duration_ms for m in metrics_list]
            sizes = [m.file_size_bytes for m in metrics_list]
            
            summary['by_content_type'][content_type] = {
                'count': len(metrics_list),
                'avg_duration_ms': statistics.mean(durations),
                'p95_duration_ms': statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else max(durations),
                'avg_file_size_mb': statistics.mean(sizes) / (1024 * 1024),
                'success_rate': len([m for m in metrics_list if m.success]) / len(metrics_list) * 100
            }
        
        return summary
    
    def get_ml_model_performance(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get ML model performance analysis"""
        if model_name:
            model_metrics = [m for m in self.ml_metrics if m.model_name == model_name]
        else:
            model_metrics = list(self.ml_metrics)
        
        if not model_metrics:
            return {'message': 'No ML metrics available'}
        
        # Group by model
        by_model = defaultdict(list)
        for metric in model_metrics:
            model_key = f"{metric.model_name}:{metric.model_version}"
            by_model[model_key].append(metric)
        
        analysis = {}
        
        for model_key, metrics_list in by_model.items():
            inference_times = [m.inference_time_ms for m in metrics_list]
            total_times = [m.total_time_ms for m in metrics_list]
            gpu_used = [m.gpu_utilized for m in metrics_list]
            
            analysis[model_key] = {
                'inference_count': len(metrics_list),
                'avg_inference_time_ms': statistics.mean(inference_times),
                'p95_inference_time_ms': statistics.quantiles(inference_times, n=20)[18] if len(inference_times) >= 20 else max(inference_times),
                'avg_total_time_ms': statistics.mean(total_times),
                'gpu_utilization_rate': sum(gpu_used) / len(gpu_used) * 100,
                'inference_types': list(set(m.inference_type for m in metrics_list))
            }
        
        return analysis


class MLInferenceTracker:
    """Context manager for tracking ML inference performance"""
    
    def __init__(self, monitor: ContentProcessingPerformance, model_name: str, 
                 model_version: str, inference_type: str, input_shape: Tuple[int, ...], batch_size: int):
        self.monitor = monitor
        self.model_name = model_name
        self.model_version = model_version
        self.inference_type = inference_type
        self.input_shape = input_shape
        self.batch_size = batch_size
        
        self.start_time = None
        self.preprocessing_start = None
        self.inference_start = None
        self.postprocessing_start = None
        self.end_time = None
        
        self.preprocessing_time_ms = 0.0
        self.inference_time_ms = 0.0
        self.postprocessing_time_ms = 0.0
        
        self.gpu_utilized = False
        self.memory_usage_mb = 0.0
        self.confidence_score = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.preprocessing_start = self.start_time
        
        # Check if GPU is being used
        if torch.cuda.is_available():
            torch.cuda.synchronize()  # Ensure accurate timing
            self.gpu_utilized = torch.cuda.is_available()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        
        # Calculate total time if not already done
        if self.postprocessing_start is None:
            self.postprocessing_start = self.end_time
        
        total_time_ms = (self.end_time - self.start_time) * 1000
        
        # Get memory usage
        if self.gpu_utilized and torch.cuda.is_available():
            self.memory_usage_mb = torch.cuda.memory_allocated() / (1024 * 1024)
        else:
            process = psutil.Process()
            self.memory_usage_mb = process.memory_info().rss / (1024 * 1024)
        
        # Create metrics
        metrics = MLInferenceMetrics(
            model_name=self.model_name,
            model_version=self.model_version,
            inference_type=self.inference_type,
            input_shape=self.input_shape,
            batch_size=self.batch_size,
            inference_time_ms=self.inference_time_ms,
            preprocessing_time_ms=self.preprocessing_time_ms,
            postprocessing_time_ms=self.postprocessing_time_ms,
            total_time_ms=total_time_ms,
            gpu_utilized=self.gpu_utilized,
            memory_usage_mb=self.memory_usage_mb,
            confidence_score=self.confidence_score,
            timestamp=datetime.utcnow()
        )
        
        self.monitor.record_ml_inference_metrics(metrics)
    
    def start_inference(self):
        """Mark start of inference phase"""
        if self.preprocessing_start:
            self.preprocessing_time_ms = (time.time() - self.preprocessing_start) * 1000
        self.inference_start = time.time()
    
    def start_postprocessing(self):
        """Mark start of postprocessing phase"""
        if self.inference_start:
            self.inference_time_ms = (time.time() - self.inference_start) * 1000
        self.postprocessing_start = time.time()
    
    def set_confidence_score(self, score: float):
        """Set confidence score for inference result"""
        self.confidence_score = score


class MediaConversionTracker:
    """Context manager for tracking media conversion performance"""
    
    def __init__(self, monitor: ContentProcessingPerformance, source_format: str, 
                 target_format: str, source_size: int):
        self.monitor = monitor
        self.source_format = source_format
        self.target_format = target_format
        self.source_size = source_size
        
        self.start_time = None
        self.end_time = None
        self.target_size = 0
        self.source_resolution = None
        self.target_resolution = None
        self.bitrate_kbps = None
        self.fps = None
        self.duration_seconds = None
        self.quality_loss_percent = 0.0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        conversion_time_ms = (self.end_time - self.start_time) * 1000
        
        # Calculate compression ratio
        compression_ratio = self.source_size / self.target_size if self.target_size > 0 else 1.0
        
        # Generate conversion ID
        conversion_id = hashlib.md5(f"{self.source_format}{self.target_format}{self.start_time}".encode()).hexdigest()[:12]
        
        metrics = MediaConversionMetrics(
            conversion_id=conversion_id,
            source_format=self.source_format,
            target_format=self.target_format,
            source_size_bytes=self.source_size,
            target_size_bytes=self.target_size,
            source_resolution=self.source_resolution,
            target_resolution=self.target_resolution,
            bitrate_kbps=self.bitrate_kbps,
            fps=self.fps,
            duration_seconds=self.duration_seconds,
            conversion_time_ms=conversion_time_ms,
            compression_ratio=compression_ratio,
            quality_loss_percent=self.quality_loss_percent,
            timestamp=datetime.utcnow()
        )
        
        self.monitor.record_media_conversion_metrics(metrics)
    
    def set_output_info(self, target_size: int, target_resolution: Optional[Tuple[int, int]] = None):
        """Set output file information"""
        self.target_size = target_size
        self.target_resolution = target_resolution
    
    def set_media_properties(self, bitrate_kbps: Optional[int] = None, fps: Optional[float] = None, 
                           duration_seconds: Optional[float] = None):
        """Set media properties"""
        self.bitrate_kbps = bitrate_kbps
        self.fps = fps
        self.duration_seconds = duration_seconds
    
    def set_quality_loss(self, quality_loss_percent: float):
        """Set quality loss percentage"""
        self.quality_loss_percent = quality_loss_percent