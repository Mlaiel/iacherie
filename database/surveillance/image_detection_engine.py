"""Image Detection Engine Module
============================

Advanced image fingerprinting and detection engine for visual content surveillance.
Implements state-of-the-art computer vision and image analysis algorithms.

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All Rights Reserved.

WARNING: This code and concept are protected intellectual property.
Any unauthorized use, copying, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""import asyncio
import logging
import numpy as np
import cv2
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import chromadb
from scipy.spatial.distance import cosine, euclidean
from dataclasses import dataclass
import io
import hashlib
import json
import base64
from PIL import Image, ImageFilter, ImageEnhance
import imagehash
from skimage import feature, segmentation, measure
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


@dataclass
class ImageFingerprint:
    """Image fingerprint data structure."""    fingerprint_id: str
    user_id: str
    title: str
    image_format: str
    dimensions: Tuple[int, int]
    file_size: int
    visual_features: Dict[str, Any]
    hash_signatures: Dict[str, str]
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class ImageMatch:
    """Image match result structure."""    original_fingerprint_id: str
    detected_url: str
    similarity_score: float
    confidence_level: float
    match_regions: List[Tuple[int, int, int, int]]  # Bounding boxes of matching regions
    hash_matches: Dict[str, float]
    feature_matches: Dict[str, float]
    platform: str
    detected_at: datetime
    match_details: Dict[str, Any]


class ImageFeatureExtractor:
    """Advanced image feature extraction for fingerprinting."""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.target_size = config.get("target_size", (512, 512))
        self.histogram_bins = config.get("histogram_bins", 64)
        self.orb_features = config.get("orb_features", 500)
        self.sift_features = config.get("sift_features", 100)
        
        # Initialize feature detectors
        self.orb_detector = cv2.ORB_create(nfeatures=self.orb_features)
        self.sift_detector = cv2.SIFT_create(nfeatures=self.sift_features)
        
        # SURF detector (if available)
        try:
            self.surf_detector = cv2.xfeatures2d.SURF_create(400)
        except:
            self.surf_detector = None
        
    async def extract_features(self, image_data: bytes) -> Dict[str, Any]:
        """Extract comprehensive image features from image data."""        try:
            # Load image from bytes
            image_array = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Could not decode image data")
            
            # Get image properties
            height, width, channels = image.shape
            
            features = {
                "dimensions": (width, height),
                "channels": channels,
                "file_size": len(image_data)
            }
            
            # Resize image for consistent processing
            image_resized = cv2.resize(image, self.target_size)
            
            # Perceptual hashes
            hash_features = await self._extract_hash_features(image_data)
            features.update(hash_features)
            
            # Color features
            color_features = await self._extract_color_features(image_resized)
            features.update(color_features)
            
            # Texture features
            texture_features = await self._extract_texture_features(image_resized)
            features.update(texture_features)
            
            # Keypoint features
            keypoint_features = await self._extract_keypoint_features(image_resized)
            features.update(keypoint_features)
            
            # Edge features
            edge_features = await self._extract_edge_features(image_resized)
            features.update(edge_features)
            
            # Histogram features
            histogram_features = await self._extract_histogram_features(image_resized)
            features.update(histogram_features)
            
            # Shape features
            shape_features = await self._extract_shape_features(image_resized)
            features.update(shape_features)
            
            logger.info(f"Extracted image features: {len(features)} feature sets")
            return features
            
        except Exception as e:
            logger.error(f"Image feature extraction failed: {e}")
            raise
    
    async def _extract_hash_features(self, image_data: bytes) -> Dict[str, Any]:
        """Extract various perceptual hashes."""        features = {}
        
        try:
            # Load with PIL for hash computation
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Perceptual hash
            features["phash"] = str(imagehash.phash(pil_image))
            
            # Average hash
            features["ahash"] = str(imagehash.average_hash(pil_image))
            
            # Difference hash
            features["dhash"] = str(imagehash.dhash(pil_image))
            
            # Wavelet hash
            features["whash"] = str(imagehash.whash(pil_image))
            
            # Color hash
            features["colorhash"] = str(imagehash.colorhash(pil_image))
            
        except Exception as e:
            logger.error(f"Hash feature extraction failed: {e}")
        
        return features
    
    async def _extract_color_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract color-based features."""        features = {}
        
        try:
            # Color histograms in different color spaces
            
            # RGB histograms
            for i, color in enumerate(['blue', 'green', 'red']):
                hist = cv2.calcHist([image], [i], None, [self.histogram_bins], [0, 256])
                features[f"rgb_{color}_hist"] = hist.flatten()
                features[f"rgb_{color}_mean"] = np.mean(image[:, :, i])
                features[f"rgb_{color}_std"] = np.std(image[:, :, i])
            
            # HSV color space
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            for i, component in enumerate(['hue', 'saturation', 'value']):
                hist = cv2.calcHist([hsv_image], [i], None, [self.histogram_bins], [0, 256])
                features[f"hsv_{component}_hist"] = hist.flatten()
                features[f"hsv_{component}_mean"] = np.mean(hsv_image[:, :, i])
                features[f"hsv_{component}_std"] = np.std(hsv_image[:, :, i])
            
            # LAB color space
            lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            for i, component in enumerate(['lightness', 'a_channel', 'b_channel']):
                hist = cv2.calcHist([lab_image], [i], None, [self.histogram_bins], [0, 256])
                features[f"lab_{component}_hist"] = hist.flatten()
                features[f"lab_{component}_mean"] = np.mean(lab_image[:, :, i])
                features[f"lab_{component}_std"] = np.std(lab_image[:, :, i])
            
            # Color moments
            features["color_moments"] = []
            for channel in range(image.shape[2]):
                channel_data = image[:, :, channel].flatten()
                moment1 = np.mean(channel_data)  # Mean
                moment2 = np.std(channel_data)   # Standard deviation
                moment3 = np.mean((channel_data - moment1) ** 3) / (moment2 ** 3)  # Skewness
                features["color_moments"].extend([moment1, moment2, moment3])
            
            # Dominant colors (simplified K-means)
            pixels = image.reshape(-1, 3).astype(np.float32)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(pixels, 5, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            features["dominant_colors"] = centers.flatten()
            
        except Exception as e:
            logger.error(f"Color feature extraction failed: {e}")
        
        return features
    
    async def _extract_texture_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract texture-based features."""        features = {}
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Local Binary Pattern (LBP)
            lbp = feature.local_binary_pattern(gray, 24, 8, method='uniform')
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=26, range=(0, 25), density=True)
            features["lbp_histogram"] = lbp_hist
            
            # Gray Level Co-occurrence Matrix (GLCM) features
            distances = [1, 2, 3]
            angles = [0, 45, 90, 135]
            glcm_features = []
            
            for distance in distances:
                for angle in angles:
                    try:
                        glcm = feature.graycomatrix(gray, [distance], [np.radians(angle)], levels=256, symmetric=True, normed=True)
                        
                        # GLCM properties
                        contrast = feature.graycoprops(glcm, 'contrast')[0, 0]
                        dissimilarity = feature.graycoprops(glcm, 'dissimilarity')[0, 0]
                        homogeneity = feature.graycoprops(glcm, 'homogeneity')[0, 0]
                        energy = feature.graycoprops(glcm, 'energy')[0, 0]
                        correlation = feature.graycoprops(glcm, 'correlation')[0, 0]
                        
                        glcm_features.extend([contrast, dissimilarity, homogeneity, energy, correlation])
                    except:
                        continue
            
            features["glcm_features"] = np.array(glcm_features)
            
            # Gabor filter responses
            gabor_features = []
            frequencies = [0.1, 0.3, 0.5]
            angles = [0, 45, 90, 135]
            
            for freq in frequencies:
                for angle in angles:
                    try:
                        real, _ = feature.gabor(gray, frequency=freq, theta=np.radians(angle))
                        gabor_features.extend([np.mean(real), np.std(real)])
                    except:
                        continue
            
            features["gabor_features"] = np.array(gabor_features)
            
        except Exception as e:
            logger.error(f"Texture feature extraction failed: {e}")
        
        return features
    
    async def _extract_keypoint_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract keypoint-based features."""        features = {}
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # ORB features
            orb_kp, orb_desc = self.orb_detector.detectAndCompute(gray, None)
            features["orb_keypoints_count"] = len(orb_kp) if orb_kp else 0
            if orb_desc is not None:
                features["orb_descriptor_mean"] = np.mean(orb_desc, axis=0)
                features["orb_descriptor_std"] = np.std(orb_desc, axis=0)
            
            # SIFT features
            sift_kp, sift_desc = self.sift_detector.detectAndCompute(gray, None)
            features["sift_keypoints_count"] = len(sift_kp) if sift_kp else 0
            if sift_desc is not None:
                features["sift_descriptor_mean"] = np.mean(sift_desc, axis=0)
                features["sift_descriptor_std"] = np.std(sift_desc, axis=0)
            
            # SURF features (if available)
            if self.surf_detector:
                try:
                    surf_kp, surf_desc = self.surf_detector.detectAndCompute(gray, None)
                    features["surf_keypoints_count"] = len(surf_kp) if surf_kp else 0
                    if surf_desc is not None:
                        features["surf_descriptor_mean"] = np.mean(surf_desc, axis=0)
                        features["surf_descriptor_std"] = np.std(surf_desc, axis=0)
                except:
                    pass
            
            # Corner detection
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
            features["corner_count"] = len(corners) if corners is not None else 0
            
        except Exception as e:
            logger.error(f"Keypoint feature extraction failed: {e}")
        
        return features
    
    async def _extract_edge_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract edge-based features."""        features = {}
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Canny edge detection
            edges_canny = cv2.Canny(gray, 50, 150)
            features["canny_edge_density"] = np.sum(edges_canny > 0) / edges_canny.size
            
            # Sobel edge detection
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            features["sobel_edge_mean"] = np.mean(sobel_magnitude)
            features["sobel_edge_std"] = np.std(sobel_magnitude)
            
            # Laplacian edge detection
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            features["laplacian_edge_mean"] = np.mean(np.abs(laplacian))
            features["laplacian_edge_std"] = np.std(laplacian)
            
            # Edge orientation histogram
            edge_orientation = np.arctan2(sobel_y, sobel_x)
            orientation_hist, _ = np.histogram(edge_orientation.ravel(), bins=36, range=(-np.pi, np.pi))
            features["edge_orientation_hist"] = orientation_hist / np.sum(orientation_hist)
            
        except Exception as e:
            logger.error(f"Edge feature extraction failed: {e}")
        
        return features
    
    async def _extract_histogram_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract various histogram features."""        features = {}
        
        try:
            # Intensity histogram
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            intensity_hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            features["intensity_histogram"] = intensity_hist.flatten()
            
            # Gradient magnitude histogram
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            grad_hist, _ = np.histogram(grad_magnitude.ravel(), bins=64, range=(0, 255))
            features["gradient_histogram"] = grad_hist / np.sum(grad_hist)
            
        except Exception as e:
            logger.error(f"Histogram feature extraction failed: {e}")
        
        return features
    
    async def _extract_shape_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract shape-based features."""        features = {}
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Binary threshold for shape analysis
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Largest contour analysis
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Contour properties
                area = cv2.contourArea(largest_contour)
                perimeter = cv2.arcLength(largest_contour, True)
                
                features["largest_contour_area"] = area
                features["largest_contour_perimeter"] = perimeter
                features["contour_count"] = len(contours)
                
                # Shape compactness
                if perimeter > 0:
                    features["shape_compactness"] = 4 * np.pi * area / (perimeter ** 2)
                
                # Aspect ratio
                x, y, w, h = cv2.boundingRect(largest_contour)
                features["aspect_ratio"] = w / h if h > 0 else 0
                
                # Extent (ratio of contour area to bounding rectangle area)
                features["extent"] = area / (w * h) if w * h > 0 else 0
                
                # Solidity (ratio of contour area to convex hull area)
                hull = cv2.convexHull(largest_contour)
                hull_area = cv2.contourArea(hull)
                features["solidity"] = area / hull_area if hull_area > 0 else 0
            
        except Exception as e:
            logger.error(f"Shape feature extraction failed: {e}")
        
        return features


class ImageSimilarityCalculator:
    """Advanced image similarity calculation engine."""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feature_weights = config.get("feature_weights", {
            "hash": 0.3,
            "color": 0.25,
            "texture": 0.2,
            "keypoint": 0.15,
            "edge": 0.1
        })
        
    async def calculate_similarity(
        self, 
        features1: Dict[str, Any], 
        features2: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate comprehensive similarity between two image feature sets."""        try:
            similarities = {}
            weighted_sum = 0.0
            total_weight = 0.0
            
            # Hash similarity
            hash_sim = await self._calculate_hash_similarity(features1, features2)
            if hash_sim is not None:
                similarities["hash"] = hash_sim
                weighted_sum += hash_sim * self.feature_weights.get("hash", 0.3)
                total_weight += self.feature_weights.get("hash", 0.3)
            
            # Color similarity
            color_sim = await self._calculate_color_similarity(features1, features2)
            if color_sim is not None:
                similarities["color"] = color_sim
                weighted_sum += color_sim * self.feature_weights.get("color", 0.25)
                total_weight += self.feature_weights.get("color", 0.25)
            
            # Texture similarity
            texture_sim = await self._calculate_texture_similarity(features1, features2)
            if texture_sim is not None:
                similarities["texture"] = texture_sim
                weighted_sum += texture_sim * self.feature_weights.get("texture", 0.2)
                total_weight += self.feature_weights.get("texture", 0.2)
            
            # Keypoint similarity
            keypoint_sim = await self._calculate_keypoint_similarity(features1, features2)
            if keypoint_sim is not None:
                similarities["keypoint"] = keypoint_sim
                weighted_sum += keypoint_sim * self.feature_weights.get("keypoint", 0.15)
                total_weight += self.feature_weights.get("keypoint", 0.15)
            
            # Edge similarity
            edge_sim = await self._calculate_edge_similarity(features1, features2)
            if edge_sim is not None:
                similarities["edge"] = edge_sim
                weighted_sum += edge_sim * self.feature_weights.get("edge", 0.1)
                total_weight += self.feature_weights.get("edge", 0.1)
            
            # Calculate overall similarity
            overall_similarity = weighted_sum / total_weight if total_weight > 0 else 0.0
            
            logger.debug(f"Image similarity calculated: {overall_similarity:.4f}")
            return overall_similarity, similarities
            
        except Exception as e:
            logger.error(f"Image similarity calculation failed: {e}")
            return 0.0, {}
    
    async def _calculate_hash_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Optional[float]:
        """Calculate similarity using perceptual hashes."""        try:
            hash_similarities = []
            
            hash_types = ["phash", "ahash", "dhash", "whash", "colorhash"]
            
            for hash_type in hash_types:
                if hash_type in features1 and hash_type in features2:
                    hash1 = features1[hash_type]
                    hash2 = features2[hash_type]
                    
                    # Calculate Hamming distance
                    hamming_dist = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
                    similarity = 1 - (hamming_dist / len(hash1))
                    hash_similarities.append(similarity)
            
            return np.mean(hash_similarities) if hash_similarities else None
            
        except Exception as e:
            logger.error(f"Hash similarity calculation failed: {e}")
            return None
    
    async def _calculate_color_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Optional[float]:
        """Calculate color similarity using various color features."""        try:
            color_similarities = []
            
            # RGB histogram similarities
            for color in ['blue', 'green', 'red']:
                hist_key = f"rgb_{color}_hist"
                if hist_key in features1 and hist_key in features2:
                    # Normalize histograms
                    hist1 = features1[hist_key] / np.sum(features1[hist_key])
                    hist2 = features2[hist_key] / np.sum(features2[hist_key])
                    similarity = 1 - cosine(hist1, hist2)
                    color_similarities.append(max(0, similarity))
            
            # HSV similarities
            for component in ['hue', 'saturation', 'value']:
                hist_key = f"hsv_{component}_hist"
                if hist_key in features1 and hist_key in features2:
                    hist1 = features1[hist_key] / np.sum(features1[hist_key])
                    hist2 = features2[hist_key] / np.sum(features2[hist_key])
                    similarity = 1 - cosine(hist1, hist2)
                    color_similarities.append(max(0, similarity))
            
            # Dominant colors similarity
            if "dominant_colors" in features1 and "dominant_colors" in features2:
                dom_sim = 1 - cosine(features1["dominant_colors"], features2["dominant_colors"])
                color_similarities.append(max(0, dom_sim))
            
            return np.mean(color_similarities) if color_similarities else None
            
        except Exception as e:
            logger.error(f"Color similarity calculation failed: {e}")
            return None
    
    async def _calculate_texture_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Optional[float]:
        """Calculate texture similarity using LBP and GLCM features."""        try:
            texture_similarities = []
            
            # LBP similarity
            if "lbp_histogram" in features1 and "lbp_histogram" in features2:
                lbp_sim = 1 - cosine(features1["lbp_histogram"], features2["lbp_histogram"])
                texture_similarities.append(max(0, lbp_sim))
            
            # GLCM similarity
            if "glcm_features" in features1 and "glcm_features" in features2:
                glcm_sim = 1 - cosine(features1["glcm_features"], features2["glcm_features"])
                texture_similarities.append(max(0, glcm_sim))
            
            # Gabor filter similarity
            if "gabor_features" in features1 and "gabor_features" in features2:
                gabor_sim = 1 - cosine(features1["gabor_features"], features2["gabor_features"])
                texture_similarities.append(max(0, gabor_sim))
            
            return np.mean(texture_similarities) if texture_similarities else None
            
        except Exception as e:
            logger.error(f"Texture similarity calculation failed: {e}")
            return None
    
    async def _calculate_keypoint_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Optional[float]:
        """Calculate keypoint similarity using descriptor features."""        try:
            keypoint_similarities = []
            
            # ORB similarity
            if "orb_descriptor_mean" in features1 and "orb_descriptor_mean" in features2:
                orb_sim = 1 - cosine(features1["orb_descriptor_mean"], features2["orb_descriptor_mean"])
                keypoint_similarities.append(max(0, orb_sim))
            
            # SIFT similarity
            if "sift_descriptor_mean" in features1 and "sift_descriptor_mean" in features2:
                sift_sim = 1 - cosine(features1["sift_descriptor_mean"], features2["sift_descriptor_mean"])
                keypoint_similarities.append(max(0, sift_sim))
            
            # SURF similarity (if available)
            if "surf_descriptor_mean" in features1 and "surf_descriptor_mean" in features2:
                surf_sim = 1 - cosine(features1["surf_descriptor_mean"], features2["surf_descriptor_mean"])
                keypoint_similarities.append(max(0, surf_sim))
            
            return np.mean(keypoint_similarities) if keypoint_similarities else None
            
        except Exception as e:
            logger.error(f"Keypoint similarity calculation failed: {e}")
            return None
    
    async def _calculate_edge_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Optional[float]:
        """Calculate edge similarity using edge features."""        try:
            edge_similarities = []
            
            # Edge density similarity
            if "canny_edge_density" in features1 and "canny_edge_density" in features2:
                density_diff = abs(features1["canny_edge_density"] - features2["canny_edge_density"])
                density_sim = 1 - density_diff
                edge_similarities.append(max(0, density_sim))
            
            # Edge orientation similarity
            if "edge_orientation_hist" in features1 and "edge_orientation_hist" in features2:
                orient_sim = 1 - cosine(features1["edge_orientation_hist"], features2["edge_orientation_hist"])
                edge_similarities.append(max(0, orient_sim))
            
            return np.mean(edge_similarities) if edge_similarities else None
            
        except Exception as e:
            logger.error(f"Edge similarity calculation failed: {e}")
            return None


class ImageDetectionEngine:
    """    Advanced image detection engine for content surveillance.
    
    Implements sophisticated image fingerprinting, matching, and detection
    algorithms for protecting visual content across platforms.
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feature_extractor = ImageFeatureExtractor(config.get("feature_extraction", {}))
        self.similarity_calculator = ImageSimilarityCalculator(config.get("similarity", {}))
        
        # ChromaDB vector store for fast similarity search
        self.chroma_client = None
        self.fingerprint_collection = None
        
        # Detection thresholds
        self.similarity_threshold = config.get("similarity_threshold", 0.8)
        self.confidence_threshold = config.get("confidence_threshold", 0.75)
        
        # Performance metrics
        self.detection_stats = {
            "total_fingerprints": 0,
            "total_detections": 0,
            "false_positives": 0,
            "processing_time_avg": 0.0
        }
        
    async def initialize(self) -> bool:
        """Initialize the image detection engine."""        try:
            # Initialize ChromaDB client
            self.chroma_client = chromadb.Client()
            
            # Get or create fingerprint collection
            try:
                self.fingerprint_collection = self.chroma_client.get_collection(
                    name="image_fingerprints"
                )
            except:
                self.fingerprint_collection = self.chroma_client.create_collection(
                    name="image_fingerprints",
                    metadata={"description": "Image fingerprint collection for content protection"}
                )
            
            logger.info("ImageDetectionEngine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ImageDetectionEngine: {e}")
            return False
    
    async def create_fingerprint(
        self, 
        image_data: bytes, 
        metadata: Dict[str, Any]
    ) -> ImageFingerprint:
        """Create image fingerprint from image data."""        try:
            start_time = datetime.utcnow()
            
            # Extract image features
            features = await self.feature_extractor.extract_features(image_data)
            
            # Extract hash signatures
            hash_signatures = {
                hash_type: features.get(hash_type, "")
                for hash_type in ["phash", "ahash", "dhash", "whash", "colorhash"]
            }
            
            # Create overall hash signature
            feature_string = json.dumps({
                k: v.tolist() if isinstance(v, np.ndarray) else v 
                for k, v in features.items() 
                if not k.startswith("rgb_") and not k.startswith("hsv_") and isinstance(v, (int, float, str))
            }, sort_keys=True)
            overall_hash = hashlib.sha256(feature_string.encode()).hexdigest()
            
            # Create fingerprint object
            fingerprint = ImageFingerprint(
                fingerprint_id=hashlib.sha256(f"{metadata.get('user_id', '')}{overall_hash}{start_time.isoformat()}".encode()).hexdigest(),
                user_id=metadata.get("user_id", ""),
                title=metadata.get("title", ""),
                image_format=metadata.get("format", "unknown"),
                dimensions=features.get("dimensions", (0, 0)),
                file_size=features.get("file_size", 0),
                visual_features=features,
                hash_signatures=hash_signatures,
                created_at=start_time,
                metadata=metadata
            )
            
            # Store in vector database
            await self._store_fingerprint(fingerprint)
            
            self.detection_stats["total_fingerprints"] += 1
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Image fingerprint created in {processing_time:.2f}s: {fingerprint.fingerprint_id}")
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Image fingerprint creation failed: {e}")
            raise
    
    async def _store_fingerprint(self, fingerprint: ImageFingerprint) -> None:
        """Store fingerprint in vector database."""        try:
            # Create embedding vector from key features
            embedding_features = []
            
            # Color features
            if "rgb_blue_hist" in fingerprint.visual_features:
                embedding_features.extend(fingerprint.visual_features["rgb_blue_hist"][:32])  # Reduced size
                embedding_features.extend(fingerprint.visual_features["rgb_green_hist"][:32])
                embedding_features.extend(fingerprint.visual_features["rgb_red_hist"][:32])
            
            # Texture features
            if "lbp_histogram" in fingerprint.visual_features:
                embedding_features.extend(fingerprint.visual_features["lbp_histogram"])
            
            # Keypoint features
            if "orb_descriptor_mean" in fingerprint.visual_features:
                embedding_features.extend(fingerprint.visual_features["orb_descriptor_mean"][:32])  # Reduced size
            
            # Pad or truncate to fixed size (256 dimensions)
            target_size = 256
            if len(embedding_features) < target_size:
                embedding_features.extend([0.0] * (target_size - len(embedding_features)))
            else:
                embedding_features = embedding_features[:target_size]
            
            # Store in ChromaDB
            self.fingerprint_collection.add(
                embeddings=[embedding_features],
                documents=[json.dumps({
                    "title": fingerprint.title,
                    "format": fingerprint.image_format,
                    "dimensions": fingerprint.dimensions,
                    "file_size": fingerprint.file_size
                })],
                metadatas=[{
                    "fingerprint_id": fingerprint.fingerprint_id,
                    "user_id": fingerprint.user_id,
                    "created_at": fingerprint.created_at.isoformat(),
                    "phash": fingerprint.hash_signatures.get("phash", ""),
                    "ahash": fingerprint.hash_signatures.get("ahash", "")
                }],
                ids=[fingerprint.fingerprint_id]
            )
            
            logger.debug(f"Image fingerprint stored in vector database: {fingerprint.fingerprint_id}")
            
        except Exception as e:
            logger.error(f"Failed to store image fingerprint: {e}")
            raise
    
    async def detect_matches(
        self, 
        image_data: bytes, 
        detection_metadata: Dict[str, Any]
    ) -> List[ImageMatch]:
        """Detect image matches against stored fingerprints."""        try:
            start_time = datetime.utcnow()
            
            # Extract features from input image
            input_features = await self.feature_extractor.extract_features(image_data)
            
            # Create embedding for similarity search
            embedding_features = []
            
            # Color features
            if "rgb_blue_hist" in input_features:
                embedding_features.extend(input_features["rgb_blue_hist"][:32])
                embedding_features.extend(input_features["rgb_green_hist"][:32])
                embedding_features.extend(input_features["rgb_red_hist"][:32])
            
            # Texture features
            if "lbp_histogram" in input_features:
                embedding_features.extend(input_features["lbp_histogram"])
            
            # Keypoint features
            if "orb_descriptor_mean" in input_features:
                embedding_features.extend(input_features["orb_descriptor_mean"][:32])
            
            # Pad or truncate to fixed size
            target_size = 256
            if len(embedding_features) < target_size:
                embedding_features.extend([0.0] * (target_size - len(embedding_features)))
            else:
                embedding_features = embedding_features[:target_size]
            
            # Search for similar fingerprints
            search_results = self.fingerprint_collection.query(
                query_embeddings=[embedding_features],
                n_results=20,  # Get top 20 candidates
                include=["documents", "metadatas", "distances"]
            )
            
            matches = []
            
            # Process search results
            if search_results['ids'][0]:
                for i, fingerprint_id in enumerate(search_results['ids'][0]):
                    distance = search_results['distances'][0][i]
                    metadata = search_results['metadatas'][0][i]
                    
                    # Convert distance to similarity score
                    initial_similarity = max(0, 1 - distance)
                    
                    # Skip if initial similarity is too low
                    if initial_similarity < self.similarity_threshold * 0.8:
                        continue
                    
                    # Load full fingerprint for detailed comparison
                    stored_fingerprint = await self._load_fingerprint(fingerprint_id)
                    if not stored_fingerprint:
                        continue
                    
                    # Calculate detailed similarity
                    detailed_similarity, feature_similarities = await self.similarity_calculator.calculate_similarity(
                        input_features, stored_fingerprint.visual_features
                    )
                    
                    # Check if similarity meets threshold
                    if detailed_similarity >= self.similarity_threshold:
                        confidence = self._calculate_confidence(
                            detailed_similarity, 
                            feature_similarities,
                            input_features,
                            stored_fingerprint.visual_features
                        )
                        
                        if confidence >= self.confidence_threshold:
                            # Calculate hash matches
                            hash_matches = {}
                            for hash_type in ["phash", "ahash", "dhash", "whash", "colorhash"]:
                                if hash_type in input_features and hash_type in stored_fingerprint.hash_signatures:
                                    hash1 = input_features[hash_type]
                                    hash2 = stored_fingerprint.hash_signatures[hash_type]
                                    hamming_dist = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
                                    hash_matches[hash_type] = 1 - (hamming_dist / len(hash1))
                            
                            match = ImageMatch(
                                original_fingerprint_id=fingerprint_id,
                                detected_url=detection_metadata.get("url", ""),
                                similarity_score=detailed_similarity,
                                confidence_level=confidence,
                                match_regions=[(0, 0, input_features.get("dimensions", (0, 0))[0], input_features.get("dimensions", (0, 0))[1])],  # Full image for now
                                hash_matches=hash_matches,
                                feature_matches=feature_similarities,
                                platform=detection_metadata.get("platform", ""),
                                detected_at=datetime.utcnow(),
                                match_details=feature_similarities
                            )
                            matches.append(match)
            
            self.detection_stats["total_detections"] += len(matches)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Image detection completed in {processing_time:.2f}s: {len(matches)} matches found")
            
            return matches
            
        except Exception as e:
            logger.error(f"Image detection failed: {e}")
            return []
    
    async def _load_fingerprint(self, fingerprint_id: str) -> Optional[ImageFingerprint]:
        """Load full fingerprint data (placeholder - implement with your storage system)."""        # This would load the full fingerprint data from your database
        # For now, return None to indicate not found
        return None
    
    def _calculate_confidence(
        self, 
        similarity_score: float, 
        feature_similarities: Dict[str, float],
        input_features: Dict[str, Any],
        stored_features: Dict[str, Any]
    ) -> float:
        """Calculate confidence level for match."""        try:
            # Base confidence from overall similarity
            confidence = similarity_score
            
            # Boost confidence if multiple feature types match well
            high_similarity_features = sum(1 for sim in feature_similarities.values() if sim > 0.85)
            feature_boost = min(0.15, high_similarity_features * 0.05)
            confidence += feature_boost
            
            # Check dimension consistency
            if "dimensions" in input_features and "dimensions" in stored_features:
                input_dims = input_features["dimensions"]
                stored_dims = stored_features["dimensions"]
                # Allow for some variation in dimensions
                dim_ratio = min(input_dims[0] / stored_dims[0], stored_dims[0] / input_dims[0]) if stored_dims[0] > 0 else 0
                if dim_ratio > 0.8:  # Within 20% difference
                    confidence += 0.05
            
            # Ensure confidence is between 0 and 1
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return similarity_score
    
    async def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection engine statistics."""        return {
            "engine_type": "image",
            "status": "active",
            "statistics": self.detection_stats,
            "thresholds": {
                "similarity_threshold": self.similarity_threshold,
                "confidence_threshold": self.confidence_threshold
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources."""        try:
            if self.chroma_client:
                # ChromaDB cleanup if needed
                pass
            logger.info("ImageDetectionEngine cleanup completed")
        except Exception as e:
            logger.error(f"ImageDetectionEngine cleanup failed: {e}")
