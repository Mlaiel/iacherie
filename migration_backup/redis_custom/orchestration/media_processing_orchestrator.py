#!/usr/bin/env python3
"""🎬 Media Processing Orchestrator - Advanced Multi-Format Media Platform
================================================================
Expert: MEDIA ENGINEER + AUDIO EXPERT + VIDEO SPECIALIST + BACKEND SENIOR
Technologies: Media Processing + Format Conversion + Quality Optimization + Multi-Format Pipeline
Architecture: Level 3 - Media Intelligence Layer
Date: 2025-01-25

Ultra-advanced media processing orchestration with intelligent format conversion,
quality optimization, multi-format support and automated media enhancement.
================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
================================================================
"""

import asyncio
import logging
import json
import time
import math
import os
import hashlib
import subprocess
from typing import Dict, List, Optional, Any, Tuple, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import redis as redis_client
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
import statistics
from collections import defaultdict, deque
from pathlib import Path

logger = logging.getLogger(__name__)

class MediaType(Enum):
    """Types de média"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    ANIMATION = "animation"
    INTERACTIVE = "interactive"
    MIXED = "mixed"

class MediaFormat(Enum):
    """Formats de média supportés"""
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    FLV = "flv"
    M4V = "m4v"
    
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    WMA = "wma"
    
    # Image formats
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"
    SVG = "svg"
    
    # Document formats
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    TXT = "txt"

class ProcessingPriority(Enum):
    """Priorité de traitement"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    REAL_TIME = "real_time"

class QualityLevel(Enum):
    """Niveaux de qualité"""
    SOURCE = "source"          # Original quality
    ULTRA_HIGH = "ultra_high"   # 4K+
    HIGH = "high"              # 1080p
    MEDIUM = "medium"          # 720p
    LOW = "low"                # 480p
    MOBILE = "mobile"          # 360p
    THUMBNAIL = "thumbnail"    # Preview quality

