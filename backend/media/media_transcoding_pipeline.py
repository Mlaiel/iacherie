"""Media Transcoding Pipeline - Advanced Media Processing & Conversion Engine
========================================================================

Advanced transcoding pipeline providing comprehensive media format conversion,
quality optimization, batch processing, and intelligent codec selection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary transcoding system contains advanced algorithms and trade secrets
belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering  
- Commercial use without explicit written permission
- Algorithm extraction or transcoding technology appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import json
import logging
import uuid
import os
import shutil
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from pathlib import Path
import hashlib
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Media processing imports with graceful fallbacks
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    logging.warning("OpenCV not available - using basic video processing")

try:
    from PIL import Image, ImageOps, ImageEnhance
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logging.warning("PIL not available - using basic image processing")

try:
    import librosa
    import soundfile as sf
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    logging.warning("Librosa not available - using basic audio processing")

try:
    import subprocess
    HAS_SUBPROCESS = True
except ImportError:
    HAS_SUBPROCESS = False
    logging.warning("Subprocess not available - limited transcoding capabilities")

logger = logging.getLogger(__name__)


class MediaType(Enum):
    """Media types for transcoding"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    ARCHIVE = "archive"


class TranscodingStatus(Enum):
    """Transcoding job status"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class Quality(Enum):
    """Quality presets"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"
    LOSSLESS = "lossless"
    CUSTOM = "custom"


class VideoCodec(Enum):
    """Video codecs"""
    H264 = "h264"
    H265 = "h265"
    VP9 = "vp9"
    AV1 = "av1"
    MPEG4 = "mpeg4"
    PRORES = "prores"


class AudioCodec(Enum):
    """Audio codecs"""
    AAC = "aac"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    OPUS = "opus"
    PCM = "pcm"


@dataclass
class TranscodingConfig:
    """Transcoding pipeline configuration"""
    # General settings
    max_concurrent_jobs: int = 4
    temp_directory: str = "/tmp/transcoding"
    output_directory: str = "./transcoded"
    cleanup_temp_files: bool = True
    
    # Quality settings
    preserve_metadata: bool = True
    auto_quality_selection: bool = True
    
    # Performance settings
    use_gpu_acceleration: bool = True
    thread_count: int = 0  # 0 = auto-detect
    memory_limit_gb: float = 8.0
    
    # Progress tracking
    progress_reporting: bool = True
    progress_interval_seconds: int = 5


