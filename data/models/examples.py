"""Usage Examples for IA Influencer Agent Data Models
=================================================

Comprehensive examples demonstrating how to use all data models.
Includes common patterns, advanced queries, and best practices.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import create_engine, and_, or_, func
from sqlalchemy.orm import sessionmaker

# Import all models and utilities
from . import (
    # Models
    ContentModel, UserModel, FingerprintModel, RevenueModel,
    AnalyticsModel, ProtectionModel, LicensingModel,
    
    # Enums
    ContentType, ContentStatus, ContentVisibility,
    UserType, UserStatus, SubscriptionTier,
    FingerprintType, FingerprintAlgorithm, FingerprintStatus,
    RevenueSource, RevenueStatus, PaymentMethod,
    AnalyticsType, MetricType, TimeGranularity,
    ProtectionType, ViolationType, SeverityLevel, ProtectionStatus,
    LicenseType, LicenseCategory, UsageType, LicenseStatus,
    
    # Utilities
    ModelManager, ValidationResult, validate_user, validate_content
)


def example_database_setup():
    """Example: Set up database connection and session"""    
    # Create engine (using SQLite for example)
    engine = create_engine('sqlite:///ia_influencer.db', echo=True)
    
    # Create session factory
    SessionLocal = sessionmaker(bind=engine)
    
    # Create all tables
    from .content_model import Base
    Base.metadata.create_all(engine)
    
    # Create session
    session = SessionLocal()
    
    return engine, session


def example_create_user():
    """Example: Create a new user with validation"""    
    # User data
    user_data = {
        'id': str(uuid.uuid4()),
        'username': 'tech_creator_2025',
        'email': 'creator@techcontent.com',
        'password_hash': 'hashed_password_here',
        'first_name': 'Alex',
        'last_name': 'Johnson',
        'display_name': 'Tech Creator',
        'bio': 'Professional technology content creator and educator',
        'user_type': UserType.CREATOR.value,
        'subscription_tier': SubscriptionTier.PREMIUM.value,
        'status': UserStatus.ACTIVE.value,
        'is_verified': True,
        'phone_number': '+1234567890',
        'country': 'US',
        'timezone': 'America/New_York',
        'language': 'en',
        'date_of_birth': date(1990, 5, 15),
        'profile_metadata': {
            'social_links': {
                'youtube': 'https://youtube.com/@techcreator',
                'instagram': '@techcreator',
                'tiktok': '@techcreator',
                'linkedin': 'linkedin.com/in/alexjohnson'
            },
            'content_categories': ['technology', 'education', 'programming'],
            'preferred_platforms': ['youtube', 'instagram', 'linkedin'],
            'monetization_enabled': True,
            'content_protection_level': 'high'
        },
        'subscription_start_date': date.today(),
        'email_verified_at': datetime.utcnow(),
        'last_login_at': datetime.utcnow()
    }
    
    # Validate user data
    validation_result = validate_user(user_data)
    if not validation_result.is_valid:
        print("Validation errors:", validation_result.get_error_messages())
        return None
    
    # Create user instance
    user = UserModel(**user_data)
    
    print(f"Created user: {user.display_name} ({user.username})")
    return user


def example_create_content(user_id: str):
    """Example: Create video content with comprehensive metadata"""    
    content_data = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'title': 'Advanced Python Tutorial: Machine Learning Fundamentals',
        'description': 'Comprehensive guide to machine learning with Python, covering algorithms, implementation, and real-world applications.',
        'content_type': ContentType.VIDEO.value,
        'status': ContentStatus.PUBLISHED.value,
        'visibility': ContentVisibility.PUBLIC.value,
        'duration_seconds': 3600,  # 1 hour
        'file_size_bytes': 1073741824,  # 1GB
        'format': 'mp4',
        'resolution': '1920x1080',
        'original_url': 'https://storage.example.com/videos/python-ml-tutorial.mp4',
        'thumbnail_url': 'https://cdn.example.com/thumbnails/python-ml-thumb.jpg',
        'view_count': 25000,
        'like_count': 2100,
        'comment_count': 185,
        'share_count': 420,
        'download_count': 150,
        'watch_time_total_minutes': 58000,
        'engagement_rate': Decimal('8.4'),
        'revenue_total': Decimal('1250.75'),
        'published_at': datetime.utcnow(),
        'content_metadata': {
            'tags': ['Python', 'Machine Learning', 'Tutorial', 'Programming', 'AI'],
            'category': 'Education',
            'language': 'en',
            'subtitles_available': True,
            'chapters': [
                {'title': 'Introduction', 'start_time': 0, 'end_time': 300},
                {'title': 'Setup Environment', 'start_time': 300, 'end_time': 900},
                {'title': 'Basic Algorithms', 'start_time': 900, 'end_time': 2100},
                {'title': 'Advanced Techniques', 'start_time': 2100, 'end_time': 3000},
                {'title': 'Real-world Example', 'start_time': 3000, 'end_time': 3600}
            ],
            'difficulty_level': 'intermediate',
            'prerequisites': ['Basic Python knowledge', 'Mathematics fundamentals'],
            'learning_objectives': [
                'Understand ML algorithms',
                'Implement models in Python',
                'Apply to real-world problems'
            ],
            'quality_score': 95,
            'encoding_settings': {
                'video_codec': 'H.264',
                'audio_codec': 'AAC',
                'bitrate': '5000kbps',
                'framerate': '30fps'
            }
        },
        'seo_metadata': {
            'keywords': [
                'python machine learning',
                'ml tutorial',
                'python programming',
                'data science',
                'artificial intelligence'
            ],
            'meta_title': 'Advanced Python ML Tutorial - Complete Guide to Machine Learning',
            'meta_description': 'Master machine learning with Python in this comprehensive tutorial covering algorithms, implementation, and real-world applications.',
            'canonical_url': 'https://techcreator.com/tutorials/python-machine-learning',
            'structured_data': {
                '@type': 'VideoObject',
                'name': 'Advanced Python Tutorial: Machine Learning Fundamentals',
                'description': 'Comprehensive guide to machine learning with Python',
                'duration': 'PT1H',
                'uploadDate': datetime.utcnow().isoformat()
            }
        },
        'platform_data': {
            'youtube': {
                'video_id': 'dQw4w9WgXcQ',
                'views': 25000,
                'likes': 2100,
                'dislikes': 45,
                'comments': 185,
                'subscribers_gained': 250
            },
            'instagram': {
                'post_id': 'CX1234567890',
                'views': 12000,
                'likes': 980,
                'saves': 150,
                'shares': 85
            },
            'linkedin': {
                'post_id': 'urn:li:activity:7123456789',
                'views': 8500,
                'likes': 420,
                'comments': 65,
                'shares': 95
            }
        }
    }
    
    # Validate content data
    validation_result = validate_content(content_data)
    if not validation_result.is_valid:
        print("Validation errors:", validation_result.get_error_messages())
        return None
    
    # Create content instance
    content = ContentModel(**content_data)
    
    print(f"Created content: {content.title}")
    return content


def example_create_fingerprint(content_id: str):
    """Example: Create content fingerprint for protection"""    
    fingerprint_data = {
        'id': str(uuid.uuid4()),
        'content_id': content_id,
        'fingerprint_type': FingerprintType.VIDEO.value,
        'algorithm': FingerprintAlgorithm.PERCEPTUAL_HASH.value,
        'hash_value': 'a1b2c3d4e5f67890123456789abcdef0123456789abcdef',
        'confidence_score': Decimal('96.8'),
        'status': FingerprintStatus.ACTIVE.value,
        'processing_time_ms': 3500,
        'algorithm_version': '2.1.0',
        'created_at': datetime.utcnow(),
        'fingerprint_metadata': {
            'video_features': {
                'duration': 3600,
                'resolution': '1920x1080',
                'framerate': 30,
                'total_frames': 108000
            },
            'extracted_features': {
                'color_histogram': [0.25, 0.35, 0.40],
                'edge_density': 0.78,
                'motion_vectors': [1.2, -0.8, 2.1],
                'audio_fingerprint': 'xyz789abc123def456'
            },
            'segment_hashes': [
                {'start_time': 0, 'end_time': 300, 'hash': 'hash1'},
                {'start_time': 300, 'end_time': 600, 'hash': 'hash2'},
                # More segments...
            ]
        }
    }
    
    fingerprint = FingerprintModel(**fingerprint_data)
    
    print(f"Created fingerprint for content with confidence: {fingerprint.confidence_score}%")
    return fingerprint


def example_create_revenue_record(user_id: str, content_id: str):
    """Example: Create revenue record from YouTube ads"""    
    revenue_data = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'content_id': content_id,
        'revenue_source': RevenueSource.YOUTUBE_ADS.value,
        'gross_amount': Decimal('325.50'),
        'platform_fee': Decimal('48.83'),
        'net_amount': Decimal('276.67'),
        'currency': 'USD',
        'status': RevenueStatus.COMPLETED.value,
        'payment_method': PaymentMethod.BANK_TRANSFER.value,
        'transaction_reference': 'YT_AD_20250115_001',
        'transaction_date': datetime.utcnow() - timedelta(days=1),
        'payment_date': datetime.utcnow(),
        'views_count': 25000,
        'cpm': Decimal('13.02'),
        'cpc': Decimal('0.65'),
        'country': 'US',
        'device_type': 'mixed',
        'created_at': datetime.utcnow(),
        'revenue_metadata': {
            'campaign_details': {
                'campaign_id': 'CAMP_YT_20250115',
                'advertiser': 'TechCorp Inc.',
                'ad_format': 'video_pre_roll',
                'category': 'technology'
            },
            'geographic_breakdown': {
                'US': Decimal('195.30'),
                'UK': Decimal('65.10'),
                'CA': Decimal('32.55'),
                'AU': Decimal('32.55')
            },
            'device_breakdown': {
                'mobile': Decimal('162.75'),
                'desktop': Decimal('130.20'),
                'tablet': Decimal('32.55')
            },
            'age_demographics': {
                '18-24': Decimal('65.10'),
                '25-34': Decimal('130.20'),
                '35-44': Decimal('97.65'),
                '45+': Decimal('32.55')
            }
        }
    }
    
    revenue = RevenueModel(**revenue_data)
    
    print(f"Created revenue record: ${revenue.net_amount} from {revenue.revenue_source}")
    return revenue


def example_create_analytics_record(user_id: str, content_id: str):
    """Example: Create analytics record for performance tracking"""    
    analytics_data = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'content_id': content_id,
        'analytics_type': AnalyticsType.PERFORMANCE.value,
        'metric_type': MetricType.ENGAGEMENT_RATE.value,
        'value': Decimal('8.4'),
        'measurement_date': date.today(),
        'time_granularity': TimeGranularity.DAILY.value,
        'platform': 'youtube',
        'country': 'US',
        'device_type': 'mobile',
        'age_group': '25-34',
        'gender': 'mixed',
        'created_at': datetime.utcnow(),
        'analytics_metadata': {
            'traffic_sources': {
                'search': 42.5,
                'direct': 28.3,
                'social_media': 18.7,
                'referral': 10.5
            },
            'engagement_breakdown': {
                'likes': 2100,
                'comments': 185,
                'shares': 420,
                'saves': 150,
                'click_through_rate': 8.4
            },
            'audience_retention': {
                'average_view_duration': 2520,  # seconds
                'retention_curve': [
                    {'time': 0, 'retention': 100},
                    {'time': 300, 'retention': 85},
                    {'time': 600, 'retention': 75},
                    {'time': 1800, 'retention': 60},
                    {'time': 3600, 'retention': 45}
                ]
            },
            'conversion_metrics': {
                'subscriber_conversion_rate': 1.0,
                'click_to_website_rate': 3.2,
                'social_follow_rate': 2.8
            }
        }
    }
    
    analytics = AnalyticsModel(**analytics_data)
    
    print(f"Created analytics record: {analytics.metric_type} = {analytics.value}")
    return analytics


def example_create_protection_alert(user_id: str, content_id: str, fingerprint_id: str):
    """Example: Create content protection alert for copyright violation"""    
    protection_data = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'content_id': content_id,
        'fingerprint_id': fingerprint_id,
        'protection_type': ProtectionType.COPYRIGHT.value,
        'violation_type': ViolationType.UNAUTHORIZED_COPY.value,
        'severity_level': SeverityLevel.HIGH.value,
        'detected_url': 'https://pirated-content.example.com/stolen-video',
        'detected_platform': 'unauthorized_platform',
        'detected_at': datetime.utcnow() - timedelta(hours=2),
        'similarity_score': Decimal('94.7'),
        'status': ProtectionStatus.CONFIRMED.value,
        'evidence_collected': True,
        'dmca_sent': True,
        'dmca_sent_at': datetime.utcnow() - timedelta(hours=1),
        'legal_action_taken': False,
        'created_at': datetime.utcnow(),
        'protection_metadata': {
            'detection_details': {
                'detection_method': 'fingerprint_match',
                'detection_confidence': 94.7,
                'matching_segments': [
                    {'start': 0, 'end': 300, 'similarity': 96.2},
                    {'start': 600, 'end': 900, 'similarity': 93.8},
                    {'start': 1200, 'end': 1500, 'similarity': 94.1}
                ]
            },
            'evidence_package': {
                'screenshots': [
                    'https://evidence.storage/screenshot_1.png',
                    'https://evidence.storage/screenshot_2.png'
                ],
                'video_samples': [
                    'https://evidence.storage/sample_1.mp4'
                ],
                'metadata_comparison': {
                    'original_duration': 3600,
                    'copied_duration': 3580,
                    'quality_degradation': 15
                }
            },
            'legal_contacts': {
                'platform_dmca_email': 'dmca@unauthorized-platform.com',
                'hosting_provider': 'BadHost Services',
                'registrar': 'DomainCorp'
            },
            'enforcement_actions': [
                {
                    'action': 'DMCA_NOTICE',
                    'timestamp': datetime.utcnow() - timedelta(hours=1),
                    'status': 'SENT',
                    'reference': 'DMCA_20250115_001'
                }
            ]
        }
    }
    
    protection = ProtectionModel(**protection_data)
    
    print(f"Created protection alert: {protection.violation_type} detected with {protection.similarity_score}% similarity")
    return protection


def example_create_licensing_contract(user_id: str, content_id: str):
    """Example: Create commercial licensing contract"""    
    licensing_data = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'content_id': content_id,
        'license_type': LicenseType.COMMERCIAL.value,
        'license_category': LicenseCategory.MEDIA_PRODUCTION.value,
        'usage_type': UsageType.COMMERCIAL_USE.value,
        'licensee_name': 'TechEdu Productions LLC',
        'licensee_email': 'licensing@techedu.com',
        'licensee_organization': 'TechEdu Productions',
        'license_fee': Decimal('5000.00'),
        'royalty_percentage': Decimal('12.5'),
        'currency': 'USD',
        'status': LicenseStatus.ACTIVE.value,
        'start_date': date.today(),
        'end_date': date.today() + timedelta(days=365*2),  # 2 years
        'usage_limit': 500000,  # 500k views
        'territory': 'worldwide',
        'created_at': datetime.utcnow(),
        'contract_metadata': {
            'license_terms': {
                'exclusive': False,
                'transferable': False,
                'sublicense_allowed': False,
                'modification_allowed': True,
                'attribution_required': True,
                'commercial_use': True,
                'educational_use': True
            },
            'usage_restrictions': [
                'No resale or redistribution without consent',
                'Attribution must include creator name and original source',
                'Cannot be used in competing educational platforms',
                'Must maintain quality standards in derivatives'
            ],
            'payment_terms': {
                'upfront_fee': Decimal('5000.00'),
                'royalty_rate': 12.5,
                'payment_schedule': 'quarterly',
                'minimum_guarantee': Decimal('1000.00'),
                'payment_due_days': 30
            },
            'territory_details': {
                'included_regions': ['North America', 'Europe', 'Asia-Pacific'],
                'excluded_countries': [],
                'language_restrictions': []
            },
            'technical_specifications': {
                'max_resolution': '4K',
                'format_restrictions': ['mp4', 'mov', 'avi'],
                'quality_requirements': 'HD minimum'
            },
            'reporting_requirements': {
                'usage_reports': 'monthly',
                'revenue_reports': 'quarterly',
                'audience_metrics': 'optional'
            }
        }
    }
    
    licensing = LicensingModel(**licensing_data)
    
    print(f"Created licensing contract: {licensing.license_type} for ${licensing.license_fee}")
    return licensing


def example_complex_queries(session):
    """Example: Complex database queries across multiple models"""    
    print("\n=== COMPLEX QUERY EXAMPLES ===\n")
    
    # 1. Get top performing content by revenue
    print("1. Top 5 content by revenue:")
    top_content = session.query(ContentModel).order_by(
        ContentModel.revenue_total.desc()
    ).limit(5).all()
    
    for content in top_content:
        print(f"   {content.title}: ${content.revenue_total}")
    
    # 2. Get users with protection alerts
    print("\n2. Users with active protection alerts:")
    users_with_alerts = session.query(UserModel).join(ProtectionModel).filter(
        ProtectionModel.status.in_([
            ProtectionStatus.DETECTED.value,
            ProtectionStatus.INVESTIGATING.value,
            ProtectionStatus.CONFIRMED.value
        ])
    ).distinct().all()
    
    for user in users_with_alerts:
        alert_count = session.query(ProtectionModel).filter(
            ProtectionModel.user_id == user.id,
            ProtectionModel.status.in_([
                ProtectionStatus.DETECTED.value,
                ProtectionStatus.INVESTIGATING.value,
                ProtectionStatus.CONFIRMED.value
            ])
        ).count()
        print(f"   {user.display_name}: {alert_count} active alerts")
    
    # 3. Revenue summary by platform
    print("\n3. Revenue by platform (last 30 days):")
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    revenue_by_platform = session.query(
        RevenueModel.revenue_source,
        func.sum(RevenueModel.net_amount).label('total_revenue'),
        func.count(RevenueModel.id).label('transaction_count')
    ).filter(
        RevenueModel.transaction_date >= thirty_days_ago,
        RevenueModel.status == RevenueStatus.COMPLETED.value
    ).group_by(RevenueModel.revenue_source).all()
    
    for platform, total, count in revenue_by_platform:
        print(f"   {platform}: ${total} ({count} transactions)")
    
    # 4. Content engagement analysis
    print("\n4. Content engagement analysis:")
    engagement_stats = session.query(
        ContentModel.content_type,
        func.avg(ContentModel.engagement_rate).label('avg_engagement'),
        func.avg(ContentModel.view_count).label('avg_views'),
        func.count(ContentModel.id).label('content_count')
    ).filter(
        ContentModel.status == ContentStatus.PUBLISHED.value,
        ContentModel.is_deleted == False
    ).group_by(ContentModel.content_type).all()
    
    for content_type, avg_engagement, avg_views, count in engagement_stats:
        print(f"   {content_type}: {avg_engagement:.2f}% engagement, {avg_views:.0f} avg views ({count} pieces)")
    
    # 5. Premium users performance
    print("\n5. Premium vs Free users comparison:")
    user_performance = session.query(
        UserModel.subscription_tier,
        func.count(ContentModel.id).label('content_count'),
        func.avg(ContentModel.revenue_total).label('avg_revenue'),
        func.sum(ContentModel.view_count).label('total_views')
    ).join(ContentModel).filter(
        ContentModel.status == ContentStatus.PUBLISHED.value,
        ContentModel.is_deleted == False
    ).group_by(UserModel.subscription_tier).all()
    
    for tier, content_count, avg_revenue, total_views in user_performance:
        print(f"   {tier}: {content_count} content, ${avg_revenue:.2f} avg revenue, {total_views} total views")


def example_model_manager_usage():
    """Example: Using ModelManager utility"""    
    print("\n=== MODEL MANAGER EXAMPLES ===\n")
    
    from .index import model_manager
    
    # Get model information
    print("1. Available models:")
    for model_name in model_manager.get_all_model_names():
        print(f"   - {model_name}")
    
    # Get model details
    print("\n2. User model information:")
    user_info = model_manager.get_model_info('UserModel')
    print(f"   Table: {user_info.get('table_name')}")
    print(f"   Attributes: {len(user_info.get('attributes', {}))} columns")
    
    # Validate sample data
    print("\n3. Data validation example:")
    sample_user_data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'password_hash': 'hashed_password'
    }
    
    validation_result = model_manager.validate_model_data('UserModel', sample_user_data)
    print(f"   Valid: {validation_result['valid']}")
    if validation_result['errors']:
        print(f"   Errors: {validation_result['errors']}")


def run_all_examples():
    """Run all examples"""    
    print("IA INFLUENCER AGENT - DATA MODELS EXAMPLES")
    print("=" * 50)
    
    # Setup database
    print("\n1. Setting up database...")
    engine, session = example_database_setup()
    
    # Create sample data
    print("\n2. Creating sample user...")
    user = example_create_user()
    session.add(user)
    session.flush()
    
    print("\n3. Creating sample content...")
    content = example_create_content(user.id)
    session.add(content)
    session.flush()
    
    print("\n4. Creating content fingerprint...")
    fingerprint = example_create_fingerprint(content.id)
    session.add(fingerprint)
    session.flush()
    
    print("\n5. Creating revenue record...")
    revenue = example_create_revenue_record(user.id, content.id)
    session.add(revenue)
    session.flush()
    
    print("\n6. Creating analytics record...")
    analytics = example_create_analytics_record(user.id, content.id)
    session.add(analytics)
    session.flush()
    
    print("\n7. Creating protection alert...")
    protection = example_create_protection_alert(user.id, content.id, fingerprint.id)
    session.add(protection)
    session.flush()
    
    print("\n8. Creating licensing contract...")
    licensing = example_create_licensing_contract(user.id, content.id)
    session.add(licensing)
    session.flush()
    
    # Commit all changes
    session.commit()
    
    # Run complex queries
    example_complex_queries(session)
    
    # Model manager examples
    example_model_manager_usage()
    
    # Cleanup
    session.close()
    
    print("\n" + "=" * 50)
    print("All examples completed successfully!")


if __name__ == "__main__":
    run_all_examples()
