"""Vector Stores Module Index - IA Influencer Agent

Central entry point for the vector stores module providing unified access to all
vector database operations, real-time streaming, and content protection features.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

WARNING: This code is proprietary to Fahed Mlaiel. Any unauthorized copying, modification, 
or distribution without explicit written permission is strictly prohibited and will result 
in legal action under German and international copyright law.
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import numpy as np

from backend.core.config import get_settings
from backend.utils.exceptions import VectorStoreError
from backend.utils.monitoring import MetricsCollector

# Import all vector store components
from . import (
    VectorStoreManager,
    RealTimeVectorStreaming,
    VectorDatabaseOptimizer,
    VectorQualityAssessment,
    EmbeddingGenerator,
    SimilaritySearchEngine,
    VectorClusteringEngine,
    StreamingMode,
    OptimizationStrategy,
    QualityMetric
)

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorStoreService:
    """    Unified service interface for all vector store operations.
    
    This class provides a high-level API that orchestrates all vector store
    components for the IA Influencer Agent platform.
    """    
    def __init__(self):
        """Initialize the unified vector store service"""        self.vector_manager = VectorStoreManager()
        self.streaming_service = RealTimeVectorStreaming()
        self.optimizer = VectorDatabaseOptimizer()
        self.quality_assessor = VectorQualityAssessment()
        self.embedding_generator = EmbeddingGenerator()
        self.similarity_engine = SimilaritySearchEngine()
        self.clustering_engine = VectorClusteringEngine()
        
        self.metrics_collector = MetricsCollector()
        self.is_initialized = False
        
        logger.info("VectorStoreService initialized")
    
    async def initialize(self) -> None:
        """Initialize all vector store components"""        try:
            if self.is_initialized:
                return
            
            # Initialize all components
            await self.vector_manager.initialize()
            await self.streaming_service.initialize()
            await self.optimizer.initialize()
            await self.quality_assessor.initialize()
            await self.embedding_generator.initialize()
            await self.similarity_engine.initialize()
            await self.clustering_engine.initialize()
            
            self.is_initialized = True
            logger.info("VectorStoreService fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize VectorStoreService: {str(e)}")
            raise VectorStoreError(f"Service initialization failed: {str(e)}")
    
    async def store_content_fingerprint(
        self,
        content_type: str,
        content_data: Union[bytes, str],
        user_id: int,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """        Store content fingerprint with embedding generation
        
        Args:
            content_type: Type of content (audio, video, image, text)
            content_data: Raw content data
            user_id: User identifier
            metadata: Additional metadata
            
        Returns:
            Storage result with fingerprint ID and embedding info
        """        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Generate embedding
            embedding = await self.embedding_generator.generate_embedding(
                content_type=content_type,
                data=content_data,
                model_quality="high"
            )
            
            # Store in vector database
            content_id = f"{user_id}_{content_type}_{datetime.now().timestamp()}"
            
            storage_result = await self.vector_manager.add_vectors(
                content_type=content_type,
                vectors=[(content_id, embedding, metadata or {})],
                strategy="primary_with_backup"
            )
            
            return {
                "success": storage_result["success"],
                "content_id": content_id,
                "embedding_dimension": len(embedding),
                "storage_details": storage_result
            }
            
        except Exception as e:
            logger.error(f"Failed to store content fingerprint: {str(e)}")
            raise VectorStoreError(f"Fingerprint storage failed: {str(e)}")
    
    async def search_similar_content(
        self,
        content_type: str,
        query_data: Union[bytes, str, np.ndarray],
        similarity_threshold: float = 0.8,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """        Search for similar content across all vector stores
        
        Args:
            content_type: Type of content to search
            query_data: Query content (raw data or embedding)
            similarity_threshold: Minimum similarity score
            limit: Maximum results to return
            
        Returns:
            List of similar content matches
        """        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Generate query embedding if needed
            if isinstance(query_data, (bytes, str)):
                query_vector = await self.embedding_generator.generate_embedding(
                    content_type=content_type,
                    data=query_data,
                    model_quality="high"
                )
            else:
                query_vector = query_data
            
            # Perform similarity search
            search_results = await self.vector_manager.search_similar(
                content_type=content_type,
                query_vector=query_vector,
                k=limit,
                similarity_threshold=similarity_threshold
            )
            
            # Convert to standardized format
            results = []
            for result in search_results:
                results.append({
                    "content_id": result.content_id,
                    "similarity_score": result.similarity_score,
                    "content_type": result.content_type,
                    "metadata": result.metadata,
                    "store_source": result.store_source,
                    "confidence": result.confidence_score
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Similar content search failed: {str(e)}")
            raise VectorStoreError(f"Search failed: {str(e)}")
    
    async def start_real_time_protection(
        self,
        user_id: int,
        content_type: str,
        streaming_mode: StreamingMode,
        websocket=None
    ) -> str:
        """        Start real-time content protection streaming
        
        Args:
            user_id: User identifier
            content_type: Type of content to monitor
            streaming_mode: Streaming configuration mode
            websocket: Optional WebSocket for real-time updates
            
        Returns:
            Stream ID for the session
        """        try:
            if not self.is_initialized:
                await self.initialize()
            
            from .realtime_streaming import StreamingConfig, StreamingPriority
            
            stream_id = f"stream_{user_id}_{content_type}_{datetime.now().timestamp()}"
            
            config = StreamingConfig(
                mode=streaming_mode,
                priority=StreamingPriority.HIGH,
                content_type=content_type,
                user_id=user_id,
                similarity_threshold=0.85,
                enable_live_alerts=True
            )
            
            success = await self.streaming_service.start_stream(
                stream_id=stream_id,
                config=config,
                websocket=websocket
            )
            
            if success:
                return stream_id
            else:
                raise VectorStoreError("Failed to start streaming session")
                
        except Exception as e:
            logger.error(f"Failed to start real-time protection: {str(e)}")
            raise VectorStoreError(f"Real-time protection failed: {str(e)}")
    
    async def optimize_performance(
        self,
        content_type: str,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    ) -> Dict[str, Any]:
        """        Optimize vector database performance for content type
        
        Args:
            content_type: Content type to optimize
            strategy: Optimization strategy to apply
            
        Returns:
            Optimization results and recommendations
        """        try:
            if not self.is_initialized:
                await self.initialize()
            
            from .optimization_engine import OptimizationConfig
            
            config = OptimizationConfig(
                strategy=strategy,
                target_latency_ms=50.0,
                target_memory_mb=1024.0,
                target_accuracy=0.95
            )
            
            result = await self.optimizer.optimize_content_type(
                content_type=content_type,
                config=config
            )
            
            return {
                "success": result.success,
                "improvement_ratio": result.improvement_ratio,
                "original_latency": result.original_metrics.query_latency_ms,
                "optimized_latency": result.optimized_metrics.query_latency_ms,
                "recommendations": result.recommended_config,
                "optimization_log": result.optimization_log
            }
            
        except Exception as e:
            logger.error(f"Performance optimization failed: {str(e)}")
            raise VectorStoreError(f"Optimization failed: {str(e)}")
    
    async def assess_vector_quality(
        self,
        content_type: str,
        metrics: List[QualityMetric] = None
    ) -> Dict[str, Any]:
        """        Assess vector embedding quality for content type
        
        Args:
            content_type: Content type to assess
            metrics: Quality metrics to compute
            
        Returns:
            Quality assessment report
        """        try:
            if not self.is_initialized:
                await self.initialize()
            
            from .quality_assessment import QualityAssessmentConfig
            
            if metrics is None:
                metrics = [
                    QualityMetric.INTRINSIC_DIMENSIONALITY,
                    QualityMetric.CLUSTERING_QUALITY,
                    QualityMetric.SEPARABILITY,
                    QualityMetric.OUTLIER_DETECTION
                ]
            
            config = QualityAssessmentConfig(
                metrics_to_compute=metrics,
                sample_size=5000,
                enable_visualization=True
            )
            
            report = await self.quality_assessor.assess_vector_quality(
                content_type=content_type,
                config=config
            )
            
            return {
                "content_type": report.content_type,
                "total_vectors": report.total_vectors,
                "overall_quality_score": report.overall_quality_score,
                "quality_breakdown": report.quality_breakdown,
                "recommendations": report.recommendations,
                "assessment_timestamp": report.assessment_timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {str(e)}")
            raise VectorStoreError(f"Quality assessment failed: {str(e)}")
    
    async def detect_content_clusters(
        self,
        content_type: str,
        clustering_algorithm: str = "kmeans"
    ) -> Dict[str, Any]:
        """        Detect content clusters and patterns
        
        Args:
            content_type: Content type to analyze
            clustering_algorithm: Clustering algorithm to use
            
        Returns:
            Clustering analysis results
        """        try:
            if not self.is_initialized:
                await self.initialize()
            
            results = await self.clustering_engine.cluster_content(
                content_type=content_type,
                algorithm=clustering_algorithm
            )
            
            return {
                "algorithm": clustering_algorithm,
                "n_clusters": results.get("n_clusters", 0),
                "silhouette_score": results.get("silhouette_score", 0.0),
                "cluster_sizes": results.get("cluster_sizes", []),
                "anomalies_detected": results.get("anomalies", [])
            }
            
        except Exception as e:
            logger.error(f"Cluster detection failed: {str(e)}")
            raise VectorStoreError(f"Cluster detection failed: {str(e)}")
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""        try:
            health_status = {}
            
            if self.is_initialized:
                # Vector store health
                health_status["vector_stores"] = await self.vector_manager.get_health_status()
                
                # Performance metrics
                health_status["performance"] = await self.vector_manager.get_performance_metrics()
                
                # Streaming stats
                health_status["streaming"] = await self.streaming_service.get_global_stats()
                
                # Overall system status
                all_healthy = all(
                    store_health.is_healthy 
                    for store_health in health_status["vector_stores"].values()
                )
                
                health_status["overall_status"] = "healthy" if all_healthy else "degraded"
            else:
                health_status["overall_status"] = "not_initialized"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {"overall_status": "unhealthy", "error": str(e)}
    
    async def close(self) -> None:
        """Close all vector store services"""        try:
            if self.is_initialized:
                await self.vector_manager.close()
                await self.streaming_service.close()
                await self.optimizer.close()
                await self.quality_assessor.close()
                await self.embedding_generator.close()
                await self.similarity_engine.close()
                await self.clustering_engine.close()
                
                self.is_initialized = False
                logger.info("VectorStoreService closed successfully")
                
        except Exception as e:
            logger.error(f"Error closing VectorStoreService: {str(e)}")


# Global service instance for module-level access
_vector_service_instance: Optional[VectorStoreService] = None


async def get_vector_service() -> VectorStoreService:
    """Get or create the global vector service instance"""    global _vector_service_instance
    
    if _vector_service_instance is None:
        _vector_service_instance = VectorStoreService()
        await _vector_service_instance.initialize()
    
    return _vector_service_instance


async def close_vector_service() -> None:
    """Close the global vector service instance"""    global _vector_service_instance
    
    if _vector_service_instance is not None:
        await _vector_service_instance.close()
        _vector_service_instance = None


# Convenience functions for common operations
async def store_fingerprint(
    content_type: str,
    content_data: Union[bytes, str],
    user_id: int,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Convenience function to store content fingerprint"""    service = await get_vector_service()
    return await service.store_content_fingerprint(content_type, content_data, user_id, metadata)


async def search_similar(
    content_type: str,
    query_data: Union[bytes, str, np.ndarray],
    similarity_threshold: float = 0.8,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Convenience function to search similar content"""    service = await get_vector_service()
    return await service.search_similar_content(content_type, query_data, similarity_threshold, limit)


async def start_protection(
    user_id: int,
    content_type: str,
    streaming_mode: StreamingMode = StreamingMode.CONTINUOUS_MONITORING
) -> str:
    """Convenience function to start real-time protection"""    service = await get_vector_service()
    return await service.start_real_time_protection(user_id, content_type, streaming_mode)


# Module metadata
__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"


if __name__ == "__main__":
    # Example usage and testing
    async def main():
        try:
            print("Vector Stores Module - IA Influencer Agent")
            print("==========================================")
            
            # Initialize service
            service = VectorStoreService()
            await service.initialize()
            
            # Get system health
            health = await service.get_system_health()
            print(f"System Status: {health['overall_status']}")
            
            # Close service
            await service.close()
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    asyncio.run(main())
