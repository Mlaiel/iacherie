"""🧠 Core Intelligence Module - IA Influencer Agent
=====================================================

This module provides the central AI intelligence capabilities for content analysis,
protection, and monetization. It integrates multiple AI engines to deliver
comprehensive content understanding and processing for creators.

🎯 Business Logic Flow:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format 
→ IA protection rights → SEO pro → Matching collaboration → Multi-platform distribution

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE PROHIBITED
====================================================
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel - All rights reserved
WARNING: Any unauthorized copying, modification, distribution or use of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited
and may result in legal action under applicable copyright laws.

🛡️ Team Expertise:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices 
- Audio + DevOps + IA Prompt Engineer
"""# Core Intelligence Components
from .content_analyzer import ContentAnalyzer, MultiModalAnalyzer, ContentQualityAssessor
from .decision_engine import DecisionEngine, BusinessRuleEngine, MonetizationDecisionEngine
from .prediction_models import PredictionModels, RevenuePredictionModel, EngagementPredictionModel
from .semantic_processor import SemanticProcessor, ContentSemanticAnalyzer, ContextualProcessor
from .vector_operations import VectorOperations, SimilarityEngine, EmbeddingManager
from .neural_networks import NeuralNetworks, ContentClassificationNetwork, ProtectionNetwork
from .feature_extraction import FeatureExtraction, AudioFeatureExtractor, VisualFeatureExtractor
from .learning_engine import LearningEngine, ReinforcementLearningEngine, AdaptiveLearningSystem
from .knowledge_base import KnowledgeBase, CreatorKnowledgeGraph, PlatformKnowledgeBase
from .inference_engine import InferenceEngine, ContentInferenceEngine, BusinessInferenceEngine

# Business Intelligence Components
from .content_recommendation import ContentRecommendationEngine, PersonalizationEngine
from .monetization_intelligence import MonetizationIntelligence, RevenueOptimizer
from .collaboration_matcher import CollaborationMatcher, CreatorMatchingEngine
from .trend_analyzer import TrendAnalyzer, ViralPredictionEngine, MarketIntelligence
from .sentiment_analyzer import SentimentAnalyzer, AudienceInsightEngine
from .performance_predictor import PerformancePredictor, SuccessMetricsEngine

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"

__all__ = [
    # Core Intelligence
    "ContentAnalyzer", "MultiModalAnalyzer", "ContentQualityAssessor",
    "DecisionEngine", "BusinessRuleEngine", "MonetizationDecisionEngine",
    "PredictionModels", "RevenuePredictionModel", "EngagementPredictionModel",
    "SemanticProcessor", "ContentSemanticAnalyzer", "ContextualProcessor",
    "VectorOperations", "SimilarityEngine", "EmbeddingManager",
    "NeuralNetworks", "ContentClassificationNetwork", "ProtectionNetwork",
    "FeatureExtraction", "AudioFeatureExtractor", "VisualFeatureExtractor",
    "LearningEngine", "ReinforcementLearningEngine", "AdaptiveLearningSystem",
    "KnowledgeBase", "CreatorKnowledgeGraph", "PlatformKnowledgeBase",
    "InferenceEngine", "ContentInferenceEngine", "BusinessInferenceEngine",
    
    # Business Intelligence
    "ContentRecommendationEngine", "PersonalizationEngine",
    "MonetizationIntelligence", "RevenueOptimizer",
    "CollaborationMatcher", "CreatorMatchingEngine",
    "TrendAnalyzer", "ViralPredictionEngine", "MarketIntelligence",
    "SentimentAnalyzer", "AudienceInsightEngine",
    "PerformancePredictor", "SuccessMetricsEngine"
]
