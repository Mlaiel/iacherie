"""Text Detection Engine Module
===========================

Advanced text fingerprinting and detection engine for textual content surveillance.
Implements sophisticated NLP and text analysis algorithms for plagiarism detection.

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All Rights Reserved.

WARNING: This code and concept are protected intellectual property.
Any unauthorized use, copying, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""
import asyncio
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
import chromadb
from scipy.spatial.distance import cosine, euclidean
from dataclasses import dataclass
import hashlib
import json
import re
from collections import Counter
import string
from difflib import SequenceMatcher
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


@dataclass
class TextFingerprint:
    """Text fingerprint data structure."""    fingerprint_id: str
    user_id: str
    title: str
    content_length: int
    language: str
    content_type: str  # article, lyrics, caption, etc.
    linguistic_features: Dict[str, Any]
    semantic_features: Dict[str, Any]
    stylistic_features: Dict[str, Any]
    hash_signatures: Dict[str, str]
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class TextMatch:
    """Text match result structure."""    original_fingerprint_id: str
    detected_url: str
    similarity_score: float
    confidence_level: float
    matching_segments: List[Tuple[int, int, str]]  # Start, end, matching text
    similarity_breakdown: Dict[str, float]
    plagiarism_type: str  # exact, paraphrase, translation, etc.
    platform: str
    detected_at: datetime
    match_details: Dict[str, Any]


class TextFeatureExtractor:
    """Advanced text feature extraction for fingerprinting."""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_length = config.get("max_length", 10000)
        self.min_length = config.get("min_length", 10)
        
        # Initialize NLP models
        self.sentence_transformer = None
        self.spacy_model = None
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            stop_words='english',
            lowercase=True,
            sublinear_tf=True
        )
        
        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('wordnet', quiet=True)
        except:
            pass
    
    async def initialize(self) -> bool:
        """Initialize NLP models."""        try:
            # Load sentence transformer
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Load spaCy model
            try:
                self.spacy_model = spacy.load("en_core_web_sm")
            except:
                logger.warning("spaCy English model not found, some features will be limited")
            
            logger.info("TextFeatureExtractor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize TextFeatureExtractor: {e}")
            return False
    
    async def extract_features(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive text features from text content."""        try:
            # Preprocess text
            cleaned_text = self._preprocess_text(text)
            
            if len(cleaned_text) < self.min_length:
                raise ValueError(f"Text too short: {len(cleaned_text)} characters")
            
            features = {
                "original_length": len(text),
                "cleaned_length": len(cleaned_text),
                "language": self._detect_language(cleaned_text)  # Language detection implementation
            }
            
            # Basic text statistics
            basic_features = await self._extract_basic_features(cleaned_text)
            features.update(basic_features)
            
            # Linguistic features
            linguistic_features = await self._extract_linguistic_features(cleaned_text)
            features.update(linguistic_features)
            
            # Semantic features
            semantic_features = await self._extract_semantic_features(cleaned_text)
            features.update(semantic_features)
            
            # Stylistic features
            stylistic_features = await self._extract_stylistic_features(cleaned_text)
            features.update(stylistic_features)
            
            # N-gram features
            ngram_features = await self._extract_ngram_features(cleaned_text)
            features.update(ngram_features)
            
            # Hash signatures
            hash_features = await self._extract_hash_features(cleaned_text)
            features.update(hash_features)
            
            logger.info(f"Extracted text features: {len(features)} feature sets")
            return features
            
        except Exception as e:
            logger.error(f"Text feature extraction failed: {e}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for feature extraction."""        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\']+', '', text)
        
        # Limit length
        if len(text) > self.max_length:
            text = text[:self.max_length]
        
        return text.strip()
    
    async def _extract_basic_features(self, text: str) -> Dict[str, Any]:
        """Extract basic text statistics."""        features = {}
        
        # Character-level features
        features["char_count"] = len(text)
        features["char_count_no_spaces"] = len(text.replace(' ', ''))
        features["uppercase_count"] = sum(1 for c in text if c.isupper())
        features["lowercase_count"] = sum(1 for c in text if c.islower())
        features["digit_count"] = sum(1 for c in text if c.isdigit())
        features["punctuation_count"] = sum(1 for c in text if c in string.punctuation)
        
        # Word-level features
        words = text.split()
        features["word_count"] = len(words)
        features["unique_word_count"] = len(set(word.lower() for word in words))
        features["avg_word_length"] = np.mean([len(word) for word in words]) if words else 0
        features["word_length_std"] = np.std([len(word) for word in words]) if words else 0
        
        # Sentence-level features
        sentences = nltk.sent_tokenize(text)
        features["sentence_count"] = len(sentences)
        features["avg_sentence_length"] = np.mean([len(sent.split()) for sent in sentences]) if sentences else 0
        features["sentence_length_std"] = np.std([len(sent.split()) for sent in sentences]) if sentences else 0
        
        # Readability metrics (simplified)
        if features["sentence_count"] > 0 and features["word_count"] > 0:
            # Flesch Reading Ease approximation
            avg_sentence_length = features["word_count"] / features["sentence_count"]
            avg_syllables_per_word = 1.5  # Approximation
            features["flesch_reading_ease"] = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        return features
    
    async def _extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        """Extract linguistic features using NLP."""        features = {}
        
        try:
            # POS tagging with NLTK
            words = nltk.word_tokenize(text.lower())
            pos_tags = nltk.pos_tag(words)
            
            pos_counts = Counter(tag for word, tag in pos_tags)
            total_pos = len(pos_tags)
            
            # Most common POS tags
            common_pos = ['NN', 'VB', 'JJ', 'RB', 'IN', 'DT', 'CC', 'PRP']
            for pos in common_pos:
                features[f"pos_{pos.lower()}_ratio"] = pos_counts.get(pos, 0) / total_pos if total_pos > 0 else 0
            
            # Named entities (if spaCy is available)
            if self.spacy_model:
                doc = self.spacy_model(text)
                entity_types = Counter(ent.label_ for ent in doc.ents)
                features["named_entity_count"] = len(doc.ents)
                features["named_entity_density"] = len(doc.ents) / len(words) if words else 0
                
                # Most common entity types
                for ent_type in ['PERSON', 'ORG', 'GPE', 'DATE', 'MONEY']:
                    features[f"entity_{ent_type.lower()}_count"] = entity_types.get(ent_type, 0)
            
            # Function words ratio
            function_words = set(['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'])
            function_word_count = sum(1 for word in words if word in function_words)
            features["function_word_ratio"] = function_word_count / len(words) if words else 0
            
        except Exception as e:
            logger.error(f"Linguistic feature extraction failed: {e}")
        
        return features
    
    async def _extract_semantic_features(self, text: str) -> Dict[str, Any]:
        """Extract semantic features using embeddings."""        features = {}
        
        try:
            if self.sentence_transformer:
                # Generate sentence embeddings
                sentences = nltk.sent_tokenize(text)
                if sentences:
                    sentence_embeddings = self.sentence_transformer.encode(sentences)
                    
                    # Aggregate sentence embeddings
                    features["sentence_embedding_mean"] = np.mean(sentence_embeddings, axis=0)
                    features["sentence_embedding_std"] = np.std(sentence_embeddings, axis=0)
                    
                    # Document-level embedding
                    doc_embedding = self.sentence_transformer.encode([text])[0]
                    features["document_embedding"] = doc_embedding
                    
                    # Semantic diversity (variance in sentence embeddings)
                    if len(sentence_embeddings) > 1:
                        pairwise_similarities = []
                        for i in range(len(sentence_embeddings)):
                            for j in range(i+1, len(sentence_embeddings)):
                                sim = cosine_similarity([sentence_embeddings[i]], [sentence_embeddings[j]])[0][0]
                                pairwise_similarities.append(sim)
                        features["semantic_diversity"] = 1 - np.mean(pairwise_similarities) if pairwise_similarities else 0
            
        except Exception as e:
            logger.error(f"Semantic feature extraction failed: {e}")
        
        return features
    
    async def _extract_stylistic_features(self, text: str) -> Dict[str, Any]:
        """Extract stylistic features."""        features = {}
        
        try:
            # Vocabulary richness
            words = text.lower().split()
            unique_words = set(words)
            features["vocabulary_richness"] = len(unique_words) / len(words) if words else 0
            
            # Yule's K (vocabulary diversity)
            if words:
                word_freq = Counter(words)
                freq_spectrum = Counter(word_freq.values())
                N = len(words)
                yules_k = 10000 * (sum(freq * (freq_class ** 2) for freq_class, freq in freq_spectrum.items()) - N) / (N ** 2)
                features["yules_k"] = yules_k
            
            # Punctuation patterns
            punctuation_chars = ''.join([c for c in text if c in string.punctuation])
            features["punctuation_density"] = len(punctuation_chars) / len(text) if text else 0
            
            # Question and exclamation marks
            features["question_mark_count"] = text.count('?')
            features["exclamation_mark_count"] = text.count('!')
            features["quotation_mark_count"] = text.count('"') + text.count("'")
            
            # Capitalization patterns
            words = text.split()
            if words:
                capitalized_words = sum(1 for word in words if word[0].isupper())
                features["capitalization_ratio"] = capitalized_words / len(words)
                
                all_caps_words = sum(1 for word in words if word.isupper() and len(word) > 1)
                features["all_caps_ratio"] = all_caps_words / len(words)
            
            # Sentence structure variety
            sentences = nltk.sent_tokenize(text)
            if sentences:
                sentence_lengths = [len(sent.split()) for sent in sentences]
                features["sentence_length_variety"] = np.std(sentence_lengths) / np.mean(sentence_lengths) if sentence_lengths else 0
            
        except Exception as e:
            logger.error(f"Stylistic feature extraction failed: {e}")
        
        return features
    
    async def _extract_ngram_features(self, text: str) -> Dict[str, Any]:
        """Extract n-gram based features."""        features = {}
        
        try:
            # Character n-grams
            for n in [2, 3, 4]:
                char_ngrams = [text[i:i+n] for i in range(len(text)-n+1)]
                char_ngram_freq = Counter(char_ngrams)
                features[f"char_{n}gram_unique_count"] = len(char_ngram_freq)
                features[f"char_{n}gram_top10"] = [gram for gram, _ in char_ngram_freq.most_common(10)]
            
            # Word n-grams
            words = text.lower().split()
            for n in [2, 3]:
                word_ngrams = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
                word_ngram_freq = Counter(word_ngrams)
                features[f"word_{n}gram_unique_count"] = len(word_ngram_freq)
                features[f"word_{n}gram_top10"] = [gram for gram, _ in word_ngram_freq.most_common(10)]
            
        except Exception as e:
            logger.error(f"N-gram feature extraction failed: {e}")
        
        return features
    
    async def _extract_hash_features(self, text: str) -> Dict[str, Any]:
        """Extract hash-based signatures."""        features = {}
        
        try:
            # MD5 hash
            features["md5_hash"] = hashlib.md5(text.encode()).hexdigest()
            
            # SHA256 hash
            features["sha256_hash"] = hashlib.sha256(text.encode()).hexdigest()
            
            # Normalized text hash (lowercase, no punctuation)
            normalized_text = re.sub(r'[^\w\s]', '', text.lower())
            features["normalized_hash"] = hashlib.sha256(normalized_text.encode()).hexdigest()
            
            # Semantic hash (based on words only)
            words = set(text.lower().split())
            words_string = ' '.join(sorted(words))
            features["semantic_hash"] = hashlib.sha256(words_string.encode()).hexdigest()
            
            # Fuzzy hash (simplified)
            # Remove stop words and sort remaining words
            from nltk.corpus import stopwords
            stop_words = set(stopwords.words('english'))
            content_words = [word for word in text.lower().split() if word not in stop_words]
            fuzzy_string = ' '.join(sorted(content_words))
            features["fuzzy_hash"] = hashlib.sha256(fuzzy_string.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Hash feature extraction failed: {e}")
        
        return features


class TextSimilarityCalculator:
    """Advanced text similarity calculation engine."""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feature_weights = config.get("feature_weights", {
            "semantic": 0.4,
            "lexical": 0.25,
            "stylistic": 0.2,
            "ngram": 0.15
        })
        
    async def calculate_similarity(
        self, 
        features1: Dict[str, Any], 
        features2: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate comprehensive similarity between two text feature sets."""        try:
            similarities = {}
            weighted_sum = 0.0
            total_weight = 0.0
            
            # Semantic similarity
            semantic_sim = await self._calculate_semantic_similarity(features1, features2)
            if semantic_sim is not None:
                similarities["semantic"] = semantic_sim
                weighted_sum += semantic_sim * self.feature_weights.get("semantic", 0.4)
                total_weight += self.feature_weights.get("semantic", 0.4)
            
            # Lexical similarity
            lexical_sim = await self._calculate_lexical_similarity(features1, features2)
            if lexical_sim is not None:
                similarities["lexical"] = lexical_sim
                weighted_sum += lexical_sim * self.feature_weights.get("lexical", 0.25)
                total_weight += self.feature_weights.get("lexical", 0.25)
            
            # Stylistic similarity
            stylistic_sim = await self._calculate_stylistic_similarity(features1, features2)
            if stylistic_sim is not None:
                similarities["stylistic"] = stylistic_sim
                weighted_sum += stylistic_sim * self.feature_weights.get("stylistic", 0.2)
                total_weight += self.feature_weights.get("stylistic", 0.2)
            
            # N-gram similarity
            ngram_sim = await self._calculate_ngram_similarity(features1, features2)
            if ngram_sim is not None:
                similarities["ngram"] = ngram_sim
                weighted_sum += ngram_sim * self.feature_weights.get("ngram", 0.15)
                total_weight += self.feature_weights.get("ngram", 0.15)
            
            # Calculate overall similarity
            overall_similarity = weighted_sum / total_weight if total_weight > 0 else 0.0
            
            logger.debug(f"Text similarity calculated: {overall_similarity:.4f}")
            return overall_similarity, similarities
            
        except Exception as e:
            logger.error(f"Text similarity calculation failed: {e}")
            return 0.0, {}
    
    async def _calculate_semantic_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Optional[float]:
        """Calculate semantic similarity using embeddings."""        try:
            semantic_similarities = []
            
            # Document embedding similarity
            if "document_embedding" in features1 and "document_embedding" in features2:
                doc_sim = 1 - cosine(features1["document_embedding"], features2["document_embedding"])
                semantic_similarities.append(max(0, doc_sim))
            
            # Sentence embedding similarity
            if "sentence_embedding_mean" in features1 and "sentence_embedding_mean" in features2:
                sent_sim = 1 - cosine(features1["sentence_embedding_mean"], features2["sentence_embedding_mean"])
                semantic_similarities.append(max(0, sent_sim))
            
            return np.mean(semantic_similarities) if semantic_similarities else None
            
        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {e}")
            return None
    
    async def _calculate_lexical_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Optional[float]:
        """Calculate lexical similarity using statistical features."""        try:
            lexical_similarities = []
            
            # Basic statistics similarity
            stat_features = ["word_count", "sentence_count", "avg_word_length", "avg_sentence_length", "vocabulary_richness"]
            
            for feature in stat_features:
                if feature in features1 and feature in features2:
                    val1 = features1[feature]
                    val2 = features2[feature]
                    if val1 + val2 > 0:
                        similarity = 1 - abs(val1 - val2) / max(val1, val2)
                        lexical_similarities.append(max(0, similarity))
            
            # POS tag similarity
            pos_features = [f"pos_{pos}_ratio" for pos in ["nn", "vb", "jj", "rb", "in", "dt"]]
            for feature in pos_features:
                if feature in features1 and feature in features2:
                    pos_sim = 1 - abs(features1[feature] - features2[feature])
                    lexical_similarities.append(max(0, pos_sim))
            
            return np.mean(lexical_similarities) if lexical_similarities else None
            
        except Exception as e:
            logger.error(f"Lexical similarity calculation failed: {e}")
            return None
    
    async def _calculate_stylistic_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Optional[float]:
        """Calculate stylistic similarity."""        try:
            stylistic_similarities = []
            
            # Stylistic features
            style_features = ["punctuation_density", "capitalization_ratio", "function_word_ratio", "yules_k"]
            
            for feature in style_features:
                if feature in features1 and feature in features2:
                    val1 = features1[feature]
                    val2 = features2[feature]
                    if val1 + val2 > 0:
                        similarity = 1 - abs(val1 - val2) / max(abs(val1), abs(val2), 1)
                        stylistic_similarities.append(max(0, similarity))
            
            return np.mean(stylistic_similarities) if stylistic_similarities else None
            
        except Exception as e:
            logger.error(f"Stylistic similarity calculation failed: {e}")
            return None
    
    async def _calculate_ngram_similarity(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> Optional[float]:
        """Calculate n-gram similarity."""        try:
            ngram_similarities = []
            
            # Character n-gram overlap
            for n in [2, 3, 4]:
                top_key = f"char_{n}gram_top10"
                if top_key in features1 and top_key in features2:
                    set1 = set(features1[top_key])
                    set2 = set(features2[top_key])
                    if set1 or set2:
                        jaccard_sim = len(set1.intersection(set2)) / len(set1.union(set2))
                        ngram_similarities.append(jaccard_sim)
            
            # Word n-gram overlap
            for n in [2, 3]:
                top_key = f"word_{n}gram_top10"
                if top_key in features1 and top_key in features2:
                    set1 = set(features1[top_key])
                    set2 = set(features2[top_key])
                    if set1 or set2:
                        jaccard_sim = len(set1.intersection(set2)) / len(set1.union(set2))
                        ngram_similarities.append(jaccard_sim)
            
            return np.mean(ngram_similarities) if ngram_similarities else None
            
        except Exception as e:
            logger.error(f"N-gram similarity calculation failed: {e}")
            return None


class TextDetectionEngine:
    """    Advanced text detection engine for content surveillance.
    
    Implements sophisticated text fingerprinting, matching, and detection
    algorithms for protecting textual content across platforms.
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feature_extractor = TextFeatureExtractor(config.get("feature_extraction", {}))
        self.similarity_calculator = TextSimilarityCalculator(config.get("similarity", {}))
        
        # ChromaDB vector store for fast similarity search
        self.chroma_client = None
        self.fingerprint_collection = None
        
        # Detection thresholds
        self.similarity_threshold = config.get("similarity_threshold", 0.75)
        self.confidence_threshold = config.get("confidence_threshold", 0.7)
        
        # Performance metrics
        self.detection_stats = {
            "total_fingerprints": 0,
            "total_detections": 0,
            "false_positives": 0,
            "processing_time_avg": 0.0
        }
        
    async def initialize(self) -> bool:
        """Initialize the text detection engine."""        try:
            # Initialize feature extractor
            await self.feature_extractor.initialize()
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.Client()
            
            # Get or create fingerprint collection
            try:
                self.fingerprint_collection = self.chroma_client.get_collection(
                    name="text_fingerprints"
                )
            except:
                self.fingerprint_collection = self.chroma_client.create_collection(
                    name="text_fingerprints",
                    metadata={"description": "Text fingerprint collection for content protection"}
                )
            
            logger.info("TextDetectionEngine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize TextDetectionEngine: {e}")
            return False
    
    async def create_fingerprint(
        self, 
        text: str, 
        metadata: Dict[str, Any]
    ) -> TextFingerprint:
        """Create text fingerprint from text content."""        try:
            start_time = datetime.utcnow()
            
            # Extract text features
            features = await self.feature_extractor.extract_features(text)
            
            # Separate feature categories
            linguistic_features = {k: v for k, v in features.items() if k.startswith(('pos_', 'entity_', 'function_word'))}
            semantic_features = {k: v for k, v in features.items() if 'embedding' in k or k == 'semantic_diversity'}
            stylistic_features = {k: v for k, v in features.items() if k in ['vocabulary_richness', 'yules_k', 'punctuation_density', 'capitalization_ratio']}
            
            # Extract hash signatures
            hash_signatures = {
                hash_type: features.get(hash_type, "")
                for hash_type in ["md5_hash", "sha256_hash", "normalized_hash", "semantic_hash", "fuzzy_hash"]
            }
            
            # Create fingerprint object
            fingerprint = TextFingerprint(
                fingerprint_id=hashlib.sha256(f"{metadata.get('user_id', '')}{features.get('sha256_hash', '')}{start_time.isoformat()}".encode()).hexdigest(),
                user_id=metadata.get("user_id", ""),
                title=metadata.get("title", ""),
                content_length=features.get("cleaned_length", 0),
                language=features.get("language", "en"),
                content_type=metadata.get("content_type", "text"),
                linguistic_features=linguistic_features,
                semantic_features=semantic_features,
                stylistic_features=stylistic_features,
                hash_signatures=hash_signatures,
                created_at=start_time,
                metadata=metadata
            )
            
            # Store in vector database
            await self._store_fingerprint(fingerprint)
            
            self.detection_stats["total_fingerprints"] += 1
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Text fingerprint created in {processing_time:.2f}s: {fingerprint.fingerprint_id}")
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Text fingerprint creation failed: {e}")
            raise
    
    async def _store_fingerprint(self, fingerprint: TextFingerprint) -> None:
        """Store fingerprint in vector database."""        try:
            # Create embedding vector from semantic features
            embedding_features = []
            
            if "document_embedding" in fingerprint.semantic_features:
                embedding_features = fingerprint.semantic_features["document_embedding"].tolist()
            elif "sentence_embedding_mean" in fingerprint.semantic_features:
                embedding_features = fingerprint.semantic_features["sentence_embedding_mean"].tolist()
            
            # If no embeddings available, create a simple feature vector
            if not embedding_features:
                # Use basic statistical features as embedding
                basic_features = [
                    fingerprint.content_length / 10000,  # Normalized length
                    fingerprint.linguistic_features.get("pos_nn_ratio", 0),
                    fingerprint.linguistic_features.get("pos_vb_ratio", 0),
                    fingerprint.stylistic_features.get("vocabulary_richness", 0),
                    fingerprint.stylistic_features.get("punctuation_density", 0)
                ]
                # Pad to 384 dimensions
                embedding_features = basic_features + [0.0] * (384 - len(basic_features))
            
            # Ensure fixed size (384 dimensions)
            target_size = 384
            if len(embedding_features) < target_size:
                embedding_features.extend([0.0] * (target_size - len(embedding_features)))
            else:
                embedding_features = embedding_features[:target_size]
            
            # Store in ChromaDB
            self.fingerprint_collection.add(
                embeddings=[embedding_features],
                documents=[json.dumps({
                    "title": fingerprint.title,
                    "content_length": fingerprint.content_length,
                    "language": fingerprint.language,
                    "content_type": fingerprint.content_type
                })],
                metadatas=[{
                    "fingerprint_id": fingerprint.fingerprint_id,
                    "user_id": fingerprint.user_id,
                    "created_at": fingerprint.created_at.isoformat(),
                    "md5_hash": fingerprint.hash_signatures.get("md5_hash", ""),
                    "semantic_hash": fingerprint.hash_signatures.get("semantic_hash", "")
                }],
                ids=[fingerprint.fingerprint_id]
            )
            
            logger.debug(f"Text fingerprint stored in vector database: {fingerprint.fingerprint_id}")
            
        except Exception as e:
            logger.error(f"Failed to store text fingerprint: {e}")
            raise
    
    async def detect_matches(
        self, 
        text: str, 
        detection_metadata: Dict[str, Any]
    ) -> List[TextMatch]:
        """Detect text matches against stored fingerprints."""        try:
            start_time = datetime.utcnow()
            
            # Extract features from input text
            input_features = await self.feature_extractor.extract_features(text)
            
            # Create embedding for similarity search
            embedding_features = []
            
            if "document_embedding" in input_features:
                embedding_features = input_features["document_embedding"].tolist()
            elif "sentence_embedding_mean" in input_features:
                embedding_features = input_features["sentence_embedding_mean"].tolist()
            
            # If no embeddings available, create a simple feature vector
            if not embedding_features:
                basic_features = [
                    input_features.get("cleaned_length", 0) / 10000,
                    input_features.get("pos_nn_ratio", 0),
                    input_features.get("pos_vb_ratio", 0),
                    input_features.get("vocabulary_richness", 0),
                    input_features.get("punctuation_density", 0)
                ]
                embedding_features = basic_features + [0.0] * (384 - len(basic_features))
            
            # Ensure fixed size
            target_size = 384
            if len(embedding_features) < target_size:
                embedding_features.extend([0.0] * (target_size - len(embedding_features)))
            else:
                embedding_features = embedding_features[:target_size]
            
            # Search for similar fingerprints
            search_results = self.fingerprint_collection.query(
                query_embeddings=[embedding_features],
                n_results=25,  # Get top 25 candidates
                include=["documents", "metadatas", "distances"]
            )
            
            matches = []
            
            # Process search results
            if search_results['ids'][0]:
                for i, fingerprint_id in enumerate(search_results['ids'][0]):
                    distance = search_results['distances'][0][i]
                    metadata = search_results['metadatas'][0][i]
                    
                    # Convert distance to similarity score
                    initial_similarity = max(0, 1 - distance)
                    
                    # Skip if initial similarity is too low
                    if initial_similarity < self.similarity_threshold * 0.7:
                        continue
                    
                    # Load full fingerprint for detailed comparison
                    stored_fingerprint = await self._load_fingerprint(fingerprint_id)
                    if not stored_fingerprint:
                        continue
                    
                    # Reconstruct stored features
                    stored_features = {}
                    stored_features.update(stored_fingerprint.linguistic_features)
                    stored_features.update(stored_fingerprint.semantic_features)
                    stored_features.update(stored_fingerprint.stylistic_features)
                    
                    # Calculate detailed similarity
                    detailed_similarity, feature_similarities = await self.similarity_calculator.calculate_similarity(
                        input_features, stored_features
                    )
                    
                    # Check if similarity meets threshold
                    if detailed_similarity >= self.similarity_threshold:
                        confidence = self._calculate_confidence(
                            detailed_similarity, 
                            feature_similarities,
                            input_features,
                            stored_features
                        )
                        
                        if confidence >= self.confidence_threshold:
                            # Determine plagiarism type
                            plagiarism_type = self._determine_plagiarism_type(
                                input_features, stored_features, feature_similarities
                            )
                            
                            # Find matching segments (simplified)
                            matching_segments = [(0, input_features.get("cleaned_length", 0), "Full text match")]
                            
                            match = TextMatch(
                                original_fingerprint_id=fingerprint_id,
                                detected_url=detection_metadata.get("url", ""),
                                similarity_score=detailed_similarity,
                                confidence_level=confidence,
                                matching_segments=matching_segments,
                                similarity_breakdown=feature_similarities,
                                plagiarism_type=plagiarism_type,
                                platform=detection_metadata.get("platform", ""),
                                detected_at=datetime.utcnow(),
                                match_details=feature_similarities
                            )
                            matches.append(match)
            
            self.detection_stats["total_detections"] += len(matches)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Text detection completed in {processing_time:.2f}s: {len(matches)} matches found")
            
            return matches
            
        except Exception as e:
            logger.error(f"Text detection failed: {e}")
            return []
    
    async def _load_fingerprint(self, fingerprint_id: str) -> Optional[TextFingerprint]:
        """Load full fingerprint data (placeholder - implement with your storage system)."""        # This would load the full fingerprint data from your database
        # For now, return None to indicate not found
        return None
    
    def _calculate_confidence(
        self, 
        similarity_score: float, 
        feature_similarities: Dict[str, float],
        input_features: Dict[str, Any],
        stored_features: Dict[str, Any]
    ) -> float:
        """Calculate confidence level for match."""        try:
            # Base confidence from overall similarity
            confidence = similarity_score
            
            # Boost confidence if multiple feature types match well
            high_similarity_features = sum(1 for sim in feature_similarities.values() if sim > 0.8)
            feature_boost = min(0.15, high_similarity_features * 0.05)
            confidence += feature_boost
            
            # Check length consistency
            input_length = input_features.get("cleaned_length", 0)
            stored_length = stored_features.get("cleaned_length", 0)
            if input_length > 0 and stored_length > 0:
                length_ratio = min(input_length / stored_length, stored_length / input_length)
                if length_ratio > 0.8:  # Within 20% difference
                    confidence += 0.05
            
            # Ensure confidence is between 0 and 1
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return similarity_score
    
    def _determine_plagiarism_type(
        self, 
        input_features: Dict[str, Any], 
        stored_features: Dict[str, Any],
        feature_similarities: Dict[str, float]
    ) -> str:
        """Determine the type of plagiarism based on feature similarities."""        try:
            semantic_sim = feature_similarities.get("semantic", 0)
            lexical_sim = feature_similarities.get("lexical", 0)
            stylistic_sim = feature_similarities.get("stylistic", 0)
            ngram_sim = feature_similarities.get("ngram", 0)
            
            # Exact match
            if ngram_sim > 0.9 and lexical_sim > 0.9:
                return "exact"
            
            # Near exact match
            elif ngram_sim > 0.8 and lexical_sim > 0.8:
                return "near_exact"
            
            # Paraphrase
            elif semantic_sim > 0.8 and lexical_sim < 0.6:
                return "paraphrase"
            
            # Stylistic similarity (same author potentially)
            elif stylistic_sim > 0.8 and semantic_sim > 0.6:
                return "stylistic_match"
            
            # Structural similarity
            elif lexical_sim > 0.7 and ngram_sim < 0.5:
                return "structural"
            
            # General similarity
            else:
                return "similar"
                
        except Exception as e:
            logger.error(f"Plagiarism type determination failed: {e}")
            return "unknown"
    
    async def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection engine statistics."""        return {
            "engine_type": "text",
            "status": "active",
            "statistics": self.detection_stats,
            "thresholds": {
                "similarity_threshold": self.similarity_threshold,
                "confidence_threshold": self.confidence_threshold
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _detect_language(self, text: str) -> str:
        """Detect the language of the input text."""        try:
            # Simple heuristic-based language detection
            text_lower = text.lower()
            
            # Common words in different languages
            language_patterns = {
                'en': ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with'],
                'fr': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
                'es': ['el', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no'],
                'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
                'it': ['il', 'di', 'che', 'e', 'la', 'per', 'una', 'in', 'con', 'da'],
                'ar': ['في', 'من', 'إلى', 'على', 'هذا', 'أن', 'كان', 'قد', 'لا', 'ما']
            }
            
            # Count matches for each language
            language_scores = {}
            words = text_lower.split()
            
            for lang, common_words in language_patterns.items():
                score = sum(1 for word in words if word in common_words)
                if len(words) > 0:
                    language_scores[lang] = score / len(words)
                else:
                    language_scores[lang] = 0.0
            
            # Return language with highest score, default to English
            if language_scores:
                detected_lang = max(language_scores, key=language_scores.get)
                # Only return if confidence is reasonable
                if language_scores[detected_lang] > 0.05:  # At least 5% match
                    return detected_lang
            
            # Check for Arabic script
            arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
            if arabic_chars > len(text) * 0.3:  # More than 30% Arabic characters
                return 'ar'
            
            # Default to English
            return 'en'
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return 'en'
    
    async def cleanup(self) -> None:
        """Cleanup resources."""        try:
            if self.chroma_client:
                # ChromaDB cleanup if needed
                pass
            logger.info("TextDetectionEngine cleanup completed")
        except Exception as e:
            logger.error(f"TextDetectionEngine cleanup failed: {e}")
