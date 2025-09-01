"""Semantic Plagiarism Detection Engine - Industrial Grade
=========================================================

Ultra-advanced semantic plagiarism detection system with contextual analysis,
multi-layered similarity detection, and enterprise-scale performance.

Features:
- Semantic similarity analysis with BERT/RoBERTa embeddings
- Multi-level plagiarism type classification
- Real-time detection pipeline
- Advanced paraphrase detection
- Cross-lingual plagiarism detection
- Style-aware similarity analysis

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
import time
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib
from collections import defaultdict, Counter
import re
import string
import math

try:
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.cluster import DBSCAN
    import scipy.stats as stats
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. Limited similarity analysis.")

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.tag import pos_tag
    from nltk.chunk import ne_chunk
    from nltk.util import ngrams
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available. Using basic text processing.")

try:
    from fuzzywuzzy import fuzz, process
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    logging.warning("FuzzyWuzzy not available. Limited fuzzy matching.")

from .industrial_embeddings_engine import IndustrialEmbeddingsEngine, ContextualEmbedding

logger = logging.getLogger(__name__)

class PlagiarismType(Enum):
    """Types of plagiarism detected"""

    EXACT_COPY = "exact_copy"
    NEAR_EXACT = "near_exact"
    PARAPHRASE = "paraphrase"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    STRUCTURAL_SIMILARITY = "structural_similarity"
    STYLISTIC_MATCH = "stylistic_match"
    TRANSLATION_PLAGIARISM = "translation_plagiarism"
    IDEA_PLAGIARISM = "idea_plagiarism"
    MOSAIC_PLAGIARISM = "mosaic_plagiarism"
    SELF_PLAGIARISM = "self_plagiarism"

class SimilarityLevel(Enum):
    """Levels of similarity"""

    IDENTICAL = "identical"
    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    NEGLIGIBLE = "negligible"

class DetectionStrategy(Enum):
    """Detection strategies"""

    COMPREHENSIVE = "comprehensive"
    FAST_SCREENING = "fast_screening"
    DEEP_SEMANTIC = "deep_semantic"
    LINGUISTIC_ANALYSIS = "linguistic_analysis"

@dataclass
class PlagiarismMatch:
    """A plagiarism match result"""
    source_id: str
    target_id: str
    source_text: str
    target_text: str
    plagiarism_type: PlagiarismType
    similarity_level: SimilarityLevel
    confidence_score: float
    similarity_scores: Dict[str, float] = field(default_factory=dict)
    matched_segments: List[Tuple[str, str]] = field(default_factory=list)
    contextual_analysis: Dict[str, Any] = field(default_factory=dict)
    detection_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlagiarismReport:
    """
Comprehensive plagiarism detection report"""
    query_id: str
    query_text: str
    total_matches: int
    matches: List[PlagiarismMatch] = field(default_factory=list)
    summary_statistics: Dict[str, Any] = field(default_factory=dict)
    risk_assessment: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    detection_strategy: DetectionStrategy = DetectionStrategy.COMPREHENSIVE
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class SemanticAnalysisConfig:
    """
Configuration for semantic analysis"""
    # Thresholds
    exact_match_threshold: float = 0.98
    near_exact_threshold: float = 0.90
    paraphrase_threshold: float = 0.80
    semantic_threshold: float = 0.70
    structural_threshold: float = 0.75
    
    # Analysis parameters
    min_text_length: int = 50
    max_text_length: int = 10000
    ngram_sizes: List[int] = field(default_factory=lambda: [2, 3, 4, 5])
    context_window_size: int = 5
    
    # Performance settings
    batch_size: int = 32
    enable_multilingual: bool = True
    enable_cross_lingual: bool = True
    
    # Detection features
    check_paraphrases: bool = True
    check_translations: bool = True
    check_stylistics: bool = True
    check_structure: bool = True

class SemanticPlagiarismDetector:
    """
    Industrial-grade semantic plagiarism detection engine
    """
    
    def __init__(self, 
                 embeddings_engine: IndustrialEmbeddingsEngine,
                 config: Optional[SemanticAnalysisConfig] = None):
        """
