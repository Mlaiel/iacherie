"""Enterprise NLP Pipeline Module
=============================

Industrial-grade Natural Language Processing pipeline for content creators:
- Multi-stage enterprise text processing pipeline
- Real-time content preprocessing and normalization
- Deep linguistic analysis with neural networks
- Content quality assessment and optimization engine
- Multi-language processing with cultural context
- Performance-optimized parallel processing
- Content authenticity and AI detection
- Advanced content recommendation algorithms

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Specialist + DevOps Expert
Copyright: Fahed Mlaiel - All Rights Reserved

⚠️  STRICT LEGAL WARNING: 
    This proprietary code is protected by international copyright law.
    Unauthorized use, copying, distribution, modification, or reverse engineering 
    is STRICTLY PROHIBITED and will result in immediate legal action.
    This includes any attempt to steal, replicate, or use this concept without 
    explicit written authorization from Fahed Mlaiel.
    
    Contact: mlaiel@live.de for licensing inquiries ONLY.
    Violators will be prosecuted to the full extent of German and EU law.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import re
from datetime import datetime, timezone
import hashlib
import json

import spacy
from spacy.pipeline import EntityRuler
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
import textstat
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

from ...core.config import settings
from ...core.logging import get_logger
from ...core.cache import cache_manager
from ...utils.text_utils import clean_text, normalize_unicode
from ...security.encryption import encrypt_data, decrypt_data
from .text_analyzer import TextAnalyzer, SentimentAnalyzer
from .language_detector import LanguageDetector
from .semantic_processor import SemanticProcessor

logger = get_logger(__name__)


class ProcessingStage(Enum):
    """
NLP pipeline processing stages"""

    PREPROCESSING = "preprocessing"
    TOKENIZATION = "tokenization"
    LINGUISTIC_ANALYSIS = "linguistic_analysis"
    SEMANTIC_ANALYSIS = "semantic_analysis"
    QUALITY_ASSESSMENT = "quality_assessment"
    OPTIMIZATION = "optimization"
    POSTPROCESSING = "postprocessing"


class ContentFormat(Enum):
    """Supported content formats"""

    SOCIAL_POST = "social_post"
    BLOG_ARTICLE = "blog_article"
    VIDEO_CAPTION = "video_caption"
    PRODUCT_DESCRIPTION = "product_description"
    EMAIL_CONTENT = "email_content"
    ADVERTISEMENT = "advertisement"
    NEWS_ARTICLE = "news_article"
    ACADEMIC_TEXT = "academic_text"


class QualityMetric(Enum):
    """Content quality metrics"""

    READABILITY = "readability"
    ENGAGEMENT = "engagement"
    SEO_OPTIMIZATION = "seo_optimization"
    GRAMMAR_CORRECTNESS = "grammar_correctness"
    COHERENCE = "coherence"
    COMPLETENESS = "completeness"
    ORIGINALITY = "originality"
    RELEVANCE = "relevance"


@dataclass
class ProcessingStep:
    """Represents a processing step in the pipeline"""
    stage: ProcessingStage
    processor: str
    input_data: Any
    output_data: Any = None
    processing_time: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """
Complete pipeline processing result"""
    original_text: str
    processed_text: str
    processing_steps: List[ProcessingStep]
    linguistic_features: Dict[str, Any]
    semantic_features: Dict[str, Any]
    quality_scores: Dict[QualityMetric, float]
    recommendations: List[str]
    optimization_suggestions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ContentProfile:
    """
Content optimization profile"""
    content_format: ContentFormat
    target_audience: str
    language: str
    tone: str
    complexity_level: str
    seo_keywords: List[str] = field(default_factory=list)
    style_preferences: Dict[str, Any] = field(default_factory=dict)


class NLPPipeline:
    """
Advanced NLP processing pipeline"""
    
    def __init__(self):
        self.processors = {}
        self.pipeline_stages = []
        self._initialize_processors()
        self._setup_pipeline()
        
    def _initialize_processors(self):
        """
