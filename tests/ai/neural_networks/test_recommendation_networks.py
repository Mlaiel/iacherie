# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
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
Comprehensive Test Suite for Recommendation Networks

Ultra-advanced industrial-grade tests for recommendation neural networks,
covering collaboration recommendations, content suggestions, audience targeting,
and trend prediction for content creators.

🎯 Expert Development Team:
✅ Lead Dev + AI Architect Developer
✅ Senior Backend Developer (Python/FastAPI/Django)  
✅ Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Backend Security Specialist
✅ Microservices Architect
✅ Audio Developer
✅ DevOps Engineer
✅ AI Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""

import pytest
import sys
import os
from pathlib import Path
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from unittest.mock import patch, MagicMock
import time

from ai.neural_networks.recommendation_networks import (
    CollaborationRecommendationNetwork,
    ContentRecommendationNetwork,
    AudienceTargetingNetwork,
    TrendPredictionNetwork
)
from ai.neural_networks.transformer_models import TransformerConfig
from ai.neural_networks.base_networks import NetworkType


@pytest.fixture
def recommendation_config():
    """
Configuration for recommendation networks"""
    return TransformerConfig(
        input_dim=512,
        hidden_dims=[512, 256, 128],
        output_dim=128,
        network_type=NetworkType.TRANSFORMER,
        num_heads=8,
        num_layers=6,
        d_model=512,
        d_ff=2048,
        max_sequence_length=1024
    )


@pytest.fixture
def creator_profiles():
    """
Sample creator profiles for testing"""
    torch.manual_seed(42)
    return {
        "creators": torch.randn(20, 512),  # 20 creators, 512-dim embeddings
        "content_history": torch.randn(20, 100, 512),  # Content history per creator
        "engagement_metrics": torch.randn(20, 10),  # Engagement features
        "audience_demographics": torch.randn(20, 15),  # Audience features
        "collaboration_history": torch.randint(0, 2, (20, 20)).float(),  # Collaboration matrix
        "creator_metadata": [
            {
                "id": f"creator_{i}",
                "followers": np.random.randint(1000, 1000000),
                "content_type": np.random.choice(["music", "video", "podcast", "art"]),
                "style": np.random.choice(["professional", "casual", "artistic", "educational"]),
                "active_platforms": np.random.choice([["youtube"], ["instagram"], ["youtube", "tiktok"], ["all"]], size=1)[0]
            } for i in range(20)
        ]
    }


@pytest.fixture
def audience_data():
    """Sample audience data for testing"""
    torch.manual_seed(42)
    return {
        "audience_segments": torch.randn(50, 256),  # 50 audience segments
        "preferences": torch.randn(50, 128),  # Preference vectors
        "engagement_patterns": torch.randn(50, 64),  # Engagement behavior
        "demographics": torch.randn(50, 32),  # Age, location, interests
        "interaction_history": torch.randn(50, 1000, 64),  # Historical interactions
        "temporal_patterns": torch.randn(50, 24, 16),  # Hourly engagement patterns
    }


@pytest.fixture
def content_data():
    """Sample content data for testing"""
    torch.manual_seed(42)
    return {
        "content_features": torch.randn(100, 512),  # 100 pieces of content
        "content_embeddings": torch.randn(100, 256),  # Semantic embeddings
        "performance_metrics": torch.randn(100, 20),  # Views, likes, shares, etc.
        "content_metadata": [
            {
                "id": f"content_{i}",
                "type": np.random.choice(["video", "audio", "image", "text"]),
                "genre": np.random.choice(["educational", "entertainment", "music", "art"]),
                "duration": np.random.uniform(30, 3600),  # Duration in seconds
                "upload_time": f"2024-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d}",
                "tags": np.random.choice(["AI", "tech", "music", "art", "tutorial"], size=3).tolist()
            } for i in range(100)
        ]
    }


@pytest.fixture
def trend_data():
    """Sample trend data for testing"""
    torch.manual_seed(42)
    return {
        "trending_topics": torch.randn(30, 128),  # 30 trending topics
        "trend_trajectories": torch.randn(30, 30, 64),  # 30-day trend evolution
        "seasonal_patterns": torch.randn(12, 128),  # Monthly seasonal trends
        "platform_trends": {
            "youtube": torch.randn(20, 128),
            "instagram": torch.randn(20, 128),
            "tiktok": torch.randn(20, 128),
            "twitter": torch.randn(20, 128)
        },
        "hashtag_trends": torch.randn(50, 64),  # Popular hashtag embeddings
        "viral_patterns": torch.randn(100, 32)  # Viral content patterns
    }


