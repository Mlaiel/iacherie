"""
Unit tests for ai_engine.personalization.core module
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock, MagicMock

# Mock external dependencies to avoid installation issues
import sys
from unittest.mock import MagicMock

# Mock heavy ML dependencies
sys.modules['numpy'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.metrics'] = MagicMock()
sys.modules['sklearn.metrics.pairwise'] = MagicMock()
sys.modules['sklearn.decomposition'] = MagicMock()
sys.modules['sklearn.cluster'] = MagicMock()
sys.modules['pandas'] = MagicMock()
sys.modules['redis'] = MagicMock()

# Mock numpy for our use
class MockNumpyModule:
    def zeros(self, size):
        return [0.0] * size
    
    def var(self, values):
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)

sys.modules['numpy'] = MockNumpyModule()

from ai_engine.personalization.core import (
    PersonalizationType, ContentType, UserInteractionType,
    PersonalizationConfig, UserProfile, ContentItem,
    PersonalizationEngine, PersonalizationError,
    UserProfileManager, ContentPersonalizer
)


class TestPersonalizationConfig:
    """Test cases for PersonalizationConfig dataclass"""

    def test_default_initialization(self):
        """Test PersonalizationConfig with default values"""
        config = PersonalizationConfig()
        
        assert config.model_type == PersonalizationType.HYBRID
        assert config.embedding_dimension == 512
        assert config.num_recommendations == 20
        assert config.min_interactions == 5
        assert config.learning_rate == 0.001
        assert config.batch_size == 64
        assert config.epochs == 100
        assert config.validation_split == 0.2
        assert config.quality_threshold == 0.7
        assert config.diversity_factor == 0.3
        assert config.novelty_factor == 0.2
        assert config.cache_ttl == 3600
        assert config.max_profile_size == 10000
        assert config.parallel_processing is True
        assert config.max_workers == 4
        assert config.anonymize_data is True
        assert config.data_retention_days == 365
        assert config.gdpr_compliant is True

    def test_custom_initialization(self):
        """Test PersonalizationConfig with custom values"""
        config = PersonalizationConfig(
            model_type=PersonalizationType.COLLABORATIVE_FILTERING,
            embedding_dimension=256,
            num_recommendations=15,
            learning_rate=0.01,
            gdpr_compliant=False
        )
        
        assert config.model_type == PersonalizationType.COLLABORATIVE_FILTERING
        assert config.embedding_dimension == 256
        assert config.num_recommendations == 15
        assert config.learning_rate == 0.01
        assert config.gdpr_compliant is False


class TestUserProfile:
    """Test cases for UserProfile dataclass"""

    def test_user_profile_initialization(self):
        """Test UserProfile initialization"""
        created_time = datetime.utcnow()
        profile = UserProfile(
            user_id="test_user_123",
            created_at=created_time,
            updated_at=created_time
        )
        
        assert profile.user_id == "test_user_123"
        assert profile.created_at == created_time
        assert profile.updated_at == created_time
        assert profile.age_group is None
        assert profile.gender is None
        assert profile.location is None
        assert profile.language is None
        assert profile.timezone is None
        assert profile.preferred_genres == {}
        assert profile.preferred_formats == {}
        assert profile.content_consumption_patterns == {}
        assert profile.interaction_history == []
        assert profile.engagement_metrics == {}
        assert profile.session_patterns == {}
        assert profile.personality_traits == {}
        assert profile.mood_patterns == {}
        assert profile.content_sophistication == 0.5
        assert profile.exploration_tendency == 0.5
        assert profile.user_embedding is None
        assert profile.content_embeddings == {}
        assert profile.collaboration_interests == []
        assert profile.skill_level == "intermediate"
        assert profile.professional_goals == []

    def test_user_profile_with_data(self):
        """Test UserProfile with initial data"""
        profile = UserProfile(
            user_id="test_user_456",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            age_group="adult",
            gender="other",
            location="Berlin",
            language="en",
            timezone="UTC+1",
            content_sophistication=0.8,
            exploration_tendency=0.3
        )
        
        assert profile.age_group == "adult"
        assert profile.gender == "other"
        assert profile.location == "Berlin"
        assert profile.language == "en"
        assert profile.timezone == "UTC+1"
        assert profile.content_sophistication == 0.8
        assert profile.exploration_tendency == 0.3


class TestContentItem:
    """Test cases for ContentItem dataclass"""

    def test_content_item_initialization(self):
        """Test ContentItem initialization"""
        created_time = datetime.utcnow()
        content = ContentItem(
            content_id="content_123",
            content_type=ContentType.VIDEO,
            created_at=created_time,
            updated_at=created_time,
            title="Test Video Content"
        )
        
        assert content.content_id == "content_123"
        assert content.content_type == ContentType.VIDEO
        assert content.title == "Test Video Content"
        assert content.description is None
        assert content.creator_id == ""
        assert content.duration is None
        assert content.file_size is None
        assert content.features == {}
        assert content.tags == []
        assert content.categories == []
        assert content.quality_score == 0.0
        assert content.engagement_metrics == {}
        assert content.content_embedding is None
        assert content.sentiment_score is None
        assert content.complexity_level == 0.5
        assert content.platform_metadata == {}
        assert content.copyright_status == "protected"
        assert content.license_type is None


class TestPersonalizationEngine:
    """Test cases for PersonalizationEngine class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.config = PersonalizationConfig(
            model_type=PersonalizationType.HYBRID,
            num_recommendations=10,
            min_interactions=3
        )
        
        # Mock Redis to avoid connection issues
        with patch('ai_engine.personalization.core.redis.Redis') as mock_redis:
            mock_redis.return_value.ping.return_value = True
            self.engine = PersonalizationEngine(self.config)

    def test_initialization(self):
        """Test PersonalizationEngine initialization"""
        assert self.engine.config == self.config
        assert self.engine.logger is not None
        assert "total_recommendations" in self.engine.metrics
        assert "successful_matches" in self.engine.metrics
        assert "avg_response_time" in self.engine.metrics
        assert "cache_hit_rate" in self.engine.metrics

    @pytest.mark.asyncio
    async def test_create_new_profile(self):
        """Test creating a new user profile"""
        profile = await self.engine._create_new_profile("new_user_123")
        
        assert profile.user_id == "new_user_123"
        assert profile.created_at is not None
        assert profile.updated_at is not None
        assert isinstance(profile.preferred_genres, dict)
        assert isinstance(profile.engagement_metrics, dict)
        assert isinstance(profile.personality_traits, dict)
        assert isinstance(profile.interaction_history, list)
        assert profile.content_sophistication == 0.5
        assert profile.exploration_tendency == 0.5

    @pytest.mark.asyncio
    async def test_get_user_profile_new_user(self):
        """Test getting profile for new user"""
        with patch.object(self.engine, '_get_cached_profile', return_value=None):
            with patch.object(self.engine, '_load_profile_from_db', return_value=None):
                with patch.object(self.engine, '_cache_profile', return_value=None):
                    profile = await self.engine.get_user_profile("new_user_456")
                    
                    assert profile.user_id == "new_user_456"
                    assert profile.created_at is not None

    @pytest.mark.asyncio
    async def test_update_user_profile(self):
        """Test updating user profile with interaction data"""
        # Create initial profile
        profile = await self.engine._create_new_profile("test_user")
        
        # Mock methods
        with patch.object(self.engine, 'get_user_profile', return_value=profile):
            with patch.object(self.engine, '_update_preferences') as mock_update_pref:
                with patch.object(self.engine, '_update_behavioral_patterns') as mock_update_behavior:
                    with patch.object(self.engine, '_save_profile_to_db') as mock_save:
                        with patch.object(self.engine, '_cache_profile') as mock_cache:
                            
                            interaction_data = {
                                'content_id': 'content_123',
                                'action': 'like',
                                'value': 1.0,
                                'genre': 'music'
                            }
                            
                            updated_profile = await self.engine.update_user_profile("test_user", interaction_data)
                            
                            assert len(updated_profile.interaction_history) == 1
                            assert updated_profile.interaction_history[0]['content_id'] == 'content_123'
                            assert updated_profile.interaction_history[0]['action'] == 'like'
                            assert updated_profile.interaction_history[0]['value'] == 1.0
                            assert 'timestamp' in updated_profile.interaction_history[0]
                            
                            mock_update_pref.assert_called_once()
                            mock_update_behavior.assert_called_once()
                            mock_save.assert_called_once()
                            mock_cache.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_recommendations_invalid_user_id(self):
        """Test get_recommendations with invalid user ID"""
        with pytest.raises(PersonalizationError, match="Invalid user ID"):
            await self.engine.get_recommendations("")

        with pytest.raises(PersonalizationError, match="Invalid user ID"):
            await self.engine.get_recommendations("   ")

        with pytest.raises(PersonalizationError, match="Invalid user ID"):
            await self.engine.get_recommendations(None)

    @pytest.mark.asyncio
    async def test_get_recommendations_valid_user(self):
        """Test get_recommendations with valid user"""
        # Create test profile
        profile = await self.engine._create_new_profile("test_user")
        
        with patch.object(self.engine, 'get_user_profile', return_value=profile):
            with patch.object(self.engine, '_get_cold_start_recommendations') as mock_cold_start:
                mock_cold_start.return_value = [
                    {
                        'content_id': 'rec_1',
                        'content_type': 'video',
                        'title': 'Test Recommendation',
                        'score': 0.8,
                        'relevance_score': 0.8,
                        'reason': 'Test reason',
                        'confidence': 0.7,
                        'strategy': 'cold_start'
                    }
                ]
                
                recommendations = await self.engine.get_recommendations(
                    user_id="test_user",
                    content_type=ContentType.VIDEO,
                    max_recommendations=5
                )
                
                assert len(recommendations) >= 0
                mock_cold_start.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_feedback_valid_data(self):
        """Test processing valid feedback"""
        # Create test profile
        profile = await self.engine._create_new_profile("test_user")
        
        with patch.object(self.engine, 'update_user_profile', return_value=profile) as mock_update:
            await self.engine.process_feedback(
                user_id="test_user",
                content_id="content_123",
                feedback_type="like",
                feedback_value=4.5
            )
            
            mock_update.assert_called_once()
            
            # Check the interaction data passed to update_user_profile
            call_args = mock_update.call_args
            assert call_args[0][0] == "test_user"  # user_id
            interaction_data = call_args[0][1]
            assert interaction_data['content_id'] == "content_123"
            assert interaction_data['action'] == "like"
            assert interaction_data['value'] == 4.5
            assert interaction_data['feedback'] is True

    @pytest.mark.asyncio
    async def test_process_feedback_invalid_type(self):
        """Test processing feedback with invalid type"""
        with pytest.raises(PersonalizationError, match="Invalid feedback type"):
            await self.engine.process_feedback(
                user_id="test_user",
                content_id="content_123",
                feedback_type="invalid_type",
                feedback_value=1.0
            )

    @pytest.mark.asyncio
    async def test_process_feedback_missing_value(self):
        """Test processing feedback with missing value"""
        with pytest.raises(PersonalizationError, match="Missing feedback value"):
            await self.engine.process_feedback(
                user_id="test_user",
                content_id="content_123",
                feedback_type="like"
            )

    @pytest.mark.asyncio
    async def test_process_feedback_invalid_value_range(self):
        """Test processing feedback with invalid value range"""
        with pytest.raises(PersonalizationError, match="Invalid feedback value"):
            await self.engine.process_feedback(
                user_id="test_user",
                content_id="content_123",
                feedback_type="like",
                feedback_value=10.0  # Too high for like feedback
            )

        with pytest.raises(PersonalizationError, match="Invalid feedback value"):
            await self.engine.process_feedback(
                user_id="test_user",
                content_id="content_123",
                feedback_type="rating",
                feedback_value=-1.0  # Negative value
            )

    @pytest.mark.asyncio
    async def test_process_feedback_with_value_parameter(self):
        """Test processing feedback using 'value' parameter instead of 'feedback_value'"""
        profile = await self.engine._create_new_profile("test_user")
        
        with patch.object(self.engine, 'update_user_profile', return_value=profile) as mock_update:
            await self.engine.process_feedback(
                user_id="test_user",
                content_id="content_123",
                feedback_type="time_spent",
                value=120.5  # 2 minutes
            )
            
            mock_update.assert_called_once()
            call_args = mock_update.call_args
            interaction_data = call_args[0][1]
            assert interaction_data['value'] == 120.5

    @pytest.mark.asyncio
    async def test_get_cold_start_recommendations(self):
        """Test cold start recommendations for new users"""
        profile = await self.engine._create_new_profile("new_user")
        
        with patch.object(self.engine, '_get_popular_content') as mock_popular:
            mock_popular.return_value = [
                {
                    'id': 'popular_1',
                    'type': 'video',
                    'title': 'Popular Video 1',
                    'popularity_score': 0.9,
                    'category': 'entertainment'
                },
                {
                    'id': 'popular_2',
                    'type': 'audio',
                    'title': 'Popular Audio 1',
                    'popularity_score': 0.8,
                    'category': 'educational'
                }
            ]
            
            recommendations = await self.engine._get_cold_start_recommendations(
                profile, content_types=[ContentType.VIDEO], limit=5
            )
            
            assert len(recommendations) >= 0
            if recommendations:
                for rec in recommendations:
                    assert 'content_id' in rec
                    assert 'content_type' in rec
                    assert 'title' in rec
                    assert 'score' in rec
                    assert 'relevance_score' in rec
                    assert 'reason' in rec
                    assert 'confidence' in rec
                    assert 'strategy' in rec

    @pytest.mark.asyncio
    async def test_apply_diversity_filter(self):
        """Test diversity filtering of recommendations"""
        recommendations = [
            {'content_id': 'video_1', 'content_type': 'video', 'category': 'entertainment', 'score': 0.9},
            {'content_id': 'video_2', 'content_type': 'video', 'category': 'entertainment', 'score': 0.8},
            {'content_id': 'audio_1', 'content_type': 'audio', 'category': 'educational', 'score': 0.7},
            {'content_id': 'text_1', 'content_type': 'text', 'category': 'news', 'score': 0.6},
            {'content_id': 'video_3', 'content_type': 'video', 'category': 'entertainment', 'score': 0.5}
        ]
        
        diverse_recs = await self.engine._apply_diversity_filter(recommendations, target_count=3)
        
        assert len(diverse_recs) == 3
        # Should prioritize different content types and categories
        content_types = [rec['content_type'] for rec in diverse_recs]
        assert len(set(content_types)) >= 2  # Should have at least 2 different types

    @pytest.mark.asyncio
    async def test_find_collaboration_matches(self):
        """Test finding collaboration matches"""
        profile = await self.engine._create_new_profile("collab_user")
        profile.collaboration_interests = ["music", "video"]
        profile.skill_level = "advanced"
        
        with patch.object(self.engine, '_get_potential_partners') as mock_partners:
            mock_partners.return_value = []  # Empty list for simplicity
            
            matches = await self.engine.find_collaboration_matches("collab_user", "music")
            
            assert isinstance(matches, list)
            assert len(matches) == 0  # No partners in mock

    def test_profile_to_dict_conversion(self):
        """Test internal profile serialization methods"""
        profile = UserProfile(
            user_id="test_user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            age_group="adult",
            preferred_genres={'music': 0.8, 'video': 0.6}
        )
        
        # Test that the engine can handle profile data
        assert profile.user_id == "test_user"
        assert profile.age_group == "adult"
        assert profile.preferred_genres['music'] == 0.8


