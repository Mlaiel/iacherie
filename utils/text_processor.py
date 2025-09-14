"""
Enterprise Text Processing Utilities - Advanced NLP and Content Analysis
======================================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Expert Roles: Lead Dev IA + ML Engineer + Backend Senior + IA Prompt Engineer
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive text processing capabilities for content analysis,
natural language processing, and intelligent text manipulation for the Ainflue platform.
"""

import asyncio
import functools
import hashlib
import html
import json
import logging
import re
import string
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urlparse
import warnings

# Third-party imports with fallbacks
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.chunk import ne_chunk
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    warnings.warn("NLTK not available. Basic text processing will be used.")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    import langdetect
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


@dataclass
class TextAnalysisResult:
    """Comprehensive text analysis result"""
    text: str
    language: Optional[str] = None
    language_confidence: float = 0.0
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    character_count: int = 0
    readability_score: float = 0.0
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"
    key_phrases: List[str] = field(default_factory=list)
    named_entities: List[Dict[str, str]] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    profanity_detected: bool = False
    spam_score: float = 0.0
    keywords: List[Tuple[str, float]] = field(default_factory=list)
    pos_tags: List[Tuple[str, str]] = field(default_factory=list)
    processing_time: float = 0.0


@dataclass
class ContentSafety:
    """Content safety and moderation result"""
    is_safe: bool = True
    confidence: float = 1.0
    detected_issues: List[str] = field(default_factory=list)
    severity: str = "none"  # none, low, medium, high, critical
    recommendations: List[str] = field(default_factory=list)
    flagged_content: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TextSimilarity:
    """Text similarity comparison result"""
    text1: str
    text2: str
    similarity_score: float
    similarity_type: str  # cosine, jaccard, levenshtein, semantic
    common_words: List[str] = field(default_factory=list)
    unique_words_1: List[str] = field(default_factory=list)
    unique_words_2: List[str] = field(default_factory=list)


