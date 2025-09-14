"""Pipeline Orchestrator for Coordinated Workflow Management
========================================================

Professional orchestration system managing complex multi-pipeline workflows
for content processing, protection, monetization, and distribution.

Team Specialties:
- Lead Developer AI: Fahed Mlaiel - Advanced orchestration architecture
- Workflow Engineer: Complex process coordination and management
- Performance Engineer: High-throughput pipeline optimization
- Monitoring Engineer: System health and performance tracking
- Integration Engineer: Cross-pipeline data flow management

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT WARNING ⚠️
This proprietary orchestration technology and workflow management systems
belong exclusively to Fahed Mlaiel. Any unauthorized use, reverse engineering,
or competitive implementation will result in immediate legal action.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable
from uuid import uuid4
from enum import Enum

import aiohttp
from celery import Celery
from redis import Redis

from backend.core.config import get_settings
from backend.core.database import AsyncDatabaseSession
from backend.core.exceptions import (
    OrchestrationError,
    WorkflowError,
    PipelineError,
    MonitoringError
)
from backend.data.pipelines.content_ingestion import ContentIngestionPipeline
from backend.data.pipelines.protection_pipeline import ProtectionPipeline
from backend.data.pipelines.monetization_pipeline import MonetizationPipeline
from backend.data.pipelines.analytics_pipeline import AnalyticsPipeline
from backend.data.pipelines.collaboration_pipeline import CollaborationPipeline
from backend.data.pipelines.distribution_pipeline import DistributionPipeline
from backend.models.orchestration import (
    WorkflowExecution,
    PipelineTask,
    WorkflowMetrics,
    OrchestrationLog
)
from backend.utils.logging import get_logger
from backend.utils.notifications import NotificationManager
from backend.utils.cache import CacheManager

logger = get_logger(__name__)
settings = get_settings()


class WorkflowType(str, Enum):
    """
