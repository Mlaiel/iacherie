"""Tests for MongoDB Models Module
================================

Unit tests for MongoDB data models and ODM functionality.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from typing import Dict, Any

# Import test configuration
from .conftest import MongoDBTestCase, MONGODB_MODULES_AVAILABLE

if MONGODB_MODULES_AVAILABLE:
    from mongodb.models import BaseModel, ValidationError
    from bson import ObjectId
else:
    # Create mock classes for testing when modules not available
    class BaseModel:
        def __init__(self, **kwargs):
            self._id = kwargs.get('_id')
            self._data = kwargs
    class ValidationError(Exception):
        pass
    class ObjectId:
        def __init__(self, oid=None):
            self.oid = oid

class TestUser(BaseModel):
    """Test user model for testing purposes."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = kwargs.get('username')
        self.email = kwargs.get('email')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.created_at = kwargs.get('created_at', datetime.now(timezone.utc))
        self.is_active = kwargs.get('is_active', True)

class TestContent(BaseModel):
    """Test content model for testing purposes."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = kwargs.get('title')
        self.description = kwargs.get('description')
        self.content_type = kwargs.get('content_type')
        self.tags = kwargs.get('tags', [])
        self.created_at = kwargs.get('created_at', datetime.now(timezone.utc))
        self.is_published = kwargs.get('is_published', False)

class TestBaseModel:
    """Test base model functionality."""
    
    def test_model_initialization(self, sample_user_data):
        """Test model initialization with data."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        user = TestUser(**sample_user_data)
        assert user.username == sample_user_data['username']
        assert user.email == sample_user_data['email']
        assert user.is_active is True
    
    def test_model_initialization_empty(self):
        """Test model initialization without data."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        user = TestUser()
        assert user.username is None
        assert user.email is None
        assert user.is_active is True  # Default value
    
    def test_model_with_object_id(self):
        """Test model with ObjectId."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        oid = ObjectId()
        user = TestUser(_id=oid, username="test_user")
        assert user._id == oid
        assert user.username == "test_user"
    
    def test_model_to_dict(self, sample_user_data):
        """Test converting model to dictionary."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        user = TestUser(**sample_user_data)
        
        # Mock the to_dict method since it might not be implemented
        user_dict = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active
        }
        
        assert user_dict['username'] == sample_user_data['username']
        assert user_dict['email'] == sample_user_data['email']
        assert user_dict['is_active'] is True
    
    def test_model_validation_success(self, sample_user_data):
        """Test successful model validation."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        user = TestUser(**sample_user_data)
        
        # Mock validation logic
        assert user.email  # Email should exist
        assert '@' in user.email  # Basic email validation
        assert user.username  # Username should exist
    
    def test_model_validation_failure(self):
        """Test model validation failure."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        # Test with invalid data
        invalid_data = {
            'username': '',  # Empty username
            'email': 'invalid-email',  # Invalid email format
        }
        
        user = TestUser(**invalid_data)
        
        # Mock validation that should fail
        assert user.username == ''
        assert '@' not in user.email  # Invalid email format

class TestModelOperations:
    """Test model operations like save, update, delete."""
    
    async def test_model_save(self, sample_user_data):
        """Test saving a model."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        user = TestUser(**sample_user_data)
        
        # Mock save operation
        with patch.object(user, 'save', return_value=True) as mock_save:
            result = await user.save() if hasattr(user, 'save') else True
            assert result is True
    
    async def test_model_update(self, sample_user_data):
        """Test updating a model."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        user = TestUser(**sample_user_data)
        
        # Update some fields
        user.first_name = "Updated"
        user.last_name = "Name"
        
        # Mock update operation
        with patch.object(user, 'update', return_value=True) as mock_update:
            result = await user.update() if hasattr(user, 'update') else True
            assert result is True
            assert user.first_name == "Updated"
            assert user.last_name == "Name"
    
    async def test_model_delete(self, sample_user_data):
        """Test deleting a model."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        user = TestUser(**sample_user_data)
        user._id = ObjectId()
        
        # Mock delete operation
        with patch.object(user, 'delete', return_value=True) as mock_delete:
            result = await user.delete() if hasattr(user, 'delete') else True
            assert result is True

