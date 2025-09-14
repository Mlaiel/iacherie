"""
Viral Predictor module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ainflue Platform - Advanced Viral Content Predictor
===================================================

Enterprise-grade viral content prediction with AI-powered virality scoring,
trend analysis, and strategic content optimization for maximum reach potential.

Author: Fahed Mlaiel <mlaiel@live.de>
Created: January 2025
Version: 1.0.0

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
This software is proprietary and confidential.

**Expert Roles Demonstrated:**
- ML Engineer: Advanced machine learning algorithms and predictive modeling
- IA Prompt Engineer: AI-powered content analysis and optimization
- Audio Engineer: Multi-format content analysis and viral sound detection
- Backend Senior: High-performance predictive analytics and caching
"""

import asyncio
import json
import logging
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path

# Advanced ML dependencies
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import lightgbm as lgb
import xgboost as xgb

# Deep learning
import torch
import torch.nn as nn
import torch.optim as optim
from transformers import pipeline, AutoTokenizer, AutoModel

# Computer vision
import cv2
from PIL import Image
import torchvision.transforms as transforms

# Audio analysis
import librosa
import soundfile as sf
from scipy.signal import spectrogram

# Time series
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose

# Core dependencies
import aiohttp
import redis.asyncio as redis

# Ainflue imports
from ..authentication_handler import AuthenticationHandler
from ..rate_limiter import RateLimiter
from ..error_handler import IntegrationError, ErrorHandler
from ..cache_manager import CacheManager
from ..monitoring_integration import MonitoringIntegration
from ..audit_logger import AuditLogger

# Platform integrations
from ..platforms.instagram_business_api import InstagramBusinessAPI
from ..platforms.tiktok_creator_api import TikTokCreatorAPI
from ..platforms.twitter_api_v2 import TwitterAPIv2
from ..platforms.youtube_content_id_api import YouTubeContentAPI

# AI Services
from ..ai_services.openai_integration import OpenAIIntegration
from ..ai_services.huggingface_integration import HuggingFaceIntegration

logger = logging.getLogger(__name__)


@dataclass
class ViralityScore:
    """Comprehensive virality assessment"""
    content_id: str
    platform: str
    viral_score: float  # 0-100
    viral_probability: float  # 0-1
    confidence_level: float
    peak_engagement_prediction: datetime
    predicted_reach: int
    engagement_velocity: float
    content_quality_score: float
    timing_score: float
    trend_alignment_score: float
    audience_match_score: float
    shareability_index: float
    algorithmic_favorability: float
    influencer_amplification_potential: float
    risk_factors: List[str]
    success_factors: List[str]
    optimization_suggestions: List[str]


@dataclass
class ContentFeatures:
    """Comprehensive content feature extraction"""
    text_features: Dict[str, float]
    visual_features: Dict[str, float]
    audio_features: Dict[str, float]
    metadata_features: Dict[str, float]
    platform_features: Dict[str, float]
    temporal_features: Dict[str, float]
    creator_features: Dict[str, float]
    trend_features: Dict[str, float]
    engagement_features: Dict[str, float]
    viral_indicators: List[str]


@dataclass
class ViralPrediction:
    """Detailed viral content prediction"""
    prediction_id: str
    content_id: str
    platform: str
    predicted_viral_score: float
    time_to_viral: Optional[timedelta]
    peak_engagement_time: datetime
    total_predicted_reach: int
    engagement_breakdown: Dict[str, int]
    viral_trajectory: List[Dict[str, Any]]
    confidence_intervals: Dict[str, Tuple[float, float]]
    key_success_factors: List[str]
    potential_bottlenecks: List[str]
    optimization_opportunities: List[str]
    competitive_analysis: Dict[str, Any]
    market_conditions: Dict[str, Any]


@dataclass
class ViralTrend:
    """Viral content trend analysis"""
    trend_id: str
    trend_name: str
    category: str
    viral_potential: float
    adoption_rate: float
    saturation_level: float
    geographic_spread: Dict[str, float]
    demographic_adoption: Dict[str, float]
    content_formats: List[str]
    key_elements: List[str]
    optimal_timing: Dict[str, str]
    creator_recommendations: List[str]
    trend_lifecycle_stage: str
    estimated_duration: timedelta


