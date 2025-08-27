"""
Notification Queue Manager

Gestionnaire avancé des files d'attente de notifications avec priorités,
retry logic, dead letter queues et processing distribué.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer, Backend Senior, Queue Systems Expert
Copyright © 2025 Fahed Mlaiel. Tous droits réservés.

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et constitue une violation des droits d'auteur.
Les contrevenants s'exposent à des poursuites judiciaires.
"""

from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import uuid
import pickle
import zlib
from abc import ABC, abstractmethod
import aioredis
import asyncpg
from celery import Celery
from kombu import Queue, Exchange
import aiormq
import aio_pika

logger = logging.getLogger(__name__)


class QueuePriority(Enum):
    """Priorités des queues"""
    VERY_LOW = 1
    LOW = 2
    NORMAL = 3
    HIGH = 4
    VERY_HIGH = 5
    URGENT = 6
    CRITICAL = 7


class ProcessingStatus(Enum):
    """Statuts de traitement"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD = "dead"
    CANCELLED = "cancelled"


class QueueType(Enum):
    """Types de queues"""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    WEBHOOK = "webhook"
    REALTIME = "realtime"
    ALERT = "alert"
    BATCH = "batch"
    SCHEDULED = "scheduled"


@dataclass
class QueueMessage:
    """Message de queue"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    queue_type: QueueType = QueueType.EMAIL
    priority: QueuePriority = QueuePriority.NORMAL
    payload: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    routing_key: str = ""
    exchange: str = "notifications"
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    max_retries: int = 3
    retry_count: int = 0
    retry_delay: int = 60  # seconds
    retry_backoff_factor: float = 2.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueueStats:
    """Statistiques de queue"""
    queue_name: str = ""
    total_messages: int = 0
    pending_messages: int = 0
    processing_messages: int = 0
    completed_messages: int = 0
    failed_messages: int = 0
    dead_messages: int = 0
    avg_processing_time: float = 0.0
    throughput_per_minute: float = 0.0
    last_processed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProcessingResult:
    """Résultat de traitement"""
    message_id: str = ""
    status: ProcessingStatus = ProcessingStatus.COMPLETED
    success: bool = True
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    processing_time: float = 0.0
    retry_after: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed_at: datetime = field(default_factory=datetime.utcnow)


class MessageProcessor(ABC):
    """Processeur de messages abstrait"""
    
    @abstractmethod
    async def process(self, message: QueueMessage) -> ProcessingResult:
        """Traiter un message"""
        pass
    
    @abstractmethod
    def get_queue_type(self) -> QueueType:
        """Retourner le type de queue supporté"""
        pass


class EmailProcessor(MessageProcessor):
    """Processeur de messages email"""
    
    def __init__(self, email_manager):
        self.email_manager = email_manager
    
    async def process(self, message: QueueMessage) -> ProcessingResult:
        """Traiter un message email"""
        try:
            start_time = datetime.utcnow()
            
            # Extraire les données email du payload
            email_data = message.payload
            
            # Créer le message email
            from .email_manager import EmailMessage, EmailPriority
            email_message = EmailMessage(
                to_email=email_data["to_email"],
                to_name=email_data.get("to_name", ""),
                from_email=email_data["from_email"],
                from_name=email_data.get("from_name", ""),
                subject=email_data["subject"],
                html_content=email_data.get("html_content", ""),
                text_content=email_data.get("text_content", ""),
                template_id=email_data.get("template_id"),
                template_data=email_data.get("template_data", {}),
                priority=EmailPriority(email_data.get("priority", "normal"))
            )
            
            # Envoyer l'email
            result_id = await self.email_manager.send_email(email_message)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                message_id=message.id,
                status=ProcessingStatus.COMPLETED,
                success=True,
                processing_time=processing_time,
                metadata={"email_id": result_id}
            )
            
        except Exception as e:
            logger.error(f"Erreur traitement email {message.id}: {e}")
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                message_id=message.id,
                status=ProcessingStatus.FAILED,
                success=False,
                error_message=str(e),
                error_type=type(e).__name__,
                processing_time=processing_time
            )
    
    def get_queue_type(self) -> QueueType:
        return QueueType.EMAIL