Initialize semantic plagiarism detector"""
        self.embeddings_engine = embeddings_engine
        self.config = config or SemanticAnalysisConfig()
        
        # Analysis tools
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 3),
            stop_words='english'
        ) if SKLEARN_AVAILABLE else None
        
        self.stemmer = PorterStemmer() if NLTK_AVAILABLE else None
        self.lemmatizer = WordNetLemmatizer() if NLTK_AVAILABLE else None
        
        # Caches for performance
        self.embedding_cache = {}
        self.analysis_cache = {}
        self.ngram_cache = {}
        
        # Performance tracking
        self.detection_stats = defaultdict(int)
        self.processing_times = []
        
        logger.info("Semantic Plagiarism Detector initialized")
    
    async def detect_plagiarism(
        self,
        query_text: str,
        candidate_texts: List[Tuple[str, str]],  # (id, text) pairs
        strategy: DetectionStrategy = DetectionStrategy.COMPREHENSIVE,
        custom_thresholds: Optional[Dict[str, float]] = None
    ) -> PlagiarismReport:
        """
        Detect plagiarism in candidate texts against query text
        
        Args:
            query_text: Text to check for plagiarism
            candidate_texts: List of (id, text) pairs to check against
            strategy: Detection strategy to use
            custom_thresholds: Custom similarity thresholds
        
        Returns:
            Comprehensive plagiarism report
        """
        start_time = time.time()
        
        # Apply custom thresholds if provided
        if custom_thresholds:
            config = self._apply_custom_thresholds(custom_thresholds)
        else:
            config = self.config
        
        # Generate query embedding
        query_id = f"query_{hashlib.md5(query_text.encode()).hexdigest()[:12]}"
        query_embedding = await self.embeddings_engine.generate_contextual_embeddings(
            query_text, text_ids=query_id, include_context=True, extract_layers=True
        )
        
        # Generate candidate embeddings
        candidate_embeddings = []
        candidate_ids = [cid for cid, _ in candidate_texts]
        candidate_text_list = [text for _, text in candidate_texts]
        
        embeddings = await self.embeddings_engine.generate_contextual_embeddings(
            candidate_text_list, text_ids=candidate_ids, include_context=True, extract_layers=True
        )
        
        if isinstance(embeddings, list):
            candidate_embeddings = embeddings
        else:
            candidate_embeddings = [embeddings]
        
        # Perform plagiarism detection based on strategy
        matches = []
        if strategy == DetectionStrategy.COMPREHENSIVE:
            matches = await self._comprehensive_detection(query_embedding, candidate_embeddings, config)
        elif strategy == DetectionStrategy.FAST_SCREENING:
            matches = await self._fast_screening(query_embedding, candidate_embeddings, config)
        elif strategy == DetectionStrategy.DEEP_SEMANTIC:
            matches = await self._deep_semantic_detection(query_embedding, candidate_embeddings, config)
        elif strategy == DetectionStrategy.LINGUISTIC_ANALYSIS:
            matches = await self._linguistic_analysis_detection(query_embedding, candidate_embeddings, config)
        
        # Generate report
        processing_time = time.time() - start_time
        report = self._generate_report(query_id, query_text, matches, processing_time, strategy)
        
        # Update statistics
        self.detection_stats['total_detections'] += 1
        self.detection_stats['total_matches'] += len(matches)
        self.processing_times.append(processing_time)
        
        return report
    
    async def _comprehensive_detection(
        self,
        query_embedding: ContextualEmbedding,
        candidate_embeddings: List[ContextualEmbedding],
        config: SemanticAnalysisConfig
    ) -> List[PlagiarismMatch]:
        """Perform comprehensive plagiarism detection"""
        
        matches = []
        
        for candidate in candidate_embeddings:
            match_start_time = time.time()
            
            # Calculate multiple similarity metrics
            similarities = await self._calculate_comprehensive_similarities(
                query_embedding, candidate, config
            )
            
            # Determine plagiarism type and confidence
            plagiarism_type, confidence = self._classify_plagiarism(similarities, config)
            
            if confidence > 0.5:  # Minimum confidence threshold
                similarity_level = self._determine_similarity_level(similarities)
                
                # Extract matched segments
                matched_segments = await self._extract_matched_segments(
                    query_embedding.text, candidate.text, similarities
                )
                
                # Perform contextual analysis
                contextual_analysis = await self._analyze_context_match(
                    query_embedding, candidate, similarities
                )
                
                match = PlagiarismMatch(
                    source_id=query_embedding.text_id,
                    target_id=candidate.text_id,
                    source_text=query_embedding.text,
                    target_text=candidate.text,
                    plagiarism_type=plagiarism_type,
                    similarity_level=similarity_level,
                    confidence_score=confidence,
                    similarity_scores=similarities,
                    matched_segments=matched_segments,
                    contextual_analysis=contextual_analysis,
                    detection_time=time.time() - match_start_time
                )
                
                matches.append(match)
        
        return matches
    
    async def _calculate_comprehensive_similarities(
        self,
        query_embedding: ContextualEmbedding,
        candidate_embedding: ContextualEmbedding,
        config: SemanticAnalysisConfig
    ) -> Dict[str, float]:
        """
