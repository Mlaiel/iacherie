"""
⚡ Real-Time Feature Service - Enterprise MLOps
Expert ML Engineer + Data Engineering: Service features temps réel ultra-rapide

🎯 EXPERTISE DÉMONTRÉ:
- ML Engineer: Feature serving <10ms + cache intelligent
- Data Engineering: Pipeline temps réel + streaming
- Backend Senior: Architecture haute performance + monitoring
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque, defaultdict
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureType(Enum):
    """Types de features"""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    EMBEDDING = "embedding"
    TEXT = "text"
    BOOLEAN = "boolean"
    TIMESTAMP = "timestamp"

class ComputationMode(Enum):
    """Modes de calcul des features"""
    BATCH = "batch"
    STREAMING = "streaming"
    ON_DEMAND = "on_demand"
    HYBRID = "hybrid"

@dataclass
class FeatureDefinition:
    """Définition d'une feature"""
    name: str
    feature_type: FeatureType
    computation_mode: ComputationMode
    computation_function: Callable
    dependencies: List[str] = field(default_factory=list)
    ttl_seconds: int = 300  # Cache TTL
    aggregation_window: Optional[str] = None  # "1h", "1d", etc.
    default_value: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FeatureValue:
    """Valeur d'une feature avec métadonnées"""
    feature_name: str
    value: Any
    timestamp: datetime
    entity_id: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FeatureRequest:
    """Requête de features"""
    entity_id: str
    feature_names: List[str]
    timestamp: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FeatureResponse:
    """Réponse avec features"""
    entity_id: str
    features: Dict[str, FeatureValue]
    computation_time_ms: float
    cache_hits: List[str] = field(default_factory=list)
    cache_misses: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