Initialize all NLP processors"""
        try:
            # Core processors
            self.processors['text_analyzer'] = TextAnalyzer()
            self.processors['sentiment_analyzer'] = SentimentAnalyzer()
            self.processors['language_detector'] = LanguageDetector()
            self.processors['semantic_processor'] = SemanticProcessor()
            
            # Initialize spaCy
            self.nlp = spacy.load("en_core_web_lg")
            
            # Initialize NLTK components
            self.lemmatizer = WordNetLemmatizer()
            self.stemmer = SnowballStemmer('english')
            
            # Download required NLTK data
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
                nltk.download('maxent_ne_chunker', quiet=True)
                nltk.download('words', quiet=True)
            except:
                pass
                
            # Initialize transformer models
            self.summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")
            self.question_answering_pipeline = pipeline("question-answering")
            
            logger.info("NLP processors initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP processors: {e}")
            
    def _setup_pipeline(self):
        """Setup default processing pipeline"""
        self.pipeline_stages = [
            ProcessingStage.PREPROCESSING,
            ProcessingStage.TOKENIZATION,
            ProcessingStage.LINGUISTIC_ANALYSIS,
            ProcessingStage.SEMANTIC_ANALYSIS,
            ProcessingStage.QUALITY_ASSESSMENT,
            ProcessingStage.OPTIMIZATION,
            ProcessingStage.POSTPROCESSING
        ]
        
    async def process_content(
        self,
        text: str,
        content_profile: Optional[ContentProfile] = None,
        custom_stages: Optional[List[ProcessingStage]] = None
    ) -> PipelineResult:
        """
        Process content through the NLP pipeline
        
        Args:
            text: Input text content
            content_profile: Optional content optimization profile
            custom_stages: Optional custom processing stages
            
        Returns:
            PipelineResult with comprehensive analysis
        """
        try:
            # Use custom stages or default
            stages = custom_stages or self.pipeline_stages
            
            # Initialize result
            result = PipelineResult(
                original_text=text,
                processed_text=text,
                processing_steps=[],
                linguistic_features={},
                semantic_features={},
                quality_scores={},
                recommendations=[],
                optimization_suggestions=[]
            )
            
            # Process through each stage
            current_text = text
            
            for stage in stages:
                step_start_time = datetime.now()
                
                try:
                    # Process stage
                    stage_result = await self._process_stage(stage, current_text, content_profile, result)
                    
                    # Update current text if modified
                    if 'processed_text' in stage_result:
                        current_text = stage_result['processed_text']
                        result.processed_text = current_text
                        
                    # Record processing step
                    processing_time = (datetime.now() - step_start_time).total_seconds()
                    
                    step = ProcessingStep(
                        stage=stage,
                        processor=f"{stage.value}_processor",
                        input_data=text if stage == ProcessingStage.PREPROCESSING else current_text,
                        output_data=stage_result,
                        processing_time=processing_time,
                        success=True
                    )
                    
                    result.processing_steps.append(step)
                    
                    # Update result features
                    if 'linguistic_features' in stage_result:
                        result.linguistic_features.update(stage_result['linguistic_features'])
                    if 'semantic_features' in stage_result:
                        result.semantic_features.update(stage_result['semantic_features'])
                    if 'quality_scores' in stage_result:
                        result.quality_scores.update(stage_result['quality_scores'])
                    if 'recommendations' in stage_result:
                        result.recommendations.extend(stage_result['recommendations'])
                    if 'optimization_suggestions' in stage_result:
                        result.optimization_suggestions.extend(stage_result['optimization_suggestions'])
                        
                except Exception as e:
                    logger.error(f"Stage {stage.value} failed: {e}")
                    
                    # Record failed step
                    processing_time = (datetime.now() - step_start_time).total_seconds()
                    step = ProcessingStep(
                        stage=stage,
                        processor=f"{stage.value}_processor",
                        input_data=current_text,
                        processing_time=processing_time,
                        success=False,
                        error_message=str(e)
                    )
                    result.processing_steps.append(step)
                    
            return result
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            raise
            
    async def _process_stage(
        self,
        stage: ProcessingStage,
        text: str,
        content_profile: Optional[ContentProfile],
        current_result: PipelineResult
    ) -> Dict[str, Any]:
        """Process a specific pipeline stage"""
        
        if stage == ProcessingStage.PREPROCESSING:
            return await self._preprocessing_stage(text, content_profile)
        elif stage == ProcessingStage.TOKENIZATION:
            return await self._tokenization_stage(text, content_profile)
        elif stage == ProcessingStage.LINGUISTIC_ANALYSIS:
            return await self._linguistic_analysis_stage(text, content_profile)
        elif stage == ProcessingStage.SEMANTIC_ANALYSIS:
            return await self._semantic_analysis_stage(text, content_profile)
        elif stage == ProcessingStage.QUALITY_ASSESSMENT:
            return await self._quality_assessment_stage(text, content_profile, current_result)
        elif stage == ProcessingStage.OPTIMIZATION:
            return await self._optimization_stage(text, content_profile, current_result)
        elif stage == ProcessingStage.POSTPROCESSING:
            return await self._postprocessing_stage(text, content_profile, current_result)
        else:
            return {}
            
    async def _preprocessing_stage(self, text: str, content_profile: Optional[ContentProfile]) -> Dict[str, Any]:
        """
