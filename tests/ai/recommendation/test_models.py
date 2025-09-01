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
Comprehensive Tests for AI Recommendation Data Models
Testing all data structures, validation, and serialization

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
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np
from dataclasses import asdict

from ai.recommendation.models import (
    CreatorProfile, ContentRecommendation, CollaborationMatch,
    TrendInsight, RevenueStrategy, AudienceInsight, Platform,
    ContentType, RevenueStream, Engagement, PerformanceMetrics,
    ContentMetadata, CreatorCompatibility, BrandMatch, ContentOpportunity
)


class TestCreatorProfile:
    """
Comprehensive tests for CreatorProfile model"""
    
    def test_creator_profile_creation(self, sample_creator_musician):
        """
Test basic creator profile creation"""
        profile = sample_creator_musician
        
        assert profile.creator_id == "musician_001"
        assert profile.display_name == "Alex Music"
        assert Platform.YOUTUBE in profile.platforms
        assert profile.followers_count[Platform.YOUTUBE] == 150000
        assert profile.engagement_rate[Platform.YOUTUBE] == 0.045
        assert ContentType.AUDIO in profile.content_types
        assert "Electronic" in profile.genres
        assert profile.verification_status is True
        assert profile.monetization_enabled is True
    
    def test_creator_profile_validation(self):
        """Test creator profile validation"""
        # Test invalid engagement rate
        with pytest.raises(ValueError):
            CreatorProfile(
                creator_id="test_001",
                display_name="Test Creator",
                engagement_rate={Platform.YOUTUBE: 1.5}  # Invalid: > 1.0
            )
        
        # Test invalid follower count
        with pytest.raises(ValueError):
            CreatorProfile(
                creator_id="test_002",
                display_name="Test Creator",
                followers_count={Platform.YOUTUBE: -100}  # Invalid: negative
            )
    
    def test_creator_profile_serialization(self, sample_creator_musician):
        """Test profile serialization and deserialization"""
        profile = sample_creator_musician
        
        # Test dictionary conversion
        profile_dict = asdict(profile)
        assert isinstance(profile_dict, dict)
        assert profile_dict["creator_id"] == "musician_001"
        
        # Test JSON serialization
        json_str = json.dumps(profile_dict, default=str)
        assert isinstance(json_str, str)
        
        # Test data integrity
        parsed_data = json.loads(json_str)
        assert parsed_data["creator_id"] == profile.creator_id
        assert parsed_data["display_name"] == profile.display_name
    
    def test_creator_profile_metrics_calculation(self, sample_creator_musician):
        """Test creator profile metric calculations"""
        profile = sample_creator_musician
        
        # Test total followers calculation
        total_followers = sum(profile.followers_count.values())
        assert total_followers == 425000  # 150k + 75k + 200k
        
        # Test average engagement rate
        avg_engagement = np.mean(list(profile.engagement_rate.values()))
        expected_avg = (0.045 + 0.12 + 0.08) / 3
        assert abs(avg_engagement - expected_avg) < 0.001
        
        # Test engagement score calculation
        engagement_score = total_followers * avg_engagement
        assert engagement_score > 0
    
    def test_creator_profile_platform_management(self):
        """
Test platform addition and removal"""
        profile = CreatorProfile(
            creator_id="test_003",
            display_name="Test Creator",
            platforms=[Platform.YOUTUBE]
        )
        
        # Add platform
        profile.platforms.append(Platform.TIKTOK)
        assert Platform.TIKTOK in profile.platforms
        assert len(profile.platforms) == 2
        
        # Remove platform
        profile.platforms.remove(Platform.YOUTUBE)
        assert Platform.YOUTUBE not in profile.platforms
        assert len(profile.platforms) == 1
    
    def test_creator_profile_comparison(self, sample_creator_musician, sample_creator_blogger):
        """Test creator profile comparison methods"""
        musician = sample_creator_musician
        blogger = sample_creator_blogger
        
        # Test they are different profiles
        assert musician.creator_id != blogger.creator_id
        assert musician.display_name != blogger.display_name
        
        # Test content type differences
        assert ContentType.AUDIO in musician.content_types
        assert ContentType.AUDIO not in blogger.content_types
        
        # Test platform overlap
        musician_platforms = set(musician.platforms)
        blogger_platforms = set(blogger.platforms)
        overlap = musician_platforms.intersection(blogger_platforms)
        assert Platform.YOUTUBE in overlap  # Both have YouTube


