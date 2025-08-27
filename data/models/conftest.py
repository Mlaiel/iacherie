"""
Pytest Configuration for Data Models
===================================

Configuration and fixtures for testing data models.
Provides database setup, test data, and common utilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import pytest
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, Any, List
import tempfile
import os

# SQLAlchemy imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Import all models and enums
from . import (
    ContentModel, UserModel, FingerprintModel, RevenueModel,
    AnalyticsModel, ProtectionModel, LicensingModel,
    ContentType, ContentStatus, ContentVisibility,
    UserType, UserStatus, SubscriptionTier,
    FingerprintType, FingerprintAlgorithm, FingerprintStatus,
    RevenueSource, RevenueStatus, PaymentMethod,
    AnalyticsType, MetricType, TimeGranularity,
    ProtectionType, ViolationType, SeverityLevel, ProtectionStatus,
    LicenseType, LicenseCategory, UsageType, LicenseStatus
)

# Import the base for table creation
from .content_model import Base


@pytest.fixture(scope="session")
def database_engine():
    """Create test database engine"""
    # Use in-memory SQLite for testing
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,  # Set to True for SQL debugging
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(database_engine):
    """Create database session for testing"""
    SessionLocal = sessionmaker(bind=database_engine)
    session = SessionLocal()
    
    yield session
    
    # Rollback any changes
    session.rollback()
    session.close()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'id': str(uuid.uuid4()),
        'username': 'test_creator_2025',
        'email': 'test.creator@example.com',
        'password_hash': 'hashed_password_123',
        'first_name': 'Test',
        'last_name': 'Creator',
        'display_name': 'Test Creator',
        'bio': 'Professional content creator for testing',
        'user_type': UserType.CREATOR.value,
        'subscription_tier': SubscriptionTier.PREMIUM.value,
        'status': UserStatus.ACTIVE.value,
        'is_verified': True,
        'phone_number': '+1234567890',
        'country': 'US',
        'timezone': 'UTC',
        'language': 'en',
        'date_of_birth': date(1990, 1, 1),
        'profile_metadata': {
            'social_links': {
                'youtube': 'https://youtube.com/@testcreator',
                'instagram': '@testcreator',
                'tiktok': '@testcreator'
            },
            'content_categories': ['education', 'technology'],
            'preferred_platforms': ['youtube', 'instagram']
        }
    }


@pytest.fixture
def sample_content_data(sample_user_data):
    """Sample content data for testing"""
    return {
        'id': str(uuid.uuid4()),
        'user_id': sample_user_data['id'],
        'title': 'Test Content: Advanced AI Tutorial',
        'description': 'A comprehensive tutorial about artificial intelligence',
        'content_type': ContentType.VIDEO.value,
        'status': ContentStatus.PUBLISHED.value,
        'visibility': ContentVisibility.PUBLIC.value,
        'duration_seconds': 3600,  # 1 hour
        'file_size_bytes': 1073741824,  # 1GB
        'format': 'mp4',
        'resolution': '1920x1080',
        'view_count': 15000,
        'like_count': 1200,
        'comment_count': 45,
        'share_count': 230,
        'download_count': 89,
        'watch_time_total_minutes': 42000,
        'engagement_rate': Decimal('8.5'),
        'revenue_total': Decimal('850.75'),
        'content_metadata': {
            'tags': ['AI', 'Tutorial', 'Technology', 'Education'],
            'category': 'Education',
            'language': 'en',
            'subtitles_available': True,
            'quality_score': 95,
            'thumbnail_url': 'https://example.com/thumbnail.jpg'
        },
        'seo_metadata': {
            'keywords': ['artificial intelligence', 'machine learning', 'tutorial'],
            'meta_title': 'Advanced AI Tutorial - Complete Guide',
            'meta_description': 'Learn AI fundamentals with this comprehensive tutorial',
            'canonical_url': 'https://example.com/ai-tutorial'
        },
        'platform_data': {
            'youtube': {
                'video_id': 'ABC123DEF456',
                'views': 15000,
                'likes': 1200,
                'dislikes': 45
            },
            'instagram': {
                'post_id': 'IGP_789012',
                'views': 8500,
                'likes': 680
            }
        }
    }


@pytest.fixture
def sample_fingerprint_data(sample_content_data):
    """Sample fingerprint data for testing"""
    return {
        'id': str(uuid.uuid4()),
        'content_id': sample_content_data['id'],
        'fingerprint_type': FingerprintType.AUDIO.value,
        'algorithm': FingerprintAlgorithm.PERCEPTUAL_HASH.value,
        'hash_value': 'a1b2c3d4e5f6789012345678901234567890abcdef',
        'confidence_score': Decimal('95.5'),
        'status': FingerprintStatus.ACTIVE.value,
        'processing_time_ms': 2500,
        'algorithm_version': '2.1.0',
        'fingerprint_metadata': {
            'audio_features': {
                'duration': 3600,
                'sample_rate': 44100,
                'channels': 2,
                'bitrate': 320
            },
            'extracted_features': {
                'spectral_centroid': [1250.5, 1180.2, 1340.8],
                'mfcc': [12.5, -8.3, 4.2, -2.1],
                'tempo': 120.5
            }
        }
    }


@pytest.fixture
def sample_revenue_data(sample_user_data, sample_content_data):
    """Sample revenue data for testing"""
    return {
        'id': str(uuid.uuid4()),
        'user_id': sample_user_data['id'],
        'content_id': sample_content_data['id'],
        'revenue_source': RevenueSource.YOUTUBE_ADS.value,
        'gross_amount': Decimal('125.50'),
        'platform_fee': Decimal('18.83'),
        'net_amount': Decimal('106.67'),
        'currency': 'USD',
        'status': RevenueStatus.COMPLETED.value,
        'payment_method': PaymentMethod.BANK_TRANSFER.value,
        'transaction_reference': 'TXN_YT_20250101_001',
        'views_count': 15000,
        'cpm': Decimal('8.37'),
        'cpc': Decimal('0.42'),
        'country': 'US',
        'device_type': 'mobile',
        'revenue_metadata': {
            'campaign_id': 'CAMP_12345',
            'advertiser': 'TechCorp Ltd',
            'ad_format': 'video_pre_roll',
            'geographic_breakdown': {
                'US': Decimal('75.50'),
                'UK': Decimal('25.00'),
                'CA': Decimal('25.00')
            }
        }
    }


@pytest.fixture
def sample_analytics_data(sample_user_data, sample_content_data):
    """Sample analytics data for testing"""
    return {
        'id': str(uuid.uuid4()),
        'user_id': sample_user_data['id'],
        'content_id': sample_content_data['id'],
        'analytics_type': AnalyticsType.PERFORMANCE.value,
        'metric_type': MetricType.VIEWS.value,
        'value': Decimal('15000'),
        'measurement_date': date.today(),
        'time_granularity': TimeGranularity.DAILY.value,
        'platform': 'youtube',
        'country': 'US',
        'device_type': 'mobile',
        'age_group': '25-34',
        'gender': 'mixed',
        'analytics_metadata': {
            'traffic_sources': {
                'direct': 45.2,
                'search': 32.1,
                'social': 15.8,
                'referral': 6.9
            },
            'engagement_metrics': {
                'avg_watch_time': 425.5,
                'bounce_rate': 12.3,
                'click_through_rate': 8.7
            }
        }
    }


@pytest.fixture
def sample_protection_data(sample_user_data, sample_content_data, sample_fingerprint_data):
    """Sample protection data for testing"""
    return {
        'id': str(uuid.uuid4()),
        'user_id': sample_user_data['id'],
        'content_id': sample_content_data['id'],
        'fingerprint_id': sample_fingerprint_data['id'],
        'protection_type': ProtectionType.COPYRIGHT.value,
        'violation_type': ViolationType.UNAUTHORIZED_COPY.value,
        'severity_level': SeverityLevel.HIGH.value,
        'detected_url': 'https://pirate-site.com/stolen-content',
        'detected_platform': 'unknown_platform',
        'similarity_score': Decimal('96.8'),
        'status': ProtectionStatus.CONFIRMED.value,
        'evidence_collected': True,
        'dmca_sent': True,
        'legal_action_taken': False,
        'protection_metadata': {
            'detection_method': 'fingerprint_match',
            'detection_confidence': 96.8,
            'evidence_urls': [
                'https://evidence.storage/screenshot1.png',
                'https://evidence.storage/video_excerpt.mp4'
            ],
            'legal_contacts': {
                'platform_email': 'dmca@pirate-site.com',
                'hosting_provider': 'BadHost Inc'
            }
        }
    }


@pytest.fixture
def sample_licensing_data(sample_user_data, sample_content_data):
    """Sample licensing data for testing"""
    return {
        'id': str(uuid.uuid4()),
        'user_id': sample_user_data['id'],
        'content_id': sample_content_data['id'],
        'license_type': LicenseType.COMMERCIAL.value,
        'license_category': LicenseCategory.MEDIA_PRODUCTION.value,
        'usage_type': UsageType.COMMERCIAL_USE.value,
        'licensee_name': 'MediaPro Productions LLC',
        'licensee_email': 'licensing@mediapro.com',
        'license_fee': Decimal('2500.00'),
        'royalty_percentage': Decimal('15.0'),
        'currency': 'USD',
        'status': LicenseStatus.ACTIVE.value,
        'usage_limit': 100000,
        'territory': 'worldwide',
        'contract_metadata': {
            'usage_restrictions': [
                'No modification without written consent',
                'Attribution required',
                'No sublicensing'
            ],
            'payment_terms': {
                'upfront_fee': Decimal('2500.00'),
                'royalty_rate': 15.0,
                'payment_schedule': 'quarterly'
            },
            'territory_details': {
                'included_countries': ['US', 'UK', 'CA', 'AU'],
                'excluded_regions': []
            }
        }
    }


@pytest.fixture
def create_test_user(db_session, sample_user_data):
    """Create a test user in database"""
    def _create_user(**overrides):
        data = {**sample_user_data, **overrides}
        user = UserModel(**data)
        db_session.add(user)
        db_session.commit()
        return user
    return _create_user


@pytest.fixture
def create_test_content(db_session, sample_content_data):
    """Create test content in database"""
    def _create_content(**overrides):
        data = {**sample_content_data, **overrides}
        content = ContentModel(**data)
        db_session.add(content)
        db_session.commit()
        return content
    return _create_content


@pytest.fixture
def full_test_dataset(db_session, sample_user_data, sample_content_data, 
                      sample_fingerprint_data, sample_revenue_data,
                      sample_analytics_data, sample_protection_data,
                      sample_licensing_data):
    """Create complete test dataset with all related models"""
    
    # Create user
    user = UserModel(**sample_user_data)
    db_session.add(user)
    db_session.flush()
    
    # Create content
    content = ContentModel(**sample_content_data)
    db_session.add(content)
    db_session.flush()
    
    # Create fingerprint
    fingerprint = FingerprintModel(**sample_fingerprint_data)
    db_session.add(fingerprint)
    db_session.flush()
    
    # Create revenue
    revenue = RevenueModel(**sample_revenue_data)
    db_session.add(revenue)
    db_session.flush()
    
    # Create analytics
    analytics = AnalyticsModel(**sample_analytics_data)
    db_session.add(analytics)
    db_session.flush()
    
    # Create protection
    protection = ProtectionModel(**sample_protection_data)
    db_session.add(protection)
    db_session.flush()
    
    # Create licensing
    licensing = LicensingModel(**sample_licensing_data)
    db_session.add(licensing)
    db_session.flush()
    
    db_session.commit()
    
    return {
        'user': user,
        'content': content,
        'fingerprint': fingerprint,
        'revenue': revenue,
        'analytics': analytics,
        'protection': protection,
        'licensing': licensing
    }


class TestHelpers:
    """Helper utilities for testing"""
    
    @staticmethod
    def assert_model_fields(model_instance, expected_fields: Dict[str, Any]):
        """Assert that model instance has expected field values"""
        for field_name, expected_value in expected_fields.items():
            actual_value = getattr(model_instance, field_name)
            assert actual_value == expected_value, (
                f"Field {field_name}: expected {expected_value}, got {actual_value}"
            )
    
    @staticmethod
    def assert_timestamps_valid(model_instance):
        """Assert that model timestamps are valid"""
        now = datetime.utcnow()
        
        if hasattr(model_instance, 'created_at') and model_instance.created_at:
            assert model_instance.created_at <= now
        
        if hasattr(model_instance, 'updated_at') and model_instance.updated_at:
            assert model_instance.updated_at <= now
            
            if hasattr(model_instance, 'created_at') and model_instance.created_at:
                assert model_instance.updated_at >= model_instance.created_at
    
    @staticmethod
    def create_uuid() -> str:
        """Generate UUID for testing"""
        return str(uuid.uuid4())
    
    @staticmethod
    def create_future_date(days: int = 30) -> date:
        """Create future date for testing"""
        return date.today() + timedelta(days=days)
    
    @staticmethod
    def create_past_date(days: int = 30) -> date:
        """Create past date for testing"""
        return date.today() - timedelta(days=days)


@pytest.fixture
def test_helpers():
    """Provide test helper utilities"""
    return TestHelpers


# Pytest markers for organizing tests
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "model: Model-specific tests")
    config.addinivalue_line("markers", "relationship: Relationship tests")
    config.addinivalue_line("markers", "validation: Validation tests")
    config.addinivalue_line("markers", "performance: Performance tests")


# Global test constants
TEST_CONSTANTS = {
    'DEFAULT_USER_ID': '00000000-0000-0000-0000-000000000001',
    'DEFAULT_CONTENT_ID': '00000000-0000-0000-0000-000000000002',
    'TEST_EMAIL': 'test@example.com',
    'TEST_USERNAME': 'testuser',
    'TEST_DOMAIN': 'example.com',
    'MAX_STRING_LENGTH': 500,
    'DECIMAL_PLACES': 2,
    'DEFAULT_CURRENCY': 'USD',
    'DEFAULT_COUNTRY': 'US',
    'DEFAULT_TIMEZONE': 'UTC',
    'DEFAULT_LANGUAGE': 'en'
}