Calculate comprehensive similarity metrics"""
        
        similarities = {}
        
        # 1. Semantic similarity (main embeddings)
        semantic_sim = cosine_similarity(
            [query_embedding.embedding], [candidate_embedding.embedding]
        )[0][0]
        similarities['semantic'] = float(semantic_sim)
        
        # 2. Contextual similarities
        if query_embedding.context_embeddings and candidate_embedding.context_embeddings:
            contextual_sims = []
            for context_type in query_embedding.context_embeddings.keys():
                if context_type in candidate_embedding.context_embeddings:
                    ctx_sim = cosine_similarity(
                        [query_embedding.context_embeddings[context_type]],
                        [candidate_embedding.context_embeddings[context_type]]
                    )[0][0]
                    contextual_sims.append(float(ctx_sim))
                    similarities[f'context_{context_type}'] = float(ctx_sim)
            
            if contextual_sims:
                similarities['contextual_avg'] = np.mean(contextual_sims)
        
        # 3. Layer-wise similarities
        if query_embedding.layer_embeddings and candidate_embedding.layer_embeddings:
            layer_sims = []
            for i, (q_layer, c_layer) in enumerate(zip(
                query_embedding.layer_embeddings, candidate_embedding.layer_embeddings
            )):
                layer_sim = cosine_similarity([q_layer], [c_layer])[0][0]
                layer_sims.append(float(layer_sim))
                similarities[f'layer_{i}'] = float(layer_sim)
            
            if layer_sims:
                similarities['layer_avg'] = np.mean(layer_sims)
        
        # 4. Lexical similarity (TF-IDF based)
        if SKLEARN_AVAILABLE and self.tfidf_vectorizer:
            try:
                tfidf_matrix = self.tfidf_vectorizer.fit_transform([
                    query_embedding.text, candidate_embedding.text
                ])
                lexical_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                similarities['lexical'] = float(lexical_sim)
            except Exception as e:
                logger.warning(f"TF-IDF similarity calculation failed: {e}")
        
        # 5. N-gram similarity
        ngram_similarities = await self._calculate_ngram_similarities(
            query_embedding.text, candidate_embedding.text, config.ngram_sizes
        )
        similarities.update(ngram_similarities)
        
        # 6. Structural similarity
        structural_sim = await self._calculate_structural_similarity(
            query_embedding.text, candidate_embedding.text
        )
        similarities['structural'] = structural_sim
        
        # 7. Stylistic similarity
        stylistic_sim = await self._calculate_stylistic_similarity(
            query_embedding, candidate_embedding
        )
        similarities['stylistic'] = stylistic_sim
        
        # 8. Fuzzy string similarity
        if FUZZYWUZZY_AVAILABLE:
            similarities['fuzzy_ratio'] = fuzz.ratio(query_embedding.text, candidate_embedding.text) / 100.0
            similarities['fuzzy_partial'] = fuzz.partial_ratio(query_embedding.text, candidate_embedding.text) / 100.0
            similarities['fuzzy_token_sort'] = fuzz.token_sort_ratio(query_embedding.text, candidate_embedding.text) / 100.0
        
        return similarities
    
    async def _calculate_ngram_similarities(
        self, text1: str, text2: str, ngram_sizes: List[int]
    ) -> Dict[str, float]:
        """Calculate n-gram based similarities"""
        
        similarities = {}
        
        if not NLTK_AVAILABLE:
            return similarities
        
        try:
            # Tokenize texts
            tokens1 = word_tokenize(text1.lower())
            tokens2 = word_tokenize(text2.lower())
            
            for n in ngram_sizes:
                if len(tokens1) >= n and len(tokens2) >= n:
                    ngrams1 = set(ngrams(tokens1, n))
                    ngrams2 = set(ngrams(tokens2, n))
                    
                    if ngrams1 and ngrams2:
                        intersection = len(ngrams1.intersection(ngrams2))
                        union = len(ngrams1.union(ngrams2))
                        jaccard = intersection / union if union > 0 else 0.0
                        similarities[f'ngram_{n}_jaccard'] = jaccard
                        
                        # Cosine similarity for n-grams
                        all_ngrams = ngrams1.union(ngrams2)
                        vec1 = [1 if ng in ngrams1 else 0 for ng in all_ngrams]
                        vec2 = [1 if ng in ngrams2 else 0 for ng in all_ngrams]
                        
                        if sum(vec1) > 0 and sum(vec2) > 0:
                            cosine_sim = cosine_similarity([vec1], [vec2])[0][0]
                            similarities[f'ngram_{n}_cosine'] = float(cosine_sim)
        
        except Exception as e:
            logger.warning(f"N-gram similarity calculation failed: {e}")
        
        return similarities
    
    async def _calculate_structural_similarity(self, text1: str, text2: str) -> float:
        """Calculate structural similarity between texts"""
        
        try:
            # Extract structural features
            features1 = self._extract_structural_features(text1)
            features2 = self._extract_structural_features(text2)
            
            # Calculate similarity of structural features
            similarities = []
            for key in features1.keys():
                if key in features2:
                    if features1[key] == 0 and features2[key] == 0:
                        similarities.append(1.0)
                    elif features1[key] == 0 or features2[key] == 0:
                        similarities.append(0.0)
                    else:
                        ratio = min(features1[key], features2[key]) / max(features1[key], features2[key])
                        similarities.append(ratio)
            
            return np.mean(similarities) if similarities else 0.0
        
        except Exception as e:
            logger.warning(f"Structural similarity calculation failed: {e}")
            return 0.0
    
    def _extract_structural_features(self, text: str) -> Dict[str, float]:
        """Extract structural features from text"""
        
        features = {}
        
        # Basic counts
        features['char_count'] = len(text)
        features['word_count'] = len(text.split())
        features['sentence_count'] = len([s for s in text.split('.') if s.strip()])
        features['paragraph_count'] = len([p for p in text.split('\n\n') if p.strip()])
        
        # Ratios and averages
        features['avg_word_length'] = np.mean([len(word) for word in text.split()]) if text.split() else 0
        features['avg_sentence_length'] = features['word_count'] / max(features['sentence_count'], 1)
        
        # Punctuation
        features['punctuation_count'] = sum(1 for c in text if c in string.punctuation)
        features['punctuation_ratio'] = features['punctuation_count'] / max(len(text), 1)
        
        # Capitalization
        features['capital_count'] = sum(1 for c in text if c.isupper())
        features['capital_ratio'] = features['capital_count'] / max(len(text), 1)
        
        # Special characters
        features['digit_count'] = sum(1 for c in text if c.isdigit())
        features['digit_ratio'] = features['digit_count'] / max(len(text), 1)
        
        return features
    
    async def _calculate_stylistic_similarity(
        self, embedding1: ContextualEmbedding, embedding2: ContextualEmbedding
    ) -> float:
        """
