#!/usr/bin/env python3
"""
🚀 Batch Inference Processor - Enterprise MLOps Platform
Backend Senior Expertise: Processeur d'inférence batch optimisé pour gros volumes

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable, Iterator
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing
import time
import sqlite3
import pickle
import gzip
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchProcessingStrategy(Enum):
    """Stratégies de traitement batch"""
    SEQUENTIAL = "sequential"
    PARALLEL_THREADS = "parallel_threads"
    PARALLEL_PROCESSES = "parallel_processes"
    DISTRIBUTED = "distributed"
    ADAPTIVE = "adaptive"

class CreatorBatchType(Enum):
    """Types de batch par créateur"""
    MUSICIAN_AUDIO_ANALYSIS = "musician_audio_analysis"
    MUSICIAN_GENRE_CLASSIFICATION = "musician_genre_classification"
    BLOGGER_CONTENT_SEO = "blogger_content_seo"
    BLOGGER_SENTIMENT_BATCH = "blogger_sentiment_batch"
    PHOTOGRAPHER_IMAGE_BATCH = "photographer_image_batch"
    PHOTOGRAPHER_STYLE_ANALYSIS = "photographer_style_analysis"
    INFLUENCER_ANALYTICS_BULK = "influencer_analytics_bulk"
    INFLUENCER_TREND_ANALYSIS = "influencer_trend_analysis"
    COMEDIAN_HUMOR_ANALYSIS = "comedian_humor_analysis"
    COMEDIAN_TIMING_OPTIMIZATION = "comedian_timing_optimization"

class BatchStatus(Enum):
    """Status des batches"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIALLY_COMPLETED = "partially_completed"

@dataclass
class BatchItem:
    """Item individuel dans un batch"""
    item_id: str
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class BatchJob:
    """Job de traitement batch"""
    job_id: str
    batch_type: CreatorBatchType
    items: List[BatchItem]
    model_id: str
    model_version: str
    processing_strategy: BatchProcessingStrategy
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: BatchStatus = BatchStatus.QUEUED
    progress: float = 0.0
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    results: Dict[str, Any] = field(default_factory=dict)
    error_log: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BatchProcessingConfig:
    """Configuration du traitement batch"""
    max_batch_size: int = 1000
    max_concurrent_batches: int = 5
    max_workers_per_batch: int = multiprocessing.cpu_count()
    chunk_size: int = 100
    timeout_seconds: int = 3600
    retry_failed_items: bool = True
    save_intermediate_results: bool = True
    compression_enabled: bool = True
    memory_limit_gb: float = 8.0

