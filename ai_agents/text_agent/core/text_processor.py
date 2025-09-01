"""Text Processor - Advanced Text Processing and Analysis Engine

Industrial-grade text processing, cleaning, normalization, and feature extraction
for content creators with enterprise performance and security.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import re
import string
import unicodedata
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import html
import ftfy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import SnowballStemmer, WordNetLemmatizer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
import spacy
from textblob import TextBlob
import contractions
from bs4 import BeautifulSoup
import numpy as np

# Create ProcessingError if it doesn't exist
class ProcessingError(Exception):
    """
Exception raised for text processing errors"""
    pass

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
    nltk.data.find('averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('maxent_ne_chunker')
except LookupError:
    nltk.download('maxent_ne_chunker')

try:
    nltk.data.find('words')
except LookupError:
    nltk.download('words')

logger = logging.getLogger(__name__)

class ProcessingLevel(Enum):
    """
Text processing complexity levels"""

    MINIMAL = "minimal"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    COMPREHENSIVE = "comprehensive"

class TextFormat(Enum):
    """Text format types"""

    PLAIN_TEXT = "plain_text"
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    XML = "xml"
    RTF = "rtf"

@dataclass
class ProcessingOptions:
    """Text processing configuration options"""
    level: ProcessingLevel = ProcessingLevel.STANDARD
    remove_html: bool = True
    remove_urls: bool = True
    remove_emails: bool = True
    remove_phone_numbers: bool = True
    remove_special_chars: bool = False
    normalize_whitespace: bool = True
    expand_contractions: bool = True
    fix_encoding: bool = True
    remove_stopwords: bool = False
    apply_stemming: bool = False
    apply_lemmatization: bool = False
    preserve_case: bool = False
    min_word_length: int = 1
    max_word_length: int = 50
    languages: List[str] = field(default_factory=lambda: ['en'])

@dataclass
class ProcessingResult:
    """
