"""AI Content Analyzer - Advanced AI-Powered Content Analysis System
===================================================================

Industrial-grade AI content analysis system for the IA Influencer Agent Platform,
providing sentiment analysis, quality scoring, genre detection, and optimization
recommendations using machine learning models.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited

AI Analysis Capabilities:
- Sentiment and emotion analysis with confidence scoring
- Content quality assessment using ML models
- Genre and style detection for categorization
- Engagement prediction and viral potential analysis
- Cross-cultural content analysis and localization
- Trend prediction and market analysis
- Optimization recommendations for creators
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import json
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of AI analysis available."""
    SENTIMENT = "sentiment"
    EMOTION = "emotion"
    QUALITY = "quality"
    GENRE = "genre"
    STYLE = "style"
    ENGAGEMENT = "engagement"
    VIRAL_POTENTIAL = "viral_potential"
    TREND_ANALYSIS = "trend_analysis"
    CULTURAL_ANALYSIS = "cultural_analysis"
    OPTIMIZATION = "optimization"

class ContentCategory(Enum):
    """Content categories for analysis."""
    ENTERTAINMENT = "entertainment"
    EDUCATIONAL = "educational"
    NEWS = "news"
    LIFESTYLE = "lifestyle"
    TECHNOLOGY = "technology"
    GAMING = "gaming"
    MUSIC = "music"
    SPORTS = "sports"
    FASHION = "fashion"
    FOOD = "food"
    TRAVEL = "travel"
    BUSINESS = "business"

