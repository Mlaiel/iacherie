"""Sentiment Monitor - Real-time Crisis Sentiment Analysis

Advanced sentiment monitoring system for crisis detection and reputation management.
Provides real-time sentiment analysis across multiple platforms and languages.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json

# AI/ML imports
import pandas as pd
import numpy as np
from textblob import TextBlob

# Core imports
from ..config.crisis_configs import CrisisConfiguration


class SentimentScore(Enum):
    """Sentiment scoring levels"""
    EXTREMELY_NEGATIVE = -1.0
    VERY_NEGATIVE = -0.75
    NEGATIVE = -0.5
    SLIGHTLY_NEGATIVE = -0.25
    NEUTRAL = 0.0
    SLIGHTLY_POSITIVE = 0.25
    POSITIVE = 0.5
    VERY_POSITIVE = 0.75
    EXTREMELY_POSITIVE = 1.0


@dataclass
class SentimentAnalysis:
    """Sentiment analysis result"""
    platform: str
    content_id: str
    text: str
    sentiment_score: float
    sentiment_label: str
    confidence: float
    language: str
    keywords: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def is_crisis_indicator(self) -> bool:
        """Check if sentiment indicates potential crisis"""
        return self.sentiment_score <= -0.6 and self.confidence >= 0.7


@dataclass
class SentimentTrend:
    """Sentiment trend analysis"""
    platform: str
    time_period: str
    sentiment_scores: List[float]
    average_sentiment: float
    trend_direction: str  # 'improving', 'declining', 'stable'
    volatility: float
    crisis_probability: float


class SentimentMonitor:
    """Advanced sentiment monitoring system for crisis management"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Sentiment analysis settings
        self.crisis_config = CrisisConfiguration()
        self.sentiment_threshold = self.config.get('crisis_sentiment_threshold', -0.6)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        
        # Platform monitoring
        self.platforms = self.config.get('platforms', [
            'twitter', 'facebook', 'instagram', 'youtube', 'tiktok',
            'linkedin', 'reddit', 'news_sites', 'blogs', 'forums'
        ])
        
        # Sentiment data storage
        self.sentiment_history: Dict[str, List[SentimentAnalysis]] = {}
        self.real_time_scores: Dict[str, float] = {}
        
        # Analysis settings
        self.languages_supported = ['en', 'fr', 'de', 'es', 'ar', 'zh']
        self.update_interval = self.config.get('update_interval', 300)  # 5 minutes
        
        self.logger.info("SentimentMonitor initialized with crisis monitoring")
    
    async def analyze_sentiment(self, text: str, platform: str, content_id: str) -> SentimentAnalysis:
        """Analyze sentiment of text content"""
        try:
            # Basic sentiment analysis using TextBlob (can be enhanced with advanced models)
            blob = TextBlob(text)
            
            # Calculate sentiment
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Determine sentiment label
            if polarity >= 0.6:
                label = "very_positive"
            elif polarity >= 0.2:
                label = "positive"
            elif polarity >= -0.2:
                label = "neutral"
            elif polarity >= -0.6:
                label = "negative"
            else:
                label = "very_negative"
            
            # Extract keywords and entities
            keywords = self._extract_keywords(text)
            entities = self._extract_entities(text)
            
            # Calculate confidence (based on subjectivity and text length)
            confidence = min(1.0, (1 - subjectivity) * (len(text.split()) / 100))
            
            analysis = SentimentAnalysis(
                platform=platform,
                content_id=content_id,
                text=text[:500],  # Truncate for storage
                sentiment_score=polarity,
                sentiment_label=label,
                confidence=confidence,
                language=blob.detect_language() if hasattr(blob, 'detect_language') else 'en',
                keywords=keywords,
                entities=entities
            )
            
            # Store analysis
            if platform not in self.sentiment_history:
                self.sentiment_history[platform] = []
            
            self.sentiment_history[platform].append(analysis)
            self.real_time_scores[platform] = polarity
            
            # Log crisis indicators
            if analysis.is_crisis_indicator():
                self.logger.warning(f"Crisis sentiment detected on {platform}: {polarity:.3f}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            raise
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        blob = TextBlob(text)
        # Get noun phrases as keywords
        keywords = list(blob.noun_phrases)[:10]  # Top 10 keywords
        return [kw.lower() for kw in keywords if len(kw) > 2]
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text"""
        # Simple implementation - can be enhanced with spaCy or other NER tools
        blob = TextBlob(text)
        entities = []
        
        # Look for capitalized words as potential entities
        words = text.split()
        for word in words:
            if word[0].isupper() and len(word) > 2 and word.isalpha():
                entities.append(word)
        
        return list(set(entities))[:5]  # Unique entities, max 5
    
    async def monitor_platform_sentiment(self, platform: str, duration_hours: int = 24) -> SentimentTrend:
        """Monitor sentiment trends for a specific platform"""
        try:
            # Get recent sentiment data
            cutoff_time = datetime.utcnow() - timedelta(hours=duration_hours)
            
            if platform not in self.sentiment_history:
                return SentimentTrend(
                    platform=platform,
                    time_period=f"{duration_hours}h",
                    sentiment_scores=[],
                    average_sentiment=0.0,
                    trend_direction="stable",
                    volatility=0.0,
                    crisis_probability=0.0
                )
            
            # Filter recent sentiments
            recent_sentiments = [
                s for s in self.sentiment_history[platform]
                if s.timestamp >= cutoff_time
            ]
            
            if not recent_sentiments:
                return SentimentTrend(
                    platform=platform,
                    time_period=f"{duration_hours}h",
                    sentiment_scores=[],
                    average_sentiment=0.0,
                    trend_direction="stable",
                    volatility=0.0,
                    crisis_probability=0.0
                )
            
            # Calculate trend metrics
            scores = [s.sentiment_score for s in recent_sentiments]
            avg_sentiment = np.mean(scores)
            volatility = np.std(scores)
            
            # Determine trend direction
            if len(scores) >= 5:
                recent_half = scores[len(scores)//2:]
                earlier_half = scores[:len(scores)//2]
                
                if np.mean(recent_half) > np.mean(earlier_half) + 0.1:
                    trend_direction = "improving"
                elif np.mean(recent_half) < np.mean(earlier_half) - 0.1:
                    trend_direction = "declining"
                else:
                    trend_direction = "stable"
            else:
                trend_direction = "stable"
            
            # Calculate crisis probability
            negative_count = sum(1 for s in scores if s <= -0.5)
            crisis_probability = min(1.0, negative_count / len(scores))
            
            return SentimentTrend(
                platform=platform,
                time_period=f"{duration_hours}h",
                sentiment_scores=scores,
                average_sentiment=avg_sentiment,
                trend_direction=trend_direction,
                volatility=volatility,
                crisis_probability=crisis_probability
            )
            
        except Exception as e:
            self.logger.error(f"Platform sentiment monitoring failed for {platform}: {e}")
            raise
    
    async def get_real_time_sentiment_overview(self) -> Dict[str, Any]:
        """Get real-time sentiment overview across all platforms"""
        try:
            overview = {
                'timestamp': datetime.utcnow().isoformat(),
                'platforms': {},
                'overall_sentiment': 0.0,
                'crisis_platforms': [],
                'alerts': []
            }
            
            platform_sentiments = []
            
            for platform in self.platforms:
                if platform in self.real_time_scores:
                    sentiment = self.real_time_scores[platform]
                    platform_sentiments.append(sentiment)
                    
                    overview['platforms'][platform] = {
                        'sentiment_score': sentiment,
                        'status': self._get_sentiment_status(sentiment),
                        'last_updated': datetime.utcnow().isoformat()
                    }
                    
                    # Check for crisis
                    if sentiment <= self.sentiment_threshold:
                        overview['crisis_platforms'].append(platform)
                        overview['alerts'].append({
                            'platform': platform,
                            'type': 'negative_sentiment',
                            'severity': 'high' if sentiment <= -0.8 else 'medium',
                            'message': f"Negative sentiment detected: {sentiment:.3f}"
                        })
            
            # Calculate overall sentiment
            if platform_sentiments:
                overview['overall_sentiment'] = np.mean(platform_sentiments)
            
            return overview
            
        except Exception as e:
            self.logger.error(f"Real-time sentiment overview failed: {e}")
            raise
    
    def _get_sentiment_status(self, score: float) -> str:
        """Get human-readable sentiment status"""
        if score >= 0.6:
            return "very_positive"
        elif score >= 0.2:
            return "positive"
        elif score >= -0.2:
            return "neutral"
        elif score >= -0.6:
            return "negative"
        else:
            return "very_negative"
    
    async def generate_sentiment_report(self, platforms: Optional[List[str]] = None, 
                                       duration_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive sentiment analysis report"""
        try:
            platforms = platforms or self.platforms
            report = {
                'report_id': f"sentiment_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'generated_at': datetime.utcnow().isoformat(),
                'duration_hours': duration_hours,
                'platforms_analyzed': platforms,
                'summary': {},
                'platform_details': {},
                'recommendations': []
            }
            
            all_trends = []
            
            # Analyze each platform
            for platform in platforms:
                trend = await self.monitor_platform_sentiment(platform, duration_hours)
                all_trends.append(trend)
                
                report['platform_details'][platform] = {
                    'average_sentiment': trend.average_sentiment,
                    'trend_direction': trend.trend_direction,
                    'volatility': trend.volatility,
                    'crisis_probability': trend.crisis_probability,
                    'total_mentions': len(trend.sentiment_scores)
                }
            
            # Generate summary
            if all_trends:
                avg_sentiments = [t.average_sentiment for t in all_trends if t.sentiment_scores]
                if avg_sentiments:
                    report['summary'] = {
                        'overall_sentiment': np.mean(avg_sentiments),
                        'most_positive_platform': max(all_trends, key=lambda x: x.average_sentiment).platform,
                        'most_negative_platform': min(all_trends, key=lambda x: x.average_sentiment).platform,
                        'highest_crisis_risk': max(all_trends, key=lambda x: x.crisis_probability).platform,
                        'platforms_at_risk': [t.platform for t in all_trends if t.crisis_probability > 0.3]
                    }
            
            # Generate recommendations
            report['recommendations'] = self._generate_recommendations(all_trends)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Sentiment report generation failed: {e}")
            raise
    
    def _generate_recommendations(self, trends: List[SentimentTrend]) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on sentiment trends"""
        recommendations = []
        
        for trend in trends:
            if trend.crisis_probability > 0.5:
                recommendations.append({
                    'platform': trend.platform,
                    'priority': 'high',
                    'action': 'immediate_response',
                    'description': f"High crisis probability on {trend.platform}. Activate crisis response protocol."
                })
            
            elif trend.trend_direction == 'declining' and trend.average_sentiment < -0.3:
                recommendations.append({
                    'platform': trend.platform,
                    'priority': 'medium',
                    'action': 'monitoring_increase',
                    'description': f"Declining sentiment on {trend.platform}. Increase monitoring frequency."
                })
            
            elif trend.volatility > 0.5:
                recommendations.append({
                    'platform': trend.platform,
                    'priority': 'medium',
                    'action': 'stabilization',
                    'description': f"High sentiment volatility on {trend.platform}. Consider stabilizing communications."
                })
        
        return recommendations
    
    async def get_sentiment_score(self, text: str, platform: str = None) -> float:
        """
        Get numerical sentiment score for given text
        
        Args:
            text: Text to analyze for sentiment
            platform: Optional platform context for platform-specific analysis
            
        Returns:
            float: Sentiment score between -1.0 (very negative) and 1.0 (very positive)
        """
        try:
            if not text or not text.strip():
                self.logger.warning("Empty text provided for sentiment analysis")
                return 0.0
            
            # Use TextBlob for basic sentiment analysis
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Apply platform-specific adjustments if provided
            if platform:
                # Platform-specific sentiment adjustments
                platform_weights = {
                    'twitter': 1.2,  # Twitter tends to be more emotional
                    'linkedin': 0.8,  # LinkedIn tends to be more professional/neutral
                    'instagram': 1.1,  # Instagram slightly more positive
                    'facebook': 1.0,  # Baseline
                    'tiktok': 1.3,   # TikTok tends to be more extreme
                    'youtube': 1.0   # Baseline
                }
                
                weight = platform_weights.get(platform.lower(), 1.0)
                polarity = polarity * weight
                
                # Ensure we stay within bounds
                polarity = max(-1.0, min(1.0, polarity))
            
            self.logger.debug(f"Sentiment score calculated: {polarity} for platform: {platform}")
            return polarity
            
        except Exception as e:
            self.logger.error(f"Sentiment score calculation failed: {e}")
            return 0.0


# Export classes
__all__ = [
    'SentimentMonitor',
    'SentimentAnalysis',
    'SentimentTrend',
    'SentimentScore'
]