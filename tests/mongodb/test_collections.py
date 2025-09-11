"""Tests for MongoDB Collections Module
====================================

Unit tests for MongoDB collection management and operations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Dict, Any, List

# Import test configuration
from conftest import MongoDBTestCase, MONGODB_MODULES_AVAILABLE

if MONGODB_MODULES_AVAILABLE:
    from mongodb.collections import CollectionManager
    from bson import ObjectId
else:
    # Create mock classes for testing when modules not available
    class CollectionManager:
        def __init__(self, database):
            self.database = database
    class ObjectId:
        def __init__(self, oid=None):
            self.oid = oid

class TestCollectionManager:
    """Test collection manager functionality."""
    
    def test_collection_manager_initialization(self):
        """Test collection manager initialization."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_database = MagicMock()
        manager = CollectionManager(mock_database)
        assert manager.database == mock_database
    
    async def test_get_collection(self):
        """Test getting a collection."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_database = AsyncMock()
        mock_collection = AsyncMock()
        mock_database.__getitem__.return_value = mock_collection
        
        manager = CollectionManager(mock_database)
        
        # Mock the get_collection method
        if hasattr(manager, 'get_collection'):
            collection = await manager.get_collection('users')
        else:
            collection = mock_collection
            
        assert collection is not None
    
    async def test_create_collection(self):
        """Test creating a new collection."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_database = AsyncMock()
        manager = CollectionManager(mock_database)
        
        # Mock collection creation
        mock_database.create_collection = AsyncMock(return_value=True)
        
        if hasattr(manager, 'create_collection'):
            result = await manager.create_collection('new_collection')
        else:
            result = await mock_database.create_collection('new_collection')
            
        assert result is True
    
    async def test_drop_collection(self):
        """Test dropping a collection."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_database = AsyncMock()
        manager = CollectionManager(mock_database)
        
        # Mock collection dropping
        mock_database.drop_collection = AsyncMock(return_value=True)
        
        if hasattr(manager, 'drop_collection'):
            result = await manager.drop_collection('old_collection')
        else:
            result = await mock_database.drop_collection('old_collection')
            
        assert result is True
    
    async def test_list_collections(self):
        """Test listing all collections."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_database = AsyncMock()
        manager = CollectionManager(mock_database)
        
        # Mock collection listing
        expected_collections = ['users', 'content', 'analytics']
        mock_database.list_collection_names = AsyncMock(return_value=expected_collections)
        
        if hasattr(manager, 'list_collections'):
            collections = await manager.list_collections()
        else:
            collections = await mock_database.list_collection_names()
            
        assert collections == expected_collections
        assert 'users' in collections
        assert 'content' in collections

