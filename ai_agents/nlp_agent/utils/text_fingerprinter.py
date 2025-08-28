"""
Text Fingerprinter - Advanced Text Fingerprinting and Similarity System
=======================================================================

Advanced text fingerprinting system for content protection, plagiarism detection,
and similarity analysis with high precision and robust matching capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import hashlib
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import json
from collections import defaultdict, Counter
import zlib

try:
    from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import TruncatedSVD
    import scipy.sparse
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. Fingerprinting will use basic methods.")

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. Using fallback fingerprinting.")

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.util import ngrams
    NLTK_AVAILABLE = True
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available. Using basic tokenization.")

from .config import NLPAgentConfig, default_config

# Setup logging
logger = logging.getLogger(__name__)

class FingerprintType(Enum):
    """Types of text fingerprints"""
    HASH = "hash"  # Simple hash-based
    SHINGLE = "shingle"  # N-gram shingles
    SEMANTIC = "semantic"  # Semantic embeddings
    STRUCTURAL = "structural"  # Text structure
    STYLOMETRIC = "stylometric"  # Writing style
    HYBRID = "hybrid"  # Combined approach

class SimilarityMethod(Enum):
    """Similarity calculation methods"""
    COSINE = "cosine"
    JACCARD = "jaccard"
    HAMMING = "hamming"
    EUCLIDEAN = "euclidean"
    LEVENSHTEIN = "levenshtein"

@dataclass
class TextFingerprint:
    """Text fingerprint with multiple representations"""
    text_id: str
    original_text: str
    hash_fingerprint: str
    shingle_fingerprint: List[str] = field(default_factory=list)
    semantic_fingerprint: Optional[np.ndarray] = None
    structural_fingerprint: Dict[str, float] = field(default_factory=dict)
    stylometric_fingerprint: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    creation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class SimilarityResult:
    """Result of similarity comparison between texts"""
    text1_id: str
    text2_id: str
    overall_similarity: float
    hash_similarity: float
    shingle_similarity: float
    semantic_similarity: float
    structural_similarity: float
    stylometric_similarity: float
    is_duplicate: bool = False
    is_near_duplicate: bool = False
    similarity_breakdown: Dict[str, float] = field(default_factory=dict)
    matched_segments: List[Tuple[str, str]] = field(default_factory=list)
    confidence: float = 0.0

@dataclass
class FingerprintingResult:
    """Complete fingerprinting analysis result"""
    fingerprints: List[TextFingerprint] = field(default_factory=list)
    similarity_matrix: Optional[np.ndarray] = None
    duplicate_pairs: List[Tuple[str, str, float]] = field(default_factory=list)
    near_duplicate_pairs: List[Tuple[str, str, float]] = field(default_factory=list)
    clusters: List[List[str]] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class TextFingerprinter:
    """
    Advanced text fingerprinting system for content protection, plagiarism detection,
    and similarity analysis with multiple fingerprinting techniques.
    """
    
    def __init__(self, config: Optional[NLPAgentConfig] = None):
        """Initialize Text Fingerprinter"""
        self.config = config or default_config
        self.fingerprint_cache = {}
        self.similarity_cache = {}
        self.vectorizers = {}
        self.pipelines = {}
        self.stop_words = self._load_stop_words()
        
        self._initialize_components()
    
    def _load_stop_words(self) -> set:
        """Load stop words for text processing"""
        stop_words = set()
        
        try:
            if NLTK_AVAILABLE:
                stop_words.update(stopwords.words('english'))
        except:
            pass
        
        # Add common stop words
        common_stops = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'this', 'but', 'they',
            'have', 'had', 'what', 'said', 'each', 'which', 'their', 'time'
        }
        stop_words.update(common_stops)
        
        return stop_words
    
    def _initialize_components(self):
        """Initialize fingerprinting components"""
        try:
            # Initialize scikit-learn vectorizers
            if SKLEARN_AVAILABLE:
                self.vectorizers["tfidf"] = TfidfVectorizer(
                    max_features=10000,
                    ngram_range=(1, 3),
                    min_df=1,
                    max_df=0.95,
                    stop_words='english'
                )
                
                self.vectorizers["hashing"] = HashingVectorizer(
                    n_features=10000,
                    ngram_range=(2, 4),
                    stop_words='english'
                )
                
                logger.info("Scikit-learn vectorizers initialized")
            
            # Initialize transformer models
            if TRANSFORMERS_AVAILABLE:
                try:
                    # Sentence embeddings for semantic fingerprinting
                    self.pipelines["embeddings"] = pipeline(
                        "feature-extraction",
                        model="sentence-transformers/all-MiniLM-L6-v2",
                        device=self._get_device()
                    )
                    
                    logger.info("Transformer models initialized")
                except Exception as e:
                    logger.warning(f"Failed to load transformer models: {e}")
            
        except Exception as e:
            logger.error(f"Failed to initialize fingerprinting components: {e}")
    
    def _get_device(self) -> int:
        """Get optimal device for model execution"""
        if self.config.performance.enable_gpu and TRANSFORMERS_AVAILABLE:
            try:
                if torch.cuda.is_available():
                    return 0  # Use first GPU
            except:
                pass
        return -1  # Use CPU
    
    def _generate_text_id(self, text: str, custom_id: Optional[str] = None) -> str:
        """Generate unique ID for text"""
        if custom_id:
            return custom_id
        
        # Generate ID based on text hash and timestamp
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"text_{text_hash}_{timestamp}"
    
    async def create_fingerprint(
        self,
        text: str,
        text_id: Optional[str] = None,
        fingerprint_types: Optional[List[FingerprintType]] = None
    ) -> TextFingerprint:
        """
        Create comprehensive fingerprint for text
        
        Args:
            text: Text to fingerprint
            text_id: Optional custom ID for the text
            fingerprint_types: Types of fingerprints to create
        
        Returns:
            TextFingerprint with all requested fingerprint types
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")
        
        if fingerprint_types is None:
            fingerprint_types = [FingerprintType.HASH, FingerprintType.SHINGLE, FingerprintType.SEMANTIC]
        
        text_id = self._generate_text_id(text, text_id)
        
        # Check cache
        cache_key = f"{text_id}_{hash(text)}_{str(fingerprint_types)}"
        if cache_key in self.fingerprint_cache:
            return self.fingerprint_cache[cache_key]
        
        fingerprint = TextFingerprint(
            text_id=text_id,
            original_text=text,
            hash_fingerprint=""
        )
        
        try:
            # Generate different types of fingerprints
            for fp_type in fingerprint_types:
                if fp_type == FingerprintType.HASH:
                    fingerprint.hash_fingerprint = await self._create_hash_fingerprint(text)
                
                elif fp_type == FingerprintType.SHINGLE:
                    fingerprint.shingle_fingerprint = await self._create_shingle_fingerprint(text)
                
                elif fp_type == FingerprintType.SEMANTIC:
                    fingerprint.semantic_fingerprint = await self._create_semantic_fingerprint(text)
                
                elif fp_type == FingerprintType.STRUCTURAL:
                    fingerprint.structural_fingerprint = await self._create_structural_fingerprint(text)
                
                elif fp_type == FingerprintType.STYLOMETRIC:
                    fingerprint.stylometric_fingerprint = await self._create_stylometric_fingerprint(text)
                
                elif fp_type == FingerprintType.HYBRID:
                    # Create all types for hybrid approach
                    fingerprint.hash_fingerprint = await self._create_hash_fingerprint(text)
                    fingerprint.shingle_fingerprint = await self._create_shingle_fingerprint(text)
                    fingerprint.semantic_fingerprint = await self._create_semantic_fingerprint(text)
                    fingerprint.structural_fingerprint = await self._create_structural_fingerprint(text)
                    fingerprint.stylometric_fingerprint = await self._create_stylometric_fingerprint(text)
            
            # Add metadata
            fingerprint.metadata = {
                "text_length": len(text),
                "word_count": len(text.split()),
                "fingerprint_types": [fp_type.value for fp_type in fingerprint_types],
                "processing_method": self._get_processing_method()
            }
            
            # Cache the result
            self.fingerprint_cache[cache_key] = fingerprint
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Fingerprint creation failed: {e}")
            raise
    
    async def _create_hash_fingerprint(self, text: str) -> str:
        """Create hash-based fingerprint"""
        # Normalize text
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Create multiple hashes for robustness
        md5_hash = hashlib.md5(normalized.encode('utf-8')).hexdigest()
        sha1_hash = hashlib.sha1(normalized.encode('utf-8')).hexdigest()
        sha256_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        
        # Combine hashes
        combined_hash = md5_hash + sha1_hash[:16] + sha256_hash[:16]
        
        return combined_hash
    
    async def _create_shingle_fingerprint(self, text: str, k: int = 5) -> List[str]:
        """Create shingle-based fingerprint using k-grams"""
        # Normalize text
        normalized = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
        words = normalized.split()
        
        shingles = []
        
        # Character-level k-grams
        if len(normalized) >= k:
            for i in range(len(normalized) - k + 1):
                shingle = normalized[i:i + k]
                shingle_hash = hashlib.md5(shingle.encode('utf-8')).hexdigest()[:16]
                shingles.append(shingle_hash)
        
        # Word-level n-grams
        if NLTK_AVAILABLE:
            try:
                word_shingles = list(ngrams(words, min(3, len(words))))
                for shingle in word_shingles:
                    shingle_text = ' '.join(shingle)
                    shingle_hash = hashlib.md5(shingle_text.encode('utf-8')).hexdigest()[:16]
                    shingles.append(shingle_hash)
            except:
                pass
        else:
            # Fallback word n-grams
            for i in range(len(words) - 2):
                if i + 3 <= len(words):
                    shingle_text = ' '.join(words[i:i + 3])
                    shingle_hash = hashlib.md5(shingle_text.encode('utf-8')).hexdigest()[:16]
                    shingles.append(shingle_hash)
        
        return list(set(shingles))  # Remove duplicates
    
    async def _create_semantic_fingerprint(self, text: str) -> Optional[np.ndarray]:
        """Create semantic fingerprint using embeddings"""
        try:
            if TRANSFORMERS_AVAILABLE and "embeddings" in self.pipelines:
                # Generate embeddings
                embeddings = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.pipelines["embeddings"](text)
                )
                
                # Average pooling
                if embeddings and len(embeddings) > 0:
                    semantic_vector = np.mean(embeddings, axis=0)
                    return semantic_vector
            
            elif SKLEARN_AVAILABLE:
                # Fallback using TF-IDF
                tfidf_matrix = self.vectorizers["tfidf"].fit_transform([text])
                return tfidf_matrix.toarray()[0]
            
        except Exception as e:
            logger.error(f"Semantic fingerprint creation failed: {e}")
        
        return None
    
    async def _create_structural_fingerprint(self, text: str) -> Dict[str, float]:
        """Create structural fingerprint based on text structure"""
        structural_features = {}
        
        try:
            # Basic text statistics
            structural_features["length"] = len(text)
            structural_features["word_count"] = len(text.split())
            structural_features["char_count"] = len(text)
            structural_features["avg_word_length"] = np.mean([len(word) for word in text.split()]) if text.split() else 0
            
            # Sentence statistics
            if NLTK_AVAILABLE:
                try:
                    sentences = sent_tokenize(text)
                    structural_features["sentence_count"] = len(sentences)
                    structural_features["avg_sentence_length"] = np.mean([len(sent.split()) for sent in sentences]) if sentences else 0
                except:
                    sentences = text.split('.')
                    structural_features["sentence_count"] = len([s for s in sentences if s.strip()])
                    structural_features["avg_sentence_length"] = structural_features["word_count"] / max(structural_features["sentence_count"], 1)
            else:
                sentences = text.split('.')
                structural_features["sentence_count"] = len([s for s in sentences if s.strip()])
                structural_features["avg_sentence_length"] = structural_features["word_count"] / max(structural_features["sentence_count"], 1)
            
            # Punctuation statistics
            structural_features["punctuation_count"] = len(re.findall(r'[^\w\s]', text))
            structural_features["exclamation_count"] = text.count('!')
            structural_features["question_count"] = text.count('?')
            structural_features["comma_count"] = text.count(',')
            structural_features["period_count"] = text.count('.')
            
            # Character type ratios
            alpha_count = len(re.findall(r'[a-zA-Z]', text))
            digit_count = len(re.findall(r'\d', text))
            space_count = text.count(' ')
            
            total_chars = len(text)
            if total_chars > 0:
                structural_features["alpha_ratio"] = alpha_count / total_chars
                structural_features["digit_ratio"] = digit_count / total_chars
                structural_features["space_ratio"] = space_count / total_chars
                structural_features["punct_ratio"] = structural_features["punctuation_count"] / total_chars
            
            # Capitalization patterns
            structural_features["uppercase_count"] = len(re.findall(r'[A-Z]', text))
            structural_features["title_case_words"] = len(re.findall(r'\b[A-Z][a-z]+\b', text))
            structural_features["all_caps_words"] = len(re.findall(r'\b[A-Z]{2,}\b', text))
            
            # Normalize features by text length for comparison
            if structural_features["word_count"] > 0:
                for key in ["punctuation_count", "exclamation_count", "question_count", "comma_count", "period_count"]:
                    structural_features[f"{key}_per_word"] = structural_features[key] / structural_features["word_count"]
            
        except Exception as e:
            logger.error(f"Structural fingerprint creation failed: {e}")
        
        return structural_features
    
    async def _create_stylometric_fingerprint(self, text: str) -> Dict[str, float]:
        """Create stylometric fingerprint based on writing style"""
        stylometric_features = {}
        
        try:
            words = text.split()
            if not words:
                return stylometric_features
            
            # Lexical diversity
            unique_words = len(set([word.lower() for word in words]))
            stylometric_features["lexical_diversity"] = unique_words / len(words)
            
            # Average word length distribution
            word_lengths = [len(word) for word in words]
            stylometric_features["avg_word_length"] = np.mean(word_lengths)
            stylometric_features["word_length_variance"] = np.var(word_lengths)
            
            # Function word usage (simplified)
            function_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            function_word_count = sum(1 for word in words if word.lower() in function_words)
            stylometric_features["function_word_ratio"] = function_word_count / len(words)
            
            # Punctuation style
            stylometric_features["comma_usage"] = text.count(',') / len(words)
            stylometric_features["semicolon_usage"] = text.count(';') / len(words)
            stylometric_features["colon_usage"] = text.count(':') / len(words)
            
            # Sentence complexity (approximated)
            sentence_delimiters = text.count('.') + text.count('!') + text.count('?')
            if sentence_delimiters > 0:
                stylometric_features["avg_words_per_sentence"] = len(words) / sentence_delimiters
            
            # Readability approximation (simplified Flesch-like measure)
            if sentence_delimiters > 0:
                avg_sentence_length = len(words) / sentence_delimiters
                avg_syllables_per_word = np.mean([self._estimate_syllables(word) for word in words])
                stylometric_features["readability_score"] = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
            
            # Capitalization style
            capital_letters = len(re.findall(r'[A-Z]', text))
            if len(text) > 0:
                stylometric_features["capitalization_ratio"] = capital_letters / len(text)
            
        except Exception as e:
            logger.error(f"Stylometric fingerprint creation failed: {e}")
        
        return stylometric_features
    
    def _estimate_syllables(self, word: str) -> int:
        """Estimate number of syllables in a word (simple heuristic)"""
        word = word.lower().strip()
        if len(word) <= 3:
            return 1
        
        vowels = 'aeiouy'
        syllables = 0
        prev_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_was_vowel:
                    syllables += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False
        
        # Handle silent e
        if word.endswith('e'):
            syllables -= 1
        
        return max(1, syllables)
    
    async def compare_fingerprints(
        self,
        fingerprint1: TextFingerprint,
        fingerprint2: TextFingerprint,
        similarity_method: SimilarityMethod = SimilarityMethod.COSINE
    ) -> SimilarityResult:
        """
        Compare two fingerprints and calculate similarity
        
        Args:
            fingerprint1: First fingerprint
            fingerprint2: Second fingerprint
            similarity_method: Method for similarity calculation
        
        Returns:
            SimilarityResult with detailed comparison
        """
        result = SimilarityResult(
            text1_id=fingerprint1.text_id,
            text2_id=fingerprint2.text_id,
            overall_similarity=0.0,
            hash_similarity=0.0,
            shingle_similarity=0.0,
            semantic_similarity=0.0,
            structural_similarity=0.0,
            stylometric_similarity=0.0
        )
        
        try:
            similarities = []
            weights = []
            
            # Hash similarity
            if fingerprint1.hash_fingerprint and fingerprint2.hash_fingerprint:
                result.hash_similarity = self._calculate_hash_similarity(
                    fingerprint1.hash_fingerprint,
                    fingerprint2.hash_fingerprint
                )
                similarities.append(result.hash_similarity)
                weights.append(0.2)
            
            # Shingle similarity
            if fingerprint1.shingle_fingerprint and fingerprint2.shingle_fingerprint:
                result.shingle_similarity = self._calculate_shingle_similarity(
                    fingerprint1.shingle_fingerprint,
                    fingerprint2.shingle_fingerprint
                )
                similarities.append(result.shingle_similarity)
                weights.append(0.3)
            
            # Semantic similarity
            if (fingerprint1.semantic_fingerprint is not None and 
                fingerprint2.semantic_fingerprint is not None):
                result.semantic_similarity = await self._calculate_semantic_similarity(
                    fingerprint1.semantic_fingerprint,
                    fingerprint2.semantic_fingerprint,
                    similarity_method
                )
                similarities.append(result.semantic_similarity)
                weights.append(0.4)
            
            # Structural similarity
            if fingerprint1.structural_fingerprint and fingerprint2.structural_fingerprint:
                result.structural_similarity = self._calculate_structural_similarity(
                    fingerprint1.structural_fingerprint,
                    fingerprint2.structural_fingerprint
                )
                similarities.append(result.structural_similarity)
                weights.append(0.05)
            
            # Stylometric similarity
            if fingerprint1.stylometric_fingerprint and fingerprint2.stylometric_fingerprint:
                result.stylometric_similarity = self._calculate_stylometric_similarity(
                    fingerprint1.stylometric_fingerprint,
                    fingerprint2.stylometric_fingerprint
                )
                similarities.append(result.stylometric_similarity)
                weights.append(0.05)
            
            # Calculate overall similarity
            if similarities and weights:
                # Normalize weights
                total_weight = sum(weights)
                normalized_weights = [w / total_weight for w in weights]
                
                result.overall_similarity = sum(
                    sim * weight for sim, weight in zip(similarities, normalized_weights)
                )
            
            # Determine duplicate status
            result.is_duplicate = result.overall_similarity > 0.95
            result.is_near_duplicate = result.overall_similarity > 0.8
            
            # Calculate confidence
            result.confidence = min(len(similarities) / 3.0, 1.0)  # Based on number of comparisons
            
            # Create similarity breakdown
            result.similarity_breakdown = {
                "hash": result.hash_similarity,
                "shingle": result.shingle_similarity,
                "semantic": result.semantic_similarity,
                "structural": result.structural_similarity,
                "stylometric": result.stylometric_similarity
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Fingerprint comparison failed: {e}")
            result.confidence = 0.0
            return result
    
    def _calculate_hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between hash fingerprints"""
        if hash1 == hash2:
            return 1.0
        
        # Calculate Hamming distance for similar-length hashes
        if len(hash1) == len(hash2):
            matches = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
            return matches / len(hash1)
        
        return 0.0
    
    def _calculate_shingle_similarity(self, shingles1: List[str], shingles2: List[str]) -> float:
        """Calculate Jaccard similarity between shingle sets"""
        set1 = set(shingles1)
        set2 = set(shingles2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    async def _calculate_semantic_similarity(
        self,
        vector1: np.ndarray,
        vector2: np.ndarray,
        similarity_method: SimilarityMethod
    ) -> float:
        """Calculate semantic similarity between vectors"""
        try:
            if similarity_method == SimilarityMethod.COSINE:
                # Cosine similarity
                dot_product = np.dot(vector1, vector2)
                norm_product = np.linalg.norm(vector1) * np.linalg.norm(vector2)
                return dot_product / norm_product if norm_product > 0 else 0.0
            
            elif similarity_method == SimilarityMethod.EUCLIDEAN:
                # Euclidean distance (converted to similarity)
                distance = np.linalg.norm(vector1 - vector2)
                max_distance = np.linalg.norm(vector1) + np.linalg.norm(vector2)
                return 1.0 - (distance / max_distance) if max_distance > 0 else 0.0
            
            else:
                # Default to cosine similarity
                return await self._calculate_semantic_similarity(vector1, vector2, SimilarityMethod.COSINE)
        
        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_structural_similarity(self, struct1: Dict[str, float], struct2: Dict[str, float]) -> float:
        """Calculate similarity between structural fingerprints"""
        try:
            common_keys = set(struct1.keys()) & set(struct2.keys())
            if not common_keys:
                return 0.0
            
            # Calculate normalized differences
            differences = []
            for key in common_keys:
                val1, val2 = struct1[key], struct2[key]
                max_val = max(abs(val1), abs(val2), 1.0)  # Avoid division by zero
                diff = 1.0 - abs(val1 - val2) / max_val
                differences.append(diff)
            
            return np.mean(differences)
        
        except Exception as e:
            logger.error(f"Structural similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_stylometric_similarity(self, style1: Dict[str, float], style2: Dict[str, float]) -> float:
        """Calculate similarity between stylometric fingerprints"""
        return self._calculate_structural_similarity(style1, style2)  # Same method
    
    async def batch_fingerprint(
        self,
        texts: List[str],
        text_ids: Optional[List[str]] = None,
        fingerprint_types: Optional[List[FingerprintType]] = None
    ) -> List[TextFingerprint]:
        """Create fingerprints for multiple texts"""
        if text_ids and len(text_ids) != len(texts):
            raise ValueError("Number of text_ids must match number of texts")
        
        fingerprints = []
        
        for i, text in enumerate(texts):
            text_id = text_ids[i] if text_ids else None
            fingerprint = await self.create_fingerprint(text, text_id, fingerprint_types)
            fingerprints.append(fingerprint)
        
        return fingerprints
    
    async def find_duplicates(
        self,
        texts: List[str],
        similarity_threshold: float = 0.8,
        text_ids: Optional[List[str]] = None
    ) -> FingerprintingResult:
        """Find duplicate and near-duplicate texts"""
        start_time = asyncio.get_event_loop().time()
        
        # Create fingerprints
        fingerprints = await self.batch_fingerprint(texts, text_ids)
        
        result = FingerprintingResult(fingerprints=fingerprints)
        
        try:
            # Compare all pairs
            n = len(fingerprints)
            similarity_matrix = np.zeros((n, n))
            
            for i in range(n):
                similarity_matrix[i, i] = 1.0  # Self-similarity
                
                for j in range(i + 1, n):
                    comparison = await self.compare_fingerprints(fingerprints[i], fingerprints[j])
                    similarity = comparison.overall_similarity
                    
                    similarity_matrix[i, j] = similarity
                    similarity_matrix[j, i] = similarity
                    
                    # Check for duplicates
                    if comparison.is_duplicate:
                        result.duplicate_pairs.append((
                            fingerprints[i].text_id,
                            fingerprints[j].text_id,
                            similarity
                        ))
                    elif comparison.is_near_duplicate or similarity >= similarity_threshold:
                        result.near_duplicate_pairs.append((
                            fingerprints[i].text_id,
                            fingerprints[j].text_id,
                            similarity
                        ))
            
            result.similarity_matrix = similarity_matrix
            
            # Create clusters of similar texts
            result.clusters = await self._create_similarity_clusters(
                fingerprints, similarity_matrix, similarity_threshold
            )
            
            # Calculate statistics
            result.statistics = {
                "total_texts": n,
                "duplicate_pairs": len(result.duplicate_pairs),
                "near_duplicate_pairs": len(result.near_duplicate_pairs),
                "clusters": len(result.clusters),
                "avg_similarity": np.mean(similarity_matrix[np.triu_indices(n, k=1)]) if n > 1 else 0.0
            }
            
            result.processing_time = asyncio.get_event_loop().time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Duplicate finding failed: {e}")
            result.processing_time = asyncio.get_event_loop().time() - start_time
            return result
    
    async def _create_similarity_clusters(
        self,
        fingerprints: List[TextFingerprint],
        similarity_matrix: np.ndarray,
        threshold: float
    ) -> List[List[str]]:
        """Create clusters of similar texts"""
        clusters = []
        visited = set()
        
        try:
            for i, fingerprint in enumerate(fingerprints):
                if i in visited:
                    continue
                
                # Start new cluster
                cluster = [fingerprint.text_id]
                visited.add(i)
                
                # Find similar texts
                for j, other_fingerprint in enumerate(fingerprints):
                    if j != i and j not in visited and similarity_matrix[i, j] >= threshold:
                        cluster.append(other_fingerprint.text_id)
                        visited.add(j)
                
                # Only keep clusters with multiple texts
                if len(cluster) > 1:
                    clusters.append(cluster)
        
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
        
        return clusters
    
    def _get_processing_method(self) -> str:
        """Get the processing method being used"""
        methods = []
        
        if SKLEARN_AVAILABLE:
            methods.append("sklearn")
        
        if TRANSFORMERS_AVAILABLE:
            methods.append("transformers")
        
        if NLTK_AVAILABLE:
            methods.append("nltk")
        
        return "+".join(methods) if methods else "basic"
    
    def clear_cache(self):
        """Clear fingerprint and similarity caches"""
        self.fingerprint_cache.clear()
        self.similarity_cache.clear()
        logger.info("Fingerprint caches cleared")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        status = {
            "status": "healthy",
            "sklearn_available": SKLEARN_AVAILABLE,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "nltk_available": NLTK_AVAILABLE,
            "vectorizers_loaded": len(self.vectorizers),
            "pipelines_loaded": len(self.pipelines),
            "cache_size": len(self.fingerprint_cache)
        }
        
        # Test basic functionality
        try:
            test_text = "This is a test document for fingerprinting."
            test_result = asyncio.run(self.create_fingerprint(test_text))
            status["test_result"] = "passed"
            status["test_fingerprint_created"] = bool(test_result.hash_fingerprint)
        except Exception as e:
            status["status"] = "degraded"
            status["error"] = str(e)
        
        return status
    
    def shutdown(self):
        """Shutdown the text fingerprinter"""
        logger.info("Shutting down Text Fingerprinter")
        
        # Clear caches
        self.clear_cache()
        
        # Clear models
        self.vectorizers.clear()
        self.pipelines.clear()
        
        # Clear GPU memory if using CUDA
        if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()

# Utility functions
def calculate_jaccard_similarity(set1: Set, set2: Set) -> float:
    """Calculate Jaccard similarity between two sets"""
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def normalize_text_for_comparison(text: str) -> str:
    """Normalize text for comparison purposes"""
    # Convert to lowercase
    normalized = text.lower()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove punctuation (optional, depends on use case)
    normalized = re.sub(r'[^\w\s]', '', normalized)
    
    return normalized.strip()

def estimate_similarity_threshold(similarity_scores: List[float]) -> float:
    """Estimate appropriate similarity threshold based on score distribution"""
    if not similarity_scores:
        return 0.8
    
    scores = np.array(similarity_scores)
    
    # Use median + standard deviation as threshold
    median_score = np.median(scores)
    std_score = np.std(scores)
    
    threshold = median_score + std_score
    return min(max(threshold, 0.5), 0.95)  # Clamp between 0.5 and 0.95
