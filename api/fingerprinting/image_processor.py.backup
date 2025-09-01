"""IA Influencer Agent - Image Fingerprinting Processor
Author: Fahed Mlaiel <mlaiel@live.de>

AVERTISSEMENT LÉGAL STRICT:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée 
sans permission écrite expresse est strictement interdite et 
constituera une violation des droits d'auteur.

Advanced image fingerprinting processor for multi-format content protection
"""
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import hashlib
import logging
from PIL import Image
import imagehash
from skimage import feature, measure
from scipy import spatial

logger = logging.getLogger(__name__)

@dataclass
class ImageFingerprint:
    """Image fingerprint data structure"""
    content_hash: str
    perceptual_hash: str
    color_histogram: np.ndarray
    texture_features: np.ndarray
    shape_features: np.ndarray
    sift_features: Optional[np.ndarray]
    resolution: Tuple[int, int]
    file_format: str
    color_space: str
    metadata: Dict[str, Any]

class ImageFingerprintProcessor:
    """
    Professional image fingerprinting processor with advanced computer vision algorithms
    Handles multi-format image content protection and similarity detection
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize image fingerprinting processor"""
        self.config = config or self._get_default_config()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.sift_detector = cv2.SIFT_create(nfeatures=500)
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for image processing"""
        return {
            'resize_width': 512,
            'resize_height': 512,
            'similarity_threshold': 0.85,
            'hash_size': 16,
            'histogram_bins': 64,
            'texture_radius': 3,
            'texture_points': 24
        }
    
    async def process_image_file(self, file_path: Path) -> ImageFingerprint:
        """
        Process image file and generate comprehensive fingerprint
        
        Args:
            file_path: Path to image file
            
        Returns:
            ImageFingerprint object with extracted features
        """
        try:
            # Load image asynchronously
            loop = asyncio.get_event_loop()
            
            image = await loop.run_in_executor(
                self.executor,
                self._load_image,
                str(file_path)
            )
            
            # Generate content hash
            content_hash = self._generate_content_hash(image)
            
            # Process features in parallel
            features = await asyncio.gather(
                self._extract_perceptual_hash(image),
                self._extract_color_histogram(image),
                self._extract_texture_features(image),
                self._extract_shape_features(image),
                self._extract_sift_features(image)
            )
            
            perceptual_hash, color_histogram, texture_features, shape_features, sift_features = features
            
            # Get image info
            height, width = image.shape[:2]
            color_space = "BGR" if len(image.shape) == 3 else "GRAY"
            
            # Create fingerprint
            fingerprint = ImageFingerprint(
                content_hash=content_hash,
                perceptual_hash=perceptual_hash,
                color_histogram=color_histogram,
                texture_features=texture_features,
                shape_features=shape_features,
                sift_features=sift_features,
                resolution=(width, height),
                file_format=file_path.suffix.lower(),
                color_space=color_space,
                metadata=self._extract_metadata(file_path)
            )
            
            logger.info(f"Image fingerprint generated for {file_path.name}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error processing image file {file_path}: {str(e)}")
            raise
    
    def _load_image(self, file_path: str) -> np.ndarray:
        """Load and preprocess image"""
        # Try OpenCV first
        image = cv2.imread(file_path)
        if image is None:
            # Fallback to PIL for other formats
            pil_image = Image.open(file_path)
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Resize if too large
        height, width = image.shape[:2]
        if width > self.config['resize_width'] or height > self.config['resize_height']:
            image = cv2.resize(
                image,
                (self.config['resize_width'], self.config['resize_height']),
                interpolation=cv2.INTER_AREA
            )
        
        return image
    
    def _generate_content_hash(self, image: np.ndarray) -> str:
        """Generate unique hash for image content"""
        image_bytes = image.tobytes()
        return hashlib.sha256(image_bytes).hexdigest()
    
    async def _extract_perceptual_hash(self, image: np.ndarray) -> str:
        """Extract perceptual hash from image"""
        loop = asyncio.get_event_loop()
        
        def compute_hash():
            # Convert to RGB for PIL
            if len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            pil_image = Image.fromarray(image_rgb)
            return str(imagehash.phash(pil_image, hash_size=self.config['hash_size']))
        
        return await loop.run_in_executor(self.executor, compute_hash)
    
    async def _extract_color_histogram(self, image: np.ndarray) -> np.ndarray:
        """Extract color histogram features"""
        loop = asyncio.get_event_loop()
        
        def compute_histogram():
            if len(image.shape) == 3:
                # Color image - calculate histogram for each channel
                hist_b = cv2.calcHist([image], [0], None, [self.config['histogram_bins']], [0, 256])
                hist_g = cv2.calcHist([image], [1], None, [self.config['histogram_bins']], [0, 256])
                hist_r = cv2.calcHist([image], [2], None, [self.config['histogram_bins']], [0, 256])
                
                # Normalize and concatenate
                hist_combined = np.concatenate([
                    hist_b.flatten() / hist_b.sum(),
                    hist_g.flatten() / hist_g.sum(),
                    hist_r.flatten() / hist_r.sum()
                ])
            else:
                # Grayscale image
                hist = cv2.calcHist([image], [0], None, [self.config['histogram_bins']], [0, 256])
                hist_combined = hist.flatten() / hist.sum()
            
            return hist_combined
        
        return await loop.run_in_executor(self.executor, compute_histogram)
    
    async def _extract_texture_features(self, image: np.ndarray) -> np.ndarray:
        """Extract texture features using Local Binary Patterns"""
        loop = asyncio.get_event_loop()
        
        def compute_texture():
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Calculate LBP
            lbp = feature.local_binary_pattern(
                gray,
                self.config['texture_points'],
                self.config['texture_radius'],
                method='uniform'
            )
            
            # Calculate histogram of LBP
            lbp_hist, _ = np.histogram(
                lbp.ravel(),
                bins=self.config['texture_points'] + 2,
                range=(0, self.config['texture_points'] + 2)
            )
            
            # Normalize histogram
            lbp_hist = lbp_hist.astype(float) / lbp_hist.sum()
            
            # Additional texture statistics
            gray_stats = [
                np.mean(gray),
                np.std(gray),
                np.min(gray),
                np.max(gray)
            ]
            
            return np.concatenate([lbp_hist, gray_stats])
        
        return await loop.run_in_executor(self.executor, compute_texture)
    
    async def _extract_shape_features(self, image: np.ndarray) -> np.ndarray:
        """Extract shape features using edge detection and contours"""
        loop = asyncio.get_event_loop()
        
        def compute_shape():
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Calculate edge density
            edge_density = np.sum(edges > 0) / edges.size
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Shape statistics
            if contours:
                # Get largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Calculate contour properties
                area = cv2.contourArea(largest_contour)
                perimeter = cv2.arcLength(largest_contour, True)
                
                # Hu moments for shape description
                moments = cv2.moments(largest_contour)
                if moments['m00'] != 0:
                    hu_moments = cv2.HuMoments(moments).flatten()
                    # Take log of absolute values to make them more manageable
                    hu_moments = -np.sign(hu_moments) * np.log10(np.abs(hu_moments) + 1e-10)
                else:
                    hu_moments = np.zeros(7)
                
                # Compactness and other shape features
                compactness = (perimeter * perimeter) / (4 * np.pi * area) if area > 0 else 0
                
                shape_features = np.concatenate([
                    [edge_density, area, perimeter, compactness],
                    hu_moments
                ])
            else:
                # No contours found
                shape_features = np.concatenate([
                    [edge_density, 0, 0, 0],
                    np.zeros(7)
                ])
            
            return shape_features
        
        return await loop.run_in_executor(self.executor, compute_shape)
    
    async def _extract_sift_features(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract SIFT keypoint features"""
        loop = asyncio.get_event_loop()
        
        def compute_sift():
            try:
                # Convert to grayscale if needed
                if len(image.shape) == 3:
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                else:
                    gray = image
                
                # Detect SIFT features
                keypoints, descriptors = self.sift_detector.detectAndCompute(gray, None)
                
                if descriptors is not None and len(descriptors) > 0:
                    # Use statistical summary of descriptors
                    sift_summary = np.concatenate([
                        np.mean(descriptors, axis=0),
                        np.std(descriptors, axis=0),
                        np.median(descriptors, axis=0)
                    ])
                    return sift_summary
                else:
                    return None
                    
            except Exception as e:
                logger.warning(f"SIFT extraction failed: {str(e)}")
                return None
        
        return await loop.run_in_executor(self.executor, compute_sift)
    
    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract file metadata"""
        return {
            'filename': file_path.name,
            'file_size': file_path.stat().st_size,
            'created_at': file_path.stat().st_ctime,
            'modified_at': file_path.stat().st_mtime
        }
    
    def calculate_similarity(self, fp1: ImageFingerprint, fp2: ImageFingerprint) -> float:
        """
        Calculate similarity score between two image fingerprints
        
        Args:
            fp1: First image fingerprint
            fp2: Second image fingerprint
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Content hash exact match
            if fp1.content_hash == fp2.content_hash:
                return 1.0
            
            # Perceptual hash similarity
            hash_similarity = self._calculate_hash_similarity(fp1.perceptual_hash, fp2.perceptual_hash)
            
            # Color histogram similarity
            color_similarity = self._histogram_intersection(fp1.color_histogram, fp2.color_histogram)
            
            # Texture similarity
            texture_similarity = self._cosine_similarity(fp1.texture_features, fp2.texture_features)
            
            # Shape similarity
            shape_similarity = self._cosine_similarity(fp1.shape_features, fp2.shape_features)
            
            # SIFT features similarity
            sift_similarity = 0.0
            if fp1.sift_features is not None and fp2.sift_features is not None:
                sift_similarity = self._cosine_similarity(fp1.sift_features, fp2.sift_features)
            
            # Resolution similarity
            resolution_similarity = self._resolution_similarity(fp1.resolution, fp2.resolution)
            
            # Weighted average
            weights = {
                'hash': 0.25,
                'color': 0.25,
                'texture': 0.2,
                'shape': 0.15,
                'sift': 0.1,
                'resolution': 0.05
            }
            
            similarity = (
                weights['hash'] * hash_similarity +
                weights['color'] * color_similarity +
                weights['texture'] * texture_similarity +
                weights['shape'] * shape_similarity +
                weights['sift'] * sift_similarity +
                weights['resolution'] * resolution_similarity
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def _calculate_hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between perceptual hashes"""
        if len(hash1) != len(hash2):
            return 0.0
        
        # Calculate Hamming distance
        hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        similarity = 1.0 - (hamming_distance / len(hash1))
        
        return similarity
    
    def _histogram_intersection(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """Calculate histogram intersection similarity"""
        try:
            if len(hist1) != len(hist2):
                return 0.0
            
            intersection = np.sum(np.minimum(hist1, hist2))
            return float(intersection)
            
        except Exception:
            return 0.0
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            if len(vec1) != len(vec2):
                return 0.0
            
            # Handle zero vectors
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(vec1, vec2) / (norm1 * norm2)
            return float(np.clip(similarity, 0.0, 1.0))
            
        except Exception:
            return 0.0
    
    def _resolution_similarity(self, res1: Tuple[int, int], res2: Tuple[int, int]) -> float:
        """Calculate resolution similarity"""
        aspect_ratio_1 = res1[0] / res1[1] if res1[1] > 0 else 0
        aspect_ratio_2 = res2[0] / res2[1] if res2[1] > 0 else 0
        
        if aspect_ratio_1 == 0 or aspect_ratio_2 == 0:
            return 0.0
        
        ratio_diff = abs(aspect_ratio_1 - aspect_ratio_2) / max(aspect_ratio_1, aspect_ratio_2)
        return 1.0 - min(ratio_diff, 1.0)
    
    def is_duplicate(self, fp1: ImageFingerprint, fp2: ImageFingerprint) -> bool:
        """Check if two fingerprints represent duplicate content"""
        similarity = self.calculate_similarity(fp1, fp2)
        return similarity >= self.config['similarity_threshold']
    
    async def batch_process(self, file_paths: List[Path]) -> List[ImageFingerprint]:
        """Process multiple image files in parallel"""
        tasks = [self.process_image_file(path) for path in file_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
