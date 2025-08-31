"""Advanced Text Fingerprinting Engine
Uses BERT, RoBERTa, and NLP techniques for text content identification

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All Rights Reserved - Unauthorized use prohibited
Team: Lead Dev IA + Backend Senior + ML Engineer + NLP Expert

WARNING: This code is proprietary and confidential. Any unauthorized copying,
distribution, modification or use is strictly prohibited and will be prosecuted
to the full extent of the law.
"""import numpy as np
from typing import Dict, List, Tuple, Optional
import hashlib
import re
from collections import Counter
import logging
from dataclasses import dataclass
import torch
from transformers import AutoTokenizer, AutoModel, pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
import spacy
from textstat import flesch_reading_ease, flesch_kincaid_grade
import string

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

logger = logging.getLogger(__name__)


@dataclass
class TextFingerprint:
    """Text fingerprint data structure"""    semantic_embedding: np.ndarray
    tfidf_vector: np.ndarray
    content_hash: str
    structure_hash: str
    stylometric_features: Dict
    ngram_signatures: Dict
    readability_scores: Dict
    language: str
    word_count: int
    character_count: int
    confidence_score: float


class TextFingerprintEngine:
    """    Enterprise-grade text fingerprinting using multiple NLP algorithms
    Combines semantic embeddings, stylometric analysis, and structure hashing
    """    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.nlp = None
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        try:
            # Load transformer model for semantic embeddings
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            logger.info(f"Text model {model_name} loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load transformer model: {e}")
            
        try:
            # Load spaCy model for advanced NLP
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.warning(f"Failed to load spaCy model: {e}")
            
        # Initialize TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3),
            lowercase=True
        )
        
    def extract_fingerprint(self, text: str, title: str = "") -> TextFingerprint:
        """Extract comprehensive text fingerprint"""        try:
            # Clean text
            cleaned_text = self._clean_text(text)
            
            if not cleaned_text.strip():
                raise ValueError("Empty or invalid text content")
                
            # 1. Semantic embedding
            semantic_embedding = self._extract_semantic_embedding(cleaned_text)
            
            # 2. TF-IDF vector
            tfidf_vector = self._extract_tfidf_features(cleaned_text)
            
            # 3. Content hash
            content_hash = self._compute_content_hash(cleaned_text)
            
            # 4. Structure hash
            structure_hash = self._compute_structure_hash(text)  # Use original text for structure
            
            # 5. Stylometric features
            stylometric_features = self._extract_stylometric_features(cleaned_text)
            
            # 6. N-gram signatures
            ngram_signatures = self._extract_ngram_signatures(cleaned_text)
            
            # 7. Readability scores
            readability_scores = self._compute_readability_scores(cleaned_text)
            
            # 8. Language detection
            language = self._detect_language(cleaned_text)
            
            # 9. Basic statistics
            word_count = len(word_tokenize(cleaned_text))
            character_count = len(cleaned_text)
            
            # 10. Confidence score
            confidence_score = self._calculate_confidence(cleaned_text, word_count)
            
            return TextFingerprint(
                semantic_embedding=semantic_embedding,
                tfidf_vector=tfidf_vector,
                content_hash=content_hash,
                structure_hash=structure_hash,
                stylometric_features=stylometric_features,
                ngram_signatures=ngram_signatures,
                readability_scores=readability_scores,
                language=language,
                word_count=word_count,
                character_count=character_count,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Error extracting text fingerprint: {str(e)}")
            raise
            
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove non-printable characters
            text = ''.join(char for char in text if char.isprintable())
            
            # Normalize quotes and apostrophes
            text = re.sub(r'["""]', '"', text)
            text = re.sub(r'[''']', "'", text)
            
            # Strip leading/trailing whitespace
            text = text.strip()
            
            return text
            
        except Exception:
            return text
            
    def _extract_semantic_embedding(self, text: str) -> np.ndarray:
        """Extract semantic embedding using transformer model"""        try:
            if not self.model or not self.tokenizer:
                return np.array([])
                
            # Tokenize and encode
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                max_length=512, 
                truncation=True, 
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Extract features
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling of last hidden states
                embeddings = outputs.last_hidden_state.mean(dim=1)
                
            # Normalize and convert to numpy
            embedding = embeddings.cpu().numpy().flatten()
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            logger.warning(f"Semantic embedding extraction failed: {str(e)}")
            return np.array([])
            
    def _extract_tfidf_features(self, text: str) -> np.ndarray:
        """Extract TF-IDF features"""        try:
            # Fit and transform text
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text])
            
            return tfidf_matrix.toarray().flatten()
            
        except Exception as e:
            logger.warning(f"TF-IDF extraction failed: {str(e)}")
            return np.array([])
            
    def _compute_content_hash(self, text: str) -> str:
        """Compute content-based hash"""        try:
            # Normalize text for hashing
            normalized = text.lower()
            normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
            normalized = re.sub(r'\s+', ' ', normalized)  # Normalize whitespace
            
            # Create hash
            return hashlib.sha256(normalized.encode()).hexdigest()
            
        except Exception:
            return ""
            
    def _compute_structure_hash(self, text: str) -> str:
        """Compute structure-based hash (paragraphs, sentences, etc.)"""        try:
            # Extract structural features
            paragraphs = text.split('\n\n')
            sentences = sent_tokenize(text)
            
            # Count structural elements
            structure_info = [
                len(paragraphs),
                len(sentences),
                len(re.findall(r'[.!?]', text)),  # Sentence endings
                len(re.findall(r'[,;:]', text)),  # Punctuation
                text.count('\n'),  # Line breaks
                len(re.findall(r'\d+', text)),  # Numbers
                len(re.findall(r'[A-Z][a-z]*', text))  # Capitalized words
            ]
            
            # Create structure signature
            structure_str = ''.join(map(str, structure_info))
            
            return hashlib.md5(structure_str.encode()).hexdigest()
            
        except Exception:
            return ""
            
    def _extract_stylometric_features(self, text: str) -> Dict:
        """Extract stylometric features for authorship analysis"""        try:
            words = word_tokenize(text.lower())
            sentences = sent_tokenize(text)
            
            # Lexical features
            avg_word_length = np.mean([len(word) for word in words if word.isalpha()])
            avg_sentence_length = np.mean([len(word_tokenize(sent)) for sent in sentences])
            
            # Vocabulary richness
            unique_words = set(words)
            vocabulary_richness = len(unique_words) / len(words) if words else 0
            
            # Function word frequencies
            function_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
            function_word_freq = {fw: words.count(fw) / len(words) for fw in function_words}
            
            # Punctuation usage
            punctuation_freq = {p: text.count(p) / len(text) for p in string.punctuation}
            
            # Part-of-speech patterns (if spaCy is available)
            pos_patterns = {}
            if self.nlp:
                doc = self.nlp(text[:1000000])  # Limit for performance
                pos_counts = Counter([token.pos_ for token in doc])
                total_tokens = sum(pos_counts.values())
                pos_patterns = {pos: count / total_tokens for pos, count in pos_counts.items()}
            
            return {
                'avg_word_length': float(avg_word_length),
                'avg_sentence_length': float(avg_sentence_length),
                'vocabulary_richness': float(vocabulary_richness),
                'function_word_freq': function_word_freq,
                'punctuation_freq': punctuation_freq,
                'pos_patterns': pos_patterns
            }
            
        except Exception as e:
            logger.warning(f"Stylometric feature extraction failed: {str(e)}")
            return {}
            
    def _extract_ngram_signatures(self, text: str, max_n: int = 3) -> Dict:
        """Extract character and word n-gram signatures"""        try:
            words = word_tokenize(text.lower())
            
            # Character n-grams
            char_ngrams = {}
            for n in range(2, max_n + 1):
                ngrams = [text[i:i+n] for i in range(len(text)-n+1)]
                char_ngrams[f'char_{n}gram'] = dict(Counter(ngrams).most_common(20))
                
            # Word n-grams
            word_ngrams = {}
            for n in range(2, max_n + 1):
                if len(words) >= n:
                    ngrams = [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
                    word_ngrams[f'word_{n}gram'] = dict(Counter(ngrams).most_common(10))
                    
            return {**char_ngrams, **word_ngrams}
            
        except Exception as e:
            logger.warning(f"N-gram extraction failed: {str(e)}")
            return {}
            
    def _compute_readability_scores(self, text: str) -> Dict:
        """Compute readability and complexity scores"""        try:
            return {
                'flesch_reading_ease': flesch_reading_ease(text),
                'flesch_kincaid_grade': flesch_kincaid_grade(text),
                'sentence_count': len(sent_tokenize(text)),
                'avg_words_per_sentence': len(word_tokenize(text)) / max(len(sent_tokenize(text)), 1)
            }
            
        except Exception as e:
            logger.warning(f"Readability score computation failed: {str(e)}")
            return {}
            
    def _detect_language(self, text: str) -> str:
        """Detect text language"""        try:
            # Simple heuristic language detection
            # Count common English words
            english_words = set(['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'have', 'has', 'had'])
            words = set(word_tokenize(text.lower()))
            english_ratio = len(words.intersection(english_words)) / max(len(words), 1)
            
            if english_ratio > 0.1:
                return 'en'
            else:
                return 'unknown'
                
        except Exception:
            return 'unknown'
            
    def _calculate_confidence(self, text: str, word_count: int) -> float:
        """Calculate confidence score based on text quality"""        try:
            # Length factor
            length_score = min(1.0, word_count / 100.0)  # Up to 100 words
            
            # Vocabulary diversity
            words = word_tokenize(text.lower())
            unique_words = set(words)
            diversity_score = len(unique_words) / max(len(words), 1)
            
            # Sentence structure
            sentences = sent_tokenize(text)
            structure_score = min(1.0, len(sentences) / 10.0)  # Up to 10 sentences
            
            # Combined confidence
            confidence = (length_score * 0.4 + 
                         diversity_score * 0.4 + 
                         structure_score * 0.2)
            
            return max(0.1, min(1.0, confidence))
            
        except Exception:
            return 0.5
            
    def compare_fingerprints(self, fp1: TextFingerprint, fp2: TextFingerprint) -> float:
        """Compare two text fingerprints and return similarity score (0-1)"""        try:
            scores = []
            
            # 1. Content hash exact match
            if fp1.content_hash and fp2.content_hash:
                content_sim = 1.0 if fp1.content_hash == fp2.content_hash else 0.0
                scores.append(content_sim * 0.3)
                
            # 2. Semantic similarity
            if len(fp1.semantic_embedding) > 0 and len(fp2.semantic_embedding) > 0:
                semantic_sim = cosine_similarity([fp1.semantic_embedding], [fp2.semantic_embedding])[0][0]
                semantic_sim = max(0.0, semantic_sim)
                scores.append(semantic_sim * 0.4)
                
            # 3. TF-IDF similarity
            if len(fp1.tfidf_vector) > 0 and len(fp2.tfidf_vector) > 0:
                # Ensure same dimensionality
                min_len = min(len(fp1.tfidf_vector), len(fp2.tfidf_vector))
                tfidf_sim = cosine_similarity(
                    [fp1.tfidf_vector[:min_len]], 
                    [fp2.tfidf_vector[:min_len]]
                )[0][0]
                tfidf_sim = max(0.0, tfidf_sim)
                scores.append(tfidf_sim * 0.2)
                
            # 4. Stylometric similarity
            stylometric_sim = self._compare_stylometric_features(
                fp1.stylometric_features, fp2.stylometric_features
            )
            scores.append(stylometric_sim * 0.1)
            
            # Weighted average
            total_similarity = sum(scores) if scores else 0.0
            
            # Apply confidence weighting
            confidence_factor = (fp1.confidence_score + fp2.confidence_score) / 2
            
            return total_similarity * confidence_factor
            
        except Exception as e:
            logger.error(f"Error comparing text fingerprints: {str(e)}")
            return 0.0
            
    def _compare_stylometric_features(self, features1: Dict, features2: Dict) -> float:
        """Compare stylometric features"""        try:
            if not features1 or not features2:
                return 0.0
                
            similarities = []
            
            # Compare numerical features
            numerical_features = ['avg_word_length', 'avg_sentence_length', 'vocabulary_richness']
            
            for feature in numerical_features:
                if feature in features1 and feature in features2:
                    val1, val2 = features1[feature], features2[feature]
                    if val1 + val2 > 0:
                        sim = 1.0 - abs(val1 - val2) / (val1 + val2)
                        similarities.append(max(0.0, sim))
                        
            # Compare frequency distributions
            freq_features = ['function_word_freq', 'punctuation_freq']
            
            for feature in freq_features:
                if feature in features1 and feature in features2:
                    freq1, freq2 = features1[feature], features2[feature]
                    if freq1 and freq2:
                        # Calculate cosine similarity of frequency vectors
                        common_keys = set(freq1.keys()).intersection(set(freq2.keys()))
                        if common_keys:
                            vec1 = [freq1.get(key, 0) for key in common_keys]
                            vec2 = [freq2.get(key, 0) for key in common_keys]
                            
                            if sum(vec1) > 0 and sum(vec2) > 0:
                                sim = cosine_similarity([vec1], [vec2])[0][0]
                                similarities.append(max(0.0, sim))
                                
            return np.mean(similarities) if similarities else 0.0
            
        except Exception:
            return 0.0
            
    def detect_plagiarism(self, text1: str, text2: str, threshold: float = 0.8) -> Dict:
        """Detect potential plagiarism between two texts"""        try:
            fp1 = self.extract_fingerprint(text1)
            fp2 = self.extract_fingerprint(text2)
            
            similarity = self.compare_fingerprints(fp1, fp2)
            
            return {
                'similarity_score': similarity,
                'is_plagiarism': similarity >= threshold,
                'content_match': fp1.content_hash == fp2.content_hash,
                'structure_match': fp1.structure_hash == fp2.structure_hash,
                'details': {
                    'word_count_diff': abs(fp1.word_count - fp2.word_count),
                    'language_match': fp1.language == fp2.language,
                    'confidence': min(fp1.confidence_score, fp2.confidence_score)
                }
            }
            
        except Exception as e:
            logger.error(f"Error detecting plagiarism: {str(e)}")
            return {'similarity_score': 0.0, 'is_plagiarism': False}
            
    def batch_extract_fingerprints(self, texts: List[Tuple[str, str]]) -> Dict[str, TextFingerprint]:
        """Extract fingerprints from multiple texts"""        fingerprints = {}
        
        for text_id, text_content in texts:
            try:
                fp = self.extract_fingerprint(text_content)
                fingerprints[text_id] = fp
                logger.info(f"Successfully extracted fingerprint for text: {text_id}")
            except Exception as e:
                logger.error(f"Failed to extract fingerprint for text {text_id}: {str(e)}")
                
        return fingerprints
        
    def find_similar_texts(self, target_fingerprint: TextFingerprint,
                          candidate_fingerprints: Dict[str, TextFingerprint],
                          threshold: float = 0.8) -> List[Tuple[str, float]]:
        """Find similar texts above threshold"""        similar_texts = []
        
        for text_id, candidate_fp in candidate_fingerprints.items():
            similarity = self.compare_fingerprints(target_fingerprint, candidate_fp)
            
            if similarity >= threshold:
                similar_texts.append((text_id, similarity))
                
        # Sort by similarity score (descending)
        similar_texts.sort(key=lambda x: x[1], reverse=True)
        
        return similar_texts
