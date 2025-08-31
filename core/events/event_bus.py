"""IA-Influencer-Agent - Event Bus System
Module: backend/core/events/event_bus.py
Architecture: Core Event Bus for Real-time Event Distribution
Auteur: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.

Description:
    Bus central d'événements pour la distribution temps réel des événements
    dans la plateforme IA-Influencer-Agent. Support pub/sub pattern avec 
    persistance et routage intelligent.
"""
from typing import Any, Dict, List, Optional, Union, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import asyncio
import uuid
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Priorité des événements pour le routage"""
    LOW = "low"
    NORMAL = "normal"  
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(Enum):
    """Statut de traitement des événements"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Event:
    """
    Événement système pour la plateforme IA-Influencer-Agent
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    source: str = ""
    subject: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    priority: EventPriority = EventPriority.NORMAL
    status: EventStatus = EventStatus.PENDING
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    version: int = 1
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'événement en dictionnaire"""
        return {
            "id": self.id,
            "type": self.type,
            "source": self.source,
            "subject": self.subject,
            "data": self.data,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "status": self.status.value,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "version": self.version,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Crée un événement depuis un dictionnaire"""
        event = cls()
        event.id = data.get("id", str(uuid.uuid4()))
        event.type = data.get("type", "")
        event.source = data.get("source", "")
        event.subject = data.get("subject", "")
        event.data = data.get("data", {})
        event.metadata = data.get("metadata", {})
        event.timestamp = datetime.fromisoformat(data.get("timestamp", datetime.now(timezone.utc).isoformat()))
        event.priority = EventPriority(data.get("priority", "normal"))
        event.status = EventStatus(data.get("status", "pending"))
        event.user_id = data.get("user_id")
        event.tenant_id = data.get("tenant_id")
        event.correlation_id = data.get("correlation_id")
        event.causation_id = data.get("causation_id")
        event.version = data.get("version", 1)
        event.retry_count = data.get("retry_count", 0)
        event.max_retries = data.get("max_retries", 3)
        return event


class EventSubscription:
    """Abonnement à un type d'événement"""
    
    def __init__(
        self,
        subscription_id: str,
        event_type: str,
        handler: Callable[[Event], Any],
        filters: Optional[Dict[str, Any]] = None,
        priority: EventPriority = EventPriority.NORMAL
    ):
        self.subscription_id = subscription_id
        self.event_type = event_type
        self.handler = handler
        self.filters = filters or {}
        self.priority = priority
        self.created_at = datetime.now(timezone.utc)
        self.active = True
    
    def matches(self, event: Event) -> bool:
        """Vérifie si l'événement correspond aux filtres"""
        if not self.active:
            return False
            
        if self.event_type != "*" and not event.type.startswith(self.event_type):
            return False
            
        for key, value in self.filters.items():
            if key == "user_id" and event.user_id != value:
                return False
            elif key == "tenant_id" and event.tenant_id != value:
                return False
            elif key in event.metadata and event.metadata[key] != value:
                return False
                
        return True


class EventBus:
    """
    Bus central d'événements pour la plateforme IA-Influencer-Agent
    """
    
    def __init__(
        self,
        name: str = "main",
        max_workers: int = 10,
        enable_persistence: bool = True,
        enable_metrics: bool = True
    ):
        self.name = name
        self.max_workers = max_workers
        self.enable_persistence = enable_persistence
        self.enable_metrics = enable_metrics
        
        # Stockage interne
        self._subscriptions: Dict[str, List[EventSubscription]] = {}
        self._wildcard_subscriptions: List[EventSubscription] = []
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processing = False
        self._lock = threading.RLock()
        
        # Statistiques
        self._stats = {
            "events_published": 0,
            "events_processed": 0,
            "events_failed": 0,
            "subscriptions_count": 0
        }
        
        # Executor pour traitements asynchrones
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        
        logger.info("EventBus '%s' initialized with %d workers", name, max_workers)
    
    async def start(self):
        """Démarre le traitement des événements"""
        if self._processing:
            return
            
        self._processing = True
        asyncio.create_task(self._process_events())
        logger.info("EventBus '%s' started", self.name)
    
    async def stop(self):
        """Arrête le traitement des événements"""
        self._processing = False
        self._executor.shutdown(wait=True)
        logger.info("EventBus '%s' stopped", self.name)
    
    def subscribe(
        self,
        event_type: str,
        handler: Callable[[Event], Any],
        filters: Optional[Dict[str, Any]] = None,
        priority: EventPriority = EventPriority.NORMAL
    ) -> str:
        """
        S'abonne à un type d'événement
        
        Args:
            event_type: Type d'événement (ex: "content.uploaded", "*" pour tous)
            handler: Fonction de traitement
            filters: Filtres additionnels
            priority: Priorité de traitement
            
        Returns:
            ID de l'abonnement
        """
        subscription_id = str(uuid.uuid4())
        subscription = EventSubscription(
            subscription_id, event_type, handler, filters, priority
        )
        
        with self._lock:
            if event_type == "*":
                self._wildcard_subscriptions.append(subscription)
            else:
                if event_type not in self._subscriptions:
                    self._subscriptions[event_type] = []
                self._subscriptions[event_type].append(subscription)
            
            self._stats["subscriptions_count"] += 1
        
        logger.debug("Subscription created: %s for event type: %s", subscription_id, event_type)
        return subscription_id
    
    def unsubscribe(self, subscription_id: str):
        """Désabonne un handler"""
        with self._lock:
            # Recherche dans les abonnements typés
            for event_type, subscriptions in self._subscriptions.items():
                for i, sub in enumerate(subscriptions):
                    if sub.subscription_id == subscription_id:
                        subscriptions.pop(i)
                        self._stats["subscriptions_count"] -= 1
                        logger.debug("Subscription %s removed", subscription_id)
                        return
            
            # Recherche dans les abonnements wildcard
            for i, sub in enumerate(self._wildcard_subscriptions):
                if sub.subscription_id == subscription_id:
                    self._wildcard_subscriptions.pop(i)
                    self._stats["subscriptions_count"] -= 1
                    logger.debug("Wildcard subscription %s removed", subscription_id)
                    return
    
    async def publish(self, event: Event) -> bool:
        """
        Publie un événement
        
        Args:
            event: Événement à publier
            
        Returns:
            True si publié avec succès
        """
        try:
            # Validation de base
            if not event.type:
                raise ValueError("Event type is required")
            
            # Ajout à la queue
            await self._event_queue.put(event)
            self._stats["events_published"] += 1
            
            logger.debug("Event published: %s (type: %s)", event.id, event.type)
            return True
            
        except Exception as e:
            logger.error("Failed to publish event %s: %s", event.id, e)
            return False
    
    async def _process_events(self):
        """Traitement continu des événements"""
        while self._processing:
            try:
                # Récupération événement avec timeout
                event = await asyncio.wait_for(
                    self._event_queue.get(), timeout=1.0
                )
                
                # Traitement asynchrone
                asyncio.create_task(self._handle_event(event))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("Error in event processing loop: %s", e)
    
    async def _handle_event(self, event: Event):
        """Traite un événement individuel"""
        try:
            event.status = EventStatus.PROCESSING
            matching_subscriptions = self._get_matching_subscriptions(event)
            
            if not matching_subscriptions:
                logger.debug("No subscribers for event %s (type: %s)", event.id, event.type)
                event.status = EventStatus.COMPLETED
                return
            
            # Tri par priorité
            matching_subscriptions.sort(
                key=lambda s: list(EventPriority).index(s.priority)
            )
            
            # Exécution des handlers
            tasks = []
            for subscription in matching_subscriptions:
                task = asyncio.create_task(
                    self._execute_handler(event, subscription)
                )
                tasks.append(task)
            
            # Attente de tous les handlers
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Vérification des résultats
            failed_count = sum(1 for r in results if isinstance(r, Exception))
            
            if failed_count > 0:
                event.status = EventStatus.FAILED
                self._stats["events_failed"] += 1
                logger.warning("Event %s partially failed: %d/%d handlers failed", 
                             event.id, failed_count, len(results))
            else:
                event.status = EventStatus.COMPLETED
                self._stats["events_processed"] += 1
                logger.debug("Event %s processed successfully", event.id)
                
        except Exception as e:
            event.status = EventStatus.FAILED
            self._stats["events_failed"] += 1
            logger.error("Failed to handle event %s: %s", event.id, e)
    
    def _get_matching_subscriptions(self, event: Event) -> List[EventSubscription]:
        """Trouve les abonnements correspondant à un événement"""
        matching = []
        
        with self._lock:
            # Abonnements spécifiques
            for event_type, subscriptions in self._subscriptions.items():
                if event.type.startswith(event_type):
                    matching.extend([s for s in subscriptions if s.matches(event)])
            
            # Abonnements wildcard
            matching.extend([s for s in self._wildcard_subscriptions if s.matches(event)])
        
        return matching
    
    async def _execute_handler(self, event: Event, subscription: EventSubscription):
        """Exécute un handler d'événement"""
        try:
            # Exécution dans l'executor si handler synchrone
            if asyncio.iscoroutinefunction(subscription.handler):
                await subscription.handler(event)
            else:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(self._executor, subscription.handler, event)
                
        except Exception as e:
            logger.error("Handler %s failed for event %s: %s", 
                        subscription.subscription_id, event.id, e)
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du bus"""
        return {
            "name": self.name,
            "stats": self._stats.copy(),
            "queue_size": self._event_queue.qsize(),
            "processing": self._processing,
            "subscriptions": {
                "typed": len(self._subscriptions),
                "wildcard": len(self._wildcard_subscriptions),
                "total": self._stats["subscriptions_count"]
            }
        }


# Instance globale par défaut
default_event_bus = EventBus()
