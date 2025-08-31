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
Test Data Handler Module

Tests for data processing, validation, transformation, and storage.

Author: Fahed Mlaiel (Legal Copyright)
Copyright © 2025 Fahed Mlaiel. Tous droits réservés.
Propriété intellectuelle protégée sous toutes juridictions.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime
from typing import Dict, Any, List
import tempfile
import os

from crawlers.handlers.data_handler import (
    DataTransformer,
    DataValidator,
    DataStorage,
    ContentData,
    UserData,
    PlatformData,
    ValidationSchema,
    TransformationRule,
    ValidationResult,
    StorageResult,
    CompressionType,
    EncryptionType
)


class TestContentData:
    """Test suite for ContentData model."""

    def test_content_data_creation(self):
        """Test content data object creation."""
        data = ContentData(
            content_id="test-123",
            platform="youtube",
            title="Test Video",
            description="Test Description",
            author="Test Author",
            created_at=datetime.now(),
            metadata={"duration": 300, "views": 1000}
        )
        
        assert data.content_id == "test-123"
        assert data.platform == "youtube"
        assert data.title == "Test Video"
        assert data.metadata["duration"] == 300

    def test_content_data_validation(self):
        """Test content data validation."""
        # Valid data
        valid_data = ContentData(
            content_id="valid-123",
            platform="instagram",
            title="Valid Post",
            author="valid_user"
        )
        assert valid_data.content_id == "valid-123"
        
        # Invalid data should raise validation error
        with pytest.raises(ValueError):
            ContentData(
                content_id="",  # Empty ID
                platform="instagram",
                title="Invalid Post",
                author="user"
            )

    def test_content_data_serialization(self):
        """Test content data JSON serialization."""
        data = ContentData(
            content_id="serial-123",
            platform="tiktok",
            title="Serialization Test",
            author="test_user",
            metadata={"hashtags": ["test", "serialization"]}
        )
        
        json_dict = data.to_dict()
        assert json_dict["content_id"] == "serial-123"
        assert json_dict["platform"] == "tiktok"
        assert "test" in json_dict["metadata"]["hashtags"]

    def test_content_data_from_dict(self):
        """Test content data creation from dictionary."""
        data_dict = {
            "content_id": "from-dict-123",
            "platform": "twitter",
            "title": "From Dict Test",
            "author": "dict_user",
            "created_at": "2025-01-11T10:00:00",
            "metadata": {"retweets": 50}
        }
        
        data = ContentData.from_dict(data_dict)
        assert data.content_id == "from-dict-123"
        assert data.platform == "twitter"
        assert data.metadata["retweets"] == 50


class TestUserData:
    """Test suite for UserData model."""

    def test_user_data_creation(self):
        """Test user data object creation."""
        data = UserData(
            user_id="user-123",
            username="testuser",
            display_name="Test User",
            platform="youtube",
            follower_count=1000,
            profile_data={"bio": "Test bio", "verified": True}
        )
        
        assert data.user_id == "user-123"
        assert data.username == "testuser"
        assert data.follower_count == 1000
        assert data.profile_data["verified"] is True

    def test_user_data_validation(self):
        """Test user data validation."""
        # Valid data
        valid_data = UserData(
            user_id="valid-user-123",
            username="validuser",
            platform="instagram"
        )
        assert valid_data.user_id == "valid-user-123"
        
        # Invalid username format
        with pytest.raises(ValueError):
            UserData(
                user_id="user-123",
                username="invalid username!",  # Contains invalid characters
                platform="instagram"
            )


class TestPlatformData:
    """Test suite for PlatformData model."""

    def test_platform_data_creation(self):
        """Test platform data object creation."""
        data = PlatformData(
            platform="youtube",
            api_version="v3",
            rate_limits={"requests_per_hour": 10000},
            supported_features=["videos", "channels", "playlists"],
            authentication={"type": "oauth2", "scopes": ["read"]}
        )
        
        assert data.platform == "youtube"
        assert data.api_version == "v3"
        assert "videos" in data.supported_features
        assert data.rate_limits["requests_per_hour"] == 10000


