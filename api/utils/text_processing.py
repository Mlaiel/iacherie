"""Text Processing Utilities for IA Influencer Agent Platform
Advanced text analysis, natural language processing, and content optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""import re
import string
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
import spacy
from spacy import displacy
import textstat
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter, defaultdict
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import logging
import asyncio
import aiohttp
import json
from concurrent.futures import ThreadPoolExecutor
import pickle
from pathlib import Path
import hashlib
import unicodedata
from langdetect import detect, LangDetectError
import emoji
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    nltk.download('maxent_ne_chunker', quiet=True)
    nltk.download('words', quiet=True)
except Exception as e:
    logger.warning(f"Failed to download NLTK data: {str(e)}")


@dataclass
class TextStats:
    """Text statistics container"""    character_count: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    average_sentence_length: float
    average_word_length: float
    syllable_count: int
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    gunning_fog_index: float
    automated_readability_index: float
    coleman_liau_index: float
    reading_time_minutes: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'character_count': self.character_count,
            'word_count': self.word_count,
            'sentence_count': self.sentence_count,
            'paragraph_count': self.paragraph_count,
            'average_sentence_length': round(self.average_sentence_length, 2),
            'average_word_length': round(self.average_word_length, 2),
            'syllable_count': self.syllable_count,
            'flesch_reading_ease': round(self.flesch_reading_ease, 2),
            'flesch_kincaid_grade': round(self.flesch_kincaid_grade, 2),
            'gunning_fog_index': round(self.gunning_fog_index, 2),
            'automated_readability_index': round(self.automated_readability_index, 2),
            'coleman_liau_index': round(self.coleman_liau_index, 2),
            'reading_time_minutes': round(self.reading_time_minutes, 2)
        }


@dataclass
class SentimentAnalysis:
    """Sentiment analysis results"""    polarity: float  # -1 (negative) to 1 (positive)
    subjectivity: float  # 0 (objective) to 1 (subjective)
    sentiment_label: str  # 'positive', 'negative', 'neutral'
    confidence: float
    emotions: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'polarity': round(self.polarity, 3),
            'subjectivity': round(self.subjectivity, 3),
            'sentiment_label': self.sentiment_label,
            'confidence': round(self.confidence, 3),
            'emotions': {k: round(v, 3) for k, v in self.emotions.items()}
        }


@dataclass
class KeywordAnalysis:
    """Keyword extraction results"""    keywords: List[Dict[str, Any]]
    key_phrases: List[Dict[str, Any]]
    named_entities: List[Dict[str, Any]]
    hashtags: List[str]
    mentions: List[str]
    urls: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'keywords': self.keywords,
            'key_phrases': self.key_phrases,
            'named_entities': self.named_entities,
            'hashtags': self.hashtags,
            'mentions': self.mentions,
            'urls': self.urls
        }


@dataclass
class LanguageAnalysis:
    """Language detection and analysis"""    detected_language: str
    confidence: float
    supported_languages: List[str]
    mixed_languages: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'detected_language': self.detected_language,
            'confidence': round(self.confidence, 3),
            'supported_languages': self.supported_languages,
            'mixed_languages': self.mixed_languages
        }


@dataclass
class ContentOptimization:
    """Content optimization suggestions"""    seo_score: float
    readability_score: float
    engagement_score: float
    suggestions: List[str]
    optimized_title: Optional[str] = None
    optimized_description: Optional[str] = None
    recommended_hashtags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'seo_score': round(self.seo_score, 2),
            'readability_score': round(self.readability_score, 2),
            'engagement_score': round(self.engagement_score, 2),
            'suggestions': self.suggestions,
            'optimized_title': self.optimized_title,
            'optimized_description': self.optimized_description,
            'recommended_hashtags': self.recommended_hashtags
        }


class TextPreprocessor:
    """Advanced text preprocessing and cleaning"""    
    def __init__(self, language: str = 'english'):
        self.language = language
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        
        try:
            self.stop_words = set(stopwords.words(language))
        except OSError:
            self.stop_words = set()
            logger.warning(f"Stop words not available for language: {language}")
        
        # Load spaCy model for advanced NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy English model not available. Some features will be limited.")
            self.nlp = None
    
    def clean_text(self, text: str, 
                   remove_punctuation: bool = True,
                   remove_numbers: bool = False,
                   remove_stopwords: bool = True,
                   lowercase: bool = True,
                   remove_extra_whitespace: bool = True) -> str:
        """Comprehensive text cleaning"""        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove emojis (optional)
        text = self._remove_emojis(text)
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Convert to lowercase
        if lowercase:
            text = text.lower()
        
        # Remove punctuation
        if remove_punctuation:
            text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove numbers
        if remove_numbers:
            text = re.sub(r'\d+', '', text)
        
        # Remove extra whitespace
        if remove_extra_whitespace:
            text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove stopwords
        if remove_stopwords and self.stop_words:
            words = word_tokenize(text)
            text = ' '.join([word for word in words if word not in self.stop_words])
        
        return text
    
    def extract_social_elements(self, text: str) -> Dict[str, List[str]]:
        """Extract hashtags, mentions, and URLs from text"""        hashtags = re.findall(r'#\w+', text)
        mentions = re.findall(r'@\w+', text)
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
        return {
            'hashtags': hashtags,
            'mentions': mentions,
            'urls': urls
        }
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize text into sentences"""        return sent_tokenize(text)
    
    def tokenize_words(self, text: str) -> List[str]:
        """Tokenize text into words"""        return word_tokenize(text)
    
    def stem_words(self, words: List[str]) -> List[str]:
        """Stem words using Porter Stemmer"""        return [self.stemmer.stem(word) for word in words]
    
    def lemmatize_words(self, words: List[str]) -> List[str]:
        """Lemmatize words"""        return [self.lemmatizer.lemmatize(word) for word in words]
    
    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text"""        return emoji.demojize(text, delimiters=("", ""))


class TextAnalyzer:
    """Advanced text analysis and statistics"""    
    def __init__(self, language: str = 'english'):
        self.language = language
        self.preprocessor = TextPreprocessor(language)
    
    def analyze_text(self, text: str) -> TextStats:
        """Comprehensive text analysis"""        if not text:
            return TextStats(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        # Basic counts
        character_count = len(text)
        words = word_tokenize(text)
        word_count = len(words)
        sentences = sent_tokenize(text)
        sentence_count = len(sentences)
        paragraphs = text.split('\n\n')
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        # Average lengths
        average_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        average_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Readability metrics
        syllable_count = textstat.syllable_count(text)
        flesch_reading_ease = textstat.flesch_reading_ease(text)
        flesch_kincaid_grade = textstat.flesch_kincaid(text)
        gunning_fog_index = textstat.gunning_fog(text)
        automated_readability_index = textstat.automated_readability_index(text)
        coleman_liau_index = textstat.coleman_liau_index(text)
        
        # Reading time (average 200 words per minute)
        reading_time_minutes = word_count / 200
        
        return TextStats(
            character_count=character_count,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            average_sentence_length=average_sentence_length,
            average_word_length=average_word_length,
            syllable_count=syllable_count,
            flesch_reading_ease=flesch_reading_ease,
            flesch_kincaid_grade=flesch_kincaid_grade,
            gunning_fog_index=gunning_fog_index,
            automated_readability_index=automated_readability_index,
            coleman_liau_index=coleman_liau_index,
            reading_time_minutes=reading_time_minutes
        )
    
    def analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """Analyze sentiment using TextBlob and advanced techniques"""        if not text:
            return SentimentAnalysis(0, 0, 'neutral', 0)
        
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Determine sentiment label
        if polarity > 0.1:
            sentiment_label = 'positive'
        elif polarity < -0.1:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        # Calculate confidence based on polarity strength
        confidence = abs(polarity)
        
        # Basic emotion detection (simplified)
        emotions = self._detect_emotions(text)
        
        return SentimentAnalysis(
            polarity=polarity,
            subjectivity=subjectivity,
            sentiment_label=sentiment_label,
            confidence=confidence,
            emotions=emotions
        )
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> KeywordAnalysis:
        """Extract keywords, key phrases, and named entities"""        if not text:
            return KeywordAnalysis([], [], [], [], [], [])
        
        # Extract social elements
        social_elements = self.preprocessor.extract_social_elements(text)
        
        # Clean text for keyword extraction
        clean_text = self.preprocessor.clean_text(text, remove_stopwords=True)
        
        # Extract keywords using TF-IDF
        keywords = self._extract_tfidf_keywords(clean_text, max_keywords)
        
        # Extract key phrases using N-grams
        key_phrases = self._extract_key_phrases(text, max_phrases=max_keywords//2)
        
        # Extract named entities
        named_entities = self._extract_named_entities(text)
        
        return KeywordAnalysis(
            keywords=keywords,
            key_phrases=key_phrases,
            named_entities=named_entities,
            hashtags=social_elements['hashtags'],
            mentions=social_elements['mentions'],
            urls=social_elements['urls']
        )
    
    def detect_language(self, text: str) -> LanguageAnalysis:
        """Detect language of text"""        if not text or len(text.strip()) < 10:
            return LanguageAnalysis('unknown', 0, [])
        
        try:
            detected_lang = detect(text)
            confidence = 0.8  # Simplified confidence score
            
            supported_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh']
            
            return LanguageAnalysis(
                detected_language=detected_lang,
                confidence=confidence,
                supported_languages=supported_languages
            )
            
        except LangDetectError:
            return LanguageAnalysis('unknown', 0, [])
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""        if not text1 or not text2:
            return 0.0
        
        # Clean texts
        clean_text1 = self.preprocessor.clean_text(text1)
        clean_text2 = self.preprocessor.clean_text(text2)
        
        # Vectorize using TF-IDF
        vectorizer = TfidfVectorizer()
        
        try:
            tfidf_matrix = vectorizer.fit_transform([clean_text1, clean_text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity
        except ValueError:
            return 0.0
    
    def _extract_tfidf_keywords(self, text: str, max_keywords: int) -> List[Dict[str, Any]]:
        """Extract keywords using TF-IDF"""        try:
            vectorizer = TfidfVectorizer(max_features=max_keywords, ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform([text])
            
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            keywords = []
            for i, score in enumerate(scores):
                if score > 0:
                    keywords.append({
                        'keyword': feature_names[i],
                        'score': float(score),
                        'type': 'tfidf'
                    })
            
            # Sort by score
            keywords.sort(key=lambda x: x['score'], reverse=True)
            return keywords
            
        except ValueError:
            return []
    
    def _extract_key_phrases(self, text: str, max_phrases: int) -> List[Dict[str, Any]]:
        """Extract key phrases using N-grams"""        try:
            # Extract 2-gram and 3-gram phrases
            vectorizer = CountVectorizer(ngram_range=(2, 3), max_features=max_phrases)
            count_matrix = vectorizer.fit_transform([text])
            
            feature_names = vectorizer.get_feature_names_out()
            counts = count_matrix.toarray()[0]
            
            phrases = []
            for i, count in enumerate(counts):
                if count > 0:
                    phrases.append({
                        'phrase': feature_names[i],
                        'frequency': int(count),
                        'type': 'ngram'
                    })
            
            # Sort by frequency
            phrases.sort(key=lambda x: x['frequency'], reverse=True)
            return phrases
            
        except ValueError:
            return []
    
    def _extract_named_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities"""        entities = []
        
        if self.preprocessor.nlp:
            # Use spaCy for named entity recognition
            doc = self.preprocessor.nlp(text)
            
            for ent in doc.ents:
                entities.append({
                    'entity': ent.text,
                    'label': ent.label_,
                    'description': spacy.explain(ent.label_),
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'type': 'spacy'
                })
        else:
            # Fallback to NLTK
            try:
                tokens = word_tokenize(text)
                pos_tags = pos_tag(tokens)
                chunks = ne_chunk(pos_tags)
                
                for chunk in chunks:
                    if hasattr(chunk, 'label'):
                        entity_text = ' '.join([token for token, pos in chunk.leaves()])
                        entities.append({
                            'entity': entity_text,
                            'label': chunk.label(),
                            'type': 'nltk'
                        })
            except Exception as e:
                logger.warning(f"Named entity extraction failed: {str(e)}")
        
        return entities
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Basic emotion detection using keyword matching"""        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'amazing', 'wonderful', 'great', 'love', 'awesome'],
            'sadness': ['sad', 'depressed', 'unhappy', 'disappointed', 'down', 'upset'],
            'anger': ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'hate'],
            'fear': ['afraid', 'scared', 'worried', 'anxious', 'nervous', 'concerned'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned'],
            'disgust': ['disgusting', 'awful', 'terrible', 'horrible', 'sick']
        }
        
        text_lower = text.lower()
        emotions = {}
        
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            emotions[emotion] = count / len(keywords) if keywords else 0
        
        return emotions


class ContentOptimizer:
    """Content optimization for SEO and engagement"""    
    def __init__(self):
        self.text_analyzer = TextAnalyzer()
        
        # Popular hashtags for different categories
        self.popular_hashtags = {
            'music': ['#music', '#song', '#artist', '#newmusic', '#musician', '#producer'],
            'video': ['#video', '#content', '#creator', '#viral', '#trending', '#entertainment'],
            'lifestyle': ['#lifestyle', '#daily', '#life', '#motivation', '#inspiration'],
            'technology': ['#tech', '#technology', '#innovation', '#digital', '#future'],
            'art': ['#art', '#artist', '#creative', '#design', '#artwork', '#gallery'],
            'fitness': ['#fitness', '#workout', '#health', '#gym', '#training', '#wellness']
        }
    
    def optimize_content(self, title: str, description: str, 
                        category: Optional[str] = None,
                        target_keywords: Optional[List[str]] = None) -> ContentOptimization:
        """Optimize content for better engagement and SEO"""        suggestions = []
        
        # Analyze current content
        title_stats = self.text_analyzer.analyze_text(title)
        desc_stats = self.text_analyzer.analyze_text(description)
        title_sentiment = self.text_analyzer.analyze_sentiment(title)
        desc_sentiment = self.text_analyzer.analyze_sentiment(description)
        
        # SEO Score calculation
        seo_score = self._calculate_seo_score(title, description, target_keywords)
        
        # Readability Score
        readability_score = self._calculate_readability_score(desc_stats)
        
        # Engagement Score
        engagement_score = self._calculate_engagement_score(title, description, title_sentiment, desc_sentiment)
        
        # Generate suggestions
        if title_stats.word_count > 10:
            suggestions.append("Consider shortening the title - optimal length is 6-10 words")
        
        if title_stats.word_count < 3:
            suggestions.append("Title is too short - consider adding more descriptive words")
        
        if desc_stats.word_count < 20:
            suggestions.append("Description is too short - add more details to improve SEO")
        
        if desc_stats.word_count > 160:
            suggestions.append("Description might be too long for some platforms - consider condensing")
        
        if readability_score < 50:
            suggestions.append("Content might be difficult to read - consider simplifying language")
        
        if title_sentiment.polarity < 0:
            suggestions.append("Consider using more positive language in the title")
        
        # Generate optimized versions
        optimized_title = self._optimize_title(title, title_stats, target_keywords)
        optimized_description = self._optimize_description(description, desc_stats, target_keywords)
        
        # Recommend hashtags
        recommended_hashtags = self._recommend_hashtags(title + " " + description, category)
        
        return ContentOptimization(
            seo_score=seo_score,
            readability_score=readability_score,
            engagement_score=engagement_score,
            suggestions=suggestions,
            optimized_title=optimized_title,
            optimized_description=optimized_description,
            recommended_hashtags=recommended_hashtags
        )
    
    def generate_variations(self, text: str, count: int = 5) -> List[str]:
        """Generate content variations"""        variations = []
        
        # Synonym replacement variations
        blob = TextBlob(text)
        
        for _ in range(count):
            variation = text
            words = word_tokenize(text)
            
            # Replace some words with synonyms
            for i, word in enumerate(words):
                if len(word) > 4 and np.random.random() < 0.3:  # 30% chance to replace
                    try:
                        synsets = blob.noun_phrases if word.lower() in text.lower() else []
                        if synsets:
                            synonym = np.random.choice(synsets)
                            variation = variation.replace(word, synonym, 1)
                    except:
                        pass
            
            if variation != text and variation not in variations:
                variations.append(variation)
        
        return variations
    
    def analyze_hashtag_performance(self, hashtags: List[str]) -> Dict[str, Any]:
        """Analyze hashtag performance (simplified simulation)"""        performance_data = {}
        
        for hashtag in hashtags:
            # Simulate performance metrics
            hashtag_clean = hashtag.lower().replace('#', '')
            
            # Basic performance calculation based on hashtag characteristics
            length_score = max(0, 1 - abs(len(hashtag_clean) - 10) / 20)  # Optimal length around 10 chars
            
            performance_data[hashtag] = {
                'estimated_reach': np.random.randint(1000, 100000),
                'competition_level': np.random.choice(['low', 'medium', 'high']),
                'trending_score': length_score * np.random.random(),
                'recommendation': 'use' if length_score > 0.5 else 'consider alternatives'
            }
        
        return performance_data
    
    def _calculate_seo_score(self, title: str, description: str, 
                           target_keywords: Optional[List[str]]) -> float:
        """Calculate SEO score"""        score = 0
        
        # Title length (6-10 words is optimal)
        title_words = len(word_tokenize(title))
        if 6 <= title_words <= 10:
            score += 20
        elif 4 <= title_words <= 12:
            score += 10
        
        # Description length (20-160 words is optimal)
        desc_words = len(word_tokenize(description))
        if 20 <= desc_words <= 160:
            score += 20
        elif 10 <= desc_words <= 200:
            score += 10
        
        # Keyword presence
        if target_keywords:
            title_lower = title.lower()
            desc_lower = description.lower()
            
            keyword_score = 0
            for keyword in target_keywords:
                if keyword.lower() in title_lower:
                    keyword_score += 15
                if keyword.lower() in desc_lower:
                    keyword_score += 10
            
            score += min(keyword_score, 40)  # Max 40 points for keywords
        
        # Sentiment bonus
        sentiment = self.text_analyzer.analyze_sentiment(title)
        if sentiment.polarity > 0.2:
            score += 10
        
        # Social elements
        social = self.text_analyzer.preprocessor.extract_social_elements(title + " " + description)
        if social['hashtags']:
            score += 5
        
        return min(score, 100)  # Cap at 100
    
    def _calculate_readability_score(self, text_stats: TextStats) -> float:
        """Calculate readability score"""        # Use Flesch Reading Ease as base
        flesch_score = text_stats.flesch_reading_ease
        
        # Adjust based on other factors
        if text_stats.average_sentence_length > 20:
            flesch_score -= 10  # Long sentences reduce readability
        
        if text_stats.average_word_length > 6:
            flesch_score -= 10  # Complex words reduce readability
        
        return max(0, min(100, flesch_score))
    
    def _calculate_engagement_score(self, title: str, description: str,
                                  title_sentiment: SentimentAnalysis,
                                  desc_sentiment: SentimentAnalysis) -> float:
        """Calculate engagement score"""        score = 0
        
        # Sentiment bonus
        if title_sentiment.polarity > 0.2:
            score += 20
        if desc_sentiment.polarity > 0.1:
            score += 15
        
        # Emotional words bonus
        emotional_words = [
            'amazing', 'incredible', 'awesome', 'fantastic', 'wonderful',
            'shocking', 'surprising', 'unbelievable', 'exclusive', 'secret',
            'must', 'need', 'important', 'urgent', 'breaking', 'new'
        ]
        
        combined_text = (title + " " + description).lower()
        emotional_count = sum(1 for word in emotional_words if word in combined_text)
        score += min(emotional_count * 5, 25)  # Max 25 points
        
        # Question marks and exclamation points
        punctuation_score = combined_text.count('!') + combined_text.count('?')
        score += min(punctuation_score * 3, 15)  # Max 15 points
        
        # Numbers in title (perform well)
        if re.search(r'\d+', title):
            score += 10
        
        # Action words
        action_words = ['learn', 'discover', 'find', 'get', 'make', 'create', 'build', 'achieve']
        action_count = sum(1 for word in action_words if word in combined_text)
        score += min(action_count * 3, 15)  # Max 15 points
        
        return min(score, 100)
    
    def _optimize_title(self, title: str, stats: TextStats, 
                       keywords: Optional[List[str]]) -> str:
        """Generate optimized title"""        # If title is already good, make minor improvements
        words = word_tokenize(title)
        
        # Add emotional words if missing
        emotional_words = ['Amazing', 'Incredible', 'Ultimate', 'Perfect', 'Essential']
        if not any(word.lower() in title.lower() for word in emotional_words):
            if len(words) < 8:
                title = f"{np.random.choice(emotional_words)} {title}"
        
        # Add numbers if missing and appropriate
        if not re.search(r'\d+', title) and len(words) < 9:
            numbers = ['5', '10', '7', '3']
            title = f"{np.random.choice(numbers)} {title}"
        
        return title
    
    def _optimize_description(self, description: str, stats: TextStats,
                            keywords: Optional[List[str]]) -> str:
        """Generate optimized description"""        # Add keywords naturally if provided
        optimized = description
        
        if keywords:
            for keyword in keywords[:2]:  # Add up to 2 keywords
                if keyword.lower() not in description.lower():
                    optimized += f" {keyword}."
        
        # Add call-to-action if missing
        cta_words = ['like', 'share', 'comment', 'subscribe', 'follow']
        if not any(word in optimized.lower() for word in cta_words):
            ctas = [
                "Don't forget to like and share!",
                "Let me know what you think in the comments!",
                "Follow for more content like this!"
            ]
            optimized += f" {np.random.choice(ctas)}"
        
        return optimized
    
    def _recommend_hashtags(self, text: str, category: Optional[str]) -> List[str]:
        """Recommend hashtags based on content"""        recommended = []
        
        # Add category-specific hashtags
        if category and category.lower() in self.popular_hashtags:
            recommended.extend(self.popular_hashtags[category.lower()][:3])
        
        # Extract keywords and convert to hashtags
        keywords = self.text_analyzer.extract_keywords(text, max_keywords=10)
        
        for keyword_data in keywords.keywords[:5]:
            keyword = keyword_data['keyword']
            # Convert to hashtag format
            hashtag = '#' + keyword.replace(' ', '').replace('-', '')
            if len(hashtag) > 3 and len(hashtag) < 25:
                recommended.append(hashtag)
        
        # Add trending general hashtags
        general_hashtags = ['#viral', '#trending', '#content', '#creator', '#follow']
        recommended.extend(general_hashtags[:2])
        
        # Remove duplicates and return
        return list(dict.fromkeys(recommended))


class TextModerator:
    """Content moderation and filtering"""    
    def __init__(self):
        self.inappropriate_words = self._load_inappropriate_words()
        self.spam_patterns = self._load_spam_patterns()
    
    def moderate_content(self, text: str) -> Dict[str, Any]:
        """Moderate text content for inappropriate material"""        issues = []
        severity = 'clean'
        
        # Check for inappropriate words
        inappropriate_found = self._check_inappropriate_words(text)
        if inappropriate_found:
            issues.extend([f"Inappropriate language: {word}" for word in inappropriate_found])
            severity = 'inappropriate'
        
        # Check for spam patterns
        spam_detected = self._check_spam_patterns(text)
        if spam_detected:
            issues.extend(spam_detected)
            if severity != 'inappropriate':
                severity = 'spam'
        
        # Check for excessive caps
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        if caps_ratio > 0.7:
            issues.append("Excessive use of capital letters")
            if severity == 'clean':
                severity = 'suspicious'
        
        # Check for repeated characters
        if re.search(r'(.)\1{4,}', text):
            issues.append("Excessive repeated characters")
            if severity == 'clean':
                severity = 'suspicious'
        
        return {
            'severity': severity,
            'issues': issues,
            'approved': severity == 'clean' or severity == 'suspicious',
            'requires_review': severity in ['inappropriate', 'spam']
        }
    
    def _load_inappropriate_words(self) -> Set[str]:
        """Load inappropriate words list"""        # In a real implementation, load from a comprehensive database
        return {
            'spam', 'scam', 'fake', 'hate', 'offensive'
            # Add more words as needed
        }
    
    def _load_spam_patterns(self) -> List[str]:
        """Load spam detection patterns"""        return [
            r'(?:click|visit|check).{0,20}(?:link|url|website)',
            r'(?:buy|purchase|order).{0,20}(?:now|today|immediately)',
            r'(?:free|win|prize).{0,20}(?:money|cash|gift)',
            r'(?:urgent|limited|exclusive).{0,20}(?:offer|deal|time)',
        ]
    
    def _check_inappropriate_words(self, text: str) -> List[str]:
        """Check for inappropriate words"""        text_lower = text.lower()
        found = []
        
        for word in self.inappropriate_words:
            if word in text_lower:
                found.append(word)
        
        return found
    
    def _check_spam_patterns(self, text: str) -> List[str]:
        """Check for spam patterns"""        issues = []
        
        for pattern in self.spam_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(f"Spam pattern detected: promotional content")
        
        return issues


class WordCloudGenerator:
    """Generate word clouds from text"""    
    def __init__(self):
        self.preprocessor = TextPreprocessor()
    
    def generate_wordcloud(self, text: str, 
                          width: int = 800, 
                          height: int = 400,
                          max_words: int = 100,
                          background_color: str = 'white') -> str:
        """Generate word cloud and return as base64 image"""        if not text:
            return ""
        
        try:
            # Clean and preprocess text
            clean_text = self.preprocessor.clean_text(
                text, 
                remove_punctuation=True, 
                remove_stopwords=True
            )
            
            if not clean_text:
                return ""
            
            # Generate word cloud
            wordcloud = WordCloud(
                width=width,
                height=height,
                max_words=max_words,
                background_color=background_color,
                relative_scaling=0.5,
                colormap='viridis'
            ).generate(clean_text)
            
            # Convert to image
            plt.figure(figsize=(width/100, height/100))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            
            # Save to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
            buffer.seek(0)
            
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            logger.error(f"Word cloud generation failed: {str(e)}")
            return ""


class TextProcessor:
    """Main text processing coordinator"""    
    def __init__(self, language: str = 'english'):
        self.language = language
        self.analyzer = TextAnalyzer(language)
        self.optimizer = ContentOptimizer()
        self.moderator = TextModerator()
        self.wordcloud_generator = WordCloudGenerator()
    
    async def process_text_comprehensive(self, text: str,
                                       title: Optional[str] = None,
                                       category: Optional[str] = None,
                                       target_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Comprehensive text processing"""        if not text:
            return {'error': 'No text provided'}
        
        try:
            # Basic analysis
            stats = self.analyzer.analyze_text(text)
            sentiment = self.analyzer.analyze_sentiment(text)
            keywords = self.analyzer.extract_keywords(text)
            language_info = self.analyzer.detect_language(text)
            
            # Content moderation
            moderation = self.moderator.moderate_content(text)
            
            # Content optimization (if title provided)
            optimization = None
            if title:
                optimization = self.optimizer.optimize_content(
                    title, text, category, target_keywords
                )
            
            # Generate word cloud
            wordcloud_b64 = self.wordcloud_generator.generate_wordcloud(text)
            
            return {
                'text_statistics': stats.to_dict(),
                'sentiment_analysis': sentiment.to_dict(),
                'keyword_analysis': keywords.to_dict(),
                'language_analysis': language_info.to_dict(),
                'content_moderation': moderation,
                'content_optimization': optimization.to_dict() if optimization else None,
                'word_cloud': wordcloud_b64,
                'processing_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Comprehensive text processing failed: {str(e)}")
            return {'error': str(e)}
    
    def calculate_content_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        """Calculate similarity between two pieces of content"""        similarity_score = self.analyzer.calculate_similarity(text1, text2)
        
        # Determine similarity level
        if similarity_score > 0.8:
            similarity_level = 'very_high'
        elif similarity_score > 0.6:
            similarity_level = 'high'
        elif similarity_score > 0.4:
            similarity_level = 'medium'
        elif similarity_score > 0.2:
            similarity_level = 'low'
        else:
            similarity_level = 'very_low'
        
        return {
            'similarity_score': round(similarity_score, 4),
            'similarity_level': similarity_level,
            'potentially_duplicate': similarity_score > 0.7
        }
    
    def batch_process_texts(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Process multiple texts efficiently"""        results = []
        
        for i, text in enumerate(texts):
            try:
                result = {
                    'index': i,
                    'text_stats': self.analyzer.analyze_text(text).to_dict(),
                    'sentiment': self.analyzer.analyze_sentiment(text).to_dict(),
                    'moderation': self.moderator.moderate_content(text)
                }
                results.append(result)
            except Exception as e:
                results.append({
                    'index': i,
                    'error': str(e)
                })
        
        return results


class TextProcessingError(Exception):
    """Custom exception for text processing errors"""    pass