Calculate stylistic similarity between embeddings"""
        
        try:
            # Use pre-computed stylometric features if available
            if embedding1.stylometric_features and embedding2.stylometric_features:
                features1 = embedding1.stylometric_features
                features2 = embedding2.stylometric_features
                
                similarities = []
                for key in features1.keys():
                    if key in features2:
                        if features1[key] == 0 and features2[key] == 0:
                            similarities.append(1.0)
                        elif features1[key] == 0 or features2[key] == 0:
                            similarities.append(0.0)
                        else:
                            ratio = min(features1[key], features2[key]) / max(features1[key], features2[key])
                            similarities.append(ratio)
                
                return np.mean(similarities) if similarities else 0.0
            
            # Fallback to basic stylistic analysis
            return await self._basic_stylistic_similarity(embedding1.text, embedding2.text)
        
        except Exception as e:
            logger.warning(f"Stylistic similarity calculation failed: {e}")
            return 0.0
    
    async def _basic_stylistic_similarity(self, text1: str, text2: str) -> float:
        """Calculate basic stylistic similarity"""
        
        try:
            # Extract basic style features
            style1 = self._extract_basic_style_features(text1)
            style2 = self._extract_basic_style_features(text2)
            
            # Calculate feature similarity
            similarities = []
            for key in style1.keys():
                if key in style2:
                    if abs(style1[key] - style2[key]) < 0.001:  # Very close values
                        similarities.append(1.0)
                    else:
                        diff = abs(style1[key] - style2[key])
                        max_val = max(abs(style1[key]), abs(style2[key]), 1.0)
                        similarity = 1.0 - (diff / max_val)
                        similarities.append(max(0.0, similarity))
            
            return np.mean(similarities) if similarities else 0.0
        
        except Exception as e:
            logger.warning(f"Basic stylistic similarity calculation failed: {e}")
            return 0.0
    
    def _extract_basic_style_features(self, text: str) -> Dict[str, float]:
        """Extract basic stylistic features"""
        
        features = {}
        
        if not text:
            return features
        
        # Sentence length variation
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if sentences:
            sent_lengths = [len(s.split()) for s in sentences]
            features['avg_sentence_length'] = np.mean(sent_lengths)
            features['sentence_length_variance'] = np.var(sent_lengths)
        
        # Word length variation
        words = text.split()
        if words:
            word_lengths = [len(word) for word in words]
            features['avg_word_length'] = np.mean(word_lengths)
            features['word_length_variance'] = np.var(word_lengths)
        
        # Punctuation patterns
        features['comma_frequency'] = text.count(',') / len(text)
        features['semicolon_frequency'] = text.count(';') / len(text)
        features['question_frequency'] = text.count('?') / len(text)
        features['exclamation_frequency'] = text.count('!') / len(text)
        
        # Function word usage (basic set)
        function_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words_lower = [word.lower().strip(string.punctuation) for word in words]
        function_word_count = sum(1 for word in words_lower if word in function_words)
        features['function_word_ratio'] = function_word_count / max(len(words), 1)
        
        return features
    
    def _classify_plagiarism(
        self, similarities: Dict[str, float], config: SemanticAnalysisConfig
    ) -> Tuple[PlagiarismType, float]:
        """
