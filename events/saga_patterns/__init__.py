"""
  Init   module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""Saga Patterns Module - Enterprise Distributed Transaction Management
import asyncio

======================================================================

Complete saga patterns implementation for Ainflue platform providing
enterprise-grade distributed transaction management, orchestration,
choreography, compensation, and monitoring capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Core saga orchestration components
try:
    from .saga_orchestration_engine import (
        SagaOrchestrationEngine,
        SagaStatus,
        SagaStepStatus,
        SagaResult,
        SagaStepResult,
        SagaStep,
        ContentProcessingSaga,
        get_saga_orchestration_engine,
        start_content_processing_saga
    )
except ImportError as e:
    logger.warning(f"Saga orchestration engine not fully available: {e}")
    # Create placeholder classes
    class SagaOrchestrationEngine: pass
    class SagaStatus: pass
    class SagaStepStatus: pass
    class SagaResult: pass
    class SagaStepResult: pass
    class SagaStep: pass
    class ContentProcessingSaga: pass
    def get_saga_orchestration_engine() -> None: return None
    def start_content_processing_saga() -> None: return None

# Choreography coordination components
try:
    from .choreography_coordination_manager import (
        ChoreographyCoordinationManager,
        DomainEvent,
        EventBus,
        CorrelationService,
        ContentProcessingChoreography,
        CollaborationWorkflowChoreography,
        ChoreographyStatus,
        get_choreography_coordination_manager,
        trigger_content_processing_choreography,
        trigger_collaboration_choreography
    )
except ImportError as e:
    logger.warning(f"Choreography coordination manager not fully available: {e}")
    class ChoreographyCoordinationManager: pass
    class DomainEvent: pass
    class EventBus: pass
    class CorrelationService: pass
    class ContentProcessingChoreography: pass
    class CollaborationWorkflowChoreography: pass
    class ChoreographyStatus: pass
    def get_choreography_coordination_manager() -> None: return None
    def trigger_content_processing_choreography() -> None: return None
    def trigger_collaboration_choreography() -> None: return None

# Rollback execution engine
try:
    from .rollback_execution_engine import (
        RollbackExecutionEngine,
        RollbackExecution,
        RollbackStatus,
        get_rollback_execution_engine
    )
except ImportError as e:
    logger.warning(f"Rollback execution engine not fully available: {e}")
    class RollbackExecutionEngine: pass
    class RollbackExecution: pass
    class RollbackStatus: pass
    def get_rollback_execution_engine() -> None: return None

# Saga monitoring analytics
try:
    from .saga_monitoring_analytics import (
        SagaMonitoringAnalytics,
        SagaMetric,
        PerformanceMetrics,
        get_saga_monitoring_analytics,
        record_saga_started,
        record_saga_completed
    )
except ImportError as e:
    logger.warning(f"Saga monitoring analytics not fully available: {e}")
    class SagaMonitoringAnalytics: pass
    class SagaMetric: pass
    class PerformanceMetrics: pass
    def get_saga_monitoring_analytics() -> None: return None
    def record_saga_started() -> None: return None
    def record_saga_completed() -> None: return None

# Error recovery orchestrator
try:
    from .error_recovery_orchestrator import (
        ErrorRecoveryOrchestrator,
        ErrorContext,
        RecoveryPlan,
        RecoveryExecution,
        RecoveryStrategy,
        ErrorSeverity,
        get_error_recovery_orchestrator,
        handle_saga_error
    )
except ImportError as e:
    logger.warning(f"Error recovery orchestrator not fully available: {e}")
    class ErrorRecoveryOrchestrator: pass
    class ErrorContext: pass
    class RecoveryPlan: pass
    class RecoveryExecution: pass
    class RecoveryStrategy: pass
    class ErrorSeverity: pass
    def get_error_recovery_orchestrator() -> None: return None
    def handle_saga_error() -> None: return None

# Saga visualization dashboard
try:
    from .saga_visualization_dashboard import (
        SagaVisualizationDashboard,
        VisualizationData,
        VisualizationNode,
        VisualizationEdge,
        VisualizationType,
        get_saga_visualization_dashboard,
        create_saga_flow_viz,
        create_metrics_viz
    )
except ImportError as e:
    logger.warning(f"Saga visualization dashboard not fully available: {e}")
    class SagaVisualizationDashboard: pass
    class VisualizationData: pass
    class VisualizationNode: pass
    class VisualizationEdge: pass
    class VisualizationType: pass
    def get_saga_visualization_dashboard() -> None: return None
    def create_saga_flow_viz() -> None: return None
    def create_metrics_viz() -> None: return None


# High-level convenience functions for common saga operations
async def create_content_processing_saga(creator_id: str, content_data: Dict[str, Any]) -> str:
    """Create and start a content processing saga"""
    try:
        return await start_content_processing_saga(creator_id, content_data)
    except Exception as e:
        logger.error(f"Failed to create content processing saga: {e}")
        return None


class SagaManager:
    """High-level saga management interface"""
    
    def __init__(self) -> None:
        self.orchestrator = get_saga_orchestration_engine()
        self.choreography_manager = get_choreography_coordination_manager()
        self.monitoring_analytics = get_saga_monitoring_analytics()
        self.error_recovery = get_error_recovery_orchestrator()
        self.visualization_dashboard = get_saga_visualization_dashboard()
    
    async def start_saga(
        self,
        saga_type: str,
        saga_data: Dict[str, Any],
        orchestration_mode: str = "orchestrated"
    ) -> str:
        """Start new saga with specified mode"""
        try:
            if orchestration_mode == "orchestrated" and self.orchestrator:
                return await self.orchestrator.start_saga(saga_type, saga_data)
            elif orchestration_mode == "choreographed" and self.choreography_manager:
                # For choreography, trigger through events
                if saga_type == "content_processing":
                    return await trigger_content_processing_choreography(
                        saga_data.get("creator_id"), saga_data.get("content_id")
                    )
            return None
        except Exception as e:
            logger.error(f"Failed to start saga: {e}")
            return None
    
    async def get_comprehensive_status(self, saga_id: str) -> Dict[str, Any]:
        """Get comprehensive status from all saga components"""
        status = {
            "saga_id": saga_id,
            "orchestration": None,
            "choreography": None,
            "monitoring": None
        }
        
        try:
            if self.orchestrator:
                status["orchestration"] = await self.orchestrator.get_saga_status(saga_id)
            
            if self.choreography_manager:
                # Try to find choreography by saga_id (approximation)
                active_choreographies = await self.choreography_manager.list_active_choreographies()
                for choreo in active_choreographies:
                    if saga_id in choreo.get("correlation_id", ""):
                        status["choreography"] = choreo
                        break
            
        except Exception as e:
            logger.error(f"Error getting comprehensive status: {e}")
        
        return status


# Global saga manager instance
_saga_manager: Optional[SagaManager] = None


def get_saga_manager() -> SagaManager:
    """Get global saga manager instance"""
    global _saga_manager
    if _saga_manager is None:
        _saga_manager = SagaManager()
    
    return _saga_manager


# Export all public API components
__all__ = [
    # Core saga orchestration
    "SagaOrchestrationEngine", "SagaStatus", "SagaStepStatus", "SagaResult", "SagaStepResult",
    "SagaStep", "ContentProcessingSaga", "get_saga_orchestration_engine", "start_content_processing_saga",
    
    # Choreography coordination
    "ChoreographyCoordinationManager", "DomainEvent", "EventBus", "CorrelationService",
    "ContentProcessingChoreography", "CollaborationWorkflowChoreography", "ChoreographyStatus",
    "get_choreography_coordination_manager", "trigger_content_processing_choreography", "trigger_collaboration_choreography",
    
    # Rollback execution
    "RollbackExecutionEngine", "RollbackExecution", "RollbackStatus", "get_rollback_execution_engine",
    
    # Monitoring analytics
    "SagaMonitoringAnalytics", "SagaMetric", "PerformanceMetrics", "get_saga_monitoring_analytics",
    "record_saga_started", "record_saga_completed",
    
    # Error recovery
    "ErrorRecoveryOrchestrator", "ErrorContext", "RecoveryPlan", "RecoveryExecution",
    "RecoveryStrategy", "ErrorSeverity", "get_error_recovery_orchestrator", "handle_saga_error",
    
    # Visualization
    "SagaVisualizationDashboard", "VisualizationData", "VisualizationNode", "VisualizationEdge",
    "VisualizationType", "get_saga_visualization_dashboard", "create_saga_flow_viz", "create_metrics_viz",
    
    # High-level interfaces
    "SagaManager", "get_saga_manager", "create_content_processing_saga"
]