"""Text AI Models for IA Influencer Agent Platform
Enterprise-grade text processing, NLP, and content generation models

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
⚠️  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Development Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security
- Microservices + Audio + DevOps + IA Prompt Engineer
Email: mlaiel@live.de
"""
import re
import json
import hashlib
import spacy
import nltk
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    pipeline, GPT2LMHeadModel, GPT2Tokenizer
)
import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
from pathlib import Path

from ..core.base_models import BaseAIModel, ModelConfig, ProcessingResult
from ..core.exceptions import ModelError, ValidationError


class TextLanguage(Enum):
    """Supported languages for text processing"""    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    AUTO_DETECT = "auto"


class TextContentType(Enum):
    """Text content type classification"""    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    ARTICLE = "article"
    CAPTION = "caption"
    DESCRIPTION = "description"
    HASHTAGS = "hashtags"
    TITLE = "title"
    SCRIPT = "script"
    LYRICS = "lyrics"
    PODCAST_TRANSCRIPT = "podcast_transcript"
    EMAIL = "email"
    PRODUCT_DESCRIPTION = "product_description"
    SEO_CONTENT = "seo_content"


class SentimentType(Enum):
    """Sentiment classification types"""    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class TextQuality(Enum):
    """Text quality levels"""    POOR = "poor"
    BASIC = "basic"
    GOOD = "good"
    PROFESSIONAL = "professional"
    EXPERT = "expert"


@dataclass
class TextFeatures:
    """Comprehensive text feature extraction results"""    content: str
    language: TextLanguage
    content_type: TextContentType
    word_count: int
    character_count: int
    sentence_count: int
    paragraph_count: int
    reading_time: float
    reading_level: str
    complexity_score: float
    sentiment: SentimentType
    sentiment_scores: Dict[str, float]
    emotion_scores: Dict[str, float]
    keywords: List[str]
    entities: List[Dict]
    topics: List[str]
    hashtags: List[str]
    mentions: List[str]
    urls: List[str]
    quality_score: float
    seo_score: float
    engagement_potential: float
    text_fingerprint: str
    similarity_hash: str
    plagiarism_score: float
    originality_score: float
    bias_analysis: Dict[str, float]
    toxicity_score: float
    readability_metrics: Dict[str, float]


@dataclass
class ContentGenerationRequest:
    """Request for content generation"""    content_type: TextContentType
    topic: str
    target_audience: str
    tone: str
    length: int
    language: TextLanguage
    keywords: List[str]
    style_preferences: Dict[str, Any]
    seo_requirements: Dict[str, Any]


@dataclass
class GeneratedContent:
    """Generated content with metadata"""    content: str
    title: Optional[str]
    meta_description: Optional[str]
    hashtags: List[str]
    keywords_used: List[str]
    seo_score: float
    engagement_score: float
    originality_score: float
    quality_metrics: Dict[str, float]


