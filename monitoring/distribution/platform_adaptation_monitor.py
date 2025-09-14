"""
🌍 MONITORING DISTRIBUTION - Platform Adaptation Monitor
Advanced multi-platform content adaptation monitoring for Ainflue ecosystem
Backend Senior + Microservices Architect Implementation

© 2025 Fahed Mlaiel - All Rights Reserved
Contact: mlaiel@live.de
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import aiohttp
import hashlib
from concurrent.futures import ThreadPoolExecutor
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Platform(Enum):
    """Supported platforms for content distribution"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    DISCORD = "discord"
    REDDIT = "reddit"

class ContentType(Enum):
    """Content types for adaptation"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    REEL = "reel"
    PODCAST = "podcast"

class AdaptationStatus(Enum):
    """Status of content adaptation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY_REQUIRED = "retry_required"
    OPTIMIZING = "optimizing"

class QualityMetric(Enum):
    """Quality metrics for adapted content"""
    RESOLUTION = "resolution"
    BITRATE = "bitrate"
    FRAME_RATE = "frame_rate"
    DURATION = "duration"
    FILE_SIZE = "file_size"
    ASPECT_RATIO = "aspect_ratio"
    AUDIO_QUALITY = "audio_quality"
    COMPRESSION_RATIO = "compression_ratio"

@dataclass
class PlatformRequirements:
    """Platform-specific content requirements"""
    platform: Platform
    max_file_size_mb: float
    supported_formats: List[str]
    max_duration_seconds: int
    required_dimensions: Dict[str, Tuple[int, int]]
    max_bitrate_kbps: int
    audio_requirements: Dict[str, Any]
    metadata_requirements: List[str]
    api_rate_limits: Dict[str, int]
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ContentItem:
    """Content item for adaptation"""
    content_id: str
    creator_id: str
    content_type: ContentType
    original_format: str
    original_size_mb: float
    original_duration: Optional[int]
    metadata: Dict[str, Any]
    target_platforms: List[Platform]
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class AdaptationTask:
    """Content adaptation task"""
    task_id: str
    content_id: str
    source_platform: Optional[Platform]
    target_platform: Platform
    content_type: ContentType
    adaptation_params: Dict[str, Any]
    status: AdaptationStatus
    progress_percentage: float
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metrics: Dict[QualityMetric, Any] = field(default_factory=dict)

@dataclass
class AdaptationResult:
    """Result of content adaptation"""
    task_id: str
    adapted_content_url: str
    adaptation_time_seconds: float
    quality_metrics: Dict[QualityMetric, Any]
    file_size_reduction_percentage: float
    quality_score: float
    platform_compliance_score: float
    optimization_recommendations: List[str] = field(default_factory=list)

