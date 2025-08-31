"""🖼️ Image Content Fingerprinting Service
=======================================

Enterprise-grade image fingerprinting with advanced computer vision:
- Perceptual hashing (pHash, dHash, aHash, wHash)
- CLIP neural embeddings
- Traditional feature extraction (SIFT, ORB, SURF)
- Color histogram analysis
- Texture and edge detection

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""
import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json

try:
    import cv2
    import imagehash
    from PIL import Image, ImageStat, ImageFilter
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    from transformers import CLIPProcessor, CLIPModel, CLIPVisionModel
    from sklearn.cluster import KMeans
    from scipy.spatial.distance import cosine, euclidean
    from skimage import feature, measure, filters
    import matplotlib.pyplot as plt
    from colorthief import ColorThief
except ImportError as e:
    logging.warning(f"Some image dependencies not available: {e}")

from ..models import FingerprintResult, SimilarityMatch

logger = logging.getLogger(__name__)

@dataclass
class ImageMetadata:
    """Comprehensive image metadata extraction."""    width: int
    height: int
    channels: int
    format: str
    mode: str
    file_size: int
    has_transparency: bool
    dominant_colors: Optional[List[Tuple[int, int, int]]]
    brightness: Optional[float]
    contrast: Optional[float]
    sharpness: Optional[float]
    color_variance: Optional[float]
    edge_density: Optional[float]
    texture_energy: Optional[float]

class PerceptualImageHashing:
    """Advanced perceptual hashing for images using multiple algorithms."""    
    def __init__(self, hash_size: int = 16):
        self.hash_size = hash_size
        
    def extract_hashes(self, image_path: str) -> Dict[str, Any]:
        """        Extract multiple perceptual hashes from image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary containing various hash types
        """        try:
            # Load image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Extract multiple hash types
                phash = str(imagehash.phash(img, hash_size=self.hash_size))
                dhash = str(imagehash.dhash(img, hash_size=self.hash_size))
                ahash = str(imagehash.average_hash(img, hash_size=self.hash_size))
                whash = str(imagehash.whash(img, hash_size=self.hash_size))
                
                # Color hash for color similarity
                colorhash = str(imagehash.colorhash(img, binbits=3))
                
                # Generate rotational variants
                rotational_hashes = self._extract_rotational_hashes(img)
                
                # Generate scale variants
                scale_hashes = self._extract_scale_hashes(img)
                
                # Combined fingerprint
                combined_hash = self._combine_hashes(phash, dhash, ahash, whash, colorhash)
                
                return {
                    "phash": phash,
                    "dhash": dhash,
                    "ahash": ahash,
                    "whash": whash,
                    "colorhash": colorhash,
                    "combined_hash": combined_hash,
                    "rotational_hashes": rotational_hashes,
                    "scale_hashes": scale_hashes,
                    "hash_size": self.hash_size,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Perceptual hash extraction failed for {image_path}: {e}")
            return {"error": str(e)}
    
    def _extract_rotational_hashes(self, img: Image.Image) -> Dict[str, str]:
        """Extract hashes for rotated versions of the image."""        rotational_hashes = {}
        
        for angle in [90, 180, 270]:
            rotated_img = img.rotate(angle, expand=True)
            rotational_hashes[f"rotation_{angle}"] = str(imagehash.phash(rotated_img, hash_size=self.hash_size))
        
        return rotational_hashes
    
    def _extract_scale_hashes(self, img: Image.Image) -> Dict[str, str]:
        """Extract hashes for scaled versions of the image."""        scale_hashes = {}
        original_size = img.size
        
        for scale in [0.5, 0.75, 1.25, 1.5]:
            new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
            scaled_img = img.resize(new_size, Image.Resampling.LANCZOS)
            scale_hashes[f"scale_{scale}"] = str(imagehash.phash(scaled_img, hash_size=self.hash_size))
        
        return scale_hashes
    
    def _combine_hashes(self, phash: str, dhash: str, ahash: str, whash: str, colorhash: str) -> str:
        """Combine multiple hash types into a single fingerprint."""        combined = f"{phash}|{dhash}|{ahash}|{whash}|{colorhash}"
        return hashlib.md5(combined.encode()).hexdigest()

class CLIPEmbeddingExtractor:
    """CLIP-based neural embeddings for semantic image understanding."""    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.model_name = model_name
        self.model = None
        self.processor = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize CLIP model."""        try:
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            self.model = CLIPModel.from_pretrained(self.model_name)
            self.model.eval()
        except Exception as e:
            logger.warning(f"CLIP model initialization failed: {e}")
    
    def extract_embeddings(self, image_path: str) -> Dict[str, Any]:
        """        Extract CLIP embeddings from image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary containing embeddings and metadata
        """        if not self.model or not self.processor:
            return {"error": "CLIP model not initialized"}
            
        try:
            # Load and preprocess image
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Process image
                inputs = self.processor(images=img, return_tensors="pt", padding=True)
                
                with torch.no_grad():
                    image_features = self.model.get_image_features(**inputs)
                    
                # Normalize embeddings
                image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
                
                # Convert to numpy
                embeddings = image_features.squeeze().numpy()
                
                # Generate embedding hash
                embedding_hash = self._compute_embedding_hash(embeddings)
                
                # Extract semantic features
                semantic_features = self._extract_semantic_features(embeddings)
                
                return {
                    "embeddings": embeddings.tolist(),
                    "embedding_hash": embedding_hash,
                    "embedding_size": len(embeddings),
                    "semantic_features": semantic_features,
                    "model_name": self.model_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"CLIP embedding extraction failed for {image_path}: {e}")
            return {"error": str(e)}
    
    def _compute_embedding_hash(self, embeddings: np.ndarray) -> str:
        """Compute hash from CLIP embeddings."""        # Quantize embeddings to binary
        binary_embeddings = (embeddings > np.median(embeddings)).astype(int)
        
        # Convert to hash
        hash_string = ''.join([str(bit) for bit in binary_embeddings])
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _extract_semantic_features(self, embeddings: np.ndarray) -> Dict[str, float]:
        """Extract semantic features from embeddings."""        return {
            "embedding_mean": float(np.mean(embeddings)),
            "embedding_std": float(np.std(embeddings)),
            "embedding_max": float(np.max(embeddings)),
            "embedding_min": float(np.min(embeddings)),
            "embedding_energy": float(np.sum(embeddings ** 2)),
            "embedding_sparsity": float(np.sum(np.abs(embeddings) < 0.01) / len(embeddings))
        }

