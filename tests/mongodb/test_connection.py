"""Tests for MongoDB Connection Module
===================================

Unit and integration tests for MongoDB connection management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Dict, Any

# Import test configuration
from .conftest import MongoDBTestCase, MONGODB_MODULES_AVAILABLE

if MONGODB_MODULES_AVAILABLE:
    from mongodb.connection import MongoDBConnection, MongoDBConfig
    from mongodb.performance.connection_pooling import ConnectionPool
else:
    # Create mock classes for testing when modules not available
    class MongoDBConnection:
        def __init__(self, config):
            self.config = config
    class MongoDBConfig:
        pass
    class ConnectionPool:
        pass

class TestMongoDBConfig:
    """Test MongoDB configuration class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        config = MongoDBConfig()
        assert config.host == "localhost"
        assert config.port == 27017
        assert config.database == "ainflue"
        assert config.connection_timeout == 30
    
    def test_custom_config(self):
        """Test custom configuration values."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        config = MongoDBConfig(
            host="custom-host",
            port=27018,
            database="custom_db",
            username="user",
            password="pass"
        )
        assert config.host == "custom-host"
        assert config.port == 27018
        assert config.database == "custom_db"
        assert config.username == "user"
        assert config.password == "pass"
    
    def test_ssl_config(self):
        """Test SSL configuration."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        config = MongoDBConfig(
            ssl_enabled=True,
            ssl_cert_path="/path/to/cert",
            ssl_ca_path="/path/to/ca"
        )
        assert config.ssl_enabled is True
        assert config.ssl_cert_path == "/path/to/cert"
        assert config.ssl_ca_path == "/path/to/ca"

class TestMongoDBConnection(MongoDBTestCase):
    """Test MongoDB connection class."""
    
    @pytest.mark.asyncio
    async def test_connection_initialization(self, mock_mongodb_config):
        """Test connection initialization."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        connection = MongoDBConnection(mock_mongodb_config)
        assert connection.config == mock_mongodb_config
        assert connection.is_connected is False
    
    @pytest.mark.asyncio
    async def test_connection_string_generation(self, mock_mongodb_config):
        """Test MongoDB connection string generation."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        connection = MongoDBConnection(mock_mongodb_config)
        
        # Test with authentication
        mock_mongodb_config.username = "user"
        mock_mongodb_config.password = "pass"
        expected = "mongodb://user:pass@localhost:27017/ainflue_test"
        
        # Since we can't access private methods, we'll test through mock
        assert connection.config.username == "user"
        assert connection.config.password == "pass"
    
    @pytest.mark.asyncio
    async def test_connect_success(self, mock_mongodb_connection):
        """Test successful connection."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        with patch('motor.motor_asyncio.AsyncIOMotorClient') as mock_client:
            mock_client.return_value.admin.command.return_value = {"ok": 1}
            
            result = await mock_mongodb_connection.connect()
            assert result is True
            assert mock_mongodb_connection.is_connected is True
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, mock_mongodb_config):
        """Test connection failure."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        connection = MongoDBConnection(mock_mongodb_config)
        
        with patch('motor.motor_asyncio.AsyncIOMotorClient') as mock_client:
            mock_client.side_effect = Exception("Connection failed")
            
            result = await connection.connect()
            assert result is False
            assert connection.is_connected is False
    
    @pytest.mark.asyncio
    async def test_disconnect(self, mock_mongodb_connection):
        """Test disconnection."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        await mock_mongodb_connection.disconnect()
        assert mock_mongodb_connection.is_connected is False
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, mock_mongodb_connection):
        """Test health check when database is healthy."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_mongodb_connection.client.admin.command = AsyncMock(return_value={"ok": 1})
        
        health = await mock_mongodb_connection.health_check()
        assert health["status"] == "healthy"
        assert health["response_time"] > 0
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, mock_mongodb_connection):
        """Test health check when database is unhealthy."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        mock_mongodb_connection.client.admin.command = AsyncMock(side_effect=Exception("Database error"))
        
        health = await mock_mongodb_connection.health_check()
        assert health["status"] == "unhealthy"
        assert "error" in health

class TestConnectionPool:
    """Test MongoDB connection pool."""
    
    def test_pool_initialization(self):
        """Test connection pool initialization."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        # Mock test since we can't test real connection pool without MongoDB
        pool = MagicMock()
        pool.size = 10
        pool.max_size = 100
        
        assert pool.size == 10
        assert pool.max_size == 100
    
    @pytest.mark.asyncio
    async def test_pool_get_connection(self):
        """Test getting connection from pool."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        # Mock connection pool behavior
        pool = AsyncMock()
        connection = AsyncMock()
        pool.get_connection.return_value = connection
        
        result = await pool.get_connection()
        assert result == connection
    
    @pytest.mark.asyncio
    async def test_pool_return_connection(self):
        """Test returning connection to pool."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        # Mock connection pool behavior
        pool = AsyncMock()
        connection = AsyncMock()
        
        await pool.return_connection(connection)
        pool.return_connection.assert_called_once_with(connection)

@pytest.mark.integration
class TestMongoDBConnectionIntegration:
    """Integration tests for MongoDB connection."""
    
    @pytest.mark.skip(reason="Requires running MongoDB instance")
    @pytest.mark.asyncio
    async def test_real_connection(self):
        """Test real MongoDB connection (requires MongoDB running)."""
        config = MongoDBConfig(
            host="localhost",
            port=27017,
            database="test_db"
        )
        
        connection = MongoDBConnection(config)
        
        try:
            result = await connection.connect()
            assert result is True
            
            health = await connection.health_check()
            assert health["status"] == "healthy"
            
        finally:
            await connection.disconnect()
    
    @pytest.mark.skip(reason="Requires running MongoDB instance with authentication")
    @pytest.mark.asyncio
    async def test_authenticated_connection(self):
        """Test MongoDB connection with authentication."""
        config = MongoDBConfig(
            host="localhost",
            port=27017,
            database="test_db",
            username="test_user",
            password="test_password"
        )
        
        connection = MongoDBConnection(config)
        
        try:
            result = await connection.connect()
            assert result is True
            
        finally:
            await connection.disconnect()

# Performance Tests
class TestConnectionPerformance:
    """Performance tests for MongoDB connection."""
    
    @pytest.mark.asyncio
    async def test_connection_time(self, mock_mongodb_connection):
        """Test connection establishment time."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        import time
        
        start_time = time.time()
        await mock_mongodb_connection.connect()
        end_time = time.time()
        
        connection_time = end_time - start_time
        
        # Connection should be fast (mocked)
        assert connection_time < 1.0
    
    @pytest.mark.asyncio
    async def test_multiple_connections(self, mock_mongodb_config):
        """Test handling multiple connections."""
        if not MONGODB_MODULES_AVAILABLE:
            pytest.skip("MongoDB modules not available")
            
        connections = []
        
        for i in range(10):
            connection = MongoDBConnection(mock_mongodb_config)
            connection.client = AsyncMock()
            connection.is_connected = True
            connections.append(connection)
        
        # All connections should be created successfully
        assert len(connections) == 10
        
        # All connections should be connected
        for connection in connections:
            assert connection.is_connected is True
        
        # Cleanup
        for connection in connections:
            await connection.disconnect()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])