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
Comprehensive Tests for Core Recommendation Engine
Testing recommendation generation, algorithms, and optimization

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
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np

from ai.recommendation.core import RecommendationEngine, RecommendationConfig
from ai.recommendation.models import (
    CreatorProfile, ContentRecommendation, Platform, ContentType,
    RecommendationRequest, RecommendationResponse
)
from ai.recommendation.exceptions import RecommendationError, ValidationError


class TestRecommendationEngine:
    """
Comprehensive tests for the main recommendation engine"""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self):
        """
Test recommendation engine initialization"""
        engine = RecommendationEngine()
        
        # Test initial state
        assert engine.status.name == "INITIALIZING"
        
        # Test initialization
        success = await engine.initialize()
        assert success is True
        assert engine.status.name == "READY"
        
        # Test initialization is idempotent
        success_again = await engine.initialize()
        assert success_again is True
    
    @pytest.mark.asyncio
    async def test_engine_initialization_failure(self):
        """Test engine initialization failure handling"""
        engine = RecommendationEngine()
        
        # Mock a failure condition
        original_method = engine._load_recommendation_models
        
        async def mock_failing_load():
        try:
            logger.info(f"Executing mock_failing_load")
            
            # Implementation for mock_failing_load
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"mock_failing_load completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mock_failing_load failed: {e}")
            raise
        engine._load_recommendation_models = mock_failing_load
        
        with pytest.raises(RecommendationError):
            await engine.initialize()
        
        assert engine.status.name == "ERROR"
        
        # Restore original method
        engine._load_recommendation_models = original_method
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_basic(self, recommendation_engine, sample_creator_musician):
        """Test basic recommendation generation"""
        creator = sample_creator_musician
        
        recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=5
        )
        
        assert len(recommendations) <= 5
        assert all(isinstance(rec, ContentRecommendation) for rec in recommendations)
        
        # Test recommendation validity
        for rec in recommendations:
            assert rec.recommendation_id
            assert rec.content_type in ContentType
            assert rec.title
            assert rec.description
            assert 0 <= rec.relevance_score <= 1
            assert 0 <= rec.engagement_prediction <= 1
            assert 0 <= rec.viral_potential <= 1
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_with_filters(self, recommendation_engine, sample_creator_musician):
        """
Test recommendation generation with content filters"""
        creator = sample_creator_musician
        
        # Test platform filter
        youtube_recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=10,
            platform_filter=[Platform.YOUTUBE]
        )
        
        assert all(rec.platform == Platform.YOUTUBE for rec in youtube_recommendations)
        
        # Test content type filter
        video_recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=10,
            content_type_filter=[ContentType.VIDEO]
        )
        
        assert all(rec.content_type == ContentType.VIDEO for rec in video_recommendations)
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_time_sensitive(self, recommendation_engine, sample_creator_musician):
        """
Test time-sensitive recommendation generation"""
        creator = sample_creator_musician
        
        # Test with specific time horizon
        short_term_recs = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=5,
            time_horizon=timedelta(days=7)
        )
        
        long_term_recs = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=5,
            time_horizon=timedelta(days=30)
        )
        
        # Short-term recommendations should focus on immediate trends
        # Long-term should have different characteristics
        assert len(short_term_recs) > 0
        assert len(long_term_recs) > 0
        
        # Test optimal posting times are within time horizon
        for rec in short_term_recs:
            if rec.optimal_posting_time:
                time_diff = rec.optimal_posting_time - datetime.now()
                assert time_diff <= timedelta(days=7)
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_personalization(self, recommendation_engine, sample_creator_musician, sample_creator_blogger):
        """
Test recommendation personalization for different creators"""
        musician = sample_creator_musician
        blogger = sample_creator_blogger
        
        musician_recs = await recommendation_engine.generate_recommendations(
            creator_profile=musician,
            limit=5
        )
        
        blogger_recs = await recommendation_engine.generate_recommendations(
            creator_profile=blogger,
            limit=5
        )
        
        # Test that recommendations are different and personalized
        musician_titles = [rec.title for rec in musician_recs]
        blogger_titles = [rec.title for rec in blogger_recs]
        
        # Should have different recommendations
        assert set(musician_titles) != set(blogger_titles)
        
        # Musician recommendations should be music-focused
        music_related = sum(1 for title in musician_titles 
                           if any(word in title.lower() for word in ['music', 'audio', 'sound', 'beat']))
        assert music_related > 0
        
        # Blogger recommendations should be tech-focused
        tech_related = sum(1 for title in blogger_titles 
                          if any(word in title.lower() for word in ['tech', 'review', 'tutorial', 'gadget']))
        assert tech_related > 0
    
    @pytest.mark.asyncio
    async def test_recommendation_scoring_algorithms(self, recommendation_engine, sample_creator_musician):
        """
Test recommendation scoring algorithm accuracy"""
        creator = sample_creator_musician
        
        recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=10
        )
        
        # Test score consistency
        for rec in recommendations:
            # Relevance should be higher for content matching creator's style
            if any(genre.lower() in rec.title.lower() for genre in creator.genres):
                assert rec.relevance_score > 0.5
            
            # Engagement prediction should correlate with trend alignment
            if rec.trend_alignment > 0.8:
                assert rec.engagement_prediction > 0.6
            
            # Viral potential should be reasonable
            assert 0 <= rec.viral_potential <= 1
        
        # Test recommendations are sorted by relevance
        relevance_scores = [rec.relevance_score for rec in recommendations]
        assert relevance_scores == sorted(relevance_scores, reverse=True)
    
    @pytest.mark.asyncio
    async def test_content_based_filtering(self, recommendation_engine, sample_creator_musician):
        """
Test content-based filtering algorithm"""
        creator = sample_creator_musician
        
        # Generate recommendations using content-based filtering
        recommendations = await recommendation_engine._generate_content_based_recommendations(
            creator, limit=5
        )
        
        assert len(recommendations) > 0
        
        # Test content alignment with creator profile
        for rec in recommendations:
            # Should match creator's content types
            content_match = rec.content_type in creator.content_types
            
            # Should align with creator's genres
            genre_match = any(genre.lower() in rec.description.lower() 
                             for genre in creator.genres)
            
            # Should target creator's platforms
            platform_match = rec.platform in creator.platforms
            
            # At least one alignment criterion should be met
            assert content_match or genre_match or platform_match
    
    @pytest.mark.asyncio
    async def test_collaborative_filtering(self, recommendation_engine, sample_creator_musician):
        """
Test collaborative filtering algorithm"""
        creator = sample_creator_musician
        
        # Mock similar creators for collaborative filtering
        similar_creators = [
            "similar_musician_001",
            "similar_musician_002",
            "similar_musician_003"
        ]
        
        recommendations = await recommendation_engine._generate_collaborative_recommendations(
            creator, similar_creators, limit=5
        )
        
        assert len(recommendations) > 0
        
        # Test that recommendations consider similar creators' successful content
        for rec in recommendations:
            assert rec.relevance_score > 0.3  # Should have reasonable relevance
            assert rec.success_patterns is not None  # Should include success pattern data
    
    @pytest.mark.asyncio
    async def test_trend_boosted_recommendations(self, recommendation_engine, sample_creator_musician):
        """Test trend-boosted recommendation generation"""
        creator = sample_creator_musician
        
        # Generate trend-boosted recommendations
        recommendations = await recommendation_engine._apply_trend_boosting(
            creator, limit=5
        )
        
        assert len(recommendations) > 0
        
        # Test trend alignment
        for rec in recommendations:
            if rec.trend_alignment > 0.7:
                # High trend alignment should boost other scores
                assert rec.viral_potential > 0.5
                assert rec.engagement_prediction > 0.6
    
    @pytest.mark.asyncio
    async def test_revenue_optimized_recommendations(self, recommendation_engine, sample_creator_musician):
        """
Test revenue-optimized recommendation generation"""
        creator = sample_creator_musician
        
        # Generate revenue-optimized recommendations
        recommendations = await recommendation_engine._optimize_for_revenue(
            creator, limit=5
        )
        
        assert len(recommendations) > 0
        
        # Test revenue optimization
        for rec in recommendations:
            assert rec.monetization_potential > 0
            assert rec.revenue_potential > 0
            
            # High monetization potential should correlate with revenue
            if rec.monetization_potential > 0.8:
                assert rec.revenue_potential > creator.average_revenue * 0.1
    
    @pytest.mark.asyncio
    async def test_recommendation_diversity(self, recommendation_engine, sample_creator_musician):
        """
Test recommendation diversity algorithms"""
        creator = sample_creator_musician
        
        recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=10,
            diversity_factor=0.8  # High diversity
        )
        
        # Test content type diversity
        content_types = [rec.content_type for rec in recommendations]
        unique_content_types = set(content_types)
        assert len(unique_content_types) > 1  # Should have variety
        
        # Test platform diversity
        platforms = [rec.platform for rec in recommendations]
        unique_platforms = set(platforms)
        assert len(unique_platforms) > 1  # Should cover multiple platforms
        
        # Test topic diversity
        titles = [rec.title.lower() for rec in recommendations]
        # Check that not all titles contain the same keywords
        music_count = sum(1 for title in titles if 'music' in title)
        assert music_count < len(recommendations)  # Not all should be about music