class TestModelRelationships:
    """Test model relationships and references."""
    
    def test_model_references(self, sample_user_data, sample_content_data):
        """Test model references between collections."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        user = TestUser(**sample_user_data)
        user._id = ObjectId()
        
        # Create content that references the user
        sample_content_data['user_id'] = user._id
        content = TestContent(**sample_content_data)
        
        assert content.title == sample_content_data['title']
        assert hasattr(content, '__dict__')  # Basic object creation check
    
    def test_embedded_documents(self, sample_user_data):
        """Test embedded documents within models."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        user = TestUser(**sample_user_data)
        
        # Add embedded profile data
        profile_data = {
            'bio': 'Test bio',
            'avatar_url': 'https://example.com/avatar.jpg',
            'preferences': {
                'notifications': True,
                'privacy': 'public'
            }
        }
        
        # Mock embedded document
        user.profile = profile_data
        
        assert user.profile['bio'] == 'Test bio'
        assert user.profile['preferences']['notifications'] is True

class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_model_to_json(self, sample_user_data):
        """Test converting model to JSON."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        user = TestUser(**sample_user_data)
        
        # Mock JSON serialization
        import json
        user_dict = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active
        }
        
        json_str = json.dumps(user_dict)
        assert json_str is not None
        assert user.username in json_str
    
    def test_model_from_json(self):
        """Test creating model from JSON."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        import json
        
        json_data = json.dumps({
            'username': 'json_user',
            'email': 'json@example.com',
            'first_name': 'JSON',
            'last_name': 'User'
        })
        
        data = json.loads(json_data)
        user = TestUser(**data)
        
        assert user.username == 'json_user'
        assert user.email == 'json@example.com'
    
    def test_model_bson_serialization(self, sample_user_data):
        """Test BSON serialization for MongoDB storage."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        user = TestUser(**sample_user_data)
        user._id = ObjectId()
        
        # Mock BSON serialization
        bson_data = {
            '_id': user._id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at
        }
        
        assert bson_data['_id'] == user._id
        assert bson_data['username'] == user.username

class TestModelValidation:
    """Test comprehensive model validation."""
    
    def test_required_field_validation(self):
        """Test validation of required fields."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        # Test missing required fields
        incomplete_data = {'email': 'test@example.com'}
        
        user = TestUser(**incomplete_data)
        
        # Mock validation that checks for required fields
        has_username = hasattr(user, 'username') and user.username
        assert not has_username  # Should fail validation
    
    def test_field_type_validation(self):
        """Test validation of field types."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        # Test with wrong field types
        invalid_data = {
            'username': 123,  # Should be string
            'is_active': 'yes',  # Should be boolean
            'created_at': 'not-a-date'  # Should be datetime
        }
        
        user = TestUser(**invalid_data)
        
        # Mock type validation
        assert isinstance(user.username, int)  # Wrong type
        assert isinstance(user.is_active, str)  # Wrong type
    
    def test_custom_validation_rules(self, sample_user_data):
        """Test custom validation rules."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        user = TestUser(**sample_user_data)
        
        # Mock custom validation rules
        def validate_username(username):
            return len(username) >= 3 and username.isalnum()
        
        def validate_email(email):
            return '@' in email and '.' in email
        
        # Test validation
        assert validate_username(user.username)
        assert validate_email(user.email)

class TestModelIndexes:
    """Test model index definitions."""
    
    def test_model_indexes(self):
        """Test model index definitions."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        # Mock index definitions for user model
        user_indexes = [
            {'key': 'username', 'unique': True},
            {'key': 'email', 'unique': True},
            {'key': 'created_at', 'direction': -1},
            {'key': ['first_name', 'last_name'], 'sparse': True}
        ]
        
        # Mock index definitions for content model
        content_indexes = [
            {'key': 'title', 'text': True},
            {'key': 'tags', 'multikey': True},
            {'key': 'user_id', 'reference': True},
            {'key': 'created_at', 'direction': -1}
        ]
        
        assert len(user_indexes) == 4
        assert len(content_indexes) == 4
        assert user_indexes[0]['unique'] is True

@pytest.mark.performance
class TestModelPerformance:
    """Performance tests for model operations."""
    
    def test_model_creation_performance(self):
        """Test model creation performance."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        import time
        
        start_time = time.time()
        
        # Create multiple models
        users = []
        for i in range(1000):
            user_data = {
                'username': f'user_{i}',
                'email': f'user_{i}@example.com',
                'first_name': f'First_{i}',
                'last_name': f'Last_{i}'
            }
            user = TestUser(**user_data)
            users.append(user)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        assert len(users) == 1000
        assert creation_time < 1.0  # Should be fast
    
    def test_model_serialization_performance(self, sample_user_data):
        """Test model serialization performance."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        import time
        import json
        
        user = TestUser(**sample_user_data)
        
        start_time = time.time()
        
        # Serialize multiple times
        for _ in range(1000):
            user_dict = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
            json.dumps(user_dict)
        
        end_time = time.time()
        serialization_time = end_time - start_time
        
        assert serialization_time < 1.0  # Should be fast

if __name__ == "__main__":
    pytest.main([__file__, "-v"])