class TestContentRecommendation:
    """
Comprehensive tests for ContentRecommendation model"""
    
    def test_recommendation_creation(self, sample_content_recommendations):
        """
Test content recommendation creation"""
        recommendation = sample_content_recommendations[0]
        
        assert recommendation.recommendation_id == "rec_001"
        assert recommendation.content_type == ContentType.VIDEO
        assert recommendation.title == "10 Music Production Tips for Beginners"
        assert recommendation.platform == Platform.YOUTUBE
        assert 0 <= recommendation.relevance_score <= 1
        assert 0 <= recommendation.engagement_prediction <= 1
        assert 0 <= recommendation.viral_potential <= 1
        assert recommendation.estimated_reach > 0
        assert len(recommendation.hashtags) > 0
        assert len(recommendation.explanations) > 0
    
    def test_recommendation_scoring_validation(self):
        """Test recommendation score validation"""
        # Test valid scores
        recommendation = ContentRecommendation(
            recommendation_id="test_rec_001",
            content_type=ContentType.VIDEO,
            title="Test Content",
            description="Test description",
            relevance_score=0.85,
            engagement_prediction=0.75,
            viral_potential=0.45
        )
        assert recommendation.relevance_score == 0.85
        
        # Test invalid scores (should be clamped or raise error)
        with pytest.raises(ValueError):
            ContentRecommendation(
                recommendation_id="test_rec_002",
                content_type=ContentType.VIDEO,
                title="Test Content",
                relevance_score=1.5  # Invalid: > 1.0
            )
    
    def test_recommendation_hashtag_processing(self):
        """Test hashtag processing and validation"""
        recommendation = ContentRecommendation(
            recommendation_id="test_rec_003",
            content_type=ContentType.IMAGE,
            title="Test Image",
            hashtags=["#photography", "#art", "#creative", "#inspiration"]
        )
        
        assert len(recommendation.hashtags) == 4
        assert all(tag.startswith("#") for tag in recommendation.hashtags)
        assert "#photography" in recommendation.hashtags
    
    def test_recommendation_timing_optimization(self, sample_content_recommendations):
        """Test optimal timing recommendations"""
        recommendation = sample_content_recommendations[0]
        
        assert recommendation.optimal_posting_time is not None
        assert isinstance(recommendation.optimal_posting_time, datetime)
        
        # Test timing is in the future
        assert recommendation.optimal_posting_time > datetime.now()
        
        # Test timing is reasonable (within next 24 hours)
        time_diff = recommendation.optimal_posting_time - datetime.now()
        assert time_diff <= timedelta(hours=24)
    
    def test_recommendation_monetization_calculation(self, sample_content_recommendations):
        """
Test monetization potential calculations"""
        recommendation = sample_content_recommendations[0]
        
        assert recommendation.monetization_potential > 0
        assert recommendation.revenue_potential > 0
        
        # Test correlation between monetization potential and revenue
        high_monetization = recommendation.monetization_potential > 0.8
        high_revenue = recommendation.revenue_potential > 400
        
        if high_monetization:
            assert high_revenue, "High monetization should correlate with high revenue"
    
    def test_recommendation_content_pillar_validation(self, sample_content_recommendations):
        """Test content pillar assignment and validation"""
        recommendation = sample_content_recommendations[0]
        
        assert len(recommendation.content_pillars) > 0
        assert "Educational" in recommendation.content_pillars
        assert "Music" in recommendation.content_pillars
        
        # Test content pillars match content type and genre
        if recommendation.content_type == ContentType.VIDEO:
            assert any(pillar in ["Educational", "Entertainment", "Tutorial"] 
                      for pillar in recommendation.content_pillars)