@dataclass
class MediaInfo:
    """Media file information"""
    file_path: str
    media_type: MediaType
    file_size: int
    duration: Optional[float] = None
    
    # Video properties
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    video_codec: Optional[str] = None
    video_bitrate: Optional[int] = None
    
    # Audio properties
    audio_codec: Optional[str] = None
    audio_bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    
    # Image properties
    color_space: Optional[str] = None
    bit_depth: Optional[int] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TranscodingProfile:
    """Transcoding profile specification"""
    profile_id: str
    name: str
    description: str
    media_type: MediaType
    
    # Output format
    output_format: str
    output_extension: str
    
    # Video settings
    video_codec: Optional[VideoCodec] = None
    video_bitrate: Optional[int] = None
    video_quality: Optional[Quality] = None
    resolution: Optional[Tuple[int, int]] = None
    fps: Optional[float] = None
    
    # Audio settings
    audio_codec: Optional[AudioCodec] = None
    audio_bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    
    # Advanced settings
    two_pass_encoding: bool = False
    use_hardware_acceleration: bool = True
    custom_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TranscodingJob:
    """Transcoding job specification"""
    job_id: str
    input_file: str
    output_file: str
    profile: TranscodingProfile
    priority: int = 1  # 1-5 scale
    
    # Job state
    status: TranscodingStatus = TranscodingStatus.PENDING
    progress_percent: float = 0.0
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    output_info: Optional[MediaInfo] = None
    compression_ratio: Optional[float] = None
    processing_time: Optional[float] = None
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class MediaAnalyzer:
    """Media file analysis and information extraction"""
    
    def __init__(self) -> None:
        self.supported_video_formats = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        self.supported_audio_formats = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
        self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
        logger.info("🔍 Media Analyzer initialized")
    
    async def analyze_media(self, file_path: str) -> MediaInfo:
        """Analyze media file and extract information"""
        try:
            file_path_obj = Path(file_path)
            file_size = file_path_obj.stat().st_size
            file_extension = file_path_obj.suffix.lower()
            
            # Determine media type
            media_type = self._determine_media_type(file_extension)
            
            # Initialize media info
            media_info = MediaInfo(
                file_path=file_path,
                media_type=media_type,
                file_size=file_size
            )
            
            # Extract format-specific information
            if media_type == MediaType.VIDEO and HAS_OPENCV:
                await self._analyze_video(media_info)
            elif media_type == MediaType.AUDIO and HAS_LIBROSA:
                await self._analyze_audio(media_info)
            elif media_type == MediaType.IMAGE and HAS_PIL:
                await self._analyze_image(media_info)
            
            return media_info
            
        except Exception as e:
            logger.error(f"Media analysis failed for {file_path}: {e}")
            # Return basic info even if analysis fails
            return MediaInfo(
                file_path=file_path,
                media_type=MediaType.VIDEO,  # Default fallback
                file_size=Path(file_path).stat().st_size if Path(file_path).exists() else 0
            )
    
    def _determine_media_type(self, file_extension: str) -> MediaType:
        """Determine media type from file extension"""
        if file_extension in self.supported_video_formats:
            return MediaType.VIDEO
        elif file_extension in self.supported_audio_formats:
            return MediaType.AUDIO
        elif file_extension in self.supported_image_formats:
            return MediaType.IMAGE
        else:
            return MediaType.DOCUMENT  # Default fallback
    
    async def _analyze_video(self, media_info -> None: MediaInfo) -> None:
        """Analyze video file properties"""
        try:
            cap = cv2.VideoCapture(media_info.file_path)
            
            if cap.isOpened():
                # Video properties
                media_info.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                media_info.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                media_info.fps = cap.get(cv2.CAP_PROP_FPS)
                
                # Calculate duration
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                if media_info.fps > 0:
                    media_info.duration = frame_count / media_info.fps
                
                # Try to get codec information
                fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
                codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
                media_info.video_codec = codec
            
            cap.release()
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
    
    async def _analyze_audio(self, media_info -> None: MediaInfo) -> None:
        """Analyze audio file properties"""
        try:
            # Load audio file
            y, sr = librosa.load(media_info.file_path, sr=None)
            
            media_info.duration = librosa.get_duration(y=y, sr=sr)
            media_info.sample_rate = sr
            media_info.channels = 1 if len(y.shape) == 1 else y.shape[0]
            
            # Estimate bitrate (rough calculation)
            if media_info.duration > 0:
                estimated_bitrate = (media_info.file_size * 8) / (media_info.duration * 1000)
                media_info.audio_bitrate = int(estimated_bitrate)
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
    
    async def _analyze_image(self, media_info -> None: MediaInfo) -> None:
        """Analyze image file properties"""
        try:
            with Image.open(media_info.file_path) as img:
                media_info.width = img.width
                media_info.height = img.height
                media_info.color_space = img.mode
                
                # Get bit depth information
                if hasattr(img, 'bits'):
                    media_info.bit_depth = img.bits
                
                # Extract metadata
                if hasattr(img, '_getexif') and img._getexif():
                    media_info.metadata = dict(img._getexif())
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")