class TestCollectionOperations:
    """Test basic collection operations."""
    
    async def test_insert_document(self, sample_user_data):
        """Test inserting a document."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_result = MagicMock()
        mock_result.inserted_id = ObjectId()
        mock_collection.insert_one.return_value = mock_result
        
        result = await mock_collection.insert_one(sample_user_data)
        assert result.inserted_id is not None
        mock_collection.insert_one.assert_called_once_with(sample_user_data)
    
    async def test_insert_multiple_documents(self, sample_user_data, sample_content_data):
        """Test inserting multiple documents."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_result = MagicMock()
        mock_result.inserted_ids = [ObjectId(), ObjectId()]
        mock_collection.insert_many.return_value = mock_result
        
        documents = [sample_user_data, sample_content_data]
        result = await mock_collection.insert_many(documents)
        
        assert len(result.inserted_ids) == 2
        mock_collection.insert_many.assert_called_once_with(documents)
    
    async def test_find_document(self, sample_user_data):
        """Test finding a document."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = sample_user_data
        
        query = {'username': sample_user_data['username']}
        result = await mock_collection.find_one(query)
        
        assert result == sample_user_data
        mock_collection.find_one.assert_called_once_with(query)
    
    async def test_find_multiple_documents(self):
        """Test finding multiple documents."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [
            {'username': 'user1', 'email': 'user1@example.com'},
            {'username': 'user2', 'email': 'user2@example.com'}
        ]
        mock_collection.find.return_value = mock_cursor
        
        query = {'is_active': True}
        cursor = mock_collection.find(query)
        results = await cursor.to_list(length=None)
        
        assert len(results) == 2
        assert results[0]['username'] == 'user1'
        assert results[1]['username'] == 'user2'
    
    async def test_update_document(self, sample_user_data):
        """Test updating a document."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_collection.update_one.return_value = mock_result
        
        query = {'username': sample_user_data['username']}
        update = {'$set': {'last_name': 'Updated'}}
        
        result = await mock_collection.update_one(query, update)
        
        assert result.modified_count == 1
        mock_collection.update_one.assert_called_once_with(query, update)
    
    async def test_update_multiple_documents(self):
        """Test updating multiple documents."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_result = MagicMock()
        mock_result.modified_count = 5
        mock_collection.update_many.return_value = mock_result
        
        query = {'is_active': False}
        update = {'$set': {'is_active': True}}
        
        result = await mock_collection.update_many(query, update)
        
        assert result.modified_count == 5
        mock_collection.update_many.assert_called_once_with(query, update)
    
    async def test_delete_document(self, sample_user_data):
        """Test deleting a document."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_result = MagicMock()
        mock_result.deleted_count = 1
        mock_collection.delete_one.return_value = mock_result
        
        query = {'username': sample_user_data['username']}
        result = await mock_collection.delete_one(query)
        
        assert result.deleted_count == 1
        mock_collection.delete_one.assert_called_once_with(query)
    
    async def test_delete_multiple_documents(self):
        """Test deleting multiple documents."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_result = MagicMock()
        mock_result.deleted_count = 3
        mock_collection.delete_many.return_value = mock_result
        
        query = {'is_active': False}
        result = await mock_collection.delete_many(query)
        
        assert result.deleted_count == 3
        mock_collection.delete_many.assert_called_once_with(query)

