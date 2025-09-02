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
    """Advanced text analysis utilities with NLP capabilities."""
    
    def __init__(self):
        """Initialize the text analyzer with NLP capabilities."""
        # Initialize text processing components
        self.stopwords = {
            'en': {
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
                'to', 'was', 'will', 'with', 'would', 'you', 'your', 'i', 'me',
                'my', 'we', 'our', 'us', 'this', 'these', 'they', 'them', 'their'
            }
        }
        
        # Sentiment lexicons
        self.positive_words = {
            'amazing', 'awesome', 'excellent', 'fantastic', 'great', 'incredible', 
            'outstanding', 'perfect', 'wonderful', 'brilliant', 'superb', 'magnificent',
            'love', 'like', 'enjoy', 'happy', 'excited', 'thrilled', 'delighted',
            'good', 'best', 'beautiful', 'nice', 'cool', 'fun', 'interesting'
        }
        
        self.negative_words = {
            'terrible', 'awful', 'horrible', 'disgusting', 'hate', 'worst', 'bad',
            'ugly', 'boring', 'stupid', 'annoying', 'frustrating', 'disappointing',
            'sad', 'angry', 'upset', 'mad', 'furious', 'disgusted', 'pathetic',
            'useless', 'worthless', 'garbage', 'trash', 'fail', 'failed'
        }
        
        # Language patterns for detection
        self.language_patterns = {
            'en': ['the', 'and', 'that', 'have', 'for', 'not', 'with', 'you', 'this', 'but'],
            'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
            'fr': ['de', 'le', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
            'es': ['de', 'la', 'que', 'el', 'en', 'y', 'a', 'es', 'se', 'no'],
            'it': ['di', 'che', 'e', 'la', 'il', 'un', 'a', 'è', 'per', 'una'],
            'pt': ['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para'],
            'ru': ['в', 'и', 'не', 'на', 'я', 'быть', 'то', 'он', 'с', 'а'],
            'zh': ['的', '一', '是', '在', '了', '不', '和', '有', '大', '这'],
            'ja': ['の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し']
        }
        
        # Content quality indicators
        self.quality_indicators = {
            'positive': ['detailed', 'comprehensive', 'thorough', 'informative', 'helpful'],
            'negative': ['spam', 'clickbait', 'fake', 'misleading', 'duplicate']
        }
        
        # Initialize optional NLP libraries
        self.nlp_available = False
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
                self.nlp_available = True
            except OSError:
                self.nlp = None
        except ImportError:
            self.nlp = None
        
        # Initialize regex patterns for advanced text processing
        import re
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.phone_pattern = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
        self.hashtag_pattern = re.compile(r'#[\w]+')
        self.mention_pattern = re.compile(r'@[\w]+')
        
        # Platform-specific emoji mappings
        self.emoji_categories = {
            'positive': ['😊', '😄', '😍', '🥰', '😘', '🤗', '👍', '❤️', '💕', '🔥'],
            'negative': ['😭', '😢', '😡', '😤', '😠', '👎', '💔', '😩', '😞', '🙄'],
            'neutral': ['😐', '😑', '🤔', '😮', '😯', '🤷', '👌', '✌️', '🤝', '💭']
        }
        
        # Initialize statistical measures
        self.stats = {
            'texts_processed': 0,
            'languages_detected': {},
            'avg_sentiment_score': 0.0,
            'total_words_processed': 0
        }
    
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