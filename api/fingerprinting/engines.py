"""Advanced AI-Powered Content Fingerprinting Engine
================================================
Enterprise-grade fingerprinting system for multi-format content protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Team: IA-Influencer-Agent Expert Development Team

Business Logic Integration:
- Multi-format content analysis (audio, video, image, text)
- High-precision similarity detection using AI/ML models
- Vector embedding generation and matching via FAISS
- Real-time fingerprint generation and storage
- Cross-platform content protection and monitoring
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import logging
import asyncio
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Core imports
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_database_session
from backend.app.models.content import ContentFingerprint, ProtectionAlert
from backend.app.schemas.fingerprinting import (
    FingerprintRequest, FingerprintResponse, 
    SimilarityMatchResult, ContentAnalysisResult
)

# AI/ML imports for fingerprinting
import numpy as np
import cv2
import librosa
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
import imagehash
from PIL import Image
import hashlib
import faiss
import chromaprint
import essentia
import ffmpeg

logger = logging.getLogger(__name__)

@dataclass
class FingerprintConfig:
    """
Configuration for fingerprinting operations."""
    audio_sample_rate: int = 22050
    video_frame_rate: int = 30
    text_max_length: int = 512
    similarity_threshold: float = 0.85
    vector_dimensions: int = 512
    batch_size: int = 32


class BaseFingerprintEngine(ABC):
    """
Abstract base class for all fingerprinting engines."""
    
    def __init__(self, config: FingerprintConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def generate_fingerprint(self, content: bytes, metadata: Dict[str, Any]) -> str:
        """
Generate unique fingerprint for content."""
        pass
    
    @abstractmethod
    async def extract_features(self, content: bytes) -> np.ndarray:
        """
Extract feature vector from content."""
        pass
    
    @abstractmethod
    async def calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """
Calculate similarity score between two feature vectors."""
        pass


class AudioFingerprintEngine(BaseFingerprintEngine):
    """
Advanced audio fingerprinting using Chromaprint and Essentia."""
    
    def __init__(self, config: FingerprintConfig):
        super().__init__(config)
        self.chromaprint_analyzer = chromaprint.Chromaprint()
        self.essentia_analyzer = essentia.standard.ChromaCrossSimilarity()
    
    async def generate_fingerprint(self, audio_content: bytes, metadata: Dict[str, Any]) -> str:
        """
Generate audio fingerprint using advanced algorithms."""
        try:
            # Load audio data
            audio_data, sr = librosa.load(
                io.BytesIO(audio_content), 
                sr=self.config.audio_sample_rate
            )
            
            # Generate Chromaprint fingerprint
            chromaprint_hash = self.chromaprint_analyzer.compute(audio_data, sr)
            
            # Extract spectral features using Essentia
            spectral_features = self._extract_spectral_features(audio_data, sr)
            
            # Combine fingerprints
            combined_hash = hashlib.sha256(
                f"{chromaprint_hash}:{spectral_features}".encode()
            ).hexdigest()
            
            self.logger.info(f"Generated audio fingerprint: {combined_hash[:16]}...")
            return combined_hash
            
        except Exception as e:
            self.logger.error(f"Audio fingerprinting failed: {str(e)}")
            raise
    
    async def extract_features(self, audio_content: bytes) -> np.ndarray:
        """Extract comprehensive audio feature vector."""
        try:
            audio_data, sr = librosa.load(
                io.BytesIO(audio_content), 
                sr=self.config.audio_sample_rate
            )
            
            # Extract multiple audio features
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
            
            # Combine features into single vector
            features = np.concatenate([
                np.mean(mfcc, axis=1),
                np.mean(chroma, axis=1),
                np.mean(spectral_centroids),
                np.mean(zero_crossing_rate)
            ])
            
            # Normalize and pad/trim to fixed size
            features = self._normalize_vector(features, self.config.vector_dimensions)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Audio feature extraction failed: {str(e)}")
            raise
    
    def _extract_spectral_features(self, audio_data: np.ndarray, sr: int) -> str:
        """Extract spectral features using Essentia."""
        # Implementation for Essentia spectral analysis
        # This is a simplified version - full implementation would use
        # advanced spectral analysis techniques
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
        return hashlib.md5(str(np.mean(spectral_centroid)).encode()).hexdigest()
    
    def _normalize_vector(self, vector: np.ndarray, target_size: int) -> np.ndarray:
        """