class TextAnalyzer(BaseAIModel):
    """Advanced text analysis and feature extraction"""    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.nlp_models = {}
        self.sentiment_analyzer = None
        self.emotion_analyzer = None
        self.language_detector = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize NLP models"""        try:
            # Load spaCy models for different languages
            self.nlp_models = {
                'en': self._load_spacy_model('en_core_web_sm'),
                'de': self._load_spacy_model('de_core_news_sm'),
                'fr': self._load_spacy_model('fr_core_news_sm'),
            }
            
            # Initialize sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # Initialize emotion analysis
            self.emotion_analyzer = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            
            # Language detection
            self.language_detector = pipeline("text-classification", 
                                            model="papluca/xlm-roberta-base-language-detection")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize NLP models: {e}")
    
    def _load_spacy_model(self, model_name: str):
        """Load spaCy model with fallback"""        try:
            return spacy.load(model_name)
        except OSError:
            self.logger.warning(f"SpaCy model {model_name} not found, using en_core_web_sm")
            try:
                return spacy.load("en_core_web_sm")
            except OSError:
                self.logger.error("No spaCy models available")
                return None
    
    async def process(self, text: str, **kwargs) -> ProcessingResult:
        """Comprehensive text analysis"""        try:
            start_time = datetime.now()
            
            if not text or not text.strip():
                raise ValidationError("Empty text provided")
            
            # Detect language
            language = await self._detect_language(text)
            
            # Extract basic features
            basic_features = self._extract_basic_features(text)
            
            # NLP analysis
            nlp_features = await self._extract_nlp_features(text, language)
            
            # Sentiment and emotion analysis
            sentiment_features = await self._analyze_sentiment_emotion(text)
            
            # Content classification
            content_type = self._classify_content_type(text)
            
            # Quality assessment
            quality_features = self._assess_quality(text)
            
            # SEO analysis
            seo_features = self._analyze_seo(text)
            
            # Generate fingerprints
            fingerprints = self._generate_text_fingerprints(text)
            
            # Combine all features
            features = TextFeatures(
                content=text,
                language=language,
                content_type=content_type,
                **basic_features,
                **nlp_features,
                **sentiment_features,
                **quality_features,
                **seo_features,
                **fingerprints
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                data=features,
                confidence=0.92,
                processing_time=processing_time,
                model_version="1.0",
                metadata={"language": language.value, "content_type": content_type.value}
            )
            
        except Exception as e:
            self.logger.error(f"Text analysis failed: {e}")
            return ProcessingResult(
                success=False,
                data=None,
                error_message=str(e)
            )
    
    async def _detect_language(self, text: str) -> TextLanguage:
        """Detect text language"""        try:
            if self.language_detector:
                # Use first 512 characters for language detection
                sample_text = text[:512]
                result = self.language_detector(sample_text)
                
                # Get highest confidence language
                if result and len(result) > 0:
                    detected_lang = result[0]['label']
                    
                    # Map detected language to our enum
                    lang_mapping = {
                        'en': TextLanguage.ENGLISH,
                        'de': TextLanguage.GERMAN,
                        'fr': TextLanguage.FRENCH,
                        'es': TextLanguage.SPANISH,
                        'it': TextLanguage.ITALIAN,
                        'pt': TextLanguage.PORTUGUESE,
                        'nl': TextLanguage.DUTCH,
                        'ru': TextLanguage.RUSSIAN,
                        'zh': TextLanguage.CHINESE,
                        'ja': TextLanguage.JAPANESE,
                        'ko': TextLanguage.KOREAN,
                        'ar': TextLanguage.ARABIC,
                    }
                    
                    return lang_mapping.get(detected_lang, TextLanguage.ENGLISH)
            
            # Fallback to English
            return TextLanguage.ENGLISH
            
        except Exception as e:
            self.logger.error(f"Language detection failed: {e}")
            return TextLanguage.ENGLISH
    
    def _extract_basic_features(self, text: str) -> Dict:
        """Extract basic text statistics"""        # Clean text for counting
        clean_text = text.strip()
        
        # Count words (split by whitespace)
        words = clean_text.split()
        word_count = len(words)
        
        # Count characters
        character_count = len(clean_text)
        
        # Count sentences (simple regex)
        sentences = re.split(r'[.!?]+', clean_text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Count paragraphs
        paragraphs = clean_text.split('\n\n')
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        # Estimate reading time (average 200 words per minute)
        reading_time = word_count / 200
        
        # Calculate complexity score (words per sentence)
        complexity_score = word_count / max(sentence_count, 1)
        
        return {
            "word_count": word_count,
            "character_count": character_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "reading_time": reading_time,
            "complexity_score": complexity_score
        }
    
    async def _extract_nlp_features(self, text: str, language: TextLanguage) -> Dict:
        """Extract NLP features using spaCy"""        try:
            # Get appropriate NLP model
            nlp = self.nlp_models.get(language.value, self.nlp_models.get('en'))
            
            if not nlp:
                return self._extract_basic_nlp_features(text)
            
            # Process text
            doc = nlp(text)
            
            # Extract entities
            entities = [
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                }
                for ent in doc.ents
            ]
            
            # Extract keywords (noun phrases and important words)
            keywords = list(set([
                chunk.text.lower() for chunk in doc.noun_chunks
                if len(chunk.text) > 2 and not chunk.text.isspace()
            ]))[:20]  # Limit to top 20
            
            # Extract topics (simplified - use most common nouns)
            topics = list(set([
                token.lemma_.lower() for token in doc
                if token.pos_ == 'NOUN' and len(token.text) > 3 and token.is_alpha
            ]))[:10]  # Limit to top 10
            
            # Reading level assessment
            reading_level = self._calculate_reading_level(text, doc)
            
            return {
                "entities": entities,
                "keywords": keywords,
                "topics": topics,
                "reading_level": reading_level
            }
            
        except Exception as e:
            self.logger.error(f"NLP feature extraction failed: {e}")
            return self._extract_basic_nlp_features(text)
    
    def _extract_basic_nlp_features(self, text: str) -> Dict:
        """Basic NLP features without advanced models"""        # Extract hashtags
        hashtags = re.findall(r'#\w+', text)
        
        # Extract mentions
        mentions = re.findall(r'@\w+', text)
        
        # Extract URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        # Basic keyword extraction (most frequent words)
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        keywords = sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:15]
        
        return {
            "entities": [],
            "keywords": keywords,
            "topics": keywords[:5],  # Use top keywords as topics
            "hashtags": hashtags,
            "mentions": mentions,
            "urls": urls,
            "reading_level": "intermediate"
        }
    
    def _calculate_reading_level(self, text: str, doc=None) -> str:
        """Calculate reading level using various metrics"""        try:
            # Flesch Reading Ease calculation
            word_count = len(text.split())
            sentence_count = len(re.split(r'[.!?]+', text))
            syllable_count = self._count_syllables(text)
            
            if sentence_count == 0 or word_count == 0:
                return "basic"
            
            # Flesch Reading Ease formula
            flesch_score = 206.835 - (1.015 * (word_count / sentence_count)) - (84.6 * (syllable_count / word_count))
            
            # Convert to reading level
            if flesch_score >= 90:
                return "elementary"
            elif flesch_score >= 80:
                return "basic"
            elif flesch_score >= 70:
                return "intermediate"
            elif flesch_score >= 60:
                return "advanced"
            else:
                return "expert"
                
        except Exception:
            return "intermediate"
    
    def _count_syllables(self, text: str) -> int:
        """Count syllables in text (approximation)"""        # Simple syllable counting using vowel patterns
        vowels = "aeiouyAEIOUY"
        syllable_count = 0
        
        for word in text.split():
            word = re.sub(r'[^a-zA-Z]', '', word)
            if not word:
                continue
                
            word_syllables = 0
            prev_was_vowel = False
            
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_was_vowel:
                    word_syllables += 1
                prev_was_vowel = is_vowel
            
            # Adjust for silent e
            if word.endswith('e') and word_syllables > 1:
                word_syllables -= 1
            
            # Ensure at least 1 syllable per word
            syllable_count += max(word_syllables, 1)
        
        return syllable_count
    
    async def _analyze_sentiment_emotion(self, text: str) -> Dict:
        """Analyze sentiment and emotions"""        try:
            sentiment_result = {"sentiment": SentimentType.NEUTRAL, "sentiment_scores": {}, "emotion_scores": {}}
            
            # Sentiment analysis
            if self.sentiment_analyzer:
                sentiment_output = self.sentiment_analyzer(text)
                if sentiment_output and len(sentiment_output) > 0:
                    scores = {item['label']: item['score'] for item in sentiment_output[0]}
                    
                    # Map labels to our sentiment types
                    sentiment_mapping = {
                        'LABEL_0': 'negative',
                        'LABEL_1': 'neutral', 
                        'LABEL_2': 'positive',
                        'negative': 'negative',
                        'neutral': 'neutral',
                        'positive': 'positive'
                    }
                    
                    mapped_scores = {}
                    for label, score in scores.items():
                        mapped_label = sentiment_mapping.get(label, label)
                        mapped_scores[mapped_label] = score
                    
                    # Determine overall sentiment
                    max_sentiment = max(mapped_scores.keys(), key=lambda x: mapped_scores[x])
                    sentiment_type = SentimentType.POSITIVE if max_sentiment == 'positive' else \
                                   SentimentType.NEGATIVE if max_sentiment == 'negative' else \
                                   SentimentType.NEUTRAL
                    
                    sentiment_result["sentiment"] = sentiment_type
                    sentiment_result["sentiment_scores"] = mapped_scores
            
            # Emotion analysis
            if self.emotion_analyzer:
                emotion_output = self.emotion_analyzer(text)
                if emotion_output and len(emotion_output) > 0:
                    emotion_scores = {item['label']: item['score'] for item in emotion_output[0]}
                    sentiment_result["emotion_scores"] = emotion_scores
            
            return sentiment_result
            
        except Exception as e:
            self.logger.error(f"Sentiment/emotion analysis failed: {e}")
            return {
                "sentiment": SentimentType.NEUTRAL,
                "sentiment_scores": {},
                "emotion_scores": {}
            }
    
    def _classify_content_type(self, text: str) -> TextContentType:
        """Classify text content type"""        text_lower = text.lower()
        
        # Check for hashtags (social media indicator)
        if '#' in text and len(text) < 280:
            return TextContentType.SOCIAL_MEDIA
        
        # Check for typical blog post indicators
        if len(text) > 1000 and any(word in text_lower for word in ['introduction', 'conclusion', 'chapter', 'section']):
            return TextContentType.BLOG_POST
        
        # Check for article indicators
        if len(text) > 500 and any(word in text_lower for word in ['according to', 'research shows', 'study found']):
            return TextContentType.ARTICLE
        
        # Check for script indicators
        if any(pattern in text for pattern in [':', '(', 'FADE IN', 'CUT TO']):
            return TextContentType.SCRIPT
        
        # Check for product description
        if any(word in text_lower for word in ['product', 'features', 'specifications', 'price', 'buy now']):
            return TextContentType.PRODUCT_DESCRIPTION
        
        # Default classification based on length
        if len(text) < 140:
            return TextContentType.CAPTION
        elif len(text) < 500:
            return TextContentType.DESCRIPTION
        else:
            return TextContentType.BLOG_POST
    
    def _assess_quality(self, text: str) -> Dict:
        """Assess text quality"""        # Calculate various quality metrics
        word_count = len(text.split())
        
        # Grammar score (simplified - count basic errors)
        grammar_score = self._estimate_grammar_quality(text)
        
        # Vocabulary diversity (unique words / total words)
        words = text.lower().split()
        unique_words = set(words)
        vocabulary_diversity = len(unique_words) / max(len(words), 1)
        
        # Structure score (paragraphs, sentences)
        structure_score = self._assess_structure(text)
        
        # Overall quality score
        quality_score = (grammar_score + vocabulary_diversity + structure_score) / 3
        
        # Determine quality level
        if quality_score >= 0.8:
            quality_level = TextQuality.EXPERT
        elif quality_score >= 0.7:
            quality_level = TextQuality.PROFESSIONAL
        elif quality_score >= 0.6:
            quality_level = TextQuality.GOOD
        elif quality_score >= 0.4:
            quality_level = TextQuality.BASIC
        else:
            quality_level = TextQuality.POOR
        
        # Calculate engagement potential
        engagement_potential = self._calculate_engagement_potential(text)
        
        # Bias and toxicity analysis (simplified)
        bias_analysis = self._analyze_bias(text)
        toxicity_score = self._analyze_toxicity(text)
        
        # Plagiarism and originality (placeholder)
        plagiarism_score = 0.1  # Low plagiarism
        originality_score = 0.9  # High originality
        
        return {
            "quality_score": quality_score,
            "engagement_potential": engagement_potential,
            "plagiarism_score": plagiarism_score,
            "originality_score": originality_score,
            "bias_analysis": bias_analysis,
            "toxicity_score": toxicity_score,
            "readability_metrics": {
                "grammar_score": grammar_score,
                "vocabulary_diversity": vocabulary_diversity,
                "structure_score": structure_score
            }
        }
    
    def _estimate_grammar_quality(self, text: str) -> float:
        """Estimate grammar quality (simplified)"""        # Count potential grammar issues
        issues = 0
        
        # Check for basic patterns that might indicate errors
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if sentence starts with capital letter
            if not sentence[0].isupper():
                issues += 1
            
            # Check for double spaces or missing spaces after punctuation
            if '  ' in sentence or re.search(r'[.!?][a-zA-Z]', sentence):
                issues += 1
        
        # Calculate grammar score (higher is better)
        total_sentences = len([s for s in sentences if s.strip()])
        if total_sentences == 0:
            return 0.5
        
        error_rate = issues / total_sentences
        grammar_score = max(0.0, 1.0 - error_rate)
        
        return grammar_score
    
    def _assess_structure(self, text: str) -> float:
        """Assess text structure quality"""        # Check for proper paragraph structure
        paragraphs = text.split('\n\n')
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        # Check sentence variety
        sentences = re.split(r'[.!?]+', text)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        
        if not sentence_lengths:
            return 0.3
        
        # Calculate sentence length variety
        avg_length = np.mean(sentence_lengths)
        length_std = np.std(sentence_lengths)
        variety_score = min(length_std / avg_length, 1.0) if avg_length > 0 else 0.0
        
        # Paragraph structure score
        words_per_paragraph = len(text.split()) / max(paragraph_count, 1)
        paragraph_score = min(words_per_paragraph / 100, 1.0)  # Ideal ~100 words per paragraph
        
        return (variety_score + paragraph_score) / 2
    
    def _calculate_engagement_potential(self, text: str) -> float:
        """Calculate potential for engagement"""        engagement_factors = 0
        total_factors = 7
        
        # Check for questions
        if '?' in text:
            engagement_factors += 1
        
        # Check for emotional words
        emotional_words = ['amazing', 'incredible', 'love', 'hate', 'excited', 'surprised']
        if any(word in text.lower() for word in emotional_words):
            engagement_factors += 1
        
        # Check for calls to action
        cta_phrases = ['click', 'share', 'comment', 'like', 'subscribe', 'follow']
        if any(phrase in text.lower() for phrase in cta_phrases):
            engagement_factors += 1
        
        # Check for personal pronouns
        personal_pronouns = ['you', 'your', 'we', 'us', 'our']
        if any(pronoun in text.lower() for pronoun in personal_pronouns):
            engagement_factors += 1
        
        # Check for numbers/statistics
        if re.search(r'\d+', text):
            engagement_factors += 1
        
        # Check for storytelling elements
        story_words = ['story', 'experience', 'journey', 'happened', 'remember']
        if any(word in text.lower() for word in story_words):
            engagement_factors += 1
        
        # Check for urgency/scarcity
        urgency_words = ['now', 'today', 'limited', 'urgent', 'deadline']
        if any(word in text.lower() for word in urgency_words):
            engagement_factors += 1
        
        return engagement_factors / total_factors
    
    def _analyze_bias(self, text: str) -> Dict[str, float]:
        """Analyze potential bias in text (simplified)"""        # This is a simplified implementation
        # In production, use specialized bias detection models
        
        bias_indicators = {
            'gender_bias': 0.0,
            'racial_bias': 0.0,
            'political_bias': 0.0,
            'age_bias': 0.0
        }
        
        text_lower = text.lower()
        
        # Simple keyword-based bias detection
        gender_biased_words = ['bossy', 'emotional', 'aggressive', 'weak']
        if any(word in text_lower for word in gender_biased_words):
            bias_indicators['gender_bias'] = 0.3
        
        # Political bias indicators
        political_words = ['liberal', 'conservative', 'democrat', 'republican']
        if any(word in text_lower for word in political_words):
            bias_indicators['political_bias'] = 0.2
        
        return bias_indicators
    
    def _analyze_toxicity(self, text: str) -> float:
        """Analyze toxicity level (simplified)"""        # Simplified toxicity detection
        # In production, use specialized toxicity detection models
        
        toxic_words = ['hate', 'stupid', 'idiot', 'kill', 'die', 'murder']
        toxic_count = sum(1 for word in toxic_words if word in text.lower())
        
        # Calculate toxicity score (0-1, where 1 is highly toxic)
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        toxicity_score = min(toxic_count / word_count * 10, 1.0)
        return toxicity_score
    
    def _analyze_seo(self, text: str) -> Dict:
        """Analyze SEO quality of text"""        word_count = len(text.split())
        
        # Keyword density analysis (simplified)
        seo_score = 0.0
        
        # Check for optimal length
        if 300 <= word_count <= 2000:
            seo_score += 0.3
        
        # Check for headers (simplified - look for title case)
        if re.search(r'\n[A-Z][^\n]*\n', text):
            seo_score += 0.2
        
        # Check for internal/external links
        if 'http' in text:
            seo_score += 0.2
        
        # Check for meta description elements
        if len(text) > 150:  # Has substantial content
            seo_score += 0.3
        
        return {"seo_score": seo_score}
    
    def _generate_text_fingerprints(self, text: str) -> Dict:
        """Generate fingerprints for text"""        # Clean text for fingerprinting
        clean_text = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Generate different fingerprints
        md5_hash = hashlib.md5(clean_text.encode()).hexdigest()
        sha256_hash = hashlib.sha256(clean_text.encode()).hexdigest()
        
        # Semantic fingerprint (simplified - use first few words)
        words = clean_text.split()[:10]
        semantic_content = ' '.join(words)
        similarity_hash = hashlib.sha256(semantic_content.encode()).hexdigest()
        
        return {
            "text_fingerprint": sha256_hash,
            "similarity_hash": similarity_hash
        }
    
    async def validate_connection(self) -> bool:
        """Validate text analysis capabilities"""        try:
            test_text = "This is a test sentence for validation."
            result = await self.process(test_text)
            return result.success
        except Exception as e:
            self.logger.error(f"Text analysis validation failed: {e}")
            return False


class ContentGenerator(BaseAIModel):
    """Advanced content generation and optimization"""    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.text_generator = None
        self.seo_optimizer = None
        self._initialize_generators()
    
    def _initialize_generators(self):
        """Initialize content generation models"""        try:
            # Initialize text generation model
            self.text_generator = pipeline(
                "text-generation",
                model="gpt2",
                tokenizer="gpt2"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize generators: {e}")
    
    async def process(self, request: ContentGenerationRequest, **kwargs) -> ProcessingResult:
        """Generate content based on request"""        try:
            start_time = datetime.now()
            
            # Generate base content
            content = await self._generate_content(request)
            
            # Optimize for SEO
            optimized_content = await self._optimize_for_seo(content, request)
            
            # Generate metadata
            metadata = await self._generate_metadata(optimized_content, request)
            
            # Calculate quality scores
            quality_metrics = await self._assess_generated_quality(optimized_content)
            
            # Create result
            generated_content = GeneratedContent(
                content=optimized_content,
                title=metadata.get('title'),
                meta_description=metadata.get('meta_description'),
                hashtags=metadata.get('hashtags', []),
                keywords_used=metadata.get('keywords_used', []),
                seo_score=quality_metrics.get('seo_score', 0.0),
                engagement_score=quality_metrics.get('engagement_score', 0.0),
                originality_score=quality_metrics.get('originality_score', 0.0),
                quality_metrics=quality_metrics
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                data=generated_content,
                confidence=0.88,
                processing_time=processing_time,
                model_version="1.0",
                metadata={"content_type": request.content_type.value}
            )
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            return ProcessingResult(
                success=False,
                data=None,
                error_message=str(e)
            )
    
    async def _generate_content(self, request: ContentGenerationRequest) -> str:
        """Generate base content"""        try:
            # Create prompt based on request
            prompt = self._create_generation_prompt(request)
            
            if self.text_generator:
                # Generate using the model
                generated = self.text_generator(
                    prompt,
                    max_length=request.length + len(prompt.split()),
                    num_return_sequences=1,
                    temperature=0.7,
                    pad_token_id=50256  # GPT-2 pad token
                )
                
                if generated and len(generated) > 0:
                    full_text = generated[0]['generated_text']
                    # Extract only the generated part (remove prompt)
                    content = full_text[len(prompt):].strip()
                    return content
            
            # Fallback to template-based generation
            return self._generate_template_content(request)
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            return self._generate_template_content(request)
    
    def _create_generation_prompt(self, request: ContentGenerationRequest) -> str:
        """Create prompt for content generation"""        prompt_parts = []
        
        # Add content type context
        if request.content_type == TextContentType.BLOG_POST:
            prompt_parts.append("Write a comprehensive blog post about")
        elif request.content_type == TextContentType.SOCIAL_MEDIA:
            prompt_parts.append("Create an engaging social media post about")
        elif request.content_type == TextContentType.PRODUCT_DESCRIPTION:
            prompt_parts.append("Write a compelling product description for")
        else:
            prompt_parts.append("Write content about")
        
        # Add topic
        prompt_parts.append(request.topic)
        
        # Add audience context
        if request.target_audience:
            prompt_parts.append(f"for {request.target_audience}")
        
        # Add tone
        if request.tone:
            prompt_parts.append(f"in a {request.tone} tone")
        
        # Add keywords if provided
        if request.keywords:
            keywords_str = ", ".join(request.keywords[:3])  # Limit to 3 keywords
            prompt_parts.append(f"including keywords: {keywords_str}")
        
        prompt = " ".join(prompt_parts) + ".\n\n"
        return prompt
    
    def _generate_template_content(self, request: ContentGenerationRequest) -> str:
        """Generate content using templates (fallback)"""        templates = {
            TextContentType.BLOG_POST: self._generate_blog_post_template(request),
            TextContentType.SOCIAL_MEDIA: self._generate_social_media_template(request),
            TextContentType.PRODUCT_DESCRIPTION: self._generate_product_description_template(request),
            TextContentType.CAPTION: self._generate_caption_template(request),
        }
        
        return templates.get(request.content_type, self._generate_generic_template(request))
    
    def _generate_blog_post_template(self, request: ContentGenerationRequest) -> str:
        """Generate blog post template"""        return f"""# {request.topic.title()}

