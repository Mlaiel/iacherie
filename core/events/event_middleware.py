"""IA-Influencer-Agent - Event Middleware System
Module: backend/core/events/event_middleware.py
Architecture: Event Processing Middleware Chain
Auteur: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.

Description:
    Système de middleware pour le traitement d'événements avec chaîne de traitement,
    authentification, validation, logging et métriques.
"""
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import json
import logging
import time
import uuid
import jwt
from functools import wraps

from .event_bus import Event, EventPriority, EventStatus
from .event_types import EventType

logger = logging.getLogger(__name__)


class MiddlewareType(Enum):
    """Types de middleware"""    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    LOGGING = "logging"
    METRICS = "metrics"
    RATE_LIMITING = "rate_limiting"
    CACHING = "caching"
    FILTERING = "filtering"


class MiddlewareAction(Enum):
    """Actions possibles du middleware"""    CONTINUE = "continue"    # Continuer le traitement
    STOP = "stop"           # Arrêter le traitement
    REJECT = "reject"       # Rejeter l'événement
    TRANSFORM = "transform"  # Transformer l'événement


@dataclass
class MiddlewareResult:
    """Résultat du traitement d'un middleware"""    action: MiddlewareAction
    event: Optional[Event] = None  # Événement transformé
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0


class EventMiddleware(ABC):
    """    Classe de base pour les middlewares d'événements
    """    
    def __init__(
        self,
        middleware_id: str,
        middleware_type: MiddlewareType,
        priority: int = 100,
        enabled: bool = True
    ):
        self.middleware_id = middleware_id
        self.middleware_type = middleware_type
        self.priority = priority
        self.enabled = enabled
        self.stats = {
            "processed": 0,
            "rejected": 0,
            "errors": 0,
            "total_time": 0.0
        }
    
    @abstractmethod
    async def process(self, event: Event, context: Dict[str, Any]) -> MiddlewareResult:
        """Traite un événement"""        pass
    
    async def execute(self, event: Event, context: Dict[str, Any]) -> MiddlewareResult:
        """Exécute le middleware avec métriques"""        if not self.enabled:
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, event=event)
        
        start_time = time.time()
        
        try:
            result = await self.process(event, context)
            self.stats["processed"] += 1
            
            if result.action == MiddlewareAction.REJECT:
                self.stats["rejected"] += 1
            
            return result
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error("Middleware %s failed: %s", self.middleware_id, e)
            
            return MiddlewareResult(
                action=MiddlewareAction.REJECT,
                error=str(e)
            )
        finally:
            processing_time = time.time() - start_time
            self.stats["total_time"] += processing_time


class AuthenticationMiddleware(EventMiddleware):
    """Middleware d'authentification des événements"""    
    def __init__(
        self,
        middleware_id: str = "auth_middleware",
        jwt_secret: str = "secret",
        required_claims: Optional[List[str]] = None
    ):
        super().__init__(middleware_id, MiddlewareType.AUTHENTICATION)
        self.jwt_secret = jwt_secret
        self.required_claims = required_claims or ["user_id", "tenant_id"]
    
    async def process(self, event: Event, context: Dict[str, Any]) -> MiddlewareResult:
        """Authentifie l'événement"""        try:
            # Vérification token JWT dans metadata
            token = event.metadata.get("auth_token")
            if not token:
                # Événements système exemptés
                if event.type.startswith("system."):
                    return MiddlewareResult(action=MiddlewareAction.CONTINUE, event=event)
                
                return MiddlewareResult(
                    action=MiddlewareAction.REJECT,
                    error="Authentication token required"
                )
            
            # Décodage et validation JWT
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            except jwt.InvalidTokenError as e:
                return MiddlewareResult(
                    action=MiddlewareAction.REJECT,
                    error=f"Invalid token: {e}"
                )
            
            # Vérification des claims requis
            for claim in self.required_claims:
                if claim not in payload:
                    return MiddlewareResult(
                        action=MiddlewareAction.REJECT,
                        error=f"Missing required claim: {claim}"
                    )
            
            # Enrichissement de l'événement
            if not event.user_id and "user_id" in payload:
                event.user_id = payload["user_id"]
            
            if not event.tenant_id and "tenant_id" in payload:
                event.tenant_id = payload["tenant_id"]
            
            # Ajout des claims au contexte
            context["auth_payload"] = payload
            context["authenticated"] = True
            
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, event=event)
            
        except Exception as e:
            return MiddlewareResult(
                action=MiddlewareAction.REJECT,
                error=f"Authentication error: {e}"
            )


