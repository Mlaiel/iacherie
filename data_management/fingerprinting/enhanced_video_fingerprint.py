"""
🎬 Video Fingerprinting Engine - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/data_management/fingerprinting/enhanced_video_fingerprint.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Video Fingerprinting - Ultra Enterprise Production-Ready
Responsibility: Advanced video fingerprinting with OpenCV, pHash, YOLO, and motion analysis
==============================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. All rights reserved.
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
    """Configuration avancée pour le fingerprinting vidéo"""
    
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
    
    # Perceptual hashing
    phash_enabled: bool = True
    dhash_enabled: bool = True
    ahash_enabled: bool = True
    whash_enabled: bool = True
    hash_size: int = 16
    
    # Object detection
    yolo_enabled: bool = True
    yolo_model: str = "yolov8n.pt"  # Nano model for speed
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    
    # Motion analysis
    motion_analysis: bool = True
    optical_flow_enabled: bool = True
    motion_threshold: float = 0.1
    
    # Scene detection
    scene_detection: bool = True
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
    
    # Ultra-robust fingerprinting settings
    compression_resistance_enabled: bool = True
    multi_scale_hashing: bool = True
    dct_hash_enabled: bool = True
    block_based_hashing: bool = True
    temporal_consistency_check: bool = True
    
    # Enhanced YOLO with face detection
    face_detection_enabled: bool = True
    real_time_optimization: bool = True
    scene_analysis_enabled: bool = True
    temporal_feature_extraction: bool = True
    
    # Watermark and crop resistance
    watermark_resistance_enabled: bool = True
    crop_resistance_enabled: bool = True
    multi_region_hashing: bool = True
    geometric_invariant_features: bool = True
    robustness_metrics_enabled: bool = True
    
    # Advanced analysis parameters
    spatial_frequency_analysis: bool = True
    content_entropy_analysis: bool = True
    attack_resistance_scoring: bool = True

@dataclass
class VideoFrame:
    """Représentation d'une frame vidéo avec caractéristiques ultra-robustes"""
    frame_number: int
    timestamp: float
    image_data: np.ndarray
    is_keyframe: bool = False
    quality_score: float = 0.0
    motion_score: float = 0.0
    scene_id: Optional[int] = None
    
    # Standard hash signatures
    phash: Optional[str] = None
    dhash: Optional[str] = None
    ahash: Optional[str] = None
    whash: Optional[str] = None
    
    # Ultra-robust compression-resistant hashes
    robust_hashes: Optional[Dict[str, Any]] = None
    
    # Object detection results
    detected_objects: List[Dict[str, Any]] = field(default_factory=list)
    enhanced_objects: List[Dict[str, Any]] = field(default_factory=list)
    detected_faces: List[Dict[str, Any]] = field(default_factory=list)
    
    # Scene and temporal analysis
    scene_analysis: Optional[Dict[str, Any]] = None
    temporal_features: Optional[Dict[str, Any]] = None
    
    # Watermark and crop resistance features
    resistance_features: Optional[Dict[str, Any]] = None
    
    # Deep features
    cnn_features: Optional[np.ndarray] = None
    
    # Motion vectors
    motion_vectors: Optional[np.ndarray] = None