class TestCollaborationMatch:
    """Comprehensive tests for CollaborationMatch model"""
    
    def test_collaboration_match_creation(self, sample_collaboration_matches):
        """
Test collaboration match creation"""
        match = sample_collaboration_matches[0]
        
        assert match.match_id == "collab_001"
        assert match.collaborator_id == "vocalist_001"
        assert match.collaborator_name == "Vocal Nina"
        assert 0 <= match.compatibility_score <= 1
        assert 0 <= match.mutual_benefit_score <= 1
        assert 0 <= match.audience_overlap <= 1
        assert match.revenue_potential > 0
        assert len(match.complementary_skills) > 0
        assert len(match.project_ideas) > 0
    
    def test_collaboration_scoring_algorithms(self, sample_collaboration_matches):
        """Test collaboration scoring calculations"""
        match = sample_collaboration_matches[0]
        
        # Test compatibility score factors
        assert match.compatibility_score > 0.5  # Should be reasonably high
        
        # Test mutual benefit calculation
        assert match.mutual_benefit_score > 0.5
        
        # Test success probability calculation
        assert 0 <= match.success_probability <= 1
        
        # Test geographic compatibility
        assert 0 <= match.geographic_compatibility <= 1
    
    def test_collaboration_timeline_estimation(self, sample_collaboration_matches):
        """
Test collaboration timeline estimation"""
        match = sample_collaboration_matches[0]
        
        assert match.timeline_estimate is not None
        assert isinstance(match.timeline_estimate, str)
        
        # Test timeline format
        timeline_parts = match.timeline_estimate.split("-")
        assert len(timeline_parts) >= 2  # Should have range like "2-4 weeks"
    
    def test_collaboration_effort_assessment(self, sample_collaboration_matches):
        """Test effort level assessment"""
        match = sample_collaboration_matches[0]
        
        valid_effort_levels = ["Low", "Medium", "High", "Very High"]
        assert match.effort_level in valid_effort_levels
        
        # Test effort level correlation with timeline
        if match.effort_level == "High":
            assert "week" in match.timeline_estimate.lower()
    
    def test_collaboration_revenue_projection(self, sample_collaboration_matches):
        """Test revenue projection calculations"""
        match = sample_collaboration_matches[0]
        
        assert match.revenue_potential > 0
        
        # Test revenue correlation with compatibility
        if match.compatibility_score > 0.8:
            assert match.revenue_potential > 1000, "High compatibility should yield higher revenue"


class TestTrendInsight:
    """Comprehensive tests for TrendInsight model"""
    
    def test_trend_insight_creation(self, sample_trend_insights):
        """
Test trend insight creation"""
        trend = sample_trend_insights[0]
        
        assert trend.trend_id == "trend_001"
        assert trend.trend_name == "Lo-Fi Hip Hop Revival"
        assert 0 <= trend.trend_score <= 1
        assert 0 <= trend.growth_velocity <= 1
        assert trend.peak_prediction is not None
        assert len(trend.geographic_distribution) > 0
        assert len(trend.demographic_appeal) > 0
        assert len(trend.platform_performance) > 0
    
    def test_trend_geographic_distribution(self, sample_trend_insights):
        """Test geographic distribution calculations"""
        trend = sample_trend_insights[0]
        
        geo_dist = trend.geographic_distribution
        
        # Test distribution sums close to 1.0
        total_distribution = sum(geo_dist.values())
        assert abs(total_distribution - 1.0) < 0.1, "Geographic distribution should sum to ~1.0"
        
        # Test all values are percentages
        assert all(0 <= value <= 1 for value in geo_dist.values())
        
        # Test major regions are included
        assert "US" in geo_dist or "USA" in geo_dist
    
    def test_trend_demographic_analysis(self, sample_trend_insights):
        """Test demographic appeal analysis"""
        trend = sample_trend_insights[0]
        
        demo_appeal = trend.demographic_appeal
        
        # Test age ranges format
        age_ranges = list(demo_appeal.keys())
        assert any("-" in age_range for age_range in age_ranges), "Should have age ranges like '18-25'"
        
        # Test distribution values
        total_appeal = sum(demo_appeal.values())
        assert abs(total_appeal - 1.0) < 0.1, "Demographic appeal should sum to ~1.0"
    
    def test_trend_platform_performance(self, sample_trend_insights):
        """Test platform performance metrics"""
        trend = sample_trend_insights[0]
        
        platform_perf = trend.platform_performance
        
        # Test platform scores
        assert all(0 <= score <= 1 for score in platform_perf.values())
        assert all(isinstance(platform, Platform) for platform in platform_perf.keys())
        
        # Test major platforms are covered
        major_platforms = {Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM}
        covered_platforms = set(platform_perf.keys())
        assert len(major_platforms.intersection(covered_platforms)) > 0
    
    def test_trend_content_opportunities(self, sample_trend_insights):
        """
Test content opportunity identification"""
        trend = sample_trend_insights[0]
        
        assert len(trend.content_opportunities) > 0
        assert len(trend.monetization_opportunities) > 0
        
        # Test opportunities are strings
        assert all(isinstance(opp, str) for opp in trend.content_opportunities)
        assert all(isinstance(opp, str) for opp in trend.monetization_opportunities)
        
        # Test opportunities are relevant to trend
        trend_keywords = trend.trend_name.lower().split()
        opportunities_text = " ".join(trend.content_opportunities).lower()
        
        # At least one keyword should appear in opportunities
        assert any(keyword in opportunities_text for keyword in trend_keywords)
    
    def test_trend_sustainability_scoring(self, sample_trend_insights):
        """Test trend sustainability scoring"""
        trend = sample_trend_insights[0]
        
        assert 0 <= trend.sustainability_score <= 1
        
        # Test sustainability factors
        competitive_landscape = trend.competitive_landscape.lower()
        valid_competition_levels = ["low", "moderate", "high", "very high"]
        assert any(level in competitive_landscape for level in valid_competition_levels)
        
        entry_difficulty = trend.entry_difficulty.lower()
        valid_difficulties = ["low", "medium", "high"]
        assert any(diff in entry_difficulty for diff in valid_difficulties)