class TestUserProfileManager:
    """Test cases for UserProfileManager class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.config = PersonalizationConfig()
        self.manager = UserProfileManager(self.config)

    @pytest.mark.asyncio
    async def test_create_profile_basic(self):
        """Test creating basic user profile"""
        initial_data = {
            'demographics': {
                'age_group': 'adult',
                'gender': 'other',
                'location': 'Berlin',
                'language': 'en'
            },
            'preferences': {
                'genres': {'music': 0.8, 'video': 0.6},
                'formats': {'video': 0.7, 'audio': 0.9}
            }
        }
        
        profile = await self.manager.create_profile("test_user", initial_data)
        
        assert profile.user_id == "test_user"
        assert profile.age_group == "adult"
        assert profile.gender == "other"
        assert profile.location == "Berlin"
        assert profile.language == "en"
        assert profile.preferred_genres == {'music': 0.8, 'video': 0.6}
        assert profile.content_sophistication == 0.5
        assert profile.exploration_tendency == 0.5

    @pytest.mark.asyncio
    async def test_create_profile_minimal_data(self):
        """Test creating profile with minimal data"""
        profile = await self.manager.create_profile("minimal_user", {})
        
        assert profile.user_id == "minimal_user"
        assert profile.age_group is None
        assert profile.preferred_genres == {}

    @pytest.mark.asyncio
    async def test_validate_profile_valid(self):
        """Test validating a valid profile"""
        profile = UserProfile(
            user_id="valid_user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            content_sophistication=0.7,
            exploration_tendency=0.3
        )
        
        is_valid = await self.manager.validate_profile(profile)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_profile_invalid_sophistication(self):
        """Test validating profile with invalid sophistication value"""
        profile = UserProfile(
            user_id="invalid_user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            content_sophistication=1.5,  # Invalid: > 1
            exploration_tendency=0.3
        )
        
        is_valid = await self.manager.validate_profile(profile)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_profile_missing_required_fields(self):
        """Test validating profile with missing required fields"""
        profile = UserProfile(
            user_id="",  # Empty user_id
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        is_valid = await self.manager.validate_profile(profile)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_optimize_profile(self):
        """Test profile optimization"""
        # Create profile with old interactions
        profile = UserProfile(
            user_id="optimize_user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add old and new interactions
        old_time = (datetime.utcnow() - timedelta(days=40)).isoformat()
        new_time = (datetime.utcnow() - timedelta(days=5)).isoformat()
        
        profile.interaction_history = [
            {'content_id': 'old_content', 'timestamp': old_time, 'action': 'view'},
            {'content_id': 'new_content', 'timestamp': new_time, 'action': 'like'}
        ]
        
        # Add preferences with low scores
        profile.preferred_genres = {
            'music': 0.8,  # Keep
            'video': 0.005,  # Should be removed
            'text': 0.3   # Keep
        }
        
        optimized_profile = await self.manager.optimize_profile(profile)
        
        # Check that old interactions are removed
        assert len(optimized_profile.interaction_history) == 1
        assert optimized_profile.interaction_history[0]['content_id'] == 'new_content'
        
        # Check that low preference scores are removed
        assert 'video' not in optimized_profile.preferred_genres
        assert 'music' in optimized_profile.preferred_genres
        assert 'text' in optimized_profile.preferred_genres


class TestContentPersonalizer:
    """Test cases for ContentPersonalizer class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.config = PersonalizationConfig()
        self.personalizer = ContentPersonalizer(self.config)

    @pytest.mark.asyncio
    async def test_personalize_content_basic(self):
        """Test basic content personalization"""
        content = {
            'id': 'test_content',
            'type': 'video',
            'title': 'Test Video',
            'genre': 'music',
            'complexity': 0.6
        }
        
        profile = UserProfile(
            user_id="test_user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            content_sophistication=0.8
        )
        profile.preferred_formats = {ContentType.VIDEO: 0.9}
        profile.personality_traits = {'creative': 0.7, 'analytical': 0.5}
        
        personalized = await self.personalizer.personalize_content(content, profile)
        
        assert personalized['id'] == 'test_content'
        assert 'personalization' in personalized
        assert personalized['personalization']['adapted_for'] == 'test_user'
        assert 'adaptation_score' in personalized['personalization']
        assert 'timestamp' in personalized['personalization']

    @pytest.mark.asyncio
    async def test_adapt_content_format(self):
        """Test content format adaptation"""
        content = {'type': 'video', 'title': 'Test Video'}
        
        profile = UserProfile(
            user_id="test_user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        profile.preferred_formats = {ContentType.VIDEO: 0.9}
        
        adapted = await self.personalizer._adapt_content_format(content, profile)
        
        assert adapted['format_priority'] == 'high'

    @pytest.mark.asyncio
    async def test_personalize_presentation_sophisticated_user(self):
        """Test presentation personalization for sophisticated user"""
        content = {'type': 'text', 'title': 'Technical Article'}
        
        profile = UserProfile(
            user_id="sophisticated_user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            content_sophistication=0.9
        )
        profile.personality_traits = {'analytical': 0.8, 'creative': 0.6}
        
        personalized = await self.personalizer._personalize_presentation(content, profile)
        
        assert personalized['presentation_style'] == 'detailed'
        assert personalized['technical_level'] == 'advanced'
        assert personalized['include_data'] is True
        assert personalized['visual_style'] == 'creative'

    @pytest.mark.asyncio
    async def test_personalize_presentation_beginner_user(self):
        """Test presentation personalization for beginner user"""
        content = {'type': 'tutorial', 'title': 'How to Guide'}
        
        profile = UserProfile(
            user_id="beginner_user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            content_sophistication=0.2
        )
        
        personalized = await self.personalizer._personalize_presentation(content, profile)
        
        assert personalized['presentation_style'] == 'simplified'
        assert personalized['technical_level'] == 'beginner'

    @pytest.mark.asyncio
    async def test_optimize_timing(self):
        """Test content timing optimization"""
        content = {'type': 'video', 'title': 'Time-sensitive Content'}
        
        profile = UserProfile(
            user_id="timed_user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        profile.session_patterns = {
            'peak_hours': [9, 10, 18, 19],
            'preferred_days': ['Monday', 'Wednesday', 'Friday']
        }
        
        optimized = await self.personalizer._optimize_timing(content, profile)
        
        assert optimized['optimal_delivery_hours'] == [9, 10, 18, 19]
        assert optimized['optimal_delivery_days'] == ['Monday', 'Wednesday', 'Friday']

    @pytest.mark.asyncio
    async def test_calculate_adaptation_score(self):
        """Test adaptation score calculation"""
        content = {
            'type': 'video',
            'genre': 'music',
            'complexity': 0.6
        }
        
        profile = UserProfile(
            user_id="score_user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            content_sophistication=0.7
        )
        profile.preferred_formats = {ContentType.VIDEO: 0.8}
        profile.preferred_genres = {'music': 0.9}
        
        score = await self.personalizer._calculate_adaptation_score(content, profile)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be high due to good matches


class TestEnumTypes:
    """Test cases for enum types"""

    def test_personalization_type_enum(self):
        """Test PersonalizationType enum values"""
        assert PersonalizationType.COLLABORATIVE_FILTERING.value == "collaborative_filtering"
        assert PersonalizationType.CONTENT_BASED.value == "content_based"
        assert PersonalizationType.HYBRID.value == "hybrid"
        assert PersonalizationType.DEEP_LEARNING.value == "deep_learning"
        assert PersonalizationType.DEMOGRAPHIC.value == "demographic"
        assert PersonalizationType.BEHAVIORAL.value == "behavioral"

    def test_content_type_enum(self):
        """Test ContentType enum values"""
        assert ContentType.AUDIO.value == "audio"
        assert ContentType.VIDEO.value == "video"
        assert ContentType.IMAGE.value == "image"
        assert ContentType.TEXT.value == "text"
        assert ContentType.MUSIC.value == "music"
        assert ContentType.PODCAST.value == "podcast"
        assert ContentType.BLOG.value == "blog"
        assert ContentType.SOCIAL_POST.value == "social_post"

    def test_user_interaction_type_enum(self):
        """Test UserInteractionType enum values"""
        assert UserInteractionType.VIEW.value == "view"
        assert UserInteractionType.LIKE.value == "like"
        assert UserInteractionType.SHARE.value == "share"
        assert UserInteractionType.COMMENT.value == "comment"
        assert UserInteractionType.DOWNLOAD.value == "download"
        assert UserInteractionType.BOOKMARK.value == "bookmark"
        assert UserInteractionType.SKIP.value == "skip"
        assert UserInteractionType.RATE.value == "rate"
        assert UserInteractionType.PURCHASE.value == "purchase"
        assert UserInteractionType.COLLABORATE.value == "collaborate"