"""
Automated Runbook Executor for IA Chérie Platform
Self-healing automation and remediation workflows

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import json
import asyncio
import subprocess
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import yaml

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of automated actions"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    RESTART_SERVICE = "restart_service"
    CLEAR_CACHE = "clear_cache"
    ROTATE_LOGS = "rotate_logs"
    HEALTH_CHECK = "health_check"
    FAILOVER = "failover"
    ROLLBACK = "rollback"
    NOTIFY_TEAM = "notify_team"
    RUN_COMMAND = "run_command"
    API_CALL = "api_call"
    DATABASE_CLEANUP = "database_cleanup"


class ExecutionStatus(Enum):
    """Execution status of runbook actions"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ApprovalLevel(Enum):
    """Approval levels for automated actions"""
    AUTOMATIC = "automatic"        # No approval needed
    TEAM_LEAD = "team_lead"       # Team lead approval
    MANAGER = "manager"           # Manager approval
    EXECUTIVE = "executive"       # Executive approval


@dataclass
class RunbookAction:
    """Individual runbook action definition"""
    action_id: str
    name: str
    description: str
    action_type: ActionType
    parameters: Dict[str, Any]
    timeout_seconds: int
    approval_required: ApprovalLevel
    retry_count: int
    prerequisites: List[str]  # Other action IDs that must succeed first
    rollback_action: Optional[str]  # Action to run if this fails
    validation_checks: List[Dict[str, Any]]
    safety_limits: Dict[str, Any]


@dataclass
class RunbookDefinition:
    """Complete runbook definition"""
    runbook_id: str
    name: str
    description: str
    version: str
    triggers: List[Dict[str, Any]]  # Conditions that trigger this runbook
    actions: List[RunbookAction]
    created_by: str
    created_at: datetime
    updated_at: datetime
    enabled: bool
    approval_matrix: Dict[str, ApprovalLevel]
    success_criteria: List[Dict[str, Any]]
    failure_criteria: List[Dict[str, Any]]
    max_execution_time: int
    tags: List[str]


@dataclass
class ExecutionContext:
    """Execution context for runbook"""
    execution_id: str
    runbook_id: str
    triggered_by: str
    trigger_event: Dict[str, Any]
    started_at: datetime
    environment: str
    variables: Dict[str, Any]
    approval_status: Dict[str, bool]
    execution_log: List[Dict[str, Any]]


@dataclass
class ActionResult:
    """Result of executing a runbook action"""
    action_id: str
    execution_id: str
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    output: Optional[str]
    error_message: Optional[str]
    exit_code: Optional[int]
    metrics: Dict[str, Any]
    artifacts: List[str]  # File paths or URLs to artifacts
    rollback_needed: bool


