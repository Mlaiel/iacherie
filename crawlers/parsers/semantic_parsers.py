"""Semantic AI Content Parsers Module
==================================

Ultra-advanced semantic content parsers using AI for deep content understanding,
entity extraction, sentiment analysis, and semantic fingerprinting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de

Development Team Specialties:
- Lead AI Developer & Architect: Fahed Mlaiel
- Backend Senior Engineer: Advanced Python/FastAPI systems
- ML Engineer: Content analysis and fingerprinting
- Audio Processing Specialist: Multi-format audio analysis  
- DevOps Engineer: Infrastructure and deployment
- Database Administrator: Performance optimization
- Security Expert: Content protection and compliance
- Microservices Architect: Scalable system design
"""

import asyncio
import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import numpy as np
import torch
import spacy
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    pipeline, BertTokenizer, BertModel
)
from sentence_transformers import SentenceTransformer
import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .exceptions import SemanticParsingError, ModelLoadError, AnalysisError
from .parser_config import ParserConfig


@dataclass
class SemanticAnalysis:
    """
Container for semantic analysis results"""
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"
    confidence: float = 0.0
    emotions: Dict[str, float] = field(default_factory=dict)
    topics: List[Dict[str, Any]] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    keywords: List[Dict[str, float]] = field(default_factory=list)
    semantic_fingerprint: str = ""
    vector_embedding: np.ndarray = field(default_factory=lambda: np.array([]))
    language: str = "unknown"
    readability_score: float = 0.0
    toxicity_score: float = 0.0


@dataclass
class ContentSemantics:
    """Complete semantic analysis of content"""
    text_analysis: SemanticAnalysis = field(default_factory=SemanticAnalysis)
    summary: str = ""
    key_phrases: List[str] = field(default_factory=list)
    content_category: str = "unknown"
    intent: str = "unknown"
    quality_score: float = 0.0
    originality_score: float = 0.0
    engagement_prediction: float = 0.0


class SemanticModelManager:
    """Manages AI models for semantic analysis"""
    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.tokenizers = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """
Initialize all AI models"""
        try:
            # Load SpaCy models
            await self._load_spacy_models()
            
            # Load BERT models
            await self._load_bert_models()
            
            # Load specialized models
            await self._load_specialized_models()
            
            # Load sentence transformers
            await self._load_sentence_transformers()
            
            self._initialized = True
            self.logger.info("Semantic models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize semantic models: {e}")
            raise ModelLoadError(f"Model initialization failed: {e}")
    
    async def _load_spacy_models(self) -> None:
        """Load SpaCy NLP models"""
        models = ['en_core_web_lg', 'de_core_news_lg', 'fr_core_news_lg']
        
        for model_name in models:
            try:
                self.models[f'spacy_{model_name}'] = spacy.load(model_name)
                self.logger.info(f"Loaded SpaCy model: {model_name}")
            except OSError:
                self.logger.warning(f"SpaCy model not found: {model_name}")
    
    async def _load_bert_models(self) -> None:
        """Load BERT-based models"""
        models = {
            'bert_multilingual': 'bert-base-multilingual-cased',
            'bert_sentiment': 'nlptown/bert-base-multilingual-uncased-sentiment',
            'bert_emotion': 'j-hartmann/emotion-english-distilroberta-base'
        }
        
        for model_key, model_name in models.items():
            try:
                self.tokenizers[model_key] = AutoTokenizer.from_pretrained(model_name)
                self.models[model_key] = AutoModel.from_pretrained(model_name)
                self.logger.info(f"Loaded BERT model: {model_name}")
            except Exception as e:
                self.logger.warning(f"Failed to load BERT model {model_name}: {e}")
    
    async def _load_specialized_models(self) -> None:
        """Load specialized AI models"""
        try:
            # Sentiment analysis
            self.models['sentiment_pipeline'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            # Emotion detection
            self.models['emotion_pipeline'] = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base"
            )
            
            # Toxicity detection
            self.models['toxicity_pipeline'] = pipeline(
                "text-classification",
                model="unitary/toxic-bert"
            )
            
            # Summarization
            self.models['summarization_pipeline'] = pipeline(
                "summarization",
                model="facebook/bart-large-cnn"
            )
            
            self.logger.info("Specialized models loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to load specialized models: {e}")
    
    async def _load_sentence_transformers(self) -> None:
        """Load sentence transformer models"""
        models = [
            'all-MiniLM-L6-v2',
            'all-mpnet-base-v2',
            'paraphrase-multilingual-MiniLM-L12-v2'
        ]
        
        for model_name in models:
            try:
                key = f'sentence_transformer_{model_name.replace("-", "_")}'
                self.models[key] = SentenceTransformer(model_name)
                self.logger.info(f"Loaded SentenceTransformer: {model_name}")
            except Exception as e:
                self.logger.warning(f"Failed to load SentenceTransformer {model_name}: {e}")