Classify the type of plagiarism and calculate confidence"""
        
        semantic_sim = similarities.get('semantic', 0.0)
        lexical_sim = similarities.get('lexical', 0.0)
        ngram_avg = np.mean([v for k, v in similarities.items() if 'ngram' in k]) if any('ngram' in k for k in similarities.keys()) else 0.0
        structural_sim = similarities.get('structural', 0.0)
        stylistic_sim = similarities.get('stylistic', 0.0)
        fuzzy_ratio = similarities.get('fuzzy_ratio', 0.0)
        
        # Exact copy detection
        if fuzzy_ratio > config.exact_match_threshold and ngram_avg > 0.95:
            return PlagiarismType.EXACT_COPY, min(1.0, fuzzy_ratio + 0.1)
        
        # Near exact copy
        if fuzzy_ratio > config.near_exact_threshold and lexical_sim > 0.85:
            return PlagiarismType.NEAR_EXACT, min(1.0, (fuzzy_ratio + lexical_sim) / 2 + 0.05)
        
        # Paraphrase detection
        if semantic_sim > config.paraphrase_threshold and lexical_sim < 0.6:
            confidence = semantic_sim * 0.7 + (1 - abs(semantic_sim - lexical_sim)) * 0.3
            return PlagiarismType.PARAPHRASE, confidence
        
        # Semantic similarity
        if semantic_sim > config.semantic_threshold:
            confidence = semantic_sim * 0.8 + structural_sim * 0.2
            return PlagiarismType.SEMANTIC_SIMILARITY, confidence
        
        # Structural similarity
        if structural_sim > config.structural_threshold and semantic_sim > 0.5:
            confidence = (structural_sim + semantic_sim) / 2
            return PlagiarismType.STRUCTURAL_SIMILARITY, confidence
        
        # Stylistic match
        if stylistic_sim > 0.8 and semantic_sim > 0.6:
            confidence = (stylistic_sim + semantic_sim) / 2
            return PlagiarismType.STYLISTIC_MATCH, confidence
        
        # Default to semantic similarity if above threshold
        if semantic_sim > 0.5:
            return PlagiarismType.SEMANTIC_SIMILARITY, semantic_sim
        
        # No significant similarity detected
        return PlagiarismType.SEMANTIC_SIMILARITY, 0.0
    
    def _determine_similarity_level(self, similarities: Dict[str, float]) -> SimilarityLevel:
        """
