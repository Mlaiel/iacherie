"""
Geolocation Rate Limiter Enterprise - Ainflue
=============================================
Rate Limiter avec géolocalisation pour compliance régionale.
Geographic limits + compliance + fraud detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Rate Limiting
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict, deque
import statistics
import re

from .distributed_rate_limiter import (
    DistributedRateLimiter, RateLimitConfig, RateLimitResult, 
    RateLimitAlgorithm, RateLimitStatus
)

logger = logging.getLogger(__name__)

class GeographicRegion(Enum):
    """Régions géographiques supportées"""
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    SOUTH_AMERICA = "south_america"
    AFRICA = "africa"
    MIDDLE_EAST = "middle_east"
    OCEANIA = "oceania"
    UNKNOWN = "unknown"

class ComplianceRegime(Enum):
    """Régimes de compliance"""
    GDPR = "gdpr"                # European Union
    CCPA = "ccpa"                # California
    PIPEDA = "pipeda"            # Canada
    LGPD = "lgpd"                # Brazil
    PDPA_SG = "pdpa_singapore"   # Singapore
    PDPA_TH = "pdpa_thailand"    # Thailand
    STANDARD = "standard"        # Default compliance

class FraudRiskLevel(Enum):
    """Niveaux de risque fraud"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class GeolocationSource(Enum):
    """Sources géolocalisation"""
    IP_ADDRESS = "ip_address"
    GPS_COORDINATES = "gps_coordinates"
    USER_DECLARED = "user_declared"
    NETWORK_PROVIDER = "network_provider"
    REVERSE_DNS = "reverse_dns"

@dataclass
class GeoConfig:
    """Configuration géolocalisation"""
    enable_compliance_enforcement: bool = True
    enable_fraud_detection: bool = True
    enable_regional_optimization: bool = True
    default_compliance_regime: ComplianceRegime = ComplianceRegime.STANDARD
    max_requests_per_country: int = 10000
    suspicious_threshold_ratio: float = 5.0  # x times normal traffic
    geo_cache_ttl_seconds: int = 3600
    enable_cross_border_tracking: bool = True
    enable_timezone_awareness: bool = True
    blocked_countries: List[str] = field(default_factory=list)
    restricted_regions: List[GeographicRegion] = field(default_factory=list)

@dataclass
class GeoLocation:
    """Information géolocalisation"""
    country_code: str
    country_name: str
    region: GeographicRegion
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    isp: Optional[str] = None
    organization: Optional[str] = None
    source: GeolocationSource = GeolocationSource.IP_ADDRESS
    confidence: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GeoRequest:
    """Request avec context géographique"""
    identifier: str
    ip_address: str
    user_agent: Optional[str] = None
    geolocation: Optional[GeoLocation] = None
    declared_location: Optional[Dict[str, str]] = None
    cost: int = 1
    priority: int = 100
    allow_cross_border: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class GeoLimitResult:
    """Résultat rate limiting géographique"""
    allowed: bool
    geolocation: GeoLocation
    compliance_regime: ComplianceRegime
    regional_limits_applied: Dict[str, int]
    fraud_score: float
    fraud_risk_level: FraudRiskLevel
    geo_anomalies: List[str]
    rate_limit_result: RateLimitResult
    cross_border_detected: bool = False
    compliance_warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GeoAnomaly:
    """Anomalie géographique détectée"""
    anomaly_id: str
    anomaly_type: str
    affected_regions: List[GeographicRegion]
    affected_countries: List[str]
    severity: str
    confidence: float
    detected_at: datetime
    description: str
    indicators: List[str]
    recommended_action: str
    auto_mitigation: bool = False

@dataclass
class GeoPattern:
    """Pattern géographique"""
    pattern_id: str
    user_id: str
    countries_accessed: List[str]
    regions_accessed: List[GeographicRegion]
    time_span_hours: int
    request_count: int
    velocity_score: float  # Requests per hour across regions
    consistency_score: float  # How consistent the pattern is
    risk_indicators: List[str]

@dataclass
class ComplianceResult:
    """Résultat compliance régionale"""
    compliant: bool
    regime: ComplianceRegime
    requirements_met: List[str]
    violations: List[str]
    required_actions: List[str]
    grace_period_expires: Optional[datetime] = None
    audit_trail_id: Optional[str] = None

@dataclass
class CoordinationResult:    
    """Résultat coordination régionale"""
    coordinated: bool
    participating_regions: List[GeographicRegion]
    global_limit_applied: int
    regional_allocations: Dict[str, int]
    load_balancing_applied: bool
    optimization_metrics: Dict[str, float]

