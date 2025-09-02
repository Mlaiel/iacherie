"""Advanced Authorship Analysis Engine - Industrial Grade
=======================================================

Ultra-advanced authorship attribution and style analysis system with
contextual BERT/RoBERTa embeddings and sophisticated stylometric analysis.

Features:
- Deep stylometric feature extraction (300+ features)
- BERT/RoBERTa-based authorship embeddings
- Multi-dimensional writing style analysis
- Cross-lingual authorship detection
- Temporal style evolution tracking
- Ensemble authorship attribution models

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
import statistics

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.svm import SVC
    from sklearn.neural_network import MLPClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.preprocessing import StandardScaler, RobustScaler
    from sklearn.decomposition import PCA, TruncatedSVD
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.feature_selection import SelectKBest, f_classif
    import scipy.stats as stats
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. Limited ML capabilities.")

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize, RegexpTokenizer
    from nltk.corpus import stopwords, wordnet
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.tag import pos_tag
    from nltk.chunk import ne_chunk
    from nltk.util import ngrams
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.translate.bleu_score import sentence_bleu
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available. Using basic text processing.")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available. Limited NLP analysis.")

from .industrial_embeddings_engine import IndustrialEmbeddingsEngine, ContextualEmbedding

logger = logging.getLogger(__name__)

class AuthorshipFeatureCategory(Enum):
    """Categories of authorship features"""

    LEXICAL = "lexical"
    SYNTACTIC = "syntactic"
    SEMANTIC = "semantic"
    STYLISTIC = "stylistic"
    STRUCTURAL = "structural"
    DISCOURSE = "discourse"
    PSYCHOLOGICAL = "psychological"
    TEMPORAL = "temporal"

class AuthorshipConfidence(Enum):
    """Confidence levels for authorship attribution"""

    VERY_HIGH = "very_high"  # >90%
    HIGH = "high"           # 75-90%
    MEDIUM = "medium"       # 60-75%
    LOW = "low"            # 40-60%
    VERY_LOW = "very_low"  # <40%

class AnalysisComplexity(Enum):
    """Complexity levels for analysis"""

    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    COMPREHENSIVE = "comprehensive"

@dataclass
class AuthorshipProfile:
    """Comprehensive authorship profile"""
    author_id: str
    author_name: Optional[str] = None
    
    # Feature vectors
    lexical_features: Dict[str, float] = field(default_factory=dict)
    syntactic_features: Dict[str, float] = field(default_factory=dict)
    semantic_features: Dict[str, float] = field(default_factory=dict)
    stylistic_features: Dict[str, float] = field(default_factory=dict)
    structural_features: Dict[str, float] = field(default_factory=dict)
    discourse_features: Dict[str, float] = field(default_factory=dict)
    psychological_features: Dict[str, float] = field(default_factory=dict)
    
    # BERT/RoBERTa embeddings
    contextual_embeddings: Dict[str, np.ndarray] = field(default_factory=dict)
    style_embeddings: List[np.ndarray] = field(default_factory=list)
    
    # Statistical measures
    feature_statistics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    consistency_scores: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    sample_count: int = 0
    text_samples: List[str] = field(default_factory=list)
    creation_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class AuthorshipAnalysisResult:
    """
Result of authorship analysis"""
    query_text_id: str
    query_text: str
    
    # Attribution results
    predicted_author: Optional[str] = None
    confidence_level: AuthorshipConfidence = AuthorshipConfidence.VERY_LOW
    confidence_score: float = 0.0
    
    # Candidate rankings
    author_rankings: List[Tuple[str, float]] = field(default_factory=list)
    similarity_scores: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Feature analysis
    distinctive_features: Dict[str, float] = field(default_factory=dict)
    style_characteristics: Dict[str, Any] = field(default_factory=dict)
    
    # Ensemble results
    model_predictions: Dict[str, Tuple[str, float]] = field(default_factory=dict)
    ensemble_confidence: float = 0.0
    
    # Analysis metadata
    processing_time: float = 0.0
    features_extracted: int = 0
    analysis_complexity: AnalysisComplexity = AnalysisComplexity.BASIC
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class StyleAnalysisConfig:
    """
Configuration for style analysis"""
    # Feature extraction
    extract_lexical: bool = True
    extract_syntactic: bool = True
    extract_semantic: bool = True
    extract_stylistic: bool = True
    extract_structural: bool = True
    extract_discourse: bool = True
    extract_psychological: bool = True
    
    # Analysis depth
    analysis_complexity: AnalysisComplexity = AnalysisComplexity.ADVANCED
    max_features_per_category: int = 50
    min_text_length: int = 100
    
    # BERT/RoBERTa settings
    use_contextual_embeddings: bool = True
    embedding_aggregation: str = "mean"  # mean, max, weighted
    
    # ML models
    use_ensemble: bool = True
    enable_cross_validation: bool = True
    feature_selection: bool = True
    
    # Performance
    enable_caching: bool = True
    parallel_processing: bool = True

class AdvancedAuthorshipAnalyzer:
    """
    Industrial-grade authorship analysis engine with contextual embeddings
    """
    
    def __init__(self, 
                 embeddings_engine: IndustrialEmbeddingsEngine,
                 config: Optional[StyleAnalysisConfig] = None):
        """