class TranscodingEngine:
    """Core transcoding engine for media conversion"""
    
    def __init__(self, config -> None: TranscodingConfig) -> None:
        self.config = config
        self.media_analyzer = MediaAnalyzer()
        
        # Create directories
        Path(self.config.temp_directory).mkdir(parents=True, exist_ok=True)
        Path(self.config.output_directory).mkdir(parents=True, exist_ok=True)
        
        logger.info("⚙️ Transcoding Engine initialized")
    
    async def transcode_video(
        self, 
        input_file: str, 
        output_file: str, 
        profile: TranscodingProfile,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Transcode video file"""
        try:
            if not HAS_SUBPROCESS:
                raise RuntimeError("Subprocess not available for video transcoding")
            
            # Build ffmpeg command
            cmd = await self._build_video_transcode_command(input_file, output_file, profile)
            
            # Execute transcoding
            success = await self._execute_transcode_command(
                cmd, progress_callback, input_file
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Video transcoding failed: {e}")
            return False
    
    async def transcode_audio(
        self, 
        input_file: str, 
        output_file: str, 
        profile: TranscodingProfile,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Transcode audio file"""
        try:
            if HAS_LIBROSA:
                return await self._transcode_audio_librosa(input_file, output_file, profile)
            else:
                return await self._transcode_audio_ffmpeg(input_file, output_file, profile)
            
        except Exception as e:
            logger.error(f"Audio transcoding failed: {e}")
            return False
    
    async def transcode_image(
        self, 
        input_file: str, 
        output_file: str, 
        profile: TranscodingProfile,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Transcode image file"""
        try:
            if not HAS_PIL:
                raise RuntimeError("PIL not available for image transcoding")
            
            with Image.open(input_file) as img:
                # Apply transformations based on profile
                processed_img = await self._process_image(img, profile)
                
                # Save with appropriate settings
                save_kwargs = self._get_image_save_options(profile)
                processed_img.save(output_file, **save_kwargs)
                
                if progress_callback:
                    await progress_callback(100.0)
            
            return True
            
        except Exception as e:
            logger.error(f"Image transcoding failed: {e}")
            return False
    
    async def _build_video_transcode_command(
        self, 
        input_file: str, 
        output_file: str, 
        profile: TranscodingProfile
    ) -> List[str]:
        """Build ffmpeg command for video transcoding"""
        cmd = ['ffmpeg', '-i', input_file]
        
        # Video codec and settings
        if profile.video_codec:
            if profile.video_codec == VideoCodec.H264:
                cmd.extend(['-c:v', 'libx264'])
            elif profile.video_codec == VideoCodec.H265:
                cmd.extend(['-c:v', 'libx265'])
            elif profile.video_codec == VideoCodec.VP9:
                cmd.extend(['-c:v', 'libvpx-vp9'])
            elif profile.video_codec == VideoCodec.AV1:
                cmd.extend(['-c:v', 'libaom-av1'])
        
        # Video bitrate
        if profile.video_bitrate:
            cmd.extend(['-b:v', f'{profile.video_bitrate}k'])
        
        # Resolution
        if profile.resolution:
            width, height = profile.resolution
            cmd.extend(['-s', f'{width}x{height}'])
        
        # Frame rate
        if profile.fps:
            cmd.extend(['-r', str(profile.fps)])
        
        # Audio codec and settings
        if profile.audio_codec:
            if profile.audio_codec == AudioCodec.AAC:
                cmd.extend(['-c:a', 'aac'])
            elif profile.audio_codec == AudioCodec.MP3:
                cmd.extend(['-c:a', 'libmp3lame'])
            elif profile.audio_codec == AudioCodec.OPUS:
                cmd.extend(['-c:a', 'libopus'])
        
        # Audio bitrate
        if profile.audio_bitrate:
            cmd.extend(['-b:a', f'{profile.audio_bitrate}k'])
        
        # Sample rate
        if profile.sample_rate:
            cmd.extend(['-ar', str(profile.sample_rate)])
        
        # Channels
        if profile.channels:
            cmd.extend(['-ac', str(profile.channels)])
        
        # Quality settings
        if profile.video_quality == Quality.LOSSLESS:
            cmd.extend(['-crf', '0'])
        elif profile.video_quality == Quality.HIGH:
            cmd.extend(['-crf', '18'])
        elif profile.video_quality == Quality.MEDIUM:
            cmd.extend(['-crf', '23'])
        elif profile.video_quality == Quality.LOW:
            cmd.extend(['-crf', '28'])
        
        # Hardware acceleration
        if profile.use_hardware_acceleration and self.config.use_gpu_acceleration:
            cmd.extend(['-hwaccel', 'auto'])
        
        # Two-pass encoding
        if profile.two_pass_encoding:
            cmd.extend(['-pass', '2'])
        
        # Output file
        cmd.extend(['-y', output_file])  # -y to overwrite
        
        return cmd
    
    async def _execute_transcode_command(
        self, 
        cmd: List[str], 
        progress_callback: Optional[Callable],
        input_file: str
    ) -> bool:
        """Execute transcoding command and track progress"""
        try:
            # Get input duration for progress calculation
            input_info = await self.media_analyzer.analyze_media(input_file)
            duration = input_info.duration or 0
            
            # Start subprocess
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Monitor progress
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                
                if output and progress_callback and duration > 0:
                    # Parse ffmpeg progress (simplified)
                    if 'time=' in output:
                        try:
                            time_str = output.split('time=')[1].split()[0]
                            time_parts = time_str.split(':')
                            if len(time_parts) == 3:
                                hours, minutes, seconds = map(float, time_parts)
                                current_time = hours * 3600 + minutes * 60 + seconds
                                progress = min(100.0, (current_time / duration) * 100)
                                await progress_callback(progress)
                        except:
                            pass
            
            # Check result
            return_code = process.poll()
            
            if return_code == 0:
                if progress_callback:
                    await progress_callback(100.0)
                return True
            else:
                error_output = process.stderr.read()
                logger.error(f"Transcoding failed with code {return_code}: {error_output}")
                return False
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return False
    
    async def _transcode_audio_librosa(
        self, 
        input_file: str, 
        output_file: str, 
        profile: TranscodingProfile
    ) -> bool:
        """Transcode audio using librosa"""
        try:
            # Load audio
            y, sr = librosa.load(input_file, sr=profile.sample_rate)
            
            # Apply audio processing based on profile
            if profile.channels == 1 and len(y.shape) > 1:
                y = librosa.to_mono(y)
            
            # Save audio
            sf.write(output_file, y, sr)
            
            return True
            
        except Exception as e:
            logger.error(f"Librosa audio transcoding failed: {e}")
            return False
    
    async def _transcode_audio_ffmpeg(
        self, 
        input_file: str, 
        output_file: str, 
        profile: TranscodingProfile
    ) -> bool:
        """Transcode audio using ffmpeg"""
        cmd = ['ffmpeg', '-i', input_file]
        
        # Audio codec
        if profile.audio_codec == AudioCodec.MP3:
            cmd.extend(['-c:a', 'libmp3lame'])
        elif profile.audio_codec == AudioCodec.AAC:
            cmd.extend(['-c:a', 'aac'])
        elif profile.audio_codec == AudioCodec.FLAC:
            cmd.extend(['-c:a', 'flac'])
        
        # Bitrate
        if profile.audio_bitrate:
            cmd.extend(['-b:a', f'{profile.audio_bitrate}k'])
        
        # Sample rate
        if profile.sample_rate:
            cmd.extend(['-ar', str(profile.sample_rate)])
        
        # Channels
        if profile.channels:
            cmd.extend(['-ac', str(profile.channels)])
        
        cmd.extend(['-y', output_file])
        
        return await self._execute_transcode_command(cmd, None, input_file)
    
    async def _process_image(self, img: Image.Image, profile: TranscodingProfile) -> Image.Image:
        """Process image based on profile settings"""
        processed_img = img.copy()
        
        # Resize if resolution specified
        if profile.resolution:
            width, height = profile.resolution
            processed_img = processed_img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Convert color space if needed
        if profile.output_format.lower() == 'jpeg' and processed_img.mode == 'RGBA':
            # Convert RGBA to RGB for JPEG
            background = Image.new('RGB', processed_img.size, (255, 255, 255))
            background.paste(processed_img, mask=processed_img.split()[-1])
            processed_img = background
        
        return processed_img
    
    def _get_image_save_options(self, profile: TranscodingProfile) -> Dict[str, Any]:
        """Get image save options based on profile"""
        options = {}
        
        if profile.output_format.lower() in ['jpeg', 'jpg']:
            if profile.video_quality == Quality.HIGH:
                options['quality'] = 95
            elif profile.video_quality == Quality.MEDIUM:
                options['quality'] = 85
            elif profile.video_quality == Quality.LOW:
                options['quality'] = 70
            else:
                options['quality'] = 90
            
            options['optimize'] = True
        
        elif profile.output_format.lower() == 'png':
            options['optimize'] = True
            if profile.video_quality == Quality.LOW:
                options['compress_level'] = 9
        
        elif profile.output_format.lower() == 'webp':
            if profile.video_quality == Quality.HIGH:
                options['quality'] = 95
            elif profile.video_quality == Quality.MEDIUM:
                options['quality'] = 85
            else:
                options['quality'] = 75
        
        return options


class TranscodingPipeline:
    """Main transcoding pipeline orchestrating batch processing"""
    
    def __init__(self, config -> None: Optional[TranscodingConfig] = None) -> None:
        """Initialize transcoding pipeline"""
        self.config = config or TranscodingConfig()
        self.transcoding_engine = TranscodingEngine(self.config)
        
        # Job management
        self.job_queue: List[TranscodingJob] = []
        self.active_jobs: Dict[str, TranscodingJob] = {}
        self.completed_jobs: List[TranscodingJob] = []
        
        # Execution control
        self.is_processing = False
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_jobs)
        
        # Predefined profiles
        self.profiles = self._initialize_profiles()
        
        logger.info("🔄 Media Transcoding Pipeline initialized")
    
    def _initialize_profiles(self) -> Dict[str, TranscodingProfile]:
        """Initialize predefined transcoding profiles"""
        profiles = {}
        
        # Video profiles
        profiles['video_hd'] = TranscodingProfile(
            profile_id='video_hd',
            name='HD Video',
            description='1080p H.264 video for general use',
            media_type=MediaType.VIDEO,
            output_format='mp4',
            output_extension='.mp4',
            video_codec=VideoCodec.H264,
            video_bitrate=5000,
            video_quality=Quality.HIGH,
            resolution=(1920, 1080),
            fps=30.0,
            audio_codec=AudioCodec.AAC,
            audio_bitrate=256,
            sample_rate=44100,
            channels=2
        )
        
        profiles['video_web'] = TranscodingProfile(
            profile_id='video_web',
            name='Web Video',
            description='720p H.264 optimized for web',
            media_type=MediaType.VIDEO,
            output_format='mp4',
            output_extension='.mp4',
            video_codec=VideoCodec.H264,
            video_bitrate=2500,
            video_quality=Quality.MEDIUM,
            resolution=(1280, 720),
            fps=30.0,
            audio_codec=AudioCodec.AAC,
            audio_bitrate=128,
            sample_rate=44100,
            channels=2
        )
        
        # Audio profiles
        profiles['audio_high'] = TranscodingProfile(
            profile_id='audio_high',
            name='High Quality Audio',
            description='High quality MP3 for music',
            media_type=MediaType.AUDIO,
            output_format='mp3',
            output_extension='.mp3',
            audio_codec=AudioCodec.MP3,
            audio_bitrate=320,
            sample_rate=44100,
            channels=2
        )
        
        profiles['audio_podcast'] = TranscodingProfile(
            profile_id='audio_podcast',
            name='Podcast Audio',
            description='Optimized for voice/podcast content',
            media_type=MediaType.AUDIO,
            output_format='mp3',
            output_extension='.mp3',
            audio_codec=AudioCodec.MP3,
            audio_bitrate=128,
            sample_rate=44100,
            channels=1
        )
        
        # Image profiles
        profiles['image_web'] = TranscodingProfile(
            profile_id='image_web',
            name='Web Image',
            description='JPEG optimized for web',
            media_type=MediaType.IMAGE,
            output_format='jpeg',
            output_extension='.jpg',
            video_quality=Quality.HIGH
        )
        
        profiles['image_thumbnail'] = TranscodingProfile(
            profile_id='image_thumbnail',
            name='Thumbnail',
            description='Small JPEG thumbnail',
            media_type=MediaType.IMAGE,
            output_format='jpeg',
            output_extension='.jpg',
            resolution=(320, 240),
            video_quality=Quality.MEDIUM
        )
        
        return profiles
    
    async def create_job(
        self,
        input_file: str,
        output_file: str,
        profile_id: str,
        priority: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TranscodingJob:
        """Create transcoding job"""
        try:
            profile = self.profiles.get(profile_id)
            if not profile:
                raise ValueError(f"Profile {profile_id} not found")
            
            job_id = str(uuid.uuid4())
            
            job = TranscodingJob(
                job_id=job_id,
                input_file=input_file,
                output_file=output_file,
                profile=profile,
                priority=priority,
                metadata=metadata or {}
            )
            
            # Add to queue
            self.job_queue.append(job)
            self._sort_queue_by_priority()
            
            logger.info(f"Created transcoding job {job_id}")
            return job
            
        except Exception as e:
            logger.error(f"Failed to create transcoding job: {e}")
            raise
    
    async def submit_batch_jobs(
        self, 
        job_requests: List[Dict[str, Any]]
    ) -> List[TranscodingJob]:
        """Submit multiple transcoding jobs"""
        try:
            jobs = []
            
            for request in job_requests:
                job = await self.create_job(
                    input_file=request['input_file'],
                    output_file=request['output_file'],
                    profile_id=request['profile_id'],
                    priority=request.get('priority', 1),
                    metadata=request.get('metadata')
                )
                jobs.append(job)
            
            logger.info(f"Submitted {len(jobs)} batch transcoding jobs")
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to submit batch jobs: {e}")
            return []
    
    async def start_processing(self) -> bool:
        """Start processing transcoding jobs"""
        try:
            if self.is_processing:
                logger.warning("Pipeline is already processing")
                return True
            
            self.is_processing = True
            
            # Start processing loop
            asyncio.create_task(self._process_queue())
            
            logger.info("Transcoding pipeline started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start processing: {e}")
            return False
    
    async def stop_processing(self) -> bool:
        """Stop processing transcoding jobs"""
        try:
            self.is_processing = False
            
            # Wait for active jobs to complete
            while self.active_jobs:
                await asyncio.sleep(1)
            
            logger.info("Transcoding pipeline stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop processing: {e}")
            return False
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status and progress"""
        try:
            # Check active jobs
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                return {
                    'job_id': job_id,
                    'status': job.status.value,
                    'progress_percent': job.progress_percent,
                    'started_at': job.started_at.isoformat() if job.started_at else None,
                    'processing_time': (datetime.now(timezone.utc) - job.started_at).total_seconds() if job.started_at else 0
                }
            
            # Check completed jobs
            completed_job = next((j for j in self.completed_jobs if j.job_id == job_id), None)
            if completed_job:
                return {
                    'job_id': job_id,
                    'status': completed_job.status.value,
                    'progress_percent': 100.0 if completed_job.status == TranscodingStatus.COMPLETED else 0.0,
                    'completed_at': completed_job.completed_at.isoformat() if completed_job.completed_at else None,
                    'processing_time': completed_job.processing_time,
                    'compression_ratio': completed_job.compression_ratio,
                    'error_message': completed_job.error_message
                }
            
            # Check queued jobs
            queued_job = next((j for j in self.job_queue if j.job_id == job_id), None)
            if queued_job:
                position = self.job_queue.index(queued_job) + 1
                return {
                    'job_id': job_id,
                    'status': queued_job.status.value,
                    'queue_position': position,
                    'created_at': queued_job.created_at.isoformat()
                }
            
            return {'error': f'Job {job_id} not found'}
            
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return {'error': str(e)}
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get pipeline status and statistics"""
        try:
            return {
                'is_processing': self.is_processing,
                'queue_size': len(self.job_queue),
                'active_jobs': len(self.active_jobs),
                'completed_jobs': len(self.completed_jobs),
                'failed_jobs': len([j for j in self.completed_jobs if j.status == TranscodingStatus.FAILED]),
                'available_profiles': list(self.profiles.keys()),
                'config': {
                    'max_concurrent_jobs': self.config.max_concurrent_jobs,
                    'temp_directory': self.config.temp_directory,
                    'output_directory': self.config.output_directory
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {e}")
            return {'error': str(e)}
    
    def _sort_queue_by_priority(self) -> None:
        """Sort job queue by priority (higher priority first)"""
        self.job_queue.sort(key=lambda job: (-job.priority, job.created_at))
    
    async def _process_queue(self) -> None:
        """Process job queue continuously"""
        while self.is_processing:
            try:
                # Check if we can process more jobs
                if len(self.active_jobs) < self.config.max_concurrent_jobs and self.job_queue:
                    # Get next job
                    job = self.job_queue.pop(0)
                    
                    # Start processing job
                    self.active_jobs[job.job_id] = job
                    asyncio.create_task(self._process_job(job))
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def _process_job(self, job -> None: TranscodingJob) -> None:
        """Process individual transcoding job"""
        try:
            job.status = TranscodingStatus.PROCESSING
            job.started_at = datetime.now(timezone.utc)
            
            # Progress callback
            async def progress_callback(progress -> None: float) -> None:
                job.progress_percent = progress
            
            # Get input file info
            input_info = await self.transcoding_engine.media_analyzer.analyze_media(job.input_file)
            
            # Perform transcoding based on media type
            success = False
            if job.profile.media_type == MediaType.VIDEO:
                success = await self.transcoding_engine.transcode_video(
                    job.input_file, job.output_file, job.profile, progress_callback
                )
            elif job.profile.media_type == MediaType.AUDIO:
                success = await self.transcoding_engine.transcode_audio(
                    job.input_file, job.output_file, job.profile, progress_callback
                )
            elif job.profile.media_type == MediaType.IMAGE:
                success = await self.transcoding_engine.transcode_image(
                    job.input_file, job.output_file, job.profile, progress_callback
                )
            
            # Update job status
            job.completed_at = datetime.now(timezone.utc)
            job.processing_time = (job.completed_at - job.started_at).total_seconds()
            
            if success and Path(job.output_file).exists():
                job.status = TranscodingStatus.COMPLETED
                job.progress_percent = 100.0
                
                # Get output file info
                job.output_info = await self.transcoding_engine.media_analyzer.analyze_media(job.output_file)
                
                # Calculate compression ratio
                if job.output_info.file_size > 0:
                    job.compression_ratio = input_info.file_size / job.output_info.file_size
                
            else:
                job.status = TranscodingStatus.FAILED
                job.error_message = "Transcoding failed or output file not created"
            
        except Exception as e:
            job.status = TranscodingStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            if job.started_at:
                job.processing_time = (job.completed_at - job.started_at).total_seconds()
            
            logger.error(f"Job {job.job_id} failed: {e}")
        
        finally:
            # Move job from active to completed
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
            self.completed_jobs.append(job)
            
            # Cleanup temp files if configured
            if self.config.cleanup_temp_files:
                await self._cleanup_temp_files(job)
    
    async def _cleanup_temp_files(self, job -> None: TranscodingJob) -> None:
        """Clean up temporary files for job"""
        try:
            # Would clean up any temporary files created during processing
            pass
        except Exception as e:
            logger.error(f"Cleanup failed for job {job.job_id}: {e}")


class MediaTranscodingPipeline:
    """Main interface for the media transcoding pipeline system"""
    
    def __init__(self, config -> None: Optional[TranscodingConfig] = None) -> None:
        """Initialize media transcoding pipeline"""
        self.config = config or TranscodingConfig()
        self.pipeline = TranscodingPipeline(self.config)
        
        logger.info("🎞️ Media Transcoding Pipeline System initialized")
    
    async def start(self) -> bool:
        """Start the transcoding pipeline"""
        return await self.pipeline.start_processing()
    
    async def stop(self) -> bool:
        """Stop the transcoding pipeline"""
        return await self.pipeline.stop_processing()
    
    async def transcode_file(
        self,
        input_file: str,
        output_file: str,
        profile_id: str,
        priority: int = 1
    ) -> TranscodingJob:
        """Transcode single file"""
        return await self.pipeline.create_job(input_file, output_file, profile_id, priority)
    
    async def transcode_batch(
        self, 
        job_requests: List[Dict[str, Any]]
    ) -> List[TranscodingJob]:
        """Transcode multiple files"""
        return await self.pipeline.submit_batch_jobs(job_requests)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get pipeline status"""
        return await self.pipeline.get_pipeline_status()
    
    def get_available_profiles(self) -> Dict[str, TranscodingProfile]:
        """Get available transcoding profiles"""
        return self.pipeline.profiles


# Export all classes for import
__all__ = [
    'MediaTranscodingPipeline',
    'TranscodingPipeline',
    'TranscodingEngine',
    'MediaAnalyzer',
    'TranscodingConfig',
    'TranscodingProfile',
    'TranscodingJob',
    'MediaInfo',
    'MediaType',
    'TranscodingStatus',
    'Quality',
    'VideoCodec',
    'AudioCodec'
]