# WARNING: Potential SQL injection risk - use parameterized queries
"""
🌍 Multi-Region Discovery Enterprise - IA Chéries
==============================================
Discovery multi-région pour deployment global.
Cross-region service discovery + latency optimization + failover.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Service Discovery
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de
"""

import asyncio
import time
import logging
import json
import math
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import statistics

from .distributed_service_registry import ServiceInstance, ServiceStatus

logger = logging.getLogger(__name__)

class Region(Enum):
    """Régions géographiques supportées"""
    US_EAST_1 = "us-east-1"
    US_WEST_1 = "us-west-1"
    US_WEST_2 = "us-west-2"
    EU_WEST_1 = "eu-west-1"
    EU_CENTRAL_1 = "eu-central-1"
    AP_SOUTHEAST_1 = "ap-southeast-1"
    AP_NORTHEAST_1 = "ap-northeast-1"
    GLOBAL = "global"

class FailoverStrategy(Enum):
    """Stratégies de failover"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    GRADUAL = "gradual"
    IMMEDIATE = "immediate"

class DataLocalityLevel(Enum):
    """Niveaux de localisation des données"""
    STRICT = "strict"  # Données doivent rester dans la région
    PREFERRED = "preferred"  # Préférence pour la région, failover autorisé
    FLEXIBLE = "flexible"  # Aucune restriction

@dataclass
class RegionConfig:
    """Configuration d'une région"""
    region_id: str
    region_name: str
    coordinates: Tuple[float, float]  # (latitude, longitude)
    data_locality_level: DataLocalityLevel = DataLocalityLevel.PREFERRED
    allowed_failover_regions: List[str] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)
    cost_factor: float = 1.0  # Facteur de coût relatif
    capacity_limit: Optional[int] = None

@dataclass
class CrossRegionRequest:
    """Requête de découverte cross-région"""
    service_name: str
    user_location: Optional[str] = None
    user_region: Optional[str] = None
    preferred_regions: List[str] = field(default_factory=list)
    latency_requirement: Optional[float] = None  # ms
    data_locality_required: bool = False
    compliance_requirements: List[str] = field(default_factory=list)
    failover_allowed: bool = True

@dataclass
class CrossRegionResult:
    """Résultat de découverte cross-région"""
    success: bool
    selected_instances: List[ServiceInstance] = field(default_factory=list)
    selected_region: Optional[str] = None
    latency_estimate: Optional[float] = None
    failover_applied: bool = False
    compliance_satisfied: bool = True
    cost_estimate: float = 0.0
    errors: List[str] = field(default_factory=list)

@dataclass
class TrafficPatterns:
    """Patterns de trafic pour optimisation"""
    service_name: str
    region_traffic: Dict[str, float] = field(default_factory=dict)  # région -> pourcentage
    peak_hours: Dict[str, List[int]] = field(default_factory=dict)  # région -> heures
    latency_requirements: Dict[str, float] = field(default_factory=dict)  # région -> ms
    data_sensitivity: Dict[str, DataLocalityLevel] = field(default_factory=dict)

@dataclass
class LatencyOptimization:
    """Résultat d'optimisation de latence"""
    optimized_placement: Dict[str, List[str]]  # service -> régions recommandées
    expected_latency_improvement: float  # pourcentage
    migration_recommendations: List[Dict] = field(default_factory=list)
    cost_impact: float = 0.0

@dataclass
class FailoverResult:
    """Résultat de failover de région"""
    success: bool
    failed_region: str
    target_regions: List[str] = field(default_factory=list)
    affected_services: List[str] = field(default_factory=list)
    traffic_redirected: bool = False
    data_migration_required: bool = False
    estimated_recovery_time: Optional[float] = None  # seconds

@dataclass
class LocalityRule:
    """Règle de localisation des données"""
    rule_id: str
    service_pattern: str  # regex pour matcher les services
    required_regions: List[str] = field(default_factory=list)
    forbidden_regions: List[str] = field(default_factory=list)
    locality_level: DataLocalityLevel = DataLocalityLevel.PREFERRED
    compliance_tags: List[str] = field(default_factory=list)

@dataclass
class LocalityResult:
    """Résultat d'enforcement des règles de localité"""
    success: bool
    enforced_rules: List[str] = field(default_factory=list)
    violations: List[Dict] = field(default_factory=list)
    migrations_required: List[Dict] = field(default_factory=list)

@dataclass
class GlobalHealthStatus:
    """État de santé global des services"""
    timestamp: float = field(default_factory=time.time)
    region_health: Dict[str, float] = field(default_factory=dict)  # région -> score (0-1)
    service_health: Dict[str, Dict[str, float]] = field(default_factory=dict)  # service -> région -> score
    cross_region_latency: Dict[str, Dict[str, float]] = field(default_factory=dict)  # région -> région -> latency
    total_instances: int = 0
    healthy_instances: int = 0
    degraded_regions: List[str] = field(default_factory=list)