Text processing results and metadata"""
    original_text: str
    processed_text: str
    original_length: int
    processed_length: int
    removed_elements: Dict[str, int]
    processing_time: float
    options_used: ProcessingOptions
    metadata: Dict[str, Any] = field(default_factory=dict)

class TextProcessor:
    """
    Industrial-grade text processing engine with comprehensive cleaning and normalization
    """
    
    def __init__(self, default_options: Optional[ProcessingOptions] = None):
        self.default_options = default_options or ProcessingOptions()
        
        # Initialize language-specific resources
        self.stemmers = {}
        self.stopwords_sets = {}
        self.lemmatizer = WordNetLemmatizer()
        
        # Pre-compile common regex patterns
        self._compile_regex_patterns()
        
        # Initialize spaCy models for advanced processing
        self.nlp_models = {}
        
        logger.info("TextProcessor initialized with advanced processing capabilities")
    
    def _compile_regex_patterns(self):
        """Pre-compile commonly used regex patterns for performance"""
        self.patterns = {
            'url': re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'),
            'html_tags': re.compile(r'<[^>]+>'),
            'multiple_spaces': re.compile(r'\s+'),
            'special_chars': re.compile(r'[^\w\s\.\,\!\?\;\:\-\'\"]'),
            'numbers': re.compile(r'\b\d+\b'),
            'repeated_chars': re.compile(r'(.)\1{2,}'),
            'social_mentions': re.compile(r'@\w+'),
            'hashtags': re.compile(r'#\w+'),
            'markdown_links': re.compile(r'\[([^\]]+)\]\([^\)]+\)'),
            'markdown_formatting': re.compile(r'[\*\_\`\~\[\]]+')
        }
    
    async def process_text(
        self,
        text: str,
        options: Optional[ProcessingOptions] = None
    ) -> ProcessingResult:
        """
        Process text with comprehensive cleaning and normalization
        
        Args:
            text: Input text to process
            options: Processing configuration options
            
        Returns:
            ProcessingResult: Processing results and metadata
        """
        start_time = time.time()
        options = options or self.default_options
        original_text = text
        original_length = len(text)
        
        removed_elements = {
            'html_tags': 0,
            'urls': 0,
            'emails': 0,
            'phone_numbers': 0,
            'special_chars': 0,
            'stopwords': 0,
            'short_words': 0,
            'long_words': 0
        }
        
        try:
            # Fix encoding issues
            if options.fix_encoding:
                text = await self._fix_encoding(text)
            
            # Remove HTML content
            if options.remove_html:
                text, html_count = await self._remove_html(text)
                removed_elements['html_tags'] = html_count
            
            # Remove URLs
            if options.remove_urls:
                text, url_count = await self._remove_urls(text)
                removed_elements['urls'] = url_count
            
            # Remove email addresses
            if options.remove_emails:
                text, email_count = await self._remove_emails(text)
                removed_elements['emails'] = email_count
            
            # Remove phone numbers
            if options.remove_phone_numbers:
                text, phone_count = await self._remove_phone_numbers(text)
                removed_elements['phone_numbers'] = phone_count
            
            # Expand contractions
            if options.expand_contractions:
                text = await self._expand_contractions(text)
            
            # Remove special characters
            if options.remove_special_chars:
                text, special_count = await self._remove_special_chars(text)
                removed_elements['special_chars'] = special_count
            
            # Normalize whitespace
            if options.normalize_whitespace:
                text = await self._normalize_whitespace(text)
            
            # Apply advanced processing based on level
            if options.level in [ProcessingLevel.AGGRESSIVE, ProcessingLevel.COMPREHENSIVE]:
                text = await self._advanced_processing(text, options)
            
            # Remove stopwords
            if options.remove_stopwords:
                text, stopword_count = await self._remove_stopwords(text, options.languages)
                removed_elements['stopwords'] = stopword_count
            
            # Apply stemming
            if options.apply_stemming:
                text = await self._apply_stemming(text, options.languages[0])
            
            # Apply lemmatization
            if options.apply_lemmatization:
                text = await self._apply_lemmatization(text)
            
            # Filter by word length
            text, short_removed, long_removed = await self._filter_by_word_length(
                text, options.min_word_length, options.max_word_length
            )
            removed_elements['short_words'] = short_removed
            removed_elements['long_words'] = long_removed
            
            # Handle case normalization
            if not options.preserve_case:
                text = text.lower()
            
            processing_time = time.time() - start_time
            
            result = ProcessingResult(
                original_text=original_text,
                processed_text=text.strip(),
                original_length=original_length,
                processed_length=len(text.strip()),
                removed_elements=removed_elements,
                processing_time=processing_time,
                options_used=options,
                metadata={
                    'compression_ratio': len(text.strip()) / original_length if original_length > 0 else 0,
                    'processing_level': options.level.value,
                    'languages_processed': options.languages
                }
            )
            
            logger.debug(f"Text processed: {original_length} -> {len(text.strip())} chars ({processing_time:.3f}s)")
            return result
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            raise ProcessingError(f"Text processing failed: {e}")
    
    async def _fix_encoding(self, text: str) -> str:
        """Fix common encoding issues"""
        try:
            # Use ftfy to fix encoding issues
            text = ftfy.fix_text(text)
            
            # Normalize unicode characters
            text = unicodedata.normalize('NFKD', text)
            
            # Remove or replace problematic characters
            text = text.encode('ascii', 'ignore').decode('ascii')
            
            return text
        except Exception as e:
            logger.warning(f"Encoding fix failed: {e}")
            return text
    
    async def _remove_html(self, text: str) -> Tuple[str, int]:
        """Remove HTML tags and decode HTML entities"""
        try:
            # Count HTML tags before removal
            html_tags = self.patterns['html_tags'].findall(text)
            tag_count = len(html_tags)
            
            # Parse HTML and extract text
            soup = BeautifulSoup(text, 'html.parser')
            clean_text = soup.get_text()
            
            # Decode HTML entities
            clean_text = html.unescape(clean_text)
            
            return clean_text, tag_count
            
        except Exception as e:
            logger.warning(f"HTML removal failed: {e}")
            # Fallback to regex
            clean_text = self.patterns['html_tags'].sub('', text)
            return clean_text, 0
    
    async def _remove_urls(self, text: str) -> Tuple[str, int]:
        """Remove URLs from text"""
        urls = self.patterns['url'].findall(text)
        clean_text = self.patterns['url'].sub('', text)
        return clean_text, len(urls)
    
    async def _remove_emails(self, text: str) -> Tuple[str, int]:
        """
Remove email addresses from text"""
        emails = self.patterns['email'].findall(text)
        clean_text = self.patterns['email'].sub('', text)
        return clean_text, len(emails)
    
    async def _remove_phone_numbers(self, text: str) -> Tuple[str, int]:
        """
Remove phone numbers from text"""
        phones = self.patterns['phone'].findall(text)
        clean_text = self.patterns['phone'].sub('', text)
        return clean_text, len(phones)
    
    async def _expand_contractions(self, text: str) -> str:
        """
