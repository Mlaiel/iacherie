"""IA Influencer Agent - Similarity Engine
High-performance similarity matching and vector search for fingerprints

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved to Fahed Mlaiel
Warning: Unauthorized use, copying, or distribution of this code is strictly prohibited
"""
import asyncio
import logging
import numpy as np
import time
import pickle
import json
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from pathlib import Path
import hashlib
from concurrent.futures import ThreadPoolExecutor

# Vector database imports (can be replaced with production vector DB)
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available, using fallback similarity search")

from .fingerprint_manager import FingerprintResult, ContentType

logger = logging.getLogger(__name__)


@dataclass
class SimilarityMatch:
    """Similarity match result"""
    query_id: str
    match_id: str
    similarity_score: float
    match_fingerprint: FingerprintResult
    match_methods: Dict[str, float]
    confidence: float


@dataclass
class VectorIndex:
    """Vector index for similarity search"""
    index_id: str
    content_type: ContentType
    vector_dimension: int
    index_size: int
    created_at: float
    last_updated: float


class SimilarityEngine:
    """
    High-performance similarity engine for fingerprint matching
    using vector similarity and optimized search algorithms
    """
    
    def __init__(self, vector_dimension: int = 512, use_gpu: bool = False):
        """
        Initialize similarity engine
        
        Args:
            vector_dimension: Dimension for vector embeddings
            use_gpu: Whether to use GPU acceleration (if available)
        """
        self.vector_dimension = vector_dimension
        self.use_gpu = use_gpu and FAISS_AVAILABLE
        
        # Vector indices for different content types
        self.indices = {}
        self.fingerprint_mappings = {}  # Maps vector IDs to fingerprint results
        self.vector_cache = {}
        
        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Search parameters
        self.default_search_k = 50  # Number of candidates to examine
        self.similarity_threshold = 0.7
        
        self._initialize_indices()
        
        logger.info(f"SimilarityEngine initialized with dimension={vector_dimension}")
    
    def _initialize_indices(self):
        """Initialize FAISS indices for each content type"""
        try:
            for content_type in [ContentType.AUDIO, ContentType.VIDEO, ContentType.IMAGE]:
                index_id = f"{content_type.value}_index"
                
                if FAISS_AVAILABLE:
                    # Create FAISS index
                    if self.use_gpu:
                        # GPU index (if CUDA available)
                        try:
                            res = faiss.StandardGpuResources()
                            index = faiss.IndexFlatIP(self.vector_dimension)  # Inner product for cosine similarity
                            gpu_index = faiss.index_cpu_to_gpu(res, 0, index)
                            self.indices[content_type] = gpu_index
                            logger.info(f"Created GPU index for {content_type.value}")
                        except Exception as e:
                            logger.warning(f"GPU index creation failed, using CPU: {str(e)}")
                            self.indices[content_type] = faiss.IndexFlatIP(self.vector_dimension)
                    else:
                        # CPU index
                        self.indices[content_type] = faiss.IndexFlatIP(self.vector_dimension)
                        logger.info(f"Created CPU index for {content_type.value}")
                else:
                    # Fallback: simple in-memory storage
                    self.indices[content_type] = {
                        'vectors': [],
                        'fingerprint_ids': [],
                        'index_type': 'fallback'
                    }
                    logger.info(f"Created fallback index for {content_type.value}")
                
                # Initialize mapping
                self.fingerprint_mappings[content_type] = {}
                
        except Exception as e:
            logger.error(f"Error initializing indices: {str(e)}")
            raise
    
    async def add_fingerprint(
        self, 
        fingerprint: FingerprintResult,
        update_existing: bool = False
    ) -> bool:
        """
        Add fingerprint to similarity index
        
        Args:
            fingerprint: Fingerprint result to add
            update_existing: Whether to update if fingerprint already exists
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not fingerprint.success:
                logger.warning(f"Skipping failed fingerprint: {fingerprint.request_id}")
                return False
            
            content_type = fingerprint.content_type
            
            # Check if already exists
            if (fingerprint.request_id in self.fingerprint_mappings[content_type] and 
                not update_existing):
                logger.info(f"Fingerprint {fingerprint.request_id} already exists, skipping")
                return True
            
            # Convert fingerprint to vector
            vector = await self._fingerprint_to_vector(fingerprint)
            
            if vector is None:
                logger.error(f"Failed to convert fingerprint to vector: {fingerprint.request_id}")
                return False
            
            # Add to index
            success = await self._add_vector_to_index(content_type, vector, fingerprint)
            
            if success:
                logger.info(f"Added fingerprint {fingerprint.request_id} to index")
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding fingerprint to index: {str(e)}")
            return False
    
    async def _fingerprint_to_vector(self, fingerprint: FingerprintResult) -> Optional[np.ndarray]:
        """Convert fingerprint data to vector representation"""
        try:
            methods_data = fingerprint.fingerprint_data.get('methods', {})
            
            if not methods_data:
                return None
            
            # Extract features based on content type
            if fingerprint.content_type == ContentType.AUDIO:
                return await self._audio_fingerprint_to_vector(methods_data)
            elif fingerprint.content_type == ContentType.VIDEO:
                return await self._video_fingerprint_to_vector(methods_data)
            elif fingerprint.content_type == ContentType.IMAGE:
                return await self._image_fingerprint_to_vector(methods_data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error converting fingerprint to vector: {str(e)}")
            return None
    
    async def _audio_fingerprint_to_vector(self, methods_data: Dict) -> Optional[np.ndarray]:
        """Convert audio fingerprint to vector"""
        try:
            features = []
            
            # Chromaprint features
            if 'chromaprint' in methods_data and 'error' not in methods_data['chromaprint']:
                # Hash to consistent numeric features
                hash_str = methods_data['chromaprint'].get('hash', '')
                hash_features = self._hash_to_features(hash_str, 128)
                features.extend(hash_features)
            else:
                features.extend([0.0] * 128)
            
            # MFCC features
            if 'mfcc' in methods_data and 'error' not in methods_data['mfcc']:
                mfcc_means = methods_data['mfcc'].get('mfcc_means', [])
                mfcc_vars = methods_data['mfcc'].get('mfcc_vars', [])
                
                # Pad or truncate to fixed size
                mfcc_features = (mfcc_means + mfcc_vars)[:128]
                mfcc_features.extend([0.0] * (128 - len(mfcc_features)))
                features.extend(mfcc_features)
            else:
                features.extend([0.0] * 128)
            
            # Spectral features
            if 'spectral_hash' in methods_data and 'error' not in methods_data['spectral_hash']:
                spectral_data = methods_data['spectral_hash']
                spectral_features = [
                    spectral_data.get('centroid_mean', 0.0),
                    spectral_data.get('rolloff_mean', 0.0),
                    spectral_data.get('zcr_mean', 0.0)
                ]
                # Normalize and pad
                spectral_features = self._normalize_features(spectral_features, 128)
                features.extend(spectral_features)
            else:
                features.extend([0.0] * 128)
            
            # Rhythm features
            if 'tempo_rhythm' in methods_data and 'error' not in methods_data['tempo_rhythm']:
                rhythm_data = methods_data['tempo_rhythm']
                rhythm_features = [rhythm_data.get('tempo', 0.0) / 200.0]  # Normalize tempo
                beat_hist = rhythm_data.get('beat_histogram', [])[:127]  # Take first 127
                beat_hist.extend([0.0] * (127 - len(beat_hist)))
                rhythm_features.extend(beat_hist)
                features.extend(rhythm_features)
            else:
                features.extend([0.0] * 128)
            
            # Ensure correct dimension
            vector = np.array(features[:self.vector_dimension], dtype=np.float32)
            if len(vector) < self.vector_dimension:
                vector = np.pad(vector, (0, self.vector_dimension - len(vector)))
            
            # Normalize vector
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            return vector
            
        except Exception as e:
            logger.error(f"Error converting audio fingerprint: {str(e)}")
            return None
    
    async def _video_fingerprint_to_vector(self, methods_data: Dict) -> Optional[np.ndarray]:
        """Convert video fingerprint to vector"""
        try:
            features = []
            
            # Perceptual hash features
            if 'perceptual_hash' in methods_data and 'error' not in methods_data['perceptual_hash']:
                sequence_hash = methods_data['perceptual_hash'].get('sequence_hash', '')
                if sequence_hash:
                    # Use first few hash values
                    hash_features = self._hash_to_features(''.join(sequence_hash[:10]), 128)
                    features.extend(hash_features)
                else:
                    features.extend([0.0] * 128)
            else:
                features.extend([0.0] * 128)
            
            # Histogram features
            if 'histogram' in methods_data and 'error' not in methods_data['histogram']:
                avg_hist = methods_data['histogram'].get('average_histogram', {})
                hist_features = []
                for channel in ['hue', 'saturation', 'value']:
                    channel_hist = avg_hist.get(channel, [])[:42]  # ~42 bins per channel
                    channel_hist.extend([0.0] * (42 - len(channel_hist)))
                    hist_features.extend(channel_hist)
                
                # Pad to 128
                hist_features = hist_features[:128]
                hist_features.extend([0.0] * (128 - len(hist_features)))
                features.extend(hist_features)
            else:
                features.extend([0.0] * 128)
            
            # Optical flow features
            if 'optical_flow' in methods_data and 'error' not in methods_data['optical_flow']:
                flow_data = methods_data['optical_flow']
                flow_features = [
                    flow_data.get('average_magnitude', 0.0),
                    flow_data.get('average_direction_variance', 0.0)
                ]
                flow_features = self._normalize_features(flow_features, 128)
                features.extend(flow_features)
            else:
                features.extend([0.0] * 128)
            
            # Edge features
            if 'edge_detection' in methods_data and 'error' not in methods_data['edge_detection']:
                edge_data = methods_data['edge_detection']
                edge_features = [
                    edge_data.get('average_edge_density', 0.0),
                    edge_data.get('average_line_count', 0.0) / 1000.0  # Normalize
                ]
                orientation_hist = edge_data.get('average_orientation', [])[:126]
                orientation_hist.extend([0.0] * (126 - len(orientation_hist)))
                edge_features.extend(orientation_hist)
                features.extend(edge_features)
            else:
                features.extend([0.0] * 128)
            
            # Ensure correct dimension
            vector = np.array(features[:self.vector_dimension], dtype=np.float32)
            if len(vector) < self.vector_dimension:
                vector = np.pad(vector, (0, self.vector_dimension - len(vector)))
            
            # Normalize vector
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            return vector
            
        except Exception as e:
            logger.error(f"Error converting video fingerprint: {str(e)}")
            return None
    
    async def _image_fingerprint_to_vector(self, methods_data: Dict) -> Optional[np.ndarray]:
        """Convert image fingerprint to vector"""
        try:
            features = []
            
            # Perceptual hash features
            if 'perceptual_hash' in methods_data and 'error' not in methods_data['perceptual_hash']:
                hashes = methods_data['perceptual_hash'].get('hashes', {})
                hash_features = []
                
                for hash_type in ['average_hash', 'difference_hash', 'perceptual_hash', 'wavelet_hash']:
                    hash_val = hashes.get(hash_type, '')
                    hash_nums = self._hash_to_features(hash_val, 32)
                    hash_features.extend(hash_nums)
                
                features.extend(hash_features[:128])
                if len(hash_features) < 128:
                    features.extend([0.0] * (128 - len(hash_features)))
            else:
                features.extend([0.0] * 128)
            
            # Histogram features
            if 'histogram' in methods_data and 'error' not in methods_data['histogram']:
                bgr_hists = methods_data['histogram'].get('bgr_histograms', [])
                hist_features = []
                
                for hist in bgr_hists[:3]:  # RGB channels
                    # Take statistical features from histogram
                    if hist:
                        hist_array = np.array(hist)
                        stats = [
                            np.mean(hist_array),
                            np.std(hist_array),
                            np.max(hist_array),
                            float(np.argmax(hist_array))  # Peak location
                        ]
                        hist_features.extend(stats)
                
                # Pad to 128
                hist_features = hist_features[:128]
                hist_features.extend([0.0] * (128 - len(hist_features)))
                features.extend(hist_features)
            else:
                features.extend([0.0] * 128)
            
            # SIFT features
            if 'sift_features' in methods_data and 'error' not in methods_data['sift_features']:
                sift_data = methods_data['sift_features']
                descriptor_stats = sift_data.get('descriptor_stats', {})
                
                sift_features = [
                    float(descriptor_stats.get('count', 0)) / 1000.0  # Normalize keypoint count
                ]
                
                # Use means of descriptors (first 127 dimensions)
                means = descriptor_stats.get('mean', [])[:127]
                means.extend([0.0] * (127 - len(means)))
                sift_features.extend(means)
                
                features.extend(sift_features)
            else:
                features.extend([0.0] * 128)
            
            # Texture features
            if 'texture_analysis' in methods_data and 'error' not in methods_data['texture_analysis']:
                texture_data = methods_data['texture_analysis']
                
                # LBP histogram statistics
                lbp_hist = texture_data.get('lbp_histogram', [])
                if lbp_hist:
                    lbp_array = np.array(lbp_hist)
                    texture_features = [
                        np.mean(lbp_array),
                        np.std(lbp_array),
                        np.max(lbp_array)
                    ]
                else:
                    texture_features = [0.0, 0.0, 0.0]
                
                # Gabor responses (first 125 dimensions)
                gabor_responses = texture_data.get('gabor_responses', [])[:125]
                gabor_responses.extend([0.0] * (125 - len(gabor_responses)))
                texture_features.extend(gabor_responses)
                
                features.extend(texture_features)
            else:
                features.extend([0.0] * 128)
            
            # Ensure correct dimension
            vector = np.array(features[:self.vector_dimension], dtype=np.float32)
            if len(vector) < self.vector_dimension:
                vector = np.pad(vector, (0, self.vector_dimension - len(vector)))
            
            # Normalize vector
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            return vector
            
        except Exception as e:
            logger.error(f"Error converting image fingerprint: {str(e)}")
            return None
    
    def _hash_to_features(self, hash_str: str, target_length: int) -> List[float]:
        """Convert hash string to numeric features"""
        try:
            if not hash_str:
                return [0.0] * target_length
            
            # Convert hash to bytes and then to numbers
            hash_bytes = hashlib.sha256(hash_str.encode()).digest()
            features = [float(b) / 255.0 for b in hash_bytes]  # Normalize to [0,1]
            
            # Repeat or truncate to target length
            while len(features) < target_length:
                features.extend(features[:min(len(features), target_length - len(features))])
            
            return features[:target_length]
            
        except Exception as e:
            logger.error(f"Error converting hash to features: {str(e)}")
            return [0.0] * target_length
    
    def _normalize_features(self, features: List[float], target_length: int) -> List[float]:
        """Normalize and pad/truncate features to target length"""
        try:
            if not features:
                return [0.0] * target_length
            
            # Normalize to prevent any feature from dominating
            max_val = max(abs(f) for f in features)
            if max_val > 0:
                normalized = [f / max_val for f in features]
            else:
                normalized = features
            
            # Pad or truncate
            if len(normalized) < target_length:
                normalized.extend([0.0] * (target_length - len(normalized)))
            
            return normalized[:target_length]
            
        except Exception as e:
            logger.error(f"Error normalizing features: {str(e)}")
            return [0.0] * target_length
    
    async def _add_vector_to_index(
        self, 
        content_type: ContentType, 
        vector: np.ndarray, 
        fingerprint: FingerprintResult
    ) -> bool:
        """Add vector to appropriate index"""
        try:
            if FAISS_AVAILABLE and not isinstance(self.indices[content_type], dict):
                # FAISS index
                index = self.indices[content_type]
                vector_id = index.ntotal  # Use current size as ID
                
                # Reshape for FAISS (expects 2D array)
                vector_2d = vector.reshape(1, -1)
                index.add(vector_2d)
                
                # Store mapping
                self.fingerprint_mappings[content_type][vector_id] = fingerprint
                
            else:
                # Fallback index
                index = self.indices[content_type]
                vector_id = len(index['vectors'])
                
                index['vectors'].append(vector)
                index['fingerprint_ids'].append(fingerprint.request_id)
                
                # Store mapping
                self.fingerprint_mappings[content_type][vector_id] = fingerprint
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding vector to index: {str(e)}")
            return False
    
    async def search_similar(
        self, 
        query_fingerprint: FingerprintResult,
        k: int = 10,
        similarity_threshold: float = None
    ) -> List[SimilarityMatch]:
        """
        Search for similar fingerprints
        
        Args:
            query_fingerprint: Query fingerprint to search with
            k: Number of similar results to return
            similarity_threshold: Minimum similarity score
        
        Returns:
            List of similarity matches
        """
        try:
            if not query_fingerprint.success:
                return []
            
            threshold = similarity_threshold or self.similarity_threshold
            content_type = query_fingerprint.content_type
            
            # Convert query to vector
            query_vector = await self._fingerprint_to_vector(query_fingerprint)
            if query_vector is None:
                return []
            
            # Search in index
            if FAISS_AVAILABLE and not isinstance(self.indices[content_type], dict):
                matches = await self._search_faiss_index(
                    content_type, query_vector, query_fingerprint, k, threshold
                )
            else:
                matches = await self._search_fallback_index(
                    content_type, query_vector, query_fingerprint, k, threshold
                )
            
            logger.info(f"Found {len(matches)} similar matches for {query_fingerprint.request_id}")
            return matches
            
        except Exception as e:
            logger.error(f"Error searching similar fingerprints: {str(e)}")
            return []
    
    async def _search_faiss_index(
        self, 
        content_type: ContentType, 
        query_vector: np.ndarray,
        query_fingerprint: FingerprintResult,
        k: int, 
        threshold: float
    ) -> List[SimilarityMatch]:
        """Search using FAISS index"""
        try:
            index = self.indices[content_type]
            
            if index.ntotal == 0:
                return []
            
            # Reshape query vector for FAISS
            query_2d = query_vector.reshape(1, -1)
            
            # Search
            search_k = min(k * 2, index.ntotal)  # Search more candidates
            similarities, indices = index.search(query_2d, search_k)
            
            matches = []
            
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx == -1:  # Invalid index
                    continue
                
                if similarity < threshold:
                    continue
                
                # Get fingerprint from mapping
                match_fingerprint = self.fingerprint_mappings[content_type].get(idx)
                
                if match_fingerprint is None:
                    continue
                
                # Skip self-match
                if match_fingerprint.request_id == query_fingerprint.request_id:
                    continue
                
                # Calculate detailed similarity by methods
                method_similarities = await self._calculate_method_similarities(
                    query_fingerprint, match_fingerprint
                )
                
                match = SimilarityMatch(
                    query_id=query_fingerprint.request_id,
                    match_id=match_fingerprint.request_id,
                    similarity_score=float(similarity),
                    match_fingerprint=match_fingerprint,
                    match_methods=method_similarities,
                    confidence=min(1.0, float(similarity) * 1.1)  # Boost confidence slightly
                )
                
                matches.append(match)
                
                if len(matches) >= k:
                    break
            
            return matches
            
        except Exception as e:
            logger.error(f"Error in FAISS search: {str(e)}")
            return []
    
    async def _search_fallback_index(
        self, 
        content_type: ContentType, 
        query_vector: np.ndarray,
        query_fingerprint: FingerprintResult,
        k: int, 
        threshold: float
    ) -> List[SimilarityMatch]:
        """Search using fallback index (simple cosine similarity)"""
        try:
            index = self.indices[content_type]
            
            if not index['vectors']:
                return []
            
            similarities = []
            
            # Calculate similarities with all vectors
            for i, stored_vector in enumerate(index['vectors']):
                # Cosine similarity
                dot_product = np.dot(query_vector, stored_vector)
                similarity = float(dot_product)  # Vectors are already normalized
                
                if similarity >= threshold:
                    similarities.append((similarity, i))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            matches = []
            
            for similarity, idx in similarities[:k]:
                match_fingerprint = self.fingerprint_mappings[content_type].get(idx)
                
                if match_fingerprint is None:
                    continue
                
                # Skip self-match
                if match_fingerprint.request_id == query_fingerprint.request_id:
                    continue
                
                # Calculate detailed similarity by methods
                method_similarities = await self._calculate_method_similarities(
                    query_fingerprint, match_fingerprint
                )
                
                match = SimilarityMatch(
                    query_id=query_fingerprint.request_id,
                    match_id=match_fingerprint.request_id,
                    similarity_score=similarity,
                    match_fingerprint=match_fingerprint,
                    match_methods=method_similarities,
                    confidence=similarity
                )
                
                matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error in fallback search: {str(e)}")
            return []
    
    async def _calculate_method_similarities(
        self, 
        fp1: FingerprintResult, 
        fp2: FingerprintResult
    ) -> Dict[str, float]:
        """Calculate similarity scores for each method using real algorithms"""
        try:
            method_similarities = {}
            
            methods1 = fp1.fingerprint_data.get('methods', {})
            methods2 = fp2.fingerprint_data.get('methods', {})
            
            for method in set(methods1.keys()) & set(methods2.keys()):
                if 'error' not in methods1[method] and 'error' not in methods2[method]:
                    # Use method-specific similarity calculations
                    similarity = await self._calculate_method_specific_similarity(
                        method, methods1[method], methods2[method], fp1.content_type
                    )
                    method_similarities[method] = similarity
            
            return method_similarities
            
        except Exception as e:
            logger.error(f"Error calculating method similarities: {str(e)}")
            return {}

    async def _calculate_method_specific_similarity(
        self,
        method: str,
        data1: Dict[str, Any],
        data2: Dict[str, Any],
        content_type: ContentType
    ) -> float:
        """Calculate similarity using method-specific algorithms."""
        try:
            # Audio-specific methods
            if content_type == ContentType.AUDIO:
                if method == 'chromaprint':
                    return self._chromaprint_similarity(data1, data2)
                elif method == 'mfcc' or 'mfcc' in method:
                    return self._mfcc_similarity(data1, data2)
                elif method == 'spectral':
                    return self._spectral_similarity(data1, data2)
            
            # Image-specific methods
            elif content_type == ContentType.IMAGE:
                if 'phash' in method or 'perceptual' in method:
                    return self._perceptual_hash_similarity(data1, data2)
                elif 'color' in method or 'histogram' in method:
                    return self._color_histogram_similarity(data1, data2)
                elif 'sift' in method or 'orb' in method:
                    return self._feature_descriptor_similarity(data1, data2)
            
            # Video-specific methods
            elif content_type == ContentType.VIDEO:
                if 'frame' in method or 'temporal' in method:
                    return self._temporal_similarity(data1, data2)
                elif 'motion' in method or 'optical' in method:
                    return self._motion_similarity(data1, data2)
                elif 'object' in method:
                    return self._object_detection_similarity(data1, data2)
            
            # Text-specific methods
            elif content_type == ContentType.TEXT:
                if 'embedding' in method or 'semantic' in method:
                    return self._semantic_similarity(data1, data2)
                elif 'ngram' in method:
                    return self._ngram_similarity(data1, data2)
                elif 'tfidf' in method:
                    return self._tfidf_similarity(data1, data2)
            
            # Fallback to generic similarity
            return self._generic_similarity(data1, data2)
            
        except Exception as e:
            logger.error(f"Method-specific similarity calculation failed for {method}: {e}")
            return 0.0

    def _chromaprint_similarity(self, data1: Dict, data2: Dict) -> float:
        """Real Chromaprint similarity calculation."""
        try:
            fp1 = data1.get('raw_fingerprint', '')
            fp2 = data2.get('raw_fingerprint', '')
            
            if not fp1 or not fp2:
                return 0.0
            
            # Simplified bit comparison (in production, use acoustid library)
            if len(fp1) != len(fp2):
                min_len = min(len(fp1), len(fp2))
                fp1 = fp1[:min_len]
                fp2 = fp2[:min_len]
            
            matches = sum(c1 == c2 for c1, c2 in zip(fp1, fp2))
            return matches / len(fp1) if fp1 else 0.0
            
        except Exception:
            return 0.0

    def _mfcc_similarity(self, data1: Dict, data2: Dict) -> float:
        """Real MFCC similarity calculation."""
        try:
            mfcc1 = data1.get('coefficients', [])
            mfcc2 = data2.get('coefficients', [])
            
            if not mfcc1 or not mfcc2:
                return 0.0
            
            # Convert to numpy arrays
            arr1 = np.array(mfcc1[:min(len(mfcc1), 13)])  # First 13 coefficients
            arr2 = np.array(mfcc2[:min(len(mfcc2), 13)])
            
            # Ensure same length
            min_len = min(len(arr1), len(arr2))
            arr1 = arr1[:min_len]
            arr2 = arr2[:min_len]
            
            if min_len == 0:
                return 0.0
            
            # Cosine similarity
            dot_product = np.dot(arr1, arr2)
            norm1 = np.linalg.norm(arr1)
            norm2 = np.linalg.norm(arr2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return max(0.0, dot_product / (norm1 * norm2))
            
        except Exception:
            return 0.0

    def _perceptual_hash_similarity(self, data1: Dict, data2: Dict) -> float:
        """Real perceptual hash similarity."""
        try:
            hash1 = data1.get('hash', '') or data1.get('phash', '')
            hash2 = data2.get('hash', '') or data2.get('phash', '')
            
            if not hash1 or not hash2 or len(hash1) != len(hash2):
                return 0.0
            
            # Convert hex to binary and calculate Hamming distance
            try:
                bin1 = bin(int(hash1, 16))[2:].zfill(64)
                bin2 = bin(int(hash2, 16))[2:].zfill(64)
                
                hamming_dist = sum(b1 != b2 for b1, b2 in zip(bin1, bin2))
                return 1.0 - (hamming_dist / 64.0)
                
            except ValueError:
                # Fallback to string comparison
                matches = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
                return matches / len(hash1)
                
        except Exception:
            return 0.0

    def _color_histogram_similarity(self, data1: Dict, data2: Dict) -> float:
        """Real color histogram similarity."""
        try:
            hist1 = data1.get('histogram', []) or data1.get('color_histogram', [])
            hist2 = data2.get('histogram', []) or data2.get('color_histogram', [])
            
            if not hist1 or not hist2:
                return 0.0
            
            # Normalize histograms
            h1 = np.array(hist1)
            h2 = np.array(hist2)
            
            # Ensure same length
            min_len = min(len(h1), len(h2))
            h1 = h1[:min_len]
            h2 = h2[:min_len]
            
            if min_len == 0:
                return 0.0
            
            h1_norm = h1 / np.sum(h1) if np.sum(h1) > 0 else h1
            h2_norm = h2 / np.sum(h2) if np.sum(h2) > 0 else h2
            
            # Chi-squared distance
            chi_squared = np.sum((h1_norm - h2_norm) ** 2 / (h1_norm + h2_norm + 1e-10))
            
            return 1.0 / (1.0 + chi_squared)
            
        except Exception:
            return 0.0

    def _semantic_similarity(self, data1: Dict, data2: Dict) -> float:
        """Real semantic similarity using embeddings."""
        try:
            emb1 = data1.get('embedding', []) or data1.get('semantic_embedding', [])
            emb2 = data2.get('embedding', []) or data2.get('semantic_embedding', [])
            
            if not emb1 or not emb2:
                return 0.0
            
            v1 = np.array(emb1)
            v2 = np.array(emb2)
            
            # Ensure same length
            min_len = min(len(v1), len(v2))
            v1 = v1[:min_len]
            v2 = v2[:min_len]
            
            if min_len == 0:
                return 0.0
            
            # Cosine similarity
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return max(0.0, dot_product / (norm1 * norm2))
            
        except Exception:
            return 0.0

    def _feature_descriptor_similarity(self, data1: Dict, data2: Dict) -> float:
        """Similarity for feature descriptors (SIFT, ORB, etc.)."""
        try:
            # Compare number of features and their distributions
            count1 = data1.get('feature_count', 0) or data1.get('keypoint_count', 0)
            count2 = data2.get('feature_count', 0) or data2.get('keypoint_count', 0)
            
            if count1 == 0 and count2 == 0:
                return 1.0
            elif count1 == 0 or count2 == 0:
                return 0.0
            
            # Feature count similarity
            count_ratio = min(count1, count2) / max(count1, count2)
            
            # Feature quality similarity if available
            quality_sim = 1.0
            if 'average_response' in data1 and 'average_response' in data2:
                resp1 = data1['average_response']
                resp2 = data2['average_response']
                if resp1 > 0 and resp2 > 0:
                    quality_sim = min(resp1, resp2) / max(resp1, resp2)
            
            return (count_ratio + quality_sim) / 2.0
            
        except Exception:
            return 0.0

    def _temporal_similarity(self, data1: Dict, data2: Dict) -> float:
        """Temporal similarity for video content."""
        try:
            # Compare temporal patterns
            pattern1 = data1.get('temporal_pattern', [])
            pattern2 = data2.get('temporal_pattern', [])
            
            if not pattern1 or not pattern2:
                return 0.0
            
            # Normalize patterns to same length
            min_len = min(len(pattern1), len(pattern2))
            p1 = np.array(pattern1[:min_len])
            p2 = np.array(pattern2[:min_len])
            
            if min_len == 0:
                return 0.0
            
            # Correlation coefficient
            correlation = np.corrcoef(p1, p2)[0, 1]
            if np.isnan(correlation):
                return 0.0
            
            return max(0.0, (correlation + 1.0) / 2.0)
            
        except Exception:
            return 0.0

    def _motion_similarity(self, data1: Dict, data2: Dict) -> float:
        """Motion similarity for video content."""
        try:
            motion1 = data1.get('motion_vectors', [])
            motion2 = data2.get('motion_vectors', [])
            
            if not motion1 or not motion2:
                return 0.0
            
            # Compare motion magnitudes
            mag1 = data1.get('average_magnitude', 0)
            mag2 = data2.get('average_magnitude', 0)
            
            if mag1 == 0 and mag2 == 0:
                return 1.0
            elif mag1 == 0 or mag2 == 0:
                return 0.0
            
            magnitude_sim = min(mag1, mag2) / max(mag1, mag2)
            
            # Compare motion directions if available
            dir_sim = 1.0
            if 'dominant_direction' in data1 and 'dominant_direction' in data2:
                dir1 = data1['dominant_direction']
                dir2 = data2['dominant_direction']
                
                # Angular difference in degrees
                angle_diff = abs(dir1 - dir2)
                angle_diff = min(angle_diff, 360 - angle_diff)  # Circular distance
                dir_sim = 1.0 - (angle_diff / 180.0)
            
            return (magnitude_sim + dir_sim) / 2.0
            
        except Exception:
            return 0.0

    def _object_detection_similarity(self, data1: Dict, data2: Dict) -> float:
        """Object detection similarity."""
        try:
            objects1 = set(data1.get('detected_objects', []))
            objects2 = set(data2.get('detected_objects', []))
            
            if not objects1 and not objects2:
                return 1.0
            elif not objects1 or not objects2:
                return 0.0
            
            # Jaccard similarity
            intersection = len(objects1 & objects2)
            union = len(objects1 | objects2)
            
            return intersection / union if union > 0 else 0.0
            
        except Exception:
            return 0.0

    def _ngram_similarity(self, data1: Dict, data2: Dict) -> float:
        """N-gram similarity for text."""
        try:
            ngrams1 = set(data1.get('ngrams', []))
            ngrams2 = set(data2.get('ngrams', []))
            
            if not ngrams1 and not ngrams2:
                return 1.0
            elif not ngrams1 or not ngrams2:
                return 0.0
            
            # Jaccard similarity
            intersection = len(ngrams1 & ngrams2)
            union = len(ngrams1 | ngrams2)
            
            return intersection / union if union > 0 else 0.0
            
        except Exception:
            return 0.0

    def _tfidf_similarity(self, data1: Dict, data2: Dict) -> float:
        """TF-IDF similarity for text."""
        try:
            tfidf1 = data1.get('tfidf_vector', [])
            tfidf2 = data2.get('tfidf_vector', [])
            
            if not tfidf1 or not tfidf2:
                return 0.0
            
            return self._semantic_similarity(
                {'embedding': tfidf1},
                {'embedding': tfidf2}
            )
            
        except Exception:
            return 0.0

    def _spectral_similarity(self, data1: Dict, data2: Dict) -> float:
        """Spectral similarity for audio."""
        try:
            spec1 = data1.get('spectral_hash', '') or data1.get('hash', '')
            spec2 = data2.get('spectral_hash', '') or data2.get('hash', '')
            
            if not spec1 or not spec2:
                return 0.0
            
            # String-based hash comparison
            if len(spec1) != len(spec2):
                min_len = min(len(spec1), len(spec2))
                spec1 = spec1[:min_len]
                spec2 = spec2[:min_len]
            
            if not spec1:
                return 0.0
            
            matches = sum(c1 == c2 for c1, c2 in zip(spec1, spec2))
            return matches / len(spec1)
            
        except Exception:
            return 0.0

    def _generic_similarity(self, data1: Dict, data2: Dict) -> float:
        """Generic similarity fallback."""
        try:
            # Convert data to strings and compare
            str1 = str(data1)
            str2 = str(data2)
            
            if str1 == str2:
                return 1.0
            
            # Simple character-based similarity
            min_len = min(len(str1), len(str2))
            max_len = max(len(str1), len(str2))
            
            if max_len == 0:
                return 0.0
            
            common_chars = sum(1 for c1, c2 in zip(str1, str2) if c1 == c2)
            return common_chars / max_len
            
        except Exception:
            return 0.0
    
    async def batch_add_fingerprints(
        self, 
        fingerprints: List[FingerprintResult]
    ) -> Dict[str, int]:
        """
        Add multiple fingerprints to indices in batch
        
        Args:
            fingerprints: List of fingerprint results to add
        
        Returns:
            Dictionary with success/failure counts
        """
        try:
            results = {'success': 0, 'failed': 0, 'skipped': 0}
            
            # Group by content type for efficient batch processing
            content_groups = {}
            for fp in fingerprints:
                if fp.success:
                    content_type = fp.content_type
                    if content_type not in content_groups:
                        content_groups[content_type] = []
                    content_groups[content_type].append(fp)
                else:
                    results['skipped'] += 1
            
            # Process each content type
            for content_type, fps in content_groups.items():
                batch_results = await self._batch_add_by_type(content_type, fps)
                results['success'] += batch_results['success']
                results['failed'] += batch_results['failed']
            
            logger.info(f"Batch add completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch add: {str(e)}")
            return {'success': 0, 'failed': len(fingerprints), 'skipped': 0}
    
    async def _batch_add_by_type(
        self, 
        content_type: ContentType, 
        fingerprints: List[FingerprintResult]
    ) -> Dict[str, int]:
        """Add batch of fingerprints of same content type"""
        try:
            results = {'success': 0, 'failed': 0}
            
            # Convert all fingerprints to vectors
            vectors = []
            valid_fingerprints = []
            
            for fp in fingerprints:
                vector = await self._fingerprint_to_vector(fp)
                if vector is not None:
                    vectors.append(vector)
                    valid_fingerprints.append(fp)
                else:
                    results['failed'] += 1
            
            if not vectors:
                return results
            
            # Add to index
            if FAISS_AVAILABLE and not isinstance(self.indices[content_type], dict):
                # FAISS batch add
                index = self.indices[content_type]
                start_id = index.ntotal
                
                # Convert to numpy array
                vectors_array = np.array(vectors, dtype=np.float32)
                index.add(vectors_array)
                
                # Update mappings
                for i, fp in enumerate(valid_fingerprints):
                    vector_id = start_id + i
                    self.fingerprint_mappings[content_type][vector_id] = fp
                    results['success'] += 1
                    
            else:
                # Fallback batch add
                index = self.indices[content_type]
                
                for vector, fp in zip(vectors, valid_fingerprints):
                    vector_id = len(index['vectors'])
                    index['vectors'].append(vector)
                    index['fingerprint_ids'].append(fp.request_id)
                    self.fingerprint_mappings[content_type][vector_id] = fp
                    results['success'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch add by type: {str(e)}")
            return {'success': 0, 'failed': len(fingerprints)}
    
    def remove_fingerprint(self, fingerprint_id: str, content_type: ContentType) -> bool:
        """
        Remove fingerprint from index
        Note: FAISS doesn't support efficient removal, so this marks as removed
        """
        try:
            # Find and mark as removed in mapping
            mappings = self.fingerprint_mappings[content_type]
            
            for vector_id, fp in list(mappings.items()):
                if fp.request_id == fingerprint_id:
                    del mappings[vector_id]
                    logger.info(f"Removed fingerprint {fingerprint_id} from index")
                    return True
            
            logger.warning(f"Fingerprint {fingerprint_id} not found in index")
            return False
            
        except Exception as e:
            logger.error(f"Error removing fingerprint: {str(e)}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about all indices"""
        try:
            stats = {
                'engine': 'SimilarityEngine',
                'version': '1.0.0',
                'vector_dimension': self.vector_dimension,
                'use_gpu': self.use_gpu,
                'faiss_available': FAISS_AVAILABLE,
                'similarity_threshold': self.similarity_threshold,
                'indices': {}
            }
            
            for content_type in [ContentType.AUDIO, ContentType.VIDEO, ContentType.IMAGE]:
                if FAISS_AVAILABLE and not isinstance(self.indices[content_type], dict):
                    index = self.indices[content_type]
                    index_size = index.ntotal
                else:
                    index = self.indices[content_type]
                    index_size = len(index['vectors'])
                
                mapping_size = len(self.fingerprint_mappings[content_type])
                
                stats['indices'][content_type.value] = {
                    'size': index_size,
                    'mapped_fingerprints': mapping_size,
                    'index_type': 'FAISS' if FAISS_AVAILABLE else 'fallback'
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {'error': str(e)}
    
    def save_indices(self, directory: Union[str, Path]) -> bool:
        """Save indices to disk"""
        try:
            directory = Path(directory)
            directory.mkdir(parents=True, exist_ok=True)
            
            for content_type in [ContentType.AUDIO, ContentType.VIDEO, ContentType.IMAGE]:
                # Save FAISS index
                if FAISS_AVAILABLE and not isinstance(self.indices[content_type], dict):
                    index_file = directory / f"{content_type.value}_index.faiss"
                    faiss.write_index(self.indices[content_type], str(index_file))
                else:
                    # Save fallback index
                    index_file = directory / f"{content_type.value}_index.pkl"
                    with open(index_file, 'wb') as f:
                        pickle.dump(self.indices[content_type], f)
                
                # Save mappings
                mapping_file = directory / f"{content_type.value}_mappings.pkl"
                with open(mapping_file, 'wb') as f:
                    pickle.dump(self.fingerprint_mappings[content_type], f)
            
            logger.info(f"Saved indices to {directory}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving indices: {str(e)}")
            return False
    
    def load_indices(self, directory: Union[str, Path]) -> bool:
        """Load indices from disk"""
        try:
            directory = Path(directory)
            
            for content_type in [ContentType.AUDIO, ContentType.VIDEO, ContentType.IMAGE]:
                # Load FAISS index
                index_file = directory / f"{content_type.value}_index.faiss"
                fallback_file = directory / f"{content_type.value}_index.pkl"
                
                if FAISS_AVAILABLE and index_file.exists():
                    self.indices[content_type] = faiss.read_index(str(index_file))
                elif fallback_file.exists():
                    with open(fallback_file, 'rb') as f:
                        self.indices[content_type] = pickle.load(f)
                
                # Load mappings
                mapping_file = directory / f"{content_type.value}_mappings.pkl"
                if mapping_file.exists():
                    with open(mapping_file, 'rb') as f:
                        self.fingerprint_mappings[content_type] = pickle.load(f)
            
            logger.info(f"Loaded indices from {directory}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading indices: {str(e)}")
            return False