class RegionCoordinator:
    """Coordinateur des régions"""
    
    def __init__(self):
        self.regions: Dict[str, RegionConfig] = self._initialize_regions()
        self.region_registries: Dict[str, Dict] = {}  # région -> registry local
        self.cross_region_cache: Dict[str, Dict] = {}
        self.cache_ttl = 60  # seconds
    
    def _initialize_regions(self) -> Dict[str, RegionConfig]:
        """Initialiser les configurations de régions"""
        return {
            Region.US_EAST_1.value: RegionConfig(
                region_id=Region.US_EAST_1.value,
                region_name="US East (N. Virginia)",
                coordinates=(39.0458, -77.4573),
                allowed_failover_regions=[Region.US_WEST_1.value, Region.US_WEST_2.value],
                compliance_requirements=["SOC2", "HIPAA"],
                cost_factor=1.0
            ),
            Region.US_WEST_1.value: RegionConfig(
                region_id=Region.US_WEST_1.value,
                region_name="US West (N. California)",
                coordinates=(37.7749, -122.4194),
                allowed_failover_regions=[Region.US_EAST_1.value, Region.US_WEST_2.value],
                compliance_requirements=["SOC2"],
                cost_factor=1.1
            ),
            Region.EU_WEST_1.value: RegionConfig(
                region_id=Region.EU_WEST_1.value,
                region_name="Europe (Ireland)",
                coordinates=(53.3498, -6.2603),
                allowed_failover_regions=[Region.EU_CENTRAL_1.value],
                compliance_requirements=["GDPR", "ISO27001"],
                cost_factor=1.2
            ),
            Region.AP_SOUTHEAST_1.value: RegionConfig(
                region_id=Region.AP_SOUTHEAST_1.value,
                region_name="Asia Pacific (Singapore)",
                coordinates=(1.3521, 103.8198),
                allowed_failover_regions=[Region.AP_NORTHEAST_1.value],
                compliance_requirements=["PDPA"],
                cost_factor=1.3
            )
        }
    
    async def register_region_service(self, region_id: str, service: ServiceInstance) -> bool:
        """Enregistrer un service dans une région"""
        try:
            if region_id not in self.region_registries:
                self.region_registries[region_id] = {}
            
            service_name = service.service_name
            if service_name not in self.region_registries[region_id]:
                self.region_registries[region_id][service_name] = []
            
            self.region_registries[region_id][service_name].append(service)
            
            logger.info(f"✅ Service {service.service_id} enregistré dans région {region_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur enregistrement service région: {e}")
            return False
    
    async def get_region_services(self, region_id: str, service_name: str) -> List[ServiceInstance]:
        """Obtenir les services d'une région"""
        try:
            if region_id in self.region_registries:
                return self.region_registries[region_id].get(service_name, [])
            return []
        except Exception as e:
            logger.error(f"Erreur récupération services région: {e}")
            return []
    
    async def get_all_region_services(self, service_name: str) -> Dict[str, List[ServiceInstance]]:
        """Obtenir un service de toutes les régions"""
        result = {}
        for region_id, registry in self.region_registries.items():
            services = registry.get(service_name, [])
            if services:
                result[region_id] = services
        return result
    
    def calculate_distance(self, region1: str, region2: str) -> float:
        """Calculer la distance entre deux régions"""
        if region1 not in self.regions or region2 not in self.regions:
            return float('inf')
        
        coord1 = self.regions[region1].coordinates
        coord2 = self.regions[region2].coordinates
        
        # Formule de Haversine pour distance géographique
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Rayon de la Terre en km
        r = 6371
        return c * r
    
    def estimate_latency(self, region1: str, region2: str) -> float:
        """Estimer la latence entre deux régions"""
        if region1 == region2:
            return 5.0  # Latence intra-région
        
        distance = self.calculate_distance(region1, region2)
        
        # Approximation: ~0.1ms par 100km + overhead réseau
        base_latency = (distance / 100) * 0.1
        network_overhead = 10.0  # ms
        
        return base_latency + network_overhead

