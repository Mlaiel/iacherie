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

"""Comprehensive Tests for Trend Analysis System
Testing trend detection, analysis, and prediction algorithms

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
⚠️  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Email: mlaiel@live.de
"""import pytest
import sys
import os
from pathlib import Path
import asyncio
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json

from ai.recommendation.trend_analyzer import (
    TrendAnalyzer, TrendDetector, TrendPredictor, ViralPredictor
)
from ai.recommendation.models import (
    TrendInsight, Platform, ContentType, TrendType, ViralPrediction
)
from ai.recommendation.exceptions import TrendAnalysisError, ValidationError


class TestTrendAnalyzer:
    """Comprehensive tests for the main trend analyzer"""    
    @pytest.mark.asyncio
    async def test_analyzer_initialization(self):
        """Test trend analyzer initialization"""        analyzer = TrendAnalyzer()
        
        # Test initial state
        assert analyzer.status.name == "INITIALIZING"
        
        # Test initialization
        success = await analyzer.initialize()
        assert success is True
        assert analyzer.status.name == "READY"
        
        # Test components are loaded
        assert analyzer.trend_detector is not None
        assert analyzer.trend_predictor is not None
        assert analyzer.viral_predictor is not None
    
    @pytest.mark.asyncio
    async def test_analyze_current_trends(self, trend_analyzer):
        """Test current trend analysis"""        trends = await trend_analyzer.analyze_current_trends(
            platforms=[Platform.YOUTUBE, Platform.TIKTOK],
            limit=10
        )
        
        assert len(trends) <= 10
        assert all(isinstance(trend, TrendInsight) for trend in trends)
        
        # Test trend validity
        for trend in trends:
            assert trend.trend_id
            assert trend.trend_type in TrendType
            assert trend.platform in [Platform.YOUTUBE, Platform.TIKTOK]
            assert 0 <= trend.trend_strength <= 1
            assert 0 <= trend.growth_rate
            assert trend.keywords
            assert trend.hashtags
    
    @pytest.mark.asyncio
    async def test_analyze_platform_specific_trends(self, trend_analyzer):
        """Test platform-specific trend analysis"""        # Test YouTube trends
        youtube_trends = await trend_analyzer.analyze_platform_trends(
            platform=Platform.YOUTUBE,
            content_type=ContentType.VIDEO,
            limit=5
        )
        
        assert all(trend.platform == Platform.YOUTUBE for trend in youtube_trends)
        assert all(ContentType.VIDEO in trend.content_types for trend in youtube_trends)
        
        # Test TikTok trends
        tiktok_trends = await trend_analyzer.analyze_platform_trends(
            platform=Platform.TIKTOK,
            content_type=ContentType.VIDEO,
            limit=5
        )
        
        assert all(trend.platform == Platform.TIKTOK for trend in tiktok_trends)
        
        # Different platforms should have different trending content
        youtube_keywords = set()
        tiktok_keywords = set()
        
        for trend in youtube_trends:
            youtube_keywords.update(trend.keywords)
        
        for trend in tiktok_trends:
            tiktok_keywords.update(trend.keywords)
        
        # Should have some platform-specific keywords
        assert len(youtube_keywords - tiktok_keywords) > 0
        assert len(tiktok_keywords - youtube_keywords) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_trending_hashtags(self, trend_analyzer):
        """Test trending hashtag analysis"""        hashtags = await trend_analyzer.analyze_trending_hashtags(
            platforms=[Platform.INSTAGRAM, Platform.TIKTOK],
            time_period=timedelta(days=7),
            limit=20
        )
        
        assert len(hashtags) <= 20
        
        for hashtag_data in hashtags:
            assert 'hashtag' in hashtag_data
            assert 'usage_count' in hashtag_data
            assert 'growth_rate' in hashtag_data
            assert 'platforms' in hashtag_data
            assert 'related_hashtags' in hashtag_data
            
            # Test hashtag format
            assert hashtag_data['hashtag'].startswith('#')
            assert hashtag_data['usage_count'] > 0
            assert hashtag_data['growth_rate'] >= 0
    
    @pytest.mark.asyncio
    async def test_analyze_trending_keywords(self, trend_analyzer):
        """Test trending keyword analysis"""        keywords = await trend_analyzer.analyze_trending_keywords(
            platforms=[Platform.YOUTUBE, Platform.TWITTER],
            category="Technology",
            limit=15
        )
        
        assert len(keywords) <= 15
        
        for keyword_data in keywords:
            assert 'keyword' in keyword_data
            assert 'search_volume' in keyword_data
            assert 'trend_direction' in keyword_data
            assert 'competition_level' in keyword_data
            assert 'related_keywords' in keyword_data
            
            # Test keyword validity
            assert len(keyword_data['keyword']) > 0
            assert keyword_data['search_volume'] >= 0
            assert keyword_data['trend_direction'] in ['rising', 'stable', 'declining']
            assert 0 <= keyword_data['competition_level'] <= 1
    
    @pytest.mark.asyncio
    async def test_predict_emerging_trends(self, trend_analyzer):
        """Test emerging trend prediction"""        emerging_trends = await trend_analyzer.predict_emerging_trends(
            platforms=[Platform.TIKTOK, Platform.INSTAGRAM],
            prediction_horizon=timedelta(days=30),
            limit=5
        )
        
        assert len(emerging_trends) <= 5
        
        for trend in emerging_trends:
            assert isinstance(trend, TrendInsight)
            assert trend.trend_type == TrendType.EMERGING
            assert 0 <= trend.emergence_probability <= 1
            assert trend.predicted_peak_time is not None
            assert trend.predicted_peak_time > datetime.now()
    
    @pytest.mark.asyncio
    async def test_analyze_seasonal_trends(self, trend_analyzer):
        """Test seasonal trend analysis"""        # Test summer trends
        summer_trends = await trend_analyzer.analyze_seasonal_trends(
            season="summer",
            platforms=[Platform.YOUTUBE, Platform.INSTAGRAM],
            limit=5
        )
        
        # Test holiday trends
        holiday_trends = await trend_analyzer.analyze_seasonal_trends(
            season="holiday",
            platforms=[Platform.YOUTUBE, Platform.INSTAGRAM],
            limit=5
        )
        
        assert len(summer_trends) > 0
        assert len(holiday_trends) > 0
        
        # Summer trends should include summer-related keywords
        summer_keywords = set()
        for trend in summer_trends:
            summer_keywords.update(trend.keywords)
        
        summer_related = any(keyword in summer_keywords 
                           for keyword in ['summer', 'beach', 'vacation', 'sun', 'travel'])
        
        # Holiday trends should include holiday-related keywords
        holiday_keywords = set()
        for trend in holiday_trends:
            holiday_keywords.update(trend.keywords)
        
        holiday_related = any(keyword in holiday_keywords 
                            for keyword in ['holiday', 'christmas', 'gift', 'family', 'celebration'])
        
        assert summer_related or len(summer_trends) > 0
        assert holiday_related or len(holiday_trends) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_trend_lifecycle(self, trend_analyzer):
        """Test trend lifecycle analysis"""        trend_lifecycles = await trend_analyzer.analyze_trend_lifecycle(
            trend_keywords=["AI", "sustainable fashion", "cryptocurrency"],
            platforms=[Platform.YOUTUBE, Platform.TWITTER],
            time_range=timedelta(days=180)
        )
        
        assert len(trend_lifecycles) == 3  # One for each keyword
        
        for lifecycle in trend_lifecycles:
            assert 'keyword' in lifecycle
            assert 'lifecycle_stage' in lifecycle
            assert 'peak_date' in lifecycle
            assert 'growth_phase_duration' in lifecycle
            assert 'decline_phase_duration' in lifecycle
            assert 'lifecycle_stages' in lifecycle
            
            # Test lifecycle stages
            stages = lifecycle['lifecycle_stages']
            assert 'emergence' in stages
            assert 'growth' in stages
            assert 'peak' in stages
            assert 'decline' in stages
    
    @pytest.mark.asyncio
    async def test_get_trend_recommendations(self, trend_analyzer, sample_creator_musician):
        """Test trend-based content recommendations"""        creator = sample_creator_musician
        
        recommendations = await trend_analyzer.get_trend_recommendations(
            creator_profile=creator,
            platforms=creator.platforms,
            limit=5
        )
        
        assert len(recommendations) <= 5
        
        for rec in recommendations:
            assert 'trend' in rec
            assert 'content_suggestion' in rec
            assert 'relevance_score' in rec
            assert 'timing_recommendation' in rec
            assert 'hashtag_suggestions' in rec
            
            # Test relevance to creator
            assert 0 <= rec['relevance_score'] <= 1
            
            # Should suggest appropriate timing
            timing = rec['timing_recommendation']
            assert 'optimal_posting_time' in timing
            assert 'posting_frequency' in timing