class TestValidationSchema:
    """Test suite for ValidationSchema class."""

    def test_schema_creation(self):
        """Test validation schema creation."""
        schema = ValidationSchema(
            name="content_schema",
            required_fields=["content_id", "platform", "title"],
            optional_fields=["description", "metadata"],
            field_types={
                "content_id": str,
                "platform": str,
                "title": str,
                "view_count": int
            },
            constraints={
                "content_id": {"min_length": 1, "max_length": 100},
                "platform": {"choices": ["youtube", "instagram", "tiktok"]},
                "view_count": {"min_value": 0}
            }
        )
        
        assert schema.name == "content_schema"
        assert "content_id" in schema.required_fields
        assert schema.field_types["content_id"] == str
        assert "youtube" in schema.constraints["platform"]["choices"]

    def test_schema_validation(self):
        """Test schema-based validation."""
        schema = ValidationSchema(
            name="test_schema",
            required_fields=["id", "name"],
            field_types={"id": str, "name": str, "count": int},
            constraints={
                "id": {"min_length": 1},
                "name": {"min_length": 2},
                "count": {"min_value": 0}
            }
        )
        
        # Valid data
        valid_data = {"id": "123", "name": "Test", "count": 5}
        assert schema.validate(valid_data)
        
        # Missing required field
        invalid_data = {"name": "Test"}
        assert not schema.validate(invalid_data)
        
        # Invalid type
        invalid_type_data = {"id": "123", "name": "Test", "count": "not_int"}
        assert not schema.validate(invalid_type_data)


class TestDataValidator:
    """Test suite for DataValidator class."""

    def test_validator_initialization(self):
        """Test validator setup."""
        validator = DataValidator()
        assert validator.schemas is not None
        assert len(validator.schemas) > 0

    def test_validate_content_data(self):
        """Test content data validation."""
        validator = DataValidator()
        
        # Valid content data
        valid_data = {
            "content_id": "valid-123",
            "platform": "youtube",
            "title": "Valid Video",
            "author": "valid_author",
            "view_count": 1000
        }
        
        result = validator.validate("content", valid_data)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_invalid_content_data(self):
        """Test validation with invalid content data."""
        validator = DataValidator()
        
        # Invalid content data
        invalid_data = {
            "content_id": "",  # Empty ID
            "platform": "invalid_platform",  # Not in allowed choices
            "title": "Test Video",
            "view_count": -100  # Negative count
        }
        
        result = validator.validate("content", invalid_data)
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_user_data(self):
        """Test user data validation."""
        validator = DataValidator()
        
        valid_data = {
            "user_id": "user-123",
            "username": "testuser",
            "platform": "instagram",
            "follower_count": 5000
        }
        
        result = validator.validate("user", valid_data)
        assert result.is_valid

    def test_validate_with_custom_schema(self):
        """Test validation with custom schema."""
        validator = DataValidator()
        
        custom_schema = ValidationSchema(
            name="custom_test",
            required_fields=["id", "value"],
            field_types={"id": str, "value": int},
            constraints={"value": {"min_value": 1, "max_value": 100}}
        )
        
        validator.add_schema(custom_schema)
        
        valid_data = {"id": "test", "value": 50}
        result = validator.validate("custom_test", valid_data)
        assert result.is_valid
        
        invalid_data = {"id": "test", "value": 150}  # Exceeds max
        result = validator.validate("custom_test", invalid_data)
        assert not result.is_valid

    def test_bulk_validation(self):
        """Test bulk data validation."""
        validator = DataValidator()
        
        data_list = [
            {"content_id": "1", "platform": "youtube", "title": "Video 1"},
            {"content_id": "2", "platform": "instagram", "title": "Post 2"},
            {"content_id": "", "platform": "invalid", "title": "Invalid"}  # Invalid
        ]
        
        results = validator.validate_bulk("content", data_list)
        assert len(results) == 3
        assert results[0].is_valid
        assert results[1].is_valid
        assert not results[2].is_valid


class TestTransformationRule:
    """Test suite for TransformationRule class."""

    def test_rule_creation(self):
        """Test transformation rule creation."""
        rule = TransformationRule(
            name="normalize_platform",
            source_field="platform_name",
            target_field="platform",
            transformation_func=lambda x: x.lower().strip()
        )
        
        assert rule.name == "normalize_platform"
        assert rule.source_field == "platform_name"
        assert rule.target_field == "platform"

    def test_rule_application(self):
        """Test rule application to data."""
        rule = TransformationRule(
            name="normalize_title",
            source_field="title",
            target_field="normalized_title",
            transformation_func=lambda x: x.strip().title()
        )
        
        data = {"title": "  test video title  "}
        transformed = rule.apply(data)
        
        assert transformed["normalized_title"] == "Test Video Title"
        assert "title" in transformed  # Original field preserved

    def test_conditional_rule(self):
        """Test conditional transformation rule."""
        def transform_views(value):
            if isinstance(value, str) and value.endswith('K'):
                return int(float(value[:-1]) * 1000)
            return int(value) if value else 0
        
        rule = TransformationRule(
            name="normalize_views",
            source_field="view_count",
            target_field="views",
            transformation_func=transform_views
        )
        
        data1 = {"view_count": "1.5K"}
        result1 = rule.apply(data1)
        assert result1["views"] == 1500
        
        data2 = {"view_count": "1000"}
        result2 = rule.apply(data2)
        assert result2["views"] == 1000