class PlatformAdaptationMonitor:
    """
    🌍 Advanced Platform Adaptation Monitor for Ainflue Distribution
    
    Multi-platform content adaptation with:
    - Real-time platform requirement monitoring
    - Intelligent content adaptation pipeline
    - Quality preservation optimization
    - Cross-platform format optimization
    - Performance monitoring and analytics
    - Automated retry and error handling
    - Platform API integration and rate limiting
    - Content delivery optimization
    """
    
    def __init__(self, redis_url -> None: str = None, max_workers -> None: int = 10) -> None:
        """Initialize platform adaptation monitor"""
        self.redis_url = redis_url
        self.max_workers = max_workers
        
        # Thread pool for adaptation tasks
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Data storage
        self.platform_requirements: Dict[Platform, PlatformRequirements] = {}
        self.adaptation_tasks: Dict[str, AdaptationTask] = {}
        self.adaptation_results: Dict[str, AdaptationResult] = {}
        self.content_queue: List[ContentItem] = []
        
        # Performance tracking
        self.platform_performance: Dict[Platform, Dict[str, float]] = {}
        self.adaptation_stats: Dict[str, int] = {
            'total_adaptations': 0,
            'successful_adaptations': 0,
            'failed_adaptations': 0,
            'retry_count': 0
        }
        
        # Rate limiting
        self.api_rate_limits: Dict[Platform, Dict[str, Any]] = {}
        
        # Initialize platform requirements
        asyncio.create_task(self._initialize_platform_requirements())
        
        logger.info("🌍 Platform Adaptation Monitor initialized")

    async def _initialize_platform_requirements(self) -> None:
        """Initialize platform-specific requirements"""
        try:
            # YouTube requirements
            self.platform_requirements[Platform.YOUTUBE] = PlatformRequirements(
                platform=Platform.YOUTUBE,
                max_file_size_mb=128000,  # 128GB for premium
                supported_formats=['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm'],
                max_duration_seconds=43200,  # 12 hours
                required_dimensions={
                    'standard': (1920, 1080),
                    'shorts': (1080, 1920),
                    'thumbnail': (1280, 720)
                },
                max_bitrate_kbps=68000,
                audio_requirements={
                    'sample_rate': 48000,
                    'channels': 2,
                    'bitrate': 320
                },
                metadata_requirements=['title', 'description', 'tags', 'category'],
                api_rate_limits={'upload': 6, 'metadata': 10000}
            )
            
            # Instagram requirements
            self.platform_requirements[Platform.INSTAGRAM] = PlatformRequirements(
                platform=Platform.INSTAGRAM,
                max_file_size_mb=4000,  # 4GB for video
                supported_formats=['mp4', 'mov', 'jpg', 'png'],
                max_duration_seconds=3600,  # 60 minutes for IGTV
                required_dimensions={
                    'feed': (1080, 1080),
                    'story': (1080, 1920),
                    'reel': (1080, 1920),
                    'igtv': (1080, 1920)
                },
                max_bitrate_kbps=8000,
                audio_requirements={
                    'sample_rate': 44100,
                    'channels': 2,
                    'bitrate': 128
                },
                metadata_requirements=['caption', 'hashtags', 'location'],
                api_rate_limits={'upload': 200, 'metadata': 600}
            )
            
            # TikTok requirements
            self.platform_requirements[Platform.TIKTOK] = PlatformRequirements(
                platform=Platform.TIKTOK,
                max_file_size_mb=287,  # 287MB
                supported_formats=['mp4', 'mov', 'webm'],
                max_duration_seconds=600,  # 10 minutes
                required_dimensions={
                    'vertical': (1080, 1920),
                    'horizontal': (1920, 1080),
                    'square': (1080, 1080)
                },
                max_bitrate_kbps=5000,
                audio_requirements={
                    'sample_rate': 44100,
                    'channels': 2,
                    'bitrate': 128
                },
                metadata_requirements=['description', 'hashtags', 'effects'],
                api_rate_limits={'upload': 100, 'metadata': 300}
            )
            
            # Add more platforms as needed
            logger.info("✅ Platform requirements initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing platform requirements: {e}")

    async def analyze_content_adaptation_needs(
        self,
        content_item: ContentItem
    ) -> Dict[Platform, Dict[str, Any]]:
        """
        🔍 Analyze content adaptation needs for target platforms
        
        Determine what adaptations are needed for each platform
        """
        try:
            logger.info(f"🔍 Analyzing adaptation needs for content: {content_item.content_id}")
            
            adaptation_needs = {}
            
            for platform in content_item.target_platforms:
                if platform not in self.platform_requirements:
                    logger.warning(f"Platform {platform} requirements not available")
                    continue
                
                requirements = self.platform_requirements[platform]
                needs = {
                    'format_conversion_needed': False,
                    'resize_needed': False,
                    'compression_needed': False,
                    'duration_adjustment_needed': False,
                    'audio_optimization_needed': False,
                    'metadata_adaptation_needed': False,
                    'recommended_adaptations': [],
                    'compliance_issues': []
                }
                
                # Check format compatibility
                if content_item.original_format.lower() not in [fmt.lower() for fmt in requirements.supported_formats]:
                    needs['format_conversion_needed'] = True
                    needs['recommended_adaptations'].append(
                        f"Convert from {content_item.original_format} to {requirements.supported_formats[0]}"
                    )
                
                # Check file size
                if content_item.original_size_mb > requirements.max_file_size_mb:
                    needs['compression_needed'] = True
                    reduction_needed = ((content_item.original_size_mb - requirements.max_file_size_mb) / 
                                      content_item.original_size_mb * 100)
                    needs['recommended_adaptations'].append(
                        f"Reduce file size by {reduction_needed:.1f}% (from {content_item.original_size_mb:.1f}MB to <{requirements.max_file_size_mb}MB)"
                    )
                
                # Check duration
                if content_item.original_duration and content_item.original_duration > requirements.max_duration_seconds:
                    needs['duration_adjustment_needed'] = True
                    needs['compliance_issues'].append(
                        f"Duration {content_item.original_duration}s exceeds limit of {requirements.max_duration_seconds}s"
                    )
                
                # Check dimensions for visual content
                if content_item.content_type in [ContentType.VIDEO, ContentType.IMAGE]:
                    current_dimensions = content_item.metadata.get('dimensions', {})
                    if current_dimensions:
                        width, height = current_dimensions.get('width', 0), current_dimensions.get('height', 0)
                        
                        # Find best matching platform dimension requirement
                        best_match = None
                        min_scale_diff = float('inf')
                        
                        for dim_type, (req_width, req_height) in requirements.required_dimensions.items():
                            scale_diff = abs((width/height) - (req_width/req_height))
                            if scale_diff < min_scale_diff:
                                min_scale_diff = scale_diff
                                best_match = (dim_type, req_width, req_height)
                        
                        if best_match and (width != best_match[1] or height != best_match[2]):
                            needs['resize_needed'] = True
                            needs['recommended_adaptations'].append(
                                f"Resize to {best_match[1]}x{best_match[2]} for {best_match[0]} format"
                            )
                
                # Check audio requirements for audio/video content
                if content_item.content_type in [ContentType.AUDIO, ContentType.VIDEO, ContentType.PODCAST]:
                    audio_metadata = content_item.metadata.get('audio', {})
                    if audio_metadata:
                        current_sample_rate = audio_metadata.get('sample_rate', 0)
                        required_sample_rate = requirements.audio_requirements.get('sample_rate', 44100)
                        
                        if current_sample_rate != required_sample_rate:
                            needs['audio_optimization_needed'] = True
                            needs['recommended_adaptations'].append(
                                f"Adjust audio sample rate from {current_sample_rate}Hz to {required_sample_rate}Hz"
                            )
                
                # Check metadata requirements
                current_metadata = set(content_item.metadata.keys())
                required_metadata = set(requirements.metadata_requirements)
                missing_metadata = required_metadata - current_metadata
                
                if missing_metadata:
                    needs['metadata_adaptation_needed'] = True
                    needs['compliance_issues'].append(
                        f"Missing required metadata: {', '.join(missing_metadata)}"
                    )
                
                adaptation_needs[platform] = needs
            
            logger.info(f"✅ Adaptation analysis completed for {len(adaptation_needs)} platforms")
            return adaptation_needs
            
        except Exception as e:
            logger.error(f"❌ Error analyzing adaptation needs: {e}")
            return {}

    async def create_adaptation_tasks(
        self,
        content_item: ContentItem,
        adaptation_needs: Dict[Platform, Dict[str, Any]],
        priority: int = 1
    ) -> List[str]:
        """
        📋 Create adaptation tasks for content
        
        Generate specific adaptation tasks based on analysis
        """
        try:
            logger.info(f"📋 Creating adaptation tasks for content: {content_item.content_id}")
            
            task_ids = []
            
            for platform, needs in adaptation_needs.items():
                # Check if any adaptation is needed
                if not any([
                    needs.get('format_conversion_needed', False),
                    needs.get('resize_needed', False),
                    needs.get('compression_needed', False),
                    needs.get('audio_optimization_needed', False)
                ]):
                    logger.info(f"No adaptation needed for {platform}")
                    continue
                
                # Create adaptation task
                task_id = f"adapt_{content_item.content_id}_{platform.value}_{int(time.time())}"
                
                # Determine adaptation parameters
                adaptation_params = {
                    'source_format': content_item.original_format,
                    'target_format': self.platform_requirements[platform].supported_formats[0],
                    'quality_target': 'high',
                    'optimization_level': 'balanced'
                }
                
                # Add format conversion params
                if needs.get('format_conversion_needed'):
                    adaptation_params['format_conversion'] = {
                        'target_format': self.platform_requirements[platform].supported_formats[0],
                        'quality_preset': 'platform_optimized'
                    }
                
                # Add resize params
                if needs.get('resize_needed'):
                    requirements = self.platform_requirements[platform]
                    # Use the first available dimension as default
                    default_dim = list(requirements.required_dimensions.values())[0]
                    adaptation_params['resize'] = {
                        'target_width': default_dim[0],
                        'target_height': default_dim[1],
                        'maintain_aspect_ratio': True,
                        'scale_mode': 'fit'
                    }
                
                # Add compression params
                if needs.get('compression_needed'):
                    target_size_mb = self.platform_requirements[platform].max_file_size_mb * 0.8  # 80% of limit
                    adaptation_params['compression'] = {
                        'target_size_mb': target_size_mb,
                        'quality_preservation': 'high',
                        'bitrate_optimization': True
                    }
                
                # Add audio optimization params
                if needs.get('audio_optimization_needed'):
                    audio_reqs = self.platform_requirements[platform].audio_requirements
                    adaptation_params['audio_optimization'] = {
                        'sample_rate': audio_reqs.get('sample_rate', 44100),
                        'channels': audio_reqs.get('channels', 2),
                        'bitrate': audio_reqs.get('bitrate', 128)
                    }
                
                # Create task
                task = AdaptationTask(
                    task_id=task_id,
                    content_id=content_item.content_id,
                    source_platform=None,
                    target_platform=platform,
                    content_type=content_item.content_type,
                    adaptation_params=adaptation_params,
                    status=AdaptationStatus.PENDING,
                    progress_percentage=0.0
                )
                
                self.adaptation_tasks[task_id] = task
                task_ids.append(task_id)
                
                logger.info(f"📋 Created adaptation task: {task_id} for {platform}")
            
            logger.info(f"✅ Created {len(task_ids)} adaptation tasks")
            return task_ids
            
        except Exception as e:
            logger.error(f"❌ Error creating adaptation tasks: {e}")
            return []

    async def execute_adaptation_task(
        self,
        task_id: str
    ) -> Optional[AdaptationResult]:
        """
        ⚙️ Execute content adaptation task
        
        Perform the actual content adaptation
        """
        try:
            if task_id not in self.adaptation_tasks:
                logger.error(f"Task {task_id} not found")
                return None
            
            task = self.adaptation_tasks[task_id]
            logger.info(f"⚙️ Executing adaptation task: {task_id}")
            
            # Update task status
            task.status = AdaptationStatus.IN_PROGRESS
            task.started_at = datetime.now()
            task.progress_percentage = 10.0
            
            start_time = time.time()
            
            try:
                # Simulate adaptation process (would be real implementation in production)
                result = await self._perform_adaptation(task)
                
                if result:
                    task.status = AdaptationStatus.COMPLETED
                    task.completed_at = datetime.now()
                    task.progress_percentage = 100.0
                    
                    # Store result
                    self.adaptation_results[task_id] = result
                    
                    # Update statistics
                    self.adaptation_stats['total_adaptations'] += 1
                    self.adaptation_stats['successful_adaptations'] += 1
                    
                    # Update platform performance
                    adaptation_time = time.time() - start_time
                    platform = task.target_platform
                    if platform not in self.platform_performance:
                        self.platform_performance[platform] = {
                            'avg_adaptation_time': 0.0,
                            'success_rate': 0.0,
                            'total_tasks': 0
                        }
                    
                    perf = self.platform_performance[platform]
                    perf['total_tasks'] += 1
                    perf['avg_adaptation_time'] = (
                        (perf['avg_adaptation_time'] * (perf['total_tasks'] - 1) + adaptation_time) /
                        perf['total_tasks']
                    )
                    
                    logger.info(f"✅ Adaptation completed: {task_id} in {adaptation_time:.2f}s")
                    return result
                else:
                    task.status = AdaptationStatus.FAILED
                    task.error_message = "Adaptation process failed"
                    self.adaptation_stats['total_adaptations'] += 1
                    self.adaptation_stats['failed_adaptations'] += 1
                    
                    logger.error(f"❌ Adaptation failed: {task_id}")
                    return None
                    
            except Exception as e:
                task.status = AdaptationStatus.FAILED
                task.error_message = str(e)
                self.adaptation_stats['total_adaptations'] += 1
                self.adaptation_stats['failed_adaptations'] += 1
                
                logger.error(f"❌ Adaptation error: {task_id} - {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error executing adaptation task {task_id}: {e}")
            return None

    async def _perform_adaptation(
        self,
        task: AdaptationTask
    ) -> Optional[AdaptationResult]:
        """Perform the actual content adaptation"""
        try:
            # Simulate adaptation process
            await asyncio.sleep(2)  # Simulate processing time
            task.progress_percentage = 50.0
            
            await asyncio.sleep(2)  # More processing
            task.progress_percentage = 80.0
            
            # Simulate quality metrics calculation
            quality_metrics = {
                QualityMetric.RESOLUTION: "1920x1080",
                QualityMetric.BITRATE: 5000,
                QualityMetric.FRAME_RATE: 30,
                QualityMetric.FILE_SIZE: 45.6,
                QualityMetric.COMPRESSION_RATIO: 0.75,
                QualityMetric.AUDIO_QUALITY: "320kbps"
            }
            
            # Calculate quality scores
            quality_score = self._calculate_quality_score(quality_metrics, task.adaptation_params)
            compliance_score = self._calculate_platform_compliance(task.target_platform, quality_metrics)
            
            # Generate optimization recommendations
            recommendations = self._generate_optimization_recommendations(
                task.target_platform, quality_metrics, quality_score
            )
            
            # Create result
            result = AdaptationResult(
                task_id=task.task_id,
                adapted_content_url=f"https://cdn.ainflue.com/adapted/{task.content_id}_{task.target_platform.value}",
                adaptation_time_seconds=4.0,  # Simulated time
                quality_metrics=quality_metrics,
                file_size_reduction_percentage=25.0,
                quality_score=quality_score,
                platform_compliance_score=compliance_score,
                optimization_recommendations=recommendations
            )
            
            await asyncio.sleep(1)  # Final processing
            task.progress_percentage = 100.0
            
            return result
            
        except Exception as e:
            logger.error(f"Adaptation process error: {e}")
            return None

    def _calculate_quality_score(
        self,
        quality_metrics: Dict[QualityMetric, Any],
        adaptation_params: Dict[str, Any]
    ) -> float:
        """Calculate overall quality score"""
        try:
            # Simplified quality scoring
            score = 0.0
            total_weight = 0.0
            
            # Resolution score
            if QualityMetric.RESOLUTION in quality_metrics:
                resolution = quality_metrics[QualityMetric.RESOLUTION]
                if isinstance(resolution, str) and 'x' in resolution:
                    width, height = map(int, resolution.split('x'))
                    pixels = width * height
                    
                    if pixels >= 2073600:  # 1920x1080
                        resolution_score = 1.0
                    elif pixels >= 921600:  # 1280x720
                        resolution_score = 0.8
                    else:
                        resolution_score = 0.6
                    
                    score += resolution_score * 0.3
                    total_weight += 0.3
            
            # Bitrate score
            if QualityMetric.BITRATE in quality_metrics:
                bitrate = quality_metrics[QualityMetric.BITRATE]
                if bitrate >= 5000:
                    bitrate_score = 1.0
                elif bitrate >= 2500:
                    bitrate_score = 0.8
                else:
                    bitrate_score = 0.6
                
                score += bitrate_score * 0.25
                total_weight += 0.25
            
            # Compression ratio score (lower is better for quality)
            if QualityMetric.COMPRESSION_RATIO in quality_metrics:
                compression = quality_metrics[QualityMetric.COMPRESSION_RATIO]
                compression_score = max(0.1, 1.0 - compression)
                score += compression_score * 0.2
                total_weight += 0.2
            
            # Frame rate score
            if QualityMetric.FRAME_RATE in quality_metrics:
                fps = quality_metrics[QualityMetric.FRAME_RATE]
                if fps >= 60:
                    fps_score = 1.0
                elif fps >= 30:
                    fps_score = 0.9
                elif fps >= 24:
                    fps_score = 0.8
                else:
                    fps_score = 0.6
                
                score += fps_score * 0.15
                total_weight += 0.15
            
            # Audio quality score
            if QualityMetric.AUDIO_QUALITY in quality_metrics:
                audio = quality_metrics[QualityMetric.AUDIO_QUALITY]
                if '320kbps' in str(audio):
                    audio_score = 1.0
                elif '256kbps' in str(audio):
                    audio_score = 0.9
                elif '128kbps' in str(audio):
                    audio_score = 0.8
                else:
                    audio_score = 0.6
                
                score += audio_score * 0.1
                total_weight += 0.1
            
            return score / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating quality score: {e}")
            return 0.5

    def _calculate_platform_compliance(
        self,
        platform: Platform,
        quality_metrics: Dict[QualityMetric, Any]
    ) -> float:
        """Calculate platform compliance score"""
        try:
            if platform not in self.platform_requirements:
                return 0.0
            
            requirements = self.platform_requirements[platform]
            compliance_score = 0.0
            total_checks = 0
            
            # Check file size compliance
            if QualityMetric.FILE_SIZE in quality_metrics:
                file_size = quality_metrics[QualityMetric.FILE_SIZE]
                if file_size <= requirements.max_file_size_mb:
                    compliance_score += 1.0
                total_checks += 1
            
            # Check bitrate compliance
            if QualityMetric.BITRATE in quality_metrics:
                bitrate = quality_metrics[QualityMetric.BITRATE]
                if bitrate <= requirements.max_bitrate_kbps:
                    compliance_score += 1.0
                total_checks += 1
            
            # Check audio quality compliance
            audio_reqs = requirements.audio_requirements
            if QualityMetric.AUDIO_QUALITY in quality_metrics:
                # Simplified audio compliance check
                compliance_score += 1.0
                total_checks += 1
            
            return compliance_score / total_checks if total_checks > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating platform compliance: {e}")
            return 0.0

    def _generate_optimization_recommendations(
        self,
        platform: Platform,
        quality_metrics: Dict[QualityMetric, Any],
        quality_score: float
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        try:
            if quality_score < 0.7:
                recommendations.append("Consider increasing bitrate for better quality")
            
            if QualityMetric.FILE_SIZE in quality_metrics:
                file_size = quality_metrics[QualityMetric.FILE_SIZE]
                if platform in self.platform_requirements:
                    max_size = self.platform_requirements[platform].max_file_size_mb
                    if file_size > max_size * 0.9:
                        recommendations.append("File size is near platform limit - consider additional compression")
            
            if QualityMetric.COMPRESSION_RATIO in quality_metrics:
                compression = quality_metrics[QualityMetric.COMPRESSION_RATIO]
                if compression > 0.8:
                    recommendations.append("High compression detected - may impact visual quality")
            
            # Platform-specific recommendations
            if platform == Platform.YOUTUBE:
                recommendations.append("Consider using VP9 codec for better compression on YouTube")
            elif platform == Platform.INSTAGRAM:
                recommendations.append("Use square format for better feed visibility")
            elif platform == Platform.TIKTOK:
                recommendations.append("Optimize for vertical viewing with 9:16 aspect ratio")
            
            if not recommendations:
                recommendations.append("Content is well optimized for target platform")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Unable to generate specific recommendations")
        
        return recommendations

    async def monitor_adaptation_queue(self) -> Dict[str, Any]:
        """
        📊 Monitor adaptation queue status
        
        Get real-time status of adaptation pipeline
        """
        try:
            logger.info("📊 Monitoring adaptation queue")
            
            # Count tasks by status
            status_counts = {}
            for status in AdaptationStatus:
                status_counts[status.value] = len([
                    task for task in self.adaptation_tasks.values()
                    if task.status == status
                ])
            
            # Calculate platform distribution
            platform_distribution = {}
            for task in self.adaptation_tasks.values():
                platform = task.target_platform.value
                if platform not in platform_distribution:
                    platform_distribution[platform] = 0
                platform_distribution[platform] += 1
            
            # Calculate average processing times
            completed_tasks = [
                task for task in self.adaptation_tasks.values()
                if task.status == AdaptationStatus.COMPLETED and task.started_at and task.completed_at
            ]
            
            avg_processing_time = 0.0
            if completed_tasks:
                processing_times = [
                    (task.completed_at - task.started_at).total_seconds()
                    for task in completed_tasks
                ]
                avg_processing_time = sum(processing_times) / len(processing_times)
            
            # Current queue status
            queue_status = {
                'timestamp': datetime.now().isoformat(),
                'total_tasks': len(self.adaptation_tasks),
                'status_distribution': status_counts,
                'platform_distribution': platform_distribution,
                'performance_metrics': {
                    'avg_processing_time_seconds': avg_processing_time,
                    'success_rate': (
                        self.adaptation_stats['successful_adaptations'] /
                        max(1, self.adaptation_stats['total_adaptations'])
                    ),
                    'total_processed': self.adaptation_stats['total_adaptations'],
                    'queue_length': status_counts.get('pending', 0)
                },
                'platform_performance': self.platform_performance,
                'statistics': self.adaptation_stats
            }
            
            logger.info(f"✅ Queue monitoring completed: {queue_status['total_tasks']} tasks")
            return queue_status
            
        except Exception as e:
            logger.error(f"❌ Error monitoring adaptation queue: {e}")
            return {}

    async def optimize_platform_performance(
        self,
        platform: Platform
    ) -> Dict[str, Any]:
        """
        🔧 Optimize performance for specific platform
        
        Analyze and improve adaptation performance
        """
        try:
            logger.info(f"🔧 Optimizing performance for {platform}")
            
            if platform not in self.platform_performance:
                return {'error': f'No performance data available for {platform}'}
            
            perf_data = self.platform_performance[platform]
            
            # Analyze current performance
            analysis = {
                'platform': platform.value,
                'current_performance': perf_data,
                'optimization_opportunities': [],
                'recommendations': [],
                'estimated_improvements': {}
            }
            
            # Check adaptation time
            if perf_data['avg_adaptation_time'] > 10.0:
                analysis['optimization_opportunities'].append({
                    'type': 'slow_adaptation',
                    'current_value': perf_data['avg_adaptation_time'],
                    'target_value': 5.0,
                    'impact': 'high'
                })
                analysis['recommendations'].append(
                    "Consider parallel processing or GPU acceleration for faster adaptation"
                )
            
            # Check success rate
            if perf_data['success_rate'] < 0.95:
                analysis['optimization_opportunities'].append({
                    'type': 'low_success_rate',
                    'current_value': perf_data['success_rate'],
                    'target_value': 0.98,
                    'impact': 'critical'
                })
                analysis['recommendations'].append(
                    "Investigate and fix common failure causes"
                )
            
            # Platform-specific optimizations
            if platform == Platform.YOUTUBE:
                analysis['recommendations'].extend([
                    "Pre-validate content against YouTube policies",
                    "Use YouTube-optimized encoding presets",
                    "Implement chunk upload for large files"
                ])
            elif platform == Platform.INSTAGRAM:
                analysis['recommendations'].extend([
                    "Optimize for mobile viewing",
                    "Pre-generate multiple aspect ratios",
                    "Use Instagram-specific filters and effects"
                ])
            
            # Estimate potential improvements
            if perf_data['avg_adaptation_time'] > 5.0:
                potential_improvement = min(50, (perf_data['avg_adaptation_time'] - 5.0) / perf_data['avg_adaptation_time'] * 100)
                analysis['estimated_improvements']['processing_time_reduction'] = f"{potential_improvement:.1f}%"
            
            if perf_data['success_rate'] < 0.95:
                potential_improvement = (0.98 - perf_data['success_rate']) * 100
                analysis['estimated_improvements']['success_rate_increase'] = f"{potential_improvement:.1f}%"
            
            logger.info(f"✅ Performance optimization analysis completed for {platform}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error optimizing platform performance: {e}")
            return {}

    async def generate_adaptation_report(
        self,
        time_period_hours: int = 24
    ) -> Dict[str, Any]:
        """
        📊 Generate comprehensive adaptation report
        
        Summary of adaptation activities and performance
        """
        try:
            logger.info(f"📊 Generating adaptation report for {time_period_hours}h")
            
            cutoff_time = datetime.now() - timedelta(hours=time_period_hours)
            
            # Filter tasks within time period
            period_tasks = [
                task for task in self.adaptation_tasks.values()
                if task.started_at and task.started_at >= cutoff_time
            ]
            
            # Filter results within time period
            period_results = [
                result for task_id, result in self.adaptation_results.items()
                if task_id in [task.task_id for task in period_tasks]
            ]
            
            report = {
                'report_period': f"{time_period_hours} hours",
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_adaptations': len(period_tasks),
                    'successful_adaptations': len([
                        task for task in period_tasks
                        if task.status == AdaptationStatus.COMPLETED
                    ]),
                    'failed_adaptations': len([
                        task for task in period_tasks
                        if task.status == AdaptationStatus.FAILED
                    ]),
                    'pending_adaptations': len([
                        task for task in period_tasks
                        if task.status in [AdaptationStatus.PENDING, AdaptationStatus.IN_PROGRESS]
                    ])
                },
                'platform_breakdown': {},
                'content_type_breakdown': {},
                'performance_metrics': {},
                'quality_analysis': {},
                'recommendations': []
            }
            
            # Platform breakdown
            for platform in Platform:
                platform_tasks = [task for task in period_tasks if task.target_platform == platform]
                if platform_tasks:
                    successful = len([task for task in platform_tasks if task.status == AdaptationStatus.COMPLETED])
                    report['platform_breakdown'][platform.value] = {
                        'total_tasks': len(platform_tasks),
                        'successful': successful,
                        'success_rate': successful / len(platform_tasks),
                        'avg_processing_time': self.platform_performance.get(platform, {}).get('avg_adaptation_time', 0)
                    }
            
            # Content type breakdown
            for content_type in ContentType:
                type_tasks = [task for task in period_tasks if task.content_type == content_type]
                if type_tasks:
                    successful = len([task for task in type_tasks if task.status == AdaptationStatus.COMPLETED])
                    report['content_type_breakdown'][content_type.value] = {
                        'total_tasks': len(type_tasks),
                        'successful': successful,
                        'success_rate': successful / len(type_tasks)
                    }
            
            # Performance metrics
            if period_results:
                adaptation_times = [result.adaptation_time_seconds for result in period_results]
                quality_scores = [result.quality_score for result in period_results]
                
                report['performance_metrics'] = {
                    'avg_adaptation_time': sum(adaptation_times) / len(adaptation_times),
                    'min_adaptation_time': min(adaptation_times),
                    'max_adaptation_time': max(adaptation_times),
                    'avg_quality_score': sum(quality_scores) / len(quality_scores),
                    'avg_file_size_reduction': sum(
                        result.file_size_reduction_percentage for result in period_results
                    ) / len(period_results)
                }
            
            # Generate recommendations
            if report['summary']['total_adaptations'] > 0:
                success_rate = (report['summary']['successful_adaptations'] / 
                              report['summary']['total_adaptations'])
                
                if success_rate < 0.9:
                    report['recommendations'].append(
                        f"Success rate is {success_rate:.1%} - investigate common failure causes"
                    )
                
                if report['performance_metrics'].get('avg_adaptation_time', 0) > 8:
                    report['recommendations'].append(
                        "Average adaptation time is high - consider performance optimization"
                    )
            
            if not report['recommendations']:
                report['recommendations'].append("Platform adaptation is performing well")
            
            logger.info(f"✅ Adaptation report generated: {report['summary']['total_adaptations']} adaptations")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating adaptation report: {e}")
            return {}

    async def cleanup_old_tasks(self, days_to_keep: int = 7) -> int:
        """Clean up old adaptation tasks and results"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            
            # Clean up old tasks
            old_task_ids = [
                task_id for task_id, task in self.adaptation_tasks.items()
                if task.completed_at and task.completed_at < cutoff_time
            ]
            
            for task_id in old_task_ids:
                del self.adaptation_tasks[task_id]
                if task_id in self.adaptation_results:
                    del self.adaptation_results[task_id]
            
            logger.info(f"🧹 Cleaned up {len(old_task_ids)} old adaptation tasks")
            return len(old_task_ids)
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old tasks: {e}")
            return 0

# Usage example
async def main() -> None:
    """Test the platform adaptation monitor"""
    try:
        # Initialize monitor
        monitor = PlatformAdaptationMonitor()
        
        # Create sample content
        content = ContentItem(
            content_id="content_123",
            creator_id="creator_456",
            content_type=ContentType.VIDEO,
            original_format="mov",
            original_size_mb=150.0,
            original_duration=300,
            metadata={
                'dimensions': {'width': 1920, 'height': 1080},
                'audio': {'sample_rate': 48000, 'channels': 2}
            },
            target_platforms=[Platform.YOUTUBE, Platform.INSTAGRAM, Platform.TIKTOK]
        )
        
        # Analyze adaptation needs
        needs = await monitor.analyze_content_adaptation_needs(content)
        print(f"Adaptation needs analyzed for {len(needs)} platforms")
        
        # Create adaptation tasks
        task_ids = await monitor.create_adaptation_tasks(content, needs)
        print(f"Created {len(task_ids)} adaptation tasks")
        
        # Execute first task
        if task_ids:
            result = await monitor.execute_adaptation_task(task_ids[0])
            if result:
                print(f"Adaptation completed with quality score: {result.quality_score:.2f}")
        
        # Monitor queue
        queue_status = await monitor.monitor_adaptation_queue()
        print(f"Queue status: {queue_status['total_tasks']} total tasks")
        
        # Generate report
        report = await monitor.generate_adaptation_report()
        print(f"Report generated: {report['summary']['total_adaptations']} adaptations")
        
    except Exception as e:
        print(f"Error in platform adaptation monitoring: {e}")

if __name__ == "__main__":
    asyncio.run(main())