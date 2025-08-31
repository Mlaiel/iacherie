# Advanced Visual Embeddings and Similarity Matching
# Industrial-Grade Content Similarity and Matching Engine
#
# Project Team Specialties:
# - Lead Dev + AI Architect: Advanced AI/ML Systems Design
# - Backend Senior (Python/FastAPI): High-Performance API Development  
# - ML Engineer (TensorFlow/PyTorch/HuggingFace): Deep Learning Models
# - DBA & Data Engineer: Scalable Data Architecture
# - Security Backend Specialist: Enterprise Security Implementation
# - Microservices Architect: Distributed Systems Design
# - Audio Developer: Professional Audio Processing
# - DevOps Engineer: Production Infrastructure
# - AI Prompt Engineer: Advanced Language Model Integration
#
# Created by: Fahed Mlaiel (mlaiel@live.de)
# 
#   STRICT COPYRIGHT WARNING  
# This code, concept, and intellectual property belongs exclusively to Fahed Mlaiel.
# ANY unauthorized use, reproduction, distribution, or theft of this code/concept 
# without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is 
# STRICTLY PROHIBITED and will result in immediate legal action.
# All rights reserved. Patent pending.

import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import faiss
import pickle
import hashlib
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import imagehash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingType(Enum):
    """Types of visual embeddings"""
    DEEP_FEATURES = "deep_features"
    PERCEPTUAL_HASH = "perceptual_hash"
    COLOR_HISTOGRAM = "color_histogram"
    TEXTURE_FEATURES = "texture_features"
    EDGE_FEATURES = "edge_features"
    SEMANTIC_FEATURES = "semantic_features"
    STYLE_FEATURES = "style_features"
    CONTENT_FEATURES = "content_features"