## Introduction

{request.topic} has become increasingly important in today's digital landscape. This comprehensive guide will explore the key aspects and provide valuable insights for {request.target_audience}.

## Key Points

Understanding {request.topic} requires attention to several crucial factors:

1. **Foundation Knowledge**: Building a solid understanding of core concepts
2. **Practical Application**: Implementing strategies that work
3. **Best Practices**: Following industry standards and recommendations

## Implementation Strategy

When working with {request.topic}, consider these essential steps:

- Research and planning phase
- Implementation and testing
- Monitoring and optimization
- Continuous improvement

## Conclusion

{request.topic} presents both opportunities and challenges. By following the strategies outlined in this guide, {request.target_audience} can achieve better results and maximize their success.

*Keywords: {', '.join(request.keywords[:5])}*"""    
    def _generate_social_media_template(self, request: ContentGenerationRequest) -> str:
        """Generate social media template"""        hashtags = ' '.join([f"#{keyword.replace(' ', '')}" for keyword in request.keywords[:5]])
        
        return f"""🚀 Exciting insights about {request.topic}!

Did you know that {request.topic} can transform your approach to {request.target_audience} success? 

Here are 3 key takeaways:
✅ Essential understanding builds strong foundations
✅ Practical implementation drives real results  
✅ Continuous learning ensures long-term success

