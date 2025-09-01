"""IA Influencer Agent - Data Pipelines Index Module
================================================

Central index module providing unified access to all pipeline components,
orchestration services, and management utilities for the professional
content lifecycle management system.

Team Specialties:
- Lead Developer AI: Fahed Mlaiel - Advanced pipeline orchestration
- Pipeline Architecture Engineer: Complex workflow coordination
- Content Processing Specialist: Multi-format content optimization
- Protection Systems Engineer: AI-powered content security
- Monetization Engineer: Revenue optimization and automation
- Analytics Engineer: Performance intelligence and insights
- Collaboration Engineer: Creator matching and partnerships
- Distribution Engineer: Multi-platform content distribution
- DevOps Engineer: Infrastructure monitoring and automation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT WARNING ⚠️
This comprehensive pipeline system and orchestration architecture belongs
exclusively to Fahed Mlaiel. Any unauthorized access, copying, or competitive
implementation will result in immediate legal prosecution under international law.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from backend.core.config import get_settings
from backend.core.exceptions import PipelineError, OrchestrationError
from backend.utils.logging import get_logger

# Import all pipeline components
from .content_ingestion import ContentIngestionPipeline, MultiFormatProcessor
from .protection_pipeline import ProtectionPipeline, FingerprintingEngine
from .monetization_pipeline import MonetizationPipeline, RevenueCalculatorEngine
from .analytics_pipeline import AnalyticsPipeline, MetricsAggregator
from .collaboration_pipeline import CollaborationPipeline, MatchingEngine
from .distribution_pipeline import DistributionPipeline, PlatformManager
from .orchestrator import PipelineOrchestrator, WorkflowManager
from .monitoring import PipelineMonitor, HealthChecker

logger = get_logger(__name__)
settings = get_settings()


class PipelineRegistry:
    """
    Central registry for all pipeline components and services
    """
    
    def __init__(self):
        self._pipelines = {}
        self._engines = {}
        self._managers = {}
        self._monitors = {}
        
        # Initialize all pipeline components
        self._initialize_pipelines()
        
    def _initialize_pipelines(self):
        """Initialize all pipeline components"""
        try:
            # Core pipelines
            self._pipelines = {
                "content_ingestion": ContentIngestionPipeline(),
                "protection": ProtectionPipeline(),
                "monetization": MonetizationPipeline(),
                "analytics": AnalyticsPipeline(),
                "collaboration": CollaborationPipeline(),
                "distribution": DistributionPipeline()
            }
            
            # Processing engines
            self._engines = {
                "multi_format_processor": MultiFormatProcessor(),
                "fingerprinting_engine": FingerprintingEngine(),
                "revenue_calculator": RevenueCalculatorEngine(),
                "metrics_aggregator": MetricsAggregator(),
                "matching_engine": MatchingEngine(),
                "platform_manager": PlatformManager()
            }
            
            # Management components
            self._managers = {
                "workflow_manager": WorkflowManager(),
                "pipeline_orchestrator": PipelineOrchestrator()
            }
            
            # Monitoring components
            self._monitors = {
                "pipeline_monitor": PipelineMonitor(),
                "health_checker": HealthChecker()
            }
            
            logger.info("Pipeline registry initialized successfully")
            
        except Exception as e:
            logger.error(f"Pipeline registry initialization failed: {str(e)}")
            raise PipelineError(f"Registry initialization failed: {str(e)}")
    
    def get_pipeline(self, pipeline_name: str):
        """Get pipeline by name"""
        if pipeline_name not in self._pipelines:
            raise PipelineError(f"Pipeline '{pipeline_name}' not found")
        return self._pipelines[pipeline_name]
    
    def get_engine(self, engine_name: str):
        """Get processing engine by name"""
        if engine_name not in self._engines:
            raise PipelineError(f"Engine '{engine_name}' not found")
        return self._engines[engine_name]
    
    def get_manager(self, manager_name: str):
        """Get manager component by name"""
        if manager_name not in self._managers:
            raise PipelineError(f"Manager '{manager_name}' not found")
        return self._managers[manager_name]
    
    def get_monitor(self, monitor_name: str):
        """Get monitoring component by name"""
        if monitor_name not in self._monitors:
            raise PipelineError(f"Monitor '{monitor_name}' not found")
        return self._monitors[monitor_name]
    
    def list_available_components(self) -> Dict[str, List[str]]:
        """List all available pipeline components"""
        return {
            "pipelines": list(self._pipelines.keys()),
            "engines": list(self._engines.keys()),
            "managers": list(self._managers.keys()),
            "monitors": list(self._monitors.keys())
        }


class PipelineFactory:
    """
    Factory class for creating and configuring pipeline workflows
    """
    
    def __init__(self):
        self.registry = PipelineRegistry()
    
    async def create_content_lifecycle_workflow(
        self,
        user_id: int,
        content_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create complete content lifecycle workflow
        """
        try:
            logger.info(f"Creating content lifecycle workflow for user {user_id}")
            
            workflow_manager = self.registry.get_manager("workflow_manager")
            
            # Define workflow steps
            workflow_data = {
                "user_id": user_id,
                "content_config": content_config,
                "workflow_type": "content_lifecycle"
            }
            
            # Execute workflow
            result = await workflow_manager.execute_workflow(
                workflow_type="content_lifecycle",
                workflow_data=workflow_data,
                priority="normal"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Content lifecycle workflow creation failed: {str(e)}")
            raise OrchestrationError(f"Workflow creation failed: {str(e)}")
    
    async def create_protection_workflow(
        self,
        content_id: str,
        protection_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create content protection workflow
        """
        try:
            logger.info(f"Creating protection workflow for content {content_id}")
            
            workflow_manager = self.registry.get_manager("workflow_manager")
            
            workflow_data = {
                "content_id": content_id,
                "protection_config": protection_config,
                "workflow_type": "protection_activation"
            }
            
            result = await workflow_manager.execute_workflow(
                workflow_type="protection_activation",
                workflow_data=workflow_data,
                priority="high"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Protection workflow creation failed: {str(e)}")
            raise OrchestrationError(f"Protection workflow failed: {str(e)}")
    
    async def create_monetization_workflow(
        self,
        user_id: int,
        monetization_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create revenue optimization workflow
        """
        try:
            logger.info(f"Creating monetization workflow for user {user_id}")
            
            workflow_manager = self.registry.get_manager("workflow_manager")
            
            workflow_data = {
                "user_id": user_id,
                "monetization_config": monetization_config,
                "workflow_type": "revenue_optimization"
            }
            
            result = await workflow_manager.execute_workflow(
                workflow_type="revenue_optimization",
                workflow_data=workflow_data,
                priority="normal"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Monetization workflow creation failed: {str(e)}")
            raise OrchestrationError(f"Monetization workflow failed: {str(e)}")
    
    async def create_collaboration_workflow(
        self,
        creator_id: int,
        collaboration_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create collaboration discovery and matching workflow
        """
        try:
            logger.info(f"Creating collaboration workflow for creator {creator_id}")
            
            workflow_manager = self.registry.get_manager("workflow_manager")
            
            workflow_data = {
                "creator_id": creator_id,
                "collaboration_config": collaboration_config,
                "workflow_type": "collaboration_matching"
            }
            
            result = await workflow_manager.execute_workflow(
                workflow_type="collaboration_matching",
                workflow_data=workflow_data,
                priority="normal"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Collaboration workflow creation failed: {str(e)}")
            raise OrchestrationError(f"Collaboration workflow failed: {str(e)}")
    
    async def create_distribution_workflow(
        self,
        content_id: str,
        distribution_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create multi-platform distribution workflow
        """
        try:
            logger.info(f"Creating distribution workflow for content {content_id}")
            
            workflow_manager = self.registry.get_manager("workflow_manager")
            
            workflow_data = {
                "content_id": content_id,
                "distribution_config": distribution_config,
                "workflow_type": "multi_platform_distribution"
            }
            
            result = await workflow_manager.execute_workflow(
                workflow_type="multi_platform_distribution",
                workflow_data=workflow_data,
                priority="normal"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Distribution workflow creation failed: {str(e)}")
            raise OrchestrationError(f"Distribution workflow failed: {str(e)}")


class PipelineService:
    """
    High-level service interface for pipeline operations
    """
    
    def __init__(self):
        self.factory = PipelineFactory()
        self.registry = PipelineRegistry()
    
    async def process_content_upload(
        self,
        user_id: int,
        file_data: bytes,
        upload_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process complete content upload with all pipelines
        """
        try:
            logger.info(f"Processing content upload for user {user_id}")
            
            # Step 1: Content ingestion
            ingestion_pipeline = self.registry.get_pipeline("content_ingestion")
            
            from .content_ingestion import ContentUploadRequest
            
            upload_request = ContentUploadRequest(
                user_id=user_id,
                content_type=upload_config.get("content_type"),
                filename=upload_config.get("filename"),
                file_size=len(file_data),
                mime_type=upload_config.get("mime_type"),
                metadata=upload_config.get("metadata"),
                tags=upload_config.get("tags"),
                description=upload_config.get("description"),
                privacy_level=upload_config.get("privacy_level", "private")
            )
            
            ingestion_result = await ingestion_pipeline.process_upload(
                file_data, upload_request
            )
            
            content_id = ingestion_result.content_id
            
            # Step 2: Auto-protection if enabled
            if upload_config.get("auto_protect", True):
                protection_pipeline = self.registry.get_pipeline("protection")
                protection_result = await protection_pipeline.protect_content(
                    content_id=content_id,
                    user_id=user_id,
                    protection_level="standard"
                )
            else:
                protection_result = {"status": "skipped"}
            
            # Step 3: Analytics setup
            analytics_pipeline = self.registry.get_pipeline("analytics")
            # Note: analytics would be set up for tracking
            
            # Step 4: Monetization setup if enabled
            monetization_result = {"status": "skipped"}
            if upload_config.get("auto_monetize", False):
                monetization_pipeline = self.registry.get_pipeline("monetization")
                monetization_result = await monetization_pipeline.setup_monetization_config(
                    user_id=user_id,
                    config_data=upload_config.get("monetization_config", {})
                )
            
            return {
                "content_id": content_id,
                "ingestion_result": ingestion_result.dict(),
                "protection_result": protection_result,
                "monetization_result": monetization_result,
                "status": "completed",
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Content upload processing failed: {str(e)}")
            raise PipelineError(f"Upload processing failed: {str(e)}")
    
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Get comprehensive system health status
        """
        try:
            health_checker = self.registry.get_monitor("health_checker")
            pipeline_monitor = self.registry.get_monitor("pipeline_monitor")
            
            # Get health status
            health_status = await health_checker.run_health_check_cycle()
            
            # Get system overview
            system_overview = await pipeline_monitor.get_system_overview()
            
            return {
                "health_status": health_status,
                "system_overview": system_overview,
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"System health check failed: {str(e)}")
            raise PipelineError(f"Health check failed: {str(e)}")
    
    async def get_user_analytics(
        self,
        user_id: int,
        analytics_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive user analytics
        """
        try:
            analytics_pipeline = self.registry.get_pipeline("analytics")
            
            # Generate comprehensive report
            report = await analytics_pipeline.generate_comprehensive_report(
                user_id=user_id,
                report_type=analytics_config.get("report_type", "monthly") if analytics_config else "monthly",
                custom_period=analytics_config.get("custom_period") if analytics_config else None
            )
            
            return report
            
        except Exception as e:
            logger.error(f"User analytics generation failed: {str(e)}")
            raise PipelineError(f"Analytics generation failed: {str(e)}")


# Global pipeline service instance
pipeline_service = PipelineService()


# Convenience functions for easy access
async def upload_content(
    user_id: int,
    file_data: bytes,
    upload_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Convenience function for content upload"""
    return await pipeline_service.process_content_upload(user_id, file_data, upload_config)


async def protect_content(
    content_id: str,
    user_id: int,
    protection_level: str = "standard"
) -> Dict[str, Any]:
    """Convenience function for content protection"""
    protection_pipeline = pipeline_service.registry.get_pipeline("protection")
    return await protection_pipeline.protect_content(content_id, user_id, protection_level)


async def get_analytics(
    user_id: int,
    report_type: str = "monthly"
) -> Dict[str, Any]:
    """Convenience function for analytics"""
    return await pipeline_service.get_user_analytics(user_id, {"report_type": report_type})


async def find_collaborators(
    creator_id: int,
    collaboration_type: str = "duet",
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Convenience function for finding collaborators"""
    collaboration_pipeline = pipeline_service.registry.get_pipeline("collaboration")
    matching_engine = pipeline_service.registry.get_engine("matching_engine")
    
    from .collaboration_pipeline import CollaborationType
    
    return await matching_engine.find_collaboration_matches(
        creator_id=creator_id,
        collaboration_type=CollaborationType(collaboration_type),
        filters=filters
    )


async def distribute_content(
    content_id: str,
    platforms: List[str],
    distribution_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function for content distribution"""
    distribution_pipeline = pipeline_service.registry.get_pipeline("distribution")
    
    config = distribution_config or {}
    config["platforms"] = platforms
    
    return await distribution_pipeline.execute_distribution_campaign(content_id, config)


async def check_system_health() -> Dict[str, Any]:
    """Convenience function for system health check"""
    return await pipeline_service.get_system_health()


# Export all components
__all__ = [
    # Classes
    "PipelineRegistry",
    "PipelineFactory", 
    "PipelineService",
    
    # Global service
    "pipeline_service",
    
    # Convenience functions
    "upload_content",
    "protect_content",
    "get_analytics",
    "find_collaborators",
    "distribute_content",
    "check_system_health",
    
    # Individual pipelines
    "ContentIngestionPipeline",
    "ProtectionPipeline",
    "MonetizationPipeline",
    "AnalyticsPipeline",
    "CollaborationPipeline",
    "DistributionPipeline",
    
    # Processing engines
    "MultiFormatProcessor",
    "FingerprintingEngine",
    "RevenueCalculatorEngine",
    "MetricsAggregator",
    "MatchingEngine",
    "PlatformManager",
    
    # Management components
    "PipelineOrchestrator",
    "WorkflowManager",
    "PipelineMonitor",
    "HealthChecker"
]
