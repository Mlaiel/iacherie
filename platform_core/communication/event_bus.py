"""🚀 Event Bus System - IA Influencer Agent Platform Enterprise
===========================================================
Module: backend/platform_core/communication/event_bus.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 BUS D'ÉVÉNEMENTS DISTRIBUÉ
Système de communication événementielle enterprise
- Publish/Subscribe pattern avec persistence
- Event sourcing et replay automatique
- Dead letter handling et retry intelligent
- Monitoring temps réel et analytics avancées
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import weakref
import inspect

import redis.asyncio as aioredis

# Configuration
logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """
Priorités des événements"""

    LOW = 1
    NORMAL = 3
    HIGH = 5
    CRITICAL = 10

class EventStatus(Enum):
    """États des événements"""

    PENDING = "pending"
    PUBLISHED = "published"
    DELIVERED = "delivered"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"

@dataclass
class Event:
    """Événement du système"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    source: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None  # Event qui a causé celui-ci
    aggregate_id: Optional[str] = None
    aggregate_version: int = 1
    status: EventStatus = EventStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'événement en dictionnaire"""
        data = asdict(self)
        # Convertir les dates et enums
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, Enum):
                data[key] = value.value
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """
Crée un événement depuis un dictionnaire"""
        # Convertir les dates
        for date_field in ['created_at', 'scheduled_at', 'expires_at']:
            if data.get(date_field):
                data[date_field] = datetime.fromisoformat(data[date_field])
                
        # Convertir les enums
        if 'priority' in data:
            data['priority'] = EventPriority(data['priority'])
        if 'status' in data:
            data['status'] = EventStatus(data['status'])
            
        return cls(**data)

@dataclass
class EventSubscription:
    """
Abonnement à des événements"""
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subscriber_id: str = ""
    event_patterns: List[str] = field(default_factory=list)  # Patterns d'événements
    handler: Optional[Callable] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    active: bool = True
    
    def matches_event(self, event: Event) -> bool:
        """Vérifie si l'événement correspond à l'abonnement"""
        if not self.active:
            return False
            
        # Vérifier les patterns
        if self.event_patterns:
            matches_pattern = any(
                self._matches_pattern(pattern, event.event_type)
                for pattern in self.event_patterns
            )
            if not matches_pattern:
                return False
                
        # Vérifier les filtres
        for filter_key, filter_value in self.filters.items():
            if filter_key == "source":
                if event.source != filter_value:
                    return False
            elif filter_key == "priority":
                if event.priority.value < filter_value:
                    return False
            elif filter_key in event.metadata:
                if event.metadata[filter_key] != filter_value:
                    return False
                    
        return True
        
    def _matches_pattern(self, pattern: str, event_type: str) -> bool:
        """Vérifie si un type d'événement correspond au pattern"""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return event_type.startswith(pattern[:-1])
        if pattern.startswith("*"):
            return event_type.endswith(pattern[1:])
        return pattern == event_type

class EventHandler:
    """Gestionnaire d'événements avec métadonnées"""
    
    def __init__(self, 
                 handler_func: Callable,
                 event_patterns: List[str],
                 filters: Optional[Dict[str, Any]] = None,
                 options: Optional[Dict[str, Any]] = None):
        self.handler_func = handler_func
        self.event_patterns = event_patterns
        self.filters = filters or {}
        self.options = options or {}
        self.handler_id = str(uuid.uuid4())
        
        # Analyser la signature de la fonction
        self.signature = inspect.signature(handler_func)
        self.is_async = asyncio.iscoroutinefunction(handler_func)
        
    async def handle(self, event: Event) -> bool:
        """
Exécute le handler pour un événement"""
        try:
            if self.is_async:
                result = await self.handler_func(event)
            else:
                result = self.handler_func(event)
                
            return result is not False  # None ou True = succès
            
        except Exception as e:
            logger.error(f"Erreur dans handler {self.handler_id}: {e}")
            return False