Expand English contractions"""
        try:
            return contractions.fix(text)
        except Exception as e:
            logger.warning(f"Contraction expansion failed: {e}")
            return text
    
    async def _remove_special_chars(self, text: str) -> Tuple[str, int]:
        """Remove special characters while preserving basic punctuation"""
        special_chars = self.patterns['special_chars'].findall(text)
        clean_text = self.patterns['special_chars'].sub(' ', text)
        return clean_text, len(special_chars)
    
    async def _normalize_whitespace(self, text: str) -> str:
        """
Normalize whitespace characters"""
        # Replace multiple spaces with single space
        text = self.patterns['multiple_spaces'].sub(' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Normalize line breaks
        text = re.sub(r'\r\n|\r|\n', ' ', text)
        
        return text
    
    async def _advanced_processing(self, text: str, options: ProcessingOptions) -> str:
        """
Apply advanced text processing techniques"""
        # Remove repeated characters (e.g., "sooooo" -> "so")
        text = self.patterns['repeated_chars'].sub(r'\1\1', text)
        
        # Remove social media mentions and hashtags for certain contexts
        if options.level == ProcessingLevel.COMPREHENSIVE:
            text = self.patterns['social_mentions'].sub('', text)
            text = self.patterns['hashtags'].sub('', text)
        
        # Clean markdown formatting
        text = self.patterns['markdown_links'].sub(r'\1', text)
        text = self.patterns['markdown_formatting'].sub('', text)
        
        return text
    
    async def _remove_stopwords(self, text: str, languages: List[str]) -> Tuple[str, int]:
        """Remove stopwords for specified languages"""
        try:
            # Get stopwords for all specified languages
            all_stopwords = set()
            for lang in languages:
                lang_code = self._get_nltk_language_code(lang)
                if lang_code:
                    all_stopwords.update(stopwords.words(lang_code))
            
            # Tokenize and filter
            words = word_tokenize(text)
            filtered_words = [word for word in words if word.lower() not in all_stopwords]
            
            stopwords_removed = len(words) - len(filtered_words)
            clean_text = ' '.join(filtered_words)
            
            return clean_text, stopwords_removed
            
        except Exception as e:
            logger.warning(f"Stopword removal failed: {e}")
            return text, 0
    
    async def _apply_stemming(self, text: str, language: str) -> str:
        """Apply stemming to reduce words to their root forms"""
        try:
            lang_code = self._get_nltk_language_code(language)
            if lang_code not in self.stemmers:
                self.stemmers[lang_code] = SnowballStemmer(lang_code)
            
            stemmer = self.stemmers[lang_code]
            words = word_tokenize(text)
            stemmed_words = [stemmer.stem(word) for word in words]
            
            return ' '.join(stemmed_words)
            
        except Exception as e:
            logger.warning(f"Stemming failed: {e}")
            return text
    
    async def _apply_lemmatization(self, text: str) -> str:
        """Apply lemmatization to reduce words to their base forms"""
        try:
            words = word_tokenize(text)
            pos_tags = pos_tag(words)
            
            lemmatized_words = []
            for word, pos in pos_tags:
                # Convert POS tag to WordNet format
                wordnet_pos = self._get_wordnet_pos(pos)
                lemmatized_word = self.lemmatizer.lemmatize(word, wordnet_pos)
                lemmatized_words.append(lemmatized_word)
            
            return ' '.join(lemmatized_words)
            
        except Exception as e:
            logger.warning(f"Lemmatization failed: {e}")
            return text
    
    async def _filter_by_word_length(
        self,
        text: str,
        min_length: int,
        max_length: int
    ) -> Tuple[str, int, int]:
        """Filter words by length"""
        words = text.split()
        short_words_removed = 0
        long_words_removed = 0
        
        filtered_words = []
        for word in words:
            if len(word) < min_length:
                short_words_removed += 1
            elif len(word) > max_length:
                long_words_removed += 1
            else:
                filtered_words.append(word)
        
        return ' '.join(filtered_words), short_words_removed, long_words_removed
    
    def _get_nltk_language_code(self, language: str) -> Optional[str]:
        """
Convert language code to NLTK format"""
        lang_map = {
            'en': 'english',
            'fr': 'french',
            'de': 'german',
            'es': 'spanish',
            'it': 'italian',
            'pt': 'portuguese',
            'ru': 'russian',
            'nl': 'dutch',
            'sv': 'swedish',
            'no': 'norwegian',
            'da': 'danish',
            'fi': 'finnish'
        }
        return lang_map.get(language.lower())
    
    def _get_wordnet_pos(self, treebank_tag: str) -> str:
        """
