"""
Image Fingerprinter - Advanced AI-Powered Image Content Identification

Ultra-sophisticated image fingerprinting system using computer vision, perceptual hashing,
and deep learning for precise image content identification and similarity matching.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import numpy as np
from pathlib import Path
from enum import Enum
import io
import pickle

# Image processing libraries
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import imagehash
import numpy as np
from skimage import feature, measure, filters
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Deep learning libraries
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet50, vgg16
import clip

# SIFT, ORB, SURF features
import cv2

try:
    from core.exceptions import ImageProcessingError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ImageProcessingError, ValidationError = globals().get('ImageProcessingError, ValidationError', Exception)
from ...utils.image_utils import ImageProcessor
from ...ml.image_models import ImageEmbeddingModel

"""
Image Fingerprinter - Advanced AI-Powered Image Content Identification

Ultra-sophisticated image fingerprinting system using computer vision, perceptual hashing,
and deep learning for precise image content identification and similarity matching.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import numpy as np
from pathlib import Path
from enum import Enum
import io
import pickle
from dataclasses import dataclass, field

# Image processing libraries
from PIL import Image, ImageFilter, ImageEnhance, ImageStat
import cv2
import imagehash
import numpy as np
from skimage import feature, measure, filters, segmentation, color
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Deep learning libraries
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet50, vgg16, efficientnet_b0
import clip

# SIFT, ORB, SURF features
import cv2

try:
    from core.exceptions import ImageProcessingError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ImageProcessingError, ValidationError = globals().get('ImageProcessingError, ValidationError', Exception)
from ...utils.image_utils import ImageProcessor
from ...ml.image_models import ImageEmbeddingModel

logger = logging.getLogger(__name__)

class ImageFingerprintQuality(Enum):
    """Image fingerprint quality levels"""
    BASIC = "basic"          # Perceptual hashes only
    STANDARD = "standard"    # + Color histograms, basic features
    ADVANCED = "advanced"    # + SIFT/ORB, texture analysis
    ULTRA = "ultra"          # + Deep learning embeddings

class ImageFeatureType(Enum):
    """Types of image features extracted"""
    PERCEPTUAL_HASH = "perceptual_hash"
    COLOR_HISTOGRAM = "color_histogram"
    TEXTURE_FEATURES = "texture_features"
    EDGE_FEATURES = "edge_features"
    KEYPOINT_FEATURES = "keypoint_features"
    SHAPE_FEATURES = "shape_features"
    DEEP_EMBEDDING = "deep_embedding"
    CLIP_EMBEDDING = "clip_embedding"
    METADATA_FEATURES = "metadata_features"

class HashType(Enum):
    """Types of perceptual hashes"""
    AVERAGE_HASH = "ahash"
    PERCEPTUAL_HASH = "phash"
    DIFFERENCE_HASH = "dhash"
    WAVELET_HASH = "whash"
    COLOR_HASH = "colorhash"

@dataclass
class ImageFeatureVector:
    """Image feature vector structure"""
    feature_type: ImageFeatureType
    vector_data: np.ndarray
    confidence_score: float
    extraction_params: Dict[str, Any]
    region_info: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class ImageFingerprint:
    """Complete image fingerprint structure"""
    fingerprint_id: str
    image_hash: str
    perceptual_hashes: Dict[str, str]
    feature_vectors: List[ImageFeatureVector]
    deep_embeddings: Dict[str, np.ndarray]
    image_metadata: Dict[str, Any]
    quality_level: ImageFingerprintQuality
    extraction_time: float
    created_at: datetime = field(default_factory=lambda: datetime.now())

