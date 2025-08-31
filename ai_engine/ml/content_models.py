"""
Content Models Module

Specialized machine learning models for content generation, analysis,
and optimization in the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import json
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple
import logging
from pathlib import Path
import cv2
import librosa
from PIL import Image
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    GPT2LMHeadModel, GPT2Tokenizer, BlipProcessor, BlipForConditionalGeneration,
    Wav2Vec2Processor, Wav2Vec2ForCTC, pipeline
)

# Optional specialized AI libraries
try:
    import clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    clip = None

try:
    from diffusers import StableDiffusionPipeline
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    StableDiffusionPipeline = None

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None

from scipy.spatial.distance import cosine
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Content types for analysis and generation"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class ContentQuality(Enum):
    """Content quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PROFESSIONAL = "professional"
    VIRAL = "viral"


class ContentCategory(Enum):
    """Content categories"""
    MUSIC = "music"
    BLOG = "blog"
    PHOTO = "photo"
    VIDEO = "video"
    PODCAST = "podcast"
    ART = "art"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    LIFESTYLE = "lifestyle"


@dataclass
class ContentMetadata:
    """Metadata for content analysis"""
    content_id: str
    content_type: ContentType
    category: ContentCategory
    title: str
    description: str
    tags: List[str] = field(default_factory=list)
    creator_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    language: str = "en"
    duration_seconds: Optional[float] = None
    file_size_mb: Optional[float] = None
    resolution: Optional[Tuple[int, int]] = None
    format: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentAnalysisResult:
    """Result from content analysis"""
    content_id: str
    quality_score: float = 0.0
    engagement_prediction: float = 0.0
    virality_potential: float = 0.0
    sentiment_score: float = 0.0
    emotion_scores: Dict[str, float] = field(default_factory=dict)
    theme_detection: List[str] = field(default_factory=list)
    style_analysis: Dict[str, Any] = field(default_factory=dict)
    technical_metrics: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    similar_content_ids: List[str] = field(default_factory=list)
    trending_potential: float = 0.0
    content_safety: Dict[str, float] = field(default_factory=dict)
    seo_metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ContentGenerationConfig:
    """Configuration for content generation"""
    content_type: ContentType
    category: ContentCategory
    style: str = "professional"
    target_audience: str = "general"
    length: Optional[int] = None
    quality_level: ContentQuality = ContentQuality.HIGH
    creativity_level: float = 0.7  # 0.0 to 1.0
    include_trending_elements: bool = True
    language: str = "en"
    seed_content: Optional[str] = None
    custom_prompts: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    output_format: str = "default"


class ContentModel(ABC):
    """Abstract base class for content models"""
    
    def __init__(self, model_name: str, device: str = "auto"):
        self.model_name = model_name
        self.device = self._get_device(device)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.model = None
        self.tokenizer = None
        self.processor = None
    
    def _get_device(self, device: str) -> torch.device:
        """Get appropriate device for model"""
        if device == "auto":
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return torch.device(device)
    
    @abstractmethod
    async def load_model(self):
        """Load the model and associated components"""
        pass
    
    @abstractmethod
    async def analyze_content(self, content: Any, metadata: ContentMetadata) -> ContentAnalysisResult:
        """Analyze content and return analysis results"""
        pass
    
    async def preprocess_content(self, content: Any) -> Any:
        """Preprocess content for analysis"""



        return content
    
    async def postprocess_results(self, results: ContentAnalysisResult) -> ContentAnalysisResult:
        """Postprocess analysis results"""



        return results


