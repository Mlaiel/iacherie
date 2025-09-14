#!/usr/bin/env python3
"""
🔄 AI Pipeline Orchestrator Service - Enterprise Grade
Orchestration complète des pipelines IA pour Ainflue

© Fahed Mlaiel 2024-2025 - Propriété intellectuelle stricte
Architecture microservices enterprise - Niveau production
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
import traceback

# Configuration logging enterprise
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    """Statuts des pipelines IA"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class TaskType(Enum):
    """Types de tâches IA"""
    INFERENCE = "inference"
    TRAINING = "training"
    VALIDATION = "validation"
    PREPROCESSING = "preprocessing"
    POSTPROCESSING = "postprocessing"
    OPTIMIZATION = "optimization"

@dataclass
class PipelineTask:
    """Tâche dans un pipeline IA"""
    task_id: str
    task_type: TaskType
    name: str
    service_endpoint: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    timeout: int = 300
    retry_count: int = 3
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class Pipeline:
    """Pipeline IA complet"""
    pipeline_id: str
    name: str
    description: str
    tasks: List[PipelineTask]
    status: PipelineStatus
    created_by: str
    priority: int = 1
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class AIPipelineOrchestrator:
    """
    🔄 Orchestrateur de pipelines IA enterprise
    Gestion complète des workflows IA distribués
    """
    
    def __init__(self):
        """Initialisation de l'orchestrateur"""
        self.pipelines: Dict[str, Pipeline] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.max_concurrent_pipelines = 50
        self.pipeline_queue: List[str] = []
        
        # Métriques enterprise
        self.metrics = {
            'total_pipelines': 0,
            'successful_pipelines': 0,
            'failed_pipelines': 0,
            'average_execution_time': 0.0,
            'active_pipelines': 0
        }
        
        logger.info("🔄 AI Pipeline Orchestrator initialisé - Mode Enterprise")
    
    async def create_pipeline(
        self,
        name: str,
        description: str,
        tasks: List[Dict[str, Any]],
        created_by: str,
        priority: int = 1
    ) -> str:
        """
        Créer un nouveau pipeline IA
        
        Args:
            name: Nom du pipeline
            description: Description du pipeline
            tasks: Liste des tâches à exécuter
            created_by: Créateur du pipeline
            priority: Priorité d'exécution (1-10)
        
        Returns:
            ID du pipeline créé
        """
        try:
            pipeline_id = f"pipeline_{uuid.uuid4().hex[:8]}"
            
            # Conversion des tâches
            pipeline_tasks = []
            for task_data in tasks:
                task = PipelineTask(
                    task_id=f"task_{uuid.uuid4().hex[:8]}",
                    task_type=TaskType(task_data['type']),
                    name=task_data['name'],
                    service_endpoint=task_data['endpoint'],
                    parameters=task_data.get('parameters', {}),
                    dependencies=task_data.get('dependencies', []),
                    timeout=task_data.get('timeout', 300),
                    retry_count=task_data.get('retry_count', 3)
                )
                pipeline_tasks.append(task)
            
            # Validation des dépendances
            await self._validate_dependencies(pipeline_tasks)
            
            # Création du pipeline
            pipeline = Pipeline(
                pipeline_id=pipeline_id,
                name=name,
                description=description,
                tasks=pipeline_tasks,
                status=PipelineStatus.PENDING,
                created_by=created_by,
                priority=priority
            )
            
            self.pipelines[pipeline_id] = pipeline
            self.metrics['total_pipelines'] += 1
            
            # Ajout à la queue selon la priorité
            self._add_to_queue(pipeline_id, priority)
            
            logger.info(f"✅ Pipeline créé: {pipeline_id} - {name}")
            return pipeline_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création pipeline: {e}")
            raise
    
    async def execute_pipeline(self, pipeline_id: str) -> bool:
        """
        Exécuter un pipeline IA
        
        Args:
            pipeline_id: ID du pipeline à exécuter
        
        Returns:
            True si succès, False sinon
        """
        try:
            if pipeline_id not in self.pipelines:
                raise ValueError(f"Pipeline {pipeline_id} introuvable")
            
            pipeline = self.pipelines[pipeline_id]
            
            if pipeline.status != PipelineStatus.PENDING:
                logger.warning(f"⚠️ Pipeline {pipeline_id} déjà traité")
                return False
            
            # Vérification de la capacité
            if self.metrics['active_pipelines'] >= self.max_concurrent_pipelines:
                logger.warning(f"⚠️ Capacité maximale atteinte, pipeline {pipeline_id} en queue")
                return False
            
            # Démarrage de l'exécution
            pipeline.status = PipelineStatus.RUNNING
            pipeline.started_at = datetime.utcnow()
            self.metrics['active_pipelines'] += 1
            
            logger.info(f"🚀 Exécution pipeline: {pipeline_id}")
            
            # Exécution des tâches
            success = await self._execute_tasks(pipeline)
            
            # Mise à jour du statut
            pipeline.completed_at = datetime.utcnow()
            if success:
                pipeline.status = PipelineStatus.COMPLETED
                self.metrics['successful_pipelines'] += 1
                logger.info(f"✅ Pipeline complété: {pipeline_id}")
            else:
                pipeline.status = PipelineStatus.FAILED
                self.metrics['failed_pipelines'] += 1
                logger.error(f"❌ Pipeline échoué: {pipeline_id}")
            
            self.metrics['active_pipelines'] -= 1
            
            # Calcul du temps d'exécution moyen
            execution_time = (pipeline.completed_at - pipeline.started_at).total_seconds()
            self._update_average_execution_time(execution_time)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution pipeline {pipeline_id}: {e}")
            if pipeline_id in self.pipelines:
                self.pipelines[pipeline_id].status = PipelineStatus.FAILED
                self.pipelines[pipeline_id].error_message = str(e)
                self.metrics['active_pipelines'] -= 1
            return False
    
    async def _execute_tasks(self, pipeline: Pipeline) -> bool:
        """
        Exécuter les tâches d'un pipeline selon leurs dépendances
        
        Args:
            pipeline: Pipeline à exécuter
        
        Returns:
            True si toutes les tâches réussissent
        """
        try:
            # Graphe de dépendances
            task_graph = self._build_dependency_graph(pipeline.tasks)
            executed_tasks = set()
            failed_tasks = set()
            
            while len(executed_tasks) < len(pipeline.tasks):
                # Trouver les tâches prêtes à être exécutées
                ready_tasks = []
                for task in pipeline.tasks:
                    if (task.task_id not in executed_tasks and
                        task.task_id not in failed_tasks and
                        all(dep in executed_tasks for dep in task.dependencies)):
                        ready_tasks.append(task)
                
                if not ready_tasks:
                    if failed_tasks:
                        logger.error(f"❌ Tâches bloquées par échecs: {failed_tasks}")
                        return False
                    break
                
                # Exécution parallèle des tâches prêtes
                task_results = await asyncio.gather(
                    *[self._execute_task(task) for task in ready_tasks],
                    return_exceptions=True
                )
                
                # Traitement des résultats
                for task, result in zip(ready_tasks, task_results):
                    if isinstance(result, Exception):
                        logger.error(f"❌ Tâche échouée {task.task_id}: {result}")
                        failed_tasks.add(task.task_id)
                    elif result:
                        logger.info(f"✅ Tâche complétée: {task.task_id}")
                        executed_tasks.add(task.task_id)
                    else:
                        logger.error(f"❌ Tâche échouée: {task.task_id}")
                        failed_tasks.add(task.task_id)
            
            return len(failed_tasks) == 0
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution tâches: {e}")
            return False
    
    async def _execute_task(self, task: PipelineTask) -> bool:
        """
        Exécuter une tâche individuelle
        
        Args:
            task: Tâche à exécuter
        
        Returns:
            True si succès, False sinon
        """
        retries = 0
        while retries <= task.retry_count:
            try:
                logger.info(f"🔄 Exécution tâche: {task.name} (tentative {retries + 1})")
                
                # Simulation d'appel au service
                # En production, ici on appellerait le vrai service
                await asyncio.sleep(1)  # Simulation temps d'exécution
                
                # Simulation de succès aléatoire pour test
                import random
                if random.random() > 0.1:  # 90% de succès
                    return True
                else:
                    raise Exception("Erreur simulée")
                
            except Exception as e:
                retries += 1
                if retries <= task.retry_count:
                    wait_time = 2 ** retries  # Backoff exponentiel
                    logger.warning(f"⚠️ Retry tâche {task.name} dans {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ Tâche {task.name} échouée après {task.retry_count} tentatives")
                    return False
        
        return False
    
    async def pause_pipeline(self, pipeline_id: str) -> bool:
        """
        Mettre en pause un pipeline
        
        Args:
            pipeline_id: ID du pipeline à pauser
        
        Returns:
            True si succès
        """
        try:
            if pipeline_id not in self.pipelines:
                return False
            
            pipeline = self.pipelines[pipeline_id]
            if pipeline.status == PipelineStatus.RUNNING:
                pipeline.status = PipelineStatus.PAUSED
                logger.info(f"⏸️ Pipeline mis en pause: {pipeline_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur pause pipeline: {e}")
            return False
    
    async def cancel_pipeline(self, pipeline_id: str) -> bool:
        """
        Annuler un pipeline
        
        Args:
            pipeline_id: ID du pipeline à annuler
        
        Returns:
            True si succès
        """
        try:
            if pipeline_id not in self.pipelines:
                return False
            
            pipeline = self.pipelines[pipeline_id]
            pipeline.status = PipelineStatus.CANCELLED
            
            # Nettoyage des tâches en cours
            if pipeline_id in self.running_tasks:
                self.running_tasks[pipeline_id].cancel()
                del self.running_tasks[pipeline_id]
            
            logger.info(f"❌ Pipeline annulé: {pipeline_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur annulation pipeline: {e}")
            return False
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtenir le statut d'un pipeline
        
        Args:
            pipeline_id: ID du pipeline
        
        Returns:
            Statut du pipeline ou None
        """
        try:
            if pipeline_id not in self.pipelines:
                return None
            
            pipeline = self.pipelines[pipeline_id]
            
            return {
                'pipeline_id': pipeline.pipeline_id,
                'name': pipeline.name,
                'status': pipeline.status.value,
                'created_at': pipeline.created_at.isoformat(),
                'started_at': pipeline.started_at.isoformat() if pipeline.started_at else None,
                'completed_at': pipeline.completed_at.isoformat() if pipeline.completed_at else None,
                'task_count': len(pipeline.tasks),
                'error_message': pipeline.error_message
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statut: {e}")
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtenir les métriques de l'orchestrateur
        
        Returns:
            Métriques enterprise
        """
        return {
            **self.metrics,
            'queue_length': len(self.pipeline_queue),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _validate_dependencies(self, tasks: List[PipelineTask]) -> None:
        """Valider les dépendances des tâches"""
        task_ids = {task.task_id for task in tasks}
        
        for task in tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    raise ValueError(f"Dépendance invalide: {dep} pour tâche {task.task_id}")
    
    def _build_dependency_graph(self, tasks: List[PipelineTask]) -> Dict[str, List[str]]:
        """Construire le graphe de dépendances"""
        graph = {}
        for task in tasks:
            graph[task.task_id] = task.dependencies
        return graph
    
    def _add_to_queue(self, pipeline_id: str, priority: int) -> None:
        """Ajouter un pipeline à la queue selon la priorité"""
        # Insertion selon la priorité (plus haute priorité = plus bas chiffre)
        inserted = False
        for i, existing_id in enumerate(self.pipeline_queue):
            if self.pipelines[existing_id].priority > priority:
                self.pipeline_queue.insert(i, pipeline_id)
                inserted = True
                break
        
        if not inserted:
            self.pipeline_queue.append(pipeline_id)
    
    def _update_average_execution_time(self, execution_time: float) -> None:
        """Mettre à jour le temps d'exécution moyen"""
        current_avg = self.metrics['average_execution_time']
        total_completed = self.metrics['successful_pipelines'] + self.metrics['failed_pipelines']
        
        if total_completed > 1:
            self.metrics['average_execution_time'] = (
                (current_avg * (total_completed - 1) + execution_time) / total_completed
            )
        else:
            self.metrics['average_execution_time'] = execution_time

# Instance globale pour l'orchestrateur
ai_pipeline_orchestrator = AIPipelineOrchestrator()

# API publique
__all__ = [
    'AIPipelineOrchestrator',
    'Pipeline',
    'PipelineTask',
    'PipelineStatus',
    'TaskType',
    'ai_pipeline_orchestrator'
]

if __name__ == "__main__":
    # Test de démonstration
    async def demo():
        orchestrator = AIPipelineOrchestrator()
        
        # Création d'un pipeline de test
        tasks = [
            {
                'type': 'preprocessing',
                'name': 'Nettoyage données',
                'endpoint': '/api/preprocess',
                'parameters': {'format': 'json'},
                'dependencies': []
            },
            {
                'type': 'training',
                'name': 'Entraînement modèle',
                'endpoint': '/api/train',
                'parameters': {'epochs': 10},
                'dependencies': ['task_preprocessing']
            },
            {
                'type': 'validation',
                'name': 'Validation modèle',
                'endpoint': '/api/validate',
                'parameters': {'split': 0.2},
                'dependencies': ['task_training']
            }
        ]
        
        pipeline_id = await orchestrator.create_pipeline(
            name="Pipeline Demo IA",
            description="Pipeline de démonstration",
            tasks=tasks,
            created_by="system"
        )
        
        success = await orchestrator.execute_pipeline(pipeline_id)
        status = orchestrator.get_pipeline_status(pipeline_id)
        metrics = orchestrator.get_metrics()
        
        print(f"Pipeline: {pipeline_id}")
        print(f"Succès: {success}")
        print(f"Statut: {status}")
        print(f"Métriques: {metrics}")
    
    # Exécution du test
    asyncio.run(demo())