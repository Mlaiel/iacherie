"""IA-Influencer-Agent - Event Aggregator and Processor
Module: backend/core/events/event_aggregator.py
Architecture: Event Stream Processing and Analytics
Auteur: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.

Description:
    Système d'agrégation d'événements avec processing temps réel,
    analytics et métriques pour la plateforme IA-Influencer-Agent.
"""
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import asyncio
import json
import logging
import uuid
from collections import defaultdict, deque
import statistics
from abc import ABC, abstractmethod

from .event_bus import Event, EventPriority, EventStatus
from .event_types import EventType

logger = logging.getLogger(__name__)


class AggregationType(Enum):
    """Types d'agrégation"""
    COUNT = "count"
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    DISTINCT_COUNT = "distinct_count"
    PERCENTILE = "percentile"
    RATE = "rate"
    TREND = "trend"


class WindowType(Enum):
    """Types de fenêtres temporelles"""
    TUMBLING = "tumbling"  # Fenêtres non-chevauchantes
    SLIDING = "sliding"    # Fenêtres glissantes
    SESSION = "session"    # Fenêtres basées sur activité


@dataclass
class AggregationWindow:
    """Fenêtre d'agrégation temporelle"""
    window_id: str
    window_type: WindowType
    size_seconds: int
    slide_seconds: Optional[int] = None  # Pour sliding windows
    session_timeout: Optional[int] = None  # Pour session windows
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_count: int = 0
    
    def contains(self, timestamp: datetime) -> bool:
        """Vérifie si un timestamp est dans la fenêtre"""
        if not self.start_time or not self.end_time:
            return False
        return self.start_time <= timestamp < self.end_time
    
    def is_complete(self) -> bool:
        """Vérifie si la fenêtre est complète"""
        if not self.end_time:
            return False
        return datetime.now(timezone.utc) >= self.end_time


@dataclass
class AggregationRule:
    """Règle d'agrégation"""
    rule_id: str
    name: str
    event_types: List[str]
    aggregation_type: AggregationType
    field_name: Optional[str] = None  # Champ à agréger
    group_by: Optional[List[str]] = None  # Champs de groupement
    filters: Optional[Dict[str, Any]] = None
    window_type: WindowType = WindowType.TUMBLING
    window_size: int = 300  # 5 minutes par défaut
    slide_interval: Optional[int] = None
    enabled: bool = True
    
    def matches_event(self, event: Event) -> bool:
        """Vérifie si l'événement correspond à la règle"""
        if not self.enabled:
            return False
        
        # Vérification type
        type_match = any(
            event.type.startswith(event_type) or event_type == "*"
            for event_type in self.event_types
        )
        
        if not type_match:
            return False
        
        # Vérification filtres
        if self.filters:
            for key, value in self.filters.items():
                if key == "user_id" and event.user_id != value:
                    return False
                elif key == "tenant_id" and event.tenant_id != value:
                    return False
                elif key in event.metadata and event.metadata[key] != value:
                    return False
                elif key in event.data and event.data[key] != value:
                    return False
        
        return True
    
    def get_group_key(self, event: Event) -> str:
        """Génère une clé de groupement pour l'événement"""
        if not self.group_by:
            return "default"
        
        key_parts = []
        for field in self.group_by:
            if field == "user_id":
                key_parts.append(event.user_id or "unknown")
            elif field == "tenant_id":
                key_parts.append(event.tenant_id or "unknown")
            elif field == "event_type":
                key_parts.append(event.type)
            elif field in event.metadata:
                key_parts.append(str(event.metadata[field]))
            elif field in event.data:
                key_parts.append(str(event.data[field]))
            else:
                key_parts.append("unknown")
        
        return "|".join(key_parts)


@dataclass
class AggregationResult:
    """Résultat d'agrégation"""
    rule_id: str
    window_id: str
    group_key: str
    aggregation_type: AggregationType
    value: Union[int, float, str, List[Any]]
    event_count: int
    start_time: datetime
    end_time: datetime
    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "window_id": self.window_id,
            "group_key": self.group_key,
            "aggregation_type": self.aggregation_type.value,
            "value": self.value,
            "event_count": self.event_count,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "computed_at": self.computed_at.isoformat(),
            "metadata": self.metadata
        }