@dataclass
class VideoFingerprint:
    """Empreinte vidéo complète"""
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
        
        # Initialize ultra-robust processors
        if config.compression_resistance_enabled:
            self.compression_resistant_processor = CompressionResistantHashProcessor(config)
        else:
            self.compression_resistant_processor = None
            
        if config.face_detection_enabled:
            self.enhanced_yolo_processor = EnhancedYOLOProcessor(config)
        else:
            self.enhanced_yolo_processor = None
            
        if config.watermark_resistance_enabled or config.crop_resistance_enabled:
            self.watermark_crop_processor = WatermarkCropResistanceProcessor(config)
        else:
            self.watermark_crop_processor = None
        
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
        """Extrait les frames clés"""
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
        """Extrait les frames sur les changements de scène"""
        # Implementation would use scene detection algorithm
        # For now, use simplified version
        async for frame_data in self._extract_keyframes(cap, fps):
            yield frame_data
    
    async def _extract_adaptive_frames(self, cap: cv2.VideoCapture, fps: float):
        """Extraction adaptative intelligente"""
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
        """Calcule le score de mouvement entre deux frames"""
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Optical flow
        flow = cv2.calcOpticalFlowPyrLK(gray1, gray2, None, None)
        magnitude = np.sqrt(flow[0]**2 + flow[1]**2) if flow[0] is not None else np.array([0])
        
        return np.mean(magnitude)
    
    async def _process_frame_batch(self, frame_batch: List[Tuple[int, float, np.ndarray]]) -> List[VideoFrame]:
        """Traite un batch de frames"""
        processed_frames = []
        
        # Process frames in parallel
        tasks = []
        for frame_number, timestamp, image_data in frame_batch:
            task = asyncio.create_task(self._process_single_frame(frame_number, timestamp, image_data))
            tasks.append(task)
        
        processed_frames = await asyncio.gather(*tasks)
        return processed_frames
    
    async def _process_single_frame(self, frame_number: int, timestamp: float, image_data: np.ndarray) -> VideoFrame:
        """Traite une frame individuelle avec analyse ultra-robuste"""
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
        
        # Standard perceptual hashes
        if IMAGEHASH_AVAILABLE:
            hashes = await self.phash_processor.generate_hashes(image_data)
            video_frame.phash = hashes.get('phash')
            video_frame.dhash = hashes.get('dhash')
            video_frame.ahash = hashes.get('ahash')
            video_frame.whash = hashes.get('whash')
        
        # Ultra-robust compression-resistant hashes
        if self.compression_resistant_processor:
            robust_hashes = await self.compression_resistant_processor.generate_robust_hashes(image_data)
            video_frame.robust_hashes = robust_hashes
        
        # Standard object detection
        if self.yolo_processor and self.config.yolo_enabled:
            video_frame.detected_objects = await self.yolo_processor.detect_objects(image_data)
        
        # Enhanced YOLO with face detection and real-time analysis
        if self.enhanced_yolo_processor:
            enhanced_detection = await self.enhanced_yolo_processor.detect_objects_and_faces(image_data)
            video_frame.enhanced_objects = enhanced_detection.get('objects', [])
            video_frame.detected_faces = enhanced_detection.get('faces', [])
            video_frame.scene_analysis = enhanced_detection.get('scene_analysis', {})
            video_frame.temporal_features = enhanced_detection.get('temporal_features', {})
        
        # Watermark and crop resistance analysis
        if self.watermark_crop_processor:
            resistance_features = await self.watermark_crop_processor.analyze_resistance_features(image_data)
            video_frame.resistance_features = resistance_features
        
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
        """Calcule les caractéristiques globales de la vidéo"""
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
        """Estime le nombre de scènes"""
        if len(frames) < 2:
            return 1
        
        scene_changes = 0
        for i in range(1, len(frames)):
            if frames[i].scene_id != frames[i-1].scene_id:
                scene_changes += 1
        
        return scene_changes + 1
    
    async def _extract_dominant_colors(self, frames: List[VideoFrame]) -> List[Tuple[int, int, int]]:
        """Extrait les couleurs dominantes"""
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
        """Génère une signature temporelle"""
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
        """Calcule la similarité temporelle"""
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
        """Calcule la similarité des hashes"""
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
        """Calcule la similarité de mouvement"""
        if fp1.motion_energy == 0 and fp2.motion_energy == 0:
            return 1.0
        
        if fp1.motion_energy == 0 or fp2.motion_energy == 0:
            return 0.0
        
        # Simple ratio-based similarity
        ratio = min(fp1.motion_energy, fp2.motion_energy) / max(fp1.motion_energy, fp2.motion_energy)
        return ratio
    
    async def _compute_scene_similarity(self, frames1: List[VideoFrame], frames2: List[VideoFrame]) -> float:
        """Calcule la similarité de structure de scène"""
        # Compare scene transition patterns
        # This is a simplified implementation
        return 0.5  # Placeholder
    
    async def _compute_object_similarity(self, frames1: List[VideoFrame], frames2: List[VideoFrame]) -> float:
        """Calcule la similarité d'objets détectés"""
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
        """Calcule la similarité des caractéristiques profondes"""
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
        """Calcule la similarité pondérée globale"""
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
        """Calcule les métriques de qualité"""
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
    """Processeur OpenCV pour analyse vidéo"""
    
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
    """Processeur de hash perceptuel"""
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        logger.info("PerceptualHashProcessor initialized")
    
    async def generate_hashes(self, image_data: np.ndarray) -> Dict[str, str]:
        """Génère les hashes perceptuels"""
        if not IMAGEHASH_AVAILABLE:
            return {}
        
        # Convert OpenCV image to PIL
        image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        hashes = {}
        
        if self.config.phash_enabled:
            hashes['phash'] = str(imagehash.phash(pil_image, hash_size=self.config.hash_size))
        
        if self.config.dhash_enabled:
            hashes['dhash'] = str(imagehash.dhash(pil_image, hash_size=self.config.hash_size))
        
        if self.config.ahash_enabled:
            hashes['ahash'] = str(imagehash.average_hash(pil_image, hash_size=self.config.hash_size))
        
        if self.config.whash_enabled:
            hashes['whash'] = str(imagehash.whash(pil_image, hash_size=self.config.hash_size))
        
        return hashes

