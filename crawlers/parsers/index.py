"""Parsers Module Index - IA Influencer Agent Platform
===================================================

Central index and initialization module for the parsers system.
Provides unified entry point for all parsing operations and services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de

Development Team Specialties:
- Lead AI Developer & Architect: Fahed Mlaiel
- Backend Senior Engineer: Advanced Python/FastAPI systems
- ML Engineer: Content analysis and fingerprinting
- Audio Processing Specialist: Multi-format audio analysis  
- DevOps Engineer: Infrastructure and deployment
- Database Administrator: Performance optimization
- Security Expert: Content protection and compliance
- Microservices Architect: Scalable system design
"""import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .parser_manager import ParserManager
from .parser_factory import ParserFactory
from .parser_config import ParserConfig
from .exceptions import ParserInitializationError


class ParsersIndex:
    """    Central index for parsers module initialization and management
    """    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize parsers index"""        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.factory = ParserFactory(self.config)
        self.manager = ParserManager(self.factory, self.config)
        self._initialized = False
    
    def _load_config(self, config_path: Optional[str] = None) -> ParserConfig:
        """Load parser configuration"""        try:
            if config_path:
                return ParserConfig.from_file(config_path)
            else:
                # Load default configuration
                default_config_path = Path(__file__).parent / "config" / "default.yml"
                if default_config_path.exists():
                    return ParserConfig.from_file(str(default_config_path))
                else:
                    return ParserConfig.default()
        except Exception as e:
            self.logger.error(f"Failed to load parser configuration: {e}")
            raise ParserInitializationError(f"Configuration loading failed: {e}")
    
    async def initialize(self) -> None:
        """Initialize all parser components"""        try:
            self.logger.info("Initializing parsers module...")
            
            # Initialize factory
            await self.factory.initialize()
            
            # Initialize manager
            await self.manager.initialize()
            
            # Validate all parsers
            await self._validate_parsers()
            
            self._initialized = True
            self.logger.info("Parsers module initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize parsers module: {e}")
            raise ParserInitializationError(f"Initialization failed: {e}")
    
    async def _validate_parsers(self) -> None:
        """Validate all available parsers"""        platform_parsers = await self.factory.get_available_platform_parsers()
        media_parsers = await self.factory.get_available_media_parsers()
        
        self.logger.info(f"Validated {len(platform_parsers)} platform parsers")
        self.logger.info(f"Validated {len(media_parsers)} media parsers")
        
        if not platform_parsers or not media_parsers:
            raise ParserInitializationError("Critical parsers missing")
    
    async def shutdown(self) -> None:
        """Shutdown parsers module"""        try:
            self.logger.info("Shutting down parsers module...")
            
            await self.manager.shutdown()
            await self.factory.shutdown()
            
            self._initialized = False
            self.logger.info("Parsers module shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def get_manager(self) -> ParserManager:
        """Get parser manager instance"""        if not self._initialized:
            raise ParserInitializationError("Module not initialized")
        return self.manager
    
    def get_factory(self) -> ParserFactory:
        """Get parser factory instance"""        if not self._initialized:
            raise ParserInitializationError("Module not initialized")
        return self.factory
    
    def get_config(self) -> ParserConfig:
        """Get parser configuration"""        return self.config
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all parsers"""        if not self._initialized:
            return {"status": "not_initialized", "healthy": False}
        
        try:
            manager_health = await self.manager.health_check()
            factory_health = await self.factory.health_check()
            
            return {
                "status": "healthy",
                "healthy": True,
                "manager": manager_health,
                "factory": factory_health,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


# Global parsers index instance
_parsers_index: Optional[ParsersIndex] = None


async def get_parsers_index(config_path: Optional[str] = None) -> ParsersIndex:
    """Get or create global parsers index instance"""    global _parsers_index
    
    if _parsers_index is None:
        _parsers_index = ParsersIndex(config_path)
        await _parsers_index.initialize()
    
    return _parsers_index


async def initialize_parsers(config_path: Optional[str] = None) -> ParsersIndex:
    """Initialize parsers module"""    return await get_parsers_index(config_path)


async def shutdown_parsers() -> None:
    """Shutdown parsers module"""    global _parsers_index
    
    if _parsers_index:
        await _parsers_index.shutdown()
        _parsers_index = None


__all__ = [
    'ParsersIndex',
    'get_parsers_index', 
    'initialize_parsers',
    'shutdown_parsers'
]