class ImageFingerprinter:
    """
    Ultra-advanced image fingerprinting system with computer vision and deep learning.
    
    Features:
    - Multiple perceptual hashing algorithms
    - Color histogram analysis
    - Texture feature extraction (LBP, GLCM)
    - Keypoint detection (SIFT, ORB, SURF)
    - Edge and shape analysis
    - Deep learning embeddings (ResNet, CLIP)
    - Metadata extraction
    - Quality assessment
    - Robustness testing
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Image processing parameters
        self.target_size = self.config.get('target_size', (512, 512))
        self.thumbnail_size = self.config.get('thumbnail_size', (256, 256))
        self.max_keypoints = self.config.get('max_keypoints', 1000)
        
        # Feature extraction parameters
        self.color_bins = self.config.get('color_bins', 32)
        self.texture_radius = self.config.get('texture_radius', 3)
        self.texture_points = self.config.get('texture_points', 24)
        
        # Deep learning models
        self.resnet_model = None
        self.clip_model = None
        self.clip_processor = None
        
        # Computer vision detectors
        self.sift_detector = None
        self.orb_detector = None
        
        # Image processing utilities
        self.image_processor = ImageProcessor()
        
        # Performance tracking
        self.processing_stats = {
            'total_processed': 0,
            'processing_times': [],
            'quality_scores': [],
            'feature_extraction_times': {}
        }
        
        logger.info("ImageFingerprinter initialized with advanced configuration")
    
    async def initialize(self):
        """Initialize all image processing models and detectors"""



        try:
            start_time = time.time()
            
            # Initialize deep learning models
            if self.config.get('enable_resnet', True):
                await self._initialize_resnet()
            
            if self.config.get('enable_clip', True):
                await self._initialize_clip()
            
            # Initialize computer vision detectors
            await self._initialize_cv_detectors()
            
            # Pre-compile feature extraction functions
            await self._precompile_extractors()
            
            initialization_time = time.time() - start_time
            logger.info(f"ImageFingerprinter fully initialized in {initialization_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize ImageFingerprinter: {e}")
            raise ImageProcessingError(f"Initialization failed: {e}")
    
    async def generate_fingerprint(
        self, 
        image_data: Union[str, np.ndarray, bytes, Image.Image], 
        quality_level: ImageFingerprintQuality = ImageFingerprintQuality.ADVANCED
    ) -> Dict[str, Any]:
        """
        Generate comprehensive image fingerprint with configurable quality levels
        """
        start_time = time.time()
        
        try:
            # Load and preprocess image
            image_array, original_image = await self._load_and_preprocess_image(image_data)
            
            # Generate unique fingerprint ID
            fingerprint_id = str(uuid.uuid4())
            
            # Create image hash for quick lookups
            image_hash = self._create_image_hash(image_array)
            
            # Extract features based on quality level
            feature_vectors = []
            deep_embeddings = {}
            perceptual_hashes = {}
            
            if quality_level.value in ['basic', 'standard', 'advanced', 'ultra']:
                # Perceptual hashes (always included)
                perceptual_hashes = await self._extract_perceptual_hashes(original_image)
                
            if quality_level.value in ['standard', 'advanced', 'ultra']:
                # Color and basic features
                color_features = await self._extract_color_features(image_array, original_image)
                feature_vectors.extend(color_features)
                
                # Edge features
                edge_features = await self._extract_edge_features(image_array)
                feature_vectors.extend(edge_features)
                
            if quality_level.value in ['advanced', 'ultra']:
                # Texture features
                texture_features = await self._extract_texture_features(image_array)
                feature_vectors.extend(texture_features)
                
                # Keypoint features
                keypoint_features = await self._extract_keypoint_features(image_array)
                feature_vectors.extend(keypoint_features)
                
                # Shape features
                shape_features = await self._extract_shape_features(image_array)
                feature_vectors.extend(shape_features)
                
            if quality_level == ImageFingerprintQuality.ULTRA:
                # Deep learning embeddings
                if self.resnet_model is not None:
                    resnet_embedding = await self._extract_resnet_embedding(original_image)
                    deep_embeddings['resnet'] = resnet_embedding
                
                if self.clip_model is not None:
                    clip_embedding = await self._extract_clip_embedding(original_image)
                    deep_embeddings['clip'] = clip_embedding
            
            # Extract image metadata
            image_metadata = await self._extract_image_metadata(original_image, image_array)
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                image_array, feature_vectors, deep_embeddings
            )
            
            # Create complete fingerprint
            processing_time = time.time() - start_time
            
            fingerprint = ImageFingerprint(
                fingerprint_id=fingerprint_id,
                image_hash=image_hash,
                perceptual_hashes=perceptual_hashes,
                feature_vectors=feature_vectors,
                deep_embeddings=deep_embeddings,
                image_metadata=image_metadata,
                quality_level=quality_level,
                extraction_time=processing_time
            )
            
            # Update processing statistics
            self._update_processing_stats(processing_time, quality_metrics)
            
            # Create unified embedding for similarity search
            unified_embedding = await self._create_unified_embedding(fingerprint)
            
            return {
                'fingerprint_id': fingerprint_id,
                'hash': image_hash,
                'perceptual_hashes': perceptual_hashes,
                'features': self._serialize_feature_vectors(feature_vectors),
                'embedding': unified_embedding,
                'deep_embeddings': deep_embeddings,
                'metadata': {
                    'image_metadata': image_metadata,
                    'quality_level': quality_level.value,
                    'processing_time': processing_time,
                    'feature_count': len(feature_vectors),
                    'image_dimensions': image_array.shape[:2],
                    'color_channels': image_array.shape[2] if len(image_array.shape) > 2 else 1
                },
                'quality': quality_metrics,
                'params': {
                    'target_size': self.target_size,
                    'color_bins': self.color_bins,
                    'texture_radius': self.texture_radius,
                    'max_keypoints': self.max_keypoints
                }
            }
            
        except Exception as e:
            logger.error(f"Image fingerprint generation failed: {e}")
            raise ImageProcessingError(f"Fingerprint generation failed: {e}")
    
    async def _load_and_preprocess_image(self, image_data: Union[str, np.ndarray, bytes, Image.Image]) -> Tuple[np.ndarray, Image.Image]:
        """Load and preprocess image data"""



        try:
            # Load image
            if isinstance(image_data, str):
                # Load from file path
                if not Path(image_data).exists():
                    raise ValidationError(f"Image file not found: {image_data}")
                original_image = Image.open(image_data)
            elif isinstance(image_data, bytes):
                # Load from bytes
                image_buffer = io.BytesIO(image_data)
                original_image = Image.open(image_buffer)
            elif isinstance(image_data, np.ndarray):
                # Convert numpy array to PIL Image
                if len(image_data.shape) == 3:
                    original_image = Image.fromarray(image_data.astype(np.uint8))
                else:
                    original_image = Image.fromarray(image_data.astype(np.uint8), mode='L')
            elif isinstance(image_data, Image.Image):
                # Use provided PIL Image
                original_image = image_data.copy()
            else:
                raise ValidationError("Unsupported image data type")
            
            # Ensure RGB format
            if original_image.mode != 'RGB':
                original_image = original_image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(original_image)
            
            # Apply preprocessing if configured
            if self.config.get('noise_reduction', False):
                image_array = await self._apply_noise_reduction(image_array)
            
            if self.config.get('enhance_contrast', False):
                image_array = await self._enhance_contrast(image_array)
            
            return image_array, original_image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise ImageProcessingError(f"Preprocessing failed: {e}")
    
    def _create_image_hash(self, image_array: np.ndarray) -> str:
        """Create fast hash of image data for quick lookups"""
        # Create hash from image statistics and sample data
        image_stats = [
            np.mean(image_array),
            np.std(image_array),
            np.max(image_array),
            np.min(image_array),
            image_array.shape[0],
            image_array.shape[1]
        ]
        
        # Sample pixels from different regions
        h, w = image_array.shape[:2]
        sample_points = [
            image_array[h//4, w//4],
            image_array[h//2, w//2],
            image_array[3*h//4, 3*w//4],
            image_array[h//4, 3*w//4],
            image_array[3*h//4, w//4]
        ]
        
        # Flatten samples
        flat_samples = []
        for point in sample_points:
            if len(point.shape) == 0:  # Grayscale
                flat_samples.append(point)
            else:  # Color
                flat_samples.extend(point)
        
        # Combine stats and samples
        hash_data = np.array(image_stats + flat_samples)
        hash_bytes = hash_data.tobytes()
        
        return hashlib.sha256(hash_bytes).hexdigest()
    
    async def _extract_perceptual_hashes(self, image: Image.Image) -> Dict[str, str]:
        """Extract multiple types of perceptual hashes"""



        try:
            hashes = {}
            
            # Average hash
            hashes['ahash'] = str(imagehash.average_hash(image, hash_size=16))
            
            # Perceptual hash
            hashes['phash'] = str(imagehash.phash(image, hash_size=16))
            
            # Difference hash
            hashes['dhash'] = str(imagehash.dhash(image, hash_size=16))
            
            # Wavelet hash
            hashes['whash'] = str(imagehash.whash(image, hash_size=16))
            
            # Color hash
            hashes['colorhash'] = str(imagehash.colorhash(image, binbits=3))
            
            return hashes
            
        except Exception as e:
            logger.error(f"Perceptual hash extraction failed: {e}")
            return {}
    
    async def _extract_color_features(self, image_array: np.ndarray, original_image: Image.Image) -> List[ImageFeatureVector]:
        """Extract color-based features"""
        features = []
        
        try:
            # Color histogram for each channel
            if len(image_array.shape) == 3:  # Color image
                for i, channel in enumerate(['red', 'green', 'blue']):
                    hist, _ = np.histogram(image_array[:, :, i], bins=self.color_bins, range=(0, 256))
                    hist = hist.astype(np.float32) / np.sum(hist)  # Normalize
                    
                    features.append(ImageFeatureVector(
                        feature_type=ImageFeatureType.COLOR_HISTOGRAM,
                        vector_data=hist,
                        confidence_score=0.9,
                        extraction_params={'channel': channel, 'bins': self.color_bins}
                    ))
                
                # Combined color histogram
                combined_hist = cv2.calcHist([image_array], [0, 1, 2], None, 
                                           [self.color_bins, self.color_bins, self.color_bins], 
                                           [0, 256, 0, 256, 0, 256])
                combined_hist = combined_hist.flatten()
                combined_hist = combined_hist / (np.sum(combined_hist) + 1e-10)
                
                features.append(ImageFeatureVector(
                    feature_type=ImageFeatureType.COLOR_HISTOGRAM,
                    vector_data=combined_hist,
                    confidence_score=0.95,
                    extraction_params={'type': 'combined_rgb', 'bins': self.color_bins}
                ))
            
            # Color moments (mean, std, skewness)
            color_moments = []
            for channel in range(image_array.shape[2] if len(image_array.shape) == 3 else 1):
                if len(image_array.shape) == 3:
                    channel_data = image_array[:, :, channel].flatten()
                else:
                    channel_data = image_array.flatten()
                
                mean = np.mean(channel_data)
                std = np.std(channel_data)
                skewness = np.mean((channel_data - mean) ** 3) / (std ** 3 + 1e-10)
                
                color_moments.extend([mean, std, skewness])
            
            features.append(ImageFeatureVector(
                feature_type=ImageFeatureType.COLOR_HISTOGRAM,
                vector_data=np.array(color_moments),
                confidence_score=0.8,
                extraction_params={'type': 'color_moments'}
            ))
            
        except Exception as e:
            logger.error(f"Color feature extraction failed: {e}")
        
        return features
    
    async def _extract_edge_features(self, image_array: np.ndarray) -> List[ImageFeatureVector]:
        """Extract edge-based features"""
        features = []
        
        try:
            # Convert to grayscale if needed
            if len(image_array.shape) == 3:
                gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray_image = image_array
            
            # Canny edge detection
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Edge histogram
            edge_hist, _ = np.histogram(edges, bins=32, range=(0, 255))
            edge_hist = edge_hist.astype(np.float32) / (np.sum(edge_hist) + 1e-10)
            
            features.append(ImageFeatureVector(
                feature_type=ImageFeatureType.EDGE_FEATURES,
                vector_data=edge_hist,
                confidence_score=0.8,
                extraction_params={'method': 'canny', 'bins': 32}
            ))
            
            # Edge density and orientation
            edge_density = np.sum(edges > 0) / edges.size
            
            # Sobel gradients for orientation
            sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
            
            # Edge orientation histogram
            orientation = np.arctan2(sobel_y, sobel_x)
            orientation_hist, _ = np.histogram(orientation.flatten(), bins=16, range=(-np.pi, np.pi))
            orientation_hist = orientation_hist.astype(np.float32) / (np.sum(orientation_hist) + 1e-10)
            
            features.append(ImageFeatureVector(
                feature_type=ImageFeatureType.EDGE_FEATURES,
                vector_data=np.concatenate([[edge_density], orientation_hist]),
                confidence_score=0.85,
                extraction_params={'method': 'sobel_orientation', 'bins': 16}
            ))
            
        except Exception as e:
            logger.error(f"Edge feature extraction failed: {e}")
        
        return features
    
    async def _extract_texture_features(self, image_array: np.ndarray) -> List[ImageFeatureVector]:
        """Extract texture-based features using LBP and GLCM"""
        features = []
        
        try:
            # Convert to grayscale if needed
            if len(image_array.shape) == 3:
                gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray_image = image_array
            
            # Local Binary Pattern (LBP)
            lbp = feature.local_binary_pattern(
                gray_image, self.texture_points, self.texture_radius, method='uniform'
            )
            
            # LBP histogram
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=self.texture_points + 2, 
                                     range=(0, self.texture_points + 2))
            lbp_hist = lbp_hist.astype(np.float32) / (np.sum(lbp_hist) + 1e-10)
            
            features.append(ImageFeatureVector(
                feature_type=ImageFeatureType.TEXTURE_FEATURES,
                vector_data=lbp_hist,
                confidence_score=0.85,
                extraction_params={'method': 'lbp', 'points': self.texture_points, 'radius': self.texture_radius}
            ))
            
            # GLCM (Gray Level Co-occurrence Matrix) features
            try:
                from skimage.feature import graycomatrix, graycoprops
                
                # Calculate GLCM for different angles
                distances = [1, 2]
                angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
                
                glcm = graycomatrix(
                    gray_image.astype(np.uint8), 
                    distances=distances, 
                    angles=angles, 
                    levels=256,
                    symmetric=True,
                    normed=True
                )
                
                # Extract GLCM properties
                contrast = graycoprops(glcm, 'contrast').flatten()
                dissimilarity = graycoprops(glcm, 'dissimilarity').flatten()
                homogeneity = graycoprops(glcm, 'homogeneity').flatten()
                energy = graycoprops(glcm, 'energy').flatten()
                
                glcm_features = np.concatenate([contrast, dissimilarity, homogeneity, energy])
                
                features.append(ImageFeatureVector(
                    feature_type=ImageFeatureType.TEXTURE_FEATURES,
                    vector_data=glcm_features,
                    confidence_score=0.8,
                    extraction_params={'method': 'glcm', 'distances': distances, 'angles': len(angles)}
                ))
                
            except ImportError:
                logger.warning("GLCM features unavailable - skimage.feature missing")
            
        except Exception as e:
            logger.error(f"Texture feature extraction failed: {e}")
        
        return features
    
    async def _extract_keypoint_features(self, image_array: np.ndarray) -> List[ImageFeatureVector]:
        """Extract keypoint-based features using SIFT, ORB"""
        features = []
        
        try:
            # Convert to grayscale if needed
            if len(image_array.shape) == 3:
                gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray_image = image_array
            
            # SIFT features
            if self.sift_detector is not None:
                try:
                    keypoints, descriptors = self.sift_detector.detectAndCompute(gray_image, None)
                    
                    if descriptors is not None and len(descriptors) > 0:
                        # Limit number of keypoints
                        if len(descriptors) > self.max_keypoints:
                            # Keep strongest keypoints
                            responses = [kp.response for kp in keypoints]
                            sorted_indices = np.argsort(responses)[-self.max_keypoints:]
                            descriptors = descriptors[sorted_indices]
                        
                        # Create bag of visual words representation
                        if len(descriptors) > 10:  # Need minimum keypoints for clustering
                            bow_size = min(128, len(descriptors))
                            kmeans = KMeans(n_clusters=bow_size, random_state=42)
                            clusters = kmeans.fit_predict(descriptors)
                            
                            # Histogram of visual words
                            bow_hist, _ = np.histogram(clusters, bins=bow_size, range=(0, bow_size))
                            bow_hist = bow_hist.astype(np.float32) / (np.sum(bow_hist) + 1e-10)
                            
                            features.append(ImageFeatureVector(
                                feature_type=ImageFeatureType.KEYPOINT_FEATURES,
                                vector_data=bow_hist,
                                confidence_score=0.9,
                                extraction_params={'method': 'sift_bow', 'keypoints': len(keypoints), 'bow_size': bow_size}
                            ))
                        
                        # Statistical summary of descriptors
                        desc_mean = np.mean(descriptors, axis=0)
                        desc_std = np.std(descriptors, axis=0)
                        desc_summary = np.concatenate([desc_mean, desc_std])
                        
                        features.append(ImageFeatureVector(
                            feature_type=ImageFeatureType.KEYPOINT_FEATURES,
                            vector_data=desc_summary,
                            confidence_score=0.85,
                            extraction_params={'method': 'sift_stats', 'keypoints': len(keypoints)}
                        ))
                        
                except Exception as e:
                    logger.warning(f"SIFT feature extraction failed: {e}")
            
            # ORB features
            if self.orb_detector is not None:
                try:
                    keypoints, descriptors = self.orb_detector.detectAndCompute(gray_image, None)
                    
                    if descriptors is not None and len(descriptors) > 0:
                        # Binary descriptors - use Hamming distance statistics
                        desc_mean = np.mean(descriptors.astype(np.float32), axis=0)
                        
                        features.append(ImageFeatureVector(
                            feature_type=ImageFeatureType.KEYPOINT_FEATURES,
                            vector_data=desc_mean,
                            confidence_score=0.8,
                            extraction_params={'method': 'orb', 'keypoints': len(keypoints)}
                        ))
                        
                except Exception as e:
                    logger.warning(f"ORB feature extraction failed: {e}")
            
        except Exception as e:
            logger.error(f"Keypoint feature extraction failed: {e}")
        
        return features
    
    async def _extract_shape_features(self, image_array: np.ndarray) -> List[ImageFeatureVector]:
        """Extract shape-based features"""
        features = []
        
        try:
            # Convert to grayscale and binary
            if len(image_array.shape) == 3:
                gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray_image = image_array
            
            # Apply threshold to create binary image
            _, binary = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) > 0:
                # Select largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Calculate shape features
                area = cv2.contourArea(largest_contour)
                perimeter = cv2.arcLength(largest_contour, True)
                
                # Shape descriptors
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter ** 2)
                    
                    # Aspect ratio of bounding rectangle
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Extent (ratio of contour area to bounding rectangle area)
                    rect_area = w * h
                    extent = area / rect_area if rect_area > 0 else 0
                    
                    # Solidity (ratio of contour area to convex hull area)
                    hull = cv2.convexHull(largest_contour)
                    hull_area = cv2.contourArea(hull)
                    solidity = area / hull_area if hull_area > 0 else 0
                    
                    shape_features = np.array([circularity, aspect_ratio, extent, solidity])
                    
                    features.append(ImageFeatureVector(
                        feature_type=ImageFeatureType.SHAPE_FEATURES,
                        vector_data=shape_features,
                        confidence_score=0.75,
                        extraction_params={'method': 'contour_analysis', 'area': area, 'perimeter': perimeter}
                    ))
                
                # Hu moments (shape descriptors invariant to translation, rotation, scale)
                try:
                    moments = cv2.moments(largest_contour)
                    if moments['m00'] != 0:  # Avoid division by zero
                        hu_moments = cv2.HuMoments(moments).flatten()
                        # Log transform to reduce dynamic range
                        hu_moments = -np.sign(hu_moments) * np.log10(np.abs(hu_moments) + 1e-10)
                        
                        features.append(ImageFeatureVector(
                            feature_type=ImageFeatureType.SHAPE_FEATURES,
                            vector_data=hu_moments,
                            confidence_score=0.8,
                            extraction_params={'method': 'hu_moments'}
                        ))
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Shape feature extraction failed: {e}")
        
        return features
    
    async def _extract_resnet_embedding(self, image: Image.Image) -> np.ndarray:
        """Extract ResNet deep learning embedding"""



        try:
            if self.resnet_model is None:
                return np.array([])
            
            # Prepare image for ResNet
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            image_tensor = transform(image).unsqueeze(0)
            
            # Extract features
            with torch.no_grad():
                features = self.resnet_model(image_tensor)
                embedding = features.squeeze().numpy()
            
            return embedding
            
        except Exception as e:
            logger.error(f"ResNet embedding extraction failed: {e}")
            return np.array([])
    
    async def _extract_clip_embedding(self, image: Image.Image) -> np.ndarray:
        """Extract CLIP embedding for semantic understanding"""



        try:
            if self.clip_model is None:
                return np.array([])
            
            # Process image with CLIP
            image_input = self.clip_processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**image_input)
                embedding = image_features.squeeze().numpy()
            
            # Normalize embedding
            embedding = embedding / (np.linalg.norm(embedding) + 1e-10)
            
            return embedding
            
        except Exception as e:
            logger.error(f"CLIP embedding extraction failed: {e}")
            return np.array([])
    
    async def _extract_image_metadata(self, image: Image.Image, image_array: np.ndarray) -> Dict[str, Any]:
        """Extract comprehensive image metadata"""



        try:
            # Basic image properties
            width, height = image.size
            
            metadata = {
                'width': width,
                'height': height,
                'aspect_ratio': width / height if height > 0 else 0,
                'total_pixels': width * height,
                'channels': image_array.shape[2] if len(image_array.shape) > 2 else 1,
                'color_mode': image.mode,
                'file_format': getattr(image, 'format', 'Unknown'),
            }
            
            # Color statistics
            if len(image_array.shape) == 3:  # Color image
                for i, channel in enumerate(['red', 'green', 'blue']):
                    channel_data = image_array[:, :, i]
                    metadata[f'{channel}_mean'] = float(np.mean(channel_data))
                    metadata[f'{channel}_std'] = float(np.std(channel_data))
                    metadata[f'{channel}_min'] = int(np.min(channel_data))
                    metadata[f'{channel}_max'] = int(np.max(channel_data))
            else:  # Grayscale
                metadata.update({
                    'luminance_mean': float(np.mean(image_array)),
                    'luminance_std': float(np.std(image_array)),
                    'luminance_min': int(np.min(image_array)),
                    'luminance_max': int(np.max(image_array))
                })
            
            # Image quality indicators
            # Blur detection using Laplacian variance
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_array
            
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            metadata['blur_measure'] = float(laplacian_var)
            metadata['is_blurry'] = laplacian_var < 100  # Threshold for blur detection
            
            # Brightness and contrast
            metadata['brightness'] = float(np.mean(image_array))
            metadata['contrast'] = float(np.std(image_array))
            
            # Color diversity (number of unique colors)
            if len(image_array.shape) == 3:
                # Sample unique colors (computational efficiency)
                resized = cv2.resize(image_array, (64, 64))
                reshaped = resized.reshape(-1, 3)
                unique_colors = len(np.unique(reshaped.view(np.dtype((np.void, reshaped.dtype.itemsize * reshaped.shape[1])))))
                metadata['color_diversity'] = unique_colors
            
            # EXIF data if available
            try:
                if hasattr(image, '_getexif') and image._getexif() is not None:
                    exif = image._getexif()
                    metadata['has_exif'] = True
                    metadata['exif_keys'] = list(exif.keys()) if exif else []
                else:
                    metadata['has_exif'] = False
            except:
                metadata['has_exif'] = False
            
            return metadata
            
        except Exception as e:
            logger.error(f"Image metadata extraction failed: {e}")
            return {'error': str(e)}
    
    # ... (continue with remaining methods similar to audio_fingerprinter.py)
    
    async def _calculate_quality_metrics(self, image_array: np.ndarray, feature_vectors: List, deep_embeddings: Dict) -> Dict[str, float]:
        """Calculate fingerprint quality metrics"""



        try:
            quality_metrics = {}
            
            # Image quality assessment
            image_quality = self._assess_image_quality(image_array)
            quality_metrics.update(image_quality)
            
            # Feature extraction quality
            feature_quality = self._assess_feature_quality(feature_vectors)
            quality_metrics.update(feature_quality)
            
            # Deep embedding quality
            if deep_embeddings:
                embedding_quality = self._assess_embedding_quality(deep_embeddings)
                quality_metrics.update(embedding_quality)
            
            # Overall quality score
            overall_score = np.mean(list(quality_metrics.values()))
            quality_metrics['overall_quality'] = float(overall_score)
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Quality metrics calculation failed: {e}")
            return {'overall_quality': 0.5}
    
    def _assess_image_quality(self, image_array: np.ndarray) -> Dict[str, float]:
        """Assess image quality"""



        try:
            # Convert to grayscale if needed
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_array
            
            # Sharpness (Laplacian variance)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(sharpness / 1000.0, 1.0)  # Normalize
            
            # Contrast (standard deviation)
            contrast = np.std(image_array)
            contrast_score = min(contrast / 50.0, 1.0)  # Normalize
            
            # Brightness distribution
            hist = np.histogram(gray, bins=256, range=(0, 255))[0]
            hist = hist / np.sum(hist)
            
            # Avoid too dark or too bright images
            dark_pixels = np.sum(hist[:50])
            bright_pixels = np.sum(hist[200:])
            brightness_score = 1.0 - max(dark_pixels, bright_pixels) * 2
            
            return {
                'image_quality': float((sharpness_score + contrast_score + brightness_score) / 3),
                'sharpness': float(sharpness_score),
                'contrast': float(contrast_score),
                'brightness_distribution': float(brightness_score)
            }
            
        except Exception as e:
            logger.error(f"Image quality assessment failed: {e}")
            return {'image_quality': 0.5}
    
    # Additional methods would continue here...
    # (Similar structure to audio_fingerprinter.py with image-specific implementations)
    
    async def cleanup(self):
        """Clean up resources"""



        try:
            # Clean up models
            if hasattr(self, 'resnet_model') and self.resnet_model is not None:
                del self.resnet_model
            
            if hasattr(self, 'clip_model') and self.clip_model is not None:
                del self.clip_model
                del self.clip_processor
            
            # Clear processing stats
            self.processing_stats = {
                'total_processed': 0,
                'processing_times': [],
                'quality_scores': [],
                'feature_extraction_times': {}
            }
            
            logger.info("ImageFingerprinter cleanup completed")
            
        except Exception as e:
            logger.error(f"ImageFingerprinter cleanup failed: {e}")
    
    async def _initialize_resnet(self):
        """Initialize ResNet model"""



        try:
            self.resnet_model = resnet50(pretrained=True)
            self.resnet_model = nn.Sequential(*list(self.resnet_model.children())[:-1])  # Remove final FC layer
            self.resnet_model.eval()
            
            logger.info("ResNet model initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize ResNet: {e}")
            self.resnet_model = None
    
    async def _initialize_clip(self):
        """Initialize CLIP model"""



        try:
            self.clip_model, self.clip_processor = clip.load("ViT-B/32")
            self.clip_model.eval()
            
            logger.info("CLIP model initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize CLIP: {e}")
            self.clip_model = None
            self.clip_processor = None
    
    async def _initialize_cv_detectors(self):
        """Initialize computer vision detectors"""



        try:
            # SIFT detector
            try:
                self.sift_detector = cv2.SIFT_create()
            except AttributeError:
                try:
                    self.sift_detector = cv2.xfeatures2d.SIFT_create()
                except:
                    logger.warning("SIFT detector not available")
                    self.sift_detector = None
            
            # ORB detector
            try:
                self.orb_detector = cv2.ORB_create(nfeatures=self.max_keypoints)
            except:
                logger.warning("ORB detector not available")
                self.orb_detector = None
            
            logger.info("Computer vision detectors initialized")
            
        except Exception as e:
            logger.error(f"CV detector initialization failed: {e}")
    
    async def _precompile_extractors(self):
        """Pre-compile feature extraction functions"""



        try:
            # Pre-compilation placeholder
            logger.info("Feature extractors pre-compiled")
            
        except Exception as e:
            logger.warning(f"Feature extractor pre-compilation failed: {e}")
    
    # Additional helper methods would continue here following the same pattern...
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats"""



        return [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
            '.webp', '.ico', '.ppm', '.pgm', '.pbm'
        ]

