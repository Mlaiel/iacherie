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
Comprehensive Tests for NLP Classification Module

Industrial-grade tests for AdvancedClassificationEngine covering content classification,
topic modeling, and categorization with real implementations.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from typing import Dict, List, Any, Optional
import logging

from ai.nlp.classification import (
    AdvancedContentClassifier, TopicClassification, ContentCategory,
    ContentIntent, ClassificationResult, ContentStyle, AudienceTarget, PlatformOptimization
)
try:
    from ai.nlp.utils import Platform, Language, ContentType
except ImportError:
    # Fallback definitions if utils doesn't exist
    Platform = type('Platform', (), {'INSTAGRAM': 'instagram', 'TIKTOK': 'tiktok', 'TWITTER': 'twitter'})
    Language = type('Language', (), {'EN': 'en', 'DE': 'de', 'FR': 'fr'})
    ContentType = type('ContentType', (), {'POST': 'post', 'STORY': 'story'})

logger = logging.getLogger(__name__)

class TestAdvancedContentClassifier:
    """Comprehensive tests for AdvancedContentClassifier"""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, classification_engine):
        """Test classification engine initialization"""
        assert classification_engine is not None
        assert hasattr(classification_engine, 'config')
        assert hasattr(classification_engine, 'topic_modeler')
        assert hasattr(classification_engine, 'content_categorizer')
        assert hasattr(classification_engine, 'intent_classifier')
        
        # Test configuration
        config = classification_engine.config
        assert 'classification_models' in config
        assert 'topic_categories' in config
        assert 'confidence_threshold' in config

    @pytest.mark.asyncio
    async def test_content_classification(self, classification_engine):
        """Test basic content classification"""
        test_cases = [
            {
                'content': "Check out our new AI-powered content creation tool! It's perfect for social media marketing and brand engagement. #AI #Marketing #SocialMedia",
                'expected_categories': ['Technology', 'Marketing', 'Business'],
                'expected_primary': 'Technology'
            },
            {
                'content': "Just finished an amazing workout at the gym! Feeling strong and healthy. Remember to stay hydrated and eat well. #Fitness #Health #Lifestyle",
                'expected_categories': ['Health', 'Fitness', 'Lifestyle'],
                'expected_primary': 'Health'
            },
            {
                'content': "Exploring the beautiful landscapes of Switzerland. The mountains and lakes are breathtaking! #Travel #Nature #Photography",
                'expected_categories': ['Travel', 'Nature', 'Photography'],
                'expected_primary': 'Travel'
            },
            {
                'content': "Cooking is my passion! Today I made a delicious pasta dish with fresh herbs from my garden. #Cooking #Food #Recipe",
                'expected_categories': ['Food', 'Cooking', 'Lifestyle'],
                'expected_primary': 'Food'
            },
            {
                'content': "Excited to announce our company's Q4 financial results. Revenue increased by 25% this quarter. #Business #Finance #Growth",
                'expected_categories': ['Business', 'Finance', 'Corporate'],
                'expected_primary': 'Business'
            }
        ]
        
        for case in test_cases:
            classification_result = await classification_engine.classify_content(
                content=case['content'],
                options={
                    'multi_label': True,
                    'hierarchical_classification': True,
                    'confidence_scoring': True,
                    'detailed_analysis': True
                }
            )
            
            assert classification_result is not None
            assert isinstance(classification_result, dict)
            assert 'primary_category' in classification_result
            assert 'categories' in classification_result
            assert 'confidence_scores' in classification_result
            assert 'classification_details' in classification_result
            
            primary_category = classification_result['primary_category']
            categories = classification_result['categories']
            confidence_scores = classification_result['confidence_scores']
            
            # Verify primary category
            assert primary_category == case['expected_primary']
            
            # Verify categories
            assert isinstance(categories, list)
            assert len(categories) > 0
            
            # Check if expected categories are found
            for expected_cat in case['expected_categories']:
                category_found = any(
                    expected_cat.lower() in cat.lower() 
                    for cat in categories
                )
                assert category_found, f"Expected category '{expected_cat}' not found in {categories}"
            
            # Verify confidence scores
            assert isinstance(confidence_scores, dict)
            for category in categories:
                assert category in confidence_scores
                assert 0.0 <= confidence_scores[category] <= 1.0

    @pytest.mark.asyncio
    async def test_topic_modeling(self, classification_engine):
        """Test topic modeling and extraction"""
        documents = [
            "Artificial intelligence is revolutionizing the way we create content for social media platforms.",
            "Machine learning algorithms can analyze user behavior and optimize engagement strategies.",
            "Natural language processing helps in understanding customer sentiment and feedback.",
            "Social media marketing requires understanding of different platform algorithms and user preferences.",
            "Content creators need tools that can automate repetitive tasks while maintaining authenticity.",
            "Brand engagement metrics show the importance of personalized content for target audiences.",
            "Digital marketing trends indicate a shift towards AI-assisted content creation and optimization.",
            "Influencer marketing platforms are integrating advanced analytics for better campaign performance."
        ]
        
        topic_analysis = await classification_engine.extract_topics(
            documents=documents,
            num_topics=3,
            options={
                'topic_coherence': True,
                'keyword_extraction': True,
                'topic_evolution': True,
                'semantic_similarity': True
            }
        )
        
        assert topic_analysis is not None
        assert 'topics' in topic_analysis
        assert 'topic_coherence_score' in topic_analysis
        assert 'topic_keywords' in topic_analysis
        assert 'document_topic_distribution' in topic_analysis
        
        topics = topic_analysis['topics']
        assert len(topics) == 3  # Requested number of topics
        
        for topic in topics:
            assert 'topic_id' in topic
            assert 'keywords' in topic
            assert 'weight' in topic
            assert 'description' in topic
            
            # Topic should have meaningful keywords
            keywords = topic['keywords']
            assert len(keywords) > 0
            assert all(isinstance(kw, str) and len(kw) > 0 for kw in keywords)

    @pytest.mark.asyncio
    async def test_intent_classification(self, classification_engine):
        """Test intent classification for user content"""
        intent_test_cases = [
            {
                'content': "I want to buy this product. Where can I purchase it?",
                'expected_intent': 'purchase',
                'expected_confidence': 0.8
            },
            {
                'content': "Can you help me understand how this feature works?",
                'expected_intent': 'information_seeking',
                'expected_confidence': 0.7
            },
            {
                'content': "This product is amazing! I love it so much!",
                'expected_intent': 'positive_feedback',
                'expected_confidence': 0.8
            },
            {
                'content': "I'm having trouble with the installation process.",
                'expected_intent': 'support_request',
                'expected_confidence': 0.7
            },
            {
                'content': "Just sharing my experience with this new tool.",
                'expected_intent': 'content_sharing',
                'expected_confidence': 0.6
            },
            {
                'content': "Looking for recommendations for similar products.",
                'expected_intent': 'recommendation_request',
                'expected_confidence': 0.7
            }
        ]
        
        for case in intent_test_cases:
            intent_result = await classification_engine.classify_intent(
                content=case['content'],
                options={
                    'context_awareness': True,
                    'multi_intent_detection': True,
                    'confidence_calibration': True
                }
            )
            
            assert intent_result is not None
            assert 'primary_intent' in intent_result
            assert 'confidence' in intent_result
            assert 'intent_distribution' in intent_result
            assert 'context_factors' in intent_result
            
            primary_intent = intent_result['primary_intent']
            confidence = intent_result['confidence']
            
            # Check intent classification
            assert primary_intent == case['expected_intent']
            assert confidence >= case['expected_confidence'] - 0.2  # Allow some tolerance

    @pytest.mark.asyncio
    async def test_hierarchical_classification(self, classification_engine):
        """Test hierarchical content classification"""
        content = "Our new smartphone features advanced AI camera technology with machine learning image enhancement and real-time photo optimization."
        
        hierarchical_result = await classification_engine.classify_hierarchical(
            content=content,
            options={
                'max_depth': 3,
                'include_subcategories': True,
                'confidence_propagation': True
            }
        )
        
        assert hierarchical_result is not None
        assert 'hierarchy' in hierarchical_result
        assert 'classification_path' in hierarchical_result
        assert 'confidence_at_levels' in hierarchical_result
        
        hierarchy = hierarchical_result['hierarchy']
        classification_path = hierarchical_result['classification_path']
        
        # Should have hierarchical structure
        assert isinstance(hierarchy, dict)
        assert 'level_0' in hierarchy  # Top level
        
        # Should have classification path
        assert isinstance(classification_path, list)
        assert len(classification_path) > 0
        
        # Expected path might be: Technology -> Electronics -> Smartphones
        # or Technology -> AI/ML -> Computer Vision
        top_level = classification_path[0]
        assert 'Technology' in top_level or 'Electronics' in top_level

    @pytest.mark.asyncio
    async def test_platform_specific_classification(self, classification_engine, sample_social_content):
        """Test platform-specific content classification"""
        platforms = [Platform.INSTAGRAM, Platform.TWITTER, Platform.LINKEDIN, Platform.TIKTOK]
        
        for platform in platforms:
            content = sample_social_content[platform.value.lower()]['post']
            
            platform_classification = await classification_engine.classify_platform_content(
                content=content,
                platform=platform,
                options={
                    'platform_context': True,
                    'audience_analysis': True,
                    'engagement_prediction': True,
                    'content_optimization': True
                }
            )
            
            assert platform_classification is not None
            assert 'content_type' in platform_classification
            assert 'platform_category' in platform_classification
            assert 'audience_match' in platform_classification
            assert 'optimization_suggestions' in platform_classification
            
            content_type = platform_classification['content_type']
            platform_category = platform_classification['platform_category']
            
            # Should classify content type appropriately
            assert content_type in ['promotional', 'educational', 'entertainment', 'personal', 'news', 'lifestyle']
            
            # Should have platform-specific insights
            assert isinstance(platform_category, str)
            assert len(platform_category) > 0

    @pytest.mark.asyncio
    async def test_multilingual_classification(self, classification_engine):
        """Test multilingual content classification"""
        multilingual_content = [
            {
                'text': "Artificial intelligence is transforming digital marketing strategies.",
                'language': 'english',
                'expected_category': 'Technology'
            },
            {
                'text': "Künstliche Intelligenz verändert digitale Marketingstrategien.",
                'language': 'german',
                'expected_category': 'Technology'
            },
            {
                'text': "L'intelligence artificielle transforme les stratégies de marketing numérique.",
                'language': 'french',
                'expected_category': 'Technology'
            },
            {
                'text': "La inteligencia artificial está transformando las estrategias de marketing digital.",
                'language': 'spanish',
                'expected_category': 'Technology'
            }
        ]
        
        for content in multilingual_content:
            classification = await classification_engine.classify_multilingual_content(
                content=content['text'],
                language=content['language'],
                options={
                    'cross_language_consistency': True,
                    'cultural_context': True,
                    'language_specific_categories': True
                }
            )
            
            assert classification is not None
            assert 'primary_category' in classification
            assert 'language_confidence' in classification
            assert 'cross_language_consistency' in classification
            
            primary_category = classification['primary_category']
            
            # Should classify consistently across languages
            assert content['expected_category'] in primary_category or primary_category in content['expected_category']

    @pytest.mark.asyncio
    async def test_dynamic_category_learning(self, classification_engine):
        """Test dynamic category learning and adaptation"""
        # Simulate new content that might represent emerging categories
        emerging_content = [
            "NFT marketplace for digital art collectors and crypto enthusiasts.",
            "Metaverse virtual reality experiences for remote collaboration.",
            "Blockchain-based social media platform with decentralized governance.",
            "AI-generated music for meditation and mindfulness applications.",
            "Sustainable fashion made from recycled ocean plastic materials."
        ]
        
        learning_result = await classification_engine.learn_new_categories(
            content_samples=emerging_content,
            options={
                'category_discovery': True,
                'semantic_clustering': True,
                'novelty_detection': True,
                'category_validation': True
            }
        )
        
        assert learning_result is not None
        assert 'discovered_categories' in learning_result
        assert 'category_confidence' in learning_result
        assert 'semantic_clusters' in learning_result
        
        discovered = learning_result['discovered_categories']
        assert isinstance(discovered, list)
        
        # Should discover some emerging categories
        if len(discovered) > 0:
            for category in discovered:
                assert 'category_name' in category
                assert 'representative_content' in category
                assert 'confidence_score' in category

    @pytest.mark.asyncio
    async def test_content_similarity_classification(self, classification_engine):
        """Test content similarity-based classification"""
        reference_content = {
            'technology': "Latest advances in artificial intelligence and machine learning applications.",
            'health': "Nutrition tips for maintaining a healthy lifestyle and balanced diet.",
            'travel': "Exploring beautiful destinations around the world and travel photography.",
            'business': "Effective strategies for growing your startup and managing business operations."
        }
        
        test_content = [
            "New breakthrough in neural network architectures for computer vision.",  # Should match technology
            "Best foods for boosting immune system and preventing diseases.",        # Should match health
            "Hidden gems in European cities perfect for weekend getaways.",         # Should match travel
            "Tips for successful entrepreneur mindset and leadership skills."        # Should match business
        ]
        
        for i, content in enumerate(test_content):
            similarity_classification = await classification_engine.classify_by_similarity(
                content=content,
                reference_categories=reference_content,
                options={
                    'semantic_similarity': True,
                    'contextual_matching': True,
                    'threshold_adjustment': True
                }
            )
            
            assert similarity_classification is not None
            assert 'best_match' in similarity_classification
            assert 'similarity_scores' in similarity_classification
            assert 'confidence' in similarity_classification
            
            best_match = similarity_classification['best_match']
            similarity_scores = similarity_classification['similarity_scores']
            
            # Should match expected categories
            expected_matches = ['technology', 'health', 'travel', 'business']
            assert best_match == expected_matches[i]
            
            # Should have reasonable similarity scores
            assert isinstance(similarity_scores, dict)
            for category, score in similarity_scores.items():
                assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_batch_classification(self, classification_engine, performance_test_data):
        """Test batch content classification"""
        texts = performance_test_data['small_batch']
        
        start_time = time.time()
        batch_classification = await classification_engine.classify_batch(
            contents=texts,
            options={
                'parallel_processing': True,
                'consistent_classification': True,
                'confidence_thresholding': True
            }
        )
        processing_time = time.time() - start_time
        
        assert batch_classification is not None
        assert 'classifications' in batch_classification
        assert 'batch_statistics' in batch_classification
        assert 'processing_metrics' in batch_classification
        
        classifications = batch_classification['classifications']
        assert len(classifications) == len(texts)
        
        # All classifications should have required fields
        for classification in classifications:
            assert 'primary_category' in classification
            assert 'confidence' in classification
            assert 'categories' in classification
        
        # Should process efficiently
        throughput = len(texts) / processing_time
        assert throughput > 10.0  # Should classify at least 10 items per second

    @pytest.mark.asyncio
    async def test_classification_explanation(self, classification_engine):
        """Test classification explanation and interpretability"""
        content = "Innovative startup using AI to revolutionize healthcare diagnostics and patient care."
        
        explanation_result = await classification_engine.explain_classification(
            content=content,
            options={
                'feature_importance': True,
                'decision_path': True,
                'counterfactual_examples': True,
                'confidence_factors': True
            }
        )
        
        assert explanation_result is not None
        assert 'classification' in explanation_result
        assert 'explanation' in explanation_result
        assert 'feature_importance' in explanation_result
        assert 'decision_factors' in explanation_result
        
        explanation = explanation_result['explanation']
        feature_importance = explanation_result['feature_importance']
        
        # Should provide meaningful explanations
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        
        # Should identify important features
        assert isinstance(feature_importance, dict)
        assert len(feature_importance) > 0

    @pytest.mark.asyncio
    async def test_custom_classification_models(self, classification_engine):
        """Test custom classification model integration"""
        # Define custom categories for a specific domain
        custom_categories = {
            'ai_content_tools': [
                "AI writing assistants and content generation tools",
                "Automated social media scheduling and optimization",
                "Machine learning for content personalization"
            ],
            'influencer_marketing': [
                "Influencer collaboration and partnership strategies",
                "Creator economy platforms and monetization",
                "Social media influence measurement and analytics"
            ],
            'content_strategy': [
                "Content planning and editorial calendar management",
                "Brand storytelling and narrative development",
                "Cross-platform content distribution strategies"
            ]
        }
        
        custom_model = await classification_engine.create_custom_model(
            categories=custom_categories,
            training_options={
                'model_type': 'fine_tuned',
                'validation_split': 0.2,
                'optimization_metric': 'f1_score'
            }
        )
        
        assert custom_model is not None
        assert 'model_id' in custom_model
        assert 'performance_metrics' in custom_model
        
        # Test classification with custom model
        test_content = "New AI tool for automated content creation and social media optimization."
        
        custom_classification = await classification_engine.classify_with_custom_model(
            content=test_content,
            model_id=custom_model['model_id'],
            options={'detailed_analysis': True}
        )
        
        assert custom_classification is not None
        assert 'primary_category' in custom_classification
        
        # Should classify into one of the custom categories
        primary = custom_classification['primary_category']
        assert primary in ['ai_content_tools', 'influencer_marketing', 'content_strategy']

    @pytest.mark.asyncio
    async def test_real_time_classification(self, classification_engine):
        """Test real-time content classification"""
        # Simulate real-time content stream
        content_stream = [
            "Breaking: New AI breakthrough in natural language processing!",
            "Quick workout tips for busy professionals - stay fit on the go!",
            "Market update: Tech stocks surge on AI adoption news.",
            "Recipe of the day: Healthy quinoa salad with fresh vegetables.",
            "Travel alert: Beautiful autumn colors in European countryside."
        ]
        
        classification_times = []
        
        for content in content_stream:
            start_time = time.time()
            
            real_time_result = await classification_engine.classify_realtime(
                content=content,
                options={
                    'low_latency': True,
                    'quick_classification': True,
                    'confidence_threshold': 0.6
                }
            )
            
            classification_time = time.time() - start_time
            classification_times.append(classification_time)
            
            assert real_time_result is not None
            assert 'primary_category' in real_time_result
            assert 'confidence' in real_time_result
            
            # Should be fast for real-time use
            assert classification_time < 1.0  # Should classify quickly
        
        # Average should be suitable for real-time
        avg_time = sum(classification_times) / len(classification_times)
        assert avg_time < 0.5

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, classification_engine, benchmark_config):
        """Test classification performance benchmarks"""
        test_content = "This is a performance test for content classification benchmarking."
        
        # Single classification performance
        start_time = time.time()
        result = await classification_engine.classify_content(
            content=test_content,
            options={'quick_classification': True}
        )
        single_time = time.time() - start_time
        
        max_time = benchmark_config.get('max_classification_time', 2.0)
        assert single_time < max_time, f"Classification took {single_time:.3f}s, max: {max_time}s"
        
        # Batch classification performance
        batch_contents = [f"Batch content {i} for classification testing." for i in range(25)]
        
        start_time = time.time()
        batch_result = await classification_engine.classify_batch(
            contents=batch_contents,
            options={'parallel_processing': True}
        )
        batch_time = time.time() - start_time
        
        throughput = len(batch_contents) / batch_time
        min_throughput = benchmark_config.get('classification_throughput', 5.0)
        
        assert throughput >= min_throughput, f"Throughput {throughput:.1f}/s, min: {min_throughput}/s"

    @pytest.mark.asyncio
    async def test_error_handling(self, classification_engine):
        """Test classification error handling"""
        # Test empty content
        result = await classification_engine.classify_content(
            content="",
            options={'handle_empty': True}
        )
        assert result is not None  # Should handle gracefully
        
        # Test very long content
        long_content = "Long content " * 3000
        result = await classification_engine.classify_content(
            content=long_content,
            options={'truncate_long_content': True}
        )
        assert result is not None
        
        # Test special characters only
        special_content = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        result = await classification_engine.classify_content(
            content=special_content,
            options={'handle_non_text': True}
        )
        assert result is not None