class TestCollaborationRecommendationNetwork:
    """Test CollaborationRecommendationNetwork functionality"""
    
    def test_collaboration_network_initialization(self, recommendation_config):
        """
Test CollaborationRecommendationNetwork initialization"""
        network = CollaborationRecommendationNetwork(recommendation_config)
        
        assert hasattr(network, 'creator_encoder')
        assert hasattr(network, 'compatibility_matcher')
        assert hasattr(network, 'synergy_predictor')
        assert hasattr(network, 'collaboration_scorer')
        assert hasattr(network, 'success_predictor')
    
    def test_creator_compatibility_scoring(self, recommendation_config, creator_profiles):
        """
Test creator compatibility scoring"""
        network = CollaborationRecommendationNetwork(recommendation_config)
        network.eval()
        
        creator1_features = creator_profiles["creators"][:5]  # First 5 creators
        creator2_features = creator_profiles["creators"][5:10]  # Next 5 creators
        
        with torch.no_grad():
            compatibility_scores = network.compute_compatibility(creator1_features, creator2_features)
        
        assert compatibility_scores.shape == (5, 5)  # Pairwise compatibility
        assert torch.all(compatibility_scores >= 0) and torch.all(compatibility_scores <= 1)
        assert torch.isfinite(compatibility_scores).all()
    
    def test_collaboration_recommendations(self, recommendation_config, creator_profiles):
        """Test collaboration recommendations"""
        network = CollaborationRecommendationNetwork(recommendation_config)
        network.eval()
        
        target_creator = creator_profiles["creators"][0:1]  # Single creator
        all_creators = creator_profiles["creators"]
        
        with torch.no_grad():
            recommendations = network.recommend_collaborators(
                target_creator_features=target_creator,
                candidate_creators=all_creators,
                top_k=5,
                exclude_previous=True
            )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5
        
        for rec in recommendations:
            assert "creator_id" in rec
            assert "compatibility_score" in rec
            assert "synergy_potential" in rec
            assert 0 <= rec["compatibility_score"] <= 1
            assert 0 <= rec["synergy_potential"] <= 1
    
    def test_synergy_prediction(self, recommendation_config, creator_profiles):
        """Test synergy prediction between creators"""
        network = CollaborationRecommendationNetwork(recommendation_config)
        network.eval()
        
        creator1 = creator_profiles["creators"][0:1]
        creator2 = creator_profiles["creators"][1:2]
        
        with torch.no_grad():
            synergy_metrics = network.predict_synergy(creator1, creator2)
        
        assert isinstance(synergy_metrics, dict)
        
        expected_metrics = [
            "creative_synergy", "audience_overlap", "complementary_skills",
            "brand_alignment", "collaboration_success_probability"
        ]
        
        for metric in expected_metrics:
            if metric in synergy_metrics:
                score = synergy_metrics[metric]
                assert isinstance(score, (float, torch.Tensor))
                if isinstance(score, torch.Tensor):
                    score = score.item()
                assert 0 <= score <= 1
    
    def test_collaboration_success_prediction(self, recommendation_config, creator_profiles):
        """Test collaboration success prediction"""
        network = CollaborationRecommendationNetwork(recommendation_config)
        network.eval()
        
        # Simulate collaboration data
        collaboration_pairs = torch.stack([
            creator_profiles["creators"][:5],   # Creator 1s
            creator_profiles["creators"][5:10]  # Creator 2s
        ], dim=1)  # Shape: [5, 2, 512]
        
        with torch.no_grad():
            success_predictions = network.predict_collaboration_success(collaboration_pairs)
        
        assert success_predictions.shape == (5,)  # One prediction per pair
        assert torch.all(success_predictions >= 0) and torch.all(success_predictions <= 1)
        assert torch.isfinite(success_predictions).all()
    
    def test_temporal_collaboration_patterns(self, recommendation_config, creator_profiles):
        """Test temporal collaboration pattern analysis"""
        network = CollaborationRecommendationNetwork(recommendation_config)
        network.eval()
        
        collaboration_history = creator_profiles["collaboration_history"]
        
        with torch.no_grad():
            temporal_patterns = network.analyze_collaboration_patterns(
                collaboration_history,
                time_window=30  # 30 days
            )
        
        assert isinstance(temporal_patterns, dict)
        assert "peak_collaboration_times" in temporal_patterns
        assert "collaboration_frequency" in temporal_patterns
        assert "network_density" in temporal_patterns