class TestRecommendationConfig:
    """
Tests for recommendation configuration and customization"""
    
    def test_default_config(self):
        """
Test default recommendation configuration"""
        config = RecommendationConfig()
        
        assert config.max_recommendations == 50
        assert config.diversity_factor == 0.5
        assert config.trend_weight == 0.3
        assert config.personalization_weight == 0.7
        assert config.enable_collaborative_filtering is True
        assert config.enable_content_based_filtering is True
        assert config.enable_trend_boosting is True
    
    def test_custom_config(self):
        """
Test custom recommendation configuration"""
        config = RecommendationConfig(
            max_recommendations=20,
            diversity_factor=0.8,
            trend_weight=0.5,
            personalization_weight=0.5,
            enable_collaborative_filtering=False
        )
        
        assert config.max_recommendations == 20
        assert config.diversity_factor == 0.8
        assert config.trend_weight == 0.5
        assert config.personalization_weight == 0.5
        assert config.enable_collaborative_filtering is False
    
    def test_config_validation(self):
        """
Test configuration validation"""
        # Test invalid diversity factor
        with pytest.raises(ValueError):
            RecommendationConfig(diversity_factor=1.5)  # > 1.0
        
        # Test invalid weights
        with pytest.raises(ValueError):
            RecommendationConfig(trend_weight=-0.1)  # < 0.0
        
        # Test weights sum validation
        with pytest.raises(ValueError):
            RecommendationConfig(
                trend_weight=0.8,
                personalization_weight=0.8  # Sum > 1.0
            )