Normalize and resize vector to target dimensions."""
        if len(vector) > target_size:
            return vector[:target_size]
        elif len(vector) < target_size:
            return np.pad(vector, (0, target_size - len(vector)), 'constant')
        return vector
    
    async def calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """
Calculate cosine similarity between audio features."""
        dot_product = np.dot(features1, features2)
        norms = np.linalg.norm(features1) * np.linalg.norm(features2)
        
        if norms == 0:
            return 0.0
        
        return dot_product / norms


class VideoFingerprintEngine(BaseFingerprintEngine):
    """
Advanced video fingerprinting using OpenCV and deep learning."""
    
    def __init__(self, config: FingerprintConfig):
        super().__init__(config)
        # Initialize YOLO for object detection (simplified)
        self.frame_extractor = cv2.VideoCapture()
    
    async def generate_fingerprint(self, video_content: bytes, metadata: Dict[str, Any]) -> str:
        """
Generate video fingerprint using frame analysis."""
        try:
            # Save temp video file for processing
            temp_path = f"/tmp/video_{hash(video_content)}.mp4"
            with open(temp_path, 'wb') as f:
                f.write(video_content)
            
            # Extract key frames
            frames = await self._extract_key_frames(temp_path)
            
            # Generate perceptual hashes for frames
            frame_hashes = []
            for frame in frames:
                frame_hash = self._generate_frame_hash(frame)
                frame_hashes.append(frame_hash)
            
            # Combine all frame hashes
            combined_hash = hashlib.sha256(
                ':'.join(frame_hashes).encode()
            ).hexdigest()
            
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)
            
            self.logger.info(f"Generated video fingerprint: {combined_hash[:16]}...")
            return combined_hash
            
        except Exception as e:
            self.logger.error(f"Video fingerprinting failed: {str(e)}")
            raise
    
    async def extract_features(self, video_content: bytes) -> np.ndarray:
        """Extract video feature vector from frames."""
        try:
            temp_path = f"/tmp/video_{hash(video_content)}.mp4"
            with open(temp_path, 'wb') as f:
                f.write(video_content)
            
            frames = await self._extract_key_frames(temp_path)
            
            # Extract features from each frame and combine
            frame_features = []
            for frame in frames:
                # Use OpenCV to extract visual features
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Extract HOG features
                hog = cv2.HOGDescriptor()
                hog_features = hog.compute(gray)
                
                if hog_features is not None:
                    frame_features.append(hog_features.flatten())
            
            # Combine all frame features
            if frame_features:
                combined_features = np.mean(frame_features, axis=0)
                combined_features = self._normalize_vector(
                    combined_features, 
                    self.config.vector_dimensions
                )
            else:
                combined_features = np.zeros(self.config.vector_dimensions)
            
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)
            
            return combined_features
            
        except Exception as e:
            self.logger.error(f"Video feature extraction failed: {str(e)}")
            raise
    
    async def _extract_key_frames(self, video_path: str, max_frames: int = 10) -> List[np.ndarray]:
        """Extract key frames from video."""
        cap = cv2.VideoCapture(video_path)
        frames = []
        
        if not cap.isOpened():
            return frames
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
        
        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
        
        cap.release()
        return frames
    
    def _generate_frame_hash(self, frame: np.ndarray) -> str:
        """
Generate perceptual hash for single frame."""
        # Convert frame to PIL Image for hashing
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # Generate multiple hash types for robustness
        ahash = str(imagehash.average_hash(pil_image))
        phash = str(imagehash.phash(pil_image))
        dhash = str(imagehash.dhash(pil_image))
        
        # Combine hashes
        combined = f"{ahash}:{phash}:{dhash}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _normalize_vector(self, vector: np.ndarray, target_size: int) -> np.ndarray:
        """Normalize and resize vector to target dimensions."""
        if len(vector) > target_size:
            return vector[:target_size]
        elif len(vector) < target_size:
            return np.pad(vector, (0, target_size - len(vector)), 'constant')
        return vector
    
    async def calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """
Calculate cosine similarity between video features."""
        dot_product = np.dot(features1, features2)
        norms = np.linalg.norm(features1) * np.linalg.norm(features2)
        
        if norms == 0:
            return 0.0
        
        return dot_product / norms


class ImageFingerprintEngine(BaseFingerprintEngine):
    """