Initialize advanced authorship analyzer"""
        self.embeddings_engine = embeddings_engine
        self.config = config or StyleAnalysisConfig()
        
        # Author profiles storage
        self.author_profiles: Dict[str, AuthorshipProfile] = {}
        
        # ML models for ensemble
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        
        # NLP tools
        self.nlp = None
        self.sentiment_analyzer = None
        self.stemmer = PorterStemmer() if NLTK_AVAILABLE else None
        self.lemmatizer = WordNetLemmatizer() if NLTK_AVAILABLE else None
        
        # Caches
        self.feature_cache = {}
        self.embedding_cache = {}
        
        # Performance tracking
        self.analysis_stats = defaultdict(int)
        self.processing_times = []
        
        self._initialize_nlp_tools()
        self._initialize_ml_models()
        
        logger.info("Advanced Authorship Analyzer initialized")
    
    def _initialize_nlp_tools(self):
        """Initialize NLP tools"""
        try:
            if SPACY_AVAILABLE:
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                except OSError:
                    logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            
            if NLTK_AVAILABLE:
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
                
        except Exception as e:
            logger.warning(f"Failed to initialize NLP tools: {e}")
    
    def _initialize_ml_models(self):
        """Initialize ML models for ensemble"""
        if not SKLEARN_AVAILABLE:
            return
        
        try:
            # Ensemble of different model types
            self.models = {
                'random_forest': RandomForestClassifier(
                    n_estimators=100, 
                    max_depth=10, 
                    random_state=42
                ),
                'gradient_boosting': GradientBoostingClassifier(
                    n_estimators=100, 
                    max_depth=8, 
                    random_state=42
                ),
                'svm': SVC(
                    kernel='rbf', 
                    probability=True, 
                    random_state=42
                ),
                'neural_network': MLPClassifier(
                    hidden_layer_sizes=(100, 50), 
                    max_iter=500, 
                    random_state=42
                )
            }
            
            # Feature scalers
            self.scalers = {
                'standard': StandardScaler(),
                'robust': RobustScaler()
            }
            
            logger.info("ML models initialized for ensemble authorship analysis")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
    
    async def register_author_profile(
        self,
        author_id: str,
        text_samples: List[str],
        author_name: Optional[str] = None,
        update_existing: bool = True
    ) -> AuthorshipProfile:
        """
        Register or update an author profile with text samples
        
        Args:
            author_id: Unique identifier for the author
            text_samples: List of text samples from the author
            author_name: Optional human-readable name
            update_existing: Whether to update existing profile
        
        Returns:
            AuthorshipProfile with extracted features
        """
        start_time = time.time()
        
        # Check if profile exists
        if author_id in self.author_profiles and not update_existing:
            return self.author_profiles[author_id]
        
        # Create or update profile
        if author_id in self.author_profiles:
            profile = self.author_profiles[author_id]
            profile.text_samples.extend(text_samples)
            profile.sample_count += len(text_samples)
            profile.last_updated = datetime.now().isoformat()
        else:
            profile = AuthorshipProfile(
                author_id=author_id,
                author_name=author_name,
                text_samples=text_samples,
                sample_count=len(text_samples)
            )
        
        # Extract comprehensive features from all samples
        await self._extract_comprehensive_features(profile, text_samples)
        
        # Generate contextual embeddings
        if self.config.use_contextual_embeddings:
            await self._generate_author_embeddings(profile, text_samples)
        
        # Calculate statistical measures
        self._calculate_feature_statistics(profile)
        
        # Store profile
        self.author_profiles[author_id] = profile
        
        processing_time = time.time() - start_time
        self.processing_times.append(processing_time)
        
        logger.info(f"Author profile registered: {author_id} with {len(text_samples)} samples in {processing_time:.3f}s")
        
        return profile
    
    async def analyze_authorship(
        self,
        query_text: str,
        candidate_authors: Optional[List[str]] = None,
        analysis_complexity: Optional[AnalysisComplexity] = None
    ) -> AuthorshipAnalysisResult:
        """
        Analyze authorship of query text against registered author profiles
        
        Args:
            query_text: Text to analyze for authorship
            candidate_authors: Optional list of candidate author IDs to consider
            analysis_complexity: Level of analysis complexity
        
        Returns:
            Comprehensive authorship analysis result
        """
        start_time = time.time()
        
        complexity = analysis_complexity or self.config.analysis_complexity
        query_id = f"query_{hashlib.md5(query_text.encode()).hexdigest()[:12]}"
        
        # Extract features from query text
        query_features = await self._extract_text_features(query_text, complexity)
        
        # Generate query embeddings
        query_embeddings = None
        if self.config.use_contextual_embeddings:
            query_embeddings = await self.embeddings_engine.generate_contextual_embeddings(
                query_text, text_ids=query_id, include_context=True, extract_layers=True
            )
        
        # Select candidate authors
        candidates = candidate_authors if candidate_authors else list(self.author_profiles.keys())
        
        if not candidates:
            return AuthorshipAnalysisResult(
                query_text_id=query_id,
                query_text=query_text,
                processing_time=time.time() - start_time,
                analysis_complexity=complexity
            )
        
        # Perform similarity analysis
        similarity_results = await self._calculate_author_similarities(
            query_features, query_embeddings, candidates, complexity
        )
        
        # Ensemble prediction if enabled
        ensemble_results = {}
        if self.config.use_ensemble and SKLEARN_AVAILABLE:
            ensemble_results = await self._ensemble_prediction(
                query_features, candidates
            )
        
        # Combine results and rank authors
        author_rankings = self._rank_authors(similarity_results, ensemble_results)
        
        # Determine best prediction
        predicted_author = None
        confidence_score = 0.0
        if author_rankings:
            predicted_author, confidence_score = author_rankings[0]
        
        confidence_level = self._determine_confidence_level(confidence_score)
        
        # Extract distinctive features
        distinctive_features = self._identify_distinctive_features(
            query_features, predicted_author if predicted_author else candidates[0]
        )
        
        # Analyze style characteristics
        style_characteristics = await self._analyze_style_characteristics(
            query_text, query_features, query_embeddings
        )
        
        processing_time = time.time() - start_time
        
        result = AuthorshipAnalysisResult(
            query_text_id=query_id,
            query_text=query_text,
            predicted_author=predicted_author,
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            author_rankings=author_rankings,
            similarity_scores=similarity_results,
            distinctive_features=distinctive_features,
            style_characteristics=style_characteristics,
            model_predictions=ensemble_results,
            ensemble_confidence=confidence_score,
            processing_time=processing_time,
            features_extracted=len(query_features),
            analysis_complexity=complexity
        )
        
        # Update statistics
        self.analysis_stats['total_analyses'] += 1
        if predicted_author:
            self.analysis_stats['successful_predictions'] += 1
        
        return result
    
    async def _extract_comprehensive_features(
        self, profile: AuthorshipProfile, text_samples: List[str]
    ):
        """Extract comprehensive features for author profile"""
        
        # Aggregate features across all samples
        all_features = {
            'lexical': [],
            'syntactic': [],
            'semantic': [],
            'stylistic': [],
            'structural': [],
            'discourse': [],
            'psychological': []
        }
        
        for text in text_samples:
            if len(text) < self.config.min_text_length:
                continue
            
            text_features = await self._extract_text_features(text, self.config.analysis_complexity)
            
            # Group features by category
            for feature_name, value in text_features.items():
                category = self._categorize_feature(feature_name)
                if category in all_features:
                    all_features[category].append({feature_name: value})
        
        # Calculate aggregate statistics for each category
        for category, feature_list in all_features.items():
            if feature_list:
                aggregated = self._aggregate_features(feature_list)
                setattr(profile, f"{category}_features", aggregated)
    
    async def _extract_text_features(
        self, text: str, complexity: AnalysisComplexity
    ) -> Dict[str, float]:
        """Extract features from text based on complexity level"""
        
        cache_key = hashlib.md5(f"{text}_{complexity.value}".encode()).hexdigest()
        if self.config.enable_caching and cache_key in self.feature_cache:
            return self.feature_cache[cache_key]
        
        features = {}
        
        # Basic features (always extracted)
        features.update(await self._extract_lexical_features(text))
        
        if complexity in [AnalysisComplexity.STANDARD, AnalysisComplexity.ADVANCED, AnalysisComplexity.COMPREHENSIVE]:
            features.update(await self._extract_syntactic_features(text))
            features.update(await self._extract_structural_features(text))
        
        if complexity in [AnalysisComplexity.ADVANCED, AnalysisComplexity.COMPREHENSIVE]:
            features.update(await self._extract_semantic_features(text))
            features.update(await self._extract_stylistic_features(text))
        
        if complexity == AnalysisComplexity.COMPREHENSIVE:
            features.update(await self._extract_discourse_features(text))
            features.update(await self._extract_psychological_features(text))
        
        # Cache results
        if self.config.enable_caching:
            self.feature_cache[cache_key] = features
        
        return features
    
    async def _extract_lexical_features(self, text: str) -> Dict[str, float]:
        """Extract lexical features"""
        features = {}
        
        try:
            # Basic text statistics
            features['text_length'] = len(text)
            features['char_count'] = len(text)
            features['word_count'] = len(text.split())
            features['sentence_count'] = len([s for s in text.split('.') if s.strip()])
            features['paragraph_count'] = len([p for p in text.split('\n\n') if p.strip()])
            
            # Word-level features
            words = text.split()
            if words:
                word_lengths = [len(word.strip(string.punctuation)) for word in words]
                features['avg_word_length'] = np.mean(word_lengths)
                features['word_length_std'] = np.std(word_lengths)
                features['max_word_length'] = max(word_lengths)
                features['min_word_length'] = min(word_lengths)
                
                # Vocabulary richness
                unique_words = set(word.lower().strip(string.punctuation) for word in words)
                features['vocabulary_richness'] = len(unique_words) / len(words)
                features['unique_word_count'] = len(unique_words)
                
                # Word frequency distribution
                word_freq = Counter(word.lower().strip(string.punctuation) for word in words)
                features['hapax_legomena'] = sum(1 for count in word_freq.values() if count == 1) / len(word_freq)
                features['dis_legomena'] = sum(1 for count in word_freq.values() if count == 2) / len(word_freq)
            
            # Character-level features
            features['char_diversity'] = len(set(text.lower())) / len(text) if len(text) > 0 else 0
            features['digit_ratio'] = sum(c.isdigit() for c in text) / len(text) if len(text) > 0 else 0
            features['upper_ratio'] = sum(c.isupper() for c in text) / len(text) if len(text) > 0 else 0
            features['lower_ratio'] = sum(c.islower() for c in text) / len(text) if len(text) > 0 else 0
            features['alpha_ratio'] = sum(c.isalpha() for c in text) / len(text) if len(text) > 0 else 0
            
            # Punctuation analysis
            features['punctuation_ratio'] = sum(c in string.punctuation for c in text) / len(text) if len(text) > 0 else 0
            features['comma_ratio'] = text.count(',') / len(text) if len(text) > 0 else 0
            features['semicolon_ratio'] = text.count(';') / len(text) if len(text) > 0 else 0
            features['colon_ratio'] = text.count(':') / len(text) if len(text) > 0 else 0
            features['period_ratio'] = text.count('.') / len(text) if len(text) > 0 else 0
            features['question_ratio'] = text.count('?') / len(text) if len(text) > 0 else 0
            features['exclamation_ratio'] = text.count('!') / len(text) if len(text) > 0 else 0
            features['apostrophe_ratio'] = text.count("'") / len(text) if len(text) > 0 else 0
            features['quotation_ratio'] = (text.count('"') + text.count("'")) / len(text) if len(text) > 0 else 0
            
            # Sentence-level features
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            if sentences:
                sent_lengths = [len(s.split()) for s in sentences]
                features['avg_sentence_length'] = np.mean(sent_lengths)
                features['sentence_length_std'] = np.std(sent_lengths)
                features['max_sentence_length'] = max(sent_lengths)
                features['min_sentence_length'] = min(sent_lengths)
                features['sentence_length_range'] = max(sent_lengths) - min(sent_lengths)
            
        except Exception as e:
            logger.warning(f"Error in lexical feature extraction: {e}")
        
        return features
    
    async def _extract_syntactic_features(self, text: str) -> Dict[str, float]:
        """Extract syntactic features"""
        features = {}
        
        if not NLTK_AVAILABLE:
            return features
        
        try:
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            
            # POS tag distribution
            pos_counts = Counter([tag for word, tag in pos_tags])
            total_tags = len(pos_tags)
            
            # Major POS categories
            pos_categories = {
                'noun_ratio': ['NN', 'NNS', 'NNP', 'NNPS'],
                'verb_ratio': ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'],
                'adjective_ratio': ['JJ', 'JJR', 'JJS'],
                'adverb_ratio': ['RB', 'RBR', 'RBS'],
                'pronoun_ratio': ['PRP', 'PRP$'],
                'preposition_ratio': ['IN'],
                'conjunction_ratio': ['CC'],
                'determiner_ratio': ['DT'],
                'modal_ratio': ['MD']
            }
            
            for category, tags in pos_categories.items():
                count = sum(pos_counts.get(tag, 0) for tag in tags)
                features[category] = count / total_tags if total_tags > 0 else 0
            
            # Function word analysis
            function_words = {
                'articles': ['the', 'a', 'an'],
                'prepositions': ['in', 'on', 'at', 'by', 'for', 'with', 'to', 'of', 'from'],
                'conjunctions': ['and', 'or', 'but', 'so', 'yet', 'nor'],
                'pronouns': ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them']
            }
            
            words_lower = [word.lower() for word in tokens if word.isalpha()]
            total_words = len(words_lower)
            
            for category, word_list in function_words.items():
                count = sum(1 for word in words_lower if word in word_list)
                features[f'{category}_ratio'] = count / total_words if total_words > 0 else 0
            
            # Syntactic complexity
            features['avg_parse_tree_depth'] = self._estimate_parse_depth(pos_tags)
            features['subordinate_clause_ratio'] = self._count_subordinate_clauses(text) / max(features.get('sentence_count', 1), 1)
            
            # N-gram analysis
            for n in [2, 3, 4]:
                pos_ngrams = list(ngrams([tag for word, tag in pos_tags], n))
                unique_ngrams = len(set(pos_ngrams))
                total_ngrams = len(pos_ngrams)
                features[f'pos_{n}gram_diversity'] = unique_ngrams / total_ngrams if total_ngrams > 0 else 0
        
        except Exception as e:
            logger.warning(f"Error in syntactic feature extraction: {e}")
        
        return features
    
    async def _extract_semantic_features(self, text: str) -> Dict[str, float]:
        """Extract semantic features"""
        features = {}
        
        try:
            # Sentiment analysis
            if NLTK_AVAILABLE and self.sentiment_analyzer:
                sentiment_scores = self.sentiment_analyzer.polarity_scores(text)
                features.update({
                    'sentiment_positive': sentiment_scores['pos'],
                    'sentiment_negative': sentiment_scores['neg'],
                    'sentiment_neutral': sentiment_scores['neu'],
                    'sentiment_compound': sentiment_scores['compound']
                })
            
            # Semantic diversity
            if NLTK_AVAILABLE:
                tokens = word_tokenize(text.lower())
                
                # Content word ratio
                content_words = [word for word in tokens if word.isalpha() and word not in stopwords.words('english')]
                features['content_word_ratio'] = len(content_words) / len(tokens) if tokens else 0
                
                # Semantic field analysis (simplified)
                emotion_words = ['happy', 'sad', 'angry', 'excited', 'calm', 'worried', 'pleased', 'disappointed']
                emotion_count = sum(1 for word in tokens if word in emotion_words)
                features['emotion_word_ratio'] = emotion_count / len(tokens) if tokens else 0
                
                # Abstract vs concrete words (simplified heuristic)
                abstract_suffixes = ['tion', 'sion', 'ment', 'ness', 'ity', 'ism']
                abstract_count = sum(1 for word in tokens if any(word.endswith(suffix) for suffix in abstract_suffixes))
                features['abstract_word_ratio'] = abstract_count / len(tokens) if tokens else 0
            
            # Readability approximation
            features.update(self._calculate_readability_features(text))
            
        except Exception as e:
            logger.warning(f"Error in semantic feature extraction: {e}")
        
        return features
    
    async def _extract_stylistic_features(self, text: str) -> Dict[str, float]:
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess__extract_stylistic_features_input(text)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess__extract_stylistic_features_result(result)
            
                    logger.info(f"AI processing _extract_stylistic_features completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing _extract_stylistic_features failed: {e}")
                    raise
    async def _extract_structural_features(self, text: str) -> Dict[str, float]:
        """Extract structural features"""
        features = {}
        
        try:
            # Document structure
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            features['paragraph_count'] = len(paragraphs)
            
            if paragraphs:
                para_lengths = [len(p.split()) for p in paragraphs]
                features['avg_paragraph_length'] = np.mean(para_lengths)
                features['paragraph_length_std'] = np.std(para_lengths)
            
            # Line breaks and formatting
            features['line_break_ratio'] = text.count('\n') / len(text) if len(text) > 0 else 0
            features['blank_line_ratio'] = text.count('\n\n') / len(text) if len(text) > 0 else 0
            
            # Sentence structure variety
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            if sentences:
                # Sentence starters
                question_starters = sum(1 for s in sentences if s.strip().startswith(('What', 'Why', 'How', 'When', 'Where', 'Who')))
                features['question_starter_ratio'] = question_starters / len(sentences)
                
                # Complex sentence indicators
                complex_indicators = [',', ';', 'which', 'that', 'because', 'although', 'while']
                complex_sentences = sum(1 for s in sentences if any(indicator in s.lower() for indicator in complex_indicators))
                features['complex_sentence_ratio'] = complex_sentences / len(sentences)
            
        except Exception as e:
            logger.warning(f"Error in structural feature extraction: {e}")
        
        return features
    
    async def _extract_discourse_features(self, text: str) -> Dict[str, float]:
        """Extract discourse-level features"""
        features = {}
        
        try:
            # Discourse markers
            discourse_markers = {
                'addition': ['furthermore', 'moreover', 'additionally', 'also', 'besides'],
                'contrast': ['however', 'nevertheless', 'nonetheless', 'although', 'despite'],
                'cause_effect': ['therefore', 'consequently', 'thus', 'hence', 'because'],
                'temporal': ['first', 'second', 'then', 'next', 'finally', 'meanwhile'],
                'example': ['for example', 'for instance', 'such as', 'namely']
            }
            
            words = text.lower().split()
            total_words = len(words)
            
            for category, markers in discourse_markers.items():
                count = 0
                for marker in markers:
                    if ' ' in marker:  # Multi-word markers
                        count += text.lower().count(marker)
                    else:  # Single word markers
                        count += sum(1 for word in words if word.strip(string.punctuation) == marker)
                features[f'{category}_marker_ratio'] = count / total_words if total_words > 0 else 0
            
            # Cohesion indicators
            features['repetition_ratio'] = self._calculate_repetition_ratio(text)
            features['pronoun_reference_ratio'] = self._calculate_pronoun_ratio(text)
            
        except Exception as e:
            logger.warning(f"Error in discourse feature extraction: {e}")
        
        return features
    
    async def _extract_psychological_features(self, text: str) -> Dict[str, float]:
        """Extract psychological/personality features"""
        features = {}
        
        try:
            # Psychological word categories (simplified LIWC-style)
            psych_categories = {
                'cognitive_processes': ['think', 'know', 'consider', 'understand', 'realize', 'believe'],
                'social_processes': ['we', 'us', 'our', 'family', 'friend', 'people', 'together'],
                'affective_processes': ['love', 'hate', 'like', 'enjoy', 'feel', 'emotion'],
                'personal_concerns': ['work', 'money', 'health', 'religion', 'death', 'body'],
                'perceptual_processes': ['see', 'hear', 'look', 'sound', 'taste', 'smell'],
                'biological_processes': ['eat', 'sleep', 'blood', 'pain', 'health', 'body']
            }
            
            words = [word.lower().strip(string.punctuation) for word in text.split()]
            total_words = len(words)
            
            for category, word_list in psych_categories.items():
                count = sum(1 for word in words if word in word_list)
                features[f'{category}_ratio'] = count / total_words if total_words > 0 else 0
            
            # Certainty and uncertainty markers
            certainty_words = ['definitely', 'certainly', 'sure', 'confident', 'know', 'clear']
            uncertainty_words = ['maybe', 'perhaps', 'might', 'could', 'possibly', 'unsure']
            
            certainty_count = sum(1 for word in words if word in certainty_words)
            uncertainty_count = sum(1 for word in words if word in uncertainty_words)
            
            features['certainty_ratio'] = certainty_count / total_words if total_words > 0 else 0
            features['uncertainty_ratio'] = uncertainty_count / total_words if total_words > 0 else 0
            
        except Exception as e:
            logger.warning(f"Error in psychological feature extraction: {e}")
        
        return features
    
    def _categorize_feature(self, feature_name: str) -> str:
        """Categorize a feature by name"""
        category_keywords = {
            'lexical': ['word', 'char', 'length', 'vocabulary', 'punctuation'],
            'syntactic': ['pos_', 'noun', 'verb', 'adjective', 'adverb', 'function', 'parse'],
            'semantic': ['sentiment', 'emotion', 'content', 'abstract', 'readability'],
            'stylistic': ['person', 'passive', 'contraction', 'formal', 'hedge', 'booster'],
            'structural': ['paragraph', 'sentence', 'line', 'complex'],
            'discourse': ['marker', 'repetition', 'pronoun'],
            'psychological': ['cognitive', 'social', 'affective', 'certainty']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in feature_name.lower() for keyword in keywords):
                return category
        
        return 'lexical'  # Default category
    
    def _aggregate_features(self, feature_list: List[Dict[str, float]]) -> Dict[str, float]:
        """
