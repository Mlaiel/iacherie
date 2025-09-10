"""🚀 Batch Inference Processor - IA Influencer Agent Platform Enterprise
======================================================================
Module: backend/ml/inference/batch_inference_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
======================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 PROCESSEUR D'INFÉRENCE PAR LOT
Traitement haute performance pour inférence en batch
- Traitement parallèle avec chunking intelligent
- Optimisation mémoire pour gros volumes
- Reprise sur erreur et checkpointing
- Monitoring détaillé des performances
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Callable, Iterator
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import hashlib
from pathlib import Path
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp
import math

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator

# Configuration
logger = logging.getLogger(__name__)

class BatchStatus(Enum):
    """Statuts des jobs batch"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ProcessingMode(Enum):
    """Modes de traitement"""
    SEQUENTIAL = "sequential"
    PARALLEL_THREAD = "parallel_thread"
    PARALLEL_PROCESS = "parallel_process"
    DISTRIBUTED = "distributed"

class ChunkStrategy(Enum):
    """Stratégies de chunking"""
    FIXED_SIZE = "fixed_size"
    MEMORY_BASED = "memory_based"
    ADAPTIVE = "adaptive"
    ROW_BASED = "row_based"

@dataclass
class BatchJob:
    """Job de traitement par lot"""
    job_id: str
    model_id: str
    input_data: Any
    output_path: Optional[str]
    status: BatchStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    chunk_size: int = 1000
    processing_mode: ProcessingMode = ProcessingMode.PARALLEL_THREAD
    chunk_strategy: ChunkStrategy = ChunkStrategy.FIXED_SIZE
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    checkpoint_path: Optional[str] = None
    resume_from_checkpoint: bool = False

@dataclass
class BatchResult:
    """Résultat d'un job batch"""
    job_id: str
    predictions: List[Any]
    processing_time: float
    total_items: int
    successful_items: int
    failed_items: int
    throughput_items_per_second: float
    average_latency_ms: float
    memory_peak_mb: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChunkResult:
    """Résultat d'un chunk"""
    chunk_id: str
    chunk_index: int
    predictions: List[Any]
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    items_processed: int = 0

@dataclass
class BatchMetrics:
    """Métriques de traitement batch"""
    active_jobs: int = 0
    queued_jobs: int = 0
    total_jobs_processed: int = 0
    total_items_processed: int = 0
    average_throughput: float = 0.0
    peak_memory_usage_mb: float = 0.0
    total_processing_time: float = 0.0