class TextContentModel(ContentModel):
    """Model for text content analysis and generation"""
    
    def __init__(self, model_name: str = "bert-base-uncased", device: str = "auto"):
        super().__init__(model_name, device)
        self.sentiment_pipeline = None
        self.generation_model = None
        self.generation_tokenizer = None
        self.nlp = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)
    
    async def load_model(self):
        """Load text analysis models"""



        try:
            # Load BERT for embeddings and classification
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # Load sentiment analysis pipeline
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if self.device.type == "cuda" else -1
            )
            
            # Load text generation model
            self.generation_tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium")
            self.generation_model = GPT2LMHeadModel.from_pretrained("gpt2-medium")
            self.generation_model.to(self.device)
            
            # Load spaCy for NLP tasks
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.logger.warning("spaCy English model not found")
            
            self.logger.info("Text content model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load text model: {e}")
            raise
    
    async def analyze_content(self, text: str, metadata: ContentMetadata) -> ContentAnalysisResult:
        """Analyze text content comprehensively"""
        start_time = time.time()
        
        try:
            # Get text embeddings
            embeddings = await self._get_text_embeddings(text)
            
            # Sentiment analysis
            sentiment_result = self.sentiment_pipeline(text[:512])  # Limit length
            sentiment_score = sentiment_result[0]['score']
            if sentiment_result[0]['label'] == 'LABEL_0':  # Negative
                sentiment_score = -sentiment_score
            elif sentiment_result[0]['label'] == 'LABEL_1':  # Neutral
                sentiment_score = 0.0
            
            # Emotion detection
            emotion_scores = await self._detect_emotions(text)
            
            # Theme detection
            themes = await self._detect_themes(text)
            
            # Style analysis
            style_analysis = await self._analyze_writing_style(text)
            
            # Quality assessment
            quality_score = await self._assess_text_quality(text)
            
            # Engagement prediction
            engagement_prediction = await self._predict_engagement(text, embeddings)
            
            # Virality potential
            virality_potential = await self._assess_virality_potential(text, themes)
            
            # SEO metrics
            seo_metrics = await self._calculate_seo_metrics(text, metadata)
            
            # Content safety
            content_safety = await self._assess_content_safety(text)
            
            # Technical metrics
            technical_metrics = {
                'word_count': len(text.split()),
                'char_count': len(text),
                'sentence_count': len(text.split('.')),
                'paragraph_count': len(text.split('\n\n')),
                'readability_score': self._calculate_readability_score(text),
                'uniqueness_score': self._calculate_uniqueness_score(text),
                'processing_time_ms': (time.time() - start_time) * 1000
            }
            
            # Generate recommendations
            recommendations = await self._generate_text_recommendations(
                text, quality_score, style_analysis, seo_metrics
            )
            
            return ContentAnalysisResult(
                content_id=metadata.content_id,
                quality_score=quality_score,
                engagement_prediction=engagement_prediction,
                virality_potential=virality_potential,
                sentiment_score=sentiment_score,
                emotion_scores=emotion_scores,
                theme_detection=themes,
                style_analysis=style_analysis,
                technical_metrics=technical_metrics,
                recommendations=recommendations,
                content_safety=content_safety,
                seo_metrics=seo_metrics
            )
            
        except Exception as e:
            self.logger.error(f"Text analysis failed: {e}")
            raise
    
    async def _get_text_embeddings(self, text: str) -> torch.Tensor:
        """Get BERT embeddings for text"""
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            max_length=512,
            truncation=True,
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            return outputs.last_hidden_state[:, 0, :]  # CLS token
    
    async def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions in text"""
        emotions = ['joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust']
        emotion_scores = {}
        
        # Simplified emotion detection using keyword matching
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'love', 'amazing', 'wonderful'],
            'sadness': ['sad', 'depressed', 'unhappy', 'sorrow', 'grief'],
            'anger': ['angry', 'rage', 'furious', 'mad', 'hate'],
            'fear': ['scared', 'afraid', 'terrified', 'anxious', 'worried'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished'],
            'disgust': ['disgusting', 'revolting', 'sick', 'gross']
        }
        
        text_lower = text.lower()
        word_count = len(text.split())
        
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = min(count / word_count * 100, 1.0)
        
        return emotion_scores
    
    async def _detect_themes(self, text: str) -> List[str]:
        """Detect themes and topics in text"""
        themes = []
        
        if self.nlp:
            doc = self.nlp(text)
            
            # Extract named entities as potential themes
            entities = [ent.text.lower() for ent in doc.ents 
                       if ent.label_ in ['PERSON', 'ORG', 'EVENT', 'PRODUCT']]
            themes.extend(entities[:10])  # Top 10
            
            # Extract noun phrases as themes
            noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks 
                           if len(chunk.text) > 3]
            themes.extend(noun_phrases[:5])  # Top 5
        
        # Remove duplicates and return
        return list(set(themes))[:15]
    
    async def _analyze_writing_style(self, text: str) -> Dict[str, Any]:
        """Analyze writing style characteristics"""
        words = text.split()
        sentences = text.split('.')
        
        avg_word_length = np.mean([len(word) for word in words])
        avg_sentence_length = np.mean([len(sent.split()) for sent in sentences if sent.strip()])
        
        # Complexity metrics
        complex_words = [word for word in words if len(word) > 6]
        complexity_ratio = len(complex_words) / len(words) if words else 0
        
        return {
            'avg_word_length': float(avg_word_length),
            'avg_sentence_length': float(avg_sentence_length),
            'complexity_ratio': float(complexity_ratio),
            'formality_score': self._calculate_formality_score(text),
            'tone': self._determine_tone(text)
        }
    
    def _calculate_formality_score(self, text: str) -> float:
        """Calculate formality score of text"""
        formal_indicators = ['therefore', 'however', 'consequently', 'furthermore']
        informal_indicators = ["don't", "can't", "won't", "it's", "that's"]
        
        formal_count = sum(1 for indicator in formal_indicators if indicator in text.lower())
        informal_count = sum(1 for indicator in informal_indicators if indicator in text.lower())
        
        if formal_count + informal_count == 0:
            return 0.5
        
        return formal_count / (formal_count + informal_count)
    
    def _determine_tone(self, text: str) -> str:
        """Determine the tone of the text"""
        tones = {
            'professional': ['business', 'company', 'organization', 'strategy'],
            'casual': ['hey', 'yeah', 'cool', 'awesome', 'stuff'],
            'academic': ['research', 'study', 'analysis', 'methodology'],
            'creative': ['imagine', 'dream', 'create', 'inspire', 'artistic']
        }
        
        text_lower = text.lower()
        tone_scores = {}
        
        for tone, keywords in tones.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            tone_scores[tone] = score
        
        return max(tone_scores, key=tone_scores.get) if tone_scores else 'neutral'
    
    async def _assess_text_quality(self, text: str) -> float:
        """Assess overall quality of text content"""
        quality_factors = []
        
        # Length appropriateness
        word_count = len(text.split())
        if 50 <= word_count <= 2000:
            quality_factors.append(0.8)
        else:
            quality_factors.append(0.4)
        
        # Grammar and spelling (simplified check)
        grammar_score = self._check_grammar_quality(text)
        quality_factors.append(grammar_score)
        
        # Coherence (simplified check)
        coherence_score = self._check_coherence(text)
        quality_factors.append(coherence_score)
        
        # Uniqueness
        uniqueness_score = self._calculate_uniqueness_score(text)
        quality_factors.append(uniqueness_score)
        
        return float(np.mean(quality_factors))
    
    def _check_grammar_quality(self, text: str) -> float:
        """Simple grammar quality check"""
        # Basic grammar indicators
        sentences = text.split('.')
        complete_sentences = [s for s in sentences if len(s.strip()) > 5 and ' ' in s.strip()]
        
        if not sentences:
            return 0.0
        
        completion_ratio = len(complete_sentences) / len(sentences)
        return min(completion_ratio * 1.2, 1.0)
    
    def _check_coherence(self, text: str) -> float:
        """Check text coherence using simple metrics"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) < 2:
            return 0.7  # Single sentence gets medium score
        
        # Check for transitional words
        transitions = ['however', 'therefore', 'moreover', 'furthermore', 'additionally', 'consequently']
        transition_count = sum(1 for transition in transitions 
                             for sentence in sentences 
                             if transition in sentence.lower())
        
        transition_score = min(transition_count / len(sentences), 0.5)
        
        # Check for topic consistency (simplified)
        consistency_score = 0.5  # Placeholder
        
        return (transition_score + consistency_score)
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate Flesch reading ease score"""
        sentences = len([s for s in text.split('.') if s.strip()])
        words = len(text.split())
        syllables = sum(self._count_syllables(word) for word in text.split())
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Flesch Reading Ease formula
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0.0, min(100.0, score)) / 100.0  # Normalize to 0-1
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        vowels = 'aeiouy'
        word = word.lower().strip()
        count = sum(1 for char in word if char in vowels)
        
        # Adjust for common patterns
        if word.endswith('e'):
            count -= 1
        if count == 0:
            count = 1
        
        return count
    
    def _calculate_uniqueness_score(self, text: str) -> float:
        """Calculate content uniqueness score"""
        words = text.lower().split()
        unique_words = set(words)
        
        if not words:
            return 0.0
        
        return len(unique_words) / len(words)
    
    async def _predict_engagement(self, text: str, embeddings: torch.Tensor) -> float:
        """Predict engagement potential of text"""
        # Simplified engagement prediction based on various factors
        factors = []
        
        # Length factor (medium length performs better)
        word_count = len(text.split())
        if 100 <= word_count <= 500:
            factors.append(0.8)
        elif 50 <= word_count <= 100 or 500 <= word_count <= 1000:
            factors.append(0.6)
        else:
            factors.append(0.4)
        
        # Emotional content factor
        emotion_words = ['love', 'hate', 'amazing', 'terrible', 'incredible', 'shocking']
        emotion_count = sum(1 for word in emotion_words if word in text.lower())
        emotion_factor = min(emotion_count / len(text.split()) * 10, 1.0)
        factors.append(emotion_factor)
        
        # Question factor (questions drive engagement)
        question_count = text.count('?')
        question_factor = min(question_count / 10, 0.3)
        factors.append(0.5 + question_factor)
        
        # Call-to-action factor
        cta_words = ['share', 'comment', 'like', 'subscribe', 'follow', 'check out']
        cta_count = sum(1 for word in cta_words if word in text.lower())
        cta_factor = min(cta_count / 5, 0.3)
        factors.append(0.5 + cta_factor)
        
        return float(np.mean(factors))
    
    async def _assess_virality_potential(self, text: str, themes: List[str]) -> float:
        """Assess potential for content to go viral"""
        viral_indicators = []
        
        # Trending topics factor
        trending_keywords = ['ai', 'technology', 'breaking', 'exclusive', 'viral', 'trending']
        trending_score = sum(1 for keyword in trending_keywords 
                           for theme in themes 
                           if keyword in theme.lower())
        viral_indicators.append(min(trending_score / 5, 1.0))
        
        # Emotional intensity
        high_emotion_words = ['shocking', 'unbelievable', 'amazing', 'outrageous', 'incredible']
        emotion_intensity = sum(1 for word in high_emotion_words if word in text.lower())
        viral_indicators.append(min(emotion_intensity / 3, 1.0))
        
        # Shareability factors
        shareable_elements = ['how to', 'you won\'t believe', 'this will', 'must see']
        shareability = sum(1 for element in shareable_elements if element in text.lower())
        viral_indicators.append(min(shareability / 2, 1.0))
        
        return float(np.mean(viral_indicators)) if viral_indicators else 0.0
    
    async def _calculate_seo_metrics(self, text: str, metadata: ContentMetadata) -> Dict[str, Any]:
        """Calculate SEO-related metrics"""
        words = text.lower().split()
        
        # Keyword density for title words
        title_words = metadata.title.lower().split() if metadata.title else []
        keyword_density = {}
        
        for word in title_words:
            if len(word) > 2:  # Ignore short words
                density = words.count(word) / len(words) if words else 0
                keyword_density[word] = density
        
        # Content structure
        headings = text.count('#')  # Markdown headings
        paragraphs = len([p for p in text.split('\n\n') if p.strip()])
        
        return {
            'keyword_density': keyword_density,
            'content_length': len(words),
            'heading_count': headings,
            'paragraph_count': paragraphs,
            'meta_description_length': len(metadata.description) if metadata.description else 0,
            'title_length': len(metadata.title) if metadata.title else 0
        }
    
    async def _assess_content_safety(self, text: str) -> Dict[str, float]:
        """Assess content safety and appropriateness"""
        safety_scores = {}
        
        # Toxic language detection (simplified)
        toxic_words = ['hate', 'violence', 'harassment', 'discrimination']
        toxic_count = sum(1 for word in toxic_words if word in text.lower())
        safety_scores['toxicity'] = min(toxic_count / len(text.split()) * 100, 1.0)
        
        # Spam detection
        spam_indicators = ['click here', 'buy now', 'limited time', 'act now']
        spam_count = sum(1 for indicator in spam_indicators if indicator in text.lower())
        safety_scores['spam_likelihood'] = min(spam_count / 5, 1.0)
        
        # Overall safety score (inverse of risk)
        overall_risk = (safety_scores['toxicity'] + safety_scores['spam_likelihood']) / 2
        safety_scores['safety_score'] = 1.0 - overall_risk
        
        return safety_scores
    
    async def _generate_text_recommendations(
        self,
        text: str,
        quality_score: float,
        style_analysis: Dict[str, Any],
        seo_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate improvement recommendations for text"""
        recommendations = []
        
        # Quality improvements
        if quality_score < 0.6:
            recommendations.append("Consider improving grammar and sentence structure")
            recommendations.append("Add more descriptive and engaging content")
        
        # Length recommendations
        word_count = len(text.split())
        if word_count < 50:
            recommendations.append("Consider expanding content for better engagement")
        elif word_count > 2000:
            recommendations.append("Consider breaking into smaller sections or multiple posts")
        
        # Style recommendations
        if style_analysis['complexity_ratio'] > 0.3:
            recommendations.append("Use simpler vocabulary for broader audience appeal")
        if style_analysis['avg_sentence_length'] > 25:
            recommendations.append("Break down long sentences for better readability")
        
        # SEO recommendations
        if seo_metrics['heading_count'] == 0 and word_count > 200:
            recommendations.append("Add headings to improve content structure and SEO")
        
        # Engagement recommendations
        if '?' not in text:
            recommendations.append("Add questions to increase audience engagement")
        
        return recommendations
    
    async def generate_content(self, config: ContentGenerationConfig) -> str:
        """Generate text content based on configuration"""



        try:
            # Prepare prompt based on configuration
            prompt = self._build_generation_prompt(config)
            
            # Tokenize input
            inputs = self.generation_tokenizer.encode(prompt, return_tensors='pt').to(self.device)
            
            # Generate with specific parameters
            with torch.no_grad():
                outputs = self.generation_model.generate(
                    inputs,
                    max_length=inputs.shape[1] + (config.length or 200),
                    temperature=config.creativity_level,
                    do_sample=True,
                    pad_token_id=self.generation_tokenizer.eos_token_id,
                    num_return_sequences=1
                )
            
            # Decode generated text
            generated_text = self.generation_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the original prompt
            generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            self.logger.error(f"Text generation failed: {e}")
            return f"Error generating content: {str(e)}"
    
    def _build_generation_prompt(self, config: ContentGenerationConfig) -> str:
        """Build prompt for text generation"""
        prompt_parts = []
        
        # Add style instruction
        prompt_parts.append(f"Write a {config.style} {config.category.value} content")
        
        # Add target audience
        if config.target_audience != "general":
            prompt_parts.append(f"for {config.target_audience}")
        
        # Add seed content if provided
        if config.seed_content:
            prompt_parts.append(f"based on: {config.seed_content}")
        
        # Add custom prompts
        if config.custom_prompts:
            prompt_parts.extend(config.custom_prompts)
        
        return ". ".join(prompt_parts) + ". Content:"


