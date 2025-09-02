#!/usr/bin/env python3
"""IA Influencer Agent - Content Management System Index
==================================================

Central initialization and coordination hub for all content management engines
with dependency injection, service registration, and orchestration management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Expert Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ LEGAL WARNING: This code and concept are protected by intellectual property laws.
Any unauthorized copying, modification, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will 
result in legal action under German and international copyright laws.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Type
from datetime import datetime
import traceback
from pathlib import Path
import json

# Import all content engines
from .content_processor import ContentProcessor
from .format_handler import FormatHandler  
from .ai_enhancer import AIEnhancer
from .distribution_manager import DistributionManager
from .collaboration_hub import CollaborationHub
from .monetization_engine import MonetizationEngine
from .quality_assurance import QualityAssurance
from .protection_engine import ProtectionEngine
from .crawler_engine import CrawlerEngine
from .recommendation_engine import RecommendationEngine
from .performance_engine import PerformanceEngine
from .config import ContentConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContentManagementSystem:
    """
    Central orchestrator for all content management engines.
    
    This class provides unified access to all content processing capabilities,
    manages engine lifecycle, handles inter-engine communication, and ensures
    system-wide consistency and reliability.
    """
    
    def __init__(self, config: Optional[ContentConfig] = None):
        """
Initialize the content management system."""
        self.config = config or ContentConfig()
        self.engines = {}
        self.is_initialized = False
        self.startup_time = None
        self.health_status = "unknown"
        
        # Engine registry with initialization order
        self.engine_registry = {
            'config': ContentConfig,
            'content_processor': ContentProcessor,
            'format_handler': FormatHandler,
            'ai_enhancer': AIEnhancer,
            'quality_assurance': QualityAssurance,
            'protection_engine': ProtectionEngine,
            'distribution_manager': DistributionManager,
            'collaboration_hub': CollaborationHub,
            'monetization_engine': MonetizationEngine,
            'crawler_engine': CrawlerEngine,
            'recommendation_engine': RecommendationEngine,
            'performance_engine': PerformanceEngine
        }
        
        # Service dependencies mapping
        self.dependencies = {
            'ai_enhancer': ['content_processor', 'format_handler'],
            'quality_assurance': ['content_processor', 'format_handler'],
            'protection_engine': ['content_processor', 'ai_enhancer'],
            'distribution_manager': ['content_processor', 'quality_assurance'],
            'collaboration_hub': ['content_processor', 'quality_assurance'],
            'monetization_engine': ['distribution_manager', 'quality_assurance'],
            'crawler_engine': ['protection_engine'],
            'recommendation_engine': ['ai_enhancer', 'monetization_engine'],
            'performance_engine': []  # No dependencies
        }
    
    async def initialize(self) -> bool:
        """
        Initialize all engines in the correct dependency order.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        logger.info("🚀 Initializing IA Influencer Content Management System...")
        start_time = datetime.now()
        
        try:
            # Initialize engines in dependency order
            initialization_order = self._resolve_dependency_order()
            
            for engine_name in initialization_order:
                if engine_name in self.engine_registry:
                    success = await self._initialize_engine(engine_name)
                    if not success:
                        logger.error(f"❌ Failed to initialize engine: {engine_name}")
                        return False
            
            # Perform post-initialization validation
            validation_success = await self._validate_system()
            
            if validation_success:
                self.is_initialized = True
                self.startup_time = datetime.now()
                self.health_status = "healthy"
                
                initialization_time = (self.startup_time - start_time).total_seconds()
                logger.info(f"✅ Content Management System initialized successfully in {initialization_time:.2f}s")
                logger.info(f"📊 Engines loaded: {len(self.engines)}/{len(self.engine_registry)}")
                
                return True
            else:
                logger.error("❌ System validation failed after initialization")
                return False
                
        except Exception as e:
            logger.error(f"❌ System initialization failed: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def _resolve_dependency_order(self) -> List[str]:
        """Resolve engine initialization order based on dependencies."""
        ordered = []
        remaining = set(self.engine_registry.keys())
        
        # Start with engines that have no dependencies
        while remaining:
            ready = []
            for engine in remaining:
                deps = self.dependencies.get(engine, [])
                if all(dep in ordered for dep in deps):
                    ready.append(engine)
            
            if not ready:
                # Circular dependency or missing dependency
                logger.warning(f"⚠️ Possible circular dependency detected. Remaining: {remaining}")
                ready = list(remaining)  # Force initialization
            
            for engine in ready:
                ordered.append(engine)
                remaining.remove(engine)
        
        return ordered
    
    async def _initialize_engine(self, engine_name: str) -> bool:
        """Initialize a specific engine."""
        try:
            engine_class = self.engine_registry[engine_name]
            
            logger.info(f"🔧 Initializing {engine_name}...")
            
            # Special handling for config
            if engine_name == 'config':
                self.engines[engine_name] = self.config
                return True
            
            # Initialize engine with dependencies
            dependencies = {}
            for dep_name in self.dependencies.get(engine_name, []):
                if dep_name in self.engines:
                    dependencies[dep_name] = self.engines[dep_name]
            
            # Create engine instance
            if dependencies:
                engine_instance = engine_class(config=self.config, **dependencies)
            else:
                engine_instance = engine_class(config=self.config)
            
            # Initialize if async initialization available
            if hasattr(engine_instance, 'initialize') and callable(getattr(engine_instance, 'initialize')):
                if asyncio.iscoroutinefunction(engine_instance.initialize):
                    await engine_instance.initialize()
                else:
                    engine_instance.initialize()
            
            self.engines[engine_name] = engine_instance
            logger.info(f"✅ {engine_name} initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {engine_name}: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    async def _validate_system(self) -> bool:
        """Validate system integrity after initialization."""
        logger.info("🔍 Validating system integrity...")
        
        validation_checks = [
            self._validate_engine_connectivity(),
            self._validate_configuration(),
            self._validate_resources(),
            self._validate_security()
        ]
        
        results = await asyncio.gather(*validation_checks, return_exceptions=True)
        
        all_passed = all(result is True for result in results if not isinstance(result, Exception))
        
        if all_passed:
            logger.info("✅ System validation passed")
        else:
            logger.error("❌ System validation failed")
            for i, result in enumerate(results):
                if isinstance(result, Exception) or result is False:
                    logger.error(f"Validation check {i+1} failed: {result}")
        
        return all_passed
    
    async def _validate_engine_connectivity(self) -> bool:
        """Validate that all engines can communicate properly."""
        try:
            # Test basic engine availability
            required_engines = ['content_processor', 'format_handler', 'ai_enhancer']
            for engine_name in required_engines:
                if engine_name not in self.engines:
                    logger.error(f"Critical engine missing: {engine_name}")
                    return False
            
            # Test inter-engine communication
            for engine_name, engine in self.engines.items():
                if hasattr(engine, 'health_check') and callable(getattr(engine, 'health_check')):
                    try:
                        if asyncio.iscoroutinefunction(engine.health_check):
                            health_status = await engine.health_check()
                        else:
                            health_status = engine.health_check()
                        
                        if not health_status:
                            logger.warning(f"⚠️ Engine {engine_name} health check failed")
                    except Exception as e:
                        logger.warning(f"⚠️ Engine {engine_name} health check error: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Engine connectivity validation failed: {e}")
            return False
    
    async def _validate_configuration(self) -> bool:
        """Validate system configuration."""
        try:
            # Check essential configuration
            if not hasattr(self.config, 'CONTENT_PROCESSING'):
                logger.error("Missing content processing configuration")
                return False
            
            # Validate directory structure
            required_dirs = ['temp', 'uploads', 'processed', 'protected']
            for dir_name in required_dirs:
                dir_path = Path(dir_name)
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created required directory: {dir_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    async def _validate_resources(self) -> bool:
        """Validate system resources."""
        try:
            import psutil
            
            # Memory check
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                logger.warning(f"⚠️ High memory usage: {memory.percent}%")
            
            # Disk space check
            disk = psutil.disk_usage('.')
            if disk.percent > 90:
                logger.warning(f"⚠️ Low disk space: {disk.percent}% used")
            
            return True
            
        except ImportError:
            logger.warning("⚠️ psutil not available for resource validation")
            return True
        except Exception as e:
            logger.error(f"Resource validation failed: {e}")
            return False
    
    async def _validate_security(self) -> bool:
        """Validate security settings."""
        try:
            # Check for sensitive files exposure
            sensitive_patterns = ['.env', '*.key', '*.pem']
            for pattern in sensitive_patterns:
                if list(Path('.').glob(pattern)):
                    logger.warning(f"⚠️ Sensitive files detected: {pattern}")
            
            return True
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            return False
    
    def get_engine(self, engine_name: str) -> Optional[Any]:
        """Get a specific engine instance."""
        return self.engines.get(engine_name)
    
    def get_all_engines(self) -> Dict[str, Any]:
        """
Get all engine instances."""
        return self.engines.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """
Perform comprehensive system health check."""
        if not self.is_initialized:
            return {
                'status': 'not_initialized',
                'message': 'System not initialized'
            }
        
        health_results = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - self.startup_time).total_seconds(),
            'engines': {},
            'system_metrics': {}
        }
        
        # Check each engine
        for engine_name, engine in self.engines.items():
            if hasattr(engine, 'health_check') and callable(getattr(engine, 'health_check')):
                try:
                    if asyncio.iscoroutinefunction(engine.health_check):
                        engine_health = await engine.health_check()
                    else:
                        engine_health = engine.health_check()
                    
                    health_results['engines'][engine_name] = {
                        'status': 'healthy' if engine_health else 'unhealthy',
                        'details': engine_health if isinstance(engine_health, dict) else {}
                    }
                except Exception as e:

                    logger.error(f"Error: {e}")

                    raise
                    health_results['engines'][engine_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
            else:
                health_results['engines'][engine_name] = {
                    'status': 'unknown',
                    'message': 'No health check available'
                }
        
        # System metrics
        try:
            import psutil
            process = psutil.Process()
            health_results['system_metrics'] = {
                'memory_mb': round(process.memory_info().rss / 1024 / 1024, 2),
                'cpu_percent': process.cpu_percent(),
                'threads': process.num_threads(),
                'open_files': process.num_fds() if hasattr(process, 'num_fds') else 'N/A'
            }
        except ImportError:
            health_results['system_metrics']['error'] = 'psutil not available'
        
        # Determine overall status
        engine_statuses = [engine['status'] for engine in health_results['engines'].values()]
        if 'error' in engine_statuses:
            health_results['status'] = 'degraded'
        elif 'unhealthy' in engine_statuses:
            health_results['status'] = 'warning'
        
        return health_results
    
    async def shutdown(self):
        """
Gracefully shutdown all engines."""
        logger.info("🛑 Shutting down Content Management System...")
        
        # Shutdown engines in reverse dependency order
        shutdown_order = list(reversed(self._resolve_dependency_order()))
        
        for engine_name in shutdown_order:
            if engine_name in self.engines:
                engine = self.engines[engine_name]
                
                if hasattr(engine, 'shutdown') and callable(getattr(engine, 'shutdown')):
                    try:
                        logger.info(f"🔧 Shutting down {engine_name}...")
                        if asyncio.iscoroutinefunction(engine.shutdown):
                            await engine.shutdown()
                        else:
                            engine.shutdown()
                    except Exception as e:
                        logger.error(f"❌ Error shutting down {engine_name}: {e}")
        
        self.engines.clear()
        self.is_initialized = False
        self.health_status = "shutdown"
        
        logger.info("✅ Content Management System shutdown complete")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        return {
            'system_name': 'IA Influencer Agent - Content Management System',
            'version': '1.0.0',
            'author': 'Fahed Mlaiel <mlaiel@live.de>',
            'initialized': self.is_initialized,
            'startup_time': self.startup_time.isoformat() if self.startup_time else None,
            'health_status': self.health_status,
            'engines_count': len(self.engines),
            'engines_list': list(self.engines.keys()),
            'dependencies': self.dependencies,
            'initialization_order': self._resolve_dependency_order()
        }
    
    async def process_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        High-level content processing orchestration.
        
        This method coordinates multiple engines to process content through
        the complete pipeline: processing → enhancement → quality assurance → protection.
        """
        if not self.is_initialized:
            raise RuntimeError("System not initialized")
        
        logger.info("🎬 Starting content processing pipeline...")
        
        try:
            # Step 1: Content Processing
            processor = self.get_engine('content_processor')
            if not processor:
                raise RuntimeError("Content processor not available")
            
            processed_content = await processor.process_content(content_data)
            
            # Step 2: AI Enhancement (if enabled)
            if self.config.AI_ENHANCEMENT.get('enabled', True):
                enhancer = self.get_engine('ai_enhancer')
                if enhancer:
                    processed_content = await enhancer.enhance_content(processed_content)
            
            # Step 3: Quality Assurance
            qa_engine = self.get_engine('quality_assurance')
            if qa_engine:
                quality_result = await qa_engine.validate_content(processed_content)
                processed_content['quality_score'] = quality_result.get('score', 0)
                processed_content['quality_issues'] = quality_result.get('issues', [])
            
            # Step 4: Content Protection
            protection = self.get_engine('protection_engine')
            if protection:
                protection_result = await protection.protect_content(processed_content)
                processed_content['protection_fingerprint'] = protection_result.get('fingerprint')
                processed_content['protection_status'] = protection_result.get('status')
            
            logger.info("✅ Content processing pipeline completed successfully")
            
            return {
                'status': 'success',
                'content': processed_content,
                'pipeline_stages': ['processing', 'enhancement', 'quality_assurance', 'protection'],
                'processing_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Content processing pipeline failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'pipeline_stages': ['processing'],
                'processing_time': datetime.now().isoformat()
            }


# Global system instance
_content_system = None


async def initialize_content_system(config: Optional[ContentConfig] = None) -> ContentManagementSystem:
    """Initialize and return the global content management system."""
    global _content_system
    
    if _content_system is None:
        _content_system = ContentManagementSystem(config)
        await _content_system.initialize()
    
    return _content_system


def get_content_system() -> Optional[ContentManagementSystem]:
    """
Get the global content management system instance."""
    return _content_system


async def shutdown_content_system():
    """
Shutdown the global content management system."""
    global _content_system
    
    if _content_system:
        await _content_system.shutdown()
        _content_system = None


# Convenience functions for direct engine access
def get_content_processor():
    """
Get the content processor engine."""
    system = get_content_system()
    return system.get_engine('content_processor') if system else None


def get_ai_enhancer():
    """
Get the AI enhancer engine."""
    system = get_content_system()
    return system.get_engine('ai_enhancer') if system else None


def get_distribution_manager():
    """
Get the distribution manager engine."""
    system = get_content_system()
    return system.get_engine('distribution_manager') if system else None


def get_monetization_engine():
    """
Get the monetization engine."""
    system = get_content_system()
    return system.get_engine('monetization_engine') if system else None


def get_protection_engine():
    """
Get the content protection engine."""
    system = get_content_system()
    return system.get_engine('protection_engine') if system else None


# Module-level initialization for easy imports
__all__ = [
    'ContentManagementSystem',
    'initialize_content_system',
    'get_content_system',
    'shutdown_content_system',
    'get_content_processor',
    'get_ai_enhancer',
    'get_distribution_manager',
    'get_monetization_engine',
    'get_protection_engine'
]


# Example usage and integration test
async def main():
    """
Example usage of the content management system."""
    print("""╔══════════════════════════════════════════════════════════════════════════════╗
║                IA Influencer Agent - Content Management System              ║
║                                                                              ║
║  Industrial-Grade Content Processing Platform                               ║
║  Author: Fahed Mlaiel <mlaiel@live.de>                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Initialize system
        system = await initialize_content_system()
        
        # Display system information
        info = system.get_system_info()
        print(f"🚀 System initialized successfully!")
        print(f"   - Engines loaded: {info['engines_count']}")
        print(f"   - Health status: {info['health_status']}")
        print(f"   - Startup time: {info['startup_time']}")
        
        # Perform health check
        health = await system.health_check()
        print(f"\n📊 System Health: {health['status']}")
        print(f"   - Uptime: {health['uptime_seconds']:.2f} seconds")
        print(f"   - Memory usage: {health['system_metrics'].get('memory_mb', 'N/A')} MB")
        
        # Example content processing
        sample_content = {
            'type': 'audio',
            'format': 'mp3',
            'title': 'Sample Audio Content',
            'data': 'sample_audio_data',
            'metadata': {
                'artist': 'Sample Artist',
                'genre': 'Electronic',
                'duration': 180
            }
        }
        
        print(f"\n🎬 Processing sample content...")
        result = await system.process_content(sample_content)
        
        if result['status'] == 'success':
            print(f"✅ Content processed successfully!")
            print(f"   - Pipeline stages: {result['pipeline_stages']}")
            print(f"   - Quality score: {result['content'].get('quality_score', 'N/A')}")
            print(f"   - Protection status: {result['content'].get('protection_status', 'N/A')}")
        else:
            print(f"❌ Content processing failed: {result.get('error')}")
        
        # Shutdown system
        await shutdown_content_system()
        print(f"\n🛑 System shutdown completed")
        
    except Exception as e:

        
        logger.error(f"Error: {e}")

        
        raise
        print(f"❌ System error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
