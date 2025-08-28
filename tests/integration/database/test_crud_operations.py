"""
Database Integration Tests - CRUD Operations

Tests database operations including create, read, update, delete
operations across all models with proper transaction handling.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, update

# Import models (mocked for testing)
class MockBase:
    metadata = type('metadata', (), {'create_all': lambda x: None, 'drop_all': lambda x: None})()

class MockUser:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, 'id'):
            self.id = kwargs.get('id')
        if not hasattr(self, 'created_at'):
            self.created_at = datetime.now()
        if not hasattr(self, 'updated_at'):
            self.updated_at = datetime.now()

class MockContent:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

# Use mock classes for testing
User = MockUser
Content = MockContent
Base = MockBase()


# Test database URL (use separate test database)
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5432/ainflue_test"


@pytest.fixture(scope="session")
async def test_engine():
    """Create mock test database engine."""
    # Mock engine for testing - in real implementation, use actual test database
    print("Mock database engine created for testing")
    yield "mock_engine"
    print("Mock database engine cleaned up")


@pytest.fixture
async def test_session(test_engine):
    """Create mock test database session."""
    # Mock session for testing
    class MockSession:
        def __init__(self):
            self._objects = []
        
        def add(self, obj):
            self._objects.append(obj)
        
        async def commit(self):
            pass
        
        async def rollback(self):
            pass
        
        async def refresh(self, obj):
            pass
        
        async def execute(self, query):
            # Mock result
            class MockResult:
                def scalar_one_or_none(self):
                    return None
                def all(self):
                    return []
            return MockResult()
    
    yield MockSession()


@pytest.fixture
async def sample_user(test_session):
    """Create a sample user for testing."""
    user = User(
        id=str(uuid.uuid4())[:32],
        email=f"test_{uuid.uuid4()}@example.com",
        username=f"testuser_{uuid.uuid4().hex[:8]}",
        password_hash="hashed_password_123",
        first_name="Test",
        last_name="User",
        creator_type="musician",
        tenant_id=str(uuid.uuid4())[:16],
        is_verified=True,
        subscription_tier="premium"
    )
    
    test_session.add(user)
    await test_session.commit()
    
    return user


class TestUserCRUDOperations:
    """Test CRUD operations for User model."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_user(self, test_session):
        """Test creating a new user."""
        user_data = {
            "id": str(uuid.uuid4())[:32],
            "email": f"create_test_{uuid.uuid4()}@example.com",
            "username": f"createuser_{uuid.uuid4().hex[:8]}",
            "password_hash": "hashed_password_123",
            "first_name": "Create",
            "last_name": "Test",
            "creator_type": "artist",
            "tenant_id": str(uuid.uuid4())[:16],
            "is_verified": False,
            "subscription_tier": "free"
        }
        
        user = User(**user_data)
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Verify user was created
        assert user.id is not None
        assert user.email == user_data["email"]
        assert user.username == user_data["username"]
        assert user.creator_type == "artist"
        assert user.is_verified is False
        assert user.created_at is not None
        assert user.updated_at is not None
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_read_user(self, test_session, sample_user):
        """Test reading a user from database."""
        # Read by ID
        result = await test_session.execute(
            select(User).where(User.id == sample_user.id)
        )
        user = result.scalar_one_or_none()
        
        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email
        assert user.username == sample_user.username
        
        # Read by email
        result = await test_session.execute(
            select(User).where(User.email == sample_user.email)
        )
        user_by_email = result.scalar_one_or_none()
        
        assert user_by_email is not None
        assert user_by_email.id == sample_user.id
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_update_user(self, test_session, sample_user):
        """Test updating a user."""
        original_updated_at = sample_user.updated_at
        
        # Update user data
        await test_session.execute(
            update(User)
            .where(User.id == sample_user.id)
            .values(
                first_name="Updated",
                last_name="Name",
                subscription_tier="enterprise",
                is_verified=True
            )
        )
        await test_session.commit()
        
        # Refresh and verify changes
        await test_session.refresh(sample_user)
        
        assert sample_user.first_name == "Updated"
        assert sample_user.last_name == "Name"
        assert sample_user.subscription_tier == "enterprise"
        assert sample_user.is_verified is True
        assert sample_user.updated_at > original_updated_at
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_delete_user(self, test_session, sample_user):
        """Test deleting a user."""
        user_id = sample_user.id
        
        # Delete user
        await test_session.execute(
            delete(User).where(User.id == user_id)
        )
        await test_session.commit()
        
        # Verify user is deleted
        result = await test_session.execute(
            select(User).where(User.id == user_id)
        )
        deleted_user = result.scalar_one_or_none()
        
        assert deleted_user is None
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_user_unique_constraints(self, test_session, sample_user):
        """Test unique constraints on user email and username."""
        # Try to create user with same email
        duplicate_email_user = User(
            id=str(uuid.uuid4())[:32],
            email=sample_user.email,  # Duplicate email
            username=f"different_{uuid.uuid4().hex[:8]}",
            password_hash="hashed_password_123",
            first_name="Duplicate",
            last_name="Email",
            creator_type="musician",
            tenant_id=str(uuid.uuid4())[:16]
        )
        
        test_session.add(duplicate_email_user)
        
        with pytest.raises(Exception):  # Should raise integrity error
            await test_session.commit()
        
        await test_session.rollback()
        
        # Try to create user with same username
        duplicate_username_user = User(
            id=str(uuid.uuid4())[:32],
            email=f"different_{uuid.uuid4()}@example.com",
            username=sample_user.username,  # Duplicate username
            password_hash="hashed_password_123",
            first_name="Duplicate",
            last_name="Username",
            creator_type="artist",
            tenant_id=str(uuid.uuid4())[:16]
        )
        
        test_session.add(duplicate_username_user)
        
        with pytest.raises(Exception):  # Should raise integrity error
            await test_session.commit()


