"""Advanced Content Distributor - Intelligent Multi-Platform Content Distribution Engine

Enterprise-grade content distribution system with AI-powered optimization, format adaptation,
and intelligent scheduling across all major content platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from dataclasses import dataclass, asdict
import uuid
from pathlib import Path
import tempfile
import aiofiles
from concurrent.futures import ThreadPoolExecutor
import logging
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip
import librosa
import soundfile as sf
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

from .platform_agent import PlatformType, ContentStatus
from .platform_connector import PlatformConnector
from ...core.ai_services import AIContentOptimizer, ImageProcessor, VideoProcessor, AudioProcessor
try:
    from core.database import DatabaseManager
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    DatabaseManager = DatabaseManager
from ...core.cache import CacheManager
from ...core.monitoring import MetricsCollector, PerformanceTracker
from ...models.content_models import ContentItem, MediaFile, OptimizedContent, DistributionResult
from ...services.content_protection import ContentProtectionService
from ...services.seo_optimizer import SEOOptimizer
from ...services.translation import TranslationService
from ...utils.file_handler import FileHandler
from ...utils.format_converter import FormatConverter
from ...utils.quality_analyzer import QualityAnalyzer


class ContentType(Enum):
    """Supported content types for distribution"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    LIVE_STREAM = "live_stream"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    PODCAST = "podcast"
    CAROUSEL = "carousel"
    ALBUM = "album"


class OptimizationLevel(Enum):
    """Content optimization levels"""    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
    AI_ENHANCED = "ai_enhanced"


class DistributionStrategy(Enum):
    """Distribution strategies for content"""    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    OPTIMIZED_TIMING = "optimized_timing"
    STAGGERED = "staggered"
    A_B_TEST = "ab_test"
    VIRAL_BOOST = "viral_boost"


@dataclass
class PlatformSpecification:
    """Platform-specific content specifications"""    platform: PlatformType
    max_file_size: int  # in MB
    supported_formats: List[str]
    max_duration: Optional[int] = None  # in seconds
    recommended_resolution: Optional[Tuple[int, int]] = None
    aspect_ratio: Optional[str] = None
    max_title_length: Optional[int] = None
    max_description_length: Optional[int] = None
    supports_hashtags: bool = True
    max_hashtags: Optional[int] = None
    supports_captions: bool = True
    supports_thumbnail: bool = True
    quality_requirements: Dict[str, Any] = None


@dataclass
class DistributionConfig:
    """Configuration for content distribution"""    target_platforms: List[PlatformType]
    strategy: DistributionStrategy = DistributionStrategy.IMMEDIATE
    optimization_level: OptimizationLevel = OptimizationLevel.ADVANCED
    enable_ai_enhancement: bool = True
    enable_seo_optimization: bool = True
    enable_auto_translation: bool = True
    enable_content_protection: bool = True
    enable_analytics_tracking: bool = True
    enable_collaboration_matching: bool = True
    custom_schedules: Dict[PlatformType, datetime] = None
    target_audience: Dict[str, Any] = None
    monetization_settings: Dict[str, Any] = None
    privacy_settings: Dict[str, str] = None
    backup_enabled: bool = True
    quality_threshold: float = 0.85


@dataclass
class ContentMetadata:
    """Extended content metadata for optimization"""    title: str
    description: str
    tags: List[str]
    category: str
    language: str = "en"
    target_audience: Dict[str, Any] = None
    mood: Optional[str] = None
    genre: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    resolution: Optional[Tuple[int, int]] = None
    bitrate: Optional[int] = None
    frame_rate: Optional[float] = None
    created_at: datetime = None
    modified_at: datetime = None


