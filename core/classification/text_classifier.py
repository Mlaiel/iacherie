"""Text Content Classification System

Advanced AI-powered text classification for content protection and analysis.
Provides sentiment analysis, genre detection, language identification, and similarity matching.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Content Protection
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + DBA + Security + Microservices + Audio + IA Prompt Engineer

Copyright © 2025 Fahed Mlaiel. All rights reserved.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing and collaboration.

⚠️ STRONG WARNING: This code and concept are the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will be prosecuted
to the full extent of the law.
"""
import re
import hashlib
import numpy as np
import torch
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from pathlib import Path
from collections import Counter
import spacy
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    pipeline, BertTokenizer, BertModel, RobertaTokenizer, RobertaModel
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import langdetect
from textstat import flesch_reading_ease, flesch_kincaid_grade
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer

from ..engines.ml_engine import MLEngine
from ..processors.text_processor import TextProcessor
from ...utils.cache_manager import cache_result
from ...utils.metrics import track_performance
from ...utils.exceptions import ClassificationError
from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class TextContentClassifier:
    """    Enterprise-grade text content classification system.
    
    Features:
    - Content type classification (lyrics, blog, script, etc.)
    - Sentiment and emotion analysis
    - Language detection and proficiency assessment
    - Genre and theme classification
    - Quality and readability scoring
    - Similarity matching for plagiarism detection
    - Named entity recognition
    - Keyword and topic extraction
    - Copyright violation detection
    """    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize text classifier with NLP models."""        self.settings = get_settings()
        self.ml_engine = MLEngine()
        self.text_processor = TextProcessor()
        
        # Load models and components
        self._load_models(model_path)
        self._init_components()
        
        # Classification thresholds
        self.thresholds = {
            'similarity': 0.85,
            'quality_score': 0.70,
            'sentiment_confidence': 0.75,
            'language_confidence': 0.80,
            'copyright_threshold': 0.90
        }

    def _load_models(self, model_path: Optional[str]):
        """Load and initialize NLP models."""        try:
            # BERT for general text understanding
            self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            self.bert_model = BertModel.from_pretrained('bert-base-uncased')
            
            # RoBERTa for sentiment analysis
            self.roberta_tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
            self.roberta_model = RobertaModel.from_pretrained('roberta-base')
            
            # Sentence transformer for semantic similarity
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Sentiment analysis pipeline
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Emotion analysis pipeline
            self.emotion_analyzer = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base"
            )
            
            # Load spaCy model for NER and linguistic analysis
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy English model not found. Some features will be limited.")
                self.nlp = None
            
            # Initialize NLTK components
            try:
                nltk.download('vader_lexicon', quiet=True)
                self.vader_analyzer = SentimentIntensityAnalyzer()
            except Exception as e:
                logger.warning(f"Could not initialize NLTK VADER: {e}")
                self.vader_analyzer = None
            
            logger.info("Text classification models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise ClassificationError(f"Failed to load models: {e}")

    def _init_components(self):
        """Initialize additional text processing components."""        # TF-IDF vectorizer for keyword extraction
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
        # Content type categories
        self.content_types = {
            'lyrics': ['song', 'lyrics', 'verse', 'chorus', 'bridge', 'hook'],
            'blog_post': ['blog', 'article', 'post', 'opinion', 'review'],
            'script': ['script', 'dialogue', 'scene', 'act', 'screenplay'],
            'description': ['description', 'bio', 'about', 'profile'],
            'social_media': ['tweet', 'post', 'status', 'update', 'caption'],
            'news': ['news', 'breaking', 'report', 'journalist', 'press'],
            'academic': ['research', 'study', 'analysis', 'paper', 'thesis'],
            'creative': ['story', 'poem', 'fiction', 'creative', 'narrative'],
            'technical': ['documentation', 'manual', 'guide', 'tutorial', 'how-to']
        }
        
        # Music-related genres
        self.music_genres = [
            'pop', 'rock', 'hip-hop', 'rap', 'r&b', 'country', 'jazz', 'blues',
            'electronic', 'dance', 'classical', 'folk', 'reggae', 'punk',
            'metal', 'alternative', 'indie', 'soul', 'funk', 'disco'
        ]
        
        # Emotional categories
        self.emotions = [
            'joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust',
            'love', 'excitement', 'calm', 'anxiety', 'hope', 'nostalgia'
        ]

    @cache_result(ttl=3600)
    @track_performance
    def classify_text(self, text: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """        Comprehensive text classification and analysis.
        
        Args:
            text: Input text to classify
            options: Classification options and parameters
            
        Returns:
            Classification results with confidence scores
        """        try:
            if not text or not isinstance(text, str):
                raise ClassificationError("Invalid text input")
            
            # Clean and preprocess text
            cleaned_text = self.text_processor.clean_text(text)
            
            results = {
                'original_text': text[:500] + "..." if len(text) > 500 else text,
                'cleaned_text': cleaned_text[:500] + "..." if len(cleaned_text) > 500 else cleaned_text,
                'timestamp': self._get_timestamp(),
                'text_stats': self._get_basic_stats(text),
                'classifications': {},
                'features': {},
                'quality_metrics': {},
                'similarity_hashes': {}
            }
            
            # Core classifications
            results['classifications'].update(self._classify_content_type(cleaned_text))
            results['classifications'].update(self._classify_language(text))
            results['classifications'].update(self._analyze_sentiment(cleaned_text))
            results['classifications'].update(self._analyze_emotions(cleaned_text))
            results['classifications'].update(self._detect_genre(cleaned_text))
            
            # Feature extraction
            results['features'].update(self._extract_keywords(cleaned_text))
            results['features'].update(self._extract_entities(text))
            results['features'].update(self._extract_topics(cleaned_text))
            
            # Quality assessment
            results['quality_metrics'].update(self._assess_quality(text))
            results['quality_metrics'].update(self._assess_readability(text))
            
            # Generate similarity hashes
            results['similarity_hashes'].update(self._generate_text_hashes(cleaned_text))
            
            # Advanced analysis (optional)
            if options and options.get('detailed_analysis'):
                results['advanced'] = self._advanced_analysis(cleaned_text)
            
            return results
            
        except Exception as e:
            logger.error(f"Error classifying text: {e}")
            raise ClassificationError(f"Text classification failed: {e}")

    def _get_basic_stats(self, text: str) -> Dict[str, Any]:
        """Extract basic text statistics."""        try:
            words = text.split()
            sentences = text.split('.')
            paragraphs = text.split('\n\n')
            
            return {
                'character_count': len(text),
                'word_count': len(words),
                'sentence_count': len([s for s in sentences if s.strip()]),
                'paragraph_count': len([p for p in paragraphs if p.strip()]),
                'average_word_length': np.mean([len(word) for word in words]) if words else 0,
                'average_sentence_length': len(words) / len(sentences) if sentences else 0,
                'unique_words': len(set(word.lower() for word in words)),
                'lexical_diversity': len(set(word.lower() for word in words)) / len(words) if words else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating basic stats: {e}")
            return {}

    def _classify_content_type(self, text: str) -> Dict[str, Any]:
        """Classify the type of text content."""        try:
            text_lower = text.lower()
            
            # Score each content type based on keyword presence
            type_scores = {}
            for content_type, keywords in self.content_types.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score > 0:
                    type_scores[content_type] = score / len(keywords)
            
            # Additional heuristics
            
            # Check for verse/chorus patterns (lyrics)
            if re.search(r'\b(verse|chorus|bridge|outro|intro)\b', text_lower):
                type_scores['lyrics'] = type_scores.get('lyrics', 0) + 0.3
            
            # Check for dialogue patterns (script)
            if ':' in text and '\n' in text:
                dialogue_count = len(re.findall(r'^[A-Z][A-Z\s]+:', text, re.MULTILINE))
                if dialogue_count > 2:
                    type_scores['script'] = type_scores.get('script', 0) + 0.4
            
            # Check for hashtags and mentions (social media)
            hashtag_count = len(re.findall(r'#\w+', text))
            mention_count = len(re.findall(r'@\w+', text))
            if hashtag_count > 0 or mention_count > 0:
                type_scores['social_media'] = type_scores.get('social_media', 0) + 0.3
            
            # Determine primary content type
            if type_scores:
                primary_type = max(type_scores.items(), key=lambda x: x[1])
                sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
            else:
                primary_type = ('unknown', 0.0)
                sorted_types = []
            
            return {
                'content_type': {
                    'primary': primary_type[0],
                    'confidence': float(primary_type[1]),
                    'alternatives': [{'type': t, 'score': float(s)} for t, s in sorted_types[1:3]],
                    'is_music_related': self._is_music_related_text(text_lower)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in content type classification: {e}")
            return {'content_type': {'primary': 'unknown', 'confidence': 0.0}}

    def _classify_language(self, text: str) -> Dict[str, Any]:
        """Detect and classify language of the text."""        try:
            # Use langdetect for primary language detection
            detected_lang = langdetect.detect(text)
            confidence = langdetect.detect_langs(text)[0].prob
            
            # Get language name
            language_names = {
                'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
                'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'zh': 'Chinese',
                'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic', 'hi': 'Hindi'
            }
            
            language_name = language_names.get(detected_lang, detected_lang.upper())
            
            # Detect multiple languages
            all_languages = langdetect.detect_langs(text)
            language_breakdown = []
            for lang_obj in all_languages[:5]:  # Top 5
                lang_name = language_names.get(lang_obj.lang, lang_obj.lang.upper())
                language_breakdown.append({
                    'language': lang_name,
                    'code': lang_obj.lang,
                    'probability': float(lang_obj.prob)
                })
            
            return {
                'language_detection': {
                    'primary_language': language_name,
                    'language_code': detected_lang,
                    'confidence': float(confidence),
                    'is_multilingual': len([l for l in all_languages if l.prob > 0.1]) > 1,
                    'language_breakdown': language_breakdown
                }
            }
            
        except Exception as e:
            logger.error(f"Error in language detection: {e}")
            return {
                'language_detection': {
                    'primary_language': 'Unknown',
                    'language_code': 'unknown',
                    'confidence': 0.0
                }
            }

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment and emotional tone of the text."""        try:
            results = {}
            
            # RoBERTa-based sentiment analysis
            roberta_result = self.sentiment_analyzer(text[:512])  # Limit length
            roberta_sentiment = {
                'label': roberta_result[0]['label'].lower(),
                'confidence': float(roberta_result[0]['score'])
            }
            
            # VADER sentiment analysis (if available)
            vader_sentiment = {}
            if self.vader_analyzer:
                vader_scores = self.vader_analyzer.polarity_scores(text)
                vader_sentiment = {
                    'compound': float(vader_scores['compound']),
                    'positive': float(vader_scores['pos']),
                    'negative': float(vader_scores['neg']),
                    'neutral': float(vader_scores['neu'])
                }
            
            # Combine results
            results['sentiment_analysis'] = {
                'primary_sentiment': roberta_sentiment['label'],
                'confidence': roberta_sentiment['confidence'],
                'roberta_analysis': roberta_sentiment,
                'vader_analysis': vader_sentiment,
                'is_positive': roberta_sentiment['label'] in ['positive', 'POSITIVE'],
                'is_negative': roberta_sentiment['label'] in ['negative', 'NEGATIVE'],
                'sentiment_strength': self._calculate_sentiment_strength(roberta_sentiment, vader_sentiment)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {'sentiment_analysis': {'primary_sentiment': 'neutral', 'confidence': 0.0}}

    def _analyze_emotions(self, text: str) -> Dict[str, Any]:
        """Analyze emotions expressed in the text."""        try:
            # Use emotion classification model
            emotion_result = self.emotion_analyzer(text[:512])
            
            # Process results
            emotions = []
            for result in emotion_result:
                emotions.append({
                    'emotion': result['label'].lower(),
                    'confidence': float(result['score'])
                })
            
            # Sort by confidence
            emotions.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Categorize emotions
            primary_emotion = emotions[0] if emotions else {'emotion': 'neutral', 'confidence': 0.0}
            
            emotion_categories = {
                'positive': ['joy', 'love', 'surprise', 'optimism'],
                'negative': ['sadness', 'anger', 'fear', 'disgust', 'pessimism'],
                'neutral': ['neutral']
            }
            
            emotion_polarity = 'neutral'
            for polarity, emotion_list in emotion_categories.items():
                if primary_emotion['emotion'] in emotion_list:
                    emotion_polarity = polarity
                    break
            
            return {
                'emotion_analysis': {
                    'primary_emotion': primary_emotion['emotion'],
                    'confidence': primary_emotion['confidence'],
                    'emotion_polarity': emotion_polarity,
                    'all_emotions': emotions[:5],  # Top 5 emotions
                    'emotional_intensity': float(primary_emotion['confidence'])
                }
            }
            
        except Exception as e:
            logger.error(f"Error in emotion analysis: {e}")
            return {'emotion_analysis': {'primary_emotion': 'neutral', 'confidence': 0.0}}

    def _detect_genre(self, text: str) -> Dict[str, Any]:
        """Detect music genre or content theme."""        try:
            text_lower = text.lower()
            
            # Music genre detection
            genre_scores = {}
            for genre in self.music_genres:
                # Direct mention
                if genre in text_lower:
                    genre_scores[genre] = genre_scores.get(genre, 0) + 1.0
                
                # Related terms
                genre_keywords = {
                    'rock': ['guitar', 'electric', 'loud', 'heavy', 'distortion'],
                    'hip-hop': ['rap', 'beats', 'rhyme', 'freestyle', 'urban'],
                    'pop': ['catchy', 'mainstream', 'radio', 'hit', 'commercial'],
                    'jazz': ['improvisation', 'saxophone', 'swing', 'blues'],
                    'classical': ['orchestra', 'symphony', 'piano', 'violin'],
                    'electronic': ['synthesizer', 'digital', 'techno', 'edm'],
                    'country': ['rural', 'southern', 'banjo', 'americana'],
                    'r&b': ['soul', 'groove', 'smooth', 'vocals']
                }
                
                keywords = genre_keywords.get(genre, [])
                keyword_score = sum(0.3 for keyword in keywords if keyword in text_lower)
                genre_scores[genre] = genre_scores.get(genre, 0) + keyword_score
            
            # General themes detection
            theme_keywords = {
                'love': ['love', 'heart', 'romance', 'relationship', 'kiss'],
                'heartbreak': ['breakup', 'goodbye', 'tears', 'lonely', 'miss'],
                'party': ['party', 'dance', 'celebration', 'fun', 'night'],
                'motivation': ['strong', 'power', 'believe', 'achieve', 'dream'],
                'nostalgia': ['remember', 'past', 'memories', 'youth', 'time'],
                'social': ['society', 'world', 'people', 'together', 'community']
            }
            
            theme_scores = {}
            for theme, keywords in theme_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score > 0:
                    theme_scores[theme] = score / len(keywords)
            
            # Determine primary genre and theme
            primary_genre = max(genre_scores.items(), key=lambda x: x[1]) if genre_scores else ('unknown', 0.0)
            primary_theme = max(theme_scores.items(), key=lambda x: x[1]) if theme_scores else ('unknown', 0.0)
            
            return {
                'genre_detection': {
                    'primary_genre': primary_genre[0],
                    'genre_confidence': float(primary_genre[1]),
                    'detected_genres': sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:3],
                    'primary_theme': primary_theme[0],
                    'theme_confidence': float(primary_theme[1]),
                    'detected_themes': sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)[:3],
                    'is_music_genre': primary_genre[0] in self.music_genres
                }
            }
            
        except Exception as e:
            logger.error(f"Error in genre detection: {e}")
            return {'genre_detection': {'primary_genre': 'unknown', 'genre_confidence': 0.0}}

    def _extract_keywords(self, text: str) -> Dict[str, Any]:
        """Extract keywords and important terms from text."""        try:
            # Simple frequency-based keywords
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            word_freq = Counter(words)
            
            # Remove common stop words
            stop_words = {
                'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'
            }
            
            filtered_freq = {word: freq for word, freq in word_freq.items() 
                           if word not in stop_words and len(word) > 2}
            
            # Get top keywords
            top_keywords = sorted(filtered_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Extract phrases (bigrams and trigrams)
            phrases = []
            words_list = text.split()
            
            # Bigrams
            for i in range(len(words_list) - 1):
                phrase = f"{words_list[i]} {words_list[i+1]}"
                if len(phrase) > 6 and not any(sw in phrase.lower() for sw in stop_words):
                    phrases.append(phrase)
            
            phrase_freq = Counter(phrases)
            top_phrases = sorted(phrase_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'keyword_extraction': {
                    'top_keywords': [{'word': word, 'frequency': freq} for word, freq in top_keywords],
                    'top_phrases': [{'phrase': phrase, 'frequency': freq} for phrase, freq in top_phrases],
                    'keyword_density': len(set(words)) / len(words) if words else 0,
                    'total_unique_words': len(set(words))
                }
            }
            
        except Exception as e:
            logger.error(f"Error in keyword extraction: {e}")
            return {'keyword_extraction': {'top_keywords': [], 'top_phrases': []}}

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text."""        try:
            if not self.nlp:
                return {'entity_extraction': {'entities': [], 'entity_types': {}}}
            
            # Process text with spaCy
            doc = self.nlp(text[:1000000])  # Limit text length for performance
            
            entities = []
            entity_types = {}
            
            for ent in doc.ents:
                entity_info = {
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'description': spacy.explain(ent.label_) or ent.label_
                }
                entities.append(entity_info)
                
                # Count entity types
                entity_types[ent.label_] = entity_types.get(ent.label_, 0) + 1
            
            # Extract music-specific entities
            music_entities = []
            for ent in entities:
                if ent['label'] in ['PERSON', 'ORG'] or any(
                    keyword in ent['text'].lower() 
                    for keyword in ['band', 'singer', 'artist', 'musician', 'producer']
                ):
                    music_entities.append(ent)
            
            return {
                'entity_extraction': {
                    'entities': entities[:20],  # Limit to top 20
                    'entity_types': entity_types,
                    'entity_count': len(entities),
                    'music_entities': music_entities,
                    'has_person_names': 'PERSON' in entity_types,
                    'has_organizations': 'ORG' in entity_types,
                    'has_locations': 'GPE' in entity_types or 'LOC' in entity_types
                }
            }
            
        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            return {'entity_extraction': {'entities': [], 'entity_types': {}}}

    def _extract_topics(self, text: str) -> Dict[str, Any]:
        """Extract main topics and themes from text."""        try:
            # Simple topic detection based on keywords
            topic_keywords = {
                'music_creation': ['create', 'write', 'compose', 'produce', 'record', 'studio'],
                'performance': ['perform', 'stage', 'concert', 'live', 'audience', 'show'],
                'collaboration': ['together', 'with', 'featuring', 'collab', 'team', 'band'],
                'emotions': ['feel', 'emotion', 'heart', 'soul', 'love', 'pain', 'joy'],
                'success': ['success', 'fame', 'money', 'hit', 'chart', 'popular', 'star'],
                'struggle': ['struggle', 'hard', 'difficult', 'fight', 'overcome', 'challenge'],
                'relationships': ['relationship', 'friend', 'family', 'partner', 'together'],
                'personal_growth': ['grow', 'learn', 'change', 'become', 'develop', 'journey']
            }
            
            text_lower = text.lower()
            topic_scores = {}
            
            for topic, keywords in topic_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score > 0:
                    topic_scores[topic] = score / len(keywords)
            
            # Sort topics by relevance
            sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'topic_extraction': {
                    'primary_topic': sorted_topics[0][0] if sorted_topics else 'general',
                    'topic_confidence': float(sorted_topics[0][1]) if sorted_topics else 0.0,
                    'all_topics': [{'topic': topic, 'relevance': float(score)} 
                                 for topic, score in sorted_topics[:5]],
                    'topic_diversity': len(sorted_topics)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in topic extraction: {e}")
            return {'topic_extraction': {'primary_topic': 'general', 'topic_confidence': 0.0}}

    def _assess_quality(self, text: str) -> Dict[str, Any]:
        """Assess the overall quality of the text."""        try:
            # Basic quality metrics
            quality_metrics = {
                'length_score': self._calculate_length_score(text),
                'vocabulary_richness': self._calculate_vocabulary_richness(text),
                'grammar_score': self._estimate_grammar_quality(text),
                'coherence_score': self._estimate_coherence(text),
                'spelling_score': self._estimate_spelling_quality(text)
            }
            
            # Calculate overall quality
            weights = {
                'length_score': 0.15,
                'vocabulary_richness': 0.25,
                'grammar_score': 0.25,
                'coherence_score': 0.20,
                'spelling_score': 0.15
            }
            
            overall_quality = sum(
                quality_metrics[metric] * weight
                for metric, weight in weights.items()
            )
            
            quality_metrics['overall_quality'] = max(0, min(1, overall_quality))
            quality_metrics['quality_grade'] = self._get_quality_grade(overall_quality)
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error in quality assessment: {e}")
            return {'overall_quality': 0.0, 'quality_grade': 'unknown'}

    def _assess_readability(self, text: str) -> Dict[str, Any]:
        """Assess text readability using various metrics."""        try:
            # Flesch Reading Ease
            flesch_ease = flesch_reading_ease(text)
            
            # Flesch-Kincaid Grade Level
            fk_grade = flesch_kincaid_grade(text)
            
            # Custom readability metrics
            words = text.split()
            sentences = text.split('.')
            
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            avg_word_length = np.mean([len(word) for word in words]) if words else 0
            
            # Readability classification
            if flesch_ease >= 90:
                readability_level = 'Very Easy'
            elif flesch_ease >= 80:
                readability_level = 'Easy'
            elif flesch_ease >= 70:
                readability_level = 'Fairly Easy'
            elif flesch_ease >= 60:
                readability_level = 'Standard'
            elif flesch_ease >= 50:
                readability_level = 'Fairly Difficult'
            elif flesch_ease >= 30:
                readability_level = 'Difficult'
            else:
                readability_level = 'Very Difficult'
            
            return {
                'readability_analysis': {
                    'flesch_reading_ease': float(flesch_ease),
                    'flesch_kincaid_grade': float(fk_grade),
                    'readability_level': readability_level,
                    'average_sentence_length': float(avg_sentence_length),
                    'average_word_length': float(avg_word_length),
                    'is_easy_to_read': flesch_ease >= 70
                }
            }
            
        except Exception as e:
            logger.error(f"Error in readability assessment: {e}")
            return {'readability_analysis': {'flesch_reading_ease': 50.0, 'readability_level': 'Unknown'}}

    def _generate_text_hashes(self, text: str) -> Dict[str, str]:
        """Generate hash signatures for similarity matching."""        try:
            hashes = {}
            
            # MD5 hash of full text
            hashes['md5_full'] = hashlib.md5(text.encode()).hexdigest()
            
            # SHA256 hash of full text
            hashes['sha256_full'] = hashlib.sha256(text.encode()).hexdigest()
            
            # Hash of normalized text (lowercase, no punctuation)
            normalized = re.sub(r'[^\w\s]', '', text.lower())
            hashes['normalized_hash'] = hashlib.md5(normalized.encode()).hexdigest()
            
            # Hash of words only (no order)
            words = sorted(set(text.lower().split()))
            words_string = ' '.join(words)
            hashes['words_hash'] = hashlib.md5(words_string.encode()).hexdigest()
            
            # Semantic hash using sentence transformer
            embedding = self.sentence_transformer.encode(text)
            embedding_str = np.array2string(embedding, precision=2)
            hashes['semantic_hash'] = hashlib.md5(embedding_str.encode()).hexdigest()
            
            return hashes
            
        except Exception as e:
            logger.error(f"Error generating text hashes: {e}")
            return {}

    def _advanced_analysis(self, text: str) -> Dict[str, Any]:
        """Perform advanced text analysis."""        try:
            # Text complexity analysis
            complexity = self._analyze_text_complexity(text)
            
            # Style analysis
            style = self._analyze_writing_style(text)
            
            # Copyright risk assessment
            copyright_risk = self._assess_copyright_risk(text)
            
            return {
                'complexity_analysis': complexity,
                'style_analysis': style,
                'copyright_risk': copyright_risk
            }
            
        except Exception as e:
            logger.error(f"Error in advanced analysis: {e}")
            return {}

    # Helper methods
    def _is_music_related_text(self, text: str) -> bool:
        """Check if text is music-related."""        music_keywords = [
            'music', 'song', 'lyrics', 'album', 'artist', 'singer', 'band',
            'guitar', 'piano', 'drums', 'vocal', 'melody', 'rhythm', 'beat',
            'concert', 'performance', 'studio', 'record', 'producer'
        ]
        return any(keyword in text for keyword in music_keywords)

    def _calculate_sentiment_strength(self, roberta_result: Dict, vader_result: Dict) -> float:
        """Calculate combined sentiment strength."""        try:
            roberta_strength = roberta_result.get('confidence', 0)
            vader_strength = abs(vader_result.get('compound', 0)) if vader_result else 0
            
            # Combine scores
            combined_strength = (roberta_strength + vader_strength) / 2
            return float(combined_strength)
            
        except Exception:
            return 0.5

    def _calculate_length_score(self, text: str) -> float:
        """Calculate score based on text length."""        word_count = len(text.split())
        
        # Optimal length ranges
        if 50 <= word_count <= 500:  # Good length
            return 1.0
        elif 20 <= word_count < 50 or 500 < word_count <= 1000:  # Acceptable
            return 0.7
        elif 10 <= word_count < 20 or 1000 < word_count <= 2000:  # Borderline
            return 0.5
        else:  # Too short or too long
            return 0.3

    def _calculate_vocabulary_richness(self, text: str) -> float:
        """Calculate vocabulary richness (TTR - Type-Token Ratio)."""        words = text.lower().split()
        if not words:
            return 0.0
        
        unique_words = len(set(words))
        total_words = len(words)
        
        # Type-Token Ratio
        ttr = unique_words / total_words
        
        # Normalize TTR (higher is better, but diminishing returns)
        normalized_ttr = min(1.0, ttr * 1.5)
        return float(normalized_ttr)

    def _estimate_grammar_quality(self, text: str) -> float:
        """Estimate grammar quality based on heuristics."""        try:
            # Simple grammar checks
            score = 1.0
            
            # Check for basic punctuation
            sentences = text.split('.')
            if len(sentences) > 1:
                # Check if sentences start with capital letters
                properly_capitalized = sum(1 for s in sentences[:-1] 
                                         if s.strip() and s.strip()[0].isupper())
                capitalization_score = properly_capitalized / (len(sentences) - 1)
                score *= capitalization_score
            
            # Check for excessive repetition
            words = text.lower().split()
            if words:
                word_freq = Counter(words)
                max_freq = max(word_freq.values())
                repetition_penalty = min(1.0, 10 / max_freq) if max_freq > 0 else 1.0
                score *= repetition_penalty
            
            return float(max(0.0, min(1.0, score)))
            
        except Exception:
            return 0.7

    def _estimate_coherence(self, text: str) -> float:
        """Estimate text coherence based on semantic similarity between sentences."""        try:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
            if len(sentences) < 2:
                return 0.8  # Single sentence is coherent by default
            
            # Calculate sentence embeddings
            embeddings = self.sentence_transformer.encode(sentences)
            
            # Calculate average cosine similarity between adjacent sentences
            similarities = []
            for i in range(len(embeddings) - 1):
                sim = cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
                similarities.append(sim)
            
            coherence_score = np.mean(similarities) if similarities else 0.5
            return float(max(0.0, min(1.0, coherence_score)))
            
        except Exception:
            return 0.6

    def _estimate_spelling_quality(self, text: str) -> float:
        """Estimate spelling quality based on word patterns."""        try:
            words = re.findall(r'\b[a-zA-Z]+\b', text)
            if not words:
                return 1.0
            
            # Simple heuristics for spelling quality
            score = 1.0
            
            # Check for excessive use of numbers in words
            mixed_words = [w for w in words if any(c.isdigit() for c in w)]
            if mixed_words:
                mixed_penalty = len(mixed_words) / len(words)
                score *= (1 - mixed_penalty * 0.5)
            
            # Check for excessive capitalization
            all_caps_words = [w for w in words if w.isupper() and len(w) > 1]
            if all_caps_words:
                caps_penalty = len(all_caps_words) / len(words)
                score *= (1 - caps_penalty * 0.3)
            
            return float(max(0.0, min(1.0, score)))
            
        except Exception:
            return 0.8

    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade."""        if score >= 0.9:
            return 'A+'
        elif score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B+'
        elif score >= 0.6:
            return 'B'
        elif score >= 0.5:
            return 'C+'
        elif score >= 0.4:
            return 'C'
        else:
            return 'D'

    def _analyze_text_complexity(self, text: str) -> Dict[str, Any]:
        """Analyze text complexity."""        try:
            words = text.split()
            sentences = text.split('.')
            
            # Complexity metrics
            avg_word_length = np.mean([len(word) for word in words]) if words else 0
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            
            # Vocabulary complexity
            complex_words = [w for w in words if len(w) > 6]
            complexity_ratio = len(complex_words) / len(words) if words else 0
            
            return {
                'average_word_length': float(avg_word_length),
                'average_sentence_length': float(avg_sentence_length),
                'complex_word_ratio': float(complexity_ratio),
                'complexity_level': 'high' if complexity_ratio > 0.3 else 'medium' if complexity_ratio > 0.1 else 'low'
            }
            
        except Exception:
            return {}

    def _analyze_writing_style(self, text: str) -> Dict[str, Any]:
        """Analyze writing style characteristics."""        try:
            # Style indicators
            exclamation_count = text.count('!')
            question_count = text.count('?')
            ellipsis_count = text.count('...')
            
            # Sentence patterns
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            short_sentences = [s for s in sentences if len(s.split()) < 10]
            long_sentences = [s for s in sentences if len(s.split()) > 20]
            
            return {
                'exclamation_usage': exclamation_count,
                'question_usage': question_count,
                'ellipsis_usage': ellipsis_count,
                'short_sentence_ratio': len(short_sentences) / len(sentences) if sentences else 0,
                'long_sentence_ratio': len(long_sentences) / len(sentences) if sentences else 0,
                'writing_style': self._classify_writing_style(exclamation_count, question_count, sentences)
            }
            
        except Exception:
            return {}

    def _classify_writing_style(self, exclamations: int, questions: int, sentences: List[str]) -> str:
        """Classify writing style based on patterns."""        total_sentences = len(sentences)
        
        if not total_sentences:
            return 'unknown'
        
        exclamation_ratio = exclamations / total_sentences
        question_ratio = questions / total_sentences
        
        if exclamation_ratio > 0.3:
            return 'expressive'
        elif question_ratio > 0.2:
            return 'inquisitive'
        elif exclamation_ratio > 0.1 or question_ratio > 0.1:
            return 'conversational'
        else:
            return 'formal'

    def _assess_copyright_risk(self, text: str) -> Dict[str, Any]:
        """Assess potential copyright infringement risk."""        try:
            # Look for indicators of copyrighted content
            copyright_indicators = [
                'copyright', '©', 'all rights reserved', 'lyrics by',
                'written by', 'composed by', 'published by'
            ]
            
            text_lower = text.lower()
            found_indicators = [ind for ind in copyright_indicators if ind in text_lower]
            
            # Check for exact matches with common phrases (simplified)
            common_phrases = [
                'happy birthday to you',
                'we wish you a merry christmas',
                'jingle bells'
            ]
            
            exact_matches = [phrase for phrase in common_phrases if phrase in text_lower]
            
            # Calculate risk score
            risk_score = 0.0
            if found_indicators:
                risk_score += 0.3
            if exact_matches:
                risk_score += 0.7
            
            risk_level = 'high' if risk_score > 0.7 else 'medium' if risk_score > 0.3 else 'low'
            
            return {
                'copyright_risk_score': float(risk_score),
                'risk_level': risk_level,
                'found_indicators': found_indicators,
                'potential_matches': exact_matches,
                'requires_review': risk_score > 0.5
            }
            
        except Exception:
            return {'copyright_risk_score': 0.0, 'risk_level': 'unknown'}

    def _get_timestamp(self) -> str:
        """Get current timestamp."""        from datetime import datetime
        return datetime.now().isoformat()

    def compare_texts(self, text1: str, text2: str) -> Dict[str, Any]:
        """        Compare two texts for similarity.
        
        Args:
            text1: First text to compare
            text2: Second text to compare
            
        Returns:
            Similarity analysis results
        """        try:
            # Clean texts
            clean_text1 = self.text_processor.clean_text(text1)
            clean_text2 = self.text_processor.clean_text(text2)
            
            # Generate embeddings
            embeddings = self.sentence_transformer.encode([clean_text1, clean_text2])
            
            # Calculate semantic similarity
            semantic_similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            # Calculate exact match similarity
            words1 = set(clean_text1.lower().split())
            words2 = set(clean_text2.lower().split())
            
            if words1 and words2:
                jaccard_similarity = len(words1.intersection(words2)) / len(words1.union(words2))
            else:
                jaccard_similarity = 0.0
            
            # Hash comparison
            hash1 = self._generate_text_hashes(clean_text1)
            hash2 = self._generate_text_hashes(clean_text2)
            
            hash_matches = {
                hash_type: hash1.get(hash_type) == hash2.get(hash_type)
                for hash_type in hash1.keys()
                if hash_type in hash2
            }
            
            # Overall similarity
            overall_similarity = (semantic_similarity * 0.7 + jaccard_similarity * 0.3)
            
            return {
                'overall_similarity': float(overall_similarity),
                'semantic_similarity': float(semantic_similarity),
                'jaccard_similarity': float(jaccard_similarity),
                'hash_matches': hash_matches,
                'is_likely_match': overall_similarity > self.thresholds['similarity'],
                'confidence_level': 'high' if overall_similarity > 0.9 else 'medium' if overall_similarity > 0.7 else 'low',
                'similarity_type': self._classify_similarity_type(semantic_similarity, jaccard_similarity)
            }
            
        except Exception as e:
            logger.error(f"Error comparing texts: {e}")
            raise ClassificationError(f"Text comparison failed: {e}")

    def _classify_similarity_type(self, semantic_sim: float, jaccard_sim: float) -> str:
        """Classify the type of similarity between texts."""        if semantic_sim > 0.8 and jaccard_sim > 0.6:
            return 'exact_match'
        elif semantic_sim > 0.7:
            return 'semantic_similarity'
        elif jaccard_sim > 0.5:
            return 'lexical_similarity'
        elif semantic_sim > 0.5:
            return 'thematic_similarity'
        else:
            return 'low_similarity'

    def get_classification_summary(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable summary of classification results."""        try:
            summary_parts = []
            
            # Content type
            content_type = results.get('classifications', {}).get('content_type', {})
            if content_type.get('primary'):
                summary_parts.append(f"Content: {content_type['primary']} ({content_type.get('confidence', 0):.2f})")
            
            # Language
            language = results.get('classifications', {}).get('language_detection', {})
            if language.get('primary_language'):
                summary_parts.append(f"Language: {language['primary_language']}")
            
            # Sentiment
            sentiment = results.get('classifications', {}).get('sentiment_analysis', {})
            if sentiment.get('primary_sentiment'):
                summary_parts.append(f"Sentiment: {sentiment['primary_sentiment']} ({sentiment.get('confidence', 0):.2f})")
            
            # Quality
            quality = results.get('quality_metrics', {})
            if quality.get('overall_quality'):
                grade = quality.get('quality_grade', 'Unknown')
                summary_parts.append(f"Quality: {grade} ({quality['overall_quality']:.2f})")
            
            # Genre/Theme
            genre = results.get('classifications', {}).get('genre_detection', {})
            if genre.get('primary_genre') and genre['primary_genre'] != 'unknown':
                summary_parts.append(f"Genre/Theme: {genre['primary_genre']}")
            
            return " | ".join(summary_parts) if summary_parts else "No classification data available"
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Summary generation failed"
