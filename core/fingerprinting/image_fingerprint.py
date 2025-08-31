"""IA Influencer Agent - Image Fingerprinting Engine
Advanced image fingerprinting for content protection and identification

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved to Fahed Mlaiel
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited
"""
import asyncio
import hashlib
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import cv2
import imagehash
from PIL import Image, ImageFilter
import json
import time
from concurrent.futures import ThreadPoolExecutor
import base64

logger = logging.getLogger(__name__)


class ImageFingerprintEngine:
    """    Professional image fingerprinting engine using multiple computer vision
    algorithms for robust content identification and protection
    """    
    def __init__(self, hash_size: int = 8, resize_dimension: int = 256):
        """        Initialize image fingerprinting engine
        
        Args:
            hash_size: Size for perceptual hashing algorithms
            resize_dimension: Standard dimension for image preprocessing
        """        self.hash_size = hash_size
        self.resize_dimension = resize_dimension
        self.similarity_threshold = 0.85
        
        # Initialize thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        logger.info(f"ImageFingerprintEngine initialized with hash_size={hash_size}")
    
    async def extract_fingerprint(
        self, 
        image_path: Union[str, Path],
        methods: List[str] = None
    ) -> Dict[str, any]:
        """        Extract comprehensive image fingerprint using multiple methods
        
        Args:
            image_path: Path to image file
            methods: List of fingerprinting methods to use
                    ['perceptual_hash', 'histogram', 'sift_features', 'texture_analysis']
        
        Returns:
            Dictionary containing all fingerprint data
        """        if methods is None:
            methods = ['perceptual_hash', 'histogram', 'sift_features', 'texture_analysis']
        
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Load and preprocess image
            image = await self._load_image(image_path)
            
            if image is None:
                raise ValueError(f"Cannot load image: {image_path}")
            
            # Get image metadata
            image_info = await self._get_image_info(image_path, image)
            
            fingerprint_data = {
                'file_path': str(image_path),
                'image_info': image_info,
                'file_size': image_path.stat().st_size,
                'created_at': time.time(),
                'methods': {}
            }
            
            # Execute fingerprinting methods
            if 'perceptual_hash' in methods:
                fingerprint_data['methods']['perceptual_hash'] = await self._extract_perceptual_hash(image)
            
            if 'histogram' in methods:
                fingerprint_data['methods']['histogram'] = await self._extract_histogram_features(image)
            
            if 'sift_features' in methods:
                fingerprint_data['methods']['sift_features'] = await self._extract_sift_features(image)
            
            if 'texture_analysis' in methods:
                fingerprint_data['methods']['texture_analysis'] = await self._extract_texture_features(image)
            
            # Generate combined hash
            fingerprint_data['combined_hash'] = self._generate_combined_hash(fingerprint_data['methods'])
            
            logger.info(f"Successfully extracted image fingerprint for {image_path.name}")
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Error extracting image fingerprint from {image_path}: {str(e)}")
            raise
    
    async def _load_image(self, image_path: Path) -> Optional[np.ndarray]:
        """Load and preprocess image"""        try:
            # Load with OpenCV (BGR format)
            image = cv2.imread(str(image_path))
            
            if image is None:
                # Try with PIL for other formats
                pil_image = Image.open(image_path)
                image = np.array(pil_image.convert('RGB'))
                # Convert RGB to BGR for OpenCV compatibility
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Resize for standardization while maintaining aspect ratio
            height, width = image.shape[:2]
            if max(height, width) > self.resize_dimension:
                if height > width:
                    new_height = self.resize_dimension
                    new_width = int((width / height) * self.resize_dimension)
                else:
                    new_width = self.resize_dimension
                    new_height = int((height / width) * self.resize_dimension)
                
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            return image
            
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            return None
    
    async def _get_image_info(self, image_path: Path, image: np.ndarray) -> Dict[str, any]:
        """Extract image metadata"""        try:
            height, width, channels = image.shape
            
            # Get file format
            file_format = image_path.suffix.lower()
            
            # Basic image statistics
            mean_intensity = np.mean(image)
            std_intensity = np.std(image)
            
            return {
                'width': int(width),
                'height': int(height),
                'channels': int(channels),
                'format': file_format,
                'mean_intensity': float(mean_intensity),
                'std_intensity': float(std_intensity),
                'aspect_ratio': float(width / height)
            }
            
        except Exception as e:
            logger.error(f"Error getting image info: {str(e)}")
            return {}
    
    async def _extract_perceptual_hash(self, image: np.ndarray) -> Dict[str, any]:
        """Extract multiple perceptual hash fingerprints"""        try:
            # Convert BGR to RGB for PIL
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Generate different types of perceptual hashes
            ahash = imagehash.average_hash(pil_image, hash_size=self.hash_size)
            dhash = imagehash.dhash(pil_image, hash_size=self.hash_size)
            phash = imagehash.phash(pil_image, hash_size=self.hash_size)
            whash = imagehash.whash(pil_image, hash_size=self.hash_size)
            
            # Color hash for color distribution
            chash = imagehash.colorhash(pil_image, binbits=3)
            
            # Convert hashes to strings and calculate combined hash
            hash_data = {
                'average_hash': str(ahash),
                'difference_hash': str(dhash),
                'perceptual_hash': str(phash),
                'wavelet_hash': str(whash),
                'color_hash': str(chash)
            }
            
            # Generate combined perceptual hash
            combined_hash_string = ''.join([str(h) for h in hash_data.values()])
            combined_hash = hashlib.sha256(combined_hash_string.encode()).hexdigest()
            
            return {
                'hashes': hash_data,
                'combined_hash': combined_hash,
                'hash_size': self.hash_size,
                'algorithm': 'perceptual_hash',
                'confidence': 0.94
            }
            
        except Exception as e:
            logger.error(f"Error in perceptual hash extraction: {str(e)}")
            return {'error': str(e), 'algorithm': 'perceptual_hash'}
    
    async def _extract_histogram_features(self, image: np.ndarray) -> Dict[str, any]:
        """Extract color histogram features"""        try:
            # Convert to different color spaces for comprehensive analysis
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            
            # Calculate histograms for BGR channels
            bgr_histograms = []
            for i in range(3):
                hist = cv2.calcHist([image], [i], None, [256], [0, 256])
                hist_normalized = hist.flatten() / np.sum(hist)
                bgr_histograms.append(hist_normalized.tolist())
            
            # Calculate histograms for HSV channels
            hsv_histograms = []
            hsv_ranges = [[0, 180], [0, 256], [0, 256]]
            hsv_bins = [180, 256, 256]
            for i in range(3):
                hist = cv2.calcHist([hsv_image], [i], None, [hsv_bins[i]], hsv_ranges[i])
                hist_normalized = hist.flatten() / np.sum(hist)
                hsv_histograms.append(hist_normalized.tolist())
            
            # Calculate dominant colors
            dominant_colors = await self._extract_dominant_colors(image)
            
            # Generate histogram hash
            all_histograms = np.concatenate([
                np.concatenate(bgr_histograms),
                np.concatenate(hsv_histograms)
            ])
            histogram_hash = hashlib.sha256(all_histograms.tobytes()).hexdigest()
            
            return {
                'bgr_histograms': bgr_histograms,
                'hsv_histograms': hsv_histograms,
                'dominant_colors': dominant_colors,
                'histogram_hash': histogram_hash,
                'algorithm': 'histogram',
                'confidence': 0.87
            }
            
        except Exception as e:
            logger.error(f"Error in histogram extraction: {str(e)}")
            return {'error': str(e), 'algorithm': 'histogram'}
    
    async def _extract_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[List[int]]:
        """Extract dominant colors using K-means clustering"""        try:
            # Reshape image to be a list of pixels
            pixels = image.reshape((-1, 3)).astype(np.float32)
            
            # Apply K-means clustering
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers back to uint8 and to list
            centers = centers.astype(np.uint8)
            dominant_colors = centers.tolist()
            
            return dominant_colors
            
        except Exception as e:
            logger.error(f"Error extracting dominant colors: {str(e)}")
            return []
    
    async def _extract_sift_features(self, image: np.ndarray) -> Dict[str, any]:
        """Extract SIFT (Scale-Invariant Feature Transform) features"""        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Initialize SIFT detector
            sift = cv2.SIFT_create()
            
            # Detect keypoints and compute descriptors
            keypoints, descriptors = sift.detectAndCompute(gray, None)
            
            if descriptors is not None and len(descriptors) > 0:
                # Calculate statistical features from descriptors
                descriptor_stats = {
                    'mean': np.mean(descriptors, axis=0).tolist(),
                    'std': np.std(descriptors, axis=0).tolist(),
                    'count': len(descriptors)
                }
                
                # Generate feature hash from descriptor statistics
                descriptor_array = np.concatenate([descriptor_stats['mean'], descriptor_stats['std']])
                feature_hash = hashlib.sha256(descriptor_array.tobytes()).hexdigest()
                
                # Extract keypoint locations for spatial distribution analysis
                keypoint_locations = [(kp.pt[0], kp.pt[1]) for kp in keypoints]
                
                return {
                    'keypoint_count': len(keypoints),
                    'descriptor_stats': descriptor_stats,
                    'keypoint_locations': keypoint_locations[:50],  # Limit to first 50
                    'feature_hash': feature_hash,
                    'algorithm': 'sift_features',
                    'confidence': 0.85
                }
            else:
                return {
                    'keypoint_count': 0,
                    'descriptor_stats': {'mean': [], 'std': [], 'count': 0},
                    'keypoint_locations': [],
                    'feature_hash': hashlib.sha256(b'no_features').hexdigest(),
                    'algorithm': 'sift_features',
                    'confidence': 0.0
                }
            
        except Exception as e:
            logger.error(f"Error in SIFT feature extraction: {str(e)}")
            return {'error': str(e), 'algorithm': 'sift_features'}
    
    async def _extract_texture_features(self, image: np.ndarray) -> Dict[str, any]:
        """Extract texture analysis features"""        try:
            # Convert to grayscale for texture analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Local Binary Pattern (LBP) texture analysis
            lbp_features = await self._calculate_lbp(gray)
            
            # Gabor filter responses for texture
            gabor_features = await self._calculate_gabor_features(gray)
            
            # Edge density and orientation
            edge_features = await self._calculate_edge_features(gray)
            
            # Combine all texture features
            all_texture_features = np.concatenate([
                lbp_features,
                gabor_features,
                edge_features
            ])
            
            texture_hash = hashlib.sha256(all_texture_features.tobytes()).hexdigest()
            
            return {
                'lbp_histogram': lbp_features.tolist(),
                'gabor_responses': gabor_features.tolist(),
                'edge_statistics': edge_features.tolist(),
                'texture_hash': texture_hash,
                'algorithm': 'texture_analysis',
                'confidence': 0.82
            }
            
        except Exception as e:
            logger.error(f"Error in texture analysis: {str(e)}")
            return {'error': str(e), 'algorithm': 'texture_analysis'}
    
    async def _calculate_lbp(self, gray_image: np.ndarray) -> np.ndarray:
        """Calculate Local Binary Pattern histogram"""        try:
            # Simple LBP implementation
            height, width = gray_image.shape
            lbp_image = np.zeros((height-2, width-2), dtype=np.uint8)
            
            for i in range(1, height-1):
                for j in range(1, width-1):
                    center = gray_image[i, j]
                    code = 0
                    
                    # 8-neighbor LBP
                    neighbors = [
                        gray_image[i-1, j-1], gray_image[i-1, j], gray_image[i-1, j+1],
                        gray_image[i, j+1], gray_image[i+1, j+1], gray_image[i+1, j],
                        gray_image[i+1, j-1], gray_image[i, j-1]
                    ]
                    
                    for k, neighbor in enumerate(neighbors):
                        if neighbor >= center:
                            code |= (1 << k)
                    
                    lbp_image[i-1, j-1] = code
            
            # Calculate histogram
            lbp_histogram = np.histogram(lbp_image.flatten(), bins=256, range=(0, 256))[0]
            lbp_histogram = lbp_histogram / np.sum(lbp_histogram)  # Normalize
            
            return lbp_histogram
            
        except Exception as e:
            logger.error(f"Error calculating LBP: {str(e)}")
            return np.zeros(256)
    
    async def _calculate_gabor_features(self, gray_image: np.ndarray) -> np.ndarray:
        """Calculate Gabor filter responses for texture analysis"""        try:
            # Define Gabor filter parameters
            orientations = [0, 45, 90, 135]  # degrees
            frequencies = [0.1, 0.3, 0.5]
            
            gabor_responses = []
            
            for orientation in orientations:
                for frequency in frequencies:
                    # Apply Gabor filter
                    kernel = cv2.getGaborKernel((21, 21), sigma=3, theta=np.radians(orientation), 
                                               lambd=1.0/frequency, gamma=0.5, psi=0, ktype=cv2.CV_32F)
                    filtered = cv2.filter2D(gray_image, cv2.CV_8UC3, kernel)
                    
                    # Calculate response statistics
                    mean_response = np.mean(filtered)
                    std_response = np.std(filtered)
                    
                    gabor_responses.extend([mean_response, std_response])
            
            return np.array(gabor_responses)
            
        except Exception as e:
            logger.error(f"Error calculating Gabor features: {str(e)}")
            return np.zeros(24)  # 4 orientations * 3 frequencies * 2 statistics
    
    async def _calculate_edge_features(self, gray_image: np.ndarray) -> np.ndarray:
        """Calculate edge-based texture features"""        try:
            # Sobel edge detection
            sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
            
            # Edge magnitude and direction
            edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            edge_direction = np.arctan2(sobel_y, sobel_x)
            
            # Edge statistics
            edge_density = np.sum(edge_magnitude > np.mean(edge_magnitude)) / edge_magnitude.size
            mean_magnitude = np.mean(edge_magnitude)
            std_magnitude = np.std(edge_magnitude)
            
            # Direction histogram
            direction_hist = np.histogram(edge_direction.flatten(), bins=8, range=(-np.pi, np.pi))[0]
            direction_hist = direction_hist / np.sum(direction_hist)
            
            # Combine edge features
            edge_features = np.array([edge_density, mean_magnitude, std_magnitude])
            edge_features = np.concatenate([edge_features, direction_hist])
            
            return edge_features
            
        except Exception as e:
            logger.error(f"Error calculating edge features: {str(e)}")
            return np.zeros(11)  # 3 statistics + 8 direction bins
    
    def _generate_combined_hash(self, methods_data: Dict[str, any]) -> str:
        """Generate combined hash from all fingerprinting methods"""        try:
            hash_parts = []
            
            for method, data in methods_data.items():
                if 'error' not in data:
                    # Extract primary hash from each method
                    if method == 'perceptual_hash' and 'combined_hash' in data:
                        hash_parts.append(data['combined_hash'])
                    elif method == 'histogram' and 'histogram_hash' in data:
                        hash_parts.append(data['histogram_hash'])
                    elif method == 'sift_features' and 'feature_hash' in data:
                        hash_parts.append(data['feature_hash'])
                    elif method == 'texture_analysis' and 'texture_hash' in data:
                        hash_parts.append(data['texture_hash'])
            
            # Combine all hashes
            combined_string = ''.join(sorted(hash_parts))
            combined_hash = hashlib.sha256(combined_string.encode()).hexdigest()
            
            return combined_hash
            
        except Exception as e:
            logger.error(f"Error generating combined hash: {str(e)}")
            return hashlib.sha256(str(time.time()).encode()).hexdigest()
    
    async def compare_fingerprints(
        self, 
        fingerprint1: Dict[str, any], 
        fingerprint2: Dict[str, any]
    ) -> Dict[str, float]:
        """        Compare two image fingerprints and return similarity scores
        
        Args:
            fingerprint1: First fingerprint data
            fingerprint2: Second fingerprint data
        
        Returns:
            Dictionary with similarity scores for each method
        """        similarities = {}
        
        try:
            # Compare each method
            for method in ['perceptual_hash', 'histogram', 'sift_features', 'texture_analysis']:
                if (method in fingerprint1.get('methods', {}) and 
                    method in fingerprint2.get('methods', {})):
                    
                    similarity = await self._compare_method(
                        fingerprint1['methods'][method],
                        fingerprint2['methods'][method],
                        method
                    )
                    similarities[method] = similarity
            
            # Overall similarity (weighted average)
            if similarities:
                weights = {'perceptual_hash': 0.4, 'histogram': 0.3, 'sift_features': 0.2, 'texture_analysis': 0.1}
                overall_similarity = sum(
                    similarities.get(method, 0) * weight 
                    for method, weight in weights.items()
                ) / sum(weights[method] for method in similarities.keys())
                
                similarities['overall'] = overall_similarity
            else:
                similarities['overall'] = 0.0
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error comparing image fingerprints: {str(e)}")
            return {'overall': 0.0, 'error': str(e)}
    
    async def _compare_method(
        self, 
        data1: Dict[str, any], 
        data2: Dict[str, any], 
        method: str
    ) -> float:
        """Compare two fingerprints using specific method"""        try:
            if 'error' in data1 or 'error' in data2:
                return 0.0
            
            if method == 'perceptual_hash':
                return self._compare_perceptual_hash(data1, data2)
            elif method == 'histogram':
                return self._compare_histogram(data1, data2)
            elif method == 'sift_features':
                return self._compare_sift_features(data1, data2)
            elif method == 'texture_analysis':
                return self._compare_texture_analysis(data1, data2)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error comparing {method}: {str(e)}")
            return 0.0
    
    def _compare_perceptual_hash(self, data1: Dict, data2: Dict) -> float:
        """Compare perceptual hash fingerprints"""        try:
            hashes1 = data1.get('hashes', {})
            hashes2 = data2.get('hashes', {})
            
            if not hashes1 or not hashes2:
                return 0.0
            
            # Compare each hash type
            similarities = []
            hash_types = ['average_hash', 'difference_hash', 'perceptual_hash', 'wavelet_hash', 'color_hash']
            
            for hash_type in hash_types:
                if hash_type in hashes1 and hash_type in hashes2:
                    h1 = hashes1[hash_type]
                    h2 = hashes2[hash_type]
                    
                    if h1 == h2:
                        similarities.append(1.0)
                    else:
                        # Calculate Hamming distance
                        if len(h1) == len(h2):
                            hamming_distance = sum(c1 != c2 for c1, c2 in zip(h1, h2))
                            similarity = 1.0 - (hamming_distance / len(h1))
                            similarities.append(max(0.0, similarity))
                        else:
                            similarities.append(0.0)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception:
            return 0.0
    
    def _compare_histogram(self, data1: Dict, data2: Dict) -> float:
        """Compare histogram features"""        try:
            # Compare BGR histograms
            bgr_hists1 = data1.get('bgr_histograms', [])
            bgr_hists2 = data2.get('bgr_histograms', [])
            
            # Compare HSV histograms
            hsv_hists1 = data1.get('hsv_histograms', [])
            hsv_hists2 = data2.get('hsv_histograms', [])
            
            similarities = []
            
            # Compare BGR channels
            for h1, h2 in zip(bgr_hists1, bgr_hists2):
                if len(h1) == len(h2) and len(h1) > 0:
                    h1_array = np.array(h1)
                    h2_array = np.array(h2)
                    # Bhattacharyya coefficient
                    bc = np.sum(np.sqrt(h1_array * h2_array))
                    similarities.append(bc)
            
            # Compare HSV channels
            for h1, h2 in zip(hsv_hists1, hsv_hists2):
                if len(h1) == len(h2) and len(h1) > 0:
                    h1_array = np.array(h1)
                    h2_array = np.array(h2)
                    # Bhattacharyya coefficient
                    bc = np.sum(np.sqrt(h1_array * h2_array))
                    similarities.append(bc)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception:
            return 0.0
    
    def _compare_sift_features(self, data1: Dict, data2: Dict) -> float:
        """Compare SIFT features"""        try:
            stats1 = data1.get('descriptor_stats', {})
            stats2 = data2.get('descriptor_stats', {})
            
            if not stats1 or not stats2 or stats1.get('count', 0) == 0 or stats2.get('count', 0) == 0:
                return 0.0
            
            # Compare descriptor means
            means1 = np.array(stats1.get('mean', []))
            means2 = np.array(stats2.get('mean', []))
            
            if len(means1) == len(means2) and len(means1) > 0:
                # Cosine similarity for descriptor means
                dot_product = np.dot(means1, means2)
                norm1 = np.linalg.norm(means1)
                norm2 = np.linalg.norm(means2)
                
                if norm1 > 0 and norm2 > 0:
                    similarity = dot_product / (norm1 * norm2)
                    return max(0.0, similarity)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _compare_texture_analysis(self, data1: Dict, data2: Dict) -> float:
        """Compare texture analysis features"""        try:
            # Compare LBP histograms
            lbp1 = np.array(data1.get('lbp_histogram', []))
            lbp2 = np.array(data2.get('lbp_histogram', []))
            
            # Compare Gabor responses
            gabor1 = np.array(data1.get('gabor_responses', []))
            gabor2 = np.array(data2.get('gabor_responses', []))
            
            similarities = []
            
            # LBP similarity
            if len(lbp1) == len(lbp2) and len(lbp1) > 0:
                lbp_similarity = np.sum(np.sqrt(lbp1 * lbp2))  # Bhattacharyya coefficient
                similarities.append(lbp_similarity)
            
            # Gabor similarity
            if len(gabor1) == len(gabor2) and len(gabor1) > 0:
                # Cosine similarity for Gabor responses
                dot_product = np.dot(gabor1, gabor2)
                norm1 = np.linalg.norm(gabor1)
                norm2 = np.linalg.norm(gabor2)
                
                if norm1 > 0 and norm2 > 0:
                    gabor_similarity = dot_product / (norm1 * norm2)
                    similarities.append(max(0.0, gabor_similarity))
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception:
            return 0.0
    
    async def batch_fingerprint(
        self, 
        image_paths: List[Union[str, Path]], 
        methods: List[str] = None
    ) -> List[Dict[str, any]]:
        """        Process multiple image files in batch
        
        Args:
            image_paths: List of image file paths
            methods: Fingerprinting methods to use
        
        Returns:
            List of fingerprint data for each file
        """        tasks = []
        for image_path in image_paths:
            task = self.extract_fingerprint(image_path, methods)
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log errors
            fingerprints = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing {image_paths[i]}: {str(result)}")
                    fingerprints.append({'error': str(result), 'file_path': str(image_paths[i])})
                else:
                    fingerprints.append(result)
            
            return fingerprints
            
        except Exception as e:
            logger.error(f"Error in batch image fingerprinting: {str(e)}")
            raise
    
    def get_engine_info(self) -> Dict[str, any]:
        """Get engine configuration and capabilities"""        return {
            'engine': 'ImageFingerprintEngine',
            'version': '1.0.0',
            'hash_size': self.hash_size,
            'resize_dimension': self.resize_dimension,
            'similarity_threshold': self.similarity_threshold,
            'supported_methods': ['perceptual_hash', 'histogram', 'sift_features', 'texture_analysis'],
            'supported_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'],
            'capabilities': {
                'perceptual_hashing': True,
                'color_analysis': True,
                'feature_detection': True,
                'texture_analysis': True,
                'batch_processing': True,
                'similarity_matching': True
            }
        }
