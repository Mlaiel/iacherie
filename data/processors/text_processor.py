"""Text Processor Module
====================

Enterprise-grade text processing for content creators and influencers.
Handles text analysis, fingerprinting, enhancement, and transformation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  COPYRIGHT WARNING ⚠️
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or theft of this code or concept without explicit 
written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and 
will result in immediate legal action under German and international copyright law.

Features:
- Professional text analysis and NLP processing
- Text fingerprinting and plagiarism detection
- Content enhancement and optimization
- Multi-language text processing and translation
- Sentiment analysis and emotion detection
- SEO optimization and keyword extraction
- Batch processing for large text collections
"""import asyncio
import logging
import re
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
import unicodedata
from collections import Counter

# NLP libraries
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.tag import pos_tag
    from nltk.chunk import ne_chunk
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
    
    # Download required NLTK data
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('maxent_ne_chunker', quiet=True)
    nltk.download('words', quiet=True)
    nltk.download('wordnet', quiet=True)
    
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available - standard NLP features will be limited")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available - professional NLP features will be limited")

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available - AI features will be limited")

try:
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.warning("Language detection not available")

try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
    logging.warning("Text statistics not available")

logger = logging.getLogger(__name__)

@dataclass
class TextMetadata:
    """Text metadata container"""    char_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    language: str
    encoding: str = 'utf-8'
    readability_score: Optional[float] = None
    complexity_score: Optional[float] = None

@dataclass
class SentimentAnalysis:
    """Sentiment analysis results"""    compound_score: float
    positive_score: float
    negative_score: float
    neutral_score: float
    emotion_scores: Dict[str, float] = field(default_factory=dict)
    overall_sentiment: str = 'neutral'
    confidence: float = 0.0

@dataclass
class TextFeatures:
    """Text feature extraction results"""    keywords: List[Tuple[str, float]]
    entities: List[Tuple[str, str]]  # (entity, type)
    topics: List[Tuple[str, float]]
    pos_tags: List[Tuple[str, str]]
    ngrams: Dict[str, List[Tuple[str, int]]]
    semantic_similarity: Optional[float] = None
    text_quality_score: Optional[float] = None

@dataclass
class SEOAnalysis:
    """SEO optimization analysis"""    keyword_density: Dict[str, float]
    title_suggestions: List[str]
    meta_description: str
    readability_improvements: List[str]
    content_structure_score: float
    seo_score: float
    target_keywords: List[str]

@dataclass
class TextFingerprint:
    """Text fingerprint for plagiarism detection"""    content_hash: str
    semantic_hash: str
    structural_hash: str
    ngram_hashes: Dict[str, str]
    sentence_hashes: List[str]
    combined_hash: str

