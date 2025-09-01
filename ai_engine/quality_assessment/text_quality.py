"""Text Quality Assessment Module

Advanced text quality analysis for writers, content creators, and digital marketers.
Implements professional text metrics and industry-standard content quality assessment.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.
"""

import asyncio
import logging
import re
import string
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import math
import nltk
from textstat import flesch_reading_ease, flesch_kincaid_grade, gunning_fog, automated_readability_index
from textblob import TextBlob
import language_tool_python
from collections import Counter

from ..core.base_models import BaseAIModel, ModelConfig, ModelType, ModelProvider
from ..core.exceptions import QualityCheckError, ContentValidationError
from ..core.performance import PerformanceMonitor, monitor_performance
from ..core.metrics import MetricsCollector, metrics_collector

logger = logging.getLogger(__name__)


class TextType(Enum):
    """
Text content types"""

    ARTICLE = "article"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    MARKETING_COPY = "marketing_copy"
    TECHNICAL_DOCUMENT = "technical_document"
    CREATIVE_WRITING = "creative_writing"
    NEWS = "news"
    REVIEW = "review"
    EMAIL = "email"
    SCRIPT = "script"


class WritingTone(Enum):
    """Writing tone categories"""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FORMAL = "formal"
    FRIENDLY = "friendly"
    PERSUASIVE = "persuasive"
    INFORMATIVE = "informative"
    ENTERTAINING = "entertaining"
    AUTHORITATIVE = "authoritative"


class ReadabilityLevel(Enum):
    """Text readability levels"""

    VERY_EASY = "very_easy"
    EASY = "easy"
    FAIRLY_EASY = "fairly_easy"
    STANDARD = "standard"
    FAIRLY_DIFFICULT = "fairly_difficult"
    DIFFICULT = "difficult"
    VERY_DIFFICULT = "very_difficult"


@dataclass
class GrammarAnalysis:
    """Grammar and language analysis results"""
    total_errors: int = field(default=0)
    grammar_errors: int = field(default=0)
    spelling_errors: int = field(default=0)
    style_errors: int = field(default=0)
    punctuation_errors: int = field(default=0)
    
    # Error details
    error_details: List[Dict] = field(default_factory=list)
    
    # Grammar score (0-100)
    grammar_score: float = field(default=100.0)
    
    # Language detection
    detected_language: str = field(default="unknown")
    language_confidence: float = field(default=0.0)


@dataclass
class ReadabilityAnalysis:
    """Text readability analysis"""
    flesch_score: float = field(default=0.0)
    flesch_kincaid_grade: float = field(default=0.0)
    gunning_fog_index: float = field(default=0.0)
    automated_readability_index: float = field(default=0.0)
    
    # Reading level classification
    readability_level: ReadabilityLevel = field(default=ReadabilityLevel.STANDARD)
    target_audience: str = field(default="general")
    
    # Detailed metrics
    average_sentence_length: float = field(default=0.0)
    average_syllables_per_word: float = field(default=0.0)
    complex_words_percentage: float = field(default=0.0)
    
    # Overall readability score
    readability_score: float = field(default=50.0)


@dataclass
class ContentStructure:
    """Content structure analysis"""
    word_count: int = field(default=0)
    sentence_count: int = field(default=0)
    paragraph_count: int = field(default=0)
    character_count: int = field(default=0)
    character_count_no_spaces: int = field(default=0)
    
    # Structure quality
    average_words_per_sentence: float = field(default=0.0)
    average_sentences_per_paragraph: float = field(default=0.0)
    
    # Headers and formatting
    headers_count: int = field(default=0)
    subheaders_count: int = field(default=0)
    lists_count: int = field(default=0)
    
    # Keywords and topics
    keyword_density: Dict[str, float] = field(default_factory=dict)
    top_keywords: List[Tuple[str, int]] = field(default_factory=list)
    
    # Structure score
    structure_score: float = field(default=50.0)


@dataclass
class SentimentAnalysis:
    """
Text sentiment and emotion analysis"""
    polarity: float = field(default=0.0)  # -1 to 1
    subjectivity: float = field(default=0.0)  # 0 to 1
    
    # Sentiment classification
    sentiment_label: str = field(default="neutral")
    emotion_scores: Dict[str, float] = field(default_factory=dict)
    
    # Engagement potential
    engagement_score: float = field(default=50.0)
    emotional_impact: float = field(default=50.0)


@dataclass
class StyleAnalysis:
    """Writing style analysis"""
    writing_tone: WritingTone = field(default=WritingTone.INFORMATIVE)
    formality_score: float = field(default=50.0)
    
    # Vocabulary analysis
    unique_words: int = field(default=0)
    vocabulary_richness: float = field(default=0.0)
    advanced_vocabulary_percentage: float = field(default=0.0)
    
    # Sentence variety
    sentence_variety_score: float = field(default=50.0)
    passive_voice_percentage: float = field(default=0.0)
    
    # Style consistency
    consistency_score: float = field(default=50.0)
    
    # Overall style score
    style_score: float = field(default=50.0)


@dataclass
class TextQualityProfile:
    """
Comprehensive text quality profile"""
    # Basic properties
    content_type: TextType = field(default=TextType.ARTICLE)
    text_length: int = field(default=0)
    reading_time_minutes: float = field(default=0.0)
    
    # Analysis components
    grammar: GrammarAnalysis = field(default_factory=GrammarAnalysis)
    readability: ReadabilityAnalysis = field(default_factory=ReadabilityAnalysis)
    structure: ContentStructure = field(default_factory=ContentStructure)
    sentiment: SentimentAnalysis = field(default_factory=SentimentAnalysis)
    style: StyleAnalysis = field(default_factory=StyleAnalysis)
    
    # SEO analysis
    seo_score: float = field(default=50.0)
    meta_description_quality: float = field(default=50.0)
    title_quality: float = field(default=50.0)
    internal_links: int = field(default=0)
    external_links: int = field(default=0)
    
    # Quality scores
    technical_score: float = field(default=0.0)
    content_score: float = field(default=0.0)
    engagement_score: float = field(default=0.0)
    
    # Overall quality
    overall_quality_score: float = field(default=0.0)
    quality_level: str = field(default="acceptable")
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)


