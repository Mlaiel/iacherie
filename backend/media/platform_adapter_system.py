"""Platform Adapter System - Multi-Platform Content Adaptation

Enterprise-grade content adaptation system for optimizing media content
across different social media platforms and distribution channels.

Author: Fahed Mlaiel (mlaiel@live.de)  
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
import hashlib
import uuid

# Multimedia processing imports with graceful fallbacks
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    logging.warning("OpenCV not available - using basic image processing")

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logging.warning("PIL not available - using fallback image handling")

try:
    import ffmpeg
    HAS_FFMPEG = True
except ImportError:
    HAS_FFMPEG = False
    logging.warning("FFmpeg not available - using basic video processing")

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    logging.warning("Librosa not available - using basic audio processing")


class PlatformType(Enum):
    """Supported platform types for content adaptation"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    DISCORD = "discord"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    GENERIC = "generic"


class ContentFormat(Enum):
    """Content format types"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    STORY = "story"
    POST = "post"
    REEL = "reel"
    SHORT = "short"
    LIVE = "live"


@dataclass
class PlatformSpecs:
    """Platform-specific content specifications"""
    name: str
    platform_type: PlatformType
    video_specs: Dict[str, Any] = field(default_factory=dict)
    audio_specs: Dict[str, Any] = field(default_factory=dict)
    image_specs: Dict[str, Any] = field(default_factory=dict)
    text_specs: Dict[str, Any] = field(default_factory=dict)
    aspect_ratios: List[str] = field(default_factory=list)
    max_file_size: int = 100  # MB
    max_duration: int = 3600  # seconds
    supported_formats: List[str] = field(default_factory=list)
    metadata_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdaptationResult:
    """Result of content adaptation process"""
    platform: PlatformType
    original_file: str
    adapted_file: str
    format_type: ContentFormat
    adaptation_stats: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    file_size: int = 0
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AdaptationJob:
    """Content adaptation job configuration"""
    job_id: str
    source_file: str
    target_platforms: List[PlatformType]
    content_format: ContentFormat
    quality_preference: str = "balanced"  # high, balanced, fast
    custom_specs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10 priority scale
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    results: List[AdaptationResult] = field(default_factory=list)


class PlatformAdapterSystem:
    """Enterprise platform adaptation system for multi-platform content optimization"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Platform specifications database
        self.platform_specs = self._initialize_platform_specs()
        
        # Active adaptation jobs
        self.active_jobs: Dict[str, AdaptationJob] = {}
        
        # Statistics tracking
        self.adaptation_stats = {
            "total_adaptations": 0,
            "successful_adaptations": 0,
            "failed_adaptations": 0,
            "platforms_processed": {},
            "average_processing_time": 0.0,
            "total_size_processed": 0
        }
        
        self.logger.info("Platform Adapter System initialized")
    
    def _initialize_platform_specs(self) -> Dict[PlatformType, PlatformSpecs]:
        """Initialize platform-specific content specifications"""
        specs = {}
        
        # YouTube specifications
        specs[PlatformType.YOUTUBE] = PlatformSpecs(
            name="YouTube",
            platform_type=PlatformType.YOUTUBE,
            video_specs={
                "resolution": ["3840x2160", "1920x1080", "1280x720"],
                "fps": [60, 30, 24],
                "bitrate": {"4k": 35000, "1080p": 8000, "720p": 5000},
                "codec": ["h264", "h265"],
                "container": ["mp4", "mov"]
            },
            audio_specs={
                "sample_rate": [48000, 44100],
                "bitrate": [320, 256, 192],
                "channels": [2, 1],
                "codec": ["aac", "mp3"]
            },
            image_specs={
                "thumbnail": {"width": 1280, "height": 720},
                "format": ["jpg", "png"],
                "quality": 90
            },
            aspect_ratios=["16:9", "9:16", "1:1"],
            max_file_size=256000,  # 256GB
            max_duration=43200,     # 12 hours
            supported_formats=["mp4", "mov", "avi", "wmv", "flv"]
        )
        
        # Instagram specifications
        specs[PlatformType.INSTAGRAM] = PlatformSpecs(
            name="Instagram",
            platform_type=PlatformType.INSTAGRAM,
            video_specs={
                "feed": {"resolution": "1080x1080", "max_duration": 60},
                "story": {"resolution": "1080x1920", "max_duration": 15},
                "reel": {"resolution": "1080x1920", "max_duration": 90},
                "igtv": {"resolution": "1080x1920", "max_duration": 3600},
                "fps": 30,
                "bitrate": 3500,
                "codec": "h264"
            },
            image_specs={
                "feed": {"width": 1080, "height": 1080},
                "story": {"width": 1080, "height": 1920},
                "format": ["jpg", "png"],
                "quality": 85
            },
            aspect_ratios=["1:1", "9:16", "4:5"],
            max_file_size=100,
            max_duration=3600,
            supported_formats=["mp4", "mov"]
        )
        
        # TikTok specifications
        specs[PlatformType.TIKTOK] = PlatformSpecs(
            name="TikTok",
            platform_type=PlatformType.TIKTOK,
            video_specs={
                "resolution": "1080x1920",
                "fps": [30, 25],
                "bitrate": 2000,
                "codec": "h264",
                "max_duration": 180
            },
            audio_specs={
                "sample_rate": 44100,
                "bitrate": 128,
                "codec": "aac"
            },
            aspect_ratios=["9:16"],
            max_file_size=287,
            max_duration=180,
            supported_formats=["mp4", "mov"]
        )
        
        # Add more platform specifications as needed
        self._add_additional_platform_specs(specs)
        
        return specs
    
    def _add_additional_platform_specs(self, specs: Dict[PlatformType, PlatformSpecs]) -> None:
        """Add additional platform specifications"""
        
        # Facebook specifications
        specs[PlatformType.FACEBOOK] = PlatformSpecs(
            name="Facebook",
            platform_type=PlatformType.FACEBOOK,
            video_specs={
                "resolution": ["1920x1080", "1280x720"],
                "fps": 30,
                "bitrate": 4000,
                "codec": "h264",
                "max_duration": 14400  # 4 hours
            },
            aspect_ratios=["16:9", "9:16", "1:1"],
            max_file_size=10240,  # 10GB
            max_duration=14400,
            supported_formats=["mp4", "mov"]
        )
        
        # Twitter specifications
        specs[PlatformType.TWITTER] = PlatformSpecs(
            name="Twitter",
            platform_type=PlatformType.TWITTER,
            video_specs={
                "resolution": ["1920x1080", "1280x720"],
                "fps": 30,
                "bitrate": 5000,
                "codec": "h264",
                "max_duration": 140
            },
            aspect_ratios=["16:9", "1:1"],
            max_file_size=512,
            max_duration=140,
            supported_formats=["mp4", "mov"]
        )
        
        # LinkedIn specifications  
        specs[PlatformType.LINKEDIN] = PlatformSpecs(
            name="LinkedIn",
            platform_type=PlatformType.LINKEDIN,
            video_specs={
                "resolution": ["1920x1080", "1280x720"],
                "fps": 30,
                "bitrate": 5000,
                "codec": "h264",
                "max_duration": 600  # 10 minutes
            },
            aspect_ratios=["16:9", "1:1"],
            max_file_size=5120,  # 5GB
            max_duration=600,
            supported_formats=["mp4", "mov", "avi"]
        )
    
    async def create_adaptation_job(
        self,
        source_file: str,
        target_platforms: List[PlatformType],
        content_format: ContentFormat,
        **kwargs
    ) -> str:
        """Create a new content adaptation job"""
        
        job_id = str(uuid.uuid4())
        
        job = AdaptationJob(
            job_id=job_id,
            source_file=source_file,
            target_platforms=target_platforms,
            content_format=content_format,
            quality_preference=kwargs.get("quality_preference", "balanced"),
            custom_specs=kwargs.get("custom_specs", {}),
            metadata=kwargs.get("metadata", {}),
            priority=kwargs.get("priority", 5)
        )
        
        self.active_jobs[job_id] = job
        
        self.logger.info(f"Created adaptation job {job_id} for {len(target_platforms)} platforms")
        
        return job_id
    
    async def process_adaptation_job(self, job_id: str) -> List[AdaptationResult]:
        """Process a content adaptation job"""
        
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.active_jobs[job_id]
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Processing adaptation job {job_id}")
            
            # Validate source file
            if not Path(job.source_file).exists():
                raise FileNotFoundError(f"Source file not found: {job.source_file}")
            
            # Process each target platform
            for platform in job.target_platforms:
                try:
                    result = await self._adapt_content_for_platform(
                        job.source_file,
                        platform,
                        job.content_format,
                        job.quality_preference,
                        job.custom_specs
                    )
                    
                    if result:
                        job.results.append(result)
                        self.adaptation_stats["successful_adaptations"] += 1
                        
                        # Update platform stats
                        platform_name = platform.value
                        if platform_name not in self.adaptation_stats["platforms_processed"]:
                            self.adaptation_stats["platforms_processed"][platform_name] = 0
                        self.adaptation_stats["platforms_processed"][platform_name] += 1
                        
                except Exception as e:
                    self.logger.error(f"Failed to adapt content for {platform.value}: {str(e)}")
                    self.adaptation_stats["failed_adaptations"] += 1
            
            # Update job completion
            job.completed_at = datetime.now()
            processing_time = (job.completed_at - start_time).total_seconds()
            
            # Update statistics
            self.adaptation_stats["total_adaptations"] += 1
            self.adaptation_stats["average_processing_time"] = (
                (self.adaptation_stats["average_processing_time"] * 
                 (self.adaptation_stats["total_adaptations"] - 1) + processing_time) /
                self.adaptation_stats["total_adaptations"]
            )
            
            self.logger.info(
                f"Completed adaptation job {job_id} in {processing_time:.2f}s "
                f"with {len(job.results)} successful adaptations"
            )
            
            return job.results
            
        except Exception as e:
            self.logger.error(f"Error processing adaptation job {job_id}: {str(e)}")
            self.adaptation_stats["failed_adaptations"] += 1
            raise
    
    async def _adapt_content_for_platform(
        self,
        source_file: str,
        platform: PlatformType,
        content_format: ContentFormat,
        quality_preference: str,
        custom_specs: Dict[str, Any]
    ) -> Optional[AdaptationResult]:
        """Adapt content for a specific platform"""
        
        if platform not in self.platform_specs:
            self.logger.warning(f"No specifications found for platform: {platform.value}")
            return None
        
        specs = self.platform_specs[platform]
        
        # Generate output filename
        source_path = Path(source_file)
        output_file = f"{source_path.stem}_{platform.value}_{content_format.value}{source_path.suffix}"
        output_path = source_path.parent / output_file
        
        try:
            # Adapt based on content format
            if content_format == ContentFormat.VIDEO:
                return await self._adapt_video_content(
                    source_file, str(output_path), specs, quality_preference, custom_specs
                )
            elif content_format == ContentFormat.AUDIO:
                return await self._adapt_audio_content(
                    source_file, str(output_path), specs, quality_preference, custom_specs
                )
            elif content_format == ContentFormat.IMAGE:
                return await self._adapt_image_content(
                    source_file, str(output_path), specs, quality_preference, custom_specs
                )
            else:
                self.logger.warning(f"Unsupported content format: {content_format.value}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error adapting content for {platform.value}: {str(e)}")
            return None
    
    async def _adapt_video_content(
        self,
        source_file: str,
        output_file: str,
        specs: PlatformSpecs,
        quality_preference: str,
        custom_specs: Dict[str, Any]
    ) -> AdaptationResult:
        """Adapt video content for platform specifications"""
        
        if not HAS_FFMPEG:
            # Fallback: basic file copy with metadata
            self.logger.warning("FFmpeg not available - using basic video processing")
            import shutil
            shutil.copy2(source_file, output_file)
            
            return AdaptationResult(
                platform=specs.platform_type,
                original_file=source_file,
                adapted_file=output_file,
                format_type=ContentFormat.VIDEO,
                adaptation_stats={"method": "basic_copy"},
                quality_score=0.7,
                file_size=Path(output_file).stat().st_size
            )
        
        try:
            # Get video specifications
            video_specs = specs.video_specs
            
            # Determine target resolution
            if isinstance(video_specs.get("resolution"), list):
                target_resolution = video_specs["resolution"][0]
            else:
                target_resolution = video_specs.get("resolution", "1920x1080")
            
            # Parse resolution
            width, height = map(int, target_resolution.split('x'))
            
            # Build FFmpeg command
            stream = ffmpeg.input(source_file)
            
            # Video processing
            video_args = {
                'vcodec': video_specs.get('codec', 'h264'),
                'video_bitrate': video_specs.get('bitrate', 5000),
                'r': video_specs.get('fps', 30),
                's': target_resolution
            }
            
            # Audio processing
            audio_args = {
                'acodec': 'aac',
                'audio_bitrate': '128k',
                'ar': 44100
            }
            
            # Apply quality preferences
            if quality_preference == "high":
                video_args['crf'] = 18
                video_args['preset'] = 'slow'
            elif quality_preference == "fast":
                video_args['crf'] = 28
                video_args['preset'] = 'ultrafast'
            else:  # balanced
                video_args['crf'] = 23
                video_args['preset'] = 'medium'
            
            # Apply custom specifications
            video_args.update(custom_specs.get('video', {}))
            audio_args.update(custom_specs.get('audio', {}))
            
            # Execute FFmpeg
            out = ffmpeg.output(stream, output_file, **video_args, **audio_args)
            ffmpeg.run(out, overwrite_output=True, quiet=True)
            
            # Calculate file size and quality score
            output_size = Path(output_file).stat().st_size
            original_size = Path(source_file).stat().st_size
            compression_ratio = output_size / original_size if original_size > 0 else 1.0
            
            # Simple quality score based on compression and specs matching
            quality_score = min(1.0, 0.8 + (0.2 * compression_ratio))
            
            return AdaptationResult(
                platform=specs.platform_type,
                original_file=source_file,
                adapted_file=output_file,
                format_type=ContentFormat.VIDEO,
                adaptation_stats={
                    "target_resolution": target_resolution,
                    "compression_ratio": compression_ratio,
                    "processing_method": "ffmpeg",
                    "video_codec": video_args.get('vcodec'),
                    "audio_codec": audio_args.get('acodec')
                },
                quality_score=quality_score,
                file_size=output_size
            )
            
        except Exception as e:
            self.logger.error(f"Error in video adaptation: {str(e)}")
            raise
    
    async def _adapt_audio_content(
        self,
        source_file: str,
        output_file: str,
        specs: PlatformSpecs,
        quality_preference: str,
        custom_specs: Dict[str, Any]
    ) -> AdaptationResult:
        """Adapt audio content for platform specifications"""
        
        if not HAS_LIBROSA:
            # Fallback: basic file copy
            self.logger.warning("Librosa not available - using basic audio processing")
            import shutil
            shutil.copy2(source_file, output_file)
            
            return AdaptationResult(
                platform=specs.platform_type,
                original_file=source_file,
                adapted_file=output_file,
                format_type=ContentFormat.AUDIO,
                adaptation_stats={"method": "basic_copy"},
                quality_score=0.7,
                file_size=Path(output_file).stat().st_size
            )
        
        try:
            # Get audio specifications
            audio_specs = specs.audio_specs
            
            # Load audio with librosa
            y, sr = librosa.load(source_file, sr=audio_specs.get('sample_rate', 44100))
            
            # Apply audio processing based on platform requirements
            target_bitrate = audio_specs.get('bitrate', 192)
            target_channels = audio_specs.get('channels', 2)
            
            # Simple quality adjustment
            if quality_preference == "high":
                target_bitrate = max(target_bitrate, 256)
            elif quality_preference == "fast":
                target_bitrate = min(target_bitrate, 128)
            
            # Save adapted audio (basic implementation)
            # In a real implementation, you would use more sophisticated audio processing
            import soundfile as sf
            sf.write(output_file, y, sr)
            
            output_size = Path(output_file).stat().st_size
            quality_score = 0.85  # Placeholder quality score
            
            return AdaptationResult(
                platform=specs.platform_type,
                original_file=source_file,
                adapted_file=output_file,
                format_type=ContentFormat.AUDIO,
                adaptation_stats={
                    "sample_rate": sr,
                    "bitrate": target_bitrate,
                    "channels": target_channels,
                    "processing_method": "librosa"
                },
                quality_score=quality_score,
                file_size=output_size,
                duration=len(y) / sr
            )
            
        except Exception as e:
            self.logger.error(f"Error in audio adaptation: {str(e)}")
            # Fallback to basic copy
            import shutil
            shutil.copy2(source_file, output_file)
            
            return AdaptationResult(
                platform=specs.platform_type,
                original_file=source_file,
                adapted_file=output_file,
                format_type=ContentFormat.AUDIO,
                adaptation_stats={"method": "fallback_copy", "error": str(e)},
                quality_score=0.5,
                file_size=Path(output_file).stat().st_size
            )
    
    async def _adapt_image_content(
        self,
        source_file: str,
        output_file: str,
        specs: PlatformSpecs,
        quality_preference: str,
        custom_specs: Dict[str, Any]
    ) -> AdaptationResult:
        """Adapt image content for platform specifications"""
        
        if not HAS_PIL:
            # Fallback: basic file copy
            self.logger.warning("PIL not available - using basic image processing")
            import shutil
            shutil.copy2(source_file, output_file)
            
            return AdaptationResult(
                platform=specs.platform_type,
                original_file=source_file,
                adapted_file=output_file,
                format_type=ContentFormat.IMAGE,
                adaptation_stats={"method": "basic_copy"},
                quality_score=0.7,
                file_size=Path(output_file).stat().st_size
            )
        
        try:
            # Get image specifications
            image_specs = specs.image_specs
            
            # Open and process image
            with Image.open(source_file) as img:
                # Determine target size
                if 'feed' in image_specs:
                    target_width = image_specs['feed']['width']
                    target_height = image_specs['feed']['height']
                elif 'width' in image_specs and 'height' in image_specs:
                    target_width = image_specs['width']
                    target_height = image_specs['height']
                else:
                    target_width, target_height = img.size
                
                # Resize image
                img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Convert format if needed
                target_format = image_specs.get('format', ['jpg'])[0].upper()
                if target_format == 'JPG':
                    target_format = 'JPEG'
                
                # Determine quality
                quality = image_specs.get('quality', 85)
                if quality_preference == "high":
                    quality = min(quality + 10, 95)
                elif quality_preference == "fast":
                    quality = max(quality - 15, 60)
                
                # Save adapted image
                save_kwargs = {'format': target_format}
                if target_format == 'JPEG':
                    save_kwargs['quality'] = quality
                    save_kwargs['optimize'] = True
                
                img_resized.save(output_file, **save_kwargs)
            
            output_size = Path(output_file).stat().st_size
            original_size = Path(source_file).stat().st_size
            compression_ratio = output_size / original_size if original_size > 0 else 1.0
            
            quality_score = min(1.0, 0.75 + (0.25 * compression_ratio))
            
            return AdaptationResult(
                platform=specs.platform_type,
                original_file=source_file,
                adapted_file=output_file,
                format_type=ContentFormat.IMAGE,
                adaptation_stats={
                    "target_size": f"{target_width}x{target_height}",
                    "compression_ratio": compression_ratio,
                    "format": target_format,
                    "quality": quality,
                    "processing_method": "PIL"
                },
                quality_score=quality_score,
                file_size=output_size
            )
            
        except Exception as e:
            self.logger.error(f"Error in image adaptation: {str(e)}")
            raise
    
    def get_platform_specifications(self, platform: PlatformType) -> Optional[PlatformSpecs]:
        """Get specifications for a specific platform"""
        return self.platform_specs.get(platform)
    
    def get_supported_platforms(self) -> List[PlatformType]:
        """Get list of supported platforms"""
        return list(self.platform_specs.keys())
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an adaptation job"""
        if job_id not in self.active_jobs:
            return None
        
        job = self.active_jobs[job_id]
        
        return {
            "job_id": job.job_id,
            "status": "completed" if job.completed_at else "processing",
            "source_file": job.source_file,
            "target_platforms": [p.value for p in job.target_platforms],
            "content_format": job.content_format.value,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "results_count": len(job.results),
            "results": [
                {
                    "platform": r.platform.value,
                    "adapted_file": r.adapted_file,
                    "quality_score": r.quality_score,
                    "file_size": r.file_size
                } for r in job.results
            ]
        }
    
    def get_adaptation_statistics(self) -> Dict[str, Any]:
        """Get system adaptation statistics"""
        return {
            **self.adaptation_stats,
            "active_jobs": len(self.active_jobs),
            "supported_platforms": len(self.platform_specs),
            "platform_list": [p.value for p in self.platform_specs.keys()]
        }
    
    async def bulk_adapt_content(
        self,
        source_files: List[str],
        target_platforms: List[PlatformType],
        content_format: ContentFormat,
        **kwargs
    ) -> List[str]:
        """Bulk adapt multiple content files"""
        
        job_ids = []
        
        for source_file in source_files:
            try:
                job_id = await self.create_adaptation_job(
                    source_file=source_file,
                    target_platforms=target_platforms,
                    content_format=content_format,
                    **kwargs
                )
                job_ids.append(job_id)
                
            except Exception as e:
                self.logger.error(f"Failed to create adaptation job for {source_file}: {str(e)}")
        
        # Process all jobs concurrently
        tasks = [self.process_adaptation_job(job_id) for job_id in job_ids]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return job_ids
    
    def cleanup_completed_jobs(self, older_than_hours: int = 24) -> int:
        """Clean up completed jobs older than specified hours"""
        
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        jobs_to_remove = []
        
        for job_id, job in self.active_jobs.items():
            if job.completed_at and job.completed_at < cutoff_time:
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.active_jobs[job_id]
        
        self.logger.info(f"Cleaned up {len(jobs_to_remove)} completed jobs")
        
        return len(jobs_to_remove)


# Global instance for easy access
_platform_adapter_system = None

def get_platform_adapter_system(config: Optional[Dict[str, Any]] = None) -> PlatformAdapterSystem:
    """Get or create global platform adapter system instance"""
    global _platform_adapter_system
    
    if _platform_adapter_system is None:
        _platform_adapter_system = PlatformAdapterSystem(config)
    
    return _platform_adapter_system


# Example usage and testing
if __name__ == "__main__":
    async def example_usage():
        """Example usage of the Platform Adapter System"""
        
        # Initialize the system
        adapter = get_platform_adapter_system()
        
        # Example: Adapt a video for multiple platforms
        platforms = [PlatformType.YOUTUBE, PlatformType.INSTAGRAM, PlatformType.TIKTOK]
        
        job_id = await adapter.create_adaptation_job(
            source_file="example_video.mp4",
            target_platforms=platforms,
            content_format=ContentFormat.VIDEO,
            quality_preference="balanced"
        )
        
        print(f"Created adaptation job: {job_id}")
        
        # Process the job
        results = await adapter.process_adaptation_job(job_id)
        
        print(f"Adaptation completed with {len(results)} results:")
        for result in results:
            print(f"- {result.platform.value}: {result.adapted_file} "
                  f"(Quality: {result.quality_score:.2f})")
        
        # Get statistics
        stats = adapter.get_adaptation_statistics()
        print(f"System statistics: {json.dumps(stats, indent=2)}")
    
    # Run example if this file is executed directly
    asyncio.run(example_usage())