class TestContentRecommendationNetwork:
    """Test ContentRecommendationNetwork functionality"""
    
    def test_content_network_initialization(self, recommendation_config):
        """
Test ContentRecommendationNetwork initialization"""
        network = ContentRecommendationNetwork(recommendation_config)
        
        assert hasattr(network, 'content_encoder')
        assert hasattr(network, 'user_encoder')
        assert hasattr(network, 'interaction_predictor')
        assert hasattr(network, 'diversity_controller')
        assert hasattr(network, 'freshness_scorer')
    
    def test_personalized_content_recommendations(self, recommendation_config, creator_profiles, content_data):
        """
Test personalized content recommendations"""
        network = ContentRecommendationNetwork(recommendation_config)
        network.eval()
        
        creator_profile = creator_profiles["creators"][0:1]  # Single creator
        content_features = content_data["content_features"]
        
        with torch.no_grad():
            recommendations = network.recommend_content(
                user_profile=creator_profile,
                content_candidates=content_features,
                top_k=10,
                diversity_factor=0.3
            )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 10
        
        for rec in recommendations:
            assert "content_id" in rec
            assert "relevance_score" in rec
            assert "diversity_contribution" in rec
            assert 0 <= rec["relevance_score"] <= 1
    
    def test_content_similarity_computation(self, recommendation_config, content_data):
        """Test content similarity computation"""
        network = ContentRecommendationNetwork(recommendation_config)
        network.eval()
        
        content1 = content_data["content_features"][:5]   # First 5 contents
        content2 = content_data["content_features"][5:10]  # Next 5 contents
        
        with torch.no_grad():
            similarity_matrix = network.compute_content_similarity(content1, content2)
        
        assert similarity_matrix.shape == (5, 5)
        assert torch.all(similarity_matrix >= -1) and torch.all(similarity_matrix <= 1)
        assert torch.isfinite(similarity_matrix).all()
        
        # Diagonal should be high similarity (same content)
        if content1.shape == content2.shape and torch.allclose(content1, content2):
            diagonal = torch.diag(similarity_matrix)
            assert torch.all(diagonal > 0.8)  # High self-similarity
    
    def test_trending_content_identification(self, recommendation_config, content_data):
        """Test trending content identification"""
        network = ContentRecommendationNetwork(recommendation_config)
        network.eval()
        
        content_features = content_data["content_features"]
        performance_metrics = content_data["performance_metrics"]
        
        with torch.no_grad():
            trending_scores = network.identify_trending_content(
                content_features=content_features,
                performance_metrics=performance_metrics,
                time_decay_factor=0.1
            )
        
        assert trending_scores.shape == (content_features.shape[0],)
        assert torch.all(trending_scores >= 0)
        assert torch.isfinite(trending_scores).all()
    
    def test_diversity_optimization(self, recommendation_config, content_data):
        """Test diversity optimization in recommendations"""
        network = ContentRecommendationNetwork(recommendation_config)
        network.eval()
        
        similar_content = content_data["content_features"][:10].repeat(1, 1)  # Similar content
        
        with torch.no_grad():
            # Low diversity recommendations
            low_diversity_recs = network.optimize_diversity(
                content_list=similar_content,
                diversity_weight=0.1,
                max_recommendations=5
            )
            
            # High diversity recommendations
            high_diversity_recs = network.optimize_diversity(
                content_list=similar_content,
                diversity_weight=0.9,
                max_recommendations=5
            )
        
        assert len(low_diversity_recs) <= 5
        assert len(high_diversity_recs) <= 5
        
        # High diversity should select more varied content
        if len(high_diversity_recs) > 1:
            high_div_ids = [rec["content_id"] for rec in high_diversity_recs]
            assert len(set(high_div_ids)) == len(high_div_ids)  # All unique
    
    def test_cold_start_recommendations(self, recommendation_config, content_data):
        """Test cold start recommendations for new users"""
        network = ContentRecommendationNetwork(recommendation_config)
        network.eval()
        
        # New user with minimal profile
        new_user_profile = torch.randn(1, recommendation_config.input_dim)
        content_features = content_data["content_features"]
        
        with torch.no_grad():
            cold_start_recs = network.handle_cold_start(
                new_user_profile=new_user_profile,
                content_candidates=content_features,
                popular_content_weight=0.7,
                exploration_factor=0.3
            )
        
        assert isinstance(cold_start_recs, list)
        assert len(cold_start_recs) > 0
        
        for rec in cold_start_recs:
            assert "content_id" in rec
            assert "popularity_score" in rec
            assert "exploration_score" in rec