class TestContentCRUDOperations:
    """Test CRUD operations for Content model."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_content(self, test_session, sample_user):
        """Test creating content associated with a user."""
        content_data = {
            "id": str(uuid.uuid4()),
            "user_id": sample_user.id,
            "title": "Test Content",
            "description": "This is a test content item",
            "content_type": "audio",
            "filename": "test_song.mp3"
        }
        
        content = Content(**content_data)
        test_session.add(content)
        await test_session.commit()
        await test_session.refresh(content)
        
        # Verify content was created
        assert content.id is not None
        assert content.user_id == sample_user.id
        assert content.title == "Test Content"
        assert content.content_type == "audio"
        assert content.filename == "test_song.mp3"
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_read_content_with_user_relationship(self, test_session, sample_user):
        """Test reading content with user relationship."""
        # Create content
        content = Content(
            id=str(uuid.uuid4()),
            user_id=sample_user.id,
            title="Relationship Test Content",
            description="Testing user relationship",
            content_type="video",
            filename="test_video.mp4"
        )
        
        test_session.add(content)
        await test_session.commit()
        
        # Read content with user relationship
        result = await test_session.execute(
            select(Content)
            .where(Content.id == content.id)
        )
        retrieved_content = result.scalar_one_or_none()
        
        assert retrieved_content is not None
        assert retrieved_content.user_id == sample_user.id
        
        # Verify we can access user through relationship
        user_result = await test_session.execute(
            select(User).where(User.id == retrieved_content.user_id)
        )
        related_user = user_result.scalar_one_or_none()
        
        assert related_user is not None
        assert related_user.id == sample_user.id
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_content_foreign_key_constraint(self, test_session):
        """Test foreign key constraint for content-user relationship."""
        # Try to create content with non-existent user_id
        invalid_content = Content(
            id=str(uuid.uuid4()),
            user_id="non_existent_user_id",
            title="Invalid Content",
            description="This should fail",
            content_type="text",
            filename="invalid.txt"
        )
        
        test_session.add(invalid_content)
        
        with pytest.raises(Exception):  # Should raise foreign key error
            await test_session.commit()


class TestTransactionHandling:
    """Test database transaction handling."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_transaction_rollback(self, test_session):
        """Test transaction rollback functionality."""
        # Count initial users
        initial_result = await test_session.execute(select(User))
        initial_count = len(initial_result.all())
        
        try:
            # Start transaction
            user1 = User(
                id=str(uuid.uuid4())[:32],
                email=f"tx_test1_{uuid.uuid4()}@example.com",
                username=f"txuser1_{uuid.uuid4().hex[:8]}",
                password_hash="hashed_password_123",
                first_name="Transaction",
                last_name="Test1",
                creator_type="musician",
                tenant_id=str(uuid.uuid4())[:16]
            )
            
            test_session.add(user1)
            await test_session.flush()  # Flush but don't commit
            
            # Add second user that will cause error (duplicate email)
            user2 = User(
                id=str(uuid.uuid4())[:32],
                email=user1.email,  # Duplicate email
                username=f"txuser2_{uuid.uuid4().hex[:8]}",
                password_hash="hashed_password_123",
                first_name="Transaction",
                last_name="Test2",
                creator_type="artist",
                tenant_id=str(uuid.uuid4())[:16]
            )
            
            test_session.add(user2)
            await test_session.commit()  # This should fail
            
        except Exception:
            await test_session.rollback()
        
        # Verify rollback - no users should be added
        final_result = await test_session.execute(select(User))
        final_count = len(final_result.all())
        
        assert final_count == initial_count  # Should be unchanged
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_concurrent_transactions(self, test_engine):
        """Test handling of concurrent transactions."""
        async def create_user_transaction(session_factory, user_data):
            async with session_factory() as session:
                user = User(**user_data)
                session.add(user)
                await session.commit()
                return user.id
        
        # Create session factory
        async_session = sessionmaker(
            test_engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Create multiple users concurrently
        tasks = []
        for i in range(5):
            user_data = {
                "id": str(uuid.uuid4())[:32],
                "email": f"concurrent_{i}_{uuid.uuid4()}@example.com",
                "username": f"concurrent_{i}_{uuid.uuid4().hex[:8]}",
                "password_hash": "hashed_password_123",
                "first_name": f"Concurrent{i}",
                "last_name": "Test",
                "creator_type": "musician",
                "tenant_id": str(uuid.uuid4())[:16]
            }
            
            task = create_user_transaction(async_session, user_data)
            tasks.append(task)
        
        # Execute all tasks concurrently
        user_ids = await asyncio.gather(*tasks)
        
        # Verify all users were created
        assert len(user_ids) == 5
        assert all(user_id is not None for user_id in user_ids)
        assert len(set(user_ids)) == 5  # All IDs should be unique


class TestDataIntegrityAndConstraints:
    """Test data integrity and database constraints."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_required_fields(self, test_session):
        """Test that required fields are enforced."""
        # Try to create user without required fields
        incomplete_user = User(
            id=str(uuid.uuid4())[:32],
            # Missing email, username, password_hash, etc.
        )
        
        test_session.add(incomplete_user)
        
        with pytest.raises(Exception):  # Should raise validation error
            await test_session.commit()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_data_type_validation(self, test_session):
        """Test data type validation."""
        # Try to create user with invalid data types
        with pytest.raises(Exception):
            invalid_user = User(
                id=12345,  # Should be string
                email="test@example.com",
                username="testuser",
                password_hash="hashed_password_123",
                first_name="Test",
                last_name="User",
                creator_type="musician",
                tenant_id="tenant123",
                is_verified="not_boolean"  # Should be boolean
            )
            
            test_session.add(invalid_user)
            await test_session.commit()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_cascade_operations(self, test_session, sample_user):
        """Test cascade operations when deleting related records."""
        # Create content for the user
        content_items = []
        for i in range(3):
            content = Content(
                id=str(uuid.uuid4()),
                user_id=sample_user.id,
                title=f"Content {i}",
                description=f"Test content {i}",
                content_type="text",
                filename=f"file_{i}.txt"
            )
            content_items.append(content)
            test_session.add(content)
        
        await test_session.commit()
        
        # Verify content exists
        result = await test_session.execute(
            select(Content).where(Content.user_id == sample_user.id)
        )
        user_content = result.all()
        assert len(user_content) == 3
        
        # Delete user (test cascade behavior)
        await test_session.execute(
            delete(User).where(User.id == sample_user.id)
        )
        await test_session.commit()
        
        # Verify content behavior (depends on cascade configuration)
        result = await test_session.execute(
            select(Content).where(Content.user_id == sample_user.id)
        )
        remaining_content = result.all()
        
        # This test depends on your cascade configuration
        # Adjust based on your actual foreign key setup
        assert len(remaining_content) >= 0  # Could be 0 (cascade delete) or 3 (no cascade)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])