class TestRecommendationRequest:
    """
Tests for recommendation request handling"""
    
    @pytest.mark.asyncio
    async def test_process_recommendation_request(self, recommendation_engine, sample_creator_musician):
        """
Test processing of recommendation requests"""
        creator = sample_creator_musician
        
        request = RecommendationRequest(
            creator_id=creator.creator_id,
            limit=5,
            platform_filter=[Platform.YOUTUBE],
            content_type_filter=[ContentType.VIDEO],
            time_horizon=timedelta(days=14),
            include_explanations=True,
            diversity_factor=0.6
        )
        
        response = await recommendation_engine.process_request(request)
        
        assert isinstance(response, RecommendationResponse)
        assert len(response.recommendations) <= 5
        assert all(rec.platform == Platform.YOUTUBE for rec in response.recommendations)
        assert all(rec.content_type == ContentType.VIDEO for rec in response.recommendations)
        assert all(len(rec.explanations) > 0 for rec in response.recommendations)
    
    @pytest.mark.asyncio
    async def test_invalid_recommendation_request(self, recommendation_engine):
        """
Test handling of invalid recommendation requests"""
        # Test missing creator ID
        invalid_request = RecommendationRequest(
            creator_id="",  # Invalid
            limit=5
        )
        
        with pytest.raises(ValidationError):
            await recommendation_engine.process_request(invalid_request)
        
        # Test invalid limit
        invalid_request = RecommendationRequest(
            creator_id="valid_creator",
            limit=-1  # Invalid
        )
        
        with pytest.raises(ValidationError):
            await recommendation_engine.process_request(invalid_request)
    
    @pytest.mark.asyncio
    async def test_recommendation_caching(self, recommendation_engine, sample_creator_musician):
        """Test recommendation caching mechanisms"""
        creator = sample_creator_musician
        
        # Generate recommendations twice
        start_time = time.time()
        first_recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=5
        )
        first_duration = time.time() - start_time
        
        start_time = time.time()
        second_recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=5
        )
        second_duration = time.time() - start_time
        
        # Second call should be faster due to caching
        assert second_duration < first_duration * 1.5  # Allow some variance
        
        # Results should be consistent
        assert len(first_recommendations) == len(second_recommendations)


