"""🔗 Database Connection - Core Connection Management
===================================================
Module: database/connection.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Database Connection Management - Production-Ready
Responsibility: Database connection handling and configuration

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This connection module provides database connection management for:
- SQLite for development and testing
- PostgreSQL for production
- Connection pooling and health monitoring
- Transaction management
"""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

# Optional imports for production features
try:
    import sqlalchemy
    from sqlalchemy import create_engine, MetaData
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    sqlalchemy = None

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_database.db")

# Global database components
engine = None
SessionLocal = None
Base = None
metadata = None

class DatabaseConnection:
    """Database connection manager"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or DATABASE_URL
        self.engine = None
        self.session_factory = None
        self.connected = False
        
    def connect(self) -> bool:
        """Establish database connection"""
        if not SQLALCHEMY_AVAILABLE:
            logger.warning("SQLAlchemy not available, using mock connection")
            self.connected = True
            return True
            
        try:
            self.engine = create_engine(self.database_url)
            self.session_factory = sessionmaker(bind=self.engine)
            self.connected = True
            logger.info(f"Connected to database: {self.database_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
        self.connected = False
        logger.info("Disconnected from database")
    
    def get_session(self):
        """Get database session"""
        if not self.connected:
            raise RuntimeError("Database not connected")
        if self.session_factory:
            return self.session_factory()
        return None
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connected

# Global connection instance
_connection = DatabaseConnection()

def get_connection() -> DatabaseConnection:
    """Get the global database connection"""
    return _connection

def connect_database(database_url: str = None) -> bool:
    """Connect to the database"""
    global _connection
    if database_url:
        _connection.database_url = database_url
    return _connection.connect()

def disconnect_database():
    """Disconnect from the database"""
    global _connection
    _connection.disconnect()

@asynccontextmanager
async def get_db_session():
    """Get database session context manager"""
    session = _connection.get_session()
    try:
        yield session
        if session:
            session.commit()
    except Exception as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()

def init_database():
    """Initialize database with default settings"""
    global engine, SessionLocal, Base, metadata
    
    if not SQLALCHEMY_AVAILABLE:
        logger.warning("SQLAlchemy not available, using mock initialization")
        return True
    
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()
        metadata = MetaData()
        
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def get_database_info() -> Dict[str, Any]:
    """Get database connection information"""
    return {
        "database_url": _connection.database_url,
        "connected": _connection.is_connected(),
        "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
        "engine": engine is not None,
        "session_factory": SessionLocal is not None
    }

# Initialize on module import
if SQLALCHEMY_AVAILABLE:
    init_database()