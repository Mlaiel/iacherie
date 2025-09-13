"""
🔄 AI PIPELINE ORCHESTRATOR SERVICE
Orchestration des pipelines ML/IA distribués

Fonctionnalités:
- Orchestration pipelines ML complexes
- Gestion des dépendances entre étapes
- Parallélisation automatique
- Monitoring et logging distribué
- Gestion des échecs et reprises

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    """États du pipeline"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class StepStatus(Enum):
    """États des étapes"""
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class PipelineStep:
    """Étape de pipeline ML"""
    step_id: str
    name: str
    function: Callable
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 3600
    status: StepStatus = StepStatus.WAITING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None

@dataclass
class Pipeline:
    """Pipeline ML complet"""
    pipeline_id: str
    name: str
    steps: List[PipelineStep]
    status: PipelineStatus = PipelineStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_context: Dict[str, Any] = field(default_factory=dict)

class AIPipelineOrchestrator:
    """
    🔄 ORCHESTRATEUR PIPELINE IA ENTERPRISE
    
    Orchestration de pipelines ML/IA distribués avec gestion
    des dépendances, parallélisation et monitoring
    """
    
    def __init__(self, service_id: str = None):
        self.service_id = service_id or f"ai-pipeline-orchestrator-{int(time.time())}"
        self.status = "initializing"
        self.active_pipelines: Dict[str, Pipeline] = {}
        self.pipeline_history: List[Pipeline] = []
        self.step_templates: Dict[str, Callable] = {}
        
    async def initialize(self) -> bool:
        """Initialiser l'orchestrateur de pipeline"""
        logger.info("🔄 Initializing AI Pipeline Orchestrator...")
        
        try:
            # Charger les templates d'étapes
            await self._load_step_templates()
            
            self.status = "ready"
            logger.info("✅ AI Pipeline Orchestrator initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Pipeline Orchestrator: {e}")
            self.status = "error"
            return False
    
    async def _load_step_templates(self) -> None:
        """Charger les templates d'étapes prédéfinies"""
        self.step_templates = {
            "data_validation": self._data_validation_step,
            "data_preprocessing": self._data_preprocessing_step,
            "feature_engineering": self._feature_engineering_step,
            "model_training": self._model_training_step,
            "model_validation": self._model_validation_step,
            "model_deployment": self._model_deployment_step,
            "performance_monitoring": self._performance_monitoring_step,
            "data_quality_check": self._data_quality_check_step,
            "model_versioning": self._model_versioning_step,
            "notification": self._notification_step
        }
    
    async def create_pipeline(
        self,
        name: str,
        steps_config: List[Dict[str, Any]],
        metadata: Dict[str, Any] = None
    ) -> str:
        """Créer un nouveau pipeline"""
        pipeline_id = str(uuid.uuid4())
        
        logger.info(f"🔄 Creating pipeline: {name} ({pipeline_id})")
        
        # Créer les étapes
        steps = []
        for step_config in steps_config:
            step = PipelineStep(
                step_id=step_config.get('step_id', str(uuid.uuid4())),
                name=step_config['name'],
                function=self.step_templates.get(step_config['type'], self._custom_step),
                dependencies=step_config.get('dependencies', []),
                parameters=step_config.get('parameters', {}),
                max_retries=step_config.get('max_retries', 3),
                timeout_seconds=step_config.get('timeout_seconds', 3600)
            )
            steps.append(step)
        
        # Créer le pipeline
        pipeline = Pipeline(
            pipeline_id=pipeline_id,
            name=name,
            steps=steps,
            metadata=metadata or {}
        )
        
        # Valider les dépendances
        if not self._validate_dependencies(pipeline):
            raise ValueError("Invalid pipeline dependencies detected")
        
        self.active_pipelines[pipeline_id] = pipeline
        
        logger.info(f"✅ Pipeline created: {pipeline_id}")
        return pipeline_id
    
    def _validate_dependencies(self, pipeline: Pipeline) -> bool:
        """Valider que les dépendances sont correctes"""
        step_ids = {step.step_id for step in pipeline.steps}
        
        for step in pipeline.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    logger.error(f"Invalid dependency: {dep} not found in pipeline steps")
                    return False
        
        # Vérifier les cycles
        if self._has_circular_dependencies(pipeline.steps):
            logger.error("Circular dependencies detected")
            return False
            
        return True
    
    def _has_circular_dependencies(self, steps: List[PipelineStep]) -> bool:
        """Détecter les dépendances circulaires"""
        # Implémentation simplifiée d'un algorithme de détection de cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_id: str) -> bool:
            visited.add(step_id)
            rec_stack.add(step_id)
            
            step = next((s for s in steps if s.step_id == step_id), None)
            if step:
                for dep in step.dependencies:
                    if dep not in visited:
                        if has_cycle(dep):
                            return True
                    elif dep in rec_stack:
                        return True
            
            rec_stack.remove(step_id)
            return False
        
        for step in steps:
            if step.step_id not in visited:
                if has_cycle(step.step_id):
                    return True
        
        return False
    
    async def execute_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Exécuter un pipeline"""
        if pipeline_id not in self.active_pipelines:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        
        pipeline = self.active_pipelines[pipeline_id]
        
        logger.info(f"🚀 Executing pipeline: {pipeline.name} ({pipeline_id})")
        
        try:
            pipeline.status = PipelineStatus.RUNNING
            pipeline.start_time = time.time()
            
            # Créer le graphe d'exécution
            execution_graph = self._build_execution_graph(pipeline.steps)
            
            # Exécuter les étapes selon les dépendances
            execution_result = await self._execute_steps_with_dependencies(
                pipeline, 
                execution_graph
            )
            
            pipeline.status = PipelineStatus.COMPLETED
            pipeline.end_time = time.time()
            
            logger.info(f"✅ Pipeline completed: {pipeline_id}")
            
            # Déplacer vers l'historique
            self.pipeline_history.append(pipeline)
            del self.active_pipelines[pipeline_id]
            
            return {
                'pipeline_id': pipeline_id,
                'status': 'completed',
                'execution_time_seconds': pipeline.end_time - pipeline.start_time,
                'steps_executed': len([s for s in pipeline.steps if s.status == StepStatus.COMPLETED]),
                'steps_failed': len([s for s in pipeline.steps if s.status == StepStatus.FAILED]),
                'execution_result': execution_result
            }
            
        except Exception as e:
            pipeline.status = PipelineStatus.FAILED
            pipeline.end_time = time.time()
            logger.error(f"❌ Pipeline failed: {pipeline_id} - {e}")
            
            return {
                'pipeline_id': pipeline_id,
                'status': 'failed',
                'error': str(e),
                'execution_time_seconds': pipeline.end_time - pipeline.start_time if pipeline.end_time else None
            }
    
    def _build_execution_graph(self, steps: List[PipelineStep]) -> Dict[str, List[str]]:
        """Construire le graphe d'exécution"""
        graph = {}
        for step in steps:
            graph[step.step_id] = step.dependencies.copy()
        return graph
    
    async def _execute_steps_with_dependencies(
        self, 
        pipeline: Pipeline,
        execution_graph: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Exécuter les étapes en respectant les dépendances"""
        completed_steps = set()
        results = {}
        
        while len(completed_steps) < len(pipeline.steps):
            # Trouver les étapes prêtes à être exécutées
            ready_steps = []
            for step in pipeline.steps:
                if (step.step_id not in completed_steps and 
                    step.status in [StepStatus.WAITING, StepStatus.FAILED] and
                    all(dep in completed_steps for dep in step.dependencies)):
                    ready_steps.append(step)
            
            if not ready_steps:
                # Pas d'étapes prêtes - possiblement des échecs bloquants
                failed_steps = [s for s in pipeline.steps if s.status == StepStatus.FAILED]
                if failed_steps:
                    raise Exception(f"Pipeline blocked by failed steps: {[s.step_id for s in failed_steps]}")
                break
            
            # Exécuter les étapes prêtes en parallèle
            tasks = []
            for step in ready_steps:
                task = asyncio.create_task(self._execute_step(step, pipeline.execution_context))
                tasks.append((step, task))
            
            # Attendre la completion
            for step, task in tasks:
                try:
                    result = await task
                    step.status = StepStatus.COMPLETED
                    step.result = result
                    results[step.step_id] = result
                    completed_steps.add(step.step_id)
                    logger.info(f"✅ Step completed: {step.name}")
                    
                except Exception as e:
                    step.status = StepStatus.FAILED
                    step.error = str(e)
                    logger.error(f"❌ Step failed: {step.name} - {e}")
                    
                    # Retry logic
                    if step.retry_count < step.max_retries:
                        step.retry_count += 1
                        step.status = StepStatus.WAITING
                        logger.info(f"🔄 Retrying step: {step.name} (attempt {step.retry_count})")
        
        return results
    
    async def _execute_step(self, step: PipelineStep, context: Dict[str, Any]) -> Any:
        """Exécuter une étape individuelle"""
        logger.info(f"🔧 Executing step: {step.name}")
        
        step.status = StepStatus.RUNNING
        step.start_time = time.time()
        
        try:
            # Exécuter avec timeout
            result = await asyncio.wait_for(
                step.function(step.parameters, context),
                timeout=step.timeout_seconds
            )
            
            step.end_time = time.time()
            return result
            
        except asyncio.TimeoutError:
            step.end_time = time.time()
            raise Exception(f"Step timeout after {step.timeout_seconds} seconds")
        except Exception as e:
            step.end_time = time.time()
            raise e
    
    # Templates d'étapes prédéfinies
    async def _data_validation_step(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Étape de validation des données"""
        await asyncio.sleep(0.1)  # Simulation
        return {"status": "validated", "records_validated": params.get("record_count", 1000)}
    
    async def _data_preprocessing_step(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Étape de préprocessing des données"""
        await asyncio.sleep(0.2)  # Simulation
        return {"status": "preprocessed", "features_created": params.get("feature_count", 50)}
    
    async def _feature_engineering_step(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Étape d'ingénierie des features"""
        await asyncio.sleep(0.15)  # Simulation
        return {"status": "features_engineered", "new_features": params.get("new_features", 10)}
    
    async def _model_training_step(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Étape d'entraînement du modèle"""
        await asyncio.sleep(0.5)  # Simulation d'entraînement plus long
        return {"status": "trained", "model_accuracy": 0.95, "epochs": params.get("epochs", 100)}
    
    async def _model_validation_step(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Étape de validation du modèle"""
        await asyncio.sleep(0.1)  # Simulation
        return {"status": "validated", "validation_score": 0.92}
    
    async def _model_deployment_step(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Étape de déploiement du modèle"""
        await asyncio.sleep(0.3)  # Simulation
        return {"status": "deployed", "endpoint_url": f"https://api.ainflue.com/models/{params.get('model_id', 'unknown')}"}
    
    async def _performance_monitoring_step(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Étape de monitoring des performances"""
        await asyncio.sleep(0.1)  # Simulation
        return {"status": "monitoring_active", "metrics_collected": True}
    
    async def _data_quality_check_step(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Étape de vérification qualité des données"""
        await asyncio.sleep(0.1)  # Simulation
        return {"status": "quality_checked", "quality_score": 0.98}
    
    async def _model_versioning_step(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Étape de versioning du modèle"""
        await asyncio.sleep(0.1)  # Simulation
        return {"status": "versioned", "version": params.get("version", "1.0.0")}
    
    async def _notification_step(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Étape de notification"""
        await asyncio.sleep(0.05)  # Simulation
        return {"status": "notified", "recipients": params.get("recipients", [])}
    
    async def _custom_step(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Étape personnalisée"""
        await asyncio.sleep(0.1)  # Simulation
        return {"status": "custom_step_completed", "parameters": params}
    
    async def pause_pipeline(self, pipeline_id: str) -> bool:
        """Mettre en pause un pipeline"""
        if pipeline_id in self.active_pipelines:
            self.active_pipelines[pipeline_id].status = PipelineStatus.PAUSED
            logger.info(f"⏸️ Pipeline paused: {pipeline_id}")
            return True
        return False
    
    async def resume_pipeline(self, pipeline_id: str) -> bool:
        """Reprendre un pipeline en pause"""
        if pipeline_id in self.active_pipelines:
            pipeline = self.active_pipelines[pipeline_id]
            if pipeline.status == PipelineStatus.PAUSED:
                pipeline.status = PipelineStatus.RUNNING
                logger.info(f"▶️ Pipeline resumed: {pipeline_id}")
                return True
        return False
    
    async def cancel_pipeline(self, pipeline_id: str) -> bool:
        """Annuler un pipeline"""
        if pipeline_id in self.active_pipelines:
            self.active_pipelines[pipeline_id].status = PipelineStatus.CANCELLED
            logger.info(f"❌ Pipeline cancelled: {pipeline_id}")
            return True
        return False
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Obtenir le statut d'un pipeline"""
        pipeline = self.active_pipelines.get(pipeline_id)
        if not pipeline:
            # Chercher dans l'historique
            pipeline = next((p for p in self.pipeline_history if p.pipeline_id == pipeline_id), None)
        
        if pipeline:
            return {
                'pipeline_id': pipeline.pipeline_id,
                'name': pipeline.name,
                'status': pipeline.status.value,
                'steps_total': len(pipeline.steps),
                'steps_completed': len([s for s in pipeline.steps if s.status == StepStatus.COMPLETED]),
                'steps_failed': len([s for s in pipeline.steps if s.status == StepStatus.FAILED]),
                'steps_running': len([s for s in pipeline.steps if s.status == StepStatus.RUNNING]),
                'start_time': pipeline.start_time,
                'end_time': pipeline.end_time,
                'execution_time_seconds': (pipeline.end_time - pipeline.start_time) if pipeline.end_time and pipeline.start_time else None
            }
        return None
    
    def list_active_pipelines(self) -> List[Dict[str, Any]]:
        """Lister les pipelines actifs"""
        return [self.get_pipeline_status(pid) for pid in self.active_pipelines.keys()]
    
    def get_service_status(self) -> Dict[str, Any]:
        """Obtenir le statut du service"""
        return {
            'service_id': self.service_id,
            'status': self.status,
            'active_pipelines': len(self.active_pipelines),
            'total_pipelines_executed': len(self.pipeline_history),
            'available_step_templates': list(self.step_templates.keys())
        }

# Instance globale du service
ai_pipeline_orchestrator = AIPipelineOrchestrator()

async def main():
    """Test de l'orchestrateur de pipeline IA"""
    await ai_pipeline_orchestrator.initialize()
    
    # Configuration d'un pipeline d'exemple
    steps_config = [
        {
            "step_id": "data_val",
            "name": "Data Validation",
            "type": "data_validation",
            "parameters": {"record_count": 10000}
        },
        {
            "step_id": "data_prep",
            "name": "Data Preprocessing", 
            "type": "data_preprocessing",
            "dependencies": ["data_val"],
            "parameters": {"feature_count": 100}
        },
        {
            "step_id": "feature_eng",
            "name": "Feature Engineering",
            "type": "feature_engineering",
            "dependencies": ["data_prep"],
            "parameters": {"new_features": 25}
        },
        {
            "step_id": "training",
            "name": "Model Training",
            "type": "model_training",
            "dependencies": ["feature_eng"],
            "parameters": {"epochs": 50}
        },
        {
            "step_id": "validation",
            "name": "Model Validation",
            "type": "model_validation",
            "dependencies": ["training"]
        },
        {
            "step_id": "deployment",
            "name": "Model Deployment",
            "type": "model_deployment",
            "dependencies": ["validation"],
            "parameters": {"model_id": "test-model-123"}
        }
    ]
    
    # Créer et exécuter le pipeline
    pipeline_id = await ai_pipeline_orchestrator.create_pipeline(
        "ML Training Pipeline Example",
        steps_config,
        {"project": "ainflue-test", "version": "1.0"}
    )
    
    print(f"Created pipeline: {pipeline_id}")
    
    # Exécuter le pipeline
    result = await ai_pipeline_orchestrator.execute_pipeline(pipeline_id)
    print(f"Execution result: {result}")

if __name__ == "__main__":
    asyncio.run(main())