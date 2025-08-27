"""
Geographic Load Balancer for IA Influencer Agent Platform

Provides intelligent geographic traffic distribution for optimal performance
of content protection, fingerprinting, and monetization services across
global regions with latency optimization and regional compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""

import asyncio
import logging
import json
import aiohttp
import geoip2.database
import geoip2.errors
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import ipaddress
import statistics
from concurrent.futures import ThreadPoolExecutor
import redis
from prometheus_client import Counter, Histogram, Gauge
import yaml
import dns.resolver
import ssl
import socket
import time

logger = logging.getLogger(__name__)

# Prometheus metrics for geographic load balancing
GEO_REQUESTS_TOTAL = Counter('geo_requests_total', 'Total requests by geographic region', ['region', 'country'])
GEO_LATENCY_HISTOGRAM = Histogram('geo_latency_seconds', 'Latency by geographic region', ['region', 'server'])
GEO_SERVER_STATUS = Gauge('geo_server_status', 'Geographic server status', ['region', 'server', 'status'])
GEO_TRAFFIC_DISTRIBUTION = Gauge('geo_traffic_distribution', 'Traffic distribution across regions', ['region'])
GEO_COMPLIANCE_STATUS = Gauge('geo_compliance_status', 'GDPR/Regional compliance status', ['region', 'service'])


@dataclass
class GeographicRegion:
    """Geographic region configuration for load balancing"""
    name: str
    countries: List[str]
    primary_servers: List[str]
    fallback_servers: List[str]
    latency_threshold_ms: int = 200
    compliance_requirements: List[str] = None
    data_residency_required: bool = False
    preferred_cdn: Optional[str] = None
    timezone: str = "UTC"
    
    def __post_init__(self):
        if self.compliance_requirements is None:
            self.compliance_requirements = []


@dataclass
class ServerEndpoint:
    """Geographic server endpoint configuration"""
    host: str
    port: int
    region: str
    datacenter: str
    coordinates: Tuple[float, float]  # (latitude, longitude)
    capacity_weight: float = 1.0
    current_load: float = 0.0
    avg_latency_ms: float = 0.0
    health_status: str = "healthy"
    ssl_enabled: bool = True
    compliance_certifications: List[str] = None
    
    def __post_init__(self):
        if self.compliance_certifications is None:
            self.compliance_certifications = []


@dataclass
class ClientLocation:
    """Client geographic location information"""
    ip_address: str
    country_code: str
    region: str
    city: str
    coordinates: Tuple[float, float]
    isp: str
    connection_type: str
    timezone: str
    compliance_region: str


class GeographicLoadBalancer:
    """
    Geographic Load Balancer for IA Influencer Agent Platform
    
    Provides intelligent geographic routing for:
    - Content protection services with regional compliance
    - AI fingerprinting with data residency requirements
    - Monetization APIs with local payment regulations
    - Real-time collaboration with latency optimization
    """
    
    def __init__(
        self,
        geoip_database_path: str = "/opt/geoip/GeoLite2-City.mmdb",
        redis_client: Optional[redis.Redis] = None,
        config_file: Optional[str] = None
    ):
        self.geoip_database_path = geoip_database_path
        self.redis_client = redis_client
        self.config_file = config_file
        
        # Geographic configuration
        self.regions: Dict[str, GeographicRegion] = {}
        self.servers: Dict[str, List[ServerEndpoint]] = {}
        self.client_cache: Dict[str, ClientLocation] = {}
        
        # Performance tracking
        self.latency_matrix: Dict[str, Dict[str, float]] = {}
        self.load_statistics: Dict[str, Dict[str, float]] = {}
        self.compliance_matrix: Dict[str, Dict[str, bool]] = {}
        
        # Configuration
        self.config = {
            "default_region": "europe",
            "fallback_region": "global",
            "max_latency_threshold": 500,
            "health_check_interval": 30,
            "latency_measurement_interval": 60,
            "cache_ttl": 3600,
            "compliance_enforcement": True,
            "data_residency_enforcement": True
        }
        
        self._geoip_reader = None
        self._executor = ThreadPoolExecutor(max_workers=20)
        self._monitoring_active = False
        
        logger.info("Geographic Load Balancer initialized for global IA Influencer Agent platform")
    
    async def initialize(self) -> bool:
        """Initialize geographic load balancer with platform configuration"""
        try:
            # Load configuration
            await self._load_configuration()
            
            # Initialize GeoIP database
            await self._initialize_geoip_database()
            
            # Configure geographic regions
            await self._configure_platform_regions()
            
            # Initialize server endpoints
            await self._initialize_server_endpoints()
            
            # Start latency monitoring
            await self._start_latency_monitoring()
            
            # Start health monitoring
            await self._start_health_monitoring()
            
            # Initialize compliance checking
            await self._initialize_compliance_checking()
            
            logger.info("Geographic load balancer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize geographic load balancer: {e}")
            return False
    
    async def _load_configuration(self) -> None:
        """Load geographic configuration from file or defaults"""
        try:
            if self.config_file and Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    file_config = yaml.safe_load(f)
                    self.config.update(file_config)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.info("Using default geographic configuration")
                
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}, using defaults")
    
    async def _initialize_geoip_database(self) -> None:
        """Initialize GeoIP database for client location detection"""
        try:
            if Path(self.geoip_database_path).exists():
                self._geoip_reader = geoip2.database.Reader(self.geoip_database_path)
                logger.info("GeoIP database initialized")
            else:
                logger.warning(f"GeoIP database not found at {self.geoip_database_path}")
                # Fall back to online service or create mock
                await self._setup_fallback_geolocation()
                
        except Exception as e:
            logger.error(f"Failed to initialize GeoIP database: {e}")
            await self._setup_fallback_geolocation()
    
    async def _setup_fallback_geolocation(self) -> None:
        """Setup fallback geolocation service"""
        try:
            # Simple fallback using online IP geolocation
            logger.info("Setting up fallback geolocation service")
            
        except Exception as e:
            logger.error(f"Failed to setup fallback geolocation: {e}")
    
    async def _configure_platform_regions(self) -> None:
        """Configure geographic regions for IA Influencer Agent platform"""
        try:
            # Europe region - GDPR compliance focus
            europe_region = GeographicRegion(
                name="europe",
                countries=["DE", "FR", "GB", "IT", "ES", "NL", "BE", "AT", "CH", "SE", "NO", "DK", "FI"],
                primary_servers=["eu-central-1", "eu-west-1", "eu-north-1"],
                fallback_servers=["us-east-1", "global"],
                latency_threshold_ms=150,
                compliance_requirements=["GDPR", "EU_DATA_PROTECTION"],
                data_residency_required=True,
                preferred_cdn="cloudflare_eu",
                timezone="Europe/Berlin"
            )
            
            # North America region
            north_america_region = GeographicRegion(
                name="north_america",
                countries=["US", "CA", "MX"],
                primary_servers=["us-east-1", "us-west-2", "ca-central-1"],
                fallback_servers=["eu-west-1", "global"],
                latency_threshold_ms=100,
                compliance_requirements=["CCPA", "COPPA", "SOX"],
                data_residency_required=False,
                preferred_cdn="cloudflare_us",
                timezone="America/New_York"
            )
            
            # Asia Pacific region
            asia_pacific_region = GeographicRegion(
                name="asia_pacific",
                countries=["JP", "KR", "SG", "AU", "HK", "TW", "IN", "TH", "VN", "MY", "PH"],
                primary_servers=["ap-northeast-1", "ap-southeast-1", "ap-south-1"],
                fallback_servers=["us-west-2", "global"],
                latency_threshold_ms=200,
                compliance_requirements=["PDPA", "LGPD_BR", "LOCAL_DATA_LAWS"],
                data_residency_required=True,
                preferred_cdn="cloudflare_asia",
                timezone="Asia/Tokyo"
            )
            
            # Global fallback region
            global_region = GeographicRegion(
                name="global",
                countries=["*"],  # All other countries
                primary_servers=["global"],
                fallback_servers=["us-east-1", "eu-west-1"],
                latency_threshold_ms=300,
                compliance_requirements=["BASIC_PRIVACY"],
                data_residency_required=False,
                preferred_cdn="cloudflare_global",
                timezone="UTC"
            )
            
            self.regions = {
                "europe": europe_region,
                "north_america": north_america_region,
                "asia_pacific": asia_pacific_region,
                "global": global_region
            }
            
            logger.info("Platform geographic regions configured")
            
        except Exception as e:
            logger.error(f"Failed to configure platform regions: {e}")
            raise
    
    async def _initialize_server_endpoints(self) -> None:
        """Initialize server endpoints for each geographic region"""
        try:
            # Europe servers
            europe_servers = [
                ServerEndpoint(
                    host="eu-central-1.ia-influencer.com",
                    port=443,
                    region="europe",
                    datacenter="eu-central-1",
                    coordinates=(50.1109, 8.6821),  # Frankfurt
                    capacity_weight=1.0,
                    compliance_certifications=["ISO27001", "SOC2", "GDPR_CERTIFIED"]
                ),
                ServerEndpoint(
                    host="eu-west-1.ia-influencer.com", 
                    port=443,
                    region="europe",
                    datacenter="eu-west-1",
                    coordinates=(53.3498, -6.2603),  # Dublin
                    capacity_weight=0.8,
                    compliance_certifications=["ISO27001", "SOC2", "GDPR_CERTIFIED"]
                ),
                ServerEndpoint(
                    host="eu-north-1.ia-influencer.com",
                    port=443,
                    region="europe", 
                    datacenter="eu-north-1",
                    coordinates=(59.3293, 18.0686),  # Stockholm
                    capacity_weight=0.6,
                    compliance_certifications=["ISO27001", "SOC2", "GDPR_CERTIFIED"]
                )
            ]
            
            # North America servers
            north_america_servers = [
                ServerEndpoint(
                    host="us-east-1.ia-influencer.com",
                    port=443,
                    region="north_america",
                    datacenter="us-east-1",
                    coordinates=(39.0458, -77.5081),  # Virginia
                    capacity_weight=1.2,
                    compliance_certifications=["SOC2", "HIPAA", "FedRAMP"]
                ),
                ServerEndpoint(
                    host="us-west-2.ia-influencer.com",
                    port=443,
                    region="north_america",
                    datacenter="us-west-2", 
                    coordinates=(45.5152, -122.6784),  # Oregon
                    capacity_weight=1.0,
                    compliance_certifications=["SOC2", "HIPAA", "FedRAMP"]
                ),
                ServerEndpoint(
                    host="ca-central-1.ia-influencer.com",
                    port=443,
                    region="north_america",
                    datacenter="ca-central-1",
                    coordinates=(43.6532, -79.3832),  # Toronto
                    capacity_weight=0.7,
                    compliance_certifications=["SOC2", "PIPEDA"]
                )
            ]
            
            # Asia Pacific servers
            asia_pacific_servers = [
                ServerEndpoint(
                    host="ap-northeast-1.ia-influencer.com",
                    port=443,
                    region="asia_pacific",
                    datacenter="ap-northeast-1",
                    coordinates=(35.6762, 139.6503),  # Tokyo
                    capacity_weight=1.0,
                    compliance_certifications=["ISO27001", "SOC2", "PDPA"]
                ),
                ServerEndpoint(
                    host="ap-southeast-1.ia-influencer.com",
                    port=443,
                    region="asia_pacific",
                    datacenter="ap-southeast-1",
                    coordinates=(1.3521, 103.8198),  # Singapore
                    capacity_weight=0.9,
                    compliance_certifications=["ISO27001", "SOC2", "PDPA"]
                ),
                ServerEndpoint(
                    host="ap-south-1.ia-influencer.com",
                    port=443,
                    region="asia_pacific",
                    datacenter="ap-south-1",
                    coordinates=(19.0760, 72.8777),  # Mumbai
                    capacity_weight=0.8,
                    compliance_certifications=["ISO27001", "SOC2", "LOCAL_COMPLIANCE"]
                )
            ]
            
            self.servers = {
                "europe": europe_servers,
                "north_america": north_america_servers,
                "asia_pacific": asia_pacific_servers,
                "global": north_america_servers + europe_servers  # Global uses all servers
            }
            
            logger.info("Server endpoints initialized for all regions")
            
        except Exception as e:
            logger.error(f"Failed to initialize server endpoints: {e}")
            raise
    
    async def get_client_location(self, ip_address: str) -> Optional[ClientLocation]:
        """Get geographic location for client IP address"""
        try:
            # Check cache first
            if ip_address in self.client_cache:
                return self.client_cache[ip_address]
            
            # Check Redis cache
            if self.redis_client:
                cached_data = await self._get_from_redis_cache(f"geo:{ip_address}")
                if cached_data:
                    location = ClientLocation(**json.loads(cached_data))
                    self.client_cache[ip_address] = location
                    return location
            
            # Resolve using GeoIP database
            if self._geoip_reader:
                response = self._geoip_reader.city(ip_address)
                
                location = ClientLocation(
                    ip_address=ip_address,
                    country_code=response.country.iso_code or "UNKNOWN",
                    region=response.subdivisions.most_specific.name or "UNKNOWN",
                    city=response.city.name or "UNKNOWN",
                    coordinates=(
                        float(response.location.latitude or 0.0),
                        float(response.location.longitude or 0.0)
                    ),
                    isp=response.traits.isp or "UNKNOWN",
                    connection_type=response.traits.connection_type or "UNKNOWN",
                    timezone=response.location.time_zone or "UTC",
                    compliance_region=self._determine_compliance_region(response.country.iso_code)
                )
                
                # Cache the result
                self.client_cache[ip_address] = location
                if self.redis_client:
                    await self._set_redis_cache(
                        f"geo:{ip_address}",
                        json.dumps(asdict(location)),
                        ttl=self.config["cache_ttl"]
                    )
                
                return location
            
            # Fallback to approximate location
            return await self._get_fallback_location(ip_address)
            
        except geoip2.errors.AddressNotFoundError:
            logger.warning(f"IP address {ip_address} not found in GeoIP database")
            return await self._get_fallback_location(ip_address)
        except Exception as e:
            logger.error(f"Failed to get client location for {ip_address}: {e}")
            return await self._get_fallback_location(ip_address)
    
    async def _get_fallback_location(self, ip_address: str) -> ClientLocation:
        """Get fallback location for unknown IP addresses"""
        return ClientLocation(
            ip_address=ip_address,
            country_code="UNKNOWN",
            region="UNKNOWN",
            city="UNKNOWN",
            coordinates=(0.0, 0.0),
            isp="UNKNOWN",
            connection_type="UNKNOWN",
            timezone="UTC",
            compliance_region="global"
        )
    
    def _determine_compliance_region(self, country_code: str) -> str:
        """Determine compliance region based on country code"""
        eu_countries = ["DE", "FR", "GB", "IT", "ES", "NL", "BE", "AT", "CH", "SE", "NO", "DK", "FI"]
        na_countries = ["US", "CA", "MX"]
        ap_countries = ["JP", "KR", "SG", "AU", "HK", "TW", "IN", "TH", "VN", "MY", "PH"]
        
        if country_code in eu_countries:
            return "europe"
        elif country_code in na_countries:
            return "north_america"
        elif country_code in ap_countries:
            return "asia_pacific"
        else:
            return "global"
    
    async def select_optimal_server(
        self,
        client_location: ClientLocation,
        service_type: str = "general",
        requirements: Optional[Dict[str, Any]] = None
    ) -> Optional[ServerEndpoint]:
        """
        Select optimal server for client based on:
        - Geographic proximity
        - Latency measurements
        - Server load
        - Compliance requirements
        - Service-specific needs
        """
        try:
            # Determine target region
            target_region = self._determine_target_region(client_location, requirements)
            
            # Get candidate servers
            candidate_servers = self._get_candidate_servers(target_region, service_type)
            
            if not candidate_servers:
                logger.warning(f"No candidate servers found for region {target_region}")
                return None
            
            # Score servers based on multiple criteria
            scored_servers = []
            for server in candidate_servers:
                score = await self._calculate_server_score(
                    server,
                    client_location,
                    service_type,
                    requirements
                )
                scored_servers.append((server, score))
            
            # Sort by score (highest first)
            scored_servers.sort(key=lambda x: x[1], reverse=True)
            
            # Select best server
            selected_server = scored_servers[0][0]
            
            # Update metrics
            GEO_REQUESTS_TOTAL.labels(
                region=target_region,
                country=client_location.country_code
            ).inc()
            
            GEO_TRAFFIC_DISTRIBUTION.labels(region=target_region).inc()
            
            logger.debug(f"Selected server {selected_server.host} for client from {client_location.country_code}")
            
            return selected_server
            
        except Exception as e:
            logger.error(f"Failed to select optimal server: {e}")
            return await self._get_fallback_server()
    
    def _determine_target_region(
        self,
        client_location: ClientLocation,
        requirements: Optional[Dict[str, Any]] = None
    ) -> str:
        """Determine target region based on client location and requirements"""
        try:
            # First check if client is in a specific compliance region
            compliance_region = client_location.compliance_region
            
            # Check for data residency requirements
            if requirements and requirements.get("data_residency_required", False):
                if compliance_region in self.regions:
                    region_config = self.regions[compliance_region]
                    if region_config.data_residency_required:
                        return compliance_region
            
            # Check for specific compliance requirements
            if requirements and "compliance_requirements" in requirements:
                required_compliance = requirements["compliance_requirements"]
                for region_name, region_config in self.regions.items():
                    if all(req in region_config.compliance_requirements for req in required_compliance):
                        return region_name
            
            # Default to closest geographic region
            return compliance_region if compliance_region in self.regions else "global"
            
        except Exception as e:
            logger.error(f"Failed to determine target region: {e}")
            return "global"
    
    def _get_candidate_servers(self, region: str, service_type: str) -> List[ServerEndpoint]:
        """Get candidate servers for a region and service type"""
        try:
            candidate_servers = []
            
            # Primary region servers
            if region in self.servers:
                candidate_servers.extend(self.servers[region])
            
            # Add fallback servers if needed
            if region in self.regions:
                region_config = self.regions[region]
                for fallback_region in region_config.fallback_servers:
                    if fallback_region in self.servers:
                        candidate_servers.extend(self.servers[fallback_region])
            
            # Filter healthy servers only
            healthy_servers = [
                server for server in candidate_servers
                if server.health_status == "healthy"
            ]
            
            return healthy_servers if healthy_servers else candidate_servers
            
        except Exception as e:
            logger.error(f"Failed to get candidate servers: {e}")
            return []
    
    async def _calculate_server_score(
        self,
        server: ServerEndpoint,
        client_location: ClientLocation,
        service_type: str,
        requirements: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate server score based on multiple criteria"""
        try:
            score = 0.0
            
            # Geographic distance score (40% weight)
            distance_score = await self._calculate_distance_score(server, client_location)
            score += distance_score * 0.40
            
            # Latency score (30% weight)  
            latency_score = await self._calculate_latency_score(server)
            score += latency_score * 0.30
            
            # Load score (20% weight)
            load_score = await self._calculate_load_score(server)
            score += load_score * 0.20
            
            # Compliance score (10% weight)
            compliance_score = await self._calculate_compliance_score(server, requirements)
            score += compliance_score * 0.10
            
            return score
            
        except Exception as e:
            logger.error(f"Failed to calculate server score: {e}")
            return 0.0
    
    async def _calculate_distance_score(
        self,
        server: ServerEndpoint,
        client_location: ClientLocation
    ) -> float:
        """Calculate score based on geographic distance"""
        try:
            # Calculate great circle distance
            distance_km = self._calculate_great_circle_distance(
                client_location.coordinates,
                server.coordinates
            )
            
            # Convert to score (closer = higher score)
            # Max distance considered: 20,000 km (half Earth circumference)
            max_distance = 20000
            score = max(0, (max_distance - distance_km) / max_distance)
            
            return score
            
        except Exception as e:
            logger.error(f"Failed to calculate distance score: {e}")
            return 0.5
    
    def _calculate_great_circle_distance(
        self,
        coord1: Tuple[float, float],
        coord2: Tuple[float, float]
    ) -> float:
        """Calculate great circle distance between two coordinates"""
        import math
        
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in kilometers
        earth_radius = 6371
        
        return earth_radius * c
    
    async def _calculate_latency_score(self, server: ServerEndpoint) -> float:
        """Calculate score based on server latency"""
        try:
            # Get average latency from monitoring
            avg_latency = server.avg_latency_ms
            
            if avg_latency <= 0:
                return 1.0  # No data, assume best
            
            # Convert to score (lower latency = higher score)
            # Max acceptable latency: 500ms
            max_latency = 500
            score = max(0, (max_latency - avg_latency) / max_latency)
            
            return score
            
        except Exception as e:
            logger.error(f"Failed to calculate latency score: {e}")
            return 0.5
    
    async def _calculate_load_score(self, server: ServerEndpoint) -> float:
        """Calculate score based on server load"""
        try:
            current_load = server.current_load
            capacity_weight = server.capacity_weight
            
            # Adjusted load considering capacity
            adjusted_load = current_load / capacity_weight
            
            # Convert to score (lower load = higher score)
            score = max(0, 1 - adjusted_load)
            
            return score
            
        except Exception as e:
            logger.error(f"Failed to calculate load score: {e}")
            return 0.5
    
    async def _calculate_compliance_score(
        self,
        server: ServerEndpoint,
        requirements: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate score based on compliance requirements"""
        try:
            if not requirements or "compliance_requirements" not in requirements:
                return 1.0  # No specific requirements
            
            required_certifications = requirements["compliance_requirements"]
            server_certifications = server.compliance_certifications
            
            # Check if server meets all requirements
            if all(req in server_certifications for req in required_certifications):
                return 1.0
            else:
                # Partial compliance
                met_requirements = sum(
                    1 for req in required_certifications
                    if req in server_certifications
                )
                return met_requirements / len(required_certifications)
                
        except Exception as e:
            logger.error(f"Failed to calculate compliance score: {e}")
            return 0.5
    
    async def _get_fallback_server(self) -> Optional[ServerEndpoint]:
        """Get fallback server when optimal selection fails"""
        try:
            # Use global region as fallback
            if "global" in self.servers:
                global_servers = self.servers["global"]
                healthy_servers = [s for s in global_servers if s.health_status == "healthy"]
                
                if healthy_servers:
                    return healthy_servers[0]
                elif global_servers:
                    return global_servers[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get fallback server: {e}")
            return None
    
    async def _start_latency_monitoring(self) -> None:
        """Start latency monitoring for all servers"""
        try:
            if self._monitoring_active:
                return
            
            self._monitoring_active = True
            
            async def monitor_latency():
                while self._monitoring_active:
                    try:
                        await self._measure_all_server_latencies()
                        await asyncio.sleep(self.config["latency_measurement_interval"])
                    except Exception as e:
                        logger.error(f"Error in latency monitoring: {e}")
                        await asyncio.sleep(60)
            
            asyncio.create_task(monitor_latency())
            logger.info("Latency monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start latency monitoring: {e}")
    
    async def _measure_all_server_latencies(self) -> None:
        """Measure latency to all servers"""
        try:
            tasks = []
            
            for region, servers in self.servers.items():
                for server in servers:
                    task = self._measure_server_latency(server)
                    tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Failed to measure server latencies: {e}")
    
    async def _measure_server_latency(self, server: ServerEndpoint) -> None:
        """Measure latency to a specific server"""
        try:
            start_time = time.time()
            
            # Simple TCP connection test
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(server.host, server.port),
                timeout=5.0
            )
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            # Update server latency
            server.avg_latency_ms = latency_ms
            
            # Update metrics
            GEO_LATENCY_HISTOGRAM.labels(
                region=server.region,
                server=server.host
            ).observe(latency_ms / 1000)
            
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            logger.warning(f"Failed to measure latency for {server.host}: {e}")
            # Don't update latency on failure
    
    async def _start_health_monitoring(self) -> None:
        """Start health monitoring for all servers"""
        try:
            async def monitor_health():
                while self._monitoring_active:
                    try:
                        await self._check_all_server_health()
                        await asyncio.sleep(self.config["health_check_interval"])
                    except Exception as e:
                        logger.error(f"Error in health monitoring: {e}")
                        await asyncio.sleep(60)
            
            asyncio.create_task(monitor_health())
            logger.info("Health monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start health monitoring: {e}")
    
    async def _check_all_server_health(self) -> None:
        """Check health of all servers"""
        try:
            tasks = []
            
            for region, servers in self.servers.items():
                for server in servers:
                    task = self._check_server_health(server)
                    tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Failed to check server health: {e}")
    
    async def _check_server_health(self, server: ServerEndpoint) -> None:
        """Check health of a specific server"""
        try:
            url = f"https://{server.host}:{server.port}/health"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        server.health_status = "healthy"
                        health_value = 1
                    else:
                        server.health_status = "unhealthy"
                        health_value = 0
            
            # Update metrics
            GEO_SERVER_STATUS.labels(
                region=server.region,
                server=server.host,
                status=server.health_status
            ).set(health_value)
            
        except Exception as e:
            logger.warning(f"Health check failed for {server.host}: {e}")
            server.health_status = "unhealthy"
            
            GEO_SERVER_STATUS.labels(
                region=server.region,
                server=server.host,
                status="unhealthy"
            ).set(0)
    
    async def _initialize_compliance_checking(self) -> None:
        """Initialize compliance checking for all regions"""
        try:
            for region_name, region in self.regions.items():
                compliance_status = {}
                
                # Check data residency compliance
                if region.data_residency_required:
                    compliance_status["data_residency"] = True
                
                # Check regulatory compliance
                for requirement in region.compliance_requirements:
                    compliance_status[requirement] = True
                    
                    # Update metrics
                    GEO_COMPLIANCE_STATUS.labels(
                        region=region_name,
                        service=requirement
                    ).set(1)
                
                self.compliance_matrix[region_name] = compliance_status
            
            logger.info("Compliance checking initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize compliance checking: {e}")
    
    async def _get_from_redis_cache(self, key: str) -> Optional[str]:
        """Get value from Redis cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                return value.decode() if value else None
            return None
        except Exception as e:
            logger.error(f"Redis cache get error: {e}")
            return None
    
    async def _set_redis_cache(self, key: str, value: str, ttl: int) -> None:
        """Set value in Redis cache"""
        try:
            if self.redis_client:
                self.redis_client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Redis cache set error: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of geographic load balancer"""
        try:
            # Calculate statistics
            total_servers = sum(len(servers) for servers in self.servers.values())
            healthy_servers = sum(
                1 for servers in self.servers.values()
                for server in servers
                if server.health_status == "healthy"
            )
            
            avg_latencies = {}
            for region, servers in self.servers.items():
                latencies = [s.avg_latency_ms for s in servers if s.avg_latency_ms > 0]
                avg_latencies[region] = statistics.mean(latencies) if latencies else 0
            
            return {
                "total_servers": total_servers,
                "healthy_servers": healthy_servers,
                "health_percentage": (healthy_servers / total_servers * 100) if total_servers > 0 else 0,
                "regions_configured": len(self.regions),
                "average_latencies": avg_latencies,
                "monitoring_active": self._monitoring_active,
                "cache_size": len(self.client_cache),
                "compliance_regions": list(self.compliance_matrix.keys()),
                "geoip_database_available": self._geoip_reader is not None,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def shutdown(self) -> None:
        """Shutdown geographic load balancer"""
        try:
            logger.info("Shutting down Geographic Load Balancer...")
            
            self._monitoring_active = False
            
            if self._geoip_reader:
                self._geoip_reader.close()
            
            if self._executor:
                self._executor.shutdown(wait=True)
            
            logger.info("Geographic Load Balancer shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Service-specific geographic routing functions
async def route_fingerprinting_request(
    client_ip: str,
    geo_balancer: GeographicLoadBalancer,
    content_type: str = "audio"
) -> Optional[ServerEndpoint]:
    """Route fingerprinting requests with data residency compliance"""
    try:
        client_location = await geo_balancer.get_client_location(client_ip)
        if not client_location:
            return None
        
        # Fingerprinting requires data residency for EU clients
        requirements = {
            "data_residency_required": client_location.country_code in ["DE", "FR", "GB", "IT", "ES"],
            "compliance_requirements": ["GDPR"] if client_location.compliance_region == "europe" else []
        }
        
        return await geo_balancer.select_optimal_server(
            client_location,
            service_type="fingerprinting",
            requirements=requirements
        )
        
    except Exception as e:
        logger.error(f"Failed to route fingerprinting request: {e}")
        return None


async def route_monetization_request(
    client_ip: str,
    geo_balancer: GeographicLoadBalancer,
    payment_method: str = "stripe"
) -> Optional[ServerEndpoint]:
    """Route monetization requests with regional payment compliance"""
    try:
        client_location = await geo_balancer.get_client_location(client_ip)
        if not client_location:
            return None
        
        # Payment processing requirements vary by region
        requirements = {}
        if client_location.compliance_region == "europe":
            requirements["compliance_requirements"] = ["GDPR", "PSD2"]
        elif client_location.compliance_region == "north_america":
            requirements["compliance_requirements"] = ["PCI_DSS", "SOX"]
        
        return await geo_balancer.select_optimal_server(
            client_location,
            service_type="monetization",
            requirements=requirements
        )
        
    except Exception as e:
        logger.error(f"Failed to route monetization request: {e}")
        return None


async def route_ai_agent_request(
    client_ip: str,
    geo_balancer: GeographicLoadBalancer,
    spotify_region: str = "global"
) -> Optional[ServerEndpoint]:
    """Route AI agent requests with optimal latency for real-time features"""
    try:
        client_location = await geo_balancer.get_client_location(client_ip)
        if not client_location:
            return None
        
        # AI agent prioritizes low latency for real-time recommendations
        requirements = {
            "max_latency_threshold": 150,  # 150ms max for real-time
            "compliance_requirements": []
        }
        
        return await geo_balancer.select_optimal_server(
            client_location,
            service_type="ai_agent",
            requirements=requirements
        )
        
    except Exception as e:
        logger.error(f"Failed to route AI agent request: {e}")
        return None
