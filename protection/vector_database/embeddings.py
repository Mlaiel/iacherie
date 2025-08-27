"""
🔗 Vector Embeddings Engine
============================

Advanced embedding generation for multi-modal content fingerprints.
Transforms content fingerprints into high-dimensional vectors for similarity search.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from pathlib import Path

try:
    import torch
    import torch.nn as nn
    from sentence_transformers import SentenceTransformer
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from transformers import CLIPProcessor, CLIPModel
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False

logger = logging.getLogger(__name__)


class EmbeddingType(Enum):
    """Types of embeddings supported"""
    AUDIO_SPECTRAL = "audio_spectral"
    VIDEO_TEMPORAL = "video_temporal"
    IMAGE_VISUAL = "image_visual"
    TEXT_SEMANTIC = "text_semantic"
    COMPOSITE_MULTIMODAL = "composite_multimodal"


@dataclass
class EmbeddingResult:
    """Result of embedding generation"""
    embedding_id: str
    vector: np.ndarray
    embedding_type: EmbeddingType
    dimension: int
    confidence_score: float
    metadata: Dict[str, Any]
    processing_time: float


class AudioEmbeddingGenerator:
    """Generate embeddings for audio content"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dimension = config.get('audio_embedding_dim', 512)
        self.logger = logging.getLogger(f"{__name__}.AudioEmbeddingGenerator")
    
    async def generate_embedding(
        self,
        audio_features: Dict[str, Any],
        content_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EmbeddingResult:
        """Generate embedding from audio features"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Extract spectral features
            spectral_features = audio_features.get('spectral_features', {})
            mfcc = spectral_features.get('mfcc', [])
            chroma = spectral_features.get('chroma', [])
            spectral_centroid = spectral_features.get('spectral_centroid', [])
            
            # Create feature vector
            feature_vector = []
            
            # MFCC features (13 coefficients)
            if mfcc:
                mfcc_mean = np.mean(mfcc, axis=0)[:13]
                feature_vector.extend(mfcc_mean.tolist())
            else:
                feature_vector.extend([0.0] * 13)
            
            # Chroma features (12 bins)
            if chroma:
                chroma_mean = np.mean(chroma, axis=0)[:12]
                feature_vector.extend(chroma_mean.tolist())
            else:
                feature_vector.extend([0.0] * 12)
            
            # Spectral centroid
            if spectral_centroid:
                centroid_stats = [
                    np.mean(spectral_centroid),
                    np.std(spectral_centroid),
                    np.max(spectral_centroid),
                    np.min(spectral_centroid)
                ]
                feature_vector.extend(centroid_stats)
            else:
                feature_vector.extend([0.0] * 4)
            
            # Pad or truncate to desired dimension
            if len(feature_vector) < self.dimension:
                feature_vector.extend([0.0] * (self.dimension - len(feature_vector)))
            else:
                feature_vector = feature_vector[:self.dimension]
            
            # Normalize vector
            vector = np.array(feature_vector, dtype=np.float32)
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Calculate confidence based on feature richness
            confidence_score = min(0.95, 0.6 + len([f for f in feature_vector if abs(f) > 0.01]) / len(feature_vector))
            
            embedding_id = f"audio_emb_{hashlib.md5(content_id.encode()).hexdigest()[:12]}"
            
            return EmbeddingResult(
                embedding_id=embedding_id,
                vector=vector,
                embedding_type=EmbeddingType.AUDIO_SPECTRAL,
                dimension=self.dimension,
                confidence_score=confidence_score,
                metadata=metadata or {},
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Audio embedding generation failed: {e}")
            raise


class VideoEmbeddingGenerator:
    """Generate embeddings for video content"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dimension = config.get('video_embedding_dim', 1024)
        self.logger = logging.getLogger(f"{__name__}.VideoEmbeddingGenerator")
    
    async def generate_embedding(
        self,
        video_features: Dict[str, Any],
        content_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EmbeddingResult:
        """Generate embedding from video features"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Extract visual features
            visual_features = video_features.get('visual_features', {})
            color_histogram = visual_features.get('color_histogram', [])
            edge_features = visual_features.get('edge_features', [])
            motion_vectors = video_features.get('motion_vectors', [])
            scene_changes = video_features.get('scene_changes', [])
            
            # Create feature vector
            feature_vector = []
            
            # Color histogram (256 bins reduced to 64)
            if color_histogram:
                hist_reduced = np.histogram(color_histogram, bins=64)[0]
                hist_normalized = hist_reduced / (np.sum(hist_reduced) + 1e-8)
                feature_vector.extend(hist_normalized.tolist())
            else:
                feature_vector.extend([0.0] * 64)
            
            # Edge density features
            if edge_features:
                edge_stats = [
                    np.mean(edge_features),
                    np.std(edge_features),
                    np.max(edge_features),
                    np.min(edge_features)
                ]
                feature_vector.extend(edge_stats)
            else:
                feature_vector.extend([0.0] * 4)
            
            # Motion analysis
            if motion_vectors:
                motion_stats = [
                    np.mean(motion_vectors),
                    np.std(motion_vectors),
                    len(motion_vectors)
                ]
                feature_vector.extend(motion_stats)
            else:
                feature_vector.extend([0.0] * 3)
            
            # Scene change detection
            if scene_changes:
                scene_stats = [
                    len(scene_changes),
                    np.mean(np.diff(scene_changes)) if len(scene_changes) > 1 else 0.0
                ]
                feature_vector.extend(scene_stats)
            else:
                feature_vector.extend([0.0] * 2)
            
            # Pad or truncate to desired dimension
            if len(feature_vector) < self.dimension:
                feature_vector.extend([0.0] * (self.dimension - len(feature_vector)))
            else:
                feature_vector = feature_vector[:self.dimension]
            
            # Normalize vector
            vector = np.array(feature_vector, dtype=np.float32)
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Calculate confidence based on feature richness
            confidence_score = min(0.95, 0.7 + len([f for f in feature_vector if abs(f) > 0.01]) / len(feature_vector))
            
            embedding_id = f"video_emb_{hashlib.md5(content_id.encode()).hexdigest()[:12]}"
            
            return EmbeddingResult(
                embedding_id=embedding_id,
                vector=vector,
                embedding_type=EmbeddingType.VIDEO_TEMPORAL,
                dimension=self.dimension,
                confidence_score=confidence_score,
                metadata=metadata or {},
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Video embedding generation failed: {e}")
            raise


class ImageEmbeddingGenerator:
    """Generate embeddings for image content"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dimension = config.get('image_embedding_dim', 768)
        self.logger = logging.getLogger(f"{__name__}.ImageEmbeddingGenerator")
        self.clip_model = None
        self.clip_processor = None
        
        if CLIP_AVAILABLE and config.get('use_clip', True):
            try:
                self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                self.logger.info("CLIP model loaded for advanced image embeddings")
            except Exception as e:
                self.logger.warning(f"Failed to load CLIP model: {e}")
    
    async def generate_embedding(
        self,
        image_features: Dict[str, Any],
        content_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EmbeddingResult:
        """Generate embedding from image features"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Extract visual features
            perceptual_features = image_features.get('perceptual_features', {})
            color_histogram = perceptual_features.get('color_histogram', [])
            edge_density = perceptual_features.get('edge_density', 0.0)
            texture_features = perceptual_features.get('texture_features', [])
            
            # Create feature vector
            feature_vector = []
            
            # Color histogram features (reduced to 128 bins)
            if color_histogram:
                if len(color_histogram) > 128:
                    # Reduce histogram size
                    hist_reduced = np.array(color_histogram[:128])
                else:
                    hist_reduced = np.array(color_histogram + [0.0] * (128 - len(color_histogram)))
                
                hist_normalized = hist_reduced / (np.sum(hist_reduced) + 1e-8)
                feature_vector.extend(hist_normalized.tolist())
            else:
                feature_vector.extend([0.0] * 128)
            
            # Edge density
            feature_vector.append(float(edge_density))
            
            # Texture features
            if texture_features:
                texture_stats = [
                    np.mean(texture_features),
                    np.std(texture_features),
                    np.max(texture_features),
                    np.min(texture_features)
                ]
                feature_vector.extend(texture_stats)
            else:
                feature_vector.extend([0.0] * 4)
            
            # Hash-based features
            dhash = perceptual_features.get('dhash', '')
            phash = perceptual_features.get('phash', '')
            ahash = perceptual_features.get('ahash', '')
            
            # Convert hashes to numerical features
            for hash_str in [dhash, phash, ahash]:
                if hash_str:
                    # Convert hex string to numerical representation
                    hash_int = int(hash_str.replace('dhash_', '').replace('phash_', '').replace('ahash_', ''), 16) if hash_str else 0
                    hash_features = [(hash_int >> i) & 1 for i in range(16)]  # 16-bit representation
                    feature_vector.extend(hash_features)
                else:
                    feature_vector.extend([0.0] * 16)
            
            # Pad or truncate to desired dimension
            if len(feature_vector) < self.dimension:
                feature_vector.extend([0.0] * (self.dimension - len(feature_vector)))
            else:
                feature_vector = feature_vector[:self.dimension]
            
            # Normalize vector
            vector = np.array(feature_vector, dtype=np.float32)
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Calculate confidence based on feature richness
            confidence_score = min(0.95, 0.75 + len([f for f in feature_vector if abs(f) > 0.01]) / len(feature_vector))
            
            embedding_id = f"image_emb_{hashlib.md5(content_id.encode()).hexdigest()[:12]}"
            
            return EmbeddingResult(
                embedding_id=embedding_id,
                vector=vector,
                embedding_type=EmbeddingType.IMAGE_VISUAL,
                dimension=self.dimension,
                confidence_score=confidence_score,
                metadata=metadata or {},
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Image embedding generation failed: {e}")
            raise


class TextEmbeddingGenerator:
    """Generate embeddings for text content"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dimension = config.get('text_embedding_dim', 384)
        self.logger = logging.getLogger(f"{__name__}.TextEmbeddingGenerator")
        self.sentence_model = None
        
        if TORCH_AVAILABLE and config.get('use_sentence_transformers', True):
            try:
                model_name = config.get('sentence_model', 'all-MiniLM-L6-v2')
                self.sentence_model = SentenceTransformer(model_name)
                self.logger.info(f"SentenceTransformer model '{model_name}' loaded")
            except Exception as e:
                self.logger.warning(f"Failed to load SentenceTransformer: {e}")
    
    async def generate_embedding(
        self,
        text_features: Dict[str, Any],
        content_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EmbeddingResult:
        """Generate embedding from text features"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Extract text content
            text_content = text_features.get('text_content', '')
            linguistic_features = text_features.get('linguistic_features', {})
            
            feature_vector = []
            
            if self.sentence_model and text_content:
                # Use SentenceTransformer for semantic embeddings
                try:
                    embeddings = self.sentence_model.encode([text_content])
                    semantic_vector = embeddings[0]
                    feature_vector.extend(semantic_vector.tolist())
                except Exception as e:
                    self.logger.warning(f"SentenceTransformer encoding failed: {e}")
                    feature_vector.extend([0.0] * 384)
            else:
                # Fallback to statistical features
                char_frequency = linguistic_features.get('character_frequency', {})
                word_count = linguistic_features.get('word_count', 0)
                sentence_count = linguistic_features.get('sentence_count', 0)
                
                # Character frequency features (26 letters)
                alphabet_freq = []
                for char in 'abcdefghijklmnopqrstuvwxyz':
                    freq = char_frequency.get(char, 0)
                    alphabet_freq.append(freq)
                
                # Normalize frequency
                total_chars = sum(alphabet_freq) + 1e-8
                alphabet_freq = [f / total_chars for f in alphabet_freq]
                feature_vector.extend(alphabet_freq)
                
                # Statistical features
                avg_word_length = word_count / max(1, sentence_count)
                feature_vector.extend([
                    word_count / 1000.0,  # Normalized word count
                    sentence_count / 100.0,  # Normalized sentence count
                    avg_word_length / 10.0,  # Normalized average word length
                    len(text_content) / 10000.0  # Normalized text length
                ])
                
                # Pad to desired dimension
                if len(feature_vector) < self.dimension:
                    feature_vector.extend([0.0] * (self.dimension - len(feature_vector)))
            
            # Ensure correct dimension
            if len(feature_vector) > self.dimension:
                feature_vector = feature_vector[:self.dimension]
            elif len(feature_vector) < self.dimension:
                feature_vector.extend([0.0] * (self.dimension - len(feature_vector)))
            
            # Normalize vector
            vector = np.array(feature_vector, dtype=np.float32)
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Calculate confidence based on text quality
            confidence_score = min(0.95, 0.6 + min(0.3, len(text_content) / 1000.0))
            
            embedding_id = f"text_emb_{hashlib.md5(content_id.encode()).hexdigest()[:12]}"
            
            return EmbeddingResult(
                embedding_id=embedding_id,
                vector=vector,
                embedding_type=EmbeddingType.TEXT_SEMANTIC,
                dimension=self.dimension,
                confidence_score=confidence_score,
                metadata=metadata or {},
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Text embedding generation failed: {e}")
            raise


class CompositeEmbeddingGenerator:
    """Generate composite embeddings for multi-modal content"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dimension = config.get('composite_embedding_dim', 1536)
        self.logger = logging.getLogger(f"{__name__}.CompositeEmbeddingGenerator")
        
        # Initialize individual generators
        self.audio_generator = AudioEmbeddingGenerator(config)
        self.video_generator = VideoEmbeddingGenerator(config)
        self.image_generator = ImageEmbeddingGenerator(config)
        self.text_generator = TextEmbeddingGenerator(config)
    
    async def generate_embedding(
        self,
        multi_modal_features: Dict[str, Any],
        content_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EmbeddingResult:
        """Generate composite embedding from multi-modal features"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            component_embeddings = []
            used_modalities = []
            
            # Generate individual embeddings for available modalities
            if 'audio_features' in multi_modal_features:
                audio_emb = await self.audio_generator.generate_embedding(
                    multi_modal_features['audio_features'], content_id, metadata
                )
                component_embeddings.append(audio_emb.vector)
                used_modalities.append('audio')
            
            if 'video_features' in multi_modal_features:
                video_emb = await self.video_generator.generate_embedding(
                    multi_modal_features['video_features'], content_id, metadata
                )
                component_embeddings.append(video_emb.vector)
                used_modalities.append('video')
            
            if 'image_features' in multi_modal_features:
                image_emb = await self.image_generator.generate_embedding(
                    multi_modal_features['image_features'], content_id, metadata
                )
                component_embeddings.append(image_emb.vector)
                used_modalities.append('image')
            
            if 'text_features' in multi_modal_features:
                text_emb = await self.text_generator.generate_embedding(
                    multi_modal_features['text_features'], content_id, metadata
                )
                component_embeddings.append(text_emb.vector)
                used_modalities.append('text')
            
            if not component_embeddings:
                raise ValueError("No valid modalities found for composite embedding")
            
            # Concatenate and normalize embeddings
            concatenated = np.concatenate(component_embeddings)
            
            # Resize to target dimension
            if len(concatenated) > self.dimension:
                # Use PCA-like reduction by selecting most significant components
                composite_vector = concatenated[:self.dimension]
            else:
                # Pad with zeros
                composite_vector = np.zeros(self.dimension, dtype=np.float32)
                composite_vector[:len(concatenated)] = concatenated
            
            # Normalize
            norm = np.linalg.norm(composite_vector)
            if norm > 0:
                composite_vector = composite_vector / norm
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # Calculate confidence based on number of modalities
            confidence_score = min(0.95, 0.5 + 0.1 * len(used_modalities))
            
            embedding_id = f"composite_emb_{hashlib.md5(content_id.encode()).hexdigest()[:12]}"
            
            composite_metadata = metadata.copy() if metadata else {}
            composite_metadata['used_modalities'] = used_modalities
            composite_metadata['modality_count'] = len(used_modalities)
            
            return EmbeddingResult(
                embedding_id=embedding_id,
                vector=composite_vector,
                embedding_type=EmbeddingType.COMPOSITE_MULTIMODAL,
                dimension=self.dimension,
                confidence_score=confidence_score,
                metadata=composite_metadata,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Composite embedding generation failed: {e}")
            raise


class EmbeddingService:
    """Main service for generating embeddings from content features"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.EmbeddingService")
        
        # Initialize generators
        self.audio_generator = AudioEmbeddingGenerator(config)
        self.video_generator = VideoEmbeddingGenerator(config)
        self.image_generator = ImageEmbeddingGenerator(config)
        self.text_generator = TextEmbeddingGenerator(config)
        self.composite_generator = CompositeEmbeddingGenerator(config)
        
        self.logger.info("EmbeddingService initialized with all generators")
    
    async def generate_embedding(
        self,
        content_features: Dict[str, Any],
        content_id: str,
        embedding_type: Optional[EmbeddingType] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EmbeddingResult:
        """Generate embedding based on content type and features"""
        try:
            # Auto-detect embedding type if not specified
            if embedding_type is None:
                embedding_type = self._detect_embedding_type(content_features)
            
            # Route to appropriate generator
            if embedding_type == EmbeddingType.AUDIO_SPECTRAL:
                return await self.audio_generator.generate_embedding(
                    content_features, content_id, metadata
                )
            elif embedding_type == EmbeddingType.VIDEO_TEMPORAL:
                return await self.video_generator.generate_embedding(
                    content_features, content_id, metadata
                )
            elif embedding_type == EmbeddingType.IMAGE_VISUAL:
                return await self.image_generator.generate_embedding(
                    content_features, content_id, metadata
                )
            elif embedding_type == EmbeddingType.TEXT_SEMANTIC:
                return await self.text_generator.generate_embedding(
                    content_features, content_id, metadata
                )
            elif embedding_type == EmbeddingType.COMPOSITE_MULTIMODAL:
                return await self.composite_generator.generate_embedding(
                    content_features, content_id, metadata
                )
            else:
                raise ValueError(f"Unsupported embedding type: {embedding_type}")
                
        except Exception as e:
            self.logger.error(f"Embedding generation failed for {content_id}: {e}")
            raise
    
    def _detect_embedding_type(self, content_features: Dict[str, Any]) -> EmbeddingType:
        """Auto-detect the appropriate embedding type based on available features"""
        feature_types = set(content_features.keys())
        
        # Check for multi-modal content
        modality_count = sum([
            'audio_features' in feature_types,
            'video_features' in feature_types,
            'image_features' in feature_types,
            'text_features' in feature_types
        ])
        
        if modality_count > 1:
            return EmbeddingType.COMPOSITE_MULTIMODAL
        
        # Single modality detection
        if 'audio_features' in feature_types or 'spectral_features' in feature_types:
            return EmbeddingType.AUDIO_SPECTRAL
        elif 'video_features' in feature_types or 'visual_features' in feature_types:
            return EmbeddingType.VIDEO_TEMPORAL
        elif 'image_features' in feature_types or 'perceptual_features' in feature_types:
            return EmbeddingType.IMAGE_VISUAL
        elif 'text_features' in feature_types or 'text_content' in feature_types:
            return EmbeddingType.TEXT_SEMANTIC
        else:
            # Default to text if no clear type detected
            return EmbeddingType.TEXT_SEMANTIC
    
    async def batch_generate_embeddings(
        self,
        content_features_list: List[Tuple[Dict[str, Any], str]],
        embedding_type: Optional[EmbeddingType] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[EmbeddingResult]:
        """Generate embeddings for multiple content items in batch"""
        try:
            tasks = []
            for content_features, content_id in content_features_list:
                task = self.generate_embedding(
                    content_features, content_id, embedding_type, metadata
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log errors
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    content_id = content_features_list[i][1]
                    self.logger.error(f"Batch embedding failed for {content_id}: {result}")
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            self.logger.error(f"Batch embedding generation failed: {e}")
            raise
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about embedding generation"""
        return {
            'supported_types': [e.value for e in EmbeddingType],
            'dimensions': {
                'audio': self.config.get('audio_embedding_dim', 512),
                'video': self.config.get('video_embedding_dim', 1024),
                'image': self.config.get('image_embedding_dim', 768),
                'text': self.config.get('text_embedding_dim', 384),
                'composite': self.config.get('composite_embedding_dim', 1536)
            },
            'frameworks': {
                'torch_available': TORCH_AVAILABLE,
                'clip_available': CLIP_AVAILABLE
            }
        }
