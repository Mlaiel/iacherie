"""Video Content Management Module - Professional Video Content Processing System

Module spécialisé pour la gestion, l'analyse et la protection du contenu vidéo
dans la plateforme IA Influencer Agent.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Computer Vision Expert, Video Processing Specialist, Content Protection Expert
Copyright: Fahed Mlaiel - All rights reserved

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import logging
import hashlib
import json
import asyncio
from enum import Enum

import cv2
import numpy as np
from PIL import Image
import imageio

logger = logging.getLogger(__name__)

class VideoFormat(Enum):
    """
Supported video formats with technical specifications"""

    MP4 = {"ext": ".mp4", "container": "MP4", "codecs": ["H.264", "H.265"], "quality": "excellent"}
    AVI = {"ext": ".avi", "container": "AVI", "codecs": ["XVID", "DivX"], "quality": "good"}
    MOV = {"ext": ".mov", "container": "QuickTime", "codecs": ["H.264", "ProRes"], "quality": "excellent"}
    WEBM = {"ext": ".webm", "container": "WebM", "codecs": ["VP8", "VP9"], "quality": "good"}
    MKV = {"ext": ".mkv", "container": "Matroska", "codecs": ["H.264", "H.265"], "quality": "excellent"}
    FLV = {"ext": ".flv", "container": "Flash Video", "codecs": ["H.264", "VP6"], "quality": "fair"}
    WMV = {"ext": ".wmv", "container": "Windows Media", "codecs": ["WMV", "VC-1"], "quality": "good"}
    THREEGP = {"ext": ".3gp", "container": "3GPP", "codecs": ["H.263", "H.264"], "quality": "fair"}

class VideoContentType(Enum):
    """Video content classification types"""

    MOVIE = "movie"
    MUSIC_VIDEO = "music_video"
    DOCUMENTARY = "documentary"
    TUTORIAL = "tutorial"
    VLOG = "vlog"
    INTERVIEW = "interview"
    LIVESTREAM = "livestream"
    SHORT_FORM = "short_form"
    COMMERCIAL = "commercial"
    ANIMATION = "animation"
    SPORTS = "sports"
    NEWS = "news"
    GAMING = "gaming"
    EDUCATIONAL = "educational"

class VideoQuality(Enum):
    """Video quality classifications"""

    SD = {"resolution": "480p", "min_width": 640, "min_height": 480}
    HD = {"resolution": "720p", "min_width": 1280, "min_height": 720}
    FULL_HD = {"resolution": "1080p", "min_width": 1920, "min_height": 1080}
    QHD = {"resolution": "1440p", "min_width": 2560, "min_height": 1440}
    UHD_4K = {"resolution": "4K", "min_width": 3840, "min_height": 2160}
    UHD_8K = {"resolution": "8K", "min_width": 7680, "min_height": 4320}

@dataclass
class VideoMetadata:
    """Comprehensive video metadata structure"""
    # Technical metadata
    duration: float
    width: int
    height: int
    fps: float
    total_frames: int
    bit_rate: Optional[int] = None
    codec: Optional[str] = None
    container_format: Optional[str] = None
    file_size: Optional[int] = None
    aspect_ratio: Optional[str] = None
    
    # Audio track metadata
    has_audio: bool = False
    audio_codec: Optional[str] = None
    audio_channels: Optional[int] = None
    audio_sample_rate: Optional[int] = None
    audio_bit_rate: Optional[int] = None
    
    # Descriptive metadata
    title: Optional[str] = None
    description: Optional[str] = None
    creator: Optional[str] = None
    production_company: Optional[str] = None
    genre: Optional[str] = None
    release_date: Optional[datetime] = None
    language: Optional[str] = None
    subtitle_languages: List[str] = field(default_factory=list)
    
    # Rights and licensing
    copyright: Optional[str] = None
    license: Optional[str] = None
    content_rating: Optional[str] = None
    distribution_rights: Optional[str] = None
    
    # Video analysis metadata
    scene_count: Optional[int] = None
    shot_count: Optional[int] = None
    motion_intensity: Optional[float] = None
    color_variance: Optional[float] = None
    brightness_avg: Optional[float] = None
    contrast_avg: Optional[float] = None
    saturation_avg: Optional[float] = None
    
    # Content analysis
    content_type: Optional[VideoContentType] = None
    quality_level: Optional[VideoQuality] = None
    objects_detected: List[str] = field(default_factory=list)
    faces_detected: int = 0
    text_detected: bool = False
    
    # Quality metrics
    quality_score: Optional[float] = None
    compression_artifacts: Optional[float] = None
    noise_level: Optional[float] = None
    sharpness_score: Optional[float] = None
    exposure_quality: Optional[float] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    chapters: List[Dict[str, Any]] = field(default_factory=list)
    thumbnails: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VideoFingerprint:
    """
