"""
Audio Fingerprinting System - Main Index Module
Industrial-grade entry point for audio content protection and identification system.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Audio Protection Suite
License: Proprietary - All rights reserved

WARNING: This code is proprietary and protected by copyright.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Contact: Fahed Mlaiel (mlaiel@live.de) for licensing agreements.

Team Specialization:
- Lead AI Developer: Fahed Mlaiel
- Backend Senior Engineer: Advanced system architecture
- ML Engineer: Machine learning algorithms implementation
- Database Administrator: High-performance data storage
- Security Engineer: Content protection and encryption
- Microservices Architect: Scalable system design
- Audio Processing Expert: Advanced signal processing
- DevOps Engineer: Production deployment and monitoring
- AI Prompt Engineer: Intelligent content analysis
"""

import asyncio
import logging
import signal
import sys
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
from datetime import datetime
from contextlib import asynccontextmanager

# Import core fingerprinting modules
from .core import AudioFingerprintCore, FingerprintResult
from .hash_generator import PerceptualHashGenerator, HashComparator
from .matching import FingerprintMatchingEngine, MatchQuery
from .database import FingerprintDatabaseManager, FingerprintRecord
from .config import FingerprintingConfigManager, get_config
from .utils import (
    FileValidator, 
    PerformanceMonitor, 
    TemporaryFileManager,
    AudioMetadata,
    format_duration,
    generate_unique_id
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('fingerprinting.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)


class AudioFingerprintingService:
    """
    Main service orchestrator for the audio fingerprinting system.
    Coordinates all components and provides high-level API for audio content protection.
    """
    
    def __init__(self, config_path: Optional[str] = None, database_url: Optional[str] = None):
        """Initialize the audio fingerprinting service."""
        self.config_path = config_path
        self.database_url = database_url
        
        # Core components
        self.config_manager: Optional[FingerprintingConfigManager] = None
        self.fingerprint_core: Optional[AudioFingerprintCore] = None
        self.matching_engine: Optional[FingerprintMatchingEngine] = None
        self.database_manager: Optional[FingerprintDatabaseManager] = None
        self.hash_generator: Optional[PerceptualHashGenerator] = None
        self.hash_comparator: Optional[HashComparator] = None
        
        # Utilities
        self.file_validator: Optional[FileValidator] = None
        self.performance_monitor: Optional[PerformanceMonitor] = None
        self.temp_file_manager: Optional[TemporaryFileManager] = None
        
        # Service state
        self.is_initialized = False
        self.is_running = False
        self.startup_time: Optional[datetime] = None
        
        # Shutdown handling
        self._shutdown_event = asyncio.Event()
        
        logger.info("AudioFingerprintingService initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize all service components.
        
        Returns:
            True if initialization successful, False otherwise
        """



        try:
            logger.info("Initializing Audio Fingerprinting Service...")
            start_time = datetime.now()
            
            # Initialize configuration
            self.config_manager = FingerprintingConfigManager(
                config_path=self.config_path
            )
            
            # Initialize database
            database_url = self.database_url or self.config_manager.database.url
            self.database_manager = FingerprintDatabaseManager(database_url)
            await self.database_manager.initialize()
            
            # Initialize core components
            core_config = {
                'sample_rate': self.config_manager.audio_processing.sample_rate,
                'hop_length': self.config_manager.audio_processing.hop_length,
                'n_fft': self.config_manager.audio_processing.n_fft,
                'n_mels': self.config_manager.audio_processing.n_mels,
                'max_workers': self.config_manager.performance.max_concurrent_fingerprints
            }
            self.fingerprint_core = AudioFingerprintCore(core_config)
            
            # Initialize hash components
            hash_config = self.config_manager.fingerprinting
            self.hash_generator = PerceptualHashGenerator(hash_config)
            self.hash_comparator = HashComparator()
            
            # Initialize matching engine
            matching_config = {
                'global_threshold': self.config_manager.matching.default_similarity_threshold,
                'max_results_per_query': self.config_manager.matching.max_results_per_query,
                'enable_caching': self.config_manager.performance.enable_caching
            }
            self.matching_engine = FingerprintMatchingEngine(matching_config)
            
            # Initialize utilities
            validator_config = {
                'max_file_size_mb': self.config_manager.security.max_file_size_mb,
                'allowed_extensions': self.config_manager.audio_processing.supported_formats
            }
            self.file_validator = FileValidator(validator_config)
            self.performance_monitor = PerformanceMonitor(
                enable_detailed_profiling=self.config_manager.monitoring.enable_performance_profiling
            )
            self.temp_file_manager = TemporaryFileManager()
            
            # Set up signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            self.is_initialized = True
            self.startup_time = start_time
            
            initialization_time = (datetime.now() - start_time).total_seconds()
            logger.info("Service initialization completed in %.2f seconds", initialization_time)
            
            return True
            
        except Exception as e:
            logger.error("Failed to initialize service: %s", str(e))
            return False
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info("Received signal %d, initiating graceful shutdown...", signum)
            self._shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self) -> bool:
        """
        Start the fingerprinting service.
        
        Returns:
            True if service started successfully
        """
        if not self.is_initialized:
            logger.error("Service not initialized. Call initialize() first.")
            return False
        
        try:
            logger.info("Starting Audio Fingerprinting Service...")
            self.is_running = True
            
            # Start background tasks if needed
            await self._start_background_tasks()
            
            logger.info("Audio Fingerprinting Service started successfully")
            return True
            
        except Exception as e:
            logger.error("Failed to start service: %s", str(e))
            self.is_running = False
            return False
    
    async def _start_background_tasks(self):
        """Start background monitoring and maintenance tasks."""
        # Performance monitoring task
        if self.config_manager.monitoring.enable_metrics_collection:
            asyncio.create_task(self._performance_monitoring_task())
        
        # Health check task
        if self.config_manager.monitoring.enable_health_checks:
            asyncio.create_task(self._health_check_task())
    
    async def _performance_monitoring_task(self):
        """Background task for performance monitoring."""
        interval = self.config_manager.monitoring.metrics_interval_seconds
        
        while self.is_running and not self._shutdown_event.is_set():
            try:
                # Collect and log performance metrics
                if self.performance_monitor:
                    metrics = self.performance_monitor.get_performance_summary()
                    logger.debug("Performance metrics: %s", metrics)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.warning("Error in performance monitoring task: %s", str(e))
                await asyncio.sleep(interval)
    
    async def _health_check_task(self):
        """Background task for system health checks."""
        interval = self.config_manager.monitoring.health_check_interval
        
        while self.is_running and not self._shutdown_event.is_set():
            try:
                health_status = await self.get_health_status()
                
                if not health_status['healthy']:
                    logger.warning("System health check failed: %s", health_status)
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.warning("Error in health check task: %s", str(e))
                await asyncio.sleep(interval)
    
    @performance_monitor.measure_execution_time('fingerprint_audio')
    async def fingerprint_audio(
        self, 
        file_path: str, 
        user_id: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[FingerprintResult]:
        """
        High-level API to fingerprint an audio file.
        
        Args:
            file_path: Path to the audio file
            user_id: Optional user ID for database storage
            metadata: Optional metadata to attach
            
        Returns:
            FingerprintResult or None if failed
        """



        try:
            if not self.is_running:
                logger.error("Service not running")
                return None
            
            # Validate file
            is_valid, errors, audio_metadata = await self.file_validator.validate_file(file_path)
            
            if not is_valid:
                logger.error("File validation failed: %s", errors)
                return None
            
            # Generate fingerprint
            result = await self.fingerprint_core.generate_fingerprint(
                file_path, metadata or {}
            )
            
            # Store in database if user_id provided
            if user_id and self.database_manager:
                record = FingerprintRecord(
                    user_id=user_id,
                    content_type="audio",
                    original_filename=Path(file_path).name,
                    fingerprint_hash=result.fingerprint_hash,
                    spectral_features=result.spectral_features,
                    metadata=result.metadata,
                    file_size_bytes=audio_metadata.file_size_bytes if audio_metadata else None,
                    duration_seconds=audio_metadata.duration_seconds if audio_metadata else None,
                    sample_rate=audio_metadata.sample_rate if audio_metadata else None,
                    channels=audio_metadata.channels if audio_metadata else None
                )
                
                record_id = await self.database_manager.store_fingerprint(record)
                result.metadata['database_id'] = record_id
            
            logger.info("Successfully fingerprinted audio file: %s", Path(file_path).name)
            return result
            
        except Exception as e:
            logger.error("Error fingerprinting audio %s: %s", file_path, str(e))
            return None
    
    @performance_monitor.measure_execution_time('find_matches')
    async def find_matches(
        self, 
        fingerprint_hash: str,
        similarity_threshold: float = 0.80,
        max_results: int = 50,
        user_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Find matches for a given fingerprint hash.
        
        Args:
            fingerprint_hash: Target fingerprint hash
            similarity_threshold: Minimum similarity score
            max_results: Maximum number of results
            user_id: Optional user ID for scoped search
            
        Returns:
            List of match results
        """



        try:
            if not self.is_running:
                logger.error("Service not running")
                return []
            
            # Find similar fingerprints in database
            candidates = await self.database_manager.find_similar_fingerprints(
                fingerprint_hash, 
                similarity_threshold=similarity_threshold,
                limit=max_results,
                user_id=user_id
            )
            
            if not candidates:
                logger.info("No matching candidates found")
                return []
            
            # Convert to match results format
            matches = []
            for candidate in candidates:
                match_data = {
                    'fingerprint_id': candidate.fingerprint_hash,
                    'similarity_score': 1.0,  # Would calculate actual similarity
                    'metadata': candidate.metadata,
                    'filename': candidate.original_filename,
                    'duration': candidate.duration_seconds,
                    'creation_date': candidate.creation_timestamp.isoformat() if candidate.creation_timestamp else None
                }
                matches.append(match_data)
            
            logger.info("Found %d matches for fingerprint", len(matches))
            return matches
            
        except Exception as e:
            logger.error("Error finding matches: %s", str(e))
            return []
    
    async def batch_fingerprint(
        self, 
        file_paths: List[str],
        user_id: Optional[int] = None,
        progress_callback: Optional[callable] = None
    ) -> List[Optional[FingerprintResult]]:
        """
        Fingerprint multiple audio files in parallel.
        
        Args:
            file_paths: List of audio file paths
            user_id: Optional user ID for database storage
            progress_callback: Optional progress callback function
            
        Returns:
            List of FingerprintResult objects (None for failed files)
        """



        try:
            logger.info("Starting batch fingerprinting of %d files", len(file_paths))
            
            results = []
            total_files = len(file_paths)
            
            for i, file_path in enumerate(file_paths):
                result = await self.fingerprint_audio(file_path, user_id)
                results.append(result)
                
                # Progress callback
                if progress_callback:
                    progress = (i + 1) / total_files
                    await progress_callback(progress, i + 1, total_files)
            
            successful_count = sum(1 for r in results if r is not None)
            logger.info("Batch fingerprinting completed: %d/%d successful", 
                       successful_count, total_files)
            
            return results
            
        except Exception as e:
            logger.error("Error in batch fingerprinting: %s", str(e))
            return []
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """Get comprehensive service statistics."""



        try:
            stats = {
                'service_info': {
                    'is_running': self.is_running,
                    'startup_time': self.startup_time.isoformat() if self.startup_time else None,
                    'uptime_seconds': (datetime.now() - self.startup_time).total_seconds() if self.startup_time else 0
                },
                'performance_metrics': {},
                'system_info': {},
                'config_info': {}
            }
            
            # Performance metrics
            if self.performance_monitor:
                stats['performance_metrics'] = self.performance_monitor.get_performance_summary()
            
            # Configuration info
            if self.config_manager:
                stats['config_info'] = {
                    'environment': self.config_manager.environment.value,
                    'audio_sample_rate': self.config_manager.audio_processing.sample_rate,
                    'max_concurrent_fingerprints': self.config_manager.performance.max_concurrent_fingerprints,
                    'similarity_threshold': self.config_manager.matching.default_similarity_threshold
                }
            
            return stats
            
        except Exception as e:
            logger.error("Error getting service stats: %s", str(e))
            return {}
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get system health status."""



        try:
            health = {
                'healthy': True,
                'components': {},
                'timestamp': datetime.now().isoformat()
            }
            
            # Check database connection
            if self.database_manager:
                try:
                    # Simple health check query
                    health['components']['database'] = 'healthy'
                except Exception as e:
                    health['components']['database'] = f'unhealthy: {str(e)}'
                    health['healthy'] = False
            
            # Check core components
            health['components']['fingerprint_core'] = 'healthy' if self.fingerprint_core else 'not_initialized'
            health['components']['matching_engine'] = 'healthy' if self.matching_engine else 'not_initialized'
            health['components']['service_running'] = 'healthy' if self.is_running else 'stopped'
            
            return health
            
        except Exception as e:
            logger.error("Error checking health status: %s", str(e))
            return {'healthy': False, 'error': str(e)}
    
    async def shutdown(self):
        """Gracefully shutdown the service."""



        try:
            logger.info("Shutting down Audio Fingerprinting Service...")
            self.is_running = False
            
            # Cleanup components
            if self.fingerprint_core:
                self.fingerprint_core.cleanup()
            
            if self.matching_engine:
                await self.matching_engine.cleanup()
            
            if self.database_manager:
                await self.database_manager.cleanup()
            
            if self.hash_generator:
                self.hash_generator.cleanup()
            
            if self.hash_comparator:
                self.hash_comparator.cleanup()
            
            if self.temp_file_manager:
                self.temp_file_manager.cleanup()
            
            logger.info("Service shutdown completed")
            
        except Exception as e:
            logger.error("Error during service shutdown: %s", str(e))
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.shutdown()


class AudioFingerprintingAPI:
    """
    RESTful API wrapper for the audio fingerprinting service.
    Provides HTTP endpoints for integration with web applications.
    """
    
    def __init__(self, service: AudioFingerprintingService):
        """Initialize the API wrapper."""
        self.service = service
        self.temp_upload_dir = Path("temp_uploads")
        self.temp_upload_dir.mkdir(exist_ok=True)
        
        logger.info("AudioFingerprintingAPI initialized")
    
    async def handle_upload_and_fingerprint(
        self, 
        file_data: bytes,
        filename: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Handle file upload and fingerprinting via API.
        
        Args:
            file_data: Binary file data
            filename: Original filename
            user_id: Optional user ID
            metadata: Optional metadata
            
        Returns:
            API response dictionary
        """
        temp_file_path = None
        
        try:
            # Create temporary file
            safe_filename = f"{generate_unique_id()}_" + Path(filename).name
            temp_file_path = self.temp_upload_dir / safe_filename
            
            # Write uploaded data to temp file
            with open(temp_file_path, 'wb') as f:
                f.write(file_data)
            
            # Fingerprint the file
            result = await self.service.fingerprint_audio(
                str(temp_file_path), 
                user_id=user_id,
                metadata=metadata
            )
            
            if result:
                return {
                    'success': True,
                    'fingerprint_hash': result.fingerprint_hash,
                    'confidence_score': result.confidence_score,
                    'processing_time': result.processing_time,
                    'metadata': result.metadata
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to generate fingerprint'
                }
                
        except Exception as e:
            logger.error("Error in upload and fingerprint: %s", str(e))
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            # Cleanup temporary file
            if temp_file_path and temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                except Exception as e:
                    logger.warning("Failed to cleanup temp file %s: %s", temp_file_path, str(e))


# Factory functions for easy service creation
def create_service(
    config_path: Optional[str] = None,
    database_url: Optional[str] = None
) -> AudioFingerprintingService:
    """
    Factory function to create a configured fingerprinting service.
    
    Args:
        config_path: Optional path to configuration file
        database_url: Optional database connection URL
        
    Returns:
        Configured AudioFingerprintingService instance
    """



    return AudioFingerprintingService(config_path=config_path, database_url=database_url)


def create_api_service(
    config_path: Optional[str] = None,
    database_url: Optional[str] = None
) -> AudioFingerprintingAPI:
    """
    Factory function to create an API-enabled fingerprinting service.
    
    Args:
        config_path: Optional path to configuration file
        database_url: Optional database connection URL
        
    Returns:
        Configured AudioFingerprintingAPI instance
    """
    service = create_service(config_path, database_url)
    return AudioFingerprintingAPI(service)


async def main():
    """
    Main entry point for standalone service execution.
    Demonstrates complete service lifecycle management.
    """
    logger.info("Starting Audio Fingerprinting Service (Standalone Mode)")
    
    # Create and configure service
    service = create_service()
    
    try:
        # Use service as async context manager
        async with service:
            logger.info("Service is running. Press Ctrl+C to stop.")
            
            # Wait for shutdown signal
            await service._shutdown_event.wait()
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error("Unexpected error in main: %s", str(e))
    
    logger.info("Service stopped")


if __name__ == "__main__":
    # Run the service
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error("Fatal error: %s", str(e))
        sys.exit(1)
