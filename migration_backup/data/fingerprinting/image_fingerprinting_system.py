#!/usr/bin/env python3
"""
Image Fingerprinting System - IA Chéries Data Fingerprinting Module
================================================================
Advanced image fingerprinting system with computer vision algorithms,
perceptual hashing, deep learning features, and specialized image content 
protection for photography creators on the IA Chéries platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Data Fingerprinting
Version: 1.0 Enterprise Production
"""

import asyncio
import hashlib
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Core imports for image processing
try:
    import cv2
    import torch
    import torchvision.transforms as transforms
    from torchvision.models import resnet50, ResNet50_Weights
    import numpy as np
    from PIL import Image, ImageStat
    import imagehash
    from skimage import feature, measure, filters
    from scipy.spatial.distance import cosine, euclidean, hamming
    from sklearn.cluster import KMeans
except ImportError as e:
    logging.error(f"Required image dependencies not installed: {e}")

# IA Chéries core imports
from .multimodal_fingerprinting_engine import FingerprintResult, FingerprintConfig
from .vector_database_matching import VectorDatabaseManager
from .performance_analytics_engine import PerformanceAnalytics


class ImageFingerprintType(Enum):
    """Types of image fingerprints supported."""
    PERCEPTUAL_HASH = "perceptual_hash"
    AVERAGE_HASH = "average_hash"
    DIFFERENCE_HASH = "difference_hash"
    WAVELET_HASH = "wavelet_hash"
    COLOR_HISTOGRAM = "color_histogram"
    LBP_FEATURES = "lbp_features"
    HOG_FEATURES = "hog_features"
    SIFT_FEATURES = "sift_features"
    ORB_FEATURES = "orb_features"
    DEEP_FEATURES = "deep_features"
    EDGE_FEATURES = "edge_features"
    TEXTURE_FEATURES = "texture_features"
    COMBINED = "combined"


class ImageFormat(Enum):
    """Supported image formats."""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"
    GIF = "gif"
    SVG = "svg"
    RAW = "raw"


@dataclass
class ImageMetadata:
    """Image file metadata container."""
    width: int
    height: int
    channels: int
    file_size: int
    format: Optional[ImageFormat] = None
    color_space: Optional[str] = None
    has_transparency: bool = False
    dpi: Optional[Tuple[int, int]] = None
    compression: Optional[str] = None
    exif_data: Optional[Dict[str, Any]] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    timestamp: Optional[datetime] = None
    gps_coordinates: Optional[Tuple[float, float]] = None
    aspect_ratio: Optional[float] = None
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    saturation: Optional[float] = None
    sharpness: Optional[float] = None


@dataclass
class ImageFingerprint:
    """Image fingerprint data structure."""
    fingerprint_id: str
    fingerprint_type: ImageFingerprintType
    data: np.ndarray
    confidence: float
    metadata: ImageMetadata
    hash_value: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    processing_time: float = 0.0
    file_path: Optional[str] = None
    hash_sha256: Optional[str] = None
    additional_features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageAnalysisConfig:
    """Configuration for image analysis."""
    resize_dimensions: Tuple[int, int] = (256, 256)
    hash_size: int = 8
    histogram_bins: int = 256
    lbp_radius: int = 3
    lbp_points: int = 24
    hog_orientations: int = 9
    hog_pixels_per_cell: Tuple[int, int] = (8, 8)
    hog_cells_per_block: Tuple[int, int] = (2, 2)
    enable_deep_features: bool = True
    enable_keypoint_detection: bool = True
    quality_threshold: float = 0.7
    confidence_threshold: float = 0.8
    max_keypoints: int = 1000


