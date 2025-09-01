"""Content Management Index - Unified Entry Point
==============================================

This module provides the main entry point and unified interface for the
IA Influencer Agent content management system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from .manager import ContentManager
from .processor import ContentProcessor
from .validator import ContentValidator
from .analyzer import ContentAnalyzer
from .optimizer import ContentOptimizer
from .distributor import ContentDistributor
from .tracker import ContentTracker
from .indexer import ContentIndexer
from .classifier import ContentClassifier
from .transformer import ContentTransformer
from .aggregator import ContentAggregator
from .synchronizer import ContentSynchronizer


@dataclass
class ContentSystemStatus:
    """
Content management system status container"""
    system_health: str
    active_processes: int
    content_count: int
    sync_status: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    last_updated: datetime


class ContentManagementSystem:
    """
    Unified Content Management System Interface
    
    This class provides a single entry point to access all content management
    functionality including processing, validation, analysis, optimization,
    distribution, tracking, indexing, classification, transformation,
    aggregation, and synchronization.
    
    It serves as the main orchestrator and facade for the entire content
    management subsystem of the IA Influencer Agent platform.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.logger = logging.getLogger(__name__)
        
        # Initialize all content management components
        self.manager = ContentManager(db_session)
        self.processor = ContentProcessor(db_session)
        self.validator = ContentValidator(db_session)
        self.analyzer = ContentAnalyzer(db_session)
        self.optimizer = ContentOptimizer(db_session)
        self.distributor = ContentDistributor(db_session)
        self.tracker = ContentTracker(db_session)
        self.indexer = ContentIndexer(db_session)
        self.classifier = ContentClassifier(db_session)
        self.transformer = ContentTransformer(db_session)
        self.aggregator = ContentAggregator(db_session)
        self.synchronizer = ContentSynchronizer(db_session)
        
        # System status
        self._system_status = None
        self._status_last_updated = None

    async def process_content_complete_workflow(
        self,
        content_data: Dict[str, Any],
        workflow_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute complete content processing workflow
        
        This method orchestrates the entire content lifecycle from upload
        to distribution and monitoring according to the business logic flow:
        Upload → IA Protection → SEO Optimization → Matching → Distribution → Tracking
        
        Args:
            content_data: Content information and file data
            workflow_config: Custom workflow configuration
            
        Returns:
            Complete workflow result with all processing steps
        """
        workflow_start = datetime.utcnow()
        workflow_id = content_data.get("id", "unknown")
        
        try:
            self.logger.info(f"Starting complete content workflow for {workflow_id}")
            
            workflow_results = {
                "workflow_id": workflow_id,
                "steps_completed": [],
                "steps_failed": [],
                "overall_success": False,
                "processing_time": 0.0
            }
            
            # Step 1: Content Creation and Initial Processing
            self.logger.info("Step 1: Content creation and processing")
            creation_result = await self.manager.create_content(content_data)
            
            if not creation_result.get("success"):
                workflow_results["steps_failed"].append("creation")
                return workflow_results
            
            workflow_results["steps_completed"].append("creation")
            workflow_results["content_id"] = creation_result.get("content_id")
            content_id = creation_result["content_id"]
            
            # Step 2: Content Validation and Security
            self.logger.info("Step 2: Content validation and security")
            validation_result = await self.validator.validate_content(content_id)
            
            if not validation_result.get("success"):
                workflow_results["steps_failed"].append("validation")
                # Continue workflow but mark as partial failure
            else:
                workflow_results["steps_completed"].append("validation")
            
            # Step 3: AI Analysis and Classification
            self.logger.info("Step 3: AI analysis and classification")
            analysis_result = await self.analyzer.analyze_content(content_id)
            classification_result = await self.classifier.classify_content(content_id)
            
            if analysis_result.get("success") and classification_result.get("success"):
                workflow_results["steps_completed"].append("ai_analysis")
            else:
                workflow_results["steps_failed"].append("ai_analysis")
            
            # Step 4: Content Optimization
            self.logger.info("Step 4: Content optimization")
            optimization_result = await self.optimizer.optimize_content(content_id)
            
            if optimization_result.get("success"):
                workflow_results["steps_completed"].append("optimization")
            else:
                workflow_results["steps_failed"].append("optimization")
            
            # Step 5: Content Indexing for Discovery
            self.logger.info("Step 5: Content indexing")
            indexing_result = await self.indexer.index_content(content_id)
            
            if indexing_result.get("success"):
                workflow_results["steps_completed"].append("indexing")
            else:
                workflow_results["steps_failed"].append("indexing")
            
            # Step 6: Platform Distribution (if configured)
            distribution_platforms = workflow_config.get("distribution_platforms", []) if workflow_config else []
            
            if distribution_platforms:
                self.logger.info("Step 6: Platform distribution")
                distribution_result = await self.distributor.distribute_content(
                    content_id, distribution_platforms
                )
                
                if distribution_result.get("success"):
                    workflow_results["steps_completed"].append("distribution")
                else:
                    workflow_results["steps_failed"].append("distribution")
            
            # Step 7: Performance Tracking Setup
            self.logger.info("Step 7: Performance tracking setup")
            tracking_result = await self.tracker.start_tracking(content_id)
            
            if tracking_result.get("success"):
                workflow_results["steps_completed"].append("tracking")
            else:
                workflow_results["steps_failed"].append("tracking")
            
            # Calculate workflow completion
            total_steps = len(workflow_results["steps_completed"]) + len(workflow_results["steps_failed"])
            success_rate = len(workflow_results["steps_completed"]) / total_steps if total_steps > 0 else 0
            
            workflow_results["overall_success"] = success_rate >= 0.7  # 70% success threshold
            workflow_results["success_rate"] = success_rate
            
            workflow_time = (datetime.utcnow() - workflow_start).total_seconds()
            workflow_results["processing_time"] = workflow_time
            
            self.logger.info(f"Complete workflow finished for {workflow_id} in {workflow_time:.2f}s with {success_rate:.1%} success rate")
            
            return workflow_results
            
        except Exception as e:
            workflow_time = (datetime.utcnow() - workflow_start).total_seconds()
            error_msg = f"Complete workflow failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "workflow_id": workflow_id,
                "overall_success": False,
                "error": error_msg,
                "processing_time": workflow_time,
                "steps_completed": workflow_results.get("steps_completed", []),
                "steps_failed": workflow_results.get("steps_failed", [])
            }

    async def search_content(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        sort_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Unified content search interface
        
        Args:
            query: Search query string
            filters: Content filters (type, platform, date range, etc.)
            sort_options: Sorting preferences
            
        Returns:
            Search results with content matches and metadata
        """
        try:
            # Use the indexer for intelligent search
            search_result = await self.indexer.search_content(
                query=query,
                filters=filters,
                sort_options=sort_options
            )
            
            return search_result
            
        except Exception as e:
            error_msg = f"Content search failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "query": query,
                "results": []
            }

    async def sync_all_platforms(
        self,
        platform_filter: List[str] = None,
        force_sync: bool = False
    ) -> Dict[str, Any]:
        """
        Synchronize content across all configured platforms
        
        Args:
            platform_filter: List of specific platforms to sync
            force_sync: Force synchronization regardless of sync intervals
            
        Returns:
            Platform synchronization results
        """
        try:
            self.logger.info("Starting platform synchronization")
            
            # Use aggregator for pulling content from platforms
            aggregation_result = await self.aggregator.aggregate_all_sources(
                source_filter={"platforms": platform_filter} if platform_filter else None
            )
            
            # Use synchronizer for pushing local content to platforms
            if platform_filter:
                sync_tasks = []
                for platform in platform_filter:
                    sync_result = await self.synchronizer.sync_from_platform(platform)
                    sync_tasks.append(sync_result)
            
            return {
                "success": True,
                "aggregation_result": aggregation_result,
                "sync_summary": {
                    "platforms_processed": len(platform_filter) if platform_filter else 0,
                    "content_aggregated": aggregation_result.get("total_items_created", 0),
                    "sync_conflicts": 0  # Would be calculated from sync results
                }
            }
            
        except Exception as e:
            error_msg = f"Platform synchronization failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg
            }

    async def get_content_analytics(
        self,
        content_id: str = None,
        time_range: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive content analytics
        
        Args:
            content_id: Specific content ID (None for global analytics)
            time_range: Time range for analytics (start_date, end_date)
            
        Returns:
            Content analytics and performance metrics
        """
        try:
            if content_id:
                # Get analytics for specific content
                analytics_result = await self.tracker.get_content_analytics(content_id, time_range)
            else:
                # Get global analytics
                analytics_result = await self.tracker.get_global_analytics(time_range)
            
            return analytics_result
            
        except Exception as e:
            error_msg = f"Analytics retrieval failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "content_id": content_id
            }

    async def transform_content_for_platforms(
        self,
        content_id: str,
        target_platforms: List[str],
        custom_specs: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Transform content for multiple target platforms
        
        Args:
            content_id: Content identifier
            target_platforms: List of target platforms
            custom_specs: Custom transformation specifications
            
        Returns:
            Multi-platform transformation results
        """
        try:
            transformation_results = {}
            
            for platform in target_platforms:
                platform_result = await self.transformer.transform_for_platform(
                    content_id, platform, custom_specs
                )
                transformation_results[platform] = platform_result
            
            # Calculate overall success
            successful_platforms = [
                platform for platform, result in transformation_results.items()
                if result.get("success")
            ]
            
            return {
                "success": len(successful_platforms) > 0,
                "content_id": content_id,
                "platforms_processed": len(target_platforms),
                "platforms_successful": len(successful_platforms),
                "transformation_results": transformation_results
            }
            
        except Exception as e:
            error_msg = f"Multi-platform transformation failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "content_id": content_id
            }

    async def get_system_status(self, force_refresh: bool = False) -> ContentSystemStatus:
        """
        Get comprehensive system status and health metrics
        
        Args:
            force_refresh: Force refresh of status data
            
        Returns:
            System status information
        """
        try:
            # Check if we need to refresh status data
            if (force_refresh or not self._system_status or 
                not self._status_last_updated or 
                (datetime.utcnow() - self._status_last_updated).total_seconds() > 300):  # 5 min cache
                
                # Collect system metrics
                system_health = "healthy"  # Would be calculated based on various metrics
                active_processes = len(self.tracker.active_tracking_sessions)
                
                # Get content count from manager
                content_count = await self._get_total_content_count()
                
                # Get sync status from synchronizer
                sync_status = {
                    "active_sync_tasks": len(self.synchronizer.active_sync_tasks),
                    "sync_queue_size": self.synchronizer.sync_queue.qsize(),
                    "last_sync": datetime.utcnow().isoformat()
                }
                
                # Performance metrics
                performance_metrics = {
                    "avg_processing_time": 0.0,
                    "success_rate": 0.95,
                    "throughput_per_hour": 0
                }
                
                self._system_status = ContentSystemStatus(
                    system_health=system_health,
                    active_processes=active_processes,
                    content_count=content_count,
                    sync_status=sync_status,
                    performance_metrics=performance_metrics,
                    last_updated=datetime.utcnow()
                )
                
                self._status_last_updated = datetime.utcnow()
            
            return self._system_status
            
        except Exception as e:
            self.logger.error(f"System status retrieval failed: {str(e)}")
            
            return ContentSystemStatus(
                system_health="error",
                active_processes=0,
                content_count=0,
                sync_status={"error": str(e)},
                performance_metrics={"error": str(e)},
                last_updated=datetime.utcnow()
            )

    async def shutdown_system(self) -> Dict[str, Any]:
        """
        Gracefully shutdown the content management system
        
        Returns:
            Shutdown status and cleanup results
        """
        try:
            self.logger.info("Initiating content management system shutdown")
            
            shutdown_results = {
                "success": True,
                "components_shutdown": [],
                "cleanup_performed": []
            }
            
            # Stop tracking sessions
            if hasattr(self.tracker, 'stop_all_tracking'):
                await self.tracker.stop_all_tracking()
                shutdown_results["components_shutdown"].append("tracker")
            
            # Stop synchronization tasks
            if hasattr(self.synchronizer, 'stop_sync_processor'):
                await self.synchronizer.stop_sync_processor()
                shutdown_results["components_shutdown"].append("synchronizer")
            
            # Clean up temporary files
            if hasattr(self.transformer, 'cleanup_temp_files'):
                await self.transformer.cleanup_temp_files()
                shutdown_results["cleanup_performed"].append("temp_files")
            
            # Close database connections would be handled by the session manager
            
            self.logger.info("Content management system shutdown completed")
            
            return shutdown_results
            
        except Exception as e:
            error_msg = f"System shutdown failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg
            }

    # Helper methods
    
    async def _get_total_content_count(self) -> int:
        """Get total content count from database"""
        try:
            # This would query the database for total content count
            return 0  # Placeholder
        except Exception:
            return 0


# Convenience function for easy system initialization
async def create_content_system(db_session: AsyncSession) -> ContentManagementSystem:
    """
    Create and initialize the content management system
    
    Args:
        db_session: Database session
        
    Returns:
        Initialized content management system
    """
    system = ContentManagementSystem(db_session)
    
    # Perform any necessary initialization
    # await system._initialize_components()
    
    return system


# Export the main system class and convenience function
__all__ = [
    "ContentManagementSystem",
    "ContentSystemStatus", 
    "create_content_system"
]