class PushProcessor(MessageProcessor):
    """Processeur de notifications push"""
    
    def __init__(self, push_manager):
        self.push_manager = push_manager
    
    async def process(self, message: QueueMessage) -> ProcessingResult:
        """Traiter une notification push"""
        try:
            start_time = datetime.utcnow()
            
            # Extraire les données push du payload
            push_data = message.payload
            
            # Créer la notification push
            from .push_manager import PushNotification, NotificationType, PushPriority
            notification = PushNotification(
                user_id=push_data["user_id"],
                device_id=push_data.get("device_id"),
                notification_type=NotificationType(push_data.get("type", "system_alert")),
                title=push_data["title"],
                body=push_data["body"],
                icon=push_data.get("icon"),
                image=push_data.get("image"),
                data=push_data.get("data", {}),
                priority=PushPriority(push_data.get("priority", "normal"))
            )
            
            # Envoyer la notification
            result_id = await self.push_manager.send_notification(notification)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                message_id=message.id,
                status=ProcessingStatus.COMPLETED,
                success=True,
                processing_time=processing_time,
                metadata={"notification_id": result_id}
            )
            
        except Exception as e:
            logger.error(f"Erreur traitement push {message.id}: {e}")
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                message_id=message.id,
                status=ProcessingStatus.FAILED,
                success=False,
                error_message=str(e),
                error_type=type(e).__name__,
                processing_time=processing_time
            )
    
    def get_queue_type(self) -> QueueType:
        return QueueType.PUSH


class WebhookProcessor(MessageProcessor):
    """Processeur de webhooks"""
    
    def __init__(self, http_client):
        self.http_client = http_client
    
    async def process(self, message: QueueMessage) -> ProcessingResult:
        """Traiter un webhook"""
        try:
            start_time = datetime.utcnow()
            
            # Extraire les données webhook du payload
            webhook_data = message.payload
            url = webhook_data["url"]
            method = webhook_data.get("method", "POST")
            headers = webhook_data.get("headers", {})
            data = webhook_data.get("data", {})
            timeout = webhook_data.get("timeout", 30)
            
            # Envoyer la requête webhook
            async with self.http_client.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=timeout
            ) as response:
                
                response_data = {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "body": await response.text()
                }
                
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                
                if 200 <= response.status < 300:
                    return ProcessingResult(
                        message_id=message.id,
                        status=ProcessingStatus.COMPLETED,
                        success=True,
                        processing_time=processing_time,
                        metadata={"response": response_data}
                    )
                else:
                    return ProcessingResult(
                        message_id=message.id,
                        status=ProcessingStatus.FAILED,
                        success=False,
                        error_message=f"HTTP {response.status}: {response_data['body']}",
                        error_type="HTTPError",
                        processing_time=processing_time,
                        metadata={"response": response_data}
                    )
                    
        except Exception as e:
            logger.error(f"Erreur traitement webhook {message.id}: {e}")
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                message_id=message.id,
                status=ProcessingStatus.FAILED,
                success=False,
                error_message=str(e),
                error_type=type(e).__name__,
                processing_time=processing_time
            )
    
    def get_queue_type(self) -> QueueType:
        return QueueType.WEBHOOK