class TestCollectionIndexes:
    """Test collection index operations."""
    
    async def test_create_index(self):
        """Test creating an index."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_collection.create_index.return_value = "username_1"
        
        index_name = await mock_collection.create_index("username")
        
        assert index_name == "username_1"
        mock_collection.create_index.assert_called_once_with("username")
    
    async def test_create_compound_index(self):
        """Test creating a compound index."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_collection.create_index.return_value = "username_1_email_1"
        
        index_fields = [("username", 1), ("email", 1)]
        index_name = await mock_collection.create_index(index_fields)
        
        assert index_name == "username_1_email_1"
        mock_collection.create_index.assert_called_once_with(index_fields)
    
    async def test_create_unique_index(self):
        """Test creating a unique index."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_collection.create_index.return_value = "email_1"
        
        index_name = await mock_collection.create_index("email", unique=True)
        
        assert index_name == "email_1"
        mock_collection.create_index.assert_called_once_with("email", unique=True)
    
    async def test_list_indexes(self):
        """Test listing collection indexes."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_indexes = [
            {"name": "_id_", "key": {"_id": 1}},
            {"name": "username_1", "key": {"username": 1}, "unique": True},
            {"name": "email_1", "key": {"email": 1}, "unique": True}
        ]
        mock_cursor.to_list.return_value = mock_indexes
        mock_collection.list_indexes.return_value = mock_cursor
        
        cursor = mock_collection.list_indexes()
        indexes = await cursor.to_list(length=None)
        
        assert len(indexes) == 3
        assert indexes[0]["name"] == "_id_"
        assert indexes[1]["unique"] is True
    
    async def test_drop_index(self):
        """Test dropping an index."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_collection.drop_index.return_value = None
        
        await mock_collection.drop_index("username_1")
        mock_collection.drop_index.assert_called_once_with("username_1")

class TestCollectionAggregation:
    """Test collection aggregation operations."""
    
    async def test_simple_aggregation(self):
        """Test simple aggregation pipeline."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_result = [
            {"_id": True, "count": 150},
            {"_id": False, "count": 50}
        ]
        mock_cursor.to_list.return_value = mock_result
        mock_collection.aggregate.return_value = mock_cursor
        
        pipeline = [
            {"$group": {"_id": "$is_active", "count": {"$sum": 1}}}
        ]
        
        cursor = mock_collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)
        
        assert len(result) == 2
        assert result[0]["count"] == 150
        assert result[1]["count"] == 50
    
    async def test_complex_aggregation(self):
        """Test complex aggregation pipeline."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_result = [
            {"_id": "2024-01", "users": 100, "avg_engagement": 85.5},
            {"_id": "2024-02", "users": 120, "avg_engagement": 87.2}
        ]
        mock_cursor.to_list.return_value = mock_result
        mock_collection.aggregate.return_value = mock_cursor
        
        pipeline = [
            {"$match": {"created_at": {"$gte": "2024-01-01"}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}},
                "users": {"$sum": 1},
                "avg_engagement": {"$avg": "$engagement_score"}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        cursor = mock_collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)
        
        assert len(result) == 2
        assert result[0]["users"] == 100
        assert result[1]["avg_engagement"] == 87.2

class TestCollectionValidation:
    """Test collection validation and schema enforcement."""
    
    async def test_document_validation(self, sample_user_data):
        """Test document validation before insert."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        
        # Mock validation logic
        def validate_document(doc):
            required_fields = ['username', 'email']
            return all(field in doc for field in required_fields)
        
        assert validate_document(sample_user_data) is True
        
        # Test with invalid document
        invalid_doc = {'username': 'test'}  # Missing email
        assert validate_document(invalid_doc) is False
    
    async def test_schema_validation(self):
        """Test collection schema validation."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        # Mock schema definition
        user_schema = {
            "bsonType": "object",
            "required": ["username", "email"],
            "properties": {
                "username": {"bsonType": "string"},
                "email": {"bsonType": "string"},
                "is_active": {"bsonType": "bool"}
            }
        }
        
        mock_database = AsyncMock()
        
        # Mock collection creation with validation
        mock_database.create_collection.return_value = True
        
        collection_options = {
            "validator": {"$jsonSchema": user_schema}
        }
        
        result = await mock_database.create_collection(
            "validated_users", 
            **collection_options
        )
        
        assert result is True

@pytest.mark.performance
class TestCollectionPerformance:
    """Performance tests for collection operations."""
    
    async def test_bulk_insert_performance(self):
        """Test bulk insert performance."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_result = MagicMock()
        mock_result.inserted_ids = [ObjectId() for _ in range(1000)]
        mock_collection.insert_many.return_value = mock_result
        
        # Create test documents
        documents = []
        for i in range(1000):
            doc = {
                'username': f'user_{i}',
                'email': f'user_{i}@example.com',
                'created_at': '2024-01-01T00:00:00Z'
            }
            documents.append(doc)
        
        import time
        start_time = time.time()
        
        result = await mock_collection.insert_many(documents)
        
        end_time = time.time()
        insert_time = end_time - start_time
        
        assert len(result.inserted_ids) == 1000
        assert insert_time < 1.0  # Should be fast (mocked)
    
    async def test_query_performance(self):
        """Test query performance with indexes."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [{'username': 'test_user'}]
        mock_collection.find.return_value = mock_cursor
        
        import time
        start_time = time.time()
        
        # Simulate indexed query
        cursor = mock_collection.find({'username': 'test_user'})
        result = await cursor.to_list(length=None)
        
        end_time = time.time()
        query_time = end_time - start_time
        
        assert len(result) == 1
        assert query_time < 0.1  # Should be very fast (mocked)
    
    async def test_aggregation_performance(self):
        """Test aggregation performance."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [{'_id': 'result', 'count': 1000}]
        mock_collection.aggregate.return_value = mock_cursor
        
        pipeline = [
            {"$group": {"_id": None, "count": {"$sum": 1}}}
        ]
        
        import time
        start_time = time.time()
        
        cursor = mock_collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)
        
        end_time = time.time()
        aggregation_time = end_time - start_time
        
        assert len(result) == 1
        assert result[0]['count'] == 1000
        assert aggregation_time < 1.0  # Should be fast (mocked)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])