"""
Database configuration and session management for MedCare-AI
Uses PostgreSQL with SQLAlchemy (async)
"""
import os
from typing import AsyncGenerator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import logging

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv(
    "MEDCARE_DATABASE_URL",
    "postgresql+asyncpg://ia2good:ia2good_password@localhost:5432/ia2good"
)

# For sync operations (migrations, etc.)
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=bool(os.getenv("SQL_ECHO", "false").lower() == "true"),
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
    # For development with connection issues
    poolclass=NullPool if os.getenv("ENV") == "development" else None,
)

# Create sync engine for migrations
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=bool(os.getenv("SQL_ECHO", "false").lower() == "true"),
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync session for migrations
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {e}", exc_info=True)
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database
    Creates all tables if they don't exist
    """
    try:
        async with engine.begin() as conn:
            # Import all models to register them
            from models import (
                patient, consultation, prescription,
                medical_record, medical_document,
                community, solidarity
            )
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)
        return False


async def check_db_connection() -> bool:
    """
    Check if database connection is working
    """
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}", exc_info=True)
        return False


def get_sync_db():
    """
    Get synchronous database session
    Used for migrations and scripts
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        raise
    finally:
        db.close()


# Health check function
async def db_health_check() -> dict:
    """
    Database health check for monitoring
    """
    try:
        is_connected = await check_db_connection()
        
        if is_connected:
            # Get some basic stats
            async with engine.connect() as conn:
                # Count tables
                result = await conn.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                table_count = result.scalar()
                
            return {
                "status": "healthy",
                "connected": True,
                "database_url": DATABASE_URL.split("@")[1] if "@" in DATABASE_URL else "unknown",
                "tables": table_count,
                "pool_size": engine.pool.size(),
                "checked_in_connections": engine.pool.checkedin(),
            }
        else:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": "Cannot connect to database"
            }
    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e)
        }


# Cleanup on shutdown
async def close_db():
    """
    Close database connections
    Call this on application shutdown
    """
    await engine.dispose()
    logger.info("Database connections closed")