class TestTrendDetector:
    """Tests for trend detection algorithms"""    
    @pytest.mark.asyncio
    async def test_detect_viral_content(self, trend_detector):
        """Test viral content detection"""        viral_content = await trend_detector.detect_viral_content(
            platforms=[Platform.TIKTOK, Platform.YOUTUBE],
            time_period=timedelta(hours=24),
            limit=10
        )
        
        assert len(viral_content) <= 10
        
        for content in viral_content:
            assert 'content_id' in content
            assert 'platform' in content
            assert 'viral_score' in content
            assert 'growth_velocity' in content
            assert 'engagement_metrics' in content
            
            # Test viral metrics
            assert 0 <= content['viral_score'] <= 1
            assert content['growth_velocity'] > 0  # Should be growing
            
            # High viral score should correlate with high engagement
            if content['viral_score'] > 0.8:
                metrics = content['engagement_metrics']
                assert metrics.get('likes', 0) > 100 or metrics.get('shares', 0) > 50
    
    @pytest.mark.asyncio
    async def test_detect_rising_trends(self, trend_detector):
        """Test rising trend detection"""        rising_trends = await trend_detector.detect_rising_trends(
            platforms=[Platform.YOUTUBE, Platform.INSTAGRAM],
            detection_window=timedelta(days=3),
            min_growth_rate=1.5,  # 150% growth
            limit=5
        )
        
        assert len(rising_trends) <= 5
        
        for trend in rising_trends:
            assert isinstance(trend, TrendInsight)
            assert trend.trend_type == TrendType.RISING
            assert trend.growth_rate >= 1.5
            assert trend.detection_confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_detect_breakout_creators(self, trend_detector):
        """Test breakout creator detection"""        breakout_creators = await trend_detector.detect_breakout_creators(
            platforms=[Platform.TIKTOK, Platform.YOUTUBE],
            time_period=timedelta(days=30),
            min_follower_growth=10000,
            limit=10
        )
        
        assert len(breakout_creators) <= 10
        
        for creator_data in breakout_creators:
            assert 'creator_id' in creator_data
            assert 'platform' in creator_data
            assert 'follower_growth' in creator_data
            assert 'growth_rate' in creator_data
            assert 'breakout_content' in creator_data
            
            # Test growth metrics
            assert creator_data['follower_growth'] >= 10000
            assert creator_data['growth_rate'] > 1.0  # More than 100% growth
    
    @pytest.mark.asyncio
    async def test_detect_content_patterns(self, trend_detector):
        """Test content pattern detection"""        patterns = await trend_detector.detect_content_patterns(
            platform=Platform.TIKTOK,
            content_type=ContentType.VIDEO,
            time_period=timedelta(days=14),
            min_pattern_frequency=0.1  # 10% of content
        )
        
        assert len(patterns) > 0
        
        for pattern in patterns:
            assert 'pattern_type' in pattern
            assert 'frequency' in pattern
            assert 'characteristics' in pattern
            assert 'success_rate' in pattern
            assert 'examples' in pattern
            
            # Test pattern validity
            assert pattern['frequency'] >= 0.1
            assert 0 <= pattern['success_rate'] <= 1
            assert len(pattern['examples']) > 0
    
    @pytest.mark.asyncio
    async def test_detect_trend_signals(self, trend_detector):
        """Test trend signal detection"""        signals = await trend_detector.detect_trend_signals(
            platforms=[Platform.TWITTER, Platform.REDDIT],
            signal_types=["hashtag_surge", "keyword_spike", "engagement_anomaly"],
            sensitivity=0.7
        )
        
        assert len(signals) > 0
        
        for signal in signals:
            assert 'signal_type' in signal
            assert 'strength' in signal
            assert 'timestamp' in signal
            assert 'source_platform' in signal
            assert 'data' in signal
            
            # Test signal validity
            assert signal['signal_type'] in ["hashtag_surge", "keyword_spike", "engagement_anomaly"]
            assert 0 <= signal['strength'] <= 1
            assert signal['strength'] >= 0.7  # Above sensitivity threshold


