"""IA Influencer Agent - License Workflow Engine
==========================================

Moteur de workflow avancé pour l'orchestration des processus de licensing.
Gère les flux automatisés, les approbations et les transitions d'état.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2024-2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LEGAL STRICT ⚠️
Ce code et tous les concepts associés sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants s'exposent à des poursuites judiciaires.

Contact autorisé: mlaiel@live.de
"""

from typing import Dict, Any, List, Optional, Callable
import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """États du workflow de licensing."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"


class WorkflowAction(Enum):
    """Actions possibles dans le workflow."""

    SUBMIT = "submit"
    REVIEW = "review"
    APPROVE = "approve"
    REJECT = "reject"
    ACTIVATE = "activate"
    SUSPEND = "suspend"
    TERMINATE = "terminate"
    RENEW = "renew"
    MODIFY = "modify"
    ESCALATE = "escalate"


class WorkflowTrigger(Enum):
    """Déclencheurs de workflow."""

    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    CONDITION_BASED = "condition_based"


class LicenseWorkflowEngine:
    """
    Moteur de workflow avancé pour l'IA Influencer Agent.
    
    Orchestre tous les processus de licensing avec des règles métier
    sophistiquées et une gestion d'état robuste.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le moteur de workflow.
        
        Args:
            config: Configuration du moteur
        """
        self.config = config or {}
        self.workflows = {}
        self.state_transitions = {}
        self.workflow_rules = {}
        self.automation_rules = {}
        self.active_workflows = {}
        self.is_initialized = False
        
        logger.info("LicenseWorkflowEngine initialized")
    
    async def initialize(self):
        """Initialise le moteur de workflow."""
        try:
            await self._setup_state_transitions()
            await self._setup_workflow_rules()
            await self._setup_automation_rules()
            await self._start_background_tasks()
            self.is_initialized = True
            logger.info("Workflow engine successfully initialized")
        except Exception as e:
            logger.error(f"Failed to initialize workflow engine: {str(e)}")
            raise
    
    async def _setup_state_transitions(self):
        """Configure les transitions d'état autorisées."""
        self.state_transitions = {
            WorkflowState.DRAFT: [
                WorkflowState.PENDING_REVIEW,
                WorkflowState.REJECTED
            ],
            WorkflowState.PENDING_REVIEW: [
                WorkflowState.UNDER_REVIEW,
                WorkflowState.DRAFT,
                WorkflowState.REJECTED
            ],
            WorkflowState.UNDER_REVIEW: [
                WorkflowState.PENDING_APPROVAL,
                WorkflowState.REJECTED,
                WorkflowState.DRAFT
            ],
            WorkflowState.PENDING_APPROVAL: [
                WorkflowState.APPROVED,
                WorkflowState.REJECTED,
                WorkflowState.UNDER_REVIEW
            ],
            WorkflowState.APPROVED: [
                WorkflowState.ACTIVE,
                WorkflowState.REJECTED
            ],
            WorkflowState.ACTIVE: [
                WorkflowState.SUSPENDED,
                WorkflowState.TERMINATED,
                WorkflowState.EXPIRED,
                WorkflowState.RENEWED
            ],
            WorkflowState.SUSPENDED: [
                WorkflowState.ACTIVE,
                WorkflowState.TERMINATED
            ],
            WorkflowState.EXPIRED: [
                WorkflowState.RENEWED,
                WorkflowState.TERMINATED
            ],
            WorkflowState.RENEWED: [
                WorkflowState.ACTIVE,
                WorkflowState.PENDING_APPROVAL
            ]
        }
    
    async def _setup_workflow_rules(self):
        """
Configure les règles métier du workflow."""
        self.workflow_rules = {
            "review_requirements": {
                "high_value_threshold": 1000.0,
                "exclusive_license_review": True,
                "international_territory_review": True,
                "sensitive_content_review": True,
                "new_creator_review": True
            },
            "approval_requirements": {
                "legal_approval_threshold": 5000.0,
                "executive_approval_threshold": 10000.0,
                "board_approval_threshold": 50000.0,
                "compliance_check_required": True,
                "financial_verification_required": True
            },
            "automation_triggers": {
                "auto_approve_threshold": 100.0,
                "auto_reject_conditions": [
                    "copyright_violation",
                    "adult_content_policy_violation",
                    "incomplete_documentation"
                ],
                "escalation_conditions": [
                    "extended_review_time",
                    "multiple_rejections",
                    "high_value_deal"
                ]
            },
            "notification_rules": {
                "creator_notifications": True,
                "licensee_notifications": True,
                "admin_notifications": True,
                "escalation_notifications": True
            }
        }
    
    async def _setup_automation_rules(self):
        """Configure les règles d'automatisation."""
        self.automation_rules = {
            "auto_transitions": {
                WorkflowState.DRAFT: {
                    "condition": "complete_documentation",
                    "target_state": WorkflowState.PENDING_REVIEW,
                    "delay": 0
                },
                WorkflowState.PENDING_REVIEW: {
                    "condition": "low_value_and_verified",
                    "target_state": WorkflowState.APPROVED,
                    "delay": 300  # 5 minutes
                },
                WorkflowState.APPROVED: {
                    "condition": "payment_confirmed",
                    "target_state": WorkflowState.ACTIVE,
                    "delay": 0
                },
                WorkflowState.ACTIVE: {
                    "condition": "expiry_date_reached",
                    "target_state": WorkflowState.EXPIRED,
                    "delay": 0
                }
            },
            "scheduled_tasks": {
                "expiry_check": {
                    "frequency": "daily",
                    "time": "00:00",
                    "action": "check_license_expiry"
                },
                "renewal_reminder": {
                    "frequency": "daily",
                    "time": "09:00",
                    "action": "send_renewal_reminders"
                },
                "compliance_audit": {
                    "frequency": "weekly",
                    "day": "monday",
                    "time": "08:00",
                    "action": "perform_compliance_audit"
                }
            }
        }
    
    async def _start_background_tasks(self):
        """Démarre les tâches de fond."""
        asyncio.create_task(self._workflow_monitor())
        asyncio.create_task(self._automation_processor())
        asyncio.create_task(self._scheduled_task_runner())
    
    async def create_workflow(self, license_id: str, 
                            workflow_type: str = "standard",
                            metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Crée un nouveau workflow de licensing.
        
        Args:
            license_id: ID de la licence
            workflow_type: Type de workflow
            metadata: Métadonnées du workflow
            
        Returns:
            Dict contenant les détails du workflow
        """
        workflow_id = f"WF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{license_id[:8]}"
        
        workflow = {
            "workflow_id": workflow_id,
            "license_id": license_id,
            "workflow_type": workflow_type,
            "current_state": WorkflowState.DRAFT,
            "previous_state": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "history": [],
            "pending_actions": [],
            "assignee": None,
            "priority": "normal",
            "sla_deadline": None,
            "escalation_level": 0
        }
        
        self.active_workflows[workflow_id] = workflow
        
        # Enregistrement de l'événement
        await self._add_workflow_event(workflow_id, WorkflowAction.SUBMIT, 
                                     "Workflow created", None)
        
        # Vérification des règles d'automatisation
        await self._check_automation_rules(workflow_id)
        
        logger.info(f"Workflow {workflow_id} created for license {license_id}")
        return workflow
    
    async def transition_state(self, workflow_id: str, 
                             target_state: WorkflowState,
                             action: WorkflowAction,
                             actor_id: str,
                             comment: str = None) -> bool:
        """
        Effectue une transition d'état dans le workflow.
        
        Args:
            workflow_id: ID du workflow
            target_state: État cible
            action: Action effectuée
            actor_id: ID de l'acteur
            comment: Commentaire optionnel
            
        Returns:
            bool: True si transition réussie
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found")
            return False
        
        current_state = WorkflowState(workflow["current_state"])
        
        # Vérification de la transition autorisée
        if not await self._is_transition_allowed(current_state, target_state):
            logger.error(f"Transition from {current_state.value} to {target_state.value} not allowed")
            return False
        
        # Vérification des permissions
        if not await self._check_actor_permissions(workflow_id, actor_id, action):
            logger.error(f"Actor {actor_id} does not have permission for action {action.value}")
            return False
        
        # Exécution de la transition
        workflow["previous_state"] = workflow["current_state"]
        workflow["current_state"] = target_state.value
        workflow["updated_at"] = datetime.utcnow().isoformat()
        
        # Enregistrement de l'événement
        await self._add_workflow_event(workflow_id, action, comment, actor_id)
        
        # Exécution des hooks post-transition
        await self._execute_post_transition_hooks(workflow_id, target_state, action)
        
        # Vérification des règles d'automatisation
        await self._check_automation_rules(workflow_id)
        
        logger.info(f"Workflow {workflow_id} transitioned to {target_state.value}")
        return True
    
    async def _is_transition_allowed(self, current_state: WorkflowState, 
                                   target_state: WorkflowState) -> bool:
        """
        Vérifie si une transition d'état est autorisée.
        
        Args:
            current_state: État actuel
            target_state: État cible
            
        Returns:
            bool: True si autorisée
        """
        allowed_transitions = self.state_transitions.get(current_state, [])
        return target_state in allowed_transitions
    
    async def _check_actor_permissions(self, workflow_id: str, 
                                     actor_id: str, 
                                     action: WorkflowAction) -> bool:
        """
        Vérifie les permissions d'un acteur pour une action.
        
        Args:
            workflow_id: ID du workflow
            actor_id: ID de l'acteur
            action: Action à effectuer
            
        Returns:
            bool: True si autorisé
        """
        # Ici on intégrerait un système de permissions réel
        # Pour l'instant, autorisons tout
        return True
    
    async def _add_workflow_event(self, workflow_id: str, 
                                action: WorkflowAction,
                                comment: str = None,
                                actor_id: str = None):
        """
        Ajoute un événement à l'historique du workflow.
        
        Args:
            workflow_id: ID du workflow
            action: Action effectuée
            comment: Commentaire
            actor_id: ID de l'acteur
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action.value,
            "actor_id": actor_id,
            "comment": comment,
            "state_before": workflow.get("previous_state"),
            "state_after": workflow["current_state"]
        }
        
        workflow["history"].append(event)
    
    async def _execute_post_transition_hooks(self, workflow_id: str,
                                           new_state: WorkflowState,
                                           action: WorkflowAction):
        """
        Exécute les hooks post-transition.
        
        Args:
            workflow_id: ID du workflow
            new_state: Nouvel état
            action: Action effectuée
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        
        # Notifications
        await self._send_notifications(workflow_id, new_state, action)
        
        # Mise à jour des SLA
        await self._update_sla_deadlines(workflow_id, new_state)
        
        # Actions spécifiques par état
        if new_state == WorkflowState.ACTIVE:
            await self._activate_license(workflow["license_id"])
        elif new_state == WorkflowState.EXPIRED:
            await self._handle_license_expiry(workflow["license_id"])
        elif new_state == WorkflowState.TERMINATED:
            await self._terminate_license(workflow["license_id"])
    
    async def _send_notifications(self, workflow_id: str,
                                new_state: WorkflowState,
                                action: WorkflowAction):
        """
        Envoie les notifications appropriées.
        
        Args:
            workflow_id: ID du workflow
            new_state: Nouvel état
            action: Action effectuée
        """
        # Ici on intégrerait un système de notifications réel
        logger.info(f"Notification sent for workflow {workflow_id}: {new_state.value}")
    
    async def _update_sla_deadlines(self, workflow_id: str, 
                                  new_state: WorkflowState):
        """
        Met à jour les délais SLA.
        
        Args:
            workflow_id: ID du workflow
            new_state: Nouvel état
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        
        # Définition des SLA par état
        sla_hours = {
            WorkflowState.PENDING_REVIEW: 24,
            WorkflowState.UNDER_REVIEW: 72,
            WorkflowState.PENDING_APPROVAL: 48,
            WorkflowState.APPROVED: 2
        }
        
        if new_state in sla_hours:
            deadline = datetime.utcnow() + timedelta(hours=sla_hours[new_state])
            workflow["sla_deadline"] = deadline.isoformat()
    
    async def _activate_license(self, license_id: str):
        """
        Active une licence.
        
        Args:
            license_id: ID de la licence
        """
        logger.info(f"License {license_id} activated")
        # Ici on intégrerait l'activation réelle de la licence
    
    async def _handle_license_expiry(self, license_id: str):
        """
        Gère l'expiration d'une licence.
        
        Args:
            license_id: ID de la licence
        """
        logger.info(f"License {license_id} expired")
        # Ici on intégrerait la gestion de l'expiration
    
    async def _terminate_license(self, license_id: str):
        """
        Termine une licence.
        
        Args:
            license_id: ID de la licence
        """
        logger.info(f"License {license_id} terminated")
        # Ici on intégrerait la terminaison réelle
    
    async def _check_automation_rules(self, workflow_id: str):
        """
        Vérifie et applique les règles d'automatisation.
        
        Args:
            workflow_id: ID du workflow
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        
        current_state = WorkflowState(workflow["current_state"])
        
        # Vérification des transitions automatiques
        auto_rule = self.automation_rules["auto_transitions"].get(current_state)
        if auto_rule:
            condition_met = await self._evaluate_condition(workflow_id, auto_rule["condition"])
            if condition_met:
                target_state = WorkflowState(auto_rule["target_state"])
                delay = auto_rule.get("delay", 0)
                
                if delay > 0:
                    # Programmer la transition
                    asyncio.create_task(
                        self._delayed_transition(workflow_id, target_state, delay)
                    )
                else:
                    # Transition immédiate
                    await self.transition_state(
                        workflow_id, target_state, WorkflowAction.AUTOMATIC, "system"
                    )
    
    async def _evaluate_condition(self, workflow_id: str, condition: str) -> bool:
        """
        Évalue une condition d'automatisation.
        
        Args:
            workflow_id: ID du workflow
            condition: Condition à évaluer
            
        Returns:
            bool: True si condition remplie
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return False
        
        # Ici on implémenterait l'évaluation réelle des conditions
        # Pour l'instant, retournons False pour éviter les transitions automatiques
        return False
    
    async def _delayed_transition(self, workflow_id: str, 
                                target_state: WorkflowState, 
                                delay_seconds: int):
        """
        Effectue une transition retardée.
        
        Args:
            workflow_id: ID du workflow
            target_state: État cible
            delay_seconds: Délai en secondes
        """
        await asyncio.sleep(delay_seconds)
        await self.transition_state(
            workflow_id, target_state, WorkflowAction.AUTOMATIC, "system"
        )
    
    async def _workflow_monitor(self):
        """Tâche de surveillance des workflows."""
        while True:
            try:
                await self._check_sla_violations()
                await self._check_stale_workflows()
                await asyncio.sleep(300)  # Vérification toutes les 5 minutes
            except Exception as e:
                logger.error(f"Error in workflow monitor: {str(e)}")
                await asyncio.sleep(60)
    
    async def _automation_processor(self):
        """Processeur d'automatisation."""
        while True:
            try:
                await self._process_automation_queue()
                await asyncio.sleep(60)  # Traitement chaque minute
            except Exception as e:
                logger.error(f"Error in automation processor: {str(e)}")
                await asyncio.sleep(60)
    
    async def _scheduled_task_runner(self):
        """Exécuteur de tâches programmées."""
        while True:
            try:
                await self._run_scheduled_tasks()
                await asyncio.sleep(3600)  # Vérification chaque heure
            except Exception as e:
                logger.error(f"Error in scheduled task runner: {str(e)}")
                await asyncio.sleep(300)
    
    async def _check_sla_violations(self):
        """Vérifie les violations de SLA."""
        current_time = datetime.utcnow()
        
        for workflow_id, workflow in self.active_workflows.items():
            sla_deadline = workflow.get("sla_deadline")
            if sla_deadline:
                deadline = datetime.fromisoformat(sla_deadline.replace('Z', '+00:00'))
                if current_time > deadline:
                    await self._handle_sla_violation(workflow_id)
    
    async def _handle_sla_violation(self, workflow_id: str):
        """
        Gère une violation de SLA.
        
        Args:
            workflow_id: ID du workflow
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        
        workflow["escalation_level"] += 1
        workflow["updated_at"] = datetime.utcnow().isoformat()
        
        # Enregistrement de l'escalade
        await self._add_workflow_event(
            workflow_id, WorkflowAction.ESCALATE, 
            f"SLA violation - escalation level {workflow['escalation_level']}", 
            "system"
        )
        
        logger.warning(f"SLA violation for workflow {workflow_id}")
    
    async def _check_stale_workflows(self):
        """Vérifie les workflows stagnants."""
        cutoff_time = datetime.utcnow() - timedelta(days=30)
        
        stale_workflows = []
        for workflow_id, workflow in self.active_workflows.items():
            updated_at = datetime.fromisoformat(workflow["updated_at"].replace('Z', '+00:00'))
            if updated_at < cutoff_time:
                stale_workflows.append(workflow_id)
        
        for workflow_id in stale_workflows:
            logger.warning(f"Stale workflow detected: {workflow_id}")
            # Ici on pourrait ajouter une logique de nettoyage
    
    async def _process_automation_queue(self):
        """Traite la queue d'automatisation."""
        # Ici on traiterait les tâches d'automatisation en attente
        logger.debug('Method executed')
        return True
    
    async def _run_scheduled_tasks(self):
        """
Exécute les tâches programmées."""
        current_time = datetime.utcnow()
        
        for task_name, task_config in self.automation_rules["scheduled_tasks"].items():
            # Ici on vérifierait si c'est le moment d'exécuter la tâche
            # et on l'exécuterait si nécessaire
            logger.debug('Method executed')
            return True
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère le statut d'un workflow.
        
        Args:
            workflow_id: ID du workflow
            
        Returns:
            Dict contenant le statut ou None
        """
        workflow = self.active_workflows.get(workflow_id)
        if workflow:
            return {
                **workflow,
                "is_sla_violated": await self._check_workflow_sla(workflow_id),
                "next_possible_actions": await self._get_next_actions(workflow_id)
            }
        return None
    
    async def _check_workflow_sla(self, workflow_id: str) -> bool:
        """
        Vérifie si le SLA d'un workflow est violé.
        
        Args:
            workflow_id: ID du workflow
            
        Returns:
            bool: True si SLA violé
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow or not workflow.get("sla_deadline"):
            return False
        
        deadline = datetime.fromisoformat(workflow["sla_deadline"].replace('Z', '+00:00'))
        return datetime.utcnow() > deadline
    
    async def _get_next_actions(self, workflow_id: str) -> List[str]:
        """
        Récupère les actions possibles pour un workflow.
        
        Args:
            workflow_id: ID du workflow
            
        Returns:
            Liste des actions possibles
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return []
        
        current_state = WorkflowState(workflow["current_state"])
        possible_transitions = self.state_transitions.get(current_state, [])
        
        return [state.value for state in possible_transitions]
