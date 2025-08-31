"""
Pytest Configuration and Fixtures for AI Recommendation System Tests
Comprehensive test setup and shared fixtures for industrial-grade testing

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Email: mlaiel@live.de
"""

import pytest
import pytest_asyncio
import asyncio
import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import AsyncMock, MagicMock
import numpy as np
from pathlib import Path

# Import models and components to test
from ai.recommendation.models import (
    CreatorProfile, ContentRecommendation, CollaborationMatch,
    TrendInsight, RevenueStrategy, Platform, ContentType, RevenueStream,
    Engagement
)
from ai.recommendation.core import RecommendationEngine
from ai.recommendation.content_analyzer import ContentAnalyzer
from ai.recommendation.collaboration_matcher import CollaborationMatcher
from ai.recommendation.trend_analyzer import TrendAnalyzer
from ai.recommendation.revenue_optimizer import RevenueOptimizer
from ai.recommendation.protection_integrator import ProtectionIntegrator
from ai.recommendation.utils import ModelManager, HealthChecker


# Pytest configuration
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings"""



    return {
        "testing": True,
        "database_url": "sqlite:///:memory:",
        "redis_url": "redis://localhost:6379/1",
        "cache_enabled": True,
        "performance_benchmarks": True,
        "mock_external_apis": True,
        "log_level": "DEBUG"
    }


@pytest.fixture
def temp_directory():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest_asyncio.fixture
async def recommendation_engine():
    """Recommendation engine instance"""
    engine = RecommendationEngine()
    await engine.initialize()
    return engine


@pytest_asyncio.fixture
async def content_analyzer():
    """Content analyzer instance"""
    analyzer = ContentAnalyzer()
    await analyzer.initialize()
    return analyzer


@pytest_asyncio.fixture
async def collaboration_matcher():
    """Collaboration matcher instance"""
    matcher = CollaborationMatcher()
    await matcher.initialize()
    return matcher


@pytest_asyncio.fixture
async def trend_analyzer():
    """Trend analyzer instance"""
    analyzer = TrendAnalyzer()
    await analyzer.initialize()
    return analyzer


@pytest_asyncio.fixture
async def revenue_optimizer():
    """Revenue optimizer instance"""
    optimizer = RevenueOptimizer()
    await optimizer.initialize()
    return optimizer


@pytest_asyncio.fixture
async def protection_integrator():
    """Protection integrator instance"""
    integrator = ProtectionIntegrator()
    await integrator.initialize()
    return integrator


@pytest.fixture
def model_manager():
    """Model manager instance"""



    return ModelManager()


@pytest.fixture
def health_checker():
    """Health checker instance"""



    return HealthChecker()


# Sample Content Data Fixtures

@pytest.fixture
def sample_video_content():
    """Sample video content data"""



    return {
        "title": "Amazing Music Production Tutorial",
        "description": "Learn professional music production techniques in this comprehensive tutorial",
        "duration": 900,  # 15 minutes
        "resolution": "1920x1080",
        "frame_rate": 30,
        "file_size": 250000000,  # 250MB
        "format": "mp4",
        "thumbnail_url": "https://example.com/thumbnail.jpg",
        "upload_date": "2025-01-31T10:00:00Z",
        "tags": ["music", "production", "tutorial", "beats"],
        "category": "Education",
        "language": "en",
        "captions_available": True,
        "quality_metrics": {
            "video_quality": 0.85,
            "audio_quality": 0.90,
            "stability": 0.88
        },
        "metadata": {
            "creator": "MusicProTV",
            "equipment": "Canon EOS R5",
            "location": "Berlin Studio"
        }
    }


@pytest.fixture
def sample_audio_content():
    """Sample audio content data"""



    return {
        "title": "Atmospheric Electronic Track",
        "description": "Ambient electronic music perfect for relaxation",
        "duration": 180,  # 3 minutes
        "sample_rate": 44100,
        "bit_rate": 320,
        "file_size": 8000000,  # 8MB
        "format": "mp3",
        "genre": "Electronic",
        "bpm": 110,
        "key": "Am",
        "mood": "Relaxing",
        "energy_level": 0.6,
        "danceability": 0.4,
        "valence": 0.7,
        "instruments": ["synthesizer", "drums", "bass"],
        "upload_date": "2025-01-31T10:00:00Z",
        "tags": ["electronic", "ambient", "relaxing", "instrumental"],
        "metadata": {
            "artist": "ElectroVibes",
            "album": "Digital Dreams",
            "year": 2025,
            "label": "Independent"
        }
    }


@pytest.fixture
def sample_text_content():
    """Sample text content data"""



    return {
        "title": "Top 10 Tech Trends for 2025",
        "content": """Here are the most exciting technology trends that will shape 2025:

1. Advanced AI Integration - AI becoming more seamlessly integrated into daily workflows
2. Quantum Computing Breakthroughs - Major advances in quantum processing power
3. Extended Reality (XR) - VR/AR experiences becoming mainstream
4. Sustainable Tech - Green technology solutions gaining momentum
5. Edge Computing Expansion - Processing power moving closer to data sources

Each of these trends represents a massive opportunity for innovation and growth. 
What excites you most about the future of technology? Let me know in the comments!

#TechTrends2025 #Innovation #FutureTech #AI #QuantumComputing""",
        "word_count": 87,
        "character_count": 542,
        "reading_time": "2 min",
        "language": "en",
        "sentiment": "positive",
        "tone": "professional",
        "hashtags": ["#TechTrends2025", "#Innovation", "#FutureTech", "#AI", "#QuantumComputing"],
        "mentions": [],
        "links": [],
        "upload_date": "2025-01-31T10:00:00Z",
        "category": "Technology",
        "target_audience": "Tech professionals 25-45",
        "call_to_action": "What excites you most about the future of technology? Let me know in the comments!",
        "metadata": {
            "author": "TechSarah",
            "platform_optimized": ["Twitter", "LinkedIn", "Facebook"],
            "engagement_prediction": 0.78
        }
    }


@pytest.fixture
def sample_image_content():
    """Sample image content data"""



    return {
        "title": "Stunning Landscape Photography",
        "description": "Captured this breathtaking sunrise over the mountains during my recent trip",
        "width": 4000,
        "height": 3000,
        "file_size": 12000000,  # 12MB
        "format": "jpg",
        "dpi": 300,
        "color_space": "sRGB",
        "camera_settings": {
            "camera": "Canon EOS R5",
            "lens": "24-70mm f/2.8",
            "focal_length": "35mm",
            "aperture": "f/8",
            "shutter_speed": "1/125",
            "iso": 200
        },
        "location": {
            "country": "Switzerland",
            "region": "Alps",
            "coordinates": [46.5197, 6.6323]
        },
        "upload_date": "2025-01-31T10:00:00Z",
        "tags": ["landscape", "mountains", "sunrise", "nature", "photography"],
        "category": "Photography",
        "style": "Landscape",
        "color_palette": ["#FF6B35", "#F7931E", "#FFD23F", "#06D6A0", "#118AB2"],
        "composition_elements": ["rule_of_thirds", "leading_lines", "foreground_interest"],
        "editing_style": "Natural",
        "metadata": {
            "photographer": "VisualEmma",
            "copyright": "All rights reserved",
            "licensing": "Commercial use available"
        }
    }


# Creator Profile Fixtures

@pytest.fixture
def sample_creator_musician():
    """Sample musician creator profile"""



    return CreatorProfile(
        creator_id="musician_001",
        username="alexmusic",
        display_name="Alex Music",
        bio="Professional musician creating electronic and acoustic content",
        follower_count=425000,  # Total across platforms
        following_count=1250,
        total_content_count=580,
        platforms=[Platform.YOUTUBE, Platform.SPOTIFY, Platform.TIKTOK],
        primary_content_types=[ContentType.AUDIO, ContentType.VIDEO],
        genres=["Electronic", "Acoustic", "Ambient"],
        languages=["en", "de"],
        target_demographics={
            "age_range": "18-35",
            "interests": ["music", "production", "technology"],
            "geographic_focus": ["EU", "US"]
        },
        engagement_metrics=Engagement(
            likes=15000,
            comments=2400,
            shares=850,
            saves=1200,
            views=125000,
            click_through_rate=0.045,
            engagement_rate=0.072
        ),
        average_views=125000,
        growth_rate=0.15,
        collaboration_openness=0.8,
        brand_safety_score=0.9,
        authenticity_score=0.85,
        influence_score=0.78,
        niche_authority=0.92,
        content_quality_score=0.88,
        consistency_score=0.85,
        trending_topics=["AI music", "electronic beats", "live sessions"],
        recent_viral_content=["beat_tutorial_001", "synth_masterclass"],
        monetization_streams=[RevenueStream.SPONSORSHIP, RevenueStream.MERCHANDISE],
        estimated_earnings=5000.0,
        collaboration_history=["collab_001", "collab_002"],
        brand_partnerships=["audio_brand_1", "synth_company"],
        verification_status=True,
        contact_information={"email": "alex@musicpro.com"},
        manager_information={"name": "Music Manager Pro"}
    )


