"""Integration Workflows Module - Advanced integration orchestration for Ainflue Platform.

This module provides comprehensive integration workflow orchestration including API integration,
data synchronization, platform connectors, and microservice coordination for seamless
multi-platform content creator operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
from dataclasses import dataclass
import asyncio

# Core Integration Workflow Classes
from .api_integration_workflow import APIIntegrationWorkflow, APIMetrics, IntegrationResult
from .data_synchronization_workflow import DataSynchronizationWorkflow, SyncMetrics, SynchronizationReport
from .platform_connector_workflow import PlatformConnectorWorkflow, ConnectorMetrics, ConnectionStatus
from .webhook_management_workflow import WebhookManagementWorkflow, WebhookMetrics, WebhookStatus
from .third_party_service_workflow import ThirdPartyServiceWorkflow, ServiceMetrics, ServiceIntegration
from .microservice_coordination_workflow import MicroserviceCoordinationWorkflow, CoordinationMetrics, ServiceMesh
from .database_integration_workflow import DatabaseIntegrationWorkflow, DatabaseMetrics, IntegrationHealth
from .cache_synchronization_workflow import CacheSynchronizationWorkflow, CacheMetrics, SyncStatus
from .event_streaming_workflow import EventStreamingWorkflow, StreamingMetrics, EventFlow
from .batch_processing_workflow import BatchProcessingWorkflow, BatchMetrics, ProcessingResults
from .real_time_sync_workflow import RealTimeSyncWorkflow, RealTimeMetrics, SyncResults
from .migration_workflow import MigrationWorkflow, MigrationMetrics, MigrationPlan
from .health_check_workflow import HealthCheckWorkflow, HealthMetrics, SystemStatus


class IntegrationWorkflowType(Enum):
    """Integration workflow types for comprehensive system integration."""
    API_INTEGRATION = "api_integration"
    DATA_SYNCHRONIZATION = "data_synchronization"
    PLATFORM_CONNECTOR = "platform_connector"
    WEBHOOK_MANAGEMENT = "webhook_management"
    THIRD_PARTY_SERVICE = "third_party_service"
    MICROSERVICE_COORDINATION = "microservice_coordination"
    DATABASE_INTEGRATION = "database_integration"
    CACHE_SYNCHRONIZATION = "cache_synchronization"
    EVENT_STREAMING = "event_streaming"
    BATCH_PROCESSING = "batch_processing"
    REAL_TIME_SYNC = "real_time_sync"
    MIGRATION = "migration"
    HEALTH_CHECK = "health_check"


@dataclass
class IntegrationConfig:
    """Configuration for integration workflows."""
    sync_interval: int = 300  # 5 minutes
    retry_attempts: int = 3
    timeout_seconds: int = 30
    health_check_enabled: bool = True
    real_time_sync_enabled: bool = True
    batch_processing_enabled: bool = True


class IntegrationOrchestrator:
    """
    Master orchestrator for all integration workflows.
    
    Provides unified interface for managing and coordinating all integration
    workflows including API connectivity, data synchronization, platform integration,
    and microservice coordination.
    """
    
    def __init__(self, config: IntegrationConfig = None):
        """Initialize integration orchestrator with configuration."""
        self.config = config or IntegrationConfig()
        self.workflows = {}
        self._initialize_workflows()
    
    def _initialize_workflows(self):
        """Initialize all integration workflow instances."""
        self.workflows = {
            IntegrationWorkflowType.API_INTEGRATION: APIIntegrationWorkflow(),
            IntegrationWorkflowType.DATA_SYNCHRONIZATION: DataSynchronizationWorkflow(),
            IntegrationWorkflowType.PLATFORM_CONNECTOR: PlatformConnectorWorkflow(),
            IntegrationWorkflowType.WEBHOOK_MANAGEMENT: WebhookManagementWorkflow(),
            IntegrationWorkflowType.THIRD_PARTY_SERVICE: ThirdPartyServiceWorkflow(),
            IntegrationWorkflowType.MICROSERVICE_COORDINATION: MicroserviceCoordinationWorkflow(),
            IntegrationWorkflowType.DATABASE_INTEGRATION: DatabaseIntegrationWorkflow(),
            IntegrationWorkflowType.CACHE_SYNCHRONIZATION: CacheSynchronizationWorkflow(),
            IntegrationWorkflowType.EVENT_STREAMING: EventStreamingWorkflow(),
            IntegrationWorkflowType.BATCH_PROCESSING: BatchProcessingWorkflow(),
            IntegrationWorkflowType.REAL_TIME_SYNC: RealTimeSyncWorkflow(),
            IntegrationWorkflowType.MIGRATION: MigrationWorkflow(),
            IntegrationWorkflowType.HEALTH_CHECK: HealthCheckWorkflow()
        }
    
    async def execute_integration(
        self, 
        workflow_type: IntegrationWorkflowType,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute specific integration workflow with parameters."""
        
        if workflow_type not in self.workflows:
            raise ValueError(f"Unknown integration workflow type: {workflow_type}")
        
        workflow = self.workflows[workflow_type]
        
        # Execute workflow based on type
        if workflow_type == IntegrationWorkflowType.API_INTEGRATION:
            return await workflow.integrate_api(**parameters)
        elif workflow_type == IntegrationWorkflowType.DATA_SYNCHRONIZATION:
            return await workflow.synchronize_data(**parameters)
        elif workflow_type == IntegrationWorkflowType.PLATFORM_CONNECTOR:
            return await workflow.connect_platform(**parameters)
        # Add more workflow executions as needed
        
        return {"status": "executed", "workflow": workflow_type.value}
    
    async def run_comprehensive_integration(
        self, 
        user_id: str,
        integration_scope: List[IntegrationWorkflowType] = None
    ) -> Dict[str, Any]:
        """Run comprehensive integration across multiple workflows."""
        
        if integration_scope is None:
            integration_scope = list(IntegrationWorkflowType)
        
        results = {}
        
        # Execute all specified integration workflows
        for workflow_type in integration_scope:
            try:
                workflow = self.workflows[workflow_type]
                if hasattr(workflow, 'get_user_analytics'):
                    results[workflow_type.value] = await workflow.get_user_analytics(user_id, 30)
            except Exception as e:
                results[workflow_type.value] = {"error": str(e)}
        
        return {
            "user_id": user_id,
            "integration_scope": [wf.value for wf in integration_scope],
            "integration_results": results,
            "overall_integration_health": await self._calculate_overall_integration_health(results),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _calculate_overall_integration_health(self, results: Dict[str, Any]) -> float:
        """Calculate overall integration health from individual results."""
        
        health_scores = []
        for workflow_result in results.values():
            if isinstance(workflow_result, dict) and "integration_health" in workflow_result:
                health_scores.append(workflow_result["integration_health"])
        
        return sum(health_scores) / len(health_scores) if health_scores else 0.0
    
    def get_workflow(self, workflow_type: IntegrationWorkflowType):
        """Get specific integration workflow instance."""
        return self.workflows.get(workflow_type)


# Workflow factory function
def create_integration_workflow(workflow_type: IntegrationWorkflowType):
    """Factory function to create specific integration workflow."""
    workflow_classes = {
        IntegrationWorkflowType.API_INTEGRATION: APIIntegrationWorkflow,
        IntegrationWorkflowType.DATA_SYNCHRONIZATION: DataSynchronizationWorkflow,
        IntegrationWorkflowType.PLATFORM_CONNECTOR: PlatformConnectorWorkflow,
        IntegrationWorkflowType.WEBHOOK_MANAGEMENT: WebhookManagementWorkflow,
        IntegrationWorkflowType.THIRD_PARTY_SERVICE: ThirdPartyServiceWorkflow,
        IntegrationWorkflowType.MICROSERVICE_COORDINATION: MicroserviceCoordinationWorkflow,
        IntegrationWorkflowType.DATABASE_INTEGRATION: DatabaseIntegrationWorkflow,
        IntegrationWorkflowType.CACHE_SYNCHRONIZATION: CacheSynchronizationWorkflow,
        IntegrationWorkflowType.EVENT_STREAMING: EventStreamingWorkflow,
        IntegrationWorkflowType.BATCH_PROCESSING: BatchProcessingWorkflow,
        IntegrationWorkflowType.REAL_TIME_SYNC: RealTimeSyncWorkflow,
        IntegrationWorkflowType.MIGRATION: MigrationWorkflow,
        IntegrationWorkflowType.HEALTH_CHECK: HealthCheckWorkflow
    }
    
    workflow_class = workflow_classes.get(workflow_type)
    if not workflow_class:
        raise ValueError(f"Unknown integration workflow type: {workflow_type}")
    
    return workflow_class()


# Export main classes and functions
__all__ = [
    # Core orchestrator
    'IntegrationOrchestrator',
    'IntegrationConfig',
    'IntegrationWorkflowType',
    
    # Workflow classes
    'APIIntegrationWorkflow',
    'DataSynchronizationWorkflow',
    'PlatformConnectorWorkflow',
    'WebhookManagementWorkflow',
    'ThirdPartyServiceWorkflow',
    'MicroserviceCoordinationWorkflow',
    'DatabaseIntegrationWorkflow',
    'CacheSynchronizationWorkflow',
    'EventStreamingWorkflow',
    'BatchProcessingWorkflow',
    'RealTimeSyncWorkflow',
    'MigrationWorkflow',
    'HealthCheckWorkflow',
    
    # Data classes
    'APIMetrics',
    'SyncMetrics',
    'ConnectorMetrics',
    'WebhookMetrics',
    'ServiceMetrics',
    'CoordinationMetrics',
    'DatabaseMetrics',
    'CacheMetrics',
    'StreamingMetrics',
    'BatchMetrics',
    'RealTimeMetrics',
    'MigrationMetrics',
    'HealthMetrics',
    
    # Factory function
    'create_integration_workflow'
]


# Module metadata
__version__ = "3.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Advanced Integration Workflows for Ainflue Creator Platform"