class BatchInferenceProcessor:
    """Processeur d'inférence par lot enterprise"""
    
    def __init__(self,
                 max_workers: int = None,
                 max_memory_mb: int = 8192,
                 checkpoint_interval: int = 1000,
                 enable_checkpointing: bool = True,
                 temp_dir: str = "/tmp/batch_inference"):
        
        self.max_workers = max_workers or min(32, (mp.cpu_count() or 1) + 4)
        self.max_memory_mb = max_memory_mb
        self.checkpoint_interval = checkpoint_interval
        self.enable_checkpointing = enable_checkpointing
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
        # Jobs et queues
        self.jobs: Dict[str, BatchJob] = {}
        self.job_queue: deque = deque()
        self.running_jobs: Dict[str, threading.Thread] = {}
        
        # Modèles chargés
        self.loaded_models: Dict[str, Any] = {}
        self.model_locks: Dict[str, threading.Lock] = defaultdict(threading.Lock)
        
        # Pools de workers
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
        
        # Métriques et monitoring
        self.metrics = BatchMetrics()
        self.job_results: Dict[str, BatchResult] = {}
        
        # State management
        self.is_running = False
        self.shutdown_event = threading.Event()
        
        # Callbacks
        self.job_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self.progress_callbacks: List[Callable[[str, float], None]] = []
        self.completion_callbacks: List[Callable[[BatchResult], None]] = []
    
    async def start(self):
        """Démarre le processeur batch"""
        try:
            self.is_running = True
            logger.info(f"Démarrage processeur batch avec {self.max_workers} workers")
            
            # Démarrer la boucle de traitement
            asyncio.create_task(self._processing_loop())
            asyncio.create_task(self._monitoring_loop())
            
            logger.info("Processeur batch démarré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur démarrage processeur batch: {e}")
            raise
    
    async def stop(self):
        """Arrête le processeur batch"""
        try:
            logger.info("Arrêt du processeur batch...")
            
            self.is_running = False
            self.shutdown_event.set()
            
            # Arrêter les jobs en cours
            for job_id, thread in self.running_jobs.items():
                logger.info(f"Arrêt job {job_id}")
                thread.join(timeout=5.0)
            
            # Fermer les pools
            self.thread_pool.shutdown(wait=True)
            self.process_pool.shutdown(wait=True)
            
            logger.info("Processeur batch arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt processeur batch: {e}")
    
    async def load_model(self, model_id: str, model: Any) -> bool:
        """Charge un modèle pour le traitement batch"""
        try:
            with self.model_locks[model_id]:
                if model_id in self.loaded_models:
                    logger.warning(f"Modèle {model_id} déjà chargé")
                    return True
                
                # Vérifier que le modèle est valide
                if not hasattr(model, 'predict'):
                    raise ValueError("Le modèle n'a pas de méthode predict")
                
                self.loaded_models[model_id] = model
                logger.info(f"Modèle {model_id} chargé pour traitement batch")
                return True
                
        except Exception as e:
            logger.error(f"Erreur chargement modèle {model_id}: {e}")
            return False
    
    async def submit_batch_job(self,
                              model_id: str,
                              input_data: Any,
                              output_path: Optional[str] = None,
                              chunk_size: int = 1000,
                              processing_mode: ProcessingMode = ProcessingMode.PARALLEL_THREAD,
                              chunk_strategy: ChunkStrategy = ChunkStrategy.FIXED_SIZE,
                              resume_from_checkpoint: bool = False,
                              job_name: Optional[str] = None) -> str:
        """Soumet un job de traitement batch"""
        
        try:
            # Générer ID du job
            job_id = str(uuid.uuid4())
            if job_name:
                job_id = f"{job_name}_{job_id[:8]}"
            
            # Vérifier que le modèle est chargé
            if model_id not in self.loaded_models:
                raise ValueError(f"Modèle {model_id} non chargé")
            
            # Calculer le nombre total d'éléments
            total_items = self._calculate_total_items(input_data)
            
            # Déterminer la taille de chunk optimale
            if chunk_strategy != ChunkStrategy.FIXED_SIZE:
                chunk_size = self._calculate_optimal_chunk_size(
                    input_data, chunk_strategy, chunk_size
                )
            
            # Créer le job
            job = BatchJob(
                job_id=job_id,
                model_id=model_id,
                input_data=input_data,
                output_path=output_path,
                status=BatchStatus.PENDING,
                created_at=datetime.now(),
                total_items=total_items,
                chunk_size=chunk_size,
                processing_mode=processing_mode,
                chunk_strategy=chunk_strategy,
                resume_from_checkpoint=resume_from_checkpoint
            )
            
            # Configurer le checkpoint si activé
            if self.enable_checkpointing:
                job.checkpoint_path = str(self.temp_dir / f"{job_id}_checkpoint.pkl")
            
            self.jobs[job_id] = job
            self.job_queue.append(job_id)
            
            logger.info(f"Job batch soumis: {job_id} - {total_items} éléments")
            return job_id
            
        except Exception as e:
            logger.error(f"Erreur soumission job batch: {e}")
            raise
    
    def _calculate_total_items(self, input_data: Any) -> int:
        """Calcule le nombre total d'éléments à traiter"""
        try:
            if isinstance(input_data, (list, tuple)):
                return len(input_data)
            elif isinstance(input_data, np.ndarray):
                return input_data.shape[0]
            elif isinstance(input_data, pd.DataFrame):
                return len(input_data)
            elif hasattr(input_data, '__len__'):
                return len(input_data)
            else:
                return 1
        except Exception:
            return 1
    
    def _calculate_optimal_chunk_size(self,
                                    input_data: Any,
                                    strategy: ChunkStrategy,
                                    default_size: int) -> int:
        """Calcule la taille optimale des chunks"""
        
        try:
            if strategy == ChunkStrategy.MEMORY_BASED:
                # Estimer la mémoire par élément
                if isinstance(input_data, np.ndarray):
                    memory_per_item = input_data.nbytes / len(input_data)
                    max_items = int(self.max_memory_mb * 1024 * 1024 * 0.1 / memory_per_item)
                    return min(max(max_items, 100), 10000)
                
            elif strategy == ChunkStrategy.ADAPTIVE:
                # Adapter basé sur le nombre de workers
                total_items = self._calculate_total_items(input_data)
                optimal_chunks = self.max_workers * 4  # 4 chunks par worker
                return max(total_items // optimal_chunks, 100)
                
            elif strategy == ChunkStrategy.ROW_BASED:
                # Pour les DataFrames, adapter à la structure
                if isinstance(input_data, pd.DataFrame):
                    memory_usage = input_data.memory_usage(deep=True).sum()
                    memory_per_row = memory_usage / len(input_data)
                    max_rows = int(self.max_memory_mb * 1024 * 1024 * 0.1 / memory_per_row)
                    return min(max(max_rows, 100), 5000)
            
            return default_size
            
        except Exception as e:
            logger.error(f"Erreur calcul taille chunk: {e}")
            return default_size
    
    async def _processing_loop(self):
        """Boucle principale de traitement"""
        while self.is_running:
            try:
                # Traiter la queue des jobs
                if self.job_queue and len(self.running_jobs) < self.max_workers:
                    job_id = self.job_queue.popleft()
                    await self._start_job(job_id)
                
                # Nettoyer les jobs terminés
                finished_jobs = [
                    job_id for job_id, thread in self.running_jobs.items()
                    if not thread.is_alive()
                ]
                
                for job_id in finished_jobs:
                    del self.running_jobs[job_id]
                
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Erreur boucle traitement: {e}")
                await asyncio.sleep(5.0)
    
    async def _start_job(self, job_id: str):
        """Démarre un job de traitement"""
        try:
            job = self.jobs[job_id]
            job.status = BatchStatus.RUNNING
            job.started_at = datetime.now()
            
            # Créer et démarrer le thread de traitement
            thread = threading.Thread(
                target=self._process_job,
                args=(job_id,),
                daemon=True
            )
            thread.start()
            self.running_jobs[job_id] = thread
            
            logger.info(f"Job {job_id} démarré")
            
        except Exception as e:
            logger.error(f"Erreur démarrage job {job_id}: {e}")
            self.jobs[job_id].status = BatchStatus.FAILED
            self.jobs[job_id].error_message = str(e)
    
    def _process_job(self, job_id: str):
        """Traite un job batch"""
        job = self.jobs[job_id]
        start_time = time.time()
        
        try:
            logger.info(f"Début traitement job {job_id}")
            
            # Vérifier si on reprend depuis un checkpoint
            if job.resume_from_checkpoint and job.checkpoint_path:
                checkpoint_data = self._load_checkpoint(job.checkpoint_path)
                if checkpoint_data:
                    job.processed_items = checkpoint_data.get('processed_items', 0)
                    job.progress = checkpoint_data.get('progress', 0.0)
                    logger.info(f"Reprise job {job_id} depuis {job.processed_items} éléments")
            
            # Découper en chunks
            chunks = list(self._create_chunks(job))
            total_chunks = len(chunks)
            
            # Traiter les chunks selon le mode
            if job.processing_mode == ProcessingMode.SEQUENTIAL:
                results = self._process_chunks_sequential(job, chunks)
            elif job.processing_mode == ProcessingMode.PARALLEL_THREAD:
                results = self._process_chunks_parallel_thread(job, chunks)
            elif job.processing_mode == ProcessingMode.PARALLEL_PROCESS:
                results = self._process_chunks_parallel_process(job, chunks)
            else:
                raise ValueError(f"Mode de traitement non supporté: {job.processing_mode}")
            
            # Consolider les résultats
            all_predictions = []
            successful_items = 0
            failed_items = 0
            
            for result in results:
                if result.success:
                    all_predictions.extend(result.predictions)
                    successful_items += result.items_processed
                else:
                    failed_items += result.items_processed
                    logger.error(f"Chunk {result.chunk_id} échoué: {result.error_message}")
            
            # Sauvegarder les résultats si chemin spécifié
            if job.output_path:
                self._save_results(job.output_path, all_predictions)
            
            # Finaliser le job
            processing_time = time.time() - start_time
            throughput = successful_items / processing_time if processing_time > 0 else 0
            
            result = BatchResult(
                job_id=job_id,
                predictions=all_predictions,
                processing_time=processing_time,
                total_items=job.total_items,
                successful_items=successful_items,
                failed_items=failed_items,
                throughput_items_per_second=throughput,
                average_latency_ms=(processing_time * 1000) / max(successful_items, 1),
                memory_peak_mb=0.0  # À implémenter avec monitoring mémoire
            )
            
            self.job_results[job_id] = result
            
            job.status = BatchStatus.COMPLETED
            job.completed_at = datetime.now()
            job.processed_items = successful_items
            job.failed_items = failed_items
            job.progress = 100.0
            
            # Nettoyer le checkpoint
            if job.checkpoint_path and Path(job.checkpoint_path).exists():
                Path(job.checkpoint_path).unlink()
            
            logger.info(f"Job {job_id} terminé: {successful_items}/{job.total_items} éléments "
                       f"en {processing_time:.2f}s ({throughput:.1f} éléments/s)")
            
            # Appeler les callbacks de completion
            for callback in self.completion_callbacks:
                try:
                    callback(result)
                except Exception as e:
                    logger.error(f"Erreur callback completion: {e}")
            
        except Exception as e:
            logger.error(f"Erreur traitement job {job_id}: {e}")
            job.status = BatchStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
        
        finally:
            # Mettre à jour les métriques
            self.metrics.total_jobs_processed += 1
            if job.status == BatchStatus.COMPLETED:
                self.metrics.total_items_processed += job.processed_items
                self.metrics.total_processing_time += (time.time() - start_time)
    
    def _create_chunks(self, job: BatchJob) -> Iterator[Tuple[int, Any]]:
        """Crée les chunks pour traitement"""
        try:
            input_data = job.input_data
            chunk_size = job.chunk_size
            start_index = job.processed_items  # Pour reprendre depuis checkpoint
            
            if isinstance(input_data, (list, tuple)):
                for i in range(start_index, len(input_data), chunk_size):
                    yield (i, input_data[i:i + chunk_size])
                    
            elif isinstance(input_data, np.ndarray):
                for i in range(start_index, len(input_data), chunk_size):
                    yield (i, input_data[i:i + chunk_size])
                    
            elif isinstance(input_data, pd.DataFrame):
                for i in range(start_index, len(input_data), chunk_size):
                    yield (i, input_data.iloc[i:i + chunk_size])
                    
            else:
                # Fallback: traiter comme un seul chunk
                if start_index == 0:
                    yield (0, input_data)
                    
        except Exception as e:
            logger.error(f"Erreur création chunks: {e}")
            raise
    
    def _process_chunks_sequential(self, job: BatchJob, chunks: List[Tuple[int, Any]]) -> List[ChunkResult]:
        """Traite les chunks séquentiellement"""
        results = []
        
        for chunk_index, (start_idx, chunk_data) in enumerate(chunks):
            try:
                result = self._process_single_chunk(
                    job.job_id, job.model_id, chunk_index, start_idx, chunk_data
                )
                results.append(result)
                
                # Mettre à jour le progrès
                progress = ((chunk_index + 1) / len(chunks)) * 100
                self._update_job_progress(job.job_id, progress)
                
                # Checkpoint périodique
                if self.enable_checkpointing and (chunk_index + 1) % self.checkpoint_interval == 0:
                    self._save_checkpoint(job, chunk_index + 1)
                
            except Exception as e:
                logger.error(f"Erreur chunk {chunk_index}: {e}")
                results.append(ChunkResult(
                    chunk_id=f"{job.job_id}_chunk_{chunk_index}",
                    chunk_index=chunk_index,
                    predictions=[],
                    processing_time=0.0,
                    success=False,
                    error_message=str(e),
                    items_processed=len(chunk_data) if hasattr(chunk_data, '__len__') else 1
                ))
        
        return results
    
    def _process_chunks_parallel_thread(self, job: BatchJob, chunks: List[Tuple[int, Any]]) -> List[ChunkResult]:
        """Traite les chunks en parallèle avec threads"""
        results = []
        futures = []
        
        # Soumettre tous les chunks
        for chunk_index, (start_idx, chunk_data) in enumerate(chunks):
            future = self.thread_pool.submit(
                self._process_single_chunk,
                job.job_id, job.model_id, chunk_index, start_idx, chunk_data
            )
            futures.append((chunk_index, future))
        
        # Collecter les résultats
        completed_chunks = 0
        for chunk_index, future in futures:
            try:
                result = future.result(timeout=300)  # 5 minutes timeout
                results.append(result)
                completed_chunks += 1
                
                # Mettre à jour le progrès
                progress = (completed_chunks / len(chunks)) * 100
                self._update_job_progress(job.job_id, progress)
                
            except Exception as e:
                logger.error(f"Erreur chunk parallèle {chunk_index}: {e}")
                results.append(ChunkResult(
                    chunk_id=f"{job.job_id}_chunk_{chunk_index}",
                    chunk_index=chunk_index,
                    predictions=[],
                    processing_time=0.0,
                    success=False,
                    error_message=str(e),
                    items_processed=0
                ))
        
        return results
    
    def _process_chunks_parallel_process(self, job: BatchJob, chunks: List[Tuple[int, Any]]) -> List[ChunkResult]:
        """Traite les chunks en parallèle avec processus"""
        results = []
        futures = []
        
        # Préparer les données pour multiprocessing
        model = self.loaded_models[job.model_id]
        
        # Soumettre tous les chunks
        for chunk_index, (start_idx, chunk_data) in enumerate(chunks):
            future = self.process_pool.submit(
                _process_chunk_worker,
                job.job_id, model, chunk_index, start_idx, chunk_data
            )
            futures.append((chunk_index, future))
        
        # Collecter les résultats
        completed_chunks = 0
        for chunk_index, future in futures:
            try:
                result = future.result(timeout=600)  # 10 minutes timeout
                results.append(result)
                completed_chunks += 1
                
                # Mettre à jour le progrès
                progress = (completed_chunks / len(chunks)) * 100
                self._update_job_progress(job.job_id, progress)
                
            except Exception as e:
                logger.error(f"Erreur chunk processus {chunk_index}: {e}")
                results.append(ChunkResult(
                    chunk_id=f"{job.job_id}_chunk_{chunk_index}",
                    chunk_index=chunk_index,
                    predictions=[],
                    processing_time=0.0,
                    success=False,
                    error_message=str(e),
                    items_processed=0
                ))
        
        return results
    
    def _process_single_chunk(self,
                             job_id: str,
                             model_id: str,
                             chunk_index: int,
                             start_idx: int,
                             chunk_data: Any) -> ChunkResult:
        """Traite un seul chunk"""
        
        chunk_id = f"{job_id}_chunk_{chunk_index}"
        start_time = time.time()
        
        try:
            model = self.loaded_models[model_id]
            
            # Effectuer la prédiction
            predictions = model.predict(chunk_data)
            
            # Convertir en liste si nécessaire
            if isinstance(predictions, np.ndarray):
                predictions = predictions.tolist()
            elif not isinstance(predictions, list):
                predictions = [predictions]
            
            processing_time = time.time() - start_time
            items_processed = len(predictions)
            
            return ChunkResult(
                chunk_id=chunk_id,
                chunk_index=chunk_index,
                predictions=predictions,
                processing_time=processing_time,
                success=True,
                items_processed=items_processed
            )
            
        except Exception as e:
            logger.error(f"Erreur traitement chunk {chunk_id}: {e}")
            return ChunkResult(
                chunk_id=chunk_id,
                chunk_index=chunk_index,
                predictions=[],
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e),
                items_processed=len(chunk_data) if hasattr(chunk_data, '__len__') else 1
            )
    
    def _update_job_progress(self, job_id: str, progress: float):
        """Met à jour le progrès d'un job"""
        try:
            if job_id in self.jobs:
                self.jobs[job_id].progress = progress
                
                # Appeler les callbacks de progrès
                for callback in self.progress_callbacks:
                    try:
                        callback(job_id, progress)
                    except Exception as e:
                        logger.error(f"Erreur callback progrès: {e}")
                        
        except Exception as e:
            logger.error(f"Erreur mise à jour progrès: {e}")
    
    def _save_checkpoint(self, job: BatchJob, chunks_processed: int):
        """Sauvegarde un checkpoint"""
        try:
            if not job.checkpoint_path:
                return
            
            checkpoint_data = {
                'job_id': job.job_id,
                'processed_items': job.processed_items,
                'chunks_processed': chunks_processed,
                'progress': job.progress,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(job.checkpoint_path, 'wb') as f:
                pickle.dump(checkpoint_data, f)
                
            logger.debug(f"Checkpoint sauvegardé pour job {job.job_id}")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde checkpoint: {e}")
    
    def _load_checkpoint(self, checkpoint_path: str) -> Optional[Dict[str, Any]]:
        """Charge un checkpoint"""
        try:
            if not Path(checkpoint_path).exists():
                return None
            
            with open(checkpoint_path, 'rb') as f:
                checkpoint_data = pickle.load(f)
            
            logger.info(f"Checkpoint chargé: {checkpoint_path}")
            return checkpoint_data
            
        except Exception as e:
            logger.error(f"Erreur chargement checkpoint: {e}")
            return None
    
    def _save_results(self, output_path: str, predictions: List[Any]):
        """Sauvegarde les résultats"""
        try:
            output_file = Path(output_path)
            
            if output_file.suffix.lower() == '.json':
                with open(output_file, 'w') as f:
                    json.dump(predictions, f, indent=2)
            elif output_file.suffix.lower() == '.pkl':
                with open(output_file, 'wb') as f:
                    pickle.dump(predictions, f)
            elif output_file.suffix.lower() == '.csv':
                pd.DataFrame(predictions).to_csv(output_file, index=False)
            else:
                # Default to JSON
                with open(output_file, 'w') as f:
                    json.dump(predictions, f, indent=2)
            
            logger.info(f"Résultats sauvegardés: {output_file}")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde résultats: {e}")
    
    async def _monitoring_loop(self):
        """Boucle de monitoring"""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Toutes les 30 secondes
                
                # Mettre à jour les métriques
                self.metrics.active_jobs = len(self.running_jobs)
                self.metrics.queued_jobs = len(self.job_queue)
                
                if self.metrics.total_jobs_processed > 0:
                    self.metrics.average_throughput = (
                        self.metrics.total_items_processed / 
                        self.metrics.total_processing_time
                    )
                
                # Loguer les métriques
                logger.info(
                    f"Batch metrics - "
                    f"Active: {self.metrics.active_jobs}, "
                    f"Queued: {self.metrics.queued_jobs}, "
                    f"Total processed: {self.metrics.total_jobs_processed}, "
                    f"Throughput: {self.metrics.average_throughput:.1f} items/s"
                )
                
            except Exception as e:
                logger.error(f"Erreur boucle monitoring: {e}")
    
    # API publique
    
    def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """Récupère le statut d'un job"""
        return self.jobs.get(job_id)
    
    def get_job_result(self, job_id: str) -> Optional[BatchResult]:
        """Récupère le résultat d'un job"""
        return self.job_results.get(job_id)
    
    def cancel_job(self, job_id: str) -> bool:
        """Annule un job"""
        try:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                if job.status in [BatchStatus.PENDING, BatchStatus.QUEUED]:
                    job.status = BatchStatus.CANCELLED
                    # Retirer de la queue si présent
                    if job_id in self.job_queue:
                        self.job_queue.remove(job_id)
                    return True
                elif job.status == BatchStatus.RUNNING:
                    # Pour les jobs en cours, marquer pour arrêt
                    job.status = BatchStatus.CANCELLED
                    return True
            return False
        except Exception as e:
            logger.error(f"Erreur annulation job {job_id}: {e}")
            return False
    
    def list_jobs(self, status_filter: Optional[BatchStatus] = None) -> List[BatchJob]:
        """Liste les jobs"""
        jobs = list(self.jobs.values())
        if status_filter:
            jobs = [job for job in jobs if job.status == status_filter]
        return jobs
    
    def add_progress_callback(self, callback: Callable[[str, float], None]):
        """Ajoute un callback de progrès"""
        self.progress_callbacks.append(callback)
    
    def add_completion_callback(self, callback: Callable[[BatchResult], None]):
        """Ajoute un callback de completion"""
        self.completion_callbacks.append(callback)
    
    def get_metrics(self) -> BatchMetrics:
        """Récupère les métriques"""
        return self.metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification de santé"""
        return {
            "status": "healthy" if self.is_running else "stopped",
            "active_jobs": self.metrics.active_jobs,
            "queued_jobs": self.metrics.queued_jobs,
            "loaded_models": len(self.loaded_models),
            "thread_pool_active": self.thread_pool._threads,
            "process_pool_active": len(self.process_pool._processes) if hasattr(self.process_pool, '_processes') else 0,
            "metrics": self.metrics.__dict__
        }


# Fonction worker pour multiprocessing
def _process_chunk_worker(job_id: str, model: Any, chunk_index: int, start_idx: int, chunk_data: Any) -> ChunkResult:
    """Worker function pour traitement multiprocessus"""
    chunk_id = f"{job_id}_chunk_{chunk_index}"
    start_time = time.time()
    
    try:
        # Effectuer la prédiction
        predictions = model.predict(chunk_data)
        
        # Convertir en liste si nécessaire
        if isinstance(predictions, np.ndarray):
            predictions = predictions.tolist()
        elif not isinstance(predictions, list):
            predictions = [predictions]
        
        processing_time = time.time() - start_time
        items_processed = len(predictions)
        
        return ChunkResult(
            chunk_id=chunk_id,
            chunk_index=chunk_index,
            predictions=predictions,
            processing_time=processing_time,
            success=True,
            items_processed=items_processed
        )
        
    except Exception as e:
        return ChunkResult(
            chunk_id=chunk_id,
            chunk_index=chunk_index,
            predictions=[],
            processing_time=time.time() - start_time,
            success=False,
            error_message=str(e),
            items_processed=len(chunk_data) if hasattr(chunk_data, '__len__') else 1
        )


# Factory pour créer des processeurs spécialisés
class BatchProcessorFactory:
    """Factory pour créer des processeurs batch spécialisés"""
    
    @staticmethod
    def create_high_throughput_processor() -> BatchInferenceProcessor:
        """Processeur optimisé pour débit élevé"""
        return BatchInferenceProcessor(
            max_workers=32,
            max_memory_mb=16384,
            checkpoint_interval=500,
            enable_checkpointing=True
        )
    
    @staticmethod
    def create_memory_efficient_processor() -> BatchInferenceProcessor:
        """Processeur optimisé pour efficacité mémoire"""
        return BatchInferenceProcessor(
            max_workers=8,
            max_memory_mb=4096,
            checkpoint_interval=100,
            enable_checkpointing=True
        )
    
    @staticmethod
    def create_development_processor() -> BatchInferenceProcessor:
        """Processeur pour développement"""
        return BatchInferenceProcessor(
            max_workers=4,
            max_memory_mb=2048,
            checkpoint_interval=1000,
            enable_checkpointing=False
        )


# Exemple d'utilisation
async def example_usage():
    """Exemple d'utilisation du processeur batch"""
    
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    import numpy as np
    
    # Créer des données d'exemple plus importantes
    X, y = make_classification(n_samples=10000, n_features=20, random_state=42)
    
    # Entraîner un modèle
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X[:1000], y[:1000])  # Entraîner sur un sous-ensemble
    
    # Créer le processeur
    processor = BatchProcessorFactory.create_development_processor()
    
    # Ajouter des callbacks
    def progress_callback(job_id: str, progress: float):
        print(f"Job {job_id}: {progress:.1f}% terminé")
    
    def completion_callback(result: BatchResult):
        print(f"Job terminé: {result.job_id}")
        print(f"- Éléments traités: {result.successful_items}/{result.total_items}")
        print(f"- Temps: {result.processing_time:.2f}s")
        print(f"- Débit: {result.throughput_items_per_second:.1f} éléments/s")
    
    processor.add_progress_callback(progress_callback)
    processor.add_completion_callback(completion_callback)
    
    try:
        # Démarrer le processeur
        await processor.start()
        
        # Charger le modèle
        await processor.load_model("test_batch_classifier", model)
        
        # Soumettre un job batch
        job_id = await processor.submit_batch_job(
            model_id="test_batch_classifier",
            input_data=X[1000:],  # Prédire sur le reste
            output_path="/tmp/batch_predictions.json",
            chunk_size=500,
            processing_mode=ProcessingMode.PARALLEL_THREAD,
            chunk_strategy=ChunkStrategy.ADAPTIVE,
            job_name="test_classification"
        )
        
        print(f"Job soumis: {job_id}")
        
        # Attendre la completion
        while True:
            job_status = processor.get_job_status(job_id)
            if job_status and job_status.status in [
                BatchStatus.COMPLETED, BatchStatus.FAILED, BatchStatus.CANCELLED
            ]:
                break
            await asyncio.sleep(2)
        
        # Afficher les résultats
        result = processor.get_job_result(job_id)
        if result:
            print(f"\nRésultats finaux:")
            print(f"- Prédictions: {len(result.predictions)}")
            print(f"- Succès: {result.successful_items}")
            print(f"- Échecs: {result.failed_items}")
            print(f"- Temps total: {result.processing_time:.2f}s")
            print(f"- Débit moyen: {result.throughput_items_per_second:.1f} éléments/s")
            print(f"- Latence moyenne: {result.average_latency_ms:.2f}ms")
        
        # Métriques du processeur
        metrics = processor.get_metrics()
        print(f"\nMétriques processeur:")
        print(f"- Jobs traités: {metrics.total_jobs_processed}")
        print(f"- Éléments traités: {metrics.total_items_processed}")
        print(f"- Débit moyen: {metrics.average_throughput:.1f} éléments/s")
        
        # Santé du système
        health = await processor.health_check()
        print(f"\nSanté système: {health}")
        
    finally:
        # Arrêter le processeur
        await processor.stop()


if __name__ == "__main__":
    asyncio.run(example_usage())