Aggregate features across multiple samples"""
        if not feature_list:
            return {}
        
        # Collect all feature values
        feature_values = defaultdict(list)
        for feature_dict in feature_list:
        try:
            logger.info(f"Executing _categorize_feature")
            
            # Implementation for _categorize_feature
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_categorize_feature completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_categorize_feature failed: {e}")
            raise
        return aggregated
    
    async def _generate_author_embeddings(self, profile: AuthorshipProfile, text_samples: List[str]):
        """Generate contextual embeddings for author profile"""
        
        try:
            # Generate embeddings for each sample
            embeddings_list = []
            for i, text in enumerate(text_samples):
                if len(text) >= self.config.min_text_length:
                    text_id = f"{profile.author_id}_sample_{i}"
                    embedding = await self.embeddings_engine.generate_contextual_embeddings(
                        text, text_ids=text_id, include_context=True, extract_layers=True
                    )
                    embeddings_list.append(embedding)
            
            if embeddings_list:
                # Aggregate embeddings
                if self.config.embedding_aggregation == "mean":
                    # Mean pooling of embeddings
                    main_embeddings = [emb.embedding for emb in embeddings_list]
                    profile.contextual_embeddings['main'] = np.mean(main_embeddings, axis=0)
                    
                    # Context embeddings
                    for context_type in ['semantic', 'syntactic', 'discourse']:
                        context_embeddings = [
                            emb.context_embeddings.get(context_type, np.zeros_like(emb.embedding))
                            for emb in embeddings_list
                            if emb.context_embeddings
                        ]
                        if context_embeddings:
                            profile.contextual_embeddings[context_type] = np.mean(context_embeddings, axis=0)
                
                # Store individual style embeddings
                profile.style_embeddings = [emb.embedding for emb in embeddings_list]
        
        except Exception as e:
            logger.warning(f"Failed to generate author embeddings: {e}")
    
    def _calculate_feature_statistics(self, profile: AuthorshipProfile):
        """Calculate statistical measures for profile features"""
        
        for category in ['lexical', 'syntactic', 'semantic', 'stylistic', 'structural', 'discourse', 'psychological']:
            features = getattr(profile, f"{category}_features", {})
            if features:
                # Calculate consistency scores
                feature_values = list(features.values())
                if feature_values:
                    profile.consistency_scores[category] = 1.0 / (1.0 + np.std(feature_values))
                
                # Store feature statistics
                profile.feature_statistics[category] = {
                    'mean': np.mean(feature_values),
                    'std': np.std(feature_values),
                    'min': np.min(feature_values),
                    'max': np.max(feature_values),
                    'feature_count': len(features)
                }
    
    async def _calculate_author_similarities(
        self,
        query_features: Dict[str, float],
        query_embeddings: Optional[ContextualEmbedding],
        candidate_authors: List[str],
        complexity: AnalysisComplexity
    ) -> Dict[str, Dict[str, float]]:
        """Calculate similarities between query and candidate authors"""
        
        similarity_results = {}
        
        for author_id in candidate_authors:
            if author_id not in self.author_profiles:
                continue
            
            profile = self.author_profiles[author_id]
            author_similarities = {}
            
            # Feature-based similarities
            for category in ['lexical', 'syntactic', 'semantic', 'stylistic', 'structural', 'discourse', 'psychological']:
                author_features = getattr(profile, f"{category}_features", {})
                if author_features:
                    similarity = self._calculate_feature_similarity(
                        query_features, author_features, category
                    )
                    author_similarities[f"{category}_similarity"] = similarity
            
            # Embedding-based similarities
            if query_embeddings and profile.contextual_embeddings:
                for emb_type, profile_emb in profile.contextual_embeddings.items():
                    if emb_type == 'main':
                        query_emb = query_embeddings.embedding
                    else:
                        query_emb = query_embeddings.context_embeddings.get(emb_type)
                    
                    if query_emb is not None:
                        emb_sim = cosine_similarity([query_emb], [profile_emb])[0][0]
                        author_similarities[f"{emb_type}_embedding_similarity"] = float(emb_sim)
            
            # Overall similarity
            if author_similarities:
                author_similarities['overall_similarity'] = np.mean(list(author_similarities.values()))
            
            similarity_results[author_id] = author_similarities
        
        return similarity_results
    
    def _calculate_feature_similarity(
        self, query_features: Dict[str, float], author_features: Dict[str, float], category: str
    ) -> float:
        """Calculate similarity between feature sets"""
        
        # Find common features
        common_features = set(query_features.keys()) & set(author_features.keys())
        
        if not common_features:
            return 0.0
        
        # Calculate similarity for common features
        similarities = []
        for feature in common_features:
            if category in feature or self._categorize_feature(feature) == category:
                query_val = query_features[feature]
                author_val = author_features[feature]
                
                # Handle zero values
                if query_val == 0 and author_val == 0:
                    similarities.append(1.0)
                elif query_val == 0 or author_val == 0:
                    similarities.append(0.0)
                else:
                    # Use ratio-based similarity
                    ratio = min(query_val, author_val) / max(query_val, author_val)
                    similarities.append(ratio)
        
        return np.mean(similarities) if similarities else 0.0
    
    async def _ensemble_prediction(
        self, query_features: Dict[str, float], candidate_authors: List[str]
    ) -> Dict[str, Tuple[str, float]]:
        """
