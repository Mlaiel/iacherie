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
Mock-based Unit Tests for AI Engine Core
========================================

Mock-based tests for AI engine core that work without psutil dependencies.

Author: Fahed Mlaiel <mlaiel@live.de>
Purpose: Complete AI engine test coverage without external dependencies
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta

class MockAIModel:
    """
Mock AI model for testing"""
    
    def __init__(self, model_name: str, model_type: str = "classification"):
        self.model_name = model_name
        self.model_type = model_type
        self.is_loaded = False
        self.inference_count = 0
        self.training_history = []
    
    async def load(self):
        """Load model"""
        self.is_loaded = True
        return True
    
    async def unload(self):
        """
Unload model"""
        self.is_loaded = False
    
    async def predict(self, input_data: Any) -> Dict:
        """
Make prediction"""
        if not self.is_loaded:
            raise Exception("Model not loaded")
        
        self.inference_count += 1
        
        # Mock predictions based on model type
        if self.model_type == "classification":
            return {
                "prediction": "category_a",
                "confidence": 0.85,
                "probabilities": {
                    "category_a": 0.85,
                    "category_b": 0.10,
                    "category_c": 0.05
                }
            }
        elif self.model_type == "regression":
            return {
                "prediction": 7.5,
                "confidence": 0.92
            }
        elif self.model_type == "embedding":
            return {
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                "dimension": 5
            }
        
        return {"prediction": "unknown"}
    
    async def train(self, training_data: List, epochs: int = 1):
        """Train model"""
        training_session = {
            "started_at": datetime.now(),
            "data_size": len(training_data),
            "epochs": epochs,
            "status": "completed"
        }
        
        self.training_history.append(training_session)
        return training_session


class MockAIOrchestrator:
    """Mock AI orchestrator for managing multiple models"""
    
    def __init__(self):
        self.models = {}
        self.inference_queue = []
        self.performance_metrics = {
            "total_inferences": 0,
            "avg_response_time": 0.05,
            "success_rate": 0.99
        }
    
    async def register_model(self, model_id: str, model: MockAIModel):
        """Register AI model"""
        self.models[model_id] = model
        await model.load()
    
    async def unregister_model(self, model_id: str):
        """
Unregister AI model"""
        if model_id in self.models:
            await self.models[model_id].unload()
            del self.models[model_id]
    
    async def inference(self, model_id: str, input_data: Any) -> Dict:
        """
Perform inference using specified model"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        start_time = datetime.now()
        result = await self.models[model_id].predict(input_data)
        end_time = datetime.now()
        
        # Track inference
        inference_record = {
            "model_id": model_id,
            "timestamp": start_time,
            "response_time": (end_time - start_time).total_seconds(),
            "success": True
        }
        
        self.inference_queue.append(inference_record)
        self.performance_metrics["total_inferences"] += 1
        
        return result
    
    async def batch_inference(self, model_id: str, batch_data: List) -> List[Dict]:
        """Perform batch inference"""
        results = []
        for data in batch_data:
            result = await self.inference(model_id, data)
            results.append(result)
        return results
    
    def get_model_status(self, model_id: str) -> Dict:
        """
Get model status"""
        if model_id not in self.models:
            return {"status": "not_found"}
        
        model = self.models[model_id]
        return {
            "model_id": model_id,
            "model_name": model.model_name,
            "model_type": model.model_type,
            "is_loaded": model.is_loaded,
            "inference_count": model.inference_count,
            "training_sessions": len(model.training_history)
        }
    
    def get_performance_metrics(self) -> Dict:
        """Get orchestrator performance metrics"""
        return self.performance_metrics.copy()


class MockPersonalizationEngine:
    """
Mock personalization engine"""
    
    def __init__(self):
        self.user_profiles = {}
        self.recommendation_cache = {}
    
    async def create_user_profile(self, user_id: str, preferences: Dict) -> Dict:
        """
