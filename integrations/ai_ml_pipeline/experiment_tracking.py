"""🧪 Experiment Tracking System - Enterprise ML Experiment Management
=====================================================================

Système de tracking d'expérimentations ML avec versioning, comparaison,
collaboration et reproductibilité pour la plateforme Ainflue.

Expert Roles Implementation:
🧠 ML Engineer: Experiment design + metrics tracking + model comparison
🤖 Lead Dev IA: Orchestration expérimentations + optimization strategies
🏗️ Backend Senior: Architecture scalable + distributed experiment management
⚙️ DevOps: MLOps automation + CI/CD intégration + experiment pipelines
🔒 Sécurité: Experiment security + access control + audit trails
🗄️ DBA: Experiment metadata storage + versioning + performance tracking
🔗 Microservices: Experiment services communication + load balancing
🎨 IA Prompt Engineer: Prompt experimentation + A/B testing + quality metrics

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0 Enterprise
Date: December 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture experiment tracking est la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).

Toute utilisation, reproduction, modification, ou distribution de cette 
architecture IA/ML, de ces algorithmes, ou de ce code source sans 
autorisation écrite EXPLICITE de Fahed Mlaiel constitue une violation 
grave des droits de propriété intellectuelle.

📧 Demandes d'autorisation : mlaiel@live.de
🚫 USAGE NON AUTORISÉ = POURSUITES JUDICIAIRES IMMÉDIATES
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
import pickle
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import numpy as np
import aiohttp
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from concurrent.futures import ThreadPoolExecutor
import queue
import statistics
import sqlite3
import tempfile
import shutil
import boto3
from botocore.exceptions import NoCredentialsError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExperimentStatus(Enum):
    """Status des expérimentations ML"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class ExperimentType(Enum):
    """Types d'expérimentations ML"""
    TRAINING = "training"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    ARCHITECTURE_SEARCH = "architecture_search"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_COMPARISON = "model_comparison"
    A_B_TESTING = "a_b_testing"
    PROMPT_OPTIMIZATION = "prompt_optimization"
    CONTENT_ANALYSIS = "content_analysis"

class MetricType(Enum):
    """Types de métriques d'expérimentation"""
    ACCURACY = "accuracy"
    LOSS = "loss"
    F1_SCORE = "f1_score"
    PRECISION = "precision"
    RECALL = "recall"
    AUC_ROC = "auc_roc"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    MEMORY_USAGE = "memory_usage"
    GPU_UTILIZATION = "gpu_utilization"
    TRAINING_TIME = "training_time"
    INFERENCE_TIME = "inference_time"
    BUSINESS_KPI = "business_kpi"
    CONTENT_QUALITY = "content_quality"
    CREATOR_SATISFACTION = "creator_satisfaction"
    ENGAGEMENT_RATE = "engagement_rate"
    MONETIZATION_EFFICIENCY = "monetization_efficiency"

@dataclass
class ExperimentParameter:
    """Paramètre d'expérimentation ML"""
    name: str
    value: Any
    parameter_type: str  # "hyperparameter", "config", "data"
    is_tunable: bool = False
    search_space: Optional[Dict[str, Any]] = None
    importance: float = 1.0

@dataclass
class ExperimentMetric:
    """Métrique d'expérimentation ML"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    step: Optional[int] = None
    epoch: Optional[int] = None
    is_primary: bool = False
    higher_is_better: bool = True
    confidence_interval: Optional[Tuple[float, float]] = None

@dataclass
class ExperimentArtifact:
    """Artifact d'expérimentation ML"""
    name: str
    artifact_type: str  # "model", "dataset", "plot", "log", "config"
    file_path: str
    size_bytes: int
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ExperimentRun:
    """Run d'expérimentation ML complet"""
    experiment_id: str
    run_id: str
    run_name: str
    experiment_type: ExperimentType
    status: ExperimentStatus
    parameters: Dict[str, ExperimentParameter]
    metrics: Dict[str, List[ExperimentMetric]]
    artifacts: Dict[str, ExperimentArtifact]
    tags: Dict[str, str]
    creator_id: Optional[str] = None
    creator_type: Optional[str] = None
    platform_target: Optional[str] = None
    content_type: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    parent_run_id: Optional[str] = None
    child_runs: List[str] = field(default_factory=list)
    notes: str = ""
    error_message: Optional[str] = None
    git_commit: Optional[str] = None
    environment_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExperimentComparison:
    """Comparaison d'expérimentations ML"""
    comparison_id: str
    experiment_runs: List[str]
    primary_metric: str
    comparison_results: Dict[str, Any]
    statistical_significance: Dict[str, float]
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None

