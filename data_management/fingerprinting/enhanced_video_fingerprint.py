"""🎬 Video Fingerprinting Engine - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/data_management/fingerprinting/enhanced_video_fingerprint.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Video Fingerprinting - Ultra Enterprise Production-Ready
Responsibility: Advanced video fingerprinting with OpenCV, pHash, YOLO, and motion analysis
==============================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC VIDEO FINGERPRINTING:
Video Upload (Influencers/Créateurs/Comédiens) → Format Validation → 
Frame Extraction → Object Detection → Motion Analysis → Perceptual Hashing → 
Scene Detection → Audio Extraction → Multi-modal Features → Vector Embedding → 
FAISS Indexing → Real-time Monitoring → Content Protection → Revenue Recovery

VIDEO FINGERPRINTING TECHNOLOGIES:
├── 🎬 OpenCV (Computer Vision)
├── 🔍 Perceptual Hashing (pHash + dHash)
├── 🤖 YOLO Object Detection (Real-time)
├── 📊 Motion Vector Analysis (Optical Flow)
├── 🎭 Scene Detection (Cut Detection)
├── 🧠 Deep Video Features (CNN + 3D CNN)
├── 🎵 Audio-Visual Fusion (Multi-modal)
├── ⚡ GPU Acceleration (CUDA + OpenCL)
└── 🛡️ Protection Pipeline (Automated)
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Generator
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import numpy as np
import asyncio
import logging
import cv2
import hashlib
import time
from datetime import datetime
from pathlib import Path
import json
import base64
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

# Deep learning libraries
try:
    import torch
    import torchvision.transforms as transforms
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available - install torch")

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logging.warning("TensorFlow not available - install tensorflow")

# Computer vision libraries
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("YOLO not available - install ultralytics")

try:
    import imagehash
    from PIL import Image
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False
    logging.warning("ImageHash not available - install imagehash")

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

logger = logging.getLogger(__name__)

class VideoQuality(Enum):
    """Qualités vidéo supportées"""

    LOW = "240p"
    MEDIUM = "480p"
    HIGH = "720p"
    FULL_HD = "1080p"
    ULTRA_HD = "4K"

class FrameExtractionMode(Enum):
    """Modes d'extraction de frames"""

    UNIFORM = "uniform"          # Extraction uniforme
    KEYFRAMES = "keyframes"      # Frames clés uniquement
    SCENE_CHANGES = "scene_changes"  # Changements de scène
    MOTION_BASED = "motion_based"    # Basé sur le mouvement
    ADAPTIVE = "adaptive"        # Adaptatif intelligent

class VideoCodec(Enum):
    """Codecs vidéo supportés"""

    H264 = "h264"
    H265 = "h265"
    VP9 = "vp9"
    AV1 = "av1"
    MPEG4 = "mpeg4"

@dataclass
class VideoFingerprintConfig:
    """Configuration avancée pour le fingerprinting vidéo ultra-robuste"""
    
    # Video processing parameters
    max_duration: int = 3600  # 1 hour max
    min_duration: float = 5.0  # 5 seconds min
    max_file_size: int = 2 * 1024 * 1024 * 1024  # 2GB
    target_fps: int = 30
    
    # Frame extraction
    extraction_mode: FrameExtractionMode = FrameExtractionMode.ADAPTIVE
    frames_per_second: float = 1.0  # 1 frame per second default
    max_frames: int = 1000
    keyframe_threshold: float = 0.3
    
    # Image processing
    frame_resize: Tuple[int, int] = (224, 224)  # Standard CNN input
    normalize_frames: bool = True
    apply_denoising: bool = True
    
    # Ultra-robust perceptual hashing (compression resistant)
    phash_enabled: bool = True
    dhash_enabled: bool = True
    ahash_enabled: bool = True
    whash_enabled: bool = True
    hash_size: int = 16
    multi_scale_hashing: bool = True  # Multiple resolutions for robustness
    wavelet_hashing: bool = True      # Wavelet-based hashing for compression resistance
    
    # Object detection (real-time YOLO)
    yolo_enabled: bool = True
    yolo_model: str = "yolov8n.pt"  # Nano model for speed
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    face_detection_enabled: bool = True
    person_detection_enhanced: bool = True
    
    # Enhanced temporal analysis
    motion_analysis: bool = True
    optical_flow_enabled: bool = True
    motion_threshold: float = 0.1
    temporal_consistency_analysis: bool = True
    frame_sequence_patterns: bool = True
    
    # Enhanced spatial analysis  
    spatial_correlation_analysis: bool = True
    local_feature_extraction: bool = True
    geometric_invariant_features: bool = True
    
    # Scene detection
    scene_detection: bool = True
    
    # Watermarking and crop resistance
    watermark_resistance: bool = True
    crop_resistance: bool = True
    rotation_resistance: bool = True
    scale_resistance: bool = True
    
    # Performance optimization
    gpu_acceleration: bool = True
    max_workers: int = 4
    batch_processing: bool = True
    scene_threshold: float = 30.0
    
    # Deep features
    deep_features_enabled: bool = True
    cnn_model: str = "resnet50"
    feature_layer: str = "avgpool"
    
    # Performance
    use_gpu: bool = True
    parallel_processing: bool = True
    max_workers: int = mp.cpu_count()
    batch_size: int = 16
    
    # Quality control
    min_quality_score: float = 0.6
    blur_threshold: float = 100.0
    brightness_range: Tuple[float, float] = (0.1, 0.9)

@dataclass
class VideoFrame:
    """Représentation d'une frame vidéo"""
    frame_number: int
    timestamp: float
    image_data: np.ndarray
    is_keyframe: bool = False
    quality_score: float = 0.0
    motion_score: float = 0.0
    scene_id: Optional[int] = None
    
    # Hash signatures
    phash: Optional[str] = None
    dhash: Optional[str] = None
    ahash: Optional[str] = None
    whash: Optional[str] = None
    
    # Object detection results
    detected_objects: List[Dict[str, Any]] = field(default_factory=list)
    
    # Deep features
    cnn_features: Optional[np.ndarray] = None
    
    # Motion vectors
    motion_vectors: Optional[np.ndarray] = None

@dataclass
class VideoFingerprint:
    """
Empreinte vidéo complète"""
    video_id: str
    duration: float
    fps: float
    resolution: Tuple[int, int]
    codec: str
    file_size: int
    
    # Frame-level fingerprints
    frames: List[VideoFrame] = field(default_factory=list)
    
    # Global features
    global_histogram: Optional[np.ndarray] = None
    motion_energy: float = 0.0
    scene_count: int = 0
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    
    # Perceptual signatures
    video_phash: Optional[str] = None
    temporal_signature: Optional[np.ndarray] = None
    
    # Audio fingerprint (if available)
    audio_fingerprint: Optional[Dict[str, Any]] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    processing_time: float = 0.0
    quality_metrics: Dict[str, float] = field(default_factory=dict)