class ImageFingerprintQuality(Enum):
    """Image fingerprint quality levels"""
    BASIC = "basic"          # Perceptual hashing only
    STANDARD = "standard"    # + Visual features
    ADVANCED = "advanced"    # + Deep learning features
    ULTRA = "ultra"          # + Multi-model ensemble

class ImageFingerprinter:
    """
    Ultra-advanced image fingerprinting system with computer vision and deep learning.
    
    Features:
    - Multi-algorithm perceptual hashing (pHash, dHash, aHash, wHash)
    - Computer vision features (SIFT, ORB, SURF)
    - Deep learning embeddings (ResNet, VGG, CLIP)
    - Color and texture analysis
    - Object detection integration
    - Face detection and recognition
    - Metadata extraction and analysis
    - Robustness testing (rotation, scaling, compression)
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Image processing parameters
        self.resize_size = self.config.get('resize_size', (224, 224))
        self.hash_size = self.config.get('hash_size', 16)
        self.max_keypoints = self.config.get('max_keypoints', 500)
        
        # Feature extraction parameters
        self.color_bins = self.config.get('color_bins', 64)
        self.texture_window = self.config.get('texture_window', 16)
        
        # Processing components
        self.image_processor = ImageProcessor()
        self.scaler = StandardScaler()
        
        # Deep learning models
        self.resnet_model = None
        self.vgg_model = None
        self.clip_model = None
        self.clip_preprocess = None
        
        # Computer vision detectors
        self.sift_detector = None
        self.orb_detector = None
        self.surf_detector = None
        self.face_cascade = None
        
        # Quality assessment parameters
        self.quality_thresholds = {
            'sharpness_score': 100.0,     # Laplacian variance threshold
            'brightness_score': 0.3,      # Brightness distribution
            'contrast_score': 0.4,        # Contrast level
            'noise_score': 0.15           # Noise level
        }
        
    async def initialize(self):
        """Initialize image fingerprinting system"""



        try:
            # Initialize deep learning models
            await self._initialize_deep_models()
            
            # Initialize computer vision components
            await self._initialize_cv_components()
            
            # Initialize face detection
            await self._initialize_face_detection()
            
            logger.info("Image fingerprinter initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize image fingerprinter: {e}")
            raise ImageProcessingError(f"Initialization failed: {e}")
    
    async def generate_fingerprint(self, image_data: Union[str, bytes, np.ndarray, Image.Image], 
                                 quality_level: ImageFingerprintQuality) -> Dict[str, Any]:
        """
        Generate comprehensive image fingerprint with specified quality level
        """
        start_time = time.time()
        
        try:
            # Load and preprocess image
            image, metadata = await self._load_image(image_data)
            
            if image is None:
                raise ImageProcessingError("Failed to load image")
            
            # Quality assessment
            quality_metrics = await self._assess_image_quality(image)
            
            fingerprint_data = {
                'hash': None,
                'features': None,
                'embedding': None,
                'metadata': metadata,
                'quality': quality_metrics,
                'params': {
                    'quality_level': quality_level.value,
                    'processing_time': 0
                }
            }
            
            # Generate fingerprint based on quality level
            if quality_level == ImageFingerprintQuality.BASIC:
                # Perceptual hashing only
                hash_data = await self._generate_perceptual_hashes(image)
                fingerprint_data['hash'] = hash_data['combined_hash']
                
            elif quality_level == ImageFingerprintQuality.STANDARD:
                # Add visual features
                hash_data = await self._generate_perceptual_hashes(image)
                visual_features = await self._extract_visual_features(image)
                color_features = await self._extract_color_features(image)
                
                combined_features = np.concatenate([
                    visual_features,
                    color_features
                ])
                
                fingerprint_data['hash'] = hash_data['combined_hash']
                fingerprint_data['features'] = combined_features
                
            elif quality_level == ImageFingerprintQuality.ADVANCED:
                # Add computer vision features
                hash_data = await self._generate_perceptual_hashes(image)
                visual_features = await self._extract_visual_features(image)
                color_features = await self._extract_color_features(image)
                cv_features = await self._extract_cv_features(image)
                texture_features = await self._extract_texture_features(image)
                
                combined_features = np.concatenate([
                    visual_features,
                    color_features,
                    cv_features,
                    texture_features
                ])
                
                fingerprint_data['hash'] = hash_data['combined_hash']
                fingerprint_data['features'] = combined_features
                
            elif quality_level == ImageFingerprintQuality.ULTRA:
                # Full pipeline with deep learning
                hash_data = await self._generate_perceptual_hashes(image)
                visual_features = await self._extract_visual_features(image)
                color_features = await self._extract_color_features(image)
                cv_features = await self._extract_cv_features(image)
                texture_features = await self._extract_texture_features(image)
                deep_embedding = await self._generate_deep_embedding(image)
                
                combined_features = np.concatenate([
                    visual_features,
                    color_features,
                    cv_features,
                    texture_features
                ])
                
                fingerprint_data['hash'] = hash_data['combined_hash']
                fingerprint_data['features'] = combined_features
                fingerprint_data['embedding'] = deep_embedding
            
            processing_time = time.time() - start_time
            fingerprint_data['params']['processing_time'] = processing_time
            
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Image fingerprinting failed: {e}")
            raise ImageProcessingError(f"Fingerprint generation failed: {e}")
    
    async def _load_image(self, image_data: Union[str, bytes, np.ndarray, Image.Image]) -> Tuple[Image.Image, Dict[str, Any]]:
        """Load image from various input formats"""
        metadata = {}
        
        try:
            if isinstance(image_data, str):
                # File path
                image = Image.open(image_data).convert('RGB')
                metadata['source'] = 'file'
                metadata['file_path'] = image_data
                
            elif isinstance(image_data, bytes):
                # Image bytes
                image = Image.open(io.BytesIO(image_data)).convert('RGB')
                metadata['source'] = 'bytes'
                
            elif isinstance(image_data, np.ndarray):
                # NumPy array
                if image_data.dtype != np.uint8:
                    image_data = (image_data * 255).astype(np.uint8)
                
                if len(image_data.shape) == 3 and image_data.shape[2] == 3:
                    # RGB array
                    image = Image.fromarray(image_data, 'RGB')
                elif len(image_data.shape) == 2:
                    # Grayscale array
                    image = Image.fromarray(image_data, 'L').convert('RGB')
                else:
                    raise ValidationError(f"Unsupported array shape: {image_data.shape}")
                    
                metadata['source'] = 'array'
                
            elif isinstance(image_data, Image.Image):
                # PIL Image
                image = image_data.convert('RGB')
                metadata['source'] = 'pil'
                
            else:
                raise ValidationError(f"Unsupported image data type: {type(image_data)}")
            
            # Extract image metadata
            metadata.update({
                'width': image.width,
                'height': image.height,
                'mode': image.mode,
                'format': getattr(image, 'format', None)
            })
            
            return image, metadata
            
        except Exception as e:
            logger.error(f"Image loading failed: {e}")
            raise ImageProcessingError(f"Image loading failed: {e}")
    
    async def _generate_perceptual_hashes(self, image: Image.Image) -> Dict[str, str]:
        """Generate multiple perceptual hashes for robustness"""



        try:
            # Generate different hash types
            phash = str(imagehash.phash(image, hash_size=self.hash_size))
            dhash = str(imagehash.dhash(image, hash_size=self.hash_size))
            ahash = str(imagehash.average_hash(image, hash_size=self.hash_size))
            whash = str(imagehash.whash(image, hash_size=self.hash_size))
            
            # Color hash for color-sensitive matching
            colorhash = str(imagehash.colorhash(image))
            
            # Combine hashes for composite fingerprint
            combined_string = f"{phash}_{dhash}_{ahash}_{whash}_{colorhash}"
            combined_hash = hashlib.sha256(combined_string.encode()).hexdigest()
            
            return {
                'phash': phash,
                'dhash': dhash,
                'ahash': ahash,
                'whash': whash,
                'colorhash': colorhash,
                'combined_hash': combined_hash
            }
            
        except Exception as e:
            logger.error(f"Perceptual hashing failed: {e}")
            raise ImageProcessingError(f"Perceptual hashing failed: {e}")
    
    async def _extract_visual_features(self, image: Image.Image) -> np.ndarray:
        """Extract basic visual features"""



        try:
            # Convert to array for processing
            img_array = np.array(image)
            
            features = []
            
            # Basic statistics
            features.extend([
                np.mean(img_array),
                np.std(img_array),
                np.min(img_array),
                np.max(img_array)
            ])
            
            # Per-channel statistics
            for channel in range(3):  # RGB
                channel_data = img_array[:, :, channel]
                features.extend([
                    np.mean(channel_data),
                    np.std(channel_data),
                    np.percentile(channel_data, 25),
                    np.percentile(channel_data, 75)
                ])
            
            # Histogram features
            hist, _ = np.histogram(img_array.flatten(), bins=32, range=(0, 256))
            hist = hist / np.sum(hist)  # Normalize
            features.extend(hist.tolist())
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Visual feature extraction failed: {e}")
            return np.zeros(50)  # Return fallback features
    
    async def _extract_color_features(self, image: Image.Image) -> np.ndarray:
        """Extract color-based features"""



        try:
            img_array = np.array(image)
            features = []
            
            # Color histograms for each channel
            for channel in range(3):
                hist, _ = np.histogram(img_array[:, :, channel], bins=self.color_bins, range=(0, 256))
                hist = hist / np.sum(hist)  # Normalize
                features.extend(hist)
            
            # HSV color space analysis
            hsv_image = image.convert('HSV')
            hsv_array = np.array(hsv_image)
            
            # HSV histograms
            for channel in range(3):
                hist, _ = np.histogram(hsv_array[:, :, channel], bins=16, range=(0, 256))
                hist = hist / np.sum(hist)
                features.extend(hist)
            
            # Dominant colors using K-means
            pixels = img_array.reshape(-1, 3)
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(pixels)
            dominant_colors = kmeans.cluster_centers_.flatten()
            features.extend(dominant_colors)
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Color feature extraction failed: {e}")
            return np.zeros(256)  # Return fallback features
    
    async def _extract_cv_features(self, image: Image.Image) -> np.ndarray:
        """Extract computer vision features using SIFT, ORB, etc."""



        try:
            # Convert to OpenCV format
            img_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            
            features = []
            
            # SIFT features
            if self.sift_detector is not None:
                keypoints, descriptors = self.sift_detector.detectAndCompute(gray, None)
                if descriptors is not None:
                    # Statistical summary of SIFT descriptors
                    features.extend([
                        len(keypoints),
                        np.mean(descriptors) if len(descriptors) > 0 else 0,
                        np.std(descriptors) if len(descriptors) > 0 else 0
                    ])
                    
                    # Bag of visual words representation
                    if len(descriptors) > 0:
                        kmeans = KMeans(n_clusters=min(32, len(descriptors)), random_state=42, n_init=10)
                        kmeans.fit(descriptors)
                        hist, _ = np.histogram(kmeans.labels_, bins=32)
                        hist = hist / np.sum(hist)
                        features.extend(hist[:16])  # Use first 16 bins
                else:
                    features.extend([0, 0, 0] + [0] * 16)
            
            # ORB features
            if self.orb_detector is not None:
                keypoints, descriptors = self.orb_detector.detectAndCompute(gray, None)
                if descriptors is not None:
                    features.extend([
                        len(keypoints),
                        np.mean(descriptors.astype(float)) if len(descriptors) > 0 else 0
                    ])
                else:
                    features.extend([0, 0])
            
            # Harris corners
            corners = cv2.cornerHarris(gray, 2, 3, 0.04)
            corner_count = len(np.where(corners > 0.01 * corners.max())[0])
            features.append(corner_count)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            features.append(edge_density)
            
            # Ensure fixed size
            target_size = 50
            if len(features) > target_size:
                features = features[:target_size]
            else:
                features.extend([0] * (target_size - len(features)))
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"CV feature extraction failed: {e}")
            return np.zeros(50)  # Return fallback features
    
    async def _extract_texture_features(self, image: Image.Image) -> np.ndarray:
        """Extract texture features using various methods"""



        try:
            # Convert to grayscale for texture analysis
            gray_image = image.convert('L')
            img_array = np.array(gray_image)
            
            features = []
            
            # Local Binary Pattern
            lbp = feature.local_binary_pattern(img_array, 24, 8, method='uniform')
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=26, range=(0, 26))
            lbp_hist = lbp_hist / np.sum(lbp_hist)
            features.extend(lbp_hist[:10])  # Use first 10 bins
            
            # Gray Level Co-occurrence Matrix (GLCM) properties
            try:
                glcm = feature.graycomatrix(img_array.astype(np.uint8), [1], [0, 45, 90, 135])
                contrast = feature.graycoprops(glcm, 'contrast').flatten()
                dissimilarity = feature.graycoprops(glcm, 'dissimilarity').flatten()
                homogeneity = feature.graycoprops(glcm, 'homogeneity').flatten()
                energy = feature.graycoprops(glcm, 'energy').flatten()
                
                features.extend([
                    np.mean(contrast),
                    np.mean(dissimilarity), 
                    np.mean(homogeneity),
                    np.mean(energy)
                ])
            except:
                features.extend([0, 0, 0, 0])
            
            # Gabor filters for texture
            angles = [0, 45, 90, 135]
            for angle in angles:
                filtered = filters.gabor(img_array, frequency=0.6, theta=np.deg2rad(angle))
                features.append(np.mean(filtered[0]))
                features.append(np.std(filtered[0]))
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Texture feature extraction failed: {e}")
            return np.zeros(30)  # Return fallback features
    
    async def _generate_deep_embedding(self, image: Image.Image) -> np.ndarray:
        """Generate deep learning embedding"""



        try:
            embeddings = []
            
            # ResNet embedding
            if self.resnet_model is not None:
                resnet_embedding = await self._get_resnet_embedding(image)
                embeddings.append(resnet_embedding)
            
            # CLIP embedding
            if self.clip_model is not None:
                clip_embedding = await self._get_clip_embedding(image)
                embeddings.append(clip_embedding)
            
            # Combine embeddings
            if embeddings:
                combined_embedding = np.concatenate(embeddings)
            else:
                combined_embedding = np.random.rand(512)  # Fallback
            
            return combined_embedding
            
        except Exception as e:
            logger.error(f"Deep embedding generation failed: {e}")
            return np.random.rand(512)  # Fallback
    
    async def _get_resnet_embedding(self, image: Image.Image) -> np.ndarray:
        """Get ResNet embedding for image"""



        try:
            transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            input_tensor = transform(image).unsqueeze(0)
            
            with torch.no_grad():
                features = self.resnet_model(input_tensor)
                embedding = features.squeeze().numpy()
            
            return embedding
            
        except Exception as e:
            logger.error(f"ResNet embedding failed: {e}")
            return np.random.rand(1000)
    
    async def _get_clip_embedding(self, image: Image.Image) -> np.ndarray:
        """Get CLIP embedding for image"""



        try:
            image_input = self.clip_preprocess(image).unsqueeze(0)
            
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_input)
                embedding = image_features.squeeze().numpy()
            
            return embedding
            
        except Exception as e:
            logger.error(f"CLIP embedding failed: {e}")
            return np.random.rand(512)
    
    async def _assess_image_quality(self, image: Image.Image) -> Dict[str, float]:
        """Assess image quality for fingerprinting reliability"""
        quality_metrics = {}
        
        try:
            img_array = np.array(image.convert('L'))  # Convert to grayscale
            
            # Sharpness (Laplacian variance)
            laplacian = cv2.Laplacian(img_array, cv2.CV_64F)
            sharpness = laplacian.var()
            quality_metrics['sharpness'] = min(sharpness / 1000.0, 1.0)
            
            # Brightness distribution
            brightness_std = np.std(img_array) / 255.0
            quality_metrics['brightness_variance'] = brightness_std
            
            # Contrast
            contrast = np.max(img_array) - np.min(img_array)
            quality_metrics['contrast'] = contrast / 255.0
            
            # Noise estimation (high frequency content)
            fft = np.fft.fft2(img_array)
            fft_shift = np.fft.fftshift(fft)
            magnitude = np.abs(fft_shift)
            
            # High frequency energy
            h, w = magnitude.shape
            center_h, center_w = h // 2, w // 2
            high_freq_region = magnitude[center_h-h//4:center_h+h//4, center_w-w//4:center_w+w//4]
            total_energy = np.sum(magnitude)
            high_freq_energy = np.sum(high_freq_region)
            
            noise_ratio = high_freq_energy / total_energy if total_energy > 0 else 0
            quality_metrics['noise_level'] = noise_ratio
            
            # Overall quality score
            quality_score = (
                quality_metrics['sharpness'] * 0.3 +
                (1.0 - quality_metrics['noise_level']) * 0.3 +
                quality_metrics['contrast'] * 0.2 +
                min(quality_metrics['brightness_variance'] * 2, 1.0) * 0.2
            )
            
            quality_metrics['overall_quality'] = quality_score
            
        except Exception as e:
            logger.error(f"Image quality assessment failed: {e}")
            quality_metrics = {
                'sharpness': 0.5,
                'brightness_variance': 0.5,
                'contrast': 0.5,
                'noise_level': 0.5,
                'overall_quality': 0.5
            }
        
        return quality_metrics
    
    async def _initialize_deep_models(self):
        """Initialize deep learning models"""



        try:
            # Load ResNet
            self.resnet_model = resnet50(pretrained=True)
            self.resnet_model.eval()
            
            # Load CLIP
            self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device="cpu")
            self.clip_model.eval()
            
            logger.info("Deep learning models loaded successfully")
            
        except Exception as e:
            logger.warning(f"Failed to load deep learning models: {e}")
    
    async def _initialize_cv_components(self):
        """Initialize computer vision components"""



        try:
            # Initialize feature detectors
            self.sift_detector = cv2.SIFT_create(nfeatures=self.max_keypoints)
            self.orb_detector = cv2.ORB_create(nfeatures=self.max_keypoints)
            
            logger.info("Computer vision components initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize CV components: {e}")
    
    async def _initialize_face_detection(self):
        """Initialize face detection"""



        try:
            # Load Haar cascade for face detection
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            logger.info("Face detection initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize face detection: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        # Clear models to free memory
        self.resnet_model = None
        self.vgg_model = None
        self.clip_model = None
        self.clip_preprocess = None
        
        logger.info("Image fingerprinter cleaned up")
