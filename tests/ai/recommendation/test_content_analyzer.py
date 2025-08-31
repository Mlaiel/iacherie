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
Comprehensive Tests for Content Analysis Components
Testing content analysis, feature extraction, and multi-modal processing

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
⚠️  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Email: mlaiel@live.de
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import numpy as np
from typing import Dict, List, Any
import json
from datetime import datetime, timedelta
import base64
from unittest.mock import Mock, patch

from ai.recommendation.content_analyzer import (
    ContentAnalyzer, VideoAnalyzer, AudioAnalyzer, TextAnalyzer,
    FeatureExtractor, MultiModalAnalyzer
)
from ai.recommendation.models import (
    ContentType, Platform, AnalysisResult, ContentFeatures,
    VideoFeatures, AudioFeatures, TextFeatures
)
from ai.recommendation.exceptions import ContentAnalysisError, ValidationError


class TestContentAnalyzer:
    """Comprehensive tests for the main content analyzer"""
    
    @pytest.mark.asyncio
    async def test_analyzer_initialization(self):
        """Test content analyzer initialization"""
        analyzer = ContentAnalyzer()
        
        # Test initial state
        assert analyzer.status.name == "INITIALIZING"
        
        # Test initialization
        success = await analyzer.initialize()
        assert success is True
        assert analyzer.status.name == "READY"
        
        # Test components are loaded
        assert analyzer.video_analyzer is not None
        assert analyzer.audio_analyzer is not None
        assert analyzer.text_analyzer is not None
        assert analyzer.feature_extractor is not None
    
    @pytest.mark.asyncio
    async def test_analyzer_initialization_failure(self):
        """Test analyzer initialization failure handling"""
        analyzer = ContentAnalyzer()
        
        # Mock a failure condition
        original_method = analyzer._load_analysis_models
        
        async def mock_failing_load():
            raise Exception("Model loading failed")
        
        analyzer._load_analysis_models = mock_failing_load
        
        with pytest.raises(ContentAnalysisError):
            await analyzer.initialize()
        
        assert analyzer.status.name == "ERROR"
        
        # Restore original method
        analyzer._load_analysis_models = original_method
    
    @pytest.mark.asyncio
    async def test_analyze_content_video(self, content_analyzer, sample_video_content):
        """Test video content analysis"""
        video_data = sample_video_content
        
        result = await content_analyzer.analyze_content(
            content_data=video_data,
            content_type=ContentType.VIDEO,
            platform=Platform.YOUTUBE
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.content_type == ContentType.VIDEO
        assert result.platform == Platform.YOUTUBE
        assert result.analysis_timestamp is not None
        
        # Test video-specific features
        assert result.video_features is not None
        assert result.video_features.duration > 0
        assert result.video_features.resolution is not None
        assert result.video_features.frame_rate > 0
        assert len(result.video_features.dominant_colors) > 0
        assert len(result.video_features.scene_transitions) >= 0
        
        # Test quality metrics
        assert 0 <= result.video_features.quality_score <= 1
        assert 0 <= result.video_features.engagement_indicators <= 1
    
    @pytest.mark.asyncio
    async def test_analyze_content_audio(self, content_analyzer, sample_audio_content):
        """Test audio content analysis"""
        audio_data = sample_audio_content
        
        result = await content_analyzer.analyze_content(
            content_data=audio_data,
            content_type=ContentType.AUDIO,
            platform=Platform.SPOTIFY
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.content_type == ContentType.AUDIO
        assert result.platform == Platform.SPOTIFY
        
        # Test audio-specific features
        assert result.audio_features is not None
        assert result.audio_features.duration > 0
        assert result.audio_features.sample_rate > 0
        assert result.audio_features.bit_rate > 0
        assert result.audio_features.tempo > 0
        assert result.audio_features.key is not None
        assert len(result.audio_features.genre_predictions) > 0
        
        # Test audio quality metrics
        assert 0 <= result.audio_features.audio_quality <= 1
        assert 0 <= result.audio_features.emotional_tone <= 1
    
    @pytest.mark.asyncio
    async def test_analyze_content_text(self, content_analyzer, sample_text_content):
        """Test text content analysis"""
        text_data = sample_text_content
        
        result = await content_analyzer.analyze_content(
            content_data=text_data,
            content_type=ContentType.TEXT,
            platform=Platform.TWITTER
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.content_type == ContentType.TEXT
        assert result.platform == Platform.TWITTER
        
        # Test text-specific features
        assert result.text_features is not None
        assert result.text_features.word_count > 0
        assert result.text_features.character_count > 0
        assert result.text_features.readability_score >= 0
        assert len(result.text_features.keywords) > 0
        assert len(result.text_features.entities) >= 0
        assert len(result.text_features.topics) > 0
        
        # Test sentiment analysis
        assert -1 <= result.text_features.sentiment_score <= 1
        assert result.text_features.sentiment_label in ['positive', 'negative', 'neutral']
    
    @pytest.mark.asyncio
    async def test_analyze_content_image(self, content_analyzer, sample_image_content):
        """Test image content analysis"""
        image_data = sample_image_content
        
        result = await content_analyzer.analyze_content(
            content_data=image_data,
            content_type=ContentType.IMAGE,
            platform=Platform.INSTAGRAM
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.content_type == ContentType.IMAGE
        assert result.platform == Platform.INSTAGRAM
        
        # Test image-specific features
        assert result.image_features is not None
        assert result.image_features.width > 0
        assert result.image_features.height > 0
        assert len(result.image_features.dominant_colors) > 0
        assert len(result.image_features.detected_objects) >= 0
        assert len(result.image_features.faces_detected) >= 0
        
        # Test aesthetic scores
        assert 0 <= result.image_features.aesthetic_score <= 1
        assert 0 <= result.image_features.composition_score <= 1
    
    @pytest.mark.asyncio
    async def test_batch_content_analysis(self, content_analyzer, sample_video_content, sample_audio_content, sample_text_content):
        """Test batch content analysis"""
        content_batch = [
            (sample_video_content, ContentType.VIDEO, Platform.YOUTUBE),
            (sample_audio_content, ContentType.AUDIO, Platform.SPOTIFY),
            (sample_text_content, ContentType.TEXT, Platform.TWITTER)
        ]
        
        results = await content_analyzer.analyze_batch(content_batch)
        
        assert len(results) == 3
        assert all(isinstance(result, AnalysisResult) for result in results)
        
        # Test each result
        video_result, audio_result, text_result = results
        
        assert video_result.content_type == ContentType.VIDEO
        assert audio_result.content_type == ContentType.AUDIO
        assert text_result.content_type == ContentType.TEXT
    
    @pytest.mark.asyncio
    async def test_content_similarity_analysis(self, content_analyzer, sample_video_content):
        """Test content similarity analysis"""
        video_data = sample_video_content
        
        # Analyze original content
        original_result = await content_analyzer.analyze_content(
            content_data=video_data,
            content_type=ContentType.VIDEO,
            platform=Platform.YOUTUBE
        )
        
        # Create slightly modified content
        modified_content = video_data.copy()
        modified_content['title'] = "Modified " + video_data['title']
        
        modified_result = await content_analyzer.analyze_content(
            content_data=modified_content,
            content_type=ContentType.VIDEO,
            platform=Platform.YOUTUBE
        )
        
        # Calculate similarity
        similarity_score = await content_analyzer.calculate_similarity(
            original_result, modified_result
        )
        
        assert 0 <= similarity_score <= 1
        assert similarity_score > 0.5  # Should be similar
    
    @pytest.mark.asyncio
    async def test_content_quality_assessment(self, content_analyzer, sample_video_content):
        """Test content quality assessment"""
        video_data = sample_video_content
        
        quality_assessment = await content_analyzer.assess_quality(
            content_data=video_data,
            content_type=ContentType.VIDEO,
            platform=Platform.YOUTUBE
        )
        
        assert 'overall_quality' in quality_assessment
        assert 'technical_quality' in quality_assessment
        assert 'content_quality' in quality_assessment
        assert 'engagement_potential' in quality_assessment
        
        # Test scores are valid
        for score in quality_assessment.values():
            assert 0 <= score <= 1


class TestVideoAnalyzer:
    """Tests for video content analysis"""
    
    @pytest.mark.asyncio
    async def test_video_feature_extraction(self, video_analyzer, sample_video_content):
        """Test video feature extraction"""
        video_data = sample_video_content
        
        features = await video_analyzer.extract_features(video_data)
        
        assert isinstance(features, VideoFeatures)
        assert features.duration > 0
        assert features.resolution is not None
        assert features.frame_rate > 0
        assert len(features.dominant_colors) > 0
        
        # Test advanced features
        assert features.motion_intensity >= 0
        assert features.scene_complexity >= 0
        assert len(features.visual_elements) >= 0
    
    @pytest.mark.asyncio
    async def test_video_object_detection(self, video_analyzer, sample_video_content):
        """Test video object detection"""
        video_data = sample_video_content
        
        objects = await video_analyzer.detect_objects(video_data)
        
        assert isinstance(objects, list)
        
        for obj in objects:
            assert 'class' in obj
            assert 'confidence' in obj
            assert 'bounding_box' in obj
            assert 0 <= obj['confidence'] <= 1
    
    @pytest.mark.asyncio
    async def test_video_scene_analysis(self, video_analyzer, sample_video_content):
        """Test video scene analysis"""
        video_data = sample_video_content
        
        scenes = await video_analyzer.analyze_scenes(video_data)
        
        assert isinstance(scenes, list)
        assert len(scenes) > 0
        
        for scene in scenes:
            assert 'start_time' in scene
            assert 'end_time' in scene
            assert 'scene_type' in scene
            assert 'dominant_action' in scene
            assert scene['start_time'] < scene['end_time']
    
    @pytest.mark.asyncio
    async def test_video_quality_metrics(self, video_analyzer, sample_video_content):
        """Test video quality metrics calculation"""
        video_data = sample_video_content
        
        quality_metrics = await video_analyzer.calculate_quality_metrics(video_data)
        
        assert 'sharpness' in quality_metrics
        assert 'brightness' in quality_metrics
        assert 'contrast' in quality_metrics
        assert 'color_balance' in quality_metrics
        assert 'noise_level' in quality_metrics
        
        # Test all metrics are valid
        for metric, value in quality_metrics.items():
            assert 0 <= value <= 1
    
    @pytest.mark.asyncio
    async def test_video_engagement_indicators(self, video_analyzer, sample_video_content):
        """Test video engagement indicators analysis"""
        video_data = sample_video_content
        
        engagement_indicators = await video_analyzer.analyze_engagement_indicators(video_data)
        
        assert 'hook_strength' in engagement_indicators
        assert 'pacing_score' in engagement_indicators
        assert 'visual_interest' in engagement_indicators
        assert 'call_to_action_strength' in engagement_indicators
        
        # Test indicator values
        for indicator, value in engagement_indicators.items():
            assert 0 <= value <= 1


class TestAudioAnalyzer:
    """Tests for audio content analysis"""
    
    @pytest.mark.asyncio
    async def test_audio_feature_extraction(self, audio_analyzer, sample_audio_content):
        """Test audio feature extraction"""
        audio_data = sample_audio_content
        
        features = await audio_analyzer.extract_features(audio_data)
        
        assert isinstance(features, AudioFeatures)
        assert features.duration > 0
        assert features.sample_rate > 0
        assert features.bit_rate > 0
        assert features.tempo > 0
        assert features.key is not None
        
        # Test spectral features
        assert len(features.mfcc_features) > 0
        assert len(features.spectral_centroid) > 0
        assert len(features.spectral_rolloff) > 0
    
    @pytest.mark.asyncio
    async def test_audio_genre_classification(self, audio_analyzer, sample_audio_content):
        """Test audio genre classification"""
        audio_data = sample_audio_content
        
        genre_predictions = await audio_analyzer.classify_genre(audio_data)
        
        assert isinstance(genre_predictions, dict)
        assert len(genre_predictions) > 0
        
        # Test predictions format
        for genre, confidence in genre_predictions.items():
            assert isinstance(genre, str)
            assert 0 <= confidence <= 1
        
        # Test top genre
        top_genre = max(genre_predictions, key=genre_predictions.get)
        assert genre_predictions[top_genre] > 0.1  # Should have some confidence
    
    @pytest.mark.asyncio
    async def test_audio_mood_analysis(self, audio_analyzer, sample_audio_content):
        """Test audio mood analysis"""
        audio_data = sample_audio_content
        
        mood_analysis = await audio_analyzer.analyze_mood(audio_data)
        
        assert 'valence' in mood_analysis  # Positive vs negative
        assert 'arousal' in mood_analysis  # Energy level
        assert 'dominance' in mood_analysis  # Dominance/submission
        
        # Test mood values
        for dimension, value in mood_analysis.items():
            assert -1 <= value <= 1
    
    @pytest.mark.asyncio
    async def test_audio_quality_assessment(self, audio_analyzer, sample_audio_content):
        """Test audio quality assessment"""
        audio_data = sample_audio_content
        
        quality_metrics = await audio_analyzer.assess_quality(audio_data)
        
        assert 'signal_to_noise_ratio' in quality_metrics
        assert 'dynamic_range' in quality_metrics
        assert 'frequency_balance' in quality_metrics
        assert 'distortion_level' in quality_metrics
        
        # Test quality scores
        for metric, value in quality_metrics.items():
            assert 0 <= value <= 1
    
    @pytest.mark.asyncio
    async def test_audio_beat_detection(self, audio_analyzer, sample_audio_content):
        """Test audio beat detection and rhythm analysis"""
        audio_data = sample_audio_content
        
        rhythm_analysis = await audio_analyzer.analyze_rhythm(audio_data)
        
        assert 'tempo' in rhythm_analysis
        assert 'beat_times' in rhythm_analysis
        assert 'time_signature' in rhythm_analysis
        assert 'rhythm_strength' in rhythm_analysis
        
        # Test tempo is reasonable
        assert 60 <= rhythm_analysis['tempo'] <= 200  # Typical music tempo range
        
        # Test beat times
        beat_times = rhythm_analysis['beat_times']
        assert isinstance(beat_times, list)
        assert len(beat_times) > 0
        
        # Test rhythm strength
        assert 0 <= rhythm_analysis['rhythm_strength'] <= 1


class TestTextAnalyzer:
    """Tests for text content analysis"""
    
    @pytest.mark.asyncio
    async def test_text_feature_extraction(self, text_analyzer, sample_text_content):
        """Test text feature extraction"""
        text_data = sample_text_content
        
        features = await text_analyzer.extract_features(text_data)
        
        assert isinstance(features, TextFeatures)
        assert features.word_count > 0
        assert features.character_count > 0
        assert features.sentence_count > 0
        assert features.readability_score >= 0
        assert len(features.keywords) > 0
    
    @pytest.mark.asyncio
    async def test_text_sentiment_analysis(self, text_analyzer, sample_text_content):
        """Test text sentiment analysis"""
        text_data = sample_text_content
        
        sentiment = await text_analyzer.analyze_sentiment(text_data)
        
        assert 'score' in sentiment
        assert 'label' in sentiment
        assert 'confidence' in sentiment
        
        # Test sentiment values
        assert -1 <= sentiment['score'] <= 1
        assert sentiment['label'] in ['positive', 'negative', 'neutral']
        assert 0 <= sentiment['confidence'] <= 1
    
    @pytest.mark.asyncio
    async def test_text_entity_extraction(self, text_analyzer, sample_text_content):
        """Test named entity extraction"""
        text_data = sample_text_content
        
        entities = await text_analyzer.extract_entities(text_data)
        
        assert isinstance(entities, list)
        
        for entity in entities:
            assert 'text' in entity
            assert 'label' in entity
            assert 'start' in entity
            assert 'end' in entity
            assert 'confidence' in entity
            
            # Test entity positions
            assert 0 <= entity['start'] < entity['end']
            assert 0 <= entity['confidence'] <= 1
    
    @pytest.mark.asyncio
    async def test_text_topic_modeling(self, text_analyzer, sample_text_content):
        """Test topic modeling and classification"""
        text_data = sample_text_content
        
        topics = await text_analyzer.extract_topics(text_data)
        
        assert isinstance(topics, list)
        assert len(topics) > 0
        
        for topic in topics:
            assert 'topic_id' in topic
            assert 'keywords' in topic
            assert 'weight' in topic
            
            # Test topic weights
            assert 0 <= topic['weight'] <= 1
            assert len(topic['keywords']) > 0
    
    @pytest.mark.asyncio
    async def test_text_readability_analysis(self, text_analyzer, sample_text_content):
        """Test text readability analysis"""
        text_data = sample_text_content
        
        readability = await text_analyzer.analyze_readability(text_data)
        
        assert 'flesch_kincaid_grade' in readability
        assert 'flesch_reading_ease' in readability
        assert 'gunning_fog_index' in readability
        assert 'automated_readability_index' in readability
        
        # Test readability scores are reasonable
        for metric, score in readability.items():
            assert score >= 0
    
    @pytest.mark.asyncio
    async def test_text_hashtag_extraction(self, text_analyzer, sample_text_content):
        """Test hashtag and mention extraction"""
        text_with_hashtags = sample_text_content.copy()
        text_with_hashtags['content'] += " #music #AI #technology @influencer"
        
        hashtags = await text_analyzer.extract_hashtags(text_with_hashtags)
        mentions = await text_analyzer.extract_mentions(text_with_hashtags)
        
        assert isinstance(hashtags, list)
        assert isinstance(mentions, list)
        
        # Test hashtag extraction
        expected_hashtags = ['#music', '#AI', '#technology']
        for hashtag in expected_hashtags:
            assert hashtag in hashtags
        
        # Test mention extraction
        assert '@influencer' in mentions


class TestFeatureExtractor:
    """Tests for feature extraction utilities"""
    
    @pytest.mark.asyncio
    async def test_multimodal_feature_extraction(self, feature_extractor, sample_video_content):
        """Test multimodal feature extraction"""
        video_data = sample_video_content
        
        features = await feature_extractor.extract_multimodal_features(
            content_data=video_data,
            content_type=ContentType.VIDEO
        )
        
        assert isinstance(features, ContentFeatures)
        assert features.video_features is not None
        assert features.audio_features is not None  # Video has audio
        assert features.text_features is not None   # Video has title/description
        
        # Test combined features
        assert features.combined_embedding is not None
        assert len(features.combined_embedding) > 0
    
    @pytest.mark.asyncio
    async def test_feature_normalization(self, feature_extractor, sample_audio_content):
        """Test feature normalization"""
        audio_data = sample_audio_content
        
        raw_features = await feature_extractor.extract_raw_features(
            audio_data, ContentType.AUDIO
        )
        
        normalized_features = await feature_extractor.normalize_features(raw_features)
        
        # Test normalization
        assert len(normalized_features) == len(raw_features)
        
        # Test values are normalized (mean close to 0, std close to 1)
        mean_val = np.mean(normalized_features)
        std_val = np.std(normalized_features)
        
        assert abs(mean_val) < 0.5  # Mean should be close to 0
        assert 0.5 < std_val < 2.0  # Std should be close to 1
    
    @pytest.mark.asyncio
    async def test_feature_embedding_generation(self, feature_extractor, sample_text_content):
        """Test feature embedding generation"""
        text_data = sample_text_content
        
        embeddings = await feature_extractor.generate_embeddings(
            content_data=text_data,
            content_type=ContentType.TEXT
        )
        
        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings.shape) == 1  # 1D embedding vector
        assert embeddings.shape[0] > 0     # Non-empty embedding
        
        # Test embedding values are reasonable
        assert not np.any(np.isnan(embeddings))  # No NaN values
        assert not np.any(np.isinf(embeddings))  # No infinite values
    
    @pytest.mark.asyncio
    async def test_feature_similarity_calculation(self, feature_extractor, sample_audio_content):
        """Test feature similarity calculation"""
        audio_data = sample_audio_content
        
        # Extract features for same content
        features1 = await feature_extractor.extract_multimodal_features(
            audio_data, ContentType.AUDIO
        )
        
        features2 = await feature_extractor.extract_multimodal_features(
            audio_data, ContentType.AUDIO
        )
        
        # Calculate similarity
        similarity = await feature_extractor.calculate_similarity(features1, features2)
        
        assert 0 <= similarity <= 1
        assert similarity > 0.9  # Same content should be very similar


class TestMultiModalAnalyzer:
    """Tests for multimodal content analysis"""
    
    @pytest.mark.asyncio
    async def test_multimodal_content_analysis(self, multimodal_analyzer, sample_video_content):
        """Test multimodal content analysis"""
        video_data = sample_video_content
        
        analysis_result = await multimodal_analyzer.analyze_multimodal_content(video_data)
        
        assert 'video_analysis' in analysis_result
        assert 'audio_analysis' in analysis_result
        assert 'text_analysis' in analysis_result
        assert 'combined_analysis' in analysis_result
        
        # Test combined analysis
        combined = analysis_result['combined_analysis']
        assert 'overall_quality' in combined
        assert 'engagement_potential' in combined
        assert 'content_coherence' in combined
    
    @pytest.mark.asyncio
    async def test_cross_modal_consistency(self, multimodal_analyzer, sample_video_content):
        """Test cross-modal consistency analysis"""
        video_data = sample_video_content
        
        consistency_score = await multimodal_analyzer.analyze_cross_modal_consistency(video_data)
        
        assert 0 <= consistency_score <= 1
        
        # High consistency means visual, audio, and text elements align well
        if consistency_score > 0.8:
            # Should have good alignment between modalities
            analysis = await multimodal_analyzer.analyze_multimodal_content(video_data)
            
            video_mood = analysis['video_analysis'].get('mood', 'neutral')
            audio_mood = analysis['audio_analysis'].get('mood', 'neutral')
            text_sentiment = analysis['text_analysis'].get('sentiment', 'neutral')
            
            # Moods should be reasonably aligned for high consistency
            assert video_mood == audio_mood or video_mood == text_sentiment or audio_mood == text_sentiment
    
    @pytest.mark.asyncio
    async def test_multimodal_feature_fusion(self, multimodal_analyzer, sample_video_content):
        """Test multimodal feature fusion"""
        video_data = sample_video_content
        
        fused_features = await multimodal_analyzer.fuse_multimodal_features(video_data)
        
        assert isinstance(fused_features, np.ndarray)
        assert len(fused_features.shape) == 1  # 1D feature vector
        assert fused_features.shape[0] > 0     # Non-empty
        
        # Test feature fusion combines different modalities
        video_features = await multimodal_analyzer.extract_video_features(video_data)
        audio_features = await multimodal_analyzer.extract_audio_features(video_data)
        text_features = await multimodal_analyzer.extract_text_features(video_data)
        
        # Fused features should be different from individual modality features
        video_similarity = np.corrcoef(fused_features, video_features)[0, 1]
        audio_similarity = np.corrcoef(fused_features, audio_features)[0, 1]
        text_similarity = np.corrcoef(fused_features, text_features)[0, 1]
        
        # Should not be perfectly correlated with any single modality
        assert video_similarity < 0.95
        assert audio_similarity < 0.95
        assert text_similarity < 0.95


class TestContentAnalysisPerformance:
    """Performance tests for content analysis"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_content_analysis_performance(self, benchmark, content_analyzer, sample_video_content):
        """Benchmark content analysis performance"""
        video_data = sample_video_content
        
        async def analyze_content():
            return await content_analyzer.analyze_content(
                content_data=video_data,
                content_type=ContentType.VIDEO,
                platform=Platform.YOUTUBE
            )
        
        result = await benchmark(analyze_content)
        assert isinstance(result, AnalysisResult)
    
    @pytest.mark.asyncio
    async def test_parallel_content_analysis(self, content_analyzer, sample_video_content, sample_audio_content, sample_text_content):
        """Test parallel content analysis performance"""
        content_items = [
            (sample_video_content, ContentType.VIDEO, Platform.YOUTUBE),
            (sample_audio_content, ContentType.AUDIO, Platform.SPOTIFY),
            (sample_text_content, ContentType.TEXT, Platform.TWITTER)
        ] * 3  # 9 items total
        
        start_time = datetime.now()
        
        # Analyze in parallel
        results = await content_analyzer.analyze_batch(content_items)
        
        analysis_time = (datetime.now() - start_time).total_seconds()
        
        # Test results
        assert len(results) == 9
        assert all(isinstance(result, AnalysisResult) for result in results)
        
        # Test performance (should be better than sequential)
        assert analysis_time < 30.0  # Should complete within 30 seconds
    
    @pytest.mark.asyncio
    async def test_memory_usage_during_analysis(self, content_analyzer, sample_video_content):
        """Test memory usage during content analysis"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform multiple analyses
        for _ in range(5):
            await content_analyzer.analyze_content(
                content_data=sample_video_content,
                content_type=ContentType.VIDEO,
                platform=Platform.YOUTUBE
            )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for 5 analyses)
        assert memory_increase < 100


class TestContentAnalysisErrorHandling:
    """Tests for content analysis error handling"""
    
    @pytest.mark.asyncio
    async def test_invalid_content_type_handling(self, content_analyzer):
        """Test handling of invalid content types"""
        invalid_content = {"invalid": "data"}
        
        with pytest.raises(ValidationError):
            await content_analyzer.analyze_content(
                content_data=invalid_content,
                content_type="INVALID_TYPE",  # Invalid content type
                platform=Platform.YOUTUBE
            )
    
    @pytest.mark.asyncio
    async def test_corrupted_content_handling(self, content_analyzer):
        """Test handling of corrupted content data"""
        corrupted_video = {
            "title": "Test Video",
            "video_data": "corrupted_binary_data",
            "format": "mp4"
        }
        
        with pytest.raises(ContentAnalysisError):
            await content_analyzer.analyze_content(
                content_data=corrupted_video,
                content_type=ContentType.VIDEO,
                platform=Platform.YOUTUBE
            )
    
    @pytest.mark.asyncio
    async def test_empty_content_handling(self, content_analyzer):
        """Test handling of empty content"""
        empty_text = {"content": ""}
        
        with pytest.raises(ValidationError):
            await content_analyzer.analyze_content(
                content_data=empty_text,
                content_type=ContentType.TEXT,
                platform=Platform.TWITTER
            )
    
    @pytest.mark.asyncio
    async def test_large_content_handling(self, content_analyzer):
        """Test handling of very large content"""
        # Create a very large text content
        large_text = {
            "content": "Large content " * 100000,  # Very large text
            "title": "Large Content Test"
        }
        
        # Should handle large content gracefully
        result = await content_analyzer.analyze_content(
            content_data=large_text,
            content_type=ContentType.TEXT,
            platform=Platform.TWITTER
        )
        
        assert isinstance(result, AnalysisResult)
        # Should truncate or sample large content appropriately
        assert result.text_features.word_count > 0
    
    @pytest.mark.asyncio
    async def test_analysis_timeout_handling(self, content_analyzer, sample_video_content):
        """Test analysis timeout handling"""
        video_data = sample_video_content
        
        try:
            # Set short timeout to test timeout handling
            result = await asyncio.wait_for(
                content_analyzer.analyze_content(
                    content_data=video_data,
                    content_type=ContentType.VIDEO,
                    platform=Platform.YOUTUBE
                ),
                timeout=30.0  # 30 second timeout
            )
            
            # Should complete within timeout
            assert isinstance(result, AnalysisResult)
            
        except asyncio.TimeoutError:
            pytest.fail("Content analysis timed out")