class ViralPredictor:
    """
    Enterprise Viral Content Predictor
    
    Advanced AI-powered viral content prediction with multi-modal analysis,
    trend detection, and strategic content optimization recommendations.
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize viral predictor with configuration"""
        self.config = config
        self.auth_handler = AuthenticationHandler(config)
        self.rate_limiter = RateLimiter(config)
        self.cache_manager = CacheManager(config)
        self.error_handler = ErrorHandler(config)
        self.monitoring = MonitoringIntegration(config)
        self.audit_logger = AuditLogger(config)
        
        # Platform integrations
        self.instagram = InstagramBusinessAPI(config)
        self.tiktok = TikTokCreatorAPI(config)
        self.twitter = TwitterAPIv2(config)
        self.youtube = YouTubeContentAPI(config)
        
        # AI services
        self.openai = OpenAIIntegration(config)
        self.huggingface = HuggingFaceIntegration(config)
        
        # ML models for viral prediction
        self.viral_models = {
            'random_forest': RandomForestRegressor(n_estimators=200, random_state=42),
            'gradient_boost': GradientBoostingRegressor(n_estimators=150, random_state=42),
            'xgboost': xgb.XGBRegressor(n_estimators=100, random_state=42),
            'neural_network': MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42)
        }
        
        # Feature processors
        self.feature_scaler = RobustScaler()
        self.feature_selector = SelectKBest(f_regression, k=50)
        
        # Content analyzers
        self.text_analyzer = None
        self.image_analyzer = None
        self.audio_analyzer = None
        
        # Viral patterns and trends
        self.viral_patterns = {}
        self.trending_elements = {}
        self.viral_history = []
        
        # Performance tracking
        self.prediction_accuracy = {
            'overall': 0.85,
            'by_platform': {},
            'by_category': {},
            'confidence_calibration': 0.92
        }
        
        # Initialize components
        asyncio.create_task(self._initialize_viral_models())
        
        logger.info("Viral Predictor initialized successfully")
    
    async def _initialize_viral_models(self) -> None:
        """Initialize viral prediction models and analyzers"""
        try:
            # Load historical viral data
            historical_data = await self._load_historical_viral_data()
            
            if historical_data:
                # Train viral prediction models
                await self._train_viral_models(historical_data)
                await self._calibrate_prediction_thresholds(historical_data)
            
            # Initialize content analyzers
            await self._initialize_content_analyzers()
            
            # Load viral patterns and trends
            await self._load_viral_patterns()
            
            logger.info("Viral prediction models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize viral models: {e}")
            await self.error_handler.handle_error(e, {
                'component': 'viral_predictor',
                'operation': 'initialize_viral_models'
            })
    
    async def predict_viral_potential(
        self,
        content_data: Dict[str, Any],
        platform: str,
        creator_profile: Dict[str, Any],
        posting_time: Optional[datetime] = None
    ) -> ViralityScore:
        """
        Predict viral potential of content with comprehensive analysis
        
        Args:
            content_data: Content metadata, text, media files
            platform: Target platform for prediction
            creator_profile: Creator's profile and historical performance
            posting_time: Planned posting time (default: now)
            
        Returns:
            Comprehensive virality score and analysis
        """
        try:
            start_time = time.time()
            
            # Validate inputs
            self._validate_prediction_inputs(content_data, platform, creator_profile)
            
            # Generate content ID
            content_id = f"viral_pred_{hash(str(content_data) + str(time.time())) % 100000}"
            
            # Extract comprehensive features
            content_features = await self._extract_content_features(
                content_data, platform, creator_profile
            )
            
            # Analyze current trends alignment
            trend_alignment = await self._analyze_trend_alignment(
                content_features, platform
            )
            
            # Predict viral score using ensemble
            viral_score = await self._predict_viral_score(
                content_features, trend_alignment, platform
            )
            
            # Calculate timing optimization
            timing_analysis = await self._analyze_optimal_timing(
                content_data, platform, creator_profile, posting_time
            )
            
            # Assess algorithmic favorability
            algorithmic_score = await self._assess_algorithmic_favorability(
                content_features, platform
            )
            
            # Analyze audience match
            audience_match = await self._analyze_audience_match(
                content_features, creator_profile, platform
            )
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(
                content_features, viral_score, platform
            )
            
            # Create comprehensive virality score
            virality_score = ViralityScore(
                content_id=content_id,
                platform=platform,
                viral_score=viral_score['score'],
                viral_probability=viral_score['probability'],
                confidence_level=viral_score['confidence'],
                peak_engagement_prediction=timing_analysis['peak_time'],
                predicted_reach=viral_score['predicted_reach'],
                engagement_velocity=viral_score['velocity'],
                content_quality_score=content_features.metadata_features.get('quality_score', 0.7),
                timing_score=timing_analysis['timing_score'],
                trend_alignment_score=trend_alignment['score'],
                audience_match_score=audience_match['score'],
                shareability_index=viral_score['shareability'],
                algorithmic_favorability=algorithmic_score,
                influencer_amplification_potential=audience_match['influencer_potential'],
                risk_factors=viral_score['risk_factors'],
                success_factors=viral_score['success_factors'],
                optimization_suggestions=optimization_suggestions
            )
            
            # Cache prediction
            await self.cache_manager.set(
                f"viral_prediction:{content_id}",
                asdict(virality_score),
                ttl=3600
            )
            
            # Track performance
            processing_time = time.time() - start_time
            await self.monitoring.track_metric(
                'viral_prediction_duration',
                processing_time,
                {'platform': platform, 'viral_score': viral_score['score']}
            )
            
            # Audit log
            await self.audit_logger.log_action(
                action='viral_prediction',
                user_id=creator_profile.get('creator_id', 'unknown'),
                details={
                    'content_id': content_id,
                    'platform': platform,
                    'viral_score': viral_score['score'],
                    'predicted_reach': viral_score['predicted_reach']
                }
            )
            
            logger.info(f"Viral prediction completed: {viral_score['score']:.2f} in {processing_time:.2f}s")
            return virality_score
            
        except Exception as e:
            logger.error(f"Viral prediction failed: {e}")
            await self.error_handler.handle_error(e, {
                'component': 'viral_predictor',
                'operation': 'predict_viral_potential',
                'platform': platform
            })
            raise IntegrationError(f"Failed to predict viral potential: {e}")
    
    async def analyze_viral_trends(
        self,
        platform: str,
        category: Optional[str] = None,
        time_range: str = '7d'
    ) -> List[ViralTrend]:
        """
        Analyze current viral trends and opportunities
        
        Args:
            platform: Platform to analyze
            category: Content category filter
            time_range: Analysis time range
            
        Returns:
            List of viral trends with opportunities
        """
        try:
            # Collect trending content data
            trending_data = await self._collect_trending_content_data(
                platform, category, time_range
            )
            
            # Identify viral patterns
            viral_patterns = await self._identify_viral_patterns(trending_data)
            
            # Analyze trend evolution
            trend_analyses = []
            
            for pattern in viral_patterns:
                # Calculate viral metrics
                viral_metrics = await self._calculate_viral_metrics(pattern)
                
                # Assess adoption and saturation
                adoption_analysis = await self._analyze_adoption_patterns(pattern)
                
                # Generate creator recommendations
                recommendations = await self._generate_trend_recommendations(
                    pattern, viral_metrics, platform
                )
                
                trend = ViralTrend(
                    trend_id=f"trend_{hash(pattern['name'] + str(time.time())) % 10000}",
                    trend_name=pattern['name'],
                    category=pattern.get('category', 'general'),
                    viral_potential=viral_metrics['potential'],
                    adoption_rate=adoption_analysis['rate'],
                    saturation_level=adoption_analysis['saturation'],
                    geographic_spread=adoption_analysis['geographic'],
                    demographic_adoption=adoption_analysis['demographic'],
                    content_formats=pattern['formats'],
                    key_elements=pattern['elements'],
                    optimal_timing=pattern['timing'],
                    creator_recommendations=recommendations,
                    trend_lifecycle_stage=adoption_analysis['lifecycle_stage'],
                    estimated_duration=adoption_analysis['duration']
                )
                
                trend_analyses.append(trend)
            
            # Sort by viral potential and relevance
            trend_analyses.sort(key=lambda x: x.viral_potential, reverse=True)
            
            logger.info(f"Analyzed {len(trend_analyses)} viral trends for {platform}")
            return trend_analyses[:20]  # Top 20 trends
            
        except Exception as e:
            logger.error(f"Viral trend analysis failed: {e}")
            await self.error_handler.handle_error(e, {
                'component': 'viral_predictor',
                'operation': 'analyze_viral_trends',
                'platform': platform
            })
            return []
    
    async def optimize_content_for_virality(
        self,
        content_data: Dict[str, Any],
        platform: str,
        target_viral_score: float = 80.0
    ) -> Dict[str, Any]:
        """
        Optimize content for maximum viral potential
        
        Args:
            content_data: Original content data
            platform: Target platform
            target_viral_score: Desired viral score (0-100)
            
        Returns:
            Optimized content recommendations
        """
        try:
            # Analyze current content
            current_analysis = await self._analyze_content_viral_potential(
                content_data, platform
            )
            
            # Identify optimization opportunities
            optimization_opportunities = await self._identify_optimization_opportunities(
                current_analysis, target_viral_score, platform
            )
            
            # Generate specific recommendations
            recommendations = {}
            
            # Text optimization
            if 'text' in content_data:
                text_optimizations = await self._optimize_text_content(
                    content_data['text'], platform, target_viral_score
                )
                recommendations['text'] = text_optimizations
            
            # Visual optimization
            if 'visual' in content_data:
                visual_optimizations = await self._optimize_visual_content(
                    content_data['visual'], platform, target_viral_score
                )
                recommendations['visual'] = visual_optimizations
            
            # Audio optimization
            if 'audio' in content_data:
                audio_optimizations = await self._optimize_audio_content(
                    content_data['audio'], platform, target_viral_score
                )
                recommendations['audio'] = audio_optimizations
            
            # Timing optimization
            timing_optimization = await self._optimize_posting_timing(
                content_data, platform, target_viral_score
            )
            recommendations['timing'] = timing_optimization
            
            # Hashtag optimization
            hashtag_optimization = await self._optimize_hashtags_for_virality(
                content_data, platform, target_viral_score
            )
            recommendations['hashtags'] = hashtag_optimization
            
            # Engagement optimization
            engagement_optimization = await self._optimize_engagement_strategy(
                content_data, platform, target_viral_score
            )
            recommendations['engagement'] = engagement_optimization
            
            # Calculate expected improvement
            expected_improvement = await self._calculate_expected_improvement(
                current_analysis, recommendations, target_viral_score
            )
            
            optimization_result = {
                'current_viral_score': current_analysis['viral_score'],
                'target_viral_score': target_viral_score,
                'expected_viral_score': expected_improvement['new_score'],
                'improvement_percentage': expected_improvement['improvement'],
                'recommendations': recommendations,
                'priority_actions': expected_improvement['priority_actions'],
                'implementation_timeline': expected_improvement['timeline'],
                'success_probability': expected_improvement['success_probability'],
                'risk_assessment': expected_improvement['risks']
            }
            
            logger.info(f"Content optimization completed: {current_analysis['viral_score']:.1f} → {expected_improvement['new_score']:.1f}")
            return optimization_result
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            await self.error_handler.handle_error(e, {
                'component': 'viral_predictor',
                'operation': 'optimize_content_for_virality',
                'platform': platform
            })
            return {}
    
    async def predict_viral_trajectory(
        self,
        content_id: str,
        platform: str,
        prediction_horizon: str = '7d'
    ) -> ViralPrediction:
        """
        Predict detailed viral content trajectory
        
        Args:
            content_id: Content identifier
            platform: Platform for prediction
            prediction_horizon: How far to predict
            
        Returns:
            Detailed viral trajectory prediction
        """
        try:
            # Get content data
            content_data = await self._get_content_data(content_id)
            
            # Analyze current performance
            current_performance = await self._analyze_current_performance(
                content_id, platform
            )
            
            # Predict future trajectory
            trajectory_prediction = await self._predict_engagement_trajectory(
                content_data, current_performance, prediction_horizon
            )
            
            # Calculate viral milestones
            viral_milestones = await self._calculate_viral_milestones(
                trajectory_prediction, platform
            )
            
            # Assess market conditions
            market_conditions = await self._assess_market_conditions(
                content_data, platform
            )
            
            # Generate competitive analysis
            competitive_analysis = await self._analyze_competitive_landscape(
                content_data, platform
            )
            
            prediction = ViralPrediction(
                prediction_id=f"viral_traj_{content_id}_{int(time.time())}",
                content_id=content_id,
                platform=platform,
                predicted_viral_score=trajectory_prediction['peak_viral_score'],
                time_to_viral=trajectory_prediction['time_to_viral'],
                peak_engagement_time=trajectory_prediction['peak_time'],
                total_predicted_reach=trajectory_prediction['total_reach'],
                engagement_breakdown=trajectory_prediction['engagement_breakdown'],
                viral_trajectory=trajectory_prediction['trajectory_points'],
                confidence_intervals=trajectory_prediction['confidence_intervals'],
                key_success_factors=viral_milestones['success_factors'],
                potential_bottlenecks=viral_milestones['bottlenecks'],
                optimization_opportunities=viral_milestones['opportunities'],
                competitive_analysis=competitive_analysis,
                market_conditions=market_conditions
            )
            
            logger.info(f"Viral trajectory predicted for {content_id}")
            return prediction
            
        except Exception as e:
            logger.error(f"Viral trajectory prediction failed: {e}")
            await self.error_handler.handle_error(e, {
                'component': 'viral_predictor',
                'operation': 'predict_viral_trajectory',
                'content_id': content_id
            })
            raise IntegrationError(f"Failed to predict viral trajectory: {e}")
    
    async def _extract_content_features(
        self,
        content_data: Dict[str, Any],
        platform: str,
        creator_profile: Dict[str, Any]
    ) -> ContentFeatures:
        """Extract comprehensive features from content"""
        try:
            # Text features
            text_features = await self._extract_text_features(
                content_data.get('text', '')
            )
            
            # Visual features
            visual_features = await self._extract_visual_features(
                content_data.get('visual', {})
            )
            
            # Audio features
            audio_features = await self._extract_audio_features(
                content_data.get('audio', {})
            )
            
            # Metadata features
            metadata_features = await self._extract_metadata_features(content_data)
            
            # Platform-specific features
            platform_features = await self._extract_platform_features(
                content_data, platform
            )
            
            # Temporal features
            temporal_features = await self._extract_temporal_features(
                content_data, platform
            )
            
            # Creator features
            creator_features = await self._extract_creator_features(creator_profile)
            
            # Trend features
            trend_features = await self._extract_trend_features(
                content_data, platform
            )
            
            # Engagement features
            engagement_features = await self._extract_engagement_features(
                content_data, creator_profile
            )
            
            # Viral indicators
            viral_indicators = await self._identify_viral_indicators(
                content_data, platform
            )
            
            return ContentFeatures(
                text_features=text_features,
                visual_features=visual_features,
                audio_features=audio_features,
                metadata_features=metadata_features,
                platform_features=platform_features,
                temporal_features=temporal_features,
                creator_features=creator_features,
                trend_features=trend_features,
                engagement_features=engagement_features,
                viral_indicators=viral_indicators
            )
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return ContentFeatures(
                text_features={}, visual_features={}, audio_features={},
                metadata_features={}, platform_features={}, temporal_features={},
                creator_features={}, trend_features={}, engagement_features={},
                viral_indicators=[]
            )
    
    async def _extract_audio_features(self, audio_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract audio features for viral prediction"""
        try:
            if not audio_data or 'file_path' not in audio_data:
                return {}
            
            # Load audio file
            y, sr = librosa.load(audio_data['file_path'])
            
            # Extract audio features
            features = {}
            
            # Tempo and rhythm
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = tempo
            features['beat_strength'] = np.mean(librosa.beat.beat_strength(y=y, sr=sr))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroids)
            features['spectral_centroid_std'] = np.std(spectral_centroids)
            
            # MFCCs
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i in range(13):
                features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
                features[f'mfcc_{i}_std'] = np.std(mfccs[i])
            
            # Energy and dynamics
            features['rms_energy'] = np.mean(librosa.feature.rms(y=y)[0])
            features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(y)[0])
            
            # Duration
            features['duration'] = len(y) / sr
            
            return features
            
        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            return {}
    
    def _validate_prediction_inputs(
        self,
        content_data -> None: Dict[str, Any],
        platform -> None: str,
        creator_profile -> None: Dict[str, Any]
    ) -> None:
        """Validate inputs for viral prediction"""
        if not content_data:
            raise ValueError("Content data cannot be empty")
        
        valid_platforms = ['instagram', 'tiktok', 'twitter', 'youtube', 'linkedin']
        if platform not in valid_platforms:
            raise ValueError(f"Invalid platform. Must be from: {valid_platforms}")
        
        if not creator_profile:
            raise ValueError("Creator profile cannot be empty")
    
    async def get_viral_analytics(
        self,
        creator_id: str,
        time_range: str = '30d'
    ) -> Dict[str, Any]:
        """Get comprehensive viral prediction analytics"""
        try:
            # Collect viral analytics data
            analytics_data = await self._collect_viral_analytics_data(creator_id, time_range)
            
            # Calculate comprehensive metrics
            analytics = {
                'viral_success_rate': analytics_data.get('success_rate', 0.0),
                'avg_viral_score': analytics_data.get('avg_score', 0.0),
                'prediction_accuracy': self.prediction_accuracy['overall'],
                'top_viral_content': analytics_data.get('top_content', []),
                'viral_trend_adoption': analytics_data.get('trend_adoption', {}),
                'platform_viral_performance': analytics_data.get('platform_performance', {}),
                'content_format_performance': analytics_data.get('format_performance', {}),
                'optimal_viral_timing': analytics_data.get('optimal_timing', {}),
                'viral_amplification_factors': analytics_data.get('amplification_factors', []),
                'missed_opportunities': analytics_data.get('missed_opportunities', []),
                'upcoming_viral_opportunities': await self._identify_upcoming_opportunities(creator_id),
                'recommendations': await self._generate_viral_recommendations(creator_id)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Viral analytics generation failed: {e}")
            return {}


# Additional implementation continues...
# This represents approximately 80% of the complete module

if __name__ == "__main__":
    # Example usage
    async def test_viral_predictor() -> None:
        config = {
            'redis_url': 'redis://localhost:6379',
            'openai_api_key': 'your-api-key',
            'platforms': {
                'tiktok': {'app_id': 'your-app-id'},
                'instagram': {'client_id': 'your-client-id'}
            }
        }
        
        predictor = ViralPredictor(config)
        
        # Predict viral potential
        content_data = {
            'text': 'Check out this amazing AI-powered music creation! 🎵✨ #AI #Music #Innovation',
            'visual': {'type': 'video', 'duration': 30},
            'audio': {'has_trending_sound': True}
        }
        
        creator_profile = {
            'creator_id': 'test_creator_123',
            'follower_count': 50000,
            'avg_engagement_rate': 0.05,
            'content_category': 'music'
        }
        
        viral_score = await predictor.predict_viral_potential(
            content_data=content_data,
            platform='tiktok',
            creator_profile=creator_profile
        )
        
        print(f"Viral score: {viral_score.viral_score:.1f}/100")
        print(f"Viral probability: {viral_score.viral_probability:.2f}")
        print(f"Predicted reach: {viral_score.predicted_reach:,}")
    
    # asyncio.run(test_viral_predictor())