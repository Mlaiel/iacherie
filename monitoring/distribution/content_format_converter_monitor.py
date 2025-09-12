"""
Content Format Converter Monitor - Distribution Module
====================================================

Advanced monitoring system for content format conversion processes across
multiple platforms with real-time tracking, optimization, and quality control.

Features:
- Real-time format conversion monitoring
- Quality assessment and validation
- Performance optimization tracking
- Multi-platform format compatibility
- Error handling and retry mechanisms
- Conversion pipeline analytics

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

class ConversionStatus(Enum):
    """Content conversion status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class ContentFormat(Enum):
    """Supported content formats"""
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WMV = "wmv"
    WEBM = "webm"
    
    # Image formats
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    SVG = "svg"

class ConversionPriority(Enum):
    """Conversion priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

@dataclass
class ConversionRequest:
    """Content conversion request"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    source_format: ContentFormat = ContentFormat.MP3
    target_formats: List[ContentFormat] = field(default_factory=list)
    priority: ConversionPriority = ConversionPriority.NORMAL
    quality_settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    platform_requirements: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None

@dataclass
class ConversionJob:
    """Active conversion job tracking"""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request: ConversionRequest = field(default_factory=ConversionRequest)
    status: ConversionStatus = ConversionStatus.QUEUED
    current_format: Optional[ContentFormat] = None
    progress_percentage: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    estimated_completion: Optional[datetime] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)

@dataclass
class ConversionResult:
    """Conversion process result"""
    job_id: str = ""
    request_id: str = ""
    source_format: ContentFormat = ContentFormat.MP3
    target_format: ContentFormat = ContentFormat.MP3
    status: ConversionStatus = ConversionStatus.COMPLETED
    output_file_path: Optional[str] = None
    file_size_bytes: int = 0
    conversion_time_seconds: float = 0.0
    quality_score: float = 0.0
    compression_ratio: float = 0.0
    metadata_preserved: bool = True
    error_details: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class QualityMetrics:
    """Content quality assessment metrics"""
    overall_score: float = 0.0
    audio_quality: Optional[float] = None
    video_quality: Optional[float] = None
    image_quality: Optional[float] = None
    bitrate_quality: float = 0.0
    resolution_quality: float = 0.0
    metadata_integrity: float = 0.0
    compression_efficiency: float = 0.0
    platform_compatibility: Dict[str, float] = field(default_factory=dict)