Video fingerprint for content identification and protection"""
    content_id: str
    primary_hash: str
    perceptual_hash: str
    frame_hash_sequence: List[str]
    motion_signature: str
    color_histogram_hash: str
    edge_density_hash: str
    temporal_features: Optional[np.ndarray] = None
    spatial_features: Optional[np.ndarray] = None
    optical_flow_features: Optional[np.ndarray] = None
    scene_signatures: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_score: float = 0.0
    quality_indicators: Dict[str, float] = field(default_factory=dict)

@dataclass
class VideoScene:
    """
Video scene detection and analysis"""
    scene_id: str
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    duration: float
    representative_frame: Optional[np.ndarray] = None
    scene_type: Optional[str] = None
    motion_level: Optional[float] = None
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    objects_detected: List[str] = field(default_factory=list)
    confidence_score: float = 0.0

class VideoContentManager:
    """
    Professional video content management system with advanced processing capabilities
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Video Content Manager
        
        Args:
            config: Configuration dictionary for video processing
        """
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.VideoContentManager")
        self.supported_formats = [fmt.value["ext"] for fmt in VideoFormat]
        
        # Initialize processing components
        self._init_components()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for video processing"""
        return {
            "max_file_size_mb": 1000,
            "max_processing_duration": 600,  # 10 minutes
            "frame_sampling_rate": 1.0,  # Process every frame
            "scene_detection_threshold": 30.0,
            "enable_fingerprinting": True,
            "enable_scene_detection": True,
            "enable_object_detection": False,  # Requires additional models
            "enable_face_detection": True,
            "enable_quality_analysis": True,
            "thumbnail_count": 5,
            "max_frames_for_analysis": 300,
            "optical_flow_analysis": True,
            "color_analysis": True,
            "motion_analysis": True
        }
    
    def _init_components(self):
        """Initialize video processing components"""
        self.logger.info("Initializing Video Content Manager components...")
        
        # OpenCV configuration
        self.face_cascade = None
        try:
            # Load face detection classifier
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        except Exception as e:
            self.logger.warning(f"Face detection not available: {e}")
        
        # Video analysis parameters
        self.analysis_config = {
            "histogram_bins": 256,
            "edge_threshold": 100,
            "motion_threshold": 2.0,
            "scene_threshold": 30.0
        }
        
        self.logger.info("Video Content Manager initialized successfully")
    
    async def process_video_file(
        self,
        file_path: Union[str, Path],
        extract_metadata: bool = True,
        generate_fingerprint: bool = True,
        scene_detection: bool = True,
        quality_analysis: bool = True,
        generate_thumbnails: bool = True
    ) -> Dict[str, Any]:
        """
        Process video file with comprehensive analysis
        
        Args:
            file_path: Path to video file
            extract_metadata: Whether to extract metadata
            generate_fingerprint: Whether to generate fingerprint
            scene_detection: Whether to detect scenes
            quality_analysis: Whether to perform quality analysis
            generate_thumbnails: Whether to generate thumbnails
            
        Returns:
            Dict containing processed video information
        """
        try:
            file_path = Path(file_path)
            self.logger.info(f"Processing video file: {file_path}")
            
            # Validate file
            if not await self._validate_video_file(file_path):
                raise ValueError(f"Invalid video file: {file_path}")
            
            # Open video file
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {file_path}")
            
            try:
                # Get basic video properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                duration = total_frames / fps if fps > 0 else 0
                
                results = {
                    "file_path": str(file_path),
                    "file_size": file_path.stat().st_size,
                    "processing_timestamp": datetime.now(timezone.utc),
                    "basic_properties": {
                        "width": width,
                        "height": height,
                        "fps": fps,
                        "total_frames": total_frames,
                        "duration": duration
                    }
                }
                
                # Load frames for analysis
                frames = await self._extract_frames_for_analysis(cap, total_frames)
                results["frames_analyzed"] = len(frames)
                
                # Extract metadata
                if extract_metadata:
                    metadata = await self._extract_video_metadata(file_path, cap, frames)
                    results["metadata"] = metadata
                
                # Generate fingerprint
                if generate_fingerprint:
                    fingerprint = await self._generate_video_fingerprint(frames, str(file_path))
                    results["fingerprint"] = fingerprint
                
                # Scene detection
                if scene_detection and len(frames) > 1:
                    scenes = await self._detect_video_scenes(frames, fps)
                    results["scenes"] = scenes
                
                # Quality analysis
                if quality_analysis:
                    quality_metrics = await self._analyze_video_quality(frames)
                    results["quality_metrics"] = quality_metrics
                
                # Generate thumbnails
                if generate_thumbnails:
                    thumbnails = await self._generate_thumbnails(frames)
                    results["thumbnails"] = thumbnails
                
                # Content classification
                content_type = await self._classify_video_content(frames, metadata if extract_metadata else None)
                results["content_classification"] = content_type
                
                self.logger.info(f"Video processing completed for: {file_path}")
                return results
                
            finally:
                cap.release()
                
        except Exception as e:
            self.logger.error(f"Failed to process video file {file_path}: {e}")
            raise
    
    async def _validate_video_file(self, file_path: Path) -> bool:
        """Validate video file format and accessibility"""
        try:
            # Check file existence and size
            if not file_path.exists():
                return False
            
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.config["max_file_size_mb"]:
                self.logger.warning(f"File size {file_size_mb:.2f}MB exceeds limit")
                return False
            
            # Check format support
            if file_path.suffix.lower() not in self.supported_formats:
                return False
            
            # Try to open video file
            try:
                cap = cv2.VideoCapture(str(file_path))
                is_valid = cap.isOpened()
                cap.release()
                return is_valid
            except Exception:
                return False
                
        except Exception as e:
            self.logger.error(f"Video file validation failed: {e}")
            return False
    
    async def _extract_frames_for_analysis(self, cap: cv2.VideoCapture, total_frames: int) -> List[np.ndarray]:
        """Extract frames for analysis with smart sampling"""
        try:
            frames = []
            max_frames = self.config["max_frames_for_analysis"]
            
            # Calculate frame sampling interval
            if total_frames <= max_frames:
                frame_interval = 1
            else:
                frame_interval = total_frames // max_frames
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames based on interval
                if frame_count % frame_interval == 0:
                    frames.append(frame)
                    
                    if len(frames) >= max_frames:
                        break
                
                frame_count += 1
            
            self.logger.info(f"Extracted {len(frames)} frames for analysis")
            return frames
            
        except Exception as e:
            self.logger.error(f"Frame extraction failed: {e}")
            return []
    
    async def _extract_video_metadata(
        self, 
        file_path: Path, 
        cap: cv2.VideoCapture,
        frames: List[np.ndarray]
    ) -> VideoMetadata:
        """Extract comprehensive video metadata"""
        try:
            # Basic properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Calculate aspect ratio
            aspect_ratio = f"{width}:{height}"
            gcd = np.gcd(width, height)
            if gcd > 1:
                aspect_ratio = f"{width//gcd}:{height//gcd}"
            
            metadata = VideoMetadata(
                duration=duration,
                width=width,
                height=height,
                fps=fps,
                total_frames=total_frames,
                file_size=file_path.stat().st_size,
                aspect_ratio=aspect_ratio,
                container_format=file_path.suffix.lower()[1:]
            )
            
            # Determine quality level
            for quality in VideoQuality:
                if width >= quality.value["min_width"] and height >= quality.value["min_height"]:
                    metadata.quality_level = quality
                    break
            
            # Audio detection (simplified)
            try:
                # Try to get audio properties
                fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
                if fourcc != 0:
                    # Video has codec information, likely has audio
                    metadata.has_audio = True
            except Exception:
                pass
            
            # Frame-based analysis
            if frames:
                # Face detection
                if self.face_cascade is not None:
                    total_faces = 0
                    for frame in frames[:10]:  # Check first 10 frames
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                        total_faces += len(faces)
                    metadata.faces_detected = total_faces
                
                # Color analysis
                if self.config.get("color_analysis", True):
                    color_stats = self._analyze_color_properties(frames)
                    metadata.brightness_avg = color_stats["brightness"]
                    metadata.contrast_avg = color_stats["contrast"]
                    metadata.saturation_avg = color_stats["saturation"]
                    metadata.color_variance = color_stats["variance"]
                
                # Motion analysis
                if self.config.get("motion_analysis", True) and len(frames) > 1:
                    motion_intensity = self._analyze_motion_intensity(frames)
                    metadata.motion_intensity = motion_intensity
                
                # Text detection (basic edge-based approach)
                text_detected = self._detect_text_in_frames(frames[:5])
                metadata.text_detected = text_detected
            
            metadata.analyzed_at = datetime.now(timezone.utc)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Video metadata extraction failed: {e}")
            raise
    
    def _analyze_color_properties(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """Analyze color properties across frames"""
        try:
            brightness_values = []
            contrast_values = []
            saturation_values = []
            color_variances = []
            
            for frame in frames[:20]:  # Analyze up to 20 frames
                # Convert to different color spaces
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                
                # Brightness (luminance)
                brightness = np.mean(gray)
                brightness_values.append(brightness)
                
                # Contrast
                contrast = np.std(gray)
                contrast_values.append(contrast)
                
                # Saturation
                saturation = np.mean(hsv[:, :, 1])
                saturation_values.append(saturation)
                
                # Color variance
                color_variance = np.var(frame.reshape(-1, 3), axis=0).mean()
                color_variances.append(color_variance)
            
            return {
                "brightness": float(np.mean(brightness_values)),
                "contrast": float(np.mean(contrast_values)),
                "saturation": float(np.mean(saturation_values)),
                "variance": float(np.mean(color_variances))
            }
            
        except Exception as e:
            self.logger.error(f"Color analysis failed: {e}")
            return {"brightness": 0.0, "contrast": 0.0, "saturation": 0.0, "variance": 0.0}
    
    def _analyze_motion_intensity(self, frames: List[np.ndarray]) -> float:
        """Analyze motion intensity between frames"""
        try:
            if len(frames) < 2:
                return 0.0
            
            motion_scores = []
            
            for i in range(len(frames) - 1):
                # Convert frames to grayscale
                frame1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                frame2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY)
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    frame1, frame2, 
                    cv2.goodFeaturesToTrack(frame1, maxCorners=100, qualityLevel=0.3, minDistance=7),
                    None
                )[0]
                
                if flow is not None and len(flow) > 0:
                    # Calculate motion magnitude
                    motion_magnitude = np.mean(np.sqrt(np.sum(flow**2, axis=1)))
                    motion_scores.append(motion_magnitude)
            
            return float(np.mean(motion_scores)) if motion_scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Motion analysis failed: {e}")
            return 0.0
    
    def _detect_text_in_frames(self, frames: List[np.ndarray]) -> bool:
        """Detect text presence in video frames using edge detection"""
        try:
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Apply edge detection
                edges = cv2.Canny(gray, 50, 150)
                
                # Look for horizontal and vertical line patterns (text characteristics)
                horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
                vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
                
                horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
                vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
                
                # Count line pixels
                h_lines_count = np.sum(horizontal_lines > 0)
                v_lines_count = np.sum(vertical_lines > 0)
                
                # Simple heuristic: if significant line patterns exist, text might be present
                if h_lines_count > 1000 or v_lines_count > 1000:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Text detection failed: {e}")
            return False
    
    async def _generate_video_fingerprint(
        self, 
        frames: List[np.ndarray], 
        content_id: str
    ) -> VideoFingerprint:
        """Generate comprehensive video fingerprint for content protection"""
        try:
            # Primary hash (concatenated frame hashes)
            frame_hashes = []
            for frame in frames[:50]:  # Use first 50 frames
                frame_hash = hashlib.md5(frame.tobytes()).hexdigest()
                frame_hashes.append(frame_hash)
            
            primary_hash = hashlib.sha256(''.join(frame_hashes).encode()).hexdigest()
            
            # Perceptual hash using average frame
            if frames:
                avg_frame = np.mean(frames[:10], axis=0).astype(np.uint8)
                perceptual_hash = hashlib.sha256(avg_frame.tobytes()).hexdigest()[:32]
            else:
                perceptual_hash = "0" * 32
            
            # Motion signature
            motion_signature = await self._generate_motion_signature(frames)
            
            # Color histogram hash
            color_histogram_hash = await self._generate_color_histogram_hash(frames)
            
            # Edge density hash
            edge_density_hash = await self._generate_edge_density_hash(frames)
            
            # Scene signatures
            scene_signatures = await self._generate_scene_signatures(frames)
            
            # Advanced features
            temporal_features = self._extract_temporal_features(frames)
            spatial_features = self._extract_spatial_features(frames)
            
            # Quality indicators
            quality_indicators = {
                "frame_consistency": self._calculate_frame_consistency(frames),
                "spatial_complexity": float(np.mean([np.std(frame) for frame in frames[:10]])),
                "temporal_complexity": float(np.std([np.mean(frame) for frame in frames[:20]])),
                "color_richness": float(np.mean([np.var(frame.reshape(-1, 3), axis=0).mean() for frame in frames[:10]]))
            }
            
            # Confidence score
            confidence_score = min(1.0, (
                quality_indicators["frame_consistency"] * 0.3 +
                min(quality_indicators["spatial_complexity"] / 100, 1.0) * 0.3 +
                min(quality_indicators["color_richness"] / 1000, 1.0) * 0.4
            ))
            
            fingerprint = VideoFingerprint(
                content_id=hashlib.md5(content_id.encode()).hexdigest(),
                primary_hash=primary_hash,
                perceptual_hash=perceptual_hash,
                frame_hash_sequence=frame_hashes,
                motion_signature=motion_signature,
                color_histogram_hash=color_histogram_hash,
                edge_density_hash=edge_density_hash,
                temporal_features=temporal_features,
                spatial_features=spatial_features,
                scene_signatures=scene_signatures,
                confidence_score=confidence_score,
                quality_indicators=quality_indicators
            )
            
            return fingerprint
            
        except Exception as e:
            self.logger.error(f"Video fingerprint generation failed: {e}")
            raise
    
    async def _generate_motion_signature(self, frames: List[np.ndarray]) -> str:
        """Generate motion signature from optical flow analysis"""
        try:
            if len(frames) < 2:
                return hashlib.sha256(b"no_motion").hexdigest()[:32]
            
            motion_vectors = []
            
            for i in range(min(len(frames) - 1, 20)):  # Analyze up to 20 frame pairs
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY)
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    gray1, gray2,
                    cv2.goodFeaturesToTrack(gray1, maxCorners=50, qualityLevel=0.3, minDistance=7),
                    None
                )[0]
                
                if flow is not None and len(flow) > 0:
                    # Calculate motion statistics
                    motion_mag = np.sqrt(np.sum(flow**2, axis=1))
                    motion_vectors.extend([
                        float(np.mean(motion_mag)),
                        float(np.std(motion_mag)),
                        float(np.max(motion_mag))
                    ])
            
            motion_str = json.dumps(motion_vectors[:60], sort_keys=True)  # Limit size
            return hashlib.sha256(motion_str.encode()).hexdigest()[:32]
            
        except Exception as e:
            self.logger.error(f"Motion signature generation failed: {e}")
            return hashlib.sha256(str(np.random.random()).encode()).hexdigest()[:32]
    
    async def _generate_color_histogram_hash(self, frames: List[np.ndarray]) -> str:
        """Generate color histogram-based hash"""
        try:
            combined_histogram = np.zeros((256, 3))
            
            for frame in frames[:10]:  # Use first 10 frames
                for channel in range(3):
                    hist = cv2.calcHist([frame], [channel], None, [256], [0, 256])
                    combined_histogram[:, channel] += hist.flatten()
            
            # Normalize
            combined_histogram = combined_histogram / (len(frames[:10]) * frame.shape[0] * frame.shape[1])
            
            return hashlib.sha256(combined_histogram.tobytes()).hexdigest()[:32]
            
        except Exception as e:
            self.logger.error(f"Color histogram hash generation failed: {e}")
            return hashlib.sha256(str(np.random.random()).encode()).hexdigest()[:32]
    
    async def _generate_edge_density_hash(self, frames: List[np.ndarray]) -> str:
        """Generate edge density-based hash"""
        try:
            edge_densities = []
            
            for frame in frames[:15]:  # Use first 15 frames
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / (frame.shape[0] * frame.shape[1])
                edge_densities.append(edge_density)
            
            edge_str = json.dumps(edge_densities, sort_keys=True)
            return hashlib.sha256(edge_str.encode()).hexdigest()[:32]
            
        except Exception as e:
            self.logger.error(f"Edge density hash generation failed: {e}")
            return hashlib.sha256(str(np.random.random()).encode()).hexdigest()[:32]
    
    async def _generate_scene_signatures(self, frames: List[np.ndarray]) -> List[str]:
        """Generate signatures for detected scenes"""
        try:
            # Simple scene detection based on histogram differences
            scene_signatures = []
            scene_start = 0
            
            if len(frames) < 2:
                return [hashlib.sha256(frames[0].tobytes()).hexdigest()[:16]]
            
            for i in range(1, len(frames)):
                # Calculate histogram difference
                hist1 = cv2.calcHist([frames[i-1]], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                hist2 = cv2.calcHist([frames[i]], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                
                diff = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                
                # Scene boundary detection
                if diff < 0.7 or i == len(frames) - 1:  # Scene change or end
                    # Generate scene signature
                    scene_frames = frames[scene_start:i+1]
                    if scene_frames:
                        avg_frame = np.mean(scene_frames, axis=0).astype(np.uint8)
                        scene_sig = hashlib.sha256(avg_frame.tobytes()).hexdigest()[:16]
                        scene_signatures.append(scene_sig)
                    
                    scene_start = i
                    
                    if len(scene_signatures) >= 10:  # Limit number of scenes
                        break
            
            return scene_signatures
            
        except Exception as e:
            self.logger.error(f"Scene signature generation failed: {e}")
            return []
    
    def _extract_temporal_features(self, frames: List[np.ndarray]) -> Optional[np.ndarray]:
        """Extract temporal features from frame sequence"""
        try:
            if len(frames) < 2:
                return None
            
            temporal_features = []
            
            for i in range(len(frames) - 1):
                # Frame difference
                diff = cv2.absdiff(frames[i], frames[i + 1])
                
                # Statistical features of difference
                temporal_features.extend([
                    float(np.mean(diff)),
                    float(np.std(diff)),
                    float(np.max(diff)),
                    float(np.min(diff))
                ])
            
            return np.array(temporal_features[:200])  # Limit size
            
        except Exception as e:
            self.logger.error(f"Temporal feature extraction failed: {e}")
            return None
    
    def _extract_spatial_features(self, frames: List[np.ndarray]) -> Optional[np.ndarray]:
        """Extract spatial features from frames"""
        try:
            spatial_features = []
            
            for frame in frames[:20]:  # Use first 20 frames
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Spatial statistics
                spatial_features.extend([
                    float(np.mean(gray)),
                    float(np.std(gray)),
                    float(np.var(gray)),
                    float(cv2.Laplacian(gray, cv2.CV_64F).var())  # Sharpness
                ])
            
            return np.array(spatial_features)
            
        except Exception as e:
            self.logger.error(f"Spatial feature extraction failed: {e}")
            return None
    
    def _calculate_frame_consistency(self, frames: List[np.ndarray]) -> float:
        """Calculate consistency between frames"""
        try:
            if len(frames) < 2:
                return 1.0
            
            correlations = []
            
            for i in range(len(frames) - 1):
                # Calculate correlation between consecutive frames
                frame1_flat = frames[i].flatten()
                frame2_flat = frames[i + 1].flatten()
                
                correlation = np.corrcoef(frame1_flat, frame2_flat)[0, 1]
                if not np.isnan(correlation):
                    correlations.append(correlation)
            
            return float(np.mean(correlations)) if correlations else 0.0
            
        except Exception as e:
            self.logger.error(f"Frame consistency calculation failed: {e}")
            return 0.0
    
    async def _detect_video_scenes(self, frames: List[np.ndarray], fps: float) -> List[VideoScene]:
        """Detect scenes in video using histogram analysis"""
        try:
            scenes = []
            scene_start = 0
            scene_id_counter = 0
            
            if len(frames) < 2:
                # Single scene
                scene = VideoScene(
                    scene_id=f"scene_{scene_id_counter:03d}",
                    start_frame=0,
                    end_frame=len(frames) - 1,
                    start_time=0.0,
                    end_time=len(frames) / fps,
                    duration=len(frames) / fps,
                    representative_frame=frames[0] if frames else None
                )
                return [scene]
            
            threshold = self.config["scene_detection_threshold"]
            
            for i in range(1, len(frames)):
                # Calculate histogram difference
                hist1 = cv2.calcHist([frames[i-1]], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                hist2 = cv2.calcHist([frames[i]], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                
                # Bhattacharyya distance
                distance = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
                
                # Scene boundary detection
                if distance > threshold or i == len(frames) - 1:
                    end_frame = i if i != len(frames) - 1 else len(frames) - 1
                    
                    # Create scene
                    scene = VideoScene(
                        scene_id=f"scene_{scene_id_counter:03d}",
                        start_frame=scene_start,
                        end_frame=end_frame,
                        start_time=scene_start / fps,
                        end_time=end_frame / fps,
                        duration=(end_frame - scene_start) / fps,
                        representative_frame=frames[(scene_start + end_frame) // 2]
                    )
                    
                    # Analyze scene properties
                    scene_frames = frames[scene_start:end_frame+1]
                    if scene_frames:
                        scene.motion_level = self._analyze_motion_intensity(scene_frames)
                        scene.dominant_colors = self._extract_dominant_colors(scene_frames[0])
                    
                    scenes.append(scene)
                    scene_start = i
                    scene_id_counter += 1
                    
                    if len(scenes) >= 20:  # Limit number of scenes
                        break
            
            return scenes
            
        except Exception as e:
            self.logger.error(f"Scene detection failed: {e}")
            return []
    
    def _extract_dominant_colors(self, frame: np.ndarray, k: int = 5) -> List[Tuple[int, int, int]]:
        """Extract dominant colors from frame using K-means clustering"""
        try:
            # Reshape frame to list of pixels
            data = frame.reshape((-1, 3))
            data = np.float32(data)
            
            # K-means clustering
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers to int and sort by frequency
            centers = np.uint8(centers)
            dominant_colors = []
            
            for center in centers:
                dominant_colors.append((int(center[2]), int(center[1]), int(center[0])))  # BGR to RGB
            
            return dominant_colors
            
        except Exception as e:
            self.logger.error(f"Dominant color extraction failed: {e}")
            return []
    
    async def _analyze_video_quality(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """Analyze video quality metrics"""
        try:
            quality_metrics = {}
            
            if not frames:
                return {"overall_quality": 0.0, "error": "No frames available"}
            
            # Sharpness (Laplacian variance)
            sharpness_scores = []
            for frame in frames[:10]:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                sharpness_scores.append(sharpness)
            
            quality_metrics["sharpness"] = float(np.mean(sharpness_scores))
            
            # Noise estimation (high frequency content)
            noise_levels = []
            for frame in frames[:10]:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # High-pass filter to estimate noise
                kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
                noise_response = cv2.filter2D(gray, cv2.CV_64F, kernel)
                noise_level = np.std(noise_response)
                noise_levels.append(noise_level)
            
            quality_metrics["noise_level"] = float(np.mean(noise_levels))
            
            # Brightness and contrast quality
            brightness_scores = []
            contrast_scores = []
            
            for frame in frames[:10]:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = np.mean(gray)
                contrast = np.std(gray)
                
                # Quality based on optimal ranges
                brightness_quality = 1.0 - abs(brightness - 128) / 128  # Optimal around 128
                contrast_quality = min(contrast / 64, 1.0)  # Good contrast above 64
                
                brightness_scores.append(brightness_quality)
                contrast_scores.append(contrast_quality)
            
            quality_metrics["brightness_quality"] = float(np.mean(brightness_scores))
            quality_metrics["contrast_quality"] = float(np.mean(contrast_scores))
            
            # Compression artifacts (blocking artifacts estimation)
            blocking_scores = []
            for frame in frames[:5]:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Check for 8x8 block patterns (typical compression artifacts)
                h_diff = np.abs(np.diff(gray, axis=1))
                v_diff = np.abs(np.diff(gray, axis=0))
                
                # Look for regular patterns indicating blocking
                h_blocking = np.mean(h_diff[:, 7::8]) / (np.mean(h_diff) + 1e-10)
                v_blocking = np.mean(v_diff[7::8, :]) / (np.mean(v_diff) + 1e-10)
                
                blocking_score = 1.0 / (1.0 + max(h_blocking, v_blocking))
                blocking_scores.append(blocking_score)
            
            quality_metrics["compression_quality"] = float(np.mean(blocking_scores))
            
            # Overall quality score
            overall_quality = (
                min(quality_metrics["sharpness"] / 1000, 1.0) * 0.25 +
                quality_metrics["brightness_quality"] * 0.25 +
                quality_metrics["contrast_quality"] * 0.25 +
                quality_metrics["compression_quality"] * 0.25
            )
            
            quality_metrics["overall_quality"] = max(0.0, min(1.0, overall_quality))
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Video quality analysis failed: {e}")
            return {"overall_quality": 0.5, "error": str(e)}
    
    async def _generate_thumbnails(self, frames: List[np.ndarray]) -> List[str]:
        """Generate representative thumbnails from video"""
        try:
            thumbnails = []
            thumbnail_count = min(self.config["thumbnail_count"], len(frames))
            
            if not frames:
                return thumbnails
            
            # Select frames evenly distributed
            indices = np.linspace(0, len(frames) - 1, thumbnail_count, dtype=int)
            
            for i, idx in enumerate(indices):
                frame = frames[idx]
                
                # Resize for thumbnail (maintain aspect ratio)
                height, width = frame.shape[:2]
                thumbnail_width = 160
                thumbnail_height = int(height * (thumbnail_width / width))
                
                thumbnail = cv2.resize(frame, (thumbnail_width, thumbnail_height))
                
                # Convert to base64 for storage (in production, save to file/storage)
                _, buffer = cv2.imencode('.jpg', thumbnail)
                thumbnail_b64 = f"thumbnail_{i}_{hashlib.md5(buffer).hexdigest()[:8]}.jpg"
                
                thumbnails.append(thumbnail_b64)
            
            return thumbnails
            
        except Exception as e:
            self.logger.error(f"Thumbnail generation failed: {e}")
            return []
    
    async def _classify_video_content(
        self, 
        frames: List[np.ndarray], 
        metadata: Optional[VideoMetadata] = None
    ) -> VideoContentType:
        """Classify video content type using visual and metadata features"""
        try:
            # Simple heuristic classification (in production, use ML model)
            
            # Check video duration and aspect ratio
            if metadata:
                duration = metadata.duration
                aspect_ratio = metadata.width / metadata.height if metadata.height > 0 else 1.0
                
                # Short-form content
                if duration < 60:  # Less than 1 minute
                    return VideoContentType.SHORT_FORM
                
                # Check for vertical aspect ratio (mobile content)
                if aspect_ratio < 0.8:
                    return VideoContentType.VLOG
            
            # Visual content analysis
            if frames:
                # Face detection based classification
                total_faces = 0
                if self.face_cascade is not None:
                    for frame in frames[:10]:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                        total_faces += len(faces)
                
                avg_faces_per_frame = total_faces / min(len(frames), 10)
                
                # Motion analysis for classification
                motion_intensity = self._analyze_motion_intensity(frames[:20])
                
                # Classification logic
                if avg_faces_per_frame > 1.5:
                    return VideoContentType.INTERVIEW
                elif motion_intensity > 5.0:
                    return VideoContentType.SPORTS
                elif avg_faces_per_frame > 0.5:
                    return VideoContentType.VLOG
                else:
                    return VideoContentType.DOCUMENTARY
            
            return VideoContentType.MOVIE  # Default
            
        except Exception as e:
            self.logger.error(f"Video content classification failed: {e}")
            return VideoContentType.MOVIE  # Default fallback
    
    async def store_content(self, video_content: Dict[str, Any]) -> str:
        """Store processed video content in database"""
        try:
            # Generate unique content ID
            content_id = hashlib.sha256(
                f"{video_content['file_path']}{datetime.now().isoformat()}".encode()
            ).hexdigest()
            
            # Here you would implement database storage
            # For now, return the generated ID
            
            self.logger.info(f"Video content stored with ID: {content_id}")
            return content_id
            
        except Exception as e:
            self.logger.error(f"Failed to store video content: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported video formats"""
        return [fmt.value["ext"] for fmt in VideoFormat]
    
    def get_format_info(self, format_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific video format"""
        for fmt in VideoFormat:
            if fmt.value["ext"] == f".{format_name.lower()}" or fmt.name.lower() == format_name.lower():
                return fmt.value
        return None