class RedisQueueBackend:
    """Backend Redis pour les queues"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        
    async def enqueue(self, queue_name: str, message: QueueMessage, delay: Optional[int] = None):
        """Ajouter un message à la queue"""
        try:
            # Sérialiser le message
            serialized_message = self._serialize_message(message)
            
            if delay:
                # Queue avec délai
                score = (datetime.utcnow() + timedelta(seconds=delay)).timestamp()
                await self.redis.zadd(f"queue:delayed:{queue_name}", {serialized_message: score})
            else:
                # Queue immédiate avec priorité
                priority_score = message.priority.value
                await self.redis.zadd(f"queue:{queue_name}", {serialized_message: priority_score})
            
            # Mettre à jour les stats
            await self._update_queue_stats(queue_name, "enqueued")
            
        except Exception as e:
            logger.error(f"Erreur enqueue Redis {queue_name}: {e}")
            raise
    
    async def dequeue(self, queue_name: str, timeout: int = 10) -> Optional[QueueMessage]:
        """Récupérer un message de la queue"""
        try:
            # Vérifier d'abord les messages délayés
            await self._process_delayed_messages(queue_name)
            
            # Récupérer le message avec la plus haute priorité
            result = await self.redis.bzpopmax(f"queue:{queue_name}", timeout=timeout)
            
            if not result:
                return None
            
            # Désérialiser le message
            _, serialized_message, _ = result
            message = self._deserialize_message(serialized_message)
            
            # Marquer comme en cours de traitement
            await self._mark_processing(queue_name, message)
            
            return message
            
        except Exception as e:
            logger.error(f"Erreur dequeue Redis {queue_name}: {e}")
            return None
    
    async def ack(self, queue_name: str, message: QueueMessage, result: ProcessingResult):
        """Acquitter un message traité"""
        try:
            # Supprimer de la liste de traitement
            await self.redis.zrem(f"queue:processing:{queue_name}", self._serialize_message(message))
            
            # Sauvegarder le résultat
            await self._save_processing_result(queue_name, result)
            
            # Mettre à jour les stats
            status = "completed" if result.success else "failed"
            await self._update_queue_stats(queue_name, status, result.processing_time)
            
        except Exception as e:
            logger.error(f"Erreur ack Redis {queue_name}: {e}")
    
    async def nack(self, queue_name: str, message: QueueMessage, retry_delay: Optional[int] = None):
        """Rejeter un message et le remettre en queue"""
        try:
            # Supprimer de la liste de traitement
            await self.redis.zrem(f"queue:processing:{queue_name}", self._serialize_message(message))
            
            # Incrémenter le compteur de retry
            message.retry_count += 1
            message.updated_at = datetime.utcnow()
            
            if message.retry_count >= message.max_retries:
                # Envoyer vers la dead letter queue
                await self._send_to_dead_letter_queue(queue_name, message)
            else:
                # Remettre en queue avec délai
                delay = retry_delay or (message.retry_delay * (message.retry_backoff_factor ** message.retry_count))
                await self.enqueue(queue_name, message, delay=int(delay))
            
            # Mettre à jour les stats
            await self._update_queue_stats(queue_name, "retried")
            
        except Exception as e:
            logger.error(f"Erreur nack Redis {queue_name}: {e}")
    
    async def _process_delayed_messages(self, queue_name: str):
        """Traiter les messages délayés"""
        try:
            now = datetime.utcnow().timestamp()
            
            # Récupérer les messages dont le délai est expiré
            messages = await self.redis.zrangebyscore(
                f"queue:delayed:{queue_name}",
                0,
                now,
                withscores=True
            )
            
            for serialized_message, score in messages:
                # Déplacer vers la queue principale
                message = self._deserialize_message(serialized_message)
                await self.redis.zadd(f"queue:{queue_name}", {serialized_message: message.priority.value})
                
                # Supprimer de la queue délayée
                await self.redis.zrem(f"queue:delayed:{queue_name}", serialized_message)
                
        except Exception as e:
            logger.error(f"Erreur traitement messages délayés: {e}")
    
    async def _mark_processing(self, queue_name: str, message: QueueMessage):
        """Marquer un message comme en cours de traitement"""
        try:
            score = datetime.utcnow().timestamp()
            await self.redis.zadd(
                f"queue:processing:{queue_name}",
                {self._serialize_message(message): score}
            )
        except Exception as e:
            logger.error(f"Erreur mark processing: {e}")
    
    async def _send_to_dead_letter_queue(self, queue_name: str, message: QueueMessage):
        """Envoyer vers la dead letter queue"""
        try:
            await self.redis.lpush(
                f"queue:dead:{queue_name}",
                self._serialize_message(message)
            )
            
            await self._update_queue_stats(queue_name, "dead")
            
        except Exception as e:
            logger.error(f"Erreur dead letter queue: {e}")
    
    async def _save_processing_result(self, queue_name: str, result: ProcessingResult):
        """Sauvegarder le résultat de traitement"""
        try:
            key = f"queue:results:{queue_name}:{result.message_id}"
            await self.redis.setex(
                key,
                86400,  # 24 heures
                json.dumps(asdict(result), default=str)
            )
        except Exception as e:
            logger.error(f"Erreur sauvegarde résultat: {e}")
    
    async def _update_queue_stats(self, queue_name: str, event: str, processing_time: Optional[float] = None):
        """Mettre à jour les statistiques de queue"""
        try:
            key = f"queue:stats:{queue_name}"
            
            # Incrémenter les compteurs
            await self.redis.hincrby(key, f"{event}_count", 1)
            await self.redis.hincrby(key, "total_count", 1)
            
            # Mettre à jour le temps de traitement moyen
            if processing_time is not None:
                await self.redis.hincrbyfloat(key, "total_processing_time", processing_time)
                
                # Calculer la moyenne
                total_time = float(await self.redis.hget(key, "total_processing_time") or 0)
                completed_count = int(await self.redis.hget(key, "completed_count") or 1)
                avg_time = total_time / max(completed_count, 1)
                await self.redis.hset(key, "avg_processing_time", avg_time)
            
            # Mettre à jour le timestamp
            await self.redis.hset(key, "last_updated", datetime.utcnow().isoformat())
            
            # Expiration après 7 jours
            await self.redis.expire(key, 604800)
            
        except Exception as e:
            logger.error(f"Erreur mise à jour stats: {e}")
    
    def _serialize_message(self, message: QueueMessage) -> str:
        """Sérialiser un message"""
        try:
            # Convertir en dict
            message_dict = asdict(message)
            
            # Sérialiser avec JSON puis compresser
            json_data = json.dumps(message_dict, default=str)
            compressed_data = zlib.compress(json_data.encode())
            
            # Encoder en base64 pour stockage Redis
            import base64
            return base64.b64encode(compressed_data).decode()
            
        except Exception as e:
            logger.error(f"Erreur sérialisation message: {e}")
            raise
    
    def _deserialize_message(self, serialized_data: str) -> QueueMessage:
        """Désérialiser un message"""
        try:
            import base64
            
            # Décoder depuis base64
            compressed_data = base64.b64decode(serialized_data.encode())
            
            # Décompresser
            json_data = zlib.decompress(compressed_data).decode()
            
            # Désérialiser JSON
            message_dict = json.loads(json_data)
            
            # Reconstituer les enums et dates
            message_dict["queue_type"] = QueueType(message_dict["queue_type"])
            message_dict["priority"] = QueuePriority(message_dict["priority"])
            
            for date_field in ["created_at", "updated_at", "scheduled_at", "expires_at"]:
                if message_dict[date_field]:
                    message_dict[date_field] = datetime.fromisoformat(message_dict[date_field])
            
            return QueueMessage(**message_dict)
            
        except Exception as e:
            logger.error(f"Erreur désérialisation message: {e}")
            raise
    
    async def get_queue_stats(self, queue_name: str) -> QueueStats:
        """Récupérer les statistiques d'une queue"""
        try:
            key = f"queue:stats:{queue_name}"
            stats_data = await self.redis.hgetall(key)
            
            # Récupérer les tailles actuelles des queues
            pending_count = await self.redis.zcard(f"queue:{queue_name}")
            processing_count = await self.redis.zcard(f"queue:processing:{queue_name}")
            dead_count = await self.redis.llen(f"queue:dead:{queue_name}")
            
            return QueueStats(
                queue_name=queue_name,
                total_messages=int(stats_data.get("total_count", 0)),
                pending_messages=pending_count,
                processing_messages=processing_count,
                completed_messages=int(stats_data.get("completed_count", 0)),
                failed_messages=int(stats_data.get("failed_count", 0)),
                dead_messages=dead_count,
                avg_processing_time=float(stats_data.get("avg_processing_time", 0)),
                last_processed_at=datetime.fromisoformat(stats_data["last_updated"]) if stats_data.get("last_updated") else None
            )
            
        except Exception as e:
            logger.error(f"Erreur récupération stats queue: {e}")
            return QueueStats(queue_name=queue_name)


