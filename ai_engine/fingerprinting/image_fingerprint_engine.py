"""Advanced Image Fingerprinting Engine
Image fingerprinting with CLIP embeddings, perceptual hashing, and SIFT features.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import numpy as np
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import io

# Image processing
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import imagehash

# ML and deep learning
import torch
import clip
from torchvision import transforms
import torch.nn.functional as F

# Feature detection
from skimage import feature, measure
import matplotlib.pyplot as plt

from ...core.logging import logger
from ...config import settings


@dataclass
class ImageFingerprint:
    """Image fingerprint data structure"""    file_id: str
    clip_embedding: List[float]
    perceptual_hashes: Dict[str, str]
    sift_features: Dict[str, Any]
    color_histogram: Dict[str, List[float]]
    texture_features: Dict[str, Any]
    edge_features: Dict[str, Any]
    geometric_features: Dict[str, Any]
    visual_features: Dict[str, Any]
    image_properties: Dict[str, Any]
    confidence_score: float
    created_at: datetime


class ImageFingerprintEngine:
    """    Advanced image fingerprinting engine supporting:
    - CLIP embeddings for semantic similarity
    - Multiple perceptual hashing algorithms
    - SIFT feature detection
    - Color histogram analysis
    - Texture analysis (LBP, Gabor filters)
    - Edge detection features
    - Geometric feature analysis
    """    
    def __init__(self):
        self.clip_model = None
        self.clip_preprocess = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize CLIP model
        self._init_clip_model()
        
        # Hash configurations
        self.hash_size = 16
        self.sift_max_features = 500
        
        logger.info(f"ImageFingerprintEngine initialized on {self.device}")
    
    def _init_clip_model(self):
        """Initialize CLIP model for semantic embeddings"""        try:
            self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)
            self.clip_model.eval()
            logger.info("CLIP model loaded successfully")
            
        except Exception as e:
            logger.warning(f"Could not load CLIP model: {str(e)}")
            self.clip_model = None
    
    async def generate_fingerprint(self, image_file_path: str, metadata: Optional[Dict] = None) -> ImageFingerprint:
        """        Generate comprehensive image fingerprint
        
        Args:
            image_file_path: Path to image file
            metadata: Optional metadata about the image
            
        Returns:
            ImageFingerprint: Complete fingerprint data
        """        try:
            logger.info(f"Generating image fingerprint for: {image_file_path}")
            
            # Load image
            image = Image.open(image_file_path).convert('RGB')
            cv_image = cv2.imread(image_file_path)
            cv_image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            
            # Generate file ID
            file_id = await self._generate_file_id(image_file_path, image)
            
            # Parallel fingerprint generation
            fingerprint_tasks = [
                self._generate_clip_embedding(image),
                self._generate_perceptual_hashes(image),
                self._extract_sift_features(cv_image),
                self._extract_color_histogram(cv_image_rgb),
                self._extract_texture_features(cv_image),
                self._extract_edge_features(cv_image),
                self._extract_geometric_features(cv_image),
                self._extract_visual_features(image),
                self._extract_image_properties(image)
            ]
            
            results = await asyncio.gather(*fingerprint_tasks)
            
            # Unpack results
            clip_embedding, perceptual_hashes, sift_features, color_histogram, \
            texture_features, edge_features, geometric_features, visual_features, \
            image_properties = results
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(results)
            
            fingerprint = ImageFingerprint(
                file_id=file_id,
                clip_embedding=clip_embedding,
                perceptual_hashes=perceptual_hashes,
                sift_features=sift_features,
                color_histogram=color_histogram,
                texture_features=texture_features,
                edge_features=edge_features,
                geometric_features=geometric_features,
                visual_features=visual_features,
                image_properties=image_properties,
                confidence_score=confidence_score,
                created_at=datetime.utcnow()
            )
            
            logger.info(f"Image fingerprint generated successfully. Confidence: {confidence_score:.3f}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error generating image fingerprint: {str(e)}")
            raise
    
    async def _generate_file_id(self, file_path: str, image: Image.Image) -> str:
        """Generate unique file ID"""        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        content_hash = hashlib.sha256(image_bytes.getvalue()).hexdigest()
        return f"image_{content_hash[:16]}"
    
    async def _generate_clip_embedding(self, image: Image.Image) -> List[float]:
        """Generate CLIP embedding for semantic similarity"""        try:
            if self.clip_model is None:
                return []
            
            # Preprocess image
            image_input = self.clip_preprocess(image).unsqueeze(0).to(self.device)
            
            # Generate embedding
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_input)
                image_features = F.normalize(image_features, dim=-1)
                embedding = image_features.cpu().numpy().flatten().tolist()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating CLIP embedding: {str(e)}")
            return []
    
    async def _generate_perceptual_hashes(self, image: Image.Image) -> Dict[str, str]:
        """Generate multiple perceptual hashes for robustness"""        try:
            hashes = {}
            
            # pHash (perceptual hash)
            hashes['phash'] = str(imagehash.phash(image, hash_size=self.hash_size))
            
            # aHash (average hash)
            hashes['ahash'] = str(imagehash.average_hash(image, hash_size=self.hash_size))
            
            # dHash (difference hash)
            hashes['dhash'] = str(imagehash.dhash(image, hash_size=self.hash_size))
            
            # wHash (wavelet hash)
            hashes['whash'] = str(imagehash.whash(image, hash_size=self.hash_size))
            
            # Colorhash
            hashes['colorhash'] = str(imagehash.colorhash(image))
            
            return hashes
            
        except Exception as e:
            logger.error(f"Error generating perceptual hashes: {str(e)}")
            return {}
    
    async def _extract_sift_features(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Extract SIFT features for geometric matching"""        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Initialize SIFT detector
            sift = cv2.SIFT_create(nfeatures=self.sift_max_features)
            
            # Detect keypoints and descriptors
            keypoints, descriptors = sift.detectAndCompute(gray, None)
            
            if descriptors is not None:
                # Statistical analysis of descriptors
                feature_stats = {
                    'num_keypoints': len(keypoints),
                    'descriptor_mean': np.mean(descriptors, axis=0).tolist(),
                    'descriptor_std': np.std(descriptors, axis=0).tolist(),
                    'keypoint_orientations': [kp.angle for kp in keypoints],
                    'keypoint_scales': [kp.size for kp in keypoints],
                    'keypoint_responses': [kp.response for kp in keypoints]
                }
            else:
                feature_stats = {
                    'num_keypoints': 0,
                    'descriptor_mean': [],
                    'descriptor_std': [],
                    'keypoint_orientations': [],
                    'keypoint_scales': [],
                    'keypoint_responses': []
                }
            
            return feature_stats
            
        except Exception as e:
            logger.error(f"Error extracting SIFT features: {str(e)}")
            return {}
    
    async def _extract_color_histogram(self, image: np.ndarray) -> Dict[str, List[float]]:
        """Extract color histograms in multiple color spaces"""        try:
            histograms = {}
            
            # RGB histogram
            hist_r = cv2.calcHist([image], [0], None, [64], [0, 256])
            hist_g = cv2.calcHist([image], [1], None, [64], [0, 256])
            hist_b = cv2.calcHist([image], [2], None, [64], [0, 256])
            
            histograms['rgb'] = {
                'red': cv2.normalize(hist_r, hist_r).flatten().tolist(),
                'green': cv2.normalize(hist_g, hist_g).flatten().tolist(),
                'blue': cv2.normalize(hist_b, hist_b).flatten().tolist()
            }
            
            # HSV histogram
            hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            hist_h = cv2.calcHist([hsv_image], [0], None, [64], [0, 180])
            hist_s = cv2.calcHist([hsv_image], [1], None, [64], [0, 256])
            hist_v = cv2.calcHist([hsv_image], [2], None, [64], [0, 256])
            
            histograms['hsv'] = {
                'hue': cv2.normalize(hist_h, hist_h).flatten().tolist(),
                'saturation': cv2.normalize(hist_s, hist_s).flatten().tolist(),
                'value': cv2.normalize(hist_v, hist_v).flatten().tolist()
            }
            
            # LAB histogram
            lab_image = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            hist_l = cv2.calcHist([lab_image], [0], None, [64], [0, 256])
            hist_a = cv2.calcHist([lab_image], [1], None, [64], [0, 256])
            hist_b_lab = cv2.calcHist([lab_image], [2], None, [64], [0, 256])
            
            histograms['lab'] = {
                'lightness': cv2.normalize(hist_l, hist_l).flatten().tolist(),
                'a_channel': cv2.normalize(hist_a, hist_a).flatten().tolist(),
                'b_channel': cv2.normalize(hist_b_lab, hist_b_lab).flatten().tolist()
            }
            
            # Dominant colors
            histograms['dominant_colors'] = await self._get_dominant_colors(image)
            
            return histograms
            
        except Exception as e:
            logger.error(f"Error extracting color histogram: {str(e)}")
            return {}
    
    async def _get_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[List[int]]:
        """Get dominant colors using K-means clustering"""        try:
            data = image.reshape((-1, 3))
            data = np.float32(data)
            
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            dominant_colors = centers.astype(int).tolist()
            return dominant_colors
            
        except Exception as e:
            logger.error(f"Error getting dominant colors: {str(e)}")
            return []
    
    async def _extract_texture_features(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Extract texture features using LBP and statistical measures"""        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            texture_features = {}
            
            # Local Binary Pattern (LBP)
            radius = 3
            n_points = 8 * radius
            lbp = feature.local_binary_pattern(gray, n_points, radius, method='uniform')
            
            # LBP histogram
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=n_points + 2, range=(0, n_points + 2))
            lbp_hist = lbp_hist.astype(float)
            lbp_hist /= (lbp_hist.sum() + 1e-7)  # Normalize
            
            texture_features['lbp_histogram'] = lbp_hist.tolist()
            
            # Gray-Level Co-occurrence Matrix (GLCM) properties
            glcm_props = ['contrast', 'dissimilarity', 'homogeneity', 'energy']
            glcm_features = {}
            
            try:
                from skimage.feature import greycomatrix, greycoprops
                
                # Compute GLCM
                glcm = greycomatrix(gray, distances=[1], angles=[0, 45, 90, 135], 
                                  levels=256, symmetric=True, normed=True)
                
                for prop in glcm_props:
                    glcm_features[prop] = greycoprops(glcm, prop).flatten().tolist()
                
                texture_features['glcm'] = glcm_features
                
            except Exception as e:
                logger.warning(f"Could not compute GLCM features: {str(e)}")
                texture_features['glcm'] = {}
            
            # Basic statistical measures
            texture_features['statistics'] = {
                'mean': float(np.mean(gray)),
                'std': float(np.std(gray)),
                'skewness': float(self._calculate_skewness(gray)),
                'kurtosis': float(self._calculate_kurtosis(gray)),
                'entropy': float(self._calculate_entropy(gray))
            }
            
            return texture_features
            
        except Exception as e:
            logger.error(f"Error extracting texture features: {str(e)}")
            return {}
    
    def _calculate_skewness(self, image: np.ndarray) -> float:
        """Calculate skewness of pixel intensity distribution"""        mean = np.mean(image)
        std = np.std(image)
        if std == 0:
            return 0.0
        return np.mean(((image - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, image: np.ndarray) -> float:
        """Calculate kurtosis of pixel intensity distribution"""        mean = np.mean(image)
        std = np.std(image)
        if std == 0:
            return 0.0
        return np.mean(((image - mean) / std) ** 4) - 3
    
    def _calculate_entropy(self, image: np.ndarray) -> float:
        """Calculate entropy of pixel intensity distribution"""        hist, _ = np.histogram(image, bins=256, range=(0, 256))
        hist = hist / hist.sum()
        hist = hist[hist > 0]  # Remove zeros
        return -np.sum(hist * np.log2(hist))
    
    async def _extract_edge_features(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Extract edge detection features"""        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            edge_features = {}
            
            # Canny edge detection
            edges_canny = cv2.Canny(gray, 50, 150)
            edge_features['canny_edge_density'] = float(np.sum(edges_canny > 0) / edges_canny.size)
            
            # Sobel edge detection
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            
            edge_features['sobel_statistics'] = {
                'mean_magnitude': float(np.mean(sobel_magnitude)),
                'std_magnitude': float(np.std(sobel_magnitude)),
                'max_magnitude': float(np.max(sobel_magnitude))
            }
            
            # Laplacian edge detection
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            edge_features['laplacian_variance'] = float(laplacian.var())
            
            # Hough line detection
            lines = cv2.HoughLines(edges_canny, 1, np.pi/180, threshold=100)
            edge_features['num_lines'] = len(lines) if lines is not None else 0
            
            return edge_features
            
        except Exception as e:
            logger.error(f"Error extracting edge features: {str(e)}")
            return {}
    
    async def _extract_geometric_features(self, cv_image: np.ndarray) -> Dict[str, Any]:
        """Extract geometric features like contours and shapes"""        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            geometric_features = {}
            
            # Find contours
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Contour statistics
                areas = [cv2.contourArea(contour) for contour in contours]
                perimeters = [cv2.arcLength(contour, True) for contour in contours]
                
                geometric_features['contour_statistics'] = {
                    'num_contours': len(contours),
                    'mean_area': float(np.mean(areas)) if areas else 0.0,
                    'max_area': float(np.max(areas)) if areas else 0.0,
                    'mean_perimeter': float(np.mean(perimeters)) if perimeters else 0.0,
                    'area_to_perimeter_ratio': float(np.mean([a/p if p > 0 else 0 for a, p in zip(areas, perimeters)]))
                }
                
                # Shape analysis for largest contour
                if contours:
                    largest_contour = max(contours, key=cv2.contourArea)
                    
                    # Bounding rectangle
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Convex hull
                    hull = cv2.convexHull(largest_contour)
                    hull_area = cv2.contourArea(hull)
                    solidity = cv2.contourArea(largest_contour) / hull_area if hull_area > 0 else 0
                    
                    geometric_features['shape_analysis'] = {
                        'aspect_ratio': float(aspect_ratio),
                        'solidity': float(solidity),
                        'extent': float(cv2.contourArea(largest_contour) / (w * h)) if w * h > 0 else 0
                    }
            else:
                geometric_features['contour_statistics'] = {
                    'num_contours': 0,
                    'mean_area': 0.0,
                    'max_area': 0.0,
                    'mean_perimeter': 0.0,
                    'area_to_perimeter_ratio': 0.0
                }
                geometric_features['shape_analysis'] = {
                    'aspect_ratio': 0.0,
                    'solidity': 0.0,
                    'extent': 0.0
                }
            
            return geometric_features
            
        except Exception as e:
            logger.error(f"Error extracting geometric features: {str(e)}")
            return {}
    
    async def _extract_visual_features(self, image: Image.Image) -> Dict[str, Any]:
        """Extract high-level visual features"""        try:
            visual_features = {}
            
            # Image properties
            width, height = image.size
            visual_features['aspect_ratio'] = width / height if height > 0 else 0
            visual_features['resolution'] = width * height
            
            # Color space analysis
            # Convert to different color spaces and analyze
            hsv_image = image.convert('HSV')
            
            # Brightness analysis
            grayscale = image.convert('L')
            pixels = list(grayscale.getdata())
            visual_features['brightness'] = {
                'mean': float(np.mean(pixels)),
                'std': float(np.std(pixels)),
                'min': float(np.min(pixels)),
                'max': float(np.max(pixels))
            }
            
            # Contrast analysis
            enhancer = ImageEnhance.Contrast(image)
            contrast_img = enhancer.enhance(2.0)
            visual_features['has_high_contrast'] = True  # Simplified
            
            # Blur detection using Laplacian variance
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            visual_features['blur_score'] = float(laplacian_var)
            visual_features['is_blurry'] = laplacian_var < 100  # Threshold for blur detection
            
            return visual_features
            
        except Exception as e:
            logger.error(f"Error extracting visual features: {str(e)}")
            return {}
    
    async def _extract_image_properties(self, image: Image.Image) -> Dict[str, Any]:
        """Extract basic image properties and metadata"""        try:
            properties = {}
            
            # Basic properties
            properties['width'] = image.width
            properties['height'] = image.height
            properties['mode'] = image.mode
            properties['format'] = image.format
            
            # File size estimation
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            properties['estimated_size'] = len(img_bytes.getvalue())
            
            # Color channels
            if image.mode == 'RGB':
                properties['num_channels'] = 3
            elif image.mode == 'RGBA':
                properties['num_channels'] = 4
            elif image.mode == 'L':
                properties['num_channels'] = 1
            else:
                properties['num_channels'] = len(image.getbands())
            
            # Histogram statistics for each channel
            if image.mode in ['RGB', 'RGBA']:
                r, g, b = image.split()[:3]
                properties['channel_stats'] = {
                    'red': {'mean': float(np.mean(list(r.getdata()))), 'std': float(np.std(list(r.getdata())))},
                    'green': {'mean': float(np.mean(list(g.getdata()))), 'std': float(np.std(list(g.getdata())))},
                    'blue': {'mean': float(np.mean(list(b.getdata()))), 'std': float(np.std(list(b.getdata())))}
                }
            
            return properties
            
        except Exception as e:
            logger.error(f"Error extracting image properties: {str(e)}")
            return {}
    
    async def _calculate_confidence_score(self, results: List[Any]) -> float:
        """Calculate overall confidence score"""        try:
            confidence_factors = []
            
            # CLIP embedding quality
            clip_embedding = results[0]
            if clip_embedding and len(clip_embedding) > 0:
                confidence_factors.append(0.95)
            else:
                confidence_factors.append(0.3)
            
            # Perceptual hashes quality
            perceptual_hashes = results[1]
            if perceptual_hashes and len(perceptual_hashes) >= 4:
                confidence_factors.append(0.9)
            else:
                confidence_factors.append(0.5)
            
            # SIFT features quality
            sift_features = results[2]
            if sift_features and sift_features.get('num_keypoints', 0) > 10:
                confidence_factors.append(0.85)
            else:
                confidence_factors.append(0.4)
            
            # Color histogram quality
            color_histogram = results[3]
            if color_histogram and len(color_histogram) > 0:
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.3)
            
            return float(np.mean(confidence_factors))
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {str(e)}")
            return 0.5
    
    async def compare_fingerprints(self, fp1: ImageFingerprint, fp2: ImageFingerprint) -> float:
        """        Compare two image fingerprints and return similarity score (0-1)
        
        Args:
            fp1: First fingerprint
            fp2: Second fingerprint
            
        Returns:
            float: Similarity score between 0 and 1
        """        try:
            similarities = []
            
            # Compare CLIP embeddings (semantic similarity)
            if fp1.clip_embedding and fp2.clip_embedding:
                clip_similarity = await self._compare_clip_embeddings(fp1.clip_embedding, fp2.clip_embedding)
                similarities.append(clip_similarity)
            
            # Compare perceptual hashes
            if fp1.perceptual_hashes and fp2.perceptual_hashes:
                hash_similarity = await self._compare_perceptual_hashes(fp1.perceptual_hashes, fp2.perceptual_hashes)
                similarities.append(hash_similarity)
            
            # Compare SIFT features
            if fp1.sift_features and fp2.sift_features:
                sift_similarity = await self._compare_sift_features(fp1.sift_features, fp2.sift_features)
                similarities.append(sift_similarity)
            
            # Compare color histograms
            if fp1.color_histogram and fp2.color_histogram:
                color_similarity = await self._compare_color_histograms(fp1.color_histogram, fp2.color_histogram)
                similarities.append(color_similarity)
            
            # Weighted average (CLIP has highest weight for semantic similarity)
            weights = [0.4, 0.3, 0.2, 0.1]
            similarity_score = sum(s * w for s, w in zip(similarities, weights[:len(similarities)]))
            
            return min(1.0, max(0.0, similarity_score))
            
        except Exception as e:
            logger.error(f"Error comparing image fingerprints: {str(e)}")
            return 0.0
    
    async def _compare_clip_embeddings(self, emb1: List[float], emb2: List[float]) -> float:
        """Compare CLIP embeddings using cosine similarity"""        try:
            if not emb1 or not emb2:
                return 0.0
            
            # Convert to numpy arrays
            vec1 = np.array(emb1)
            vec2 = np.array(emb2)
            
            # Calculate cosine similarity
            cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            
            # Convert to 0-1 range (cosine similarity is -1 to 1)
            similarity = (cosine_sim + 1) / 2
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error comparing CLIP embeddings: {str(e)}")
            return 0.0
    
    async def _compare_perceptual_hashes(self, hashes1: Dict[str, str], hashes2: Dict[str, str]) -> float:
        """Compare perceptual hashes"""        try:
            similarities = []
            
            for hash_type in ['phash', 'ahash', 'dhash', 'whash']:
                if hash_type in hashes1 and hash_type in hashes2:
                    # Calculate Hamming distance
                    hash1 = imagehash.hex_to_hash(hashes1[hash_type])
                    hash2 = imagehash.hex_to_hash(hashes2[hash_type])
                    
                    hamming_distance = hash1 - hash2
                    max_distance = len(hash1.hash.flatten())
                    
                    # Convert to similarity (0-1)
                    similarity = 1 - (hamming_distance / max_distance)
                    similarities.append(similarity)
            
            return float(np.mean(similarities)) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Error comparing perceptual hashes: {str(e)}")
            return 0.0
    
    async def _compare_sift_features(self, sift1: Dict[str, Any], sift2: Dict[str, Any]) -> float:
        """Compare SIFT features"""        try:
            # Compare number of keypoints
            kp1_count = sift1.get('num_keypoints', 0)
            kp2_count = sift2.get('num_keypoints', 0)
            
            if kp1_count == 0 and kp2_count == 0:
                return 1.0
            elif kp1_count == 0 or kp2_count == 0:
                return 0.0
            
            # Compare keypoint count similarity
            count_similarity = min(kp1_count, kp2_count) / max(kp1_count, kp2_count)
            
            # Compare descriptor statistics
            desc_similarities = []
            
            if 'descriptor_mean' in sift1 and 'descriptor_mean' in sift2:
                desc1_mean = np.array(sift1['descriptor_mean'])
                desc2_mean = np.array(sift2['descriptor_mean'])
                
                if len(desc1_mean) > 0 and len(desc2_mean) > 0:
                    desc_similarity = 1 - np.linalg.norm(desc1_mean - desc2_mean) / np.linalg.norm(desc1_mean + desc2_mean + 1e-10)
                    desc_similarities.append(max(0, desc_similarity))
            
            # Combine similarities
            similarities = [count_similarity] + desc_similarities
            return float(np.mean(similarities))
            
        except Exception as e:
            logger.error(f"Error comparing SIFT features: {str(e)}")
            return 0.0
    
    async def _compare_color_histograms(self, hist1: Dict[str, Any], hist2: Dict[str, Any]) -> float:
        """Compare color histograms"""        try:
            similarities = []
            
            # Compare RGB histograms
            if 'rgb' in hist1 and 'rgb' in hist2:
                for channel in ['red', 'green', 'blue']:
                    if channel in hist1['rgb'] and channel in hist2['rgb']:
                        h1 = np.array(hist1['rgb'][channel])
                        h2 = np.array(hist2['rgb'][channel])
                        
                        # Calculate correlation
                        correlation = np.corrcoef(h1, h2)[0, 1]
                        if not np.isnan(correlation):
                            similarities.append(max(0, correlation))
            
            # Compare HSV histograms
            if 'hsv' in hist1 and 'hsv' in hist2:
                for channel in ['hue', 'saturation', 'value']:
                    if channel in hist1['hsv'] and channel in hist2['hsv']:
                        h1 = np.array(hist1['hsv'][channel])
                        h2 = np.array(hist2['hsv'][channel])
                        
                        correlation = np.corrcoef(h1, h2)[0, 1]
                        if not np.isnan(correlation):
                            similarities.append(max(0, correlation))
            
            return float(np.mean(similarities)) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Error comparing color histograms: {str(e)}")
            return 0.0