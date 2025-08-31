"""Ainflue Platform Main Entry Point
Run the complete AI-powered content protection and monetization platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import sys
import importlib.util
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Try to import the app, fallback to a simple one if complex dependencies fail
try:
    from api.asgi import app
    print("✓ Successfully imported api.asgi app")
    MAIN_APP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Could not import api.asgi app: {e}")
    MAIN_APP_AVAILABLE = False

# Try to import config, fallback to simple config if needed
try:
    # First try simple_config.py which has comprehensive settings
    import simple_config
    settings = simple_config.settings
    print("✓ Successfully imported simple_config.py")
    print(f"✓ Environment: {settings.app.environment}")
    print(f"✓ Debug mode: {settings.app.debug}")
    print(f"✓ Host: {settings.app.host}")
    print(f"✓ Port: {settings.app.port}")
except ImportError as e:
    try:
        # Fallback to unified app_config module
        import app_config
        settings = app_config.settings
        print("✓ Successfully imported app_config.py as fallback")
        print(f"✓ Environment: {settings.app.environment}")
        print(f"✓ Debug mode: {settings.app.debug}")
        print(f"✓ Host: {settings.app.host}")
        print(f"✓ Port: {settings.app.port}")
    except Exception as e:
        print(f"❌ Failed to import any config: {e}")
        # Create minimal fallback settings
        class MockSettings:
            class App:
                environment = "development"
                debug = True
                host = "127.0.0.1"
                port = 8000
            app = App()
        settings = MockSettings()
        print("⚠️  Using minimal fallback settings")

# Create minimal FastAPI app if main app not available
if not MAIN_APP_AVAILABLE:
    print("📦 Creating minimal FastAPI app for testing")
    
    from fastapi import FastAPI
    from pydantic import BaseModel
    
    app = FastAPI(
        title="Ainflue AI Platform",
        description="AI-Powered Content Protection & Monetization Platform",
        version="1.0.0"
    )
    
    class StatusResponse(BaseModel):
        message: str
        status: str
        environment: str
    
    @app.get("/", response_model=StatusResponse)
    async def root():
        return StatusResponse(
            message="Ainflue AI Platform is running!",
            status="success",
            environment=settings.app.environment
        )
    
    @app.get("/health", response_model=StatusResponse)
    async def health_check():
        return StatusResponse(
            message="Platform is healthy",
            status="operational",
            environment=settings.app.environment
        )

# Try to import optional components
try:
    from database.schema import create_tables
    CREATE_TABLES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Database schema not available: {e}")
    CREATE_TABLES_AVAILABLE = False

try:
    from core.logging import logger
    LOGGING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Core logging not available: {e}")
    import logging
    logger = logging.getLogger(__name__)
    LOGGING_AVAILABLE = False

import uvicorn


async def initialize_platform():
    """Initialize the platform on first run"""    try:
        logger.info("Initializing Ainflue platform...")
        
        # Create database tables if available
        if CREATE_TABLES_AVAILABLE:
            await create_tables()
            logger.info("Database tables created successfully")
        else:
            logger.info("Database initialization skipped (not available)")
        
        logger.info("Platform initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Platform initialization failed: {str(e)}")
        raise


def main():
    """Main entry point"""    logger.info("Starting Ainflue AI Platform")
    logger.info(f"Environment: {settings.app.environment}")
    logger.info(f"Debug mode: {settings.app.debug}")
    
    try:
        # Initialize platform if needed
        if settings.app.environment in ["development", "staging"]:
            if CREATE_TABLES_AVAILABLE:
                asyncio.run(initialize_platform())
            else:
                logger.info("Platform initialization skipped (database not available)")
        
        # Start the server
        uvicorn.run(
            "main:app",  # Use import string to avoid reload issues
            host=settings.app.host,
            port=settings.app.port,
            reload=False,  # Disable reload to avoid import string issues
            log_level="info",
            access_log=True,
            workers=1  # Use 1 worker for now to avoid issues
        )
        
    except KeyboardInterrupt:
        logger.info("Platform stopped by user")
    except Exception as e:
        logger.error(f"Platform startup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()