class TextProcessor:
    """Professional text processing and NLP engine"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize NLP engines
        self._initialize_engines()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default text processing configuration"""        return {
            'language': 'auto',
            'sentiment_analysis': True,
            'entity_recognition': True,
            'keyword_extraction': True,
            'seo_analysis': True,
            'plagiarism_detection': True,
            'quality_assessment': True,
            'readability_analysis': True,
            'topic_modeling': False,  # Computationally expensive
            'translation': False,
            'max_length': 100000,
            'min_word_length': 2,
            'stop_words_removal': True,
            'lemmatization': True,
            'ngram_range': (1, 3),
            'top_keywords': 20,
            'similarity_threshold': 0.8
        }
    
    def _initialize_engines(self):
        """Initialize text processing engines"""        try:
            # Initialize NLTK tools
            if NLTK_AVAILABLE:
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
                self.lemmatizer = WordNetLemmatizer()
                
                # Initialize stopwords for multiple languages
                self.stop_words = {
                    'en': set(stopwords.words('english')),
                    'de': set(stopwords.words('german')),
                    'fr': set(stopwords.words('french')),
                    'es': set(stopwords.words('spanish')),
                    'it': set(stopwords.words('italian'))
                }
                
                self.logger.info("NLTK engines initialized")
            
            # Initialize spaCy models
            if SPACY_AVAILABLE:
                try:
                    self.nlp_models = {}
                    # Try to load common models
                    model_names = ['en_core_web_sm', 'de_core_news_sm', 'fr_core_news_sm']
                    for model_name in model_names:
                        try:
                            self.nlp_models[model_name[:2]] = spacy.load(model_name)
                        except OSError:
                            self.logger.warning(f"spaCy model {model_name} not found")
                    
                    if self.nlp_models:
                        self.logger.info(f"Loaded {len(self.nlp_models)} spaCy models")
                except Exception as e:
                    self.logger.warning(f"spaCy initialization failed: {str(e)}")
            
            # Initialize Transformers models
            if TRANSFORMERS_AVAILABLE:
                try:
                    # Initialize sentiment analysis pipeline
                    self.transformers_sentiment = pipeline(
                        "sentiment-analysis",
                        model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                        return_all_scores=True
                    )
                    
                    # Initialize text generation pipeline
                    self.text_generator = pipeline(
                        "text-generation",
                        model="gpt2",
                        max_length=50
                    )
                    
                    self.logger.info("Transformers models initialized")
                except Exception as e:
                    self.logger.warning(f"Transformers initialization failed: {str(e)}")
            
            self.logger.info("Text processor engines initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing text engines: {str(e)}")
            raise
    
    async def process(
        self,
        text_data: Union[str, bytes],
        format_hint: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Main text processing pipeline
        
        Args:
            text_data: Text data as string or bytes
            format_hint: Optional format hint for processing
            config: Optional processing configuration override
        
        Returns:
            Dict containing processed text data and analysis results
        """        try:
            # Merge configuration
            processing_config = self.config.copy()
            if config:
                processing_config.update(config)
            
            # Prepare text
            text_content = await self._prepare_text(text_data, format_hint)
            
            # Extract metadata
            metadata = await self._extract_metadata(text_content)
            
            # Process text in parallel
            tasks = []
            
            if processing_config.get('sentiment_analysis', True):
                tasks.append(self._analyze_sentiment(text_content))
            
            if processing_config.get('keyword_extraction', True):
                tasks.append(self._extract_features(text_content, metadata))
            
            if processing_config.get('seo_analysis', True):
                tasks.append(self._analyze_seo(text_content, metadata))
            
            if processing_config.get('plagiarism_detection', True):
                tasks.append(self._generate_fingerprint(text_content))
            
            if processing_config.get('quality_assessment', True):
                tasks.append(self._assess_quality(text_content, metadata))
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Compile final result
            result = {
                'success': True,
                'metadata': metadata,
                'original_text': text_content,
                'processing_config': processing_config,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add processing results
            for i, task_result in enumerate(results):
                if isinstance(task_result, Exception):
                    self.logger.error(f"Task {i} failed: {str(task_result)}")
                else:
                    result.update(task_result)
            
            self.logger.info("Text processing completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Text processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _prepare_text(
        self,
        text_data: Union[str, bytes],
        format_hint: Optional[str] = None
    ) -> str:
        """Prepare text data for processing"""        try:
            if isinstance(text_data, bytes):
                # Decode bytes to string
                text_content = text_data.decode('utf-8', errors='ignore')
            elif isinstance(text_data, str):
                text_content = text_data
            else:
                raise ValueError(f"Unsupported text data type: {type(text_data)}")
            
            # Standard text cleaning
            text_content = self._clean_text(text_content)
            
            # Length validation
            if len(text_content) > self.config['max_length']:
                self.logger.warning(f"Text truncated from {len(text_content)} to {self.config['max_length']} characters")
                text_content = text_content[:self.config['max_length']]
            
            return text_content
            
        except Exception as e:
            self.logger.error(f"Error preparing text: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""        try:
            # Normalize unicode characters
            text = unicodedata.normalize('NFKD', text)
            
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove control characters
            text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
            
            # Strip leading/trailing whitespace
            text = text.strip()
            
            return text
            
        except Exception as e:
            self.logger.warning(f"Text cleaning failed: {str(e)}")
            return text

import asyncio
import logging
import re
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import numpy as np

# NLP libraries
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer, PorterStemmer
    from nltk.tag import pos_tag
    from nltk.chunk import ne_chunk
    NLTK_AVAILABLE = True
    
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
        
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('averaged_perceptron_tagger', quiet=True)
        
    try:
        nltk.data.find('chunkers/maxent_ne_chunker')
    except LookupError:
        nltk.download('maxent_ne_chunker', quiet=True)
        
    try:
        nltk.data.find('corpora/words')
    except LookupError:
        nltk.download('words', quiet=True)

except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available - some text processing features will be limited")

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available - AI features will be limited")

try:
    from textstat import flesch_reading_ease, flesch_kincaid_grade, automated_readability_index
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
    logging.warning("Textstat not available - readability analysis will be limited")

try:
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.warning("Langdetect not available - language detection will be limited")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available - some analysis features will be limited")

logger = logging.getLogger(__name__)

@dataclass
class TextMetadata:
    """Text metadata container"""    char_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    language: Optional[str] = None
    encoding: str = 'utf-8'
    file_size: int = 0
    reading_time_minutes: float = 0.0

@dataclass
class TextFeatures:
    """Text feature extraction results"""    tfidf_vector: Optional[np.ndarray] = None
    word_frequencies: Dict[str, int] = None
    pos_tags: List[Tuple[str, str]] = None
    named_entities: List[Tuple[str, str]] = None
    sentiment_score: Optional[float] = None
    emotion_scores: Optional[Dict[str, float]] = None
    readability_scores: Optional[Dict[str, float]] = None
    keywords: List[str] = None
    topics: List[str] = None
    embeddings: Optional[np.ndarray] = None

@dataclass
class TextFingerprint:
    """Text fingerprint data"""    content_hash: Optional[str] = None
    semantic_hash: Optional[str] = None
    structure_hash: Optional[str] = None
    n_gram_hash: Optional[str] = None
    keyword_hash: Optional[str] = None
    combined_hash: Optional[str] = None

class TextProcessor:
    """Professional text processing engine"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize text processing engines
        self._initialize_engines()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default text processing configuration"""        return {
            'language': 'auto',
            'max_length': 100000,
            'enhancement': True,
            'spell_check': False,
            'grammar_check': False,
            'sentiment_analysis': True,
            'emotion_analysis': False,
            'named_entity_recognition': True,
            'keyword_extraction': True,
            'topic_modeling': False,
            'readability_analysis': True,
            'fingerprinting': True,
            'feature_extraction': True,
            'similarity_analysis': False,
            'seo_optimization': True,
            'batch_size': 32,
            'n_gram_size': 3,
            'min_keyword_freq': 2,
            'max_keywords': 50
        }
    
    def _initialize_engines(self):
        """Initialize text processing engines"""        try:
            # Initialize NLTK components
            if NLTK_AVAILABLE:
                self.lemmatizer = WordNetLemmatizer()
                self.stemmer = PorterStemmer()
                self.stop_words = set(stopwords.words('english'))
                
                # Add more stop words for different languages
                try:
                    self.stop_words.update(stopwords.words('german'))
                    self.stop_words.update(stopwords.words('french'))
                    self.stop_words.update(stopwords.words('spanish'))
                except:
                    pass
            
            # Initialize transformers models
            if TRANSFORMERS_AVAILABLE:
                try:
                    # Sentiment analysis pipeline
                    self.sentiment_analyzer = pipeline(
                        "sentiment-analysis",
                        model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                        return_all_scores=True
                    )
                    
                    # Text embeddings model
                    self.embedding_model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
                    self.embedding_tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
                    
                    self.logger.info("Transformers models initialized")
                    
                except Exception as e:
                    self.logger.warning(f"Transformers initialization failed: {str(e)}")
                    self.sentiment_analyzer = None
                    self.embedding_model = None
                    self.embedding_tokenizer = None
            else:
                self.sentiment_analyzer = None
                self.embedding_model = None
                self.embedding_tokenizer = None
            
            # Initialize TF-IDF vectorizer
            if SKLEARN_AVAILABLE:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
            
            self.logger.info("Text processor engines initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing text engines: {str(e)}")
            raise
    
    async def process(
        self,
        text_data: Union[str, bytes],
        format_hint: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Main text processing pipeline
        
        Args:
            text_data: Text data as string or bytes
            format_hint: Optional format hint for processing
            config: Optional processing configuration override
        
        Returns:
            Dict containing processed text data and analysis results
        """        try:
            # Merge configuration
            processing_config = self.config.copy()
            if config:
                processing_config.update(config)
            
            # Prepare text
            text = await self._prepare_text(text_data, format_hint)
            
            # Extract metadata
            metadata = await self._extract_metadata(text)
            
            # Process text in parallel
            tasks = []
            
            if processing_config.get('feature_extraction', True):
                tasks.append(self._extract_features(text))
            
            if processing_config.get('fingerprinting', True):
                tasks.append(self._generate_fingerprint(text))
            
            if processing_config.get('sentiment_analysis', True):
                tasks.append(self._analyze_sentiment(text))
            
            if processing_config.get('named_entity_recognition', True):
                tasks.append(self._extract_named_entities(text))
            
            if processing_config.get('keyword_extraction', True):
                tasks.append(self._extract_keywords(text))
            
            if processing_config.get('readability_analysis', True):
                tasks.append(self._analyze_readability(text))
            
            if processing_config.get('enhancement', True):
                tasks.append(self._enhance_text(text))
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Compile final result
            result = {
                'success': True,
                'metadata': metadata,
                'original_text': text,
                'text_length': len(text),
                'processing_config': processing_config,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add processing results
            for i, task_result in enumerate(results):
                if isinstance(task_result, Exception):
                    self.logger.error(f"Task {i} failed: {str(task_result)}")
                else:
                    result.update(task_result)
            
            self.logger.info("Text processing completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Text processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _prepare_text(
        self,
        text_data: Union[str, bytes],
        format_hint: Optional[str] = None
    ) -> str:
        """Prepare text data for processing"""        try:
            if isinstance(text_data, bytes):
                # Decode bytes to string
                try:
                    text = text_data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        text = text_data.decode('latin-1')
                    except UnicodeDecodeError:
                        text = text_data.decode('utf-8', errors='ignore')
            elif isinstance(text_data, str):
                text = text_data
            else:
                raise ValueError(f"Unsupported text data type: {type(text_data)}")
            
            # Clean and normalize text
            text = self._clean_text(text)
            
            # Truncate if too long
            max_length = self.config.get('max_length', 100000)
            if len(text) > max_length:
                text = text[:max_length]
                self.logger.warning(f"Text truncated to {max_length} characters")
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error preparing text: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove control characters
            text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
            
            # Normalize line endings
            text = text.replace('\r\n', '\n').replace('\r', '\n')
            
            # Remove excessive newlines
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            # Strip leading/trailing whitespace
            text = text.strip()
            
            return text
            
        except Exception as e:
            self.logger.warning(f"Text cleaning failed: {str(e)}")
            return text
    
    async def _extract_metadata(self, text: str) -> TextMetadata:
        """Extract comprehensive text metadata"""        try:
            # Standard counts
            char_count = len(text)
            word_count = len(text.split())
            
            # Sentence count
            if NLTK_AVAILABLE:
                sentences = sent_tokenize(text)
                sentence_count = len(sentences)
            else:
                # Optimized sentence counting
                sentence_count = len(re.split(r'[.!?]+', text))
            
            # Paragraph count
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            paragraph_count = len(paragraphs)
            
            # Language detection
            language = None
            if LANGDETECT_AVAILABLE and len(text.strip()) > 10:
                try:
                    language = detect(text)
                except:
                    language = 'unknown'
            
            # Reading time estimation (average 200 words per minute)
            reading_time_minutes = word_count / 200.0
            
            metadata = TextMetadata(
                char_count=char_count,
                word_count=word_count,
                sentence_count=sentence_count,
                paragraph_count=paragraph_count,
                language=language,
                encoding='utf-8',
                file_size=len(text.encode('utf-8')),
                reading_time_minutes=reading_time_minutes
            )
            
            self.logger.debug(f"Extracted metadata: {metadata}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {str(e)}")
            raise
    
    async def _extract_features(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive text features"""        try:
            features_data = {}
            
            # Word frequency analysis
            if NLTK_AVAILABLE:
                tokens = word_tokenize(text.lower())
                tokens = [token for token in tokens if token.isalpha() and token not in self.stop_words]
                
                word_freq = {}
                for token in tokens:
                    word_freq[token] = word_freq.get(token, 0) + 1
                
                # Get top words
                top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]
                features_data['word_frequencies'] = dict(top_words)
                
                # POS tagging
                pos_tags = pos_tag(word_tokenize(text))
                features_data['pos_tags'] = pos_tags[:100]  # Limit for performance
            else:
                # Optimized word frequency
                words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
                word_freq = {}
                for word in words:
                    if len(word) > 2:  # Skip very short words
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:50]
                features_data['word_frequencies'] = dict(top_words)
                features_data['pos_tags'] = []
            
            # TF-IDF vectorization
            if SKLEARN_AVAILABLE and len(text.strip()) > 10:
                try:
                    # Create corpus for TF-IDF (split text into sentences)
                    sentences = sent_tokenize(text) if NLTK_AVAILABLE else [text]
                    
                    if len(sentences) > 1:
                        tfidf_matrix = self.tfidf_vectorizer.fit_transform(sentences)
                        features_data['tfidf_vector'] = tfidf_matrix.mean(axis=0).A1
                    else:
                        features_data['tfidf_vector'] = None
                except Exception as e:
                    self.logger.warning(f"TF-IDF vectorization failed: {str(e)}")
                    features_data['tfidf_vector'] = None
            
            # Text embeddings
            if self.embedding_model and self.embedding_tokenizer:
                try:
                    # Truncate text for embeddings
                    text_sample = text[:512] if len(text) > 512 else text
                    
                    inputs = self.embedding_tokenizer(
                        text_sample, 
                        return_tensors="pt", 
                        truncation=True, 
                        padding=True,
                        max_length=512
                    )
                    
                    with torch.no_grad():
                        outputs = self.embedding_model(**inputs)
                        # Use mean pooling
                        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                        features_data['embeddings'] = embeddings
                except Exception as e:
                    self.logger.warning(f"Text embedding failed: {str(e)}")
                    features_data['embeddings'] = None
            
            # N-gram analysis
            n_gram_size = self.config.get('n_gram_size', 3)
            if NLTK_AVAILABLE:
                tokens = word_tokenize(text.lower())
                tokens = [token for token in tokens if token.isalpha()]
                
                n_grams = []
                for i in range(len(tokens) - n_gram_size + 1):
                    n_gram = ' '.join(tokens[i:i + n_gram_size])
                    n_grams.append(n_gram)
                
                n_gram_freq = {}
                for n_gram in n_grams:
                    n_gram_freq[n_gram] = n_gram_freq.get(n_gram, 0) + 1
                
                top_n_grams = sorted(n_gram_freq.items(), key=lambda x: x[1], reverse=True)[:20]
                features_data['n_grams'] = dict(top_n_grams)
            
            features = TextFeatures(
                tfidf_vector=features_data.get('tfidf_vector'),
                word_frequencies=features_data.get('word_frequencies', {}),
                pos_tags=features_data.get('pos_tags', []),
                named_entities=[],  # Will be filled by NER task
                embeddings=features_data.get('embeddings')
            )
            
            return {
                'features': features,
                'feature_extraction_success': True,
                'feature_statistics': {
                    'unique_words': len(features_data.get('word_frequencies', {})),
                    'most_common_word': max(features_data.get('word_frequencies', {}).items(), key=lambda x: x[1])[0] if features_data.get('word_frequencies') else None,
                    'vocab_richness': len(features_data.get('word_frequencies', {})) / max(sum(features_data.get('word_frequencies', {}).values()), 1),
                    'embedding_dimension': len(features_data.get('embeddings', [])) if features_data.get('embeddings') is not None else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {str(e)}")
            return {
                'features': None,
                'feature_extraction_success': False,
                'error': str(e)
            }
    
    async def _generate_fingerprint(self, text: str) -> Dict[str, Any]:
        """Generate comprehensive text fingerprint"""        try:
            fingerprint = TextFingerprint()
            
            # Content hash (optimized MD5 of cleaned text)
            cleaned_text = re.sub(r'\s+', ' ', text.lower()).strip()
            fingerprint.content_hash = hashlib.md5(cleaned_text.encode()).hexdigest()
            
            # Structure hash (based on paragraph and sentence structure)
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            structure_data = {
                'paragraph_count': len(paragraphs),
                'avg_paragraph_length': np.mean([len(p) for p in paragraphs]) if paragraphs else 0,
                'sentence_count': len(re.split(r'[.!?]+', text))
            }
            structure_str = json.dumps(structure_data, sort_keys=True)
            fingerprint.structure_hash = hashlib.md5(structure_str.encode()).hexdigest()
            
            # N-gram hash
            if NLTK_AVAILABLE:
                tokens = word_tokenize(text.lower())
                tokens = [token for token in tokens if token.isalpha()]
                
                # Create n-grams
                n_grams = []
                for n in range(2, 4):  # 2-grams and 3-grams
                    for i in range(len(tokens) - n + 1):
                        n_gram = ' '.join(tokens[i:i + n])
                        n_grams.append(n_gram)
                
                # Hash most frequent n-grams
                n_gram_freq = {}
                for n_gram in n_grams:
                    n_gram_freq[n_gram] = n_gram_freq.get(n_gram, 0) + 1
                
                top_n_grams = sorted(n_gram_freq.items(), key=lambda x: x[1], reverse=True)[:50]
                n_gram_str = '|'.join([ng[0] for ng in top_n_grams])
                fingerprint.n_gram_hash = hashlib.md5(n_gram_str.encode()).hexdigest()
            
            # Keyword hash
            words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Only consider longer words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:30]
            keyword_str = '|'.join([kw[0] for kw in top_keywords])
            fingerprint.keyword_hash = hashlib.md5(keyword_str.encode()).hexdigest()
            
            # Semantic hash (if embeddings available)
            if self.embedding_model and self.embedding_tokenizer:
                try:
                    text_sample = text[:512] if len(text) > 512 else text
                    inputs = self.embedding_tokenizer(
                        text_sample, 
                        return_tensors="pt", 
                        truncation=True, 
                        padding=True,
                        max_length=512
                    )
                    
                    with torch.no_grad():
                        outputs = self.embedding_model(**inputs)
                        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                        
                        # Create hash from embedding
                        # Quantize embeddings to create stable hash
                        quantized = (embeddings * 1000).astype(int)
                        fingerprint.semantic_hash = hashlib.md5(quantized.tobytes()).hexdigest()
                except Exception as e:
                    self.logger.warning(f"Semantic hash generation failed: {str(e)}")
            
            # Combined hash
            combined_data = (
                (fingerprint.content_hash or '') +
                (fingerprint.structure_hash or '') +
                (fingerprint.n_gram_hash or '') +
                (fingerprint.keyword_hash or '') +
                (fingerprint.semantic_hash or '')
            )
            fingerprint.combined_hash = hashlib.sha256(combined_data.encode()).hexdigest()
            
            return {
                'fingerprint': fingerprint,
                'fingerprint_success': True,
                'fingerprint_algorithms': ['content', 'structure', 'n_gram', 'keyword', 'semantic', 'combined']
            }
            
        except Exception as e:
            self.logger.error(f"Text fingerprinting failed: {str(e)}")
            return {
                'fingerprint': None,
                'fingerprint_success': False,
                'error': str(e)
            }
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze text sentiment"""        try:
            sentiment_data = {}
            
            if self.sentiment_analyzer:
                try:
                    # Analyze sentiment with transformers
                    # Split long text into chunks
                    chunks = self._split_text_chunks(text, max_length=512)
                    
                    sentiment_scores = []
                    for chunk in chunks[:5]:  # Analyze max 5 chunks
                        if len(chunk.strip()) > 10:
                            results = self.sentiment_analyzer(chunk)
                            sentiment_scores.extend(results)
                    
                    if sentiment_scores:
                        # Aggregate scores
                        labels = ['NEGATIVE', 'NEUTRAL', 'POSITIVE']
                        aggregated_scores = {label: 0.0 for label in labels}
                        
                        for scores in sentiment_scores:
                            if isinstance(scores, list):
                                for score in scores:
                                    label = score['label']
                                    if label in aggregated_scores:
                                        aggregated_scores[label] += score['score']
                        
                        # Normalize scores
                        total_score = sum(aggregated_scores.values())
                        if total_score > 0:
                            for label in aggregated_scores:
                                aggregated_scores[label] /= total_score
                        
                        sentiment_data['sentiment_scores'] = aggregated_scores
                        
                        # Overall sentiment
                        if aggregated_scores['POSITIVE'] > aggregated_scores['NEGATIVE']:
                            overall_sentiment = 'positive'
                            sentiment_confidence = aggregated_scores['POSITIVE']
                        elif aggregated_scores['NEGATIVE'] > aggregated_scores['POSITIVE']:
                            overall_sentiment = 'negative'
                            sentiment_confidence = aggregated_scores['NEGATIVE']
                        else:
                            overall_sentiment = 'neutral'
                            sentiment_confidence = aggregated_scores['NEUTRAL']
                        
                        sentiment_data['overall_sentiment'] = overall_sentiment
                        sentiment_data['sentiment_confidence'] = float(sentiment_confidence)
                        
                except Exception as e:
                    self.logger.warning(f"Transformer sentiment analysis failed: {str(e)}")
            
            # Professional rule-based sentiment as fallback
            if not sentiment_data:
                positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'enjoy', 'happy']
                negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'sad', 'angry', 'disappointed', 'frustrated', 'horrible']
                
                words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
                
                positive_count = sum(1 for word in words if word in positive_words)
                negative_count = sum(1 for word in words if word in negative_words)
                
                if positive_count > negative_count:
                    overall_sentiment = 'positive'
                    sentiment_confidence = positive_count / (positive_count + negative_count)
                elif negative_count > positive_count:
                    overall_sentiment = 'negative'
                    sentiment_confidence = negative_count / (positive_count + negative_count)
                else:
                    overall_sentiment = 'neutral'
                    sentiment_confidence = 0.5
                
                sentiment_data = {
                    'overall_sentiment': overall_sentiment,
                    'sentiment_confidence': float(sentiment_confidence),
                    'positive_word_count': positive_count,
                    'negative_word_count': negative_count
                }
            
            return {
                'sentiment_analysis': sentiment_data,
                'sentiment_analysis_success': True
            }
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {str(e)}")
            return {
                'sentiment_analysis': None,
                'sentiment_analysis_success': False,
                'error': str(e)
            }
    
    async def _extract_named_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text"""        try:
            named_entities = []
            
            if NLTK_AVAILABLE:
                try:
                    # NLTK named entity recognition
                    tokens = word_tokenize(text)
                    pos_tags = pos_tag(tokens)
                    tree = ne_chunk(pos_tags)
                    
                    for subtree in tree:
                        if hasattr(subtree, 'label'):
                            entity = ' '.join([token for token, pos in subtree.leaves()])
                            entity_type = subtree.label()
                            named_entities.append((entity, entity_type))
                            
                except Exception as e:
                    self.logger.warning(f"NLTK NER failed: {str(e)}")
            
            # Professional pattern-based entity extraction as fallback
            if not named_entities:
                # Email addresses
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
                for email in emails:
                    named_entities.append((email, 'EMAIL'))
                
                # URLs
                urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
                for url in urls:
                    named_entities.append((url, 'URL'))
                
                # Dates (professional patterns)
                dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)
                for date in dates:
                    named_entities.append((date, 'DATE'))
                
                # Phone numbers (professional pattern)
                phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
                for phone in phones:
                    named_entities.append((phone, 'PHONE'))
            
            # Group entities by type
            entity_types = {}
            for entity, entity_type in named_entities:
                if entity_type not in entity_types:
                    entity_types[entity_type] = []
                entity_types[entity_type].append(entity)
            
            return {
                'named_entity_recognition': {
                    'entities': named_entities,
                    'entity_types': entity_types,
                    'entity_count': len(named_entities),
                    'unique_entities': len(set(entity for entity, _ in named_entities))
                },
                'ner_success': True
            }
            
        except Exception as e:
            self.logger.error(f"Named entity recognition failed: {str(e)}")
            return {
                'named_entity_recognition': None,
                'ner_success': False,
                'error': str(e)
            }
    
    async def _extract_keywords(self, text: str) -> Dict[str, Any]:
        """Extract keywords from text"""        try:
            keywords_data = {}
            
            # Professional TF-IDF based keyword extraction
            if SKLEARN_AVAILABLE:
                try:
                    # Prepare text
                    sentences = sent_tokenize(text) if NLTK_AVAILABLE else [text]
                    
                    if len(sentences) > 1:
                        # Use TF-IDF to find important terms
                        vectorizer = TfidfVectorizer(
                            max_features=self.config.get('max_keywords', 50),
                            stop_words='english',
                            ngram_range=(1, 2),
                            min_df=1
                        )
                        
                        tfidf_matrix = vectorizer.fit_transform(sentences)
                        feature_names = vectorizer.get_feature_names_out()
                        
                        # Get average TF-IDF scores
                        mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
                        
                        # Sort by importance
                        keyword_scores = list(zip(feature_names, mean_scores))
                        keyword_scores.sort(key=lambda x: x[1], reverse=True)
                        
                        keywords_data['tfidf_keywords'] = [
                            {'keyword': kw, 'score': float(score)} 
                            for kw, score in keyword_scores[:20]
                        ]
                    
                except Exception as e:
                    self.logger.warning(f"TF-IDF keyword extraction failed: {str(e)}")
            
            # Frequency-based keyword extraction
            if NLTK_AVAILABLE:
                tokens = word_tokenize(text.lower())
                tokens = [token for token in tokens if token.isalpha() and len(token) > 3 and token not in self.stop_words]
                
                word_freq = {}
                for token in tokens:
                    word_freq[token] = word_freq.get(token, 0) + 1
                
                # Filter by minimum frequency
                min_freq = self.config.get('min_keyword_freq', 2)
                keywords = [(word, freq) for word, freq in word_freq.items() if freq >= min_freq]
                keywords.sort(key=lambda x: x[1], reverse=True)
                
                keywords_data['frequency_keywords'] = [
                    {'keyword': kw, 'frequency': freq} 
                    for kw, freq in keywords[:30]
                ]
            
            # SEO keyword suggestions (professional approach)
            seo_keywords = []
            if self.config.get('seo_optimization', True):
                # Extract phrases that might be good for SEO
                phrases = re.findall(r'\b[a-zA-Z]+(?:\s+[a-zA-Z]+){1,3}\b', text)
                
                phrase_freq = {}
                for phrase in phrases:
                    phrase_lower = phrase.lower()
                    if len(phrase_lower) > 10 and len(phrase_lower) < 50:  # Good SEO phrase length
                        phrase_freq[phrase_lower] = phrase_freq.get(phrase_lower, 0) + 1
                
                seo_keywords = [
                    {'phrase': phrase, 'frequency': freq}
                    for phrase, freq in sorted(phrase_freq.items(), key=lambda x: x[1], reverse=True)[:10]
                    if freq > 1
                ]
            
            keywords_data['seo_keywords'] = seo_keywords
            
            return {
                'keyword_extraction': keywords_data,
                'keyword_extraction_success': True
            }
            
        except Exception as e:
            self.logger.error(f"Keyword extraction failed: {str(e)}")
            return {
                'keyword_extraction': None,
                'keyword_extraction_success': False,
                'error': str(e)
            }
    
    async def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability"""        try:
            readability_data = {}
            
            if TEXTSTAT_AVAILABLE:
                try:
                    readability_data['flesch_reading_ease'] = flesch_reading_ease(text)
                    readability_data['flesch_kincaid_grade'] = flesch_kincaid_grade(text)
                    readability_data['automated_readability_index'] = automated_readability_index(text)
                    
                    # Readability level interpretation
                    flesch_score = readability_data['flesch_reading_ease']
                    if flesch_score >= 90:
                        readability_level = 'Very Easy'
                    elif flesch_score >= 80:
                        readability_level = 'Easy'
                    elif flesch_score >= 70:
                        readability_level = 'Fairly Easy'
                    elif flesch_score >= 60:
                        readability_level = 'Standard'
                    elif flesch_score >= 50:
                        readability_level = 'Fairly Difficult'
                    elif flesch_score >= 30:
                        readability_level = 'Difficult'
                    else:
                        readability_level = 'Very Difficult'
                    
                    readability_data['readability_level'] = readability_level
                    
                except Exception as e:
                    self.logger.warning(f"Textstat readability analysis failed: {str(e)}")
            
            # Professional readability metrics
            words = text.split()
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if words and sentences:
                avg_words_per_sentence = len(words) / len(sentences)
                avg_chars_per_word = sum(len(word) for word in words) / len(words)
                
                readability_data['avg_words_per_sentence'] = float(avg_words_per_sentence)
                readability_data['avg_chars_per_word'] = float(avg_chars_per_word)
                
                # Professional complexity score
                complexity_score = (avg_words_per_sentence / 20) + (avg_chars_per_word / 6)
                readability_data['complexity_score'] = float(complexity_score)
            
            return {
                'readability_analysis': readability_data,
                'readability_analysis_success': True
            }
            
        except Exception as e:
            self.logger.error(f"Readability analysis failed: {str(e)}")
            return {
                'readability_analysis': None,
                'readability_analysis_success': False,
                'error': str(e)
            }
    
    async def _enhance_text(self, text: str) -> Dict[str, Any]:
        """Enhance text quality"""        try:
            enhanced_text = text
            enhancements_applied = []
            
            # Remove excessive whitespace
            enhanced_text = re.sub(r'\s+', ' ', enhanced_text)
            enhanced_text = re.sub(r'\n{3,}', '\n\n', enhanced_text)
            enhancements_applied.append('whitespace_normalization')
            
            # Fix common punctuation issues
            enhanced_text = re.sub(r'\s+([,.!?;:])', r'\1', enhanced_text)
            enhanced_text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', enhanced_text)
            enhancements_applied.append('punctuation_fixes')
            
            # Capitalize sentences
            sentences = re.split(r'([.!?]+)', enhanced_text)
            for i in range(0, len(sentences), 2):
                if i < len(sentences) and sentences[i].strip():
                    sentences[i] = sentences[i].strip()
                    if sentences[i] and sentences[i][0].islower():
                        sentences[i] = sentences[i][0].upper() + sentences[i][1:]
            enhanced_text = ''.join(sentences)
            enhancements_applied.append('capitalization')
            
            # Calculate improvement score
            original_quality = self._calculate_text_quality(text)
            enhanced_quality = self._calculate_text_quality(enhanced_text)
            improvement_score = enhanced_quality - original_quality
            
            return {
                'text_enhancement': {
                    'enhanced_text': enhanced_text,
                    'original_quality_score': float(original_quality),
                    'enhanced_quality_score': float(enhanced_quality),
                    'improvement_score': float(improvement_score),
                    'enhancements_applied': enhancements_applied
                },
                'enhancement_success': True
            }
            
        except Exception as e:
            self.logger.error(f"Text enhancement failed: {str(e)}")
            return {
                'text_enhancement': {
                    'enhanced_text': text,
                    'enhancement_success': False,
                    'error': str(e)
                },
                'enhancement_success': False
            }
    
    def _calculate_text_quality(self, text: str) -> float:
        """Calculate a professional text quality score"""        try:
            score = 0.0
            
            # Check for proper capitalization
            sentences = re.split(r'[.!?]+', text)
            capitalized_sentences = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
            if sentences:
                score += (capitalized_sentences / len(sentences)) * 20
            
            # Check for proper punctuation
            punctuation_score = min(len(re.findall(r'[.!?]', text)) / max(len(sentences), 1) * 20, 20)
            score += punctuation_score
            
            # Check for reasonable sentence length
            words = text.split()
            if sentences and words:
                avg_sentence_length = len(words) / len(sentences)
                if 10 <= avg_sentence_length <= 25:  # Ideal range
                    score += 20
                else:
                    score += max(0, 20 - abs(avg_sentence_length - 17.5))
            
            # Check for vocabulary diversity
            unique_words = len(set(word.lower() for word in words if word.isalpha()))
            if words:
                vocab_diversity = unique_words / len(words)
                score += vocab_diversity * 20
            
            # Check for excessive whitespace issues
            whitespace_issues = len(re.findall(r'\s{2,}', text))
            score -= min(whitespace_issues, 20)
            
            return max(0, min(100, score))
            
        except Exception:
            return 50.0  # Default score
    
    def _split_text_chunks(self, text: str, max_length: int = 512) -> List[str]:
        """Split text into chunks for processing"""        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = sent_tokenize(text) if NLTK_AVAILABLE else [text]
        
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
    
    async def batch_process(
        self,
        text_files: List[str],
        config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Process multiple text files in batch"""        tasks = []
        for file_path in text_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            task = self.process(text_content, config=config)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if not isinstance(result, Exception) 
            else {'success': False, 'error': str(result), 'file': text_files[i]}
            for i, result in enumerate(results)
        ]
