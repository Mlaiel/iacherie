"""
NLP Utilities for Ainflue platform.
Provides enums and utility classes for NLP operations.
"""

from enum import Enum
from typing import Dict, List, Any


class Platform(Enum):
    """Social media platforms."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"


class Language(Enum):
    """Supported languages."""
    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    ARABIC = "ar"


class ContentType(Enum):
    """Content types."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CAPTION = "caption"
    HASHTAGS = "hashtags"
    DESCRIPTION = "description"
    SCRIPT = "script"


class TextAnalyzer:
    """Basic text analysis utilities."""
    
    def __init__(self):
        pass
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Basic cleaning
        text = text.strip()
        text = " ".join(text.split())  # Normalize whitespace
        
        return text
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        import re
        hashtags = re.findall(r'#\w+', text)
        return [tag.lower() for tag in hashtags]
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text."""
        import re
        mentions = re.findall(r'@\w+', text)
        return [mention.lower() for mention in mentions]
    
    def count_words(self, text: str) -> int:
        """Count words in text."""
        if not text:
            return 0
        return len(text.split())
    
    def analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability."""
        words = len(text.split())
        sentences = len([s for s in text.split('.') if s.strip()])
        
        if sentences == 0:
            return {"level": "unknown", "score": 0.0}
        
        avg_words_per_sentence = words / sentences
        
        if avg_words_per_sentence < 10:
            level = "easy"
            score = 0.9
        elif avg_words_per_sentence < 20:
            level = "medium"
            score = 0.7
        else:
            level = "hard"
            score = 0.5
        
        return {
            "level": level,
            "score": score,
            "word_count": words,
            "sentence_count": sentences,
            "avg_words_per_sentence": avg_words_per_sentence
        }


# Utility functions
def get_platform_limits(platform: Platform) -> Dict[str, Any]:
    """Get platform-specific content limits."""
    limits = {
        Platform.INSTAGRAM: {
            "caption_max": 2200,
            "hashtags_max": 30,
            "hashtags_optimal": 11
        },
        Platform.TWITTER: {
            "text_max": 280,
            "hashtags_max": 2
        },
        Platform.TIKTOK: {
            "caption_max": 150,
            "hashtags_max": 100
        },
        Platform.YOUTUBE: {
            "title_max": 100,
            "description_max": 5000
        },
        Platform.LINKEDIN: {
            "post_max": 3000,
            "hashtags_max": 5
        }
    }
    
    return limits.get(platform, {})


def detect_content_type(content: str) -> ContentType:
    """Detect content type from text."""
    content_lower = content.lower()
    
    if content.startswith('#'):
        return ContentType.HASHTAGS
    elif '@' in content and len(content.split()) < 10:
        return ContentType.CAPTION
    elif len(content) > 500:
        return ContentType.DESCRIPTION
    else:
        return ContentType.TEXT