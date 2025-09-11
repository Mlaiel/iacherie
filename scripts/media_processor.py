#!/usr/bin/env python3
"""
Media Processor - Enterprise Audio/Video Processing
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Advanced media processing for Ainflue Platform:
- Multi-format audio/video transcoding
- Quality optimization and compression
- Watermarking and digital protection
- Thumbnail and preview generation
- Audio analysis and enhancement
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import hashlib
from dataclasses import dataclass, asdict
from enum import Enum

# Media processing libraries
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    import librosa
    import soundfile as sf
    HAS_AUDIO_LIBS = True
except ImportError:
    HAS_AUDIO_LIBS = False

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ainflue/media_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MediaType(Enum):
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    LIVESTREAM = "livestream"

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUEUED = "queued"

class Quality(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

@dataclass
class MediaFile:
    """Media file metadata"""
    file_id: str
    file_path: str
    media_type: MediaType
    original_format: str
    file_size: int
    duration: Optional[float]
    resolution: Optional[Tuple[int, int]]
    bitrate: Optional[int]
    sample_rate: Optional[int]
    channels: Optional[int]
    created_at: datetime

@dataclass
class ProcessingJob:
    """Media processing job"""
    job_id: str
    media_file: MediaFile
    target_format: str
    quality: Quality
    processing_options: Dict[str, Any]
    status: ProcessingStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_files: List[str] = None

class MediaProcessor:
    """
    Enterprise media processing system
    
    Features:
    - Multi-format audio/video transcoding
    - Intelligent quality optimization
    - Digital watermarking and protection
    - Automated thumbnail generation
    - Audio analysis and enhancement
    - Batch processing with queue management
    """
    
    def __init__(self, config_path: str = "/etc/ainflue/media_config.yaml"):
        self.config_path = config_path
        self.processing_queue: List[ProcessingJob] = []
        self.completed_jobs: List[ProcessingJob] = []
        self.active_jobs: Dict[str, ProcessingJob] = {}
        self.media_files: Dict[str, MediaFile] = {}
        self.config = {}
        
    async def load_media_configuration(self) -> Dict[str, Any]:
        """Load media processing configuration"""
        try:
            if os.path.exists(self.config_path):
                import yaml
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
            else:
                self.config = {
                    'ffmpeg_path': 'ffmpeg',
                    'output_directory': '/var/lib/ainflue/media/processed',
                    'temp_directory': '/tmp/ainflue_media',
                    'max_concurrent_jobs': 4,
                    'supported_formats': {
                        'audio': ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg'],
                        'video': ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'],
                        'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
                    },
                    'quality_presets': {
                        'low': {'video_bitrate': '500k', 'audio_bitrate': '128k'},
                        'medium': {'video_bitrate': '1500k', 'audio_bitrate': '192k'},
                        'high': {'video_bitrate': '3000k', 'audio_bitrate': '320k'},
                        'ultra': {'video_bitrate': '8000k', 'audio_bitrate': '320k'}
                    },
                    'watermark': {
                        'enabled': True,
                        'text': 'Ainflue',
                        'position': 'bottom-right',
                        'opacity': 0.7
                    }
                }
            
            # Create directories
            os.makedirs(self.config['output_directory'], exist_ok=True)
            os.makedirs(self.config['temp_directory'], exist_ok=True)
            
            logger.info("Media processing configuration loaded")
            return self.config
            
        except Exception as e:
            logger.error(f"Failed to load media configuration: {e}")
            raise
    
    async def register_media_file(self, file_path: str) -> str:
        """Register a media file for processing"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Media file not found: {file_path}")
            
            file_id = hashlib.md5(f"{file_path}_{datetime.now()}".encode()).hexdigest()
            
            # Detect media type and extract metadata
            media_info = await self._extract_media_info(file_path)
            
            media_file = MediaFile(
                file_id=file_id,
                file_path=file_path,
                media_type=media_info['type'],
                original_format=media_info['format'],
                file_size=os.path.getsize(file_path),
                duration=media_info.get('duration'),
                resolution=media_info.get('resolution'),
                bitrate=media_info.get('bitrate'),
                sample_rate=media_info.get('sample_rate'),
                channels=media_info.get('channels'),
                created_at=datetime.now()
            )
            
            self.media_files[file_id] = media_file
            
            logger.info(f"Media file registered: {file_id} ({media_info['type'].value})")
            return file_id
            
        except Exception as e:
            logger.error(f"Failed to register media file: {e}")
            raise
    
    async def _extract_media_info(self, file_path: str) -> Dict[str, Any]:
        """Extract media file information using FFprobe"""
        try:
            # Use FFprobe to get media information
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise RuntimeError(f"FFprobe failed: {result.stderr}")
            
            probe_data = json.loads(result.stdout)
            format_info = probe_data.get('format', {})
            streams = probe_data.get('streams', [])
            
            # Determine media type
            video_streams = [s for s in streams if s['codec_type'] == 'video']
            audio_streams = [s for s in streams if s['codec_type'] == 'audio']
            
            if video_streams:
                media_type = MediaType.VIDEO
            elif audio_streams:
                media_type = MediaType.AUDIO
            else:
                # Check file extension for images
                ext = Path(file_path).suffix.lower()[1:]
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                    media_type = MediaType.IMAGE
                else:
                    raise ValueError(f"Unknown media type for file: {file_path}")
            
            info = {
                'type': media_type,
                'format': format_info.get('format_name', '').split(',')[0],
                'duration': float(format_info.get('duration', 0)) if format_info.get('duration') else None,
                'bitrate': int(format_info.get('bit_rate', 0)) if format_info.get('bit_rate') else None
            }
            
            # Video-specific info
            if video_streams:
                video_stream = video_streams[0]
                info['resolution'] = (
                    int(video_stream.get('width', 0)),
                    int(video_stream.get('height', 0))
                )
            
            # Audio-specific info
            if audio_streams:
                audio_stream = audio_streams[0]
                info['sample_rate'] = int(audio_stream.get('sample_rate', 0))
                info['channels'] = int(audio_stream.get('channels', 0))
            
            return info
            
        except subprocess.TimeoutExpired:
            logger.error("FFprobe timeout")
            raise
        except Exception as e:
            logger.error(f"Media info extraction failed: {e}")
            raise
    
    async def create_processing_job(self, file_id: str, target_format: str, 
                                  quality: Quality, options: Dict[str, Any] = None) -> str:
        """Create a new media processing job"""
        try:
            if file_id not in self.media_files:
                raise ValueError(f"Media file {file_id} not found")
            
            job_id = f"job_{file_id}_{int(time.time())}"
            media_file = self.media_files[file_id]
            
            processing_job = ProcessingJob(
                job_id=job_id,
                media_file=media_file,
                target_format=target_format,
                quality=quality,
                processing_options=options or {},
                status=ProcessingStatus.QUEUED,
                created_at=datetime.now(),
                output_files=[]
            )
            
            self.processing_queue.append(processing_job)
            
            logger.info(f"Processing job created: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to create processing job: {e}")
            raise
    
    async def process_media_queue(self, max_concurrent: int = None) -> List[str]:
        """Process all jobs in the media processing queue"""
        try:
            if max_concurrent is None:
                max_concurrent = self.config.get('max_concurrent_jobs', 4)
            
            logger.info(f"Starting queue processing with {max_concurrent} concurrent jobs")
            
            completed_jobs = []
            active_tasks = []
            
            while self.processing_queue or active_tasks:
                # Start new jobs if under limit
                while (len(active_tasks) < max_concurrent and 
                       self.processing_queue):
                    job = self.processing_queue.pop(0)
                    task = asyncio.create_task(self._process_single_job(job))
                    active_tasks.append(task)
                
                # Wait for at least one job to complete
                if active_tasks:
                    done, pending = await asyncio.wait(
                        active_tasks, 
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    for task in done:
                        try:
                            job_id = await task
                            completed_jobs.append(job_id)
                        except Exception as e:
                            logger.error(f"Job processing failed: {e}")
                    
                    active_tasks = list(pending)
            
            logger.info(f"Queue processing completed. {len(completed_jobs)} jobs processed")
            return completed_jobs
            
        except Exception as e:
            logger.error(f"Queue processing failed: {e}")
            raise
    
    async def _process_single_job(self, job: ProcessingJob) -> str:
        """Process a single media job"""
        try:
            job.status = ProcessingStatus.PROCESSING
            job.started_at = datetime.now()
            self.active_jobs[job.job_id] = job
            
            logger.info(f"Processing job: {job.job_id}")
            
            # Choose processing method based on media type
            if job.media_file.media_type == MediaType.AUDIO:
                output_files = await self._process_audio(job)
            elif job.media_file.media_type == MediaType.VIDEO:
                output_files = await self._process_video(job)
            elif job.media_file.media_type == MediaType.IMAGE:
                output_files = await self._process_image(job)
            else:
                raise ValueError(f"Unsupported media type: {job.media_file.media_type}")
            
            # Update job status
            job.status = ProcessingStatus.COMPLETED
            job.completed_at = datetime.now()
            job.output_files = output_files
            
            # Move from active to completed
            del self.active_jobs[job.job_id]
            self.completed_jobs.append(job)
            
            logger.info(f"Job completed: {job.job_id}")
            return job.job_id
            
        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
            
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
            
            logger.error(f"Job failed: {job.job_id} - {e}")
            raise
    
    async def _process_audio(self, job: ProcessingJob) -> List[str]:
        """Process audio file"""
        try:
            input_file = job.media_file.file_path
            output_dir = self.config['output_directory']
            base_name = Path(input_file).stem
            
            output_files = []
            quality_preset = self.config['quality_presets'][job.quality.value]
            
            # Main transcoding
            output_file = f"{output_dir}/{base_name}_{job.job_id}.{job.target_format}"
            
            cmd = [
                self.config['ffmpeg_path'],
                '-i', input_file,
                '-acodec', self._get_audio_codec(job.target_format),
                '-ab', quality_preset['audio_bitrate'],
                '-y',  # Overwrite output file
                output_file
            ]
            
            # Add additional options
            if job.processing_options.get('normalize', False):
                cmd.extend(['-filter:a', 'loudnorm'])
            
            if job.processing_options.get('trim_silence', False):
                cmd.extend(['-af', 'silenceremove=1:0:-50dB'])
            
            result = await self._run_ffmpeg_command(cmd)
            if result:
                output_files.append(output_file)
            
            # Generate thumbnail if requested
            if job.processing_options.get('generate_waveform', False):
                waveform_file = await self._generate_audio_waveform(input_file, job.job_id)
                if waveform_file:
                    output_files.append(waveform_file)
            
            # Audio analysis if requested
            if job.processing_options.get('analyze_audio', False):
                analysis_file = await self._analyze_audio_content(input_file, job.job_id)
                if analysis_file:
                    output_files.append(analysis_file)
            
            return output_files
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            raise
    
    async def _process_video(self, job: ProcessingJob) -> List[str]:
        """Process video file"""
        try:
            input_file = job.media_file.file_path
            output_dir = self.config['output_directory']
            base_name = Path(input_file).stem
            
            output_files = []
            quality_preset = self.config['quality_presets'][job.quality.value]
            
            # Main transcoding
            output_file = f"{output_dir}/{base_name}_{job.job_id}.{job.target_format}"
            
            cmd = [
                self.config['ffmpeg_path'],
                '-i', input_file,
                '-vcodec', self._get_video_codec(job.target_format),
                '-acodec', self._get_audio_codec(job.target_format),
                '-b:v', quality_preset['video_bitrate'],
                '-b:a', quality_preset['audio_bitrate'],
                '-y',
                output_file
            ]
            
            # Add video filters
            filters = []
            
            # Scale if requested
            if 'scale' in job.processing_options:
                scale = job.processing_options['scale']
                filters.append(f"scale={scale['width']}:{scale['height']}")
            
            # Add watermark
            if (self.config['watermark']['enabled'] and 
                job.processing_options.get('add_watermark', True)):
                watermark_filter = await self._create_watermark_filter(job)
                if watermark_filter:
                    filters.append(watermark_filter)
            
            if filters:
                cmd.extend(['-vf', ','.join(filters)])
            
            result = await self._run_ffmpeg_command(cmd)
            if result:
                output_files.append(output_file)
            
            # Generate thumbnail
            thumbnail_file = await self._generate_video_thumbnail(input_file, job.job_id)
            if thumbnail_file:
                output_files.append(thumbnail_file)
            
            # Generate preview if requested
            if job.processing_options.get('generate_preview', False):
                preview_file = await self._generate_video_preview(input_file, job.job_id)
                if preview_file:
                    output_files.append(preview_file)
            
            return output_files
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            raise
    
    async def _process_image(self, job: ProcessingJob) -> List[str]:
        """Process image file"""
        try:
            input_file = job.media_file.file_path
            output_dir = self.config['output_directory']
            base_name = Path(input_file).stem
            
            output_files = []
            
            if not HAS_CV2:
                # Use ImageMagick fallback
                return await self._process_image_imagemagick(job)
            
            # Load image with OpenCV
            image = cv2.imread(input_file)
            if image is None:
                raise ValueError(f"Could not load image: {input_file}")
            
            # Apply processing options
            processed_image = image.copy()
            
            # Resize if requested
            if 'resize' in job.processing_options:
                size = job.processing_options['resize']
                processed_image = cv2.resize(
                    processed_image, 
                    (size['width'], size['height'])
                )
            
            # Add watermark
            if (self.config['watermark']['enabled'] and 
                job.processing_options.get('add_watermark', True)):
                processed_image = await self._add_image_watermark(processed_image)
            
            # Quality adjustment
            if job.quality == Quality.LOW:
                quality = 60
            elif job.quality == Quality.MEDIUM:
                quality = 80
            elif job.quality == Quality.HIGH:
                quality = 95
            else:  # ULTRA
                quality = 100
            
            # Save processed image
            output_file = f"{output_dir}/{base_name}_{job.job_id}.{job.target_format}"
            
            if job.target_format.lower() in ['jpg', 'jpeg']:
                cv2.imwrite(output_file, processed_image, 
                           [cv2.IMWRITE_JPEG_QUALITY, quality])
            elif job.target_format.lower() == 'png':
                compression = 9 - (quality // 11)  # Invert quality for PNG
                cv2.imwrite(output_file, processed_image,
                           [cv2.IMWRITE_PNG_COMPRESSION, compression])
            else:
                cv2.imwrite(output_file, processed_image)
            
            output_files.append(output_file)
            
            # Generate thumbnails in different sizes
            if job.processing_options.get('generate_thumbnails', False):
                thumbnail_sizes = [(150, 150), (300, 300), (600, 600)]
                for size in thumbnail_sizes:
                    thumb_file = f"{output_dir}/{base_name}_{job.job_id}_thumb_{size[0]}x{size[1]}.{job.target_format}"
                    thumbnail = cv2.resize(processed_image, size)
                    cv2.imwrite(thumb_file, thumbnail)
                    output_files.append(thumb_file)
            
            return output_files
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise
    
    async def _process_image_imagemagick(self, job: ProcessingJob) -> List[str]:
        """Process image using ImageMagick as fallback"""
        try:
            input_file = job.media_file.file_path
            output_dir = self.config['output_directory']
            base_name = Path(input_file).stem
            
            output_file = f"{output_dir}/{base_name}_{job.job_id}.{job.target_format}"
            
            cmd = ['convert', input_file]
            
            # Resize if requested
            if 'resize' in job.processing_options:
                size = job.processing_options['resize']
                cmd.extend(['-resize', f"{size['width']}x{size['height']}"])
            
            # Quality setting
            quality_map = {
                Quality.LOW: 60,
                Quality.MEDIUM: 80,
                Quality.HIGH: 95,
                Quality.ULTRA: 100
            }
            cmd.extend(['-quality', str(quality_map[job.quality])])
            
            cmd.append(output_file)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return [output_file]
            else:
                raise RuntimeError(f"ImageMagick failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"ImageMagick processing failed: {e}")
            raise
    
    async def _run_ffmpeg_command(self, cmd: List[str]) -> bool:
        """Run FFmpeg command asynchronously"""
        try:
            logger.debug(f"Running FFmpeg: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.debug("FFmpeg command successful")
                return True
            else:
                logger.error(f"FFmpeg failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"FFmpeg execution failed: {e}")
            return False
    
    def _get_audio_codec(self, format: str) -> str:
        """Get appropriate audio codec for format"""
        codec_map = {
            'mp3': 'mp3',
            'aac': 'aac',
            'm4a': 'aac',
            'ogg': 'vorbis',
            'flac': 'flac',
            'wav': 'pcm_s16le'
        }
        return codec_map.get(format.lower(), 'aac')
    
    def _get_video_codec(self, format: str) -> str:
        """Get appropriate video codec for format"""
        codec_map = {
            'mp4': 'libx264',
            'avi': 'libx264',
            'mov': 'libx264',
            'mkv': 'libx264',
            'webm': 'libvpx-vp9',
            'flv': 'libx264'
        }
        return codec_map.get(format.lower(), 'libx264')
    
    async def _create_watermark_filter(self, job: ProcessingJob) -> str:
        """Create FFmpeg watermark filter"""
        try:
            watermark_config = self.config['watermark']
            text = watermark_config['text']
            position = watermark_config['position']
            opacity = watermark_config['opacity']
            
            # Position mapping
            position_map = {
                'top-left': 'x=10:y=10',
                'top-right': 'x=w-tw-10:y=10',
                'bottom-left': 'x=10:y=h-th-10',
                'bottom-right': 'x=w-tw-10:y=h-th-10',
                'center': 'x=(w-tw)/2:y=(h-th)/2'
            }
            
            pos = position_map.get(position, position_map['bottom-right'])
            
            return f"drawtext=text='{text}':{pos}:fontsize=24:fontcolor=white@{opacity}"
            
        except Exception as e:
            logger.error(f"Watermark filter creation failed: {e}")
            return None
    
    async def _add_image_watermark(self, image: np.ndarray) -> np.ndarray:
        """Add watermark to image"""
        try:
            if not HAS_CV2:
                return image
            
            watermark_config = self.config['watermark']
            text = watermark_config['text']
            position = watermark_config['position']
            opacity = watermark_config['opacity']
            
            height, width = image.shape[:2]
            
            # Calculate text position
            font_scale = max(width // 1000, 1)
            thickness = max(width // 500, 1)
            
            (text_width, text_height), baseline = cv2.getTextSize(
                text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
            )
            
            if position == 'bottom-right':
                x = width - text_width - 20
                y = height - 20
            elif position == 'bottom-left':
                x = 20
                y = height - 20
            elif position == 'top-right':
                x = width - text_width - 20
                y = text_height + 20
            elif position == 'top-left':
                x = 20
                y = text_height + 20
            else:  # center
                x = (width - text_width) // 2
                y = (height + text_height) // 2
            
            # Create overlay
            overlay = image.copy()
            cv2.putText(overlay, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                       font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
            
            # Blend overlay with original
            result = cv2.addWeighted(image, 1 - opacity, overlay, opacity, 0)
            
            return result
            
        except Exception as e:
            logger.error(f"Image watermark failed: {e}")
            return image
    
    async def _generate_video_thumbnail(self, input_file: str, job_id: str) -> Optional[str]:
        """Generate video thumbnail"""
        try:
            output_dir = self.config['output_directory']
            thumbnail_file = f"{output_dir}/thumb_{job_id}.jpg"
            
            # Extract frame at 10% of video duration
            cmd = [
                self.config['ffmpeg_path'],
                '-i', input_file,
                '-ss', '00:00:01',  # 1 second in
                '-vframes', '1',
                '-q:v', '2',  # High quality
                '-y',
                thumbnail_file
            ]
            
            success = await self._run_ffmpeg_command(cmd)
            return thumbnail_file if success else None
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return None
    
    async def _generate_video_preview(self, input_file: str, job_id: str) -> Optional[str]:
        """Generate video preview (short clip)"""
        try:
            output_dir = self.config['output_directory']
            preview_file = f"{output_dir}/preview_{job_id}.mp4"
            
            # Create 10-second preview starting at 10% of video
            cmd = [
                self.config['ffmpeg_path'],
                '-i', input_file,
                '-ss', '5',  # Start at 5 seconds
                '-t', '10',  # 10 seconds duration
                '-vcodec', 'libx264',
                '-acodec', 'aac',
                '-b:v', '1000k',
                '-b:a', '128k',
                '-y',
                preview_file
            ]
            
            success = await self._run_ffmpeg_command(cmd)
            return preview_file if success else None
            
        except Exception as e:
            logger.error(f"Preview generation failed: {e}")
            return None
    
    async def _generate_audio_waveform(self, input_file: str, job_id: str) -> Optional[str]:
        """Generate audio waveform visualization"""
        try:
            if not HAS_AUDIO_LIBS:
                logger.warning("Audio libraries not available for waveform generation")
                return None
            
            output_dir = self.config['output_directory']
            waveform_file = f"{output_dir}/waveform_{job_id}.png"
            
            # Load audio
            y, sr = librosa.load(input_file, duration=60)  # First 60 seconds
            
            # Create waveform plot
            import matplotlib.pyplot as plt
            plt.figure(figsize=(12, 4))
            plt.plot(y)
            plt.title('Audio Waveform')
            plt.xlabel('Time')
            plt.ylabel('Amplitude')
            plt.savefig(waveform_file, dpi=150, bbox_inches='tight')
            plt.close()
            
            return waveform_file
            
        except Exception as e:
            logger.error(f"Waveform generation failed: {e}")
            return None
    
    async def _analyze_audio_content(self, input_file: str, job_id: str) -> Optional[str]:
        """Analyze audio content and generate report"""
        try:
            if not HAS_AUDIO_LIBS:
                logger.warning("Audio libraries not available for analysis")
                return None
            
            output_dir = self.config['output_directory']
            analysis_file = f"{output_dir}/analysis_{job_id}.json"
            
            # Load audio
            y, sr = librosa.load(input_file)
            
            # Perform analysis
            analysis = {
                'duration': len(y) / sr,
                'sample_rate': sr,
                'tempo': float(librosa.beat.tempo(y=y, sr=sr)[0]),
                'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
                'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(y))),
                'rms_energy': float(np.mean(librosa.feature.rms(y=y))),
                'mfcc_mean': librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).mean(axis=1).tolist()
            }
            
            # Save analysis
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            return analysis_file
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return None
    
    async def get_job_status(self, job_id: str) -> Optional[ProcessingJob]:
        """Get the status of a processing job"""
        # Check active jobs
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        
        # Check completed jobs
        for job in self.completed_jobs:
            if job.job_id == job_id:
                return job
        
        # Check queue
        for job in self.processing_queue:
            if job.job_id == job_id:
                return job
        
        return None
    
    async def generate_processing_report(self) -> Dict[str, Any]:
        """Generate comprehensive processing report"""
        try:
            report = {
                'report_id': hashlib.md5(f"media_report_{datetime.now()}".encode()).hexdigest(),
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_files': len(self.media_files),
                    'queued_jobs': len(self.processing_queue),
                    'active_jobs': len(self.active_jobs),
                    'completed_jobs': len(self.completed_jobs)
                },
                'media_types': {
                    media_type.value: len([f for f in self.media_files.values() 
                                         if f.media_type == media_type])
                    for media_type in MediaType
                },
                'processing_status': {
                    status.value: len([j for j in self.completed_jobs 
                                     if j.status == status])
                    for status in ProcessingStatus
                },
                'recent_jobs': [
                    asdict(job) for job in self.completed_jobs[-10:]
                ]
            }
            
            logger.info("Media processing report generated")
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise

async def main():
    """CLI entry point for media processor"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ainflue Media Processor')
    parser.add_argument('--register', metavar='FILE', help='Register media file')
    parser.add_argument('--process', metavar='FILE_ID', help='Process media file')
    parser.add_argument('--format', default='mp4', help='Target format')
    parser.add_argument('--quality', choices=['low', 'medium', 'high', 'ultra'], 
                       default='high', help='Processing quality')
    parser.add_argument('--queue', action='store_true', help='Process entire queue')
    parser.add_argument('--status', metavar='JOB_ID', help='Get job status')
    parser.add_argument('--report', action='store_true', help='Generate processing report')
    
    args = parser.parse_args()
    
    processor = MediaProcessor()
    await processor.load_media_configuration()
    
    try:
        if args.register:
            file_id = await processor.register_media_file(args.register)
            print(f"File registered: {file_id}")
        
        if args.process:
            quality = Quality(args.quality)
            job_id = await processor.create_processing_job(
                args.process, args.format, quality
            )
            print(f"Processing job created: {job_id}")
        
        if args.queue:
            completed = await processor.process_media_queue()
            print(f"Queue processed. {len(completed)} jobs completed.")
        
        if args.status:
            job = await processor.get_job_status(args.status)
            if job:
                print(json.dumps(asdict(job), indent=2, default=str))
            else:
                print("Job not found")
        
        if args.report:
            report = await processor.generate_processing_report()
            print(json.dumps(report, indent=2, default=str))
    
    except Exception as e:
        logger.error(f"Media processor failed: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())