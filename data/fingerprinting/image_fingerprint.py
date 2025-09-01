"""Image Fingerprinter Implementation
==================================

Professional image fingerprinting system for visual content protection and similarity detection.
Implements advanced computer vision and perceptual hashing algorithms.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""

import asyncio
import cv2
import numpy as np
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import io
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

try:
    import imagehash
    from PIL import Image, ImageFilter, ImageEnhance
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False
    logging.warning("imagehash/PIL not available, using alternative methods")

try:
    import torch
    import torchvision.transforms as transforms
    from torchvision.models import resnet50
    import clip
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.warning("PyTorch/CLIP not available, using OpenCV only")

try:
    from skimage.feature import local_binary_pattern
    from skimage.measure import compare_ssim
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    logging.warning("scikit-image not available")


class ImageFingerprintType(Enum):
    """Types of image fingerprints"""

    PERCEPTUAL_HASH = "perceptual_hash"
    FEATURE_DESCRIPTOR = "feature_descriptor"
    COLOR_HISTOGRAM = "color_histogram"
    EDGE_DESCRIPTOR = "edge_descriptor"
    TEXTURE_DESCRIPTOR = "texture_descriptor"
    CLIP_EMBEDDING = "clip_embedding"
    STRUCTURAL_HASH = "structural_hash"


@dataclass
class ImageFingerprint:
    """Image fingerprint data structure"""
    image_id: str
    fingerprint_type: ImageFingerprintType
    fingerprint_data: Union[str, np.ndarray, List[float]]
    image_dimensions: Tuple[int, int]
    file_size: Optional[int] = None
    color_space: str = "RGB"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ImageMatchResult:
    """Image similarity match result"""
    query_image_id: str
    matched_image_id: str
    similarity_score: float
    fingerprint_type: ImageFingerprintType
    confidence_metrics: Dict[str, float]
    transformation_detected: Dict[str, Any]
    match_regions: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.utcnow)


class ImageFingerprinter:
    """
    Professional image fingerprinting system for content protection.
    
    Features:
    - Multiple fingerprinting algorithms
    - Perceptual hashing (resistant to minor changes)
    - Deep learning feature extraction
    - Color and texture analysis
    - CLIP-based semantic embeddings
    - Transformation detection
    - Batch processing capabilities
    - GPU acceleration support
    """
    
    def __init__(self, 
                 max_workers: int = 4,
                 gpu_acceleration: bool = True,
                 cache_embeddings: bool = True):
        """
        Initialize image fingerprinter.
        
        Args:
            max_workers: Maximum worker threads
            gpu_acceleration: Enable GPU acceleration if available
            cache_embeddings: Cache computed embeddings
        """
        self.max_workers = max_workers
        self.gpu_acceleration = gpu_acceleration and TORCH_AVAILABLE
        self.cache_embeddings = cache_embeddings
        self.logger = logging.getLogger(__name__)
        
        # Thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        
        # Embedding cache
        self.embedding_cache: Dict[str, np.ndarray] = {}
        self.cache_max_size = 1000
        
        # Performance metrics
        self.processing_count = 0
        self.total_processing_time = 0.0
        
        # Initialize AI models
        self.feature_extractor = None
        self.clip_model = None
        self.clip_preprocess = None
        
        if self.gpu_acceleration:
            self._initialize_ai_models()
    
    def _initialize_ai_models(self):
        """
