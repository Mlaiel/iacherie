"""🌍 Geospatial Intelligence & Surveillance Engine
===============================================

Ultra-advanced geospatial monitoring system with geopolitical analysis,
territorial risk assessment, and international enforcement coordination.

Industrial Features:
- Real-time geospatial threat mapping
- Geopolitical risk analysis and jurisdiction assessment
- International law enforcement coordination
- Territorial pattern analysis and border monitoring
- Cultural and linguistic threat adaptation

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

⚖️ LEGAL WARNING: This software is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or reverse engineering is strictly prohibited
and will result in immediate legal action under German and international copyright law.
Contact mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
import geoip2.database
import geoip2.errors
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque

import aioredis
import aiohttp
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import folium
from folium.plugins import HeatMap, MarkerCluster

logger = logging.getLogger(__name__)

class JurisdictionType(str, Enum):
    """
Legal jurisdiction classifications."""

    STRONG_COPYRIGHT = "strong_copyright"      # US, UK, Germany, etc.
    MODERATE_COPYRIGHT = "moderate_copyright"  # Many EU countries
    WEAK_COPYRIGHT = "weak_copyright"          # Some developing nations
    COMPLEX_JURISDICTION = "complex_jurisdiction"  # China, Russia, etc.
    SAFE_HARBOR = "safe_harbor"               # Countries with limited enforcement
    UNKNOWN = "unknown"

class GeopoliticalRisk(str, Enum):
    """Geopolitical risk levels."""

    MINIMAL = "minimal"       # Strong rule of law, good enforcement
    LOW = "low"              # Generally reliable but some gaps
    MODERATE = "moderate"     # Mixed enforcement, political considerations
    HIGH = "high"            # Weak enforcement, corruption issues
    EXTREME = "extreme"      # Hostile jurisdiction, state-sponsored piracy
    EMBARGO = "embargo"      # Sanctioned countries

class TerritorialPattern(str, Enum):
    """Territorial activity patterns."""

    DOMESTIC_ONLY = "domestic_only"
    REGIONAL_SPREAD = "regional_spread"
    INTERNATIONAL_NETWORK = "international_network"
    JURISDICTION_SHOPPING = "jurisdiction_shopping"
    SAFE_HARBOR_SEEKING = "safe_harbor_seeking"
    NOMADIC_OPERATION = "nomadic_operation"

@dataclass
class GeospatialThreat:
    """Geospatial threat intelligence."""
    threat_id: str
    detection_time: datetime
    coordinates: Tuple[float, float]  # lat, lon
    country_code: str
    region: str
    city: str
    jurisdiction_type: JurisdictionType
    geopolitical_risk: GeopoliticalRisk
    threat_severity: str
    attribution_confidence: float
    ip_addresses: List[str] = field(default_factory=list)
    infrastructure_details: Dict[str, Any] = field(default_factory=dict)
    legal_context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class JurisdictionProfile:
    """
Legal jurisdiction profile."""
    country_code: str
    country_name: str
    jurisdiction_type: JurisdictionType
    copyright_strength: float  # 0.0 to 1.0
    enforcement_effectiveness: float
    international_treaties: List[str]
    enforcement_agencies: List[str]
    typical_response_time_days: int
    success_rate: float
    cost_factor: float
    language_codes: List[str]
    timezone: str
    business_hours: Dict[str, str]

@dataclass
class GeospatialCluster:
    """
Cluster of geospatial activity."""
    cluster_id: str
    center_coordinates: Tuple[float, float]
    radius_km: float
    threat_count: int
    countries_involved: List[str]
    pattern_type: TerritorialPattern
    coordination_score: float
    emergence_date: datetime
    growth_rate: float

class GeospatialIntelligenceEngine:
    """
Ultra-advanced geospatial intelligence and surveillance system."""
    
    def __init__(self, config: Dict[str, Any]):
        """
