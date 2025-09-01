"""Data Ingestion Index
===================

Main index file for the data ingestion module providing centralized access
to all ingestion capabilities and orchestration functionality.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, BinaryIO
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis

from .content_ingestion_manager import ContentIngestionManager, IngestionRequest, IngestionResult
from .multi_format_processor import MultiFormatProcessor, ProcessingOptions, ProcessingQuality
from .metadata_extractor import MetadataExtractor, MetadataCollection
from .batch_ingestion_processor import BatchIngestionProcessor, BatchConfiguration, BatchItem, BatchResult

from ..storage.storage_manager import StorageManager
from ..validators.content_validator import ContentValidator
from ..quality.data_quality_manager import DataQualityManager
from ...core.exceptions import IngestionError
from ...core.config import get_settings


@dataclass
class IngestionCapabilities:
    """Available ingestion capabilities and configuration"""
    supported_formats: Dict[str, List[str]]
    max_file_size: int
    max_batch_size: int
    processing_modes: List[str]
    ai_features_enabled: bool
    quality_levels: List[str]
    concurrent_uploads: int


class DataIngestionOrchestrator:
    """
    Central orchestrator for all data ingestion operations.
    
    Provides unified interface for:
    - Single content ingestion
    - Batch processing
    - Metadata extraction
    - Multi-format processing
    - Quality management
    - Progress tracking
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis,
                 storage_manager: StorageManager, content_validator: ContentValidator,
                 quality_manager: DataQualityManager):
        """
        Initialize DataIngestionOrchestrator.
        
        Args:
            db_session: Async database session
            redis_client: Redis client
            storage_manager: Storage management service
            content_validator: Content validation service
            quality_manager: Data quality management service
        """
        self.db_session = db_session
        self.redis = redis_client
        self.storage_manager = storage_manager
        self.content_validator = content_validator
        self.quality_manager = quality_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.content_manager = ContentIngestionManager(
            db_session, redis_client, storage_manager, 
            content_validator, quality_manager
        )
        
        self.multi_processor = MultiFormatProcessor()
        self.metadata_extractor = MetadataExtractor()
        
        self.batch_processor = BatchIngestionProcessor(
            db_session, redis_client, self.content_manager,
            self.multi_processor, self.metadata_extractor
        )
        
        # Configuration
        self.settings = get_settings()
        
    async def ingest_single_content(self, request: IngestionRequest) -> IngestionResult:
        """
        Ingest single content item with full processing pipeline.
        
        Args:
            request: Content ingestion request
            
        Returns:
            Complete ingestion result
        """
        try:
            self.logger.info(f"Starting single content ingestion for user: {request.user_id}")
            
            # Validate request
            await self._validate_ingestion_request(request)
            
            # Process content
            result = await self.content_manager.ingest_content(request)
            
            # Log result
            if result.success:
                self.logger.info(f"Content ingestion successful: {result.content_id}")
            else:
                self.logger.warning(f"Content ingestion failed: {result.errors}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Single content ingestion failed: {str(e)}")
            raise IngestionError(f"Ingestion failed: {str(e)}")
    
    async def ingest_batch_content(self, items: List[Dict[str, Any]], 
                                 config: Dict[str, Any]) -> str:
        """
        Ingest multiple content items in batch.
        
        Args:
            items: List of content items to process
            config: Batch configuration
            
        Returns:
            Batch ID for tracking
        """
        try:
            self.logger.info(f"Starting batch ingestion with {len(items)} items")
            
            # Convert items to BatchItem objects
            batch_items = []
            for i, item_data in enumerate(items):
                batch_item = BatchItem(
                    item_id=f"item_{i}",
                    file_data=item_data['file_data'],
                    filename=item_data['filename'],
                    content_type=item_data.get('content_type', 'auto'),
                    metadata=item_data.get('metadata', {}),
                    priority=item_data.get('priority', 5)
                )
                batch_items.append(batch_item)
            
            # Create batch configuration
            batch_config = BatchConfiguration(
                batch_id=config.get('batch_id', ''),
                name=config.get('name', f"Batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
                description=config.get('description', ''),
                user_id=config['user_id'],
                processing_mode=config.get('processing_mode', 'parallel'),
                priority=config.get('priority', 'normal'),
                max_concurrent_items=config.get('max_concurrent_items', 10)
            )
            
            # Create and start batch
            batch_id = await self.batch_processor.create_batch(batch_items, batch_config)
            await self.batch_processor.start_batch_processing(batch_id)
            
            self.logger.info(f"Batch ingestion started: {batch_id}")
            return batch_id
            
        except Exception as e:
            self.logger.error(f"Batch ingestion failed: {str(e)}")
            raise IngestionError(f"Batch ingestion failed: {str(e)}")
    
    async def extract_metadata_only(self, file_data: Union[bytes, BinaryIO], 
                                  filename: str, include_ai: bool = True) -> MetadataCollection:
        """
        Extract metadata without full content ingestion.
        
        Args:
            file_data: Content file data
            filename: Original filename
            include_ai: Include AI-powered analysis
            
        Returns:
            Metadata collection
        """
        try:
            self.logger.info(f"Extracting metadata for: {filename}")
            
            metadata_collection = await self.metadata_extractor.extract_metadata(
                file_data, filename, include_ai_analysis=include_ai
            )
            
            self.logger.info(f"Metadata extraction completed: {metadata_collection.content_id}")
            return metadata_collection
            
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {str(e)}")
            raise IngestionError(f"Metadata extraction failed: {str(e)}")
    
    async def process_content_only(self, file_data: Union[bytes, BinaryIO], 
                                 filename: str, options: ProcessingOptions = None):
        """
        Process content without full ingestion pipeline.
        
        Args:
            file_data: Content file data
            filename: Original filename
            options: Processing configuration
            
        Returns:
            Processing result
        """
        try:
            self.logger.info(f"Processing content: {filename}")
            
            if options is None:
                options = ProcessingOptions(quality=ProcessingQuality.STANDARD)
            
            result = await self.multi_processor.process_content(
                file_data, filename, options=options
            )
            
            self.logger.info(f"Content processing completed: {result.success}")
            return result
            
        except Exception as e:
            self.logger.error(f"Content processing failed: {str(e)}")
            raise IngestionError(f"Content processing failed: {str(e)}")
    
    async def get_ingestion_status(self, content_id: str) -> Dict[str, Any]:
        """
        Get ingestion status for content or batch.
        
        Args:
            content_id: Content or batch identifier
            
        Returns:
            Status information
        """
        try:
            # Try as single content first
            status = await self.content_manager.get_ingestion_status(content_id)
            
            if status.get('status') == 'unknown':
                # Try as batch
                batch_result = await self.batch_processor.get_batch_status(content_id)
                if batch_result:
                    status = {
                        'content_id': content_id,
                        'status': batch_result.status.value,
                        'progress': {
                            'total_items': batch_result.progress.total_items,
                            'processed_items': batch_result.progress.processed_items,
                            'successful_items': batch_result.progress.successful_items,
                            'failed_items': batch_result.progress.failed_items
                        }
                    }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get ingestion status: {str(e)}")
            return {'content_id': content_id, 'status': 'error', 'message': str(e)}
    
    async def get_batch_metrics(self, batch_id: str) -> Dict[str, Any]:
        """
        Get detailed batch processing metrics.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Comprehensive metrics
        """
        try:
            return await self.batch_processor.get_batch_metrics(batch_id)
            
        except Exception as e:
            self.logger.error(f"Failed to get batch metrics: {str(e)}")
            return {}
    
    async def list_active_operations(self) -> Dict[str, Any]:
        """
        List all active ingestion operations.
        
        Returns:
            Summary of active operations
        """
        try:
            active_batches = await self.batch_processor.list_active_batches()
            
            return {
                'active_batches': active_batches,
                'total_active_batches': len(active_batches),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list active operations: {str(e)}")
            return {'error': str(e)}
    
    async def pause_batch(self, batch_id: str) -> bool:
        """Pause batch processing"""
        try:
            return await self.batch_processor.pause_batch(batch_id)
        except Exception as e:
            self.logger.error(f"Failed to pause batch: {str(e)}")
            return False
    
    async def resume_batch(self, batch_id: str) -> bool:
        """Resume paused batch processing"""
        try:
            return await self.batch_processor.resume_batch(batch_id)
        except Exception as e:
            self.logger.error(f"Failed to resume batch: {str(e)}")
            return False
    
    async def cancel_batch(self, batch_id: str) -> bool:
        """Cancel batch processing"""
        try:
            return await self.batch_processor.cancel_batch(batch_id)
        except Exception as e:
            self.logger.error(f"Failed to cancel batch: {str(e)}")
            return False
    
    async def cleanup_old_operations(self, hours: int = 24) -> Dict[str, int]:
        """
        Cleanup old completed operations.
        
        Args:
            hours: Remove operations older than this many hours
            
        Returns:
            Cleanup statistics
        """
        try:
            cleaned_batches = await self.batch_processor.cleanup_completed_batches(hours)
            
            return {
                'cleaned_batches': cleaned_batches,
                'cleanup_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
            return {'error': str(e)}
    
    def get_capabilities(self) -> IngestionCapabilities:
        """
        Get current ingestion capabilities and limits.
        
        Returns:
            Ingestion capabilities configuration
        """
        try:
            # Collect supported formats from all processors
            supported_formats = {}
            
            # From multi-format processor
            formats = self.multi_processor.get_supported_formats()
            supported_formats.update(formats)
            
            # From metadata extractor
            metadata_formats = self.metadata_extractor.get_supported_formats()
            for content_type, extensions in metadata_formats.items():
                if content_type in supported_formats:
                    # Merge and deduplicate
                    supported_formats[content_type] = list(set(
                        supported_formats[content_type] + extensions
                    ))
                else:
                    supported_formats[content_type] = extensions
            
            return IngestionCapabilities(
                supported_formats=supported_formats,
                max_file_size=self.content_manager.max_file_size,
                max_batch_size=10000,  # From batch processor
                processing_modes=['sequential', 'parallel', 'distributed', 'adaptive'],
                ai_features_enabled=True,
                quality_levels=['draft', 'standard', 'high', 'ultra'],
                concurrent_uploads=self.content_manager.concurrent_uploads
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get capabilities: {str(e)}")
            return IngestionCapabilities(
                supported_formats={},
                max_file_size=0,
                max_batch_size=0,
                processing_modes=[],
                ai_features_enabled=False,
                quality_levels=[],
                concurrent_uploads=1
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on ingestion system.
        
        Returns:
            Health status of all components
        """
        try:
            health_status = {
                'overall_status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'components': {}
            }
            
            # Check Redis connection
            try:
                await self.redis.ping()
                health_status['components']['redis'] = {'status': 'healthy'}
            except Exception as e:
                health_status['components']['redis'] = {'status': 'unhealthy', 'error': str(e)}
                health_status['overall_status'] = 'degraded'
            
            # Check database connection
            try:
                # Simple query to test connection
                await self.db_session.execute('SELECT 1')
                health_status['components']['database'] = {'status': 'healthy'}
            except Exception as e:
                health_status['components']['database'] = {'status': 'unhealthy', 'error': str(e)}
                health_status['overall_status'] = 'degraded'
            
            # Check storage manager
            try:
                # This would depend on storage manager implementation
                health_status['components']['storage'] = {'status': 'healthy'}
            except Exception as e:
                health_status['components']['storage'] = {'status': 'unhealthy', 'error': str(e)}
                health_status['overall_status'] = 'degraded'
            
            # Check AI models availability
            try:
                ai_status = {
                    'image_classifier': self.metadata_extractor.image_classifier is not None,
                    'text_classifier': self.metadata_extractor.text_classifier is not None,
                    'ner_model': self.metadata_extractor.ner_model is not None
                }
                health_status['components']['ai_models'] = {'status': 'healthy', 'models': ai_status}
            except Exception as e:
                health_status['components']['ai_models'] = {'status': 'degraded', 'error': str(e)}
            
            # Get active operations count
            try:
                active_ops = await self.list_active_operations()
                health_status['active_operations'] = active_ops['total_active_batches']
            except Exception:
                health_status['active_operations'] = 0
            
            return health_status
            
        except Exception as e:
            return {
                'overall_status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _validate_ingestion_request(self, request: IngestionRequest):
        """Validate ingestion request"""
        try:
            if not request.user_id:
                raise ValueError("User ID is required")
            
            if not request.filename:
                raise ValueError("Filename is required")
            
            if not request.file_data:
                raise ValueError("File data is required")
            
            # Check file size
            if hasattr(request.file_data, 'seek'):
                request.file_data.seek(0, 2)
                file_size = request.file_data.tell()
                request.file_data.seek(0)
            else:
                file_size = len(request.file_data)
            
            if file_size > self.content_manager.max_file_size:
                raise ValueError(f"File size {file_size} exceeds maximum {self.content_manager.max_file_size}")
            
            if file_size == 0:
                raise ValueError("File is empty")
                
        except Exception as e:
            self.logger.error(f"Request validation failed: {str(e)}")
            raise IngestionError(f"Invalid request: {str(e)}")


# Factory function for easy initialization
async def create_ingestion_orchestrator(db_session: AsyncSession, redis_client: Redis,
                                      storage_manager: StorageManager, 
                                      content_validator: ContentValidator,
                                      quality_manager: DataQualityManager) -> DataIngestionOrchestrator:
    """
    Factory function to create and initialize DataIngestionOrchestrator.
    
    Args:
        db_session: Async database session
        redis_client: Redis client
        storage_manager: Storage management service
        content_validator: Content validation service
        quality_manager: Data quality management service
        
    Returns:
        Initialized DataIngestionOrchestrator
    """
    try:
        orchestrator = DataIngestionOrchestrator(
            db_session, redis_client, storage_manager, 
            content_validator, quality_manager
        )
        
        # Perform initial health check
        health = await orchestrator.health_check()
        if health['overall_status'] == 'unhealthy':
            raise RuntimeError(f"Ingestion system unhealthy: {health.get('error', 'Unknown error')}")
        
        return orchestrator
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to create ingestion orchestrator: {str(e)}")
        raise


# Export main classes and functions
__all__ = [
    'DataIngestionOrchestrator',
    'IngestionCapabilities',
    'create_ingestion_orchestrator'
]