Initialize AI models for feature extraction"""
        try:
            if TORCH_AVAILABLE:
                # Load ResNet for feature extraction
                self.feature_extractor = resnet50(pretrained=True)
                self.feature_extractor.fc = torch.nn.Identity()  # Remove classifier
                self.feature_extractor.eval()
                
                # Load CLIP model for semantic embeddings
                try:
                    self.clip_model, self.clip_preprocess = clip.load("ViT-B/32")
                    self.clip_model.eval()
                    self.logger.info("Loaded CLIP model successfully")
                except Exception as e:
                    self.logger.warning(f"Failed to load CLIP model: {str(e)}")
                
                # Move to GPU if available
                if torch.cuda.is_available():
                    self.feature_extractor = self.feature_extractor.cuda()
                    if self.clip_model:
                        self.clip_model = self.clip_model.cuda()
                
                # Define image transforms
                self.transform = transforms.Compose([
                    transforms.ToPILImage(),
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                       std=[0.229, 0.224, 0.225])
                ])
                
                self.logger.info("Initialized AI models for image fingerprinting")
                
        except Exception as e:
            self.logger.warning(f"Failed to initialize AI models: {str(e)}")
            self.feature_extractor = None
            self.clip_model = None
    
    async def extract_fingerprint(self, 
                                image_data: Union[str, np.ndarray, bytes],
                                image_id: str,
                                fingerprint_types: List[ImageFingerprintType] = None) -> List[ImageFingerprint]:
        """
        Extract image fingerprints using multiple algorithms.
        
        Args:
            image_data: Image data (file path, numpy array, or bytes)
            image_id: Unique identifier for image
            fingerprint_types: Types of fingerprints to extract
            
        Returns:
            List of image fingerprints
        """
        try:
            start_time = datetime.utcnow()
            
            if fingerprint_types is None:
                fingerprint_types = [
                    ImageFingerprintType.PERCEPTUAL_HASH,
                    ImageFingerprintType.COLOR_HISTOGRAM,
                    ImageFingerprintType.EDGE_DESCRIPTOR
                ]
                
                # Add CLIP embedding if available
                if self.clip_model:
                    fingerprint_types.append(ImageFingerprintType.CLIP_EMBEDDING)
            
            # Load and preprocess image
            image = await self._load_image(image_data)
            if image is None:
                self.logger.error(f"Failed to load image {image_id}")
                return []
            
            # Extract fingerprints
            fingerprints = []
            for fingerprint_type in fingerprint_types:
                try:
                    fingerprint = await self._extract_single_fingerprint(
                        image, image_id, fingerprint_type
                    )
                    fingerprints.append(fingerprint)
                except Exception as e:
                    self.logger.error(f"Error extracting {fingerprint_type.value}: {str(e)}")
                    continue
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.processing_count += 1
            self.total_processing_time += processing_time
            
            self.logger.info(f"Extracted {len(fingerprints)} fingerprints for {image_id} in {processing_time:.2f}s")
            return fingerprints
            
        except Exception as e:
            self.logger.error(f"Error extracting image fingerprint for {image_id}: {str(e)}")
            return []
    
    async def compare_fingerprints(self, 
                                 fingerprint1: ImageFingerprint,
                                 fingerprint2: ImageFingerprint) -> ImageMatchResult:
        """
        Compare two image fingerprints for similarity.
        
        Args:
            fingerprint1: First image fingerprint
            fingerprint2: Second image fingerprint
            
        Returns:
            Image match result with similarity metrics
        """
        try:
            if fingerprint1.fingerprint_type != fingerprint2.fingerprint_type:
                raise ValueError("Cannot compare different fingerprint types")
            
            fingerprint_type = fingerprint1.fingerprint_type
            
            if fingerprint_type == ImageFingerprintType.PERCEPTUAL_HASH:
                similarity_score = await self._compare_perceptual_hashes(
                    fingerprint1.fingerprint_data, fingerprint2.fingerprint_data
                )
            elif fingerprint_type == ImageFingerprintType.COLOR_HISTOGRAM:
                similarity_score = await self._compare_color_histograms(
                    fingerprint1.fingerprint_data, fingerprint2.fingerprint_data
                )
            elif fingerprint_type == ImageFingerprintType.EDGE_DESCRIPTOR:
                similarity_score = await self._compare_edge_descriptors(
                    fingerprint1.fingerprint_data, fingerprint2.fingerprint_data
                )
            elif fingerprint_type == ImageFingerprintType.FEATURE_DESCRIPTOR:
                similarity_score = await self._compare_feature_descriptors(
                    fingerprint1.fingerprint_data, fingerprint2.fingerprint_data
                )
            elif fingerprint_type == ImageFingerprintType.CLIP_EMBEDDING:
                similarity_score = await self._compare_clip_embeddings(
                    fingerprint1.fingerprint_data, fingerprint2.fingerprint_data
                )
            else:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            # Calculate confidence metrics
            confidence_metrics = self._calculate_confidence_metrics(
                similarity_score, fingerprint1, fingerprint2
            )
            
            # Detect transformations
            transformation_detected = self._detect_transformations(
                fingerprint1, fingerprint2, similarity_score
            )
            
            # Identify match regions (simplified for images)
            match_regions = self._identify_match_regions(similarity_score)
            
            result = ImageMatchResult(
                query_image_id=fingerprint1.image_id,
                matched_image_id=fingerprint2.image_id,
                similarity_score=similarity_score,
                fingerprint_type=fingerprint_type,
                confidence_metrics=confidence_metrics,
                transformation_detected=transformation_detected,
                match_regions=match_regions
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error comparing fingerprints: {str(e)}")
            # Return empty result
            return ImageMatchResult(
                query_image_id=fingerprint1.image_id,
                matched_image_id=fingerprint2.image_id,
                similarity_score=0.0,
                fingerprint_type=fingerprint1.fingerprint_type,
                confidence_metrics={},
                transformation_detected={},
                match_regions=[]
            )
    
    async def find_similar_images(self, 
                                query_fingerprint: ImageFingerprint,
                                candidate_fingerprints: List[ImageFingerprint],
                                similarity_threshold: float = 0.8) -> List[ImageMatchResult]:
        """
        Find similar images from a list of candidates.
        
        Args:
            query_fingerprint: Query image fingerprint
            candidate_fingerprints: List of candidate fingerprints
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            List of matching image results sorted by similarity
        """
        try:
            # Filter candidates by fingerprint type
            compatible_candidates = [
                fp for fp in candidate_fingerprints 
                if fp.fingerprint_type == query_fingerprint.fingerprint_type
            ]
            
            # Compare with each candidate
            comparison_tasks = []
            for candidate in compatible_candidates:
                task = asyncio.create_task(
                    self.compare_fingerprints(query_fingerprint, candidate)
                )
                comparison_tasks.append(task)
            
            # Wait for all comparisons
            results = await asyncio.gather(*comparison_tasks)
            
            # Filter by threshold and sort by similarity
            filtered_results = [
                result for result in results 
                if result.similarity_score >= similarity_threshold
            ]
            
            filtered_results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            self.logger.info(f"Found {len(filtered_results)} similar images above threshold {similarity_threshold}")
            return filtered_results
            
        except Exception as e:
            self.logger.error(f"Error finding similar images: {str(e)}")
            return []
    
    async def extract_batch_fingerprints(self, 
                                       image_batch: List[Tuple[Union[str, np.ndarray, bytes], str]],
                                       fingerprint_types: List[ImageFingerprintType] = None) -> Dict[str, List[ImageFingerprint]]:
        """
        Extract fingerprints for a batch of images efficiently.
        
        Args:
            image_batch: List of tuples (image_data, image_id)
            fingerprint_types: Types of fingerprints to extract
            
        Returns:
            Dictionary mapping image_id to list of fingerprints
        """
        try:
            # Process images in parallel
            extraction_tasks = []
            for image_data, image_id in image_batch:
                task = asyncio.create_task(
                    self.extract_fingerprint(image_data, image_id, fingerprint_types)
                )
                extraction_tasks.append((image_id, task))
            
            # Collect results
            batch_results = {}
            for image_id, task in extraction_tasks:
                try:
                    fingerprints = await task
                    batch_results[image_id] = fingerprints
                except Exception as e:
                    self.logger.error(f"Error processing image {image_id}: {str(e)}")
                    batch_results[image_id] = []
            
            successful_count = sum(1 for fps in batch_results.values() if fps)
            self.logger.info(f"Processed batch of {len(image_batch)} images, {successful_count} successful")
            
            return batch_results
            
        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _load_image(self, image_data: Union[str, np.ndarray, bytes]) -> Optional[np.ndarray]:
        """Load image from various input formats"""
        try:
            if isinstance(image_data, str):
                # File path
                image = cv2.imread(image_data)
                if image is None:
                    self.logger.error(f"Failed to load image from path: {image_data}")
                    return None
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
            elif isinstance(image_data, np.ndarray):
                # Already a numpy array
                if len(image_data.shape) == 3 and image_data.shape[2] == 3:
                    return image_data
                elif len(image_data.shape) == 2:
                    return cv2.cvtColor(image_data, cv2.COLOR_GRAY2RGB)
                else:
                    self.logger.error(f"Unsupported image array shape: {image_data.shape}")
                    return None
                    
            elif isinstance(image_data, bytes):
                # Bytes data
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if image is None:
                    self.logger.error("Failed to decode image from bytes")
                    return None
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
            else:
                self.logger.error(f"Unsupported image data type: {type(image_data)}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error loading image: {str(e)}")
            return None
    
    async def _extract_single_fingerprint(self, 
                                        image: np.ndarray,
                                        image_id: str,
                                        fingerprint_type: ImageFingerprintType) -> ImageFingerprint:
        """Extract single type of fingerprint"""
        try:
            if fingerprint_type == ImageFingerprintType.PERCEPTUAL_HASH:
                fingerprint_data = await self._extract_perceptual_hash(image)
            elif fingerprint_type == ImageFingerprintType.COLOR_HISTOGRAM:
                fingerprint_data = await self._extract_color_histogram(image)
            elif fingerprint_type == ImageFingerprintType.EDGE_DESCRIPTOR:
                fingerprint_data = await self._extract_edge_descriptor(image)
            elif fingerprint_type == ImageFingerprintType.TEXTURE_DESCRIPTOR:
                fingerprint_data = await self._extract_texture_descriptor(image)
            elif fingerprint_type == ImageFingerprintType.FEATURE_DESCRIPTOR:
                fingerprint_data = await self._extract_feature_descriptor(image)
            elif fingerprint_type == ImageFingerprintType.CLIP_EMBEDDING:
                fingerprint_data = await self._extract_clip_embedding(image)
            elif fingerprint_type == ImageFingerprintType.STRUCTURAL_HASH:
                fingerprint_data = await self._extract_structural_hash(image)
            else:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            return ImageFingerprint(
                image_id=image_id,
                fingerprint_type=fingerprint_type,
                fingerprint_data=fingerprint_data,
                image_dimensions=(image.shape[1], image.shape[0]),
                color_space="RGB"
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting {fingerprint_type.value}: {str(e)}")
            raise
    
    async def _extract_perceptual_hash(self, image: np.ndarray) -> str:
        """Extract perceptual hash"""
        try:
            if IMAGEHASH_AVAILABLE:
                # Convert to PIL Image
                pil_image = Image.fromarray(image)
                
                # Calculate multiple hash types for robustness
                avg_hash = str(imagehash.average_hash(pil_image, hash_size=16))
                p_hash = str(imagehash.phash(pil_image, hash_size=16))
                d_hash = str(imagehash.dhash(pil_image, hash_size=16))
                w_hash = str(imagehash.whash(pil_image, hash_size=16))
                
                # Combine hashes
                combined_hash = f"{avg_hash}:{p_hash}:{d_hash}:{w_hash}"
                return combined_hash
            else:
                # Fallback to simple hash
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                resized = cv2.resize(gray, (16, 16))
                hash_value = hashlib.md5(resized.tobytes()).hexdigest()
                return hash_value
                
        except Exception as e:
            self.logger.error(f"Error extracting perceptual hash: {str(e)}")
            return ""
    
    async def _extract_color_histogram(self, image: np.ndarray) -> np.ndarray:
        """Extract color histogram"""
        try:
            # Convert to HSV for better color representation
            hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            
            # Calculate histogram for each channel
            hist_h = cv2.calcHist([hsv_image], [0], None, [180], [0, 180])
            hist_s = cv2.calcHist([hsv_image], [1], None, [256], [0, 256])
            hist_v = cv2.calcHist([hsv_image], [2], None, [256], [0, 256])
            
            # Concatenate and normalize
            hist = np.concatenate([hist_h, hist_s, hist_v]).flatten()
            hist = hist / np.sum(hist)  # Normalize
            
            return hist
            
        except Exception as e:
            self.logger.error(f"Error extracting color histogram: {str(e)}")
            return np.array([])
    
    async def _extract_edge_descriptor(self, image: np.ndarray) -> np.ndarray:
        """Extract edge-based descriptor"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply multiple edge detection methods
            edges_canny = cv2.Canny(gray, 50, 150)
            edges_sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            edges_sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            edges_laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            
            # Calculate edge statistics
            features = []
            
            # Edge density
            features.append(np.sum(edges_canny > 0) / (edges_canny.shape[0] * edges_canny.shape[1]))
            
            # Edge orientation histogram
            magnitude = np.sqrt(edges_sobel_x**2 + edges_sobel_y**2)
            orientation = np.arctan2(edges_sobel_y, edges_sobel_x)
            
            # Histogram of oriented gradients (simplified)
            hist, _ = np.histogram(orientation[magnitude > np.mean(magnitude)], bins=18, range=(-np.pi, np.pi))
            hist = hist / np.sum(hist)  # Normalize
            features.extend(hist)
            
            # Laplacian statistics
            features.extend([
                np.mean(edges_laplacian),
                np.std(edges_laplacian),
                np.min(edges_laplacian),
                np.max(edges_laplacian)
            ])
            
            return np.array(features)
            
        except Exception as e:
            self.logger.error(f"Error extracting edge descriptor: {str(e)}")
            return np.array([])
    
    async def _extract_texture_descriptor(self, image: np.ndarray) -> np.ndarray:
        """Extract texture-based descriptor"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            features = []
            
            if SKIMAGE_AVAILABLE:
                # Local Binary Pattern
                radius = 3
                n_points = 8 * radius
                lbp = local_binary_pattern(gray, n_points, radius, method='uniform')
                
                # LBP histogram
                hist, _ = np.histogram(lbp.ravel(), bins=n_points + 2, range=(0, n_points + 2))
                hist = hist / np.sum(hist)
                features.extend(hist)
            
            # Gray-Level Co-occurrence Matrix (simplified)
            # Calculate texture statistics using image patches
            patch_size = 32
            h, w = gray.shape
            
            texture_stats = []
            for i in range(0, h - patch_size, patch_size):
                for j in range(0, w - patch_size, patch_size):
                    patch = gray[i:i+patch_size, j:j+patch_size]
                    
                    # Calculate local statistics
                    texture_stats.append(np.std(patch))
                    texture_stats.append(np.mean(np.gradient(patch.astype(float))))
            
            if texture_stats:
                features.extend([
                    np.mean(texture_stats),
                    np.std(texture_stats),
                    np.min(texture_stats),
                    np.max(texture_stats)
                ])
            
            return np.array(features)
            
        except Exception as e:
            self.logger.error(f"Error extracting texture descriptor: {str(e)}")
            return np.array([])
    
    async def _extract_feature_descriptor(self, image: np.ndarray) -> np.ndarray:
        """Extract deep learning feature descriptor"""
        try:
            if not self.feature_extractor:
                raise ValueError("Feature extractor not available")
            
            # Preprocess image
            tensor = self.transform(image).unsqueeze(0)
            
            # Move to GPU if available
            if torch.cuda.is_available():
                tensor = tensor.cuda()
            
            # Extract features
            with torch.no_grad():
                features = self.feature_extractor(tensor)
                features = features.cpu().numpy().flatten()
            
            # Normalize features
            features = features / np.linalg.norm(features)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting feature descriptor: {str(e)}")
            return np.array([])
    
    async def _extract_clip_embedding(self, image: np.ndarray) -> np.ndarray:
        """Extract CLIP embedding"""
        try:
            if not self.clip_model:
                raise ValueError("CLIP model not available")
            
            # Preprocess image for CLIP
            pil_image = Image.fromarray(image)
            tensor = self.clip_preprocess(pil_image).unsqueeze(0)
            
            # Move to GPU if available
            if torch.cuda.is_available():
                tensor = tensor.cuda()
            
            # Extract CLIP features
            with torch.no_grad():
                image_features = self.clip_model.encode_image(tensor)
                image_features = image_features.cpu().numpy().flatten()
            
            # Normalize features
            image_features = image_features / np.linalg.norm(image_features)
            
            return image_features
            
        except Exception as e:
            self.logger.error(f"Error extracting CLIP embedding: {str(e)}")
            return np.array([])
    
    async def _extract_structural_hash(self, image: np.ndarray) -> str:
        """Extract structural hash based on image structure"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Resize to standard size
            resized = cv2.resize(gray, (64, 64))
            
            # Apply structural analysis
            # 1. Edge structure
            edges = cv2.Canny(resized, 50, 150)
            edge_hash = hashlib.md5(edges.tobytes()).hexdigest()[:16]
            
            # 2. Corner structure
            corners = cv2.cornerHarris(resized, 2, 3, 0.04)
            corner_hash = hashlib.md5(corners.tobytes()).hexdigest()[:16]
            
            # 3. Texture structure (simplified)
            blur = cv2.GaussianBlur(resized, (5, 5), 0)
            texture_diff = resized.astype(float) - blur.astype(float)
            texture_hash = hashlib.md5(texture_diff.tobytes()).hexdigest()[:16]
            
            # Combine structural hashes
            combined_hash = f"{edge_hash}:{corner_hash}:{texture_hash}"
            
            return combined_hash
            
        except Exception as e:
            self.logger.error(f"Error extracting structural hash: {str(e)}")
            return ""
    
    async def _compare_perceptual_hashes(self, hash1: str, hash2: str) -> float:
        """Compare perceptual hashes"""
        try:
            if IMAGEHASH_AVAILABLE and ':' in hash1 and ':' in hash2:
                # Parse combined hashes
                h1_parts = hash1.split(':')
                h2_parts = hash2.split(':')
                
                similarities = []
                for h1_part, h2_part in zip(h1_parts, h2_parts):
                    # Hamming distance for perceptual hashes
                    hamming_dist = sum(c1 != c2 for c1, c2 in zip(h1_part, h2_part))
                    similarity = 1.0 - (hamming_dist / len(h1_part))
                    similarities.append(similarity)
                
                # Average similarity across hash types
                return np.mean(similarities)
            else:
                # Simple string comparison for fallback
                return 1.0 if hash1 == hash2 else 0.0
                
        except Exception as e:
            self.logger.error(f"Error comparing perceptual hashes: {str(e)}")
            return 0.0
    
    async def _compare_color_histograms(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """Compare color histograms"""
        try:
            if len(hist1) == 0 or len(hist2) == 0:
                return 0.0
            
            # Use multiple comparison methods
            correlation = cv2.compareHist(hist1.astype(np.float32), hist2.astype(np.float32), cv2.HISTCMP_CORREL)
            chi_square = cv2.compareHist(hist1.astype(np.float32), hist2.astype(np.float32), cv2.HISTCMP_CHISQR)
            intersection = cv2.compareHist(hist1.astype(np.float32), hist2.astype(np.float32), cv2.HISTCMP_INTERSECT)
            
            # Normalize chi-square (lower is better, so invert)
            chi_square_norm = 1.0 / (1.0 + chi_square)
            
            # Weighted combination
            similarity = 0.5 * correlation + 0.3 * intersection + 0.2 * chi_square_norm
            
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            self.logger.error(f"Error comparing color histograms: {str(e)}")
            return 0.0
    
    async def _compare_edge_descriptors(self, desc1: np.ndarray, desc2: np.ndarray) -> float:
        """Compare edge descriptors"""
        try:
            if len(desc1) == 0 or len(desc2) == 0:
                return 0.0
            
            # Cosine similarity
            dot_product = np.dot(desc1, desc2)
            norm_product = np.linalg.norm(desc1) * np.linalg.norm(desc2)
            
            if norm_product == 0:
                return 0.0
            
            similarity = dot_product / norm_product
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            self.logger.error(f"Error comparing edge descriptors: {str(e)}")
            return 0.0
    
    async def _compare_feature_descriptors(self, desc1: np.ndarray, desc2: np.ndarray) -> float:
        """Compare deep learning feature descriptors"""
        try:
            if len(desc1) == 0 or len(desc2) == 0:
                return 0.0
            
            # Cosine similarity (features are already normalized)
            similarity = np.dot(desc1, desc2)
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            self.logger.error(f"Error comparing feature descriptors: {str(e)}")
            return 0.0
    
    async def _compare_clip_embeddings(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compare CLIP embeddings"""
        try:
            if len(emb1) == 0 or len(emb2) == 0:
                return 0.0
            
            # Cosine similarity (embeddings are already normalized)
            similarity = np.dot(emb1, emb2)
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            self.logger.error(f"Error comparing CLIP embeddings: {str(e)}")
            return 0.0
    
    def _calculate_confidence_metrics(self, 
                                    similarity_score: float,
                                    fingerprint1: ImageFingerprint,
                                    fingerprint2: ImageFingerprint) -> Dict[str, float]:
        """Calculate confidence metrics for the match"""
        try:
            w1, h1 = fingerprint1.image_dimensions
            w2, h2 = fingerprint2.image_dimensions
            
            # Resolution compatibility
            resolution_ratio = min(w1 * h1, w2 * h2) / max(w1 * h1, w2 * h2) if max(w1 * h1, w2 * h2) > 0 else 0
            
            # Aspect ratio compatibility
            aspect_ratio_1 = w1 / h1 if h1 > 0 else 0
            aspect_ratio_2 = w2 / h2 if h2 > 0 else 0
            aspect_ratio_similarity = min(aspect_ratio_1, aspect_ratio_2) / max(aspect_ratio_1, aspect_ratio_2) if max(aspect_ratio_1, aspect_ratio_2) > 0 else 0
            
            confidence_metrics = {
                'similarity_score': similarity_score,
                'resolution_compatibility': resolution_ratio,
                'aspect_ratio_compatibility': aspect_ratio_similarity,
                'fingerprint_quality': self._assess_fingerprint_quality(fingerprint1, fingerprint2),
                'overall_confidence': (similarity_score + resolution_ratio + aspect_ratio_similarity) / 3.0
            }
            
            return confidence_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence metrics: {str(e)}")
            return {}
    
    def _assess_fingerprint_quality(self, 
                                  fingerprint1: ImageFingerprint,
                                  fingerprint2: ImageFingerprint) -> float:
        """Assess quality of fingerprints for comparison"""
        try:
            quality_score = 1.0
            
            # Check if fingerprint data is valid
            if fingerprint1.fingerprint_type == ImageFingerprintType.PERCEPTUAL_HASH:
                if not fingerprint1.fingerprint_data or not fingerprint2.fingerprint_data:
                    quality_score *= 0.5
            elif fingerprint1.fingerprint_type in [
                ImageFingerprintType.COLOR_HISTOGRAM,
                ImageFingerprintType.EDGE_DESCRIPTOR,
                ImageFingerprintType.FEATURE_DESCRIPTOR,
                ImageFingerprintType.CLIP_EMBEDDING
            ]:
                if (isinstance(fingerprint1.fingerprint_data, np.ndarray) and len(fingerprint1.fingerprint_data) == 0) or \
                   (isinstance(fingerprint2.fingerprint_data, np.ndarray) and len(fingerprint2.fingerprint_data) == 0):
                    quality_score *= 0.5
            
            # Check image dimensions (very small images are lower quality)
            w1, h1 = fingerprint1.image_dimensions
            w2, h2 = fingerprint2.image_dimensions
            
            min_area = min(w1 * h1, w2 * h2)
            if min_area < 100 * 100:  # Less than 100x100 pixels
                quality_score *= 0.7
            elif min_area < 50 * 50:  # Less than 50x50 pixels
                quality_score *= 0.4
            
            return quality_score
            
        except Exception as e:
            self.logger.error(f"Error assessing fingerprint quality: {str(e)}")
            return 0.5
    
    def _detect_transformations(self, 
                              fingerprint1: ImageFingerprint,
                              fingerprint2: ImageFingerprint,
                              similarity_score: float) -> Dict[str, Any]:
        """Detect possible transformations between images"""
        try:
            w1, h1 = fingerprint1.image_dimensions
            w2, h2 = fingerprint2.image_dimensions
            
            transformations = {
                'scaling_detected': False,
                'rotation_detected': False,
                'cropping_detected': False,
                'compression_detected': False,
                'color_adjustment_detected': False
            }
            
            # Scaling detection
            size_ratio = (w1 * h1) / (w2 * h2) if (w2 * h2) > 0 else 1.0
            if not (0.9 <= size_ratio <= 1.1):
                transformations['scaling_detected'] = True
                transformations['scale_ratio'] = size_ratio
            
            # Aspect ratio change (might indicate cropping)
            aspect_ratio_1 = w1 / h1 if h1 > 0 else 1.0
            aspect_ratio_2 = w2 / h2 if h2 > 0 else 1.0
            aspect_ratio_change = abs(aspect_ratio_1 - aspect_ratio_2) / max(aspect_ratio_1, aspect_ratio_2)
            
            if aspect_ratio_change > 0.1:
                transformations['cropping_detected'] = True
                transformations['aspect_ratio_change'] = aspect_ratio_change
            
            # High similarity with different dimensions suggests compression
            if similarity_score > 0.8 and (transformations['scaling_detected'] or size_ratio < 1.0):
                transformations['compression_detected'] = True
            
            # If perceptual hash similarity is high but exact match is low, might indicate color adjustment
            if fingerprint1.fingerprint_type == ImageFingerprintType.PERCEPTUAL_HASH and similarity_score > 0.7:
                transformations['color_adjustment_detected'] = True
            
            return transformations
            
        except Exception as e:
            self.logger.error(f"Error detecting transformations: {str(e)}")
            return {}
    
    def _identify_match_regions(self, similarity_score: float) -> List[Dict[str, Any]]:
        """Identify match regions (simplified for images)"""
        try:
            if similarity_score < 0.5:
                return []
            
            # For images, we consider the entire image as a match region
            # In more advanced implementations, this could include spatial matching
            match_regions = [{
                'region_type': 'full_image',
                'similarity_score': similarity_score,
                'confidence': 'high' if similarity_score > 0.8 else 'medium' if similarity_score > 0.6 else 'low'
            }]
            
            return match_regions
            
        except Exception as e:
            self.logger.error(f"Error identifying match regions: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get fingerprinter statistics"""
        avg_processing_time = (self.total_processing_time / self.processing_count 
                             if self.processing_count > 0 else 0.0)
        
        return {
            'processing_count': self.processing_count,
            'average_processing_time': avg_processing_time,
            'cached_embeddings': len(self.embedding_cache),
            'gpu_acceleration': self.gpu_acceleration,
            'torch_available': TORCH_AVAILABLE,
            'imagehash_available': IMAGEHASH_AVAILABLE,
            'skimage_available': SKIMAGE_AVAILABLE,
            'feature_extractor_loaded': self.feature_extractor is not None,
            'clip_model_loaded': self.clip_model is not None
        }
    
    async def close(self):
        """
Cleanup resources"""
        try:
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)
            
            # Clear cache
            self.embedding_cache.clear()
            
            self.logger.info("Image fingerprinter closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing image fingerprinter: {str(e)}")
