"""
IA-Influencer-Agent - Event Scheduler System
Module: backend/core/events/event_scheduler.py
Architecture: Delayed and Scheduled Event Processing
Auteur: Fahed Mlaiel <mlaiel@live.de>

  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT 
© 2025 Fahed Mlaiel. Tous droits réservés.

Description:
    Système de planification d'événements avec support des événements différés,
    récurrents et conditionnels pour la plateforme IA-Influencer-Agent.
"""

from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import asyncio
import json
import logging
import uuid
import heapq
from abc import ABC, abstractmethod
import cron_descriptor

from .event_bus import Event, EventPriority, EventStatus
from .event_types import EventType

logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """Types de planification"""
    ONCE = "once"              # Exécution unique
    RECURRING = "recurring"    # Récurrent
    CRON = "cron"             # Expression cron
    CONDITIONAL = "conditional" # Basé sur condition


class ScheduleStatus(Enum):
    """Statut des tâches planifiées"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class ScheduledTask:
    """Tâche planifiée"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    schedule_type: ScheduleType = ScheduleType.ONCE
    scheduled_at: Optional[datetime] = None
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    max_executions: Optional[int] = None
    condition: Optional[str] = None  # Expression conditionnelle
    event_template: Optional[Dict[str, Any]] = None
    handler_function: Optional[str] = None  # Nom de la fonction à exécuter
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # État d'exécution
    status: ScheduleStatus = ScheduleStatus.PENDING
    execution_count: int = 0
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Configuration
    timeout: float = 300.0  # 5 minutes
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: float = 60.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "schedule_type": self.schedule_type.value,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "cron_expression": self.cron_expression,
            "interval_seconds": self.interval_seconds,
            "max_executions": self.max_executions,
            "condition": self.condition,
            "event_template": self.event_template,
            "handler_function": self.handler_function,
            "payload": self.payload,
            "metadata": self.metadata,
            "status": self.status.value,
            "execution_count": self.execution_count,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "next_execution": self.next_execution.isoformat() if self.next_execution else None,
            "created_at": self.created_at.isoformat()
        }


class ConditionEvaluator:
    """Évaluateur de conditions pour tâches conditionnelles"""
    
    def __init__(self):
        self._context: Dict[str, Any] = {}
    
    def update_context(self, context: Dict[str, Any]):
        """Met à jour le contexte d'évaluation"""
        self._context.update(context)
    
    def evaluate(self, condition: str) -> bool:
        """Évalue une condition"""



        try:
            # Sécurisation de l'évaluation (simple)
            allowed_names = {
                'len', 'sum', 'max', 'min', 'abs',
                'True', 'False', 'None',
                **self._context
            }
            
            # Compilation sécurisée
            code = compile(condition, '<condition>', 'eval')
            
            # Vérification des noms utilisés
            for name in code.co_names:
                if name not in allowed_names:
                    raise ValueError(f"Name '{name}' not allowed in condition")
            
            # Évaluation
            result = eval(code, {"__builtins__": {}}, allowed_names)
            return bool(result)
            
        except Exception as e:
            logger.error("Failed to evaluate condition '%s': %s", condition, e)
            return False


class CronScheduler:
    """Planificateur cron simplifié"""
    
    @staticmethod
    def parse_cron(expression: str) -> Dict[str, Any]:
        """Parse une expression cron (format simplifié)"""



        try:
            parts = expression.split()
            if len(parts) != 5:
                raise ValueError("Cron expression must have 5 parts")
            
            return {
                'minute': parts[0],
                'hour': parts[1],
                'day': parts[2],
                'month': parts[3],
                'weekday': parts[4]
            }
        except Exception as e:
            logger.error("Failed to parse cron expression '%s': %s", expression, e)
            return {}
    
    @staticmethod
    def get_next_execution(cron_expr: str, from_time: datetime) -> Optional[datetime]:
        """Calcule la prochaine exécution selon expression cron"""



        try:
            # Implementation simplifiée - nécessiterait une librairie cron complète
            # Pour démo, retourne dans 1 heure
            return from_time + timedelta(hours=1)
        except Exception as e:
            logger.error("Failed to calculate next cron execution: %s", e)
            return None


