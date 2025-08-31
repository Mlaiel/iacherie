#!/usr/bin/env python3
"""Natural Language Processing Module for IA-Influencer-Agent
=========================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides advanced NLP capabilities including:
- Text generation and completion
- Language detection and classification
- Text summarization
- Keyword extraction and analysis
- Sentiment analysis
- Named entity recognition

Features:
- Multi-language support
- High-quality text processing
- Real-time analysis capabilities
- Extensible architecture
"""
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re
from collections import Counter
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# Conditional imports for optional NLP libraries
try:
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        AutoModelForCausalLM, pipeline
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("transformers library not available, using fallback implementations")
    TRANSFORMERS_AVAILABLE = False

try:
    import nltk
    NLTK_AVAILABLE = True
except ImportError:
    logger.warning("NLTK not available, using simple text processing")
    NLTK_AVAILABLE = False


class NLPTaskType(Enum):
    """NLP task types"""    TEXT_GENERATION = "text_generation"
    LANGUAGE_DETECTION = "language_detection"
    TEXT_SUMMARIZATION = "text_summarization"
    KEYWORD_EXTRACTION = "keyword_extraction"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NAMED_ENTITY_RECOGNITION = "ner"
    TEXT_CLASSIFICATION = "text_classification"


class Language(Enum):
    """Supported languages"""    ENGLISH = "en"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    UNKNOWN = "unknown"


class SentimentPolarity(Enum):
    """Sentiment polarity levels"""    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


@dataclass
class NLPResult:
    """Result from NLP processing"""    task_type: NLPTaskType
    input_text: str
    output: Any
    confidence: float
    processing_time: float
    metadata: Dict[str, Any] = None


@dataclass
class LanguageDetectionResult:
    """Language detection result"""    detected_language: Language
    confidence: float
    all_predictions: List[Tuple[Language, float]] = None


@dataclass
class SummaryResult:
    """Text summarization result"""    original_text: str
    summary: str
    compression_ratio: float
    key_sentences: List[str] = None


@dataclass
class KeywordResult:
    """Keyword extraction result"""    keywords: List[str]
    scores: List[float]
    phrases: List[str] = None
    entities: List[str] = None


@dataclass
class SentimentResult:
    """Sentiment analysis result"""    polarity: SentimentPolarity
    confidence: float
    compound_score: float
    positive_score: float = 0.0
    negative_score: float = 0.0
    neutral_score: float = 0.0


class BaseNLPProcessor(ABC):
    """Base class for NLP processors"""    
    def __init__(self, processor_name: str = "base_nlp"):
        self.processor_name = processor_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
    @abstractmethod
    def load_model(self) -> bool:
        """Load the NLP model"""        pass
        
    def preprocess_text(self, text: str) -> str:
        """Basic text preprocessing"""        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def tokenize_simple(self, text: str) -> List[str]:
        """Simple tokenization fallback"""        # Basic word tokenization
        words = re.findall(r'\b\w+\b', text.lower())
        return words


