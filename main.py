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
from database.schema import create_tables
from core.logging import logger
from config import settings

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
            app,
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