class TestAudienceTargetingNetwork:
    """Test AudienceTargetingNetwork functionality"""
    
    def test_audience_network_initialization(self, recommendation_config):
        """
Test AudienceTargetingNetwork initialization"""
        network = AudienceTargetingNetwork(recommendation_config)
        
        assert hasattr(network, 'audience_segmenter')
        assert hasattr(network, 'preference_predictor')
        assert hasattr(network, 'engagement_estimator')
        assert hasattr(network, 'demographic_analyzer')
        assert hasattr(network, 'personalization_engine')
    
    def test_audience_segmentation(self, recommendation_config, audience_data):
        """
Test audience segmentation"""
        network = AudienceTargetingNetwork(recommendation_config)
        network.eval()
        
        audience_features = audience_data["audience_segments"]
        demographics = audience_data["demographics"]
        
        with torch.no_grad():
            segments = network.segment_audience(
                audience_features=audience_features,
                demographic_data=demographics,
                num_segments=5,
                segmentation_method="clustering"
            )
        
        assert isinstance(segments, dict)
        assert "segment_assignments" in segments
        assert "segment_centroids" in segments
        assert "segment_characteristics" in segments
        
        segment_assignments = segments["segment_assignments"]
        assert segment_assignments.shape == (audience_features.shape[0],)
        assert torch.all(segment_assignments >= 0) and torch.all(segment_assignments < 5)
    
    def test_engagement_prediction(self, recommendation_config, audience_data, content_data):
        """Test engagement prediction for content-audience pairs"""
        network = AudienceTargetingNetwork(recommendation_config)
        network.eval()
        
        audience_features = audience_data["audience_segments"][:5]  # 5 audience segments
        content_features = content_data["content_features"][:5]    # 5 content pieces
        
        with torch.no_grad():
            engagement_predictions = network.predict_engagement(
                audience_features=audience_features,
                content_features=content_features,
                interaction_context="social_media"
            )
        
        assert engagement_predictions.shape == (5, 5)  # Audience x Content
        assert torch.all(engagement_predictions >= 0) and torch.all(engagement_predictions <= 1)
        assert torch.isfinite(engagement_predictions).all()
    
    def test_optimal_posting_time_prediction(self, recommendation_config, audience_data):
        """Test optimal posting time prediction"""
        network = AudienceTargetingNetwork(recommendation_config)
        network.eval()
        
        temporal_patterns = audience_data["temporal_patterns"]
        
        with torch.no_grad():
            optimal_times = network.predict_optimal_posting_times(
                audience_temporal_patterns=temporal_patterns,
                content_type="video",
                timezone="UTC"
            )
        
        assert isinstance(optimal_times, dict)
        assert "hourly_scores" in optimal_times
        assert "peak_hours" in optimal_times
        assert "day_of_week_preferences" in optimal_times
        
        hourly_scores = optimal_times["hourly_scores"]
        assert len(hourly_scores) == 24  # 24 hours
        
        peak_hours = optimal_times["peak_hours"]
        assert isinstance(peak_hours, list)
        assert all(0 <= hour <= 23 for hour in peak_hours)
    
    def test_demographic_analysis(self, recommendation_config, audience_data):
        """Test demographic analysis"""
        network = AudienceTargetingNetwork(recommendation_config)
        network.eval()
        
        demographic_features = audience_data["demographics"]
        engagement_patterns = audience_data["engagement_patterns"]
        
        with torch.no_grad():
            demographic_insights = network.analyze_demographics(
                demographic_data=demographic_features,
                engagement_data=engagement_patterns,
                analysis_depth="detailed"
            )
        
        assert isinstance(demographic_insights, dict)
        
        expected_insights = [
            "age_distribution", "geographic_distribution", "interest_clusters",
            "engagement_by_demo", "content_preferences"
        ]
        
        for insight in expected_insights:
            if insight in demographic_insights:
                assert demographic_insights[insight] is not None
    
    def test_personalization_recommendations(self, recommendation_config, audience_data, creator_profiles):
        """Test personalized content recommendations"""
        network = AudienceTargetingNetwork(recommendation_config)
        network.eval()
        
        audience_profile = audience_data["audience_segments"][0:1]  # Single audience member
        creator_profile = creator_profiles["creators"][0:1]        # Single creator
        
        with torch.no_grad():
            personalization_strategy = network.generate_personalization_strategy(
                creator_profile=creator_profile,
                audience_profile=audience_profile,
                campaign_objective="engagement"
            )
        
        assert isinstance(personalization_strategy, dict)
        
        expected_components = [
            "content_recommendations", "style_adjustments", "timing_suggestions",
            "platform_preferences", "messaging_tone"
        ]
        
        for component in expected_components:
            if component in personalization_strategy:
                assert personalization_strategy[component] is not None
    
    def test_audience_expansion_strategies(self, recommendation_config, audience_data):
        """Test audience expansion strategies"""
        network = AudienceTargetingNetwork(recommendation_config)
        network.eval()
        
        current_audience = audience_data["audience_segments"][:10]  # Current audience
        all_potential_audience = audience_data["audience_segments"]  # All potential
        
        with torch.no_grad():
            expansion_recommendations = network.recommend_audience_expansion(
                current_audience=current_audience,
                potential_audience=all_potential_audience,
                expansion_strategy="lookalike",
                similarity_threshold=0.7
            )
        
        assert isinstance(expansion_recommendations, list)
        
        for recommendation in expansion_recommendations:
            assert "audience_segment" in recommendation
            assert "similarity_score" in recommendation
            assert "expansion_potential" in recommendation
            assert 0 <= recommendation["similarity_score"] <= 1


