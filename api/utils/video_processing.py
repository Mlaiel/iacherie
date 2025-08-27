"""
Video Processing Utilities for IA Influencer Agent Platform
Advanced video analysis, processing, fingerprinting, and optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""

import cv2
import numpy as np
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple, Generator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import base64
from PIL import Image
import librosa
import soundfile as sf
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
import tensorflow as tf
from sklearn.cluster import KMeans
from scipy import stats
import imagehash
import pickle
import sqlite3
from collections import defaultdict, Counter
import threading
import time
import requests

logger = logging.getLogger(__name__)


@dataclass
class VideoMetadata:
    """Video metadata container"""
    filename: str
    duration: float
    fps: float
    width: int
    height: int
    total_frames: int
    codec: str
    bitrate: Optional[int] = None
    audio_codec: Optional[str] = None
    audio_channels: Optional[int] = None
    audio_sample_rate: Optional[int] = None
    file_size: int = 0
    creation_date: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'filename': self.filename,
            'duration': self.duration,
            'fps': self.fps,
            'width': self.width,
            'height': self.height,
            'total_frames': self.total_frames,
            'codec': self.codec,
            'bitrate': self.bitrate,
            'audio_codec': self.audio_codec,
            'audio_channels': self.audio_channels,
            'audio_sample_rate': self.audio_sample_rate,
            'file_size': self.file_size,
            'creation_date': self.creation_date.isoformat() if self.creation_date else None,
            'aspect_ratio': round(self.width / self.height, 2) if self.height > 0 else 0,
            'resolution': f"{self.width}x{self.height}"
        }


@dataclass
class VideoFingerprint:
    """Video fingerprint container"""
    video_hash: str
    frame_hashes: List[str] = field(default_factory=list)
    histogram_features: List[float] = field(default_factory=list)
    motion_features: List[float] = field(default_factory=list)
    audio_fingerprint: Optional[str] = None
    temporal_features: List[float] = field(default_factory=list)
    scene_changes: List[int] = field(default_factory=list)
    color_palette: List[Tuple[int, int, int]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'video_hash': self.video_hash,
            'frame_hashes': self.frame_hashes,
            'histogram_features': self.histogram_features,
            'motion_features': self.motion_features,
            'audio_fingerprint': self.audio_fingerprint,
            'temporal_features': self.temporal_features,
            'scene_changes': self.scene_changes,
            'color_palette': self.color_palette,
            'fingerprint_version': '2.0'
        }


@dataclass
class VideoAnalysisResult:
    """Video analysis results"""
    metadata: VideoMetadata
    fingerprint: VideoFingerprint
    quality_score: float
    complexity_score: float
    motion_intensity: float
    scene_count: int
    dominant_colors: List[Tuple[int, int, int]]
    brightness_stats: Dict[str, float]
    contrast_stats: Dict[str, float]
    audio_analysis: Optional[Dict[str, Any]] = None
    object_detection: List[Dict[str, Any]] = field(default_factory=list)
    face_detection: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'metadata': self.metadata.to_dict(),
            'fingerprint': self.fingerprint.to_dict(),
            'quality_score': round(self.quality_score, 3),
            'complexity_score': round(self.complexity_score, 3),
            'motion_intensity': round(self.motion_intensity, 3),
            'scene_count': self.scene_count,
            'dominant_colors': self.dominant_colors,
            'brightness_stats': {k: round(v, 3) for k, v in self.brightness_stats.items()},
            'contrast_stats': {k: round(v, 3) for k, v in self.contrast_stats.items()},
            'audio_analysis': self.audio_analysis,
            'object_detection': self.object_detection,
            'face_detection': self.face_detection
        }


@dataclass
class VideoOptimizationResult:
    """Video optimization results"""
    original_size: int
    optimized_size: int
    compression_ratio: float
    quality_retention: float
    processing_time: float
    output_path: str
    optimization_settings: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'original_size': self.original_size,
            'optimized_size': self.optimized_size,
            'compression_ratio': round(self.compression_ratio, 3),
            'quality_retention': round(self.quality_retention, 3),
            'processing_time': round(self.processing_time, 3),
            'output_path': self.output_path,
            'optimization_settings': self.optimization_settings,
            'size_reduction_mb': round((self.original_size - self.optimized_size) / 1024 / 1024, 2)
        }


class VideoMetadataExtractor:
    """Extract comprehensive video metadata"""
    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
    
    def extract_metadata(self, video_path: str) -> VideoMetadata:
        """Extract video metadata"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Use OpenCV for basic metadata
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        try:
            # Basic properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Codec information
            fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
            
            # File information
            file_size = os.path.getsize(video_path)
            creation_date = datetime.fromtimestamp(os.path.getctime(video_path))
            
            # Try to get additional info with moviepy
            audio_codec = None
            audio_channels = None
            audio_sample_rate = None
            bitrate = None
            
            try:
                with VideoFileClip(video_path) as clip:
                    if clip.audio:
                        audio_sample_rate = clip.audio.fps
                        audio_channels = clip.audio.nchannels
                        audio_codec = "audio_present"  # moviepy doesn't provide codec info directly
                    
                    # Estimate bitrate
                    if duration > 0:
                        bitrate = int((file_size * 8) / duration)  # bits per second
                        
            except Exception as e:
                logger.warning(f"Could not extract audio metadata: {str(e)}")
            
            return VideoMetadata(
                filename=os.path.basename(video_path),
                duration=duration,
                fps=fps,
                width=width,
                height=height,
                total_frames=total_frames,
                codec=codec,
                bitrate=bitrate,
                audio_codec=audio_codec,
                audio_channels=audio_channels,
                audio_sample_rate=audio_sample_rate,
                file_size=file_size,
                creation_date=creation_date
            )
            
        finally:
            cap.release()
    
    def extract_metadata_ffprobe(self, video_path: str) -> Dict[str, Any]:
        """Extract detailed metadata using ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
            
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"ffprobe metadata extraction failed: {str(e)}")
            return {}


class VideoFrameExtractor:
    """Extract and process video frames"""
    
    def __init__(self, max_frames_per_second: float = 1.0):
        self.max_frames_per_second = max_frames_per_second
    
    def extract_frames(self, video_path: str, 
                      output_dir: Optional[str] = None,
                      frame_format: str = 'jpg',
                      max_frames: Optional[int] = None) -> List[str]:
        """Extract frames from video"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame interval
        frame_interval = max(1, int(fps / self.max_frames_per_second))
        
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        frame_paths = []
        frame_count = 0
        extracted_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    frame_filename = f"frame_{extracted_count:06d}.{frame_format}"
                    frame_path = os.path.join(output_dir, frame_filename)
                    
                    cv2.imwrite(frame_path, frame)
                    frame_paths.append(frame_path)
                    extracted_count += 1
                    
                    if max_frames and extracted_count >= max_frames:
                        break
                
                frame_count += 1
                
        finally:
            cap.release()
        
        return frame_paths
    
    def extract_key_frames(self, video_path: str, 
                          threshold: float = 30.0) -> List[np.ndarray]:
        """Extract key frames based on scene changes"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        key_frames = []
        prev_frame = None
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if prev_frame is not None:
                    # Calculate frame difference
                    diff = cv2.absdiff(
                        cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                        cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                    )
                    
                    # Calculate mean difference
                    mean_diff = np.mean(diff)
                    
                    if mean_diff > threshold:
                        key_frames.append(frame.copy())
                
                prev_frame = frame.copy()
                
        finally:
            cap.release()
        
        return key_frames
    
    def extract_representative_frames(self, video_path: str, 
                                    num_frames: int = 10) -> List[np.ndarray]:
        """Extract representative frames using k-means clustering"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Extract frames at regular intervals
        frame_indices = np.linspace(0, total_frames - 1, min(100, total_frames), dtype=int)
        
        frames = []
        frame_features = []
        
        try:
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if ret:
                    frames.append((idx, frame))
                    
                    # Extract features (color histogram)
                    hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                    frame_features.append(hist.flatten())
                    
        finally:
            cap.release()
        
        if len(frame_features) == 0:
            return []
        
        # Cluster frames
        n_clusters = min(num_frames, len(frame_features))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(frame_features)
        
        # Select representative frame from each cluster
        representative_frames = []
        
        for cluster_id in range(n_clusters):
            cluster_frames = [(frames[i], np.linalg.norm(frame_features[i] - kmeans.cluster_centers_[cluster_id])) 
                            for i in range(len(frames)) if cluster_labels[i] == cluster_id]
            
            if cluster_frames:
                # Select frame closest to cluster center
                best_frame = min(cluster_frames, key=lambda x: x[1])
                representative_frames.append(best_frame[0][1])
        
        return representative_frames


