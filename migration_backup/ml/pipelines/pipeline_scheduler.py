"""
Pipeline Scheduler - IA Chéries Enterprise ML Pipeline
Système d'ordonnancement avancé avec gestion des priorités et optimisation des ressources

Auteur: Mlaiel (Expert Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + DevOps)  
Copyright: © 2024 IA Chéries. Tous droits réservés.
Licence: Propriétaire - Usage strictement réservé à IA Chéries
Version: 1.0.0 - Architecture Niveau 3 Backend

CONFIDENTIAL - NE PAS DISTRIBUER
Ce code contient des informations propriétaires et des algorithmes d'IA confidentiels.
Toute reproduction, modification ou distribution non autorisée est strictement interdite.
"""

import asyncio
import heapq
import json
import logging
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, Future
import uuid

import croniter
import psutil


class TaskPriority(Enum):
    """Niveaux de priorité des tâches"""
    EMERGENCY = 1    # Tâches critiques urgentes
    HIGH = 2         # Tâches importantes
    NORMAL = 3       # Tâches standard
    LOW = 4          # Tâches en arrière-plan
    BATCH = 5        # Tâches de traitement par lot


class TaskStatus(Enum):
    """États des tâches"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class SchedulingStrategy(Enum):
    """Stratégies d'ordonnancement"""
    FIFO = "fifo"              # Premier arrivé, premier servi
    PRIORITY = "priority"       # Basé sur la priorité
    ROUND_ROBIN = "round_robin" # Rotation équitable
    WEIGHTED = "weighted"       # Pondéré par ressources
    ADAPTIVE = "adaptive"       # Adaptatif selon la charge


@dataclass
class ResourceRequirements:
    """Exigences en ressources pour une tâche"""
    cpu_cores: float = 1.0
    memory_mb: int = 512
    gpu_memory_mb: int = 0
    disk_space_mb: int = 100
    network_bandwidth_mbps: float = 0.0
    estimated_duration: timedelta = field(default_factory=lambda: timedelta(minutes=5))


@dataclass
class ScheduledTask:
    """Tâche planifiée"""
    task_id: str
    name: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    resources: ResourceRequirements = field(default_factory=ResourceRequirements)
    
    # Planification
    scheduled_time: Optional[datetime] = None
    cron_expression: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    
    # Gestion des échecs
    max_retries: int = 3
    retry_delay: timedelta = field(default_factory=lambda: timedelta(minutes=1))
    
    # Métadonnées
    created_at: datetime = field(default_factory=datetime.now)
    tags: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[timedelta] = None
    
    def __lt__(self, other):
        """Comparaison pour la file de priorité"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.scheduled_time < other.scheduled_time if self.scheduled_time else True


@dataclass
class TaskExecution:
    """Informations d'exécution d'une tâche"""
    task_id: str
    status: TaskStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Any = None
    error: Optional[Exception] = None
    retry_count: int = 0
    worker_id: Optional[str] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)


@dataclass
class WorkerStatus:
    """État d'un worker"""
    worker_id: str
    is_active: bool
    current_task: Optional[str] = None
    tasks_completed: int = 0
    total_runtime: timedelta = field(default_factory=lambda: timedelta(0))
    resource_capacity: ResourceRequirements = field(default_factory=ResourceRequirements)
    resource_usage: ResourceRequirements = field(default_factory=ResourceRequirements)


