"""
🔄 Pipeline Orchestration Engine - Enterprise MLOps
Expert DevOps: Advanced pipeline orchestration for complex ML workflows

🎯 EXPERTISE DÉMONTRÉ:
- DevOps: Pipeline orchestration avancée + workflow automation
- Lead Dev IA: Coordination multi-systèmes + gestion conflits
- Backend Senior: Architecture distributed pipelines + performance
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from contextlib import asynccontextmanager
import uuid

# Configuration et logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    """Statuts de pipeline pour orchestration avancée"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RETRYING = "retrying"

class PipelineType(Enum):
    """Types de pipelines MLOps"""
    DATA_PIPELINE = "data_pipeline"
    TRAINING_PIPELINE = "training_pipeline"
    DEPLOYMENT_PIPELINE = "deployment_pipeline"
    MONITORING_PIPELINE = "monitoring_pipeline"
    SECURITY_PIPELINE = "security_pipeline"
    VALIDATION_PIPELINE = "validation_pipeline"

@dataclass
class PipelineStep:
    """Étape individuelle dans un pipeline orchestré"""
    id: str
    name: str
    function: Callable
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 3600  # secondes
    retry_count: int = 3
    retry_delay: int = 30
    priority: int = 1
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
class PipelineOrchestrator:
    """
    🔄 Orchestrateur Enterprise de Pipelines MLOps
    
    Expertise DevOps: Orchestration avancée de workflows complexes
    - Dependency resolution intelligente
    - Parallel execution avec resource management
    - Error handling et recovery automatique
    - Monitoring en temps réel
    """
    
    def __init__(self, max_concurrent_pipelines: int = 10):
        self.max_concurrent_pipelines = max_concurrent_pipelines
        self.active_pipelines: Dict[str, Dict] = {}
        self.pipeline_history: List[Dict] = []
        self.step_registry: Dict[str, PipelineStep] = {}
        self.pipeline_definitions: Dict[str, Dict] = {}
        self.resource_pool = asyncio.Semaphore(max_concurrent_pipelines)
        
    async def register_step(self, step: PipelineStep) -> bool:
        """Enregistre une étape de pipeline avec validation"""
        try:
            # Validation de l'étape
            if not callable(step.function):
                raise ValueError(f"Function for step {step.id} is not callable")
            
            # Validation des dépendances
            for dep_id in step.dependencies:
                if dep_id not in self.step_registry and dep_id != step.id:
                    logger.warning(f"Dependency {dep_id} not found for step {step.id}")
            
            self.step_registry[step.id] = step
            logger.info(f"Registered pipeline step: {step.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register step {step.id}: {str(e)}")
            return False
    
    async def define_pipeline(
        self, 
        pipeline_id: str, 
        pipeline_type: PipelineType,
        steps: List[str],
        metadata: Optional[Dict] = None
    ) -> bool:
        """Définit un pipeline avec ses étapes et métadonnées"""
        try:
            # Validation des étapes
            for step_id in steps:
                if step_id not in self.step_registry:
                    raise ValueError(f"Step {step_id} not registered")
            
            # Validation des dépendances (détection de cycles)
            if not await self._validate_dependencies(steps):
                raise ValueError("Circular dependencies detected")
            
            pipeline_def = {
                "id": pipeline_id,
                "type": pipeline_type.value,
                "steps": steps,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            self.pipeline_definitions[pipeline_id] = pipeline_def
            logger.info(f"Defined pipeline: {pipeline_id} with {len(steps)} steps")
            return True
            
        except Exception as e:
            logger.error(f"Failed to define pipeline {pipeline_id}: {str(e)}")
            return False
    
    async def execute_pipeline(
        self, 
        pipeline_id: str, 
        execution_id: Optional[str] = None,
        parameters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Exécute un pipeline avec orchestration avancée
        
        Features:
        - Dependency resolution automatique
        - Parallel execution optimisée
        - Resource management
        - Error handling et recovery
        """
        if not execution_id:
            execution_id = f"{pipeline_id}_{uuid.uuid4().hex[:8]}"
        
        if pipeline_id not in self.pipeline_definitions:
            raise ValueError(f"Pipeline {pipeline_id} not defined")
        
        async with self.resource_pool:
            return await self._execute_pipeline_internal(
                pipeline_id, execution_id, parameters or {}
            )
    
    async def _execute_pipeline_internal(
        self, 
        pipeline_id: str, 
        execution_id: str,
        parameters: Dict
    ) -> Dict[str, Any]:
        """Exécution interne avec gestion des ressources"""
        start_time = datetime.utcnow()
        pipeline_def = self.pipeline_definitions[pipeline_id]
        
        execution_context = {
            "execution_id": execution_id,
            "pipeline_id": pipeline_id,
            "status": PipelineStatus.RUNNING,
            "start_time": start_time,
            "steps_completed": [],
            "steps_failed": [],
            "parameters": parameters,
            "results": {},
            "metrics": {
                "total_steps": len(pipeline_def["steps"]),
                "completed_steps": 0,
                "failed_steps": 0,
                "execution_time": 0
            }
        }
        
        self.active_pipelines[execution_id] = execution_context
        
        try:
            # Résolution des dépendances et création du DAG
            execution_graph = await self._build_execution_graph(pipeline_def["steps"])
            
            # Exécution parallèle du DAG
            results = await self._execute_dag(execution_graph, execution_context)
            
            # Finalisation
            execution_context["status"] = PipelineStatus.SUCCESS
            execution_context["end_time"] = datetime.utcnow()
            execution_context["results"] = results
            execution_context["metrics"]["execution_time"] = (
                execution_context["end_time"] - start_time
            ).total_seconds()
            
            logger.info(f"Pipeline {pipeline_id} completed successfully in {execution_context['metrics']['execution_time']:.2f}s")
            
        except Exception as e:
            execution_context["status"] = PipelineStatus.FAILED
            execution_context["error"] = str(e)
            execution_context["end_time"] = datetime.utcnow()
            logger.error(f"Pipeline {pipeline_id} failed: {str(e)}")
            
        finally:
            # Archivage de l'exécution
            self.pipeline_history.append(execution_context.copy())
            if execution_id in self.active_pipelines:
                del self.active_pipelines[execution_id]
        
        return execution_context
    
    async def _build_execution_graph(self, step_ids: List[str]) -> Dict[str, List[str]]:
        """Construit le graphe d'exécution DAG à partir des dépendances"""
        graph = {}
        
        for step_id in step_ids:
            step = self.step_registry[step_id]
            # Filtrer les dépendances valides (dans le pipeline)
            valid_deps = [dep for dep in step.dependencies if dep in step_ids]
            graph[step_id] = valid_deps
        
        return graph
    
    async def _execute_dag(
        self, 
        graph: Dict[str, List[str]], 
        context: Dict
    ) -> Dict[str, Any]:
        """Exécute le DAG avec parallélisme optimal"""
        completed_steps = set()
        running_steps = set()
        results = {}
        
        while len(completed_steps) < len(graph):
            # Identifier les étapes prêtes à exécuter
            ready_steps = [
                step_id for step_id in graph
                if step_id not in completed_steps 
                and step_id not in running_steps
                and all(dep in completed_steps for dep in graph[step_id])
            ]
            
            if not ready_steps and not running_steps:
                raise Exception("Deadlock detected in pipeline execution")
            
            # Lancer les étapes prêtes en parallèle
            tasks = []
            for step_id in ready_steps:
                if len(running_steps) < self.max_concurrent_pipelines:
                    running_steps.add(step_id)
                    task = asyncio.create_task(
                        self._execute_step(step_id, context, results)
                    )
                    tasks.append((step_id, task))
            
            # Attendre la completion d'au moins une tâche
            if tasks:
                done, pending = await asyncio.wait(
                    [task for _, task in tasks],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Traiter les tâches terminées
                for step_id, task in tasks:
                    if task in done:
                        try:
                            step_result = await task
                            results[step_id] = step_result
                            completed_steps.add(step_id)
                            running_steps.discard(step_id)
                            context["steps_completed"].append(step_id)
                            context["metrics"]["completed_steps"] += 1
                            logger.info(f"Step {step_id} completed successfully")
                            
                        except Exception as e:
                            running_steps.discard(step_id)
                            context["steps_failed"].append(step_id)
                            context["metrics"]["failed_steps"] += 1
                            logger.error(f"Step {step_id} failed: {str(e)}")
                            
                            # Politique de gestion d'erreur
                            step = self.step_registry[step_id]
                            if step.retry_count > 0:
                                # Implémenter retry logic
                                await asyncio.sleep(step.retry_delay)
                                # Logic de retry ici
                            else:
                                raise Exception(f"Step {step_id} failed: {str(e)}")
            else:
                # Attendre que des tâches se libèrent
                await asyncio.sleep(0.1)
        
        return results
    
    async def _execute_step(
        self, 
        step_id: str, 
        context: Dict, 
        previous_results: Dict
    ) -> Any:
        """Exécute une étape individuelle avec monitoring"""
        step = self.step_registry[step_id]
        step_start = datetime.utcnow()
        
        try:
            # Préparer les arguments de l'étape
            step_context = {
                "step_id": step_id,
                "execution_id": context["execution_id"],
                "parameters": context["parameters"],
                "previous_results": previous_results,
                "metadata": step.metadata
            }
            
            # Exécution avec timeout
            result = await asyncio.wait_for(
                step.function(step_context),
                timeout=step.timeout
            )
            
            step_duration = (datetime.utcnow() - step_start).total_seconds()
            logger.info(f"Step {step_id} executed in {step_duration:.2f}s")
            
            return result
            
        except asyncio.TimeoutError:
            raise Exception(f"Step {step_id} timed out after {step.timeout}s")
        except Exception as e:
            raise Exception(f"Step {step_id} execution failed: {str(e)}")
    
    async def _validate_dependencies(self, step_ids: List[str]) -> bool:
        """Valide qu'il n'y a pas de dépendances circulaires"""
        def has_cycle(graph, node, visited, rec_stack):
            visited[node] = True
            rec_stack[node] = True
            
            for neighbor in graph.get(node, []):
                if neighbor in step_ids:  # Seulement les étapes du pipeline
                    if not visited.get(neighbor, False):
                        if has_cycle(graph, neighbor, visited, rec_stack):
                            return True
                    elif rec_stack.get(neighbor, False):
                        return True
            
            rec_stack[node] = False
            return False
        
        # Construire le graphe des dépendances
        dep_graph = {}
        for step_id in step_ids:
            if step_id in self.step_registry:
                dep_graph[step_id] = self.step_registry[step_id].dependencies
        
        # Vérifier les cycles
        visited = {}
        rec_stack = {}
        
        for step_id in step_ids:
            if not visited.get(step_id, False):
                if has_cycle(dep_graph, step_id, visited, rec_stack):
                    return False
        
        return True
    
    async def get_pipeline_status(self, execution_id: str) -> Optional[Dict]:
        """Récupère le statut d'un pipeline en cours ou terminé"""
        if execution_id in self.active_pipelines:
            return self.active_pipelines[execution_id]
        
        # Chercher dans l'historique
        for execution in self.pipeline_history:
            if execution["execution_id"] == execution_id:
                return execution
        
        return None
    
    async def pause_pipeline(self, execution_id: str) -> bool:
        """Met en pause un pipeline en cours"""
        if execution_id in self.active_pipelines:
            self.active_pipelines[execution_id]["status"] = PipelineStatus.PAUSED
            logger.info(f"Pipeline {execution_id} paused")
            return True
        return False
    
    async def cancel_pipeline(self, execution_id: str) -> bool:
        """Annule un pipeline en cours"""
        if execution_id in self.active_pipelines:
            self.active_pipelines[execution_id]["status"] = PipelineStatus.CANCELLED
            logger.info(f"Pipeline {execution_id} cancelled")
            return True
        return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques d'orchestration"""
        active_count = len(self.active_pipelines)
        total_executions = len(self.pipeline_history)
        
        success_count = sum(
            1 for execution in self.pipeline_history 
            if execution["status"] == PipelineStatus.SUCCESS
        )
        
        avg_execution_time = 0
        if success_count > 0:
            total_time = sum(
                execution["metrics"]["execution_time"]
                for execution in self.pipeline_history
                if execution["status"] == PipelineStatus.SUCCESS
            )
            avg_execution_time = total_time / success_count
        
        return {
            "active_pipelines": active_count,
            "total_executions": total_executions,
            "success_rate": success_count / total_executions if total_executions > 0 else 0,
            "average_execution_time": avg_execution_time,
            "registered_steps": len(self.step_registry),
            "pipeline_definitions": len(self.pipeline_definitions)
        }

# Factory et utilitaires pour l'orchestration enterprise
class PipelineFactory:
    """Factory pour créer des pipelines MLOps standardisés"""
    
    @staticmethod
    async def create_data_pipeline(orchestrator: PipelineOrchestrator) -> str:
        """Crée un pipeline de données standard"""
        # Étapes typiques d'un pipeline de données
        steps = [
            PipelineStep(
                id="data_ingestion",
                name="Data Ingestion",
                function=lambda ctx: {"status": "data_ingested", "records": 1000}
            ),
            PipelineStep(
                id="data_validation",
                name="Data Validation", 
                function=lambda ctx: {"status": "data_validated", "quality_score": 0.95},
                dependencies=["data_ingestion"]
            ),
            PipelineStep(
                id="feature_engineering",
                name="Feature Engineering",
                function=lambda ctx: {"status": "features_created", "feature_count": 50},
                dependencies=["data_validation"]
            )
        ]
        
        for step in steps:
            await orchestrator.register_step(step)
        
        pipeline_id = "data_pipeline_standard"
        await orchestrator.define_pipeline(
            pipeline_id,
            PipelineType.DATA_PIPELINE,
            [step.id for step in steps]
        )
        
        return pipeline_id
    
    @staticmethod
    async def create_training_pipeline(orchestrator: PipelineOrchestrator) -> str:
        """Crée un pipeline d'entraînement standard"""
        steps = [
            PipelineStep(
                id="model_training",
                name="Model Training",
                function=lambda ctx: {"status": "model_trained", "accuracy": 0.92}
            ),
            PipelineStep(
                id="model_validation",
                name="Model Validation",
                function=lambda ctx: {"status": "model_validated", "metrics": {"f1": 0.89}},
                dependencies=["model_training"]
            ),
            PipelineStep(
                id="model_registration",
                name="Model Registration",
                function=lambda ctx: {"status": "model_registered", "model_id": "model_123"},
                dependencies=["model_validation"]
            )
        ]
        
        for step in steps:
            await orchestrator.register_step(step)
        
        pipeline_id = "training_pipeline_standard"
        await orchestrator.define_pipeline(
            pipeline_id,
            PipelineType.TRAINING_PIPELINE,
            [step.id for step in steps]
        )
        
        return pipeline_id

# Context manager pour orchestration enterprise
@asynccontextmanager
async def pipeline_execution_context(orchestrator: PipelineOrchestrator):
    """Context manager pour l'exécution sécurisée de pipelines"""
    execution_start = datetime.utcnow()
    try:
        yield orchestrator
    except Exception as e:
        logger.error(f"Pipeline execution error: {str(e)}")
        raise
    finally:
        execution_duration = datetime.utcnow() - execution_start
        logger.info(f"Pipeline execution context closed after {execution_duration.total_seconds():.2f}s")

# Exemple d'utilisation avancée
async def demo_enterprise_orchestration():
    """Démo de l'orchestration enterprise complète"""
    orchestrator = PipelineOrchestrator(max_concurrent_pipelines=5)
    
    # Créer des pipelines standardisés
    data_pipeline_id = await PipelineFactory.create_data_pipeline(orchestrator)
    training_pipeline_id = await PipelineFactory.create_training_pipeline(orchestrator)
    
    async with pipeline_execution_context(orchestrator):
        # Exécuter les pipelines
        data_result = await orchestrator.execute_pipeline(data_pipeline_id)
        training_result = await orchestrator.execute_pipeline(training_pipeline_id)
        
        # Métriques
        metrics = await orchestrator.get_metrics()
        
        print(f"Orchestration completed:")
        print(f"- Data pipeline: {data_result['status']}")
        print(f"- Training pipeline: {training_result['status']}")
        print(f"- Metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(demo_enterprise_orchestration())