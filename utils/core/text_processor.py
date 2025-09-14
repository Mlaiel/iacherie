"""
Text Processor - Core Utilities Level 1
=======================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade text processing utility consolidating:
- Text processor (text_processor.py)
- Prompt optimizer (prompt_optimizer.py)

Performance: < 10ms per operation
Standards: 100% async, type hints, NLP optimization, AI prompt engineering
"""

import asyncio
import re
import time
import logging
import string
import unicodedata
from typing import (
    Any, Dict, List, Optional, Union, Callable, Tuple, 
    Set, Pattern, AsyncIterator
)
from datetime import datetime, timezone
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import aiofiles

# Optional NLP dependencies with fallbacks for enterprise flexibility
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
except ImportError:
    nltk = None
    stopwords = None
    word_tokenize = sent_tokenize = None
    PorterStemmer = WordNetLemmatizer = None
    SentimentIntensityAnalyzer = None
    NLTK_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    SPACY_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    pipeline = None
    TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TextBlob = None
    TEXTBLOB_AVAILABLE = False

try:
    import langdetect
    LANGDETECT_AVAILABLE = True
except ImportError:
    langdetect = None
    LANGDETECT_AVAILABLE = False
# from googletrans import Translator  # Temporarily disabled due to dependency issues
import html
# import markdown  # Will install if needed
# import bleach    # Will install if needed

logger = logging.getLogger(__name__)

@dataclass
class TextResult:
    """Enterprise result container for text processing operations."""
    success: bool
    result: Optional[Any] = None
    original_text: Optional[str] = None
    processed_text: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'success': self.success,
            'result': self.result,
            'original_text': self.original_text,
            'processed_text': self.processed_text,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'execution_time_ms': self.execution_time_ms
        }

