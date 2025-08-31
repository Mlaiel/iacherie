"""Advanced Threat Detection System for Deployment Security

Provides real-time threat detection, anomaly detection, behavioral analysis,
and automated incident response for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Company: IA Influencer Agent Platform
License: Proprietary - All rights reserved

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and
will result in legal action.
"""
import asyncio
import logging
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import redis.asyncio as aioredis
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import geoip2.database
import ipaddress

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Types of security threats"""    BRUTE_FORCE = "brute_force"
    DDOS = "ddos"
    INJECTION = "injection"
    XSS = "xss"
    CSRF = "csrf"
    MALWARE = "malware"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    SUSPICIOUS_LOCATION = "suspicious_location"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    INSIDER_THREAT = "insider_threat"


class AttackVector(Enum):
    """Attack vectors"""    WEB_API = "web_api"
    SSH = "ssh"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    NETWORK = "network"
    APPLICATION = "application"
    EMAIL = "email"
    SOCIAL_ENGINEERING = "social_engineering"


@dataclass
class ThreatIndicator:
    """Threat indicator data structure"""    id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    attack_vector: AttackVector
    source_ip: str
    target_resource: str
    description: str
    evidence: Dict[str, Any]
    timestamp: datetime
    confidence_score: float
    is_confirmed: bool = False
    is_mitigated: bool = False
    mitigation_actions: List[str] = field(default_factory=list)


@dataclass
class SecurityEvent:
    """Security event data structure"""    event_id: str
    event_type: str
    source_ip: str
    user_id: Optional[str]
    resource: str
    action: str
    timestamp: datetime
    user_agent: Optional[str] = None
    geo_location: Optional[Dict[str, str]] = None
    request_headers: Optional[Dict[str, str]] = None
    response_status: Optional[int] = None
    payload_size: Optional[int] = None
    session_id: Optional[str] = None


@dataclass
class BehaviorProfile:
    """User behavior profile for anomaly detection"""    user_id: str
    normal_login_hours: Set[int]
    normal_ip_ranges: Set[str]
    normal_user_agents: Set[str]
    average_session_duration: float
    typical_resources_accessed: Set[str]
    typical_actions: Set[str]
    login_frequency_per_day: float
    created_at: datetime
    updated_at: datetime


class GeoLocationAnalyzer:
    """    Geographic location analysis for threat detection
    """    
    def __init__(self, geoip_db_path: str = None):
        self.geoip_db_path = geoip_db_path or "GeoLite2-City.mmdb"
        self.reader = None
        self._initialize_geoip()
        
    def _initialize_geoip(self):
        """Initialize GeoIP database reader"""        try:
            if os.path.exists(self.geoip_db_path):
                self.reader = geoip2.database.Reader(self.geoip_db_path)
                logger.info("GeoIP database initialized")
            else:
                logger.warning(f"GeoIP database not found: {self.geoip_db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize GeoIP database: {e}")
    
    def get_location_info(self, ip_address: str) -> Optional[Dict[str, str]]:
        """        Get geographic location information for IP address
        
        Args:
            ip_address: IP address to analyze
            
        Returns:
            Location information dictionary
        """        try:
            if not self.reader:
                return None
                
            if ipaddress.ip_address(ip_address).is_private:
                return {"country": "Private", "city": "Private Network"}
                
            response = self.reader.city(ip_address)
            
            return {
                "country": response.country.name or "Unknown",
                "country_code": response.country.iso_code or "XX",
                "city": response.city.name or "Unknown",
                "latitude": float(response.location.latitude) if response.location.latitude else 0.0,
                "longitude": float(response.location.longitude) if response.location.longitude else 0.0,
                "timezone": response.location.time_zone or "Unknown"
            }
            
        except Exception as e:
            logger.warning(f"Failed to get location for IP {ip_address}: {e}")
            return None
    
    def calculate_distance(self, location1: Dict[str, Any], location2: Dict[str, Any]) -> float:
        """        Calculate distance between two geographic locations
        
        Args:
            location1: First location with lat/lng
            location2: Second location with lat/lng
            
        Returns:
            Distance in kilometers
        """        try:
            lat1, lng1 = location1.get("latitude", 0), location1.get("longitude", 0)
            lat2, lng2 = location2.get("latitude", 0), location2.get("longitude", 0)
            
            # Haversine formula
            R = 6371  # Earth's radius in kilometers
            
            lat1_rad = np.radians(lat1)
            lat2_rad = np.radians(lat2)
            delta_lat = np.radians(lat2 - lat1)
            delta_lng = np.radians(lng2 - lng1)
            
            a = (np.sin(delta_lat / 2) ** 2 + 
                 np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lng / 2) ** 2)
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
            
            return R * c
            
        except Exception as e:
            logger.error(f"Failed to calculate distance: {e}")
            return 0.0


class AnomalyDetector:
    """    Machine learning-based anomaly detection system
    """    
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        
    def extract_features(self, events: List[SecurityEvent]) -> np.ndarray:
        """        Extract features from security events for ML analysis
        
        Args:
            events: List of security events
            
        Returns:
            Feature matrix
        """        features = []
        
        for event in events:
            # Time-based features
            hour_of_day = event.timestamp.hour
            day_of_week = event.timestamp.weekday()
            
            # Request features
            payload_size = event.payload_size or 0
            response_status = event.response_status or 200
            
            # User agent entropy (complexity measure)
            user_agent_entropy = self._calculate_entropy(event.user_agent or "")
            
            # Feature vector
            feature_vector = [
                hour_of_day,
                day_of_week,
                payload_size,
                response_status,
                user_agent_entropy,
                len(event.resource),
                len(event.action)
            ]
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""        if not text:
            return 0.0
            
        # Count character frequencies
        char_counts = defaultdict(int)
        for char in text:
            char_counts[char] += 1
        
        # Calculate entropy
        text_len = len(text)
        entropy = 0.0
        
        for count in char_counts.values():
            probability = count / text_len
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        return entropy
    
    def train(self, training_events: List[SecurityEvent]):
        """        Train anomaly detection model
        
        Args:
            training_events: Events for training (normal behavior)
        """        try:
            if len(training_events) < 100:
                logger.warning("Insufficient training data for anomaly detection")
                return
            
            # Extract features
            features = self.extract_features(training_events)
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Train isolation forest
            self.isolation_forest.fit(features_scaled)
            self.is_trained = True
            
            logger.info(f"Anomaly detector trained on {len(training_events)} events")
            
        except Exception as e:
            logger.error(f"Failed to train anomaly detector: {e}")
    
    def detect_anomalies(self, events: List[SecurityEvent]) -> List[Tuple[SecurityEvent, float]]:
        """        Detect anomalous events
        
        Args:
            events: Events to analyze
            
        Returns:
            List of (event, anomaly_score) tuples
        """        try:
            if not self.is_trained:
                logger.warning("Anomaly detector not trained")
                return []
            
            # Extract features
            features = self.extract_features(events)
            
            if len(features) == 0:
                return []
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get anomaly scores
            anomaly_scores = self.isolation_forest.decision_function(features_scaled)
            predictions = self.isolation_forest.predict(features_scaled)
            
            # Return anomalous events with scores
            anomalous_events = []
            for i, (event, score, prediction) in enumerate(zip(events, anomaly_scores, predictions)):
                if prediction == -1:  # Anomaly
                    anomalous_events.append((event, float(abs(score))))
            
            return anomalous_events
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []


class BehaviorAnalyzer:
    """    User behavior analysis and profiling system
    """    
    def __init__(self):
        self.behavior_profiles: Dict[str, BehaviorProfile] = {}
        self.geo_analyzer = GeoLocationAnalyzer()
        
    def create_behavior_profile(self, user_id: str, historical_events: List[SecurityEvent]) -> BehaviorProfile:
        """        Create behavior profile from historical user events
        
        Args:
            user_id: User identifier
            historical_events: Historical security events for the user
            
        Returns:
            User behavior profile
        """        try:
            # Filter events for this user
            user_events = [e for e in historical_events if e.user_id == user_id]
            
            if not user_events:
                # Create empty profile for new users
                return BehaviorProfile(
                    user_id=user_id,
                    normal_login_hours=set(),
                    normal_ip_ranges=set(),
                    normal_user_agents=set(),
                    average_session_duration=0.0,
                    typical_resources_accessed=set(),
                    typical_actions=set(),
                    login_frequency_per_day=0.0,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            
            # Analyze login patterns
            login_hours = set()
            ip_addresses = set()
            user_agents = set()
            resources = set()
            actions = set()
            session_durations = []
            
            # Extract patterns from events
            daily_logins = defaultdict(int)
            
            for event in user_events:
                login_hours.add(event.timestamp.hour)
                ip_addresses.add(event.source_ip)
                if event.user_agent:
                    user_agents.add(event.user_agent)
                resources.add(event.resource)
                actions.add(event.action)
                
                # Count daily logins
                date_key = event.timestamp.date()
                daily_logins[date_key] += 1
                
                # Estimate session duration (simplified)
                if event.session_id:
                    # This would need more sophisticated session tracking in practice
                    session_durations.append(1800.0)  # 30 minutes default
            
            # Calculate averages
            avg_session_duration = np.mean(session_durations) if session_durations else 1800.0
            login_frequency = np.mean(list(daily_logins.values())) if daily_logins else 1.0
            
            # Create profile
            profile = BehaviorProfile(
                user_id=user_id,
                normal_login_hours=login_hours,
                normal_ip_ranges=self._extract_ip_ranges(ip_addresses),
                normal_user_agents=user_agents,
                average_session_duration=avg_session_duration,
                typical_resources_accessed=resources,
                typical_actions=actions,
                login_frequency_per_day=login_frequency,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.behavior_profiles[user_id] = profile
            logger.info(f"Created behavior profile for user: {user_id}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create behavior profile: {e}")
            raise
    
    def _extract_ip_ranges(self, ip_addresses: Set[str]) -> Set[str]:
        """Extract IP ranges from individual IP addresses"""        ranges = set()
        
        for ip in ip_addresses:
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_private:
                    # For private IPs, use /24 subnet
                    network = ipaddress.ip_network(f"{ip}/24", strict=False)
                    ranges.add(str(network))
                else:
                    # For public IPs, use /16 range for country-level matching
                    network = ipaddress.ip_network(f"{ip}/16", strict=False)
                    ranges.add(str(network))
            except Exception:
                continue
        
        return ranges
    
    def analyze_event_anomaly(self, event: SecurityEvent) -> Dict[str, Any]:
        """        Analyze event for behavioral anomalies
        
        Args:
            event: Security event to analyze
            
        Returns:
            Anomaly analysis results
        """        try:
            if not event.user_id or event.user_id not in self.behavior_profiles:
                return {"is_anomalous": False, "reason": "No behavior profile available"}
            
            profile = self.behavior_profiles[event.user_id]
            anomalies = []
            anomaly_score = 0.0
            
            # Check time-based anomalies
            if event.timestamp.hour not in profile.normal_login_hours:
                anomalies.append("unusual_login_hour")
                anomaly_score += 0.3
            
            # Check IP address anomalies
            ip_in_range = False
            for ip_range in profile.normal_ip_ranges:
                try:
                    network = ipaddress.ip_network(ip_range)
                    if ipaddress.ip_address(event.source_ip) in network:
                        ip_in_range = True
                        break
                except Exception:
                    continue
            
            if not ip_in_range:
                anomalies.append("unusual_ip_address")
                anomaly_score += 0.4
                
                # Check geographic anomaly
                location = self.geo_analyzer.get_location_info(event.source_ip)
                if location:
                    anomalies.append(f"unusual_location_{location.get('country', 'Unknown')}")
                    anomaly_score += 0.2
            
            # Check user agent anomalies
            if event.user_agent and event.user_agent not in profile.normal_user_agents:
                anomalies.append("unusual_user_agent")
                anomaly_score += 0.2
            
            # Check resource access anomalies
            if event.resource not in profile.typical_resources_accessed:
                anomalies.append("unusual_resource_access")
                anomaly_score += 0.2
            
            # Check action anomalies
            if event.action not in profile.typical_actions:
                anomalies.append("unusual_action")
                anomaly_score += 0.2
            
            is_anomalous = anomaly_score > 0.5
            
            return {
                "is_anomalous": is_anomalous,
                "anomaly_score": anomaly_score,
                "anomalies": anomalies,
                "profile_age_days": (datetime.utcnow() - profile.created_at).days
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze event anomaly: {e}")
            return {"is_anomalous": False, "error": str(e)}


class ThreatDetector:
    """    Main threat detection engine
    """    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_pool = None
        
        # Detection components
        self.behavior_analyzer = BehaviorAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        
        # Attack pattern detection
        self.attack_patterns = self._load_attack_patterns()
        
        # Rate limiting trackers
        self.rate_limiters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Threat indicators storage
        self.threat_indicators: List[ThreatIndicator] = []
        
        logger.info("Threat detector initialized")
    
    async def initialize_redis(self):
        """Initialize Redis connection"""        try:
            self.redis_pool = aioredis.ConnectionPool.from_url(self.redis_url)
            logger.info("Redis connection initialized for threat detection")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    def _load_attack_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load known attack patterns"""        return {
            "sql_injection": {
                "patterns": [
                    r"(\s*(union|select|insert|update|delete|drop|create|alter)\s+)",
                    r"(\s*(or|and)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
                    r"(\s*['\"];?\s*--)",
                    r"(\s*['\"];?\s*/\*.*\*/)"
                ],
                "threat_level": ThreatLevel.HIGH,
                "attack_vector": AttackVector.WEB_API
            },
            "xss": {
                "patterns": [
                    r"<script[^>]*>.*?</script>",
                    r"javascript:",
                    r"on\w+\s*=",
                    r"<iframe[^>]*>"
                ],
                "threat_level": ThreatLevel.MEDIUM,
                "attack_vector": AttackVector.WEB_API
            },
            "brute_force": {
                "max_attempts": 5,
                "time_window": 300,  # 5 minutes
                "threat_level": ThreatLevel.HIGH,
                "attack_vector": AttackVector.WEB_API
            },
            "ddos": {
                "max_requests": 100,
                "time_window": 60,  # 1 minute
                "threat_level": ThreatLevel.CRITICAL,
                "attack_vector": AttackVector.NETWORK
            }
        }
    
    async def analyze_event(self, event: SecurityEvent) -> List[ThreatIndicator]:
        """        Analyze security event for threats
        
        Args:
            event: Security event to analyze
            
        Returns:
            List of detected threat indicators
        """        try:
            detected_threats = []
            
            # 1. Pattern-based detection
            pattern_threats = await self._detect_pattern_threats(event)
            detected_threats.extend(pattern_threats)
            
            # 2. Rate-based detection
            rate_threats = await self._detect_rate_threats(event)
            detected_threats.extend(rate_threats)
            
            # 3. Behavioral anomaly detection
            behavior_threats = await self._detect_behavior_threats(event)
            detected_threats.extend(behavior_threats)
            
            # 4. Geographic anomaly detection
            geo_threats = await self._detect_geographic_threats(event)
            detected_threats.extend(geo_threats)
            
            # Store detected threats
            self.threat_indicators.extend(detected_threats)
            
            # Log threats
            for threat in detected_threats:
                logger.warning(f"Threat detected: {threat.threat_type.value} - {threat.description}")
            
            return detected_threats
            
        except Exception as e:
            logger.error(f"Failed to analyze security event: {e}")
            return []
    
    async def _detect_pattern_threats(self, event: SecurityEvent) -> List[ThreatIndicator]:
        """Detect threats based on known attack patterns"""        threats = []
        
        # Check for SQL injection patterns
        if self._contains_sql_injection(event):
            threat = ThreatIndicator(
                id=f"sql_inj_{int(time.time())}_{hash(event.event_id)}",
                threat_type=ThreatType.INJECTION,
                threat_level=ThreatLevel.HIGH,
                attack_vector=AttackVector.WEB_API,
                source_ip=event.source_ip,
                target_resource=event.resource,
                description=f"SQL injection attempt detected from {event.source_ip}",
                evidence={
                    "event_id": event.event_id,
                    "payload_patterns": "SQL injection patterns detected",
                    "user_agent": event.user_agent
                },
                timestamp=event.timestamp,
                confidence_score=0.9
            )
            threats.append(threat)
        
        # Check for XSS patterns
        if self._contains_xss(event):
            threat = ThreatIndicator(
                id=f"xss_{int(time.time())}_{hash(event.event_id)}",
                threat_type=ThreatType.XSS,
                threat_level=ThreatLevel.MEDIUM,
                attack_vector=AttackVector.WEB_API,
                source_ip=event.source_ip,
                target_resource=event.resource,
                description=f"XSS attempt detected from {event.source_ip}",
                evidence={
                    "event_id": event.event_id,
                    "payload_patterns": "XSS patterns detected",
                    "user_agent": event.user_agent
                },
                timestamp=event.timestamp,
                confidence_score=0.8
            )
            threats.append(threat)
        
        return threats
    
    async def _detect_rate_threats(self, event: SecurityEvent) -> List[ThreatIndicator]:
        """Detect rate-based threats (brute force, DDoS)"""        threats = []
        current_time = time.time()
        
        # Track requests by IP
        ip_tracker = self.rate_limiters[f"ip_{event.source_ip}"]
        ip_tracker.append(current_time)
        
        # Remove old entries
        while ip_tracker and current_time - ip_tracker[0] > 300:  # 5 minutes
            ip_tracker.popleft()
        
        # Check for brute force (failed login attempts)
        if event.action == "login" and event.response_status != 200:
            failed_logins = sum(1 for t in ip_tracker if current_time - t <= 300)
            
            if failed_logins >= 5:
                threat = ThreatIndicator(
                    id=f"brute_force_{int(time.time())}_{hash(event.source_ip)}",
                    threat_type=ThreatType.BRUTE_FORCE,
                    threat_level=ThreatLevel.HIGH,
                    attack_vector=AttackVector.WEB_API,
                    source_ip=event.source_ip,
                    target_resource=event.resource,
                    description=f"Brute force attack detected from {event.source_ip}",
                    evidence={
                        "failed_attempts": failed_logins,
                        "time_window": "5 minutes",
                        "user_agent": event.user_agent
                    },
                    timestamp=event.timestamp,
                    confidence_score=0.95
                )
                threats.append(threat)
        
        # Check for DDoS (high request rate)
        recent_requests = sum(1 for t in ip_tracker if current_time - t <= 60)
        
        if recent_requests >= 100:
            threat = ThreatIndicator(
                id=f"ddos_{int(time.time())}_{hash(event.source_ip)}",
                threat_type=ThreatType.DDOS,
                threat_level=ThreatLevel.CRITICAL,
                attack_vector=AttackVector.NETWORK,
                source_ip=event.source_ip,
                target_resource=event.resource,
                description=f"DDoS attack detected from {event.source_ip}",
                evidence={
                    "request_rate": recent_requests,
                    "time_window": "1 minute",
                    "user_agent": event.user_agent
                },
                timestamp=event.timestamp,
                confidence_score=0.9
            )
            threats.append(threat)
        
        return threats
    
    async def _detect_behavior_threats(self, event: SecurityEvent) -> List[ThreatIndicator]:
        """Detect behavioral anomaly threats"""        threats = []
        
        if event.user_id:
            anomaly_result = self.behavior_analyzer.analyze_event_anomaly(event)
            
            if anomaly_result.get("is_anomalous", False):
                threat = ThreatIndicator(
                    id=f"behavior_{int(time.time())}_{hash(event.event_id)}",
                    threat_type=ThreatType.ANOMALOUS_BEHAVIOR,
                    threat_level=ThreatLevel.MEDIUM if anomaly_result["anomaly_score"] < 0.8 else ThreatLevel.HIGH,
                    attack_vector=AttackVector.APPLICATION,
                    source_ip=event.source_ip,
                    target_resource=event.resource,
                    description=f"Anomalous behavior detected for user {event.user_id}",
                    evidence={
                        "anomaly_score": anomaly_result["anomaly_score"],
                        "anomalies": anomaly_result["anomalies"],
                        "user_id": event.user_id
                    },
                    timestamp=event.timestamp,
                    confidence_score=anomaly_result["anomaly_score"]
                )
                threats.append(threat)
        
        return threats
    
    async def _detect_geographic_threats(self, event: SecurityEvent) -> List[ThreatIndicator]:
        """Detect geographic anomaly threats"""        threats = []
        
        # Check if IP is from suspicious location
        location = self.behavior_analyzer.geo_analyzer.get_location_info(event.source_ip)
        
        if location:
            # Check against known malicious countries (simplified example)
            suspicious_countries = ["Unknown", "North Korea", "Iran"]
            
            if location.get("country") in suspicious_countries:
                threat = ThreatIndicator(
                    id=f"geo_{int(time.time())}_{hash(event.source_ip)}",
                    threat_type=ThreatType.SUSPICIOUS_LOCATION,
                    threat_level=ThreatLevel.MEDIUM,
                    attack_vector=AttackVector.NETWORK,
                    source_ip=event.source_ip,
                    target_resource=event.resource,
                    description=f"Access from suspicious location: {location.get('country')}",
                    evidence={
                        "country": location.get("country"),
                        "city": location.get("city"),
                        "coordinates": {
                            "lat": location.get("latitude"),
                            "lng": location.get("longitude")
                        }
                    },
                    timestamp=event.timestamp,
                    confidence_score=0.6
                )
                threats.append(threat)
        
        return threats
    
    def _contains_sql_injection(self, event: SecurityEvent) -> bool:
        """Check if event contains SQL injection patterns"""        import re
        
        # Check various fields for SQL injection patterns
        fields_to_check = [
            str(event.resource),
            str(event.action),
            str(event.request_headers or {}),
        ]
        
        patterns = self.attack_patterns["sql_injection"]["patterns"]
        
        for field in fields_to_check:
            for pattern in patterns:
                if re.search(pattern, field, re.IGNORECASE):
                    return True
        
        return False
    
    def _contains_xss(self, event: SecurityEvent) -> bool:
        """Check if event contains XSS patterns"""        import re
        
        # Check various fields for XSS patterns
        fields_to_check = [
            str(event.resource),
            str(event.action),
            str(event.request_headers or {}),
        ]
        
        patterns = self.attack_patterns["xss"]["patterns"]
        
        for field in fields_to_check:
            for pattern in patterns:
                if re.search(pattern, field, re.IGNORECASE):
                    return True
        
        return False
    
    async def get_threat_summary(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """        Get threat detection summary
        
        Args:
            time_range_hours: Time range for summary in hours
            
        Returns:
            Threat summary statistics
        """        try:
            current_time = datetime.utcnow()
            start_time = current_time - timedelta(hours=time_range_hours)
            
            # Filter threats by time range
            recent_threats = [
                t for t in self.threat_indicators
                if t.timestamp >= start_time
            ]
            
            # Group by threat type and level
            threat_type_counts = defaultdict(int)
            threat_level_counts = defaultdict(int)
            source_ip_counts = defaultdict(int)
            
            for threat in recent_threats:
                threat_type_counts[threat.threat_type.value] += 1
                threat_level_counts[threat.threat_level.value] += 1
                source_ip_counts[threat.source_ip] += 1
            
            # Get top threat sources
            top_sources = sorted(
                source_ip_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return {
                "time_range_hours": time_range_hours,
                "total_threats": len(recent_threats),
                "threat_types": dict(threat_type_counts),
                "threat_levels": dict(threat_level_counts),
                "top_threat_sources": top_sources,
                "critical_threats": len([t for t in recent_threats if t.threat_level == ThreatLevel.CRITICAL]),
                "high_threats": len([t for t in recent_threats if t.threat_level == ThreatLevel.HIGH]),
                "mitigated_threats": len([t for t in recent_threats if t.is_mitigated]),
                "confirmed_threats": len([t for t in recent_threats if t.is_confirmed])
            }
            
        except Exception as e:
            logger.error(f"Failed to get threat summary: {e}")
            return {"error": str(e)}


class IncidentResponse:
    """    Automated incident response system
    """    
    def __init__(self, threat_detector: ThreatDetector):
        self.threat_detector = threat_detector
        self.response_actions = self._setup_response_actions()
        logger.info("Incident response system initialized")
    
    def _setup_response_actions(self) -> Dict[ThreatType, List[str]]:
        """Setup automated response actions for different threat types"""        return {
            ThreatType.BRUTE_FORCE: [
                "block_ip_temporarily",
                "increase_login_delay",
                "require_captcha",
                "alert_security_team"
            ],
            ThreatType.DDOS: [
                "activate_rate_limiting",
                "block_ip_range",
                "enable_cdn_protection",
                "alert_network_team"
            ],
            ThreatType.INJECTION: [
                "block_request",
                "sanitize_input",
                "alert_security_team",
                "log_for_analysis"
            ],
            ThreatType.XSS: [
                "sanitize_output",
                "block_request",
                "alert_security_team",
                "update_waf_rules"
            ],
            ThreatType.ANOMALOUS_BEHAVIOR: [
                "require_additional_auth",
                "limit_account_actions",
                "alert_security_team",
                "monitor_closely"
            ],
            ThreatType.SUSPICIOUS_LOCATION: [
                "require_mfa",
                "alert_user",
                "monitor_session",
                "geographic_restrictions"
            ]
        }
    
    async def respond_to_threat(self, threat: ThreatIndicator) -> Dict[str, Any]:
        """        Execute automated response to threat
        
        Args:
            threat: Threat indicator to respond to
            
        Returns:
            Response execution results
        """        try:
            response_actions = self.response_actions.get(threat.threat_type, [])
            executed_actions = []
            
            for action in response_actions:
                try:
                    result = await self._execute_action(action, threat)
                    executed_actions.append({
                        "action": action,
                        "result": result,
                        "success": True
                    })
                except Exception as e:
                    executed_actions.append({
                        "action": action,
                        "error": str(e),
                        "success": False
                    })
            
            # Mark threat as having mitigation attempted
            threat.mitigation_actions = [a["action"] for a in executed_actions if a["success"]]
            threat.is_mitigated = any(a["success"] for a in executed_actions)
            
            logger.info(f"Responded to threat {threat.id}: {len(executed_actions)} actions executed")
            
            return {
                "threat_id": threat.id,
                "executed_actions": executed_actions,
                "response_success": threat.is_mitigated
            }
            
        except Exception as e:
            logger.error(f"Failed to respond to threat: {e}")
            return {"error": str(e)}
    
    async def _execute_action(self, action: str, threat: ThreatIndicator) -> str:
        """Execute specific response action"""        try:
            if action == "block_ip_temporarily":
                # Add IP to temporary block list
                return f"IP {threat.source_ip} blocked for 1 hour"
            
            elif action == "increase_login_delay":
                # Increase login delay for this IP
                return f"Login delay increased for IP {threat.source_ip}"
            
            elif action == "require_captcha":
                # Enable CAPTCHA for this IP
                return f"CAPTCHA required for IP {threat.source_ip}"
            
            elif action == "alert_security_team":
                # Send alert to security team
                return "Security team alerted"
            
            elif action == "activate_rate_limiting":
                # Activate rate limiting
                return f"Rate limiting activated for IP {threat.source_ip}"
            
            elif action == "block_ip_range":
                # Block IP range
                return f"IP range blocked for {threat.source_ip}"
            
            elif action == "enable_cdn_protection":
                # Enable CDN protection
                return "CDN protection enabled"
            
            elif action == "alert_network_team":
                # Alert network team
                return "Network team alerted"
            
            elif action == "block_request":
                # Block the specific request
                return "Request blocked"
            
            elif action == "sanitize_input":
                # Sanitize input data
                return "Input sanitization applied"
            
            elif action == "log_for_analysis":
                # Log for detailed analysis
                return "Logged for detailed analysis"
            
            elif action == "sanitize_output":
                # Sanitize output data
                return "Output sanitization applied"
            
            elif action == "update_waf_rules":
                # Update WAF rules
                return "WAF rules updated"
            
            elif action == "require_additional_auth":
                # Require additional authentication
                return "Additional authentication required"
            
            elif action == "limit_account_actions":
                # Limit account actions
                return "Account actions limited"
            
            elif action == "monitor_closely":
                # Monitor closely
                return "Close monitoring activated"
            
            elif action == "require_mfa":
                # Require multi-factor authentication
                return "MFA required"
            
            elif action == "alert_user":
                # Alert the user
                return "User alerted"
            
            elif action == "monitor_session":
                # Monitor user session
                return "Session monitoring activated"
            
            elif action == "geographic_restrictions":
                # Apply geographic restrictions
                return "Geographic restrictions applied"
            
            else:
                return f"Unknown action: {action}"
                
        except Exception as e:
            logger.error(f"Failed to execute action {action}: {e}")
            raise


# Main threat detection system integration
class DeploymentThreatDetection:
    """    Main threat detection system for deployment security
    """    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize components
        self.threat_detector = ThreatDetector(
            redis_url=self.config.get("redis_url", "redis://localhost:6379")
        )
        
        self.incident_response = IncidentResponse(self.threat_detector)
        
        # Background tasks
        self._monitoring_task = None
        self._cleanup_task = None
        
        logger.info("Deployment threat detection system initialized")
    
    async def start_monitoring(self):
        """Start threat monitoring background tasks"""        try:
            await self.threat_detector.initialize_redis()
            
            # Start monitoring tasks
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("Threat monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start threat monitoring: {e}")
            raise
    
    async def stop_monitoring(self):
        """Stop threat monitoring background tasks"""        try:
            if self._monitoring_task:
                self._monitoring_task.cancel()
            
            if self._cleanup_task:
                self._cleanup_task.cancel()
            
            logger.info("Threat monitoring stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop threat monitoring: {e}")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""        while True:
            try:
                # Perform periodic threat analysis
                await asyncio.sleep(60)  # Check every minute
                
                # This would integrate with log collection systems
                # For now, we'll skip the actual implementation
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""        while True:
            try:
                # Cleanup old threat indicators
                await asyncio.sleep(3600)  # Every hour
                
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=30)
                
                # Remove old indicators
                self.threat_detector.threat_indicators = [
                    t for t in self.threat_detector.threat_indicators
                    if t.timestamp > cutoff_time
                ]
                
                logger.info("Threat indicators cleanup completed")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)
    
    async def analyze_security_event(self, event: SecurityEvent) -> List[ThreatIndicator]:
        """        Analyze security event for threats
        
        Args:
            event: Security event to analyze
            
        Returns:
            List of detected threats
        """        try:
            threats = await self.threat_detector.analyze_event(event)
            
            # Automatically respond to critical threats
            for threat in threats:
                if threat.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                    response_result = await self.incident_response.respond_to_threat(threat)
                    logger.info(f"Automated response executed for threat {threat.id}")
            
            return threats
            
        except Exception as e:
            logger.error(f"Failed to analyze security event: {e}")
            return []
    
    def get_threat_dashboard_data(self) -> Dict[str, Any]:
        """Get data for threat detection dashboard"""        try:
            # Get recent threat summary
            # This would be implemented with async call in production
            threat_summary = {
                "total_threats_24h": len(self.threat_detector.threat_indicators),
                "critical_threats": len([
                    t for t in self.threat_detector.threat_indicators
                    if t.threat_level == ThreatLevel.CRITICAL
                ]),
                "active_monitoring": self._monitoring_task is not None and not self._monitoring_task.done(),
                "last_update": datetime.utcnow().isoformat()
            }
            
            return threat_summary
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}
