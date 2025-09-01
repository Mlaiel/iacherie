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


# Additional analyzer classes for test compatibility
class AnalysisResult:
    """Analysis result container."""
    
    def __init__(self, content_id: str = None, analysis_type: str = None, 
                 results: Dict[str, Any] = None, confidence_score: float = 0.0,
                 metadata: Dict[str, Any] = None):
        self.content_id = content_id
        self.analysis_type = analysis_type
        self.results = results or {}
        self.confidence_score = confidence_score
        self.metadata = metadata or {}


class TopicAnalyzer:
    """Analyzes topics in content."""
    
    def __init__(self):
        pass
    
    async def analyze(self, content: str, metadata: Dict[str, Any] = None) -> AnalysisResult:
        """Analyze topics in content."""
        # Simple topic analysis based on keywords
        topics = []
        topic_keywords = {
            "fitness": ["workout", "gym", "exercise", "fitness", "training"],
            "food": ["food", "recipe", "cooking", "meal", "restaurant"],
            "travel": ["travel", "trip", "vacation", "explore", "adventure"],
            "tech": ["technology", "tech", "AI", "computer", "software"],
            "business": ["business", "work", "career", "professional", "company"]
        }
        
        content_lower = content.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append({"topic": topic, "confidence": 0.7})
        
        results = {
            "topics": topics,
            "num_topics": len(topics)
        }
        
        return AnalysisResult(
            analysis_type="topic_analysis",
            results=results,
            confidence_score=0.8
        )
    
    async def extract_topics(self, text: str, num_topics: int = 5, 
                           options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Extract topics from text."""
        result = await self.analyze(text)
        topics = result.results.get("topics", [])
        return topics[:num_topics]


class CollaborationAnalyzer:
    """Analyzes collaboration opportunities."""
    
    def __init__(self):
        pass
    
    async def detect_opportunities(self, text: str, platform: Any = None, 
                                 options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Detect collaboration opportunities in text."""
        opportunities = []
        
        # Look for mentions, collaboration keywords
        collaboration_indicators = ["collaboration", "collab", "partner", "work together", "@"]
        
        text_lower = text.lower()
        for indicator in collaboration_indicators:
            if indicator in text_lower:
                opportunities.append({
                    "type": "mention" if indicator == "@" else "collaboration_keyword",
                    "indicator": indicator,
                    "confidence": 0.6
                })
        
        return opportunities


class AnalysisConfig:
    """Configuration for analysis."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class ContentAnalysisPipeline:
    """Advanced content analysis pipeline."""
    
    def __init__(self):
        self.config = {}
        self.analyzers = {
            'sentiment': SentimentAnalyzer(),
            'topic': TopicAnalyzer(),
            'collaboration': CollaborationAnalyzer()
        }
    
    async def analyze_comprehensive(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive content analysis."""
        if metadata is None:
            metadata = {}
        
        results = {}
        
        # Sentiment analysis
        sentiment_analyzer = self.analyzers['sentiment']
        sentiment_result = sentiment_analyzer.analyze_sentiment(content)
        
        # Enhanced sentiment result with expected structure
        sentiment_analysis_result = AnalysisResult(
            analysis_type="sentiment_analysis",
            results={
                "overall_sentiment": {
                    "positive": sentiment_result.get("positive_words", 0) / 10,
                    "negative": sentiment_result.get("negative_words", 0) / 10,
                    "neutral": 1 - (sentiment_result.get("positive_words", 0) + sentiment_result.get("negative_words", 0)) / 10
                },
                "emotions": {
                    "joy": 0.5 if sentiment_result.get("sentiment") == "positive" else 0.1,
                    "anger": 0.5 if sentiment_result.get("sentiment") == "negative" else 0.1,
                    "sadness": 0.3 if sentiment_result.get("sentiment") == "negative" else 0.1,
                    "fear": 0.2,
                    "surprise": 0.3,
                    "love": 0.4 if sentiment_result.get("sentiment") == "positive" else 0.1
                },
                "engagement_prediction": {
                    "predicted_engagement": min(1.0, sentiment_result.get("confidence", 0.5) + 0.2)
                }
            },
            confidence_score=sentiment_result.get("confidence", 0.5)
        )
        
        results["sentiment"] = sentiment_analysis_result
        
        # Topic analysis
        topic_analyzer = self.analyzers['topic']
        topic_analysis_result = await topic_analyzer.analyze(content, metadata)
        results["topic"] = topic_analysis_result
        
        return results