Create user profile"""
        profile = {
            "user_id": user_id,
            "preferences": preferences,
            "created_at": datetime.now().isoformat(),
            "interaction_count": 0,
            "recommendation_score": 0.0
        }
        
        self.user_profiles[user_id] = profile
        return profile
    
    async def update_user_preferences(self, user_id: str, new_preferences: Dict):
        """Update user preferences"""
        if user_id in self.user_profiles:
            self.user_profiles[user_id]["preferences"].update(new_preferences)
            self.user_profiles[user_id]["interaction_count"] += 1
    
    async def generate_recommendations(self, user_id: str, content_type: str = "general") -> List[Dict]:
        """Generate personalized recommendations"""
        if user_id not in self.user_profiles:
            # Default recommendations for unknown users
            return [
                {"content_id": "default_1", "score": 0.5, "type": content_type},
                {"content_id": "default_2", "score": 0.4, "type": content_type}
            ]
        
        # Mock personalized recommendations
        profile = self.user_profiles[user_id]
        recommendations = []
        
        for i in range(5):
            rec = {
                "content_id": f"rec_{user_id}_{i}",
                "score": 0.9 - (i * 0.1),
                "type": content_type,
                "reason": f"Based on your preference for {list(profile['preferences'].keys())[0] if profile['preferences'] else 'content'}"
            }
            recommendations.append(rec)
        
        # Cache recommendations
        cache_key = f"{user_id}_{content_type}"
        self.recommendation_cache[cache_key] = {
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
        return recommendations


@pytest.mark.asyncio
class TestAIModels:
    """Test AI model functionality"""
    
    @pytest.fixture
    def classification_model(self):
        return MockAIModel("content_classifier", "classification")
    
    @pytest.fixture
    def regression_model(self):
        return MockAIModel("engagement_predictor", "regression")
    
    @pytest.fixture
    def embedding_model(self):
        return MockAIModel("content_embedder", "embedding")
    
    async def test_model_loading(self, classification_model):
        """Test model loading and unloading"""
        assert not classification_model.is_loaded
        
        success = await classification_model.load()
        assert success
        assert classification_model.is_loaded
        
        await classification_model.unload()
        assert not classification_model.is_loaded
    
    async def test_classification_prediction(self, classification_model):
        """
Test classification model prediction"""
        await classification_model.load()
        
        result = await classification_model.predict("test input")
        
        assert "prediction" in result
        assert "confidence" in result
        assert "probabilities" in result
        assert isinstance(result["probabilities"], dict)
        assert result["confidence"] > 0 and result["confidence"] <= 1
    
    async def test_regression_prediction(self, regression_model):
        """Test regression model prediction"""
        await regression_model.load()
        
        result = await regression_model.predict([1, 2, 3, 4, 5])
        
        assert "prediction" in result
        assert "confidence" in result
        assert isinstance(result["prediction"], (int, float))
    
    async def test_embedding_generation(self, embedding_model):
        """Test embedding model"""
        await embedding_model.load()
        
        result = await embedding_model.predict("text to embed")
        
        assert "embedding" in result
        assert "dimension" in result
        assert isinstance(result["embedding"], list)
        assert len(result["embedding"]) == result["dimension"]
    
    async def test_model_training(self, classification_model):
        """Test model training"""
        training_data = [
            {"input": "text1", "label": "category_a"},
            {"input": "text2", "label": "category_b"},
            {"input": "text3", "label": "category_a"}
        ]
        
        training_result = await classification_model.train(training_data, epochs=2)
        
        assert "started_at" in training_result
        assert training_result["data_size"] == 3
        assert training_result["epochs"] == 2
        assert training_result["status"] == "completed"
        assert len(classification_model.training_history) == 1
    
    async def test_inference_counting(self, classification_model):
        """Test inference counting"""
        await classification_model.load()
        
        initial_count = classification_model.inference_count
        
        await classification_model.predict("test1")
        await classification_model.predict("test2")
        
        assert classification_model.inference_count == initial_count + 2


@pytest.mark.asyncio
class TestAIOrchestrator:
    """Test AI orchestrator functionality"""
    
    @pytest.fixture
    def orchestrator(self):
        return MockAIOrchestrator()
    
    @pytest.fixture
    def sample_models(self):
        return {
            "classifier": MockAIModel("content_classifier", "classification"),
            "regressor": MockAIModel("engagement_predictor", "regression"),
            "embedder": MockAIModel("content_embedder", "embedding")
        }
    
    async def test_model_registration(self, orchestrator, sample_models):
        """Test model registration and management"""
        # Register models
        for model_id, model in sample_models.items():
            await orchestrator.register_model(model_id, model)
        
        # Verify models are registered and loaded
        assert len(orchestrator.models) == 3
        for model_id in sample_models.keys():
            assert model_id in orchestrator.models
            assert orchestrator.models[model_id].is_loaded
    
    async def test_model_unregistration(self, orchestrator, sample_models):
        """