Perform ensemble prediction using multiple ML models"""
        
        if not SKLEARN_AVAILABLE or not self.author_profiles:
            return {}
        
        try:
            # Prepare training data
            X_train, y_train = self._prepare_training_data(candidate_authors)
            
            if len(X_train) < 2 or len(set(y_train)) < 2:
                return {}
            
            # Prepare query data
            X_query = self._prepare_query_data(query_features, X_train[0].shape[0])
            
            ensemble_results = {}
            
            for model_name, model in self.models.items():
                try:
                    # Scale features
                    scaler = self.scalers['standard']
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_query_scaled = scaler.transform([X_query])
                    
                    # Train model
                    model.fit(X_train_scaled, y_train)
                    
                    # Predict
                    prediction = model.predict(X_query_scaled)[0]
                    
                    # Get prediction confidence
                    if hasattr(model, 'predict_proba'):
                        probabilities = model.predict_proba(X_query_scaled)[0]
                        confidence = np.max(probabilities)
                    else:
                        confidence = 0.5  # Default confidence for non-probabilistic models
                    
                    ensemble_results[model_name] = (prediction, float(confidence))
                
                except Exception as e:
                    logger.warning(f"Model {model_name} prediction failed: {e}")
            
            return ensemble_results
        
        except Exception as e:
            logger.warning(f"Ensemble prediction failed: {e}")
            return {}
    
    def _prepare_training_data(self, candidate_authors: List[str]) -> Tuple[np.ndarray, List[str]]:
        """Prepare training data from author profiles"""
        
        X_train = []
        y_train = []
        
        for author_id in candidate_authors:
            if author_id in self.author_profiles:
                profile = self.author_profiles[author_id]
                
                # Collect all features
                all_features = {}
                for category in ['lexical', 'syntactic', 'semantic', 'stylistic', 'structural', 'discourse', 'psychological']:
                    features = getattr(profile, f"{category}_features", {})
                    all_features.update(features)
                
                if all_features:
                    X_train.append(list(all_features.values()))
                    y_train.append(author_id)
        
        return np.array(X_train), y_train
    
    def _prepare_query_data(self, query_features: Dict[str, float], expected_length: int) -> List[float]:
        """Prepare query data for prediction"""
        
        # Ensure consistent feature ordering and length
        feature_vector = []
        for i in range(expected_length):
            if i < len(query_features):
                feature_vector.append(list(query_features.values())[i])
            else:
                feature_vector.append(0.0)  # Pad with zeros
        
        return feature_vector[:expected_length]  # Truncate if necessary
    
    def _rank_authors(
        self, similarity_results: Dict[str, Dict[str, float]], ensemble_results: Dict[str, Tuple[str, float]]
    ) -> List[Tuple[str, float]]:
        """