class TestRecommendationPerformance:
    """
Performance tests for recommendation generation"""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_recommendation_generation_performance(self, benchmark, recommendation_engine, sample_creator_musician):
        """
Benchmark recommendation generation performance"""
        creator = sample_creator_musician
        
        async def generate_recommendations():
            return await recommendation_engine.generate_recommendations(
                creator_profile=creator,
                limit=10
            )
        
        # Benchmark the operation
        result = await benchmark(generate_recommendations)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_recommendation_generation_timeout(self, recommendation_engine, sample_creator_musician):
        """
Test recommendation generation with timeout"""
        creator = sample_creator_musician
        
        try:
            # Set short timeout to test timeout handling
            recommendations = await asyncio.wait_for(
                recommendation_engine.generate_recommendations(
                    creator_profile=creator,
                    limit=100  # Large request
                ),
                timeout=10.0  # 10 second timeout
            )
            
            # Should complete within timeout
            assert len(recommendations) > 0
            
        except asyncio.TimeoutError:
            pytest.fail("Recommendation generation timed out")
    
    @pytest.mark.asyncio
    async def test_batch_recommendation_generation(self, recommendation_engine, sample_creator_musician, sample_creator_blogger):
        """Test batch recommendation generation for multiple creators"""
        creators = [sample_creator_musician, sample_creator_blogger]
        
        start_time = time.time()
        
        # Generate recommendations for all creators
        all_recommendations = await recommendation_engine.generate_batch_recommendations(
            creator_profiles=creators,
            limit_per_creator=5
        )
        
        generation_time = time.time() - start_time
        
        # Test results
        assert len(all_recommendations) == len(creators)
        assert all(len(recs) <= 5 for recs in all_recommendations.values())
        
        # Test performance (should be better than sequential)
        assert generation_time < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.asyncio
    async def test_concurrent_recommendation_requests(self, recommendation_engine, sample_creator_musician):
        """
Test handling concurrent recommendation requests"""
        creator = sample_creator_musician
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            task = recommendation_engine.generate_recommendations(
                creator_profile=creator,
                limit=3
            )
            tasks.append(task)
        
        # Execute concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time
        
        # Test all requests completed successfully
        assert len(results) == 5
        assert all(len(recs) > 0 for recs in results)
        
        # Test reasonable performance
        assert concurrent_time < 10.0  # Should handle concurrent requests efficiently


class TestRecommendationQuality:
    """
Tests for recommendation quality and accuracy"""
    
    @pytest.mark.asyncio
    async def test_recommendation_relevance_scoring(self, recommendation_engine, sample_creator_musician):
        """
Test recommendation relevance scoring accuracy"""
        creator = sample_creator_musician
        
        recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=10
        )
        
        # Test that high relevance scores correlate with creator profile
        high_relevance_recs = [rec for rec in recommendations if rec.relevance_score > 0.8]
        
        for rec in high_relevance_recs:
            # High relevance should mean good alignment
            content_match = rec.content_type in creator.content_types
            platform_match = rec.platform in creator.platforms
            genre_match = any(genre.lower() in (rec.title + rec.description).lower() 
                             for genre in creator.genres)
            
            # At least two alignment criteria should be met for high relevance
            alignment_count = sum([content_match, platform_match, genre_match])
            assert alignment_count >= 2
    
    @pytest.mark.asyncio
    async def test_recommendation_engagement_prediction(self, recommendation_engine, sample_creator_musician):
        """
Test engagement prediction accuracy"""
        creator = sample_creator_musician
        
        recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=10
        )
        
        # Test engagement prediction factors
        for rec in recommendations:
            # High engagement prediction should have supporting factors
            if rec.engagement_prediction > 0.8:
                # Should have good trend alignment or viral potential
                assert rec.trend_alignment > 0.5 or rec.viral_potential > 0.5
                
                # Should be optimally timed
                assert rec.optimal_posting_time is not None
                
                # Should have relevant hashtags
                assert len(rec.hashtags) > 0
    
    @pytest.mark.asyncio
    async def test_recommendation_explanation_quality(self, recommendation_engine, sample_creator_musician):
        """
Test quality of recommendation explanations"""
        creator = sample_creator_musician
        
        recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=5,
            include_explanations=True
        )
        
        for rec in recommendations:
            # Should have explanations
            assert len(rec.explanations) > 0
            
            # Explanations should be meaningful
            for explanation in rec.explanations:
                assert len(explanation) > 10  # Not just single words
                assert any(word in explanation.lower() for word in 
                          ['because', 'based', 'trending', 'audience', 'similar', 'performance'])
    
    @pytest.mark.asyncio
    async def test_recommendation_consistency(self, recommendation_engine, sample_creator_musician):
        """
Test recommendation consistency across multiple generations"""
        creator = sample_creator_musician
        
        # Generate recommendations multiple times
        recommendation_sets = []
        for _ in range(3):
            recs = await recommendation_engine.generate_recommendations(
                creator_profile=creator,
                limit=5,
                consistency_mode=True  # Use consistent random seeds
            )
            recommendation_sets.append(recs)
        
        # Test that recommendations are reasonably consistent
        first_set = recommendation_sets[0]
        second_set = recommendation_sets[1]
        
        # Should have some overlap in content types and platforms
        first_content_types = set(rec.content_type for rec in first_set)
        second_content_types = set(rec.content_type for rec in second_set)
        
        first_platforms = set(rec.platform for rec in first_set)
        second_platforms = set(rec.platform for rec in second_set)
        
        # Should have significant overlap
        content_overlap = len(first_content_types.intersection(second_content_types))
        platform_overlap = len(first_platforms.intersection(second_platforms))
        
        assert content_overlap > 0
        assert platform_overlap > 0


