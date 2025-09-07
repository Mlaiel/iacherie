"""Sentiment Analyzer - Brand Safety and Sentiment Analysis Engine
==============================================================

Advanced AI-powered sentiment analysis system for brand safety, content moderation,
and market sentiment tracking in marketplace operations.

Features:
- Real-time sentiment analysis of content and comments
- Brand safety scoring and risk assessment
- Toxicity detection and content moderation
- Emotion recognition and classification
- Trend sentiment tracking and alerts

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/marketplace/sentiment_analyzer.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import re
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from collections import Counter, defaultdict
import uuid
import json
import statistics

logger = logging.getLogger(__name__)

class SentimentPolarity(Enum):
    """Sentiment polarity enumeration"""
    VERY_POSITIVE = "very_positive"    # 0.8 to 1.0
    POSITIVE = "positive"              # 0.2 to 0.8
    NEUTRAL = "neutral"                # -0.2 to 0.2
    NEGATIVE = "negative"              # -0.8 to -0.2
    VERY_NEGATIVE = "very_negative"    # -1.0 to -0.8

class EmotionType(Enum):
    """Emotion type enumeration"""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"

class ToxicityLevel(Enum):
    """Toxicity level enumeration"""
    SAFE = "safe"                # 0.0 to 0.3
    MILD = "mild"                # 0.3 to 0.5
    MODERATE = "moderate"        # 0.5 to 0.7
    HIGH = "high"                # 0.7 to 0.9
    SEVERE = "severe"            # 0.9 to 1.0

class BrandSafetyLevel(Enum):
    """Brand safety level enumeration"""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    UNSAFE = "unsafe"

class ContentType(Enum):
    """Content type for analysis"""
    TEXT = "text"
    COMMENT = "comment"
    REVIEW = "review"
    DESCRIPTION = "description"
    TITLE = "title"
    MESSAGE = "message"
    POST = "post"

@dataclass
class SentimentScore:
    """Sentiment analysis score"""
    polarity: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    polarity_label: SentimentPolarity
    subjectivity: float = 0.5  # 0.0 (objective) to 1.0 (subjective)
    intensity: float = 0.5     # 0.0 (weak) to 1.0 (strong)

@dataclass
class EmotionScore:
    """Emotion analysis score"""
    emotion: EmotionType
    intensity: float  # 0.0 to 1.0
    confidence: float # 0.0 to 1.0

@dataclass
class ToxicityScore:
    """Toxicity analysis score"""
    score: float  # 0.0 to 1.0
    level: ToxicityLevel
    confidence: float  # 0.0 to 1.0
    categories: List[str] = field(default_factory=list)  # ["hate", "harassment", "violence", etc.]

@dataclass
class BrandSafetyScore:
    """Brand safety assessment"""
    score: float  # 0.0 to 1.0 (0 = unsafe, 1 = safe)
    level: BrandSafetyLevel
    risk_factors: List[str] = field(default_factory=list)
    confidence: float = 0.8

@dataclass
class SentimentAnalysis:
    """Complete sentiment analysis result"""
    analysis_id: str
    text: str
    content_type: ContentType
    sentiment: SentimentScore
    emotions: List[EmotionScore] = field(default_factory=list)
    toxicity: Optional[ToxicityScore] = None
    brand_safety: Optional[BrandSafetyScore] = None
    keywords: List[str] = field(default_factory=list)
    language: str = "en"
    analyzed_at: datetime = field(default_factory=datetime.utcnow)
    processing_time_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SentimentTrend:
    """Sentiment trend over time"""
    trend_id: str
    entity_id: str  # product_id, creator_id, etc.
    entity_type: str
    period_start: datetime
    period_end: datetime
    average_sentiment: float
    sentiment_distribution: Dict[str, float] = field(default_factory=dict)
    volume: int = 0
    trend_direction: str = "stable"  # "improving", "declining", "stable"
    volatility: float = 0.0
    key_topics: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ContentModerationResult:
    """Content moderation decision"""
    moderation_id: str
    content_id: str
    action: str  # "approve", "reject", "review", "flag"
    reason: str = ""
    confidence: float = 0.8
    flags: List[str] = field(default_factory=list)
    reviewed_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class SentimentAnalyzer:
    """Advanced sentiment analysis and brand safety system"""
    
    def __init__(self):
        self.sentiment_analyses: Dict[str, SentimentAnalysis] = {}
        self.sentiment_trends: Dict[str, SentimentTrend] = {}
        self.moderation_results: Dict[str, ContentModerationResult] = {}
        
        # Sentiment lexicons (simplified - in production would use comprehensive datasets)
        self.positive_words = {
            "excellent", "amazing", "great", "wonderful", "fantastic", "awesome", 
            "love", "perfect", "brilliant", "outstanding", "superb", "magnificent",
            "good", "nice", "happy", "satisfied", "pleased", "delighted"
        }
        
        self.negative_words = {
            "terrible", "awful", "horrible", "bad", "worst", "hate", "disgusting",
            "pathetic", "useless", "garbage", "trash", "disappointing", "poor",
            "sad", "angry", "frustrated", "annoyed", "upset", "dissatisfied"
        }
        
        self.toxic_patterns = [
            r'\b(hate|kill|die|murder)\b',
            r'\b(stupid|idiot|moron|dumb)\b',
            r'\b(f[*u]ck|sh[*i]t|damn)\b',
            r'\b(threat|harm|hurt)\b'
        ]
        
        self.emotion_keywords = {
            EmotionType.JOY: ["happy", "joy", "excited", "thrilled", "delighted", "cheerful"],
            EmotionType.SADNESS: ["sad", "depressed", "disappointed", "gloomy", "melancholy"],
            EmotionType.ANGER: ["angry", "furious", "mad", "annoyed", "irritated", "rage"],
            EmotionType.FEAR: ["scared", "afraid", "terrified", "worried", "anxious", "nervous"],
            EmotionType.SURPRISE: ["surprised", "shocked", "amazed", "astonished", "stunned"],
            EmotionType.DISGUST: ["disgusted", "revolted", "repulsed", "sickened"],
            EmotionType.TRUST: ["trust", "confident", "reliable", "dependable", "secure"],
            EmotionType.ANTICIPATION: ["excited", "eager", "hopeful", "expecting", "anticipating"]
        }
        
        # Brand safety risk patterns
        self.brand_risk_patterns = [
            r'\b(controversy|scandal|lawsuit|investigation)\b',
            r'\b(fraud|scam|cheat|lie|fake)\b',
            r'\b(violence|weapon|attack|assault)\b',
            r'\b(drug|alcohol|gambling|addiction)\b'
        ]
    
    async def analyze_sentiment(
        self,
        text: str,
        content_type: ContentType = ContentType.TEXT,
        include_emotions: bool = True,
        include_toxicity: bool = True,
        include_brand_safety: bool = True,
        language: str = "en"
    ) -> SentimentAnalysis:
        """Perform comprehensive sentiment analysis"""
        try:
            start_time = datetime.utcnow()
            analysis_id = f"sentiment_{uuid.uuid4().hex[:12]}"
            
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # Analyze sentiment
            sentiment = await self._analyze_sentiment_polarity(cleaned_text)
            
            # Analyze emotions
            emotions = []
            if include_emotions:
                emotions = await self._analyze_emotions(cleaned_text)
            
            # Analyze toxicity
            toxicity = None
            if include_toxicity:
                toxicity = await self._analyze_toxicity(cleaned_text)
            
            # Analyze brand safety
            brand_safety = None
            if include_brand_safety:
                brand_safety = await self._analyze_brand_safety(cleaned_text, sentiment, toxicity)
            
            # Extract keywords
            keywords = self._extract_keywords(cleaned_text)
            
            # Calculate processing time
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            analysis = SentimentAnalysis(
                analysis_id=analysis_id,
                text=text,
                content_type=content_type,
                sentiment=sentiment,
                emotions=emotions,
                toxicity=toxicity,
                brand_safety=brand_safety,
                keywords=keywords,
                language=language,
                processing_time_ms=processing_time
            )
            
            self.sentiment_analyses[analysis_id] = analysis
            
            logger.info(f"Sentiment analysis completed: {analysis_id} - {sentiment.polarity_label.value}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{3,}', '...', text)
        
        return text
    
    async def _analyze_sentiment_polarity(self, text: str) -> SentimentScore:
        """Analyze sentiment polarity using lexicon-based approach"""
        words = text.split()
        
        # Count positive and negative words
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Handle negations (simplified)
        negation_words = {"not", "no", "never", "none", "nothing", "neither", "nowhere", "nobody"}
        negated_positive = 0
        negated_negative = 0
        
        for i, word in enumerate(words):
            if word in negation_words and i + 1 < len(words):
                next_word = words[i + 1]
                if next_word in self.positive_words:
                    negated_positive += 1
                elif next_word in self.negative_words:
                    negated_negative += 1
        
        # Adjust counts for negations
        positive_count = max(0, positive_count - negated_positive)
        negative_count = max(0, negative_count - negated_negative)
        
        # Add negated sentiments with reversed polarity
        positive_count += negated_negative
        negative_count += negated_positive
        
        # Calculate polarity score
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            polarity = 0.0
            confidence = 0.5
        else:
            polarity = (positive_count - negative_count) / len(words)  # Normalize by total words
            confidence = min(1.0, total_sentiment_words / max(1, len(words) / 10))  # Confidence based on sentiment word density
        
        # Clamp polarity to [-1, 1]
        polarity = max(-1.0, min(1.0, polarity))
        
        # Determine polarity label
        if polarity >= 0.6:
            polarity_label = SentimentPolarity.VERY_POSITIVE
        elif polarity >= 0.1:
            polarity_label = SentimentPolarity.POSITIVE
        elif polarity <= -0.6:
            polarity_label = SentimentPolarity.VERY_NEGATIVE
        elif polarity <= -0.1:
            polarity_label = SentimentPolarity.NEGATIVE
        else:
            polarity_label = SentimentPolarity.NEUTRAL
        
        # Calculate subjectivity (ratio of opinion words to total words)
        subjectivity = min(1.0, total_sentiment_words / max(1, len(words)))
        
        # Calculate intensity
        intensity = min(1.0, abs(polarity) * 2)
        
        return SentimentScore(
            polarity=polarity,
            confidence=confidence,
            polarity_label=polarity_label,
            subjectivity=subjectivity,
            intensity=intensity
        )
    
    async def _analyze_emotions(self, text: str) -> List[EmotionScore]:
        """Analyze emotions in text"""
        emotions = []
        words = text.split()
        
        for emotion_type, keywords in self.emotion_keywords.items():
            # Count emotion-related words
            emotion_count = sum(1 for word in words if word in keywords)
            
            if emotion_count > 0:
                # Calculate intensity based on word frequency and context
                intensity = min(1.0, emotion_count / max(1, len(words) / 20))
                confidence = min(1.0, emotion_count / 3)  # Higher confidence with more emotion words
                
                emotions.append(EmotionScore(
                    emotion=emotion_type,
                    intensity=intensity,
                    confidence=confidence
                ))
        
        # Sort by intensity (strongest emotions first)
        emotions.sort(key=lambda x: x.intensity, reverse=True)
        
        # Return top 3 emotions
        return emotions[:3]
    
    async def _analyze_toxicity(self, text: str) -> ToxicityScore:
        """Analyze toxicity level in text"""
        toxicity_score = 0.0
        categories = []
        
        # Check for toxic patterns
        for pattern in self.toxic_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                toxicity_score += len(matches) * 0.3
                categories.append("offensive_language")
        
        # Check for excessive capitalization (shouting)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
        if caps_ratio > 0.5:
            toxicity_score += 0.1
            categories.append("aggressive_tone")
        
        # Check for repeated punctuation (aggressive)
        if re.search(r'[!]{3,}|[?]{3,}', text):
            toxicity_score += 0.1
            categories.append("aggressive_tone")
        
        # Check for personal attacks
        personal_attack_patterns = [
            r'\byou\s+(are|r)\s+(stupid|dumb|idiot)',
            r'\byour?\s+(stupid|dumb|pathetic)',
            r'\bshut\s+up\b'
        ]
        
        for pattern in personal_attack_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                toxicity_score += 0.4
                categories.append("personal_attack")
        
        # Normalize toxicity score
        toxicity_score = min(1.0, toxicity_score)
        
        # Determine toxicity level
        if toxicity_score >= 0.9:
            level = ToxicityLevel.SEVERE
        elif toxicity_score >= 0.7:
            level = ToxicityLevel.HIGH
        elif toxicity_score >= 0.5:
            level = ToxicityLevel.MODERATE
        elif toxicity_score >= 0.3:
            level = ToxicityLevel.MILD
        else:
            level = ToxicityLevel.SAFE
        
        # Calculate confidence
        confidence = min(1.0, len(categories) * 0.3 + (toxicity_score * 0.5))
        
        return ToxicityScore(
            score=toxicity_score,
            level=level,
            confidence=confidence,
            categories=list(set(categories))
        )
    
    async def _analyze_brand_safety(
        self,
        text: str,
        sentiment: SentimentScore,
        toxicity: Optional[ToxicityScore]
    ) -> BrandSafetyScore:
        """Analyze brand safety level"""
        safety_score = 1.0  # Start with safe
        risk_factors = []
        
        # Deduct for negative sentiment
        if sentiment.polarity < -0.5:
            safety_score -= 0.3
            risk_factors.append("negative_sentiment")
        elif sentiment.polarity < -0.2:
            safety_score -= 0.1
            risk_factors.append("mildly_negative_sentiment")
        
        # Deduct for toxicity
        if toxicity:
            safety_score -= toxicity.score * 0.5
            if toxicity.level != ToxicityLevel.SAFE:
                risk_factors.append(f"toxicity_{toxicity.level.value}")
        
        # Check for brand risk patterns
        for pattern in self.brand_risk_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                safety_score -= 0.2
                risk_factors.append("controversial_content")
        
        # Check for competitor mentions (simplified)
        competitor_patterns = [
            r'\bcompetitor\b',
            r'\bbetter\s+than\s+\w+',
            r'\bswitch\s+to\s+\w+'
        ]
        
        for pattern in competitor_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                safety_score -= 0.1
                risk_factors.append("competitor_mention")
        
        # Ensure score is in valid range
        safety_score = max(0.0, min(1.0, safety_score))
        
        # Determine safety level
        if safety_score >= 0.8:
            level = BrandSafetyLevel.SAFE
        elif safety_score >= 0.6:
            level = BrandSafetyLevel.LOW_RISK
        elif safety_score >= 0.4:
            level = BrandSafetyLevel.MEDIUM_RISK
        elif safety_score >= 0.2:
            level = BrandSafetyLevel.HIGH_RISK
        else:
            level = BrandSafetyLevel.UNSAFE
        
        return BrandSafetyScore(
            score=safety_score,
            level=level,
            risk_factors=risk_factors,
            confidence=0.8
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove stop words and extract meaningful terms
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"
        }
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Return most frequent words (simplified keyword extraction)
        from collections import Counter
        word_counts = Counter(keywords)
        
        return [word for word, count in word_counts.most_common(10)]
    
    async def moderate_content(
        self,
        content_id: str,
        text: str,
        content_type: ContentType = ContentType.TEXT
    ) -> ContentModerationResult:
        """Perform automated content moderation"""
        try:
            moderation_id = f"mod_{uuid.uuid4().hex[:12]}"
            
            # Analyze content
            analysis = await self.analyze_sentiment(text, content_type)
            
            # Make moderation decision
            action = "approve"
            reason = "Content meets community guidelines"
            flags = []
            confidence = 0.8
            
            # Check toxicity
            if analysis.toxicity:
                if analysis.toxicity.level == ToxicityLevel.SEVERE:
                    action = "reject"
                    reason = "Content contains severe toxic language"
                    flags.extend(analysis.toxicity.categories)
                    confidence = analysis.toxicity.confidence
                elif analysis.toxicity.level == ToxicityLevel.HIGH:
                    action = "review"
                    reason = "Content requires manual review due to potential toxicity"
                    flags.extend(analysis.toxicity.categories)
                    confidence = analysis.toxicity.confidence
                elif analysis.toxicity.level == ToxicityLevel.MODERATE:
                    action = "flag"
                    reason = "Content flagged for moderate toxicity"
                    flags.extend(analysis.toxicity.categories)
            
            # Check brand safety
            if analysis.brand_safety:
                if analysis.brand_safety.level == BrandSafetyLevel.UNSAFE:
                    action = "reject"
                    reason = "Content unsafe for brand association"
                    flags.extend(analysis.brand_safety.risk_factors)
                elif analysis.brand_safety.level == BrandSafetyLevel.HIGH_RISK:
                    if action == "approve":  # Don't override more severe actions
                        action = "review"
                        reason = "Content requires review due to brand safety risks"
                        flags.extend(analysis.brand_safety.risk_factors)
            
            # Check sentiment for extreme negativity
            if analysis.sentiment.polarity <= -0.8 and analysis.sentiment.confidence > 0.7:
                if action == "approve":
                    action = "flag"
                    reason = "Content flagged for extremely negative sentiment"
                    flags.append("extreme_negativity")
            
            result = ContentModerationResult(
                moderation_id=moderation_id,
                content_id=content_id,
                action=action,
                reason=reason,
                confidence=confidence,
                flags=list(set(flags))  # Remove duplicates
            )
            
            self.moderation_results[moderation_id] = result
            
            logger.info(f"Content moderation completed: {content_id} -> {action}")
            return result
            
        except Exception as e:
            logger.error(f"Error moderating content: {e}")
            raise
    
    async def analyze_sentiment_trend(
        self,
        entity_id: str,
        entity_type: str,
        period_days: int = 7
    ) -> SentimentTrend:
        """Analyze sentiment trend for an entity over time"""
        try:
            trend_id = f"trend_{uuid.uuid4().hex[:12]}"
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get relevant sentiment analyses (in production would query from database)
            relevant_analyses = [
                analysis for analysis in self.sentiment_analyses.values()
                if start_date <= analysis.analyzed_at <= end_date
                # In production would filter by entity_id/entity_type
            ]
            
            if not relevant_analyses:
                # Return neutral trend for no data
                return SentimentTrend(
                    trend_id=trend_id,
                    entity_id=entity_id,
                    entity_type=entity_type,
                    period_start=start_date,
                    period_end=end_date,
                    average_sentiment=0.0,
                    volume=0
                )
            
            # Calculate average sentiment
            sentiments = [analysis.sentiment.polarity for analysis in relevant_analyses]
            average_sentiment = statistics.mean(sentiments)
            
            # Calculate sentiment distribution
            sentiment_distribution = {
                "very_positive": sum(1 for s in sentiments if s >= 0.6) / len(sentiments),
                "positive": sum(1 for s in sentiments if 0.1 <= s < 0.6) / len(sentiments),
                "neutral": sum(1 for s in sentiments if -0.1 < s < 0.1) / len(sentiments),
                "negative": sum(1 for s in sentiments if -0.6 <= s <= -0.1) / len(sentiments),
                "very_negative": sum(1 for s in sentiments if s < -0.6) / len(sentiments)
            }
            
            # Determine trend direction (simplified)
            if len(sentiments) >= 3:
                recent_avg = statistics.mean(sentiments[-len(sentiments)//3:])
                earlier_avg = statistics.mean(sentiments[:len(sentiments)//3])
                
                if recent_avg > earlier_avg + 0.1:
                    trend_direction = "improving"
                elif recent_avg < earlier_avg - 0.1:
                    trend_direction = "declining"
                else:
                    trend_direction = "stable"
            else:
                trend_direction = "stable"
            
            # Calculate volatility
            volatility = statistics.stdev(sentiments) if len(sentiments) > 1 else 0.0
            
            # Extract key topics from keywords
            all_keywords = []
            for analysis in relevant_analyses:
                all_keywords.extend(analysis.keywords)
            
            # Get most frequent keywords as key topics
            from collections import Counter
            keyword_counts = Counter(all_keywords)
            key_topics = [keyword for keyword, count in keyword_counts.most_common(5)]
            
            trend = SentimentTrend(
                trend_id=trend_id,
                entity_id=entity_id,
                entity_type=entity_type,
                period_start=start_date,
                period_end=end_date,
                average_sentiment=average_sentiment,
                sentiment_distribution=sentiment_distribution,
                volume=len(relevant_analyses),
                trend_direction=trend_direction,
                volatility=volatility,
                key_topics=key_topics
            )
            
            self.sentiment_trends[trend_id] = trend
            
            logger.info(f"Sentiment trend analyzed: {entity_id} - {trend_direction}")
            return trend
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment trend: {e}")
            raise
    
    async def get_brand_safety_report(
        self,
        entity_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive brand safety report"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Get relevant analyses
            relevant_analyses = [
                analysis for analysis in self.sentiment_analyses.values()
                if start_date <= analysis.analyzed_at <= end_date
                and analysis.brand_safety is not None
            ]
            
            if not relevant_analyses:
                return {
                    "entity_id": entity_id,
                    "period_days": period_days,
                    "total_content": 0,
                    "overall_safety_score": 1.0,
                    "safety_level": "safe"
                }
            
            # Calculate overall safety metrics
            safety_scores = [analysis.brand_safety.score for analysis in relevant_analyses]
            overall_safety_score = statistics.mean(safety_scores)
            
            # Safety level distribution
            safety_levels = [analysis.brand_safety.level.value for analysis in relevant_analyses]
            level_distribution = {level: safety_levels.count(level) / len(safety_levels) for level in set(safety_levels)}
            
            # Risk factors analysis
            all_risk_factors = []
            for analysis in relevant_analyses:
                all_risk_factors.extend(analysis.brand_safety.risk_factors)
            
            from collections import Counter
            risk_factor_counts = Counter(all_risk_factors)
            
            # Toxicity analysis
            toxic_content = [
                analysis for analysis in relevant_analyses
                if analysis.toxicity and analysis.toxicity.level != ToxicityLevel.SAFE
            ]
            
            toxicity_rate = len(toxic_content) / len(relevant_analyses)
            
            # Content moderation summary
            moderation_actions = [
                result.action for result in self.moderation_results.values()
                # In production would filter by entity and time period
            ]
            
            action_distribution = {}
            if moderation_actions:
                from collections import Counter
                action_counts = Counter(moderation_actions)
                action_distribution = {action: count / len(moderation_actions) for action, count in action_counts.items()}
            
            return {
                "entity_id": entity_id,
                "period_days": period_days,
                "total_content": len(relevant_analyses),
                "overall_safety_score": overall_safety_score,
                "safety_level": self._determine_overall_safety_level(overall_safety_score),
                "safety_level_distribution": level_distribution,
                "top_risk_factors": dict(risk_factor_counts.most_common(5)),
                "toxicity_rate": toxicity_rate,
                "content_moderation": {
                    "total_moderated": len(moderation_actions),
                    "action_distribution": action_distribution
                },
                "recommendations": self._generate_safety_recommendations(
                    overall_safety_score, risk_factor_counts, toxicity_rate
                ),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating brand safety report: {e}")
            return {"error": str(e)}
    
    def _determine_overall_safety_level(self, score: float) -> str:
        """Determine overall safety level from score"""
        if score >= 0.8:
            return "safe"
        elif score >= 0.6:
            return "low_risk"
        elif score >= 0.4:
            return "medium_risk"
        elif score >= 0.2:
            return "high_risk"
        else:
            return "unsafe"
    
    def _generate_safety_recommendations(
        self,
        overall_score: float,
        risk_factors: Dict[str, int],
        toxicity_rate: float
    ) -> List[str]:
        """Generate brand safety recommendations"""
        recommendations = []
        
        if overall_score < 0.6:
            recommendations.append("Implement stricter content moderation policies")
        
        if toxicity_rate > 0.1:
            recommendations.append("Enhance toxicity detection and prevention measures")
        
        if "negative_sentiment" in risk_factors:
            recommendations.append("Monitor and address sources of negative sentiment")
        
        if "controversial_content" in risk_factors:
            recommendations.append("Review content guidelines for controversial topics")
        
        if "competitor_mention" in risk_factors:
            recommendations.append("Implement competitor mention monitoring")
        
        if not recommendations:
            recommendations.append("Continue current brand safety practices")
        
        return recommendations
    
    # Public interface methods
    
    def get_analysis(self, analysis_id: str) -> Optional[SentimentAnalysis]:
        """Get sentiment analysis by ID"""
        return self.sentiment_analyses.get(analysis_id)
    
    def get_trend(self, trend_id: str) -> Optional[SentimentTrend]:
        """Get sentiment trend by ID"""
        return self.sentiment_trends.get(trend_id)
    
    def get_moderation_result(self, moderation_id: str) -> Optional[ContentModerationResult]:
        """Get moderation result by ID"""
        return self.moderation_results.get(moderation_id)
    
    async def get_sentiment_analytics(self) -> Dict[str, Any]:
        """Get sentiment analyzer analytics"""
        total_analyses = len(self.sentiment_analyses)
        
        if total_analyses == 0:
            return {"total_analyses": 0}
        
        # Sentiment distribution
        sentiments = [analysis.sentiment.polarity_label.value for analysis in self.sentiment_analyses.values()]
        from collections import Counter
        sentiment_distribution = Counter(sentiments)
        
        # Average processing time
        processing_times = [analysis.processing_time_ms for analysis in self.sentiment_analyses.values()]
        avg_processing_time = statistics.mean(processing_times)
        
        # Toxicity statistics
        toxic_analyses = [
            analysis for analysis in self.sentiment_analyses.values()
            if analysis.toxicity and analysis.toxicity.level != ToxicityLevel.SAFE
        ]
        toxicity_rate = len(toxic_analyses) / total_analyses
        
        # Brand safety statistics
        unsafe_content = [
            analysis for analysis in self.sentiment_analyses.values()
            if analysis.brand_safety and analysis.brand_safety.level in [BrandSafetyLevel.HIGH_RISK, BrandSafetyLevel.UNSAFE]
        ]
        unsafe_rate = len(unsafe_content) / total_analyses
        
        # Moderation statistics
        moderation_actions = [result.action for result in self.moderation_results.values()]
        moderation_distribution = Counter(moderation_actions) if moderation_actions else {}
        
        return {
            "total_analyses": total_analyses,
            "sentiment_distribution": dict(sentiment_distribution),
            "average_processing_time_ms": avg_processing_time,
            "toxicity_rate": toxicity_rate,
            "brand_safety_risk_rate": unsafe_rate,
            "moderation_actions": dict(moderation_distribution),
            "total_trends": len(self.sentiment_trends),
            "total_moderation_results": len(self.moderation_results)
        }

# Example usage
async def main():
    """Example usage of SentimentAnalyzer"""
    analyzer = SentimentAnalyzer()
    
    # Analyze sentiment of different texts
    test_texts = [
        "I absolutely love this product! It's amazing and works perfectly.",
        "This is terrible quality. I hate it and want my money back.",
        "The service is okay, nothing special but gets the job done.",
        "You're an idiot if you buy this garbage. Complete waste of money!",
        "Great collaboration opportunity! Looking forward to working together."
    ]
    
    for i, text in enumerate(test_texts):
        analysis = await analyzer.analyze_sentiment(text, ContentType.REVIEW)
        
        print(f"\nText {i+1}: {text}")
        print(f"Sentiment: {analysis.sentiment.polarity_label.value} ({analysis.sentiment.polarity:.2f})")
        print(f"Confidence: {analysis.sentiment.confidence:.2f}")
        
        if analysis.emotions:
            print(f"Top emotion: {analysis.emotions[0].emotion.value} ({analysis.emotions[0].intensity:.2f})")
        
        if analysis.toxicity:
            print(f"Toxicity: {analysis.toxicity.level.value} ({analysis.toxicity.score:.2f})")
        
        if analysis.brand_safety:
            print(f"Brand safety: {analysis.brand_safety.level.value} ({analysis.brand_safety.score:.2f})")
        
        # Moderate content
        moderation = await analyzer.moderate_content(f"content_{i+1}", text, ContentType.REVIEW)
        print(f"Moderation: {moderation.action} - {moderation.reason}")
    
    # Generate sentiment trend
    trend = await analyzer.analyze_sentiment_trend("product_123", "product", 7)
    print(f"\nSentiment trend: {trend.trend_direction} (avg: {trend.average_sentiment:.2f})")
    
    # Generate brand safety report
    safety_report = await analyzer.get_brand_safety_report("brand_123", 30)
    print(f"\nBrand safety score: {safety_report['overall_safety_score']:.2f}")
    print(f"Safety level: {safety_report['safety_level']}")
    
    # Get analytics
    analytics = await analyzer.get_sentiment_analytics()
    print(f"\nSentiment analytics: {analytics}")

if __name__ == "__main__":
    asyncio.run(main())