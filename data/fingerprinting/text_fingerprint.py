"""Text Fingerprinter Implementation
=================================

Professional text fingerprinting system for content protection and plagiarism detection.
Implements advanced NLP and semantic analysis algorithms.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""
import asyncio
import hashlib
import re
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import math

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.chunk import ne_chunk
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available, using basic text processing")

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available, using traditional methods")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available")


class TextFingerprintType(Enum):
    """Types of text fingerprints"""    LEXICAL_HASH = "lexical_hash"
    SEMANTIC_EMBEDDING = "semantic_embedding"
    SYNTACTIC_PATTERN = "syntactic_pattern"
    STYLOMETRIC_FEATURES = "stylometric_features"
    NGRAM_SIGNATURE = "ngram_signature"
    TOPIC_VECTOR = "topic_vector"
    STRUCTURE_HASH = "structure_hash"


@dataclass
class TextFingerprint:
    """Text fingerprint data structure"""    text_id: str
    fingerprint_type: TextFingerprintType
    fingerprint_data: Union[str, np.ndarray, List[float], Dict[str, Any]]
    text_length: int
    language: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TextMatchResult:
    """Text similarity match result"""    query_text_id: str
    matched_text_id: str
    similarity_score: float
    fingerprint_type: TextFingerprintType
    confidence_metrics: Dict[str, float]
    match_details: Dict[str, Any]
    semantic_similarity: float
    structural_similarity: float
    lexical_similarity: float
    created_at: datetime = field(default_factory=datetime.utcnow)


class TextFingerprinter:
    """    Professional text fingerprinting system for content protection.
    
    Features:
    - Multiple fingerprinting algorithms
    - Semantic embedding using transformers
    - Syntactic pattern analysis
    - Stylometric feature extraction
    - N-gram signature generation
    - Topic modeling and analysis
    - Multi-language support
    - Plagiarism detection capabilities
    - Paraphrase detection
    - Author identification features
    """    
    def __init__(self, 
                 max_workers: int = 4,
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 cache_embeddings: bool = True):
        """        Initialize text fingerprinter.
        
        Args:
            max_workers: Maximum worker threads
            model_name: Transformer model name for embeddings
            cache_embeddings: Cache computed embeddings
        """        self.max_workers = max_workers
        self.model_name = model_name
        self.cache_embeddings = cache_embeddings
        self.logger = logging.getLogger(__name__)
        
        # Thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        
        # Embedding cache
        self.embedding_cache: Dict[str, np.ndarray] = {}
        self.cache_max_size = 1000
        
        # Performance metrics
        self.processing_count = 0
        self.total_processing_time = 0.0
        
        # Initialize NLP models
        self.tokenizer = None
        self.model = None
        self.tfidf_vectorizer = None
        self.nlp = None
        
        # NLTK components
        self.stemmer = None
        self.lemmatizer = None
        self.stop_words = set()
        
        self._initialize_nlp_models()
    
    def _initialize_nlp_models(self):
        """Initialize NLP models and components"""        try:
            # Initialize transformers model
            if TRANSFORMERS_AVAILABLE:
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                    self.model = AutoModel.from_pretrained(self.model_name)
                    self.model.eval()
                    
                    # Move to GPU if available
                    if torch.cuda.is_available():
                        self.model = self.model.cuda()
                    
                    self.logger.info(f"Loaded transformer model: {self.model_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to load transformer model: {str(e)}")
            
            # Initialize TF-IDF vectorizer
            if SKLEARN_AVAILABLE:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=10000,
                    ngram_range=(1, 3),
                    stop_words='english'
                )
            
            # Initialize spaCy
            if SPACY_AVAILABLE:
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                    self.logger.info("Loaded spaCy model")
                except Exception as e:
                    self.logger.warning(f"Failed to load spaCy model: {str(e)}")
            
            # Initialize NLTK components
            if NLTK_AVAILABLE:
                try:
                    # Download required NLTK data
                    nltk.download('punkt', quiet=True)
                    nltk.download('stopwords', quiet=True)
                    nltk.download('wordnet', quiet=True)
                    nltk.download('averaged_perceptron_tagger', quiet=True)
                    nltk.download('maxent_ne_chunker', quiet=True)
                    nltk.download('words', quiet=True)
                    
                    self.stemmer = PorterStemmer()
                    self.lemmatizer = WordNetLemmatizer()
                    self.stop_words = set(stopwords.words('english'))
                    
                    self.logger.info("Initialized NLTK components")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize NLTK: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Error initializing NLP models: {str(e)}")
    
    async def extract_fingerprint(self, 
                                text: str,
                                text_id: str,
                                fingerprint_types: List[TextFingerprintType] = None,
                                language: str = "en") -> List[TextFingerprint]:
        """        Extract text fingerprints using multiple algorithms.
        
        Args:
            text: Input text
            text_id: Unique identifier for text
            fingerprint_types: Types of fingerprints to extract
            language: Text language
            
        Returns:
            List of text fingerprints
        """        try:
            start_time = datetime.utcnow()
            
            if fingerprint_types is None:
                fingerprint_types = [
                    TextFingerprintType.LEXICAL_HASH,
                    TextFingerprintType.NGRAM_SIGNATURE,
                    TextFingerprintType.STYLOMETRIC_FEATURES
                ]
                
                # Add semantic embedding if available
                if self.model:
                    fingerprint_types.append(TextFingerprintType.SEMANTIC_EMBEDDING)
            
            # Preprocess text
            preprocessed_text = await self._preprocess_text(text)
            
            # Extract fingerprints
            fingerprints = []
            for fingerprint_type in fingerprint_types:
                try:
                    fingerprint = await self._extract_single_fingerprint(
                        text, preprocessed_text, text_id, fingerprint_type, language
                    )
                    fingerprints.append(fingerprint)
                except Exception as e:
                    self.logger.error(f"Error extracting {fingerprint_type.value}: {str(e)}")
                    continue
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.processing_count += 1
            self.total_processing_time += processing_time
            
            self.logger.info(f"Extracted {len(fingerprints)} fingerprints for {text_id} in {processing_time:.2f}s")
            return fingerprints
            
        except Exception as e:
            self.logger.error(f"Error extracting text fingerprint for {text_id}: {str(e)}")
            return []
    
    async def compare_fingerprints(self, 
                                 fingerprint1: TextFingerprint,
                                 fingerprint2: TextFingerprint) -> TextMatchResult:
        """        Compare two text fingerprints for similarity.
        
        Args:
            fingerprint1: First text fingerprint
            fingerprint2: Second text fingerprint
            
        Returns:
            Text match result with similarity metrics
        """        try:
            if fingerprint1.fingerprint_type != fingerprint2.fingerprint_type:
                raise ValueError("Cannot compare different fingerprint types")
            
            fingerprint_type = fingerprint1.fingerprint_type
            
            if fingerprint_type == TextFingerprintType.LEXICAL_HASH:
                similarity_score = await self._compare_lexical_hashes(
                    fingerprint1.fingerprint_data, fingerprint2.fingerprint_data
                )
            elif fingerprint_type == TextFingerprintType.SEMANTIC_EMBEDDING:
                similarity_score = await self._compare_semantic_embeddings(
                    fingerprint1.fingerprint_data, fingerprint2.fingerprint_data
                )
            elif fingerprint_type == TextFingerprintType.NGRAM_SIGNATURE:
                similarity_score = await self._compare_ngram_signatures(
                    fingerprint1.fingerprint_data, fingerprint2.fingerprint_data
                )
            elif fingerprint_type == TextFingerprintType.STYLOMETRIC_FEATURES:
                similarity_score = await self._compare_stylometric_features(
                    fingerprint1.fingerprint_data, fingerprint2.fingerprint_data
                )
            elif fingerprint_type == TextFingerprintType.SYNTACTIC_PATTERN:
                similarity_score = await self._compare_syntactic_patterns(
                    fingerprint1.fingerprint_data, fingerprint2.fingerprint_data
                )
            else:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            # Calculate detailed similarity metrics
            semantic_similarity = similarity_score if fingerprint_type == TextFingerprintType.SEMANTIC_EMBEDDING else 0.0
            structural_similarity = similarity_score if fingerprint_type == TextFingerprintType.SYNTACTIC_PATTERN else 0.0
            lexical_similarity = similarity_score if fingerprint_type == TextFingerprintType.LEXICAL_HASH else 0.0
            
            # Calculate confidence metrics
            confidence_metrics = self._calculate_confidence_metrics(
                similarity_score, fingerprint1, fingerprint2
            )
            
            # Generate match details
            match_details = self._generate_match_details(
                fingerprint1, fingerprint2, similarity_score
            )
            
            result = TextMatchResult(
                query_text_id=fingerprint1.text_id,
                matched_text_id=fingerprint2.text_id,
                similarity_score=similarity_score,
                fingerprint_type=fingerprint_type,
                confidence_metrics=confidence_metrics,
                match_details=match_details,
                semantic_similarity=semantic_similarity,
                structural_similarity=structural_similarity,
                lexical_similarity=lexical_similarity
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error comparing fingerprints: {str(e)}")
            # Return empty result
            return TextMatchResult(
                query_text_id=fingerprint1.text_id,
                matched_text_id=fingerprint2.text_id,
                similarity_score=0.0,
                fingerprint_type=fingerprint1.fingerprint_type,
                confidence_metrics={},
                match_details={},
                semantic_similarity=0.0,
                structural_similarity=0.0,
                lexical_similarity=0.0
            )
    
    async def find_similar_texts(self, 
                               query_fingerprint: TextFingerprint,
                               candidate_fingerprints: List[TextFingerprint],
                               similarity_threshold: float = 0.8) -> List[TextMatchResult]:
        """        Find similar texts from a list of candidates.
        
        Args:
            query_fingerprint: Query text fingerprint
            candidate_fingerprints: List of candidate fingerprints
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            List of matching text results sorted by similarity
        """        try:
            # Filter candidates by fingerprint type
            compatible_candidates = [
                fp for fp in candidate_fingerprints 
                if fp.fingerprint_type == query_fingerprint.fingerprint_type
            ]
            
            # Compare with each candidate
            comparison_tasks = []
            for candidate in compatible_candidates:
                task = asyncio.create_task(
                    self.compare_fingerprints(query_fingerprint, candidate)
                )
                comparison_tasks.append(task)
            
            # Wait for all comparisons
            results = await asyncio.gather(*comparison_tasks)
            
            # Filter by threshold and sort by similarity
            filtered_results = [
                result for result in results 
                if result.similarity_score >= similarity_threshold
            ]
            
            filtered_results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            self.logger.info(f"Found {len(filtered_results)} similar texts above threshold {similarity_threshold}")
            return filtered_results
            
        except Exception as e:
            self.logger.error(f"Error finding similar texts: {str(e)}")
            return []
    
    async def detect_plagiarism(self, 
                              query_text: str,
                              reference_texts: List[Tuple[str, str]],
                              threshold: float = 0.7) -> List[Dict[str, Any]]:
        """        Detect potential plagiarism in query text.
        
        Args:
            query_text: Text to check for plagiarism
            reference_texts: List of tuples (text_id, text_content)
            threshold: Plagiarism detection threshold
            
        Returns:
            List of potential plagiarism matches
        """        try:
            # Extract fingerprints for query text
            query_id = f"query_{hashlib.md5(query_text.encode()).hexdigest()[:8]}"
            query_fingerprints = await self.extract_fingerprint(
                query_text, query_id, 
                [TextFingerprintType.SEMANTIC_EMBEDDING, TextFingerprintType.NGRAM_SIGNATURE]
            )
            
            plagiarism_matches = []
            
            for fingerprint_type in [TextFingerprintType.SEMANTIC_EMBEDDING, TextFingerprintType.NGRAM_SIGNATURE]:
                query_fp = next((fp for fp in query_fingerprints if fp.fingerprint_type == fingerprint_type), None)
                if not query_fp:
                    continue
                
                # Extract fingerprints for reference texts
                reference_fingerprints = []
                for ref_id, ref_text in reference_texts:
                    ref_fps = await self.extract_fingerprint(ref_text, ref_id, [fingerprint_type])
                    if ref_fps:
                        reference_fingerprints.extend(ref_fps)
                
                # Find similarities
                similar_texts = await self.find_similar_texts(
                    query_fp, reference_fingerprints, threshold
                )
                
                # Convert to plagiarism match format
                for match in similar_texts:
                    plagiarism_match = {
                        'reference_id': match.matched_text_id,
                        'similarity_score': match.similarity_score,
                        'fingerprint_type': fingerprint_type.value,
                        'confidence': match.confidence_metrics.get('overall_confidence', 0.0),
                        'match_details': match.match_details
                    }
                    plagiarism_matches.append(plagiarism_match)
            
            # Remove duplicates and sort by similarity
            seen_refs = set()
            unique_matches = []
            for match in sorted(plagiarism_matches, key=lambda x: x['similarity_score'], reverse=True):
                if match['reference_id'] not in seen_refs:
                    unique_matches.append(match)
                    seen_refs.add(match['reference_id'])
            
            return unique_matches
            
        except Exception as e:
            self.logger.error(f"Error detecting plagiarism: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _preprocess_text(self, text: str) -> str:
        """Preprocess text for fingerprinting"""        try:
            # Basic cleaning
            text = text.strip()
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            
            # Remove excessive punctuation
            text = re.sub(r'[^\w\s\.\,\!\?\;\:]', ' ', text)
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error preprocessing text: {str(e)}")
            return text
    
    async def _extract_single_fingerprint(self, 
                                        original_text: str,
                                        preprocessed_text: str,
                                        text_id: str,
                                        fingerprint_type: TextFingerprintType,
                                        language: str) -> TextFingerprint:
        """Extract single type of fingerprint"""        try:
            if fingerprint_type == TextFingerprintType.LEXICAL_HASH:
                fingerprint_data = await self._extract_lexical_hash(preprocessed_text)
            elif fingerprint_type == TextFingerprintType.SEMANTIC_EMBEDDING:
                fingerprint_data = await self._extract_semantic_embedding(preprocessed_text)
            elif fingerprint_type == TextFingerprintType.NGRAM_SIGNATURE:
                fingerprint_data = await self._extract_ngram_signature(preprocessed_text)
            elif fingerprint_type == TextFingerprintType.STYLOMETRIC_FEATURES:
                fingerprint_data = await self._extract_stylometric_features(original_text)
            elif fingerprint_type == TextFingerprintType.SYNTACTIC_PATTERN:
                fingerprint_data = await self._extract_syntactic_pattern(preprocessed_text)
            elif fingerprint_type == TextFingerprintType.TOPIC_VECTOR:
                fingerprint_data = await self._extract_topic_vector(preprocessed_text)
            elif fingerprint_type == TextFingerprintType.STRUCTURE_HASH:
                fingerprint_data = await self._extract_structure_hash(original_text)
            else:
                raise ValueError(f"Unsupported fingerprint type: {fingerprint_type}")
            
            return TextFingerprint(
                text_id=text_id,
                fingerprint_type=fingerprint_type,
                fingerprint_data=fingerprint_data,
                text_length=len(original_text),
                language=language
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting {fingerprint_type.value}: {str(e)}")
            raise
    
    async def _extract_lexical_hash(self, text: str) -> str:
        """Extract lexical hash based on word patterns"""        try:
            if NLTK_AVAILABLE:
                # Tokenize and normalize
                tokens = word_tokenize(text.lower())
                tokens = [token for token in tokens if token.isalpha() and token not in self.stop_words]
                
                # Stem words for normalization
                stemmed_tokens = [self.stemmer.stem(token) for token in tokens]
                
                # Create sorted word frequency signature
                word_freq = Counter(stemmed_tokens)
                top_words = word_freq.most_common(50)  # Top 50 words
                
                # Create hash from word patterns
                word_pattern = ''.join([f"{word}:{count}" for word, count in top_words])
                lexical_hash = hashlib.sha256(word_pattern.encode()).hexdigest()
            else:
                # Fallback to simple word-based hash
                words = re.findall(r'\b\w+\b', text.lower())
                words = [word for word in words if len(word) > 3]
                word_pattern = ''.join(sorted(set(words)))
                lexical_hash = hashlib.sha256(word_pattern.encode()).hexdigest()
            
            return lexical_hash
            
        except Exception as e:
            self.logger.error(f"Error extracting lexical hash: {str(e)}")
            return ""
    
    async def _extract_semantic_embedding(self, text: str) -> np.ndarray:
        """Extract semantic embedding using transformers"""        try:
            if not self.model or not self.tokenizer:
                raise ValueError("Transformer model not available")
            
            # Check cache first
            cache_key = hashlib.md5(text.encode()).hexdigest()
            if self.cache_embeddings and cache_key in self.embedding_cache:
                return self.embedding_cache[cache_key]
            
            # Tokenize and encode
            inputs = self.tokenizer(text, return_tensors="pt", max_length=512, truncation=True, padding=True)
            
            # Move to GPU if available
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Extract embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling of last hidden states
                embeddings = outputs.last_hidden_state.mean(dim=1)
                embeddings = embeddings.cpu().numpy().flatten()
            
            # Normalize embeddings
            embeddings = embeddings / np.linalg.norm(embeddings)
            
            # Cache if enabled
            if self.cache_embeddings:
                if len(self.embedding_cache) >= self.cache_max_size:
                    # Remove oldest entry
                    oldest_key = next(iter(self.embedding_cache))
                    del self.embedding_cache[oldest_key]
                self.embedding_cache[cache_key] = embeddings
            
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Error extracting semantic embedding: {str(e)}")
            return np.array([])
    
    async def _extract_ngram_signature(self, text: str) -> Dict[str, float]:
        """Extract n-gram signature"""        try:
            # Generate various n-grams
            ngram_counts = {}
            
            # Character n-grams (for style detection)
            for n in range(2, 6):  # 2-5 character grams
                char_grams = [text[i:i+n] for i in range(len(text)-n+1)]
                char_freq = Counter(char_grams)
                top_char_grams = dict(char_freq.most_common(20))
                ngram_counts[f"char_{n}gram"] = top_char_grams
            
            # Word n-grams
            if NLTK_AVAILABLE:
                tokens = word_tokenize(text.lower())
                tokens = [token for token in tokens if token.isalpha()]
                
                for n in range(1, 4):  # 1-3 word grams
                    word_grams = [' '.join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
                    word_freq = Counter(word_grams)
                    top_word_grams = dict(word_freq.most_common(30))
                    ngram_counts[f"word_{n}gram"] = top_word_grams
            else:
                # Simple word splitting
                words = text.lower().split()
                words = [word.strip(string.punctuation) for word in words if word.strip(string.punctuation)]
                
                word_freq = Counter(words)
                top_words = dict(word_freq.most_common(50))
                ngram_counts["word_1gram"] = top_words
            
            return ngram_counts
            
        except Exception as e:
            self.logger.error(f"Error extracting n-gram signature: {str(e)}")
            return {}
    
    async def _extract_stylometric_features(self, text: str) -> Dict[str, float]:
        """Extract stylometric features for authorship analysis"""        try:
            features = {}
            
            # Basic text statistics
            features['text_length'] = len(text)
            features['word_count'] = len(text.split())
            features['sentence_count'] = len(re.split(r'[.!?]+', text))
            features['paragraph_count'] = len(text.split('\n\n'))
            
            # Character-level features
            features['avg_word_length'] = np.mean([len(word) for word in text.split()])
            features['char_diversity'] = len(set(text.lower())) / len(text) if len(text) > 0 else 0
            features['digit_ratio'] = sum(c.isdigit() for c in text) / len(text) if len(text) > 0 else 0
            features['upper_ratio'] = sum(c.isupper() for c in text) / len(text) if len(text) > 0 else 0
            features['punctuation_ratio'] = sum(c in string.punctuation for c in text) / len(text) if len(text) > 0 else 0
            
            # Sentence-level features
            sentences = re.split(r'[.!?]+', text)
            if sentences:
                features['avg_sentence_length'] = np.mean([len(sent.split()) for sent in sentences if sent.strip()])
                features['sentence_length_variance'] = np.var([len(sent.split()) for sent in sentences if sent.strip()])
            
            # Punctuation patterns
            features['exclamation_ratio'] = text.count('!') / len(text) if len(text) > 0 else 0
            features['question_ratio'] = text.count('?') / len(text) if len(text) > 0 else 0
            features['comma_ratio'] = text.count(',') / len(text) if len(text) > 0 else 0
            features['semicolon_ratio'] = text.count(';') / len(text) if len(text) > 0 else 0
            
            # Advanced features with NLTK
            if NLTK_AVAILABLE:
                try:
                    tokens = word_tokenize(text.lower())
                    
                    # Lexical diversity
                    features['lexical_diversity'] = len(set(tokens)) / len(tokens) if len(tokens) > 0 else 0
                    
                    # Function word ratio
                    function_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
                    function_word_count = sum(1 for token in tokens if token in function_words)
                    features['function_word_ratio'] = function_word_count / len(tokens) if len(tokens) > 0 else 0
                    
                    # POS tag distribution
                    pos_tags = pos_tag(tokens)
                    pos_counts = Counter([tag for word, tag in pos_tags])
                    total_tags = len(pos_tags)
                    
                    for pos, count in pos_counts.most_common(10):
                        features[f'pos_{pos.lower()}_ratio'] = count / total_tags if total_tags > 0 else 0
                        
                except Exception as e:
                    self.logger.warning(f"Error in advanced stylometric features: {str(e)}")
            
            return features
            
        except Exception as e:
            self.logger.error(f"Error extracting stylometric features: {str(e)}")
            return {}
    
    async def _extract_syntactic_pattern(self, text: str) -> Dict[str, Any]:
        """Extract syntactic patterns"""        try:
            patterns = {}
            
            if NLTK_AVAILABLE:
                try:
                    tokens = word_tokenize(text)
                    pos_tags = pos_tag(tokens)
                    
                    # POS sequence patterns
                    pos_sequence = [tag for word, tag in pos_tags]
                    
                    # Extract common POS patterns
                    pattern_lengths = [2, 3, 4]
                    for length in pattern_lengths:
                        pos_patterns = [' '.join(pos_sequence[i:i+length]) 
                                      for i in range(len(pos_sequence)-length+1)]
                        pattern_freq = Counter(pos_patterns)
                        top_patterns = dict(pattern_freq.most_common(20))
                        patterns[f'pos_pattern_{length}'] = top_patterns
                    
                    # Dependency patterns (simplified)
                    if self.nlp:
                        doc = self.nlp(text)
                        dep_patterns = [f"{token.dep_}:{token.pos_}" for token in doc]
                        dep_freq = Counter(dep_patterns)
                        patterns['dependency_patterns'] = dict(dep_freq.most_common(30))
                        
                except Exception as e:
                    self.logger.warning(f"Error in syntactic pattern extraction: {str(e)}")
            
            # Simple pattern matching
            patterns['sentence_patterns'] = {
                'questions': len(re.findall(r'\?', text)),
                'exclamations': len(re.findall(r'!', text)),
                'complex_sentences': len(re.findall(r',.*,', text)),
                'passive_voice': len(re.findall(r'\b(?:was|were|been|being)\s+\w+ed\b', text, re.IGNORECASE))
            }
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error extracting syntactic patterns: {str(e)}")
            return {}
    
    async def _extract_topic_vector(self, text: str) -> np.ndarray:
        """Extract topic vector using TF-IDF"""        try:
            if not SKLEARN_AVAILABLE or not self.tfidf_vectorizer:
                return np.array([])
            
            # Fit and transform text (for single document, this is simplified)
            # In practice, you'd have a pre-trained TF-IDF model
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
            topic_vector = tfidf_matrix.toarray().flatten()
            
            # Normalize
            if np.linalg.norm(topic_vector) > 0:
                topic_vector = topic_vector / np.linalg.norm(topic_vector)
            
            return topic_vector
            
        except Exception as e:
            self.logger.error(f"Error extracting topic vector: {str(e)}")
            return np.array([])
    
    async def _extract_structure_hash(self, text: str) -> str:
        """Extract structural hash based on document structure"""        try:
            # Document structure features
            paragraphs = text.split('\n\n')
            sentences = re.split(r'[.!?]+', text)
            
            structure_features = {
                'paragraph_count': len(paragraphs),
                'sentence_count': len(sentences),
                'avg_paragraph_length': np.mean([len(p.split()) for p in paragraphs if p.strip()]),
                'avg_sentence_length': np.mean([len(s.split()) for s in sentences if s.strip()]),
                'structure_pattern': f"{len(paragraphs)}:{len(sentences)}"
            }
            
            # Create hash from structure
            structure_string = ':'.join([f"{k}={v}" for k, v in sorted(structure_features.items())])
            structure_hash = hashlib.sha256(structure_string.encode()).hexdigest()
            
            return structure_hash
            
        except Exception as e:
            self.logger.error(f"Error extracting structure hash: {str(e)}")
            return ""
    
    # Comparison methods
    
    async def _compare_lexical_hashes(self, hash1: str, hash2: str) -> float:
        """Compare lexical hashes"""        try:
            return 1.0 if hash1 == hash2 else 0.0
        except Exception as e:
            self.logger.error(f"Error comparing lexical hashes: {str(e)}")
            return 0.0
    
    async def _compare_semantic_embeddings(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compare semantic embeddings"""        try:
            if len(emb1) == 0 or len(emb2) == 0:
                return 0.0
            
            # Cosine similarity
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            self.logger.error(f"Error comparing semantic embeddings: {str(e)}")
            return 0.0
    
    async def _compare_ngram_signatures(self, sig1: Dict[str, Any], sig2: Dict[str, Any]) -> float:
        """Compare n-gram signatures"""        try:
            if not sig1 or not sig2:
                return 0.0
            
            similarities = []
            
            # Compare each n-gram type
            common_ngram_types = set(sig1.keys()) & set(sig2.keys())
            
            for ngram_type in common_ngram_types:
                ngrams1 = sig1[ngram_type]
                ngrams2 = sig2[ngram_type]
                
                if not ngrams1 or not ngrams2:
                    continue
                
                # Calculate Jaccard similarity
                set1 = set(ngrams1.keys())
                set2 = set(ngrams2.keys())
                
                intersection = len(set1 & set2)
                union = len(set1 | set2)
                
                if union > 0:
                    jaccard_sim = intersection / union
                    similarities.append(jaccard_sim)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            self.logger.error(f"Error comparing n-gram signatures: {str(e)}")
            return 0.0
    
    async def _compare_stylometric_features(self, features1: Dict[str, float], features2: Dict[str, float]) -> float:
        """Compare stylometric features"""        try:
            if not features1 or not features2:
                return 0.0
            
            # Get common features
            common_features = set(features1.keys()) & set(features2.keys())
            
            if not common_features:
                return 0.0
            
            # Calculate feature-wise similarities
            similarities = []
            
            for feature in common_features:
                val1 = features1[feature]
                val2 = features2[feature]
                
                # Normalize and calculate similarity
                if val1 == 0 and val2 == 0:
                    similarities.append(1.0)
                elif val1 == 0 or val2 == 0:
                    similarities.append(0.0)
                else:
                    # Use relative difference
                    diff = abs(val1 - val2) / max(val1, val2)
                    similarity = 1.0 - min(diff, 1.0)
                    similarities.append(similarity)
            
            return np.mean(similarities)
            
        except Exception as e:
            self.logger.error(f"Error comparing stylometric features: {str(e)}")
            return 0.0
    
    async def _compare_syntactic_patterns(self, patterns1: Dict[str, Any], patterns2: Dict[str, Any]) -> float:
        """Compare syntactic patterns"""        try:
            if not patterns1 or not patterns2:
                return 0.0
            
            similarities = []
            
            # Compare pattern types
            common_pattern_types = set(patterns1.keys()) & set(patterns2.keys())
            
            for pattern_type in common_pattern_types:
                p1 = patterns1[pattern_type]
                p2 = patterns2[pattern_type]
                
                if isinstance(p1, dict) and isinstance(p2, dict):
                    # Compare pattern dictionaries
                    set1 = set(p1.keys())
                    set2 = set(p2.keys())
                    
                    intersection = len(set1 & set2)
                    union = len(set1 | set2)
                    
                    if union > 0:
                        jaccard_sim = intersection / union
                        similarities.append(jaccard_sim)
                elif isinstance(p1, (int, float)) and isinstance(p2, (int, float)):
                    # Compare numeric values
                    if p1 == 0 and p2 == 0:
                        similarities.append(1.0)
                    elif p1 == 0 or p2 == 0:
                        similarities.append(0.0)
                    else:
                        diff = abs(p1 - p2) / max(p1, p2)
                        similarity = 1.0 - min(diff, 1.0)
                        similarities.append(similarity)
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception as e:
            self.logger.error(f"Error comparing syntactic patterns: {str(e)}")
            return 0.0
    
    def _calculate_confidence_metrics(self, 
                                    similarity_score: float,
                                    fingerprint1: TextFingerprint,
                                    fingerprint2: TextFingerprint) -> Dict[str, float]:
        """Calculate confidence metrics for the match"""        try:
            # Text length compatibility
            len1 = fingerprint1.text_length
            len2 = fingerprint2.text_length
            
            length_ratio = min(len1, len2) / max(len1, len2) if max(len1, len2) > 0 else 0
            
            # Language compatibility
            lang_compatibility = 1.0
            if fingerprint1.language and fingerprint2.language:
                lang_compatibility = 1.0 if fingerprint1.language == fingerprint2.language else 0.5
            
            # Fingerprint quality assessment
            fp_quality = self._assess_fingerprint_quality(fingerprint1, fingerprint2)
            
            confidence_metrics = {
                'similarity_score': similarity_score,
                'length_compatibility': length_ratio,
                'language_compatibility': lang_compatibility,
                'fingerprint_quality': fp_quality,
                'overall_confidence': (similarity_score + length_ratio + lang_compatibility + fp_quality) / 4.0
            }
            
            return confidence_metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence metrics: {str(e)}")
            return {}
    
    def _assess_fingerprint_quality(self, 
                                  fingerprint1: TextFingerprint,
                                  fingerprint2: TextFingerprint) -> float:
        """Assess quality of fingerprints for comparison"""        try:
            quality_score = 1.0
            
            # Check text length (very short texts are lower quality)
            min_length = min(fingerprint1.text_length, fingerprint2.text_length)
            if min_length < 100:  # Less than 100 characters
                quality_score *= 0.7
            elif min_length < 50:  # Less than 50 characters
                quality_score *= 0.4
            
            # Check fingerprint data validity
            fp_type = fingerprint1.fingerprint_type
            
            if fp_type == TextFingerprintType.SEMANTIC_EMBEDDING:
                if (isinstance(fingerprint1.fingerprint_data, np.ndarray) and len(fingerprint1.fingerprint_data) == 0) or \
                   (isinstance(fingerprint2.fingerprint_data, np.ndarray) and len(fingerprint2.fingerprint_data) == 0):
                    quality_score *= 0.5
            elif fp_type in [TextFingerprintType.NGRAM_SIGNATURE, TextFingerprintType.STYLOMETRIC_FEATURES]:
                if not fingerprint1.fingerprint_data or not fingerprint2.fingerprint_data:
                    quality_score *= 0.5
            
            return quality_score
            
        except Exception as e:
            self.logger.error(f"Error assessing fingerprint quality: {str(e)}")
            return 0.5
    
    def _generate_match_details(self, 
                              fingerprint1: TextFingerprint,
                              fingerprint2: TextFingerprint,
                              similarity_score: float) -> Dict[str, Any]:
        """Generate detailed match information"""        try:
            details = {
                'fingerprint_type': fingerprint1.fingerprint_type.value,
                'similarity_score': similarity_score,
                'text1_length': fingerprint1.text_length,
                'text2_length': fingerprint2.text_length,
                'length_ratio': min(fingerprint1.text_length, fingerprint2.text_length) / max(fingerprint1.text_length, fingerprint2.text_length) if max(fingerprint1.text_length, fingerprint2.text_length) > 0 else 0
            }
            
            # Add type-specific details
            if fingerprint1.fingerprint_type == TextFingerprintType.NGRAM_SIGNATURE:
                if isinstance(fingerprint1.fingerprint_data, dict) and isinstance(fingerprint2.fingerprint_data, dict):
                    common_ngrams = set(fingerprint1.fingerprint_data.keys()) & set(fingerprint2.fingerprint_data.keys())
                    details['common_ngram_types'] = len(common_ngrams)
            
            elif fingerprint1.fingerprint_type == TextFingerprintType.STYLOMETRIC_FEATURES:
                if isinstance(fingerprint1.fingerprint_data, dict) and isinstance(fingerprint2.fingerprint_data, dict):
                    common_features = set(fingerprint1.fingerprint_data.keys()) & set(fingerprint2.fingerprint_data.keys())
                    details['common_features'] = len(common_features)
            
            return details
            
        except Exception as e:
            self.logger.error(f"Error generating match details: {str(e)}")
            return {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get fingerprinter statistics"""        avg_processing_time = (self.total_processing_time / self.processing_count 
                             if self.processing_count > 0 else 0.0)
        
        return {
            'processing_count': self.processing_count,
            'average_processing_time': avg_processing_time,
            'cached_embeddings': len(self.embedding_cache),
            'transformers_available': TRANSFORMERS_AVAILABLE,
            'nltk_available': NLTK_AVAILABLE,
            'sklearn_available': SKLEARN_AVAILABLE,
            'spacy_available': SPACY_AVAILABLE,
            'model_loaded': self.model is not None,
            'tfidf_vectorizer_loaded': self.tfidf_vectorizer is not None
        }
    
    async def close(self):
        """Cleanup resources"""        try:
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)
            
            # Clear cache
            self.embedding_cache.clear()
            
            self.logger.info("Text fingerprinter closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error closing text fingerprinter: {str(e)}")