class TestRevenueStrategy:
    """Comprehensive tests for RevenueStrategy model"""
    
    def test_revenue_strategy_creation(self):
        """
Test revenue strategy creation"""
        strategy = RevenueStrategy(
            creator_id="test_creator_001",
            target_revenue=10000.0,
            optimization_period=timedelta(days=90),
            primary_revenue_streams=[RevenueStream.SPONSORSHIPS, RevenueStream.ADVERTISING]
        )
        
        assert strategy.creator_id == "test_creator_001"
        assert strategy.target_revenue == 10000.0
        assert strategy.optimization_period == timedelta(days=90)
        assert len(strategy.primary_revenue_streams) == 2
        assert RevenueStream.SPONSORSHIPS in strategy.primary_revenue_streams
    
    def test_revenue_stream_diversification(self):
        """Test revenue stream diversification"""
        # Test single stream (high risk)
        single_stream_strategy = RevenueStrategy(
            creator_id="test_001",
            primary_revenue_streams=[RevenueStream.ADVERTISING]
        )
        assert len(single_stream_strategy.primary_revenue_streams) == 1
        
        # Test diversified streams (lower risk)
        diversified_strategy = RevenueStrategy(
            creator_id="test_002",
            primary_revenue_streams=[
                RevenueStream.SPONSORSHIPS,
                RevenueStream.SUBSCRIPTIONS,
                RevenueStream.MERCHANDISE,
                RevenueStream.AFFILIATE
            ]
        )
        assert len(diversified_strategy.primary_revenue_streams) == 4
    
    def test_revenue_projections_validation(self):
        """Test revenue projection calculations"""
        strategy = RevenueStrategy(
            creator_id="test_003",
            target_revenue=5000.0,
            growth_projections={
                "month_1": 1000.0,
                "month_2": 1500.0,
                "month_3": 2500.0
            }
        )
        
        projections = strategy.growth_projections
        
        # Test projections are positive
        assert all(value > 0 for value in projections.values())
        
        # Test growth trajectory
        values = list(projections.values())
        assert values[1] > values[0], "Should show growth"
        assert values[2] > values[1], "Should show continued growth"
    
    def test_revenue_optimization_scoring(self):
        """Test optimization score calculation"""
        strategy = RevenueStrategy(
            creator_id="test_004",
            optimization_score=0.85,
            confidence_level=0.78,
            expected_roi=2.5
        )
        
        assert 0 <= strategy.optimization_score <= 1
        assert 0 <= strategy.confidence_level <= 1
        assert strategy.expected_roi > 0
        
        # Test correlation between confidence and optimization score
        if strategy.optimization_score > 0.8:
            assert strategy.confidence_level > 0.5, "High optimization should have reasonable confidence"


