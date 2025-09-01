"""Comprehensive exception handling for workflow management system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Optional, Dict, Any, List
from enum import Enum


class WorkflowErrorCode(Enum):
    """
Standardized workflow error codes."""
    # General workflow errors (1000-1099)
    WORKFLOW_INITIALIZATION_FAILED = "WF1000"
    WORKFLOW_EXECUTION_FAILED = "WF1001"
    WORKFLOW_TIMEOUT = "WF1002"
    WORKFLOW_CANCELLED = "WF1003"
    WORKFLOW_NOT_FOUND = "WF1004"
    WORKFLOW_INVALID_STATE = "WF1005"
    
    # Pipeline errors (1100-1199)
    PIPELINE_CREATION_FAILED = "WF1100"
    PIPELINE_STEP_FAILED = "WF1101"
    PIPELINE_DEPENDENCY_ERROR = "WF1102"
    PIPELINE_DEADLOCK = "WF1103"
    PIPELINE_RESOURCE_EXHAUSTED = "WF1104"
    PIPELINE_VALIDATION_ERROR = "WF1105"
    
    # Scheduling errors (1200-1299)
    SCHEDULE_INVALID_CRON = "WF1200"
    SCHEDULE_TASK_NOT_FOUND = "WF1201"
    SCHEDULE_EXECUTION_FAILED = "WF1202"
    SCHEDULE_CONFLICT = "WF1203"
    SCHEDULE_RESOURCE_BUSY = "WF1204"
    
    # State management errors (1300-1399)
    STATE_CORRUPTION = "WF1300"
    STATE_LOCK_TIMEOUT = "WF1301"
    STATE_SERIALIZATION_ERROR = "WF1302"
    STATE_PERSISTENCE_FAILED = "WF1303"
    STATE_RECOVERY_FAILED = "WF1304"
    
    # Automation errors (1400-1499)
    AUTOMATION_TRIGGER_FAILED = "WF1400"
    AUTOMATION_ACTION_FAILED = "WF1401"
    AUTOMATION_CONDITION_ERROR = "WF1402"
    AUTOMATION_RULE_CONFLICT = "WF1403"
    
    # Resource errors (1500-1599)
    RESOURCE_NOT_AVAILABLE = "WF1500"
    RESOURCE_ACCESS_DENIED = "WF1501"
    RESOURCE_QUOTA_EXCEEDED = "WF1502"
    RESOURCE_TIMEOUT = "WF1503"


class WorkflowException(Exception):
    """Base exception for all workflow-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: WorkflowErrorCode = None,
        workflow_id: str = None,
        context: Dict[str, Any] = None,
        cause: Exception = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.workflow_id = workflow_id
        self.context = context or {}
        self.cause = cause
        self.timestamp = None
        
    def to_dict(self) -> Dict[str, Any]:
        """
Convert exception to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code.value if self.error_code else None,
            "workflow_id": self.workflow_id,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __str__(self) -> str:
        components = [self.message]
        
        if self.error_code:
            components.append(f"Code: {self.error_code.value}")
        
        if self.workflow_id:
            components.append(f"Workflow: {self.workflow_id}")
        
        return " | ".join(components)


class PipelineException(WorkflowException):
    """Exception for pipeline-specific errors."""
    
    def __init__(
        self,
        message: str,
        error_code: WorkflowErrorCode = None,
        pipeline_id: str = None,
        step_name: str = None,
        step_error: str = None,
        **kwargs
    ):
        super().__init__(message, error_code, **kwargs)
        self.pipeline_id = pipeline_id
        self.step_name = step_name
        self.step_error = step_error
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "pipeline_id": self.pipeline_id,
            "step_name": self.step_name,
            "step_error": self.step_error
        })
        return result


class PipelineStepException(PipelineException):
    """Exception for individual pipeline step failures."""
    
    def __init__(
        self,
        message: str,
        step_name: str,
        retry_attempt: int = 0,
        max_retries: int = 3,
        **kwargs
    ):
        super().__init__(message, step_name=step_name, **kwargs)
        self.retry_attempt = retry_attempt
        self.max_retries = max_retries
        self.is_retryable = retry_attempt < max_retries
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "retry_attempt": self.retry_attempt,
            "max_retries": self.max_retries,
            "is_retryable": self.is_retryable
        })
        return result


class PipelineDependencyException(PipelineException):
    """Exception for pipeline dependency resolution errors."""
    
    def __init__(
        self,
        message: str,
        circular_dependencies: List[str] = None,
        missing_dependencies: List[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code=WorkflowErrorCode.PIPELINE_DEPENDENCY_ERROR, **kwargs)
        self.circular_dependencies = circular_dependencies or []
        self.missing_dependencies = missing_dependencies or []
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "circular_dependencies": self.circular_dependencies,
            "missing_dependencies": self.missing_dependencies
        })
        return result


class SchedulingException(WorkflowException):
    """Exception for scheduling-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: WorkflowErrorCode = None,
        task_id: str = None,
        schedule_expression: str = None,
        **kwargs
    ):
        super().__init__(message, error_code, **kwargs)
        self.task_id = task_id
        self.schedule_expression = schedule_expression
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "task_id": self.task_id,
            "schedule_expression": self.schedule_expression
        })
        return result