Convert TreeBank POS tag to WordNet POS tag"""
        if treebank_tag.startswith('J'):
            return 'a'  # adjective
        elif treebank_tag.startswith('V'):
            return 'v'  # verb
        elif treebank_tag.startswith('N'):
            return 'n'  # noun
        elif treebank_tag.startswith('R'):
            return 'r'  # adverb
        else:
            return 'n'  # default to noun


class TextAnalyzer:
    """
    Advanced text analysis engine for extracting insights and statistics
    """
    
    def __init__(self):
        self.processor = TextProcessor()
        logger.info("TextAnalyzer initialized")
    
    async def analyze_text_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze text complexity and readability"""
        try:
            # Basic statistics
            words = text.split()
            sentences = sent_tokenize(text)
            paragraphs = text.split('\n\n')
            
            # Calculate complexity metrics
            avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
            avg_syllables_per_word = await self._calculate_avg_syllables(words)
            
            # Lexical diversity (Type-Token Ratio)
            unique_words = set(word.lower() for word in words if word.isalpha())
            lexical_diversity = len(unique_words) / len(words) if words else 0
            
            # Sentence length variation
            sentence_lengths = [len(sent.split()) for sent in sentences]
            sentence_length_variance = np.var(sentence_lengths) if sentence_lengths else 0
            
            return {
                'total_words': len(words),
                'total_sentences': len(sentences),
                'total_paragraphs': len([p for p in paragraphs if p.strip()]),
                'avg_words_per_sentence': avg_words_per_sentence,
                'avg_syllables_per_word': avg_syllables_per_word,
                'lexical_diversity': lexical_diversity,
                'sentence_length_variance': sentence_length_variance,
                'unique_words': len(unique_words),
                'complexity_score': await self._calculate_complexity_score(
                    avg_words_per_sentence, avg_syllables_per_word, lexical_diversity
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing text complexity: {e}")
            return {}
    
    async def extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive linguistic features"""
        try:
            # Tokenize text
            words = word_tokenize(text)
            sentences = sent_tokenize(text)
            
            # POS tagging
            pos_tags = pos_tag(words)
            pos_distribution = {}
            for word, pos in pos_tags:
                pos_distribution[pos] = pos_distribution.get(pos, 0) + 1
            
            # Named entity recognition
            entities = ne_chunk(pos_tags)
            named_entities = []
            for chunk in entities:
                if hasattr(chunk, 'label'):
                    entity_text = ' '.join([token for token, pos in chunk.leaves()])
                    named_entities.append({
                        'text': entity_text,
                        'label': chunk.label()
                    })
            
            # Calculate linguistic ratios
            total_words = len(words)
            noun_ratio = sum(1 for _, pos in pos_tags if pos.startswith('N')) / total_words
            verb_ratio = sum(1 for _, pos in pos_tags if pos.startswith('V')) / total_words
            adj_ratio = sum(1 for _, pos in pos_tags if pos.startswith('J')) / total_words
            adv_ratio = sum(1 for _, pos in pos_tags if pos.startswith('R')) / total_words
            
            return {
                'pos_distribution': pos_distribution,
                'named_entities': named_entities,
                'linguistic_ratios': {
                    'noun_ratio': noun_ratio,
                    'verb_ratio': verb_ratio,
                    'adjective_ratio': adj_ratio,
                    'adverb_ratio': adv_ratio
                },
                'total_tokens': total_words,
                'total_sentences': len(sentences)
            }
            
        except Exception as e:
            logger.error(f"Error extracting linguistic features: {e}")
            return {}
    
    async def _calculate_avg_syllables(self, words: List[str]) -> float:
        """Calculate average syllables per word"""
        if not words:
            return 0.0
        
        total_syllables = 0
        for word in words:
            if word.isalpha():
                # Simple syllable counting heuristic
                syllables = max(1, len(re.findall(r'[aeiouyAEIOUY]', word)))
                total_syllables += syllables
        
        return total_syllables / len(words)
    
    async def _calculate_complexity_score(
        self,
        avg_words_per_sentence: float,
        avg_syllables_per_word: float,
        lexical_diversity: float
    ) -> float:
        """
Calculate overall text complexity score"""
        # Normalize metrics to 0-1 scale and combine
        sentence_complexity = min(1.0, avg_words_per_sentence / 25)  # Assuming 25 words = high complexity
        syllable_complexity = min(1.0, avg_syllables_per_word / 3)   # Assuming 3+ syllables = complex
        diversity_complexity = lexical_diversity  # Already 0-1
        
        # Weighted combination
        complexity_score = (
            sentence_complexity * 0.4 +
            syllable_complexity * 0.3 +
            diversity_complexity * 0.3
        )
        
        return complexity_score
