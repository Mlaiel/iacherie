"""Visual Similarity - Enterprise Visual Similarity Matching System
================================================================

Advanced visual similarity detection using deep learning embeddings,
perceptual hashing, and vector similarity for content protection and matching.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import imagehash
import hashlib
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import faiss

from ..base import BaseAgent, AgentStatus
try:
    from core.exceptions import SimilarityProcessingError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    SimilarityProcessingError, ValidationError = globals().get('SimilarityProcessingError, ValidationError', Exception)
from ...utils.performance_monitor import PerformanceMonitor
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager

logger = logging.getLogger(__name__)

class SimilarityMethod:
    """
Visual similarity detection methods"""

    PERCEPTUAL_HASH = "perceptual_hash"
    DEEP_FEATURES = "deep_features"
    HISTOGRAM = "histogram"
    STRUCTURAL = "structural"
    COMBINED = "combined"

class VisualSimilarity(BaseAgent):
    """
    Enterprise-grade visual similarity detection system using multiple
    algorithms for robust content matching and protection.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="visual_similarity",
            name="Visual Similarity",
            version="2.1.0"
        )
        
        self.performance_monitor = PerformanceMonitor("visual_similarity")
        
        # Similarity configuration
        self.similarity_thresholds = {
            'high': 0.9,
            'medium': 0.75,
            'low': 0.6
        }
        
        # Feature extraction configuration
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.feature_model = None
        self.feature_extractor = None
        self.feature_dimension = 2048
        
        # FAISS index for fast similarity search
        self.similarity_index = None
        self.indexed_fingerprints = {}
        
        # Hash types for perceptual hashing
        self.hash_functions = {
            'dhash': imagehash.dhash,
            'phash': imagehash.phash,
            'ahash': imagehash.average_hash,
            'whash': imagehash.whash
        }

    async def initialize(self) -> bool:
        """Initialize similarity detection components"""
        try:
            logger.info("Initializing Visual Similarity...")
            
            # Initialize deep learning feature extractor
            await self._initialize_feature_extractor()
            
            # Initialize FAISS index for similarity search
            await self._initialize_similarity_index()
            
            # Initialize image preprocessing
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
            
            self.status = AgentStatus.READY
            logger.info("Visual Similarity initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Visual Similarity initialization failed: {e}")
            self.status = AgentStatus.ERROR
            return False

    async def _initialize_feature_extractor(self) -> None:
        """Initialize deep learning feature extraction model"""
        try:
            # Use ResNet50 as feature extractor
            self.feature_model = models.resnet50(pretrained=True)
            
            # Remove final classification layer to get features
            self.feature_extractor = torch.nn.Sequential(
                *list(self.feature_model.children())[:-1]
            )
            
            self.feature_extractor.eval()
            self.feature_extractor.to(self.device)
            
            # Set feature dimension
            self.feature_dimension = 2048
            
            logger.info("Deep learning feature extractor initialized")
            
        except Exception as e:
            logger.error(f"Feature extractor initialization failed: {e}")
            raise

    async def _initialize_similarity_index(self) -> None:
        """Initialize FAISS index for fast similarity search"""
        try:
            # Initialize FAISS index for cosine similarity
            self.similarity_index = faiss.IndexFlatIP(self.feature_dimension)
            
            # Add GPU support if available
            if torch.cuda.is_available() and hasattr(faiss, 'StandardGpuResources'):
                gpu_resources = faiss.StandardGpuResources()
                self.similarity_index = faiss.index_cpu_to_gpu(
                    gpu_resources, 0, self.similarity_index
                )
            
            logger.info("FAISS similarity index initialized")
            
        except Exception as e:
            logger.warning(f"FAISS initialization failed, using CPU fallback: {e}")
            self.similarity_index = faiss.IndexFlatIP(self.feature_dimension)

    async def generate_fingerprint(
        self, 
        image: np.ndarray,
        method: str = SimilarityMethod.COMBINED
    ) -> Dict[str, Any]:
        """
        Generate comprehensive visual fingerprint for image
        
        Args:
            image: Input image as numpy array
            method: Fingerprint generation method
            
        Returns:
            Visual fingerprint data
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Generating visual fingerprint using {method}")
            
            # Validate input
            if image is None or image.size == 0:
                raise ValidationError("Invalid input image")
            
            fingerprint_data = {
                'generation_timestamp': datetime.now().isoformat(),
                'image_dimensions': image.shape,
                'method_used': method,
                'fingerprint_id': self._generate_unique_id(image)
            }
            
            # Generate different types of fingerprints based on method
            if method == SimilarityMethod.PERCEPTUAL_HASH or method == SimilarityMethod.COMBINED:
                perceptual_hashes = await self._generate_perceptual_hashes(image)
                fingerprint_data['perceptual_hashes'] = perceptual_hashes
            
            if method == SimilarityMethod.DEEP_FEATURES or method == SimilarityMethod.COMBINED:
                deep_features = await self._extract_deep_features(image)
                fingerprint_data['deep_features'] = deep_features
            
            if method == SimilarityMethod.HISTOGRAM or method == SimilarityMethod.COMBINED:
                color_histogram = await self._generate_color_histogram(image)
                fingerprint_data['color_histogram'] = color_histogram
            
            if method == SimilarityMethod.STRUCTURAL or method == SimilarityMethod.COMBINED:
                structural_features = await self._extract_structural_features(image)
                fingerprint_data['structural_features'] = structural_features
            
            # Generate combined fingerprint hash
            combined_fingerprint = await self._combine_fingerprints(fingerprint_data)
            fingerprint_data['combined_hash'] = combined_fingerprint
            
            processing_time = (datetime.now() - start_time).total_seconds()
            fingerprint_data['processing_time'] = processing_time
            
            logger.info(f"Fingerprint generated in {processing_time:.2f}s")
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed: {e}")
            return {
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }

    def _generate_unique_id(self, image: np.ndarray) -> str:
        """Generate unique ID for image based on content"""
        # Use basic image statistics for ID generation
        image_stats = {
            'shape': image.shape,
            'mean': float(np.mean(image)),
            'std': float(np.std(image)),
            'min': int(np.min(image)),
            'max': int(np.max(image))
        }
        
        stats_string = json.dumps(image_stats, sort_keys=True)
        return hashlib.sha256(stats_string.encode()).hexdigest()[:16]

    async def _generate_perceptual_hashes(self, image: np.ndarray) -> Dict[str, str]:
        """
