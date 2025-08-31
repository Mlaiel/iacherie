"""
Advanced Utilities Module for IA Influencer Agent Platform NLP

Comprehensive utility functions, helpers, and common functionality
for the NLP processing pipeline.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING - Unauthorized use prohibited 
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import asyncio
import logging
import re
import string
from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import json
import hashlib
import base64
from pathlib import Path
import urllib.parse
import html
import unicodedata
from collections import defaultdict, Counter
import math
import statistics
from enum import Enum
import time
import locale
import zoneinfo

logger = logging.getLogger(__name__)

class Platform(Enum):
    """Social media platforms"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok" 
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"
    DISCORD = "discord"

class ContentType(Enum):
    """Content types"""
    POST = "post"
    STORY = "story"
    REEL = "reel"
    VIDEO = "video"
    LIVE = "live"
    ARTICLE = "article"
    COMMENT = "comment"
    REPLY = "reply"
    CAPTION = "caption"
    HASHTAG = "hashtag"

class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    JAPANESE = "ja"
    KOREAN = "ko"
    CHINESE = "zh"
    ARABIC = "ar"
    RUSSIAN = "ru"
    HINDI = "hi"

@dataclass
class TextStats:
    """Text statistics"""
    character_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    reading_time_minutes: float
    readability_score: float
    complexity_score: float
    emoji_count: int
    hashtag_count: int
    mention_count: int
    url_count: int

@dataclass
class PlatformLimits:
    """Platform-specific content limits"""
    platform: Platform
    max_caption_length: int
    max_hashtags: int
    max_mentions: int
    supports_markdown: bool
    supports_emojis: bool
    video_max_duration: int  # seconds
    image_formats: List[str]

