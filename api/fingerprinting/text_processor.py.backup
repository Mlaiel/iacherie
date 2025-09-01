"""IA Influencer Agent - Text Fingerprinting Processor
Author: Fahed Mlaiel <mlaiel@live.de>

AVERTISSEMENT LÉGAL STRICT:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée 
sans permission écrite expresse est strictement interdite et 
constituera une violation des droits d'auteur.

Advanced text fingerprinting processor for multi-format content protection
"""
import hashlib
import re
from typing import Dict, List, Optional, Tuple, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import logging
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import Counter
import textstat
import language_tool_python

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

logger = logging.getLogger(__name__)

@dataclass
class TextFingerprint:
    """Text fingerprint data structure"""
    content_hash: str
    semantic_hash: str
    style_features: np.ndarray
    linguistic_features: np.ndarray
    tfidf_features: np.ndarray
    readability_scores: Dict[str, float]
    language: str
    word_count: int
    character_count: int
    sentence_count: int
    paragraph_count: int
    metadata: Dict[str, Any]

class TextFingerprintProcessor:
    """
    Professional text fingerprinting processor with advanced NLP algorithms
    Handles multi-language text content protection and similarity detection
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize text fingerprinting processor"""
        self.config = config or self._get_default_config()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.lemmatizer = WordNetLemmatizer()
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        self.grammar_tool = None
        self._initialize_tools()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for text processing"""
        return {
            'similarity_threshold': 0.8,
            'max_text_length': 100000,
            'supported_languages': ['en', 'fr', 'de', 'es'],
            'min_words': 10
        }
    
    def _initialize_tools(self):
        """Initialize language processing tools"""
        try:
            self.grammar_tool = language_tool_python.LanguageTool('en-US')
        except Exception as e:
            logger.warning(f"Grammar tool initialization failed: {str(e)}")
    
    async def process_text_file(self, file_path: Path) -> TextFingerprint:
        """
        Process text file and generate comprehensive fingerprint
        
        Args:
            file_path: Path to text file
            
        Returns:
            TextFingerprint object with extracted features
        """
        try:
            # Load text file asynchronously
            loop = asyncio.get_event_loop()
            
            text_content = await loop.run_in_executor(
                self.executor,
                self._load_text_file,
                str(file_path)
            )
            
            # Process text content
            return await self.process_text_content(text_content, file_path)
            
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {str(e)}")
            raise
    
    async def process_text_content(self, text_content: str, file_path: Optional[Path] = None) -> TextFingerprint:
        """
        Process text content and generate comprehensive fingerprint
        
        Args:
            text_content: Raw text content
            file_path: Optional file path for metadata
            
        Returns:
            TextFingerprint object with extracted features
        """
        try:
            # Truncate if too long
            if len(text_content) > self.config['max_text_length']:
                text_content = text_content[:self.config['max_text_length']]
            
            # Generate content hash
            content_hash = self._generate_content_hash(text_content)
            
            # Process features in parallel
            loop = asyncio.get_event_loop()
            
            features = await asyncio.gather(
                self._extract_semantic_hash(text_content),
                self._extract_style_features(text_content),
                self._extract_linguistic_features(text_content),
                self._extract_tfidf_features(text_content),
                self._extract_readability_scores(text_content),
                self._detect_language(text_content)
            )
            
            semantic_hash, style_features, linguistic_features, tfidf_features, readability_scores, language = features
            
            # Get basic text statistics
            word_count = len(word_tokenize(text_content))
            character_count = len(text_content)
            sentence_count = len(sent_tokenize(text_content))
            paragraph_count = len([p for p in text_content.split('\n\n') if p.strip()])
            
            # Create fingerprint
            fingerprint = TextFingerprint(
                content_hash=content_hash,
                semantic_hash=semantic_hash,
                style_features=style_features,
                linguistic_features=linguistic_features,
                tfidf_features=tfidf_features,
                readability_scores=readability_scores,
                language=language,
                word_count=word_count,
                character_count=character_count,
                sentence_count=sentence_count,
                paragraph_count=paragraph_count,
                metadata=self._extract_metadata(file_path) if file_path else {}
            )
            
            logger.info(f"Text fingerprint generated for {'content' if not file_path else file_path.name}")
            return fingerprint
            
        except Exception as e:
            logger.error(f"Error processing text content: {str(e)}")
            raise
    
    def _load_text_file(self, file_path: str) -> str:
        """Load text file content"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
            
            # Fallback: read as binary and decode with errors='ignore'
            with open(file_path, 'rb') as file:
                return file.read().decode('utf-8', errors='ignore')
                
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {str(e)}")
            raise
    
    def _generate_content_hash(self, text_content: str) -> str:
        """Generate unique hash for text content"""
        text_bytes = text_content.encode('utf-8')
        return hashlib.sha256(text_bytes).hexdigest()
    
    async def _extract_semantic_hash(self, text_content: str) -> str:
        """Extract semantic hash based on normalized content"""
        loop = asyncio.get_event_loop()
        
        def compute_semantic():
            # Normalize text for semantic comparison
            normalized = self._normalize_text(text_content)
            
            # Remove stopwords and lemmatize
            words = word_tokenize(normalized.lower())
            stop_words = set(stopwords.words('english'))
            
            meaningful_words = []
            for word in words:
                if word.isalpha() and word not in stop_words and len(word) > 2:
                    lemmatized = self.lemmatizer.lemmatize(word)
                    meaningful_words.append(lemmatized)
            
            # Create semantic signature from most important words
            word_freq = Counter(meaningful_words)
            top_words = [word for word, _ in word_freq.most_common(50)]
            
            semantic_content = ' '.join(sorted(top_words))
            return hashlib.md5(semantic_content.encode('utf-8')).hexdigest()
        
        return await loop.run_in_executor(self.executor, compute_semantic)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation structure
        text = re.sub(r'[^\w\s.,!?;:()\-\'""]', '', text)
        
        return text.strip()
    
    async def _extract_style_features(self, text_content: str) -> np.ndarray:
        """Extract stylistic features from text"""
        loop = asyncio.get_event_loop()
        
        def compute_style():
            features = []
            
            # Character-level features
            features.append(len(text_content))  # Total characters
            features.append(text_content.count(' '))  # Spaces
            features.append(text_content.count('\n'))  # Line breaks
            features.append(text_content.count('\t'))  # Tabs
            
            # Punctuation features
            punctuation = '.,!?;:()[]{}"\'-'
            for punct in punctuation:
                features.append(text_content.count(punct))
            
            # Case features
            features.append(sum(1 for c in text_content if c.isupper()))  # Uppercase chars
            features.append(sum(1 for c in text_content if c.islower()))  # Lowercase chars
            features.append(sum(1 for c in text_content if c.isdigit()))  # Digits
            
            # Word length distribution
            words = word_tokenize(text_content)
            if words:
                word_lengths = [len(word) for word in words]
                features.extend([
                    np.mean(word_lengths),
                    np.std(word_lengths),
                    np.median(word_lengths),
                    max(word_lengths),
                    min(word_lengths)
                ])
            else:
                features.extend([0, 0, 0, 0, 0])
            
            # Sentence length distribution
            sentences = sent_tokenize(text_content)
            if sentences:
                sentence_lengths = [len(sent.split()) for sent in sentences]
                features.extend([
                    np.mean(sentence_lengths),
                    np.std(sentence_lengths),
                    np.median(sentence_lengths),
                    max(sentence_lengths),
                    min(sentence_lengths)
                ])
            else:
                features.extend([0, 0, 0, 0, 0])
            
            return np.array(features, dtype=float)
        
        return await loop.run_in_executor(self.executor, compute_style)
    
    async def _extract_linguistic_features(self, text_content: str) -> np.ndarray:
        """Extract linguistic features from text"""
        loop = asyncio.get_event_loop()
        
        def compute_linguistic():
            features = []
            
            # Lexical diversity
            words = word_tokenize(text_content.lower())
            unique_words = set(words)
            
            if len(words) > 0:
                lexical_diversity = len(unique_words) / len(words)
            else:
                lexical_diversity = 0
            
            features.append(lexical_diversity)
            
            # POS tag distribution (simplified)
            try:
                import nltk
                if 'averaged_perceptron_tagger' not in nltk.data.find('taggers/averaged_perceptron_tagger'):
                    nltk.download('averaged_perceptron_tagger')
                
                pos_tags = nltk.pos_tag(words[:1000])  # Limit for performance
                pos_counts = Counter([tag for _, tag in pos_tags])
                
                # Common POS categories
                common_pos = ['NN', 'NNS', 'NNP', 'VB', 'VBD', 'VBG', 'JJ', 'RB', 'IN', 'DT']
                for pos in common_pos:
                    features.append(pos_counts.get(pos, 0) / len(pos_tags) if pos_tags else 0)
                
            except Exception:
                # Fallback if POS tagging fails
                features.extend([0] * 10)
            
            # Function word ratios
            function_words = {
                'articles': ['a', 'an', 'the'],
                'prepositions': ['in', 'on', 'at', 'by', 'for', 'with', 'to', 'of', 'from'],
                'pronouns': ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her'],
                'conjunctions': ['and', 'or', 'but', 'so', 'yet', 'for', 'nor']
            }
            
            word_count = len(words)
            for category, word_list in function_words.items():
                count = sum(1 for word in words if word in word_list)
                features.append(count / word_count if word_count > 0 else 0)
            
            return np.array(features, dtype=float)
        
        return await loop.run_in_executor(self.executor, compute_linguistic)
    
    async def _extract_tfidf_features(self, text_content: str) -> np.ndarray:
        """Extract TF-IDF features from text"""
        loop = asyncio.get_event_loop()
        
        def compute_tfidf():
            try:
                # Fit and transform the text
                sentences = sent_tokenize(text_content)
                if len(sentences) < 2:
                    sentences = [text_content]
                
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(sentences)
                
                # Return average TF-IDF vector
                return tfidf_matrix.mean(axis=0).A1
                
            except Exception as e:
                logger.warning(f"TF-IDF extraction failed: {str(e)}")
                return np.zeros(1000)
        
        return await loop.run_in_executor(self.executor, compute_tfidf)
    
    async def _extract_readability_scores(self, text_content: str) -> Dict[str, float]:
        """Extract readability scores from text"""
        loop = asyncio.get_event_loop()
        
        def compute_readability():
            try:
                scores = {
                    'flesch_reading_ease': textstat.flesch_reading_ease(text_content),
                    'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text_content),
                    'gunning_fog': textstat.gunning_fog(text_content),
                    'smog_index': textstat.smog_index(text_content),
                    'automated_readability_index': textstat.automated_readability_index(text_content),
                    'coleman_liau_index': textstat.coleman_liau_index(text_content),
                    'linsear_write_formula': textstat.linsear_write_formula(text_content),
                    'dale_chall_readability_score': textstat.dale_chall_readability_score(text_content)
                }
                
                # Add grammar complexity score if tool is available
                if self.grammar_tool:
                    try:
                        matches = self.grammar_tool.check(text_content[:1000])  # Limit for performance
                        scores['grammar_error_rate'] = len(matches) / len(word_tokenize(text_content[:1000]))
                    except Exception:
                        scores['grammar_error_rate'] = 0.0
                else:
                    scores['grammar_error_rate'] = 0.0
                
                return scores
                
            except Exception as e:
                logger.warning(f"Readability analysis failed: {str(e)}")
                return {
                    'flesch_reading_ease': 0.0,
                    'flesch_kincaid_grade': 0.0,
                    'gunning_fog': 0.0,
                    'smog_index': 0.0,
                    'automated_readability_index': 0.0,
                    'coleman_liau_index': 0.0,
                    'linsear_write_formula': 0.0,
                    'dale_chall_readability_score': 0.0,
                    'grammar_error_rate': 0.0
                }
        
        return await loop.run_in_executor(self.executor, compute_readability)
    
    async def _detect_language(self, text_content: str) -> str:
        """Detect language of text content"""
        loop = asyncio.get_event_loop()
        
        def detect_lang():
            try:
                from langdetect import detect
                return detect(text_content)
            except Exception:
                # Fallback to simple heuristics
                if any(word in text_content.lower() for word in ['the', 'and', 'is', 'of', 'to']):
                    return 'en'
                elif any(word in text_content.lower() for word in ['le', 'la', 'et', 'de', 'un']):
                    return 'fr'
                elif any(word in text_content.lower() for word in ['der', 'die', 'das', 'und', 'ist']):
                    return 'de'
                else:
                    return 'unknown'
        
        return await loop.run_in_executor(self.executor, detect_lang)
    
    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract file metadata"""
        return {
            'filename': file_path.name,
            'file_size': file_path.stat().st_size,
            'created_at': file_path.stat().st_ctime,
            'modified_at': file_path.stat().st_mtime
        }
    
    def calculate_similarity(self, fp1: TextFingerprint, fp2: TextFingerprint) -> float:
        """
        Calculate similarity score between two text fingerprints
        
        Args:
            fp1: First text fingerprint
            fp2: Second text fingerprint
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Content hash exact match
            if fp1.content_hash == fp2.content_hash:
                return 1.0
            
            # Semantic hash similarity
            semantic_similarity = 1.0 if fp1.semantic_hash == fp2.semantic_hash else 0.0
            
            # Style features similarity
            style_similarity = self._cosine_similarity(fp1.style_features, fp2.style_features)
            
            # Linguistic features similarity
            linguistic_similarity = self._cosine_similarity(fp1.linguistic_features, fp2.linguistic_features)
            
            # TF-IDF similarity
            if len(fp1.tfidf_features) == len(fp2.tfidf_features):
                tfidf_similarity = cosine_similarity(
                    fp1.tfidf_features.reshape(1, -1),
                    fp2.tfidf_features.reshape(1, -1)
                )[0][0]
            else:
                tfidf_similarity = 0.0
            
            # Readability similarity
            readability_similarity = self._readability_similarity(
                fp1.readability_scores,
                fp2.readability_scores
            )
            
            # Language similarity
            language_similarity = 1.0 if fp1.language == fp2.language else 0.0
            
            # Length similarity
            length_diff = abs(fp1.word_count - fp2.word_count) / max(fp1.word_count, fp2.word_count, 1)
            length_similarity = 1.0 - min(length_diff, 1.0)
            
            # Weighted average
            weights = {
                'semantic': 0.3,
                'tfidf': 0.25,
                'style': 0.2,
                'linguistic': 0.1,
                'readability': 0.08,
                'language': 0.05,
                'length': 0.02
            }
            
            similarity = (
                weights['semantic'] * semantic_similarity +
                weights['tfidf'] * tfidf_similarity +
                weights['style'] * style_similarity +
                weights['linguistic'] * linguistic_similarity +
                weights['readability'] * readability_similarity +
                weights['language'] * language_similarity +
                weights['length'] * length_similarity
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            if len(vec1) != len(vec2):
                return 0.0
            
            # Handle zero vectors
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = np.dot(vec1, vec2) / (norm1 * norm2)
            return float(np.clip(similarity, 0.0, 1.0))
            
        except Exception:
            return 0.0
    
    def _readability_similarity(self, scores1: Dict[str, float], scores2: Dict[str, float]) -> float:
        """Calculate similarity between readability scores"""
        try:
            similarities = []
            
            for key in scores1.keys():
                if key in scores2:
                    val1, val2 = scores1[key], scores2[key]
                    if val1 == 0 and val2 == 0:
                        similarities.append(1.0)
                    elif max(abs(val1), abs(val2)) == 0:
                        similarities.append(1.0)
                    else:
                        diff = abs(val1 - val2) / max(abs(val1), abs(val2))
                        similarities.append(1.0 - min(diff, 1.0))
            
            return np.mean(similarities) if similarities else 0.0
            
        except Exception:
            return 0.0
    
    def is_duplicate(self, fp1: TextFingerprint, fp2: TextFingerprint) -> bool:
        """Check if two fingerprints represent duplicate content"""
        similarity = self.calculate_similarity(fp1, fp2)
        return similarity >= self.config['similarity_threshold']
    
    async def batch_process_files(self, file_paths: List[Path]) -> List[TextFingerprint]:
        """Process multiple text files in parallel"""
        tasks = [self.process_text_file(path) for path in file_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def batch_process_content(self, text_contents: List[str]) -> List[TextFingerprint]:
        """Process multiple text contents in parallel"""
        tasks = [self.process_text_content(content) for content in text_contents]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
        if hasattr(self, 'grammar_tool') and self.grammar_tool:
            self.grammar_tool.close()
