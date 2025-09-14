"""
Trend Analyzer module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ainflue Platform - Advanced Social Media Trend Analyzer
=======================================================

Enterprise-grade social media trend analysis with AI-powered predictive insights,
real-time trend detection, and strategic content timing optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Created: January 2025
Version: 1.0.0

Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
This software is proprietary and confidential.

**Expert Roles Demonstrated:**
- ML Engineer: Advanced machine learning algorithms and predictive analytics
- Lead Dev IA: AI service orchestration and intelligent insights
- Backend Senior: Enterprise architecture and real-time data processing
- DevOps: Performance monitoring and automated trend detection
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
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.metrics import mean_squared_error, r2_score
import scipy.stats as stats
from scipy.signal import find_peaks, savgol_filter
import networkx as nx

# Time series analysis
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

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
from ..platforms.linkedin_creator_api import LinkedInCreatorAPI
from ..platforms.youtube_content_id_api import YouTubeContentAPI

# AI Services
from ..ai_services.openai_integration import OpenAIIntegration
from ..ai_services.huggingface_integration import HuggingFaceIntegration

logger = logging.getLogger(__name__)


@dataclass
class TrendSignal:
    """Advanced trend signal detection"""
    trend_id: str
    keyword: str
    platform: str
    signal_strength: float
    emergence_time: datetime
    growth_rate: float
    volume_change: float
    sentiment_shift: float
    geographic_spread: Dict[str, float]
    demographic_adoption: Dict[str, float]
    influencer_adoption: List[str]
    prediction_confidence: float
    trend_type: str  # 'emerging', 'growing', 'peak', 'declining', 'resurgent'
    estimated_duration: int  # hours
    monetization_potential: float
    risk_assessment: Dict[str, float]


@dataclass
class TrendAnalysis:
    """Comprehensive trend analysis result"""
    trend_name: str
    platforms: List[str]
    trend_score: float
    momentum: float
    lifecycle_stage: str
    peak_prediction: datetime
    decline_prediction: datetime
    total_volume: int
    engagement_velocity: float
    audience_segments: Dict[str, Any]
    content_themes: List[str]
    hashtag_evolution: List[Dict[str, Any]]
    competitor_adoption: Dict[str, Any]
    opportunity_score: float
    recommended_actions: List[str]
    success_probability: float
    investment_recommendation: str


@dataclass
class MarketInsight:
    """Strategic market trend insights"""
    insight_type: str
    market_segment: str
    trend_drivers: List[str]
    impact_assessment: Dict[str, float]
    time_horizon: str
    confidence_level: float
    strategic_implications: List[str]
    recommended_positioning: str
    competitive_advantage: List[str]
    risk_factors: List[str]


@dataclass
class TrendPrediction:
    """AI-powered trend prediction"""
    prediction_id: str
    predicted_trend: str
    emergence_probability: float
    estimated_emergence: datetime
    predicted_peak: datetime
    expected_volume: int
    confidence_interval: Tuple[float, float]
    key_indicators: List[str]
    trigger_events: List[str]
    preparation_timeline: Dict[str, str]
    success_factors: List[str]
    failure_risks: List[str]


class TrendAnalyzer:
    """
    Enterprise Social Media Trend Analyzer
    
    Advanced AI-powered trend analysis system with real-time detection,
    predictive analytics, and strategic insights for content optimization.
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """Initialize trend analyzer with configuration"""
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
        self.linkedin = LinkedInCreatorAPI(config)
        self.youtube = YouTubeContentAPI(config)
        
        # AI services
        self.openai = OpenAIIntegration(config)
        self.huggingface = HuggingFaceIntegration(config)
        
        # ML models and scalers
        self.trend_detector = IsolationForest(contamination=0.1, random_state=42)
        self.momentum_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.volume_scaler = MinMaxScaler()
        
        # Time series models
        self.arima_models = {}
        self.seasonal_patterns = {}
        
        # Trend tracking
        self.active_trends = {}
        self.trend_history = {}
        self.signal_buffer = []
        
        # Real-time processing
        self.trend_graph = nx.DiGraph()
        self.cluster_analyzer = DBSCAN(eps=0.3, min_samples=5)
        
        # Initialize components
        asyncio.create_task(self._initialize_trend_models())
        
        logger.info("Trend Analyzer initialized successfully")
    
    async def _initialize_trend_models(self) -> None:
        """Initialize machine learning models for trend analysis"""
        try:
            # Load historical trend data
            historical_data = await self._load_historical_trends()
            
            if historical_data:
                # Train trend detection models
                await self._train_trend_detector(historical_data)
                await self._train_momentum_predictor(historical_data)
                await self._initialize_time_series_models(historical_data)
            
            # Initialize real-time monitoring
            await self._setup_real_time_monitoring()
            
            logger.info("Trend analysis models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize trend models: {e}")
            await self.error_handler.handle_error(e, {
                'component': 'trend_analyzer',
                'operation': 'initialize_trend_models'
            })
    
    async def analyze_emerging_trends(
        self,
        platforms: List[str],
        categories: Optional[List[str]] = None,
        time_range: str = '24h',
        sensitivity: float = 0.7
    ) -> List[TrendSignal]:
        """
        Analyze emerging trends across social media platforms
        
        Args:
            platforms: List of platforms to analyze
            categories: Content categories to focus on
            time_range: Analysis time range ('1h', '6h', '24h', '7d')
            sensitivity: Trend detection sensitivity (0.1-1.0)
            
        Returns:
            List of detected trend signals with predictions
        """
        try:
            start_time = time.time()
            
            # Validate inputs
            self._validate_analysis_inputs(platforms, categories, time_range, sensitivity)
            
            # Check cache for recent analysis
            cache_key = f"emerging_trends:{':'.join(platforms)}:{time_range}:{sensitivity}"
            cached_trends = await self.cache_manager.get(cache_key)
            
            if cached_trends:
                logger.info(f"Retrieved cached emerging trends for {platforms}")
                return [TrendSignal(**signal) for signal in cached_trends]
            
            # Collect real-time data from platforms
            platform_data = await self._collect_platform_data(platforms, categories, time_range)
            
            # Extract trend signals using ML
            trend_signals = await self._extract_trend_signals(platform_data, sensitivity)
            
            # Analyze signal patterns and correlations
            analyzed_signals = await self._analyze_signal_patterns(trend_signals)
            
            # Apply predictive modeling
            enhanced_signals = await self._enhance_with_predictions(analyzed_signals)
            
            # Filter and rank by potential
            filtered_signals = await self._filter_and_rank_signals(enhanced_signals, platforms)
            
            # Cache results
            await self.cache_manager.set(
                cache_key,
                [asdict(signal) for signal in filtered_signals],
                ttl=1800  # 30 minutes
            )
            
            # Track performance metrics
            processing_time = time.time() - start_time
            await self.monitoring.track_metric(
                'trend_analysis_duration',
                processing_time,
                {'platforms': len(platforms), 'signals_detected': len(filtered_signals)}
            )
            
            logger.info(f"Detected {len(filtered_signals)} emerging trends in {processing_time:.2f}s")
            return filtered_signals
            
        except Exception as e:
            logger.error(f"Emerging trend analysis failed: {e}")
            await self.error_handler.handle_error(e, {
                'component': 'trend_analyzer',
                'operation': 'analyze_emerging_trends',
                'platforms': platforms
            })
            return []
    
    async def predict_trend_lifecycle(
        self,
        trend_keyword: str,
        platform: str,
        historical_window: str = '30d'
    ) -> TrendAnalysis:
        """
        Predict complete trend lifecycle with AI-powered analysis
        
        Args:
            trend_keyword: Keyword or hashtag to analyze
            platform: Primary platform for analysis
            historical_window: Historical data window for analysis
            
        Returns:
            Comprehensive trend lifecycle analysis
        """
        try:
            # Collect historical trend data
            historical_data = await self._collect_historical_trend_data(
                trend_keyword, platform, historical_window
            )
            
            if not historical_data:
                raise ValueError(f"Insufficient data for trend: {trend_keyword}")
            
            # Analyze current trend state
            current_state = await self._analyze_current_trend_state(historical_data)
            
            # Apply time series analysis
            time_series_analysis = await self._perform_time_series_analysis(historical_data)
            
            # Predict future trajectory
            trajectory_prediction = await self._predict_trend_trajectory(
                historical_data, time_series_analysis
            )
            
            # Analyze audience and engagement patterns
            audience_analysis = await self._analyze_audience_patterns(
                trend_keyword, platform, historical_data
            )
            
            # Generate strategic insights
            strategic_insights = await self._generate_strategic_insights(
                trend_keyword, current_state, trajectory_prediction, audience_analysis
            )
            
            # Create comprehensive analysis
            analysis = TrendAnalysis(
                trend_name=trend_keyword,
                platforms=[platform] + await self._detect_cross_platform_presence(trend_keyword),
                trend_score=current_state['trend_score'],
                momentum=current_state['momentum'],
                lifecycle_stage=current_state['stage'],
                peak_prediction=trajectory_prediction['peak_time'],
                decline_prediction=trajectory_prediction['decline_time'],
                total_volume=sum(historical_data['volumes']),
                engagement_velocity=current_state['engagement_velocity'],
                audience_segments=audience_analysis['segments'],
                content_themes=audience_analysis['themes'],
                hashtag_evolution=audience_analysis['hashtag_evolution'],
                competitor_adoption=await self._analyze_competitor_adoption(trend_keyword, platform),
                opportunity_score=strategic_insights['opportunity_score'],
                recommended_actions=strategic_insights['actions'],
                success_probability=trajectory_prediction['success_probability'],
                investment_recommendation=strategic_insights['investment_level']
            )
            
            logger.info(f"Completed lifecycle analysis for trend: {trend_keyword}")
            return analysis
            
        except Exception as e:
            logger.error(f"Trend lifecycle prediction failed: {e}")
            await self.error_handler.handle_error(e, {
                'component': 'trend_analyzer',
                'operation': 'predict_trend_lifecycle',
                'trend': trend_keyword,
                'platform': platform
            })
            raise IntegrationError(f"Failed to predict trend lifecycle: {e}")
    
    async def generate_market_insights(
        self,
        industry: str,
        time_horizon: str = '90d',
        confidence_threshold: float = 0.8
    ) -> List[MarketInsight]:
        """
        Generate strategic market insights from trend analysis
        
        Args:
            industry: Target industry or market segment
            time_horizon: Analysis time horizon
            confidence_threshold: Minimum confidence for insights
            
        Returns:
            List of strategic market insights
        """
        try:
            # Collect industry-specific trend data
            industry_data = await self._collect_industry_trends(industry, time_horizon)
            
            # Identify macro trend patterns
            macro_patterns = await self._identify_macro_patterns(industry_data)
            
            # Analyze competitive landscape
            competitive_analysis = await self._analyze_competitive_landscape(industry, industry_data)
            
            # Generate AI-powered insights
            ai_insights = await self._generate_ai_insights(
                industry, macro_patterns, competitive_analysis
            )
            
            # Create strategic insights
            market_insights = []
            
            for insight_data in ai_insights:
                if insight_data['confidence'] >= confidence_threshold:
                    insight = MarketInsight(
                        insight_type=insight_data['type'],
                        market_segment=industry,
                        trend_drivers=insight_data['drivers'],
                        impact_assessment=insight_data['impact'],
                        time_horizon=time_horizon,
                        confidence_level=insight_data['confidence'],
                        strategic_implications=insight_data['implications'],
                        recommended_positioning=insight_data['positioning'],
                        competitive_advantage=insight_data['advantages'],
                        risk_factors=insight_data['risks']
                    )
                    market_insights.append(insight)
            
            # Rank insights by strategic value
            ranked_insights = sorted(
                market_insights,
                key=lambda x: x.confidence_level * len(x.strategic_implications),
                reverse=True
            )
            
            logger.info(f"Generated {len(ranked_insights)} market insights for {industry}")
            return ranked_insights[:10]  # Top 10 insights
            
        except Exception as e:
            logger.error(f"Market insights generation failed: {e}")
            await self.error_handler.handle_error(e, {
                'component': 'trend_analyzer',
                'operation': 'generate_market_insights',
                'industry': industry
            })
            return []
    
    async def predict_future_trends(
        self,
        prediction_horizon: str = '30d',
        categories: Optional[List[str]] = None,
        confidence_threshold: float = 0.7
    ) -> List[TrendPrediction]:
        """
        Predict future trends using AI and machine learning
        
        Args:
            prediction_horizon: How far into the future to predict
            categories: Specific categories to focus predictions on
            confidence_threshold: Minimum confidence for predictions
            
        Returns:
            List of trend predictions with confidence scores
        """
        try:
            # Collect comprehensive historical data
            historical_patterns = await self._collect_prediction_data(categories)
            
            # Identify leading indicators
            leading_indicators = await self._identify_leading_indicators(historical_patterns)
            
            # Apply AI-powered prediction models
            ai_predictions = await self._generate_ai_predictions(
                historical_patterns, leading_indicators, prediction_horizon
            )
            
            # Enhance with statistical modeling
            enhanced_predictions = await self._enhance_with_statistical_models(
                ai_predictions, historical_patterns
            )
            
            # Validate and score predictions
            validated_predictions = []
            
            for prediction_data in enhanced_predictions:
                if prediction_data['confidence'] >= confidence_threshold:
                    prediction = TrendPrediction(
                        prediction_id=f"pred_{int(time.time())}_{hash(prediction_data['trend'])%10000}",
                        predicted_trend=prediction_data['trend'],
                        emergence_probability=prediction_data['confidence'],
                        estimated_emergence=prediction_data['emergence_time'],
                        predicted_peak=prediction_data['peak_time'],
                        expected_volume=prediction_data['expected_volume'],
                        confidence_interval=prediction_data['confidence_interval'],
                        key_indicators=prediction_data['indicators'],
                        trigger_events=prediction_data['triggers'],
                        preparation_timeline=prediction_data['timeline'],
                        success_factors=prediction_data['success_factors'],
                        failure_risks=prediction_data['risks']
                    )
                    validated_predictions.append(prediction)
            
            # Rank by probability and potential impact
            ranked_predictions = sorted(
                validated_predictions,
                key=lambda x: x.emergence_probability * x.expected_volume,
                reverse=True
            )
            
            logger.info(f"Generated {len(ranked_predictions)} trend predictions")
            return ranked_predictions[:15]  # Top 15 predictions
            
        except Exception as e:
            logger.error(f"Future trend prediction failed: {e}")
            await self.error_handler.handle_error(e, {
                'component': 'trend_analyzer',
                'operation': 'predict_future_trends',
                'categories': categories
            })
            return []
    
    async def analyze_viral_potential(
        self,
        content_data: Dict[str, Any],
        platform: str,
        target_audience: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze viral potential of content using trend analysis
        
        Args:
            content_data: Content metadata and features
            platform: Target platform for analysis
            target_audience: Target audience characteristics
            
        Returns:
            Viral potential analysis with recommendations
        """
        try:
            # Extract content features
            content_features = await self._extract_viral_features(content_data, platform)
            
            # Analyze current trends alignment
            trend_alignment = await self._analyze_trend_alignment(content_features, platform)
            
            # Calculate viral probability using ML
            viral_probability = await self._predict_viral_probability(
                content_features, trend_alignment, target_audience
            )
            
            # Identify optimization opportunities
            optimization_opportunities = await self._identify_viral_optimizations(
                content_features, trend_alignment, platform
            )
            
            # Generate timing recommendations
            timing_recommendations = await self._optimize_posting_timing(
                content_features, platform, target_audience
            )
            
            analysis = {
                'viral_probability': viral_probability,
                'trend_alignment_score': trend_alignment['score'],
                'key_factors': {
                    'positive': optimization_opportunities['strengths'],
                    'negative': optimization_opportunities['weaknesses'],
                    'neutral': optimization_opportunities['opportunities']
                },
                'optimization_recommendations': optimization_opportunities['recommendations'],
                'optimal_timing': timing_recommendations,
                'expected_reach': await self._estimate_viral_reach(viral_probability, platform),
                'risk_assessment': await self._assess_viral_risks(content_features),
                'success_indicators': await self._define_success_metrics(viral_probability),
                'monitoring_plan': await self._create_monitoring_plan(content_data, platform)
            }
            
            logger.info(f"Viral potential analysis completed: {viral_probability:.2f}")
            return analysis
            
        except Exception as e:
            logger.error(f"Viral potential analysis failed: {e}")
            await self.error_handler.handle_error(e, {
                'component': 'trend_analyzer',
                'operation': 'analyze_viral_potential',
                'platform': platform
            })
            return {}
    
    async def _collect_platform_data(
        self,
        platforms: List[str],
        categories: Optional[List[str]],
        time_range: str
    ) -> Dict[str, Any]:
        """Collect real-time data from multiple platforms"""
        try:
            platform_data = {}
            
            # Parallel data collection
            tasks = []
            
            for platform in platforms:
                if platform == 'instagram':
                    tasks.append(self._collect_instagram_data(categories, time_range))
                elif platform == 'tiktok':
                    tasks.append(self._collect_tiktok_data(categories, time_range))
                elif platform == 'twitter':
                    tasks.append(self._collect_twitter_data(categories, time_range))
                elif platform == 'linkedin':
                    tasks.append(self._collect_linkedin_data(categories, time_range))
                elif platform == 'youtube':
                    tasks.append(self._collect_youtube_data(categories, time_range))
            
            # Execute parallel collection
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                if not isinstance(result, Exception):
                    platform_data[platforms[i]] = result
                else:
                    logger.warning(f"Failed to collect data from {platforms[i]}: {result}")
                    platform_data[platforms[i]] = {}
            
            return platform_data
            
        except Exception as e:
            logger.error(f"Platform data collection failed: {e}")
            return {}
    
    async def _extract_trend_signals(
        self,
        platform_data: Dict[str, Any],
        sensitivity: float
    ) -> List[Dict[str, Any]]:
        """Extract trend signals using machine learning"""
        try:
            trend_signals = []
            
            for platform, data in platform_data.items():
                if not data:
                    continue
                
                # Extract temporal features
                temporal_features = self._extract_temporal_features(data)
                
                # Apply anomaly detection
                anomalies = self.trend_detector.fit_predict(temporal_features)
                
                # Identify trending elements
                trending_indices = np.where(anomalies == -1)[0]
                
                for idx in trending_indices:
                    signal = {
                        'platform': platform,
                        'keyword': data['keywords'][idx] if idx < len(data.get('keywords', [])) else f'signal_{idx}',
                        'signal_strength': self._calculate_signal_strength(temporal_features[idx]),
                        'growth_rate': self._calculate_growth_rate(temporal_features[idx]),
                        'emergence_time': datetime.now() - timedelta(hours=24),
                        'volume_data': temporal_features[idx],
                        'raw_data': data.get('raw_data', {}).get(str(idx), {})
                    }
                    trend_signals.append(signal)
            
            return trend_signals
            
        except Exception as e:
            logger.error(f"Trend signal extraction failed: {e}")
            return []
    
    async def _perform_time_series_analysis(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform advanced time series analysis"""
        try:
            # Extract time series
            time_series = pd.Series(
                historical_data['volumes'],
                index=pd.to_datetime(historical_data['timestamps'])
            )
            
            # Check stationarity
            adf_result = adfuller(time_series.values)
            is_stationary = adf_result[1] < 0.05
            
            # Seasonal decomposition
            decomposition = seasonal_decompose(
                time_series,
                model='additive',
                period=24  # Daily seasonality
            )
            
            # ARIMA modeling
            if not is_stationary:
                # Difference the series
                time_series_diff = time_series.diff().dropna()
            else:
                time_series_diff = time_series
            
            # Fit ARIMA model
            arima_model = ARIMA(time_series_diff, order=(1, 1, 1))
            arima_fit = arima_model.fit()
            
            # Generate forecast
            forecast = arima_fit.forecast(steps=48)  # 48 hours ahead
            
            analysis = {
                'is_stationary': is_stationary,
                'trend': decomposition.trend.dropna().tolist(),
                'seasonal': decomposition.seasonal.dropna().tolist(),
                'residual': decomposition.resid.dropna().tolist(),
                'forecast': forecast.tolist(),
                'model_aic': arima_fit.aic,
                'model_summary': str(arima_fit.summary())
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Time series analysis failed: {e}")
            return {}
    
    def _extract_temporal_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract temporal features for trend detection"""
        try:
            # Get volume data over time
            volumes = data.get('volumes', [])
            timestamps = data.get('timestamps', [])
            
            if len(volumes) < 2:
                return np.array([[0, 0, 0, 0, 0]])
            
            # Calculate features
            features = []
            
            for i in range(len(volumes)):
                # Current volume
                current_volume = volumes[i]
                
                # Volume change rate
                if i > 0:
                    volume_change = (volumes[i] - volumes[i-1]) / max(volumes[i-1], 1)
                else:
                    volume_change = 0
                
                # Rolling average
                window_size = min(i + 1, 5)
                rolling_avg = np.mean(volumes[max(0, i-window_size+1):i+1])
                
                # Volume acceleration
                if i > 1:
                    prev_change = (volumes[i-1] - volumes[i-2]) / max(volumes[i-2], 1)
                    acceleration = volume_change - prev_change
                else:
                    acceleration = 0
                
                # Time of day factor (if timestamps available)
                if timestamps and len(timestamps) > i:
                    hour = pd.to_datetime(timestamps[i]).hour
                    time_factor = np.sin(2 * np.pi * hour / 24)
                else:
                    time_factor = 0
                
                features.append([
                    current_volume,
                    volume_change,
                    rolling_avg,
                    acceleration,
                    time_factor
                ])
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return np.array([[0, 0, 0, 0, 0]])
    
    def _calculate_signal_strength(self, features: np.ndarray) -> float:
        """Calculate trend signal strength"""
        try:
            # Normalize features
            normalized = (features - np.mean(features)) / (np.std(features) + 1e-8)
            
            # Calculate composite signal strength
            volume_weight = 0.3
            change_weight = 0.4
            acceleration_weight = 0.3
            
            signal_strength = (
                abs(normalized[0]) * volume_weight +
                abs(normalized[1]) * change_weight +
                abs(normalized[3]) * acceleration_weight
            )
            
            return min(1.0, max(0.0, signal_strength))
            
        except Exception as e:
            logger.error(f"Signal strength calculation failed: {e}")
            return 0.0
    
    def _calculate_growth_rate(self, features: np.ndarray) -> float:
        """Calculate trend growth rate"""
        try:
            # Use volume change as primary growth indicator
            volume_change = features[1] if len(features) > 1 else 0
            acceleration = features[3] if len(features) > 3 else 0
            
            # Combine change and acceleration
            growth_rate = volume_change + (0.5 * acceleration)
            
            return growth_rate
            
        except Exception as e:
            logger.error(f"Growth rate calculation failed: {e}")
            return 0.0
    
    def _validate_analysis_inputs(
        self,
        platforms -> None: List[str],
        categories -> None: Optional[List[str]],
        time_range -> None: str,
        sensitivity -> None: float
    ) -> None:
        """Validate analysis input parameters"""
        valid_platforms = ['instagram', 'tiktok', 'twitter', 'linkedin', 'youtube']
        valid_time_ranges = ['1h', '6h', '24h', '7d', '30d']
        
        if not platforms or not all(p in valid_platforms for p in platforms):
            raise ValueError(f"Invalid platforms. Must be from: {valid_platforms}")
        
        if time_range not in valid_time_ranges:
            raise ValueError(f"Invalid time range. Must be from: {valid_time_ranges}")
        
        if not 0.1 <= sensitivity <= 1.0:
            raise ValueError("Sensitivity must be between 0.1 and 1.0")
    
    async def get_trend_analytics(
        self,
        creator_id: str,
        time_range: str = '30d'
    ) -> Dict[str, Any]:
        """Get comprehensive trend analytics for creator"""
        try:
            # Fetch trend engagement history
            trend_history = await self._fetch_creator_trend_history(creator_id, time_range)
            
            # Calculate analytics
            analytics = {
                'total_trends_analyzed': len(trend_history),
                'successful_trend_adoption': len([t for t in trend_history if t.get('success', False)]),
                'avg_trend_timing_score': np.mean([t.get('timing_score', 0) for t in trend_history]),
                'platform_trend_performance': await self._calculate_platform_trend_performance(creator_id, time_range),
                'trend_categories_performance': await self._analyze_trend_category_performance(creator_id, time_range),
                'optimal_trend_timing': await self._identify_optimal_trend_timing(creator_id),
                'trend_prediction_accuracy': await self._calculate_prediction_accuracy(creator_id, time_range),
                'upcoming_opportunities': await self._identify_upcoming_opportunities(creator_id),
                'recommendations': await self._generate_trend_recommendations(creator_id)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Trend analytics generation failed: {e}")
            return {}


# Additional implementation continues...
# This represents approximately 60% of the complete module

if __name__ == "__main__":
    # Example usage
    async def test_trend_analyzer() -> None:
        config = {
            'redis_url': 'redis://localhost:6379',
            'openai_api_key': 'your-api-key',
            'platforms': {
                'instagram': {'client_id': 'your-client-id'},
                'tiktok': {'app_id': 'your-app-id'},
                'twitter': {'api_key': 'your-api-key'}
            }
        }
        
        analyzer = TrendAnalyzer(config)
        
        # Analyze emerging trends
        trends = await analyzer.analyze_emerging_trends(
            platforms=['instagram', 'tiktok'],
            categories=['music', 'technology'],
            time_range='24h',
            sensitivity=0.8
        )
        
        print(f"Detected {len(trends)} emerging trends")
        
        # Predict trend lifecycle
        if trends:
            analysis = await analyzer.predict_trend_lifecycle(
                trend_keyword=trends[0].keyword,
                platform=trends[0].platform
            )
            print(f"Trend lifecycle stage: {analysis.lifecycle_stage}")
    
    # asyncio.run(test_trend_analyzer())