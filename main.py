"""
Ainflue Platform Main Entry Point
Run the complete AI-powered content protection and monetization platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from api.main import app
try:
    from database.schema import create_tables
except ImportError:
    # Fallback if database modules are not available
    async def create_tables():
        print("Database creation skipped - dependencies not available")
        pass
try:
    from core.logging import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
try:
    from config import settings
except ImportError:
    # Create minimal settings fallback
    class Settings:
        class App:
            environment = "development"
            debug = True
            host = "0.0.0.0"
            port = 8000
        class Monitoring:
            log_level = "INFO"
        app = App()
        monitoring = Monitoring()
    settings = Settings()

import uvicorn


async def initialize_platform():
    """Initialize the platform on first run"""
    try:
        logger.info("Initializing Ainflue platform...")
        
        # Create database tables
        await create_tables()
        
        logger.info("Platform initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Platform initialization failed: {str(e)}")
        raise


def main():
    """Main entry point"""
    logger.info("Starting Ainflue AI Platform")
    logger.info(f"Environment: {settings.app.environment}")
    logger.info(f"Debug mode: {settings.app.debug}")
    
    try:
        # Initialize platform if needed
        if settings.app.environment in ["development", "staging"]:
            asyncio.run(initialize_platform())
        
        # Start the server
        uvicorn.run(
            "api.main:app",  # Pass as string for reload to work
            host=settings.app.host,
            port=settings.app.port,
            reload=settings.app.debug,
            log_level=settings.monitoring.log_level.lower(),
            access_log=True,
            workers=1 if settings.app.debug else 4
        )
        
    except KeyboardInterrupt:
        logger.info("Platform stopped by user")
    except Exception as e:
        logger.error(f"Platform startup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()