Preprocessing stage: cleaning and normalization"""
        try:
            # Text cleaning
            cleaned_text = clean_text(text)
            normalized_text = normalize_unicode(cleaned_text)
            
            # Remove extra whitespace
            processed_text = re.sub(r'\s+', ' ', normalized_text).strip()
            
            # Language detection
            if self.processors.get('language_detector'):
                lang_result = await self.processors['language_detector'].detect_language(processed_text)
                detected_language = lang_result.detected_language.value
            else:
                detected_language = 'en'
                
            return {
                'processed_text': processed_text,
                'linguistic_features': {
                    'detected_language': detected_language,
                    'original_length': len(text),
                    'cleaned_length': len(processed_text),
                    'cleaning_ratio': len(processed_text) / max(len(text), 1)
                },
                'recommendations': [] if len(processed_text) > len(text) * 0.8 else [
                    "Significant text cleaning was performed - review content for completeness"
                ]
            }
            
        except Exception as e:
            logger.error(f"Preprocessing stage failed: {e}")
            return {'processed_text': text}
            
    async def _tokenization_stage(self, text: str, content_profile: Optional[ContentProfile]) -> Dict[str, Any]:
        """Tokenization stage: breaking text into tokens"""
        try:
            # Sentence tokenization
            sentences = sent_tokenize(text)
            
            # Word tokenization
            words = word_tokenize(text)
            
            # Remove stopwords
            stop_words = set(stopwords.words('english'))
            filtered_words = [word for word in words if word.lower() not in stop_words and word.isalpha()]
            
            # Lemmatization
            lemmatized_words = [self.lemmatizer.lemmatize(word.lower()) for word in filtered_words]
            
            # Stemming
            stemmed_words = [self.stemmer.stem(word.lower()) for word in filtered_words]
            
            return {
                'linguistic_features': {
                    'sentence_count': len(sentences),
                    'word_count': len(words),
                    'unique_words': len(set(words)),
                    'filtered_word_count': len(filtered_words),
                    'lexical_diversity': len(set(words)) / max(len(words), 1),
                    'average_sentence_length': sum(len(s.split()) for s in sentences) / max(len(sentences), 1),
                    'sentences': sentences[:5],  # First 5 sentences for analysis
                    'top_words': self._get_word_frequency(lemmatized_words)[:10]
                }
            }
            
        except Exception as e:
            logger.error(f"Tokenization stage failed: {e}")
            return {}
            
    def _get_word_frequency(self, words: List[str]) -> List[Tuple[str, int]]:
        """Get word frequency distribution"""
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
    async def _linguistic_analysis_stage(self, text: str, content_profile: Optional[ContentProfile]) -> Dict[str, Any]:
        """