class ExperimentTrackingSystem:
    """🧪 ML Engineer - Système de tracking d'expérimentations enterprise"""
    
    def __init__(self, 
                 storage_backend: str = "local",
                 redis_url: str = "redis://localhost:6379",
                 database_path: str = "experiments.db",
                 s3_bucket: Optional[str] = None,
                 artifact_storage_path: str = "./experiment_artifacts"):
        """
        Initialise le système de tracking d'expérimentations
        
        Args:
            storage_backend: Backend de stockage ("local", "s3", "hybrid")
            redis_url: URL Redis pour le cache
            database_path: Chemin de la base de données SQLite
            s3_bucket: Bucket S3 pour les artifacts (optionnel)
            artifact_storage_path: Chemin local pour les artifacts
        """
        self.storage_backend = storage_backend
        self.redis_url = redis_url
        self.database_path = database_path
        self.s3_bucket = s3_bucket
        self.artifact_storage_path = Path(artifact_storage_path)
        
        # Créer le dossier d'artifacts
        self.artifact_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Composants
        self.redis_client = None
        self.db_connection = None
        self.s3_client = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # État
        self.active_runs: Dict[str, ExperimentRun] = {}
        self.experiments_cache: Dict[str, List[ExperimentRun]] = {}
        self.metrics_buffer: Dict[str, List[ExperimentMetric]] = {}
        
        # Initialiser
        asyncio.create_task(self._initialize())
    
    async def _initialize(self):
        """🔧 DevOps - Initialisation des composants"""
        try:
            # Initialiser Redis
            self.redis_client = await aioredis.from_url(self.redis_url)
            
            # Initialiser la base de données
            await self._initialize_database()
            
            # Initialiser S3 si configuré
            if self.storage_backend in ["s3", "hybrid"] and self.s3_bucket:
                self.s3_client = boto3.client('s3')
            
            logger.info("🧪 Experiment tracking system initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize experiment tracking: {e}")
            raise
    
    async def _initialize_database(self):
        """🗄️ DBA - Initialisation de la base de données"""
        self.db_connection = sqlite3.connect(self.database_path, check_same_thread=False)
        
        # Créer les tables
        cursor = self.db_connection.cursor()
        
        # Table des expérimentations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id TEXT PRIMARY KEY,
                experiment_name TEXT NOT NULL,
                experiment_type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                tags TEXT,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Table des runs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiment_runs (
                run_id TEXT PRIMARY KEY,
                experiment_id TEXT NOT NULL,
                run_name TEXT NOT NULL,
                status TEXT NOT NULL,
                experiment_type TEXT NOT NULL,
                parameters TEXT,
                tags TEXT,
                creator_id TEXT,
                creator_type TEXT,
                platform_target TEXT,
                content_type TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                duration_seconds REAL,
                parent_run_id TEXT,
                notes TEXT,
                error_message TEXT,
                git_commit TEXT,
                environment_info TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments (experiment_id)
            )
        """)
        
        # Table des métriques
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiment_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_type TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                step INTEGER,
                epoch INTEGER,
                is_primary BOOLEAN DEFAULT FALSE,
                higher_is_better BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (run_id) REFERENCES experiment_runs (run_id)
            )
        """)
        
        # Table des artifacts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiment_artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                artifact_name TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                size_bytes INTEGER,
                checksum TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES experiment_runs (run_id)
            )
        """)
        
        # Index pour les performances
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_experiment_id ON experiment_runs (experiment_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_run_id ON experiment_metrics (run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_run_id ON experiment_artifacts (run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_status ON experiment_runs (status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_created_at ON experiment_runs (started_at)")
        
        self.db_connection.commit()
        logger.info("🗄️ Database initialized with experiment tracking schema")
    
    async def create_experiment(self,
                              experiment_name: str,
                              experiment_type: ExperimentType,
                              description: str = "",
                              tags: Dict[str, str] = None,
                              created_by: str = None) -> str:
        """🧠 ML Engineer - Créer une nouvelle expérimentation"""
        
        experiment_id = f"exp_{uuid.uuid4().hex[:12]}"
        tags = tags or {}
        
        try:
            # Enregistrer en base
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO experiments 
                (experiment_id, experiment_name, experiment_type, description, created_by, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                experiment_id,
                experiment_name,
                experiment_type.value,
                description,
                created_by,
                json.dumps(tags)
            ))
            self.db_connection.commit()
            
            # Cache Redis
            await self.redis_client.hset(
                f"experiment:{experiment_id}",
                mapping={
                    "name": experiment_name,
                    "type": experiment_type.value,
                    "description": description,
                    "created_by": created_by or "",
                    "created_at": datetime.now().isoformat(),
                    "tags": json.dumps(tags)
                }
            )
            
            logger.info(f"🧪 Created experiment: {experiment_name} ({experiment_id})")
            return experiment_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create experiment: {e}")
            raise
    
    async def start_experiment_run(self,
                                 experiment_id: str,
                                 run_name: str,
                                 parameters: Dict[str, Any] = None,
                                 tags: Dict[str, str] = None,
                                 creator_id: str = None,
                                 creator_type: str = None,
                                 platform_target: str = None,
                                 content_type: str = None,
                                 parent_run_id: str = None) -> str:
        """🤖 Lead Dev IA - Démarrer un run d'expérimentation"""
        
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        parameters = parameters or {}
        tags = tags or {}
        
        # Créer les paramètres d'expérimentation
        exp_parameters = {}
        for name, value in parameters.items():
            exp_parameters[name] = ExperimentParameter(
                name=name,
                value=value,
                parameter_type="hyperparameter"
            )
        
        # Obtenir le type d'expérimentation
        experiment_info = await self.redis_client.hgetall(f"experiment:{experiment_id}")
        experiment_type = ExperimentType(experiment_info.get("type", "training"))
        
        # Créer le run
        run = ExperimentRun(
            experiment_id=experiment_id,
            run_id=run_id,
            run_name=run_name,
            experiment_type=experiment_type,
            status=ExperimentStatus.RUNNING,
            parameters=exp_parameters,
            metrics={},
            artifacts={},
            tags=tags,
            creator_id=creator_id,
            creator_type=creator_type,
            platform_target=platform_target,
            content_type=content_type,
            started_at=datetime.now(),
            parent_run_id=parent_run_id
        )
        
        try:
            # Enregistrer en base
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO experiment_runs 
                (run_id, experiment_id, run_name, status, experiment_type, parameters, 
                 tags, creator_id, creator_type, platform_target, content_type, 
                 started_at, parent_run_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id, experiment_id, run_name, run.status.value, 
                run.experiment_type.value, json.dumps({k: v.value for k, v in exp_parameters.items()}),
                json.dumps(tags), creator_id, creator_type, platform_target, 
                content_type, run.started_at.isoformat(), parent_run_id
            ))
            self.db_connection.commit()
            
            # Ajouter aux runs actifs
            self.active_runs[run_id] = run
            
            # Cache Redis
            await self.redis_client.hset(
                f"run:{run_id}",
                mapping={
                    "experiment_id": experiment_id,
                    "run_name": run_name,
                    "status": run.status.value,
                    "started_at": run.started_at.isoformat(),
                    "creator_id": creator_id or "",
                    "creator_type": creator_type or "",
                    "platform_target": platform_target or "",
                    "content_type": content_type or ""
                }
            )
            
            logger.info(f"🚀 Started experiment run: {run_name} ({run_id})")
            return run_id
            
        except Exception as e:
            logger.error(f"❌ Failed to start experiment run: {e}")
            raise
    
    async def log_metric(self,
                        run_id: str,
                        metric_name: str,
                        value: float,
                        metric_type: MetricType = MetricType.ACCURACY,
                        step: int = None,
                        epoch: int = None,
                        is_primary: bool = False,
                        higher_is_better: bool = True):
        """📊 Analytics - Logger une métrique d'expérimentation"""
        
        if run_id not in self.active_runs:
            logger.warning(f"⚠️ Run {run_id} not found in active runs")
            return
        
        metric = ExperimentMetric(
            name=metric_name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            step=step,
            epoch=epoch,
            is_primary=is_primary,
            higher_is_better=higher_is_better
        )
        
        try:
            # Ajouter au run actif
            if metric_name not in self.active_runs[run_id].metrics:
                self.active_runs[run_id].metrics[metric_name] = []
            self.active_runs[run_id].metrics[metric_name].append(metric)
            
            # Buffer pour batch insert
            if run_id not in self.metrics_buffer:
                self.metrics_buffer[run_id] = []
            self.metrics_buffer[run_id].append(metric)
            
            # Flush si le buffer est plein
            if len(self.metrics_buffer[run_id]) >= 100:
                await self._flush_metrics_buffer(run_id)
            
            # Cache Redis pour les métriques courantes
            await self.redis_client.hset(
                f"run:{run_id}:metrics",
                metric_name,
                json.dumps({
                    "value": value,
                    "type": metric_type.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "step": step,
                    "epoch": epoch,
                    "is_primary": is_primary
                })
            )
            
            logger.debug(f"📊 Logged metric {metric_name}={value} for run {run_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log metric: {e}")
    
    async def _flush_metrics_buffer(self, run_id: str):
        """🗄️ DBA - Flush des métriques en buffer vers la DB"""
        
        if run_id not in self.metrics_buffer or not self.metrics_buffer[run_id]:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            metrics_data = []
            for metric in self.metrics_buffer[run_id]:
                metrics_data.append((
                    run_id,
                    metric.name,
                    metric.value,
                    metric.metric_type.value,
                    metric.timestamp.isoformat(),
                    metric.step,
                    metric.epoch,
                    metric.is_primary,
                    metric.higher_is_better
                ))
            
            cursor.executemany("""
                INSERT INTO experiment_metrics 
                (run_id, metric_name, metric_value, metric_type, timestamp, 
                 step, epoch, is_primary, higher_is_better)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, metrics_data)
            
            self.db_connection.commit()
            
            # Vider le buffer
            self.metrics_buffer[run_id] = []
            
            logger.debug(f"💾 Flushed {len(metrics_data)} metrics for run {run_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to flush metrics buffer: {e}")
    
    async def log_artifact(self,
                          run_id: str,
                          artifact_name: str,
                          artifact_path: str,
                          artifact_type: str = "model",
                          metadata: Dict[str, Any] = None) -> str:
        """💾 Storage - Logger un artifact d'expérimentation"""
        
        if run_id not in self.active_runs:
            logger.warning(f"⚠️ Run {run_id} not found in active runs")
            return ""
        
        metadata = metadata or {}
        
        try:
            # Calculer checksum
            checksum = await self._calculate_file_checksum(artifact_path)
            file_size = Path(artifact_path).stat().st_size
            
            # Destination de stockage
            storage_path = self.artifact_storage_path / run_id / artifact_name
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copier le fichier
            shutil.copy2(artifact_path, storage_path)
            
            # Uploader vers S3 si configuré
            s3_path = None
            if self.storage_backend in ["s3", "hybrid"] and self.s3_client:
                s3_key = f"experiments/{run_id}/artifacts/{artifact_name}"
                self.s3_client.upload_file(str(storage_path), self.s3_bucket, s3_key)
                s3_path = f"s3://{self.s3_bucket}/{s3_key}"
            
            # Créer l'artifact
            artifact = ExperimentArtifact(
                name=artifact_name,
                artifact_type=artifact_type,
                file_path=str(storage_path) if self.storage_backend == "local" else s3_path,
                size_bytes=file_size,
                checksum=checksum,
                metadata=metadata
            )
            
            # Ajouter au run
            self.active_runs[run_id].artifacts[artifact_name] = artifact
            
            # Enregistrer en base
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO experiment_artifacts 
                (run_id, artifact_name, artifact_type, file_path, size_bytes, checksum, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id, artifact_name, artifact_type, artifact.file_path,
                file_size, checksum, json.dumps(metadata)
            ))
            self.db_connection.commit()
            
            logger.info(f"💾 Logged artifact {artifact_name} for run {run_id}")
            return artifact.file_path
            
        except Exception as e:
            logger.error(f"❌ Failed to log artifact: {e}")
            return ""
    
    async def _calculate_file_checksum(self, file_path: str) -> str:
        """🔒 Security - Calculer le checksum d'un fichier"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def end_experiment_run(self,
                               run_id: str,
                               status: ExperimentStatus = ExperimentStatus.COMPLETED,
                               error_message: str = None):
        """🏁 Completion - Terminer un run d'expérimentation"""
        
        if run_id not in self.active_runs:
            logger.warning(f"⚠️ Run {run_id} not found in active runs")
            return
        
        try:
            run = self.active_runs[run_id]
            run.status = status
            run.completed_at = datetime.now()
            run.error_message = error_message
            
            if run.started_at:
                run.duration_seconds = (run.completed_at - run.started_at).total_seconds()
            
            # Flush remaining metrics
            await self._flush_metrics_buffer(run_id)
            
            # Mettre à jour en base
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE experiment_runs 
                SET status = ?, completed_at = ?, duration_seconds = ?, error_message = ?
                WHERE run_id = ?
            """, (
                status.value, 
                run.completed_at.isoformat(),
                run.duration_seconds,
                error_message,
                run_id
            ))
            self.db_connection.commit()
            
            # Mettre à jour Redis
            await self.redis_client.hset(
                f"run:{run_id}",
                mapping={
                    "status": status.value,
                    "completed_at": run.completed_at.isoformat(),
                    "duration_seconds": str(run.duration_seconds) if run.duration_seconds else "0"
                }
            )
            
            # Retirer des runs actifs
            del self.active_runs[run_id]
            
            logger.info(f"🏁 Ended experiment run {run_id} with status {status.value}")
            
        except Exception as e:
            logger.error(f"❌ Failed to end experiment run: {e}")
    
    async def get_experiment_runs(self, 
                                experiment_id: str,
                                status_filter: List[ExperimentStatus] = None,
                                limit: int = 100) -> List[ExperimentRun]:
        """📋 Query - Récupérer les runs d'une expérimentation"""
        
        try:
            cursor = self.db_connection.cursor()
            
            # Base query
            query = """
                SELECT run_id, experiment_id, run_name, status, experiment_type, 
                       parameters, tags, creator_id, creator_type, platform_target, 
                       content_type, started_at, completed_at, duration_seconds, 
                       parent_run_id, notes, error_message
                FROM experiment_runs 
                WHERE experiment_id = ?
            """
            params = [experiment_id]
            
            # Filtre de status
            if status_filter:
                status_values = [s.value for s in status_filter]
                placeholders = ",".join(["?" for _ in status_values])
                query += f" AND status IN ({placeholders})"
                params.extend(status_values)
            
            query += " ORDER BY started_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            runs = []
            for row in rows:
                # Reconstruit le run
                run = ExperimentRun(
                    experiment_id=row[1],
                    run_id=row[0],
                    run_name=row[2],
                    experiment_type=ExperimentType(row[4]),
                    status=ExperimentStatus(row[3]),
                    parameters={},  # Sera chargé séparément si nécessaire
                    metrics={},     # Sera chargé séparément si nécessaire
                    artifacts={},   # Sera chargé séparément si nécessaire
                    tags=json.loads(row[6]) if row[6] else {},
                    creator_id=row[7],
                    creator_type=row[8],
                    platform_target=row[9],
                    content_type=row[10],
                    started_at=datetime.fromisoformat(row[11]) if row[11] else None,
                    completed_at=datetime.fromisoformat(row[12]) if row[12] else None,
                    duration_seconds=row[13],
                    parent_run_id=row[14],
                    notes=row[15] or "",
                    error_message=row[16]
                )
                
                # Charger les paramètres
                if row[5]:
                    params_dict = json.loads(row[5])
                    for name, value in params_dict.items():
                        run.parameters[name] = ExperimentParameter(
                            name=name,
                            value=value,
                            parameter_type="hyperparameter"
                        )
                
                runs.append(run)
            
            return runs
            
        except Exception as e:
            logger.error(f"❌ Failed to get experiment runs: {e}")
            return []
    
    async def compare_experiments(self,
                                run_ids: List[str],
                                primary_metric: str,
                                comparison_name: str = None) -> ExperimentComparison:
        """📊 Analytics - Comparer plusieurs expérimentations"""
        
        comparison_id = f"comp_{uuid.uuid4().hex[:12]}"
        comparison_name = comparison_name or f"Comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Récupérer les métriques pour chaque run
            run_metrics = {}
            statistical_significance = {}
            
            for run_id in run_ids:
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    SELECT metric_value, timestamp 
                    FROM experiment_metrics 
                    WHERE run_id = ? AND metric_name = ?
                    ORDER BY timestamp DESC
                """, (run_id, primary_metric))
                
                metrics = cursor.fetchall()
                if metrics:
                    # Prendre la dernière valeur
                    run_metrics[run_id] = metrics[0][0]
            
            # Calculs statistiques simples
            if len(run_metrics) >= 2:
                values = list(run_metrics.values())
                mean_value = statistics.mean(values)
                std_value = statistics.stdev(values) if len(values) > 1 else 0
                
                # Calculer la significativité relative
                for run_id, value in run_metrics.items():
                    if std_value > 0:
                        z_score = abs(value - mean_value) / std_value
                        statistical_significance[run_id] = min(z_score, 5.0)  # Cap à 5
                    else:
                        statistical_significance[run_id] = 0.0
            
            # Générer des recommandations
            recommendations = []
            if run_metrics:
                best_run = max(run_metrics.items(), key=lambda x: x[1])
                worst_run = min(run_metrics.items(), key=lambda x: x[1])
                
                recommendations.append(f"Best performing run: {best_run[0]} ({primary_metric}: {best_run[1]:.4f})")
                
                if len(run_metrics) > 1:
                    improvement = ((best_run[1] - worst_run[1]) / worst_run[1]) * 100
                    recommendations.append(f"Performance improvement: {improvement:.2f}%")
                
                if std_value > 0:
                    recommendations.append(f"Standard deviation: {std_value:.4f}")
            
            # Créer la comparaison
            comparison = ExperimentComparison(
                comparison_id=comparison_id,
                experiment_runs=run_ids,
                primary_metric=primary_metric,
                comparison_results={
                    "run_metrics": run_metrics,
                    "mean_value": mean_value if 'mean_value' in locals() else 0,
                    "std_value": std_value if 'std_value' in locals() else 0,
                    "best_run": best_run[0] if 'best_run' in locals() else None,
                    "best_value": best_run[1] if 'best_run' in locals() else None
                },
                statistical_significance=statistical_significance,
                recommendations=recommendations
            )
            
            logger.info(f"📊 Created experiment comparison: {comparison_id}")
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Failed to compare experiments: {e}")
            return None
    
    async def search_experiments(self,
                               query: str = "",
                               experiment_type: ExperimentType = None,
                               creator_id: str = None,
                               creator_type: str = None,
                               date_range: Tuple[datetime, datetime] = None,
                               tags: Dict[str, str] = None,
                               limit: int = 50) -> List[ExperimentRun]:
        """🔍 Search - Rechercher des expérimentations"""
        
        try:
            cursor = self.db_connection.cursor()
            
            # Base query
            base_query = """
                SELECT run_id, experiment_id, run_name, status, experiment_type, 
                       parameters, tags, creator_id, creator_type, platform_target, 
                       content_type, started_at, completed_at, duration_seconds, 
                       parent_run_id, notes, error_message
                FROM experiment_runs 
                WHERE 1=1
            """
            params = []
            
            # Filtre par nom
            if query:
                base_query += " AND (run_name LIKE ? OR notes LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            # Filtre par type
            if experiment_type:
                base_query += " AND experiment_type = ?"
                params.append(experiment_type.value)
            
            # Filtre par créateur
            if creator_id:
                base_query += " AND creator_id = ?"
                params.append(creator_id)
            
            if creator_type:
                base_query += " AND creator_type = ?"
                params.append(creator_type)
            
            # Filtre par date
            if date_range:
                base_query += " AND started_at BETWEEN ? AND ?"
                params.extend([date_range[0].isoformat(), date_range[1].isoformat()])
            
            base_query += " ORDER BY started_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                run = ExperimentRun(
                    experiment_id=row[1],
                    run_id=row[0],
                    run_name=row[2],
                    experiment_type=ExperimentType(row[4]),
                    status=ExperimentStatus(row[3]),
                    parameters={},
                    metrics={},
                    artifacts={},
                    tags=json.loads(row[6]) if row[6] else {},
                    creator_id=row[7],
                    creator_type=row[8],
                    platform_target=row[9],
                    content_type=row[10],
                    started_at=datetime.fromisoformat(row[11]) if row[11] else None,
                    completed_at=datetime.fromisoformat(row[12]) if row[12] else None,
                    duration_seconds=row[13],
                    parent_run_id=row[14],
                    notes=row[15] or "",
                    error_message=row[16]
                )
                
                # Filtre par tags si spécifié
                if tags:
                    run_tags = run.tags
                    tag_match = all(
                        run_tags.get(key) == value 
                        for key, value in tags.items()
                    )
                    if tag_match:
                        results.append(run)
                else:
                    results.append(run)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to search experiments: {e}")
            return []
    
    async def get_experiment_analytics(self, experiment_id: str) -> Dict[str, Any]:
        """📈 Analytics - Obtenir les analytics d'une expérimentation"""
        
        try:
            cursor = self.db_connection.cursor()
            
            # Statistiques générales
            cursor.execute("""
                SELECT COUNT(*) as total_runs,
                       COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_runs,
                       COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_runs,
                       AVG(duration_seconds) as avg_duration,
                       MIN(started_at) as first_run,
                       MAX(started_at) as last_run
                FROM experiment_runs 
                WHERE experiment_id = ?
            """, (experiment_id,))
            
            stats = cursor.fetchone()
            
            # Métriques par run
            cursor.execute("""
                SELECT r.run_id, r.run_name, m.metric_name, m.metric_value, 
                       m.is_primary, r.creator_type, r.platform_target
                FROM experiment_runs r
                LEFT JOIN experiment_metrics m ON r.run_id = m.run_id
                WHERE r.experiment_id = ? AND m.is_primary = 1
                ORDER BY r.started_at DESC
            """, (experiment_id,))
            
            metrics_data = cursor.fetchall()
            
            # Organiser les données
            runs_performance = {}
            metric_trends = {}
            creator_performance = {}
            platform_performance = {}
            
            for row in metrics_data:
                run_id, run_name, metric_name, metric_value, is_primary, creator_type, platform_target = row
                
                if metric_name:
                    # Performance par run
                    if run_id not in runs_performance:
                        runs_performance[run_id] = {"name": run_name, "metrics": {}}
                    runs_performance[run_id]["metrics"][metric_name] = metric_value
                    
                    # Trends des métriques
                    if metric_name not in metric_trends:
                        metric_trends[metric_name] = []
                    metric_trends[metric_name].append(metric_value)
                    
                    # Performance par créateur
                    if creator_type:
                        if creator_type not in creator_performance:
                            creator_performance[creator_type] = []
                        creator_performance[creator_type].append(metric_value)
                    
                    # Performance par plateforme
                    if platform_target:
                        if platform_target not in platform_performance:
                            platform_performance[platform_target] = []
                        platform_performance[platform_target].append(metric_value)
            
            # Calculer les moyennes
            creator_avg = {
                creator: statistics.mean(values) 
                for creator, values in creator_performance.items()
            }
            
            platform_avg = {
                platform: statistics.mean(values) 
                for platform, values in platform_performance.items()
            }
            
            return {
                "experiment_id": experiment_id,
                "general_stats": {
                    "total_runs": stats[0],
                    "completed_runs": stats[1],
                    "failed_runs": stats[2],
                    "success_rate": (stats[1] / stats[0] * 100) if stats[0] > 0 else 0,
                    "avg_duration_seconds": stats[3],
                    "first_run": stats[4],
                    "last_run": stats[5]
                },
                "runs_performance": runs_performance,
                "metric_trends": {
                    metric: {
                        "values": values,
                        "mean": statistics.mean(values),
                        "std": statistics.stdev(values) if len(values) > 1 else 0,
                        "min": min(values),
                        "max": max(values)
                    }
                    for metric, values in metric_trends.items()
                },
                "creator_performance": creator_avg,
                "platform_performance": platform_avg,
                "recommendations": self._generate_recommendations(
                    stats, metric_trends, creator_avg, platform_avg
                )
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get experiment analytics: {e}")
            return {}
    
    def _generate_recommendations(self, 
                                stats: tuple, 
                                metric_trends: Dict[str, List[float]],
                                creator_performance: Dict[str, float],
                                platform_performance: Dict[str, float]) -> List[str]:
        """🎯 AI Optimization - Générer des recommandations intelligentes"""
        
        recommendations = []
        
        # Recommandations basées sur le taux de succès
        if stats[0] > 0:
            success_rate = (stats[1] / stats[0]) * 100
            if success_rate < 70:
                recommendations.append("🔧 Consider reviewing experiment setup - low success rate detected")
            elif success_rate > 90:
                recommendations.append("✅ Excellent experiment success rate - maintain current approach")
        
        # Recommandations basées sur les métriques
        for metric_name, values in metric_trends.items():
            if len(values) > 3:
                recent_trend = values[-3:]
                if all(recent_trend[i] >= recent_trend[i-1] for i in range(1, len(recent_trend))):
                    recommendations.append(f"📈 {metric_name} showing consistent improvement")
                elif all(recent_trend[i] <= recent_trend[i-1] for i in range(1, len(recent_trend))):
                    recommendations.append(f"📉 {metric_name} declining - investigate parameter changes")
        
        # Recommandations créateurs
        if creator_performance:
            best_creator = max(creator_performance.items(), key=lambda x: x[1])
            recommendations.append(f"🏆 Best performing creator type: {best_creator[0]}")
        
        # Recommandations plateformes
        if platform_performance:
            best_platform = max(platform_performance.items(), key=lambda x: x[1])
            recommendations.append(f"🎯 Best performing platform: {best_platform[0]}")
        
        return recommendations
    
    async def export_experiment_data(self, 
                                   experiment_id: str,
                                   export_format: str = "json",
                                   include_artifacts: bool = False) -> str:
        """📤 Export - Exporter les données d'expérimentation"""
        
        try:
            # Récupérer toutes les données
            runs = await self.get_experiment_runs(experiment_id)
            analytics = await self.get_experiment_analytics(experiment_id)
            
            export_data = {
                "experiment_id": experiment_id,
                "exported_at": datetime.now().isoformat(),
                "analytics": analytics,
                "runs": []
            }
            
            # Ajouter les détails des runs
            for run in runs:
                run_data = asdict(run)
                
                # Charger les métriques détaillées
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    SELECT metric_name, metric_value, metric_type, timestamp, 
                           step, epoch, is_primary, higher_is_better
                    FROM experiment_metrics 
                    WHERE run_id = ?
                    ORDER BY timestamp
                """, (run.run_id,))
                
                detailed_metrics = {}
                for metric_row in cursor.fetchall():
                    metric_name = metric_row[0]
                    if metric_name not in detailed_metrics:
                        detailed_metrics[metric_name] = []
                    
                    detailed_metrics[metric_name].append({
                        "value": metric_row[1],
                        "type": metric_row[2],
                        "timestamp": metric_row[3],
                        "step": metric_row[4],
                        "epoch": metric_row[5],
                        "is_primary": bool(metric_row[6]),
                        "higher_is_better": bool(metric_row[7])
                    })
                
                run_data["detailed_metrics"] = detailed_metrics
                
                # Ajouter les artifacts si demandé
                if include_artifacts:
                    cursor.execute("""
                        SELECT artifact_name, artifact_type, file_path, 
                               size_bytes, checksum, metadata
                        FROM experiment_artifacts 
                        WHERE run_id = ?
                    """, (run.run_id,))
                    
                    artifacts_info = []
                    for artifact_row in cursor.fetchall():
                        artifacts_info.append({
                            "name": artifact_row[0],
                            "type": artifact_row[1],
                            "path": artifact_row[2],
                            "size_bytes": artifact_row[3],
                            "checksum": artifact_row[4],
                            "metadata": json.loads(artifact_row[5]) if artifact_row[5] else {}
                        })
                    
                    run_data["artifacts_info"] = artifacts_info
                
                export_data["runs"].append(run_data)
            
            # Créer le fichier d'export
            export_filename = f"experiment_{experiment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
            export_path = self.artifact_storage_path / "exports" / export_filename
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            if export_format == "json":
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
            else:
                # Format CSV pour les métriques principales
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Header
                    writer.writerow(['run_id', 'run_name', 'status', 'creator_type', 
                                   'platform_target', 'started_at', 'duration_seconds'])
                    
                    # Data
                    for run in runs:
                        writer.writerow([
                            run.run_id, run.run_name, run.status.value, 
                            run.creator_type, run.platform_target,
                            run.started_at.isoformat() if run.started_at else "",
                            run.duration_seconds or 0
                        ])
            
            logger.info(f"📤 Exported experiment data to {export_path}")
            return str(export_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to export experiment data: {e}")
            return ""
    
    async def cleanup_old_experiments(self, days_old: int = 90):
        """🧹 Maintenance - Nettoyer les anciennes expérimentations"""
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            cursor = self.db_connection.cursor()
            
            # Trouver les runs à supprimer
            cursor.execute("""
                SELECT run_id FROM experiment_runs 
                WHERE completed_at < ? AND status IN ('completed', 'failed', 'cancelled')
            """, (cutoff_date.isoformat(),))
            
            old_runs = [row[0] for row in cursor.fetchall()]
            
            if not old_runs:
                logger.info("🧹 No old experiments to cleanup")
                return
            
            # Supprimer les artifacts physiques
            deleted_artifacts = 0
            for run_id in old_runs:
                run_artifacts_path = self.artifact_storage_path / run_id
                if run_artifacts_path.exists():
                    shutil.rmtree(run_artifacts_path)
                    deleted_artifacts += 1
            
            # Supprimer de la base de données
            cursor.execute(f"""
                DELETE FROM experiment_metrics 
                WHERE run_id IN ({','.join(['?' for _ in old_runs])})
            """, old_runs)
            
            cursor.execute(f"""
                DELETE FROM experiment_artifacts 
                WHERE run_id IN ({','.join(['?' for _ in old_runs])})
            """, old_runs)
            
            cursor.execute(f"""
                DELETE FROM experiment_runs 
                WHERE run_id IN ({','.join(['?' for _ in old_runs])})
            """, old_runs)
            
            self.db_connection.commit()
            
            # Nettoyer Redis
            for run_id in old_runs:
                await self.redis_client.delete(f"run:{run_id}")
                await self.redis_client.delete(f"run:{run_id}:metrics")
            
            logger.info(f"🧹 Cleaned up {len(old_runs)} old experiment runs and {deleted_artifacts} artifact folders")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old experiments: {e}")
    
    async def get_system_health(self) -> Dict[str, Any]:
        """❤️ Health Check - Vérifier la santé du système"""
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "metrics": {}
        }
        
        try:
            # Vérifier Redis
            try:
                await self.redis_client.ping()
                health_status["components"]["redis"] = "healthy"
            except Exception as e:
                health_status["components"]["redis"] = f"unhealthy: {e}"
                health_status["status"] = "degraded"
            
            # Vérifier la base de données
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM experiment_runs")
                total_runs = cursor.fetchone()[0]
                health_status["components"]["database"] = "healthy"
                health_status["metrics"]["total_runs"] = total_runs
            except Exception as e:
                health_status["components"]["database"] = f"unhealthy: {e}"
                health_status["status"] = "unhealthy"
            
            # Vérifier le stockage
            try:
                storage_free = shutil.disk_usage(self.artifact_storage_path).free
                storage_total = shutil.disk_usage(self.artifact_storage_path).total
                storage_usage = ((storage_total - storage_free) / storage_total) * 100
                
                health_status["components"]["storage"] = "healthy"
                health_status["metrics"]["storage_usage_percent"] = storage_usage
                
                if storage_usage > 90:
                    health_status["components"]["storage"] = "warning: high disk usage"
                    health_status["status"] = "degraded"
                    
            except Exception as e:
                health_status["components"]["storage"] = f"unhealthy: {e}"
                health_status["status"] = "degraded"
            
            # Métriques du système
            health_status["metrics"]["active_runs"] = len(self.active_runs)
            health_status["metrics"]["metrics_buffer_size"] = sum(len(buffer) for buffer in self.metrics_buffer.values())
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Failed to get system health: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Export principal
__all__ = [
    'ExperimentTrackingSystem',
    'ExperimentStatus',
    'ExperimentType', 
    'MetricType',
    'ExperimentParameter',
    'ExperimentMetric',
    'ExperimentArtifact',
    'ExperimentRun',
    'ExperimentComparison'
]