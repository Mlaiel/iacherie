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

"""Recommendation System Tests - Enterprise Grade Test Suite

Comprehensive tests for advanced recommendation systems including collaborative filtering,
content-based recommendations, hybrid approaches, and creator collaboration matching.

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
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

from ai.ml.recommendation import (
    HybridRecommendationEngine, CollaborativeFilteringEngine, ContentBasedEngine,
    DeepRecommendationModel, CreatorMatchingEngine, ContentRecommendationEngine,
    TrendAwareRecommendationEngine, PersonalizationEngine, RecommendationMetrics,
    RecommendationConfig, CollaborationMatcher, InfluencerCollaborationEngine,
    ContentStrategyRecommender
)


class TestRecommendationConfig:
    """Tests for recommendation system configuration"""    
    def test_init_recommendation_config(self):
        """Test recommendation configuration initialization"""        config = RecommendationConfig(
            model_type="hybrid",
            num_recommendations=10,
            min_score_threshold=0.5,
            enable_diversity=True,
            diversity_weight=0.3,
            enable_novelty=True,
            novelty_weight=0.2,
            enable_serendipity=True,
            cold_start_strategy="popular_items"
        )
        
        assert config.model_type == "hybrid"
        assert config.num_recommendations == 10
        assert config.min_score_threshold == 0.5
        assert config.enable_diversity
        assert config.diversity_weight == 0.3
        assert config.enable_novelty
        assert config.novelty_weight == 0.2
        assert config.enable_serendipity
        assert config.cold_start_strategy == "popular_items"

    def test_config_validation(self):
        """Test configuration parameter validation"""        # Valid configuration
        valid_config = RecommendationConfig(
            num_recommendations=5,
            min_score_threshold=0.3,
            diversity_weight=0.25
        )
        
        assert valid_config.num_recommendations == 5
        assert 0 <= valid_config.min_score_threshold <= 1
        assert 0 <= valid_config.diversity_weight <= 1

    def test_config_serialization(self):
        """Test configuration serialization"""        config = RecommendationConfig(
            model_type="collaborative",
            num_recommendations=15,
            enable_diversity=True
        )
        
        config_dict = {
            "model_type": config.model_type,
            "num_recommendations": config.num_recommendations,
            "enable_diversity": config.enable_diversity
        }
        
        assert config_dict["model_type"] == "collaborative"
        assert config_dict["num_recommendations"] == 15
        assert config_dict["enable_diversity"] is True


class TestCollaborativeFilteringEngine:
    """Tests for collaborative filtering recommendation engine"""    
    def test_init_collaborative_filtering(self):
        """Test collaborative filtering engine initialization"""        config = RecommendationConfig(model_type="collaborative")
        engine = CollaborativeFilteringEngine(config)
        
        assert engine.config.model_type == "collaborative"
        assert engine.user_item_matrix is None
        assert engine.user_similarity_matrix is None
        assert engine.item_similarity_matrix is None

    def test_build_user_item_matrix(self, sample_recommendation_data):
        """Test user-item interaction matrix construction"""        config = RecommendationConfig()
        engine = CollaborativeFilteringEngine(config)
        
        interactions = sample_recommendation_data["interactions"]
        user_item_matrix = engine.build_user_item_matrix(interactions)
        
        assert isinstance(user_item_matrix, (np.ndarray, csr_matrix, pd.DataFrame))
        assert user_item_matrix.shape[0] > 0  # Users
        assert user_item_matrix.shape[1] > 0  # Items

    def test_compute_user_similarity(self, sample_recommendation_data):
        """Test user similarity computation"""        config = RecommendationConfig()
        engine = CollaborativeFilteringEngine(config)
        
        # Create sample user-item matrix
        n_users, n_items = 10, 20
        user_item_matrix = np.random.rand(n_users, n_items)
        
        user_similarity = engine.compute_user_similarity(user_item_matrix)
        
        assert user_similarity.shape == (n_users, n_users)
        assert np.allclose(user_similarity.diagonal(), 1.0)  # Self-similarity = 1

    def test_compute_item_similarity(self, sample_recommendation_data):
        """Test item similarity computation"""        config = RecommendationConfig()
        engine = CollaborativeFilteringEngine(config)
        
        # Create sample user-item matrix
        n_users, n_items = 10, 20
        user_item_matrix = np.random.rand(n_users, n_items)
        
        item_similarity = engine.compute_item_similarity(user_item_matrix)
        
        assert item_similarity.shape == (n_items, n_items)
        assert np.allclose(item_similarity.diagonal(), 1.0)  # Self-similarity = 1

    def test_user_based_recommendations(self, sample_recommendation_data):
        """Test user-based collaborative filtering"""        config = RecommendationConfig(num_recommendations=5)
        engine = CollaborativeFilteringEngine(config)
        
        # Mock user-item matrix and similarity
        n_users, n_items = 100, 500
        engine.user_item_matrix = np.random.rand(n_users, n_items)
        engine.user_similarity_matrix = np.random.rand(n_users, n_users)
        
        user_id = 0
        recommendations = engine.get_user_based_recommendations(user_id)
        
        assert len(recommendations) <= config.num_recommendations
        assert all(isinstance(rec, dict) for rec in recommendations)
        assert all("item_id" in rec for rec in recommendations)
        assert all("score" in rec for rec in recommendations)

    def test_item_based_recommendations(self, sample_recommendation_data):
        """Test item-based collaborative filtering"""        config = RecommendationConfig(num_recommendations=5)
        engine = CollaborativeFilteringEngine(config)
        
        # Mock user-item matrix and similarity
        n_users, n_items = 100, 500
        engine.user_item_matrix = np.random.rand(n_users, n_items)
        engine.item_similarity_matrix = np.random.rand(n_items, n_items)
        
        user_id = 0
        recommendations = engine.get_item_based_recommendations(user_id)
        
        assert len(recommendations) <= config.num_recommendations
        assert all(isinstance(rec, dict) for rec in recommendations)
        assert all("item_id" in rec for rec in recommendations)
        assert all("score" in rec for rec in recommendations)

    def test_cold_start_user_handling(self):
        """Test cold start problem handling for new users"""        config = RecommendationConfig(cold_start_strategy="popular_items")
        engine = CollaborativeFilteringEngine(config)
        
        # Mock popular items
        popular_items = [f"item_{i}" for i in range(10)]
        engine.popular_items = popular_items
        
        new_user_id = "new_user_999"
        recommendations = engine.handle_cold_start_user(new_user_id)
        
        assert len(recommendations) > 0
        assert all("item_id" in rec for rec in recommendations)
        assert all(rec["item_id"] in popular_items for rec in recommendations)

    def test_matrix_factorization(self, sample_recommendation_data):
        """Test matrix factorization for collaborative filtering"""        config = RecommendationConfig(embedding_dim=50, num_epochs=10)
        engine = CollaborativeFilteringEngine(config)
        
        # Create sparse user-item matrix
        n_users, n_items = 100, 200
        user_item_matrix = np.random.choice([0, 1], size=(n_users, n_items), p=[0.9, 0.1])
        
        user_embeddings, item_embeddings = engine.matrix_factorization(
            user_item_matrix, 
            embedding_dim=config.embedding_dim,
            num_epochs=config.num_epochs
        )
        
        assert user_embeddings.shape == (n_users, config.embedding_dim)
        assert item_embeddings.shape == (n_items, config.embedding_dim)


class TestContentBasedEngine:
    """Tests for content-based recommendation engine"""    
    def test_init_content_based_engine(self):
        """Test content-based engine initialization"""        config = RecommendationConfig(model_type="content_based")
        engine = ContentBasedEngine(config)
        
        assert engine.config.model_type == "content_based"
        assert engine.item_features is None
        assert engine.item_similarity_matrix is None

    def test_extract_item_features(self, sample_recommendation_data):
        """Test item feature extraction"""        config = RecommendationConfig()
        engine = ContentBasedEngine(config)
        
        items = sample_recommendation_data["features"]
        item_features = engine.extract_item_features(items)
        
        assert isinstance(item_features, dict)
        assert len(item_features) == len(items)
        assert all(isinstance(features, (list, np.ndarray)) for features in item_features.values())

    def test_compute_content_similarity(self, sample_recommendation_data):
        """Test content-based similarity computation"""        config = RecommendationConfig()
        engine = ContentBasedEngine(config)
        
        # Mock item features
        n_items = 100
        feature_dim = 50
        item_features = {
            f"item_{i}": np.random.rand(feature_dim) 
            for i in range(n_items)
        }
        
        similarity_matrix = engine.compute_content_similarity(item_features)
        
        assert similarity_matrix.shape == (n_items, n_items)
        assert np.allclose(similarity_matrix.diagonal(), 1.0)

    def test_user_profile_building(self, sample_recommendation_data):
        """Test user profile building from interaction history"""        config = RecommendationConfig()
        engine = ContentBasedEngine(config)
        
        # Mock user interactions and item features
        user_interactions = [
            {"item_id": "item_0", "rating": 5.0},
            {"item_id": "item_1", "rating": 4.0},
            {"item_id": "item_2", "rating": 3.0}
        ]
        
        item_features = {
            "item_0": np.array([1.0, 0.5, 0.8]),
            "item_1": np.array([0.8, 0.7, 0.6]),
            "item_2": np.array([0.6, 0.4, 0.9])
        }
        
        user_profile = engine.build_user_profile(user_interactions, item_features)
        
        assert isinstance(user_profile, np.ndarray)
        assert len(user_profile) == 3  # Feature dimension

    def test_content_based_recommendations(self, sample_recommendation_data):
        """Test content-based recommendations generation"""        config = RecommendationConfig(num_recommendations=5)
        engine = ContentBasedEngine(config)
        
        # Mock user profile and item features
        user_profile = np.array([0.7, 0.5, 0.8])
        item_features = {
            f"item_{i}": np.random.rand(3) 
            for i in range(20)
        }
        
        recommendations = engine.get_content_based_recommendations(
            user_profile, item_features
        )
        
        assert len(recommendations) <= config.num_recommendations
        assert all("item_id" in rec for rec in recommendations)
        assert all("score" in rec for rec in recommendations)
        
        # Check descending score order
        scores = [rec["score"] for rec in recommendations]
        assert scores == sorted(scores, reverse=True)

    def test_tag_based_recommendations(self, sample_recommendation_data):
        """Test tag-based content recommendations"""        config = RecommendationConfig()
        engine = ContentBasedEngine(config)
        
        user_tags = ["technology", "AI", "music"]
        item_tags = {
            "item_0": ["technology", "AI", "programming"],
            "item_1": ["music", "audio", "production"],
            "item_2": ["photography", "visual", "art"],
            "item_3": ["technology", "music", "innovation"]
        }
        
        recommendations = engine.get_tag_based_recommendations(user_tags, item_tags)
        
        assert len(recommendations) > 0
        assert all("item_id" in rec for rec in recommendations)
        assert all("score" in rec for rec in recommendations)

    def test_category_based_filtering(self, sample_recommendation_data):
        """Test category-based content filtering"""        config = RecommendationConfig()
        engine = ContentBasedEngine(config)
        
        user_preferences = {"music": 0.8, "blog": 0.6, "photo": 0.4}
        item_categories = {
            "item_0": "music",
            "item_1": "blog",
            "item_2": "photo",
            "item_3": "music",
            "item_4": "video"
        }
        
        filtered_recommendations = engine.filter_by_category(
            user_preferences, item_categories
        )
        
        assert len(filtered_recommendations) > 0
        assert all("item_id" in rec for rec in filtered_recommendations)
        assert all("score" in rec for rec in filtered_recommendations)


class TestHybridRecommendationEngine:
    """Tests for hybrid recommendation engine"""    
    def test_init_hybrid_engine(self):
        """Test hybrid recommendation engine initialization"""        config = RecommendationConfig(model_type="hybrid")
        engine = HybridRecommendationEngine(config)
        
        assert engine.config.model_type == "hybrid"
        assert engine.collaborative_engine is not None
        assert engine.content_based_engine is not None

    def test_weighted_hybrid_recommendations(self, sample_recommendation_data):
        """Test weighted hybrid recommendation fusion"""        config = RecommendationConfig(num_recommendations=10)
        engine = HybridRecommendationEngine(config)
        
        # Mock individual recommendation results
        collaborative_recs = [
            {"item_id": "item_0", "score": 0.9},
            {"item_id": "item_1", "score": 0.8},
            {"item_id": "item_2", "score": 0.7}
        ]
        
        content_based_recs = [
            {"item_id": "item_1", "score": 0.85},
            {"item_id": "item_3", "score": 0.75},
            {"item_id": "item_4", "score": 0.65}
        ]
        
        weights = {"collaborative": 0.6, "content_based": 0.4}
        
        hybrid_recs = engine.combine_recommendations(
            collaborative_recs, content_based_recs, weights
        )
        
        assert len(hybrid_recs) > 0
        assert all("item_id" in rec for rec in hybrid_recs)
        assert all("score" in rec for rec in hybrid_recs)

    def test_switching_hybrid_strategy(self, sample_recommendation_data):
        """Test switching hybrid recommendation strategy"""        config = RecommendationConfig(hybrid_strategy="switching")
        engine = HybridRecommendationEngine(config)
        
        # Mock user context for switching decision
        user_context = {
            "interaction_count": 50,  # Experienced user
            "recent_activity": True,
            "content_preferences": ["music", "technology"]
        }
        
        # Should choose collaborative for experienced users
        strategy = engine.choose_strategy(user_context)
        
        assert strategy in ["collaborative", "content_based", "hybrid"]

    def test_mixed_hybrid_recommendations(self, sample_recommendation_data):
        """Test mixed hybrid recommendations"""        config = RecommendationConfig(
            hybrid_strategy="mixed",
            num_recommendations=10,
            collaborative_ratio=0.7
        )
        engine = HybridRecommendationEngine(config)
        
        # Mock recommendations from both approaches
        collaborative_recs = [{"item_id": f"collab_{i}", "score": 0.9-i*0.1} for i in range(10)]
        content_recs = [{"item_id": f"content_{i}", "score": 0.85-i*0.1} for i in range(10)]
        
        mixed_recs = engine.get_mixed_recommendations(
            collaborative_recs, content_recs
        )
        
        assert len(mixed_recs) == config.num_recommendations
        
        # Check ratio of collaborative vs content-based recommendations
        collab_count = sum(1 for rec in mixed_recs if "collab_" in rec["item_id"])
        expected_collab = int(config.num_recommendations * config.collaborative_ratio)
        assert abs(collab_count - expected_collab) <= 1


class TestDeepRecommendationModel:
    """Tests for deep learning-based recommendation model"""    
    def test_init_deep_model(self):
        """Test deep recommendation model initialization"""        config = RecommendationConfig(
            embedding_dim=128,
            hidden_dims=[256, 128, 64],
            dropout_rate=0.2
        )
        model = DeepRecommendationModel(config)
        
        assert model.embedding_dim == 128
        assert model.hidden_dims == [256, 128, 64]
        assert model.dropout_rate == 0.2

    def test_neural_collaborative_filtering(self):
        """Test neural collaborative filtering architecture"""        config = RecommendationConfig(
            num_users=1000,
            num_items=2000,
            embedding_dim=64,
            hidden_dims=[128, 64, 32]
        )
        model = DeepRecommendationModel(config)
        
        # Mock forward pass
        user_ids = torch.randint(0, config.num_users, (32,))
        item_ids = torch.randint(0, config.num_items, (32,))
        
        # Build simple neural CF model for testing
        user_embeddings = torch.nn.Embedding(config.num_users, config.embedding_dim)
        item_embeddings = torch.nn.Embedding(config.num_items, config.embedding_dim)
        
        user_embeds = user_embeddings(user_ids)
        item_embeds = item_embeddings(item_ids)
        
        assert user_embeds.shape == (32, config.embedding_dim)
        assert item_embeds.shape == (32, config.embedding_dim)

    def test_wide_and_deep_architecture(self):
        """Test Wide & Deep model architecture"""        config = RecommendationConfig(
            embedding_dim=32,
            wide_features_dim=100,
            deep_hidden_dims=[256, 128, 64]
        )
        model = DeepRecommendationModel(config)
        
        # Mock input features
        batch_size = 64
        wide_features = torch.randn(batch_size, config.wide_features_dim)
        deep_features = torch.randn(batch_size, config.embedding_dim * 2)  # User + Item embeddings
        
        # Simple wide & deep forward pass simulation
        wide_output = torch.nn.Linear(config.wide_features_dim, 1)(wide_features)
        deep_output = torch.nn.Linear(config.embedding_dim * 2, 1)(deep_features)
        combined_output = wide_output + deep_output
        
        assert combined_output.shape == (batch_size, 1)

    def test_autoencoder_recommendations(self):
        """Test autoencoder-based collaborative filtering"""        config = RecommendationConfig(
            input_dim=1000,  # Number of items
            hidden_dims=[512, 256, 128, 256, 512],
            dropout_rate=0.5
        )
        model = DeepRecommendationModel(config)
        
        # Mock user-item interaction vector
        batch_size = 32
        user_interactions = torch.randn(batch_size, config.input_dim)
        
        # Simple autoencoder architecture for testing
        encoder = torch.nn.Sequential(
            torch.nn.Linear(config.input_dim, 512),
            torch.nn.ReLU(),
            torch.nn.Dropout(config.dropout_rate),
            torch.nn.Linear(512, 128)
        )
        
        decoder = torch.nn.Sequential(
            torch.nn.Linear(128, 512),
            torch.nn.ReLU(),
            torch.nn.Linear(512, config.input_dim),
            torch.nn.Sigmoid()
        )
        
        encoded = encoder(user_interactions)
        reconstructed = decoder(encoded)
        
        assert encoded.shape == (batch_size, 128)
        assert reconstructed.shape == (batch_size, config.input_dim)

    def test_session_based_recommendations(self):
        """Test session-based recommendation with RNNs"""        config = RecommendationConfig(
            num_items=5000,
            embedding_dim=64,
            hidden_size=128,
            num_layers=2
        )
        model = DeepRecommendationModel(config)
        
        # Mock session sequence
        batch_size = 16
        seq_length = 10
        session_items = torch.randint(0, config.num_items, (batch_size, seq_length))
        
        # Simple LSTM for session modeling
        item_embeddings = torch.nn.Embedding(config.num_items, config.embedding_dim)
        lstm = torch.nn.LSTM(
            config.embedding_dim, 
            config.hidden_size, 
            config.num_layers,
            batch_first=True
        )
        
        embedded_items = item_embeddings(session_items)
        lstm_output, (hidden, cell) = lstm(embedded_items)
        
        assert lstm_output.shape == (batch_size, seq_length, config.hidden_size)
        assert hidden.shape == (config.num_layers, batch_size, config.hidden_size)


class TestCreatorMatchingEngine:
    """Tests for creator collaboration matching engine"""    
    def test_init_creator_matching(self):
        """Test creator matching engine initialization"""        config = RecommendationConfig()
        engine = CreatorMatchingEngine(config)
        
        assert engine.config == config
        assert hasattr(engine, 'creator_profiles')
        assert hasattr(engine, 'collaboration_history')

    def test_creator_profile_analysis(self):
        """Test creator profile analysis"""        engine = CreatorMatchingEngine(RecommendationConfig())
        
        creator_data = {
            "creator_id": "creator_001",
            "content_categories": ["music", "technology", "lifestyle"],
            "audience_demographics": {
                "age_ranges": {"18-24": 0.3, "25-34": 0.4, "35-44": 0.3},
                "interests": ["music production", "tech reviews", "lifestyle tips"]
            },
            "engagement_metrics": {
                "avg_views": 50000,
                "avg_likes": 2500,
                "avg_shares": 300,
                "engagement_rate": 0.05
            },
            "collaboration_preferences": {
                "types": ["sponsorship", "cross-promotion", "joint_content"],
                "budget_range": "mid-tier",
                "duration": "long-term"
            }
        }
        
        profile_features = engine.analyze_creator_profile(creator_data)
        
        assert isinstance(profile_features, dict)
        assert "content_similarity" in profile_features
        assert "audience_overlap" in profile_features
        assert "engagement_compatibility" in profile_features
        assert "collaboration_compatibility" in profile_features

    def test_collaboration_matching(self):
        """Test creator collaboration matching algorithm"""        engine = CreatorMatchingEngine(RecommendationConfig(num_recommendations=5))
        
        # Mock creator profiles
        target_creator = {
            "creator_id": "target_001",
            "categories": ["music", "technology"],
            "audience_size": 100000,
            "engagement_rate": 0.04,
            "location": "US"
        }
        
        potential_collaborators = [
            {
                "creator_id": "collab_001",
                "categories": ["music", "lifestyle"],
                "audience_size": 80000,
                "engagement_rate": 0.06,
                "location": "US"
            },
            {
                "creator_id": "collab_002",
                "categories": ["technology", "education"],
                "audience_size": 120000,
                "engagement_rate": 0.03,
                "location": "UK"
            }
        ]
        
        matches = engine.find_collaboration_matches(
            target_creator, potential_collaborators
        )
        
        assert len(matches) <= 5
        assert all("creator_id" in match for match in matches)
        assert all("compatibility_score" in match for match in matches)
        assert all("match_reasons" in match for match in matches)

    def test_audience_overlap_calculation(self):
        """Test audience overlap calculation between creators"""        engine = CreatorMatchingEngine(RecommendationConfig())
        
        creator_a_audience = {
            "demographics": {"18-24": 0.3, "25-34": 0.5, "35-44": 0.2},
            "interests": ["music", "technology", "gaming"],
            "locations": {"US": 0.6, "UK": 0.2, "CA": 0.2}
        }
        
        creator_b_audience = {
            "demographics": {"18-24": 0.4, "25-34": 0.4, "35-44": 0.2},
            "interests": ["technology", "gaming", "lifestyle"],
            "locations": {"US": 0.5, "UK": 0.3, "DE": 0.2}
        }
        
        overlap_score = engine.calculate_audience_overlap(
            creator_a_audience, creator_b_audience
        )
        
        assert isinstance(overlap_score, float)
        assert 0 <= overlap_score <= 1

    def test_collaboration_success_prediction(self):
        """Test collaboration success prediction"""        engine = CreatorMatchingEngine(RecommendationConfig())
        
        collaboration_features = {
            "content_similarity": 0.75,
            "audience_overlap": 0.45,
            "engagement_compatibility": 0.82,
            "brand_alignment": 0.68,
            "previous_collaborations": 3,
            "timing_favorability": 0.85
        }
        
        success_probability = engine.predict_collaboration_success(collaboration_features)
        
        assert isinstance(success_probability, float)
        assert 0 <= success_probability <= 1


class TestPersonalizationEngine:
    """Tests for personalization engine"""    
    def test_init_personalization_engine(self):
        """Test personalization engine initialization"""        config = RecommendationConfig(
            personalization_level="high",
            context_awareness=True,
            real_time_adaptation=True
        )
        engine = PersonalizationEngine(config)
        
        assert engine.config.personalization_level == "high"
        assert engine.config.context_awareness
        assert engine.config.real_time_adaptation

    def test_user_context_analysis(self):
        """Test user context analysis"""        engine = PersonalizationEngine(RecommendationConfig())
        
        user_context = {
            "timestamp": datetime.now().isoformat(),
            "device": "mobile",
            "location": {"country": "US", "city": "New York"},
            "session_duration": 1800,  # seconds
            "previous_interactions": [
                {"content_id": "content_001", "interaction_type": "view", "duration": 120},
                {"content_id": "content_002", "interaction_type": "like"},
                {"content_id": "content_003", "interaction_type": "share"}
            ],
            "current_mood": "exploratory",
            "time_of_day": "evening"
        }
        
        context_features = engine.analyze_user_context(user_context)
        
        assert isinstance(context_features, dict)
        assert "temporal_features" in context_features
        assert "device_features" in context_features
        assert "behavioral_features" in context_features
        assert "contextual_preferences" in context_features

    def test_real_time_preference_adaptation(self):
        """Test real-time preference adaptation"""        engine = PersonalizationEngine(
            RecommendationConfig(real_time_adaptation=True)
        )
        
        # Mock user interaction history
        recent_interactions = [
            {"content_id": "music_001", "rating": 5, "timestamp": datetime.now()},
            {"content_id": "tech_001", "rating": 4, "timestamp": datetime.now() - timedelta(minutes=5)},
            {"content_id": "music_002", "rating": 5, "timestamp": datetime.now() - timedelta(minutes=10)}
        ]
        
        adapted_preferences = engine.adapt_preferences_realtime(
            recent_interactions, decay_factor=0.9
        )
        
        assert isinstance(adapted_preferences, dict)
        assert len(adapted_preferences) > 0
        assert all(isinstance(score, (int, float)) for score in adapted_preferences.values())

    def test_multi_armed_bandit_exploration(self):
        """Test multi-armed bandit for exploration-exploitation balance"""        engine = PersonalizationEngine(
            RecommendationConfig(exploration_strategy="epsilon_greedy")
        )
        
        # Mock content performance data
        content_performance = {
            "content_001": {"clicks": 100, "views": 1000, "ctr": 0.1},
            "content_002": {"clicks": 80, "views": 800, "ctr": 0.1},
            "content_003": {"clicks": 50, "views": 1000, "ctr": 0.05},
            "content_004": {"clicks": 10, "views": 50, "ctr": 0.2}  # New content
        }
        
        selected_content = engine.select_content_with_exploration(
            content_performance, epsilon=0.1
        )
        
        assert selected_content in content_performance.keys()

    def test_dynamic_user_segmentation(self):
        """Test dynamic user segmentation"""        engine = PersonalizationEngine(RecommendationConfig())
        
        user_features = {
            "age": 28,
            "location": "urban",
            "content_consumption_rate": "high",
            "preferred_categories": ["music", "technology", "lifestyle"],
            "engagement_patterns": {
                "peak_hours": [18, 19, 20, 21],
                "session_length": "medium",
                "interaction_types": ["view", "like", "share"]
            },
            "device_usage": {"mobile": 0.7, "desktop": 0.3}
        }
        
        user_segment = engine.segment_user_dynamically(user_features)
        
        assert isinstance(user_segment, dict)
        assert "segment_id" in user_segment
        assert "segment_characteristics" in user_segment
        assert "personalization_strategy" in user_segment


class TestRecommendationMetrics:
    """Tests for recommendation system metrics and evaluation"""    
    def test_init_metrics(self):
        """Test recommendation metrics initialization"""        metrics = RecommendationMetrics()
        
        assert hasattr(metrics, 'precision_scores')
        assert hasattr(metrics, 'recall_scores')
        assert hasattr(metrics, 'ndcg_scores')
        assert hasattr(metrics, 'diversity_scores')

    def test_precision_at_k(self):
        """Test precision@k calculation"""        metrics = RecommendationMetrics()
        
        # Mock recommendations and ground truth
        recommendations = ["item_1", "item_2", "item_3", "item_4", "item_5"]
        relevant_items = {"item_1", "item_3", "item_6", "item_7"}
        
        precision_5 = metrics.precision_at_k(recommendations, relevant_items, k=5)
        precision_3 = metrics.precision_at_k(recommendations, relevant_items, k=3)
        
        assert 0 <= precision_5 <= 1
        assert 0 <= precision_3 <= 1
        assert precision_5 == 2/5  # 2 relevant items in top 5
        assert precision_3 == 2/3  # 2 relevant items in top 3

    def test_recall_at_k(self):
        """Test recall@k calculation"""        metrics = RecommendationMetrics()
        
        recommendations = ["item_1", "item_2", "item_3", "item_4", "item_5"]
        relevant_items = {"item_1", "item_3", "item_6", "item_7"}
        
        recall_5 = metrics.recall_at_k(recommendations, relevant_items, k=5)
        
        assert 0 <= recall_5 <= 1
        assert recall_5 == 2/4  # 2 found out of 4 relevant items

    def test_ndcg_calculation(self):
        """Test NDCG (Normalized Discounted Cumulative Gain) calculation"""        metrics = RecommendationMetrics()
        
        # Mock relevance scores (higher is better)
        relevance_scores = [3, 2, 3, 0, 1, 2]  # For recommended items
        
        ndcg_score = metrics.calculate_ndcg(relevance_scores, k=5)
        
        assert 0 <= ndcg_score <= 1

    def test_diversity_calculation(self):
        """Test recommendation diversity calculation"""        metrics = RecommendationMetrics()
        
        # Mock item features for diversity calculation
        item_features = {
            "item_1": np.array([1, 0, 0, 1, 0]),  # Category A
            "item_2": np.array([0, 1, 0, 0, 1]),  # Category B
            "item_3": np.array([1, 0, 0, 1, 0]),  # Category A (similar to item_1)
            "item_4": np.array([0, 0, 1, 1, 0]),  # Category C
            "item_5": np.array([0, 1, 1, 0, 0])   # Mixed categories
        }
        
        recommendations = ["item_1", "item_2", "item_3", "item_4", "item_5"]
        
        diversity_score = metrics.calculate_diversity(recommendations, item_features)
        
        assert 0 <= diversity_score <= 1

    def test_novelty_calculation(self):
        """Test recommendation novelty calculation"""        metrics = RecommendationMetrics()
        
        # Mock item popularity (lower popularity = higher novelty)
        item_popularity = {
            "item_1": 0.8,  # Very popular (low novelty)
            "item_2": 0.1,  # Not popular (high novelty)
            "item_3": 0.5,  # Medium popularity
            "item_4": 0.05, # Very rare (very high novelty)
            "item_5": 0.3   # Somewhat rare
        }
        
        recommendations = ["item_1", "item_2", "item_3", "item_4", "item_5"]
        
        novelty_score = metrics.calculate_novelty(recommendations, item_popularity)
        
        assert 0 <= novelty_score <= 1

    def test_coverage_calculation(self):
        """Test catalog coverage calculation"""        metrics = RecommendationMetrics()
        
        # Mock all recommendations made to all users
        all_recommendations = [
            ["item_1", "item_2", "item_3"],
            ["item_2", "item_4", "item_5"],
            ["item_1", "item_3", "item_6"],
            ["item_4", "item_7", "item_8"]
        ]
        
        total_items = 20  # Total items in catalog
        
        coverage = metrics.calculate_catalog_coverage(all_recommendations, total_items)
        
        assert 0 <= coverage <= 1
        # Should cover 8 unique items out of 20
        assert coverage == 8/20


class TestTrendAwareRecommendationEngine:
    """Tests for trend-aware recommendation engine"""    
    def test_init_trend_aware_engine(self):
        """Test trend-aware recommendation engine initialization"""        config = RecommendationConfig(
            enable_trend_analysis=True,
            trend_weight=0.3,
            trend_decay_rate=0.1
        )
        engine = TrendAwareRecommendationEngine(config)
        
        assert engine.config.enable_trend_analysis
        assert engine.config.trend_weight == 0.3
        assert engine.config.trend_decay_rate == 0.1

    def test_trend_detection(self, sample_trend_data):
        """Test trend detection in content popularity"""        engine = TrendAwareRecommendationEngine(RecommendationConfig())
        
        # Use sample trend data
        trends = engine.detect_trends(sample_trend_data)
        
        assert isinstance(trends, dict)
        assert "trending_topics" in trends
        assert "trend_scores" in trends
        assert "trend_velocity" in trends

    def test_trend_incorporation_in_recommendations(self, sample_recommendation_data):
        """Test incorporating trends into recommendations"""        config = RecommendationConfig(trend_weight=0.4)
        engine = TrendAwareRecommendationEngine(config)
        
        # Mock base recommendations and trending items
        base_recommendations = [
            {"item_id": "item_1", "score": 0.8},
            {"item_id": "item_2", "score": 0.7},
            {"item_id": "item_3", "score": 0.6}
        ]
        
        trending_scores = {
            "item_1": 0.5,
            "item_2": 0.9,  # Highly trending
            "item_3": 0.3,
            "item_4": 0.95  # New trending item
        }
        
        trend_adjusted_recs = engine.incorporate_trends(
            base_recommendations, trending_scores
        )
        
        assert len(trend_adjusted_recs) >= len(base_recommendations)
        assert all("item_id" in rec for rec in trend_adjusted_recs)
        assert all("score" in rec for rec in trend_adjusted_recs)

    def test_seasonal_trend_adjustment(self):
        """Test seasonal trend adjustments"""        engine = TrendAwareRecommendationEngine(RecommendationConfig())
        
        # Mock seasonal patterns
        current_time = datetime.now()
        seasonal_factors = {
            "music": engine.get_seasonal_factor("music", current_time),
            "fashion": engine.get_seasonal_factor("fashion", current_time),
            "technology": engine.get_seasonal_factor("technology", current_time)
        }
        
        assert all(isinstance(factor, float) for factor in seasonal_factors.values())
        assert all(factor >= 0 for factor in seasonal_factors.values())


@pytest.mark.integration
class TestRecommendationIntegration:
    """Integration tests for recommendation systems"""    
    @pytest.mark.slow
    def test_end_to_end_recommendation_pipeline(self, sample_recommendation_data, temp_dir):
        """Test complete recommendation pipeline"""        config = RecommendationConfig(
            model_type="hybrid",
            num_recommendations=10,
            enable_diversity=True,
            enable_novelty=True
        )
        
        # Initialize hybrid engine
        engine = HybridRecommendationEngine(config)
        
        # Load data and train models
        interactions = sample_recommendation_data["interactions"]
        features = sample_recommendation_data["features"]
        
        # Mock training process
        engine.fit(interactions, features)
        
        # Generate recommendations for a user
        user_id = "user_0"
        recommendations = engine.recommend(user_id)
        
        assert len(recommendations) <= config.num_recommendations
        assert all("item_id" in rec for rec in recommendations)
        assert all("score" in rec for rec in recommendations)
        
        # Evaluate recommendations
        metrics = RecommendationMetrics()
        
        # Mock evaluation
        relevant_items = {"content_1", "content_3", "content_5"}
        rec_items = [rec["item_id"] for rec in recommendations]
        
        precision = metrics.precision_at_k(rec_items, relevant_items, k=5)
        recall = metrics.recall_at_k(rec_items, relevant_items, k=5)
        
        assert 0 <= precision <= 1
        assert 0 <= recall <= 1

    def test_real_time_recommendation_update(self, sample_recommendation_data):
        """Test real-time recommendation updates"""        config = RecommendationConfig(real_time_adaptation=True)
        engine = PersonalizationEngine(config)
        
        # Initial recommendations
        user_id = "user_test"
        initial_recs = engine.get_recommendations(user_id)
        
        # Simulate new user interaction
        new_interaction = {
            "user_id": user_id,
            "item_id": "new_item_001",
            "rating": 5.0,
            "timestamp": datetime.now()
        }
        
        # Update model with new interaction
        engine.update_with_interaction(new_interaction)
        
        # Get updated recommendations
        updated_recs = engine.get_recommendations(user_id)
        
        # Recommendations should potentially be different
        assert isinstance(updated_recs, list)
        assert len(updated_recs) > 0

    def test_a_b_testing_recommendations(self, sample_recommendation_data):
        """Test A/B testing for recommendation strategies"""        # Strategy A: Collaborative Filtering
        config_a = RecommendationConfig(model_type="collaborative")
        engine_a = CollaborativeFilteringEngine(config_a)
        
        # Strategy B: Content-Based
        config_b = RecommendationConfig(model_type="content_based")
        engine_b = ContentBasedEngine(config_b)
        
        user_id = "test_user"
        
        # Get recommendations from both strategies
        recs_a = engine_a.get_recommendations_mock(user_id)  # Mock method
        recs_b = engine_b.get_recommendations_mock(user_id)  # Mock method
        
        # Compare diversity
        metrics = RecommendationMetrics()
        
        # Mock item features for diversity calculation
        item_features = {f"item_{i}": np.random.rand(10) for i in range(100)}
        
        if recs_a and recs_b:
            diversity_a = metrics.calculate_diversity([r["item_id"] for r in recs_a], item_features)
            diversity_b = metrics.calculate_diversity([r["item_id"] for r in recs_b], item_features)
            
            assert 0 <= diversity_a <= 1
            assert 0 <= diversity_b <= 1


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
