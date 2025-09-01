"""🚀 Message Queue System - IA Influencer Agent Platform Enterprise
===============================================================
Module: backend/platform_core/communication/message_queue.py
Author: Fahed Mlaiel (mlaiel@live.de)
===============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE FILES D'ATTENTE ASYNCHRONE
Message queue enterprise avec traitement distribué
- Redis Streams pour haute performance
- Dead Letter Queue pour gestion d'erreurs
- Priority queues avec backpressure
- Monitoring temps réel et métriques avancées
"""
import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Coroutine
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import pickle
import hashlib

import aioredis
from pydantic import BaseModel, Field

# Configuration
logger = logging.getLogger(__name__)

class MessagePriority(Enum):
    """Priorités des messages"""
    LOW = 1
    NORMAL = 3
    HIGH = 5
    CRITICAL = 10

class MessageStatus(Enum):
    """États des messages"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"

@dataclass
class QueueMessage:
    """Structure d'un message de queue"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    queue_name: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: float = 1.0
    status: MessageStatus = MessageStatus.PENDING
    error_message: Optional[str] = None
    processed_by: Optional[str] = None
    processed_at: Optional[datetime] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire sérializable"""
        data = asdict(self)
        # Convertir les dates en ISO format
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif key == 'priority':
                data[key] = value.value
            elif key == 'status':
                data[key] = value.value
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueueMessage':
        """Crée un message depuis un dictionnaire"""
        # Convertir les dates depuis ISO format
        for date_field in ['created_at', 'scheduled_at', 'expires_at', 'processed_at']:
            if data.get(date_field):
                data[date_field] = datetime.fromisoformat(data[date_field])
                
        # Convertir les enums
        if 'priority' in data:
            data['priority'] = MessagePriority(data['priority'])
        if 'status' in data:
            data['status'] = MessageStatus(data['status'])
            
        return cls(**data)

@dataclass
class QueueStats:
    """Statistiques d'une queue"""
    total_messages: int = 0
    pending_messages: int = 0
    processing_messages: int = 0
    completed_messages: int = 0
    failed_messages: int = 0
    dead_letter_messages: int = 0
    average_processing_time: float = 0.0
    throughput_per_minute: float = 0.0
    last_message_time: Optional[datetime] = None

