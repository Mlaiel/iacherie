"""📈 Trend Analyzer - IA Influencer Agent
=====================================

Advanced trend analysis system for identifying viral content patterns,
market opportunities, and predictive analytics for content creators.

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE PROHIBITED
====================================================
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel - All rights reserved
WARNING: Any unauthorized copying, modification, distribution or use of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime, timedelta
import json
import hashlib
import re

# ML/AI Libraries
import torch
import torch.nn as nn
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import DBSCAN, KMeans
from transformers import AutoModel, AutoTokenizer, pipeline
import pandas as pd
from scipy import stats
import networkx as nx

# Time series analysis
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose

# Core Dependencies
from ..analytics.social_analytics import SocialAnalytics
from ..processors.content_processor import ContentProcessor
from ..crawlers.social_crawler import SocialCrawler
from ..storage.time_series_storage import TimeSeriesStorage
from ..cache.redis_cache import RedisCache


class TrendType(Enum):
    """
Types of trends"""

    VIRAL_CONTENT = "viral_content"
    HASHTAG_TREND = "hashtag_trend"
    TOPIC_TREND = "topic_trend"
    PLATFORM_TREND = "platform_trend"
    FORMAT_TREND = "format_trend"
    MUSIC_TREND = "music_trend"
    CHALLENGE_TREND = "challenge_trend"
    STYLE_TREND = "style_trend"


class TrendStage(Enum):
    """Trend lifecycle stages"""

    EMERGING = "emerging"
    GROWING = "growing"
    PEAK = "peak"
    DECLINING = "declining"
    DEAD = "dead"


class TrendScope(Enum):
    """Trend geographical scope"""

    LOCAL = "local"
    REGIONAL = "regional"
    NATIONAL = "national"
    GLOBAL = "global"


@dataclass
class TrendData:
    """Trend data structure"""
    trend_id: str
    trend_type: TrendType
    trend_stage: TrendStage
    trend_scope: TrendScope
    title: str
    description: str
    keywords: List[str]
    hashtags: List[str]
    momentum_score: float
    viral_probability: float
    growth_rate: float
    peak_prediction: datetime
    decay_prediction: datetime
    platforms: List[str]
    demographics: Dict[str, Any]
    engagement_metrics: Dict[str, float]
    content_examples: List[str]
    creator_count: int
    total_engagement: int
    geographic_distribution: Dict[str, float]
    related_trends: List[str]
    monetization_potential: float
    risk_factors: List[str]
    opportunities: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ViralPrediction:
    """
Viral content prediction"""
    prediction_id: str
    content_id: str
    viral_probability: float
    estimated_reach: int
    peak_time_hours: float
    engagement_prediction: Dict[str, float]
    platform_performance: Dict[str, float]
    success_factors: List[str]
    risk_factors: List[str]
    optimization_suggestions: List[str]
    confidence_score: float
    prediction_model: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MarketIntelligence:
    """