class ImageContentModel(ContentModel):
    """Model for image content analysis and generation"""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32", device: str = "auto"):
        super().__init__(model_name, device)
        self.clip_model = None
        self.clip_preprocess = None
        self.generation_pipeline = None
        self.caption_processor = None
        self.caption_model = None
    
    async def load_model(self):
        """Load image analysis and generation models"""



        try:
            # Load CLIP for image understanding
            self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)
            
            # Load image captioning model
            self.caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            self.caption_model.to(self.device)
            
            # Load image generation pipeline (optional, requires significant GPU memory)
            try:
                self.generation_pipeline = StableDiffusionPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5",
                    torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
                )
                self.generation_pipeline.to(self.device)
            except Exception as e:
                self.logger.warning(f"Could not load image generation pipeline: {e}")
            
            self.logger.info("Image content model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load image model: {e}")
            raise
    
    async def analyze_content(self, image_path: str, metadata: ContentMetadata) -> ContentAnalysisResult:
        """Analyze image content comprehensively"""
        start_time = time.time()
        
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.clip_preprocess(image).unsqueeze(0).to(self.device)
            
            # Generate caption
            caption = await self._generate_image_caption(image)
            
            # Analyze visual features
            visual_features = await self._analyze_visual_features(image_path)
            
            # Aesthetic quality assessment
            quality_score = await self._assess_image_quality(image, visual_features)
            
            # Style analysis
            style_analysis = await self._analyze_image_style(image, image_tensor)
            
            # Emotion detection from image
            emotion_scores = await self._detect_image_emotions(image_tensor, caption)
            
            # Technical metrics
            technical_metrics = await self._calculate_image_technical_metrics(image_path, image)
            
            # Engagement prediction
            engagement_prediction = await self._predict_image_engagement(
                visual_features, style_analysis, technical_metrics
            )
            
            # Content safety
            content_safety = await self._assess_image_safety(image, caption)
            
            # Generate recommendations
            recommendations = await self._generate_image_recommendations(
                visual_features, quality_score, style_analysis, technical_metrics
            )
            
            technical_metrics['processing_time_ms'] = (time.time() - start_time) * 1000
            
            return ContentAnalysisResult(
                content_id=metadata.content_id,
                quality_score=quality_score,
                engagement_prediction=engagement_prediction,
                emotion_scores=emotion_scores,
                theme_detection=[caption] if caption else [],
                style_analysis=style_analysis,
                technical_metrics=technical_metrics,
                recommendations=recommendations,
                content_safety=content_safety
            )
            
        except Exception as e:
            self.logger.error(f"Image analysis failed: {e}")
            raise
    
    async def _generate_image_caption(self, image: Image.Image) -> str:
        """Generate caption for image"""



        try:
            inputs = self.caption_processor(image, return_tensors="pt").to(self.device)
            out = self.caption_model.generate(**inputs, max_length=50)
            caption = self.caption_processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            self.logger.error(f"Caption generation failed: {e}")
            return ""
    
    async def _analyze_visual_features(self, image_path: str) -> Dict[str, Any]:
        """Analyze visual features of image"""
        image = cv2.imread(image_path)
        
        features = {}
        
        # Color analysis
        features['dominant_colors'] = self._get_dominant_colors(image)
        features['color_diversity'] = self._calculate_color_diversity(image)
        features['brightness'] = float(np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)))
        features['contrast'] = float(np.std(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)))
        
        # Composition analysis
        features['rule_of_thirds_score'] = self._analyze_rule_of_thirds(image)
        features['symmetry_score'] = self._analyze_symmetry(image)
        
        # Complexity analysis
        edges = cv2.Canny(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), 50, 150)
        features['edge_density'] = float(np.sum(edges > 0) / edges.size)
        
        return features
    
    def _get_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[List[int]]:
        """Extract dominant colors from image"""
        from sklearn.cluster import KMeans
        
        # Reshape image to pixel array
        pixels = image.reshape(-1, 3)
        
        # Apply k-means clustering
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get dominant colors
        colors = kmeans.cluster_centers_.astype(int)
        return colors.tolist()
    
    def _calculate_color_diversity(self, image: np.ndarray) -> float:
        """Calculate color diversity using histogram"""
        hist_b = cv2.calcHist([image], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([image], [1], None, [256], [0, 256])
        hist_r = cv2.calcHist([image], [2], None, [256], [0, 256])
        
        # Calculate entropy for each channel
        def entropy(hist):
            hist = hist.flatten()
            hist = hist[hist > 0]  # Remove zeros
            hist = hist / hist.sum()  # Normalize
            return -np.sum(hist * np.log2(hist))
        
        entropy_b = entropy(hist_b)
        entropy_g = entropy(hist_g)
        entropy_r = entropy(hist_r)
        
        return float((entropy_b + entropy_g + entropy_r) / 3)
    
    def _analyze_rule_of_thirds(self, image: np.ndarray) -> float:
        """Analyze adherence to rule of thirds"""
        h, w = image.shape[:2]
        
        # Define thirds lines
        v_lines = [w // 3, 2 * w // 3]
        h_lines = [h // 3, 2 * h // 3]
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Calculate interest points near thirds lines
        interest_score = 0
        for v_line in v_lines:
            for h_line in h_lines:
                # Check 20x20 region around intersection
                region = edges[max(0, h_line-10):min(h, h_line+10), 
                             max(0, v_line-10):min(w, v_line+10)]
                interest_score += np.sum(region > 0)
        
        # Normalize by total edges
        total_edges = np.sum(edges > 0)
        return float(interest_score / total_edges) if total_edges > 0 else 0.0
    
    def _analyze_symmetry(self, image: np.ndarray) -> float:
        """Analyze image symmetry"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        # Vertical symmetry
        left_half = gray[:, :w//2]
        right_half = cv2.flip(gray[:, w//2:], 1)
        
        # Resize to match if needed
        min_width = min(left_half.shape[1], right_half.shape[1])
        left_half = left_half[:, :min_width]
        right_half = right_half[:, :min_width]
        
        # Calculate symmetry score
        diff = cv2.absdiff(left_half, right_half)
        symmetry_score = 1.0 - (np.mean(diff) / 255.0)
        
        return float(symmetry_score)
    
    async def _assess_image_quality(self, image: Image.Image, visual_features: Dict[str, Any]) -> float:
        """Assess overall image quality"""
        quality_factors = []
        
        # Resolution factor
        width, height = image.size
        resolution_score = min((width * height) / (1920 * 1080), 1.0)
        quality_factors.append(resolution_score)
        
        # Brightness and contrast
        brightness = visual_features['brightness']
        contrast = visual_features['contrast']
        
        # Optimal brightness range
        brightness_score = 1.0 - abs(brightness - 127.5) / 127.5
        quality_factors.append(brightness_score)
        
        # Sufficient contrast
        contrast_score = min(contrast / 50.0, 1.0)  # Normalize contrast
        quality_factors.append(contrast_score)
        
        # Color diversity
        color_diversity = visual_features['color_diversity']
        diversity_score = min(color_diversity / 6.0, 1.0)  # Max entropy ~8 bits
        quality_factors.append(diversity_score)
        
        # Composition score
        composition_score = (
            visual_features['rule_of_thirds_score'] * 0.6 + 
            visual_features['symmetry_score'] * 0.4
        )
        quality_factors.append(composition_score)
        
        return float(np.mean(quality_factors))
    
    async def _analyze_image_style(self, image: Image.Image, image_tensor: torch.Tensor) -> Dict[str, Any]:
        """Analyze artistic and stylistic elements"""
        # Get CLIP features for style analysis
        with torch.no_grad():
            image_features = self.clip_model.encode_image(image_tensor)
        
        # Define style descriptors
        style_descriptors = [
            "professional photography", "artistic", "vintage", "modern", 
            "minimalist", "colorful", "black and white", "portrait", 
            "landscape", "abstract", "realistic", "dramatic"
        ]
        
        # Calculate similarity with style descriptors
        text_inputs = torch.cat([clip.tokenize(desc) for desc in style_descriptors]).to(self.device)
        with torch.no_grad():
            text_features = self.clip_model.encode_text(text_inputs)
        
        # Calculate similarities
        similarities = F.cosine_similarity(image_features, text_features)
        
        # Create style profile
        style_profile = {}
        for i, descriptor in enumerate(style_descriptors):
            style_profile[descriptor] = float(similarities[i])
        
        # Determine primary style
        primary_style = max(style_profile, key=style_profile.get)
        
        return {
            'primary_style': primary_style,
            'style_confidence': float(style_profile[primary_style]),
            'style_profile': style_profile
        }
    
    async def _detect_image_emotions(self, image_tensor: torch.Tensor, caption: str) -> Dict[str, float]:
        """Detect emotions conveyed by image"""
        # Emotion descriptors
        emotion_descriptors = [
            "happy joyful", "sad melancholy", "angry intense", 
            "peaceful calm", "exciting energetic", "mysterious dark"
        ]
        
        # Calculate similarities with emotion descriptors
        text_inputs = torch.cat([clip.tokenize(desc) for desc in emotion_descriptors]).to(self.device)
        
        with torch.no_grad():
            image_features = self.clip_model.encode_image(image_tensor)
            text_features = self.clip_model.encode_text(text_inputs)
            similarities = F.cosine_similarity(image_features, text_features)
        
        emotions = ['joy', 'sadness', 'anger', 'peace', 'excitement', 'mystery']
        emotion_scores = {}
        
        for i, emotion in enumerate(emotions):
            emotion_scores[emotion] = float(similarities[i])
        
        return emotion_scores
    
    async def _calculate_image_technical_metrics(self, image_path: str, image: Image.Image) -> Dict[str, Any]:
        """Calculate technical metrics for image"""
        from pathlib import Path
        
        file_path = Path(image_path)
        file_size = file_path.stat().st_size / (1024 * 1024)  # MB
        
        width, height = image.size
        aspect_ratio = width / height
        
        # Calculate sharpness using Laplacian variance
        cv_image = cv2.imread(image_path)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate noise level (simplified)
        noise_level = np.std(cv2.GaussianBlur(gray, (5, 5), 0) - gray)
        
        return {
            'width': width,
            'height': height,
            'aspect_ratio': float(aspect_ratio),
            'file_size_mb': float(file_size),
            'megapixels': float((width * height) / 1000000),
            'sharpness_score': float(laplacian_var),
            'noise_level': float(noise_level),
            'format': image.format or 'Unknown'
        }
    
    async def _predict_image_engagement(
        self,
        visual_features: Dict[str, Any],
        style_analysis: Dict[str, Any],
        technical_metrics: Dict[str, Any]
    ) -> float:
        """Predict engagement potential of image"""
        engagement_factors = []
        
        # Quality factors
        if technical_metrics['sharpness_score'] > 100:  # Sharp image
            engagement_factors.append(0.8)
        else:
            engagement_factors.append(0.4)
        
        # Resolution factor
        if technical_metrics['megapixels'] > 2:  # High resolution
            engagement_factors.append(0.7)
        else:
            engagement_factors.append(0.5)
        
        # Color vibrancy
        color_diversity = visual_features['color_diversity']
        if color_diversity > 4:  # Colorful
            engagement_factors.append(0.8)
        else:
            engagement_factors.append(0.6)
        
        # Composition quality
        composition = (visual_features['rule_of_thirds_score'] + visual_features['symmetry_score']) / 2
        engagement_factors.append(composition)
        
        # Style confidence
        style_confidence = style_analysis['style_confidence']
        engagement_factors.append(style_confidence)
        
        return float(np.mean(engagement_factors))
    
    async def _assess_image_safety(self, image: Image.Image, caption: str) -> Dict[str, float]:
        """Assess image safety and appropriateness"""
        safety_scores = {}
        
        # Content analysis based on caption
        inappropriate_keywords = ['violence', 'explicit', 'inappropriate', 'offensive']
        inappropriate_count = sum(1 for keyword in inappropriate_keywords 
                                if keyword in caption.lower())
        
        content_risk = min(inappropriate_count / 3, 1.0)
        safety_scores['content_safety'] = 1.0 - content_risk
        
        # Technical safety (e.g., no corrupted data)
        try:
            # Simple check - if we can process the image, it's probably safe
            image.verify()
            safety_scores['technical_safety'] = 1.0
        except Exception:
            safety_scores['technical_safety'] = 0.0
        
        # Overall safety
        safety_scores['overall_safety'] = (
            safety_scores['content_safety'] + safety_scores['technical_safety']
        ) / 2
        
        return safety_scores
    
    async def _generate_image_recommendations(
        self,
        visual_features: Dict[str, Any],
        quality_score: float,
        style_analysis: Dict[str, Any],
        technical_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate improvement recommendations for images"""
        recommendations = []
        
        # Quality improvements
        if quality_score < 0.6:
            recommendations.append("Consider improving image composition and lighting")
        
        # Technical recommendations
        if technical_metrics['sharpness_score'] < 50:
            recommendations.append("Image appears blurry - ensure proper focus")
        
        if technical_metrics['megapixels'] < 1:
            recommendations.append("Consider using higher resolution for better quality")
        
        # Color recommendations
        if visual_features['brightness'] < 80:
            recommendations.append("Image appears too dark - consider brightening")
        elif visual_features['brightness'] > 180:
            recommendations.append("Image appears overexposed - consider reducing brightness")
        
        if visual_features['contrast'] < 30:
            recommendations.append("Increase contrast for more visual impact")
        
        # Composition recommendations
        if visual_features['rule_of_thirds_score'] < 0.1:
            recommendations.append("Consider repositioning key elements using rule of thirds")
        
        # Style recommendations
        if style_analysis['style_confidence'] < 0.5:
            recommendations.append("Develop a more distinctive visual style")
        
        return recommendations


# Export main classes
__all__ = [
    'ContentModel',
    'TextContentModel',
    'ImageContentModel',
    'ContentMetadata',
    'ContentAnalysisResult',
    'ContentGenerationConfig',
    'ContentType',
    'ContentQuality',
    'ContentCategory'
]