class TestRecommendationEdgeCases:
    """
Tests for edge cases and error scenarios"""
    
    @pytest.mark.asyncio
    async def test_recommendations_for_new_creator(self, recommendation_engine):
        """
Test recommendations for creators with minimal data"""
        new_creator = CreatorProfile(
            creator_id="new_creator_001",
            display_name="New Creator",
            platforms=[Platform.YOUTUBE],
            followers_count={Platform.YOUTUBE: 10},  # Very small following
            engagement_rate={Platform.YOUTUBE: 0.0},  # No engagement yet
            content_types=[ContentType.VIDEO],
            genres=["General"]
        )
        
        recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=new_creator,
            limit=5
        )
        
        # Should still generate recommendations
        assert len(recommendations) > 0
        
        # Should focus on beginner-friendly content
        beginner_keywords = ['beginner', 'start', 'first', 'intro', 'basic', 'getting started']
        beginner_content = sum(1 for rec in recommendations 
                              if any(keyword in rec.title.lower() for keyword in beginner_keywords))
        
        assert beginner_content > 0
    
    @pytest.mark.asyncio
    async def test_recommendations_with_empty_filters(self, recommendation_engine, sample_creator_musician):
        """Test recommendations with empty filters"""
        creator = sample_creator_musician
        
        # Test with empty platform filter
        recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=5,
            platform_filter=[]  # Empty filter
        )
        
        # Should still generate recommendations
        assert len(recommendations) > 0
        
        # Should use creator's platforms
        platforms_used = set(rec.platform for rec in recommendations)
        creator_platforms = set(creator.platforms)
        
        assert len(platforms_used.intersection(creator_platforms)) > 0
    
    @pytest.mark.asyncio
    async def test_recommendations_with_zero_limit(self, recommendation_engine, sample_creator_musician):
        """
Test recommendations with zero limit"""
        creator = sample_creator_musician
        
        with pytest.raises(ValidationError):
            await recommendation_engine.generate_recommendations(
                creator_profile=creator,
                limit=0  # Invalid limit
            )
    
    @pytest.mark.asyncio
    async def test_recommendations_with_very_high_limit(self, recommendation_engine, sample_creator_musician):
        """
Test recommendations with very high limit"""
        creator = sample_creator_musician
        
        recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=1000  # Very high limit
        )
        
        # Should be capped at maximum
        assert len(recommendations) <= recommendation_engine.config.max_recommendations
    
    @pytest.mark.asyncio
    async def test_recommendations_for_unsupported_platform(self, recommendation_engine):
        """
Test recommendations for unsupported platforms"""
        creator = CreatorProfile(
            creator_id="test_creator",
            display_name="Test Creator",
            platforms=[],  # No supported platforms
            content_types=[ContentType.VIDEO]
        )
        
        recommendations = await recommendation_engine.generate_recommendations(
            creator_profile=creator,
            limit=5
        )
        
        # Should use default platforms or popular platforms
        assert len(recommendations) > 0
        platforms_used = set(rec.platform for rec in recommendations)
        popular_platforms = {Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM}
        
        assert len(platforms_used.intersection(popular_platforms)) > 0