class YOLOFrameProcessor:
    """Processeur YOLO pour détection d'objets"""
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        
        if YOLO_AVAILABLE:
            self.model = YOLO(config.yolo_model)
        else:
            self.model = None
            
        logger.info("YOLOFrameProcessor initialized")
    
    async def detect_objects(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Détecte les objets dans une frame"""
        if not self.model:
            return []
        
        try:
            # Run YOLO detection
            results = self.model(frame, 
                               conf=self.config.confidence_threshold,
                               iou=self.config.iou_threshold,
                               verbose=False)
            
            detected_objects = []
            
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        obj_info = {
                            'class': result.names[int(box.cls)],
                            'confidence': float(box.conf),
                            'bbox': box.xyxy.tolist()[0] if hasattr(box, 'xyxy') else [],
                        }
                        detected_objects.append(obj_info)
            
            return detected_objects
            
        except Exception as e:
            logger.error(f"Error in YOLO detection: {e}")
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
        """Calcule la similarité entre deux frames"""
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Compute histogram correlation
        hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
        
        correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return correlation

class DeepFeaturesProcessor:
    """Processeur de caractéristiques profondes"""
    
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

class CompressionResistantHashProcessor:
    """Processeur de hash perceptuel résistant à la compression ultra-robuste"""
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        logger.info("CompressionResistantHashProcessor initialized")
    
    async def generate_robust_hashes(self, image_data: np.ndarray) -> Dict[str, Any]:
        """Génère des hash résistants à la compression avec techniques avancées"""
        if not IMAGEHASH_AVAILABLE:
            return {}
        
        try:
            # Convert to different color spaces for robustness
            gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
            yuv = cv2.cvtColor(image_data, cv2.COLOR_BGR2YUV)
            
            # Multi-scale perceptual hashing
            robust_hashes = {}
            
            # 1. DCT-based hash (compression resistant)
            robust_hashes['dct_hash'] = self._generate_dct_hash(gray)
            
            # 2. Multi-scale perceptual hash
            for scale in [0.5, 1.0, 1.5]:
                scaled_img = self._scale_image(image_data, scale)
                pil_image = Image.fromarray(cv2.cvtColor(scaled_img, cv2.COLOR_BGR2RGB))
                
                robust_hashes[f'phash_scale_{scale}'] = str(
                    imagehash.phash(pil_image, hash_size=self.config.hash_size)
                )
            
            # 3. Color-channel based hashing
            for i, channel_name in enumerate(['Y', 'U', 'V']):
                channel = yuv[:, :, i]
                pil_channel = Image.fromarray(channel)
                robust_hashes[f'channel_hash_{channel_name}'] = str(
                    imagehash.phash(pil_channel, hash_size=self.config.hash_size)
                )
            
            # 4. Block-based hashing for spatial robustness
            robust_hashes['block_hashes'] = self._generate_block_hashes(gray)
            
            # 5. Temporal consistency hash (if previous frame available)
            robust_hashes['temporal_consistency'] = self._calculate_temporal_hash(gray)
            
            return robust_hashes
            
        except Exception as e:
            logger.error(f"Error generating robust hashes: {e}")
            return {}
    
    def _generate_dct_hash(self, gray_image: np.ndarray, hash_size: int = 8) -> str:
        """Génère un hash basé sur la DCT résistant à la compression"""
        try:
            # Resize to standard size
            resized = cv2.resize(gray_image, (32, 32))
            
            # Apply DCT
            dct = cv2.dct(np.float32(resized))
            
            # Keep low frequency components (top-left corner)
            dct_low_freq = dct[0:hash_size, 0:hash_size]
            
            # Calculate median
            median = np.median(dct_low_freq)
            
            # Generate binary hash
            binary_hash = dct_low_freq > median
            
            # Convert to string
            return ''.join(['1' if b else '0' for b in binary_hash.flatten()])
            
        except Exception as e:
            logger.error(f"Error in DCT hash generation: {e}")
            return ""
    
    def _scale_image(self, image: np.ndarray, scale: float) -> np.ndarray:
        """Redimensionne l'image selon le facteur d'échelle"""
        height, width = image.shape[:2]
        new_height, new_width = int(height * scale), int(width * scale)
        return cv2.resize(image, (new_width, new_height))
    
    def _generate_block_hashes(self, gray_image: np.ndarray, block_size: int = 64) -> List[str]:
        """Génère des hash par blocs pour résister au recadrage"""
        height, width = gray_image.shape
        block_hashes = []
        
        for y in range(0, height - block_size, block_size // 2):
            for x in range(0, width - block_size, block_size // 2):
                block = gray_image[y:y+block_size, x:x+block_size]
                if block.shape[0] == block_size and block.shape[1] == block_size:
                    block_hash = self._generate_dct_hash(block, 8)
                    block_hashes.append(block_hash)
        
        return block_hashes
    
    def _calculate_temporal_hash(self, current_frame: np.ndarray) -> Optional[str]:
        """Calcule un hash temporel pour la cohérence entre frames"""
        # Cette méthode serait étendue pour utiliser les frames précédentes
        # Pour l'instant, retourne un hash simple
        try:
            # Simple temporal hash based on edge patterns
            edges = cv2.Canny(current_frame, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Quantize edge density to create temporal signature
            temporal_signature = int(edge_density * 255)
            return f"temporal_{temporal_signature:02x}"
            
        except Exception:
            return None

class EnhancedYOLOProcessor:
    """Processeur YOLO avancé avec détection de visages temps réel"""
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        self.yolo_model = None
        self.face_detector = None
        
        if YOLO_AVAILABLE:
            self.yolo_model = YOLO(config.yolo_model)
        
        # Initialize face detection
        self._initialize_face_detection()
        
        logger.info("EnhancedYOLOProcessor initialized with face detection")
    
    def _initialize_face_detection(self):
        """Initialise la détection de visages avec OpenCV"""
        try:
            # Use OpenCV's pre-trained face detection
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_detector = cv2.CascadeClassifier(face_cascade_path)
            logger.info("Face detection initialized successfully")
        except Exception as e:
            logger.warning(f"Face detection initialization failed: {e}")
            self.face_detector = None
    
    async def detect_objects_and_faces(self, frame: np.ndarray) -> Dict[str, Any]:
        """Détection d'objets et de visages en temps réel"""
        detection_results = {
            'objects': [],
            'faces': [],
            'scene_analysis': {},
            'temporal_features': {}
        }
        
        try:
            # YOLO object detection
            if self.yolo_model:
                object_detections = await self._detect_objects_yolo(frame)
                detection_results['objects'] = object_detections
            
            # Face detection
            if self.face_detector is not None:
                face_detections = await self._detect_faces(frame)
                detection_results['faces'] = face_detections
            
            # Scene analysis
            detection_results['scene_analysis'] = await self._analyze_scene_content(frame)
            
            # Temporal features for consistency
            detection_results['temporal_features'] = await self._extract_temporal_features(frame)
            
            return detection_results
            
        except Exception as e:
            logger.error(f"Error in enhanced detection: {e}")
            return detection_results
    
    async def _detect_objects_yolo(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Détection d'objets YOLO optimisée"""
        objects = []
        
        try:
            results = self.yolo_model(frame, 
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
                            'center': self._calculate_center(box.xyxy.tolist()[0]) if hasattr(box, 'xyxy') else [],
                            'area': self._calculate_area(box.xyxy.tolist()[0]) if hasattr(box, 'xyxy') else 0
                        }
                        objects.append(obj_info)
        
        except Exception as e:
            logger.error(f"YOLO detection error: {e}")
        
        return objects
    
    async def _detect_faces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Détection de visages avec caractéristiques avancées"""
        faces = []
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_rects = self.face_detector.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            for (x, y, w, h) in face_rects:
                face_info = {
                    'bbox': [x, y, x+w, y+h],
                    'center': [x + w//2, y + h//2],
                    'area': w * h,
                    'confidence': 0.8,  # OpenCV doesn't provide confidence
                    'face_features': await self._extract_face_features(gray[y:y+h, x:x+w])
                }
                faces.append(face_info)
        
        except Exception as e:
            logger.error(f"Face detection error: {e}")
        
        return faces
    
    async def _extract_face_features(self, face_roi: np.ndarray) -> Dict[str, Any]:
        """Extrait des caractéristiques du visage pour la robustesse"""
        try:
            features = {}
            
            # Basic geometric features
            height, width = face_roi.shape
            features['aspect_ratio'] = width / height if height > 0 else 0
            
            # Texture analysis
            features['texture_variance'] = float(np.var(face_roi))
            features['mean_intensity'] = float(np.mean(face_roi))
            
            # Edge density in face region
            edges = cv2.Canny(face_roi, 50, 150)
            features['edge_density'] = float(np.sum(edges > 0) / (height * width))
            
            return features
            
        except Exception as e:
            logger.error(f"Face feature extraction error: {e}")
            return {}
    
    async def _analyze_scene_content(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyse du contenu de la scène pour la cohérence temporelle"""
        try:
            analysis = {}
            
            # Color distribution
            hist_b = cv2.calcHist([frame], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([frame], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([frame], [2], None, [256], [0, 256])
            
            analysis['color_distribution'] = {
                'dominant_colors': self._find_dominant_colors(frame),
                'color_variance': float(np.var([hist_b, hist_g, hist_r]))
            }
            
            # Scene complexity
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            analysis['scene_complexity'] = float(np.sum(edges > 0) / (edges.shape[0] * edges.shape[1]))
            
            # Brightness and contrast
            analysis['brightness'] = float(np.mean(gray))
            analysis['contrast'] = float(np.std(gray))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Scene analysis error: {e}")
            return {}
    
    async def _extract_temporal_features(self, frame: np.ndarray) -> Dict[str, Any]:
        """Extrait des caractéristiques temporelles pour la cohérence"""
        try:
            features = {}
            
            # Frame signature based on spatial distribution
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Spatial frequency analysis
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude = np.abs(f_shift)
            
            features['spatial_frequency_energy'] = float(np.mean(magnitude))
            features['frequency_distribution'] = float(np.std(magnitude))
            
            return features
            
        except Exception as e:
            logger.error(f"Temporal feature extraction error: {e}")
            return {}
    
    def _calculate_center(self, bbox: List[float]) -> List[float]:
        """Calcule le centre d'une bbox"""
        if len(bbox) >= 4:
            return [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]
        return [0, 0]
    
    def _calculate_area(self, bbox: List[float]) -> float:
        """Calcule l'aire d'une bbox"""
        if len(bbox) >= 4:
            return (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
        return 0
    
    def _find_dominant_colors(self, image: np.ndarray, k: int = 3) -> List[List[int]]:
        """Trouve les couleurs dominantes dans l'image"""
        try:
            # Reshape image to be a list of pixels
            data = image.reshape((-1, 3))
            data = np.float32(data)
            
            # Apply K-means clustering
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers to integers and return
            centers = np.uint8(centers)
            return centers.tolist()
            
        except Exception as e:
            logger.error(f"Dominant color extraction error: {e}")
            return []

class WatermarkCropResistanceProcessor:
    """Processeur de résistance aux watermarks et recadrages"""
    
    def __init__(self, config: VideoFingerprintConfig):
        self.config = config
        logger.info("WatermarkCropResistanceProcessor initialized")
    
    async def analyze_resistance_features(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyse les caractéristiques de résistance aux attaques"""
        resistance_features = {
            'multi_region_hashes': {},
            'geometric_invariants': {},
            'watermark_detection': {},
            'robustness_metrics': {}
        }
        
        try:
            # 1. Multi-region hashing for crop resistance
            resistance_features['multi_region_hashes'] = await self._generate_multi_region_hashes(frame)
            
            # 2. Geometric invariant features
            resistance_features['geometric_invariants'] = await self._extract_geometric_invariants(frame)
            
            # 3. Watermark detection and analysis
            resistance_features['watermark_detection'] = await self._detect_potential_watermarks(frame)
            
            # 4. Content robustness metrics
            resistance_features['robustness_metrics'] = await self._calculate_robustness_metrics(frame)
            
            return resistance_features
            
        except Exception as e:
            logger.error(f"Error in resistance analysis: {e}")
            return resistance_features
    
    async def _generate_multi_region_hashes(self, frame: np.ndarray) -> Dict[str, Any]:
        """Génère des hash multi-régions pour résister au recadrage"""
        try:
            h, w = frame.shape[:2]
            region_hashes = {}
            
            # Define multiple overlapping regions
            regions = {
                'center': (w//4, h//4, 3*w//4, 3*h//4),
                'top_left': (0, 0, w//2, h//2),
                'top_right': (w//2, 0, w, h//2),
                'bottom_left': (0, h//2, w//2, h),
                'bottom_right': (w//2, h//2, w, h),
                'horizontal_center': (0, h//4, w, 3*h//4),
                'vertical_center': (w//4, 0, 3*w//4, h)
            }
            
            for region_name, (x1, y1, x2, y2) in regions.items():
                region_frame = frame[y1:y2, x1:x2]
                if region_frame.size > 0:
                    region_hashes[region_name] = await self._hash_region(region_frame)
            
            # Generate overlapping grid hashes
            grid_size = 4
            grid_hashes = []
            for i in range(grid_size):
                for j in range(grid_size):
                    x1 = (w * i) // grid_size
                    y1 = (h * j) // grid_size
                    x2 = (w * (i + 1)) // grid_size
                    y2 = (h * (j + 1)) // grid_size
                    
                    grid_region = frame[y1:y2, x1:x2]
                    if grid_region.size > 0:
                        grid_hash = await self._hash_region(grid_region)
                        grid_hashes.append(grid_hash)
            
            region_hashes['grid_hashes'] = grid_hashes
            
            return region_hashes
            
        except Exception as e:
            logger.error(f"Multi-region hash error: {e}")
            return {}
    
    async def _hash_region(self, region: np.ndarray) -> str:
        """Génère un hash pour une région spécifique"""
        try:
            if IMAGEHASH_AVAILABLE:
                # Convert to PIL Image
                if len(region.shape) == 3:
                    region_rgb = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(region_rgb)
                else:
                    pil_image = Image.fromarray(region)
                
                # Use perceptual hash
                return str(imagehash.phash(pil_image, hash_size=8))
            else:
                # Fallback simple hash
                return hashlib.md5(region.tobytes()).hexdigest()[:16]
                
        except Exception as e:
            logger.error(f"Region hashing error: {e}")
            return ""
    
    async def _extract_geometric_invariants(self, frame: np.ndarray) -> Dict[str, Any]:
        """Extrait des invariants géométriques résistants aux transformations"""
        try:
            invariants = {}
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect keypoints and descriptors
            sift = cv2.SIFT_create()
            keypoints, descriptors = sift.detectAndCompute(gray, None)
            
            if descriptors is not None:
                # Statistical moments of descriptors (rotation/scale invariant)
                invariants['descriptor_moments'] = {
                    'mean': float(np.mean(descriptors)),
                    'std': float(np.std(descriptors)),
                    'skewness': float(self._calculate_skewness(descriptors)),
                    'kurtosis': float(self._calculate_kurtosis(descriptors))
                }
                
                # Spatial distribution of keypoints
                if keypoints:
                    kp_coords = np.array([[kp.pt[0], kp.pt[1]] for kp in keypoints])
                    invariants['keypoint_distribution'] = {
                        'centroid': np.mean(kp_coords, axis=0).tolist(),
                        'spread': float(np.std(kp_coords)),
                        'count': len(keypoints)
                    }
            
            # Hu moments (affine invariant)
            moments = cv2.moments(gray)
            hu_moments = cv2.HuMoments(moments)
            invariants['hu_moments'] = [float(hu) for hu in hu_moments.flatten()]
            
            return invariants
            
        except Exception as e:
            logger.error(f"Geometric invariant extraction error: {e}")
            return {}
    
    async def _detect_potential_watermarks(self, frame: np.ndarray) -> Dict[str, Any]:
        """Détecte les watermarks potentiels"""
        try:
            detection_result = {
                'watermark_probability': 0.0,
                'suspected_regions': [],
                'transparency_analysis': {},
                'pattern_analysis': {}
            }
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Look for semi-transparent regions (common in watermarks)
            # Analyze alpha channel if available or detect transparency patterns
            
            # Edge detection to find overlay patterns
            edges = cv2.Canny(gray, 50, 150)
            
            # Look for repeated patterns (watermark signatures)
            # Use template matching or frequency analysis
            
            # Analyze corners and edges where watermarks are often placed
            corner_regions = [
                gray[0:gray.shape[0]//4, 0:gray.shape[1]//4],  # Top-left
                gray[0:gray.shape[0]//4, -gray.shape[1]//4:],  # Top-right
                gray[-gray.shape[0]//4:, 0:gray.shape[1]//4],  # Bottom-left
                gray[-gray.shape[0]//4:, -gray.shape[1]//4:]   # Bottom-right
            ]
            
            for i, corner in enumerate(corner_regions):
                if corner.size > 0:
                    # Analyze corner for watermark-like patterns
                    corner_variance = np.var(corner)
                    corner_edges = cv2.Canny(corner, 30, 100)
                    edge_density = np.sum(corner_edges > 0) / corner.size
                    
                    if corner_variance < 500 and edge_density > 0.01:  # Potential watermark
                        detection_result['suspected_regions'].append({
                            'region': f'corner_{i}',
                            'variance': float(corner_variance),
                            'edge_density': float(edge_density)
                        })
            
            # Calculate overall watermark probability
            if detection_result['suspected_regions']:
                detection_result['watermark_probability'] = min(
                    len(detection_result['suspected_regions']) * 0.25, 1.0
                )
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Watermark detection error: {e}")
            return {}
    
    async def _calculate_robustness_metrics(self, frame: np.ndarray) -> Dict[str, Any]:
        """Calcule les métriques de robustesse du contenu"""
        try:
            metrics = {}
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Information density
            # High information density = more robust to attacks
            edges = cv2.Canny(gray, 50, 150)
            metrics['information_density'] = float(np.sum(edges > 0) / edges.size)
            
            # Spatial frequency distribution
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.abs(f_shift)
            
            # Energy distribution across frequencies
            low_freq_energy = np.mean(magnitude_spectrum[
                gray.shape[0]//2-10:gray.shape[0]//2+10,
                gray.shape[1]//2-10:gray.shape[1]//2+10
            ])
            total_energy = np.mean(magnitude_spectrum)
            
            metrics['frequency_robustness'] = float(low_freq_energy / total_energy) if total_energy > 0 else 0
            
            # Content uniqueness (entropy)
            hist, _ = np.histogram(gray.flatten(), bins=256, range=[0, 256])
            hist = hist / hist.sum()  # Normalize
            entropy = -np.sum(hist * np.log2(hist + 1e-10))
            metrics['content_entropy'] = float(entropy)
            
            # Structural complexity
            metrics['structural_complexity'] = float(np.std(gray)) / 255.0
            
            # Attack resistance score (composite metric)
            metrics['attack_resistance_score'] = (
                metrics['information_density'] * 0.3 +
                metrics['frequency_robustness'] * 0.2 +
                (metrics['content_entropy'] / 8.0) * 0.3 +  # Normalize entropy
                metrics['structural_complexity'] * 0.2
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Robustness metrics calculation error: {e}")
            return {}
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calcule l'asymétrie des données"""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0
            return np.mean(((data - mean) / std) ** 3)
        except:
            return 0
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calcule l'aplatissement des données"""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0
            return np.mean(((data - mean) / std) ** 4) - 3
        except:
            return 0

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
    'VideoCodec',
    # Ultra-robust processors
    'CompressionResistantHashProcessor',
    'EnhancedYOLOProcessor',
    'WatermarkCropResistanceProcessor'
]