class ScheduleCronException(SchedulingException):
    """Exception for invalid cron expressions."""
    
    def __init__(self, message: str, cron_expression: str, **kwargs):
        super().__init__(
            message, 
            error_code=WorkflowErrorCode.SCHEDULE_INVALID_CRON,
            schedule_expression=cron_expression,
            **kwargs
        )
        self.cron_expression = cron_expression


class ScheduleConflictException(SchedulingException):
    """
Exception for scheduling conflicts."""
    
    def __init__(
        self,
        message: str,
        conflicting_tasks: List[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code=WorkflowErrorCode.SCHEDULE_CONFLICT, **kwargs)
        self.conflicting_tasks = conflicting_tasks or []
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "conflicting_tasks": self.conflicting_tasks
        })
        return result


class StateException(WorkflowException):
    """Exception for workflow state management errors."""
    
    def __init__(
        self,
        message: str,
        error_code: WorkflowErrorCode = None,
        state_id: str = None,
        state_version: int = None,
        **kwargs
    ):
        super().__init__(message, error_code, **kwargs)
        self.state_id = state_id
        self.state_version = state_version
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "state_id": self.state_id,
            "state_version": self.state_version
        })
        return result


class StateLockException(StateException):
    """Exception for state locking errors."""
    
    def __init__(
        self,
        message: str,
        lock_holder: str = None,
        lock_timeout: float = None,
        **kwargs
    ):
        super().__init__(message, error_code=WorkflowErrorCode.STATE_LOCK_TIMEOUT, **kwargs)
        self.lock_holder = lock_holder
        self.lock_timeout = lock_timeout
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "lock_holder": self.lock_holder,
            "lock_timeout": self.lock_timeout
        })
        return result


class StateCorruptionException(StateException):
    """Exception for corrupted workflow state."""
    
    def __init__(
        self,
        message: str,
        corruption_details: Dict[str, Any] = None,
        recovery_possible: bool = False,
        **kwargs
    ):
        super().__init__(message, error_code=WorkflowErrorCode.STATE_CORRUPTION, **kwargs)
        self.corruption_details = corruption_details or {}
        self.recovery_possible = recovery_possible
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "corruption_details": self.corruption_details,
            "recovery_possible": self.recovery_possible
        })
        return result