class RealTimeFeatureService:
    """
    ⚡ Service Enterprise de Features Temps Réel
    
    Expertise ML Engineer + Data Engineering:
    - Serving ultra-rapide <10ms
    - Cache multi-niveau intelligent
    - Streaming features en temps réel
    - Auto-scaling et monitoring
    """
    
    def __init__(self, cache_size: int = 10000):
        self.feature_definitions: Dict[str, FeatureDefinition] = {}
        
        # Cache multi-niveau
        self.l1_cache: Dict[str, FeatureValue] = {}  # Cache mémoire ultra-rapide
        self.l2_cache: Dict[str, FeatureValue] = {}  # Cache avec TTL
        self.cache_size = cache_size
        
        # Streaming data pour features temps réel
        self.streaming_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Métriques performance
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_response_time": 0.0,
            "feature_computations": defaultdict(int),
            "error_count": 0
        }
        
        # Monitoring temps réel
        self.performance_buffer = deque(maxlen=1000)  # Buffer des dernières performances
        self.is_monitoring = False
    
    async def register_feature(self, feature_def: FeatureDefinition) -> bool:
        """
        Enregistre une définition de feature
        
        Expertise ML Engineer: Registry features avec validation
        """
        try:
            # Validation de la définition
            if not feature_def.name:
                raise ValueError("Feature name is required")
            
            if not callable(feature_def.computation_function):
                raise ValueError("Computation function must be callable")
            
            # Validation des dépendances
            for dep in feature_def.dependencies:
                if dep not in self.feature_definitions and dep != feature_def.name:
                    logger.warning(f"Dependency {dep} not found for feature {feature_def.name}")
            
            self.feature_definitions[feature_def.name] = feature_def
            logger.info(f"Registered feature: {feature_def.name} ({feature_def.feature_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register feature {feature_def.name}: {str(e)}")
            return False
    
    async def get_features(
        self,
        request: FeatureRequest,
        max_latency_ms: float = 10.0
    ) -> FeatureResponse:
        """
        Récupère des features avec contrainte de latence
        
        Expertise Backend Senior: Performance <10ms garantie
        """
        start_time = time.time()
        
        response = FeatureResponse(
            entity_id=request.entity_id,
            features={},
            computation_time_ms=0.0
        )
        
        try:
            # Traitement parallèle avec timeout
            feature_tasks = []
            
            for feature_name in request.feature_names:
                if feature_name in self.feature_definitions:
                    task = asyncio.create_task(
                        self._get_single_feature(
                            feature_name, 
                            request.entity_id, 
                            request.timestamp,
                            request.context
                        )
                    )
                    feature_tasks.append((feature_name, task))
                else:
                    response.errors.append(f"Feature {feature_name} not found")
            
            # Attendre toutes les features avec timeout
            timeout_seconds = max_latency_ms / 1000.0
            
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*[task for _, task in feature_tasks], return_exceptions=True),
                    timeout=timeout_seconds
                )
                
                # Traiter les résultats
                for i, (feature_name, _) in enumerate(feature_tasks):
                    result = results[i]
                    
                    if isinstance(result, Exception):
                        response.errors.append(f"Error computing {feature_name}: {str(result)}")
                        self.metrics["error_count"] += 1
                    elif result:
                        response.features[feature_name] = result
                        if result.metadata.get("cache_hit"):
                            response.cache_hits.append(feature_name)
                        else:
                            response.cache_misses.append(feature_name)
            
            except asyncio.TimeoutError:
                # Timeout - retourner features déjà calculées
                logger.warning(f"Feature request timeout for entity {request.entity_id}")
                for feature_name, task in feature_tasks:
                    if not task.done():
                        task.cancel()
                        response.errors.append(f"Timeout computing {feature_name}")
            
            # Métriques
            computation_time = (time.time() - start_time) * 1000
            response.computation_time_ms = computation_time
            
            self._update_metrics(response, computation_time)
            
            # Log performance si > seuil
            if computation_time > max_latency_ms:
                logger.warning(f"High latency: {computation_time:.2f}ms (target: {max_latency_ms}ms)")
            
            return response
            
        except Exception as e:
            computation_time = (time.time() - start_time) * 1000
            response.computation_time_ms = computation_time
            response.errors.append(f"Request processing error: {str(e)}")
            logger.error(f"Feature request failed for entity {request.entity_id}: {str(e)}")
            return response
    
    async def _get_single_feature(
        self,
        feature_name: str,
        entity_id: str,
        timestamp: Optional[datetime],
        context: Dict[str, Any]
    ) -> Optional[FeatureValue]:
        """Récupère une feature individuelle avec cache multi-niveau"""
        feature_def = self.feature_definitions[feature_name]
        current_time = timestamp or datetime.utcnow()
        
        # Clé de cache
        cache_key = self._generate_cache_key(feature_name, entity_id, context)
        
        # L1 Cache (ultra-rapide en mémoire)
        if cache_key in self.l1_cache:
            cached_value = self.l1_cache[cache_key]
            if self._is_cache_valid(cached_value, feature_def.ttl_seconds):
                cached_value.metadata["cache_hit"] = True
                cached_value.metadata["cache_level"] = "L1"
                self.metrics["cache_hits"] += 1
                return cached_value
        
        # L2 Cache (avec TTL)
        if cache_key in self.l2_cache:
            cached_value = self.l2_cache[cache_key]
            if self._is_cache_valid(cached_value, feature_def.ttl_seconds):
                # Promouvoir vers L1
                self.l1_cache[cache_key] = cached_value
                self._manage_l1_cache_size()
                
                cached_value.metadata["cache_hit"] = True
                cached_value.metadata["cache_level"] = "L2"
                self.metrics["cache_hits"] += 1
                return cached_value
        
        # Cache miss - calculer la feature
        self.metrics["cache_misses"] += 1
        self.metrics["feature_computations"][feature_name] += 1
        
        try:
            # Calculer selon le mode
            if feature_def.computation_mode == ComputationMode.STREAMING:
                feature_value = await self._compute_streaming_feature(
                    feature_def, entity_id, current_time, context
                )
            elif feature_def.computation_mode == ComputationMode.ON_DEMAND:
                feature_value = await self._compute_on_demand_feature(
                    feature_def, entity_id, current_time, context
                )
            else:
                feature_value = await self._compute_batch_feature(
                    feature_def, entity_id, current_time, context
                )
            
            if feature_value:
                feature_value.metadata["cache_hit"] = False
                feature_value.metadata["computation_mode"] = feature_def.computation_mode.value
                
                # Mise en cache
                self.l2_cache[cache_key] = feature_value
                self.l1_cache[cache_key] = feature_value
                self._manage_l1_cache_size()
            
            return feature_value
            
        except Exception as e:
            logger.error(f"Failed to compute feature {feature_name}: {str(e)}")
            # Retourner valeur par défaut si disponible
            if feature_def.default_value is not None:
                return FeatureValue(
                    feature_name=feature_name,
                    value=feature_def.default_value,
                    timestamp=current_time,
                    entity_id=entity_id,
                    confidence=0.0,
                    metadata={"fallback": True, "error": str(e)}
                )
            return None
    
    async def _compute_streaming_feature(
        self,
        feature_def: FeatureDefinition,
        entity_id: str,
        timestamp: datetime,
        context: Dict[str, Any]
    ) -> Optional[FeatureValue]:
        """
        Calcule une feature à partir des données streaming
        
        Expertise Data Engineering: Streaming temps réel
        """
        # Récupérer les données streaming récentes
        stream_key = f"{feature_def.name}_{entity_id}"
        recent_data = list(self.streaming_data.get(stream_key, []))
        
        if not recent_data:
            return None
        
        # Appliquer la fonction de calcul
        if asyncio.iscoroutinefunction(feature_def.computation_function):
            value = await feature_def.computation_function(recent_data, context)
        else:
            value = feature_def.computation_function(recent_data, context)
        
        return FeatureValue(
            feature_name=feature_def.name,
            value=value,
            timestamp=timestamp,
            entity_id=entity_id,
            metadata={"data_points": len(recent_data)}
        )
    
    async def _compute_on_demand_feature(
        self,
        feature_def: FeatureDefinition,
        entity_id: str,
        timestamp: datetime,
        context: Dict[str, Any]
    ) -> Optional[FeatureValue]:
        """Calcule une feature à la demande"""
        # Calcul direct avec le contexte fourni
        if asyncio.iscoroutinefunction(feature_def.computation_function):
            value = await feature_def.computation_function(entity_id, context)
        else:
            value = feature_def.computation_function(entity_id, context)
        
        return FeatureValue(
            feature_name=feature_def.name,
            value=value,
            timestamp=timestamp,
            entity_id=entity_id
        )
    
    async def _compute_batch_feature(
        self,
        feature_def: FeatureDefinition,
        entity_id: str,
        timestamp: datetime,
        context: Dict[str, Any]
    ) -> Optional[FeatureValue]:
        """Calcule une feature en mode batch (pré-calculé)"""
        # Dans un vrai système, ceci récupérerait des données pré-calculées
        # Simulation
        await asyncio.sleep(0.001)  # Simule latence base de données
        
        # Fonction de calcul simulée
        if asyncio.iscoroutinefunction(feature_def.computation_function):
            value = await feature_def.computation_function(entity_id, context)
        else:
            value = feature_def.computation_function(entity_id, context)
        
        return FeatureValue(
            feature_name=feature_def.name,
            value=value,
            timestamp=timestamp,
            entity_id=entity_id,
            metadata={"precomputed": True}
        )
    
    async def ingest_streaming_data(
        self,
        feature_name: str,
        entity_id: str,
        data_point: Any,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Ingère des données en streaming pour features temps réel
        
        Expertise Data Engineering: Ingestion haute fréquence
        """
        try:
            stream_key = f"{feature_name}_{entity_id}"
            
            data_entry = {
                "value": data_point,
                "timestamp": timestamp or datetime.utcnow(),
                "entity_id": entity_id
            }
            
            self.streaming_data[stream_key].append(data_entry)
            
            # Invalider le cache pour cette feature/entity
            await self._invalidate_cache(feature_name, entity_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to ingest streaming data: {str(e)}")
            return False
    
    async def batch_get_features(
        self,
        requests: List[FeatureRequest],
        max_latency_ms: float = 50.0
    ) -> List[FeatureResponse]:
        """
        Traitement batch de requêtes de features
        
        Expertise ML Engineer: Optimisation batch pour ML inference
        """
        # Traitement parallèle avec limite de concurrence
        semaphore = asyncio.Semaphore(100)  # Max 100 requêtes simultanées
        
        async def process_request(request):
            async with semaphore:
                return await self.get_features(request, max_latency_ms)
        
        tasks = [process_request(req) for req in requests]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrer les exceptions
        valid_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(f"Batch request {i} failed: {str(response)}")
                # Créer une réponse d'erreur
                error_response = FeatureResponse(
                    entity_id=requests[i].entity_id,
                    features={},
                    computation_time_ms=0.0,
                    errors=[str(response)]
                )
                valid_responses.append(error_response)
            else:
                valid_responses.append(response)
        
        return valid_responses
    
    def _generate_cache_key(
        self,
        feature_name: str,
        entity_id: str,
        context: Dict[str, Any]
    ) -> str:
        """Génère une clé de cache déterministe"""
        context_str = json.dumps(context, sort_keys=True) if context else ""
        cache_input = f"{feature_name}_{entity_id}_{context_str}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _is_cache_valid(self, feature_value: FeatureValue, ttl_seconds: int) -> bool:
        """Vérifie si une valeur en cache est encore valide"""
        age_seconds = (datetime.utcnow() - feature_value.timestamp).total_seconds()
        return age_seconds < ttl_seconds
    
    def _manage_l1_cache_size(self):
        """Gère la taille du cache L1 (LRU)"""
        if len(self.l1_cache) > self.cache_size:
            # Supprimer les plus anciens (approximation LRU)
            oldest_keys = sorted(
                self.l1_cache.keys(),
                key=lambda k: self.l1_cache[k].timestamp
            )[:len(self.l1_cache) - self.cache_size]
            
            for key in oldest_keys:
                del self.l1_cache[key]
    
    async def _invalidate_cache(self, feature_name: str, entity_id: str):
        """Invalide le cache pour une feature/entity"""
        # Invalidation approximative - supprimer les entrées correspondantes
        keys_to_remove = []
        
        for cache_key in self.l1_cache:
            feature_value = self.l1_cache[cache_key]
            if (feature_value.feature_name == feature_name and 
                feature_value.entity_id == entity_id):
                keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del self.l1_cache[key]
            if key in self.l2_cache:
                del self.l2_cache[key]
    
    def _update_metrics(self, response: FeatureResponse, computation_time: float):
        """Met à jour les métriques de performance"""
        self.metrics["total_requests"] += 1
        
        # Moyenne mobile du temps de réponse
        total_requests = self.metrics["total_requests"]
        current_avg = self.metrics["avg_response_time"]
        new_avg = ((current_avg * (total_requests - 1)) + computation_time) / total_requests
        self.metrics["avg_response_time"] = new_avg
        
        # Buffer de performance pour monitoring
        self.performance_buffer.append({
            "timestamp": datetime.utcnow(),
            "response_time_ms": computation_time,
            "cache_hits": len(response.cache_hits),
            "cache_misses": len(response.cache_misses),
            "errors": len(response.errors)
        })
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de performance détaillées"""
        # Métriques temps réel des dernières 5 minutes
        five_min_ago = datetime.utcnow() - timedelta(minutes=5)
        recent_performance = [
            p for p in self.performance_buffer 
            if p["timestamp"] > five_min_ago
        ]
        
        if recent_performance:
            recent_avg_latency = sum(p["response_time_ms"] for p in recent_performance) / len(recent_performance)
            recent_cache_hit_rate = sum(p["cache_hits"] for p in recent_performance) / max(
                sum(p["cache_hits"] + p["cache_misses"] for p in recent_performance), 1
            )
        else:
            recent_avg_latency = 0
            recent_cache_hit_rate = 0
        
        cache_hit_rate = 0
        if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0:
            cache_hit_rate = self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"])
        
        return {
            "total_requests": self.metrics["total_requests"],
            "overall_avg_response_time_ms": self.metrics["avg_response_time"],
            "recent_avg_response_time_ms": recent_avg_latency,
            "overall_cache_hit_rate": cache_hit_rate,
            "recent_cache_hit_rate": recent_cache_hit_rate,
            "l1_cache_size": len(self.l1_cache),
            "l2_cache_size": len(self.l2_cache),
            "registered_features": len(self.feature_definitions),
            "streaming_features": len(self.streaming_data),
            "error_count": self.metrics["error_count"],
            "feature_computations": dict(self.metrics["feature_computations"])
        }
    
    async def warmup_cache(self, entity_ids: List[str], feature_names: List[str]) -> Dict[str, int]:
        """
        Préchauffe le cache pour des entités et features spécifiques
        
        Expertise ML Engineer: Optimisation warm-up pour inference
        """
        warmup_stats = {"success": 0, "failed": 0}
        
        for entity_id in entity_ids:
            request = FeatureRequest(
                entity_id=entity_id,
                feature_names=feature_names
            )
            
            try:
                response = await self.get_features(request, max_latency_ms=1000.0)  # Latence relaxée pour warmup
                if not response.errors:
                    warmup_stats["success"] += 1
                else:
                    warmup_stats["failed"] += 1
            except Exception as e:
                logger.error(f"Warmup failed for entity {entity_id}: {str(e)}")
                warmup_stats["failed"] += 1
        
        logger.info(f"Cache warmup completed: {warmup_stats}")
        return warmup_stats

# Features exemple pour démo
async def user_age_feature(entity_id: str, context: Dict[str, Any]) -> int:
    """Feature age utilisateur"""
    return hash(entity_id) % 80 + 18  # Simulation

async def user_activity_score(recent_data: List[Dict], context: Dict[str, Any]) -> float:
    """Score d'activité basé sur données streaming"""
    if not recent_data:
        return 0.0
    
    # Score basé sur la fréquence d'activité
    return min(len(recent_data) / 10.0, 1.0)

async def user_preferences_embedding(entity_id: str, context: Dict[str, Any]) -> List[float]:
    """Embedding des préférences utilisateur"""
    # Simulation d'un embedding 128D
    seed = hash(entity_id)
    return [(seed + i) % 100 / 100.0 for i in range(128)]

# Exemple d'utilisation
async def demo_realtime_features():
    """Démo du service de features temps réel"""
    service = RealTimeFeatureService()
    
    # Enregistrer des features
    await service.register_feature(FeatureDefinition(
        name="user_age",
        feature_type=FeatureType.NUMERIC,
        computation_mode=ComputationMode.ON_DEMAND,
        computation_function=user_age_feature,
        ttl_seconds=3600
    ))
    
    await service.register_feature(FeatureDefinition(
        name="activity_score",
        feature_type=FeatureType.NUMERIC,
        computation_mode=ComputationMode.STREAMING,
        computation_function=user_activity_score,
        ttl_seconds=60
    ))
    
    await service.register_feature(FeatureDefinition(
        name="preferences_embedding",
        feature_type=FeatureType.EMBEDDING,
        computation_mode=ComputationMode.ON_DEMAND,
        computation_function=user_preferences_embedding,
        ttl_seconds=1800
    ))
    
    # Simuler des données streaming
    for i in range(5):
        await service.ingest_streaming_data("activity_score", "user_123", f"action_{i}")
    
    # Requête de features
    request = FeatureRequest(
        entity_id="user_123",
        feature_names=["user_age", "activity_score", "preferences_embedding"]
    )
    
    # Test performance avec contrainte latence
    response = await service.get_features(request, max_latency_ms=5.0)
    
    print(f"Feature response:")
    print(f"  Entity: {response.entity_id}")
    print(f"  Computation time: {response.computation_time_ms:.2f}ms")
    print(f"  Features retrieved: {len(response.features)}")
    print(f"  Cache hits: {response.cache_hits}")
    print(f"  Cache misses: {response.cache_misses}")
    print(f"  Errors: {response.errors}")
    
    # Test seconde requête (devrait utiliser le cache)
    response2 = await service.get_features(request, max_latency_ms=5.0)
    print(f"\nSecond request (cached):")
    print(f"  Computation time: {response2.computation_time_ms:.2f}ms")
    print(f"  Cache hits: {response2.cache_hits}")
    
    # Métriques de performance
    metrics = await service.get_performance_metrics()
    print(f"\nPerformance metrics:")
    print(f"  Total requests: {metrics['total_requests']}")
    print(f"  Cache hit rate: {metrics['overall_cache_hit_rate']:.2%}")
    print(f"  Avg response time: {metrics['overall_avg_response_time_ms']:.2f}ms")

if __name__ == "__main__":
    asyncio.run(demo_realtime_features())