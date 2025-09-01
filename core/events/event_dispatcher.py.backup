"""IA-Influencer-Agent - Event Dispatcher System
Module: backend/core/events/event_dispatcher.py
Architecture: Event Handler Orchestration and Routing
Auteur: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.

Description:
    Système de dispatch d'événements avec routage intelligent, gestion d'erreurs,
    retry automatique et orchestration des handlers pour la plateforme IA-Influencer-Agent.
"""
from typing import Any, Dict, List, Optional, Union, Callable, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import asyncio
import logging
import traceback
import inspect
from enum import Enum

from .event_bus import Event, EventPriority, EventStatus

logger = logging.getLogger(__name__)


class HandlerType(Enum):
    """Type de handler d'événement"""
    SYNC = "sync"
    ASYNC = "async"
    BACKGROUND = "background"


class RetryPolicy(Enum):
    """Politique de retry"""
    NONE = "none"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIXED = "fixed"


@dataclass
class HandlerConfig:
    """Configuration d'un handler d'événement"""
    handler_id: str
    event_types: List[str]
    handler_type: HandlerType = HandlerType.ASYNC
    priority: int = 100
    retry_policy: RetryPolicy = RetryPolicy.LINEAR
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0
    filters: Optional[Dict[str, Any]] = field(default_factory=dict)
    enabled: bool = True
    description: str = ""


class EventHandler(ABC):
    """
    Classe de base pour les handlers d'événements
    """
    
    def __init__(self, config: HandlerConfig):
        self.config = config
        self.stats = {
            "handled": 0,
            "succeeded": 0,
            "failed": 0,
            "retried": 0,
            "last_execution": None,
            "average_duration": 0.0
        }
    
    @abstractmethod
    async def handle(self, event: Event) -> Any:
        """Traite un événement"""
        pass
    
    def can_handle(self, event: Event) -> bool:
        """Vérifie si ce handler peut traiter l'événement"""
        if not self.config.enabled:
            return False
        
        # Vérification type d'événement
        type_match = any(
            event.type.startswith(event_type) or event_type == "*"
            for event_type in self.config.event_types
        )
        
        if not type_match:
            return False
        
        # Vérification filtres
        for key, value in self.config.filters.items():
            if key == "user_id" and event.user_id != value:
                return False
            elif key == "tenant_id" and event.tenant_id != value:
                return False
            elif key == "priority" and event.priority.value != value:
                return False
            elif key in event.metadata and event.metadata[key] != value:
                return False
        
        return True
    
    async def execute(self, event: Event) -> Dict[str, Any]:
        """Exécute le handler avec gestion d'erreurs et métriques"""
        start_time = datetime.now(timezone.utc)
        result = {
            "handler_id": self.config.handler_id,
            "success": False,
            "error": None,
            "duration": 0.0,
            "retries": 0
        }
        
        self.stats["handled"] += 1
        
        try:
            # Exécution avec timeout
            if self.config.timeout > 0:
                await asyncio.wait_for(
                    self.handle(event),
                    timeout=self.config.timeout
                )
            else:
                await self.handle(event)
            
            result["success"] = True
            self.stats["succeeded"] += 1
            
        except asyncio.TimeoutError:
            error_msg = f"Handler {self.config.handler_id} timed out after {self.config.timeout}s"
            result["error"] = error_msg
            self.stats["failed"] += 1
            logger.warning(error_msg)
            
        except Exception as e:
            result["error"] = str(e)
            self.stats["failed"] += 1
            logger.error("Handler %s failed: %s\n%s", 
                        self.config.handler_id, e, traceback.format_exc())
        
        # Calcul de la durée
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        result["duration"] = duration
        
        # Mise à jour statistiques
        self.stats["last_execution"] = end_time
        total_executions = self.stats["succeeded"] + self.stats["failed"]
        if total_executions > 0:
            self.stats["average_duration"] = (
                self.stats["average_duration"] * (total_executions - 1) + duration
            ) / total_executions
        
        return result


class FunctionHandler(EventHandler):
    """Handler basé sur une fonction"""
    
    def __init__(self, config: HandlerConfig, func: Callable):
        super().__init__(config)
        self.func = func
        self.is_async = asyncio.iscoroutinefunction(func)
    
    async def handle(self, event: Event) -> Any:
        """Exécute la fonction handler"""
        if self.is_async:
            return await self.func(event)
        else:
            # Exécution synchrone dans thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.func, event)


class ClassHandler(EventHandler):
    """Handler basé sur une classe avec méthode handle"""
    
    def __init__(self, config: HandlerConfig, handler_class: Type, *args, **kwargs):
        super().__init__(config)
        self.handler_instance = handler_class(*args, **kwargs)
    
    async def handle(self, event: Event) -> Any:
        """Délègue à l'instance de la classe"""
        handle_method = getattr(self.handler_instance, 'handle', None)
        if not handle_method:
            raise ValueError(f"Handler class must have a 'handle' method")
        
        if asyncio.iscoroutinefunction(handle_method):
            return await handle_method(event)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, handle_method, event)


