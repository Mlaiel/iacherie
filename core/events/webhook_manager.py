"""IA-Influencer-Agent - Webhook Management System
Module: backend/core/events/webhook_manager.py
Architecture: Webhook Processing and External Integrations
Auteur: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.

Description:
    Système de gestion de webhooks pour intégrations externes avec retry,
    signature et transformation pour la plateforme IA-Influencer-Agent.
"""

from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import asyncio
import json
import logging
import uuid
import hmac
import hashlib
import aiohttp
from urllib.parse import urlparse

from .event_bus import Event, EventPriority, EventStatus
from .event_types import EventType

logger = logging.getLogger(__name__)


class WebhookEvent(Enum):
    """
Types d'événements webhook"""

    DELIVERY_SUCCESS = "delivery.success"
    DELIVERY_FAILED = "delivery.failed"
    DELIVERY_RETRY = "delivery.retry"
    ENDPOINT_DISABLED = "endpoint.disabled"
    SIGNATURE_INVALID = "signature.invalid"


class WebhookStatus(Enum):
    """Statut des webhooks"""

    ACTIVE = "active"
    DISABLED = "disabled"
    FAILED = "failed"
    SUSPENDED = "suspended"


@dataclass
class WebhookEndpoint:
    """Point de terminaison webhook"""
    endpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    url: str = ""
    name: str = ""
    description: str = ""
    secret: Optional[str] = None
    event_types: List[str] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 60.0
    status: WebhookStatus = WebhookStatus.ACTIVE
    
    # Filtres
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # Transformation
    transform_template: Optional[str] = None
    
    # Statistiques
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    last_delivery: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
            "endpoint_id": self.endpoint_id,
            "url": self.url,
            "name": self.name,
            "description": self.description,
            "event_types": self.event_types,
            "headers": self.headers,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "status": self.status.value,
            "filters": self.filters,
            "transform_template": self.transform_template,
            "total_deliveries": self.total_deliveries,
            "successful_deliveries": self.successful_deliveries,
            "failed_deliveries": self.failed_deliveries,
            "last_delivery": self.last_delivery.isoformat() if self.last_delivery else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def matches_event(self, event: Event) -> bool:
        """Vérifie si l'endpoint doit recevoir cet événement"""
        if self.status != WebhookStatus.ACTIVE:
            return False
        
        # Vérification types d'événements
        if not self.event_types or "*" in self.event_types:
            type_match = True
        else:
            type_match = any(
                event.type.startswith(event_type) or event_type == event.type
                for event_type in self.event_types
            )
        
        if not type_match:
            return False
        
        # Vérification filtres
        for key, value in self.filters.items():
            if key == "user_id" and event.user_id != value:
                return False
            elif key == "tenant_id" and event.tenant_id != value:
                return False
            elif key == "priority" and event.priority.value != value:
                return False
            elif key in event.metadata and event.metadata[key] != value:
                return False
            elif key in event.data and event.data[key] != value:
                return False
        
        return True


@dataclass
class WebhookDelivery:
    """Livraison de webhook"""
    delivery_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    endpoint_id: str = ""
    event_id: str = ""
    url: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    signature: Optional[str] = None
    
    # État de livraison
    status: str = "pending"  # pending, success, failed, retrying
    attempts: int = 0
    max_attempts: int = 3
    next_attempt: Optional[datetime] = None
        try:
            logger.info(f"Executing to_dict")
            
            # Implementation for to_dict
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    response_headers: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None
    
    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    delivered_at: Optional[datetime] = None
    duration: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "delivery_id": self.delivery_id,
            "endpoint_id": self.endpoint_id,
            "event_id": self.event_id,
            "url": self.url,
            "status": self.status,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "next_attempt": self.next_attempt.isoformat() if self.next_attempt else None,
            "response_status": self.response_status,
            "response_body": self.response_body,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "duration": self.duration
        }