Generate multiple perceptual hashes"""
        try:
            # Convert to PIL Image
            if len(image.shape) == 3:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.fromarray(image)
            
            hashes = {}
            
            for hash_name, hash_func in self.hash_functions.items():
                try:
                    hash_value = str(hash_func(pil_image))
                    hashes[hash_name] = hash_value
                except Exception as e:
                    logger.warning(f"Failed to generate {hash_name}: {e}")
                    hashes[hash_name] = None
            
            return hashes
            
        except Exception as e:
            logger.error(f"Perceptual hash generation failed: {e}")
            return {}

    async def _extract_deep_features(self, image: np.ndarray) -> List[float]:
        """Extract deep learning features"""
        try:
            # Convert to PIL and preprocess
            if len(image.shape) == 3:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            else:
                pil_image = Image.fromarray(image).convert('RGB')
            
            # Apply transforms
            input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            
            # Extract features
            with torch.no_grad():
                features = self.feature_extractor(input_tensor)
                features = features.squeeze().cpu().numpy()
                
                # Normalize features for cosine similarity
                features = features / np.linalg.norm(features)
                
                return features.tolist()
            
        except Exception as e:
            logger.error(f"Deep feature extraction failed: {e}")
            return [0.0] * self.feature_dimension

    async def _generate_color_histogram(self, image: np.ndarray) -> Dict[str, List[float]]:
        """Generate color histogram fingerprint"""
        try:
            histograms = {}
            
            if len(image.shape) == 3:
                # RGB histograms
                for i, color in enumerate(['blue', 'green', 'red']):
                    hist = cv2.calcHist([image], [i], None, [256], [0, 256])
                    hist = hist.flatten() / np.sum(hist)  # Normalize
                    histograms[color] = hist[:64].tolist()  # Use first 64 bins
                
                # HSV histogram
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                hsv_hist = cv2.calcHist([hsv], [0, 1, 2], None, [50, 60, 60], 
                                      [0, 180, 0, 256, 0, 256])
                hsv_hist = hsv_hist.flatten() / np.sum(hsv_hist)
                histograms['hsv'] = hsv_hist[:100].tolist()  # Use first 100 bins
            
            else:
                # Grayscale histogram
                hist = cv2.calcHist([image], [0], None, [256], [0, 256])
                hist = hist.flatten() / np.sum(hist)
                histograms['grayscale'] = hist[:64].tolist()
            
            return histograms
            
        except Exception as e:
            logger.error(f"Color histogram generation failed: {e}")
            return {}

    async def _extract_structural_features(self, image: np.ndarray) -> Dict[str, float]:
        """Extract structural features like edges, corners, etc."""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            features = {}
            
            # Edge density
            edges = cv2.Canny(gray, 100, 200)
            features['edge_density'] = float(np.sum(edges > 0) / edges.size)
            
            # Corner detection
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, 
                                            qualityLevel=0.01, minDistance=10)
            features['corner_count'] = len(corners) if corners is not None else 0
            
            # Texture analysis using Local Binary Patterns
            from skimage import feature
            lbp = feature.local_binary_pattern(gray, P=8, R=1, method='uniform')
            lbp_hist, _ = np.histogram(lbp.ravel(), bins=10)
            lbp_hist = lbp_hist / np.sum(lbp_hist)
            features['texture_uniformity'] = float(np.std(lbp_hist))
            
            # Gradient magnitude
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            features['gradient_mean'] = float(np.mean(grad_magnitude))
            features['gradient_std'] = float(np.std(grad_magnitude))
            
            return features
            
        except Exception as e:
            logger.error(f"Structural feature extraction failed: {e}")
            return {}

    async def _combine_fingerprints(self, fingerprint_data: Dict[str, Any]) -> str:
        """Combine all fingerprint components into single hash"""
        try:
            # Collect all fingerprint components
            components = []
            
            # Add perceptual hashes
            if 'perceptual_hashes' in fingerprint_data:
                for hash_value in fingerprint_data['perceptual_hashes'].values():
                    if hash_value:
                        components.append(str(hash_value))
            
            # Add deep features (use first 32 values)
            if 'deep_features' in fingerprint_data:
                features = fingerprint_data['deep_features'][:32]
                features_str = ','.join([f"{f:.6f}" for f in features])
                components.append(features_str)
            
            # Add color histogram summary
            if 'color_histogram' in fingerprint_data:
                for hist_name, hist_data in fingerprint_data['color_histogram'].items():
                    hist_summary = sum(hist_data[:10])  # Sum of first 10 bins
                    components.append(f"{hist_name}:{hist_summary:.6f}")
            
            # Add structural features
            if 'structural_features' in fingerprint_data:
                for feature_name, feature_value in fingerprint_data['structural_features'].items():
                    components.append(f"{feature_name}:{feature_value:.6f}")
            
            # Combine all components
            combined_string = '|'.join(components)
            combined_hash = hashlib.sha256(combined_string.encode()).hexdigest()
            
            return combined_hash
            
        except Exception as e:
            logger.error(f"Fingerprint combination failed: {e}")
            return ""

    async def compare_images(
        self, 
        image1: np.ndarray,
        image2: np.ndarray,
        similarity_method: str = SimilarityMethod.COMBINED
    ) -> Dict[str, Any]:
        """
        Compare two images for visual similarity
        
        Args:
            image1: First image
            image2: Second image  
            similarity_method: Method to use for comparison
            
        Returns:
            Similarity comparison results
        """
        start_time = datetime.now()
        
        try:
            logger.info("Comparing images for similarity...")
            
            # Generate fingerprints for both images
            fingerprint1 = await self.generate_fingerprint(image1, similarity_method)
            fingerprint2 = await self.generate_fingerprint(image2, similarity_method)
            
            if 'error' in fingerprint1 or 'error' in fingerprint2:
                raise SimilarityProcessingError("Failed to generate fingerprints")
            
            # Calculate similarity scores
            similarity_scores = {}
            
            # Perceptual hash similarity
            if 'perceptual_hashes' in fingerprint1 and 'perceptual_hashes' in fingerprint2:
                hash_similarities = await self._compare_perceptual_hashes(
                    fingerprint1['perceptual_hashes'],
                    fingerprint2['perceptual_hashes']
                )
                similarity_scores['perceptual'] = hash_similarities
            
            # Deep feature similarity
            if 'deep_features' in fingerprint1 and 'deep_features' in fingerprint2:
                feature_similarity = await self._compare_deep_features(
                    fingerprint1['deep_features'],
                    fingerprint2['deep_features']
                )
                similarity_scores['deep_features'] = feature_similarity
            
            # Histogram similarity
            if 'color_histogram' in fingerprint1 and 'color_histogram' in fingerprint2:
                histogram_similarity = await self._compare_histograms(
                    fingerprint1['color_histogram'],
                    fingerprint2['color_histogram']
                )
                similarity_scores['histogram'] = histogram_similarity
            
            # Structural similarity
            if 'structural_features' in fingerprint1 and 'structural_features' in fingerprint2:
                structural_similarity = await self._compare_structural_features(
                    fingerprint1['structural_features'],
                    fingerprint2['structural_features']
                )
                similarity_scores['structural'] = structural_similarity
            
            # Calculate overall similarity
            overall_similarity = await self._calculate_overall_similarity(similarity_scores)
            
            # Determine similarity level
            similarity_level = self._determine_similarity_level(overall_similarity)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'overall_similarity': overall_similarity,
                'similarity_level': similarity_level,
                'detailed_scores': similarity_scores,
                'fingerprint1_id': fingerprint1.get('fingerprint_id'),
                'fingerprint2_id': fingerprint2.get('fingerprint_id'),
                'processing_time': processing_time,
                'method_used': similarity_method,
                'is_similar': overall_similarity >= self.similarity_thresholds['low']
            }
            
            logger.info(
                f"Image comparison completed: {overall_similarity:.3f} "
                f"similarity ({similarity_level}) in {processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Image comparison failed: {e}")
            return {
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'overall_similarity': 0.0,
                'is_similar': False
            }

    async def _compare_perceptual_hashes(
        self, 
        hashes1: Dict[str, str], 
        hashes2: Dict[str, str]
    ) -> Dict[str, float]:
        """Compare perceptual hashes"""
        similarities = {}
        
        for hash_type in self.hash_functions.keys():
            if hash_type in hashes1 and hash_type in hashes2:
                hash1_val = hashes1[hash_type]
                hash2_val = hashes2[hash_type]
                
                if hash1_val and hash2_val:
                    try:
                        # Calculate Hamming distance
                        hash1_obj = imagehash.hex_to_hash(hash1_val)
                        hash2_obj = imagehash.hex_to_hash(hash2_val)
                        
                        hamming_distance = abs(hash1_obj - hash2_obj)
                        max_distance = len(hash1_val) * 4  # 4 bits per hex char
                        
                        similarity = 1.0 - (hamming_distance / max_distance)
                        similarities[hash_type] = similarity
                        
                    except Exception as e:
                        logger.warning(f"Hash comparison failed for {hash_type}: {e}")
                        similarities[hash_type] = 0.0
        
        return similarities

    async def _compare_deep_features(
        self, 
        features1: List[float], 
        features2: List[float]
    ) -> float:
        """Compare deep learning features using cosine similarity"""
        try:
            features1_array = np.array(features1).reshape(1, -1)
            features2_array = np.array(features2).reshape(1, -1)
            
            similarity = cosine_similarity(features1_array, features2_array)[0][0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Deep feature comparison failed: {e}")
            return 0.0

    async def _compare_histograms(
        self, 
        hist1: Dict[str, List[float]], 
        hist2: Dict[str, List[float]]
    ) -> Dict[str, float]:
        """Compare color histograms"""
        similarities = {}
        
        for hist_type in hist1.keys():
            if hist_type in hist2:
                try:
                    # Use correlation similarity
                    correlation = cv2.compareHist(
                        np.array(hist1[hist_type], dtype=np.float32),
                        np.array(hist2[hist_type], dtype=np.float32),
                        cv2.HISTCMP_CORREL
                    )
                    similarities[hist_type] = float(correlation)
                    
                except Exception as e:
                    logger.warning(f"Histogram comparison failed for {hist_type}: {e}")
                    similarities[hist_type] = 0.0
        
        return similarities

    async def _compare_structural_features(
        self, 
        features1: Dict[str, float], 
        features2: Dict[str, float]
    ) -> Dict[str, float]:
        """Compare structural features"""
        similarities = {}
        
        for feature_name in features1.keys():
            if feature_name in features2:
                val1 = features1[feature_name]
                val2 = features2[feature_name]
                
                # Normalize difference to similarity score
                max_val = max(abs(val1), abs(val2), 1.0)
                difference = abs(val1 - val2) / max_val
                similarity = 1.0 - min(difference, 1.0)
                
                similarities[feature_name] = similarity
        
        return similarities

    async def _calculate_overall_similarity(self, similarity_scores: Dict[str, Any]) -> float:
        """
