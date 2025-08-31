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
Comprehensive Tests for NLP Sentiment Analysis Module

Industrial-grade tests for AdvancedSentimentAnalyzer covering emotion detection,
mood analysis, and sentiment optimization with real implementations.

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

from ai.nlp.sentiment import (
    AdvancedSentimentAnalyzer, SentimentScore, EmotionAnalysis,
    EngagementSentiment, SentimentAnalysisResult
)
try:
    from ai.nlp.utils import Platform, Language, ContentType
except ImportError:
    Platform = type('Platform', (), {'INSTAGRAM': 'instagram', 'TIKTOK': 'tiktok', 'TWITTER': 'twitter'})
    Language = type('Language', (), {'EN': 'en', 'DE': 'de', 'FR': 'fr'})
    ContentType = type('ContentType', (), {'POST': 'post', 'STORY': 'story'})

logger = logging.getLogger(__name__)

class TestAdvancedSentimentAnalyzer:
    """Comprehensive tests for AdvancedSentimentAnalyzer"""
    
    @pytest.mark.asyncio
    async def test_analyzer_initialization(self, sentiment_analyzer):
        """Test sentiment analyzer initialization"""
        assert sentiment_analyzer is not None
        assert hasattr(sentiment_analyzer, 'config')
        assert hasattr(sentiment_analyzer, 'emotion_detector')
        assert hasattr(sentiment_analyzer, 'mood_analyzer')
        assert hasattr(sentiment_analyzer, 'sentiment_optimizer')
        
        # Test configuration
        config = sentiment_analyzer.config
        assert 'emotion_models' in config
        assert 'sentiment_scale' in config
        assert 'supported_languages' in config

    @pytest.mark.asyncio
    async def test_basic_sentiment_analysis(self, sentiment_analyzer):
        """Test basic sentiment analysis"""
        test_cases = [
            {
                'text': "I absolutely love this amazing product! It's fantastic!",
                'expected_sentiment': 'positive',
                'expected_confidence': 0.8
            },
            {
                'text': "This is terrible and I hate it completely.",
                'expected_sentiment': 'negative',
                'expected_confidence': 0.8
            },
            {
                'text': "The weather is okay today, nothing special.",
                'expected_sentiment': 'neutral',
                'expected_confidence': 0.6
            },
            {
                'text': "I'm so excited and happy about this opportunity!",
                'expected_sentiment': 'positive',
                'expected_confidence': 0.9
            },
            {
                'text': "Feeling disappointed and frustrated with the service.",
                'expected_sentiment': 'negative',
                'expected_confidence': 0.8
            }
        ]
        
        for case in test_cases:
            sentiment_result = await sentiment_analyzer.analyze_sentiment(
                text=case['text'],
                options={
                    'detailed_analysis': True,
                    'emotion_detection': True,
                    'confidence_scoring': True
                }
            )
            
            assert sentiment_result is not None
            assert isinstance(sentiment_result, dict)
            assert 'sentiment' in sentiment_result
            assert 'confidence' in sentiment_result
            assert 'sentiment_score' in sentiment_result
            assert 'emotion_profile' in sentiment_result
            
            sentiment = sentiment_result['sentiment']
            confidence = sentiment_result['confidence']
            score = sentiment_result['sentiment_score']
            
            # Verify sentiment classification
            assert sentiment in ['positive', 'negative', 'neutral']
            assert sentiment == case['expected_sentiment']
            
            # Verify confidence and score
            assert 0.0 <= confidence <= 1.0
            assert confidence >= case['expected_confidence'] - 0.2  # Allow some tolerance
            assert -1.0 <= score <= 1.0
            
            # Verify sentiment score alignment
            if sentiment == 'positive':
                assert score > 0.1
            elif sentiment == 'negative':
                assert score < -0.1
            else:  # neutral
                assert -0.3 <= score <= 0.3

    @pytest.mark.asyncio
    async def test_emotion_detection(self, sentiment_analyzer):
        """Test advanced emotion detection"""
        emotion_test_cases = [
            {
                'text': "I'm absolutely thrilled and can't contain my excitement!",
                'expected_emotions': ['joy', 'excitement'],
                'dominant_emotion': 'joy'
            },
            {
                'text': "I feel so angry and frustrated about this situation!",
                'expected_emotions': ['anger', 'frustration'],
                'dominant_emotion': 'anger'
            },
            {
                'text': "This makes me feel worried and anxious about the future.",
                'expected_emotions': ['fear', 'anxiety'],
                'dominant_emotion': 'fear'
            },
            {
                'text': "I'm feeling sad and disappointed about what happened.",
                'expected_emotions': ['sadness', 'disappointment'],
                'dominant_emotion': 'sadness'
            },
            {
                'text': "What a wonderful surprise! I'm so grateful and happy!",
                'expected_emotions': ['joy', 'gratitude', 'surprise'],
                'dominant_emotion': 'joy'
            }
        ]
        
        for case in emotion_test_cases:
            emotion_analysis = await sentiment_analyzer.detect_emotions(
                text=case['text'],
                options={
                    'granular_emotions': True,
                    'emotion_intensity': True,
                    'emotional_context': True,
                    'multi_emotion_detection': True
                }
            )
            
            assert emotion_analysis is not None
            assert 'emotions' in emotion_analysis
            assert 'dominant_emotion' in emotion_analysis
            assert 'emotion_intensity' in emotion_analysis
            assert 'emotional_complexity' in emotion_analysis
            
            emotions = emotion_analysis['emotions']
            dominant = emotion_analysis['dominant_emotion']
            intensity = emotion_analysis['emotion_intensity']
            
            # Check emotion detection
            assert isinstance(emotions, dict)
            assert len(emotions) > 0
            assert dominant == case['dominant_emotion']
            assert 0.0 <= intensity <= 1.0
            
            # Check for expected emotions
            detected_emotion_names = list(emotions.keys())
            for expected_emotion in case['expected_emotions']:
                # Should detect at least one expected emotion
                emotion_found = any(
                    expected_emotion in emotion_name.lower() 
                    for emotion_name in detected_emotion_names
                )
                if not emotion_found:
                    # Alternative check for similar emotions
                    emotion_mappings = {
                        'joy': ['happiness', 'joy', 'delight'],
                        'anger': ['anger', 'rage', 'fury'],
                        'fear': ['fear', 'anxiety', 'worry'],
                        'sadness': ['sadness', 'sorrow', 'grief']
                    }
                    if expected_emotion in emotion_mappings:
                        alternative_found = any(
                            alt in emotion_name.lower()
                            for alt in emotion_mappings[expected_emotion]
                            for emotion_name in detected_emotion_names
                        )
                        assert alternative_found, f"Expected emotion {expected_emotion} not found in {detected_emotion_names}"

    @pytest.mark.asyncio
    async def test_multilingual_sentiment_analysis(self, sentiment_analyzer, sample_texts):
        """Test multilingual sentiment analysis"""
        multilingual_test_cases = [
            {
                'language': 'english',
                'positive_text': "I love this amazing product!",
                'negative_text': "This is absolutely terrible!"
            },
            {
                'language': 'german',
                'positive_text': "Ich liebe dieses fantastische Produkt!",
                'negative_text': "Das ist absolut schrecklich!"
            },
            {
                'language': 'french',
                'positive_text': "J'adore ce produit incroyable!",
                'negative_text': "C'est absolument terrible!"
            },
            {
                'language': 'spanish',
                'positive_text': "¡Me encanta este producto increíble!",
                'negative_text': "¡Esto es absolutamente terrible!"
            }
        ]
        
        for case in multilingual_test_cases:
            # Test positive sentiment
            positive_result = await sentiment_analyzer.analyze_sentiment(
                text=case['positive_text'],
                language=case['language'],
                options={
                    'multilingual_analysis': True,
                    'cultural_context': True
                }
            )
            
            assert positive_result['sentiment'] == 'positive'
            assert positive_result['confidence'] > 0.6
            
            # Test negative sentiment
            negative_result = await sentiment_analyzer.analyze_sentiment(
                text=case['negative_text'],
                language=case['language'],
                options={
                    'multilingual_analysis': True,
                    'cultural_context': True
                }
            )
            
            assert negative_result['sentiment'] == 'negative'
            assert negative_result['confidence'] > 0.6

    @pytest.mark.asyncio
    async def test_social_media_sentiment_analysis(self, sentiment_analyzer, sample_social_content):
        """Test social media content sentiment analysis"""
        platforms = [Platform.INSTAGRAM, Platform.TWITTER, Platform.LINKEDIN]
        
        for platform in platforms:
            content = sample_social_content[platform.value.lower()]['post']
            
            social_sentiment = await sentiment_analyzer.analyze_social_sentiment(
                content=content,
                platform=platform,
                options={
                    'hashtag_sentiment': True,
                    'emoji_analysis': True,
                    'social_context': True,
                    'engagement_prediction': True
                }
            )
            
            assert social_sentiment is not None
            assert 'overall_sentiment' in social_sentiment
            assert 'hashtag_sentiment' in social_sentiment
            assert 'emoji_sentiment' in social_sentiment
            assert 'engagement_sentiment_score' in social_sentiment
            assert 'platform_optimization_suggestions' in social_sentiment
            
            # Should have reasonable sentiment scores
            overall = social_sentiment['overall_sentiment']
            assert 'sentiment' in overall
            assert 'confidence' in overall
            assert overall['sentiment'] in ['positive', 'negative', 'neutral']

    @pytest.mark.asyncio
    async def test_sentiment_trends_analysis(self, sentiment_analyzer):
        """Test sentiment trends over time"""
        # Simulate content evolution over time
        content_timeline = [
            {
                'text': "Excited to start this new project!",
                'timestamp': time.time() - 7*24*3600,  # 7 days ago
                'expected_trend': 'positive'
            },
            {
                'text': "Making good progress on the project.",
                'timestamp': time.time() - 5*24*3600,  # 5 days ago
                'expected_trend': 'positive'
            },
            {
                'text': "Facing some challenges but staying optimistic.",
                'timestamp': time.time() - 3*24*3600,  # 3 days ago
                'expected_trend': 'neutral'
            },
            {
                'text': "Frustrated with the setbacks we're experiencing.",
                'timestamp': time.time() - 1*24*3600,  # 1 day ago
                'expected_trend': 'negative'
            },
            {
                'text': "Finally solved the issues! Great progress today!",
                'timestamp': time.time(),  # Now
                'expected_trend': 'positive'
            }
        ]
        
        trend_analysis = await sentiment_analyzer.analyze_sentiment_trends(
            content_timeline=content_timeline,
            options={
                'trend_detection': True,
                'sentiment_momentum': True,
                'pattern_recognition': True,
                'future_prediction': True
            }
        )
        
        assert trend_analysis is not None
        assert 'sentiment_timeline' in trend_analysis
        assert 'trend_direction' in trend_analysis
        assert 'sentiment_momentum' in trend_analysis
        assert 'pattern_insights' in trend_analysis
        assert 'future_prediction' in trend_analysis
        
        timeline = trend_analysis['sentiment_timeline']
        assert len(timeline) == len(content_timeline)
        
        # Should show sentiment progression
        for i, point in enumerate(timeline):
            assert 'sentiment' in point
            assert 'timestamp' in point
            assert 'confidence' in point

    @pytest.mark.asyncio
    async def test_contextual_sentiment_analysis(self, sentiment_analyzer):
        """Test contextual sentiment analysis"""
        contextual_test_cases = [
            {
                'text': "This is sick!",
                'contexts': [
                    {
                        'context': 'youth_slang',
                        'expected_sentiment': 'positive'  # "sick" means "cool"
                    },
                    {
                        'context': 'medical',
                        'expected_sentiment': 'negative'  # "sick" means ill
                    }
                ]
            },
            {
                'text': "That's mad!",
                'contexts': [
                    {
                        'context': 'british_slang',
                        'expected_sentiment': 'positive'  # "mad" means crazy good
                    },
                    {
                        'context': 'general',
                        'expected_sentiment': 'negative'  # "mad" means angry
                    }
                ]
            }
        ]
        
        for test_case in contextual_test_cases:
            for context_info in test_case['contexts']:
                contextual_result = await sentiment_analyzer.analyze_contextual_sentiment(
                    text=test_case['text'],
                    context={
                        'type': context_info['context'],
                        'domain': context_info['context'],
                        'cultural_background': 'diverse'
                    },
                    options={
                        'context_sensitivity': 'high',
                        'cultural_awareness': True,
                        'slang_detection': True
                    }
                )
                
                assert contextual_result is not None
                assert 'contextual_sentiment' in contextual_result
                assert 'context_confidence' in contextual_result
                
                sentiment = contextual_result['contextual_sentiment']['sentiment']
                expected = context_info['expected_sentiment']
                
                # Should interpret according to context
                assert sentiment == expected, f"Expected {expected}, got {sentiment} for '{test_case['text']}' in {context_info['context']} context"

    @pytest.mark.asyncio
    async def test_sentiment_optimization(self, sentiment_analyzer):
        """Test sentiment optimization for content"""
        content_to_optimize = [
            {
                'original': "This product is okay, nothing special.",
                'target_sentiment': 'positive',
                'expected_improvement': True
            },
            {
                'original': "I hate this terrible experience.",
                'target_sentiment': 'neutral',
                'expected_improvement': True
            },
            {
                'original': "The service was disappointing and slow.",
                'target_sentiment': 'positive',
                'expected_improvement': True
            }
        ]
        
        for case in content_to_optimize:
            optimization_result = await sentiment_analyzer.optimize_sentiment(
                content=case['original'],
                target_sentiment=case['target_sentiment'],
                options={
                    'preserve_meaning': True,
                    'maintain_authenticity': True,
                    'gradual_optimization': True,
                    'style_preservation': True
                }
            )
            
            assert optimization_result is not None
            assert 'optimized_content' in optimization_result
            assert 'sentiment_improvement' in optimization_result
            assert 'optimization_strategies' in optimization_result
            assert 'authenticity_score' in optimization_result
            
            optimized = optimization_result['optimized_content']
            improvement = optimization_result['sentiment_improvement']
            authenticity = optimization_result['authenticity_score']
            
            # Should improve sentiment
            assert len(optimized) > 0
            assert optimized != case['original']  # Should be changed
            assert improvement > 0 if case['expected_improvement'] else True
            assert 0.0 <= authenticity <= 1.0
            
            # Verify improved sentiment
            verification = await sentiment_analyzer.analyze_sentiment(
                text=optimized,
                options={'quick_analysis': True}
            )
            
            if case['target_sentiment'] == 'positive':
                assert verification['sentiment_score'] > 0
            elif case['target_sentiment'] == 'neutral':
                assert -0.3 <= verification['sentiment_score'] <= 0.3

    @pytest.mark.asyncio
    async def test_emotion_intensity_analysis(self, sentiment_analyzer):
        """Test emotion intensity analysis"""
        intensity_test_cases = [
            {
                'text': "I'm slightly happy about this.",
                'expected_intensity': 'low'
            },
            {
                'text': "I'm really excited and happy!",
                'expected_intensity': 'medium'
            },
            {
                'text': "I'm absolutely ecstatic and overjoyed!!!",
                'expected_intensity': 'high'
            },
            {
                'text': "I'm a bit disappointed.",
                'expected_intensity': 'low'
            },
            {
                'text': "I'm extremely angry and furious!",
                'expected_intensity': 'high'
            }
        ]
        
        for case in intensity_test_cases:
            intensity_analysis = await sentiment_analyzer.analyze_emotion_intensity(
                text=case['text'],
                options={
                    'granular_intensity': True,
                    'intensity_indicators': True,
                    'linguistic_markers': True
                }
            )
            
            assert intensity_analysis is not None
            assert 'overall_intensity' in intensity_analysis
            assert 'intensity_score' in intensity_analysis
            assert 'intensity_indicators' in intensity_analysis
            
            intensity_score = intensity_analysis['intensity_score']
            assert 0.0 <= intensity_score <= 1.0
            
            # Check intensity levels
            if case['expected_intensity'] == 'low':
                assert intensity_score < 0.4
            elif case['expected_intensity'] == 'medium':
                assert 0.3 <= intensity_score <= 0.7
            elif case['expected_intensity'] == 'high':
                assert intensity_score > 0.6

    @pytest.mark.asyncio
    async def test_sentiment_confidence_calibration(self, sentiment_analyzer):
        """Test sentiment confidence calibration"""
        confidence_test_cases = [
            {
                'text': "This is absolutely amazing and perfect!",
                'expected_confidence': 'high'  # Clear positive sentiment
            },
            {
                'text': "This is terrible and awful.",
                'expected_confidence': 'high'  # Clear negative sentiment
            },
            {
                'text': "It's okay, I guess.",
                'expected_confidence': 'low'  # Ambiguous sentiment
            },
            {
                'text': "I love it but hate the price.",
                'expected_confidence': 'medium'  # Mixed sentiment
            }
        ]
        
        for case in confidence_test_cases:
            result = await sentiment_analyzer.analyze_sentiment(
                text=case['text'],
                options={
                    'confidence_calibration': True,
                    'uncertainty_estimation': True
                }
            )
            
            confidence = result['confidence']
            
            if case['expected_confidence'] == 'high':
                assert confidence > 0.8
            elif case['expected_confidence'] == 'medium':
                assert 0.5 <= confidence <= 0.8
            elif case['expected_confidence'] == 'low':
                assert confidence < 0.6

    @pytest.mark.asyncio
    async def test_batch_sentiment_analysis(self, sentiment_analyzer, performance_test_data):
        """Test batch sentiment analysis"""
        texts = performance_test_data['small_batch']
        
        start_time = time.time()
        batch_results = await sentiment_analyzer.analyze_batch_sentiment(
            texts=texts,
            options={
                'parallel_processing': True,
                'consistent_analysis': True,
                'quality_assurance': True
            }
        )
        processing_time = time.time() - start_time
        
        assert batch_results is not None
        assert 'results' in batch_results
        assert 'batch_statistics' in batch_results
        assert 'processing_metrics' in batch_results
        
        results = batch_results['results']
        assert len(results) == len(texts)
        
        # All results should have required fields
        for result in results:
            assert 'sentiment' in result
            assert 'confidence' in result
            assert 'sentiment_score' in result
        
        # Should process efficiently
        throughput = len(texts) / processing_time
        assert throughput > 5.0  # Should analyze at least 5 texts per second

    @pytest.mark.asyncio
    async def test_cross_platform_sentiment_analysis(self, sentiment_analyzer):
        """Test cross-platform sentiment analysis"""
        base_content = "Just tried this new AI tool and it's incredible!"
        platforms = [Platform.INSTAGRAM, Platform.TWITTER, Platform.LINKEDIN, Platform.TIKTOK]
        
        platform_results = {}
        
        for platform in platforms:
            result = await sentiment_analyzer.analyze_platform_specific_sentiment(
                content=base_content,
                platform=platform,
                options={
                    'platform_context': True,
                    'audience_considerations': True,
                    'engagement_factors': True
                }
            )
            
            platform_results[platform.value] = result
            
            assert result is not None
            assert 'platform_sentiment' in result
            assert 'audience_reception' in result
            assert 'engagement_prediction' in result
        
        # Should have consistent base sentiment across platforms
        base_sentiments = [r['platform_sentiment']['sentiment'] for r in platform_results.values()]
        assert len(set(base_sentiments)) <= 2  # Should be mostly consistent

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, sentiment_analyzer, benchmark_config):
        """Test sentiment analysis performance benchmarks"""
        test_text = "This is a performance test for sentiment analysis benchmarking."
        
        # Single analysis performance
        start_time = time.time()
        result = await sentiment_analyzer.analyze_sentiment(
            text=test_text,
            options={'quick_analysis': True}
        )
        single_time = time.time() - start_time
        
        max_time = benchmark_config.get('max_sentiment_time', 1.0)
        assert single_time < max_time, f"Analysis took {single_time:.3f}s, max: {max_time}s"
        
        # Batch analysis performance
        batch_texts = [f"Batch text {i} for sentiment testing." for i in range(50)]
        
        start_time = time.time()
        batch_result = await sentiment_analyzer.analyze_batch_sentiment(
            texts=batch_texts,
            options={'parallel_processing': True}
        )
        batch_time = time.time() - start_time
        
        throughput = len(batch_texts) / batch_time
        min_throughput = benchmark_config.get('sentiment_throughput', 10.0)
        
        assert throughput >= min_throughput, f"Throughput {throughput:.1f}/s, min: {min_throughput}/s"

    @pytest.mark.asyncio
    async def test_error_handling(self, sentiment_analyzer):
        """Test sentiment analyzer error handling"""
        # Test empty content
        result = await sentiment_analyzer.analyze_sentiment(
            text="",
            options={'handle_empty': True}
        )
        assert result is not None  # Should handle gracefully
        
        # Test very long content
        long_text = "Long content " * 5000
        result = await sentiment_analyzer.analyze_sentiment(
            text=long_text,
            options={'truncate_long_text': True}
        )
        assert result is not None
        
        # Test special characters only
        special_text = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        result = await sentiment_analyzer.analyze_sentiment(
            text=special_text,
            options={'handle_non_text': True}
        )
        assert result is not None