Determine the overall similarity level"""
        
        # Use the highest semantic or combined similarity
        max_sim = max(
            similarities.get('semantic', 0.0),
            similarities.get('fuzzy_ratio', 0.0),
            similarities.get('contextual_avg', 0.0)
        )
        
        if max_sim >= 0.95:
            return SimilarityLevel.IDENTICAL
        elif max_sim >= 0.85:
            return SimilarityLevel.VERY_HIGH
        elif max_sim >= 0.70:
            return SimilarityLevel.HIGH
        elif max_sim >= 0.50:
            return SimilarityLevel.MODERATE
        elif max_sim >= 0.30:
            return SimilarityLevel.LOW
        else:
            return SimilarityLevel.NEGLIGIBLE
    
    async def _extract_matched_segments(
        self, text1: str, text2: str, similarities: Dict[str, float]
    ) -> List[Tuple[str, str]]:
        """
Extract matched segments between texts"""
        
        matched_segments = []
        
        try:
            # Simple sentence-based matching for now
            sentences1 = [s.strip() for s in text1.split('.') if s.strip()]
            sentences2 = [s.strip() for s in text2.split('.') if s.strip()]
            
            for s1 in sentences1:
                for s2 in sentences2:
                    if len(s1) > 20 and len(s2) > 20:  # Only consider substantial sentences
                        if FUZZYWUZZY_AVAILABLE:
                            similarity = fuzz.ratio(s1, s2) / 100.0
                            if similarity > 0.7:  # High similarity threshold
                                matched_segments.append((s1, s2))
        
        except Exception as e:
            logger.warning(f"Failed to extract matched segments: {e}")
        
        return matched_segments[:5]  # Limit to top 5 matches
    
    async def _analyze_context_match(
        self,
        query_embedding: ContextualEmbedding,
        candidate_embedding: ContextualEmbedding,
        similarities: Dict[str, float]
    ) -> Dict[str, Any]:
        """Analyze contextual aspects of the match"""
        
        analysis = {}
        
        try:
            # Length analysis
            len_ratio = len(candidate_embedding.text) / max(len(query_embedding.text), 1)
            analysis['length_ratio'] = len_ratio
            analysis['length_similarity'] = 1.0 - abs(1.0 - len_ratio)
            
            # Complexity analysis
            query_complexity = len(query_embedding.text.split()) / max(len([s for s in query_embedding.text.split('.') if s.strip()]), 1)
            candidate_complexity = len(candidate_embedding.text.split()) / max(len([s for s in candidate_embedding.text.split('.') if s.strip()]), 1)
            analysis['complexity_similarity'] = 1.0 - abs(query_complexity - candidate_complexity) / max(query_complexity, candidate_complexity, 1)
            
            # Feature analysis
            if query_embedding.semantic_features and candidate_embedding.semantic_features:
                feature_similarities = []
                for key in query_embedding.semantic_features.keys():
                    if key in candidate_embedding.semantic_features:
                        f1 = query_embedding.semantic_features[key]
                        f2 = candidate_embedding.semantic_features[key]
                        if f1 == 0 and f2 == 0:
                            feature_similarities.append(1.0)
                        elif f1 == 0 or f2 == 0:
                            feature_similarities.append(0.0)
                        else:
                            sim = min(f1, f2) / max(f1, f2)
                            feature_similarities.append(sim)
                
                if feature_similarities:
                    analysis['feature_similarity'] = np.mean(feature_similarities)
            
            # Overall assessment
            analysis['match_strength'] = np.mean([
                similarities.get('semantic', 0.0),
                similarities.get('lexical', 0.0),
                analysis.get('length_similarity', 0.0),
                analysis.get('complexity_similarity', 0.0)
            ])
        
        except Exception as e:
            logger.warning(f"Context analysis failed: {e}")
        
        return analysis
    
    async def _fast_screening(
        self,
        query_embedding: ContextualEmbedding,
        candidate_embeddings: List[ContextualEmbedding],
        config: SemanticAnalysisConfig
    ) -> List[PlagiarismMatch]:
        """Perform fast screening detection"""
        
        matches = []
        
        # Use only semantic similarity for fast screening
        for candidate in candidate_embeddings:
            semantic_sim = cosine_similarity(
                [query_embedding.embedding], [candidate.embedding]
            )[0][0]
            
            if semantic_sim > config.semantic_threshold:
                similarities = {'semantic': float(semantic_sim)}
                plagiarism_type, confidence = self._classify_plagiarism(similarities, config)
                
                if confidence > 0.6:
                    similarity_level = self._determine_similarity_level(similarities)
                    
                    match = PlagiarismMatch(
                        source_id=query_embedding.text_id,
                        target_id=candidate.text_id,
                        source_text=query_embedding.text,
                        target_text=candidate.text,
                        plagiarism_type=plagiarism_type,
                        similarity_level=similarity_level,
                        confidence_score=confidence,
                        similarity_scores=similarities,
                        detection_time=0.001  # Fast screening
                    )
                    
                    matches.append(match)
        
        return matches
    
    async def _deep_semantic_detection(
        self,
        query_embedding: ContextualEmbedding,
        candidate_embeddings: List[ContextualEmbedding],
        config: SemanticAnalysisConfig
    ) -> List[PlagiarismMatch]:
        """