class ContentFormatConverterMonitor:
    """Main content format converter monitoring system"""
    
    def __init__(self):
        self.active_jobs: Dict[str, ConversionJob] = {}
        self.completed_jobs: List[ConversionJob] = []
        self.conversion_queue: List[ConversionRequest] = []
        self.conversion_history: List[ConversionResult] = []
        self.performance_metrics: Dict[str, Any] = {}
        self.quality_thresholds = {
            'minimum_quality_score': 0.8,
            'maximum_conversion_time': 300,  # 5 minutes
            'maximum_file_size_mb': 500
        }
        self.platform_specifications = self._initialize_platform_specs()
        
    def _initialize_platform_specs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific format requirements"""
        return {
            'youtube': {
                'video': {
                    'formats': [ContentFormat.MP4, ContentFormat.WEBM],
                    'max_resolution': '4K',
                    'max_bitrate': '68Mbps',
                    'codecs': ['H.264', 'VP9']
                },
                'audio': {
                    'formats': [ContentFormat.AAC, ContentFormat.MP3],
                    'max_bitrate': '320kbps',
                    'sample_rate': '48kHz'
                }
            },
            'spotify': {
                'audio': {
                    'formats': [ContentFormat.OGG, ContentFormat.AAC],
                    'bitrate': '320kbps',
                    'sample_rate': '44.1kHz'
                }
            },
            'instagram': {
                'video': {
                    'formats': [ContentFormat.MP4],
                    'max_duration': 60,
                    'aspect_ratios': ['1:1', '9:16', '16:9']
                },
                'image': {
                    'formats': [ContentFormat.JPEG, ContentFormat.PNG],
                    'max_resolution': '1080x1080'
                }
            },
            'tiktok': {
                'video': {
                    'formats': [ContentFormat.MP4],
                    'aspect_ratio': '9:16',
                    'max_duration': 180
                }
            }
        }
        
    async def submit_conversion_request(self, request: ConversionRequest) -> str:
        """Submit a new conversion request"""
        # Validate request
        if not self._validate_conversion_request(request):
            raise ValueError("Invalid conversion request")
            
        # Create conversion job
        job = ConversionJob(request=request)
        self.active_jobs[job.job_id] = job
        
        # Add to queue based on priority
        self._add_to_queue(request)
        
        logger.info(f"Conversion request submitted: {request.request_id}")
        return job.job_id
        
    def _validate_conversion_request(self, request: ConversionRequest) -> bool:
        """Validate conversion request parameters"""
        if not request.content_id:
            return False
            
        if not request.target_formats:
            return False
            
        # Check if target formats are supported
        for target_format in request.target_formats:
            if not self._is_conversion_supported(request.source_format, target_format):
                return False
                
        return True
        
    def _is_conversion_supported(self, source: ContentFormat, target: ContentFormat) -> bool:
        """Check if format conversion is supported"""
        # Audio to audio conversions
        audio_formats = {ContentFormat.MP3, ContentFormat.WAV, ContentFormat.FLAC, 
                        ContentFormat.AAC, ContentFormat.OGG}
        
        # Video to video conversions
        video_formats = {ContentFormat.MP4, ContentFormat.AVI, ContentFormat.MOV, 
                        ContentFormat.WMV, ContentFormat.WEBM}
        
        # Image to image conversions
        image_formats = {ContentFormat.JPEG, ContentFormat.PNG, ContentFormat.GIF, 
                        ContentFormat.WEBP, ContentFormat.SVG}
        
        # Same category conversions are supported
        if source in audio_formats and target in audio_formats:
            return True
        if source in video_formats and target in video_formats:
            return True
        if source in image_formats and target in image_formats:
            return True
            
        # Cross-category conversions (limited support)
        if source in video_formats and target in audio_formats:
            return True  # Extract audio from video
            
        return False
        
    def _add_to_queue(self, request: ConversionRequest):
        """Add request to conversion queue with priority sorting"""
        # Insert based on priority
        inserted = False
        for i, queued_request in enumerate(self.conversion_queue):
            if request.priority.value > queued_request.priority.value:
                self.conversion_queue.insert(i, request)
                inserted = True
                break
                
        if not inserted:
            self.conversion_queue.append(request)
            
    async def process_conversion_queue(self):
        """Process queued conversion requests"""
        while self.conversion_queue:
            request = self.conversion_queue.pop(0)
            
            # Find corresponding job
            job = None
            for j in self.active_jobs.values():
                if j.request.request_id == request.request_id:
                    job = j
                    break
                    
            if not job:
                continue
                
            # Process conversion
            await self._process_conversion_job(job)
            
    async def _process_conversion_job(self, job: ConversionJob):
        """Process individual conversion job"""
        job.status = ConversionStatus.PROCESSING
        job.started_at = datetime.now()
        
        try:
            total_formats = len(job.request.target_formats)
            
            for i, target_format in enumerate(job.request.target_formats):
                # Update progress
                job.current_format = target_format
                job.progress_percentage = (i / total_formats) * 100
                
                # Simulate conversion process
                result = await self._convert_content(
                    job.request.source_format, 
                    target_format, 
                    job.request
                )
                
                # Add result to history
                self.conversion_history.append(result)
                
                # Update job progress
                job.progress_percentage = ((i + 1) / total_formats) * 100
                
            # Mark job as completed
            job.status = ConversionStatus.COMPLETED
            job.completed_at = datetime.now()
            
            # Move to completed jobs
            self.completed_jobs.append(job)
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
                
        except Exception as e:
            job.status = ConversionStatus.FAILED
            job.error_message = str(e)
            job.retry_count += 1
            
            # Retry logic
            if job.retry_count < 3:
                job.status = ConversionStatus.RETRYING
                await asyncio.sleep(5)  # Wait before retry
                await self._process_conversion_job(job)
            else:
                logger.error(f"Conversion job failed after retries: {job.job_id}")
                
    async def _convert_content(self, 
                             source_format: ContentFormat, 
                             target_format: ContentFormat,
                             request: ConversionRequest) -> ConversionResult:
        """Simulate content conversion process"""
        start_time = datetime.now()
        
        # Simulate conversion time based on format complexity
        conversion_time = self._estimate_conversion_time(source_format, target_format)
        await asyncio.sleep(min(conversion_time, 1.0))  # Simulate work (max 1 second for demo)
        
        # Calculate quality metrics
        quality_score = await self._assess_conversion_quality(source_format, target_format)
        
        # Create result
        result = ConversionResult(
            job_id=request.request_id,
            request_id=request.request_id,
            source_format=source_format,
            target_format=target_format,
            status=ConversionStatus.COMPLETED,
            output_file_path=f"/output/{request.content_id}.{target_format.value}",
            file_size_bytes=self._estimate_file_size(target_format),
            conversion_time_seconds=(datetime.now() - start_time).total_seconds(),
            quality_score=quality_score,
            compression_ratio=self._calculate_compression_ratio(source_format, target_format),
            metadata_preserved=True
        )
        
        return result
        
    def _estimate_conversion_time(self, source: ContentFormat, target: ContentFormat) -> float:
        """Estimate conversion time based on format complexity"""
        complexity_scores = {
            ContentFormat.WAV: 1.0,
            ContentFormat.MP3: 2.0,
            ContentFormat.AAC: 2.5,
            ContentFormat.FLAC: 3.0,
            ContentFormat.OGG: 2.8,
            ContentFormat.MP4: 5.0,
            ContentFormat.AVI: 4.0,
            ContentFormat.WEBM: 6.0,
            ContentFormat.JPEG: 0.5,
            ContentFormat.PNG: 1.0,
            ContentFormat.WEBP: 1.5
        }
        
        source_complexity = complexity_scores.get(source, 2.0)
        target_complexity = complexity_scores.get(target, 2.0)
        
        return (source_complexity + target_complexity) * 0.5
        
    async def _assess_conversion_quality(self, 
                                       source: ContentFormat, 
                                       target: ContentFormat) -> float:
        """Assess quality of converted content"""
        # Base quality score
        base_quality = 0.9
        
        # Format-specific quality factors
        quality_factors = {
            # Lossless to lossy conversions
            (ContentFormat.WAV, ContentFormat.MP3): 0.85,
            (ContentFormat.FLAC, ContentFormat.MP3): 0.85,
            (ContentFormat.PNG, ContentFormat.JPEG): 0.8,
            
            # Lossy to lossless (no quality gain)
            (ContentFormat.MP3, ContentFormat.WAV): 0.7,
            (ContentFormat.JPEG, ContentFormat.PNG): 0.75,
            
            # Same format family
            (ContentFormat.MP3, ContentFormat.AAC): 0.95,
            (ContentFormat.MP4, ContentFormat.WEBM): 0.92
        }
        
        factor = quality_factors.get((source, target), base_quality)
        
        # Add some randomness for realism
        import random
        noise = random.uniform(-0.05, 0.05)
        
        return max(0.0, min(1.0, factor + noise))
        
    def _estimate_file_size(self, format: ContentFormat) -> int:
        """Estimate output file size in bytes"""
        # Rough estimates for different formats (for 3-minute content)
        size_estimates = {
            ContentFormat.WAV: 30 * 1024 * 1024,  # 30MB
            ContentFormat.FLAC: 15 * 1024 * 1024,  # 15MB
            ContentFormat.MP3: 3 * 1024 * 1024,   # 3MB
            ContentFormat.AAC: 2.5 * 1024 * 1024, # 2.5MB
            ContentFormat.OGG: 2.8 * 1024 * 1024, # 2.8MB
            ContentFormat.MP4: 50 * 1024 * 1024,  # 50MB
            ContentFormat.WEBM: 35 * 1024 * 1024, # 35MB
            ContentFormat.JPEG: 2 * 1024 * 1024,  # 2MB
            ContentFormat.PNG: 5 * 1024 * 1024,   # 5MB
            ContentFormat.WEBP: 1.5 * 1024 * 1024 # 1.5MB
        }
        
        return size_estimates.get(format, 5 * 1024 * 1024)
        
    def _calculate_compression_ratio(self, source: ContentFormat, target: ContentFormat) -> float:
        """Calculate compression ratio"""
        source_size = self._estimate_file_size(source)
        target_size = self._estimate_file_size(target)
        
        if source_size == 0:
            return 1.0
            
        return target_size / source_size
        
    def get_job_status(self, job_id: str) -> Optional[ConversionJob]:
        """Get status of a conversion job"""
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
            
        for job in self.completed_jobs:
            if job.job_id == job_id:
                return job
                
        return None
        
    def get_conversion_statistics(self) -> Dict[str, Any]:
        """Get comprehensive conversion statistics"""
        total_jobs = len(self.completed_jobs) + len(self.active_jobs)
        completed_jobs = len(self.completed_jobs)
        
        if completed_jobs == 0:
            return {
                'total_jobs': total_jobs,
                'completed_jobs': 0,
                'success_rate': 0.0,
                'average_conversion_time': 0.0,
                'average_quality_score': 0.0
            }
            
        # Calculate success rate
        successful_jobs = sum(1 for job in self.completed_jobs 
                            if job.status == ConversionStatus.COMPLETED)
        success_rate = successful_jobs / completed_jobs
        
        # Calculate average conversion time
        conversion_times = []
        for result in self.conversion_history:
            if result.conversion_time_seconds > 0:
                conversion_times.append(result.conversion_time_seconds)
                
        avg_conversion_time = sum(conversion_times) / len(conversion_times) if conversion_times else 0
        
        # Calculate average quality score
        quality_scores = [result.quality_score for result in self.conversion_history 
                         if result.quality_score > 0]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Format popularity
        format_usage = {}
        for result in self.conversion_history:
            target_format = result.target_format.value
            format_usage[target_format] = format_usage.get(target_format, 0) + 1
            
        return {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'active_jobs': len(self.active_jobs),
            'queued_jobs': len(self.conversion_queue),
            'success_rate': success_rate,
            'average_conversion_time': avg_conversion_time,
            'average_quality_score': avg_quality,
            'format_popularity': format_usage,
            'total_conversions': len(self.conversion_history)
        }
        
    async def optimize_conversion_parameters(self, platform: str, content_type: str) -> Dict[str, Any]:
        """Optimize conversion parameters for specific platform"""
        platform_specs = self.platform_specifications.get(platform, {})
        content_specs = platform_specs.get(content_type, {})
        
        if not content_specs:
            return {'error': f'No specifications found for {platform}/{content_type}'}
            
        # Generate optimized parameters
        optimized_params = {
            'recommended_formats': content_specs.get('formats', []),
            'quality_settings': {},
            'compression_settings': {},
            'metadata_requirements': {}
        }
        
        # Add quality settings based on format
        if 'bitrate' in content_specs:
            optimized_params['quality_settings']['bitrate'] = content_specs['bitrate']
        if 'max_resolution' in content_specs:
            optimized_params['quality_settings']['resolution'] = content_specs['max_resolution']
        if 'sample_rate' in content_specs:
            optimized_params['quality_settings']['sample_rate'] = content_specs['sample_rate']
            
        return optimized_params
        
    def cancel_conversion(self, job_id: str) -> bool:
        """Cancel an active conversion job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            if job.status in [ConversionStatus.QUEUED, ConversionStatus.PROCESSING]:
                job.status = ConversionStatus.CANCELLED
                
                # Remove from queue if queued
                self.conversion_queue = [req for req in self.conversion_queue 
                                       if req.request_id != job.request.request_id]
                
                logger.info(f"Conversion job cancelled: {job_id}")
                return True
                
        return False
        
    async def cleanup_old_jobs(self, days_old: int = 7):
        """Clean up old completed jobs"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Remove old completed jobs
        old_jobs = [job for job in self.completed_jobs 
                   if job.completed_at and job.completed_at < cutoff_date]
        
        for job in old_jobs:
            self.completed_jobs.remove(job)
            
        # Remove old conversion history
        old_results = [result for result in self.conversion_history 
                      if result.timestamp < cutoff_date]
        
        for result in old_results:
            self.conversion_history.remove(result)
            
        logger.info(f"Cleaned up {len(old_jobs)} old jobs and {len(old_results)} old results")

# Export main classes
__all__ = [
    'ContentFormatConverterMonitor',
    'ConversionRequest', 
    'ConversionJob',
    'ConversionResult',
    'ConversionStatus',
    'ContentFormat',
    'ConversionPriority',
    'QualityMetrics'
]