class ValidationMiddleware(EventMiddleware):
    """Middleware de validation des événements"""    
    def __init__(
        self,
        middleware_id: str = "validation_middleware",
        validation_rules: Optional[Dict[str, Any]] = None
    ):
        super().__init__(middleware_id, MiddlewareType.VALIDATION)
        self.validation_rules = validation_rules or {}
    
    async def process(self, event: Event, context: Dict[str, Any]) -> MiddlewareResult:
        """Valide l'événement"""        try:
            # Validation de base
            validation_errors = []
            
            # Vérification ID
            if not event.id:
                validation_errors.append("Event ID is required")
            
            # Vérification type
            if not event.type:
                validation_errors.append("Event type is required")
            
            # Vérification timestamp
            if not event.timestamp:
                validation_errors.append("Event timestamp is required")
            
            # Validation métier selon le type
            if event.type.startswith("content."):
                if not event.data.get("content_id"):
                    validation_errors.append("content_id is required for content events")
            
            elif event.type.startswith("protection."):
                if not event.data.get("content_id"):
                    validation_errors.append("content_id is required for protection events")
            
            elif event.type.startswith("monetization."):
                if not event.data.get("content_id"):
                    validation_errors.append("content_id is required for monetization events")
                
                if event.type == "monetization.revenue.detected":
                    if not event.data.get("revenue_amount"):
                        validation_errors.append("revenue_amount is required")
                    if not event.data.get("platform"):
                        validation_errors.append("platform is required")
            
            # Validation personnalisée
            type_rules = self.validation_rules.get(event.type, {})
            for field, rule in type_rules.items():
                if rule.get("required", False):
                    if field not in event.data and field not in event.metadata:
                        validation_errors.append(f"Required field missing: {field}")
                
                # Validation de type
                if field in event.data:
                    expected_type = rule.get("type")
                    if expected_type and not isinstance(event.data[field], expected_type):
                        validation_errors.append(
                            f"Field {field} must be of type {expected_type.__name__}"
                        )
            
            if validation_errors:
                return MiddlewareResult(
                    action=MiddlewareAction.REJECT,
                    error=f"Validation failed: {'; '.join(validation_errors)}"
                )
            
            context["validated"] = True
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, event=event)
            
        except Exception as e:
            return MiddlewareResult(
                action=MiddlewareAction.REJECT,
                error=f"Validation error: {e}"
            )


class LoggingMiddleware(EventMiddleware):
    """Middleware de logging des événements"""    
    def __init__(
        self,
        middleware_id: str = "logging_middleware",
        log_level: str = "INFO",
        include_data: bool = False,
        include_metadata: bool = False
    ):
        super().__init__(middleware_id, MiddlewareType.LOGGING)
        self.log_level = getattr(logging, log_level.upper())
        self.include_data = include_data
        self.include_metadata = include_metadata
    
    async def process(self, event: Event, context: Dict[str, Any]) -> MiddlewareResult:
        """Logge l'événement"""        try:
            # Construction du message de log
            log_data = {
                "event_id": event.id,
                "event_type": event.type,
                "source": event.source,
                "user_id": event.user_id,
                "tenant_id": event.tenant_id,
                "timestamp": event.timestamp.isoformat(),
                "priority": event.priority.value
            }
            
            if self.include_data:
                log_data["data"] = event.data
            
            if self.include_metadata:
                log_data["metadata"] = event.metadata
            
            # Log selon la priorité
            if event.priority == EventPriority.CRITICAL:
                logger.critical("Critical event: %s", json.dumps(log_data))
            elif event.priority == EventPriority.HIGH:
                logger.warning("High priority event: %s", json.dumps(log_data))
            else:
                logger.log(self.log_level, "Event: %s", json.dumps(log_data))
            
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, event=event)
            
        except Exception as e:
            logger.error("Logging middleware error: %s", e)
            # Ne pas bloquer le traitement pour une erreur de log
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, event=event)