class TestTrendPredictionNetwork:
    """Test TrendPredictionNetwork functionality"""
    
    def test_trend_network_initialization(self, recommendation_config):
        """
Test TrendPredictionNetwork initialization"""
        network = TrendPredictionNetwork(recommendation_config)
        
        assert hasattr(network, 'trend_analyzer')
        assert hasattr(network, 'temporal_predictor')
        assert hasattr(network, 'viral_potential_estimator')
        assert hasattr(network, 'topic_extractor')
        assert hasattr(network, 'seasonality_detector')
    
    def test_trend_detection(self, recommendation_config, trend_data):
        """
Test trend detection in content"""
        network = TrendPredictionNetwork(recommendation_config)
        network.eval()
        
        trending_topics = trend_data["trending_topics"]
        trend_trajectories = trend_data["trend_trajectories"]
        
        with torch.no_grad():
            trend_analysis = network.detect_trends(
                topic_data=trending_topics,
                temporal_data=trend_trajectories,
                detection_sensitivity=0.7
            )
        
        assert isinstance(trend_analysis, dict)
        assert "emerging_trends" in trend_analysis
        assert "declining_trends" in trend_analysis
        assert "stable_trends" in trend_analysis
        
        emerging_trends = trend_analysis["emerging_trends"]
        assert isinstance(emerging_trends, list)
        
        for trend in emerging_trends:
            assert "trend_id" in trend
            assert "growth_rate" in trend
            assert "confidence_score" in trend
            assert trend["growth_rate"] > 0  # Should be growing
    
    def test_viral_potential_prediction(self, recommendation_config, content_data, trend_data):
        """Test viral potential prediction"""
        network = TrendPredictionNetwork(recommendation_config)
        network.eval()
        
        content_features = content_data["content_features"][:10]
        viral_patterns = trend_data["viral_patterns"]
        
        with torch.no_grad():
            viral_scores = network.predict_viral_potential(
                content_features=content_features,
                viral_patterns=viral_patterns,
                time_horizon=7  # 7 days
            )
        
        assert viral_scores.shape == (10,)  # One score per content
        assert torch.all(viral_scores >= 0) and torch.all(viral_scores <= 1)
        assert torch.isfinite(viral_scores).all()
    
    def test_seasonal_trend_analysis(self, recommendation_config, trend_data):
        """Test seasonal trend analysis"""
        network = TrendPredictionNetwork(recommendation_config)
        network.eval()
        
        seasonal_patterns = trend_data["seasonal_patterns"]
        
        with torch.no_grad():
            seasonal_analysis = network.analyze_seasonality(
                trend_data=seasonal_patterns,
                time_granularity="monthly",
                years_of_data=2
            )
        
        assert isinstance(seasonal_analysis, dict)
        assert "seasonal_peaks" in seasonal_analysis
        assert "seasonal_troughs" in seasonal_analysis
        assert "recurring_patterns" in seasonal_analysis
        
        seasonal_peaks = seasonal_analysis["seasonal_peaks"]
        assert isinstance(seasonal_peaks, list)
        assert all(1 <= month <= 12 for month in seasonal_peaks if isinstance(month, int))
    
    def test_platform_specific_trends(self, recommendation_config, trend_data):
        """Test platform-specific trend analysis"""
        network = TrendPredictionNetwork(recommendation_config)
        network.eval()
        
        platform_trends = trend_data["platform_trends"]
        
        platform_analyses = {}
        
        with torch.no_grad():
            for platform, platform_data in platform_trends.items():
                analysis = network.analyze_platform_trends(
                    platform_name=platform,
                    trend_data=platform_data,
                    comparison_platforms=list(platform_trends.keys())
                )
                platform_analyses[platform] = analysis
        
        assert len(platform_analyses) == len(platform_trends)
        
        for platform, analysis in platform_analyses.items():
            assert isinstance(analysis, dict)
            assert "unique_trends" in analysis
            assert "cross_platform_trends" in analysis
            assert "platform_dominance" in analysis
    
    def test_hashtag_trend_prediction(self, recommendation_config, trend_data):
        """Test hashtag trend prediction"""
        network = TrendPredictionNetwork(recommendation_config)
        network.eval()
        
        hashtag_trends = trend_data["hashtag_trends"]
        
        with torch.no_grad():
            hashtag_predictions = network.predict_hashtag_trends(
                hashtag_embeddings=hashtag_trends,
                prediction_horizon=14,  # 14 days
                confidence_threshold=0.6
            )
        
        assert isinstance(hashtag_predictions, dict)
        assert "trending_hashtags" in hashtag_predictions
        assert "emerging_hashtags" in hashtag_predictions
        assert "declining_hashtags" in hashtag_predictions
        
        trending_hashtags = hashtag_predictions["trending_hashtags"]
        assert isinstance(trending_hashtags, list)
        
        for hashtag_info in trending_hashtags:
            assert "hashtag_id" in hashtag_info
            assert "trend_score" in hashtag_info
            assert "predicted_peak" in hashtag_info
    
    def test_trend_forecasting(self, recommendation_config, trend_data):
        """Test multi-step trend forecasting"""
        network = TrendPredictionNetwork(recommendation_config)
        network.eval()
        
        trend_trajectories = trend_data["trend_trajectories"]
        
        with torch.no_grad():
            forecasts = network.forecast_trends(
                historical_trends=trend_trajectories,
                forecast_steps=7,  # 7 future time steps
                uncertainty_estimation=True
            )
        
        assert isinstance(forecasts, dict)
        assert "trend_forecasts" in forecasts
        assert "confidence_intervals" in forecasts
        assert "forecast_uncertainty" in forecasts
        
        trend_forecasts = forecasts["trend_forecasts"]
        assert trend_forecasts.shape == (trend_trajectories.shape[0], 7, trend_trajectories.shape[2])
        assert torch.isfinite(trend_forecasts).all()
        
        confidence_intervals = forecasts["confidence_intervals"]
        assert "lower_bound" in confidence_intervals
        assert "upper_bound" in confidence_intervals