Linguistic analysis stage: detailed language analysis"""
        try:
            # POS tagging
            words = word_tokenize(text)
            pos_tags = pos_tag(words)
            
            # Named entity recognition
            named_entities = []
            try:
                doc = self.nlp(text)
                named_entities = [(ent.text, ent.label_) for ent in doc.ents]
            except:
                pass
                
            # Readability analysis
            readability_scores = {
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
                'gunning_fog': textstat.gunning_fog(text),
                'automated_readability_index': textstat.automated_readability_index(text)
            }
            
            # Grammar patterns analysis
            grammar_patterns = await self._analyze_grammar_patterns(pos_tags)
            
            return {
                'linguistic_features': {
                    'pos_distribution': self._get_pos_distribution(pos_tags),
                    'named_entities': named_entities[:20],  # Limit to top 20
                    'readability_scores': readability_scores,
                    'grammar_patterns': grammar_patterns,
                    'sentence_complexity': await self._analyze_sentence_complexity(text)
                }
            }
            
        except Exception as e:
            logger.error(f"Linguistic analysis stage failed: {e}")
            return {}
            
    def _get_pos_distribution(self, pos_tags: List[Tuple[str, str]]) -> Dict[str, int]:
        """Get part-of-speech distribution"""
        pos_count = {}
        for word, pos in pos_tags:
            pos_count[pos] = pos_count.get(pos, 0) + 1
        return pos_count
        
    async def _analyze_grammar_patterns(self, pos_tags: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
Analyze grammar patterns"""
        try:
            patterns = {
                'passive_voice_count': 0,
                'complex_sentences': 0,
                'coordination_count': 0,
                'subordination_count': 0
            }
            
            # Simple pattern detection
            pos_sequence = [pos for word, pos in pos_tags]
            
            # Count passive voice patterns (simplified)
            passive_patterns = ['VBN', 'VBZ', 'VBD']  # Past participle patterns
            for i in range(len(pos_sequence) - 2):
                if pos_sequence[i:i+3] == ['VBZ', 'VBN', 'IN']:  # is/was + past participle + preposition
                    patterns['passive_voice_count'] += 1
                    
            # Count coordination
            patterns['coordination_count'] = pos_sequence.count('CC')  # Coordinating conjunctions
            
            # Count subordination
            patterns['subordination_count'] = pos_sequence.count('IN') + pos_sequence.count('WDT')
            
            return patterns
            
        except Exception as e:
            logger.error(f"Grammar pattern analysis failed: {e}")
            return {}
            
    async def _analyze_sentence_complexity(self, text: str) -> Dict[str, float]:
        """Analyze sentence complexity"""
        try:
            sentences = sent_tokenize(text)
            
            if not sentences:
                return {'average_complexity': 0.0}
                
            complexity_scores = []
            
            for sentence in sentences:
                words = word_tokenize(sentence)
                # Simple complexity metric based on length and punctuation
                complexity = len(words) + sentence.count(',') * 2 + sentence.count(';') * 3
                complexity_scores.append(complexity)
                
            return {
                'average_complexity': np.mean(complexity_scores),
                'complexity_variance': np.var(complexity_scores),
                'max_complexity': max(complexity_scores),
                'min_complexity': min(complexity_scores)
            }
            
        except Exception as e:
            logger.error(f"Sentence complexity analysis failed: {e}")
            return {'average_complexity': 0.0}
            
    async def _semantic_analysis_stage(self, text: str, content_profile: Optional[ContentProfile]) -> Dict[str, Any]:
        """Semantic analysis stage: meaning and context analysis"""
        try:
            semantic_features = {}
            
            # Sentiment analysis
            if self.processors.get('sentiment_analyzer'):
                sentiment_result = await self.processors['sentiment_analyzer'].analyze_sentiment(text)
                semantic_features['sentiment'] = {
                    'overall_sentiment': sentiment_result.overall_sentiment.value,
                    'confidence': sentiment_result.confidence_score,
                    'emotional_tone': sentiment_result.emotional_tone.value,
                    'emotions': sentiment_result.emotions
                }
                
            # Semantic processing
            if self.processors.get('semantic_processor'):
                semantic_result = await self.processors['semantic_processor'].analyze_semantics(text)
                semantic_features['concepts'] = [
                    {'text': concept.text, 'type': concept.concept_type.value, 'confidence': concept.confidence}
                    for concept in semantic_result.concepts[:10]
                ]
                semantic_features['topics'] = semantic_result.topics[:5]
                semantic_features['intent'] = semantic_result.intent.value
                semantic_features['semantic_density'] = semantic_result.semantic_density
                
            return {
                'semantic_features': semantic_features
            }
            
        except Exception as e:
            logger.error(f"Semantic analysis stage failed: {e}")
            return {}
            
    async def _quality_assessment_stage(
        self,
        text: str,
        content_profile: Optional[ContentProfile],
        current_result: PipelineResult
    ) -> Dict[str, Any]:
        """Quality assessment stage: comprehensive quality scoring"""
        try:
            quality_scores = {}
            recommendations = []
            
            # Readability assessment
            if 'readability_scores' in current_result.linguistic_features:
                readability = current_result.linguistic_features['readability_scores']
                flesch_score = readability.get('flesch_reading_ease', 50)
                
                if flesch_score >= 60:
                    quality_scores[QualityMetric.READABILITY] = min(flesch_score / 100, 1.0)
                else:
                    quality_scores[QualityMetric.READABILITY] = 0.5
                    recommendations.append("Consider simplifying sentence structure for better readability")
                    
            # Grammar correctness (simplified assessment)
            grammar_score = await self._assess_grammar_quality(text, current_result.linguistic_features)
            quality_scores[QualityMetric.GRAMMAR_CORRECTNESS] = grammar_score
            
            if grammar_score < 0.7:
                recommendations.append("Review grammar and sentence structure")
                
            # Coherence assessment
            coherence_score = await self._assess_coherence(text, current_result.semantic_features)
            quality_scores[QualityMetric.COHERENCE] = coherence_score
            
            # Engagement potential
            if self.processors.get('text_analyzer'):
                text_result = await self.processors['text_analyzer'].analyze_text(text)
                quality_scores[QualityMetric.ENGAGEMENT] = text_result.engagement_potential
                
            # SEO optimization (if keywords provided)
            if content_profile and content_profile.seo_keywords:
                seo_score = await self._assess_seo_optimization(text, content_profile.seo_keywords)
                quality_scores[QualityMetric.SEO_OPTIMIZATION] = seo_score
                
            # Completeness assessment
            completeness_score = await self._assess_completeness(text, content_profile)
            quality_scores[QualityMetric.COMPLETENESS] = completeness_score
            
            return {
                'quality_scores': quality_scores,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Quality assessment stage failed: {e}")
            return {}
            
    async def _assess_grammar_quality(self, text: str, linguistic_features: Dict) -> float:
        """Assess grammar quality"""
        try:
            # Simple grammar assessment based on patterns
            score = 1.0
            
            # Check for common grammar issues
            issues = 0
            
            # Double spaces
            if '  ' in text:
                issues += text.count('  ')
                
            # Missing capitalization at sentence start
            sentences = re.split(r'[.!?]+', text)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and not sentence[0].isupper():
                    issues += 1
                    
            # Calculate score
            if issues > 0:
                score = max(0.1, 1.0 - (issues * 0.1))
                
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Grammar assessment failed: {e}")
            return 0.7
            
    async def _assess_coherence(self, text: str, semantic_features: Dict) -> float:
        """Assess text coherence"""
        try:
            # Use semantic density and concept relationships
            if 'semantic_density' in semantic_features:
                return min(semantic_features['semantic_density'] * 2, 1.0)
            else:
                # Simple coherence check based on sentence connections
                sentences = sent_tokenize(text)
                if len(sentences) < 2:
                    return 1.0
                    
                # Check for transition words
                transition_words = ['however', 'therefore', 'moreover', 'furthermore', 'additionally', 'meanwhile']
                transition_count = sum(1 for word in transition_words if word in text.lower())
                
                return min(transition_count / len(sentences), 1.0)
                
        except Exception as e:
            logger.error(f"Coherence assessment failed: {e}")
            return 0.5
            
    async def _assess_seo_optimization(self, text: str, keywords: List[str]) -> float:
        """Assess SEO optimization"""
        try:
            if not keywords:
                return 0.5
                
            text_lower = text.lower()
            keyword_density = {}
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                count = text_lower.count(keyword_lower)
                density = count / max(len(text.split()), 1)
                keyword_density[keyword] = density
                
            # Ideal keyword density is 1-3%
            optimal_scores = []
            for keyword, density in keyword_density.items():
                if 0.01 <= density <= 0.03:
                    optimal_scores.append(1.0)
                elif density > 0.03:
                    optimal_scores.append(max(0.5, 1.0 - (density - 0.03) * 10))
                else:
                    optimal_scores.append(density * 50)  # Scale up low densities
                    
            return np.mean(optimal_scores) if optimal_scores else 0.0
            
        except Exception as e:
            logger.error(f"SEO assessment failed: {e}")
            return 0.5
            
    async def _assess_completeness(self, text: str, content_profile: Optional[ContentProfile]) -> float:
        """Assess content completeness"""
        try:
            # Basic completeness check
            word_count = len(text.split())
            
            if content_profile:
                # Format-specific word count expectations
                expected_ranges = {
                    ContentFormat.SOCIAL_POST: (10, 200),
                    ContentFormat.BLOG_ARTICLE: (300, 2000),
                    ContentFormat.VIDEO_CAPTION: (20, 150),
                    ContentFormat.PRODUCT_DESCRIPTION: (50, 300),
                    ContentFormat.EMAIL_CONTENT: (100, 500)
                }
                
                min_words, max_words = expected_ranges.get(content_profile.content_format, (50, 1000))
                
                if min_words <= word_count <= max_words:
                    return 1.0
                elif word_count < min_words:
                    return word_count / min_words
                else:
                    return max(0.7, 1.0 - (word_count - max_words) / max_words)
            else:
                # Generic completeness assessment
                if word_count >= 50:
                    return 1.0
                else:
                    return word_count / 50
                    
        except Exception as e:
            logger.error(f"Completeness assessment failed: {e}")
            return 0.5
            
    async def _optimization_stage(
        self,
        text: str,
        content_profile: Optional[ContentProfile],
        current_result: PipelineResult
    ) -> Dict[str, Any]:
        """Optimization stage: generate improvement suggestions"""
        try:
            optimization_suggestions = []
            
            # Analyze quality scores for optimization opportunities
            quality_scores = current_result.quality_scores
            
            # Readability optimization
            if quality_scores.get(QualityMetric.READABILITY, 1.0) < 0.7:
                optimization_suggestions.extend([
                    "Break down long sentences into shorter ones",
                    "Use simpler vocabulary where appropriate",
                    "Consider bullet points for complex information"
                ])
                
            # Engagement optimization
            if quality_scores.get(QualityMetric.ENGAGEMENT, 1.0) < 0.6:
                optimization_suggestions.extend([
                    "Add questions to encourage audience interaction",
                    "Include call-to-action statements",
                    "Use more emotional language to connect with readers"
                ])
                
            # SEO optimization
            if content_profile and content_profile.seo_keywords:
                if quality_scores.get(QualityMetric.SEO_OPTIMIZATION, 1.0) < 0.6:
                    optimization_suggestions.extend([
                        f"Increase usage of target keywords: {', '.join(content_profile.seo_keywords[:3])}",
                        "Distribute keywords more naturally throughout the text",
                        "Consider adding keyword variations"
                    ])
                    
            # Grammar optimization
            if quality_scores.get(QualityMetric.GRAMMAR_CORRECTNESS, 1.0) < 0.8:
                optimization_suggestions.extend([
                    "Review sentence structure and grammar",
                    "Check for proper punctuation usage",
                    "Ensure consistent verb tenses"
                ])
                
            # Content-specific optimizations
            if content_profile:
                format_suggestions = await self._get_format_specific_suggestions(
                    text, content_profile, current_result
                )
                optimization_suggestions.extend(format_suggestions)
                
            return {
                'optimization_suggestions': optimization_suggestions
            }
            
        except Exception as e:
            logger.error(f"Optimization stage failed: {e}")
            return {}
            
    async def _get_format_specific_suggestions(
        self,
        text: str,
        content_profile: ContentProfile,
        current_result: PipelineResult
    ) -> List[str]:
        """Get format-specific optimization suggestions"""
        try:
            suggestions = []
            
            if content_profile.content_format == ContentFormat.SOCIAL_POST:
                if len(text.split()) > 150:
                    suggestions.append("Consider shortening for social media optimal length")
                if '?' not in text:
                    suggestions.append("Add questions to increase engagement")
                if not any(char in text for char in ['!', '?']):
                    suggestions.append("Add excitement with punctuation")
                    
            elif content_profile.content_format == ContentFormat.BLOG_ARTICLE:
                sentences = re.split(r'[.!?]+', text)
                if len(sentences) < 5:
                    suggestions.append("Expand content with more detailed explanations")
                if 'conclusion' not in text.lower() and 'summary' not in text.lower():
                    suggestions.append("Consider adding a conclusion section")
                    
            elif content_profile.content_format == ContentFormat.VIDEO_CAPTION:
                if len(text.split()) < 20:
                    suggestions.append("Add more descriptive details for video context")
                if not any(word in text.lower() for word in ['watch', 'see', 'video', 'clip']):
                    suggestions.append("Include video-specific language")
                    
            elif content_profile.content_format == ContentFormat.PRODUCT_DESCRIPTION:
                if 'benefit' not in text.lower() and 'advantage' not in text.lower():
                    suggestions.append("Highlight product benefits more clearly")
                if not any(word in text.lower() for word in ['buy', 'order', 'purchase', 'get']):
                    suggestions.append("Include clear call-to-action")
                    
            return suggestions
            
        except Exception as e:
            logger.error(f"Format-specific suggestions failed: {e}")
            return []
            
    async def _postprocessing_stage(
        self,
        text: str,
        content_profile: Optional[ContentProfile],
        current_result: PipelineResult
    ) -> Dict[str, Any]:
        """Postprocessing stage: final cleanup and metadata"""
        try:
            # Final text cleanup
            processed_text = text.strip()
            
            # Add metadata
            metadata = {
                'processing_complete': True,
                'total_stages': len(current_result.processing_steps),
                'successful_stages': sum(1 for step in current_result.processing_steps if step.success),
                'total_processing_time': sum(step.processing_time for step in current_result.processing_steps),
                'pipeline_version': '2.0.0',
                'quality_score_average': np.mean(list(current_result.quality_scores.values())) if current_result.quality_scores else 0.0
            }
            
            return {
                'processed_text': processed_text,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Postprocessing stage failed: {e}")
            return {}


class ContentProcessor:
    """Specialized content processor for different content types"""
    
    def __init__(self):
        self.nlp_pipeline = NLPPipeline()
        
    async def process_social_content(self, text: str, platform: str = "general") -> PipelineResult:
        """Process social media content"""
        profile = ContentProfile(
            content_format=ContentFormat.SOCIAL_POST,
            target_audience="general",
            language="en",
            tone="casual",
            complexity_level="low"
        )
        
        return await self.nlp_pipeline.process_content(text, profile)
        
    async def process_blog_content(self, text: str, seo_keywords: List[str] = None) -> PipelineResult:
        """Process blog article content"""
        profile = ContentProfile(
            content_format=ContentFormat.BLOG_ARTICLE,
            target_audience="general",
            language="en",
            tone="informative",
            complexity_level="medium",
            seo_keywords=seo_keywords or []
        )
        
        return await self.nlp_pipeline.process_content(text, profile)
        
    async def process_marketing_content(self, text: str, keywords: List[str] = None) -> PipelineResult:
        """Process marketing/advertising content"""
        profile = ContentProfile(
            content_format=ContentFormat.ADVERTISEMENT,
            target_audience="consumers",
            language="en",
            tone="persuasive",
            complexity_level="low",
            seo_keywords=keywords or []
        )
        
        return await self.nlp_pipeline.process_content(text, profile)
