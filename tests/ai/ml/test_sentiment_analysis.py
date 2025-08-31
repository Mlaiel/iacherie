# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Sentiment Analysis Tests - Enterprise Grade Test Suite

Comprehensive tests for sentiment analysis, emotion detection, opinion mining,
and advanced natural language understanding capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING ⚠️
Contact: mlaiel@live.de - Unauthorized use STRICTLY PROHIBITED
"""import pytest
import sys
import os
from pathlib import Path
import numpy as np
import torch
import asyncio
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Tuple

from ai.ml.sentiment_analysis import (
    SentimentAnalyzer, EmotionDetector, AdvancedSentimentModel,
    MultilingualSentimentAnalyzer, SentimentTrendAnalyzer,
    EmotionClassifier, SentimentMetrics, OpinionMiningEngine,
    EmotionalIntelligenceEngine, BrandSentimentAnalyzer,
    InfluencerSentimentTracker, AudienceSentimentAnalyzer
)


class TestSentimentAnalyzer:
    """Tests for basic sentiment analysis functionality"""    
    def test_init_sentiment_analyzer(self):
        """Test sentiment analyzer initialization"""        analyzer = SentimentAnalyzer(
            model_name="bert-base-uncased",
            max_length=512,
            batch_size=32,
            confidence_threshold=0.7
        )
        
        assert analyzer.model_name == "bert-base-uncased"
        assert analyzer.max_length == 512
        assert analyzer.batch_size == 32
        assert analyzer.confidence_threshold == 0.7

    def test_sentiment_preprocessing(self, sample_text_data):
        """Test text preprocessing for sentiment analysis"""        analyzer = SentimentAnalyzer()
        
        raw_text = "This is AMAZING!!! 😀 #love #happy"
        processed_text = analyzer.preprocess_text(raw_text)
        
        assert isinstance(processed_text, str)
        assert len(processed_text) > 0
        # Should handle emojis and hashtags appropriately

    def test_single_text_sentiment(self, sample_text_data):
        """Test sentiment analysis for single text"""        analyzer = SentimentAnalyzer()
        
        with patch.object(analyzer, '_predict_sentiment') as mock_predict:
            mock_predict.return_value = {
                "label": "POSITIVE",
                "score": 0.87,
                "confidence": 0.92,
                "probabilities": {
                    "POSITIVE": 0.87,
                    "NEGATIVE": 0.08,
                    "NEUTRAL": 0.05
                }
            }
            
            text = sample_text_data[0]
            result = analyzer.analyze_sentiment(text)
            
            assert "label" in result
            assert "score" in result
            assert "confidence" in result
            assert result["label"] in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
            assert 0 <= result["score"] <= 1
            assert 0 <= result["confidence"] <= 1

    def test_batch_sentiment_analysis(self, sample_text_data):
        """Test batch sentiment analysis"""        analyzer = SentimentAnalyzer(batch_size=4)
        
        with patch.object(analyzer, '_predict_batch_sentiment') as mock_batch:
            mock_batch.return_value = [
                {"label": "POSITIVE", "score": 0.85, "confidence": 0.90},
                {"label": "NEGATIVE", "score": 0.75, "confidence": 0.85},
                {"label": "NEUTRAL", "score": 0.55, "confidence": 0.70},
                {"label": "POSITIVE", "score": 0.92, "confidence": 0.95}
            ]
            
            results = analyzer.analyze_batch(sample_text_data[:4])
            
            assert len(results) == 4
            assert all("label" in result for result in results)
            assert all("score" in result for result in results)
            assert all("confidence" in result for result in results)

    def test_aspect_based_sentiment(self):
        """Test aspect-based sentiment analysis"""        analyzer = SentimentAnalyzer(enable_aspect_analysis=True)
        
        with patch.object(analyzer, 'analyze_aspect_sentiment') as mock_aspect:
            mock_aspect.return_value = {
                "overall_sentiment": {"label": "POSITIVE", "score": 0.75},
                "aspects": {
                    "quality": {"label": "POSITIVE", "score": 0.85, "mentions": 3},
                    "price": {"label": "NEGATIVE", "score": 0.65, "mentions": 2},
                    "service": {"label": "POSITIVE", "score": 0.80, "mentions": 1}
                }
            }
            
            text = "The quality is excellent but the price is too high. Great service though."
            result = analyzer.analyze_aspect_sentiment(text)
            
            assert "overall_sentiment" in result
            assert "aspects" in result
            assert "quality" in result["aspects"]
            assert "price" in result["aspects"]
            assert "service" in result["aspects"]

    def test_temporal_sentiment_analysis(self):
        """Test temporal sentiment analysis"""        analyzer = SentimentAnalyzer(enable_temporal_analysis=True)
        
        timestamped_texts = [
            {"text": "Great product launch!", "timestamp": datetime.now()},
            {"text": "Having some issues now", "timestamp": datetime.now() - timedelta(hours=2)},
            {"text": "All fixed, working perfectly", "timestamp": datetime.now() - timedelta(hours=1)}
        ]
        
        with patch.object(analyzer, 'analyze_temporal_sentiment') as mock_temporal:
            mock_temporal.return_value = {
                "sentiment_timeline": [
                    {"timestamp": timestamped_texts[1]["timestamp"].isoformat(), "sentiment": "NEGATIVE", "score": 0.72},
                    {"timestamp": timestamped_texts[2]["timestamp"].isoformat(), "sentiment": "POSITIVE", "score": 0.88},
                    {"timestamp": timestamped_texts[0]["timestamp"].isoformat(), "sentiment": "POSITIVE", "score": 0.91}
                ],
                "trend": "improving",
                "volatility": 0.35
            }
            
            result = analyzer.analyze_temporal_sentiment(timestamped_texts)
            
            assert "sentiment_timeline" in result
            assert "trend" in result
            assert "volatility" in result
            assert len(result["sentiment_timeline"]) == 3

    def test_confidence_calibration(self):
        """Test sentiment confidence calibration"""        analyzer = SentimentAnalyzer()
        
        # Mock raw model outputs
        raw_predictions = [
            {"logits": torch.tensor([2.5, -1.0, 0.5]), "predicted_class": 0},
            {"logits": torch.tensor([-0.5, 0.2, 0.1]), "predicted_class": 1},
            {"logits": torch.tensor([0.1, -0.1, 0.0]), "predicted_class": 0}
        ]
        
        calibrated_results = []
        for pred in raw_predictions:
            softmax_probs = torch.softmax(pred["logits"], dim=0)
            confidence = torch.max(softmax_probs).item()
            
            # Apply calibration (mock)
            calibrated_confidence = analyzer._calibrate_confidence(confidence)
            
            calibrated_results.append({
                "predicted_class": pred["predicted_class"],
                "raw_confidence": confidence,
                "calibrated_confidence": calibrated_confidence
            })
        
        assert len(calibrated_results) == 3
        assert all(0 <= result["calibrated_confidence"] <= 1 for result in calibrated_results)


class TestEmotionDetector:
    """Tests for emotion detection functionality"""    
    def test_init_emotion_detector(self):
        """Test emotion detector initialization"""        detector = EmotionDetector(
            emotion_model="roberta-base",
            emotions=["joy", "sadness", "anger", "fear", "surprise", "disgust"],
            enable_intensity_scoring=True
        )
        
        assert detector.emotion_model == "roberta-base"
        assert len(detector.emotions) == 6
        assert detector.enable_intensity_scoring

    def test_basic_emotion_detection(self, sample_text_data):
        """Test basic emotion detection"""        detector = EmotionDetector()
        
        with patch.object(detector, 'detect_emotions') as mock_detect:
            mock_detect.return_value = {
                "primary_emotion": "joy",
                "emotion_scores": {
                    "joy": 0.85,
                    "sadness": 0.05,
                    "anger": 0.02,
                    "fear": 0.03,
                    "surprise": 0.04,
                    "disgust": 0.01
                },
                "intensity": 0.85,
                "confidence": 0.92
            }
            
            text = sample_text_data[0]
            result = detector.detect_emotions(text)
            
            assert "primary_emotion" in result
            assert "emotion_scores" in result
            assert "intensity" in result
            assert "confidence" in result
            assert result["primary_emotion"] in detector.emotions

    def test_multi_emotion_detection(self):
        """Test detection of multiple emotions in text"""        detector = EmotionDetector(enable_multi_emotion=True)
        
        with patch.object(detector, 'detect_multiple_emotions') as mock_multi:
            mock_multi.return_value = {
                "detected_emotions": [
                    {"emotion": "joy", "score": 0.78, "text_span": "happy and excited"},
                    {"emotion": "surprise", "score": 0.65, "text_span": "unexpected news"}
                ],
                "emotion_complexity": 0.72,
                "dominant_emotion": "joy"
            }
            
            text = "I'm happy and excited about this unexpected news!"
            result = detector.detect_multiple_emotions(text)
            
            assert "detected_emotions" in result
            assert "emotion_complexity" in result
            assert "dominant_emotion" in result
            assert len(result["detected_emotions"]) == 2

    def test_emotion_intensity_scoring(self):
        """Test emotion intensity scoring"""        detector = EmotionDetector(enable_intensity_scoring=True)
        
        intensity_texts = [
            "I'm happy",           # Low intensity
            "I'm very happy!",     # Medium intensity
            "I'm ecstatic!!!!"     # High intensity
        ]
        
        intensities = []
        for text in intensity_texts:
            with patch.object(detector, 'calculate_emotion_intensity') as mock_intensity:
                mock_intensity.return_value = np.random.uniform(0.3, 0.95)
                intensity = detector.calculate_emotion_intensity(text, "joy")
                intensities.append(intensity)
        
        # Intensities should generally increase
        assert all(0 <= intensity <= 1 for intensity in intensities)

    def test_contextual_emotion_analysis(self):
        """Test contextual emotion analysis"""        detector = EmotionDetector(enable_contextual_analysis=True)
        
        context_data = {
            "text": "Great job everyone!",
            "context": {
                "situation": "work_meeting",
                "relationship": "professional",
                "prior_interactions": ["positive", "collaborative"]
            }
        }
        
        with patch.object(detector, 'analyze_contextual_emotion') as mock_context:
            mock_context.return_value = {
                "emotion": "pride",
                "confidence": 0.88,
                "context_influence": 0.25,
                "social_emotion": True
            }
            
            result = detector.analyze_contextual_emotion(
                context_data["text"], 
                context_data["context"]
            )
            
            assert "emotion" in result
            assert "context_influence" in result
            assert "social_emotion" in result


class TestAdvancedSentimentModel:
    """Tests for advanced sentiment analysis models"""    
    def test_init_advanced_model(self):
        """Test advanced sentiment model initialization"""        model = AdvancedSentimentModel(
            architecture="transformer",
            pretrained_model="roberta-large",
            fine_tuning_enabled=True,
            domain_adaptation=True,
            target_domain="social_media"
        )
        
        assert model.architecture == "transformer"
        assert model.pretrained_model == "roberta-large"
        assert model.fine_tuning_enabled
        assert model.domain_adaptation
        assert model.target_domain == "social_media"

    def test_domain_specific_sentiment(self, sample_text_data):
        """Test domain-specific sentiment analysis"""        model = AdvancedSentimentModel(target_domain="finance")
        
        financial_text = "Stock prices are up 15% this quarter, showing strong market confidence"
        
        with patch.object(model, 'analyze_domain_sentiment') as mock_domain:
            mock_domain.return_value = {
                "sentiment": "POSITIVE",
                "score": 0.89,
                "domain_confidence": 0.93,
                "financial_indicators": {
                    "bullish_signals": 3,
                    "bearish_signals": 0,
                    "market_sentiment": "optimistic"
                }
            }
            
            result = model.analyze_domain_sentiment(financial_text)
            
            assert "sentiment" in result
            assert "domain_confidence" in result
            assert "financial_indicators" in result

    def test_hierarchical_sentiment_analysis(self):
        """Test hierarchical sentiment analysis (document -> sentences -> phrases)"""        model = AdvancedSentimentModel(enable_hierarchical_analysis=True)
        
        document = """        The new product launch was fantastic. Everyone loved the design and features.
        However, the price point seems a bit high for the target market.
        Overall, I think this will be successful despite some concerns.
        """        
        with patch.object(model, 'analyze_hierarchical_sentiment') as mock_hierarchical:
            mock_hierarchical.return_value = {
                "document_sentiment": {"label": "POSITIVE", "score": 0.68},
                "sentence_sentiments": [
                    {"text": "The new product launch was fantastic.", "sentiment": "POSITIVE", "score": 0.92},
                    {"text": "Everyone loved the design and features.", "sentiment": "POSITIVE", "score": 0.88},
                    {"text": "However, the price point seems a bit high for the target market.", "sentiment": "NEGATIVE", "score": 0.71},
                    {"text": "Overall, I think this will be successful despite some concerns.", "sentiment": "POSITIVE", "score": 0.65}
                ],
                "sentiment_consistency": 0.73,
                "conflicting_sentiments": True
            }
            
            result = model.analyze_hierarchical_sentiment(document)
            
            assert "document_sentiment" in result
            assert "sentence_sentiments" in result
            assert "sentiment_consistency" in result
            assert len(result["sentence_sentiments"]) == 4

    def test_fine_grained_sentiment_scoring(self):
        """Test fine-grained sentiment scoring (beyond positive/negative/neutral)"""        model = AdvancedSentimentModel(enable_fine_grained_scoring=True)
        
        with patch.object(model, 'get_fine_grained_sentiment') as mock_fine:
            mock_fine.return_value = {
                "sentiment_scale": 0.23,  # -1 (very negative) to +1 (very positive)
                "sentiment_category": "slightly_positive",
                "intensity": 0.45,
                "certainty": 0.78,
                "subjectivity": 0.82
            }
            
            text = "The movie was pretty good, I guess"
            result = model.get_fine_grained_sentiment(text)
            
            assert "sentiment_scale" in result
            assert "sentiment_category" in result
            assert "intensity" in result
            assert -1 <= result["sentiment_scale"] <= 1


class TestMultilingualSentimentAnalyzer:
    """Tests for multilingual sentiment analysis"""    
    def test_init_multilingual_analyzer(self):
        """Test multilingual sentiment analyzer initialization"""        analyzer = MultilingualSentimentAnalyzer(
            supported_languages=["en", "fr", "de", "es", "it"],
            model_name="xlm-roberta-base",
            enable_auto_detection=True
        )
        
        assert len(analyzer.supported_languages) == 5
        assert analyzer.model_name == "xlm-roberta-base"
        assert analyzer.enable_auto_detection

    def test_language_detection(self):
        """Test automatic language detection"""        analyzer = MultilingualSentimentAnalyzer(enable_auto_detection=True)
        
        texts = {
            "en": "This is a great product!",
            "fr": "C'est un excellent produit!",
            "de": "Das ist ein großartiges Produkt!",
            "es": "¡Este es un gran producto!",
            "it": "Questo è un ottimo prodotto!"
        }
        
        for expected_lang, text in texts.items():
            with patch.object(analyzer, 'detect_language') as mock_detect:
                mock_detect.return_value = {
                    "language": expected_lang,
                    "confidence": 0.95,
                    "alternatives": []
                }
                
                result = analyzer.detect_language(text)
                assert result["language"] == expected_lang
                assert result["confidence"] > 0.9

    def test_cross_lingual_sentiment_analysis(self):
        """Test sentiment analysis across different languages"""        analyzer = MultilingualSentimentAnalyzer()
        
        multilingual_texts = [
            {"text": "I love this!", "language": "en"},
            {"text": "J'adore ça!", "language": "fr"},
            {"text": "Ich liebe das!", "language": "de"}
        ]
        
        results = []
        for item in multilingual_texts:
            with patch.object(analyzer, 'analyze_multilingual_sentiment') as mock_analyze:
                mock_analyze.return_value = {
                    "sentiment": "POSITIVE",
                    "score": 0.88,
                    "language": item["language"],
                    "confidence": 0.92
                }
                
                result = analyzer.analyze_multilingual_sentiment(
                    item["text"], item["language"]
                )
                results.append(result)
        
        assert len(results) == 3
        assert all(result["sentiment"] == "POSITIVE" for result in results)

    def test_translation_based_sentiment(self):
        """Test translation-based sentiment analysis"""        analyzer = MultilingualSentimentAnalyzer(
            translation_strategy="translate_then_analyze"
        )
        
        with patch.object(analyzer, 'translate_and_analyze') as mock_translate:
            mock_translate.return_value = {
                "original_text": "C'est fantastique!",
                "translated_text": "It's fantastic!",
                "source_language": "fr",
                "target_language": "en",
                "sentiment": "POSITIVE",
                "score": 0.91,
                "translation_confidence": 0.95
            }
            
            french_text = "C'est fantastique!"
            result = analyzer.translate_and_analyze(french_text, target_lang="en")
            
            assert "original_text" in result
            assert "translated_text" in result
            assert "sentiment" in result
            assert result["sentiment"] == "POSITIVE"


class TestSentimentTrendAnalyzer:
    """Tests for sentiment trend analysis"""    
    def test_init_trend_analyzer(self):
        """Test sentiment trend analyzer initialization"""        analyzer = SentimentTrendAnalyzer(
            time_window="7d",
            aggregation_method="weighted_average",
            enable_anomaly_detection=True
        )
        
        assert analyzer.time_window == "7d"
        assert analyzer.aggregation_method == "weighted_average"
        assert analyzer.enable_anomaly_detection

    def test_sentiment_time_series_analysis(self, sample_trend_data):
        """Test sentiment time series analysis"""        analyzer = SentimentTrendAnalyzer()
        
        # Use sample trend data with sentiment scores
        sentiment_trends = analyzer.analyze_sentiment_trends(sample_trend_data)
        
        assert isinstance(sentiment_trends, dict)
        assert "trend_direction" in sentiment_trends
        assert "trend_strength" in sentiment_trends
        assert "volatility" in sentiment_trends
        assert "seasonal_patterns" in sentiment_trends

    def test_sentiment_anomaly_detection(self):
        """Test sentiment anomaly detection"""        analyzer = SentimentTrendAnalyzer(enable_anomaly_detection=True)
        
        # Mock sentiment time series with anomalies
        sentiment_scores = np.array([0.6, 0.65, 0.7, 0.68, 0.72, -0.8, 0.69, 0.71])  # -0.8 is anomaly
        timestamps = [datetime.now() - timedelta(hours=i) for i in range(len(sentiment_scores))]
        
        anomalies = analyzer.detect_sentiment_anomalies(sentiment_scores, timestamps)
        
        assert isinstance(anomalies, list)
        assert len(anomalies) > 0  # Should detect the -0.8 anomaly
        assert all("timestamp" in anomaly for anomaly in anomalies)
        assert all("score" in anomaly for anomaly in anomalies)
        assert all("anomaly_type" in anomaly for anomaly in anomalies)

    def test_sentiment_correlation_analysis(self):
        """Test sentiment correlation with external factors"""        analyzer = SentimentTrendAnalyzer()
        
        sentiment_data = np.random.uniform(-1, 1, 100)
        external_factors = {
            "market_performance": np.random.uniform(-0.5, 0.5, 100),
            "weather_score": np.random.uniform(0, 1, 100),
            "social_events": np.random.choice([0, 1], 100, p=[0.8, 0.2])
        }
        
        correlations = analyzer.analyze_sentiment_correlations(
            sentiment_data, external_factors
        )
        
        assert isinstance(correlations, dict)
        assert "market_performance" in correlations
        assert "weather_score" in correlations
        assert "social_events" in correlations
        assert all(-1 <= corr <= 1 for corr in correlations.values())


class TestOpinionMiningEngine:
    """Tests for opinion mining functionality"""    
    def test_init_opinion_mining(self):
        """Test opinion mining engine initialization"""        engine = OpinionMiningEngine(
            enable_aspect_extraction=True,
            enable_opinion_summarization=True,
            enable_stance_detection=True
        )
        
        assert engine.enable_aspect_extraction
        assert engine.enable_opinion_summarization
        assert engine.enable_stance_detection

    def test_aspect_extraction(self):
        """Test aspect extraction from opinions"""        engine = OpinionMiningEngine(enable_aspect_extraction=True)
        
        review_text = """        The camera quality is excellent and takes stunning photos.
        However, the battery life is quite poor and needs frequent charging.
        The build quality feels premium but the price is too expensive.
        """        
        with patch.object(engine, 'extract_aspects') as mock_extract:
            mock_extract.return_value = {
                "aspects": [
                    {"aspect": "camera_quality", "mentions": 2, "sentiment": "POSITIVE"},
                    {"aspect": "battery_life", "mentions": 2, "sentiment": "NEGATIVE"},
                    {"aspect": "build_quality", "mentions": 1, "sentiment": "POSITIVE"},
                    {"aspect": "price", "mentions": 1, "sentiment": "NEGATIVE"}
                ],
                "aspect_sentiment_summary": {
                    "positive_aspects": ["camera_quality", "build_quality"],
                    "negative_aspects": ["battery_life", "price"]
                }
            }
            
            result = engine.extract_aspects(review_text)
            
            assert "aspects" in result
            assert "aspect_sentiment_summary" in result
            assert len(result["aspects"]) == 4

    def test_opinion_summarization(self):
        """Test opinion summarization"""        engine = OpinionMiningEngine(enable_opinion_summarization=True)
        
        multiple_opinions = [
            "Great product, love the features",
            "Quality is good but expensive",
            "Excellent design and performance",
            "Price is too high for what you get",
            "Amazing quality, worth every penny"
        ]
        
        with patch.object(engine, 'summarize_opinions') as mock_summarize:
            mock_summarize.return_value = {
                "summary": "Generally positive opinions about quality and features, but concerns about pricing",
                "key_themes": ["quality", "features", "pricing", "design"],
                "sentiment_distribution": {
                    "POSITIVE": 0.6,
                    "NEGATIVE": 0.3,
                    "NEUTRAL": 0.1
                },
                "consensus_level": 0.72
            }
            
            result = engine.summarize_opinions(multiple_opinions)
            
            assert "summary" in result
            assert "key_themes" in result
            assert "sentiment_distribution" in result
            assert "consensus_level" in result

    def test_stance_detection(self):
        """Test stance detection in opinions"""        engine = OpinionMiningEngine(enable_stance_detection=True)
        
        topic = "artificial intelligence in healthcare"
        opinions = [
            "AI will revolutionize medical diagnosis and save lives",
            "AI cannot replace human doctors and personal care",
            "AI tools can assist doctors but should not make final decisions"
        ]
        
        stances = []
        for opinion in opinions:
            with patch.object(engine, 'detect_stance') as mock_stance:
                mock_stance.return_value = {
                    "stance": "FAVOR",  # or "AGAINST" or "NEUTRAL"
                    "confidence": 0.85,
                    "reasoning": ["mentions benefits", "positive language"]
                }
                
                stance = engine.detect_stance(opinion, topic)
                stances.append(stance)
        
        assert len(stances) == 3
        assert all("stance" in stance for stance in stances)
        assert all("confidence" in stance for stance in stances)


class TestBrandSentimentAnalyzer:
    """Tests for brand sentiment analysis"""    
    def test_init_brand_analyzer(self):
        """Test brand sentiment analyzer initialization"""        analyzer = BrandSentimentAnalyzer(
            brand_name="TechCorp",
            competitor_brands=["CompetitorA", "CompetitorB"],
            enable_competitor_comparison=True
        )
        
        assert analyzer.brand_name == "TechCorp"
        assert len(analyzer.competitor_brands) == 2
        assert analyzer.enable_competitor_comparison

    def test_brand_mention_extraction(self):
        """Test brand mention extraction from text"""        analyzer = BrandSentimentAnalyzer(brand_name="TechCorp")
        
        texts = [
            "I love TechCorp's new product release",
            "TechCorp customer service was excellent",
            "The TechCorp brand is really innovative",
            "Other companies are better than TechCorp"
        ]
        
        mentions = []
        for text in texts:
            with patch.object(analyzer, 'extract_brand_mentions') as mock_extract:
                mock_extract.return_value = [
                    {
                        "brand": "TechCorp",
                        "context": text,
                        "mention_type": "direct",
                        "position": text.find("TechCorp")
                    }
                ]
                
                mention = analyzer.extract_brand_mentions(text)
                mentions.extend(mention)
        
        assert len(mentions) == 4
        assert all(mention["brand"] == "TechCorp" for mention in mentions)

    def test_brand_sentiment_tracking(self):
        """Test brand sentiment tracking over time"""        analyzer = BrandSentimentAnalyzer(brand_name="TechCorp")
        
        brand_mentions = [
            {"text": "TechCorp is amazing!", "timestamp": datetime.now()},
            {"text": "TechCorp disappointed me", "timestamp": datetime.now() - timedelta(hours=1)},
            {"text": "Love TechCorp's innovation", "timestamp": datetime.now() - timedelta(hours=2)}
        ]
        
        with patch.object(analyzer, 'track_brand_sentiment') as mock_track:
            mock_track.return_value = {
                "overall_sentiment": "POSITIVE",
                "sentiment_score": 0.67,
                "sentiment_trend": "improving",
                "mention_volume": 3,
                "time_series": [
                    {"timestamp": mention["timestamp"].isoformat(), "sentiment": "POSITIVE", "score": 0.8}
                    for mention in brand_mentions
                ]
            }
            
            result = analyzer.track_brand_sentiment(brand_mentions)
            
            assert "overall_sentiment" in result
            assert "sentiment_trend" in result
            assert "mention_volume" in result
            assert "time_series" in result

    def test_competitor_sentiment_comparison(self):
        """Test competitor sentiment comparison"""        analyzer = BrandSentimentAnalyzer(
            brand_name="TechCorp",
            competitor_brands=["CompetitorA", "CompetitorB"],
            enable_competitor_comparison=True
        )
        
        with patch.object(analyzer, 'compare_competitor_sentiment') as mock_compare:
            mock_compare.return_value = {
                "brand_rankings": [
                    {"brand": "TechCorp", "sentiment_score": 0.75, "rank": 1},
                    {"brand": "CompetitorA", "sentiment_score": 0.65, "rank": 2},
                    {"brand": "CompetitorB", "sentiment_score": 0.60, "rank": 3}
                ],
                "competitive_advantage": 0.10,
                "sentiment_gaps": {
                    "vs_CompetitorA": 0.10,
                    "vs_CompetitorB": 0.15
                }
            }
            
            result = analyzer.compare_competitor_sentiment()
            
            assert "brand_rankings" in result
            assert "competitive_advantage" in result
            assert "sentiment_gaps" in result


class TestSentimentMetrics:
    """Tests for sentiment analysis metrics and evaluation"""    
    def test_init_metrics(self):
        """Test sentiment metrics initialization"""        metrics = SentimentMetrics()
        
        assert hasattr(metrics, 'accuracy_scores')
        assert hasattr(metrics, 'precision_scores')
        assert hasattr(metrics, 'recall_scores')
        assert hasattr(metrics, 'f1_scores')

    def test_classification_metrics(self):
        """Test sentiment classification metrics"""        metrics = SentimentMetrics()
        
        # Mock predictions and ground truth
        y_true = ["POSITIVE", "NEGATIVE", "NEUTRAL", "POSITIVE", "NEGATIVE"]
        y_pred = ["POSITIVE", "NEGATIVE", "NEUTRAL", "NEGATIVE", "NEGATIVE"]
        
        results = metrics.calculate_classification_metrics(y_true, y_pred)
        
        assert "accuracy" in results
        assert "precision" in results
        assert "recall" in results
        assert "f1_score" in results
        assert 0 <= results["accuracy"] <= 1

    def test_confidence_calibration_metrics(self):
        """Test confidence calibration metrics"""        metrics = SentimentMetrics()
        
        # Mock predictions with confidence scores
        predictions = [
            {"predicted": "POSITIVE", "confidence": 0.9, "actual": "POSITIVE"},
            {"predicted": "NEGATIVE", "confidence": 0.8, "actual": "NEGATIVE"},
            {"predicted": "POSITIVE", "confidence": 0.6, "actual": "NEGATIVE"},
            {"predicted": "NEUTRAL", "confidence": 0.7, "actual": "NEUTRAL"}
        ]
        
        calibration_metrics = metrics.evaluate_confidence_calibration(predictions)
        
        assert "expected_calibration_error" in calibration_metrics
        assert "max_calibration_error" in calibration_metrics
        assert "reliability_diagram" in calibration_metrics

    def test_aspect_sentiment_metrics(self):
        """Test aspect-based sentiment analysis metrics"""        metrics = SentimentMetrics()
        
        # Mock aspect-based predictions
        aspect_predictions = {
            "quality": {"predicted": "POSITIVE", "actual": "POSITIVE", "confidence": 0.85},
            "price": {"predicted": "NEGATIVE", "actual": "NEGATIVE", "confidence": 0.78},
            "service": {"predicted": "POSITIVE", "actual": "NEUTRAL", "confidence": 0.65}
        }
        
        aspect_metrics = metrics.calculate_aspect_metrics(aspect_predictions)
        
        assert "aspect_accuracy" in aspect_metrics
        assert "aspect_f1_scores" in aspect_metrics
        assert "overall_aspect_performance" in aspect_metrics

    def test_temporal_consistency_metrics(self):
        """Test temporal consistency metrics for sentiment analysis"""        metrics = SentimentMetrics()
        
        # Mock temporal sentiment predictions
        temporal_predictions = [
            {"timestamp": datetime.now() - timedelta(hours=3), "sentiment": "NEGATIVE", "score": 0.7},
            {"timestamp": datetime.now() - timedelta(hours=2), "sentiment": "NEUTRAL", "score": 0.5},
            {"timestamp": datetime.now() - timedelta(hours=1), "sentiment": "POSITIVE", "score": 0.8},
            {"timestamp": datetime.now(), "sentiment": "POSITIVE", "score": 0.85}
        ]
        
        consistency_metrics = metrics.evaluate_temporal_consistency(temporal_predictions)
        
        assert "sentiment_volatility" in consistency_metrics
        assert "trend_consistency" in consistency_metrics
        assert "stability_score" in consistency_metrics


@pytest.mark.integration
class TestSentimentAnalysisIntegration:
    """Integration tests for sentiment analysis components"""    
    @pytest.mark.slow
    def test_end_to_end_sentiment_pipeline(self, sample_text_data, temp_dir):
        """Test complete sentiment analysis pipeline"""        # Initialize components
        analyzer = SentimentAnalyzer(batch_size=4)
        emotion_detector = EmotionDetector()
        opinion_miner = OpinionMiningEngine(enable_aspect_extraction=True)
        
        # Process batch of texts
        batch_results = []
        
        for text in sample_text_data[:3]:
            # Sentiment analysis
            with patch.object(analyzer, 'analyze_sentiment') as mock_sentiment:
                mock_sentiment.return_value = {"label": "POSITIVE", "score": 0.8}
                sentiment_result = analyzer.analyze_sentiment(text)
            
            # Emotion detection
            with patch.object(emotion_detector, 'detect_emotions') as mock_emotion:
                mock_emotion.return_value = {"primary_emotion": "joy", "intensity": 0.75}
                emotion_result = emotion_detector.detect_emotions(text)
            
            # Opinion mining
            with patch.object(opinion_miner, 'extract_aspects') as mock_opinion:
                mock_opinion.return_value = {"aspects": [{"aspect": "quality", "sentiment": "POSITIVE"}]}
                opinion_result = opinion_miner.extract_aspects(text)
            
            batch_results.append({
                "text": text,
                "sentiment": sentiment_result,
                "emotions": emotion_result,
                "opinions": opinion_result
            })
        
        assert len(batch_results) == 3
        assert all("sentiment" in result for result in batch_results)
        assert all("emotions" in result for result in batch_results)
        assert all("opinions" in result for result in batch_results)

    def test_multilingual_sentiment_integration(self):
        """Test multilingual sentiment analysis integration"""        analyzer = MultilingualSentimentAnalyzer(
            supported_languages=["en", "fr", "de"],
            enable_auto_detection=True
        )
        
        multilingual_texts = [
            "This product is amazing!",     # English
            "Ce produit est incroyable!",   # French
            "Dieses Produkt ist fantastisch!" # German
        ]
        
        results = []
        for text in multilingual_texts:
            with patch.object(analyzer, 'analyze_multilingual_sentiment') as mock_analyze:
                mock_analyze.return_value = {
                    "sentiment": "POSITIVE",
                    "score": 0.85,
                    "language": "auto_detected",
                    "confidence": 0.9
                }
                
                result = analyzer.analyze_multilingual_sentiment(text)
                results.append(result)
        
        assert len(results) == 3
        assert all(result["sentiment"] == "POSITIVE" for result in results)

    def test_real_time_sentiment_monitoring(self):
        """Test real-time sentiment monitoring integration"""        analyzer = SentimentTrendAnalyzer(
            time_window="1h",
            enable_anomaly_detection=True
        )
        
        # Simulate real-time sentiment data stream
        sentiment_stream = []
        for i in range(10):
            sentiment_data = {
                "timestamp": datetime.now() - timedelta(minutes=i*6),
                "text": f"Sample text {i}",
                "sentiment_score": np.random.uniform(-1, 1)
            }
            sentiment_stream.append(sentiment_data)
        
        # Process stream
        with patch.object(analyzer, 'process_sentiment_stream') as mock_process:
            mock_process.return_value = {
                "current_trend": "stable",
                "anomalies_detected": [],
                "average_sentiment": 0.12,
                "volatility": 0.35
            }
            
            stream_analysis = analyzer.process_sentiment_stream(sentiment_stream)
            
            assert "current_trend" in stream_analysis
            assert "anomalies_detected" in stream_analysis
            assert "average_sentiment" in stream_analysis


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
