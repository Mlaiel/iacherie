# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Trend Detection Tests - Enterprise Grade Test Suite

Comprehensive tests for trend detection, market analysis, virality prediction,
and competitive intelligence systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING ⚠️
Contact: mlaiel@live.de - Unauthorized use STRICTLY PROHIBITED
"""

import pytest
import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import asyncio
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Tuple
from scipy import stats
import networkx as nx

from ai.ml.trend_detection import (
    TrendDetector, MarketTrendAnalyzer, ContentTrendPredictor,
    ViralityPredictor, TrendForecastingEngine, SeasonalTrendAnalyzer,
    CompetitiveIntelligenceEngine, MarketOpportunityDetector,
    InfluencerTrendAnalyzer, ContentPerformancePredictor,
    TrendMetrics, SocialMediaTrendAnalyzer, CreatorMarketAnalyzer
)


class TestTrendDetector:
    """Tests for basic trend detection functionality"""
    
    def test_init_trend_detector(self):
        """Test trend detector initialization"""
        detector = TrendDetector(
            time_window="7d",
            min_trend_strength=0.3,
            detection_algorithms=["momentum", "breakout", "seasonal"],
            enable_anomaly_detection=True
        )
        
        assert detector.time_window == "7d"
        assert detector.min_trend_strength == 0.3
        assert len(detector.detection_algorithms) == 3
        assert detector.enable_anomaly_detection

    def test_momentum_trend_detection(self, sample_trend_data):
        """Test momentum-based trend detection"""
        detector = TrendDetector(detection_algorithms=["momentum"])
        
        # Use sample trend data
        trends = detector.detect_momentum_trends(sample_trend_data)
        
        assert isinstance(trends, dict)
        assert "trend_direction" in trends
        assert "momentum_strength" in trends
        assert "acceleration" in trends
        assert trends["trend_direction"] in ["upward", "downward", "stable"]

    def test_breakout_trend_detection(self, sample_trend_data):
        """Test breakout pattern detection"""
        detector = TrendDetector(detection_algorithms=["breakout"])
        
        # Mock breakout detection
        with patch.object(detector, 'detect_breakouts') as mock_breakout:
            mock_breakout.return_value = {
                "breakout_detected": True,
                "breakout_type": "upward_breakout",
                "breakout_strength": 0.75,
                "breakout_timestamp": datetime.now().isoformat(),
                "resistance_level": 150.0,
                "support_level": 100.0
            }
            
            breakouts = detector.detect_breakouts(sample_trend_data)
            
            assert "breakout_detected" in breakouts
            assert "breakout_type" in breakouts
            assert "breakout_strength" in breakouts
            assert breakouts["breakout_detected"] is True

    def test_seasonal_trend_analysis(self):
        """Test seasonal trend pattern detection"""
        detector = TrendDetector(detection_algorithms=["seasonal"])
        
        # Generate sample seasonal data
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
        # Add seasonal pattern (higher in summer, lower in winter)
        seasonal_component = 50 * np.sin(2 * np.pi * dates.dayofyear / 365.25)
        trend_component = np.linspace(100, 120, len(dates))
        noise = np.random.normal(0, 10, len(dates))
        values = seasonal_component + trend_component + noise
        
        seasonal_data = pd.DataFrame({
            'date': dates,
            'value': values
        })
        
        seasonal_trends = detector.detect_seasonal_patterns(seasonal_data)
        
        assert isinstance(seasonal_trends, dict)
        assert "seasonal_strength" in seasonal_trends
        assert "seasonal_period" in seasonal_trends
        assert "peak_seasons" in seasonal_trends
        assert "trough_seasons" in seasonal_trends

    def test_anomaly_detection_in_trends(self, sample_trend_data):
        """Test anomaly detection in trend data"""
        detector = TrendDetector(enable_anomaly_detection=True)
        
        # Add some anomalous points to sample data
        anomalous_data = sample_trend_data.copy()
        anomalous_data.iloc[50, anomalous_data.columns.get_loc('trend_score')] = 999  # Anomaly
        
        anomalies = detector.detect_trend_anomalies(anomalous_data)
        
        assert isinstance(anomalies, list)
        assert len(anomalies) > 0
        assert all("timestamp" in anomaly for anomaly in anomalies)
        assert all("anomaly_score" in anomaly for anomaly in anomalies)
        assert all("anomaly_type" in anomaly for anomaly in anomalies)

    def test_trend_strength_calculation(self):
        """Test trend strength calculation"""
        detector = TrendDetector()
        
        # Mock time series with clear trend
        upward_trend = np.array([10, 12, 14, 16, 18, 20, 22, 24, 26, 28])
        downward_trend = np.array([30, 28, 26, 24, 22, 20, 18, 16, 14, 12])
        no_trend = np.array([15, 16, 14, 17, 15, 16, 15, 14, 16, 15])
        
        upward_strength = detector.calculate_trend_strength(upward_trend)
        downward_strength = detector.calculate_trend_strength(downward_trend)
        no_trend_strength = detector.calculate_trend_strength(no_trend)
        
        assert upward_strength > 0.8  # Strong upward trend
        assert downward_strength > 0.8  # Strong downward trend (absolute value)
        assert no_trend_strength < 0.3  # Weak or no trend

    def test_multi_timeframe_trend_analysis(self, sample_trend_data):
        """Test trend analysis across multiple timeframes"""
        detector = TrendDetector()
        
        timeframes = ["1h", "4h", "1d", "1w", "1m"]
        
        multi_trend_analysis = {}
        for timeframe in timeframes:
            with patch.object(detector, 'analyze_timeframe_trend') as mock_analyze:
                mock_analyze.return_value = {
                    "timeframe": timeframe,
                    "trend_direction": np.random.choice(["upward", "downward", "stable"]),
                    "trend_strength": np.random.uniform(0.2, 0.9),
                    "confidence": np.random.uniform(0.7, 0.95)
                }
                
                trend_result = detector.analyze_timeframe_trend(sample_trend_data, timeframe)
                multi_trend_analysis[timeframe] = trend_result
        
        assert len(multi_trend_analysis) == 5
        assert all("trend_direction" in result for result in multi_trend_analysis.values())
        assert all("trend_strength" in result for result in multi_trend_analysis.values())


class TestMarketTrendAnalyzer:
    """Tests for market trend analysis functionality"""
    
    def test_init_market_analyzer(self):
        """Test market trend analyzer initialization"""
        analyzer = MarketTrendAnalyzer(
            market_sectors=["technology", "healthcare", "finance", "entertainment"],
            data_sources=["social_media", "news", "search_trends", "financial_data"],
            enable_cross_sector_analysis=True
        )
        
        assert len(analyzer.market_sectors) == 4
        assert len(analyzer.data_sources) == 4
        assert analyzer.enable_cross_sector_analysis

    def test_sector_trend_analysis(self):
        """Test sector-specific trend analysis"""
        analyzer = MarketTrendAnalyzer(market_sectors=["technology"])
        
        # Mock technology sector data
        tech_data = {
            "keywords": ["AI", "machine learning", "blockchain", "cloud computing"],
            "companies": ["TechCorp", "InnovateTech", "FutureSoft"],
            "metrics": {
                "search_volume": np.random.randint(1000, 10000, 30),
                "social_mentions": np.random.randint(500, 5000, 30),
                "news_sentiment": np.random.uniform(-1, 1, 30)
            }
        }
        
        with patch.object(analyzer, 'analyze_sector_trends') as mock_analyze:
            mock_analyze.return_value = {
                "sector": "technology",
                "overall_trend": "growth",
                "trend_strength": 0.78,
                "key_drivers": ["AI adoption", "cloud migration", "digital transformation"],
                "emerging_themes": ["generative AI", "edge computing", "quantum computing"],
                "market_sentiment": "optimistic",
                "growth_indicators": {
                    "search_trend": "increasing",
                    "social_engagement": "high",
                    "investment_flow": "positive"
                }
            }
            
            sector_trends = analyzer.analyze_sector_trends("technology", tech_data)
            
            assert "sector" in sector_trends
            assert "overall_trend" in sector_trends
            assert "key_drivers" in sector_trends
            assert "emerging_themes" in sector_trends

    def test_cross_sector_correlation_analysis(self):
        """Test cross-sector correlation analysis"""
        analyzer = MarketTrendAnalyzer(
            market_sectors=["technology", "healthcare", "finance"],
            enable_cross_sector_analysis=True
        )
        
        # Mock multi-sector data
        sector_data = {
            "technology": np.random.randn(100),
            "healthcare": np.random.randn(100),
            "finance": np.random.randn(100)
        }
        
        correlations = analyzer.analyze_cross_sector_correlations(sector_data)
        
        assert isinstance(correlations, dict)
        assert "correlation_matrix" in correlations
        assert "significant_correlations" in correlations
        assert "sector_relationships" in correlations

    def test_market_sentiment_aggregation(self):
        """Test market sentiment aggregation across sources"""
        analyzer = MarketTrendAnalyzer(
            data_sources=["social_media", "news", "search_trends"]
        )
        
        # Mock sentiment data from different sources
        sentiment_data = {
            "social_media": {"sentiment": 0.6, "volume": 10000, "confidence": 0.8},
            "news": {"sentiment": 0.4, "volume": 500, "confidence": 0.9},
            "search_trends": {"sentiment": 0.7, "volume": 25000, "confidence": 0.7}
        }
        
        aggregated_sentiment = analyzer.aggregate_market_sentiment(sentiment_data)
        
        assert isinstance(aggregated_sentiment, dict)
        assert "overall_sentiment" in aggregated_sentiment
        assert "weighted_sentiment" in aggregated_sentiment
        assert "sentiment_consensus" in aggregated_sentiment
        assert "source_reliability" in aggregated_sentiment

    def test_market_volatility_analysis(self):
        """Test market volatility analysis"""
        analyzer = MarketTrendAnalyzer()
        
        # Generate sample market data with varying volatility
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        prices = 100 * np.exp(np.random.randn(100) * 0.02).cumprod()
        
        market_data = pd.DataFrame({
            'date': dates,
            'price': prices,
            'volume': np.random.randint(1000000, 10000000, 100)
        })
        
        volatility_analysis = analyzer.analyze_market_volatility(market_data)
        
        assert isinstance(volatility_analysis, dict)
        assert "volatility_measure" in volatility_analysis
        assert "volatility_regime" in volatility_analysis
        assert "risk_level" in volatility_analysis
        assert "stability_score" in volatility_analysis


class TestContentTrendPredictor:
    """Tests for content trend prediction"""
    
    def test_init_content_predictor(self):
        """Test content trend predictor initialization"""
        predictor = ContentTrendPredictor(
            content_categories=["music", "technology", "lifestyle", "education"],
            prediction_horizon="30d",
            model_type="neural_network",
            enable_feature_engineering=True
        )
        
        assert len(predictor.content_categories) == 4
        assert predictor.prediction_horizon == "30d"
        assert predictor.model_type == "neural_network"
        assert predictor.enable_feature_engineering

    def test_content_feature_extraction(self):
        """Test content feature extraction for trend prediction"""
        predictor = ContentTrendPredictor(enable_feature_engineering=True)
        
        # Mock content data
        content_data = {
            "content_id": "content_001",
            "title": "Amazing AI Technology Breakthrough",
            "description": "Revolutionary new AI system that changes everything",
            "category": "technology",
            "tags": ["AI", "innovation", "breakthrough", "technology"],
            "creator_metrics": {
                "follower_count": 50000,
                "engagement_rate": 0.05,
                "content_frequency": 3  # posts per week
            },
            "content_metrics": {
                "length": 150,
                "reading_time": 2,
                "multimedia_count": 2
            },
            "temporal_features": {
                "posting_time": "18:00",
                "day_of_week": "Tuesday",
                "season": "spring"
            }
        }
        
        features = predictor.extract_content_features(content_data)
        
        assert isinstance(features, dict)
        assert "textual_features" in features
        assert "creator_features" in features
        assert "content_features" in features
        assert "temporal_features" in features

    def test_viral_potential_prediction(self):
        """Test viral potential prediction for content"""
        predictor = ContentTrendPredictor()
        
        with patch.object(predictor, 'predict_viral_potential') as mock_predict:
            mock_predict.return_value = {
                "viral_probability": 0.78,
                "predicted_reach": 250000,
                "predicted_engagement": 12500,
                "time_to_peak": "6 hours",
                "viral_factors": [
                    {"factor": "trending_topic", "contribution": 0.35},
                    {"factor": "creator_influence", "contribution": 0.25},
                    {"factor": "content_quality", "contribution": 0.18}
                ],
                "confidence_interval": [0.65, 0.91]
            }
            
            content_features = {"feature_vector": np.random.rand(50)}
            viral_prediction = predictor.predict_viral_potential(content_features)
            
            assert "viral_probability" in viral_prediction
            assert "predicted_reach" in viral_prediction
            assert "viral_factors" in viral_prediction
            assert 0 <= viral_prediction["viral_probability"] <= 1

    def test_trending_topic_prediction(self):
        """Test trending topic prediction"""
        predictor = ContentTrendPredictor()
        
        # Mock historical topic data
        topic_history = {
            "AI": [100, 120, 150, 200, 250, 300, 280, 320],
            "blockchain": [50, 45, 60, 55, 70, 65, 80, 75],
            "sustainability": [80, 90, 95, 110, 130, 140, 160, 180],
            "gaming": [200, 190, 210, 205, 220, 240, 260, 280]
        }
        
        with patch.object(predictor, 'predict_trending_topics') as mock_topics:
            mock_topics.return_value = {
                "predicted_topics": [
                    {"topic": "AI", "predicted_score": 350, "growth_rate": 0.15, "confidence": 0.85},
                    {"topic": "sustainability", "predicted_score": 200, "growth_rate": 0.12, "confidence": 0.78},
                    {"topic": "gaming", "predicted_score": 310, "growth_rate": 0.08, "confidence": 0.72}
                ],
                "emerging_topics": [
                    {"topic": "quantum_computing", "predicted_score": 120, "emergence_probability": 0.65}
                ],
                "declining_topics": [
                    {"topic": "blockchain", "predicted_score": 70, "decline_rate": -0.05}
                ]
            }
            
            trending_predictions = predictor.predict_trending_topics(topic_history)
            
            assert "predicted_topics" in trending_predictions
            assert "emerging_topics" in trending_predictions
            assert "declining_topics" in trending_predictions

    def test_content_performance_forecasting(self):
        """Test content performance forecasting"""
        predictor = ContentTrendPredictor(prediction_horizon="7d")
        
        # Mock content performance history
        performance_history = {
            "views": [1000, 2500, 4000, 6500, 8000, 9500, 10500],
            "likes": [50, 125, 200, 325, 400, 475, 525],
            "shares": [10, 25, 40, 65, 80, 95, 105],
            "comments": [5, 12, 20, 32, 40, 47, 52]
        }
        
        forecast = predictor.forecast_content_performance(
            performance_history, prediction_days=7
        )
        
        assert isinstance(forecast, dict)
        assert "predicted_views" in forecast
        assert "predicted_engagement" in forecast
        assert "performance_trend" in forecast
        assert "confidence_bounds" in forecast


class TestViralityPredictor:
    """Tests for virality prediction functionality"""
    
    def test_init_virality_predictor(self):
        """Test virality predictor initialization"""
        predictor = ViralityPredictor(
            viral_threshold=10000,  # Minimum views for viral content
            prediction_window="24h",
            feature_set="comprehensive",
            enable_real_time_prediction=True
        )
        
        assert predictor.viral_threshold == 10000
        assert predictor.prediction_window == "24h"
        assert predictor.feature_set == "comprehensive"
        assert predictor.enable_real_time_prediction

    def test_viral_pattern_recognition(self):
        """Test viral pattern recognition"""
        predictor = ViralityPredictor()
        
        # Mock engagement patterns (typical viral vs non-viral)
        viral_pattern = np.array([100, 500, 2000, 8000, 25000, 60000, 100000, 120000])
        non_viral_pattern = np.array([50, 80, 120, 150, 180, 200, 220, 240])
        
        viral_score = predictor.recognize_viral_pattern(viral_pattern)
        non_viral_score = predictor.recognize_viral_pattern(non_viral_pattern)
        
        assert viral_score > non_viral_score
        assert viral_score > 0.7  # High viral probability
        assert non_viral_score < 0.3  # Low viral probability

    def test_early_viral_detection(self):
        """Test early viral detection within first few hours"""
        predictor = ViralityPredictor(enable_real_time_prediction=True)
        
        # Mock early engagement data (first 2 hours)
        early_metrics = {
            "views": [100, 300, 800, 1500],  # Rapid growth
            "likes": [10, 35, 85, 160],
            "shares": [2, 8, 20, 40],
            "comments": [1, 4, 10, 18],
            "timestamps": [
                datetime.now() - timedelta(minutes=120),
                datetime.now() - timedelta(minutes=90),
                datetime.now() - timedelta(minutes=60),
                datetime.now() - timedelta(minutes=30)
            ]
        }
        
        with patch.object(predictor, 'predict_early_virality') as mock_early:
            mock_early.return_value = {
                "early_viral_probability": 0.82,
                "predicted_24h_views": 50000,
                "growth_velocity": 1.8,  # Views doubling rate per hour
                "viral_indicators": [
                    "rapid_initial_growth",
                    "high_engagement_rate",
                    "accelerating_shares"
                ],
                "time_to_peak": "4-6 hours"
            }
            
            early_prediction = predictor.predict_early_virality(early_metrics)
            
            assert "early_viral_probability" in early_prediction
            assert "predicted_24h_views" in early_prediction
            assert "growth_velocity" in early_prediction
            assert early_prediction["early_viral_probability"] > 0.5

    def test_network_effect_analysis(self):
        """Test network effect analysis for viral spread"""
        predictor = ViralityPredictor()
        
        # Mock social network data
        network_data = {
            "initial_sharers": [
                {"user_id": "user_1", "follower_count": 10000, "influence_score": 0.7},
                {"user_id": "user_2", "follower_count": 50000, "influence_score": 0.9},
                {"user_id": "user_3", "follower_count": 5000, "influence_score": 0.4}
            ],
            "sharing_patterns": {
                "cascade_depth": 3,
                "branching_factor": 2.5,
                "cross_platform_spread": True
            }
        }
        
        with patch.object(predictor, 'analyze_network_effects') as mock_network:
            mock_network.return_value = {
                "network_amplification": 3.2,
                "influential_nodes": 2,
                "cascade_potential": 0.78,
                "cross_platform_boost": 0.15,
                "estimated_reach": 180000
            }
            
            network_analysis = predictor.analyze_network_effects(network_data)
            
            assert "network_amplification" in network_analysis
            assert "cascade_potential" in network_analysis
            assert "estimated_reach" in network_analysis

    def test_content_virality_factors(self):
        """Test analysis of content factors contributing to virality"""
        predictor = ViralityPredictor()
        
        # Mock content characteristics
        content_characteristics = {
            "emotional_appeal": 0.85,
            "novelty_score": 0.72,
            "relatability": 0.68,
            "shareability": 0.91,
            "format": "video",
            "length": 45,  # seconds
            "has_trending_topic": True,
            "has_call_to_action": True,
            "visual_quality": 0.88,
            "audio_quality": 0.82
        }
        
        virality_factors = predictor.analyze_virality_factors(content_characteristics)
        
        assert isinstance(virality_factors, dict)
        assert "factor_contributions" in virality_factors
        assert "overall_virality_score" in virality_factors
        assert "improvement_suggestions" in virality_factors


class TestTrendForecastingEngine:
    """Tests for trend forecasting functionality"""
    
    def test_init_forecasting_engine(self):
        """Test trend forecasting engine initialization"""
        engine = TrendForecastingEngine(
            forecasting_models=["ARIMA", "LSTM", "Prophet"],
            forecast_horizons=["1d", "1w", "1m", "3m"],
            enable_ensemble_forecasting=True,
            confidence_intervals=[0.8, 0.95]
        )
        
        assert len(engine.forecasting_models) == 3
        assert len(engine.forecast_horizons) == 4
        assert engine.enable_ensemble_forecasting
        assert engine.confidence_intervals == [0.8, 0.95]

    def test_time_series_forecasting(self, sample_trend_data):
        """Test time series forecasting"""
        engine = TrendForecastingEngine(forecasting_models=["ARIMA"])
        
        # Use sample trend data for forecasting
        with patch.object(engine, 'forecast_time_series') as mock_forecast:
            mock_forecast.return_value = {
                "forecast_values": [105, 108, 112, 115, 118, 120, 122],
                "confidence_intervals": {
                    "lower_80": [100, 102, 105, 107, 109, 111, 113],
                    "upper_80": [110, 114, 119, 123, 127, 129, 131],
                    "lower_95": [98, 99, 102, 104, 106, 108, 110],
                    "upper_95": [112, 117, 122, 126, 130, 132, 134]
                },
                "model_performance": {
                    "mae": 2.3,
                    "rmse": 3.1,
                    "mape": 0.028
                },
                "trend_direction": "upward",
                "forecast_period": "7d"
            }
            
            forecast = engine.forecast_time_series(
                sample_trend_data, forecast_days=7, model="ARIMA"
            )
            
            assert "forecast_values" in forecast
            assert "confidence_intervals" in forecast
            assert "model_performance" in forecast
            assert len(forecast["forecast_values"]) == 7

    def test_ensemble_forecasting(self, sample_trend_data):
        """Test ensemble forecasting combining multiple models"""
        engine = TrendForecastingEngine(
            forecasting_models=["ARIMA", "LSTM", "Prophet"],
            enable_ensemble_forecasting=True
        )
        
        with patch.object(engine, 'ensemble_forecast') as mock_ensemble:
            mock_ensemble.return_value = {
                "ensemble_forecast": [103, 106, 109, 112, 115],
                "model_weights": {
                    "ARIMA": 0.35,
                    "LSTM": 0.40,
                    "Prophet": 0.25
                },
                "individual_forecasts": {
                    "ARIMA": [102, 105, 108, 111, 114],
                    "LSTM": [104, 107, 110, 113, 116],
                    "Prophet": [103, 106, 109, 112, 115]
                },
                "ensemble_confidence": 0.87,
                "forecast_uncertainty": 0.15
            }
            
            ensemble_result = engine.ensemble_forecast(sample_trend_data, forecast_days=5)
            
            assert "ensemble_forecast" in ensemble_result
            assert "model_weights" in ensemble_result
            assert "individual_forecasts" in ensemble_result
            assert sum(ensemble_result["model_weights"].values()) == pytest.approx(1.0)

    def test_seasonal_decomposition_forecasting(self):
        """Test seasonal decomposition for forecasting"""
        engine = TrendForecastingEngine()
        
        # Generate seasonal time series
        dates = pd.date_range(start='2023-01-01', periods=365, freq='D')
        trend = np.linspace(100, 150, 365)
        seasonal = 20 * np.sin(2 * np.pi * np.arange(365) / 365.25 * 4)  # Quarterly seasonality
        noise = np.random.normal(0, 5, 365)
        values = trend + seasonal + noise
        
        seasonal_data = pd.DataFrame({
            'date': dates,
            'value': values
        })
        
        with patch.object(engine, 'seasonal_decompose_forecast') as mock_seasonal:
            mock_seasonal.return_value = {
                "trend_component": trend[-30:].tolist(),
                "seasonal_component": seasonal[-30:].tolist(),
                "residual_component": noise[-30:].tolist(),
                "forecast": (trend[-1] + seasonal[-30:] + np.mean(noise[-30:])).tolist(),
                "seasonal_strength": 0.68,
                "trend_strength": 0.85
            }
            
            seasonal_forecast = engine.seasonal_decompose_forecast(seasonal_data, forecast_days=30)
            
            assert "trend_component" in seasonal_forecast
            assert "seasonal_component" in seasonal_forecast
            assert "forecast" in seasonal_forecast
            assert "seasonal_strength" in seasonal_forecast

    def test_regime_change_detection(self, sample_trend_data):
        """Test regime change detection in forecasting"""
        engine = TrendForecastingEngine()
        
        # Mock regime change detection
        with patch.object(engine, 'detect_regime_changes') as mock_regime:
            mock_regime.return_value = {
                "regime_changes": [
                    {"date": "2024-06-15", "type": "trend_break", "significance": 0.92},
                    {"date": "2024-09-20", "type": "volatility_change", "significance": 0.78}
                ],
                "current_regime": {
                    "start_date": "2024-09-20",
                    "regime_type": "high_volatility_upward",
                    "stability": 0.65
                },
                "forecast_adjustments": {
                    "confidence_reduction": 0.15,
                    "prediction_interval_widening": 0.25
                }
            }
            
            regime_analysis = engine.detect_regime_changes(sample_trend_data)
            
            assert "regime_changes" in regime_analysis
            assert "current_regime" in regime_analysis
            assert "forecast_adjustments" in regime_analysis


class TestCompetitiveIntelligenceEngine:
    """Tests for competitive intelligence functionality"""
    
    def test_init_competitive_intelligence(self):
        """Test competitive intelligence engine initialization"""
        engine = CompetitiveIntelligenceEngine(
            target_company="TechCorp",
            competitors=["CompetitorA", "CompetitorB", "CompetitorC"],
            analysis_domains=["social_media", "news", "patents", "hiring"],
            enable_automated_monitoring=True
        )
        
        assert engine.target_company == "TechCorp"
        assert len(engine.competitors) == 3
        assert len(engine.analysis_domains) == 4
        assert engine.enable_automated_monitoring

    def test_competitor_trend_analysis(self):
        """Test competitor trend analysis"""
        engine = CompetitiveIntelligenceEngine(
            target_company="TechCorp",
            competitors=["CompetitorA", "CompetitorB"]
        )
        
        # Mock competitor data
        competitor_metrics = {
            "TechCorp": {
                "social_mentions": 5000,
                "sentiment": 0.65,
                "market_share": 0.25,
                "innovation_score": 0.78
            },
            "CompetitorA": {
                "social_mentions": 3500,
                "sentiment": 0.58,
                "market_share": 0.18,
                "innovation_score": 0.72
            },
            "CompetitorB": {
                "social_mentions": 4200,
                "sentiment": 0.62,
                "market_share": 0.22,
                "innovation_score": 0.68
            }
        }
        
        with patch.object(engine, 'analyze_competitor_trends') as mock_analyze:
            mock_analyze.return_value = {
                "market_position": {
                    "TechCorp": {"rank": 1, "score": 0.68},
                    "CompetitorB": {"rank": 2, "score": 0.62},
                    "CompetitorA": {"rank": 3, "score": 0.58}
                },
                "competitive_gaps": {
                    "social_presence": "TechCorp leads by 19%",
                    "innovation": "TechCorp leads by 6%",
                    "market_share": "TechCorp leads by 3%"
                },
                "threat_level": {
                    "CompetitorA": "low",
                    "CompetitorB": "medium"
                },
                "opportunities": [
                    "Expand social media presence",
                    "Leverage innovation advantage"
                ]
            }
            
            analysis = engine.analyze_competitor_trends(competitor_metrics)
            
            assert "market_position" in analysis
            assert "competitive_gaps" in analysis
            assert "threat_level" in analysis
            assert "opportunities" in analysis

    def test_market_share_analysis(self):
        """Test market share trend analysis"""
        engine = CompetitiveIntelligenceEngine()
        
        # Mock historical market share data
        market_share_history = {
            "TechCorp": [0.20, 0.22, 0.24, 0.25, 0.26, 0.25],
            "CompetitorA": [0.25, 0.24, 0.22, 0.20, 0.18, 0.18],
            "CompetitorB": [0.15, 0.16, 0.18, 0.20, 0.22, 0.22],
            "Others": [0.40, 0.38, 0.36, 0.35, 0.34, 0.35]
        }
        
        market_analysis = engine.analyze_market_share_trends(market_share_history)
        
        assert isinstance(market_analysis, dict)
        assert "market_leaders" in market_analysis
        assert "gaining_share" in market_analysis
        assert "losing_share" in market_analysis
        assert "market_concentration" in market_analysis

    def test_competitive_intelligence_alerts(self):
        """Test competitive intelligence alert system"""
        engine = CompetitiveIntelligenceEngine(enable_automated_monitoring=True)
        
        # Mock monitoring data
        monitoring_data = {
            "new_product_launch": {
                "company": "CompetitorA",
                "product": "AI Assistant Pro",
                "launch_date": "2024-12-01",
                "market_impact": "high"
            },
            "patent_filing": {
                "company": "CompetitorB",
                "technology": "Advanced ML Algorithm",
                "filing_date": "2024-11-15",
                "threat_level": "medium"
            },
            "executive_hire": {
                "company": "CompetitorC",
                "position": "Chief AI Officer",
                "previous_company": "TechGiant",
                "significance": "high"
            }
        }
        
        alerts = engine.generate_competitive_alerts(monitoring_data)
        
        assert isinstance(alerts, list)
        assert len(alerts) >= 1
        assert all("alert_type" in alert for alert in alerts)
        assert all("priority" in alert for alert in alerts)
        assert all("description" in alert for alert in alerts)


class TestTrendMetrics:
    """Tests for trend analysis metrics and evaluation"""
    
    def test_init_trend_metrics(self):
        """Test trend metrics initialization"""
        metrics = TrendMetrics()
        
        assert hasattr(metrics, 'prediction_accuracy')
        assert hasattr(metrics, 'trend_detection_precision')
        assert hasattr(metrics, 'forecast_errors')
        assert hasattr(metrics, 'timing_accuracy')

    def test_trend_detection_accuracy(self):
        """Test trend detection accuracy calculation"""
        metrics = TrendMetrics()
        
        # Mock trend predictions vs actual trends
        predicted_trends = ["upward", "downward", "stable", "upward", "downward"]
        actual_trends = ["upward", "downward", "upward", "upward", "stable"]
        
        accuracy = metrics.calculate_trend_detection_accuracy(
            predicted_trends, actual_trends
        )
        
        assert 0 <= accuracy <= 1
        assert accuracy == 3/5  # 3 out of 5 correct predictions

    def test_forecast_error_metrics(self):
        """Test forecast error metrics calculation"""
        metrics = TrendMetrics()
        
        # Mock forecast vs actual values
        forecasted = np.array([100, 105, 110, 115, 120])
        actual = np.array([102, 103, 112, 113, 118])
        
        error_metrics = metrics.calculate_forecast_errors(forecasted, actual)
        
        assert "mae" in error_metrics  # Mean Absolute Error
        assert "rmse" in error_metrics  # Root Mean Square Error
        assert "mape" in error_metrics  # Mean Absolute Percentage Error
        assert "smape" in error_metrics  # Symmetric Mean Absolute Percentage Error
        assert all(error >= 0 for error in error_metrics.values())

    def test_trend_timing_accuracy(self):
        """Test trend timing accuracy metrics"""
        metrics = TrendMetrics()
        
        # Mock trend timing predictions
        predicted_peaks = [
            {"date": "2024-06-15", "value": 150},
            {"date": "2024-09-20", "value": 180}
        ]
        actual_peaks = [
            {"date": "2024-06-18", "value": 148},
            {"date": "2024-09-15", "value": 175}
        ]
        
        timing_accuracy = metrics.calculate_timing_accuracy(
            predicted_peaks, actual_peaks, tolerance_days=5
        )
        
        assert isinstance(timing_accuracy, dict)
        assert "average_timing_error" in timing_accuracy
        assert "timing_precision" in timing_accuracy
        assert "value_accuracy" in timing_accuracy

    def test_volatility_prediction_accuracy(self):
        """Test volatility prediction accuracy"""
        metrics = TrendMetrics()
        
        # Mock volatility predictions
        predicted_volatility = [0.1, 0.15, 0.3, 0.2, 0.1]
        actual_volatility = [0.12, 0.18, 0.28, 0.22, 0.08]
        
        volatility_accuracy = metrics.evaluate_volatility_predictions(
            predicted_volatility, actual_volatility
        )
        
        assert isinstance(volatility_accuracy, dict)
        assert "correlation" in volatility_accuracy
        assert "mean_absolute_error" in volatility_accuracy
        assert "directional_accuracy" in volatility_accuracy

    def test_trend_strength_evaluation(self):
        """Test trend strength evaluation metrics"""
        metrics = TrendMetrics()
        
        # Mock trend strength assessments
        predicted_strengths = [0.8, 0.3, 0.7, 0.9, 0.2]
        actual_strengths = [0.85, 0.25, 0.75, 0.95, 0.15]
        
        strength_evaluation = metrics.evaluate_trend_strength_predictions(
            predicted_strengths, actual_strengths
        )
        
        assert isinstance(strength_evaluation, dict)
        assert "correlation_coefficient" in strength_evaluation
        assert "mean_squared_error" in strength_evaluation
        assert "classification_accuracy" in strength_evaluation


@pytest.mark.integration
class TestTrendDetectionIntegration:
    """Integration tests for trend detection systems"""
    
    @pytest.mark.slow
    def test_end_to_end_trend_analysis_pipeline(self, sample_trend_data, temp_dir):
        """Test complete trend analysis pipeline"""
        # Initialize components
        detector = TrendDetector(detection_algorithms=["momentum", "breakout"])
        predictor = ContentTrendPredictor(content_categories=["technology"])
        forecaster = TrendForecastingEngine(forecasting_models=["ARIMA"])
        
        # Run trend detection
        with patch.object(detector, 'detect_trends') as mock_detect:
            mock_detect.return_value = {
                "trend_direction": "upward",
                "trend_strength": 0.75,
                "momentum": 0.68
            }
            
            trend_results = detector.detect_trends(sample_trend_data)
            
            assert "trend_direction" in trend_results
            assert "trend_strength" in trend_results
        
        # Run content trend prediction
        with patch.object(predictor, 'predict_content_trends') as mock_predict:
            mock_predict.return_value = {
                "trending_probability": 0.82,
                "predicted_engagement": 50000
            }
            
            content_features = {"category": "technology", "quality_score": 0.8}
            prediction_results = predictor.predict_content_trends(content_features)
            
            assert "trending_probability" in prediction_results
        
        # Run forecasting
        with patch.object(forecaster, 'forecast_trends') as mock_forecast:
            mock_forecast.return_value = {
                "forecast_values": [105, 108, 112, 115],
                "confidence": 0.85
            }
            
            forecast_results = forecaster.forecast_trends(sample_trend_data, days=4)
            
            assert "forecast_values" in forecast_results
            assert len(forecast_results["forecast_values"]) == 4

    def test_real_time_trend_monitoring(self, sample_trend_data):
        """Test real-time trend monitoring integration"""
        detector = TrendDetector(enable_anomaly_detection=True)
        
        # Simulate streaming trend data
        streaming_data = []
        for i in range(10):
            data_point = {
                "timestamp": datetime.now() - timedelta(minutes=i*10),
                "value": 100 + i * 5 + np.random.normal(0, 2),
                "volume": np.random.randint(1000, 5000)
            }
            streaming_data.append(data_point)
        
        # Process streaming data
        with patch.object(detector, 'process_streaming_data') as mock_stream:
            mock_stream.return_value = {
                "current_trend": "upward",
                "anomalies_detected": [],
                "alert_level": "normal",
                "trend_confidence": 0.78
            }
            
            stream_results = detector.process_streaming_data(streaming_data)
            
            assert "current_trend" in stream_results
            assert "anomalies_detected" in stream_results
            assert "alert_level" in stream_results

    def test_multi_platform_trend_aggregation(self):
        """Test trend aggregation across multiple platforms"""
        analyzer = SocialMediaTrendAnalyzer()
        
        # Mock multi-platform trend data
        platform_data = {
            "twitter": {"mentions": 5000, "sentiment": 0.6, "growth_rate": 0.15},
            "instagram": {"mentions": 3500, "sentiment": 0.7, "growth_rate": 0.22},
            "tiktok": {"mentions": 8000, "sentiment": 0.65, "growth_rate": 0.35},
            "youtube": {"mentions": 2000, "sentiment": 0.75, "growth_rate": 0.08}
        }
        
        with patch.object(analyzer, 'aggregate_platform_trends') as mock_aggregate:
            mock_aggregate.return_value = {
                "overall_trend_strength": 0.72,
                "dominant_platform": "tiktok",
                "cross_platform_correlation": 0.68,
                "aggregated_sentiment": 0.675,
                "total_reach": 18500
            }
            
            aggregated_trends = analyzer.aggregate_platform_trends(platform_data)
            
            assert "overall_trend_strength" in aggregated_trends
            assert "dominant_platform" in aggregated_trends
            assert aggregated_trends["dominant_platform"] == "tiktok"


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
