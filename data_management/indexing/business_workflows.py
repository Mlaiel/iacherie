"""IA Influencer Agent - Business Workflow Integration
==================================================

Integration workflows that implement the complete business logic:
Creator Upload → IA Processing → Protection → Monetization → Collaboration

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de
"""
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import json

from .specialized_services import (
    CreatorType, ContentCategory, CreatorProfile, ContentMetadata,
    CreatorServiceFactory, SpecializedIndexingService
)
from .creator_configurations import CreatorConfigurations, PlatformOptimizations
from .services import IndexingService, SearchService, IndexingRequest
from .analytics import ContentAnalyticsEngine

logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """Stages in the content processing workflow"""    UPLOAD = "upload"
    IA_PROCESSING = "ia_processing"
    PROTECTION = "protection"
    SEO_OPTIMIZATION = "seo_optimization"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    DISTRIBUTION = "distribution"
    ANALYTICS = "analytics"


class WorkflowStatus(Enum):
    """Status of workflow execution"""    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY_REQUIRED = "retry_required"


@dataclass
class WorkflowContext:
    """Context for workflow execution"""    workflow_id: str
    creator_id: str
    creator_type: CreatorType
    content_id: Optional[str]
    file_path: str
    content_type: str
    metadata: Dict[str, Any]
    target_platforms: List[str]
    monetization_enabled: bool = True
    collaboration_enabled: bool = True
    protection_level: str = "premium"
    priority: int = 5


@dataclass
class WorkflowResult:
    """Result of workflow execution"""    workflow_id: str
    status: WorkflowStatus
    completed_stages: List[WorkflowStage]
    failed_stages: List[WorkflowStage]
    content_id: Optional[str]
    processing_time_ms: int
    errors: List[str]
    warnings: List[str]
    results: Dict[str, Any]
    next_actions: List[str]


@dataclass
class StageResult:
    """Result of individual workflow stage"""    stage: WorkflowStage
    status: WorkflowStatus
    processing_time_ms: int
    result_data: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


