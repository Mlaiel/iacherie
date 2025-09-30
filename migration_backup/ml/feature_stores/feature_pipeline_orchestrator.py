"""🚀 Feature Pipeline Orchestrator - IA Influencer Agent Platform Enterprise
==========================================================================
Module: backend/ml/feature_stores/feature_pipeline_orchestrator.py
Author: Fahed Mlaiel (mlaiel@live.de)
==========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ORCHESTRATEUR DE PIPELINES DE FEATURES
Orchestration complète des pipelines de feature engineering
- DAG de transformations avec dépendances automatiques
- Feature lineage tracking et data governance
- Parallélisation intelligente et caching
- Validation et quality gates automatiques
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import hashlib
from pathlib import Path
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import networkx as nx

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.impute import SimpleImputer, KNNImputer

# Configuration
logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    """Statuts des pipelines"""
    CREATED = "created"
    VALIDATING = "validating"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FeatureType(Enum):
    """Types de features"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    TIMESTAMP = "timestamp"
    EMBEDDING = "embedding"
    DERIVED = "derived"

class TransformationType(Enum):
    """Types de transformations"""
    SCALING = "scaling"
    ENCODING = "encoding"
    IMPUTATION = "imputation"
    DERIVATION = "derivation"
    AGGREGATION = "aggregation"
    SELECTION = "selection"
    VALIDATION = "validation"

class ExecutionMode(Enum):
    """Modes d'exécution"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"
    STREAMING = "streaming"

@dataclass
class FeatureDefinition:
    """Définition d'une feature"""
    name: str
    feature_type: FeatureType
    description: Optional[str] = None
    source_columns: List[str] = field(default_factory=list)
    transformation_params: Dict[str, Any] = field(default_factory=dict)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class TransformationStep:
    """Étape de transformation"""
    step_id: str
    name: str
    transformation_type: TransformationType
    transformer: Union[Callable, BaseEstimator, str]
    input_features: List[str]
    output_features: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    parallel_safe: bool = True
    cache_enabled: bool = True
    validation_enabled: bool = True

@dataclass
class PipelineConfig:
    """Configuration de pipeline"""
    pipeline_id: str
    name: str
    description: Optional[str] = None
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL
    max_workers: int = 4
    enable_caching: bool = True
    enable_validation: bool = True
    enable_lineage_tracking: bool = True
    cache_ttl_hours: int = 24
    retry_attempts: int = 3
    timeout_minutes: int = 30

@dataclass
class PipelineRun:
    """Exécution de pipeline"""
    run_id: str
    pipeline_id: str
    status: PipelineStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    input_data_hash: Optional[str] = None
    output_features_count: int = 0
    error_message: Optional[str] = None
    execution_metrics: Dict[str, Any] = field(default_factory=dict)
    lineage_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FeatureLineage:
    """Lignage de feature"""
    feature_name: str
    source_data: List[str]
    transformations: List[str]
    dependencies: List[str]
    created_by_run: str
    created_at: datetime
    quality_metrics: Dict[str, Any] = field(default_factory=dict)

