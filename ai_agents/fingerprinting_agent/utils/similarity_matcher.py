"""
Similarity Matcher - Advanced Multi-Modal Content Similarity Analysis

Ultra-sophisticated similarity matching system for cross-format content comparison
using advanced ML algorithms, vector similarity, and multi-modal analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import numpy as np
from dataclasses import dataclass
from enum import Enum
import json

# Similarity metrics
from scipy.spatial.distance import cosine, euclidean, hamming
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.preprocessing import StandardScaler
import numpy as np

# Image similarity
from PIL import Image
import imagehash

# Audio similarity
import librosa
from scipy.signal import correlate

# Text similarity
from difflib import SequenceMatcher
import nltk
from nltk.translate.bleu_score import sentence_bleu
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from core.exceptions import SimilarityError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    SimilarityError, ValidationError = globals().get('SimilarityError, ValidationError', Exception)
from ...utils.similarity_utils import SimilarityCalculator

logger = logging.getLogger(__name__)

class SimilarityType(Enum):
    """Types of similarity analysis"""
    EXACT_MATCH = "exact_match"
    NEAR_DUPLICATE = "near_duplicate"
    STRUCTURAL_SIMILAR = "structural_similar"
    SEMANTIC_SIMILAR = "semantic_similar"
    STYLE_SIMILAR = "style_similar"
    PARTIAL_MATCH = "partial_match"

class MatchConfidence(Enum):
    """Confidence levels for similarity matches"""
    VERY_HIGH = "very_high"    # >0.95
    HIGH = "high"              # 0.85-0.95
    MEDIUM = "medium"          # 0.70-0.85
    LOW = "low"                # 0.50-0.70
    VERY_LOW = "very_low"      # <0.50

@dataclass
class SimilarityResult:
    """Comprehensive similarity analysis result"""
    overall_score: float
    confidence: MatchConfidence
    similarity_type: SimilarityType
    detailed_scores: Dict[str, float]
    analysis_details: Dict[str, Any]
    processing_time: float

class SimilarityMatcher:
    """
    Ultra-advanced multi-modal similarity matching system.
    
    Features:
    - Cross-format similarity analysis
    - Multiple similarity algorithms
    - Weighted scoring systems
    - Robustness testing
    - Confidence estimation
    - Detailed analysis reports
    - Performance optimization
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Similarity thresholds
        self.thresholds = {
            'exact_match': self.config.get('exact_threshold', 0.98),
            'near_duplicate': self.config.get('near_duplicate_threshold', 0.90),
            'similar': self.config.get('similar_threshold', 0.75),
            'related': self.config.get('related_threshold', 0.60)
        }
        
        # Algorithm weights for combined scoring
        self.algorithm_weights = {
            'hash_similarity': 0.3,
            'feature_similarity': 0.4,
            'embedding_similarity': 0.3
        }
        
        # Content-specific weights
        self.content_weights = {
            'audio': {'spectral': 0.4, 'temporal': 0.3, 'semantic': 0.3},
            'video': {'visual': 0.4, 'motion': 0.3, 'temporal': 0.3},
            'image': {'perceptual': 0.4, 'structural': 0.3, 'semantic': 0.3},
            'text': {'lexical': 0.3, 'structural': 0.3, 'semantic': 0.4}
        }
        
        # Processing components
        self.scaler = StandardScaler()
        self.similarity_calculator = SimilarityCalculator()
        
        # Performance tracking
        self.performance_metrics = {
            'total_comparisons': 0,
            'processing_times': [],
            'accuracy_scores': []
        }
        
    async def initialize(self):
        """Initialize similarity matching system"""
        try:
            # Initialize similarity calculator
            await self.similarity_calculator.initialize()
            
            logger.info("Similarity matcher initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize similarity matcher: {e}")
            raise SimilarityError(f"Initialization failed: {e}")
    
    async def analyze_similarity(self, 
                               fingerprint1: Dict[str, Any], 
                               fingerprint2: Dict[str, Any],
                               content_type: str) -> Dict[str, Any]:
        """
        Analyze similarity between two fingerprints with comprehensive analysis
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            if not fingerprint1 or not fingerprint2:
                raise ValidationError("Both fingerprints are required")
            
            # Extract similarity scores using multiple algorithms
            similarity_scores = {}
            
            # Hash-based similarity
            if 'hash' in fingerprint1 and 'hash' in fingerprint2:
                hash_similarity = await self._calculate_hash_similarity(
                    fingerprint1['hash'], fingerprint2['hash']
                )
                similarity_scores['hash'] = hash_similarity
            
            # Feature-based similarity
            if 'features' in fingerprint1 and 'features' in fingerprint2:
                feature_similarity = await self._calculate_feature_similarity(
                    fingerprint1['features'], fingerprint2['features'], content_type
                )
                similarity_scores['features'] = feature_similarity
            
            # Embedding-based similarity
            if 'embedding' in fingerprint1 and 'embedding' in fingerprint2:
                embedding_similarity = await self._calculate_embedding_similarity(
                    fingerprint1['embedding'], fingerprint2['embedding']
                )
                similarity_scores['embedding'] = embedding_similarity
            
            # Content-specific similarity analysis
            content_similarity = await self._analyze_content_specific_similarity(
                fingerprint1, fingerprint2, content_type
            )
            similarity_scores.update(content_similarity)
            
            # Calculate overall similarity score
            overall_score = await self._calculate_weighted_score(
                similarity_scores, content_type
            )
            
            # Determine similarity type and confidence
            similarity_type = self._determine_similarity_type(overall_score, similarity_scores)
            confidence = self._calculate_confidence(similarity_scores, overall_score)
            
            # Create detailed analysis
            analysis_details = await self._create_analysis_details(
                fingerprint1, fingerprint2, similarity_scores, content_type
            )
            
            processing_time = time.time() - start_time
            
            # Update performance metrics
            self._update_performance_metrics(processing_time, overall_score)
            
            result = {
                'score': overall_score,
                'confidence': confidence.value,
                'match_type': similarity_type.value,
                'details': {
                    'individual_scores': similarity_scores,
                    'analysis_details': analysis_details,
                    'processing_time': processing_time,
                    'content_type': content_type
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Similarity analysis failed: {e}")
            raise SimilarityError(f"Analysis failed: {e}")
    
    async def _calculate_hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between hash values"""
        try:
            if not hash1 or not hash2:
                return 0.0
            
            if hash1 == hash2:
                return 1.0
            
            # Calculate Hamming distance for hash strings
            if len(hash1) == len(hash2):
                hamming_dist = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
                similarity = 1.0 - (hamming_dist / len(hash1))
            else:
                # Use sequence similarity for different length hashes
                similarity = SequenceMatcher(None, hash1, hash2).ratio()
            
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"Hash similarity calculation failed: {e}")
            return 0.0
    
    async def _calculate_feature_similarity(self, 
                                          features1: Union[List, Dict], 
                                          features2: Union[List, Dict], 
                                          content_type: str) -> Dict[str, float]:
        """Calculate similarity between feature vectors"""
        try:
            feature_similarities = {}
            
            # Handle different feature formats
            if isinstance(features1, list) and isinstance(features2, list):
                # Features as list of feature vectors
                for i, (f1, f2) in enumerate(zip(features1, features2)):
                    if 'vector_data' in f1 and 'vector_data' in f2:
                        vec1 = np.array(f1['vector_data'])
                        vec2 = np.array(f2['vector_data'])
                        
                        if len(vec1) > 0 and len(vec2) > 0:
                            similarity = await self._calculate_vector_similarity(vec1, vec2)
                            feature_type = f1.get('feature_type', f'feature_{i}')
                            feature_similarities[feature_type] = similarity
            
            elif isinstance(features1, dict) and isinstance(features2, dict):
                # Features as dictionary
                common_keys = set(features1.keys()) & set(features2.keys())
                for key in common_keys:
                    vec1 = np.array(features1[key])
                    vec2 = np.array(features2[key])
                    
                    if len(vec1) > 0 and len(vec2) > 0:
                        similarity = await self._calculate_vector_similarity(vec1, vec2)
                        feature_similarities[key] = similarity
            
            # Calculate overall feature similarity
            if feature_similarities:
                overall_feature_sim = np.mean(list(feature_similarities.values()))
                feature_similarities['overall'] = overall_feature_sim
            
            return feature_similarities
            
        except Exception as e:
            logger.error(f"Feature similarity calculation failed: {e}")
            return {}
    
    async def _calculate_embedding_similarity(self, 
                                            embedding1: Union[np.ndarray, List], 
                                            embedding2: Union[np.ndarray, List]) -> float:
        """Calculate similarity between embedding vectors"""
        try:
            # Convert to numpy arrays
            if isinstance(embedding1, list):
                embedding1 = np.array(embedding1)
            if isinstance(embedding2, list):
                embedding2 = np.array(embedding2)
            
            if len(embedding1) == 0 or len(embedding2) == 0:
                return 0.0
            
            # Ensure same dimensions
            min_dim = min(len(embedding1), len(embedding2))
            embedding1 = embedding1[:min_dim]
            embedding2 = embedding2[:min_dim]
            
            return await self._calculate_vector_similarity(embedding1, embedding2)
            
        except Exception as e:
            logger.error(f"Embedding similarity calculation failed: {e}")
            return 0.0
    
    async def _calculate_vector_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate similarity between two vectors using multiple metrics"""
        try:
            if len(vec1) == 0 or len(vec2) == 0:
                return 0.0
            
            # Ensure vectors are same length
            min_len = min(len(vec1), len(vec2))
            vec1 = vec1[:min_len]
            vec2 = vec2[:min_len]
            
            # Multiple similarity metrics
            similarities = []
            
            # Cosine similarity (most important for embeddings)
            cos_sim = 1 - cosine(vec1, vec2) if np.linalg.norm(vec1) > 0 and np.linalg.norm(vec2) > 0 else 0
            similarities.append(cos_sim * 0.5)  # High weight
            
            # Pearson correlation
            try:
                pearson_corr, _ = pearsonr(vec1, vec2)
                if not np.isnan(pearson_corr):
                    similarities.append(abs(pearson_corr) * 0.3)
            except:
                pass
            
            # Euclidean distance based similarity
            eucl_dist = euclidean(vec1, vec2)
            max_dist = np.linalg.norm(vec1) + np.linalg.norm(vec2)
            if max_dist > 0:
                eucl_sim = 1 - (eucl_dist / max_dist)
                similarities.append(eucl_sim * 0.2)
            
            # Return weighted average
            return max(0.0, min(1.0, sum(similarities))) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Vector similarity calculation failed: {e}")
            return 0.0
    
    async def _analyze_content_specific_similarity(self, 
                                                 fingerprint1: Dict[str, Any], 
                                                 fingerprint2: Dict[str, Any], 
                                                 content_type: str) -> Dict[str, float]:
        """Analyze content-specific similarity features"""
        try:
            if content_type == 'audio':
                return await self._analyze_audio_similarity(fingerprint1, fingerprint2)
            elif content_type == 'video':
                return await self._analyze_video_similarity(fingerprint1, fingerprint2)
            elif content_type == 'image':
                return await self._analyze_image_similarity(fingerprint1, fingerprint2)
            elif content_type == 'text':
                return await self._analyze_text_similarity(fingerprint1, fingerprint2)
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Content-specific similarity analysis failed: {e}")
            return {}
    
    async def _analyze_audio_similarity(self, fp1: Dict[str, Any], fp2: Dict[str, Any]) -> Dict[str, float]:
        """Analyze audio-specific similarity features"""
        similarities = {}
        
        try:
            # Chromaprint similarity
            if 'chromaprint' in fp1 and 'chromaprint' in fp2:
                chromaprint_sim = await self._calculate_chromaprint_similarity(
                    fp1['chromaprint'], fp2['chromaprint']
                )
                similarities['chromaprint'] = chromaprint_sim
            
            # Metadata similarity (tempo, key, etc.)
            if 'metadata' in fp1 and 'metadata' in fp2:
                metadata_sim = await self._calculate_audio_metadata_similarity(
                    fp1['metadata'], fp2['metadata']
                )
                similarities['metadata'] = metadata_sim
            
            # Deep embedding similarity (if available)
            if 'deep_embeddings' in fp1 and 'deep_embeddings' in fp2:
                deep_sim = await self._calculate_deep_embedding_similarity(
                    fp1['deep_embeddings'], fp2['deep_embeddings']
                )
                similarities['deep_embeddings'] = deep_sim
            
        except Exception as e:
            logger.error(f"Audio similarity analysis failed: {e}")
        
        return similarities
    
    async def _analyze_video_similarity(self, fp1: Dict[str, Any], fp2: Dict[str, Any]) -> Dict[str, float]:
        """Analyze video-specific similarity features"""
        similarities = {}
        
        try:
            # Frame similarity
            if 'frame_features' in fp1 and 'frame_features' in fp2:
                frame_sim = await self._calculate_frame_similarity(
                    fp1['frame_features'], fp2['frame_features']
                )
                similarities['frames'] = frame_sim
            
            # Motion similarity
            if 'motion_features' in fp1 and 'motion_features' in fp2:
                motion_sim = await self._calculate_motion_similarity(
                    fp1['motion_features'], fp2['motion_features']
                )
                similarities['motion'] = motion_sim
            
            # Audio track similarity (if present)
            if 'audio_track' in fp1 and 'audio_track' in fp2:
                audio_sim = await self._analyze_audio_similarity(
                    fp1['audio_track'], fp2['audio_track']
                )
                similarities.update({f'audio_{k}': v for k, v in audio_sim.items()})
                
        except Exception as e:
            logger.error(f"Video similarity analysis failed: {e}")
        
        return similarities
    
    async def _analyze_image_similarity(self, fp1: Dict[str, Any], fp2: Dict[str, Any]) -> Dict[str, float]:
        """Analyze image-specific similarity features"""
        similarities = {}
        
        try:
            # Perceptual hash similarity
            if 'perceptual_hash' in fp1 and 'perceptual_hash' in fp2:
                phash_sim = await self._calculate_perceptual_hash_similarity(
                    fp1['perceptual_hash'], fp2['perceptual_hash']
                )
                similarities['perceptual_hash'] = phash_sim
            
            # Color histogram similarity
            if 'color_histogram' in fp1 and 'color_histogram' in fp2:
                color_sim = await self._calculate_color_similarity(
                    fp1['color_histogram'], fp2['color_histogram']
                )
                similarities['color'] = color_sim
            
            # Texture features similarity
            if 'texture_features' in fp1 and 'texture_features' in fp2:
                texture_sim = await self._calculate_vector_similarity(
                    np.array(fp1['texture_features']), np.array(fp2['texture_features'])
                )
                similarities['texture'] = texture_sim
                
        except Exception as e:
            logger.error(f"Image similarity analysis failed: {e}")
        
        return similarities
    
    async def _analyze_text_similarity(self, fp1: Dict[str, Any], fp2: Dict[str, Any]) -> Dict[str, float]:
        """Analyze text-specific similarity features"""
        similarities = {}
        
        try:
            # N-gram similarity
            if 'ngram_features' in fp1 and 'ngram_features' in fp2:
                ngram_sim = await self._calculate_ngram_similarity(
                    fp1['ngram_features'], fp2['ngram_features']
                )
                similarities['ngrams'] = ngram_sim
            
            # Semantic embedding similarity
            if 'semantic_embedding' in fp1 and 'semantic_embedding' in fp2:
                semantic_sim = await self._calculate_vector_similarity(
                    np.array(fp1['semantic_embedding']), np.array(fp2['semantic_embedding'])
                )
                similarities['semantic'] = semantic_sim
            
            # TF-IDF similarity
            if 'tfidf_vector' in fp1 and 'tfidf_vector' in fp2:
                tfidf_sim = await self._calculate_vector_similarity(
                    np.array(fp1['tfidf_vector']), np.array(fp2['tfidf_vector'])
                )
                similarities['tfidf'] = tfidf_sim
                
        except Exception as e:
            logger.error(f"Text similarity analysis failed: {e}")
        
        return similarities
    
    async def _calculate_chromaprint_similarity(self, chromaprint1: str, chromaprint2: str) -> float:
        """Calculate similarity between Chromaprint fingerprints"""
        try:
            if not chromaprint1 or not chromaprint2:
                return 0.0
            
            # Convert hex strings to binary for bit-level comparison
            try:
                bytes1 = bytes.fromhex(chromaprint1)
                bytes2 = bytes.fromhex(chromaprint2)
            except ValueError:
                # Fallback to string similarity
                return SequenceMatcher(None, chromaprint1, chromaprint2).ratio()
            
            # Calculate bit-level similarity
            min_len = min(len(bytes1), len(bytes2))
            if min_len == 0:
                return 0.0
            
            # Compare bytes
            matching_bits = 0
            total_bits = min_len * 8
            
            for i in range(min_len):
                byte_xor = bytes1[i] ^ bytes2[i]
                matching_bits += 8 - bin(byte_xor).count('1')
            
            similarity = matching_bits / total_bits
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"Chromaprint similarity calculation failed: {e}")
            return 0.0
    
    async def _calculate_audio_metadata_similarity(self, metadata1: Dict, metadata2: Dict) -> float:
        """Calculate similarity between audio metadata"""
        try:
            similarities = []
            
            # Tempo similarity
            if 'estimated_tempo' in metadata1 and 'estimated_tempo' in metadata2:
                tempo1 = metadata1['estimated_tempo']
                tempo2 = metadata2['estimated_tempo']
                if tempo1 > 0 and tempo2 > 0:
                    tempo_diff = abs(tempo1 - tempo2) / max(tempo1, tempo2)
                    tempo_sim = 1.0 - min(tempo_diff, 1.0)
                    similarities.append(tempo_sim * 0.3)
            
            # Duration similarity
            if 'duration' in metadata1 and 'duration' in metadata2:
                dur1 = metadata1['duration']
                dur2 = metadata2['duration']
                if dur1 > 0 and dur2 > 0:
                    dur_diff = abs(dur1 - dur2) / max(dur1, dur2)
                    dur_sim = 1.0 - min(dur_diff, 1.0)
                    similarities.append(dur_sim * 0.2)
            
            # Harmonic/percussive ratio similarity
            if 'harmonic_ratio' in metadata1 and 'harmonic_ratio' in metadata2:
                harm1 = metadata1['harmonic_ratio']
                harm2 = metadata2['harmonic_ratio']
                harm_diff = abs(harm1 - harm2)
                harm_sim = 1.0 - min(harm_diff, 1.0)
                similarities.append(harm_sim * 0.2)
            
            # Spectral characteristics similarity
            spectral_features = ['spectral_centroid_mean', 'spectral_bandwidth', 'spectral_rolloff']
            for feature in spectral_features:
                if feature in metadata1 and feature in metadata2:
                    val1 = metadata1[feature]
                    val2 = metadata2[feature]
                    if val1 > 0 and val2 > 0:
                        diff = abs(val1 - val2) / max(val1, val2)
                        sim = 1.0 - min(diff, 1.0)
                        similarities.append(sim * 0.1)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Audio metadata similarity calculation failed: {e}")
            return 0.0
    
    async def _calculate_deep_embedding_similarity(self, embeddings1: Dict, embeddings2: Dict) -> float:
        """Calculate similarity between deep learning embeddings"""
        try:
            similarities = []
            
            # Compare embeddings from same models
            common_models = set(embeddings1.keys()) & set(embeddings2.keys())
            
            for model in common_models:
                emb1 = embeddings1[model]
                emb2 = embeddings2[model]
                
                if isinstance(emb1, list):
                    emb1 = np.array(emb1)
                if isinstance(emb2, list):
                    emb2 = np.array(emb2)
                
                if len(emb1) > 0 and len(emb2) > 0:
                    similarity = await self._calculate_vector_similarity(emb1, emb2)
                    similarities.append(similarity)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Deep embedding similarity calculation failed: {e}")
            return 0.0
    
    async def _calculate_weighted_score(self, similarity_scores: Dict[str, Any], content_type: str) -> float:
        """Calculate weighted overall similarity score"""
        try:
            if not similarity_scores:
                return 0.0
            
            # Get content-specific weights
            content_weights = self.content_weights.get(content_type, {})
            
            weighted_scores = []
            total_weight = 0.0
            
            for score_type, score_value in similarity_scores.items():
                # Handle nested score dictionaries
                if isinstance(score_value, dict):
                    if 'overall' in score_value:
                        score = score_value['overall']
                    else:
                        score = np.mean(list(score_value.values()))
                else:
                    score = score_value
                
                # Apply weights
                weight = content_weights.get(score_type, 1.0)
                weighted_scores.append(score * weight)
                total_weight += weight
            
            # Calculate weighted average
            if total_weight > 0:
                overall_score = sum(weighted_scores) / total_weight
            else:
                overall_score = np.mean(weighted_scores) if weighted_scores else 0.0
            
            return max(0.0, min(1.0, overall_score))
            
        except Exception as e:
            logger.error(f"Weighted score calculation failed: {e}")
            return 0.0
    
    def _determine_similarity_type(self, overall_score: float, similarity_scores: Dict) -> SimilarityType:
        """Determine the type of similarity based on scores"""
        try:
            if overall_score >= self.thresholds['exact_match']:
                return SimilarityType.EXACT_MATCH
            elif overall_score >= self.thresholds['near_duplicate']:
                return SimilarityType.NEAR_DUPLICATE
            elif overall_score >= self.thresholds['similar']:
                # Check if it's structural or semantic similarity
                if 'embedding' in similarity_scores and similarity_scores['embedding'] > 0.8:
                    return SimilarityType.SEMANTIC_SIMILAR
                else:
                    return SimilarityType.STRUCTURAL_SIMILAR
            elif overall_score >= self.thresholds['related']:
                return SimilarityType.PARTIAL_MATCH
            else:
                return SimilarityType.PARTIAL_MATCH  # Or could be "no_match"
                
        except Exception as e:
            logger.error(f"Similarity type determination failed: {e}")
            return SimilarityType.PARTIAL_MATCH
    
    def _calculate_confidence(self, similarity_scores: Dict, overall_score: float) -> MatchConfidence:
        """Calculate confidence level for the similarity match"""
        try:
            # Factors that affect confidence:
            # 1. Number of different similarity metrics agreeing
            # 2. Variance in similarity scores
            # 3. Overall score level
            
            score_values = []
            for value in similarity_scores.values():
                if isinstance(value, dict):
                    score_values.extend([v for v in value.values() if isinstance(v, (int, float))])
                elif isinstance(value, (int, float)):
                    score_values.append(value)
            
            if not score_values:
                return MatchConfidence.VERY_LOW
            
            # Calculate variance - lower variance = higher confidence
            variance = np.var(score_values)
            variance_score = max(0, 1 - variance * 4)  # Penalize high variance
            
            # Number of metrics - more metrics = higher confidence
            metric_count = len([s for s in score_values if s > 0.1])  # Only count meaningful scores
            metric_score = min(metric_count / 5.0, 1.0)  # Normalize to 0-1
            
            # Overall score contribution
            score_contribution = overall_score
            
            # Combined confidence
            confidence_score = (variance_score * 0.4 + metric_score * 0.3 + score_contribution * 0.3)
            
            # Map to confidence levels
            if confidence_score >= 0.9:
                return MatchConfidence.VERY_HIGH
            elif confidence_score >= 0.75:
                return MatchConfidence.HIGH
            elif confidence_score >= 0.6:
                return MatchConfidence.MEDIUM
            elif confidence_score >= 0.4:
                return MatchConfidence.LOW
            else:
                return MatchConfidence.VERY_LOW
                
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return MatchConfidence.LOW
    
    async def _create_analysis_details(self, 
                                     fingerprint1: Dict, 
                                     fingerprint2: Dict, 
                                     similarity_scores: Dict, 
                                     content_type: str) -> Dict[str, Any]:
        """Create detailed analysis report"""
        try:
            details = {
                'content_type': content_type,
                'algorithms_used': list(similarity_scores.keys()),
                'score_breakdown': similarity_scores,
                'thresholds_applied': self.thresholds,
                'weights_used': self.content_weights.get(content_type, {}),
                'metadata_comparison': {}
            }
            
            # Add metadata comparison if available
            if 'metadata' in fingerprint1 and 'metadata' in fingerprint2:
                meta1 = fingerprint1['metadata']
                meta2 = fingerprint2['metadata']
                
                details['metadata_comparison'] = {
                    'fingerprint1_metadata': {k: v for k, v in meta1.items() if isinstance(v, (str, int, float))},
                    'fingerprint2_metadata': {k: v for k, v in meta2.items() if isinstance(v, (str, int, float))},
                    'common_attributes': list(set(meta1.keys()) & set(meta2.keys())),
                    'unique_to_fp1': list(set(meta1.keys()) - set(meta2.keys())),
                    'unique_to_fp2': list(set(meta2.keys()) - set(meta1.keys()))
                }
            
            # Add quality assessment
            details['quality_assessment'] = {
                'score_consistency': np.std(list(similarity_scores.values())) if similarity_scores else 0,
                'algorithm_agreement': self._calculate_algorithm_agreement(similarity_scores),
                'reliability_indicators': self._get_reliability_indicators(similarity_scores)
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Analysis details creation failed: {e}")
            return {'error': str(e)}
    
    def _calculate_algorithm_agreement(self, similarity_scores: Dict) -> float:
        """Calculate how much different algorithms agree"""
        try:
            scores = []
            for value in similarity_scores.values():
                if isinstance(value, dict):
                    scores.extend([v for v in value.values() if isinstance(v, (int, float))])
                elif isinstance(value, (int, float)):
                    scores.append(value)
            
            if len(scores) < 2:
                return 1.0  # Perfect agreement if only one score
            
            # Calculate pairwise agreement
            agreements = []
            for i in range(len(scores)):
                for j in range(i + 1, len(scores)):
                    agreement = 1.0 - abs(scores[i] - scores[j])
                    agreements.append(agreement)
            
            return np.mean(agreements) if agreements else 1.0
            
        except Exception as e:
            logger.error(f"Algorithm agreement calculation failed: {e}")
            return 0.5
    
    def _get_reliability_indicators(self, similarity_scores: Dict) -> Dict[str, Any]:
        """Get indicators of match reliability"""
        try:
            indicators = {
                'multiple_algorithms': len(similarity_scores) > 2,
                'consistent_scores': np.std(list(similarity_scores.values())) < 0.2,
                'high_confidence_algorithms': sum(1 for s in similarity_scores.values() if s > 0.8),
                'cross_modal_agreement': 'hash' in similarity_scores and 'embedding' in similarity_scores
            }
            
            # Overall reliability score
            reliability_score = sum([
                indicators['multiple_algorithms'] * 0.3,
                indicators['consistent_scores'] * 0.3,
                (indicators['high_confidence_algorithms'] / len(similarity_scores)) * 0.2,
                indicators['cross_modal_agreement'] * 0.2
            ])
            
            indicators['overall_reliability'] = min(reliability_score, 1.0)
            
            return indicators
            
        except Exception as e:
            logger.error(f"Reliability indicators calculation failed: {e}")
            return {'overall_reliability': 0.5}
    
    def _update_performance_metrics(self, processing_time: float, accuracy_score: float):
        """Update internal performance metrics"""
        self.performance_metrics['total_comparisons'] += 1
        self.performance_metrics['processing_times'].append(processing_time)
        self.performance_metrics['accuracy_scores'].append(accuracy_score)
        
        # Keep only recent metrics to manage memory
        max_history = 1000
        if len(self.performance_metrics['processing_times']) > max_history:
            self.performance_metrics['processing_times'] = self.performance_metrics['processing_times'][-max_history:]
        if len(self.performance_metrics['accuracy_scores']) > max_history:
            self.performance_metrics['accuracy_scores'] = self.performance_metrics['accuracy_scores'][-max_history:]
    
    async def batch_similarity_analysis(self, 
                                      query_fingerprint: Dict[str, Any],
                                      candidate_fingerprints: List[Dict[str, Any]],
                                      content_type: str,
                                      threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Perform batch similarity analysis against multiple candidates"""
        try:
            results = []
            
            # Process candidates concurrently
            tasks = []
            for i, candidate in enumerate(candidate_fingerprints):
                task = self.analyze_similarity(query_fingerprint, candidate, content_type)
                tasks.append((i, task))
            
            # Execute with concurrency limit
            semaphore = asyncio.Semaphore(10)  # Limit concurrent operations
            
            async def process_with_semaphore(idx, task):
                async with semaphore:
                    result = await task
                    result['candidate_index'] = idx
                    return result
            
            batch_results = await asyncio.gather(*[
                process_with_semaphore(idx, task) for idx, task in tasks
            ], return_exceptions=True)
            
            # Filter and sort results
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch similarity analysis error: {result}")
                    continue
                
                if result['score'] >= threshold:
                    results.append(result)
            
            # Sort by similarity score (descending)
            results.sort(key=lambda x: x['score'], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Batch similarity analysis failed: {e}")
            return []
    
    async def get_performance_statistics(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        try:
            metrics = self.performance_metrics
            
            stats = {
                'total_comparisons': metrics['total_comparisons'],
                'average_processing_time': np.mean(metrics['processing_times']) if metrics['processing_times'] else 0,
                'processing_time_std': np.std(metrics['processing_times']) if metrics['processing_times'] else 0,
                'average_accuracy': np.mean(metrics['accuracy_scores']) if metrics['accuracy_scores'] else 0,
                'accuracy_std': np.std(metrics['accuracy_scores']) if metrics['accuracy_scores'] else 0,
                'throughput': len(metrics['processing_times']) / sum(metrics['processing_times']) if metrics['processing_times'] else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Performance statistics calculation failed: {e}")
            return {}
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            # Clear performance metrics
            self.performance_metrics = {
                'total_comparisons': 0,
                'processing_times': [],
                'accuracy_scores': []
            }
            
            # Cleanup similarity calculator
            if hasattr(self, 'similarity_calculator'):
                await self.similarity_calculator.cleanup()
            
            logger.info("SimilarityMatcher cleanup completed")
            
        except Exception as e:
            logger.error(f"SimilarityMatcher cleanup failed: {e}")
    
    # Additional helper methods for specific similarity calculations
    
    async def _calculate_frame_similarity(self, frames1: List, frames2: List) -> float:
        """Calculate similarity between video frame sequences"""
        # Implementation for video frame comparison
        # This would involve comparing frame features, optical flow, etc.
        return 0.5  # Placeholder
    
    async def _calculate_motion_similarity(self, motion1: Dict, motion2: Dict) -> float:
        """Calculate similarity between motion features"""
        # Implementation for motion vector comparison
        return 0.5  # Placeholder
    
    async def _calculate_perceptual_hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between perceptual hashes"""
        try:
            # Convert hex strings to integers and calculate Hamming distance
            h1 = int(hash1, 16)
            h2 = int(hash2, 16)
            
            # XOR to find different bits
            xor_result = h1 ^ h2
            
            # Count different bits
            different_bits = bin(xor_result).count('1')
            
            # Calculate similarity (assuming 64-bit hash)
            total_bits = 64
            similarity = 1.0 - (different_bits / total_bits)
            
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"Perceptual hash similarity calculation failed: {e}")
            return 0.0
    
    async def _calculate_color_similarity(self, hist1: List, hist2: List) -> float:
        """Calculate similarity between color histograms"""
        try:
            h1 = np.array(hist1)
            h2 = np.array(hist2)
            
            # Use histogram intersection
            intersection = np.sum(np.minimum(h1, h2))
            union = np.sum(np.maximum(h1, h2))
            
            if union > 0:
                return intersection / union
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Color similarity calculation failed: {e}")
            return 0.0
    
    async def _calculate_ngram_similarity(self, ngrams1: Dict, ngrams2: Dict) -> float:
        """Calculate similarity between n-gram features"""
        try:
            # Calculate Jaccard similarity for n-grams
            set1 = set(ngrams1.keys())
            set2 = set(ngrams2.keys())
            
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            
            if union > 0:
                return intersection / union
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"N-gram similarity calculation failed: {e}")
            return 0.0
            # Validate inputs
            await self._validate_fingerprints(fingerprint1, fingerprint2, content_type)
            
            # Perform multi-level similarity analysis
            similarity_scores = {}
            
            # Hash-based similarity
            if 'hash' in fingerprint1 and 'hash' in fingerprint2:
                hash_similarity = await self._calculate_hash_similarity(
                    fingerprint1['hash'], fingerprint2['hash'], content_type
                )
                similarity_scores['hash_similarity'] = hash_similarity
            
            # Feature-based similarity
            if 'features' in fingerprint1 and 'features' in fingerprint2:
                feature_similarity = await self._calculate_feature_similarity(
                    fingerprint1['features'], fingerprint2['features'], content_type
                )
                similarity_scores['feature_similarity'] = feature_similarity
            
            # Embedding-based similarity
            if 'embedding' in fingerprint1 and 'embedding' in fingerprint2:
                embedding_similarity = await self._calculate_embedding_similarity(
                    fingerprint1['embedding'], fingerprint2['embedding'], content_type
                )
                similarity_scores['embedding_similarity'] = embedding_similarity
            
            # Content-specific analysis
            content_specific_scores = await self._analyze_content_specific(
                fingerprint1, fingerprint2, content_type
            )
            similarity_scores.update(content_specific_scores)
            
            # Calculate weighted overall score
            overall_score = await self._calculate_weighted_score(similarity_scores, content_type)
            
            # Determine similarity type and confidence
            similarity_type = await self._determine_similarity_type(overall_score, similarity_scores)
            confidence = await self._calculate_confidence(similarity_scores, content_type)
            
            # Generate detailed analysis
            analysis_details = await self._generate_analysis_details(
                similarity_scores, fingerprint1, fingerprint2, content_type
            )
            
            processing_time = time.time() - start_time
            
            # Update performance metrics
            self.performance_metrics['total_comparisons'] += 1
            self.performance_metrics['processing_times'].append(processing_time)
            
            result = {
                'score': overall_score,
                'confidence': confidence.value,
                'match_type': similarity_type.value,
                'details': similarity_scores,
                'analysis': analysis_details,
                'processing_time': processing_time
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Similarity analysis failed: {e}")
            raise SimilarityError(f"Similarity analysis failed: {e}")
    
    async def _calculate_hash_similarity(self, hash1: str, hash2: str, content_type: str) -> Dict[str, float]:
        """Calculate hash-based similarity"""
        try:
            scores = {}
            
            if content_type == 'audio':
                # Audio hash comparison
                scores['exact_match'] = 1.0 if hash1 == hash2 else 0.0
                
                # Hamming distance for perceptual hashes
                if len(hash1) == len(hash2):
                    hamming_dist = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
                    hamming_similarity = 1.0 - (hamming_dist / len(hash1))
                    scores['perceptual_hash'] = hamming_similarity
                else:
                    scores['perceptual_hash'] = 0.0
                    
            elif content_type == 'video':
                # Video hash comparison
                scores['exact_match'] = 1.0 if hash1 == hash2 else 0.0
                
                # Parse combined hash if available
                if '_' in hash1 and '_' in hash2:
                    hash1_parts = hash1.split('_')
                    hash2_parts = hash2.split('_')
                    
                    if len(hash1_parts) == len(hash2_parts):
                        part_similarities = []
                        for p1, p2 in zip(hash1_parts, hash2_parts):
                            if len(p1) == len(p2):
                                hamming_dist = sum(c1 != c2 for c1, c2 in zip(p1, p2))
                                similarity = 1.0 - (hamming_dist / len(p1))
                                part_similarities.append(similarity)
                        
                        if part_similarities:
                            scores['perceptual_hash'] = np.mean(part_similarities)
                        else:
                            scores['perceptual_hash'] = 0.0
                    else:
                        scores['perceptual_hash'] = 0.0
                else:
                    scores['perceptual_hash'] = 0.0
                    
            elif content_type == 'image':
                # Image hash comparison using imagehash
                scores['exact_match'] = 1.0 if hash1 == hash2 else 0.0
                
                # Parse multi-hash format
                if '_' in hash1 and '_' in hash2:
                    hash1_parts = hash1.split('_')
                    hash2_parts = hash2.split('_')
                    
                    hash_similarities = []
                    for p1, p2 in zip(hash1_parts, hash2_parts):
                        try:
                            # Convert hex to binary and calculate Hamming distance
                            if len(p1) == len(p2):
                                bin1 = bin(int(p1, 16))[2:].zfill(len(p1) * 4)
                                bin2 = bin(int(p2, 16))[2:].zfill(len(p2) * 4)
                                hamming_dist = sum(c1 != c2 for c1, c2 in zip(bin1, bin2))
                                similarity = 1.0 - (hamming_dist / len(bin1))
                                hash_similarities.append(similarity)
                        except:
                            hash_similarities.append(0.0)
                    
                    if hash_similarities:
                        scores['perceptual_hash'] = np.mean(hash_similarities)
                    else:
                        scores['perceptual_hash'] = 0.0
                else:
                    scores['perceptual_hash'] = 0.0
                    
            elif content_type == 'text':
                # Text hash comparison
                scores['exact_match'] = 1.0 if hash1 == hash2 else 0.0
                
                # For text, we might have multiple hashes
                if isinstance(hash1, dict) and isinstance(hash2, dict):
                    hash_scores = {}
                    for key in hash1.keys():
                        if key in hash2:
                            hash_scores[key] = 1.0 if hash1[key] == hash2[key] else 0.0
                    scores.update(hash_scores)
                else:
                    scores['content_hash'] = 1.0 if hash1 == hash2 else 0.0
            
            return scores
            
        except Exception as e:
            logger.error(f"Hash similarity calculation failed: {e}")
            return {'exact_match': 0.0, 'perceptual_hash': 0.0}
    
    async def _calculate_feature_similarity(self, features1: np.ndarray, features2: np.ndarray, 
                                          content_type: str) -> Dict[str, float]:
        """Calculate feature-based similarity using multiple metrics"""
        try:
            scores = {}
            
            # Ensure features are numpy arrays
            if not isinstance(features1, np.ndarray):
                features1 = np.array(features1)
            if not isinstance(features2, np.ndarray):
                features2 = np.array(features2)
            
            # Handle different feature lengths
            min_length = min(len(features1), len(features2))
            if min_length == 0:
                return {'cosine': 0.0, 'euclidean': 0.0, 'correlation': 0.0}
            
            features1 = features1[:min_length]
            features2 = features2[:min_length]
            
            # Cosine similarity
            try:
                if np.linalg.norm(features1) > 0 and np.linalg.norm(features2) > 0:
                    cosine_sim = 1 - cosine(features1, features2)
                    scores['cosine'] = max(0, cosine_sim)  # Ensure non-negative
                else:
                    scores['cosine'] = 0.0
            except:
                scores['cosine'] = 0.0
            
            # Euclidean similarity (normalized)
            try:
                euclidean_dist = euclidean(features1, features2)
                max_dist = np.sqrt(len(features1)) * 256  # Assuming normalized features
                euclidean_sim = 1.0 - (euclidean_dist / max_dist)
                scores['euclidean'] = max(0, euclidean_sim)
            except:
                scores['euclidean'] = 0.0
            
            # Pearson correlation
            try:
                correlation, _ = pearsonr(features1, features2)
                scores['correlation'] = max(0, correlation) if not np.isnan(correlation) else 0.0
            except:
                scores['correlation'] = 0.0
            
            # Manhattan similarity
            try:
                manhattan_dist = np.sum(np.abs(features1 - features2))
                max_manhattan = len(features1) * 256
                manhattan_sim = 1.0 - (manhattan_dist / max_manhattan)
                scores['manhattan'] = max(0, manhattan_sim)
            except:
                scores['manhattan'] = 0.0
            
            # Content-specific feature analysis
            if content_type == 'audio':
                # Audio-specific feature comparison
                scores['spectral_similarity'] = await self._analyze_audio_features(features1, features2)
            elif content_type == 'image':
                # Image-specific feature comparison
                scores['visual_similarity'] = await self._analyze_image_features(features1, features2)
            elif content_type == 'text':
                # Text-specific feature comparison
                scores['linguistic_similarity'] = await self._analyze_text_features(features1, features2)
            
            return scores
            
        except Exception as e:
            logger.error(f"Feature similarity calculation failed: {e}")
            return {'cosine': 0.0, 'euclidean': 0.0, 'correlation': 0.0}
    
    async def _calculate_embedding_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray,
                                            content_type: str) -> Dict[str, float]:
        """Calculate embedding-based similarity"""
        try:
            scores = {}
            
            # Ensure embeddings are numpy arrays
            if not isinstance(embedding1, np.ndarray):
                embedding1 = np.array(embedding1)
            if not isinstance(embedding2, np.ndarray):
                embedding2 = np.array(embedding2)
            
            # Handle different embedding sizes
            min_length = min(len(embedding1), len(embedding2))
            if min_length == 0:
                return {'semantic_similarity': 0.0}
            
            embedding1 = embedding1[:min_length]
            embedding2 = embedding2[:min_length]
            
            # Cosine similarity for semantic comparison
            try:
                if np.linalg.norm(embedding1) > 0 and np.linalg.norm(embedding2) > 0:
                    semantic_sim = 1 - cosine(embedding1, embedding2)
                    scores['semantic_similarity'] = max(0, semantic_sim)
                else:
                    scores['semantic_similarity'] = 0.0
            except:
                scores['semantic_similarity'] = 0.0
            
            # Dot product similarity
            try:
                dot_product = np.dot(embedding1, embedding2)
                norm_product = np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
                if norm_product > 0:
                    dot_similarity = dot_product / norm_product
                    scores['dot_similarity'] = max(0, dot_similarity)
                else:
                    scores['dot_similarity'] = 0.0
            except:
                scores['dot_similarity'] = 0.0
            
            # L2 normalized similarity
            try:
                l2_norm1 = embedding1 / np.linalg.norm(embedding1) if np.linalg.norm(embedding1) > 0 else embedding1
                l2_norm2 = embedding2 / np.linalg.norm(embedding2) if np.linalg.norm(embedding2) > 0 else embedding2
                l2_similarity = np.dot(l2_norm1, l2_norm2)
                scores['l2_normalized'] = max(0, l2_similarity)
            except:
                scores['l2_normalized'] = 0.0
            
            return scores
            
        except Exception as e:
            logger.error(f"Embedding similarity calculation failed: {e}")
            return {'semantic_similarity': 0.0}
    
    async def _analyze_content_specific(self, fingerprint1: Dict[str, Any], 
                                      fingerprint2: Dict[str, Any], content_type: str) -> Dict[str, float]:
        """Perform content-specific similarity analysis"""
        try:
            scores = {}
            
            if content_type == 'audio':
                scores.update(await self._analyze_audio_similarity(fingerprint1, fingerprint2))
            elif content_type == 'video':
                scores.update(await self._analyze_video_similarity(fingerprint1, fingerprint2))
            elif content_type == 'image':
                scores.update(await self._analyze_image_similarity(fingerprint1, fingerprint2))
            elif content_type == 'text':
                scores.update(await self._analyze_text_similarity(fingerprint1, fingerprint2))
            
            return scores
            
        except Exception as e:
            logger.error(f"Content-specific analysis failed: {e}")
            return {}
    
    async def _calculate_weighted_score(self, similarity_scores: Dict[str, Any], content_type: str) -> float:
        """Calculate weighted overall similarity score"""
        try:
            weighted_score = 0.0
            total_weight = 0.0
            
            # Primary algorithm weights
            for algorithm, weight in self.algorithm_weights.items():
                if algorithm in similarity_scores:
                    if isinstance(similarity_scores[algorithm], dict):
                        # Average sub-scores
                        sub_score = np.mean(list(similarity_scores[algorithm].values()))
                    else:
                        sub_score = similarity_scores[algorithm]
                    
                    weighted_score += sub_score * weight
                    total_weight += weight
            
            # Content-specific weights
            if content_type in self.content_weights:
                content_specific_weights = self.content_weights[content_type]
                for aspect, weight in content_specific_weights.items():
                    aspect_key = f"{aspect}_similarity"
                    if aspect_key in similarity_scores:
                        if isinstance(similarity_scores[aspect_key], dict):
                            sub_score = np.mean(list(similarity_scores[aspect_key].values()))
                        else:
                            sub_score = similarity_scores[aspect_key]
                        
                        weighted_score += sub_score * weight * 0.5  # Reduced weight for content-specific
                        total_weight += weight * 0.5
            
            # Normalize by total weight
            if total_weight > 0:
                final_score = weighted_score / total_weight
            else:
                # Fallback: simple average
                all_scores = []
                for score in similarity_scores.values():
                    if isinstance(score, dict):
                        all_scores.extend(list(score.values()))
                    else:
                        all_scores.append(score)
                
                final_score = np.mean(all_scores) if all_scores else 0.0
            
            return min(1.0, max(0.0, final_score))  # Clamp to [0, 1]
            
        except Exception as e:
            logger.error(f"Weighted score calculation failed: {e}")
            return 0.0
    
    async def _determine_similarity_type(self, overall_score: float, 
                                       similarity_scores: Dict[str, Any]) -> SimilarityType:
        """Determine the type of similarity based on scores"""
        try:
            # Check for exact match
            if overall_score >= self.thresholds['exact_match']:
                return SimilarityType.EXACT_MATCH
            
            # Check for near duplicate
            elif overall_score >= self.thresholds['near_duplicate']:
                return SimilarityType.NEAR_DUPLICATE
            
            # Check for structural similarity
            elif overall_score >= self.thresholds['similar']:
                # Look for high feature similarity
                feature_scores = similarity_scores.get('feature_similarity', {})
                if isinstance(feature_scores, dict):
                    avg_feature_score = np.mean(list(feature_scores.values()))
                    if avg_feature_score >= 0.8:
                        return SimilarityType.STRUCTURAL_SIMILAR
                
                # Look for high semantic similarity
                embedding_scores = similarity_scores.get('embedding_similarity', {})
                if isinstance(embedding_scores, dict):
                    semantic_score = embedding_scores.get('semantic_similarity', 0)
                    if semantic_score >= 0.8:
                        return SimilarityType.SEMANTIC_SIMILAR
                
                return SimilarityType.STYLE_SIMILAR
            
            # Check for partial match
            elif overall_score >= self.thresholds['related']:
                return SimilarityType.PARTIAL_MATCH
            
            else:
                return SimilarityType.PARTIAL_MATCH  # Default for low scores
                
        except Exception as e:
            logger.error(f"Similarity type determination failed: {e}")
            return SimilarityType.PARTIAL_MATCH
    
    async def _calculate_confidence(self, similarity_scores: Dict[str, Any], 
                                  content_type: str) -> MatchConfidence:
        """Calculate confidence level for similarity match"""
        try:
            # Calculate confidence based on score consistency
            all_scores = []
            for score in similarity_scores.values():
                if isinstance(score, dict):
                    all_scores.extend(list(score.values()))
                else:
                    all_scores.append(score)
            
            if not all_scores:
                return MatchConfidence.VERY_LOW
            
            # Mean and standard deviation of scores
            mean_score = np.mean(all_scores)
            std_score = np.std(all_scores)
            
            # Confidence based on mean score and consistency
            consistency_factor = 1.0 / (1.0 + std_score)  # Lower std = higher consistency
            confidence_score = mean_score * consistency_factor
            
            # Map to confidence levels
            if confidence_score >= 0.90:
                return MatchConfidence.VERY_HIGH
            elif confidence_score >= 0.75:
                return MatchConfidence.HIGH
            elif confidence_score >= 0.60:
                return MatchConfidence.MEDIUM
            elif confidence_score >= 0.40:
                return MatchConfidence.LOW
            else:
                return MatchConfidence.VERY_LOW
                
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return MatchConfidence.VERY_LOW
    
    async def _generate_analysis_details(self, similarity_scores: Dict[str, Any],
                                       fingerprint1: Dict[str, Any], fingerprint2: Dict[str, Any],
                                       content_type: str) -> Dict[str, Any]:
        """Generate detailed analysis report"""
        try:
            analysis = {
                'content_type': content_type,
                'algorithm_breakdown': {},
                'quality_assessment': {},
                'recommendations': []
            }
            
            # Algorithm performance breakdown
            for algorithm, scores in similarity_scores.items():
                if isinstance(scores, dict):
                    analysis['algorithm_breakdown'][algorithm] = {
                        'scores': scores,
                        'average': np.mean(list(scores.values())),
                        'max': np.max(list(scores.values())),
                        'min': np.min(list(scores.values()))
                    }
                else:
                    analysis['algorithm_breakdown'][algorithm] = {
                        'score': scores,
                        'performance': 'high' if scores > 0.8 else 'medium' if scores > 0.5 else 'low'
                    }
            
            # Quality assessment
            quality1 = fingerprint1.get('quality', {})
            quality2 = fingerprint2.get('quality', {})
            
            analysis['quality_assessment'] = {
                'fingerprint1_quality': quality1.get('overall_quality', 0),
                'fingerprint2_quality': quality2.get('overall_quality', 0),
                'quality_impact': 'high' if min(quality1.get('overall_quality', 0), 
                                              quality2.get('overall_quality', 0)) > 0.8 else 'medium'
            }
            
            # Generate recommendations
            analysis['recommendations'] = await self._generate_recommendations(similarity_scores, content_type)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis details generation failed: {e}")
            return {'error': str(e)}
    
    async def _generate_recommendations(self, similarity_scores: Dict[str, Any], 
                                      content_type: str) -> List[str]:
        """Generate recommendations based on similarity analysis"""
        recommendations = []
        
        try:
            # Get overall performance
            all_scores = []
            for score in similarity_scores.values():
                if isinstance(score, dict):
                    all_scores.extend(list(score.values()))
                else:
                    all_scores.append(score)
            
            avg_score = np.mean(all_scores) if all_scores else 0
            
            if avg_score < 0.3:
                recommendations.append("Content appears to be significantly different")
                recommendations.append("Consider using alternative matching algorithms")
            elif avg_score < 0.6:
                recommendations.append("Moderate similarity detected - manual review recommended")
                recommendations.append("Check for partial matches or derived content")
            elif avg_score < 0.9:
                recommendations.append("High similarity detected - likely related content")
                recommendations.append("Consider investigation for potential copyright issues")
            else:
                recommendations.append("Very high similarity - possible duplicate or near-duplicate")
                recommendations.append("Strong evidence of content matching")
            
            # Content-specific recommendations
            if content_type == 'audio':
                if 'spectral_similarity' in similarity_scores:
                    spectral_score = similarity_scores['spectral_similarity']
                    if isinstance(spectral_score, dict):
                        spectral_score = np.mean(list(spectral_score.values()))
                    if spectral_score > 0.8:
                        recommendations.append("High spectral similarity suggests same audio source")
            
            elif content_type == 'image':
                if 'perceptual_hash' in similarity_scores:
                    perceptual_score = similarity_scores['perceptual_hash']
                    if isinstance(perceptual_score, dict):
                        perceptual_score = np.mean(list(perceptual_score.values()))
                    if perceptual_score > 0.9:
                        recommendations.append("High perceptual similarity - likely same or modified image")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Analysis completed with limited recommendations due to processing error"]
    
    # Content-specific analysis methods (simplified implementations)
    async def _analyze_audio_features(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Analyze audio-specific features"""
        try:
            # Simplified audio feature analysis
            return 1 - cosine(features1, features2) if len(features1) == len(features2) else 0.0
        except:
            return 0.0
    
    async def _analyze_image_features(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Analyze image-specific features"""
        try:
            # Simplified image feature analysis
            return 1 - cosine(features1, features2) if len(features1) == len(features2) else 0.0
        except:
            return 0.0
    
    async def _analyze_text_features(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Analyze text-specific features"""
        try:
            # Simplified text feature analysis
            return 1 - cosine(features1, features2) if len(features1) == len(features2) else 0.0
        except:
            return 0.0
    
    # Content-specific similarity methods (simplified)
    async def _analyze_audio_similarity(self, fp1: Dict, fp2: Dict) -> Dict[str, float]:
        """Audio-specific similarity analysis"""
        return {'audio_specific': 0.5}  # Placeholder
    
    async def _analyze_video_similarity(self, fp1: Dict, fp2: Dict) -> Dict[str, float]:
        """Video-specific similarity analysis"""
        return {'video_specific': 0.5}  # Placeholder
    
    async def _analyze_image_similarity(self, fp1: Dict, fp2: Dict) -> Dict[str, float]:
        """Image-specific similarity analysis"""
        return {'image_specific': 0.5}  # Placeholder
    
    async def _analyze_text_similarity(self, fp1: Dict, fp2: Dict) -> Dict[str, float]:
        """Text-specific similarity analysis"""
        return {'text_specific': 0.5}  # Placeholder
    
    async def _validate_fingerprints(self, fp1: Dict[str, Any], fp2: Dict[str, Any], 
                                   content_type: str):
        """Validate fingerprint inputs"""
        if not fp1 or not fp2:
            raise ValidationError("Both fingerprints are required")
        
        if not content_type:
            raise ValidationError("Content type is required")
        
        # Check if at least one similarity method is available
        has_hash = 'hash' in fp1 and 'hash' in fp2
        has_features = 'features' in fp1 and 'features' in fp2
        has_embedding = 'embedding' in fp1 and 'embedding' in fp2
        
        if not (has_hash or has_features or has_embedding):
            raise ValidationError("No comparable fingerprint data found")
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Similarity matcher cleaned up")