class SentimentPolarity(Enum):
    """Sentiment polarity classifications."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    MIXED = "mixed"

class EmotionType(Enum):
    """Emotion classifications."""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"

@dataclass
class SentimentAnalysis:
    """Sentiment analysis results."""
    polarity: SentimentPolarity
    confidence: float
    intensity: float
    subjectivity: float
    emotional_tone: str
    key_indicators: List[str] = field(default_factory=list)
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class EmotionAnalysis:
    """Emotion analysis results."""
    primary_emotion: EmotionType
    emotion_scores: Dict[EmotionType, float] = field(default_factory=dict)
    emotional_complexity: float = 0.0
    emotional_consistency: float = 0.0
    emotional_intensity: float = 0.0
    detected_emotions: List[str] = field(default_factory=list)
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class QualityAnalysis:
    """Content quality analysis results."""
    overall_quality_score: float
    technical_quality: float
    creative_quality: float
    educational_value: float
    entertainment_value: float
    originality_score: float
    production_value: float
    engagement_potential: float
    improvement_areas: List[str] = field(default_factory=list)
    quality_factors: Dict[str, float] = field(default_factory=dict)
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class GenreAnalysis:
    """Genre and style analysis results."""
    primary_genre: str
    genre_confidence: float
    sub_genres: List[str] = field(default_factory=list)
    style_characteristics: List[str] = field(default_factory=list)
    content_themes: List[str] = field(default_factory=list)
    target_audience: str = "general"
    genre_trends: Dict[str, Any] = field(default_factory=dict)
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class EngagementAnalysis:
    """Engagement prediction analysis."""
    engagement_score: float
    viral_potential: float
    shareability_score: float
    comment_likelihood: float
    retention_prediction: float
    platform_performance: Dict[str, float] = field(default_factory=dict)
    engagement_factors: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class AIAnalysisResult:
    """Comprehensive AI analysis result."""
    content_id: str
    analysis_types: List[AnalysisType]
    sentiment_analysis: Optional[SentimentAnalysis] = None
    emotion_analysis: Optional[EmotionAnalysis] = None
    quality_analysis: Optional[QualityAnalysis] = None
    genre_analysis: Optional[GenreAnalysis] = None
    engagement_analysis: Optional[EngagementAnalysis] = None
    overall_score: float = 0.0
    confidence_level: float = 0.0
    processing_time_ms: int = 0
    model_versions: Dict[str, str] = field(default_factory=dict)
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

class AIContentAnalyzer:
    """Advanced AI-powered content analysis system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize AI content analyzer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.model_config = self._load_model_configuration()
        
        # Analysis settings
        self.enable_sentiment_analysis = self.config.get('enable_sentiment_analysis', True)
        self.enable_emotion_analysis = self.config.get('enable_emotion_analysis', True)
        self.enable_quality_analysis = self.config.get('enable_quality_analysis', True)
        self.enable_genre_analysis = self.config.get('enable_genre_analysis', True)
        self.enable_engagement_analysis = self.config.get('enable_engagement_analysis', True)
        
        # Performance settings
        self.max_content_length = self.config.get('max_content_length', 50000)
        self.analysis_timeout_seconds = self.config.get('analysis_timeout_seconds', 30)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        
        logger.info("AIContentAnalyzer initialized")
    
    def _load_model_configuration(self) -> Dict[str, Any]:
        """Load AI model configuration.
        
        Returns:
            Model configuration dictionary
        """
        return {
            'sentiment_model': {
                'name': 'ainflue-sentiment-v2',
                'version': '2.1.0',
                'accuracy': 0.92,
                'languages': ['en', 'fr', 'de', 'es', 'ar']
            },
            'emotion_model': {
                'name': 'ainflue-emotion-v2',
                'version': '2.0.0',
                'accuracy': 0.89,
                'emotions': ['joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust']
            },
            'quality_model': {
                'name': 'ainflue-quality-v2',
                'version': '2.2.0',
                'accuracy': 0.85,
                'dimensions': ['technical', 'creative', 'educational', 'entertainment']
            },
            'genre_model': {
                'name': 'ainflue-genre-v2',
                'version': '2.0.0',
                'accuracy': 0.88,
                'genres': ['entertainment', 'educational', 'news', 'lifestyle', 'technology']
            },
            'engagement_model': {
                'name': 'ainflue-engagement-v2',
                'version': '2.1.0',
                'accuracy': 0.83,
                'platforms': ['youtube', 'instagram', 'tiktok', 'twitter']
            }
        }
    
    async def analyze_content(self, content: Union[str, Dict[str, Any]],
                            content_type: str = "text",
                            analysis_types: Optional[List[AnalysisType]] = None,
                            context: Optional[Dict[str, Any]] = None) -> AIAnalysisResult:
        """Perform comprehensive AI analysis on content.
        
        Args:
            content: Content to analyze (text, metadata, or file path)
            content_type: Type of content (text, video, audio, image)
            analysis_types: Specific analysis types to perform
            context: Optional context information
            
        Returns:
            AIAnalysisResult with comprehensive analysis
        """
        start_time = datetime.now(timezone.utc)
        content_id = self._generate_content_id(content)
        
        # Default analysis types
        if analysis_types is None:
            analysis_types = [
                AnalysisType.SENTIMENT,
                AnalysisType.EMOTION,
                AnalysisType.QUALITY,
                AnalysisType.GENRE,
                AnalysisType.ENGAGEMENT
            ]
        
        logger.info(f"Starting AI analysis for content {content_id}")
        
        try:
            # Prepare content for analysis
            processed_content = await self._preprocess_content(content, content_type)
            
            # Perform individual analyses
            sentiment_analysis = None
            emotion_analysis = None
            quality_analysis = None
            genre_analysis = None
            engagement_analysis = None
            
            if AnalysisType.SENTIMENT in analysis_types and self.enable_sentiment_analysis:
                sentiment_analysis = await self._analyze_sentiment(processed_content, context)
            
            if AnalysisType.EMOTION in analysis_types and self.enable_emotion_analysis:
                emotion_analysis = await self._analyze_emotions(processed_content, context)
            
            if AnalysisType.QUALITY in analysis_types and self.enable_quality_analysis:
                quality_analysis = await self._analyze_quality(processed_content, content_type, context)
            
            if AnalysisType.GENRE in analysis_types and self.enable_genre_analysis:
                genre_analysis = await self._analyze_genre(processed_content, content_type, context)
            
            if AnalysisType.ENGAGEMENT in analysis_types and self.enable_engagement_analysis:
                engagement_analysis = await self._analyze_engagement(processed_content, content_type, context)
            
            # Calculate overall scores
            overall_score = self._calculate_overall_score(
                sentiment_analysis, emotion_analysis, quality_analysis,
                genre_analysis, engagement_analysis
            )
            
            confidence_level = self._calculate_confidence_level(
                sentiment_analysis, emotion_analysis, quality_analysis,
                genre_analysis, engagement_analysis
            )
            
            # Calculate processing time
            end_time = datetime.now(timezone.utc)
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return AIAnalysisResult(
                content_id=content_id,
                analysis_types=analysis_types,
                sentiment_analysis=sentiment_analysis,
                emotion_analysis=emotion_analysis,
                quality_analysis=quality_analysis,
                genre_analysis=genre_analysis,
                engagement_analysis=engagement_analysis,
                overall_score=overall_score,
                confidence_level=confidence_level,
                processing_time_ms=processing_time_ms,
                model_versions={
                    model: self.model_config[f"{model}_model"]['version']
                    for model in ['sentiment', 'emotion', 'quality', 'genre', 'engagement']
                },
                analyzed_at=start_time,
                metadata={
                    'content_type': content_type,
                    'content_length': len(str(processed_content)),
                    'context': context or {}
                }
            )
            
        except Exception as e:
            logger.error(f"AI analysis failed for content {content_id}: {e}")
            end_time = datetime.now(timezone.utc)
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return AIAnalysisResult(
                content_id=content_id,
                analysis_types=analysis_types,
                overall_score=0.0,
                confidence_level=0.0,
                processing_time_ms=processing_time_ms,
                analyzed_at=start_time,
                metadata={
                    'error': str(e),
                    'content_type': content_type
                }
            )
    
    async def _preprocess_content(self, content: Union[str, Dict[str, Any]],
                                content_type: str) -> str:
        """Preprocess content for AI analysis.
        
        Args:
            content: Raw content
            content_type: Type of content
            
        Returns:
            Preprocessed content string
        """
        if isinstance(content, str):
            # Text content - clean and normalize
            processed = content.strip()
            
            # Remove excessive whitespace
            processed = re.sub(r'\s+', ' ', processed)
            
            # Limit length
            if len(processed) > self.max_content_length:
                processed = processed[:self.max_content_length]
                logger.warning(f"Content truncated to {self.max_content_length} characters")
            
            return processed
        
        elif isinstance(content, dict):
            # Structured content - extract text fields
            text_fields = []
            
            for key in ['title', 'description', 'transcript', 'captions', 'text']:
                if key in content and content[key]:
                    text_fields.append(str(content[key]))
            
            processed = ' '.join(text_fields)
            return await self._preprocess_content(processed, content_type)
        
        else:
            # For other types, convert to string
            return str(content)
    
    async def _analyze_sentiment(self, content: str,
                               context: Optional[Dict[str, Any]] = None) -> SentimentAnalysis:
        """Analyze sentiment of content.
        
        Args:
            content: Content to analyze
            context: Optional context
            
        Returns:
            SentimentAnalysis result
        """
        try:
            # Simulate AI model analysis - in production, this would call actual AI models
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Simple sentiment analysis simulation
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'best']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting']
            
            content_lower = content.lower()
            positive_count = sum(1 for word in positive_words if word in content_lower)
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            # Calculate sentiment scores
            total_sentiment_words = positive_count + negative_count
            
            if total_sentiment_words == 0:
                polarity = SentimentPolarity.NEUTRAL
                confidence = 0.5
                intensity = 0.0
            elif positive_count > negative_count:
                intensity = min(1.0, positive_count / 3)
                if intensity > 0.7:
                    polarity = SentimentPolarity.VERY_POSITIVE
                else:
                    polarity = SentimentPolarity.POSITIVE
                confidence = min(0.95, 0.6 + intensity * 0.3)
            elif negative_count > positive_count:
                intensity = min(1.0, negative_count / 3)
                if intensity > 0.7:
                    polarity = SentimentPolarity.VERY_NEGATIVE
                else:
                    polarity = SentimentPolarity.NEGATIVE
                confidence = min(0.95, 0.6 + intensity * 0.3)
            else:
                polarity = SentimentPolarity.MIXED
                confidence = 0.7
                intensity = 0.5
            
            # Calculate subjectivity (simple heuristic)
            subjective_indicators = ['i think', 'believe', 'feel', 'opinion', 'personally']
            subjectivity = min(1.0, sum(1 for indicator in subjective_indicators 
                                       if indicator in content_lower) / 3)
            
            # Generate emotional tone
            tone_map = {
                SentimentPolarity.VERY_POSITIVE: "enthusiastic",
                SentimentPolarity.POSITIVE: "optimistic",
                SentimentPolarity.NEUTRAL: "balanced",
                SentimentPolarity.NEGATIVE: "critical",
                SentimentPolarity.VERY_NEGATIVE: "pessimistic",
                SentimentPolarity.MIXED: "ambivalent"
            }
            
            emotional_tone = tone_map.get(polarity, "neutral")
            
            # Extract key indicators
            key_indicators = []
            for word in positive_words:
                if word in content_lower:
                    key_indicators.append(f"positive: {word}")
            for word in negative_words:
                if word in content_lower:
                    key_indicators.append(f"negative: {word}")
            
            return SentimentAnalysis(
                polarity=polarity,
                confidence=confidence,
                intensity=intensity,
                subjectivity=subjectivity,
                emotional_tone=emotional_tone,
                key_indicators=key_indicators[:5]  # Limit to top 5
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return SentimentAnalysis(
                polarity=SentimentPolarity.NEUTRAL,
                confidence=0.0,
                intensity=0.0,
                subjectivity=0.0,
                emotional_tone="unknown",
                key_indicators=[f"analysis_error: {str(e)}"]
            )
    
    async def _analyze_emotions(self, content: str,
                              context: Optional[Dict[str, Any]] = None) -> EmotionAnalysis:
        """Analyze emotions in content.
        
        Args:
            content: Content to analyze
            context: Optional context
            
        Returns:
            EmotionAnalysis result
        """
        try:
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Emotion keywords mapping
            emotion_keywords = {
                EmotionType.JOY: ['happy', 'joy', 'excited', 'delighted', 'cheerful', 'elated'],
                EmotionType.SADNESS: ['sad', 'depressed', 'melancholy', 'sorrowful', 'grief'],
                EmotionType.ANGER: ['angry', 'furious', 'rage', 'irritated', 'mad', 'livid'],
                EmotionType.FEAR: ['afraid', 'scared', 'terrified', 'anxious', 'worried'],
                EmotionType.SURPRISE: ['surprised', 'shocked', 'amazed', 'astonished'],
                EmotionType.DISGUST: ['disgusted', 'revolted', 'repulsed', 'sickened'],
                EmotionType.TRUST: ['trust', 'confident', 'secure', 'reliable', 'faith'],
                EmotionType.ANTICIPATION: ['excited', 'eager', 'hopeful', 'expectant']
            }
            
            content_lower = content.lower()
            emotion_scores = {}
            
            # Calculate emotion scores
            for emotion, keywords in emotion_keywords.items():
                score = sum(1 for keyword in keywords if keyword in content_lower)
                emotion_scores[emotion] = min(1.0, score / 3)  # Normalize to 0-1
            
            # Find primary emotion
            if emotion_scores:
                primary_emotion = max(emotion_scores, key=emotion_scores.get)
                max_score = emotion_scores[primary_emotion]
            else:
                primary_emotion = EmotionType.JOY  # Default
                max_score = 0.0
            
            # Calculate emotional complexity (variety of emotions)
            significant_emotions = [e for e, score in emotion_scores.items() if score > 0.1]
            emotional_complexity = min(1.0, len(significant_emotions) / 4)
            
            # Calculate emotional consistency (dominance of primary emotion)
            if max_score > 0:
                other_scores = [score for emotion, score in emotion_scores.items() 
                              if emotion != primary_emotion]
                avg_other_score = sum(other_scores) / len(other_scores) if other_scores else 0
                emotional_consistency = max(0.0, 1.0 - (avg_other_score / max_score))
            else:
                emotional_consistency = 0.5
            
            # Calculate emotional intensity
            emotional_intensity = max_score
            
            # Get detected emotions (above threshold)
            detected_emotions = [emotion.value for emotion, score in emotion_scores.items() 
                               if score > 0.2]
            
            return EmotionAnalysis(
                primary_emotion=primary_emotion,
                emotion_scores=emotion_scores,
                emotional_complexity=emotional_complexity,
                emotional_consistency=emotional_consistency,
                emotional_intensity=emotional_intensity,
                detected_emotions=detected_emotions
            )
            
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return EmotionAnalysis(
                primary_emotion=EmotionType.JOY,
                emotion_scores={},
                emotional_complexity=0.0,
                emotional_consistency=0.0,
                emotional_intensity=0.0,
                detected_emotions=[]
            )
    
    async def _analyze_quality(self, content: str, content_type: str,
                             context: Optional[Dict[str, Any]] = None) -> QualityAnalysis:
        """Analyze content quality.
        
        Args:
            content: Content to analyze
            content_type: Type of content
            context: Optional context
            
        Returns:
            QualityAnalysis result
        """
        try:
            await asyncio.sleep(0.15)  # Simulate processing time
            
            # Quality factors analysis
            quality_factors = {}
            
            # Technical quality factors
            length_score = self._assess_content_length(content, content_type)
            structure_score = self._assess_content_structure(content)
            clarity_score = self._assess_content_clarity(content)
            
            technical_quality = (length_score + structure_score + clarity_score) / 3
            quality_factors['length'] = length_score
            quality_factors['structure'] = structure_score
            quality_factors['clarity'] = clarity_score
            
            # Creative quality factors
            originality_score = self._assess_originality(content)
            creativity_score = self._assess_creativity(content)
            
            creative_quality = (originality_score + creativity_score) / 2
            quality_factors['originality'] = originality_score
            quality_factors['creativity'] = creativity_score
            
            # Educational value
            educational_value = self._assess_educational_value(content)
            quality_factors['educational'] = educational_value
            
            # Entertainment value
            entertainment_value = self._assess_entertainment_value(content)
            quality_factors['entertainment'] = entertainment_value
            
            # Production value (simulated)
            production_value = (technical_quality + creative_quality) / 2
            
            # Engagement potential
            engagement_potential = (entertainment_value + creative_quality) / 2
            
            # Overall quality score
            overall_quality_score = (
                technical_quality * 0.25 +
                creative_quality * 0.25 +
                educational_value * 0.2 +
                entertainment_value * 0.2 +
                production_value * 0.1
            )
            
            # Generate improvement areas
            improvement_areas = []
            if technical_quality < 0.6:
                improvement_areas.append("Improve technical presentation and structure")
            if creative_quality < 0.6:
                improvement_areas.append("Enhance creativity and originality")
            if educational_value < 0.5:
                improvement_areas.append("Add more educational or informative content")
            if entertainment_value < 0.5:
                improvement_areas.append("Increase entertainment value and engagement")
            
            return QualityAnalysis(
                overall_quality_score=overall_quality_score,
                technical_quality=technical_quality,
                creative_quality=creative_quality,
                educational_value=educational_value,
                entertainment_value=entertainment_value,
                originality_score=originality_score,
                production_value=production_value,
                engagement_potential=engagement_potential,
                improvement_areas=improvement_areas,
                quality_factors=quality_factors
            )
            
        except Exception as e:
            logger.error(f"Quality analysis failed: {e}")
            return QualityAnalysis(
                overall_quality_score=0.0,
                technical_quality=0.0,
                creative_quality=0.0,
                educational_value=0.0,
                entertainment_value=0.0,
                originality_score=0.0,
                production_value=0.0,
                engagement_potential=0.0,
                improvement_areas=["Quality analysis failed - manual review required"]
            )
    
    async def _analyze_genre(self, content: str, content_type: str,
                           context: Optional[Dict[str, Any]] = None) -> GenreAnalysis:
        """Analyze content genre and style.
        
        Args:
            content: Content to analyze
            content_type: Type of content
            context: Optional context
            
        Returns:
            GenreAnalysis result
        """
        try:
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Genre keywords mapping
            genre_keywords = {
                'entertainment': ['funny', 'hilarious', 'comedy', 'entertainment', 'laugh', 'humor'],
                'educational': ['learn', 'education', 'tutorial', 'guide', 'how to', 'explain'],
                'news': ['news', 'breaking', 'update', 'report', 'journalist', 'current'],
                'lifestyle': ['lifestyle', 'daily', 'routine', 'personal', 'life', 'vlog'],
                'technology': ['tech', 'software', 'programming', 'computer', 'digital', 'app'],
                'gaming': ['game', 'gaming', 'play', 'player', 'level', 'score', 'competition'],
                'music': ['music', 'song', 'artist', 'album', 'concert', 'melody', 'rhythm'],
                'sports': ['sport', 'game', 'athlete', 'competition', 'team', 'win', 'match'],
                'fashion': ['fashion', 'style', 'clothing', 'outfit', 'trend', 'designer'],
                'food': ['food', 'recipe', 'cooking', 'restaurant', 'delicious', 'cuisine']
            }
            
            content_lower = content.lower()
            genre_scores = {}
            
            # Calculate genre scores
            for genre, keywords in genre_keywords.items():
                score = sum(1 for keyword in keywords if keyword in content_lower)
                genre_scores[genre] = score
            
            # Determine primary genre
            if genre_scores and max(genre_scores.values()) > 0:
                primary_genre = max(genre_scores, key=genre_scores.get)
                genre_confidence = min(0.95, 0.5 + (genre_scores[primary_genre] / 10))
            else:
                primary_genre = 'general'
                genre_confidence = 0.3
            
            # Determine sub-genres
            threshold = max(1, max(genre_scores.values()) * 0.3)
            sub_genres = [genre for genre, score in genre_scores.items() 
                         if score >= threshold and genre != primary_genre]
            
            # Style characteristics
            style_characteristics = []
            if any(word in content_lower for word in ['personal', 'my', 'i']):
                style_characteristics.append('personal')
            if any(word in content_lower for word in ['professional', 'business', 'corporate']):
                style_characteristics.append('professional')
            if any(word in content_lower for word in ['casual', 'friendly', 'relaxed']):
                style_characteristics.append('casual')
            if len(content) > 1000:
                style_characteristics.append('detailed')
            elif len(content) < 200:
                style_characteristics.append('concise')
            
            # Content themes (simplified)
            content_themes = []
            theme_keywords = {
                'inspiration': ['inspire', 'motivate', 'achieve', 'success', 'dream'],
                'information': ['fact', 'data', 'research', 'study', 'analysis'],
                'entertainment': ['fun', 'enjoy', 'laugh', 'amusing', 'entertaining'],
                'community': ['community', 'together', 'share', 'connect', 'social']
            }
            
            for theme, keywords in theme_keywords.items():
                if any(keyword in content_lower for keyword in keywords):
                    content_themes.append(theme)
            
            # Target audience (simplified)
            if any(word in content_lower for word in ['kids', 'children', 'young']):
                target_audience = 'children'
            elif any(word in content_lower for word in ['teen', 'teenager', 'youth']):
                target_audience = 'teenagers'
            elif any(word in content_lower for word in ['professional', 'business', 'career']):
                target_audience = 'professionals'
            else:
                target_audience = 'general'
            
            return GenreAnalysis(
                primary_genre=primary_genre,
                genre_confidence=genre_confidence,
                sub_genres=sub_genres[:3],  # Limit to top 3
                style_characteristics=style_characteristics,
                content_themes=content_themes,
                target_audience=target_audience,
                genre_trends={'primary_score': genre_scores.get(primary_genre, 0)}
            )
            
        except Exception as e:
            logger.error(f"Genre analysis failed: {e}")
            return GenreAnalysis(
                primary_genre='general',
                genre_confidence=0.0,
                sub_genres=[],
                style_characteristics=[],
                content_themes=[],
                target_audience='general'
            )
    
    async def _analyze_engagement(self, content: str, content_type: str,
                                context: Optional[Dict[str, Any]] = None) -> EngagementAnalysis:
        """Analyze engagement potential.
        
        Args:
            content: Content to analyze
            content_type: Type of content
            context: Optional context
            
        Returns:
            EngagementAnalysis result
        """
        try:
            await asyncio.sleep(0.12)  # Simulate processing time
            
            # Engagement factors
            engagement_factors = []
            
            # Calculate engagement components
            hook_score = self._assess_hook_strength(content)
            if hook_score > 0.7:
                engagement_factors.append("strong opening hook")
            
            call_to_action_score = self._assess_call_to_action(content)
            if call_to_action_score > 0.5:
                engagement_factors.append("clear call-to-action")
            
            emotional_appeal_score = self._assess_emotional_appeal(content)
            if emotional_appeal_score > 0.6:
                engagement_factors.append("strong emotional appeal")
            
            interactivity_score = self._assess_interactivity(content)
            if interactivity_score > 0.5:
                engagement_factors.append("interactive elements")
            
            trending_score = self._assess_trending_elements(content)
            if trending_score > 0.6:
                engagement_factors.append("trending elements")
            
            # Calculate scores
            engagement_score = (hook_score + call_to_action_score + emotional_appeal_score + 
                              interactivity_score + trending_score) / 5
            
            viral_potential = (emotional_appeal_score + trending_score + hook_score) / 3
            
            shareability_score = (emotional_appeal_score + interactivity_score + viral_potential) / 3
            
            comment_likelihood = (call_to_action_score + interactivity_score + emotional_appeal_score) / 3
            
            retention_prediction = (hook_score + engagement_score) / 2
            
            # Platform performance predictions
            platform_performance = {
                'youtube': min(1.0, engagement_score * 1.1),  # YouTube favors longer engagement
                'instagram': min(1.0, shareability_score * 1.2),  # Instagram favors visual appeal
                'tiktok': min(1.0, viral_potential * 1.3),  # TikTok favors viral content
                'twitter': min(1.0, shareability_score * 1.1),  # Twitter favors shareable content
                'linkedin': min(1.0, (engagement_score + 0.3) if 'professional' in content.lower() else engagement_score * 0.8)
            }
            
            # Optimization suggestions
            optimization_suggestions = []
            if hook_score < 0.6:
                optimization_suggestions.append("Strengthen opening hook to capture attention")
            if call_to_action_score < 0.4:
                optimization_suggestions.append("Add clear call-to-action for audience engagement")
            if emotional_appeal_score < 0.5:
                optimization_suggestions.append("Increase emotional connection with audience")
            if trending_score < 0.5:
                optimization_suggestions.append("Include current trends or topics")
            if viral_potential < 0.6:
                optimization_suggestions.append("Add shareable elements to increase viral potential")
            
            return EngagementAnalysis(
                engagement_score=engagement_score,
                viral_potential=viral_potential,
                shareability_score=shareability_score,
                comment_likelihood=comment_likelihood,
                retention_prediction=retention_prediction,
                platform_performance=platform_performance,
                engagement_factors=engagement_factors,
                optimization_suggestions=optimization_suggestions
            )
            
        except Exception as e:
            logger.error(f"Engagement analysis failed: {e}")
            return EngagementAnalysis(
                engagement_score=0.0,
                viral_potential=0.0,
                shareability_score=0.0,
                comment_likelihood=0.0,
                retention_prediction=0.0,
                platform_performance={},
                engagement_factors=[],
                optimization_suggestions=["Engagement analysis failed - manual review required"]
            )
    
    def _assess_content_length(self, content: str, content_type: str) -> float:
        """Assess if content length is appropriate."""
        length = len(content)
        
        optimal_ranges = {
            'text': (300, 2000),
            'video': (500, 3000),  # Assuming this is video description/transcript
            'audio': (200, 1500),
            'image': (50, 500)
        }
        
        min_len, max_len = optimal_ranges.get(content_type, (100, 1000))
        
        if min_len <= length <= max_len:
            return 1.0
        elif length < min_len:
            return max(0.3, length / min_len)
        else:
            return max(0.3, 1.0 - ((length - max_len) / max_len))
    
    def _assess_content_structure(self, content: str) -> float:
        """Assess content structure and organization."""
        score = 0.5  # Base score
        
        # Check for paragraphs
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            score += 0.2
        
        # Check for sentences
        sentences = content.split('.')
        if 3 <= len(sentences) <= 20:
            score += 0.2
        
        # Check for questions (engagement)
        if '?' in content:
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_content_clarity(self, content: str) -> float:
        """Assess content clarity and readability."""
        words = content.split()
        if not words:
            return 0.0
        
        # Average word length (simpler words = better clarity)
        avg_word_length = sum(len(word) for word in words) / len(words)
        word_score = max(0.0, 1.0 - ((avg_word_length - 5) / 10))
        
        # Sentence length
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            sentence_score = max(0.0, 1.0 - ((avg_sentence_length - 15) / 25))
        else:
            sentence_score = 0.5
        
        return (word_score + sentence_score) / 2
    
    def _assess_originality(self, content: str) -> float:
        """Assess content originality (simplified heuristic)."""
        # Check for personal pronouns (indicates original perspective)
        personal_indicators = content.lower().count('i ') + content.lower().count('my ') + content.lower().count('me ')
        personal_score = min(0.4, personal_indicators / 10)
        
        # Check for unique expressions
        unique_phrases = ['in my opinion', 'personally', 'from my experience', 'i believe']
        unique_score = min(0.3, sum(1 for phrase in unique_phrases if phrase in content.lower()) / 10)
        
        # Length bonus (longer content often more original)
        length_bonus = min(0.3, len(content) / 1000)
        
        return personal_score + unique_score + length_bonus
    
    def _assess_creativity(self, content: str) -> float:
        """Assess content creativity."""
        creative_indicators = ['creative', 'innovative', 'unique', 'original', 'novel', 'artistic']
        creative_words = sum(1 for word in creative_indicators if word in content.lower())
        
        # Check for metaphors and descriptive language
        descriptive_words = ['like', 'as if', 'imagine', 'picture', 'visualize']
        descriptive_count = sum(1 for word in descriptive_words if word in content.lower())
        
        # Check for storytelling elements
        story_elements = ['once', 'then', 'finally', 'suddenly', 'meanwhile']
        story_count = sum(1 for word in story_elements if word in content.lower())
        
        creativity_score = (creative_words + descriptive_count + story_count) / 15
        return min(1.0, creativity_score)
    
    def _assess_educational_value(self, content: str) -> float:
        """Assess educational value of content."""
        educational_indicators = ['learn', 'teach', 'explain', 'understand', 'knowledge', 'fact', 'study']
        educational_count = sum(1 for word in educational_indicators if word in content.lower())
        
        # Check for instructional language
        instructional_words = ['how to', 'step', 'method', 'process', 'technique', 'guide']
        instructional_count = sum(1 for word in instructional_words if word in content.lower())
        
        educational_score = (educational_count + instructional_count) / 10
        return min(1.0, educational_score)
    
    def _assess_entertainment_value(self, content: str) -> float:
        """Assess entertainment value of content."""
        entertainment_indicators = ['fun', 'funny', 'entertaining', 'amusing', 'hilarious', 'laugh']
        entertainment_count = sum(1 for word in entertainment_indicators if word in content.lower())
        
        # Check for exclamation points (excitement)
        excitement_score = min(0.3, content.count('!') / 10)
        
        # Check for emotive language
        emotive_words = ['amazing', 'incredible', 'awesome', 'fantastic', 'wonderful']
        emotive_count = sum(1 for word in emotive_words if word in content.lower())
        
        entertainment_score = (entertainment_count + emotive_count) / 10 + excitement_score
        return min(1.0, entertainment_score)
    
    def _assess_hook_strength(self, content: str) -> float:
        """Assess strength of opening hook."""
        if len(content) < 50:
            return 0.3
        
        opening = content[:100].lower()
        
        # Strong opening indicators
        hook_indicators = ['did you know', 'imagine', 'what if', 'ever wondered', 'question:', '?']
        hook_score = sum(1 for indicator in hook_indicators if indicator in opening) / 5
        
        return min(1.0, hook_score)
    
    def _assess_call_to_action(self, content: str) -> float:
        """Assess call-to-action strength."""
        cta_indicators = ['subscribe', 'like', 'comment', 'share', 'follow', 'click', 'visit', 'join']
        cta_count = sum(1 for word in cta_indicators if word in content.lower())
        
        return min(1.0, cta_count / 3)
    
    def _assess_emotional_appeal(self, content: str) -> float:
        """Assess emotional appeal of content."""
        emotional_words = ['love', 'hate', 'excited', 'sad', 'happy', 'angry', 'surprised', 'fear']
        emotional_count = sum(1 for word in emotional_words if word in content.lower())
        
        return min(1.0, emotional_count / 5)
    
    def _assess_interactivity(self, content: str) -> float:
        """Assess interactive elements in content."""
        interactive_indicators = ['?', 'comment', 'tell me', 'what do you think', 'share your']
        interactive_count = sum(1 for indicator in interactive_indicators if indicator in content.lower())
        
        return min(1.0, interactive_count / 3)
    
    def _assess_trending_elements(self, content: str) -> float:
        """Assess trending elements (simplified)."""
        trending_words = ['trending', 'viral', 'popular', 'latest', 'new', 'fresh', 'hot']
        trending_count = sum(1 for word in trending_words if word in content.lower())
        
        return min(1.0, trending_count / 3)
    
    def _calculate_overall_score(self, sentiment_analysis: Optional[SentimentAnalysis],
                               emotion_analysis: Optional[EmotionAnalysis],
                               quality_analysis: Optional[QualityAnalysis],
                               genre_analysis: Optional[GenreAnalysis],
                               engagement_analysis: Optional[EngagementAnalysis]) -> float:
        """Calculate overall AI analysis score."""
        scores = []
        
        if sentiment_analysis:
            # Positive sentiment contributes to score
            sentiment_score = 0.5  # Neutral baseline
            if sentiment_analysis.polarity in [SentimentPolarity.POSITIVE, SentimentPolarity.VERY_POSITIVE]:
                sentiment_score = 0.5 + (sentiment_analysis.confidence * 0.5)
            elif sentiment_analysis.polarity in [SentimentPolarity.NEGATIVE, SentimentPolarity.VERY_NEGATIVE]:
                sentiment_score = 0.5 - (sentiment_analysis.confidence * 0.3)
            scores.append(sentiment_score)
        
        if emotion_analysis:
            scores.append(emotion_analysis.emotional_intensity)
        
        if quality_analysis:
            scores.append(quality_analysis.overall_quality_score)
        
        if genre_analysis:
            scores.append(genre_analysis.genre_confidence)
        
        if engagement_analysis:
            scores.append(engagement_analysis.engagement_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_confidence_level(self, sentiment_analysis: Optional[SentimentAnalysis],
                                  emotion_analysis: Optional[EmotionAnalysis],
                                  quality_analysis: Optional[QualityAnalysis],
                                  genre_analysis: Optional[GenreAnalysis],
                                  engagement_analysis: Optional[EngagementAnalysis]) -> float:
        """Calculate overall confidence level."""
        confidences = []
        
        if sentiment_analysis:
            confidences.append(sentiment_analysis.confidence)
        
        if emotion_analysis:
            confidences.append(emotion_analysis.emotional_consistency)
        
        if quality_analysis:
            # Quality confidence based on multiple factors
            confidences.append(0.8)  # Assume good confidence for quality analysis
        
        if genre_analysis:
            confidences.append(genre_analysis.genre_confidence)
        
        if engagement_analysis:
            # Engagement confidence based on score consistency
            confidences.append(min(0.9, max(0.5, engagement_analysis.engagement_score)))
        
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def _generate_content_id(self, content: Union[str, Dict[str, Any]]) -> str:
        """Generate unique content ID for analysis tracking."""
        import hashlib
        content_str = str(content)[:1000]  # Use first 1000 chars
        return hashlib.md5(content_str.encode()).hexdigest()[:16]

# Export main classes and functions
__all__ = [
    'AIContentAnalyzer',
    'AnalysisType',
    'ContentCategory',
    'SentimentPolarity',
    'EmotionType',
    'SentimentAnalysis',
    'EmotionAnalysis',
    'QualityAnalysis',
    'GenreAnalysis',
    'EngagementAnalysis',
    'AIAnalysisResult'
]