class PipelineScheduler:
    """
    Système d'ordonnancement avancé pour IA Chéries
    
    Fonctionnalités:
    - Ordonnancement basé sur les priorités
    - Gestion des dépendances entre tâches
    - Planification avec expressions cron
    - Optimisation des ressources
    - Pool de workers dynamique
    - Tolérance aux pannes avec retry
    - Monitoring en temps réel
    - Métriques de performance
    """
    
    def __init__(
        self, 
        max_workers: int = 4,
        strategy: SchedulingStrategy = SchedulingStrategy.ADAPTIVE,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.max_workers = max_workers
        self.strategy = strategy
        self.logger = self._setup_logger()
        
        # Files de tâches
        self.pending_tasks: List[ScheduledTask] = []  # Heap de priorité
        self.running_tasks: Dict[str, TaskExecution] = {}
        self.completed_tasks: deque = deque(maxlen=1000)
        self.failed_tasks: deque = deque(maxlen=100)
        
        # Gestion des workers
        self.workers: Dict[str, WorkerStatus] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="ainflue_worker")
        
        # Gestion des dépendances
        self.dependency_graph: Dict[str, List[str]] = defaultdict(list)
        self.completed_task_ids: set = set()
        
        # Tâches récurrentes
        self.cron_tasks: Dict[str, ScheduledTask] = {}
        self.next_cron_runs: List[Tuple[datetime, str]] = []
        
        # Ressources système
        self.system_resources = self._get_system_resources()
        self.resource_usage = ResourceRequirements()
        
        # Métriques
        self.metrics = {
            "tasks_scheduled": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0.0,
            "average_wait_time": 0.0
        }
        
        # Thread de planification
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        # Initialisation des workers
        self._initialize_workers()
    
    def _setup_logger(self) -> logging.Logger:
        """Configuration du logging"""
        logger = logging.getLogger(f"ainflue_scheduler_{id(self)}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _get_system_resources(self) -> ResourceRequirements:
        """Obtention des ressources système disponibles"""
        try:
            cpu_count = psutil.cpu_count()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return ResourceRequirements(
                cpu_cores=float(cpu_count),
                memory_mb=int(memory.total / (1024 * 1024)),
                disk_space_mb=int(disk.free / (1024 * 1024))
            )
        except Exception as e:
            self.logger.error(f"Erreur obtention ressources système: {e}")
            return ResourceRequirements(cpu_cores=4.0, memory_mb=8192)
    
    def _initialize_workers(self):
        """Initialisation des workers"""
        for i in range(self.max_workers):
            worker_id = f"worker_{i+1}"
            self.workers[worker_id] = WorkerStatus(
                worker_id=worker_id,
                is_active=True,
                resource_capacity=ResourceRequirements(
                    cpu_cores=self.system_resources.cpu_cores / self.max_workers,
                    memory_mb=self.system_resources.memory_mb // self.max_workers
                )
            )
    
    def schedule_task(
        self,
        name: str,
        function: Callable,
        args: tuple = (),
        kwargs: Optional[dict] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        resources: Optional[ResourceRequirements] = None,
        dependencies: Optional[List[str]] = None,
        scheduled_time: Optional[datetime] = None,
        cron_expression: Optional[str] = None,
        max_retries: int = 3,
        timeout: Optional[timedelta] = None,
        tags: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Planification d'une tâche
        
        Args:
            name: Nom de la tâche
            function: Fonction à exécuter
            args: Arguments positionnels
            kwargs: Arguments nommés
            priority: Priorité de la tâche
            resources: Exigences en ressources
            dependencies: IDs des tâches dépendantes
            scheduled_time: Heure de planification
            cron_expression: Expression cron pour tâches récurrentes
            max_retries: Nombre maximum de tentatives
            timeout: Timeout d'exécution
            tags: Métadonnées supplémentaires
            
        Returns:
            str: ID de la tâche planifiée
        """
        try:
            task_id = str(uuid.uuid4())
            
            task = ScheduledTask(
                task_id=task_id,
                name=name,
                function=function,
                args=args,
                kwargs=kwargs or {},
                priority=priority,
                resources=resources or ResourceRequirements(),
                dependencies=dependencies or [],
                scheduled_time=scheduled_time or datetime.now(),
                cron_expression=cron_expression,
                max_retries=max_retries,
                timeout=timeout,
                tags=tags or {}
            )
            
            # Ajout à la file de priorité
            heapq.heappush(self.pending_tasks, task)
            
            # Gestion des dépendances
            if dependencies:
                for dep_id in dependencies:
                    self.dependency_graph[dep_id].append(task_id)
            
            # Gestion des tâches récurrentes
            if cron_expression:
                self.cron_tasks[task_id] = task
                self._schedule_next_cron_run(task)
            
            self.metrics["tasks_scheduled"] += 1
            self.logger.info(f"Tâche planifiée: {name} (ID: {task_id})")
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"Erreur planification tâche {name}: {e}")
            raise
    
    def _schedule_next_cron_run(self, task: ScheduledTask):
        """Planification de la prochaine exécution cron"""
        try:
            if task.cron_expression:
                cron = croniter.croniter(task.cron_expression, datetime.now())
                next_run = cron.get_next(datetime)
                heapq.heappush(self.next_cron_runs, (next_run, task.task_id))
        except Exception as e:
            self.logger.error(f"Erreur planification cron {task.name}: {e}")
    
    def _scheduler_loop(self):
        """Boucle principale du planificateur"""
        while self.scheduler_running:
            try:
                current_time = datetime.now()
                
                # Traitement des tâches cron
                self._process_cron_tasks(current_time)
                
                # Ordonnancement des tâches en attente
                self._schedule_pending_tasks()
                
                # Nettoyage des tâches terminées
                self._cleanup_completed_tasks()
                
                # Attente avant prochaine itération
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Erreur dans la boucle du planificateur: {e}")
                time.sleep(5)
    
    def _process_cron_tasks(self, current_time: datetime):
        """Traitement des tâches cron"""
        while self.next_cron_runs and self.next_cron_runs[0][0] <= current_time:
            _, task_id = heapq.heappop(self.next_cron_runs)
            
            if task_id in self.cron_tasks:
                original_task = self.cron_tasks[task_id]
                
                # Création d'une nouvelle instance de la tâche
                new_task_id = str(uuid.uuid4())
                new_task = ScheduledTask(
                    task_id=new_task_id,
                    name=f"{original_task.name}_cron_{int(time.time())}",
                    function=original_task.function,
                    args=original_task.args,
                    kwargs=original_task.kwargs,
                    priority=original_task.priority,
                    resources=original_task.resources,
                    scheduled_time=current_time,
                    max_retries=original_task.max_retries,
                    timeout=original_task.timeout,
                    tags=original_task.tags
                )
                
                heapq.heappush(self.pending_tasks, new_task)
                
                # Planification de la prochaine exécution
                self._schedule_next_cron_run(original_task)
    
    def _schedule_pending_tasks(self):
        """Ordonnancement des tâches en attente"""
        available_workers = [
            worker for worker in self.workers.values()
            if worker.is_active and worker.current_task is None
        ]
        
        if not available_workers or not self.pending_tasks:
            return
        
        # Tri selon la stratégie d'ordonnancement
        ready_tasks = self._get_ready_tasks()
        
        if self.strategy == SchedulingStrategy.ADAPTIVE:
            ready_tasks = self._optimize_task_assignment(ready_tasks, available_workers)
        
        # Attribution des tâches aux workers
        for task, worker in zip(ready_tasks, available_workers):
            if self._can_allocate_resources(task.resources):
                self._assign_task_to_worker(task, worker)
    
    def _get_ready_tasks(self) -> List[ScheduledTask]:
        """Obtention des tâches prêtes à être exécutées"""
        ready_tasks = []
        current_time = datetime.now()
        
        # Tri temporaire pour examiner les tâches
        temp_tasks = []
        
        while self.pending_tasks:
            task = heapq.heappop(self.pending_tasks)
            
            # Vérification du moment d'exécution
            if task.scheduled_time and task.scheduled_time > current_time:
                temp_tasks.append(task)
                continue
            
            # Vérification des dépendances
            if self._dependencies_satisfied(task):
                ready_tasks.append(task)
            else:
                temp_tasks.append(task)
        
        # Remise des tâches non prêtes dans la file
        for task in temp_tasks:
            heapq.heappush(self.pending_tasks, task)
        
        return ready_tasks
    
    def _dependencies_satisfied(self, task: ScheduledTask) -> bool:
        """Vérification si les dépendances d'une tâche sont satisfaites"""
        return all(dep_id in self.completed_task_ids for dep_id in task.dependencies)
    
    def _can_allocate_resources(self, required: ResourceRequirements) -> bool:
        """Vérification si les ressources peuvent être allouées"""
        available_cpu = self.system_resources.cpu_cores - self.resource_usage.cpu_cores
        available_memory = self.system_resources.memory_mb - self.resource_usage.memory_mb
        
        return (
            available_cpu >= required.cpu_cores and
            available_memory >= required.memory_mb
        )
    
    def _optimize_task_assignment(
        self, 
        tasks: List[ScheduledTask], 
        workers: List[WorkerStatus]
    ) -> List[ScheduledTask]:
        """Optimisation de l'attribution des tâches (stratégie adaptative)"""
        if not tasks:
            return []
        
        # Score basé sur la priorité et les ressources
        def task_score(task):
            priority_weight = 6 - task.priority.value  # Plus la priorité est élevée, plus le score est élevé
            resource_efficiency = 1.0 / (task.resources.cpu_cores + task.resources.memory_mb / 1000)
            wait_time = (datetime.now() - task.created_at).total_seconds() / 3600  # Heures d'attente
            
            return priority_weight * 10 + resource_efficiency * 5 + wait_time
        
        # Tri par score décroissant
        return sorted(tasks, key=task_score, reverse=True)
    
    def _assign_task_to_worker(self, task: ScheduledTask, worker: WorkerStatus):
        """Attribution d'une tâche à un worker"""
        try:
            # Mise à jour des ressources
            self.resource_usage.cpu_cores += task.resources.cpu_cores
            self.resource_usage.memory_mb += task.resources.memory_mb
            
            # Création de l'exécution
            execution = TaskExecution(
                task_id=task.task_id,
                status=TaskStatus.RUNNING,
                start_time=datetime.now(),
                worker_id=worker.worker_id
            )
            
            self.running_tasks[task.task_id] = execution
            worker.current_task = task.task_id
            
            # Soumission au thread pool
            future = self.executor.submit(self._execute_task, task, execution)
            
            # Callback pour la fin d'exécution
            future.add_done_callback(lambda f: self._task_completed(task, execution, f))
            
            self.logger.info(f"Tâche {task.name} assignée au worker {worker.worker_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur attribution tâche {task.name}: {e}")
            self._release_resources(task.resources)
    
    def _execute_task(self, task: ScheduledTask, execution: TaskExecution) -> Any:
        """Exécution d'une tâche"""
        try:
            start_time = time.time()
            
            # Application du timeout si spécifié
            if task.timeout:
                # Note: Dans un environnement réel, il faudrait implémenter un mécanisme de timeout
                pass
            
            # Exécution de la fonction
            result = task.function(*task.args, **task.kwargs)
            
            execution.result = result
            execution.resource_usage = {
                "execution_time": time.time() - start_time,
                "cpu_usage": task.resources.cpu_cores,
                "memory_usage": task.resources.memory_mb
            }
            
            return result
            
        except Exception as e:
            execution.error = e
            raise
    
    def _task_completed(self, task: ScheduledTask, execution: TaskExecution, future: Future):
        """Callback pour la fin d'exécution d'une tâche"""
        try:
            end_time = datetime.now()
            execution.end_time = end_time
            
            # Libération du worker
            worker_id = execution.worker_id
            if worker_id in self.workers:
                worker = self.workers[worker_id]
                worker.current_task = None
                worker.tasks_completed += 1
                if execution.start_time:
                    worker.total_runtime += end_time - execution.start_time
            
            # Libération des ressources
            self._release_resources(task.resources)
            
            # Suppression de la liste des tâches en cours
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
            
            try:
                result = future.result()
                execution.status = TaskStatus.COMPLETED
                execution.result = result
                
                # Ajout aux tâches complétées
                self.completed_tasks.append(execution)
                self.completed_task_ids.add(task.task_id)
                
                # Déclenchement des tâches dépendantes
                self._trigger_dependent_tasks(task.task_id)
                
                # Mise à jour des métriques
                self.metrics["tasks_completed"] += 1
                if execution.start_time:
                    exec_time = (end_time - execution.start_time).total_seconds()
                    self.metrics["total_execution_time"] += exec_time
                
                self.logger.info(f"Tâche {task.name} terminée avec succès")
                
            except Exception as e:
                execution.status = TaskStatus.FAILED
                execution.error = e
                
                # Gestion des tentatives
                if execution.retry_count < task.max_retries:
                    self._retry_task(task, execution)
                else:
                    self.failed_tasks.append(execution)
                    self.metrics["tasks_failed"] += 1
                    self.logger.error(f"Tâche {task.name} échouée définitivement: {e}")
            
        except Exception as e:
            self.logger.error(f"Erreur dans callback de fin de tâche: {e}")
    
    def _release_resources(self, resources: ResourceRequirements):
        """Libération des ressources"""
        self.resource_usage.cpu_cores -= resources.cpu_cores
        self.resource_usage.memory_mb -= resources.memory_mb
        
        # Assurance que les valeurs ne deviennent pas négatives
        self.resource_usage.cpu_cores = max(0, self.resource_usage.cpu_cores)
        self.resource_usage.memory_mb = max(0, self.resource_usage.memory_mb)
    
    def _retry_task(self, task: ScheduledTask, execution: TaskExecution):
        """Nouvelle tentative d'exécution d'une tâche"""
        try:
            execution.retry_count += 1
            execution.status = TaskStatus.RETRYING
            
            # Planification de la nouvelle tentative
            retry_time = datetime.now() + task.retry_delay
            
            retry_task = ScheduledTask(
                task_id=task.task_id,
                name=f"{task.name}_retry_{execution.retry_count}",
                function=task.function,
                args=task.args,
                kwargs=task.kwargs,
                priority=task.priority,
                resources=task.resources,
                scheduled_time=retry_time,
                dependencies=task.dependencies,
                max_retries=task.max_retries,
                timeout=task.timeout,
                tags=task.tags
            )
            
            heapq.heappush(self.pending_tasks, retry_task)
            
            self.logger.info(f"Nouvelle tentative planifiée pour {task.name} (tentative {execution.retry_count})")
            
        except Exception as e:
            self.logger.error(f"Erreur planification nouvelle tentative {task.name}: {e}")
    
    def _trigger_dependent_tasks(self, completed_task_id: str):
        """Déclenchement des tâches dépendantes"""
        dependent_task_ids = self.dependency_graph.get(completed_task_id, [])
        
        for dep_task_id in dependent_task_ids:
            # Vérification si toutes les dépendances sont satisfaites
            # (cette logique serait plus complexe dans un système réel)
            pass
    
    def _cleanup_completed_tasks(self):
        """Nettoyage périodique des tâches terminées"""
        # Nettoyage des tâches anciennes (plus de 24h)
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Nettoyage des tâches complétées
        while (self.completed_tasks and 
               self.completed_tasks[0].end_time and 
               self.completed_tasks[0].end_time < cutoff_time):
            self.completed_tasks.popleft()
        
        # Nettoyage des tâches échouées
        while (self.failed_tasks and 
               self.failed_tasks[0].end_time and 
               self.failed_tasks[0].end_time < cutoff_time):
            self.failed_tasks.popleft()
    
    def get_status(self) -> Dict[str, Any]:
        """Obtention du statut du planificateur"""
        try:
            current_time = datetime.now()
            uptime = current_time - datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            
            return {
                "scheduler_status": "running" if self.scheduler_running else "stopped",
                "uptime_seconds": uptime.total_seconds(),
                "tasks": {
                    "pending": len(self.pending_tasks),
                    "running": len(self.running_tasks),
                    "completed": len(self.completed_tasks),
                    "failed": len(self.failed_tasks)
                },
                "workers": {
                    "total": len(self.workers),
                    "active": sum(1 for w in self.workers.values() if w.is_active),
                    "busy": sum(1 for w in self.workers.values() if w.current_task is not None)
                },
                "resources": {
                    "cpu_usage": self.resource_usage.cpu_cores,
                    "memory_usage_mb": self.resource_usage.memory_mb,
                    "cpu_capacity": self.system_resources.cpu_cores,
                    "memory_capacity_mb": self.system_resources.memory_mb
                },
                "metrics": self.metrics,
                "cron_tasks": len(self.cron_tasks)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur obtention statut: {e}")
            return {"error": "Unable to get scheduler status"}
    
    def cancel_task(self, task_id: str) -> bool:
        """Annulation d'une tâche"""
        try:
            # Recherche dans les tâches en attente
            for i, task in enumerate(self.pending_tasks):
                if task.task_id == task_id:
                    # Suppression de la file (reconstruction nécessaire pour heap)
                    self.pending_tasks.pop(i)
                    heapq.heapify(self.pending_tasks)
                    
                    self.logger.info(f"Tâche {task_id} annulée (en attente)")
                    return True
            
            # Recherche dans les tâches en cours
            if task_id in self.running_tasks:
                execution = self.running_tasks[task_id]
                execution.status = TaskStatus.CANCELLED
                
                # Note: Dans un environnement réel, il faudrait pouvoir interrompre
                # l'exécution de la tâche dans le thread pool
                
                self.logger.info(f"Tâche {task_id} marquée pour annulation")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erreur annulation tâche {task_id}: {e}")
            return False
    
    def pause_scheduler(self):
        """Pause du planificateur"""
        self.scheduler_running = False
        self.logger.info("Planificateur mis en pause")
    
    def resume_scheduler(self):
        """Reprise du planificateur"""
        if not self.scheduler_running:
            self.scheduler_running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            self.logger.info("Planificateur repris")
    
    def shutdown(self, wait: bool = True):
        """Arrêt du planificateur"""
        self.scheduler_running = False
        
        if wait:
            # Attente de la fin des tâches en cours
            self.executor.shutdown(wait=True)
        else:
            # Arrêt immédiat
            self.executor.shutdown(wait=False)
        
        self.logger.info("Planificateur arrêté")


# Configuration par défaut
DEFAULT_SCHEDULER_CONFIG = {
    "max_workers": 4,
    "strategy": SchedulingStrategy.ADAPTIVE,
    "resource_monitoring": True,
    "auto_scaling": False,
    "max_retry_attempts": 3
}


async def main():
    """Fonction principale pour tests"""
    scheduler = PipelineScheduler(
        max_workers=2,
        strategy=SchedulingStrategy.ADAPTIVE
    )
    
    # Fonction de test
    def test_function(name: str, duration: float = 1.0):
        print(f"Exécution de {name}")
        time.sleep(duration)
        return f"Résultat de {name}"
    
    # Planification de tâches de test
    task1_id = scheduler.schedule_task(
        name="Tâche prioritaire",
        function=test_function,
        args=("tâche_1", 2.0),
        priority=TaskPriority.HIGH
    )
    
    task2_id = scheduler.schedule_task(
        name="Tâche normale",
        function=test_function,
        args=("tâche_2", 1.0),
        priority=TaskPriority.NORMAL
    )
    
    # Tâche avec dépendance
    task3_id = scheduler.schedule_task(
        name="Tâche dépendante",
        function=test_function,
        args=("tâche_3", 0.5),
        dependencies=[task1_id]
    )
    
    # Tâche récurrente (toutes les minutes)
    cron_task_id = scheduler.schedule_task(
        name="Tâche cron",
        function=test_function,
        args=("tâche_cron",),
        cron_expression="* * * * *"
    )
    
    # Attente et affichage du statut
    await asyncio.sleep(5)
    
    status = scheduler.get_status()
    print(f"Statut du planificateur:")
    print(f"- Tâches en attente: {status['tasks']['pending']}")
    print(f"- Tâches en cours: {status['tasks']['running']}")
    print(f"- Tâches terminées: {status['tasks']['completed']}")
    print(f"- Workers actifs: {status['workers']['active']}")
    
    # Arrêt du planificateur
    scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())