class TestRecommendationNetworksPerformance:
    """Performance tests for recommendation networks"""
    
    def test_recommendation_speed(self, recommendation_config, creator_profiles, content_data):
        """
Test recommendation generation speed"""
        network = ContentRecommendationNetwork(recommendation_config)
        network.eval()
        
        creator_profile = creator_profiles["creators"][:1]
        content_features = content_data["content_features"]
        
        # Warm up
        for _ in range(3):
            with torch.no_grad():
                _ = network.recommend_content(creator_profile, content_features, top_k=10)
        
        # Measure recommendation time
        times = []
        for _ in range(10):
            start_time = time.time()
            with torch.no_grad():
                _ = network.recommend_content(creator_profile, content_features, top_k=10)
            end_time = time.time()
            times.append((end_time - start_time) * 1000)
        
        avg_time = np.mean(times)
        print(f"Content recommendation: {avg_time:.2f}ms")
        
        # Recommendations should be fast
        assert avg_time < 500  # Less than 500ms
    
    def test_batch_recommendation_efficiency(self, recommendation_config, creator_profiles, content_data):
        """Test batch recommendation efficiency"""
        network = ContentRecommendationNetwork(recommendation_config)
        network.eval()
        
        # Single recommendations
        single_times = []
        for i in range(5):
            creator = creator_profiles["creators"][i:i+1]
            start_time = time.time()
            with torch.no_grad():
                _ = network.recommend_content(creator, content_data["content_features"], top_k=5)
            single_times.append((time.time() - start_time) * 1000)
        
        total_single_time = sum(single_times)
        
        # Batch recommendation
        batch_creators = creator_profiles["creators"][:5]
        start_time = time.time()
        with torch.no_grad():
            for i in range(5):
                _ = network.recommend_content(
                    batch_creators[i:i+1], 
                    content_data["content_features"], 
                    top_k=5
                )
        batch_time = (time.time() - start_time) * 1000
        
        print(f"Single recommendations total: {total_single_time:.2f}ms")
        print(f"Batch recommendations: {batch_time:.2f}ms")
        
        # Should be reasonably efficient
        assert batch_time < total_single_time * 1.5  # Not more than 50% slower
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
    def test_gpu_acceleration(self, recommendation_config, creator_profiles, content_data):
        """Test GPU acceleration for recommendations"""
        network = ContentRecommendationNetwork(recommendation_config)
        
        creator_profile = creator_profiles["creators"][:1]
        content_features = content_data["content_features"]
        
        # CPU timing
        network_cpu = network.cpu()
        creator_cpu = creator_profile.cpu()
        content_cpu = content_features.cpu()
        
        start_time = time.time()
        with torch.no_grad():
            _ = network_cpu.recommend_content(creator_cpu, content_cpu, top_k=10)
        cpu_time = (time.time() - start_time) * 1000
        
        # GPU timing
        network_gpu = network.cuda()
        creator_gpu = creator_profile.cuda()
        content_gpu = content_features.cuda()
        
        torch.cuda.synchronize()
        start_time = time.time()
        with torch.no_grad():
            _ = network_gpu.recommend_content(creator_gpu, content_gpu, top_k=10)
        torch.cuda.synchronize()
        gpu_time = (time.time() - start_time) * 1000
        
        speedup = cpu_time / gpu_time
        print(f"GPU speedup: {speedup:.2f}x")
        
        assert speedup >= 1.0  # Should not be slower