@dataclass
class ValidationResult:
    """Content validation result"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    compliance_score: float = 1.0

class TextCleaner:
    """Advanced text cleaning utilities"""
    
    def __init__(self):
        # Compiled regex patterns for efficiency
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        self.hashtag_pattern = re.compile(r'#\w+')
        self.mention_pattern = re.compile(r'@\w+')
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002500-\U00002BEF"  # chinese char
            "\U00002702-\U000027B0"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"  # dingbats
            "\u3030"
            "]+", re.UNICODE
        )
        self.phone_pattern = re.compile(
            r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        )
        self.punctuation_pattern = re.compile(f'[{re.escape(string.punctuation)}]')
        self.whitespace_pattern = re.compile(r'\s+')
        
        # HTML entities
        self.html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&nbsp;': ' '
        }
    
    def clean_text(self, text: str, level: str = "standard") -> str:
        """
        Clean text with different levels of processing
        
        Levels:
        - basic: Remove extra whitespace, normalize unicode
        - standard: + Remove URLs, emails, normalize case
        - aggressive: + Remove all special characters, emojis
        - platform: Platform-specific cleaning
        """
        if not text:
            return ""
        
        cleaned = text
        
        # Always apply basic cleaning
        cleaned = self._normalize_unicode(cleaned)
        cleaned = self._decode_html_entities(cleaned)
        cleaned = self._normalize_whitespace(cleaned)
        
        if level in ["standard", "aggressive", "platform"]:
            # Remove URLs and emails
            cleaned = self.url_pattern.sub('', cleaned)
            cleaned = self.email_pattern.sub('', cleaned)
            cleaned = self.phone_pattern.sub('', cleaned)
            
            # Normalize case for hashtags and mentions
            cleaned = self._normalize_social_elements(cleaned)
        
        if level in ["aggressive"]:
            # Remove emojis and special characters
            cleaned = self.emoji_pattern.sub('', cleaned)
            cleaned = self.punctuation_pattern.sub(' ', cleaned)
            
            # Remove hashtags and mentions
            cleaned = self.hashtag_pattern.sub('', cleaned)
            cleaned = self.mention_pattern.sub('', cleaned)
        
        if level == "platform":
            # Platform-specific cleaning
            cleaned = self._platform_specific_clean(cleaned)
        
        # Final whitespace normalization
        cleaned = self._normalize_whitespace(cleaned)
        
        return cleaned.strip()
    
    def extract_elements(self, text: str) -> Dict[str, List[str]]:
        """Extract social media elements from text"""
        if not text:
            return {
                'urls': [],
                'emails': [],
                'hashtags': [],
                'mentions': [],
                'emojis': [],
                'phones': []
            }
        
        return {
            'urls': self.url_pattern.findall(text),
            'emails': self.email_pattern.findall(text),
            'hashtags': [tag.lower() for tag in self.hashtag_pattern.findall(text)],
            'mentions': [mention.lower() for mention in self.mention_pattern.findall(text)],
            'emojis': self.emoji_pattern.findall(text),
            'phones': self.phone_pattern.findall(text)
        }
    
    def _normalize_unicode(self, text: str) -> str:
        """Normalize unicode characters"""



        return unicodedata.normalize('NFKC', text)
    
    def _decode_html_entities(self, text: str) -> str:
        """Decode HTML entities"""
        decoded = html.unescape(text)
        
        # Handle additional entities
        for entity, replacement in self.html_entities.items():
            decoded = decoded.replace(entity, replacement)
        
        return decoded
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace"""



        return self.whitespace_pattern.sub(' ', text)
    
    def _normalize_social_elements(self, text: str) -> str:
        """Normalize hashtags and mentions"""
        # Convert hashtags to lowercase
        def lowercase_hashtag(match):
            return match.group(0).lower()
        
        def lowercase_mention(match):
            return match.group(0).lower()
        
        text = self.hashtag_pattern.sub(lowercase_hashtag, text)
        text = self.mention_pattern.sub(lowercase_mention, text)
        
        return text
    
    def _platform_specific_clean(self, text: str) -> str:
        """Platform-specific text cleaning"""
        # Remove platform-specific markup
        # Instagram: Remove line breaks in captions
        text = text.replace('\n\n', '\n')
        
        # Twitter: Handle thread indicators
        text = re.sub(r'\d+/\d+$', '', text)
        
        # TikTok: Remove duet/stitch indicators
        text = re.sub(r'(duet with|stitch with) @\w+', '', text, flags=re.IGNORECASE)
        
        return text

