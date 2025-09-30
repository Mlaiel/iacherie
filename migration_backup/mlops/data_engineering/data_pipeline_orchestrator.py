"""
Data Pipeline Orchestrator
Enterprise data pipeline orchestration and management

This module provides:
- End-to-end data pipeline orchestration
- Multi-source data ingestion coordination
- Pipeline dependency management
- Data flow monitoring and optimization
- Error handling and recovery mechanisms

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class PipelineStageType(Enum):
    INGESTION = "ingestion"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    FEATURE_ENGINEERING = "feature_engineering"
    OUTPUT = "output"

@dataclass
class PipelineStage:
    """Individual pipeline stage configuration"""
    stage_id: str
    stage_name: str
    stage_type: PipelineStageType
    dependencies: List[str]
    config: Dict[str, Any]
    retry_count: int = 3
    timeout_minutes: int = 60
    enabled: bool = True

@dataclass
class DataPipeline:
    """Complete data pipeline definition"""
    pipeline_id: str
    pipeline_name: str
    description: str
    stages: List[PipelineStage]
    schedule: Optional[str] = None  # Cron expression
    data_sources: List[str] = None
    output_destinations: List[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.data_sources is None:
            self.data_sources = []
        if self.output_destinations is None:
            self.output_destinations = []

@dataclass
class PipelineExecution:
    """Pipeline execution state"""
    execution_id: str
    pipeline_id: str
    status: PipelineStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_stage: Optional[str] = None
    stage_results: Dict[str, Any] = None
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.stage_results is None:
            self.stage_results = {}
        if self.metrics is None:
            self.metrics = {}

class DataPipelineOrchestrator:
    """
    Enterprise data pipeline orchestrator
    Manages complex data workflows for 53 AI agents
    """
    
    def __init__(self):
        self.pipelines: Dict[str, DataPipeline] = {}
        self.executions: Dict[str, PipelineExecution] = {}
        self.stage_handlers: Dict[PipelineStageType, Callable] = {}
        self.scheduler_running = False
        self.monitoring_active = False
        
        # Register default stage handlers
        self._register_default_handlers()
        
    async def create_pipeline(
        self,
        pipeline_name: str,
        description: str,
        stages_config: List[Dict[str, Any]],
        schedule: Optional[str] = None
    ) -> str:
        """
        Create a new data pipeline
        
        Args:
            pipeline_name: Pipeline name
            description: Pipeline description
            stages_config: List of stage configurations
            schedule: Cron schedule expression
            
        Returns:
            pipeline_id: Unique pipeline identifier
        """
        try:
            pipeline_id = str(uuid.uuid4())
            
            # Create pipeline stages
            stages = []
            for stage_config in stages_config:
                stage = PipelineStage(
                    stage_id=str(uuid.uuid4()),
                    stage_name=stage_config["name"],
                    stage_type=PipelineStageType(stage_config["type"]),
                    dependencies=stage_config.get("dependencies", []),
                    config=stage_config.get("config", {}),
                    retry_count=stage_config.get("retry_count", 3),
                    timeout_minutes=stage_config.get("timeout_minutes", 60),
                    enabled=stage_config.get("enabled", True)
                )
                stages.append(stage)
            
            # Create pipeline
            pipeline = DataPipeline(
                pipeline_id=pipeline_id,
                pipeline_name=pipeline_name,
                description=description,
                stages=stages,
                schedule=schedule
            )
            
            # Validate pipeline
            await self._validate_pipeline(pipeline)
            
            self.pipelines[pipeline_id] = pipeline
            
            logger.info(f"Created data pipeline {pipeline_id}: {pipeline_name}")
            return pipeline_id
            
        except Exception as e:
            logger.error(f"Failed to create pipeline: {e}")
            raise
    
    async def execute_pipeline(
        self,
        pipeline_id: str,
        execution_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a data pipeline
        
        Args:
            pipeline_id: Pipeline to execute
            execution_context: Additional execution context
            
        Returns:
            execution_id: Unique execution identifier
        """
        try:
            if pipeline_id not in self.pipelines:
                raise ValueError(f"Pipeline {pipeline_id} not found")
            
            pipeline = self.pipelines[pipeline_id]
            execution_id = str(uuid.uuid4())
            
            # Create execution record
            execution = PipelineExecution(
                execution_id=execution_id,
                pipeline_id=pipeline_id,
                status=PipelineStatus.PENDING,
                started_at=datetime.utcnow()
            )
            
            self.executions[execution_id] = execution
            
            # Start pipeline execution
            asyncio.create_task(self._run_pipeline_execution(execution, pipeline, execution_context))
            
            logger.info(f"Started pipeline execution {execution_id} for pipeline {pipeline_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to execute pipeline: {e}")
            raise
    
    async def create_ai_agent_pipeline(
        self,
        agent_category: str,
        agent_ids: List[str],
        data_requirements: Dict[str, Any]
    ) -> str:
        """
        Create specialized pipeline for AI agents
        
        Args:
            agent_category: Category of AI agents (content_processing, etc.)
            agent_ids: List of agent identifiers
            data_requirements: Data processing requirements
            
        Returns:
            pipeline_id: Created pipeline identifier
        """
        try:
            pipeline_name = f"{agent_category}_data_pipeline"
            description = f"Data pipeline for {agent_category} AI agents: {', '.join(agent_ids)}"
            
            # Create stages based on agent category
            stages_config = await self._create_agent_specific_stages(
                agent_category, agent_ids, data_requirements
            )
            
            pipeline_id = await self.create_pipeline(
                pipeline_name=pipeline_name,
                description=description,
                stages_config=stages_config,
                schedule=data_requirements.get("schedule", "0 */6 * * *")  # Every 6 hours default
            )
            
            logger.info(f"Created AI agent pipeline for {agent_category}: {pipeline_id}")
            return pipeline_id
            
        except Exception as e:
            logger.error(f"Failed to create AI agent pipeline: {e}")
            raise
    
    async def get_pipeline_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get current pipeline execution status
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            status_info: Current execution status and progress
        """
        try:
            if execution_id not in self.executions:
                raise ValueError(f"Execution {execution_id} not found")
            
            execution = self.executions[execution_id]
            pipeline = self.pipelines[execution.pipeline_id]
            
            # Calculate progress
            total_stages = len([s for s in pipeline.stages if s.enabled])
            completed_stages = len([s for s in execution.stage_results if execution.stage_results[s].get("status") == "completed"])
            progress = (completed_stages / total_stages) * 100 if total_stages > 0 else 0
            
            return {
                "execution_id": execution_id,
                "pipeline_id": execution.pipeline_id,
                "pipeline_name": pipeline.pipeline_name,
                "status": execution.status.value,
                "progress_percent": progress,
                "current_stage": execution.current_stage,
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "stage_results": execution.stage_results,
                "metrics": execution.metrics,
                "error_message": execution.error_message
            }
            
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {e}")
            raise
    
    async def pause_pipeline(self, execution_id: str) -> bool:
        """Pause a running pipeline execution"""
        try:
            if execution_id not in self.executions:
                raise ValueError(f"Execution {execution_id} not found")
            
            execution = self.executions[execution_id]
            
            if execution.status != PipelineStatus.RUNNING:
                raise ValueError(f"Execution {execution_id} is not running")
            
            execution.status = PipelineStatus.PAUSED
            
            logger.info(f"Paused pipeline execution {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause pipeline: {e}")
            raise
    
    async def resume_pipeline(self, execution_id: str) -> bool:
        """Resume a paused pipeline execution"""
        try:
            if execution_id not in self.executions:
                raise ValueError(f"Execution {execution_id} not found")
            
            execution = self.executions[execution_id]
            
            if execution.status != PipelineStatus.PAUSED:
                raise ValueError(f"Execution {execution_id} is not paused")
            
            execution.status = PipelineStatus.RUNNING
            
            # Resume pipeline execution
            pipeline = self.pipelines[execution.pipeline_id]
            asyncio.create_task(self._resume_pipeline_execution(execution, pipeline))
            
            logger.info(f"Resumed pipeline execution {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume pipeline: {e}")
            raise
    
    async def list_pipelines(self) -> List[Dict[str, Any]]:
        """List all registered pipelines"""
        try:
            pipelines_list = []
            
            for pipeline_id, pipeline in self.pipelines.items():
                # Get recent executions
                recent_executions = [
                    ex for ex in self.executions.values()
                    if ex.pipeline_id == pipeline_id and
                    ex.started_at >= (datetime.utcnow() - timedelta(days=7))
                ]
                
                pipelines_list.append({
                    "pipeline_id": pipeline_id,
                    "pipeline_name": pipeline.pipeline_name,
                    "description": pipeline.description,
                    "stage_count": len(pipeline.stages),
                    "schedule": pipeline.schedule,
                    "created_at": pipeline.created_at.isoformat(),
                    "recent_executions_count": len(recent_executions),
                    "last_execution_status": recent_executions[-1].status.value if recent_executions else None
                })
            
            return pipelines_list
            
        except Exception as e:
            logger.error(f"Failed to list pipelines: {e}")
            raise
    
    async def _validate_pipeline(self, pipeline: DataPipeline) -> None:
        """Validate pipeline configuration"""
        try:
            # Check for circular dependencies
            await self._check_circular_dependencies(pipeline.stages)
            
            # Validate stage configurations
            for stage in pipeline.stages:
                if stage.stage_type not in self.stage_handlers:
                    logger.warning(f"No handler registered for stage type: {stage.stage_type}")
            
        except Exception as e:
            logger.error(f"Pipeline validation failed: {e}")
            raise
    
    async def _check_circular_dependencies(self, stages: List[PipelineStage]) -> None:
        """Check for circular dependencies in pipeline stages"""
        stage_map = {stage.stage_id: stage for stage in stages}
        visited = set()
        rec_stack = set()
        
        def has_cycle(stage_id: str) -> bool:
            if stage_id in rec_stack:
                return True
            if stage_id in visited:
                return False
            
            visited.add(stage_id)
            rec_stack.add(stage_id)
            
            if stage_id in stage_map:
                for dep_id in stage_map[stage_id].dependencies:
                    if has_cycle(dep_id):
                        return True
            
            rec_stack.remove(stage_id)
            return False
        
        for stage in stages:
            if has_cycle(stage.stage_id):
                raise ValueError("Circular dependency detected in pipeline stages")
    
    async def _run_pipeline_execution(
        self,
        execution: PipelineExecution,
        pipeline: DataPipeline,
        execution_context: Optional[Dict[str, Any]]
    ) -> None:
        """Run complete pipeline execution"""
        try:
            execution.status = PipelineStatus.RUNNING
            
            # Execute stages in dependency order
            execution_order = await self._calculate_execution_order(pipeline.stages)
            
            for stage_id in execution_order:
                stage = next(s for s in pipeline.stages if s.stage_id == stage_id)
                
                if not stage.enabled:
                    continue
                
                execution.current_stage = stage.stage_name
                
                # Execute stage
                stage_result = await self._execute_stage(stage, execution_context)
                execution.stage_results[stage_id] = stage_result
                
                if stage_result.get("status") == "failed":
                    execution.status = PipelineStatus.FAILED
                    execution.error_message = stage_result.get("error_message")
                    break
                
                # Check if paused
                if execution.status == PipelineStatus.PAUSED:
                    break
            
            # Complete execution if not failed or paused
            if execution.status == PipelineStatus.RUNNING:
                execution.status = PipelineStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
            
            # Calculate final metrics
            execution.metrics = await self._calculate_execution_metrics(execution, pipeline)
            
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.error_message = str(e)
            logger.error(f"Pipeline execution failed: {e}")
    
    async def _calculate_execution_order(self, stages: List[PipelineStage]) -> List[str]:
        """Calculate optimal execution order based on dependencies"""
        # Topological sort
        in_degree = {stage.stage_id: 0 for stage in stages}
        adj_list = {stage.stage_id: [] for stage in stages}
        
        # Build adjacency list and calculate in-degrees
        for stage in stages:
            for dep_id in stage.dependencies:
                adj_list[dep_id].append(stage.stage_id)
                in_degree[stage.stage_id] += 1
        
        # Topological sort using Kahn's algorithm
        queue = [stage_id for stage_id in in_degree if in_degree[stage_id] == 0]
        execution_order = []
        
        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            
            for neighbor in adj_list[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return execution_order
    
    async def _execute_stage(
        self,
        stage: PipelineStage,
        execution_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute individual pipeline stage"""
        try:
            start_time = datetime.utcnow()
            
            # Get stage handler
            handler = self.stage_handlers.get(stage.stage_type)
            if not handler:
                return {
                    "status": "failed",
                    "error_message": f"No handler found for stage type: {stage.stage_type}",
                    "execution_time_seconds": 0
                }
            
            # Execute stage with retry logic
            last_error = None
            for attempt in range(stage.retry_count):
                try:
                    result = await asyncio.wait_for(
                        handler(stage, execution_context),
                        timeout=stage.timeout_minutes * 60
                    )
                    
                    execution_time = (datetime.utcnow() - start_time).total_seconds()
                    result["execution_time_seconds"] = execution_time
                    result["attempt"] = attempt + 1
                    
                    return result
                    
                except Exception as e:
                    last_error = e
                    if attempt < stage.retry_count - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            # All retries failed
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return {
                "status": "failed",
                "error_message": str(last_error),
                "execution_time_seconds": execution_time,
                "attempts": stage.retry_count
            }
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return {
                "status": "failed",
                "error_message": str(e),
                "execution_time_seconds": execution_time
            }
    
    async def _create_agent_specific_stages(
        self,
        agent_category: str,
        agent_ids: List[str],
        data_requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Create pipeline stages specific to AI agent category"""
        stages = []
        
        # Common ingestion stage
        stages.append({
            "name": "data_ingestion",
            "type": "ingestion",
            "dependencies": [],
            "config": {
                "sources": data_requirements.get("data_sources", []),
                "format": data_requirements.get("input_format", "json"),
                "batch_size": data_requirements.get("batch_size", 1000)
            }
        })
        
        # Category-specific transformation stages
        if agent_category == "content_processing":
            stages.extend([
                {
                    "name": "text_preprocessing",
                    "type": "transformation",
                    "dependencies": ["data_ingestion"],
                    "config": {"tokenization": True, "normalization": True}
                },
                {
                    "name": "image_preprocessing",
                    "type": "transformation",
                    "dependencies": ["data_ingestion"],
                    "config": {"resize": True, "normalization": True}
                },
                {
                    "name": "audio_preprocessing",
                    "type": "transformation",
                    "dependencies": ["data_ingestion"],
                    "config": {"sample_rate": 16000, "channels": 1}
                }
            ])
        elif agent_category == "creator_intelligence":
            stages.extend([
                {
                    "name": "user_profile_extraction",
                    "type": "feature_engineering",
                    "dependencies": ["data_ingestion"],
                    "config": {"profile_features": ["demographics", "behavior", "preferences"]}
                },
                {
                    "name": "interaction_analysis",
                    "type": "transformation",
                    "dependencies": ["user_profile_extraction"],
                    "config": {"time_windows": ["1d", "7d", "30d"]}
                }
            ])
        elif agent_category == "security_protection":
            stages.extend([
                {
                    "name": "anomaly_feature_extraction",
                    "type": "feature_engineering",
                    "dependencies": ["data_ingestion"],
                    "config": {"statistical_features": True, "temporal_features": True}
                },
                {
                    "name": "threat_pattern_analysis",
                    "type": "transformation",
                    "dependencies": ["anomaly_feature_extraction"],
                    "config": {"pattern_detection": True, "baseline_comparison": True}
                }
            ])
        
        # Common validation and output stages
        stages.extend([
            {
                "name": "data_validation",
                "type": "validation",
                "dependencies": [s["name"] for s in stages if s["type"] in ["transformation", "feature_engineering"]],
                "config": {"quality_checks": True, "schema_validation": True}
            },
            {
                "name": "output_preparation",
                "type": "output",
                "dependencies": ["data_validation"],
                "config": {
                    "output_format": data_requirements.get("output_format", "parquet"),
                    "destination": data_requirements.get("output_destination", "/data/processed")
                }
            }
        ])
        
        return stages
    
    def _register_default_handlers(self) -> None:
        """Register default stage handlers"""
        self.stage_handlers[PipelineStageType.INGESTION] = self._handle_ingestion_stage
        self.stage_handlers[PipelineStageType.TRANSFORMATION] = self._handle_transformation_stage
        self.stage_handlers[PipelineStageType.VALIDATION] = self._handle_validation_stage
        self.stage_handlers[PipelineStageType.FEATURE_ENGINEERING] = self._handle_feature_engineering_stage
        self.stage_handlers[PipelineStageType.OUTPUT] = self._handle_output_stage
    
    async def _handle_ingestion_stage(
        self,
        stage: PipelineStage,
        execution_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle data ingestion stage"""
        # Placeholder implementation
        await asyncio.sleep(1)  # Simulate processing
        return {
            "status": "completed",
            "records_processed": 1000,
            "data_size_mb": 50.5
        }
    
    async def _handle_transformation_stage(
        self,
        stage: PipelineStage,
        execution_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle data transformation stage"""
        # Placeholder implementation
        await asyncio.sleep(2)  # Simulate processing
        return {
            "status": "completed",
            "records_transformed": 950,
            "transformation_applied": stage.config.keys()
        }
    
    async def _handle_validation_stage(
        self,
        stage: PipelineStage,
        execution_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle data validation stage"""
        # Placeholder implementation
        await asyncio.sleep(1)  # Simulate processing
        return {
            "status": "completed",
            "validation_passed": True,
            "quality_score": 0.95
        }
    
    async def _handle_feature_engineering_stage(
        self,
        stage: PipelineStage,
        execution_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle feature engineering stage"""
        # Placeholder implementation
        await asyncio.sleep(3)  # Simulate processing
        return {
            "status": "completed",
            "features_created": 25,
            "feature_quality_score": 0.92
        }
    
    async def _handle_output_stage(
        self,
        stage: PipelineStage,
        execution_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle output stage"""
        # Placeholder implementation
        await asyncio.sleep(1)  # Simulate processing
        return {
            "status": "completed",
            "output_files": 3,
            "output_size_mb": 45.2
        }
    
    async def _calculate_execution_metrics(
        self,
        execution: PipelineExecution,
        pipeline: DataPipeline
    ) -> Dict[str, Any]:
        """Calculate execution metrics"""
        total_time = (execution.completed_at - execution.started_at).total_seconds() if execution.completed_at else 0
        
        return {
            "total_execution_time_seconds": total_time,
            "stages_executed": len(execution.stage_results),
            "stages_successful": len([r for r in execution.stage_results.values() if r.get("status") == "completed"]),
            "stages_failed": len([r for r in execution.stage_results.values() if r.get("status") == "failed"]),
            "total_records_processed": sum(r.get("records_processed", 0) for r in execution.stage_results.values()),
            "average_stage_time": total_time / len(execution.stage_results) if execution.stage_results else 0
        }
    
    async def _resume_pipeline_execution(
        self,
        execution: PipelineExecution,
        pipeline: DataPipeline
    ) -> None:
        """Resume paused pipeline execution"""
        # Find where to resume and continue execution
        # Implementation would continue from the last completed stage
        pass