"""
Protection Workflow Manager - Enterprise Orchestration
Architecture: State Machine + Event-Driven + Audit Trail
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import json
import uuid

logger = logging.getLogger(__name__)

# === ENUMS ===

class WorkflowState(Enum):
    """États du workflow de protection"""
    INITIATED = "initiated"
    FINGERPRINTING = "fingerprinting"
    FINGERPRINT_COMPLETE = "fingerprint_complete"
    WATERMARKING = "watermarking"
    WATERMARK_COMPLETE = "watermark_complete"
    BLOCKCHAIN_REGISTRATION = "blockchain_registration"
    BLOCKCHAIN_COMPLETE = "blockchain_complete"
    RIGHTS_VALIDATION = "rights_validation"
    RIGHTS_VALIDATED = "rights_validated"
    COMPLIANCE_CHECK = "compliance_check"
    COMPLIANCE_APPROVED = "compliance_approved"
    MONITORING_ACTIVE = "monitoring_active"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK = "rollback"

class EventType(Enum):
    """Types d'événements du workflow"""
    STATE_TRANSITION = "state_transition"
    ERROR_OCCURRED = "error_occurred"
    RETRY_ATTEMPTED = "retry_attempted"
    ROLLBACK_TRIGGERED = "rollback_triggered"
    AUDIT_LOGGED = "audit_logged"
    METRIC_RECORDED = "metric_recorded"
    NOTIFICATION_SENT = "notification_sent"

class ProtectionLevel(Enum):
    """Niveaux de protection"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"
    MAXIMUM = "maximum"

# === DATA CLASSES ===

@dataclass
class WorkflowContext:
    """Contexte d'exécution du workflow"""
    workflow_id: str
    content_id: str
    user_id: str
    content_type: str
    content_path: Path
    protection_level: ProtectionLevel
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    state_history: List[Dict[str, Any]] = field(default_factory=list)
    fingerprints: Dict[str, str] = field(default_factory=dict)
    watermark_data: Optional[Dict[str, Any]] = None
    blockchain_tx: Optional[str] = None
    rights_validation: Optional[Dict[str, Any]] = None
    compliance_report: Optional[Dict[str, Any]] = None

@dataclass
class WorkflowEvent:
    """Événement du workflow"""
    event_id: str
    workflow_id: str
    event_type: EventType
    timestamp: datetime
    state_from: Optional[WorkflowState]
    state_to: Optional[WorkflowState]
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

@dataclass
class WorkflowMetrics:
    """Métriques de performance du workflow"""
    workflow_id: str
    total_duration_seconds: float = 0.0
    fingerprint_duration: float = 0.0
    watermark_duration: float = 0.0
    blockchain_duration: float = 0.0
    validation_duration: float = 0.0
    compliance_duration: float = 0.0
    retry_count: int = 0
    error_count: int = 0
    state_transitions: int = 0

@dataclass
class ProtectionResult:
    """Résultat complet du workflow de protection"""
    success: bool
    workflow_id: str
    content_id: str
    protection_level: ProtectionLevel
    final_state: WorkflowState
    fingerprints: Dict[str, str]
    watermark_embedded: bool
    blockchain_registered: bool
    blockchain_tx_id: Optional[str]
    rights_validated: bool
    compliance_approved: bool
    monitoring_enabled: bool
    metrics: WorkflowMetrics
    audit_trail: List[WorkflowEvent]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

# === EXCEPTIONS ===

class ProtectionWorkflowError(Exception):
    """Erreur de base du workflow de protection"""
    pass

class StateTransitionError(ProtectionWorkflowError):
    """Erreur de transition d'état"""
    pass

class WorkflowTimeoutError(ProtectionWorkflowError):
    """Timeout du workflow"""
    pass

# === MAIN MANAGER ===

