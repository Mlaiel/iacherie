"""IA-Influencer-Agent - Event Workflow Orchestration System
Module: backend/core/events/event_workflows.py
Architecture: Advanced Business Process Orchestration via Events
Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
INTERDIT : Copie, reproduction, modification, ou usage sans autorisation écrite explicite.
Toute violation sera poursuivie selon la loi allemande et française.
Contact autorisations : mlaiel@live.de

Description:
    Système d'orchestration de workflows complexes basé sur les événements.
    Gère les processus métier de la plateforme IA-Influencer-Agent :
    - Workflow upload → processing → protection → monétisation
    - Orchestration collaboration et matching
    - Gestion des processus de takedown et revenus
"""

from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import json
import logging
import uuid
from collections import defaultdict

from .event_bus import Event, EventBus, EventPriority, EventStatus
from .event_types import EventType, ContentEvent, ProtectionEvent, MonetizationEvent, CollaborationEvent, SystemEvent

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """
Statut d'un workflow"""

    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"  # En attente d'événement
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class StepStatus(Enum):
    """Statut d'une étape de workflow"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class StepType(Enum):
    """Types d'étapes de workflow"""

    ACTION = "action"  # Exécution d'une action
    WAIT_EVENT = "wait_event"  # Attente d'un événement
    CONDITION = "condition"  # Vérification de condition
    PARALLEL = "parallel"  # Exécution parallèle
    CHOICE = "choice"  # Choix conditionnel
    LOOP = "loop"  # Boucle conditionnelle
    TIMEOUT = "timeout"  # Gestion de timeout


@dataclass
class WorkflowVariable:
    """Variable de workflow"""
    name: str
    value: Any
    var_type: str = "string"  # string, number, boolean, object, array
    description: str = ""
    required: bool = False


@dataclass
class WorkflowStep:
    """Étape de workflow"""
    step_id: str
    name: str
    step_type: StepType
    config: Dict[str, Any] = field(default_factory=dict)
    conditions: List[str] = field(default_factory=list)
    timeout: Optional[timedelta] = None
    retry_count: int = 0
    max_retries: int = 3
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output: Dict[str, Any] = field(default_factory=dict)
    next_steps: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "step_type": self.step_type.value,
            "config": self.config,
            "conditions": self.conditions,
            "timeout": self.timeout.total_seconds() if self.timeout else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "output": self.output,
            "next_steps": self.next_steps
        }


@dataclass
class WorkflowInstance:
    """Instance d'exécution de workflow"""
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    variables: Dict[str, WorkflowVariable] = field(default_factory=dict)
    current_step: Optional[str] = None
    steps: Dict[str, WorkflowStep] = field(default_factory=dict)
    events_consumed: List[str] = field(default_factory=list)  # Event IDs
    events_produced: List[str] = field(default_factory=list)  # Event IDs
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "variables": {k: {"name": v.name, "value": v.value, "type": v.var_type} for k, v in self.variables.items()},
            "current_step": self.current_step,
            "steps": {k: v.to_dict() for k, v in self.steps.items()},
            "events_consumed": self.events_consumed,
            "events_produced": self.events_produced,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata
        }


class WorkflowDefinition:
    """Définition d'un workflow"""
    
    def __init__(
        self,
        workflow_id: str,
        name: str,
        description: str,
        version: str = "1.0.0"
    ):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.version = version
        self.steps: Dict[str, WorkflowStep] = {}
        self.start_step: Optional[str] = None
        self.end_steps: Set[str] = set()
        self.variables: Dict[str, WorkflowVariable] = {}
        self.triggers: List[str] = []  # Event types qui déclenchent le workflow
        self.timeout: Optional[timedelta] = None
        self.enabled: bool = True
        
    def add_step(self, step: WorkflowStep) -> "WorkflowDefinition":
        """Ajoute une étape au workflow"""
        self.steps[step.step_id] = step
        return self
    
    def set_start_step(self, step_id: str) -> "WorkflowDefinition":
        """Définit l'étape de démarrage"""
        self.start_step = step_id
        return self
    
    def add_end_step(self, step_id: str) -> "WorkflowDefinition":
        """Ajoute une étape de fin"""
        self.end_steps.add(step_id)
        return self
    
    def add_variable(self, variable: WorkflowVariable) -> "WorkflowDefinition":
        """Ajoute une variable"""
        self.variables[variable.name] = variable
        return self
    
    def add_trigger(self, event_type: str) -> "WorkflowDefinition":
        """Ajoute un déclencheur d'événement"""
        self.triggers.append(event_type)
        return self
    
    def validate(self) -> List[str]:
        """
Valide la définition du workflow"""
        errors = []
        
        if not self.start_step:
            errors.append("No start step defined")
        elif self.start_step not in self.steps:
            errors.append(f"Start step '{self.start_step}' not found in steps")
        
        if not self.end_steps:
            errors.append("No end steps defined")
        
        for step_id in self.end_steps:
            if step_id not in self.steps:
                errors.append(f"End step '{step_id}' not found in steps")
        
        # Validation des liens entre étapes
        for step in self.steps.values():
            for next_step in step.next_steps:
                if next_step not in self.steps:
                    errors.append(f"Step '{step.step_id}' references unknown next step '{next_step}'")
        
        return errors