class TestTrendPredictor:
    """Tests for trend prediction algorithms"""    
    @pytest.mark.asyncio
    async def test_predict_trend_evolution(self, trend_predictor):
        """Test trend evolution prediction"""        predictions = await trend_predictor.predict_trend_evolution(
            trend_keywords=["AI art", "sustainable living"],
            prediction_horizon=timedelta(days=60),
            platforms=[Platform.YOUTUBE, Platform.INSTAGRAM]
        )
        
        assert len(predictions) == 2  # One for each keyword
        
        for prediction in predictions:
            assert 'keyword' in prediction
            assert 'predicted_trajectory' in prediction
            assert 'peak_prediction' in prediction
            assert 'confidence_interval' in prediction
            assert 'influencing_factors' in prediction
            
            # Test prediction structure
            trajectory = prediction['predicted_trajectory']
            assert len(trajectory) > 0
            
            for point in trajectory:
                assert 'date' in point
                assert 'predicted_volume' in point
                assert 'confidence' in point
    
    @pytest.mark.asyncio
    async def test_predict_seasonal_peaks(self, trend_predictor):
        """Test seasonal peak prediction"""        seasonal_predictions = await trend_predictor.predict_seasonal_peaks(
            categories=["Fashion", "Travel", "Food"],
            year=2025,
            platforms=[Platform.INSTAGRAM, Platform.PINTEREST]
        )
        
        assert len(seasonal_predictions) == 3  # One for each category
        
        for prediction in seasonal_predictions:
            assert 'category' in prediction
            assert 'predicted_peaks' in prediction
            assert 'seasonal_patterns' in prediction
            
            peaks = prediction['predicted_peaks']
            for peak in peaks:
                assert 'month' in peak
                assert 'peak_strength' in peak
                assert 'trending_subtopics' in peak
                assert 1 <= peak['month'] <= 12
                assert 0 <= peak['peak_strength'] <= 1
    
    @pytest.mark.asyncio
    async def test_predict_cross_platform_spread(self, trend_predictor):
        """Test cross-platform trend spread prediction"""        spread_predictions = await trend_predictor.predict_cross_platform_spread(
            origin_platform=Platform.TIKTOK,
            trend_keywords=["dance challenge", "cooking hack"],
            target_platforms=[Platform.INSTAGRAM, Platform.YOUTUBE, Platform.TWITTER]
        )
        
        assert len(spread_predictions) > 0
        
        for prediction in spread_predictions:
            assert 'trend_keyword' in prediction
            assert 'origin_platform' in prediction
            assert 'spread_timeline' in prediction
            
            timeline = prediction['spread_timeline']
            for platform_prediction in timeline:
                assert 'platform' in platform_prediction
                assert 'predicted_arrival_date' in platform_prediction
                assert 'adaptation_probability' in platform_prediction
                assert 'expected_modifications' in platform_prediction
    
    @pytest.mark.asyncio
    async def test_predict_trend_longevity(self, trend_predictor):
        """Test trend longevity prediction"""        longevity_predictions = await trend_predictor.predict_trend_longevity(
            trends=["minimalist lifestyle", "retro gaming", "plant-based diet"],
            platforms=[Platform.YOUTUBE, Platform.INSTAGRAM]
        )
        
        assert len(longevity_predictions) == 3
        
        for prediction in longevity_predictions:
            assert 'trend' in prediction
            assert 'predicted_lifespan' in prediction
            assert 'decay_rate' in prediction
            assert 'sustainability_factors' in prediction
            
            # Test prediction validity
            lifespan = prediction['predicted_lifespan']
            assert lifespan > 0  # Should predict positive lifespan
            
            decay_rate = prediction['decay_rate']
            assert 0 <= decay_rate <= 1


