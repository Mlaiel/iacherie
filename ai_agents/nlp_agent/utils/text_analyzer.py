"""Text Analyzer - Core Text Processing Engine
==========================================

Advanced text analysis engine providing comprehensive text preprocessing,
analysis, and feature extraction capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import re
import string
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import unicodedata
import asyncio
from concurrent.futures import ThreadPoolExecutor

import nltk
import spacy
from textstat import flesch_reading_ease, flesch_kincaid_grade, automated_readability_index
from wordcloud import WordCloud
import emoji

from .config import NLPAgentConfig, default_config

# Ensure NLTK data is available
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class TextStatistics:
    """Text statistics and metrics"""    character_count: int = 0
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    avg_word_length: float = 0.0
    avg_sentence_length: float = 0.0
    unique_words: int = 0
    vocabulary_richness: float = 0.0
    readability_score: float = 0.0
    reading_grade: float = 0.0
    automated_readability: float = 0.0
    emoji_count: int = 0
    hashtag_count: int = 0
    mention_count: int = 0
    url_count: int = 0

@dataclass
class TextFeatures:
    """Extracted text features"""    tokens: List[str] = field(default_factory=list)
    sentences: List[str] = field(default_factory=list)
    words: List[str] = field(default_factory=list)
    pos_tags: List[Tuple[str, str]] = field(default_factory=list)
    named_entities: List[Dict[str, Any]] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    bigrams: List[Tuple[str, str]] = field(default_factory=list)
    trigrams: List[Tuple[str, str, str]] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    emojis: List[str] = field(default_factory=list)

@dataclass
class TextAnalysisResult:
    """Complete text analysis result"""    text: str
    cleaned_text: str
    language: Optional[str] = None
    statistics: TextStatistics = field(default_factory=TextStatistics)
    features: TextFeatures = field(default_factory=TextFeatures)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class TextAnalyzer:
    """    Advanced text analysis engine providing comprehensive text preprocessing,
    analysis, and feature extraction capabilities.
    """    
    def __init__(self, config: Optional[NLPAgentConfig] = None):
        """Initialize Text Analyzer"""        self.config = config or default_config
        self.executor = ThreadPoolExecutor(max_workers=self.config.performance.max_workers)
        self._nlp_models = {}
        self._initialize_models()
        
        # Compile regex patterns for performance
        self._compile_patterns()
    
    def _initialize_models(self):
        """Initialize NLP models"""        try:
            # Initialize spaCy model for advanced features
            spacy_models = ["en_core_web_sm", "en_core_web_md"]
            for model_name in spacy_models:
                try:
                    self._nlp_models["spacy_en"] = spacy.load(model_name)
                    logger.info(f"Loaded spaCy model: {model_name}")
                    break
                except OSError:
                    continue
            
            if "spacy_en" not in self._nlp_models:
                logger.warning("No spaCy English model found. Advanced features will be limited.")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP models: {e}")
    
    def _compile_patterns(self):
        """Compile regex patterns for text analysis"""        self.patterns = {
            "url": re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            "hashtag": re.compile(r'#\w+'),
            "mention": re.compile(r'@\w+'),
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            "whitespace": re.compile(r'\s+'),
            "punctuation": re.compile(r'[{}]'.format(re.escape(string.punctuation))),
            "non_ascii": re.compile(r'[^\x00-\x7F]+'),
            "html_tags": re.compile(r'<[^>]+>'),
            "number": re.compile(r'\b\d+(?:\.\d+)?\b')
        }
    
    async def analyze(self, text: str, **kwargs) -> TextAnalysisResult:
        """        Perform comprehensive text analysis
        
        Args:
            text: Input text to analyze
            **kwargs: Additional analysis options
        
        Returns:
            TextAnalysisResult with comprehensive analysis
        """        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")
        
        start_time = asyncio.get_event_loop().time()
        
        # Initialize result
        result = TextAnalysisResult(text=text, cleaned_text="")
        
        try:
            # Preprocessing
            result.cleaned_text = await self._preprocess_text(text)
            
            # Extract basic statistics
            result.statistics = await self._extract_statistics(text, result.cleaned_text)
            
            # Extract features
            result.features = await self._extract_features(text, result.cleaned_text)
            
            # Add metadata
            result.metadata = {
                "original_length": len(text),
                "cleaned_length": len(result.cleaned_text),
                "processing_options": kwargs,
                "analyzer_version": "2.0"
            }
            
            result.processing_time = asyncio.get_event_loop().time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            result.processing_time = asyncio.get_event_loop().time() - start_time
            raise
    
    async def _preprocess_text(self, text: str) -> str:
        """Preprocess text based on configuration"""        processed_text = text
        
        if self.config.processing.enable_preprocessing:
            # Remove HTML tags
            if self.config.processing.remove_html:
                processed_text = self.patterns["html_tags"].sub("", processed_text)
            
            # Remove URLs
            if self.config.processing.remove_urls:
                processed_text = self.patterns["url"].sub("", processed_text)
            
            # Normalize whitespace
            if self.config.processing.normalize_whitespace:
                processed_text = self.patterns["whitespace"].sub(" ", processed_text)
            
            # Convert to lowercase
            if self.config.processing.lowercase:
                processed_text = processed_text.lower()
            
            # Remove punctuation
            if self.config.processing.remove_punctuation:
                processed_text = self.patterns["punctuation"].sub("", processed_text)
            
            # Unicode normalization
            processed_text = unicodedata.normalize('NFKC', processed_text)
            
            # Strip whitespace
            processed_text = processed_text.strip()
        
        return processed_text
    
    async def _extract_statistics(self, original_text: str, cleaned_text: str) -> TextStatistics:
        """Extract comprehensive text statistics"""        stats = TextStatistics()
        
        # Basic counts
        stats.character_count = len(original_text)
        words = cleaned_text.split()
        stats.word_count = len(words)
        
        # Sentence count using NLTK
        try:
            sentences = nltk.sent_tokenize(original_text)
            stats.sentence_count = len(sentences)
        except Exception:
            # Fallback to simple sentence splitting
            stats.sentence_count = len([s for s in original_text.split('.') if s.strip()])
        
        # Paragraph count
        stats.paragraph_count = len([p for p in original_text.split('\n\n') if p.strip()])
        
        # Average calculations
        if stats.word_count > 0:
            stats.avg_word_length = sum(len(word) for word in words) / stats.word_count
        
        if stats.sentence_count > 0:
            stats.avg_sentence_length = stats.word_count / stats.sentence_count
        
        # Unique words and vocabulary richness
        unique_words = set(word.lower() for word in words if word.isalpha())
        stats.unique_words = len(unique_words)
        
        if stats.word_count > 0:
            stats.vocabulary_richness = stats.unique_words / stats.word_count
        
        # Readability scores
        if stats.word_count > 0 and stats.sentence_count > 0:
            try:
                stats.readability_score = flesch_reading_ease(original_text)
                stats.reading_grade = flesch_kincaid_grade(original_text)
                stats.automated_readability = automated_readability_index(original_text)
            except Exception as e:
                logger.warning(f"Readability calculation failed: {e}")
        
        # Social media specific counts
        stats.hashtag_count = len(self.patterns["hashtag"].findall(original_text))
        stats.mention_count = len(self.patterns["mention"].findall(original_text))
        stats.url_count = len(self.patterns["url"].findall(original_text))
        stats.emoji_count = len([char for char in original_text if char in emoji.UNICODE_EMOJI['en']])
        
        return stats
    
    async def _extract_features(self, original_text: str, cleaned_text: str) -> TextFeatures:
        """Extract comprehensive text features"""        features = TextFeatures()
        
        try:
            # Basic tokenization
            features.words = cleaned_text.split()
            features.tokens = nltk.word_tokenize(original_text.lower())
            
            # Sentence tokenization
            features.sentences = nltk.sent_tokenize(original_text)
            
            # POS tagging
            if features.tokens:
                features.pos_tags = nltk.pos_tag(features.tokens)
            
            # N-grams
            if len(features.words) >= 2:
                features.bigrams = list(nltk.bigrams(features.words))
            
            if len(features.words) >= 3:
                features.trigrams = list(nltk.trigrams(features.words))
            
            # Social media features
            features.hashtags = self.patterns["hashtag"].findall(original_text)
            features.mentions = self.patterns["mention"].findall(original_text)
            features.urls = self.patterns["url"].findall(original_text)
            features.emojis = [char for char in original_text if char in emoji.UNICODE_EMOJI['en']]
            
            # Advanced features using spaCy (if available)
            if "spacy_en" in self._nlp_models:
                await self._extract_spacy_features(original_text, features)
            
            # Keyword extraction (simple TF-IDF based)
            features.keywords = await self._extract_keywords(cleaned_text)
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
        
        return features
    
    async def _extract_spacy_features(self, text: str, features: TextFeatures):
        """Extract features using spaCy"""        try:
            nlp = self._nlp_models["spacy_en"]
            doc = nlp(text)
            
            # Named entities
            features.named_entities = [
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": getattr(ent, "confidence", 1.0)
                }
                for ent in doc.ents
            ]
            
        except Exception as e:
            logger.error(f"spaCy feature extraction failed: {e}")
    
    async def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords using TF-IDF approach"""        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from nltk.corpus import stopwords
            
            # Get stopwords
            try:
                stop_words = set(stopwords.words('english'))
            except LookupError:
                stop_words = set()
            
            # Simple keyword extraction
            words = text.split()
            filtered_words = [
                word.lower() for word in words
                if word.lower() not in stop_words and len(word) > 3 and word.isalpha()
            ]
            
            # Count frequency
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Return top keywords
            keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in keywords[:max_keywords]]
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    async def batch_analyze(self, texts: List[str], **kwargs) -> List[TextAnalysisResult]:
        """Analyze multiple texts concurrently"""        if not texts:
            return []
        
        tasks = [self.analyze(text, **kwargs) for text in texts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to analyze text {i}: {result}")
                # Create error result
                error_result = TextAnalysisResult(
                    text=texts[i],
                    cleaned_text="",
                    metadata={"error": str(result)}
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def clean_text(self, text: str, **options) -> str:
        """Clean text with specific options"""        cleaned = text
        
        # Remove HTML tags
        if options.get("remove_html", True):
            cleaned = self.patterns["html_tags"].sub("", cleaned)
        
        # Remove URLs
        if options.get("remove_urls", False):
            cleaned = self.patterns["url"].sub("", cleaned)
        
        # Remove social media elements
        if options.get("remove_hashtags", False):
            cleaned = self.patterns["hashtag"].sub("", cleaned)
        
        if options.get("remove_mentions", False):
            cleaned = self.patterns["mention"].sub("", cleaned)
        
        # Normalize whitespace
        if options.get("normalize_whitespace", True):
            cleaned = self.patterns["whitespace"].sub(" ", cleaned)
        
        # Convert case
        if options.get("lowercase", False):
            cleaned = cleaned.lower()
        elif options.get("uppercase", False):
            cleaned = cleaned.upper()
        
        # Remove punctuation
        if options.get("remove_punctuation", False):
            cleaned = self.patterns["punctuation"].sub("", cleaned)
        
        # Remove numbers
        if options.get("remove_numbers", False):
            cleaned = self.patterns["number"].sub("", cleaned)
        
        # Unicode normalization
        cleaned = unicodedata.normalize('NFKC', cleaned)
        
        return cleaned.strip()
    
    def get_word_frequency(self, text: str, top_n: int = 20) -> List[Tuple[str, int]]:
        """Get word frequency distribution"""        from collections import Counter
        
        words = self.clean_text(text, lowercase=True, remove_punctuation=True).split()
        
        # Filter out stopwords and short words
        try:
            from nltk.corpus import stopwords
            stop_words = set(stopwords.words('english'))
        except:
            stop_words = set()
        
        filtered_words = [
            word for word in words
            if len(word) > 2 and word not in stop_words and word.isalpha()
        ]
        
        return Counter(filtered_words).most_common(top_n)
    
    def generate_wordcloud(self, text: str, **kwargs) -> WordCloud:
        """Generate word cloud from text"""        cleaned_text = self.clean_text(
            text,
            lowercase=True,
            remove_punctuation=True,
            remove_urls=True
        )
        
        wordcloud_config = {
            "width": kwargs.get("width", 800),
            "height": kwargs.get("height", 400),
            "background_color": kwargs.get("background_color", "white"),
            "max_words": kwargs.get("max_words", 100),
            "colormap": kwargs.get("colormap", "viridis")
        }
        
        return WordCloud(**wordcloud_config).generate(cleaned_text)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""        return {
            "status": "healthy",
            "models_loaded": len(self._nlp_models),
            "spacy_available": "spacy_en" in self._nlp_models,
            "patterns_compiled": len(self.patterns),
            "executor_active": not self.executor._shutdown
        }
    
    def shutdown(self):
        """Shutdown the text analyzer"""        logger.info("Shutting down Text Analyzer")
        self.executor.shutdown(wait=True)

# Utility functions
def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity using simple overlap"""    from difflib import SequenceMatcher
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def extract_social_media_metrics(text: str) -> Dict[str, int]:
    """Extract social media specific metrics"""    patterns = {
        "hashtags": re.compile(r'#\w+'),
        "mentions": re.compile(r'@\w+'),
        "urls": re.compile(r'http[s]?://\S+'),
        "emojis": re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+')
    }
    
    return {
        name: len(pattern.findall(text))
        for name, pattern in patterns.items()
    }