Market intelligence data"""
    intelligence_id: str
    market_segment: str
    market_size: int
    growth_rate: float
    competition_level: str
    entry_barriers: List[str]
    key_players: List[str]
    emerging_opportunities: List[str]
    threat_analysis: List[str]
    recommended_strategies: List[str]
    investment_attractiveness: float
    time_to_market: str
    success_probability: float
    revenue_potential: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class TrendAnalyzer:
    """
    Advanced trend analysis engine for content creators
    
    Provides comprehensive trend analysis including:
    - Real-time trend detection across platforms
    - Viral content prediction algorithms
    - Market intelligence and opportunity analysis
    - Trend lifecycle tracking and prediction
    - Geographic and demographic trend mapping
    - Content optimization recommendations
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
Initialize trend analyzer"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.social_analytics = SocialAnalytics(config.get('social_analytics', {}))
        self.content_processor = ContentProcessor(config.get('content', {}))
        self.social_crawler = SocialCrawler(config.get('crawler', {}))
        self.time_series_storage = TimeSeriesStorage(config.get('time_series', {}))
        self.cache = RedisCache(config.get('redis', {}))
        
        # ML Models
        self.trend_detector = None
        self.viral_predictor = None
        self.growth_predictor = None
        self.sentiment_analyzer = None
        
        # Analysis parameters
        self.trend_threshold = config.get('trend_threshold', 0.7)
        self.viral_threshold = config.get('viral_threshold', 0.8)
        self.min_data_points = config.get('min_data_points', 100)
        self.analysis_window_hours = config.get('analysis_window_hours', 24)
        self.prediction_horizon_hours = config.get('prediction_horizon_hours', 72)
        
        # Platform weights
        self.platform_weights = config.get('platform_weights', {
            'tiktok': 0.3,
            'instagram': 0.25,
            'youtube': 0.2,
            'twitter': 0.15,
            'facebook': 0.1
        })
        
        self._initialize_models()
    
    def _initialize_models(self):
        """
Initialize ML models for trend analysis"""
        try:
            # Trend detection model
            class TrendDetector(nn.Module):
                def __init__(self, input_size: int = 100, hidden_size: int = 128):
                    super().__init__()
                    self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True, num_layers=2)
                    self.attention = nn.MultiheadAttention(hidden_size, num_heads=8)
                    self.fc1 = nn.Linear(hidden_size, 64)
                    self.fc2 = nn.Linear(64, 32)
                    self.fc3 = nn.Linear(32, 1)
                    self.dropout = nn.Dropout(0.2)
                    self.relu = nn.ReLU()
                    self.sigmoid = nn.Sigmoid()
                
                def forward(self, x):
                    # LSTM processing
                    lstm_out, _ = self.lstm(x)
                    
                    # Attention mechanism
                    attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
                    
                    # Take last output
                    x = attn_out[:, -1, :]
                    
                    # Classification layers
                    x = self.dropout(self.relu(self.fc1(x)))
                    x = self.dropout(self.relu(self.fc2(x)))
                    x = self.sigmoid(self.fc3(x))
                    
                    return x
            
            self.trend_detector = TrendDetector()
            
            # Viral prediction model
            class ViralPredictor(nn.Module):
                def __init__(self, input_size: int = 150, hidden_size: int = 256):
                    super().__init__()
                    # Content features branch
                    self.content_branch = nn.Sequential(
                        nn.Linear(50, 128),
                        nn.ReLU(),
                        nn.Dropout(0.2),
                        nn.Linear(128, 64)
                    )
                    
                    # Engagement features branch
                    self.engagement_branch = nn.Sequential(
                        nn.Linear(50, 128),
                        nn.ReLU(),
                        nn.Dropout(0.2),
                        nn.Linear(128, 64)
                    )
                    
                    # Temporal features branch
                    self.temporal_branch = nn.Sequential(
                        nn.Linear(50, 128),
                        nn.ReLU(),
                        nn.Dropout(0.2),
                        nn.Linear(128, 64)
                    )
                    
                    # Fusion layer
                    self.fusion = nn.Sequential(
                        nn.Linear(192, 128),  # 64 * 3
                        nn.ReLU(),
                        nn.Dropout(0.3),
                        nn.Linear(128, 64),
                        nn.ReLU(),
                        nn.Linear(64, 1),
                        nn.Sigmoid()
                    )
                
                def forward(self, content_features, engagement_features, temporal_features):
                    content_out = self.content_branch(content_features)
                    engagement_out = self.engagement_branch(engagement_features)
                    temporal_out = self.temporal_branch(temporal_features)
                    
                    # Concatenate features
                    fused = torch.cat([content_out, engagement_out, temporal_out], dim=1)
                    
                    # Final prediction
                    output = self.fusion(fused)
                    return output
            
            self.viral_predictor = ViralPredictor()
            
            # Growth prediction model (time series)
            self.growth_predictor = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            # Sentiment analysis pipeline
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.logger.info("Trend analysis models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing models: {e}")
            raise
    
    async def analyze_current_trends(
        self,
        platforms: List[str] = None,
        categories: List[str] = None,
        geographic_scope: TrendScope = TrendScope.GLOBAL,
        time_window_hours: int = 24,
        cultural_context: str = None,
        region: str = None
    ) -> List[TrendData]:
        """
        Analyze current trending topics and content across platforms
        
        Args:
            platforms: Specific platforms to analyze
            categories: Content categories to focus on
            geographic_scope: Geographic scope of analysis
            time_window_hours: Analysis time window
            cultural_context: Cultural context for localized trends
            region: Specific region for local trend analysis
            
        Returns:
            List of current trends with analysis
        """
        try:
            self.logger.info(f"Analyzing current trends for {time_window_hours}h window")
            
            # Get platform data
            if not platforms:
                platforms = list(self.platform_weights.keys())
            
            # Collect trending data from all platforms
            trending_data = {}
            for platform in platforms:
                platform_trends = await self._collect_platform_trends(
                    platform, categories, time_window_hours
                )
                trending_data[platform] = platform_trends
            
            # Process and analyze trends
            trends = []
            
            # Hashtag trends
            hashtag_trends = await self._analyze_hashtag_trends(trending_data)
            trends.extend(hashtag_trends)
            
            # Topic trends
            topic_trends = await self._analyze_topic_trends(trending_data)
            trends.extend(topic_trends)
            
            # Format trends
            format_trends = await self._analyze_format_trends(trending_data)
            trends.extend(format_trends)
            
            # Music/audio trends
            music_trends = await self._analyze_music_trends(trending_data)
            trends.extend(music_trends)
            
            # Challenge trends
            challenge_trends = await self._analyze_challenge_trends(trending_data)
            trends.extend(challenge_trends)
            
            # Score and rank trends
            scored_trends = await self._score_trends(trends)
            
            # Filter by geographic scope
            filtered_trends = await self._filter_by_geographic_scope(
                scored_trends, geographic_scope
            )
            
            # Sort by momentum and relevance
            filtered_trends.sort(
                key=lambda x: (x.momentum_score * x.viral_probability),
                reverse=True
            )
            
            # Cache results
            cache_key = f"current_trends:{':'.join(platforms)}:{geographic_scope.value}"
            await self.cache.set(cache_key, filtered_trends[:50], ttl=1800)
            
            self.logger.info(f"Analyzed {len(filtered_trends)} current trends")
            return filtered_trends[:30]  # Return top 30 trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing current trends: {e}")
            return []
    
    async def predict_viral_content(
        self,
        content_data: Dict[str, Any],
        creator_profile: Dict[str, Any] = None,
        target_platforms: List[str] = None
    ) -> ViralPrediction:
        """
        Predict viral potential of content before posting
        
        Args:
            content_data: Content metadata and features
            creator_profile: Creator's profile and history
            target_platforms: Platforms where content will be posted
            
        Returns:
            Viral prediction with optimization suggestions
        """
        try:
            self.logger.info(f"Predicting viral potential for content {content_data.get('content_id', 'unknown')}")
            
            # Extract features for prediction
            content_features = await self._extract_content_features(content_data)
            engagement_features = await self._extract_engagement_features(
                content_data, creator_profile
            )
            temporal_features = await self._extract_temporal_features(content_data)
            
            # Predict viral probability
            viral_probability = await self._predict_viral_probability(
                content_features, engagement_features, temporal_features
            )
            
            # Estimate reach and engagement
            estimated_reach = await self._estimate_viral_reach(
                content_data, creator_profile, viral_probability
            )
            
            # Predict peak timing
            peak_time_hours = await self._predict_peak_timing(
                content_features, temporal_features
            )
            
            # Platform-specific predictions
            platform_performance = await self._predict_platform_performance(
                content_data, target_platforms or ['instagram', 'tiktok']
            )
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(
                content_data, content_features, viral_probability
            )
            
            # Identify success and risk factors
            success_factors = await self._identify_viral_success_factors(
                content_features, engagement_features
            )
            risk_factors = await self._identify_viral_risk_factors(
                content_features, temporal_features
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_prediction_confidence(
                content_features, creator_profile
            )
            
            prediction = ViralPrediction(
                prediction_id=self._generate_id(),
                content_id=content_data.get('content_id', 'unknown'),
                viral_probability=viral_probability,
                estimated_reach=estimated_reach,
                peak_time_hours=peak_time_hours,
                engagement_prediction=await self._predict_engagement_metrics(
                    content_features, viral_probability
                ),
                platform_performance=platform_performance,
                success_factors=success_factors,
                risk_factors=risk_factors,
                optimization_suggestions=optimization_suggestions,
                confidence_score=confidence_score,
                prediction_model="neural_ensemble_v2"
            )
            
            # Cache prediction
            cache_key = f"viral_prediction:{content_data.get('content_id', 'unknown')}"
            await self.cache.set(cache_key, prediction.__dict__, ttl=3600)
            
            self.logger.info(f"Viral prediction completed: {viral_probability:.2%} probability")
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting viral content: {e}")
            return ViralPrediction(
                prediction_id=self._generate_id(),
                content_id=content_data.get('content_id', 'unknown'),
                viral_probability=0.1,
                estimated_reach=0,
                peak_time_hours=24.0,
                engagement_prediction={},
                platform_performance={},
                success_factors=[],
                risk_factors=["Prediction error"],
                optimization_suggestions=[],
                confidence_score=0.0,
                prediction_model="fallback"
            )
    
    async def _collect_platform_trends(
        self,
        platform: str,
        categories: List[str] = None,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Collect trending data from specific platform"""
        try:
            # Get trending content from platform
            trending_content = await self.social_crawler.get_trending_content(
                platform=platform,
                categories=categories,
                time_window_hours=time_window_hours,
                limit=1000
            )
            
            # Get trending hashtags
            trending_hashtags = await self.social_crawler.get_trending_hashtags(
                platform=platform,
                time_window_hours=time_window_hours,
                limit=100
            )
            
            # Get engagement metrics
            engagement_data = await self.social_analytics.get_platform_engagement_trends(
                platform=platform,
                time_window_hours=time_window_hours
            )
            
            return {
                'platform': platform,
                'trending_content': trending_content,
                'trending_hashtags': trending_hashtags,
                'engagement_data': engagement_data,
                'collection_time': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting trends from {platform}: {e}")
            return {'platform': platform, 'trending_content': [], 'trending_hashtags': [], 'engagement_data': {}}
    
    async def _analyze_hashtag_trends(self, trending_data: Dict[str, Any]) -> List[TrendData]:
        """Analyze hashtag trends across platforms"""
        hashtag_trends = []
        
        try:
            # Aggregate hashtags across platforms
            hashtag_metrics = {}
            
            for platform, data in trending_data.items():
                platform_weight = self.platform_weights.get(platform, 0.1)
                
                for hashtag_data in data.get('trending_hashtags', []):
                    hashtag = hashtag_data.get('hashtag', '').lower()
                    if not hashtag:
                        continue
                    
                    if hashtag not in hashtag_metrics:
                        hashtag_metrics[hashtag] = {
                            'total_posts': 0,
                            'total_engagement': 0,
                            'platforms': set(),
                            'growth_rate': 0,
                            'demographics': {},
                            'sentiment_score': 0,
                            'creator_count': 0
                        }
                    
                    metrics = hashtag_metrics[hashtag]
                    metrics['total_posts'] += hashtag_data.get('post_count', 0) * platform_weight
                    metrics['total_engagement'] += hashtag_data.get('engagement', 0) * platform_weight
                    metrics['platforms'].add(platform)
                    metrics['growth_rate'] += hashtag_data.get('growth_rate', 0) * platform_weight
                    metrics['creator_count'] += hashtag_data.get('creator_count', 0)
                    
                    # Aggregate demographics
                    if 'demographics' in hashtag_data:
                        for demo_key, demo_value in hashtag_data['demographics'].items():
                            if demo_key not in metrics['demographics']:
                                metrics['demographics'][demo_key] = 0
                            metrics['demographics'][demo_key] += demo_value * platform_weight
            
            # Create trend objects for significant hashtags
            for hashtag, metrics in hashtag_metrics.items():
                if metrics['total_posts'] >= self.min_data_points:
                    
                    # Calculate momentum score
                    momentum_score = self._calculate_momentum_score(
                        metrics['growth_rate'],
                        metrics['total_engagement'],
                        len(metrics['platforms'])
                    )
                    
                    # Determine trend stage
                    trend_stage = await self._determine_trend_stage(hashtag, metrics)
                    
                    # Predict viral probability
                    viral_probability = await self._calculate_viral_probability(metrics)
                    
                    # Calculate monetization potential
                    monetization_potential = await self._calculate_monetization_potential(
                        hashtag, metrics
                    )
                    
                    trend = TrendData(
                        trend_id=self._generate_id(),
                        trend_type=TrendType.HASHTAG_TREND,
                        trend_stage=trend_stage,
                        trend_scope=TrendScope.GLOBAL,  # Will be refined later
                        title=f"#{hashtag}",
                        description=f"Trending hashtag with {metrics['total_posts']:.0f} posts",
                        keywords=[hashtag],
                        hashtags=[hashtag],
                        momentum_score=momentum_score,
                        viral_probability=viral_probability,
                        growth_rate=metrics['growth_rate'],
                        peak_prediction=await self._predict_trend_peak(hashtag, metrics),
                        decay_prediction=await self._predict_trend_decay(hashtag, metrics),
                        platforms=list(metrics['platforms']),
                        demographics=metrics['demographics'],
                        engagement_metrics={
                            'total_engagement': metrics['total_engagement'],
                            'engagement_rate': metrics['total_engagement'] / max(metrics['total_posts'], 1)
                        },
                        content_examples=[],  # Would be populated with actual examples
                        creator_count=metrics['creator_count'],
                        total_engagement=int(metrics['total_engagement']),
                        geographic_distribution={},  # Would be calculated from data
                        related_trends=[],
                        monetization_potential=monetization_potential,
                        risk_factors=await self._identify_trend_risks(hashtag, metrics),
                        opportunities=await self._identify_trend_opportunities(hashtag, metrics)
                    )
                    
                    hashtag_trends.append(trend)
            
            return hashtag_trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing hashtag trends: {e}")
            return []
    
    async def _analyze_topic_trends(self, trending_data: Dict[str, Any]) -> List[TrendData]:
        """Analyze topic trends using NLP"""
        topic_trends = []
        
        try:
            # Extract and process text content
            all_content = []
            
            for platform, data in trending_data.items():
                for content in data.get('trending_content', []):
                    text = content.get('caption', '') + ' ' + content.get('description', '')
                    if text.strip():
                        all_content.append({
                            'text': text,
                            'platform': platform,
                            'engagement': content.get('engagement', 0),
                            'created_at': content.get('created_at', datetime.now())
                        })
            
            if not all_content:
                return topic_trends
            
            # Extract topics using topic modeling
            topics = await self._extract_topics_from_content(all_content)
            
            # Analyze each topic
            for topic_data in topics:
                topic_name = topic_data['topic_name']
                topic_keywords = topic_data['keywords']
                topic_score = topic_data['score']
                
                if topic_score >= self.trend_threshold:
                    # Calculate metrics for this topic
                    topic_metrics = await self._calculate_topic_metrics(
                        topic_keywords, all_content
                    )
                    
                    # Create trend object
                    trend = TrendData(
                        trend_id=self._generate_id(),
                        trend_type=TrendType.TOPIC_TREND,
                        trend_stage=await self._determine_trend_stage(topic_name, topic_metrics),
                        trend_scope=TrendScope.GLOBAL,
                        title=topic_name,
                        description=f"Trending topic with {topic_metrics['mention_count']} mentions",
                        keywords=topic_keywords,
                        hashtags=topic_metrics.get('associated_hashtags', []),
                        momentum_score=topic_score,
                        viral_probability=await self._calculate_viral_probability(topic_metrics),
                        growth_rate=topic_metrics.get('growth_rate', 0.1),
                        peak_prediction=await self._predict_trend_peak(topic_name, topic_metrics),
                        decay_prediction=await self._predict_trend_decay(topic_name, topic_metrics),
                        platforms=topic_metrics.get('platforms', []),
                        demographics=topic_metrics.get('demographics', {}),
                        engagement_metrics=topic_metrics.get('engagement_metrics', {}),
                        content_examples=topic_metrics.get('examples', []),
                        creator_count=topic_metrics.get('creator_count', 0),
                        total_engagement=topic_metrics.get('total_engagement', 0),
                        geographic_distribution={},
                        related_trends=[],
                        monetization_potential=await self._calculate_monetization_potential(
                            topic_name, topic_metrics
                        ),
                        risk_factors=await self._identify_trend_risks(topic_name, topic_metrics),
                        opportunities=await self._identify_trend_opportunities(topic_name, topic_metrics)
                    )
                    
                    topic_trends.append(trend)
            
            return topic_trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing topic trends: {e}")
            return []
    
    async def _analyze_format_trends(self, trending_data: Dict[str, Any]) -> List[TrendData]:
        """Analyze content format trends"""
        format_trends = []
        
        try:
            # Analyze content formats across platforms
            format_metrics = {}
            
            for platform, data in trending_data.items():
                for content in data.get('trending_content', []):
                    content_format = content.get('format', 'unknown')
                    
                    if content_format not in format_metrics:
                        format_metrics[content_format] = {
                            'post_count': 0,
                            'total_engagement': 0,
                            'platforms': set(),
                            'avg_duration': 0,
                            'creator_count': set(),
                            'growth_rate': 0
                        }
                    
                    metrics = format_metrics[content_format]
                    metrics['post_count'] += 1
                    metrics['total_engagement'] += content.get('engagement', 0)
                    metrics['platforms'].add(platform)
                    metrics['creator_count'].add(content.get('creator_id', 'unknown'))
                    
                    if 'duration' in content:
                        metrics['avg_duration'] = (
                            metrics['avg_duration'] * (metrics['post_count'] - 1) + 
                            content['duration']
                        ) / metrics['post_count']
            
            # Create format trend objects
            for format_name, metrics in format_metrics.items():
                if metrics['post_count'] >= 50:  # Minimum threshold for format trends
                    
                    momentum_score = self._calculate_momentum_score(
                        metrics.get('growth_rate', 0.1),
                        metrics['total_engagement'],
                        len(metrics['platforms'])
                    )
                    
                    trend = TrendData(
                        trend_id=self._generate_id(),
                        trend_type=TrendType.FORMAT_TREND,
                        trend_stage=TrendStage.GROWING,  # Most format trends are growing
                        trend_scope=TrendScope.GLOBAL,
                        title=f"{format_name.title()} Content Format",
                        description=f"Trending {format_name} format with {metrics['post_count']} posts",
                        keywords=[format_name, 'format', 'content'],
                        hashtags=[],
                        momentum_score=momentum_score,
                        viral_probability=min(momentum_score, 0.9),
                        growth_rate=metrics.get('growth_rate', 0.1),
                        peak_prediction=datetime.now() + timedelta(days=7),
                        decay_prediction=datetime.now() + timedelta(days=30),
                        platforms=list(metrics['platforms']),
                        demographics={},
                        engagement_metrics={
                            'avg_engagement': metrics['total_engagement'] / metrics['post_count'],
                            'engagement_rate': metrics['total_engagement'] / max(metrics['post_count'] * 1000, 1)
                        },
                        content_examples=[],
                        creator_count=len(metrics['creator_count']),
                        total_engagement=int(metrics['total_engagement']),
                        geographic_distribution={},
                        related_trends=[],
                        monetization_potential=0.6,  # Format trends generally have good monetization
                        risk_factors=["Format saturation", "Platform algorithm changes"],
                        opportunities=["Early adoption advantage", "Format optimization"]
                    )
                    
                    format_trends.append(trend)
            
            return format_trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing format trends: {e}")
            return []
    
    async def _analyze_music_trends(self, trending_data: Dict[str, Any]) -> List[TrendData]:
        """Analyze music and audio trends"""
        music_trends = []
        
        try:
            # Extract music/audio data
            music_data = {}
            
            for platform, data in trending_data.items():
                for content in data.get('trending_content', []):
                    audio_id = content.get('audio_id')
                    track_name = content.get('track_name')
                    artist = content.get('artist')
                    
                    if audio_id or track_name:
                        key = audio_id or f"{artist}_{track_name}".lower().replace(' ', '_')
                        
                        if key not in music_data:
                            music_data[key] = {
                                'track_name': track_name or 'Unknown',
                                'artist': artist or 'Unknown',
                                'usage_count': 0,
                                'total_engagement': 0,
                                'platforms': set(),
                                'creators': set(),
                                'genres': set()
                            }
                        
                        track_data = music_data[key]
                        track_data['usage_count'] += 1
                        track_data['total_engagement'] += content.get('engagement', 0)
                        track_data['platforms'].add(platform)
                        track_data['creators'].add(content.get('creator_id', 'unknown'))
                        
                        if 'genre' in content:
                            track_data['genres'].add(content['genre'])
            
            # Create music trend objects
            for track_key, track_data in music_data.items():
                if track_data['usage_count'] >= 20:  # Minimum threshold for music trends
                    
                    momentum_score = self._calculate_momentum_score(
                        0.2,  # Music trends often have steady growth
                        track_data['total_engagement'],
                        len(track_data['platforms'])
                    )
                    
                    trend = TrendData(
                        trend_id=self._generate_id(),
                        trend_type=TrendType.MUSIC_TREND,
                        trend_stage=TrendStage.GROWING,
                        trend_scope=TrendScope.GLOBAL,
                        title=f"{track_data['track_name']} by {track_data['artist']}",
                        description=f"Trending audio used in {track_data['usage_count']} posts",
                        keywords=[track_data['track_name'], track_data['artist'], 'music', 'audio'],
                        hashtags=[],
                        momentum_score=momentum_score,
                        viral_probability=min(momentum_score * 1.2, 0.95),  # Music has high viral potential
                        growth_rate=0.2,
                        peak_prediction=datetime.now() + timedelta(days=5),
                        decay_prediction=datetime.now() + timedelta(days=21),
                        platforms=list(track_data['platforms']),
                        demographics={},
                        engagement_metrics={
                            'avg_engagement': track_data['total_engagement'] / track_data['usage_count'],
                            'usage_rate': track_data['usage_count']
                        },
                        content_examples=[],
                        creator_count=len(track_data['creators']),
                        total_engagement=int(track_data['total_engagement']),
                        geographic_distribution={},
                        related_trends=[],
                        monetization_potential=0.8,  # Music trends have high monetization potential
                        risk_factors=["Copyright issues", "Audio availability"],
                        opportunities=["Early trend adoption", "Music collaboration", "Audio branding"]
                    )
                    
                    music_trends.append(trend)
            
            return music_trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing music trends: {e}")
            return []
    
    async def _analyze_challenge_trends(self, trending_data: Dict[str, Any]) -> List[TrendData]:
        """Analyze challenge and meme trends"""
        challenge_trends = []
        
        try:
            # Identify challenges from content
            challenge_patterns = [
                r'#\w*challenge\w*',
                r'#\w*trend\w*',
                r'try this',
                r'challenge accepted',
                r'viral dance',
                r'duet this'
            ]
            
            challenge_data = {}
            
            for platform, data in trending_data.items():
                for content in data.get('trending_content', []):
                    caption = content.get('caption', '').lower()
                    description = content.get('description', '').lower()
                    text_content = caption + ' ' + description
                    
                    # Check for challenge patterns
                    for pattern in challenge_patterns:
                        matches = re.findall(pattern, text_content, re.IGNORECASE)
                        for match in matches:
                            challenge_name = match.strip('#').replace('challenge', '').strip()
                            
                            if len(challenge_name) > 2:  # Valid challenge name
                                if challenge_name not in challenge_data:
                                    challenge_data[challenge_name] = {
                                        'participation_count': 0,
                                        'total_engagement': 0,
                                        'platforms': set(),
                                        'creators': set(),
                                        'hashtags': set(),
                                        'original_post': None
                                    }
                                
                                challenge = challenge_data[challenge_name]
                                challenge['participation_count'] += 1
                                challenge['total_engagement'] += content.get('engagement', 0)
                                challenge['platforms'].add(platform)
                                challenge['creators'].add(content.get('creator_id', 'unknown'))
                                
                                # Extract related hashtags
                                hashtags = re.findall(r'#\w+', text_content)
                                challenge['hashtags'].update(hashtags)
            
            # Create challenge trend objects
            for challenge_name, challenge_data in challenge_data.items():
                if challenge_data['participation_count'] >= 30:  # Minimum threshold
                    
                    momentum_score = self._calculate_momentum_score(
                        0.3,  # Challenges often have rapid growth
                        challenge_data['total_engagement'],
                        len(challenge_data['platforms'])
                    )
                    
                    trend = TrendData(
                        trend_id=self._generate_id(),
                        trend_type=TrendType.CHALLENGE_TREND,
                        trend_stage=TrendStage.GROWING,
                        trend_scope=TrendScope.GLOBAL,
                        title=f"{challenge_name.title()} Challenge",
                        description=f"Viral challenge with {challenge_data['participation_count']} participants",
                        keywords=[challenge_name, 'challenge', 'viral', 'participation'],
                        hashtags=list(challenge_data['hashtags'])[:10],
                        momentum_score=momentum_score,
                        viral_probability=min(momentum_score * 1.3, 0.98),  # Challenges have very high viral potential
                        growth_rate=0.3,
                        peak_prediction=datetime.now() + timedelta(days=3),
                        decay_prediction=datetime.now() + timedelta(days=14),
                        platforms=list(challenge_data['platforms']),
                        demographics={},
                        engagement_metrics={
                            'participation_rate': challenge_data['participation_count'],
                            'avg_engagement': challenge_data['total_engagement'] / challenge_data['participation_count']
                        },
                        content_examples=[],
                        creator_count=len(challenge_data['creators']),
                        total_engagement=int(challenge_data['total_engagement']),
                        geographic_distribution={},
                        related_trends=[],
                        monetization_potential=0.7,  # Challenges can be monetized through participation
                        risk_factors=["Short lifespan", "Participation difficulty", "Platform restrictions"],
                        opportunities=["Early participation", "Challenge variation", "Brand integration"]
                    )
                    
                    challenge_trends.append(trend)
            
            return challenge_trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing challenge trends: {e}")
            return []
    
    def _calculate_momentum_score(
        self,
        growth_rate: float,
        total_engagement: float,
        platform_count: int
    ) -> float:
        """Calculate trend momentum score"""
        try:
            # Normalize components
            growth_component = min(growth_rate, 1.0)
            engagement_component = min(total_engagement / 1000000, 1.0)  # Normalize to 1M
            platform_component = min(platform_count / 5, 1.0)  # Max 5 platforms
            
            # Weighted combination
            momentum = (
                growth_component * 0.4 +
                engagement_component * 0.4 +
                platform_component * 0.2
            )
            
            return min(momentum, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating momentum score: {e}")
            return 0.5
    
    async def _extract_content_features(self, content_data: Dict[str, Any]) -> List[float]:
        """Extract content features for viral prediction"""
        features = []
        
        try:
            # Content type features
            content_type = content_data.get('type', 'image')
            type_encoding = {'image': 0.2, 'video': 0.8, 'carousel': 0.5, 'story': 0.3}
            features.append(type_encoding.get(content_type, 0.5))
            
            # Content length/duration
            duration = content_data.get('duration', 0)
            features.append(min(duration / 60, 1.0))  # Normalize to 1 minute
            
            # Visual complexity
            features.append(content_data.get('visual_complexity', 0.5))
            
            # Text analysis
            caption = content_data.get('caption', '')
            features.append(len(caption) / 2200)  # Normalize to Instagram limit
            features.append(len(re.findall(r'#\w+', caption)) / 30)  # Hashtag count normalized
            features.append(len(re.findall(r'@\w+', caption)) / 10)  # Mention count normalized
            
            # Sentiment score
            if caption:
                sentiment_result = self.sentiment_analyzer(caption[:512])  # Truncate for model
                sentiment_score = sentiment_result[0]['score'] if sentiment_result[0]['label'] == 'POSITIVE' else -sentiment_result[0]['score']
                features.append((sentiment_score + 1) / 2)  # Normalize to 0-1
            else:
                features.append(0.5)
            
            # Content quality indicators
            features.append(content_data.get('resolution_score', 0.5))
            features.append(content_data.get('audio_quality', 0.5))
            features.append(content_data.get('editing_complexity', 0.5))
            
            # Trending elements
            features.append(content_data.get('uses_trending_audio', 0))
            features.append(content_data.get('uses_trending_hashtags', 0))
            features.append(content_data.get('follows_trend_format', 0))
            
            # Pad to fixed size (50 features)
            while len(features) < 50:
                features.append(0.0)
            
            return features[:50]
            
        except Exception as e:
            self.logger.error(f"Error extracting content features: {e}")
            return [0.5] * 50
    
    async def _extract_engagement_features(
        self,
        content_data: Dict[str, Any],
        creator_profile: Dict[str, Any] = None
    ) -> List[float]:
        """Extract engagement-related features"""
        features = []
        
        try:
            if creator_profile:
                # Creator metrics
                features.append(min(creator_profile.get('follower_count', 0) / 1000000, 1.0))
                features.append(creator_profile.get('engagement_rate', 0.05))
                features.append(creator_profile.get('viral_content_ratio', 0.1))
                features.append(min(creator_profile.get('posting_frequency', 1) / 10, 1.0))
                features.append(creator_profile.get('audience_loyalty', 0.5))
            else:
                features.extend([0.5] * 5)
            
            # Content-specific engagement predictors
            features.append(content_data.get('estimated_reach', 0) / 1000000)
            features.append(content_data.get('early_engagement_rate', 0.05))
            features.append(content_data.get('share_likelihood', 0.1))
            features.append(content_data.get('comment_likelihood', 0.05))
            features.append(content_data.get('save_likelihood', 0.03))
            
            # Platform-specific factors
            target_platform = content_data.get('target_platform', 'instagram')
            platform_encoding = {'instagram': 0.7, 'tiktok': 0.9, 'youtube': 0.6, 'twitter': 0.5}
            features.append(platform_encoding.get(target_platform, 0.5))
            
            # Timing factors
            posting_time = content_data.get('posting_time', datetime.now())
            hour = posting_time.hour
            features.append(self._get_optimal_hour_score(hour))
            
            weekday = posting_time.weekday()
            features.append(self._get_optimal_weekday_score(weekday))
            
            # Pad to fixed size (50 features)
            while len(features) < 50:
                features.append(0.0)
            
            return features[:50]
            
        except Exception as e:
            self.logger.error(f"Error extracting engagement features: {e}")
            return [0.5] * 50
    
    async def _extract_temporal_features(self, content_data: Dict[str, Any]) -> List[float]:
        """Extract temporal features for prediction"""
        features = []
        
        try:
            now = datetime.now()
            posting_time = content_data.get('posting_time', now)
            
            # Time-based features
            hour = posting_time.hour
            features.append(hour / 24)  # Hour of day normalized
            
            weekday = posting_time.weekday()
            features.append(weekday / 7)  # Day of week normalized
            
            # Seasonal factors
            month = posting_time.month
            features.append(month / 12)  # Month normalized
            
            # Weekend vs weekday
            features.append(1 if weekday >= 5 else 0)
            
            # Peak hours (typically 6-9 PM)
            features.append(1 if 18 <= hour <= 21 else 0)
            
            # Competition factor (how many others posting at same time)
            competition_score = content_data.get('competition_level', 0.5)
            features.append(competition_score)
            
            # Trending cycle position
            trend_cycle = content_data.get('trend_cycle_position', 0.5)
            features.append(trend_cycle)
            
            # Platform-specific optimal timing
            platform = content_data.get('target_platform', 'instagram')
            optimal_timing_score = self._get_platform_timing_score(platform, hour, weekday)
            features.append(optimal_timing_score)
            
            # Pad to fixed size (50 features)
            while len(features) < 50:
                features.append(0.0)
            
            return features[:50]
            
        except Exception as e:
            self.logger.error(f"Error extracting temporal features: {e}")
            return [0.5] * 50
    
    def _get_optimal_hour_score(self, hour: int) -> float:
        """Get optimal hour score based on general engagement patterns"""
        # General peak hours: 6-9 AM, 12-1 PM, 6-9 PM
        peak_hours = [6, 7, 8, 9, 12, 13, 18, 19, 20, 21]
        return 0.8 if hour in peak_hours else 0.4
    
    def _get_optimal_weekday_score(self, weekday: int) -> float:
        """
Get optimal weekday score"""
        # Monday=0, Sunday=6
        # Generally Tuesday-Thursday and Sunday are good
        good_days = [1, 2, 3, 6]  # Tue, Wed, Thu, Sun
        return 0.8 if weekday in good_days else 0.6
    
    def _get_platform_timing_score(self, platform: str, hour: int, weekday: int) -> float:
        """
Get platform-specific timing score"""
        platform_optimal_times = {
            'instagram': {
                'hours': [6, 7, 8, 12, 17, 18, 19, 20],
                'weekdays': [1, 2, 3, 4]  # Tue-Fri
            },
            'tiktok': {
                'hours': [6, 10, 19, 20, 21, 22],
                'weekdays': [1, 2, 3, 4, 5, 6]  # Tue-Sun
            },
            'youtube': {
                'hours': [14, 15, 16, 17, 18, 19, 20],
                'weekdays': [2, 3, 4, 5, 6]  # Wed-Sun
            },
            'twitter': {
                'hours': [8, 9, 12, 13, 17, 18],
                'weekdays': [1, 2, 3, 4]  # Tue-Fri
            }
        }
        
        platform_data = platform_optimal_times.get(platform, {'hours': [], 'weekdays': []})
        
        hour_score = 0.8 if hour in platform_data['hours'] else 0.4
        weekday_score = 0.8 if weekday in platform_data['weekdays'] else 0.6
        
        return (hour_score + weekday_score) / 2
    
    async def _predict_viral_probability(
        self,
        content_features: List[float],
        engagement_features: List[float],
        temporal_features: List[float]
    ) -> float:
        """
Predict viral probability using ML model"""
        try:
            if self.viral_predictor:
                with torch.no_grad():
                    content_tensor = torch.tensor(content_features).float().unsqueeze(0)
                    engagement_tensor = torch.tensor(engagement_features).float().unsqueeze(0)
                    temporal_tensor = torch.tensor(temporal_features).float().unsqueeze(0)
                    
                    viral_prob = float(self.viral_predictor(
                        content_tensor, engagement_tensor, temporal_tensor
                    ).item())
                    
                    return viral_prob
            
            # Fallback: rule-based prediction
            return self._rule_based_viral_prediction(
                content_features, engagement_features, temporal_features
            )
            
        except Exception as e:
            self.logger.error(f"Error predicting viral probability: {e}")
            return 0.1
    
    def _rule_based_viral_prediction(
        self,
        content_features: List[float],
        engagement_features: List[float],
        temporal_features: List[float]
    ) -> float:
        """Rule-based viral probability prediction"""
        try:
            # Extract key features
            content_quality = np.mean(content_features[:10])
            engagement_potential = np.mean(engagement_features[:10])
            timing_score = np.mean(temporal_features[:10])
            
            # Calculate base probability
            base_prob = (content_quality * 0.4 + engagement_potential * 0.4 + timing_score * 0.2)
            
            # Apply viral multipliers
            viral_multipliers = []
            
            # High-quality content
            if content_quality > 0.8:
                viral_multipliers.append(1.5)
            
            # Strong engagement potential
            if engagement_potential > 0.7:
                viral_multipliers.append(1.3)
            
            # Optimal timing
            if timing_score > 0.8:
                viral_multipliers.append(1.2)
            
            # Apply multipliers
            final_prob = base_prob
            for multiplier in viral_multipliers:
                final_prob *= multiplier
            
            return min(final_prob, 0.95)  # Cap at 95%
            
        except Exception as e:
            self.logger.error(f"Error in rule-based viral prediction: {e}")
            return 0.1
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}{hash(self)}".encode()).hexdigest()[:12]


class ViralPredictionEngine:
    """
    Specialized engine for viral content prediction
    
    Uses ensemble methods and continuous learning to improve
    viral prediction accuracy over time.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
Initialize viral prediction engine"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Ensemble models
        self.prediction_models = []
        self.model_weights = []
        
        self._initialize_ensemble_models()
    
    def _initialize_ensemble_models(self):
        """
Initialize ensemble of prediction models"""
        try:
            # Model 1: Neural network
            self.prediction_models.append(self._create_neural_model())
            self.model_weights.append(0.4)
            
            # Model 2: Random forest
            self.prediction_models.append(RandomForestRegressor(n_estimators=100))
            self.model_weights.append(0.3)
            
            # Model 3: Gradient boosting
            from sklearn.ensemble import GradientBoostingRegressor
            self.prediction_models.append(GradientBoostingRegressor(n_estimators=100))
            self.model_weights.append(0.3)
            
            self.logger.info("Viral prediction ensemble initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing ensemble: {e}")
            raise
    
    def _create_neural_model(self):
        """Create neural network for viral prediction"""
        class ViralNN(nn.Module):
            def __init__(self):
                super().__init__()
                self.layers = nn.Sequential(
                    nn.Linear(150, 256),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(256, 128),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.Linear(64, 1),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                return self.layers(x)
        
        return ViralNN()

    async def analyze_local_trends(
        self,
        region: str,
        cultural_context: str = None,
        platforms: List[str] = None,
        time_window_hours: int = 24
    ) -> List[TrendData]:
        """
        Analyze local and regional trends with cultural context
        
        Args:
            region: Target region (e.g., "MENA", "NA", "GCC")
            cultural_context: Cultural context (e.g., "AR", "AMAZIGH", "HE")
            platforms: Specific platforms to analyze
            time_window_hours: Analysis time window
            
        Returns:
            List of localized trends
        """
        try:
            self.logger.info(f"Analyzing local trends for region: {region}")
            
            # Get standard trends first
            global_trends = await self.analyze_current_trends(
                platforms=platforms,
                geographic_scope=TrendScope.REGIONAL,
                time_window_hours=time_window_hours,
                cultural_context=cultural_context,
                region=region
            )
            
            # Apply local filtering and enhancement
            local_trends = []
            
            for trend in global_trends:
                # Apply cultural and regional filtering
                local_trend = await self._localize_trend(trend, region, cultural_context)
                if local_trend:
                    local_trends.append(local_trend)
            
            # Add region-specific trends
            regional_trends = await self._get_regional_specific_trends(region, cultural_context)
            local_trends.extend(regional_trends)
            
            # Sort by relevance to local context
            local_trends = await self._sort_by_local_relevance(local_trends, region, cultural_context)
            
            return local_trends[:50]  # Return top 50 local trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing local trends: {e}")
            return []

    async def _localize_trend(
        self, trend: TrendData, region: str, cultural_context: str = None
    ) -> Optional[TrendData]:
        """Localize a global trend for specific region and culture"""
        
        # Cultural sensitivity check
        if cultural_context and not await self._is_culturally_appropriate(trend, cultural_context):
            return None
        
        # Regional relevance score
        relevance_score = await self._calculate_regional_relevance(trend, region)
        if relevance_score < 0.3:  # Threshold for local relevance
            return None
        
        # Create localized version
        localized_trend = TrendData(
            trend_id=trend.trend_id + f"_{region.lower()}",
            trend_type=trend.trend_type,
            trend_stage=trend.trend_stage,
            trend_scope=TrendScope.REGIONAL,
            title=await self._localize_title(trend.title, region, cultural_context),
            description=await self._localize_description(trend.description, region, cultural_context),
            keywords=await self._localize_keywords(trend.keywords, region, cultural_context),
            hashtags=await self._localize_hashtags(trend.hashtags, region, cultural_context),
            momentum_score=trend.momentum_score * relevance_score,
            viral_probability=trend.viral_probability * relevance_score,
            growth_rate=trend.growth_rate,
            peak_prediction=trend.peak_prediction,
            decay_prediction=trend.decay_prediction,
            platforms=trend.platforms,
            demographics=await self._localize_demographics(trend.demographics, region),
            engagement_metrics=trend.engagement_metrics,
            content_examples=trend.content_examples,
            creator_count=trend.creator_count,
            total_engagement=trend.total_engagement,
            geographic_distribution={region: 1.0},  # 100% local
            related_trends=trend.related_trends,
            monetization_potential=trend.monetization_potential,
            risk_factors=await self._add_regional_risks(trend.risk_factors, region, cultural_context),
            opportunities=await self._add_regional_opportunities(trend.opportunities, region, cultural_context),
            metadata={
                **trend.metadata,
                "region": region,
                "cultural_context": cultural_context,
                "localization_score": relevance_score
            }
        )
        
        return localized_trend

    async def _is_culturally_appropriate(self, trend: TrendData, cultural_context: str) -> bool:
        """Check if trend is culturally appropriate for target context"""
        
        # Define sensitive content for different cultures
        sensitive_content = {
            "AR": ["alcohol", "pork", "gambling", "dating", "nudity"],
            "AMAZIGH": ["colonial", "primitive", "backward"],
            "HE": ["nazi", "antisemitic", "holocaust denial"]
        }
        
        sensitive_terms = sensitive_content.get(cultural_context.upper(), [])
        
        # Check trend content for sensitive terms
        content_to_check = [
            trend.title.lower(),
            trend.description.lower(),
            " ".join(trend.keywords).lower(),
            " ".join(trend.hashtags).lower()
        ]
        
        for content in content_to_check:
            for term in sensitive_terms:
                if term in content:
                    return False
        
        return True

    async def _calculate_regional_relevance(self, trend: TrendData, region: str) -> float:
        """Calculate how relevant a trend is to a specific region"""
        
        relevance_score = 0.5  # Base score
        
        # Regional keyword boosters
        regional_keywords = {
            "MENA": ["ramadan", "eid", "hajj", "arabic", "middle east", "gulf"],
            "NA": ["maghreb", "amazigh", "berber", "atlas", "sahara", "tamazgha"],
            "GCC": ["dubai", "saudi", "qatar", "kuwait", "luxury", "oil"]
        }
        
        region_terms = regional_keywords.get(region, [])
        trend_content = " ".join([
            trend.title, trend.description, 
            " ".join(trend.keywords), 
            " ".join(trend.hashtags)
        ]).lower()
        
        # Boost score for regional keywords
        for term in region_terms:
            if term in trend_content:
                relevance_score += 0.1
        
        # Platform relevance by region
        regional_platform_weights = {
            "MENA": {"instagram": 1.2, "tiktok": 1.1, "twitter": 1.0, "youtube": 0.9},
            "NA": {"instagram": 1.3, "tiktok": 1.2, "facebook": 1.1, "youtube": 1.0},
            "GCC": {"instagram": 1.4, "twitter": 1.2, "tiktok": 1.0, "youtube": 0.8}
        }
        
        platform_weights = regional_platform_weights.get(region, {})
        for platform in trend.platforms:
            weight = platform_weights.get(platform, 1.0)
            relevance_score *= weight
        
        return min(relevance_score, 1.0)

    async def _get_regional_specific_trends(self, region: str, cultural_context: str = None) -> List[TrendData]:
        """Get trends specific to a region/culture"""
        
        regional_trends = []
        
        # Define region-specific trending topics
        regional_topics = {
            "MENA": {
                "topics": ["ramadan preparation", "eid celebrations", "arabic music", "gulf culture"],
                "hashtags": ["#رمضان", "#عيد_مبارك", "#الخليج", "#العرب"],
                "keywords": ["islamic", "arabic", "middle eastern", "traditional"]
            },
            "NA": {
                "topics": ["amazigh culture", "atlas mountains", "maghreb food", "berber traditions"],
                "hashtags": ["#amazigh", "#maghreb", "#tamazgha", "#atlas"],
                "keywords": ["berber", "north african", "sahara", "traditional"]
            },
            "GCC": {
                "topics": ["luxury lifestyle", "desert adventures", "modern architecture", "business hub"],
                "hashtags": ["#dubai", "#saudi", "#gulf", "#luxury"],
                "keywords": ["luxury", "modern", "business", "innovation"]
            }
        }
        
        region_data = regional_topics.get(region, {})
        
        for i, topic in enumerate(region_data.get("topics", [])):
            trend = TrendData(
                trend_id=f"regional_{region.lower()}_{i}",
                trend_type=TrendType.TOPIC_TREND,
                trend_stage=TrendStage.GROWING,
                trend_scope=TrendScope.REGIONAL,
                title=f"{topic.title()} - {region}",
                description=f"Regional trend popular in {region}",
                keywords=region_data.get("keywords", [])[:5],
                hashtags=region_data.get("hashtags", [])[:5],
                momentum_score=0.7,
                viral_probability=0.6,
                growth_rate=0.15,
                peak_prediction=datetime.now() + timedelta(days=7),
                decay_prediction=datetime.now() + timedelta(days=30),
                platforms=["instagram", "tiktok", "twitter"],
                demographics={"age": "18-35", "region": region},
                engagement_metrics={"avg_engagement": 5000},
                content_examples=[],
                creator_count=500,
                total_engagement=250000,
                geographic_distribution={region: 1.0},
                related_trends=[],
                monetization_potential=0.7,
                risk_factors=["Cultural sensitivity required"],
                opportunities=["Local partnerships", "Cultural authenticity"],
                metadata={"region": region, "cultural_context": cultural_context}
            )
            regional_trends.append(trend)
        
        return regional_trends

    async def _localize_title(self, title: str, region: str, cultural_context: str = None) -> str:
        """Localize trend title for region and culture"""
        
        # Add regional suffix for clarity
        region_suffixes = {
            "MENA": "الشرق الأوسط",
            "NA": "شمال أفريقيا", 
            "GCC": "دول الخليج"
        }
        
        suffix = region_suffixes.get(region, region)
        return f"{title} - {suffix}"

    async def _localize_description(self, description: str, region: str, cultural_context: str = None) -> str:
        """Localize trend description for region and culture"""
        
        return f"{description} Popular in {region} region."

    async def _localize_keywords(self, keywords: List[str], region: str, cultural_context: str = None) -> List[str]:
        """Localize keywords for region and culture"""
        
        localized = keywords.copy()
        
        # Add regional keywords
        regional_additions = {
            "MENA": ["arabic", "middle_east", "gulf"],
            "NA": ["maghreb", "amazigh", "north_africa"],
            "GCC": ["gulf", "luxury", "modern"]
        }
        
        additions = regional_additions.get(region, [])
        localized.extend(additions)
        
        return list(set(localized))[:10]  # Remove duplicates, limit to 10

    async def _localize_hashtags(self, hashtags: List[str], region: str, cultural_context: str = None) -> List[str]:
        """Localize hashtags for region and culture"""
        
        localized = hashtags.copy()
        
        # Add regional hashtags
        regional_hashtags = {
            "MENA": ["#الشرق_الأوسط", "#العرب", "#الخليج"],
            "NA": ["#المغرب_العربي", "#أمازيغ", "#شمال_أفريقيا"],
            "GCC": ["#دول_الخليج", "#الإمارات", "#السعودية"]
        }
        
        additions = regional_hashtags.get(region, [])
        localized.extend(additions)
        
        return list(set(localized))[:15]  # Remove duplicates, limit to 15

    async def _localize_demographics(self, demographics: Dict[str, Any], region: str) -> Dict[str, Any]:
        """Localize demographics for region"""
        
        localized = demographics.copy()
        localized["region"] = region
        
        return localized

    async def _add_regional_risks(self, risks: List[str], region: str, cultural_context: str = None) -> List[str]:
        """Add region-specific risk factors"""
        
        regional_risks = risks.copy()
        
        # Add cultural/regional risks
        if cultural_context in ["AR", "AMAZIGH"]:
            regional_risks.extend([
                "Cultural sensitivity required",
                "Religious considerations",
                "Traditional values alignment"
            ])
        
        if region == "MENA":
            regional_risks.append("Political sensitivity")
        
        return list(set(regional_risks))

    async def _add_regional_opportunities(self, opportunities: List[str], region: str, cultural_context: str = None) -> List[str]:
        """Add region-specific opportunities"""
        
        regional_opportunities = opportunities.copy()
        
        # Add cultural/regional opportunities
        if region == "MENA":
            regional_opportunities.extend([
                "Large Arabic-speaking audience",
                "Cultural authenticity advantage",
                "Regional partnership opportunities"
            ])
        elif region == "NA":
            regional_opportunities.extend([
                "Amazigh cultural content niche",
                "Multilingual content opportunity",
                "North African diaspora reach"
            ])
        elif region == "GCC":
            regional_opportunities.extend([
                "High purchasing power audience",
                "Luxury brand partnerships",
                "Business networking content"
            ])
        
        return list(set(regional_opportunities))

    async def _sort_by_local_relevance(self, trends: List[TrendData], region: str, cultural_context: str = None) -> List[TrendData]:
        """Sort trends by local relevance score"""
        
        def relevance_key(trend):
            # Calculate composite relevance score
            base_score = trend.momentum_score
            
            # Boost for regional metadata
            if trend.metadata.get("region") == region:
                base_score += 0.2
            
            # Boost for cultural context match
            if trend.metadata.get("cultural_context") == cultural_context:
                base_score += 0.1
            
            # Boost for localization score
            localization_score = trend.metadata.get("localization_score", 0)
            base_score += localization_score * 0.3
            
            return base_score
        
        return sorted(trends, key=relevance_key, reverse=True)


class MarketIntelligence:
    """
    Market intelligence engine for content creators
    
    Provides insights into market opportunities, competition analysis,
    and strategic recommendations for content positioning.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
Initialize market intelligence engine"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components for market analysis
        self.trend_analyzer = TrendAnalyzer(config)
        
    async def analyze_market_opportunity(
        self,
        content_niche: str,
        target_audience: Dict[str, Any],
        geographic_market: str = "global"
    ) -> MarketIntelligence:
        """
        Analyze market opportunity for specific content niche
        
        Args:
            content_niche: Content niche or category
            target_audience: Target audience demographics
            geographic_market: Geographic market scope
            
        Returns:
            Market intelligence analysis
        """
        try:
            self.logger.info(f"Analyzing market opportunity for {content_niche}")
            
            # This would implement comprehensive market analysis
            # For now, return mock data structure
            
            return MarketIntelligence(
                intelligence_id=self._generate_id(),
                market_segment=content_niche,
                market_size=1000000,
                growth_rate=0.15,
                competition_level="medium",
                entry_barriers=["Content quality requirements", "Algorithm competition"],
                key_players=["Top creators in niche"],
                emerging_opportunities=["New platform features", "Trend adoption"],
                threat_analysis=["Market saturation", "Platform changes"],
                recommended_strategies=["Niche specialization", "Community building"],
                investment_attractiveness=0.7,
                time_to_market="2-3 months",
                success_probability=0.6,
                revenue_potential=50000.0
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing market opportunity: {e}")
            return MarketIntelligence(
                intelligence_id=self._generate_id(),
                market_segment=content_niche,
                market_size=0,
                growth_rate=0.0,
                competition_level="unknown",
                entry_barriers=[],
                key_players=[],
                emerging_opportunities=[],
                threat_analysis=[],
                recommended_strategies=[],
                investment_attractiveness=0.0,
                time_to_market="unknown",
                success_probability=0.0,
                revenue_potential=0.0
            )
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}{hash(self)}".encode()).hexdigest()[:12]