class AutomationException(WorkflowException):
    """Exception for automation-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: WorkflowErrorCode = None,
        automation_rule_id: str = None,
        trigger_data: Dict[str, Any] = None,
        **kwargs
    ):
        super().__init__(message, error_code, **kwargs)
        self.automation_rule_id = automation_rule_id
        self.trigger_data = trigger_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "automation_rule_id": self.automation_rule_id,
            "trigger_data": self.trigger_data
        })
        return result


class AutomationTriggerException(AutomationException):
    """Exception for automation trigger failures."""
    
    def __init__(
        self,
        message: str,
        trigger_type: str = None,
        trigger_conditions: List[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code=WorkflowErrorCode.AUTOMATION_TRIGGER_FAILED, **kwargs)
        self.trigger_type = trigger_type
        self.trigger_conditions = trigger_conditions or []
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "trigger_type": self.trigger_type,
            "trigger_conditions": self.trigger_conditions
        })
        return result


class ResourceException(WorkflowException):
    """Exception for resource-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: WorkflowErrorCode = None,
        resource_type: str = None,
        resource_id: str = None,
        **kwargs
    ):
        super().__init__(message, error_code, **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "resource_type": self.resource_type,
            "resource_id": self.resource_id
        })
        return result


class ResourceQuotaException(ResourceException):
    """Exception for resource quota exceeded errors."""
    
    def __init__(
        self,
        message: str,
        current_usage: int = None,
        quota_limit: int = None,
        **kwargs
    ):
        super().__init__(message, error_code=WorkflowErrorCode.RESOURCE_QUOTA_EXCEEDED, **kwargs)
        self.current_usage = current_usage
        self.quota_limit = quota_limit
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "current_usage": self.current_usage,
            "quota_limit": self.quota_limit
        })
        return result


# Exception utilities

def create_workflow_exception(
    error_type: str,
    message: str,
    **kwargs
) -> WorkflowException:
    """Factory function to create appropriate workflow exception."""
    exception_classes = {
        "workflow": WorkflowException,
        "pipeline": PipelineException,
        "pipeline_step": PipelineStepException,
        "pipeline_dependency": PipelineDependencyException,
        "scheduling": SchedulingException,
        "schedule_cron": ScheduleCronException,
        "schedule_conflict": ScheduleConflictException,
        "state": StateException,
        "state_lock": StateLockException,
        "state_corruption": StateCorruptionException,
        "automation": AutomationException,
        "automation_trigger": AutomationTriggerException,
        "resource": ResourceException,
        "resource_quota": ResourceQuotaException
    }
    
    exception_class = exception_classes.get(error_type, WorkflowException)
    return exception_class(message, **kwargs)


def handle_workflow_exception(
    exception: WorkflowException,
    logger=None,
    metrics_collector=None
):
    """Standard exception handler for workflow exceptions."""
    if logger:
        logger.error(
            f"Workflow exception occurred: {exception}",
            extra=exception.to_dict()
        )
    
    if metrics_collector:
        metrics_collector.increment(
            "workflow.exceptions",
            tags={
                "error_code": exception.error_code.value if exception.error_code else "unknown",
                "exception_type": exception.__class__.__name__
            }
        )
    
    # Could add additional handling like notifications, alerts, etc.
    return exception.to_dict()


def is_retryable_exception(exception: Exception) -> bool:
    """Determine if an exception is retryable."""
    if isinstance(exception, PipelineStepException):
        return exception.is_retryable
    
    retryable_codes = [
        WorkflowErrorCode.WORKFLOW_TIMEOUT,
        WorkflowErrorCode.RESOURCE_NOT_AVAILABLE,
        WorkflowErrorCode.RESOURCE_TIMEOUT,
        WorkflowErrorCode.STATE_LOCK_TIMEOUT,
        WorkflowErrorCode.SCHEDULE_RESOURCE_BUSY
    ]
    
    if isinstance(exception, WorkflowException) and exception.error_code:
        return exception.error_code in retryable_codes
    
    return False


def extract_error_context(exception: Exception) -> Dict[str, Any]:
    """
Extract context information from any exception for debugging."""
    context = {
        "exception_type": exception.__class__.__name__,
        "message": str(exception),
        "cause": str(exception.__cause__) if exception.__cause__ else None
    }
    
    if isinstance(exception, WorkflowException):
        context.update(exception.to_dict())
    
    return context
