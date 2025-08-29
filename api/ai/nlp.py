"""Natural Language Processing: sentiment analysis, keyword extraction, content classification."""

import re
from typing import Dict, List, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)

# Try to import spacy, fallback to None if not available
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available, using fallback NLP implementation")


class TextAnalyzer:
    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except OSError:
                logger.warning("spaCy model 'en_core_web_sm' not found, using fallback")
                self.nlp = None
        else:
            logger.info("Using fallback NLP implementation")

    def analyze_sentiment(self, text: str) -> Dict:
        """Simple sentiment analysis using word scoring."""
        # Basic positive/negative word lists
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'awesome',
            'brilliant', 'perfect', 'beautiful', 'best', 'incredible', 'outstanding'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'angry',
            'sad', 'disappointed', 'frustrated', 'worst', 'ugly', 'boring',
            'annoying', 'stupid', 'useless', 'poor', 'weak', 'disgusting'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        
        positive_score = sum(1 for word in words if word in positive_words)
        negative_score = sum(1 for word in words if word in negative_words)
        
        total_score = positive_score - negative_score
        
        if total_score > 0:
            sentiment = "positive"
        elif total_score < 0:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "confidence": min(abs(total_score) / max(len(words), 1) * 10, 1.0),
            "positive_score": positive_score,
            "negative_score": negative_score,
            "word_count": len(words)
        }

    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """Extract important keywords from text."""
        if self.nlp:
            doc = self.nlp(text)
            # Extract named entities and important nouns
            keywords = []
            
            # Named entities
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'PRODUCT', 'EVENT']:
                    keywords.append(ent.text.lower())
            
            # Important POS tags
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN'] and 
                    not token.is_stop and 
                    len(token.text) > 2 and
                    token.text.isalpha()):
                    keywords.append(token.lemma_.lower())
        else:
            # Fallback: simple word frequency
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            # Remove common stop words
            stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'had', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
            keywords = [w for w in words if w not in stop_words]
        
        # Count and return most frequent
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(top_k)]

    def classify_content(self, text: str) -> Dict:
        """Classify content type and topics."""
        text_lower = text.lower()
        
        # Topic classification
        topics = {
            'music': ['music', 'song', 'album', 'artist', 'band', 'concert', 'guitar', 'piano', 'drums', 'vocals'],
            'technology': ['tech', 'software', 'computer', 'digital', 'ai', 'machine learning', 'coding', 'programming'],
            'lifestyle': ['food', 'travel', 'fashion', 'health', 'fitness', 'beauty', 'home', 'family'],
            'business': ['business', 'marketing', 'sales', 'finance', 'entrepreneur', 'startup', 'company'],
            'entertainment': ['movie', 'film', 'tv', 'show', 'celebrity', 'entertainment', 'comedy', 'drama'],
            'education': ['learn', 'study', 'school', 'university', 'education', 'teaching', 'tutorial']
        }
        
        topic_scores = {}
        words = re.findall(r'\b\w+\b', text_lower)
        
        for topic, keywords in topics.items():
            score = sum(1 for word in words if word in keywords)
            topic_scores[topic] = score
        
        # Determine primary topic
        primary_topic = max(topic_scores.keys(), key=lambda k: topic_scores[k]) if any(topic_scores.values()) else 'general'
        
        return {
            "primary_topic": primary_topic,
            "topic_scores": topic_scores,
            "content_length": len(text),
            "reading_time_minutes": max(1, len(words) // 200)  # ~200 WPM average
        }

    def extract_hashtags_mentions(self, text: str) -> Dict:
        """Extract hashtags and mentions from social media text."""
        hashtags = re.findall(r'#\w+', text)
        mentions = re.findall(r'@\w+', text)
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
        return {
            "hashtags": hashtags,
            "mentions": mentions,
            "urls": urls,
            "hashtag_count": len(hashtags),
            "mention_count": len(mentions),
            "url_count": len(urls)
        }
