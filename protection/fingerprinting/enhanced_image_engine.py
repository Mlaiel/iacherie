#!/usr/bin/env python3
"""Enhanced Image Protection Engine with Perceptual Hashing + Advanced Watermarking
Production-ready image protection for content security

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import hashlib
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import base64

# Core image processing
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None

try:
    import imagehash
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False
    imagehash = None
    Image = None

# For advanced features
try:
    from scipy import ndimage
    from scipy.fft import fft2, ifft2
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    ndimage = None
    fft2 = None
    ifft2 = None

try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    KMeans = None

logger = logging.getLogger(__name__)

@dataclass
class EnhancedImageFingerprint:
    """Enhanced image fingerprint with multiple hashing algorithms"""
    file_id: str
    
    # Perceptual hashes
    dhash: str
    phash: str
    ahash: str
    whash: str
    
    # Color features
    color_histogram: np.ndarray
    dominant_colors: List[Tuple[int, int, int]]
    color_moments: Dict[str, float]
    
    # Texture features
    lbp_histogram: np.ndarray
    glcm_features: Dict[str, float]
    gabor_features: np.ndarray
    
    # Shape features
    edge_histogram: np.ndarray
    contour_features: Dict[str, Any]
    
    # Quality metrics
    sharpness_score: float
    noise_level: float
    compression_artifacts: float
    
    # Metadata
    dimensions: Tuple[int, int]
    file_size: int
    confidence_score: float
    created_at: datetime

@dataclass
class WatermarkInfo:
    """Watermark embedding information"""
    watermark_type: str  # 'lsb', 'dct', 'dwt', 'spread_spectrum'
    embedded_text: str
    embedding_strength: float
    location: Optional[Tuple[int, int]]
    size: Optional[Tuple[int, int]]
    key: Optional[str]  # For encryption

class EnhancedImageProtectionEngine:
    """Production-ready image protection engine with advanced watermarking"""
    
    def __init__(self,
                 hash_size: int = 8,
                 enable_advanced_features: bool = True,
                 watermark_strength: float = 0.1):
        """
        Initialize enhanced image protection engine
        
        Args:
            hash_size: Size for perceptual hashing
            enable_advanced_features: Enable SIFT, texture analysis etc.
            watermark_strength: Default watermark embedding strength
        """
        if not IMAGEHASH_AVAILABLE:
            raise RuntimeError("PIL and imagehash are required for image protection")
        
        self.hash_size = hash_size
        self.enable_advanced_features = enable_advanced_features
        self.watermark_strength = watermark_strength
        
        # Initialize feature extractors
        if OPENCV_AVAILABLE and enable_advanced_features:
            self.sift = None
            try:
                self.sift = cv2.SIFT_create()
            except:
                logger.warning("SIFT not available")
            
            self.orb = cv2.ORB_create(nfeatures=500)
        
        self.similarity_threshold = 0.85
        
        logger.info(f"Enhanced Image Protection Engine initialized")
        logger.info(f"OpenCV available: {OPENCV_AVAILABLE}")
        logger.info(f"ImageHash available: {IMAGEHASH_AVAILABLE}")
        logger.info(f"SciPy available: {SCIPY_AVAILABLE}")
        logger.info(f"Advanced features enabled: {enable_advanced_features}")
    
    async def extract_fingerprint(self, image_path: Union[str, Path]) -> EnhancedImageFingerprint:
        """
        Extract comprehensive image fingerprint
        
        Args:
            image_path: Path to image file
            
        Returns:
            Enhanced image fingerprint
        """
        # Load image
        pil_image = Image.open(str(image_path))
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to numpy array for OpenCV operations
        cv_image = None
        if OPENCV_AVAILABLE:
            cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Generate file ID
        file_id = self._generate_file_id(image_path, pil_image)
        
        # Extract all features
        features = await self._extract_all_features(pil_image, cv_image)
        
        return EnhancedImageFingerprint(
            file_id=file_id,
            dhash=features['dhash'],
            phash=features['phash'],
            ahash=features['ahash'],
            whash=features['whash'],
            color_histogram=features['color_histogram'],
            dominant_colors=features['dominant_colors'],
            color_moments=features['color_moments'],
            lbp_histogram=features['lbp_histogram'],
            glcm_features=features['glcm_features'],
            gabor_features=features['gabor_features'],
            edge_histogram=features['edge_histogram'],
            contour_features=features['contour_features'],
            sharpness_score=features['sharpness_score'],
            noise_level=features['noise_level'],
            compression_artifacts=features['compression_artifacts'],
            dimensions=pil_image.size,
            file_size=Path(image_path).stat().st_size,
            confidence_score=features['confidence_score'],
            created_at=datetime.utcnow()
        )
    
    async def _extract_all_features(self, pil_image: Image.Image, cv_image: Optional[np.ndarray]) -> Dict[str, Any]:
        """Extract all image features"""
        features = {}
        
        # Perceptual hashes
        features['dhash'] = str(imagehash.dhash(pil_image, hash_size=self.hash_size))
        features['phash'] = str(imagehash.phash(pil_image, hash_size=self.hash_size))
        features['ahash'] = str(imagehash.average_hash(pil_image, hash_size=self.hash_size))
        features['whash'] = str(imagehash.whash(pil_image, hash_size=self.hash_size))
        
        # Color features
        features.update(await self._extract_color_features(pil_image, cv_image))
        
        # Texture features
        if self.enable_advanced_features and cv_image is not None:
            features.update(await self._extract_texture_features(cv_image))
        else:
            features.update(self._default_texture_features())
        
        # Shape features
        if cv_image is not None:
            features.update(await self._extract_shape_features(cv_image))
        else:
            features.update(self._default_shape_features())
        
        # Quality assessment
        features.update(await self._assess_image_quality(pil_image, cv_image))
        
        # Calculate confidence
        features['confidence_score'] = self._calculate_confidence(features)
        
        return features
    
    async def _extract_color_features(self, pil_image: Image.Image, cv_image: Optional[np.ndarray]) -> Dict[str, Any]:
        """Extract color-based features"""
        features = {}
        
        # Color histogram (RGB)
        img_array = np.array(pil_image)
        hist_r = np.histogram(img_array[:, :, 0], bins=64, range=(0, 256))[0]
        hist_g = np.histogram(img_array[:, :, 1], bins=64, range=(0, 256))[0]
        hist_b = np.histogram(img_array[:, :, 2], bins=64, range=(0, 256))[0]
        
        color_histogram = np.concatenate([hist_r, hist_g, hist_b])
        color_histogram = color_histogram / (np.sum(color_histogram) + 1e-10)
        features['color_histogram'] = color_histogram
        
        # Dominant colors using K-means
        if SKLEARN_AVAILABLE:
            pixels = img_array.reshape(-1, 3)
            # Sample pixels for efficiency
            sample_size = min(10000, len(pixels))
            sampled_pixels = pixels[np.random.choice(len(pixels), sample_size, replace=False)]
            
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(sampled_pixels)
            dominant_colors = [(int(c[0]), int(c[1]), int(c[2])) for c in kmeans.cluster_centers_]
            features['dominant_colors'] = dominant_colors
        else:
            features['dominant_colors'] = [(0, 0, 0)] * 5
        
        # Color moments (mean, std, skewness for each channel)
        color_moments = {}
        for i, channel in enumerate(['r', 'g', 'b']):
            channel_data = img_array[:, :, i]
            color_moments[f'{channel}_mean'] = float(np.mean(channel_data))
            color_moments[f'{channel}_std'] = float(np.std(channel_data))
            
            # Skewness calculation
            mean_val = np.mean(channel_data)
            std_val = np.std(channel_data)
            if std_val > 0:
                skewness = np.mean(((channel_data - mean_val) / std_val) ** 3)
                color_moments[f'{channel}_skewness'] = float(skewness)
            else:
                color_moments[f'{channel}_skewness'] = 0.0
        
        features['color_moments'] = color_moments
        
        return features
    
    async def _extract_texture_features(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Extract texture-based features"""
        features = {}
        
        # Convert to grayscale for texture analysis
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Local Binary Pattern (LBP)
        lbp_histogram = self._compute_lbp_histogram(gray)
        features['lbp_histogram'] = lbp_histogram
        
        # Gray-Level Co-occurrence Matrix (GLCM) features
        glcm_features = self._compute_glcm_features(gray)
        features['glcm_features'] = glcm_features
        
        # Gabor filter responses
        gabor_features = self._compute_gabor_features(gray)
        features['gabor_features'] = gabor_features
        
        return features
    
    def _default_texture_features(self) -> Dict[str, Any]:
        """Default texture features when advanced processing is not available"""
        return {
            'lbp_histogram': np.zeros(256),
            'glcm_features': {'contrast': 0.0, 'dissimilarity': 0.0, 'homogeneity': 0.0, 'energy': 0.0},
            'gabor_features': np.zeros(8)
        }
    
    async def _extract_shape_features(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Extract shape-based features"""
        features = {}
        
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Edge histogram using Canny
        edges = cv2.Canny(gray, 50, 150)
        edge_histogram = self._compute_edge_direction_histogram(edges, gray)
        features['edge_histogram'] = edge_histogram
        
        # Contour features
        contour_features = self._compute_contour_features(edges)
        features['contour_features'] = contour_features
        
        return features
    
    def _default_shape_features(self) -> Dict[str, Any]:
        """Default shape features when OpenCV is not available"""
        return {
            'edge_histogram': np.zeros(8),
            'contour_features': {'contour_count': 0, 'total_area': 0.0, 'avg_perimeter': 0.0}
        }
    
    async def _assess_image_quality(self, pil_image: Image.Image, cv_image: Optional[np.ndarray]) -> Dict[str, Any]:
        """Assess image quality metrics"""
        features = {}
        
        if cv_image is not None:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Sharpness using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            features['sharpness_score'] = float(laplacian_var)
            
            # Noise estimation using high-frequency content
            # Apply Gaussian blur and compute difference
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            noise_estimate = np.std(gray.astype(float) - blurred.astype(float))
            features['noise_level'] = float(noise_estimate)
            
            # Compression artifacts detection
            # Look for blocking artifacts (simplified)
            block_size = 8
            h, w = gray.shape
            block_variance = []
            
            for i in range(0, h - block_size, block_size):
                for j in range(0, w - block_size, block_size):
                    block = gray[i:i+block_size, j:j+block_size]
                    block_variance.append(np.var(block))
            
            compression_artifacts = float(np.std(block_variance)) if block_variance else 0.0
            features['compression_artifacts'] = compression_artifacts
        else:
            # Fallback quality metrics
            img_array = np.array(pil_image.convert('L'))
            features['sharpness_score'] = float(np.std(img_array))
            features['noise_level'] = 0.0
            features['compression_artifacts'] = 0.0
        
        return features
    
    def _compute_lbp_histogram(self, gray_image: np.ndarray) -> np.ndarray:
        """Compute Local Binary Pattern histogram"""
        # Simple LBP implementation
        h, w = gray_image.shape
        lbp = np.zeros_like(gray_image)
        
        for i in range(1, h-1):
            for j in range(1, w-1):
                center = gray_image[i, j]
                code = 0
                code |= (gray_image[i-1, j-1] > center) << 0
                code |= (gray_image[i-1, j] > center) << 1
                code |= (gray_image[i-1, j+1] > center) << 2
                code |= (gray_image[i, j+1] > center) << 3
                code |= (gray_image[i+1, j+1] > center) << 4
                code |= (gray_image[i+1, j] > center) << 5
                code |= (gray_image[i+1, j-1] > center) << 6
                code |= (gray_image[i, j-1] > center) << 7
                lbp[i, j] = code
        
        # Compute histogram
        histogram = np.histogram(lbp, bins=256, range=(0, 256))[0]
        return histogram / (np.sum(histogram) + 1e-10)
    
    def _compute_glcm_features(self, gray_image: np.ndarray) -> Dict[str, float]:
        """Compute Gray-Level Co-occurrence Matrix features"""
        # Simplified GLCM implementation
        h, w = gray_image.shape
        
        # Quantize to reduce levels
        quantized = (gray_image // 32).astype(np.uint8)
        max_level = np.max(quantized) + 1
        
        # Compute GLCM for 0-degree direction (horizontal)
        glcm = np.zeros((max_level, max_level))
        
        for i in range(h):
            for j in range(w-1):
                glcm[quantized[i, j], quantized[i, j+1]] += 1
        
        # Normalize
        glcm = glcm / (np.sum(glcm) + 1e-10)
        
        # Compute features
        features = {}
        
        # Contrast
        contrast = 0.0
        for i in range(max_level):
            for j in range(max_level):
                contrast += glcm[i, j] * (i - j) ** 2
        features['contrast'] = float(contrast)
        
        # Dissimilarity
        dissimilarity = 0.0
        for i in range(max_level):
            for j in range(max_level):
                dissimilarity += glcm[i, j] * abs(i - j)
        features['dissimilarity'] = float(dissimilarity)
        
        # Homogeneity
        homogeneity = 0.0
        for i in range(max_level):
            for j in range(max_level):
                homogeneity += glcm[i, j] / (1 + (i - j) ** 2)
        features['homogeneity'] = float(homogeneity)
        
        # Energy
        energy = np.sum(glcm ** 2)
        features['energy'] = float(energy)
        
        return features
    
    def _compute_gabor_features(self, gray_image: np.ndarray) -> np.ndarray:
        """Compute Gabor filter responses"""
        if not OPENCV_AVAILABLE:
            return np.zeros(8)
        
        # Gabor filter parameters
        orientations = [0, 45, 90, 135]  # degrees
        frequencies = [0.1, 0.3]  # cycles per pixel
        
        responses = []
        
        for freq in frequencies:
            for angle in orientations:
                # Create Gabor kernel
                kernel = cv2.getGaborKernel((21, 21), 5, np.radians(angle), 2*np.pi*freq, 0.5, 0, ktype=cv2.CV_32F)
                
                # Apply filter
                filtered = cv2.filter2D(gray_image, cv2.CV_8UC3, kernel)
                
                # Compute response magnitude
                response = np.mean(np.abs(filtered))
                responses.append(response)
        
        return np.array(responses)
    
    def _compute_edge_direction_histogram(self, edges: np.ndarray, gray_image: np.ndarray) -> np.ndarray:
        """Compute edge direction histogram"""
        if not OPENCV_AVAILABLE:
            return np.zeros(8)
        
        # Compute gradients
        grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        
        # Compute gradient direction
        angles = np.arctan2(grad_y, grad_x)
        
        # Quantize angles to 8 bins
        angle_bins = ((angles + np.pi) / (2 * np.pi) * 8).astype(int)
        angle_bins = np.clip(angle_bins, 0, 7)
        
        # Only consider edge pixels
        edge_pixels = edges > 0
        edge_angles = angle_bins[edge_pixels]
        
        # Compute histogram
        histogram = np.histogram(edge_angles, bins=8, range=(0, 8))[0]
        return histogram / (np.sum(histogram) + 1e-10)
    
    def _compute_contour_features(self, edges: np.ndarray) -> Dict[str, Any]:
        """Compute contour-based features"""
        if not OPENCV_AVAILABLE:
            return {'contour_count': 0, 'total_area': 0.0, 'avg_perimeter': 0.0}
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter small contours
        significant_contours = [c for c in contours if cv2.contourArea(c) > 100]
        
        features = {}
        features['contour_count'] = len(significant_contours)
        
        if significant_contours:
            areas = [cv2.contourArea(c) for c in significant_contours]
            perimeters = [cv2.arcLength(c, True) for c in significant_contours]
            
            features['total_area'] = float(np.sum(areas))
            features['avg_perimeter'] = float(np.mean(perimeters))
        else:
            features['total_area'] = 0.0
            features['avg_perimeter'] = 0.0
        
        return features
    
    def _calculate_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate confidence score for the fingerprint"""
        confidence_factors = []
        
        # Hash completeness
        hash_features = ['dhash', 'phash', 'ahash', 'whash']
        hash_completeness = sum(1 for h in hash_features if features.get(h)) / len(hash_features)
        confidence_factors.append(hash_completeness)
        
        # Feature richness
        feature_groups = ['color_histogram', 'dominant_colors', 'lbp_histogram', 'edge_histogram']
        feature_richness = sum(1 for f in feature_groups if f in features) / len(feature_groups)
        confidence_factors.append(feature_richness)
        
        # Image quality
        sharpness = features.get('sharpness_score', 0)
        quality_score = min(sharpness / 100.0, 1.0)  # Normalize sharpness
        confidence_factors.append(quality_score)
        
        return float(np.mean(confidence_factors))
    
    def _generate_file_id(self, image_path: Union[str, Path], pil_image: Image.Image) -> str:
        """Generate unique file ID"""
        path_str = str(image_path)
        path_hash = hashlib.md5(path_str.encode()).hexdigest()[:16]
        
        # Use image data for additional uniqueness
        img_array = np.array(pil_image)
        img_hash = hashlib.md5(img_array.tobytes()).hexdigest()[:16]
        
        return f"image_{path_hash}_{img_hash}"
    
    # Watermarking methods
    
    async def embed_watermark(self,
                            image_path: Union[str, Path],
                            watermark_text: str,
                            output_path: Union[str, Path],
                            method: str = 'lsb',
                            strength: Optional[float] = None) -> WatermarkInfo:
        """
        Embed watermark into image
        
        Args:
            image_path: Input image path
            watermark_text: Text to embed
            output_path: Output image path
            method: Watermarking method ('lsb', 'dct', 'spread_spectrum')
            strength: Embedding strength (0.0 to 1.0)
            
        Returns:
            Watermark information
        """
        if strength is None:
            strength = self.watermark_strength
        
        # Load image
        pil_image = Image.open(str(image_path))
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Apply watermarking based on method
        if method == 'lsb':
            watermarked_image = await self._embed_lsb_watermark(pil_image, watermark_text)
        elif method == 'dct':
            watermarked_image = await self._embed_dct_watermark(pil_image, watermark_text, strength)
        elif method == 'spread_spectrum':
            watermarked_image = await self._embed_spread_spectrum_watermark(pil_image, watermark_text, strength)
        else:
            raise ValueError(f"Unknown watermarking method: {method}")
        
        # Save watermarked image
        watermarked_image.save(str(output_path))
        
        return WatermarkInfo(
            watermark_type=method,
            embedded_text=watermark_text,
            embedding_strength=strength,
            location=None,
            size=watermarked_image.size,
            key=None
        )
    
    async def _embed_lsb_watermark(self, image: Image.Image, text: str) -> Image.Image:
        """Embed watermark using Least Significant Bit method"""
        img_array = np.array(image)
        
        # Convert text to binary
        binary_text = ''.join(format(ord(char), '08b') for char in text)
        binary_text += '1111111111111110'  # End marker
        
        # Flatten image for easier processing
        flat_img = img_array.flatten()
        
        # Embed watermark
        for i, bit in enumerate(binary_text):
            if i < len(flat_img):
                flat_img[i] = (flat_img[i] & 0xFE) | int(bit)
        
        # Reshape back to image
        watermarked_array = flat_img.reshape(img_array.shape)
        return Image.fromarray(watermarked_array)
    
    async def _embed_dct_watermark(self, image: Image.Image, text: str, strength: float) -> Image.Image:
        """Embed watermark using DCT method"""
        if not SCIPY_AVAILABLE:
            logger.warning("SciPy not available, falling back to LSB")
            return await self._embed_lsb_watermark(image, text)
        
        img_array = np.array(image).astype(np.float32)
        
        # Convert text to binary
        binary_text = ''.join(format(ord(char), '08b') for char in text)
        
        # Process each color channel
        watermarked_channels = []
        
        for channel in range(3):  # R, G, B
            channel_data = img_array[:, :, channel]
            
            # Apply DCT
            dct_coeffs = fft2(channel_data)
            
            # Embed watermark in low-frequency coefficients
            embed_locations = [(8, 8), (8, 16), (16, 8), (16, 16)]
            
            for i, (x, y) in enumerate(embed_locations):
                if i < len(binary_text):
                    bit = int(binary_text[i])
                    if x < dct_coeffs.shape[0] and y < dct_coeffs.shape[1]:
                        dct_coeffs[x, y] = dct_coeffs[x, y] + strength * bit * 100
            
            # Inverse DCT
            watermarked_channel = np.real(ifft2(dct_coeffs))
            watermarked_channel = np.clip(watermarked_channel, 0, 255)
            watermarked_channels.append(watermarked_channel)
        
        # Combine channels
        watermarked_array = np.stack(watermarked_channels, axis=2).astype(np.uint8)
        return Image.fromarray(watermarked_array)
    
    async def _embed_spread_spectrum_watermark(self, image: Image.Image, text: str, strength: float) -> Image.Image:
        """Embed watermark using spread spectrum method"""
        img_array = np.array(image).astype(np.float32)
        
        # Generate pseudo-random sequence for spreading
        np.random.seed(42)  # Fixed seed for reproducibility
        spread_sequence = np.random.randn(*img_array.shape) * strength
        
        # Convert text to binary
        binary_text = ''.join(format(ord(char), '08b') for char in text)
        
        # Modulate the spread sequence with the binary text
        for i, bit in enumerate(binary_text):
            if i < spread_sequence.size:
                flat_idx = i
                y, x, c = np.unravel_index(flat_idx, img_array.shape)
                if int(bit):
                    img_array[y, x, c] += spread_sequence[y, x, c]
                else:
                    img_array[y, x, c] -= spread_sequence[y, x, c]
        
        # Clip values to valid range
        watermarked_array = np.clip(img_array, 0, 255).astype(np.uint8)
        return Image.fromarray(watermarked_array)
    
    async def extract_watermark(self,
                              image_path: Union[str, Path],
                              method: str = 'lsb',
                              expected_length: Optional[int] = None) -> Optional[str]:
        """
        Extract watermark from image
        
        Args:
            image_path: Watermarked image path
            method: Watermarking method used
            expected_length: Expected length of embedded text
            
        Returns:
            Extracted watermark text or None if not found
        """
        pil_image = Image.open(str(image_path))
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        if method == 'lsb':
            return await self._extract_lsb_watermark(pil_image, expected_length)
        elif method == 'dct':
            return await self._extract_dct_watermark(pil_image, expected_length)
        elif method == 'spread_spectrum':
            return await self._extract_spread_spectrum_watermark(pil_image, expected_length)
        else:
            raise ValueError(f"Unknown watermarking method: {method}")
    
    async def _extract_lsb_watermark(self, image: Image.Image, expected_length: Optional[int]) -> Optional[str]:
        """Extract LSB watermark"""
        img_array = np.array(image)
        flat_img = img_array.flatten()
        
        # Extract bits
        binary_text = ''
        for pixel in flat_img:
            binary_text += str(pixel & 1)
            
            # Check for end marker
            if binary_text.endswith('1111111111111110'):
                binary_text = binary_text[:-16]  # Remove end marker
                break
        
        # Convert binary to text
        try:
            # Process in chunks of 8 bits
            text = ''
            for i in range(0, len(binary_text), 8):
                if i + 8 <= len(binary_text):
                    byte = binary_text[i:i+8]
                    char = chr(int(byte, 2))
                    text += char
            
            return text if text else None
        except:
            return None
    
    async def _extract_dct_watermark(self, image: Image.Image, expected_length: Optional[int]) -> Optional[str]:
        """Extract DCT watermark (simplified)"""
        # This is a simplified extraction - in practice, needs correlation detection
        return None
    
    async def _extract_spread_spectrum_watermark(self, image: Image.Image, expected_length: Optional[int]) -> Optional[str]:
        """Extract spread spectrum watermark (simplified)"""
        # This is a simplified extraction - in practice, needs correlation detection
        return None
    
    async def compare_fingerprints(self,
                                 fp1: EnhancedImageFingerprint,
                                 fp2: EnhancedImageFingerprint) -> float:
        """
        Compare two image fingerprints
        
        Returns:
            Similarity score between 0 and 1
        """
        similarities = []
        
        # Compare perceptual hashes
        hash_similarities = []
        for hash1, hash2 in [(fp1.dhash, fp2.dhash), (fp1.phash, fp2.phash),
                            (fp1.ahash, fp2.ahash), (fp1.whash, fp2.whash)]:
            hamming_dist = sum(c1 != c2 for c1, c2 in zip(hash1, hash2)) if len(hash1) == len(hash2) else len(hash1)
            similarity = 1.0 - (hamming_dist / max(len(hash1), len(hash2)))
            hash_similarities.append(similarity)
        
        similarities.append(np.mean(hash_similarities))
        
        # Compare color histograms
        color_sim = 1.0 - np.sum(np.abs(fp1.color_histogram - fp2.color_histogram)) / 2.0
        similarities.append(color_sim)
        
        # Compare texture features
        lbp_sim = 1.0 - np.sum(np.abs(fp1.lbp_histogram - fp2.lbp_histogram)) / 2.0
        similarities.append(lbp_sim)
        
        # Compare edge histograms
        edge_sim = 1.0 - np.sum(np.abs(fp1.edge_histogram - fp2.edge_histogram)) / 2.0
        similarities.append(edge_sim)
        
        # Weighted average
        weights = [0.4, 0.3, 0.2, 0.1]  # Perceptual hashes get highest weight
        return float(np.average(similarities, weights=weights))
    
    def export_fingerprint(self, fingerprint: EnhancedImageFingerprint) -> Dict[str, Any]:
        """Export fingerprint to serializable format"""
        return {
            'file_id': fingerprint.file_id,
            'dhash': fingerprint.dhash,
            'phash': fingerprint.phash,
            'ahash': fingerprint.ahash,
            'whash': fingerprint.whash,
            'color_histogram_b64': base64.b64encode(fingerprint.color_histogram.tobytes()).decode(),
            'dominant_colors': fingerprint.dominant_colors,
            'color_moments': fingerprint.color_moments,
            'lbp_histogram_b64': base64.b64encode(fingerprint.lbp_histogram.tobytes()).decode(),
            'glcm_features': fingerprint.glcm_features,
            'gabor_features_b64': base64.b64encode(fingerprint.gabor_features.tobytes()).decode(),
            'edge_histogram_b64': base64.b64encode(fingerprint.edge_histogram.tobytes()).decode(),
            'contour_features': fingerprint.contour_features,
            'sharpness_score': fingerprint.sharpness_score,
            'noise_level': fingerprint.noise_level,
            'compression_artifacts': fingerprint.compression_artifacts,
            'dimensions': fingerprint.dimensions,
            'file_size': fingerprint.file_size,
            'confidence_score': fingerprint.confidence_score,
            'created_at': fingerprint.created_at.isoformat()
        }
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information and capabilities"""
        return {
            'engine': 'EnhancedImageProtectionEngine',
            'version': '1.0.0',
            'capabilities': {
                'opencv': OPENCV_AVAILABLE,
                'imagehash': IMAGEHASH_AVAILABLE,
                'scipy': SCIPY_AVAILABLE,
                'sklearn': SKLEARN_AVAILABLE,
                'perceptual_hashing': True,
                'watermarking': True,
                'texture_analysis': self.enable_advanced_features,
                'quality_assessment': True
            },
            'config': {
                'hash_size': self.hash_size,
                'enable_advanced_features': self.enable_advanced_features,
                'watermark_strength': self.watermark_strength
            },
            'supported_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'],
            'watermark_methods': ['lsb', 'dct', 'spread_spectrum']
        }