class ImageFingerprintingSystem:
    """
    Advanced Image Fingerprinting System
    
    Provides comprehensive image content fingerprinting with:
    - Multiple hashing algorithms (pHash, aHash, dHash, wHash)
    - Computer vision features (SIFT, ORB, HOG, LBP)
    - Deep learning-based features
    - Color and texture analysis
    - Perceptual similarity matching
    """
    
    def __init__(self, config: Optional[ImageAnalysisConfig] = None):
        """Initialize image fingerprinting system."""
        self.config = config or ImageAnalysisConfig()
        self.logger = logging.getLogger(__name__)
        
        # Vector database for similarity matching
        self.vector_db = VectorDatabaseManager()
        self.performance_analytics = PerformanceAnalytics()
        
        # Deep learning models
        self.deep_model = None
        self.feature_extractor = None
        
        # Feature detectors
        self.sift_detector = None
        self.orb_detector = None
        
        # Initialize components
        self._initialize_models()
        
        self.logger.info("ImageFingerprintingSystem initialized successfully")
    
    def _initialize_models(self):
        """Initialize deep learning models and feature detectors."""
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
            
            if self.config.enable_keypoint_detection:
                # Initialize SIFT and ORB detectors
                try:
                    self.sift_detector = cv2.SIFT_create(nfeatures=self.config.max_keypoints)
                    self.orb_detector = cv2.ORB_create(nfeatures=self.config.max_keypoints)
                    self.logger.info("Keypoint detectors initialized successfully")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize keypoint detectors: {e}")
                    self.config.enable_keypoint_detection = False
                
        except Exception as e:
            self.logger.warning(f"Failed to initialize models: {e}")
            self.config.enable_deep_features = False
    
    async def process_image_file(
        self,
        file_path: str,
        creator_id: str,
        fingerprint_types: Optional[List[ImageFingerprintType]] = None
    ) -> List[ImageFingerprint]:
        """
        Process image file and generate multiple fingerprints.
        
        Args:
            file_path: Path to image file
            creator_id: Creator identifier for protection
            fingerprint_types: Types of fingerprints to generate
        
        Returns:
            List of generated image fingerprints
        """
        start_time = datetime.utcnow()
        
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Failed to load image file: {file_path}")
            
            # Load PIL image for additional processing
            pil_image = Image.open(file_path)
            
            # Extract metadata
            metadata = await self._extract_metadata(pil_image, image, file_path)
            
            # Generate file hash
            file_hash = await self._generate_file_hash(file_path)
            
            # Default fingerprint types
            if fingerprint_types is None:
                fingerprint_types = [
                    ImageFingerprintType.PERCEPTUAL_HASH,
                    ImageFingerprintType.COLOR_HISTOGRAM,
                    ImageFingerprintType.LBP_FEATURES,
                    ImageFingerprintType.HOG_FEATURES,
                    ImageFingerprintType.DEEP_FEATURES,
                    ImageFingerprintType.COMBINED
                ]
            
            # Generate fingerprints
            fingerprints = []
            for fp_type in fingerprint_types:
                fingerprint = await self._generate_fingerprint(
                    image=image,
                    pil_image=pil_image,
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
                'operation': 'image_fingerprinting',
                'file_path': file_path,
                'creator_id': creator_id,
                'processing_time': processing_time,
                'fingerprint_count': len(fingerprints),
                'success': True
            })
            
            self.logger.info(
                f"Generated {len(fingerprints)} fingerprints for {file_path} "
                f"in {processing_time:.2f}s"
            )
            
            return fingerprints
            
        except Exception as e:
            error_msg = f"Failed to process image file {file_path}: {e}"
            self.logger.error(error_msg)
            
            await self.performance_analytics.record_processing_metrics({
                'operation': 'image_fingerprinting',
                'file_path': file_path,
                'creator_id': creator_id,
                'processing_time': (datetime.utcnow() - start_time).total_seconds(),
                'fingerprint_count': 0,
                'success': False,
                'error': str(e)
            })
            
            raise
    
    async def _generate_fingerprint(
        self,
        image: np.ndarray,
        pil_image: Image.Image,
        fingerprint_type: ImageFingerprintType,
        metadata: ImageMetadata,
        file_path: str,
        file_hash: str
    ) -> ImageFingerprint:
        """Generate specific type of image fingerprint."""
        
        try:
            if fingerprint_type == ImageFingerprintType.PERCEPTUAL_HASH:
                data, confidence, hash_value = await self._generate_perceptual_hash(pil_image)
            
            elif fingerprint_type == ImageFingerprintType.AVERAGE_HASH:
                data, confidence, hash_value = await self._generate_average_hash(pil_image)
            
            elif fingerprint_type == ImageFingerprintType.DIFFERENCE_HASH:
                data, confidence, hash_value = await self._generate_difference_hash(pil_image)
            
            elif fingerprint_type == ImageFingerprintType.WAVELET_HASH:
                data, confidence, hash_value = await self._generate_wavelet_hash(pil_image)
            
            elif fingerprint_type == ImageFingerprintType.COLOR_HISTOGRAM:
                data, confidence = await self._generate_color_histogram(image)
                hash_value = None
            
            elif fingerprint_type == ImageFingerprintType.LBP_FEATURES:
                data, confidence = await self._generate_lbp_features(image)
                hash_value = None
            
            elif fingerprint_type == ImageFingerprintType.HOG_FEATURES:
                data, confidence = await self._generate_hog_features(image)
                hash_value = None
            
            elif fingerprint_type == ImageFingerprintType.SIFT_FEATURES:
                data, confidence = await self._generate_sift_features(image)
                hash_value = None
            
            elif fingerprint_type == ImageFingerprintType.ORB_FEATURES:
                data, confidence = await self._generate_orb_features(image)
                hash_value = None
            
            elif fingerprint_type == ImageFingerprintType.DEEP_FEATURES:
                data, confidence = await self._generate_deep_features(image)
                hash_value = None
            
            elif fingerprint_type == ImageFingerprintType.EDGE_FEATURES:
                data, confidence = await self._generate_edge_features(image)
                hash_value = None
            
            elif fingerprint_type == ImageFingerprintType.TEXTURE_FEATURES:
                data, confidence = await self._generate_texture_features(image)
                hash_value = None
            
            elif fingerprint_type == ImageFingerprintType.COMBINED:
                data, confidence = await self._generate_combined_fingerprint(image, pil_image)
                hash_value = None
            
            else:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            # Generate unique fingerprint ID
            fingerprint_id = self._generate_fingerprint_id(
                file_hash, fingerprint_type.value, data
            )
            
            return ImageFingerprint(
                fingerprint_id=fingerprint_id,
                fingerprint_type=fingerprint_type,
                data=data,
                confidence=confidence,
                metadata=metadata,
                hash_value=hash_value,
                file_path=file_path,
                hash_sha256=file_hash
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate {fingerprint_type.value} fingerprint: {e}")
            raise
    
    async def _generate_perceptual_hash(
        self, pil_image: Image.Image
    ) -> Tuple[np.ndarray, float, str]:
        """Generate perceptual hash fingerprint."""
        try:
            # Calculate perceptual hash
            phash = imagehash.phash(pil_image, hash_size=self.config.hash_size)
            
            # Convert to numpy array
            hash_array = np.array([int(x) for x in str(phash)], dtype=np.uint8)
            
            # Calculate confidence based on hash entropy
            confidence = self._calculate_hash_confidence(hash_array)
            
            return hash_array, confidence, str(phash)
            
        except Exception as e:
            self.logger.error(f"Perceptual hash generation failed: {e}")
            return np.array([]), 0.0, ""
    
    async def _generate_average_hash(
        self, pil_image: Image.Image
    ) -> Tuple[np.ndarray, float, str]:
        """Generate average hash fingerprint."""
        try:
            # Calculate average hash
            ahash = imagehash.average_hash(pil_image, hash_size=self.config.hash_size)
            
            # Convert to numpy array
            hash_array = np.array([int(x) for x in str(ahash)], dtype=np.uint8)
            
            # Calculate confidence
            confidence = self._calculate_hash_confidence(hash_array)
            
            return hash_array, confidence, str(ahash)
            
        except Exception as e:
            self.logger.error(f"Average hash generation failed: {e}")
            return np.array([]), 0.0, ""
    
    async def _generate_difference_hash(
        self, pil_image: Image.Image
    ) -> Tuple[np.ndarray, float, str]:
        """Generate difference hash fingerprint."""
        try:
            # Calculate difference hash
            dhash = imagehash.dhash(pil_image, hash_size=self.config.hash_size)
            
            # Convert to numpy array
            hash_array = np.array([int(x) for x in str(dhash)], dtype=np.uint8)
            
            # Calculate confidence
            confidence = self._calculate_hash_confidence(hash_array)
            
            return hash_array, confidence, str(dhash)
            
        except Exception as e:
            self.logger.error(f"Difference hash generation failed: {e}")
            return np.array([]), 0.0, ""
    
    async def _generate_wavelet_hash(
        self, pil_image: Image.Image
    ) -> Tuple[np.ndarray, float, str]:
        """Generate wavelet hash fingerprint."""
        try:
            # Calculate wavelet hash
            whash = imagehash.whash(pil_image, hash_size=self.config.hash_size)
            
            # Convert to numpy array
            hash_array = np.array([int(x) for x in str(whash)], dtype=np.uint8)
            
            # Calculate confidence
            confidence = self._calculate_hash_confidence(hash_array)
            
            return hash_array, confidence, str(whash)
            
        except Exception as e:
            self.logger.error(f"Wavelet hash generation failed: {e}")
            return np.array([]), 0.0, ""
    
    async def _generate_color_histogram(
        self, image: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Generate color histogram fingerprint."""
        try:
            # Convert to different color spaces
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            # Calculate histograms
            hist_features = []
            
            # HSV histograms
            for channel in range(3):
                hist = cv2.calcHist([hsv], [channel], None, [self.config.histogram_bins], [0, 256])
                hist = hist.flatten() / (hist.sum() + 1e-10)
                hist_features.extend(hist)
            
            # LAB histograms
            for channel in range(3):
                hist = cv2.calcHist([lab], [channel], None, [self.config.histogram_bins], [0, 256])
                hist = hist.flatten() / (hist.sum() + 1e-10)
                hist_features.extend(hist)
            
            features = np.array(hist_features)
            
            # Calculate confidence
            confidence = self._calculate_histogram_confidence(features)
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"Color histogram generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_lbp_features(
        self, image: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Generate Local Binary Pattern features."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate LBP
            lbp = feature.local_binary_pattern(
                gray, self.config.lbp_points, self.config.lbp_radius, method='uniform'
            )
            
            # Calculate LBP histogram
            hist, _ = np.histogram(lbp.ravel(), bins=self.config.lbp_points + 2, 
                                  range=(0, self.config.lbp_points + 2))
            hist = hist.astype(float) / (hist.sum() + 1e-10)
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(hist)
            
            return hist, confidence
            
        except Exception as e:
            self.logger.error(f"LBP features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_hog_features(
        self, image: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Generate Histogram of Oriented Gradients features."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Resize image for consistent HOG features
            resized = cv2.resize(gray, self.config.resize_dimensions)
            
            # Calculate HOG features
            hog_features = feature.hog(
                resized,
                orientations=self.config.hog_orientations,
                pixels_per_cell=self.config.hog_pixels_per_cell,
                cells_per_block=self.config.hog_cells_per_block,
                visualize=False,
                feature_vector=True
            )
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(hog_features)
            
            return hog_features, confidence
            
        except Exception as e:
            self.logger.error(f"HOG features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_sift_features(
        self, image: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Generate SIFT features."""
        try:
            if not self.config.enable_keypoint_detection or self.sift_detector is None:
                return np.array([]), 0.0
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect keypoints and compute descriptors
            keypoints, descriptors = self.sift_detector.detectAndCompute(gray, None)
            
            if descriptors is None or len(descriptors) == 0:
                return np.array([]), 0.0
            
            # Aggregate descriptors using bag-of-words approach
            if len(descriptors) > 50:
                # Use K-means to create visual vocabulary
                n_clusters = min(50, len(descriptors))
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(descriptors)
                
                # Create histogram of visual words
                hist, _ = np.histogram(cluster_labels, bins=n_clusters, range=(0, n_clusters))
                features = hist.astype(float) / (hist.sum() + 1e-10)
            else:
                # Use mean and std of descriptors
                features = np.concatenate([
                    np.mean(descriptors, axis=0),
                    np.std(descriptors, axis=0)
                ])
            
            # Calculate confidence based on number of keypoints
            confidence = min(1.0, len(keypoints) / 100.0)
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"SIFT features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_orb_features(
        self, image: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Generate ORB features."""
        try:
            if not self.config.enable_keypoint_detection or self.orb_detector is None:
                return np.array([]), 0.0
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect keypoints and compute descriptors
            keypoints, descriptors = self.orb_detector.detectAndCompute(gray, None)
            
            if descriptors is None or len(descriptors) == 0:
                return np.array([]), 0.0
            
            # Aggregate descriptors
            if len(descriptors) > 50:
                # Use K-means clustering
                n_clusters = min(50, len(descriptors))
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(descriptors.astype(float))
                
                # Create histogram
                hist, _ = np.histogram(cluster_labels, bins=n_clusters, range=(0, n_clusters))
                features = hist.astype(float) / (hist.sum() + 1e-10)
            else:
                # Use statistical measures
                features = np.concatenate([
                    np.mean(descriptors.astype(float), axis=0),
                    np.std(descriptors.astype(float), axis=0)
                ])
            
            # Calculate confidence
            confidence = min(1.0, len(keypoints) / 100.0)
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"ORB features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_deep_features(
        self, image: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Generate deep learning-based features."""
        try:
            if not self.config.enable_deep_features or self.feature_extractor is None:
                return np.array([]), 0.0
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Preprocess image
            preprocess = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            input_tensor = preprocess(rgb_image).unsqueeze(0)
            
            # Extract features
            with torch.no_grad():
                features = self.feature_extractor(input_tensor)
                features = features.view(features.size(0), -1)
                features = features.squeeze().numpy()
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features)
            
            return features, confidence
            
        except Exception as e:
            self.logger.error(f"Deep features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_edge_features(
        self, image: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Generate edge-based features."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate different edge features
            features = []
            
            # Canny edges
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            features.append(edge_density)
            
            # Sobel edges
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            gradient_direction = np.arctan2(sobel_y, sobel_x)
            
            features.extend([
                np.mean(gradient_magnitude),
                np.std(gradient_magnitude),
                np.mean(gradient_direction),
                np.std(gradient_direction)
            ])
            
            # Laplacian edges
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            features.extend([
                np.mean(np.abs(laplacian)),
                np.std(laplacian)
            ])
            
            # Edge orientation histogram
            orientation_hist, _ = np.histogram(gradient_direction.ravel(), bins=36, range=(-np.pi, np.pi))
            orientation_hist = orientation_hist.astype(float) / (orientation_hist.sum() + 1e-10)
            features.extend(orientation_hist)
            
            features_array = np.array(features)
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features_array)
            
            return features_array, confidence
            
        except Exception as e:
            self.logger.error(f"Edge features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_texture_features(
        self, image: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Generate texture-based features."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            features = []
            
            # GLCM features (Gray Level Co-occurrence Matrix)
            from skimage.feature import greycomatrix, greycoprops
            
            # Calculate GLCM
            glcm = greycomatrix(gray, distances=[1], angles=[0, 45, 90, 135], levels=256, symmetric=True, normed=True)
            
            # Extract GLCM properties
            properties = ['dissimilarity', 'correlation', 'homogeneity', 'energy']
            for prop in properties:
                prop_values = greycoprops(glcm, prop)
                features.extend([
                    np.mean(prop_values),
                    np.std(prop_values)
                ])
            
            # Gabor filter responses
            gabor_features = []
            for theta in range(0, 180, 45):
                for frequency in [0.1, 0.3, 0.5]:
                    filtered_real, _ = filters.gabor(gray, frequency=frequency, theta=np.deg2rad(theta))
                    gabor_features.extend([
                        np.mean(filtered_real),
                        np.std(filtered_real)
                    ])
            
            features.extend(gabor_features)
            
            features_array = np.array(features)
            
            # Calculate confidence
            confidence = self._calculate_feature_confidence(features_array)
            
            return features_array, confidence
            
        except Exception as e:
            self.logger.error(f"Texture features generation failed: {e}")
            return np.array([]), 0.0
    
    async def _generate_combined_fingerprint(
        self, image: np.ndarray, pil_image: Image.Image
    ) -> Tuple[np.ndarray, float]:
        """Generate combined fingerprint from multiple features."""
        try:
            features_list = []
            confidences = []
            
            # Generate multiple fingerprints
            fingerprint_types = [
                (ImageFingerprintType.PERCEPTUAL_HASH, True),
                (ImageFingerprintType.COLOR_HISTOGRAM, False),
                (ImageFingerprintType.LBP_FEATURES, False),
                (ImageFingerprintType.HOG_FEATURES, False)
            ]
            
            for fp_type, use_pil in fingerprint_types:
                try:
                    if fp_type == ImageFingerprintType.PERCEPTUAL_HASH:
                        features, confidence, _ = await self._generate_perceptual_hash(pil_image)
                    elif fp_type == ImageFingerprintType.COLOR_HISTOGRAM:
                        features, confidence = await self._generate_color_histogram(image)
                    elif fp_type == ImageFingerprintType.LBP_FEATURES:
                        features, confidence = await self._generate_lbp_features(image)
                    elif fp_type == ImageFingerprintType.HOG_FEATURES:
                        features, confidence = await self._generate_hog_features(image)
                    
                    if len(features) > 0:
                        features_list.append(features)
                        confidences.append(confidence)
                except Exception as e:
                    self.logger.warning(f"Failed to generate {fp_type.value} for combined fingerprint: {e}")
            
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
    
    async def _extract_metadata(
        self, pil_image: Image.Image, cv_image: np.ndarray, file_path: str
    ) -> ImageMetadata:
        """Extract comprehensive image metadata."""
        try:
            # Basic image properties
            width, height = pil_image.size
            channels = len(cv_image.shape) if len(cv_image.shape) == 2 else cv_image.shape[2]
            file_size = Path(file_path).stat().st_size
            
            # Format detection
            format_str = pil_image.format.lower() if pil_image.format else Path(file_path).suffix.lower().lstrip('.')
            image_format = None
            try:
                image_format = ImageFormat(format_str)
            except ValueError:
                pass
            
            # Aspect ratio
            aspect_ratio = width / height if height > 0 else 0
            
            # Color space
            color_space = pil_image.mode
            
            # Transparency
            has_transparency = pil_image.mode in ('RGBA', 'LA') or 'transparency' in pil_image.info
            
            # DPI information
            dpi = pil_image.info.get('dpi', None)
            
            # EXIF data
            exif_data = None
            camera_make = None
            camera_model = None
            timestamp = None
            gps_coordinates = None
            
            try:
                from PIL.ExifTags import TAGS, GPSTAGS
                exif = pil_image._getexif()
                if exif:
                    exif_data = {}
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                        
                        if tag == 'Make':
                            camera_make = str(value)
                        elif tag == 'Model':
                            camera_model = str(value)
                        elif tag == 'DateTime':
                            try:
                                timestamp = datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
                            except ValueError:
                                pass
                        elif tag == 'GPSInfo':
                            gps_coordinates = self._parse_gps_coordinates(value)
            except Exception as e:
                self.logger.debug(f"EXIF extraction failed: {e}")
            
            # Image quality metrics
            brightness, contrast, saturation = self._calculate_image_quality(cv_image)
            
            return ImageMetadata(
                width=width,
                height=height,
                channels=channels,
                file_size=file_size,
                format=image_format,
                color_space=color_space,
                has_transparency=has_transparency,
                dpi=dpi,
                exif_data=exif_data,
                camera_make=camera_make,
                camera_model=camera_model,
                timestamp=timestamp,
                gps_coordinates=gps_coordinates,
                aspect_ratio=aspect_ratio,
                brightness=brightness,
                contrast=contrast,
                saturation=saturation
            )
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            return ImageMetadata(
                width=0,
                height=0,
                channels=0,
                file_size=0
            )
    
    def _parse_gps_coordinates(self, gps_info: Dict) -> Optional[Tuple[float, float]]:
        """Parse GPS coordinates from EXIF data."""
        try:
            from PIL.ExifTags import GPSTAGS
            
            if not gps_info:
                return None
            
            gps_data = {}
            for key, value in gps_info.items():
                gps_tag = GPSTAGS.get(key, key)
                gps_data[gps_tag] = value
            
            def convert_to_degrees(value):
                d, m, s = value
                return d + (m / 60.0) + (s / 3600.0)
            
            lat = convert_to_degrees(gps_data.get('GPSLatitude', [0, 0, 0]))
            lon = convert_to_degrees(gps_data.get('GPSLongitude', [0, 0, 0]))
            
            if gps_data.get('GPSLatitudeRef') == 'S':
                lat = -lat
            if gps_data.get('GPSLongitudeRef') == 'W':
                lon = -lon
            
            return (lat, lon) if lat != 0 or lon != 0 else None
            
        except Exception:
            return None
    
    def _calculate_image_quality(self, image: np.ndarray) -> Tuple[float, float, float]:
        """Calculate basic image quality metrics."""
        try:
            # Convert to different color spaces
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Brightness (mean of luminance)
            brightness = np.mean(gray) / 255.0
            
            # Contrast (standard deviation of luminance)
            contrast = np.std(gray) / 255.0
            
            # Saturation (mean of saturation channel)
            saturation = np.mean(hsv[:, :, 1]) / 255.0
            
            return brightness, contrast, saturation
            
        except Exception:
            return 0.0, 0.0, 0.0
    
    def _calculate_hash_confidence(self, hash_array: np.ndarray) -> float:
        """Calculate confidence based on hash entropy."""
        try:
            if len(hash_array) == 0:
                return 0.0
            
            # Calculate entropy
            unique_values, counts = np.unique(hash_array, return_counts=True)
            probabilities = counts / len(hash_array)
            entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
            
            # Normalize to [0, 1]
            max_entropy = np.log2(len(unique_values))
            confidence = entropy / max_entropy if max_entropy > 0 else 0.0
            
            return min(1.0, max(0.0, confidence))
            
        except Exception:
            return 0.0
    
    def _calculate_histogram_confidence(self, hist: np.ndarray) -> float:
        """Calculate confidence based on histogram distribution."""
        try:
            if len(hist) == 0:
                return 0.0
            
            # Calculate uniformity (lower is better for distinctiveness)
            uniformity = np.sum((hist - np.mean(hist))**2) / len(hist)
            confidence = min(1.0, uniformity * 1000)  # Scale factor
            
            return max(0.0, confidence)
            
        except Exception:
            return 0.0
    
    def _calculate_feature_confidence(self, features: np.ndarray) -> float:
        """Calculate confidence based on feature variance."""
        try:
            if len(features) == 0:
                return 0.0
            
            # Calculate coefficient of variation
            mean_val = np.mean(np.abs(features))
            std_val = np.std(features)
            
            if mean_val == 0:
                return 0.0
            
            cv = std_val / mean_val
            confidence = min(1.0, cv)  # Higher variance = higher confidence
            
            return max(0.0, confidence)
            
        except Exception:
            return 0.0
    
    async def _generate_file_hash(self, file_path: str) -> str:
        """Generate SHA-256 hash of image file."""
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
        self, fingerprints: List[ImageFingerprint], creator_id: str
    ):
        """Store fingerprints in vector database."""
        try:
            for fingerprint in fingerprints:
                await self.vector_db.store_fingerprint(
                    fingerprint_id=fingerprint.fingerprint_id,
                    vector=fingerprint.data,
                    metadata={
                        'type': 'image',
                        'subtype': fingerprint.fingerprint_type.value,
                        'creator_id': creator_id,
                        'confidence': fingerprint.confidence,
                        'dimensions': f"{fingerprint.metadata.width}x{fingerprint.metadata.height}",
                        'file_size': fingerprint.metadata.file_size,
                        'format': fingerprint.metadata.format.value if fingerprint.metadata.format else None,
                        'hash_value': fingerprint.hash_value,
                        'file_path': fingerprint.file_path,
                        'hash': fingerprint.hash_sha256,
                        'created_at': fingerprint.created_at.isoformat()
                    }
                )
        except Exception as e:
            self.logger.error(f"Failed to store fingerprints: {e}")
            raise
    
    async def find_similar_images(
        self,
        fingerprint: ImageFingerprint,
        similarity_threshold: float = 0.85,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Find similar image content based on fingerprint."""
        try:
            # Search in vector database
            results = await self.vector_db.search_similar(
                vector=fingerprint.data,
                threshold=similarity_threshold,
                max_results=max_results,
                metadata_filter={'type': 'image', 'subtype': fingerprint.fingerprint_type.value}
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Similarity search failed: {e}")
            return []
    
    async def compare_image_hashes(
        self, hash1: str, hash2: str, hash_type: ImageFingerprintType
    ) -> float:
        """Compare two image hashes and return similarity score."""
        try:
            if hash_type in [
                ImageFingerprintType.PERCEPTUAL_HASH,
                ImageFingerprintType.AVERAGE_HASH,
                ImageFingerprintType.DIFFERENCE_HASH,
                ImageFingerprintType.WAVELET_HASH
            ]:
                # Calculate Hamming distance for binary hashes
                if len(hash1) != len(hash2):
                    return 0.0
                
                hamming_dist = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
                similarity = 1.0 - (hamming_dist / len(hash1))
                
                return similarity
            else:
                self.logger.warning(f"Hash comparison not supported for {hash_type.value}")
                return 0.0
                
        except Exception as e:
            self.logger.error(f"Hash comparison failed: {e}")
            return 0.0
    
    async def analyze_image_quality(self, fingerprint: ImageFingerprint) -> Dict[str, float]:
        """Analyze image quality metrics."""
        try:
            quality_metrics = {
                'confidence': fingerprint.confidence,
                'resolution_score': self._calculate_resolution_score(
                    fingerprint.metadata.width, fingerprint.metadata.height
                ),
                'file_size_score': min(1.0, fingerprint.metadata.file_size / (1024 * 1024)),  # 1MB baseline
                'aspect_ratio_score': self._calculate_aspect_ratio_score(fingerprint.metadata.aspect_ratio),
                'brightness_score': 1.0 - abs(0.5 - (fingerprint.metadata.brightness or 0.5)),
                'contrast_score': fingerprint.metadata.contrast or 0.5,
                'feature_completeness': 1.0 if len(fingerprint.data) > 0 else 0.0
            }
            
            # Overall quality score
            quality_metrics['overall_quality'] = np.mean(list(quality_metrics.values()))
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed: {e}")
            return {'overall_quality': 0.0}
    
    def _calculate_resolution_score(self, width: int, height: int) -> float:
        """Calculate score based on image resolution."""
        try:
            total_pixels = width * height
            
            # Resolution scoring
            if total_pixels >= 3840 * 2160:  # 4K
                return 1.0
            elif total_pixels >= 1920 * 1080:  # 1080p
                return 0.8
            elif total_pixels >= 1280 * 720:  # 720p
                return 0.6
            elif total_pixels >= 640 * 480:  # VGA
                return 0.4
            else:
                return 0.2
                
        except Exception:
            return 0.0
    
    def _calculate_aspect_ratio_score(self, aspect_ratio: Optional[float]) -> float:
        """Calculate score based on aspect ratio."""
        try:
            if aspect_ratio is None:
                return 0.5
            
            # Common aspect ratios
            common_ratios = [1.0, 4/3, 3/2, 16/9, 16/10, 21/9]
            
            # Find closest common ratio
            min_diff = min(abs(aspect_ratio - ratio) for ratio in common_ratios)
            
            # Score based on how close to common ratio
            score = 1.0 - min(1.0, min_diff * 2)
            
            return max(0.0, score)
            
        except Exception:
            return 0.5


# Factory function for creating image fingerprinting system
def create_image_fingerprinting_system(
    config: Optional[ImageAnalysisConfig] = None
) -> ImageFingerprintingSystem:
    """Create and initialize image fingerprinting system."""
    return ImageFingerprintingSystem(config)


# Export public interface
__all__ = [
    'ImageFingerprintingSystem',
    'ImageFingerprint',
    'ImageFingerprintType',
    'ImageFormat',
    'ImageMetadata',
    'ImageAnalysisConfig',
    'create_image_fingerprinting_system'
]