class GeolocationDetector:
    """Détecteur géolocalisation"""
    
    def __init__(self, config: GeoConfig):
        self.config = config
        self.geo_cache = {}
        self.ip_database = {}  # Simulation IP geolocation DB
        self.country_mappings = self._load_country_mappings()
        self.logger = logging.getLogger(__name__)
        
        # Populate simulation data
        self._initialize_simulation_data()
    
    def _initialize_simulation_data(self):
        """Initialisation données simulation"""
        # Simulation IP ranges pour différents pays
        self.ip_database = {
            "192.168.1.": {"country": "US", "region": GeographicRegion.NORTH_AMERICA},
            "10.0.0.": {"country": "CA", "region": GeographicRegion.NORTH_AMERICA},
            "172.16.0.": {"country": "DE", "region": GeographicRegion.EUROPE},
            "203.0.113.": {"country": "JP", "region": GeographicRegion.ASIA_PACIFIC},
            "198.51.100.": {"country": "GB", "region": GeographicRegion.EUROPE},
            "233.252.0.": {"country": "BR", "region": GeographicRegion.SOUTH_AMERICA}
        }
    
    def _load_country_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Chargement mappings pays"""
        return {
            "US": {
                "name": "United States",
                "region": GeographicRegion.NORTH_AMERICA,
                "compliance": ComplianceRegime.STANDARD,
                "timezone": "America/New_York"
            },
            "CA": {
                "name": "Canada", 
                "region": GeographicRegion.NORTH_AMERICA,
                "compliance": ComplianceRegime.PIPEDA,
                "timezone": "America/Toronto"
            },
            "DE": {
                "name": "Germany",
                "region": GeographicRegion.EUROPE,
                "compliance": ComplianceRegime.GDPR,
                "timezone": "Europe/Berlin"
            },
            "GB": {
                "name": "United Kingdom",
                "region": GeographicRegion.EUROPE,
                "compliance": ComplianceRegime.GDPR,
                "timezone": "Europe/London"
            },
            "JP": {
                "name": "Japan",
                "region": GeographicRegion.ASIA_PACIFIC,
                "compliance": ComplianceRegime.STANDARD,
                "timezone": "Asia/Tokyo"
            },
            "BR": {
                "name": "Brazil",
                "region": GeographicRegion.SOUTH_AMERICA,
                "compliance": ComplianceRegime.LGPD,
                "timezone": "America/Sao_Paulo"
            },
            "SG": {
                "name": "Singapore",
                "region": GeographicRegion.ASIA_PACIFIC,
                "compliance": ComplianceRegime.PDPA_SG,
                "timezone": "Asia/Singapore"
            }
        }
    
    async def detect_geolocation(self, ip_address: str, 
                               additional_context: Optional[Dict[str, Any]] = None) -> GeoLocation:
        """Détection géolocalisation depuis IP"""
        try:
            # Vérification cache
            cache_key = f"geo:{ip_address}"
            if cache_key in self.geo_cache:
                cached_geo = self.geo_cache[cache_key]
                if time.time() - cached_geo["timestamp"] < self.config.geo_cache_ttl_seconds:
                    return cached_geo["location"]
            
            # Détection géolocalisation
            geolocation = await self._perform_geolocation_lookup(ip_address)
            
            # Enrichissement avec context additionnel
            if additional_context:
                geolocation = await self._enrich_geolocation(geolocation, additional_context)
            
            # Cache résultat
            self.geo_cache[cache_key] = {
                "location": geolocation,
                "timestamp": time.time()
            }
            
            return geolocation
            
        except Exception as e:
            self.logger.error(f"Geolocation detection failed for {ip_address}: {e}")
            return GeoLocation(
                country_code="UNKNOWN",
                country_name="Unknown",
                region=GeographicRegion.UNKNOWN,
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    async def _perform_geolocation_lookup(self, ip_address: str) -> GeoLocation:
        """Lookup géolocalisation IP"""
        # Simulation lookup - dans une vraie implémentation, utiliser MaxMind GeoIP2
        for ip_prefix, geo_data in self.ip_database.items():
            if ip_address.startswith(ip_prefix):
                country_code = geo_data["country"]
                country_info = self.country_mappings.get(country_code, {})
                
                return GeoLocation(
                    country_code=country_code,
                    country_name=country_info.get("name", "Unknown"),
                    region=geo_data["region"],
                    timezone=country_info.get("timezone"),
                    source=GeolocationSource.IP_ADDRESS,
                    confidence=0.85,
                    metadata={
                        "ip_prefix": ip_prefix,
                        "lookup_method": "simulation"
                    }
                )
        
        # IP non trouvé - location par défaut
        return GeoLocation(
            country_code="UNKNOWN",
            country_name="Unknown",
            region=GeographicRegion.UNKNOWN,
            source=GeolocationSource.IP_ADDRESS,
            confidence=0.1,
            metadata={"reason": "ip_not_found"}
        )
    
    async def _enrich_geolocation(self, geolocation: GeoLocation, 
                                context: Dict[str, Any]) -> GeoLocation:
        """Enrichissement géolocalisation avec context"""
        # Enrichissement avec user agent
        if "user_agent" in context:
            user_agent = context["user_agent"]
            if "Mobile" in user_agent:
                geolocation.metadata["device_type"] = "mobile"
            elif "Bot" in user_agent:
                geolocation.metadata["device_type"] = "bot"
                geolocation.confidence *= 0.7  # Reduce confidence for bots
        
        # Enrichissement avec declared location
        if "declared_location" in context:
            declared = context["declared_location"]
            declared_country = declared.get("country")
            
            if declared_country and declared_country != geolocation.country_code:
                geolocation.metadata["location_mismatch"] = True
                geolocation.metadata["declared_country"] = declared_country
                geolocation.confidence *= 0.8  # Reduce confidence for mismatches
        
        return geolocation

class RegionalComplianceEngine:
    """Moteur compliance régionale"""
    
    def __init__(self, config: GeoConfig):
        self.config = config
        self.compliance_rules = self._load_compliance_rules()
        self.audit_trails = deque(maxlen=100000)
        self.violation_history = defaultdict(list)
        self.logger = logging.getLogger(__name__)
    
    def _load_compliance_rules(self) -> Dict[ComplianceRegime, Dict[str, Any]]:
        """Chargement règles compliance"""
        return {
            ComplianceRegime.GDPR: {
                "max_requests_per_hour": 1000,
                "data_retention_days": 30,
                "consent_required": True,
                "right_to_deletion": True,
                "data_portability": True,
                "breach_notification_hours": 72,
                "penalties": {"minor": 10000, "major": 20000000}
            },
            ComplianceRegime.CCPA: {
                "max_requests_per_hour": 1500,
                "data_retention_days": 60,
                "consent_required": False,
                "right_to_deletion": True,
                "data_portability": True,
                "breach_notification_hours": 72,
                "penalties": {"minor": 2500, "major": 7500}
            },
            ComplianceRegime.PIPEDA: {
                "max_requests_per_hour": 1200,
                "data_retention_days": 365,
                "consent_required": True,
                "right_to_deletion": False,
                "data_portability": False,
                "breach_notification_hours": 72,
                "penalties": {"minor": 100000, "major": 100000}
            },
            ComplianceRegime.LGPD: {
                "max_requests_per_hour": 800,
                "data_retention_days": 90,
                "consent_required": True,
                "right_to_deletion": True,
                "data_portability": True,
                "breach_notification_hours": 72,
                "penalties": {"minor": 50000000, "major": 50000000}  # BRL
            }
        }
    
    async def enforce_regional_compliance(self, region: str, request: GeoRequest) -> ComplianceResult:
        """Enforcement compliance régionale"""
        try:
            # Détermination régime compliance
            compliance_regime = await self._determine_compliance_regime(region, request.geolocation)
            
            # Récupération règles
            rules = self.compliance_rules.get(compliance_regime, {})
            if not rules:
                return ComplianceResult(
                    compliant=True,
                    regime=ComplianceRegime.STANDARD,
                    requirements_met=["default_compliance"],
                    violations=[],
                    required_actions=[]
                )
            
            # Vérifications compliance
            violations = []
            requirements_met = []
            required_actions = []
            
            # Vérification rate limiting
            max_requests = rules.get("max_requests_per_hour", 1000)
            current_usage = await self._get_current_usage(request.identifier, region)
            
            if current_usage > max_requests:
                violations.append(f"Rate limit exceeded: {current_usage} > {max_requests}")
                required_actions.append("Reduce request rate")
            else:
                requirements_met.append("rate_limit_compliance")
            
            # Vérification consent (pour GDPR/LGPD)
            if rules.get("consent_required", False):
                consent_status = await self._check_consent_status(request.identifier)
                if not consent_status:
                    violations.append("User consent required but not provided")
                    required_actions.append("Obtain user consent")
                else:
                    requirements_met.append("consent_compliance")
            
            # Vérification data retention
            retention_days = rules.get("data_retention_days", 365)
            data_age = await self._check_data_age(request.identifier)
            if data_age > retention_days:
                violations.append(f"Data retention exceeded: {data_age} > {retention_days} days")
                required_actions.append("Delete or anonymize old data")
            else:
                requirements_met.append("data_retention_compliance")
            
            # Génération audit trail
            audit_trail_id = await self._generate_audit_trail(request, compliance_regime, violations)
            
            # Calcul grace period si violations
            grace_period_expires = None
            if violations:
                grace_period_expires = datetime.now() + timedelta(hours=24)  # 24h grace period
            
            # Résultat compliance
            result = ComplianceResult(
                compliant=len(violations) == 0,
                regime=compliance_regime,
                requirements_met=requirements_met,
                violations=violations,
                required_actions=required_actions,
                grace_period_expires=grace_period_expires,
                audit_trail_id=audit_trail_id
            )
            
            # Enregistrement violations pour tracking
            if violations:
                self.violation_history[request.identifier].extend(violations)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Regional compliance enforcement failed: {e}")
            return ComplianceResult(
                compliant=False,
                regime=ComplianceRegime.STANDARD,
                requirements_met=[],
                violations=[f"Compliance check error: {str(e)}"],
                required_actions=["Retry compliance check"]
            )
    
    async def _determine_compliance_regime(self, region: str, 
                                         geolocation: Optional[GeoLocation]) -> ComplianceRegime:
        """Détermination régime compliance"""
        if not geolocation:
            return self.config.default_compliance_regime
        
        # Mapping pays -> régime
        country_regimes = {
            "DE": ComplianceRegime.GDPR,
            "FR": ComplianceRegime.GDPR, 
            "GB": ComplianceRegime.GDPR,
            "IT": ComplianceRegime.GDPR,
            "ES": ComplianceRegime.GDPR,
            "US": ComplianceRegime.CCPA,  # Simplified - would be state-specific
            "CA": ComplianceRegime.PIPEDA,
            "BR": ComplianceRegime.LGPD,
            "SG": ComplianceRegime.PDPA_SG,
            "TH": ComplianceRegime.PDPA_TH
        }
        
        return country_regimes.get(geolocation.country_code, self.config.default_compliance_regime)
    
    async def _get_current_usage(self, identifier: str, region: str) -> int:
        """Récupération usage actuel"""
        # Simulation - dans une vraie implémentation, query depuis rate limiter
        return 50  # requests per hour
    
    async def _check_consent_status(self, identifier: str) -> bool:
        """Vérification status consent"""
        # Simulation - dans une vraie implémentation, query depuis consent management
        return True  # Assume consent given
    
    async def _check_data_age(self, identifier: str) -> int:
        """Vérification âge données"""
        # Simulation - dans une vraie implémentation, query depuis data storage
        return 15  # days
    
    async def _generate_audit_trail(self, request: GeoRequest, 
                                  regime: ComplianceRegime, violations: List[str]) -> str:
        """Génération audit trail"""
        audit_id = str(uuid.uuid4())
        
        audit_entry = {
            "audit_id": audit_id,
            "timestamp": datetime.now().isoformat(),
            "identifier": request.identifier,
            "compliance_regime": regime.value,
            "geolocation": {
                "country": request.geolocation.country_code if request.geolocation else "UNKNOWN",
                "region": request.geolocation.region.value if request.geolocation else "UNKNOWN"
            },
            "violations": violations,
            "compliant": len(violations) == 0
        }
        
        self.audit_trails.append(audit_entry)
        return audit_id

class GeoFraudDetector:
    """Détecteur fraud géographique"""
    
    def __init__(self, config: GeoConfig):
        self.config = config
        self.user_patterns = defaultdict(lambda: deque(maxlen=1000))
        self.fraud_indicators = {}
        self.anomaly_thresholds = self._load_anomaly_thresholds()
        self.logger = logging.getLogger(__name__)
    
    def _load_anomaly_thresholds(self) -> Dict[str, float]:
        """Chargement seuils anomalie"""
        return {
            "max_countries_per_hour": 5,
            "max_regions_per_hour": 3,
            "velocity_threshold": 100,  # requests per hour across regions
            "distance_threshold_km": 1000,  # impossible travel distance
            "time_window_minutes": 60
        }
    
    async def detect_geographic_anomalies(self, request_pattern: GeoPattern) -> List[GeoAnomaly]:
        """Détection anomalies géographiques"""
        anomalies = []
        
        try:
            # Anomalie: trop de pays en peu de temps
            country_anomaly = await self._detect_country_hopping(request_pattern)
            if country_anomaly:
                anomalies.append(country_anomaly)
            
            # Anomalie: velocity suspecte
            velocity_anomaly = await self._detect_suspicious_velocity(request_pattern)
            if velocity_anomaly:
                anomalies.append(velocity_anomaly)
            
            # Anomalie: travel impossible
            travel_anomaly = await self._detect_impossible_travel(request_pattern)
            if travel_anomaly:
                anomalies.append(travel_anomaly)
            
            # Anomalie: patterns bots
            bot_anomaly = await self._detect_bot_patterns(request_pattern)
            if bot_anomaly:
                anomalies.append(bot_anomaly)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Geographic anomaly detection failed: {e}")
            return []
    
    async def _detect_country_hopping(self, pattern: GeoPattern) -> Optional[GeoAnomaly]:
        """Détection country hopping"""
        max_countries = self.anomaly_thresholds["max_countries_per_hour"]
        
        if len(pattern.countries_accessed) > max_countries:
            return GeoAnomaly(
                anomaly_id=str(uuid.uuid4()),
                anomaly_type="country_hopping",
                affected_regions=pattern.regions_accessed,
                affected_countries=pattern.countries_accessed,
                severity="high",
                confidence=0.9,
                detected_at=datetime.now(),
                description=f"User accessed {len(pattern.countries_accessed)} countries in {pattern.time_span_hours} hours",
                indicators=[
                    f"countries_accessed: {pattern.countries_accessed}",
                    f"time_span: {pattern.time_span_hours}h",
                    f"request_count: {pattern.request_count}"
                ],
                recommended_action="restrict_geographic_access",
                auto_mitigation=True
            )
        
        return None
    
    async def _detect_suspicious_velocity(self, pattern: GeoPattern) -> Optional[GeoAnomaly]:
        """Détection velocity suspecte"""
        velocity_threshold = self.anomaly_thresholds["velocity_threshold"]
        
        if pattern.velocity_score > velocity_threshold:
            return GeoAnomaly(
                anomaly_id=str(uuid.uuid4()),
                anomaly_type="suspicious_velocity",
                affected_regions=pattern.regions_accessed,
                affected_countries=pattern.countries_accessed,
                severity="medium",
                confidence=0.8,
                detected_at=datetime.now(),
                description=f"High velocity detected: {pattern.velocity_score:.1f} req/h across regions",
                indicators=[
                    f"velocity_score: {pattern.velocity_score}",
                    f"regions: {len(pattern.regions_accessed)}",
                    f"consistency: {pattern.consistency_score}"
                ],
                recommended_action="rate_limit_reduction",
                auto_mitigation=False
            )
        
        return None
    
    async def _detect_impossible_travel(self, pattern: GeoPattern) -> Optional[GeoAnomaly]:
        """Détection travel impossible"""
        # Simulation calcul distance/temps
        if len(pattern.countries_accessed) >= 2 and pattern.time_span_hours <= 1:
            # Check si countries sont géographiquement éloignés
            if await self._are_countries_distant(pattern.countries_accessed):
                return GeoAnomaly(
                    anomaly_id=str(uuid.uuid4()),
                    anomaly_type="impossible_travel",
                    affected_regions=pattern.regions_accessed,
                    affected_countries=pattern.countries_accessed,
                    severity="critical",
                    confidence=0.95,
                    detected_at=datetime.now(),
                    description="Impossible physical travel detected between geographic locations",
                    indicators=[
                        f"countries: {pattern.countries_accessed}",
                        f"time_span: {pattern.time_span_hours}h",
                        "distance_check: impossible"
                    ],
                    recommended_action="block_user_temporarily",
                    auto_mitigation=True
                )
        
        return None
    
    async def _detect_bot_patterns(self, pattern: GeoPattern) -> Optional[GeoAnomaly]:
        """Détection patterns bots"""
        # Pattern bot: consistency très élevée + velocity élevée
        if (pattern.consistency_score > 0.95 and 
            pattern.velocity_score > 50 and
            len(pattern.regions_accessed) > 2):
            
            return GeoAnomaly(
                anomaly_id=str(uuid.uuid4()),
                anomaly_type="bot_behavior",
                affected_regions=pattern.regions_accessed,
                affected_countries=pattern.countries_accessed,
                severity="medium",
                confidence=0.7,
                detected_at=datetime.now(),
                description="Bot-like behavior pattern detected across multiple regions",
                indicators=[
                    f"consistency_score: {pattern.consistency_score}",
                    f"velocity_score: {pattern.velocity_score}",
                    f"regions_span: {len(pattern.regions_accessed)}"
                ],
                recommended_action="challenge_user",
                auto_mitigation=False
            )
        
        return None
    
    async def _are_countries_distant(self, countries: List[str]) -> bool:
        """Vérification distance pays"""
        # Simulation - dans une vraie implémentation, utiliser calculs géographiques
        distant_pairs = [
            ("US", "JP"), ("DE", "AU"), ("BR", "CN"), ("CA", "IN")
        ]
        
        for i, country1 in enumerate(countries):
            for country2 in countries[i+1:]:
                if (country1, country2) in distant_pairs or (country2, country1) in distant_pairs:
                    return True
        
        return False
    
    async def calculate_fraud_score(self, request: GeoRequest, 
                                  patterns: List[GeoPattern]) -> Tuple[float, FraudRiskLevel]:
        """Calcul score fraud"""
        fraud_score = 0.0
        
        try:
            # Score basé sur géolocalisation
            if request.geolocation:
                if request.geolocation.confidence < 0.5:
                    fraud_score += 0.2  # Low confidence location
                
                if request.geolocation.country_code in self.config.blocked_countries:
                    fraud_score += 0.8  # Blocked country
            
            # Score basé sur patterns
            for pattern in patterns:
                if len(pattern.countries_accessed) > 3:
                    fraud_score += 0.3
                
                if pattern.velocity_score > 100:
                    fraud_score += 0.4
                
                if pattern.consistency_score > 0.9:
                    fraud_score += 0.2  # Very consistent = potentially automated
            
            # Score basé sur request metadata
            if request.user_agent:
                if "bot" in request.user_agent.lower():
                    fraud_score += 0.5
                if len(request.user_agent) < 20:  # Very short user agent
                    fraud_score += 0.3
            
            # Normalisation score
            fraud_score = min(1.0, fraud_score)
            
            # Détermination risk level
            if fraud_score >= 0.8:
                risk_level = FraudRiskLevel.CRITICAL
            elif fraud_score >= 0.6:
                risk_level = FraudRiskLevel.HIGH
            elif fraud_score >= 0.4:
                risk_level = FraudRiskLevel.MEDIUM
            else:
                risk_level = FraudRiskLevel.LOW
            
            return fraud_score, risk_level
            
        except Exception as e:
            self.logger.error(f"Fraud score calculation failed: {e}")
            return 0.5, FraudRiskLevel.MEDIUM

class GeolocationRateLimiter:
    """
    Rate Limiter avec géolocalisation pour compliance régionale.
    Geographic limits + compliance + fraud detection.
    """
    
    def __init__(self, distributed_limiter: DistributedRateLimiter, geo_config: GeoConfig):
        self.distributed_limiter = distributed_limiter
        self.geo_config = geo_config
        self.geo_detector = GeolocationDetector(geo_config)
        self.compliance_engine = RegionalComplianceEngine(geo_config)
        self.fraud_detector = GeoFraudDetector(geo_config)
        self.regional_limiters = {}
        
        # Tracking cross-border
        self.cross_border_tracking = defaultdict(lambda: deque(maxlen=1000))
        self.regional_quotas = {}
        self.coordination_cache = {}
        
        # Métriques
        self.geo_metrics = {
            "total_requests": 0,
            "cross_border_requests": 0,
            "compliance_violations": 0,
            "fraud_detections": 0,
            "regional_blocks": 0
        }
        
        self.logger = logging.getLogger(__name__)
        
        # Background tasks
        self._background_tasks = []
        self._stop_event = asyncio.Event()
    
    async def initialize(self) -> bool:
        """Initialisation geolocation rate limiter"""
        try:
            # Initialisation distributed limiter base
            await self.distributed_limiter.initialize()
            
            # Initialisation limiters régionaux
            await self._initialize_regional_limiters()
            
            # Chargement quotas régionaux
            await self._load_regional_quotas()
            
            # Démarrage background tasks
            await self._start_background_tasks()
            
            self.logger.info("Geolocation rate limiter initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Geolocation rate limiter initialization failed: {e}")
            return False
    
    async def apply_geolocation_limits(self, request: GeoRequest) -> GeoLimitResult:
        """
        Application rate limits basés sur géolocalisation.
        
        Geolocation Features:
        - Geographic rate limiting par région/pays
        - Compliance-aware rate limiting (GDPR/CCPA)
        - Fraud detection basé sur geographic anomalies
        - Regional load balancing avec rate coordination
        - Time-zone aware rate limiting
        - Cross-border request tracking
        - Regional quota allocation et management
        """
        start_time = time.time()
        self.geo_metrics["total_requests"] += 1
        
        try:
            # 1. Détection géolocalisation
            if not request.geolocation:
                request.geolocation = await self.geo_detector.detect_geolocation(
                    request.ip_address, {
                        "user_agent": request.user_agent,
                        "declared_location": request.declared_location
                    }
                )
            
            # 2. Vérification pays/régions bloqués
            if await self._is_blocked_location(request.geolocation):
                self.geo_metrics["regional_blocks"] += 1
                return GeoLimitResult(
                    allowed=False,
                    geolocation=request.geolocation,
                    compliance_regime=ComplianceRegime.STANDARD,
                    regional_limits_applied={},
                    fraud_score=1.0,
                    fraud_risk_level=FraudRiskLevel.CRITICAL,
                    geo_anomalies=["blocked_location"],
                    rate_limit_result=RateLimitResult(
                        status=RateLimitStatus.DENIED,
                        allowed=False
                    ),
                    compliance_warnings=["Location blocked by policy"]
                )
            
            # 3. Enforcement compliance régionale
            compliance_result = await self.compliance_engine.enforce_regional_compliance(
                request.geolocation.region.value, request
            )
            
            if not compliance_result.compliant:
                self.geo_metrics["compliance_violations"] += 1
                return GeoLimitResult(
                    allowed=False,
                    geolocation=request.geolocation,
                    compliance_regime=compliance_result.regime,
                    regional_limits_applied={},
                    fraud_score=0.5,
                    fraud_risk_level=FraudRiskLevel.MEDIUM,
                    geo_anomalies=[],
                    rate_limit_result=RateLimitResult(
                        status=RateLimitStatus.DENIED,
                        allowed=False
                    ),
                    compliance_warnings=compliance_result.violations
                )
            
            # 4. Détection anomalies géographiques
            user_pattern = await self._build_user_pattern(request)
            geo_anomalies = await self.fraud_detector.detect_geographic_anomalies(user_pattern)
            
            # 5. Calcul fraud score
            fraud_score, fraud_risk_level = await self.fraud_detector.calculate_fraud_score(
                request, [user_pattern]
            )
            
            # 6. Blocage si fraud critique
            if fraud_risk_level == FraudRiskLevel.CRITICAL:
                self.geo_metrics["fraud_detections"] += 1
                return GeoLimitResult(
                    allowed=False,
                    geolocation=request.geolocation,
                    compliance_regime=compliance_result.regime,
                    regional_limits_applied={},
                    fraud_score=fraud_score,
                    fraud_risk_level=fraud_risk_level,
                    geo_anomalies=[a.anomaly_type for a in geo_anomalies],
                    rate_limit_result=RateLimitResult(
                        status=RateLimitStatus.DENIED,
                        allowed=False
                    ),
                    compliance_warnings=["High fraud risk detected"]
                )
            
            # 7. Application rate limiting régional
            regional_rate_result = await self._apply_regional_rate_limiting(request)
            
            # 8. Détection cross-border
            cross_border_detected = await self._detect_cross_border_request(request)
            if cross_border_detected:
                self.geo_metrics["cross_border_requests"] += 1
            
            # 9. Coordination régionale si nécessaire
            coordination_applied = False
            if self.geo_config.enable_regional_optimization:
                coordination_applied = await self._apply_regional_coordination(request)
            
            # 10. Construction résultat final
            result = GeoLimitResult(
                allowed=regional_rate_result.allowed,
                geolocation=request.geolocation,
                compliance_regime=compliance_result.regime,
                regional_limits_applied=await self._get_applied_regional_limits(request),
                fraud_score=fraud_score,
                fraud_risk_level=fraud_risk_level,
                geo_anomalies=[a.anomaly_type for a in geo_anomalies],
                rate_limit_result=regional_rate_result,
                cross_border_detected=cross_border_detected,
                compliance_warnings=compliance_result.violations,
                metadata={
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "regional_limiter_used": request.geolocation.region.value,
                    "coordination_applied": coordination_applied,
                    "anomalies_detected": len(geo_anomalies)
                }
            )
            
            # 11. Tracking pour patterns futurs
            await self._track_request_pattern(request, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Geolocation rate limiting failed for {request.identifier}: {e}")
            return GeoLimitResult(
                allowed=False,
                geolocation=GeoLocation(
                    country_code="ERROR",
                    country_name="Error",
                    region=GeographicRegion.UNKNOWN
                ),
                compliance_regime=ComplianceRegime.STANDARD,
                regional_limits_applied={},
                fraud_score=0.5,
                fraud_risk_level=FraudRiskLevel.MEDIUM,
                geo_anomalies=["processing_error"],
                rate_limit_result=RateLimitResult(
                    status=RateLimitStatus.ERROR,
                    allowed=False
                ),
                metadata={"error": str(e)}
            )
    
    async def _initialize_regional_limiters(self):
        """Initialisation limiters régionaux"""
        for region in GeographicRegion:
            if region == GeographicRegion.UNKNOWN:
                continue
            
            # Configuration spécialisée par région
            regional_config = await self._get_regional_config(region)
            
            # Création limiter régional
            regional_limiter = DistributedRateLimiter(
                self.distributed_limiter.redis,
                regional_config
            )
            await regional_limiter.initialize()
            
            self.regional_limiters[region] = regional_limiter
    
    async def _get_regional_config(self, region: GeographicRegion) -> RateLimitConfig:
        """Configuration spécialisée par région"""
        base_config = self.distributed_limiter.config
        
        # Customizations par région
        regional_settings = {
            GeographicRegion.EUROPE: {
                "requests_per_second": 50,  # Plus restrictif pour GDPR
                "burst_capacity": 100,
                "redis_key_prefix": "eu_rl"
            },
            GeographicRegion.NORTH_AMERICA: {
                "requests_per_second": 100,
                "burst_capacity": 200,
                "redis_key_prefix": "na_rl"
            },
            GeographicRegion.ASIA_PACIFIC: {
                "requests_per_second": 80,
                "burst_capacity": 160,
                "redis_key_prefix": "ap_rl"
            },
            GeographicRegion.SOUTH_AMERICA: {
                "requests_per_second": 30,  # Plus restrictif pour LGPD
                "burst_capacity": 60,
                "redis_key_prefix": "sa_rl"
            }
        }
        
        settings = regional_settings.get(region, {
            "requests_per_second": base_config.requests_per_second,
            "burst_capacity": base_config.burst_capacity,
            "redis_key_prefix": base_config.redis_key_prefix
        })
        
        return RateLimitConfig(
            requests_per_second=settings["requests_per_second"],
            burst_capacity=settings["burst_capacity"],
            window_size_seconds=base_config.window_size_seconds,
            algorithm=base_config.algorithm,
            redis_key_prefix=settings["redis_key_prefix"],
            compliance_mode="strict" if region == GeographicRegion.EUROPE else "standard"
        )
    
    async def _load_regional_quotas(self):
        """Chargement quotas régionaux"""
        self.regional_quotas = {
            GeographicRegion.EUROPE: {"daily_quota": 50000, "hourly_quota": 2500},
            GeographicRegion.NORTH_AMERICA: {"daily_quota": 100000, "hourly_quota": 5000},
            GeographicRegion.ASIA_PACIFIC: {"daily_quota": 80000, "hourly_quota": 4000},
            GeographicRegion.SOUTH_AMERICA: {"daily_quota": 30000, "hourly_quota": 1500}
        }
    
    async def _is_blocked_location(self, geolocation: GeoLocation) -> bool:
        """Vérification location bloquée"""
        if geolocation.country_code in self.geo_config.blocked_countries:
            return True
        
        if geolocation.region in self.geo_config.restricted_regions:
            return True
        
        return False
    
    async def _build_user_pattern(self, request: GeoRequest) -> GeoPattern:
        """Construction pattern utilisateur"""
        # Récupération historique requests utilisateur
        user_history = self.cross_border_tracking.get(request.identifier, deque())
        
        # Analyse dernières 24h
        now = datetime.now()
        recent_requests = [
            r for r in user_history 
            if (now - r["timestamp"]).total_seconds() < 86400  # 24h
        ]
        
        # Extraction countries et regions
        countries_accessed = list(set(r["country"] for r in recent_requests))
        regions_accessed = list(set(GeographicRegion(r["region"]) for r in recent_requests))
        
        # Calcul métriques
        time_span_hours = 24 if recent_requests else 0
        request_count = len(recent_requests)
        velocity_score = request_count / max(1, time_span_hours)
        
        # Calcul consistency score
        if request_count > 1:
            intervals = []
            for i in range(1, len(recent_requests)):
                interval = (recent_requests[i]["timestamp"] - recent_requests[i-1]["timestamp"]).total_seconds()
                intervals.append(interval)
            
            if intervals:
                consistency_score = 1.0 - (statistics.stdev(intervals) / max(1, statistics.mean(intervals)))
                consistency_score = max(0.0, min(1.0, consistency_score))
            else:
                consistency_score = 1.0
        else:
            consistency_score = 0.0
        
        return GeoPattern(
            pattern_id=str(uuid.uuid4()),
            user_id=request.identifier,
            countries_accessed=countries_accessed,
            regions_accessed=regions_accessed,
            time_span_hours=time_span_hours,
            request_count=request_count,
            velocity_score=velocity_score,
            consistency_score=consistency_score,
            risk_indicators=[]
        )
    
    async def _apply_regional_rate_limiting(self, request: GeoRequest) -> RateLimitResult:
        """Application rate limiting régional"""
        region = request.geolocation.region
        regional_limiter = self.regional_limiters.get(region, self.distributed_limiter)
        
        # Construction identifiant avec namespace région
        regional_identifier = f"{region.value}:{request.identifier}"
        
        return await regional_limiter.check_rate_limit(
            regional_identifier,
            request.cost,
            request.metadata
        )
    
    async def _detect_cross_border_request(self, request: GeoRequest) -> bool:
        """Détection request cross-border"""
        if not self.geo_config.enable_cross_border_tracking:
            return False
        
        user_history = self.cross_border_tracking.get(request.identifier, deque())
        
        if not user_history:
            return False
        
        # Vérification dernière location
        last_request = user_history[-1] if user_history else None
        if last_request:
            last_country = last_request["country"]
            current_country = request.geolocation.country_code
            
            return last_country != current_country
        
        return False
    
    async def _apply_regional_coordination(self, request: GeoRequest) -> bool:
        """Application coordination régionale"""
        # Simulation coordination - dans une vraie implémentation,
        # coordonner avec autres instances régionales
        return True
    
    async def _get_applied_regional_limits(self, request: GeoRequest) -> Dict[str, int]:
        """Récupération limites régionales appliquées"""
        region = request.geolocation.region
        regional_quota = self.regional_quotas.get(region, {})
        
        return {
            "regional_hourly_limit": regional_quota.get("hourly_quota", 1000),
            "regional_daily_limit": regional_quota.get("daily_quota", 24000),
            "country_limit": self.geo_config.max_requests_per_country
        }
    
    async def _track_request_pattern(self, request: GeoRequest, result: GeoLimitResult):
        """Tracking pattern request pour analyses futures"""
        tracking_entry = {
            "timestamp": request.timestamp,
            "country": request.geolocation.country_code,
            "region": request.geolocation.region.value,
            "allowed": result.allowed,
            "fraud_score": result.fraud_score,
            "compliance_regime": result.compliance_regime.value
        }
        
        self.cross_border_tracking[request.identifier].append(tracking_entry)
    
    async def _start_background_tasks(self):
        """Démarrage tâches background"""
        # Tâche cleanup tracking data
        cleanup_task = asyncio.create_task(self._tracking_cleanup_loop())
        self._background_tasks.append(cleanup_task)
        
        # Tâche analysis patterns géographiques
        pattern_task = asyncio.create_task(self._pattern_analysis_loop())
        self._background_tasks.append(pattern_task)
        
        # Tâche update regional quotas
        quota_task = asyncio.create_task(self._quota_update_loop())
        self._background_tasks.append(quota_task)
    
    async def _tracking_cleanup_loop(self):
        """Loop cleanup données tracking anciennes"""
        while not self._stop_event.is_set():
            try:
                cutoff_time = datetime.now() - timedelta(days=7)
                
                for user_id, tracking_data in self.cross_border_tracking.items():
                    # Filtrage données anciennes
                    recent_data = deque([
                        entry for entry in tracking_data 
                        if entry["timestamp"] > cutoff_time
                    ], maxlen=1000)
                    
                    self.cross_border_tracking[user_id] = recent_data
                
                await asyncio.sleep(3600)  # Every hour
            except Exception as e:
                self.logger.error(f"Tracking cleanup error: {e}")
                await asyncio.sleep(300)
    
    async def _pattern_analysis_loop(self):
        """Loop analysis patterns géographiques"""
        while not self._stop_event.is_set():
            try:
                # Analyse patterns suspects pour tous utilisateurs
                suspect_patterns = await self._analyze_all_user_patterns()
                
                # Processing patterns suspects
                for pattern in suspect_patterns:
                    await self._handle_suspect_pattern(pattern)
                
                await asyncio.sleep(1800)  # Every 30 minutes
            except Exception as e:
                self.logger.error(f"Pattern analysis error: {e}")
                await asyncio.sleep(600)
    
    async def _quota_update_loop(self):
        """Loop update quotas régionaux"""
        while not self._stop_event.is_set():
            try:
                # Update quotas basé sur usage
                await self._update_regional_quotas_based_on_usage()
                
                await asyncio.sleep(3600)  # Every hour
            except Exception as e:
                self.logger.error(f"Quota update error: {e}")
                await asyncio.sleep(600)
    
    async def get_geolocation_status(self, identifier: str) -> Dict[str, Any]:
        """Status géolocalisation complet"""
        try:
            user_pattern = await self._get_user_current_pattern(identifier)
            fraud_score, fraud_risk = await self.fraud_detector.calculate_fraud_score(
                GeoRequest(identifier=identifier, ip_address="0.0.0.0"), [user_pattern]
            )
            
            return {
                "identifier": identifier,
                "current_pattern": user_pattern.__dict__ if user_pattern else None,
                "fraud_assessment": {
                    "fraud_score": fraud_score,
                    "risk_level": fraud_risk.value
                },
                "tracking_history_size": len(self.cross_border_tracking.get(identifier, [])),
                "metrics": self.geo_metrics,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    # Helper methods pour operations internes
    async def _analyze_all_user_patterns(self) -> List[GeoPattern]:
        """Analyse patterns tous utilisateurs"""
        return []  # Simplified
    
    async def _handle_suspect_pattern(self, pattern: GeoPattern):
        """Handling pattern suspect"""
        pass  # Simplified
    
    async def _update_regional_quotas_based_on_usage(self):
        """Update quotas basé sur usage"""
        pass  # Simplified
    
    async def _get_user_current_pattern(self, identifier: str) -> Optional[GeoPattern]:
        """Pattern actuel utilisateur"""
        return None  # Simplified

# Factory functions
def create_gdpr_compliant_limiter(redis_client) -> GeolocationRateLimiter:
    """Factory pour limiter GDPR-compliant"""
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=50,
        burst_capacity=100,
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        redis_key_prefix="gdpr_rl",
        compliance_mode="strict"
    ))
    
    geo_config = GeoConfig(
        enable_compliance_enforcement=True,
        enable_fraud_detection=True,
        enable_regional_optimization=True,
        default_compliance_regime=ComplianceRegime.GDPR,
        max_requests_per_country=5000,
        suspicious_threshold_ratio=3.0,
        enable_cross_border_tracking=True,
        blocked_countries=["XX", "YY"],  # Example blocked countries
        restricted_regions=[GeographicRegion.UNKNOWN]
    )
    
    return GeolocationRateLimiter(base_limiter, geo_config)

def create_global_rate_limiter(redis_client) -> GeolocationRateLimiter:
    """Factory pour limiter global"""
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=100,
        burst_capacity=200,
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
        redis_key_prefix="global_rl"
    ))
    
    geo_config = GeoConfig(
        enable_compliance_enforcement=True,
        enable_fraud_detection=True,
        enable_regional_optimization=True,
        default_compliance_regime=ComplianceRegime.STANDARD,
        max_requests_per_country=20000,
        suspicious_threshold_ratio=10.0,
        enable_cross_border_tracking=True
    )
    
    return GeolocationRateLimiter(base_limiter, geo_config)

# Export classes principales
__all__ = [
    'GeolocationRateLimiter',
    'GeoConfig',
    'GeoRequest',
    'GeoLimitResult',
    'GeoLocation',
    'GeoAnomaly',
    'GeographicRegion',
    'ComplianceRegime',
    'FraudRiskLevel',
    'create_gdpr_compliant_limiter',
    'create_global_rate_limiter'
]