@dataclass
class TextQualityMetrics:
    """Text quality metrics container"""
    profile: TextQualityProfile = field(default_factory=TextQualityProfile)
    
    # Platform compliance
    social_media_ready: bool = field(default=False)
    blog_ready: bool = field(default=False)
    email_ready: bool = field(default=False)
    seo_optimized: bool = field(default=False)
    
    # Content characteristics
    originality_score: float = field(default=50.0)
    expertise_level: str = field(default="intermediate")
    target_audience_match: float = field(default=50.0)
    
    # Performance indicators
    viral_potential: float = field(default=30.0)
    conversion_potential: float = field(default=40.0)
    shareability_score: float = field(default=30.0)
    
    # Metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = field(default=0.0)
    confidence: float = field(default=0.0)


class TextQualityAnalyzer(BaseAIModel):
    """
    Professional Text Quality Analyzer
    
    Provides comprehensive text quality assessment for:
    - Content creators and bloggers
    - Digital marketers and copywriters
    - Social media managers
    - Technical writers and journalists
    - SEO optimization specialists
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """
Initialize text quality analyzer"""
        super().__init__(config or ModelConfig(
            name="text_quality_analyzer",
            model_type=ModelType.TEXT_MODEL,
            provider=ModelProvider.LOCAL
        ))
        
        # self.performance_monitor = performance_monitor
        # self.metrics_collector = metrics_collector
        
        # Initialize NLTK components
        self._initialize_nltk()
        
        # Initialize grammar checker
        try:
            self.grammar_tool = language_tool_python.LanguageTool('en-US')
        except Exception as e:
            logger.warning(f"Grammar tool initialization failed: {str(e)}")
            self.grammar_tool = None
        
        # Platform requirements
        self.platform_requirements = {
            'instagram': {
                'caption_max_length': 2200,
                'optimal_length': 125,
                'hashtag_limit': 30,
                'tone': [WritingTone.CASUAL, WritingTone.FRIENDLY, WritingTone.ENTERTAINING]
            },
            'twitter': {
                'max_length': 280,
                'optimal_length': 100,
                'hashtag_limit': 2,
                'tone': [WritingTone.CASUAL, WritingTone.INFORMATIVE]
            },
            'linkedin': {
                'post_max_length': 3000,
                'optimal_length': 1300,
                'tone': [WritingTone.PROFESSIONAL, WritingTone.INFORMATIVE]
            },
            'facebook': {
                'max_length': 63206,
                'optimal_length': 40,
                'tone': [WritingTone.FRIENDLY, WritingTone.CASUAL]
            },
            'blog': {
                'min_length': 300,
                'optimal_length': 1600,
                'max_length': 5000,
                'readability': [ReadabilityLevel.EASY, ReadabilityLevel.FAIRLY_EASY, ReadabilityLevel.STANDARD]
            },
            'email': {
                'subject_max_length': 50,
                'preview_max_length': 90,
                'optimal_length': 200,
                'tone': [WritingTone.PROFESSIONAL, WritingTone.FRIENDLY]
            }
        }
        
        # Advanced vocabulary words (simplified set)
        self.advanced_vocabulary = {
            'aberration', 'abhor', 'acquiesce', 'alacrity', 'amiable', 'appease', 'arcane',
            'avarice', 'brazen', 'brevity', 'candor', 'capricious', 'caustic', 'chicanery',
            'coalesce', 'cogent', 'complacent', 'convoluted', 'corroborate', 'craven',
            'cursory', 'dearth', 'debacle', 'deference', 'delineate', 'deride', 'desiccate',
            'desultory', 'deterrent', 'didactic', 'diffident', 'digress', 'diligent',
            'discordant', 'disdain', 'disparage', 'disseminate', 'dogmatic', 'ebullient',
            'eclectic', 'efficacy', 'elicit', 'elucidate', 'emulate', 'enervate', 'enhance',
            'ephemeral', 'equivocate', 'erudite', 'esoteric', 'exacerbate', 'exonerate',
            'expedite', 'extol', 'facetious', 'fastidious', 'filibuster', 'flagrant',
            'fledgling', 'fortuitous', 'fractious', 'garrulous', 'gratuitous', 'gregarious',
            'hackneyed', 'halcyon', 'hegemony', 'heresy', 'heterodox', 'histrionic',
            'homogeneous', 'hyperbole', 'iconoclast', 'idiosyncrasy', 'ignominious',
            'immutable', 'impair', 'impartial', 'impetuous', 'impinge', 'inadvertent',
            'inchoate', 'incongruous', 'incontrovertible', 'indigenous', 'indolent',
            'ineffable', 'inert', 'inexorable', 'ingenuous', 'inherent', 'inimical',
            'insidious', 'insipid', 'intractable', 'intransigent', 'inveterate', 'irascible'
        }
        
        logger.info("Text Quality Analyzer initialized successfully")
    
    def _initialize_nltk(self):
        """Initialize required NLTK components"""
        try:
            # Download required NLTK data
            required_packages = ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'vader_lexicon']
            for package in required_packages:
                try:
                    nltk.data.find(f'tokenizers/{package}')
                except LookupError:
                    try:
                        nltk.download(package, quiet=True)
                    except Exception:
                        pass  # Continue without this package
        except Exception as e:
            logger.warning(f"NLTK initialization warning: {str(e)}")
    
    @monitor_performance
    async def analyze_quality(
        self,
        text: str,
        content_type: Optional[TextType] = None,
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive text quality analysis
        
        Args:
            text: Text content to analyze
            content_type: Type of content being analyzed
            analysis_options: Analysis configuration options
            
        Returns:
            Dict containing complete text quality analysis
            
        Raises:
            QualityCheckError: If analysis fails
            ContentValidationError: If text content is invalid
        """
        start_time = datetime.now()
        
        try:
            if not text or not text.strip():
                raise ContentValidationError("Empty or whitespace-only text provided")
            
            text = text.strip()
            
            # Create quality profile
            profile = TextQualityProfile()
            profile.content_type = content_type or self._detect_content_type(text)
            profile.text_length = len(text)
            profile.reading_time_minutes = self._estimate_reading_time(text)
            
            # Perform comprehensive analysis
            await self._analyze_grammar_and_language(text, profile)
            await self._analyze_readability(text, profile)
            await self._analyze_content_structure(text, profile)
            await self._analyze_sentiment_and_emotion(text, profile)
            await self._analyze_writing_style(text, profile)
            await self._analyze_seo_factors(text, profile)
            
            # Calculate quality scores
            self._calculate_quality_scores(profile)
            
            # Generate recommendations
            self._generate_text_recommendations(profile)
            
            # Create metrics
            metrics = TextQualityMetrics(profile=profile)
            await self._analyze_platform_compliance(profile, metrics)
            await self._analyze_content_performance(text, profile, metrics)
            
            end_time = datetime.now()
            metrics.processing_time = (end_time - start_time).total_seconds()
            metrics.confidence = self._calculate_confidence(profile)
            
            # Prepare result
            result = {
                'technical_score': profile.technical_score,
                'confidence': metrics.confidence,
                'content_details': {
                    'content_type': profile.content_type.value,
                    'word_count': profile.structure.word_count,
                    'sentence_count': profile.structure.sentence_count,
                    'paragraph_count': profile.structure.paragraph_count,
                    'reading_time_minutes': profile.reading_time_minutes,
                    'character_count': profile.structure.character_count,
                    'average_words_per_sentence': profile.structure.average_words_per_sentence
                },
                'grammar_analysis': {
                    'grammar_score': profile.grammar.grammar_score,
                    'total_errors': profile.grammar.total_errors,
                    'grammar_errors': profile.grammar.grammar_errors,
                    'spelling_errors': profile.grammar.spelling_errors,
                    'style_errors': profile.grammar.style_errors,
                    'detected_language': profile.grammar.detected_language,
                    'language_confidence': profile.grammar.language_confidence
                },
                'readability_analysis': {
                    'readability_score': profile.readability.readability_score,
                    'readability_level': profile.readability.readability_level.value,
                    'flesch_score': profile.readability.flesch_score,
                    'flesch_kincaid_grade': profile.readability.flesch_kincaid_grade,
                    'gunning_fog_index': profile.readability.gunning_fog_index,
                    'target_audience': profile.readability.target_audience,
                    'average_sentence_length': profile.readability.average_sentence_length,
                    'complex_words_percentage': profile.readability.complex_words_percentage
                },
                'sentiment_analysis': {
                    'sentiment_label': profile.sentiment.sentiment_label,
                    'polarity': profile.sentiment.polarity,
                    'subjectivity': profile.sentiment.subjectivity,
                    'engagement_score': profile.sentiment.engagement_score,
                    'emotional_impact': profile.sentiment.emotional_impact
                },
                'style_analysis': {
                    'writing_tone': profile.style.writing_tone.value,
                    'formality_score': profile.style.formality_score,
                    'vocabulary_richness': profile.style.vocabulary_richness,
                    'advanced_vocabulary_percentage': profile.style.advanced_vocabulary_percentage,
                    'passive_voice_percentage': profile.style.passive_voice_percentage,
                    'sentence_variety_score': profile.style.sentence_variety_score,
                    'style_score': profile.style.style_score
                },
                'seo_analysis': {
                    'seo_score': profile.seo_score,
                    'title_quality': profile.title_quality,
                    'internal_links': profile.internal_links,
                    'external_links': profile.external_links,
                    'keyword_density': profile.structure.keyword_density,
                    'top_keywords': profile.structure.top_keywords[:10]
                },
                'platform_compliance': {
                    'social_media_ready': metrics.social_media_ready,
                    'blog_ready': metrics.blog_ready,
                    'email_ready': metrics.email_ready,
                    'seo_optimized': metrics.seo_optimized
                },
                'quality_scores': {
                    'overall_quality_score': profile.overall_quality_score,
                    'quality_level': profile.quality_level,
                    'content_score': profile.content_score,
                    'engagement_score': profile.engagement_score
                },
                'performance_indicators': {
                    'viral_potential': metrics.viral_potential,
                    'conversion_potential': metrics.conversion_potential,
                    'shareability_score': metrics.shareability_score,
                    'originality_score': metrics.originality_score
                },
                'recommendations': profile.recommendations,
                'improvement_suggestions': profile.improvement_suggestions
            }
            
            # Log metrics
            self.metrics_collector.track_business_metric(
                metric_name="text_quality_analysis_completed",
                value=1,
                metadata={
                    'quality_score': profile.overall_quality_score,
                    'content_type': profile.content_type.value,
                    'word_count': profile.structure.word_count,
                    'processing_time': metrics.processing_time
                }
            )
            
            logger.info(f"Text quality analysis completed: {profile.overall_quality_score:.2f}/100")
            return result
            
        except Exception as e:
            logger.error(f"Text quality analysis failed: {str(e)}")
            self.metrics_collector.capture_errors("text_quality_analysis_error", str(e))
            raise QualityCheckError(f"Text quality analysis failed: {str(e)}") from e
    
    async def connect(self) -> bool:
        """Connect to text processing services."""
        return True
    
    async def disconnect(self) -> bool:
        """
Disconnect from text processing services."""
        return True
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
Process text quality assessment."""
        return await self.analyze_text_quality(data.get('text', ''), 
                                              data.get('profile', TextQualityProfile()))
    
    def _detect_content_type(self, text: str) -> TextType:
        """