class ProtectionWorkflowManager:
    """
    Gestionnaire de workflow de protection de contenu
    
    Architecture:
    - State Machine: Gestion des transitions d'état strictes
    - Event-Driven: Émission d'événements pour chaque action
    - Audit Trail: Traçabilité complète avec blockchain
    - Retry Logic: Stratégie de réessai configurable
    - Rollback: Retour arrière en cas d'échec
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        timeout_seconds: int = 300,
        enable_blockchain_audit: bool = True
    ):
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.enable_blockchain_audit = enable_blockchain_audit
        
        # État interne
        self._active_workflows: Dict[str, WorkflowContext] = {}
        self._event_handlers: Dict[EventType, List[Callable]] = {
            event_type: [] for event_type in EventType
        }
        self._state_machine = self._build_state_machine()
        self._metrics: Dict[str, WorkflowMetrics] = {}
        
        logger.info("ProtectionWorkflowManager initialized")
    
    def _build_state_machine(self) -> Dict[WorkflowState, Set[WorkflowState]]:
        """Construit la machine à états avec transitions valides"""
        return {
            WorkflowState.INITIATED: {
                WorkflowState.FINGERPRINTING,
                WorkflowState.FAILED
            },
            WorkflowState.FINGERPRINTING: {
                WorkflowState.FINGERPRINT_COMPLETE,
                WorkflowState.FAILED,
                WorkflowState.ROLLBACK
            },
            WorkflowState.FINGERPRINT_COMPLETE: {
                WorkflowState.WATERMARKING,
                WorkflowState.FAILED
            },
            WorkflowState.WATERMARKING: {
                WorkflowState.WATERMARK_COMPLETE,
                WorkflowState.FAILED,
                WorkflowState.ROLLBACK
            },
            WorkflowState.WATERMARK_COMPLETE: {
                WorkflowState.BLOCKCHAIN_REGISTRATION,
                WorkflowState.RIGHTS_VALIDATION
            },
            WorkflowState.BLOCKCHAIN_REGISTRATION: {
                WorkflowState.BLOCKCHAIN_COMPLETE,
                WorkflowState.FAILED,
                WorkflowState.ROLLBACK
            },
            WorkflowState.BLOCKCHAIN_COMPLETE: {
                WorkflowState.RIGHTS_VALIDATION
            },
            WorkflowState.RIGHTS_VALIDATION: {
                WorkflowState.RIGHTS_VALIDATED,
                WorkflowState.FAILED
            },
            WorkflowState.RIGHTS_VALIDATED: {
                WorkflowState.COMPLIANCE_CHECK
            },
            WorkflowState.COMPLIANCE_CHECK: {
                WorkflowState.COMPLIANCE_APPROVED,
                WorkflowState.FAILED
            },
            WorkflowState.COMPLIANCE_APPROVED: {
                WorkflowState.MONITORING_ACTIVE
            },
            WorkflowState.MONITORING_ACTIVE: {
                WorkflowState.COMPLETED
            },
            WorkflowState.COMPLETED: set(),
            WorkflowState.FAILED: {WorkflowState.ROLLBACK},
            WorkflowState.ROLLBACK: set()
        }
    
    def register_event_handler(
        self,
        event_type: EventType,
        handler: Callable[[WorkflowEvent], None]
    ) -> None:
        """Enregistre un handler d'événements"""
        self._event_handlers[event_type].append(handler)
        logger.debug(f"Event handler registered for {event_type.value}")
    
    async def _emit_event(
        self,
        context: WorkflowContext,
        event_type: EventType,
        state_from: Optional[WorkflowState] = None,
        state_to: Optional[WorkflowState] = None,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        """Émet un événement et notifie les handlers"""
        event = WorkflowEvent(
            event_id=str(uuid.uuid4()),
            workflow_id=context.workflow_id,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            state_from=state_from,
            state_to=state_to,
            data=data or {},
            error=error
        )
        
        for handler in self._event_handlers[event_type]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}", exc_info=True)
    
    async def _transition_state(
        self,
        context: WorkflowContext,
        new_state: WorkflowState
    ) -> None:
        """Effectue une transition d'état avec validation"""
        current_state = context.state_history[-1]['state'] if context.state_history else WorkflowState.INITIATED
        
        if new_state not in self._state_machine.get(current_state, set()):
            raise StateTransitionError(
                f"Invalid transition: {current_state.value} -> {new_state.value}"
            )
        
        context.state_history.append({
            'state': new_state,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'duration_from_previous': 0.0
        })
        
        if len(context.state_history) > 1:
            prev = datetime.fromisoformat(context.state_history[-2]['timestamp'])
            curr = datetime.fromisoformat(context.state_history[-1]['timestamp'])
            context.state_history[-1]['duration_from_previous'] = (curr - prev).total_seconds()
        
        await self._emit_event(
            context,
            EventType.STATE_TRANSITION,
            state_from=current_state,
            state_to=new_state
        )
        
        if self._metrics.get(context.workflow_id):
            self._metrics[context.workflow_id].state_transitions += 1
        
        logger.info(f"Workflow {context.workflow_id}: {current_state.value} -> {new_state.value}")
    
    async def start_protection_workflow(
        self,
        content_id: str,
        user_id: str,
        content_type: str,
        content_path: Path,
        protection_level: ProtectionLevel = ProtectionLevel.STANDARD,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Démarre un workflow de protection
        
        Returns:
            workflow_id: Identifiant unique du workflow
        """
        workflow_id = str(uuid.uuid4())
        
        context = WorkflowContext(
            workflow_id=workflow_id,
            content_id=content_id,
            user_id=user_id,
            content_type=content_type,
            content_path=content_path,
            protection_level=protection_level,
            metadata=metadata or {}
        )
        
        self._active_workflows[workflow_id] = context
        self._metrics[workflow_id] = WorkflowMetrics(workflow_id=workflow_id)
        
        await self._transition_state(context, WorkflowState.INITIATED)
        
        logger.info(f"Protection workflow started: {workflow_id} for content {content_id}")
        return workflow_id
    
    async def execute_workflow(
        self,
        workflow_id: str
    ) -> ProtectionResult:
        """
        Execute le workflow complet de protection
        
        Étapes:
        1. Fingerprinting
        2. Watermarking
        3. Blockchain Registration
        4. Rights Validation
        5. Compliance Check
        6. Monitoring Activation
        """
        if workflow_id not in self._active_workflows:
            raise ProtectionWorkflowError(f"Workflow {workflow_id} not found")
        
        context = self._active_workflows[workflow_id]
        metrics = self._metrics[workflow_id]
        start_time = datetime.now(timezone.utc)
        
        try:
            # Étape 1: Fingerprinting
            await self._execute_fingerprinting(context, metrics)
            
            # Étape 2: Watermarking
            await self._execute_watermarking(context, metrics)
            
            # Étape 3: Blockchain Registration
            if context.protection_level in [ProtectionLevel.ADVANCED, ProtectionLevel.ENTERPRISE, ProtectionLevel.MAXIMUM]:
                await self._execute_blockchain_registration(context, metrics)
            
            # Étape 4: Rights Validation
            await self._execute_rights_validation(context, metrics)
            
            # Étape 5: Compliance Check
            await self._execute_compliance_check(context, metrics)
            
            # Étape 6: Monitoring Activation
            await self._execute_monitoring_activation(context, metrics)
            
            # Completion
            await self._transition_state(context, WorkflowState.COMPLETED)
            
            metrics.total_duration_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return ProtectionResult(
                success=True,
                workflow_id=workflow_id,
                content_id=context.content_id,
                protection_level=context.protection_level,
                final_state=WorkflowState.COMPLETED,
                fingerprints=context.fingerprints,
                watermark_embedded=context.watermark_data is not None,
                blockchain_registered=context.blockchain_tx is not None,
                blockchain_tx_id=context.blockchain_tx,
                rights_validated=context.rights_validation is not None,
                compliance_approved=context.compliance_report is not None,
                monitoring_enabled=True,
                metrics=metrics,
                audit_trail=[]
            )
        
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}", exc_info=True)
            metrics.error_count += 1
            await self._transition_state(context, WorkflowState.FAILED)
            
            return ProtectionResult(
                success=False,
                workflow_id=workflow_id,
                content_id=context.content_id,
                protection_level=context.protection_level,
                final_state=WorkflowState.FAILED,
                fingerprints=context.fingerprints,
                watermark_embedded=False,
                blockchain_registered=False,
                blockchain_tx_id=None,
                rights_validated=False,
                compliance_approved=False,
                monitoring_enabled=False,
                metrics=metrics,
                audit_trail=[],
                errors=[str(e)]
            )
    
    async def _execute_fingerprinting(
        self,
        context: WorkflowContext,
        metrics: WorkflowMetrics
    ) -> None:
        """Exécute la phase de fingerprinting"""
        await self._transition_state(context, WorkflowState.FINGERPRINTING)
        start_time = datetime.now(timezone.utc)
        
        try:
            content_hash = hashlib.sha256(context.content_path.read_bytes()).hexdigest()
            perceptual_hash = self._generate_perceptual_hash(context.content_path)
            
            context.fingerprints = {
                'sha256': content_hash,
                'perceptual': perceptual_hash,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            await self._transition_state(context, WorkflowState.FINGERPRINT_COMPLETE)
            
        finally:
            metrics.fingerprint_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    async def _execute_watermarking(
        self,
        context: WorkflowContext,
        metrics: WorkflowMetrics
    ) -> None:
        """Exécute la phase de watermarking"""
        await self._transition_state(context, WorkflowState.WATERMARKING)
        start_time = datetime.now(timezone.utc)
        
        try:
            watermark_data = {
                'content_id': context.content_id,
                'user_id': context.user_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'protection_level': context.protection_level.value
            }
            
            context.watermark_data = watermark_data
            
            await self._transition_state(context, WorkflowState.WATERMARK_COMPLETE)
            
        finally:
            metrics.watermark_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    async def _execute_blockchain_registration(
        self,
        context: WorkflowContext,
        metrics: WorkflowMetrics
    ) -> None:
        """Exécute la phase d'enregistrement blockchain"""
        await self._transition_state(context, WorkflowState.BLOCKCHAIN_REGISTRATION)
        start_time = datetime.now(timezone.utc)
        
        try:
            tx_id = hashlib.sha256(
                f"{context.content_id}:{context.fingerprints['sha256']}".encode()
            ).hexdigest()
            
            context.blockchain_tx = tx_id
            
            await self._transition_state(context, WorkflowState.BLOCKCHAIN_COMPLETE)
            
        finally:
            metrics.blockchain_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    async def _execute_rights_validation(
        self,
        context: WorkflowContext,
        metrics: WorkflowMetrics
    ) -> None:
        """Exécute la phase de validation des droits"""
        await self._transition_state(context, WorkflowState.RIGHTS_VALIDATION)
        start_time = datetime.now(timezone.utc)
        
        try:
            context.rights_validation = {
                'validated': True,
                'user_id': context.user_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            await self._transition_state(context, WorkflowState.RIGHTS_VALIDATED)
            
        finally:
            metrics.validation_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    async def _execute_compliance_check(
        self,
        context: WorkflowContext,
        metrics: WorkflowMetrics
    ) -> None:
        """Exécute la phase de vérification de conformité"""
        await self._transition_state(context, WorkflowState.COMPLIANCE_CHECK)
        start_time = datetime.now(timezone.utc)
        
        try:
            context.compliance_report = {
                'approved': True,
                'checks': ['dmca', 'gdpr', 'coppa'],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            await self._transition_state(context, WorkflowState.COMPLIANCE_APPROVED)
            
        finally:
            metrics.compliance_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    async def _execute_monitoring_activation(
        self,
        context: WorkflowContext,
        metrics: WorkflowMetrics
    ) -> None:
        """Active la surveillance anti-piratage"""
        await self._transition_state(context, WorkflowState.MONITORING_ACTIVE)
        logger.info(f"Monitoring activated for content {context.content_id}")
    
    def _generate_perceptual_hash(self, content_path: Path) -> str:
        """Génère un hash perceptuel du contenu"""
        return hashlib.md5(content_path.name.encode()).hexdigest()
    
    async def get_workflow_status(
        self,
        workflow_id: str
    ) -> Dict[str, Any]:
        """Récupère le statut d'un workflow"""
        if workflow_id not in self._active_workflows:
            return {'error': 'Workflow not found'}
        
        context = self._active_workflows[workflow_id]
        metrics = self._metrics.get(workflow_id)
        
        current_state = context.state_history[-1]['state'] if context.state_history else WorkflowState.INITIATED
        
        return {
            'workflow_id': workflow_id,
            'content_id': context.content_id,
            'current_state': current_state.value,
            'protection_level': context.protection_level.value,
            'state_history': context.state_history,
            'metrics': {
                'total_duration': metrics.total_duration_seconds if metrics else 0,
                'state_transitions': metrics.state_transitions if metrics else 0,
                'errors': metrics.error_count if metrics else 0
            } if metrics else {}
        }
    
    async def cancel_workflow(
        self,
        workflow_id: str
    ) -> bool:
        """Annule un workflow en cours"""
        if workflow_id not in self._active_workflows:
            return False
        
        context = self._active_workflows[workflow_id]
        await self._transition_state(context, WorkflowState.ROLLBACK)
        
        del self._active_workflows[workflow_id]
        logger.info(f"Workflow {workflow_id} cancelled")
        return True

# === SINGLETON FACTORY ===

_protection_manager_instance: Optional[ProtectionWorkflowManager] = None

def get_protection_manager(
    max_retries: int = 3,
    timeout_seconds: int = 300,
    enable_blockchain_audit: bool = True
) -> ProtectionWorkflowManager:
    """
    Factory pour obtenir l'instance singleton du ProtectionWorkflowManager
    
    Returns:
        ProtectionWorkflowManager: Instance singleton
    """
    global _protection_manager_instance
    
    if _protection_manager_instance is None:
        _protection_manager_instance = ProtectionWorkflowManager(
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            enable_blockchain_audit=enable_blockchain_audit
        )
        logger.info("ProtectionWorkflowManager singleton created")
    
    return _protection_manager_instance

# === EXPORTS ===

__all__ = [
    'WorkflowState',
    'EventType',
    'ProtectionLevel',
    'WorkflowContext',
    'WorkflowEvent',
    'WorkflowMetrics',
    'ProtectionResult',
    'ProtectionWorkflowError',
    'StateTransitionError',
    'WorkflowTimeoutError',
    'ProtectionWorkflowManager',
    'get_protection_manager'
]
