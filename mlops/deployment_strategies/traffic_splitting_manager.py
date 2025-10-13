"""
🚦 Traffic Splitting Manager - Enterprise MLOps
Expert Microservices + DevOps: Gestionnaire répartition trafic intelligent

🎯 EXPERTISE DÉMONTRÉ:
- Microservices: Load balancing + circuit breakers avancés
- DevOps: Traffic management + monitoring temps réel
- Backend Senior: Performance <50ms + architecture distribuée
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SplitStrategy(Enum):
    """Stratégies de répartition du trafic"""
    PERCENTAGE = "percentage"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RESPONSE_TIME = "response_time"
    GEOGRAPHIC = "geographic"
    USER_BASED = "user_based"

class TrafficRule(Enum):
    """Règles de routage du trafic"""
    HEADER_BASED = "header_based"
    IP_BASED = "ip_based"
    USER_AGENT = "user_agent"
    COOKIE_BASED = "cookie_based"
    RANDOM = "random"

@dataclass
class TrafficTarget:
    """Cible de trafic (version/environnement)"""
    id: str
    version: str
    endpoint: str
    weight: float = 0.0
    max_capacity: int = 1000
    current_load: int = 0
    health_status: str = "unknown"
    response_time_ms: float = 0.0
    error_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrafficSplit:
    """Configuration de répartition du trafic"""
    id: str
    service_name: str
    strategy: SplitStrategy
    targets: List[TrafficTarget]
    rules: List[Dict[str, Any]] = field(default_factory=list)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TrafficMetrics:
    """Métriques de trafic"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    requests_per_target: Dict[str, int] = field(default_factory=dict)
    error_rates_per_target: Dict[str, float] = field(default_factory=dict)