class DelayedEventHandler:
    """Handler pour événements différés"""
    
    def __init__(self, task: ScheduledTask):
        self.task = task
        self.is_running = False
    
    async def execute(self, scheduler: "EventScheduler") -> bool:
        """Exécute la tâche planifiée"""
        if self.is_running:
            logger.warning("Task %s is already running", self.task.task_id)
            return False
        
        self.is_running = True
        success = False
        
        try:
            self.task.status = ScheduleStatus.RUNNING
            self.task.last_execution = datetime.now(timezone.utc)
            self.task.execution_count += 1
            
            logger.debug("Executing scheduled task: %s", self.task.name)
            
            # Exécution selon le type
            if self.task.event_template:
                success = await self._execute_event_creation(scheduler)
            elif self.task.handler_function:
                success = await self._execute_handler_function(scheduler)
            else:
                logger.warning("No execution method defined for task %s", self.task.task_id)
                success = False
            
            # Mise à jour du statut
            if success:
                self.task.status = ScheduleStatus.COMPLETED
                self.task.retry_count = 0
                
                # Planification suivante si récurrent
                if self._should_reschedule():
                    self._calculate_next_execution()
                    self.task.status = ScheduleStatus.PENDING
                
            else:
                self.task.status = ScheduleStatus.FAILED
                
                # Retry si configuré
                if self.task.retry_count < self.task.max_retries:
                    self.task.retry_count += 1
                    self.task.status = ScheduleStatus.PENDING
                    self.task.next_execution = datetime.now(timezone.utc) + timedelta(seconds=self.task.retry_delay)
                    logger.info("Scheduled retry %d/%d for task %s", 
                               self.task.retry_count, self.task.max_retries, self.task.task_id)
            
            return success
            
        except Exception as e:
            logger.error("Error executing task %s: %s", self.task.task_id, e)
            self.task.status = ScheduleStatus.FAILED
            return False
        finally:
            self.is_running = False
    
    async def _execute_event_creation(self, scheduler: "EventScheduler") -> bool:
        """Exécute la création d'un événement"""



        try:
            if not self.task.event_template:
                return False
            
            # Création de l'événement depuis le template
            event_data = self.task.event_template.copy()
            event_data.update(self.task.payload)
            
            # Substitution des variables
            event_data = self._substitute_variables(event_data)
            
            # Création de l'événement
            event = Event.from_dict(event_data)
            
            # Publication via le scheduler
            if scheduler.event_bus:
                success = await scheduler.event_bus.publish(event)
                if success:
                    logger.debug("Event published from scheduled task %s: %s", 
                               self.task.task_id, event.id)
                return success
            
            return False
            
        except Exception as e:
            logger.error("Failed to execute event creation for task %s: %s", 
                        self.task.task_id, e)
            return False
    
    async def _execute_handler_function(self, scheduler: "EventScheduler") -> bool:
        """Exécute une fonction handler"""



        try:
            if not self.task.handler_function:
                return False
            
            # Récupération de la fonction depuis le registry du scheduler
            handler = scheduler.get_handler_function(self.task.handler_function)
            
            if not handler:
                logger.error("Handler function '%s' not found", self.task.handler_function)
                return False
            
            # Exécution avec timeout
            if asyncio.iscoroutinefunction(handler):
                result = await asyncio.wait_for(
                    handler(self.task),
                    timeout=self.task.timeout
                )
            else:
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, handler, self.task),
                    timeout=self.task.timeout
                )
            
            return bool(result)
            
        except asyncio.TimeoutError:
            logger.error("Handler function timed out for task %s", self.task.task_id)
            return False
        except Exception as e:
            logger.error("Failed to execute handler function for task %s: %s", 
                        self.task.task_id, e)
            return False
    
    def _substitute_variables(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Substitue les variables dans les données"""



        try:
            variables = {
                'now': datetime.now(timezone.utc).isoformat(),
                'task_id': self.task.task_id,
                'execution_count': self.task.execution_count,
                **self.task.payload
            }
            
            # Conversion en JSON puis substitution simple
            json_str = json.dumps(data)
            
            for key, value in variables.items():
                json_str = json_str.replace(f"{{{{{key}}}}}", str(value))
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.error("Failed to substitute variables: %s", e)
            return data
    
    def _should_reschedule(self) -> bool:
        """Vérifie si la tâche doit être replanifiée"""
        if self.task.schedule_type == ScheduleType.ONCE:
            return False
        
        if self.task.max_executions and self.task.execution_count >= self.task.max_executions:
            return False
        
        return True
    
    def _calculate_next_execution(self):
        """Calcule la prochaine exécution"""
        now = datetime.now(timezone.utc)
        
        if self.task.schedule_type == ScheduleType.RECURRING and self.task.interval_seconds:
            self.task.next_execution = now + timedelta(seconds=self.task.interval_seconds)
        
        elif self.task.schedule_type == ScheduleType.CRON and self.task.cron_expression:
            self.task.next_execution = CronScheduler.get_next_execution(
                self.task.cron_expression, now
            )
        
        else:
            logger.warning("Cannot calculate next execution for task %s", self.task.task_id)


class EventScheduler:
    """
    Système principal de planification d'événements
    """
    
    def __init__(
        self,
        event_bus=None,
        max_concurrent_tasks: int = 20
    ):
        self.event_bus = event_bus
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # Stockage des tâches
        self._tasks: Dict[str, ScheduledTask] = {}
        self._task_heap: List[Tuple[datetime, str]] = []  # (next_execution, task_id)
        self._handlers: Dict[str, DelayedEventHandler] = {}
        
        # Registry des fonctions handler
        self._handler_functions: Dict[str, Callable] = {}
        
        # Évaluateur de conditions
        self._condition_evaluator = ConditionEvaluator()
        
        # Contrôle d'exécution
        self._running = False
        self._execution_semaphore = asyncio.Semaphore(max_concurrent_tasks)
        
        # Statistiques
        self._stats = {
            "tasks_scheduled": 0,
            "tasks_executed": 0,
            "tasks_failed": 0,
            "tasks_cancelled": 0,
            "active_tasks": 0
        }
        
        logger.info("EventScheduler initialized")
    
    async def start(self):
        """Démarre le planificateur"""
        if self._running:
            return
        
        self._running = True
        asyncio.create_task(self._execution_loop())
        logger.info("EventScheduler started")
    
    async def stop(self):
        """Arrête le planificateur"""
        self._running = False
        logger.info("EventScheduler stopped")
    
    def schedule_task(self, task: ScheduledTask) -> str:
        """Planifie une tâche"""



        try:
            # Validation
            if not self._validate_task(task):
                raise ValueError("Invalid task configuration")
            
            # Calcul de la prochaine exécution
            self._calculate_initial_execution(task)
            
            # Stockage
            self._tasks[task.task_id] = task
            self._handlers[task.task_id] = DelayedEventHandler(task)
            
            # Ajout au heap si exécution programmée
            if task.next_execution:
                heapq.heappush(self._task_heap, (task.next_execution, task.task_id))
            
            self._stats["tasks_scheduled"] += 1
            self._stats["active_tasks"] += 1
            
            logger.info("Task scheduled: %s (%s)", task.name, task.task_id)
            return task.task_id
            
        except Exception as e:
            logger.error("Failed to schedule task %s: %s", task.name, e)
            raise
    
    def schedule_event(
        self,
        event_template: Dict[str, Any],
        delay_seconds: Optional[int] = None,
        scheduled_at: Optional[datetime] = None,
        name: Optional[str] = None
    ) -> str:
        """Planifie la publication d'un événement"""
        task = ScheduledTask(
            name=name or f"event_{event_template.get('type', 'unknown')}",
            schedule_type=ScheduleType.ONCE,
            scheduled_at=scheduled_at,
            event_template=event_template
        )
        
        if delay_seconds and not scheduled_at:
            task.scheduled_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
        
        return self.schedule_task(task)
    
    def schedule_recurring_event(
        self,
        event_template: Dict[str, Any],
        interval_seconds: int,
        max_executions: Optional[int] = None,
        name: Optional[str] = None
    ) -> str:
        """Planifie un événement récurrent"""
        task = ScheduledTask(
            name=name or f"recurring_{event_template.get('type', 'unknown')}",
            schedule_type=ScheduleType.RECURRING,
            interval_seconds=interval_seconds,
            max_executions=max_executions,
            event_template=event_template,
            scheduled_at=datetime.now(timezone.utc)
        )
        
        return self.schedule_task(task)
    
    def schedule_cron_event(
        self,
        event_template: Dict[str, Any],
        cron_expression: str,
        max_executions: Optional[int] = None,
        name: Optional[str] = None
    ) -> str:
        """Planifie un événement avec expression cron"""
        task = ScheduledTask(
            name=name or f"cron_{event_template.get('type', 'unknown')}",
            schedule_type=ScheduleType.CRON,
            cron_expression=cron_expression,
            max_executions=max_executions,
            event_template=event_template
        )
        
        return self.schedule_task(task)
    
    def schedule_function(
        self,
        handler_function: str,
        delay_seconds: Optional[int] = None,
        scheduled_at: Optional[datetime] = None,
        payload: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None
    ) -> str:
        """Planifie l'exécution d'une fonction"""
        task = ScheduledTask(
            name=name or f"function_{handler_function}",
            schedule_type=ScheduleType.ONCE,
            scheduled_at=scheduled_at,
            handler_function=handler_function,
            payload=payload or {}
        )
        
        if delay_seconds and not scheduled_at:
            task.scheduled_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
        
        return self.schedule_task(task)
    
    def register_handler_function(self, name: str, function: Callable):
        """Enregistre une fonction handler"""
        self._handler_functions[name] = function
        logger.debug("Handler function registered: %s", name)
    
    def get_handler_function(self, name: str) -> Optional[Callable]:
        """Récupère une fonction handler"""



        return self._handler_functions.get(name)
    
    def cancel_task(self, task_id: str) -> bool:
        """Annule une tâche planifiée"""
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        task.status = ScheduleStatus.CANCELLED
        
        self._stats["tasks_cancelled"] += 1
        self._stats["active_tasks"] -= 1
        
        logger.info("Task cancelled: %s", task_id)
        return True
    
    def pause_task(self, task_id: str) -> bool:
        """Met en pause une tâche"""
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        if task.status == ScheduleStatus.PENDING:
            task.status = ScheduleStatus.PAUSED
            logger.info("Task paused: %s", task_id)
            return True
        
        return False
    
    def resume_task(self, task_id: str) -> bool:
        """Remet en marche une tâche"""
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        if task.status == ScheduleStatus.PAUSED:
            task.status = ScheduleStatus.PENDING
            
            # Recalcul de la prochaine exécution
            self._calculate_initial_execution(task)
            if task.next_execution:
                heapq.heappush(self._task_heap, (task.next_execution, task_id))
            
            logger.info("Task resumed: %s", task_id)
            return True
        
        return False
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Récupère une tâche par ID"""



        return self._tasks.get(task_id)
    
    def get_tasks(
        self,
        status: Optional[ScheduleStatus] = None,
        schedule_type: Optional[ScheduleType] = None
    ) -> List[ScheduledTask]:
        """Récupère les tâches selon critères"""
        tasks = list(self._tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if schedule_type:
            tasks = [t for t in tasks if t.schedule_type == schedule_type]
        
        return tasks
    
    def update_condition_context(self, context: Dict[str, Any]):
        """Met à jour le contexte pour l'évaluation des conditions"""
        self._condition_evaluator.update_context(context)
    
    async def _execution_loop(self):
        """Boucle principale d'exécution"""
        while self._running:
            try:
                await self._process_due_tasks()
                await asyncio.sleep(1.0)  # Vérification chaque seconde
                
            except Exception as e:
                logger.error("Error in scheduler execution loop: %s", e)
    
    async def _process_due_tasks(self):
        """Traite les tâches à exécuter"""
        now = datetime.now(timezone.utc)
        due_tasks = []
        
        # Récupération des tâches dues
        while self._task_heap:
            next_time, task_id = self._task_heap[0]
            
            if next_time <= now:
                heapq.heappop(self._task_heap)
                
                if task_id in self._tasks:
                    task = self._tasks[task_id]
                    
                    # Vérification des conditions
                    if self._should_execute_task(task):
                        due_tasks.append(task_id)
            else:
                break
        
        # Exécution des tâches dues
        if due_tasks:
            tasks = [self._execute_task(task_id) for task_id in due_tasks]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def _should_execute_task(self, task: ScheduledTask) -> bool:
        """Vérifie si une tâche doit être exécutée"""
        if task.status != ScheduleStatus.PENDING:
            return False
        
        # Vérification des conditions
        if task.condition:
            if not self._condition_evaluator.evaluate(task.condition):
                logger.debug("Condition not met for task %s: %s", 
                           task.task_id, task.condition)
                return False
        
        return True
    
    async def _execute_task(self, task_id: str):
        """Exécute une tâche"""
        async with self._execution_semaphore:
            try:
                if task_id not in self._handlers:
                    logger.error("Handler not found for task %s", task_id)
                    return
                
                handler = self._handlers[task_id]
                success = await handler.execute(self)
                
                if success:
                    self._stats["tasks_executed"] += 1
                    logger.debug("Task executed successfully: %s", task_id)
                else:
                    self._stats["tasks_failed"] += 1
                    logger.warning("Task execution failed: %s", task_id)
                
                # Nettoyage si terminé
                task = self._tasks.get(task_id)
                if task and task.status in [ScheduleStatus.COMPLETED, ScheduleStatus.FAILED]:
                    if not handler._should_reschedule():
                        self._stats["active_tasks"] -= 1
                
            except Exception as e:
                logger.error("Error executing task %s: %s", task_id, e)
                self._stats["tasks_failed"] += 1
    
    def _validate_task(self, task: ScheduledTask) -> bool:
        """Valide la configuration d'une tâche"""
        if not task.name:
            return False
        
        if task.schedule_type == ScheduleType.CRON and not task.cron_expression:
            return False
        
        if task.schedule_type == ScheduleType.RECURRING and not task.interval_seconds:
            return False
        
        if not task.event_template and not task.handler_function:
            return False
        
        return True
    
    def _calculate_initial_execution(self, task: ScheduledTask):
        """Calcule la première exécution d'une tâche"""
        now = datetime.now(timezone.utc)
        
        if task.scheduled_at:
            task.next_execution = task.scheduled_at
        elif task.schedule_type == ScheduleType.RECURRING and task.interval_seconds:
            task.next_execution = now + timedelta(seconds=task.interval_seconds)
        elif task.schedule_type == ScheduleType.CRON and task.cron_expression:
            task.next_execution = CronScheduler.get_next_execution(
                task.cron_expression, now
            )
        else:
            task.next_execution = now
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques"""
        pending_tasks = len([t for t in self._tasks.values() 
                           if t.status == ScheduleStatus.PENDING])
        
        return {
            "stats": self._stats.copy(),
            "total_tasks": len(self._tasks),
            "pending_tasks": pending_tasks,
            "registered_functions": len(self._handler_functions),
            "running": self._running
        }


# Instance globale
default_scheduler = EventScheduler()
