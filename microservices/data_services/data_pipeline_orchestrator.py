"""
🔄 Data Pipeline Orchestrator - Orchestrateur de Pipelines Enterprise
© Fahed Mlaiel 2024-2025 - Ainflue Microservices Enterprise

Orchestrateur intelligent pour pipelines de données complexes avec Kafka, Spark et Flink.
Gestion automatisée des workflows ETL avec monitoring temps réel et récupération d'erreurs.
"""

import asyncio
from typing import Dict, List, Optional, Union, Any, Callable
from datetime import datetime, timedelta
import logging
import json
from dataclasses import dataclass, field
from enum import Enum
import uuid

import yaml
from croniter import croniter

logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """Statuts possibles d'un pipeline"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskType(Enum):
    """Types de tâches dans un pipeline"""
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    VALIDATION = "validation"
    NOTIFICATION = "notification"
    CLEANUP = "cleanup"


@dataclass
class PipelineTask:
    """Définition d'une tâche dans un pipeline"""
    task_id: str
    name: str
    task_type: TaskType
    function: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 3
    timeout: int = 3600  # secondes
    resources: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Pipeline:
    """Définition d'un pipeline de données"""
    pipeline_id: str
    name: str
    description: str
    tasks: List[PipelineTask]
    schedule: Optional[str] = None  # Cron expression
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    max_concurrent_runs: int = 1
    timeout: int = 7200  # secondes
    notification_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineRun:
    """Instance d'exécution d'un pipeline"""
    run_id: str
    pipeline_id: str
    status: PipelineStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    task_results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    triggered_by: str = "scheduler"
    context: Dict[str, Any] = field(default_factory=dict)