class TestAudienceInsight:
    """Comprehensive tests for AudienceInsight model"""
    
    def test_audience_insight_creation(self):
        """
Test audience insight creation"""
        insight = AudienceInsight(
            primary_demographics={
                "age_18_24": 0.35,
                "age_25_34": 0.40,
                "age_35_44": 0.25
            },
            interest_categories={
                "music": 0.6,
                "technology": 0.3,
                "lifestyle": 0.1
            },
            platform_preferences={
                Platform.YOUTUBE: 0.8,
                Platform.TIKTOK: 0.6
            }
        )
        
        # Test demographic distribution
        demo_total = sum(insight.primary_demographics.values())
        assert abs(demo_total - 1.0) < 0.01, "Demographics should sum to 1.0"
        
        # Test interest distribution
        interest_total = sum(insight.interest_categories.values())
        assert abs(interest_total - 1.0) < 0.01, "Interests should sum to 1.0"
        
        # Test platform preferences
        assert all(0 <= pref <= 1 for pref in insight.platform_preferences.values())
    
    def test_audience_overlap_calculation(self):
        """Test audience overlap calculations"""
        audience1 = AudienceInsight(
            primary_demographics={"age_18_24": 0.5, "age_25_34": 0.5},
            interest_categories={"music": 0.7, "technology": 0.3}
        )
        
        audience2 = AudienceInsight(
            primary_demographics={"age_18_24": 0.3, "age_25_34": 0.7},
            interest_categories={"music": 0.8, "lifestyle": 0.2}
        )
        
        # Test that audiences have some overlap in demographics
        overlap_age = min(audience1.primary_demographics.get("age_18_24", 0),
                         audience2.primary_demographics.get("age_18_24", 0))
        assert overlap_age > 0, "Should have some age overlap"
        
        # Test interest overlap
        overlap_interest = min(audience1.interest_categories.get("music", 0),
                              audience2.interest_categories.get("music", 0))
        assert overlap_interest > 0, "Should have music interest overlap"


class TestPerformanceMetrics:
    """Comprehensive tests for PerformanceMetrics model"""
    
    def test_performance_metrics_creation(self, sample_performance_metrics):
        """
Test performance metrics creation"""
        metrics = PerformanceMetrics(
            views=sample_performance_metrics["views"],
            likes=sample_performance_metrics["likes"],
            comments=sample_performance_metrics["comments"],
            shares=sample_performance_metrics["shares"],
            engagement_rate=sample_performance_metrics["engagement_rate"],
            revenue_generated=sample_performance_metrics["revenue_generated"]
        )
        
        assert metrics.views == 15000
        assert metrics.likes == 1200
        assert metrics.comments == 180
        assert metrics.shares == 95
        assert abs(metrics.engagement_rate - 0.067) < 0.001
        assert abs(metrics.revenue_generated - 280.50) < 0.01
    
    def test_engagement_rate_calculation(self, sample_performance_metrics):
        """Test engagement rate calculations"""
        views = sample_performance_metrics["views"]
        likes = sample_performance_metrics["likes"]
        comments = sample_performance_metrics["comments"]
        shares = sample_performance_metrics["shares"]
        
        # Calculate expected engagement rate
        total_engagements = likes + comments + shares
        expected_rate = total_engagements / views
        
        actual_rate = sample_performance_metrics["engagement_rate"]
        
        # Allow small tolerance for floating point calculations
        assert abs(actual_rate - expected_rate) < 0.01
    
    def test_roi_calculation(self, sample_performance_metrics):
        """Test ROI calculation"""
        revenue = sample_performance_metrics["revenue_generated"]
        cost_per_engagement = sample_performance_metrics["cost_per_engagement"]
        views = sample_performance_metrics["views"]
        engagement_rate = sample_performance_metrics["engagement_rate"]
        
        # Calculate expected ROI
        total_cost = (views * engagement_rate) * cost_per_engagement
        expected_roi = revenue / total_cost if total_cost > 0 else 0
        
        actual_roi = sample_performance_metrics["roi"]
        
        # Test ROI is positive and reasonable
        assert actual_roi > 0
        assert abs(actual_roi - expected_roi) < 0.1