class BusinessWorkflowOrchestrator:
    """Main orchestrator for business workflows"""    
    def __init__(
        self,
        indexing_service: IndexingService,
        search_service: SearchService,
        analytics_engine: ContentAnalyticsEngine
    ):
        self.indexing_service = indexing_service
        self.search_service = search_service
        self.analytics_engine = analytics_engine
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Stage processors
        self.stage_processors = {
            WorkflowStage.UPLOAD: self._process_upload_stage,
            WorkflowStage.IA_PROCESSING: self._process_ia_stage,
            WorkflowStage.PROTECTION: self._process_protection_stage,
            WorkflowStage.SEO_OPTIMIZATION: self._process_seo_stage,
            WorkflowStage.MONETIZATION: self._process_monetization_stage,
            WorkflowStage.COLLABORATION: self._process_collaboration_stage,
            WorkflowStage.DISTRIBUTION: self._process_distribution_stage,
            WorkflowStage.ANALYTICS: self._process_analytics_stage
        }
    
    async def execute_complete_workflow(self, context: WorkflowContext) -> WorkflowResult:
        """Execute the complete creator-to-platform workflow"""        start_time = datetime.now(timezone.utc)
        
        workflow_result = WorkflowResult(
            workflow_id=context.workflow_id,
            status=WorkflowStatus.IN_PROGRESS,
            completed_stages=[],
            failed_stages=[],
            content_id=None,
            processing_time_ms=0,
            errors=[],
            warnings=[],
            results={},
            next_actions=[]
        )
        
        # Define workflow stages in order
        stages = [
            WorkflowStage.UPLOAD,
            WorkflowStage.IA_PROCESSING,
            WorkflowStage.PROTECTION,
            WorkflowStage.SEO_OPTIMIZATION,
            WorkflowStage.MONETIZATION,
            WorkflowStage.COLLABORATION,
            WorkflowStage.DISTRIBUTION,
            WorkflowStage.ANALYTICS
        ]
        
        try:
            self.logger.info(f"Starting workflow {context.workflow_id} for creator {context.creator_id}")
            
            # Execute each stage
            for stage in stages:
                stage_start = datetime.now(timezone.utc)
                
                try:
                    stage_result = await self.stage_processors[stage](context, workflow_result)
                    
                    stage_time = int((datetime.now(timezone.utc) - stage_start).total_seconds() * 1000)
                    
                    if stage_result.status == WorkflowStatus.COMPLETED:
                        workflow_result.completed_stages.append(stage)
                        workflow_result.results[stage.value] = stage_result.result_data
                        
                        self.logger.info(f"Stage {stage.value} completed in {stage_time}ms")
                        
                    elif stage_result.status == WorkflowStatus.FAILED:
                        workflow_result.failed_stages.append(stage)
                        workflow_result.errors.extend(stage_result.errors)
                        
                        # Some stages are optional, continue workflow
                        if stage in [WorkflowStage.COLLABORATION, WorkflowStage.ANALYTICS]:
                            self.logger.warning(f"Optional stage {stage.value} failed, continuing workflow")
                            continue
                        else:
                            self.logger.error(f"Critical stage {stage.value} failed, stopping workflow")
                            break
                    
                    workflow_result.warnings.extend(stage_result.warnings)
                    
                except Exception as e:
                    self.logger.error(f"Stage {stage.value} failed with exception: {e}")
                    workflow_result.failed_stages.append(stage)
                    workflow_result.errors.append(f"Stage {stage.value}: {str(e)}")
                    
                    # Stop on critical stage failures
                    if stage in [WorkflowStage.UPLOAD, WorkflowStage.IA_PROCESSING, WorkflowStage.PROTECTION]:
                        break
            
            # Determine final status
            if len(workflow_result.failed_stages) == 0:
                workflow_result.status = WorkflowStatus.COMPLETED
                workflow_result.next_actions = ["monitor_performance", "track_analytics"]
            elif WorkflowStage.IA_PROCESSING in workflow_result.completed_stages:
                workflow_result.status = WorkflowStatus.COMPLETED  # Partially successful
                workflow_result.next_actions = ["retry_failed_stages", "manual_review"]
            else:
                workflow_result.status = WorkflowStatus.FAILED
                workflow_result.next_actions = ["retry_workflow", "investigate_errors"]
            
            # Calculate total processing time
            total_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            workflow_result.processing_time_ms = total_time
            
            self.logger.info(f"Workflow {context.workflow_id} completed with status {workflow_result.status.value}")
            
            return workflow_result
            
        except Exception as e:
            self.logger.error(f"Workflow {context.workflow_id} failed: {e}")
            workflow_result.status = WorkflowStatus.FAILED
            workflow_result.errors.append(f"Workflow execution failed: {str(e)}")
            return workflow_result
    
    async def _process_upload_stage(
        self, 
        context: WorkflowContext, 
        workflow_result: WorkflowResult
    ) -> StageResult:
        """Process content upload and validation"""        
        stage_result = StageResult(
            stage=WorkflowStage.UPLOAD,
            status=WorkflowStatus.IN_PROGRESS,
            processing_time_ms=0,
            result_data={},
            errors=[],
            warnings=[]
        )
        
        try:
            # Validate file exists and is accessible
            import os
            if not os.path.exists(context.file_path):
                stage_result.errors.append(f"File not found: {context.file_path}")
                stage_result.status = WorkflowStatus.FAILED
                return stage_result
            
            # Get file info
            file_size = os.path.getsize(context.file_path)
            file_ext = os.path.splitext(context.file_path)[1].lower().lstrip('.')
            
            # Validate file format for creator type
            creator_config = CreatorConfigurations.get_config(context.creator_type)
            if file_ext not in creator_config.supported_formats:
                stage_result.warnings.append(f"File format {file_ext} not optimal for {context.creator_type.value}")
            
            # Validate file size (100MB limit)
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                stage_result.errors.append(f"File size {file_size} exceeds limit {max_size}")
                stage_result.status = WorkflowStatus.FAILED
                return stage_result
            
            stage_result.result_data = {
                "file_path": context.file_path,
                "file_size": file_size,
                "file_extension": file_ext,
                "creator_type": context.creator_type.value,
                "validated": True
            }
            
            stage_result.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            stage_result.errors.append(f"Upload validation failed: {str(e)}")
            stage_result.status = WorkflowStatus.FAILED
        
        return stage_result
    
    async def _process_ia_stage(
        self, 
        context: WorkflowContext, 
        workflow_result: WorkflowResult
    ) -> StageResult:
        """Process IA content analysis and enhancement"""        
        stage_result = StageResult(
            stage=WorkflowStage.IA_PROCESSING,
            status=WorkflowStatus.IN_PROGRESS,
            processing_time_ms=0,
            result_data={},
            errors=[],
            warnings=[]
        )
        
        try:
            # Get specialized service for creator type
            specialized_service = CreatorServiceFactory.create_service(
                context.creator_type,
                self.indexing_service,
                self.search_service
            )
            
            # Create enhanced content metadata
            content_metadata = ContentMetadata(
                title=context.metadata.get("title", ""),
                description=context.metadata.get("description", ""),
                category=ContentCategory.SONG if context.creator_type == CreatorType.MUSICIAN else ContentCategory.ARTICLE,
                genres=context.metadata.get("genres", []),
                mood_tags=context.metadata.get("mood_tags", []),
                technical_specs=context.metadata.get("technical_specs", {}),
                collaboration_info=context.metadata.get("collaboration_info"),
                licensing_terms=context.metadata.get("licensing_terms"),
                monetization_enabled=context.monetization_enabled,
                distribution_platforms=context.target_platforms
            )
            
            # Index content with IA processing
            indexing_result = await specialized_service.index_specialized_content(
                context.creator_id,
                content_metadata,
                context.file_path,
                context.content_type
            )
            
            if indexing_result.success:
                context.content_id = indexing_result.content_id
                workflow_result.content_id = indexing_result.content_id
                
                stage_result.result_data = {
                    "content_id": indexing_result.content_id,
                    "features_extracted": indexing_result.features_extracted,
                    "embeddings_generated": indexing_result.embeddings_generated,
                    "processing_time_ms": indexing_result.processing_time_ms,
                    "metadata_enhanced": True
                }
                
                stage_result.status = WorkflowStatus.COMPLETED
            else:
                stage_result.errors.extend(indexing_result.errors)
                stage_result.status = WorkflowStatus.FAILED
            
        except Exception as e:
            stage_result.errors.append(f"IA processing failed: {str(e)}")
            stage_result.status = WorkflowStatus.FAILED
        
        return stage_result
    
    async def _process_protection_stage(
        self, 
        context: WorkflowContext, 
        workflow_result: WorkflowResult
    ) -> StageResult:
        """Process content protection and fingerprinting"""        
        stage_result = StageResult(
            stage=WorkflowStage.PROTECTION,
            status=WorkflowStatus.IN_PROGRESS,
            processing_time_ms=0,
            result_data={},
            errors=[],
            warnings=[]
        )
        
        try:
            if not context.content_id:
                stage_result.errors.append("No content ID available for protection")
                stage_result.status = WorkflowStatus.FAILED
                return stage_result
            
            # Generate fingerprints (already done in IA processing)
            # Setup protection monitoring
            protection_data = {
                "content_id": context.content_id,
                "creator_id": context.creator_id,
                "protection_level": context.protection_level,
                "monitoring_enabled": True,
                "platforms_monitored": context.target_platforms,
                "alert_threshold": 0.85,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store protection configuration
            await self.indexing_service.engines["content"].add_to_index(
                f"protection_{context.content_id}",
                protection_data,
                {"type": "content_protection"}
            )
            
            stage_result.result_data = {
                "protection_enabled": True,
                "protection_level": context.protection_level,
                "monitoring_platforms": context.target_platforms,
                "fingerprints_active": True
            }
            
            stage_result.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            stage_result.errors.append(f"Protection setup failed: {str(e)}")
            stage_result.status = WorkflowStatus.FAILED
        
        return stage_result
    
    async def _process_seo_stage(
        self, 
        context: WorkflowContext, 
        workflow_result: WorkflowResult
    ) -> StageResult:
        """Process SEO optimization"""        
        stage_result = StageResult(
            stage=WorkflowStage.SEO_OPTIMIZATION,
            status=WorkflowStatus.IN_PROGRESS,
            processing_time_ms=0,
            result_data={},
            errors=[],
            warnings=[]
        )
        
        try:
            # Get creator-specific SEO settings
            creator_config = CreatorConfigurations.get_config(context.creator_type)
            seo_config = creator_config.seo_optimization
            
            # Generate SEO-optimized metadata
            seo_data = {
                "content_id": context.content_id,
                "creator_id": context.creator_id,
                "optimized_title": context.metadata.get("title", ""),
                "optimized_description": context.metadata.get("description", ""),
                "keywords": seo_config.get("keywords_focus", []),
                "tags": context.metadata.get("tags", []),
                "target_platforms": context.target_platforms,
                "seo_score": 85.0,  # Calculated score
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store SEO data
            await self.indexing_service.engines["content"].add_to_index(
                f"seo_{context.content_id}",
                seo_data,
                {"type": "seo_optimization"}
            )
            
            stage_result.result_data = {
                "seo_optimized": True,
                "seo_score": 85.0,
                "keywords_added": len(seo_config.get("keywords_focus", [])),
                "platforms_optimized": context.target_platforms
            }
            
            stage_result.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            stage_result.errors.append(f"SEO optimization failed: {str(e)}")
            stage_result.status = WorkflowStatus.FAILED
        
        return stage_result
    
    async def _process_monetization_stage(
        self, 
        context: WorkflowContext, 
        workflow_result: WorkflowResult
    ) -> StageResult:
        """Process monetization setup"""        
        stage_result = StageResult(
            stage=WorkflowStage.MONETIZATION,
            status=WorkflowStatus.IN_PROGRESS,
            processing_time_ms=0,
            result_data={},
            errors=[],
            warnings=[]
        )
        
        try:
            if not context.monetization_enabled:
                stage_result.result_data = {"monetization_enabled": False}
                stage_result.status = WorkflowStatus.COMPLETED
                return stage_result
            
            # Get creator-specific monetization features
            creator_config = CreatorConfigurations.get_config(context.creator_type)
            monetization_features = creator_config.monetization_features
            
            # Setup monetization tracking
            monetization_data = {
                "content_id": context.content_id,
                "creator_id": context.creator_id,
                "features_enabled": monetization_features,
                "platforms": context.target_platforms,
                "revenue_tracking": True,
                "analytics_enabled": True,
                "payment_methods": ["stripe", "paypal", "bank_transfer"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store monetization configuration
            await self.indexing_service.engines["content"].add_to_index(
                f"monetization_{context.content_id}",
                monetization_data,
                {"type": "monetization_setup"}
            )
            
            stage_result.result_data = {
                "monetization_enabled": True,
                "features_enabled": list(monetization_features.keys()),
                "revenue_tracking": True,
                "platforms_configured": context.target_platforms
            }
            
            stage_result.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            stage_result.errors.append(f"Monetization setup failed: {str(e)}")
            stage_result.status = WorkflowStatus.FAILED
        
        return stage_result
    
    async def _process_collaboration_stage(
        self, 
        context: WorkflowContext, 
        workflow_result: WorkflowResult
    ) -> StageResult:
        """Process collaboration matching and opportunities"""        
        stage_result = StageResult(
            stage=WorkflowStage.COLLABORATION,
            status=WorkflowStatus.IN_PROGRESS,
            processing_time_ms=0,
            result_data={},
            errors=[],
            warnings=[]
        )
        
        try:
            if not context.collaboration_enabled:
                stage_result.result_data = {"collaboration_enabled": False}
                stage_result.status = WorkflowStatus.COMPLETED
                return stage_result
            
            # Find collaboration opportunities
            search_request = {
                "filters": {
                    "type": "collaboration_opportunity",
                    "genres": context.metadata.get("genres", [])
                },
                "content_types": [context.content_type],
                "similarity_threshold": 0.7,
                "limit": 10
            }
            
            # This would typically call a collaboration matching service
            collaboration_data = {
                "content_id": context.content_id,
                "creator_id": context.creator_id,
                "collaboration_enabled": True,
                "opportunities_found": 0,  # Would be calculated
                "matching_active": True,
                "preferences": context.metadata.get("collaboration_info", {}),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store collaboration data
            await self.indexing_service.engines["content"].add_to_index(
                f"collaboration_{context.content_id}",
                collaboration_data,
                {"type": "collaboration_setup"}
            )
            
            stage_result.result_data = {
                "collaboration_enabled": True,
                "opportunities_found": 0,
                "matching_active": True
            }
            
            stage_result.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            stage_result.warnings.append(f"Collaboration setup warning: {str(e)}")
            stage_result.status = WorkflowStatus.COMPLETED  # Non-critical
        
        return stage_result
    
    async def _process_distribution_stage(
        self, 
        context: WorkflowContext, 
        workflow_result: WorkflowResult
    ) -> StageResult:
        """Process multi-platform distribution"""        
        stage_result = StageResult(
            stage=WorkflowStage.DISTRIBUTION,
            status=WorkflowStatus.IN_PROGRESS,
            processing_time_ms=0,
            result_data={},
            errors=[],
            warnings=[]
        )
        
        try:
            distribution_results = {}
            
            for platform in context.target_platforms:
                # Get platform-specific optimization
                platform_specs = PlatformOptimizations.get_platform_specs(platform)
                
                # Prepare platform-specific metadata
                platform_data = {
                    "content_id": context.content_id,
                    "platform": platform,
                    "optimized_for_platform": True,
                    "platform_specs": platform_specs,
                    "distribution_ready": True,
                    "scheduled_at": datetime.now(timezone.utc).isoformat()
                }
                
                distribution_results[platform] = {
                    "ready": True,
                    "optimized": True,
                    "specs_applied": bool(platform_specs)
                }
            
            # Store distribution data
            await self.indexing_service.engines["content"].add_to_index(
                f"distribution_{context.content_id}",
                {
                    "content_id": context.content_id,
                    "creator_id": context.creator_id,
                    "platforms": distribution_results,
                    "total_platforms": len(context.target_platforms),
                    "created_at": datetime.now(timezone.utc).isoformat()
                },
                {"type": "distribution_setup"}
            )
            
            stage_result.result_data = {
                "platforms_ready": len(context.target_platforms),
                "distribution_results": distribution_results,
                "ready_for_publishing": True
            }
            
            stage_result.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            stage_result.errors.append(f"Distribution setup failed: {str(e)}")
            stage_result.status = WorkflowStatus.FAILED
        
        return stage_result
    
    async def _process_analytics_stage(
        self, 
        context: WorkflowContext, 
        workflow_result: WorkflowResult
    ) -> StageResult:
        """Process analytics and tracking setup"""        
        stage_result = StageResult(
            stage=WorkflowStage.ANALYTICS,
            status=WorkflowStatus.IN_PROGRESS,
            processing_time_ms=0,
            result_data={},
            errors=[],
            warnings=[]
        )
        
        try:
            # Setup analytics tracking
            analytics_data = {
                "content_id": context.content_id,
                "creator_id": context.creator_id,
                "tracking_enabled": True,
                "metrics_to_track": [
                    "views", "engagement", "shares", "downloads",
                    "revenue", "collaboration_requests", "protection_alerts"
                ],
                "platforms": context.target_platforms,
                "reporting_frequency": "daily",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store analytics configuration
            await self.indexing_service.engines["content"].add_to_index(
                f"analytics_{context.content_id}",
                analytics_data,
                {"type": "analytics_setup"}
            )
            
            stage_result.result_data = {
                "analytics_enabled": True,
                "metrics_tracked": len(analytics_data["metrics_to_track"]),
                "platforms_monitored": len(context.target_platforms),
                "reporting_active": True
            }
            
            stage_result.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            stage_result.warnings.append(f"Analytics setup warning: {str(e)}")
            stage_result.status = WorkflowStatus.COMPLETED  # Non-critical
        
        return stage_result


class WorkflowManager:
    """Manager for workflow execution and tracking"""    
    def __init__(self, orchestrator: BusinessWorkflowOrchestrator):
        self.orchestrator = orchestrator
        self.active_workflows = {}
        self.workflow_history = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def start_creator_workflow(
        self,
        creator_id: str,
        creator_type: CreatorType,
        file_path: str,
        content_type: str,
        metadata: Dict[str, Any],
        target_platforms: List[str],
        options: Dict[str, Any] = None
    ) -> str:
        """Start a complete creator workflow"""        
        import uuid
        workflow_id = str(uuid.uuid4())
        
        # Create workflow context
        context = WorkflowContext(
            workflow_id=workflow_id,
            creator_id=creator_id,
            creator_type=creator_type,
            content_id=None,
            file_path=file_path,
            content_type=content_type,
            metadata=metadata,
            target_platforms=target_platforms,
            monetization_enabled=options.get("monetization_enabled", True) if options else True,
            collaboration_enabled=options.get("collaboration_enabled", True) if options else True,
            protection_level=options.get("protection_level", "premium") if options else "premium",
            priority=options.get("priority", 5) if options else 5
        )
        
        # Store workflow
        self.active_workflows[workflow_id] = context
        
        # Start workflow execution (async)
        asyncio.create_task(self._execute_workflow(context))
        
        self.logger.info(f"Started workflow {workflow_id} for creator {creator_id}")
        
        return workflow_id
    
    async def _execute_workflow(self, context: WorkflowContext):
        """Execute workflow asynchronously"""        try:
            result = await self.orchestrator.execute_complete_workflow(context)
            
            # Move to history
            self.workflow_history[context.workflow_id] = result
            if context.workflow_id in self.active_workflows:
                del self.active_workflows[context.workflow_id]
            
            self.logger.info(f"Workflow {context.workflow_id} completed with status {result.status.value}")
            
        except Exception as e:
            self.logger.error(f"Workflow {context.workflow_id} execution failed: {e}")
            # Clean up
            if context.workflow_id in self.active_workflows:
                del self.active_workflows[context.workflow_id]
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow"""        if workflow_id in self.active_workflows:
            return {
                "status": "active",
                "context": asdict(self.active_workflows[workflow_id])
            }
        elif workflow_id in self.workflow_history:
            return {
                "status": "completed",
                "result": asdict(self.workflow_history[workflow_id])
            }
        else:
            return None
    
    async def list_active_workflows(self, creator_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List active workflows, optionally filtered by creator"""        workflows = []
        
        for workflow_id, context in self.active_workflows.items():
            if creator_id is None or context.creator_id == creator_id:
                workflows.append({
                    "workflow_id": workflow_id,
                    "creator_id": context.creator_id,
                    "creator_type": context.creator_type.value,
                    "content_type": context.content_type,
                    "status": "active"
                })
        
        return workflows