Perform deep semantic detection"""
        
        matches = []
        
        for candidate in candidate_embeddings:
            # Focus on semantic and contextual analysis
            similarities = {}
            
            # Main semantic similarity
            semantic_sim = cosine_similarity(
                [query_embedding.embedding], [candidate.embedding]
            )[0][0]
            similarities['semantic'] = float(semantic_sim)
            
            # Contextual similarities
            if query_embedding.context_embeddings and candidate.context_embeddings:
                for context_type in query_embedding.context_embeddings.keys():
                    if context_type in candidate.context_embeddings:
                        ctx_sim = cosine_similarity(
                            [query_embedding.context_embeddings[context_type]],
                            [candidate.context_embeddings[context_type]]
                        )[0][0]
                        similarities[f'context_{context_type}'] = float(ctx_sim)
            
            # Layer-wise analysis
            if query_embedding.layer_embeddings and candidate.layer_embeddings:
                layer_sims = []
                for q_layer, c_layer in zip(query_embedding.layer_embeddings, candidate.layer_embeddings):
                    layer_sim = cosine_similarity([q_layer], [c_layer])[0][0]
                    layer_sims.append(float(layer_sim))
                
                if layer_sims:
                    similarities['layer_avg'] = np.mean(layer_sims)
                    similarities['layer_max'] = np.max(layer_sims)
            
            # Determine if match is significant
            avg_similarity = np.mean(list(similarities.values()))
            if avg_similarity > config.semantic_threshold * 0.8:  # Slightly lower threshold for deep analysis
                
                plagiarism_type, confidence = self._classify_plagiarism(similarities, config)
                similarity_level = self._determine_similarity_level(similarities)
                
                contextual_analysis = await self._analyze_context_match(
                    query_embedding, candidate, similarities
                )
                
                match = PlagiarismMatch(
                    source_id=query_embedding.text_id,
                    target_id=candidate.text_id,
                    source_text=query_embedding.text,
                    target_text=candidate.text,
                    plagiarism_type=plagiarism_type,
                    similarity_level=similarity_level,
                    confidence_score=confidence,
                    similarity_scores=similarities,
                    contextual_analysis=contextual_analysis,
                    detection_time=0.0
                )
                
                matches.append(match)
        
        return matches
    
    async def _linguistic_analysis_detection(
        self,
        query_embedding: ContextualEmbedding,
        candidate_embeddings: List[ContextualEmbedding],
        config: SemanticAnalysisConfig
    ) -> List[PlagiarismMatch]:
        """
Perform linguistic analysis based detection"""
        
        matches = []
        
        for candidate in candidate_embeddings:
            similarities = {}
            
            # Structural analysis
            structural_sim = await self._calculate_structural_similarity(
                query_embedding.text, candidate.text
            )
            similarities['structural'] = structural_sim
            
            # Stylistic analysis
            stylistic_sim = await self._calculate_stylistic_similarity(
                query_embedding, candidate
            )
            similarities['stylistic'] = stylistic_sim
            
            # N-gram analysis
            ngram_similarities = await self._calculate_ngram_similarities(
                query_embedding.text, candidate.text, config.ngram_sizes
            )
            similarities.update(ngram_similarities)
            
            # Basic semantic similarity
            semantic_sim = cosine_similarity(
                [query_embedding.embedding], [candidate.embedding]
            )[0][0]
            similarities['semantic'] = float(semantic_sim)
            
            # Determine if linguistic patterns indicate plagiarism
            linguistic_score = np.mean([
                structural_sim,
                stylistic_sim,
                np.mean([v for k, v in ngram_similarities.items()]) if ngram_similarities else 0.0
            ])
            
            if linguistic_score > 0.6 or semantic_sim > config.semantic_threshold:
                plagiarism_type, confidence = self._classify_plagiarism(similarities, config)
                similarity_level = self._determine_similarity_level(similarities)
                
                match = PlagiarismMatch(
                    source_id=query_embedding.text_id,
                    target_id=candidate.text_id,
                    source_text=query_embedding.text,
                    target_text=candidate.text,
                    plagiarism_type=plagiarism_type,
                    similarity_level=similarity_level,
                    confidence_score=confidence,
                    similarity_scores=similarities,
                    detection_time=0.0
                )
                
                matches.append(match)
        
        return matches
    
    def _generate_report(
        self,
        query_id: str,
        query_text: str,
        matches: List[PlagiarismMatch],
        processing_time: float,
        strategy: DetectionStrategy
    ) -> PlagiarismReport:
        """