class LatencyOptimizer:
    """Optimiseur de latence cross-région"""
    
    def __init__(self, region_coordinator: RegionCoordinator):
        self.region_coordinator = region_coordinator
        self.latency_measurements: Dict[str, Dict[str, List[float]]] = {}  # région1 -> région2 -> [latencies]
        self.optimization_history: List[Dict] = []
    
    async def optimize_cross_region_latency(self, traffic_patterns: TrafficPatterns) -> LatencyOptimization:
        """Optimization latence cross-region basée sur traffic patterns"""
        try:
            service_name = traffic_patterns.service_name
            optimized_placement = {}
            migration_recommendations = []
            
            # Analyser les patterns de trafic
            total_traffic = sum(traffic_patterns.region_traffic.values())
            if total_traffic == 0:
                return LatencyOptimization(optimized_placement={}, expected_latency_improvement=0.0)
            
            # Calculer le placement optimal pour chaque région source
            for source_region, traffic_percentage in traffic_patterns.region_traffic.items():
                if traffic_percentage > 0:
                    optimal_regions = await self._find_optimal_target_regions(
                        source_region, 
                        traffic_patterns,
                        traffic_percentage / total_traffic
                    )
                    optimized_placement[source_region] = optimal_regions
            
            # Calculer l'amélioration de latence attendue
            current_latency = await self._calculate_current_weighted_latency(traffic_patterns)
            optimized_latency = await self._calculate_optimized_weighted_latency(
                traffic_patterns, optimized_placement
            )
            
            improvement = max(0, (current_latency - optimized_latency) / current_latency * 100)
            
            # Générer les recommandations de migration
            migration_recommendations = await self._generate_migration_recommendations(
                service_name, optimized_placement
            )
            
            # Estimer l'impact sur les coûts
            cost_impact = await self._estimate_cost_impact(optimized_placement, traffic_patterns)
            
            result = LatencyOptimization(
                optimized_placement=optimized_placement,
                expected_latency_improvement=improvement,
                migration_recommendations=migration_recommendations,
                cost_impact=cost_impact
            )
            
            # Sauvegarder dans l'historique
            self.optimization_history.append({
                'timestamp': time.time(),
                'service_name': service_name,
                'optimization_result': result,
                'traffic_patterns': traffic_patterns
            })
            
            logger.info(f"🎯 Optimisation latence {service_name}: {improvement:.1f}% amélioration attendue")
            return result
            
        except Exception as e:
            logger.error(f"Erreur optimisation latence: {e}")
            return LatencyOptimization(optimized_placement={}, expected_latency_improvement=0.0)
    
    async def _find_optimal_target_regions(self, source_region: str, traffic_patterns: TrafficPatterns, 
                                         traffic_weight: float) -> List[str]:
        """Trouver les régions cibles optimales pour une région source"""
        candidates = []
        
        # Évaluer chaque région cible possible
        for target_region in self.region_coordinator.regions.keys():
            if target_region == source_region:
                continue
            
            # Calculer le score basé sur latence, coût et capacité
            latency = self.region_coordinator.estimate_latency(source_region, target_region)
            cost_factor = self.region_coordinator.regions[target_region].cost_factor
            
            # Score combiné (plus bas = meilleur)
            score = latency * cost_factor * traffic_weight
            
            candidates.append((target_region, score))
        
        # Trier par score et retourner les 2 meilleures options
        candidates.sort(key=lambda x: x[1])
        return [region for region, score in candidates[:2]]
    
    async def _calculate_current_weighted_latency(self, traffic_patterns: TrafficPatterns) -> float:
        """Calculer la latence moyenne pondérée actuelle"""
        total_weighted_latency = 0.0
        total_weight = 0.0
        
        for source_region, traffic_percentage in traffic_patterns.region_traffic.items():
            # Supposer que le trafic va vers la région la plus proche actuellement
            min_latency = float('inf')
            for target_region in self.region_coordinator.regions.keys():
                if target_region != source_region:
                    latency = self.region_coordinator.estimate_latency(source_region, target_region)
                    min_latency = min(min_latency, latency)
            
            if min_latency != float('inf'):
                total_weighted_latency += min_latency * traffic_percentage
                total_weight += traffic_percentage
        
        return total_weighted_latency / total_weight if total_weight > 0 else 0.0
    
    async def _calculate_optimized_weighted_latency(self, traffic_patterns: TrafficPatterns, 
                                                  optimized_placement: Dict[str, List[str]]) -> float:
        """Calculer la latence moyenne pondérée optimisée"""
        total_weighted_latency = 0.0
        total_weight = 0.0
        
        for source_region, traffic_percentage in traffic_patterns.region_traffic.items():
            if source_region in optimized_placement:
                target_regions = optimized_placement[source_region]
                if target_regions:
                    # Utiliser la meilleure région cible
                    best_target = target_regions[0]
                    latency = self.region_coordinator.estimate_latency(source_region, best_target)
                    total_weighted_latency += latency * traffic_percentage
                    total_weight += traffic_percentage
        
        return total_weighted_latency / total_weight if total_weight > 0 else 0.0
    
    async def _generate_migration_recommendations(self, service_name: str, 
                                                optimized_placement: Dict[str, List[str]]) -> List[Dict]:
        """Générer les recommandations de migration"""
        recommendations = []
        
        for source_region, target_regions in optimized_placement.items():
            for target_region in target_regions:
                recommendations.append({
                    'action': 'deploy_service',
                    'service_name': service_name,
                    'target_region': target_region,
                    'reason': f'Optimisation latence pour trafic depuis {source_region}',
                    'priority': 'medium',
                    'estimated_benefit': 'reduced_latency'
                })
        
        return recommendations
    
    async def _estimate_cost_impact(self, optimized_placement: Dict[str, List[str]], 
                                  traffic_patterns: TrafficPatterns) -> float:
        """Estimer l'impact sur les coûts"""
        additional_cost = 0.0
        
        # Calculer les coûts additionnels des nouvelles régions
        new_regions = set()
        for target_regions in optimized_placement.values():
            new_regions.update(target_regions)
        
        for region in new_regions:
            if region in self.region_coordinator.regions:
                cost_factor = self.region_coordinator.regions[region].cost_factor
                # Estimer le coût additionnel basé sur le facteur de coût
                additional_cost += (cost_factor - 1.0) * 100  # Base cost unit
        
        return additional_cost
    
    async def record_latency_measurement(self, source_region: str, target_region: str, latency_ms: float):
        """Enregistrer une mesure de latence réelle"""
        if source_region not in self.latency_measurements:
            self.latency_measurements[source_region] = {}
        
        if target_region not in self.latency_measurements[source_region]:
            self.latency_measurements[source_region][target_region] = []
        
        measurements = self.latency_measurements[source_region][target_region]
        measurements.append(latency_ms)
        
        # Garder seulement les 100 dernières mesures
        if len(measurements) > 100:
            self.latency_measurements[source_region][target_region] = measurements[-100:]