class FeaturePipelineOrchestrator:
    """Orchestrateur de pipelines de features enterprise"""
    
    def __init__(self,
                 max_concurrent_pipelines: int = 10,
                 global_cache_size: int = 1000,
                 enable_distributed_execution: bool = False):
        
        self.max_concurrent_pipelines = max_concurrent_pipelines
        self.global_cache_size = global_cache_size
        self.enable_distributed_execution = enable_distributed_execution
        
        # Registres
        self.pipelines: Dict[str, PipelineConfig] = {}
        self.pipeline_steps: Dict[str, List[TransformationStep]] = {}
        self.pipeline_runs: Dict[str, PipelineRun] = {}
        self.feature_definitions: Dict[str, FeatureDefinition] = {}
        self.feature_lineage: Dict[str, FeatureLineage] = {}
        
        # Exécution
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.running_pipelines: Dict[str, asyncio.Task] = {}
        self.pipeline_graphs: Dict[str, nx.DiGraph] = {}
        
        # Cache
        self.transformation_cache: Dict[str, Any] = {}
        self.cache_access_times: Dict[str, datetime] = {}
        
        # Monitoring
        self.execution_metrics = {
            "total_pipelines_run": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "total_features_generated": 0,
            "average_execution_time": 0.0,
            "cache_hit_rate": 0.0
        }
        
        # State management
        self.is_running = False
        self.shutdown_event = threading.Event()
        
        # Callbacks
        self.pipeline_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self.feature_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
        
        # Built-in transformers
        self._register_builtin_transformers()
    
    def _register_builtin_transformers(self):
        """Enregistre les transformateurs intégrés"""
        self.builtin_transformers = {
            "standard_scaler": StandardScaler,
            "minmax_scaler": MinMaxScaler,
            "robust_scaler": RobustScaler,
            "simple_imputer": SimpleImputer,
            "knn_imputer": KNNImputer,
            "log_transform": lambda: lambda x: np.log1p(x),
            "sqrt_transform": lambda: lambda x: np.sqrt(np.abs(x)),
            "polynomial_features": self._polynomial_features_transformer,
            "interaction_features": self._interaction_features_transformer,
            "time_features": self._time_features_transformer,
            "text_features": self._text_features_transformer
        }
    
    async def start(self):
        """Démarre l'orchestrateur"""
        try:
            self.is_running = True
            logger.info("Démarrage orchestrateur de pipelines de features")
            
            # Démarrer les tâches de maintenance
            asyncio.create_task(self._monitoring_loop())
            asyncio.create_task(self._cache_cleanup_loop())
            
            logger.info("Orchestrateur démarré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur démarrage orchestrateur: {e}")
            raise
    
    async def stop(self):
        """Arrête l'orchestrateur"""
        try:
            logger.info("Arrêt orchestrateur de pipelines...")
            
            self.is_running = False
            self.shutdown_event.set()
            
            # Arrêter les pipelines en cours
            for pipeline_id, task in self.running_pipelines.items():
                logger.info(f"Arrêt pipeline {pipeline_id}")
                task.cancel()
            
            # Fermer l'executor
            self.executor.shutdown(wait=True)
            
            logger.info("Orchestrateur arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt orchestrateur: {e}")
    
    async def register_pipeline(self,
                               config: PipelineConfig,
                               steps: List[TransformationStep]) -> bool:
        """Enregistre un pipeline de features"""
        try:
            # Valider la configuration
            if config.pipeline_id in self.pipelines:
                raise ValueError(f"Pipeline {config.pipeline_id} existe déjà")
            
            # Valider les étapes
            await self._validate_pipeline_steps(steps)
            
            # Créer le graphe de dépendances
            graph = self._build_dependency_graph(steps)
            
            # Vérifier l'absence de cycles
            if not nx.is_directed_acyclic_graph(graph):
                raise ValueError("Le pipeline contient des dépendances cycliques")
            
            # Enregistrer le pipeline
            self.pipelines[config.pipeline_id] = config
            self.pipeline_steps[config.pipeline_id] = steps
            self.pipeline_graphs[config.pipeline_id] = graph
            
            logger.info(f"Pipeline {config.pipeline_id} enregistré avec {len(steps)} étapes")
            return True
            
        except Exception as e:
            logger.error(f"Erreur enregistrement pipeline {config.pipeline_id}: {e}")
            return False
    
    async def _validate_pipeline_steps(self, steps: List[TransformationStep]):
        """Valide les étapes d'un pipeline"""
        step_ids = {step.step_id for step in steps}
        
        for step in steps:
            # Vérifier les dépendances
            for dep in step.dependencies:
                if dep not in step_ids:
                    raise ValueError(f"Dépendance inconnue: {dep} pour l'étape {step.step_id}")
            
            # Vérifier le transformateur
            if isinstance(step.transformer, str):
                if step.transformer not in self.builtin_transformers:
                    raise ValueError(f"Transformateur inconnu: {step.transformer}")
            elif not (callable(step.transformer) or hasattr(step.transformer, 'transform')):
                raise ValueError(f"Transformateur invalide pour l'étape {step.step_id}")
    
    def _build_dependency_graph(self, steps: List[TransformationStep]) -> nx.DiGraph:
        """Construit le graphe de dépendances"""
        graph = nx.DiGraph()
        
        # Ajouter les nœuds
        for step in steps:
            graph.add_node(step.step_id, step=step)
        
        # Ajouter les arêtes de dépendance
        for step in steps:
            for dep in step.dependencies:
                graph.add_edge(dep, step.step_id)
        
        return graph
    
    async def execute_pipeline(self,
                              pipeline_id: str,
                              input_data: pd.DataFrame,
                              run_name: Optional[str] = None) -> str:
        """Exécute un pipeline de features"""
        
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} n'existe pas")
        
        if len(self.running_pipelines) >= self.max_concurrent_pipelines:
            raise ValueError("Limite de pipelines concurrents atteinte")
        
        # Créer l'exécution
        run_id = str(uuid.uuid4())
        if run_name:
            run_id = f"{run_name}_{run_id[:8]}"
        
        pipeline_run = PipelineRun(
            run_id=run_id,
            pipeline_id=pipeline_id,
            status=PipelineStatus.SCHEDULED,
            start_time=datetime.now(),
            input_data_hash=self._hash_dataframe(input_data)
        )
        
        self.pipeline_runs[run_id] = pipeline_run
        
        # Démarrer l'exécution
        task = asyncio.create_task(self._execute_pipeline_async(run_id, input_data))
        self.running_pipelines[run_id] = task
        
        logger.info(f"Pipeline {pipeline_id} démarré (run: {run_id})")
        return run_id
    
    async def _execute_pipeline_async(self, run_id: str, input_data: pd.DataFrame):
        """Exécute un pipeline de manière asynchrone"""
        
        pipeline_run = self.pipeline_runs[run_id]
        config = self.pipelines[pipeline_run.pipeline_id]
        steps = self.pipeline_steps[pipeline_run.pipeline_id]
        graph = self.pipeline_graphs[pipeline_run.pipeline_id]
        
        start_time = time.time()
        
        try:
            pipeline_run.status = PipelineStatus.RUNNING
            logger.info(f"Début exécution pipeline {pipeline_run.pipeline_id} (run: {run_id})")
            
            # Préparer les données de travail
            working_data = input_data.copy()
            feature_lineage_info = {}
            execution_stats = {
                "steps_executed": 0,
                "steps_cached": 0,
                "features_created": 0,
                "validation_errors": 0
            }
            
            # Obtenir l'ordre d'exécution topologique
            execution_order = list(nx.topological_sort(graph))
            
            # Exécuter selon le mode
            if config.execution_mode == ExecutionMode.SEQUENTIAL:
                working_data = await self._execute_sequential(
                    run_id, steps, execution_order, working_data, execution_stats
                )
            elif config.execution_mode == ExecutionMode.PARALLEL:
                working_data = await self._execute_parallel(
                    run_id, steps, graph, working_data, execution_stats
                )
            else:
                raise ValueError(f"Mode d'exécution non supporté: {config.execution_mode}")
            
            # Finaliser l'exécution
            execution_time = time.time() - start_time
            
            pipeline_run.status = PipelineStatus.COMPLETED
            pipeline_run.end_time = datetime.now()
            pipeline_run.output_features_count = len(working_data.columns)
            pipeline_run.execution_metrics = execution_stats
            pipeline_run.execution_metrics["total_time_seconds"] = execution_time
            
            # Mettre à jour les métriques globales
            self.execution_metrics["total_pipelines_run"] += 1
            self.execution_metrics["successful_runs"] += 1
            self.execution_metrics["total_features_generated"] += execution_stats["features_created"]
            
            # Calculer le temps moyen
            total_runs = self.execution_metrics["total_pipelines_run"]
            avg_time = self.execution_metrics["average_execution_time"]
            self.execution_metrics["average_execution_time"] = (
                (avg_time * (total_runs - 1) + execution_time) / total_runs
            )
            
            logger.info(f"Pipeline {pipeline_run.pipeline_id} terminé avec succès "
                       f"(run: {run_id}, {execution_time:.2f}s, "
                       f"{execution_stats['features_created']} features)")
            
            # Appeler les callbacks
            for callback in self.pipeline_callbacks[pipeline_run.pipeline_id]:
                try:
                    await callback(pipeline_run, working_data)
                except Exception as e:
                    logger.error(f"Erreur callback pipeline: {e}")
            
            return working_data
            
        except Exception as e:
            logger.error(f"Erreur exécution pipeline {run_id}: {e}")
            
            pipeline_run.status = PipelineStatus.FAILED
            pipeline_run.end_time = datetime.now()
            pipeline_run.error_message = str(e)
            
            self.execution_metrics["failed_runs"] += 1
            
            # Appeler les callbacks d'erreur
            for callback in self.error_callbacks:
                try:
                    await callback(e, pipeline_run)
                except Exception as cb_error:
                    logger.error(f"Erreur callback erreur: {cb_error}")
            
            raise
        
        finally:
            # Nettoyer
            if run_id in self.running_pipelines:
                del self.running_pipelines[run_id]
    
    async def _execute_sequential(self,
                                 run_id: str,
                                 steps: List[TransformationStep],
                                 execution_order: List[str],
                                 working_data: pd.DataFrame,
                                 execution_stats: Dict[str, Any]) -> pd.DataFrame:
        """Exécute les étapes séquentiellement"""
        
        step_dict = {step.step_id: step for step in steps}
        
        for step_id in execution_order:
            step = step_dict[step_id]
            
            try:
                working_data = await self._execute_step(run_id, step, working_data, execution_stats)
                execution_stats["steps_executed"] += 1
                
            except Exception as e:
                logger.error(f"Erreur étape {step_id}: {e}")
                raise
        
        return working_data
    
    async def _execute_parallel(self,
                               run_id: str,
                               steps: List[TransformationStep],
                               graph: nx.DiGraph,
                               working_data: pd.DataFrame,
                               execution_stats: Dict[str, Any]) -> pd.DataFrame:
        """Exécute les étapes en parallèle quand possible"""
        
        step_dict = {step.step_id: step for step in steps}
        executed_steps = set()
        futures = {}
        
        while len(executed_steps) < len(steps):
            # Trouver les étapes prêtes à être exécutées
            ready_steps = []
            for step_id in step_dict:
                if step_id not in executed_steps and step_id not in futures:
                    # Vérifier que toutes les dépendances sont satisfaites
                    dependencies = list(graph.predecessors(step_id))
                    if all(dep in executed_steps for dep in dependencies):
                        ready_steps.append(step_id)
            
            # Lancer les étapes parallèles
            for step_id in ready_steps:
                step = step_dict[step_id]
                if step.parallel_safe:
                    future = asyncio.create_task(
                        self._execute_step(run_id, step, working_data.copy(), execution_stats)
                    )
                    futures[step_id] = future
                else:
                    # Étape non thread-safe, exécuter directement
                    working_data = await self._execute_step(run_id, step, working_data, execution_stats)
                    executed_steps.add(step_id)
                    execution_stats["steps_executed"] += 1
            
            # Attendre la completion des futures
            if futures:
                done, pending = await asyncio.wait(
                    futures.values(),
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Traiter les résultats
                for future in done:
                    step_id = None
                    for sid, fut in futures.items():
                        if fut == future:
                            step_id = sid
                            break
                    
                    if step_id:
                        try:
                            result_data = await future
                            # Merger les nouvelles colonnes
                            for col in result_data.columns:
                                if col not in working_data.columns:
                                    working_data[col] = result_data[col]
                            
                            executed_steps.add(step_id)
                            del futures[step_id]
                            execution_stats["steps_executed"] += 1
                            
                        except Exception as e:
                            logger.error(f"Erreur étape parallèle {step_id}: {e}")
                            del futures[step_id]
                            raise
        
        return working_data
    
    async def _execute_step(self,
                           run_id: str,
                           step: TransformationStep,
                           data: pd.DataFrame,
                           execution_stats: Dict[str, Any]) -> pd.DataFrame:
        """Exécute une étape de transformation"""
        
        step_start_time = time.time()
        
        try:
            # Vérifier le cache si activé
            if step.cache_enabled and self.pipelines[self.pipeline_runs[run_id].pipeline_id].enable_caching:
                cache_key = self._generate_step_cache_key(step, data)
                cached_result = self._get_from_cache(cache_key)
                if cached_result is not None:
                    execution_stats["steps_cached"] += 1
                    return cached_result
            
            # Préparer les données d'entrée
            input_data = self._prepare_step_input(step, data)
            
            # Obtenir le transformateur
            transformer = self._get_transformer(step)
            
            # Exécuter la transformation
            if hasattr(transformer, 'transform'):
                # Sklearn-style transformer
                if hasattr(transformer, 'fit'):
                    # Fit + transform
                    transformer.fit(input_data)
                    output_data = transformer.transform(input_data)
                else:
                    # Transform seulement
                    output_data = transformer.transform(input_data)
            elif callable(transformer):
                # Fonction callable
                output_data = transformer(input_data)
            else:
                raise ValueError(f"Transformateur invalide pour {step.step_id}")
            
            # Traiter la sortie
            result_data = self._process_step_output(step, data, output_data)
            
            # Validation si activée
            if step.validation_enabled:
                await self._validate_step_output(step, result_data)
            
            # Mettre en cache si activé
            if step.cache_enabled and self.pipelines[self.pipeline_runs[run_id].pipeline_id].enable_caching:
                self._put_in_cache(cache_key, result_data)
            
            # Mettre à jour les statistiques
            execution_stats["features_created"] += len(step.output_features)
            
            step_time = time.time() - step_start_time
            logger.debug(f"Étape {step.step_id} exécutée en {step_time:.2f}s")
            
            return result_data
            
        except Exception as e:
            logger.error(f"Erreur exécution étape {step.step_id}: {e}")
            execution_stats["validation_errors"] += 1
            raise
    
    def _prepare_step_input(self, step: TransformationStep, data: pd.DataFrame) -> pd.DataFrame:
        """Prépare les données d'entrée pour une étape"""
        if step.input_features:
            # Utiliser seulement les colonnes spécifiées
            available_features = [f for f in step.input_features if f in data.columns]
            if not available_features:
                raise ValueError(f"Aucune feature d'entrée disponible pour {step.step_id}")
            return data[available_features]
        else:
            # Utiliser toutes les données
            return data
    
    def _get_transformer(self, step: TransformationStep):
        """Obtient le transformateur pour une étape"""
        if isinstance(step.transformer, str):
            # Transformateur intégré
            if step.transformer in self.builtin_transformers:
                transformer_class = self.builtin_transformers[step.transformer]
                if callable(transformer_class):
                    return transformer_class(**step.parameters)
                else:
                    return transformer_class
            else:
                raise ValueError(f"Transformateur inconnu: {step.transformer}")
        else:
            # Transformateur fourni directement
            return step.transformer
    
    def _process_step_output(self,
                            step: TransformationStep,
                            original_data: pd.DataFrame,
                            output_data: Any) -> pd.DataFrame:
        """Traite la sortie d'une étape"""
        
        result_data = original_data.copy()
        
        # Convertir la sortie en DataFrame si nécessaire
        if isinstance(output_data, np.ndarray):
            if output_data.ndim == 1:
                output_data = output_data.reshape(-1, 1)
            
            # Créer les noms de colonnes
            if len(step.output_features) == output_data.shape[1]:
                output_df = pd.DataFrame(output_data, columns=step.output_features, index=original_data.index)
            else:
                # Générer des noms automatiques
                output_df = pd.DataFrame(
                    output_data,
                    columns=[f"{step.step_id}_feature_{i}" for i in range(output_data.shape[1])],
                    index=original_data.index
                )
        elif isinstance(output_data, pd.DataFrame):
            output_df = output_data
        elif isinstance(output_data, pd.Series):
            output_df = output_data.to_frame()
        else:
            # Essayer de convertir
            output_df = pd.DataFrame(output_data, index=original_data.index)
        
        # Ajouter les nouvelles colonnes
        for col in output_df.columns:
            result_data[col] = output_df[col]
        
        return result_data
    
    async def _validate_step_output(self, step: TransformationStep, data: pd.DataFrame):
        """Valide la sortie d'une étape"""
        # Validation basique
        for feature_name in step.output_features:
            if feature_name in data.columns:
                feature_data = data[feature_name]
                
                # Vérifier les valeurs manquantes
                if feature_data.isnull().any():
                    null_count = feature_data.isnull().sum()
                    if null_count > len(feature_data) * 0.5:  # Plus de 50% de valeurs manquantes
                        logger.warning(f"Feature {feature_name} a {null_count} valeurs manquantes")
                
                # Vérifier les valeurs infinies
                if pd.api.types.is_numeric_dtype(feature_data):
                    inf_count = np.isinf(feature_data).sum()
                    if inf_count > 0:
                        logger.warning(f"Feature {feature_name} a {inf_count} valeurs infinies")
    
    def _generate_step_cache_key(self, step: TransformationStep, data: pd.DataFrame) -> str:
        """Génère une clé de cache pour une étape"""
        try:
            # Créer un hash basé sur l'étape et les données
            step_info = f"{step.step_id}_{step.transformation_type.value}_{str(step.parameters)}"
            data_hash = self._hash_dataframe(data[step.input_features] if step.input_features else data)
            return hashlib.md5(f"{step_info}_{data_hash}".encode()).hexdigest()
        except Exception:
            return f"{step.step_id}_{int(time.time())}"
    
    def _hash_dataframe(self, df: pd.DataFrame) -> str:
        """Calcule un hash d'un DataFrame"""
        try:
            return hashlib.md5(pd.util.hash_pandas_object(df).values.tobytes()).hexdigest()
        except Exception:
            return str(hash(str(df.shape)))
    
    def _get_from_cache(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Récupère une valeur du cache"""
        if cache_key in self.transformation_cache:
            self.cache_access_times[cache_key] = datetime.now()
            return self.transformation_cache[cache_key].copy()
        return None
    
    def _put_in_cache(self, cache_key: str, data: pd.DataFrame):
        """Met une valeur en cache"""
        if len(self.transformation_cache) >= self.global_cache_size:
            self._evict_cache()
        
        self.transformation_cache[cache_key] = data.copy()
        self.cache_access_times[cache_key] = datetime.now()
    
    def _evict_cache(self):
        """Éviction LRU du cache"""
        if not self.cache_access_times:
            return
        
        oldest_key = min(self.cache_access_times.keys(),
                        key=lambda k: self.cache_access_times[k])
        
        if oldest_key in self.transformation_cache:
            del self.transformation_cache[oldest_key]
        if oldest_key in self.cache_access_times:
            del self.cache_access_times[oldest_key]
    
    # Transformateurs intégrés
    
    def _polynomial_features_transformer(self, degree: int = 2, include_bias: bool = False):
        """Transformateur de features polynomiales"""
        from sklearn.preprocessing import PolynomialFeatures
        return PolynomialFeatures(degree=degree, include_bias=include_bias)
    
    def _interaction_features_transformer(self, max_combinations: int = 2):
        """Transformateur de features d'interaction"""
        def transform(data):
            result = data.copy()
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) >= 2:
                for i, col1 in enumerate(numeric_cols):
                    for j, col2 in enumerate(numeric_cols[i+1:], i+1):
                        if len(result.columns) < len(data.columns) + max_combinations:
                            interaction_name = f"{col1}_x_{col2}"
                            result[interaction_name] = data[col1] * data[col2]
            
            return result
        return transform
    
    def _time_features_transformer(self, datetime_columns: List[str] = None):
        """Transformateur de features temporelles"""
        def transform(data):
            result = data.copy()
            
            if datetime_columns:
                target_cols = datetime_columns
            else:
                target_cols = data.select_dtypes(include=['datetime64']).columns
            
            for col in target_cols:
                if col in data.columns:
                    dt_col = pd.to_datetime(data[col])
                    result[f"{col}_year"] = dt_col.dt.year
                    result[f"{col}_month"] = dt_col.dt.month
                    result[f"{col}_day"] = dt_col.dt.day
                    result[f"{col}_hour"] = dt_col.dt.hour
                    result[f"{col}_dayofweek"] = dt_col.dt.dayofweek
                    result[f"{col}_quarter"] = dt_col.dt.quarter
            
            return result
        return transform
    
    def _text_features_transformer(self, text_columns: List[str] = None, max_features: int = 100):
        """Transformateur de features textuelles"""
        def transform(data):
            result = data.copy()
            
            if text_columns:
                target_cols = text_columns
            else:
                target_cols = data.select_dtypes(include=['object']).columns
            
            for col in target_cols:
                if col in data.columns:
                    text_data = data[col].astype(str)
                    result[f"{col}_length"] = text_data.str.len()
                    result[f"{col}_word_count"] = text_data.str.split().str.len()
                    result[f"{col}_char_count"] = text_data.str.replace(' ', '').str.len()
            
            return result
        return transform
    
    # Boucles de maintenance
    
    async def _monitoring_loop(self):
        """Boucle de monitoring"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Toutes les minutes
                
                # Calculer le taux de cache hit
                total_requests = (self.execution_metrics["total_pipelines_run"] *
                                len(self.pipelines) if self.pipelines else 1)
                cache_hits = len(self.transformation_cache)
                self.execution_metrics["cache_hit_rate"] = cache_hits / max(total_requests, 1)
                
                # Log des métriques
                logger.info(
                    f"Pipeline metrics - "
                    f"Running: {len(self.running_pipelines)}, "
                    f"Total runs: {self.execution_metrics['total_pipelines_run']}, "
                    f"Success rate: {self.execution_metrics['successful_runs'] / max(self.execution_metrics['total_pipelines_run'], 1):.2%}, "
                    f"Avg time: {self.execution_metrics['average_execution_time']:.2f}s, "
                    f"Cache hit rate: {self.execution_metrics['cache_hit_rate']:.2%}"
                )
                
            except Exception as e:
                logger.error(f"Erreur boucle monitoring: {e}")
    
    async def _cache_cleanup_loop(self):
        """Boucle de nettoyage du cache"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Toutes les heures
                
                # Nettoyer les entrées anciennes
                cutoff_time = datetime.now() - timedelta(hours=24)
                keys_to_remove = [
                    key for key, access_time in self.cache_access_times.items()
                    if access_time < cutoff_time
                ]
                
                for key in keys_to_remove:
                    if key in self.transformation_cache:
                        del self.transformation_cache[key]
                    if key in self.cache_access_times:
                        del self.cache_access_times[key]
                
                logger.debug(f"Cache cleanup: {len(keys_to_remove)} entrées supprimées")
                
            except Exception as e:
                logger.error(f"Erreur nettoyage cache: {e}")
    
    # API publique
    
    def get_pipeline_run(self, run_id: str) -> Optional[PipelineRun]:
        """Récupère une exécution de pipeline"""
        return self.pipeline_runs.get(run_id)
    
    def list_pipelines(self) -> List[str]:
        """Liste les pipelines enregistrés"""
        return list(self.pipelines.keys())
    
    def get_pipeline_config(self, pipeline_id: str) -> Optional[PipelineConfig]:
        """Récupère la configuration d'un pipeline"""
        return self.pipelines.get(pipeline_id)
    
    def get_execution_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques d'exécution"""
        return self.execution_metrics.copy()
    
    def add_pipeline_callback(self, pipeline_id: str, callback: Callable):
        """Ajoute un callback pour un pipeline"""
        self.pipeline_callbacks[pipeline_id].append(callback)
    
    def add_feature_callback(self, callback: Callable):
        """Ajoute un callback pour les features"""
        self.feature_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable):
        """Ajoute un callback pour les erreurs"""
        self.error_callbacks.append(callback)
    
    async def cancel_pipeline_run(self, run_id: str) -> bool:
        """Annule une exécution de pipeline"""
        try:
            if run_id in self.running_pipelines:
                task = self.running_pipelines[run_id]
                task.cancel()
                
                pipeline_run = self.pipeline_runs.get(run_id)
                if pipeline_run:
                    pipeline_run.status = PipelineStatus.CANCELLED
                    pipeline_run.end_time = datetime.now()
                
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur annulation pipeline {run_id}: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification de santé"""
        return {
            "status": "healthy" if self.is_running else "stopped",
            "registered_pipelines": len(self.pipelines),
            "running_pipelines": len(self.running_pipelines),
            "cached_transformations": len(self.transformation_cache),
            "total_runs": self.execution_metrics["total_pipelines_run"],
            "success_rate": (self.execution_metrics["successful_runs"] / 
                            max(self.execution_metrics["total_pipelines_run"], 1)),
            "cache_hit_rate": self.execution_metrics["cache_hit_rate"]
        }


# Factory pour créer des orchestrateurs spécialisés
class PipelineOrchestratorFactory:
    """Factory pour créer des orchestrateurs spécialisés"""
    
    @staticmethod
    def create_production_orchestrator() -> FeaturePipelineOrchestrator:
        """Orchestrateur pour production"""
        return FeaturePipelineOrchestrator(
            max_concurrent_pipelines=20,
            global_cache_size=5000,
            enable_distributed_execution=True
        )
    
    @staticmethod
    def create_development_orchestrator() -> FeaturePipelineOrchestrator:
        """Orchestrateur pour développement"""
        return FeaturePipelineOrchestrator(
            max_concurrent_pipelines=5,
            global_cache_size=100,
            enable_distributed_execution=False
        )


# Exemple d'utilisation
async def example_usage():
    """Exemple d'utilisation de l'orchestrateur"""
    
    import pandas as pd
    import numpy as np
    from sklearn.datasets import make_classification
    
    # Créer des données d'exemple
    X, y = make_classification(n_samples=1000, n_features=10, random_state=42)
    data = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(10)])
    data['target'] = y
    data['timestamp'] = pd.date_range('2023-01-01', periods=1000, freq='1H')
    data['text_data'] = [f"sample text {i}" for i in range(1000)]
    
    # Créer l'orchestrateur
    orchestrator = PipelineOrchestratorFactory.create_development_orchestrator()
    
    try:
        await orchestrator.start()
        
        # Définir les étapes de transformation
        steps = [
            # Étape 1: Normalisation
            TransformationStep(
                step_id="normalize",
                name="Normalisation des features numériques",
                transformation_type=TransformationType.SCALING,
                transformer="standard_scaler",
                input_features=[f"feature_{i}" for i in range(5)],
                output_features=[f"feature_{i}_normalized" for i in range(5)],
                parameters={}
            ),
            
            # Étape 2: Features temporelles
            TransformationStep(
                step_id="time_features",
                name="Extraction de features temporelles",
                transformation_type=TransformationType.DERIVATION,
                transformer="time_features",
                input_features=["timestamp"],
                output_features=["timestamp_year", "timestamp_month", "timestamp_day", 
                               "timestamp_hour", "timestamp_dayofweek", "timestamp_quarter"],
                parameters={"datetime_columns": ["timestamp"]}
            ),
            
            # Étape 3: Features de texte
            TransformationStep(
                step_id="text_features",
                name="Extraction de features textuelles",
                transformation_type=TransformationType.DERIVATION,
                transformer="text_features",
                input_features=["text_data"],
                output_features=["text_data_length", "text_data_word_count", "text_data_char_count"],
                parameters={"text_columns": ["text_data"]}
            ),
            
            # Étape 4: Features d'interaction (dépend de la normalisation)
            TransformationStep(
                step_id="interactions",
                name="Features d'interaction",
                transformation_type=TransformationType.DERIVATION,
                transformer="interaction_features",
                input_features=[f"feature_{i}_normalized" for i in range(3)],
                output_features=["interaction_0_1", "interaction_0_2", "interaction_1_2"],
                parameters={"max_combinations": 3},
                dependencies=["normalize"]
            )
        ]
        
        # Configuration du pipeline
        config = PipelineConfig(
            pipeline_id="example_pipeline",
            name="Pipeline d'exemple de feature engineering",
            description="Pipeline de démonstration avec différents types de transformations",
            execution_mode=ExecutionMode.PARALLEL,
            max_workers=4,
            enable_caching=True,
            enable_validation=True
        )
        
        # Enregistrer le pipeline
        success = await orchestrator.register_pipeline(config, steps)
        if not success:
            print("Erreur enregistrement pipeline")
            return
        
        print("Pipeline enregistré avec succès")
        
        # Exécuter le pipeline
        run_id = await orchestrator.execute_pipeline(
            "example_pipeline",
            data,
            "demo_run"
        )
        
        print(f"Exécution démarrée: {run_id}")
        
        # Attendre la completion
        while True:
            run_info = orchestrator.get_pipeline_run(run_id)
            if run_info and run_info.status in [PipelineStatus.COMPLETED, PipelineStatus.FAILED]:
                break
            await asyncio.sleep(1)
        
        # Afficher les résultats
        final_run = orchestrator.get_pipeline_run(run_id)
        if final_run:
            print(f"\nRésultats de l'exécution:")
            print(f"- Statut: {final_run.status.value}")
            print(f"- Durée: {(final_run.end_time - final_run.start_time).total_seconds():.2f}s")
            print(f"- Features générées: {final_run.output_features_count}")
            print(f"- Métriques: {final_run.execution_metrics}")
        
        # Métriques globales
        metrics = orchestrator.get_execution_metrics()
        print(f"\nMétriques globales: {metrics}")
        
        # Santé du système
        health = await orchestrator.health_check()
        print(f"\nSanté système: {health}")
        
    finally:
        await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(example_usage())