Test model unregistration"""
        # Register and then unregister
        await orchestrator.register_model("test_model", sample_models["classifier"])
        assert "test_model" in orchestrator.models
        
        await orchestrator.unregister_model("test_model")
        assert "test_model" not in orchestrator.models
    
    async def test_inference_execution(self, orchestrator, sample_models):
        """Test inference execution through orchestrator"""
        await orchestrator.register_model("classifier", sample_models["classifier"])
        
        result = await orchestrator.inference("classifier", "test input")
        
        assert "prediction" in result
        assert orchestrator.performance_metrics["total_inferences"] == 1
        assert len(orchestrator.inference_queue) == 1
    
    async def test_batch_inference(self, orchestrator, sample_models):
        """Test batch inference"""
        await orchestrator.register_model("classifier", sample_models["classifier"])
        
        batch_data = ["input1", "input2", "input3"]
        results = await orchestrator.batch_inference("classifier", batch_data)
        
        assert len(results) == 3
        assert all("prediction" in result for result in results)
        assert orchestrator.performance_metrics["total_inferences"] == 3
    
    async def test_model_status_retrieval(self, orchestrator, sample_models):
        """Test model status retrieval"""
        await orchestrator.register_model("test_model", sample_models["classifier"])
        
        status = orchestrator.get_model_status("test_model")
        
        assert status["model_id"] == "test_model"
        assert status["model_name"] == "content_classifier"
        assert status["is_loaded"] == True
        assert "inference_count" in status
    
    async def test_performance_metrics(self, orchestrator, sample_models):
        """Test performance metrics tracking"""
        await orchestrator.register_model("classifier", sample_models["classifier"])
        
        # Perform some inferences
        await orchestrator.inference("classifier", "test1")
        await orchestrator.inference("classifier", "test2")
        
        metrics = orchestrator.get_performance_metrics()
        
        assert metrics["total_inferences"] == 2
        assert "avg_response_time" in metrics
        assert "success_rate" in metrics


@pytest.mark.asyncio
class TestPersonalizationEngine:
    """Test personalization engine functionality"""
    
    @pytest.fixture
    def personalization_engine(self):
        return MockPersonalizationEngine()
    
    async def test_user_profile_creation(self, personalization_engine):
        """