class TestViralPredictor:
    """Tests for viral prediction algorithms"""    
    @pytest.mark.asyncio
    async def test_predict_viral_potential(self, viral_predictor, sample_video_content):
        """Test viral potential prediction"""        video_data = sample_video_content
        
        prediction = await viral_predictor.predict_viral_potential(
            content_data=video_data,
            platform=Platform.TIKTOK
        )
        
        assert isinstance(prediction, ViralPrediction)
        assert 0 <= prediction.viral_score <= 1
        assert 0 <= prediction.reach_prediction
        assert 0 <= prediction.engagement_prediction
        assert prediction.optimal_posting_time is not None
        assert len(prediction.viral_factors) > 0
    
    @pytest.mark.asyncio
    async def test_predict_optimal_timing(self, viral_predictor, sample_video_content):
        """Test optimal timing prediction for viral content"""        video_data = sample_video_content
        
        timing_prediction = await viral_predictor.predict_optimal_timing(
            content_data=video_data,
            platform=Platform.YOUTUBE,
            target_audience_timezone="US/Eastern"
        )
        
        assert 'optimal_posting_time' in timing_prediction
        assert 'peak_engagement_windows' in timing_prediction
        assert 'day_of_week_recommendations' in timing_prediction
        assert 'timing_confidence' in timing_prediction
        
        # Test timing validity
        optimal_time = timing_prediction['optimal_posting_time']
        assert isinstance(optimal_time, datetime)
        
        confidence = timing_prediction['timing_confidence']
        assert 0 <= confidence <= 1
    
    @pytest.mark.asyncio
    async def test_predict_hashtag_effectiveness(self, viral_predictor):
        """Test hashtag effectiveness prediction"""        hashtags = ["#AI", "#technology", "#innovation", "#viral", "#trending"]
        
        effectiveness_predictions = await viral_predictor.predict_hashtag_effectiveness(
            hashtags=hashtags,
            platform=Platform.INSTAGRAM,
            content_category="Technology"
        )
        
        assert len(effectiveness_predictions) == len(hashtags)
        
        for prediction in effectiveness_predictions:
            assert 'hashtag' in prediction
            assert 'effectiveness_score' in prediction
            assert 'reach_potential' in prediction
            assert 'competition_level' in prediction
            assert 'trend_momentum' in prediction
            
            # Test score validity
            assert 0 <= prediction['effectiveness_score'] <= 1
            assert 0 <= prediction['competition_level'] <= 1
            assert -1 <= prediction['trend_momentum'] <= 1  # Can be negative for declining trends
    
    @pytest.mark.asyncio
    async def test_predict_content_saturation(self, viral_predictor):
        """Test content saturation prediction"""        saturation_predictions = await viral_predictor.predict_content_saturation(
            content_topics=["AI tutorials", "cooking videos", "fitness challenges"],
            platforms=[Platform.YOUTUBE, Platform.TIKTOK],
            time_horizon=timedelta(days=30)
        )
        
        assert len(saturation_predictions) == 3
        
        for prediction in saturation_predictions:
            assert 'topic' in prediction
            assert 'current_saturation_level' in prediction
            assert 'predicted_saturation_trend' in prediction
            assert 'market_opportunity' in prediction
            
            # Test saturation metrics
            current_saturation = prediction['current_saturation_level']
            assert 0 <= current_saturation <= 1
            
            opportunity = prediction['market_opportunity']
            assert 0 <= opportunity <= 1
            
            # High saturation should correlate with low opportunity
            if current_saturation > 0.8:
                assert opportunity < 0.5


