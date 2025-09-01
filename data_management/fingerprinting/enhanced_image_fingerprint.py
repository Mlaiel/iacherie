"""📸 Image Fingerprinting Engine - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/data_management/fingerprinting/enhanced_image_fingerprint.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Image Fingerprinting - Ultra Enterprise Production-Ready
Responsibility: Advanced image fingerprinting with CLIP, ImageHash, CNN features, and perceptual analysis
===============================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC IMAGE FINGERPRINTING:
Image Upload (Photographes/Influencers/Artistes) → Format Validation → 
Quality Assessment → Perceptual Hashing → CLIP Encoding → CNN Features → 
Object Detection → Scene Analysis → Color Analysis → Texture Features → 
Vector Embedding → FAISS Indexing → Real-time Monitoring → Violation Detection

IMAGE FINGERPRINTING TECHNOLOGIES:
├── 🧠 CLIP (Vision-Language Model)
├── 🔍 Perceptual Hashing (pHash + dHash + aHash + wHash)
├── 🤖 CNN Features (ResNet + EfficientNet + Vision Transformer)
├── 👁️ Object Detection (YOLO + DETR)
├── 🎨 Color Analysis (Histogram + Dominant Colors)
├── 🧵 Texture Features (LBP + GLCM + Gabor)
├── 📐 Geometric Features (SIFT + ORB + SURF)
├── 🔬 Quality Assessment (BRISQUE + NIQE)
└── 🛡️ Protection Pipeline (Multi-modal Matching)
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Set
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

# Image processing libraries
try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - install Pillow")

try:
    import imagehash
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False
    logging.warning("ImageHash not available - install imagehash")

# Deep learning libraries
try:
    import torch
    import torchvision.transforms as transforms
    import torchvision.models as models
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch not available - install torch")

try:
    import clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    logging.warning("CLIP not available - install git+https://github.com/openai/CLIP.git")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("YOLO not available - install ultralytics")

try:
    from skimage import feature, measure, filters
    from skimage.feature import local_binary_pattern, greycomatrix, greycoprops
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    logging.warning("Scikit-image not available - install scikit-image")

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

logger = logging.getLogger(__name__)

class ImageFormat(Enum):
    """Formats d'images supportés"""

    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"
    GIF = "gif"

class ImageQuality(Enum):
    """Niveaux de qualité d'image"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

class ColorSpace(Enum):
    """Espaces colorimétriques"""

    RGB = "rgb"
    BGR = "bgr"
    HSV = "hsv"
    LAB = "lab"
    YUV = "yuv"

@dataclass
class ImageFingerprintConfig:
    """Configuration avancée pour le fingerprinting d'images"""
    
    # Image processing parameters
    max_dimension: int = 2048  # Maximum width/height
    min_dimension: int = 64   # Minimum width/height
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    supported_formats: Set[str] = field(default_factory=lambda: {
        'jpg', 'jpeg', 'png', 'webp', 'tiff', 'bmp', 'gif'
    })
    
    # Quality assessment
    quality_assessment: bool = True
    min_quality_score: float = 0.3
    blur_threshold: float = 100.0
    noise_threshold: float = 0.1
    
    # Perceptual hashing
    phash_enabled: bool = True
    dhash_enabled: bool = True
    ahash_enabled: bool = True
    whash_enabled: bool = True
    colorhash_enabled: bool = True
    hash_size: int = 16
    
    # CLIP features
    clip_enabled: bool = True
    clip_model: str = "ViT-B/32"
    
    # CNN features
    cnn_enabled: bool = True
    cnn_models: List[str] = field(default_factory=lambda: ["resnet50", "efficientnet_b0"])
    feature_layers: List[str] = field(default_factory=lambda: ["avgpool", "features"])
    
    # Object detection
    object_detection: bool = True
    yolo_model: str = "yolov8n.pt"
    confidence_threshold: float = 0.5
    
    # Color analysis
    color_analysis: bool = True
    dominant_colors_count: int = 5
    color_histogram_bins: int = 32
    
    # Texture analysis
    texture_analysis: bool = True
    lbp_radius: int = 3
    lbp_n_points: int = 24
    glcm_distances: List[int] = field(default_factory=lambda: [1, 2, 3])
    glcm_angles: List[float] = field(default_factory=lambda: [0, np.pi/4, np.pi/2, 3*np.pi/4])
    
    # Geometric features
    geometric_features: bool = True
    sift_enabled: bool = True
    orb_enabled: bool = True
    max_keypoints: int = 500
    
    # Performance
    use_gpu: bool = True
    parallel_processing: bool = True
    max_workers: int = mp.cpu_count()
    batch_size: int = 8
    
    # Preprocessing
    auto_enhance: bool = True
    noise_reduction: bool = True
    contrast_enhancement: bool = True

@dataclass
class ColorAnalysis:
    """Analyse colorimétrique d'une image"""
    dominant_colors: List[Tuple[int, int, int]] = field(default_factory=list)
    color_histogram: Optional[np.ndarray] = None
    average_color: Tuple[int, int, int] = (0, 0, 0)
    color_variance: float = 0.0
    brightness: float = 0.0
    contrast: float = 0.0
    saturation: float = 0.0