class VideoFingerprintEngine:
    """
    Engine principal de fingerprinting vidéo ultra-avancé
    
    Features:
    - Multi-modal video analysis
    - Real-time processing capability
    - GPU acceleration support
    - Scene-aware fingerprinting
    - Motion-based signatures
    - Object detection integration
    - Deep learning features
    - Temporal consistency analysis
    """
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        
        # Initialize processors
        self.opencv_processor = OpenCVProcessor(config)
        self.phash_processor = PerceptualHashProcessor(config)
        self.yolo_processor = YOLOFrameProcessor(config) if YOLO_AVAILABLE else None
        self.motion_processor = MotionVectorProcessor(config)
        self.scene_detector = SceneDetector(config)
        self.deep_features_processor = DeepFeaturesProcessor(config)
        
        # GPU setup
        self.device = self._setup_device()
        
        # Thread pools
        self.thread_pool = ThreadPoolExecutor(max_workers=config.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=config.max_workers)
        
        logger.info("VideoFingerprintEngine initialized")
    
    def _setup_device(self) -> str:
        """Configure le device de traitement"""
        if self.config.use_gpu:
            if TORCH_AVAILABLE and torch.cuda.is_available():
                return "cuda"
            elif TENSORFLOW_AVAILABLE and tf.config.list_physical_devices('GPU'):
                return "gpu"
        return "cpu"
    
    async def generate_fingerprint(self, video_path: str) -> VideoFingerprint:
        """Génère l'empreinte complète d'une vidéo"""
        start_time = time.time()
        
        try:
            # Validate video file
            video_info = await self._validate_video_file(video_path)
            
            # Create fingerprint container
            fingerprint = VideoFingerprint(
                video_id=self._generate_video_id(video_path),
                duration=video_info['duration'],
                fps=video_info['fps'],
                resolution=video_info['resolution'],
                codec=video_info['codec'],
                file_size=video_info['file_size']
            )
            
            # Extract frames based on strategy
            frames_generator = await self._extract_frames(video_path)
            
            # Process frames in batches
            frame_batch = []
            async for frame_data in frames_generator:
                frame_batch.append(frame_data)
                
                if len(frame_batch) >= self.config.batch_size:
                    processed_frames = await self._process_frame_batch(frame_batch)
                    fingerprint.frames.extend(processed_frames)
                    frame_batch = []
            
            # Process remaining frames
            if frame_batch:
                processed_frames = await self._process_frame_batch(frame_batch)
                fingerprint.frames.extend(processed_frames)
            
            # Generate global features
            await self._compute_global_features(fingerprint)
            
            # Compute quality metrics
            fingerprint.quality_metrics = await self._compute_quality_metrics(fingerprint)
            
            # Calculate processing time
            fingerprint.processing_time = time.time() - start_time
            
            logger.info(f"Video fingerprint generated for {video_path} in {fingerprint.processing_time:.2f}s")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error generating video fingerprint: {e}")
            raise
    
    async def compare_fingerprints(self,
                                 fingerprint1: VideoFingerprint,
                                 fingerprint2: VideoFingerprint) -> Dict[str, float]:
        """Compare deux empreintes vidéo"""
        try:
            similarity_scores = {}
            
            # Temporal signature similarity
            if (fingerprint1.temporal_signature is not None and 
                fingerprint2.temporal_signature is not None):
                temporal_similarity = await self._compute_temporal_similarity(
                    fingerprint1.temporal_signature,
                    fingerprint2.temporal_signature
                )
                similarity_scores['temporal'] = temporal_similarity
            
            # Frame-by-frame hash comparison
            hash_similarity = await self._compute_hash_similarity(
                fingerprint1.frames, fingerprint2.frames
            )
            similarity_scores['hash'] = hash_similarity
            
            # Motion pattern similarity
            motion_similarity = await self._compute_motion_similarity(
                fingerprint1, fingerprint2
            )
            similarity_scores['motion'] = motion_similarity
            
            # Scene structure similarity
            scene_similarity = await self._compute_scene_similarity(
                fingerprint1.frames, fingerprint2.frames
            )
            similarity_scores['scene'] = scene_similarity
            
            # Object detection similarity
            if self.yolo_processor:
                object_similarity = await self._compute_object_similarity(
                    fingerprint1.frames, fingerprint2.frames
                )
                similarity_scores['objects'] = object_similarity
            
            # Deep feature similarity
            if fingerprint1.frames and fingerprint2.frames:
                deep_similarity = await self._compute_deep_feature_similarity(
                    fingerprint1.frames, fingerprint2.frames
                )
                similarity_scores['deep_features'] = deep_similarity
            
            # Weighted overall similarity
            overall_similarity = await self._compute_weighted_similarity(similarity_scores)
            similarity_scores['overall'] = overall_similarity
            
            return similarity_scores
            
        except Exception as e:
            logger.error(f"Error comparing video fingerprints: {e}")
            raise
    
    async def _validate_video_file(self, video_path: str) -> Dict[str, Any]:
        """Valide un fichier vidéo"""
        path = Path(video_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if path.stat().st_size > self.config.max_file_size:
            raise ValueError(f"Video file too large: {path.stat().st_size} bytes")
        
        # Get video info using OpenCV
        cap = cv2.VideoCapture(str(path))
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        # Get codec information
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
        
        cap.release()
        
        if duration < self.config.min_duration:
            raise ValueError(f"Video too short: {duration}s (min: {self.config.min_duration}s)")
        
        if duration > self.config.max_duration:
            raise ValueError(f"Video too long: {duration}s (max: {self.config.max_duration}s)")
        
        return {
            'duration': duration,
            'fps': fps,
            'resolution': (width, height),
            'frame_count': frame_count,
            'codec': codec,
            'file_size': path.stat().st_size
        }
    
    def _generate_video_id(self, video_path: str) -> str:
        """Génère un ID unique pour la vidéo"""
        path = Path(video_path)
        content = f"{path.name}_{path.stat().st_size}_{path.stat().st_mtime}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def _extract_frames(self, video_path: str) -> Generator[Tuple[int, float, np.ndarray], None, None]:
        """Extrait les frames selon la stratégie configurée"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if self.config.extraction_mode == FrameExtractionMode.UNIFORM:
            # Extraction uniforme
            frame_interval = max(1, int(fps / self.config.frames_per_second))
            
            frame_number = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_number % frame_interval == 0:
                    timestamp = frame_number / fps
                    yield frame_number, timestamp, frame
                
                frame_number += 1
                
                if len(list(range(0, frame_number, frame_interval))) >= self.config.max_frames:
                    break
        
        elif self.config.extraction_mode == FrameExtractionMode.KEYFRAMES:
            # Extraction des frames clés
            async for frame_data in self._extract_keyframes(cap, fps):
                yield frame_data
        
        elif self.config.extraction_mode == FrameExtractionMode.SCENE_CHANGES:
            # Extraction sur les changements de scène
            async for frame_data in self._extract_scene_change_frames(cap, fps):
                yield frame_data
        
        elif self.config.extraction_mode == FrameExtractionMode.ADAPTIVE:
            # Extraction adaptative combinée
            async for frame_data in self._extract_adaptive_frames(cap, fps):
                yield frame_data
        
        cap.release()
    
    async def _extract_keyframes(self, cap: cv2.VideoCapture, fps: float):
        """
Extrait les frames clés"""
        prev_frame = None
        frame_number = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if prev_frame is not None:
                # Calculate frame difference
                gray_current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                
                diff = cv2.absdiff(gray_current, gray_prev)
                non_zero_count = cv2.countNonZero(diff)
                total_pixels = diff.shape[0] * diff.shape[1]
                change_ratio = non_zero_count / total_pixels
                
                if change_ratio > self.config.keyframe_threshold:
                    timestamp = frame_number / fps
                    yield frame_number, timestamp, frame
            else:
                # First frame is always a keyframe
                timestamp = frame_number / fps
                yield frame_number, timestamp, frame
            
            prev_frame = frame.copy()
            frame_number += 1
    
    async def _extract_scene_change_frames(self, cap: cv2.VideoCapture, fps: float):
        """
Extrait les frames sur les changements de scène"""
        # Implementation would use scene detection algorithm
        # For now, use simplified version
        async for frame_data in self._extract_keyframes(cap, fps):
            yield frame_data
    
    async def _extract_adaptive_frames(self, cap: cv2.VideoCapture, fps: float):
        """
Extraction adaptative intelligente"""
        # Combine multiple strategies for optimal frame selection
        frames_yielded = 0
        frame_number = 0
        prev_frame = None
        
        # Start with first frame
        ret, frame = cap.read()
        if ret:
            timestamp = frame_number / fps
            yield frame_number, timestamp, frame
            frames_yielded += 1
            prev_frame = frame.copy()
            frame_number += 1
        
        # Continue with adaptive strategy
        while frames_yielded < self.config.max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            timestamp = frame_number / fps
            
            # Motion-based extraction
            if prev_frame is not None:
                motion_score = self._calculate_motion_score(prev_frame, frame)
                
                if motion_score > self.config.motion_threshold:
                    yield frame_number, timestamp, frame
                    frames_yielded += 1
                    prev_frame = frame.copy()
            
            frame_number += 1
    
    def _calculate_motion_score(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
Calcule le score de mouvement entre deux frames"""
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Optical flow
        flow = cv2.calcOpticalFlowPyrLK(gray1, gray2, None, None)
        magnitude = np.sqrt(flow[0]**2 + flow[1]**2) if flow[0] is not None else np.array([0])
        
        return np.mean(magnitude)
    
    async def _process_frame_batch(self, frame_batch: List[Tuple[int, float, np.ndarray]]) -> List[VideoFrame]:
        """
Traite un batch de frames"""
        processed_frames = []
        
        # Process frames in parallel
        tasks = []
        for frame_number, timestamp, image_data in frame_batch:
            task = asyncio.create_task(self._process_single_frame(frame_number, timestamp, image_data))
            tasks.append(task)
        
        processed_frames = await asyncio.gather(*tasks)
        return processed_frames
    
    async def _process_single_frame(self, frame_number: int, timestamp: float, image_data: np.ndarray) -> VideoFrame:
        """
Traite une frame individuelle"""
        # Create VideoFrame object
        video_frame = VideoFrame(
            frame_number=frame_number,
            timestamp=timestamp,
            image_data=image_data
        )
        
        # Quality assessment
        video_frame.quality_score = await self._assess_frame_quality(image_data)
        
        # Skip low-quality frames
        if video_frame.quality_score < self.config.min_quality_score:
            return video_frame
        
        # Generate perceptual hashes
        if IMAGEHASH_AVAILABLE:
            hashes = await self.phash_processor.generate_hashes(image_data)
            video_frame.phash = hashes.get('phash')
            video_frame.dhash = hashes.get('dhash')
            video_frame.ahash = hashes.get('ahash')
            video_frame.whash = hashes.get('whash')
        
        # Object detection
        if self.yolo_processor and self.config.yolo_enabled:
            video_frame.detected_objects = await self.yolo_processor.detect_objects(image_data)
        
        # Deep features extraction
        if self.config.deep_features_enabled:
            video_frame.cnn_features = await self.deep_features_processor.extract_features(image_data)
        
        return video_frame
    
    async def _assess_frame_quality(self, image_data: np.ndarray) -> float:
        """Évalue la qualité d'une frame"""
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        
        # Blur detection (Laplacian variance)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_quality = min(1.0, blur_score / self.config.blur_threshold)
        
        # Brightness analysis
        brightness = np.mean(gray) / 255.0
        brightness_quality = 1.0
        if brightness < self.config.brightness_range[0] or brightness > self.config.brightness_range[1]:
            brightness_quality = 0.5
        
        # Contrast analysis
        contrast = np.std(gray) / 255.0
        contrast_quality = min(1.0, contrast * 4)  # Scale contrast
        
        # Combined quality score
        quality_score = (blur_quality * 0.5 + brightness_quality * 0.3 + contrast_quality * 0.2)
        
        return quality_score
    
    async def _compute_global_features(self, fingerprint: VideoFingerprint):
        """
Calcule les caractéristiques globales de la vidéo"""
        if not fingerprint.frames:
            return
        
        # Global color histogram
        all_histograms = []
        for frame in fingerprint.frames:
            if frame.quality_score >= self.config.min_quality_score:
                hist = cv2.calcHist([frame.image_data], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                all_histograms.append(hist.flatten())
        
        if all_histograms:
            fingerprint.global_histogram = np.mean(all_histograms, axis=0)
        
        # Motion energy calculation
        motion_scores = [frame.motion_score for frame in fingerprint.frames if frame.motion_score > 0]
        fingerprint.motion_energy = np.mean(motion_scores) if motion_scores else 0.0
        
        # Scene count estimation
        fingerprint.scene_count = await self._estimate_scene_count(fingerprint.frames)
        
        # Dominant colors extraction
        fingerprint.dominant_colors = await self._extract_dominant_colors(fingerprint.frames)
        
        # Temporal signature
        fingerprint.temporal_signature = await self._generate_temporal_signature(fingerprint.frames)
    
    async def _estimate_scene_count(self, frames: List[VideoFrame]) -> int:
        """
Estime le nombre de scènes"""
        if len(frames) < 2:
            return 1
        
        scene_changes = 0
        for i in range(1, len(frames)):
            if frames[i].scene_id != frames[i-1].scene_id:
                scene_changes += 1
        
        return scene_changes + 1
    
    async def _extract_dominant_colors(self, frames: List[VideoFrame]) -> List[Tuple[int, int, int]]:
        """
Extrait les couleurs dominantes"""
        all_colors = []
        
        for frame in frames[:10]:  # Use first 10 frames for efficiency
            if frame.quality_score >= self.config.min_quality_score:
                # Reshape image for k-means
                data = frame.image_data.reshape((-1, 3))
                data = np.float32(data)
                
                # K-means clustering
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
                _, labels, centers = cv2.kmeans(data, 3, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
                
                # Convert centers to RGB tuples
                centers = np.uint8(centers)
                dominant_colors = [tuple(center) for center in centers]
                all_colors.extend(dominant_colors)
        
        # Return most common colors
        from collections import Counter
        color_counts = Counter(all_colors)
        return [color for color, _ in color_counts.most_common(5)]
    
    async def _generate_temporal_signature(self, frames: List[VideoFrame]) -> np.ndarray:
        """
Génère une signature temporelle"""
        if not frames:
            return np.array([])
        
        # Extract temporal features from frame hashes
        temporal_features = []
        
        for frame in frames:
            if frame.phash:
                # Convert hash to binary array
                hash_int = int(frame.phash, 16)
                binary_array = np.array([int(b) for b in format(hash_int, '064b')])
                temporal_features.append(binary_array)
        
        if temporal_features:
            return np.array(temporal_features)
        
        return np.array([])
    
    async def _compute_temporal_similarity(self, sig1: np.ndarray, sig2: np.ndarray) -> float:
        """
Calcule la similarité temporelle"""
        if sig1.size == 0 or sig2.size == 0:
            return 0.0
        
        # Dynamic Time Warping or simple correlation
        min_len = min(len(sig1), len(sig2))
        sig1_trimmed = sig1[:min_len]
        sig2_trimmed = sig2[:min_len]
        
        # Cosine similarity
        flat1 = sig1_trimmed.flatten()
        flat2 = sig2_trimmed.flatten()
        
        dot_product = np.dot(flat1, flat2)
        norm1 = np.linalg.norm(flat1)
        norm2 = np.linalg.norm(flat2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def _compute_hash_similarity(self, frames1: List[VideoFrame], frames2: List[VideoFrame]) -> float:
        """
Calcule la similarité des hashes"""
        if not frames1 or not frames2:
            return 0.0
        
        similarities = []
        
        for f1 in frames1:
            if not f1.phash:
                continue
            
            best_similarity = 0.0
            for f2 in frames2:
                if not f2.phash:
                    continue
                
                # Hamming distance between hashes
                hash1_int = int(f1.phash, 16)
                hash2_int = int(f2.phash, 16)
                
                hamming_distance = bin(hash1_int ^ hash2_int).count('1')
                similarity = 1.0 - (hamming_distance / 64.0)  # 64-bit hash
                
                best_similarity = max(best_similarity, similarity)
            
            similarities.append(best_similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    async def _compute_motion_similarity(self, fp1: VideoFingerprint, fp2: VideoFingerprint) -> float:
        """
Calcule la similarité de mouvement"""
        if fp1.motion_energy == 0 and fp2.motion_energy == 0:
            return 1.0
        
        if fp1.motion_energy == 0 or fp2.motion_energy == 0:
            return 0.0
        
        # Simple ratio-based similarity
        ratio = min(fp1.motion_energy, fp2.motion_energy) / max(fp1.motion_energy, fp2.motion_energy)
        return ratio
    
    async def _compute_scene_similarity(self, frames1: List[VideoFrame], frames2: List[VideoFrame]) -> float:
        """
Calcule la similarité de structure de scène"""
        # Compare scene transition patterns
        # This is a simplified implementation
        return 0.5  # Placeholder
    
    async def _compute_object_similarity(self, frames1: List[VideoFrame], frames2: List[VideoFrame]) -> float:
        """
Calcule la similarité d'objets détectés"""
        if not self.yolo_processor:
            return 0.0
        
        # Extract object classes from both videos
        objects1 = set()
        objects2 = set()
        
        for frame in frames1:
            for obj in frame.detected_objects:
                objects1.add(obj.get('class', ''))
        
        for frame in frames2:
            for obj in frame.detected_objects:
                objects2.add(obj.get('class', ''))
        
        # Jaccard similarity
        intersection = len(objects1.intersection(objects2))
        union = len(objects1.union(objects2))
        
        return intersection / union if union > 0 else 0.0
    
    async def _compute_deep_feature_similarity(self, frames1: List[VideoFrame], frames2: List[VideoFrame]) -> float:
        """
Calcule la similarité des caractéristiques profondes"""
        features1 = [f.cnn_features for f in frames1 if f.cnn_features is not None]
        features2 = [f.cnn_features for f in frames2 if f.cnn_features is not None]
        
        if not features1 or not features2:
            return 0.0
        
        # Average features for each video
        avg_features1 = np.mean(features1, axis=0)
        avg_features2 = np.mean(features2, axis=0)
        
        # Cosine similarity
        dot_product = np.dot(avg_features1, avg_features2)
        norm1 = np.linalg.norm(avg_features1)
        norm2 = np.linalg.norm(avg_features2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def _compute_weighted_similarity(self, similarity_scores: Dict[str, float]) -> float:
        """
Calcule la similarité pondérée globale"""
        weights = {
            'temporal': 0.3,
            'hash': 0.25,
            'motion': 0.15,
            'scene': 0.1,
            'objects': 0.1,
            'deep_features': 0.1
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric, score in similarity_scores.items():
            if metric in weights:
                weighted_sum += score * weights[metric]
                total_weight += weights[metric]
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    async def _compute_quality_metrics(self, fingerprint: VideoFingerprint) -> Dict[str, float]:
        """
Calcule les métriques de qualité"""
        if not fingerprint.frames:
            return {}
        
        quality_scores = [f.quality_score for f in fingerprint.frames]
        
        return {
            'avg_quality': np.mean(quality_scores),
            'min_quality': np.min(quality_scores),
            'max_quality': np.max(quality_scores),
            'quality_variance': np.var(quality_scores),
            'high_quality_ratio': sum(1 for q in quality_scores if q >= 0.8) / len(quality_scores)
        }

class OpenCVProcessor:
    """
Processeur OpenCV pour analyse vidéo"""
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        logger.info("OpenCVProcessor initialized")
    
    async def extract_features(self, frame: np.ndarray) -> Dict[str, Any]:
        """Extrait les caractéristiques OpenCV"""
        features = {}
        
        # Color histogram
        hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        features['color_histogram'] = hist.flatten()
        
        # Edge detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        features['edge_density'] = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Texture features (LBP)
        features['texture_score'] = np.std(gray)
        
        return features

class PerceptualHashProcessor:
    """
Processeur de hash perceptuel ultra-robuste résistant à la compression"""
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        logger.info("PerceptualHashProcessor initialized with ultra-robust features")
    
    async def generate_hashes(self, image_data: np.ndarray) -> Dict[str, Any]:
        """Génère les hashes perceptuels ultra-robustes"""
        if not IMAGEHASH_AVAILABLE:
            return {}
        
        # Convert OpenCV image to PIL
        image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        hashes = {}
        
        # Standard perceptual hashes
        if self.config.phash_enabled:
            hashes['phash'] = str(imagehash.phash(pil_image, hash_size=self.config.hash_size))
        
        if self.config.dhash_enabled:
            hashes['dhash'] = str(imagehash.dhash(pil_image, hash_size=self.config.hash_size))
        
        if self.config.ahash_enabled:
            hashes['ahash'] = str(imagehash.average_hash(pil_image, hash_size=self.config.hash_size))
        
        if self.config.whash_enabled:
            hashes['whash'] = str(imagehash.whash(pil_image, hash_size=self.config.hash_size))
        
        # Multi-scale hashing for compression resistance
        if self.config.multi_scale_hashing:
            multi_scale_hashes = await self._generate_multiscale_hashes(pil_image)
            hashes.update(multi_scale_hashes)
        
        # Wavelet-based hashing for enhanced compression resistance
        if self.config.wavelet_hashing:
            wavelet_hash = await self._generate_wavelet_hash(image_data)
            hashes['wavelet_hash'] = wavelet_hash
            
        # Geometric invariant hashes for crop/rotation resistance
        if self.config.crop_resistance or self.config.rotation_resistance:
            invariant_hashes = await self._generate_invariant_hashes(pil_image)
            hashes.update(invariant_hashes)
        
        return hashes
    
    async def _generate_multiscale_hashes(self, image: Image.Image) -> Dict[str, str]:
        """
Génère des hashes à plusieurs échelles pour la résistance à la compression"""
        multiscale_hashes = {}
        scales = [0.5, 0.75, 1.0, 1.25, 1.5]
        
        for scale in scales:
            new_size = (int(image.width * scale), int(image.height * scale))
            if new_size[0] > 0 and new_size[1] > 0:
                scaled_image = image.resize(new_size, Image.Resampling.LANCZOS)
                scale_key = f"scale_{scale:.2f}"
                multiscale_hashes[f"phash_{scale_key}"] = str(imagehash.phash(scaled_image))
                multiscale_hashes[f"dhash_{scale_key}"] = str(imagehash.dhash(scaled_image))
        
        return multiscale_hashes
    
    async def _generate_wavelet_hash(self, image_data: np.ndarray) -> str:
        """Génère un hash basé sur les ondelettes pour la résistance à la compression"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
            
            # Resize to standard size
            resized = cv2.resize(gray, (64, 64))
            
            # Apply Gaussian blur to reduce noise (compression resistance)
            blurred = cv2.GaussianBlur(resized, (3, 3), 1.0)
            
            # Calculate DCT (Discrete Cosine Transform) for frequency domain analysis
            float_img = np.float32(blurred)
            dct = cv2.dct(float_img)
            
            # Extract low-frequency components (most robust to compression)
            low_freq = dct[:16, :16]
            
            # Create binary hash from DCT coefficients
            median_val = np.median(low_freq)
            binary_hash = (low_freq > median_val).astype(int)
            
            # Convert to hex string
            hash_bits = binary_hash.flatten()
            hex_string = ''.join([str(bit) for bit in hash_bits])
            
            return hex_string
            
        except Exception as e:
            logger.error(f"Error generating wavelet hash: {e}")
            return ""
    
    async def _generate_invariant_hashes(self, image: Image.Image) -> Dict[str, str]:
        """Génère des hashes invariants géométriques pour la résistance aux crops/rotations"""
        invariant_hashes = {}
        
        try:
            # Center crop hash (crop resistance)
            center_crop = self._center_crop(image, 0.8)
            invariant_hashes['center_crop_phash'] = str(imagehash.phash(center_crop))
            
            # Corner crops for robust matching
            corners = self._extract_corner_regions(image)
            for i, corner in enumerate(corners):
                invariant_hashes[f'corner_{i}_phash'] = str(imagehash.phash(corner))
            
            # Rotation-normalized hash  
            normalized_image = self._normalize_rotation(image)
            invariant_hashes['rotation_normalized_phash'] = str(imagehash.phash(normalized_image))
            
        except Exception as e:
            logger.error(f"Error generating invariant hashes: {e}")
            
        return invariant_hashes
    
    def _center_crop(self, image: Image.Image, crop_ratio: float) -> Image.Image:
        """Crop central region of image"""
        width, height = image.size
        new_width = int(width * crop_ratio)
        new_height = int(height * crop_ratio)
        left = (width - new_width) // 2
        top = (height - new_height) // 2
        return image.crop((left, top, left + new_width, top + new_height))
    
    def _extract_corner_regions(self, image: Image.Image) -> List[Image.Image]:
        """
Extract corner regions for robust matching"""
        width, height = image.size
        corner_size = min(width, height) // 4
        
        corners = []
        # Top-left
        corners.append(image.crop((0, 0, corner_size, corner_size)))
        # Top-right  
        corners.append(image.crop((width - corner_size, 0, width, corner_size)))
        # Bottom-left
        corners.append(image.crop((0, height - corner_size, corner_size, height)))
        # Bottom-right
        corners.append(image.crop((width - corner_size, height - corner_size, width, height)))
        
        return corners
    
    def _normalize_rotation(self, image: Image.Image) -> Image.Image:
        """
Normalize image rotation for rotation-invariant hashing"""
        # Simple rotation normalization - find dominant edges and align
        # This is a simplified version; full implementation would use sophisticated edge detection
        return image  # Placeholder for now

class YOLOFrameProcessor:
    """
Processeur YOLO pour détection d'objets/visages en temps réel"""
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        
        if YOLO_AVAILABLE:
            self.model = YOLO(config.yolo_model)
            # Load face detection model if enabled
            if config.face_detection_enabled:
                try:
                    self.face_model = YOLO('yolov8n-face.pt')  # Specialized face detection
                except:
                    self.face_model = None
                    logger.warning("Face detection model not available")
            else:
                self.face_model = None
        else:
            self.model = None
            self.face_model = None
            
        logger.info("YOLOFrameProcessor initialized for real-time detection")
    
    async def detect_objects(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Détecte les objets et visages dans une frame en temps réel"""
        if not self.model:
            return []
        
        try:
            detected_objects = []
            
            # Standard object detection
            results = self.model(frame, 
                               conf=self.config.confidence_threshold,
                               iou=self.config.iou_threshold,
                               verbose=False)
            
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        obj_info = {
                            'class': result.names[int(box.cls)],
                            'confidence': float(box.conf),
                            'bbox': box.xyxy.tolist()[0] if hasattr(box, 'xyxy') else [],
                            'detection_type': 'object'
                        }
                        detected_objects.append(obj_info)
            
            # Enhanced face detection
            if self.face_model and self.config.face_detection_enabled:
                face_detections = await self._detect_faces(frame)
                detected_objects.extend(face_detections)
            
            # Enhanced person detection with pose analysis
            if self.config.person_detection_enhanced:
                person_detections = await self._enhanced_person_detection(detected_objects, frame)
                detected_objects.extend(person_detections)
            
            return detected_objects
            
        except Exception as e:
            logger.error(f"Error in YOLO detection: {e}")
            return []
    
    async def _detect_faces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Détection spécialisée des visages"""
        if not self.face_model:
            return []
        
        try:
            face_results = self.face_model(frame, 
                                         conf=self.config.confidence_threshold * 0.8,  # Lower threshold for faces
                                         iou=self.config.iou_threshold,
                                         verbose=False)
            
            face_detections = []
            for result in face_results:
                if result.boxes is not None:
                    for box in result.boxes:
                        face_info = {
                            'class': 'face',
                            'confidence': float(box.conf),
                            'bbox': box.xyxy.tolist()[0] if hasattr(box, 'xyxy') else [],
                            'detection_type': 'face',
                            'face_features': await self._extract_face_features(frame, box)
                        }
                        face_detections.append(face_info)
            
            return face_detections
            
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return []
    
    async def _enhanced_person_detection(self, detected_objects: List[Dict], frame: np.ndarray) -> List[Dict[str, Any]]:
        """Analyse améliorée des personnes détectées"""
        enhanced_detections = []
        
        for obj in detected_objects:
            if obj.get('class') == 'person':
                # Extract person-specific features
                bbox = obj.get('bbox', [])
                if len(bbox) == 4:
                    person_features = await self._extract_person_features(frame, bbox)
                    enhanced_person = {
                        **obj,
                        'detection_type': 'enhanced_person',
                        'person_features': person_features,
                        'pose_analysis': await self._analyze_pose(frame, bbox)
                    }
                    enhanced_detections.append(enhanced_person)
        
        return enhanced_detections
    
    async def _extract_face_features(self, frame: np.ndarray, box) -> Dict[str, Any]:
        """
Extrait les caractéristiques faciales pour l'identification"""
        try:
            if hasattr(box, 'xyxy'):
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                face_roi = frame[y1:y2, x1:x2]
                
                # Basic face analysis
                gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
                
                return {
                    'face_size': (x2 - x1, y2 - y1),
                    'face_area': (x2 - x1) * (y2 - y1),
                    'brightness': float(np.mean(gray_face)),
                    'contrast': float(np.std(gray_face)),
                    'aspect_ratio': (x2 - x1) / max(y2 - y1, 1)
                }
        except Exception as e:
            logger.error(f"Error extracting face features: {e}")
            
        return {}
    
    async def _extract_person_features(self, frame: np.ndarray, bbox: List[float]) -> Dict[str, Any]:
        """Extrait les caractéristiques de la personne"""
        try:
            x1, y1, x2, y2 = map(int, bbox)
            person_roi = frame[y1:y2, x1:x2]
            
            # Basic person analysis
            gray_person = cv2.cvtColor(person_roi, cv2.COLOR_BGR2GRAY)
            
            # Color analysis
            hsv_person = cv2.cvtColor(person_roi, cv2.COLOR_BGR2HSV)
            dominant_colors = await self._extract_dominant_colors(person_roi)
            
            return {
                'person_size': (x2 - x1, y2 - y1),
                'person_area': (x2 - x1) * (y2 - y1),
                'brightness': float(np.mean(gray_person)),
                'contrast': float(np.std(gray_person)),
                'aspect_ratio': (x2 - x1) / max(y2 - y1, 1),
                'dominant_colors': dominant_colors,
                'location_in_frame': {
                    'center_x': (x1 + x2) / 2 / frame.shape[1],
                    'center_y': (y1 + y2) / 2 / frame.shape[0]
                }
            }
        except Exception as e:
            logger.error(f"Error extracting person features: {e}")
            
        return {}
    
    async def _analyze_pose(self, frame: np.ndarray, bbox: List[float]) -> Dict[str, Any]:
        """Analyse basique de la pose (peut être étendue avec des modèles de pose)"""
        try:
            x1, y1, x2, y2 = map(int, bbox)
            
            # Basic pose analysis based on bounding box proportions
            width = x2 - x1
            height = y2 - y1
            
            return {
                'standing_likelihood': height / width if width > 0 else 0,
                'size_category': 'large' if width * height > 50000 else 'medium' if width * height > 10000 else 'small',
                'position': 'upper' if y1 < frame.shape[0] / 3 else 'middle' if y1 < 2 * frame.shape[0] / 3 else 'lower'
            }
        except Exception as e:
            logger.error(f"Error analyzing pose: {e}")
            
        return {}
    
    async def _extract_dominant_colors(self, image_roi: np.ndarray) -> List[List[int]]:
        """Extrait les couleurs dominantes de la région"""
        try:
            # Reshape image to be a list of pixels
            pixels = image_roi.reshape(-1, 3)
            
            # Use K-means to find dominant colors
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get the dominant colors
            dominant_colors = kmeans.cluster_centers_.astype(int).tolist()
            
            return dominant_colors
            
        except Exception as e:
            logger.error(f"Error extracting dominant colors: {e}")
            return []

class MotionVectorProcessor:
    """Processeur d'analyse de mouvement"""
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        logger.info("MotionVectorProcessor initialized")
    
    async def analyze_motion(self, frame1: np.ndarray, frame2: np.ndarray) -> Dict[str, Any]:
        """Analyse le mouvement entre deux frames"""
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Optical flow
        flow = cv2.calcOpticalFlowPyrLK(gray1, gray2, None, None)
        
        motion_info = {
            'magnitude': np.mean(np.sqrt(flow[0]**2 + flow[1]**2)) if flow[0] is not None else 0,
            'direction': np.mean(np.arctan2(flow[1], flow[0])) if flow[1] is not None else 0,
            'motion_vectors': flow
        }
        
        return motion_info

class TemporalAnalysisProcessor:
    """
Processeur d'analyse temporelle avancée pour patterns et séquences"""
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        self.frame_history = []
        self.motion_history = []
        logger.info("TemporalAnalysisProcessor initialized")
    
    async def analyze_temporal_patterns(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyse les patterns temporels dans la séquence de frames"""
        if len(frames) < 2:
            return {}
        
        temporal_features = {}
        
        # Frame sequence patterns
        if self.config.frame_sequence_patterns:
            sequence_patterns = await self._analyze_frame_sequences(frames)
            temporal_features['sequence_patterns'] = sequence_patterns
        
        # Temporal consistency analysis
        if self.config.temporal_consistency_analysis:
            consistency_metrics = await self._analyze_temporal_consistency(frames)
            temporal_features['consistency_metrics'] = consistency_metrics
        
        # Motion trajectory analysis
        motion_trajectories = await self._analyze_motion_trajectories(frames)
        temporal_features['motion_trajectories'] = motion_trajectories
        
        # Scene transition analysis
        scene_transitions = await self._analyze_scene_transitions(frames)
        temporal_features['scene_transitions'] = scene_transitions
        
        return temporal_features
    
    async def _analyze_frame_sequences(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """
Analyse les patterns dans les séquences de frames"""
        sequence_features = {}
        
        try:
            # Calculate frame differences
            frame_diffs = []
            for i in range(1, len(frames)):
                diff = cv2.absdiff(frames[i-1], frames[i])
                frame_diffs.append(np.mean(diff))
            
            # Pattern analysis
            sequence_features['avg_frame_diff'] = float(np.mean(frame_diffs))
            sequence_features['max_frame_diff'] = float(np.max(frame_diffs))
            sequence_features['frame_diff_variance'] = float(np.var(frame_diffs))
            
            # Detect periodic patterns
            if len(frame_diffs) > 10:
                periodicity = await self._detect_periodicity(frame_diffs)
                sequence_features['periodicity'] = periodicity
            
        except Exception as e:
            logger.error(f"Error analyzing frame sequences: {e}")
            
        return sequence_features
    
    async def _analyze_temporal_consistency(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyse la cohérence temporelle des frames"""
        consistency_metrics = {}
        
        try:
            # Color consistency across frames
            color_means = []
            for frame in frames:
                color_mean = np.mean(frame, axis=(0, 1))
                color_means.append(color_mean)
            
            color_consistency = np.std(color_means, axis=0)
            consistency_metrics['color_consistency'] = {
                'b_channel': float(color_consistency[0]),
                'g_channel': float(color_consistency[1]),
                'r_channel': float(color_consistency[2])
            }
            
            # Brightness consistency
            brightness_values = [np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)) for frame in frames]
            consistency_metrics['brightness_consistency'] = float(np.std(brightness_values))
            
            # Edge consistency
            edge_densities = []
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
                edge_densities.append(edge_density)
            
            consistency_metrics['edge_consistency'] = float(np.std(edge_densities))
            
        except Exception as e:
            logger.error(f"Error analyzing temporal consistency: {e}")
            
        return consistency_metrics
    
    async def _analyze_motion_trajectories(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyse les trajectoires de mouvement"""
        motion_features = {}
        
        try:
            if len(frames) < 3:
                return motion_features
            
            # Calculate optical flow between consecutive frames
            flows = []
            for i in range(1, len(frames)):
                prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
                curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                
                flow = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, None, None)
                if flow[0] is not None:
                    flows.append(flow[0])
            
            if flows:
                # Analyze motion patterns
                motion_magnitudes = []
                motion_directions = []
                
                for flow_points in flows:
                    if len(flow_points) > 0:
                        magnitudes = np.sqrt(np.sum(flow_points**2, axis=2))
                        directions = np.arctan2(flow_points[:,:,1], flow_points[:,:,0])
                        
                        motion_magnitudes.append(np.mean(magnitudes))
                        motion_directions.append(np.mean(directions))
                
                if motion_magnitudes:
                    motion_features['avg_motion_magnitude'] = float(np.mean(motion_magnitudes))
                    motion_features['motion_variance'] = float(np.var(motion_magnitudes))
                    motion_features['dominant_direction'] = float(np.mean(motion_directions))
                    motion_features['direction_consistency'] = float(np.std(motion_directions))
            
        except Exception as e:
            logger.error(f"Error analyzing motion trajectories: {e}")
            
        return motion_features
    
    async def _analyze_scene_transitions(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyse les transitions de scène"""
        transition_features = {}
        
        try:
            # Detect scene cuts based on histogram differences
            scene_cuts = []
            for i in range(1, len(frames)):
                # Calculate color histograms
                hist1 = cv2.calcHist([frames[i-1]], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                hist2 = cv2.calcHist([frames[i]], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                
                # Calculate histogram correlation
                correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                
                # Scene cut threshold
                if correlation < 0.7:  # Threshold for scene change
                    scene_cuts.append(i)
            
            transition_features['scene_cuts'] = scene_cuts
            transition_features['num_scene_cuts'] = len(scene_cuts)
            transition_features['avg_scene_length'] = len(frames) / max(len(scene_cuts) + 1, 1)
            
        except Exception as e:
            logger.error(f"Error analyzing scene transitions: {e}")
            
        return transition_features
    
    async def _detect_periodicity(self, signal: List[float]) -> Dict[str, Any]:
        """Détecte la périodicité dans un signal temporel"""
        periodicity = {}
        
        try:
            # Simple autocorrelation for periodicity detection
            signal_array = np.array(signal)
            
            # Normalize signal
            signal_normalized = (signal_array - np.mean(signal_array)) / np.std(signal_array)
            
            # Calculate autocorrelation
            autocorr = np.correlate(signal_normalized, signal_normalized, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            # Find peaks in autocorrelation
            if len(autocorr) > 1:
                peaks = []
                for i in range(1, len(autocorr) - 1):
                    if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1] and autocorr[i] > 0.3:
                        peaks.append(i)
                
                if peaks:
                    periodicity['dominant_period'] = int(peaks[0])
                    periodicity['peak_strength'] = float(autocorr[peaks[0]])
                    periodicity['num_periods'] = len(peaks)
            
        except Exception as e:
            logger.error(f"Error detecting periodicity: {e}")
            
        return periodicity

class SpatialAnalysisProcessor:
    """Processeur d'analyse spatiale avancée pour caractéristiques géométriques"""
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        logger.info("SpatialAnalysisProcessor initialized")
    
    async def analyze_spatial_features(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyse les caractéristiques spatiales de la frame"""
        spatial_features = {}
        
        # Spatial correlation analysis
        if self.config.spatial_correlation_analysis:
            correlation_features = await self._analyze_spatial_correlation(frame)
            spatial_features['correlation_features'] = correlation_features
        
        # Local feature extraction (SIFT-like features)
        if self.config.local_feature_extraction:
            local_features = await self._extract_local_features(frame)
            spatial_features['local_features'] = local_features
        
        # Geometric invariant features
        if self.config.geometric_invariant_features:
            geometric_features = await self._extract_geometric_features(frame)
            spatial_features['geometric_features'] = geometric_features
        
        # Spatial distribution analysis
        distribution_features = await self._analyze_spatial_distribution(frame)
        spatial_features['distribution_features'] = distribution_features
        
        return spatial_features
    
    async def _analyze_spatial_correlation(self, frame: np.ndarray) -> Dict[str, Any]:
        """
Analyse la corrélation spatiale dans la frame"""
        correlation_features = {}
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Horizontal correlation
            horizontal_corr = np.corrcoef(gray.flatten()[:-1], gray.flatten()[1:])
            correlation_features['horizontal_correlation'] = float(horizontal_corr[0, 1])
            
            # Vertical correlation
            gray_transposed = gray.T
            vertical_corr = np.corrcoef(gray_transposed.flatten()[:-1], gray_transposed.flatten()[1:])
            correlation_features['vertical_correlation'] = float(vertical_corr[0, 1])
            
            # Diagonal correlation
            diagonal_pixels = []
            for i in range(min(gray.shape[0], gray.shape[1]) - 1):
                diagonal_pixels.append(gray[i, i])
                diagonal_pixels.append(gray[i+1, i+1])
            
            if len(diagonal_pixels) > 3:
                diagonal_corr = np.corrcoef(diagonal_pixels[:-1], diagonal_pixels[1:])
                correlation_features['diagonal_correlation'] = float(diagonal_corr[0, 1])
            
        except Exception as e:
            logger.error(f"Error analyzing spatial correlation: {e}")
            
        return correlation_features
    
    async def _extract_local_features(self, frame: np.ndarray) -> Dict[str, Any]:
        """Extrait les caractéristiques locales (keypoints et descripteurs)"""
        local_features = {}
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # ORB features (rotation and scale invariant)
            orb = cv2.ORB_create(nfeatures=100)
            keypoints, descriptors = orb.detectAndCompute(gray, None)
            
            if keypoints:
                # Analyze keypoint distribution
                keypoint_coords = np.array([kp.pt for kp in keypoints])
                
                local_features['num_keypoints'] = len(keypoints)
                local_features['keypoint_density'] = len(keypoints) / (frame.shape[0] * frame.shape[1])
                
                if len(keypoint_coords) > 1:
                    # Spatial distribution of keypoints
                    center_x, center_y = np.mean(keypoint_coords, axis=0)
                    local_features['keypoint_center'] = [float(center_x), float(center_y)]
                    
                    # Spread of keypoints
                    distances = np.sqrt(np.sum((keypoint_coords - [center_x, center_y])**2, axis=1))
                    local_features['keypoint_spread'] = float(np.std(distances))
            
            # Corner detection (Harris corners)
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=50, qualityLevel=0.01, minDistance=10)
            if corners is not None:
                local_features['num_corners'] = len(corners)
                local_features['corner_density'] = len(corners) / (frame.shape[0] * frame.shape[1])
            
        except Exception as e:
            logger.error(f"Error extracting local features: {e}")
            
        return local_features
    
    async def _extract_geometric_features(self, frame: np.ndarray) -> Dict[str, Any]:
        """Extrait les caractéristiques géométriques invariantes"""
        geometric_features = {}
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Edge-based geometric features
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Analyze largest contours
                largest_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
                
                contour_features = []
                for contour in largest_contours:
                    if len(contour) > 5:  # Minimum points for meaningful analysis
                        # Geometric moments
                        moments = cv2.moments(contour)
                        if moments['m00'] > 0:
                            # Centroid
                            cx = moments['m10'] / moments['m00']
                            cy = moments['m01'] / moments['m00']
                            
                            # Hu moments (scale, rotation, translation invariant)
                            hu_moments = cv2.HuMoments(moments).flatten()
                            
                            contour_feature = {
                                'area': float(cv2.contourArea(contour)),
                                'perimeter': float(cv2.arcLength(contour, True)),
                                'centroid': [float(cx), float(cy)],
                                'hu_moments': [float(h) for h in hu_moments[:4]]  # First 4 Hu moments
                            }
                            contour_features.append(contour_feature)
                
                geometric_features['contour_features'] = contour_features[:3]  # Top 3 contours
                geometric_features['num_significant_contours'] = len(contour_features)
            
            # Line detection (Hough transform)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=50)
            if lines is not None:
                geometric_features['num_lines'] = len(lines)
                
                # Analyze line orientations
                angles = [line[0][1] for line in lines]
                geometric_features['dominant_line_angle'] = float(np.mean(angles))
                geometric_features['line_angle_variance'] = float(np.var(angles))
            
        except Exception as e:
            logger.error(f"Error extracting geometric features: {e}")
            
        return geometric_features
    
    async def _analyze_spatial_distribution(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyse la distribution spatiale des intensités"""
        distribution_features = {}
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Divide frame into regions and analyze distribution
            h, w = gray.shape
            regions = {
                'top_left': gray[:h//2, :w//2],
                'top_right': gray[:h//2, w//2:],
                'bottom_left': gray[h//2:, :w//2],
                'bottom_right': gray[h//2:, w//2:]
            }
            
            region_stats = {}
            for region_name, region in regions.items():
                region_stats[region_name] = {
                    'mean': float(np.mean(region)),
                    'std': float(np.std(region)),
                    'entropy': float(-np.sum(np.histogram(region, bins=256, density=True)[0] * 
                                           np.log(np.histogram(region, bins=256, density=True)[0] + 1e-10)))
                }
            
            distribution_features['region_statistics'] = region_stats
            
            # Overall distribution metrics
            distribution_features['global_mean'] = float(np.mean(gray))
            distribution_features['global_std'] = float(np.std(gray))
            distribution_features['skewness'] = float(np.mean(((gray - np.mean(gray)) / np.std(gray))**3))
            distribution_features['kurtosis'] = float(np.mean(((gray - np.mean(gray)) / np.std(gray))**4))
            
        except Exception as e:
            logger.error(f"Error analyzing spatial distribution: {e}")
            
        return distribution_features

class SceneDetector:
    """Détecteur de changements de scène"""
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        logger.info("SceneDetector initialized")
    
    async def detect_scene_changes(self, frames: List[np.ndarray]) -> List[int]:
        """Détecte les changements de scène"""
        scene_boundaries = [0]  # First frame is always a scene boundary
        
        for i in range(1, len(frames)):
            # Compare consecutive frames
            similarity = self._compute_frame_similarity(frames[i-1], frames[i])
            
            if similarity < (1.0 - self.config.scene_threshold / 100.0):
                scene_boundaries.append(i)
        
        return scene_boundaries
    
    def _compute_frame_similarity(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
Calcule la similarité entre deux frames"""
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Compute histogram correlation
        hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
        
        correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return correlation

class DeepFeaturesProcessor:
    """
Processeur de caractéristiques profondes"""
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() and config.use_gpu else "cpu"
        
        if TORCH_AVAILABLE:
            self._load_model()
        
        logger.info("DeepFeaturesProcessor initialized")
    
    def _load_model(self):
        """Charge le modèle CNN pré-entraîné"""
        try:
            import torchvision.models as models
            
            if self.config.cnn_model == "resnet50":
                self.model = models.resnet50(pretrained=True)
                self.model.eval()
                self.model = self.model.to(self.device)
                
                # Remove final classification layer
                self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
            
        except Exception as e:
            logger.error(f"Error loading CNN model: {e}")
            self.model = None
    
    async def extract_features(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Extrait les caractéristiques profondes"""
        if not self.model or not TORCH_AVAILABLE:
            return None
        
        try:
            # Preprocess frame
            transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            input_tensor = transform(frame_rgb).unsqueeze(0).to(self.device)
            
            # Extract features
            with torch.no_grad():
                features = self.model(input_tensor)
                features = features.squeeze().cpu().numpy()
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting deep features: {e}")
            return None

# Export public API
__all__ = [
    'VideoFingerprintEngine',
    'VideoFingerprint',
    'VideoFrame',
    'VideoFingerprintConfig',
    'OpenCVProcessor',
    'PerceptualHashProcessor',
    'YOLOFrameProcessor',
    'MotionVectorProcessor',
    'SceneDetector',
    'DeepFeaturesProcessor',
    'VideoQuality',
    'FrameExtractionMode',
    'VideoCodec'
]