class SemanticContentParser:
    """Ultra-advanced semantic content parser with AI capabilities"""
    
    def __init__(self, config: ParserConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model_manager = SemanticModelManager(config)
        self._cache = {}
    
    async def initialize(self) -> None:
        """
Initialize the semantic parser"""
        await self.model_manager.initialize()
    
    async def parse_semantic_content(
        self, 
        text: str, 
        language: str = "auto",
        include_embeddings: bool = True
    ) -> ContentSemantics:
        """
        Perform comprehensive semantic analysis of text content
        """
        try:
            # Detect language if auto
            if language == "auto":
                language = await self._detect_language(text)
            
            # Perform core semantic analysis
            text_analysis = await self._analyze_text_semantics(text, language)
            
            # Generate content summary
            summary = await self._generate_summary(text)
            
            # Extract key phrases
            key_phrases = await self._extract_key_phrases(text)
            
            # Classify content category
            content_category = await self._classify_content_category(text)
            
            # Determine user intent
            intent = await self._analyze_intent(text)
            
            # Calculate quality scores
            quality_score = await self._calculate_quality_score(text)
            originality_score = await self._calculate_originality_score(text)
            engagement_prediction = await self._predict_engagement(text)
            
            return ContentSemantics(
                text_analysis=text_analysis,
                summary=summary,
                key_phrases=key_phrases,
                content_category=content_category,
                intent=intent,
                quality_score=quality_score,
                originality_score=originality_score,
                engagement_prediction=engagement_prediction
            )
            
        except Exception as e:
            self.logger.error(f"Semantic parsing failed: {e}")
            raise SemanticParsingError(f"Failed to parse semantic content: {e}")
    
    async def _analyze_text_semantics(self, text: str, language: str) -> SemanticAnalysis:
        """Perform detailed semantic analysis"""
        analysis = SemanticAnalysis()
        
        # Sentiment analysis
        sentiment_result = await self._analyze_sentiment(text)
        analysis.sentiment_score = sentiment_result['score']
        analysis.sentiment_label = sentiment_result['label']
        analysis.confidence = sentiment_result['confidence']
        
        # Emotion detection
        analysis.emotions = await self._detect_emotions(text)
        
        # Topic modeling
        analysis.topics = await self._extract_topics(text)
        
        # Named entity recognition
        analysis.entities = await self._extract_entities(text, language)
        
        # Keyword extraction
        analysis.keywords = await self._extract_keywords(text)
        
        # Generate semantic fingerprint
        analysis.semantic_fingerprint = await self._generate_semantic_fingerprint(text)
        
        # Create vector embedding
        if self.model_manager._initialized:
            analysis.vector_embedding = await self._create_vector_embedding(text)
        
        # Calculate additional scores
        analysis.language = language
        analysis.readability_score = await self._calculate_readability(text)
        analysis.toxicity_score = await self._detect_toxicity(text)
        
        return analysis
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
Analyze sentiment with multiple models"""
        try:
            if 'sentiment_pipeline' in self.model_manager.models:
                result = self.model_manager.models['sentiment_pipeline'](text)[0]
                
                # Normalize score to -1 to 1 range
                score = result['score']
                if result['label'] in ['NEGATIVE', 'LABEL_0']:
                    score = -score
                elif result['label'] in ['NEUTRAL']:
                    score = 0.0
                
                return {
                    'score': score,
                    'label': result['label'].lower(),
                    'confidence': result['score']
                }
            
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
            
        except Exception as e:
            self.logger.warning(f"Sentiment analysis failed: {e}")
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
    
    async def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions in text"""
        try:
            if 'emotion_pipeline' in self.model_manager.models:
                results = self.model_manager.models['emotion_pipeline'](text)
                
                emotions = {}
                for result in results:
                    emotions[result['label'].lower()] = result['score']
                
                return emotions
            
            return {}
            
        except Exception as e:
            self.logger.warning(f"Emotion detection failed: {e}")
            return {}
    
    async def _extract_topics(self, text: str) -> List[Dict[str, Any]]:
        """Extract topics using advanced NLP"""
        try:
            # Use TF-IDF for basic topic extraction
            vectorizer = TfidfVectorizer(
                max_features=20,
                stop_words='english',
                ngram_range=(1, 3)
            )
            
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            topics = []
            for idx, score in enumerate(tfidf_scores):
                if score > 0.1:  # Threshold for topic relevance
                    topics.append({
                        'topic': feature_names[idx],
                        'relevance': float(score),
                        'type': 'keyword_based'
                    })
            
            return sorted(topics, key=lambda x: x['relevance'], reverse=True)[:10]
            
        except Exception as e:
            self.logger.warning(f"Topic extraction failed: {e}")
            return []
    
    async def _extract_entities(self, text: str, language: str) -> List[Dict[str, Any]]:
        """Extract named entities"""
        entities = []
        
        try:
            # Use SpaCy for entity extraction
            spacy_model_key = f'spacy_en_core_web_lg'  # Default to English
            if language == 'de':
                spacy_model_key = 'spacy_de_core_news_lg'
            elif language == 'fr':
                spacy_model_key = 'spacy_fr_core_news_lg'
            
            if spacy_model_key in self.model_manager.models:
                nlp = self.model_manager.models[spacy_model_key]
                doc = nlp(text)
                
                for ent in doc.ents:
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char,
                        'confidence': getattr(ent, 'confidence', 0.8)
                    })
            
            return entities
            
        except Exception as e:
            self.logger.warning(f"Entity extraction failed: {e}")
            return []
    
    async def _extract_keywords(self, text: str) -> List[Dict[str, float]]:
        """Extract keywords with importance scores"""
        try:
            # Use TF-IDF for keyword extraction
            vectorizer = TfidfVectorizer(
                max_features=50,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            keywords = []
            for idx, score in enumerate(tfidf_scores):
                if score > 0.05:
                    keywords.append({
                        'keyword': feature_names[idx],
                        'importance': float(score)
                    })
            
            return sorted(keywords, key=lambda x: x['importance'], reverse=True)[:20]
            
        except Exception as e:
            self.logger.warning(f"Keyword extraction failed: {e}")
            return []
    
    async def _generate_semantic_fingerprint(self, text: str) -> str:
        """Generate unique semantic fingerprint"""
        try:
            # Create a hash based on semantic features
            normalized_text = re.sub(r'\W+', ' ', text.lower()).strip()
            
            # Extract semantic features
            words = normalized_text.split()
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Create semantic signature
            semantic_features = []
            for word, freq in sorted(word_freq.items()):
                if freq > 1:  # Only include repeated words
                    semantic_features.append(f"{word}:{freq}")
            
            fingerprint_text = "|".join(semantic_features)
            return hashlib.sha256(fingerprint_text.encode()).hexdigest()[:32]
            
        except Exception as e:
            self.logger.warning(f"Semantic fingerprint generation failed: {e}")
            return hashlib.sha256(text.encode()).hexdigest()[:32]
    
    async def _create_vector_embedding(self, text: str) -> np.ndarray:
        """Create vector embedding for semantic similarity"""
        try:
            model_key = 'sentence_transformer_all_MiniLM_L6_v2'
            if model_key in self.model_manager.models:
                model = self.model_manager.models[model_key]
                embedding = model.encode([text])[0]
                return embedding
            
            return np.array([])
            
        except Exception as e:
            self.logger.warning(f"Vector embedding creation failed: {e}")
            return np.array([])
    
    async def _detect_language(self, text: str) -> str:
        """Detect text language"""
        try:
            # Simple language detection based on common words
            english_words = set(['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'])
            german_words = set(['der', 'die', 'das', 'und', 'oder', 'aber', 'in', 'an', 'zu', 'für'])
            french_words = set(['le', 'la', 'les', 'et', 'ou', 'mais', 'dans', 'sur', 'à', 'pour'])
            
            words = set(text.lower().split())
            
            english_score = len(words.intersection(english_words))
            german_score = len(words.intersection(german_words))
            french_score = len(words.intersection(french_words))
            
            if english_score >= german_score and english_score >= french_score:
                return 'en'
            elif german_score >= french_score:
                return 'de'
            else:
                return 'fr'
                
        except Exception:
            return 'en'  # Default to English
    
    async def _generate_summary(self, text: str) -> str:
        """
Generate content summary"""
        try:
            if 'summarization_pipeline' in self.model_manager.models and len(text) > 100:
                # Limit text length for summarization
                max_length = min(len(text), 1024)
                truncated_text = text[:max_length]
                
                summary_result = self.model_manager.models['summarization_pipeline'](
                    truncated_text,
                    max_length=150,
                    min_length=50,
                    do_sample=False
                )
                
                return summary_result[0]['summary_text']
            
            # Fallback: return first sentence or truncated text
            sentences = text.split('.')
            return sentences[0][:200] + '...' if len(sentences[0]) > 200 else sentences[0]
            
        except Exception as e:
            self.logger.warning(f"Summary generation failed: {e}")
            return text[:200] + '...' if len(text) > 200 else text
    
    async def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases using advanced NLP"""
        try:
            # Extract noun phrases and important keywords
            key_phrases = []
            
            # Simple extraction based on capitalized words and phrases
            capitalized_phrases = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', text)
            key_phrases.extend(capitalized_phrases[:5])
            
            # Extract quoted phrases
            quoted_phrases = re.findall(r'"([^"]*)"', text)
            key_phrases.extend(quoted_phrases[:3])
            
            return list(set(key_phrases))[:10]
            
        except Exception as e:
            self.logger.warning(f"Key phrase extraction failed: {e}")
            return []
    
    async def _classify_content_category(self, text: str) -> str:
        """Classify content into categories"""
        try:
            # Simple rule-based classification
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['music', 'song', 'album', 'artist', 'audio']):
                return 'music'
            elif any(word in text_lower for word in ['video', 'movie', 'film', 'watch']):
                return 'video'
            elif any(word in text_lower for word in ['photo', 'image', 'picture', 'photography']):
                return 'image'
            elif any(word in text_lower for word in ['news', 'article', 'report', 'journalism']):
                return 'news'
            elif any(word in text_lower for word in ['blog', 'post', 'personal', 'diary']):
                return 'blog'
            elif any(word in text_lower for word in ['business', 'company', 'corporate', 'professional']):
                return 'business'
            else:
                return 'general'
                
        except Exception:
            return 'general'
    
    async def _analyze_intent(self, text: str) -> str:
        """
Analyze user intent"""
        try:
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['buy', 'purchase', 'order', 'price']):
                return 'commercial'
            elif any(word in text_lower for word in ['learn', 'how to', 'tutorial', 'guide']):
                return 'educational'
            elif any(word in text_lower for word in ['entertainment', 'fun', 'funny', 'game']):
                return 'entertainment'
            elif any(word in text_lower for word in ['information', 'about', 'what is', 'explain']):
                return 'informational'
            elif any(word in text_lower for word in ['share', 'tell', 'show', 'look']):
                return 'social'
            else:
                return 'unknown'
                
        except Exception:
            return 'unknown'
    
    async def _calculate_quality_score(self, text: str) -> float:
        """
Calculate content quality score"""
        try:
            score = 0.0
            
            # Length score (optimal around 300-1000 words)
            word_count = len(text.split())
            if 300 <= word_count <= 1000:
                score += 0.3
            elif 100 <= word_count < 300 or 1000 < word_count <= 2000:
                score += 0.2
            elif word_count > 50:
                score += 0.1
            
            # Sentence variety
            sentences = text.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
            if 10 <= avg_sentence_length <= 25:
                score += 0.2
            
            # Vocabulary richness
            words = text.lower().split()
            unique_words = set(words)
            vocabulary_ratio = len(unique_words) / max(len(words), 1)
            score += min(vocabulary_ratio * 0.3, 0.3)
            
            # Grammar indicators (simple heuristics)
            if re.search(r'[.!?]', text):  # Has punctuation
                score += 0.1
            if re.search(r'[A-Z]', text):  # Has capital letters
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception:
            return 0.5  # Default moderate quality
    
    async def _calculate_originality_score(self, text: str) -> float:
        """
Calculate content originality score"""
        try:
            # Simple originality heuristics
            score = 0.5  # Base score
            
            # Check for common cliches and phrases
            cliches = ['at the end of the day', 'think outside the box', 'low hanging fruit']
            for cliche in cliches:
                if cliche in text.lower():
                    score -= 0.1
            
            # Vocabulary diversity
            words = text.lower().split()
            unique_words = set(words)
            diversity_ratio = len(unique_words) / max(len(words), 1)
            score += diversity_ratio * 0.3
            
            # Creative indicators
            creative_words = ['unique', 'innovative', 'creative', 'original', 'novel']
            for word in creative_words:
                if word in text.lower():
                    score += 0.05
            
            return min(max(score, 0.0), 1.0)
            
        except Exception:
            return 0.5
    
    async def _predict_engagement(self, text: str) -> float:
        """
Predict content engagement potential"""
        try:
            score = 0.0
            
            # Question indicators
            if '?' in text:
                score += 0.2
            
            # Emotional words
            emotional_words = ['amazing', 'incredible', 'shocking', 'unbelievable', 'wow']
            for word in emotional_words:
                if word in text.lower():
                    score += 0.1
            
            # Call to action
            cta_phrases = ['comment below', 'share this', 'like if', 'what do you think']
            for phrase in cta_phrases:
                if phrase in text.lower():
                    score += 0.15
            
            # Length optimization for engagement
            word_count = len(text.split())
            if 50 <= word_count <= 300:  # Optimal for social media
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception:
            return 0.5
    
    async def _calculate_readability(self, text: str) -> float:
        """
Calculate readability score (simplified)"""
        try:
            words = text.split()
            sentences = text.split('.')
            
            if not words or not sentences:
                return 0.0
            
            avg_words_per_sentence = len(words) / len(sentences)
            avg_syllables_per_word = sum(self._count_syllables(word) for word in words) / len(words)
            
            # Simplified Flesch Reading Ease formula
            readability = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
            
            # Normalize to 0-1 scale
            return max(0.0, min(1.0, readability / 100.0))
            
        except Exception:
            return 0.5
    
    def _count_syllables(self, word: str) -> int:
        """
Count syllables in a word (simplified)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    async def _detect_toxicity(self, text: str) -> float:
        """
Detect content toxicity"""
        try:
            if 'toxicity_pipeline' in self.model_manager.models:
                result = self.model_manager.models['toxicity_pipeline'](text)[0]
                return result['score'] if result['label'] == 'TOXIC' else 1.0 - result['score']
            
            # Simple heuristic fallback
            toxic_indicators = ['hate', 'stupid', 'idiot', 'kill', 'die']
            toxic_count = sum(1 for word in toxic_indicators if word in text.lower())
            return min(toxic_count * 0.2, 1.0)
            
        except Exception:
            return 0.0


__all__ = [
    'SemanticContentParser',
    'SemanticAnalysis', 
    'ContentSemantics',
    'SemanticModelManager'
]