class VideoFingerprinter:
    """Generate unique video fingerprints for duplicate detection"""
    
    def __init__(self):
        self.frame_extractor = VideoFrameExtractor()
    
    def generate_fingerprint(self, video_path: str) -> VideoFingerprint:
        """Generate comprehensive video fingerprint"""
        # Generate video hash
        video_hash = self._generate_video_hash(video_path)
        
        # Extract representative frames
        frames = self.frame_extractor.extract_representative_frames(video_path, 20)
        
        # Generate frame hashes
        frame_hashes = [self._generate_frame_hash(frame) for frame in frames]
        
        # Extract histogram features
        histogram_features = self._extract_histogram_features(frames)
        
        # Extract motion features
        motion_features = self._extract_motion_features(video_path)
        
        # Extract temporal features
        temporal_features = self._extract_temporal_features(video_path)
        
        # Detect scene changes
        scene_changes = self._detect_scene_changes(video_path)
        
        # Extract color palette
        color_palette = self._extract_color_palette(frames)
        
        # Extract audio fingerprint if available
        audio_fingerprint = self._extract_audio_fingerprint(video_path)
        
        return VideoFingerprint(
            video_hash=video_hash,
            frame_hashes=frame_hashes,
            histogram_features=histogram_features,
            motion_features=motion_features,
            audio_fingerprint=audio_fingerprint,
            temporal_features=temporal_features,
            scene_changes=scene_changes,
            color_palette=color_palette
        )
    
    def _generate_video_hash(self, video_path: str) -> str:
        """Generate hash of entire video file"""
        hash_algo = hashlib.sha256()
        
        with open(video_path, 'rb') as f:
            # Read file in chunks to handle large videos
            while chunk := f.read(8192):
                hash_algo.update(chunk)
        
        return hash_algo.hexdigest()
    
    def _generate_frame_hash(self, frame: np.ndarray) -> str:
        """Generate perceptual hash for a frame"""
        # Convert to PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        
        # Generate perceptual hash
        phash = imagehash.phash(pil_image, hash_size=16)
        return str(phash)
    
    def _extract_histogram_features(self, frames: List[np.ndarray]) -> List[float]:
        """Extract color histogram features"""
        if not frames:
            return []
        
        all_features = []
        
        for frame in frames:
            # Calculate color histogram
            hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            normalized_hist = cv2.normalize(hist, hist).flatten()
            all_features.extend(normalized_hist.tolist())
        
        # Average features across frames
        features_array = np.array(all_features).reshape(len(frames), -1)
        averaged_features = np.mean(features_array, axis=0)
        
        return averaged_features.tolist()
    
    def _extract_motion_features(self, video_path: str) -> List[float]:
        """Extract motion-based features"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return []
        
        motion_vectors = []
        prev_frame = None
        
        try:
            # Sample frames for motion analysis
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, total_frames // 50)  # Sample 50 frames max
            
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % sample_interval == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    if prev_frame is not None:
                        # Calculate optical flow
                        flow = cv2.calcOpticalFlowPyrLK(
                            prev_frame, gray,
                            np.array([[100, 100]], dtype=np.float32),
                            None,
                            winSize=(15, 15),
                            maxLevel=2
                        )[0]
                        
                        if flow is not None and len(flow) > 0:
                            motion_magnitude = np.linalg.norm(flow[0])
                            motion_vectors.append(motion_magnitude)
                    
                    prev_frame = gray.copy()
                
                frame_count += 1
                
        finally:
            cap.release()
        
        if motion_vectors:
            return [
                np.mean(motion_vectors),
                np.std(motion_vectors),
                np.max(motion_vectors),
                np.min(motion_vectors)
            ]
        
        return [0.0, 0.0, 0.0, 0.0]
    
    def _extract_temporal_features(self, video_path: str) -> List[float]:
        """Extract temporal features like scene transitions"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return []
        
        brightness_values = []
        contrast_values = []
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Calculate brightness (mean)
                brightness = np.mean(gray)
                brightness_values.append(brightness)
                
                # Calculate contrast (standard deviation)
                contrast = np.std(gray)
                contrast_values.append(contrast)
                
        finally:
            cap.release()
        
        if brightness_values and contrast_values:
            return [
                np.mean(brightness_values),
                np.std(brightness_values),
                np.mean(contrast_values),
                np.std(contrast_values)
            ]
        
        return [0.0, 0.0, 0.0, 0.0]
    
    def _detect_scene_changes(self, video_path: str, threshold: float = 30.0) -> List[int]:
        """Detect scene change frame indices"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return []
        
        scene_changes = []
        prev_frame = None
        frame_idx = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    # Calculate frame difference
                    diff = cv2.absdiff(gray, prev_frame)
                    mean_diff = np.mean(diff)
                    
                    if mean_diff > threshold:
                        scene_changes.append(frame_idx)
                
                prev_frame = gray.copy()
                frame_idx += 1
                
        finally:
            cap.release()
        
        return scene_changes
    
    def _extract_color_palette(self, frames: List[np.ndarray], 
                             num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """Extract dominant color palette from frames"""
        if not frames:
            return []
        
        # Combine all frames and sample pixels
        all_pixels = []
        
        for frame in frames[:5]:  # Use first 5 frames
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (50, 50))
            pixels = small_frame.reshape(-1, 3)
            all_pixels.extend(pixels)
        
        if not all_pixels:
            return []
        
        # Cluster colors
        pixels_array = np.array(all_pixels)
        
        n_colors = min(num_colors, len(pixels_array))
        kmeans = KMeans(n_clusters=n_colors, random_state=42)
        kmeans.fit(pixels_array)
        
        # Convert to RGB tuples
        colors = []
        for center in kmeans.cluster_centers_:
            # Convert from BGR to RGB
            color = (int(center[2]), int(center[1]), int(center[0]))
            colors.append(color)
        
        return colors
    
    def _extract_audio_fingerprint(self, video_path: str) -> Optional[str]:
        """Extract audio fingerprint if audio track exists"""
        try:
            with VideoFileClip(video_path) as clip:
                if clip.audio is None:
                    return None
                
                # Extract audio to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                    clip.audio.write_audiofile(temp_audio.name, verbose=False, logger=None)
                    
                    # Load audio with librosa
                    y, sr = librosa.load(temp_audio.name, sr=22050)
                    
                    # Extract MFCC features
                    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                    mfcc_mean = np.mean(mfccs, axis=1)
                    
                    # Create hash from features
                    feature_bytes = mfcc_mean.tobytes()
                    audio_hash = hashlib.sha256(feature_bytes).hexdigest()[:32]
                    
                    # Cleanup
                    os.unlink(temp_audio.name)
                    
                    return audio_hash
                    
        except Exception as e:
            logger.warning(f"Audio fingerprint extraction failed: {str(e)}")
            return None


class VideoAnalyzer:
    """Comprehensive video analysis"""
    
    def __init__(self):
        self.metadata_extractor = VideoMetadataExtractor()
        self.fingerprinter = VideoFingerprinter()
        self.frame_extractor = VideoFrameExtractor()
    
    def analyze_video(self, video_path: str, 
                     include_object_detection: bool = False,
                     include_face_detection: bool = False) -> VideoAnalysisResult:
        """Comprehensive video analysis"""
        # Extract metadata
        metadata = self.metadata_extractor.extract_metadata(video_path)
        
        # Generate fingerprint
        fingerprint = self.fingerprinter.generate_fingerprint(video_path)
        
        # Analyze quality and complexity
        quality_score = self._calculate_quality_score(video_path, metadata)
        complexity_score = self._calculate_complexity_score(fingerprint)
        
        # Analyze motion
        motion_intensity = self._calculate_motion_intensity(fingerprint.motion_features)
        
        # Count scenes
        scene_count = len(fingerprint.scene_changes)
        
        # Extract visual statistics
        brightness_stats, contrast_stats = self._calculate_visual_statistics(video_path)
        
        # Dominant colors
        dominant_colors = fingerprint.color_palette
        
        # Audio analysis
        audio_analysis = self._analyze_audio(video_path) if metadata.audio_codec else None
        
        # Object and face detection (optional)
        object_detection = []
        face_detection = []
        
        if include_object_detection:
            object_detection = self._detect_objects(video_path)
        
        if include_face_detection:
            face_detection = self._detect_faces(video_path)
        
        return VideoAnalysisResult(
            metadata=metadata,
            fingerprint=fingerprint,
            quality_score=quality_score,
            complexity_score=complexity_score,
            motion_intensity=motion_intensity,
            scene_count=scene_count,
            dominant_colors=dominant_colors,
            brightness_stats=brightness_stats,
            contrast_stats=contrast_stats,
            audio_analysis=audio_analysis,
            object_detection=object_detection,
            face_detection=face_detection
        )
    
    def _calculate_quality_score(self, video_path: str, metadata: VideoMetadata) -> float:
        """Calculate video quality score"""
        score = 0.0
        
        # Resolution score (0-30 points)
        if metadata.width >= 1920 and metadata.height >= 1080:  # 1080p+
            score += 30
        elif metadata.width >= 1280 and metadata.height >= 720:  # 720p
            score += 20
        elif metadata.width >= 854 and metadata.height >= 480:   # 480p
            score += 10
        
        # Frame rate score (0-20 points)
        if metadata.fps >= 60:
            score += 20
        elif metadata.fps >= 30:
            score += 15
        elif metadata.fps >= 24:
            score += 10
        
        # Bitrate score (0-25 points)
        if metadata.bitrate:
            # Good bitrate thresholds (bits per second)
            if metadata.bitrate >= 5000000:  # 5 Mbps
                score += 25
            elif metadata.bitrate >= 2000000:  # 2 Mbps
                score += 15
            elif metadata.bitrate >= 1000000:  # 1 Mbps
                score += 10
        
        # Codec score (0-15 points)
        modern_codecs = ['H264', 'H265', 'VP9', 'AV01']
        if any(codec in metadata.codec.upper() for codec in modern_codecs):
            score += 15
        elif metadata.codec:
            score += 5
        
        # Visual analysis score (0-10 points)
        try:
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    # Check for blur/sharpness
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                    
                    if laplacian_var > 500:  # Sharp
                        score += 10
                    elif laplacian_var > 100:  # Moderate
                        score += 5
                
            cap.release()
        except Exception:
            pass
        
        return min(100.0, score)
    
    def _calculate_complexity_score(self, fingerprint: VideoFingerprint) -> float:
        """Calculate video complexity score"""
        score = 0.0
        
        # Scene changes complexity (0-30 points)
        scene_count = len(fingerprint.scene_changes)
        if scene_count > 50:
            score += 30
        elif scene_count > 20:
            score += 20
        elif scene_count > 5:
            score += 10
        
        # Motion complexity (0-25 points)
        if fingerprint.motion_features:
            motion_mean = fingerprint.motion_features[0]
            motion_std = fingerprint.motion_features[1]
            
            if motion_mean > 10:
                score += 15
            elif motion_mean > 5:
                score += 10
            
            if motion_std > 5:
                score += 10
            elif motion_std > 2:
                score += 5
        
        # Color complexity (0-25 points)
        color_count = len(fingerprint.color_palette)
        if color_count >= 5:
            score += 25
        elif color_count >= 3:
            score += 15
        elif color_count >= 1:
            score += 5
        
        # Histogram complexity (0-20 points)
        if fingerprint.histogram_features:
            hist_std = np.std(fingerprint.histogram_features)
            if hist_std > 0.1:
                score += 20
            elif hist_std > 0.05:
                score += 10
        
        return min(100.0, score)
    
    def _calculate_motion_intensity(self, motion_features: List[float]) -> float:
        """Calculate motion intensity"""
        if not motion_features or len(motion_features) < 2:
            return 0.0
        
        motion_mean = motion_features[0]
        motion_std = motion_features[1]
        
        # Normalize and combine
        intensity = min(100.0, (motion_mean * 2) + (motion_std * 1.5))
        return intensity
    
    def _calculate_visual_statistics(self, video_path: str) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Calculate brightness and contrast statistics"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {}, {}
        
        brightness_values = []
        contrast_values = []
        
        try:
            # Sample frames for statistics
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, total_frames // 50)
            
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % sample_interval == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    brightness = np.mean(gray)
                    contrast = np.std(gray)
                    
                    brightness_values.append(brightness)
                    contrast_values.append(contrast)
                
                frame_count += 1
                
        finally:
            cap.release()
        
        brightness_stats = {}
        contrast_stats = {}
        
        if brightness_values:
            brightness_stats = {
                'mean': np.mean(brightness_values),
                'std': np.std(brightness_values),
                'min': np.min(brightness_values),
                'max': np.max(brightness_values),
                'median': np.median(brightness_values)
            }
        
        if contrast_values:
            contrast_stats = {
                'mean': np.mean(contrast_values),
                'std': np.std(contrast_values),
                'min': np.min(contrast_values),
                'max': np.max(contrast_values),
                'median': np.median(contrast_values)
            }
        
        return brightness_stats, contrast_stats
    
    def _analyze_audio(self, video_path: str) -> Optional[Dict[str, Any]]:
        """Analyze audio track"""
        try:
            with VideoFileClip(video_path) as clip:
                if clip.audio is None:
                    return None
                
                # Extract audio to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                    clip.audio.write_audiofile(temp_audio.name, verbose=False, logger=None)
                    
                    # Load audio with librosa
                    y, sr = librosa.load(temp_audio.name, sr=22050)
                    
                    # Extract features
                    rms = librosa.feature.rms(y=y)[0]
                    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
                    zero_crossings = librosa.feature.zero_crossing_rate(y)[0]
                    
                    # Calculate statistics
                    audio_analysis = {
                        'duration': len(y) / sr,
                        'sample_rate': sr,
                        'rms_mean': float(np.mean(rms)),
                        'rms_std': float(np.std(rms)),
                        'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                        'spectral_centroid_std': float(np.std(spectral_centroids)),
                        'zero_crossing_rate_mean': float(np.mean(zero_crossings)),
                        'energy': float(np.sum(y ** 2))
                    }
                    
                    # Cleanup
                    os.unlink(temp_audio.name)
                    
                    return audio_analysis
                    
        except Exception as e:
            logger.warning(f"Audio analysis failed: {str(e)}")
            return None
    
    def _detect_objects(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect objects in video (simplified implementation)"""
        # This would typically use a pre-trained model like YOLO or SSD
        # For now, return empty list
        logger.info("Object detection not implemented - requires model loading")
        return []
    
    def _detect_faces(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect faces in video"""
        try:
            # Load face cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return []
            
            face_detections = []
            frame_count = 0
            
            # Sample every 30th frame
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % 30 == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    for (x, y, w, h) in faces:
                        face_detections.append({
                            'frame': frame_count,
                            'timestamp': frame_count / cap.get(cv2.CAP_PROP_FPS),
                            'x': int(x),
                            'y': int(y),
                            'width': int(w),
                            'height': int(h),
                            'confidence': 0.8  # Haar cascades don't provide confidence
                        })
                
                frame_count += 1
            
            cap.release()
            return face_detections
            
        except Exception as e:
            logger.warning(f"Face detection failed: {str(e)}")
            return []


class VideoOptimizer:
    """Video optimization and compression"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ffmpeg_available = self._check_ffmpeg()
    
    def optimize_video(self, input_path: str, 
                      output_path: str,
                      target_size_mb: Optional[int] = None,
                      quality: str = 'medium',
                      platform: str = 'general') -> VideoOptimizationResult:
        """Optimize video for size and quality"""
        start_time = time.time()
        original_size = os.path.getsize(input_path)
        
        # Get optimization settings
        settings = self._get_optimization_settings(quality, platform, target_size_mb)
        
        if self.ffmpeg_available:
            success = self._optimize_with_ffmpeg(input_path, output_path, settings)
        else:
            success = self._optimize_with_moviepy(input_path, output_path, settings)
        
        if not success:
            raise RuntimeError("Video optimization failed")
        
        processing_time = time.time() - start_time
        optimized_size = os.path.getsize(output_path)
        compression_ratio = original_size / optimized_size if optimized_size > 0 else 1.0
        
        # Estimate quality retention (simplified)
        quality_retention = self._estimate_quality_retention(settings, compression_ratio)
        
        return VideoOptimizationResult(
            original_size=original_size,
            optimized_size=optimized_size,
            compression_ratio=compression_ratio,
            quality_retention=quality_retention,
            processing_time=processing_time,
            output_path=output_path,
            optimization_settings=settings
        )
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _get_optimization_settings(self, quality: str, platform: str, 
                                 target_size_mb: Optional[int]) -> Dict[str, Any]:
        """Get optimization settings based on parameters"""
        base_settings = {
            'codec': 'libx264',
            'preset': 'medium',
            'crf': 23,
            'audio_codec': 'aac',
            'audio_bitrate': '128k'
        }
        
        # Quality adjustments
        if quality == 'high':
            base_settings['crf'] = 18
            base_settings['preset'] = 'slow'
        elif quality == 'low':
            base_settings['crf'] = 28
            base_settings['preset'] = 'fast'
        
        # Platform-specific optimizations
        platform_settings = {
            'youtube': {
                'format': 'mp4',
                'max_width': 1920,
                'max_height': 1080,
                'fps': 30
            },
            'instagram': {
                'format': 'mp4',
                'max_width': 1080,
                'max_height': 1080,
                'fps': 30
            },
            'tiktok': {
                'format': 'mp4',
                'max_width': 720,
                'max_height': 1280,
                'fps': 30
            },
            'twitter': {
                'format': 'mp4',
                'max_width': 1280,
                'max_height': 720,
                'fps': 30
            }
        }
        
        if platform in platform_settings:
            base_settings.update(platform_settings[platform])
        
        # Target size adjustment
        if target_size_mb:
            # Estimate bitrate for target size (simplified)
            estimated_bitrate = int((target_size_mb * 8 * 1024) / 60)  # Assume 60 second video
            base_settings['video_bitrate'] = f"{estimated_bitrate}k"
        
        return base_settings
    
    def _optimize_with_ffmpeg(self, input_path: str, output_path: str, 
                            settings: Dict[str, Any]) -> bool:
        """Optimize video using FFmpeg"""
        try:
            cmd = [
                'ffmpeg', '-i', input_path,
                '-c:v', settings['codec'],
                '-preset', settings['preset'],
                '-crf', str(settings['crf']),
                '-c:a', settings['audio_codec'],
                '-b:a', settings['audio_bitrate']
            ]
            
            # Add resolution scaling if specified
            if 'max_width' in settings and 'max_height' in settings:
                scale_filter = f"scale='min({settings['max_width']},iw)':'min({settings['max_height']},ih)':force_original_aspect_ratio=decrease"
                cmd.extend(['-vf', scale_filter])
            
            # Add frame rate if specified
            if 'fps' in settings:
                cmd.extend(['-r', str(settings['fps'])])
            
            # Add bitrate if specified
            if 'video_bitrate' in settings:
                cmd.extend(['-b:v', settings['video_bitrate']])
            
            cmd.extend(['-y', output_path])  # Overwrite output file
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"FFmpeg optimization failed: {str(e)}")
            return False
    
    def _optimize_with_moviepy(self, input_path: str, output_path: str, 
                             settings: Dict[str, Any]) -> bool:
        """Optimize video using MoviePy"""
        try:
            with VideoFileClip(input_path) as clip:
                # Apply resolution scaling
                if 'max_width' in settings and 'max_height' in settings:
                    max_w, max_h = settings['max_width'], settings['max_height']
                    if clip.w > max_w or clip.h > max_h:
                        clip = clip.resize(height=min(max_h, clip.h))
                        if clip.w > max_w:
                            clip = clip.resize(width=max_w)
                
                # Apply frame rate
                if 'fps' in settings and clip.fps > settings['fps']:
                    clip = clip.set_fps(settings['fps'])
                
                # Write video
                clip.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile=os.path.join(self.temp_dir, 'temp_audio.m4a'),
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )
            
            return True
            
        except Exception as e:
            logger.error(f"MoviePy optimization failed: {str(e)}")
            return False
    
    def _estimate_quality_retention(self, settings: Dict[str, Any], 
                                   compression_ratio: float) -> float:
        """Estimate quality retention based on settings"""
        base_quality = 100.0
        
        # CRF impact
        if 'crf' in settings:
            crf = settings['crf']
            if crf > 28:
                base_quality *= 0.6
            elif crf > 23:
                base_quality *= 0.8
            elif crf > 18:
                base_quality *= 0.95
        
        # Compression ratio impact
        if compression_ratio > 10:
            base_quality *= 0.7
        elif compression_ratio > 5:
            base_quality *= 0.85
        elif compression_ratio > 2:
            base_quality *= 0.95
        
        return min(100.0, base_quality)


