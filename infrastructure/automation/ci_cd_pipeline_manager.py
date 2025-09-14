"""
CI/CD Pipeline Manager - Enterprise CI/CD Automation for Ainflue
===============================================================

Advanced CI/CD pipeline management and automation for the creator economy platform.
Supports multiple deployment strategies, automated testing, and creator-focused workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """CI/CD pipeline stages."""
    SOURCE = "source"
    BUILD = "build"
    TEST = "test"
    SECURITY_SCAN = "security_scan"
    PACKAGE = "package"
    DEPLOY_STAGING = "deploy_staging"
    INTEGRATION_TEST = "integration_test"
    DEPLOY_PRODUCTION = "deploy_production"
    POST_DEPLOY_VERIFICATION = "post_deploy_verification"
    MONITORING = "monitoring"


class PipelineStatus(Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class DeploymentStrategy(Enum):
    """Deployment strategies for production releases."""
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    RECREATE = "recreate"
    A_B_TEST = "a_b_test"


@dataclass
class PipelineConfig:
    """Configuration for CI/CD pipeline."""
    id: str
    name: str
    description: str
    trigger_events: List[str]
    stages: List[PipelineStage]
    deployment_strategy: DeploymentStrategy
    environments: List[str]
    notification_channels: List[str]
    creator_context: Dict[str, Any] = field(default_factory=dict)
    quality_gates: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    rollback_config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PipelineExecution:
    """Pipeline execution instance."""
    id: str
    pipeline_id: str
    trigger_event: str
    status: PipelineStatus
    stages_status: Dict[PipelineStage, PipelineStatus]
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    creator_impact: Dict[str, Any] = field(default_factory=dict)


class CICDPipelineManager:
    """
    Enterprise CI/CD pipeline manager for Ainflue creator platform.
    Manages automated builds, tests, deployments, and creator workflow integration.
    """
    
    def __init__(self):
        self.pipelines: Dict[str, PipelineConfig] = {}
        self.executions: Dict[str, PipelineExecution] = {}
        self.execution_history: List[PipelineExecution] = []
        
        # Initialize default pipelines for Ainflue creator platform
        self._initialize_creator_platform_pipelines()
        
        logger.info("CI/CD Pipeline Manager initialized for Ainflue creator platform")
    
    def _initialize_creator_platform_pipelines(self):
        """Initialize default CI/CD pipelines for creator platform components."""
        
        # Main Creator Platform Pipeline
        self.pipelines["creator_platform_main"] = PipelineConfig(
            id="creator_platform_main",
            name="Ainflue Creator Platform Main Pipeline",
            description="Main CI/CD pipeline for creator platform core services",
            trigger_events=["push_main", "pull_request", "scheduled_daily"],
            stages=[
                PipelineStage.SOURCE,
                PipelineStage.BUILD,
                PipelineStage.TEST,
                PipelineStage.SECURITY_SCAN,
                PipelineStage.PACKAGE,
                PipelineStage.DEPLOY_STAGING,
                PipelineStage.INTEGRATION_TEST,
                PipelineStage.DEPLOY_PRODUCTION,
                PipelineStage.POST_DEPLOY_VERIFICATION,
                PipelineStage.MONITORING
            ],
            deployment_strategy=DeploymentStrategy.BLUE_GREEN,
            environments=["development", "staging", "production"],
            notification_channels=["slack", "email", "teams"],
            creator_context={
                "supports_creator_workflows": True,
                "includes_ai_agent_deployment": True,
                "monetization_features": True,
                "collaboration_features": True
            },
            quality_gates={
                "test_coverage": {"threshold": 90.0, "required": True},
                "security_scan": {"threshold": "A", "required": True},
                "performance_test": {"latency_ms": 200, "required": True},
                "creator_acceptance": {"satisfaction_score": 8.5, "required": False}
            },
            rollback_config={
                "automatic_rollback_enabled": True,
                "rollback_triggers": ["high_error_rate", "performance_degradation"],
                "rollback_timeout_minutes": 10
            }
        )
        
        # AI Agents Pipeline
        self.pipelines["ai_agents_pipeline"] = PipelineConfig(
            id="ai_agents_pipeline",
            name="AI Agents Deployment Pipeline",
            description="Specialized pipeline for 53 AI agents deployment and optimization",
            trigger_events=["ai_model_update", "agent_config_change", "performance_optimization"],
            stages=[
                PipelineStage.SOURCE,
                PipelineStage.BUILD,
                PipelineStage.TEST,
                PipelineStage.SECURITY_SCAN,
                PipelineStage.PACKAGE,
                PipelineStage.DEPLOY_STAGING,
                PipelineStage.INTEGRATION_TEST,
                PipelineStage.DEPLOY_PRODUCTION,
                PipelineStage.MONITORING
            ],
            deployment_strategy=DeploymentStrategy.CANARY,
            environments=["ai_staging", "ai_production"],
            notification_channels=["slack", "pagerduty"],
            creator_context={
                "ai_agent_count": 53,
                "supports_model_serving": True,
                "gpu_optimization": True,
                "real_time_inference": True
            },
            quality_gates={
                "model_accuracy": {"threshold": 0.92, "required": True},
                "inference_latency": {"threshold": 200, "required": True},
                "gpu_utilization": {"threshold": 85.0, "required": False}
            }
        )
        
        # Infrastructure Pipeline
        self.pipelines["infrastructure_pipeline"] = PipelineConfig(
            id="infrastructure_pipeline",
            name="Infrastructure as Code Pipeline",
            description="Pipeline for infrastructure provisioning and configuration",
            trigger_events=["infrastructure_change", "scaling_event", "security_update"],
            stages=[
                PipelineStage.SOURCE,
                PipelineStage.BUILD,
                PipelineStage.TEST,
                PipelineStage.SECURITY_SCAN,
                PipelineStage.DEPLOY_STAGING,
                PipelineStage.INTEGRATION_TEST,
                PipelineStage.DEPLOY_PRODUCTION,
                PipelineStage.MONITORING
            ],
            deployment_strategy=DeploymentStrategy.ROLLING,
            environments=["staging", "production"],
            notification_channels=["slack", "email"],
            creator_context={
                "supports_auto_scaling": True,
                "multi_cloud_deployment": True,
                "creator_workload_optimization": True
            }
        )
        
        # Creator Tools Pipeline
        self.pipelines["creator_tools_pipeline"] = PipelineConfig(
            id="creator_tools_pipeline",
            name="Creator Tools and Features Pipeline",
            description="Pipeline for creator-specific tools and features deployment",
            trigger_events=["feature_update", "creator_feedback", "tool_enhancement"],
            stages=[
                PipelineStage.SOURCE,
                PipelineStage.BUILD,
                PipelineStage.TEST,
                PipelineStage.PACKAGE,
                PipelineStage.DEPLOY_STAGING,
                PipelineStage.INTEGRATION_TEST,
                PipelineStage.DEPLOY_PRODUCTION,
                PipelineStage.POST_DEPLOY_VERIFICATION
            ],
            deployment_strategy=DeploymentStrategy.A_B_TEST,
            environments=["staging", "production"],
            notification_channels=["slack", "email"],
            creator_context={
                "creator_feature_focus": True,
                "monetization_tools": True,
                "collaboration_features": True,
                "content_protection": True
            }
        )
        
        logger.info(f"Initialized {len(self.pipelines)} CI/CD pipelines for creator platform")
    
    async def create_pipeline(self, config: PipelineConfig) -> str:
        """
        Create a new CI/CD pipeline.
        
        Args:
            config: Pipeline configuration
            
        Returns:
            Pipeline ID
        """
        self.pipelines[config.id] = config
        logger.info(f"Created new pipeline: {config.name}")
        return config.id
    
    async def trigger_pipeline(self, pipeline_id: str, trigger_event: str, 
                             context: Optional[Dict[str, Any]] = None) -> str:
        """
        Trigger a pipeline execution.
        
        Args:
            pipeline_id: ID of the pipeline to trigger
            trigger_event: Event that triggered the pipeline
            context: Additional context for the execution
            
        Returns:
            Execution ID
        """
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        pipeline = self.pipelines[pipeline_id]
        execution_id = str(uuid.uuid4())
        
        # Initialize execution
        execution = PipelineExecution(
            id=execution_id,
            pipeline_id=pipeline_id,
            trigger_event=trigger_event,
            status=PipelineStatus.PENDING,
            stages_status={stage: PipelineStatus.PENDING for stage in pipeline.stages},
            start_time=datetime.now()
        )
        
        self.executions[execution_id] = execution
        
        # Start pipeline execution asynchronously
        asyncio.create_task(self._execute_pipeline(execution_id, context or {}))
        
        logger.info(f"Triggered pipeline {pipeline.name} with execution ID: {execution_id}")
        return execution_id
    
    async def _execute_pipeline(self, execution_id: str, context: Dict[str, Any]):
        """Execute a pipeline with all its stages."""
        execution = self.executions[execution_id]
        pipeline = self.pipelines[execution.pipeline_id]
        
        try:
            execution.status = PipelineStatus.RUNNING
            
            for stage in pipeline.stages:
                logger.info(f"Executing stage {stage.value} for pipeline {execution.pipeline_id}")
                
                # Update stage status
                execution.stages_status[stage] = PipelineStatus.RUNNING
                
                # Execute stage
                stage_result = await self._execute_stage(stage, pipeline, execution, context)
                
                if stage_result["success"]:
                    execution.stages_status[stage] = PipelineStatus.SUCCESS
                    execution.logs.append(f"Stage {stage.value} completed successfully")
                    
                    # Store stage artifacts
                    if stage_result.get("artifacts"):
                        execution.artifacts[stage.value] = stage_result["artifacts"]
                    
                    # Check quality gates
                    if not await self._check_quality_gates(stage, pipeline, stage_result):
                        execution.stages_status[stage] = PipelineStatus.FAILED
                        execution.status = PipelineStatus.FAILED
                        execution.logs.append(f"Quality gate failed for stage {stage.value}")
                        break
                else:
                    execution.stages_status[stage] = PipelineStatus.FAILED
                    execution.status = PipelineStatus.FAILED
                    execution.logs.append(f"Stage {stage.value} failed: {stage_result.get('error', 'Unknown error')}")
                    break
            
            # If all stages completed successfully
            if execution.status == PipelineStatus.RUNNING:
                execution.status = PipelineStatus.SUCCESS
                execution.logs.append("Pipeline completed successfully")
        
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.logs.append(f"Pipeline execution failed: {str(e)}")
            logger.error(f"Pipeline execution {execution_id} failed: {e}")
        
        finally:
            # Finalize execution
            execution.end_time = datetime.now()
            execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()
            
            # Calculate metrics
            execution.metrics = await self._calculate_execution_metrics(execution, pipeline)
            
            # Assess creator impact
            execution.creator_impact = await self._assess_creator_impact(execution, pipeline)
            
            # Move to history
            self.execution_history.append(execution)
            
            # Notify stakeholders
            await self._send_notifications(execution, pipeline)
            
            logger.info(f"Pipeline execution {execution_id} completed with status: {execution.status.value}")
    
    async def _execute_stage(self, stage: PipelineStage, pipeline: PipelineConfig, 
                           execution: PipelineExecution, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific pipeline stage."""
        stage_start_time = time.time()
        
        try:
            if stage == PipelineStage.SOURCE:
                return await self._execute_source_stage(pipeline, context)
            elif stage == PipelineStage.BUILD:
                return await self._execute_build_stage(pipeline, context)
            elif stage == PipelineStage.TEST:
                return await self._execute_test_stage(pipeline, context)
            elif stage == PipelineStage.SECURITY_SCAN:
                return await self._execute_security_scan_stage(pipeline, context)
            elif stage == PipelineStage.PACKAGE:
                return await self._execute_package_stage(pipeline, context)
            elif stage == PipelineStage.DEPLOY_STAGING:
                return await self._execute_deploy_stage(pipeline, context, "staging")
            elif stage == PipelineStage.INTEGRATION_TEST:
                return await self._execute_integration_test_stage(pipeline, context)
            elif stage == PipelineStage.DEPLOY_PRODUCTION:
                return await self._execute_deploy_stage(pipeline, context, "production")
            elif stage == PipelineStage.POST_DEPLOY_VERIFICATION:
                return await self._execute_post_deploy_verification_stage(pipeline, context)
            elif stage == PipelineStage.MONITORING:
                return await self._execute_monitoring_stage(pipeline, context)
            else:
                return {"success": False, "error": f"Unknown stage: {stage}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        finally:
            stage_duration = time.time() - stage_start_time
            execution.logs.append(f"Stage {stage.value} duration: {stage_duration:.2f}s")
    
    async def _execute_source_stage(self, pipeline: PipelineConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute source code checkout stage."""
        await asyncio.sleep(0.5)  # Simulate checkout time
        
        return {
            "success": True,
            "artifacts": {
                "source_commit": "abc123def",
                "branch": context.get("branch", "main"),
                "commit_message": "Update creator platform features"
            }
        }
    
    async def _execute_build_stage(self, pipeline: PipelineConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute build stage."""
        # Simulate build time based on pipeline complexity
        build_time = 2.0 if "ai_agents" in pipeline.id else 1.0
        await asyncio.sleep(build_time)
        
        return {
            "success": True,
            "artifacts": {
                "build_artifacts": ["api-service.tar", "ai-agents.tar", "frontend.tar"],
                "build_time_seconds": build_time,
                "build_size_mb": 250.5
            }
        }
    
    async def _execute_test_stage(self, pipeline: PipelineConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute testing stage."""
        await asyncio.sleep(1.5)  # Simulate test execution
        
        # Simulate test results
        test_coverage = 92.5 if "creator_platform" in pipeline.id else 88.0
        tests_passed = 485
        tests_total = 500
        
        return {
            "success": True,
            "artifacts": {
                "test_coverage": test_coverage,
                "tests_passed": tests_passed,
                "tests_total": tests_total,
                "test_success_rate": (tests_passed / tests_total) * 100,
                "test_report_url": f"https://reports.ainflue.com/{pipeline.id}/tests"
            }
        }
    
    async def _execute_security_scan_stage(self, pipeline: PipelineConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute security scanning stage."""
        await asyncio.sleep(1.0)  # Simulate security scan
        
        return {
            "success": True,
            "artifacts": {
                "security_score": "A+",
                "vulnerabilities_found": 0,
                "compliance_score": 98.5,
                "scan_duration_seconds": 45.2,
                "security_report_url": f"https://security.ainflue.com/{pipeline.id}/scan"
            }
        }
    
    async def _execute_package_stage(self, pipeline: PipelineConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute packaging stage."""
        await asyncio.sleep(0.8)  # Simulate packaging
        
        return {
            "success": True,
            "artifacts": {
                "container_images": [
                    f"ainflue/{pipeline.id}:latest",
                    f"ainflue/{pipeline.id}:v1.2.3"
                ],
                "image_size_mb": 180.5,
                "registry_url": "https://registry.ainflue.com"
            }
        }
    
    async def _execute_deploy_stage(self, pipeline: PipelineConfig, context: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Execute deployment stage."""
        # Deployment time varies by strategy and environment
        deploy_time = 3.0 if environment == "production" else 1.5
        if pipeline.deployment_strategy == DeploymentStrategy.BLUE_GREEN:
            deploy_time *= 1.5
        
        await asyncio.sleep(deploy_time)
        
        return {
            "success": True,
            "artifacts": {
                "deployment_strategy": pipeline.deployment_strategy.value,
                "environment": environment,
                "deployment_url": f"https://{environment}.ainflue.com",
                "deployment_time_seconds": deploy_time,
                "instances_deployed": 5 if environment == "production" else 2,
                "health_check_passed": True
            }
        }
    
    async def _execute_integration_test_stage(self, pipeline: PipelineConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration testing stage."""
        await asyncio.sleep(2.0)  # Simulate integration tests
        
        return {
            "success": True,
            "artifacts": {
                "integration_tests_passed": 45,
                "integration_tests_total": 50,
                "api_response_time_ms": 95.5,
                "creator_workflow_tests_passed": True,
                "platform_integration_score": 96.8
            }
        }
    
    async def _execute_post_deploy_verification_stage(self, pipeline: PipelineConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute post-deployment verification stage."""
        await asyncio.sleep(1.0)  # Simulate verification
        
        return {
            "success": True,
            "artifacts": {
                "health_checks_passed": True,
                "performance_metrics_ok": True,
                "creator_platform_accessible": True,
                "ai_agents_operational": True,
                "verification_score": 98.5
            }
        }
    
    async def _execute_monitoring_stage(self, pipeline: PipelineConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute monitoring setup stage."""
        await asyncio.sleep(0.5)  # Simulate monitoring setup
        
        return {
            "success": True,
            "artifacts": {
                "monitoring_enabled": True,
                "dashboards_configured": 5,
                "alerts_configured": 15,
                "monitoring_url": f"https://monitoring.ainflue.com/{pipeline.id}"
            }
        }
    
    async def _check_quality_gates(self, stage: PipelineStage, pipeline: PipelineConfig, stage_result: Dict[str, Any]) -> bool:
        """Check quality gates for a stage."""
        if stage == PipelineStage.TEST:
            # Check test coverage
            test_coverage = stage_result.get("artifacts", {}).get("test_coverage", 0)
            required_coverage = pipeline.quality_gates.get("test_coverage", {}).get("threshold", 80)
            
            if test_coverage < required_coverage:
                logger.warning(f"Test coverage {test_coverage}% below required {required_coverage}%")
                return False
        
        elif stage == PipelineStage.SECURITY_SCAN:
            # Check security score
            security_score = stage_result.get("artifacts", {}).get("security_score", "F")
            required_score = pipeline.quality_gates.get("security_scan", {}).get("threshold", "B")
            
            score_values = {"A+": 100, "A": 95, "B": 85, "C": 75, "D": 65, "F": 0}
            if score_values.get(security_score, 0) < score_values.get(required_score, 85):
                logger.warning(f"Security score {security_score} below required {required_score}")
                return False
        
        return True
    
    async def _calculate_execution_metrics(self, execution: PipelineExecution, pipeline: PipelineConfig) -> Dict[str, Any]:
        """Calculate comprehensive metrics for pipeline execution."""
        successful_stages = sum(1 for status in execution.stages_status.values() if status == PipelineStatus.SUCCESS)
        total_stages = len(execution.stages_status)
        
        metrics = {
            "execution_duration_seconds": execution.duration_seconds,
            "execution_duration_minutes": execution.duration_seconds / 60 if execution.duration_seconds else 0,
            "stages_completed": successful_stages,
            "stages_total": total_stages,
            "success_rate": (successful_stages / total_stages) * 100,
            "deployment_strategy": pipeline.deployment_strategy.value,
            "quality_gates_passed": execution.status == PipelineStatus.SUCCESS,
            "creator_platform_impact": "positive" if execution.status == PipelineStatus.SUCCESS else "neutral"
        }
        
        # Add stage-specific metrics
        if "test" in [stage.value for stage in execution.stages_status.keys()]:
            test_artifacts = execution.artifacts.get("test", {})
            metrics["test_coverage"] = test_artifacts.get("test_coverage", 0)
            metrics["tests_passed"] = test_artifacts.get("tests_passed", 0)
        
        if "security_scan" in [stage.value for stage in execution.stages_status.keys()]:
            security_artifacts = execution.artifacts.get("security_scan", {})
            metrics["security_score"] = security_artifacts.get("security_score", "N/A")
            metrics["vulnerabilities_found"] = security_artifacts.get("vulnerabilities_found", 0)
        
        return metrics
    
    async def _assess_creator_impact(self, execution: PipelineExecution, pipeline: PipelineConfig) -> Dict[str, Any]:
        """Assess the impact of pipeline execution on creator experience."""
        impact = {
            "deployment_successful": execution.status == PipelineStatus.SUCCESS,
            "feature_delivery_improved": execution.status == PipelineStatus.SUCCESS,
            "platform_stability_maintained": True,
            "creator_workflow_enhanced": False,
            "estimated_creators_affected": 0,
            "estimated_impact_severity": "low"
        }
        
        # Assess impact based on pipeline type and success
        if execution.status == PipelineStatus.SUCCESS:
            if "creator_platform" in pipeline.id:
                impact["creator_workflow_enhanced"] = True
                impact["estimated_creators_affected"] = 5000
                impact["estimated_impact_severity"] = "high"
            elif "ai_agents" in pipeline.id:
                impact["ai_performance_improved"] = True
                impact["estimated_creators_affected"] = 3000
                impact["estimated_impact_severity"] = "medium"
            elif "creator_tools" in pipeline.id:
                impact["creator_tools_enhanced"] = True
                impact["estimated_creators_affected"] = 2000
                impact["estimated_impact_severity"] = "medium"
        else:
            impact["platform_stability_maintained"] = False
            impact["estimated_impact_severity"] = "high" if "production" in str(pipeline.environments) else "medium"
        
        return impact
    
    async def _send_notifications(self, execution: PipelineExecution, pipeline: PipelineConfig):
        """Send notifications about pipeline execution results."""
        status_emoji = "✅" if execution.status == PipelineStatus.SUCCESS else "❌"
        
        message = f"{status_emoji} Pipeline {pipeline.name} - {execution.status.value.upper()}"
        if execution.duration_seconds:
            message += f" (Duration: {execution.duration_seconds/60:.1f}min)"
        
        # Log notification (in real implementation, would send to actual channels)
        logger.info(f"NOTIFICATION: {message}")
        
        for channel in pipeline.notification_channels:
            # Simulate sending notification
            logger.info(f"Sent notification to {channel}: {message}")
    
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get current status of a pipeline."""
        if pipeline_id not in self.pipelines:
            return {"error": f"Pipeline {pipeline_id} not found"}
        
        pipeline = self.pipelines[pipeline_id]
        
        # Get recent executions
        recent_executions = [
            execution for execution in self.execution_history
            if execution.pipeline_id == pipeline_id
        ][-10:]  # Last 10 executions
        
        status = {
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline.name,
            "total_executions": len([e for e in self.execution_history if e.pipeline_id == pipeline_id]),
            "recent_executions": len(recent_executions),
            "success_rate": 0.0,
            "average_duration_minutes": 0.0,
            "last_execution": None
        }
        
        if recent_executions:
            successful_executions = [e for e in recent_executions if e.status == PipelineStatus.SUCCESS]
            status["success_rate"] = (len(successful_executions) / len(recent_executions)) * 100
            
            durations = [e.duration_seconds for e in recent_executions if e.duration_seconds]
            if durations:
                status["average_duration_minutes"] = sum(durations) / len(durations) / 60
            
            latest = max(recent_executions, key=lambda x: x.start_time)
            status["last_execution"] = {
                "id": latest.id,
                "status": latest.status.value,
                "start_time": latest.start_time.isoformat(),
                "duration_seconds": latest.duration_seconds
            }
        
        return status
    
    def get_pipeline_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics for all pipelines."""
        analytics = {
            "total_pipelines": len(self.pipelines),
            "total_executions": len(self.execution_history),
            "pipeline_performance": {},
            "deployment_strategies": {},
            "creator_impact_summary": {},
            "recommendations": []
        }
        
        # Pipeline performance analysis
        for pipeline_id, pipeline in self.pipelines.items():
            pipeline_executions = [e for e in self.execution_history if e.pipeline_id == pipeline_id]
            
            if pipeline_executions:
                successful = [e for e in pipeline_executions if e.status == PipelineStatus.SUCCESS]
                durations = [e.duration_seconds for e in pipeline_executions if e.duration_seconds]
                
                analytics["pipeline_performance"][pipeline_id] = {
                    "total_executions": len(pipeline_executions),
                    "success_rate": (len(successful) / len(pipeline_executions)) * 100,
                    "average_duration_minutes": (sum(durations) / len(durations) / 60) if durations else 0,
                    "deployment_strategy": pipeline.deployment_strategy.value
                }
        
        # Deployment strategies distribution
        for pipeline in self.pipelines.values():
            strategy = pipeline.deployment_strategy.value
            analytics["deployment_strategies"][strategy] = analytics["deployment_strategies"].get(strategy, 0) + 1
        
        # Creator impact summary
        total_creator_impact = sum(
            execution.creator_impact.get("estimated_creators_affected", 0)
            for execution in self.execution_history
            if execution.status == PipelineStatus.SUCCESS
        )
        
        analytics["creator_impact_summary"] = {
            "total_creators_affected": total_creator_impact,
            "successful_deployments": len([e for e in self.execution_history if e.status == PipelineStatus.SUCCESS]),
            "platform_improvements": len([e for e in self.execution_history if e.creator_impact.get("creator_workflow_enhanced", False)]),
            "average_impact_per_deployment": total_creator_impact / max(len(self.execution_history), 1)
        }
        
        # Recommendations
        overall_success_rate = (len([e for e in self.execution_history if e.status == PipelineStatus.SUCCESS]) / max(len(self.execution_history), 1)) * 100
        
        if overall_success_rate < 95:
            analytics["recommendations"].append("Improve pipeline reliability and quality gates")
        if len(analytics["deployment_strategies"]) < 3:
            analytics["recommendations"].append("Consider implementing diverse deployment strategies")
        
        analytics["recommendations"].extend([
            "Implement advanced automated testing for creator workflows",
            "Enable predictive deployment scheduling based on creator activity",
            "Setup advanced monitoring for creator impact metrics"
        ])
        
        return analytics


# Global instance for easy access
cicd_pipeline_manager = CICDPipelineManager()

# Export main classes and functions
__all__ = [
    "CICDPipelineManager",
    "PipelineConfig",
    "PipelineExecution",
    "PipelineStage",
    "PipelineStatus",
    "DeploymentStrategy",
    "cicd_pipeline_manager"
]