Initialize the geospatial intelligence engine."""
        self.config = config
        self.redis_client = None
        self.db_session = None
        
        # GeoIP database
        self._geoip_db = None
        self._geocoder = Nominatim(user_agent="content_protection_geospatial")
        
        # Jurisdiction database
        self._jurisdiction_profiles: Dict[str, JurisdictionProfile] = {}
        self._territorial_clusters: Dict[str, GeospatialCluster] = {}
        
        # Threat mapping
        self._threat_map: Dict[str, List[GeospatialThreat]] = defaultdict(list)
        self._heat_map_data = []
        
        # Surveillance state
        self._geospatial_monitoring_active = False
        self._monitoring_regions: Set[str] = set()
        
        logger.info("Geospatial Intelligence Engine initialized")

    async def initialize(self, redis_client: aioredis.Redis, db_session: AsyncSession):
        """Initialize geospatial engine with dependencies."""
        self.redis_client = redis_client
        self.db_session = db_session
        
        # Initialize GeoIP database
        await self._initialize_geoip_database()
        
        # Load jurisdiction profiles
        await self._load_jurisdiction_profiles()
        
        # Start geospatial monitoring
        await self._start_geospatial_monitoring()
        
        logger.info("Geospatial Intelligence Engine fully initialized")

    async def _initialize_geoip_database(self):
        """Initialize GeoIP database for location resolution."""
        try:
            # In production, use actual GeoIP2 database file
            geoip_db_path = self.config.get("geoip_db_path", "/usr/share/GeoIP/GeoLite2-City.mmdb")
            
            try:
                self._geoip_db = geoip2.database.Reader(geoip_db_path)
                logger.info("GeoIP database loaded successfully")
            except FileNotFoundError:
                logger.warning("GeoIP database not found, using fallback geolocation")
                self._geoip_db = None
                
        except Exception as e:
            logger.error(f"Failed to initialize GeoIP database: {e}")
            self._geoip_db = None

    async def _load_jurisdiction_profiles(self):
        """Load comprehensive jurisdiction profiles."""
        try:
            # Load jurisdiction data (in production, this would come from a database)
            jurisdiction_data = {
                "US": JurisdictionProfile(
                    country_code="US",
                    country_name="United States",
                    jurisdiction_type=JurisdictionType.STRONG_COPYRIGHT,
                    copyright_strength=0.95,
                    enforcement_effectiveness=0.90,
                    international_treaties=["DMCA", "WIPO", "Berne Convention"],
                    enforcement_agencies=["FBI", "ICE", "State Courts"],
                    typical_response_time_days=7,
                    success_rate=0.85,
                    cost_factor=1.2,
                    language_codes=["en"],
                    timezone="America/New_York",
                    business_hours={"start": "09:00", "end": "17:00"}
                ),
                "DE": JurisdictionProfile(
                    country_code="DE",
                    country_name="Germany",
                    jurisdiction_type=JurisdictionType.STRONG_COPYRIGHT,
                    copyright_strength=0.92,
                    enforcement_effectiveness=0.88,
                    international_treaties=["EU Copyright Directive", "WIPO", "Berne Convention"],
                    enforcement_agencies=["Federal Police", "State Courts", "BKA"],
                    typical_response_time_days=10,
                    success_rate=0.82,
                    cost_factor=1.1,
                    language_codes=["de"],
                    timezone="Europe/Berlin",
                    business_hours={"start": "08:00", "end": "16:00"}
                ),
                "CN": JurisdictionProfile(
                    country_code="CN",
                    country_name="China",
                    jurisdiction_type=JurisdictionType.COMPLEX_JURISDICTION,
                    copyright_strength=0.65,
                    enforcement_effectiveness=0.45,
                    international_treaties=["WIPO", "Berne Convention"],
                    enforcement_agencies=["SIPO", "Local Courts"],
                    typical_response_time_days=30,
                    success_rate=0.35,
                    cost_factor=1.8,
                    language_codes=["zh"],
                    timezone="Asia/Shanghai",
                    business_hours={"start": "09:00", "end": "17:00"}
                ),
                "RU": JurisdictionProfile(
                    country_code="RU",
                    country_name="Russia",
                    jurisdiction_type=JurisdictionType.COMPLEX_JURISDICTION,
                    copyright_strength=0.55,
                    enforcement_effectiveness=0.30,
                    international_treaties=["WIPO"],
                    enforcement_agencies=["Roskomnadzor", "Federal Courts"],
                    typical_response_time_days=45,
                    success_rate=0.25,
                    cost_factor=2.0,
                    language_codes=["ru"],
                    timezone="Europe/Moscow",
                    business_hours={"start": "09:00", "end": "17:00"}
                )
            }
            
            self._jurisdiction_profiles = jurisdiction_data
            
            # Store in Redis for fast access
            for country_code, profile in jurisdiction_data.items():
                await self.redis_client.hset(
                    f"jurisdiction_profile:{country_code}",
                    mapping={
                        "country_name": profile.country_name,
                        "jurisdiction_type": profile.jurisdiction_type.value,
                        "copyright_strength": profile.copyright_strength,
                        "enforcement_effectiveness": profile.enforcement_effectiveness,
                        "success_rate": profile.success_rate,
                        "typical_response_time_days": profile.typical_response_time_days
                    }
                )
            
            logger.info(f"Loaded {len(jurisdiction_data)} jurisdiction profiles")
            
        except Exception as e:
            logger.error(f"Failed to load jurisdiction profiles: {e}")

    async def analyze_geospatial_threat(
        self,
        detection_data: Dict[str, Any],
        source_ip: str
    ) -> GeospatialThreat:
        """Analyze geospatial threat from detection data."""
        try:
            # Resolve IP to location
            location_data = await self._resolve_ip_location(source_ip)
            
            if not location_data:
                logger.warning(f"Could not resolve location for IP: {source_ip}")
                return None
            
            # Get jurisdiction profile
            country_code = location_data.get("country_code", "UNKNOWN")
            jurisdiction_profile = self._jurisdiction_profiles.get(country_code)
            
            # Determine jurisdiction type and risk
            jurisdiction_type = JurisdictionType.UNKNOWN
            geopolitical_risk = GeopoliticalRisk.MODERATE
            
            if jurisdiction_profile:
                jurisdiction_type = jurisdiction_profile.jurisdiction_type
                
                # Calculate geopolitical risk based on enforcement effectiveness
                if jurisdiction_profile.enforcement_effectiveness >= 0.8:
                    geopolitical_risk = GeopoliticalRisk.MINIMAL
                elif jurisdiction_profile.enforcement_effectiveness >= 0.6:
                    geopolitical_risk = GeopoliticalRisk.LOW
                elif jurisdiction_profile.enforcement_effectiveness >= 0.4:
                    geopolitical_risk = GeopoliticalRisk.MODERATE
                elif jurisdiction_profile.enforcement_effectiveness >= 0.2:
                    geopolitical_risk = GeopoliticalRisk.HIGH
                else:
                    geopolitical_risk = GeopoliticalRisk.EXTREME
            
            # Assess threat severity based on multiple factors
            threat_severity = self._assess_geospatial_threat_severity(
                detection_data, location_data, jurisdiction_profile
            )
            
            # Calculate attribution confidence
            attribution_confidence = self._calculate_attribution_confidence(
                source_ip, location_data, detection_data
            )
            
            # Create geospatial threat
            threat = GeospatialThreat(
                threat_id=f"geo_threat_{int(datetime.utcnow().timestamp())}_{source_ip.replace('.', '_')}",
                detection_time=datetime.utcnow(),
                coordinates=(location_data.get("latitude", 0.0), location_data.get("longitude", 0.0)),
                country_code=country_code,
                region=location_data.get("region", "Unknown"),
                city=location_data.get("city", "Unknown"),
                jurisdiction_type=jurisdiction_type,
                geopolitical_risk=geopolitical_risk,
                threat_severity=threat_severity,
                attribution_confidence=attribution_confidence,
                ip_addresses=[source_ip],
                infrastructure_details=await self._analyze_infrastructure(source_ip),
                legal_context=await self._analyze_legal_context(country_code, detection_data)
            )
            
            # Store threat in map
            self._threat_map[country_code].append(threat)
            
            # Update heat map data
            self._heat_map_data.append([
                threat.coordinates[0],  # latitude
                threat.coordinates[1],  # longitude
                self._severity_to_weight(threat_severity)
            ])
            
            # Store in Redis
            await self.redis_client.hset(
                f"geospatial_threat:{threat.threat_id}",
                mapping={
                    "detection_time": threat.detection_time.isoformat(),
                    "country_code": threat.country_code,
                    "region": threat.region,
                    "city": threat.city,
                    "jurisdiction_type": threat.jurisdiction_type.value,
                    "geopolitical_risk": threat.geopolitical_risk.value,
                    "threat_severity": threat.threat_severity,
                    "attribution_confidence": threat.attribution_confidence,
                    "coordinates": json.dumps(threat.coordinates),
                    "ip_addresses": json.dumps(threat.ip_addresses)
                }
            )
            
            logger.info(f"Geospatial threat analyzed: {threat.threat_id} in {country_code}")
            return threat
            
        except Exception as e:
            logger.error(f"Failed to analyze geospatial threat: {e}")
            return None

    async def _resolve_ip_location(self, ip_address: str) -> Dict[str, Any]:
        """Resolve IP address to geographical location."""
        try:
            location_data = {}
            
            if self._geoip_db:
                try:
                    response = self._geoip_db.city(ip_address)
                    location_data = {
                        "latitude": float(response.location.latitude or 0.0),
                        "longitude": float(response.location.longitude or 0.0),
                        "country_code": response.country.iso_code or "UNKNOWN",
                        "country_name": response.country.name or "Unknown",
                        "region": response.subdivisions.most_specific.name or "Unknown",
                        "city": response.city.name or "Unknown",
                        "postal_code": response.postal.code or "",
                        "accuracy_radius": response.location.accuracy_radius or 0,
                        "time_zone": response.location.time_zone or "UTC"
                    }
                except geoip2.errors.AddressNotFoundError:
                    logger.warning(f"IP address not found in GeoIP database: {ip_address}")
                    
            # Fallback to online geolocation service
            if not location_data:
                location_data = await self._fallback_ip_geolocation(ip_address)
            
            return location_data
            
        except Exception as e:
            logger.error(f"Failed to resolve IP location: {e}")
            return {}

    async def _fallback_ip_geolocation(self, ip_address: str) -> Dict[str, Any]:
        """Fallback IP geolocation using online service."""
        try:
            # Use a free IP geolocation service as fallback
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://ip-api.com/json/{ip_address}") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "success":
                            return {
                                "latitude": float(data.get("lat", 0.0)),
                                "longitude": float(data.get("lon", 0.0)),
                                "country_code": data.get("countryCode", "UNKNOWN"),
                                "country_name": data.get("country", "Unknown"),
                                "region": data.get("regionName", "Unknown"),
                                "city": data.get("city", "Unknown"),
                                "postal_code": data.get("zip", ""),
                                "time_zone": data.get("timezone", "UTC"),
                                "isp": data.get("isp", "Unknown")
                            }
            
            return {}
            
        except Exception as e:
            logger.error(f"Fallback IP geolocation failed: {e}")
            return {}

    def _assess_geospatial_threat_severity(
        self,
        detection_data: Dict[str, Any],
        location_data: Dict[str, Any],
        jurisdiction_profile: Optional[JurisdictionProfile]
    ) -> str:
        """Assess threat severity based on geospatial factors."""
        try:
            severity_score = 0.0
            
            # Base severity from detection data
            similarity_score = float(detection_data.get("similarity_score", 0.0))
            confidence_score = float(detection_data.get("confidence_score", 0.0))
            base_severity = (similarity_score + confidence_score) / 2
            severity_score += base_severity * 0.4
            
            # Jurisdiction-based severity adjustment
            if jurisdiction_profile:
                if jurisdiction_profile.jurisdiction_type in [JurisdictionType.WEAK_COPYRIGHT, JurisdictionType.SAFE_HARBOR]:
                    severity_score += 0.3  # Higher threat in weak jurisdictions
                elif jurisdiction_profile.jurisdiction_type == JurisdictionType.COMPLEX_JURISDICTION:
                    severity_score += 0.2  # Moderate increase for complex jurisdictions
            else:
                severity_score += 0.25  # Unknown jurisdiction penalty
            
            # Geographic risk factors
            country_code = location_data.get("country_code", "")
            if country_code in ["CN", "RU", "IR", "KP"]:  # High-risk countries
                severity_score += 0.2
            elif country_code in ["BR", "IN", "PK"]:  # Moderate-risk countries
                severity_score += 0.1
            
            # ISP-based assessment
            isp = location_data.get("isp", "").lower()
            if any(keyword in isp for keyword in ["hosting", "server", "datacenter", "cloud"]):
                severity_score += 0.1  # Server infrastructure indicates professional operation
            
            # Convert to severity level
            if severity_score >= 0.8:
                return "critical"
            elif severity_score >= 0.6:
                return "high"
            elif severity_score >= 0.4:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.error(f"Failed to assess geospatial threat severity: {e}")
            return "medium"

    def _calculate_attribution_confidence(
        self,
        ip_address: str,
        location_data: Dict[str, Any],
        detection_data: Dict[str, Any]
    ) -> float:
        """Calculate confidence in threat attribution."""
        try:
            confidence = 0.5  # Base confidence
            
            # IP address type assessment
            if self._is_residential_ip(ip_address, location_data):
                confidence += 0.2  # Higher confidence for residential IPs
            elif self._is_datacenter_ip(location_data):
                confidence -= 0.1  # Lower confidence for datacenter IPs
            
            # Geographic consistency
            if location_data.get("accuracy_radius", 1000) < 50:  # High location accuracy
                confidence += 0.2
            elif location_data.get("accuracy_radius", 1000) > 500:  # Low location accuracy
                confidence -= 0.1
            
            # Detection quality
            detection_confidence = float(detection_data.get("confidence_score", 0.5))
            confidence += (detection_confidence - 0.5) * 0.3
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"Failed to calculate attribution confidence: {e}")
            return 0.5

    def _is_residential_ip(self, ip_address: str, location_data: Dict[str, Any]) -> bool:
        """Determine if IP address is likely residential."""
        isp = location_data.get("isp", "").lower()
        residential_indicators = ["residential", "home", "broadband", "dsl", "cable", "fiber"]
        return any(indicator in isp for indicator in residential_indicators)

    def _is_datacenter_ip(self, location_data: Dict[str, Any]) -> bool:
        """Determine if IP address is from a datacenter."""
        isp = location_data.get("isp", "").lower()
        datacenter_indicators = ["hosting", "server", "datacenter", "cloud", "aws", "google", "azure"]
        return any(indicator in isp for indicator in datacenter_indicators)

    async def _analyze_infrastructure(self, ip_address: str) -> Dict[str, Any]:
        """Analyze infrastructure details for IP address."""
        try:
            infrastructure = {
                "ip_address": ip_address,
                "reverse_dns": "",
                "autonomous_system": {},
                "hosting_provider": "",
                "infrastructure_type": "unknown",
                "risk_indicators": []
            }
            
            # Reverse DNS lookup
            try:
                import socket
                hostname = socket.gethostbyaddr(ip_address)[0]
                infrastructure["reverse_dns"] = hostname
                
                # Analyze hostname for indicators
                if any(indicator in hostname.lower() for indicator in ["server", "host", "vps", "dedicated"]):
                    infrastructure["infrastructure_type"] = "hosting"
                    infrastructure["risk_indicators"].append("professional_hosting")
                
            except socket.herror:
                infrastructure["reverse_dns"] = "No reverse DNS"
            
            # Additional infrastructure analysis would go here
            # (ASN lookup, BGP analysis, etc.)
            
            return infrastructure
            
        except Exception as e:
            logger.error(f"Failed to analyze infrastructure: {e}")
            return {"error": str(e)}

    async def _analyze_legal_context(self, country_code: str, detection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze legal context for enforcement actions."""
        try:
            legal_context = {
                "jurisdiction": country_code,
                "applicable_laws": [],
                "enforcement_agencies": [],
                "recommended_actions": [],
                "estimated_success_probability": 0.0,
                "estimated_response_time_days": 30,
                "cost_estimate": "medium"
            }
            
            jurisdiction_profile = self._jurisdiction_profiles.get(country_code)
            if jurisdiction_profile:
                legal_context.update({
                    "applicable_laws": jurisdiction_profile.international_treaties,
                    "enforcement_agencies": jurisdiction_profile.enforcement_agencies,
                    "estimated_success_probability": jurisdiction_profile.success_rate,
                    "estimated_response_time_days": jurisdiction_profile.typical_response_time_days
                })
                
                # Determine cost estimate
                if jurisdiction_profile.cost_factor <= 1.0:
                    legal_context["cost_estimate"] = "low"
                elif jurisdiction_profile.cost_factor <= 1.5:
                    legal_context["cost_estimate"] = "medium"
                else:
                    legal_context["cost_estimate"] = "high"
                
                # Generate recommended actions
                if jurisdiction_profile.jurisdiction_type == JurisdictionType.STRONG_COPYRIGHT:
                    legal_context["recommended_actions"] = [
                        "DMCA takedown notice",
                        "Direct platform reporting",
                        "Legal cease and desist"
                    ]
                elif jurisdiction_profile.jurisdiction_type == JurisdictionType.COMPLEX_JURISDICTION:
                    legal_context["recommended_actions"] = [
                        "Local legal counsel consultation",
                        "Platform-specific reporting",
                        "International treaty invocation"
                    ]
                else:
                    legal_context["recommended_actions"] = [
                        "Platform reporting only",
                        "Monitor for escalation"
                    ]
            
            return legal_context
            
        except Exception as e:
            logger.error(f"Failed to analyze legal context: {e}")
            return {"error": str(e)}

    def _severity_to_weight(self, severity: str) -> float:
        """Convert severity level to heat map weight."""
        severity_weights = {
            "critical": 1.0,
            "high": 0.7,
            "medium": 0.4,
            "low": 0.2
        }
        return severity_weights.get(severity, 0.3)

    async def detect_territorial_clusters(self, timeframe_hours: int = 24) -> List[GeospatialCluster]:
        """Detect clusters of territorial activity."""
        try:
            # Get recent threats within timeframe
            cutoff_time = datetime.utcnow() - timedelta(hours=timeframe_hours)
            recent_threats = []
            
            for country_threats in self._threat_map.values():
                for threat in country_threats:
                    if threat.detection_time >= cutoff_time:
                        recent_threats.append(threat)
            
            if len(recent_threats) < 3:
                return []
            
            # Perform geographic clustering
            clusters = await self._perform_geographic_clustering(recent_threats)
            
            # Analyze clusters for patterns
            analyzed_clusters = []
            for cluster in clusters:
                analyzed_cluster = await self._analyze_territorial_cluster(cluster, recent_threats)
                if analyzed_cluster:
                    analyzed_clusters.append(analyzed_cluster)
                    
                    # Store cluster in Redis
                    await self.redis_client.hset(
                        f"territorial_cluster:{analyzed_cluster.cluster_id}",
                        mapping={
                            "center_coordinates": json.dumps(analyzed_cluster.center_coordinates),
                            "radius_km": analyzed_cluster.radius_km,
                            "threat_count": analyzed_cluster.threat_count,
                            "countries_involved": json.dumps(analyzed_cluster.countries_involved),
                            "pattern_type": analyzed_cluster.pattern_type.value,
                            "coordination_score": analyzed_cluster.coordination_score,
                            "emergence_date": analyzed_cluster.emergence_date.isoformat()
                        }
                    )
            
            return analyzed_clusters
            
        except Exception as e:
            logger.error(f"Failed to detect territorial clusters: {e}")
            return []

    async def _perform_geographic_clustering(self, threats: List[GeospatialThreat]) -> List[List[GeospatialThreat]]:
        """Perform geographic clustering of threats."""
        try:
            from sklearn.cluster import DBSCAN
            from sklearn.preprocessing import StandardScaler
            
            # Extract coordinates
            coordinates = np.array([threat.coordinates for threat in threats])
            
            # Normalize coordinates for clustering
            scaler = StandardScaler()
            normalized_coords = scaler.fit_transform(coordinates)
            
            # Perform DBSCAN clustering
            # eps=0.5 roughly corresponds to ~500km for normalized coordinates
            clustering = DBSCAN(eps=0.5, min_samples=3).fit(normalized_coords)
            
            # Group threats by cluster
            clusters = {}
            for i, label in enumerate(clustering.labels_):
                if label != -1:  # Ignore noise points
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append(threats[i])
            
            return list(clusters.values())
            
        except Exception as e:
            logger.error(f"Failed to perform geographic clustering: {e}")
            return []

    async def _analyze_territorial_cluster(
        self,
        cluster_threats: List[GeospatialThreat],
        all_threats: List[GeospatialThreat]
    ) -> Optional[GeospatialCluster]:
        """Analyze a territorial cluster for patterns."""
        try:
            if len(cluster_threats) < 3:
                return None
            
            # Calculate cluster center and radius
            latitudes = [threat.coordinates[0] for threat in cluster_threats]
            longitudes = [threat.coordinates[1] for threat in cluster_threats]
            
            center_lat = np.mean(latitudes)
            center_lon = np.mean(longitudes)
            center_coordinates = (center_lat, center_lon)
            
            # Calculate radius (maximum distance from center)
            max_distance = 0.0
            for threat in cluster_threats:
                distance = geodesic(center_coordinates, threat.coordinates).kilometers
                max_distance = max(max_distance, distance)
            
            # Get unique countries
            countries_involved = list(set(threat.country_code for threat in cluster_threats))
            
            # Determine pattern type
            pattern_type = self._determine_territorial_pattern(cluster_threats, countries_involved)
            
            # Calculate coordination score
            coordination_score = self._calculate_territorial_coordination(cluster_threats)
            
            # Find emergence date (earliest threat)
            emergence_date = min(threat.detection_time for threat in cluster_threats)
            
            # Calculate growth rate
            growth_rate = self._calculate_cluster_growth_rate(cluster_threats)
            
            cluster = GeospatialCluster(
                cluster_id=f"territorial_cluster_{int(datetime.utcnow().timestamp())}_{len(cluster_threats)}",
                center_coordinates=center_coordinates,
                radius_km=max_distance,
                threat_count=len(cluster_threats),
                countries_involved=countries_involved,
                pattern_type=pattern_type,
                coordination_score=coordination_score,
                emergence_date=emergence_date,
                growth_rate=growth_rate
            )
            
            return cluster
            
        except Exception as e:
            logger.error(f"Failed to analyze territorial cluster: {e}")
            return None

    def _determine_territorial_pattern(
        self,
        cluster_threats: List[GeospatialThreat],
        countries_involved: List[str]
    ) -> TerritorialPattern:
        """Determine the territorial pattern type."""
        try:
            # Single country
            if len(countries_involved) == 1:
                return TerritorialPattern.DOMESTIC_ONLY
            
            # Multiple countries in same region
            if len(countries_involved) <= 3 and self._are_countries_regional(countries_involved):
                return TerritorialPattern.REGIONAL_SPREAD
            
            # Check for jurisdiction shopping
            if self._indicates_jurisdiction_shopping(cluster_threats):
                return TerritorialPattern.JURISDICTION_SHOPPING
            
            # Check for safe harbor seeking
            if self._indicates_safe_harbor_seeking(cluster_threats):
                return TerritorialPattern.SAFE_HARBOR_SEEKING
            
            # Check for nomadic operation
            if self._indicates_nomadic_operation(cluster_threats):
                return TerritorialPattern.NOMADIC_OPERATION
            
            # Default to international network
            return TerritorialPattern.INTERNATIONAL_NETWORK
            
        except Exception as e:
            logger.error(f"Failed to determine territorial pattern: {e}")
            return TerritorialPattern.INTERNATIONAL_NETWORK

    def _are_countries_regional(self, countries: List[str]) -> bool:
        """Check if countries are in the same geographic region."""
        # Simplified regional groupings
        regions = {
            "EU": ["DE", "FR", "IT", "ES", "NL", "BE", "AT", "PL", "CZ", "HU"],
            "ASIA": ["CN", "JP", "KR", "IN", "TH", "VN", "SG", "MY", "ID"],
            "AMERICAS": ["US", "CA", "MX", "BR", "AR", "CL", "CO"],
            "MENA": ["SA", "AE", "EG", "TR", "IL", "IR", "IQ"]
        }
        
        for region_countries in regions.values():
            if all(country in region_countries for country in countries):
                return True
        
        return False

    def _indicates_jurisdiction_shopping(self, threats: List[GeospatialThreat]) -> bool:
        """Check if pattern indicates jurisdiction shopping."""
        # Look for movement from strong to weak copyright jurisdictions
        strong_jurisdictions = [t for t in threats if t.jurisdiction_type == JurisdictionType.STRONG_COPYRIGHT]
        weak_jurisdictions = [t for t in threats if t.jurisdiction_type in [JurisdictionType.WEAK_COPYRIGHT, JurisdictionType.SAFE_HARBOR]]
        
        return len(strong_jurisdictions) > 0 and len(weak_jurisdictions) > len(strong_jurisdictions)

    def _indicates_safe_harbor_seeking(self, threats: List[GeospatialThreat]) -> bool:
        """
Check if pattern indicates safe harbor seeking."""
        safe_harbor_count = sum(1 for t in threats if t.jurisdiction_type == JurisdictionType.SAFE_HARBOR)
        return safe_harbor_count > len(threats) * 0.5

    def _indicates_nomadic_operation(self, threats: List[GeospatialThreat]) -> bool:
        """
Check if pattern indicates nomadic operation."""
        # Look for frequent country changes over time
        threats_sorted = sorted(threats, key=lambda x: x.detection_time)
        country_changes = 0
        
        for i in range(1, len(threats_sorted)):
            if threats_sorted[i].country_code != threats_sorted[i-1].country_code:
                country_changes += 1
        
        # High frequency of country changes indicates nomadic behavior
        return country_changes > len(threats) * 0.3

    def _calculate_territorial_coordination(self, threats: List[GeospatialThreat]) -> float:
        """
Calculate coordination score for territorial cluster."""
        try:
            if len(threats) < 2:
                return 0.0
            
            coordination_factors = []
            
            # Time synchronization
            detection_times = [threat.detection_time for threat in threats]
            detection_times.sort()
            
            if len(detection_times) >= 2:
                time_diffs = [(detection_times[i+1] - detection_times[i]).total_seconds() 
                             for i in range(len(detection_times)-1)]
                avg_time_diff = np.mean(time_diffs)
                
                # Lower time differences indicate higher coordination
                time_coordination = max(0, 1 - (avg_time_diff / 3600))  # Normalize by 1 hour
                coordination_factors.append(time_coordination)
            
            # Attribution confidence consistency
            confidences = [threat.attribution_confidence for threat in threats]
            confidence_std = np.std(confidences)
            confidence_coordination = max(0, 1 - confidence_std)
            coordination_factors.append(confidence_coordination)
            
            # Threat severity consistency
            severities = [threat.threat_severity for threat in threats]
            severity_values = [{"low": 0.25, "medium": 0.5, "high": 0.75, "critical": 1.0}[s] for s in severities]
            severity_std = np.std(severity_values)
            severity_coordination = max(0, 1 - severity_std)
            coordination_factors.append(severity_coordination)
            
            return np.mean(coordination_factors)
            
        except Exception as e:
            logger.error(f"Failed to calculate territorial coordination: {e}")
            return 0.0

    def _calculate_cluster_growth_rate(self, threats: List[GeospatialThreat]) -> float:
        """Calculate growth rate of cluster."""
        try:
            if len(threats) < 2:
                return 0.0
            
            # Sort by detection time
            threats_sorted = sorted(threats, key=lambda x: x.detection_time)
            
            # Calculate time span
            time_span = (threats_sorted[-1].detection_time - threats_sorted[0].detection_time).total_seconds()
            
            if time_span <= 0:
                return 0.0
            
            # Growth rate as threats per hour
            growth_rate = len(threats) / (time_span / 3600)
            
            return growth_rate
            
        except Exception as e:
            logger.error(f"Failed to calculate cluster growth rate: {e}")
            return 0.0

    async def generate_geospatial_intelligence_report(
        self,
        timeframe_hours: int = 168  # 7 days
    ) -> Dict[str, Any]:
        """Generate comprehensive geospatial intelligence report."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=timeframe_hours)
            
            report = {
                "report_id": f"geospatial_intel_{int(datetime.utcnow().timestamp())}",
                "generation_time": datetime.utcnow().isoformat(),
                "timeframe_hours": timeframe_hours,
                "threat_summary": {},
                "geographic_distribution": {},
                "jurisdiction_analysis": {},
                "territorial_clusters": [],
                "risk_assessment": {},
                "enforcement_recommendations": []
            }
            
            # Collect recent threats
            recent_threats = []
            for country_threats in self._threat_map.values():
                for threat in country_threats:
                    if threat.detection_time >= cutoff_time:
                        recent_threats.append(threat)
            
            # Generate threat summary
            report["threat_summary"] = {
                "total_threats": len(recent_threats),
                "countries_affected": len(set(t.country_code for t in recent_threats)),
                "severity_distribution": self._analyze_severity_distribution(recent_threats),
                "trend_analysis": self._analyze_threat_trends(recent_threats)
            }
            
            # Geographic distribution analysis
            report["geographic_distribution"] = self._analyze_geographic_distribution(recent_threats)
            
            # Jurisdiction analysis
            report["jurisdiction_analysis"] = self._analyze_jurisdiction_effectiveness(recent_threats)
            
            # Detect and analyze territorial clusters
            clusters = await self.detect_territorial_clusters(timeframe_hours)
            report["territorial_clusters"] = [
                {
                    "cluster_id": cluster.cluster_id,
                    "center_coordinates": cluster.center_coordinates,
                    "radius_km": cluster.radius_km,
                    "threat_count": cluster.threat_count,
                    "countries_involved": cluster.countries_involved,
                    "pattern_type": cluster.pattern_type.value,
                    "coordination_score": cluster.coordination_score
                }
                for cluster in clusters
            ]
            
            # Risk assessment
            report["risk_assessment"] = self._generate_risk_assessment(recent_threats, clusters)
            
            # Enforcement recommendations
            report["enforcement_recommendations"] = self._generate_enforcement_recommendations(recent_threats, clusters)
            
            # Store report in Redis
            await self.redis_client.hset(
                f"geospatial_report:{report['report_id']}",
                mapping={"report": json.dumps(report)}
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate geospatial intelligence report: {e}")
            return {"error": str(e)}

    def _analyze_severity_distribution(self, threats: List[GeospatialThreat]) -> Dict[str, int]:
        """Analyze distribution of threat severities."""
        distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for threat in threats:
            distribution[threat.threat_severity] = distribution.get(threat.threat_severity, 0) + 1
        
        return distribution

    def _analyze_threat_trends(self, threats: List[GeospatialThreat]) -> Dict[str, Any]:
        """Analyze trends in threat activity."""
        if len(threats) < 2:
            return {"trend": "insufficient_data"}
        
        # Sort by time
        threats_sorted = sorted(threats, key=lambda x: x.detection_time)
        
        # Split into two halves for trend analysis
        mid_point = len(threats_sorted) // 2
        first_half = threats_sorted[:mid_point]
        second_half = threats_sorted[mid_point:]
        
        first_half_rate = len(first_half) / max(1, (threats_sorted[mid_point-1].detection_time - threats_sorted[0].detection_time).total_seconds() / 3600)
        second_half_rate = len(second_half) / max(1, (threats_sorted[-1].detection_time - threats_sorted[mid_point].detection_time).total_seconds() / 3600)
        
        if second_half_rate > first_half_rate * 1.2:
            trend = "increasing"
        elif second_half_rate < first_half_rate * 0.8:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "first_half_rate": first_half_rate,
            "second_half_rate": second_half_rate,
            "rate_change": (second_half_rate - first_half_rate) / max(first_half_rate, 0.001)
        }

    def _analyze_geographic_distribution(self, threats: List[GeospatialThreat]) -> Dict[str, Any]:
        """Analyze geographic distribution of threats."""
        distribution = {
            "by_country": defaultdict(int),
            "by_region": defaultdict(int),
            "by_jurisdiction_type": defaultdict(int),
            "hotspots": []
        }
        
        for threat in threats:
            distribution["by_country"][threat.country_code] += 1
            distribution["by_region"][threat.region] += 1
            distribution["by_jurisdiction_type"][threat.jurisdiction_type.value] += 1
        
        # Convert defaultdicts to regular dicts
        distribution["by_country"] = dict(distribution["by_country"])
        distribution["by_region"] = dict(distribution["by_region"])
        distribution["by_jurisdiction_type"] = dict(distribution["by_jurisdiction_type"])
        
        # Identify hotspots (countries with >10% of total threats)
        total_threats = len(threats)
        threshold = total_threats * 0.1
        
        for country, count in distribution["by_country"].items():
            if count >= threshold:
                distribution["hotspots"].append({
                    "country": country,
                    "threat_count": count,
                    "percentage": (count / total_threats) * 100
                })
        
        return distribution

    def _analyze_jurisdiction_effectiveness(self, threats: List[GeospatialThreat]) -> Dict[str, Any]:
        """Analyze effectiveness of different jurisdictions."""
        jurisdiction_analysis = {
            "enforcement_success_rates": {},
            "response_times": {},
            "cost_effectiveness": {},
            "recommendations": []
        }
        
        for country_code, profile in self._jurisdiction_profiles.items():
            country_threats = [t for t in threats if t.country_code == country_code]
            
            if country_threats:
                jurisdiction_analysis["enforcement_success_rates"][country_code] = {
                    "expected_success_rate": profile.success_rate,
                    "threat_count": len(country_threats),
                    "jurisdiction_type": profile.jurisdiction_type.value
                }
                
                jurisdiction_analysis["response_times"][country_code] = profile.typical_response_time_days
                jurisdiction_analysis["cost_effectiveness"][country_code] = 1.0 / profile.cost_factor
        
        # Generate recommendations
        high_threat_countries = [cc for cc, data in jurisdiction_analysis["enforcement_success_rates"].items() 
                               if data["threat_count"] >= 5]
        
        for country in high_threat_countries:
            profile = self._jurisdiction_profiles.get(country)
            if profile and profile.success_rate < 0.5:
                jurisdiction_analysis["recommendations"].append(f"Consider alternative enforcement strategies for {country} due to low success rates")
        
        return jurisdiction_analysis

    def _generate_risk_assessment(
        self,
        threats: List[GeospatialThreat],
        clusters: List[GeospatialCluster]
    ) -> Dict[str, Any]:
        """Generate comprehensive risk assessment."""
        risk_assessment = {
            "overall_risk_level": "medium",
            "risk_factors": [],
            "geographic_risks": {},
            "coordination_risks": {},
            "trend_risks": {}
        }
        
        # Calculate overall risk score
        risk_score = 0.0
        
        # High-risk jurisdiction threats
        high_risk_threats = [t for t in threats if t.geopolitical_risk in [GeopoliticalRisk.HIGH, GeopoliticalRisk.EXTREME]]
        if high_risk_threats:
            risk_score += min(len(high_risk_threats) / len(threats), 0.3)
            risk_assessment["risk_factors"].append(f"{len(high_risk_threats)} threats from high-risk jurisdictions")
        
        # Large territorial clusters
        large_clusters = [c for c in clusters if c.threat_count >= 10]
        if large_clusters:
            risk_score += min(len(large_clusters) * 0.2, 0.3)
            risk_assessment["risk_factors"].append(f"{len(large_clusters)} large territorial clusters detected")
        
        # High coordination clusters
        coordinated_clusters = [c for c in clusters if c.coordination_score >= 0.7]
        if coordinated_clusters:
            risk_score += min(len(coordinated_clusters) * 0.15, 0.25)
            risk_assessment["risk_factors"].append(f"{len(coordinated_clusters)} highly coordinated clusters")
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_assessment["overall_risk_level"] = "critical"
        elif risk_score >= 0.5:
            risk_assessment["overall_risk_level"] = "high"
        elif risk_score >= 0.3:
            risk_assessment["overall_risk_level"] = "medium"
        else:
            risk_assessment["overall_risk_level"] = "low"
        
        return risk_assessment

    def _generate_enforcement_recommendations(
        self,
        threats: List[GeospatialThreat],
        clusters: List[GeospatialCluster]
    ) -> List[Dict[str, Any]]:
        """Generate enforcement recommendations based on geospatial analysis."""
        recommendations = []
        
        # Country-specific recommendations
        country_threat_counts = defaultdict(int)
        for threat in threats:
            country_threat_counts[threat.country_code] += 1
        
        for country, count in country_threat_counts.items():
            if count >= 5:  # High activity threshold
                profile = self._jurisdiction_profiles.get(country)
                if profile:
                    recommendation = {
                        "type": "country_specific",
                        "country": country,
                        "threat_count": count,
                        "priority": "high" if count >= 10 else "medium",
                        "recommended_actions": profile.enforcement_agencies,
                        "expected_success_rate": profile.success_rate,
                        "estimated_cost": "high" if profile.cost_factor > 1.5 else "medium"
                    }
                    
                    if profile.jurisdiction_type == JurisdictionType.STRONG_COPYRIGHT:
                        recommendation["strategy"] = "Direct legal action via DMCA/local copyright law"
                    elif profile.jurisdiction_type == JurisdictionType.COMPLEX_JURISDICTION:
                        recommendation["strategy"] = "Engage local legal counsel and use international treaties"
                    else:
                        recommendation["strategy"] = "Focus on platform-level enforcement"
                    
                    recommendations.append(recommendation)
        
        # Cluster-specific recommendations
        for cluster in clusters:
            if cluster.threat_count >= 5:
                recommendation = {
                    "type": "cluster_specific",
                    "cluster_id": cluster.cluster_id,
                    "threat_count": cluster.threat_count,
                    "countries_involved": cluster.countries_involved,
                    "pattern_type": cluster.pattern_type.value,
                    "priority": "critical" if cluster.coordination_score >= 0.8 else "high",
                    "strategy": "Coordinated multi-jurisdiction enforcement"
                }
                
                if cluster.pattern_type == TerritorialPattern.JURISDICTION_SHOPPING:
                    recommendation["specific_actions"] = [
                        "File simultaneous enforcement actions",
                        "Coordinate with international law enforcement",
                        "Monitor for jurisdiction shifts"
                    ]
                elif cluster.pattern_type == TerritorialPattern.COORDINATED_ATTACK:
                    recommendation["specific_actions"] = [
                        "Emergency response activation",
                        "International law enforcement notification",
                        "Platform-wide coordination"
                    ]
                
                recommendations.append(recommendation)
        
        return recommendations

    async def create_threat_heat_map(self, output_path: str = None) -> str:
        """Create interactive heat map of geospatial threats."""
        try:
            if not self._heat_map_data:
                logger.warning("No heat map data available")
                return ""
            
            # Create base map centered on global threats
            if self._heat_map_data:
                center_lat = np.mean([point[0] for point in self._heat_map_data])
                center_lon = np.mean([point[1] for point in self._heat_map_data])
            else:
                center_lat, center_lon = 20.0, 0.0  # Default global center
            
            threat_map = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=2,
                tiles='OpenStreetMap'
            )
            
            # Add heat map layer
            HeatMap(self._heat_map_data, radius=15, blur=25, max_zoom=1).add_to(threat_map)
            
            # Add markers for high-severity threats
            for country_threats in self._threat_map.values():
                for threat in country_threats:
                    if threat.threat_severity in ["high", "critical"]:
                        color = "red" if threat.threat_severity == "critical" else "orange"
                        
                        popup_text = f"""
                        <b>Threat ID:</b> {threat.threat_id}<br>
                        <b>Location:</b> {threat.city}, {threat.country_code}<br>
                        <b>Severity:</b> {threat.threat_severity}<br>
                        <b>Risk:</b> {threat.geopolitical_risk.value}<br>
                        <b>Confidence:</b> {threat.attribution_confidence:.2f}<br>
                        <b>Detection:</b> {threat.detection_time.strftime('%Y-%m-%d %H:%M')}
                        """
                        
                        folium.Marker(
                            location=threat.coordinates,
                            popup=folium.Popup(popup_text, max_width=300),
                            icon=folium.Icon(color=color, icon='exclamation-sign')
                        ).add_to(threat_map)
            
            # Save map
            if not output_path:
                output_path = f"/tmp/threat_heatmap_{int(datetime.utcnow().timestamp())}.html"
            
            threat_map.save(output_path)
            logger.info(f"Threat heat map saved: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to create threat heat map: {e}")
            return ""

    async def _start_geospatial_monitoring(self):
        """Start continuous geospatial monitoring."""
        try:
            self._geospatial_monitoring_active = True
            
            # Start monitoring task
            asyncio.create_task(self._geospatial_monitoring_loop())
            
            logger.info("Geospatial monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start geospatial monitoring: {e}")

    async def _geospatial_monitoring_loop(self):
        """Main geospatial monitoring loop."""
        try:
            while self._geospatial_monitoring_active:
                # Perform periodic analysis
                await self._perform_periodic_analysis()
                
                # Update territorial clusters
                await self.detect_territorial_clusters()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                # Wait before next cycle
                await asyncio.sleep(self.config.get("geospatial_monitoring_interval", 1800))  # 30 minutes
                
        except asyncio.CancelledError:
            logger.info("Geospatial monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Geospatial monitoring loop error: {e}")

    async def _perform_periodic_analysis(self):
        """Perform periodic geospatial analysis."""
        try:
            # Generate intelligence report
            report = await self.generate_geospatial_intelligence_report(timeframe_hours=24)
            
            # Check for high-risk situations
            if report.get("risk_assessment", {}).get("overall_risk_level") in ["high", "critical"]:
                await self._handle_high_risk_situation(report)
            
        except Exception as e:
            logger.error(f"Failed to perform periodic analysis: {e}")

    async def _handle_high_risk_situation(self, report: Dict[str, Any]):
        """Handle high-risk geospatial situations."""
        try:
            alert_data = {
                "alert_type": "geospatial_high_risk",
                "risk_level": report.get("risk_assessment", {}).get("overall_risk_level"),
                "timestamp": datetime.utcnow().isoformat(),
                "threat_summary": report.get("threat_summary", {}),
                "recommendations": report.get("enforcement_recommendations", [])
            }
            
            # Store alert
            await self.redis_client.hset(
                f"geospatial_alert:{int(datetime.utcnow().timestamp())}",
                mapping=alert_data
            )
            
            logger.warning(f"High-risk geospatial situation detected: {alert_data['risk_level']}")
            
        except Exception as e:
            logger.error(f"Failed to handle high-risk situation: {e}")

    async def _cleanup_old_data(self):
        """Clean up old geospatial data."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=30)
            
            # Clean up old threats from memory
            for country_code in list(self._threat_map.keys()):
                self._threat_map[country_code] = [
                    threat for threat in self._threat_map[country_code]
                    if threat.detection_time >= cutoff_time
                ]
                
                # Remove empty countries
                if not self._threat_map[country_code]:
                    del self._threat_map[country_code]
            
            # Update heat map data
            self._heat_map_data = [
                point for point in self._heat_map_data
                # Note: heat map data doesn't have timestamps, so we keep recent data based on threat map
            ]
            
            # Clean up Redis data
            old_keys = await self.redis_client.keys("geospatial_threat:*")
            for key in old_keys:
                threat_data = await self.redis_client.hgetall(key)
                if threat_data:
                    detection_time = datetime.fromisoformat(threat_data.get('detection_time', ''))
                    if detection_time < cutoff_time:
                        await self.redis_client.delete(key)
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")

    async def get_geospatial_statistics(self) -> Dict[str, Any]:
        """Get comprehensive geospatial statistics."""
        try:
            stats = {
                "total_threats": 0,
                "countries_affected": 0,
                "territorial_clusters": len(self._territorial_clusters),
                "jurisdiction_distribution": {},
                "risk_distribution": {},
                "recent_activity": {}
            }
            
            all_threats = []
            for country_threats in self._threat_map.values():
                all_threats.extend(country_threats)
            
            stats["total_threats"] = len(all_threats)
            stats["countries_affected"] = len(self._threat_map.keys())
            
            # Jurisdiction distribution
            jurisdiction_counts = defaultdict(int)
            risk_counts = defaultdict(int)
            
            for threat in all_threats:
                jurisdiction_counts[threat.jurisdiction_type.value] += 1
                risk_counts[threat.geopolitical_risk.value] += 1
            
            stats["jurisdiction_distribution"] = dict(jurisdiction_counts)
            stats["risk_distribution"] = dict(risk_counts)
            
            # Recent activity (last 24 hours)
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            recent_threats = [t for t in all_threats if t.detection_time >= recent_cutoff]
            
            stats["recent_activity"] = {
                "last_24h_threats": len(recent_threats),
                "activity_rate": len(recent_threats) / 24.0,  # per hour
                "trending_countries": self._get_trending_countries(recent_threats)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get geospatial statistics: {e}")
            return {"error": str(e)}

    def _get_trending_countries(self, recent_threats: List[GeospatialThreat]) -> List[Dict[str, Any]]:
        """Get trending countries from recent threats."""
        country_counts = defaultdict(int)
        for threat in recent_threats:
            country_counts[threat.country_code] += 1
        
        # Sort by count and return top 5
        trending = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return [{"country": country, "threat_count": count} for country, count in trending]

    async def shutdown(self):
        """Shutdown the geospatial intelligence engine."""
        logger.info("Shutting down Geospatial Intelligence Engine...")
        
        self._geospatial_monitoring_active = False
        
        # Close GeoIP database
        if self._geoip_db:
            self._geoip_db.close()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Geospatial Intelligence Engine shutdown complete")