class MessageQueue:
    """File d'attente de messages avec Redis Streams"""
    
    def __init__(self, 
                 redis_client: aioredis.Redis,
                 queue_name: str,
                 max_length: int = 10000,
                 dead_letter_queue: bool = True):
        self.redis_client = redis_client
        self.queue_name = queue_name
        self.max_length = max_length
        self.dead_letter_queue = dead_letter_queue
        self.dlq_name = f"{queue_name}:dlq"
        self.stats_key = f"{queue_name}:stats"
        self.processing_key = f"{queue_name}:processing"
        
        # Métriques
        self.stats = QueueStats()
        self._last_stats_update = datetime.utcnow()
        
    async def put(self, 
                  data: Dict[str, Any],
                  priority: MessagePriority = MessagePriority.NORMAL,
                  delay: Optional[float] = None,
                  expires_in: Optional[float] = None,
                  correlation_id: Optional[str] = None,
                  reply_to: Optional[str] = None,
                  headers: Optional[Dict[str, str]] = None) -> str:
        """Ajoute un message à la queue"""
        
        message = QueueMessage(
            queue_name=self.queue_name,
            data=data,
            priority=priority,
            correlation_id=correlation_id,
            reply_to=reply_to,
            headers=headers or {}
        )
        
        # Gestion du délai
        if delay:
            message.scheduled_at = datetime.utcnow() + timedelta(seconds=delay)
            
        # Gestion de l'expiration
        if expires_in:
            message.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
        # Sérialiser le message
        message_data = json.dumps(message.to_dict())
        
        # Ajouter à Redis Stream avec priorité
        stream_key = f"{self.queue_name}:p{priority.value}"
        
        await self.redis_client.xadd(
            stream_key,
            fields={"message": message_data},
            maxlen=self.max_length,
            approximate=True
        )
        
        # Mettre à jour les statistiques
        await self._update_stats("put", message)
        
        logger.debug(f"Message ajouté à {self.queue_name}: {message.message_id}")
        return message.message_id
        
    async def get(self, 
                  timeout: Optional[float] = None,
                  consumer_name: Optional[str] = None) -> Optional[QueueMessage]:
        """Récupère un message de la queue (par priorité)"""
        
        consumer_name = consumer_name or f"consumer-{uuid.uuid4().hex[:8]}"
        group_name = f"{self.queue_name}:group"
        
        # Essayer de créer le consumer group
        try:
            for priority in sorted(MessagePriority, key=lambda x: x.value, reverse=True):
                stream_key = f"{self.queue_name}:p{priority.value}"
                try:
                    await self.redis_client.xgroup_create(
                        stream_key, group_name, id="0", mkstream=True
                    )
                except Exception:
                    pass  # Le groupe existe déjà
                    
        except Exception as e:
            logger.debug(f"Consumer group setup: {e}")
            
        # Lire les messages par ordre de priorité
        streams = {}
        for priority in sorted(MessagePriority, key=lambda x: x.value, reverse=True):
            stream_key = f"{self.queue_name}:p{priority.value}"
            streams[stream_key] = ">"
            
        try:
            # Traiter d'abord les messages en attente
            pending_result = await self.redis_client.xreadgroup(
                group_name,
                consumer_name,
                streams=streams,
                count=1,
                block=0
            )
            
            if not pending_result:
                # Lire de nouveaux messages
                block_time = int(timeout * 1000) if timeout else 0
                result = await self.redis_client.xreadgroup(
                    group_name,
                    consumer_name,
                    streams=streams,
                    count=1,
                    block=block_time
                )
            else:
                result = pending_result
                
            if result:
                stream_key, messages = result[0]
                if messages:
                    message_id, fields = messages[0]
                    message_data = json.loads(fields[b"message"])
                    message = QueueMessage.from_dict(message_data)
                    
                    # Vérifier l'expiration
                    if message.expires_at and datetime.utcnow() > message.expires_at:
                        await self._ack_message(stream_key, group_name, message_id)
                        logger.debug(f"Message expiré ignoré: {message.message_id}")
                        return await self.get(timeout, consumer_name)
                        
                    # Vérifier la planification
                    if message.scheduled_at and datetime.utcnow() < message.scheduled_at:
                        # Remettre en queue pour plus tard
                        await self._reschedule_message(message)
                        await self._ack_message(stream_key, group_name, message_id)
                        return await self.get(timeout, consumer_name)
                        
                    # Marquer comme en traitement
                    message.status = MessageStatus.PROCESSING
                    message.processed_by = consumer_name
                    message.processed_at = datetime.utcnow()
                    
                    # Stocker dans la liste de traitement
                    processing_data = {
                        "message": json.dumps(message.to_dict()),
                        "stream_key": stream_key,
                        "message_id": message_id,
                        "started_at": datetime.utcnow().isoformat()
                    }
                    
                    await self.redis_client.hset(
                        self.processing_key,
                        message.message_id,
                        json.dumps(processing_data)
                    )
                    
                    await self._update_stats("get", message)
                    return message
                    
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de queue {self.queue_name}: {e}")
            
        return None
        
    async def ack(self, message: QueueMessage, success: bool = True, error: Optional[str] = None):
        """Accuse réception d'un message traité"""
        
        # Récupérer les infos de traitement
        processing_data_raw = await self.redis_client.hget(
            self.processing_key, message.message_id
        )
        
        if not processing_data_raw:
            logger.warning(f"Message de traitement non trouvé: {message.message_id}")
            return
            
        processing_data = json.loads(processing_data_raw)
        stream_key = processing_data["stream_key"]
        redis_message_id = processing_data["message_id"]
        group_name = f"{self.queue_name}:group"
        
        if success:
            message.status = MessageStatus.COMPLETED
            # Acknowledger dans Redis
            await self._ack_message(stream_key, group_name, redis_message_id)
            
        else:
            message.status = MessageStatus.FAILED
            message.error_message = error
            message.retry_count += 1
            
            if message.retry_count <= message.max_retries:
                # Programmer un retry
                message.status = MessageStatus.RETRYING
                retry_delay = message.retry_delay * (2 ** (message.retry_count - 1))
                message.scheduled_at = datetime.utcnow() + timedelta(seconds=retry_delay)
                
                await self.put(
                    data=message.data,
                    priority=message.priority,
                    delay=retry_delay,
                    correlation_id=message.correlation_id,
                    reply_to=message.reply_to,
                    headers=message.headers
                )
                
                await self._ack_message(stream_key, group_name, redis_message_id)
                logger.info(f"Message programmé pour retry {message.retry_count}: {message.message_id}")
                
            else:
                # Envoyer en Dead Letter Queue
                if self.dead_letter_queue:
                    message.status = MessageStatus.DEAD_LETTER
                    await self._send_to_dlq(message)
                    
                await self._ack_message(stream_key, group_name, redis_message_id)
                logger.warning(f"Message envoyé en DLQ après {message.retry_count} échecs: {message.message_id}")
                
        # Nettoyer le traitement
        await self.redis_client.hdel(self.processing_key, message.message_id)
        await self._update_stats("ack", message)
        
    async def _ack_message(self, stream_key: str, group_name: str, message_id: str):
        """Acknowledge un message dans Redis Stream"""
        try:
            await self.redis_client.xack(stream_key, group_name, message_id)
        except Exception as e:
            logger.error(f"Erreur lors de l'ack du message {message_id}: {e}")
            
    async def _send_to_dlq(self, message: QueueMessage):
        """Envoie un message vers la Dead Letter Queue"""
        dlq_data = message.to_dict()
        dlq_data["original_queue"] = self.queue_name
        dlq_data["dlq_timestamp"] = datetime.utcnow().isoformat()
        
        await self.redis_client.xadd(
            self.dlq_name,
            fields={"message": json.dumps(dlq_data)},
            maxlen=1000,  # Limiter la taille de la DLQ
            approximate=True
        )
        
    async def _reschedule_message(self, message: QueueMessage):
        """Replanifie un message pour plus tard"""
        delay_seconds = (message.scheduled_at - datetime.utcnow()).total_seconds()
        if delay_seconds > 0:
            await self.put(
                data=message.data,
                priority=message.priority,
                delay=delay_seconds,
                correlation_id=message.correlation_id,
                reply_to=message.reply_to,
                headers=message.headers
            )
            
    async def _update_stats(self, operation: str, message: QueueMessage):
        """Met à jour les statistiques de la queue"""
        now = datetime.utcnow()
        
        if operation == "put":
            self.stats.total_messages += 1
            self.stats.pending_messages += 1
            
        elif operation == "get":
            self.stats.pending_messages = max(0, self.stats.pending_messages - 1)
            self.stats.processing_messages += 1
            
        elif operation == "ack":
            self.stats.processing_messages = max(0, self.stats.processing_messages - 1)
            
            if message.status == MessageStatus.COMPLETED:
                self.stats.completed_messages += 1
                
                # Calculer le temps de traitement
                if message.processed_at:
                    processing_time = (now - message.processed_at).total_seconds()
                    self.stats.average_processing_time = (
                        (self.stats.average_processing_time * (self.stats.completed_messages - 1) + processing_time)
                        / self.stats.completed_messages
                    )
                    
            elif message.status in [MessageStatus.FAILED, MessageStatus.DEAD_LETTER]:
                if message.status == MessageStatus.DEAD_LETTER:
                    self.stats.dead_letter_messages += 1
                else:
                    self.stats.failed_messages += 1
                    
        self.stats.last_message_time = now
        
        # Calculer le throughput
        time_diff = (now - self._last_stats_update).total_seconds()
        if time_diff >= 60:  # Mettre à jour chaque minute
            await self._persist_stats()
            self._last_stats_update = now
            
    async def _persist_stats(self):
        """Persiste les statistiques dans Redis"""
        stats_data = asdict(self.stats)
        # Convertir les dates
        for key, value in stats_data.items():
            if isinstance(value, datetime):
                stats_data[key] = value.isoformat()
                
        await self.redis_client.set(
            self.stats_key,
            json.dumps(stats_data),
            ex=3600  # TTL 1 heure
        )
        
    async def get_queue_info(self) -> Dict[str, Any]:
        """Retourne les informations détaillées de la queue"""
        info = {
            "queue_name": self.queue_name,
            "stats": asdict(self.stats),
            "streams": {}
        }
        
        # Informations sur les streams par priorité
        for priority in MessagePriority:
            stream_key = f"{self.queue_name}:p{priority.value}"
            try:
                stream_info = await self.redis_client.xinfo_stream(stream_key)
                info["streams"][priority.name] = {
                    "length": stream_info.get("length", 0),
                    "first_entry": stream_info.get("first-entry"),
                    "last_entry": stream_info.get("last-entry")
                }
            except Exception:
                info["streams"][priority.name] = {"length": 0}
                
        return info
        
    async def purge(self, priority: Optional[MessagePriority] = None):
        """Vide la queue (optionnellement par priorité)"""
        if priority:
            stream_key = f"{self.queue_name}:p{priority.value}"
            await self.redis_client.delete(stream_key)
        else:
            # Vider toutes les priorités
            for p in MessagePriority:
                stream_key = f"{self.queue_name}:p{p.value}"
                await self.redis_client.delete(stream_key)
                
        # Reset des stats
        self.stats = QueueStats()
        await self._persist_stats()
        
        logger.info(f"Queue {self.queue_name} vidée")