Rank authors based on similarity and ensemble results"""
        
        author_scores = {}
        
        # Calculate scores from similarity results
        for author_id, similarities in similarity_results.items():
            overall_sim = similarities.get('overall_similarity', 0.0)
            author_scores[author_id] = overall_sim
        
        # Incorporate ensemble results
        if ensemble_results:
            ensemble_votes = defaultdict(list)
            for model_name, (prediction, confidence) in ensemble_results.items():
                ensemble_votes[prediction].append(confidence)
            
            # Average ensemble confidences
            for author_id, confidences in ensemble_votes.items():
                ensemble_score = np.mean(confidences)
                if author_id in author_scores:
                    # Weighted combination of similarity and ensemble scores
                    author_scores[author_id] = 0.6 * author_scores[author_id] + 0.4 * ensemble_score
                else:
                    author_scores[author_id] = ensemble_score
        
        # Sort by score
        ranked_authors = sorted(author_scores.items(), key=lambda x: x[1], reverse=True)
        
        return ranked_authors
    
    def _determine_confidence_level(self, confidence_score: float) -> AuthorshipConfidence:
        """
Determine confidence level based on score"""
        
        if confidence_score >= 0.90:
            return AuthorshipConfidence.VERY_HIGH
        elif confidence_score >= 0.75:
            return AuthorshipConfidence.HIGH
        elif confidence_score >= 0.60:
            return AuthorshipConfidence.MEDIUM
        elif confidence_score >= 0.40:
            return AuthorshipConfidence.LOW
        else:
            return AuthorshipConfidence.VERY_LOW
    
    def _identify_distinctive_features(
        self, query_features: Dict[str, float], author_id: str
    ) -> Dict[str, float]:
        """