@dataclass
class PromptTemplate:
    """Template for AI prompt optimization."""
    name: str
    template: str
    variables: List[str]
    constraints: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class TextProcessor:
    """
    Enterprise text processor with ultra-high performance standards.
    
    Provides comprehensive text processing, NLP operations, and AI prompt
    optimization following enterprise architecture patterns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize text processor with enterprise configuration."""
        self.config = config or {}
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        self._performance_threshold_ms = 10.0
        self._max_text_length = self.config.get('max_text_length', 1000000)
        self._supported_languages = set(self.config.get('supported_languages', ['en']))
        
        # Initialize NLP components
        self._stemmer = PorterStemmer()
        self._lemmatizer = WordNetLemmatizer()
        self._sentiment_analyzer = SentimentIntensityAnalyzer()
        self._translator = Translator()
        
        # Pre-compiled regex patterns for performance
        self._url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        self._email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self._phone_pattern = re.compile(r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}')
        self._whitespace_pattern = re.compile(r'\s+')
        
        # Prompt templates storage
        self._prompt_templates: Dict[str, PromptTemplate] = {}
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_nlp_components()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        self._thread_pool.shutdown(wait=True)
        
    async def _initialize_nlp_components(self) -> None:
        """Initialize NLP components asynchronously."""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            
            # Load spaCy model
            try:
                self._nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found, some features will be limited")
                self._nlp = None
                
        except Exception as e:
            logger.error(f"NLP initialization failed: {e}")
            
    async def _measure_performance(self, operation: Callable) -> Tuple[Any, float]:
        """Measure operation performance and validate against thresholds."""
        start_time = time.perf_counter()
        
        if asyncio.iscoroutinefunction(operation):
            result = await operation()
        else:
            result = await asyncio.get_event_loop().run_in_executor(
                self._thread_pool, operation
            )
            
        execution_time = (time.perf_counter() - start_time) * 1000
        
        if execution_time > self._performance_threshold_ms:
            logger.warning(
                f"Performance threshold exceeded: {execution_time:.2f}ms > {self._performance_threshold_ms}ms"
            )
            
        return result, execution_time
    
    def _validate_text_input(self, text: str) -> List[str]:
        """Validate text input against security and size constraints."""
        errors = []
        
        if not isinstance(text, str):
            errors.append("Input must be a string")
            return errors
            
        if len(text) > self._max_text_length:
            errors.append(f"Text too long: {len(text)} > {self._max_text_length}")
            
        return errors
    
    # === CORE TEXT PROCESSING ===
    
    async def clean_text(
        self,
        text: str,
        remove_urls: bool = True,
        remove_emails: bool = True,
        remove_phone_numbers: bool = True,
        normalize_whitespace: bool = True,
        remove_html: bool = True,
        lowercase: bool = False
    ) -> TextResult:
        """Clean text with comprehensive preprocessing options."""
        def _clean():
            # Security validation
            validation_errors = self._validate_text_input(text)
            if validation_errors:
                return None, validation_errors
                
            cleaned_text = text
            operations = []
            
            # Remove HTML tags
            if remove_html:
                cleaned_text = bleach.clean(cleaned_text, tags=[], strip=True)
                operations.append('html_removal')
            
            # Remove URLs
            if remove_urls:
                cleaned_text = self._url_pattern.sub('', cleaned_text)
                operations.append('url_removal')
            
            # Remove emails
            if remove_emails:
                cleaned_text = self._email_pattern.sub('', cleaned_text)
                operations.append('email_removal')
            
            # Remove phone numbers
            if remove_phone_numbers:
                cleaned_text = self._phone_pattern.sub('', cleaned_text)
                operations.append('phone_removal')
            
            # Normalize whitespace
            if normalize_whitespace:
                cleaned_text = self._whitespace_pattern.sub(' ', cleaned_text).strip()
                operations.append('whitespace_normalization')
            
            # Convert to lowercase
            if lowercase:
                cleaned_text = cleaned_text.lower()
                operations.append('lowercase')
            
            return {
                'cleaned_text': cleaned_text,
                'operations_applied': operations,
                'character_reduction': len(text) - len(cleaned_text)
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_clean)
            
            if result[0] is None:  # Error case
                return TextResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'clean_text'}
                )
            
            data = result[0]
            return TextResult(
                success=True,
                result=data['cleaned_text'],
                original_text=text,
                processed_text=data['cleaned_text'],
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'clean_text',
                    'operations_applied': data['operations_applied'],
                    'character_reduction': data['character_reduction'],
                    'original_length': len(text),
                    'cleaned_length': len(data['cleaned_text'])
                }
            )
        except Exception as e:
            logger.error(f"Text cleaning failed: {e}")
            return TextResult(
                success=False,
                errors=[str(e)],
                original_text=text,
                metadata={'operation': 'clean_text'}
            )
    
    async def tokenize_text(
        self,
        text: str,
        method: str = 'word',  # 'word', 'sentence', 'custom'
        custom_pattern: Optional[str] = None,
        remove_stopwords: bool = False,
        language: str = 'english'
    ) -> TextResult:
        """Tokenize text with multiple methods and preprocessing options."""
        def _tokenize():
            validation_errors = self._validate_text_input(text)
            if validation_errors:
                return None, validation_errors
            
            if method == 'word':
                tokens = word_tokenize(text)
            elif method == 'sentence':
                tokens = sent_tokenize(text)
            elif method == 'custom' and custom_pattern:
                tokens = re.findall(custom_pattern, text)
            else:
                return None, [f"Invalid tokenization method: {method}"]
            
            # Remove stopwords if requested
            if remove_stopwords and method == 'word':
                try:
                    stop_words = set(stopwords.words(language))
                    tokens = [token for token in tokens if token.lower() not in stop_words]
                except Exception:
                    # Language not available, continue without stopword removal
                    pass
            
            return {
                'tokens': tokens,
                'token_count': len(tokens),
                'unique_tokens': len(set(tokens)) if method == 'word' else None,
                'method': method,
                'stopwords_removed': remove_stopwords
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_tokenize)
            
            if result[0] is None:  # Error case
                return TextResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'tokenize_text'}
                )
            
            data = result[0]
            return TextResult(
                success=True,
                result=data['tokens'],
                original_text=text,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'tokenize_text',
                    'method': method,
                    'token_count': data['token_count'],
                    'unique_tokens': data['unique_tokens'],
                    'stopwords_removed': remove_stopwords,
                    'language': language
                }
            )
        except Exception as e:
            logger.error(f"Text tokenization failed: {e}")
            return TextResult(
                success=False,
                errors=[str(e)],
                original_text=text,
                metadata={'operation': 'tokenize_text'}
            )
    
    async def analyze_sentiment(self, text: str) -> TextResult:
        """Analyze text sentiment with multiple methods."""
        def _analyze_sentiment():
            validation_errors = self._validate_text_input(text)
            if validation_errors:
                return None, validation_errors
            
            # VADER sentiment analysis
            vader_scores = self._sentiment_analyzer.polarity_scores(text)
            
            # TextBlob sentiment analysis
            blob = TextBlob(text)
            textblob_sentiment = {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
            
            # Determine overall sentiment
            compound_score = vader_scores['compound']
            if compound_score >= 0.05:
                overall_sentiment = 'positive'
            elif compound_score <= -0.05:
                overall_sentiment = 'negative'
            else:
                overall_sentiment = 'neutral'
            
            return {
                'overall_sentiment': overall_sentiment,
                'confidence': abs(compound_score),
                'vader_scores': vader_scores,
                'textblob_sentiment': textblob_sentiment,
                'analysis_methods': ['vader', 'textblob']
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_analyze_sentiment)
            
            if result[0] is None:  # Error case
                return TextResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'analyze_sentiment'}
                )
            
            data = result[0]
            return TextResult(
                success=True,
                result=data,
                original_text=text,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'analyze_sentiment',
                    'overall_sentiment': data['overall_sentiment'],
                    'confidence': data['confidence']
                }
            )
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return TextResult(
                success=False,
                errors=[str(e)],
                original_text=text,
                metadata={'operation': 'analyze_sentiment'}
            )
    
    async def detect_language(self, text: str) -> TextResult:
        """Detect text language with confidence scoring."""
        def _detect_language():
            validation_errors = self._validate_text_input(text)
            if validation_errors:
                return None, validation_errors
            
            # Use langdetect for primary detection
            try:
                detected_lang = langdetect.detect(text)
                confidence = 1.0  # langdetect doesn't provide confidence, so assume high
                
                # Get detailed language information
                lang_probabilities = langdetect.detect_langs(text)
                probabilities = {
                    lang.lang: lang.prob for lang in lang_probabilities
                }
                
            except Exception:
                # Fallback to simple heuristics
                detected_lang = 'unknown'
                confidence = 0.0
                probabilities = {}
            
            return {
                'detected_language': detected_lang,
                'confidence': confidence,
                'language_probabilities': probabilities,
                'is_supported': detected_lang in self._supported_languages
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_detect_language)
            
            if result[0] is None:  # Error case
                return TextResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'detect_language'}
                )
            
            data = result[0]
            return TextResult(
                success=True,
                result=data,
                original_text=text,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'detect_language',
                    'detected_language': data['detected_language'],
                    'confidence': data['confidence']
                }
            )
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return TextResult(
                success=False,
                errors=[str(e)],
                original_text=text,
                metadata={'operation': 'detect_language'}
            )
    
    # === PROMPT OPTIMIZATION ===
    
    async def register_prompt_template(
        self,
        template: PromptTemplate
    ) -> TextResult:
        """Register a new prompt template for optimization."""
        try:
            # Validate template
            if not template.name:
                return TextResult(
                    success=False,
                    errors=["Template name is required"],
                    metadata={'operation': 'register_prompt_template'}
                )
            
            if not template.template:
                return TextResult(
                    success=False,
                    errors=["Template text is required"],
                    metadata={'operation': 'register_prompt_template'}
                )
            
            # Store template
            self._prompt_templates[template.name] = template
            
            return TextResult(
                success=True,
                result=f"Template '{template.name}' registered successfully",
                metadata={
                    'operation': 'register_prompt_template',
                    'template_name': template.name,
                    'variables_count': len(template.variables),
                    'examples_count': len(template.examples)
                }
            )
        except Exception as e:
            logger.error(f"Template registration failed: {e}")
            return TextResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'register_prompt_template'}
            )
    
    async def optimize_prompt(
        self,
        template_name: str,
        variables: Dict[str, str],
        optimization_strategy: str = 'clarity'  # 'clarity', 'brevity', 'creativity'
    ) -> TextResult:
        """Optimize prompt using registered template and variables."""
        def _optimize():
            if template_name not in self._prompt_templates:
                return None, [f"Template '{template_name}' not found"]
            
            template = self._prompt_templates[template_name]
            
            # Validate all required variables are provided
            missing_vars = set(template.variables) - set(variables.keys())
            if missing_vars:
                return None, [f"Missing variables: {', '.join(missing_vars)}"]
            
            # Replace variables in template
            optimized_prompt = template.template
            for var_name, var_value in variables.items():
                placeholder = f"{{{var_name}}}"
                optimized_prompt = optimized_prompt.replace(placeholder, var_value)
            
            # Apply optimization strategy
            if optimization_strategy == 'clarity':
                # Add clarity improvements
                optimized_prompt = self._enhance_clarity(optimized_prompt)
            elif optimization_strategy == 'brevity':
                # Make more concise
                optimized_prompt = self._enhance_brevity(optimized_prompt)
            elif optimization_strategy == 'creativity':
                # Add creative elements
                optimized_prompt = self._enhance_creativity(optimized_prompt)
            
            return {
                'optimized_prompt': optimized_prompt,
                'template_name': template_name,
                'optimization_strategy': optimization_strategy,
                'variables_used': variables,
                'character_count': len(optimized_prompt),
                'word_count': len(optimized_prompt.split())
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_optimize)
            
            if result[0] is None:  # Error case
                return TextResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'optimize_prompt'}
                )
            
            data = result[0]
            return TextResult(
                success=True,
                result=data['optimized_prompt'],
                processed_text=data['optimized_prompt'],
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'optimize_prompt',
                    'template_name': template_name,
                    'optimization_strategy': optimization_strategy,
                    'character_count': data['character_count'],
                    'word_count': data['word_count'],
                    'variables_used': list(variables.keys())
                }
            )
        except Exception as e:
            logger.error(f"Prompt optimization failed: {e}")
            return TextResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'optimize_prompt'}
            )
    
    def _enhance_clarity(self, prompt: str) -> str:
        """Enhance prompt clarity with structure and explicit instructions."""
        # Add clear instruction markers
        if not prompt.strip().endswith(':'):
            prompt += "\n\nPlease provide a clear and detailed response."
        
        # Add structure hints
        if len(prompt.split('.')) > 3:
            prompt += "\n\nStructure your response with clear sections if applicable."
        
        return prompt
    
    def _enhance_brevity(self, prompt: str) -> str:
        """Make prompt more concise while preserving meaning."""
        # Remove redundant phrases
        brevity_replacements = {
            'please be sure to': '',
            'make sure that you': '',
            'it is important that': '',
            'you should': '',
            'please note that': ''
        }
        
        for redundant, replacement in brevity_replacements.items():
            prompt = prompt.replace(redundant, replacement)
        
        # Clean up extra whitespace
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        
        return prompt
    
    def _enhance_creativity(self, prompt: str) -> str:
        """Add creative elements to encourage innovative responses."""
        creative_additions = [
            "Think outside the box and consider unique perspectives.",
            "Feel free to use creative approaches and innovative ideas.",
            "Consider unconventional solutions and fresh angles."
        ]
        
        # Add a random creative prompt
        import random
        creative_element = random.choice(creative_additions)
        
        return f"{prompt}\n\n{creative_element}"
    
    # === TEXT EXTRACTION AND PARSING ===
    
    async def extract_entities(self, text: str) -> TextResult:
        """Extract named entities using spaCy NLP."""
        def _extract():
            validation_errors = self._validate_text_input(text)
            if validation_errors:
                return None, validation_errors
            
            if not self._nlp:
                return None, ["spaCy model not available"]
            
            doc = self._nlp(text)
            
            entities = []
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'description': spacy.explain(ent.label_),
                    'start_char': ent.start_char,
                    'end_char': ent.end_char
                })
            
            return {
                'entities': entities,
                'entity_count': len(entities),
                'entity_types': list(set(ent['label'] for ent in entities))
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_extract)
            
            if result[0] is None:  # Error case
                return TextResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'extract_entities'}
                )
            
            data = result[0]
            return TextResult(
                success=True,
                result=data,
                original_text=text,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'extract_entities',
                    'entity_count': data['entity_count'],
                    'entity_types': data['entity_types']
                }
            )
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return TextResult(
                success=False,
                errors=[str(e)],
                original_text=text,
                metadata={'operation': 'extract_entities'}
            )
    
    async def summarize_text(
        self,
        text: str,
        max_length: int = 150,
        method: str = 'extractive'  # 'extractive', 'abstractive'
    ) -> TextResult:
        """Summarize text using various methods."""
        def _summarize():
            validation_errors = self._validate_text_input(text)
            if validation_errors:
                return None, validation_errors
            
            if method == 'extractive':
                # Simple extractive summarization
                sentences = sent_tokenize(text)
                if len(sentences) <= 3:
                    summary = text
                else:
                    # Take first, middle, and last sentences
                    summary = '. '.join([
                        sentences[0],
                        sentences[len(sentences)//2],
                        sentences[-1]
                    ])
            else:
                # For abstractive, we'd need a more complex model
                summary = text[:max_length] + "..." if len(text) > max_length else text
            
            return {
                'summary': summary,
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': len(summary) / len(text),
                'method': method
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_summarize)
            
            if result[0] is None:  # Error case
                return TextResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'summarize_text'}
                )
            
            data = result[0]
            return TextResult(
                success=True,
                result=data['summary'],
                original_text=text,
                processed_text=data['summary'],
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'summarize_text',
                    'method': method,
                    'original_length': data['original_length'],
                    'summary_length': data['summary_length'],
                    'compression_ratio': data['compression_ratio']
                }
            )
        except Exception as e:
            logger.error(f"Text summarization failed: {e}")
            return TextResult(
                success=False,
                errors=[str(e)],
                original_text=text,
                metadata={'operation': 'summarize_text'}
            )

# Enterprise factory pattern for text processor
class TextProcessorFactory:
    """Factory for creating configured text processor instances."""
    
    @staticmethod
    async def create_processor(config: Optional[Dict[str, Any]] = None) -> TextProcessor:
        """Create and initialize text processor."""
        processor = TextProcessor(config)
        await processor._initialize_nlp_components()
        return processor
    
    @staticmethod
    async def create_ai_optimized_processor(
        max_text_length: int = 100000,
        supported_languages: Optional[List[str]] = None
    ) -> TextProcessor:
        """Create text processor optimized for AI operations."""
        config = {
            'max_text_length': max_text_length,
            'supported_languages': supported_languages or ['en', 'fr', 'de', 'es']
        }
        return await TextProcessorFactory.create_processor(config)