class LanguageDetector:
    """Advanced language detection with confidence scoring"""
    
    def __init__(self) -> None:
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi'
        }
        
        # Basic language patterns for fallback detection
        self.language_patterns = {
            'en': re.compile(r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b', re.IGNORECASE),
            'es': re.compile(r'\b(el|la|los|las|de|del|en|con|por|para|que|se)\b', re.IGNORECASE),
            'fr': re.compile(r'\b(le|la|les|de|du|des|en|dans|avec|pour|que|se)\b', re.IGNORECASE),
            'de': re.compile(r'\b(der|die|das|den|dem|des|und|oder|aber|in|auf|mit)\b', re.IGNORECASE),
            'ar': re.compile(r'[\u0600-\u06FF]'),
            'zh': re.compile(r'[\u4e00-\u9fff]'),
            'ja': re.compile(r'[\u3040-\u309f\u30a0-\u30ff]'),
            'ru': re.compile(r'[\u0400-\u04FF]')
        }
    
    def detect_language(self, text: str) -> Tuple[Optional[str], float]:
        """Detect language with confidence score"""
        if not text or len(text.strip()) < 3:
            return None, 0.0
        
        # Try advanced detection first
        if LANGDETECT_AVAILABLE:
            try:
                lang_probs = detect_langs(text)
                if lang_probs:
                    best_match = lang_probs[0]
                    return best_match.lang, best_match.prob
            except Exception:
                pass
        
        # Fallback to pattern-based detection
        return self._pattern_based_detection(text)
    
    def _pattern_based_detection(self, text: str) -> Tuple[Optional[str], float]:
        """Pattern-based language detection fallback"""
        text_lower = text.lower()
        scores = {}
        
        for lang, pattern in self.language_patterns.items():
            matches = pattern.findall(text_lower)
            if matches:
                # Score based on match frequency and total words
                words = len(text_lower.split())
                score = len(matches) / max(words, 1)
                scores[lang] = min(score, 1.0)
        
        if scores:
            best_lang = max(scores, key=scores.get)
            return best_lang, scores[best_lang]
        
        return None, 0.0


class TextNormalizer:
    """Advanced text normalization and cleaning"""
    
    def __init__(self) -> None:
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        self.hashtag_pattern = re.compile(r'#\w+')
        self.mention_pattern = re.compile(r'@\w+')
        self.emoji_pattern = re.compile(
            r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|'
            r'[\U0001F1E0-\U0001F1FF]|[\U00002700-\U000027BF]|[\U0001f900-\U0001f9ff]'
        )
    
    def normalize_text(self, text: str, options: Dict[str, bool] = None) -> str:
        """Comprehensive text normalization"""
        if not text:
            return ""
        
        options = options or {}
        normalized = text
        
        # Unicode normalization
        if options.get('unicode_normalize', True):
            normalized = unicodedata.normalize('NFKC', normalized)
        
        # HTML entity decoding
        if options.get('decode_html', True):
            normalized = html.unescape(normalized)
        
        # Remove/replace URLs
        if options.get('remove_urls', False):
            normalized = self.url_pattern.sub('', normalized)
        elif options.get('replace_urls', False):
            normalized = self.url_pattern.sub('[URL]', normalized)
        
        # Remove/replace emails
        if options.get('remove_emails', False):
            normalized = self.email_pattern.sub('', normalized)
        elif options.get('replace_emails', False):
            normalized = self.email_pattern.sub('[EMAIL]', normalized)
        
        # Remove/replace phone numbers
        if options.get('remove_phones', False):
            normalized = self.phone_pattern.sub('', normalized)
        elif options.get('replace_phones', False):
            normalized = self.phone_pattern.sub('[PHONE]', normalized)
        
        # Handle social media elements
        if options.get('remove_hashtags', False):
            normalized = self.hashtag_pattern.sub('', normalized)
        if options.get('remove_mentions', False):
            normalized = self.mention_pattern.sub('', normalized)
        
        # Remove emojis
        if options.get('remove_emojis', False):
            normalized = self.emoji_pattern.sub('', normalized)
        
        # Case normalization
        if options.get('lowercase', False):
            normalized = normalized.lower()
        elif options.get('uppercase', False):
            normalized = normalized.upper()
        elif options.get('title_case', False):
            normalized = normalized.title()
        
        # Remove extra whitespace
        if options.get('normalize_whitespace', True):
            normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Remove special characters (optional)
        if options.get('remove_special_chars', False):
            normalized = re.sub(r'[^\w\s]', '', normalized)
        
        return normalized
    
    def extract_elements(self, text: str) -> Dict[str, List[str]]:
        """Extract various elements from text"""
        elements = {
            'urls': self.url_pattern.findall(text),
            'emails': self.email_pattern.findall(text),
            'phones': [' '.join(match) for match in self.phone_pattern.findall(text)],
            'hashtags': [tag[1:] for tag in self.hashtag_pattern.findall(text)],  # Remove #
            'mentions': [mention[1:] for mention in self.mention_pattern.findall(text)],  # Remove @
            'emojis': self.emoji_pattern.findall(text)
        }
        return elements


class SentimentAnalyzer:
    """Advanced sentiment analysis with multiple approaches"""
    
    def __init__(self) -> None:
        self.positive_words = {
            'excellent', 'amazing', 'wonderful', 'fantastic', 'great', 'good', 'nice',
            'awesome', 'brilliant', 'perfect', 'outstanding', 'superb', 'magnificent',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'delighted'
        }
        
        self.negative_words = {
            'terrible', 'awful', 'horrible', 'bad', 'poor', 'worst', 'hate', 'dislike',
            'disgusting', 'disappointing', 'annoying', 'frustrating', 'angry', 'upset',
            'sad', 'depressed', 'miserable', 'pathetic', 'useless', 'stupid'
        }
        
        # Intensifiers and negations
        self.intensifiers = {'very', 'extremely', 'incredibly', 'absolutely', 'completely', 'totally'}
        self.negations = {'not', 'no', 'never', 'none', 'nothing', 'neither', 'nobody'}
    
    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """Analyze sentiment with score and label"""
        if not text:
            return 0.0, "neutral"
        
        # Try TextBlob if available
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                return polarity, self._polarity_to_label(polarity)
            except Exception:
                pass
        
        # Fallback to rule-based analysis
        return self._rule_based_sentiment(text)
    
    def _rule_based_sentiment(self, text: str) -> Tuple[float, str]:
        """Rule-based sentiment analysis"""
        words = text.lower().split()
        score = 0.0
        word_count = 0
        
        i = 0
        while i < len(words):
            word = words[i].strip(string.punctuation)
            
            # Check for negation in previous words
            negated = any(neg in words[max(0, i-3):i] for neg in self.negations)
            
            # Check for intensifiers
            intensified = any(intens in words[max(0, i-2):i] for intens in self.intensifiers)
            multiplier = 1.5 if intensified else 1.0
            
            if word in self.positive_words:
                sentiment_value = 1.0 * multiplier
                if negated:
                    sentiment_value *= -1
                score += sentiment_value
                word_count += 1
            elif word in self.negative_words:
                sentiment_value = -1.0 * multiplier
                if negated:
                    sentiment_value *= -1
                score += sentiment_value
                word_count += 1
            
            i += 1
        
        # Normalize score
        if word_count > 0:
            normalized_score = score / word_count
            # Clamp to [-1, 1]
            normalized_score = max(-1.0, min(1.0, normalized_score))
        else:
            normalized_score = 0.0
        
        return normalized_score, self._polarity_to_label(normalized_score)
    
    def _polarity_to_label(self, polarity: float) -> str:
        """Convert polarity score to label"""
        if polarity > 0.1:
            return "positive"
        elif polarity < -0.1:
            return "negative"
        else:
            return "neutral"


class KeywordExtractor:
    """Advanced keyword and key phrase extraction"""
    
    def __init__(self) -> None:
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'would', 'you', 'your', 'this', 'that',
            'these', 'those', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours'
        }
        
        if NLTK_AVAILABLE:
            try:
                nltk.download('stopwords', quiet=True)
                nltk.download('punkt', quiet=True)
                self.stop_words.update(set(stopwords.words('english')))
            except Exception:
                pass
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[Tuple[str, float]]:
        """Extract keywords with TF-IDF-like scoring"""
        if not text:
            return []
        
        # Tokenize and clean
        words = self._tokenize_and_clean(text)
        
        # Calculate word frequencies
        word_freq = Counter(words)
        total_words = len(words)
        
        # Calculate TF-IDF-like scores
        scored_words = []
        for word, freq in word_freq.items():
            # Term frequency
            tf = freq / total_words
            
            # Simple inverse document frequency approximation
            # (In a real system, this would use a corpus)
            idf = 1.0 / (1.0 + freq / total_words)
            
            score = tf * idf
            scored_words.append((word, score))
        
        # Sort by score and return top keywords
        scored_words.sort(key=lambda x: x[1], reverse=True)
        return scored_words[:max_keywords]
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases using n-gram analysis"""
        if not text:
            return []
        
        # Use NLTK if available
        if NLTK_AVAILABLE:
            try:
                sentences = sent_tokenize(text)
                phrases = []
                
                for sentence in sentences:
                    words = word_tokenize(sentence.lower())
                    # Extract 2-3 word phrases
                    for i in range(len(words) - 1):
                        bigram = ' '.join(words[i:i+2])
                        if self._is_valid_phrase(bigram):
                            phrases.append(bigram)
                        
                        if i < len(words) - 2:
                            trigram = ' '.join(words[i:i+3])
                            if self._is_valid_phrase(trigram):
                                phrases.append(trigram)
                
                # Count and return most frequent phrases
                phrase_counts = Counter(phrases)
                return [phrase for phrase, count in phrase_counts.most_common(max_phrases)]
            except Exception:
                pass
        
        # Fallback to simple n-gram extraction
        return self._simple_ngram_extraction(text, max_phrases)
    
    def _tokenize_and_clean(self, text: str) -> List[str]:
        """Tokenize and clean text for keyword extraction"""
        # Basic tokenization
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words and short words
        cleaned_words = [
            word for word in words
            if word not in self.stop_words
            and len(word) > 2
            and not word.isdigit()
        ]
        
        return cleaned_words
    
    def _is_valid_phrase(self, phrase: str) -> bool:
        """Check if phrase is valid for extraction"""
        words = phrase.split()
        
        # Skip if contains stop words
        if any(word in self.stop_words for word in words):
            return False
        
        # Skip if too short
        if len(phrase) < 5:
            return False
        
        # Skip if all digits
        if phrase.replace(' ', '').isdigit():
            return False
        
        return True
    
    def _simple_ngram_extraction(self, text: str, max_phrases: int) -> List[str]:
        """Simple n-gram extraction fallback"""
        words = self._tokenize_and_clean(text)
        phrases = []
        
        # Extract bigrams and trigrams
        for i in range(len(words) - 1):
            bigram = ' '.join(words[i:i+2])
            phrases.append(bigram)
            
            if i < len(words) - 2:
                trigram = ' '.join(words[i:i+3])
                phrases.append(trigram)
        
        # Return most frequent phrases
        phrase_counts = Counter(phrases)
        return [phrase for phrase, count in phrase_counts.most_common(max_phrases)]


class ContentModerator:
    """Advanced content moderation and safety checking"""
    
    def __init__(self) -> None:
        self.profanity_words = {
            # Basic profanity detection (implement with external list for production)
            'damn', 'hell', 'crap', 'stupid', 'idiot', 'moron', 'fool'
        }
        
        self.spam_indicators = {
            'buy now', 'click here', 'free money', 'guaranteed', 'limited time',
            'act now', 'call now', 'urgent', 'winner', 'congratulations',
            'exclusive deal', 'special offer', 'discount', 'promotion'
        }
        
        self.sensitive_topics = {
            'violence', 'weapon', 'drug', 'suicide', 'self-harm', 'hate',
            'discrimination', 'harassment', 'abuse', 'threat'
        }
    
    def moderate_content(self, text: str) -> ContentSafety:
        """Perform comprehensive content moderation"""
        if not text:
            return ContentSafety()
        
        text_lower = text.lower()
        detected_issues = []
        flagged_content = []
        severity = "none"
        
        # Check for profanity
        profanity_found = []
        for word in self.profanity_words:
            if word in text_lower:
                profanity_found.append(word)
        
        if profanity_found:
            detected_issues.append("profanity")
            flagged_content.append({
                'type': 'profanity',
                'words': profanity_found,
                'severity': 'low'
            })
            severity = "low"
        
        # Check for spam indicators
        spam_indicators_found = []
        for indicator in self.spam_indicators:
            if indicator in text_lower:
                spam_indicators_found.append(indicator)
        
        spam_score = len(spam_indicators_found) / len(text.split()) if text.split() else 0
        
        if spam_score > 0.1:  # More than 10% spam indicators
            detected_issues.append("spam")
            flagged_content.append({
                'type': 'spam',
                'indicators': spam_indicators_found,
                'score': spam_score,
                'severity': 'medium'
            })
            severity = "medium"
        
        # Check for sensitive topics
        sensitive_found = []
        for topic in self.sensitive_topics:
            if topic in text_lower:
                sensitive_found.append(topic)
        
        if sensitive_found:
            detected_issues.append("sensitive_content")
            flagged_content.append({
                'type': 'sensitive_content',
                'topics': sensitive_found,
                'severity': 'high'
            })
            severity = "high"
        
        # Check for excessive caps (shouting)
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        if caps_ratio > 0.7 and len(text) > 10:
            detected_issues.append("excessive_caps")
            flagged_content.append({
                'type': 'excessive_caps',
                'ratio': caps_ratio,
                'severity': 'low'
            })
        
        # Determine overall safety
        is_safe = len(detected_issues) == 0 or (severity in ["none", "low"])
        confidence = 1.0 - (len(detected_issues) * 0.2)  # Reduce confidence with more issues
        
        # Generate recommendations
        recommendations = []
        if "profanity" in detected_issues:
            recommendations.append("Remove or replace profane language")
        if "spam" in detected_issues:
            recommendations.append("Reduce promotional language and spam indicators")
        if "sensitive_content" in detected_issues:
            recommendations.append("Review content for sensitive topics and provide appropriate warnings")
        if "excessive_caps" in detected_issues:
            recommendations.append("Reduce use of capital letters")
        
        return ContentSafety(
            is_safe=is_safe,
            confidence=max(0.0, confidence),
            detected_issues=detected_issues,
            severity=severity,
            recommendations=recommendations,
            flagged_content=flagged_content
        )


class TextSimilarityCalculator:
    """Calculate similarity between texts using multiple algorithms"""
    
    def __init__(self) -> None:
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'would', 'you', 'your'
        }
    
    def calculate_similarity(self, text1: str, text2: str, method: str = 'cosine') -> TextSimilarity:
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return TextSimilarity(
                text1=text1 or "",
                text2=text2 or "",
                similarity_score=0.0,
                similarity_type=method
            )
        
        if method == 'cosine':
            return self._cosine_similarity(text1, text2)
        elif method == 'jaccard':
            return self._jaccard_similarity(text1, text2)
        elif method == 'levenshtein':
            return self._levenshtein_similarity(text1, text2)
        else:
            raise ValueError(f"Unsupported similarity method: {method}")
    
    def _cosine_similarity(self, text1: str, text2: str) -> TextSimilarity:
        """Calculate cosine similarity"""
        # Tokenize and clean
        words1 = self._tokenize_text(text1)
        words2 = self._tokenize_text(text2)
        
        # Create vocabulary
        vocab = set(words1 + words2)
        
        # Create vectors
        vec1 = [words1.count(word) for word in vocab]
        vec2 = [words2.count(word) for word in vocab]
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            similarity = 0.0
        else:
            similarity = dot_product / (magnitude1 * magnitude2)
        
        # Find common and unique words
        set1, set2 = set(words1), set(words2)
        common_words = list(set1 & set2)
        unique_1 = list(set1 - set2)
        unique_2 = list(set2 - set1)
        
        return TextSimilarity(
            text1=text1,
            text2=text2,
            similarity_score=similarity,
            similarity_type='cosine',
            common_words=common_words,
            unique_words_1=unique_1,
            unique_words_2=unique_2
        )
    
    def _jaccard_similarity(self, text1: str, text2: str) -> TextSimilarity:
        """Calculate Jaccard similarity"""
        words1 = set(self._tokenize_text(text1))
        words2 = set(self._tokenize_text(text2))
        
        intersection = words1 & words2
        union = words1 | words2
        
        if len(union) == 0:
            similarity = 0.0
        else:
            similarity = len(intersection) / len(union)
        
        return TextSimilarity(
            text1=text1,
            text2=text2,
            similarity_score=similarity,
            similarity_type='jaccard',
            common_words=list(intersection),
            unique_words_1=list(words1 - words2),
            unique_words_2=list(words2 - words1)
        )
    
    def _levenshtein_similarity(self, text1: str, text2: str) -> TextSimilarity:
        """Calculate Levenshtein distance-based similarity"""
        distance = self._levenshtein_distance(text1, text2)
        max_len = max(len(text1), len(text2))
        
        if max_len == 0:
            similarity = 1.0
        else:
            similarity = 1.0 - (distance / max_len)
        
        return TextSimilarity(
            text1=text1,
            text2=text2,
            similarity_score=similarity,
            similarity_type='levenshtein'
        )
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text for similarity calculation"""
        # Basic tokenization and cleaning
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if word not in self.stop_words and len(word) > 2]


