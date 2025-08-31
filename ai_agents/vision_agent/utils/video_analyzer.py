"""Video Analyzer - Enterprise Video Processing & Analysis System
==============================================================

Advanced video analysis system with AI-powered scene detection, motion tracking,
object recognition, temporal analysis, and comprehensive video content understanding
for digital content creators and influencers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple, Generator, Callable
from datetime import datetime, timedelta
import torch
import torchvision.transforms as transforms
from collections import defaultdict
import json
import hashlib
from pathlib import Path
import subprocess
import tempfile
import os
from dataclasses import dataclass
from enum import Enum
import time
from concurrent.futures import ThreadPoolExecutor
import threading

# Advanced video processing libraries
import ffmpeg
from moviepy.editor import VideoFileClip, AudioFileClip
from scipy.spatial.distance import cosine
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import librosa

from ..base import BaseAgent, AgentStatus, AgentCapability
try:
    from core.exceptions import VideoProcessingError, ValidationError, SecurityError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    VideoProcessingError, ValidationError, SecurityError = globals().get('VideoProcessingError, ValidationError, SecurityError', Exception)
from ...utils.performance_monitor import PerformanceMonitor
from ...security.content_validator import ContentValidator
from ...utils.cache_manager import CacheManager
from .config import VisionAgentConfig
from .image_processor import ImageProcessor

logger = logging.getLogger(__name__)

class VideoQuality(Enum):
    """Video quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

class SceneType(Enum):
    """Types of scenes detected in video"""
    STATIC = "static"
    LOW_MOTION = "low_motion"
    HIGH_MOTION = "high_motion"
    TRANSITION = "transition"
    CUT = "cut"
    FADE = "fade"
    WIPE = "wipe"

class VideoAnalysisType(Enum):
    """Types of video analysis"""
    BASIC = "basic"
    COMPREHENSIVE = "comprehensive"
    PROFESSIONAL = "professional"
    FORENSIC = "forensic"

@dataclass
class VideoFrame:
    """Represents a single video frame"""
    frame_number: int
    timestamp: float
    image: np.ndarray
    quality_score: float
    motion_score: float
    scene_type: SceneType
    objects_detected: List[Dict] = None
    faces_detected: List[Dict] = None

@dataclass
class VideoSegment:
    """Represents a video segment/scene"""
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    duration: float
    scene_type: SceneType
    average_quality: float
    motion_intensity: float
    key_frames: List[int]
    dominant_colors: List[Tuple[int, int, int]]
    audio_features: Optional[Dict] = None

@dataclass
class VideoMetrics:
    """Comprehensive video quality and content metrics"""
    resolution: Tuple[int, int]
    fps: float
    duration: float
    bitrate: int
    codec: str
    file_size_bytes: int
    
    # Quality metrics
    overall_quality: VideoQuality
    average_frame_quality: float
    quality_consistency: float
    motion_analysis: Dict[str, float]
    audio_quality: Optional[float]
    
    # Content metrics
    scene_count: int
    transition_count: int
    face_time_percentage: float
    object_diversity: float
    color_variance: float
    temporal_complexity: float
    
    # Technical metrics
    compression_efficiency: float
    encoding_quality: float
    frame_drops: int
    sync_issues: int

@dataclass
class VideoAnalysisResult:
    """Complete video analysis result"""
    video_path: str
    analysis_type: VideoAnalysisType
    processing_time: float
    success: bool
    
    # Core metrics
    metrics: Optional[VideoMetrics] = None
    
    # Temporal analysis
    segments: List[VideoSegment] = None
    key_frames: List[VideoFrame] = None
    
    # Detection results
    objects_timeline: Dict[str, List[Tuple[float, float]]] = None
    faces_timeline: Dict[str, List[Tuple[float, float]]] = None
    
    # Content analysis
    dominant_themes: List[str] = None
    mood_timeline: List[Tuple[float, str, float]] = None
    
    # Generated assets
    thumbnails: List[str] = None
    preview_clips: List[str] = None
    
    # Error handling
    warnings: List[str] = None
    errors: List[str] = None