class WebhookTransformer:
    """Transformateur de payload webhook"""
    
    @staticmethod
    def transform_event(event: Event, template: Optional[str] = None) -> Dict[str, Any]:
        """
Transforme un événement en payload webhook"""
        if template:
            return WebhookTransformer._apply_template(event, template)
        else:
            return WebhookTransformer._default_transform(event)
    
    @staticmethod
    def _default_transform(event: Event) -> Dict[str, Any]:
        """
Transformation par défaut"""
        return {
            "webhook_version": "1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": {
                "id": event.id,
                "type": event.type,
                "source": event.source,
                "subject": event.subject,
                "timestamp": event.timestamp.isoformat(),
                "priority": event.priority.value,
                "user_id": event.user_id,
                "tenant_id": event.tenant_id,
                "data": event.data,
                "metadata": event.metadata
            }
        }
    
    @staticmethod
    def _apply_template(event: Event, template: str) -> Dict[str, Any]:
        """Applique un template de transformation"""
        try:
            # Variables disponibles
            variables = {
                "event_id": event.id,
                "event_type": event.type,
                "event_source": event.source,
                "event_subject": event.subject,
                "timestamp": event.timestamp.isoformat(),
                "priority": event.priority.value,
                "user_id": event.user_id or "",
                "tenant_id": event.tenant_id or "",
                "data": event.data,
                "metadata": event.metadata
            }
            
            # Remplacement des variables dans le template
            transformed = template
            for key, value in variables.items():
                if isinstance(value, dict):
                    # Pour les objets complexes, sérialiser en JSON
                    transformed = transformed.replace(f"{{{{{key}}}}}", json.dumps(value))
                else:
                    transformed = transformed.replace(f"{{{{{key}}}}}", str(value))
            
            return json.loads(transformed)
            
        except Exception as e:
            logger.error("Failed to apply webhook template: %s", e)
            return WebhookTransformer._default_transform(event)


class WebhookSigner:
    """Générateur de signatures webhook"""
    
    @staticmethod
    def generate_signature(payload: bytes, secret: str) -> str:
        """
Génère une signature HMAC-SHA256"""
        signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    @staticmethod
    def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Vérifie une signature webhook"""
        expected_signature = WebhookSigner.generate_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)


class WebhookProcessor:
    """
Processeur de livraison de webhooks"""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def start(self):
        """
Démarre le processeur"""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=60)
            self._session = aiohttp.ClientSession(timeout=timeout)
    
    async def stop(self):
        """
Arrête le processeur"""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def deliver_webhook(
        self, 
        endpoint: WebhookEndpoint, 
        delivery: WebhookDelivery
    ) -> bool:
        """
Livre un webhook"""
        async with self._semaphore:
            return await self._attempt_delivery(endpoint, delivery)
    
    async def _attempt_delivery(
        self, 
        endpoint: WebhookEndpoint, 
        delivery: WebhookDelivery
    ) -> bool:
        """
Tente la livraison d'un webhook"""
        if not self._session:
            await self.start()
        
        delivery.attempts += 1
        start_time = datetime.now(timezone.utc)
        
        try:
            # Préparation des headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "IA-Influencer-Agent-Webhook/1.0",
                "X-Webhook-Delivery": delivery.delivery_id,
                "X-Webhook-Event": delivery.event_id,
                **endpoint.headers,
                **delivery.headers
            }
            
            # Ajout de la signature
            if endpoint.secret and delivery.signature:
                headers["X-Webhook-Signature"] = delivery.signature
            
            # Envoi de la requête
            async with self._session.post(
                delivery.url,
                json=delivery.payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=endpoint.timeout)
            ) as response:
                
                delivery.response_status = response.status
                delivery.response_body = await response.text()
                delivery.response_headers = dict(response.headers)
                
                # Succès si status 2xx
                if 200 <= response.status < 300:
                    delivery.status = "success"
                    delivery.delivered_at = datetime.now(timezone.utc)
                    delivery.duration = (delivery.delivered_at - start_time).total_seconds()
                    
                    logger.debug("Webhook delivered successfully: %s", delivery.delivery_id)
                    return True
                else:
                    delivery.status = "failed"
                    delivery.error_message = f"HTTP {response.status}: {delivery.response_body[:200]}"
                    
                    logger.warning("Webhook delivery failed: %s (status: %d)", 
                                 delivery.delivery_id, response.status)
                    return False
        
        except asyncio.TimeoutError:
            delivery.status = "failed"
            delivery.error_message = "Request timeout"
            logger.warning("Webhook delivery timeout: %s", delivery.delivery_id)
            return False
        
        except Exception as e:
            delivery.status = "failed"
            delivery.error_message = str(e)
            logger.error("Webhook delivery error: %s - %s", delivery.delivery_id, e)
            return False
        
        finally:
            if not delivery.duration:
                end_time = datetime.now(timezone.utc)
                delivery.duration = (end_time - start_time).total_seconds()