class TestTrendAnalysisPerformance:
    """Performance tests for trend analysis"""    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_trend_analysis_performance(self, benchmark, trend_analyzer):
        """Benchmark trend analysis performance"""        async def analyze_trends():
            return await trend_analyzer.analyze_current_trends(
                platforms=[Platform.YOUTUBE, Platform.TIKTOK],
                limit=10
            )
        
        result = await benchmark(analyze_trends)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_real_time_trend_monitoring(self, trend_analyzer):
        """Test real-time trend monitoring performance"""        start_time = datetime.now()
        
        # Simulate real-time monitoring
        monitoring_tasks = []
        for _ in range(3):
            task = trend_analyzer.monitor_real_time_trends(
                platforms=[Platform.TWITTER, Platform.TIKTOK],
                update_interval=timedelta(seconds=30),
                duration=timedelta(minutes=2)
            )
            monitoring_tasks.append(task)
        
        # Run monitoring tasks concurrently
        results = await asyncio.gather(*monitoring_tasks)
        
        monitoring_time = (datetime.now() - start_time).total_seconds()
        
        # Test that monitoring completed efficiently
        assert monitoring_time < 150  # Should complete within 2.5 minutes
        assert all(len(result) > 0 for result in results)
    
    @pytest.mark.asyncio
    async def test_batch_trend_prediction(self, trend_predictor):
        """Test batch trend prediction performance"""        trend_keywords = [
            "artificial intelligence", "sustainable fashion", "remote work",
            "electric vehicles", "cryptocurrency", "virtual reality",
            "plant-based food", "renewable energy", "mental health",
            "social media marketing"
        ]
        
        start_time = datetime.now()
        
        predictions = await trend_predictor.predict_batch_trends(
            keywords=trend_keywords,
            prediction_horizon=timedelta(days=30),
            platforms=[Platform.YOUTUBE, Platform.INSTAGRAM]
        )
        
        prediction_time = (datetime.now() - start_time).total_seconds()
        
        # Test results
        assert len(predictions) == len(trend_keywords)
        
        # Test performance
        assert prediction_time < 60  # Should complete within 1 minute