class DataPipelineOrchestrator:
    """Orchestrateur enterprise pour pipelines de données"""
    
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.active_runs: Dict[str, PipelineRun] = {}
        self.task_registry: Dict[str, Callable] = {}
        self.scheduler_running = False
        self.max_concurrent_runs = 10
        
        # Configuration des exécuteurs
        self.executors = {
            'spark': self._create_spark_executor(),
            'kafka': self._create_kafka_executor(),
            'flink': self._create_flink_executor(),
            'python': self._create_python_executor()
        }
        
        # Métriques
        self.metrics = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'avg_execution_time': 0.0
        }
    
    async def register_pipeline(self, pipeline: Pipeline) -> Dict[str, Any]:
        """Enregistre un nouveau pipeline"""
        
        try:
            # Valider le pipeline
            validation_result = await self._validate_pipeline(pipeline)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Pipeline validation failed',
                    'details': validation_result['errors']
                }
            
            # Enregistrer le pipeline
            self.pipelines[pipeline.pipeline_id] = pipeline
            
            logger.info(f"Pipeline {pipeline.pipeline_id} registered successfully")
            
            return {
                'success': True,
                'pipeline_id': pipeline.pipeline_id,
                'message': 'Pipeline registered successfully'
            }
            
        except Exception as e:
            logger.error(f"Error registering pipeline {pipeline.pipeline_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _validate_pipeline(self, pipeline: Pipeline) -> Dict[str, Any]:
        """Valide la configuration d'un pipeline"""
        
        errors = []
        warnings = []
        
        # Validation de base
        if not pipeline.name:
            errors.append("Pipeline name is required")
        
        if not pipeline.tasks:
            errors.append("Pipeline must have at least one task")
        
        # Validation des tâches
        task_ids = [task.task_id for task in pipeline.tasks]
        if len(task_ids) != len(set(task_ids)):
            errors.append("Duplicate task IDs found")
        
        # Validation des dépendances
        for task in pipeline.tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    errors.append(f"Task {task.task_id} depends on non-existent task {dep}")
        
        # Détection de cycles
        if self._has_cycles(pipeline.tasks):
            errors.append("Circular dependencies detected")
        
        # Validation du schedule
        if pipeline.schedule:
            try:
                croniter(pipeline.schedule)
            except:
                errors.append("Invalid cron schedule expression")
        
        # Validation des fonctions
        for task in pipeline.tasks:
            if task.function not in self.task_registry:
                warnings.append(f"Task function {task.function} not registered")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _has_cycles(self, tasks: List[PipelineTask]) -> bool:
        """Détecte les cycles dans les dépendances des tâches"""
        
        # Créer un graphe des dépendances
        graph = {}
        for task in tasks:
            graph[task.task_id] = task.dependencies
        
        # DFS pour détecter les cycles
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False
    
    async def trigger_pipeline(
        self,
        pipeline_id: str,
        context: Optional[Dict[str, Any]] = None,
        triggered_by: str = "manual"
    ) -> Dict[str, Any]:
        """Déclenche l'exécution d'un pipeline"""
        
        try:
            if pipeline_id not in self.pipelines:
                return {
                    'success': False,
                    'error': f'Pipeline {pipeline_id} not found'
                }
            
            pipeline = self.pipelines[pipeline_id]
            
            if not pipeline.enabled:
                return {
                    'success': False,
                    'error': f'Pipeline {pipeline_id} is disabled'
                }
            
            # Vérifier les exécutions concurrentes
            active_runs_count = sum(
                1 for run in self.active_runs.values()
                if run.pipeline_id == pipeline_id and run.status == PipelineStatus.RUNNING
            )
            
            if active_runs_count >= pipeline.max_concurrent_runs:
                return {
                    'success': False,
                    'error': f'Maximum concurrent runs ({pipeline.max_concurrent_runs}) reached'
                }
            
            # Créer une nouvelle exécution
            run_id = str(uuid.uuid4())
            pipeline_run = PipelineRun(
                run_id=run_id,
                pipeline_id=pipeline_id,
                status=PipelineStatus.PENDING,
                start_time=datetime.utcnow(),
                triggered_by=triggered_by,
                context=context or {}
            )
            
            self.active_runs[run_id] = pipeline_run
            
            # Lancer l'exécution en arrière-plan
            asyncio.create_task(self._execute_pipeline(run_id))
            
            return {
                'success': True,
                'run_id': run_id,
                'message': f'Pipeline {pipeline_id} triggered successfully'
            }
            
        except Exception as e:
            logger.error(f"Error triggering pipeline {pipeline_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_pipeline(self, run_id: str) -> None:
        """Exécute un pipeline"""
        
        pipeline_run = self.active_runs[run_id]
        pipeline = self.pipelines[pipeline_run.pipeline_id]
        
        try:
            logger.info(f"Starting pipeline execution: {run_id}")
            
            # Marquer comme en cours
            pipeline_run.status = PipelineStatus.RUNNING
            
            # Créer le graphe d'exécution
            execution_graph = self._create_execution_graph(pipeline.tasks)
            
            # Exécuter les tâches
            await self._execute_tasks(run_id, execution_graph)
            
            # Marquer comme réussi
            pipeline_run.status = PipelineStatus.SUCCESS
            pipeline_run.end_time = datetime.utcnow()
            
            # Mettre à jour les métriques
            self._update_metrics(pipeline_run)
            
            # Envoyer notifications
            await self._send_notifications(pipeline_run, pipeline)
            
            logger.info(f"Pipeline execution completed successfully: {run_id}")
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {run_id}, error: {e}")
            
            pipeline_run.status = PipelineStatus.FAILED
            pipeline_run.end_time = datetime.utcnow()
            pipeline_run.error_message = str(e)
            
            # Mettre à jour les métriques
            self._update_metrics(pipeline_run)
            
            # Envoyer notifications d'erreur
            await self._send_notifications(pipeline_run, pipeline)
        
        finally:
            # Nettoyer les ressources si nécessaire
            await self._cleanup_pipeline_run(run_id)
    
    def _create_execution_graph(self, tasks: List[PipelineTask]) -> Dict[str, Any]:
        """Crée le graphe d'exécution des tâches"""
        
        # Trier topologiquement les tâches
        sorted_tasks = self._topological_sort(tasks)
        
        # Créer les niveaux d'exécution
        levels = []
        task_levels = {}
        
        for task in sorted_tasks:
            # Calculer le niveau de la tâche
            max_dep_level = -1
            for dep in task.dependencies:
                if dep in task_levels:
                    max_dep_level = max(max_dep_level, task_levels[dep])
            
            task_level = max_dep_level + 1
            task_levels[task.task_id] = task_level
            
            # Ajouter au niveau approprié
            while len(levels) <= task_level:
                levels.append([])
            
            levels[task_level].append(task)
        
        return {
            'levels': levels,
            'task_levels': task_levels
        }
    
    def _topological_sort(self, tasks: List[PipelineTask]) -> List[PipelineTask]:
        """Tri topologique des tâches"""
        
        # Créer un graphe des dépendances
        graph = {task.task_id: task for task in tasks}
        in_degree = {task.task_id: 0 for task in tasks}
        
        for task in tasks:
            for dep in task.dependencies:
                in_degree[task.task_id] += 1
        
        # Tri topologique avec l'algorithme de Kahn
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        sorted_tasks = []
        
        while queue:
            current_id = queue.pop(0)
            current_task = graph[current_id]
            sorted_tasks.append(current_task)
            
            # Trouver les tâches qui dépendent de celle-ci
            for task in tasks:
                if current_id in task.dependencies:
                    in_degree[task.task_id] -= 1
                    if in_degree[task.task_id] == 0:
                        queue.append(task.task_id)
        
        return sorted_tasks
    
    async def _execute_tasks(self, run_id: str, execution_graph: Dict[str, Any]) -> None:
        """Exécute les tâches selon le graphe d'exécution"""
        
        pipeline_run = self.active_runs[run_id]
        levels = execution_graph['levels']
        
        for level_index, level_tasks in enumerate(levels):
            logger.info(f"Executing level {level_index} with {len(level_tasks)} tasks")
            
            # Exécuter toutes les tâches du niveau en parallèle
            level_results = await asyncio.gather(*[
                self._execute_task(run_id, task)
                for task in level_tasks
            ], return_exceptions=True)
            
            # Vérifier les résultats
            for i, result in enumerate(level_results):
                task = level_tasks[i]
                
                if isinstance(result, Exception):
                    raise Exception(f"Task {task.task_id} failed: {str(result)}")
                
                pipeline_run.task_results[task.task_id] = result
    
    async def _execute_task(self, run_id: str, task: PipelineTask) -> Any:
        """Exécute une tâche individuelle"""
        
        pipeline_run = self.active_runs[run_id]
        
        try:
            logger.info(f"Executing task {task.task_id} in run {run_id}")
            
            # Préparer le contexte d'exécution
            task_context = {
                'run_id': run_id,
                'pipeline_id': pipeline_run.pipeline_id,
                'task_id': task.task_id,
                'context': pipeline_run.context,
                'parameters': task.parameters
            }
            
            # Sélectionner l'exécuteur approprié
            executor_type = task.resources.get('executor', 'python')
            executor = self.executors.get(executor_type, self.executors['python'])
            
            # Exécuter avec retry et timeout
            result = await self._execute_with_retry(
                task, executor, task_context
            )
            
            logger.info(f"Task {task.task_id} completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            raise
    
    async def _execute_with_retry(
        self,
        task: PipelineTask,
        executor: Callable,
        context: Dict[str, Any]
    ) -> Any:
        """Exécute une tâche avec retry et timeout"""
        
        last_exception = None
        
        for attempt in range(task.retry_count + 1):
            try:
                # Exécuter avec timeout
                result = await asyncio.wait_for(
                    executor(task, context),
                    timeout=task.timeout
                )
                
                return result
                
            except asyncio.TimeoutError:
                last_exception = Exception(f"Task {task.task_id} timed out after {task.timeout}s")
                logger.warning(f"Task {task.task_id} timed out, attempt {attempt + 1}")
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Task {task.task_id} failed, attempt {attempt + 1}: {e}")
                
                if attempt < task.retry_count:
                    # Attendre avant de réessayer
                    await asyncio.sleep(2 ** attempt)  # Backoff exponentiel
        
        raise last_exception
    
    def _create_spark_executor(self) -> Callable:
        """Crée un exécuteur pour tâches Spark"""
        
        async def spark_executor(task: PipelineTask, context: Dict[str, Any]) -> Any:
            # Placeholder pour exécution Spark
            logger.info(f"Executing Spark task: {task.function}")
            
            # En production, ici on lancerait un job Spark
            await asyncio.sleep(1)  # Simuler traitement
            
            return {
                'executor': 'spark',
                'status': 'completed',
                'output': f'Spark job {task.function} completed'
            }
        
        return spark_executor
    
    def _create_kafka_executor(self) -> Callable:
        """Crée un exécuteur pour tâches Kafka"""
        
        async def kafka_executor(task: PipelineTask, context: Dict[str, Any]) -> Any:
            # Placeholder pour exécution Kafka
            logger.info(f"Executing Kafka task: {task.function}")
            
            # En production, ici on interagirait avec Kafka
            await asyncio.sleep(0.5)  # Simuler traitement
            
            return {
                'executor': 'kafka',
                'status': 'completed',
                'output': f'Kafka task {task.function} completed'
            }
        
        return kafka_executor
    
    def _create_flink_executor(self) -> Callable:
        """Crée un exécuteur pour tâches Flink"""
        
        async def flink_executor(task: PipelineTask, context: Dict[str, Any]) -> Any:
            # Placeholder pour exécution Flink
            logger.info(f"Executing Flink task: {task.function}")
            
            # En production, ici on lancerait un job Flink
            await asyncio.sleep(1.5)  # Simuler traitement
            
            return {
                'executor': 'flink',
                'status': 'completed',
                'output': f'Flink job {task.function} completed'
            }
        
        return flink_executor
    
    def _create_python_executor(self) -> Callable:
        """Crée un exécuteur pour tâches Python"""
        
        async def python_executor(task: PipelineTask, context: Dict[str, Any]) -> Any:
            # Exécution de fonction Python
            if task.function in self.task_registry:
                function = self.task_registry[task.function]
                
                # Exécuter la fonction
                if asyncio.iscoroutinefunction(function):
                    result = await function(context)
                else:
                    result = function(context)
                
                return result
            else:
                raise Exception(f"Function {task.function} not registered")
        
        return python_executor
    
    def register_task_function(self, name: str, function: Callable) -> None:
        """Enregistre une fonction de tâche"""
        self.task_registry[name] = function
        logger.info(f"Task function {name} registered")
    
    async def start_scheduler(self) -> None:
        """Démarre le scheduler pour exécutions automatiques"""
        
        self.scheduler_running = True
        logger.info("Pipeline scheduler started")
        
        while self.scheduler_running:
            try:
                await self._check_scheduled_pipelines()
                await asyncio.sleep(60)  # Vérifier chaque minute
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def _check_scheduled_pipelines(self) -> None:
        """Vérifie les pipelines à exécuter selon leur schedule"""
        
        current_time = datetime.utcnow()
        
        for pipeline_id, pipeline in self.pipelines.items():
            if not pipeline.schedule or not pipeline.enabled:
                continue
            
            try:
                # Vérifier si le pipeline doit être exécuté
                cron = croniter(pipeline.schedule, current_time)
                next_run = cron.get_prev(datetime)
                
                # Vérifier si une exécution est due (dans la dernière minute)
                if (current_time - next_run).total_seconds() < 60:
                    # Vérifier qu'il n'y a pas déjà une exécution récente
                    recent_runs = [
                        run for run in self.active_runs.values()
                        if (run.pipeline_id == pipeline_id and
                            run.triggered_by == "scheduler" and
                            (current_time - run.start_time).total_seconds() < 60)
                    ]
                    
                    if not recent_runs:
                        await self.trigger_pipeline(
                            pipeline_id,
                            triggered_by="scheduler"
                        )
                        
            except Exception as e:
                logger.error(f"Error checking schedule for pipeline {pipeline_id}: {e}")
    
    def stop_scheduler(self) -> None:
        """Arrête le scheduler"""
        self.scheduler_running = False
        logger.info("Pipeline scheduler stopped")
    
    async def _send_notifications(self, pipeline_run: PipelineRun, pipeline: Pipeline) -> None:
        """Envoie des notifications sur l'état du pipeline"""
        
        notification_config = pipeline.notification_config
        
        if not notification_config:
            return
        
        try:
            # Préparer le message
            if pipeline_run.status == PipelineStatus.SUCCESS:
                subject = f"Pipeline {pipeline.name} completed successfully"
                message = f"Run {pipeline_run.run_id} completed in {(pipeline_run.end_time - pipeline_run.start_time).total_seconds():.1f}s"
            else:
                subject = f"Pipeline {pipeline.name} failed"
                message = f"Run {pipeline_run.run_id} failed: {pipeline_run.error_message}"
            
            # Envoyer selon la configuration
            if 'email' in notification_config:
                await self._send_email_notification(
                    notification_config['email'],
                    subject,
                    message
                )
            
            if 'webhook' in notification_config:
                await self._send_webhook_notification(
                    notification_config['webhook'],
                    pipeline_run,
                    pipeline
                )
                
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
    
    async def _send_email_notification(
        self,
        email_config: Dict[str, Any],
        subject: str,
        message: str
    ) -> None:
        """Envoie une notification par email"""
        # Placeholder pour l'envoi d'email
        logger.info(f"Email notification: {subject}")
    
    async def _send_webhook_notification(
        self,
        webhook_config: Dict[str, Any],
        pipeline_run: PipelineRun,
        pipeline: Pipeline
    ) -> None:
        """Envoie une notification via webhook"""
        # Placeholder pour l'envoi de webhook
        logger.info(f"Webhook notification for run {pipeline_run.run_id}")
    
    def _update_metrics(self, pipeline_run: PipelineRun) -> None:
        """Met à jour les métriques de performance"""
        
        self.metrics['total_runs'] += 1
        
        if pipeline_run.status == PipelineStatus.SUCCESS:
            self.metrics['successful_runs'] += 1
        elif pipeline_run.status == PipelineStatus.FAILED:
            self.metrics['failed_runs'] += 1
        
        # Calculer temps d'exécution moyen
        if pipeline_run.end_time:
            execution_time = (pipeline_run.end_time - pipeline_run.start_time).total_seconds()
            
            current_avg = self.metrics['avg_execution_time']
            total_runs = self.metrics['total_runs']
            
            self.metrics['avg_execution_time'] = (
                (current_avg * (total_runs - 1) + execution_time) / total_runs
            )
    
    async def _cleanup_pipeline_run(self, run_id: str) -> None:
        """Nettoie les ressources d'une exécution de pipeline"""
        
        try:
            # Garder l'historique des exécutions terminées
            # mais limiter le nombre
            if len(self.active_runs) > 1000:
                # Supprimer les plus anciennes exécutions terminées
                completed_runs = [
                    (run_id, run) for run_id, run in self.active_runs.items()
                    if run.status in [PipelineStatus.SUCCESS, PipelineStatus.FAILED]
                ]
                
                completed_runs.sort(key=lambda x: x[1].start_time)
                
                # Garder seulement les 800 plus récentes
                to_remove = completed_runs[:-800]
                for run_id_to_remove, _ in to_remove:
                    del self.active_runs[run_id_to_remove]
                    
        except Exception as e:
            logger.error(f"Error cleaning up pipeline run {run_id}: {e}")
    
    async def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Obtient le statut d'un pipeline"""
        
        if pipeline_id not in self.pipelines:
            return {
                'error': f'Pipeline {pipeline_id} not found'
            }
        
        pipeline = self.pipelines[pipeline_id]
        
        # Obtenir les exécutions récentes
        recent_runs = [
            {
                'run_id': run.run_id,
                'status': run.status.value,
                'start_time': run.start_time.isoformat(),
                'end_time': run.end_time.isoformat() if run.end_time else None,
                'triggered_by': run.triggered_by
            }
            for run in self.active_runs.values()
            if run.pipeline_id == pipeline_id
        ]
        
        recent_runs.sort(key=lambda x: x['start_time'], reverse=True)
        
        return {
            'pipeline_id': pipeline_id,
            'name': pipeline.name,
            'enabled': pipeline.enabled,
            'schedule': pipeline.schedule,
            'recent_runs': recent_runs[:10],  # 10 dernières exécutions
            'metrics': self._get_pipeline_metrics(pipeline_id)
        }
    
    def _get_pipeline_metrics(self, pipeline_id: str) -> Dict[str, Any]:
        """Calcule les métriques pour un pipeline spécifique"""
        
        pipeline_runs = [
            run for run in self.active_runs.values()
            if run.pipeline_id == pipeline_id
        ]
        
        if not pipeline_runs:
            return {}
        
        total_runs = len(pipeline_runs)
        successful_runs = sum(1 for run in pipeline_runs if run.status == PipelineStatus.SUCCESS)
        failed_runs = sum(1 for run in pipeline_runs if run.status == PipelineStatus.FAILED)
        
        # Temps d'exécution moyen
        completed_runs = [
            run for run in pipeline_runs
            if run.end_time and run.status in [PipelineStatus.SUCCESS, PipelineStatus.FAILED]
        ]
        
        avg_execution_time = 0
        if completed_runs:
            total_time = sum(
                (run.end_time - run.start_time).total_seconds()
                for run in completed_runs
            )
            avg_execution_time = total_time / len(completed_runs)
        
        return {
            'total_runs': total_runs,
            'successful_runs': successful_runs,
            'failed_runs': failed_runs,
            'success_rate': successful_runs / total_runs if total_runs > 0 else 0,
            'avg_execution_time': avg_execution_time
        }
    
    async def pause_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Met en pause un pipeline"""
        
        if pipeline_id not in self.pipelines:
            return {
                'success': False,
                'error': f'Pipeline {pipeline_id} not found'
            }
        
        self.pipelines[pipeline_id].enabled = False
        
        return {
            'success': True,
            'message': f'Pipeline {pipeline_id} paused'
        }
    
    async def resume_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Reprend un pipeline mis en pause"""
        
        if pipeline_id not in self.pipelines:
            return {
                'success': False,
                'error': f'Pipeline {pipeline_id} not found'
            }
        
        self.pipelines[pipeline_id].enabled = True
        
        return {
            'success': True,
            'message': f'Pipeline {pipeline_id} resumed'
        }
    
    async def cancel_run(self, run_id: str) -> Dict[str, Any]:
        """Annule une exécution de pipeline"""
        
        if run_id not in self.active_runs:
            return {
                'success': False,
                'error': f'Run {run_id} not found'
            }
        
        pipeline_run = self.active_runs[run_id]
        
        if pipeline_run.status != PipelineStatus.RUNNING:
            return {
                'success': False,
                'error': f'Run {run_id} is not currently running'
            }
        
        pipeline_run.status = PipelineStatus.CANCELLED
        pipeline_run.end_time = datetime.utcnow()
        
        return {
            'success': True,
            'message': f'Run {run_id} cancelled'
        }


# Instance globale du service
data_pipeline_orchestrator = DataPipelineOrchestrator()