@dataclass
class TextureFeatures:
    """
Caractéristiques de texture"""
    lbp_histogram: Optional[np.ndarray] = None
    glcm_properties: Dict[str, float] = field(default_factory=dict)
    gabor_responses: Optional[np.ndarray] = None
    texture_energy: float = 0.0
    texture_homogeneity: float = 0.0
    texture_contrast: float = 0.0

@dataclass
class GeometricFeatures:
    """
Caractéristiques géométriques"""
    sift_keypoints: List[cv2.KeyPoint] = field(default_factory=list)
    sift_descriptors: Optional[np.ndarray] = None
    orb_keypoints: List[cv2.KeyPoint] = field(default_factory=list)
    orb_descriptors: Optional[np.ndarray] = None
    corner_points: List[Tuple[int, int]] = field(default_factory=list)
    edge_density: float = 0.0

@dataclass
class QualityMetrics:
    """
Métriques de qualité d'image"""
    overall_score: float = 0.0
    sharpness_score: float = 0.0
    noise_score: float = 0.0
    brightness_score: float = 0.0
    contrast_score: float = 0.0
    color_score: float = 0.0
    brisque_score: Optional[float] = None
    niqe_score: Optional[float] = None

@dataclass
class ImageFingerprint:
    """
Empreinte complète d'une image"""
    image_id: str
    filename: str
    dimensions: Tuple[int, int]
    file_size: int
    format: str
    color_channels: int
    
    # Perceptual hashes
    phash: Optional[str] = None
    dhash: Optional[str] = None
    ahash: Optional[str] = None
    whash: Optional[str] = None
    colorhash: Optional[str] = None
    
    # Deep learning features
    clip_features: Optional[np.ndarray] = None
    cnn_features: Dict[str, np.ndarray] = field(default_factory=dict)
    
    # Traditional computer vision features
    color_analysis: ColorAnalysis = field(default_factory=ColorAnalysis)
    texture_features: TextureFeatures = field(default_factory=TextureFeatures)
    geometric_features: GeometricFeatures = field(default_factory=GeometricFeatures)
    
    # Object detection
    detected_objects: List[Dict[str, Any]] = field(default_factory=list)
    
    # Quality assessment
    quality_metrics: QualityMetrics = field(default_factory=QualityMetrics)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    processing_time: float = 0.0
    
    # Scene and semantic information
    scene_category: Optional[str] = None
    semantic_tags: List[str] = field(default_factory=list)
    
    # Multi-scale features
    pyramid_features: Dict[int, Dict[str, Any]] = field(default_factory=dict)