class EventBuffer:
    """Buffer pour stocker les événements en attente d'agrégation"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._events: deque = deque(maxlen=max_size)
        self._index_by_type: Dict[str, List[Event]] = defaultdict(list)
        self._index_by_time: Dict[datetime, List[Event]] = defaultdict(list)
    
    def add_event(self, event: Event):
        """Ajoute un événement au buffer"""
        self._events.append(event)
        self._index_by_type[event.type].append(event)
        
        # Index par minute pour optimisation
        minute_key = event.timestamp.replace(second=0, microsecond=0)
        self._index_by_time[minute_key].append(event)
        
        # Nettoyage des index anciens
        self._cleanup_old_indexes()
    
    def get_events_by_type(self, event_type: str) -> List[Event]:
        """Récupère les événements par type"""
        events = []
        for stored_type, event_list in self._index_by_type.items():
            if stored_type.startswith(event_type) or event_type == "*":
                events.extend(event_list)
        return events
    
    def get_events_in_window(
        self, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[Event]:
        """Récupère les événements dans une fenêtre temporelle"""
        events = []
        for event in self._events:
            if start_time <= event.timestamp < end_time:
                events.append(event)
        return events
    
    def _cleanup_old_indexes(self):
        """Nettoie les index d'événements anciens"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
        
        # Nettoyage index temporel
        expired_keys = [
            key for key in self._index_by_time.keys()
            if key < cutoff_time
        ]
        for key in expired_keys:
            del self._index_by_time[key]
    
    def size(self) -> int:
        """Retourne la taille du buffer"""
        return len(self._events)