Advanced image fingerprinting using CLIP and perceptual hashing."""
    
    def __init__(self, config: FingerprintConfig):
        super().__init__(config)
        # Initialize CLIP model for semantic understanding
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    async def generate_fingerprint(self, image_content: bytes, metadata: Dict[str, Any]) -> str:
        """Generate image fingerprint using multiple hash algorithms."""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_content))
            
            # Generate multiple hash types for robustness
            average_hash = str(imagehash.average_hash(image))
            perceptual_hash = str(imagehash.phash(image))
            difference_hash = str(imagehash.dhash(image))
            wavelet_hash = str(imagehash.whash(image))
            
            # Combine all hashes
            combined_hash = hashlib.sha256(
                f"{average_hash}:{perceptual_hash}:{difference_hash}:{wavelet_hash}".encode()
            ).hexdigest()
            
            self.logger.info(f"Generated image fingerprint: {combined_hash[:16]}...")
            return combined_hash
            
        except Exception as e:
            self.logger.error(f"Image fingerprinting failed: {str(e)}")
            raise
    
    async def extract_features(self, image_content: bytes) -> np.ndarray:
        """Extract semantic image features using CLIP."""
        try:
            # Load and preprocess image
            image = Image.open(io.BytesIO(image_content))
            inputs = self.clip_processor(images=image, return_tensors="pt")
            
            # Extract CLIP features
            image_features = self.clip_model.get_image_features(**inputs)
            
            # Convert to numpy and normalize
            features = image_features.detach().numpy().flatten()
            features = self._normalize_vector(features, self.config.vector_dimensions)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Image feature extraction failed: {str(e)}")
            raise
    
    def _normalize_vector(self, vector: np.ndarray, target_size: int) -> np.ndarray:
        """Normalize and resize vector to target dimensions."""
        if len(vector) > target_size:
            return vector[:target_size]
        elif len(vector) < target_size:
            return np.pad(vector, (0, target_size - len(vector)), 'constant')
        return vector
    
    async def calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """
Calculate cosine similarity between image features."""
        dot_product = np.dot(features1, features2)
        norms = np.linalg.norm(features1) * np.linalg.norm(features2)
        
        if norms == 0:
            return 0.0
        
        return dot_product / norms


class TextFingerprintEngine(BaseFingerprintEngine):
    """
Advanced text fingerprinting using transformer models."""
    
    def __init__(self, config: FingerprintConfig):
        super().__init__(config)
        # Initialize sentence transformer for semantic similarity
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def generate_fingerprint(self, text_content: bytes, metadata: Dict[str, Any]) -> str:
        """
Generate text fingerprint using content hashing."""
        try:
            text = text_content.decode('utf-8')
            
            # Normalize text (remove whitespace, convert to lowercase)
            normalized_text = ' '.join(text.lower().split())
            
            # Generate multiple hashes for different granularities
            full_hash = hashlib.sha256(normalized_text.encode()).hexdigest()
            word_hash = hashlib.md5(' '.join(sorted(normalized_text.split())).encode()).hexdigest()
            
            # Combine hashes
            combined_hash = hashlib.sha256(f"{full_hash}:{word_hash}".encode()).hexdigest()
            
            self.logger.info(f"Generated text fingerprint: {combined_hash[:16]}...")
            return combined_hash
            
        except Exception as e:
            self.logger.error(f"Text fingerprinting failed: {str(e)}")
            raise
    
    async def extract_features(self, text_content: bytes) -> np.ndarray:
        """Extract semantic text features using sentence transformers."""
        try:
            text = text_content.decode('utf-8')
            
            # Truncate text if too long
            if len(text) > self.config.text_max_length:
                text = text[:self.config.text_max_length]
            
            # Generate semantic embeddings
            embeddings = self.sentence_model.encode([text])
            features = embeddings[0]
            
            # Normalize to target dimensions
            features = self._normalize_vector(features, self.config.vector_dimensions)
            
            return features
            
        except Exception as e:
            self.logger.error(f"Text feature extraction failed: {str(e)}")
            raise
    
    def _normalize_vector(self, vector: np.ndarray, target_size: int) -> np.ndarray:
        """Normalize and resize vector to target dimensions."""
        if len(vector) > target_size:
            return vector[:target_size]
        elif len(vector) < target_size:
            return np.pad(vector, (0, target_size - len(vector)), 'constant')
        return vector
    
    async def calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """
Calculate cosine similarity between text features."""
        dot_product = np.dot(features1, features2)
        norms = np.linalg.norm(features1) * np.linalg.norm(features2)
        
        if norms == 0:
            return 0.0
        
        return dot_product / norms


class UniversalFingerprintEngine:
    """
Unified engine for all content types with FAISS integration."""
    
    def __init__(self, config: Optional[FingerprintConfig] = None):
        self.config = config or FingerprintConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize specialized engines
        self.audio_engine = AudioFingerprintEngine(self.config)
        self.video_engine = VideoFingerprintEngine(self.config)
        self.image_engine = ImageFingerprintEngine(self.config)
        self.text_engine = TextFingerprintEngine(self.config)
        
        # Initialize FAISS index for vector similarity search
        self.faiss_index = faiss.IndexFlatIP(self.config.vector_dimensions)
        self.content_mapping = {}  # Maps FAISS IDs to content IDs
    
    async def process_content(
        self, 
        content: bytes, 
        content_type: str, 
        metadata: Dict[str, Any]
    ) -> ContentAnalysisResult:
        """
Process content and generate comprehensive fingerprint analysis."""
        try:
            # Select appropriate engine based on content type
            engine = self._get_engine_for_type(content_type)
            
            if not engine:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Generate fingerprint
            fingerprint_hash = await engine.generate_fingerprint(content, metadata)
            
            # Extract feature vector
            features = await engine.extract_features(content)
            
            # Check for similar content using FAISS
            similar_matches = await self._find_similar_content(features, content_type)
            
            result = ContentAnalysisResult(
                fingerprint_hash=fingerprint_hash,
                content_type=content_type,
                features=features.tolist(),
                similarity_matches=similar_matches,
                analysis_metadata=metadata
            )
            
            self.logger.info(f"Content analysis completed for {content_type}")
            return result
            
        except Exception as e:
            self.logger.error(f"Content processing failed: {str(e)}")
            raise
    
    async def add_to_index(self, content_id: int, features: np.ndarray) -> None:
        """Add content features to FAISS index for similarity search."""
        try:
            # Normalize features for cosine similarity
            features_normalized = features / np.linalg.norm(features)
            features_array = features_normalized.reshape(1, -1).astype('float32')
            
            # Add to FAISS index
            faiss_id = self.faiss_index.ntotal
            self.faiss_index.add(features_array)
            
            # Map FAISS ID to content ID
            self.content_mapping[faiss_id] = content_id
            
            self.logger.debug(f"Added content {content_id} to FAISS index")
            
        except Exception as e:
            self.logger.error(f"Failed to add to index: {str(e)}")
            raise
    
    async def _find_similar_content(
        self, 
        query_features: np.ndarray, 
        content_type: str,
        top_k: int = 10
    ) -> List[SimilarityMatchResult]:
        """Find similar content using FAISS vector similarity search."""
        try:
            if self.faiss_index.ntotal == 0:
                return []
            
            # Normalize query features
            query_normalized = query_features / np.linalg.norm(query_features)
            query_array = query_normalized.reshape(1, -1).astype('float32')
            
            # Search for similar vectors
            scores, indices = self.faiss_index.search(query_array, top_k)
            
            matches = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx != -1 and score > self.config.similarity_threshold:
                    content_id = self.content_mapping.get(idx)
                    if content_id:
                        matches.append(SimilarityMatchResult(
                            content_id=content_id,
                            similarity_score=float(score),
                            rank=i + 1
                        ))
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Similar content search failed: {str(e)}")
            return []
    
    def _get_engine_for_type(self, content_type: str) -> Optional[BaseFingerprintEngine]:
        """Get appropriate fingerprinting engine for content type."""
        type_mapping = {
            'audio': self.audio_engine,
            'video': self.video_engine,
            'image': self.image_engine,
            'text': self.text_engine
        }
        
        return type_mapping.get(content_type.lower())


# Export classes for use in other modules
__all__ = [
    'FingerprintConfig',
    'BaseFingerprintEngine', 
    'AudioFingerprintEngine',
    'VideoFingerprintEngine', 
    'ImageFingerprintEngine',
    'TextFingerprintEngine',
    'UniversalFingerprintEngine'
]