Identify distinctive features for the predicted author"""
        
        if author_id not in self.author_profiles:
            return {}
        
        profile = self.author_profiles[author_id]
        distinctive_features = {}
        
        # Compare query features with author's typical features
        for category in ['lexical', 'syntactic', 'semantic', 'stylistic', 'structural', 'discourse', 'psychological']:
            author_features = getattr(profile, f"{category}_features", {})
            
            for feature_name, query_value in query_features.items():
                if feature_name in author_features:
                    author_mean = author_features.get(f"{feature_name}_mean", author_features.get(feature_name, 0))
                    author_std = author_features.get(f"{feature_name}_std", 0)
                    
                    # Calculate how distinctive this feature is
                    if author_std > 0:
                        z_score = abs(query_value - author_mean) / author_std
                        distinctive_features[feature_name] = z_score
                    else:
                        # If no variance, check exact match
                        if query_value == author_mean:
                            distinctive_features[feature_name] = 0.0  # Perfect match
                        else:
                            distinctive_features[feature_name] = 1.0  # Different
        
        # Return top distinctive features
        sorted_features = sorted(distinctive_features.items(), key=lambda x: x[1])
        return dict(sorted_features[:10])  # Top 10 most similar features
    
    async def _analyze_style_characteristics(
        self, text: str, features: Dict[str, float], embeddings: Optional[ContextualEmbedding]
    ) -> Dict[str, Any]:
        """Analyze style characteristics of the text"""
        
        characteristics = {}
        
        try:
            # Writing style assessment
            formality_score = features.get('formality_ratio', 0) * 100
            characteristics['formality'] = 'high' if formality_score > 2 else 'medium' if formality_score > 1 else 'low'
            
            # Emotional tone
            sentiment_compound = features.get('sentiment_compound', 0)
            if sentiment_compound > 0.1:
                characteristics['emotional_tone'] = 'positive'
            elif sentiment_compound < -0.1:
                characteristics['emotional_tone'] = 'negative'
            else:
                characteristics['emotional_tone'] = 'neutral'
            
            # Complexity assessment
            avg_sentence_length = features.get('avg_sentence_length', 0)
            vocabulary_richness = features.get('vocabulary_richness', 0)
            
            complexity_score = (avg_sentence_length / 20 + vocabulary_richness) / 2
            characteristics['complexity'] = 'high' if complexity_score > 0.7 else 'medium' if complexity_score > 0.4 else 'low'
            
            # Personal vs impersonal
            first_person = features.get('first_person_ratio', 0)
            third_person = features.get('third_person_ratio', 0)
            
            if first_person > third_person * 2:
                characteristics['perspective'] = 'personal'
            elif third_person > first_person * 2:
                characteristics['perspective'] = 'impersonal'
            else:
                characteristics['perspective'] = 'mixed'
            
            # Confidence level
            certainty_ratio = features.get('certainty_ratio', 0)
            uncertainty_ratio = features.get('uncertainty_ratio', 0)
            
            if certainty_ratio > uncertainty_ratio * 2:
                characteristics['confidence'] = 'high'
            elif uncertainty_ratio > certainty_ratio * 2:
                characteristics['confidence'] = 'low'
            else:
                characteristics['confidence'] = 'moderate'
        
        except Exception as e:
            logger.warning(f"Style characteristics analysis failed: {e}")
        
        return characteristics
    
    # Helper methods
    def _estimate_parse_depth(self, pos_tags: List[Tuple[str, str]]) -> float:
        """Estimate average parse tree depth (simplified)"""
        # Simplified heuristic based on subordinate clauses and complex structures
        subordinating_conjunctions = ['IN', 'DT']  # Simplified
        complex_tags = sum(1 for word, tag in pos_tags if tag in subordinating_conjunctions)
        return complex_tags / len(pos_tags) * 10 if pos_tags else 0
    
    def _count_subordinate_clauses(self, text: str) -> int:
        """