class NotificationQueueManager:
    """Gestionnaire principal des queues de notifications"""
    
    def __init__(self, db_pool: asyncpg.Pool, redis_client: aioredis.Redis, config: Dict[str, Any]):
        self.db_pool = db_pool
        self.redis = redis_client
        self.config = config
        
        # Backend de queue
        self.queue_backend = RedisQueueBackend(redis_client)
        
        # Processeurs
        self.processors: Dict[QueueType, MessageProcessor] = {}
        
        # Workers
        self.workers: Dict[str, asyncio.Task] = {}
        self.worker_configs = config.get("workers", {})
        
        # Monitoring
        self.is_running = False
        
    def register_processor(self, processor: MessageProcessor):
        """Enregistrer un processeur"""
        queue_type = processor.get_queue_type()
        self.processors[queue_type] = processor
        logger.info(f"Processeur enregistré pour {queue_type.value}")
    
    async def start(self):
        """Démarrer le gestionnaire de queues"""
        try:
            self.is_running = True
            
            # Démarrer les workers pour chaque type de queue
            for queue_type in QueueType:
                if queue_type in self.processors:
                    worker_config = self.worker_configs.get(queue_type.value, {"count": 1})
                    worker_count = worker_config.get("count", 1)
                    
                    for i in range(worker_count):
                        worker_name = f"{queue_type.value}_worker_{i}"
                        self.workers[worker_name] = asyncio.create_task(
                            self._worker_loop(worker_name, queue_type)
                        )
            
            # Démarrer les tâches de maintenance
            self.workers["maintenance"] = asyncio.create_task(self._maintenance_loop())
            self.workers["monitor"] = asyncio.create_task(self._monitoring_loop())
            
            logger.info(f"Gestionnaire de queues démarré avec {len(self.workers)} workers")
            
        except Exception as e:
            logger.error(f"Erreur démarrage gestionnaire queues: {e}")
            raise
    
    async def stop(self):
        """Arrêter le gestionnaire de queues"""
        try:
            self.is_running = False
            
            # Arrêter tous les workers
            for worker_name, task in self.workers.items():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self.workers.clear()
            logger.info("Gestionnaire de queues arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt gestionnaire queues: {e}")
    
    async def enqueue_message(self, message: QueueMessage) -> str:
        """Ajouter un message à la queue"""
        try:
            queue_name = message.queue_type.value
            
            # Calculer le délai si programmé
            delay = None
            if message.scheduled_at and message.scheduled_at > datetime.utcnow():
                delay = int((message.scheduled_at - datetime.utcnow()).total_seconds())
            
            # Ajouter à la queue
            await self.queue_backend.enqueue(queue_name, message, delay)
            
            # Sauvegarder en base pour audit
            await self._save_message_audit(message)
            
            logger.debug(f"Message {message.id} ajouté à la queue {queue_name}")
            return message.id
            
        except Exception as e:
            logger.error(f"Erreur ajout message queue: {e}")
            raise
    
    async def _worker_loop(self, worker_name: str, queue_type: QueueType):
        """Boucle de traitement d'un worker"""
        queue_name = queue_type.value
        processor = self.processors[queue_type]
        
        logger.info(f"Worker {worker_name} démarré pour queue {queue_name}")
        
        while self.is_running:
            try:
                # Récupérer un message de la queue
                message = await self.queue_backend.dequeue(queue_name, timeout=5)
                
                if not message:
                    continue
                
                logger.debug(f"Worker {worker_name} traite message {message.id}")
                
                # Vérifier l'expiration
                if message.expires_at and message.expires_at <= datetime.utcnow():
                    logger.warning(f"Message {message.id} expiré, ignoré")
                    await self.queue_backend.ack(queue_name, message, ProcessingResult(
                        message_id=message.id,
                        status=ProcessingStatus.CANCELLED,
                        success=False,
                        error_message="Message expired"
                    ))
                    continue
                
                # Traiter le message
                try:
                    result = await processor.process(message)
                    
                    if result.success:
                        # Acquitter le message
                        await self.queue_backend.ack(queue_name, message, result)
                        logger.debug(f"Message {message.id} traité avec succès")
                    else:
                        # Déterminer si on doit retry
                        if message.retry_count < message.max_retries:
                            retry_delay = result.retry_after or message.retry_delay
                            await self.queue_backend.nack(queue_name, message, retry_delay)
                            logger.warning(f"Message {message.id} échec, retry {message.retry_count + 1}/{message.max_retries}")
                        else:
                            # Envoyer vers dead letter queue
                            await self.queue_backend.ack(queue_name, message, result)
                            logger.error(f"Message {message.id} échec définitif après {message.max_retries} tentatives")
                    
                except Exception as e:
                    # Erreur de traitement
                    logger.error(f"Erreur traitement message {message.id} par worker {worker_name}: {e}")
                    
                    result = ProcessingResult(
                        message_id=message.id,
                        status=ProcessingStatus.FAILED,
                        success=False,
                        error_message=str(e),
                        error_type=type(e).__name__
                    )
                    
                    if message.retry_count < message.max_retries:
                        await self.queue_backend.nack(queue_name, message)
                    else:
                        await self.queue_backend.ack(queue_name, message, result)
                
            except Exception as e:
                logger.error(f"Erreur worker {worker_name}: {e}")
                await asyncio.sleep(10)  # Pause avant de reprendre
        
        logger.info(f"Worker {worker_name} arrêté")
    
    async def _maintenance_loop(self):
        """Boucle de maintenance"""
        logger.info("Tâche de maintenance démarrée")
        
        while self.is_running:
            try:
                # Nettoyer les messages en cours de traitement depuis trop longtemps
                await self._cleanup_stale_processing_messages()
                
                # Nettoyer les résultats anciens
                await self._cleanup_old_results()
                
                # Compacter les statistiques
                await self._compact_stats()
                
                # Attendre 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Erreur maintenance: {e}")
                await asyncio.sleep(60)
        
        logger.info("Tâche de maintenance arrêtée")
    
    async def _monitoring_loop(self):
        """Boucle de monitoring"""
        logger.info("Tâche de monitoring démarrée")
        
        while self.is_running:
            try:
                # Collecter les métriques
                await self._collect_metrics()
                
                # Vérifier les alertes
                await self._check_queue_alerts()
                
                # Attendre 1 minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Erreur monitoring: {e}")
                await asyncio.sleep(60)
        
        logger.info("Tâche de monitoring arrêtée")
    
    async def _cleanup_stale_processing_messages(self):
        """Nettoyer les messages en cours de traitement depuis trop longtemps"""
        try:
            stale_timeout = self.config.get("stale_processing_timeout", 3600)  # 1 heure
            cutoff_time = (datetime.utcnow() - timedelta(seconds=stale_timeout)).timestamp()
            
            for queue_type in QueueType:
                queue_name = queue_type.value
                processing_key = f"queue:processing:{queue_name}"
                
                # Récupérer les messages stale
                stale_messages = await self.redis.zrangebyscore(
                    processing_key,
                    0,
                    cutoff_time,
                    withscores=True
                )
                
                for serialized_message, score in stale_messages:
                    # Remettre en queue
                    message = self.queue_backend._deserialize_message(serialized_message)
                    await self.queue_backend.nack(queue_name, message)
                    
                    logger.warning(f"Message stale remis en queue: {message.id}")
                    
        except Exception as e:
            logger.error(f"Erreur nettoyage messages stale: {e}")
    
    async def _cleanup_old_results(self):
        """Nettoyer les anciens résultats"""
        try:
            # Les résultats sont automatiquement expirés par Redis (24h)
            # Cette fonction peut être étendue pour d'autres nettoyages
            pass
        except Exception as e:
            logger.error(f"Erreur nettoyage résultats: {e}")
    
    async def _compact_stats(self):
        """Compacter les statistiques"""
        try:
            # Archiver les stats anciennes vers la base de données
            for queue_type in QueueType:
                queue_name = queue_type.value
                stats = await self.queue_backend.get_queue_stats(queue_name)
                
                if stats.total_messages > 0:
                    await self._save_stats_snapshot(stats)
                    
        except Exception as e:
            logger.error(f"Erreur compactage stats: {e}")
    
    async def _collect_metrics(self):
        """Collecter les métriques"""
        try:
            metrics = {}
            
            for queue_type in QueueType:
                queue_name = queue_type.value
                stats = await self.queue_backend.get_queue_stats(queue_name)
                
                metrics[queue_name] = {
                    "pending": stats.pending_messages,
                    "processing": stats.processing_messages,
                    "completed": stats.completed_messages,
                    "failed": stats.failed_messages,
                    "dead": stats.dead_messages,
                    "avg_processing_time": stats.avg_processing_time
                }
            
            # Publier les métriques vers un système de monitoring externe
            await self.redis.setex(
                "queue:metrics",
                300,  # 5 minutes
                json.dumps(metrics, default=str)
            )
            
        except Exception as e:
            logger.error(f"Erreur collecte métriques: {e}")
    
    async def _check_queue_alerts(self):
        """Vérifier les alertes de queue"""
        try:
            alert_thresholds = self.config.get("alert_thresholds", {})
            
            for queue_type in QueueType:
                queue_name = queue_type.value
                stats = await self.queue_backend.get_queue_stats(queue_name)
                
                # Vérifier les seuils
                if stats.pending_messages > alert_thresholds.get("pending_messages", 1000):
                    logger.warning(f"Queue {queue_name} a {stats.pending_messages} messages en attente")
                
                if stats.dead_messages > alert_thresholds.get("dead_messages", 100):
                    logger.error(f"Queue {queue_name} a {stats.dead_messages} messages morts")
                
                if stats.avg_processing_time > alert_thresholds.get("avg_processing_time", 60):
                    logger.warning(f"Queue {queue_name} temps de traitement moyen élevé: {stats.avg_processing_time}s")
                    
        except Exception as e:
            logger.error(f"Erreur vérification alertes: {e}")
    
    async def _save_message_audit(self, message: QueueMessage):
        """Sauvegarder un audit de message"""
        async with self.db_pool.acquire() as conn:
            query = """
                INSERT INTO notification_queue_audit (
                    message_id, queue_type, priority, payload, headers,
                    routing_key, exchange, scheduled_at, expires_at,
                    max_retries, metadata, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """
            
            await conn.execute(
                query,
                message.id, message.queue_type.value, message.priority.value,
                json.dumps(message.payload), json.dumps(message.headers),
                message.routing_key, message.exchange, message.scheduled_at,
                message.expires_at, message.max_retries, json.dumps(message.metadata),
                message.created_at
            )
    
    async def _save_stats_snapshot(self, stats: QueueStats):
        """Sauvegarder un snapshot de statistiques"""
        async with self.db_pool.acquire() as conn:
            query = """
                INSERT INTO notification_queue_stats (
                    queue_name, total_messages, pending_messages,
                    processing_messages, completed_messages, failed_messages,
                    dead_messages, avg_processing_time, throughput_per_minute,
                    last_processed_at, snapshot_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """
            
            await conn.execute(
                query,
                stats.queue_name, stats.total_messages, stats.pending_messages,
                stats.processing_messages, stats.completed_messages,
                stats.failed_messages, stats.dead_messages, stats.avg_processing_time,
                stats.throughput_per_minute, stats.last_processed_at, datetime.utcnow()
            )
    
    async def get_queue_status(self, queue_type: Optional[QueueType] = None) -> Dict[str, QueueStats]:
        """Récupérer le statut des queues"""
        try:
            status = {}
            
            queue_types = [queue_type] if queue_type else list(QueueType)
            
            for qt in queue_types:
                queue_name = qt.value
                stats = await self.queue_backend.get_queue_stats(queue_name)
                status[queue_name] = stats
            
            return status
            
        except Exception as e:
            logger.error(f"Erreur récupération statut queues: {e}")
            return {}
    
    async def purge_queue(self, queue_type: QueueType, confirm: bool = False) -> int:
        """Purger une queue (attention: action destructive)"""
        if not confirm:
            raise ValueError("Purge must be confirmed with confirm=True")
        
        try:
            queue_name = queue_type.value
            
            # Compter les messages avant suppression
            pending_count = await self.redis.zcard(f"queue:{queue_name}")
            delayed_count = await self.redis.zcard(f"queue:delayed:{queue_name}")
            processing_count = await self.redis.zcard(f"queue:processing:{queue_name}")
            
            total_count = pending_count + delayed_count + processing_count
            
            # Supprimer toutes les queues
            await self.redis.delete(f"queue:{queue_name}")
            await self.redis.delete(f"queue:delayed:{queue_name}")
            await self.redis.delete(f"queue:processing:{queue_name}")
            
            logger.warning(f"Queue {queue_name} purgée: {total_count} messages supprimés")
            return total_count
            
        except Exception as e:
            logger.error(f"Erreur purge queue {queue_type.value}: {e}")
            raise
    
    async def get_dead_letter_messages(self, queue_type: QueueType, limit: int = 100) -> List[QueueMessage]:
        """Récupérer les messages de la dead letter queue"""
        try:
            queue_name = queue_type.value
            
            # Récupérer les messages morts
            serialized_messages = await self.redis.lrange(f"queue:dead:{queue_name}", 0, limit - 1)
            
            messages = []
            for serialized_message in serialized_messages:
                try:
                    message = self.queue_backend._deserialize_message(serialized_message)
                    messages.append(message)
                except Exception as e:
                    logger.error(f"Erreur désérialisation message mort: {e}")
            
            return messages
            
        except Exception as e:
            logger.error(f"Erreur récupération messages morts: {e}")
            return []
    
    async def requeue_dead_message(self, queue_type: QueueType, message_id: str) -> bool:
        """Remettre un message mort en queue"""
        try:
            queue_name = queue_type.value
            dead_queue_key = f"queue:dead:{queue_name}"
            
            # Rechercher le message dans la dead letter queue
            serialized_messages = await self.redis.lrange(dead_queue_key, 0, -1)
            
            for i, serialized_message in enumerate(serialized_messages):
                try:
                    message = self.queue_backend._deserialize_message(serialized_message)
                    if message.id == message_id:
                        # Réinitialiser le compteur de retry
                        message.retry_count = 0
                        message.updated_at = datetime.utcnow()
                        
                        # Remettre en queue
                        await self.queue_backend.enqueue(queue_name, message)
                        
                        # Supprimer de la dead letter queue
                        await self.redis.lrem(dead_queue_key, 1, serialized_message)
                        
                        logger.info(f"Message {message_id} remis en queue depuis dead letter")
                        return True
                        
                except Exception as e:
                    logger.error(f"Erreur traitement message mort: {e}")
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur requeue message mort: {e}")
            return False