Detect content type based on text characteristics"""
        try:
            text_lower = text.lower()
            
            # Check for email patterns
            if re.search(r'subject:|dear\s+\w+|sincerely|best\s+regards', text_lower):
                return TextType.EMAIL
            
            # Check for social media patterns
            if len(text) <= 280 or '#' in text or '@' in text:
                return TextType.SOCIAL_MEDIA
            
            # Check for marketing copy patterns
            marketing_keywords = ['buy now', 'limited time', 'special offer', 'act now', 'call to action']
            if any(keyword in text_lower for keyword in marketing_keywords):
                return TextType.MARKETING_COPY
            
            # Check for blog post patterns
            if len(text) > 500 and (text.count('\n\n') > 2 or text.count('#') > 0):
                return TextType.BLOG_POST
            
            # Check for technical document patterns
            technical_keywords = ['algorithm', 'implementation', 'configuration', 'specification']
            if any(keyword in text_lower for keyword in technical_keywords):
                return TextType.TECHNICAL_DOCUMENT
            
            # Default to article
            return TextType.ARTICLE
            
        except Exception:
            return TextType.ARTICLE
    
    def _estimate_reading_time(self, text: str) -> float:
        """
Estimate reading time in minutes"""
        try:
            words = len(text.split())
            # Average reading speed: 225 words per minute
            return words / 225.0
        except Exception:
            return 0.0
    
    async def _analyze_grammar_and_language(self, text: str, profile: TextQualityProfile):
        """