class SimilarityMetric(Enum):
    """Similarity metrics"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    HAMMING = "hamming"
    JACCARD = "jaccard"
    PEARSON = "pearson"
    SSIM = "ssim"
    LPIPS = "lpips"

@dataclass
class MatchingThreshold:
    """Threshold configuration for matching"""
    similarity_threshold: float = 0.8
    confidence_threshold: float = 0.7
    distance_threshold: float = 0.3
    quality_threshold: float = 0.6
    strict_mode: bool = False
    adaptive_threshold: bool = True
    context_aware: bool = True

@dataclass
class SimilarityResult:
    """Result structure for similarity comparison"""
    similarity_score: float
    confidence: float
    distance: float
    metric_used: SimilarityMetric
    embedding_type: EmbeddingType
    match_quality: float
    is_match: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0

@dataclass
class EmbeddingMetadata:
    """Metadata for embeddings"""
    embedding_id: str
    source_path: str
    creation_timestamp: float
    embedding_type: EmbeddingType
    model_version: str
    preprocessing_config: Dict[str, Any]
    quality_metrics: Dict[str, float]
    content_tags: List[str] = field(default_factory=list)
    author_info: Optional[str] = None

class VisualEmbeddingModel:
    """Advanced visual embedding generation and management system"""
    
    def __init__(self, device: str = "auto", cache_dir: str = "./embeddings_cache"):
        self.device = self._setup_device(device)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize embedding extractors
        self.extractors = self._init_extractors()
        
        # Initialize embedding storage
        self.embedding_store = {}
        self.metadata_store = {}
        
        # FAISS index for fast similarity search
        self.faiss_indices = {}
        
        # Load pre-trained models
        self._load_pretrained_models()
        
    def _setup_device(self, device: str) -> torch.device:
        """Setup optimal device for processing"""
        if device == "auto":
            if torch.cuda.is_available():
                return torch.device("cuda")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return torch.device("mps")
            else:
                return torch.device("cpu")
        return torch.device(device)
    
    def _init_extractors(self) -> Dict[str, Any]:
        """Initialize embedding extractors"""



        return {
            'deep_features': DeepFeatureExtractor(self.device),
            'perceptual_hash': PerceptualHashExtractor(),
            'color_histogram': ColorHistogramExtractor(),
            'texture_features': TextureFeatureExtractor(),
            'edge_features': EdgeFeatureExtractor(),
            'semantic_features': SemanticFeatureExtractor(self.device),
            'style_features': StyleFeatureExtractor(self.device),
            'content_features': ContentFeatureExtractor(self.device)
        }
    
    def _load_pretrained_models(self):
        """Load pre-trained models for feature extraction"""
        logger.info("Loading pre-trained models for feature extraction...")
        
        # Load models in background
        for extractor_name, extractor in self.extractors.items():
            if hasattr(extractor, 'load_model'):
                try:
                    extractor.load_model()
                    logger.info(f"Loaded {extractor_name} model successfully")
                except Exception as e:
                    logger.warning(f"Failed to load {extractor_name} model: {e}")
    
    def generate_embedding(self, image: np.ndarray, embedding_types: List[EmbeddingType], 
                          metadata: Optional[EmbeddingMetadata] = None) -> Dict[EmbeddingType, np.ndarray]:
        """Generate embeddings for an image"""
        embeddings = {}
        
        for embedding_type in embedding_types:
            try:
                start_time = time.time()
                
                if embedding_type == EmbeddingType.DEEP_FEATURES:
                    embedding = self.extractors['deep_features'].extract(image)
                elif embedding_type == EmbeddingType.PERCEPTUAL_HASH:
                    embedding = self.extractors['perceptual_hash'].extract(image)
                elif embedding_type == EmbeddingType.COLOR_HISTOGRAM:
                    embedding = self.extractors['color_histogram'].extract(image)
                elif embedding_type == EmbeddingType.TEXTURE_FEATURES:
                    embedding = self.extractors['texture_features'].extract(image)
                elif embedding_type == EmbeddingType.EDGE_FEATURES:
                    embedding = self.extractors['edge_features'].extract(image)
                elif embedding_type == EmbeddingType.SEMANTIC_FEATURES:
                    embedding = self.extractors['semantic_features'].extract(image)
                elif embedding_type == EmbeddingType.STYLE_FEATURES:
                    embedding = self.extractors['style_features'].extract(image)
                elif embedding_type == EmbeddingType.CONTENT_FEATURES:
                    embedding = self.extractors['content_features'].extract(image)
                else:
                    raise ValueError(f"Unsupported embedding type: {embedding_type}")
                
                embeddings[embedding_type] = embedding
                
                processing_time = time.time() - start_time
                logger.debug(f"Generated {embedding_type.value} embedding in {processing_time:.3f}s")
                
            except Exception as e:
                logger.error(f"Failed to generate {embedding_type.value} embedding: {e}")
                continue
        
        # Store embeddings if metadata provided
        if metadata:
            self._store_embeddings(embeddings, metadata)
        
        return embeddings
    
    def _store_embeddings(self, embeddings: Dict[EmbeddingType, np.ndarray], metadata: EmbeddingMetadata):
        """Store embeddings with metadata"""
        embedding_id = metadata.embedding_id
        
        # Store embeddings
        self.embedding_store[embedding_id] = embeddings
        self.metadata_store[embedding_id] = metadata
        
        # Update FAISS indices
        for embedding_type, embedding in embeddings.items():
            self._update_faiss_index(embedding_type, embedding_id, embedding)
        
        # Save to disk cache
        self._save_to_cache(embedding_id, embeddings, metadata)
    
    def _update_faiss_index(self, embedding_type: EmbeddingType, embedding_id: str, embedding: np.ndarray):
        """Update FAISS index with new embedding"""
        if embedding_type not in self.faiss_indices:
            # Initialize FAISS index
            dimension = embedding.shape[0] if embedding.ndim == 1 else embedding.size
            index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            self.faiss_indices[embedding_type] = {
                'index': index,
                'id_map': []
            }
        
        # Normalize embedding for cosine similarity
        normalized_embedding = embedding / np.linalg.norm(embedding)
        
        # Add to index
        self.faiss_indices[embedding_type]['index'].add(normalized_embedding.reshape(1, -1).astype('float32'))
        self.faiss_indices[embedding_type]['id_map'].append(embedding_id)
    
    def _save_to_cache(self, embedding_id: str, embeddings: Dict[EmbeddingType, np.ndarray], metadata: EmbeddingMetadata):
        """Save embeddings to disk cache"""
        cache_file = self.cache_dir / f"{embedding_id}.pkl"
        
        cache_data = {
            'embeddings': embeddings,
            'metadata': metadata
        }
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            logger.warning(f"Failed to save embedding cache: {e}")
    
    def load_from_cache(self, embedding_id: str) -> Optional[Tuple[Dict[EmbeddingType, np.ndarray], EmbeddingMetadata]]:
        """Load embeddings from cache"""
        cache_file = self.cache_dir / f"{embedding_id}.pkl"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                return cache_data['embeddings'], cache_data['metadata']
        except Exception as e:
            logger.warning(f"Failed to load embedding cache: {e}")
            return None

class SimilarityMatcher:
    """Advanced similarity matching engine"""
    
    def __init__(self, embedding_model: VisualEmbeddingModel):
        self.embedding_model = embedding_model
        self.similarity_functions = self._init_similarity_functions()
        self.adaptive_thresholds = {}
        
    def _init_similarity_functions(self) -> Dict[SimilarityMetric, callable]:
        """Initialize similarity computation functions"""



        return {
            SimilarityMetric.COSINE: self._cosine_similarity,
            SimilarityMetric.EUCLIDEAN: self._euclidean_distance,
            SimilarityMetric.MANHATTAN: self._manhattan_distance,
            SimilarityMetric.HAMMING: self._hamming_distance,
            SimilarityMetric.JACCARD: self._jaccard_similarity,
            SimilarityMetric.PEARSON: self._pearson_correlation,
            SimilarityMetric.SSIM: self._ssim_similarity,
            SimilarityMetric.LPIPS: self._lpips_similarity
        }
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray, 
                          metric: SimilarityMetric, embedding_type: EmbeddingType) -> SimilarityResult:
        """Compute similarity between two embeddings"""
        start_time = time.time()
        
        try:
            # Get similarity function
            similarity_func = self.similarity_functions[metric]
            
            # Compute similarity
            if metric in [SimilarityMetric.EUCLIDEAN, SimilarityMetric.MANHATTAN, SimilarityMetric.HAMMING]:
                # Distance metrics (lower is better)
                distance = similarity_func(embedding1, embedding2)
                similarity_score = 1.0 / (1.0 + distance)  # Convert to similarity
            else:
                # Similarity metrics (higher is better)
                similarity_score = similarity_func(embedding1, embedding2)
                distance = 1.0 - similarity_score  # Convert to distance
            
            # Calculate confidence based on embedding type and metric
            confidence = self._calculate_confidence(similarity_score, embedding_type, metric)
            
            # Determine match quality
            match_quality = self._assess_match_quality(similarity_score, confidence, embedding_type)
            
            # Apply adaptive threshold
            threshold = self._get_adaptive_threshold(embedding_type, metric)
            is_match = similarity_score >= threshold
            
            processing_time = time.time() - start_time
            
            return SimilarityResult(
                similarity_score=similarity_score,
                confidence=confidence,
                distance=distance,
                metric_used=metric,
                embedding_type=embedding_type,
                match_quality=match_quality,
                is_match=is_match,
                processing_time=processing_time,
                metadata={
                    'threshold_used': threshold,
                    'embedding_dimensions': embedding1.shape
                }
            )
            
        except Exception as e:
            logger.error(f"Similarity computation failed: {e}")
            return SimilarityResult(
                similarity_score=0.0,
                confidence=0.0,
                distance=1.0,
                metric_used=metric,
                embedding_type=embedding_type,
                match_quality=0.0,
                is_match=False,
                metadata={'error': str(e)}
            )
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity"""
        # Flatten vectors if needed
        vec1_flat = vec1.flatten()
        vec2_flat = vec2.flatten()
        
        # Compute cosine similarity
        dot_product = np.dot(vec1_flat, vec2_flat)
        norm1 = np.linalg.norm(vec1_flat)
        norm2 = np.linalg.norm(vec2_flat)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _euclidean_distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute Euclidean distance"""



        return np.linalg.norm(vec1.flatten() - vec2.flatten())
    
    def _manhattan_distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute Manhattan distance"""



        return np.sum(np.abs(vec1.flatten() - vec2.flatten()))
    
    def _hamming_distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute Hamming distance for binary vectors"""
        # Convert to binary if needed
        bin1 = (vec1 > 0.5).astype(int)
        bin2 = (vec2 > 0.5).astype(int)
        
        return np.sum(bin1.flatten() != bin2.flatten()) / len(bin1.flatten())
    
    def _jaccard_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute Jaccard similarity"""
        # Convert to binary
        bin1 = (vec1 > 0.5).astype(int)
        bin2 = (vec2 > 0.5).astype(int)
        
        intersection = np.sum(bin1 & bin2)
        union = np.sum(bin1 | bin2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _pearson_correlation(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute Pearson correlation coefficient"""
        correlation_matrix = np.corrcoef(vec1.flatten(), vec2.flatten())
        correlation = correlation_matrix[0, 1]
        
        # Handle NaN case
        if np.isnan(correlation):
            return 0.0
        
        return abs(correlation)  # Return absolute value
    
    def _ssim_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute SSIM-inspired similarity for image embeddings"""



        try:
            # Normalize vectors
            vec1_norm = (vec1 - np.mean(vec1)) / (np.std(vec1) + 1e-8)
            vec2_norm = (vec2 - np.mean(vec2)) / (np.std(vec2) + 1e-8)
            
            # SSIM-inspired computation with luminance, contrast, structure
            # Luminance comparison
            mu1, mu2 = np.mean(vec1_norm), np.mean(vec2_norm)
            luminance = (2 * mu1 * mu2 + 0.01) / (mu1**2 + mu2**2 + 0.01)
            
            # Contrast comparison  
            sigma1, sigma2 = np.std(vec1_norm), np.std(vec2_norm)
            contrast = (2 * sigma1 * sigma2 + 0.03) / (sigma1**2 + sigma2**2 + 0.03)
            
            # Structure comparison (correlation coefficient)
            covariance = np.mean((vec1_norm - mu1) * (vec2_norm - mu2))
            structure = (covariance + 0.015) / (sigma1 * sigma2 + 0.015)
            
            # Combined SSIM-like score
            ssim_score = luminance * contrast * structure
            
            # Normalize to [0, 1] range
            return max(0.0, min(1.0, (ssim_score + 1) / 2))
            
        except Exception as e:
            logger.warning(f"SSIM similarity calculation failed: {e}")
            return self._cosine_similarity(vec1, vec2)
    
    def _lpips_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute LPIPS-inspired perceptual similarity for embeddings"""



        try:
            # LPIPS-inspired multi-scale feature comparison
            # Split vectors into different "scale" segments for comparison
            
            vec_len = len(vec1)
            scales = [vec_len // 4, vec_len // 2, vec_len]  # Multi-scale analysis
            
            perceptual_scores = []
            
            for scale in scales:
                if scale <= vec_len:
                    # Extract features at this scale
                    v1_scale = vec1[:scale]
                    v2_scale = vec2[:scale]
                    
                    # Compute feature differences
                    diff = np.abs(v1_scale - v2_scale)
                    
                    # Weight differences by feature importance (higher dimensions often more important)
                    weights = np.linspace(1.0, 2.0, len(diff))
                    weighted_diff = diff * weights
                    
                    # Perceptual distance (lower is more similar)
                    perceptual_dist = np.mean(weighted_diff)
                    
                    # Convert to similarity score
                    similarity = 1.0 / (1.0 + perceptual_dist)
                    perceptual_scores.append(similarity)
            
            # Combine multi-scale similarities with weights
            scale_weights = [0.2, 0.3, 0.5]  # Higher weight for full-scale comparison
            weighted_similarity = sum(score * weight for score, weight in zip(perceptual_scores, scale_weights[:len(perceptual_scores)]))
            
            # Apply non-linear transformation for better perceptual alignment
            final_score = 1.0 - np.exp(-3 * weighted_similarity)
            
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            logger.warning(f"LPIPS similarity calculation failed: {e}")
            return self._cosine_similarity(vec1, vec2)
    
    def _calculate_confidence(self, similarity_score: float, embedding_type: EmbeddingType, metric: SimilarityMetric) -> float:
        """Calculate confidence score based on various factors"""
        base_confidence = similarity_score
        
        # Adjust confidence based on embedding type reliability
        type_multipliers = {
            EmbeddingType.DEEP_FEATURES: 1.0,
            EmbeddingType.SEMANTIC_FEATURES: 0.95,
            EmbeddingType.CONTENT_FEATURES: 0.9,
            EmbeddingType.STYLE_FEATURES: 0.85,
            EmbeddingType.PERCEPTUAL_HASH: 0.8,
            EmbeddingType.COLOR_HISTOGRAM: 0.7,
            EmbeddingType.TEXTURE_FEATURES: 0.75,
            EmbeddingType.EDGE_FEATURES: 0.65
        }
        
        # Adjust confidence based on metric reliability
        metric_multipliers = {
            SimilarityMetric.COSINE: 1.0,
            SimilarityMetric.PEARSON: 0.95,
            SimilarityMetric.EUCLIDEAN: 0.9,
            SimilarityMetric.JACCARD: 0.85,
            SimilarityMetric.MANHATTAN: 0.8,
            SimilarityMetric.HAMMING: 0.75,
            SimilarityMetric.SSIM: 0.9,
            SimilarityMetric.LPIPS: 0.85
        }
        
        type_mult = type_multipliers.get(embedding_type, 0.7)
        metric_mult = metric_multipliers.get(metric, 0.8)
        
        adjusted_confidence = base_confidence * type_mult * metric_mult
        
        return min(1.0, max(0.0, adjusted_confidence))
    
    def _assess_match_quality(self, similarity_score: float, confidence: float, embedding_type: EmbeddingType) -> float:
        """Assess overall match quality"""
        # Weighted combination of similarity and confidence
        quality = (similarity_score * 0.7) + (confidence * 0.3)
        
        # Bonus for high-quality embedding types
        if embedding_type in [EmbeddingType.DEEP_FEATURES, EmbeddingType.SEMANTIC_FEATURES]:
            quality *= 1.1
        
        return min(1.0, quality)
    
    def _get_adaptive_threshold(self, embedding_type: EmbeddingType, metric: SimilarityMetric) -> float:
        """Get adaptive threshold for matching"""
        # Default thresholds
        default_thresholds = {
            (EmbeddingType.DEEP_FEATURES, SimilarityMetric.COSINE): 0.85,
            (EmbeddingType.SEMANTIC_FEATURES, SimilarityMetric.COSINE): 0.8,
            (EmbeddingType.CONTENT_FEATURES, SimilarityMetric.COSINE): 0.75,
            (EmbeddingType.PERCEPTUAL_HASH, SimilarityMetric.HAMMING): 0.9,
            (EmbeddingType.COLOR_HISTOGRAM, SimilarityMetric.COSINE): 0.7,
        }
        
        key = (embedding_type, metric)
        return default_thresholds.get(key, 0.75)  # Default threshold

class ContentMatcher:
    """High-level content matching system"""
    
    def __init__(self, embedding_model: VisualEmbeddingModel, similarity_matcher: SimilarityMatcher):
        self.embedding_model = embedding_model
        self.similarity_matcher = similarity_matcher
        self.content_database = {}
        self.match_history = []
        
    def add_content(self, content_id: str, image: np.ndarray, metadata: Optional[Dict[str, Any]] = None):
        """Add content to the matching database"""
        # Generate embeddings
        embedding_types = [
            EmbeddingType.DEEP_FEATURES,
            EmbeddingType.PERCEPTUAL_HASH,
            EmbeddingType.COLOR_HISTOGRAM,
            EmbeddingType.SEMANTIC_FEATURES
        ]
        
        embedding_metadata = EmbeddingMetadata(
            embedding_id=content_id,
            source_path=metadata.get('source_path', '') if metadata else '',
            creation_timestamp=time.time(),
            embedding_type=EmbeddingType.DEEP_FEATURES,  # Primary type
            model_version="1.0.0",
            preprocessing_config={},
            quality_metrics={},
            content_tags=metadata.get('tags', []) if metadata else [],
            author_info=metadata.get('author', None) if metadata else None
        )
        
        embeddings = self.embedding_model.generate_embedding(image, embedding_types, embedding_metadata)
        
        # Store content
        self.content_database[content_id] = {
            'embeddings': embeddings,
            'metadata': embedding_metadata,
            'original_metadata': metadata or {}
        }
        
        logger.info(f"Added content {content_id} to matching database")
    
    def find_matches(self, query_image: np.ndarray, threshold: MatchingThreshold, 
                    max_results: int = 10) -> List[Dict[str, Any]]:
        """Find matching content in the database"""
        # Generate query embeddings
        query_embedding_types = [
            EmbeddingType.DEEP_FEATURES,
            EmbeddingType.PERCEPTUAL_HASH,
            EmbeddingType.COLOR_HISTOGRAM,
            EmbeddingType.SEMANTIC_FEATURES
        ]
        
        query_embeddings = self.embedding_model.generate_embedding(query_image, query_embedding_types)
        
        matches = []
        
        # Compare with each content in database
        for content_id, content_data in self.content_database.items():
            content_embeddings = content_data['embeddings']
            
            # Multi-embedding similarity
            similarity_results = []
            
            for embedding_type in query_embedding_types:
                if embedding_type in query_embeddings and embedding_type in content_embeddings:
                    # Choose appropriate metric for embedding type
                    if embedding_type == EmbeddingType.PERCEPTUAL_HASH:
                        metric = SimilarityMetric.HAMMING
                    else:
                        metric = SimilarityMetric.COSINE
                    
                    result = self.similarity_matcher.compute_similarity(
                        query_embeddings[embedding_type],
                        content_embeddings[embedding_type],
                        metric,
                        embedding_type
                    )
                    
                    similarity_results.append(result)
            
            if similarity_results:
                # Aggregate similarity scores
                aggregated_similarity = self._aggregate_similarities(similarity_results)
                
                # Check if meets threshold
                if aggregated_similarity['overall_similarity'] >= threshold.similarity_threshold:
                    match_data = {
                        'content_id': content_id,
                        'similarity_score': aggregated_similarity['overall_similarity'],
                        'confidence': aggregated_similarity['overall_confidence'],
                        'match_quality': aggregated_similarity['match_quality'],
                        'individual_results': similarity_results,
                        'metadata': content_data['metadata'],
                        'original_metadata': content_data['original_metadata']
                    }
                    
                    matches.append(match_data)
        
        # Sort by similarity score
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Apply max results limit
        matches = matches[:max_results]
        
        # Log match attempt
        self.match_history.append({
            'timestamp': time.time(),
            'query_type': 'image_search',
            'results_count': len(matches),
            'threshold_used': threshold.similarity_threshold
        })
        
        logger.info(f"Found {len(matches)} matches for query image")
        return matches
    
    def _aggregate_similarities(self, similarity_results: List[SimilarityResult]) -> Dict[str, float]:
        """Aggregate multiple similarity results"""
        if not similarity_results:
            return {
                'overall_similarity': 0.0,
                'overall_confidence': 0.0,
                'match_quality': 0.0
            }
        
        # Weighted aggregation based on embedding type reliability
        weights = {
            EmbeddingType.DEEP_FEATURES: 0.4,
            EmbeddingType.SEMANTIC_FEATURES: 0.3,
            EmbeddingType.CONTENT_FEATURES: 0.2,
            EmbeddingType.PERCEPTUAL_HASH: 0.1
        }
        
        total_weight = 0.0
        weighted_similarity = 0.0
        weighted_confidence = 0.0
        weighted_quality = 0.0
        
        for result in similarity_results:
            weight = weights.get(result.embedding_type, 0.1)
            total_weight += weight
            
            weighted_similarity += result.similarity_score * weight
            weighted_confidence += result.confidence * weight
            weighted_quality += result.match_quality * weight
        
        if total_weight > 0:
            overall_similarity = weighted_similarity / total_weight
            overall_confidence = weighted_confidence / total_weight
            match_quality = weighted_quality / total_weight
        else:
            overall_similarity = np.mean([r.similarity_score for r in similarity_results])
            overall_confidence = np.mean([r.confidence for r in similarity_results])
            match_quality = np.mean([r.match_quality for r in similarity_results])
        
        return {
            'overall_similarity': overall_similarity,
            'overall_confidence': overall_confidence,
            'match_quality': match_quality
        }
    
    def batch_search(self, query_images: List[np.ndarray], threshold: MatchingThreshold, 
                    max_results_per_query: int = 10) -> List[List[Dict[str, Any]]]:
        """Perform batch search for multiple query images"""
        results = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_index = {
                executor.submit(self.find_matches, img, threshold, max_results_per_query): i
                for i, img in enumerate(query_images)
            }
            
            # Initialize results list with correct size
            results = [[] for _ in range(len(query_images))]
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    logger.error(f"Batch search failed for image {index}: {e}")
                    results[index] = []
        
        return results

class EmbeddingGenerator:
    """Utility class for generating various types of embeddings"""
    
    def __init__(self, device: str = "auto"):
        self.device = self._setup_device(device)
        self.generators = self._init_generators()
    
    def _setup_device(self, device: str) -> torch.device:
        """Setup device"""
        if device == "auto":
            if torch.cuda.is_available():
                return torch.device("cuda")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return torch.device("mps")
            else:
                return torch.device("cpu")
        return torch.device(device)
    
    def _init_generators(self) -> Dict[str, Any]:
        """Initialize embedding generators"""



        return {
            'deep': DeepFeatureExtractor(self.device),
            'perceptual': PerceptualHashExtractor(),
            'color': ColorHistogramExtractor(),
            'texture': TextureFeatureExtractor(),
            'edge': EdgeFeatureExtractor()
        }
    
    def generate_all_embeddings(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """Generate all available embeddings for an image"""
        embeddings = {}
        
        for name, generator in self.generators.items():
            try:
                embedding = generator.extract(image)
                embeddings[name] = embedding
            except Exception as e:
                logger.warning(f"Failed to generate {name} embedding: {e}")
        
        return embeddings

# Feature Extractor Classes
class BaseFeatureExtractor(ABC):
    """Abstract base class for feature extractors"""
    
    @abstractmethod
    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract features from image"""
        pass

class DeepFeatureExtractor(BaseFeatureExtractor):
    """Deep learning-based feature extractor"""
    
    def __init__(self, device: torch.device):
        self.device = device
        self.model = None
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def load_model(self):
        """Load pre-trained model"""



        try:
            import torchvision.models as models
            self.model = models.resnet50(pretrained=True)
            self.model.fc = nn.Identity()  # Remove final classification layer
            self.model.eval()
            self.model.to(self.device)
            logger.info("Loaded ResNet50 model for deep feature extraction")
        except Exception as e:
            logger.error(f"Failed to load deep feature model: {e}")
    
    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract deep features"""
        if self.model is None:
            self.load_model()
        
        if self.model is None:
            # Fallback to basic features
            return self._extract_basic_features(image)
        
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(image)
            
            # Apply transforms
            input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            
            # Extract features
            with torch.no_grad():
                features = self.model(input_tensor)
            
            return features.cpu().numpy().flatten()
            
        except Exception as e:
            logger.warning(f"Deep feature extraction failed: {e}")
            return self._extract_basic_features(image)
    
    def _extract_basic_features(self, image: np.ndarray) -> np.ndarray:
        """Fallback basic feature extraction"""
        # Simple color and edge features
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        edges = cv2.Canny(gray, 50, 150)
        edge_hist = cv2.calcHist([edges], [0], None, [256], [0, 256])
        
        features = np.concatenate([hist.flatten(), edge_hist.flatten()])
        return features / np.linalg.norm(features)  # Normalize

class PerceptualHashExtractor(BaseFeatureExtractor):
    """Perceptual hash extractor"""
    
    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract perceptual hash"""
        pil_image = Image.fromarray(image)
        
        # Multiple hash types for robustness
        phash = imagehash.phash(pil_image, hash_size=16)
        ahash = imagehash.average_hash(pil_image, hash_size=16)
        dhash = imagehash.dhash(pil_image, hash_size=16)
        whash = imagehash.whash(pil_image, hash_size=16)
        
        # Combine hashes
        combined_hash = str(phash) + str(ahash) + str(dhash) + str(whash)
        
        # Convert to binary array
        binary_array = np.array([int(c, 16) for c in combined_hash])
        
        return binary_array

class ColorHistogramExtractor(BaseFeatureExtractor):
    """Color histogram feature extractor"""
    
    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract color histogram features"""
        # RGB histograms
        hist_r = cv2.calcHist([image], [0], None, [32], [0, 256])
        hist_g = cv2.calcHist([image], [1], None, [32], [0, 256])
        hist_b = cv2.calcHist([image], [2], None, [32], [0, 256])
        
        # HSV histograms for better color representation
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hist_h = cv2.calcHist([hsv], [0], None, [32], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [32], [0, 256])
        hist_v = cv2.calcHist([hsv], [2], None, [32], [0, 256])
        
        # Combine all histograms
        combined_hist = np.concatenate([
            hist_r.flatten(), hist_g.flatten(), hist_b.flatten(),
            hist_h.flatten(), hist_s.flatten(), hist_v.flatten()
        ])
        
        # Normalize
        return combined_hist / np.sum(combined_hist)

class TextureFeatureExtractor(BaseFeatureExtractor):
    """Texture feature extractor using LBP and GLCM"""
    
    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract texture features"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Local Binary Pattern
        lbp_features = self._compute_lbp(gray)
        
        # Gray Level Co-occurrence Matrix features
        glcm_features = self._compute_glcm_features(gray)
        
        # Gabor filter responses
        gabor_features = self._compute_gabor_features(gray)
        
        # Combine all texture features
        texture_features = np.concatenate([lbp_features, glcm_features, gabor_features])
        
        return texture_features
    
    def _compute_lbp(self, gray: np.ndarray) -> np.ndarray:
        """Compute Local Binary Pattern features"""
        # Simplified LBP implementation
        h, w = gray.shape
        lbp = np.zeros_like(gray)
        
        for i in range(1, h-1):
            for j in range(1, w-1):
                center = gray[i, j]
                code = 0
                code |= (gray[i-1, j-1] > center) << 7
                code |= (gray[i-1, j] > center) << 6
                code |= (gray[i-1, j+1] > center) << 5
                code |= (gray[i, j+1] > center) << 4
                code |= (gray[i+1, j+1] > center) << 3
                code |= (gray[i+1, j] > center) << 2
                code |= (gray[i+1, j-1] > center) << 1
                code |= (gray[i, j-1] > center) << 0
                lbp[i, j] = code
        
        # Compute histogram
        hist = cv2.calcHist([lbp], [0], None, [256], [0, 256])
        return hist.flatten() / np.sum(hist)
    
    def _compute_glcm_features(self, gray: np.ndarray) -> np.ndarray:
        """Compute GLCM-based texture features"""
        # Simplified GLCM implementation
        # Quantize to reduce computation
        quantized = (gray // 32).astype(np.uint8)
        
        # Compute co-occurrence for horizontal direction
        glcm = np.zeros((8, 8), dtype=np.float32)
        h, w = quantized.shape
        
        for i in range(h):
            for j in range(w-1):
                glcm[quantized[i, j], quantized[i, j+1]] += 1
        
        # Normalize
        glcm = glcm / np.sum(glcm)
        
        # Compute texture measures
        contrast = np.sum(glcm * np.square(np.arange(8)[:, None] - np.arange(8)))
        correlation = np.sum(glcm * np.outer(np.arange(8), np.arange(8)))
        energy = np.sum(glcm ** 2)
        homogeneity = np.sum(glcm / (1 + np.abs(np.arange(8)[:, None] - np.arange(8))))
        
        return np.array([contrast, correlation, energy, homogeneity])
    
    def _compute_gabor_features(self, gray: np.ndarray) -> np.ndarray:
        """Compute Gabor filter features"""
        features = []
        
        # Different orientations and frequencies
        for theta in [0, 45, 90, 135]:
            for frequency in [0.1, 0.3, 0.5]:
                kernel = cv2.getGaborKernel((21, 21), 5, np.radians(theta), 
                                          2*np.pi*frequency, 0.5, 0, ktype=cv2.CV_32F)
                filtered = cv2.filter2D(gray, cv2.CV_8UC3, kernel)
                features.extend([np.mean(filtered), np.std(filtered)])
        
        return np.array(features)

class EdgeFeatureExtractor(BaseFeatureExtractor):
    """Edge-based feature extractor"""
    
    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract edge features"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Canny edges
        edges_canny = cv2.Canny(gray, 50, 150)
        
        # Sobel edges
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edges_sobel = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # Laplacian edges
        edges_laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        
        # Edge histograms
        hist_canny = cv2.calcHist([edges_canny], [0], None, [256], [0, 256])
        hist_sobel = cv2.calcHist([edges_sobel.astype(np.uint8)], [0], None, [256], [0, 256])
        hist_laplacian = cv2.calcHist([np.abs(edges_laplacian).astype(np.uint8)], [0], None, [256], [0, 256])
        
        # Combine edge features
        edge_features = np.concatenate([
            hist_canny.flatten(),
            hist_sobel.flatten(),
            hist_laplacian.flatten()
        ])
        
        # Normalize
        return edge_features / np.sum(edge_features)

class SemanticFeatureExtractor(BaseFeatureExtractor):
    """Semantic feature extractor using pre-trained models"""
    
    def __init__(self, device: torch.device):
        self.device = device
        self.model = None
    
    def load_model(self):
        """Load semantic model"""



        try:
            # Would load a semantic segmentation or object detection model
            # For now, use ResNet features as semantic features
            import torchvision.models as models
            self.model = models.resnet50(pretrained=True)
            self.model.eval()
            self.model.to(self.device)
            logger.info("Loaded semantic feature model")
        except Exception as e:
            logger.error(f"Failed to load semantic model: {e}")
    
    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract semantic features"""
        if self.model is None:
            self.load_model()
        
        # Use deep features as semantic features for now
        deep_extractor = DeepFeatureExtractor(self.device)
        return deep_extractor.extract(image)

class StyleFeatureExtractor(BaseFeatureExtractor):
    """Style feature extractor for artistic style analysis"""
    
    def __init__(self, device: torch.device):
        self.device = device
        self.model = None
    
    def load_model(self):
        """Load style analysis model"""
        # Would load a VGG model for style features
        try:
            import torchvision.models as models
            vgg = models.vgg19(pretrained=True).features
            self.model = nn.Sequential(*list(vgg.children())[:28])  # Up to conv4_4
            self.model.eval()
            self.model.to(self.device)
            logger.info("Loaded VGG model for style features")
        except Exception as e:
            logger.error(f"Failed to load style model: {e}")
    
    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract style features"""
        if self.model is None:
            self.load_model()
        
        if self.model is None:
            # Fallback to color features
            return ColorHistogramExtractor().extract(image)
        
        try:
            # Preprocess image
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            pil_image = Image.fromarray(image)
            input_tensor = transform(pil_image).unsqueeze(0).to(self.device)
            
            # Extract features
            with torch.no_grad():
                features = self.model(input_tensor)
            
            # Compute Gram matrix for style representation
            b, c, h, w = features.size()
            features = features.view(b, c, h * w)
            gram = torch.bmm(features, features.transpose(1, 2))
            
            return gram.cpu().numpy().flatten()
            
        except Exception as e:
            logger.warning(f"Style feature extraction failed: {e}")
            return ColorHistogramExtractor().extract(image)

class ContentFeatureExtractor(BaseFeatureExtractor):
    """Content feature extractor for content-based analysis"""
    
    def __init__(self, device: torch.device):
        self.device = device
        self.model = None
    
    def load_model(self):
        """Load content analysis model"""
        # Similar to deep features but with different layer selection
        try:
            import torchvision.models as models
            self.model = models.resnet50(pretrained=True)
            # Use features from conv4 layer for content
            self.model = nn.Sequential(*list(self.model.children())[:-3])
            self.model.eval()
            self.model.to(self.device)
            logger.info("Loaded content feature model")
        except Exception as e:
            logger.error(f"Failed to load content model: {e}")
    
    def extract(self, image: np.ndarray) -> np.ndarray:
        """Extract content features"""
        if self.model is None:
            self.load_model()
        
        if self.model is None:
            # Fallback to edge and texture features
            edge_extractor = EdgeFeatureExtractor()
            texture_extractor = TextureFeatureExtractor()
            
            edge_features = edge_extractor.extract(image)
            texture_features = texture_extractor.extract(image)
            
            return np.concatenate([edge_features[:512], texture_features[:512]])
        
        try:
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            pil_image = Image.fromarray(image)
            input_tensor = transform(pil_image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                features = self.model(input_tensor)
            
            # Global average pooling
            features = F.adaptive_avg_pool2d(features, (1, 1))
            
            return features.cpu().numpy().flatten()
            
        except Exception as e:
            logger.warning(f"Content feature extraction failed: {e}")
            # Fallback
            edge_extractor = EdgeFeatureExtractor()
            return edge_extractor.extract(image)