class MetricsMiddleware(EventMiddleware):
    """Middleware de collecte de métriques"""    
    def __init__(
        self,
        middleware_id: str = "metrics_middleware",
        metrics_backend: Optional[str] = None
    ):
        super().__init__(middleware_id, MiddlewareType.METRICS)
        self.metrics_backend = metrics_backend
        self.counters = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_user": {},
            "events_by_tenant": {},
            "events_by_priority": {}
        }
        self.last_reset = datetime.now(timezone.utc)
    
    async def process(self, event: Event, context: Dict[str, Any]) -> MiddlewareResult:
        """Collecte les métriques"""        try:
            # Compteurs globaux
            self.counters["total_events"] += 1
            
            # Par type
            event_type_base = event.type.split('.')[0]
            if event_type_base not in self.counters["events_by_type"]:
                self.counters["events_by_type"][event_type_base] = 0
            self.counters["events_by_type"][event_type_base] += 1
            
            # Par utilisateur
            if event.user_id:
                if event.user_id not in self.counters["events_by_user"]:
                    self.counters["events_by_user"][event.user_id] = 0
                self.counters["events_by_user"][event.user_id] += 1
            
            # Par tenant
            if event.tenant_id:
                if event.tenant_id not in self.counters["events_by_tenant"]:
                    self.counters["events_by_tenant"][event.tenant_id] = 0
                self.counters["events_by_tenant"][event.tenant_id] += 1
            
            # Par priorité
            priority_key = event.priority.value
            if priority_key not in self.counters["events_by_priority"]:
                self.counters["events_by_priority"][priority_key] = 0
            self.counters["events_by_priority"][priority_key] += 1
            
            # Ajout métriques au contexte
            context["metrics_collected"] = True
            
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, event=event)
            
        except Exception as e:
            logger.error("Metrics middleware error: %s", e)
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, event=event)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques collectées"""        return {
            "counters": self.counters.copy(),
            "last_reset": self.last_reset.isoformat(),
            "collection_period": (datetime.now(timezone.utc) - self.last_reset).total_seconds()
        }
    
    def reset_metrics(self):
        """Remet à zéro les métriques"""        self.counters = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_user": {},
            "events_by_tenant": {},
            "events_by_priority": {}
        }
        self.last_reset = datetime.now(timezone.utc)


class RateLimitingMiddleware(EventMiddleware):
    """Middleware de limitation de débit"""    
    def __init__(
        self,
        middleware_id: str = "rate_limiting_middleware",
        global_limit: int = 1000,  # événements/minute
        user_limit: int = 100,     # événements/minute par utilisateur
        tenant_limit: int = 500    # événements/minute par tenant
    ):
        super().__init__(middleware_id, MiddlewareType.RATE_LIMITING)
        self.global_limit = global_limit
        self.user_limit = user_limit
        self.tenant_limit = tenant_limit
        
        # Compteurs par fenêtre glissante (1 minute)
        self.global_counter = 0
        self.user_counters = {}
        self.tenant_counters = {}
        self.last_reset = datetime.now(timezone.utc)
    
    async def process(self, event: Event, context: Dict[str, Any]) -> MiddlewareResult:
        """Vérifie les limites de débit"""        try:
            current_time = datetime.now(timezone.utc)
            
            # Reset des compteurs chaque minute
            if (current_time - self.last_reset).seconds >= 60:
                self._reset_counters()
                self.last_reset = current_time
            
            # Vérification limite globale
            if self.global_counter >= self.global_limit:
                return MiddlewareResult(
                    action=MiddlewareAction.REJECT,
                    error="Global rate limit exceeded"
                )
            
            # Vérification limite utilisateur
            if event.user_id:
                user_count = self.user_counters.get(event.user_id, 0)
                if user_count >= self.user_limit:
                    return MiddlewareResult(
                        action=MiddlewareAction.REJECT,
                        error=f"User rate limit exceeded for {event.user_id}"
                    )
            
            # Vérification limite tenant
            if event.tenant_id:
                tenant_count = self.tenant_counters.get(event.tenant_id, 0)
                if tenant_count >= self.tenant_limit:
                    return MiddlewareResult(
                        action=MiddlewareAction.REJECT,
                        error=f"Tenant rate limit exceeded for {event.tenant_id}"
                    )
            
            # Incrémentation des compteurs
            self.global_counter += 1
            
            if event.user_id:
                self.user_counters[event.user_id] = self.user_counters.get(event.user_id, 0) + 1
            
            if event.tenant_id:
                self.tenant_counters[event.tenant_id] = self.tenant_counters.get(event.tenant_id, 0) + 1
            
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, event=event)
            
        except Exception as e:
            logger.error("Rate limiting middleware error: %s", e)
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, event=event)
    
    def _reset_counters(self):
        """Remet à zéro les compteurs"""        self.global_counter = 0
        self.user_counters.clear()
        self.tenant_counters.clear()


class TransformationMiddleware(EventMiddleware):
    """Middleware de transformation d'événements"""    
    def __init__(
        self,
        middleware_id: str = "transformation_middleware",
        transformations: Optional[Dict[str, Callable]] = None
    ):
        super().__init__(middleware_id, MiddlewareType.TRANSFORMATION)
        self.transformations = transformations or {}
    
    async def process(self, event: Event, context: Dict[str, Any]) -> MiddlewareResult:
        """Transforme l'événement"""        try:
            # Transformations standard
            transformed_event = await self._apply_standard_transforms(event)
            
            # Transformations personnalisées par type
            if event.type in self.transformations:
                transformer = self.transformations[event.type]
                if asyncio.iscoroutinefunction(transformer):
                    transformed_event = await transformer(transformed_event)
                else:
                    transformed_event = transformer(transformed_event)
            
            return MiddlewareResult(
                action=MiddlewareAction.TRANSFORM,
                event=transformed_event
            )
            
        except Exception as e:
            logger.error("Transformation middleware error: %s", e)
            return MiddlewareResult(action=MiddlewareAction.CONTINUE, event=event)
    
    async def _apply_standard_transforms(self, event: Event) -> Event:
        """Applique les transformations standard"""        # Enrichissement automatique
        if not event.metadata.get("processed_at"):
            event.metadata["processed_at"] = datetime.now(timezone.utc).isoformat()
        
        # Normalisation des données selon le type
        if event.type.startswith("content."):
            self._normalize_content_event(event)
        elif event.type.startswith("protection."):
            self._normalize_protection_event(event)
        elif event.type.startswith("monetization."):
            self._normalize_monetization_event(event)
        
        return event
    
    def _normalize_content_event(self, event: Event):
        """Normalise les événements de contenu"""        # Standardisation des champs
        if "fileSize" in event.data and "file_size" not in event.data:
            event.data["file_size"] = event.data.pop("fileSize")
        
        if "contentType" in event.data and "content_type" not in event.data:
            event.data["content_type"] = event.data.pop("contentType")
    
    def _normalize_protection_event(self, event: Event):
        """Normalise les événements de protection"""        # Standardisation score de similarité
        if "similarity" in event.data and "similarity_score" not in event.data:
            event.data["similarity_score"] = event.data.pop("similarity")
    
    def _normalize_monetization_event(self, event: Event):
        """Normalise les événements de monétisation"""        # Standardisation montant
        if "amount" in event.data and "revenue_amount" not in event.data:
            event.data["revenue_amount"] = event.data.pop("amount")


