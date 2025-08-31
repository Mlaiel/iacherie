"""Sentiment Analysis Agent - Advanced Sentiment and Emotion Detection

This agent provides comprehensive sentiment analysis for content and user interactions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .core.sentiment_analysis_agent import SentimentAnalysisAgent
from .models.sentiment_models import (
    SentimentAnalysisRequest,
    SentimentAnalysisResult,
    EmotionProfile,
    SentimentTrend
)

__all__ = [
    'SentimentAnalysisAgent',
    'SentimentAnalysisRequest',
    'SentimentAnalysisResult', 
    'EmotionProfile',
    'SentimentTrend'
]

__version__ = "1.0.0"