class TestDataTransformer:
    """Test suite for DataTransformer class."""

    def test_transformer_initialization(self):
        """Test transformer setup."""
        transformer = DataTransformer()
        assert transformer.rules is not None
        assert len(transformer.rules) >= 0

    def test_add_transformation_rule(self):
        """Test adding transformation rules."""
        transformer = DataTransformer()
        
        rule = TransformationRule(
            name="test_rule",
            source_field="input",
            target_field="output",
            transformation_func=lambda x: x.upper()
        )
        
        transformer.add_rule(rule)
        assert "test_rule" in transformer.rules

    def test_transform_content_data(self):
        """Test content data transformation."""
        transformer = DataTransformer()
        
        raw_data = {
            "id": "youtube-123",
            "snippet": {
                "title": "  Test Video  ",
                "channelTitle": "Test Channel",
                "publishedAt": "2025-01-11T10:00:00Z"
            },
            "statistics": {
                "viewCount": "1500",
                "likeCount": "75"
            }
        }
        
        transformed = transformer.transform("youtube_content", raw_data)
        
        assert "content_id" in transformed
        assert "title" in transformed
        assert "author" in transformed
        assert isinstance(transformed["view_count"], int)

    def test_transform_user_data(self):
        """Test user data transformation."""
        transformer = DataTransformer()
        
        raw_data = {
            "id": "user123",
            "username": "TestUser",
            "profile": {
                "displayName": "Test User",
                "followerCount": "5000",
                "description": "Test bio"
            }
        }
        
        transformed = transformer.transform("instagram_user", raw_data)
        
        assert "user_id" in transformed
        assert "username" in transformed
        assert "display_name" in transformed
        assert isinstance(transformed["follower_count"], int)

    def test_custom_transformation_pipeline(self):
        """Test custom transformation pipeline."""
        transformer = DataTransformer()
        
        # Add custom rules
        rules = [
            TransformationRule(
                "extract_hashtags",
                "description",
                "hashtags",
                lambda x: [tag.strip('#') for tag in x.split() if tag.startswith('#')]
            ),
            TransformationRule(
                "calculate_engagement",
                "stats",
                "engagement_rate",
                lambda stats: (stats.get("likes", 0) + stats.get("comments", 0)) / max(stats.get("views", 1), 1)
            )
        ]
        
        for rule in rules:
            transformer.add_rule(rule)
        
        data = {
            "description": "Great video! #awesome #trending #viral",
            "stats": {"views": 1000, "likes": 100, "comments": 20}
        }
        
        transformed = transformer.apply_custom_rules(data, ["extract_hashtags", "calculate_engagement"])
        
        assert "hashtags" in transformed
        assert len(transformed["hashtags"]) == 3
        assert "awesome" in transformed["hashtags"]
        assert "engagement_rate" in transformed
        assert transformed["engagement_rate"] == 0.12  # (100+20)/1000

    def test_batch_transformation(self):
        """Test batch data transformation."""
        transformer = DataTransformer()
        
        raw_data_list = [
            {"id": "1", "title": "Video 1", "views": "1000"},
            {"id": "2", "title": "Video 2", "views": "2000"},
            {"id": "3", "title": "Video 3", "views": "500"}
        ]
        
        transformed_list = transformer.transform_batch("simple_content", raw_data_list)
        
        assert len(transformed_list) == 3
        assert all("content_id" in item for item in transformed_list)
        assert all(isinstance(item["view_count"], int) for item in transformed_list)