class TestTrendAnalysisErrorHandling:
    """Tests for trend analysis error handling"""    
    @pytest.mark.asyncio
    async def test_invalid_platform_handling(self, trend_analyzer):
        """Test handling of invalid platforms"""        with pytest.raises(ValidationError):
            await trend_analyzer.analyze_current_trends(
                platforms=["INVALID_PLATFORM"],  # Invalid platform
                limit=5
            )
    
    @pytest.mark.asyncio
    async def test_empty_keyword_handling(self, trend_predictor):
        """Test handling of empty keywords"""        with pytest.raises(ValidationError):
            await trend_predictor.predict_trend_evolution(
                trend_keywords=[],  # Empty keyword list
                prediction_horizon=timedelta(days=30),
                platforms=[Platform.YOUTUBE]
            )
    
    @pytest.mark.asyncio
    async def test_invalid_time_period_handling(self, trend_detector):
        """Test handling of invalid time periods"""        with pytest.raises(ValidationError):
            await trend_detector.detect_viral_content(
                platforms=[Platform.TIKTOK],
                time_period=timedelta(days=-1),  # Negative time period
                limit=5
            )
    
    @pytest.mark.asyncio
    async def test_api_rate_limit_handling(self, trend_analyzer):
        """Test handling of API rate limits"""        # Mock rate limit scenario
        with patch.object(trend_analyzer, '_make_api_call') as mock_api:
            mock_api.side_effect = Exception("Rate limit exceeded")
            
            # Should handle rate limits gracefully
            try:
                await trend_analyzer.analyze_current_trends(
                    platforms=[Platform.TWITTER],
                    limit=5
                )
            except Exception as e:
                # Should get a proper TrendAnalysisError, not the raw exception
                assert isinstance(e, TrendAnalysisError)
    
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, viral_predictor, sample_video_content):
        """Test handling of network timeouts"""        video_data = sample_video_content
        
        try:
            # Set short timeout to test timeout handling
            prediction = await asyncio.wait_for(
                viral_predictor.predict_viral_potential(
                    content_data=video_data,
                    platform=Platform.TIKTOK
                ),
                timeout=30.0  # 30 second timeout
            )
            
            # Should complete within timeout
            assert isinstance(prediction, ViralPrediction)
            
        except asyncio.TimeoutError:
            pytest.fail("Viral prediction timed out")


