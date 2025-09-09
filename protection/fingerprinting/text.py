"""📝 Text Content Fingerprinting Service
======================================

Enterprise-grade text fingerprinting with advanced NLP techniques:
- BERT/RoBERTa neural embeddings
- TF-IDF vectorization
- N-gram analysis
- Semantic similarity matching
- Plagiarism detection
- Language detection

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
import unicodedata
from collections import Counter

try:
    import torch
    import torch.nn as nn
    import numpy as np
    from transformers import (
        AutoTokenizer, AutoModel, 
        BertTokenizer, BertModel,
        RobertaTokenizer, RobertaModel,
        pipeline
    )
    from sentence_transformers import SentenceTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.cluster import KMeans
    import faiss
    
    # NLP libraries
    NLP_AVAILABLE = True
    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize, sent_tokenize
        from nltk.stem import PorterStemmer, WordNetLemmatizer
        from nltk.util import ngrams
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
            
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet', quiet=True)
            
    except ImportError:
        NLP_AVAILABLE = False
        logging.warning("NLTK not available - using basic text processing")
    
    # Language detection
    LANG_DETECT_AVAILABLE = True
    try:
        from langdetect import detect, detect_langs
        import polyglot
        from polyglot.detect import Detector
    except ImportError:
        LANG_DETECT_AVAILABLE = False
        logging.warning("Language detection libraries not available")
    
    # Fuzzy matching for paraphrase detection
    FUZZY_AVAILABLE = True
    try:
        from fuzzywuzzy import fuzz, process
        import textdistance
    except ImportError:
        FUZZY_AVAILABLE = False
        logging.warning("Fuzzy matching libraries not available")
        
except ImportError as e:
    logging.error(f"Critical text processing dependencies missing: {e}")
    logging.error("Please install: pip install torch transformers sentence-transformers sklearn nltk")
    NLP_AVAILABLE = False
    LANG_DETECT_AVAILABLE = False
    FUZZY_AVAILABLE = False

from ..models import FingerprintResult, SimilarityMatch

logger = logging.getLogger(__name__)

@dataclass
class TextMetadata:
    """Comprehensive text metadata extraction."""
    char_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    language: Optional[str]
    readability_score: Optional[float]
    sentiment_score: Optional[float]
    named_entities: Optional[List[Dict[str, str]]]
    pos_tags: Optional[Dict[str, int]]
    lexical_diversity: Optional[float]
    avg_sentence_length: Optional[float]
    complexity_score: Optional[float]

class EnterpriseTextFingerprinter:
    """
    Enterprise-grade text fingerprinting with BERT semantic similarity and 644 language support.
    Includes paraphrase detection, style analysis, and anti-spinning protection.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.sentence_model = None
        self.bert_model = None
        self.bert_tokenizer = None
        self.tfidf_vectorizer = None
        self.faiss_index = None
        self.language_support = None
        
        # Initialize models
        self._initialize_models()
        self._initialize_faiss_index()
        
        # Initialize multilingual support if available
        try:
            self.language_support = Enhanced644LanguageSupport()
        except:
            self.language_support = None
    
    def _initialize_models(self):
        """Initialize BERT and sentence transformer models."""
        try:
            # Sentence transformer for semantic similarity
            self.sentence_model = SentenceTransformer(self.model_name)
            logger.info(f"Sentence transformer loaded: {self.model_name}")
            
            # BERT for detailed analysis
            self.bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
            self.bert_model = AutoModel.from_pretrained("bert-base-multilingual-cased")
            self.bert_model.eval()
            
            # TF-IDF for traditional analysis
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 3),
                stop_words='english'
            )
            
            logger.info("Text fingerprinting models initialized successfully")
            
        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            # Fallback to basic models
            self._initialize_fallback_models()
    
    def _initialize_fallback_models(self):
        """Initialize fallback models when main models fail."""
        try:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2)
            )
            logger.info("Fallback TF-IDF model initialized")
        except Exception as e:
            logger.error(f"Fallback model initialization failed: {e}")
    
    def _initialize_faiss_index(self):
        """Initialize FAISS index for text similarity search."""
        try:
            # Use 384 dimensions for all-MiniLM-L6-v2 or 768 for BERT
            dimension = 384 if "MiniLM" in self.model_name else 768
            self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            logger.info(f"FAISS text index initialized with {dimension} dimensions")
        except Exception as e:
            logger.error(f"FAISS text index initialization failed: {e}")
    
    def extract_comprehensive_fingerprint(self, text: str, text_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract comprehensive text fingerprint with semantic and structural analysis.
        
        Args:
            text: Input text content
            text_id: Optional identifier for the text
            
        Returns:
            Dictionary containing all fingerprint data and features
        """
        try:
            # Preprocessing
            cleaned_text = self._preprocess_text(text)
            
            # Semantic embeddings
            semantic_features = self._extract_semantic_features(cleaned_text)
            
            # Traditional NLP features
            nlp_features = self._extract_nlp_features(cleaned_text)
            
            # Structural analysis
            structural_features = self._analyze_text_structure(text, cleaned_text)
            
            # Language detection and analysis
            language_features = self._analyze_language(text)
            
            # Paraphrase detection features
            paraphrase_features = self._extract_paraphrase_features(cleaned_text)
            
            # Style analysis
            style_features = self._analyze_writing_style(cleaned_text)
            
            # Anti-spinning features
            spinning_features = self._detect_spinning_patterns(text, cleaned_text)
            
            # Metadata extraction
            metadata = self._extract_text_metadata(text)
            
            # Create combined fingerprint
            combined_fingerprint = self._create_combined_fingerprint(
                semantic_features, nlp_features, structural_features
            )
            
            fingerprint_data = {
                "text_id": text_id or hashlib.sha256(text.encode()).hexdigest()[:16],
                "semantic_features": semantic_features,
                "nlp_features": nlp_features,
                "structural_features": structural_features,
                "language_features": language_features,
                "paraphrase_features": paraphrase_features,
                "style_features": style_features,
                "spinning_features": spinning_features,
                "metadata": metadata,
                "combined_fingerprint": combined_fingerprint,
                "timestamp": datetime.utcnow().isoformat(),
                "original_text_hash": hashlib.sha256(text.encode()).hexdigest()
            }
            
            # Add to FAISS index for similarity search
            if self.faiss_index and semantic_features.get("sentence_embedding"):
                embedding = np.array(semantic_features["sentence_embedding"]).reshape(1, -1)
                self.faiss_index.add(embedding.astype(np.float32))
            
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Comprehensive text fingerprinting failed: {e}")
            return {"error": str(e)}
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis."""
        try:
            # Normalize unicode
            text = unicodedata.normalize('NFKD', text)
            
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove non-printable characters but keep basic punctuation
            text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\']+', '', text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Text preprocessing failed: {e}")
            return text
    
    def _extract_semantic_features(self, text: str) -> Dict[str, Any]:
        """Extract semantic features using BERT and sentence transformers."""
        try:
            features = {}
            
            # Sentence transformer embeddings
            if self.sentence_model:
                sentence_embedding = self.sentence_model.encode(text, convert_to_numpy=True)
                features["sentence_embedding"] = sentence_embedding.tolist()
                features["embedding_model"] = self.model_name
            
            # BERT embeddings for detailed analysis
            if self.bert_model and self.bert_tokenizer:
                inputs = self.bert_tokenizer(
                    text, 
                    return_tensors="pt", 
                    max_length=512, 
                    truncation=True, 
                    padding=True
                )
                
                with torch.no_grad():
                    outputs = self.bert_model(**inputs)
                    # Use CLS token embedding
                    cls_embedding = outputs.last_hidden_state[:, 0, :].numpy().flatten()
                    features["bert_cls_embedding"] = cls_embedding.tolist()
                    
                    # Aggregate sentence representation
                    sentence_rep = torch.mean(outputs.last_hidden_state, dim=1).numpy().flatten()
                    features["bert_sentence_embedding"] = sentence_rep.tolist()
            
            # Semantic density analysis
            if NLP_AVAILABLE:
                sentences = sent_tokenize(text)
                if len(sentences) > 1:
                    sentence_embeddings = []
                    for sentence in sentences:
                        if self.sentence_model:
                            emb = self.sentence_model.encode(sentence, convert_to_numpy=True)
                            sentence_embeddings.append(emb)
                    
                    if sentence_embeddings:
                        # Calculate semantic coherence
                        similarities = []
                        for i in range(len(sentence_embeddings) - 1):
                            sim = cosine_similarity([sentence_embeddings[i]], [sentence_embeddings[i+1]])[0][0]
                            similarities.append(sim)
                        
                        features["semantic_coherence"] = float(np.mean(similarities))
                        features["semantic_variance"] = float(np.var(similarities))
            
            return features
            
        except Exception as e:
            logger.error(f"Semantic feature extraction failed: {e}")
            return {}
    
    def _extract_nlp_features(self, text: str) -> Dict[str, Any]:
        """Extract traditional NLP features."""
        try:
            features = {}
            
            if not NLP_AVAILABLE:
                return features
            
            # Tokenization
            words = word_tokenize(text.lower())
            sentences = sent_tokenize(text)
            
            # Basic statistics
            features["word_count"] = len(words)
            features["sentence_count"] = len(sentences)
            features["avg_word_length"] = np.mean([len(word) for word in words])
            features["avg_sentence_length"] = np.mean([len(sent.split()) for sent in sentences])
            
            # Lexical diversity
            unique_words = set(words)
            features["lexical_diversity"] = len(unique_words) / len(words) if words else 0
            
            # N-gram analysis
            bigrams = list(ngrams(words, 2))
            trigrams = list(ngrams(words, 3))
            
            features["unique_bigrams"] = len(set(bigrams))
            features["unique_trigrams"] = len(set(trigrams))
            
            # Part-of-speech distribution (simplified)
            # This would require additional NLP libraries like spaCy
            features["pos_complexity"] = len(set(words)) / len(words) if words else 0
            
            # Function word ratio
            try:
                stop_words = set(stopwords.words('english'))
                function_words = [word for word in words if word in stop_words]
                features["function_word_ratio"] = len(function_words) / len(words) if words else 0
            except:
                features["function_word_ratio"] = 0.0
            
            # Vocabulary complexity
            word_freq = Counter(words)
            features["vocabulary_richness"] = len([word for word, count in word_freq.items() if count == 1])
            
            return features
            
        except Exception as e:
            logger.error(f"NLP feature extraction failed: {e}")
            return {}
    
    def _analyze_text_structure(self, original_text: str, cleaned_text: str) -> Dict[str, Any]:
        """Analyze text structure and formatting."""
        try:
            features = {}
            
            # Paragraph analysis
            paragraphs = original_text.split('\n\n')
            features["paragraph_count"] = len([p for p in paragraphs if p.strip()])
            features["avg_paragraph_length"] = np.mean([len(p.split()) for p in paragraphs if p.strip()])
            
            # Punctuation analysis
            punctuation_chars = '.,!?;:"()[]{}/-'
            punct_count = sum(text.count(char) for char in punctuation_chars)
            features["punctuation_density"] = punct_count / len(original_text) if original_text else 0
            
            # Capitalization patterns
            capitals = sum(1 for char in original_text if char.isupper())
            features["capitalization_ratio"] = capitals / len(original_text) if original_text else 0
            
            # Sentence structure variety
            if NLP_AVAILABLE:
                sentences = sent_tokenize(cleaned_text)
                sentence_lengths = [len(sent.split()) for sent in sentences]
                features["sentence_length_variance"] = float(np.var(sentence_lengths))
                features["min_sentence_length"] = min(sentence_lengths) if sentence_lengths else 0
                features["max_sentence_length"] = max(sentence_lengths) if sentence_lengths else 0
            
            # Special characters and formatting
            features["has_numbers"] = bool(re.search(r'\d', original_text))
            features["has_urls"] = bool(re.search(r'http[s]?://\S+', original_text))
            features["has_emails"] = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', original_text))
            
            return features
            
        except Exception as e:
            logger.error(f"Structural analysis failed: {e}")
            return {}
    
    def _analyze_language(self, text: str) -> Dict[str, Any]:
        """Analyze language and multilingual features."""
        try:
            features = {}
            
            # Language detection
            if LANG_DETECT_AVAILABLE:
                try:
                    detected_lang = detect(text)
                    features["detected_language"] = detected_lang
                    
                    # Multiple language probabilities
                    lang_probs = detect_langs(text)
                    features["language_probabilities"] = [
                        {"lang": str(lang).split(':')[0], "prob": float(str(lang).split(':')[1])}
                        for lang in lang_probs[:3]
                    ]
                except:
                    features["detected_language"] = "unknown"
                    features["language_probabilities"] = []
            
            # Character set analysis
            features["has_non_ascii"] = any(ord(char) > 127 for char in text)
            features["has_unicode"] = any(ord(char) > 255 for char in text)
            
            # Script analysis (basic)
            scripts = set()
            for char in text:
                if char.isalpha():
                    if ord(char) < 128:
                        scripts.add("latin")
                    elif 0x0370 <= ord(char) <= 0x03FF:
                        scripts.add("greek")
                    elif 0x0400 <= ord(char) <= 0x04FF:
                        scripts.add("cyrillic")
                    elif 0x4E00 <= ord(char) <= 0x9FFF:
                        scripts.add("cjk")
                    elif 0x0600 <= ord(char) <= 0x06FF:
                        scripts.add("arabic")
            
            features["detected_scripts"] = list(scripts)
            features["is_multilingual"] = len(scripts) > 1
            
            return features
            
        except Exception as e:
            logger.error(f"Language analysis failed: {e}")
            return {}
    
    def _extract_paraphrase_features(self, text: str) -> Dict[str, Any]:
        """Extract features for paraphrase detection."""
        try:
            features = {}
            
            if not NLP_AVAILABLE:
                return features
            
            # Sentence-level analysis for paraphrasing patterns
            sentences = sent_tokenize(text)
            
            # Synonym usage patterns
            words = word_tokenize(text.lower())
            word_freq = Counter(words)
            
            # Rare word usage (potential synonym substitution)
            rare_words = [word for word, count in word_freq.items() if count == 1 and len(word) > 6]
            features["rare_word_ratio"] = len(rare_words) / len(words) if words else 0
            
            # Sentence complexity variation
            sentence_complexities = []
            for sentence in sentences:
                sent_words = word_tokenize(sentence.lower())
                # Simple complexity measure
                complexity = len(sent_words) * len(set(sent_words)) / (len(sent_words) + 1)
                sentence_complexities.append(complexity)
            
            features["complexity_variance"] = float(np.var(sentence_complexities)) if sentence_complexities else 0
            
            # Syntactic patterns
            if FUZZY_AVAILABLE:
                # Check for potential paraphrasing patterns between sentences
                sentence_similarities = []
                for i in range(len(sentences) - 1):
                    similarity = fuzz.ratio(sentences[i], sentences[i + 1])
                    sentence_similarities.append(similarity)
                
                features["inter_sentence_similarity"] = float(np.mean(sentence_similarities)) if sentence_similarities else 0
            
            return features
            
        except Exception as e:
            logger.error(f"Paraphrase feature extraction failed: {e}")
            return {}
    
    def _analyze_writing_style(self, text: str) -> Dict[str, Any]:
        """Analyze writing style for author attribution."""
        try:
            features = {}
            
            if not NLP_AVAILABLE:
                return features
            
            words = word_tokenize(text.lower())
            sentences = sent_tokenize(text)
            
            # Stylometric features
            features["avg_word_length"] = np.mean([len(word) for word in words]) if words else 0
            features["word_length_variance"] = float(np.var([len(word) for word in words])) if words else 0
            
            # Sentence patterns
            sentence_starters = []
            for sentence in sentences:
                words_in_sent = word_tokenize(sentence.lower())
                if words_in_sent:
                    sentence_starters.append(words_in_sent[0])
            
            features["sentence_starter_diversity"] = len(set(sentence_starters)) / len(sentence_starters) if sentence_starters else 0
            
            # Punctuation style
            features["exclamation_ratio"] = text.count('!') / len(text) if text else 0
            features["question_ratio"] = text.count('?') / len(text) if text else 0
            features["comma_ratio"] = text.count(',') / len(text) if text else 0
            
            # Word choice patterns
            word_lengths = [len(word) for word in words]
            features["short_word_ratio"] = sum(1 for length in word_lengths if length <= 3) / len(words) if words else 0
            features["long_word_ratio"] = sum(1 for length in word_lengths if length >= 7) / len(words) if words else 0
            
            return features
            
        except Exception as e:
            logger.error(f"Style analysis failed: {e}")
            return {}
    
    def _detect_spinning_patterns(self, original_text: str, cleaned_text: str) -> Dict[str, Any]:
        """Detect content spinning and text manipulation patterns."""
        try:
            features = {}
            
            # Synonym spinning detection
            if FUZZY_AVAILABLE:
                words = word_tokenize(cleaned_text.lower())
                
                # Look for unnatural word choices (potential synonyms)
                unusual_patterns = 0
                for word in words:
                    # Check if word might be an unusual synonym
                    if len(word) > 6 and word.count('tion') == 0 and word.count('ing') == 0:
                        unusual_patterns += 1
                
                features["potential_synonym_ratio"] = unusual_patterns / len(words) if words else 0
            
            # Sentence reordering detection
            if NLP_AVAILABLE:
                sentences = sent_tokenize(cleaned_text)
                
                # Check for logical flow disruption
                if self.sentence_model and len(sentences) > 2:
                    sentence_embeddings = []
                    for sentence in sentences:
                        emb = self.sentence_model.encode(sentence, convert_to_numpy=True)
                        sentence_embeddings.append(emb)
                    
                    # Calculate coherence disruption
                    coherence_scores = []
                    for i in range(len(sentence_embeddings) - 1):
                        sim = cosine_similarity([sentence_embeddings[i]], [sentence_embeddings[i+1]])[0][0]
                        coherence_scores.append(sim)
                    
                    features["coherence_disruption"] = float(np.std(coherence_scores)) if coherence_scores else 0
            
            # Character-level manipulation detection
            features["excessive_spacing"] = len(re.findall(r'\s{3,}', original_text))
            features["mixed_case_words"] = len(re.findall(r'\b[a-z]+[A-Z]+[a-zA-Z]*\b', original_text))
            features["special_char_insertions"] = len(re.findall(r'[a-zA-Z][^\w\s][a-zA-Z]', original_text))
            
            # Overall spinning likelihood
            spinning_indicators = [
                features.get("potential_synonym_ratio", 0) > 0.1,
                features.get("coherence_disruption", 0) > 0.5,
                features.get("excessive_spacing", 0) > 0,
                features.get("mixed_case_words", 0) > 0
            ]
            
            features["spinning_likelihood"] = sum(spinning_indicators) / len(spinning_indicators)
            
            return features
            
        except Exception as e:
            logger.error(f"Spinning detection failed: {e}")
            return {}
    
    def _extract_text_metadata(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive text metadata."""
        try:
            metadata = {}
            
            # Basic counts
            metadata["character_count"] = len(text)
            metadata["character_count_no_spaces"] = len(text.replace(' ', ''))
            metadata["line_count"] = len(text.split('\n'))
            
            if NLP_AVAILABLE:
                words = word_tokenize(text.lower())
                sentences = sent_tokenize(text)
                
                metadata["word_count"] = len(words)
                metadata["sentence_count"] = len(sentences)
                metadata["unique_word_count"] = len(set(words))
            
            # Encoding and format
            metadata["encoding"] = "utf-8"  # Assumed
            metadata["has_non_printable"] = bool(re.search(r'[^\x20-\x7E\s]', text))
            
            # Content indicators
            metadata["has_code"] = bool(re.search(r'[{}();]', text))
            metadata["has_markup"] = bool(re.search(r'<[^>]+>', text))
            metadata["has_math"] = bool(re.search(r'[\+\-\*/=\^]', text))
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {}
    
    def _create_combined_fingerprint(self, semantic_features: Dict, 
                                   nlp_features: Dict, structural_features: Dict) -> str:
        """Create a combined fingerprint hash from all features."""
        try:
            # Combine key features into a string
            feature_components = []
            
            # Add semantic embedding summary
            if semantic_features.get("sentence_embedding"):
                embedding = semantic_features["sentence_embedding"]
                # Use statistical summary of embedding
                stats = [np.mean(embedding), np.std(embedding), np.median(embedding)]
                feature_components.extend([f"{stat:.6f}" for stat in stats])
            
            # Add NLP features
            nlp_keys = ["word_count", "lexical_diversity", "function_word_ratio"]
            for key in nlp_keys:
                if key in nlp_features:
                    feature_components.append(f"{nlp_features[key]:.6f}")
            
            # Add structural features
            struct_keys = ["paragraph_count", "punctuation_density", "capitalization_ratio"]
            for key in struct_keys:
                if key in structural_features:
                    feature_components.append(f"{structural_features[key]:.6f}")
            
            # Create hash
            combined_string = "_".join(feature_components)
            fingerprint = hashlib.sha256(combined_string.encode()).hexdigest()
            
            return fingerprint[:32]  # 32-character fingerprint
            
        except Exception as e:
            logger.error(f"Combined fingerprint creation failed: {e}")
            return "fingerprint_error"

class BERTEmbeddingExtractor:
    """
BERT-based neural embeddings for semantic text understanding."""
    
    def __init__(self, model_name: str = "bert-base-uncased"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize BERT model."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.eval()
        except Exception as e:
            logger.warning(f"BERT model initialization failed: {e}")
    
    def extract_embeddings(self, text: str) -> Dict[str, Any]:
        """
        Extract BERT embeddings from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing embeddings and metadata
        """
        if not self.model or not self.tokenizer:
            return {"error": "BERT model not initialized"}
            
        try:
            # Preprocess text
            text = self._preprocess_text(text)
            
            # Handle long texts by chunking
            chunks = self._chunk_text(text, max_length=512)
            
            chunk_embeddings = []
            for chunk in chunks:
                # Tokenize
                inputs = self.tokenizer(
                    chunk, 
                    return_tensors="pt", 
                    truncation=True, 
                    padding=True, 
                    max_length=512
                )
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    
                # Extract embeddings (use [CLS] token)
                cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze()
                chunk_embeddings.append(cls_embedding.numpy())
            
            # Combine chunk embeddings
            if chunk_embeddings:
                combined_embeddings = np.mean(chunk_embeddings, axis=0)
            else:
                combined_embeddings = np.zeros(768)  # Default BERT size
            
            # Generate embedding hash
            embedding_hash = self._compute_embedding_hash(combined_embeddings)
            
            # Extract semantic features
            semantic_features = self._extract_semantic_features(combined_embeddings)
            
            return {
                "embeddings": combined_embeddings.tolist(),
                "embedding_hash": embedding_hash,
                "embedding_size": len(combined_embeddings),
                "num_chunks": len(chunks),
                "semantic_features": semantic_features,
                "model_name": self.model_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"BERT embedding extraction failed: {e}")
            return {"error": str(e)}
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for BERT."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    def _chunk_text(self, text: str, max_length: int = 512) -> List[str]:
        """
Split text into chunks that fit BERT's maximum length."""
        # Tokenize to get accurate token count
        tokens = self.tokenizer.tokenize(text)
        
        if len(tokens) <= max_length - 2:  # Account for [CLS] and [SEP]
            return [text]
        
        # Split into chunks
        chunks = []
        chunk_size = max_length - 2
        
        for i in range(0, len(tokens), chunk_size):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = self.tokenizer.convert_tokens_to_string(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
    
    def _compute_embedding_hash(self, embeddings: np.ndarray) -> str:
        """
Compute hash from BERT embeddings."""
        # Quantize embeddings to binary
        binary_embeddings = (embeddings > np.median(embeddings)).astype(int)
        
        # Convert to hash
        hash_string = ''.join([str(bit) for bit in binary_embeddings])
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _extract_semantic_features(self, embeddings: np.ndarray) -> Dict[str, float]:
        """
Extract semantic features from embeddings."""
        return {
            "embedding_mean": float(np.mean(embeddings)),
            "embedding_std": float(np.std(embeddings)),
            "embedding_max": float(np.max(embeddings)),
            "embedding_min": float(np.min(embeddings)),
            "embedding_norm": float(np.linalg.norm(embeddings)),
            "embedding_sparsity": float(np.sum(np.abs(embeddings) < 0.01) / len(embeddings))
        }

class MultilingualBERTCopyrightExtractor:
    """
    Multilingual BERT-based semantic similarity for copyright detection across 644 languages.
    
    This class extends the basic BERT functionality to support:
    - Multilingual BERT models (bert-base-multilingual-cased, XLM-RoBERTa)
    - Cross-lingual semantic similarity
    - Integration with 644 language support system
    - Copyright-specific similarity thresholds
    """
    
    def __init__(self, model_name: str = "bert-base-multilingual-cased"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.language_support = None
        self._supported_models = {
            "bert-base-multilingual-cased": "BERT Multilingual",
            "xlm-roberta-base": "XLM-RoBERTa Base", 
            "xlm-roberta-large": "XLM-RoBERTa Large",
            "distilbert-base-multilingual-cased": "DistilBERT Multilingual"
        }
        self._initialize_model()
        self._initialize_language_support()
        
    def _initialize_model(self):
        """Initialize multilingual BERT model."""
        try:
            if self.model_name not in self._supported_models:
                logger.warning(f"Model {self.model_name} not in recommended list. Using anyway.")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.eval()
            logger.info(f"Initialized {self._supported_models.get(self.model_name, self.model_name)} for copyright detection")
        except Exception as e:
            logger.error(f"Multilingual BERT model initialization failed: {e}")
    
    def _initialize_language_support(self):
        """Initialize 644 language support system."""
        if MULTILINGUAL_AVAILABLE:
            try:
                self.language_support = Enhanced644LanguageSupport()
                logger.info("Enhanced 644 language support initialized for copyright detection")
            except Exception as e:
                logger.warning(f"Failed to initialize language support: {e}")
    
    def detect_semantic_copyright_violation(
        self, 
        original_text: str, 
        suspected_text: str,
        similarity_threshold: float = 0.85,
        language_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect potential copyright violation using semantic similarity across languages.
        
        Args:
            original_text: The original copyrighted text
            suspected_text: Text suspected of copyright violation
            similarity_threshold: Similarity threshold for violation detection (0.85 = 85%)
            language_hint: Optional language hint for better processing
            
        Returns:
            Dictionary containing copyright analysis results
        """
        if not self.model or not self.tokenizer:
            return {"error": "Multilingual BERT model not initialized"}
        
        try:
            # Detect languages
            original_lang_info = self._detect_and_analyze_language(original_text)
            suspected_lang_info = self._detect_and_analyze_language(suspected_text)
            
            # Extract multilingual embeddings
            original_embeddings = self._extract_multilingual_embeddings(original_text, original_lang_info.get('language'))
            suspected_embeddings = self._extract_multilingual_embeddings(suspected_text, suspected_lang_info.get('language'))
            
            if "error" in original_embeddings or "error" in suspected_embeddings:
                return {"error": "Failed to extract embeddings for copyright analysis"}
            
            # Calculate semantic similarity
            similarity_score = self._calculate_semantic_similarity(
                original_embeddings['embeddings'], 
                suspected_embeddings['embeddings']
            )
            
            # Determine copyright violation
            is_violation = similarity_score >= similarity_threshold
            
            # Calculate confidence based on text length, language match, etc.
            confidence = self._calculate_violation_confidence(
                original_text, suspected_text, 
                original_lang_info, suspected_lang_info, 
                similarity_score
            )
            
            return {
                "copyright_violation_detected": is_violation,
                "semantic_similarity_score": float(similarity_score),
                "confidence": float(confidence),
                "similarity_threshold": similarity_threshold,
                "original_language": original_lang_info,
                "suspected_language": suspected_lang_info,
                "cross_lingual_analysis": original_lang_info.get('language') != suspected_lang_info.get('language'),
                "model_used": self.model_name,
                "analysis_metadata": {
                    "original_embedding_hash": original_embeddings.get('embedding_hash'),
                    "suspected_embedding_hash": suspected_embeddings.get('embedding_hash'),
                    "original_text_length": len(original_text),
                    "suspected_text_length": len(suspected_text),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Copyright violation detection failed: {e}")
            return {"error": str(e)}
    
    def _detect_and_analyze_language(self, text: str) -> Dict[str, Any]:
        """Detect and analyze language using 644 language support."""
        if self.language_support:
            try:
                # Use enhanced language detection
                detection_result = asyncio.run(self.language_support.detect_language(text))
                return {
                    "language": detection_result.detected_language,
                    "confidence": detection_result.confidence,
                    "language_family": getattr(detection_result, 'language_family', None),
                    "writing_system": getattr(detection_result, 'writing_system', None),
                    "enhanced_detection": True
                }
            except Exception as e:
                logger.warning(f"Enhanced language detection failed: {e}")
        
        # Fallback to basic language detection
        try:
            from langdetect import detect, detect_probabilities
            detected_lang = detect(text)
            probabilities = detect_probabilities(text)
            confidence = max(prob.prob for prob in probabilities) if probabilities else 0.0
            
            return {
                "language": detected_lang,
                "confidence": confidence,
                "enhanced_detection": False
            }
        except Exception as e:
            logger.warning(f"Basic language detection failed: {e}")
            return {
                "language": "unknown",
                "confidence": 0.0,
                "enhanced_detection": False
            }
    
    def _extract_multilingual_embeddings(self, text: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Extract embeddings optimized for multilingual content."""
        try:
            # Preprocess text considering language-specific characteristics
            processed_text = self._preprocess_multilingual_text(text, language)
            
            # Handle long texts by chunking
            chunks = self._chunk_text(processed_text, max_length=512)
            
            chunk_embeddings = []
            for chunk in chunks:
                # Tokenize with multilingual considerations
                inputs = self.tokenizer(
                    chunk,
                    return_tensors="pt",
                    truncation=True,
                    padding=True,
                    max_length=512,
                    add_special_tokens=True
                )
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    
                # Extract embeddings (use [CLS] token for classification tasks)
                cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze()
                chunk_embeddings.append(cls_embedding.numpy())
            
            # Combine chunk embeddings
            if chunk_embeddings:
                combined_embeddings = np.mean(chunk_embeddings, axis=0)
            else:
                # Default size for multilingual BERT
                embedding_size = 768 if "base" in self.model_name else 1024
                combined_embeddings = np.zeros(embedding_size)
            
            # Generate embedding hash
            embedding_hash = self._compute_embedding_hash(combined_embeddings)
            
            # Extract semantic features
            semantic_features = self._extract_semantic_features(combined_embeddings)
            
            return {
                "embeddings": combined_embeddings.tolist(),
                "embedding_hash": embedding_hash,
                "embedding_size": len(combined_embeddings),
                "num_chunks": len(chunks),
                "semantic_features": semantic_features,
                "model_name": self.model_name,
                "language": language,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Multilingual embedding extraction failed: {e}")
            return {"error": str(e)}
    
    def _preprocess_multilingual_text(self, text: str, language: Optional[str] = None) -> str:
        """Preprocess text with multilingual considerations."""
        # Basic preprocessing
        text = text.strip()
        
        # Language-specific preprocessing could be added here
        if language:
            # Handle RTL languages
            if language in ['ar', 'he', 'fa', 'ur']:
                # RTL text preprocessing if needed
                pass
            
            # Handle logographic languages
            elif language in ['zh', 'ja', 'ko']:
                # No space-based tokenization preprocessing
                pass
            
            # Handle complex scripts
            elif language in ['hi', 'bn', 'ta', 'te', 'ml', 'gu', 'mr']:
                # Devanagari and related scripts preprocessing
                pass
        
        # Unicode normalization
        text = unicodedata.normalize('NFKC', text)
        
        return text
    
    def _chunk_text(self, text: str, max_length: int = 512) -> List[str]:
        """Split text into chunks for multilingual processing."""
        # Use tokenizer to get accurate token count
        tokens = self.tokenizer.tokenize(text)
        
        if len(tokens) <= max_length - 2:  # Account for [CLS] and [SEP]
            return [text]
        
        chunks = []
        chunk_size = max_length - 2
        
        for i in range(0, len(tokens), chunk_size):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = self.tokenizer.convert_tokens_to_string(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
    
    def _calculate_semantic_similarity(self, embeddings1: List[float], embeddings2: List[float]) -> float:
        """Calculate cosine similarity between two embedding vectors."""
        try:
            vec1 = np.array(embeddings1)
            vec2 = np.array(embeddings2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Ensure similarity is between 0 and 1
            return max(0.0, min(1.0, float(similarity)))
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_violation_confidence(
        self, 
        original_text: str, 
        suspected_text: str,
        original_lang_info: Dict[str, Any],
        suspected_lang_info: Dict[str, Any],
        similarity_score: float
    ) -> float:
        """Calculate confidence in copyright violation detection."""
        try:
            confidence_factors = []
            
            # Base confidence from similarity score
            base_confidence = similarity_score
            confidence_factors.append(base_confidence * 0.4)  # 40% weight
            
            # Text length factor (longer texts give more confident results)
            min_length = min(len(original_text), len(suspected_text))
            max_length = max(len(original_text), len(suspected_text))
            length_factor = min(1.0, min_length / 100)  # Normalize to 100 chars
            confidence_factors.append(length_factor * 0.2)  # 20% weight
            
            # Language detection confidence
            lang_confidence = (
                original_lang_info.get('confidence', 0.5) + 
                suspected_lang_info.get('confidence', 0.5)
            ) / 2
            confidence_factors.append(lang_confidence * 0.2)  # 20% weight
            
            # Cross-lingual penalty (slightly lower confidence for different languages)
            same_language = original_lang_info.get('language') == suspected_lang_info.get('language')
            cross_lingual_factor = 1.0 if same_language else 0.9
            confidence_factors.append(cross_lingual_factor * 0.1)  # 10% weight
            
            # Text ratio factor (very different lengths might indicate different types of content)
            if max_length > 0:
                ratio_factor = min_length / max_length
                confidence_factors.append(ratio_factor * 0.1)  # 10% weight
            
            # Calculate final confidence
            final_confidence = sum(confidence_factors)
            
            return max(0.0, min(1.0, final_confidence))
            
        except Exception as e:
            logger.warning(f"Confidence calculation failed: {e}")
            return 0.5  # Default moderate confidence
    
    def _compute_embedding_hash(self, embeddings: np.ndarray) -> str:
        """Compute hash from BERT embeddings for copyright fingerprinting."""
        # Quantize embeddings to binary
        binary_embeddings = (embeddings > np.median(embeddings)).astype(int)
        
        # Convert to hash
        hash_string = ''.join([str(bit) for bit in binary_embeddings])
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _extract_semantic_features(self, embeddings: np.ndarray) -> Dict[str, float]:
        """Extract semantic features from embeddings for copyright analysis."""
        return {
            "embedding_mean": float(np.mean(embeddings)),
            "embedding_std": float(np.std(embeddings)),
            "embedding_max": float(np.max(embeddings)),
            "embedding_min": float(np.min(embeddings)),
            "embedding_norm": float(np.linalg.norm(embeddings)),
            "embedding_sparsity": float(np.sum(np.abs(embeddings) < 0.01) / len(embeddings)),
            "semantic_diversity": float(np.std(embeddings) / (np.mean(np.abs(embeddings)) + 1e-8))
        }

class SentenceTransformerExtractor:
    """Sentence-BERT embeddings for better semantic similarity."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize Sentence-BERT model."""
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            logger.warning(f"Sentence-BERT model initialization failed: {e}")
    
    def extract_embeddings(self, text: str) -> Dict[str, Any]:
        """
        Extract sentence-level embeddings.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing sentence embeddings
        """
        if not self.model:
            return {"error": "Sentence-BERT model not initialized"}
            
        try:
            # Split into sentences
            sentences = sent_tokenize(text)
            
            if not sentences:
                return {"error": "No sentences found"}
            
            # Extract embeddings for each sentence
            sentence_embeddings = self.model.encode(sentences)
            
            # Compute document-level embedding (average of sentences)
            doc_embedding = np.mean(sentence_embeddings, axis=0)
            
            # Generate embedding hash
            embedding_hash = self._compute_embedding_hash(doc_embedding)
            
            return {
                "doc_embedding": doc_embedding.tolist(),
                "sentence_embeddings": sentence_embeddings.tolist(),
                "embedding_hash": embedding_hash,
                "num_sentences": len(sentences),
                "embedding_size": len(doc_embedding),
                "model_name": self.model_name,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sentence-BERT extraction failed: {e}")
            return {"error": str(e)}
    
    def _compute_embedding_hash(self, embeddings: np.ndarray) -> str:
        """Compute hash from sentence embeddings."""
        binary_embeddings = (embeddings > np.median(embeddings)).astype(int)
        hash_string = ''.join([str(bit) for bit in binary_embeddings])
        return hashlib.md5(hash_string.encode()).hexdigest()

class TFIDFAnalyzer:
    """
TF-IDF vectorization and analysis."""
    
    def __init__(self, max_features: int = 5000, ngram_range: Tuple[int, int] = (1, 3)):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vectorizer = None
        self.stop_words = self._get_stop_words()
        
    def _get_stop_words(self) -> Set[str]:
        """
Get combined stop words from multiple sources."""
        try:
            nltk_stops = set(stopwords.words('english'))
        except LookupError:
            nltk_stops = set()
        
        # Additional stop words
        custom_stops = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'this', 'that', 'these', 'those', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
            'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
            'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves'
        }
        
        return nltk_stops.union(custom_stops)
    
    def analyze_tfidf(self, text: str) -> Dict[str, Any]:
        """
        Perform TF-IDF analysis on text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing TF-IDF analysis results
        """
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Initialize vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                ngram_range=self.ngram_range,
                stop_words=list(self.stop_words),
                lowercase=True,
                strip_accents='unicode'
            )
            
            # Fit and transform
            tfidf_matrix = self.vectorizer.fit_transform([processed_text])
            
            # Get feature names and scores
            feature_names = self.vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Create feature dictionary
            feature_scores = dict(zip(feature_names, tfidf_scores))
            
            # Get top features
            top_features = sorted(feature_scores.items(), key=lambda x: x[1], reverse=True)[:50]
            
            # Generate TF-IDF fingerprint
            tfidf_fingerprint = self._generate_tfidf_fingerprint(tfidf_scores)
            
            # Calculate document statistics
            doc_stats = self._calculate_document_stats(tfidf_scores, feature_names)
            
            return {
                "tfidf_vector": tfidf_scores.tolist(),
                "top_features": top_features,
                "document_stats": doc_stats,
                "tfidf_fingerprint": tfidf_fingerprint,
                "vocabulary_size": len(feature_names),
                "ngram_range": self.ngram_range,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"TF-IDF analysis failed: {e}")
            return {"error": str(e)}
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for TF-IDF analysis."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _generate_tfidf_fingerprint(self, tfidf_scores: np.ndarray) -> str:
        """
Generate fingerprint from TF-IDF scores."""
        # Use top N features for fingerprint
        top_indices = np.argsort(tfidf_scores)[-100:][::-1]  # Top 100 features
        top_scores = tfidf_scores[top_indices]
        
        # Quantize scores
        quantized_scores = np.round(top_scores * 1000).astype(int)
        
        # Create hash
        fingerprint_string = "|".join(map(str, quantized_scores))
        return hashlib.md5(fingerprint_string.encode()).hexdigest()
    
    def _calculate_document_stats(self, tfidf_scores: np.ndarray, feature_names: np.ndarray) -> Dict[str, float]:
        """Calculate document-level statistics from TF-IDF."""
        non_zero_scores = tfidf_scores[tfidf_scores > 0]
        
        return {
            "tfidf_mean": float(np.mean(non_zero_scores)) if len(non_zero_scores) > 0 else 0.0,
            "tfidf_std": float(np.std(non_zero_scores)) if len(non_zero_scores) > 0 else 0.0,
            "tfidf_max": float(np.max(tfidf_scores)),
            "tfidf_sparsity": float(np.sum(tfidf_scores == 0) / len(tfidf_scores)),
            "unique_terms": int(np.sum(tfidf_scores > 0)),
            "vocabulary_coverage": float(np.sum(tfidf_scores > 0) / len(tfidf_scores))
        }

class NGramAnalyzer:
    """N-gram analysis for pattern detection and fingerprinting."""
    
    def __init__(self, max_n: int = 5):
        self.max_n = max_n
        self.stemmer = PorterStemmer()
        
    def analyze_ngrams(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive N-gram analysis.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing N-gram analysis results
        """
        try:
            # Preprocess and tokenize
            tokens = self._preprocess_and_tokenize(text)
            
            if not tokens:
                return {"error": "No tokens found after preprocessing"}
            
            # Generate N-grams for different N values
            ngram_data = {}
            for n in range(1, self.max_n + 1):
                ngram_data[f"{n}gram"] = self._extract_ngrams(tokens, n)
            
            # Character-level N-grams
            char_ngrams = self._extract_character_ngrams(text)
            
            # Generate N-gram fingerprints
            ngram_fingerprints = self._generate_ngram_fingerprints(ngram_data, char_ngrams)
            
            # Calculate diversity metrics
            diversity_metrics = self._calculate_diversity_metrics(ngram_data)
            
            return {
                "ngram_data": ngram_data,
                "char_ngrams": char_ngrams,
                "ngram_fingerprints": ngram_fingerprints,
                "diversity_metrics": diversity_metrics,
                "total_tokens": len(tokens),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"N-gram analysis failed: {e}")
            return {"error": str(e)}
    
    def _preprocess_and_tokenize(self, text: str) -> List[str]:
        """Preprocess text and tokenize into words."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation but keep word boundaries
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove very short tokens and numbers
        tokens = [token for token in tokens if len(token) > 2 and not token.isdigit()]
        
        # Optional: stem tokens
        # tokens = [self.stemmer.stem(token) for token in tokens]
        
        return tokens
    
    def _extract_ngrams(self, tokens: List[str], n: int) -> Dict[str, Any]:
        """
Extract N-grams of specified length."""
        if len(tokens) < n:
            return {"ngrams": [], "frequencies": {}, "total_count": 0}
        
        # Generate N-grams
        token_ngrams = list(ngrams(tokens, n))
        
        # Count frequencies
        ngram_counts = Counter(token_ngrams)
        
        # Convert to strings for serialization
        ngram_strings = [" ".join(ngram) for ngram in token_ngrams]
        frequency_dict = {" ".join(k): v for k, v in ngram_counts.items()}
        
        # Get most common N-grams
        most_common = ngram_counts.most_common(20)
        most_common_strings = [(" ".join(ngram), count) for ngram, count in most_common]
        
        return {
            "ngrams": ngram_strings[:100],  # Limit size
            "frequencies": frequency_dict,
            "most_common": most_common_strings,
            "total_count": len(token_ngrams),
            "unique_count": len(ngram_counts)
        }
    
    def _extract_character_ngrams(self, text: str, n_values: List[int] = [3, 4, 5]) -> Dict[str, Any]:
        """Extract character-level N-grams."""
        # Clean text
        clean_text = re.sub(r'\s+', ' ', text.lower())
        clean_text = re.sub(r'[^a-z0-9\s]', '', clean_text)
        
        char_ngram_data = {}
        
        for n in n_values:
            if len(clean_text) >= n:
                # Generate character N-grams
                char_ngrams = [clean_text[i:i+n] for i in range(len(clean_text) - n + 1)]
                
                # Count frequencies
                char_counts = Counter(char_ngrams)
                
                # Get most common
                most_common = char_counts.most_common(20)
                
                char_ngram_data[f"char_{n}gram"] = {
                    "frequencies": dict(char_counts),
                    "most_common": most_common,
                    "total_count": len(char_ngrams),
                    "unique_count": len(char_counts)
                }
        
        return char_ngram_data
    
    def _generate_ngram_fingerprints(self, ngram_data: Dict, char_ngrams: Dict) -> Dict[str, str]:
        """Generate fingerprints from N-gram data."""
        fingerprints = {}
        
        # Word N-gram fingerprints
        for ngram_type, data in ngram_data.items():
            if "most_common" in data and data["most_common"]:
                # Use most common N-grams for fingerprint
                common_ngrams = [ngram for ngram, count in data["most_common"][:20]]
                fingerprint_string = "|".join(common_ngrams)
                fingerprints[f"{ngram_type}_fingerprint"] = hashlib.md5(fingerprint_string.encode()).hexdigest()
        
        # Character N-gram fingerprints
        for char_type, data in char_ngrams.items():
            if "most_common" in data and data["most_common"]:
                common_chars = [ngram for ngram, count in data["most_common"][:20]]
                fingerprint_string = "|".join(common_chars)
                fingerprints[f"{char_type}_fingerprint"] = hashlib.md5(fingerprint_string.encode()).hexdigest()
        
        return fingerprints
    
    def _calculate_diversity_metrics(self, ngram_data: Dict) -> Dict[str, float]:
        """Calculate lexical diversity metrics."""
        metrics = {}
        
        for ngram_type, data in ngram_data.items():
            total_count = data.get("total_count", 0)
            unique_count = data.get("unique_count", 0)
            
            if total_count > 0:
                # Type-Token Ratio (TTR)
                ttr = unique_count / total_count
                
                # Lexical diversity (using Yule's K)
                frequencies = list(data.get("frequencies", {}).values())
                if frequencies:
                    yule_k = 10000 * (sum(freq * freq for freq in frequencies) / (total_count * total_count) - 1)
                else:
                    yule_k = 0.0
                
                metrics[f"{ngram_type}_ttr"] = ttr
                metrics[f"{ngram_type}_yule_k"] = yule_k
        
        return metrics

class SemanticAnalyzer:
    """Semantic analysis including topic modeling and sentiment analysis."""
    
    def __init__(self):
        self.sentiment_pipeline = None
        self.ner_pipeline = None
        self._initialize_pipelines()
        
    def _initialize_pipelines(self):
        """
Initialize HuggingFace pipelines."""
        try:
            self.sentiment_pipeline = pipeline("sentiment-analysis")
            self.ner_pipeline = pipeline("ner", aggregation_strategy="simple")
        except Exception as e:
            logger.warning(f"Pipeline initialization failed: {e}")
    
    def analyze_semantics(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive semantic analysis.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing semantic analysis results
        """
        try:
            # Language detection
            language_info = self._detect_language(text)
            
            # Sentiment analysis
            sentiment_info = self._analyze_sentiment(text)
            
            # Named entity recognition
            ner_info = self._extract_named_entities(text)
            
            # Topic modeling (simplified)
            topic_info = self._analyze_topics(text)
            
            # Readability analysis
            readability_info = self._analyze_readability(text)
            
            # Generate semantic fingerprint
            semantic_fingerprint = self._generate_semantic_fingerprint(
                sentiment_info, ner_info, topic_info, readability_info
            )
            
            return {
                "language": language_info,
                "sentiment": sentiment_info,
                "named_entities": ner_info,
                "topics": topic_info,
                "readability": readability_info,
                "semantic_fingerprint": semantic_fingerprint,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Semantic analysis failed: {e}")
            return {"error": str(e)}
    
    def _detect_language(self, text: str) -> Dict[str, Any]:
        """Detect text language."""
        try:
            # Clean text for language detection
            clean_text = re.sub(r'[^a-zA-Z\s]', ' ', text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            if len(clean_text) < 10:
                return {"language": "unknown", "confidence": 0.0}
            
            detected_lang = detect(clean_text)
            
            return {
                "language": detected_lang,
                "confidence": 1.0,  # langdetect doesn't provide confidence
                "text_length": len(clean_text)
            }
            
        except LangDetectError:
            return {"language": "unknown", "confidence": 0.0}
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {"error": str(e)}
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze text sentiment."""
        if not self.sentiment_pipeline:
            return {"error": "Sentiment pipeline not initialized"}
            
        try:
            # Split long text into chunks
            chunks = self._split_text_into_chunks(text, max_length=500)
            
            chunk_sentiments = []
            for chunk in chunks:
                if len(chunk.strip()) > 10:  # Only analyze non-empty chunks
                    result = self.sentiment_pipeline(chunk)[0]
                    chunk_sentiments.append(result)
            
            if not chunk_sentiments:
                return {"overall_sentiment": "NEUTRAL", "confidence": 0.0, "chunks": []}
            
            # Aggregate sentiment
            positive_scores = [r['score'] for r in chunk_sentiments if r['label'] == 'POSITIVE']
            negative_scores = [r['score'] for r in chunk_sentiments if r['label'] == 'NEGATIVE']
            
            avg_positive = np.mean(positive_scores) if positive_scores else 0.0
            avg_negative = np.mean(negative_scores) if negative_scores else 0.0
            
            if avg_positive > avg_negative:
                overall_sentiment = "POSITIVE"
                overall_confidence = avg_positive
            elif avg_negative > avg_positive:
                overall_sentiment = "NEGATIVE"
                overall_confidence = avg_negative
            else:
                overall_sentiment = "NEUTRAL"
                overall_confidence = 0.5
            
            return {
                "overall_sentiment": overall_sentiment,
                "confidence": float(overall_confidence),
                "positive_ratio": len(positive_scores) / len(chunk_sentiments),
                "negative_ratio": len(negative_scores) / len(chunk_sentiments),
                "chunk_sentiments": chunk_sentiments[:10]  # Limit output size
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"error": str(e)}
    
    def _extract_named_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text."""
        if not self.ner_pipeline:
            return {"error": "NER pipeline not initialized"}
            
        try:
            # Split long text into chunks
            chunks = self._split_text_into_chunks(text, max_length=500)
            
            all_entities = []
            entity_counts = Counter()
            
            for chunk in chunks:
                if len(chunk.strip()) > 10:
                    entities = self.ner_pipeline(chunk)
                    
                    for entity in entities:
                        entity_info = {
                            "text": entity["word"],
                            "label": entity["entity_group"],
                            "confidence": entity["score"],
                            "start": entity["start"],
                            "end": entity["end"]
                        }
                        all_entities.append(entity_info)
                        entity_counts[entity["entity_group"]] += 1
            
            # Group entities by type
            entities_by_type = {}
            for entity in all_entities:
                entity_type = entity["label"]
                if entity_type not in entities_by_type:
                    entities_by_type[entity_type] = []
                entities_by_type[entity_type].append(entity)
            
            return {
                "entities": all_entities[:50],  # Limit output size
                "entity_counts": dict(entity_counts),
                "entities_by_type": {k: v[:10] for k, v in entities_by_type.items()},  # Limit per type
                "total_entities": len(all_entities),
                "unique_entity_types": len(entity_counts)
            }
            
        except Exception as e:
            logger.error(f"NER extraction failed: {e}")
            return {"error": str(e)}
    
    def _analyze_topics(self, text: str) -> Dict[str, Any]:
        """Simplified topic analysis using keyword extraction."""
        try:
            # Preprocess text
            tokens = self._preprocess_and_tokenize(text)
            
            if len(tokens) < 10:
                return {"topics": [], "keywords": [], "topic_coherence": 0.0}
            
            # Simple keyword extraction using TF-IDF
            vectorizer = TfidfVectorizer(
                max_features=100,
                ngram_range=(1, 2),
                stop_words='english'
            )
            
            tfidf_matrix = vectorizer.fit_transform([" ".join(tokens)])
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            top_indices = np.argsort(tfidf_scores)[-20:][::-1]
            keywords = [(feature_names[i], float(tfidf_scores[i])) for i in top_indices if tfidf_scores[i] > 0]
            
            # Simple topic clustering (group similar keywords)
            topics = self._cluster_keywords(keywords)
            
            return {
                "keywords": keywords,
                "topics": topics,
                "num_keywords": len(keywords),
                "topic_coherence": self._calculate_topic_coherence(topics)
            }
            
        except Exception as e:
            logger.error(f"Topic analysis failed: {e}")
            return {"error": str(e)}
    
    def _cluster_keywords(self, keywords: List[Tuple[str, float]]) -> List[Dict[str, Any]]:
        """Simple keyword clustering for topic identification."""
        # Group keywords by semantic similarity (simplified)
        topics = []
        used_keywords = set()
        
        for keyword, score in keywords:
            if keyword in used_keywords:
                continue
                
            # Create topic with current keyword as seed
            topic_keywords = [(keyword, score)]
            used_keywords.add(keyword)
            
            # Find similar keywords (simple word overlap)
            for other_keyword, other_score in keywords:
                if other_keyword in used_keywords:
                    continue
                    
                # Simple similarity: shared words
                if self._keywords_similar(keyword, other_keyword):
                    topic_keywords.append((other_keyword, other_score))
                    used_keywords.add(other_keyword)
            
            if len(topic_keywords) >= 2:  # Only create topics with multiple keywords
                topics.append({
                    "topic_id": len(topics),
                    "keywords": topic_keywords,
                    "topic_score": sum(score for _, score in topic_keywords)
                })
        
        return topics[:5]  # Limit to top 5 topics
    
    def _keywords_similar(self, kw1: str, kw2: str) -> bool:
        """Check if two keywords are similar."""
        words1 = set(kw1.lower().split())
        words2 = set(kw2.lower().split())
        
        # Check for word overlap
        overlap = len(words1.intersection(words2))
        return overlap > 0 and overlap / max(len(words1), len(words2)) > 0.3
    
    def _calculate_topic_coherence(self, topics: List[Dict[str, Any]]) -> float:
        """
Calculate topic coherence score."""
        if not topics:
            return 0.0
        
        # Simple coherence: average topic score normalized by number of keywords
        coherence_scores = []
        for topic in topics:
            if topic["keywords"]:
                avg_score = topic["topic_score"] / len(topic["keywords"])
                coherence_scores.append(avg_score)
        
        return float(np.mean(coherence_scores)) if coherence_scores else 0.0
    
    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability."""
        try:
            # Basic text statistics
            sentences = sent_tokenize(text)
            words = word_tokenize(text.lower())
            words = [w for w in words if w.isalpha()]
            
            # Calculate basic metrics
            char_count = len(text)
            word_count = len(words)
            sentence_count = len(sentences)
            
            if sentence_count == 0 or word_count == 0:
                return {"error": "Text too short for readability analysis"}
            
            avg_sentence_length = word_count / sentence_count
            avg_word_length = sum(len(word) for word in words) / word_count
            
            # Lexical diversity
            unique_words = len(set(words))
            lexical_diversity = unique_words / word_count if word_count > 0 else 0
            
            # Use textstat for advanced metrics
            flesch_score = textstat.flesch_reading_ease(text)
            flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
            
            return {
                "char_count": char_count,
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_sentence_length": avg_sentence_length,
                "avg_word_length": avg_word_length,
                "lexical_diversity": lexical_diversity,
                "flesch_reading_ease": flesch_score,
                "flesch_kincaid_grade": flesch_kincaid_grade,
                "readability_level": self._interpret_flesch_score(flesch_score)
            }
            
        except Exception as e:
            logger.error(f"Readability analysis failed: {e}")
            return {"error": str(e)}
    
    def _interpret_flesch_score(self, score: float) -> str:
        """Interpret Flesch reading ease score."""
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def _split_text_into_chunks(self, text: str, max_length: int = 500) -> List[str]:
        """Split text into chunks for processing."""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _preprocess_and_tokenize(self, text: str) -> List[str]:
        """Preprocess text and tokenize."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Filter tokens
        tokens = [token for token in tokens if len(token) > 2 and not token.isdigit()]
        
        return tokens
    
    def _generate_semantic_fingerprint(self, sentiment_info: Dict, ner_info: Dict,
                                     topic_info: Dict, readability_info: Dict) -> str:
        """
Generate fingerprint from semantic analysis."""
        fingerprint_components = []
        
        # Sentiment fingerprint
        if "overall_sentiment" in sentiment_info:
            sentiment_string = f"{sentiment_info['overall_sentiment']}:{sentiment_info.get('confidence', 0):.2f}"
            fingerprint_components.append(sentiment_string)
        
        # Entity fingerprint
        if "entity_counts" in ner_info:
            entity_string = "|".join([f"{k}:{v}" for k, v in ner_info["entity_counts"].items()])
            fingerprint_components.append(entity_string)
        
        # Topic fingerprint
        if "keywords" in topic_info and topic_info["keywords"]:
            keyword_string = "|".join([kw for kw, score in topic_info["keywords"][:10]])
            fingerprint_components.append(keyword_string)
        
        # Readability fingerprint
        if "flesch_reading_ease" in readability_info:
            readability_string = f"flesch:{readability_info['flesch_reading_ease']:.1f}"
            fingerprint_components.append(readability_string)
        
        # Combine all components
        if fingerprint_components:
            combined_string = "|".join(fingerprint_components)
            return hashlib.md5(combined_string.encode()).hexdigest()
        
        return ""

class TextFingerprintingService:
    """
    Comprehensive text fingerprinting service combining multiple NLP techniques.
    
    Features:
    - BERT/RoBERTa neural embeddings
    - Sentence-BERT for semantic similarity
    - TF-IDF vectorization
    - N-gram analysis (word and character level)
    - Semantic analysis (sentiment, NER, topics)
    - Plagiarism detection capabilities
    - Multi-language support
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bert_extractor = BERTEmbeddingExtractor()
        self.sentence_bert_extractor = SentenceTransformerExtractor()
        self.tfidf_analyzer = TFIDFAnalyzer()
        self.ngram_analyzer = NGramAnalyzer()
        self.semantic_analyzer = SemanticAnalyzer()
        
        # NEW: Add multilingual BERT copyright detector
        self.multilingual_copyright_detector = MultilingualBERTCopyrightExtractor(
            model_name=config.get("multilingual_model", "bert-base-multilingual-cased")
        )
        
        # Similarity thresholds
        self.similarity_thresholds = {
            "bert": 0.85,
            "sentence_bert": 0.90,
            "tfidf": 0.75,
            "ngrams": 0.80,
            "semantic": 0.70,
            "combined": 0.80,
            # NEW: Copyright detection threshold
            "copyright_semantic": 0.85
        }
        
    async def process_text(self, text: str, user_id: int, file_path: Optional[str] = None) -> FingerprintResult:
        """
        Process text and generate comprehensive fingerprint.
        
        Args:
            text: Input text content
            user_id: User ID for attribution
            file_path: Optional path to text file
            
        Returns:
            FingerprintResult containing all fingerprint data
        """
        try:
            logger.info(f"Processing text fingerprint for user {user_id}")
            
            # Extract metadata
            metadata = await self._extract_metadata(text)
            
            # Run all fingerprinting algorithms in parallel
            tasks = [
                asyncio.create_task(self._run_bert_extraction(text)),
                asyncio.create_task(self._run_sentence_bert_extraction(text)),
                asyncio.create_task(self._run_tfidf_analysis(text)),
                asyncio.create_task(self._run_ngram_analysis(text)),
                asyncio.create_task(self._run_semantic_analysis(text))
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            bert_result = results[0] if not isinstance(results[0], Exception) else {}
            sentence_bert_result = results[1] if not isinstance(results[1], Exception) else {}
            tfidf_result = results[2] if not isinstance(results[2], Exception) else {}
            ngram_result = results[3] if not isinstance(results[3], Exception) else {}
            semantic_result = results[4] if not isinstance(results[4], Exception) else {}
            
            # Combine results
            fingerprint_data = {
                "bert": bert_result,
                "sentence_bert": sentence_bert_result,
                "tfidf": tfidf_result,
                "ngrams": ngram_result,
                "semantics": semantic_result,
                "metadata": metadata,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
            # Generate combined hash
            combined_hash = self._generate_combined_hash(fingerprint_data)
            
            return FingerprintResult(
                user_id=user_id,
                content_type="text",
                file_path=file_path,
                fingerprint_data=fingerprint_data,
                hash_value=combined_hash,
                processing_time=datetime.utcnow(),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Text fingerprinting failed: {e}")
            raise
    
    async def detect_copyright_violation(
        self, 
        original_text: str, 
        suspected_text: str,
        similarity_threshold: Optional[float] = None,
        language_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect potential copyright violation using multilingual BERT semantic similarity.
        
        This method provides advanced copyright detection across 644 languages using:
        - Multilingual BERT models for cross-lingual understanding
        - Enhanced language detection and analysis
        - Semantic similarity scoring
        - Confidence assessment based on multiple factors
        
        Args:
            original_text: The original copyrighted text
            suspected_text: Text suspected of copyright violation
            similarity_threshold: Custom threshold (defaults to config)
            language_hint: Optional language hint for better processing
            
        Returns:
            Dictionary containing comprehensive copyright analysis
        """
        try:
            logger.info("Starting multilingual copyright violation detection")
            
            # Use configured threshold if not provided
            threshold = similarity_threshold or self.similarity_thresholds["copyright_semantic"]
            
            # Run copyright detection using multilingual BERT
            detection_result = self.multilingual_copyright_detector.detect_semantic_copyright_violation(
                original_text=original_text,
                suspected_text=suspected_text,
                similarity_threshold=threshold,
                language_hint=language_hint
            )
            
            # Add additional context and metadata
            detection_result.update({
                "service_version": "v1.0",
                "detection_engine": "MultilinguaBERT-644Lang",
                "enhanced_features": {
                    "cross_lingual_support": True,
                    "language_count": 644,
                    "advanced_confidence_scoring": True,
                    "enterprise_grade": True
                }
            })
            
            logger.info(f"Copyright detection completed. Violation detected: {detection_result.get('copyright_violation_detected', False)}")
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Copyright violation detection failed: {e}")
            return {
                "error": str(e),
                "copyright_violation_detected": False,
                "confidence": 0.0,
                "analysis_failed": True
            }
    
    async def _extract_metadata(self, text: str) -> TextMetadata:
        """Extract comprehensive text metadata."""
        try:
            # Basic counts
            char_count = len(text)
            words = word_tokenize(text.lower())
            words = [w for w in words if w.isalpha()]
            word_count = len(words)
            
            sentences = sent_tokenize(text)
            sentence_count = len(sentences)
            
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            paragraph_count = len(paragraphs)
            
            # Language detection
            try:
                language = detect(text) if len(text) > 10 else None
            except:
                language = None
            
            # Readability
            try:
                readability_score = textstat.flesch_reading_ease(text)
            except:
                readability_score = None
            
            # Lexical diversity
            unique_words = len(set(words))
            lexical_diversity = unique_words / word_count if word_count > 0 else 0
            
            # Average sentence length
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # Complexity score (simplified)
            complexity_score = self._calculate_complexity_score(text, words, sentences)
            
            return TextMetadata(
                char_count=char_count,
                word_count=word_count,
                sentence_count=sentence_count,
                paragraph_count=paragraph_count,
                language=language,
                readability_score=readability_score,
                sentiment_score=None,  # Will be filled by semantic analysis
                named_entities=None,  # Will be filled by semantic analysis
                pos_tags=None,  # Could be added
                lexical_diversity=lexical_diversity,
                avg_sentence_length=avg_sentence_length,
                complexity_score=complexity_score
            )
            
        except Exception as e:
            logger.error(f"Text metadata extraction failed: {e}")
            return TextMetadata(
                char_count=0, word_count=0, sentence_count=0, paragraph_count=0,
                language=None, readability_score=None, sentiment_score=None,
                named_entities=None, pos_tags=None, lexical_diversity=None,
                avg_sentence_length=None, complexity_score=None
            )
    
    def _calculate_complexity_score(self, text: str, words: List[str], sentences: List[str]) -> float:
        """Calculate text complexity score."""
        try:
            # Average word length
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            # Average sentence length
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            
            # Vocabulary richness
            unique_words = len(set(words))
            vocab_richness = unique_words / len(words) if words else 0
            
            # Normalize and combine metrics
            complexity = (
                (avg_word_length / 10) * 0.3 +  # Word complexity
                (avg_sentence_length / 20) * 0.4 +  # Sentence complexity
                (vocab_richness) * 0.3  # Vocabulary richness
            )
            
            return min(complexity, 1.0)  # Cap at 1.0
            
        except Exception:
            return 0.0
    
    async def _run_bert_extraction(self, text: str) -> Dict[str, Any]:
        """
Run BERT embedding extraction."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.bert_extractor.extract_embeddings, text
        )
    
    async def _run_sentence_bert_extraction(self, text: str) -> Dict[str, Any]:
        """
Run Sentence-BERT extraction."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.sentence_bert_extractor.extract_embeddings, text
        )
    
    async def _run_tfidf_analysis(self, text: str) -> Dict[str, Any]:
        """
Run TF-IDF analysis."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.tfidf_analyzer.analyze_tfidf, text
        )
    
    async def _run_ngram_analysis(self, text: str) -> Dict[str, Any]:
        """
Run N-gram analysis."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.ngram_analyzer.analyze_ngrams, text
        )
    
    async def _run_semantic_analysis(self, text: str) -> Dict[str, Any]:
        """
Run semantic analysis."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.semantic_analyzer.analyze_semantics, text
        )
    
    def _generate_combined_hash(self, fingerprint_data: Dict[str, Any]) -> str:
        """
Generate combined hash from all fingerprint components."""
        hash_components = []
        
        # Extract key hash components
        if "bert" in fingerprint_data and "embedding_hash" in fingerprint_data["bert"]:
            hash_components.append(fingerprint_data["bert"]["embedding_hash"])
            
        if "sentence_bert" in fingerprint_data and "embedding_hash" in fingerprint_data["sentence_bert"]:
            hash_components.append(fingerprint_data["sentence_bert"]["embedding_hash"])
            
        if "tfidf" in fingerprint_data and "tfidf_fingerprint" in fingerprint_data["tfidf"]:
            hash_components.append(fingerprint_data["tfidf"]["tfidf_fingerprint"])
            
        if "ngrams" in fingerprint_data and "ngram_fingerprints" in fingerprint_data["ngrams"]:
            ngram_hashes = list(fingerprint_data["ngrams"]["ngram_fingerprints"].values())
            hash_components.extend(ngram_hashes[:3])  # Limit to first 3
            
        if "semantics" in fingerprint_data and "semantic_fingerprint" in fingerprint_data["semantics"]:
            hash_components.append(fingerprint_data["semantics"]["semantic_fingerprint"])
        
        # Combine and hash
        combined_string = "|".join(hash_components)
        return hashlib.sha256(combined_string.encode()).hexdigest()
    
    async def find_similar(self, fingerprint_data: Dict[str, Any], threshold: float = 0.8) -> List[SimilarityMatch]:
        """
        Find similar text content based on fingerprint data.
        
        Args:
            fingerprint_data: Fingerprint data to match against
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            List of similarity matches
        """
        # This would typically interface with a vector database
        # For now, return empty list (implementation depends on storage backend)
        logger.info(f"Searching for similar text with threshold {threshold}")
        return []
    
    def calculate_similarity(self, fp1: Dict[str, Any], fp2: Dict[str, Any]) -> float:
        """
        Calculate similarity score between two text fingerprints.
        
        Args:
            fp1: First fingerprint data
            fp2: Second fingerprint data
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        similarity_scores = []
        
        # BERT similarity
        if ("bert" in fp1 and "bert" in fp2 and
            "embeddings" in fp1["bert"] and "embeddings" in fp2["bert"]):
            bert_sim = self._cosine_similarity(fp1["bert"]["embeddings"], fp2["bert"]["embeddings"])
            similarity_scores.append(bert_sim * 0.35)  # 35% weight
        
        # Sentence-BERT similarity
        if ("sentence_bert" in fp1 and "sentence_bert" in fp2 and
            "doc_embedding" in fp1["sentence_bert"] and "doc_embedding" in fp2["sentence_bert"]):
            sbert_sim = self._cosine_similarity(fp1["sentence_bert"]["doc_embedding"], fp2["sentence_bert"]["doc_embedding"])
            similarity_scores.append(sbert_sim * 0.35)  # 35% weight
        
        # TF-IDF similarity
        if ("tfidf" in fp1 and "tfidf" in fp2 and
            "tfidf_vector" in fp1["tfidf"] and "tfidf_vector" in fp2["tfidf"]):
            tfidf_sim = self._cosine_similarity(fp1["tfidf"]["tfidf_vector"], fp2["tfidf"]["tfidf_vector"])
            similarity_scores.append(tfidf_sim * 0.2)  # 20% weight
        
        # N-gram similarity
        if ("ngrams" in fp1 and "ngrams" in fp2 and
            "ngram_fingerprints" in fp1["ngrams"] and "ngram_fingerprints" in fp2["ngrams"]):
            ngram_sim = self._ngram_similarity(fp1["ngrams"]["ngram_fingerprints"], fp2["ngrams"]["ngram_fingerprints"])
            similarity_scores.append(ngram_sim * 0.1)  # 10% weight
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors."""
        try:
            vec1_array = np.array(vec1)
            vec2_array = np.array(vec2)
            
            dot_product = np.dot(vec1_array, vec2_array)
            norm1 = np.linalg.norm(vec1_array)
            norm2 = np.linalg.norm(vec2_array)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
                
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {e}")
            return 0.0
    
    def _ngram_similarity(self, ngrams1: Dict[str, str], ngrams2: Dict[str, str]) -> float:
        """Calculate N-gram fingerprint similarity."""
        try:
            # Compare common fingerprint types
            common_types = set(ngrams1.keys()).intersection(set(ngrams2.keys()))
            
            if not common_types:
                return 0.0
            
            similarities = []
            for ngram_type in common_types:
                hash1 = ngrams1[ngram_type]
                hash2 = ngrams2[ngram_type]
                
                # Simple hash comparison
                if hash1 == hash2:
                    similarities.append(1.0)
                else:
                    # Character-level similarity
                    char_sim = sum(c1 == c2 for c1, c2 in zip(hash1, hash2)) / max(len(hash1), len(hash2))
                    similarities.append(char_sim)
            
            return sum(similarities) / len(similarities)
            
        except Exception as e:
            logger.error(f"N-gram similarity calculation failed: {e}")
            return 0.0
