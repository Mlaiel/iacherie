"""Advanced Content Detector - AI-Powered Content Analysis & Similarity Detection

Industrial content detection system with multi-modal analysis, fingerprinting,
and similarity matching for content protection and infringement detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""
import asyncio
import logging
import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
import cv2
from PIL import Image, ImageHash
import imagehash
import librosa
import soundfile as sf
from textblob import TextBlob
import spacy
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import faiss
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import ContentDetectionError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ContentDetectionError, ValidationError = globals().get('ContentDetectionError, ValidationError', Exception)
from ...ml.embeddings import ContentEmbeddings
from ...ml.feature_extraction import FeatureExtractor
from ...security.content_fingerprint import ContentFingerprint
from ...utils.file_handler import FileHandler
from ...utils.preprocessing import TextPreprocessor

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Supported content types for detection"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    CODE = "code"
    MIXED = "mixed"

class SimilarityMethod(Enum):
    """Similarity calculation methods"""
    COSINE = "cosine"
    JACCARD = "jaccard"
    EUCLIDEAN = "euclidean"
    HAMMING = "hamming"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    PERCEPTUAL = "perceptual"

class DetectionLevel(Enum):
    """Detection sensitivity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

@dataclass
class ContentSignature:
    """Comprehensive content signature for matching"""
    content_id: str
    content_type: ContentType
    
    # Text signatures
    text_hash: str = ""
    semantic_embedding: Optional[np.ndarray] = None
    tfidf_features: Optional[np.ndarray] = None
    structural_features: Dict[str, float] = field(default_factory=dict)
    
    # Image signatures
    image_hash: str = ""
    image_features: Optional[np.ndarray] = None
    color_histogram: Optional[np.ndarray] = None
    
    # Audio signatures
    audio_fingerprint: str = ""
    mfcc_features: Optional[np.ndarray] = None
    spectral_features: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    language: str = ""
    quality_score: float = 0.0
    creation_timestamp: datetime = field(default_factory=datetime.now)
    update_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SimilarityResult:
    """Similarity detection result"""
    content_id_1: str
    content_id_2: str
    similarity_score: float
    similarity_method: SimilarityMethod
    content_type: ContentType
    
    # Detailed scores
    text_similarity: float = 0.0
    semantic_similarity: float = 0.0
    structural_similarity: float = 0.0
    visual_similarity: float = 0.0
    audio_similarity: float = 0.0
    
    # Analysis details
    matching_segments: List[Dict] = field(default_factory=list)
    differences: List[Dict] = field(default_factory=list)
    confidence_score: float = 0.0
    
    # Metadata
    detection_timestamp: datetime = field(default_factory=datetime.now)
    processing_time_ms: float = 0.0

@dataclass
class DetectionConfig:
    """Content detection configuration"""
    detection_level: DetectionLevel = DetectionLevel.HIGH
    similarity_threshold: float = 0.7
    enable_semantic_analysis: bool = True
    enable_structural_analysis: bool = True
    enable_perceptual_hashing: bool = True
    
    # Text analysis
    use_embeddings: bool = True
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_text_length: int = 10000
    
    # Image analysis
    image_hash_size: int = 16
    color_histogram_bins: int = 256
    enable_deep_features: bool = True
    
    # Audio analysis
    sample_rate: int = 22050
    n_mfcc: int = 13
    hop_length: int = 512
    
    # Performance
    batch_size: int = 32
    max_concurrent_operations: int = 4