class EventBus:
    """Bus d'événements distribué"""
    
    def __init__(self, 
                 redis_client: aioredis.Redis,
                 namespace: str = "events"):
        self.redis_client = redis_client
        self.namespace = namespace
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.handlers: Dict[str, EventHandler] = {}
        
        # Clés Redis
        self.events_stream = f"{namespace}:events"
        self.dead_letter_stream = f"{namespace}:dlq"
        self.subscriptions_key = f"{namespace}:subscriptions"
        
        # Contrôle
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        self._consumer_group = f"{namespace}:processors"
        self._consumer_name = f"processor-{uuid.uuid4().hex[:8]}"
        
        # Métriques
        self.events_published = 0
        self.events_processed = 0
        self.events_failed = 0
        self.start_time = datetime.utcnow()
        
    async def start(self):
        """Démarre le bus d'événements avec support enterprise"""
        try:
            logger.info("Starting Enterprise Event Bus...")
            
            if self._running:
                logger.warning("Event Bus already running")
                return
            
            # Initialize Redis consumer group
            try:
                await self.redis_client.xgroup_create(
                    self.events_stream,
                    self._consumer_group,
                    id="0",
                    mkstream=True
                )
                logger.info(f"Created consumer group: {self._consumer_group}")
            except Exception as e:
                if "BUSYGROUP" not in str(e):
                    logger.error(f"Failed to create consumer group: {e}")
                    raise
                else:
                    logger.info(f"Consumer group already exists: {self._consumer_group}")
            
            # Initialize dead letter queue consumer group
            try:
                await self.redis_client.xgroup_create(
                    self.dead_letter_stream,
                    f"{self._consumer_group}:dlq",
                    id="0",
                    mkstream=True
                )
            except Exception as e:
                if "BUSYGROUP" not in str(e):
                    logger.warning(f"Dead letter queue group creation failed: {e}")
            
            # Start event processing
            self._running = True
            self._processor_task = asyncio.create_task(self._process_events())
            
            # Start scheduled events processor
            self._scheduler_task = asyncio.create_task(self._process_scheduled_events())
            
            # Start dead letter queue processor
            self._dlq_task = asyncio.create_task(self._process_dead_letter_queue())
            
            # Start metrics collection
            self._metrics_task = asyncio.create_task(self._collect_metrics())
            
            # Reset start time for metrics
            self.start_time = datetime.utcnow()
            
            logger.info("✅ Enterprise Event Bus started successfully")
            logger.info(f"  - Consumer Group: {self._consumer_group}")
            logger.info(f"  - Consumer Name: {self._consumer_name}")
            logger.info(f"  - Stream: {self.events_stream}")
            logger.info(f"  - Dead Letter Queue: {self.dead_letter_stream}")
            
            # Health check
            await self._perform_startup_health_check()
            
        except Exception as e:
            logger.error(f"❌ Failed to start Event Bus: {e}")
            self._running = False
            raise
    
    async def stop(self):
        """Arrête le bus d'événements avec nettoyage graceful"""
        try:
            logger.info("Stopping Enterprise Event Bus...")
            
            if not self._running:
                logger.warning("Event Bus not running")
                return
            
            self._running = False
            
            # Cancel all background tasks gracefully
            tasks_to_cancel = []
            
            if self._processor_task and not self._processor_task.done():
                tasks_to_cancel.append(self._processor_task)
            
            if hasattr(self, '_scheduler_task') and self._scheduler_task and not self._scheduler_task.done():
                tasks_to_cancel.append(self._scheduler_task)
            
            if hasattr(self, '_dlq_task') and self._dlq_task and not self._dlq_task.done():
                tasks_to_cancel.append(self._dlq_task)
            
            if hasattr(self, '_metrics_task') and self._metrics_task and not self._metrics_task.done():
                tasks_to_cancel.append(self._metrics_task)
            
            # Cancel tasks
            for task in tasks_to_cancel:
                task.cancel()
            
            # Wait for tasks to complete with timeout
            if tasks_to_cancel:
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*tasks_to_cancel, return_exceptions=True),
                        timeout=10.0
                    )
                except asyncio.TimeoutError:
                    logger.warning("Some tasks did not complete within timeout")
            
            # Clear subscriptions and handlers
            subscription_count = len(self.subscriptions)
            handler_count = len(self.handlers)
            
            self.subscriptions.clear()
            self.handlers.clear()
            
            # Log final metrics
            uptime = datetime.utcnow() - self.start_time
            logger.info("📊 Event Bus Final Metrics:")
            logger.info(f"  - Uptime: {uptime}")
            logger.info(f"  - Events Published: {self.events_published}")
            logger.info(f"  - Events Processed: {self.events_processed}")
            logger.info(f"  - Events Failed: {self.events_failed}")
            logger.info(f"  - Subscriptions Cleared: {subscription_count}")
            logger.info(f"  - Handlers Cleared: {handler_count}")
            
            # Calculate success rate
            if self.events_processed > 0:
                success_rate = ((self.events_processed - self.events_failed) / self.events_processed) * 100
                logger.info(f"  - Success Rate: {success_rate:.2f}%")
            
            logger.info("✅ Enterprise Event Bus stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping Event Bus: {e}")
            raise
    
    async def _perform_startup_health_check(self):
        """Perform health check after startup"""
        try:
            # Test Redis connection
            await self.redis_client.ping()
            
            # Test stream operations
            test_event_id = await self.publish(
                event_type="system.health_check",
                source="event_bus.startup",
                data={"timestamp": datetime.utcnow().isoformat()},
                metadata={"health_check": True}
            )
            
            logger.info(f"✅ Health check passed - Test event: {test_event_id}")
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            raise
    
    async def _process_scheduled_events(self):
        """Process scheduled events that are ready"""
        logger.info("Started scheduled events processor")
        
        while self._running:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                # Get all scheduled events (in production, this would be a separate sorted set)
                # For now, we'll simulate scheduled event processing
                current_time = datetime.utcnow()
                
                # Process any scheduled events that are due
                # This is a simplified implementation
                logger.debug("Checking for scheduled events...")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduled events processor: {e}")
                await asyncio.sleep(5)
        
        logger.info("Scheduled events processor stopped")
    
    async def _process_dead_letter_queue(self):
        """Process dead letter queue for retry logic"""
        logger.info("Started dead letter queue processor")
        
        while self._running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Check for messages in dead letter queue that can be retried
                try:
                    result = await self.redis_client.xreadgroup(
                        f"{self._consumer_group}:dlq",
                        f"{self._consumer_name}:dlq",
                        streams={self.dead_letter_stream: ">"},
                        count=5,
                        block=1000
                    )
                    
                    if result:
                        for stream_name, messages in result:
                            for message_id, fields in messages:
                                await self._process_dead_letter_message(
                                    stream_name.decode(),
                                    message_id.decode(),
                                    fields
                                )
                                
                except Exception as e:
                    if "NOGROUP" in str(e):
                        # Consumer group doesn't exist yet, skip
                        continue
                    else:
                        logger.error(f"Error reading dead letter queue: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in dead letter queue processor: {e}")
                await asyncio.sleep(30)
        
        logger.info("Dead letter queue processor stopped")
    
    async def _collect_metrics(self):
        """Collect and log metrics periodically"""
        logger.info("Started metrics collector")
        
        while self._running:
            try:
                await asyncio.sleep(60)  # Collect metrics every minute
                
                uptime = datetime.utcnow() - self.start_time
                
                metrics = {
                    "uptime_seconds": uptime.total_seconds(),
                    "events_published": self.events_published,
                    "events_processed": self.events_processed,
                    "events_failed": self.events_failed,
                    "active_subscriptions": len(self.subscriptions),
                    "active_handlers": len(self.handlers)
                }
                
                # Calculate rates
                if uptime.total_seconds() > 0:
                    metrics["events_per_second"] = self.events_processed / uptime.total_seconds()
                    metrics["publish_rate"] = self.events_published / uptime.total_seconds()
                    
                if self.events_processed > 0:
                    metrics["success_rate"] = ((self.events_processed - self.events_failed) / self.events_processed) * 100
                
                logger.debug(f"Event Bus Metrics: {metrics}")
                
                # Store metrics in Redis for monitoring
                await self.redis_client.hset(
                    f"{self.namespace}:metrics",
                    mapping={k: str(v) for k, v in metrics.items()}
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(60)
        
        logger.info("Metrics collector stopped")
    
    async def _process_dead_letter_message(self, stream_name: str, message_id: str, fields: Dict):
        """Process a message from dead letter queue"""
        try:
            # Simplified dead letter processing
            logger.debug(f"Processing dead letter message: {message_id}")
            
            # In production, this would implement retry logic based on:
            # - Message age
            # - Retry count
            # - Error type
            # - Business rules
            
            # For now, just acknowledge the message
            await self.redis_client.xack(stream_name, f"{self._consumer_group}:dlq", message_id)
            
        except Exception as e:
            logger.error(f"Error processing dead letter message {message_id}: {e}")
    
    async def publish(self,
                     event_type: str,
                     source: str,
                     data: Dict[str, Any],
        
        event = Event(
            event_type=event_type,
            source=source,
            data=data,
            metadata=metadata or {},
            priority=priority,
            correlation_id=correlation_id,
            aggregate_id=aggregate_id
        )
        
        # Gestion du délai
        if delay:
            event.scheduled_at = datetime.utcnow() + timedelta(seconds=delay)
            
        # Gestion de l'expiration
        if expires_in:
            event.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
        # Publier dans Redis Stream
        event_data = json.dumps(event.to_dict())
        
        await self.redis_client.xadd(
            self.events_stream,
            fields={"event": event_data},
            maxlen=100000,  # Limite de rétention
            approximate=True
        )
        
        event.status = EventStatus.PUBLISHED
        self.events_published += 1
        
        logger.debug(f"Événement publié: {event_type} ({event.event_id})")
        return event.event_id
        
    async def subscribe(self, 
                       event_patterns: List[str],
                       handler: Callable,
                       subscriber_id: Optional[str] = None,
                       filters: Optional[Dict[str, Any]] = None,
                       options: Optional[Dict[str, Any]] = None) -> str:
        """S'abonne à des événements"""
        
        subscriber_id = subscriber_id or f"subscriber-{uuid.uuid4().hex[:8]}"
        
        subscription = EventSubscription(
            subscriber_id=subscriber_id,
            event_patterns=event_patterns,
            handler=handler,
            filters=filters or {},
            options=options or {}
        )
        
        # Créer le handler
        event_handler = EventHandler(
            handler_func=handler,
            event_patterns=event_patterns,
            filters=filters,
            options=options
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        self.handlers[subscription.subscription_id] = event_handler
        
        logger.info(f"Abonnement créé: {event_patterns} ({subscription.subscription_id})")
        return subscription.subscription_id
        
    async def unsubscribe(self, subscription_id: str):
        """Se désabonne d'événements"""
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
        if subscription_id in self.handlers:
            del self.handlers[subscription_id]
            
        logger.info(f"Désabonnement: {subscription_id}")
        
    async def _process_events(self):
        """Boucle de traitement des événements"""
        while self._running:
            try:
                # Lire les événements du stream
                result = await self.redis_client.xreadgroup(
                    self._consumer_group,
                    self._consumer_name,
                    streams={self.events_stream: ">"},
                    count=10,
                    block=1000  # 1 seconde
                )
                
                if result:
                    for stream_name, messages in result:
                        for message_id, fields in messages:
                            await self._process_event_message(
                                stream_name.decode(), 
                                message_id.decode(), 
                                fields
                            )
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur dans le processeur d'événements: {e}")
                await asyncio.sleep(1)
                
    async def _process_event_message(self, stream_name: str, message_id: str, fields: Dict):
        """Traite un message d'événement"""
        try:
            event_data = json.loads(fields[b"event"])
            event = Event.from_dict(event_data)
            
            # Vérifier l'expiration
            if event.expires_at and datetime.utcnow() > event.expires_at:
                await self._ack_message(message_id)
                logger.debug(f"Événement expiré ignoré: {event.event_id}")
                return
                
            # Vérifier la planification
            if event.scheduled_at and datetime.utcnow() < event.scheduled_at:
                # Republier pour plus tard
                delay = (event.scheduled_at - datetime.utcnow()).total_seconds()
                await self.publish(
                    event_type=event.event_type,
                    data=event.data,
                    source=event.source,
                    priority=event.priority,
                    metadata=event.metadata,
                    correlation_id=event.correlation_id,
                    aggregate_id=event.aggregate_id,
                    delay=delay
                )
                await self._ack_message(message_id)
                return
                
            # Distribuer aux abonnés
            delivered = await self._distribute_event(event)
            
            if delivered:
                event.status = EventStatus.DELIVERED
                self.events_processed += 1
            else:
                event.status = EventStatus.FAILED
                self.events_failed += 1
                
                # Gérer les retries
                if event.retry_count < event.max_retries:
                    event.retry_count += 1
                    retry_delay = 2 ** event.retry_count  # Backoff exponentiel
                    
                    await self.publish(
                        event_type=event.event_type,
                        data=event.data,
                        source=event.source,
                        priority=event.priority,
                        metadata=event.metadata,
                        correlation_id=event.correlation_id,
                        aggregate_id=event.aggregate_id,
                        delay=retry_delay
                    )
                else:
                    # Envoyer en Dead Letter Queue
                    await self._send_to_dlq(event)
                    
            await self._ack_message(message_id)
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'événement {message_id}: {e}")
            
    async def _distribute_event(self, event: Event) -> bool:
        """Distribue un événement aux abonnés correspondants"""
        delivered = False
        
        for subscription_id, subscription in self.subscriptions.items():
            if subscription.matches_event(event):
                handler = self.handlers.get(subscription_id)
                if handler:
                    try:
                        success = await handler.handle(event)
                        if success:
                            delivered = True
                        else:
                            logger.warning(f"Handler {subscription_id} a échoué pour {event.event_id}")
                    except Exception as e:
                        logger.error(f"Erreur dans handler {subscription_id}: {e}")
                        
        return delivered
        
    async def _ack_message(self, message_id: str):
        """Acknowledge un message traité"""
        try:
            await self.redis_client.xack(
                self.events_stream, 
                self._consumer_group, 
                message_id
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'ack du message {message_id}: {e}")
            
    async def _send_to_dlq(self, event: Event):
        """Envoie un événement en Dead Letter Queue"""
        event.status = EventStatus.DEAD_LETTER
        dlq_data = event.to_dict()
        dlq_data["dlq_timestamp"] = datetime.utcnow().isoformat()
        
        await self.redis_client.xadd(
            self.dead_letter_stream,
            fields={"event": json.dumps(dlq_data)},
            maxlen=10000,
            approximate=True
        )
        
        logger.warning(f"Événement envoyé en DLQ: {event.event_id}")
        
    async def replay_events(self, 
                           from_timestamp: datetime,
                           to_timestamp: Optional[datetime] = None,
                           event_types: Optional[List[str]] = None,
                           aggregate_id: Optional[str] = None) -> int:
        """Rejoue des événements depuis l'historique"""
        replayed = 0
        
        # Convertir les timestamps en IDs Redis
        from_id = str(int(from_timestamp.timestamp() * 1000)) + "-0"
        to_id = "+" if not to_timestamp else str(int(to_timestamp.timestamp() * 1000)) + "-0"
        
        try:
            # Lire les événements dans la plage
            result = await self.redis_client.xrange(
                self.events_stream,
                min=from_id,
                max=to_id
            )
            
            for message_id, fields in result:
                try:
                    event_data = json.loads(fields[b"event"])
                    event = Event.from_dict(event_data)
                    
                    # Filtrer par type d'événement
                    if event_types and event.event_type not in event_types:
                        continue
                        
                    # Filtrer par aggregate
                    if aggregate_id and event.aggregate_id != aggregate_id:
                        continue
                        
                    # Republier l'événement
                    await self.publish(
                        event_type=event.event_type,
                        data=event.data,
                        source=f"replay:{event.source}",
                        priority=event.priority,
                        metadata={**event.metadata, "replayed": True},
                        correlation_id=event.correlation_id,
                        aggregate_id=event.aggregate_id
                    )
                    
                    replayed += 1
                    
                except Exception as e:
                    logger.error(f"Erreur lors du replay de l'événement {message_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Erreur lors du replay d'événements: {e}")
            
        logger.info(f"Replay terminé: {replayed} événements rejoués")
        return replayed
        
    async def get_event_history(self, 
                               aggregate_id: str,
                               from_version: int = 1) -> List[Event]:
        """Récupère l'historique d'événements pour un agrégat"""
        events = []
        
        try:
            # Lire tous les événements du stream
            result = await self.redis_client.xrange(self.events_stream)
            
            for message_id, fields in result:
                try:
                    event_data = json.loads(fields[b"event"])
                    event = Event.from_dict(event_data)
                    
                    if (event.aggregate_id == aggregate_id and 
                        event.aggregate_version >= from_version):
                        events.append(event)
                        
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture de l'événement {message_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique: {e}")
            
        # Trier par version
        events.sort(key=lambda e: e.aggregate_version)
        return events
        
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du bus d'événements"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "namespace": self.namespace,
            "running": self._running,
            "subscriptions": len(self.subscriptions),
            "events_published": self.events_published,
            "events_processed": self.events_processed,
            "events_failed": self.events_failed,
            "success_rate": self.events_processed / max(self.events_published, 1),
            "events_per_second": self.events_processed / max(uptime, 1),
            "uptime_seconds": uptime,
            "subscription_details": {
                sub_id: {
                    "subscriber_id": sub.subscriber_id,
                    "event_patterns": sub.event_patterns,
                    "active": sub.active,
                    "created_at": sub.created_at.isoformat()
                }
                for sub_id, sub in self.subscriptions.items()
            }
        }