class EventDispatcher:
    """
    Système central de dispatch d'événements
    """
    
    def __init__(
        self,
        name: str = "main_dispatcher",
        max_concurrent_handlers: int = 50,
        default_timeout: float = 30.0
    ):
        self.name = name
        self.max_concurrent_handlers = max_concurrent_handlers
        self.default_timeout = default_timeout
        
        # Stockage des handlers
        self._handlers: Dict[str, EventHandler] = {}
        self._handler_priorities: Dict[str, int] = {}
        
        # Semaphore pour limiter concurrence
        self._semaphore = asyncio.Semaphore(max_concurrent_handlers)
        
        # Statistiques
        self._stats = {
            "events_dispatched": 0,
            "events_succeeded": 0,
            "events_failed": 0,
            "handlers_registered": 0,
            "total_execution_time": 0.0
        }
        
        logger.info("EventDispatcher '%s' initialized", name)
    
    def register_handler(
        self,
        handler: EventHandler,
        priority: int = 100
    ) -> str:
        """
        Enregistre un handler d'événement
        
        Args:
            handler: Instance du handler
            priority: Priorité d'exécution (plus petit = plus prioritaire)
            
        Returns:
            ID du handler enregistré
        """
        handler_id = handler.config.handler_id
        
        if handler_id in self._handlers:
            logger.warning("Handler %s already registered, replacing", handler_id)
        
        self._handlers[handler_id] = handler
        self._handler_priorities[handler_id] = priority
        self._stats["handlers_registered"] += 1
        
        logger.info("Handler registered: %s (priority: %d)", handler_id, priority)
        return handler_id
    
    def register_function(
        self,
        func: Callable,
        event_types: List[str],
        handler_id: Optional[str] = None,
        priority: int = 100,
        **config_kwargs
    ) -> str:
        """
        Enregistre une fonction comme handler
        
        Args:
            func: Fonction à enregistrer
            event_types: Types d'événements à traiter
            handler_id: ID du handler (auto-généré si None)
            priority: Priorité d'exécution
            **config_kwargs: Configuration additionnelle
            
        Returns:
            ID du handler enregistré
        """
        if handler_id is None:
            handler_id = f"func_{func.__name__}_{id(func)}"
        
        config = HandlerConfig(
            handler_id=handler_id,
            event_types=event_types,
            priority=priority,
            **config_kwargs
        )
        
        handler = FunctionHandler(config, func)
        return self.register_handler(handler, priority)
    
    def register_class(
        self,
        handler_class: Type,
        event_types: List[str],
        handler_id: Optional[str] = None,
        priority: int = 100,
        *args,
        **kwargs
    ) -> str:
        """
        Enregistre une classe comme handler
        
        Args:
            handler_class: Classe handler
            event_types: Types d'événements à traiter
            handler_id: ID du handler (auto-généré si None)
            priority: Priorité d'exécution
            *args, **kwargs: Arguments pour le constructeur de la classe
            
        Returns:
            ID du handler enregistré
        """
        if handler_id is None:
            handler_id = f"class_{handler_class.__name__}_{id(handler_class)}"
        
        config_kwargs = kwargs.pop('config', {})
        config = HandlerConfig(
            handler_id=handler_id,
            event_types=event_types,
            priority=priority,
            **config_kwargs
        )
        
        handler = ClassHandler(config, handler_class, *args, **kwargs)
        return self.register_handler(handler, priority)
    
    def unregister_handler(self, handler_id: str) -> bool:
        """
        Désenregistre un handler
        
        Args:
            handler_id: ID du handler à supprimer
            
        Returns:
            True si supprimé avec succès
        """
        if handler_id in self._handlers:
            del self._handlers[handler_id]
            del self._handler_priorities[handler_id]
            self._stats["handlers_registered"] -= 1
            logger.info("Handler unregistered: %s", handler_id)
            return True
        
        logger.warning("Handler %s not found for unregistration", handler_id)
        return False
    
    async def dispatch(self, event: Event) -> Dict[str, Any]:
        """
        Dispatch un événement vers tous les handlers compatibles
        
        Args:
            event: Événement à dispatcher
            
        Returns:
            Résultats du dispatch avec détails par handler
        """
        start_time = datetime.now(timezone.utc)
        self._stats["events_dispatched"] += 1
        
        # Recherche des handlers compatibles
        compatible_handlers = self._get_compatible_handlers(event)
        
        if not compatible_handlers:
            logger.debug("No handlers found for event %s (type: %s)", event.id, event.type)
            return {
                "event_id": event.id,
                "handlers_count": 0,
                "handlers_results": [],
                "duration": 0.0,
                "success": True
            }
        
        # Tri par priorité
        compatible_handlers.sort(key=lambda h: self._handler_priorities.get(h.config.handler_id, 100))
        
        # Exécution des handlers
        results = []
        successful = 0
        failed = 0
        
        # Exécution avec limitation de concurrence
        async with self._semaphore:
            tasks = []
            for handler in compatible_handlers:
                task = asyncio.create_task(
                    self._execute_handler_with_retry(handler, event)
                )
                tasks.append(task)
            
            # Attente de tous les handlers
            handler_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(handler_results):
                if isinstance(result, Exception):
                    # Erreur non gérée
                    error_result = {
                        "handler_id": compatible_handlers[i].config.handler_id,
                        "success": False,
                        "error": str(result),
                        "duration": 0.0,
                        "retries": 0
                    }
                    results.append(error_result)
                    failed += 1
                else:
                    results.append(result)
                    if result["success"]:
                        successful += 1
                    else:
                        failed += 1
        
        # Calcul statistiques
        end_time = datetime.now(timezone.utc)
        total_duration = (end_time - start_time).total_seconds()
        
        if successful > 0:
            self._stats["events_succeeded"] += 1
        if failed > 0:
            self._stats["events_failed"] += 1
        
        self._stats["total_execution_time"] += total_duration
        
        dispatch_result = {
            "event_id": event.id,
            "handlers_count": len(compatible_handlers),
            "handlers_results": results,
            "successful_handlers": successful,
            "failed_handlers": failed,
            "duration": total_duration,
            "success": failed == 0
        }
        
        logger.debug("Event %s dispatched to %d handlers (success: %d, failed: %d)",
                    event.id, len(compatible_handlers), successful, failed)
        
        return dispatch_result
    
    def _get_compatible_handlers(self, event: Event) -> List[EventHandler]:
        """Trouve les handlers compatibles avec un événement"""
        compatible = []
        
        for handler in self._handlers.values():
            if handler.can_handle(event):
                compatible.append(handler)
        
        return compatible
    
    async def _execute_handler_with_retry(
        self, 
        handler: EventHandler, 
        event: Event
    ) -> Dict[str, Any]:
        """Exécute un handler avec retry selon sa politique"""
        last_error = None
        
        for attempt in range(handler.config.max_retries + 1):
            try:
                result = await handler.execute(event)
                
                if result["success"]:
                    result["retries"] = attempt
                    return result
                
                last_error = result["error"]
                
            except Exception as e:
                last_error = str(e)
                logger.error("Handler %s attempt %d failed: %s", 
                           handler.config.handler_id, attempt + 1, e)
            
            # Si pas le dernier essai, attendre selon la politique
            if attempt < handler.config.max_retries:
                delay = self._calculate_retry_delay(
                    handler.config.retry_policy,
                    attempt,
                    handler.config.retry_delay
                )
                
                if delay > 0:
                    await asyncio.sleep(delay)
                
                handler.stats["retried"] += 1
        
        # Échec après tous les essais
        return {
            "handler_id": handler.config.handler_id,
            "success": False,
            "error": last_error,
            "duration": 0.0,
            "retries": handler.config.max_retries
        }
    
    def _calculate_retry_delay(
        self, 
        policy: RetryPolicy, 
        attempt: int, 
        base_delay: float
    ) -> float:
        """Calcule le délai de retry selon la politique"""
        if policy == RetryPolicy.NONE:
            return 0.0
        elif policy == RetryPolicy.FIXED:
            return base_delay
        elif policy == RetryPolicy.LINEAR:
            return base_delay * (attempt + 1)
        elif policy == RetryPolicy.EXPONENTIAL:
            return base_delay * (2 ** attempt)
        else:
            return base_delay
    
    def get_handlers_info(self) -> List[Dict[str, Any]]:
        """Retourne les informations sur tous les handlers"""
        handlers_info = []
        
        for handler_id, handler in self._handlers.items():
            info = {
                "handler_id": handler_id,
                "event_types": handler.config.event_types,
                "priority": self._handler_priorities.get(handler_id, 100),
                "enabled": handler.config.enabled,
                "stats": handler.stats.copy(),
                "config": {
                    "handler_type": handler.config.handler_type.value,
                    "retry_policy": handler.config.retry_policy.value,
                    "max_retries": handler.config.max_retries,
                    "timeout": handler.config.timeout
                }
            }
            handlers_info.append(info)
        
        return handlers_info
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du dispatcher"""
        return {
            "name": self.name,
            "stats": self._stats.copy(),
            "handlers_count": len(self._handlers),
            "max_concurrent": self.max_concurrent_handlers,
            "average_execution_time": (
                self._stats["total_execution_time"] / max(1, self._stats["events_dispatched"])
            )
        }


# Instance globale par défaut
default_dispatcher = EventDispatcher()
