"""Similarity Matching Engine for Content Protection

Advanced AI-powered similarity detection across all content types.
Provides fingerprint matching, vector similarity, and violation detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Content Protection
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + DBA + Security + Microservices + Audio + IA Prompt Engineer

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing and collaboration.
"""

import numpy as np
import torch
import faiss
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from pathlib import Path
import hashlib
import cv2
import librosa
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModel, AutoTokenizer, CLIPProcessor, CLIPModel
import chromaprint
import essentia.standard as es

from ..engines.vector_engine import VectorEngine
from ..fingerprinting.audio_fingerprint import AudioFingerprint
from ..fingerprinting.image_fingerprint import ImageFingerprint
from ..fingerprinting.video_fingerprint import VideoFingerprint
from ..fingerprinting.text_fingerprint import TextFingerprint
from ...utils.cache_manager import cache_result
from ...utils.metrics import track_performance
from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class SimilarityMatcher:
    """
    Enterprise-grade similarity matching system for content protection.
    
    Features:
    - Multi-modal similarity detection (audio, video, image, text)
    - FAISS vector database integration
    - Real-time fingerprint matching
    - Perceptual hashing and robust features
    - Copyright violation detection
    - Scalable similarity search
    """
    
    def __init__(self):
        """
Initialize similarity matcher with vector engines."""
        self.settings = get_settings()
        self.vector_engine = VectorEngine()
        
        # Initialize fingerprint extractors
        self.audio_fingerprint = AudioFingerprint()
        self.image_fingerprint = ImageFingerprint()
        self.video_fingerprint = VideoFingerprint()
        self.text_fingerprint = TextFingerprint()
        
        # FAISS indexes for different content types
        self.audio_index = None
        self.image_index = None
        self.video_index = None
        self.text_index = None
        
        # Models for deep feature extraction
        self.clip_model = None
        self.clip_processor = None
        self.text_model = None
        self.text_tokenizer = None
        
        # Similarity thresholds
        self.similarity_thresholds = {
            'audio': 0.85,
            'image': 0.80,
            'video': 0.82,
            'text': 0.75,
            'exact_match': 0.95
        }
        
        self._initialize_models()
        self._load_indexes()
        
    def _initialize_models(self) -> None:
        """
Initialize deep learning models for feature extraction."""
        try:
            # Load CLIP model for image/video similarity
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            # Load text embedding model
            self.text_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            self.text_tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            
            logger.info("Similarity matching models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing similarity models: {e}")
    
    def _load_indexes(self) -> None:
        """Load FAISS indexes for similarity search."""
        try:
            index_path = Path(self.settings.VECTOR_DB_PATH)
            
            # Load audio index
            audio_index_file = index_path / 'audio_similarity.index'
            if audio_index_file.exists():
                self.audio_index = faiss.read_index(str(audio_index_file))
            else:
                self.audio_index = faiss.IndexFlatIP(512)  # 512-dim audio features
                
            # Load image index
            image_index_file = index_path / 'image_similarity.index'
            if image_index_file.exists():
                self.image_index = faiss.read_index(str(image_index_file))
            else:
                self.image_index = faiss.IndexFlatIP(512)  # CLIP features
                
            # Load video index
            video_index_file = index_path / 'video_similarity.index'
            if video_index_file.exists():
                self.video_index = faiss.read_index(str(video_index_file))
            else:
                self.video_index = faiss.IndexFlatIP(512)  # Video features
                
            # Load text index
            text_index_file = index_path / 'text_similarity.index'
            if text_index_file.exists():
                self.text_index = faiss.read_index(str(text_index_file))
            else:
                self.text_index = faiss.IndexFlatIP(384)  # Text embedding dim
                
            logger.info("FAISS indexes loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading FAISS indexes: {e}")
    
    @track_performance
    @cache_result(ttl=300)
    def find_similar_content(
        self, 
        content_path: str, 
        content_type: str,
        top_k: int = 10,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar content across the database.
        
        Args:
            content_path: Path to content file
            content_type: Type of content (audio, image, video, text)
            top_k: Number of similar items to return
            threshold: Similarity threshold (optional)
            
        Returns:
            List of similar content with scores and metadata
        """
        try:
            # Get similarity threshold
            sim_threshold = threshold or self.similarity_thresholds.get(content_type, 0.8)
            
            # Extract features based on content type
            if content_type == 'audio':
                return self._find_similar_audio(content_path, top_k, sim_threshold)
            elif content_type == 'image':
                return self._find_similar_images(content_path, top_k, sim_threshold)
            elif content_type == 'video':
                return self._find_similar_videos(content_path, top_k, sim_threshold)
            elif content_type == 'text':
                return self._find_similar_text(content_path, top_k, sim_threshold)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
                
        except Exception as e:
            logger.error(f"Error finding similar content: {e}")
            return []
    
    def _find_similar_audio(self, audio_path: str, top_k: int, threshold: float) -> List[Dict[str, Any]]:
        """Find similar audio content using acoustic fingerprints."""
        try:
            # Extract audio fingerprint
            fingerprint = self.audio_fingerprint.extract_fingerprint(audio_path)
            
            # Extract deep audio features
            features = self._extract_audio_features(audio_path)
            
            # Search in FAISS index
            features_np = np.array(features).reshape(1, -1).astype('float32')
            scores, indices = self.audio_index.search(features_np, top_k)
            
            # Filter by threshold and prepare results
            similar_items = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if score >= threshold and idx != -1:
                    similar_items.append({
                        'index': int(idx),
                        'similarity_score': float(score),
                        'content_type': 'audio',
                        'match_type': 'acoustic_similarity',
                        'fingerprint_match': self._compare_audio_fingerprints(fingerprint, idx)
                    })
            
            return similar_items
            
        except Exception as e:
            logger.error(f"Error finding similar audio: {e}")
            return []
    
    def _find_similar_images(self, image_path: str, top_k: int, threshold: float) -> List[Dict[str, Any]]:
        """Find similar images using CLIP embeddings and perceptual hashing."""
        try:
            # Load and process image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not load image")
            
            # Extract CLIP features
            clip_features = self._extract_clip_features(image)
            
            # Extract perceptual hash
            perceptual_hash = self.image_fingerprint.extract_perceptual_hash(image_path)
            
            # Search in FAISS index
            features_np = np.array(clip_features).reshape(1, -1).astype('float32')
            scores, indices = self.image_index.search(features_np, top_k)
            
            # Filter and prepare results
            similar_items = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if score >= threshold and idx != -1:
                    similar_items.append({
                        'index': int(idx),
                        'similarity_score': float(score),
                        'content_type': 'image',
                        'match_type': 'visual_similarity',
                        'perceptual_hash': perceptual_hash,
                        'hash_distance': self._calculate_hash_distance(perceptual_hash, idx)
                    })
            
            return similar_items
            
        except Exception as e:
            logger.error(f"Error finding similar images: {e}")
            return []
    
    def _find_similar_videos(self, video_path: str, top_k: int, threshold: float) -> List[Dict[str, Any]]:
        """Find similar videos using frame analysis and temporal features."""
        try:
            # Extract video features (keyframes + temporal)
            video_features = self._extract_video_features(video_path)
            
            # Extract video fingerprint
            video_fingerprint = self.video_fingerprint.extract_fingerprint(video_path)
            
            # Search in FAISS index
            features_np = np.array(video_features).reshape(1, -1).astype('float32')
            scores, indices = self.video_index.search(features_np, top_k)
            
            # Filter and prepare results
            similar_items = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if score >= threshold and idx != -1:
                    similar_items.append({
                        'index': int(idx),
                        'similarity_score': float(score),
                        'content_type': 'video',
                        'match_type': 'video_similarity',
                        'fingerprint': video_fingerprint,
                        'temporal_match': self._compare_temporal_patterns(video_fingerprint, idx)
                    })
            
            return similar_items
            
        except Exception as e:
            logger.error(f"Error finding similar videos: {e}")
            return []
    
    def _find_similar_text(self, text_path: str, top_k: int, threshold: float) -> List[Dict[str, Any]]:
        """Find similar text using semantic embeddings."""
        try:
            # Read text content
            with open(text_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Extract text embeddings
            text_embeddings = self._extract_text_embeddings(text_content)
            
            # Extract text fingerprint
            text_fingerprint = self.text_fingerprint.extract_fingerprint(text_content)
            
            # Search in FAISS index
            features_np = np.array(text_embeddings).reshape(1, -1).astype('float32')
            scores, indices = self.text_index.search(features_np, top_k)
            
            # Filter and prepare results
            similar_items = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if score >= threshold and idx != -1:
                    similar_items.append({
                        'index': int(idx),
                        'similarity_score': float(score),
                        'content_type': 'text',
                        'match_type': 'semantic_similarity',
                        'fingerprint': text_fingerprint,
                        'exact_match_ratio': self._calculate_text_similarity(text_content, idx)
                    })
            
            return similar_items
            
        except Exception as e:
            logger.error(f"Error finding similar text: {e}")
            return []
    
    def _extract_audio_features(self, audio_path: str) -> np.ndarray:
        """Extract comprehensive audio features for similarity matching."""
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=22050)
            
            # Extract multiple feature types
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            chroma = librosa.feature.chroma(y=y, sr=sr)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
            
            # Combine features
            features = np.concatenate([
                np.mean(mfccs, axis=1),
                np.mean(chroma, axis=1),
                np.mean(spectral_centroid, axis=1),
                np.mean(spectral_rolloff, axis=1),
                np.mean(zero_crossing_rate, axis=1)
            ])
            
            # Pad or truncate to fixed size (512 dims)
            if len(features) < 512:
                features = np.pad(features, (0, 512 - len(features)))
            else:
                features = features[:512]
                
            return features
            
        except Exception as e:
            logger.error(f"Error extracting audio features: {e}")
            return np.zeros(512)
    
    def _extract_clip_features(self, image: np.ndarray) -> np.ndarray:
        """Extract CLIP features from image."""
        try:
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process with CLIP
            inputs = self.clip_processor(images=image_rgb, return_tensors="pt")
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                
            return image_features.numpy().flatten()
            
        except Exception as e:
            logger.error(f"Error extracting CLIP features: {e}")
            return np.zeros(512)
    
    def _extract_video_features(self, video_path: str) -> np.ndarray:
        """Extract video features from keyframes and temporal analysis."""
        try:
            cap = cv2.VideoCapture(video_path)
            
            # Extract keyframes
            keyframe_features = []
            frame_count = 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample frames uniformly
            frame_indices = np.linspace(0, total_frames-1, min(10, total_frames), dtype=int)
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if ret:
                    # Extract CLIP features from frame
                    clip_features = self._extract_clip_features(frame)
                    keyframe_features.append(clip_features)
            
            cap.release()
            
            # Average features across keyframes
            if keyframe_features:
                video_features = np.mean(keyframe_features, axis=0)
            else:
                video_features = np.zeros(512)
                
            return video_features
            
        except Exception as e:
            logger.error(f"Error extracting video features: {e}")
            return np.zeros(512)
    
    def _extract_text_embeddings(self, text: str) -> np.ndarray:
        """Extract semantic text embeddings."""
        try:
            # Tokenize text
            encoded = self.text_tokenizer(
                text, 
                truncation=True, 
                padding=True, 
                max_length=512, 
                return_tensors='pt'
            )
            
            # Extract embeddings
            with torch.no_grad():
                outputs = self.text_model(**encoded)
                # Use [CLS] token embedding
                embeddings = outputs.last_hidden_state[:, 0, :].numpy().flatten()
                
            return embeddings
            
        except Exception as e:
            logger.error(f"Error extracting text embeddings: {e}")
            return np.zeros(384)
    
    def _compare_audio_fingerprints(self, fingerprint1: str, index: int) -> float:
        """Compare audio fingerprints for exact matching."""
        # This would compare with stored fingerprint at index
        # Implementation depends on fingerprint storage format
        return 0.0
    
    def _calculate_hash_distance(self, hash1: str, index: int) -> int:
        """
Calculate Hamming distance between perceptual hashes."""
        # Implementation for hash comparison
        return 0
    
    def _compare_temporal_patterns(self, fingerprint: Dict, index: int) -> float:
        """
Compare temporal patterns in video fingerprints."""
        # Implementation for temporal pattern matching
        return 0.0
    
    def _calculate_text_similarity(self, text: str, index: int) -> float:
        """
Calculate exact text similarity ratio."""
        # Implementation for text similarity calculation
        return 0.0
    
    def add_content_to_index(
        self, 
        content_path: str, 
        content_type: str, 
        content_id: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
Add new content to similarity index."""
        try:
            if content_type == 'audio':
                features = self._extract_audio_features(content_path)
                self.audio_index.add(features.reshape(1, -1).astype('float32'))
            elif content_type == 'image':
                image = cv2.imread(content_path)
                features = self._extract_clip_features(image)
                self.image_index.add(features.reshape(1, -1).astype('float32'))
            elif content_type == 'video':
                features = self._extract_video_features(content_path)
                self.video_index.add(features.reshape(1, -1).astype('float32'))
            elif content_type == 'text':
                with open(content_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                features = self._extract_text_embeddings(text)
                self.text_index.add(features.reshape(1, -1).astype('float32'))
            
            logger.info(f"Added {content_type} content {content_id} to similarity index")
            return True
            
        except Exception as e:
            logger.error(f"Error adding content to index: {e}")
            return False
    
    def save_indexes(self) -> None:
        """Save FAISS indexes to disk."""
        try:
            index_path = Path(self.settings.VECTOR_DB_PATH)
            index_path.mkdir(parents=True, exist_ok=True)
            
            if self.audio_index:
                faiss.write_index(self.audio_index, str(index_path / 'audio_similarity.index'))
            if self.image_index:
                faiss.write_index(self.image_index, str(index_path / 'image_similarity.index'))
            if self.video_index:
                faiss.write_index(self.video_index, str(index_path / 'video_similarity.index'))
            if self.text_index:
                faiss.write_index(self.text_index, str(index_path / 'text_similarity.index'))
                
            logger.info("FAISS indexes saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving indexes: {e}")
    
    def get_similarity_stats(self) -> Dict[str, Any]:
        """Get statistics about similarity indexes."""
        return {
            'audio_index_size': self.audio_index.ntotal if self.audio_index else 0,
            'image_index_size': self.image_index.ntotal if self.image_index else 0,
            'video_index_size': self.video_index.ntotal if self.video_index else 0,
            'text_index_size': self.text_index.ntotal if self.text_index else 0,
            'thresholds': self.similarity_thresholds
        }
