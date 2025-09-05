"""MongoDB Connection Management
============================

Advanced MongoDB connection handling with async support, connection pooling,
authentication, SSL, and health monitoring for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import ssl
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
import os

try:
    import motor.motor_asyncio
    import pymongo
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    # Create mock classes to prevent NameError
    class motor:
        class motor_asyncio:
            class AsyncIOMotorClient:
                pass
    class pymongo:
        class MongoClient:
            pass

logger = logging.getLogger(__name__)

@dataclass
class MongoDBConfig:
    """MongoDB connection configuration."""
    host: str = "localhost"
    port: int = 27017
    database: str = "ainflue"
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_enabled: bool = False
    ssl_cert_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    connection_timeout: int = 30
    server_selection_timeout: int = 30
    max_pool_size: int = 100
    min_pool_size: int = 0
    max_idle_time: int = 0
    replica_set: Optional[str] = None
    read_preference: str = "primary"
    write_concern: int = 1
    auth_source: str = "admin"
    extra_params: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> 'MongoDBConfig':
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("MONGODB_HOST", "localhost"),
            port=int(os.getenv("MONGODB_PORT", "27017")),
            database=os.getenv("MONGODB_DATABASE", "ainflue"),
            username=os.getenv("MONGODB_USERNAME"),
            password=os.getenv("MONGODB_PASSWORD"),
            ssl_enabled=os.getenv("MONGODB_SSL_ENABLED", "false").lower() == "true",
            ssl_cert_path=os.getenv("MONGODB_SSL_CERT_PATH"),
            ssl_ca_path=os.getenv("MONGODB_SSL_CA_PATH"),
            connection_timeout=int(os.getenv("MONGODB_CONNECTION_TIMEOUT", "30")),
            server_selection_timeout=int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT", "30")),
            max_pool_size=int(os.getenv("MONGODB_MAX_POOL_SIZE", "100")),
            replica_set=os.getenv("MONGODB_REPLICA_SET"),
            auth_source=os.getenv("MONGODB_AUTH_SOURCE", "admin")
        )

class MongoDBConnection:
    """MongoDB connection manager with async support."""
    
    def __init__(self, config: Optional[MongoDBConfig] = None):
        """Initialize MongoDB connection manager."""
        if not MONGODB_AVAILABLE:
            raise ImportError("MongoDB dependencies (motor, pymongo) not available")
        
        self.config = config or MongoDBConfig.from_env()
        self._client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self._sync_client: Optional[pymongo.MongoClient] = None
        self._database = None
        self._connected = False
        self._connection_time: Optional[datetime] = None
        self._last_ping: Optional[datetime] = None
        
    def _build_connection_string(self) -> str:
        """Build MongoDB connection string."""
        auth_string = ""
        if self.config.username and self.config.password:
            auth_string = f"{self.config.username}:{self.config.password}@"
        
        return f"mongodb://{auth_string}{self.config.host}:{self.config.port}/{self.config.database}"
    
    def _get_connection_options(self) -> Dict[str, Any]:
        """Get connection options dictionary."""
        options = {
            "serverSelectionTimeoutMS": self.config.server_selection_timeout * 1000,
            "connectTimeoutMS": self.config.connection_timeout * 1000,
            "maxPoolSize": self.config.max_pool_size,
            "minPoolSize": self.config.min_pool_size,
            "authSource": self.config.auth_source,
            **self.config.extra_params
        }
        
        if self.config.replica_set:
            options["replicaSet"] = self.config.replica_set
            
        if self.config.ssl_enabled:
            options["ssl"] = True
            if self.config.ssl_cert_path:
                options["ssl_certfile"] = self.config.ssl_cert_path
            if self.config.ssl_ca_path:
                options["ssl_ca_certs"] = self.config.ssl_ca_path
                
        return options
    
    async def connect(self) -> bool:
        """Establish async connection to MongoDB."""
        try:
            connection_string = self._build_connection_string()
            options = self._get_connection_options()
            
            self._client = motor.motor_asyncio.AsyncIOMotorClient(
                connection_string, **options
            )
            
            # Test connection
            await self._client.admin.command('ping')
            
            self._database = self._client[self.config.database]
            self._connected = True
            self._connection_time = datetime.utcnow()
            self._last_ping = self._connection_time
            
            logger.info(f"Connected to MongoDB at {self.config.host}:{self.config.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._connected = False
            return False
    
    def connect_sync(self) -> bool:
        """Establish synchronous connection to MongoDB."""
        try:
            connection_string = self._build_connection_string()
            options = self._get_connection_options()
            
            self._sync_client = pymongo.MongoClient(connection_string, **options)
            
            # Test connection
            self._sync_client.admin.command('ping')
            
            self._connected = True
            self._connection_time = datetime.utcnow()
            
            logger.info(f"Connected to MongoDB (sync) at {self.config.host}:{self.config.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB (sync): {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Close async connection."""
        if self._client:
            self._client.close()
            self._client = None
        self._connected = False
        logger.info("Disconnected from MongoDB")
    
    def disconnect_sync(self):
        """Close synchronous connection."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
        self._connected = False
        logger.info("Disconnected from MongoDB (sync)")
    
    async def ping(self) -> bool:
        """Ping MongoDB server to check connectivity."""
        try:
            if not self._client:
                return False
            await self._client.admin.command('ping')
            self._last_ping = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"MongoDB ping failed: {e}")
            return False
    
    def ping_sync(self) -> bool:
        """Ping MongoDB server synchronously."""
        try:
            if not self._sync_client:
                return False
            self._sync_client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB ping (sync) failed: {e}")
            return False
    
    @property
    def client(self) -> Optional[motor.motor_asyncio.AsyncIOMotorClient]:
        """Get async MongoDB client."""
        return self._client
    
    @property
    def sync_client(self) -> Optional[pymongo.MongoClient]:
        """Get sync MongoDB client."""
        return self._sync_client
    
    @property
    def database(self):
        """Get database instance."""
        return self._database
    
    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected
    
    @property
    def connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        return {
            "connected": self._connected,
            "host": self.config.host,
            "port": self.config.port,
            "database": self.config.database,
            "connection_time": self._connection_time.isoformat() if self._connection_time else None,
            "last_ping": self._last_ping.isoformat() if self._last_ping else None,
            "ssl_enabled": self.config.ssl_enabled,
            "replica_set": self.config.replica_set
        }

# Global connection instance
_default_connection: Optional[MongoDBConnection] = None

def get_connection(config: Optional[MongoDBConfig] = None) -> MongoDBConnection:
    """Get or create default MongoDB connection."""
    global _default_connection
    if _default_connection is None:
        _default_connection = MongoDBConnection(config)
    return _default_connection

async def ensure_connection(config: Optional[MongoDBConfig] = None) -> MongoDBConnection:
    """Ensure MongoDB connection is established."""
    connection = get_connection(config)
    if not connection.is_connected:
        await connection.connect()
    return connection

# Export main classes and functions
__all__ = [
    'MongoDBConfig',
    'MongoDBConnection', 
    'get_connection',
    'ensure_connection',
    'MONGODB_AVAILABLE'
]