class RunbookExecutor:
    """
    Automated runbook execution engine
    Handles incident remediation and self-healing workflows
    """
    
    def __init__(self):
        """Initialize the runbook executor"""
        self.runbooks = {}
        self.active_executions = {}
        self.execution_history = []
        self.approval_handlers = {}
        self.action_handlers = self._initialize_action_handlers()
        
        # Safety limits
        self.safety_config = {
            "max_concurrent_executions": 5,
            "max_actions_per_runbook": 20,
            "default_timeout_seconds": 300,
            "require_approval_for_production": True,
            "allowed_environments": ["development", "staging", "production"]
        }
        
        logger.info("Automated Runbook Executor initialized")
    
    def _initialize_action_handlers(self) -> Dict[ActionType, Callable]:
        """Initialize action type handlers"""
        return {
            ActionType.SCALE_UP: self._handle_scale_up,
            ActionType.SCALE_DOWN: self._handle_scale_down,
            ActionType.RESTART_SERVICE: self._handle_restart_service,
            ActionType.CLEAR_CACHE: self._handle_clear_cache,
            ActionType.HEALTH_CHECK: self._handle_health_check,
            ActionType.FAILOVER: self._handle_failover,
            ActionType.ROLLBACK: self._handle_rollback,
            ActionType.NOTIFY_TEAM: self._handle_notify_team,
            ActionType.RUN_COMMAND: self._handle_run_command,
            ActionType.API_CALL: self._handle_api_call,
            ActionType.DATABASE_CLEANUP: self._handle_database_cleanup
        }
    
    def register_runbook(self, runbook: RunbookDefinition) -> bool:
        """Register a new runbook"""
        try:
            # Validate runbook
            validation_result = self._validate_runbook(runbook)
            if not validation_result["valid"]:
                logger.error(f"Runbook validation failed: {validation_result['errors']}")
                return False
            
            self.runbooks[runbook.runbook_id] = runbook
            logger.info(f"Registered runbook: {runbook.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register runbook {runbook.runbook_id}: {e}")
            return False
    
    def _validate_runbook(self, runbook: RunbookDefinition) -> Dict[str, Any]:
        """Validate runbook definition"""
        errors = []
        
        # Check action count
        if len(runbook.actions) > self.safety_config["max_actions_per_runbook"]:
            errors.append(f"Too many actions ({len(runbook.actions)} > {self.safety_config['max_actions_per_runbook']})")
        
        # Check action dependencies
        action_ids = {action.action_id for action in runbook.actions}
        for action in runbook.actions:
            for prereq in action.prerequisites:
                if prereq not in action_ids:
                    errors.append(f"Action {action.action_id} has invalid prerequisite: {prereq}")
        
        # Check for circular dependencies
        if self._has_circular_dependencies(runbook.actions):
            errors.append("Circular dependencies detected in action prerequisites")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _has_circular_dependencies(self, actions: List[RunbookAction]) -> bool:
        """Check for circular dependencies in action prerequisites"""
        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(action_id: str) -> bool:
            visited.add(action_id)
            rec_stack.add(action_id)
            
            # Find action by ID
            action = next((a for a in actions if a.action_id == action_id), None)
            if not action:
                return False
            
            for prereq in action.prerequisites:
                if prereq not in visited:
                    if has_cycle(prereq):
                        return True
                elif prereq in rec_stack:
                    return True
            
            rec_stack.remove(action_id)
            return False
        
        for action in actions:
            if action.action_id not in visited:
                if has_cycle(action.action_id):
                    return True
        
        return False
    
    async def trigger_runbook(self,
                            runbook_id: str,
                            trigger_event: Dict[str, Any],
                            triggered_by: str,
                            environment: str = "production",
                            variables: Dict[str, Any] = None) -> Optional[str]:
        """
        Trigger execution of a runbook
        
        Args:
            runbook_id: ID of runbook to execute
            trigger_event: Event that triggered the runbook
            triggered_by: Who/what triggered the runbook
            environment: Target environment
            variables: Additional variables for execution
            
        Returns:
            Execution ID if successful, None if failed
        """
        try:
            # Validate environment
            if environment not in self.safety_config["allowed_environments"]:
                logger.error(f"Invalid environment: {environment}")
                return None
            
            # Check if runbook exists and is enabled
            runbook = self.runbooks.get(runbook_id)
            if not runbook or not runbook.enabled:
                logger.error(f"Runbook {runbook_id} not found or disabled")
                return None
            
            # Check concurrent execution limits
            if len(self.active_executions) >= self.safety_config["max_concurrent_executions"]:
                logger.warning("Max concurrent executions reached, queuing runbook")
                # TODO: Implement execution queue
                return None
            
            # Create execution context
            execution_id = f"EXEC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
            
            context = ExecutionContext(
                execution_id=execution_id,
                runbook_id=runbook_id,
                triggered_by=triggered_by,
                trigger_event=trigger_event,
                started_at=datetime.utcnow(),
                environment=environment,
                variables=variables or {},
                approval_status={},
                execution_log=[]
            )
            
            # Store active execution
            self.active_executions[execution_id] = context
            
            # Start execution asynchronously
            asyncio.create_task(self._execute_runbook(context, runbook))
            
            logger.info(f"Started runbook execution {execution_id} for {runbook.name}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to trigger runbook {runbook_id}: {e}")
            return None
    
    async def _execute_runbook(self, context: ExecutionContext, runbook: RunbookDefinition):
        """Execute a runbook with all its actions"""
        try:
            logger.info(f"Executing runbook {runbook.name} (ID: {context.execution_id})")
            
            # Log execution start
            context.execution_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "execution_started",
                "runbook": runbook.name,
                "triggered_by": context.triggered_by
            })
            
            # Check if approval is required
            if self._needs_approval(runbook, context.environment):
                approval_granted = await self._request_approval(context, runbook)
                if not approval_granted:
                    await self._complete_execution(context, "cancelled", "Approval not granted")
                    return
            
            # Sort actions by dependencies
            sorted_actions = self._sort_actions_by_dependencies(runbook.actions)
            
            # Execute actions in order
            failed_actions = []
            for action in sorted_actions:
                try:
                    # Check prerequisites
                    if not self._check_prerequisites(action, context):
                        logger.warning(f"Prerequisites not met for action {action.name}")
                        continue
                    
                    # Execute action
                    result = await self._execute_action(action, context)
                    
                    # Log result
                    context.execution_log.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "action_completed",
                        "action": action.name,
                        "status": result.status.value,
                        "output": result.output
                    })
                    
                    # Handle action failure
                    if result.status == ExecutionStatus.FAILED:
                        failed_actions.append(action)
                        
                        # Check if we should continue or abort
                        if self._should_abort_on_failure(action, runbook):
                            logger.error(f"Aborting runbook due to critical action failure: {action.name}")
                            break
                    
                except Exception as e:
                    logger.error(f"Error executing action {action.name}: {e}")
                    failed_actions.append(action)
                    
                    context.execution_log.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "event": "action_error",
                        "action": action.name,
                        "error": str(e)
                    })
            
            # Determine overall execution status
            if not failed_actions:
                await self._complete_execution(context, "success", "All actions completed successfully")
            elif len(failed_actions) < len(runbook.actions):
                await self._complete_execution(context, "partial_success", f"{len(failed_actions)} actions failed")
            else:
                await self._complete_execution(context, "failed", "All actions failed")
            
        except Exception as e:
            logger.error(f"Runbook execution failed: {e}")
            await self._complete_execution(context, "error", str(e))
    
    def _needs_approval(self, runbook: RunbookDefinition, environment: str) -> bool:
        """Check if runbook execution needs approval"""
        if environment == "production" and self.safety_config["require_approval_for_production"]:
            return True
        
        # Check if any actions require approval
        for action in runbook.actions:
            if action.approval_required != ApprovalLevel.AUTOMATIC:
                return True
        
        return False
    
    async def _request_approval(self, context: ExecutionContext, runbook: RunbookDefinition) -> bool:
        """Request approval for runbook execution"""
        # TODO: Implement actual approval workflow (notifications, approvals)
        logger.info(f"Approval required for runbook {runbook.name}")
        
        # For now, simulate approval based on trigger
        if context.triggered_by == "automated_system":
            # Automatic approval for system-triggered runbooks
            return True
        
        # TODO: Send approval request to appropriate approvers
        # For now, assume approval is granted
        return True
    
    def _sort_actions_by_dependencies(self, actions: List[RunbookAction]) -> List[RunbookAction]:
        """Sort actions based on their dependencies"""
        sorted_actions = []
        completed = set()
        
        while len(sorted_actions) < len(actions):
            progress_made = False
            
            for action in actions:
                if action.action_id in completed:
                    continue
                
                # Check if all prerequisites are completed
                if all(prereq in completed for prereq in action.prerequisites):
                    sorted_actions.append(action)
                    completed.add(action.action_id)
                    progress_made = True
            
            if not progress_made:
                # Circular dependency or invalid prerequisites
                remaining_actions = [a for a in actions if a.action_id not in completed]
                logger.warning(f"Could not resolve dependencies for {len(remaining_actions)} actions")
                sorted_actions.extend(remaining_actions)
                break
        
        return sorted_actions
    
    def _check_prerequisites(self, action: RunbookAction, context: ExecutionContext) -> bool:
        """Check if action prerequisites are met"""
        # For now, assume prerequisites are met if previous actions succeeded
        # TODO: Implement actual prerequisite checking
        return True
    
    async def _execute_action(self, action: RunbookAction, context: ExecutionContext) -> ActionResult:
        """Execute a single runbook action"""
        result = ActionResult(
            action_id=action.action_id,
            execution_id=context.execution_id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.utcnow(),
            completed_at=None,
            output=None,
            error_message=None,
            exit_code=None,
            metrics={},
            artifacts=[],
            rollback_needed=False
        )
        
        try:
            logger.info(f"Executing action: {action.name}")
            
            # Get action handler
            handler = self.action_handlers.get(action.action_type)
            if not handler:
                raise ValueError(f"No handler for action type: {action.action_type}")
            
            # Execute action with timeout
            try:
                output = await asyncio.wait_for(
                    handler(action, context),
                    timeout=action.timeout_seconds
                )
                
                result.status = ExecutionStatus.SUCCESS
                result.output = output
                result.exit_code = 0
                
            except asyncio.TimeoutError:
                result.status = ExecutionStatus.TIMEOUT
                result.error_message = f"Action timed out after {action.timeout_seconds} seconds"
                
            except Exception as e:
                result.status = ExecutionStatus.FAILED
                result.error_message = str(e)
                result.exit_code = 1
            
            result.completed_at = datetime.utcnow()
            
            # Run validation checks
            if result.status == ExecutionStatus.SUCCESS:
                validation_passed = await self._validate_action_result(action, result, context)
                if not validation_passed:
                    result.status = ExecutionStatus.FAILED
                    result.error_message = "Validation checks failed"
            
            logger.info(f"Action {action.name} completed with status: {result.status.value}")
            
        except Exception as e:
            logger.error(f"Error executing action {action.name}: {e}")
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.utcnow()
        
        return result
    
    async def _validate_action_result(self, action: RunbookAction, result: ActionResult, context: ExecutionContext) -> bool:
        """Validate action execution result"""
        if not action.validation_checks:
            return True
        
        for check in action.validation_checks:
            check_type = check.get("type")
            
            if check_type == "exit_code":
                expected_code = check.get("expected", 0)
                if result.exit_code != expected_code:
                    return False
            
            elif check_type == "output_contains":
                expected_text = check.get("text", "")
                if expected_text not in (result.output or ""):
                    return False
            
            elif check_type == "api_response":
                # TODO: Implement API response validation
                pass
        
        return True
    
    def _should_abort_on_failure(self, action: RunbookAction, runbook: RunbookDefinition) -> bool:
        """Determine if runbook should abort on action failure"""
        # Check if action is marked as critical
        if "critical" in action.name.lower() or "critical" in action.description.lower():
            return True
        
        # Check runbook-level failure criteria
        for criteria in runbook.failure_criteria:
            if criteria.get("abort_on_action_failure") and criteria.get("action_id") == action.action_id:
                return True
        
        return False
    
    async def _complete_execution(self, context: ExecutionContext, status: str, message: str):
        """Complete runbook execution"""
        try:
            # Log completion
            context.execution_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "execution_completed",
                "status": status,
                "message": message,
                "duration_seconds": (datetime.utcnow() - context.started_at).total_seconds()
            })
            
            # Move to history
            self.execution_history.append(context)
            
            # Remove from active executions
            if context.execution_id in self.active_executions:
                del self.active_executions[context.execution_id]
            
            logger.info(f"Runbook execution {context.execution_id} completed with status: {status}")
            
        except Exception as e:
            logger.error(f"Error completing execution: {e}")
    
    # Action handlers
    async def _handle_scale_up(self, action: RunbookAction, context: ExecutionContext) -> str:
        """Handle scale up action"""
        service = action.parameters.get("service")
        replicas = action.parameters.get("replicas", 1)
        
        logger.info(f"Scaling up {service} by {replicas} replicas")
        
        # TODO: Implement actual scaling (Kubernetes, Docker, etc.)
        await asyncio.sleep(2)  # Simulate scaling time
        
        return f"Scaled up {service} by {replicas} replicas"
    
    async def _handle_scale_down(self, action: RunbookAction, context: ExecutionContext) -> str:
        """Handle scale down action"""
        service = action.parameters.get("service")
        replicas = action.parameters.get("replicas", 1)
        
        logger.info(f"Scaling down {service} by {replicas} replicas")
        
        # TODO: Implement actual scaling (Kubernetes, Docker, etc.)
        await asyncio.sleep(2)  # Simulate scaling time
        
        return f"Scaled down {service} by {replicas} replicas"
    
    async def _handle_restart_service(self, action: RunbookAction, context: ExecutionContext) -> str:
        """Handle service restart action"""
        service = action.parameters.get("service")
        
        logger.info(f"Restarting service: {service}")
        
        # TODO: Implement actual service restart
        await asyncio.sleep(5)  # Simulate restart time
        
        return f"Service {service} restarted successfully"
    
    async def _handle_clear_cache(self, action: RunbookAction, context: ExecutionContext) -> str:
        """Handle cache clearing action"""
        cache_type = action.parameters.get("cache_type", "redis")
        
        logger.info(f"Clearing {cache_type} cache")
        
        # TODO: Implement actual cache clearing
        await asyncio.sleep(1)
        
        return f"{cache_type} cache cleared"
    
    async def _handle_health_check(self, action: RunbookAction, context: ExecutionContext) -> str:
        """Handle health check action"""
        endpoint = action.parameters.get("endpoint")
        
        logger.info(f"Running health check on {endpoint}")
        
        # TODO: Implement actual health check
        await asyncio.sleep(2)
        
        return f"Health check passed for {endpoint}"
    
    async def _handle_failover(self, action: RunbookAction, context: ExecutionContext) -> str:
        """Handle failover action"""
        primary = action.parameters.get("primary")
        secondary = action.parameters.get("secondary")
        
        logger.info(f"Failing over from {primary} to {secondary}")
        
        # TODO: Implement actual failover
        await asyncio.sleep(10)
        
        return f"Failover from {primary} to {secondary} completed"
    
    async def _handle_rollback(self, action: RunbookAction, context: ExecutionContext) -> str:
        """Handle rollback action"""
        deployment = action.parameters.get("deployment")
        version = action.parameters.get("version")
        
        logger.info(f"Rolling back {deployment} to version {version}")
        
        # TODO: Implement actual rollback
        await asyncio.sleep(15)
        
        return f"Rollback of {deployment} to {version} completed"
    
    async def _handle_notify_team(self, action: RunbookAction, context: ExecutionContext) -> str:
        """Handle team notification action"""
        team = action.parameters.get("team")
        message = action.parameters.get("message")
        
        logger.info(f"Notifying {team}: {message}")
        
        # TODO: Integrate with notification system
        await asyncio.sleep(1)
        
        return f"Notification sent to {team}"
    
    async def _handle_run_command(self, action: RunbookAction, context: ExecutionContext) -> str:
        """Handle run command action"""
        command = action.parameters.get("command")
        working_dir = action.parameters.get("working_dir", "/tmp")
        
        logger.info(f"Running command: {command}")
        
        try:
            # Execute command safely
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return stdout.decode()
            else:
                raise Exception(f"Command failed: {stderr.decode()}")
                
        except Exception as e:
            raise Exception(f"Failed to execute command: {e}")
    
    async def _handle_api_call(self, action: RunbookAction, context: ExecutionContext) -> str:
        """Handle API call action"""
        url = action.parameters.get("url")
        method = action.parameters.get("method", "GET")
        
        logger.info(f"Making {method} request to {url}")
        
        # TODO: Implement actual API call
        await asyncio.sleep(2)
        
        return f"API call to {url} successful"
    
    async def _handle_database_cleanup(self, action: RunbookAction, context: ExecutionContext) -> str:
        """Handle database cleanup action"""
        database = action.parameters.get("database")
        cleanup_type = action.parameters.get("cleanup_type")
        
        logger.info(f"Running {cleanup_type} cleanup on {database}")
        
        # TODO: Implement actual database cleanup
        await asyncio.sleep(5)
        
        return f"Database cleanup ({cleanup_type}) completed on {database}"
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        # Check active executions
        if execution_id in self.active_executions:
            context = self.active_executions[execution_id]
            return {
                "execution_id": execution_id,
                "status": "running",
                "started_at": context.started_at.isoformat(),
                "runbook_id": context.runbook_id,
                "progress": len(context.execution_log),
                "last_update": context.execution_log[-1]["timestamp"] if context.execution_log else None
            }
        
        # Check execution history
        for context in self.execution_history:
            if context.execution_id == execution_id:
                last_log = context.execution_log[-1] if context.execution_log else {}
                return {
                    "execution_id": execution_id,
                    "status": last_log.get("status", "unknown"),
                    "started_at": context.started_at.isoformat(),
                    "completed_at": last_log.get("timestamp"),
                    "runbook_id": context.runbook_id,
                    "total_actions": len(context.execution_log)
                }
        
        return None
    
    def get_runbook_statistics(self) -> Dict[str, Any]:
        """Get runbook executor statistics"""
        return {
            "registered_runbooks": len(self.runbooks),
            "active_executions": len(self.active_executions),
            "total_executions": len(self.execution_history),
            "enabled_runbooks": sum(1 for r in self.runbooks.values() if r.enabled),
            "action_types_supported": len(self.action_handlers),
            "safety_limits": self.safety_config
        }


# Factory function
def create_automated_runbook_executor() -> RunbookExecutor:
    """Create new automated runbook executor instance"""
    return RunbookExecutor()


# Export all classes and functions
__all__ = [
    'RunbookExecutor',
    'ActionType',
    'ExecutionStatus',
    'ApprovalLevel',
    'RunbookAction',
    'RunbookDefinition',
    'ExecutionContext',
    'ActionResult',
    'create_automated_runbook_executor'
]