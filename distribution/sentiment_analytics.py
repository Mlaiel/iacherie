"""
Sentiment Analytics Engine
=========================

Enterprise-grade sentiment analysis for content and audience feedback.
Advanced NLP and ML for real-time sentiment tracking across platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import re
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
import json
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class SentimentPolarity(Enum):
    """Sentiment polarity classifications"""
    VERY_POSITIVE = "very_positive"    # 0.8 to 1.0
    POSITIVE = "positive"              # 0.2 to 0.8
    NEUTRAL = "neutral"                # -0.2 to 0.2
    NEGATIVE = "negative"              # -0.8 to -0.2
    VERY_NEGATIVE = "very_negative"    # -1.0 to -0.8

class EmotionType(Enum):
    """Emotional classifications"""
    JOY = "joy"
    ANGER = "anger"
    FEAR = "fear"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"

class SentimentConfidence(Enum):
    """Confidence levels for sentiment analysis"""
    VERY_HIGH = "very_high"    # 90%+
    HIGH = "high"              # 75-90%
    MEDIUM = "medium"          # 60-75%
    LOW = "low"                # 45-60%
    VERY_LOW = "very_low"      # <45%

@dataclass
class SentimentResult:
    """Result of sentiment analysis"""
    text: str
    polarity: SentimentPolarity
    polarity_score: float  # -1.0 to 1.0
    subjectivity: float    # 0.0 to 1.0 (objective to subjective)
    confidence: float      # 0.0 to 1.0
    confidence_level: SentimentConfidence
    emotions: Dict[EmotionType, float] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    language: str = "en"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class SentimentTrend:
    """Sentiment trend over time"""
    time_period: str
    average_sentiment: float
    sentiment_distribution: Dict[SentimentPolarity, int]
    emotion_trends: Dict[EmotionType, float]
    volume: int
    volatility: float  # Measure of sentiment stability
    trending_keywords: List[Tuple[str, int]] = field(default_factory=list)

@dataclass
class CommentAnalysis:
    """Analysis of comments/feedback"""
    total_comments: int
    sentiment_breakdown: Dict[SentimentPolarity, int]
    average_sentiment: float
    most_positive_comments: List[str]
    most_negative_comments: List[str]
    common_themes: List[str]
    response_needed: bool = False
    urgency_level: str = "low"

class BaseSentimentAnalyzer(ABC):
    """Base class for sentiment analyzers"""
    
    @abstractmethod
    async def analyze_text(self, text: str, language: str = "en") -> SentimentResult:
        """Analyze sentiment of text"""
        pass
    
    @abstractmethod
    async def analyze_batch(self, texts: List[str], language: str = "en") -> List[SentimentResult]:
        """Analyze sentiment of multiple texts"""
        pass

class RuleBasedSentimentAnalyzer(BaseSentimentAnalyzer):
    """Rule-based sentiment analyzer using lexicons"""
    
    def __init__(self):
        # Simplified lexicons (in production, use comprehensive databases)
        self.positive_words = {
            "amazing", "awesome", "brilliant", "excellent", "fantastic", 
            "great", "incredible", "love", "perfect", "wonderful",
            "outstanding", "superb", "magnificent", "spectacular", 
            "phenomenal", "beautiful", "stunning", "impressive",
            "remarkable", "extraordinary", "fabulous", "marvelous",
            "good", "nice", "cool", "sweet", "epic", "best"
        }
        
        self.negative_words = {
            "awful", "terrible", "horrible", "disgusting", "hate",
            "worst", "bad", "disappointing", "annoying", "stupid",
            "ridiculous", "pathetic", "useless", "garbage", "trash",
            "boring", "lame", "weak", "poor", "failed", "broken",
            "disaster", "nightmare", "catastrophe", "abysmal"
        }
        
        self.emotion_keywords = {
            EmotionType.JOY: {"happy", "joy", "excited", "thrilled", "delighted", "cheerful"},
            EmotionType.ANGER: {"angry", "mad", "furious", "irritated", "annoyed", "rage"},
            EmotionType.FEAR: {"scared", "afraid", "terrified", "anxious", "worried", "panic"},
            EmotionType.SADNESS: {"sad", "depressed", "upset", "disappointed", "heartbroken"},
            EmotionType.SURPRISE: {"surprised", "shocked", "amazed", "astonished", "stunned"},
            EmotionType.DISGUST: {"disgusted", "revolted", "repulsed", "sickened"},
            EmotionType.TRUST: {"trust", "reliable", "dependable", "faithful", "loyal"},
            EmotionType.ANTICIPATION: {"excited", "eager", "anticipate", "looking forward"}
        }
        
        self.intensifiers = {"very", "extremely", "incredibly", "absolutely", "totally", "completely"}
        self.negators = {"not", "no", "never", "nothing", "none", "neither", "without"}
    
    async def analyze_text(self, text: str, language: str = "en") -> SentimentResult:
        """Analyze sentiment of single text"""
        try:
            # Preprocess text
            cleaned_text = self._preprocess_text(text)
            words = cleaned_text.lower().split()
            
            # Calculate sentiment scores
            positive_score = 0
            negative_score = 0
            subjectivity_score = 0
            
            # Track emotions
            emotion_scores = {emotion: 0 for emotion in EmotionType}
            
            # Extract keywords and entities
            keywords = []
            entities = []
            
            i = 0
            while i < len(words):
                word = words[i]
                
                # Check for negation
                is_negated = i > 0 and words[i-1] in self.negators
                
                # Check for intensification
                intensity = 1.0
                if i > 0 and words[i-1] in self.intensifiers:
                    intensity = 1.5
                
                # Sentiment scoring
                if word in self.positive_words:
                    score = intensity * (1 if not is_negated else -0.5)
                    positive_score += score
                    subjectivity_score += 0.5
                    
                elif word in self.negative_words:
                    score = intensity * (1 if not is_negated else -0.5)
                    negative_score += score
                    subjectivity_score += 0.5
                
                # Emotion detection
                for emotion, emotion_words in self.emotion_keywords.items():
                    if word in emotion_words:
                        emotion_scores[emotion] += intensity * (1 if not is_negated else 0.3)
                
                # Keyword extraction (simplified)
                if len(word) > 4 and word.isalpha():
                    keywords.append(word)
                
                i += 1
            
            # Calculate final scores
            total_sentiment_words = positive_score + negative_score
            if total_sentiment_words > 0:
                polarity_score = (positive_score - negative_score) / total_sentiment_words
                subjectivity = min(subjectivity_score / len(words), 1.0)
            else:
                polarity_score = 0.0
                subjectivity = 0.0
            
            # Normalize polarity score to -1 to 1 range
            polarity_score = max(-1.0, min(1.0, polarity_score))
            
            # Determine polarity classification
            polarity = self._classify_polarity(polarity_score)
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                polarity_score, subjectivity, total_sentiment_words, len(words)
            )
            confidence_level = self._get_confidence_level(confidence)
            
            # Normalize emotion scores
            if sum(emotion_scores.values()) > 0:
                max_emotion_score = max(emotion_scores.values())
                emotion_scores = {
                    emotion: score / max_emotion_score 
                    for emotion, score in emotion_scores.items()
                }
            
            # Extract top keywords
            keyword_counts = {}
            for keyword in keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            top_keywords = sorted(
                keyword_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            return SentimentResult(
                text=text,
                polarity=polarity,
                polarity_score=polarity_score,
                subjectivity=subjectivity,
                confidence=confidence,
                confidence_level=confidence_level,
                emotions=emotion_scores,
                keywords=[kw for kw, _ in top_keywords],
                entities=entities,  # Would be populated by NER in production
                language=language
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {e}")
            raise
    
    async def analyze_batch(self, texts: List[str], language: str = "en") -> List[SentimentResult]:
        """Analyze sentiment of multiple texts"""
        results = []
        
        for text in texts:
            try:
                result = await self.analyze_text(text, language)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to analyze text in batch: {e}")
                # Add default result for failed analysis
                results.append(SentimentResult(
                    text=text,
                    polarity=SentimentPolarity.NEUTRAL,
                    polarity_score=0.0,
                    subjectivity=0.0,
                    confidence=0.0,
                    confidence_level=SentimentConfidence.VERY_LOW,
                    language=language
                ))
        
        return results
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _classify_polarity(self, score: float) -> SentimentPolarity:
        """Classify polarity based on score"""
        if score >= 0.6:
            return SentimentPolarity.VERY_POSITIVE
        elif score >= 0.2:
            return SentimentPolarity.POSITIVE
        elif score >= -0.2:
            return SentimentPolarity.NEUTRAL
        elif score >= -0.6:
            return SentimentPolarity.NEGATIVE
        else:
            return SentimentPolarity.VERY_NEGATIVE
    
    def _calculate_confidence(
        self, 
        polarity_score: float, 
        subjectivity: float, 
        sentiment_words: float, 
        total_words: int
    ) -> float:
        """Calculate confidence in sentiment analysis"""
        # Base confidence from sentiment strength
        base_confidence = abs(polarity_score)
        
        # Boost confidence with subjectivity
        subjectivity_boost = subjectivity * 0.3
        
        # Boost confidence with sentiment word density
        if total_words > 0:
            density_boost = min(sentiment_words / total_words, 1.0) * 0.3
        else:
            density_boost = 0.0
        
        # Text length factor
        length_factor = min(total_words / 10, 1.0) * 0.1
        
        confidence = base_confidence + subjectivity_boost + density_boost + length_factor
        return min(confidence, 1.0)
    
    def _get_confidence_level(self, confidence: float) -> SentimentConfidence:
        """Convert confidence score to level"""
        if confidence >= 0.9:
            return SentimentConfidence.VERY_HIGH
        elif confidence >= 0.75:
            return SentimentConfidence.HIGH
        elif confidence >= 0.6:
            return SentimentConfidence.MEDIUM
        elif confidence >= 0.45:
            return SentimentConfidence.LOW
        else:
            return SentimentConfidence.VERY_LOW

class SentimentAnalyticsEngine:
    """Main sentiment analytics engine"""
    
    def __init__(self, analyzer: Optional[BaseSentimentAnalyzer] = None):
        self.analyzer = analyzer or RuleBasedSentimentAnalyzer()
        self.sentiment_history: List[SentimentResult] = []
        self.trend_cache: Dict[str, SentimentTrend] = {}
        self.cache_ttl = timedelta(minutes=15)
        
        # Configuration
        self.max_history_size = 10000
        self.trend_periods = ["1h", "6h", "1d", "7d", "30d"]
    
    async def analyze_content(self, text: str, language: str = "en") -> SentimentResult:
        """Analyze sentiment of content"""
        try:
            result = await self.analyzer.analyze_text(text, language)
            
            # Store in history
            self._add_to_history(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze content sentiment: {e}")
            raise
    
    async def analyze_comments(
        self, 
        comments: List[str], 
        language: str = "en"
    ) -> CommentAnalysis:
        """Analyze sentiment of comments/feedback"""
        try:
            if not comments:
                return CommentAnalysis(
                    total_comments=0,
                    sentiment_breakdown={},
                    average_sentiment=0.0,
                    most_positive_comments=[],
                    most_negative_comments=[],
                    common_themes=[]
                )
            
            # Analyze all comments
            results = await self.analyzer.analyze_batch(comments, language)
            
            # Store in history
            for result in results:
                self._add_to_history(result)
            
            # Calculate breakdown
            sentiment_breakdown = {}
            total_sentiment = 0.0
            
            for result in results:
                polarity = result.polarity
                sentiment_breakdown[polarity] = sentiment_breakdown.get(polarity, 0) + 1
                total_sentiment += result.polarity_score
            
            average_sentiment = total_sentiment / len(results)
            
            # Find most positive and negative comments
            sorted_results = sorted(results, key=lambda x: x.polarity_score, reverse=True)
            
            most_positive = [
                r.text for r in sorted_results[:3] 
                if r.polarity_score > 0.5
            ]
            
            most_negative = [
                r.text for r in sorted_results[-3:] 
                if r.polarity_score < -0.5
            ]
            
            # Extract common themes (simplified keyword analysis)
            all_keywords = []
            for result in results:
                all_keywords.extend(result.keywords)
            
            keyword_counts = {}
            for keyword in all_keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            common_themes = [
                kw for kw, count in sorted(
                    keyword_counts.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10] if count > 1
            ]
            
            # Determine if response is needed
            negative_ratio = sentiment_breakdown.get(SentimentPolarity.NEGATIVE, 0) + \
                           sentiment_breakdown.get(SentimentPolarity.VERY_NEGATIVE, 0)
            negative_ratio = negative_ratio / len(results)
            
            response_needed = negative_ratio > 0.3 or average_sentiment < -0.5
            
            urgency_level = "low"
            if negative_ratio > 0.6 or average_sentiment < -0.7:
                urgency_level = "high"
            elif negative_ratio > 0.4 or average_sentiment < -0.3:
                urgency_level = "medium"
            
            return CommentAnalysis(
                total_comments=len(comments),
                sentiment_breakdown=sentiment_breakdown,
                average_sentiment=average_sentiment,
                most_positive_comments=most_positive,
                most_negative_comments=most_negative,
                common_themes=common_themes,
                response_needed=response_needed,
                urgency_level=urgency_level
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze comments: {e}")
            raise
    
    async def get_sentiment_trend(
        self, 
        period: str = "1d",
        platform: Optional[str] = None
    ) -> SentimentTrend:
        """Get sentiment trend for specified period"""
        try:
            cache_key = f"{period}_{platform or 'all'}"
            
            # Check cache
            if cache_key in self.trend_cache:
                cached_trend = self.trend_cache[cache_key]
                # Check if cache is still valid (simplified)
                return cached_trend
            
            # Calculate trend from history
            cutoff_time = self._get_cutoff_time(period)
            
            relevant_history = [
                result for result in self.sentiment_history
                if result.timestamp >= cutoff_time
            ]
            
            if not relevant_history:
                return SentimentTrend(
                    time_period=period,
                    average_sentiment=0.0,
                    sentiment_distribution={},
                    emotion_trends={},
                    volume=0,
                    volatility=0.0
                )
            
            # Calculate average sentiment
            total_sentiment = sum(r.polarity_score for r in relevant_history)
            average_sentiment = total_sentiment / len(relevant_history)
            
            # Calculate sentiment distribution
            sentiment_dist = {}
            for result in relevant_history:
                polarity = result.polarity
                sentiment_dist[polarity] = sentiment_dist.get(polarity, 0) + 1
            
            # Calculate emotion trends
            emotion_totals = {}
            emotion_counts = {}
            
            for result in relevant_history:
                for emotion, score in result.emotions.items():
                    if score > 0:
                        emotion_totals[emotion] = emotion_totals.get(emotion, 0) + score
                        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            emotion_trends = {
                emotion: emotion_totals.get(emotion, 0) / emotion_counts.get(emotion, 1)
                for emotion in EmotionType
            }
            
            # Calculate volatility (sentiment variance)
            sentiment_scores = [r.polarity_score for r in relevant_history]
            if len(sentiment_scores) > 1:
                variance = sum((s - average_sentiment) ** 2 for s in sentiment_scores) / len(sentiment_scores)
                volatility = variance ** 0.5
            else:
                volatility = 0.0
            
            # Extract trending keywords
            all_keywords = []
            for result in relevant_history:
                all_keywords.extend(result.keywords)
            
            keyword_counts = {}
            for keyword in all_keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            trending_keywords = sorted(
                keyword_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            trend = SentimentTrend(
                time_period=period,
                average_sentiment=average_sentiment,
                sentiment_distribution=sentiment_dist,
                emotion_trends=emotion_trends,
                volume=len(relevant_history),
                volatility=volatility,
                trending_keywords=trending_keywords
            )
            
            # Cache the result
            self.trend_cache[cache_key] = trend
            
            return trend
            
        except Exception as e:
            logger.error(f"Failed to get sentiment trend: {e}")
            raise
    
    async def get_real_time_sentiment(self) -> Dict[str, Any]:
        """Get real-time sentiment metrics"""
        try:
            # Get recent sentiment data (last hour)
            recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
            recent_results = [
                r for r in self.sentiment_history
                if r.timestamp >= recent_cutoff
            ]
            
            if not recent_results:
                return {
                    "status": "no_recent_data",
                    "average_sentiment": 0.0,
                    "volume": 0,
                    "dominant_emotion": None,
                    "trending_up": False
                }
            
            # Calculate current metrics
            current_avg = sum(r.polarity_score for r in recent_results) / len(recent_results)
            
            # Compare with previous period
            previous_cutoff = recent_cutoff - timedelta(hours=1)
            previous_results = [
                r for r in self.sentiment_history
                if previous_cutoff <= r.timestamp < recent_cutoff
            ]
            
            trending_up = False
            if previous_results:
                previous_avg = sum(r.polarity_score for r in previous_results) / len(previous_results)
                trending_up = current_avg > previous_avg
            
            # Find dominant emotion
            emotion_totals = {}
            for result in recent_results:
                for emotion, score in result.emotions.items():
                    emotion_totals[emotion] = emotion_totals.get(emotion, 0) + score
            
            dominant_emotion = None
            if emotion_totals:
                dominant_emotion = max(emotion_totals.items(), key=lambda x: x[1])[0].value
            
            return {
                "status": "active",
                "average_sentiment": current_avg,
                "volume": len(recent_results),
                "dominant_emotion": dominant_emotion,
                "trending_up": trending_up,
                "volatility": self._calculate_volatility(recent_results),
                "polarity_distribution": self._get_polarity_distribution(recent_results)
            }
            
        except Exception as e:
            logger.error(f"Failed to get real-time sentiment: {e}")
            return {"status": "error", "message": str(e)}
    
    def _add_to_history(self, result: SentimentResult):
        """Add sentiment result to history"""
        self.sentiment_history.append(result)
        
        # Trim history if too large
        if len(self.sentiment_history) > self.max_history_size:
            self.sentiment_history = self.sentiment_history[-self.max_history_size:]
    
    def _get_cutoff_time(self, period: str) -> datetime:
        """Get cutoff time for period"""
        now = datetime.now(timezone.utc)
        
        if period == "1h":
            return now - timedelta(hours=1)
        elif period == "6h":
            return now - timedelta(hours=6)
        elif period == "1d":
            return now - timedelta(days=1)
        elif period == "7d":
            return now - timedelta(days=7)
        elif period == "30d":
            return now - timedelta(days=30)
        else:
            return now - timedelta(days=1)  # Default to 1 day
    
    def _calculate_volatility(self, results: List[SentimentResult]) -> float:
        """Calculate sentiment volatility"""
        if len(results) < 2:
            return 0.0
        
        scores = [r.polarity_score for r in results]
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        
        return variance ** 0.5
    
    def _get_polarity_distribution(self, results: List[SentimentResult]) -> Dict[str, int]:
        """Get polarity distribution for results"""
        distribution = {}
        
        for result in results:
            polarity = result.polarity.value
            distribution[polarity] = distribution.get(polarity, 0) + 1
        
        return distribution
    
    async def export_sentiment_data(
        self, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Export sentiment data for analysis"""
        try:
            # Filter by time range
            filtered_results = self.sentiment_history
            
            if start_time:
                filtered_results = [r for r in filtered_results if r.timestamp >= start_time]
            
            if end_time:
                filtered_results = [r for r in filtered_results if r.timestamp <= end_time]
            
            # Aggregate data
            export_data = {
                "total_analyzed": len(filtered_results),
                "time_range": {
                    "start": start_time.isoformat() if start_time else None,
                    "end": end_time.isoformat() if end_time else None
                },
                "summary": {
                    "average_sentiment": sum(r.polarity_score for r in filtered_results) / len(filtered_results) if filtered_results else 0,
                    "average_confidence": sum(r.confidence for r in filtered_results) / len(filtered_results) if filtered_results else 0
                },
                "polarity_breakdown": self._get_polarity_distribution(filtered_results),
                "emotion_analysis": self._aggregate_emotions(filtered_results),
                "language_breakdown": self._get_language_distribution(filtered_results)
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export sentiment data: {e}")
            raise
    
    def _aggregate_emotions(self, results: List[SentimentResult]) -> Dict[str, float]:
        """Aggregate emotion data across results"""
        emotion_totals = {}
        emotion_counts = {}
        
        for result in results:
            for emotion, score in result.emotions.items():
                if score > 0:
                    emotion_totals[emotion.value] = emotion_totals.get(emotion.value, 0) + score
                    emotion_counts[emotion.value] = emotion_counts.get(emotion.value, 0) + 1
        
        return {
            emotion: emotion_totals.get(emotion, 0) / emotion_counts.get(emotion, 1)
            for emotion in emotion_totals
        }
    
    def _get_language_distribution(self, results: List[SentimentResult]) -> Dict[str, int]:
        """Get language distribution for results"""
        distribution = {}
        
        for result in results:
            language = result.language
            distribution[language] = distribution.get(language, 0) + 1
        
        return distribution
    
    def clear_history(self):
        """Clear sentiment analysis history"""
        self.sentiment_history.clear()
        self.trend_cache.clear()
        logger.info("Sentiment analysis history cleared")


# Export main components
__all__ = [
    "SentimentAnalyticsEngine",
    "SentimentResult",
    "SentimentTrend",
    "CommentAnalysis",
    "BaseSentimentAnalyzer",
    "RuleBasedSentimentAnalyzer",
    "SentimentPolarity",
    "EmotionType",
    "SentimentConfidence"
]