class FailoverManager:
    """Gestionnaire de failover cross-région"""
    
    def __init__(self, region_coordinator: RegionCoordinator):
        self.region_coordinator = region_coordinator
        self.failover_history: List[Dict] = []
        self.active_failovers: Dict[str, Dict] = {}  # région -> failover info
        self.recovery_strategies: Dict[str, FailoverStrategy] = {}
    
    async def coordinate_region_failover(self, failed_region: str, 
                                       strategy: FailoverStrategy = FailoverStrategy.AUTOMATIC) -> FailoverResult:
        """Coordination failover région avec traffic redirection"""
        try:
            # Identifier les services affectés
            affected_services = []
            if failed_region in self.region_coordinator.region_registries:
                affected_services = list(self.region_coordinator.region_registries[failed_region].keys())
            
            if not affected_services:
                logger.warning(f"Aucun service trouvé dans la région défaillante: {failed_region}")
                return FailoverResult(success=True, failed_region=failed_region)
            
            # Déterminer les régions cibles pour le failover
            target_regions = await self._select_failover_targets(failed_region, affected_services)
            
            if not target_regions:
                return FailoverResult(
                    success=False,
                    failed_region=failed_region,
                    affected_services=affected_services,
                    errors=["Aucune région cible disponible pour le failover"]
                )
            
            # Exécuter le failover selon la stratégie
            traffic_redirected = False
            data_migration_required = False
            
            if strategy == FailoverStrategy.IMMEDIATE:
                traffic_redirected = await self._execute_immediate_failover(
                    failed_region, target_regions, affected_services
                )
            elif strategy == FailoverStrategy.GRADUAL:
                traffic_redirected = await self._execute_gradual_failover(
                    failed_region, target_regions, affected_services
                )
            else:  # AUTOMATIC
                traffic_redirected = await self._execute_automatic_failover(
                    failed_region, target_regions, affected_services
                )
            
            # Vérifier si migration de données nécessaire
            data_migration_required = await self._check_data_migration_required(
                failed_region, target_regions, affected_services
            )
            
            # Estimer le temps de récupération
            estimated_recovery_time = await self._estimate_recovery_time(
                len(affected_services), strategy, data_migration_required
            )
            
            # Enregistrer le failover actif
            self.active_failovers[failed_region] = {
                'failed_at': time.time(),
                'target_regions': target_regions,
                'affected_services': affected_services,
                'strategy': strategy,
                'recovery_time_estimate': estimated_recovery_time
            }
            
            result = FailoverResult(
                success=True,
                failed_region=failed_region,
                target_regions=target_regions,
                affected_services=affected_services,
                traffic_redirected=traffic_redirected,
                data_migration_required=data_migration_required,
                estimated_recovery_time=estimated_recovery_time
            )
            
            # Sauvegarder dans l'historique
            self.failover_history.append({
                'timestamp': time.time(),
                'failover_result': result,
                'strategy': strategy
            })
            
            logger.info(f"🚨 Failover exécuté pour région {failed_region} vers {target_regions}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur failover région: {e}")
            return FailoverResult(
                success=False,
                failed_region=failed_region,
                errors=[str(e)]
            )
    
    async def _select_failover_targets(self, failed_region: str, affected_services: List[str]) -> List[str]:
        """Sélectionner les régions cibles pour le failover"""
        targets = []
        
        # Obtenir les régions de failover autorisées
        if failed_region in self.region_coordinator.regions:
            allowed_regions = self.region_coordinator.regions[failed_region].allowed_failover_regions
            
            # Vérifier la capacité et santé de chaque région autorisée
            for region in allowed_regions:
                if await self._check_region_capacity(region, len(affected_services)):
                    targets.append(region)
        
        # Si pas de régions spécifiquement autorisées, utiliser les plus proches
        if not targets:
            all_regions = list(self.region_coordinator.regions.keys())
            region_distances = []
            
            for region in all_regions:
                if region != failed_region:
                    distance = self.region_coordinator.calculate_distance(failed_region, region)
                    region_distances.append((region, distance))
            
            # Trier par distance et prendre les 2 plus proches
            region_distances.sort(key=lambda x: x[1])
            targets = [region for region, distance in region_distances[:2]]
        
        return targets
    
    async def _execute_immediate_failover(self, failed_region: str, target_regions: List[str], 
                                        services: List[str]) -> bool:
        """Exécuter un failover immédiat"""
        try:
            logger.info(f"⚡ Failover immédiat: {failed_region} -> {target_regions}")
            
            for service_name in services:
                # Redistribuer le trafic immédiatement
                await self._redirect_service_traffic(service_name, failed_region, target_regions)
            
            return True
        except Exception as e:
            logger.error(f"Erreur failover immédiat: {e}")
            return False
    
    async def _execute_gradual_failover(self, failed_region: str, target_regions: List[str], 
                                      services: List[str]) -> bool:
        """Exécuter un failover graduel"""
        try:
            logger.info(f"🐌 Failover graduel: {failed_region} -> {target_regions}")
            
            # Failover par étapes sur 5 minutes
            batch_size = max(1, len(services) // 5)
            
            for i in range(0, len(services), batch_size):
                batch_services = services[i:i + batch_size]
                
                for service_name in batch_services:
                    await self._redirect_service_traffic(service_name, failed_region, target_regions)
                
                # Attendre entre les batches
                if i + batch_size < len(services):
                    await asyncio.sleep(60)  # 1 minute entre batches
            
            return True
        except Exception as e:
            logger.error(f"Erreur failover graduel: {e}")
            return False
    
    async def _execute_automatic_failover(self, failed_region: str, target_regions: List[str], 
                                        services: List[str]) -> bool:
        """Exécuter un failover automatique (hybride)"""
        try:
            logger.info(f"🤖 Failover automatique: {failed_region} -> {target_regions}")
            
            # Services critiques en failover immédiat
            critical_services = [s for s in services if 'critical' in s or 'auth' in s or 'payment' in s]
            normal_services = [s for s in services if s not in critical_services]
            
            # Failover immédiat pour services critiques
            for service_name in critical_services:
                await self._redirect_service_traffic(service_name, failed_region, target_regions)
            
            # Failover graduel pour services normaux
            for service_name in normal_services:
                await self._redirect_service_traffic(service_name, failed_region, target_regions)
                await asyncio.sleep(5)  # 5 secondes entre services
            
            return True
        except Exception as e:
            logger.error(f"Erreur failover automatique: {e}")
            return False
    
    async def _redirect_service_traffic(self, service_name: str, failed_region: str, 
                                      target_regions: List[str]):
        """Rediriger le trafic d'un service"""
        # En production, ceci interagit avec le load balancer et DNS
        logger.info(f"🔀 Redirection trafic {service_name}: {failed_region} -> {target_regions}")
    
    async def _check_region_capacity(self, region: str, required_services: int) -> bool:
        """Vérifier la capacité d'une région"""
        if region in self.region_coordinator.regions:
            region_config = self.region_coordinator.regions[region]
            if region_config.capacity_limit:
                current_services = len(self.region_coordinator.region_registries.get(region, {}))
                return current_services + required_services <= region_config.capacity_limit
        return True  # Pas de limite configurée
    
    async def _check_data_migration_required(self, failed_region: str, target_regions: List[str], 
                                           services: List[str]) -> bool:
        """Vérifier si migration de données nécessaire"""
        # Vérifier si des services ont des données persistantes
        stateful_services = ['database', 'storage', 'cache', 'session']
        
        for service in services:
            for stateful_pattern in stateful_services:
                if stateful_pattern in service.lower():
                    return True
        
        return False
    
    async def _estimate_recovery_time(self, num_services: int, strategy: FailoverStrategy, 
                                    data_migration: bool) -> float:
        """Estimer le temps de récupération"""
        base_time = num_services * 30  # 30 secondes par service
        
        if strategy == FailoverStrategy.GRADUAL:
            base_time *= 2  # Plus lent
        elif strategy == FailoverStrategy.IMMEDIATE:
            base_time *= 0.5  # Plus rapide
        
        if data_migration:
            base_time *= 3  # Migration de données prend du temps
        
        return base_time

class GeographicRouter:
    """Routeur géographique intelligent"""
    
    def __init__(self, region_coordinator: RegionCoordinator):
        self.region_coordinator = region_coordinator
        self.routing_rules: Dict[str, Dict] = {}
        self.user_location_cache: Dict[str, str] = {}
    
    async def route_to_optimal_region(self, user_location: str, service_name: str, 
                                    requirements: Dict[str, Any] = None) -> Optional[str]:
        """Router vers la région optimale basée sur la localisation"""
        try:
            requirements = requirements or {}
            
            # Déterminer la région de l'utilisateur
            user_region = await self._determine_user_region(user_location)
            
            if not user_region:
                return None
            
            # Obtenir les services disponibles dans toutes les régions
            all_region_services = await self.region_coordinator.get_all_region_services(service_name)
            
            if not all_region_services:
                return None
            
            # Calculer le score pour chaque région
            region_scores = []
            
            for region, services in all_region_services.items():
                if not services:  # Pas de services sains dans cette région
                    continue
                
                score = await self._calculate_region_score(
                    user_region, region, services, requirements
                )
                region_scores.append((region, score))
            
            if not region_scores:
                return None
            
            # Trier par score (plus haut = meilleur)
            region_scores.sort(key=lambda x: x[1], reverse=True)
            
            selected_region = region_scores[0][0]
            logger.info(f"🌍 Région optimale sélectionnée pour {service_name}: {selected_region}")
            
            return selected_region
            
        except Exception as e:
            logger.error(f"Erreur routing géographique: {e}")
            return None
    
    async def _determine_user_region(self, user_location: str) -> Optional[str]:
        """Déterminer la région de l'utilisateur"""
        # Cache lookup
        if user_location in self.user_location_cache:
            return self.user_location_cache[user_location]
        
        # Mapping simple pays/ville -> région
        location_to_region = {
            'US': Region.US_EAST_1.value,
            'USA': Region.US_EAST_1.value,
            'Canada': Region.US_EAST_1.value,
            'UK': Region.EU_WEST_1.value,
            'France': Region.EU_WEST_1.value,
            'Germany': Region.EU_CENTRAL_1.value,
            'Singapore': Region.AP_SOUTHEAST_1.value,
            'Japan': Region.AP_NORTHEAST_1.value,
            'Australia': Region.AP_SOUTHEAST_1.value
        }
        
        # Recherche par correspondance partielle
        user_location_upper = user_location.upper()
        for location_key, region in location_to_region.items():
            if location_key.upper() in user_location_upper:
                self.user_location_cache[user_location] = region
                return region
        
        # Région par défaut
        default_region = Region.US_EAST_1.value
        self.user_location_cache[user_location] = default_region
        return default_region
    
    async def _calculate_region_score(self, user_region: str, target_region: str, 
                                    services: List[ServiceInstance], requirements: Dict) -> float:
        """Calculer le score d'une région pour le routing"""
        score = 0.0
        
        # Score de latence (plus importante, poids élevé)
        latency = self.region_coordinator.estimate_latency(user_region, target_region)
        latency_score = max(0, 100 - latency)  # Score diminue avec la latence
        score += latency_score * 0.4
        
        # Score de santé des services
        healthy_services = [s for s in services if s.status == ServiceStatus.HEALTHY]
        health_ratio = len(healthy_services) / len(services) if services else 0
        score += health_ratio * 100 * 0.3
        
        # Score de capacité (basé sur le poids moyen)
        if services:
            avg_weight = sum(s.weight for s in services) / len(services)
            capacity_score = min(100, avg_weight)
            score += capacity_score * 0.2
        
        # Score de coût (région moins chère = meilleur score)
        if target_region in self.region_coordinator.regions:
            cost_factor = self.region_coordinator.regions[target_region].cost_factor
            cost_score = max(0, 200 - cost_factor * 100)  # Score diminue avec le coût
            score += cost_score * 0.1
        
        return score

class MultiRegionDiscovery:
    """
    Discovery multi-région pour deployment global.
    Cross-region service discovery + latency optimization + failover.
    """
    
    def __init__(self, region_config: Dict = None):
        self.region_config = region_config or {}
        
        # Composants principaux
        self.region_coordinator = RegionCoordinator()
        self.latency_optimizer = LatencyOptimizer(self.region_coordinator)
        self.failover_manager = FailoverManager(self.region_coordinator)
        self.geo_router = GeographicRouter(self.region_coordinator)
        
        # Règles de localisation des données
        self.locality_rules: Dict[str, LocalityRule] = {}
        
        logger.info("🌍 MultiRegionDiscovery initialisé")
    
    async def discover_cross_region_services(self, discovery_request: CrossRegionRequest) -> CrossRegionResult:
        """
        Discovery services cross-region avec optimization latence.
        
        Multi-Region Features:
        - Cross-region service discovery avec latency awareness
        - Geographic routing pour optimal user experience
        - Region failover avec automatic traffic shifting
        - Data locality enforcement pour compliance
        - Cross-region load balancing avec cost optimization
        - Edge location service placement
        - Global service health monitoring
        """
        try:
            service_name = discovery_request.service_name
            
            # 1. Obtenir tous les services cross-région
            all_region_services = await self.region_coordinator.get_all_region_services(service_name)
            
            if not all_region_services:
                return CrossRegionResult(
                    success=False,
                    errors=[f"Service {service_name} introuvable dans toutes les régions"]
                )
            
            # 2. Filtrer par régions préférées si spécifiées
            if discovery_request.preferred_regions:
                filtered_services = {
                    region: services for region, services in all_region_services.items()
                    if region in discovery_request.preferred_regions
                }
                if filtered_services:
                    all_region_services = filtered_services
            
            # 3. Vérifier les contraintes de localisation des données
            compliance_satisfied = True
            if discovery_request.data_locality_required:
                compliant_regions = await self._filter_compliant_regions(
                    service_name, 
                    list(all_region_services.keys()),
                    discovery_request.compliance_requirements
                )
                
                if compliant_regions:
                    all_region_services = {
                        region: services for region, services in all_region_services.items()
                        if region in compliant_regions
                    }
                else:
                    compliance_satisfied = False
            
            # 4. Sélectionner la région optimale
            selected_region = None
            if discovery_request.user_location:
                selected_region = await self.geo_router.route_to_optimal_region(
                    discovery_request.user_location,
                    service_name,
                    {
                        'latency_requirement': discovery_request.latency_requirement,
                        'compliance_requirements': discovery_request.compliance_requirements
                    }
                )
            
            # 5. Fallback si pas de région sélectionnée géographiquement
            if not selected_region or selected_region not in all_region_services:
                # Sélectionner la région avec les services les plus sains
                best_region = None
                best_health_score = -1
                
                for region, services in all_region_services.items():
                    healthy_services = [s for s in services if s.status == ServiceStatus.HEALTHY]
                    health_score = len(healthy_services) / len(services) if services else 0
                    
                    if health_score > best_health_score:
                        best_health_score = health_score
                        best_region = region
                
                selected_region = best_region
            
            # 6. Récupérer les instances sélectionnées
            selected_instances = []
            latency_estimate = None
            failover_applied = False
            
            if selected_region and selected_region in all_region_services:
                selected_instances = all_region_services[selected_region]
                
                # Estimer la latence si région utilisateur connue
                if discovery_request.user_region:
                    latency_estimate = self.region_coordinator.estimate_latency(
                        discovery_request.user_region, selected_region
                    )
                
                # Vérifier si failover a été appliqué
                if selected_region in self.failover_manager.active_failovers:
                    failover_applied = True
            
            # 7. Calculer le coût estimé
            cost_estimate = 0.0
            if selected_region in self.region_coordinator.regions:
                cost_factor = self.region_coordinator.regions[selected_region].cost_factor
                cost_estimate = len(selected_instances) * cost_factor * 10  # Coût par instance
            
            result = CrossRegionResult(
                success=len(selected_instances) > 0,
                selected_instances=selected_instances,
                selected_region=selected_region,
                latency_estimate=latency_estimate,
                failover_applied=failover_applied,
                compliance_satisfied=compliance_satisfied,
                cost_estimate=cost_estimate
            )
            
            if not result.success:
                result.errors.append("Aucune instance saine trouvée dans les régions sélectionnées")
            
            logger.info(f"🌍 Discovery cross-région {service_name}: région {selected_region}, {len(selected_instances)} instances")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur discovery cross-région: {e}")
            return CrossRegionResult(
                success=False,
                errors=[str(e)]
            )
    
    async def optimize_cross_region_latency(self, traffic_patterns: TrafficPatterns) -> LatencyOptimization:
        """Optimization latence cross-region basée sur traffic patterns"""
        return await self.latency_optimizer.optimize_cross_region_latency(traffic_patterns)
    
    async def coordinate_region_failover(self, failed_region: str) -> FailoverResult:
        """Coordination failover région avec traffic redirection"""
        return await self.failover_manager.coordinate_region_failover(failed_region)
    
    async def enforce_data_locality(self, data_locality_rules: List[LocalityRule]) -> LocalityResult:
        """Enforcement règles data locality pour compliance"""
        try:
            enforced_rules = []
            violations = []
            migrations_required = []
            
            for rule in data_locality_rules:
                self.locality_rules[rule.rule_id] = rule
                
                # Vérifier les services existants contre cette règle
                rule_violations = await self._check_locality_compliance(rule)
                
                if rule_violations:
                    violations.extend(rule_violations)
                    
                    # Générer les migrations nécessaires
                    for violation in rule_violations:
                        migration = await self._generate_locality_migration(violation, rule)
                        if migration:
                            migrations_required.append(migration)
                else:
                    enforced_rules.append(rule.rule_id)
            
            result = LocalityResult(
                success=len(violations) == 0,
                enforced_rules=enforced_rules,
                violations=violations,
                migrations_required=migrations_required
            )
            
            logger.info(f"🏛️ Règles localité: {len(enforced_rules)} appliquées, {len(violations)} violations")
            return result
            
        except Exception as e:
            logger.error(f"Erreur enforcement localité: {e}")
            return LocalityResult(
                success=False,
                violations=[{'error': str(e)}]
            )
    
    async def monitor_global_service_health(self) -> GlobalHealthStatus:
        """Monitoring santé services global avec regional aggregation"""
        try:
            global_status = GlobalHealthStatus()
            
            total_instances = 0
            healthy_instances = 0
            
            # Évaluer chaque région
            for region_id, registry in self.region_coordinator.region_registries.items():
                region_instances = 0
                region_healthy = 0
                
                # Compteur par service dans la région
                for service_name, instances in registry.items():
                    region_instances += len(instances)
                    region_healthy += len([i for i in instances if i.status == ServiceStatus.HEALTHY])
                
                # Score de santé de la région
                region_health_score = region_healthy / region_instances if region_instances > 0 else 1.0
                global_status.region_health[region_id] = region_health_score
                
                total_instances += region_instances
                healthy_instances += region_healthy
                
                # Identifier les régions dégradées
                if region_health_score < 0.7:
                    global_status.degraded_regions.append(region_id)
            
            global_status.total_instances = total_instances
            global_status.healthy_instances = healthy_instances
            
            # Calculer les latences cross-région
            regions = list(self.region_coordinator.regions.keys())
            for i, region1 in enumerate(regions):
                global_status.cross_region_latency[region1] = {}
                for region2 in regions:
                    if region1 != region2:
                        latency = self.region_coordinator.estimate_latency(region1, region2)
                        global_status.cross_region_latency[region1][region2] = latency
            
            logger.info(f"🏥 Santé globale: {healthy_instances}/{total_instances} instances saines")
            return global_status
            
        except Exception as e:
            logger.error(f"Erreur monitoring global: {e}")
            return GlobalHealthStatus()
    
    async def _filter_compliant_regions(self, service_name: str, available_regions: List[str], 
                                      compliance_requirements: List[str]) -> List[str]:
        """Filtrer les régions conformes aux exigences"""
        compliant_regions = []
        
        for region in available_regions:
            if region in self.region_coordinator.regions:
                region_config = self.region_coordinator.regions[region]
                
                # Vérifier si la région satisfait toutes les exigences de compliance
                region_compliance = set(region_config.compliance_requirements)
                required_compliance = set(compliance_requirements)
                
                if required_compliance.issubset(region_compliance):
                    compliant_regions.append(region)
        
        return compliant_regions
    
    async def _check_locality_compliance(self, rule: LocalityRule) -> List[Dict]:
        """Vérifier la conformité d'une règle de localité"""
        violations = []
        
        # Vérifier tous les services qui matchent le pattern
        for region_id, registry in self.region_coordinator.region_registries.items():
            for service_name in registry.keys():
                import re
                if re.match(rule.service_pattern, service_name):
                    # Vérifier si la région est autorisée
                    if rule.required_regions and region_id not in rule.required_regions:
                        violations.append({
                            'service_name': service_name,
                            'current_region': region_id,
                            'rule_id': rule.rule_id,
                            'violation_type': 'unauthorized_region'
                        })
                    
                    # Vérifier si la région est interdite
                    if rule.forbidden_regions and region_id in rule.forbidden_regions:
                        violations.append({
                            'service_name': service_name,
                            'current_region': region_id,
                            'rule_id': rule.rule_id,
                            'violation_type': 'forbidden_region'
                        })
        
        return violations
    
    async def _generate_locality_migration(self, violation: Dict, rule: LocalityRule) -> Optional[Dict]:
        """Générer une migration pour une violation de localité"""
        if rule.required_regions:
            # Choisir la première région requise comme cible
            target_region = rule.required_regions[0]
            
            return {
                'action': 'migrate_service',
                'service_name': violation['service_name'],
                'source_region': violation['current_region'],
                'target_region': target_region,
                'reason': f"Conformité règle {rule.rule_id}",
                'priority': 'high' if rule.locality_level == DataLocalityLevel.STRICT else 'medium'
            }
        
        return None
    
    async def get_multi_region_stats(self) -> Dict:
        """Obtenir les statistiques multi-région"""
        total_regions = len(self.region_coordinator.regions)
        active_regions = len(self.region_coordinator.region_registries)
        active_failovers = len(self.failover_manager.active_failovers)
        locality_rules = len(self.locality_rules)
        
        return {
            'total_regions': total_regions,
            'active_regions': active_regions,
            'active_failovers': active_failovers,
            'locality_rules': locality_rules,
            'optimization_history': len(self.latency_optimizer.optimization_history),
            'failover_history': len(self.failover_manager.failover_history)
        }

# Factory function
def create_multi_region_discovery(config: Dict = None) -> MultiRegionDiscovery:
    """Factory pour créer un gestionnaire multi-région"""
    return MultiRegionDiscovery(config)

__all__ = [
    'MultiRegionDiscovery',
    'Region',
    'FailoverStrategy',
    'DataLocalityLevel',
    'RegionConfig',
    'CrossRegionRequest',
    'CrossRegionResult',
    'TrafficPatterns',
    'LatencyOptimization',
    'FailoverResult',
    'LocalityRule',
    'LocalityResult',
    'GlobalHealthStatus',
    'RegionCoordinator',
    'LatencyOptimizer',
    'FailoverManager',
    'GeographicRouter',
    'create_multi_region_discovery'
]