class TraditionalFeatureExtractor:
    """Traditional computer vision feature extraction (SIFT, ORB, SURF)."""    
    def __init__(self):
        self.sift = cv2.SIFT_create()
        self.orb = cv2.ORB_create()
        try:
            self.surf = cv2.xfeatures2d.SURF_create()
        except AttributeError:
            self.surf = None
            logger.warning("SURF not available in this OpenCV build")
    
    def extract_features(self, image_path: str) -> Dict[str, Any]:
        """        Extract traditional computer vision features.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary containing extracted features
        """        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Cannot load image: {image_path}")
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Extract SIFT features
            sift_features = self._extract_sift_features(gray)
            
            # Extract ORB features
            orb_features = self._extract_orb_features(gray)
            
            # Extract SURF features if available
            surf_features = self._extract_surf_features(gray) if self.surf else {}
            
            # Extract corner features
            corner_features = self._extract_corner_features(gray)
            
            # Extract edge features
            edge_features = self._extract_edge_features(gray)
            
            # Generate traditional fingerprint
            traditional_fingerprint = self._generate_traditional_fingerprint(
                sift_features, orb_features, corner_features, edge_features
            )
            
            return {
                "sift": sift_features,
                "orb": orb_features,
                "surf": surf_features,
                "corners": corner_features,
                "edges": edge_features,
                "traditional_fingerprint": traditional_fingerprint,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Traditional feature extraction failed for {image_path}: {e}")
            return {"error": str(e)}
    
    def _extract_sift_features(self, gray: np.ndarray) -> Dict[str, Any]:
        """Extract SIFT features."""        try:
            keypoints, descriptors = self.sift.detectAndCompute(gray, None)
            
            if descriptors is not None:
                # Compute feature statistics
                feature_stats = {
                    "num_keypoints": len(keypoints),
                    "descriptor_mean": float(np.mean(descriptors)),
                    "descriptor_std": float(np.std(descriptors)),
                    "descriptor_shape": descriptors.shape
                }
                
                # Create compact representation
                if len(descriptors) > 0:
                    # Use k-means to create vocabulary
                    n_clusters = min(50, len(descriptors))
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                    clusters = kmeans.fit_predict(descriptors)
                    
                    # Create histogram of visual words
                    histogram = np.bincount(clusters, minlength=n_clusters)
                    feature_hash = hashlib.md5(histogram.tobytes()).hexdigest()
                else:
                    feature_hash = ""
                
                return {
                    **feature_stats,
                    "feature_hash": feature_hash,
                    "keypoint_locations": [(kp.pt[0], kp.pt[1]) for kp in keypoints[:20]]  # Limit size
                }
            else:
                return {"num_keypoints": 0, "feature_hash": ""}
                
        except Exception as e:
            logger.error(f"SIFT extraction failed: {e}")
            return {"error": str(e)}
    
    def _extract_orb_features(self, gray: np.ndarray) -> Dict[str, Any]:
        """Extract ORB features."""        try:
            keypoints, descriptors = self.orb.detectAndCompute(gray, None)
            
            if descriptors is not None:
                feature_stats = {
                    "num_keypoints": len(keypoints),
                    "descriptor_shape": descriptors.shape
                }
                
                # Create binary hash from ORB descriptors
                if len(descriptors) > 0:
                    # ORB descriptors are already binary
                    combined_descriptors = np.bitwise_xor.reduce(descriptors)
                    feature_hash = hashlib.md5(combined_descriptors.tobytes()).hexdigest()
                else:
                    feature_hash = ""
                
                return {
                    **feature_stats,
                    "feature_hash": feature_hash,
                    "keypoint_locations": [(kp.pt[0], kp.pt[1]) for kp in keypoints[:20]]
                }
            else:
                return {"num_keypoints": 0, "feature_hash": ""}
                
        except Exception as e:
            logger.error(f"ORB extraction failed: {e}")
            return {"error": str(e)}
    
    def _extract_surf_features(self, gray: np.ndarray) -> Dict[str, Any]:
        """Extract SURF features."""        if not self.surf:
            return {"error": "SURF not available"}
            
        try:
            keypoints, descriptors = self.surf.detectAndCompute(gray, None)
            
            if descriptors is not None:
                feature_stats = {
                    "num_keypoints": len(keypoints),
                    "descriptor_mean": float(np.mean(descriptors)),
                    "descriptor_std": float(np.std(descriptors)),
                    "descriptor_shape": descriptors.shape
                }
                
                # Create compact representation
                if len(descriptors) > 0:
                    feature_hash = hashlib.md5(descriptors.tobytes()).hexdigest()
                else:
                    feature_hash = ""
                
                return {
                    **feature_stats,
                    "feature_hash": feature_hash
                }
            else:
                return {"num_keypoints": 0, "feature_hash": ""}
                
        except Exception as e:
            logger.error(f"SURF extraction failed: {e}")
            return {"error": str(e)}
    
    def _extract_corner_features(self, gray: np.ndarray) -> Dict[str, Any]:
        """Extract corner features using Harris corner detection."""        try:
            # Harris corner detection
            corners = cv2.cornerHarris(gray, 2, 3, 0.04)
            
            # Find corner coordinates
            corner_coords = np.where(corners > 0.01 * corners.max())
            num_corners = len(corner_coords[0])
            
            # Corner statistics
            if num_corners > 0:
                corner_response_mean = float(np.mean(corners[corner_coords]))
                corner_response_std = float(np.std(corners[corner_coords]))
                
                # Create spatial histogram of corners
                h, w = gray.shape
                hist_h = np.histogram(corner_coords[0], bins=10, range=(0, h))[0]
                hist_w = np.histogram(corner_coords[1], bins=10, range=(0, w))[0]
                spatial_hash = hashlib.md5((hist_h.tobytes() + hist_w.tobytes())).hexdigest()
            else:
                corner_response_mean = 0.0
                corner_response_std = 0.0
                spatial_hash = ""
            
            return {
                "num_corners": num_corners,
                "corner_response_mean": corner_response_mean,
                "corner_response_std": corner_response_std,
                "spatial_hash": spatial_hash
            }
            
        except Exception as e:
            logger.error(f"Corner extraction failed: {e}")
            return {"error": str(e)}
    
    def _extract_edge_features(self, gray: np.ndarray) -> Dict[str, Any]:
        """Extract edge features using Canny edge detection."""        try:
            # Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Edge statistics
            num_edge_pixels = np.sum(edges > 0)
            edge_density = num_edge_pixels / (gray.shape[0] * gray.shape[1])
            
            # Edge orientation histogram
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            edge_magnitude = np.sqrt(sobelx**2 + sobely**2)
            edge_orientation = np.arctan2(sobely, sobelx)
            
            # Create orientation histogram
            hist, _ = np.histogram(edge_orientation[edge_magnitude > np.mean(edge_magnitude)], 
                                 bins=16, range=(-np.pi, np.pi))
            orientation_hash = hashlib.md5(hist.tobytes()).hexdigest()
            
            return {
                "num_edge_pixels": int(num_edge_pixels),
                "edge_density": float(edge_density),
                "edge_magnitude_mean": float(np.mean(edge_magnitude)),
                "edge_magnitude_std": float(np.std(edge_magnitude)),
                "orientation_hash": orientation_hash
            }
            
        except Exception as e:
            logger.error(f"Edge extraction failed: {e}")
            return {"error": str(e)}
    
    def _generate_traditional_fingerprint(self, sift_features: Dict, orb_features: Dict, 
                                        corner_features: Dict, edge_features: Dict) -> str:
        """Generate combined fingerprint from traditional features."""        hash_components = []
        
        # Collect hash components
        if "feature_hash" in sift_features and sift_features["feature_hash"]:
            hash_components.append(sift_features["feature_hash"])
        
        if "feature_hash" in orb_features and orb_features["feature_hash"]:
            hash_components.append(orb_features["feature_hash"])
        
        if "spatial_hash" in corner_features and corner_features["spatial_hash"]:
            hash_components.append(corner_features["spatial_hash"])
        
        if "orientation_hash" in edge_features and edge_features["orientation_hash"]:
            hash_components.append(edge_features["orientation_hash"])
        
        # Combine hashes
        if hash_components:
            combined_string = "|".join(hash_components)
            return hashlib.md5(combined_string.encode()).hexdigest()
        
        return ""

class ColorAnalyzer:
    """Advanced color analysis and histogram extraction."""    
    def __init__(self):
        self.n_dominant_colors = 8
        
    def analyze_colors(self, image_path: str) -> Dict[str, Any]:
        """        Perform comprehensive color analysis.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary containing color analysis results
        """        try:
            # Load image
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Extract dominant colors
                dominant_colors = self._extract_dominant_colors(image_path)
                
                # Color histogram
                color_histogram = self._compute_color_histogram(img)
                
                # Color statistics
                color_stats = self._compute_color_statistics(img)
                
                # Color harmony analysis
                harmony_analysis = self._analyze_color_harmony(dominant_colors)
                
                # Generate color fingerprint
                color_fingerprint = self._generate_color_fingerprint(
                    color_histogram, dominant_colors, color_stats
                )
                
                return {
                    "dominant_colors": dominant_colors,
                    "color_histogram": color_histogram,
                    "color_statistics": color_stats,
                    "color_harmony": harmony_analysis,
                    "color_fingerprint": color_fingerprint,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Color analysis failed for {image_path}: {e}")
            return {"error": str(e)}
    
    def _extract_dominant_colors(self, image_path: str) -> List[Dict[str, Any]]:
        """Extract dominant colors using ColorThief."""        try:
            color_thief = ColorThief(image_path)
            
            # Get dominant color
            dominant_color = color_thief.get_color(quality=1)
            
            # Get color palette
            palette = color_thief.get_palette(color_count=self.n_dominant_colors, quality=1)
            
            # Convert to list of dictionaries with additional info
            dominant_colors = []
            for i, color in enumerate(palette):
                color_info = {
                    "rank": i + 1,
                    "rgb": color,
                    "hex": f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}",
                    "hsv": self._rgb_to_hsv(color),
                    "lab": self._rgb_to_lab(color)
                }
                dominant_colors.append(color_info)
            
            return dominant_colors
            
        except Exception as e:
            logger.error(f"Dominant color extraction failed: {e}")
            return []
    
    def _compute_color_histogram(self, img: Image.Image) -> Dict[str, List[float]]:
        """Compute color histograms in different color spaces."""        try:
            # Convert to numpy array
            img_array = np.array(img)
            
            # RGB histogram
            rgb_hist = []
            for i in range(3):
                hist, _ = np.histogram(img_array[:, :, i], bins=32, range=(0, 256))
                rgb_hist.extend(hist.tolist())
            
            # HSV histogram
            img_hsv = img.convert('HSV')
            hsv_array = np.array(img_hsv)
            hsv_hist = []
            for i in range(3):
                hist, _ = np.histogram(hsv_array[:, :, i], bins=32, range=(0, 256))
                hsv_hist.extend(hist.tolist())
            
            return {
                "rgb_histogram": rgb_hist,
                "hsv_histogram": hsv_hist
            }
            
        except Exception as e:
            logger.error(f"Color histogram computation failed: {e}")
            return {"rgb_histogram": [], "hsv_histogram": []}
    
    def _compute_color_statistics(self, img: Image.Image) -> Dict[str, float]:
        """Compute color statistics."""        try:
            stat = ImageStat.Stat(img)
            
            return {
                "mean_r": stat.mean[0],
                "mean_g": stat.mean[1],
                "mean_b": stat.mean[2],
                "stddev_r": stat.stddev[0],
                "stddev_g": stat.stddev[1],
                "stddev_b": stat.stddev[2],
                "variance_r": stat.var[0],
                "variance_g": stat.var[1],
                "variance_b": stat.var[2],
                "overall_brightness": sum(stat.mean) / 3,
                "overall_contrast": sum(stat.stddev) / 3
            }
            
        except Exception as e:
            logger.error(f"Color statistics computation failed: {e}")
            return {}
    
    def _analyze_color_harmony(self, dominant_colors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze color harmony and relationships."""        if len(dominant_colors) < 2:
            return {"harmony_score": 0.0, "color_scheme": "monochromatic"}
        
        try:
            # Extract hue values
            hues = [color["hsv"][0] for color in dominant_colors[:5]]
            
            # Analyze hue relationships
            harmony_score = self._calculate_harmony_score(hues)
            color_scheme = self._determine_color_scheme(hues)
            
            return {
                "harmony_score": harmony_score,
                "color_scheme": color_scheme,
                "hue_variance": float(np.var(hues)) if len(hues) > 1 else 0.0,
                "hue_range": max(hues) - min(hues) if len(hues) > 1 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Color harmony analysis failed: {e}")
            return {"harmony_score": 0.0, "color_scheme": "unknown"}
    
    def _calculate_harmony_score(self, hues: List[float]) -> float:
        """Calculate color harmony score based on hue relationships."""        if len(hues) < 2:
            return 1.0
        
        # Calculate pairwise hue differences
        differences = []
        for i in range(len(hues)):
            for j in range(i + 1, len(hues)):
                diff = abs(hues[i] - hues[j])
                # Handle circular nature of hue
                diff = min(diff, 360 - diff)
                differences.append(diff)
        
        # Harmony is higher when differences are close to ideal intervals
        ideal_intervals = [30, 60, 90, 120, 150, 180]  # Common harmonic intervals
        harmony_scores = []
        
        for diff in differences:
            closest_ideal = min(ideal_intervals, key=lambda x: abs(x - diff))
            score = 1.0 - abs(diff - closest_ideal) / 180.0
            harmony_scores.append(score)
        
        return sum(harmony_scores) / len(harmony_scores) if harmony_scores else 0.0
    
    def _determine_color_scheme(self, hues: List[float]) -> str:
        """Determine the color scheme type."""        if len(hues) < 2:
            return "monochromatic"
        
        # Calculate hue range
        hue_range = max(hues) - min(hues)
        
        if hue_range < 30:
            return "monochromatic"
        elif hue_range < 90:
            return "analogous"
        elif hue_range < 150:
            return "triadic"
        else:
            return "complementary"
    
    def _rgb_to_hsv(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert RGB to HSV."""        r, g, b = [x / 255.0 for x in rgb]
        
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Hue
        if diff == 0:
            h = 0
        elif max_val == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:
            h = (60 * ((r - g) / diff) + 240) % 360
        
        # Saturation
        s = 0 if max_val == 0 else diff / max_val
        
        # Value
        v = max_val
        
        return (h, s * 100, v * 100)
    
    def _rgb_to_lab(self, rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert RGB to LAB (simplified approximation)."""        r, g, b = [x / 255.0 for x in rgb]
        
        # Simplified sRGB to XYZ conversion
        x = 0.412453 * r + 0.357580 * g + 0.180423 * b
        y = 0.212671 * r + 0.715160 * g + 0.072169 * b
        z = 0.019334 * r + 0.119193 * g + 0.950227 * b
        
        # XYZ to LAB (simplified)
        l = 116 * (y ** (1/3)) - 16 if y > 0.008856 else 903.3 * y
        a = 500 * ((x ** (1/3)) - (y ** (1/3))) if x > 0.008856 and y > 0.008856 else 0
        b_lab = 200 * ((y ** (1/3)) - (z ** (1/3))) if y > 0.008856 and z > 0.008856 else 0
        
        return (l, a, b_lab)
    
    def _generate_color_fingerprint(self, color_histogram: Dict, dominant_colors: List, 
                                  color_stats: Dict) -> str:
        """Generate fingerprint from color analysis."""        fingerprint_components = []
        
        # Add histogram hash
        if "rgb_histogram" in color_histogram:
            hist_hash = hashlib.md5(str(color_histogram["rgb_histogram"]).encode()).hexdigest()
            fingerprint_components.append(hist_hash)
        
        # Add dominant colors hash
        if dominant_colors:
            colors_string = "|".join([color["hex"] for color in dominant_colors[:5]])
            colors_hash = hashlib.md5(colors_string.encode()).hexdigest()
            fingerprint_components.append(colors_hash)
        
        # Add statistics hash
        if color_stats:
            stats_string = "|".join([f"{k}:{v:.2f}" for k, v in color_stats.items() if isinstance(v, (int, float))])
            stats_hash = hashlib.md5(stats_string.encode()).hexdigest()
            fingerprint_components.append(stats_hash)
        
        # Combine all components
        if fingerprint_components:
            combined_string = "|".join(fingerprint_components)
            return hashlib.md5(combined_string.encode()).hexdigest()
        
        return ""

class TextureAnalyzer:
    """Texture and pattern analysis for images."""    
    def __init__(self):
        self.lbp_radius = 3
        self.lbp_n_points = 8 * self.lbp_radius
        
    def analyze_texture(self, image_path: str) -> Dict[str, Any]:
        """        Perform comprehensive texture analysis.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary containing texture analysis results
        """        try:
            # Load image
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise ValueError(f"Cannot load image: {image_path}")
            
            # Local Binary Pattern analysis
            lbp_features = self._analyze_lbp(img)
            
            # Gabor filter analysis
            gabor_features = self._analyze_gabor_filters(img)
            
            # Gray-Level Co-occurrence Matrix
            glcm_features = self._analyze_glcm(img)
            
            # Fractal dimension
            fractal_features = self._analyze_fractal_dimension(img)
            
            # Generate texture fingerprint
            texture_fingerprint = self._generate_texture_fingerprint(
                lbp_features, gabor_features, glcm_features, fractal_features
            )
            
            return {
                "lbp": lbp_features,
                "gabor": gabor_features,
                "glcm": glcm_features,
                "fractal": fractal_features,
                "texture_fingerprint": texture_fingerprint,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Texture analysis failed for {image_path}: {e}")
            return {"error": str(e)}
    
    def _analyze_lbp(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze Local Binary Patterns."""        try:
            # Compute LBP
            lbp = feature.local_binary_pattern(img, self.lbp_n_points, self.lbp_radius, method='uniform')
            
            # Compute LBP histogram
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=self.lbp_n_points + 2, 
                                     range=(0, self.lbp_n_points + 2))
            
            # Normalize histogram
            lbp_hist = lbp_hist.astype(float)
            lbp_hist /= (lbp_hist.sum() + 1e-8)
            
            # LBP statistics
            lbp_stats = {
                "uniformity": float(np.sum(lbp_hist ** 2)),
                "entropy": float(-np.sum(lbp_hist * np.log2(lbp_hist + 1e-8))),
                "contrast": float(np.var(lbp))
            }
            
            # Generate LBP hash
            lbp_hash = hashlib.md5(lbp_hist.tobytes()).hexdigest()
            
            return {
                "histogram": lbp_hist.tolist(),
                "statistics": lbp_stats,
                "lbp_hash": lbp_hash
            }
            
        except Exception as e:
            logger.error(f"LBP analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_gabor_filters(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze image using Gabor filters."""        try:
            # Define Gabor filter parameters
            frequencies = [0.1, 0.3, 0.5]
            angles = [0, 45, 90, 135]
            
            gabor_responses = []
            
            for freq in frequencies:
                for angle in angles:
                    # Apply Gabor filter
                    real_response = filters.gabor(img, frequency=freq, theta=np.radians(angle))[0]
                    
                    # Compute response statistics
                    gabor_responses.append({
                        "frequency": freq,
                        "angle": angle,
                        "mean": float(np.mean(real_response)),
                        "std": float(np.std(real_response)),
                        "energy": float(np.sum(real_response ** 2))
                    })
            
            # Overall Gabor statistics
            all_energies = [resp["energy"] for resp in gabor_responses]
            gabor_stats = {
                "total_energy": sum(all_energies),
                "energy_variance": float(np.var(all_energies)),
                "dominant_frequency": frequencies[np.argmax([sum(resp["energy"] for resp in gabor_responses 
                                                               if resp["frequency"] == freq) for freq in frequencies])],
                "dominant_angle": angles[np.argmax([sum(resp["energy"] for resp in gabor_responses 
                                                       if resp["angle"] == angle) for angle in angles])]
            }
            
            # Generate Gabor hash
            energy_string = "|".join([f"{resp['energy']:.6f}" for resp in gabor_responses])
            gabor_hash = hashlib.md5(energy_string.encode()).hexdigest()
            
            return {
                "responses": gabor_responses,
                "statistics": gabor_stats,
                "gabor_hash": gabor_hash
            }
            
        except Exception as e:
            logger.error(f"Gabor analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_glcm(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze Gray-Level Co-occurrence Matrix."""        try:
            # Resize image if too large (for performance)
            if img.shape[0] > 256 or img.shape[1] > 256:
                img = cv2.resize(img, (256, 256))
            
            # Compute GLCM properties
            distances = [1, 2, 3]
            angles = [0, 45, 90, 135]
            
            glcm_features = {}
            
            for distance in distances:
                for angle in angles:
                    # Compute GLCM
                    glcm = feature.graycomatrix(img, distances=[distance], 
                                              angles=[np.radians(angle)], 
                                              levels=256, symmetric=True, normed=True)
                    
                    # Compute GLCM properties
                    contrast = feature.graycoprops(glcm, 'contrast')[0, 0]
                    dissimilarity = feature.graycoprops(glcm, 'dissimilarity')[0, 0]
                    homogeneity = feature.graycoprops(glcm, 'homogeneity')[0, 0]
                    energy = feature.graycoprops(glcm, 'energy')[0, 0]
                    correlation = feature.graycoprops(glcm, 'correlation')[0, 0]
                    
                    glcm_features[f"d{distance}_a{angle}"] = {
                        "contrast": float(contrast),
                        "dissimilarity": float(dissimilarity),
                        "homogeneity": float(homogeneity),
                        "energy": float(energy),
                        "correlation": float(correlation)
                    }
            
            # Compute average features
            avg_features = {}
            for prop in ["contrast", "dissimilarity", "homogeneity", "energy", "correlation"]:
                values = [features[prop] for features in glcm_features.values()]
                avg_features[f"avg_{prop}"] = float(np.mean(values))
                avg_features[f"std_{prop}"] = float(np.std(values))
            
            # Generate GLCM hash
            features_string = "|".join([f"{k}:{v:.6f}" for k, v in avg_features.items()])
            glcm_hash = hashlib.md5(features_string.encode()).hexdigest()
            
            return {
                "features": glcm_features,
                "average_features": avg_features,
                "glcm_hash": glcm_hash
            }
            
        except Exception as e:
            logger.error(f"GLCM analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_fractal_dimension(self, img: np.ndarray) -> Dict[str, Any]:
        """Analyze fractal dimension of the image."""        try:
            # Simple box-counting method for fractal dimension
            def box_count(img, k):
                s = np.add.reduceat(
                    np.add.reduceat(img, np.arange(0, img.shape[0], k), axis=0),
                    np.arange(0, img.shape[1], k), axis=1)
                return len(np.where((s > 0) & (s < 255 * k * k))[0])
            
            # Apply box counting for different scales
            scales = np.logspace(0.1, 1, 10, dtype=int)
            scales = scales[scales < min(img.shape)]
            
            if len(scales) < 2:
                return {"fractal_dimension": 0.0, "error": "Image too small for fractal analysis"}
            
            counts = []
            for scale in scales:
                counts.append(box_count(img, scale))
            
            # Fit line to log-log plot
            coeffs = np.polyfit(np.log(scales), np.log(counts), 1)
            fractal_dimension = -coeffs[0]
            
            return {
                "fractal_dimension": float(fractal_dimension),
                "scales": scales.tolist(),
                "counts": counts,
                "r_squared": float(np.corrcoef(np.log(scales), np.log(counts))[0, 1] ** 2)
            }
            
        except Exception as e:
            logger.error(f"Fractal analysis failed: {e}")
            return {"error": str(e)}
    
    def _generate_texture_fingerprint(self, lbp_features: Dict, gabor_features: Dict,
                                    glcm_features: Dict, fractal_features: Dict) -> str:
        """Generate combined texture fingerprint."""        fingerprint_components = []
        
        # Add feature hashes
        if "lbp_hash" in lbp_features:
            fingerprint_components.append(lbp_features["lbp_hash"])
        
        if "gabor_hash" in gabor_features:
            fingerprint_components.append(gabor_features["gabor_hash"])
        
        if "glcm_hash" in glcm_features:
            fingerprint_components.append(glcm_features["glcm_hash"])
        
        if "fractal_dimension" in fractal_features:
            fd_hash = hashlib.md5(str(fractal_features["fractal_dimension"]).encode()).hexdigest()
            fingerprint_components.append(fd_hash)
        
        # Combine all components
        if fingerprint_components:
            combined_string = "|".join(fingerprint_components)
            return hashlib.md5(combined_string.encode()).hexdigest()
        
        return ""

class ImageFingerprintingService:
    """    Comprehensive image fingerprinting service combining multiple techniques.
    
    Features:
    - Perceptual hashing (multiple algorithms)
    - CLIP neural embeddings
    - Traditional computer vision features
    - Color analysis and harmony
    - Texture and pattern analysis
    - Multi-scale and rotation invariance
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.perceptual_hasher = PerceptualImageHashing()
        self.clip_extractor = CLIPEmbeddingExtractor()
        self.traditional_extractor = TraditionalFeatureExtractor()
        self.color_analyzer = ColorAnalyzer()
        self.texture_analyzer = TextureAnalyzer()
        
        # Similarity thresholds
        self.similarity_thresholds = {
            "perceptual": 0.85,
            "clip": 0.90,
            "traditional": 0.75,
            "color": 0.80,
            "texture": 0.70,
            "combined": 0.82
        }
        
    async def process_image(self, image_path: str, user_id: int) -> FingerprintResult:
        """        Process image file and generate comprehensive fingerprint.
        
        Args:
            image_path: Path to image file
            user_id: User ID for attribution
            
        Returns:
            FingerprintResult containing all fingerprint data
        """        try:
            logger.info(f"Processing image fingerprint for: {image_path}")
            
            # Extract metadata
            metadata = await self._extract_metadata(image_path)
            
            # Run all fingerprinting algorithms in parallel
            tasks = [
                asyncio.create_task(self._run_perceptual_hashing(image_path)),
                asyncio.create_task(self._run_clip_extraction(image_path)),
                asyncio.create_task(self._run_traditional_features(image_path)),
                asyncio.create_task(self._run_color_analysis(image_path)),
                asyncio.create_task(self._run_texture_analysis(image_path))
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            perceptual_result = results[0] if not isinstance(results[0], Exception) else {}
            clip_result = results[1] if not isinstance(results[1], Exception) else {}
            traditional_result = results[2] if not isinstance(results[2], Exception) else {}
            color_result = results[3] if not isinstance(results[3], Exception) else {}
            texture_result = results[4] if not isinstance(results[4], Exception) else {}
            
            # Combine results
            fingerprint_data = {
                "perceptual": perceptual_result,
                "clip": clip_result,
                "traditional": traditional_result,
                "color": color_result,
                "texture": texture_result,
                "metadata": metadata,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
            # Generate combined hash
            combined_hash = self._generate_combined_hash(fingerprint_data)
            
            return FingerprintResult(
                user_id=user_id,
                content_type="image",
                file_path=image_path,
                fingerprint_data=fingerprint_data,
                hash_value=combined_hash,
                processing_time=datetime.utcnow(),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Image fingerprinting failed for {image_path}: {e}")
            raise
    
    async def _extract_metadata(self, image_path: str) -> ImageMetadata:
        """Extract comprehensive image metadata."""        try:
            with Image.open(image_path) as img:
                width, height = img.size
                channels = len(img.getbands())
                format_name = img.format or "unknown"
                mode = img.mode
                
                # Check for transparency
                has_transparency = img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                
                # File size
                file_size = Path(image_path).stat().st_size
                
                # Basic image statistics
                stat = ImageStat.Stat(img.convert('RGB'))
                brightness = sum(stat.mean) / 3
                contrast = sum(stat.stddev) / 3
                
                # Calculate sharpness using Laplacian variance
                gray_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if gray_img is not None:
                    laplacian_var = cv2.Laplacian(gray_img, cv2.CV_64F).var()
                    sharpness = float(laplacian_var)
                    
                    # Edge density
                    edges = cv2.Canny(gray_img, 50, 150)
                    edge_density = float(np.sum(edges > 0) / (gray_img.shape[0] * gray_img.shape[1]))
                else:
                    sharpness = None
                    edge_density = None
                
                return ImageMetadata(
                    width=width,
                    height=height,
                    channels=channels,
                    format=format_name,
                    mode=mode,
                    file_size=file_size,
                    has_transparency=has_transparency,
                    dominant_colors=None,  # Will be filled by color analysis
                    brightness=brightness,
                    contrast=contrast,
                    sharpness=sharpness,
                    color_variance=float(np.var([stat.mean[0], stat.mean[1], stat.mean[2]])),
                    edge_density=edge_density,
                    texture_energy=None  # Will be filled by texture analysis
                )
                
        except Exception as e:
            logger.error(f"Image metadata extraction failed for {image_path}: {e}")
            return ImageMetadata(
                width=0, height=0, channels=0, format="unknown", mode="unknown",
                file_size=0, has_transparency=False, dominant_colors=None,
                brightness=None, contrast=None, sharpness=None,
                color_variance=None, edge_density=None, texture_energy=None
            )
    
    async def _run_perceptual_hashing(self, image_path: str) -> Dict[str, Any]:
        """Run perceptual hashing."""        return await asyncio.get_event_loop().run_in_executor(
            None, self.perceptual_hasher.extract_hashes, image_path
        )
    
    async def _run_clip_extraction(self, image_path: str) -> Dict[str, Any]:
        """Run CLIP embedding extraction."""        return await asyncio.get_event_loop().run_in_executor(
            None, self.clip_extractor.extract_embeddings, image_path
        )
    
    async def _run_traditional_features(self, image_path: str) -> Dict[str, Any]:
        """Run traditional feature extraction."""        return await asyncio.get_event_loop().run_in_executor(
            None, self.traditional_extractor.extract_features, image_path
        )
    
    async def _run_color_analysis(self, image_path: str) -> Dict[str, Any]:
        """Run color analysis."""        return await asyncio.get_event_loop().run_in_executor(
            None, self.color_analyzer.analyze_colors, image_path
        )
    
    async def _run_texture_analysis(self, image_path: str) -> Dict[str, Any]:
        """Run texture analysis."""        return await asyncio.get_event_loop().run_in_executor(
            None, self.texture_analyzer.analyze_texture, image_path
        )
    
    def _generate_combined_hash(self, fingerprint_data: Dict[str, Any]) -> str:
        """Generate combined hash from all fingerprint components."""        hash_components = []
        
        # Extract key hash components
        if "perceptual" in fingerprint_data and "combined_hash" in fingerprint_data["perceptual"]:
            hash_components.append(fingerprint_data["perceptual"]["combined_hash"])
            
        if "clip" in fingerprint_data and "embedding_hash" in fingerprint_data["clip"]:
            hash_components.append(fingerprint_data["clip"]["embedding_hash"])
            
        if "traditional" in fingerprint_data and "traditional_fingerprint" in fingerprint_data["traditional"]:
            hash_components.append(fingerprint_data["traditional"]["traditional_fingerprint"])
            
        if "color" in fingerprint_data and "color_fingerprint" in fingerprint_data["color"]:
            hash_components.append(fingerprint_data["color"]["color_fingerprint"])
            
        if "texture" in fingerprint_data and "texture_fingerprint" in fingerprint_data["texture"]:
            hash_components.append(fingerprint_data["texture"]["texture_fingerprint"])
        
        # Combine and hash
        combined_string = "|".join(hash_components)
        return hashlib.sha256(combined_string.encode()).hexdigest()
    
    async def find_similar(self, fingerprint_data: Dict[str, Any], threshold: float = 0.8) -> List[SimilarityMatch]:
        """        Find similar image content based on fingerprint data.
        
        Args:
            fingerprint_data: Fingerprint data to match against
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            List of similarity matches
        """        # This would typically interface with a vector database
        # For now, return empty list (implementation depends on storage backend)
        logger.info(f"Searching for similar images with threshold {threshold}")
        return []
    
    def calculate_similarity(self, fp1: Dict[str, Any], fp2: Dict[str, Any]) -> float:
        """        Calculate similarity score between two image fingerprints.
        
        Args:
            fp1: First fingerprint data
            fp2: Second fingerprint data
            
        Returns:
            Similarity score (0.0 to 1.0)
        """        similarity_scores = []
        
        # Perceptual hash similarity
        if ("perceptual" in fp1 and "perceptual" in fp2 and
            "phash" in fp1["perceptual"] and "phash" in fp2["perceptual"]):
            # Calculate Hamming distance for perceptual hashes
            phash_sim = self._hamming_similarity(fp1["perceptual"]["phash"], fp2["perceptual"]["phash"])
            similarity_scores.append(phash_sim * 0.25)  # 25% weight
        
        # CLIP similarity
        if ("clip" in fp1 and "clip" in fp2 and
            "embeddings" in fp1["clip"] and "embeddings" in fp2["clip"]):
            clip_sim = self._cosine_similarity(fp1["clip"]["embeddings"], fp2["clip"]["embeddings"])
            similarity_scores.append(clip_sim * 0.35)  # 35% weight
        
        # Color similarity
        if ("color" in fp1 and "color" in fp2 and
            "color_fingerprint" in fp1["color"] and "color_fingerprint" in fp2["color"]):
            color_sim = self._hash_similarity(fp1["color"]["color_fingerprint"], fp2["color"]["color_fingerprint"])
            similarity_scores.append(color_sim * 0.2)  # 20% weight
        
        # Traditional features similarity
        if ("traditional" in fp1 and "traditional" in fp2 and
            "traditional_fingerprint" in fp1["traditional"] and "traditional_fingerprint" in fp2["traditional"]):
            traditional_sim = self._hash_similarity(
                fp1["traditional"]["traditional_fingerprint"],
                fp2["traditional"]["traditional_fingerprint"]
            )
            similarity_scores.append(traditional_sim * 0.2)  # 20% weight
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    def _hamming_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity using Hamming distance."""        if len(hash1) != len(hash2):
            return 0.0
        
        # Convert hex hashes to binary
        try:
            bin1 = bin(int(hash1, 16))[2:].zfill(len(hash1) * 4)
            bin2 = bin(int(hash2, 16))[2:].zfill(len(hash2) * 4)
            
            # Calculate Hamming distance
            hamming_distance = sum(c1 != c2 for c1, c2 in zip(bin1, bin2))
            similarity = 1.0 - (hamming_distance / len(bin1))
            
            return similarity
        except ValueError:
            return 0.0
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors."""        try:
            vec1_array = np.array(vec1)
            vec2_array = np.array(vec2)
            
            return 1.0 - cosine(vec1_array, vec2_array)
        except Exception:
            return 0.0
    
    def _hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate hash similarity."""        if len(hash1) != len(hash2):
            return 0.0
        
        matches = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
        return matches / len(hash1)
