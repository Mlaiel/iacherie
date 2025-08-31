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
Unit tests for Revenue Calculator
Tests for automated revenue calculation functionality.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from monetization.revenue_calculator import RevenueCalculator, RevenueData


class TestRevenueCalculator:
    """Test suite for RevenueCalculator class"""
    
    @pytest.fixture
    def calculator(self):
        """Create RevenueCalculator instance for testing"""
        return RevenueCalculator()
    
    @pytest.fixture
    def sample_revenue_data(self):
        """Sample revenue data for testing"""
        return [
            RevenueData(
                platform="youtube",
                content_id="test_123",
                views=10000,
                engagement_rate=0.05,
                revenue=25.50,
                period_start=datetime.now() - timedelta(days=30),
                period_end=datetime.now()
            ),
            RevenueData(
                platform="youtube", 
                content_id="test_123",
                views=12000,
                engagement_rate=0.06,
                revenue=30.25,
                period_start=datetime.now() - timedelta(days=29),
                period_end=datetime.now()
            )
        ]
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_youtube_revenue_calculation_basic(self, calculator):
        """Test basic YouTube revenue calculation"""
        revenue = await calculator.calculate_youtube_revenue(
            views=10000,
            watch_time_hours=5000,
            engagement_rate=0.05,
            subscriber_count=2000,
            country="US"
        )
        
        assert revenue > 0
        assert isinstance(revenue, float)
        assert revenue > 2.5  # Minimum expected for 10k views
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_youtube_revenue_below_threshold(self, calculator):
        """Test YouTube revenue when below monetization threshold"""
        revenue = await calculator.calculate_youtube_revenue(
            views=10000,
            watch_time_hours=5000,
            engagement_rate=0.05,
            subscriber_count=500,  # Below 1000 threshold
            country="US"
        )
        
        assert revenue == 0.0
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_youtube_revenue_high_engagement_bonus(self, calculator):
        """Test YouTube revenue with high engagement bonus"""
        base_revenue = await calculator.calculate_youtube_revenue(
            views=10000,
            watch_time_hours=5000,
            engagement_rate=0.03,  # Below bonus threshold
            subscriber_count=2000,
            country="US"
        )
        
        bonus_revenue = await calculator.calculate_youtube_revenue(
            views=10000,
            watch_time_hours=5000,
            engagement_rate=0.08,  # Above bonus threshold
            subscriber_count=2000,
            country="US"
        )
        
        assert bonus_revenue > base_revenue
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_instagram_revenue_calculation(self, calculator):
        """Test Instagram revenue calculation"""
        revenue = await calculator.calculate_instagram_revenue(
            impressions=50000,
            reach=35000,
            engagement_rate=0.04,
            story_views=5000,
            follower_count=1500
        )
        
        assert revenue > 0
        assert isinstance(revenue, float)
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_instagram_revenue_below_threshold(self, calculator):
        """Test Instagram revenue below follower threshold"""
        revenue = await calculator.calculate_instagram_revenue(
            impressions=50000,
            reach=35000,
            engagement_rate=0.04,
            story_views=5000,
            follower_count=500  # Below 1000 threshold
        )
        
        assert revenue == 0.0
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_tiktok_revenue_calculation(self, calculator):
        """Test TikTok revenue calculation"""
        revenue = await calculator.calculate_tiktok_revenue(
            views=100000,
            shares=5000,
            likes=8000,
            follower_count=15000,
            in_creator_fund=True
        )
        
        assert revenue >= 0
        assert isinstance(revenue, float)
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_tiktok_revenue_below_threshold(self, calculator):
        """Test TikTok revenue below follower threshold"""
        revenue = await calculator.calculate_tiktok_revenue(
            views=100000,
            shares=5000,
            likes=8000,
            follower_count=5000,  # Below 10000 threshold
            in_creator_fund=True
        )
        
        assert revenue == 0.0
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_spotify_revenue_calculation(self, calculator):
        """Test Spotify revenue calculation"""
        revenue = await calculator.calculate_spotify_revenue(
            streams=50000,
            premium_streams=30000,
            country_distribution={"US": 20000, "CA": 15000, "GB": 15000}
        )
        
        assert revenue > 0
        assert isinstance(revenue, float)
        # Should be around streams * 0.003 * 0.70 for base calculation
        expected_min = 50000 * 0.003 * 0.70 * 0.8  # Conservative estimate
        assert revenue >= expected_min
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_spotify_premium_bonus(self, calculator):
        """Test Spotify premium streams earn more"""
        base_revenue = await calculator.calculate_spotify_revenue(
            streams=50000,
            premium_streams=10000,  # Low premium ratio
            country_distribution={"US": 50000}
        )
        
        premium_revenue = await calculator.calculate_spotify_revenue(
            streams=50000,
            premium_streams=40000,  # High premium ratio
            country_distribution={"US": 50000}
        )
        
        assert premium_revenue > base_revenue
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_total_revenue_calculation(self, calculator):
        """Test total revenue calculation across platforms"""
        platform_data = {
            "youtube": {
                "views": 10000,
                "watch_time_hours": 5000,
                "engagement_rate": 0.05,
                "subscriber_count": 2000,
                "country": "US"
            },
            "instagram": {
                "impressions": 50000,
                "reach": 35000,
                "engagement_rate": 0.04,
                "story_views": 5000,
                "follower_count": 1500
            },
            "spotify": {
                "streams": 25000,
                "premium_streams": 15000,
                "country_distribution": {"US": 25000}
            }
        }
        
        revenues = await calculator.calculate_total_revenue("test_content", platform_data)
        
        assert "total" in revenues
        assert "youtube" in revenues
        assert "instagram" in revenues
        assert "spotify" in revenues
        assert revenues["total"] >= 0
        assert revenues["total"] == sum([
            revenues["youtube"], 
            revenues["instagram"], 
            revenues["spotify"]
        ])
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_ml_revenue_prediction(self, calculator, sample_revenue_data):
        """Test ML-based revenue prediction"""
        predictions = await calculator.predict_revenue_ml(
            platform="youtube",
            historical_data=sample_revenue_data,
            forecast_days=7
        )
        
        assert len(predictions) == 7
        assert all(isinstance(pred, float) for pred in predictions)
        assert all(pred >= 0 for pred in predictions)  # Revenue can't be negative
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_ml_prediction_insufficient_data(self, calculator):
        """Test ML prediction with insufficient historical data"""
        limited_data = [
            RevenueData("youtube", "test", 1000, 0.05, 10.0)
        ]
        
        predictions = await calculator.predict_revenue_ml(
            platform="youtube",
            historical_data=limited_data,
            forecast_days=5
        )
        
        assert len(predictions) == 5
        assert all(pred == 10.0 for pred in predictions)  # Should return average
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_ml_prediction_no_data(self, calculator):
        """Test ML prediction with no historical data"""
        predictions = await calculator.predict_revenue_ml(
            platform="youtube",
            historical_data=[],
            forecast_days=3
        )
        
        assert len(predictions) == 3
        assert all(pred == 0.0 for pred in predictions)
    
    @pytest.mark.unit
    @pytest.mark.monetization
    def test_country_cpm_multiplier(self, calculator):
        """Test country-based CPM multipliers"""
        assert calculator._get_country_cpm_multiplier("US") == 1.0
        assert calculator._get_country_cpm_multiplier("DE") == 0.7
        assert calculator._get_country_cpm_multiplier("IN") == 0.1
        assert calculator._get_country_cpm_multiplier("UNKNOWN") == 0.5
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_real_time_revenue_caching(self, calculator):
        """Test real-time revenue caching mechanism"""
        content_id = "test_content_123"
        
        # First call should calculate
        revenue1 = await calculator.get_real_time_revenue(content_id)
        
        # Second call should use cache
        revenue2 = await calculator.get_real_time_revenue(content_id)
        
        assert revenue1 == revenue2
        assert "total" in revenue1
        assert revenue1["total"] > 0
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_error_handling_youtube(self, calculator):
        """Test error handling in YouTube revenue calculation"""
        # Test with invalid data types
        revenue = await calculator.calculate_youtube_revenue(
            views="invalid",  # Should be int
            watch_time_hours=5000,
            engagement_rate=0.05,
            subscriber_count=2000,
            country="US"
        )
        
        assert revenue == 0.0
    
    @pytest.mark.unit
    @pytest.mark.monetization
    async def test_revenue_data_structure(self):
        """Test RevenueData dataclass structure"""
        revenue_data = RevenueData(
            platform="youtube",
            content_id="test_123",
            views=10000,
            engagement_rate=0.05,
            revenue=25.50
        )
        
        assert revenue_data.platform == "youtube"
        assert revenue_data.content_id == "test_123"
        assert revenue_data.views == 10000
        assert revenue_data.engagement_rate == 0.05
        assert revenue_data.revenue == 25.50
        assert revenue_data.currency == "EUR"  # Default value
    
    @pytest.mark.slow
    @pytest.mark.monetization
    async def test_large_scale_calculation(self, calculator):
        """Test revenue calculation with large numbers"""
        # Test with very large view counts
        revenue = await calculator.calculate_youtube_revenue(
            views=10_000_000,  # 10 million views
            watch_time_hours=50_000,
            engagement_rate=0.05,
            subscriber_count=100_000,
            country="US"
        )
        
        assert revenue > 1000  # Should be substantial revenue
        assert isinstance(revenue, float)
    
    @pytest.mark.unit
    @pytest.mark.monetization
    def test_platform_rates_configuration(self, calculator):
        """Test platform rates configuration"""
        rates = calculator.PLATFORM_RATES
        
        # Verify all expected platforms are configured
        expected_platforms = ["youtube", "instagram", "tiktok", "spotify", "twitter"]
        for platform in expected_platforms:
            assert platform in rates
        
        # Verify YouTube configuration
        youtube_config = rates["youtube"]
        assert "cpm_min" in youtube_config
        assert "cpm_max" in youtube_config
        assert "engagement_multiplier" in youtube_config
        assert "monetization_threshold" in youtube_config
        
        # Verify reasonable values
        assert youtube_config["cpm_min"] > 0
        assert youtube_config["cpm_max"] > youtube_config["cpm_min"]
        assert youtube_config["monetization_threshold"] == 1000