class ContentDistributor:
    """    Advanced Content Distributor - Intelligent Multi-Platform Distribution Engine
    
    Provides comprehensive content distribution with AI-powered optimization,
    format adaptation, and intelligent scheduling across all platforms.
    """    
    def __init__(self, platform_connector: PlatformConnector):
        self.platform_connector = platform_connector
        self.ai_optimizer = AIContentOptimizer()
        self.image_processor = ImageProcessor()
        self.video_processor = VideoProcessor()
        self.audio_processor = AudioProcessor()
        self.content_protection = ContentProtectionService()
        self.seo_optimizer = SEOOptimizer()
        self.translation_service = TranslationService()
        self.file_handler = FileHandler()
        self.format_converter = FormatConverter()
        self.quality_analyzer = QualityAnalyzer()
        self.db_manager = DatabaseManager()
        self.cache_manager = CacheManager()
        self.metrics_collector = MetricsCollector()
        self.performance_tracker = PerformanceTracker()
        
        # Platform specifications
        self.platform_specs = self._initialize_platform_specifications()
        
        # Optimization pipelines
        self.optimization_pipelines = {}
        self.content_cache = {}
        self.distribution_queue = asyncio.PriorityQueue()
        
        # Processing resources
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="content_dist_"))
        
        self.logger = logging.getLogger(f"{__name__}.ContentDistributor")

    async def initialize(self) -> bool:
        """Initialize content distributor and all services"""        try:
            # Initialize AI services
            await self.ai_optimizer.initialize()
            await self.image_processor.initialize()
            await self.video_processor.initialize()
            await self.audio_processor.initialize()
            
            # Initialize other services
            await self.content_protection.initialize()
            await self.seo_optimizer.initialize()
            await self.translation_service.initialize()
            
            # Initialize optimization pipelines
            await self._initialize_optimization_pipelines()
            
            # Start background processing tasks
            await self._start_background_tasks()
            
            self.logger.info("Content Distributor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Content Distributor: {e}")
            return False

    def _initialize_platform_specifications(self) -> Dict[PlatformType, PlatformSpecification]:
        """Initialize platform-specific content specifications"""        return {
            PlatformType.SPOTIFY: PlatformSpecification(
                platform=PlatformType.SPOTIFY,
                max_file_size=200,  # MB
                supported_formats=['mp3', 'wav', 'flac'],
                max_duration=None,
                supports_hashtags=False,
                supports_thumbnail=True,
                quality_requirements={'min_bitrate': 320, 'sample_rate': 44100}
            ),
            PlatformType.YOUTUBE: PlatformSpecification(
                platform=PlatformType.YOUTUBE,
                max_file_size=256000,  # MB (256GB)
                supported_formats=['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm'],
                max_duration=43200,  # 12 hours
                recommended_resolution=(1920, 1080),
                aspect_ratio="16:9",
                max_title_length=100,
                max_description_length=5000,
                max_hashtags=15,
                quality_requirements={'min_resolution': (1280, 720), 'min_bitrate': 5000}
            ),
            PlatformType.INSTAGRAM: PlatformSpecification(
                platform=PlatformType.INSTAGRAM,
                max_file_size=100,  # MB
                supported_formats=['jpg', 'png', 'mp4', 'mov'],
                max_duration=60,
                recommended_resolution=(1080, 1080),
                aspect_ratio="1:1",
                max_title_length=2200,
                max_hashtags=30,
                quality_requirements={'min_resolution': (1080, 1080)}
            ),
            PlatformType.TIKTOK: PlatformSpecification(
                platform=PlatformType.TIKTOK,
                max_file_size=72,  # MB
                supported_formats=['mp4', 'mov'],
                max_duration=180,  # 3 minutes
                recommended_resolution=(1080, 1920),
                aspect_ratio="9:16",
                max_title_length=150,
                max_hashtags=100,
                quality_requirements={'min_resolution': (720, 1280), 'min_fps': 30}
            ),
            PlatformType.TWITTER: PlatformSpecification(
                platform=PlatformType.TWITTER,
                max_file_size=512,  # MB
                supported_formats=['jpg', 'png', 'gif', 'mp4', 'mov'],
                max_duration=140,
                max_title_length=280,
                max_hashtags=None,
                quality_requirements={'max_gif_size': 15}
            ),
            PlatformType.FACEBOOK: PlatformSpecification(
                platform=PlatformType.FACEBOOK,
                max_file_size=10240,  # MB (10GB)
                supported_formats=['mp4', 'mov', 'avi', 'jpg', 'png'],
                max_duration=240,  # 4 hours
                recommended_resolution=(1920, 1080),
                max_title_length=63206,
                quality_requirements={'min_resolution': (720, 720)}
            ),
            PlatformType.LINKEDIN: PlatformSpecification(
                platform=PlatformType.LINKEDIN,
                max_file_size=5120,  # MB (5GB)
                supported_formats=['mp4', 'mov', 'jpg', 'png'],
                max_duration=600,  # 10 minutes
                recommended_resolution=(1920, 1080),
                max_title_length=3000,
                quality_requirements={'min_resolution': (640, 360)}
            )
        }

    async def distribute_content(
        self,
        content_item: ContentItem,
        distribution_config: DistributionConfig,
        user_id: str
    ) -> Dict[str, Any]:
        """        Main content distribution method with comprehensive optimization
        
        Args:
            content_item: Content to distribute
            distribution_config: Distribution configuration
            user_id: User ID for tracking and permissions
            
        Returns:
            Comprehensive distribution results
        """        distribution_id = str(uuid.uuid4())
        
        try:
            self.logger.info(f"Starting content distribution: {distribution_id}")
            
            # Start performance tracking
            with self.performance_tracker.track_operation("content_distribution"):
                
                # Step 1: Validate content and permissions
                await self._validate_content_and_permissions(content_item, user_id)
                
                # Step 2: Content protection and fingerprinting
                if distribution_config.enable_content_protection:
                    protection_result = await self._protect_content(content_item, user_id)
                
                # Step 3: AI-powered content analysis and enhancement
                if distribution_config.enable_ai_enhancement:
                    enhanced_content = await self._enhance_content_with_ai(content_item)
                else:
                    enhanced_content = content_item
                
                # Step 4: Platform-specific optimization
                optimized_content = await self._optimize_for_platforms(
                    enhanced_content,
                    distribution_config.target_platforms,
                    distribution_config.optimization_level
                )
                
                # Step 5: SEO optimization and translation
                if distribution_config.enable_seo_optimization:
                    optimized_content = await self._apply_seo_optimization(optimized_content)
                
                if distribution_config.enable_auto_translation:
                    optimized_content = await self._apply_translation(optimized_content)
                
                # Step 6: Quality validation
                quality_results = await self._validate_content_quality(
                    optimized_content, distribution_config.quality_threshold
                )
                
                # Step 7: Execute distribution strategy
                distribution_results = await self._execute_distribution_strategy(
                    optimized_content,
                    distribution_config,
                    distribution_id,
                    user_id
                )
                
                # Step 8: Post-distribution tasks
                await self._handle_post_distribution(
                    distribution_id, distribution_results, user_id
                )
                
                # Step 9: Generate comprehensive report
                final_report = await self._generate_distribution_report(
                    distribution_id, distribution_results, quality_results
                )
                
                self.logger.info(f"Content distribution completed: {distribution_id}")
                return final_report
                
        except Exception as e:
            self.logger.error(f"Content distribution failed: {distribution_id} - {e}")
            await self._handle_distribution_error(distribution_id, e, user_id)
            raise

    async def _enhance_content_with_ai(self, content_item: ContentItem) -> ContentItem:
        """Apply AI-powered content enhancement"""        try:
            enhanced_content = content_item.copy()
            
            # Content type specific enhancement
            if content_item.content_type == ContentType.IMAGE:
                enhanced_content = await self._enhance_image_content(enhanced_content)
            elif content_item.content_type == ContentType.VIDEO:
                enhanced_content = await self._enhance_video_content(enhanced_content)
            elif content_item.content_type == ContentType.AUDIO:
                enhanced_content = await self._enhance_audio_content(enhanced_content)
            elif content_item.content_type == ContentType.TEXT:
                enhanced_content = await self._enhance_text_content(enhanced_content)
            
            # Universal AI enhancements
            enhanced_content = await self._apply_universal_ai_enhancements(enhanced_content)
            
            return enhanced_content
            
        except Exception as e:
            self.logger.warning(f"AI enhancement failed, using original content: {e}")
            return content_item

    async def _enhance_image_content(self, content: ContentItem) -> ContentItem:
        """AI-powered image enhancement"""        enhanced_content = content.copy()
        
        # Load image
        image_path = content.media_files[0].file_path
        
        # Apply AI enhancements
        enhanced_image = await self.image_processor.enhance_image(
            image_path,
            enhancement_level="advanced",
            auto_crop=True,
            color_correction=True,
            noise_reduction=True,
            sharpening=True
        )
        
        # Generate optimized thumbnails
        thumbnails = await self.image_processor.generate_thumbnails(
            enhanced_image,
            sizes=[(1080, 1080), (1920, 1080), (1080, 1920)]
        )
        
        # Update content with enhanced version
        enhanced_content.media_files[0].file_path = enhanced_image
        enhanced_content.thumbnails = thumbnails
        
        # AI-generated metadata
        ai_metadata = await self.ai_optimizer.analyze_image_content(enhanced_image)
        enhanced_content.ai_analysis = ai_metadata
        
        return enhanced_content

    async def _enhance_video_content(self, content: ContentItem) -> ContentItem:
        """AI-powered video enhancement"""        enhanced_content = content.copy()
        
        video_path = content.media_files[0].file_path
        
        # Video AI enhancements
        enhanced_video = await self.video_processor.enhance_video(
            video_path,
            stabilization=True,
            color_grading=True,
            noise_reduction=True,
            auto_crop=True,
            generate_subtitles=True
        )
        
        # Generate multiple resolutions
        video_variants = await self.video_processor.generate_resolutions(
            enhanced_video,
            resolutions=[(1920, 1080), (1280, 720), (720, 480)]
        )
        
        # Generate engaging thumbnails using AI
        thumbnails = await self.video_processor.generate_ai_thumbnails(
            enhanced_video,
            num_thumbnails=5,
            use_face_detection=True,
            use_action_detection=True
        )
        
        # AI content analysis
        ai_analysis = await self.ai_optimizer.analyze_video_content(enhanced_video)
        
        # Update content
        enhanced_content.media_files = [MediaFile(path=path, resolution=res) 
                                     for path, res in video_variants.items()]
        enhanced_content.thumbnails = thumbnails
        enhanced_content.ai_analysis = ai_analysis
        
        return enhanced_content

    async def _enhance_audio_content(self, content: ContentItem) -> ContentItem:
        """AI-powered audio enhancement"""        enhanced_content = content.copy()
        
        audio_path = content.media_files[0].file_path
        
        # Audio AI enhancements
        enhanced_audio = await self.audio_processor.enhance_audio(
            audio_path,
            noise_reduction=True,
            normalization=True,
            eq_optimization=True,
            dynamic_range_compression=True
        )
        
        # Generate multiple formats and bitrates
        audio_variants = await self.audio_processor.generate_formats(
            enhanced_audio,
            formats=['mp3', 'wav', 'flac'],
            bitrates=[128, 256, 320]
        )
        
        # Generate waveform visualizations
        waveform_images = await self.audio_processor.generate_waveform_images(
            enhanced_audio,
            styles=['classic', 'modern', 'colorful']
        )
        
        # AI audio analysis
        ai_analysis = await self.ai_optimizer.analyze_audio_content(enhanced_audio)
        
        # Update content
        enhanced_content.media_files = [MediaFile(path=path) for path in audio_variants]
        enhanced_content.visualizations = waveform_images
        enhanced_content.ai_analysis = ai_analysis
        
        return enhanced_content

    async def _optimize_for_platforms(
        self,
        content: ContentItem,
        target_platforms: List[PlatformType],
        optimization_level: OptimizationLevel
    ) -> Dict[PlatformType, OptimizedContent]:
        """Optimize content for each target platform"""        optimized_content = {}
        
        for platform in target_platforms:
            try:
                # Get platform specifications
                specs = self.platform_specs[platform]
                
                # Platform-specific optimization
                platform_optimized = await self._optimize_for_single_platform(
                    content, specs, optimization_level
                )
                
                optimized_content[platform] = platform_optimized
                
            except Exception as e:
                self.logger.error(f"Failed to optimize for {platform.value}: {e}")
                # Use fallback optimization
                optimized_content[platform] = await self._fallback_optimization(content, platform)
        
        return optimized_content

    async def _optimize_for_single_platform(
        self,
        content: ContentItem,
        specs: PlatformSpecification,
        optimization_level: OptimizationLevel
    ) -> OptimizedContent:
        """Optimize content for a specific platform"""        
        # Format conversion if needed
        if content.content_type == ContentType.VIDEO:
            optimized_media = await self._optimize_video_for_platform(content, specs)
        elif content.content_type == ContentType.IMAGE:
            optimized_media = await self._optimize_image_for_platform(content, specs)
        elif content.content_type == ContentType.AUDIO:
            optimized_media = await self._optimize_audio_for_platform(content, specs)
        else:
            optimized_media = content.media_files
        
        # Metadata optimization
        optimized_metadata = await self._optimize_metadata_for_platform(
            content.metadata, specs
        )
        
        # Generate platform-specific tags and descriptions
        platform_tags = await self._generate_platform_tags(content, specs.platform)
        platform_description = await self._generate_platform_description(
            content, specs.platform
        )
        
        return OptimizedContent(
            original_content=content,
            platform=specs.platform,
            optimized_media=optimized_media,
            optimized_metadata=optimized_metadata,
            platform_tags=platform_tags,
            platform_description=platform_description,
            optimization_level=optimization_level,
            created_at=datetime.utcnow()
        )

    async def _execute_distribution_strategy(
        self,
        optimized_content: Dict[PlatformType, OptimizedContent],
        config: DistributionConfig,
        distribution_id: str,
        user_id: str
    ) -> Dict[PlatformType, DistributionResult]:
        """Execute the chosen distribution strategy"""        
        match config.strategy:
            case DistributionStrategy.IMMEDIATE:
                return await self._execute_immediate_distribution(
                    optimized_content, user_id
                )
            case DistributionStrategy.SCHEDULED:
                return await self._execute_scheduled_distribution(
                    optimized_content, config.custom_schedules, user_id
                )
            case DistributionStrategy.OPTIMIZED_TIMING:
                return await self._execute_optimized_timing_distribution(
                    optimized_content, user_id
                )
            case DistributionStrategy.STAGGERED:
                return await self._execute_staggered_distribution(
                    optimized_content, user_id
                )
            case DistributionStrategy.A_B_TEST:
                return await self._execute_ab_test_distribution(
                    optimized_content, user_id
                )
            case DistributionStrategy.VIRAL_BOOST:
                return await self._execute_viral_boost_distribution(
                    optimized_content, user_id
                )
            case _:
                return await self._execute_immediate_distribution(
                    optimized_content, user_id
                )

    async def _execute_immediate_distribution(
        self,
        optimized_content: Dict[PlatformType, OptimizedContent],
        user_id: str
    ) -> Dict[PlatformType, DistributionResult]:
        """Execute immediate distribution to all platforms"""        distribution_tasks = []
        
        for platform, content in optimized_content.items():
            task = asyncio.create_task(
                self._upload_to_platform(platform, content, user_id)
            )
            distribution_tasks.append((platform, task))
        
        results = {}
        for platform, task in distribution_tasks:
            try:
                result = await task
                results[platform] = result
            except Exception as e:
                self.logger.error(f"Upload to {platform.value} failed: {e}")
                results[platform] = DistributionResult(
                    platform=platform,
                    success=False,
                    error_message=str(e),
                    timestamp=datetime.utcnow()
                )
        
        return results

    async def _upload_to_platform(
        self,
        platform: PlatformType,
        content: OptimizedContent,
        user_id: str
    ) -> DistributionResult:
        """Upload optimized content to specific platform"""        try:
            # Get platform connector
            connector = await self.platform_connector.get_connector(platform)
            
            # Prepare upload data
            upload_data = await self._prepare_upload_data(content, platform)
            
            # Execute upload
            upload_result = await connector.upload_content(upload_data)
            
            # Track upload in database
            await self._track_upload(user_id, platform, content, upload_result)
            
            # Schedule analytics tracking
            await self._schedule_analytics_tracking(platform, upload_result['content_id'])
            
            return DistributionResult(
                platform=platform,
                success=True,
                content_id=upload_result.get('content_id'),
                platform_url=upload_result.get('url'),
                upload_details=upload_result,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to upload to {platform.value}: {e}")
            return DistributionResult(
                platform=platform,
                success=False,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )

    async def get_distribution_status(self, distribution_id: str) -> Dict[str, Any]:
        """Get real-time status of content distribution"""        try:
            # Get distribution from database
            distribution = await self.db_manager.get_distribution(distribution_id)
            
            if not distribution:
                raise ValueError(f"Distribution not found: {distribution_id}")
            
            # Get current status from each platform
            platform_statuses = {}
            for platform_result in distribution['platform_results']:
                platform = PlatformType(platform_result['platform'])
                
                try:
                    connector = await self.platform_connector.get_connector(platform)
                    current_status = await connector.get_content_status(
                        platform_result.get('content_id')
                    )
                    platform_statuses[platform.value] = current_status
                except Exception as e:
                    platform_statuses[platform.value] = {
                        'error': str(e),
                        'last_known_status': platform_result.get('status', 'unknown')
                    }
            
            # Get aggregated analytics if content is published
            analytics = await self._get_distribution_analytics(distribution_id)
            
            return {
                'distribution_id': distribution_id,
                'overall_status': self._calculate_overall_status(platform_statuses),
                'platform_statuses': platform_statuses,
                'analytics': analytics,
                'created_at': distribution['created_at'],
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get distribution status: {e}")
            raise

    async def schedule_content_distribution(
        self,
        content_item: ContentItem,
        schedule: Dict[PlatformType, datetime],
        config: DistributionConfig,
        user_id: str
    ) -> Dict[str, Any]:
        """Schedule content for future distribution"""        try:
            scheduling_id = str(uuid.uuid4())
            
            # Validate schedule times
            await self._validate_schedule_times(schedule)
            
            # Pre-optimize content for all platforms
            optimized_content = await self._optimize_for_platforms(
                content_item,
                list(schedule.keys()),
                config.optimization_level
            )
            
            # Store scheduled distribution
            await self._store_scheduled_distribution(
                scheduling_id, content_item, optimized_content,
                schedule, config, user_id
            )
            
            # Schedule tasks
            for platform, scheduled_time in schedule.items():
                await self._schedule_platform_task(
                    scheduling_id, platform, scheduled_time,
                    optimized_content[platform], user_id
                )
            
            return {
                'scheduling_id': scheduling_id,
                'scheduled_platforms': list(schedule.keys()),
                'schedule_times': {p.value: t.isoformat() for p, t in schedule.items()},
                'status': 'scheduled',
                'created_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to schedule content distribution: {e}")
            raise

    async def cancel_scheduled_distribution(self, scheduling_id: str) -> Dict[str, Any]:
        """Cancel scheduled content distribution"""        try:
            # Get scheduled distribution
            scheduled = await self.db_manager.get_scheduled_distribution(scheduling_id)
            
            if not scheduled:
                raise ValueError(f"Scheduled distribution not found: {scheduling_id}")
            
            # Cancel all platform tasks
            cancellation_results = {}
            for platform_task in scheduled['platform_tasks']:
                platform = PlatformType(platform_task['platform'])
                task_id = platform_task['task_id']
                
                cancelled = await self._cancel_platform_task(task_id)
                cancellation_results[platform.value] = cancelled
            
            # Update database
            await self.db_manager.update_scheduled_distribution_status(
                scheduling_id, 'cancelled'
            )
            
            return {
                'scheduling_id': scheduling_id,
                'status': 'cancelled',
                'cancellation_results': cancellation_results,
                'cancelled_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to cancel scheduled distribution: {e}")
            raise

    async def get_optimal_posting_times(
        self,
        user_id: str,
        platforms: List[PlatformType] = None,
        content_type: ContentType = None
    ) -> Dict[str, Any]:
        """Get AI-recommended optimal posting times for platforms"""        try:
            if platforms is None:
                platforms = list(self.platform_specs.keys())
            
            optimal_times = {}
            
            for platform in platforms:
                # Analyze historical performance
                historical_data = await self._get_historical_performance(
                    user_id, platform, content_type
                )
                
                # Analyze audience activity patterns
                audience_patterns = await self._analyze_audience_patterns(
                    user_id, platform
                )
                
                # Analyze competition timing
                competition_data = await self._analyze_competition_timing(
                    user_id, platform
                )
                
                # Generate optimal times using AI
                platform_optimal_times = await self._calculate_optimal_times(
                    historical_data, audience_patterns, competition_data
                )
                
                optimal_times[platform.value] = platform_optimal_times
            
            # Cross-platform optimization
            cross_platform_recommendations = await self._optimize_cross_platform_timing(
                optimal_times
            )
            
            return {
                'user_id': user_id,
                'platform_optimal_times': optimal_times,
                'cross_platform_recommendations': cross_platform_recommendations,
                'confidence_scores': await self._calculate_timing_confidence(optimal_times),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get optimal posting times: {e}")
            raise

    async def shutdown(self):
        """Graceful shutdown of content distributor"""        try:
            self.logger.info("Shutting down Content Distributor...")
            
            # Stop background tasks
            for task in getattr(self, '_background_tasks', []):
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Shutdown AI services
            await self.ai_optimizer.shutdown()
            await self.image_processor.shutdown()
            await self.video_processor.shutdown()
            await self.audio_processor.shutdown()
            
            # Shutdown other services
            await self.content_protection.shutdown()
            await self.seo_optimizer.shutdown()
            await self.translation_service.shutdown()
            
            # Cleanup temporary files
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            self.logger.info("Content Distributor shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during Content Distributor shutdown: {e}")


class MultiPlatformPublisher:
    """    Multi-Platform Publisher - High-level publishing interface
    
    Provides simplified interface for common publishing scenarios
    with intelligent defaults and automated optimization.
    """    
    def __init__(self, content_distributor: ContentDistributor):
        self.content_distributor = content_distributor
        self.logger = logging.getLogger(f"{__name__}.MultiPlatformPublisher")

    async def publish_music_release(
        self,
        audio_file: str,
        metadata: Dict[str, Any],
        user_id: str,
        platforms: List[PlatformType] = None
    ) -> Dict[str, Any]:
        """Publish music release across streaming platforms"""        if platforms is None:
            platforms = [
                PlatformType.SPOTIFY,
                PlatformType.APPLE_MUSIC,
                PlatformType.YOUTUBE,
                PlatformType.SOUNDCLOUD
            ]
        
        # Create content item for music
        content_item = ContentItem(
            content_type=ContentType.AUDIO,
            media_files=[MediaFile(file_path=audio_file)],
            metadata=ContentMetadata(**metadata)
        )
        
        # Configure for music distribution
        config = DistributionConfig(
            target_platforms=platforms,
            optimization_level=OptimizationLevel.ENTERPRISE,
            strategy=DistributionStrategy.OPTIMIZED_TIMING,
            enable_content_protection=True,
            monetization_settings={'enable_revenue_tracking': True}
        )
        
        return await self.content_distributor.distribute_content(
            content_item, config, user_id
        )

    async def publish_video_content(
        self,
        video_file: str,
        metadata: Dict[str, Any],
        user_id: str,
        platforms: List[PlatformType] = None
    ) -> Dict[str, Any]:
        """Publish video content across video platforms"""        if platforms is None:
            platforms = [
                PlatformType.YOUTUBE,
                PlatformType.TIKTOK,
                PlatformType.INSTAGRAM,
                PlatformType.FACEBOOK
            ]
        
        content_item = ContentItem(
            content_type=ContentType.VIDEO,
            media_files=[MediaFile(file_path=video_file)],
            metadata=ContentMetadata(**metadata)
        )
        
        config = DistributionConfig(
            target_platforms=platforms,
            optimization_level=OptimizationLevel.ADVANCED,
            strategy=DistributionStrategy.STAGGERED,
            enable_ai_enhancement=True
        )
        
        return await self.content_distributor.distribute_content(
            content_item, config, user_id
        )

    async def publish_social_media_post(
        self,
        content: Dict[str, Any],
        user_id: str,
        platforms: List[PlatformType] = None
    ) -> Dict[str, Any]:
        """Publish social media post across platforms"""        if platforms is None:
            platforms = [
                PlatformType.INSTAGRAM,
                PlatformType.TWITTER,
                PlatformType.FACEBOOK,
                PlatformType.LINKEDIN
            ]
        
        # Determine content type
        content_type = ContentType.IMAGE if 'image' in content else ContentType.TEXT
        
        content_item = ContentItem(
            content_type=content_type,
            media_files=[MediaFile(file_path=content.get('image'))] if content.get('image') else [],
            metadata=ContentMetadata(
                title=content.get('title', ''),
                description=content.get('description', ''),
                tags=content.get('tags', [])
            )
        )
        
        config = DistributionConfig(
            target_platforms=platforms,
            optimization_level=OptimizationLevel.STANDARD,
            strategy=DistributionStrategy.IMMEDIATE,
            enable_seo_optimization=True
        )
        
        return await self.content_distributor.distribute_content(
            content_item, config, user_id
        )

    async def schedule_content_series(
        self,
        content_series: List[Dict[str, Any]],
        schedule_pattern: str,
        user_id: str,
        platforms: List[PlatformType] = None
    ) -> Dict[str, Any]:
        """Schedule a series of content with intelligent timing"""        scheduling_results = []
        
        # Generate optimal schedule for the series
        optimal_schedule = await self._generate_series_schedule(
            content_series, schedule_pattern, platforms
        )
        
        for i, content_data in enumerate(content_series):
            content_item = self._create_content_item_from_data(content_data)
            platform_schedule = optimal_schedule[i]
            
            config = DistributionConfig(
                target_platforms=platforms or list(platform_schedule.keys()),
                strategy=DistributionStrategy.SCHEDULED,
                custom_schedules=platform_schedule
            )
            
            result = await self.content_distributor.schedule_content_distribution(
                content_item, platform_schedule, config, user_id
            )
            
            scheduling_results.append(result)
        
        return {
            'series_id': str(uuid.uuid4()),
            'total_content_items': len(content_series),
            'scheduling_results': scheduling_results,
            'series_schedule': optimal_schedule,
            'created_at': datetime.utcnow().isoformat()
        }
