"""Advanced Text Fingerprinting Engine
Text fingerprinting with BERT embeddings, semantic similarity, and plagiarism detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import numpy as np
import hashlib
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

# Text processing
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
import string

# ML and NLP
import torch
from transformers import AutoTokenizer, AutoModel, pipeline
from sentence_transformers import SentenceTransformer
import spacy

# Text statistics
import textstat
from textblob import TextBlob

from ...core.logging import logger
from ...config import settings


# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass


@dataclass
class TextFingerprint:
    """
Text fingerprint data structure"""
    file_id: str
    bert_embedding: List[float]
    sentence_embeddings: List[List[float]]
    semantic_features: Dict[str, Any]
    linguistic_features: Dict[str, Any]
    stylometric_features: Dict[str, Any]
    statistical_features: Dict[str, Any]
    content_features: Dict[str, Any]
    similarity_hashes: Dict[str, str]
    language_features: Dict[str, Any]
    confidence_score: float
    created_at: datetime


class TextFingerprintEngine:
    """
    Advanced text fingerprinting engine supporting:
    - BERT embeddings for semantic similarity
    - Sentence-level embeddings
    - Linguistic feature analysis
    - Stylometric analysis (writing style)
    - Statistical text features
    - Content-based features
    - Language detection
    - Plagiarism detection capabilities
    """
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize models
        self.bert_model = None
        self.bert_tokenizer = None
        self.sentence_model = None
        self.nlp = None
        
        # Initialize NLP tools
        self._init_models()
        
        # Text processing tools
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        logger.info(f"TextFingerprintEngine initialized on {self.device}")
    
    def _init_models(self):
        """Initialize NLP models"""
        try:
            # BERT model for embeddings
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.sentence_model = SentenceTransformer(model_name, device=self.device)
            
            # Alternative BERT model
            self.bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            self.bert_model = AutoModel.from_pretrained("bert-base-uncased").to(self.device)
            self.bert_model.eval()
            
            logger.info("NLP models loaded successfully")
            
        except Exception as e:
            logger.warning(f"Could not load some NLP models: {str(e)}")
        
        try:
            # SpaCy for linguistic analysis
            self.nlp = spacy.load("en_core_web_sm")
            
        except Exception as e:
            logger.warning(f"Could not load SpaCy model: {str(e)}")
    
    async def generate_fingerprint(self, text_content: str, metadata: Optional[Dict] = None) -> TextFingerprint:
        """
        Generate comprehensive text fingerprint
        
        Args:
            text_content: Text content to fingerprint
            metadata: Optional metadata about the text
            
        Returns:
            TextFingerprint: Complete fingerprint data
        """
        try:
            logger.info(f"Generating text fingerprint for {len(text_content)} characters")
            
            # Clean and preprocess text
            cleaned_text = await self._preprocess_text(text_content)
            
            # Generate file ID
            file_id = await self._generate_file_id(text_content)
            
            # Parallel fingerprint generation
            fingerprint_tasks = [
                self._generate_bert_embedding(cleaned_text),
                self._generate_sentence_embeddings(cleaned_text),
                self._extract_semantic_features(cleaned_text),
                self._extract_linguistic_features(cleaned_text),
                self._extract_stylometric_features(cleaned_text),
                self._extract_statistical_features(cleaned_text),
                self._extract_content_features(cleaned_text),
                self._generate_similarity_hashes(cleaned_text),
                self._extract_language_features(cleaned_text)
            ]
            
            results = await asyncio.gather(*fingerprint_tasks)
            
            # Unpack results
            bert_embedding, sentence_embeddings, semantic_features, linguistic_features, \
            stylometric_features, statistical_features, content_features, similarity_hashes, \
            language_features = results
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(results)
            
            fingerprint = TextFingerprint(
                file_id=file_id,
                bert_embedding=bert_embedding,
                sentence_embeddings=sentence_embeddings,
                semantic_features=semantic_features,
                linguistic_features=linguistic_features,
                stylometric_features=stylometric_features,
                statistical_features=statistical_features,
                content_features=content_features,
                similarity_hashes=similarity_hashes,
                language_features=language_features,
                confidence_score=confidence_score,
                created_at=datetime.utcnow()
            )
            
            logger.info(f"Text fingerprint generated successfully. Confidence: {confidence_score:.3f}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error generating text fingerprint: {str(e)}")
            raise
    
    async def _generate_file_id(self, text_content: str) -> str:
        """Generate unique file ID"""
        content_hash = hashlib.sha256(text_content.encode('utf-8')).hexdigest()
        return f"text_{content_hash[:16]}"
    
    async def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\?\!\,\;\:\'\"]', '', text)
        
        return text
    
    async def _generate_bert_embedding(self, text: str) -> List[float]:
        """Generate BERT embedding for the entire text"""
        try:
            if self.sentence_model is None:
                return []
            
            # Use sentence transformer for text embedding
            embedding = self.sentence_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating BERT embedding: {str(e)}")
            return []
    
    async def _generate_sentence_embeddings(self, text: str) -> List[List[float]]:
        """Generate embeddings for individual sentences"""
        try:
            if self.sentence_model is None:
                return []
            
            # Split into sentences
            sentences = sent_tokenize(text)
            
            # Limit number of sentences for efficiency
            sentences = sentences[:50]
            
            # Generate embeddings for each sentence
            sentence_embeddings = []
            for sentence in sentences:
                if len(sentence.strip()) > 10:  # Skip very short sentences
                    embedding = self.sentence_model.encode(sentence, convert_to_numpy=True)
                    sentence_embeddings.append(embedding.tolist())
            
            return sentence_embeddings
            
        except Exception as e:
            logger.error(f"Error generating sentence embeddings: {str(e)}")
            return []
    
    async def _extract_semantic_features(self, text: str) -> Dict[str, Any]:
        """Extract semantic features using NLP analysis"""
        try:
            semantic_features = {}
            
            # TextBlob analysis
            blob = TextBlob(text)
            
            # Sentiment analysis
            semantic_features['sentiment'] = {
                'polarity': float(blob.sentiment.polarity),
                'subjectivity': float(blob.sentiment.subjectivity)
            }
            
            # Noun phrases (key concepts)
            noun_phrases = list(blob.noun_phrases)[:20]  # Limit to top 20
            semantic_features['key_concepts'] = noun_phrases
            
            # SpaCy analysis if available
            if self.nlp:
                doc = self.nlp(text[:1000000])  # Limit text length for efficiency
                
                # Named entities
                entities = [(ent.text, ent.label_) for ent in doc.ents][:30]
                semantic_features['named_entities'] = entities
                
                # Dependency parsing features
                pos_tags = [token.pos_ for token in doc]
                semantic_features['pos_distribution'] = {
                    pos: pos_tags.count(pos) for pos in set(pos_tags)
                }
                
                # Semantic similarity concepts
                semantic_features['entity_types'] = list(set([ent.label_ for ent in doc.ents]))
            
            return semantic_features
            
        except Exception as e:
            logger.error(f"Error extracting semantic features: {str(e)}")
            return {}
    
    async def _extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        """Extract linguistic features"""
        try:
            linguistic_features = {}
            
            # Basic tokenization
            words = word_tokenize(text.lower())
            sentences = sent_tokenize(text)
            
            # Vocabulary analysis
            unique_words = set(words)
            linguistic_features['vocabulary'] = {
                'total_words': len(words),
                'unique_words': len(unique_words),
                'vocabulary_richness': len(unique_words) / len(words) if words else 0,
                'type_token_ratio': len(unique_words) / len(words) if words else 0
            }
            
            # Word length analysis
            word_lengths = [len(word) for word in words if word.isalpha()]
            if word_lengths:
                linguistic_features['word_length'] = {
                    'mean': float(np.mean(word_lengths)),
                    'std': float(np.std(word_lengths)),
                    'max': int(np.max(word_lengths)),
                    'min': int(np.min(word_lengths))
                }
            
            # Sentence analysis
            sentence_lengths = [len(word_tokenize(sent)) for sent in sentences]
            if sentence_lengths:
                linguistic_features['sentence_length'] = {
                    'mean': float(np.mean(sentence_lengths)),
                    'std': float(np.std(sentence_lengths)),
                    'max': int(np.max(sentence_lengths)),
                    'min': int(np.min(sentence_lengths))
                }
            
            # Function words analysis (stylometric indicator)
            function_words = ['the', 'and', 'of', 'to', 'a', 'in', 'is', 'it', 'you', 'that']
            function_word_counts = {word: words.count(word) for word in function_words}
            linguistic_features['function_words'] = function_word_counts
            
            # Punctuation analysis
            punctuation_counts = {char: text.count(char) for char in string.punctuation}
            linguistic_features['punctuation'] = punctuation_counts
            
            return linguistic_features
            
        except Exception as e:
            logger.error(f"Error extracting linguistic features: {str(e)}")
            return {}
    
    async def _extract_stylometric_features(self, text: str) -> Dict[str, Any]:
        """Extract stylometric features (writing style indicators)"""
        try:
            stylometric_features = {}
            
            words = word_tokenize(text.lower())
            sentences = sent_tokenize(text)
            
            # Readability measures
            stylometric_features['readability'] = {
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'smog_index': textstat.smog_index(text),
                'coleman_liau_index': textstat.coleman_liau_index(text),
                'automated_readability_index': textstat.automated_readability_index(text)
            }
            
            # Lexical diversity
            stylometric_features['lexical_diversity'] = {
                'lexical_diversity': textstat.lexical_diversity(text),
                'difficult_words': textstat.difficult_words(text),
                'linsear_write_formula': textstat.linsear_write_formula(text)
            }
            
            # Character-level features
            char_counts = {
                'uppercase': sum(1 for c in text if c.isupper()),
                'lowercase': sum(1 for c in text if c.islower()),
                'digits': sum(1 for c in text if c.isdigit()),
                'spaces': sum(1 for c in text if c.isspace()),
                'punctuation': sum(1 for c in text if c in string.punctuation)
            }
            stylometric_features['character_distribution'] = char_counts
            
            # Stylistic patterns
            stylometric_features['style_patterns'] = {
                'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0,
                'avg_chars_per_word': len(text) / len(words) if words else 0,
                'sentences_per_paragraph': len(sentences) / max(1, text.count('\n\n') + 1),
                'exclamation_ratio': text.count('!') / len(sentences) if sentences else 0,
                'question_ratio': text.count('?') / len(sentences) if sentences else 0
            }
            
            return stylometric_features
            
        except Exception as e:
            logger.error(f"Error extracting stylometric features: {str(e)}")
            return {}
    
    async def _extract_statistical_features(self, text: str) -> Dict[str, Any]:
        """Extract statistical features"""
        try:
            statistical_features = {}
            
            # Basic statistics
            statistical_features['basic_stats'] = {
                'character_count': len(text),
                'word_count': len(word_tokenize(text)),
                'sentence_count': len(sent_tokenize(text)),
                'paragraph_count': len(text.split('\n\n')),
                'line_count': len(text.split('\n'))
            }
            
            # Character frequency analysis
            char_freq = {}
            for char in text.lower():
                if char.isalpha():
                    char_freq[char] = char_freq.get(char, 0) + 1
            
            # Normalize frequencies
            total_chars = sum(char_freq.values())
            if total_chars > 0:
                char_freq_norm = {char: count/total_chars for char, count in char_freq.items()}
                statistical_features['character_frequency'] = char_freq_norm
            
            # Word frequency analysis (top 20 words)
            words = [word.lower() for word in word_tokenize(text) if word.isalpha()]
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Top frequent words
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
            statistical_features['top_words'] = dict(top_words)
            
            # N-gram analysis (bigrams and trigrams)
            if len(words) > 1:
                bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
                bigram_freq = {}
                for bigram in bigrams:
                    bigram_freq[bigram] = bigram_freq.get(bigram, 0) + 1
                
                top_bigrams = sorted(bigram_freq.items(), key=lambda x: x[1], reverse=True)[:10]
                statistical_features['top_bigrams'] = dict(top_bigrams)
            
            return statistical_features
            
        except Exception as e:
            logger.error(f"Error extracting statistical features: {str(e)}")
            return {}
    
    async def _extract_content_features(self, text: str) -> Dict[str, Any]:
        """Extract content-based features"""
        try:
            content_features = {}
            
            # Content type detection
            content_features['content_type'] = await self._detect_content_type(text)
            
            # Topic modeling indicators (simplified)
            words = [word.lower() for word in word_tokenize(text) if word.isalpha() and word not in self.stop_words]
            
            # Keyword density analysis
            if words:
                word_freq = {}
                for word in words:
                    word_freq[word] = word_freq.get(word, 0) + 1
                
                # Calculate keyword density
                total_words = len(words)
                keyword_density = {word: count/total_words for word, count in word_freq.items()}
                
                # Top keywords
                top_keywords = sorted(keyword_density.items(), key=lambda x: x[1], reverse=True)[:15]
                content_features['keyword_density'] = dict(top_keywords)
            
            # Content structure
            content_features['structure'] = {
                'has_headers': bool(re.search(r'^#+ ', text, re.MULTILINE)),
                'has_lists': bool(re.search(r'^\s*[-*+]\s', text, re.MULTILINE)),
                'has_numbers': bool(re.search(r'\d+', text)),
                'has_urls': bool(re.search(r'https?://\S+', text)),
                'has_emails': bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
            }
            
            return content_features
            
        except Exception as e:
            logger.error(f"Error extracting content features: {str(e)}")
            return {}
    
    async def _detect_content_type(self, text: str) -> str:
        """Detect the type of content (academic, news, social media, etc.)"""
        try:
            # Simple heuristic-based content type detection
            text_lower = text.lower()
            
            # Academic indicators
            academic_words = ['abstract', 'methodology', 'conclusion', 'references', 'hypothesis']
            academic_score = sum(1 for word in academic_words if word in text_lower)
            
            # News indicators
            news_words = ['breaking', 'reported', 'according to', 'sources', 'interview']
            news_score = sum(1 for word in news_words if word in text_lower)
            
            # Social media indicators
            social_words = ['#', '@', 'lol', 'omg', 'follow', 'like', 'share']
            social_score = sum(1 for word in social_words if word in text_lower)
            
            # Blog/informal indicators
            blog_words = ['i think', 'in my opinion', 'personally', 'believe', 'feel']
            blog_score = sum(1 for word in blog_words if word in text_lower)
            
            scores = {
                'academic': academic_score,
                'news': news_score,
                'social_media': social_score,
                'blog': blog_score
            }
            
            return max(scores, key=scores.get) if max(scores.values()) > 0 else 'general'
            
        except Exception as e:
            logger.error(f"Error detecting content type: {str(e)}")
            return 'unknown'
    
    async def _generate_similarity_hashes(self, text: str) -> Dict[str, str]:
        """Generate various hashes for similarity detection"""
        try:
            hashes = {}
            
            # Simple content hash
            hashes['content_hash'] = hashlib.md5(text.encode('utf-8')).hexdigest()
            
            # Normalized content hash (remove spaces and punctuation)
            normalized_text = re.sub(r'[^\w]', '', text.lower())
            hashes['normalized_hash'] = hashlib.md5(normalized_text.encode('utf-8')).hexdigest()
            
            # Word-based hash (sorted words)
            words = sorted([word.lower() for word in word_tokenize(text) if word.isalpha()])
            word_text = ' '.join(words)
            hashes['word_hash'] = hashlib.md5(word_text.encode('utf-8')).hexdigest()
            
            # Stemmed hash
            stemmed_words = [self.stemmer.stem(word.lower()) for word in word_tokenize(text) if word.isalpha()]
            stemmed_text = ' '.join(sorted(stemmed_words))
            hashes['stemmed_hash'] = hashlib.md5(stemmed_text.encode('utf-8')).hexdigest()
            
            # Shingle hash (for near-duplicate detection)
            shingles = await self._generate_shingles(text, k=5)
            shingle_text = ' '.join(sorted(shingles))
            hashes['shingle_hash'] = hashlib.md5(shingle_text.encode('utf-8')).hexdigest()
            
            return hashes
            
        except Exception as e:
            logger.error(f"Error generating similarity hashes: {str(e)}")
            return {}
    
    async def _generate_shingles(self, text: str, k: int = 5) -> List[str]:
        """Generate k-shingles (k-grams of words) for similarity detection"""
        try:
            words = [word.lower() for word in word_tokenize(text) if word.isalpha()]
            shingles = []
            
            for i in range(len(words) - k + 1):
                shingle = ' '.join(words[i:i+k])
                shingles.append(shingle)
            
            return list(set(shingles))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error generating shingles: {str(e)}")
            return []
    
    async def _extract_language_features(self, text: str) -> Dict[str, Any]:
        """Extract language-specific features"""
        try:
            language_features = {}
            
            # Simple language detection using character patterns
            language_features['detected_language'] = await self._detect_language(text)
            
            # Language-specific statistics
            # English-specific features
            english_words = set(['the', 'and', 'of', 'to', 'a', 'in', 'is', 'it', 'you', 'that', 'he', 'was', 'for', 'on', 'are'])
            words = [word.lower() for word in word_tokenize(text) if word.isalpha()]
            english_word_count = sum(1 for word in words if word in english_words)
            language_features['english_indicator'] = english_word_count / len(words) if words else 0
            
            # Character set analysis
            char_sets = {
                'latin': sum(1 for c in text if ord(c) < 256),
                'extended': sum(1 for c in text if 256 <= ord(c) < 1024),
                'unicode': sum(1 for c in text if ord(c) >= 1024)
            }
            total_chars = sum(char_sets.values())
            if total_chars > 0:
                language_features['character_sets'] = {k: v/total_chars for k, v in char_sets.items()}
            
            return language_features
            
        except Exception as e:
            logger.error(f"Error extracting language features: {str(e)}")
            return {}
    
    async def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        try:
            # Very simple heuristic-based language detection
            # In production, use proper language detection library like langdetect
            
            text_sample = text[:1000].lower()
            
            # English indicators
            english_words = ['the', 'and', 'of', 'to', 'a', 'in', 'is', 'it', 'you', 'that']
            english_score = sum(1 for word in english_words if word in text_sample)
            
            # French indicators
            french_words = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir']
            french_score = sum(1 for word in french_words if word in text_sample)
            
            # German indicators
            german_words = ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich']
            german_score = sum(1 for word in german_words if word in text_sample)
            
            # Spanish indicators
            spanish_words = ['el', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no']
            spanish_score = sum(1 for word in spanish_words if word in text_sample)
            
            scores = {
                'english': english_score,
                'french': french_score,
                'german': german_score,
                'spanish': spanish_score
            }
            
            detected = max(scores, key=scores.get) if max(scores.values()) > 0 else 'unknown'
            return detected
            
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return 'unknown'
    
    async def _calculate_confidence_score(self, results: List[Any]) -> float:
        """Calculate overall confidence score"""
        try:
            confidence_factors = []
            
            # BERT embedding quality
            bert_embedding = results[0]
            if bert_embedding and len(bert_embedding) > 0:
                confidence_factors.append(0.95)
            else:
                confidence_factors.append(0.3)
            
            # Sentence embeddings quality
            sentence_embeddings = results[1]
            if sentence_embeddings and len(sentence_embeddings) > 0:
                confidence_factors.append(0.9)
            else:
                confidence_factors.append(0.4)
            
            # Semantic features quality
            semantic_features = results[2]
            if semantic_features and len(semantic_features) > 0:
                confidence_factors.append(0.85)
            else:
                confidence_factors.append(0.5)
            
            # Linguistic features quality
            linguistic_features = results[3]
            if linguistic_features and len(linguistic_features) > 0:
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.6)
            
            return float(np.mean(confidence_factors))
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {str(e)}")
            return 0.5
    
    async def compare_fingerprints(self, fp1: TextFingerprint, fp2: TextFingerprint) -> float:
        """
        Compare two text fingerprints and return similarity score (0-1)
        
        Args:
            fp1: First fingerprint
            fp2: Second fingerprint
            
        Returns:
            float: Similarity score between 0 and 1
        """
        try:
            similarities = []
            
            # Compare BERT embeddings (semantic similarity)
            if fp1.bert_embedding and fp2.bert_embedding:
                bert_similarity = await self._compare_embeddings(fp1.bert_embedding, fp2.bert_embedding)
                similarities.append(bert_similarity)
            
            # Compare sentence embeddings
            if fp1.sentence_embeddings and fp2.sentence_embeddings:
                sentence_similarity = await self._compare_sentence_embeddings(fp1.sentence_embeddings, fp2.sentence_embeddings)
                similarities.append(sentence_similarity)
            
            # Compare similarity hashes
            if fp1.similarity_hashes and fp2.similarity_hashes:
                hash_similarity = await self._compare_similarity_hashes(fp1.similarity_hashes, fp2.similarity_hashes)
                similarities.append(hash_similarity)
            
            # Compare stylometric features
            if fp1.stylometric_features and fp2.stylometric_features:
                style_similarity = await self._compare_stylometric_features(fp1.stylometric_features, fp2.stylometric_features)
                similarities.append(style_similarity)
            
            # Weighted average (semantic similarity has highest weight)
            weights = [0.4, 0.3, 0.2, 0.1]
            similarity_score = sum(s * w for s, w in zip(similarities, weights[:len(similarities)]))
            
            return min(1.0, max(0.0, similarity_score))
            
        except Exception as e:
            logger.error(f"Error comparing text fingerprints: {str(e)}")
            return 0.0
    
    async def _compare_embeddings(self, emb1: List[float], emb2: List[float]) -> float:
        """Compare embeddings using cosine similarity"""
        try:
            if not emb1 or not emb2:
                return 0.0
            
            vec1 = np.array(emb1)
            vec2 = np.array(emb2)
            
            cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            similarity = (cosine_sim + 1) / 2  # Convert to 0-1 range
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error comparing embeddings: {str(e)}")
            return 0.0
    
    async def _compare_sentence_embeddings(self, emb1: List[List[float]], emb2: List[List[float]]) -> float:
        """Compare sentence embeddings"""
        try:
            if not emb1 or not emb2:
                return 0.0
            
            # Calculate pairwise similarities between sentences
            similarities = []
            
            for sent1_emb in emb1[:10]:  # Limit for efficiency
                for sent2_emb in emb2[:10]:
                    sim = await self._compare_embeddings(sent1_emb, sent2_emb)
                    similarities.append(sim)
            
            # Return average similarity
            return float(np.mean(similarities)) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Error comparing sentence embeddings: {str(e)}")
            return 0.0
    
    async def _compare_similarity_hashes(self, hashes1: Dict[str, str], hashes2: Dict[str, str]) -> float:
        """Compare similarity hashes"""
        try:
            matches = 0
            total = 0
            
            for hash_type in ['content_hash', 'normalized_hash', 'word_hash', 'stemmed_hash', 'shingle_hash']:
                if hash_type in hashes1 and hash_type in hashes2:
                    total += 1
                    if hashes1[hash_type] == hashes2[hash_type]:
                        matches += 1
            
            return matches / total if total > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error comparing similarity hashes: {str(e)}")
            return 0.0
    
    async def _compare_stylometric_features(self, style1: Dict[str, Any], style2: Dict[str, Any]) -> float:
        """Compare stylometric features"""
        try:
            similarities = []
            
            # Compare readability scores
            if 'readability' in style1 and 'readability' in style2:
                readability_sim = await self._compare_numerical_features(style1['readability'], style2['readability'])
                similarities.append(readability_sim)
            
            # Compare style patterns
            if 'style_patterns' in style1 and 'style_patterns' in style2:
                pattern_sim = await self._compare_numerical_features(style1['style_patterns'], style2['style_patterns'])
                similarities.append(pattern_sim)
            
            return float(np.mean(similarities)) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Error comparing stylometric features: {str(e)}")
            return 0.0
    
    async def _compare_numerical_features(self, features1: Dict[str, Any], features2: Dict[str, Any]) -> float:
        """Compare numerical feature dictionaries"""
        try:
            similarities = []
            
            for key in features1:
                if key in features2:
                    val1, val2 = features1[key], features2[key]
                    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                        # Normalize difference
                        max_val = max(abs(val1), abs(val2), 1)
                        diff = abs(val1 - val2) / max_val
                        similarity = max(0, 1 - diff)
                        similarities.append(similarity)
            
            return float(np.mean(similarities)) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Error comparing numerical features: {str(e)}")
            return 0.0