class TestRecommendationNetworksRobustness:
    """Robustness tests for recommendation networks"""
    
    def test_missing_data_handling(self, recommendation_config, creator_profiles):
        """
Test handling of missing data"""
        network = CollaborationRecommendationNetwork(recommendation_config)
        network.eval()
        
        # Test with incomplete creator profiles
        incomplete_profile = creator_profiles["creators"][:1]
        incomplete_profile[0, :100] = 0  # Zero out some features
        
        all_creators = creator_profiles["creators"]
        
        with torch.no_grad():
            recommendations = network.recommend_collaborators(
                target_creator_features=incomplete_profile,
                candidate_creators=all_creators,
                top_k=5
            )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0  # Should still provide recommendations
    
    def test_cold_start_scenarios(self, recommendation_config, content_data):
        """Test cold start scenarios"""
        network = ContentRecommendationNetwork(recommendation_config)
        network.eval()
        
        # Brand new user with no history
        new_user_profile = torch.zeros(1, recommendation_config.input_dim)
        content_features = content_data["content_features"]
        
        with torch.no_grad():
            cold_start_recs = network.handle_cold_start(
                new_user_profile=new_user_profile,
                content_candidates=content_features,
                popular_content_weight=0.8
            )
        
        assert isinstance(cold_start_recs, list)
        assert len(cold_start_recs) > 0
        
        # Should recommend popular content for cold start
        for rec in cold_start_recs:
            assert "popularity_score" in rec
            assert rec["popularity_score"] > 0
    
    def test_extreme_user_preferences(self, recommendation_config, creator_profiles, content_data):
        """Test with extreme user preferences"""
        network = ContentRecommendationNetwork(recommendation_config)
        network.eval()
        
        # Create user with extreme preferences (all maximum values)
        extreme_user = torch.ones(1, recommendation_config.input_dim)
        content_features = content_data["content_features"]
        
        with torch.no_grad():
            recommendations = network.recommend_content(
                user_profile=extreme_user,
                content_candidates=content_features,
                top_k=5
            )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should handle gracefully
        for rec in recommendations:
            assert "relevance_score" in rec
            assert torch.isfinite(torch.tensor(rec["relevance_score"]))
    
    def test_adversarial_inputs(self, recommendation_config, creator_profiles):
        """Test with adversarial inputs"""
        network = CollaborationRecommendationNetwork(recommendation_config)
        network.eval()
        
        # Add noise to creator profiles
        noisy_creator = creator_profiles["creators"][:1].clone()
        noise = torch.randn_like(noisy_creator) * 0.1
        noisy_creator += noise
        
        all_creators = creator_profiles["creators"]
        
        with torch.no_grad():
            noisy_recommendations = network.recommend_collaborators(
                target_creator_features=noisy_creator,
                candidate_creators=all_creators,
                top_k=5
            )
        
        assert isinstance(noisy_recommendations, list)
        # Should be robust to small perturbations
        assert len(noisy_recommendations) > 0