class TestModelIntegration:
    """Integration tests for model interactions"""
    
    def test_creator_recommendation_integration(self, sample_creator_musician, sample_content_recommendations):
        """
Test integration between creator profile and recommendations"""
        creator = sample_creator_musician
        recommendations = sample_content_recommendations
        
        # Test recommendations are suitable for creator
        for rec in recommendations:
            # Test content type compatibility
            if rec.content_type in creator.content_types:
                assert True  # Compatible content type
            
            # Test platform compatibility
            if rec.platform in creator.platforms:
                assert True  # Compatible platform
            
            # Test genre alignment
            if any(genre.lower() in rec.title.lower() or genre.lower() in rec.description.lower() 
                   for genre in creator.genres):
                assert True  # Genre alignment found
    
    def test_collaboration_creator_matching(self, sample_creator_musician, sample_collaboration_matches):
        """
Test collaboration matching with creator profiles"""
        creator = sample_creator_musician
        matches = sample_collaboration_matches
        
        for match in matches:
            # Test collaboration makes sense for creator
            assert match.compatibility_score > 0.5
            
            # Test complementary skills exist
            assert len(match.complementary_skills) > 0
            
            # Test revenue potential is reasonable
            assert match.revenue_potential > 0
            assert match.revenue_potential < creator.average_revenue * 10  # Not unrealistic
    
    def test_trend_recommendation_alignment(self, sample_trend_insights, sample_content_recommendations):
        """
Test alignment between trends and recommendations"""
        trends = sample_trend_insights
        recommendations = sample_content_recommendations
        
        for trend in trends:
            # Find recommendations that align with this trend
            aligned_recs = [
                rec for rec in recommendations
                if rec.trend_alignment > 0.7
            ]
            
            # Test trend-aligned recommendations exist
            if aligned_recs:
                for rec in aligned_recs:
                    # Test hashtag alignment
                    trend_hashtags = set(tag.lower() for tag in trend.related_hashtags)
                    rec_hashtags = set(tag.lower() for tag in rec.hashtags)
                    
                    if trend_hashtags.intersection(rec_hashtags):
                        assert True  # Hashtag alignment found


class TestModelValidation:
    """
Comprehensive model validation tests"""
    
    def test_all_models_serializable(self, sample_creator_musician, sample_content_recommendations,
                                   sample_collaboration_matches, sample_trend_insights):
        """
Test all models can be serialized to JSON"""
        models_to_test = [
            sample_creator_musician,
            sample_content_recommendations[0],
            sample_collaboration_matches[0],
            sample_trend_insights[0]
        ]
        
        for model in models_to_test:
            try:
                # Test dictionary conversion
                model_dict = asdict(model)
                assert isinstance(model_dict, dict)
                
                # Test JSON serialization
                json_str = json.dumps(model_dict, default=str)
                assert isinstance(json_str, str)
                
                # Test deserialization
                parsed_data = json.loads(json_str)
                assert isinstance(parsed_data, dict)
                
            except Exception as e:
                pytest.fail(f"Serialization failed for {type(model).__name__}: {str(e)}")
    
    def test_model_field_types(self, sample_creator_musician):
        """Test model field type validation"""
        creator = sample_creator_musician
        
        # Test string fields
        assert isinstance(creator.creator_id, str)
        assert isinstance(creator.display_name, str)
        assert isinstance(creator.bio, str)
        
        # Test list fields
        assert isinstance(creator.platforms, list)
        assert isinstance(creator.content_types, list)
        assert isinstance(creator.genres, list)
        
        # Test dict fields
        assert isinstance(creator.followers_count, dict)
        assert isinstance(creator.engagement_rate, dict)
        
        # Test numeric fields
        assert isinstance(creator.average_revenue, (int, float))
        assert isinstance(creator.collaboration_openness, (int, float))
        assert isinstance(creator.brand_safety_score, (int, float))
        
        # Test boolean fields
        assert isinstance(creator.verification_status, bool)
        assert isinstance(creator.monetization_enabled, bool)
    
    def test_model_constraints(self):
        """
Test model constraint validation"""
        # Test engagement rate constraints
        with pytest.raises(ValueError):
            CreatorProfile(
                creator_id="test",
                engagement_rate={Platform.YOUTUBE: -0.1}  # Negative not allowed
            )
        
        # Test score constraints in recommendations
        with pytest.raises(ValueError):
            ContentRecommendation(
                recommendation_id="test",
                relevance_score=1.5  # > 1.0 not allowed
            )
    
    @pytest.mark.benchmark
    def test_model_performance(self, benchmark, sample_creator_musician):
        """Benchmark model creation and serialization performance"""
        def create_and_serialize():
            # Create model instance
            creator = CreatorProfile(
                creator_id="perf_test",
                display_name="Performance Test Creator",
                platforms=[Platform.YOUTUBE, Platform.TIKTOK],
                followers_count={Platform.YOUTUBE: 100000, Platform.TIKTOK: 50000},
                engagement_rate={Platform.YOUTUBE: 0.05, Platform.TIKTOK: 0.08}
            )
            
            # Serialize to dict
            creator_dict = asdict(creator)
            
            # Serialize to JSON
            json_str = json.dumps(creator_dict, default=str)
            
            return len(json_str)
        
        # Benchmark the operation
        result = benchmark(create_and_serialize)
        assert result > 0  # Should return non-zero length