class TestDataStorage:
    """Test suite for DataStorage class."""

    def test_storage_initialization(self):
        """Test storage setup."""
        storage = DataStorage()
        assert storage.compression_manager is not None
        assert storage.encryption_manager is not None

    @pytest.mark.asyncio
    async def test_store_content_data(self):
        """Test storing content data."""
        storage = DataStorage()
        
        content = ContentData(
            content_id="store-123",
            platform="youtube",
            title="Test Storage",
            author="test_author"
        )
        
        with patch.object(storage, '_save_to_database') as mock_save:
            mock_save.return_value = True
            
            result = await storage.store_content(content)
            
            assert result.success
            assert result.stored_id == "store-123"
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_with_compression(self):
        """Test storing data with compression."""
        storage = DataStorage()
        
        large_content = ContentData(
            content_id="compress-123",
            platform="youtube",
            title="Large Content",
            author="test_author",
            metadata={"large_data": "x" * 10000}  # Large metadata
        )
        
        with patch.object(storage.compression_manager, 'compress') as mock_compress:
            mock_compress.return_value = b"compressed_data"
            
            with patch.object(storage, '_save_to_database') as mock_save:
                mock_save.return_value = True
                
                result = await storage.store_content(
                    large_content, 
                    compression=CompressionType.GZIP
                )
                
                assert result.success
                assert result.compression_used
                mock_compress.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_with_encryption(self):
        """Test storing data with encryption."""
        storage = DataStorage()
        
        sensitive_content = ContentData(
            content_id="encrypt-123",
            platform="youtube",
            title="Sensitive Content",
            author="test_author",
            metadata={"sensitive": "personal_data"}
        )
        
        with patch.object(storage.encryption_manager, 'encrypt') as mock_encrypt:
            mock_encrypt.return_value = b"encrypted_data"
            
            with patch.object(storage, '_save_to_database') as mock_save:
                mock_save.return_value = True
                
                result = await storage.store_content(
                    sensitive_content,
                    encryption=EncryptionType.AES256
                )
                
                assert result.success
                assert result.encryption_used
                mock_encrypt.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_content_data(self):
        """Test retrieving content data."""
        storage = DataStorage()
        
        expected_content = ContentData(
            content_id="retrieve-123",
            platform="youtube",
            title="Retrieved Content",
            author="test_author"
        )
        
        with patch.object(storage, '_load_from_database') as mock_load:
            mock_load.return_value = expected_content.to_dict()
            
            content = await storage.retrieve_content("retrieve-123")
            
            assert content is not None
            assert content.content_id == "retrieve-123"
            assert content.title == "Retrieved Content"

    @pytest.mark.asyncio
    async def test_retrieve_with_decryption(self):
        """Test retrieving encrypted data."""
        storage = DataStorage()
        
        with patch.object(storage.encryption_manager, 'decrypt') as mock_decrypt:
            mock_decrypt.return_value = json.dumps({
                "content_id": "decrypt-123",
                "platform": "youtube",
                "title": "Decrypted Content",
                "author": "test_author"
            }).encode()
            
            with patch.object(storage, '_load_from_database') as mock_load:
                mock_load.return_value = {
                    "encrypted_data": b"encrypted_content",
                    "encryption_type": "AES256"
                }
                
                content = await storage.retrieve_content("decrypt-123")
                
                assert content is not None
                assert content.content_id == "decrypt-123"
                mock_decrypt.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_storage(self):
        """Test bulk data storage."""
        storage = DataStorage()
        
        contents = [
            ContentData(f"bulk-{i}", "youtube", f"Video {i}", f"author_{i}")
            for i in range(5)
        ]
        
        with patch.object(storage, '_save_batch_to_database') as mock_save_batch:
            mock_save_batch.return_value = [True] * 5
            
            results = await storage.store_batch(contents)
            
            assert len(results) == 5
            assert all(r.success for r in results)
            mock_save_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_content(self):
        """Test content searching."""
        storage = DataStorage()
        
        search_results = [
            {"content_id": "search-1", "title": "Search Result 1"},
            {"content_id": "search-2", "title": "Search Result 2"}
        ]
        
        with patch.object(storage, '_search_database') as mock_search:
            mock_search.return_value = search_results
            
            results = await storage.search_content(
                query="test search",
                filters={"platform": "youtube"},
                limit=10
            )
            
            assert len(results) == 2
            assert results[0]["content_id"] == "search-1"
            mock_search.assert_called_once()

    def test_generate_storage_key(self):
        """Test storage key generation."""
        storage = DataStorage()
        
        content = ContentData(
            content_id="key-123",
            platform="youtube",
            title="Key Test",
            author="test_author"
        )
        
        key = storage._generate_storage_key(content)
        assert "youtube" in key
        assert "key-123" in key

    def test_validate_storage_constraints(self):
        """Test storage constraint validation."""
        storage = DataStorage()
        
        # Valid content
        valid_content = ContentData(
            content_id="valid-123",
            platform="youtube",
            title="Valid Content",
            author="test_author"
        )
        
        assert storage._validate_storage_constraints(valid_content)
        
        # Invalid content (missing required fields)
        invalid_content = ContentData(
            content_id="",  # Empty ID
            platform="youtube",
            title="Invalid Content",
            author="test_author"
        )
        
        assert not storage._validate_storage_constraints(invalid_content)