class ContentDetector:
    """
    Advanced Content Detector for Multi-Modal Similarity Analysis
    
    Provides comprehensive content detection capabilities including text, image,
    and audio similarity detection with AI-powered analysis and fingerprinting.
    """
    
    def __init__(self, config: Optional[DetectionConfig] = None):
        self.config = config or DetectionConfig()
        
        # Initialize components
        self.content_fingerprint = ContentFingerprint()
        self.text_preprocessor = TextPreprocessor()
        self.feature_extractor = FeatureExtractor()
        self.content_embeddings = ContentEmbeddings()
        self.file_handler = FileHandler()
        
        # ML models and tools
        self.sentence_transformer = None
        self.nlp_model = None
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.95
        )
        
        # Storage for signatures and indices
        self.content_signatures: Dict[str, ContentSignature] = {}
        self.text_index: Optional[faiss.Index] = None
        self.image_index: Optional[faiss.Index] = None
        
        # Statistics
        self.detection_stats = {
            'signatures_created': 0,
            'comparisons_performed': 0,
            'matches_found': 0,
            'average_processing_time': 0.0
        }
        
        logger.info("Content Detector initialized")

    async def initialize(self) -> None:
        """Initialize content detection models and indices"""
        try:
            # Download required NLTK data
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
            except:
                logger.warning("Failed to download NLTK data")
            
            # Initialize sentence transformer for embeddings
            if self.config.use_embeddings:
                self.sentence_transformer = SentenceTransformer(self.config.embedding_model)
                logger.info(f"Loaded sentence transformer: {self.config.embedding_model}")
            
            # Initialize spaCy for advanced NLP
            try:
                self.nlp_model = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy English model not found. Installing...")
                # In production, models should be pre-installed
                self.nlp_model = None
            
            # Initialize FAISS indices
            self._initialize_faiss_indices()
            
            logger.info("Content Detector initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Content Detector: {str(e)}")
            raise ContentDetectionError(f"Initialization failed: {str(e)}")

    def _initialize_faiss_indices(self) -> None:
        """Initialize FAISS indices for fast similarity search"""
        # Text embeddings index (assuming 384-dimensional embeddings)
        embedding_dim = 384
        self.text_index = faiss.IndexFlatIP(embedding_dim)  # Inner product for cosine similarity
        
        # Image features index (assuming 2048-dimensional features)
        image_dim = 2048
        self.image_index = faiss.IndexFlatL2(image_dim)  # L2 distance for image features

    async def create_content_signature(self, content: Union[str, bytes], content_type: ContentType,
                                     content_id: Optional[str] = None, metadata: Dict = None) -> ContentSignature:
        """Create comprehensive content signature"""
        start_time = time.time()
        
        try:
            # Generate content ID if not provided
            if not content_id:
                content_hash = hashlib.sha256(
                    content.encode() if isinstance(content, str) else content
                ).hexdigest()
                content_id = f"{content_type.value}_{content_hash[:12]}"
            
            signature = ContentSignature(
                content_id=content_id,
                content_type=content_type
            )
            
            # Create type-specific signatures
            if content_type == ContentType.TEXT:
                await self._create_text_signature(content, signature)
            elif content_type == ContentType.IMAGE:
                await self._create_image_signature(content, signature)
            elif content_type == ContentType.AUDIO:
                await self._create_audio_signature(content, signature)
            elif content_type == ContentType.MIXED:
                await self._create_mixed_signature(content, signature)
            
            # Add to storage and indices
            self.content_signatures[content_id] = signature
            await self._add_to_indices(signature)
            
            # Update statistics
            self.detection_stats['signatures_created'] += 1
            processing_time = (time.time() - start_time) * 1000
            self._update_average_processing_time(processing_time)
            
            logger.debug(f"Created signature for {content_id} in {processing_time:.2f}ms")
            
            return signature
            
        except Exception as e:
            logger.error(f"Failed to create content signature: {str(e)}")
            raise ContentDetectionError(f"Signature creation failed: {str(e)}")

    async def _create_text_signature(self, text: str, signature: ContentSignature) -> None:
        """Create text-specific signature components"""
        # Basic text hash
        signature.text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Preprocess text
        cleaned_text = self.text_preprocessor.clean_text(text)
        if len(cleaned_text) > self.config.max_text_length:
            cleaned_text = cleaned_text[:self.config.max_text_length]
        
        # Semantic embedding
        if self.config.use_embeddings and self.sentence_transformer:
            embedding = self.sentence_transformer.encode(cleaned_text)
            signature.semantic_embedding = embedding.astype(np.float32)
        
        # TF-IDF features
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([cleaned_text])
            signature.tfidf_features = tfidf_matrix.toarray()[0].astype(np.float32)
        except:
            logger.warning("Failed to create TF-IDF features")
        
        # Structural features
        signature.structural_features = self._extract_text_structural_features(text)
        
        # Language detection
        try:
            blob = TextBlob(cleaned_text)
            signature.language = blob.detect_language()
        except:
            signature.language = "unknown"
        
        # Quality score
        signature.quality_score = self._calculate_text_quality(text)

    def _extract_text_structural_features(self, text: str) -> Dict[str, float]:
        """Extract structural features from text"""
        features = {}
        
        # Basic metrics
        features['length'] = len(text)
        features['word_count'] = len(text.split())
        features['sentence_count'] = len(sent_tokenize(text))
        features['paragraph_count'] = len(text.split('\n\n'))
        
        # Character distribution
        features['uppercase_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        features['digit_ratio'] = sum(1 for c in text if c.isdigit()) / len(text) if text else 0
        features['punctuation_ratio'] = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text) if text else 0
        
        # Linguistic features
        words = word_tokenize(text.lower())
        features['avg_word_length'] = np.mean([len(word) for word in words]) if words else 0
        features['unique_word_ratio'] = len(set(words)) / len(words) if words else 0
        
        # Readability approximation (simplified)
        if features['sentence_count'] > 0:
            features['avg_words_per_sentence'] = features['word_count'] / features['sentence_count']
        else:
            features['avg_words_per_sentence'] = 0
        
        # Special patterns
        features['url_count'] = len(re.findall(r'https?://\S+', text))
        features['email_count'] = len(re.findall(r'\S+@\S+\.\S+', text))
        features['hashtag_count'] = len(re.findall(r'#\w+', text))
        
        return features

    def _calculate_text_quality(self, text: str) -> float:
        """Calculate text quality score"""
        if not text:
            return 0.0
        
        score = 0.0
        
        # Length factor
        if 100 <= len(text) <= 10000:
            score += 0.3
        elif 50 <= len(text) <= 20000:
            score += 0.2
        
        # Structure factor
        sentences = sent_tokenize(text)
        if len(sentences) >= 3:
            score += 0.2
        
        # Language quality
        try:
            blob = TextBlob(text)
            # Check for proper sentence structure
            if blob.sentiment.subjectivity < 0.8:  # More objective text
                score += 0.2
        except:
            pass
        
        # Grammar and spelling approximation
        words = word_tokenize(text)
        if words:
            # Simple heuristic: ratio of dictionary words
            try:
                english_words = set(nltk.corpus.words.words())
                known_words = sum(1 for word in words if word.lower() in english_words)
                score += 0.3 * (known_words / len(words))
            except:
                score += 0.15  # Fallback score
        
        return min(score, 1.0)

    async def _create_image_signature(self, image_data: bytes, signature: ContentSignature) -> None:
        """Create image-specific signature components"""
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Perceptual hash
            if self.config.enable_perceptual_hashing:
                phash = imagehash.phash(image, hash_size=self.config.image_hash_size)
                signature.image_hash = str(phash)
            
            # Color histogram
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            histogram = np.array(image.histogram())
            signature.color_histogram = histogram.astype(np.float32)
            
            # Deep features (if enabled)
            if self.config.enable_deep_features:
                signature.image_features = await self._extract_deep_image_features(image)
            
        except Exception as e:
            logger.error(f"Failed to create image signature: {str(e)}")

    async def _extract_deep_image_features(self, image: Image.Image) -> np.ndarray:
        """Extract deep features from image using pre-trained model"""
        try:
            # Convert PIL image to numpy array
            img_array = np.array(image.resize((224, 224)))
            
            # Normalize
            img_array = img_array.astype(np.float32) / 255.0
            
            # Simple feature extraction (in production, use ResNet/VGG features)
            # This is a placeholder - implement actual deep feature extraction
            features = np.mean(img_array.reshape(-1, 3), axis=0)
            return features.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Deep feature extraction failed: {str(e)}")
            return np.zeros(2048, dtype=np.float32)

    async def _create_audio_signature(self, audio_data: bytes, signature: ContentSignature) -> None:
        """Create audio-specific signature components"""
        try:
            # Load audio data
            # This is a placeholder - implement actual audio loading
            # audio, sr = librosa.load(io.BytesIO(audio_data), sr=self.config.sample_rate)
            
            # For now, create a simple fingerprint
            signature.audio_fingerprint = hashlib.sha256(audio_data).hexdigest()
            
            # MFCC features (placeholder)
            # mfcc = librosa.feature.mfcc(audio, sr=sr, n_mfcc=self.config.n_mfcc)
            # signature.mfcc_features = mfcc.mean(axis=1).astype(np.float32)
            
            # Spectral features (placeholder)
            signature.spectral_features = {
                'duration': 0.0,  # len(audio) / sr
                'energy': 0.0,
                'zero_crossing_rate': 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to create audio signature: {str(e)}")

    async def _create_mixed_signature(self, content: Dict, signature: ContentSignature) -> None:
        """Create signature for mixed content types"""
        # Handle mixed content by processing each component
        if 'text' in content:
            await self._create_text_signature(content['text'], signature)
        
        if 'image' in content:
            await self._create_image_signature(content['image'], signature)
        
        if 'audio' in content:
            await self._create_audio_signature(content['audio'], signature)

    async def _add_to_indices(self, signature: ContentSignature) -> None:
        """Add signature to FAISS indices for fast retrieval"""
        try:
            # Add text embeddings to index
            if signature.semantic_embedding is not None and self.text_index is not None:
                # Normalize for cosine similarity
                embedding = signature.semantic_embedding.reshape(1, -1)
                embedding = embedding / np.linalg.norm(embedding)
                self.text_index.add(embedding)
            
            # Add image features to index
            if signature.image_features is not None and self.image_index is not None:
                features = signature.image_features.reshape(1, -1)
                self.image_index.add(features)
                
        except Exception as e:
            logger.error(f"Failed to add signature to indices: {str(e)}")

    async def calculate_similarity(self, content_id_1: str, content_id_2: str,
                                 method: SimilarityMethod = SimilarityMethod.SEMANTIC) -> Optional[SimilarityResult]:
        """Calculate similarity between two content items"""
        start_time = time.time()
        
        try:
            # Get signatures
            sig1 = self.content_signatures.get(content_id_1)
            sig2 = self.content_signatures.get(content_id_2)
            
            if not sig1 or not sig2:
                return None
            
            if sig1.content_type != sig2.content_type:
                logger.warning(f"Comparing different content types: {sig1.content_type} vs {sig2.content_type}")
            
            # Calculate similarity based on method and content type
            similarity_score = 0.0
            result = SimilarityResult(
                content_id_1=content_id_1,
                content_id_2=content_id_2,
                similarity_score=0.0,
                similarity_method=method,
                content_type=sig1.content_type
            )
            
            if sig1.content_type == ContentType.TEXT:
                result = await self._calculate_text_similarity(sig1, sig2, method, result)
            elif sig1.content_type == ContentType.IMAGE:
                result = await self._calculate_image_similarity(sig1, sig2, method, result)
            elif sig1.content_type == ContentType.AUDIO:
                result = await self._calculate_audio_similarity(sig1, sig2, method, result)
            
            # Calculate confidence score
            result.confidence_score = self._calculate_confidence_score(result)
            
            # Update statistics
            self.detection_stats['comparisons_performed'] += 1
            if result.similarity_score > self.config.similarity_threshold:
                self.detection_stats['matches_found'] += 1
            
            # Set processing time
            result.processing_time_ms = (time.time() - start_time) * 1000
            self._update_average_processing_time(result.processing_time_ms)
            
            return result
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {str(e)}")
            raise ContentDetectionError(f"Similarity calculation failed: {str(e)}")

    async def _calculate_text_similarity(self, sig1: ContentSignature, sig2: ContentSignature,
                                       method: SimilarityMethod, result: SimilarityResult) -> SimilarityResult:
        """Calculate text similarity using various methods"""
        
        # Semantic similarity using embeddings
        if method == SimilarityMethod.SEMANTIC and sig1.semantic_embedding is not None and sig2.semantic_embedding is not None:
            semantic_sim = cosine_similarity([sig1.semantic_embedding], [sig2.semantic_embedding])[0][0]
            result.semantic_similarity = float(semantic_sim)
            result.similarity_score = semantic_sim
        
        # TF-IDF cosine similarity
        elif method == SimilarityMethod.COSINE and sig1.tfidf_features is not None and sig2.tfidf_features is not None:
            cosine_sim = cosine_similarity([sig1.tfidf_features], [sig2.tfidf_features])[0][0]
            result.text_similarity = float(cosine_sim)
            result.similarity_score = cosine_sim
        
        # Structural similarity
        elif method == SimilarityMethod.STRUCTURAL:
            structural_sim = self._calculate_structural_similarity(
                sig1.structural_features, sig2.structural_features
            )
            result.structural_similarity = structural_sim
            result.similarity_score = structural_sim
        
        # Jaccard similarity (simple word overlap)
        elif method == SimilarityMethod.JACCARD:
            # This would require access to original text - placeholder
            result.similarity_score = 0.5  # Placeholder
        
        # Combined similarity (default)
        else:
            # Combine multiple similarity measures
            similarities = []
            
            if sig1.semantic_embedding is not None and sig2.semantic_embedding is not None:
                semantic_sim = cosine_similarity([sig1.semantic_embedding], [sig2.semantic_embedding])[0][0]
                result.semantic_similarity = float(semantic_sim)
                similarities.append(semantic_sim)
            
            if sig1.tfidf_features is not None and sig2.tfidf_features is not None:
                cosine_sim = cosine_similarity([sig1.tfidf_features], [sig2.tfidf_features])[0][0]
                result.text_similarity = float(cosine_sim)
                similarities.append(cosine_sim)
            
            structural_sim = self._calculate_structural_similarity(
                sig1.structural_features, sig2.structural_features
            )
            result.structural_similarity = structural_sim
            similarities.append(structural_sim)
            
            # Weighted average
            if similarities:
                weights = [0.5, 0.3, 0.2][:len(similarities)]  # Prioritize semantic similarity
                result.similarity_score = sum(w * s for w, s in zip(weights, similarities)) / sum(weights)
        
        return result

    def _calculate_structural_similarity(self, features1: Dict[str, float], features2: Dict[str, float]) -> float:
        """Calculate structural similarity between text features"""
        if not features1 or not features2:
            return 0.0
        
        # Get common features
        common_features = set(features1.keys()) & set(features2.keys())
        if not common_features:
            return 0.0
        
        # Calculate normalized differences
        similarities = []
        for feature in common_features:
            val1, val2 = features1[feature], features2[feature]
            
            # Handle zero values
            if val1 == 0 and val2 == 0:
                similarities.append(1.0)
            elif val1 == 0 or val2 == 0:
                similarities.append(0.0)
            else:
                # Normalized difference
                diff = abs(val1 - val2) / max(val1, val2)
                similarities.append(1.0 - diff)
        
        return np.mean(similarities) if similarities else 0.0

    async def _calculate_image_similarity(self, sig1: ContentSignature, sig2: ContentSignature,
                                        method: SimilarityMethod, result: SimilarityResult) -> SimilarityResult:
        """Calculate image similarity"""
        
        # Perceptual hash similarity
        if sig1.image_hash and sig2.image_hash:
            try:
                hash1 = imagehash.hex_to_hash(sig1.image_hash)
                hash2 = imagehash.hex_to_hash(sig2.image_hash)
                hash_diff = hash1 - hash2
                # Convert to similarity (0-1 scale)
                max_diff = len(sig1.image_hash) * 4  # Max possible difference for hex hash
                visual_sim = 1.0 - (hash_diff / max_diff)
                result.visual_similarity = visual_sim
                result.similarity_score = visual_sim
            except:
                result.visual_similarity = 0.0
        
        # Color histogram similarity
        if sig1.color_histogram is not None and sig2.color_histogram is not None:
            # Normalize histograms
            hist1_norm = sig1.color_histogram / np.sum(sig1.color_histogram)
            hist2_norm = sig2.color_histogram / np.sum(sig2.color_histogram)
            
            # Calculate correlation
            correlation = np.corrcoef(hist1_norm, hist2_norm)[0, 1]
            color_sim = (correlation + 1) / 2  # Normalize to 0-1
            
            # Combine with visual similarity
            if result.visual_similarity > 0:
                result.similarity_score = (result.visual_similarity + color_sim) / 2
            else:
                result.similarity_score = color_sim
        
        # Deep features similarity
        if sig1.image_features is not None and sig2.image_features is not None:
            deep_sim = cosine_similarity([sig1.image_features], [sig2.image_features])[0][0]
            
            # Combine with other similarities
            similarities = [s for s in [result.visual_similarity, result.similarity_score, deep_sim] if s > 0]
            if similarities:
                result.similarity_score = np.mean(similarities)
        
        return result

    async def _calculate_audio_similarity(self, sig1: ContentSignature, sig2: ContentSignature,
                                        method: SimilarityMethod, result: SimilarityResult) -> SimilarityResult:
        """Calculate audio similarity"""
        
        # Fingerprint similarity (exact match)
        if sig1.audio_fingerprint and sig2.audio_fingerprint:
            if sig1.audio_fingerprint == sig2.audio_fingerprint:
                result.audio_similarity = 1.0
                result.similarity_score = 1.0
            else:
                result.audio_similarity = 0.0
                result.similarity_score = 0.0
        
        # MFCC features similarity
        if sig1.mfcc_features is not None and sig2.mfcc_features is not None:
            mfcc_sim = cosine_similarity([sig1.mfcc_features], [sig2.mfcc_features])[0][0]
            result.audio_similarity = float(mfcc_sim)
            result.similarity_score = max(result.similarity_score, mfcc_sim)
        
        return result

    def _calculate_confidence_score(self, result: SimilarityResult) -> float:
        """Calculate confidence score for similarity result"""
        confidence = 0.0
        
        # Higher confidence for multiple similarity measures
        active_measures = sum(1 for score in [
            result.text_similarity, result.semantic_similarity, result.structural_similarity,
            result.visual_similarity, result.audio_similarity
        ] if score > 0)
        
        confidence += min(0.4, active_measures * 0.1)
        
        # Higher confidence for extreme similarity scores
        if result.similarity_score > 0.9 or result.similarity_score < 0.1:
            confidence += 0.3
        elif result.similarity_score > 0.8 or result.similarity_score < 0.2:
            confidence += 0.2
        
        # Content type specific adjustments
        if result.content_type == ContentType.TEXT:
            if result.semantic_similarity > 0:
                confidence += 0.2
        elif result.content_type == ContentType.IMAGE:
            if result.visual_similarity > 0:
                confidence += 0.2
        
        return min(confidence, 1.0)

    async def find_similar_content(self, query_content_id: str, max_results: int = 10,
                                 similarity_threshold: float = None) -> List[SimilarityResult]:
        """Find similar content using FAISS indices for fast search"""
        threshold = similarity_threshold or self.config.similarity_threshold
        
        query_signature = self.content_signatures.get(query_content_id)
        if not query_signature:
            return []
        
        similar_results = []
        
        try:
            # Search in appropriate index
            if query_signature.content_type == ContentType.TEXT and query_signature.semantic_embedding is not None:
                similar_results = await self._search_text_index(query_signature, max_results, threshold)
            elif query_signature.content_type == ContentType.IMAGE and query_signature.image_features is not None:
                similar_results = await self._search_image_index(query_signature, max_results, threshold)
            
            # Fallback to brute force search
            if not similar_results:
                similar_results = await self._brute_force_similarity_search(query_content_id, max_results, threshold)
            
        except Exception as e:
            logger.error(f"Similar content search failed: {str(e)}")
        
        return sorted(similar_results, key=lambda x: x.similarity_score, reverse=True)

    async def _search_text_index(self, query_signature: ContentSignature, max_results: int, threshold: float) -> List[SimilarityResult]:
        """Search text index for similar embeddings"""
        results = []
        
        if self.text_index is None or query_signature.semantic_embedding is None:
            return results
        
        try:
            # Normalize query embedding
            query_embedding = query_signature.semantic_embedding.reshape(1, -1)
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            # Search index
            scores, indices = self.text_index.search(query_embedding, max_results + 1)  # +1 to account for self
            
            # Convert to similarity results
            signature_list = list(self.content_signatures.values())
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(signature_list) and score >= threshold:
                    candidate_sig = signature_list[idx]
                    if candidate_sig.content_id != query_signature.content_id:  # Skip self
                        result = SimilarityResult(
                            content_id_1=query_signature.content_id,
                            content_id_2=candidate_sig.content_id,
                            similarity_score=float(score),
                            similarity_method=SimilarityMethod.SEMANTIC,
                            content_type=query_signature.content_type,
                            semantic_similarity=float(score)
                        )
                        results.append(result)
            
        except Exception as e:
            logger.error(f"Text index search failed: {str(e)}")
        
        return results

    async def _search_image_index(self, query_signature: ContentSignature, max_results: int, threshold: float) -> List[SimilarityResult]:
        """Search image index for similar features"""
        results = []
        
        if self.image_index is None or query_signature.image_features is None:
            return results
        
        try:
            # Search index (L2 distance)
            distances, indices = self.image_index.search(
                query_signature.image_features.reshape(1, -1), 
                max_results + 1
            )
            
            # Convert distances to similarities
            signature_list = list(self.content_signatures.values())
            for distance, idx in zip(distances[0], indices[0]):
                if idx < len(signature_list):
                    # Convert L2 distance to similarity score
                    similarity = 1.0 / (1.0 + distance)
                    if similarity >= threshold:
                        candidate_sig = signature_list[idx]
                        if candidate_sig.content_id != query_signature.content_id:
                            result = SimilarityResult(
                                content_id_1=query_signature.content_id,
                                content_id_2=candidate_sig.content_id,
                                similarity_score=similarity,
                                similarity_method=SimilarityMethod.PERCEPTUAL,
                                content_type=query_signature.content_type,
                                visual_similarity=similarity
                            )
                            results.append(result)
            
        except Exception as e:
            logger.error(f"Image index search failed: {str(e)}")
        
        return results

    async def _brute_force_similarity_search(self, query_content_id: str, max_results: int, threshold: float) -> List[SimilarityResult]:
        """Brute force similarity search as fallback"""
        results = []
        
        for content_id, signature in self.content_signatures.items():
            if content_id != query_content_id:
                similarity_result = await self.calculate_similarity(
                    query_content_id, content_id, SimilarityMethod.SEMANTIC
                )
                
                if similarity_result and similarity_result.similarity_score >= threshold:
                    results.append(similarity_result)
                
                if len(results) >= max_results:
                    break
        
        return results

    def _update_average_processing_time(self, processing_time: float) -> None:
        """Update average processing time statistics"""
        total_operations = self.detection_stats['signatures_created'] + self.detection_stats['comparisons_performed']
        if total_operations > 0:
            self.detection_stats['average_processing_time'] = (
                (self.detection_stats['average_processing_time'] * (total_operations - 1) + processing_time) /
                total_operations
            )

    def get_content_signature(self, content_id: str) -> Optional[ContentSignature]:
        """Get content signature by ID"""
        return self.content_signatures.get(content_id)

    def remove_content_signature(self, content_id: str) -> bool:
        """Remove content signature from storage"""
        if content_id in self.content_signatures:
            del self.content_signatures[content_id]
            # Note: FAISS indices would need to be rebuilt to remove entries
            return True
        return False

    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection system statistics"""
        return {
            **self.detection_stats,
            'total_signatures': len(self.content_signatures),
            'text_index_size': self.text_index.ntotal if self.text_index else 0,
            'image_index_size': self.image_index.ntotal if self.image_index else 0,
            'success_rate': (
                self.detection_stats['matches_found'] / max(1, self.detection_stats['comparisons_performed'])
            ) * 100
        }

    async def batch_similarity_detection(self, content_ids: List[str]) -> List[SimilarityResult]:
        """Perform batch similarity detection across multiple content items"""
        results = []
        
        # Create all pairwise combinations
        for i in range(len(content_ids)):
            for j in range(i + 1, len(content_ids)):
                similarity_result = await self.calculate_similarity(
                    content_ids[i], content_ids[j]
                )
                if similarity_result:
                    results.append(similarity_result)
        
        return results

    async def cleanup(self) -> None:
        """Clean up resources and save state"""
        # Save signatures to persistent storage if needed
        logger.info("Content Detector cleanup complete")


class SimilarityScanner:
    """
    High-Level Similarity Scanner for Content Protection
    
    Provides easy-to-use interface for content similarity scanning
    with automated threat detection and reporting.
    """
    
    def __init__(self, detector: ContentDetector):
        self.detector = detector
        self.scan_history: List[Dict] = []
        self.threat_threshold = 0.85
        
    async def scan_for_violations(self, protected_content_id: str,
                                search_content_ids: List[str]) -> Dict[str, Any]:
        """Scan for potential content violations"""
        violations = []
        suspicious_matches = []
        
        for content_id in search_content_ids:
            result = await self.detector.calculate_similarity(
                protected_content_id, content_id
            )
            
            if result:
                if result.similarity_score >= self.threat_threshold:
                    violations.append({
                        'content_id': content_id,
                        'similarity_score': result.similarity_score,
                        'threat_level': 'HIGH',
                        'confidence': result.confidence_score,
                        'details': result
                    })
                elif result.similarity_score >= 0.7:
                    suspicious_matches.append({
                        'content_id': content_id,
                        'similarity_score': result.similarity_score,
                        'threat_level': 'MEDIUM',
                        'confidence': result.confidence_score,
                        'details': result
                    })
        
        scan_report = {
            'protected_content_id': protected_content_id,
            'total_scanned': len(search_content_ids),
            'violations_found': len(violations),
            'suspicious_matches': len(suspicious_matches),
            'violations': violations,
            'suspicious': suspicious_matches,
            'scan_timestamp': datetime.now().isoformat(),
            'threat_summary': self._generate_threat_summary(violations, suspicious_matches)
        }
        
        self.scan_history.append(scan_report)
        return scan_report
    
    def _generate_threat_summary(self, violations: List, suspicious: List) -> Dict:
        """Generate threat level summary"""
        total_threats = len(violations) + len(suspicious)
        
        if len(violations) >= 5:
            threat_level = "CRITICAL"
        elif len(violations) >= 2:
            threat_level = "HIGH"
        elif len(violations) >= 1 or len(suspicious) >= 3:
            threat_level = "MEDIUM"
        elif len(suspicious) >= 1:
            threat_level = "LOW"
        else:
            threat_level = "NONE"
        
        return {
            'threat_level': threat_level,
            'total_threats': total_threats,
            'high_risk_matches': len(violations),
            'medium_risk_matches': len(suspicious),
            'recommendation': self._get_threat_recommendation(threat_level)
        }
    
    def _get_threat_recommendation(self, threat_level: str) -> str:
        """Get recommendation based on threat level"""
        recommendations = {
            'CRITICAL': 'Immediate legal action recommended. Multiple high-similarity matches detected.',
            'HIGH': 'Investigation required. Potential content theft detected.',
            'MEDIUM': 'Monitor closely. Some suspicious similarities found.',
            'LOW': 'Routine monitoring sufficient. Low-risk similarities detected.',
            'NONE': 'No threats detected. Content appears secure.'
        }
        return recommendations.get(threat_level, 'Unknown threat level')
    
    def get_scan_history(self) -> List[Dict]:
        """Get historical scan results"""
        return self.scan_history
