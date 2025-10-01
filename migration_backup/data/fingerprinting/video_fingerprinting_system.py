#!/usr/bin/env python3
"""
Video Fingerprinting System - IA Chéries Data Fingerprinting Module
================================================================
Advanced video fingerprinting system with deep learning-powered analysis,
frame extraction, temporal patterns, and specialized video content protection
for video creators on the IA Chéries platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Data Fingerprinting
Version: 1.0 Enterprise Production
"""

import asyncio
import hashlib
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Core imports for video processing
try:
    import cv2
    import torch
    import torchvision.transforms as transforms
    from torchvision.models import resnet50, ResNet50_Weights
    import numpy as np
    from scipy.spatial.distance import cosine, euclidean
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
except ImportError as e:
    logging.error(f"Required video dependencies not installed: {e}")

# IA Chéries core imports
from .multimodal_fingerprinting_engine import FingerprintResult, FingerprintConfig
from .vector_database_matching import VectorDatabaseManager
from .performance_analytics_engine import PerformanceAnalytics


class VideoFingerprintType(Enum):
    """Types of video fingerprints supported."""
    FRAME_HISTOGRAM = "frame_histogram"
    OPTICAL_FLOW = "optical_flow"
    TEMPORAL_FEATURES = "temporal_features"
    DEEP_FEATURES = "deep_features"
    COLOR_MOMENTS = "color_moments"
    EDGE_HISTOGRAM = "edge_histogram"
    MOTION_VECTORS = "motion_vectors"
    SCENE_DETECTION = "scene_detection"
    OBJECT_DETECTION = "object_detection"
    COMBINED = "combined"


class VideoFormat(Enum):
    """Supported video formats."""
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    FLV = "flv"
    WMV = "wmv"
    M4V = "m4v"


class VideoQuality(Enum):
    """Video quality levels."""
    LOW = "low"           # 240p-480p
    MEDIUM = "medium"     # 720p
    HIGH = "high"         # 1080p
    ULTRA = "ultra"       # 4K+


@dataclass
class VideoMetadata:
    """Video file metadata container."""
    duration: float
    fps: float
    width: int
    height: int
    total_frames: int
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    format: Optional[VideoFormat] = None
    quality: Optional[VideoQuality] = None
    file_size: Optional[int] = None
    aspect_ratio: Optional[float] = None
    has_audio: bool = False
    audio_codec: Optional[str] = None
    color_space: Optional[str] = None
    scene_count: Optional[int] = None
    motion_intensity: Optional[float] = None
    brightness_avg: Optional[float] = None
    contrast_avg: Optional[float] = None


@dataclass
class VideoFrame:
    """Video frame data structure."""
    frame_number: int
    timestamp: float
    frame_data: np.ndarray
    features: Optional[np.ndarray] = None
    histogram: Optional[np.ndarray] = None
    edges: Optional[np.ndarray] = None
    motion_vector: Optional[np.ndarray] = None


@dataclass
class VideoFingerprint:
    """Video fingerprint data structure."""
    fingerprint_id: str
    fingerprint_type: VideoFingerprintType
    data: np.ndarray
    confidence: float
    metadata: VideoMetadata
    frame_count: int
    key_frames: List[int] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    processing_time: float = 0.0
    file_path: Optional[str] = None
    hash_sha256: Optional[str] = None
    additional_features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoAnalysisConfig:
    """Configuration for video analysis."""
    sample_fps: float = 1.0  # Frames per second to sample
    max_frames: int = 1000   # Maximum frames to process
    frame_resize: Tuple[int, int] = (224, 224)  # Resize frames for processing
    histogram_bins: int = 256
    enable_deep_features: bool = True
    enable_motion_analysis: bool = True
    enable_scene_detection: bool = True
    edge_threshold: float = 100.0
    motion_threshold: float = 0.1
    scene_threshold: float = 0.3
    quality_threshold: float = 0.7
    confidence_threshold: float = 0.8
    batch_size: int = 32