What's your experience with {request.topic}? Share in the comments! 👇

{hashtags}

#Success #Growth #Innovation"""    
    def _generate_product_description_template(self, request: ContentGenerationRequest) -> str:
        """Generate product description template"""        return f"""**{request.topic}** - Premium Solution for {request.target_audience}

🌟 **Key Features:**
• Advanced functionality designed for modern needs
• User-friendly interface with intuitive design
• Professional-grade quality and reliability
• Comprehensive support and documentation

💡 **Perfect For:**
{request.target_audience} looking to enhance their capabilities and achieve better results.

🎯 **Benefits:**
- Streamlined workflow and improved efficiency
- Professional results with minimal effort
- Long-term value and reliability
- Expert support when you need it

*Keywords: {', '.join(request.keywords[:3])}*

**Order now and transform your {request.topic} experience!**"""    
    def _generate_caption_template(self, request: ContentGenerationRequest) -> str:
        """Generate caption template"""        hashtags = ' '.join([f"#{keyword.replace(' ', '')}" for keyword in request.keywords[:3]])
        
        return f"""Exploring {request.topic} today! 📸

Perfect moment for {request.target_audience} to discover new possibilities.

{hashtags} #Inspiration #Moment"""    
    def _generate_generic_template(self, request: ContentGenerationRequest) -> str:
        """Generate generic content template"""        return f"""# {request.topic}

This content explores {request.topic} specifically designed for {request.target_audience}.

## Overview

{request.topic} represents an important aspect that deserves attention and understanding.

## Key Information

• Comprehensive approach to {request.topic}
• Practical insights for {request.target_audience}
• Professional guidance and recommendations

## Implementation

Consider these factors when working with {request.topic}:

1. Planning and preparation
2. Execution and monitoring
3. Analysis and optimization

*Focus keywords: {', '.join(request.keywords[:3])}*"""    
    async def _optimize_for_seo(self, content: str, request: ContentGenerationRequest) -> str:
        """Optimize content for SEO"""        # Ensure keywords are naturally integrated
        optimized_content = content
        
        # Add keywords if not present
        for keyword in request.keywords[:3]:  # Limit to top 3 keywords
            if keyword.lower() not in content.lower():
                # Add keyword naturally to the content
                optimized_content = optimized_content.replace(
                    request.topic, 
                    f"{request.topic} {keyword}", 
                    1  # Replace only first occurrence
                )
        
        return optimized_content
    
    async def _generate_metadata(self, content: str, request: ContentGenerationRequest) -> Dict:
        """Generate metadata for content"""        # Generate title
        title = self._generate_title(content, request)
        
        # Generate meta description
        meta_description = self._generate_meta_description(content, request)
        
        # Generate hashtags
        hashtags = self._generate_hashtags(content, request)
        
        # Track keywords used
        keywords_used = [kw for kw in request.keywords if kw.lower() in content.lower()]
        
        return {
            'title': title,
            'meta_description': meta_description,
            'hashtags': hashtags,
            'keywords_used': keywords_used
        }
    
    def _generate_title(self, content: str, request: ContentGenerationRequest) -> str:
        """Generate SEO-optimized title"""        # Extract first keyword for title
        primary_keyword = request.keywords[0] if request.keywords else request.topic
        
        title_templates = [
            f"Complete Guide to {primary_keyword} for {request.target_audience}",
            f"Master {primary_keyword}: Expert Tips and Strategies",
            f"{primary_keyword} Essentials: What {request.target_audience} Need to Know",
            f"Ultimate {primary_keyword} Resource for Success",
        ]
        
        # Choose template based on content type
        if request.content_type == TextContentType.BLOG_POST:
            return title_templates[0]
        elif request.content_type == TextContentType.SOCIAL_MEDIA:
            return f"🚀 {primary_keyword} Tips for {request.target_audience}"
        else:
            return title_templates[1]
    
    def _generate_meta_description(self, content: str, request: ContentGenerationRequest) -> str:
        """Generate meta description"""        # Extract first sentence or create summary
        sentences = re.split(r'[.!?]+', content)
        first_meaningful_sentence = None
        
        for sentence in sentences:
            if len(sentence.strip()) > 50:  # Find substantial sentence
                first_meaningful_sentence = sentence.strip()
                break
        
        if first_meaningful_sentence:
            # Limit to 155 characters for SEO
            meta_desc = first_meaningful_sentence[:155]
            if len(first_meaningful_sentence) > 155:
                meta_desc += "..."
            return meta_desc
        
        # Fallback meta description
        primary_keyword = request.keywords[0] if request.keywords else request.topic
        return f"Discover essential insights about {primary_keyword} for {request.target_audience}. Expert tips and strategies for success."
    
    def _generate_hashtags(self, content: str, request: ContentGenerationRequest) -> List[str]:
        """Generate relevant hashtags"""        hashtags = []
        
        # Add hashtags from keywords
        for keyword in request.keywords[:5]:
            # Clean keyword for hashtag
            hashtag = re.sub(r'[^a-zA-Z0-9]', '', keyword.title())
            if hashtag:
                hashtags.append(f"#{hashtag}")
        
        # Add content type specific hashtags
        type_hashtags = {
            TextContentType.BLOG_POST: ["#Blog", "#Content", "#Guide"],
            TextContentType.SOCIAL_MEDIA: ["#SocialMedia", "#Engagement", "#Community"],
            TextContentType.PRODUCT_DESCRIPTION: ["#Product", "#Quality", "#Innovation"],
        }
        
        hashtags.extend(type_hashtags.get(request.content_type, ["#Content", "#Information"]))
        
        return hashtags[:8]  # Limit to 8 hashtags
    
    async def _assess_generated_quality(self, content: str) -> Dict[str, float]:
        """Assess quality of generated content"""        # Use the text analyzer to assess quality
        analyzer = TextAnalyzer(self.config)
        result = await analyzer.process(content)
        
        if result.success:
            features = result.data
            return {
                'seo_score': features.seo_score,
                'engagement_score': features.engagement_potential,
                'originality_score': features.originality_score,
                'quality_score': features.quality_score,
                'readability_score': features.readability_metrics.get('overall_score', 0.7)
            }
        
        # Fallback scores
        return {
            'seo_score': 0.7,
            'engagement_score': 0.6,
            'originality_score': 0.8,
            'quality_score': 0.7,
            'readability_score': 0.7
        }
    
    async def validate_connection(self) -> bool:
        """Validate content generation capabilities"""        try:
            test_request = ContentGenerationRequest(
                content_type=TextContentType.CAPTION,
                topic="test content",
                target_audience="general",
                tone="professional",
                length=100,
                language=TextLanguage.ENGLISH,
                keywords=["test"],
                style_preferences={},
                seo_requirements={}
            )
            
            result = await self.process(test_request)
            return result.success
        except Exception as e:
            self.logger.error(f"Content generation validation failed: {e}")
            return False


# Export all text models
__all__ = [
    'TextLanguage',
    'TextContentType',
    'SentimentType',
    'TextQuality',
    'TextFeatures',
    'ContentGenerationRequest',
    'GeneratedContent',
    'TextAnalyzer',
    'ContentGenerator'
]