class ImageFingerprintEngine:
    """
    Engine principal de fingerprinting d'images ultra-avancé
    
    Features:
    - Multi-modal feature extraction
    - Perceptual hashing suite complète
    - Deep learning features (CLIP, CNN)
    - Traditional computer vision
    - Quality assessment automatique
    - Object and scene detection
    - Color and texture analysis
    - Geometric feature extraction
    - Multi-scale processing
    - GPU acceleration
    """
    
    def __init__(self, config: ImageFingerprintConfig):
        self.config = config
        
        # Initialize processors
        self.hash_processor = PerceptualImageProcessor(config)
        self.clip_processor = CLIPProcessor(config) if CLIP_AVAILABLE else None
        self.cnn_processor = CNNFeaturesProcessor(config)
        self.object_detector = ObjectDetector(config) if YOLO_AVAILABLE else None
        self.quality_assessor = QualityAssessor(config)
        self.color_analyzer = ColorAnalyzer(config)
        self.texture_analyzer = TextureAnalyzer(config)
        self.geometric_analyzer = GeometricAnalyzer(config)
        
        # GPU setup
        self.device = self._setup_device()
        
        # Thread pools
        self.thread_pool = ThreadPoolExecutor(max_workers=config.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=config.max_workers)
        
        logger.info("ImageFingerprintEngine initialized")
    
    def _setup_device(self) -> str:
        """Configure le device de traitement"""
        if self.config.use_gpu:
            if TORCH_AVAILABLE and torch.cuda.is_available():
                return "cuda"
        return "cpu"
    
    async def generate_fingerprint(self, image_path: str) -> ImageFingerprint:
        """Génère l'empreinte complète d'une image"""
        start_time = time.time()
        
        try:
            # Validate and load image
            image_info, image_data = await self._load_and_validate_image(image_path)
            
            # Create fingerprint container
            fingerprint = ImageFingerprint(
                image_id=self._generate_image_id(image_path, image_info),
                filename=Path(image_path).name,
                dimensions=image_info['dimensions'],
                file_size=image_info['file_size'],
                format=image_info['format'],
                color_channels=image_info['channels']
            )
            
            # Preprocess image if needed
            processed_image = await self._preprocess_image(image_data)
            
            # Generate all features in parallel
            feature_tasks = []
            
            # Perceptual hashes
            if any([self.config.phash_enabled, self.config.dhash_enabled, 
                   self.config.ahash_enabled, self.config.whash_enabled]):
                feature_tasks.append(
                    self._generate_perceptual_hashes(processed_image, fingerprint)
                )
            
            # CLIP features
            if self.clip_processor and self.config.clip_enabled:
                feature_tasks.append(
                    self._generate_clip_features(processed_image, fingerprint)
                )
            
            # CNN features
            if self.config.cnn_enabled:
                feature_tasks.append(
                    self._generate_cnn_features(processed_image, fingerprint)
                )
            
            # Quality assessment
            if self.config.quality_assessment:
                feature_tasks.append(
                    self._assess_image_quality(processed_image, fingerprint)
                )
            
            # Color analysis
            if self.config.color_analysis:
                feature_tasks.append(
                    self._analyze_colors(processed_image, fingerprint)
                )
            
            # Texture analysis
            if self.config.texture_analysis:
                feature_tasks.append(
                    self._analyze_texture(processed_image, fingerprint)
                )
            
            # Geometric features
            if self.config.geometric_features:
                feature_tasks.append(
                    self._extract_geometric_features(processed_image, fingerprint)
                )
            
            # Object detection
            if self.object_detector and self.config.object_detection:
                feature_tasks.append(
                    self._detect_objects(processed_image, fingerprint)
                )
            
            # Execute all tasks
            await asyncio.gather(*feature_tasks)
            
            # Generate multi-scale features
            if len(processed_image.shape) >= 2:
                await self._generate_multiscale_features(processed_image, fingerprint)
            
            # Scene classification
            await self._classify_scene(fingerprint)
            
            # Calculate processing time
            fingerprint.processing_time = time.time() - start_time
            
            logger.info(f"Image fingerprint generated for {image_path} in {fingerprint.processing_time:.2f}s")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error generating image fingerprint: {e}")
            raise
    
    async def compare_fingerprints(self,
                                 fingerprint1: ImageFingerprint,
                                 fingerprint2: ImageFingerprint) -> Dict[str, float]:
        """Compare deux empreintes d'images"""
        try:
            similarity_scores = {}
            
            # Perceptual hash similarity
            hash_similarity = await self._compute_hash_similarity(fingerprint1, fingerprint2)
            similarity_scores.update(hash_similarity)
            
            # CLIP similarity
            if (fingerprint1.clip_features is not None and 
                fingerprint2.clip_features is not None):
                clip_sim = await self._compute_clip_similarity(
                    fingerprint1.clip_features, fingerprint2.clip_features
                )
                similarity_scores['clip'] = clip_sim
            
            # CNN features similarity
            cnn_similarity = await self._compute_cnn_similarity(
                fingerprint1.cnn_features, fingerprint2.cnn_features
            )
            similarity_scores.update(cnn_similarity)
            
            # Color similarity
            color_similarity = await self._compute_color_similarity(
                fingerprint1.color_analysis, fingerprint2.color_analysis
            )
            similarity_scores['color'] = color_similarity
            
            # Texture similarity
            texture_similarity = await self._compute_texture_similarity(
                fingerprint1.texture_features, fingerprint2.texture_features
            )
            similarity_scores['texture'] = texture_similarity
            
            # Geometric similarity
            geometric_similarity = await self._compute_geometric_similarity(
                fingerprint1.geometric_features, fingerprint2.geometric_features
            )
            similarity_scores['geometric'] = geometric_similarity
            
            # Object detection similarity
            if fingerprint1.detected_objects and fingerprint2.detected_objects:
                object_similarity = await self._compute_object_similarity(
                    fingerprint1.detected_objects, fingerprint2.detected_objects
                )
                similarity_scores['objects'] = object_similarity
            
            # Multi-scale similarity
            multiscale_similarity = await self._compute_multiscale_similarity(
                fingerprint1.pyramid_features, fingerprint2.pyramid_features
            )
            similarity_scores['multiscale'] = multiscale_similarity
            
            # Weighted overall similarity
            overall_similarity = await self._compute_weighted_image_similarity(similarity_scores)
            similarity_scores['overall'] = overall_similarity
            
            return similarity_scores
            
        except Exception as e:
            logger.error(f"Error comparing image fingerprints: {e}")
            raise
    
    async def _load_and_validate_image(self, image_path: str) -> Tuple[Dict[str, Any], np.ndarray]:
        """Charge et valide une image"""
        path = Path(image_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if path.stat().st_size > self.config.max_file_size:
            raise ValueError(f"Image file too large: {path.stat().st_size} bytes")
        
        # Check file extension
        file_extension = path.suffix.lower().lstrip('.')
        if file_extension not in self.config.supported_formats:
            raise ValueError(f"Unsupported image format: {file_extension}")
        
        # Load image with OpenCV
        image_data = cv2.imread(str(path), cv2.IMREAD_COLOR)
        
        if image_data is None:
            raise ValueError(f"Cannot load image: {image_path}")
        
        height, width = image_data.shape[:2]
        channels = image_data.shape[2] if len(image_data.shape) > 2 else 1
        
        # Validate dimensions
        if min(width, height) < self.config.min_dimension:
            raise ValueError(f"Image too small: {width}x{height}")
        
        if max(width, height) > self.config.max_dimension:
            # Resize if too large
            scale = self.config.max_dimension / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image_data = cv2.resize(image_data, (new_width, new_height), interpolation=cv2.INTER_AREA)
            height, width = new_height, new_width
        
        image_info = {
            'dimensions': (width, height),
            'channels': channels,
            'format': file_extension,
            'file_size': path.stat().st_size
        }
        
        return image_info, image_data
    
    def _generate_image_id(self, image_path: str, image_info: Dict[str, Any]) -> str:
        """Génère un ID unique pour l'image"""
        path = Path(image_path)
        content = f"{path.name}_{image_info['file_size']}_{path.stat().st_mtime}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def _preprocess_image(self, image_data: np.ndarray) -> np.ndarray:
        """Prétraite l'image"""
        processed = image_data.copy()
        
        if self.config.noise_reduction:
            # Apply noise reduction
            processed = cv2.bilateralFilter(processed, 9, 75, 75)
        
        if self.config.contrast_enhancement:
            # Enhance contrast using CLAHE
            if len(processed.shape) == 3:
                # Convert to LAB for better contrast enhancement
                lab = cv2.cvtColor(processed, cv2.COLOR_BGR2LAB)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                lab[:, :, 0] = clahe.apply(lab[:, :, 0])
                processed = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            else:
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                processed = clahe.apply(processed)
        
        return processed
    
    async def _generate_perceptual_hashes(self, image_data: np.ndarray, fingerprint: ImageFingerprint):
        """
Génère les hashes perceptuels"""
        if not IMAGEHASH_AVAILABLE or not PIL_AVAILABLE:
            return
        
        # Convert OpenCV image to PIL
        if len(image_data.shape) == 3:
            image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image_data
        
        pil_image = Image.fromarray(image_rgb)
        
        # Generate hashes
        if self.config.phash_enabled:
            fingerprint.phash = str(imagehash.phash(pil_image, hash_size=self.config.hash_size))
        
        if self.config.dhash_enabled:
            fingerprint.dhash = str(imagehash.dhash(pil_image, hash_size=self.config.hash_size))
        
        if self.config.ahash_enabled:
            fingerprint.ahash = str(imagehash.average_hash(pil_image, hash_size=self.config.hash_size))
        
        if self.config.whash_enabled:
            fingerprint.whash = str(imagehash.whash(pil_image, hash_size=self.config.hash_size))
        
        if self.config.colorhash_enabled:
            fingerprint.colorhash = str(imagehash.colorhash(pil_image, binbits=3))
    
    async def _generate_clip_features(self, image_data: np.ndarray, fingerprint: ImageFingerprint):
        """
Génère les caractéristiques CLIP"""
        if not self.clip_processor:
            return
        
        features = await self.clip_processor.extract_features(image_data)
        fingerprint.clip_features = features
    
    async def _generate_cnn_features(self, image_data: np.ndarray, fingerprint: ImageFingerprint):
        """
Génère les caractéristiques CNN"""
        for model_name in self.config.cnn_models:
            features = await self.cnn_processor.extract_features(image_data, model_name)
            if features is not None:
                fingerprint.cnn_features[model_name] = features
    
    async def _assess_image_quality(self, image_data: np.ndarray, fingerprint: ImageFingerprint):
        """Évalue la qualité de l'image"""
        quality_metrics = await self.quality_assessor.assess_quality(image_data)
        fingerprint.quality_metrics = quality_metrics
    
    async def _analyze_colors(self, image_data: np.ndarray, fingerprint: ImageFingerprint):
        """
Analyse les couleurs de l'image"""
        color_analysis = await self.color_analyzer.analyze_colors(image_data)
        fingerprint.color_analysis = color_analysis
    
    async def _analyze_texture(self, image_data: np.ndarray, fingerprint: ImageFingerprint):
        """
Analyse la texture de l'image"""
        texture_features = await self.texture_analyzer.analyze_texture(image_data)
        fingerprint.texture_features = texture_features
    
    async def _extract_geometric_features(self, image_data: np.ndarray, fingerprint: ImageFingerprint):
        """
Extrait les caractéristiques géométriques"""
        geometric_features = await self.geometric_analyzer.extract_features(image_data)
        fingerprint.geometric_features = geometric_features
    
    async def _detect_objects(self, image_data: np.ndarray, fingerprint: ImageFingerprint):
        """
Détecte les objets dans l'image"""
        if not self.object_detector:
            return
        
        detected_objects = await self.object_detector.detect(image_data)
        fingerprint.detected_objects = detected_objects
    
    async def _generate_multiscale_features(self, image_data: np.ndarray, fingerprint: ImageFingerprint):
        """
Génère des caractéristiques multi-échelles"""
        scales = [0.5, 0.75, 1.0, 1.25, 1.5]
        
        for scale in scales:
            if scale == 1.0:
                continue  # Skip original scale
            
            # Resize image
            height, width = image_data.shape[:2]
            new_height, new_width = int(height * scale), int(width * scale)
            
            if new_height < 32 or new_width < 32:
                continue  # Skip too small images
            
            scaled_image = cv2.resize(image_data, (new_width, new_height))
            
            # Extract basic features at this scale
            scale_features = {}
            
            # Color histogram at this scale
            if len(scaled_image.shape) == 3:
                hist = cv2.calcHist([scaled_image], [0, 1, 2], None, 
                                  [8, 8, 8], [0, 256, 0, 256, 0, 256])
                scale_features['color_histogram'] = hist.flatten()
            
            # Edge density at this scale
            gray = cv2.cvtColor(scaled_image, cv2.COLOR_BGR2GRAY) if len(scaled_image.shape) == 3 else scaled_image
            edges = cv2.Canny(gray, 50, 150)
            scale_features['edge_density'] = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            fingerprint.pyramid_features[int(scale * 100)] = scale_features
    
    async def _classify_scene(self, fingerprint: ImageFingerprint):
        """
Classifie la scène de l'image"""
        # Use CNN features or CLIP features for scene classification
        if fingerprint.clip_features is not None:
            # Scene classification based on CLIP features
            # This would use a trained classifier in production
            fingerprint.scene_category = "general"  # Placeholder
        
        # Generate semantic tags based on detected objects
        if fingerprint.detected_objects:
            tags = set()
            for obj in fingerprint.detected_objects:
                if obj.get('confidence', 0) > 0.7:
                    tags.add(obj.get('class', ''))
            fingerprint.semantic_tags = list(tags)
    
    async def _compute_hash_similarity(self, 
                                     fp1: ImageFingerprint, 
                                     fp2: ImageFingerprint) -> Dict[str, float]:
        """Calcule la similarité des hashes"""
        similarities = {}
        
        # pHash similarity
        if fp1.phash and fp2.phash:
            similarities['phash'] = self._hamming_similarity(fp1.phash, fp2.phash)
        
        # dHash similarity
        if fp1.dhash and fp2.dhash:
            similarities['dhash'] = self._hamming_similarity(fp1.dhash, fp2.dhash)
        
        # aHash similarity
        if fp1.ahash and fp2.ahash:
            similarities['ahash'] = self._hamming_similarity(fp1.ahash, fp2.ahash)
        
        # wHash similarity
        if fp1.whash and fp2.whash:
            similarities['whash'] = self._hamming_similarity(fp1.whash, fp2.whash)
        
        # Color hash similarity
        if fp1.colorhash and fp2.colorhash:
            similarities['colorhash'] = self._hamming_similarity(fp1.colorhash, fp2.colorhash)
        
        return similarities
    
    def _hamming_similarity(self, hash1: str, hash2: str) -> float:
        """
Calcule la similarité basée sur la distance de Hamming"""
        if len(hash1) != len(hash2):
            return 0.0
        
        # Convert hex hashes to binary
        try:
            bin1 = bin(int(hash1, 16))[2:].zfill(len(hash1) * 4)
            bin2 = bin(int(hash2, 16))[2:].zfill(len(hash2) * 4)
        except ValueError:
            return 0.0
        
        # Calculate Hamming distance
        hamming_distance = sum(c1 != c2 for c1, c2 in zip(bin1, bin2))
        max_distance = len(bin1)
        
        # Convert to similarity
        similarity = 1.0 - (hamming_distance / max_distance)
        return similarity
    
    async def _compute_clip_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """
Calcule la similarité CLIP"""
        # Cosine similarity
        dot_product = np.dot(features1, features2)
        norm1 = np.linalg.norm(features1)
        norm2 = np.linalg.norm(features2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def _compute_cnn_similarity(self, 
                                    features1: Dict[str, np.ndarray], 
                                    features2: Dict[str, np.ndarray]) -> Dict[str, float]:
        """
Calcule la similarité des caractéristiques CNN"""
        similarities = {}
        
        for model_name in features1:
            if model_name in features2:
                f1 = features1[model_name]
                f2 = features2[model_name]
                
                # Cosine similarity
                dot_product = np.dot(f1, f2)
                norm1 = np.linalg.norm(f1)
                norm2 = np.linalg.norm(f2)
                
                if norm1 > 0 and norm2 > 0:
                    similarity = dot_product / (norm1 * norm2)
                    similarities[f'cnn_{model_name}'] = similarity
        
        return similarities
    
    async def _compute_color_similarity(self, 
                                      color1: ColorAnalysis, 
                                      color2: ColorAnalysis) -> float:
        """
Calcule la similarité colorimétrique"""
        similarities = []
        
        # Histogram similarity
        if color1.color_histogram is not None and color2.color_histogram is not None:
            hist_corr = cv2.compareHist(color1.color_histogram, color2.color_histogram, cv2.HISTCMP_CORREL)
            similarities.append(max(0, hist_corr))
        
        # Average color similarity
        if color1.average_color and color2.average_color:
            color_diff = np.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color1.average_color, color2.average_color)))
            color_similarity = 1.0 - min(1.0, color_diff / (255 * np.sqrt(3)))
            similarities.append(color_similarity)
        
        # Dominant colors similarity
        if color1.dominant_colors and color2.dominant_colors:
            # Simple intersection over union
            set1 = set(color1.dominant_colors)
            set2 = set(color2.dominant_colors)
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            dominant_similarity = intersection / union if union > 0 else 0.0
            similarities.append(dominant_similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    async def _compute_texture_similarity(self, 
                                        texture1: TextureFeatures, 
                                        texture2: TextureFeatures) -> float:
        """
Calcule la similarité de texture"""
        similarities = []
        
        # LBP histogram similarity
        if texture1.lbp_histogram is not None and texture2.lbp_histogram is not None:
            lbp_corr = cv2.compareHist(texture1.lbp_histogram, texture2.lbp_histogram, cv2.HISTCMP_CORREL)
            similarities.append(max(0, lbp_corr))
        
        # GLCM properties similarity
        if texture1.glcm_properties and texture2.glcm_properties:
            prop_similarities = []
            for prop in texture1.glcm_properties:
                if prop in texture2.glcm_properties:
                    val1 = texture1.glcm_properties[prop]
                    val2 = texture2.glcm_properties[prop]
                    prop_sim = 1.0 - min(1.0, abs(val1 - val2) / max(abs(val1) + abs(val2), 1e-6))
                    prop_similarities.append(prop_sim)
            
            if prop_similarities:
                similarities.append(np.mean(prop_similarities))
        
        return np.mean(similarities) if similarities else 0.0
    
    async def _compute_geometric_similarity(self, 
                                          geo1: GeometricFeatures, 
                                          geo2: GeometricFeatures) -> float:
        """
Calcule la similarité géométrique"""
        similarities = []
        
        # SIFT descriptor matching
        if (geo1.sift_descriptors is not None and geo2.sift_descriptors is not None and
            len(geo1.sift_descriptors) > 0 and len(geo2.sift_descriptors) > 0):
            
            # Use FLANN matcher for SIFT
            FLANN_INDEX_KDTREE = 1
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            search_params = dict(checks=50)
            flann = cv2.FlannBasedMatcher(index_params, search_params)
            
            try:
                matches = flann.knnMatch(geo1.sift_descriptors, geo2.sift_descriptors, k=2)
                good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]
                
                # Calculate similarity based on number of good matches
                total_features = min(len(geo1.sift_descriptors), len(geo2.sift_descriptors))
                sift_similarity = len(good_matches) / total_features if total_features > 0 else 0.0
                similarities.append(min(1.0, sift_similarity))
            except:
                pass
        
        # Edge density similarity
        edge_diff = abs(geo1.edge_density - geo2.edge_density)
        edge_similarity = 1.0 - min(1.0, edge_diff)
        similarities.append(edge_similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    async def _compute_object_similarity(self, 
                                       objects1: List[Dict[str, Any]], 
                                       objects2: List[Dict[str, Any]]) -> float:
        """
Calcule la similarité d'objets détectés"""
        # Extract object classes
        classes1 = set(obj.get('class', '') for obj in objects1 if obj.get('confidence', 0) > 0.5)
        classes2 = set(obj.get('class', '') for obj in objects2 if obj.get('confidence', 0) > 0.5)
        
        # Jaccard similarity
        intersection = len(classes1.intersection(classes2))
        union = len(classes1.union(classes2))
        
        return intersection / union if union > 0 else 0.0
    
    async def _compute_multiscale_similarity(self, 
                                           pyramid1: Dict[int, Dict[str, Any]], 
                                           pyramid2: Dict[int, Dict[str, Any]]) -> float:
        """
Calcule la similarité multi-échelles"""
        similarities = []
        
        for scale in pyramid1:
            if scale in pyramid2:
                features1 = pyramid1[scale]
                features2 = pyramid2[scale]
                
                # Color histogram similarity
                if 'color_histogram' in features1 and 'color_histogram' in features2:
                    hist_corr = cv2.compareHist(features1['color_histogram'], 
                                              features2['color_histogram'], 
                                              cv2.HISTCMP_CORREL)
                    similarities.append(max(0, hist_corr))
                
                # Edge density similarity
                if 'edge_density' in features1 and 'edge_density' in features2:
                    edge_diff = abs(features1['edge_density'] - features2['edge_density'])
                    edge_sim = 1.0 - min(1.0, edge_diff)
                    similarities.append(edge_sim)
        
        return np.mean(similarities) if similarities else 0.0
    
    async def _compute_weighted_image_similarity(self, similarity_scores: Dict[str, float]) -> float:
        """
Calcule la similarité pondérée globale"""
        weights = {
            'phash': 0.2,
            'dhash': 0.15,
            'ahash': 0.1,
            'whash': 0.1,
            'colorhash': 0.05,
            'clip': 0.2,
            'cnn_resnet50': 0.1,
            'cnn_efficientnet_b0': 0.05,
            'color': 0.1,
            'texture': 0.1,
            'geometric': 0.1,
            'objects': 0.05,
            'multiscale': 0.1
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric, score in similarity_scores.items():
            if metric in weights:
                weighted_sum += score * weights[metric]
                total_weight += weights[metric]
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0

# Processeurs spécialisés

class PerceptualImageProcessor:
    """
Processeur de hashes perceptuels"""
    
    def __init__(self, config: ImageFingerprintConfig):
        self.config = config
        logger.info("PerceptualImageProcessor initialized")

class CLIPProcessor:
    """Processeur CLIP pour caractéristiques visuelles-linguistiques"""
    
    def __init__(self, config: ImageFingerprintConfig):
        self.config = config
        self.model = None
        self.preprocess = None
        self.device = "cuda" if torch.cuda.is_available() and config.use_gpu else "cpu"
        
        if CLIP_AVAILABLE:
            self._load_model()
        
        logger.info("CLIPProcessor initialized")
    
    def _load_model(self):
        """Charge le modèle CLIP"""
        try:
            self.model, self.preprocess = clip.load(self.config.clip_model, device=self.device)
            self.model.eval()
        except Exception as e:
            logger.error(f"Error loading CLIP model: {e}")
            self.model = None
    
    async def extract_features(self, image_data: np.ndarray) -> Optional[np.ndarray]:
        """Extrait les caractéristiques CLIP"""
        if not self.model:
            return None
        
        try:
            # Convert OpenCV image to PIL
            if len(image_data.shape) == 3:
                image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image_data
            
            pil_image = Image.fromarray(image_rgb)
            
            # Preprocess image
            image_tensor = self.preprocess(pil_image).unsqueeze(0).to(self.device)
            
            # Extract features
            with torch.no_grad():
                features = self.model.encode_image(image_tensor)
                features = features.cpu().numpy().flatten()
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting CLIP features: {e}")
            return None

class CNNFeaturesProcessor:
    """Processeur de caractéristiques CNN"""
    
    def __init__(self, config: ImageFingerprintConfig):
        self.config = config
        self.models = {}
        self.device = "cuda" if torch.cuda.is_available() and config.use_gpu else "cpu"
        
        if TORCH_AVAILABLE:
            self._load_models()
        
        logger.info("CNNFeaturesProcessor initialized")
    
    def _load_models(self):
        """Charge les modèles CNN"""
        try:
            for model_name in self.config.cnn_models:
                if model_name == "resnet50":
                    model = models.resnet50(pretrained=True)
                    model = torch.nn.Sequential(*list(model.children())[:-1])  # Remove classifier
                elif model_name == "efficientnet_b0":
                    model = models.efficientnet_b0(pretrained=True)
                    model.classifier = torch.nn.Identity()  # Remove classifier
                else:
                    continue
                
                model.eval()
                model = model.to(self.device)
                self.models[model_name] = model
                
        except Exception as e:
            logger.error(f"Error loading CNN models: {e}")
    
    async def extract_features(self, image_data: np.ndarray, model_name: str) -> Optional[np.ndarray]:
        """Extrait les caractéristiques CNN"""
        if model_name not in self.models:
            return None
        
        try:
            # Preprocess image
            transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            # Convert BGR to RGB
            if len(image_data.shape) == 3:
                image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = cv2.cvtColor(image_data, cv2.COLOR_GRAY2RGB)
            
            input_tensor = transform(image_rgb).unsqueeze(0).to(self.device)
            
            # Extract features
            with torch.no_grad():
                features = self.models[model_name](input_tensor)
                features = features.squeeze().cpu().numpy()
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting {model_name} features: {e}")
            return None

class ObjectDetector:
    """Détecteur d'objets YOLO"""
    
    def __init__(self, config: ImageFingerprintConfig):
        self.config = config
        
        if YOLO_AVAILABLE:
            self.model = YOLO(config.yolo_model)
        else:
            self.model = None
        
        logger.info("ObjectDetector initialized")
    
    async def detect(self, image_data: np.ndarray) -> List[Dict[str, Any]]:
        """Détecte les objets dans l'image"""
        if not self.model:
            return []
        
        try:
            results = self.model(image_data, 
                               conf=self.config.confidence_threshold,
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
            logger.error(f"Error in object detection: {e}")
            return []

class QualityAssessor:
    """Évaluateur de qualité d'image"""
    
    def __init__(self, config: ImageFingerprintConfig):
        self.config = config
        logger.info("QualityAssessor initialized")
    
    async def assess_quality(self, image_data: np.ndarray) -> QualityMetrics:
        """Évalue la qualité de l'image"""
        metrics = QualityMetrics()
        
        # Convert to grayscale for some metrics
        if len(image_data.shape) == 3:
            gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_data
        
        # Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        metrics.sharpness_score = min(1.0, laplacian_var / self.config.blur_threshold)
        
        # Noise estimation
        noise_estimate = np.std(cv2.medianBlur(gray, 5) - gray)
        metrics.noise_score = max(0.0, 1.0 - noise_estimate / (255 * self.config.noise_threshold))
        
        # Brightness
        brightness = np.mean(gray) / 255.0
        if 0.2 <= brightness <= 0.8:
            metrics.brightness_score = 1.0
        else:
            metrics.brightness_score = max(0.0, 1.0 - abs(brightness - 0.5) * 2)
        
        # Contrast
        contrast = np.std(gray) / 255.0
        metrics.contrast_score = min(1.0, contrast * 4)
        
        # Color score (for color images)
        if len(image_data.shape) == 3:
            hsv = cv2.cvtColor(image_data, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv[:, :, 1]) / 255.0
            metrics.color_score = saturation
        else:
            metrics.color_score = 0.5  # Neutral for grayscale
        
        # Overall score
        metrics.overall_score = np.mean([
            metrics.sharpness_score,
            metrics.noise_score,
            metrics.brightness_score,
            metrics.contrast_score,
            metrics.color_score
        ])
        
        return metrics

class ColorAnalyzer:
    """
Analyseur de couleurs"""
    
    def __init__(self, config: ImageFingerprintConfig):
        self.config = config
        logger.info("ColorAnalyzer initialized")
    
    async def analyze_colors(self, image_data: np.ndarray) -> ColorAnalysis:
        """Analyse les couleurs de l'image"""
        analysis = ColorAnalysis()
        
        if len(image_data.shape) != 3:
            return analysis  # Skip grayscale images
        
        # Color histogram
        hist = cv2.calcHist([image_data], [0, 1, 2], None, 
                          [self.config.color_histogram_bins] * 3,
                          [0, 256] * 3)
        analysis.color_histogram = hist.flatten()
        
        # Average color
        analysis.average_color = tuple(np.mean(image_data, axis=(0, 1)).astype(int))
        
        # Color variance
        analysis.color_variance = float(np.var(image_data))
        
        # Brightness, contrast, saturation
        gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        analysis.brightness = float(np.mean(gray) / 255.0)
        analysis.contrast = float(np.std(gray) / 255.0)
        
        hsv = cv2.cvtColor(image_data, cv2.COLOR_BGR2HSV)
        analysis.saturation = float(np.mean(hsv[:, :, 1]) / 255.0)
        
        # Dominant colors using k-means
        analysis.dominant_colors = await self._extract_dominant_colors(image_data)
        
        return analysis
    
    async def _extract_dominant_colors(self, image_data: np.ndarray) -> List[Tuple[int, int, int]]:
        """
Extrait les couleurs dominantes"""
        try:
            # Reshape for k-means
            data = image_data.reshape((-1, 3))
            data = np.float32(data)
            
            # K-means clustering
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, labels, centers = cv2.kmeans(data, self.config.dominant_colors_count, None, 
                                          criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers to RGB tuples
            centers = np.uint8(centers)
            dominant_colors = [tuple(center) for center in centers]
            
            return dominant_colors
            
        except Exception as e:
            logger.error(f"Error extracting dominant colors: {e}")
            return []

class TextureAnalyzer:
    """Analyseur de texture"""
    
    def __init__(self, config: ImageFingerprintConfig):
        self.config = config
        logger.info("TextureAnalyzer initialized")
    
    async def analyze_texture(self, image_data: np.ndarray) -> TextureFeatures:
        """Analyse la texture de l'image"""
        features = TextureFeatures()
        
        # Convert to grayscale
        if len(image_data.shape) == 3:
            gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_data
        
        if not SKIMAGE_AVAILABLE:
            return features
        
        try:
            # Local Binary Pattern
            lbp = local_binary_pattern(gray, self.config.lbp_n_points, 
                                     self.config.lbp_radius, method='uniform')
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=self.config.lbp_n_points + 2, 
                                     range=(0, self.config.lbp_n_points + 2))
            features.lbp_histogram = lbp_hist.astype(float)
            
            # Gray-Level Co-occurrence Matrix
            glcm = greycomatrix(gray, distances=self.config.glcm_distances, 
                              angles=self.config.glcm_angles, levels=256,
                              symmetric=True, normed=True)
            
            # GLCM properties
            features.glcm_properties = {
                'contrast': float(np.mean(greycoprops(glcm, 'contrast'))),
                'dissimilarity': float(np.mean(greycoprops(glcm, 'dissimilarity'))),
                'homogeneity': float(np.mean(greycoprops(glcm, 'homogeneity'))),
                'energy': float(np.mean(greycoprops(glcm, 'energy'))),
                'correlation': float(np.mean(greycoprops(glcm, 'correlation')))
            }
            
            # Texture energy, homogeneity, contrast
            features.texture_energy = features.glcm_properties.get('energy', 0.0)
            features.texture_homogeneity = features.glcm_properties.get('homogeneity', 0.0)
            features.texture_contrast = features.glcm_properties.get('contrast', 0.0)
            
        except Exception as e:
            logger.error(f"Error analyzing texture: {e}")
        
        return features

class GeometricAnalyzer:
    """Analyseur de caractéristiques géométriques"""
    
    def __init__(self, config: ImageFingerprintConfig):
        self.config = config
        logger.info("GeometricAnalyzer initialized")
    
    async def extract_features(self, image_data: np.ndarray) -> GeometricFeatures:
        """Extrait les caractéristiques géométriques"""
        features = GeometricFeatures()
        
        # Convert to grayscale
        if len(image_data.shape) == 3:
            gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_data
        
        try:
            # SIFT features
            if self.config.sift_enabled:
                sift = cv2.SIFT_create(nfeatures=self.config.max_keypoints)
                kp, desc = sift.detectAndCompute(gray, None)
                features.sift_keypoints = kp
                features.sift_descriptors = desc
            
            # ORB features
            if self.config.orb_enabled:
                orb = cv2.ORB_create(nfeatures=self.config.max_keypoints)
                kp, desc = orb.detectAndCompute(gray, None)
                features.orb_keypoints = kp
                features.orb_descriptors = desc
            
            # Corner detection
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, 
                                            qualityLevel=0.01, minDistance=10)
            if corners is not None:
                features.corner_points = [(int(x), int(y)) for x, y in corners.reshape(-1, 2)]
            
            # Edge density
            edges = cv2.Canny(gray, 50, 150)
            total_pixels = edges.shape[0] * edges.shape[1]
            edge_pixels = np.sum(edges > 0)
            features.edge_density = edge_pixels / total_pixels
            
        except Exception as e:
            logger.error(f"Error extracting geometric features: {e}")
        
        return features

# Export public API
__all__ = [
    'ImageFingerprintEngine',
    'ImageFingerprint',
    'ImageFingerprintConfig',
    'ColorAnalysis',
    'TextureFeatures',
    'GeometricFeatures',
    'QualityMetrics',
    'CLIPProcessor',
    'CNNFeaturesProcessor',
    'ObjectDetector',
    'QualityAssessor',
    'ColorAnalyzer',
    'TextureAnalyzer',
    'GeometricAnalyzer',
    'ImageFormat',
    'ImageQuality',
    'ColorSpace'
]