class VideoFingerprintingSystem:
    """
    Advanced Video Fingerprinting System
    
    Provides comprehensive video content fingerprinting with:
    - Frame-based feature extraction
    - Temporal pattern analysis
    - Deep learning-powered content analysis
    - Motion vector analysis
    - Scene detection and segmentation
    - Multi-scale feature extraction
    """
    
    def __init__(self, config: Optional[VideoAnalysisConfig] = None):
        """Initialize video fingerprinting system."""
        self.config = config or VideoAnalysisConfig()
        self.logger = logging.getLogger(__name__)
        
        # Vector database for similarity matching
        self.vector_db = VectorDatabaseManager()
        self.performance_analytics = PerformanceAnalytics()
        
        # Deep learning models
        self.deep_model = None
        self.feature_extractor = None
        
        # OpenCV face/object detectors
        self.face_cascade = None
        self.body_cascade = None
        
        # Initialize components
        self._initialize_models()
        
        self.logger.info("VideoFingerprintingSystem initialized successfully")
    
    def _initialize_models(self):
        """Initialize deep learning models and OpenCV detectors."""
        try:
            if self.config.enable_deep_features:
                # Load pre-trained ResNet50 for feature extraction
                self.deep_model = resnet50(weights=ResNet50_Weights.DEFAULT)
                self.deep_model.eval()
                
                # Remove final classification layer for feature extraction
                self.feature_extractor = torch.nn.Sequential(
                    *list(self.deep_model.children())[:-1]
                )
                
                self.logger.info("Deep learning models initialized successfully")
            
            # Initialize OpenCV cascades
            try:
                self.face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
                self.body_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_fullbody.xml'
                )
                self.logger.info("OpenCV detectors initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize OpenCV detectors: {e}")
                
        except Exception as e:
            self.logger.warning(f"Failed to initialize deep models: {e}")
            self.config.enable_deep_features = False
    
    async def process_video_file(
        self,
        file_path: str,
        creator_id: str,
        fingerprint_types: Optional[List[VideoFingerprintType]] = None
    ) -> List[VideoFingerprint]:
        """
        Process video file and generate multiple fingerprints.
        
        Args:
            file_path: Path to video file
            creator_id: Creator identifier for protection
            fingerprint_types: Types of fingerprints to generate
        
        Returns:
            List of generated video fingerprints
        """
        start_time = datetime.utcnow()
        
        try:
            # Open video file
            video_capture = cv2.VideoCapture(file_path)
            if not video_capture.isOpened():
                raise ValueError(f"Failed to open video file: {file_path}")
            
            # Extract metadata
            metadata = await self._extract_metadata(video_capture, file_path)
            
            # Generate file hash
            file_hash = await self._generate_file_hash(file_path)
            
            # Extract frames
            frames = await self._extract_frames(video_capture, metadata)
            
            # Default fingerprint types
            if fingerprint_types is None:
                fingerprint_types = [
                    VideoFingerprintType.FRAME_HISTOGRAM,
                    VideoFingerprintType.TEMPORAL_FEATURES,
                    VideoFingerprintType.DEEP_FEATURES,
                    VideoFingerprintType.OPTICAL_FLOW,
                    VideoFingerprintType.COMBINED
                ]
            
            # Generate fingerprints
            fingerprints = []
            for fp_type in fingerprint_types:
                fingerprint = await self._generate_fingerprint(
                    frames=frames,
                    fingerprint_type=fp_type,
                    metadata=metadata,
                    file_path=file_path,
                    file_hash=file_hash
                )
                fingerprints.append(fingerprint)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update fingerprints with processing time
            for fp in fingerprints:
                fp.processing_time = processing_time
            
            # Store fingerprints in vector database
            await self._store_fingerprints(fingerprints, creator_id)
            
            # Record analytics
            await self.performance_analytics.record_processing_metrics({
                'operation': 'video_fingerprinting',
                'file_path': file_path,
                'creator_id': creator_id,
                'processing_time': processing_time,
                'fingerprint_count': len(fingerprints),
                'frame_count': len(frames),
                'success': True
            })
            
            # Clean up
            video_capture.release()
            
            self.logger.info(
                f"Generated {len(fingerprints)} fingerprints from {len(frames)} frames "
                f"for {file_path} in {processing_time:.2f}s"
            )
            
            return fingerprints
            
        except Exception as e:
            error_msg = f"Failed to process video file {file_path}: {e}"
            self.logger.error(error_msg)
            
            await self.performance_analytics.record_processing_metrics({
                'operation': 'video_fingerprinting',
                'file_path': file_path,
                'creator_id': creator_id,
                'processing_time': (datetime.utcnow() - start_time).total_seconds(),
                'fingerprint_count': 0,
                'success': False,
                'error': str(e)
            })
            
            raise
    
    async def _extract_metadata(
        self, video_capture: cv2.VideoCapture, file_path: str
    ) -> VideoMetadata:
        """Extract comprehensive video metadata."""
        try:
            # Basic video properties
            fps = video_capture.get(cv2.CAP_PROP_FPS)
            frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # File size
            file_size = Path(file_path).stat().st_size
            
            # Aspect ratio
            aspect_ratio = width / height if height > 0 else 0
            
            # Determine quality
            quality = self._determine_video_quality(width, height)
            
            # Get format from file extension
            format_ext = Path(file_path).suffix.lower().lstrip('.')
            video_format = None
            try:
                video_format = VideoFormat(format_ext)
            except ValueError:
                pass
            
            return VideoMetadata(
                duration=duration,
                fps=fps,
                width=width,
                height=height,
                total_frames=frame_count,
                file_size=file_size,
                aspect_ratio=aspect_ratio,
                quality=quality,
                format=video_format
            )
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            return VideoMetadata(
                duration=0,
                fps=0,
                width=0,
                height=0,
                total_frames=0
            )
    
    def _determine_video_quality(self, width: int, height: int) -> VideoQuality:
        """Determine video quality based on resolution."""
        if height >= 2160:  # 4K
            return VideoQuality.ULTRA
        elif height >= 1080:  # 1080p
            return VideoQuality.HIGH
        elif height >= 720:  # 720p
            return VideoQuality.MEDIUM
        else:  # 480p and below
            return VideoQuality.LOW
    
    async def _extract_frames(
        self, video_capture: cv2.VideoCapture, metadata: VideoMetadata
    ) -> List[VideoFrame]:
        """Extract frames from video for analysis."""
        try:
            frames = []
            frame_interval = max(1, int(metadata.fps / self.config.sample_fps))
            
            frame_number = 0
            extracted_count = 0
            
            while extracted_count < self.config.max_frames:
                ret, frame = video_capture.read()
                if not ret:
                    break
                
                # Sample frames at specified interval
                if frame_number % frame_interval == 0:
                    timestamp = frame_number / metadata.fps
                    
                    # Resize frame for processing
                    resized_frame = cv2.resize(frame, self.config.frame_resize)
                    
                    video_frame = VideoFrame(
                        frame_number=frame_number,
                        timestamp=timestamp,
                        frame_data=resized_frame
                    )
                    
                    frames.append(video_frame)
                    extracted_count += 1
                
                frame_number += 1
            
            self.logger.info(f"Extracted {len(frames)} frames from video")
            return frames
            
        except Exception as e:
            self.logger.error(f"Frame extraction failed: {e}")
            return []
    
    async def _generate_fingerprint(
        self,
        frames: List[VideoFrame],
        fingerprint_type: VideoFingerprintType,
        metadata: VideoMetadata,
        file_path: str,
        file_hash: str
    ) -> VideoFingerprint:
        """Generate specific type of video fingerprint."""
        
        try:
            if fingerprint_type == VideoFingerprintType.FRAME_HISTOGRAM:
                data, confidence = await self._generate_frame_histogram(frames)
            
            elif fingerprint_type == VideoFingerprintType.OPTICAL_FLOW:
                data, confidence = await self._generate_optical_flow(frames)
            
            elif fingerprint_type == VideoFingerprintType.TEMPORAL_FEATURES:
                data, confidence = await self._generate_temporal_features(frames)
            
            elif fingerprint_type == VideoFingerprintType.DEEP_FEATURES:
                data, confidence = await self._generate_deep_features(frames)
            
            elif fingerprint_type == VideoFingerprintType.COLOR_MOMENTS:
                data, confidence = await self._generate_color_moments(frames)
            
            elif fingerprint_type == VideoFingerprintType.EDGE_HISTOGRAM:
                data, confidence = await self._generate_edge_histogram(frames)
            
            elif fingerprint_type == VideoFingerprintType.MOTION_VECTORS:
                data, confidence = await self._generate_motion_vectors(frames)
            
            elif fingerprint_type == VideoFingerprintType.SCENE_DETECTION:
                data, confidence = await self._generate_scene_features(frames)
            
            elif fingerprint_type == VideoFingerprintType.OBJECT_DETECTION:
                data, confidence = await self._generate_object_features(frames)
            
            elif fingerprint_type == VideoFingerprintType.COMBINED:
                data, confidence = await self._generate_combined_fingerprint(frames)
            
            else:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            # Generate unique fingerprint ID
            fingerprint_id = self._generate_fingerprint_id(
                file_hash, fingerprint_type.value, data
            )
            
            # Extract key frame indices
            key_frames = self._extract_key_frames(frames)
            
            return VideoFingerprint(
                fingerprint_id=fingerprint_id,
                fingerprint_type=fingerprint_type,
                data=data,
                confidence=confidence,
                metadata=metadata,
                frame_count=len(frames),
                key_frames=key_frames,
                file_path=file_path,
                hash_sha256=file_hash
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate {fingerprint_type.value} fingerprint: {e}")
            raise
    
    async def _generate_frame_histogram(
        self, frames: List[VideoFrame]
    ) -> Tuple[np.ndarray, float]:
        """Generate histogram-based fingerprint."""
        try:
            histograms = []
            
            for frame in frames:
                # Convert to HSV for better color representation
                hsv = cv2.cvtColor(frame.frame_data, cv2.COLOR_BGR2HSV)
                
                # Calculate histogram for each channel
                hist_h = cv2.calcHist([hsv], [0], None, [self.config.histogram_bins], [0, 180])
                hist_s = cv2.calcHist([hsv], [1], None, [self.config.histogram_bins], [0, 256])
                hist_v = cv2.calcHist([hsv], [2], None, [self.config.histogram_bins], [0, 256])
                
                # Normalize histograms
                hist_h = hist_h.flatten() / (hist_h.sum() + 1e-10)
                hist_s = hist_s.flatten() / (hist_s.sum() + 1e-10)
                hist_v = hist_v.flatten() / (hist_v.sum() + 1e-10)
                
                # Combine histograms
                combined_hist = np.concatenate([hist_h, hist_s, hist_v])
                histograms.append(combined_hist)
                
                # Store histogram in frame
                frame.histogram = combined_hist
            
            if not histograms:
                return np.array([]), 0.0
            
            # Calculate temporal histogram features
            histograms_array = np.array(histograms)
            
            # Statistical features across time
            mean_hist = np.mean(histograms_array, axis=0)
            std_hist = np.std(histograms_array, axis=0)
            
            # Combine features
            features = np.concatenate([mean_hist, std_hist])
            
            # Calculate confidence based on histogram variance
            confidence = self._calculate_histogram_confidence(histograms_array)
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"Frame histogram generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_optical_flow(
        self, frames: List[VideoFrame]
    ) -> Tuple[np.ndarray, float]:
        """Generate optical flow-based fingerprint."""
        try:
            if len(frames) < 2:
                return np.array([]), 0.0
            
            flow_features = []
            
            for i in range(1, len(frames)):
                prev_frame = cv2.cvtColor(frames[i-1].frame_data, cv2.COLOR_BGR2GRAY)
                curr_frame = cv2.cvtColor(frames[i].frame_data, cv2.COLOR_BGR2GRAY)
                
                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    prev_frame, curr_frame, None, None
                )
                
                if flow[0] is not None and len(flow[0]) > 0:
                    # Extract flow statistics
                    flow_magnitude = np.sqrt(flow[0][:, 0]**2 + flow[0][:, 1]**2)
                    flow_angle = np.arctan2(flow[0][:, 1], flow[0][:, 0])
                    
                    # Calculate features
                    features = np.array([
                        np.mean(flow_magnitude),
                        np.std(flow_magnitude),
                        np.mean(flow_angle),
                        np.std(flow_angle),
                        np.max(flow_magnitude),
                        np.min(flow_magnitude)
                    ])
                    
                    flow_features.append(features)
            
            if not flow_features:
                return np.array([]), 0.0
            
            # Aggregate flow features
            flow_array = np.array(flow_features)
            aggregated_features = np.concatenate([
                np.mean(flow_array, axis=0),
                np.std(flow_array, axis=0)
            ])
            
            # Calculate confidence
            confidence = self._calculate_flow_confidence(flow_array)
            
            return aggregated_features, confidence
            
        except Exception as e:
            self.logger.error(f"Optical flow generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_temporal_features(
        self, frames: List[VideoFrame]
    ) -> Tuple[np.ndarray, float]:
        """Generate temporal pattern features."""
        try:
            if len(frames) < 3:
                return np.array([]), 0.0
            
            temporal_features = []
            
            # Calculate frame differences
            for i in range(1, len(frames)):
                prev_gray = cv2.cvtColor(frames[i-1].frame_data, cv2.COLOR_BGR2GRAY)
                curr_gray = cv2.cvtColor(frames[i].frame_data, cv2.COLOR_BGR2GRAY)
                
                # Frame difference
                diff = cv2.absdiff(prev_gray, curr_gray)
                
                # Calculate temporal features
                features = np.array([
                    np.mean(diff),
                    np.std(diff),
                    np.sum(diff > 50) / diff.size,  # Motion ratio
                    np.max(diff),
                    np.percentile(diff, 95)
                ])
                
                temporal_features.append(features)
            
            # Aggregate temporal features
            temporal_array = np.array(temporal_features)
            aggregated_features = np.concatenate([
                np.mean(temporal_array, axis=0),
                np.std(temporal_array, axis=0),
                np.max(temporal_array, axis=0),
                np.min(temporal_array, axis=0)
            ])
            
            # Calculate confidence
            confidence = self._calculate_temporal_confidence(temporal_array)
            
            return aggregated_features, confidence
            
        except Exception as e:
            self.logger.error(f"Temporal features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_deep_features(
        self, frames: List[VideoFrame]
    ) -> Tuple[np.ndarray, float]:
        """Generate deep learning-based features."""
        try:
            if not self.config.enable_deep_features or self.feature_extractor is None:
                return np.array([]), 0.0
            
            deep_features = []
            
            # Image preprocessing
            preprocess = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            # Process frames in batches
            batch_size = self.config.batch_size
            for i in range(0, len(frames), batch_size):
                batch_frames = frames[i:i + batch_size]
                batch_tensors = []
                
                for frame in batch_frames:
                    # Convert BGR to RGB
                    rgb_frame = cv2.cvtColor(frame.frame_data, cv2.COLOR_BGR2RGB)
                    tensor = preprocess(rgb_frame).unsqueeze(0)
                    batch_tensors.append(tensor)
                
                if batch_tensors:
                    batch_tensor = torch.cat(batch_tensors, dim=0)
                    
                    with torch.no_grad():
                        features = self.feature_extractor(batch_tensor)
                        features = features.view(features.size(0), -1)
                        
                    deep_features.extend(features.numpy())
            
            if not deep_features:
                return np.array([]), 0.0
            
            # Aggregate deep features
            deep_array = np.array(deep_features)
            
            # Use PCA for dimensionality reduction
            if deep_array.shape[0] > 1:
                pca = PCA(n_components=min(128, deep_array.shape[1], deep_array.shape[0]))
                reduced_features = pca.fit_transform(deep_array)
            else:
                reduced_features = deep_array
            
            # Calculate final features
            aggregated_features = np.concatenate([
                np.mean(reduced_features, axis=0),
                np.std(reduced_features, axis=0)
            ])
            
            # Calculate confidence
            confidence = self._calculate_deep_confidence(reduced_features)
            
            return aggregated_features, confidence
            
        except Exception as e:
            self.logger.error(f"Deep features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_color_moments(
        self, frames: List[VideoFrame]
    ) -> Tuple[np.ndarray, float]:
        """Generate color moments fingerprint."""
        try:
            color_moments = []
            
            for frame in frames:
                # Convert to different color spaces
                hsv = cv2.cvtColor(frame.frame_data, cv2.COLOR_BGR2HSV)
                lab = cv2.cvtColor(frame.frame_data, cv2.COLOR_BGR2LAB)
                
                # Calculate moments for each channel
                moments = []
                
                # HSV moments
                for channel in range(3):
                    channel_data = hsv[:, :, channel].flatten()
                    moments.extend([
                        np.mean(channel_data),
                        np.std(channel_data),
                        np.mean((channel_data - np.mean(channel_data))**3)  # Skewness
                    ])
                
                # LAB moments
                for channel in range(3):
                    channel_data = lab[:, :, channel].flatten()
                    moments.extend([
                        np.mean(channel_data),
                        np.std(channel_data)
                    ])
                
                color_moments.append(np.array(moments))
            
            if not color_moments:
                return np.array([]), 0.0
            
            # Aggregate color moments
            moments_array = np.array(color_moments)
            aggregated_features = np.concatenate([
                np.mean(moments_array, axis=0),
                np.std(moments_array, axis=0)
            ])
            
            # Calculate confidence
            confidence = self._calculate_color_confidence(moments_array)
            
            return aggregated_features, confidence
            
        except Exception as e:
            self.logger.error(f"Color moments generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_edge_histogram(
        self, frames: List[VideoFrame]
    ) -> Tuple[np.ndarray, float]:
        """Generate edge histogram fingerprint."""
        try:
            edge_features = []
            
            for frame in frames:
                gray = cv2.cvtColor(frame.frame_data, cv2.COLOR_BGR2GRAY)
                
                # Calculate edges using Canny
                edges = cv2.Canny(gray, 50, 150)
                
                # Edge histogram
                edge_hist = cv2.calcHist([edges], [0], None, [256], [0, 256])
                edge_hist = edge_hist.flatten() / (edge_hist.sum() + 1e-10)
                
                # Edge direction features
                sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                
                gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
                gradient_direction = np.arctan2(sobel_y, sobel_x)
                
                # Features
                features = np.concatenate([
                    edge_hist,
                    [
                        np.mean(gradient_magnitude),
                        np.std(gradient_magnitude),
                        np.mean(gradient_direction),
                        np.std(gradient_direction)
                    ]
                ])
                
                edge_features.append(features)
                
                # Store edges in frame
                frame.edges = edges
            
            if not edge_features:
                return np.array([]), 0.0
            
            # Aggregate edge features
            edge_array = np.array(edge_features)
            aggregated_features = np.concatenate([
                np.mean(edge_array, axis=0),
                np.std(edge_array, axis=0)
            ])
            
            # Calculate confidence
            confidence = self._calculate_edge_confidence(edge_array)
            
            return aggregated_features, confidence
            
        except Exception as e:
            self.logger.error(f"Edge histogram generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_motion_vectors(
        self, frames: List[VideoFrame]
    ) -> Tuple[np.ndarray, float]:
        """Generate motion vector fingerprint."""
        try:
            if len(frames) < 2:
                return np.array([]), 0.0
            
            motion_features = []
            
            # Initialize Lucas-Kanade parameters
            lk_params = {
                'winSize': (15, 15),
                'maxLevel': 2,
                'criteria': (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
            }
            
            # Feature detection parameters
            feature_params = {
                'maxCorners': 100,
                'qualityLevel': 0.3,
                'minDistance': 7,
                'blockSize': 7
            }
            
            for i in range(1, len(frames)):
                prev_gray = cv2.cvtColor(frames[i-1].frame_data, cv2.COLOR_BGR2GRAY)
                curr_gray = cv2.cvtColor(frames[i].frame_data, cv2.COLOR_BGR2GRAY)
                
                # Detect features to track
                p0 = cv2.goodFeaturesToTrack(prev_gray, mask=None, **feature_params)
                
                if p0 is not None and len(p0) > 0:
                    # Calculate optical flow
                    p1, st, err = cv2.calcOpticalFlowPyrLK(
                        prev_gray, curr_gray, p0, None, **lk_params
                    )
                    
                    # Select good points
                    if p1 is not None:
                        good_new = p1[st == 1]
                        good_old = p0[st == 1]
                        
                        if len(good_new) > 0:
                            # Calculate motion vectors
                            motion_vectors = good_new - good_old
                            
                            # Extract motion features
                            features = np.array([
                                np.mean(np.linalg.norm(motion_vectors, axis=1)),  # Avg magnitude
                                np.std(np.linalg.norm(motion_vectors, axis=1)),   # Std magnitude
                                np.mean(motion_vectors[:, 0]),  # Avg horizontal
                                np.mean(motion_vectors[:, 1]),  # Avg vertical
                                np.std(motion_vectors[:, 0]),   # Std horizontal
                                np.std(motion_vectors[:, 1]),   # Std vertical
                                len(good_new) / len(p0) if len(p0) > 0 else 0  # Tracking ratio
                            ])
                            
                            motion_features.append(features)
                            
                            # Store motion vector in frame
                            frames[i].motion_vector = motion_vectors
            
            if not motion_features:
                return np.array([]), 0.0
            
            # Aggregate motion features
            motion_array = np.array(motion_features)
            aggregated_features = np.concatenate([
                np.mean(motion_array, axis=0),
                np.std(motion_array, axis=0)
            ])
            
            # Calculate confidence
            confidence = self._calculate_motion_confidence(motion_array)
            
            return aggregated_features, confidence
            
        except Exception as e:
            self.logger.error(f"Motion vectors generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_scene_features(
        self, frames: List[VideoFrame]
    ) -> Tuple[np.ndarray, float]:
        """Generate scene detection features."""
        try:
            if len(frames) < 3:
                return np.array([]), 0.0
            
            scene_features = []
            scene_boundaries = []
            
            # Calculate frame similarities
            similarities = []
            for i in range(1, len(frames)):
                prev_hist = cv2.calcHist(
                    [frames[i-1].frame_data], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256]
                )
                curr_hist = cv2.calcHist(
                    [frames[i].frame_data], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256]
                )
                
                # Normalize histograms
                prev_hist = prev_hist / (prev_hist.sum() + 1e-10)
                curr_hist = curr_hist / (curr_hist.sum() + 1e-10)
                
                # Calculate similarity
                similarity = cv2.compareHist(prev_hist, curr_hist, cv2.HISTCMP_CORREL)
                similarities.append(similarity)
                
                # Detect scene boundary
                if similarity < self.config.scene_threshold:
                    scene_boundaries.append(i)
            
            # Scene statistics
            scene_count = len(scene_boundaries) + 1
            avg_scene_length = len(frames) / scene_count if scene_count > 0 else len(frames)
            
            # Features
            features = np.array([
                scene_count,
                avg_scene_length,
                np.mean(similarities) if similarities else 0,
                np.std(similarities) if similarities else 0,
                np.min(similarities) if similarities else 0,
                len(scene_boundaries) / len(frames) if len(frames) > 0 else 0
            ])
            
            scene_features.append(features)
            
            # Calculate confidence
            confidence = min(1.0, len(similarities) / 10.0) if similarities else 0.0
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"Scene features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_object_features(
        self, frames: List[VideoFrame]
    ) -> Tuple[np.ndarray, float]:
        """Generate object detection features."""
        try:
            object_features = []
            
            for frame in frames:
                gray = cv2.cvtColor(frame.frame_data, cv2.COLOR_BGR2GRAY)
                
                # Face detection
                faces = []
                bodies = []
                
                if self.face_cascade is not None:
                    faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if self.body_cascade is not None:
                    bodies = self.body_cascade.detectMultiScale(gray, 1.1, 4)
                
                # Object features
                features = np.array([
                    len(faces),  # Face count
                    len(bodies),  # Body count
                    np.sum([w * h for (x, y, w, h) in faces]) / (frame.frame_data.shape[0] * frame.frame_data.shape[1]) if faces else 0,  # Face area ratio
                    np.sum([w * h for (x, y, w, h) in bodies]) / (frame.frame_data.shape[0] * frame.frame_data.shape[1]) if bodies else 0,  # Body area ratio
                ])
                
                object_features.append(features)
            
            if not object_features:
                return np.array([]), 0.0
            
            # Aggregate object features
            object_array = np.array(object_features)
            aggregated_features = np.concatenate([
                np.mean(object_array, axis=0),
                np.std(object_array, axis=0),
                np.max(object_array, axis=0)
            ])
            
            # Calculate confidence
            confidence = self._calculate_object_confidence(object_array)
            
            return aggregated_features, confidence
            
        except Exception as e:
            self.logger.error(f"Object features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_combined_fingerprint(
        self, frames: List[VideoFrame]
    ) -> Tuple[np.ndarray, float]:
        """Generate combined fingerprint from multiple features."""
        try:
            features_list = []
            confidences = []
            
            # Generate multiple fingerprints
            fingerprint_types = [
                VideoFingerprintType.FRAME_HISTOGRAM,
                VideoFingerprintType.TEMPORAL_FEATURES,
                VideoFingerprintType.COLOR_MOMENTS,
                VideoFingerprintType.EDGE_HISTOGRAM
            ]
            
            for fp_type in fingerprint_types:
                if fp_type == VideoFingerprintType.FRAME_HISTOGRAM:
                    features, confidence = await self._generate_frame_histogram(frames)
                elif fp_type == VideoFingerprintType.TEMPORAL_FEATURES:
                    features, confidence = await self._generate_temporal_features(frames)
                elif fp_type == VideoFingerprintType.COLOR_MOMENTS:
                    features, confidence = await self._generate_color_moments(frames)
                elif fp_type == VideoFingerprintType.EDGE_HISTOGRAM:
                    features, confidence = await self._generate_edge_histogram(frames)
                
                if len(features) > 0:
                    features_list.append(features)
                    confidences.append(confidence)
            
            # Combine all features
            if features_list:
                combined_features = np.concatenate(features_list)
                combined_confidence = np.mean(confidences)
            else:
                combined_features = np.array([])
                combined_confidence = 0.0
            
            return combined_features, combined_confidence
            
        except Exception as e:
            self.logger.error(f"Combined fingerprint generation failed: {e}")
            return np.array([]), 0.0
    
    def _extract_key_frames(self, frames: List[VideoFrame]) -> List[int]:
        """Extract key frame indices based on visual content."""
        try:
            if len(frames) <= 5:
                return list(range(len(frames)))
            
            # Calculate frame differences
            differences = []
            for i in range(1, len(frames)):
                prev_gray = cv2.cvtColor(frames[i-1].frame_data, cv2.COLOR_BGR2GRAY)
                curr_gray = cv2.cvtColor(frames[i].frame_data, cv2.COLOR_BGR2GRAY)
                
                diff = cv2.absdiff(prev_gray, curr_gray)
                diff_score = np.mean(diff)
                differences.append((i, diff_score))
            
            # Sort by difference score and select top frames
            differences.sort(key=lambda x: x[1], reverse=True)
            key_frames = [0]  # Always include first frame
            
            # Select frames with high differences
            for frame_idx, score in differences[:min(10, len(differences))]:
                if score > np.mean([d[1] for d in differences]):
                    key_frames.append(frame_idx)
            
            # Always include last frame
            key_frames.append(len(frames) - 1)
            
            return sorted(list(set(key_frames)))
            
        except Exception as e:
            self.logger.error(f"Key frame extraction failed: {e}")
            return [0, len(frames) - 1] if frames else []
    
    def _calculate_histogram_confidence(self, histograms: np.ndarray) -> float:
        """Calculate confidence based on histogram variance."""
        try:
            if len(histograms) == 0:
                return 0.0
            
            # Calculate temporal variance
            temporal_variance = np.mean(np.var(histograms, axis=0))
            confidence = min(1.0, temporal_variance * 10)  # Scale factor
            
            return max(0.0, confidence)
            
        except Exception:
            return 0.0
    
    def _calculate_flow_confidence(self, flow_features: np.ndarray) -> float:
        """Calculate confidence based on optical flow consistency."""
        try:
            if len(flow_features) == 0:
                return 0.0
            
            # Calculate feature stability
            feature_std = np.mean(np.std(flow_features, axis=0))
            confidence = min(1.0, feature_std / 2.0)
            
            return max(0.0, confidence)
            
        except Exception:
            return 0.0
    
    def _calculate_temporal_confidence(self, temporal_features: np.ndarray) -> float:
        """Calculate confidence based on temporal consistency."""
        try:
            if len(temporal_features) == 0:
                return 0.0
            
            # Calculate temporal stability
            temporal_std = np.mean(np.std(temporal_features, axis=0))
            confidence = min(1.0, temporal_std / 50.0)  # Scale factor
            
            return max(0.0, confidence)
            
        except Exception:
            return 0.0
    
    def _calculate_deep_confidence(self, deep_features: np.ndarray) -> float:
        """Calculate confidence based on deep feature quality."""
        try:
            if len(deep_features) == 0:
                return 0.0
            
            # Calculate feature diversity
            feature_var = np.mean(np.var(deep_features, axis=0))
            confidence = min(1.0, feature_var * 0.1)  # Scale factor
            
            return max(0.0, confidence)
            
        except Exception:
            return 0.0
    
    def _calculate_color_confidence(self, color_features: np.ndarray) -> float:
        """Calculate confidence based on color consistency."""
        try:
            if len(color_features) == 0:
                return 0.0
            
            # Calculate color stability
            color_std = np.mean(np.std(color_features, axis=0))
            confidence = min(1.0, color_std / 100.0)  # Scale factor
            
            return max(0.0, confidence)
            
        except Exception:
            return 0.0
    
    def _calculate_edge_confidence(self, edge_features: np.ndarray) -> float:
        """Calculate confidence based on edge consistency."""
        try:
            if len(edge_features) == 0:
                return 0.0
            
            # Calculate edge stability
            edge_std = np.mean(np.std(edge_features, axis=0))
            confidence = min(1.0, edge_std / 0.1)  # Scale factor
            
            return max(0.0, confidence)
            
        except Exception:
            return 0.0
    
    def _calculate_motion_confidence(self, motion_features: np.ndarray) -> float:
        """Calculate confidence based on motion consistency."""
        try:
            if len(motion_features) == 0:
                return 0.0
            
            # Calculate motion stability
            motion_std = np.mean(np.std(motion_features, axis=0))
            confidence = min(1.0, motion_std / 5.0)  # Scale factor
            
            return max(0.0, confidence)
            
        except Exception:
            return 0.0
    
    def _calculate_object_confidence(self, object_features: np.ndarray) -> float:
        """Calculate confidence based on object detection consistency."""
        try:
            if len(object_features) == 0:
                return 0.0
            
            # Calculate object detection stability
            object_std = np.mean(np.std(object_features, axis=0))
            confidence = min(1.0, object_std)
            
            return max(0.0, confidence)
            
        except Exception:
            return 0.0
    
    async def _generate_file_hash(self, file_path: str) -> str:
        """Generate SHA-256 hash of video file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"File hash generation failed: {e}")
            return ""
    
    def _generate_fingerprint_id(
        self, file_hash: str, fingerprint_type: str, data: np.ndarray
    ) -> str:
        """Generate unique fingerprint identifier."""
        content = f"{file_hash}_{fingerprint_type}_{hash(data.tobytes())}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _store_fingerprints(
        self, fingerprints: List[VideoFingerprint], creator_id: str
    ):
        """Store fingerprints in vector database."""
        try:
            for fingerprint in fingerprints:
                await self.vector_db.store_fingerprint(
                    fingerprint_id=fingerprint.fingerprint_id,
                    vector=fingerprint.data,
                    metadata={
                        'type': 'video',
                        'subtype': fingerprint.fingerprint_type.value,
                        'creator_id': creator_id,
                        'confidence': fingerprint.confidence,
                        'duration': fingerprint.metadata.duration,
                        'resolution': f"{fingerprint.metadata.width}x{fingerprint.metadata.height}",
                        'fps': fingerprint.metadata.fps,
                        'frame_count': fingerprint.frame_count,
                        'key_frames': fingerprint.key_frames,
                        'file_path': fingerprint.file_path,
                        'hash': fingerprint.hash_sha256,
                        'created_at': fingerprint.created_at.isoformat()
                    }
                )
        except Exception as e:
            self.logger.error(f"Failed to store fingerprints: {e}")
            raise
    
    async def find_similar_videos(
        self,
        fingerprint: VideoFingerprint,
        similarity_threshold: float = 0.85,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Find similar video content based on fingerprint."""
        try:
            # Search in vector database
            results = await self.vector_db.search_similar(
                vector=fingerprint.data,
                threshold=similarity_threshold,
                max_results=max_results,
                metadata_filter={'type': 'video', 'subtype': fingerprint.fingerprint_type.value}
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Similarity search failed: {e}")
            return []
    
    async def analyze_video_quality(self, fingerprint: VideoFingerprint) -> Dict[str, float]:
        """Analyze video quality metrics."""
        try:
            quality_metrics = {
                'confidence': fingerprint.confidence,
                'resolution_score': self._calculate_resolution_score(
                    fingerprint.metadata.width, fingerprint.metadata.height
                ),
                'fps_score': min(1.0, fingerprint.metadata.fps / 30.0),
                'duration_score': min(1.0, fingerprint.metadata.duration / 60.0),  # 1 minute baseline
                'frame_completeness': min(1.0, fingerprint.frame_count / 100.0),
                'feature_completeness': 1.0 if len(fingerprint.data) > 0 else 0.0
            }
            
            # Overall quality score
            quality_metrics['overall_quality'] = np.mean(list(quality_metrics.values()))
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed: {e}")
            return {'overall_quality': 0.0}
    
    def _calculate_resolution_score(self, width: int, height: int) -> float:
        """Calculate score based on video resolution."""
        try:
            total_pixels = width * height
            
            # Resolution scoring
            if total_pixels >= 3840 * 2160:  # 4K
                return 1.0
            elif total_pixels >= 1920 * 1080:  # 1080p
                return 0.8
            elif total_pixels >= 1280 * 720:  # 720p
                return 0.6
            elif total_pixels >= 854 * 480:  # 480p
                return 0.4
            else:
                return 0.2
                
        except Exception:
            return 0.0


# Factory function for creating video fingerprinting system
def create_video_fingerprinting_system(
    config: Optional[VideoAnalysisConfig] = None
) -> VideoFingerprintingSystem:
    """Create and initialize video fingerprinting system."""
    return VideoFingerprintingSystem(config)


# Export public interface
__all__ = [
    'VideoFingerprintingSystem',
    'VideoFingerprint',
    'VideoFingerprintType',
    'VideoFormat',
    'VideoQuality',
    'VideoMetadata',
    'VideoFrame',
    'VideoAnalysisConfig',
    'create_video_fingerprinting_system'
]