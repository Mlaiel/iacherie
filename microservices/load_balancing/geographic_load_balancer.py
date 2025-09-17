"""
🌍 GEOGRAPHIC LOAD BALANCER - ENTERPRISE GLOBAL DISTRIBUTION
Load balancer géographique pour optimization latence globale

Implements multi-region routing + latency optimization + geo-aware distribution
for enterprise-grade global traffic management and compliance-aware routing.

Key Features:
- GeoIP-based client location detection avec précision continent/pays/région
- Multi-region server pool management avec health monitoring
- Latency-aware routing decisions avec real-time measurements
- CDN integration pour static content optimization
- Cross-region failover strategies avec data locality preservation
- Compliance-aware data locality routing (GDPR, CCPA, etc.)

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture geographic load balancer est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution sans autorisation écrite est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import time
import ipaddress
import math
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib
from collections import defaultdict, deque
import aiohttp
from geopy.distance import geodesic
import socket

logger = logging.getLogger(__name__)

class GeographicRegion(Enum):
    """Régions géographiques supportées"""
    NORTH_AMERICA_EAST = "na-east"
    NORTH_AMERICA_WEST = "na-west" 
    NORTH_AMERICA_CENTRAL = "na-central"
    EUROPE_WEST = "eu-west"
    EUROPE_CENTRAL = "eu-central"
    EUROPE_NORTH = "eu-north"
    ASIA_PACIFIC_EAST = "ap-east"
    ASIA_PACIFIC_SOUTH = "ap-south"
    ASIA_PACIFIC_SOUTHEAST = "ap-southeast"
    MIDDLE_EAST = "me-central"
    AFRICA = "af-south"
    SOUTH_AMERICA = "sa-east"
    OCEANIA = "oc-southeast"

class ComplianceRegion(Enum):
    """Régions compliance pour data locality"""
    GDPR_EU = "gdpr_eu"           # Union Européenne GDPR
    CCPA_CALIFORNIA = "ccpa_ca"   # Californie CCPA
    PIPEDA_CANADA = "pipeda_ca"   # Canada PIPEDA
    LGPD_BRAZIL = "lgpd_br"       # Brésil LGPD
    PDPA_SINGAPORE = "pdpa_sg"    # Singapour PDPA
    DPA_UK = "dpa_uk"             # Royaume-Uni DPA
    PRIVACY_ACT_AU = "privacy_au" # Australie Privacy Act

class RoutingStrategy(Enum):
    """Stratégies routing géographique"""
    LOWEST_LATENCY = "lowest_latency"
    NEAREST_REGION = "nearest_region"
    COMPLIANCE_FIRST = "compliance_first"
    LOAD_BALANCED_GEO = "load_balanced_geo"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    COST_OPTIMIZED = "cost_optimized"

@dataclass
class GeoLocation:
    """Localisation géographique"""
    latitude: float
    longitude: float
    country: str
    region: str
    city: str
    continent: str
    timezone: str
    accuracy_radius: Optional[int] = None
    
    def distance_to(self, other: 'GeoLocation') -> float:
        """Calcul distance géographique en km"""
        return geodesic((self.latitude, self.longitude), (other.latitude, other.longitude)).kilometers

@dataclass
class RegionalServer:
    """Serveur dans région géographique"""
    server_id: str
    region: GeographicRegion
    location: GeoLocation
    endpoint: str
    capacity: int
    current_load: int
    health_status: str
    average_latency: float
    compliance_regions: Set[ComplianceRegion]
    cdn_enabled: bool = False
    cost_per_request: float = 0.001
    last_health_check: datetime = field(default_factory=datetime.now)
    
    @property
    def load_percentage(self) -> float:
        """Pourcentage charge actuelle"""
        return (self.current_load / max(1, self.capacity)) * 100.0
    
    @property
    def is_healthy(self) -> bool:
        """Vérification santé serveur"""
        return self.health_status == "healthy" and self.load_percentage < 90.0

@dataclass
class LatencyMeasurement:
    """Mesure latence entre client et serveur"""
    client_location: GeoLocation
    server_location: GeoLocation
    measured_latency_ms: float
    timestamp: datetime
    network_path: Optional[List[str]] = None
    
@dataclass
class GeographicConfig:
    """Configuration load balancer géographique"""
    default_strategy: RoutingStrategy = RoutingStrategy.LOWEST_LATENCY
    max_latency_threshold_ms: float = 500.0
    latency_measurement_interval: int = 300  # 5 minutes
    health_check_interval: int = 60          # 1 minute
    failover_latency_multiplier: float = 2.0
    enable_cdn_routing: bool = True
    enable_compliance_routing: bool = True
    latency_cache_ttl: int = 600            # 10 minutes
    geoip_provider: str = "maxmind"         # maxmind, ipinfo, etc.
    backup_regions_per_primary: int = 2

class GeoIPResolver:
    """Résolveur GeoIP pour localisation clients"""
    
    def __init__(self, provider: str = "maxmind"):
        self.provider = provider
        self.ip_location_cache: Dict[str, GeoLocation] = {}
        self.cache_ttl = 3600  # 1 heure
        self.last_cache_cleanup = datetime.now()
        
        # Base de données GeoIP intégrée simple (pour démo)
        self.geoip_database = self._initialize_geoip_database()
        
    def _initialize_geoip_database(self) -> Dict[str, GeoLocation]:
        """Initialisation base données GeoIP simplifiée"""
        return {
            # Plages IP exemples pour démo
            "192.168.0.0/16": GeoLocation(37.7749, -122.4194, "US", "California", "San Francisco", "North America", "America/Los_Angeles"),
            "10.0.0.0/8": GeoLocation(51.5074, -0.1278, "GB", "England", "London", "Europe", "Europe/London"),
            "172.16.0.0/12": GeoLocation(35.6762, 139.6503, "JP", "Tokyo", "Tokyo", "Asia", "Asia/Tokyo"),
            "203.0.113.0/24": GeoLocation(1.3521, 103.8198, "SG", "Singapore", "Singapore", "Asia", "Asia/Singapore"),
            "198.51.100.0/24": GeoLocation(52.5200, 13.4050, "DE", "Berlin", "Berlin", "Europe", "Europe/Berlin"),
            "0.0.0.0/0": GeoLocation(39.0458, -76.6413, "US", "Maryland", "Baltimore", "North America", "America/New_York")  # Fallback
        }
    
    async def resolve_ip_location(self, client_ip: str) -> GeoLocation:
        """Résolution localisation IP client"""
        try:
            # Vérification cache
            cache_key = client_ip
            if cache_key in self.ip_location_cache:
                cached_location = self.ip_location_cache[cache_key]
                return cached_location
            
            # Nettoyage cache périodique
            await self._cleanup_cache_if_needed()
            
            # Résolution IP
            location = await self._resolve_ip_with_provider(client_ip)
            
            # Cache résultat
            self.ip_location_cache[cache_key] = location
            
            logger.debug(f"🌍 IP {client_ip} résolue vers: {location.city}, {location.country}")
            
            return location
            
        except Exception as e:
            logger.error(f"❌ Erreur résolution GeoIP pour {client_ip}: {e}")
            # Retour localisation par défaut
            return self.geoip_database["0.0.0.0/0"]
    
    async def _resolve_ip_with_provider(self, client_ip: str) -> GeoLocation:
        """Résolution IP avec provider externe ou base interne"""
        try:
            # Vérification IP privée
            ip_obj = ipaddress.ip_address(client_ip)
            if ip_obj.is_private or ip_obj.is_loopback:
                return self.geoip_database["0.0.0.0/0"]  # Fallback pour IPs privées
            
            # Recherche dans base interne
            for ip_range, location in self.geoip_database.items():
                if ip_range != "0.0.0.0/0":
                    try:
                        network = ipaddress.ip_network(ip_range)
                        if ip_obj in network:
                            return location
                    except Exception:
                        continue
            
            # Fallback si pas trouvé
            return self.geoip_database["0.0.0.0/0"]
            
        except Exception as e:
            logger.error(f"❌ Erreur résolution provider IP {client_ip}: {e}")
            return self.geoip_database["0.0.0.0/0"]
    
    async def _cleanup_cache_if_needed(self):
        """Nettoyage cache GeoIP"""
        now = datetime.now()
        if (now - self.last_cache_cleanup).total_seconds() > self.cache_ttl:
            self.ip_location_cache.clear()
            self.last_cache_cleanup = now
            logger.debug("🧹 Cache GeoIP nettoyé")

class LatencyMonitor:
    """Moniteur latence entre régions"""
    
    def __init__(self, config: GeographicConfig):
        self.config = config
        self.latency_measurements: Dict[Tuple[str, str], deque] = defaultdict(lambda: deque(maxlen=100))
        self.active_measurements: Dict[str, datetime] = {}
        
    async def measure_latency(self, client_location: GeoLocation, server: RegionalServer) -> float:
        """Mesure latence client vers serveur"""
        try:
            measurement_key = (f"{client_location.latitude}_{client_location.longitude}", server.server_id)
            
            # Vérification cache latence
            if measurement_key in self.latency_measurements:
                recent_measurements = list(self.latency_measurements[measurement_key])
                if recent_measurements:
                    # Utilisation mesure récente si disponible
                    latest_measurement = recent_measurements[-1]
                    if isinstance(latest_measurement, LatencyMeasurement):
                        age = (datetime.now() - latest_measurement.timestamp).total_seconds()
                        if age < self.config.latency_cache_ttl:
                            return latest_measurement.measured_latency_ms
            
            # Nouvelle mesure latence
            start_time = time.time()
            
            # Simulation mesure latence basée sur distance géographique
            distance_km = client_location.distance_to(server.location)
            
            # Calcul latence estimée basée sur distance et type connexion
            base_latency = max(10.0, distance_km * 0.02)  # ~20ms pour 1000km base
            
            # Facteurs additionnels
            if server.current_load > server.capacity * 0.8:
                base_latency *= 1.5  # Pénalité charge élevée
            
            if not server.is_healthy:
                base_latency *= 2.0  # Pénalité santé dégradée
            
            # Simulation variabilité réseau
            import random
            network_jitter = random.uniform(0.8, 1.2)
            measured_latency = base_latency * network_jitter
            
            # Stockage mesure
            measurement = LatencyMeasurement(
                client_location=client_location,
                server_location=server.location,
                measured_latency_ms=measured_latency,
                timestamp=datetime.now()
            )
            
            self.latency_measurements[measurement_key].append(measurement)
            
            logger.debug(f"📡 Latence mesurée: {client_location.city} → {server.region.value}: {measured_latency:.1f}ms")
            
            return measured_latency
            
        except Exception as e:
            logger.error(f"❌ Erreur mesure latence: {e}")
            # Fallback basé sur distance géographique
            return max(50.0, client_location.distance_to(server.location) * 0.05)
    
    async def get_average_latency(self, client_location: GeoLocation, server: RegionalServer) -> float:
        """Obtention latence moyenne historique"""
        measurement_key = (f"{client_location.latitude}_{client_location.longitude}", server.server_id)
        
        if measurement_key in self.latency_measurements:
            measurements = [m.measured_latency_ms for m in self.latency_measurements[measurement_key] 
                          if isinstance(m, LatencyMeasurement)]
            if measurements:
                return sum(measurements) / len(measurements)
        
        # Mesure si pas d'historique
        return await self.measure_latency(client_location, server)

class RegionManager:
    """Gestionnaire régions et serveurs"""
    
    def __init__(self):
        self.regional_servers: Dict[GeographicRegion, List[RegionalServer]] = defaultdict(list)
        self.compliance_mapping: Dict[str, Set[ComplianceRegion]] = self._initialize_compliance_mapping()
        
    def _initialize_compliance_mapping(self) -> Dict[str, Set[ComplianceRegion]]:
        """Initialisation mapping compliance par pays"""
        return {
            # Union Européenne GDPR
            "DE": {ComplianceRegion.GDPR_EU},
            "FR": {ComplianceRegion.GDPR_EU},
            "IT": {ComplianceRegion.GDPR_EU},
            "ES": {ComplianceRegion.GDPR_EU},
            "NL": {ComplianceRegion.GDPR_EU},
            "BE": {ComplianceRegion.GDPR_EU},
            "AT": {ComplianceRegion.GDPR_EU},
            "SE": {ComplianceRegion.GDPR_EU},
            "DK": {ComplianceRegion.GDPR_EU},
            "FI": {ComplianceRegion.GDPR_EU},
            "NO": {ComplianceRegion.GDPR_EU},
            "PL": {ComplianceRegion.GDPR_EU},
            
            # Royaume-Uni post-Brexit
            "GB": {ComplianceRegion.DPA_UK},
            
            # Amérique du Nord
            "US": {ComplianceRegion.CCPA_CALIFORNIA},  # Californie principalement
            "CA": {ComplianceRegion.PIPEDA_CANADA},
            
            # Amérique du Sud
            "BR": {ComplianceRegion.LGPD_BRAZIL},
            
            # Asie-Pacifique
            "SG": {ComplianceRegion.PDPA_SINGAPORE},
            "AU": {ComplianceRegion.PRIVACY_ACT_AU},
        }
    
    def add_regional_server(self, server: RegionalServer):
        """Ajout serveur régional"""
        self.regional_servers[server.region].append(server)
        logger.info(f"🌍 Serveur régional ajouté: {server.server_id} ({server.region.value})")
    
    def get_servers_by_region(self, region: GeographicRegion) -> List[RegionalServer]:
        """Obtention serveurs par région"""
        return [s for s in self.regional_servers[region] if s.is_healthy]
    
    def get_compliant_servers(self, client_country: str) -> List[RegionalServer]:
        """Obtention serveurs conformes pour pays client"""
        required_compliance = self.compliance_mapping.get(client_country, set())
        
        compliant_servers = []
        for servers in self.regional_servers.values():
            for server in servers:
                if server.is_healthy and required_compliance.issubset(server.compliance_regions):
                    compliant_servers.append(server)
        
        return compliant_servers
    
    def get_nearest_regions(self, client_location: GeoLocation, max_regions: int = 3) -> List[GeographicRegion]:
        """Obtention régions les plus proches"""
        region_distances = []
        
        # Localisation approximative centres régions
        region_centers = {
            GeographicRegion.NORTH_AMERICA_EAST: GeoLocation(40.7128, -74.0060, "US", "NY", "New York", "North America", "America/New_York"),
            GeographicRegion.NORTH_AMERICA_WEST: GeoLocation(37.7749, -122.4194, "US", "CA", "San Francisco", "North America", "America/Los_Angeles"),
            GeographicRegion.EUROPE_WEST: GeoLocation(51.5074, -0.1278, "GB", "England", "London", "Europe", "Europe/London"),
            GeographicRegion.EUROPE_CENTRAL: GeoLocation(52.5200, 13.4050, "DE", "Berlin", "Berlin", "Europe", "Europe/Berlin"),
            GeographicRegion.ASIA_PACIFIC_EAST: GeoLocation(35.6762, 139.6503, "JP", "Tokyo", "Tokyo", "Asia", "Asia/Tokyo"),
            GeographicRegion.ASIA_PACIFIC_SOUTHEAST: GeoLocation(1.3521, 103.8198, "SG", "Singapore", "Singapore", "Asia", "Asia/Singapore"),
        }
        
        for region, center_location in region_centers.items():
            distance = client_location.distance_to(center_location)
            region_distances.append((region, distance))
        
        # Tri par distance croissante
        region_distances.sort(key=lambda x: x[1])
        
        return [region for region, _ in region_distances[:max_regions]]

class CDNIntegrator:
    """Intégrateur CDN pour content routing"""
    
    def __init__(self):
        self.cdn_endpoints: Dict[GeographicRegion, List[str]] = defaultdict(list)
        self.content_rules: Dict[str, str] = {}  # content_type -> routing_rule
        
    def setup_cdn_endpoints(self):
        """Configuration endpoints CDN par région"""
        self.cdn_endpoints = {
            GeographicRegion.NORTH_AMERICA_EAST: ["cdn-na-east-1.ainflue.com", "cdn-na-east-2.ainflue.com"],
            GeographicRegion.NORTH_AMERICA_WEST: ["cdn-na-west-1.ainflue.com", "cdn-na-west-2.ainflue.com"],
            GeographicRegion.EUROPE_WEST: ["cdn-eu-west-1.ainflue.com", "cdn-eu-west-2.ainflue.com"],
            GeographicRegion.ASIA_PACIFIC_EAST: ["cdn-ap-east-1.ainflue.com", "cdn-ap-east-2.ainflue.com"],
        }
        
        self.content_rules = {
            "image": "cdn_optimized",
            "video": "cdn_streaming",
            "audio": "cdn_streaming", 
            "static": "cdn_edge",
            "api": "origin_server"
        }
    
    async def get_optimal_cdn_endpoint(self, content_type: str, client_region: GeographicRegion) -> Optional[str]:
        """Obtention endpoint CDN optimal"""
        try:
            routing_rule = self.content_rules.get(content_type, "origin_server")
            
            if routing_rule.startswith("cdn_") and client_region in self.cdn_endpoints:
                endpoints = self.cdn_endpoints[client_region]
                if endpoints:
                    # Sélection endpoint basée sur charge (simulée)
                    import random
                    return random.choice(endpoints)
            
            return None  # Pas de CDN approprié
            
        except Exception as e:
            logger.error(f"❌ Erreur sélection endpoint CDN: {e}")
            return None

class GeographicLoadBalancer:
    """
    🌍 LOAD BALANCER GÉOGRAPHIQUE ENTERPRISE
    
    Load balancer géographique pour optimization latence globale.
    Multi-region routing + latency optimization + geo-aware distribution.
    """
    
    def __init__(self, geo_config: Optional[GeographicConfig] = None):
        self.geo_config = geo_config or GeographicConfig()
        self.geo_ip_resolver = GeoIPResolver(self.geo_config.geoip_provider)
        self.latency_monitor = LatencyMonitor(self.geo_config)
        self.region_manager = RegionManager()
        self.cdn_integrator = CDNIntegrator()
        
        # Métriques geographic routing
        self.total_routing_requests = 0
        self.successful_geo_routes = 0
        self.compliance_routes = 0
        self.cdn_routes = 0
        self.average_routing_latency = 0.0
        
        # Initialisation
        self._initialize_demo_servers()
        self.cdn_integrator.setup_cdn_endpoints()
        
        logger.info("🌍 Geographic Load Balancer initialisé avec succès")
    
    def _initialize_demo_servers(self):
        """Initialisation serveurs démo pour test"""
        demo_servers = [
            RegionalServer(
                server_id="na-east-01",
                region=GeographicRegion.NORTH_AMERICA_EAST,
                location=GeoLocation(40.7128, -74.0060, "US", "NY", "New York", "North America", "America/New_York"),
                endpoint="https://api-na-east.ainflue.com",
                capacity=1000,
                current_load=450,
                health_status="healthy",
                average_latency=25.0,
                compliance_regions={ComplianceRegion.CCPA_CALIFORNIA},
                cdn_enabled=True
            ),
            RegionalServer(
                server_id="eu-west-01", 
                region=GeographicRegion.EUROPE_WEST,
                location=GeoLocation(51.5074, -0.1278, "GB", "England", "London", "Europe", "Europe/London"),
                endpoint="https://api-eu-west.ainflue.com",
                capacity=800,
                current_load=320,
                health_status="healthy",
                average_latency=30.0,
                compliance_regions={ComplianceRegion.GDPR_EU, ComplianceRegion.DPA_UK},
                cdn_enabled=True
            ),
            RegionalServer(
                server_id="ap-east-01",
                region=GeographicRegion.ASIA_PACIFIC_EAST,
                location=GeoLocation(35.6762, 139.6503, "JP", "Tokyo", "Tokyo", "Asia", "Asia/Tokyo"),
                endpoint="https://api-ap-east.ainflue.com",
                capacity=600,
                current_load=180,
                health_status="healthy",
                average_latency=35.0,
                compliance_regions=set(),
                cdn_enabled=True
            ),
        ]
        
        for server in demo_servers:
            self.region_manager.add_regional_server(server)

    async def route_by_geography(self, client_ip: str, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎯 ROUTING GÉOGRAPHIQUE INTELLIGENT AVEC LATENCE OPTIMIZATION
        
        Routing géographique intelligent avec latence optimization comprehensive.
        """
        start_time = time.time()
        
        try:
            logger.debug(f"🌍 Routing géographique pour IP {client_ip}")
            
            # Résolution localisation client
            client_location = await self.geo_ip_resolver.resolve_ip_location(client_ip)
            
            # Extraction contexte requête
            content_type = request_context.get("content_type", "api")
            priority_level = request_context.get("priority_level", 5)
            compliance_required = request_context.get("compliance_required", True)
            latency_requirement = request_context.get("max_latency_ms", self.geo_config.max_latency_threshold_ms)
            
            # Sélection stratégie routing
            strategy = self._determine_routing_strategy(request_context, client_location)
            
            # Routing selon stratégie
            routing_result = await self._execute_geographic_routing(
                client_location, strategy, content_type, latency_requirement, compliance_required
            )
            
            # Mise à jour métriques
            self.total_routing_requests += 1
            routing_time = time.time() - start_time
            self.average_routing_latency = (
                self.average_routing_latency * 0.9 + routing_time * 0.1
            )
            
            if routing_result["success"]:
                self.successful_geo_routes += 1
                
                if routing_result.get("compliance_satisfied"):
                    self.compliance_routes += 1
                    
                if routing_result.get("cdn_used"):
                    self.cdn_routes += 1
            
            # Enrichissement résultat
            routing_result.update({
                "client_location": {
                    "country": client_location.country,
                    "region": client_location.region,
                    "city": client_location.city,
                    "continent": client_location.continent
                },
                "routing_strategy": strategy.value,
                "routing_time_ms": routing_time * 1000,
                "total_requests": self.total_routing_requests
            })
            
            logger.info(
                f"✅ Routing géographique terminé: {routing_result.get('selected_server_id', 'none')} "
                f"(stratégie: {strategy.value}, temps: {routing_time*1000:.1f}ms)"
            )
            
            return routing_result
            
        except Exception as e:
            logger.error(f"❌ Erreur routing géographique: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_used": True,
                "selected_server_id": None
            }

    async def optimize_regional_distribution(self, traffic_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
        ⚖️ OPTIMISATION DISTRIBUTION RÉGIONALE BASÉE SUR PATTERNS
        
        Optimisation distribution régionale basée sur patterns trafic historiques.
        """
        logger.info("⚖️ Optimisation distribution régionale")
        
        optimization_result = {
            "optimizations_applied": [],
            "capacity_recommendations": {},
            "rebalancing_actions": [],
            "performance_improvements": {},
            "summary": {}
        }
        
        try:
            # Analyse patterns trafic par région
            regional_traffic = traffic_patterns.get("regional_distribution", {})
            if not regional_traffic:
                logger.warning("Aucun pattern trafic régional fourni")
                return optimization_result
            
            # Calcul utilisation actuelle par région
            current_utilization = {}
            total_capacity = 0
            total_load = 0
            
            for region, servers in self.region_manager.regional_servers.items():
                region_capacity = sum(s.capacity for s in servers)
                region_load = sum(s.current_load for s in servers)
                
                if region_capacity > 0:
                    utilization = (region_load / region_capacity) * 100
                    current_utilization[region.value] = {
                        "utilization_percent": utilization,
                        "capacity": region_capacity,
                        "load": region_load,
                        "servers": len(servers)
                    }
                    
                    total_capacity += region_capacity
                    total_load += region_load
            
            # Identification déséquilibres
            for region_name, traffic_data in regional_traffic.items():
                if region_name in current_utilization:
                    util_data = current_utilization[region_name]
                    traffic_percentage = traffic_data.get("traffic_percentage", 0)
                    utilization_percentage = util_data["utilization_percent"]
                    
                    # Détection sur-utilisation
                    if utilization_percentage > 85:
                        optimization_result["optimizations_applied"].append({
                            "region": region_name,
                            "action": "scale_up",
                            "reason": f"Sur-utilisation détectée: {utilization_percentage:.1f}%",
                            "recommended_capacity_increase": max(200, int(util_data["capacity"] * 0.3))
                        })
                    
                    # Détection sous-utilisation
                    elif utilization_percentage < 20 and traffic_percentage < 5:
                        optimization_result["optimizations_applied"].append({
                            "region": region_name,
                            "action": "scale_down", 
                            "reason": f"Sous-utilisation détectée: {utilization_percentage:.1f}%",
                            "recommended_capacity_decrease": int(util_data["capacity"] * 0.2)
                        })
                    
                    # Déséquilibre trafic vs capacité
                    capacity_ratio = util_data["capacity"] / max(1, total_capacity) * 100
                    if abs(traffic_percentage - capacity_ratio) > 15:
                        optimization_result["rebalancing_actions"].append({
                            "region": region_name,
                            "traffic_percentage": traffic_percentage,
                            "capacity_percentage": capacity_ratio,
                            "rebalancing_needed": abs(traffic_percentage - capacity_ratio)
                        })
            
            # Recommandations capacité globales
            if total_capacity > 0:
                global_utilization = (total_load / total_capacity) * 100
                optimization_result["capacity_recommendations"]["global_utilization"] = global_utilization
                
                if global_utilization > 80:
                    optimization_result["capacity_recommendations"]["action"] = "global_scale_up"
                    optimization_result["capacity_recommendations"]["additional_capacity_needed"] = int(total_capacity * 0.3)
                elif global_utilization < 30:
                    optimization_result["capacity_recommendations"]["action"] = "global_optimization"
                    optimization_result["capacity_recommendations"]["capacity_reduction_possible"] = int(total_capacity * 0.2)
            
            # Calcul améliorations performance
            optimization_result["performance_improvements"] = {
                "estimated_latency_reduction_ms": len(optimization_result["optimizations_applied"]) * 15,
                "estimated_throughput_increase_percent": len(optimization_result["optimizations_applied"]) * 8,
                "estimated_cost_optimization_percent": len(optimization_result["rebalancing_actions"]) * 5
            }
            
            # Résumé
            optimization_result["summary"] = {
                "total_optimizations": len(optimization_result["optimizations_applied"]),
                "regions_analyzed": len(current_utilization),
                "rebalancing_actions": len(optimization_result["rebalancing_actions"]),
                "global_utilization": global_utilization if total_capacity > 0 else 0
            }
            
            logger.info(
                f"✅ Optimisation régionale terminée: "
                f"{optimization_result['summary']['total_optimizations']} optimisations identifiées"
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur optimisation distribution régionale: {e}")
            
        return optimization_result

    async def manage_cross_region_failover(self, region_health: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔄 GESTION FAILOVER CROSS-RÉGION AVEC DATA LOCALITY
        
        Gestion failover cross-région avec préservation data locality.
        """
        logger.info("🔄 Gestion failover cross-région")
        
        failover_result = {
            "failover_actions": [],
            "traffic_redirections": [],
            "compliance_maintained": True,
            "data_locality_preserved": True,
            "affected_regions": [],
            "recovery_plan": {}
        }
        
        try:
            # Analyse santé régions
            unhealthy_regions = []
            healthy_regions = []
            
            for region_name, health_data in region_health.items():
                health_status = health_data.get("status", "unknown")
                error_rate = health_data.get("error_rate", 0.0)
                response_time = health_data.get("average_response_time", 0.0)
                
                # Critères région unhealthy
                if (health_status == "degraded" or 
                    error_rate > 0.1 or 
                    response_time > self.geo_config.max_latency_threshold_ms):
                    unhealthy_regions.append(region_name)
                else:
                    healthy_regions.append(region_name)
            
            # Traitement failover pour régions unhealthy
            for unhealthy_region in unhealthy_regions:
                region_enum = self._get_region_enum(unhealthy_region)
                if region_enum:
                    # Recherche régions backup appropriées
                    backup_regions = await self._find_backup_regions(
                        region_enum, healthy_regions, region_health
                    )
                    
                    if backup_regions:
                        # Configuration failover
                        failover_action = {
                            "failed_region": unhealthy_region,
                            "backup_regions": [r.value for r in backup_regions],
                            "traffic_split": self._calculate_failover_traffic_split(backup_regions),
                            "failover_timestamp": datetime.now(),
                            "estimated_recovery_time": "15-30 minutes"
                        }
                        
                        failover_result["failover_actions"].append(failover_action)
                        failover_result["affected_regions"].append(unhealthy_region)
                        
                        # Vérification compliance pendant failover
                        compliance_check = await self._verify_failover_compliance(
                            region_enum, backup_regions
                        )
                        
                        if not compliance_check["compliant"]:
                            failover_result["compliance_maintained"] = False
                            logger.warning(f"⚠️ Compliance compromise pendant failover: {compliance_check['issues']}")
                        
                        # Configuration redirection trafic
                        for backup_region in backup_regions:
                            traffic_redirection = {
                                "from_region": unhealthy_region,
                                "to_region": backup_region.value,
                                "traffic_percentage": failover_action["traffic_split"].get(backup_region.value, 0),
                                "latency_impact_ms": await self._estimate_failover_latency_impact(
                                    region_enum, backup_region
                                )
                            }
                            failover_result["traffic_redirections"].append(traffic_redirection)
                    
                    else:
                        logger.error(f"❌ Aucune région backup trouvée pour {unhealthy_region}")
                        failover_result["compliance_maintained"] = False
                        failover_result["data_locality_preserved"] = False
            
            # Plan récupération
            if failover_result["failover_actions"]:
                failover_result["recovery_plan"] = {
                    "monitoring_interval": "1 minute",
                    "health_check_criteria": {
                        "max_error_rate": 0.05,
                        "max_response_time_ms": self.geo_config.max_latency_threshold_ms,
                        "min_success_rate": 0.95
                    },
                    "automatic_fallback": True,
                    "fallback_delay_minutes": 5,
                    "manual_intervention_required": len(unhealthy_regions) > len(healthy_regions) / 2
                }
            
            logger.info(
                f"✅ Failover cross-région terminé: "
                f"{len(failover_result['failover_actions'])} actions failover, "
                f"{len(failover_result['traffic_redirections'])} redirections trafic"
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur gestion failover cross-région: {e}")
            failover_result["error"] = str(e)
            
        return failover_result

    async def integrate_cdn_routing(self, content_type: str, client_location: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 INTÉGRATION ROUTING CDN POUR OPTIMIZATION PERFORMANCE
        
        Intégration routing CDN pour optimization performance content delivery.
        """
        logger.debug(f"🚀 Intégration CDN routing pour {content_type}")
        
        cdn_routing_result = {
            "cdn_endpoint": None,
            "origin_server": None,
            "routing_decision": "origin",
            "performance_improvement": {},
            "cache_strategy": "none",
            "optimization_applied": False
        }
        
        try:
            # Détermination région client
            client_country = client_location.get("country", "US")
            client_region = self._determine_client_region(client_location)
            
            # Vérification éligibilité CDN
            if self._is_cdn_eligible_content(content_type):
                # Recherche endpoint CDN optimal
                cdn_endpoint = await self.cdn_integrator.get_optimal_cdn_endpoint(
                    content_type, client_region
                )
                
                if cdn_endpoint:
                    cdn_routing_result["cdn_endpoint"] = cdn_endpoint
                    cdn_routing_result["routing_decision"] = "cdn"
                    cdn_routing_result["optimization_applied"] = True
                    
                    # Configuration stratégie cache
                    cdn_routing_result["cache_strategy"] = self._determine_cache_strategy(content_type)
                    
                    # Estimation amélioration performance
                    cdn_routing_result["performance_improvement"] = {
                        "estimated_latency_reduction_ms": 50,
                        "estimated_bandwidth_savings_percent": 40,
                        "cache_hit_probability": 0.85 if content_type in ["image", "video", "audio"] else 0.6
                    }
                    
                    logger.debug(f"✅ CDN routing configuré: {cdn_endpoint}")
                
                else:
                    # Fallback vers serveur origine
                    origin_server = await self._select_origin_server(client_location)
                    cdn_routing_result["origin_server"] = origin_server
                    cdn_routing_result["routing_decision"] = "origin_fallback"
            
            else:
                # Content non-éligible CDN, routing direct vers origine
                origin_server = await self._select_origin_server(client_location)
                cdn_routing_result["origin_server"] = origin_server
                cdn_routing_result["routing_decision"] = "origin_direct"
            
        except Exception as e:
            logger.error(f"❌ Erreur intégration CDN routing: {e}")
            cdn_routing_result["error"] = str(e)
            
        return cdn_routing_result
    
    # Méthodes utilitaires privées
    
    def _determine_routing_strategy(self, request_context: Dict[str, Any], client_location: GeoLocation) -> RoutingStrategy:
        """Détermination stratégie routing basée sur contexte"""
        priority_level = request_context.get("priority_level", 5)
        latency_requirement = request_context.get("max_latency_ms", 500)
        compliance_required = request_context.get("compliance_required", False)
        
        if compliance_required:
            return RoutingStrategy.COMPLIANCE_FIRST
        elif latency_requirement < 100:
            return RoutingStrategy.LOWEST_LATENCY
        elif priority_level > 8:
            return RoutingStrategy.PERFORMANCE_OPTIMIZED
        else:
            return self.geo_config.default_strategy
    
    async def _execute_geographic_routing(
        self, 
        client_location: GeoLocation, 
        strategy: RoutingStrategy,
        content_type: str,
        latency_requirement: float,
        compliance_required: bool
    ) -> Dict[str, Any]:
        """Exécution routing géographique selon stratégie"""
        
        # Obtention serveurs candidats
        if compliance_required:
            candidate_servers = self.region_manager.get_compliant_servers(client_location.country)
        else:
            # Tous serveurs sains
            candidate_servers = []
            for servers in self.region_manager.regional_servers.values():
                candidate_servers.extend([s for s in servers if s.is_healthy])
        
        if not candidate_servers:
            return {"success": False, "error": "Aucun serveur candidat disponible"}
        
        # Sélection selon stratégie
        selected_server = None
        
        if strategy == RoutingStrategy.LOWEST_LATENCY:
            # Mesure latence pour tous candidats
            server_latencies = []
            for server in candidate_servers:
                latency = await self.latency_monitor.get_average_latency(client_location, server)
                if latency <= latency_requirement:
                    server_latencies.append((server, latency))
            
            if server_latencies:
                selected_server = min(server_latencies, key=lambda x: x[1])[0]
        
        elif strategy == RoutingStrategy.NEAREST_REGION:
            # Sélection région la plus proche
            nearest_regions = self.region_manager.get_nearest_regions(client_location, 3)
            for region in nearest_regions:
                region_servers = self.region_manager.get_servers_by_region(region)
                if region_servers:
                    # Sélection serveur moins chargé dans région
                    selected_server = min(region_servers, key=lambda s: s.load_percentage)
                    break
        
        elif strategy == RoutingStrategy.LOAD_BALANCED_GEO:
            # Équilibrage charge avec considération géographique
            weighted_servers = []
            for server in candidate_servers:
                distance = client_location.distance_to(server.location)
                load_factor = server.load_percentage / 100.0
                # Score composite: plus faible = meilleur
                score = (distance / 1000.0) + (load_factor * 2.0)
                weighted_servers.append((server, score))
            
            if weighted_servers:
                selected_server = min(weighted_servers, key=lambda x: x[1])[0]
        
        # Fallback si pas de sélection
        if not selected_server and candidate_servers:
            selected_server = candidate_servers[0]
        
        if selected_server:
            return {
                "success": True,
                "selected_server_id": selected_server.server_id,
                "selected_region": selected_server.region.value,
                "server_endpoint": selected_server.endpoint,
                "estimated_latency_ms": await self.latency_monitor.get_average_latency(client_location, selected_server),
                "server_load_percent": selected_server.load_percentage,
                "compliance_satisfied": compliance_required and len(
                    self.region_manager.compliance_mapping.get(client_location.country, set()).intersection(
                        selected_server.compliance_regions
                    )
                ) > 0,
                "cdn_used": selected_server.cdn_enabled and self._is_cdn_eligible_content(content_type)
            }
        else:
            return {"success": False, "error": "Aucun serveur sélectionnable"}
    
    def _get_region_enum(self, region_name: str) -> Optional[GeographicRegion]:
        """Conversion nom région vers enum"""
        try:
            return GeographicRegion(region_name)
        except ValueError:
            return None
    
    async def _find_backup_regions(
        self, 
        failed_region: GeographicRegion, 
        healthy_regions: List[str],
        region_health: Dict[str, Any]
    ) -> List[GeographicRegion]:
        """Recherche régions backup pour failover"""
        backup_regions = []
        
        # Mapping proximité régions (simplifié)
        region_proximity = {
            GeographicRegion.NORTH_AMERICA_EAST: [GeographicRegion.NORTH_AMERICA_CENTRAL, GeographicRegion.NORTH_AMERICA_WEST],
            GeographicRegion.EUROPE_WEST: [GeographicRegion.EUROPE_CENTRAL, GeographicRegion.EUROPE_NORTH],
            GeographicRegion.ASIA_PACIFIC_EAST: [GeographicRegion.ASIA_PACIFIC_SOUTHEAST, GeographicRegion.ASIA_PACIFIC_SOUTH],
        }
        
        # Recherche régions proches saines
        preferred_backups = region_proximity.get(failed_region, [])
        for backup_region in preferred_backups:
            if backup_region.value in healthy_regions:
                backup_regions.append(backup_region)
        
        # Ajout autres régions saines si nécessaire
        while len(backup_regions) < self.geo_config.backup_regions_per_primary:
            for region_name in healthy_regions:
                region_enum = self._get_region_enum(region_name)
                if region_enum and region_enum not in backup_regions:
                    backup_regions.append(region_enum)
                    break
            break  # Éviter boucle infinie
        
        return backup_regions[:self.geo_config.backup_regions_per_primary]
    
    def _calculate_failover_traffic_split(self, backup_regions: List[GeographicRegion]) -> Dict[str, float]:
        """Calcul répartition trafic failover"""
        if not backup_regions:
            return {}
        
        # Répartition égale par défaut
        split_percentage = 100.0 / len(backup_regions)
        
        return {region.value: split_percentage for region in backup_regions}
    
    async def _verify_failover_compliance(
        self, 
        failed_region: GeographicRegion, 
        backup_regions: List[GeographicRegion]
    ) -> Dict[str, Any]:
        """Vérification compliance pendant failover"""
        compliance_result = {
            "compliant": True,
            "issues": [],
            "recommendations": []
        }
        
        # Vérification capacité compliance régions backup
        for backup_region in backup_regions:
            backup_servers = self.region_manager.get_servers_by_region(backup_region)
            
            # Vérifier si régions backup supportent toutes compliance requirements
            # Implementation simplifiée - peut être étendue selon besoins spécifiques
            if not backup_servers:
                compliance_result["issues"].append(f"Région backup {backup_region.value} sans serveurs")
                compliance_result["compliant"] = False
        
        return compliance_result
    
    async def _estimate_failover_latency_impact(
        self, 
        failed_region: GeographicRegion, 
        backup_region: GeographicRegion
    ) -> float:
        """Estimation impact latence failover"""
        # Calcul approximatif basé sur distance géographique
        # À améliorer avec vraies mesures
        base_impact = 20.0  # 20ms base
        
        # Ajustement selon distance régions (approximation)
        if failed_region == backup_region:
            return 0.0
        
        # Impact plus élevé pour failover cross-continent
        cross_continent_pairs = [
            (GeographicRegion.NORTH_AMERICA_EAST, GeographicRegion.EUROPE_WEST),
            (GeographicRegion.EUROPE_WEST, GeographicRegion.ASIA_PACIFIC_EAST),
            (GeographicRegion.NORTH_AMERICA_WEST, GeographicRegion.ASIA_PACIFIC_EAST),
        ]
        
        for pair in cross_continent_pairs:
            if (failed_region, backup_region) == pair or (backup_region, failed_region) == pair:
                return base_impact * 3.0
        
        return base_impact
    
    def _determine_client_region(self, client_location: Dict[str, Any]) -> GeographicRegion:
        """Détermination région client basée sur localisation"""
        country = client_location.get("country", "US")
        continent = client_location.get("continent", "North America")
        
        # Mapping simplifié pays -> région
        country_region_mapping = {
            "US": GeographicRegion.NORTH_AMERICA_EAST,
            "CA": GeographicRegion.NORTH_AMERICA_EAST,
            "GB": GeographicRegion.EUROPE_WEST,
            "DE": GeographicRegion.EUROPE_CENTRAL,
            "FR": GeographicRegion.EUROPE_WEST,
            "JP": GeographicRegion.ASIA_PACIFIC_EAST,
            "SG": GeographicRegion.ASIA_PACIFIC_SOUTHEAST,
            "AU": GeographicRegion.OCEANIA,
        }
        
        return country_region_mapping.get(country, GeographicRegion.NORTH_AMERICA_EAST)
    
    def _is_cdn_eligible_content(self, content_type: str) -> bool:
        """Vérification éligibilité CDN pour type contenu"""
        cdn_eligible_types = ["image", "video", "audio", "static", "css", "js", "font"]
        return content_type.lower() in cdn_eligible_types
    
    def _determine_cache_strategy(self, content_type: str) -> str:
        """Détermination stratégie cache basée sur type contenu"""
        cache_strategies = {
            "image": "long_term",      # 24h+
            "video": "streaming",      # Streaming optimisé
            "audio": "streaming",      # Streaming optimisé  
            "static": "immutable",     # Cache permanent
            "css": "versioned",        # Cache avec versioning
            "js": "versioned",         # Cache avec versioning
            "api": "no_cache"          # Pas de cache
        }
        
        return cache_strategies.get(content_type.lower(), "default")
    
    async def _select_origin_server(self, client_location: Dict[str, Any]) -> Optional[str]:
        """Sélection serveur origine pour fallback"""
        try:
            client_region = self._determine_client_region(client_location)
            region_servers = self.region_manager.get_servers_by_region(client_region)
            
            if region_servers:
                # Sélection serveur moins chargé
                best_server = min(region_servers, key=lambda s: s.load_percentage)
                return best_server.endpoint
            
            # Fallback vers n'importe quel serveur sain
            for servers in self.region_manager.regional_servers.values():
                healthy_servers = [s for s in servers if s.is_healthy]
                if healthy_servers:
                    return healthy_servers[0].endpoint
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur sélection serveur origine: {e}")
            return None

# Point d'entrée pour tests et démonstration
async def main():
    """Démonstration Geographic Load Balancer"""
    logger.info("🚀 Démonstration Geographic Load Balancer")
    
    # Configuration géographique
    geo_config = GeographicConfig(
        default_strategy=RoutingStrategy.LOWEST_LATENCY,
        max_latency_threshold_ms=300.0,
        enable_cdn_routing=True,
        enable_compliance_routing=True
    )
    
    # Initialisation load balancer géographique
    geo_lb = GeographicLoadBalancer(geo_config)
    
    # Test routing géographique
    test_ips = [
        "192.168.1.100",  # Simule US
        "10.0.0.50",      # Simule UK  
        "172.16.0.25"     # Simule JP
    ]
    
    for test_ip in test_ips:
        request_context = {
            "content_type": "api",
            "priority_level": 7,
            "compliance_required": True,
            "max_latency_ms": 200.0
        }
        
        routing_result = await geo_lb.route_by_geography(test_ip, request_context)
        
        logger.info(f"🌍 Routing IP {test_ip}: "
                   f"serveur={routing_result.get('selected_server_id', 'none')}, "
                   f"région={routing_result.get('selected_region', 'none')}")
    
    # Test optimisation régionale
    traffic_patterns = {
        "regional_distribution": {
            "na-east": {"traffic_percentage": 45.0, "peak_hours": [14, 15, 16]},
            "eu-west": {"traffic_percentage": 35.0, "peak_hours": [9, 10, 11]},
            "ap-east": {"traffic_percentage": 20.0, "peak_hours": [2, 3, 4]}
        }
    }
    
    optimization_result = await geo_lb.optimize_regional_distribution(traffic_patterns)
    logger.info(f"⚖️ Optimisation régionale: {optimization_result['summary']['total_optimizations']} actions")
    
    # Test failover cross-région
    region_health = {
        "na-east": {"status": "degraded", "error_rate": 0.15, "average_response_time": 800},
        "eu-west": {"status": "healthy", "error_rate": 0.02, "average_response_time": 120},
        "ap-east": {"status": "healthy", "error_rate": 0.01, "average_response_time": 95}
    }
    
    failover_result = await geo_lb.manage_cross_region_failover(region_health)
    logger.info(f"🔄 Failover cross-région: {len(failover_result['failover_actions'])} actions")
    
    logger.info("✅ Démonstration terminée avec succès")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())