class QueueManager:
    """Gestionnaire de multiples queues avec load balancing"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client
        self.queues: Dict[str, MessageQueue] = {}
        self.consumers: Dict[str, asyncio.Task] = {}
        self.handlers: Dict[str, Callable] = {}
        self._running = False
        
    async def create_queue(self, 
                          queue_name: str,
                          max_length: int = 10000,
                          dead_letter_queue: bool = True) -> MessageQueue:
        """Crée une nouvelle queue"""
        if queue_name in self.queues:
            return self.queues[queue_name]
            
        queue = MessageQueue(
            self.redis_client,
            queue_name,
            max_length,
            dead_letter_queue
        )
        
        self.queues[queue_name] = queue
        logger.info(f"Queue créée: {queue_name}")
        return queue
        
    async def register_handler(self, queue_name: str, handler: Callable):
        """Enregistre un handler pour une queue"""
        self.handlers[queue_name] = handler
        
        # Démarrer un consumer si pas déjà fait
        if queue_name not in self.consumers and self._running:
            await self._start_consumer(queue_name)
            
    async def start(self):
        """Démarre le gestionnaire de queues"""
        self._running = True
        
        # Démarrer les consumers pour les handlers enregistrés
        for queue_name in self.handlers:
            await self._start_consumer(queue_name)
            
        logger.info("QueueManager démarré")
        
    async def stop(self):
        """Arrête le gestionnaire de queues"""
        self._running = False
        
        # Arrêter tous les consumers
        for queue_name, task in self.consumers.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
        self.consumers.clear()
        logger.info("QueueManager arrêté")
        
    async def _start_consumer(self, queue_name: str):
        """Démarre un consumer pour une queue"""
        if queue_name in self.consumers:
            return
            
        task = asyncio.create_task(self._consumer_loop(queue_name))
        self.consumers[queue_name] = task
        logger.info(f"Consumer démarré pour {queue_name}")
        
    async def _consumer_loop(self, queue_name: str):
        """Boucle principale du consumer"""
        queue = self.queues.get(queue_name)
        handler = self.handlers.get(queue_name)
        
        if not queue or not handler:
            logger.error(f"Queue ou handler manquant pour {queue_name}")
            return
            
        consumer_name = f"consumer-{queue_name}-{uuid.uuid4().hex[:8]}"
        
        while self._running:
            try:
                message = await queue.get(timeout=5.0, consumer_name=consumer_name)
                if message:
                    try:
                        # Exécuter le handler
                        if asyncio.iscoroutinefunction(handler):
                            result = await handler(message.data)
                        else:
                            result = handler(message.data)
                            
                        await queue.ack(message, success=True)
                        
                    except Exception as e:
                        logger.error(f"Erreur dans le handler {queue_name}: {e}")
                        await queue.ack(message, success=False, error=str(e))
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur dans le consumer {queue_name}: {e}")
                await asyncio.sleep(1)
                
        logger.info(f"Consumer arrêté pour {queue_name}")
        
    async def send_message(self, 
                          queue_name: str,
                          data: Dict[str, Any],
                          **kwargs) -> str:
        """Envoie un message vers une queue"""
        queue = self.queues.get(queue_name)
        if not queue:
            raise ValueError(f"Queue non trouvée: {queue_name}")
            
        return await queue.put(data, **kwargs)
        
    async def get_global_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques globales"""
        total_stats = {
            "total_queues": len(self.queues),
            "active_consumers": len(self.consumers),
            "queue_details": {}
        }
        
        for queue_name, queue in self.queues.items():
            total_stats["queue_details"][queue_name] = await queue.get_queue_info()
            
        return total_stats