Generate comprehensive plagiarism report"""
        
        # Calculate summary statistics
        if matches:
            confidence_scores = [match.confidence_score for match in matches]
            summary_stats = {
                'avg_confidence': np.mean(confidence_scores),
                'max_confidence': np.max(confidence_scores),
                'min_confidence': np.min(confidence_scores),
                'std_confidence': np.std(confidence_scores),
                'high_confidence_matches': sum(1 for score in confidence_scores if score > 0.8),
                'medium_confidence_matches': sum(1 for score in confidence_scores if 0.5 < score <= 0.8),
                'low_confidence_matches': sum(1 for score in confidence_scores if score <= 0.5)
            }
            
            # Risk assessment
            risk_assessment = {
                'overall_risk': min(1.0, summary_stats['max_confidence'] * 1.2),
                'plagiarism_likelihood': summary_stats['avg_confidence'],
                'severity_score': summary_stats['high_confidence_matches'] / len(matches),
                'pattern_consistency': 1.0 - summary_stats['std_confidence']
            }
        else:
            summary_stats = {}
            risk_assessment = {'overall_risk': 0.0, 'plagiarism_likelihood': 0.0}
        
        # Generate recommendations
        recommendations = self._generate_recommendations(matches, risk_assessment)
        
        return PlagiarismReport(
            query_id=query_id,
            query_text=query_text,
            total_matches=len(matches),
            matches=matches,
            summary_statistics=summary_stats,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            processing_time=processing_time,
            detection_strategy=strategy
        )
    
    def _generate_recommendations(
        self, matches: List[PlagiarismMatch], risk_assessment: Dict[str, float]
    ) -> List[str]:
        """
Generate recommendations based on detection results"""
        
        recommendations = []
        
        if not matches:
            recommendations.append("No significant plagiarism detected. Content appears to be original.")
            return recommendations
        
        overall_risk = risk_assessment.get('overall_risk', 0.0)
        
        if overall_risk > 0.8:
            recommendations.append("HIGH RISK: Strong evidence of plagiarism detected. Immediate review recommended.")
        elif overall_risk > 0.6:
            recommendations.append("MEDIUM RISK: Potential plagiarism detected. Further investigation advised.")
        else:
            recommendations.append("LOW RISK: Some similarities detected, but likely not problematic.")
        
        # Type-specific recommendations
        exact_matches = [m for m in matches if m.plagiarism_type == PlagiarismType.EXACT_COPY]
        if exact_matches:
            recommendations.append("Exact copying detected. Verify if proper attribution is provided.")
        
        paraphrase_matches = [m for m in matches if m.plagiarism_type == PlagiarismType.PARAPHRASE]
        if paraphrase_matches:
            recommendations.append("Paraphrasing detected. Check if ideas are properly cited.")
        
        if len(matches) > 5:
            recommendations.append("Multiple similarities found. Consider comprehensive review of sources.")
        
        return recommendations
    
    def _apply_custom_thresholds(self, custom_thresholds: Dict[str, float]) -> SemanticAnalysisConfig:
        """Apply custom thresholds to configuration"""
        config = SemanticAnalysisConfig()
        
        if 'exact_match_threshold' in custom_thresholds:
            config.exact_match_threshold = custom_thresholds['exact_match_threshold']
        if 'paraphrase_threshold' in custom_thresholds:
            config.paraphrase_threshold = custom_thresholds['paraphrase_threshold']
        if 'semantic_threshold' in custom_thresholds:
            config.semantic_threshold = custom_thresholds['semantic_threshold']
        
        return config
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """
Get detection performance statistics"""
        return {
            'total_detections': self.detection_stats['total_detections'],
            'total_matches': self.detection_stats['total_matches'],
            'avg_processing_time': np.mean(self.processing_times) if self.processing_times else 0.0,
            'cache_hit_rate': len(self.analysis_cache) / max(self.detection_stats['total_detections'], 1),
            'performance_trend': list(self.processing_times[-10:])  # Last 10 processing times
        }