Calculate weighted overall similarity score"""
        try:
            total_weight = 0.0
            weighted_sum = 0.0
            
            # Weights for different similarity methods
            weights = {
                'perceptual': 0.25,
                'deep_features': 0.35,
                'histogram': 0.25,
                'structural': 0.15
            }
            
            # Perceptual hash scores
            if 'perceptual' in similarity_scores:
                perceptual_scores = list(similarity_scores['perceptual'].values())
                if perceptual_scores:
                    avg_perceptual = np.mean([s for s in perceptual_scores if s > 0])
                    weighted_sum += avg_perceptual * weights['perceptual']
                    total_weight += weights['perceptual']
            
            # Deep feature score
            if 'deep_features' in similarity_scores:
                weighted_sum += similarity_scores['deep_features'] * weights['deep_features']
                total_weight += weights['deep_features']
            
            # Histogram scores
            if 'histogram' in similarity_scores:
                histogram_scores = list(similarity_scores['histogram'].values())
                if histogram_scores:
                    avg_histogram = np.mean([s for s in histogram_scores if s > 0])
                    weighted_sum += avg_histogram * weights['histogram']
                    total_weight += weights['histogram']
            
            # Structural scores
            if 'structural' in similarity_scores:
                structural_scores = list(similarity_scores['structural'].values())
                if structural_scores:
                    avg_structural = np.mean([s for s in structural_scores if s > 0])
                    weighted_sum += avg_structural * weights['structural']
                    total_weight += weights['structural']
            
            # Calculate final score
            overall_similarity = weighted_sum / total_weight if total_weight > 0 else 0.0
            return max(0.0, min(1.0, overall_similarity))
            
        except Exception as e:
            logger.error(f"Overall similarity calculation failed: {e}")
            return 0.0

    def _determine_similarity_level(self, similarity_score: float) -> str:
        """Determine similarity level based on score"""
        if similarity_score >= self.similarity_thresholds['high']:
            return 'high'
        elif similarity_score >= self.similarity_thresholds['medium']:
            return 'medium'
        elif similarity_score >= self.similarity_thresholds['low']:
            return 'low'
        else:
            return 'none'

    async def search_similar(
        self, 
        query_fingerprint: str,
        similarity_threshold: float = 0.8,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for visually similar content using fingerprint
        
        Args:
            query_fingerprint: Fingerprint to search for
            similarity_threshold: Minimum similarity threshold
            limit: Maximum number of results
            
        Returns:
            List of similar content with similarity scores
        """
        try:
            # This would query the database for similar fingerprints
            # For now, return empty list as placeholder
            
            logger.info(f"Searching for similar content with threshold {similarity_threshold}")
            
            similar_content = []
            
            # In production, this would:
            # 1. Query database for content with similar fingerprints
            # 2. Use FAISS index for fast similarity search
            # 3. Apply similarity threshold filtering
            # 4. Return top results with metadata
            
            return similar_content
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []

    async def add_to_index(
        self, 
        content_id: str, 
        fingerprint_data: Dict[str, Any]
    ) -> bool:
        """Add fingerprint to similarity index"""
        try:
            if 'deep_features' in fingerprint_data:
                features = np.array(fingerprint_data['deep_features'], dtype=np.float32)
                features = features.reshape(1, -1)
                
                # Add to FAISS index
                self.similarity_index.add(features)
                
                # Store mapping
                index_id = self.similarity_index.ntotal - 1
                self.indexed_fingerprints[index_id] = {
                    'content_id': content_id,
                    'fingerprint_id': fingerprint_data.get('fingerprint_id'),
                    'combined_hash': fingerprint_data.get('combined_hash')
                }
                
                logger.info(f"Added content {content_id} to similarity index")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to add to index: {e}")
            return False

    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            await self.performance_monitor.close()
            
            # Clear models and indices
            if hasattr(self, 'feature_model'):
                del self.feature_model
            if hasattr(self, 'feature_extractor'):
                del self.feature_extractor
            if hasattr(self, 'similarity_index'):
                del self.similarity_index
            
            self.indexed_fingerprints.clear()
            
            logger.info("Visual Similarity cleanup completed")
        except Exception as e:
            logger.error(f"Visual Similarity cleanup failed: {e}")

    def get_similarity_stats(self) -> Dict[str, Any]:
        """Get similarity detection statistics"""
        return {
            'indexed_fingerprints': len(self.indexed_fingerprints),
            'similarity_thresholds': self.similarity_thresholds,
            'supported_methods': [
                SimilarityMethod.PERCEPTUAL_HASH,
                SimilarityMethod.DEEP_FEATURES,
                SimilarityMethod.HISTOGRAM,
                SimilarityMethod.STRUCTURAL,
                SimilarityMethod.COMBINED
            ],
            'hash_functions': list(self.hash_functions.keys())
        }