Analyze grammar and language quality"""
        try:
            # Language detection using TextBlob
            blob = TextBlob(text)
            try:
                profile.grammar.detected_language = blob.detect_language()
                profile.grammar.language_confidence = 0.8  # Simplified confidence
            except Exception:
                profile.grammar.detected_language = "en"
                profile.grammar.language_confidence = 0.5
            
            # Grammar checking with LanguageTool
            if self.grammar_tool:
                try:
                    matches = self.grammar_tool.check(text)
                    profile.grammar.total_errors = len(matches)
                    
                    # Categorize errors
                    for match in matches:
                        error_detail = {
                            'message': match.message,
                            'offset': match.offset,
                            'length': match.errorLength,
                            'category': match.category,
                            'suggestions': match.replacements[:3]  # Top 3 suggestions
                        }
                        profile.grammar.error_details.append(error_detail)
                        
                        # Categorize by type
                        category = match.category.lower()
                        if 'grammar' in category:
                            profile.grammar.grammar_errors += 1
                        elif 'spell' in category:
                            profile.grammar.spelling_errors += 1
                        elif 'style' in category:
                            profile.grammar.style_errors += 1
                        elif 'punct' in category:
                            profile.grammar.punctuation_errors += 1
                
                except Exception as e:
                    logger.warning(f"Grammar checking failed: {str(e)}")
            
            # Calculate grammar score
            word_count = len(text.split())
            if word_count > 0:
                error_rate = profile.grammar.total_errors / word_count
                profile.grammar.grammar_score = max(0, 100 - (error_rate * 100))
            else:
                profile.grammar.grammar_score = 100
            
        except Exception as e:
            logger.warning(f"Grammar analysis failed: {str(e)}")
            profile.grammar.grammar_score = 70  # Default score
    
    async def _analyze_readability(self, text: str, profile: TextQualityProfile):
        """Analyze text readability"""
        try:
            # Calculate readability metrics
            profile.readability.flesch_score = flesch_reading_ease(text)
            profile.readability.flesch_kincaid_grade = flesch_kincaid_grade(text)
            profile.readability.gunning_fog_index = gunning_fog(text)
            profile.readability.automated_readability_index = automated_readability_index(text)
            
            # Classify readability level based on Flesch score
            flesch = profile.readability.flesch_score
            if flesch >= 90:
                profile.readability.readability_level = ReadabilityLevel.VERY_EASY
                profile.readability.target_audience = "elementary_school"
            elif flesch >= 80:
                profile.readability.readability_level = ReadabilityLevel.EASY
                profile.readability.target_audience = "middle_school"
            elif flesch >= 70:
                profile.readability.readability_level = ReadabilityLevel.FAIRLY_EASY
                profile.readability.target_audience = "high_school"
            elif flesch >= 60:
                profile.readability.readability_level = ReadabilityLevel.STANDARD
                profile.readability.target_audience = "general_adult"
            elif flesch >= 50:
                profile.readability.readability_level = ReadabilityLevel.FAIRLY_DIFFICULT
                profile.readability.target_audience = "college_level"
            elif flesch >= 30:
                profile.readability.readability_level = ReadabilityLevel.DIFFICULT
                profile.readability.target_audience = "university_graduate"
            else:
                profile.readability.readability_level = ReadabilityLevel.VERY_DIFFICULT
                profile.readability.target_audience = "academic_professional"
            
            # Calculate detailed metrics
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            words = text.split()
            
            if sentences:
                profile.readability.average_sentence_length = len(words) / len(sentences)
            
            # Syllable counting (simplified)
            syllable_count = 0
            for word in words:
                syllable_count += self._count_syllables(word)
            
            if words:
                profile.readability.average_syllables_per_word = syllable_count / len(words)
            
            # Complex words analysis
            complex_words = 0
            for word in words:
                if self._count_syllables(word) >= 3:
                    complex_words += 1
            
            if words:
                profile.readability.complex_words_percentage = (complex_words / len(words)) * 100
            
            # Overall readability score (normalized Flesch score)
            profile.readability.readability_score = max(0, min(100, profile.readability.flesch_score))
            
        except Exception as e:
            logger.warning(f"Readability analysis failed: {str(e)}")
            profile.readability.readability_score = 50
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified algorithm)"""
        try:
            word = word.lower().strip(string.punctuation)
            if not word:
                return 0
            
            # Remove silent 'e' at the end
            if word.endswith('e'):
                word = word[:-1]
            
            # Count vowel groups
            vowels = 'aeiouy'
            syllable_count = 0
            prev_was_vowel = False
            
            for char in word:
                if char in vowels:
                    if not prev_was_vowel:
                        syllable_count += 1
                    prev_was_vowel = True
                else:
                    prev_was_vowel = False
            
            # Every word has at least one syllable
            return max(1, syllable_count)
            
        except Exception:
            return 1
    
    async def _analyze_content_structure(self, text: str, profile: TextQualityProfile):
        """
Analyze content structure and organization"""
        try:
            structure = profile.structure
            
            # Basic counts
            structure.character_count = len(text)
            structure.character_count_no_spaces = len(text.replace(' ', ''))
            
            # Word and sentence analysis
            words = text.split()
            structure.word_count = len(words)
            
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            structure.sentence_count = len(sentences)
            
            # Paragraph analysis
            paragraphs = text.split('\n\n')
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            structure.paragraph_count = len(paragraphs)
            
            # Average calculations
            if structure.sentence_count > 0:
                structure.average_words_per_sentence = structure.word_count / structure.sentence_count
            
            if structure.paragraph_count > 0:
                structure.average_sentences_per_paragraph = structure.sentence_count / structure.paragraph_count
            
            # Headers and formatting analysis
            structure.headers_count = len(re.findall(r'^#{1,6}\s+', text, re.MULTILINE))
            structure.subheaders_count = len(re.findall(r'^#{2,6}\s+', text, re.MULTILINE))
            structure.lists_count = len(re.findall(r'^\s*[-*+]\s+|^\s*\d+\.\s+', text, re.MULTILINE))
            
            # Keyword analysis
            await self._analyze_keywords(text, structure)
            
            # Structure quality score
            structure_factors = []
            
            # Sentence length variety
            if sentences:
                sentence_lengths = [len(s.split()) for s in sentences]
                length_variance = np.var(sentence_lengths) if len(sentence_lengths) > 1 else 0
                variety_score = min(100, length_variance * 5)  # Normalize
                structure_factors.append(variety_score)
            
            # Paragraph structure
            if structure.paragraph_count > 1:
                if 3 <= structure.average_sentences_per_paragraph <= 6:
                    structure_factors.append(90)  # Good paragraph length
                else:
                    structure_factors.append(60)
            else:
                structure_factors.append(40)  # Single paragraph
            
            # Header usage
            if structure.headers_count > 0:
                structure_factors.append(80)
            else:
                structure_factors.append(50)
            
            structure.structure_score = np.mean(structure_factors) if structure_factors else 50
            
        except Exception as e:
            logger.warning(f"Content structure analysis failed: {str(e)}")
            profile.structure.structure_score = 50
    
    async def _analyze_keywords(self, text: str, structure: ContentStructure):
        """Analyze keywords and their density"""
        try:
            # Clean and tokenize text
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            
            # Remove common stop words (simplified list)
            stop_words = {
                'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
                'after', 'above', 'below', 'between', 'among', 'under', 'over',
                'this', 'that', 'these', 'those', 'they', 'them', 'their', 'there',
                'where', 'when', 'why', 'how', 'what', 'which', 'who', 'whom',
                'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must',
                'have', 'has', 'had', 'been', 'being', 'are', 'was', 'were',
                'very', 'too', 'quite', 'rather', 'such', 'more', 'most', 'much',
                'many', 'some', 'any', 'all', 'each', 'every', 'both', 'either',
                'neither', 'other', 'another', 'same', 'different'
            }
            
            filtered_words = [word for word in words if word not in stop_words]
            
            # Count word frequencies
            word_counts = Counter(filtered_words)
            total_words = len(filtered_words)
            
            # Calculate keyword density
            if total_words > 0:
                for word, count in word_counts.items():
                    density = (count / total_words) * 100
                    structure.keyword_density[word] = density
            
            # Get top keywords
            structure.top_keywords = word_counts.most_common(20)
            
        except Exception as e:
            logger.warning(f"Keyword analysis failed: {str(e)}")
    
    async def _analyze_sentiment_and_emotion(self, text: str, profile: TextQualityProfile):
        """Analyze sentiment and emotional content"""
        try:
            blob = TextBlob(text)
            
            # Basic sentiment analysis
            profile.sentiment.polarity = blob.sentiment.polarity
            profile.sentiment.subjectivity = blob.sentiment.subjectivity
            
            # Classify sentiment
            if profile.sentiment.polarity > 0.1:
                profile.sentiment.sentiment_label = "positive"
            elif profile.sentiment.polarity < -0.1:
                profile.sentiment.sentiment_label = "negative"
            else:
                profile.sentiment.sentiment_label = "neutral"
            
            # Emotional impact based on polarity strength and subjectivity
            polarity_strength = abs(profile.sentiment.polarity)
            profile.sentiment.emotional_impact = (polarity_strength + profile.sentiment.subjectivity) * 50
            
            # Engagement score based on emotional content
            engagement_factors = []
            
            # Emotional words analysis
            emotional_words = {
                'positive': ['amazing', 'fantastic', 'incredible', 'wonderful', 'excellent', 'brilliant'],
                'negative': ['terrible', 'awful', 'horrible', 'disgusting', 'disappointing'],
                'exciting': ['exciting', 'thrilling', 'adventure', 'surprising', 'shocking'],
                'urgent': ['urgent', 'immediate', 'quickly', 'hurry', 'deadline', 'limited']
            }
            
            text_lower = text.lower()
            emotion_score = 0
            
            for category, words in emotional_words.items():
                for word in words:
                    if word in text_lower:
                        emotion_score += 10
            
            engagement_factors.append(min(100, emotion_score))
            engagement_factors.append(profile.sentiment.emotional_impact)
            
            profile.sentiment.engagement_score = np.mean(engagement_factors)
            
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {str(e)}")
            profile.sentiment.engagement_score = 50
    
    async def _analyze_writing_style(self, text: str, profile: TextQualityProfile):
        """Analyze writing style and tone"""
        try:
            style = profile.style
            words = text.split()
            
            # Vocabulary analysis
            unique_words = set(word.lower().strip(string.punctuation) for word in words)
            style.unique_words = len(unique_words)
            
            if words:
                style.vocabulary_richness = len(unique_words) / len(words)
            
            # Advanced vocabulary analysis
            advanced_count = 0
            for word in unique_words:
                if word in self.advanced_vocabulary:
                    advanced_count += 1
            
            if unique_words:
                style.advanced_vocabulary_percentage = (advanced_count / len(unique_words)) * 100
            
            # Passive voice detection (simplified)
            passive_patterns = [
                r'\b(was|were|is|are|been|being)\s+\w+ed\b',
                r'\b(was|were|is|are|been|being)\s+\w+en\b'
            ]
            
            passive_count = 0
            for pattern in passive_patterns:
                passive_count += len(re.findall(pattern, text, re.IGNORECASE))
            
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if sentences:
                style.passive_voice_percentage = (passive_count / len(sentences)) * 100
            
            # Sentence variety analysis
            if sentences:
                sentence_lengths = [len(s.split()) for s in sentences]
                if len(sentence_lengths) > 1:
                    length_variance = np.var(sentence_lengths)
                    style.sentence_variety_score = min(100, length_variance * 5)
                else:
                    style.sentence_variety_score = 30
            
            # Tone detection
            style.writing_tone = self._detect_writing_tone(text)
            
            # Formality score
            style.formality_score = self._calculate_formality_score(text, style)
            
            # Overall style score
            style_factors = [
                style.vocabulary_richness * 100,
                min(100, style.advanced_vocabulary_percentage * 2),
                style.sentence_variety_score,
                max(0, 100 - style.passive_voice_percentage * 2)  # Lower passive voice is better
            ]
            
            style.style_score = np.mean(style_factors)
            
        except Exception as e:
            logger.warning(f"Style analysis failed: {str(e)}")
            profile.style.style_score = 50
    
    def _detect_writing_tone(self, text: str) -> WritingTone:
        """Detect the writing tone of the text"""
        try:
            text_lower = text.lower()
            
            # Tone indicators
            professional_indicators = ['furthermore', 'however', 'therefore', 'consequently', 'moreover']
            casual_indicators = ['hey', 'yeah', 'cool', 'awesome', 'gonna', 'wanna']
            formal_indicators = ['pursuant', 'hereby', 'wherein', 'aforementioned', 'notwithstanding']
            friendly_indicators = ['thanks', 'please', 'welcome', 'appreciate', 'glad']
            persuasive_indicators = ['should', 'must', 'need to', 'have to', 'important']
            
            tone_scores = {
                WritingTone.PROFESSIONAL: sum(1 for ind in professional_indicators if ind in text_lower),
                WritingTone.CASUAL: sum(1 for ind in casual_indicators if ind in text_lower),
                WritingTone.FORMAL: sum(1 for ind in formal_indicators if ind in text_lower),
                WritingTone.FRIENDLY: sum(1 for ind in friendly_indicators if ind in text_lower),
                WritingTone.PERSUASIVE: sum(1 for ind in persuasive_indicators if ind in text_lower)
            }
            
            # Default to informative if no clear indicators
            if max(tone_scores.values()) == 0:
                return WritingTone.INFORMATIVE
            
            return max(tone_scores, key=tone_scores.get)
            
        except Exception:
            return WritingTone.INFORMATIVE
    
    def _calculate_formality_score(self, text: str, style: StyleAnalysis) -> float:
        """
Calculate formality score"""
        try:
            formality_factors = []
            
            # Advanced vocabulary increases formality
            formality_factors.append(style.advanced_vocabulary_percentage)
            
            # Passive voice increases formality
            formality_factors.append(style.passive_voice_percentage)
            
            # Sentence length affects formality
            sentences = re.split(r'[.!?]+', text)
            avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
            
            if avg_sentence_length > 20:
                formality_factors.append(80)  # Long sentences = more formal
            elif avg_sentence_length > 15:
                formality_factors.append(70)
            else:
                formality_factors.append(50)
            
            # Contractions decrease formality
            contractions = len(re.findall(r"\w+'\w+", text))
            words = len(text.split())
            if words > 0:
                contraction_rate = (contractions / words) * 100
                formality_factors.append(max(0, 100 - contraction_rate * 5))
            
            return np.mean(formality_factors)
            
        except Exception:
            return 50.0
    
    async def _analyze_seo_factors(self, text: str, profile: TextQualityProfile):
        """Analyze SEO-related factors"""
        try:
            # Basic SEO score calculation
            seo_factors = []
            
            # Content length for SEO
            word_count = profile.structure.word_count
            if 300 <= word_count <= 2000:
                seo_factors.append(90)  # Optimal length
            elif 200 <= word_count <= 3000:
                seo_factors.append(75)  # Acceptable length
            else:
                seo_factors.append(50)  # Suboptimal length
            
            # Keyword density (check for over-optimization)
            if profile.structure.keyword_density:
                max_density = max(profile.structure.keyword_density.values())
                if 1 <= max_density <= 3:
                    seo_factors.append(90)  # Good keyword density
                elif max_density <= 5:
                    seo_factors.append(70)  # Acceptable
                else:
                    seo_factors.append(40)  # Over-optimized
            else:
                seo_factors.append(60)  # No clear keywords
            
            # Headers for structure
            if profile.structure.headers_count > 0:
                seo_factors.append(80)
            else:
                seo_factors.append(50)
            
            # Links analysis
            internal_links = len(re.findall(r'href=["\'](?!http)', text))
            external_links = len(re.findall(r'href=["\']https?://', text))
            
            profile.internal_links = internal_links
            profile.external_links = external_links
            
            if internal_links > 0:
                seo_factors.append(75)
            else:
                seo_factors.append(60)
            
            profile.seo_score = np.mean(seo_factors)
            
            # Title quality (if text starts with header)
            first_line = text.split('\n')[0].strip()
            if first_line.startswith('#'):
                title = first_line.lstrip('#').strip()
                if 30 <= len(title) <= 60:
                    profile.title_quality = 90
                elif 20 <= len(title) <= 70:
                    profile.title_quality = 75
                else:
                    profile.title_quality = 60
            else:
                profile.title_quality = 50
            
        except Exception as e:
            logger.warning(f"SEO analysis failed: {str(e)}")
            profile.seo_score = 50
    
    def _calculate_quality_scores(self, profile: TextQualityProfile):
        """Calculate comprehensive quality scores"""
        try:
            # Technical score
            tech_score = (
                profile.grammar.grammar_score * 0.4 +
                profile.readability.readability_score * 0.3 +
                profile.structure.structure_score * 0.3
            )
            profile.technical_score = tech_score
            
            # Content score
            content_score = (
                profile.style.style_score * 0.4 +
                profile.sentiment.engagement_score * 0.3 +
                profile.seo_score * 0.3
            )
            profile.content_score = content_score
            
            # Engagement score
            engagement_score = (
                profile.sentiment.engagement_score * 0.5 +
                profile.sentiment.emotional_impact * 0.3 +
                profile.style.vocabulary_richness * 100 * 0.2
            )
            profile.engagement_score = engagement_score
            
            # Overall quality score
            profile.overall_quality_score = (
                profile.technical_score * 0.4 +
                profile.content_score * 0.4 +
                profile.engagement_score * 0.2
            )
            
            # Quality level classification
            if profile.overall_quality_score >= 90:
                profile.quality_level = "professional"
            elif profile.overall_quality_score >= 80:
                profile.quality_level = "excellent"
            elif profile.overall_quality_score >= 70:
                profile.quality_level = "good"
            elif profile.overall_quality_score >= 60:
                profile.quality_level = "acceptable"
            else:
                profile.quality_level = "needs_improvement"
            
        except Exception as e:
            logger.warning(f"Quality score calculation failed: {str(e)}")
            profile.overall_quality_score = 50.0
            profile.quality_level = "needs_improvement"
    
    def _generate_text_recommendations(self, profile: TextQualityProfile):
        """Generate text-specific recommendations"""
        recommendations = []
        
        # Grammar recommendations
        if profile.grammar.grammar_score < 80:
            recommendations.append("Improve grammar and reduce errors for better readability")
            if profile.grammar.spelling_errors > 0:
                recommendations.append("Check spelling and correct errors")
            if profile.grammar.punctuation_errors > 0:
                recommendations.append("Review punctuation usage")
        
        # Readability recommendations
        if profile.readability.readability_score < 60:
            recommendations.append("Improve readability by using simpler language and shorter sentences")
        if profile.readability.average_sentence_length > 25:
            recommendations.append("Break down long sentences for better readability")
        if profile.readability.complex_words_percentage > 20:
            recommendations.append("Reduce complex words to improve accessibility")
        
        # Structure recommendations
        if profile.structure.paragraph_count <= 1 and profile.structure.word_count > 200:
            recommendations.append("Break content into multiple paragraphs for better structure")
        if profile.structure.headers_count == 0 and profile.structure.word_count > 300:
            recommendations.append("Add headers and subheaders to improve organization")
        
        # Style recommendations
        if profile.style.vocabulary_richness < 0.4:
            recommendations.append("Expand vocabulary to avoid repetition")
        if profile.style.passive_voice_percentage > 20:
            recommendations.append("Reduce passive voice usage for more engaging writing")
        if profile.style.sentence_variety_score < 50:
            recommendations.append("Vary sentence length and structure for better flow")
        
        # SEO recommendations
        if profile.seo_score < 70:
            recommendations.append("Optimize content for search engines with better keyword usage")
        if profile.internal_links == 0:
            recommendations.append("Add internal links to improve SEO and user experience")
        
        # Engagement recommendations
        if profile.sentiment.engagement_score < 60:
            recommendations.append("Increase emotional appeal and engagement factors")
        
        profile.recommendations = recommendations
        
        # Improvement suggestions
        improvements = []
        
        if profile.overall_quality_score < 80:
            improvements.extend([
                "Consider professional editing or proofreading",
                "Research target audience preferences and adjust tone accordingly",
                "Use tools like Grammarly or Hemingway Editor for additional insights"
            ])
        
        if profile.content_score < 70:
            improvements.extend([
                "Enhance content with examples, case studies, or personal anecdotes",
                "Improve call-to-action placement and effectiveness",
                "Consider multimedia elements to support text content"
            ])
        
        profile.improvement_suggestions = improvements
    
    async def _analyze_platform_compliance(
        self,
        profile: TextQualityProfile,
        metrics: TextQualityMetrics
    ):
        """Analyze compliance with platform requirements"""
        try:
            word_count = profile.structure.word_count
            
            # Social media compliance
            social_ready = (
                (word_count <= 280 and profile.style.writing_tone in [WritingTone.CASUAL, WritingTone.FRIENDLY]) or
                (word_count <= 2200 and profile.engagement_score >= 60)
            )
            metrics.social_media_ready = social_ready
            
            # Blog compliance
            blog_ready = (
                300 <= word_count <= 5000 and
                profile.readability.readability_level in [ReadabilityLevel.EASY, ReadabilityLevel.FAIRLY_EASY, ReadabilityLevel.STANDARD] and
                profile.structure.headers_count > 0 and
                profile.overall_quality_score >= 70
            )
            metrics.blog_ready = blog_ready
            
            # Email compliance
            email_ready = (
                word_count <= 500 and
                profile.style.writing_tone in [WritingTone.PROFESSIONAL, WritingTone.FRIENDLY] and
                profile.grammar.grammar_score >= 85
            )
            metrics.email_ready = email_ready
            
            # SEO optimization
            metrics.seo_optimized = (
                profile.seo_score >= 75 and
                word_count >= 300 and
                profile.structure.headers_count > 0
            )
            
        except Exception as e:
            logger.warning(f"Platform compliance analysis failed: {str(e)}")
    
    async def _analyze_content_performance(
        self,
        text: str,
        profile: TextQualityProfile,
        metrics: TextQualityMetrics
    ):
        """Analyze content performance indicators"""
        try:
            # Viral potential
            viral_factors = []
            
            # Emotional content increases viral potential
            viral_factors.append(profile.sentiment.emotional_impact)
            
            # Engagement elements
            questions = len(re.findall(r'\?', text))
            if questions > 0:
                viral_factors.append(70)
            else:
                viral_factors.append(30)
            
            # Surprising or shocking content
            surprise_words = ['surprising', 'shocking', 'incredible', 'unbelievable', 'amazing']
            surprise_score = sum(10 for word in surprise_words if word.lower() in text.lower())
            viral_factors.append(min(100, surprise_score))
            
            metrics.viral_potential = np.mean(viral_factors)
            
            # Conversion potential
            conversion_factors = []
            
            # Call-to-action presence
            cta_patterns = ['click here', 'learn more', 'sign up', 'buy now', 'get started', 'download']
            cta_score = sum(20 for pattern in cta_patterns if pattern.lower() in text.lower())
            conversion_factors.append(min(100, cta_score))
            
            # Persuasive language
            if profile.style.writing_tone == WritingTone.PERSUASIVE:
                conversion_factors.append(80)
            else:
                conversion_factors.append(40)
            
            # Trust signals
            trust_words = ['guarantee', 'proven', 'tested', 'certified', 'secure']
            trust_score = sum(15 for word in trust_words if word.lower() in text.lower())
            conversion_factors.append(min(100, trust_score))
            
            metrics.conversion_potential = np.mean(conversion_factors)
            
            # Shareability score
            share_factors = [
                metrics.viral_potential,
                profile.sentiment.engagement_score,
                profile.content_score
            ]
            
            metrics.shareability_score = np.mean(share_factors)
            
            # Originality score (simplified)
            # Check for unique phrases and original thinking
            unique_phrases = len(set(re.findall(r'\b\w+\s+\w+\s+\w+\b', text.lower())))
            total_phrases = len(re.findall(r'\b\w+\s+\w+\s+\w+\b', text.lower()))
            
            if total_phrases > 0:
                phrase_uniqueness = (unique_phrases / total_phrases) * 100
                metrics.originality_score = min(100, phrase_uniqueness + profile.style.vocabulary_richness * 30)
            else:
                metrics.originality_score = 50
            
        except Exception as e:
            logger.warning(f"Content performance analysis failed: {str(e)}")
            metrics.viral_potential = 30
            metrics.conversion_potential = 40
            metrics.shareability_score = 30
            metrics.originality_score = 50
    
    def _calculate_confidence(self, profile: TextQualityProfile) -> float:
        """Calculate analysis confidence score"""
        confidence = 0.9  # Base confidence
        
        # Adjust based on text length
        word_count = profile.structure.word_count
        if word_count >= 100:
            confidence += 0.05
        elif word_count < 50:
            confidence -= 0.15
        
        # Adjust based on language detection confidence
        confidence += (profile.grammar.language_confidence - 0.5) * 0.1
        
        # Adjust based on grammar tool availability
        if self.grammar_tool is None:
            confidence -= 0.1
        
        return max(0.5, min(1.0, confidence))


# Global text quality analyzer instance
# text_quality_analyzer = TextQualityAnalyzer()  # Commented out for testing


async def analyze_text_quality(text: str, content_type: Optional[TextType] = None) -> Dict[str, Any]:
    """
    Convenient function for text quality analysis
    
    Args:
        text: Text content to analyze
        content_type: Type of content being analyzed
        
    Returns:
        Dict containing text quality analysis results
    """
    try:
        result = await text_quality_analyzer.analyze_quality(text, content_type)
        return result
    except Exception as e:
        logger.error(f"Text quality analysis error: {str(e)}")
        return {
            'error': str(e),
            'success': False
        }