@pytest_asyncio.fixture(autouse=True)
async def cleanup_after_test():
    """Cleanup after each test"""
    yield
    # Cleanup any test artifacts, temporary files, etc.
    # This runs after each test automatically


# Test Data Fixtures

@pytest.fixture
def sample_audio_features():
    """Sample audio feature vectors"""



    return {
        "mfcc": np.random.rand(13, 100).tolist(),
        "chroma": np.random.rand(12, 100).tolist(),
        "spectral_centroid": np.random.rand(100).tolist(),
        "zero_crossing_rate": np.random.rand(100).tolist(),
        "tempo": 120.5,
        "key": "C major",
        "energy": 0.75,
        "valence": 0.68,
        "danceability": 0.82
    }


@pytest.fixture
def sample_image_features():
    """Sample image feature vectors"""



    return {
        "color_histogram": np.random.rand(256).tolist(),
        "texture_features": np.random.rand(64).tolist(),
        "edge_density": 0.42,
        "brightness": 0.65,
        "contrast": 0.78,
        "saturation": 0.55,
        "dominant_colors": ["#FF5733", "#33FF57", "#3357FF"],
        "objects_detected": ["person", "camera", "studio"],
        "scene_classification": "indoor_studio",
        "aesthetic_score": 0.81
    }


@pytest.fixture
def sample_text_features():
    """Sample text feature vectors"""



    return {
        "sentiment_score": 0.72,
        "emotion_distribution": {
            "joy": 0.45,
            "excitement": 0.35,
            "neutral": 0.15,
            "sadness": 0.05
        },
        "topic_distribution": {
            "music": 0.6,
            "technology": 0.25,
            "lifestyle": 0.15
        },
        "readability_score": 0.78,
        "engagement_words": ["amazing", "incredible", "must-see"],
        "hashtag_relevance": 0.85,
        "call_to_action_strength": 0.67,
        "brand_mention_sentiment": 0.89
    }


# Mock Fixtures for External Services

@pytest.fixture
def mock_external_api():
    """Mock external API calls"""
    mock = AsyncMock()
    mock.get_trending_hashtags.return_value = ["#trending", "#viral", "#popular"]
    mock.get_platform_insights.return_value = {
        "optimal_posting_times": ["14:00", "18:00", "20:00"],
        "audience_activity": 0.75,
        "competition_level": 0.45
    }
    mock.get_monetization_data.return_value = {
        "cpm": 2.50,
        "cpc": 0.35,
        "conversion_rate": 0.028
    }
    return mock


@pytest.fixture
def mock_database():
    """Mock database operations"""
    mock = AsyncMock()
    mock.save_recommendation.return_value = True
    mock.get_creator_history.return_value = []
    mock.update_performance_metrics.return_value = True
    return mock


# Benchmark Fixtures

@pytest.fixture
def performance_thresholds():
    """Performance benchmark thresholds"""



    return {
        "recommendation_generation": 0.2,  # 200ms
        "content_analysis": 0.5,           # 500ms
        "collaboration_matching": 0.3,     # 300ms
        "trend_analysis": 1.0,             # 1s
        "revenue_optimization": 0.3,       # 300ms
        "batch_processing_100": 2.0,       # 2s for 100 items
        "model_initialization": 5.0        # 5s for model init
    }


# Utility Functions for Tests

def assert_creator_profile_valid(profile: CreatorProfile):
    """Assert creator profile is valid"""
    assert profile.creator_id
    assert profile.display_name
    assert len(profile.platforms) > 0
    assert all(platform in Platform for platform in profile.platforms)
    assert all(count >= 0 for count in profile.followers_count.values())
    assert all(0 <= rate <= 1 for rate in profile.engagement_rate.values())


# Test Data Loading

@pytest.fixture
def load_test_data():
    """Load test data from JSON files"""
    def _load_data(filename: str):
        test_data_path = Path(__file__).parent / "fixtures" / filename
        if test_data_path.exists():
            with open(test_data_path, 'r') as f:
                return json.load(f)
        return {}
    return _load_data


