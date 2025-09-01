"""Vector Database Module - Entry Point
====================================

Unified entry point for the vector database management system providing
easy access to all vector database operations and capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

ATTENTION: Ce code est protégé par les droits d'auteur.
Toute reproduction, distribution ou modification non autorisée est strictement interdite.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from datetime import datetime
import json

# Import all main components
from .operations import VectorDBOperations, IndexMetrics, BackupInfo, PerformanceStats
from .similarity_search import (
    SimilaritySearchEngine, SearchConfig, SearchType, RankingStrategy,
    DuplicateAnalysis, CollaborationMatch, ContentRecommendation
)
from .embedding_engine import (
    MultiModalEmbeddingEngine, EmbeddingResult,
    TextEmbeddingGenerator, AudioEmbeddingGenerator,
    ImageEmbeddingGenerator, VideoEmbeddingGenerator
)
from . import VectorSearchResult

logger = logging.getLogger(__name__)


class VectorDatabaseManager:
    """
    Unified vector database manager providing high-level interface for all
    vector database operations including content indexing, similarity search,
    duplicate detection, collaboration matching, and system management.
    
    This is the main entry point for the vector database system.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the vector database manager.
        
        Args:
            config: Configuration dictionary for the system
        """
        self.config = config or self._get_default_config()
        
        # Initialize the operations manager
        self.operations = VectorDBOperations(self.config)
        
        # Quick access to components
        self.vector_db = self.operations.vector_db
        self.embedding_engine = self.operations.embedding_engine
        self.similarity_engine = self.operations.similarity_engine
        
        logger.info("Vector Database Manager initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the vector database system."""
        return {
            'backend': 'faiss',
            'storage_path': './data/vector_db',
            'embedding': {
                'text': {
                    'text_model': 'all-MiniLM-L6-v2',
                    'bert_model': 'bert-base-uncased',
                    'max_length': 512
                },
                'audio': {
                    'sample_rate': 22050,
                    'max_duration': 30.0,
                    'n_mfcc': 13,
                    'n_chroma': 12
                },
                'image': {
                    'image_size': 224
                },
                'video': {
                    'max_frames': 100,
                    'frame_step': 10
                }
            },
            'similarity_thresholds': {
                'audio': 0.85,
                'video': 0.80,
                'image': 0.75,
                'text': 0.70
            },
            'duplicate_thresholds': {
                'audio': 0.92,
                'image': 0.95,
                'text': 0.88,
                'video': 0.90
            },
            'auto_backup': True,
            'backup_interval_hours': 24,
            'version': '1.0.0'
        }
    
    async def initialize(self) -> bool:
        """
        Initialize the complete vector database system.
        
        Returns:
            Success status
        """
        try:
            success = await self.operations.initialize_system()
            
            if success:
                logger.info("Vector Database Manager successfully initialized")
            else:
                logger.error("Failed to initialize Vector Database Manager")
            
            return success
            
        except Exception as e:
            logger.error(f"Vector Database Manager initialization failed: {str(e)}")
            return False
    
    # Content Management Methods
    
    async def add_text_content(self, text: str, content_id: str,
                             metadata: Dict[str, Any] = None) -> bool:
        """
        Add text content to the vector database.
        
        Args:
            text: Text content to add
            content_id: Unique identifier for the content
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        metadata = metadata or {}
        return await self.operations.add_content(text, 'text', content_id, metadata)
    
    async def add_audio_content(self, audio_data: Any, content_id: str,
                              metadata: Dict[str, Any] = None) -> bool:
        """
        Add audio content to the vector database.
        
        Args:
            audio_data: Audio data (numpy array)
            content_id: Unique identifier for the content
            metadata: Additional metadata (should include sample_rate)
            
        Returns:
            Success status
        """
        metadata = metadata or {}
        return await self.operations.add_content(audio_data, 'audio', content_id, metadata)
    
    async def add_image_content(self, image: Any, content_id: str,
                              metadata: Dict[str, Any] = None) -> bool:
        """
        Add image content to the vector database.
        
        Args:
            image: Image data (PIL Image)
            content_id: Unique identifier for the content
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        metadata = metadata or {}
        return await self.operations.add_content(image, 'image', content_id, metadata)
    
    async def add_video_content(self, video_path: str, content_id: str,
                              metadata: Dict[str, Any] = None) -> bool:
        """
        Add video content to the vector database.
        
        Args:
            video_path: Path to video file
            content_id: Unique identifier for the content
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        metadata = metadata or {}
        return await self.operations.add_content(video_path, 'video', content_id, metadata)
    
    async def remove_content(self, content_id: str, content_type: str) -> bool:
        """
        Remove content from the vector database.
        
        Args:
            content_id: ID of content to remove
            content_type: Type of content ('text', 'audio', 'image', 'video')
            
        Returns:
            Success status
        """
        return await self.operations.remove_content(content_id, content_type)
    
    # Search Methods
    
    async def search_similar_text(self, query_text: str, max_results: int = 20,
                                threshold: float = None,
                                metadata_filters: Dict[str, Any] = None) -> List[VectorSearchResult]:
        """
        Search for similar text content.
        
        Args:
            query_text: Text to search for
            max_results: Maximum number of results
            threshold: Similarity threshold
            metadata_filters: Filters to apply
            
        Returns:
            List of similar content results
        """
        threshold = threshold or self.config['similarity_thresholds']['text']
        
        search_config = SearchConfig(
            search_type=SearchType.SIMILAR_CONTENT,
            ranking_strategy=RankingStrategy.METADATA_BOOST,
            similarity_threshold=threshold,
            max_results=max_results,
            metadata_filters=metadata_filters or {}
        )
        
        return await self.operations.search_content(query_text, 'text', search_config)
    
    async def search_similar_audio(self, audio_data: Any, max_results: int = 20,
                                 threshold: float = None,
                                 metadata_filters: Dict[str, Any] = None) -> List[VectorSearchResult]:
        """
        Search for similar audio content.
        
        Args:
            audio_data: Audio data to search for
            max_results: Maximum number of results
            threshold: Similarity threshold
            metadata_filters: Filters to apply
            
        Returns:
            List of similar content results
        """
        threshold = threshold or self.config['similarity_thresholds']['audio']
        
        search_config = SearchConfig(
            search_type=SearchType.SIMILAR_CONTENT,
            ranking_strategy=RankingStrategy.METADATA_BOOST,
            similarity_threshold=threshold,
            max_results=max_results,
            metadata_filters=metadata_filters or {}
        )
        
        return await self.operations.search_content(audio_data, 'audio', search_config)
    
    async def search_similar_image(self, image: Any, max_results: int = 20,
                                 threshold: float = None,
                                 metadata_filters: Dict[str, Any] = None) -> List[VectorSearchResult]:
        """
        Search for similar image content.
        
        Args:
            image: Image data to search for
            max_results: Maximum number of results
            threshold: Similarity threshold
            metadata_filters: Filters to apply
            
        Returns:
            List of similar content results
        """
        threshold = threshold or self.config['similarity_thresholds']['image']
        
        search_config = SearchConfig(
            search_type=SearchType.SIMILAR_CONTENT,
            ranking_strategy=RankingStrategy.METADATA_BOOST,
            similarity_threshold=threshold,
            max_results=max_results,
            metadata_filters=metadata_filters or {}
        )
        
        return await self.operations.search_content(image, 'image', search_config)
    
    async def search_similar_video(self, video_path: str, max_results: int = 20,
                                 threshold: float = None,
                                 metadata_filters: Dict[str, Any] = None) -> List[VectorSearchResult]:
        """
        Search for similar video content.
        
        Args:
            video_path: Video file path to search for
            max_results: Maximum number of results
            threshold: Similarity threshold
            metadata_filters: Filters to apply
            
        Returns:
            List of similar content results
        """
        threshold = threshold or self.config['similarity_thresholds']['video']
        
        search_config = SearchConfig(
            search_type=SearchType.SIMILAR_CONTENT,
            ranking_strategy=RankingStrategy.METADATA_BOOST,
            similarity_threshold=threshold,
            max_results=max_results,
            metadata_filters=metadata_filters or {}
        )
        
        return await self.operations.search_content(video_path, 'video', search_config)
    
    # Duplicate Detection Methods
    
    async def detect_text_duplicates(self, text: str,
                                   metadata: Dict[str, Any] = None) -> List[Tuple[VectorSearchResult, DuplicateAnalysis]]:
        """
        Detect duplicate text content.
        
        Args:
            text: Text to check for duplicates
            metadata: Additional metadata
            
        Returns:
            List of (result, analysis) tuples for potential duplicates
        """
        return await self.operations.detect_duplicates(text, 'text', metadata)
    
    async def detect_audio_duplicates(self, audio_data: Any,
                                    metadata: Dict[str, Any] = None) -> List[Tuple[VectorSearchResult, DuplicateAnalysis]]:
        """
        Detect duplicate audio content.
        
        Args:
            audio_data: Audio data to check for duplicates
            metadata: Additional metadata
            
        Returns:
            List of (result, analysis) tuples for potential duplicates
        """
        return await self.operations.detect_duplicates(audio_data, 'audio', metadata)
    
    async def detect_image_duplicates(self, image: Any,
                                    metadata: Dict[str, Any] = None) -> List[Tuple[VectorSearchResult, DuplicateAnalysis]]:
        """
        Detect duplicate image content.
        
        Args:
            image: Image to check for duplicates
            metadata: Additional metadata
            
        Returns:
            List of (result, analysis) tuples for potential duplicates
        """
        return await self.operations.detect_duplicates(image, 'image', metadata)
    
    async def detect_video_duplicates(self, video_path: str,
                                    metadata: Dict[str, Any] = None) -> List[Tuple[VectorSearchResult, DuplicateAnalysis]]:
        """
        Detect duplicate video content.
        
        Args:
            video_path: Video file path to check for duplicates
            metadata: Additional metadata
            
        Returns:
            List of (result, analysis) tuples for potential duplicates
        """
        return await self.operations.detect_duplicates(video_path, 'video', metadata)
    
    # Collaboration and Recommendation Methods
    
    async def find_collaboration_opportunities(self, creator_profile: Dict[str, Any],
                                             content_example: Any,
                                             content_type: str) -> List[CollaborationMatch]:
        """
        Find collaboration opportunities with other creators.
        
        Args:
            creator_profile: Profile of the creator seeking collaborations
            content_example: Example content representing creator's style
            content_type: Type of content
            
        Returns:
            List of collaboration matches
        """
        return await self.operations.find_collaborations(creator_profile, content_example, content_type)
    
    async def get_content_recommendations(self, user_profile: Dict[str, Any],
                                        content_example: Any,
                                        content_type: str) -> List[ContentRecommendation]:
        """
        Get content recommendations for inspiration and strategy.
        
        Args:
            user_profile: User's profile and preferences
            content_example: Example content representing user's style
            content_type: Type of content
            
        Returns:
            List of content recommendations
        """
        return await self.operations.get_recommendations(user_profile, content_example, content_type)
    
    # System Management Methods
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status including all indices and performance.
        
        Returns:
            System status information
        """
        try:
            # Get performance stats
            performance = await self.operations.get_performance_stats()
            
            # Get index metrics for all content types
            index_metrics = await self.operations.get_index_metrics()
            
            # Get vector database status
            vector_db_status = self.vector_db.get_system_status()
            
            return {
                'status': 'healthy',  # Would be calculated based on metrics
                'performance': performance.__dict__,
                'indices': {name: metrics.__dict__ for name, metrics in index_metrics.items()},
                'vector_database': vector_db_status,
                'supported_content_types': ['text', 'audio', 'image', 'video'],
                'last_updated': performance.last_optimization.isoformat() if performance.last_optimization else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'supported_content_types': ['text', 'audio', 'image', 'video']
            }
    
    async def get_index_statistics(self, content_type: str = None) -> Union[IndexMetrics, Dict[str, IndexMetrics]]:
        """
        Get statistics for vector indices.
        
        Args:
            content_type: Specific content type, or None for all indices
            
        Returns:
            Index metrics
        """
        return await self.operations.get_index_metrics(content_type)
    
    async def get_performance_metrics(self) -> PerformanceStats:
        """
        Get performance metrics for the system.
        
        Returns:
            Performance statistics
        """
        return await self.operations.get_performance_stats()
    
    # Backup and Maintenance Methods
    
    async def create_system_backup(self, backup_name: str = None) -> BackupInfo:
        """
        Create a complete system backup.
        
        Args:
            backup_name: Custom name for the backup
            
        Returns:
            Backup information
        """
        return await self.operations.create_backup(backup_name=backup_name)
    
    async def create_content_backup(self, content_type: str, backup_name: str = None) -> BackupInfo:
        """
        Create a backup for specific content type.
        
        Args:
            content_type: Content type to backup
            backup_name: Custom name for the backup
            
        Returns:
            Backup information
        """
        return await self.operations.create_backup(content_type, backup_name)
    
    async def list_available_backups(self) -> List[BackupInfo]:
        """
        List all available backups.
        
        Returns:
            List of backup information
        """
        return await self.operations.list_backups()
    
    async def restore_from_backup(self, backup_id: str) -> bool:
        """
        Restore system from a backup.
        
        Args:
            backup_id: ID of the backup to restore
            
        Returns:
            Success status
        """
        return await self.operations.restore_backup(backup_id)
    
    async def optimize_system(self, content_type: str = None) -> bool:
        """
        Optimize the vector database system for better performance.
        
        Args:
            content_type: Specific content type to optimize, or None for all
            
        Returns:
            Success status
        """
        return await self.operations.optimize_indices(content_type)
    
    # Utility Methods
    
    def get_supported_content_types(self) -> List[str]:
        """
        Get list of supported content types.
        
        Returns:
            List of supported content types
        """
        return ['text', 'audio', 'image', 'video']
    
    def get_embedding_dimensions(self) -> Dict[str, int]:
        """
        Get embedding dimensions for each content type.
        
        Returns:
            Dictionary mapping content types to their embedding dimensions
        """
        return self.embedding_engine.get_embedding_dimensions()
    
    def export_configuration(self) -> Dict[str, Any]:
        """
        Export current system configuration.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    async def update_configuration(self, new_config: Dict[str, Any]) -> bool:
        """
        Update system configuration.
        
        Args:
            new_config: New configuration to apply
            
        Returns:
            Success status
        """
        try:
            # Validate configuration
            required_keys = ['backend', 'storage_path', 'embedding', 'similarity_thresholds']
            for key in required_keys:
                if key not in new_config:
                    logger.error(f"Missing required configuration key: {key}")
                    return False
            
            # Update configuration
            self.config.update(new_config)
            
            logger.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Configuration update failed: {str(e)}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a comprehensive health check of the system.
        
        Returns:
            Health check results
        """
        try:
            health_results = {
                'overall_status': 'healthy',
                'components': {},
                'recommendations': [],
                'timestamp': datetime.now().isoformat()
            }
            
            # Check vector database
            try:
                vector_db_status = self.vector_db.get_system_status()
                health_results['components']['vector_database'] = {
                    'status': 'healthy' if vector_db_status else 'error',
                    'details': vector_db_status
                }
            except Exception as e:
                health_results['components']['vector_database'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # Check indices
            try:
                index_metrics = await self.operations.get_index_metrics()
                healthy_indices = 0
                total_indices = len(index_metrics)
                
                for content_type, metrics in index_metrics.items():
                    if metrics.health_score > 0.7:
                        healthy_indices += 1
                    elif metrics.health_score < 0.5:
                        health_results['recommendations'].append(f"Consider optimizing {content_type} index")
                
                health_results['components']['indices'] = {
                    'status': 'healthy' if healthy_indices == total_indices else 'degraded',
                    'healthy_count': healthy_indices,
                    'total_count': total_indices
                }
                
            except Exception as e:
                health_results['components']['indices'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # Check performance
            try:
                performance = await self.operations.get_performance_stats()
                
                performance_status = 'healthy'
                if performance.error_rate > 0.1:  # 10% error rate
                    performance_status = 'degraded'
                    health_results['recommendations'].append("High error rate detected - investigate system issues")
                
                if performance.avg_query_time_ms > 5000:  # 5 second average
                    performance_status = 'degraded'
                    health_results['recommendations'].append("High query latency - consider optimization")
                
                health_results['components']['performance'] = {
                    'status': performance_status,
                    'avg_query_time_ms': performance.avg_query_time_ms,
                    'error_rate': performance.error_rate
                }
                
            except Exception as e:
                health_results['components']['performance'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # Determine overall status
            component_statuses = [comp['status'] for comp in health_results['components'].values()]
            if 'error' in component_statuses:
                health_results['overall_status'] = 'error'
            elif 'degraded' in component_statuses:
                health_results['overall_status'] = 'degraded'
            
            return health_results
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'overall_status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Convenience function for quick initialization
async def create_vector_database(config: Dict[str, Any] = None) -> VectorDatabaseManager:
    """
    Create and initialize a vector database manager.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Initialized VectorDatabaseManager instance
    """
    manager = VectorDatabaseManager(config)
    await manager.initialize()
    return manager


# Export main components
__all__ = [
    'VectorDatabaseManager',
    'create_vector_database',
    'VectorSearchResult',
    'SearchConfig',
    'SearchType',
    'RankingStrategy',
    'DuplicateAnalysis',
    'CollaborationMatch',
    'ContentRecommendation',
    'IndexMetrics',
    'BackupInfo',
    'PerformanceStats'
]