class TestEmotionDetector:
    """Test emotion detector component"""
    
    @pytest.mark.asyncio
    async def test_emotion_detector_initialization(self):
        """Test emotion detector initialization"""
        detector = EmotionDetector()
        assert detector is not None
        assert hasattr(detector, 'detect_emotions')

class TestMoodAnalyzer:
    """Test mood analyzer component"""
    
    @pytest.mark.asyncio
    async def test_mood_analyzer_initialization(self):
        """Test mood analyzer initialization"""
        analyzer = MoodAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_mood')

class TestSentimentOptimizer:
    """Test sentiment optimizer component"""
    
    @pytest.mark.asyncio
    async def test_sentiment_optimizer_initialization(self):
        """Test sentiment optimizer initialization"""
        optimizer = SentimentOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, 'optimize_sentiment')

class TestSentimentConfig:
    """Test sentiment configuration"""
    
    def test_config_creation(self):
        """Test sentiment configuration creation"""
        config = SentimentConfig(
            emotion_models=['basic', 'advanced'],
            sentiment_scale=[-1.0, 1.0],
            supported_languages=['en', 'de', 'fr']
        )
        
        assert 'basic' in config.emotion_models
        assert config.sentiment_scale == [-1.0, 1.0]
        assert 'en' in config.supported_languages