class TestRecommendationNetworksIntegration:
    """Integration tests for recommendation networks"""
    
    def test_complete_recommendation_pipeline(self, recommendation_config, creator_profiles, content_data, audience_data, trend_data):
        """
Test complete recommendation pipeline"""
        # Initialize all networks
        collaboration_net = CollaborationRecommendationNetwork(recommendation_config)
        content_net = ContentRecommendationNetwork(recommendation_config)
        audience_net = AudienceTargetingNetwork(recommendation_config)
        trend_net = TrendPredictionNetwork(recommendation_config)
        
        # Set to eval mode
        collaboration_net.eval()
        content_net.eval()
        audience_net.eval()
        trend_net.eval()
        
        target_creator = creator_profiles["creators"][:1]
        
        with torch.no_grad():
            # Step 1: Get collaboration recommendations
            collaborator_recs = collaboration_net.recommend_collaborators(
                target_creator_features=target_creator,
                candidate_creators=creator_profiles["creators"],
                top_k=3
            )
            
            # Step 2: Get content recommendations  
            content_recs = content_net.recommend_content(
                user_profile=target_creator,
                content_candidates=content_data["content_features"],
                top_k=5
            )
            
            # Step 3: Analyze audience
            audience_segments = audience_net.segment_audience(
                audience_features=audience_data["audience_segments"],
                demographic_data=audience_data["demographics"],
                num_segments=3
            )
            
            # Step 4: Get trend insights
            trend_analysis = trend_net.detect_trends(
                topic_data=trend_data["trending_topics"],
                temporal_data=trend_data["trend_trajectories"]
            )
        
        # Verify pipeline results
        assert len(collaborator_recs) <= 3
        assert len(content_recs) <= 5
        assert isinstance(audience_segments, dict)
        assert isinstance(trend_analysis, dict)
        
        # All components should provide valid outputs
        for collab in collaborator_recs:
            assert 0 <= collab["compatibility_score"] <= 1
        
        for content in content_recs:
            assert 0 <= content["relevance_score"] <= 1
        
        assert "segment_assignments" in audience_segments
        assert "emerging_trends" in trend_analysis
    
    def test_creator_growth_strategy_generation(self, recommendation_config, creator_profiles, content_data, audience_data):
        """Test complete creator growth strategy generation"""
        # Initialize networks
        content_net = ContentRecommendationNetwork(recommendation_config)
        audience_net = AudienceTargetingNetwork(recommendation_config)
        collaboration_net = CollaborationRecommendationNetwork(recommendation_config)
        
        content_net.eval()
        audience_net.eval()
        collaboration_net.eval()
        
        creator_profile = creator_profiles["creators"][:1]
        
        with torch.no_grad():
            # Generate comprehensive growth strategy
            growth_strategy = {}
            
            # Content strategy
            growth_strategy["content_recommendations"] = content_net.recommend_content(
                user_profile=creator_profile,
                content_candidates=content_data["content_features"],
                top_k=10,
                diversity_factor=0.4
            )
            
            # Audience strategy
            growth_strategy["audience_expansion"] = audience_net.recommend_audience_expansion(
                current_audience=audience_data["audience_segments"][:5],  # Current audience
                potential_audience=audience_data["audience_segments"],
                expansion_strategy="lookalike"
            )
            
            # Collaboration strategy
            growth_strategy["collaboration_opportunities"] = collaboration_net.recommend_collaborators(
                target_creator_features=creator_profile,
                candidate_creators=creator_profiles["creators"],
                top_k=5
            )
            
            # Optimal timing
            growth_strategy["posting_schedule"] = audience_net.predict_optimal_posting_times(
                audience_temporal_patterns=audience_data["temporal_patterns"][:10],
                content_type="video"
            )
        
        # Verify growth strategy completeness
        assert "content_recommendations" in growth_strategy
        assert "audience_expansion" in growth_strategy
        assert "collaboration_opportunities" in growth_strategy
        assert "posting_schedule" in growth_strategy
        
        # All recommendations should be actionable
        assert len(growth_strategy["content_recommendations"]) > 0
        assert len(growth_strategy["audience_expansion"]) > 0
        assert len(growth_strategy["collaboration_opportunities"]) > 0
        assert "peak_hours" in growth_strategy["posting_schedule"]


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