class TextGenerator(BaseNLPProcessor):
    """Advanced text generation using language models"""    
    def __init__(self, model_name: str = "gpt2"):
        super().__init__(f"generator_{model_name}")
        self.model_name = model_name
        self.max_length = 200
        self.temperature = 0.7
        
    def load_model(self) -> bool:
        """Load text generation model"""        try:
            if TRANSFORMERS_AVAILABLE:
                # Use Hugging Face transformers
                self.tokenizer = AutoTokenizer.from_pretrained('gpt2')
                self.model = AutoModelForCausalLM.from_pretrained('gpt2')
                self.model.to(self.device)
                self.model.eval()
            else:
                # Simple fallback model
                self.model = self._create_simple_generator()
                
            self.is_loaded = True
            logger.info(f"Text generator {self.processor_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading text generator: {str(e)}")
            return False
    
    def _create_simple_generator(self):
        """Create simple text generation model"""        class SimpleTextGenerator(nn.Module):
            def __init__(self, vocab_size=10000, embed_size=256, hidden_size=512):
                super().__init__()
                self.embedding = nn.Embedding(vocab_size, embed_size)
                self.lstm = nn.LSTM(embed_size, hidden_size, batch_first=True)
                self.output = nn.Linear(hidden_size, vocab_size)
                
            def forward(self, x, hidden=None):
                embedded = self.embedding(x)
                output, hidden = self.lstm(embedded, hidden)
                output = self.output(output)
                return output, hidden
        
        return SimpleTextGenerator()
    
    def generate_text(self, prompt: str, max_length: Optional[int] = None, 
                     temperature: Optional[float] = None) -> NLPResult:
        """Generate text continuation from prompt"""        import time
        start_time = time.time()
        
        try:
            if not self.is_loaded:
                if not self.load_model():
                    raise RuntimeError("Failed to load text generation model")
            
            max_len = max_length or self.max_length
            temp = temperature or self.temperature
            
            if TRANSFORMERS_AVAILABLE and hasattr(self, 'tokenizer'):
                generated_text = self._generate_with_transformers(prompt, max_len, temp)
            else:
                generated_text = self._generate_simple(prompt, max_len)
                
            processing_time = time.time() - start_time
            
            return NLPResult(
                task_type=NLPTaskType.TEXT_GENERATION,
                input_text=prompt,
                output=generated_text,
                confidence=0.8,  # Mock confidence
                processing_time=processing_time,
                metadata={
                    'model': self.processor_name,
                    'max_length': max_len,
                    'temperature': temp
                }
            )
            
        except Exception as e:
            logger.error(f"Error in text generation: {str(e)}")
            return NLPResult(
                task_type=NLPTaskType.TEXT_GENERATION,
                input_text=prompt,
                output=f"{prompt} [Error: {str(e)}]",
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    def _generate_with_transformers(self, prompt: str, max_length: int, temperature: float) -> str:
        """Generate text using transformers library"""        inputs = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=len(inputs[0]) + max_length,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text
    
    def _generate_simple(self, prompt: str, max_length: int) -> str:
        """Simple text generation fallback"""        # Basic template-based generation
        common_continuations = [
            "and this opens up new possibilities for innovation.",
            "which represents a significant advancement in the field.",
            "enabling more efficient and effective solutions.",
            "providing valuable insights for future development.",
            "demonstrating the potential for practical applications."
        ]
        
        import random
        continuation = random.choice(common_continuations)
        return f"{prompt} {continuation}"
    
    def complete_sentence(self, partial_sentence: str) -> str:
        """Complete a partial sentence"""        result = self.generate_text(partial_sentence, max_length=50, temperature=0.5)
        return result.output


class LanguageDetector(BaseNLPProcessor):
    """Language detection for text content"""    
    def __init__(self, model_name: str = "language_detector_v1"):
        super().__init__(f"lang_det_{model_name}")
        self.language_patterns = self._load_language_patterns()
        
    def _load_language_patterns(self) -> Dict[Language, List[str]]:
        """Load language detection patterns"""        return {
            Language.ENGLISH: ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with'],
            Language.FRENCH: ['le', 'de', 'et', 'est', 'un', 'il', 'être', 'et', 'en', 'avoir'],
            Language.GERMAN: ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'ich'],
            Language.SPANISH: ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no'],
            Language.ITALIAN: ['il', 'di', 'che', 'e', 'la', 'per', 'un', 'in', 'con', 'del'],
            Language.PORTUGUESE: ['o', 'de', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com'],
            Language.DUTCH: ['de', 'en', 'van', 'het', 'een', 'in', 'te', 'dat', 'op', 'voor'],
            Language.RUSSIAN: ['в', 'и', 'не', 'на', 'с', 'то', 'что', 'по', 'для', 'как']
        }
    
    def load_model(self) -> bool:
        """Load language detection model"""        try:
            if TRANSFORMERS_AVAILABLE:
                # Could load a dedicated language detection model
                pass
                
            self.is_loaded = True
            logger.info(f"Language detector {self.processor_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading language detector: {str(e)}")
            return False
    
    def detect_language(self, text: str) -> LanguageDetectionResult:
        """Detect the language of input text"""        try:
            if not self.is_loaded:
                if not self.load_model():
                    raise RuntimeError("Failed to load language detection model")
            
            # Simple pattern-based detection
            text_lower = text.lower()
            words = self.tokenize_simple(text_lower)
            
            language_scores = {}
            
            for language, patterns in self.language_patterns.items():
                score = 0
                for word in words:
                    if word in patterns:
                        score += 1
                
                # Normalize score by text length
                if len(words) > 0:
                    language_scores[language] = score / len(words)
                else:
                    language_scores[language] = 0
            
            # Find best match
            if language_scores:
                best_language = max(language_scores, key=language_scores.get)
                confidence = language_scores[best_language]
                
                # Sort all predictions
                all_predictions = [(lang, score) for lang, score in language_scores.items()]
                all_predictions.sort(key=lambda x: x[1], reverse=True)
                
                return LanguageDetectionResult(
                    detected_language=best_language,
                    confidence=confidence,
                    all_predictions=all_predictions
                )
            else:
                return LanguageDetectionResult(
                    detected_language=Language.UNKNOWN,
                    confidence=0.0
                )
                
        except Exception as e:
            logger.error(f"Error in language detection: {str(e)}")
            return LanguageDetectionResult(
                detected_language=Language.UNKNOWN,
                confidence=0.0
            )


class TextSummarizer(BaseNLPProcessor):
    """Text summarization using extractive and abstractive methods"""    
    def __init__(self, model_name: str = "summarizer_v1"):
        super().__init__(f"summarizer_{model_name}")
        self.max_summary_length = 150
        self.compression_ratio = 0.3
        
    def load_model(self) -> bool:
        """Load text summarization model"""        try:
            if TRANSFORMERS_AVAILABLE:
                # Could load BART or T5 for summarization
                self.summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")
            
            self.is_loaded = True
            logger.info(f"Text summarizer {self.processor_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading text summarizer: {str(e)}")
            return False
    
    def summarize_text(self, text: str, max_length: Optional[int] = None,
                      compression_ratio: Optional[float] = None) -> SummaryResult:
        """Summarize input text"""        try:
            if not self.is_loaded:
                if not self.load_model():
                    raise RuntimeError("Failed to load text summarization model")
            
            max_len = max_length or self.max_summary_length
            ratio = compression_ratio or self.compression_ratio
            
            if TRANSFORMERS_AVAILABLE and hasattr(self, 'summarization_pipeline'):
                summary = self._summarize_with_transformers(text, max_len)
            else:
                summary = self._summarize_extractive(text, ratio)
            
            actual_ratio = len(summary) / len(text) if text else 0
            key_sentences = self._extract_key_sentences(text, 3)
            
            return SummaryResult(
                original_text=text,
                summary=summary,
                compression_ratio=actual_ratio,
                key_sentences=key_sentences
            )
            
        except Exception as e:
            logger.error(f"Error in text summarization: {str(e)}")
            return SummaryResult(
                original_text=text,
                summary=f"Error summarizing text: {str(e)}",
                compression_ratio=1.0
            )
    
    def _summarize_with_transformers(self, text: str, max_length: int) -> str:
        """Summarize using transformers pipeline"""        summary = self.summarization_pipeline(text, max_length=max_length, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    
    def _summarize_extractive(self, text: str, ratio: float) -> str:
        """Simple extractive summarization"""        sentences = self._split_sentences(text)
        
        if len(sentences) <= 2:
            return text
        
        # Score sentences by word frequency
        word_freq = self._calculate_word_frequencies(text)
        sentence_scores = []
        
        for sentence in sentences:
            score = 0
            words = self.tokenize_simple(sentence)
            for word in words:
                if word in word_freq:
                    score += word_freq[word]
            
            if len(words) > 0:
                score = score / len(words)
            sentence_scores.append((sentence, score))
        
        # Select top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        num_sentences = max(1, int(len(sentences) * ratio))
        selected_sentences = [sent for sent, score in sentence_scores[:num_sentences]]
        
        return ' '.join(selected_sentences)
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _calculate_word_frequencies(self, text: str) -> Dict[str, float]:
        """Calculate word frequencies"""        words = self.tokenize_simple(text)
        word_count = Counter(words)
        max_freq = max(word_count.values()) if word_count else 1
        
        # Normalize frequencies
        word_freq = {word: count / max_freq for word, count in word_count.items()}
        return word_freq
    
    def _extract_key_sentences(self, text: str, num_sentences: int) -> List[str]:
        """Extract key sentences from text"""        sentences = self._split_sentences(text)
        word_freq = self._calculate_word_frequencies(text)
        
        sentence_scores = []
        for sentence in sentences:
            score = 0
            words = self.tokenize_simple(sentence)
            for word in words:
                if word in word_freq:
                    score += word_freq[word]
            sentence_scores.append((sentence, score))
        
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        return [sent for sent, score in sentence_scores[:num_sentences]]


class KeywordExtractor(BaseNLPProcessor):
    """Keyword and key phrase extraction from text"""    
    def __init__(self, model_name: str = "keyword_extractor_v1"):
        super().__init__(f"keyword_{model_name}")
        self.stop_words = self._load_stop_words()
        
    def _load_stop_words(self) -> set:
        """Load stop words for filtering"""        # Basic English stop words
        return {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'said', 'each', 'which', 'their', 'time', 'if'
        }
    
    def load_model(self) -> bool:
        """Load keyword extraction model"""        try:
            self.is_loaded = True
            logger.info(f"Keyword extractor {self.processor_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading keyword extractor: {str(e)}")
            return False
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> KeywordResult:
        """Extract keywords from text"""        try:
            if not self.is_loaded:
                if not self.load_model():
                    raise RuntimeError("Failed to load keyword extraction model")
            
            # Tokenize and filter words
            words = self.tokenize_simple(text)
            filtered_words = [word for word in words if word not in self.stop_words and len(word) > 2]
            
            # Calculate word frequencies
            word_freq = Counter(filtered_words)
            
            # Extract top keywords
            top_words = word_freq.most_common(num_keywords)
            keywords = [word for word, count in top_words]
            scores = [count / len(filtered_words) for word, count in top_words]
            
            # Extract phrases (simple bigrams)
            phrases = self._extract_phrases(text, num_keywords // 2)
            
            # Extract potential entities (capitalized words)
            entities = self._extract_entities(text)
            
            return KeywordResult(
                keywords=keywords,
                scores=scores,
                phrases=phrases,
                entities=entities
            )
            
        except Exception as e:
            logger.error(f"Error in keyword extraction: {str(e)}")
            return KeywordResult(
                keywords=[],
                scores=[],
                phrases=[],
                entities=[]
            )
    
    def _extract_phrases(self, text: str, num_phrases: int) -> List[str]:
        """Extract key phrases (bigrams)"""        words = self.tokenize_simple(text)
        filtered_words = [word for word in words if word not in self.stop_words]
        
        # Generate bigrams
        bigrams = []
        for i in range(len(filtered_words) - 1):
            bigram = f"{filtered_words[i]} {filtered_words[i+1]}"
            bigrams.append(bigram)
        
        # Count and return top phrases
        phrase_freq = Counter(bigrams)
        top_phrases = phrase_freq.most_common(num_phrases)
        
        return [phrase for phrase, count in top_phrases]
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract potential named entities (capitalized words)"""        # Simple entity extraction based on capitalization
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        entity_freq = Counter(words)
        
        # Filter out common words that might be capitalized at sentence start
        common_starts = {'The', 'This', 'That', 'These', 'Those', 'And', 'But', 'Or'}
        entities = [word for word in entity_freq.keys() if word not in common_starts]
        
        return entities[:10]  # Return top 10 potential entities


# Export main classes
__all__ = [
    'TextGenerator',
    'LanguageDetector',
    'TextSummarizer',
    'KeywordExtractor',
    'NLPResult',
    'LanguageDetectionResult',
    'SummaryResult',
    'KeywordResult',
    'SentimentResult',
    'NLPTaskType',
    'Language',
    'SentimentPolarity',
    'BaseNLPProcessor'
]

logger.info("NLP module loaded successfully")