@pytest.fixture
def sample_creator_portfolio():
    """Sample creator portfolio data"""



    return [
        {
            "content_id": "track_001",
            "content_type": "audio",
            "title": "Summer Vibes",
            "genre": "pop",
            "views": 15000,
            "engagement_rate": 0.08,
            "upload_date": "2025-01-15T12:00:00Z"
        },
        {
            "content_id": "track_002", 
            "content_type": "audio",
            "title": "Midnight Blues",
            "genre": "blues",
            "views": 8500,
            "engagement_rate": 0.12,
            "upload_date": "2025-01-20T14:30:00Z"
        },
        {
            "content_id": "video_001",
            "content_type": "video", 
            "title": "Behind the Music",
            "duration": 300,
            "views": 22000,
            "engagement_rate": 0.15,
            "upload_date": "2025-01-25T16:00:00Z"
        }
    ]


@pytest.fixture
def sample_creator_blogger():
    """Sample blogger creator profile"""



    return CreatorProfile(
        creator_id="blogger_001",
        username="lifestyleblogger",
        display_name="Sarah Lifestyle",
        bio="Lifestyle blogger focusing on wellness, travel and personal development",
        follower_count=180000,  # Total across platforms
        following_count=850,
        total_content_count=420,
        platforms=[Platform.INSTAGRAM, Platform.YOUTUBE, Platform.TIKTOK],
        primary_content_types=[ContentType.IMAGE, ContentType.VIDEO, ContentType.TEXT],
        genres=["Lifestyle", "Travel", "Wellness"],
        languages=["en", "fr"],
        target_demographics={
            "age_range": "20-40",
            "interests": ["lifestyle", "wellness", "travel", "fashion"],
            "geographic_focus": ["US", "CA", "EU"]
        },
        engagement_metrics=Engagement(
            likes=8500,
            comments=1200,
            shares=650,
            saves=900,
            views=45000,
            click_through_rate=0.08,
            engagement_rate=0.12
        ),
        average_views=45000,
        growth_rate=0.12,
        collaboration_openness=0.9,
        brand_safety_score=0.95,
        authenticity_score=0.92,
        influence_score=0.75,
        niche_authority=0.85,
        content_quality_score=0.88,
        consistency_score=0.82,
        trending_topics=["wellness trends", "travel hacks", "sustainable living"],
        recent_viral_content=["morning_routine_viral", "travel_budget_tips"],
        monetization_streams=[RevenueStream.SPONSORSHIP, RevenueStream.AFFILIATE_MARKETING],
        estimated_earnings=3500.0,
        collaboration_history=["lifestyle_collab_001"],
        brand_partnerships=["wellness_brand_1", "travel_company"],
        verification_status=True,
        contact_information={"email": "sarah@lifestyleblog.com"},
        manager_information={"name": "Lifestyle Manager"}
    )


# Advanced Recommendation Fixtures

@pytest.fixture
def compatibility_scorer():
    """Sample compatibility scorer instance"""
    from ai.recommendation.collaboration_matcher import CompatibilityScorer
    config = {
        'scoring_weights': {
            'audience_overlap': 0.25,
            'content_synergy': 0.30,
            'engagement_compatibility': 0.20,
            'schedule_alignment': 0.15,
            'brand_safety': 0.10
        },
        'threshold_minimum': 0.3,
        'boost_factors': {
            'verified_creators': 1.1,
            'high_engagement': 1.2,
            'premium_members': 1.15
        }
    }
    return CompatibilityScorer(config=config)


@pytest.fixture
def partnership_analyzer():
    """Sample partnership analyzer instance"""
    from ai.recommendation.collaboration_matcher import PartnershipAnalyzer
    config = {
        'analysis_depth': 'comprehensive',
        'risk_threshold': 0.4,
        'opportunity_weights': {
            'audience_growth': 0.35,
            'engagement_boost': 0.25,
            'revenue_potential': 0.40
        }
    }
    return PartnershipAnalyzer(config=config)


@pytest.fixture 
def collaboration_recommender():
    """Sample collaboration recommender instance"""
    from ai.recommendation.collaboration_matcher import CollaborationRecommender
    config = {
        'recommendation_count': 10,
        'diversity_factor': 0.3,
        'freshness_weight': 0.2,
        'personalization_strength': 0.8
    }
    return CollaborationRecommender(config=config)