class MiddlewareChain:
    """    Chaîne de traitement des middlewares
    """    
    def __init__(self):
        self._middlewares: List[EventMiddleware] = []
    
    def add_middleware(self, middleware: EventMiddleware):
        """Ajoute un middleware à la chaîne"""        self._middlewares.append(middleware)
        # Tri par priorité (plus petit = plus prioritaire)
        self._middlewares.sort(key=lambda m: m.priority)
        
        logger.debug("Middleware added: %s (priority: %d)", 
                    middleware.middleware_id, middleware.priority)
    
    def remove_middleware(self, middleware_id: str) -> bool:
        """Supprime un middleware de la chaîne"""        for i, middleware in enumerate(self._middlewares):
            if middleware.middleware_id == middleware_id:
                del self._middlewares[i]
                logger.debug("Middleware removed: %s", middleware_id)
                return True
        return False
    
    async def process_event(
        self, 
        event: Event, 
        context: Optional[Dict[str, Any]] = None
    ) -> MiddlewareResult:
        """Traite un événement à travers la chaîne de middlewares"""        if context is None:
            context = {}
        
        current_event = event
        
        for middleware in self._middlewares:
            try:
                result = await middleware.execute(current_event, context)
                
                if result.action == MiddlewareAction.REJECT:
                    logger.warning("Event rejected by middleware %s: %s", 
                                 middleware.middleware_id, result.error)
                    return result
                
                elif result.action == MiddlewareAction.STOP:
                    logger.debug("Event processing stopped by middleware %s", 
                               middleware.middleware_id)
                    return MiddlewareResult(
                        action=MiddlewareAction.CONTINUE,
                        event=current_event
                    )
                
                elif result.action == MiddlewareAction.TRANSFORM and result.event:
                    current_event = result.event
                    logger.debug("Event transformed by middleware %s", 
                               middleware.middleware_id)
                
                # CONTINUE: on continue avec l'événement courant
                
            except Exception as e:
                logger.error("Middleware %s failed: %s", middleware.middleware_id, e)
                # Continuer avec les autres middlewares
                continue
        
        return MiddlewareResult(
            action=MiddlewareAction.CONTINUE,
            event=current_event,
            metadata=context
        )
    
    def get_middlewares(self) -> List[Dict[str, Any]]:
        """Retourne la liste des middlewares"""        return [
            {
                "middleware_id": m.middleware_id,
                "type": m.middleware_type.value,
                "priority": m.priority,
                "enabled": m.enabled,
                "stats": m.stats.copy()
            }
            for m in self._middlewares
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de la chaîne"""        total_processed = sum(m.stats["processed"] for m in self._middlewares)
        total_rejected = sum(m.stats["rejected"] for m in self._middlewares)
        total_errors = sum(m.stats["errors"] for m in self._middlewares)
        
        return {
            "middleware_count": len(self._middlewares),
            "total_processed": total_processed,
            "total_rejected": total_rejected,
            "total_errors": total_errors,
            "middlewares": self.get_middlewares()
        }


# Instance globale de la chaîne de middlewares
default_middleware_chain = MiddlewareChain()

# Configuration par défaut
def setup_default_middlewares():
    """Configure les middlewares par défaut"""    # Authentification (priorité 10)
    auth_middleware = AuthenticationMiddleware(priority=10)
    default_middleware_chain.add_middleware(auth_middleware)
    
    # Validation (priorité 20)
    validation_middleware = ValidationMiddleware(priority=20)
    default_middleware_chain.add_middleware(validation_middleware)
    
    # Rate limiting (priorité 30)
    rate_middleware = RateLimitingMiddleware(priority=30)
    default_middleware_chain.add_middleware(rate_middleware)
    
    # Transformation (priorité 40)
    transform_middleware = TransformationMiddleware(priority=40)
    default_middleware_chain.add_middleware(transform_middleware)
    
    # Métriques (priorité 80)
    metrics_middleware = MetricsMiddleware(priority=80)
    default_middleware_chain.add_middleware(metrics_middleware)
    
    # Logging (priorité 90)
    logging_middleware = LoggingMiddleware(priority=90)
    default_middleware_chain.add_middleware(logging_middleware)
    
    logger.info("Default middleware chain configured")


# Décorateur pour appliquer automatiquement les middlewares
def with_middleware(chain: MiddlewareChain = default_middleware_chain):
    """Décorateur pour appliquer les middlewares à une fonction"""    def decorator(func: Callable[[Event], Awaitable[Any]]):
        @wraps(func)
        async def wrapper(event: Event, context: Optional[Dict[str, Any]] = None):
            # Traitement par les middlewares
            result = await chain.process_event(event, context)
            
            if result.action == MiddlewareAction.REJECT:
                raise ValueError(f"Event rejected: {result.error}")
            
            # Appel de la fonction originale avec l'événement (possiblement transformé)
            return await func(result.event or event)
        
        return wrapper
    return decorator