class BatchInferenceProcessor:
    """
    Processeur d'inférence batch optimisé enterprise
    
    Fonctionnalités:
    - Traitement batch haute performance avec stratégies adaptatives
    - Support multi-modèles pour tous types de créateurs
    - Parallélisation intelligente (threads/processes)
    - Gestion d'erreurs robuste avec retry automatique
    - Monitoring temps réel et métriques de performance
    - Persistance et reprise après panne
    """
    
    def __init__(self, 
                 config: Optional[BatchProcessingConfig] = None,
                 storage_path: str = "/tmp/batch_processor",
                 db_path: str = "/tmp/batch_processor.db"):
        self.config = config or BatchProcessingConfig()
        self.storage_path = Path(storage_path)
        self.db_path = db_path
        
        # Queues et état
        self.job_queue: Dict[str, BatchJob] = {}
        self.active_jobs: Dict[str, BatchJob] = {}
        self.completed_jobs: Dict[str, BatchJob] = {}
        
        # Executors
        self.thread_executor = ThreadPoolExecutor(max_workers=self.config.max_workers_per_batch)
        self.process_executor = ProcessPoolExecutor(max_workers=min(8, multiprocessing.cpu_count()))
        
        # Callbacks
        self.progress_callbacks: List[Callable] = []
        self.completion_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
        
        # Modèles chargés
        self.loaded_models: Dict[str, Any] = {}
        
        # Stats en temps réel
        self.processing_stats = {
            "total_jobs_processed": 0,
            "total_items_processed": 0,
            "total_processing_time": 0.0,
            "avg_items_per_second": 0.0,
            "error_rate": 0.0
        }
        
        self._setup_storage()
        self._setup_database()
        logger.info("🚀 BatchInferenceProcessor initialized for enterprise batch processing")
    
    def _setup_storage(self):
        """Initialisation du stockage"""
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            (self.storage_path / "jobs").mkdir(exist_ok=True)
            (self.storage_path / "results").mkdir(exist_ok=True)
            (self.storage_path / "temp").mkdir(exist_ok=True)
            
        except Exception as e:
            logger.error(f"❌ Storage setup error: {e}")
            raise
    
    def _setup_database(self):
        """Initialisation de la base de données"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table des jobs batch
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS batch_jobs (
                        job_id TEXT PRIMARY KEY,
                        batch_type TEXT NOT NULL,
                        model_id TEXT NOT NULL,
                        model_version TEXT NOT NULL,
                        processing_strategy TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        started_at TEXT,
                        completed_at TEXT,
                        status TEXT NOT NULL,
                        progress REAL NOT NULL,
                        total_items INTEGER NOT NULL,
                        processed_items INTEGER NOT NULL,
                        failed_items INTEGER NOT NULL,
                        metadata TEXT,
                        error_log TEXT
                    )
                """)
                
                # Table des métriques de performance
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS batch_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        items_per_second REAL NOT NULL,
                        cpu_usage REAL NOT NULL,
                        memory_usage_gb REAL NOT NULL,
                        worker_count INTEGER NOT NULL,
                        queue_size INTEGER NOT NULL
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Database setup error: {e}")
            raise
    
    async def submit_batch_job(self,
                             batch_type: CreatorBatchType,
                             items: List[BatchItem],
                             model_id: str,
                             model_version: str = "latest",
                             processing_strategy: BatchProcessingStrategy = BatchProcessingStrategy.ADAPTIVE,
                             metadata: Optional[Dict[str, Any]] = None) -> str:
        """Soumettre un job de traitement batch"""
        try:
            job_id = f"batch_{batch_type.value}_{int(time.time())}"
            
            # Validation de la taille du batch
            if len(items) > self.config.max_batch_size:
                raise ValueError(f"Batch size {len(items)} exceeds maximum {self.config.max_batch_size}")
            
            # Création du job
            batch_job = BatchJob(
                job_id=job_id,
                batch_type=batch_type,
                items=items,
                model_id=model_id,
                model_version=model_version,
                processing_strategy=processing_strategy,
                created_at=datetime.now(),
                total_items=len(items),
                metadata=metadata or {}
            )
            
            # Stockage du job
            self.job_queue[job_id] = batch_job
            await self._save_job_to_db(batch_job)
            
            logger.info(f"📋 Batch job submitted: {job_id} ({len(items)} items)")
            
            # Démarrage automatique si possible
            if len(self.active_jobs) < self.config.max_concurrent_batches:
                asyncio.create_task(self._process_job(job_id))
            
            return job_id
            
        except Exception as e:
            logger.error(f"❌ Error submitting batch job: {e}")
            raise
    
    async def _process_job(self, job_id: str):
        """Traitement d'un job batch"""
        try:
            if job_id not in self.job_queue:
                logger.error(f"❌ Job {job_id} not found in queue")
                return
            
            job = self.job_queue[job_id]
            
            # Déplacement vers active jobs
            self.active_jobs[job_id] = job
            del self.job_queue[job_id]
            
            job.status = BatchStatus.PROCESSING
            job.started_at = datetime.now()
            
            logger.info(f"🔄 Processing batch job: {job_id}")
            
            # Chargement du modèle si nécessaire
            await self._ensure_model_loaded(job.model_id, job.model_version)
            
            # Sélection de la stratégie de traitement
            if job.processing_strategy == BatchProcessingStrategy.ADAPTIVE:
                job.processing_strategy = await self._select_optimal_strategy(job)
            
            # Traitement selon la stratégie
            await self._execute_processing_strategy(job)
            
            # Finalisation
            job.completed_at = datetime.now()
            job.status = BatchStatus.COMPLETED if job.failed_items == 0 else BatchStatus.PARTIALLY_COMPLETED
            job.progress = 1.0
            
            # Déplacement vers completed jobs
            self.completed_jobs[job_id] = job
            del self.active_jobs[job_id]
            
            # Sauvegarde finale
            await self._save_job_to_db(job)
            await self._save_results(job)
            
            # Mise à jour des stats
            self._update_processing_stats(job)
            
            # Callbacks de completion
            for callback in self.completion_callbacks:
                try:
                    await callback(job)
                except Exception as e:
                    logger.error(f"❌ Completion callback error: {e}")
            
            logger.info(f"✅ Batch job completed: {job_id} ({job.processed_items}/{job.total_items} items)")
            
            # Traitement du job suivant dans la queue
            if self.job_queue and len(self.active_jobs) < self.config.max_concurrent_batches:
                next_job_id = next(iter(self.job_queue))
                asyncio.create_task(self._process_job(next_job_id))
            
        except Exception as e:
            logger.error(f"❌ Error processing job {job_id}: {e}")
            await self._handle_job_error(job_id, str(e))
    
    async def _select_optimal_strategy(self, job: BatchJob) -> BatchProcessingStrategy:
        """Sélection adaptative de la stratégie optimale"""
        try:
            # Critères de décision
            item_count = len(job.items)
            estimated_item_processing_time = self._estimate_processing_time(job.batch_type)
            
            # Stratégie basée sur la taille et complexité
            if item_count < 10:
                return BatchProcessingStrategy.SEQUENTIAL
            elif item_count < 100 and estimated_item_processing_time < 0.1:
                return BatchProcessingStrategy.PARALLEL_THREADS
            elif item_count < 1000:
                return BatchProcessingStrategy.PARALLEL_THREADS
            else:
                # Pour de gros volumes, utiliser les processus
                return BatchProcessingStrategy.PARALLEL_PROCESSES
                
        except Exception as e:
            logger.error(f"❌ Error selecting strategy: {e}")
            return BatchProcessingStrategy.PARALLEL_THREADS
    
    def _estimate_processing_time(self, batch_type: CreatorBatchType) -> float:
        """Estimation du temps de traitement par item"""
        # Temps estimés par type de traitement créateur (en secondes)
        time_estimates = {
            CreatorBatchType.MUSICIAN_AUDIO_ANALYSIS: 0.5,
            CreatorBatchType.MUSICIAN_GENRE_CLASSIFICATION: 0.1,
            CreatorBatchType.BLOGGER_CONTENT_SEO: 0.3,
            CreatorBatchType.BLOGGER_SENTIMENT_BATCH: 0.05,
            CreatorBatchType.PHOTOGRAPHER_IMAGE_BATCH: 1.0,
            CreatorBatchType.PHOTOGRAPHER_STYLE_ANALYSIS: 0.8,
            CreatorBatchType.INFLUENCER_ANALYTICS_BULK: 0.2,
            CreatorBatchType.INFLUENCER_TREND_ANALYSIS: 0.4,
            CreatorBatchType.COMEDIAN_HUMOR_ANALYSIS: 0.15,
            CreatorBatchType.COMEDIAN_TIMING_OPTIMIZATION: 0.25
        }
        return time_estimates.get(batch_type, 0.2)
    
    async def _execute_processing_strategy(self, job: BatchJob):
        """Exécution de la stratégie de traitement"""
        try:
            if job.processing_strategy == BatchProcessingStrategy.SEQUENTIAL:
                await self._process_sequential(job)
            elif job.processing_strategy == BatchProcessingStrategy.PARALLEL_THREADS:
                await self._process_parallel_threads(job)
            elif job.processing_strategy == BatchProcessingStrategy.PARALLEL_PROCESSES:
                await self._process_parallel_processes(job)
            else:
                # Fallback vers threads
                await self._process_parallel_threads(job)
                
        except Exception as e:
            logger.error(f"❌ Error executing strategy {job.processing_strategy}: {e}")
            raise
    
    async def _process_sequential(self, job: BatchJob):
        """Traitement séquentiel"""
        for i, item in enumerate(job.items):
            try:
                result = await self._process_single_item(job, item)
                job.results[item.item_id] = result
                job.processed_items += 1
                
            except Exception as e:
                logger.error(f"❌ Error processing item {item.item_id}: {e}")
                job.error_log.append(f"Item {item.item_id}: {str(e)}")
                job.failed_items += 1
                
                # Retry si configuré
                if self.config.retry_failed_items and item.retry_count < item.max_retries:
                    item.retry_count += 1
                    try:
                        result = await self._process_single_item(job, item)
                        job.results[item.item_id] = result
                        job.processed_items += 1
                        job.failed_items -= 1
                    except Exception as retry_e:
                        logger.error(f"❌ Retry failed for item {item.item_id}: {retry_e}")
            
            # Mise à jour du progrès
            job.progress = (job.processed_items + job.failed_items) / job.total_items
            
            # Callbacks de progrès
            if i % 10 == 0:  # Notification tous les 10 items
                for callback in self.progress_callbacks:
                    try:
                        await callback(job)
                    except Exception as e:
                        logger.error(f"❌ Progress callback error: {e}")
    
    async def _process_parallel_threads(self, job: BatchJob):
        """Traitement parallèle avec threads"""
        try:
            # Division en chunks
            chunk_size = min(self.config.chunk_size, len(job.items) // self.config.max_workers_per_batch + 1)
            chunks = [job.items[i:i + chunk_size] for i in range(0, len(job.items), chunk_size)]
            
            # Traitement des chunks en parallèle
            futures = []
            for chunk in chunks:
                future = self.thread_executor.submit(self._process_chunk_sync, job, chunk)
                futures.append(future)
            
            # Collecte des résultats
            for future in as_completed(futures):
                try:
                    chunk_results, chunk_errors = future.result(timeout=self.config.timeout_seconds)
                    
                    # Mise à jour des résultats
                    job.results.update(chunk_results)
                    job.error_log.extend(chunk_errors)
                    job.processed_items += len(chunk_results)
                    job.failed_items += len(chunk_errors)
                    job.progress = (job.processed_items + job.failed_items) / job.total_items
                    
                    # Callback de progrès
                    for callback in self.progress_callbacks:
                        try:
                            await callback(job)
                        except Exception as e:
                            logger.error(f"❌ Progress callback error: {e}")
                            
                except Exception as e:
                    logger.error(f"❌ Chunk processing error: {e}")
                    job.error_log.append(f"Chunk error: {str(e)}")
                    
        except Exception as e:
            logger.error(f"❌ Parallel threads processing error: {e}")
            raise
    
    def _process_chunk_sync(self, job: BatchJob, chunk: List[BatchItem]) -> Tuple[Dict[str, Any], List[str]]:
        """Traitement synchrone d'un chunk (pour thread executor)"""
        results = {}
        errors = []
        
        for item in chunk:
            try:
                # Simulation du traitement (remplacer par vraie logique)
                result = self._process_item_sync(job, item)
                results[item.item_id] = result
                
            except Exception as e:
                error_msg = f"Item {item.item_id}: {str(e)}"
                errors.append(error_msg)
                
                # Retry si configuré
                if self.config.retry_failed_items and item.retry_count < item.max_retries:
                    item.retry_count += 1
                    try:
                        result = self._process_item_sync(job, item)
                        results[item.item_id] = result
                        errors.pop()  # Retirer l'erreur car le retry a réussi
                    except Exception:
                        pass  # L'erreur reste
        
        return results, errors
    
    def _process_item_sync(self, job: BatchJob, item: BatchItem) -> Any:
        """Traitement synchrone d'un item individuel"""
        # Simulation basée sur le type de créateur
        processing_time = self._estimate_processing_time(job.batch_type)
        
        # Simulation d'une charge de travail variable
        import random
        time.sleep(processing_time * random.uniform(0.5, 1.5))
        
        # Résultat simulé basé sur le type
        if job.batch_type in [CreatorBatchType.MUSICIAN_AUDIO_ANALYSIS, CreatorBatchType.MUSICIAN_GENRE_CLASSIFICATION]:
            return {
                "genre": random.choice(["rock", "pop", "jazz", "classical"]),
                "confidence": random.uniform(0.7, 0.95),
                "features": [random.uniform(0, 1) for _ in range(10)]
            }
        elif job.batch_type in [CreatorBatchType.BLOGGER_CONTENT_SEO, CreatorBatchType.BLOGGER_SENTIMENT_BATCH]:
            return {
                "sentiment": random.choice(["positive", "negative", "neutral"]),
                "keywords": [f"keyword_{i}" for i in range(random.randint(3, 8))],
                "seo_score": random.uniform(0.6, 0.9)
            }
        elif job.batch_type in [CreatorBatchType.PHOTOGRAPHER_IMAGE_BATCH, CreatorBatchType.PHOTOGRAPHER_STYLE_ANALYSIS]:
            return {
                "style": random.choice(["portrait", "landscape", "street", "macro"]),
                "quality_score": random.uniform(0.7, 0.95),
                "enhancement_suggestions": ["brightness", "contrast", "saturation"]
            }
        elif job.batch_type in [CreatorBatchType.INFLUENCER_ANALYTICS_BULK, CreatorBatchType.INFLUENCER_TREND_ANALYSIS]:
            return {
                "engagement_rate": random.uniform(0.02, 0.15),
                "trend_score": random.uniform(0.1, 0.9),
                "audience_segments": ["18-24", "25-34", "35-44"]
            }
        else:  # Comedian types
            return {
                "humor_type": random.choice(["observational", "self-deprecating", "wordplay"]),
                "timing_score": random.uniform(0.6, 0.9),
                "audience_reaction": random.choice(["positive", "mixed", "needs_work"])
            }
    
    async def _process_single_item(self, job: BatchJob, item: BatchItem) -> Any:
        """Version asynchrone du traitement d'item"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._process_item_sync, job, item)
    
    async def _process_parallel_processes(self, job: BatchJob):
        """Traitement parallèle avec processus (pour très gros volumes)"""
        try:
            # Pour les processus, on doit sérialiser les données
            chunk_size = len(job.items) // self.config.max_workers_per_batch + 1
            chunks = [job.items[i:i + chunk_size] for i in range(0, len(job.items), chunk_size)]
            
            # Préparation des tâches
            tasks = []
            for i, chunk in enumerate(chunks):
                # Sauvegarde temporaire du chunk
                chunk_file = self.storage_path / "temp" / f"chunk_{job.job_id}_{i}.pkl"
                with open(chunk_file, 'wb') as f:
                    pickle.dump((job.batch_type, chunk), f)
                
                # Soumission au process executor
                future = self.process_executor.submit(_process_chunk_file, str(chunk_file))
                tasks.append((future, chunk_file))
            
            # Collecte des résultats
            for future, chunk_file in tasks:
                try:
                    chunk_results, chunk_errors = future.result(timeout=self.config.timeout_seconds)
                    
                    # Mise à jour
                    job.results.update(chunk_results)
                    job.error_log.extend(chunk_errors)
                    job.processed_items += len(chunk_results)
                    job.failed_items += len(chunk_errors)
                    job.progress = (job.processed_items + job.failed_items) / job.total_items
                    
                    # Nettoyage du fichier temporaire
                    chunk_file.unlink(missing_ok=True)
                    
                except Exception as e:
                    logger.error(f"❌ Process chunk error: {e}")
                    job.error_log.append(f"Process error: {str(e)}")
                    chunk_file.unlink(missing_ok=True)
                    
        except Exception as e:
            logger.error(f"❌ Parallel processes error: {e}")
            raise
    
    async def _ensure_model_loaded(self, model_id: str, model_version: str):
        """S'assurer que le modèle est chargé"""
        model_key = f"{model_id}_{model_version}"
        
        if model_key not in self.loaded_models:
            # Simulation du chargement de modèle
            logger.info(f"📥 Loading model: {model_key}")
            
            # Ici, on chargerait le vrai modèle
            # model = load_model(model_id, model_version)
            self.loaded_models[model_key] = {
                "model_id": model_id,
                "version": model_version,
                "loaded_at": datetime.now(),
                "dummy": True  # Marqueur pour la simulation
            }
            
            logger.info(f"✅ Model loaded: {model_key}")
    
    async def _save_job_to_db(self, job: BatchJob):
        """Sauvegarde d'un job en base"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO batch_jobs 
                    (job_id, batch_type, model_id, model_version, processing_strategy,
                     created_at, started_at, completed_at, status, progress,
                     total_items, processed_items, failed_items, metadata, error_log)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.job_id,
                    job.batch_type.value,
                    job.model_id,
                    job.model_version,
                    job.processing_strategy.value,
                    job.created_at.isoformat(),
                    job.started_at.isoformat() if job.started_at else None,
                    job.completed_at.isoformat() if job.completed_at else None,
                    job.status.value,
                    job.progress,
                    job.total_items,
                    job.processed_items,
                    job.failed_items,
                    json.dumps(job.metadata),
                    json.dumps(job.error_log)
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Error saving job to DB: {e}")
    
    async def _save_results(self, job: BatchJob):
        """Sauvegarde des résultats d'un job"""
        try:
            results_file = self.storage_path / "results" / f"{job.job_id}_results.json"
            
            # Données à sauvegarder
            results_data = {
                "job_id": job.job_id,
                "batch_type": job.batch_type.value,
                "model_id": job.model_id,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "total_items": job.total_items,
                "processed_items": job.processed_items,
                "failed_items": job.failed_items,
                "results": job.results,
                "error_log": job.error_log,
                "metadata": job.metadata
            }
            
            # Sauvegarde avec compression si activée
            if self.config.compression_enabled:
                with gzip.open(f"{results_file}.gz", 'wt') as f:
                    json.dump(results_data, f, indent=2)
            else:
                with open(results_file, 'w') as f:
                    json.dump(results_data, f, indent=2)
            
            logger.info(f"💾 Results saved for job {job.job_id}")
            
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")
    
    async def _handle_job_error(self, job_id: str, error_message: str):
        """Gestion d'erreur de job"""
        try:
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                job.status = BatchStatus.FAILED
                job.error_log.append(f"Job error: {error_message}")
                
                # Callbacks d'erreur
                for callback in self.error_callbacks:
                    try:
                        await callback(job, error_message)
                    except Exception as e:
                        logger.error(f"❌ Error callback error: {e}")
                
                # Déplacement vers completed avec status failed
                self.completed_jobs[job_id] = job
                del self.active_jobs[job_id]
                
                await self._save_job_to_db(job)
                
        except Exception as e:
            logger.error(f"❌ Error handling job error: {e}")
    
    def _update_processing_stats(self, job: BatchJob):
        """Mise à jour des statistiques de traitement"""
        try:
            if job.started_at and job.completed_at:
                processing_duration = (job.completed_at - job.started_at).total_seconds()
                
                self.processing_stats["total_jobs_processed"] += 1
                self.processing_stats["total_items_processed"] += job.processed_items
                self.processing_stats["total_processing_time"] += processing_duration
                
                # Calcul des moyennes
                if job.processed_items > 0 and processing_duration > 0:
                    current_rate = job.processed_items / processing_duration
                    total_items = self.processing_stats["total_items_processed"]
                    total_time = self.processing_stats["total_processing_time"]
                    
                    if total_time > 0:
                        self.processing_stats["avg_items_per_second"] = total_items / total_time
                    
                    # Taux d'erreur global
                    total_failed = sum(job.failed_items for job in self.completed_jobs.values())
                    if total_items > 0:
                        self.processing_stats["error_rate"] = total_failed / (total_items + total_failed)
                        
        except Exception as e:
            logger.error(f"❌ Error updating stats: {e}")
    
    async def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """Obtenir le status d'un job"""
        # Recherche dans toutes les queues
        for job_dict in [self.job_queue, self.active_jobs, self.completed_jobs]:
            if job_id in job_dict:
                return job_dict[job_id]
        
        # Recherche en base si pas en mémoire
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM batch_jobs WHERE job_id = ?", (job_id,))
                row = cursor.fetchone()
                
                if row:
                    # Reconstruction partielle du job depuis la DB
                    return BatchJob(
                        job_id=row[0],
                        batch_type=CreatorBatchType(row[1]),
                        items=[],  # Items pas stockés en DB
                        model_id=row[2],
                        model_version=row[3],
                        processing_strategy=BatchProcessingStrategy(row[4]),
                        created_at=datetime.fromisoformat(row[5]),
                        started_at=datetime.fromisoformat(row[6]) if row[6] else None,
                        completed_at=datetime.fromisoformat(row[7]) if row[7] else None,
                        status=BatchStatus(row[8]),
                        progress=row[9],
                        total_items=row[10],
                        processed_items=row[11],
                        failed_items=row[12],
                        metadata=json.loads(row[13]) if row[13] else {},
                        error_log=json.loads(row[14]) if row[14] else []
                    )
        except Exception as e:
            logger.error(f"❌ Error getting job status: {e}")
        
        return None
    
    async def cancel_job(self, job_id: str) -> bool:
        """Annuler un job"""
        try:
            if job_id in self.job_queue:
                job = self.job_queue[job_id]
                job.status = BatchStatus.CANCELLED
                self.completed_jobs[job_id] = job
                del self.job_queue[job_id]
                await self._save_job_to_db(job)
                logger.info(f"🚫 Job cancelled: {job_id}")
                return True
            elif job_id in self.active_jobs:
                # Les jobs actifs sont plus difficiles à annuler
                # On marque comme cancelled mais le traitement peut continuer
                job = self.active_jobs[job_id]
                job.status = BatchStatus.CANCELLED
                logger.warning(f"⚠️ Active job marked for cancellation: {job_id}")
                return True
            else:
                logger.warning(f"⚠️ Job {job_id} not found or already completed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error cancelling job {job_id}: {e}")
            return False
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques de traitement"""
        return {
            **self.processing_stats,
            "queued_jobs": len(self.job_queue),
            "active_jobs": len(self.active_jobs),
            "completed_jobs": len(self.completed_jobs),
            "loaded_models": len(self.loaded_models)
        }
    
    def add_progress_callback(self, callback: Callable):
        """Ajouter un callback de progrès"""
        self.progress_callbacks.append(callback)
    
    def add_completion_callback(self, callback: Callable):
        """Ajouter un callback de completion"""
        self.completion_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable):
        """Ajouter un callback d'erreur"""
        self.error_callbacks.append(callback)
    
    async def cleanup_old_data(self, days_back: int = 7):
        """Nettoyage des données anciennes"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Nettoyage de la base
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM batch_jobs 
                    WHERE created_at < ? AND status IN ('completed', 'failed', 'cancelled')
                """, (cutoff_date.isoformat(),))
                
                jobs_deleted = cursor.rowcount
                
                cursor.execute("""
                    DELETE FROM batch_metrics 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                metrics_deleted = cursor.rowcount
                conn.commit()
            
            # Nettoyage des fichiers de résultats
            results_deleted = 0
            results_dir = self.storage_path / "results"
            if results_dir.exists():
                for file_path in results_dir.glob("*"):
                    if file_path.stat().st_mtime < cutoff_date.timestamp():
                        file_path.unlink()
                        results_deleted += 1
            
            logger.info(f"🧹 Cleaned up {jobs_deleted} jobs, {metrics_deleted} metrics, {results_deleted} result files")
            return jobs_deleted + metrics_deleted + results_deleted
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            return 0


# Fonction helper pour traitement en processus séparé
def _process_chunk_file(chunk_file_path: str) -> Tuple[Dict[str, Any], List[str]]:
    """Traitement d'un chunk depuis un fichier (pour ProcessPoolExecutor)"""
    try:
        with open(chunk_file_path, 'rb') as f:
            batch_type, chunk = pickle.load(f)
        
        results = {}
        errors = []
        
        # Traitement simulé des items
        for item in chunk:
            try:
                # Simulation simple basée sur le type
                import random
                import time
                
                processing_time = 0.1  # Temps de base
                time.sleep(processing_time * random.uniform(0.5, 1.5))
                
                results[item.item_id] = {
                    "processed_at": datetime.now().isoformat(),
                    "batch_type": batch_type.value,
                    "result": f"processed_{item.item_id}"
                }
                
            except Exception as e:
                errors.append(f"Item {item.item_id}: {str(e)}")
        
        return results, errors
        
    except Exception as e:
        return {}, [f"Chunk file error: {str(e)}"]


# Exemple d'utilisation pour démonstration
async def main():
    """Démonstration des capacités du BatchInferenceProcessor"""
    
    # Configuration custom
    config = BatchProcessingConfig(
        max_batch_size=500,
        max_concurrent_batches=3,
        max_workers_per_batch=4,
        chunk_size=50
    )
    
    processor = BatchInferenceProcessor(config=config)
    
    # Callbacks de démonstration
    async def progress_callback(job: BatchJob):
        print(f"📈 Progress {job.job_id}: {job.progress:.2%} ({job.processed_items}/{job.total_items})")
    
    async def completion_callback(job: BatchJob):
        print(f"✅ Completed {job.job_id}: {job.processed_items} items processed")
    
    async def error_callback(job: BatchJob, error: str):
        print(f"❌ Error in {job.job_id}: {error}")
    
    processor.add_progress_callback(progress_callback)
    processor.add_completion_callback(completion_callback)
    processor.add_error_callback(error_callback)
    
    # Création de jobs de test pour différents créateurs
    test_scenarios = [
        (CreatorBatchType.MUSICIAN_AUDIO_ANALYSIS, "audio_model", 100),
        (CreatorBatchType.BLOGGER_CONTENT_SEO, "seo_model", 200),
        (CreatorBatchType.PHOTOGRAPHER_IMAGE_BATCH, "vision_model", 50),
        (CreatorBatchType.INFLUENCER_ANALYTICS_BULK, "analytics_model", 300),
        (CreatorBatchType.COMEDIAN_HUMOR_ANALYSIS, "humor_model", 75)
    ]
    
    job_ids = []
    
    for batch_type, model_id, item_count in test_scenarios:
        # Création des items de test
        items = []
        for i in range(item_count):
            item = BatchItem(
                item_id=f"{batch_type.value}_item_{i}",
                data=f"test_data_{i}",
                metadata={"creator_type": batch_type.value.split('_')[0]}
            )
            items.append(item)
        
        # Soumission du job
        job_id = await processor.submit_batch_job(
            batch_type=batch_type,
            items=items,
            model_id=model_id,
            processing_strategy=BatchProcessingStrategy.ADAPTIVE,
            metadata={"test_run": True}
        )
        job_ids.append(job_id)
        print(f"🚀 Submitted batch job: {job_id} ({item_count} items)")
    
    # Attente de completion des jobs
    print(f"\n⏳ Waiting for jobs to complete...")
    while processor.active_jobs or processor.job_queue:
        await asyncio.sleep(2)
        stats = await processor.get_processing_stats()
        print(f"📊 Status: {stats['active_jobs']} active, {stats['queued_jobs']} queued, {stats['completed_jobs']} completed")
    
    # Affichage des résultats finaux
    print(f"\n📋 Final Results:")
    final_stats = await processor.get_processing_stats()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")
    
    # Vérification des statuts individuels
    print(f"\n🔍 Individual Job Status:")
    for job_id in job_ids:
        job = await processor.get_job_status(job_id)
        if job:
            print(f"   {job_id}: {job.status.value} ({job.processed_items}/{job.total_items} items)")
    
    print(f"✅ BatchInferenceProcessor demonstration completed")


if __name__ == "__main__":
    asyncio.run(main())