class TestTopicModeler:
    """Test topic modeler component"""
    
    @pytest.mark.asyncio
    async def test_topic_modeler_initialization(self):
        """Test topic modeler initialization"""
        modeler = TopicModeler()
        assert modeler is not None
        assert hasattr(modeler, 'extract_topics')

class TestContentCategorizer:
    """Test content categorizer component"""
    
    @pytest.mark.asyncio
    async def test_content_categorizer_initialization(self):
        """Test content categorizer initialization"""
        categorizer = ContentCategorizer()
        assert categorizer is not None
        assert hasattr(categorizer, 'categorize_content')

class TestIntentClassifier:
    """Test intent classifier component"""
    
    @pytest.mark.asyncio
    async def test_intent_classifier_initialization(self):
        """Test intent classifier initialization"""
        classifier = IntentClassifier()
        assert classifier is not None
        assert hasattr(classifier, 'classify_intent')

class TestClassificationConfig:
    """Test classification configuration"""
    
    def test_config_creation(self):
        """Test classification configuration creation"""
        config = ClassificationConfig(
            classification_models=['basic', 'advanced'],
            topic_categories=['technology', 'health', 'business'],
            confidence_threshold=0.7
        )
        
        assert 'basic' in config.classification_models
        assert 'technology' in config.topic_categories
        assert config.confidence_threshold == 0.7