class TextAnalyzer:
    """Advanced text analysis utilities"""
    
    def __init__(self):
        self.cleaner = TextCleaner()
        # Common stop words for multiple languages
        self.stop_words = {
            'en': {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'},
            'de': {'der', 'die', 'das', 'den', 'dem', 'des', 'ein', 'eine', 'einer', 'eines', 'und', 'oder', 'aber', 'in', 'an', 'auf', 'zu', 'für', 'von', 'mit', 'durch', 'ist', 'sind', 'war', 'waren', 'sein', 'haben', 'hat', 'hatte', 'werden', 'wird', 'wurde', 'kann', 'könnte', 'soll', 'sollte', 'muss', 'darf', 'dieser', 'diese', 'dieses'},
            'fr': {'le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'mais', 'dans', 'sur', 'à', 'pour', 'de', 'avec', 'par', 'est', 'sont', 'était', 'étaient', 'être', 'avoir', 'a', 'avait', 'sera', 'serait', 'peut', 'pourrait', 'doit', 'devrait', 'ce', 'cette', 'ces'},
            'es': {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'o', 'pero', 'en', 'sobre', 'a', 'para', 'de', 'con', 'por', 'es', 'son', 'era', 'eran', 'ser', 'tener', 'tiene', 'tenía', 'será', 'sería', 'puede', 'podría', 'debe', 'debería', 'este', 'esta', 'estos', 'estas'}
        }
    
    def get_text_stats(self, text: str, language: str = 'en') -> TextStats:
        """Get comprehensive text statistics"""
        if not text:
            return TextStats(0, 0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0, 0)
        
        # Basic counts
        character_count = len(text)
        words = self._get_words(text)
        word_count = len(words)
        sentences = self._get_sentences(text)
        sentence_count = len(sentences)
        paragraphs = text.split('\n\n')
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        # Extract elements
        elements = self.cleaner.extract_elements(text)
        emoji_count = len(elements['emojis'])
        hashtag_count = len(elements['hashtags'])
        mention_count = len(elements['mentions'])
        url_count = len(elements['urls'])
        
        # Calculate reading time (average 200 words per minute)
        reading_time_minutes = word_count / 200.0
        
        # Calculate readability score (simplified Flesch Reading Ease)
        readability_score = self._calculate_readability(text, sentences, words)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity(words, sentences, language)
        
        return TextStats(
            character_count=character_count,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            reading_time_minutes=reading_time_minutes,
            readability_score=readability_score,
            complexity_score=complexity_score,
            emoji_count=emoji_count,
            hashtag_count=hashtag_count,
            mention_count=mention_count,
            url_count=url_count
        )
    
    def extract_keywords(self, text: str, language: str = 'en', 
                        max_keywords: int = 10) -> List[Tuple[str, float]]:
        """Extract keywords with TF-IDF-like scoring"""
        if not text:
            return []
        
        # Clean and tokenize
        cleaned_text = self.cleaner.clean_text(text, level="standard")
        words = self._get_words(cleaned_text.lower())
        
        # Remove stop words
        stop_words = self.stop_words.get(language, self.stop_words['en'])
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        if not filtered_words:
            return []
        
        # Calculate word frequencies
        word_freq = Counter(filtered_words)
        total_words = len(filtered_words)
        
        # Calculate TF-IDF-like scores
        scored_words = []
        for word, freq in word_freq.items():
            # TF (Term Frequency)
            tf = freq / total_words
            
            # Simple IDF approximation (penalize very common words)
            idf = math.log(total_words / freq)
            
            # Combined score
            score = tf * idf
            scored_words.append((word, score))
        
        # Sort by score and return top keywords
        scored_words.sort(key=lambda x: x[1], reverse=True)
        return scored_words[:max_keywords]
    
    def detect_language(self, text: str) -> str:
        """Simple language detection based on character patterns"""
        if not text:
            return 'en'
        
        # Clean text for analysis
        cleaned = self.cleaner.clean_text(text, level="basic")
        words = self._get_words(cleaned.lower())
        
        if not words:
            return 'en'
        
        # Language indicators
        language_scores = defaultdict(float)
        
        # Check for language-specific stop words
        for lang, stop_words in self.stop_words.items():
            common_words = set(words) & stop_words
            if common_words:
                language_scores[lang] += len(common_words) / len(words)
        
        # Check for character patterns
        # German: umlauts and eszett
        if re.search(r'[äöüßÄÖÜ]', text):
            language_scores['de'] += 0.3
        
        # French: accents and cedilla
        if re.search(r'[àâäçéèêëïîôöùûüÿñæœÀÂÄÇÉÈÊËÏÎÔÖÙÛÜŸÑÆŒ]', text):
            language_scores['fr'] += 0.3
        
        # Spanish: specific accents and ñ
        if re.search(r'[ñáéíóúüÑÁÉÍÓÚÜ]', text):
            language_scores['es'] += 0.3
        
        # Return language with highest score, default to English
        if language_scores:
            return max(language_scores.items(), key=lambda x: x[1])[0]
        
        return 'en'
    
    def _get_words(self, text: str) -> List[str]:
        """Extract words from text"""
        # Simple word extraction
        word_pattern = re.compile(r'\b\w+\b')
        return word_pattern.findall(text)
    
    def _get_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        # Simple sentence splitting
        sentence_pattern = re.compile(r'[.!?]+')
        sentences = sentence_pattern.split(text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_readability(self, text: str, sentences: List[str], words: List[str]) -> float:
        """Calculate readability score (simplified Flesch Reading Ease)"""
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Count syllables (simplified)
        total_syllables = 0
        for word in words:
            syllables = max(1, len(re.findall(r'[aeiouAEIOU]', word)))
            total_syllables += syllables
        
        avg_syllables_per_word = total_syllables / len(words)
        
        # Flesch Reading Ease formula (simplified)
        readability = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # Normalize to 0-1 scale
        return max(0.0, min(1.0, readability / 100.0))
    
    def _calculate_complexity(self, words: List[str], sentences: List[str], language: str) -> float:
        """Calculate text complexity score"""
        if not words:
            return 0.0
        
        complexity_factors = []
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        complexity_factors.append(min(1.0, avg_word_length / 10.0))
        
        # Vocabulary diversity (unique words / total words)
        vocabulary_diversity = len(set(words)) / len(words)
        complexity_factors.append(1.0 - vocabulary_diversity)
        
        # Long word percentage (words > 6 characters)
        long_words = [word for word in words if len(word) > 6]
        long_word_ratio = len(long_words) / len(words)
        complexity_factors.append(long_word_ratio)
        
        # Average sentence length
        if sentences:
            avg_sentence_length = len(words) / len(sentences)
            complexity_factors.append(min(1.0, avg_sentence_length / 20.0))
        
        return statistics.mean(complexity_factors)

class PlatformValidator:
    """Platform-specific content validation"""
    
    def __init__(self):
        self.platform_limits = {
            Platform.INSTAGRAM: PlatformLimits(
                platform=Platform.INSTAGRAM,
                max_caption_length=2200,
                max_hashtags=30,
                max_mentions=20,
                supports_markdown=False,
                supports_emojis=True,
                video_max_duration=60,
                image_formats=['jpg', 'jpeg', 'png']
            ),
            Platform.TIKTOK: PlatformLimits(
                platform=Platform.TIKTOK,
                max_caption_length=2200,
                max_hashtags=100,
                max_mentions=20,
                supports_markdown=False,
                supports_emojis=True,
                video_max_duration=180,
                image_formats=['jpg', 'jpeg', 'png']
            ),
            Platform.TWITTER: PlatformLimits(
                platform=Platform.TWITTER,
                max_caption_length=280,
                max_hashtags=10,
                max_mentions=10,
                supports_markdown=False,
                supports_emojis=True,
                video_max_duration=140,
                image_formats=['jpg', 'jpeg', 'png', 'gif']
            ),
            Platform.YOUTUBE: PlatformLimits(
                platform=Platform.YOUTUBE,
                max_caption_length=5000,
                max_hashtags=15,
                max_mentions=50,
                supports_markdown=True,
                supports_emojis=True,
                video_max_duration=43200,  # 12 hours
                image_formats=['jpg', 'jpeg', 'png']
            ),
            Platform.LINKEDIN: PlatformLimits(
                platform=Platform.LINKEDIN,
                max_caption_length=3000,
                max_hashtags=5,
                max_mentions=50,
                supports_markdown=True,
                supports_emojis=True,
                video_max_duration=600,
                image_formats=['jpg', 'jpeg', 'png']
            )
        }
        
        self.cleaner = TextCleaner()
    
    def validate_content(self, content: str, platform: Platform, 
                        content_type: ContentType = ContentType.POST) -> ValidationResult:
        """Validate content for specific platform"""
        if platform not in self.platform_limits:
            return ValidationResult(
                is_valid=False,
                errors=[f"Unsupported platform: {platform.value}"]
            )
        
        limits = self.platform_limits[platform]
        result = ValidationResult(is_valid=True)
        
        # Extract elements from content
        elements = self.cleaner.extract_elements(content)
        
        # Check content length
        if len(content) > limits.max_caption_length:
            result.is_valid = False
            result.errors.append(
                f"Content exceeds maximum length ({len(content)}/{limits.max_caption_length} characters)"
            )
        elif len(content) > limits.max_caption_length * 0.9:
            result.warnings.append(
                f"Content is close to maximum length ({len(content)}/{limits.max_caption_length} characters)"
            )
        
        # Check hashtag count
        hashtag_count = len(elements['hashtags'])
        if hashtag_count > limits.max_hashtags:
            result.is_valid = False
            result.errors.append(
                f"Too many hashtags ({hashtag_count}/{limits.max_hashtags})"
            )
        
        # Check mention count
        mention_count = len(elements['mentions'])
        if mention_count > limits.max_mentions:
            result.is_valid = False
            result.errors.append(
                f"Too many mentions ({mention_count}/{limits.max_mentions})"
            )
        
        # Platform-specific validations
        if platform == Platform.TWITTER:
            # Check for thread indicators
            if content_type == ContentType.POST and '1/' in content:
                result.suggestions.append("Consider using Twitter's native threading feature")
        
        elif platform == Platform.INSTAGRAM:
            # Check for line breaks (Instagram displays poorly)
            if content.count('\n') > 10:
                result.warnings.append("Too many line breaks may affect readability on Instagram")
            
            # Suggest hashtag placement
            if hashtag_count > 0 and not content.strip().endswith('#'):
                result.suggestions.append("Consider placing hashtags at the end for better readability")
        
        elif platform == Platform.LINKEDIN:
            # Check for professional tone
            informal_words = ['lol', 'omg', 'yolo', 'tbh', 'imo']
            content_lower = content.lower()
            found_informal = [word for word in informal_words if word in content_lower]
            if found_informal:
                result.warnings.append(f"Informal language detected: {', '.join(found_informal)}")
        
        # Calculate compliance score
        score_factors = []
        
        # Length compliance
        length_ratio = len(content) / limits.max_caption_length
        score_factors.append(1.0 - min(1.0, length_ratio))
        
        # Hashtag compliance
        hashtag_ratio = hashtag_count / limits.max_hashtags
        score_factors.append(1.0 - min(1.0, hashtag_ratio))
        
        # Mention compliance
        mention_ratio = mention_count / limits.max_mentions
        score_factors.append(1.0 - min(1.0, mention_ratio))
        
        result.compliance_score = statistics.mean(score_factors)
        
        return result
    
    def optimize_for_platform(self, content: str, platform: Platform) -> str:
        """Optimize content for specific platform"""
        if platform not in self.platform_limits:
            return content
        
        limits = self.platform_limits[platform]
        optimized = content
        
        # Truncate if too long
        if len(optimized) > limits.max_caption_length:
            # Try to truncate at word boundary
            truncated = optimized[:limits.max_caption_length - 3]
            last_space = truncated.rfind(' ')
            if last_space > limits.max_caption_length * 0.8:
                optimized = truncated[:last_space] + "..."
            else:
                optimized = truncated + "..."
        
        # Platform-specific optimizations
        if platform == Platform.TWITTER:
            # Ensure hashtags and mentions are properly formatted
            optimized = re.sub(r'#(\w+)', r'#\1', optimized)
            optimized = re.sub(r'@(\w+)', r'@\1', optimized)
        
        elif platform == Platform.INSTAGRAM:
            # Move hashtags to end if they're in the middle
            hashtags = re.findall(r'#\w+', optimized)
            if hashtags:
                # Remove hashtags from middle
                temp = re.sub(r'#\w+', '', optimized)
                # Add them at the end
                optimized = temp.strip() + '\n\n' + ' '.join(hashtags)
        
        elif platform == Platform.LINKEDIN:
            # Ensure professional formatting
            # Capitalize first letter of sentences
            sentences = optimized.split('. ')
            sentences = [s.capitalize() for s in sentences]
            optimized = '. '.join(sentences)
        
        return optimized.strip()

class HashGenerator:
    """Utility for generating various types of hashes"""
    
    @staticmethod
    def generate_content_hash(content: str, algorithm: str = 'md5') -> str:
        """Generate hash for content"""
        if not content:
            return ""
        
        content_bytes = content.encode('utf-8')
        
        if algorithm == 'md5':
            return hashlib.md5(content_bytes).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(content_bytes).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(content_bytes).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    @staticmethod
    def generate_similarity_hash(content: str, length: int = 64) -> str:
        """Generate similarity hash for fuzzy matching"""
        # Simple implementation - in production, use algorithms like SimHash
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        # Convert to binary and sample bits
        binary = bin(int(content_hash, 16))[2:].zfill(256)
        
        # Sample every nth bit to create shorter hash
        step = max(1, len(binary) // length)
        similarity_hash = ''.join(binary[i] for i in range(0, len(binary), step))
        
        return similarity_hash[:length]
    
    @staticmethod
    def generate_fingerprint(content: str, metadata: Dict[str, Any] = None) -> str:
        """Generate unique fingerprint combining content and metadata"""
        fingerprint_data = {
            'content': content,
            'metadata': metadata or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_string.encode('utf-8')).hexdigest()

class DateTimeUtils:
    """Date and time utilities"""
    
    @staticmethod
    def get_optimal_posting_times(platform: Platform, timezone_str: str = 'UTC') -> List[int]:
        """Get optimal posting hours for platform (24-hour format)"""
        # Based on general social media research
        optimal_times = {
            Platform.INSTAGRAM: [8, 11, 13, 17, 19],
            Platform.TIKTOK: [6, 10, 19, 20, 21],
            Platform.TWITTER: [8, 9, 12, 17, 18],
            Platform.FACEBOOK: [9, 13, 15],
            Platform.LINKEDIN: [8, 9, 10, 11, 12, 17],
            Platform.YOUTUBE: [14, 15, 16, 17, 18, 19, 20],
            Platform.PINTEREST: [8, 11, 14, 15, 20, 21]
        }
        
        return optimal_times.get(platform, [9, 12, 15, 18])
    
    @staticmethod
    def is_optimal_posting_time(platform: Platform, dt: datetime, 
                               timezone_str: str = 'UTC') -> bool:
        """Check if given time is optimal for posting"""



        try:
            # Convert to specified timezone
            if timezone_str != 'UTC':
                tz = zoneinfo.ZoneInfo(timezone_str)
                dt = dt.replace(tzinfo=zoneinfo.ZoneInfo('UTC')).astimezone(tz)
            
            optimal_hours = DateTimeUtils.get_optimal_posting_times(platform, timezone_str)
            return dt.hour in optimal_hours
        except Exception:
            return False
    
    @staticmethod
    def format_relative_time(dt: datetime, language: str = 'en') -> str:
        """Format relative time (e.g., '2 hours ago')"""
        now = datetime.utcnow()
        if dt.tzinfo:
            now = now.replace(tzinfo=timezone.utc)
        
        delta = now - dt
        
        if delta.days > 0:
            if language == 'de':
                return f"vor {delta.days} Tag{'en' if delta.days != 1 else ''}"
            elif language == 'fr':
                return f"il y a {delta.days} jour{'s' if delta.days != 1 else ''}"
            elif language == 'es':
                return f"hace {delta.days} día{'s' if delta.days != 1 else ''}"
            else:
                return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
        
        hours = delta.seconds // 3600
        if hours > 0:
            if language == 'de':
                return f"vor {hours} Stunde{'n' if hours != 1 else ''}"
            elif language == 'fr':
                return f"il y a {hours} heure{'s' if hours != 1 else ''}"
            elif language == 'es':
                return f"hace {hours} hora{'s' if hours != 1 else ''}"
            else:
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
        
        minutes = (delta.seconds % 3600) // 60
        if minutes > 0:
            if language == 'de':
                return f"vor {minutes} Minute{'n' if minutes != 1 else ''}"
            elif language == 'fr':
                return f"il y a {minutes} minute{'s' if minutes != 1 else ''}"
            elif language == 'es':
                return f"hace {minutes} minuto{'s' if minutes != 1 else ''}"
            else:
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        
        if language == 'de':
            return "gerade eben"
        elif language == 'fr':
            return "à l'instant"
        elif language == 'es':
            return "ahora mismo"
        else:
            return "just now"

class PerformanceUtils:
    """Performance optimization utilities"""
    
    @staticmethod
    async def batch_process(items: List[Any], processor: Callable, 
                          batch_size: int = 10, max_concurrent: int = 5) -> List[Any]:
        """Process items in batches with concurrency control"""
        results = []
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_batch(batch):
            async with semaphore:
                batch_results = []
                for item in batch:
                    try:
                        if asyncio.iscoroutinefunction(processor):
                            result = await processor(item)
                        else:
                            result = processor(item)
                        batch_results.append(result)
                    except Exception as e:
                        logger.error(f"Error processing item: {e}")
                        batch_results.append(None)
                return batch_results
        
        # Create batches
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
        
        # Process batches concurrently
        batch_tasks = [process_batch(batch) for batch in batches]
        batch_results = await asyncio.gather(*batch_tasks)
        
        # Flatten results
        for batch_result in batch_results:
            results.extend(batch_result)
        
        return results
    
    @staticmethod
    def memoize(func: Callable) -> Callable:
        """Simple memoization decorator"""
        cache = {}
        
        def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))
            key_hash = hashlib.md5(key.encode()).hexdigest()
            
            if key_hash not in cache:
                cache[key_hash] = func(*args, **kwargs)
            
            return cache[key_hash]
        
        return wrapper
    
    @staticmethod
    def time_function(func: Callable) -> Callable:
        """Decorator to measure function execution time"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.debug(f"Function {func.__name__} took {execution_time:.4f} seconds")
            return result
        
        return wrapper

# Utility functions for common operations
def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem operations"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    
    return filename

def extract_dominant_colors(image_path: str, num_colors: int = 5) -> List[Tuple[int, int, int]]:
    """Extract dominant colors from image (placeholder implementation)"""
    # In production, this would use image processing libraries like PIL/Pillow
    # with color quantization algorithms
    
    # Placeholder: return some sample colors
    sample_colors = [
        (255, 87, 51),   # Red-orange
        (46, 204, 113),  # Green
        (52, 152, 219),  # Blue
        (155, 89, 182),  # Purple
        (241, 196, 15),  # Yellow
        (230, 126, 34),  # Orange
        (231, 76, 60),   # Red
        (26, 188, 156),  # Turquoise
    ]
    
    return sample_colors[:num_colors]

def calculate_engagement_score(likes: int, comments: int, shares: int, 
                             views: int, followers: int) -> float:
    """Calculate engagement score based on interaction metrics"""
    if followers == 0 or views == 0:
        return 0.0
    
    # Weighted engagement calculation
    engagement = (likes * 1.0 + comments * 2.0 + shares * 3.0) / max(views, followers)
    
    # Normalize to 0-1 scale
    return min(1.0, engagement * 100)

def generate_variations(text: str, num_variations: int = 3) -> List[str]:
    """Generate text variations using simple transformations"""
    variations = []
    
    # Original text
    variations.append(text)
    
    if num_variations <= 1:
        return variations[:num_variations]
    
    # Variation 1: Different punctuation
    variation1 = text.replace('!', '.').replace('?', '.')
    if variation1 != text:
        variations.append(variation1)
    
    # Variation 2: Add emojis
    if '' not in text:
        variation2 = text + ' '
        variations.append(variation2)
    
    # Variation 3: Different capitalization
    if text != text.title():
        variation3 = text.title()
        variations.append(variation3)
    
    # Return requested number of variations
    return variations[:num_variations]

# Initialize global instances
text_cleaner = TextCleaner()
text_analyzer = TextAnalyzer()
platform_validator = PlatformValidator()