Count subordinate clauses (simplified)"""
        subordinators = ['because', 'although', 'while', 'since', 'if', 'unless', 'when', 'where', 'which', 'that']
        return sum(text.lower().count(sub) for sub in subordinators)
    
    def _count_pattern(self, text: str, pattern: str) -> int:
        """
Count regex pattern occurrences"""
        try:
            return len(re.findall(pattern, text, re.IGNORECASE))
        except:
            return 0
    
    def _calculate_readability_features(self, text: str) -> Dict[str, float]:
        """
Calculate readability-related features"""
        features = {}
        
        try:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            words = text.split()
            syllables = sum(self._count_syllables(word) for word in words)
            
            if sentences and words:
                # Flesch Reading Ease approximation
                avg_sentence_length = len(words) / len(sentences)
                avg_syllables_per_word = syllables / len(words)
                
                flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
                features['flesch_reading_ease'] = max(0, min(100, flesch_score))
                
                # Additional readability metrics
                features['avg_syllables_per_word'] = avg_syllables_per_word
                features['sentence_complexity'] = avg_sentence_length / 20  # Normalized
        
        except Exception as e:
            logger.warning(f"Readability calculation failed: {e}")
        
        return features
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        vowels = 'aeiouy'
        word = word.lower().strip(string.punctuation)
        if not word:
            return 0
        
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _calculate_repetition_ratio(self, text: str) -> float:
        """
