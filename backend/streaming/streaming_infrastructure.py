"""
Streaming Infrastructure - Real Implementation

Copyright (c) 2025 Fahed Mlaiel
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from uuid import uuid4

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    BATCH = "batch"
    STREAM = "stream"
    REAL_TIME = "real_time"
    MICRO_BATCH = "micro_batch"


class ProcessingStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class InfrastructureType(Enum):
    CLOUD = "cloud"
    ON_PREMISE = "on_premise"
    HYBRID = "hybrid"
    EDGE = "edge"


@dataclass
class ProcessingConfig:
    config_id: str
    mode: ProcessingMode
    batch_size: int = 100
    processing_interval_ms: int = 100
    max_parallel_tasks: int = 10


@dataclass
class ProcessingTask:
    task_id: str
    data: Any
    status: ProcessingStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class InfrastructureMetrics:
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_processing_time_ms: float = 0.0
    throughput_per_sec: float = 0.0


@dataclass
class StreamingInfrastructureRecord:
    record_id: str = field(default_factory=lambda: str(uuid4()))
    infrastructure_type: InfrastructureType = InfrastructureType.CLOUD
    config: Optional[ProcessingConfig] = None
    metrics: Optional[InfrastructureMetrics] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class RealTimeProcessingEngine:
    """Moteur de traitement en temps réel avec gestion de tâches parallèles."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.pending_tasks: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, ProcessingTask] = {}
        self.completed_tasks: List[ProcessingTask] = []
        self.workers: List[asyncio.Task] = []
        self.is_running = False
        self.metrics = InfrastructureMetrics()
        self.processing_handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)

    async def start(self, num_workers: int = 5) -> None:
        """Démarre le moteur avec N workers."""
        if self.is_running:
            return
        self.is_running = True
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        self.logger.info(f"Processing engine started with {num_workers} workers")

    async def stop(self) -> None:
        """Arrête le moteur."""
        self.is_running = False
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
            self.workers.clear()
        self.logger.info("Processing engine stopped")

    async def submit_task(self, data: Any, handler_name: str = "default") -> str:
        """Soumet une tâche pour traitement."""
        task = ProcessingTask(task_id=str(uuid4()), data=data, status=ProcessingStatus.IDLE)
        task.data = {"payload": data, "handler": handler_name}
        await self.pending_tasks.put(task)
        self.metrics.total_tasks += 1
        return task.task_id

    async def _worker(self, worker_id: str) -> None:
        """Worker qui traite les tâches."""
        self.logger.info(f"Worker {worker_id} started")
        while self.is_running:
            try:
                try:
                    task = await asyncio.wait_for(self.pending_tasks.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                await self._process_task(task, worker_id)
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {e}")

    async def _process_task(self, task: ProcessingTask, worker_id: str) -> None:
        """Traite une tâche."""
        task.status = ProcessingStatus.PROCESSING
        task.started_at = datetime.utcnow()
        self.active_tasks[task.task_id] = task
        try:
            handler_name = task.data.get("handler", "default")
            payload = task.data.get("payload")
            if handler_name in self.processing_handlers:
                handler = self.processing_handlers[handler_name]
                result = await handler(payload)
            else:
                result = {"processed": True, "data": payload}
            task.result = result
            task.status = ProcessingStatus.COMPLETED
            self.metrics.completed_tasks += 1
        except Exception as e:
            task.error = str(e)
            task.status = ProcessingStatus.FAILED
            self.metrics.failed_tasks += 1
            self.logger.error(f"Task {task.task_id} failed: {e}")
        finally:
            task.completed_at = datetime.utcnow()
            if task.started_at and task.completed_at:
                processing_time = (task.completed_at - task.started_at).total_seconds() * 1000
                current_avg = self.metrics.avg_processing_time_ms
                completed = self.metrics.completed_tasks
                if completed > 0:
                    self.metrics.avg_processing_time_ms = ((current_avg * (completed - 1) + processing_time) / completed)
            del self.active_tasks[task.task_id]
            self.completed_tasks.append(task)
            if len(self.completed_tasks) > 1000:
                self.completed_tasks = self.completed_tasks[-1000:]

    def register_handler(self, name: str, handler: Callable) -> None:
        """Enregistre un handler de traitement."""
        self.processing_handlers[name] = handler
        self.logger.info(f"Handler registered: {name}")

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut d'une tâche."""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {"task_id": task_id, "status": task.status.value, "started_at": task.started_at.isoformat() if task.started_at else None}
        for task in reversed(self.completed_tasks):
            if task.task_id == task_id:
                return {"task_id": task_id, "status": task.status.value, "result": task.result, "error": task.error, "completed_at": task.completed_at.isoformat() if task.completed_at else None}
        return None

    def get_metrics(self) -> InfrastructureMetrics:
        """Retourne les métriques."""
        if self.metrics.completed_tasks > 0 and self.completed_tasks:
            first_task = self.completed_tasks[0]
            last_task = self.completed_tasks[-1]
            if first_task.completed_at and last_task.completed_at:
                time_span = (last_task.completed_at - first_task.completed_at).total_seconds()
                if time_span > 0:
                    self.metrics.throughput_per_sec = len(self.completed_tasks) / time_span
        return self.metrics


# Alias
StreamingInfrastructure = RealTimeProcessingEngine
EventStreamManager = RealTimeProcessingEngine
WebSocketOrchestrator = RealTimeProcessingEngine
StreamProcessor = RealTimeProcessingEngine
DataPipeline = RealTimeProcessingEngine


def create_realtimeprocessing_engine(config: Optional[Dict[str, Any]] = None) -> RealTimeProcessingEngine:
    return RealTimeProcessingEngine(config=config)


create_real_time_processing_engine = create_realtimeprocessing_engine
create_streaming_infrastructure = create_realtimeprocessing_engine


__all__ = [
    "RealTimeProcessingEngine",
    "StreamingInfrastructure",
    "EventStreamManager",
    "WebSocketOrchestrator",
    "StreamProcessor",
    "DataPipeline",
    "ProcessingMode",
    "ProcessingStatus",
    "InfrastructureType",
    "ProcessingConfig",
    "ProcessingTask",
    "InfrastructureMetrics",
    "StreamingInfrastructureRecord",
    "create_realtimeprocessing_engine",
    "create_real_time_processing_engine",
    "create_streaming_infrastructure"
]