class VideoDuplicateDetector:
    """Detect duplicate and similar videos"""
    
    def __init__(self, database_path: Optional[str] = None):
        self.database_path = database_path or os.path.join(tempfile.gettempdir(), 'video_fingerprints.db')
        self.fingerprinter = VideoFingerprinter()
        self._init_database()
    
    def _init_database(self):
        """Initialize fingerprint database"""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS video_fingerprints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE,
                    video_hash TEXT,
                    fingerprint_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def add_video(self, video_path: str) -> str:
        """Add video fingerprint to database"""
        fingerprint = self.fingerprinter.generate_fingerprint(video_path)
        fingerprint_json = json.dumps(fingerprint.to_dict())
        
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO video_fingerprints 
                (file_path, video_hash, fingerprint_data)
                VALUES (?, ?, ?)
            """, (video_path, fingerprint.video_hash, fingerprint_json))
            conn.commit()
        
        return fingerprint.video_hash
    
    def find_duplicates(self, video_path: str, 
                       similarity_threshold: float = 0.9) -> List[Dict[str, Any]]:
        """Find duplicate or similar videos"""
        target_fingerprint = self.fingerprinter.generate_fingerprint(video_path)
        
        duplicates = []
        
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.execute("""
                SELECT file_path, video_hash, fingerprint_data 
                FROM video_fingerprints
                WHERE file_path != ?
            """, (video_path,))
            
            for row in cursor.fetchall():
                stored_path, stored_hash, stored_fingerprint_json = row
                stored_fingerprint_data = json.loads(stored_fingerprint_json)
                stored_fingerprint = VideoFingerprint(**stored_fingerprint_data)
                
                # Calculate similarity
                similarity = self._calculate_similarity(target_fingerprint, stored_fingerprint)
                
                if similarity >= similarity_threshold:
                    duplicates.append({
                        'file_path': stored_path,
                        'video_hash': stored_hash,
                        'similarity_score': similarity,
                        'match_type': 'exact' if similarity > 0.98 else 'similar'
                    })
        
        return sorted(duplicates, key=lambda x: x['similarity_score'], reverse=True)
    
    def _calculate_similarity(self, fp1: VideoFingerprint, fp2: VideoFingerprint) -> float:
        """Calculate similarity between two video fingerprints"""
        similarity_scores = []
        
        # Exact hash match
        if fp1.video_hash == fp2.video_hash:
            return 1.0
        
        # Frame hash similarity
        if fp1.frame_hashes and fp2.frame_hashes:
            frame_similarities = []
            for hash1 in fp1.frame_hashes:
                for hash2 in fp2.frame_hashes:
                    # Calculate Hamming distance for perceptual hashes
                    hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
                    similarity = 1.0 - (hamming_distance / len(hash1))
                    frame_similarities.append(similarity)
            
            if frame_similarities:
                similarity_scores.append(max(frame_similarities))
        
        # Histogram similarity
        if fp1.histogram_features and fp2.histogram_features:
            hist1 = np.array(fp1.histogram_features)
            hist2 = np.array(fp2.histogram_features)
            
            # Calculate correlation
            correlation = np.corrcoef(hist1, hist2)[0, 1]
            if not np.isnan(correlation):
                similarity_scores.append(max(0, correlation))
        
        # Motion similarity
        if fp1.motion_features and fp2.motion_features:
            motion1 = np.array(fp1.motion_features)
            motion2 = np.array(fp2.motion_features)
            
            # Calculate cosine similarity
            dot_product = np.dot(motion1, motion2)
            norms = np.linalg.norm(motion1) * np.linalg.norm(motion2)
            
            if norms > 0:
                cosine_sim = dot_product / norms
                similarity_scores.append(max(0, cosine_sim))
        
        # Audio similarity
        if fp1.audio_fingerprint and fp2.audio_fingerprint:
            # Simple string comparison for audio hashes
            audio_sim = 1.0 if fp1.audio_fingerprint == fp2.audio_fingerprint else 0.0
            similarity_scores.append(audio_sim)
        
        # Return average similarity
        return np.mean(similarity_scores) if similarity_scores else 0.0


class VideoProcessor:
    """Main video processing coordinator"""
    
    def __init__(self):
        self.analyzer = VideoAnalyzer()
        self.optimizer = VideoOptimizer()
        self.duplicate_detector = VideoDuplicateDetector()
        self.metadata_extractor = VideoMetadataExtractor()
    
    async def process_video_comprehensive(self, video_path: str,
                                        optimize: bool = False,
                                        check_duplicates: bool = False,
                                        optimization_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Comprehensive video processing"""
        if not os.path.exists(video_path):
            return {'error': 'Video file not found'}
        
        try:
            # Basic analysis
            analysis_result = self.analyzer.analyze_video(
                video_path, 
                include_object_detection=False,
                include_face_detection=True
            )
            
            results = {
                'analysis': analysis_result.to_dict(),
                'processing_timestamp': datetime.utcnow().isoformat()
            }
            
            # Optimization
            if optimize:
                optimization_result = await self._optimize_video_async(
                    video_path, optimization_settings or {}
                )
                results['optimization'] = optimization_result.to_dict()
            
            # Duplicate check
            if check_duplicates:
                # Add to database first
                video_hash = self.duplicate_detector.add_video(video_path)
                
                # Find duplicates
                duplicates = self.duplicate_detector.find_duplicates(video_path, 0.8)
                results['duplicate_check'] = {
                    'video_hash': video_hash,
                    'duplicates_found': len(duplicates),
                    'duplicates': duplicates
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive video processing failed: {str(e)}")
            return {'error': str(e)}
    
    async def _optimize_video_async(self, video_path: str, 
                                   settings: Dict[str, Any]) -> VideoOptimizationResult:
        """Asynchronous video optimization"""
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor() as executor:
            # Create optimized output path
            path_obj = Path(video_path)
            output_path = str(path_obj.parent / f"{path_obj.stem}_optimized{path_obj.suffix}")
            
            # Run optimization in thread pool
            optimization_result = await loop.run_in_executor(
                executor,
                self.optimizer.optimize_video,
                video_path,
                output_path,
                settings.get('target_size_mb'),
                settings.get('quality', 'medium'),
                settings.get('platform', 'general')
            )
            
            return optimization_result
    
    def batch_process_videos(self, video_paths: List[str],
                           analyze: bool = True,
                           optimize: bool = False,
                           check_duplicates: bool = False) -> List[Dict[str, Any]]:
        """Process multiple videos in batch"""
        results = []
        
        for i, video_path in enumerate(video_paths):
            try:
                result = {
                    'index': i,
                    'file_path': video_path,
                    'file_exists': os.path.exists(video_path)
                }
                
                if result['file_exists']:
                    if analyze:
                        analysis = self.analyzer.analyze_video(video_path)
                        result['analysis'] = analysis.to_dict()
                    
                    if check_duplicates:
                        video_hash = self.duplicate_detector.add_video(video_path)
                        duplicates = self.duplicate_detector.find_duplicates(video_path)
                        result['duplicates'] = {
                            'hash': video_hash,
                            'matches': duplicates
                        }
                
                results.append(result)
                
            except Exception as e:
                results.append({
                    'index': i,
                    'file_path': video_path,
                    'error': str(e)
                })
        
        return results
    
    def generate_video_report(self, video_path: str) -> Dict[str, Any]:
        """Generate comprehensive video report"""
        analysis = self.analyzer.analyze_video(video_path, 
                                             include_face_detection=True)
        
        report = {
            'file_info': {
                'path': video_path,
                'exists': os.path.exists(video_path),
                'size_mb': round(os.path.getsize(video_path) / 1024 / 1024, 2) if os.path.exists(video_path) else 0
            },
            'technical_analysis': analysis.to_dict(),
            'quality_assessment': {
                'overall_score': analysis.quality_score,
                'complexity_score': analysis.complexity_score,
                'motion_intensity': analysis.motion_intensity,
                'visual_quality': self._assess_visual_quality(analysis),
                'audio_quality': self._assess_audio_quality(analysis.audio_analysis),
                'recommendations': self._generate_recommendations(analysis)
            },
            'content_analysis': {
                'scene_count': analysis.scene_count,
                'dominant_colors': analysis.dominant_colors,
                'faces_detected': len(analysis.face_detection),
                'objects_detected': len(analysis.object_detection)
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return report
    
    def _assess_visual_quality(self, analysis: VideoAnalysisResult) -> str:
        """Assess visual quality"""
        score = analysis.quality_score
        
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Fair'
        else:
            return 'Poor'
    
    def _assess_audio_quality(self, audio_analysis: Optional[Dict[str, Any]]) -> str:
        """Assess audio quality"""
        if not audio_analysis:
            return 'No Audio'
        
        # Simple heuristic based on energy and spectral features
        energy = audio_analysis.get('energy', 0)
        rms_mean = audio_analysis.get('rms_mean', 0)
        
        if energy > 1000 and rms_mean > 0.1:
            return 'Good'
        elif energy > 100 and rms_mean > 0.05:
            return 'Fair'
        else:
            return 'Poor'
    
    def _generate_recommendations(self, analysis: VideoAnalysisResult) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Resolution recommendations
        if analysis.metadata.width < 1280 or analysis.metadata.height < 720:
            recommendations.append("Consider increasing resolution to at least 720p for better quality")
        
        # Frame rate recommendations
        if analysis.metadata.fps < 24:
            recommendations.append("Frame rate is below standard 24fps - consider increasing")
        
        # Quality recommendations
        if analysis.quality_score < 50:
            recommendations.append("Overall video quality is low - consider re-encoding with higher quality settings")
        
        # Motion recommendations
        if analysis.motion_intensity < 10:
            recommendations.append("Low motion detected - video might benefit from stabilization")
        elif analysis.motion_intensity > 80:
            recommendations.append("High motion detected - consider motion blur reduction")
        
        # Audio recommendations
        if not analysis.audio_analysis:
            recommendations.append("No audio track detected - consider adding audio if appropriate")
        
        # Scene recommendations
        if analysis.scene_count > 100:
            recommendations.append("High number of scene changes detected - consider reducing cuts for better flow")
        
        return recommendations


class VideoProcessingError(Exception):
    """Custom exception for video processing errors"""
    pass
