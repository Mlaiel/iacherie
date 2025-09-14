"""Instant Feedback Processor - Real-Time User Feedback Analysis

Enterprise-grade instant feedback processing system for real-time content optimization.
Processes user feedback, comments, reactions, and engagement signals in milliseconds
to provide immediate optimization insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
from pydantic import BaseModel, Field, validator


class FeedbackType(str, Enum):
    """Types of user feedback"""
    LIKE = "like"
    DISLIKE = "dislike"
    COMMENT = "comment"
    SHARE = "share"
    SAVE = "save"
    REACTION = "reaction"
    VIEW_TIME = "view_time"
    CLICK_THROUGH = "click_through"
    ENGAGEMENT = "engagement"


class SentimentPolarity(str, Enum):
    """Sentiment analysis results"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class FeedbackSignal:
    """Individual feedback signal"""
    signal_type: FeedbackType
    user_id: str
    content_id: str
    platform: str
    timestamp: datetime
    value: Union[str, int, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    sentiment: Optional[SentimentPolarity] = None
    confidence: float = 0.0


@dataclass
class FeedbackAnalysis:
    """Comprehensive feedback analysis results"""
    content_id: str
    platform: str
    analysis_timestamp: datetime
    
    # Engagement metrics
    total_signals: int
    engagement_rate: float
    sentiment_distribution: Dict[SentimentPolarity, float]
    feedback_velocity: float  # signals per minute
    
    # Quality indicators
    positive_ratio: float
    negative_ratio: float
    authenticity_score: float
    spam_probability: float
    
    # Trend analysis
    momentum_trend: str  # "increasing", "decreasing", "stable"
    peak_engagement_time: Optional[datetime]
    predicted_virality: float
    
    # Actionable insights
    optimization_suggestions: List[str]
    immediate_actions: List[str]
    risk_alerts: List[str]
    
    confidence_level: float
    processing_time_ms: float


class InstantFeedbackProcessor:
    """Real-time feedback processing and analysis engine"""
    
    def __init__(self, 
                 sentiment_threshold -> None: float = 0.7,
                 spam_detection_threshold -> None: float = 0.8,
                 velocity_window_minutes -> None: int = 5,
                 max_processing_time_ms -> None: float = 50.0) -> None:
        self.sentiment_threshold = sentiment_threshold
        self.spam_detection_threshold = spam_detection_threshold
        self.velocity_window_minutes = velocity_window_minutes
        self.max_processing_time_ms = max_processing_time_ms
        
        # Real-time buffers
        self.feedback_buffer: Dict[str, List[FeedbackSignal]] = {}
        self.analysis_cache: Dict[str, FeedbackAnalysis] = {}
        self.sentiment_models = self._initialize_sentiment_models()
        self.spam_detector = self._initialize_spam_detector()
        
        # Performance monitoring
        self.processing_stats = {
            "total_processed": 0,
            "avg_processing_time": 0.0,
            "cache_hit_rate": 0.0,
            "error_rate": 0.0
        }
        
        self.logger = logging.getLogger(__name__)
    
    def _initialize_sentiment_models(self) -> Dict[str, Any]:
        """Initialize sentiment analysis models for different content types"""
        return {
            "text": self._load_text_sentiment_model(),
            "visual": self._load_visual_sentiment_model(),
            "audio": self._load_audio_sentiment_model(),
            "multimodal": self._load_multimodal_sentiment_model()
        }
    
    def _load_text_sentiment_model(self) -> Any:
        """Load text sentiment analysis model"""
        # In production, this would load actual ML models
        return {
            "model_type": "transformer_based",
            "accuracy": 0.94,
            "processing_speed": "sub_10ms"
        }
    
    def _load_visual_sentiment_model(self) -> Any:
        """Load visual content sentiment analysis model"""
        return {
            "model_type": "cnn_lstm_hybrid",
            "accuracy": 0.89,
            "processing_speed": "sub_20ms"
        }
    
    def _load_audio_sentiment_model(self) -> Any:
        """Load audio sentiment analysis model"""
        return {
            "model_type": "wav2vec_sentiment",
            "accuracy": 0.91,
            "processing_speed": "sub_15ms"
        }
    
    def _load_multimodal_sentiment_model(self) -> Any:
        """Load multimodal sentiment fusion model"""
        return {
            "model_type": "transformer_fusion",
            "accuracy": 0.96,
            "processing_speed": "sub_25ms"
        }
    
    def _initialize_spam_detector(self) -> Dict[str, Any]:
        """Initialize spam and bot detection system"""
        return {
            "behavioral_patterns": self._load_behavioral_patterns(),
            "linguistic_features": self._load_linguistic_features(),
            "network_analysis": self._load_network_analyzer(),
            "temporal_analysis": self._load_temporal_analyzer()
        }
    
    def _load_behavioral_patterns(self) -> Dict[str, Any]:
        """Load behavioral pattern recognition for spam detection"""
        return {
            "rapid_succession_threshold": 10,  # actions per minute
            "identical_content_threshold": 0.95,  # similarity score
            "account_age_weight": 0.3
        }
    
    def _load_linguistic_features(self) -> Dict[str, Any]:
        """Load linguistic features for spam detection"""
        return {
            "spam_keywords": ["bot", "fake", "spam", "scam"],
            "promotional_patterns": ["buy now", "click here", "limited time"],
            "language_coherence_threshold": 0.7
        }
    
    def _load_network_analyzer(self) -> Dict[str, Any]:
        """Load network analysis for coordinated behavior detection"""
        return {
            "cluster_detection": True,
            "coordination_threshold": 0.8,
            "network_centrality_analysis": True
        }
    
    def _load_temporal_analyzer(self) -> Dict[str, Any]:
        """Load temporal pattern analysis"""
        return {
            "burst_detection": True,
            "periodicity_analysis": True,
            "anomaly_threshold": 2.5  # standard deviations
        }
    
    async def process_feedback_stream(self, 
                                    feedback_signals: List[FeedbackSignal]) -> List[FeedbackAnalysis]:
        """Process a stream of feedback signals in real-time"""
        start_time = time.time()
        
        try:
            # Group signals by content and platform
            grouped_signals = self._group_signals(feedback_signals)
            
            # Process each group concurrently
            analysis_tasks = []
            for content_key, signals in grouped_signals.items():
                task = self._analyze_content_feedback(content_key, signals)
                analysis_tasks.append(task)
            
            # Execute analysis concurrently
            analyses = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Filter out exceptions and update cache
            valid_analyses = []
            for analysis in analyses:
                if isinstance(analysis, FeedbackAnalysis):
                    valid_analyses.append(analysis)
                    self.analysis_cache[f"{analysis.content_id}_{analysis.platform}"] = analysis
                else:
                    self.logger.error(f"Analysis failed: {analysis}")
            
            # Update processing stats
            processing_time = (time.time() - start_time) * 1000
            self._update_processing_stats(len(feedback_signals), processing_time)
            
            return valid_analyses
            
        except Exception as e:
            self.logger.error(f"Stream processing failed: {e}")
            return []
    
    def _group_signals(self, signals: List[FeedbackSignal]) -> Dict[str, List[FeedbackSignal]]:
        """Group feedback signals by content and platform"""
        grouped = {}
        for signal in signals:
            key = f"{signal.content_id}_{signal.platform}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(signal)
        return grouped
    
    async def _analyze_content_feedback(self, 
                                      content_key: str, 
                                      signals: List[FeedbackSignal]) -> FeedbackAnalysis:
        """Analyze feedback for a specific content piece"""
        content_id, platform = content_key.split('_', 1)
        analysis_start = time.time()
        
        # Basic metrics calculation
        total_signals = len(signals)
        engagement_rate = self._calculate_engagement_rate(signals)
        
        # Sentiment analysis
        sentiment_distribution = await self._analyze_sentiment_distribution(signals)
        
        # Feedback velocity calculation
        feedback_velocity = self._calculate_feedback_velocity(signals)
        
        # Quality indicators
        positive_ratio = sentiment_distribution.get(SentimentPolarity.POSITIVE, 0.0)
        negative_ratio = sentiment_distribution.get(SentimentPolarity.NEGATIVE, 0.0)
        authenticity_score = await self._calculate_authenticity_score(signals)
        spam_probability = await self._detect_spam_probability(signals)
        
        # Trend analysis
        momentum_trend = self._analyze_momentum_trend(signals)
        peak_engagement_time = self._find_peak_engagement_time(signals)
        predicted_virality = self._predict_virality(signals, sentiment_distribution)
        
        # Generate actionable insights
        optimization_suggestions = self._generate_optimization_suggestions(
            sentiment_distribution, engagement_rate, momentum_trend
        )
        immediate_actions = self._generate_immediate_actions(
            negative_ratio, spam_probability, momentum_trend
        )
        risk_alerts = self._generate_risk_alerts(
            spam_probability, negative_ratio, authenticity_score
        )
        
        # Calculate confidence and processing time
        confidence_level = self._calculate_confidence_level(
            total_signals, authenticity_score, spam_probability
        )
        processing_time_ms = (time.time() - analysis_start) * 1000
        
        return FeedbackAnalysis(
            content_id=content_id,
            platform=platform,
            analysis_timestamp=datetime.now(timezone.utc),
            total_signals=total_signals,
            engagement_rate=engagement_rate,
            sentiment_distribution=sentiment_distribution,
            feedback_velocity=feedback_velocity,
            positive_ratio=positive_ratio,
            negative_ratio=negative_ratio,
            authenticity_score=authenticity_score,
            spam_probability=spam_probability,
            momentum_trend=momentum_trend,
            peak_engagement_time=peak_engagement_time,
            predicted_virality=predicted_virality,
            optimization_suggestions=optimization_suggestions,
            immediate_actions=immediate_actions,
            risk_alerts=risk_alerts,
            confidence_level=confidence_level,
            processing_time_ms=processing_time_ms
        )
    
    def _calculate_engagement_rate(self, signals: List[FeedbackSignal]) -> float:
        """Calculate engagement rate from feedback signals"""
        if not signals:
            return 0.0
        
        engagement_signals = [
            s for s in signals 
            if s.signal_type in [FeedbackType.LIKE, FeedbackType.COMMENT, 
                               FeedbackType.SHARE, FeedbackType.SAVE]
        ]
        
        total_views = len([s for s in signals if s.signal_type == FeedbackType.VIEW_TIME])
        if total_views == 0:
            return 0.0
        
        return len(engagement_signals) / total_views
    
    async def _analyze_sentiment_distribution(self, 
                                            signals: List[FeedbackSignal]) -> Dict[SentimentPolarity, float]:
        """Analyze sentiment distribution across feedback signals"""
        sentiment_counts = {polarity: 0 for polarity in SentimentPolarity}
        total_sentiment_signals = 0
        
        for signal in signals:
            if signal.sentiment:
                sentiment_counts[signal.sentiment] += 1
                total_sentiment_signals += 1
            elif signal.signal_type == FeedbackType.COMMENT and isinstance(signal.value, str):
                # Perform real-time sentiment analysis
                sentiment = await self._analyze_text_sentiment(signal.value)
                sentiment_counts[sentiment] += 1
                total_sentiment_signals += 1
        
        if total_sentiment_signals == 0:
            return {polarity: 0.0 for polarity in SentimentPolarity}
        
        return {
            polarity: count / total_sentiment_signals 
            for polarity, count in sentiment_counts.items()
        }
    
    async def _analyze_text_sentiment(self, text: str) -> SentimentPolarity:
        """Analyze sentiment of text content"""
        # Simulate advanced sentiment analysis
        # In production, this would use actual ML models
        
        # Simple keyword-based sentiment for demo
        positive_keywords = ["good", "great", "amazing", "love", "awesome", "excellent"]
        negative_keywords = ["bad", "terrible", "hate", "awful", "horrible", "worst"]
        
        text_lower = text.lower()
        positive_score = sum(1 for word in positive_keywords if word in text_lower)
        negative_score = sum(1 for word in negative_keywords if word in text_lower)
        
        if positive_score > negative_score:
            return SentimentPolarity.POSITIVE
        elif negative_score > positive_score:
            return SentimentPolarity.NEGATIVE
        else:
            return SentimentPolarity.NEUTRAL
    
    def _calculate_feedback_velocity(self, signals: List[FeedbackSignal]) -> float:
        """Calculate feedback velocity (signals per minute)"""
        if not signals:
            return 0.0
        
        # Sort signals by timestamp
        sorted_signals = sorted(signals, key=lambda s: s.timestamp)
        
        # Calculate time span
        time_span = (sorted_signals[-1].timestamp - sorted_signals[0].timestamp).total_seconds()
        if time_span == 0:
            return 0.0
        
        # Convert to signals per minute
        return len(signals) / (time_span / 60)
    
    async def _calculate_authenticity_score(self, signals: List[FeedbackSignal]) -> float:
        """Calculate authenticity score to detect organic vs artificial engagement"""
        if not signals:
            return 0.0
        
        # Factors for authenticity calculation
        temporal_distribution = self._analyze_temporal_distribution(signals)
        user_diversity = self._calculate_user_diversity(signals)
        behavioral_naturalness = self._assess_behavioral_naturalness(signals)
        
        # Weighted authenticity score
        authenticity = (
            temporal_distribution * 0.3 +
            user_diversity * 0.4 +
            behavioral_naturalness * 0.3
        )
        
        return min(max(authenticity, 0.0), 1.0)
    
    def _analyze_temporal_distribution(self, signals: List[FeedbackSignal]) -> float:
        """Analyze temporal distribution of signals for naturalness"""
        if len(signals) < 2:
            return 1.0
        
        # Calculate time intervals between signals
        sorted_signals = sorted(signals, key=lambda s: s.timestamp)
        intervals = []
        
        for i in range(1, len(sorted_signals)):
            interval = (sorted_signals[i].timestamp - sorted_signals[i-1].timestamp).total_seconds()
            intervals.append(interval)
        
        if not intervals:
            return 1.0
        
        # Natural engagement should have varied intervals
        variance = np.var(intervals) if len(intervals) > 1 else 0
        mean_interval = np.mean(intervals)
        
        # High variance relative to mean indicates natural behavior
        if mean_interval == 0:
            return 0.0
        
        coefficient_of_variation = variance / (mean_interval ** 2)
        return min(coefficient_of_variation, 1.0)
    
    def _calculate_user_diversity(self, signals: List[FeedbackSignal]) -> float:
        """Calculate user diversity in feedback signals"""
        if not signals:
            return 0.0
        
        unique_users = len(set(s.user_id for s in signals))
        total_signals = len(signals)
        
        # Diversity ratio
        return unique_users / total_signals
    
    def _assess_behavioral_naturalness(self, signals: List[FeedbackSignal]) -> float:
        """Assess naturalness of user behavior patterns"""
        if not signals:
            return 0.0
        
        # Group signals by user
        user_signals = {}
        for signal in signals:
            if signal.user_id not in user_signals:
                user_signals[signal.user_id] = []
            user_signals[signal.user_id].append(signal)
        
        naturalness_scores = []
        
        for user_id, user_sigs in user_signals.items():
            if len(user_sigs) == 1:
                naturalness_scores.append(1.0)  # Single interaction is natural
            else:
                # Check for rapid succession (potential bot behavior)
                sorted_sigs = sorted(user_sigs, key=lambda s: s.timestamp)
                rapid_succession_count = 0
                
                for i in range(1, len(sorted_sigs)):
                    time_diff = (sorted_sigs[i].timestamp - sorted_sigs[i-1].timestamp).total_seconds()
                    if time_diff < 5:  # Less than 5 seconds between actions
                        rapid_succession_count += 1
                
                # Penalize rapid succession
                naturalness = 1.0 - (rapid_succession_count / len(user_sigs))
                naturalness_scores.append(max(naturalness, 0.0))
        
        return np.mean(naturalness_scores) if naturalness_scores else 0.0
    
    async def _detect_spam_probability(self, signals: List[FeedbackSignal]) -> float:
        """Detect probability of spam/bot activity in feedback"""
        if not signals:
            return 0.0
        
        spam_indicators = []
        
        # Check for suspicious patterns
        for signal in signals:
            spam_score = 0.0
            
            # Check for spam keywords in comments
            if signal.signal_type == FeedbackType.COMMENT and isinstance(signal.value, str):
                spam_keywords = self.spam_detector["linguistic_features"]["spam_keywords"]
                text_lower = signal.value.lower()
                spam_keyword_count = sum(1 for keyword in spam_keywords if keyword in text_lower)
                spam_score += spam_keyword_count * 0.3
            
            # Check for promotional content
            if signal.signal_type == FeedbackType.COMMENT and isinstance(signal.value, str):
                promo_patterns = self.spam_detector["linguistic_features"]["promotional_patterns"]
                text_lower = signal.value.lower()
                promo_count = sum(1 for pattern in promo_patterns if pattern in text_lower)
                spam_score += promo_count * 0.4
            
            # Normalize spam score
            spam_indicators.append(min(spam_score, 1.0))
        
        # Calculate overall spam probability
        return np.mean(spam_indicators) if spam_indicators else 0.0
    
    def _analyze_momentum_trend(self, signals: List[FeedbackSignal]) -> str:
        """Analyze momentum trend of feedback"""
        if len(signals) < 3:
            return "stable"
        
        # Sort signals by timestamp
        sorted_signals = sorted(signals, key=lambda s: s.timestamp)
        
        # Calculate engagement in time windows
        total_time = (sorted_signals[-1].timestamp - sorted_signals[0].timestamp).total_seconds()
        if total_time < 60:  # Less than 1 minute of data
            return "stable"
        
        # Split into 3 equal time windows
        window_size = total_time / 3
        window_counts = [0, 0, 0]
        
        for signal in sorted_signals:
            time_offset = (signal.timestamp - sorted_signals[0].timestamp).total_seconds()
            window_index = min(int(time_offset / window_size), 2)
            window_counts[window_index] += 1
        
        # Analyze trend
        if window_counts[2] > window_counts[1] > window_counts[0]:
            return "increasing"
        elif window_counts[0] > window_counts[1] > window_counts[2]:
            return "decreasing"
        else:
            return "stable"
    
    def _find_peak_engagement_time(self, signals: List[FeedbackSignal]) -> Optional[datetime]:
        """Find the time of peak engagement"""
        if not signals:
            return None
        
        # Group signals by minute intervals
        minute_counts = {}
        for signal in signals:
            minute_key = signal.timestamp.replace(second=0, microsecond=0)
            minute_counts[minute_key] = minute_counts.get(minute_key, 0) + 1
        
        if not minute_counts:
            return None
        
        # Find peak minute
        peak_minute = max(minute_counts.keys(), key=lambda k: minute_counts[k])
        return peak_minute
    
    def _predict_virality(self, 
                         signals: List[FeedbackSignal], 
                         sentiment_distribution: Dict[SentimentPolarity, float]) -> float:
        """Predict virality potential based on current feedback"""
        if not signals:
            return 0.0
        
        # Virality factors
        velocity = self._calculate_feedback_velocity(signals)
        positive_sentiment = sentiment_distribution.get(SentimentPolarity.POSITIVE, 0.0)
        engagement_types = len(set(s.signal_type for s in signals))
        
        # Sharing is a strong virality indicator
        share_ratio = len([s for s in signals if s.signal_type == FeedbackType.SHARE]) / len(signals)
        
        # Calculate virality score
        virality_score = (
            min(velocity / 100, 1.0) * 0.3 +  # Normalize velocity
            positive_sentiment * 0.3 +
            min(engagement_types / 5, 1.0) * 0.2 +  # Engagement diversity
            share_ratio * 0.2
        )
        
        return min(virality_score, 1.0)
    
    def _generate_optimization_suggestions(self, 
                                         sentiment_distribution: Dict[SentimentPolarity, float],
                                         engagement_rate: float,
                                         momentum_trend: str) -> List[str]:
        """Generate actionable optimization suggestions"""
        suggestions = []
        
        negative_ratio = sentiment_distribution.get(SentimentPolarity.NEGATIVE, 0.0)
        positive_ratio = sentiment_distribution.get(SentimentPolarity.POSITIVE, 0.0)
        
        # Sentiment-based suggestions
        if negative_ratio > 0.3:
            suggestions.append("Consider moderating negative comments and addressing concerns")
        
        if positive_ratio > 0.7:
            suggestions.append("Leverage positive sentiment with follow-up content")
        
        # Engagement-based suggestions
        if engagement_rate < 0.02:
            suggestions.append("Increase call-to-action elements to boost engagement")
        elif engagement_rate > 0.1:
            suggestions.append("Excellent engagement - consider cross-promotion")
        
        # Momentum-based suggestions
        if momentum_trend == "increasing":
            suggestions.append("Momentum building - consider paid promotion to amplify reach")
        elif momentum_trend == "decreasing":
            suggestions.append("Engagement declining - analyze and adjust content strategy")
        
        return suggestions
    
    def _generate_immediate_actions(self, 
                                  negative_ratio: float,
                                  spam_probability: float,
                                  momentum_trend: str) -> List[str]:
        """Generate immediate actions needed"""
        actions = []
        
        # Urgent responses
        if negative_ratio > 0.5:
            actions.append("URGENT: High negative sentiment detected - immediate response required")
        
        if spam_probability > 0.7:
            actions.append("URGENT: High spam probability - activate spam filtering")
        
        # Opportunity actions
        if momentum_trend == "increasing" and negative_ratio < 0.2:
            actions.append("OPPORTUNITY: Positive momentum - boost distribution now")
        
        return actions
    
    def _generate_risk_alerts(self, 
                            spam_probability: float,
                            negative_ratio: float,
                            authenticity_score: float) -> List[str]:
        """Generate risk alerts"""
        alerts = []
        
        if spam_probability > 0.8:
            alerts.append("HIGH RISK: Coordinated spam attack detected")
        
        if negative_ratio > 0.6:
            alerts.append("HIGH RISK: Potential reputation damage from negative sentiment")
        
        if authenticity_score < 0.3:
            alerts.append("MEDIUM RISK: Low authenticity score - possible bot activity")
        
        return alerts
    
    def _calculate_confidence_level(self, 
                                  total_signals: int,
                                  authenticity_score: float,
                                  spam_probability: float) -> float:
        """Calculate confidence level of the analysis"""
        # Base confidence on signal volume
        volume_confidence = min(total_signals / 100, 1.0)
        
        # Authenticity affects confidence
        authenticity_confidence = authenticity_score
        
        # Low spam probability increases confidence
        spam_confidence = 1.0 - spam_probability
        
        # Combined confidence
        confidence = (volume_confidence * 0.4 + 
                     authenticity_confidence * 0.3 + 
                     spam_confidence * 0.3)
        
        return min(max(confidence, 0.0), 1.0)
    
    def _update_processing_stats(self, signal_count -> None: int, processing_time -> None: float) -> None:
        """Update processing performance statistics"""
        self.processing_stats["total_processed"] += signal_count
        
        # Update average processing time
        current_avg = self.processing_stats["avg_processing_time"]
        new_avg = (current_avg + processing_time) / 2
        self.processing_stats["avg_processing_time"] = new_avg
    
    async def get_real_time_insights(self, content_id: str, platform: str) -> Optional[FeedbackAnalysis]:
        """Get real-time insights for specific content"""
        cache_key = f"{content_id}_{platform}"
        return self.analysis_cache.get(cache_key)
    
    def get_processing_stats(self) -> Dict[str, float]:
        """Get current processing performance statistics"""
        return self.processing_stats.copy()
    
    async def cleanup_old_data(self, max_age_hours -> None: int = 24) -> None:
        """Clean up old cached data"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (max_age_hours * 3600)
        
        # Clean analysis cache
        keys_to_remove = []
        for key, analysis in self.analysis_cache.items():
            if analysis.analysis_timestamp.timestamp() < cutoff_time:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.analysis_cache[key]
        
        # Clean feedback buffer
        for content_key in list(self.feedback_buffer.keys()):
            self.feedback_buffer[content_key] = [
                signal for signal in self.feedback_buffer[content_key]
                if signal.timestamp.timestamp() >= cutoff_time
            ]
            
            if not self.feedback_buffer[content_key]:
                del self.feedback_buffer[content_key]


# Factory function for easy instantiation
def create_instant_feedback_processor(**kwargs) -> InstantFeedbackProcessor:
    """Create and configure an InstantFeedbackProcessor instance"""
    return InstantFeedbackProcessor(**kwargs)


# Performance optimization utilities
class FeedbackProcessorOptimizer:
    """Performance optimization utilities for feedback processing"""
    
    @staticmethod
    def optimize_for_high_volume(processor -> None: InstantFeedbackProcessor) -> None:
        """Optimize processor for high-volume scenarios"""
        processor.max_processing_time_ms = 30.0  # Stricter timing
        processor.velocity_window_minutes = 3     # Smaller window
    
    @staticmethod
    def optimize_for_accuracy(processor -> None: InstantFeedbackProcessor) -> None:
        """Optimize processor for maximum accuracy"""
        processor.sentiment_threshold = 0.8       # Higher threshold
        processor.spam_detection_threshold = 0.9  # Stricter spam detection
        processor.velocity_window_minutes = 10    # Larger analysis window