class TestIntegration:
    """Integration tests for data handling system."""

    @pytest.mark.asyncio
    async def test_complete_data_processing_pipeline(self):
        """Test complete data processing from raw to stored."""
        validator = DataValidator()
        transformer = DataTransformer()
        storage = DataStorage()
        
        # Raw YouTube API response
        raw_data = {
            "id": "pipeline-123",
            "snippet": {
                "title": "  Integration Test Video  ",
                "channelTitle": "Test Channel",
                "description": "Test description #integration #test",
                "publishedAt": "2025-01-11T10:00:00Z"
            },
            "statistics": {
                "viewCount": "5000",
                "likeCount": "250",
                "commentCount": "50"
            }
        }
        
        # Transform raw data
        transformed = transformer.transform("youtube_content", raw_data)
        
        # Validate transformed data
        validation_result = validator.validate("content", transformed)
        assert validation_result.is_valid
        
        # Create content object
        content = ContentData.from_dict(transformed)
        
        # Store content
        with patch.object(storage, '_save_to_database') as mock_save:
            mock_save.return_value = True
            
            storage_result = await storage.store_content(content)
            
            assert storage_result.success
            assert storage_result.stored_id == "pipeline-123"

    @pytest.mark.asyncio
    async def test_error_handling_in_pipeline(self):
        """Test error handling throughout the data pipeline."""
        validator = DataValidator()
        transformer = DataTransformer()
        storage = DataStorage()
        
        # Invalid raw data
        invalid_raw_data = {
            "id": "",  # Invalid empty ID
            "snippet": {
                "title": "",  # Invalid empty title
                "channelTitle": None  # Invalid null value
            }
        }
        
        # Transform (should handle gracefully)
        try:
            transformed = transformer.transform("youtube_content", invalid_raw_data)
        except Exception as e:
            # Should not raise exception, but handle gracefully
            assert False, f"Transformer should handle invalid data gracefully: {e}"
        
        # Validate (should fail)
        validation_result = validator.validate("content", transformed)
        assert not validation_result.is_valid
        assert len(validation_result.errors) > 0

    @pytest.mark.asyncio
    async def test_data_consistency_across_operations(self):
        """Test data consistency across multiple operations."""
        storage = DataStorage()
        
        # Create test content
        original_content = ContentData(
            content_id="consistency-123",
            platform="youtube",
            title="Consistency Test",
            author="test_author",
            metadata={"test": "data"}
        )
        
        # Store content
        with patch.object(storage, '_save_to_database') as mock_save:
            mock_save.return_value = True
            
            store_result = await storage.store_content(original_content)
            assert store_result.success
        
        # Retrieve content
        with patch.object(storage, '_load_from_database') as mock_load:
            mock_load.return_value = original_content.to_dict()
            
            retrieved_content = await storage.retrieve_content("consistency-123")
            
            # Verify consistency
            assert retrieved_content.content_id == original_content.content_id
            assert retrieved_content.title == original_content.title
            assert retrieved_content.metadata == original_content.metadata

    @pytest.mark.asyncio
    async def test_performance_with_large_datasets(self):
        """Test performance with large datasets."""
        transformer = DataTransformer()
        storage = DataStorage()
        
        # Generate large dataset
        large_dataset = []
        for i in range(100):
            raw_data = {
                "id": f"perf-{i}",
                "snippet": {
                    "title": f"Performance Test Video {i}",
                    "channelTitle": f"Channel {i % 10}",
                    "publishedAt": "2025-01-11T10:00:00Z"
                },
                "statistics": {
                    "viewCount": str(i * 100),
                    "likeCount": str(i * 5)
                }
            }
            large_dataset.append(raw_data)
        
        # Batch transform
        start_time = datetime.now()
        transformed_batch = transformer.transform_batch("youtube_content", large_dataset)
        transform_duration = (datetime.now() - start_time).total_seconds()
        
        assert len(transformed_batch) == 100
        assert transform_duration < 5.0  # Should complete within 5 seconds
        
        # Convert to ContentData objects
        content_objects = [ContentData.from_dict(item) for item in transformed_batch]
        
        # Batch store
        with patch.object(storage, '_save_batch_to_database') as mock_save_batch:
            mock_save_batch.return_value = [True] * 100
            
            start_time = datetime.now()
            storage_results = await storage.store_batch(content_objects)
            storage_duration = (datetime.now() - start_time).total_seconds()
            
            assert len(storage_results) == 100
            assert all(r.success for r in storage_results)
            assert storage_duration < 10.0  # Should complete within 10 seconds


if __name__ == '__main__':
    pytest.main([str(Path(__file__))])