class WorkflowStepExecutor(ABC):
    """Interface pour l'exécution d'étapes de workflow"""
    
    @abstractmethod
    async def execute(
        self,
        step: WorkflowStep,
        instance: WorkflowInstance,
        context: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Exécute une étape
        
        Returns:
            (success, output_data)
        """
        pass


class ActionStepExecutor(WorkflowStepExecutor):
    """
Exécuteur pour les étapes d'action"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.actions: Dict[str, Callable] = {}
    
    def register_action(self, action_name: str, handler: Callable):
        """
Enregistre une action"""
        self.actions[action_name] = handler
    
    async def execute(
        self,
        step: WorkflowStep,
        instance: WorkflowInstance,
        context: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
Exécute une action"""
        action_name = step.config.get("action")
        if not action_name:
            return False, {"error": "No action specified"}
        
        if action_name not in self.actions:
            return False, {"error": f"Unknown action: {action_name}"}
        
        try:
            # Préparation des paramètres
            params = step.config.get("params", {})
            
            # Substitution des variables
            resolved_params = self._resolve_variables(params, instance, context)
            
            # Exécution de l'action
            handler = self.actions[action_name]
            if asyncio.iscoroutinefunction(handler):
                result = await handler(resolved_params, instance, context)
            else:
                result = handler(resolved_params, instance, context)
            
            return True, {"result": result}
            
        except Exception as e:
            logger.error("Action execution failed: %s", e)
            return False, {"error": str(e)}
    
    def _resolve_variables(
        self,
        params: Dict[str, Any],
        instance: WorkflowInstance,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Résout les variables dans les paramètres"""
        resolved = {}
        
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                var_name = value[2:-1]
                if var_name in instance.variables:
                    resolved[key] = instance.variables[var_name].value
                elif var_name in context:
                    resolved[key] = context[var_name]
                else:
                    resolved[key] = value  # Keep original if not found
            else:
                resolved[key] = value
        
        return resolved


class WaitEventStepExecutor(WorkflowStepExecutor):
    """Exécuteur pour les étapes d'attente d'événement"""
    
    async def execute(
        self,
        step: WorkflowStep,
        instance: WorkflowInstance,
        context: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
Configure l'attente d'événement"""
        event_type = step.config.get("event_type")
        if not event_type:
            return False, {"error": "No event type specified"}
        
        # L'étape est marquée comme en attente
        # Le WorkflowEngine gère l'attente réelle
        return True, {
            "waiting_for": event_type,
            "filters": step.config.get("filters", {}),
            "timeout": step.timeout.total_seconds() if step.timeout else None
        }


class ConditionStepExecutor(WorkflowStepExecutor):
    """Exécuteur pour les étapes de condition"""
    
    async def execute(
        self,
        step: WorkflowStep,
        instance: WorkflowInstance,
        context: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Évalue une condition"""
        condition = step.config.get("condition")
        if not condition:
            return False, {"error": "No condition specified"}
        
        try:
            # Évaluation simple de conditions
            result = self._evaluate_condition(condition, instance, context)
            return True, {"condition_result": result}
            
        except Exception as e:
            logger.error("Condition evaluation failed: %s", e)
            return False, {"error": str(e)}
    
    def _evaluate_condition(
        self,
        condition: str,
        instance: WorkflowInstance,
        context: Dict[str, Any]
    ) -> bool:
        """Évalue une condition simple"""
        # Implémentation basique - peut être étendue
        # Supporte des conditions comme: "${variable} == 'value'", "${count} > 5"
        
        # Substitution des variables
        resolved_condition = condition
        for var_name, var in instance.variables.items():
            resolved_condition = resolved_condition.replace(
                f"${{{var_name}}}", str(var.value)
            )
        
        # Évaluation sécurisée (basique)
        try:
            return eval(resolved_condition)
        except:
            return False


class WorkflowEngine:
    """Moteur d'exécution de workflows"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.definitions: Dict[str, WorkflowDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.waiting_instances: Dict[str, List[str]] = defaultdict(list)  # event_type -> instance_ids
        
        # Exécuteurs d'étapes
        self.executors: Dict[StepType, WorkflowStepExecutor] = {
            StepType.ACTION: ActionStepExecutor(event_bus),
            StepType.WAIT_EVENT: WaitEventStepExecutor(),
            StepType.CONDITION: ConditionStepExecutor()
        }
        
        # Statistiques
        self.stats = {
            "workflows_started": 0,
            "workflows_completed": 0,
            "workflows_failed": 0,
            "steps_executed": 0
        }
        
        # Abonnement aux événements
        self.event_bus.subscribe("*", self._handle_event)
        
        logger.info("WorkflowEngine initialized")
    
    def register_workflow(self, definition: WorkflowDefinition) -> bool:
        """Enregistre une définition de workflow"""
        errors = definition.validate()
        if errors:
            logger.error("Workflow validation failed: %s", errors)
            return False
        
        self.definitions[definition.workflow_id] = definition
        logger.info("Workflow registered: %s", definition.workflow_id)
        return True
    
    def register_action(self, action_name: str, handler: Callable):
        """Enregistre une action pour les étapes ACTION"""
        if StepType.ACTION in self.executors:
            self.executors[StepType.ACTION].register_action(action_name, handler)
    
    async def start_workflow(
        self,
        workflow_id: str,
        variables: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """
Démarre une instance de workflow"""
        if workflow_id not in self.definitions:
            logger.error("Unknown workflow: %s", workflow_id)
            return None
        
        definition = self.definitions[workflow_id]
        if not definition.enabled:
            logger.warning("Workflow %s is disabled", workflow_id)
            return None
        
        # Création de l'instance
        instance = WorkflowInstance(
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            user_id=user_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            started_at=datetime.now(timezone.utc)
        )
        
        # Initialisation des variables
        for var_name, var_def in definition.variables.items():
            value = variables.get(var_name) if variables else None
            if value is None and var_def.required:
                logger.error("Required variable %s not provided", var_name)
                return None
            
            instance.variables[var_name] = WorkflowVariable(
                name=var_name,
                value=value if value is not None else getattr(var_def, 'default_value', None),
                var_type=var_def.var_type,
                description=var_def.description,
                required=var_def.required
            )
        
        # Copie des étapes depuis la définition
        for step_id, step_def in definition.steps.items():
            instance.steps[step_id] = WorkflowStep(
                step_id=step_def.step_id,
                name=step_def.name,
                step_type=step_def.step_type,
                config=step_def.config.copy(),
                conditions=step_def.conditions.copy(),
                timeout=step_def.timeout,
                max_retries=step_def.max_retries,
                next_steps=step_def.next_steps.copy()
            )
        
        self.instances[instance.instance_id] = instance
        self.stats["workflows_started"] += 1
        
        # Démarrage de l'exécution
        asyncio.create_task(self._execute_workflow(instance, definition.start_step))
        
        logger.info("Workflow instance started: %s (workflow: %s)", 
                   instance.instance_id, workflow_id)
        return instance.instance_id
    
    async def _execute_workflow(self, instance: WorkflowInstance, step_id: str):
        """Exécute un workflow à partir d'une étape"""
        try:
            while step_id and instance.status == WorkflowStatus.RUNNING:
                step = instance.steps.get(step_id)
                if not step:
                    logger.error("Step %s not found in instance %s", step_id, instance.instance_id)
                    break
                
                # Exécution de l'étape
                success, next_step = await self._execute_step(instance, step)
                
                if not success:
                    instance.status = WorkflowStatus.FAILED
                    break
                
                if next_step == "WAIT":
                    # L'étape attend un événement
                    instance.status = WorkflowStatus.WAITING
                    break
                elif next_step == "END":
                    # Workflow terminé
                    instance.status = WorkflowStatus.COMPLETED
                    instance.completed_at = datetime.now(timezone.utc)
                    self.stats["workflows_completed"] += 1
                    break
                else:
                    step_id = next_step
            
        except Exception as e:
            logger.error("Workflow execution failed: %s", e)
            instance.status = WorkflowStatus.FAILED
            self.stats["workflows_failed"] += 1
    
    async def _execute_step(
        self,
        instance: WorkflowInstance,
        step: WorkflowStep
    ) -> Tuple[bool, Optional[str]]:
        """Exécute une étape de workflow"""
        logger.debug("Executing step %s in instance %s", step.step_id, instance.instance_id)
        
        step.status = StepStatus.RUNNING
        step.started_at = datetime.now(timezone.utc)
        instance.current_step = step.step_id
        
        # Vérification des conditions
        if step.conditions and not self._check_conditions(step.conditions, instance):
            step.status = StepStatus.SKIPPED
            step.completed_at = datetime.now(timezone.utc)
            return True, self._get_next_step(step)
        
        try:
            # Exécution selon le type d'étape
            executor = self.executors.get(step.step_type)
            if not executor:
                raise ValueError(f"No executor for step type {step.step_type}")
            
            success, output = await executor.execute(step, instance, {})
            step.output = output
            
            if success:
                step.status = StepStatus.COMPLETED
                step.completed_at = datetime.now(timezone.utc)
                self.stats["steps_executed"] += 1
                
                # Gestion spéciale pour l'attente d'événements
                if step.step_type == StepType.WAIT_EVENT and "waiting_for" in output:
                    event_type = output["waiting_for"]
                    self.waiting_instances[event_type].append(instance.instance_id)
                    return True, "WAIT"
                
                # Étape de fin ?
                definition = self.definitions[instance.workflow_id]
                if step.step_id in definition.end_steps:
                    return True, "END"
                
                return True, self._get_next_step(step)
            else:
                # Gestion des erreurs avec retry
                step.retry_count += 1
                if step.retry_count <= step.max_retries:
                    step.status = StepStatus.RETRYING
                    logger.warning("Step %s failed, retrying (%d/%d)", 
                                 step.step_id, step.retry_count, step.max_retries)
                    await asyncio.sleep(2 ** step.retry_count)  # Exponential backoff
                    return await self._execute_step(instance, step)
                else:
                    step.status = StepStatus.FAILED
                    step.error_message = output.get("error", "Unknown error")
                    step.completed_at = datetime.now(timezone.utc)
                    return False, None
                    
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error_message = str(e)
            step.completed_at = datetime.now(timezone.utc)
            logger.error("Step execution failed: %s", e)
            return False, None
    
    def _check_conditions(self, conditions: List[str], instance: WorkflowInstance) -> bool:
        """Vérifie les conditions d'une étape"""
        # Implémentation basique
        for condition in conditions:
            if not self._evaluate_simple_condition(condition, instance):
                return False
        return True
    
    def _evaluate_simple_condition(self, condition: str, instance: WorkflowInstance) -> bool:
        """Évalue une condition simple"""
        # Format: "variable_name == value" ou "variable_name > value"
        try:
            # Substitution des variables
            for var_name, var in instance.variables.items():
                condition = condition.replace(f"${{{var_name}}}", str(var.value))
            
            return eval(condition)
        except:
            return False
    
    def _get_next_step(self, step: WorkflowStep) -> Optional[str]:
        """Détermine la prochaine étape"""
        if not step.next_steps:
            return None
        
        # Pour l'instant, prend la première étape suivante
        # Peut être étendu pour la logique conditionnelle
        return step.next_steps[0]
    
    async def _handle_event(self, event: Event):
        """
Gère les événements pour les workflows en attente"""
        # Vérification des déclencheurs de nouveaux workflows
        await self._check_workflow_triggers(event)
        
        # Vérification des workflows en attente
        await self._check_waiting_workflows(event)
    
    async def _check_workflow_triggers(self, event: Event):
        """
Vérifie si l'événement déclenche de nouveaux workflows"""
        for definition in self.definitions.values():
            if not definition.enabled:
                continue
            
            for trigger in definition.triggers:
                if event.type.startswith(trigger) or trigger == "*":
                    # Variables depuis l'événement
                    variables = {
                        "event_id": event.id,
                        "event_type": event.type,
                        "user_id": event.user_id,
                        "tenant_id": event.tenant_id,
                        **event.data
                    }
                    
                    await self.start_workflow(
                        definition.workflow_id,
                        variables=variables,
                        user_id=event.user_id,
                        tenant_id=event.tenant_id,
                        correlation_id=event.correlation_id
                    )
    
    async def _check_waiting_workflows(self, event: Event):
        """Vérifie les workflows en attente d'événements"""
        matching_types = []
        
        # Recherche des types d'événements correspondants
        for event_type in self.waiting_instances.keys():
            if event.type.startswith(event_type) or event_type == "*":
                matching_types.append(event_type)
        
        for event_type in matching_types:
            instance_ids = self.waiting_instances[event_type].copy()
            
            for instance_id in instance_ids:
                instance = self.instances.get(instance_id)
                if not instance or instance.status != WorkflowStatus.WAITING:
                    self.waiting_instances[event_type].remove(instance_id)
                    continue
                
                # Vérification des filtres si nécessaire
                step = instance.steps.get(instance.current_step)
                if step and self._event_matches_filters(event, step.output.get("filters", {})):
                    # Réveil du workflow
                    instance.status = WorkflowStatus.RUNNING
                    instance.events_consumed.append(event.id)
                    self.waiting_instances[event_type].remove(instance_id)
                    
                    # Continuation du workflow
                    next_step = self._get_next_step(step)
                    if next_step:
                        asyncio.create_task(self._execute_workflow(instance, next_step))
                    else:
                        instance.status = WorkflowStatus.COMPLETED
                        instance.completed_at = datetime.now(timezone.utc)
    
    def _event_matches_filters(self, event: Event, filters: Dict[str, Any]) -> bool:
        """Vérifie si un événement correspond aux filtres"""
        for key, expected_value in filters.items():
            if key == "user_id" and event.user_id != expected_value:
                return False
            elif key == "tenant_id" and event.tenant_id != expected_value:
                return False
            elif key in event.data and event.data[key] != expected_value:
                return False
            elif key in event.metadata and event.metadata[key] != expected_value:
                return False
        
        return True
    
    def get_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Retourne une instance de workflow"""
        return self.instances.get(instance_id)
    
    def get_instances_by_workflow(self, workflow_id: str) -> List[WorkflowInstance]:
        """
Retourne toutes les instances d'un workflow"""
        return [
            instance for instance in self.instances.values()
            if instance.workflow_id == workflow_id
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """
Retourne les statistiques"""
        return {
            "stats": self.stats.copy(),
            "definitions_count": len(self.definitions),
            "active_instances": len([i for i in self.instances.values() 
                                   if i.status in [WorkflowStatus.RUNNING, WorkflowStatus.WAITING]]),
            "waiting_instances": sum(len(instances) for instances in self.waiting_instances.values())
        }


# Workflows prédéfinis pour IA-Influencer-Agent
def create_content_processing_workflow() -> WorkflowDefinition:
    """Crée le workflow de traitement de contenu"""
    workflow = WorkflowDefinition(
        workflow_id="content_processing",
        name="Content Processing Workflow",
        description="Workflow complet de traitement du contenu uploadé"
    )
    
    # Variables
    workflow.add_variable(WorkflowVariable("content_id", "", "string", "ID du contenu", True))
    workflow.add_variable(WorkflowVariable("content_type", "", "string", "Type de contenu", True))
    workflow.add_variable(WorkflowVariable("user_id", "", "string", "ID utilisateur", True))
    
    # Étapes
    workflow.add_step(WorkflowStep(
        step_id="validate_content",
        name="Validate Content",
        step_type=StepType.ACTION,
        config={"action": "validate_content", "params": {"content_id": "${content_id}"}},
        next_steps=["fingerprint_content"]
    ))
    
    workflow.add_step(WorkflowStep(
        step_id="fingerprint_content",
        name="Generate Fingerprint",
        step_type=StepType.ACTION,
        config={"action": "generate_fingerprint", "params": {"content_id": "${content_id}", "type": "${content_type}"}},
        next_steps=["enable_protection"]
    ))
    
    workflow.add_step(WorkflowStep(
        step_id="enable_protection",
        name="Enable Protection",
        step_type=StepType.ACTION,
        config={"action": "enable_protection", "params": {"content_id": "${content_id}"}},
        next_steps=["start_monitoring"]
    ))
    
    workflow.add_step(WorkflowStep(
        step_id="start_monitoring",
        name="Start Monitoring",
        step_type=StepType.ACTION,
        config={"action": "start_monitoring", "params": {"content_id": "${content_id}"}},
        next_steps=[]
    ))
    
    workflow.set_start_step("validate_content")
    workflow.add_end_step("start_monitoring")
    workflow.add_trigger("content.uploaded")
    
    return workflow


def create_violation_response_workflow() -> WorkflowDefinition:
    """Crée le workflow de réponse aux violations"""
    workflow = WorkflowDefinition(
        workflow_id="violation_response",
        name="Violation Response Workflow",
        description="Workflow de réponse automatique aux violations détectées"
    )
    
    # Variables
    workflow.add_variable(WorkflowVariable("violation_url", "", "string", "URL de la violation", True))
    workflow.add_variable(WorkflowVariable("similarity_score", 0.0, "number", "Score de similarité", True))
    workflow.add_variable(WorkflowVariable("platform", "", "string", "Plateforme", True))
    
    # Étapes
    workflow.add_step(WorkflowStep(
        step_id="analyze_violation",
        name="Analyze Violation",
        step_type=StepType.ACTION,
        config={"action": "analyze_violation", "params": {"url": "${violation_url}", "score": "${similarity_score}"}},
        next_steps=["check_severity"]
    ))
    
    workflow.add_step(WorkflowStep(
        step_id="check_severity",
        name="Check Severity",
        step_type=StepType.CONDITION,
        config={"condition": "${similarity_score} > 0.9"},
        next_steps=["send_takedown", "monitor_violation"]
    ))
    
    workflow.add_step(WorkflowStep(
        step_id="send_takedown",
        name="Send Takedown Request",
        step_type=StepType.ACTION,
        config={"action": "send_takedown", "params": {"url": "${violation_url}", "platform": "${platform}"}},
        conditions=["${similarity_score} > 0.9"],
        next_steps=["wait_takedown_response"]
    ))
    
    workflow.add_step(WorkflowStep(
        step_id="monitor_violation",
        name="Monitor Violation",
        step_type=StepType.ACTION,
        config={"action": "monitor_violation", "params": {"url": "${violation_url}"}},
        conditions=["${similarity_score} <= 0.9"],
        next_steps=[]
    ))
    
    workflow.add_step(WorkflowStep(
        step_id="wait_takedown_response",
        name="Wait Takedown Response",
        step_type=StepType.WAIT_EVENT,
        config={"event_type": "protection.takedown.completed", "filters": {"violation_url": "${violation_url}"}},
        timeout=timedelta(days=7),
        next_steps=[]
    ))
    
    workflow.set_start_step("analyze_violation")
    workflow.add_end_step("monitor_violation")
    workflow.add_end_step("wait_takedown_response")
    workflow.add_trigger("protection.violation.detected")
    
    return workflow


# Instance globale
workflow_engine: Optional[WorkflowEngine] = None


def initialize_workflow_engine(event_bus: EventBus) -> WorkflowEngine:
    """Initialise le moteur de workflows"""
    global workflow_engine
    
    if workflow_engine is None:
        workflow_engine = WorkflowEngine(event_bus)
        
        # Enregistrement des workflows prédéfinis
        workflow_engine.register_workflow(create_content_processing_workflow())
        workflow_engine.register_workflow(create_violation_response_workflow())
        
        logger.info("WorkflowEngine initialized with predefined workflows")
    
    return workflow_engine