class ProcessingStatus(Enum):
    """Statuts de traitement"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

@dataclass
class MediaFile:
    """Fichier média"""
    file_id: str
    original_filename: str
    media_type: MediaType
    format: MediaFormat
    file_path: str
    file_size: int  # bytes
    duration: Optional[float] = None  # seconds for video/audio
    dimensions: Optional[Tuple[int, int]] = None  # width, height for images/video
    bitrate: Optional[int] = None  # bits per second
    frame_rate: Optional[float] = None  # fps for video
    sample_rate: Optional[int] = None  # Hz for audio
    channels: Optional[int] = None  # audio channels
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ProcessingJob:
    """Job de traitement média"""
    job_id: str
    creator_id: str
    input_file: MediaFile
    target_formats: List[MediaFormat]
    target_qualities: List[QualityLevel]
    processing_options: Dict[str, Any] = field(default_factory=dict)
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    status: ProcessingStatus = ProcessingStatus.QUEUED
    progress: float = 0.0  # 0.0 to 1.0
    output_files: List[MediaFile] = field(default_factory=list)
    error_message: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    processing_time: float = 0.0  # seconds
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ProcessingPipeline:
    """Pipeline de traitement"""
    pipeline_id: str
    name: str
    description: str
    steps: List[Dict[str, Any]]
    supported_input_formats: List[MediaFormat]
    output_specifications: Dict[str, Any]
    performance_profile: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

class MediaAnalyzer:
    """Analyseur de média"""
    
    def __init__(self):
        self.supported_formats = {
            MediaType.VIDEO: [MediaFormat.MP4, MediaFormat.AVI, MediaFormat.MOV, MediaFormat.MKV, MediaFormat.WEBM],
            MediaType.AUDIO: [MediaFormat.MP3, MediaFormat.WAV, MediaFormat.FLAC, MediaFormat.AAC, MediaFormat.OGG],
            MediaType.IMAGE: [MediaFormat.JPEG, MediaFormat.PNG, MediaFormat.GIF, MediaFormat.WEBP, MediaFormat.TIFF]
        }
    
    async def analyze_media_file(self, file_path: str) -> MediaFile:
        """Analyser un fichier média"""
        try:
            # Get basic file info
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            filename = os.path.basename(file_path)
            
            # Calculate checksum
            checksum = await self._calculate_checksum(file_path)
            
            # Detect media type and format
            media_type, media_format = await self._detect_media_type_and_format(file_path)
            
            # Extract metadata based on media type
            metadata = {}
            duration = None
            dimensions = None
            bitrate = None
            frame_rate = None
            sample_rate = None
            channels = None
            
            if media_type == MediaType.VIDEO:
                video_info = await self._analyze_video(file_path)
                duration = video_info.get("duration")
                dimensions = video_info.get("dimensions")
                bitrate = video_info.get("bitrate")
                frame_rate = video_info.get("frame_rate")
                metadata.update(video_info.get("metadata", {}))
            
            elif media_type == MediaType.AUDIO:
                audio_info = await self._analyze_audio(file_path)
                duration = audio_info.get("duration")
                bitrate = audio_info.get("bitrate")
                sample_rate = audio_info.get("sample_rate")
                channels = audio_info.get("channels")
                metadata.update(audio_info.get("metadata", {}))
            
            elif media_type == MediaType.IMAGE:
                image_info = await self._analyze_image(file_path)
                dimensions = image_info.get("dimensions")
                metadata.update(image_info.get("metadata", {}))
            
            # Create MediaFile object
            media_file = MediaFile(
                file_id=str(uuid.uuid4()),
                original_filename=filename,
                media_type=media_type,
                format=media_format,
                file_path=file_path,
                file_size=file_size,
                duration=duration,
                dimensions=dimensions,
                bitrate=bitrate,
                frame_rate=frame_rate,
                sample_rate=sample_rate,
                channels=channels,
                metadata=metadata,
                checksum=checksum
            )
            
            logger.info(f"Media file analyzed: {filename} ({media_type.value}, {media_format.value})")
            return media_file
            
        except Exception as e:
            logger.error(f"Error analyzing media file {file_path}: {e}")
            raise
    
    async def _calculate_checksum(self, file_path: str) -> str:
        """Calculer le checksum d'un fichier"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            return ""
    
    async def _detect_media_type_and_format(self, file_path: str) -> Tuple[MediaType, MediaFormat]:
        """Détecter le type et format de média"""
        try:
            file_extension = Path(file_path).suffix.lower().lstrip('.')
            
            # Video formats
            video_extensions = {
                'mp4': MediaFormat.MP4,
                'avi': MediaFormat.AVI,
                'mov': MediaFormat.MOV,
                'mkv': MediaFormat.MKV,
                'webm': MediaFormat.WEBM,
                'flv': MediaFormat.FLV,
                'm4v': MediaFormat.M4V
            }
            
            # Audio formats
            audio_extensions = {
                'mp3': MediaFormat.MP3,
                'wav': MediaFormat.WAV,
                'flac': MediaFormat.FLAC,
                'aac': MediaFormat.AAC,
                'ogg': MediaFormat.OGG,
                'm4a': MediaFormat.M4A,
                'wma': MediaFormat.WMA
            }
            
            # Image formats
            image_extensions = {
                'jpg': MediaFormat.JPEG,
                'jpeg': MediaFormat.JPEG,
                'png': MediaFormat.PNG,
                'gif': MediaFormat.GIF,
                'webp': MediaFormat.WEBP,
                'tiff': MediaFormat.TIFF,
                'tif': MediaFormat.TIFF,
                'bmp': MediaFormat.BMP,
                'svg': MediaFormat.SVG
            }
            
            if file_extension in video_extensions:
                return MediaType.VIDEO, video_extensions[file_extension]
            elif file_extension in audio_extensions:
                return MediaType.AUDIO, audio_extensions[file_extension]
            elif file_extension in image_extensions:
                return MediaType.IMAGE, image_extensions[file_extension]
            else:
                # Default to document for unknown extensions
                return MediaType.DOCUMENT, MediaFormat.PDF  # Fallback
                
        except Exception as e:
            logger.error(f"Error detecting media type: {e}")
            return MediaType.DOCUMENT, MediaFormat.PDF
    
    async def _analyze_video(self, file_path: str) -> Dict[str, Any]:
        """Analyser une vidéo avec FFprobe"""
        try:
            # Simulate FFprobe analysis (in real implementation, use subprocess to run ffprobe)
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file_path
            ]
            
            # Simulate ffprobe output
            simulated_info = {
                "duration": 120.5,  # seconds
                "dimensions": (1920, 1080),
                "bitrate": 5000000,  # bits per second
                "frame_rate": 30.0,
                "metadata": {
                    "codec": "h264",
                    "color_space": "yuv420p",
                    "audio_codec": "aac",
                    "creation_time": datetime.now().isoformat()
                }
            }
            
            return simulated_info
            
        except Exception as e:
            logger.error(f"Error analyzing video: {e}")
            return {}
    
    async def _analyze_audio(self, file_path: str) -> Dict[str, Any]:
        """Analyser un fichier audio"""
        try:
            # Simulate audio analysis
            simulated_info = {
                "duration": 180.0,  # seconds
                "bitrate": 320000,  # bits per second
                "sample_rate": 44100,  # Hz
                "channels": 2,
                "metadata": {
                    "codec": "mp3",
                    "artist": "Unknown",
                    "title": "Unknown",
                    "album": "Unknown"
                }
            }
            
            return simulated_info
            
        except Exception as e:
            logger.error(f"Error analyzing audio: {e}")
            return {}
    
    async def _analyze_image(self, file_path: str) -> Dict[str, Any]:
        """Analyser une image"""
        try:
            # Simulate image analysis
            simulated_info = {
                "dimensions": (1920, 1080),
                "metadata": {
                    "color_mode": "RGB",
                    "dpi": 300,
                    "has_transparency": False,
                    "creation_time": datetime.now().isoformat()
                }
            }
            
            return simulated_info
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {}