class TextProcessor:
    """Main text processing class combining all capabilities"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.language_detector = LanguageDetector()
        self.normalizer = TextNormalizer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.keyword_extractor = KeywordExtractor()
        self.content_moderator = ContentModerator()
        self.similarity_calculator = TextSimilarityCalculator()
        
        # Configure logging
        logging.basicConfig(
            level=self.config.get('log_level', logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize NLTK data if available
        if NLTK_AVAILABLE:
            self._initialize_nltk()
    
    def _initialize_nltk(self) -> None:
        """Initialize NLTK data"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('maxent_ne_chunker', quiet=True)
            nltk.download('words', quiet=True)
        except Exception as e:
            self.logger.warning(f"Failed to download NLTK data: {e}")
    
    def analyze_text(self, text: str, deep_analysis: bool = True) -> TextAnalysisResult:
        """Perform comprehensive text analysis"""
        start_time = datetime.now()
        
        if not text:
            return TextAnalysisResult(text="")
        
        # Basic metrics
        word_count = len(text.split())
        sentence_count = len(re.split(r'[.!?]+', text))
        paragraph_count = len(text.split('\n\n'))
        character_count = len(text)
        
        # Language detection
        language, lang_confidence = self.language_detector.detect_language(text)
        
        # Sentiment analysis
        sentiment_score, sentiment_label = self.sentiment_analyzer.analyze_sentiment(text)
        
        # Extract elements
        elements = self.normalizer.extract_elements(text)
        
        # Keywords and phrases
        keywords = self.keyword_extractor.extract_keywords(text)
        key_phrases = self.keyword_extractor.extract_key_phrases(text)
        
        # Content safety
        safety_result = self.content_moderator.moderate_content(text)
        
        # Readability score (simple approximation)
        readability_score = self._calculate_readability(text, word_count, sentence_count)
        
        # Deep analysis (if requested)
        named_entities = []
        pos_tags = []
        topics = []
        
        if deep_analysis and NLTK_AVAILABLE:
            try:
                # POS tagging
                tokens = word_tokenize(text)
                pos_tags = pos_tag(tokens)
                
                # Named entity recognition
                tree = ne_chunk(pos_tags)
                named_entities = self._extract_named_entities(tree)
                
                # Simple topic extraction (based on keywords)
                topics = [word for word, score in keywords[:5] if score > 0.1]
                
            except Exception as e:
                self.logger.warning(f"Deep analysis failed: {e}")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return TextAnalysisResult(
            text=text,
            language=language,
            language_confidence=lang_confidence,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            character_count=character_count,
            readability_score=readability_score,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            key_phrases=key_phrases,
            named_entities=named_entities,
            topics=topics,
            hashtags=elements['hashtags'],
            mentions=elements['mentions'],
            urls=elements['urls'],
            emails=elements['emails'],
            phones=elements['phones'],
            profanity_detected=not safety_result.is_safe and 'profanity' in safety_result.detected_issues,
            spam_score=1.0 - safety_result.confidence if 'spam' in safety_result.detected_issues else 0.0,
            keywords=keywords,
            pos_tags=pos_tags[:20],  # Limit for performance
            processing_time=processing_time
        )
    
    def normalize_text(self, text: str, options: Dict[str, bool] = None) -> str:
        """Normalize text with specified options"""
        return self.normalizer.normalize_text(text, options)
    
    def compare_texts(self, text1: str, text2: str, method: str = 'cosine') -> TextSimilarity:
        """Compare similarity between two texts"""
        return self.similarity_calculator.calculate_similarity(text1, text2, method)
    
    def moderate_content(self, text: str) -> ContentSafety:
        """Moderate content for safety"""
        return self.content_moderator.moderate_content(text)
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[Tuple[str, float]]:
        """Extract keywords from text"""
        return self.keyword_extractor.extract_keywords(text, max_keywords)
    
    def batch_process_texts(self, texts: List[str], **kwargs) -> List[TextAnalysisResult]:
        """Process multiple texts in batch"""
        results = []
        for text in texts:
            try:
                result = self.analyze_text(text, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process text: {e}")
                results.append(TextAnalysisResult(text=text))
        
        return results
    
    async def async_analyze_text(self, text: str, **kwargs) -> TextAnalysisResult:
        """Async text analysis"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.analyze_text, text, **kwargs)
    
    def _calculate_readability(self, text: str, word_count: int, sentence_count: int) -> float:
        """Calculate simple readability score (Flesch-like)"""
        if sentence_count == 0:
            return 0.0
        
        avg_sentence_length = word_count / sentence_count
        
        # Count syllables (approximation)
        syllable_count = 0
        for word in text.split():
            syllable_count += max(1, len(re.findall(r'[aeiouyAEIOUY]', word)))
        
        avg_syllables_per_word = syllable_count / word_count if word_count > 0 else 0
        
        # Simplified Flesch reading ease score
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Normalize to 0-100 scale
        return max(0, min(100, score))
    
    def _extract_named_entities(self, tree) -> List[Dict[str, str]]:
        """Extract named entities from NLTK tree"""
        entities = []
        
        for subtree in tree:
            if hasattr(subtree, 'label'):
                entity_text = ' '.join([token for token, pos in subtree.leaves()])
                entity_type = subtree.label()
                entities.append({
                    'text': entity_text,
                    'type': entity_type
                })
        
        return entities


# Export main classes and utilities
__all__ = [
    'TextProcessor',
    'TextAnalysisResult',
    'ContentSafety',
    'TextSimilarity',
    'LanguageDetector',
    'TextNormalizer',
    'SentimentAnalyzer',
    'KeywordExtractor',
    'ContentModerator',
    'TextSimilarityCalculator'
]