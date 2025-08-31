"""Advanced Image Fingerprinting Engine
Uses CLIP, ImageHash, and perceptual analysis for image content identification

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All Rights Reserved - Unauthorized use prohibited
Team: Lead Dev IA + Backend Senior + ML Engineer + Computer Vision Expert

WARNING: This code is proprietary and confidential. Any unauthorized copying,
distribution, modification or use is strictly prohibited and will be prosecuted
to the full extent of the law.
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
import hashlib
import imagehash
from PIL import Image, ImageEnhance, ImageFilter
import logging
from dataclasses import dataclass
import torch
import torchvision.transforms as transforms
from transformers import CLIPProcessor, CLIPModel
import cv2
from sklearn.metrics.pairwise import cosine_similarity
import os

logger = logging.getLogger(__name__)


@dataclass
class ImageFingerprint:
    """Image fingerprint data structure"""    perceptual_hash: str
    average_hash: str
    difference_hash: str
    wavelet_hash: str
    clip_embedding: np.ndarray
    color_histogram: np.ndarray
    texture_features: np.ndarray
    edge_features: np.ndarray
    dimensions: Tuple[int, int]
    file_size: int
    confidence_score: float


class ImageFingerprintEngine:
    """    Enterprise-grade image fingerprinting using multiple algorithms
    Combines perceptual hashing, CLIP embeddings, and computer vision features
    """    
    def __init__(self, clip_model_name: str = "openai/clip-vit-base-patch32"):
        self.clip_model = None
        self.clip_processor = None
        
        try:
            # Load CLIP model for semantic embeddings
            self.clip_model = CLIPModel.from_pretrained(clip_model_name)
            self.clip_processor = CLIPProcessor.from_pretrained(clip_model_name)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.clip_model.to(self.device)
            logger.info("CLIP model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load CLIP model: {e}")
            
    def extract_fingerprint(self, image_file_path: str) -> ImageFingerprint:
        """Extract comprehensive image fingerprint from file"""        try:
            # Load image
            image = Image.open(image_file_path)
            original_size = image.size
            file_size = os.path.getsize(image_file_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # 1. Perceptual hashes
            perceptual_hash = str(imagehash.phash(image, hash_size=16))
            average_hash = str(imagehash.average_hash(image, hash_size=16))
            difference_hash = str(imagehash.dhash(image, hash_size=16))
            wavelet_hash = str(imagehash.whash(image, hash_size=16))
            
            # 2. CLIP semantic embedding
            clip_embedding = self._extract_clip_embedding(image)
            
            # 3. Color histogram
            color_histogram = self._extract_color_histogram(image)
            
            # 4. Texture features
            texture_features = self._extract_texture_features(image)
            
            # 5. Edge features
            edge_features = self._extract_edge_features(image)
            
            # 6. Confidence score
            confidence_score = self._calculate_confidence(image, file_size)
            
            return ImageFingerprint(
                perceptual_hash=perceptual_hash,
                average_hash=average_hash,
                difference_hash=difference_hash,
                wavelet_hash=wavelet_hash,
                clip_embedding=clip_embedding,
                color_histogram=color_histogram,
                texture_features=texture_features,
                edge_features=edge_features,
                dimensions=original_size,
                file_size=file_size,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Error extracting image fingerprint: {str(e)}")
            raise
            
    def _extract_clip_embedding(self, image: Image.Image) -> np.ndarray:
        """Extract CLIP semantic embedding"""        try:
            if not self.clip_model or not self.clip_processor:
                return np.array([])
                
            # Preprocess image
            inputs = self.clip_processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Extract features
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                
            # Normalize and convert to numpy
            embedding = image_features.cpu().numpy().flatten()
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            logger.warning(f"CLIP embedding extraction failed: {str(e)}")
            return np.array([])
            
    def _extract_color_histogram(self, image: Image.Image, bins: int = 64) -> np.ndarray:
        """Extract color histogram features"""        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Extract histograms for each channel
            hist_r, _ = np.histogram(img_array[:, :, 0], bins=bins, range=(0, 256))
            hist_g, _ = np.histogram(img_array[:, :, 1], bins=bins, range=(0, 256))
            hist_b, _ = np.histogram(img_array[:, :, 2], bins=bins, range=(0, 256))
            
            # Combine histograms
            histogram = np.concatenate([hist_r, hist_g, hist_b])
            
            # Normalize
            histogram = histogram / np.sum(histogram)
            
            return histogram
            
        except Exception as e:
            logger.warning(f"Color histogram extraction failed: {str(e)}")
            return np.array([])
            
    def _extract_texture_features(self, image: Image.Image) -> np.ndarray:
        """Extract texture features using Gray Level Co-occurrence Matrix (GLCM)"""        try:
            # Convert to grayscale
            gray_image = image.convert('L')
            img_array = np.array(gray_image)
            
            # Resize for computational efficiency
            if img_array.shape[0] > 512 or img_array.shape[1] > 512:
                gray_image = gray_image.resize((512, 512), Image.Resampling.LANCZOS)
                img_array = np.array(gray_image)
            
            # Calculate texture features using OpenCV
            # 1. Local Binary Pattern approximation
            kernel_3x3 = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float32) / 16
            filtered = cv2.filter2D(img_array, -1, kernel_3x3)
            
            # 2. Gradient features
            grad_x = cv2.Sobel(img_array, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(img_array, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Statistical features
            features = [
                np.mean(filtered),
                np.std(filtered),
                np.mean(gradient_magnitude),
                np.std(gradient_magnitude),
                np.percentile(gradient_magnitude, 25),
                np.percentile(gradient_magnitude, 75)
            ]
            
            return np.array(features)
            
        except Exception as e:
            logger.warning(f"Texture feature extraction failed: {str(e)}")
            return np.array([])
            
    def _extract_edge_features(self, image: Image.Image) -> np.ndarray:
        """Extract edge-based features"""        try:
            # Convert to grayscale
            gray_image = image.convert('L')
            img_array = np.array(gray_image)
            
            # Resize for computational efficiency
            if img_array.shape[0] > 512 or img_array.shape[1] > 512:
                gray_image = gray_image.resize((512, 512), Image.Resampling.LANCZOS)
                img_array = np.array(gray_image)
            
            # Edge detection using Canny
            edges = cv2.Canny(img_array, 50, 150)
            
            # Edge statistics
            edge_density = np.sum(edges > 0) / edges.size
            
            # Edge direction histogram
            grad_x = cv2.Sobel(img_array, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(img_array, cv2.CV_64F, 0, 1, ksize=3)
            
            angles = np.arctan2(grad_y, grad_x) * 180 / np.pi
            angle_hist, _ = np.histogram(angles, bins=8, range=(-180, 180))
            angle_hist = angle_hist / np.sum(angle_hist)
            
            # Combine features
            features = np.concatenate([[edge_density], angle_hist])
            
            return features
            
        except Exception as e:
            logger.warning(f"Edge feature extraction failed: {str(e)}")
            return np.array([])
            
    def _calculate_confidence(self, image: Image.Image, file_size: int) -> float:
        """Calculate confidence score based on image quality metrics"""        try:
            # Image size factor
            width, height = image.size
            pixel_count = width * height
            size_score = min(1.0, pixel_count / (1920 * 1080))  # Normalize to 1080p
            
            # File size factor (indicates compression quality)
            size_per_pixel = file_size / pixel_count if pixel_count > 0 else 0
            quality_score = min(1.0, size_per_pixel / 3.0)  # ~3 bytes per pixel for good quality
            
            # Aspect ratio factor (standard ratios have higher confidence)
            aspect_ratio = width / height if height > 0 else 1.0
            standard_ratios = [1.0, 4/3, 16/9, 3/2, 5/4]
            ratio_score = max([1.0 - abs(aspect_ratio - ratio) for ratio in standard_ratios])
            
            # Weighted combination
            confidence = (size_score * 0.4 + 
                         quality_score * 0.4 + 
                         ratio_score * 0.2)
            
            return max(0.1, min(1.0, confidence))
            
        except Exception:
            return 0.5
            
    def compare_fingerprints(self, fp1: ImageFingerprint, 
                           fp2: ImageFingerprint) -> float:
        """Compare two image fingerprints and return similarity score (0-1)"""        try:
            scores = []
            
            # 1. Perceptual hash similarity
            hash_sim = self._compare_hashes(fp1, fp2)
            scores.append(hash_sim * 0.3)
            
            # 2. CLIP semantic similarity
            if len(fp1.clip_embedding) > 0 and len(fp2.clip_embedding) > 0:
                clip_sim = cosine_similarity([fp1.clip_embedding], [fp2.clip_embedding])[0][0]
                clip_sim = max(0.0, clip_sim)  # Ensure non-negative
                scores.append(clip_sim * 0.4)
                
            # 3. Color histogram similarity
            if len(fp1.color_histogram) > 0 and len(fp2.color_histogram) > 0:
                color_sim = self._histogram_intersection(fp1.color_histogram, fp2.color_histogram)
                scores.append(color_sim * 0.15)
                
            # 4. Texture similarity
            if len(fp1.texture_features) > 0 and len(fp2.texture_features) > 0:
                texture_sim = cosine_similarity([fp1.texture_features], [fp2.texture_features])[0][0]
                texture_sim = max(0.0, texture_sim)
                scores.append(texture_sim * 0.1)
                
            # 5. Edge similarity
            if len(fp1.edge_features) > 0 and len(fp2.edge_features) > 0:
                edge_sim = cosine_similarity([fp1.edge_features], [fp2.edge_features])[0][0]
                edge_sim = max(0.0, edge_sim)
                scores.append(edge_sim * 0.05)
                
            # Weighted average
            total_similarity = sum(scores) if scores else 0.0
            
            # Apply confidence weighting
            confidence_factor = (fp1.confidence_score + fp2.confidence_score) / 2
            
            return total_similarity * confidence_factor
            
        except Exception as e:
            logger.error(f"Error comparing image fingerprints: {str(e)}")
            return 0.0
            
    def _compare_hashes(self, fp1: ImageFingerprint, fp2: ImageFingerprint) -> float:
        """Compare perceptual hashes"""        try:
            # Convert hashes back to imagehash objects for comparison
            ph1 = imagehash.hex_to_hash(fp1.perceptual_hash)
            ph2 = imagehash.hex_to_hash(fp2.perceptual_hash)
            
            ah1 = imagehash.hex_to_hash(fp1.average_hash)
            ah2 = imagehash.hex_to_hash(fp2.average_hash)
            
            dh1 = imagehash.hex_to_hash(fp1.difference_hash)
            dh2 = imagehash.hex_to_hash(fp2.difference_hash)
            
            wh1 = imagehash.hex_to_hash(fp1.wavelet_hash)
            wh2 = imagehash.hex_to_hash(fp2.wavelet_hash)
            
            # Calculate Hamming distances (lower is more similar)
            p_dist = ph1 - ph2
            a_dist = ah1 - ah2
            d_dist = dh1 - dh2
            w_dist = wh1 - wh2
            
            # Convert to similarity scores (higher is more similar)
            max_distance = 256  # Max possible distance for 16x16 hash
            
            p_sim = 1.0 - (p_dist / max_distance)
            a_sim = 1.0 - (a_dist / max_distance)
            d_sim = 1.0 - (d_dist / max_distance)
            w_sim = 1.0 - (w_dist / max_distance)
            
            # Weighted average of hash similarities
            hash_similarity = (p_sim * 0.4 + a_sim * 0.3 + d_sim * 0.2 + w_sim * 0.1)
            
            return max(0.0, hash_similarity)
            
        except Exception as e:
            logger.warning(f"Hash comparison failed: {str(e)}")
            return 0.0
            
    def _histogram_intersection(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """Calculate histogram intersection similarity"""        try:
            if len(hist1) == 0 or len(hist2) == 0:
                return 0.0
                
            # Histogram intersection
            intersection = np.minimum(hist1, hist2)
            similarity = np.sum(intersection)
            
            return similarity
            
        except Exception:
            return 0.0
            
    def batch_extract_fingerprints(self, image_files: List[str]) -> Dict[str, ImageFingerprint]:
        """Extract fingerprints from multiple image files"""        fingerprints = {}
        
        for image_file in image_files:
            try:
                fp = self.extract_fingerprint(image_file)
                fingerprints[image_file] = fp
                logger.info(f"Successfully extracted fingerprint for: {image_file}")
            except Exception as e:
                logger.error(f"Failed to extract fingerprint for {image_file}: {str(e)}")
                
        return fingerprints
        
    def find_similar_images(self, target_fingerprint: ImageFingerprint,
                          candidate_fingerprints: Dict[str, ImageFingerprint],
                          threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Find similar image files above threshold"""        similar_files = []
        
        for file_path, candidate_fp in candidate_fingerprints.items():
            similarity = self.compare_fingerprints(target_fingerprint, candidate_fp)
            
            if similarity >= threshold:
                similar_files.append((file_path, similarity))
                
        # Sort by similarity score (descending)
        similar_files.sort(key=lambda x: x[1], reverse=True)
        
        return similar_files
        
    def detect_modifications(self, original_fp: ImageFingerprint,
                           modified_fp: ImageFingerprint) -> Dict[str, bool]:
        """Detect types of modifications made to an image"""        try:
            modifications = {
                'resized': False,
                'cropped': False,
                'color_adjusted': False,
                'compressed': False,
                'filtered': False
            }
            
            # Check for resizing
            if original_fp.dimensions != modified_fp.dimensions:
                aspect_ratio_diff = abs(
                    (original_fp.dimensions[0] / original_fp.dimensions[1]) - 
                    (modified_fp.dimensions[0] / modified_fp.dimensions[1])
                )
                
                if aspect_ratio_diff < 0.1:  # Same aspect ratio
                    modifications['resized'] = True
                else:
                    modifications['cropped'] = True
                    
            # Check for compression
            if original_fp.file_size > modified_fp.file_size * 1.5:
                modifications['compressed'] = True
                
            # Check for color adjustments
            if len(original_fp.color_histogram) > 0 and len(modified_fp.color_histogram) > 0:
                color_sim = self._histogram_intersection(
                    original_fp.color_histogram, modified_fp.color_histogram
                )
                if color_sim < 0.8:
                    modifications['color_adjusted'] = True
                    
            # Check for filtering/effects
            if len(original_fp.texture_features) > 0 and len(modified_fp.texture_features) > 0:
                texture_sim = cosine_similarity(
                    [original_fp.texture_features], [modified_fp.texture_features]
                )[0][0]
                if texture_sim < 0.7:
                    modifications['filtered'] = True
                    
            return modifications
            
        except Exception as e:
            logger.error(f"Error detecting modifications: {str(e)}")
            return {key: False for key in modifications}