class MediaProcessor:
    """Processeur de média"""
    
    def __init__(self):
        self.processing_engines = {
            MediaType.VIDEO: VideoProcessor(),
            MediaType.AUDIO: AudioProcessor(),
            MediaType.IMAGE: ImageProcessor()
        }
        self.quality_profiles = self._initialize_quality_profiles()
    
    def _initialize_quality_profiles(self) -> Dict[QualityLevel, Dict[str, Any]]:
        """Initialiser les profils de qualité"""
        return {
            QualityLevel.ULTRA_HIGH: {
                "video": {"width": 3840, "height": 2160, "bitrate": 15000000, "fps": 60},
                "audio": {"bitrate": 320000, "sample_rate": 48000},
                "image": {"width": 4096, "height": 4096, "quality": 95}
            },
            QualityLevel.HIGH: {
                "video": {"width": 1920, "height": 1080, "bitrate": 8000000, "fps": 30},
                "audio": {"bitrate": 256000, "sample_rate": 44100},
                "image": {"width": 1920, "height": 1920, "quality": 90}
            },
            QualityLevel.MEDIUM: {
                "video": {"width": 1280, "height": 720, "bitrate": 4000000, "fps": 30},
                "audio": {"bitrate": 192000, "sample_rate": 44100},
                "image": {"width": 1280, "height": 1280, "quality": 85}
            },
            QualityLevel.LOW: {
                "video": {"width": 854, "height": 480, "bitrate": 2000000, "fps": 24},
                "audio": {"bitrate": 128000, "sample_rate": 44100},
                "image": {"width": 854, "height": 854, "quality": 75}
            },
            QualityLevel.MOBILE: {
                "video": {"width": 640, "height": 360, "bitrate": 1000000, "fps": 24},
                "audio": {"bitrate": 96000, "sample_rate": 44100},
                "image": {"width": 640, "height": 640, "quality": 70}
            },
            QualityLevel.THUMBNAIL: {
                "video": {"width": 320, "height": 180, "bitrate": 500000, "fps": 15},
                "audio": {"bitrate": 64000, "sample_rate": 22050},
                "image": {"width": 320, "height": 320, "quality": 60}
            }
        }
    
    async def process_media(self, job: ProcessingJob) -> List[MediaFile]:
        """Traiter un média selon les spécifications"""
        try:
            input_file = job.input_file
            output_files = []
            
            # Get appropriate processor
            processor = self.processing_engines.get(input_file.media_type)
            if not processor:
                raise ValueError(f"No processor available for media type: {input_file.media_type}")
            
            # Process for each target format and quality
            total_tasks = len(job.target_formats) * len(job.target_qualities)
            completed_tasks = 0
            
            for target_format in job.target_formats:
                for target_quality in job.target_qualities:
                    try:
                        # Get quality profile
                        quality_profile = self.quality_profiles.get(target_quality, {})
                        
                        # Process media
                        output_file = await processor.process(
                            input_file,
                            target_format,
                            target_quality,
                            quality_profile,
                            job.processing_options
                        )
                        
                        if output_file:
                            output_files.append(output_file)
                        
                        completed_tasks += 1
                        job.progress = completed_tasks / total_tasks
                        
                    except Exception as e:
                        logger.error(f"Error processing {target_format.value} at {target_quality.value}: {e}")
                        continue
            
            logger.info(f"Media processing completed: {len(output_files)} files generated")
            return output_files
            
        except Exception as e:
            logger.error(f"Error in media processing: {e}")
            raise