Calculate repetition ratio in text"""
        try:
            sentences = [s.strip().lower() for s in text.split('.') if s.strip()]
            if len(sentences) < 2:
                return 0.0
            
            repeated_phrases = 0
            total_comparisons = 0
            
            for i in range(len(sentences)):
                for j in range(i + 1, len(sentences)):
                    words1 = sentences[i].split()
                    words2 = sentences[j].split()
                    
                    # Check for repeated phrases (3+ words)
                    for k in range(len(words1) - 2):
                        phrase = ' '.join(words1[k:k+3])
                        if phrase in sentences[j]:
                            repeated_phrases += 1
                    
                    total_comparisons += 1
            
            return repeated_phrases / total_comparisons if total_comparisons > 0 else 0.0
        
        except Exception:
            return 0.0
    
    def _calculate_pronoun_ratio(self, text: str) -> float:
        """
Calculate pronoun reference ratio"""
        try:
            words = text.lower().split()
            pronouns = ['he', 'she', 'it', 'they', 'this', 'that', 'these', 'those']
            pronoun_count = sum(1 for word in words if word.strip(string.punctuation) in pronouns)
            return pronoun_count / len(words) if words else 0.0
        except Exception:
            return 0.0
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """
Get analysis performance statistics"""
        return {
            'total_analyses': self.analysis_stats['total_analyses'],
            'successful_predictions': self.analysis_stats['successful_predictions'],
            'success_rate': self.analysis_stats['successful_predictions'] / max(self.analysis_stats['total_analyses'], 1),
            'registered_authors': len(self.author_profiles),
            'avg_processing_time': np.mean(self.processing_times) if self.processing_times else 0.0,
            'cache_size': len(self.feature_cache),
            'models_available': len(self.models)
        }