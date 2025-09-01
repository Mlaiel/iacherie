"""
NLP Analyzers for Ainflue platform.
Provides content analysis, sentiment analysis, and language detection capabilities.
"""

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from typing import Dict, List, Optional, Any
import re


class ContentAnalyzer:
    """Analyzes content for quality, topics, and characteristics."""
    
    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Fallback if model not installed
                pass
    
    def analyze_content(self, text: str) -> Dict[str, Any]:
        """Analyze content for various characteristics."""
        if not text:
            return {"error": "Empty content"}
        
        analysis = {
            "length": len(text),
            "word_count": len(text.split()),
            "sentence_count": len(re.split(r'[.!?]+', text)),
            "quality_score": self._calculate_quality_score(text),
            "topics": self._extract_topics(text),
            "readability": self._calculate_readability(text)
        }
        
        if self.nlp:
            doc = self.nlp(text)
            analysis.update({
                "entities": [(ent.text, ent.label_) for ent in doc.ents],
                "keywords": [token.lemma_ for token in doc if token.is_alpha and not token.is_stop],
                "language_confidence": 0.95  # Placeholder
            })
        
        return analysis
    
    def _calculate_quality_score(self, text: str) -> float:
        """Calculate content quality score (0-100)."""
        if not text:
            return 0.0
        
        score = 50.0  # Base score
        
        # Length bonus
        if 100 <= len(text) <= 5000:
            score += 20
        
        # Grammar check (simplified)
        if re.search(r'[.!?]', text):
            score += 10
        
        # Capitalization check
        if any(c.isupper() for c in text):
            score += 10
        
        # No excessive repetition
        words = text.lower().split()
        if len(set(words)) / len(words) > 0.7:
            score += 10
        
        return min(100.0, score)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text."""
        # Simplified topic extraction
        words = text.lower().split()
        common_topics = [
            "music", "video", "art", "business", "technology", 
            "education", "entertainment", "sports", "health", "travel"
        ]
        
        found_topics = []
        for topic in common_topics:
            if topic in text.lower():
                found_topics.append(topic)
        
        return found_topics[:5]  # Top 5 topics
    
    def _calculate_readability(self, text: str) -> str:
        """Calculate readability level."""
        if not text:
            return "Unknown"
        
        words = len(text.split())
        sentences = len(re.split(r'[.!?]+', text))
        
        if sentences == 0:
            return "Poor"
        
        avg_words_per_sentence = words / sentences
        
        if avg_words_per_sentence < 10:
            return "Easy"
        elif avg_words_per_sentence < 20:
            return "Medium"
        else:
            return "Hard"


class SentimentAnalyzer:
    """Analyzes sentiment of content."""
    
    def __init__(self):
        self.positive_words = {
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "love", "like", "enjoy", "happy", "pleased", "satisfied"
        }
        self.negative_words = {
            "bad", "terrible", "awful", "horrible", "hate", "dislike",
            "sad", "angry", "disappointed", "frustrated", "upset"
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        if not text:
            return {"sentiment": "neutral", "confidence": 0.0, "score": 0.0}
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return {"sentiment": "neutral", "confidence": 0.5, "score": 0.0}
        
        score = (positive_count - negative_count) / len(words)
        
        if score > 0.05:
            sentiment = "positive"
        elif score < -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        confidence = min(1.0, total_sentiment_words / len(words) * 10)
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "score": score,
            "positive_words": positive_count,
            "negative_words": negative_count
        }


class LanguageDetector:
    """Detects language of content."""
    
    def __init__(self):
        # Simple language patterns
        self.language_patterns = {
            "en": ["the", "and", "is", "in", "to", "of", "a", "that", "it"],
            "fr": ["le", "de", "et", "à", "un", "une", "ce", "que", "qui"],
            "es": ["el", "la", "de", "que", "y", "a", "en", "un", "es"],
            "de": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit"],
            "it": ["il", "di", "che", "e", "la", "a", "per", "non", "in"],
            "pt": ["o", "de", "a", "e", "do", "da", "em", "um", "para"],
            "ru": ["в", "и", "не", "на", "я", "с", "что", "он", "как"],
            "zh": ["的", "是", "了", "在", "有", "我", "他", "这", "个"],
            "ja": ["の", "は", "が", "を", "に", "で", "と", "も", "だ"],
            "ar": ["في", "من", "إلى", "على", "أن", "هذا", "كان", "لا", "ما"]
        }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of the text."""
        if not text:
            return {"language": "unknown", "confidence": 0.0}
        
        words = text.lower().split()
        if not words:
            return {"language": "unknown", "confidence": 0.0}
        
        language_scores = {}
        
        for lang_code, patterns in self.language_patterns.items():
            score = sum(1 for word in words if word in patterns)
            language_scores[lang_code] = score / len(words)
        
        if not language_scores:
            return {"language": "unknown", "confidence": 0.0}
        
        best_language = max(language_scores, key=language_scores.get)
        confidence = language_scores[best_language]
        
        # If confidence is too low, mark as unknown
        if confidence < 0.1:
            return {"language": "unknown", "confidence": confidence}
        
        return {
            "language": best_language,
            "confidence": confidence,
            "all_scores": language_scores
        }
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        return list(self.language_patterns.keys())


# Convenience functions
def analyze_content(text: str) -> Dict[str, Any]:
    """Analyze content using ContentAnalyzer."""
    analyzer = ContentAnalyzer()
    return analyzer.analyze_content(text)


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze sentiment using SentimentAnalyzer."""
    analyzer = SentimentAnalyzer()
    return analyzer.analyze_sentiment(text)


def detect_language(text: str) -> Dict[str, Any]:
    """Detect language using LanguageDetector."""
    detector = LanguageDetector()
    return detector.detect_language(text)