class VideoProcessor:
    """Processeur vidéo"""
    
    async def process(
        self,
        input_file: MediaFile,
        target_format: MediaFormat,
        target_quality: QualityLevel,
        quality_profile: Dict[str, Any],
        processing_options: Dict[str, Any]
    ) -> Optional[MediaFile]:
        """Traiter une vidéo"""
        try:
            # Prepare output file path
            output_dir = processing_options.get("output_dir", "/tmp/processed")
            os.makedirs(output_dir, exist_ok=True)
            
            output_filename = f"{Path(input_file.original_filename).stem}_{target_quality.value}.{target_format.value}"
            output_path = os.path.join(output_dir, output_filename)
            
            # Get video quality settings
            video_profile = quality_profile.get("video", {})
            
            # Simulate FFmpeg processing
            await self._simulate_ffmpeg_processing(
                input_file.file_path,
                output_path,
                target_format,
                video_profile,
                processing_options
            )
            
            # Create output file info
            output_file = MediaFile(
                file_id=str(uuid.uuid4()),
                original_filename=output_filename,
                media_type=MediaType.VIDEO,
                format=target_format,
                file_path=output_path,
                file_size=self._estimate_output_size(input_file, video_profile),
                duration=input_file.duration,
                dimensions=(video_profile.get("width", 1920), video_profile.get("height", 1080)),
                bitrate=video_profile.get("bitrate", 8000000),
                frame_rate=video_profile.get("fps", 30),
                metadata={
                    "source_file": input_file.file_id,
                    "processing_quality": target_quality.value,
                    "codec": "h264",
                    "processed_at": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Video processed: {target_format.value} at {target_quality.value}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return None
    
    async def _simulate_ffmpeg_processing(
        self,
        input_path: str,
        output_path: str,
        target_format: MediaFormat,
        video_profile: Dict[str, Any],
        processing_options: Dict[str, Any]
    ):
        """Simuler le traitement FFmpeg"""
        try:
            # In real implementation, this would run FFmpeg
            # ffmpeg_cmd = [
            #     'ffmpeg', '-i', input_path,
            #     '-c:v', 'libx264',
            #     '-b:v', str(video_profile.get('bitrate', 8000000)),
            #     '-s', f"{video_profile.get('width', 1920)}x{video_profile.get('height', 1080)}",
            #     '-r', str(video_profile.get('fps', 30)),
            #     '-c:a', 'aac',
            #     '-b:a', '128k',
            #     output_path
            # ]
            # subprocess.run(ffmpeg_cmd, check=True)
            
            # Simulate processing time
            processing_time = 2.0  # seconds
            await asyncio.sleep(processing_time)
            
            # Create dummy output file
            with open(output_path, 'w') as f:
                f.write(f"Processed video: {target_format.value}\n")
            
        except Exception as e:
            logger.error(f"Error in FFmpeg simulation: {e}")
            raise
    
    def _estimate_output_size(self, input_file: MediaFile, video_profile: Dict[str, Any]) -> int:
        """Estimer la taille de sortie"""
        try:
            # Simple estimation based on bitrate and duration
            if input_file.duration:
                estimated_bitrate = video_profile.get("bitrate", 8000000)  # bits per second
                estimated_size = int((estimated_bitrate * input_file.duration) / 8)  # bytes
                return estimated_size
            return input_file.file_size
        except:
            return input_file.file_size

class AudioProcessor:
    """Processeur audio"""
    
    async def process(
        self,
        input_file: MediaFile,
        target_format: MediaFormat,
        target_quality: QualityLevel,
        quality_profile: Dict[str, Any],
        processing_options: Dict[str, Any]
    ) -> Optional[MediaFile]:
        """Traiter un fichier audio"""
        try:
            # Prepare output file path
            output_dir = processing_options.get("output_dir", "/tmp/processed")
            os.makedirs(output_dir, exist_ok=True)
            
            output_filename = f"{Path(input_file.original_filename).stem}_{target_quality.value}.{target_format.value}"
            output_path = os.path.join(output_dir, output_filename)
            
            # Get audio quality settings
            audio_profile = quality_profile.get("audio", {})
            
            # Simulate audio processing
            await self._simulate_audio_processing(
                input_file.file_path,
                output_path,
                target_format,
                audio_profile,
                processing_options
            )
            
            # Create output file info
            output_file = MediaFile(
                file_id=str(uuid.uuid4()),
                original_filename=output_filename,
                media_type=MediaType.AUDIO,
                format=target_format,
                file_path=output_path,
                file_size=self._estimate_audio_size(input_file, audio_profile),
                duration=input_file.duration,
                bitrate=audio_profile.get("bitrate", 256000),
                sample_rate=audio_profile.get("sample_rate", 44100),
                channels=input_file.channels or 2,
                metadata={
                    "source_file": input_file.file_id,
                    "processing_quality": target_quality.value,
                    "codec": target_format.value,
                    "processed_at": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Audio processed: {target_format.value} at {target_quality.value}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return None
    
    async def _simulate_audio_processing(
        self,
        input_path: str,
        output_path: str,
        target_format: MediaFormat,
        audio_profile: Dict[str, Any],
        processing_options: Dict[str, Any]
    ):
        """Simuler le traitement audio"""
        try:
            # Simulate processing time
            processing_time = 1.0  # seconds
            await asyncio.sleep(processing_time)
            
            # Create dummy output file
            with open(output_path, 'w') as f:
                f.write(f"Processed audio: {target_format.value}\n")
            
        except Exception as e:
            logger.error(f"Error in audio processing simulation: {e}")
            raise
    
    def _estimate_audio_size(self, input_file: MediaFile, audio_profile: Dict[str, Any]) -> int:
        """Estimer la taille audio"""
        try:
            if input_file.duration:
                estimated_bitrate = audio_profile.get("bitrate", 256000)
                estimated_size = int((estimated_bitrate * input_file.duration) / 8)
                return estimated_size
            return input_file.file_size
        except:
            return input_file.file_size

class ImageProcessor:
    """Processeur d'images"""
    
    async def process(
        self,
        input_file: MediaFile,
        target_format: MediaFormat,
        target_quality: QualityLevel,
        quality_profile: Dict[str, Any],
        processing_options: Dict[str, Any]
    ) -> Optional[MediaFile]:
        """Traiter une image"""
        try:
            # Prepare output file path
            output_dir = processing_options.get("output_dir", "/tmp/processed")
            os.makedirs(output_dir, exist_ok=True)
            
            output_filename = f"{Path(input_file.original_filename).stem}_{target_quality.value}.{target_format.value}"
            output_path = os.path.join(output_dir, output_filename)
            
            # Get image quality settings
            image_profile = quality_profile.get("image", {})
            
            # Simulate image processing
            await self._simulate_image_processing(
                input_file.file_path,
                output_path,
                target_format,
                image_profile,
                processing_options
            )
            
            # Create output file info
            output_file = MediaFile(
                file_id=str(uuid.uuid4()),
                original_filename=output_filename,
                media_type=MediaType.IMAGE,
                format=target_format,
                file_path=output_path,
                file_size=self._estimate_image_size(input_file, image_profile),
                dimensions=(image_profile.get("width", 1920), image_profile.get("height", 1080)),
                metadata={
                    "source_file": input_file.file_id,
                    "processing_quality": target_quality.value,
                    "quality": image_profile.get("quality", 90),
                    "processed_at": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Image processed: {target_format.value} at {target_quality.value}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None
    
    async def _simulate_image_processing(
        self,
        input_path: str,
        output_path: str,
        target_format: MediaFormat,
        image_profile: Dict[str, Any],
        processing_options: Dict[str, Any]
    ):
        """Simuler le traitement d'image"""
        try:
            # Simulate processing time
            processing_time = 0.5  # seconds
            await asyncio.sleep(processing_time)
            
            # Create dummy output file
            with open(output_path, 'w') as f:
                f.write(f"Processed image: {target_format.value}\n")
            
        except Exception as e:
            logger.error(f"Error in image processing simulation: {e}")
            raise
    
    def _estimate_image_size(self, input_file: MediaFile, image_profile: Dict[str, Any]) -> int:
        """Estimer la taille d'image"""
        try:
            # Simple estimation based on dimensions and quality
            width = image_profile.get("width", 1920)
            height = image_profile.get("height", 1080)
            quality = image_profile.get("quality", 90)
            
            # Rough estimation: 3 bytes per pixel * quality factor
            estimated_size = int(width * height * 3 * (quality / 100))
            return estimated_size
        except:
            return input_file.file_size

class MediaProcessingOrchestrator:
    """🎬 Orchestrateur de Traitement Média Enterprise pour Creators"""
    
    def __init__(self, redis_client: redis_client.Redis):
        self.redis_client = redis_client
        self.media_analyzer = MediaAnalyzer()
        self.media_processor = MediaProcessor()
        self.processing_jobs: Dict[str, ProcessingJob] = {}
        self.processing_pipelines: Dict[str, ProcessingPipeline] = {}
        self.job_queue: deque = deque()
        self.active_jobs: Set[str] = set()
        self.processing_stats: Dict[str, Any] = defaultdict(int)
        
        # Initialize default pipelines
        self._initialize_default_pipelines()
        
        logger.info("🎬 Media Processing Orchestrator initialized")
    
    def _initialize_default_pipelines(self):
        """Initialiser les pipelines par défaut"""
        default_pipelines = [
            {
                "pipeline_id": "video_standard",
                "name": "Standard Video Processing",
                "description": "Standard video processing with multiple quality outputs",
                "steps": [
                    {"action": "analyze", "parameters": {}},
                    {"action": "convert", "parameters": {"formats": ["mp4", "webm"]}},
                    {"action": "optimize", "parameters": {"qualities": ["high", "medium", "low"]}}
                ],
                "supported_input_formats": [MediaFormat.MP4, MediaFormat.AVI, MediaFormat.MOV],
                "output_specifications": {
                    "formats": ["mp4", "webm"],
                    "qualities": ["high", "medium", "low"]
                }
            },
            {
                "pipeline_id": "audio_podcast",
                "name": "Podcast Audio Processing",
                "description": "Optimized audio processing for podcast content",
                "steps": [
                    {"action": "analyze", "parameters": {}},
                    {"action": "normalize", "parameters": {"level": -23}},
                    {"action": "convert", "parameters": {"formats": ["mp3", "aac"]}},
                    {"action": "optimize", "parameters": {"qualities": ["high", "medium"]}}
                ],
                "supported_input_formats": [MediaFormat.WAV, MediaFormat.FLAC, MediaFormat.MP3],
                "output_specifications": {
                    "formats": ["mp3", "aac"],
                    "qualities": ["high", "medium"]
                }
            },
            {
                "pipeline_id": "image_social",
                "name": "Social Media Image Processing",
                "description": "Image processing optimized for social media platforms",
                "steps": [
                    {"action": "analyze", "parameters": {}},
                    {"action": "resize", "parameters": {"aspect_ratios": ["1:1", "16:9", "9:16"]}},
                    {"action": "convert", "parameters": {"formats": ["jpeg", "png", "webp"]}},
                    {"action": "optimize", "parameters": {"qualities": ["high", "medium"]}}
                ],
                "supported_input_formats": [MediaFormat.JPEG, MediaFormat.PNG, MediaFormat.TIFF],
                "output_specifications": {
                    "formats": ["jpeg", "png", "webp"],
                    "aspect_ratios": ["1:1", "16:9", "9:16"]
                }
            }
        ]
        
        for pipeline_data in default_pipelines:
            pipeline = ProcessingPipeline(**pipeline_data)
            self.processing_pipelines[pipeline.pipeline_id] = pipeline
    
    async def submit_processing_job(
        self,
        creator_id: str,
        file_path: str,
        target_formats: List[str] = None,
        target_qualities: List[str] = None,
        processing_options: Dict[str, Any] = None,
        priority: str = "normal",
        pipeline_id: str = None
    ) -> Optional[ProcessingJob]:
        """Soumettre un job de traitement"""
        try:
            # Analyze input file
            input_file = await self.media_analyzer.analyze_media_file(file_path)
            
            # Convert string parameters to enums
            target_format_enums = []
            if target_formats:
                for fmt in target_formats:
                    try:
                        target_format_enums.append(MediaFormat(fmt.lower()))
                    except ValueError:
                        logger.warning(f"Unsupported format: {fmt}")
            else:
                # Default formats based on media type
                if input_file.media_type == MediaType.VIDEO:
                    target_format_enums = [MediaFormat.MP4, MediaFormat.WEBM]
                elif input_file.media_type == MediaType.AUDIO:
                    target_format_enums = [MediaFormat.MP3, MediaFormat.AAC]
                elif input_file.media_type == MediaType.IMAGE:
                    target_format_enums = [MediaFormat.JPEG, MediaFormat.WEBP]
            
            target_quality_enums = []
            if target_qualities:
                for quality in target_qualities:
                    try:
                        target_quality_enums.append(QualityLevel(quality.lower()))
                    except ValueError:
                        logger.warning(f"Unsupported quality: {quality}")
            else:
                # Default qualities
                target_quality_enums = [QualityLevel.HIGH, QualityLevel.MEDIUM, QualityLevel.LOW]
            
            # Convert priority
            try:
                priority_enum = ProcessingPriority(priority.lower())
            except ValueError:
                priority_enum = ProcessingPriority.NORMAL
            
            # Create processing job
            job_id = str(uuid.uuid4())
            job = ProcessingJob(
                job_id=job_id,
                creator_id=creator_id,
                input_file=input_file,
                target_formats=target_format_enums,
                target_qualities=target_quality_enums,
                processing_options=processing_options or {},
                priority=priority_enum
            )
            
            # If pipeline specified, override formats and qualities
            if pipeline_id and pipeline_id in self.processing_pipelines:
                pipeline = self.processing_pipelines[pipeline_id]
                output_specs = pipeline.output_specifications
                
                if "formats" in output_specs:
                    job.target_formats = [MediaFormat(fmt) for fmt in output_specs["formats"]]
                if "qualities" in output_specs:
                    job.target_qualities = [QualityLevel(qual) for qual in output_specs["qualities"]]
            
            # Store job
            self.processing_jobs[job_id] = job
            
            # Add to queue based on priority
            if priority_enum in [ProcessingPriority.URGENT, ProcessingPriority.REAL_TIME]:
                self.job_queue.appendleft(job_id)  # High priority to front
            else:
                self.job_queue.append(job_id)  # Normal priority to back
            
            # Estimate completion time
            job.estimated_completion = await self._estimate_completion_time(job)
            
            # Store in Redis
            await self.redis_client.hset(
                f"media:job:{job_id}",
                mapping={
                    "creator_id": creator_id,
                    "input_file": input_file.original_filename,
                    "media_type": input_file.media_type.value,
                    "status": job.status.value,
                    "priority": job.priority.value,
                    "progress": str(job.progress),
                    "created_at": job.created_at.isoformat(),
                    "estimated_completion": job.estimated_completion.isoformat() if job.estimated_completion else ""
                }
            )
            
            logger.info(f"Processing job submitted: {job_id} for {input_file.original_filename}")
            return job
            
        except Exception as e:
            logger.error(f"Error submitting processing job: {e}")
            return None
    
    async def process_job_queue(self) -> None:
        """Traiter la queue des jobs"""
        try:
            while self.job_queue:
                job_id = self.job_queue.popleft()
                
                if job_id not in self.active_jobs and job_id in self.processing_jobs:
                    # Start processing job
                    asyncio.create_task(self._process_single_job(job_id))
                    
                    # Add small delay to prevent overwhelming the system
                    await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error processing job queue: {e}")
    
    async def _process_single_job(self, job_id: str) -> None:
        """Traiter un job individuel"""
        try:
            if job_id not in self.processing_jobs:
                return
            
            job = self.processing_jobs[job_id]
            self.active_jobs.add(job_id)
            
            # Update job status
            job.status = ProcessingStatus.PROCESSING
            job.started_at = datetime.now()
            
            # Update Redis
            await self.redis_client.hset(
                f"media:job:{job_id}",
                mapping={
                    "status": job.status.value,
                    "started_at": job.started_at.isoformat(),
                    "progress": str(job.progress)
                }
            )
            
            try:
                # Process media
                output_files = await self.media_processor.process_media(job)
                
                # Update job with results
                job.output_files = output_files
                job.status = ProcessingStatus.COMPLETED
                job.completed_at = datetime.now()
                job.processing_time = (job.completed_at - job.started_at).total_seconds()
                job.progress = 1.0
                
                # Update statistics
                self.processing_stats["completed_jobs"] += 1
                self.processing_stats["total_processing_time"] += job.processing_time
                
                # Store output files in Redis
                for output_file in output_files:
                    await self.redis_client.hset(
                        f"media:file:{output_file.file_id}",
                        mapping={
                            "filename": output_file.original_filename,
                            "media_type": output_file.media_type.value,
                            "format": output_file.format.value,
                            "file_size": str(output_file.file_size),
                            "file_path": output_file.file_path,
                            "parent_job": job_id,
                            "created_at": output_file.created_at.isoformat()
                        }
                    )
                
                logger.info(f"Job completed successfully: {job_id} ({len(output_files)} files generated)")
                
            except Exception as e:
                # Handle processing error
                job.status = ProcessingStatus.FAILED
                job.error_message = str(e)
                job.completed_at = datetime.now()
                
                self.processing_stats["failed_jobs"] += 1
                
                logger.error(f"Job failed: {job_id} - {e}")
            
            # Update final job status in Redis
            await self.redis_client.hset(
                f"media:job:{job_id}",
                mapping={
                    "status": job.status.value,
                    "progress": str(job.progress),
                    "completed_at": job.completed_at.isoformat() if job.completed_at else "",
                    "processing_time": str(job.processing_time),
                    "output_files_count": str(len(job.output_files)),
                    "error_message": job.error_message
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing single job {job_id}: {e}")
        
        finally:
            self.active_jobs.discard(job_id)
    
    async def _estimate_completion_time(self, job: ProcessingJob) -> datetime:
        """Estimer le temps de completion"""
        try:
            # Base processing time estimates (seconds per MB)
            processing_rates = {
                MediaType.VIDEO: 10.0,  # seconds per MB
                MediaType.AUDIO: 2.0,   # seconds per MB
                MediaType.IMAGE: 0.5    # seconds per MB
            }
            
            # Get file size in MB
            file_size_mb = job.input_file.file_size / (1024 * 1024)
            
            # Get base processing time
            base_rate = processing_rates.get(job.input_file.media_type, 5.0)
            base_time = file_size_mb * base_rate
            
            # Multiply by number of output variations
            num_outputs = len(job.target_formats) * len(job.target_qualities)
            total_time = base_time * num_outputs
            
            # Add queue wait time
            queue_position = len([j for j in self.job_queue if j == job.job_id or 
                                self.processing_jobs.get(j, ProcessingJob("", "", MediaFile("", "", MediaType.VIDEO, MediaFormat.MP4, "", 0), [], [])).priority.value >= job.priority.value])
            queue_wait_time = queue_position * 30  # 30 seconds average per job ahead
            
            # Calculate estimated completion
            estimated_seconds = total_time + queue_wait_time
            estimated_completion = datetime.now() + timedelta(seconds=estimated_seconds)
            
            return estimated_completion
            
        except Exception as e:
            logger.error(f"Error estimating completion time: {e}")
            return datetime.now() + timedelta(hours=1)  # Default 1 hour
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Obtenir le statut d'un job"""
        try:
            if job_id not in self.processing_jobs:
                return {"error": "Job not found"}
            
            job = self.processing_jobs[job_id]
            
            status_info = {
                "job_id": job_id,
                "creator_id": job.creator_id,
                "input_file": {
                    "filename": job.input_file.original_filename,
                    "media_type": job.input_file.media_type.value,
                    "format": job.input_file.format.value,
                    "file_size": job.input_file.file_size,
                    "duration": job.input_file.duration,
                    "dimensions": job.input_file.dimensions
                },
                "processing_config": {
                    "target_formats": [fmt.value for fmt in job.target_formats],
                    "target_qualities": [qual.value for qual in job.target_qualities],
                    "priority": job.priority.value
                },
                "status": {
                    "current_status": job.status.value,
                    "progress": job.progress,
                    "created_at": job.created_at.isoformat(),
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "estimated_completion": job.estimated_completion.isoformat() if job.estimated_completion else None,
                    "processing_time": job.processing_time,
                    "error_message": job.error_message
                },
                "output_files": [
                    {
                        "file_id": output_file.file_id,
                        "filename": output_file.original_filename,
                        "format": output_file.format.value,
                        "file_size": output_file.file_size,
                        "quality": output_file.metadata.get("processing_quality", "unknown")
                    } for output_file in job.output_files
                ],
                "queue_info": {
                    "position_in_queue": list(self.job_queue).index(job_id) + 1 if job_id in self.job_queue else 0,
                    "is_active": job_id in self.active_jobs
                }
            }
            
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting job status: {e}")
            return {"error": str(e)}
    
    async def get_processing_analytics(self, creator_id: str = None, time_period_days: int = 30) -> Dict[str, Any]:
        """Obtenir les analytics de traitement"""
        try:
            # Filter jobs by creator and time period
            cutoff_date = datetime.now() - timedelta(days=time_period_days)
            
            relevant_jobs = []
            for job in self.processing_jobs.values():
                if job.created_at >= cutoff_date:
                    if creator_id is None or job.creator_id == creator_id:
                        relevant_jobs.append(job)
            
            if not relevant_jobs:
                return {"message": "No processing data found for the specified criteria"}
            
            # Calculate statistics
            total_jobs = len(relevant_jobs)
            completed_jobs = len([j for j in relevant_jobs if j.status == ProcessingStatus.COMPLETED])
            failed_jobs = len([j for j in relevant_jobs if j.status == ProcessingStatus.FAILED])
            processing_jobs = len([j for j in relevant_jobs if j.status == ProcessingStatus.PROCESSING])
            queued_jobs = len([j for j in relevant_jobs if j.status == ProcessingStatus.QUEUED])
            
            # Media type distribution
            media_type_stats = defaultdict(int)
            for job in relevant_jobs:
                media_type_stats[job.input_file.media_type.value] += 1
            
            # Processing time statistics
            completed_job_times = [j.processing_time for j in relevant_jobs if j.status == ProcessingStatus.COMPLETED and j.processing_time > 0]
            avg_processing_time = statistics.mean(completed_job_times) if completed_job_times else 0
            
            # File size statistics
            input_sizes = [j.input_file.file_size for j in relevant_jobs]
            total_input_size = sum(input_sizes)
            avg_input_size = statistics.mean(input_sizes) if input_sizes else 0
            
            # Output statistics
            total_output_files = sum(len(j.output_files) for j in relevant_jobs)
            total_output_size = sum(
                sum(output_file.file_size for output_file in j.output_files) 
                for j in relevant_jobs
            )
            
            analytics = {
                "summary": {
                    "time_period_days": time_period_days,
                    "creator_id": creator_id,
                    "total_jobs": total_jobs,
                    "success_rate": round((completed_jobs / total_jobs) * 100, 2) if total_jobs > 0 else 0
                },
                "job_status_distribution": {
                    "completed": completed_jobs,
                    "failed": failed_jobs,
                    "processing": processing_jobs,
                    "queued": queued_jobs
                },
                "media_type_distribution": dict(media_type_stats),
                "processing_performance": {
                    "average_processing_time_seconds": round(avg_processing_time, 2),
                    "total_processing_time_hours": round(sum(completed_job_times) / 3600, 2),
                    "average_input_size_mb": round(avg_input_size / (1024 * 1024), 2),
                    "total_input_size_gb": round(total_input_size / (1024 * 1024 * 1024), 2)
                },
                "output_statistics": {
                    "total_output_files": total_output_files,
                    "total_output_size_gb": round(total_output_size / (1024 * 1024 * 1024), 2),
                    "average_outputs_per_job": round(total_output_files / total_jobs, 2) if total_jobs > 0 else 0
                },
                "efficiency_metrics": {
                    "throughput_jobs_per_hour": round(completed_jobs / (time_period_days * 24), 2),
                    "error_rate": round((failed_jobs / total_jobs) * 100, 2) if total_jobs > 0 else 0,
                    "queue_efficiency": round((completed_jobs / (completed_jobs + queued_jobs)) * 100, 2) if (completed_jobs + queued_jobs) > 0 else 0
                }
            }
            
            logger.info(f"Processing analytics generated for {creator_id or 'all creators'}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating processing analytics: {e}")
            return {"error": str(e)}
    
    async def cancel_job(self, job_id: str, creator_id: str) -> bool:
        """Annuler un job de traitement"""
        try:
            if job_id not in self.processing_jobs:
                return False
            
            job = self.processing_jobs[job_id]
            
            # Verify creator ownership
            if job.creator_id != creator_id:
                logger.warning(f"Creator {creator_id} attempted to cancel job {job_id} owned by {job.creator_id}")
                return False
            
            # Can only cancel queued or processing jobs
            if job.status not in [ProcessingStatus.QUEUED, ProcessingStatus.PROCESSING]:
                return False
            
            # Update job status
            job.status = ProcessingStatus.CANCELLED
            job.completed_at = datetime.now()
            
            # Remove from queue if still queued
            if job_id in self.job_queue:
                temp_queue = deque()
                while self.job_queue:
                    current_job_id = self.job_queue.popleft()
                    if current_job_id != job_id:
                        temp_queue.append(current_job_id)
                self.job_queue = temp_queue
            
            # Update Redis
            await self.redis_client.hset(
                f"media:job:{job_id}",
                mapping={
                    "status": job.status.value,
                    "completed_at": job.completed_at.isoformat()
                }
            )
            
            logger.info(f"Job cancelled: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling job: {e}")
            return False

# Export
__all__ = [
    'MediaProcessingOrchestrator',
    'MediaType',
    'MediaFormat',
    'ProcessingPriority',
    'QualityLevel',
    'ProcessingStatus',
    'MediaFile',
    'ProcessingJob',
    'ProcessingPipeline'
]