class WebhookManager:
    """
    Gestionnaire principal des webhooks
    """
    
    def __init__(self, processor: Optional[WebhookProcessor] = None):
        self.processor = processor or WebhookProcessor()
        
        # Stockage des endpoints et livraisons
        self._endpoints: Dict[str, WebhookEndpoint] = {}
        self._deliveries: Dict[str, WebhookDelivery] = {}
        self._delivery_queue: asyncio.Queue = asyncio.Queue()
        
        # Traitement en arrière-plan
        self._processing = False
        self._process_task: Optional[asyncio.Task] = None
        
        # Statistiques
        self._stats = {
            "endpoints_count": 0,
            "total_deliveries": 0,
            "successful_deliveries": 0,
            "failed_deliveries": 0,
            "pending_deliveries": 0
        }
        
        logger.info("WebhookManager initialized")
    
    async def start(self):
        """Démarre le gestionnaire de webhooks"""
        if self._processing:
            return
        
        await self.processor.start()
        self._processing = True
        self._process_task = asyncio.create_task(self._process_deliveries())
        
        logger.info("WebhookManager started")
    
    async def stop(self):
        """Arrête le gestionnaire de webhooks"""
        if not self._processing:
            return
        
        self._processing = False
        if self._process_task:
            await self._process_task
        
        await self.processor.stop()
        logger.info("WebhookManager stopped")
    
    def register_endpoint(self, endpoint: WebhookEndpoint) -> str:
        """Enregistre un endpoint webhook"""
        try:
            # Validation de l'URL
            parsed_url = urlparse(endpoint.url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid webhook URL")
            
            if parsed_url.scheme not in ["http", "https"]:
                raise ValueError("Webhook URL must use HTTP or HTTPS")
            
            # Stockage
            self._endpoints[endpoint.endpoint_id] = endpoint
            self._stats["endpoints_count"] += 1
            
            logger.info("Webhook endpoint registered: %s (%s)", endpoint.name, endpoint.url)
            return endpoint.endpoint_id
            
        except Exception as e:
            logger.error("Failed to register webhook endpoint: %s", e)
            raise
    
    def unregister_endpoint(self, endpoint_id: str) -> bool:
        """Supprime un endpoint webhook"""
        if endpoint_id in self._endpoints:
            endpoint = self._endpoints[endpoint_id]
            endpoint.status = WebhookStatus.DISABLED
            del self._endpoints[endpoint_id]
            self._stats["endpoints_count"] -= 1
            
            logger.info("Webhook endpoint unregistered: %s", endpoint_id)
            return True
        
        return False
    
    def get_endpoint(self, endpoint_id: str) -> Optional[WebhookEndpoint]:
        """Récupère un endpoint par ID"""
        return self._endpoints.get(endpoint_id)
    
    def get_endpoints(
        self, 
        status: Optional[WebhookStatus] = None,
        event_type: Optional[str] = None
    ) -> List[WebhookEndpoint]:
        """
Récupère les endpoints selon critères"""
        endpoints = list(self._endpoints.values())
        
        if status:
            endpoints = [e for e in endpoints if e.status == status]
        
        if event_type:
            endpoints = [
                e for e in endpoints 
                if "*" in e.event_types or any(
                    event_type.startswith(et) for et in e.event_types
                )
            ]
        
        return endpoints
    
    async def process_event(self, event: Event) -> List[str]:
        """Traite un événement et crée les livraisons webhook"""
        delivery_ids = []
        
        # Recherche des endpoints correspondants
        matching_endpoints = [
            endpoint for endpoint in self._endpoints.values()
            if endpoint.matches_event(event)
        ]
        
        if not matching_endpoints:
            logger.debug("No webhook endpoints found for event %s", event.id)
            return delivery_ids
        
        # Création des livraisons
        for endpoint in matching_endpoints:
            try:
                delivery = await self._create_delivery(event, endpoint)
                delivery_ids.append(delivery.delivery_id)
                
                # Ajout à la queue de traitement
                await self._delivery_queue.put(delivery)
                
            except Exception as e:
                logger.error("Failed to create webhook delivery for endpoint %s: %s", 
                           endpoint.endpoint_id, e)
        
        self._stats["pending_deliveries"] += len(delivery_ids)
        logger.debug("Created %d webhook deliveries for event %s", 
                    len(delivery_ids), event.id)
        
        return delivery_ids
    
    async def _create_delivery(self, event: Event, endpoint: WebhookEndpoint) -> WebhookDelivery:
        """Crée une livraison webhook"""
        # Transformation du payload
        payload = WebhookTransformer.transform_event(event, endpoint.transform_template)
        
        # Création de la livraison
        delivery = WebhookDelivery(
            endpoint_id=endpoint.endpoint_id,
            event_id=event.id,
            url=endpoint.url,
            payload=payload,
            headers=endpoint.headers.copy(),
            max_attempts=endpoint.max_retries + 1
        )
        
        # Génération de la signature
        if endpoint.secret:
            payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
            delivery.signature = WebhookSigner.generate_signature(payload_bytes, endpoint.secret)
        
        # Stockage
        self._deliveries[delivery.delivery_id] = delivery
        self._stats["total_deliveries"] += 1
        
        return delivery
    
    async def _process_deliveries(self):
        """Traitement continu des livraisons en queue"""
        while self._processing:
            try:
                # Récupération de la prochaine livraison
                delivery = await asyncio.wait_for(
                    self._delivery_queue.get(), timeout=1.0
                )
                
                # Traitement asynchrone
                asyncio.create_task(self._handle_delivery(delivery))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("Error in webhook delivery processing: %s", e)
    
    async def _handle_delivery(self, delivery: WebhookDelivery):
        """Traite une livraison webhook"""
        try:
            endpoint = self._endpoints.get(delivery.endpoint_id)
            if not endpoint:
                logger.error("Endpoint not found for delivery %s", delivery.delivery_id)
                return
            
            # Tentative de livraison
            success = await self.processor.deliver_webhook(endpoint, delivery)
            
            # Mise à jour des statistiques
            endpoint.total_deliveries += 1
            endpoint.last_delivery = datetime.now(timezone.utc)
            
            if success:
                endpoint.successful_deliveries += 1
                endpoint.last_success = endpoint.last_delivery
                self._stats["successful_deliveries"] += 1
                self._stats["pending_deliveries"] -= 1
                
                logger.debug("Webhook delivered successfully: %s", delivery.delivery_id)
                
            else:
                endpoint.failed_deliveries += 1
                endpoint.last_failure = endpoint.last_delivery
                
                # Retry si nécessaire
                if delivery.attempts < delivery.max_attempts:
                    await self._schedule_retry(delivery, endpoint)
                    self._stats["pending_deliveries"] -= 1
                    logger.info("Scheduled retry for webhook delivery: %s (attempt %d/%d)", 
                              delivery.delivery_id, delivery.attempts, delivery.max_attempts)
                else:
                    self._stats["failed_deliveries"] += 1
                    self._stats["pending_deliveries"] -= 1
                    logger.warning("Webhook delivery failed permanently: %s", delivery.delivery_id)
                    
                    # Désactivation automatique si trop d'échecs
                    failure_rate = endpoint.failed_deliveries / max(1, endpoint.total_deliveries)
                    if endpoint.total_deliveries >= 10 and failure_rate > 0.8:
                        endpoint.status = WebhookStatus.SUSPENDED
                        logger.warning("Webhook endpoint suspended due to high failure rate: %s", 
                                     endpoint.endpoint_id)
        
        except Exception as e:
            logger.error("Error handling webhook delivery %s: %s", delivery.delivery_id, e)
    
    async def _schedule_retry(self, delivery: WebhookDelivery, endpoint: WebhookEndpoint):
        """Planifie un retry de livraison"""
        # Calcul du délai (backoff exponentiel)
        delay = endpoint.retry_delay * (2 ** (delivery.attempts - 1))
        delivery.next_attempt = datetime.now(timezone.utc) + timedelta(seconds=delay)
        delivery.status = "retrying"
        
        # Replanification
        await asyncio.sleep(delay)
        await self._delivery_queue.put(delivery)
    
    def get_delivery(self, delivery_id: str) -> Optional[WebhookDelivery]:
        """Récupère une livraison par ID"""
        return self._deliveries.get(delivery_id)
    
    def get_deliveries(
        self,
        endpoint_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[WebhookDelivery]:
        """
Récupère les livraisons selon critères"""
        deliveries = list(self._deliveries.values())
        
        if endpoint_id:
            deliveries = [d for d in deliveries if d.endpoint_id == endpoint_id]
        
        if status:
            deliveries = [d for d in deliveries if d.status == status]
        
        # Tri par date de création (plus récent en premier)
        deliveries.sort(key=lambda d: d.created_at, reverse=True)
        
        return deliveries[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """
Retourne les statistiques"""
        return {
            "stats": self._stats.copy(),
            "queue_size": self._delivery_queue.qsize(),
            "processing": self._processing
        }


# Instance globale
default_webhook_manager = WebhookManager()
