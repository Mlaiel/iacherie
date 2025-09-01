"""Text Transformer - Professional text processing for IA Influencer Agent Platform
=================================================================================

Advanced text transformation, analysis, and conversion capabilities
for creators' text content workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""
import asyncio
import logging
import os
import tempfile
import re
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json
import time
import chardet
import hashlib

try:
    import nltk
    from transformers import pipeline, AutoTokenizer, AutoModel
    import spacy
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    TEXT_LIBS_AVAILABLE = True
except ImportError:
    TEXT_LIBS_AVAILABLE = False
    logging.warning("Text processing libraries not available. Some features may be limited.")

logger = logging.getLogger(__name__)


class TextFormat(Enum):
    """Supported text formats."""
    TXT = "txt"
    JSON = "json"
    XML = "xml"
    HTML = "html"
    MARKDOWN = "md"
    CSV = "csv"
    YAML = "yaml"
    RTF = "rtf"


class Language(Enum):
    """Supported languages."""
    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    AUTO = "auto"


class TextProcessingMode(Enum):
    """Text processing modes."""
    CLEAN = "clean"
    NORMALIZE = "normalize"
    TRANSLATE = "translate"
    SUMMARIZE = "summarize"
    SENTIMENT = "sentiment"
    KEYWORDS = "keywords"
    ENTITIES = "entities"
    ENHANCE = "enhance"


@dataclass
class TextSettings:
    """Text processing settings."""
    format: TextFormat = TextFormat.TXT
    encoding: str = "utf-8"
    language: Language = Language.AUTO
    processing_modes: List[TextProcessingMode] = None
    
    # Translation settings
    target_language: Optional[Language] = None
    
    # Cleaning settings
    remove_html: bool = True
    remove_urls: bool = False
    remove_emails: bool = False
    remove_phone_numbers: bool = False
    remove_extra_whitespace: bool = True
    normalize_unicode: bool = True
    
    # Enhancement settings
    fix_spelling: bool = False
    improve_grammar: bool = False
    enhance_readability: bool = False
    
    # Analysis settings
    extract_keywords: bool = False
    extract_entities: bool = False
    sentiment_analysis: bool = False
    readability_analysis: bool = False
    
    # Summarization settings
    summary_ratio: float = 0.3
    max_summary_length: Optional[int] = None


@dataclass
class TextMetadata:
    """Text file metadata."""
    encoding: Optional[str] = None
    language: Optional[str] = None
    char_count: int = 0
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    reading_time_minutes: float = 0.0
    readability_score: Optional[float] = None
    grade_level: Optional[float] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    keywords: Optional[List[str]] = None
    named_entities: Optional[List[Dict[str, str]]] = None
    size: Optional[int] = None
    hash: Optional[str] = None


class TextTransformer:
    """
    Professional text transformation engine for the IA Influencer Agent Platform.
    
    Provides advanced text processing, analysis, and conversion capabilities
    optimized for creator content workflows.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        temp_dir: Optional[str] = None
    ):
        """
        Initialize text transformer.
        
        Args:
            config: Configuration options
            temp_dir: Temporary directory for processing
        """
        self.config = config or {}
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "text_transform"
        
        # Create temp directory
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize NLP models if available
        self.nlp_models = {}
        self.pipelines = {}
        
        if TEXT_LIBS_AVAILABLE:
            self._init_nlp_models()
        
        logger.info("TextTransformer initialized")
    
    def _init_nlp_models(self):
        """Initialize NLP models and pipelines."""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('wordnet', quiet=True)
            
            # Initialize spaCy models for common languages
            try:
                self.nlp_models['en'] = spacy.load('en_core_web_sm')
            except OSError:
                logger.warning("English spaCy model not available")
            
            # Initialize transformer pipelines
            self.pipelines['sentiment'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            self.pipelines['summarization'] = pipeline(
                "summarization",
                model="facebook/bart-large-cnn"
            )
            
            self.pipelines['translation'] = pipeline(
                "translation",
                model="Helsinki-NLP/opus-mt-en-fr"  # Example model
            )
            
        except Exception as e:
            logger.warning(f"Could not initialize all NLP models: {e}")
    
    async def transform(self, request) -> Any:
        """
        Transform text based on request configuration.
        
        Args:
            request: Transformation request with text settings
            
        Returns:
            TransformationResult with processing metrics
        """
        start_time = time.time()
        
        try:
            # Parse request
            input_path = Path(request.input_path)
            settings = self._parse_text_settings(request)
            
            # Generate output path
            output_path = self._generate_output_path(input_path, settings, request.output_path)
            
            # Read input text
            text_content, input_encoding = await self._read_text_file(input_path)
            input_size = len(text_content.encode('utf-8'))
            
            # Get input metadata
            input_metadata = await self.get_metadata(text_content)
            input_metadata.size = input_path.stat().st_size
            
            # Process text
            processed_text = await self._process_text(text_content, settings)
            
            # Apply enhancements if requested
            if request.enhance_quality:
                processed_text = await self._enhance_text(processed_text, settings)
            
            # Save processed text
            await self._save_text_file(processed_text, output_path, settings)
            
            # Get output metadata
            output_metadata = await self.get_metadata(processed_text)
            output_size = len(processed_text.encode('utf-8'))
            
            # Calculate metrics
            compression_ratio = (input_size - output_size) / input_size if input_size > 0 else 0.0
            
            return type('TransformationResult', (), {
                'success': True,
                'output_path': str(output_path),
                'input_size': input_size,
                'output_size': output_size,
                'compression_ratio': compression_ratio,
                'metadata': {
                    'input': input_metadata.__dict__,
                    'output': output_metadata.__dict__,
                    'settings': settings.__dict__
                },
                'processing_time': time.time() - start_time
            })()
            
        except Exception as e:
            logger.error(f"Text transformation failed: {str(e)}")
            return type('TransformationResult', (), {
                'success': False,
                'error_message': str(e),
                'processing_time': time.time() - start_time
            })()
    
    async def convert(
        self,
        input_path: str,
        output_path: str,
        format: Union[str, TextFormat] = TextFormat.TXT,
        encoding: str = "utf-8",
        **kwargs
    ) -> bool:
        """
        Convert text file to specified format.
        
        Args:
            input_path: Input text file path
            output_path: Output text file path
            format: Target text format
            encoding: Output encoding
            **kwargs: Additional settings
            
        Returns:
            Success status
        """
        settings = TextSettings(
            format=format if isinstance(format, TextFormat) else TextFormat(format),
            encoding=encoding,
            **kwargs
        )
        
        try:
            # Read input text
            text_content, _ = await self._read_text_file(Path(input_path))
            
            # Process text
            processed_text = await self._process_text(text_content, settings)
            
            # Save text
            await self._save_text_file(processed_text, Path(output_path), settings)
            return True
            
        except Exception as e:
            logger.error(f"Text conversion failed: {str(e)}")
            return False
    
    async def analyze(
        self,
        text: str,
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze text and extract insights.
        
        Args:
            text: Text to analyze
            analysis_options: Analysis configuration
            
        Returns:
            Analysis results
        """
        try:
            options = analysis_options or {}
            results = {}
            
            # Basic statistics
            results['char_count'] = len(text)
            results['word_count'] = len(text.split())
            results['sentence_count'] = len(re.split(r'[.!?]+', text))
            results['paragraph_count'] = len([p for p in text.split('\n\n') if p.strip()])
            
            if TEXT_LIBS_AVAILABLE:
                # Sentiment analysis
                if options.get('sentiment', True):
                    sentiment = await self._analyze_sentiment(text)
                    results['sentiment'] = sentiment
                
                # Readability analysis
                if options.get('readability', True):
                    readability = await self._analyze_readability(text)
                    results['readability'] = readability
                
                # Keyword extraction
                if options.get('keywords', True):
                    keywords = await self._extract_keywords(text)
                    results['keywords'] = keywords
                
                # Named entity recognition
                if options.get('entities', True):
                    entities = await self._extract_entities(text)
                    results['entities'] = entities
                
                # Language detection
                language = await self._detect_language(text)
                results['language'] = language
            
            return results
            
        except Exception as e:
            logger.error(f"Text analysis failed: {str(e)}")
            return {}
    
    async def translate(
        self,
        text: str,
        target_language: Union[str, Language],
        source_language: Union[str, Language] = Language.AUTO
    ) -> str:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language
            source_language: Source language (auto-detect if AUTO)
            
        Returns:
            Translated text
        """
        try:
            if not TEXT_LIBS_AVAILABLE:
                logger.warning("Translation requires transformers library")
                return text
            
            # Detect source language if auto
            if source_language == Language.AUTO:
                detected_lang = await self._detect_language(text)
                source_language = Language(detected_lang) if detected_lang else Language.ENGLISH
            
            # Convert to string if enum
            if isinstance(target_language, Language):
                target_language = target_language.value
            if isinstance(source_language, Language):
                source_language = source_language.value
            
            # Use translation pipeline
            if 'translation' in self.pipelines:
                # This is a simplified example - in practice, you'd need
                # language-specific translation models
                result = self.pipelines['translation'](text)
                return result[0]['translation_text']
            
            return text
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            return text
    
    async def summarize(
        self,
        text: str,
        ratio: float = 0.3,
        max_length: Optional[int] = None
    ) -> str:
        """
        Summarize text content.
        
        Args:
            text: Text to summarize
            ratio: Summary ratio (0.1 = 10% of original)
            max_length: Maximum summary length
            
        Returns:
            Summarized text
        """
        try:
            if not TEXT_LIBS_AVAILABLE:
                logger.warning("Summarization requires transformers library")
                return text
            
            if 'summarization' in self.pipelines:
                # Calculate target length
                if not max_length:
                    word_count = len(text.split())
                    max_length = max(50, int(word_count * ratio))
                
                # Ensure text is not too short
                if len(text.split()) < 50:
                    return text
                
                result = self.pipelines['summarization'](
                    text,
                    max_length=max_length,
                    min_length=max(10, max_length // 4),
                    do_sample=False
                )
                return result[0]['summary_text']
            
            # Fallback: extractive summarization
            return await self._extractive_summarization(text, ratio)
            
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            return text
    
    async def get_metadata(self, text: str) -> TextMetadata:
        """
        Extract comprehensive text metadata.
        
        Args:
            text: Text content
            
        Returns:
            TextMetadata object
        """
        try:
            metadata = TextMetadata()
            
            # Basic statistics
            metadata.char_count = len(text)
            metadata.word_count = len(text.split())
            metadata.sentence_count = len(re.split(r'[.!?]+', text))
            metadata.paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
            
            # Reading time (average 200 WPM)
            metadata.reading_time_minutes = metadata.word_count / 200.0
            
            # Generate hash
            metadata.hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            
            if TEXT_LIBS_AVAILABLE:
                # Language detection
                metadata.language = await self._detect_language(text)
                
                # Readability analysis
                if metadata.sentence_count > 0:
                    try:
                        metadata.readability_score = flesch_reading_ease(text)
                        metadata.grade_level = flesch_kincaid_grade(text)
                    except:
                        pass
                
                # Sentiment analysis
                sentiment = await self._analyze_sentiment(text)
                if sentiment:
                    metadata.sentiment_score = sentiment.get('score')
                    metadata.sentiment_label = sentiment.get('label')
                
                # Extract keywords
                metadata.keywords = await self._extract_keywords(text, max_keywords=10)
                
                # Extract named entities
                metadata.named_entities = await self._extract_entities(text)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return TextMetadata()
    
    async def _read_text_file(self, file_path: Path) -> Tuple[str, str]:
        """Read text file with encoding detection."""
        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding_result = chardet.detect(raw_data)
                encoding = encoding_result['encoding'] or 'utf-8'
            
            # Read with detected encoding
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return content, encoding
            
        except Exception as e:
            # Fallback to utf-8
            logger.warning(f"Encoding detection failed, using utf-8: {e}")
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return content, 'utf-8'
    
    async def _save_text_file(self, text: str, output_path: Path, settings: TextSettings):
        """Save text file with specified format and encoding."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if settings.format == TextFormat.JSON:
                # Save as JSON
                data = {
                    "content": text,
                    "metadata": {
                        "encoding": settings.encoding,
                        "format": settings.format.value,
                        "processed_at": time.time()
                    }
                }
                with open(output_path, 'w', encoding=settings.encoding) as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            elif settings.format == TextFormat.XML:
                # Save as XML
                xml_content = f"""<?xml version="1.0" encoding="{settings.encoding}"?>
<document>
    <content><![CDATA[{text}]]></content>
    <metadata>
        <encoding>{settings.encoding}</encoding>
        <format>{settings.format.value}</format>
        <processed_at>{time.time()}</processed_at>
    </metadata>
</document>"""
                with open(output_path, 'w', encoding=settings.encoding) as f:
                    f.write(xml_content)
            
            else:
                # Save as plain text
                with open(output_path, 'w', encoding=settings.encoding) as f:
                    f.write(text)
            
        except Exception as e:
            logger.error(f"Text save failed: {str(e)}")
            raise
    
    async def _process_text(self, text: str, settings: TextSettings) -> str:
        """Process text according to settings."""
        processed = text
        
        try:
            # Apply processing modes
            for mode in settings.processing_modes or []:
                if mode == TextProcessingMode.CLEAN:
                    processed = await self._clean_text(processed, settings)
                elif mode == TextProcessingMode.NORMALIZE:
                    processed = await self._normalize_text(processed, settings)
                elif mode == TextProcessingMode.TRANSLATE and settings.target_language:
                    processed = await self.translate(processed, settings.target_language)
                elif mode == TextProcessingMode.SUMMARIZE:
                    processed = await self.summarize(processed, settings.summary_ratio)
            
            return processed
            
        except Exception as e:
            logger.error(f"Text processing failed: {str(e)}")
            return text
    
    async def _clean_text(self, text: str, settings: TextSettings) -> str:
        """Clean text content."""
        cleaned = text
        
        try:
            # Remove HTML tags
            if settings.remove_html:
                cleaned = re.sub(r'<[^>]+>', '', cleaned)
            
            # Remove URLs
            if settings.remove_urls:
                cleaned = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', cleaned)
            
            # Remove email addresses
            if settings.remove_emails:
                cleaned = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', cleaned)
            
            # Remove phone numbers
            if settings.remove_phone_numbers:
                cleaned = re.sub(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b', '', cleaned)
            
            # Remove extra whitespace
            if settings.remove_extra_whitespace:
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            
            # Normalize unicode
            if settings.normalize_unicode:
                import unicodedata
                cleaned = unicodedata.normalize('NFKD', cleaned)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Text cleaning failed: {str(e)}")
            return text
    
    async def _normalize_text(self, text: str, settings: TextSettings) -> str:
        """Normalize text content."""
        try:
            normalized = text
            
            # Convert to lowercase (optional)
            # normalized = normalized.lower()
            
            # Remove extra punctuation
            normalized = re.sub(r'[^\w\s]', ' ', normalized)
            
            # Normalize whitespace
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            
            return normalized
            
        except Exception as e:
            logger.error(f"Text normalization failed: {str(e)}")
            return text
    
    async def _enhance_text(self, text: str, settings: TextSettings) -> str:
        """Enhance text quality."""
        try:
            enhanced = text
            
            # Grammar and spelling improvements would require specialized models
            # This is a placeholder for enhancement logic
            
            if settings.enhance_readability:
                # Simple readability improvements
                # Split long sentences, simplify vocabulary, etc.
                enhanced = await self._improve_readability(enhanced)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Text enhancement failed: {str(e)}")
            return text
    
    async def _improve_readability(self, text: str) -> str:
        """Improve text readability."""
        try:
            # This is a simplified implementation
            # In practice, you'd use more sophisticated NLP techniques
            
            improved = text
            
            # Split long sentences
            sentences = re.split(r'[.!?]+', improved)
            improved_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence.split()) > 20:  # Long sentence
                    # Try to split at conjunctions
                    parts = re.split(r'\b(and|but|or|because|since|although)\b', sentence)
                    improved_sentences.extend([part.strip() for part in parts if part.strip()])
                else:
                    improved_sentences.append(sentence)
            
            improved = '. '.join([s for s in improved_sentences if s])
            
            return improved
            
        except Exception as e:
            logger.error(f"Readability improvement failed: {str(e)}")
            return text
    
    async def _analyze_sentiment(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze text sentiment."""
        try:
            if 'sentiment' not in self.pipelines:
                return None
            
            result = self.pipelines['sentiment'](text)
            
            if result and len(result) > 0:
                # Get the best score
                best_result = max(result[0], key=lambda x: x['score'])
                return {
                    'label': best_result['label'],
                    'score': best_result['score']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return None
    
    async def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability."""
        try:
            readability = {}
            
            if TEXT_LIBS_AVAILABLE:
                readability['flesch_reading_ease'] = flesch_reading_ease(text)
                readability['flesch_kincaid_grade'] = flesch_kincaid_grade(text)
            
            return readability
            
        except Exception as e:
            logger.error(f"Readability analysis failed: {str(e)}")
            return {}
    
    async def _extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """Extract keywords from text."""
        try:
            if not TEXT_LIBS_AVAILABLE:
                return []
            
            # Simple keyword extraction using NLTK
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            from collections import Counter
            
            # Tokenize and filter
            words = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            
            # Filter words
            keywords = [
                word for word in words 
                if word.isalpha() and len(word) > 3 and word not in stop_words
            ]
            
            # Count frequency
            word_freq = Counter(keywords)
            
            # Return top keywords
            return [word for word, freq in word_freq.most_common(max_keywords)]
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {str(e)}")
            return []
    
    async def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities from text."""
        try:
            if 'en' not in self.nlp_models:
                return []
            
            nlp = self.nlp_models['en']
            doc = nlp(text)
            
            entities = []
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'description': spacy.explain(ent.label_)
                })
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            return []
    
    async def _detect_language(self, text: str) -> Optional[str]:
        """Detect text language."""
        try:
            # Simple language detection based on common words
            # In practice, you'd use a proper language detection library
            
            # Check for common English words
            english_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            french_words = {'le', 'la', 'les', 'de', 'du', 'et', 'ou', 'mais', 'dans', 'sur', 'pour', 'avec'}
            german_words = {'der', 'die', 'das', 'und', 'oder', 'aber', 'in', 'auf', 'für', 'mit', 'von'}
            
            words = set(text.lower().split())
            
            english_score = len(words & english_words)
            french_score = len(words & french_words)
            german_score = len(words & german_words)
            
            if english_score >= french_score and english_score >= german_score:
                return 'en'
            elif french_score >= german_score:
                return 'fr'
            elif german_score > 0:
                return 'de'
            
            return 'en'  # Default to English
            
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return None
    
    async def _extractive_summarization(self, text: str, ratio: float) -> str:
        """Simple extractive summarization."""
        try:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) <= 3:
                return text
            
            # Score sentences by word frequency
            from collections import Counter
            words = text.lower().split()
            word_freq = Counter(words)
            
            sentence_scores = []
            for sentence in sentences:
                score = sum(word_freq[word] for word in sentence.lower().split())
                sentence_scores.append((score, sentence))
            
            # Sort by score and take top sentences
            sentence_scores.sort(reverse=True)
            top_count = max(1, int(len(sentences) * ratio))
            
            top_sentences = [sent for score, sent in sentence_scores[:top_count]]
            
            return '. '.join(top_sentences) + '.'
            
        except Exception as e:
            logger.error(f"Extractive summarization failed: {str(e)}")
            return text
    
    def _parse_text_settings(self, request) -> TextSettings:
        """Parse transformation request into text settings."""
        settings = TextSettings()
        
        if hasattr(request, 'target_format') and request.target_format:
            settings.format = TextFormat(request.target_format)
        
        if hasattr(request, 'options') and request.options:
            options = request.options
            settings.encoding = options.get('encoding', 'utf-8')
            settings.remove_html = options.get('remove_html', True)
            settings.remove_urls = options.get('remove_urls', False)
            settings.remove_emails = options.get('remove_emails', False)
            settings.normalize_unicode = options.get('normalize_unicode', True)
            settings.extract_keywords = options.get('extract_keywords', False)
            settings.sentiment_analysis = options.get('sentiment_analysis', False)
            settings.summary_ratio = options.get('summary_ratio', 0.3)
            
            if options.get('language'):
                settings.language = Language(options['language'])
            if options.get('target_language'):
                settings.target_language = Language(options['target_language'])
            if options.get('processing_modes'):
                settings.processing_modes = [
                    TextProcessingMode(mode) for mode in options['processing_modes']
                ]
        
        return settings
    
    def _generate_output_path(
        self,
        input_path: Path,
        settings: TextSettings,
        requested_output: Optional[str] = None
    ) -> Path:
        """Generate output file path."""
        if requested_output:
            return Path(requested_output)
        
        # Generate based on input and settings
        output_name = f"{input_path.stem}_processed.{settings.format.value}"
        return input_path.parent / output_name
    
    async def cleanup(self):
        """Cleanup temporary files and resources."""
        try:
            # Clean temp directory
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            logger.info("TextTransformer cleanup completed")
            
        except Exception as e:
            logger.error(f"TextTransformer cleanup failed: {str(e)}")


class TextConverter:
    """Simplified text converter interface."""
    
    def __init__(self, transformer: Optional[TextTransformer] = None):
        self.transformer = transformer or TextTransformer()
    
    async def convert(
        self,
        input_path: str,
        output_path: str,
        format: str = "txt",
        encoding: str = "utf-8"
    ) -> bool:
        """Convert text file."""
        return await self.transformer.convert(input_path, output_path, format, encoding)


class TextAnalyzer:
    """Simplified text analyzer interface."""
    
    def __init__(self, transformer: Optional[TextTransformer] = None):
        self.transformer = transformer or TextTransformer()
    
    async def analyze(
        self,
        text: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze text content."""
        return await self.transformer.analyze(text, options)