Test user profile creation"""
        user_id = "user_123"
        preferences = {
            "genre": "rock",
            "language": "english",
            "content_type": "music"
        }
        
        profile = await personalization_engine.create_user_profile(user_id, preferences)
        
        assert profile["user_id"] == user_id
        assert profile["preferences"] == preferences
        assert "created_at" in profile
        assert profile["interaction_count"] == 0
        assert user_id in personalization_engine.user_profiles
    
    async def test_preference_updates(self, personalization_engine):
        """Test user preference updates"""
        user_id = "user_123"
        initial_prefs = {"genre": "rock"}
        
        await personalization_engine.create_user_profile(user_id, initial_prefs)
        
        new_prefs = {"language": "spanish", "genre": "pop"}
        await personalization_engine.update_user_preferences(user_id, new_prefs)
        
        profile = personalization_engine.user_profiles[user_id]
        assert profile["preferences"]["genre"] == "pop"  # Updated
        assert profile["preferences"]["language"] == "spanish"  # Added
        assert profile["interaction_count"] == 1
    
    async def test_personalized_recommendations(self, personalization_engine):
        """Test personalized recommendation generation"""
        user_id = "user_123"
        preferences = {"genre": "jazz", "mood": "relaxed"}
        
        await personalization_engine.create_user_profile(user_id, preferences)
        
        recommendations = await personalization_engine.generate_recommendations(user_id, "music")
        
        assert len(recommendations) == 5
        assert all("content_id" in rec for rec in recommendations)
        assert all("score" in rec for rec in recommendations)
        assert all("type" in rec for rec in recommendations)
        assert all(rec["type"] == "music" for rec in recommendations)
        
        # Scores should be in descending order
        scores = [rec["score"] for rec in recommendations]
        assert scores == sorted(scores, reverse=True)
    
    async def test_default_recommendations(self, personalization_engine):
        """Test default recommendations for unknown users"""
        recommendations = await personalization_engine.generate_recommendations("unknown_user", "video")
        
        assert len(recommendations) == 2  # Default count
        assert all(rec["type"] == "video" for rec in recommendations)
        assert all("content_id" in rec for rec in recommendations)
    
    async def test_recommendation_caching(self, personalization_engine):
        """Test recommendation caching"""
        user_id = "user_123"
        await personalization_engine.create_user_profile(user_id, {"genre": "pop"})
        
        await personalization_engine.generate_recommendations(user_id, "music")
        
        cache_key = f"{user_id}_music"
        assert cache_key in personalization_engine.recommendation_cache
        cached_data = personalization_engine.recommendation_cache[cache_key]
        assert "recommendations" in cached_data
        assert "generated_at" in cached_data


class TestAIEngineIntegration:
    """Test AI engine integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_complete_ai_workflow(self):
        """
Test complete AI workflow from orchestration to personalization"""
        # Setup components
        orchestrator = MockAIOrchestrator()
        personalization = MockPersonalizationEngine()
        
        # Register models
        classifier = MockAIModel("content_classifier", "classification")
        embedder = MockAIModel("content_embedder", "embedding")
        
        await orchestrator.register_model("classifier", classifier)
        await orchestrator.register_model("embedder", embedder)
        
        # Create user profile
        user_id = "integration_user"
        preferences = {"content_type": "music", "genre": "electronic"}
        await personalization.create_user_profile(user_id, preferences)
        
        # Perform content classification
        content_result = await orchestrator.inference("classifier", "new music content")
        assert "prediction" in content_result
        
        # Generate content embeddings
        embedding_result = await orchestrator.inference("embedder", "music content to embed")
        assert "embedding" in embedding_result
        
        # Generate personalized recommendations
        recommendations = await personalization.generate_recommendations(user_id, "music")
        assert len(recommendations) > 0
        
        # Verify system state
        assert orchestrator.performance_metrics["total_inferences"] == 2
        assert len(personalization.user_profiles) == 1


def test_ai_engine_coverage():
    """Test that all essential AI engine functionality is covered"""
    
    # Test model coverage
    model = MockAIModel("test_model", "classification")
    required_model_methods = ['load', 'unload', 'predict', 'train']
    for method in required_model_methods:
        assert hasattr(model, method)
        assert callable(getattr(model, method))
    
    # Test orchestrator coverage
    orchestrator = MockAIOrchestrator()
    required_orchestrator_methods = [
        'register_model', 'unregister_model', 'inference', 
        'batch_inference', 'get_model_status', 'get_performance_metrics'
    ]
    for method in required_orchestrator_methods:
        assert hasattr(orchestrator, method)
        assert callable(getattr(orchestrator, method))
    
    # Test personalization coverage
    personalization = MockPersonalizationEngine()
    required_personalization_methods = [
        'create_user_profile', 'update_user_preferences', 'generate_recommendations'
    ]
    for method in required_personalization_methods:
        assert hasattr(personalization, method)
        assert callable(getattr(personalization, method))