class VideoAnalyzer(BaseAgent):
    """
    Enterprise-grade video analysis system providing comprehensive
    video processing, temporal analysis, content understanding, and
    professional-grade video intelligence capabilities.
    """
    
    def __init__(self, config: Optional[VisionAgentConfig] = None):
        super().__init__(
            agent_id="video_analyzer",
            name="Video Analyzer",
            version="2.1.0",
            capabilities=[
                AgentCapability.VIDEO_ANALYSIS,
                AgentCapability.SCENE_DETECTION,
                AgentCapability.MOTION_TRACKING,
                AgentCapability.TEMPORAL_ANALYSIS,
                AgentCapability.OBJECT_DETECTION,
                AgentCapability.FACE_RECOGNITION,
                AgentCapability.QUALITY_ASSESSMENT,
                AgentCapability.THUMBNAIL_GENERATION,
                AgentCapability.CONTENT_FINGERPRINTING
            ]
        )
        
        self.config = config or VisionAgentConfig()
        self.performance_monitor = PerformanceMonitor("video_analysis")
        self.content_validator = ContentValidator()
        self.cache_manager = CacheManager("video_cache")
        self.image_processor = ImageProcessor(config)
        
        # Thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Video processing configuration
        self.max_resolution = (3840, 2160)  # 4K support
        self.min_resolution = (320, 240)
        self.max_duration = 3600  # 1 hour max
        self.max_file_size = self.config.security.max_file_size_mb * 1024 * 1024
        
        # Analysis parameters
        self.frame_sampling_rates = {
            VideoAnalysisType.BASIC: 30,        # Every 30th frame
            VideoAnalysisType.COMPREHENSIVE: 15, # Every 15th frame  
            VideoAnalysisType.PROFESSIONAL: 5,   # Every 5th frame
            VideoAnalysisType.FORENSIC: 1        # Every frame
        }
        
        self.scene_change_thresholds = {
            'histogram': 0.3,
            'structural': 0.4,
            'optical_flow': 0.5
        }
        
        # Motion analysis parameters
        self.motion_detection_params = {
            'min_area': 500,
            'learning_rate': 0.01,
            'history': 500,
            'var_threshold': 16,
            'detect_shadows': True
        }
        
        # Optical flow parameters
        self.optical_flow_params = {
            'winSize': (15, 15),
            'maxLevel': 2,
            'criteria': (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
            'flags': 0,
            'minEigThreshold': 1e-4
        }
        
        # Supported formats with characteristics
        self.format_specs = {
            'MP4': {'codecs': ['h264', 'h265'], 'audio': ['aac', 'mp3'], 'quality': 'high'},
            'AVI': {'codecs': ['xvid', 'divx'], 'audio': ['mp3', 'wav'], 'quality': 'medium'},
            'MOV': {'codecs': ['h264', 'prores'], 'audio': ['aac'], 'quality': 'high'},
            'MKV': {'codecs': ['h264', 'h265', 'vp9'], 'audio': ['aac', 'flac'], 'quality': 'high'},
            'WEBM': {'codecs': ['vp8', 'vp9'], 'audio': ['vorbis', 'opus'], 'quality': 'good'},
            'FLV': {'codecs': ['h264', 'flv1'], 'audio': ['aac', 'mp3'], 'quality': 'medium'}
        }

    async def initialize(self) -> bool:
        """Initialize video analysis components with advanced ML models"""
        try:
            logger.info("Initializing Enterprise Video Analyzer...")
            
            # Initialize device and GPU optimization
            self.device = torch.device("cuda" if torch.cuda.is_available() and 
                                     self.config.models['yolo'].gpu_acceleration else "cpu")
            
            if self.device.type == 'cuda':
                torch.backends.cudnn.benchmark = True
                logger.info(f"GPU acceleration enabled: {torch.cuda.get_device_name(0)}")
            
            # Initialize image processor for frame analysis
            await self.image_processor.initialize()
            
            # Initialize motion detection models
            self._init_motion_detection()
            
            # Initialize scene detection models
            self._init_scene_detection()
            
            # Initialize audio analysis capabilities
            self._init_audio_analysis()
            
            # Initialize object tracking
            self._init_object_tracking()
            
            # Warm up models
            await self._warm_up_models()
            
            # Create processing directories
            self._ensure_directories()
            
            self.status = AgentStatus.READY
            logger.info("Video Analyzer initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Video Analyzer: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    def _init_motion_detection(self):
        """Initialize motion detection algorithms"""
        try:
            # Background subtractor for motion detection
            self.bg_subtractors = {
                'mog2': cv2.createBackgroundSubtractorMOG2(
                    history=self.motion_detection_params['history'],
                    varThreshold=self.motion_detection_params['var_threshold'],
                    detectShadows=self.motion_detection_params['detect_shadows']
                ),
                'knn': cv2.createBackgroundSubtractorKNN(
                    history=self.motion_detection_params['history'],
                    dist2Threshold=400.0,
                    detectShadows=self.motion_detection_params['detect_shadows']
                )
            }
            
            # Initialize optical flow trackers
            self.flow_trackers = {
                'lucas_kanade': cv2.calcOpticalFlowPyrLK,
                'farneback': cv2.calcOpticalFlowFarneback
            }
            
            logger.info("Motion detection models initialized")
            
        except Exception as e:
            logger.warning(f"Motion detection initialization failed: {e}")
    
    def _init_scene_detection(self):
        """Initialize scene detection algorithms"""
        try:
            # Initialize histogram comparators
            self.histogram_comparators = [
                cv2.HISTCMP_CORREL,
                cv2.HISTCMP_CHISQR,
                cv2.HISTCMP_INTERSECT,
                cv2.HISTCMP_BHATTACHARYYA
            ]
            
            # Initialize feature extractors for scene analysis
            # In production, would load trained scene classification models
            self.scene_classifier = None  # Placeholder for actual model
            
            logger.info("Scene detection models initialized")
            
        except Exception as e:
            logger.warning(f"Scene detection initialization failed: {e}")
    
    def _init_audio_analysis(self):
        """Initialize audio analysis capabilities"""
        try:
            # Audio analysis parameters
            self.audio_params = {
                'sample_rate': 22050,
                'hop_length': 512,
                'n_fft': 2048,
                'n_mels': 128,
                'fmin': 20,
                'fmax': 8000
            }
            
            # Audio feature extractors would be initialized here
            self.audio_analyzer = None  # Placeholder
            
            logger.info("Audio analysis initialized")
            
        except Exception as e:
            logger.warning(f"Audio analysis initialization failed: {e}")
    
    def _init_object_tracking(self):
        """Initialize object tracking algorithms"""
        try:
            # Initialize various trackers for robust tracking
            self.tracker_types = {
                'CSRT': cv2.TrackerCSRT_create,
                'KCF': cv2.TrackerKCF_create,
                'MIL': cv2.TrackerMIL_create,
                'BOOSTING': cv2.legacy.TrackerBoosting_create if hasattr(cv2, 'legacy') else None,
                'TLD': cv2.legacy.TrackerTLD_create if hasattr(cv2, 'legacy') else None
            }
            
            # Filter out unavailable trackers
            self.tracker_types = {k: v for k, v in self.tracker_types.items() if v is not None}
            
            logger.info(f"Object tracking initialized with {len(self.tracker_types)} tracker types")
            
        except Exception as e:
            logger.warning(f"Object tracking initialization failed: {e}")
            self.tracker_types = {}
    
    async def _warm_up_models(self):
        """Warm up models with sample data"""
        try:
            # Create dummy video frame for warm-up
            dummy_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # Warm up image processing
            await self.image_processor.assess_quality(dummy_frame)
            
            # Warm up motion detection
            if hasattr(self, 'bg_subtractors'):
                for subtractor in self.bg_subtractors.values():
                    subtractor.apply(dummy_frame)
            
            logger.info("Model warm-up completed")
            
        except Exception as e:
            logger.warning(f"Model warm-up failed: {e}")
    
    def _ensure_directories(self):
        """Ensure all necessary directories exist"""
        directories = [
            self.config.storage.temp_path,
            self.config.storage.cache_path,
            f"{self.config.storage.temp_path}/video_frames",
            f"{self.config.storage.temp_path}/thumbnails",
            f"{self.config.storage.temp_path}/previews"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    async def analyze_video(self,
                          video_input: Union[str, bytes],
                          analysis_type: VideoAnalysisType = VideoAnalysisType.COMPREHENSIVE,
                          extract_audio: bool = True,
                          generate_thumbnails: bool = True,
                          custom_options: Optional[Dict[str, Any]] = None) -> VideoAnalysisResult:
        """
        Comprehensive video analysis with temporal understanding
        
        Args:
            video_input: Video file path or bytes
            analysis_type: Type of analysis to perform
            extract_audio: Whether to analyze audio track
            generate_thumbnails: Whether to generate thumbnail images
            custom_options: Custom analysis options
            
        Returns:
            VideoAnalysisResult with comprehensive analysis data
        """
        start_time = time.time()
        
        try:
            # Load and validate video
            video_path = await self._prepare_video_input(video_input)
            
            # Check cache first
            cache_key = self._generate_video_cache_key(video_path, analysis_type)
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result and self.config.performance.cache_enabled:
                logger.info("Returning cached video analysis result")
                return cached_result
            
            # Initialize result object
            result = VideoAnalysisResult(
                video_path=video_path,
                analysis_type=analysis_type,
                processing_time=0.0,
                success=False,
                segments=[],
                key_frames=[],
                objects_timeline={},
                faces_timeline={},
                dominant_themes=[],
                mood_timeline=[],
                thumbnails=[],
                preview_clips=[],
                warnings=[],
                errors=[]
            )
            
            # Extract basic video information
            video_info = await self._extract_video_info(video_path)
            if not video_info:
                result.errors.append("Failed to extract video information")
                return result
            
            # Validate video constraints
            validation_result = await self._validate_video(video_info)
            if not validation_result['valid']:
                result.errors.extend(validation_result['errors'])
                return result
            
            # Perform frame-by-frame analysis
            frames_analysis = await self._analyze_video_frames(
                video_path, analysis_type, custom_options
            )
            
            # Perform temporal analysis
            temporal_analysis = await self._perform_temporal_analysis(frames_analysis)
            
            # Extract audio features if requested
            audio_analysis = None
            if extract_audio and video_info.get('has_audio'):
                audio_analysis = await self._analyze_audio_track(video_path)
            
            # Generate comprehensive metrics
            metrics = await self._generate_video_metrics(
                video_info, frames_analysis, temporal_analysis, audio_analysis
            )
            
            # Generate thumbnails if requested
            thumbnails = []
            if generate_thumbnails:
                thumbnails = await self._generate_video_thumbnails(
                    video_path, frames_analysis['key_frames']
                )
            
            # Compile final result
            result.success = True
            result.processing_time = time.time() - start_time
            result.metrics = metrics
            result.segments = temporal_analysis['segments']
            result.key_frames = frames_analysis['key_frames']
            result.objects_timeline = frames_analysis.get('objects_timeline', {})
            result.faces_timeline = frames_analysis.get('faces_timeline', {})
            result.thumbnails = thumbnails
            result.dominant_themes = temporal_analysis.get('dominant_themes', [])
            result.mood_timeline = temporal_analysis.get('mood_timeline', [])
            
            # Cache successful result
            if self.config.performance.cache_enabled:
                await self.cache_manager.set(cache_key, result, ttl=7200)
            
            # Record performance metrics
            await self.performance_monitor.record_metric(
                "video_analysis_time", result.processing_time
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            processing_time = time.time() - start_time
            
            return VideoAnalysisResult(
                video_path=video_input if isinstance(video_input, str) else "bytes_input",
                analysis_type=analysis_type,
                processing_time=processing_time,
                success=False,
                errors=[str(e)]
            )
            logger.error(f"Video Analyzer initialization failed: {e}")
            self.status = AgentStatus.ERROR
            return False

    async def analyze_video(
        self, 
        video_input: Union[str, bytes],
        analysis_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive video analysis
        
        Args:
            video_input: Video file path or binary data
            analysis_options: Analysis configuration options
            
        Returns:
            Complete video analysis results
        """
        start_time = datetime.now()
        
        try:
            logger.info("Starting comprehensive video analysis...")
            
            # Load video
            video_capture = await self._load_video(video_input)
            
            # Extract basic video properties
            video_properties = await self._extract_video_properties(video_capture)
            
            # Initialize analysis options
            options = analysis_options or {}
            
            # Perform comprehensive analysis
            analysis_results = {
                'video_properties': video_properties,
                'processing_timestamp': datetime.now().isoformat(),
                'analysis_version': self.version
            }
            
            # Scene detection and analysis
            if options.get('scene_detection', True):
                scenes = await self._detect_scenes(video_capture)
                analysis_results['scenes'] = scenes
            
            # Motion analysis
            if options.get('motion_analysis', True):
                motion_data = await self._analyze_motion(video_capture)
                analysis_results['motion_analysis'] = motion_data
            
            # Object detection across frames
            if options.get('object_detection', True):
                objects = await self._detect_objects_in_video(video_capture)
                analysis_results['detected_objects'] = objects
            
            # Quality assessment
            if options.get('quality_assessment', True):
                quality = await self._assess_video_quality(video_capture)
                analysis_results['quality_metrics'] = quality
            
            # Generate video thumbnails
            if options.get('thumbnail_generation', True):
                thumbnails = await self._generate_thumbnails(video_capture)
                analysis_results['thumbnails'] = thumbnails
            
            # Audio analysis if available
            if options.get('audio_analysis', True) and isinstance(video_input, str):
                audio_analysis = await self._analyze_audio_track(video_input)
                analysis_results['audio_analysis'] = audio_analysis
            
            # Generate video fingerprint
            video_fingerprint = await self._generate_video_fingerprint(video_capture)
            analysis_results['video_fingerprint'] = video_fingerprint
            
            video_capture.release()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            analysis_results['processing_time'] = processing_time
            analysis_results['status'] = 'completed'
            
            logger.info(f"Video analysis completed in {processing_time:.2f}s")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }

    async def _load_video(self, video_input: Union[str, bytes]) -> cv2.VideoCapture:
        """Load video from file path or binary data"""
        if isinstance(video_input, str):
            # Load from file path
            cap = cv2.VideoCapture(video_input)
            if not cap.isOpened():
                raise VideoProcessingError(f"Failed to open video file: {video_input}")
            return cap
        
        elif isinstance(video_input, bytes):
            # Save binary data to temporary file and load
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
                tmp_file.write(video_input)
                tmp_path = tmp_file.name
            
            cap = cv2.VideoCapture(tmp_path)
            if not cap.isOpened():
                raise VideoProcessingError("Failed to open video from binary data")
            return cap
        
        else:
            raise ValidationError("Video input must be file path or binary data")

    async def _extract_video_properties(self, video_capture: cv2.VideoCapture) -> Dict[str, Any]:
        """Extract comprehensive video properties"""
        try:
            properties = {
                'frame_count': int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)),
                'fps': video_capture.get(cv2.CAP_PROP_FPS),
                'width': int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'duration_seconds': 0,
                'codec': int(video_capture.get(cv2.CAP_PROP_FOURCC)),
                'bitrate': video_capture.get(cv2.CAP_PROP_BITRATE) if hasattr(cv2, 'CAP_PROP_BITRATE') else None
            }
            
            # Calculate duration
            if properties['fps'] > 0:
                properties['duration_seconds'] = properties['frame_count'] / properties['fps']
                properties['duration_formatted'] = str(timedelta(seconds=int(properties['duration_seconds'])))
            
            # Calculate resolution category
            total_pixels = properties['width'] * properties['height']
            if total_pixels >= 3840 * 2160:
                properties['resolution_category'] = '4K'
            elif total_pixels >= 1920 * 1080:
                properties['resolution_category'] = 'Full HD'
            elif total_pixels >= 1280 * 720:
                properties['resolution_category'] = 'HD'
            else:
                properties['resolution_category'] = 'SD'
            
            # Aspect ratio
            if properties['height'] > 0:
                aspect_ratio = properties['width'] / properties['height']
                properties['aspect_ratio'] = round(aspect_ratio, 2)
                
                # Common aspect ratio detection
                if abs(aspect_ratio - 16/9) < 0.1:
                    properties['aspect_ratio_name'] = '16:9'
                elif abs(aspect_ratio - 4/3) < 0.1:
                    properties['aspect_ratio_name'] = '4:3'
                elif abs(aspect_ratio - 1) < 0.1:
                    properties['aspect_ratio_name'] = '1:1'
                else:
                    properties['aspect_ratio_name'] = 'custom'
            
            return properties
            
    
    async def _prepare_video_input(self, video_input: Union[str, bytes]) -> str:
        """Prepare video input for processing"""
        
        if isinstance(video_input, str):
            # File path provided
            if not os.path.exists(video_input):
                raise ValidationError(f"Video file not found: {video_input}")
            return video_input
            
        elif isinstance(video_input, bytes):
            # Bytes provided - save to temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.mp4', 
                delete=False, 
                dir=self.config.storage.temp_path
            )
            
            with temp_file:
                temp_file.write(video_input)
            
            return temp_file.name
        
        else:
            raise ValidationError("Unsupported video input type")

    async def _extract_video_info(self, video_path: str) -> Optional[Dict[str, Any]]:
        """Extract comprehensive video information using FFmpeg"""
        try:
            # Use ffprobe to get detailed video information
            probe_result = ffmpeg.probe(video_path)
            
            video_stream = None
            audio_stream = None
            
            # Find video and audio streams
            for stream in probe_result['streams']:
                if stream['codec_type'] == 'video' and video_stream is None:
                    video_stream = stream
                elif stream['codec_type'] == 'audio' and audio_stream is None:
                    audio_stream = stream
            
            if not video_stream:
                raise VideoProcessingError("No video stream found")
            
            # Extract video information
            info = {
                'duration': float(probe_result['format']['duration']),
                'file_size': int(probe_result['format']['size']),
                'bitrate': int(probe_result['format']['bit_rate']),
                'format_name': probe_result['format']['format_name'],
                
                # Video stream info
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'fps': eval(video_stream['r_frame_rate']),  # Convert fraction to float
                'codec': video_stream['codec_name'],
                'pix_fmt': video_stream.get('pix_fmt', 'unknown'),
                'frame_count': int(video_stream.get('nb_frames', 0)),
                
                # Audio info
                'has_audio': audio_stream is not None,
                'audio_codec': audio_stream['codec_name'] if audio_stream else None,
                'sample_rate': int(audio_stream['sample_rate']) if audio_stream else None,
                'channels': int(audio_stream['channels']) if audio_stream else None,
                
                # Additional metadata
                'metadata': probe_result['format'].get('tags', {})
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to extract video info: {e}")
            return None

    async def _validate_video(self, video_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate video against constraints"""
        validation_result = {'valid': True, 'errors': [], 'warnings': []}
        
        # Check file size
        if video_info['file_size'] > self.max_file_size:
            validation_result['errors'].append(
                f"File size ({video_info['file_size']} bytes) exceeds limit ({self.max_file_size} bytes)"
            )
            validation_result['valid'] = False
        
        # Check duration
        if video_info['duration'] > self.max_duration:
            validation_result['errors'].append(
                f"Duration ({video_info['duration']}s) exceeds limit ({self.max_duration}s)"
            )
            validation_result['valid'] = False
        
        # Check resolution
        width, height = video_info['width'], video_info['height']
        max_w, max_h = self.max_resolution
        min_w, min_h = self.min_resolution
        
        if width > max_w or height > max_h:
            validation_result['warnings'].append(
                f"Resolution ({width}x{height}) exceeds recommended maximum ({max_w}x{max_h})"
            )
        
        if width < min_w or height < min_h:
            validation_result['errors'].append(
                f"Resolution ({width}x{height}) below minimum ({min_w}x{min_h})"
            )
            validation_result['valid'] = False
        
        # Check frame rate
        if video_info['fps'] > 120:
            validation_result['warnings'].append(
                f"High frame rate ({video_info['fps']} fps) may impact processing performance"
            )
        
        return validation_result

    async def _analyze_video_frames(self, 
                                   video_path: str,
                                   analysis_type: VideoAnalysisType,
                                   custom_options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze video frames comprehensively"""
        
        sampling_rate = self.frame_sampling_rates[analysis_type]
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise VideoProcessingError(f"Cannot open video file: {video_path}")
        
        try:
            frames_data = []
            key_frames = []
            objects_timeline = defaultdict(list)
            faces_timeline = defaultdict(list)
            
            frame_number = 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Initialize motion detection if needed
            bg_subtractor = self.bg_subtractors.get('mog2') if hasattr(self, 'bg_subtractors') else None
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames based on analysis type
                if frame_number % sampling_rate == 0:
                    timestamp = frame_number / fps
                    
                    # Basic frame analysis
                    frame_quality = await self._analyze_frame_quality(frame)
                    motion_score = await self._calculate_motion_score(frame, bg_subtractor)
                    
                    # Advanced analysis for comprehensive modes
                    objects_detected = []
                    faces_detected = []
                    
                    if analysis_type in [VideoAnalysisType.COMPREHENSIVE, VideoAnalysisType.PROFESSIONAL]:
                        # Object detection (simplified - would use actual YOLO model)
                        objects_detected = await self._detect_objects_in_frame(frame)
                        
                        # Face detection
                        faces_detected = await self._detect_faces_in_frame(frame)
                    
                    # Create frame data
                    frame_data = VideoFrame(
                        frame_number=frame_number,
                        timestamp=timestamp,
                        image=frame.copy(),
                        quality_score=frame_quality,
                        motion_score=motion_score,
                        scene_type=self._classify_scene_type(motion_score),
                        objects_detected=objects_detected,
                        faces_detected=faces_detected
                    )
                    
                    frames_data.append(frame_data)
                    
                    # Identify key frames
                    if self._is_key_frame(frame_data, frames_data):
                        key_frames.append(frame_data)
                    
                    # Update timelines
                    for obj in objects_detected:
                        objects_timeline[obj['class']].append((timestamp, timestamp + 1/fps))
                    
                    for face in faces_detected:
                        face_id = face.get('person_id', 'unknown')
                        faces_timeline[face_id].append((timestamp, timestamp + 1/fps))
                
                frame_number += 1
                
                # Progress logging
                if frame_number % 1000 == 0:
                    progress = (frame_number / total_frames) * 100
                    logger.info(f"Frame analysis progress: {progress:.1f}%")
            
            return {
                'frames_data': frames_data,
                'key_frames': key_frames,
                'objects_timeline': dict(objects_timeline),
                'faces_timeline': dict(faces_timeline),
                'total_frames': frame_number,
                'fps': fps
            }
            
        finally:
            cap.release()

    async def _analyze_frame_quality(self, frame: np.ndarray) -> float:
        """Analyze quality of individual frame"""
        try:
            # Use image processor for detailed quality analysis
            metrics = await self.image_processor.assess_quality(frame)
            
            # Calculate composite quality score
            quality_factors = [
                metrics.blur_score / 1000,  # Normalize blur score
                1.0 - (metrics.noise_level / 100),  # Invert noise (lower is better)
                metrics.brightness_score,
                metrics.contrast_score,
                metrics.sharpness_score
            ]
            
            return np.mean(quality_factors)
            
        except:
            # Fallback to simple quality assessment
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            return min(laplacian_var / 1000, 1.0)

    async def _calculate_motion_score(self, frame: np.ndarray, bg_subtractor) -> float:
        """Calculate motion intensity in frame"""
        try:
            if bg_subtractor is None:
                return 0.0
            
            # Apply background subtraction
            fg_mask = bg_subtractor.apply(frame)
            
            # Calculate motion as percentage of foreground pixels
            motion_pixels = np.sum(fg_mask > 0)
            total_pixels = fg_mask.shape[0] * fg_mask.shape[1]
            
            return motion_pixels / total_pixels
            
        except:
            return 0.0

    def _classify_scene_type(self, motion_score: float) -> SceneType:
        """Classify scene type based on motion score"""
        if motion_score < 0.01:
            return SceneType.STATIC
        elif motion_score < 0.05:
            return SceneType.LOW_MOTION
        elif motion_score < 0.2:
            return SceneType.HIGH_MOTION
        else:
            return SceneType.TRANSITION

    async def _detect_objects_in_frame(self, frame: np.ndarray) -> List[Dict]:
        """Detect objects in frame (simplified implementation)"""
        # In production, this would use actual YOLO or other object detection model
        # For now, return placeholder data
        return []

    async def _detect_faces_in_frame(self, frame: np.ndarray) -> List[Dict]:
        """Detect faces in frame"""
        try:
            if not hasattr(self, 'face_detector') or self.face_detector is None:
                return []
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector(gray)
            
            face_data = []
            for i, face in enumerate(faces):
                x, y, w, h = face.left(), face.top(), face.width(), face.height()
                face_data.append({
                    'bbox': [x, y, w, h],
                    'confidence': 0.9,  # Placeholder
                    'person_id': f'person_{i}'  # Would be actual face recognition ID
                })
            
            return face_data
            
        except:
            return []

    def _is_key_frame(self, current_frame: VideoFrame, frames_history: List[VideoFrame]) -> bool:
        """Determine if current frame is a key frame"""
        if len(frames_history) < 2:
            return True
        
        # Key frame criteria
        criteria = [
            # High quality frame
            current_frame.quality_score > 0.8,
            
            # Scene transition
            current_frame.scene_type in [SceneType.TRANSITION, SceneType.CUT],
            
            # Significant motion change
            len(frames_history) > 0 and abs(
                current_frame.motion_score - frames_history[-1].motion_score
            ) > 0.1,
            
            # Regular interval (every 30 seconds)
            current_frame.timestamp > 0 and current_frame.timestamp % 30 < 1.0
        ]
        
        return any(criteria)

    async def _perform_temporal_analysis(self, frames_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform temporal analysis to identify patterns and segments"""
        
        frames_data = frames_analysis['frames_data']
        fps = frames_analysis['fps']
        
        # Segment video based on scene changes and motion patterns
        segments = await self._segment_video(frames_data, fps)
        
        # Analyze dominant themes
        dominant_themes = await self._analyze_dominant_themes(frames_data)
        
        # Create mood timeline
        mood_timeline = await self._create_mood_timeline(frames_data)
        
        # Analyze temporal patterns
        temporal_patterns = await self._analyze_temporal_patterns(frames_data)
        
        return {
            'segments': segments,
            'dominant_themes': dominant_themes,
            'mood_timeline': mood_timeline,
            'temporal_patterns': temporal_patterns
        }

    async def _segment_video(self, frames_data: List[VideoFrame], fps: float) -> List[VideoSegment]:
        """Segment video into coherent scenes"""
        
        segments = []
        current_segment_start = 0
        
        for i in range(1, len(frames_data)):
            current_frame = frames_data[i]
            prev_frame = frames_data[i-1]
            
            # Detect segment boundary
            if self._is_segment_boundary(current_frame, prev_frame):
                # Create segment for previous section
                segment = self._create_video_segment(
                    frames_data[current_segment_start:i],
                    current_segment_start,
                    i-1,
                    fps
                )
                segments.append(segment)
                current_segment_start = i
        
        # Create final segment
        if current_segment_start < len(frames_data):
            segment = self._create_video_segment(
                frames_data[current_segment_start:],
                current_segment_start,
                len(frames_data)-1,
                fps
            )
            segments.append(segment)
        
        return segments

    def _is_segment_boundary(self, current_frame: VideoFrame, prev_frame: VideoFrame) -> bool:
        """Determine if there's a segment boundary between frames"""
        
        # Scene type change
        if current_frame.scene_type != prev_frame.scene_type:
            return True
        
        # Significant quality change
        if abs(current_frame.quality_score - prev_frame.quality_score) > 0.3:
            return True
        
        # Significant motion change
        if abs(current_frame.motion_score - prev_frame.motion_score) > 0.2:
            return True
        
        return False

    def _create_video_segment(self, 
                            segment_frames: List[VideoFrame],
                            start_idx: int,
                            end_idx: int,
                            fps: float) -> VideoSegment:
        """Create VideoSegment from frame data"""
        
        if not segment_frames:
            return None
        
        start_frame = segment_frames[0]
        end_frame = segment_frames[-1]
        
        # Calculate segment statistics
        quality_scores = [f.quality_score for f in segment_frames]
        motion_scores = [f.motion_score for f in segment_frames]
        
        # Find key frames in segment
        key_frame_indices = [
            i for i, f in enumerate(segment_frames)
            if f in [frame for frame in segment_frames if self._is_key_frame(f, segment_frames[:i])]
        ]
        
        # Analyze dominant colors (simplified)
        dominant_colors = self._extract_dominant_colors(segment_frames)
        
        return VideoSegment(
            start_frame=start_frame.frame_number,
            end_frame=end_frame.frame_number,
            start_time=start_frame.timestamp,
            end_time=end_frame.timestamp,
            duration=end_frame.timestamp - start_frame.timestamp,
            scene_type=self._determine_segment_scene_type(segment_frames),
            average_quality=np.mean(quality_scores),
            motion_intensity=np.mean(motion_scores),
            key_frames=key_frame_indices,
            dominant_colors=dominant_colors
        )

    def _determine_segment_scene_type(self, frames: List[VideoFrame]) -> SceneType:
        """Determine overall scene type for segment"""
        scene_types = [f.scene_type for f in frames]
        # Return most common scene type
        return max(set(scene_types), key=scene_types.count)

    def _extract_dominant_colors(self, frames: List[VideoFrame]) -> List[Tuple[int, int, int]]:
        """Extract dominant colors from segment frames"""
        try:
            if not frames:
                return []
            
            # Sample a few frames from the segment
            sample_frames = frames[::max(1, len(frames)//5)]
            
            all_colors = []
            for frame in sample_frames[:3]:  # Use max 3 frames
                # Resize image for faster processing
                small_frame = cv2.resize(frame.image, (50, 50))
                colors = small_frame.reshape(-1, 3)
                all_colors.extend(colors)
            
            if not all_colors:
                return []
            
            # Cluster colors to find dominant ones
            all_colors = np.array(all_colors)
            
            # Use KMeans to find 5 dominant colors
            try:
                kmeans = KMeans(n_clusters=min(5, len(all_colors)), random_state=42, n_init=10)
                kmeans.fit(all_colors)
                
                # Return dominant colors as tuples
                dominant_colors = []
                for center in kmeans.cluster_centers_:
                    color = tuple(map(int, center))
                    dominant_colors.append(color)
                
                return dominant_colors
            except:
                return []
                
        except:
            return []

    async def _analyze_dominant_themes(self, frames_data: List[VideoFrame]) -> List[str]:
        """Analyze dominant themes in video content"""
        
        themes = []
        
        # Analyze object presence
        all_objects = defaultdict(int)
        for frame in frames_data:
            if frame.objects_detected:
                for obj in frame.objects_detected:
                    all_objects[obj['class']] += 1
        
        # Identify dominant object types
        if all_objects:
            sorted_objects = sorted(all_objects.items(), key=lambda x: x[1], reverse=True)
            themes.extend([obj[0] for obj in sorted_objects[:5]])  # Top 5 objects
        
        # Analyze motion patterns
        motion_scores = [f.motion_score for f in frames_data]
        avg_motion = np.mean(motion_scores)
        
        if avg_motion > 0.1:
            themes.append("high_activity")
        elif avg_motion < 0.02:
            themes.append("static_content")
        
        # Analyze scene types
        scene_types = [f.scene_type for f in frames_data]
        scene_type_counts = defaultdict(int)
        for scene_type in scene_types:
            scene_type_counts[scene_type] += 1
        
        dominant_scene = max(scene_type_counts, key=scene_type_counts.get)
        themes.append(f"primarily_{dominant_scene.value}")
        
        return themes

    async def _create_mood_timeline(self, frames_data: List[VideoFrame]) -> List[Tuple[float, str, float]]:
        """Create mood timeline based on visual analysis"""
        
        mood_timeline = []
        
        # Analyze in 10-second windows
        window_size = 10  # seconds
        current_time = 0
        
        while current_time < frames_data[-1].timestamp if frames_data else 0:
            window_end = current_time + window_size
            
            # Get frames in current window
            window_frames = [
                f for f in frames_data
                if current_time <= f.timestamp < window_end
            ]
            
            if window_frames:
                # Analyze mood based on motion, quality, and content
                mood, confidence = self._analyze_window_mood(window_frames)
                mood_timeline.append((current_time, mood, confidence))
            
            current_time += window_size
        
        return mood_timeline

    def _analyze_window_mood(self, frames: List[VideoFrame]) -> Tuple[str, float]:
        """Analyze mood for a window of frames"""
        
        if not frames:
            return "neutral", 0.0
        
        # Calculate metrics for mood analysis
        avg_motion = np.mean([f.motion_score for f in frames])
        avg_quality = np.mean([f.quality_score for f in frames])
        
        # Simple mood classification
        if avg_motion > 0.15:
            mood = "energetic"
            confidence = min(avg_motion * 2, 1.0)
        elif avg_motion < 0.02 and avg_quality > 0.7:
            mood = "calm"
            confidence = avg_quality
        elif avg_quality < 0.4:
            mood = "chaotic"
            confidence = 1.0 - avg_quality
        else:
            mood = "neutral"
            confidence = 0.5
        
        return mood, confidence

    async def _analyze_temporal_patterns(self, frames_data: List[VideoFrame]) -> Dict[str, Any]:
        """Analyze temporal patterns in video"""
        
        patterns = {
            'motion_trends': self._analyze_motion_trends(frames_data),
            'quality_trends': self._analyze_quality_trends(frames_data),
            'scene_transitions': self._analyze_scene_transitions(frames_data),
            'rhythmic_patterns': self._analyze_rhythmic_patterns(frames_data)
        }
        
        return patterns

    def _analyze_motion_trends(self, frames_data: List[VideoFrame]) -> Dict[str, Any]:
        """Analyze motion trends over time"""
        
        motion_scores = [f.motion_score for f in frames_data]
        timestamps = [f.timestamp for f in frames_data]
        
        return {
            'average_motion': np.mean(motion_scores),
            'motion_variance': np.var(motion_scores),
            'peak_motion_times': [
                timestamps[i] for i, score in enumerate(motion_scores)
                if score > np.mean(motion_scores) + 2 * np.std(motion_scores)
            ],
            'motion_trend': 'increasing' if motion_scores[-1] > motion_scores[0] else 'decreasing'
        }

    def _analyze_quality_trends(self, frames_data: List[VideoFrame]) -> Dict[str, Any]:
        """Analyze quality trends over time"""
        
        quality_scores = [f.quality_score for f in frames_data]
        
        return {
            'average_quality': np.mean(quality_scores),
            'quality_consistency': 1.0 - np.std(quality_scores),
            'quality_drops': len([q for q in quality_scores if q < 0.3])
        }

    def _analyze_scene_transitions(self, frames_data: List[VideoFrame]) -> Dict[str, Any]:
        """Analyze scene transition patterns"""
        
        scene_types = [f.scene_type for f in frames_data]
        
        transitions = []
        for i in range(1, len(scene_types)):
            if scene_types[i] != scene_types[i-1]:
                transitions.append({
                    'from': scene_types[i-1].value,
                    'to': scene_types[i].value,
                    'timestamp': frames_data[i].timestamp
                })
        
        return {
            'transition_count': len(transitions),
            'transitions': transitions,
            'average_scene_duration': len(frames_data) / max(len(transitions), 1)
        }

    def _analyze_rhythmic_patterns(self, frames_data: List[VideoFrame]) -> Dict[str, Any]:
        """Analyze rhythmic patterns in motion and cuts"""
        
        # This would implement more sophisticated rhythm analysis
        # For now, return basic pattern information
        
        motion_scores = [f.motion_score for f in frames_data]
        
        # Simple rhythm detection based on motion peaks
        motion_peaks = []
        for i in range(1, len(motion_scores)-1):
            if (motion_scores[i] > motion_scores[i-1] and 
                motion_scores[i] > motion_scores[i+1] and
                motion_scores[i] > np.mean(motion_scores)):
                motion_peaks.append(frames_data[i].timestamp)
        
        # Calculate rhythm
        if len(motion_peaks) > 1:
            intervals = [motion_peaks[i+1] - motion_peaks[i] for i in range(len(motion_peaks)-1)]
            avg_interval = np.mean(intervals)
            rhythm_consistency = 1.0 - (np.std(intervals) / avg_interval) if avg_interval > 0 else 0
        else:
            avg_interval = 0
            rhythm_consistency = 0
        
        return {
            'rhythm_detected': len(motion_peaks) > 2,
            'average_beat_interval': avg_interval,
            'rhythm_consistency': rhythm_consistency,
    
    async def _analyze_audio_track(self, video_path: str) -> Optional[Dict[str, Any]]:
        """Analyze audio track of video"""
        try:
            # Extract audio using moviepy
            audio_clip = AudioFileClip(video_path)
            
            # Get audio array
            audio_array = audio_clip.to_soundarray(fps=self.audio_params['sample_rate'])
            
            if len(audio_array.shape) == 2:
                # Convert stereo to mono
                audio_array = np.mean(audio_array, axis=1)
            
            # Basic audio analysis
            audio_features = {
                'duration': audio_clip.duration,
                'sample_rate': self.audio_params['sample_rate'],
                'rms_energy': np.sqrt(np.mean(audio_array**2)),
                'zero_crossing_rate': np.mean(librosa.zero_crossings(audio_array)),
                'spectral_centroid': np.mean(librosa.feature.spectral_centroid(y=audio_array, sr=self.audio_params['sample_rate'])),
                'tempo': librosa.beat.tempo(y=audio_array, sr=self.audio_params['sample_rate'])[0]
            }
            
            audio_clip.close()
            return audio_features
            
        except Exception as e:
            logger.warning(f"Audio analysis failed: {e}")
            return None

    async def _generate_video_metrics(self,
                                     video_info: Dict[str, Any],
                                     frames_analysis: Dict[str, Any],
                                     temporal_analysis: Dict[str, Any],
                                     audio_analysis: Optional[Dict[str, Any]]) -> VideoMetrics:
        """Generate comprehensive video metrics"""
        
        frames_data = frames_analysis['frames_data']
        
        # Calculate quality metrics
        quality_scores = [f.quality_score for f in frames_data]
        average_quality = np.mean(quality_scores)
        quality_consistency = 1.0 - np.std(quality_scores)
        
        # Determine overall quality level
        if average_quality >= 0.8:
            overall_quality = VideoQuality.EXCELLENT
        elif average_quality >= 0.6:
            overall_quality = VideoQuality.GOOD
        elif average_quality >= 0.4:
            overall_quality = VideoQuality.FAIR
        elif average_quality >= 0.2:
            overall_quality = VideoQuality.POOR
        else:
            overall_quality = VideoQuality.UNACCEPTABLE
        
        # Motion analysis
        motion_scores = [f.motion_score for f in frames_data]
        motion_analysis = {
            'average_motion': np.mean(motion_scores),
            'motion_variance': np.var(motion_scores),
            'peak_motion': np.max(motion_scores),
            'static_percentage': len([m for m in motion_scores if m < 0.01]) / len(motion_scores) * 100
        }
        
        # Content analysis
        segments = temporal_analysis.get('segments', [])
        transitions = temporal_analysis.get('temporal_patterns', {}).get('scene_transitions', {}).get('transitions', [])
        
        # Face time calculation
        faces_timeline = frames_analysis.get('faces_timeline', {})
        total_face_time = 0
        for face_id, intervals in faces_timeline.items():
            for start, end in intervals:
                total_face_time += (end - start)
        face_time_percentage = (total_face_time / video_info['duration']) * 100 if video_info['duration'] > 0 else 0
        
        # Object diversity
        objects_timeline = frames_analysis.get('objects_timeline', {})
        object_diversity = len(objects_timeline.keys()) / max(1, len(frames_data) / 100)  # Objects per 100 frames
        
        # Color variance (simplified)
        color_variance = self._calculate_color_variance(frames_data)
        
        # Temporal complexity
        temporal_complexity = len(transitions) / max(1, video_info['duration'] / 60)  # Transitions per minute
        
        # Audio quality
        audio_quality = None
        if audio_analysis:
            # Simple audio quality assessment
            rms = audio_analysis.get('rms_energy', 0)
            audio_quality = min(rms * 10, 1.0)  # Normalize to 0-1
        
        # Technical metrics
        compression_efficiency = self._calculate_compression_efficiency(video_info)
        encoding_quality = self._assess_encoding_quality(video_info)
        
        return VideoMetrics(
            resolution=(video_info['width'], video_info['height']),
            fps=video_info['fps'],
            duration=video_info['duration'],
            bitrate=video_info['bitrate'],
            codec=video_info['codec'],
            file_size_bytes=video_info['file_size'],
            
            # Quality metrics
            overall_quality=overall_quality,
            average_frame_quality=average_quality,
            quality_consistency=quality_consistency,
            motion_analysis=motion_analysis,
            audio_quality=audio_quality,
            
            # Content metrics
            scene_count=len(segments),
            transition_count=len(transitions),
            face_time_percentage=face_time_percentage,
            object_diversity=object_diversity,
            color_variance=color_variance,
            temporal_complexity=temporal_complexity,
            
            # Technical metrics
            compression_efficiency=compression_efficiency,
            encoding_quality=encoding_quality,
            frame_drops=0,  # Would be calculated from analysis
            sync_issues=0   # Would be detected during analysis
        )

    def _calculate_color_variance(self, frames_data: List[VideoFrame]) -> float:
        """Calculate color variance across frames"""
        try:
            if not frames_data:
                return 0.0
            
            # Sample frames for color analysis
            sample_frames = frames_data[::max(1, len(frames_data)//20)]  # Sample 20 frames
            
            color_means = []
            for frame in sample_frames:
                # Calculate mean color for each channel
                mean_color = np.mean(frame.image.reshape(-1, 3), axis=0)
                color_means.append(mean_color)
            
            if not color_means:
                return 0.0
            
            # Calculate variance across frames
            color_variance = np.var(color_means, axis=0)
            return np.mean(color_variance) / (255 * 255)  # Normalize
            
        except:
            return 0.0

    def _calculate_compression_efficiency(self, video_info: Dict[str, Any]) -> float:
        """Calculate compression efficiency score"""
        
        # Theoretical uncompressed size
        width, height = video_info['width'], video_info['height']
        fps = video_info['fps']
        duration = video_info['duration']
        
        # Assuming 3 bytes per pixel (RGB) and given fps
        theoretical_size = width * height * 3 * fps * duration
        actual_size = video_info['file_size']
        
        if theoretical_size > 0:
            compression_ratio = actual_size / theoretical_size
            # Lower compression ratio = better efficiency
            efficiency = 1.0 - min(compression_ratio, 1.0)
            return efficiency
        
        return 0.5

    def _assess_encoding_quality(self, video_info: Dict[str, Any]) -> float:
        """Assess encoding quality based on technical parameters"""
        
        codec = video_info['codec'].lower()
        bitrate = video_info['bitrate']
        resolution = video_info['width'] * video_info['height']
        
        # Quality scoring based on codec
        codec_scores = {
            'h264': 0.8,
            'h265': 0.9,
            'hevc': 0.9,
            'vp9': 0.85,
            'vp8': 0.7,
            'mpeg4': 0.6,
            'xvid': 0.6
        }
        
        codec_score = codec_scores.get(codec, 0.5)
        
        # Bitrate adequacy for resolution
        # Higher resolution needs higher bitrate
        expected_bitrate = resolution * 0.1  # Rough estimate
        bitrate_ratio = min(bitrate / expected_bitrate, 2.0) / 2.0 if expected_bitrate > 0 else 0.5
        
        return (codec_score + bitrate_ratio) / 2

    async def _generate_video_thumbnails(self, video_path: str, key_frames: List[VideoFrame]) -> List[str]:
        """Generate thumbnail images from key frames"""
        
        thumbnails = []
        thumbnail_dir = Path(self.config.storage.temp_path) / "thumbnails"
        thumbnail_dir.mkdir(exist_ok=True)
        
        try:
            for i, frame in enumerate(key_frames[:10]):  # Limit to 10 thumbnails
                # Resize frame for thumbnail
                thumbnail = cv2.resize(frame.image, (320, 180))  # 16:9 aspect ratio
                
                # Save thumbnail
                thumbnail_path = thumbnail_dir / f"thumb_{i}_{frame.frame_number}.jpg"
                cv2.imwrite(str(thumbnail_path), thumbnail)
                thumbnails.append(str(thumbnail_path))
            
            return thumbnails
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return []

    def _generate_video_cache_key(self, video_path: str, analysis_type: VideoAnalysisType) -> str:
        """Generate cache key for video analysis results"""
        
        # Include file modification time for cache invalidation
        try:
            mtime = os.path.getmtime(video_path)
            path_hash = hashlib.md5(f"{video_path}_{mtime}".encode()).hexdigest()[:16]
        except:
            path_hash = hashlib.md5(video_path.encode()).hexdigest()[:16]
        
        return f"video_analysis_{path_hash}_{analysis_type.value}"

    async def extract_frames(self,
                           video_path: str,
                           frame_numbers: Optional[List[int]] = None,
                           timestamps: Optional[List[float]] = None,
                           interval_seconds: Optional[float] = None) -> List[np.ndarray]:
        """
        Extract specific frames from video
        
        Args:
            video_path: Path to video file
            frame_numbers: Specific frame numbers to extract
            timestamps: Specific timestamps to extract (in seconds)
            interval_seconds: Extract frames at regular intervals
            
        Returns:
            List of extracted frames as numpy arrays
        """
        
        frames = []
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise VideoProcessingError(f"Cannot open video: {video_path}")
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if frame_numbers:
                # Extract specific frame numbers
                for frame_num in frame_numbers:
                    if 0 <= frame_num < total_frames:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                        ret, frame = cap.read()
                        if ret:
                            frames.append(frame)
            
            elif timestamps:
                # Extract frames at specific timestamps
                for timestamp in timestamps:
                    frame_num = int(timestamp * fps)
                    if 0 <= frame_num < total_frames:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                        ret, frame = cap.read()
                        if ret:
                            frames.append(frame)
            
            elif interval_seconds:
                # Extract frames at regular intervals
                frame_interval = int(interval_seconds * fps)
                for frame_num in range(0, total_frames, frame_interval):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                    ret, frame = cap.read()
                    if ret:
                        frames.append(frame)
            
            return frames
            
        finally:
            cap.release()

    async def generate_video_summary(self, video_path: str) -> Dict[str, Any]:
        """
        Generate a comprehensive video summary
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing video summary information
        """
        
        try:
            # Perform basic analysis
            analysis_result = await self.analyze_video(
                video_path, 
                VideoAnalysisType.BASIC,
                extract_audio=True,
                generate_thumbnails=True
            )
            
            if not analysis_result.success:
                return {'error': 'Analysis failed', 'details': analysis_result.errors}
            
            # Create summary
            summary = {
                'basic_info': {
                    'duration': analysis_result.metrics.duration,
                    'resolution': f"{analysis_result.metrics.resolution[0]}x{analysis_result.metrics.resolution[1]}",
                    'fps': analysis_result.metrics.fps,
                    'codec': analysis_result.metrics.codec,
                    'file_size_mb': round(analysis_result.metrics.file_size_bytes / (1024*1024), 2),
                    'overall_quality': analysis_result.metrics.overall_quality.value
                },
                'content_analysis': {
                    'scene_count': analysis_result.metrics.scene_count,
                    'average_motion': analysis_result.metrics.motion_analysis.get('average_motion', 0),
                    'face_time_percentage': analysis_result.metrics.face_time_percentage,
                    'dominant_themes': analysis_result.dominant_themes
                },
                'technical_analysis': {
                    'compression_efficiency': analysis_result.metrics.compression_efficiency,
                    'encoding_quality': analysis_result.metrics.encoding_quality,
                    'bitrate': analysis_result.metrics.bitrate
                },
                'key_moments': [
                    {
                        'timestamp': frame.timestamp,
                        'quality_score': frame.quality_score,
                        'motion_score': frame.motion_score,
                        'scene_type': frame.scene_type.value
                    }
                    for frame in analysis_result.key_frames[:5]  # Top 5 key moments
                ],
                'thumbnails': analysis_result.thumbnails,
                'processing_time': analysis_result.processing_time
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Video summary generation failed: {e}")
            return {'error': str(e)}

    async def cleanup(self):
        """Cleanup resources and temporary files"""
        try:
            # Close thread pool
            if hasattr(self, 'thread_pool'):
                self.thread_pool.shutdown(wait=True)
            
            # Cleanup image processor
            if hasattr(self, 'image_processor'):
                await self.image_processor.cleanup()
            
            # Clear caches
            if hasattr(self, 'cache_manager'):
                await self.cache_manager.clear()
            
            # Clean temporary files
            temp_paths = [
                Path(self.config.storage.temp_path) / "video_frames",
                Path(self.config.storage.temp_path) / "thumbnails",
                Path(self.config.storage.temp_path) / "previews"
            ]
            
            for temp_path in temp_paths:
                if temp_path.exists():
                    for file in temp_path.glob("*"):
                        try:
                            file.unlink()
                        except:
                            pass
            
            logger.info("Video Analyzer cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    async def get_statistics(self) -> Dict[str, Any]:
        """Get video analyzer statistics"""
        return {
            'status': self.status.value,
            'version': self.version,
            'device': str(self.device) if hasattr(self, 'device') else 'unknown',
            'supported_formats': list(self.format_specs.keys()),
            'max_resolution': self.max_resolution,
            'max_duration': self.max_duration,
            'analysis_capabilities': [cap.value for cap in self.capabilities],
            'cache_enabled': self.config.performance.cache_enabled
        }
            
        except Exception as e:
            logger.error(f"Scene detection failed: {e}")
            return []

    async def _analyze_motion(self, video_capture: cv2.VideoCapture) -> Dict[str, Any]:
        """Analyze motion patterns in video"""
        motion_data = {
            'total_motion': 0,
            'motion_intensity': [],
            'motion_direction': [],
            'static_periods': [],
            'activity_level': 'unknown'
        }
        
        try:
            frame_number = 0
            motion_values = []
            
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break
                
                if frame_number % 5 == 0:  # Analyze every 5th frame
                    # Apply background subtraction
                    fg_mask = self.background_subtractor.apply(frame)
                    
                    # Calculate motion intensity
                    motion_pixels = np.sum(fg_mask == 255)
                    total_pixels = fg_mask.shape[0] * fg_mask.shape[1]
                    motion_percentage = (motion_pixels / total_pixels) * 100
                    
                    motion_values.append(motion_percentage)
                    motion_data['motion_intensity'].append({
                        'frame': frame_number,
                        'motion_percentage': motion_percentage,
                        'timestamp': frame_number / video_capture.get(cv2.CAP_PROP_FPS)
                    })
                
                frame_number += 1
            
            if motion_values:
                motion_data['total_motion'] = sum(motion_values)
                motion_data['average_motion'] = np.mean(motion_values)
                motion_data['max_motion'] = max(motion_values)
                motion_data['min_motion'] = min(motion_values)
                
                # Classify activity level
                avg_motion = motion_data['average_motion']
                if avg_motion > 20:
                    motion_data['activity_level'] = 'high'
                elif avg_motion > 5:
                    motion_data['activity_level'] = 'medium'
                else:
                    motion_data['activity_level'] = 'low'
                
                # Detect static periods (low motion)
                static_threshold = 2.0
                static_periods = []
                in_static_period = False
                static_start = 0
                
                for i, motion_val in enumerate(motion_values):
                    if motion_val < static_threshold:
                        if not in_static_period:
                            static_start = i
                            in_static_period = True
                    else:
                        if in_static_period:
                            static_periods.append({
                                'start_frame': static_start * 5,
                                'end_frame': (i - 1) * 5,
                                'duration_frames': (i - static_start) * 5
                            })
                            in_static_period = False
                
                motion_data['static_periods'] = static_periods
            
            # Reset video position
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            return motion_data
            
        except Exception as e:
            logger.error(f"Motion analysis failed: {e}")
            return motion_data

    async def _detect_objects_in_video(self, video_capture: cv2.VideoCapture) -> Dict[str, Any]:
        """Detect objects across video frames"""
        object_detections = {
            'total_detections': 0,
            'unique_objects': set(),
            'detection_timeline': [],
            'confidence_scores': []
        }
        
        try:
            # Note: This is a simplified implementation
            # In production, you would use YOLO, SSD, or other object detection models
            
            frame_number = 0
            cascade_face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            cascade_car = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_car.xml') if hasattr(cv2.data, 'haarcascades') else None
            
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break
                
                if frame_number % self.frame_extraction_interval == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Face detection
                    faces = cascade_face.detectMultiScale(gray, 1.1, 4)
                    
                    for (x, y, w, h) in faces:
                        object_detections['detection_timeline'].append({
                            'frame': frame_number,
                            'timestamp': frame_number / video_capture.get(cv2.CAP_PROP_FPS),
                            'object_type': 'face',
                            'bbox': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                            'confidence': 0.8  # Approximate confidence
                        })
                        object_detections['unique_objects'].add('face')
                        object_detections['total_detections'] += 1
                        object_detections['confidence_scores'].append(0.8)
                
                frame_number += 1
            
            # Convert set to list for JSON serialization
            object_detections['unique_objects'] = list(object_detections['unique_objects'])
            
            # Calculate statistics
            if object_detections['confidence_scores']:
                object_detections['average_confidence'] = np.mean(object_detections['confidence_scores'])
                object_detections['min_confidence'] = min(object_detections['confidence_scores'])
                object_detections['max_confidence'] = max(object_detections['confidence_scores'])
            
            # Reset video position
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            return object_detections
            
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return object_detections

    async def _assess_video_quality(self, video_capture: cv2.VideoCapture) -> Dict[str, Any]:
        """Assess technical quality of video"""
        quality_metrics = {
            'overall_score': 0.0,
            'resolution_score': 0.0,
            'framerate_score': 0.0,
            'stability_score': 0.0,
            'brightness_score': 0.0,
            'contrast_score': 0.0,
            'sharpness_score': 0.0,
            'noise_level': 0.0,
            'quality_issues': []
        }
        
        try:
            # Get video properties
            width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = video_capture.get(cv2.CAP_PROP_FPS)
            
            # Resolution quality assessment
            total_pixels = width * height
            if total_pixels >= 1920 * 1080:
                quality_metrics['resolution_score'] = 1.0
            elif total_pixels >= 1280 * 720:
                quality_metrics['resolution_score'] = 0.8
            elif total_pixels >= 854 * 480:
                quality_metrics['resolution_score'] = 0.6
            else:
                quality_metrics['resolution_score'] = 0.4
                quality_metrics['quality_issues'].append('Low resolution')
            
            # Framerate quality assessment
            if fps >= 60:
                quality_metrics['framerate_score'] = 1.0
            elif fps >= 30:
                quality_metrics['framerate_score'] = 0.9
            elif fps >= 24:
                quality_metrics['framerate_score'] = 0.7
            else:
                quality_metrics['framerate_score'] = 0.5
                quality_metrics['quality_issues'].append('Low framerate')
            
            # Sample frames for quality analysis
            frame_samples = []
            frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, frame_count // 20)  # Sample 20 frames
            
            for i in range(0, frame_count, sample_interval):
                video_capture.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = video_capture.read()
                if ret:
                    frame_samples.append(frame)
                if len(frame_samples) >= 20:
                    break
            
            if frame_samples:
                # Analyze frame quality
                brightness_scores = []
                contrast_scores = []
                sharpness_scores = []
                noise_scores = []
                
                for frame in frame_samples:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Brightness
                    brightness = np.mean(gray)
                    brightness_normalized = 1.0 - abs(brightness - 128) / 128
                    brightness_scores.append(brightness_normalized)
                    
                    # Contrast
                    contrast = gray.std()
                    contrast_normalized = min(contrast / 50.0, 1.0)
                    contrast_scores.append(contrast_normalized)
                    
                    # Sharpness (Laplacian variance)
                    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                    sharpness_normalized = min(sharpness / 1000.0, 1.0)
                    sharpness_scores.append(sharpness_normalized)
                    
                    # Noise estimation
                    noise = np.std(cv2.GaussianBlur(gray, (5, 5), 0) - gray)
                    noise_scores.append(noise)
                
                quality_metrics['brightness_score'] = np.mean(brightness_scores)
                quality_metrics['contrast_score'] = np.mean(contrast_scores)
                quality_metrics['sharpness_score'] = np.mean(sharpness_scores)
                quality_metrics['noise_level'] = np.mean(noise_scores)
                
                # Check for quality issues
                if quality_metrics['brightness_score'] < 0.5:
                    quality_metrics['quality_issues'].append('Poor brightness')
                if quality_metrics['contrast_score'] < 0.3:
                    quality_metrics['quality_issues'].append('Low contrast')
                if quality_metrics['sharpness_score'] < 0.3:
                    quality_metrics['quality_issues'].append('Blurry content')
                if quality_metrics['noise_level'] > 10:
                    quality_metrics['quality_issues'].append('High noise level')
            
            # Calculate overall score
            scores = [
                quality_metrics['resolution_score'] * 0.25,
                quality_metrics['framerate_score'] * 0.15,
                quality_metrics['brightness_score'] * 0.2,
                quality_metrics['contrast_score'] * 0.2,
                quality_metrics['sharpness_score'] * 0.2
            ]
            
            quality_metrics['overall_score'] = sum(scores)
            
            # Reset video position
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return quality_metrics

    async def _generate_thumbnails(
        self, 
        video_capture: cv2.VideoCapture,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate video thumbnails"""
        thumbnails = []
        
        try:
            frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = video_capture.get(cv2.CAP_PROP_FPS)
            
            # Calculate frame positions for thumbnails
            if frame_count > count:
                interval = frame_count // (count + 1)
                frame_positions = [interval * (i + 1) for i in range(count)]
            else:
                frame_positions = list(range(frame_count))
            
            for i, frame_pos in enumerate(frame_positions):
                video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                ret, frame = video_capture.read()
                
                if ret:
                    # Resize thumbnail
                    height, width = frame.shape[:2]
                    thumb_width = 320
                    thumb_height = int((thumb_width / width) * height)
                    thumbnail = cv2.resize(frame, (thumb_width, thumb_height))
                    
                    # Convert to base64 for easy storage/transmission
                    _, buffer = cv2.imencode('.jpg', thumbnail, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    thumbnail_base64 = hashlib.md5(buffer).hexdigest()  # Use hash instead of base64 for privacy
                    
                    thumbnails.append({
                        'index': i,
                        'frame_position': int(frame_pos),
                        'timestamp': frame_pos / fps if fps > 0 else 0,
                        'dimensions': {'width': thumb_width, 'height': thumb_height},
                        'thumbnail_hash': thumbnail_base64
                    })
            
            # Reset video position
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            return thumbnails
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return []

    async def _analyze_audio_track(self, video_path: str) -> Dict[str, Any]:
        """Analyze audio track of video (placeholder for audio analysis)"""
        try:
            # This would typically use librosa or similar audio processing library
            # For now, return placeholder data
            audio_analysis = {
                'has_audio': True,
                'duration_seconds': 0,
                'sample_rate': 0,
                'channels': 0,
                'audio_codec': 'unknown',
                'analysis_note': 'Audio analysis requires additional audio processing libraries'
            }
            
            return audio_analysis
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {'has_audio': False, 'error': str(e)}

    async def _generate_video_fingerprint(self, video_capture: cv2.VideoCapture) -> str:
        """Generate unique fingerprint for video content"""
        try:
            fingerprint_data = []
            
            # Sample frames for fingerprinting
            frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, frame_count // 10)  # Sample 10 frames
            
            for i in range(0, frame_count, sample_interval):
                video_capture.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = video_capture.read()
                if ret:
                    # Convert to grayscale and resize for consistent fingerprinting
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    resized = cv2.resize(gray, (64, 64))
                    
                    # Calculate histogram
                    hist = cv2.calcHist([resized], [0], None, [256], [0, 256])
                    hist_normalized = hist.flatten() / np.sum(hist)
                    
                    # Add to fingerprint data
                    fingerprint_data.extend(hist_normalized[:32])  # Use first 32 bins
                
                if len(fingerprint_data) >= 320:  # Limit fingerprint size
                    break
            
            # Generate hash from fingerprint data
            fingerprint_str = ','.join([f"{x:.6f}" for x in fingerprint_data])
            video_fingerprint = hashlib.sha256(fingerprint_str.encode()).hexdigest()
            
            # Reset video position
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            return video_fingerprint
            
        except Exception as e:
            logger.error(f"Video fingerprint generation failed: {e}")
            return ""

    async def extract_frames(
        self, 
        video_input: Union[str, bytes],
        frame_interval: int = 30,
        max_frames: int = 100
    ) -> List[np.ndarray]:
        """Extract frames from video at specified intervals"""
        try:
            video_capture = await self._load_video(video_input)
            frames = []
            frame_number = 0
            
            while len(frames) < max_frames:
                ret, frame = video_capture.read()
                if not ret:
                    break
                
                if frame_number % frame_interval == 0:
                    frames.append(frame)
                
                frame_number += 1
            
            video_capture.release()
            return frames
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            return []

    async def get_video_duration(self, video_input: Union[str, bytes]) -> float:
        """Get video duration in seconds"""
        try:
            video_capture = await self._load_video(video_input)
            frame_count = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
            fps = video_capture.get(cv2.CAP_PROP_FPS)
            duration = frame_count / fps if fps > 0 else 0
            video_capture.release()
            return duration
        except Exception as e:
            logger.error(f"Duration extraction failed: {e}")
            return 0.0

    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            await self.performance_monitor.close()
            await self.content_validator.cleanup()
            logger.info("Video Analyzer cleanup completed")
        except Exception as e:
            logger.error(f"Video Analyzer cleanup failed: {e}")

    def get_supported_formats(self) -> List[str]:
        """Get list of supported video formats"""
        return self.supported_formats.copy()

    def get_analysis_capabilities(self) -> Dict[str, bool]:
        """Get available analysis capabilities"""
        return self.analysis_capabilities.copy()