Types of orchestrated workflows"""

    CONTENT_LIFECYCLE = "content_lifecycle"           # Full content processing
    PROTECTION_ACTIVATION = "protection_activation"   # Content protection setup
    REVENUE_OPTIMIZATION = "revenue_optimization"     # Monetization optimization
    COLLABORATION_MATCHING = "collaboration_matching" # Creator matching
    MULTI_PLATFORM_DISTRIBUTION = "multi_platform_distribution"  # Content distribution
    ANALYTICS_GENERATION = "analytics_generation"     # Comprehensive analytics
    AUTOMATED_MANAGEMENT = "automated_management"      # Automated content management


class PipelineStatus(str, Enum):
    """Pipeline execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class WorkflowPriority(str, Enum):
    """Workflow execution priority"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowManager:
    """
    Advanced workflow management system for complex multi-step processes
    """
    
    def __init__(self) -> None:
        self.redis_client = Redis.from_url(settings.REDIS_URL)
        self.celery_app = Celery('pipeline_orchestrator')
        
        # Pipeline registry
        self.pipelines = {
            "content_ingestion": ContentIngestionPipeline(),
            "protection": ProtectionPipeline(),
            "monetization": MonetizationPipeline(),
            "analytics": AnalyticsPipeline(),
            "collaboration": CollaborationPipeline(),
            "distribution": DistributionPipeline()
        }
        
        # Workflow definitions
        self.workflow_definitions = {
            WorkflowType.CONTENT_LIFECYCLE: {
                "steps": [
                    {"pipeline": "content_ingestion", "method": "process_upload"},
                    {"pipeline": "protection", "method": "protect_content"},
                    {"pipeline": "analytics", "method": "analyze_content_performance"},
                    {"pipeline": "monetization", "method": "setup_revenue_tracking"}
                ],
                "parallel_steps": [],
                "rollback_strategy": "full",
                "timeout_minutes": 30
            },
            WorkflowType.PROTECTION_ACTIVATION: {
                "steps": [
                    {"pipeline": "protection", "method": "generate_fingerprint"},
                    {"pipeline": "protection", "method": "initiate_monitoring"},
                    {"pipeline": "analytics", "method": "setup_protection_metrics"}
                ],
                "parallel_steps": ["protection.generate_fingerprint", "analytics.setup_protection_metrics"],
                "rollback_strategy": "selective",
                "timeout_minutes": 15
            },
            WorkflowType.REVENUE_OPTIMIZATION: {
                "steps": [
                    {"pipeline": "analytics", "method": "analyze_revenue_potential"},
                    {"pipeline": "monetization", "method": "optimize_revenue_strategy"},
                    {"pipeline": "distribution", "method": "optimize_platform_mix"}
                ],
                "parallel_steps": [],
                "rollback_strategy": "none",
                "timeout_minutes": 20
            },
            WorkflowType.COLLABORATION_MATCHING: {
                "steps": [
                    {"pipeline": "analytics", "method": "analyze_creator_profile"},
                    {"pipeline": "collaboration", "method": "find_matches"},
                    {"pipeline": "collaboration", "method": "generate_recommendations"}
                ],
                "parallel_steps": [],
                "rollback_strategy": "none",
                "timeout_minutes": 10
            },
            WorkflowType.MULTI_PLATFORM_DISTRIBUTION: {
                "steps": [
                    {"pipeline": "distribution", "method": "optimize_content"},
                    {"pipeline": "distribution", "method": "schedule_distribution"},
                    {"pipeline": "analytics", "method": "setup_performance_tracking"}
                ],
                "parallel_steps": ["distribution.optimize_content"],
                "rollback_strategy": "selective",
                "timeout_minutes": 25
            }
        }

    async def execute_workflow(
        self,
        workflow_type: WorkflowType,
        workflow_data: Dict[str, Any],
        priority: WorkflowPriority = WorkflowPriority.NORMAL
    ) -> Dict[str, Any]:
        """
        Execute a complete workflow with error handling and monitoring
        """
        try:
            workflow_id = str(uuid4())
            logger.info(f"Starting workflow execution: {workflow_id} ({workflow_type.value})")
            
            # Get workflow definition
            workflow_def = self.workflow_definitions.get(workflow_type)
            if not workflow_def:
                raise WorkflowError(f"Unknown workflow type: {workflow_type.value}")
            
            # Create workflow execution record
            execution = WorkflowExecution(
                id=workflow_id,
                workflow_type=workflow_type.value,
                input_data=workflow_data,
                status=PipelineStatus.RUNNING.value,
                priority=priority.value,
                started_at=datetime.utcnow(),
                timeout_at=datetime.utcnow() + timedelta(minutes=workflow_def["timeout_minutes"])
            )
            
            # Save initial execution record
            async with AsyncDatabaseSession() as session:
                session.add(execution)
                await session.commit()
            
            # Execute workflow steps
            execution_result = await self._execute_workflow_steps(
                workflow_id, workflow_def, workflow_data
            )
            
            # Update execution record
            execution.status = PipelineStatus.COMPLETED.value
            execution.completed_at = datetime.utcnow()
            execution.output_data = execution_result
            execution.success = True
            
            async with AsyncDatabaseSession() as session:
                await session.merge(execution)
                await session.commit()
            
            logger.info(f"Workflow completed successfully: {workflow_id}")
            
            return {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type.value,
                "status": "completed",
                "execution_time_seconds": (execution.completed_at - execution.started_at).total_seconds(),
                "result": execution_result
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            
            # Update execution record with failure
            try:
                async with AsyncDatabaseSession() as session:
                    execution = await session.get(WorkflowExecution, workflow_id)
                    if execution:
                        execution.status = PipelineStatus.FAILED.value
                        execution.error_message = str(e)
                        execution.completed_at = datetime.utcnow()
                        execution.success = False
                        await session.commit()
            except:
                pass  # Don't fail on logging failure
            
            raise WorkflowError(f"Workflow execution failed: {str(e)}")

    async def _execute_workflow_steps(
        self,
        workflow_id: str,
        workflow_def: Dict[str, Any],
        workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute individual workflow steps with dependency management
        """
        steps = workflow_def["steps"]
        parallel_steps = workflow_def.get("parallel_steps", [])
        
        step_results = {}
        execution_context = {"workflow_id": workflow_id, **workflow_data}
        
        # Group steps by execution phase
        sequential_steps = []
        parallel_step_groups = []
        
        for step in steps:
            step_key = f"{step['pipeline']}.{step['method']}"
            
            if step_key in parallel_steps:
                # Find or create parallel group
                group_found = False
                for group in parallel_step_groups:
                    if step_key in group:
                        group_found = True
                        break
                
                if not group_found:
                    # Create new parallel group
                    parallel_group = [step for s in steps 
                                    if f"{s['pipeline']}.{s['method']}" in parallel_steps]
                    parallel_step_groups.append(parallel_group)
            else:
                sequential_steps.append(step)
        
        # Execute parallel groups first
        for parallel_group in parallel_step_groups:
            parallel_tasks = []
            
            for step in parallel_group:
                task = self._execute_pipeline_step(
                    workflow_id, step, execution_context, step_results
                )
                parallel_tasks.append(task)
            
            # Wait for all parallel tasks to complete
            parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
            
            # Process parallel results
            for i, result in enumerate(parallel_results):
                step = parallel_group[i]
                step_key = f"{step['pipeline']}.{step['method']}"
                
                if isinstance(result, Exception):
                    raise PipelineError(f"Step {step_key} failed: {str(result)}")
                
                step_results[step_key] = result
                execution_context.update(result)
        
        # Execute sequential steps
        for step in sequential_steps:
            step_key = f"{step['pipeline']}.{step['method']}"
            
            if step_key not in step_results:  # Skip if already executed in parallel
                result = await self._execute_pipeline_step(
                    workflow_id, step, execution_context, step_results
                )
                
                step_results[step_key] = result
                execution_context.update(result)
        
        return {
            "workflow_id": workflow_id,
            "step_results": step_results,
            "execution_summary": {
                "total_steps": len(steps),
                "successful_steps": len(step_results),
                "parallel_groups": len(parallel_step_groups)
            }
        }

    async def _execute_pipeline_step(
        self,
        workflow_id: str,
        step: Dict[str, str],
        execution_context: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute individual pipeline step with monitoring
        """
        pipeline_name = step["pipeline"]
        method_name = step["method"]
        step_key = f"{pipeline_name}.{method_name}"
        
        logger.info(f"Executing step: {step_key} for workflow {workflow_id}")
        
        # Create step task record
        task = PipelineTask(
            id=str(uuid4()),
            workflow_id=workflow_id,
            pipeline_name=pipeline_name,
            method_name=method_name,
            input_data=execution_context,
            status=PipelineStatus.RUNNING.value,
            started_at=datetime.utcnow()
        )
        
        try:
            # Get pipeline and method
            pipeline = self.pipelines.get(pipeline_name)
            if not pipeline:
                raise PipelineError(f"Unknown pipeline: {pipeline_name}")
            
            method = getattr(pipeline, method_name, None)
            if not method:
                raise PipelineError(f"Unknown method: {method_name} in {pipeline_name}")
            
            # Execute pipeline method
            start_time = datetime.utcnow()
            
            # Prepare method arguments from context
            method_args = self._prepare_method_arguments(
                method, execution_context, previous_results
            )
            
            result = await method(**method_args)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update task record
            task.status = PipelineStatus.COMPLETED.value
            task.completed_at = datetime.utcnow()
            task.output_data = result
            task.execution_time_seconds = execution_time
            task.success = True
            
            logger.info(f"Step completed: {step_key} in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Step failed: {step_key} - {str(e)}")
            
            # Update task record with failure
            task.status = PipelineStatus.FAILED.value
            task.completed_at = datetime.utcnow()
            task.error_message = str(e)
            task.success = False
            
            raise PipelineError(f"Step {step_key} failed: {str(e)}")
        
        finally:
            # Save task record
            try:
                async with AsyncDatabaseSession() as session:
                    session.add(task)
                    await session.commit()
            except Exception as e:
                logger.warning(f"Failed to save task record: {str(e)}")

    def _prepare_method_arguments(
        self,
        method: Callable,
        execution_context: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare method arguments from execution context
        """
        import inspect
        
        # Get method signature
        sig = inspect.signature(method)
        method_args = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            
            # Try to find parameter value in context
            if param_name in execution_context:
                method_args[param_name] = execution_context[param_name]
            elif param_name in previous_results:
                method_args[param_name] = previous_results[param_name]
            elif param.default is not inspect.Parameter.empty:
                # Use default value
                continue
            else:
                # Try common parameter mappings
                param_mappings = {
                    "user_id": execution_context.get("user_id"),
                    "content_id": execution_context.get("content_id"),
                    "data": execution_context,
                    "config": execution_context.get("config", {}),
                    "options": execution_context.get("options", {})
                }
                
                if param_name in param_mappings:
                    value = param_mappings[param_name]
                    if value is not None:
                        method_args[param_name] = value
        
        return method_args

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get detailed workflow execution status
        """
        try:
            async with AsyncDatabaseSession() as session:
                # Get workflow execution
                execution = await session.get(WorkflowExecution, workflow_id)
                if not execution:
                    raise WorkflowError("Workflow not found")
                
                # Get all tasks for this workflow
                tasks = await session.query(PipelineTask).filter(
                    PipelineTask.workflow_id == workflow_id
                ).all()
            
            # Calculate workflow metrics
            total_execution_time = 0
            step_details = []
            
            for task in tasks:
                step_detail = {
                    "step": f"{task.pipeline_name}.{task.method_name}",
                    "status": task.status,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "execution_time_seconds": task.execution_time_seconds,
                    "success": task.success,
                    "error_message": task.error_message
                }
                step_details.append(step_detail)
                
                if task.execution_time_seconds:
                    total_execution_time += task.execution_time_seconds
            
            return {
                "workflow_id": workflow_id,
                "workflow_type": execution.workflow_type,
                "status": execution.status,
                "priority": execution.priority,
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "total_execution_time_seconds": total_execution_time,
                "success": execution.success,
                "error_message": execution.error_message,
                "step_details": step_details,
                "progress": {
                    "total_steps": len(step_details),
                    "completed_steps": len([t for t in tasks if t.status == PipelineStatus.COMPLETED.value]),
                    "failed_steps": len([t for t in tasks if t.status == PipelineStatus.FAILED.value]),
                    "running_steps": len([t for t in tasks if t.status == PipelineStatus.RUNNING.value])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
            raise WorkflowError(f"Status retrieval failed: {str(e)}")

    async def cancel_workflow(self, workflow_id: str, reason: str = "User cancelled") -> Dict[str, Any]:
        """
        Cancel running workflow
        """
        try:
            async with AsyncDatabaseSession() as session:
                execution = await session.get(WorkflowExecution, workflow_id)
                if not execution:
                    raise WorkflowError("Workflow not found")
                
                if execution.status not in [PipelineStatus.RUNNING.value, PipelineStatus.PENDING.value]:
                    raise WorkflowError("Workflow cannot be cancelled in current status")
                
                # Update execution status
                execution.status = PipelineStatus.CANCELLED.value
                execution.completed_at = datetime.utcnow()
                execution.error_message = f"Cancelled: {reason}"
                execution.success = False
                
                # Cancel running tasks
                tasks = await session.query(PipelineTask).filter(
                    PipelineTask.workflow_id == workflow_id,
                    PipelineTask.status == PipelineStatus.RUNNING.value
                ).all()
                
                for task in tasks:
                    task.status = PipelineStatus.CANCELLED.value
                    task.completed_at = datetime.utcnow()
                    task.error_message = f"Cancelled: {reason}"
                    task.success = False
                
                await session.commit()
            
            logger.info(f"Workflow cancelled: {workflow_id}")
            
            return {
                "workflow_id": workflow_id,
                "status": "cancelled",
                "reason": reason,
                "cancelled_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow: {str(e)}")
            raise WorkflowError(f"Cancellation failed: {str(e)}")


class PipelineMonitor:
    """
    System monitoring and health checking for pipeline operations
    """
    
    def __init__(self) -> None:
        self.cache_manager = CacheManager()
        self.notification_manager = NotificationManager()
        
        # Health check thresholds
        self.health_thresholds = {
            "max_execution_time_minutes": 60,
            "max_failure_rate_percent": 10,
            "max_queue_size": 1000,
            "min_success_rate_percent": 90
        }

    async def check_system_health(self) -> Dict[str, Any]:
        """
        Comprehensive system health check
        """
        try:
            health_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": "healthy",
                "pipeline_health": {},
                "workflow_metrics": {},
                "resource_usage": {},
                "alerts": []
            }
            
            # Check individual pipeline health
            for pipeline_name in ["content_ingestion", "protection", "monetization", 
                                "analytics", "collaboration", "distribution"]:
                pipeline_health = await self._check_pipeline_health(pipeline_name)
                health_report["pipeline_health"][pipeline_name] = pipeline_health
                
                if pipeline_health["status"] != "healthy":
                    health_report["overall_status"] = "degraded"
            
            # Check workflow execution metrics
            workflow_metrics = await self._get_workflow_metrics()
            health_report["workflow_metrics"] = workflow_metrics
            
            # Check resource usage
            resource_usage = await self._check_resource_usage()
            health_report["resource_usage"] = resource_usage
            
            # Generate alerts
            alerts = await self._generate_health_alerts(health_report)
            health_report["alerts"] = alerts
            
            if alerts:
                health_report["overall_status"] = "warning" if health_report["overall_status"] == "healthy" else "critical"
            
            return health_report
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": "critical",
                "error": str(e)
            }

    async def _check_pipeline_health(self, pipeline_name: str) -> Dict[str, Any]:
        """Check health of individual pipeline"""
        try:
            # Get recent task statistics
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)
            
            async with AsyncDatabaseSession() as session:
                tasks = await session.query(PipelineTask).filter(
                    PipelineTask.pipeline_name == pipeline_name,
                    PipelineTask.started_at >= start_time
                ).all()
            
            if not tasks:
                return {
                    "status": "healthy",
                    "message": "No recent activity",
                    "metrics": {"total_tasks": 0}
                }
            
            # Calculate metrics
            total_tasks = len(tasks)
            successful_tasks = len([t for t in tasks if t.success])
            failed_tasks = len([t for t in tasks if not t.success and t.status == PipelineStatus.FAILED.value])
            
            success_rate = (successful_tasks / total_tasks) * 100 if total_tasks > 0 else 100
            failure_rate = (failed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
            
            avg_execution_time = sum(
                t.execution_time_seconds for t in tasks 
                if t.execution_time_seconds
            ) / len([t for t in tasks if t.execution_time_seconds]) if tasks else 0
            
            # Determine health status
            status = "healthy"
            message = "Pipeline operating normally"
            
            if failure_rate > self.health_thresholds["max_failure_rate_percent"]:
                status = "unhealthy"
                message = f"High failure rate: {failure_rate:.1f}%"
            elif success_rate < self.health_thresholds["min_success_rate_percent"]:
                status = "degraded"
                message = f"Low success rate: {success_rate:.1f}%"
            elif avg_execution_time > (self.health_thresholds["max_execution_time_minutes"] * 60):
                status = "degraded"
                message = f"High execution time: {avg_execution_time:.1f}s"
            
            return {
                "status": status,
                "message": message,
                "metrics": {
                    "total_tasks": total_tasks,
                    "successful_tasks": successful_tasks,
                    "failed_tasks": failed_tasks,
                    "success_rate_percent": round(success_rate, 2),
                    "failure_rate_percent": round(failure_rate, 2),
                    "avg_execution_time_seconds": round(avg_execution_time, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Pipeline health check failed for {pipeline_name}: {str(e)}")
            return {
                "status": "critical",
                "message": f"Health check failed: {str(e)}",
                "metrics": {}
            }

    async def _get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow execution metrics"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            async with AsyncDatabaseSession() as session:
                workflows = await session.query(WorkflowExecution).filter(
                    WorkflowExecution.started_at >= start_time
                ).all()
            
            if not workflows:
                return {"total_workflows": 0}
            
            # Calculate metrics
            total_workflows = len(workflows)
            successful_workflows = len([w for w in workflows if w.success])
            failed_workflows = len([w for w in workflows if not w.success])
            running_workflows = len([w for w in workflows if w.status == PipelineStatus.RUNNING.value])
            
            # Workflow type breakdown
            type_breakdown = {}
            for workflow in workflows:
                wf_type = workflow.workflow_type
                if wf_type not in type_breakdown:
                    type_breakdown[wf_type] = {"total": 0, "successful": 0, "failed": 0}
                
                type_breakdown[wf_type]["total"] += 1
                if workflow.success:
                    type_breakdown[wf_type]["successful"] += 1
                elif not workflow.success:
                    type_breakdown[wf_type]["failed"] += 1
            
            return {
                "total_workflows": total_workflows,
                "successful_workflows": successful_workflows,
                "failed_workflows": failed_workflows,
                "running_workflows": running_workflows,
                "success_rate_percent": (successful_workflows / total_workflows) * 100 if total_workflows > 0 else 100,
                "type_breakdown": type_breakdown
            }
            
        except Exception as e:
            logger.error(f"Workflow metrics collection failed: {str(e)}")
            return {"error": str(e)}

    async def _check_resource_usage(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Redis connection info
            redis_info = {}
            try:
                redis_client = Redis.from_url(settings.REDIS_URL)
                redis_info = {
                    "connected_clients": redis_client.info().get("connected_clients", 0),
                    "used_memory": redis_client.info().get("used_memory", 0),
                    "used_memory_human": redis_client.info().get("used_memory_human", "0B")
                }
            except:
                redis_info = {"error": "Could not connect to Redis"}
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "redis_info": redis_info
            }
            
        except Exception as e:
            logger.error(f"Resource usage check failed: {str(e)}")
            return {"error": str(e)}

    async def _generate_health_alerts(self, health_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate health alerts based on metrics"""
        alerts = []
        
        # Check pipeline health alerts
        for pipeline_name, health in health_report.get("pipeline_health", {}).items():
            if health.get("status") in ["unhealthy", "critical"]:
                alerts.append({
                    "type": "pipeline_health",
                    "severity": "high" if health["status"] == "critical" else "medium",
                    "message": f"Pipeline {pipeline_name} is {health['status']}: {health['message']}",
                    "pipeline": pipeline_name,
                    "metrics": health.get("metrics", {})
                })
        
        # Check resource usage alerts
        resource_usage = health_report.get("resource_usage", {})
        
        if resource_usage.get("cpu_percent", 0) > 80:
            alerts.append({
                "type": "resource_usage",
                "severity": "high" if resource_usage["cpu_percent"] > 90 else "medium",
                "message": f"High CPU usage: {resource_usage['cpu_percent']:.1f}%",
                "metric": "cpu_percent",
                "value": resource_usage["cpu_percent"]
            })
        
        if resource_usage.get("memory_percent", 0) > 80:
            alerts.append({
                "type": "resource_usage",
                "severity": "high" if resource_usage["memory_percent"] > 90 else "medium",
                "message": f"High memory usage: {resource_usage['memory_percent']:.1f}%",
                "metric": "memory_percent",
                "value": resource_usage["memory_percent"]
            })
        
        # Check workflow metrics alerts
        workflow_metrics = health_report.get("workflow_metrics", {})
        success_rate = workflow_metrics.get("success_rate_percent", 100)
        
        if success_rate < self.health_thresholds["min_success_rate_percent"]:
            alerts.append({
                "type": "workflow_performance",
                "severity": "high" if success_rate < 80 else "medium",
                "message": f"Low workflow success rate: {success_rate:.1f}%",
                "metric": "success_rate_percent",
                "value": success_rate
            })
        
        return alerts


class HealthChecker:
    """
    Automated health checking and alerting system
    """
    
    def __init__(self) -> None:
        self.monitor = PipelineMonitor()
        self.notification_manager = NotificationManager()

    async def run_health_check_cycle(self) -> None:
        """
        Run complete health check cycle with alerting
        """
        try:
            logger.info("Starting health check cycle")
            
            # Run system health check
            health_report = await self.monitor.check_system_health()
            
            # Process alerts
            alerts = health_report.get("alerts", [])
            
            if alerts:
                # Send alerts to administrators
                await self._send_health_alerts(alerts, health_report)
            
            # Log health status
            overall_status = health_report.get("overall_status", "unknown")
            logger.info(f"Health check completed - Status: {overall_status}, Alerts: {len(alerts)}")
            
            # Save health metrics
            await self._save_health_metrics(health_report)
            
            return health_report
            
        except Exception as e:
            logger.error(f"Health check cycle failed: {str(e)}")
            
            # Send critical alert
            await self._send_critical_alert(str(e))
            
            raise MonitoringError(f"Health check failed: {str(e)}")

    async def _send_health_alerts(self, alerts -> None: List[Dict[str, Any]], health_report -> None: Dict[str, Any]) -> None:
        """Send health alerts to administrators"""
        try:
            high_severity_alerts = [a for a in alerts if a.get("severity") == "high"]
            
            if high_severity_alerts:
                # Send immediate notification for high severity
                await self.notification_manager.send_admin_alert(
                    "System Health Alert",
                    f"Detected {len(high_severity_alerts)} high severity issues",
                    {
                        "alerts": high_severity_alerts,
                        "overall_status": health_report.get("overall_status"),
                        "timestamp": health_report.get("timestamp")
                    }
                )
            
            # Log all alerts
            for alert in alerts:
                logger.warning(f"Health Alert [{alert.get('severity', 'unknown')}]: {alert.get('message')}")
                
        except Exception as e:
            logger.error(f"Failed to send health alerts: {str(e)}")

    async def _send_critical_alert(self, error_message -> None: str) -> None:
        """Send critical system alert"""
        try:
            await self.notification_manager.send_admin_alert(
                "Critical System Error",
                f"Health check system failure: {error_message}",
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": error_message,
                    "severity": "critical"
                }
            )
        except Exception as e:
            logger.error(f"Failed to send critical alert: {str(e)}")

    async def _save_health_metrics(self, health_report -> None: Dict[str, Any]) -> None:
        """Save health metrics to database"""
        try:
            metrics = WorkflowMetrics(
                id=str(uuid4()),
                timestamp=datetime.utcnow(),
                overall_status=health_report.get("overall_status"),
                pipeline_health=health_report.get("pipeline_health", {}),
                workflow_metrics=health_report.get("workflow_metrics", {}),
                resource_usage=health_report.get("resource_usage", {}),
                alert_count=len(health_report.get("alerts", []))
            )
            
            async with AsyncDatabaseSession() as session:
                session.add(metrics)
                await session.commit()
                
        except Exception as e:
            logger.error(f"Failed to save health metrics: {str(e)}")


class PipelineOrchestrator:
    """
    Main orchestrator managing all pipeline operations and workflows
    """
    
    def __init__(self) -> None:
        self.workflow_manager = WorkflowManager()
        self.health_checker = HealthChecker()
        
    async def start_orchestration_services(self) -> None:
        """
Start all orchestration services"""
        logger.info("Starting pipeline orchestration services")
        
        # Start background health monitoring
        asyncio.create_task(self._health_monitoring_loop())
        
        logger.info("Orchestration services started successfully")

    async def _health_monitoring_loop(self) -> None:
        """Background health monitoring loop"""
        while True:
            try:
                await self.health_checker.run_health_check_cycle()
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Health monitoring loop error: {str(e)}")
                await asyncio.sleep(60)  # Retry after 1 minute on error