class TrafficSplittingManager:
    """
    🚦 Gestionnaire Enterprise de Répartition de Trafic
    
    Expertise Microservices + DevOps:
    - Load balancing intelligent avec métriques temps réel
    - Circuit breakers automatiques
    - Stratégies de routage avancées
    - Monitoring et analytics continus
    """
    
    def __init__(self):
        self.traffic_splits: Dict[str, TrafficSplit] = {}
        self.active_sessions: Dict[str, str] = {}  # session_id -> target_id
        self.traffic_history: List[Dict] = []
        self.circuit_breakers: Dict[str, Dict] = {}
        
        # Métriques en temps réel
        self.metrics_cache: Dict[str, TrafficMetrics] = {}
        self.request_logs: List[Dict] = []
        
        # Configuration
        self.circuit_breaker_config = {
            "failure_threshold": 5,
            "timeout_seconds": 60,
            "half_open_max_calls": 3
        }
    
    async def create_traffic_split(
        self,
        service_name: str,
        targets: List[TrafficTarget],
        strategy: SplitStrategy = SplitStrategy.PERCENTAGE,
        rules: Optional[List[Dict]] = None
    ) -> str:
        """
        Crée une nouvelle configuration de répartition
        
        Expertise DevOps: Configuration traffic management
        """
        split_id = f"split_{service_name}_{int(time.time())}"
        
        # Validation des cibles
        total_weight = sum(target.weight for target in targets)
        if abs(total_weight - 100.0) > 0.01:  # Tolérance pour erreurs floating point
            raise ValueError(f"Total weight must be 100%, got {total_weight}%")
        
        # Créer la configuration
        traffic_split = TrafficSplit(
            id=split_id,
            service_name=service_name,
            strategy=strategy,
            targets=targets,
            rules=rules or []
        )
        
        self.traffic_splits[split_id] = traffic_split
        
        # Initialiser circuit breakers pour chaque cible
        for target in targets:
            self.circuit_breakers[target.id] = {
                "state": "closed",  # closed, open, half_open
                "failure_count": 0,
                "last_failure_time": None,
                "half_open_calls": 0
            }
        
        logger.info(f"Created traffic split {split_id} for service {service_name}")
        return split_id
    
    async def route_request(
        self,
        service_name: str,
        request_context: Dict[str, Any]
    ) -> Optional[TrafficTarget]:
        """
        Route une requête vers la cible appropriée
        
        Expertise Microservices: Routage intelligent avec circuit breakers
        """
        start_time = time.time()
        
        # Trouver la configuration de split active
        active_split = None
        for split in self.traffic_splits.values():
            if split.service_name == service_name and split.active:
                active_split = split
                break
        
        if not active_split:
            logger.warning(f"No active traffic split found for service {service_name}")
            return None
        
        try:
            # Sélectionner la cible selon la stratégie
            target = await self._select_target(active_split, request_context)
            
            if not target:
                return None
            
            # Vérifier circuit breaker
            if not await self._check_circuit_breaker(target.id):
                # Circuit ouvert - essayer la cible suivante
                logger.warning(f"Circuit breaker open for target {target.id}")
                return await self._select_fallback_target(active_split, target.id)
            
            # Enregistrer la requête
            routing_time = (time.time() - start_time) * 1000
            await self._log_request(target.id, request_context, routing_time)
            
            return target
            
        except Exception as e:
            logger.error(f"Failed to route request for {service_name}: {str(e)}")
            return None
    
    async def _select_target(
        self,
        traffic_split: TrafficSplit,
        request_context: Dict[str, Any]
    ) -> Optional[TrafficTarget]:
        """Sélectionne la cible selon la stratégie configurée"""
        
        # Filtrer les cibles disponibles
        available_targets = [
            t for t in traffic_split.targets 
            if t.health_status == "healthy" and t.weight > 0
        ]
        
        if not available_targets:
            logger.warning(f"No healthy targets available for {traffic_split.service_name}")
            return None
        
        # Appliquer les règles de routage d'abord
        rule_target = await self._apply_routing_rules(traffic_split.rules, request_context, available_targets)
        if rule_target:
            return rule_target
        
        # Appliquer la stratégie de split
        if traffic_split.strategy == SplitStrategy.PERCENTAGE:
            return await self._select_by_percentage(available_targets)
        
        elif traffic_split.strategy == SplitStrategy.WEIGHTED_ROUND_ROBIN:
            return await self._select_by_weighted_round_robin(available_targets)
        
        elif traffic_split.strategy == SplitStrategy.LEAST_CONNECTIONS:
            return await self._select_by_least_connections(available_targets)
        
        elif traffic_split.strategy == SplitStrategy.RESPONSE_TIME:
            return await self._select_by_response_time(available_targets)
        
        else:
            # Par défaut, sélection aléatoire pondérée
            return await self._select_by_percentage(available_targets)
    
    async def _apply_routing_rules(
        self,
        rules: List[Dict[str, Any]],
        request_context: Dict[str, Any],
        targets: List[TrafficTarget]
    ) -> Optional[TrafficTarget]:
        """Applique les règles de routage spécifiques"""
        
        for rule in rules:
            rule_type = rule.get("type")
            
            if rule_type == "header_based":
                header_name = rule.get("header")
                header_value = request_context.get("headers", {}).get(header_name)
                target_mapping = rule.get("mapping", {})
                
                if header_value in target_mapping:
                    target_id = target_mapping[header_value]
                    for target in targets:
                        if target.id == target_id:
                            return target
            
            elif rule_type == "user_based":
                user_id = request_context.get("user_id")
                if user_id:
                    # Routage sticky basé sur hash de user_id
                    target_index = hash(user_id) % len(targets)
                    return targets[target_index]
            
            elif rule_type == "geographic":
                user_region = request_context.get("region")
                target_mapping = rule.get("region_mapping", {})
                
                if user_region in target_mapping:
                    target_id = target_mapping[user_region]
                    for target in targets:
                        if target.id == target_id:
                            return target
        
        return None
    
    async def _select_by_percentage(self, targets: List[TrafficTarget]) -> TrafficTarget:
        """Sélection aléatoire pondérée par pourcentage"""
        import random
        
        total_weight = sum(t.weight for t in targets)
        random_value = random.uniform(0, total_weight)
        
        cumulative_weight = 0
        for target in targets:
            cumulative_weight += target.weight
            if random_value <= cumulative_weight:
                return target
        
        # Fallback sur le dernier
        return targets[-1]
    
    async def _select_by_weighted_round_robin(self, targets: List[TrafficTarget]) -> TrafficTarget:
        """Round robin pondéré"""
        # Simulation simple - en production, maintenir des compteurs
        min_load_ratio = float('inf')
        best_target = targets[0]
        
        for target in targets:
            load_ratio = target.current_load / max(target.weight, 1)
            if load_ratio < min_load_ratio:
                min_load_ratio = load_ratio
                best_target = target
        
        return best_target
    
    async def _select_by_least_connections(self, targets: List[TrafficTarget]) -> TrafficTarget:
        """Sélection par moins de connexions"""
        return min(targets, key=lambda t: t.current_load)
    
    async def _select_by_response_time(self, targets: List[TrafficTarget]) -> TrafficTarget:
        """Sélection par temps de réponse"""
        return min(targets, key=lambda t: t.response_time_ms)
    
    async def _check_circuit_breaker(self, target_id: str) -> bool:
        """Vérifie l'état du circuit breaker pour une cible"""
        breaker = self.circuit_breakers.get(target_id)
        if not breaker:
            return True
        
        if breaker["state"] == "closed":
            return True
        
        elif breaker["state"] == "open":
            # Vérifier si on peut passer en half-open
            if breaker["last_failure_time"]:
                elapsed = time.time() - breaker["last_failure_time"]
                if elapsed > self.circuit_breaker_config["timeout_seconds"]:
                    breaker["state"] = "half_open"
                    breaker["half_open_calls"] = 0
                    return True
            return False
        
        elif breaker["state"] == "half_open":
            # Limiter les appels en half-open
            if breaker["half_open_calls"] < self.circuit_breaker_config["half_open_max_calls"]:
                breaker["half_open_calls"] += 1
                return True
            return False
        
        return False
    
    async def _select_fallback_target(
        self,
        traffic_split: TrafficSplit,
        failed_target_id: str
    ) -> Optional[TrafficTarget]:
        """Sélectionne une cible de fallback"""
        fallback_targets = [
            t for t in traffic_split.targets
            if t.id != failed_target_id and t.health_status == "healthy"
        ]
        
        if fallback_targets:
            return await self._select_by_percentage(fallback_targets)
        
        return None
    
    async def report_request_result(
        self,
        target_id: str,
        success: bool,
        response_time_ms: float,
        error_message: Optional[str] = None
    ) -> None:
        """
        Rapporte le résultat d'une requête pour mise à jour des métriques
        
        Expertise Backend Senior: Feedback loop pour optimisation
        """
        # Mettre à jour circuit breaker
        breaker = self.circuit_breakers.get(target_id)
        if breaker:
            if success:
                # Reset du circuit breaker
                if breaker["state"] == "half_open":
                    breaker["state"] = "closed"
                breaker["failure_count"] = 0
            else:
                # Incrémenter les échecs
                breaker["failure_count"] += 1
                breaker["last_failure_time"] = time.time()
                
                # Ouvrir le circuit si seuil dépassé
                if breaker["failure_count"] >= self.circuit_breaker_config["failure_threshold"]:
                    breaker["state"] = "open"
                    logger.warning(f"Circuit breaker opened for target {target_id}")
        
        # Mettre à jour les métriques de la cible
        await self._update_target_metrics(target_id, success, response_time_ms)
        
        # Log pour analytics
        self.request_logs.append({
            "timestamp": datetime.utcnow(),
            "target_id": target_id,
            "success": success,
            "response_time_ms": response_time_ms,
            "error_message": error_message
        })
        
        # Nettoyer les anciens logs
        if len(self.request_logs) > 10000:
            self.request_logs = self.request_logs[-5000:]
    
    async def update_traffic_weights(
        self,
        split_id: str,
        new_weights: Dict[str, float]
    ) -> bool:
        """
        Met à jour les poids de répartition du trafic
        
        Expertise DevOps: Gestion dynamique traffic splitting
        """
        if split_id not in self.traffic_splits:
            return False
        
        traffic_split = self.traffic_splits[split_id]
        
        # Validation des nouveaux poids
        total_weight = sum(new_weights.values())
        if abs(total_weight - 100.0) > 0.01:
            raise ValueError(f"Total weight must be 100%, got {total_weight}%")
        
        # Appliquer les nouveaux poids
        for target in traffic_split.targets:
            if target.id in new_weights:
                old_weight = target.weight
                target.weight = new_weights[target.id]
                logger.info(f"Updated weight for target {target.id}: {old_weight}% -> {target.weight}%")
        
        traffic_split.updated_at = datetime.utcnow()
        
        # Log le changement
        self.traffic_history.append({
            "timestamp": datetime.utcnow(),
            "split_id": split_id,
            "action": "weight_update",
            "new_weights": new_weights.copy()
        })
        
        return True
    
    async def get_traffic_metrics(self, split_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les métriques de trafic pour un split"""
        if split_id not in self.traffic_splits:
            return None
        
        traffic_split = self.traffic_splits[split_id]
        
        # Calculer métriques récentes (dernière heure)
        recent_logs = [
            log for log in self.request_logs
            if (datetime.utcnow() - log["timestamp"]).total_seconds() < 3600
        ]
        
        metrics = {
            "split_id": split_id,
            "service_name": traffic_split.service_name,
            "total_requests": len(recent_logs),
            "successful_requests": sum(1 for log in recent_logs if log["success"]),
            "failed_requests": sum(1 for log in recent_logs if not log["success"]),
            "targets": {}
        }
        
        # Métriques par cible
        for target in traffic_split.targets:
            target_logs = [log for log in recent_logs if log["target_id"] == target.id]
            
            if target_logs:
                response_times = [log["response_time_ms"] for log in target_logs]
                success_count = sum(1 for log in target_logs if log["success"])
                
                metrics["targets"][target.id] = {
                    "requests": len(target_logs),
                    "success_rate": success_count / len(target_logs),
                    "avg_response_time": sum(response_times) / len(response_times),
                    "current_weight": target.weight,
                    "circuit_breaker_state": self.circuit_breakers.get(target.id, {}).get("state", "unknown")
                }
            else:
                metrics["targets"][target.id] = {
                    "requests": 0,
                    "success_rate": 0.0,
                    "avg_response_time": 0.0,
                    "current_weight": target.weight,
                    "circuit_breaker_state": self.circuit_breakers.get(target.id, {}).get("state", "unknown")
                }
        
        return metrics
    
    async def _update_target_metrics(
        self,
        target_id: str,
        success: bool,
        response_time_ms: float
    ) -> None:
        """Met à jour les métriques en temps réel d'une cible"""
        # Trouver la cible et mettre à jour ses métriques
        for split in self.traffic_splits.values():
            for target in split.targets:
                if target.id == target_id:
                    # Moyenne mobile simple des temps de réponse
                    alpha = 0.1  # Facteur de lissage
                    target.response_time_ms = (
                        alpha * response_time_ms + 
                        (1 - alpha) * target.response_time_ms
                    )
                    
                    # Mise à jour taux d'erreur (moyenne mobile)
                    error_rate_delta = 0.0 if success else 1.0
                    target.error_rate = (
                        alpha * error_rate_delta + 
                        (1 - alpha) * target.error_rate
                    )
                    break
    
    async def _log_request(
        self,
        target_id: str,
        request_context: Dict[str, Any],
        routing_time_ms: float
    ) -> None:
        """Log une requête pour analytics"""
        if routing_time_ms > 50:  # Plus de 50ms
            logger.warning(f"Slow traffic routing: {routing_time_ms:.2f}ms for target {target_id}")

# Exemple d'utilisation
async def demo_traffic_splitting():
    """Démo du gestionnaire de répartition de trafic"""
    manager = TrafficSplittingManager()
    
    # Créer des cibles
    targets = [
        TrafficTarget(
            id="v1_target",
            version="v1.0.0",
            endpoint="http://service-v1:8080",
            weight=80.0,
            health_status="healthy"
        ),
        TrafficTarget(
            id="v2_target", 
            version="v2.0.0",
            endpoint="http://service-v2:8080",
            weight=20.0,
            health_status="healthy"
        )
    ]
    
    # Créer un split
    split_id = await manager.create_traffic_split(
        "user-service",
        targets,
        SplitStrategy.PERCENTAGE
    )
    
    print(f"Created traffic split: {split_id}")
    
    # Simuler quelques requêtes
    for i in range(10):
        request_context = {
            "user_id": f"user_{i}",
            "headers": {"x-version": "v2" if i % 5 == 0 else "v1"}
        }
        
        target = await manager.route_request("user-service", request_context)
        if target:
            # Simuler réponse
            success = i % 7 != 0  # Échouer 1 requête sur 7
            response_time = 45.0 + (i * 10)
            
            await manager.report_request_result(
                target.id, success, response_time
            )
            
            print(f"Request {i}: routed to {target.version} ({'✓' if success else '✗'})")
    
    # Métriques
    metrics = await manager.get_traffic_metrics(split_id)
    print(f"\nTraffic metrics:")
    print(f"  Total requests: {metrics['total_requests']}")
    print(f"  Success rate: {metrics['successful_requests'] / max(1, metrics['total_requests']):.1%}")
    
    for target_id, target_metrics in metrics["targets"].items():
        print(f"  {target_id}: {target_metrics['requests']} requests, {target_metrics['success_rate']:.1%} success")

if __name__ == "__main__":
    asyncio.run(demo_traffic_splitting())