class AggregationProcessor:
    """Processeur d'agrégation pour un type spécifique"""
    
    def __init__(self, rule: AggregationRule):
        self.rule = rule
        self._windows: Dict[str, AggregationWindow] = {}
        self._values: Dict[str, List[Any]] = defaultdict(list)  # group_key -> values
        self._results: List[AggregationResult] = []
    
    def process_event(self, event: Event) -> List[AggregationResult]:
        """Traite un événement et retourne les résultats complétés"""
        if not self.rule.matches_event(event):
            return []
        
        group_key = self.rule.get_group_key(event)
        current_time = event.timestamp
        
        # Gestion des fenêtres
        window = self._get_or_create_window(current_time, group_key)
        
        if not window.contains(current_time):
            # Finaliser les fenêtres complètes
            completed_results = self._finalize_completed_windows()
            
            # Créer nouvelle fenêtre
            window = self._create_new_window(current_time, group_key)
            
            # Traiter l'événement dans la nouvelle fenêtre
            self._add_event_to_window(event, window, group_key)
            
            return completed_results
        else:
            # Ajouter à la fenêtre existante
            self._add_event_to_window(event, window, group_key)
            return []
    
    def _get_or_create_window(
        self, 
        timestamp: datetime, 
        group_key: str
    ) -> AggregationWindow:
        """Récupère ou crée une fenêtre pour un timestamp"""
        window_key = f"{group_key}_{timestamp.strftime('%Y%m%d_%H%M')}"
        
        if window_key not in self._windows:
            return self._create_new_window(timestamp, group_key, window_key)
        
        return self._windows[window_key]
    
    def _create_new_window(
        self, 
        timestamp: datetime, 
        group_key: str,
        window_key: Optional[str] = None
    ) -> AggregationWindow:
        """Crée une nouvelle fenêtre"""
        if not window_key:
            window_key = f"{group_key}_{timestamp.strftime('%Y%m%d_%H%M')}"
        
        if self.rule.window_type == WindowType.TUMBLING:
            # Fenêtre tumbling alignée
            window_start = self._align_to_window(timestamp)
            window_end = window_start + timedelta(seconds=self.rule.window_size)
        else:
            # Autres types de fenêtres
            window_start = timestamp
            window_end = timestamp + timedelta(seconds=self.rule.window_size)
        
        window = AggregationWindow(
            window_id=window_key,
            window_type=self.rule.window_type,
            size_seconds=self.rule.window_size,
            start_time=window_start,
            end_time=window_end
        )
        
        self._windows[window_key] = window
        return window
    
    def _align_to_window(self, timestamp: datetime) -> datetime:
        """Aligne un timestamp au début de fenêtre"""
        window_size = self.rule.window_size
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        seconds_since_epoch = (timestamp - epoch).total_seconds()
        aligned_seconds = (seconds_since_epoch // window_size) * window_size
        return epoch + timedelta(seconds=aligned_seconds)
    
    def _add_event_to_window(
        self, 
        event: Event, 
        window: AggregationWindow, 
        group_key: str
    ):
        """Ajoute un événement à une fenêtre"""
        window.event_count += 1
        
        # Extraction de la valeur selon le type d'agrégation
        value = self._extract_value(event)
        if value is not None:
            window_group_key = f"{window.window_id}_{group_key}"
            self._values[window_group_key].append(value)
    
    def _extract_value(self, event: Event) -> Any:
        """Extrait la valeur à agréger d'un événement"""
        if not self.rule.field_name:
            return 1  # Comptage simple
        
        # Recherche dans data puis metadata
        if self.rule.field_name in event.data:
            return event.data[self.rule.field_name]
        elif self.rule.field_name in event.metadata:
            return event.metadata[self.rule.field_name]
        
        return None
    
    def _finalize_completed_windows(self) -> List[AggregationResult]:
        """Finalise les fenêtres complètes"""
        results = []
        current_time = datetime.now(timezone.utc)
        completed_windows = []
        
        for window_key, window in self._windows.items():
            if window.is_complete():
                result = self._compute_aggregation(window)
                if result:
                    results.append(result)
                completed_windows.append(window_key)
        
        # Nettoyage des fenêtres complètes
        for window_key in completed_windows:
            del self._windows[window_key]
            # Nettoyage des valeurs associées
            keys_to_remove = [
                key for key in self._values.keys()
                if key.startswith(window_key)
            ]
            for key in keys_to_remove:
                del self._values[key]
        
        return results
    
    def _compute_aggregation(self, window: AggregationWindow) -> Optional[AggregationResult]:
        """Calcule l'agrégation pour une fenêtre"""
        try:
            # Récupération des valeurs pour cette fenêtre
            window_values = []
            for key, values in self._values.items():
                if key.startswith(window.window_id):
                    window_values.extend(values)
            
            if not window_values and self.rule.aggregation_type != AggregationType.COUNT:
                return None
            
            # Calcul selon le type d'agrégation
            result_value = self._calculate_aggregation_value(window_values)
            
            # Extraction du group_key (simplifié)
            group_key = "default"
            
            return AggregationResult(
                rule_id=self.rule.rule_id,
                window_id=window.window_id,
                group_key=group_key,
                aggregation_type=self.rule.aggregation_type,
                value=result_value,
                event_count=window.event_count,
                start_time=window.start_time,
                end_time=window.end_time
            )
            
        except Exception as e:
            logger.error("Failed to compute aggregation for window %s: %s", 
                        window.window_id, e)
            return None
    
    def _calculate_aggregation_value(self, values: List[Any]) -> Union[int, float, str, List[Any]]:
        """Calcule la valeur d'agrégation"""
        if self.rule.aggregation_type == AggregationType.COUNT:
            return len(values)
        elif self.rule.aggregation_type == AggregationType.SUM:
            return sum(values)
        elif self.rule.aggregation_type == AggregationType.AVERAGE:
            return statistics.mean(values) if values else 0
        elif self.rule.aggregation_type == AggregationType.MIN:
            return min(values) if values else 0
        elif self.rule.aggregation_type == AggregationType.MAX:
            return max(values) if values else 0
        elif self.rule.aggregation_type == AggregationType.DISTINCT_COUNT:
            return len(set(values))
        elif self.rule.aggregation_type == AggregationType.PERCENTILE:
            # Percentile 95 par défaut
            if values:
                sorted_values = sorted(values)
                index = int(0.95 * len(sorted_values))
                return sorted_values[min(index, len(sorted_values) - 1)]
            return 0
        else:
            return len(values)


class EventAggregator:
    """
    Système principal d'agrégation d'événements
    """
    
    def __init__(
        self,
        buffer_size: int = 10000,
        processing_interval: float = 10.0
    ):
        self.buffer_size = buffer_size
        self.processing_interval = processing_interval
        
        # Composants internes
        self._buffer = EventBuffer(buffer_size)
        self._rules: Dict[str, AggregationRule] = {}
        self._processors: Dict[str, AggregationProcessor] = {}
        self._results: List[AggregationResult] = []
        
        # Callbacks pour les résultats
        self._result_callbacks: List[Callable[[AggregationResult], None]] = []
        
        # État du traitement
        self._processing = False
        self._process_task: Optional[asyncio.Task] = None
        
        # Statistiques
        self._stats = {
            "events_processed": 0,
            "rules_count": 0,
            "results_generated": 0,
            "processing_errors": 0
        }
        
        logger.info("EventAggregator initialized")
    
    async def start(self):
        """Démarre le traitement d'agrégation"""
        if self._processing:
            return
        
        self._processing = True
        self._process_task = asyncio.create_task(self._process_loop())
        logger.info("EventAggregator started")
    
    async def stop(self):
        """Arrête le traitement d'agrégation"""
        if not self._processing:
            return
        
        self._processing = False
        if self._process_task:
            await self._process_task
        
        logger.info("EventAggregator stopped")
    
    def register_rule(self, rule: AggregationRule) -> bool:
        """Enregistre une règle d'agrégation"""
        try:
            self._rules[rule.rule_id] = rule
            self._processors[rule.rule_id] = AggregationProcessor(rule)
            self._stats["rules_count"] += 1
            
            logger.info("Aggregation rule registered: %s", rule.rule_id)
            return True
            
        except Exception as e:
            logger.error("Failed to register rule %s: %s", rule.rule_id, e)
            return False
    
    def unregister_rule(self, rule_id: str) -> bool:
        """Désenregistre une règle d'agrégation"""
        if rule_id in self._rules:
            del self._rules[rule_id]
            del self._processors[rule_id]
            self._stats["rules_count"] -= 1
            
            logger.info("Aggregation rule unregistered: %s", rule_id)
            return True
        
        return False
    
    def add_result_callback(self, callback: Callable[[AggregationResult], None]):
        """Ajoute un callback pour les résultats"""
        self._result_callbacks.append(callback)
    
    async def process_event(self, event: Event) -> List[AggregationResult]:
        """Traite un événement et retourne les résultats immédiats"""
        self._buffer.add_event(event)
        self._stats["events_processed"] += 1
        
        results = []
        
        # Traitement par tous les processeurs
        for processor in self._processors.values():
            try:
                processor_results = processor.process_event(event)
                results.extend(processor_results)
                
            except Exception as e:
                logger.error("Error in processor %s: %s", processor.rule.rule_id, e)
                self._stats["processing_errors"] += 1
        
        # Notification des callbacks
        for result in results:
            self._stats["results_generated"] += 1
            self._results.append(result)
            
            for callback in self._result_callbacks:
                try:
                    callback(result)
                except Exception as e:
                    logger.error("Error in result callback: %s", e)
        
        return results
    
    async def _process_loop(self):
        """Boucle de traitement périodique"""
        while self._processing:
            try:
                # Finalisation des fenêtres expirées
                await self._finalize_expired_windows()
                
                # Nettoyage des anciens résultats
                self._cleanup_old_results()
                
                await asyncio.sleep(self.processing_interval)
                
            except Exception as e:
                logger.error("Error in aggregation processing loop: %s", e)
                self._stats["processing_errors"] += 1
    
    async def _finalize_expired_windows(self):
        """Finalise les fenêtres expirées"""
        for processor in self._processors.values():
            try:
                results = processor._finalize_completed_windows()
                
                for result in results:
                    self._stats["results_generated"] += 1
                    self._results.append(result)
                    
                    for callback in self._result_callbacks:
                        try:
                            callback(result)
                        except Exception as e:
                            logger.error("Error in result callback: %s", e)
                            
            except Exception as e:
                logger.error("Error finalizing windows for processor %s: %s", 
                           processor.rule.rule_id, e)
    
    def _cleanup_old_results(self):
        """Nettoie les anciens résultats"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        initial_count = len(self._results)
        self._results = [
            result for result in self._results
            if result.computed_at > cutoff_time
        ]
        
        cleaned_count = initial_count - len(self._results)
        if cleaned_count > 0:
            logger.debug("Cleaned %d old aggregation results", cleaned_count)
    
    def get_results(
        self, 
        rule_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AggregationResult]:
        """Récupère les résultats d'agrégation"""
        results = self._results.copy()
        
        # Filtrage par rule_id
        if rule_id:
            results = [r for r in results if r.rule_id == rule_id]
        
        # Filtrage par timestamp
        if since:
            results = [r for r in results if r.computed_at >= since]
        
        # Tri par timestamp (plus récent en premier)
        results.sort(key=lambda r: r.computed_at, reverse=True)
        
        return results[:limit]
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques temps réel"""
        now = datetime.now(timezone.utc)
        last_hour = now - timedelta(hours=1)
        
        # Compteurs par type d'événement (dernière heure)
        event_counts = defaultdict(int)
        recent_events = self._buffer.get_events_in_window(last_hour, now)
        
        for event in recent_events:
            event_type_base = event.type.split('.')[0]
            event_counts[event_type_base] += 1
        
        # Résultats récents
        recent_results = [
            r for r in self._results
            if r.computed_at >= last_hour
        ]
        
        return {
            "timestamp": now.isoformat(),
            "buffer_size": self._buffer.size(),
            "active_rules": len(self._rules),
            "recent_events": dict(event_counts),
            "recent_results_count": len(recent_results),
            "processing": self._processing,
            "stats": self._stats.copy()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques complètes"""
        return {
            "stats": self._stats.copy(),
            "buffer_size": self._buffer.size(),
            "rules_count": len(self._rules),
            "results_count": len(self._results),
            "processing": self._processing
        }


class EventProcessor:
    """Processeur d'événements de haut niveau avec agrégation"""
    
    def __init__(self, aggregator: EventAggregator):
        self.aggregator = aggregator
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Configuration des règles par défaut
        self._setup_default_rules()
        
        # Callbacks pour analytics
        self.aggregator.add_result_callback(self._handle_aggregation_result)
    
    def _setup_default_rules(self):
        """Configure les règles d'agrégation par défaut"""
        default_rules = [
            # Comptage des uploads de contenu par utilisateur
            AggregationRule(
                rule_id="content_uploads_per_user",
                name="Content Uploads per User",
                event_types=["content.uploaded"],
                aggregation_type=AggregationType.COUNT,
                group_by=["user_id"],
                window_size=3600  # 1 heure
            ),
            
            # Détections de violations par tenant
            AggregationRule(
                rule_id="violations_per_tenant",
                name="Protection Violations per Tenant",
                event_types=["protection.violation.detected"],
                aggregation_type=AggregationType.COUNT,
                group_by=["tenant_id"],
                window_size=1800  # 30 minutes
            ),
            
            # Revenus totaux par plateforme
            AggregationRule(
                rule_id="revenue_by_platform",
                name="Revenue by Platform",
                event_types=["monetization.revenue.detected"],
                aggregation_type=AggregationType.SUM,
                field_name="revenue_amount",
                group_by=["platform"],
                window_size=3600  # 1 heure
            ),
            
            # Erreurs système par composant
            AggregationRule(
                rule_id="errors_by_component",
                name="System Errors by Component",
                event_types=["system.error.occurred"],
                aggregation_type=AggregationType.COUNT,
                group_by=["component"],
                window_size=900  # 15 minutes
            )
        ]
        
        for rule in default_rules:
            self.aggregator.register_rule(rule)
    
    def _handle_aggregation_result(self, result: AggregationResult):
        """Traite les résultats d'agrégation"""
        try:
            # Alertes automatiques pour certains seuils
            if result.rule_id == "violations_per_tenant" and result.value > 10:
                logger.warning("High violation rate detected for tenant %s: %d violations", 
                             result.group_key, result.value)
            
            elif result.rule_id == "errors_by_component" and result.value > 5:
                logger.error("High error rate for component %s: %d errors", 
                           result.group_key, result.value)
            
            # Triggers pour handlers spécifiques
            handlers = self._event_handlers.get(result.rule_id, [])
            for handler in handlers:
                try:
                    handler(result)
                except Exception as e:
                    logger.error("Error in aggregation result handler: %s", e)
                    
        except Exception as e:
            logger.error("Error handling aggregation result: %s", e)
    
    def register_aggregation_handler(
        self, 
        rule_id: str, 
        handler: Callable[[AggregationResult], None]
    ):
        """Enregistre un handler pour les résultats d'une règle"""
        self._event_handlers[rule_id].append(handler)
    
    async def process_event(self, event: Event) -> List[AggregationResult]:
        """Point d'entrée principal pour traitement d'événements"""
        return await self.aggregator.process_event(event)


# Instance globale
default_aggregator = EventAggregator()
default_processor = EventProcessor(default_aggregator)