class TestTrendDataValidation:
    """Tests for trend data validation and quality"""    
    @pytest.mark.asyncio
    async def test_trend_data_consistency(self, trend_analyzer):
        """Test consistency of trend data across multiple calls"""        # Get trends multiple times
        trends_1 = await trend_analyzer.analyze_current_trends(
            platforms=[Platform.YOUTUBE],
            limit=5
        )
        
        trends_2 = await trend_analyzer.analyze_current_trends(
            platforms=[Platform.YOUTUBE],
            limit=5
        )
        
        # Should have some consistency in trending topics
        keywords_1 = set()
        keywords_2 = set()
        
        for trend in trends_1:
            keywords_1.update(trend.keywords)
        
        for trend in trends_2:
            keywords_2.update(trend.keywords)
        
        # Should have some overlap in trending keywords
        overlap = len(keywords_1.intersection(keywords_2))
        total_unique = len(keywords_1.union(keywords_2))
        
        # At least 30% overlap expected for current trends
        overlap_ratio = overlap / total_unique if total_unique > 0 else 0
        assert overlap_ratio >= 0.3
    
    @pytest.mark.asyncio
    async def test_trend_score_validation(self, trend_analyzer):
        """Test validation of trend scores and metrics"""        trends = await trend_analyzer.analyze_current_trends(
            platforms=[Platform.TIKTOK, Platform.INSTAGRAM],
            limit=10
        )
        
        for trend in trends:
            # All scores should be valid
            assert 0 <= trend.trend_strength <= 1
            assert trend.growth_rate >= 0
            assert 0 <= trend.detection_confidence <= 1
            
            # Viral potential should be reasonable
            if hasattr(trend, 'viral_potential'):
                assert 0 <= trend.viral_potential <= 1
            
            # Keywords and hashtags should be non-empty
            assert len(trend.keywords) > 0
            assert len(trend.hashtags) > 0
            
            # No invalid characters in hashtags
            for hashtag in trend.hashtags:
                assert hashtag.startswith('#')
                assert len(hashtag) > 1  # More than just '#'
    
    @pytest.mark.asyncio
    async def test_prediction_accuracy_validation(self, trend_predictor):
        """Test validation of prediction accuracy metrics"""        predictions = await trend_predictor.predict_trend_evolution(
            trend_keywords=["machine learning", "sustainable energy"],
            prediction_horizon=timedelta(days=14),
            platforms=[Platform.YOUTUBE]
        )
        
        for prediction in predictions:
            trajectory = prediction['predicted_trajectory']
            
            # Trajectory should have reasonable progression
            volumes = [point['predicted_volume'] for point in trajectory]
            confidences = [point['confidence'] for point in trajectory]
            
            # All volumes should be non-negative
            assert all(vol >= 0 for vol in volumes)
            
            # All confidences should be valid
            assert all(0 <= conf <= 1 for conf in confidences)
            
            # Confidence should generally decrease for future predictions
            if len(confidences) > 1:
                far_future_conf = confidences[-1]
                near_future_conf = confidences[0]
                assert far_future_conf <= near_future_conf * 1.2  # Allow some variance
