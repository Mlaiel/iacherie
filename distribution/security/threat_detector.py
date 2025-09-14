"""
Security Module - Threat Detector
Advanced threat detection system for Ainflue Distribution Platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import redis.asyncio as redis
import httpx

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ThreatType(Enum):
    """Types of threats detected"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    DDOS_ATTACK = "ddos_attack"
    CREDENTIAL_STUFFING = "credential_stuffing"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    MALICIOUS_CONTENT = "malicious_content"
    RATE_LIMIT_ABUSE = "rate_limit_abuse"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"

@dataclass
class ThreatEvent:
    """Threat event data structure"""
    id: str
    threat_type: ThreatType
    level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    timestamp: datetime
    description: str
    indicators: Dict[str, Any]
    raw_data: Dict[str, Any]
    confidence: float  # 0.0 to 1.0
    automated_response: bool = False
    response_actions: List[str] = field(default_factory=list)

@dataclass
class ThreatPattern:
    """Threat detection pattern"""
    id: str
    name: str
    threat_type: ThreatType
    pattern: str  # Regex or rule
    confidence_threshold: float
    enabled: bool = True
    description: str = ""

class ThreatDetector:
    """
    Advanced threat detection system using machine learning and pattern matching
    Real-time threat detection with automated response capabilities
    """
    
    def __init__(self, redis_client -> None: redis.Redis) -> None:
        self.redis = redis_client
        self.threat_patterns = {}
        self.ml_models = {}
        self.threat_history = deque(maxlen=50000)
        self.ip_reputation_cache = {}
        self.behavior_baselines = {}
        self.running = False
        
        # Initialize threat patterns
        self._initialize_threat_patterns()
        
    async def start(self) -> None:
        """Start the threat detection system"""
        self.running = True
        logger.info("Starting threat detection system")
        
        # Load configurations
        await self._load_threat_patterns()
        await self._load_ml_models()
        await self._load_ip_reputation_data()
        
        # Start background tasks
        asyncio.create_task(self._update_behavior_baselines())
        asyncio.create_task(self._cleanup_old_data())
        
    async def stop(self) -> None:
        """Stop the threat detection system"""
        self.running = False
        logger.info("Stopping threat detection system")
    
    def _initialize_threat_patterns(self) -> None:
        """Initialize predefined threat detection patterns"""
        patterns = [
            ThreatPattern(
                id="sql_injection_basic",
                name="Basic SQL Injection",
                threat_type=ThreatType.SQL_INJECTION,
                pattern=r"(?i)(union\s+select|select\s+.*\s+from|insert\s+into|drop\s+table|';|\s+or\s+1=1)",
                confidence_threshold=0.8,
                description="Detects common SQL injection patterns"
            ),
            ThreatPattern(
                id="xss_basic",
                name="Basic XSS Attack",
                threat_type=ThreatType.XSS_ATTACK,
                pattern=r"(?i)(<script|javascript:|on\w+\s*=|<iframe|<object|<embed)",
                confidence_threshold=0.7,
                description="Detects common XSS attack patterns"
            ),
            ThreatPattern(
                id="brute_force_login",
                name="Brute Force Login",
                threat_type=ThreatType.BRUTE_FORCE,
                pattern=r"login_failed",
                confidence_threshold=0.9,
                description="Detects brute force login attempts"
            ),
            ThreatPattern(
                id="suspicious_user_agent",
                name="Suspicious User Agent",
                threat_type=ThreatType.SUSPICIOUS_ACTIVITY,
                pattern=r"(?i)(bot|crawler|scanner|sqlmap|nikto|acunetix|nessus)",
                confidence_threshold=0.6,
                description="Detects suspicious user agents"
            )
        ]
        
        for pattern in patterns:
            self.threat_patterns[pattern.id] = pattern
    
    async def analyze_request(self, request_data: Dict[str, Any]) -> List[ThreatEvent]:
        """
        Analyze incoming request for threats
        
        Args:
            request_data: Request information including IP, headers, payload, etc.
            
        Returns:
            List of detected threat events
        """
        threats = []
        
        # Extract request information
        source_ip = request_data.get('ip_address')
        user_agent = request_data.get('user_agent', '')
        payload = request_data.get('payload', '')
        headers = request_data.get('headers', {})
        user_id = request_data.get('user_id')
        endpoint = request_data.get('endpoint', '')
        
        # Pattern-based detection
        pattern_threats = await self._detect_pattern_threats(request_data)
        threats.extend(pattern_threats)
        
        # IP reputation check
        ip_threats = await self._check_ip_reputation(source_ip)
        threats.extend(ip_threats)
        
        # Behavioral analysis
        behavioral_threats = await self._analyze_behavior(request_data)
        threats.extend(behavioral_threats)
        
        # Rate-based detection
        rate_threats = await self._detect_rate_abuse(source_ip, user_id)
        threats.extend(rate_threats)
        
        # Content analysis
        content_threats = await self._analyze_content(payload, endpoint)
        threats.extend(content_threats)
        
        # Process detected threats
        for threat in threats:
            await self._process_threat(threat)
        
        return threats
    
    async def _detect_pattern_threats(self, request_data: Dict[str, Any]) -> List[ThreatEvent]:
        """Detect threats using pattern matching"""
        threats = []
        
        # Combine all text data for analysis
        text_data = ' '.join([
            str(request_data.get('payload', '')),
            str(request_data.get('user_agent', '')),
            str(request_data.get('referer', '')),
            ' '.join(request_data.get('headers', {}).values())
        ])
        
        for pattern in self.threat_patterns.values():
            if not pattern.enabled:
                continue
                
            matches = re.findall(pattern.pattern, text_data)
            if matches:
                confidence = min(len(matches) * 0.2 + 0.6, 1.0)
                
                if confidence >= pattern.confidence_threshold:
                    threat = ThreatEvent(
                        id=self._generate_threat_id(),
                        threat_type=pattern.threat_type,
                        level=self._calculate_threat_level(confidence),
                        source_ip=request_data.get('ip_address', 'unknown'),
                        user_id=request_data.get('user_id'),
                        timestamp=datetime.now(),
                        description=f"{pattern.name} detected",
                        indicators={
                            'pattern_id': pattern.id,
                            'matches': matches,
                            'match_count': len(matches)
                        },
                        raw_data=request_data,
                        confidence=confidence
                    )
                    threats.append(threat)
        
        return threats
    
    async def _check_ip_reputation(self, ip_address: str) -> List[ThreatEvent]:
        """Check IP address reputation"""
        if not ip_address or ip_address in ['127.0.0.1', 'localhost']:
            return []
        
        threats = []
        
        # Check cache first
        if ip_address in self.ip_reputation_cache:
            reputation = self.ip_reputation_cache[ip_address]
        else:
            reputation = await self._get_ip_reputation(ip_address)
            self.ip_reputation_cache[ip_address] = reputation
        
        if reputation['malicious']:
            threat = ThreatEvent(
                id=self._generate_threat_id(),
                threat_type=ThreatType.SUSPICIOUS_ACTIVITY,
                level=ThreatLevel.HIGH,
                source_ip=ip_address,
                user_id=None,
                timestamp=datetime.now(),
                description=f"Malicious IP detected: {ip_address}",
                indicators={
                    'reputation_score': reputation['score'],
                    'threat_categories': reputation['categories'],
                    'last_seen': reputation['last_seen']
                },
                raw_data={'ip_address': ip_address},
                confidence=reputation['confidence']
            )
            threats.append(threat)
        
        return threats
    
    async def _get_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """Get IP reputation from external services or local database"""
        # Check local blacklist first
        blacklist_key = f"ip_blacklist:{ip_address}"
        is_blacklisted = await self.redis.exists(blacklist_key)
        
        if is_blacklisted:
            return {
                'malicious': True,
                'score': 1.0,
                'categories': ['blacklisted'],
                'last_seen': datetime.now().isoformat(),
                'confidence': 1.0
            }
        
        # Check threat intelligence feeds (mock implementation)
        # In production, this would query real threat intelligence APIs
        reputation = {
            'malicious': False,
            'score': 0.0,
            'categories': [],
            'last_seen': None,
            'confidence': 0.5
        }
        
        # Simulate checking against known malicious patterns
        suspicious_patterns = ['192.168.1.', '10.0.0.', '172.16.']
        for pattern in suspicious_patterns:
            if ip_address.startswith(pattern):
                # These are actually private IPs, but for demo purposes
                reputation['score'] = 0.1
                break
        
        return reputation
    
    async def _analyze_behavior(self, request_data: Dict[str, Any]) -> List[ThreatEvent]:
        """Analyze behavioral patterns for anomalies"""
        threats = []
        
        user_id = request_data.get('user_id')
        ip_address = request_data.get('ip_address')
        
        if not user_id and not ip_address:
            return threats
        
        # Analyze request frequency
        frequency_threat = await self._analyze_request_frequency(request_data)
        if frequency_threat:
            threats.append(frequency_threat)
        
        # Analyze geographic anomalies
        geo_threat = await self._analyze_geographic_anomaly(request_data)
        if geo_threat:
            threats.append(geo_threat)
        
        # Analyze time-based anomalies
        time_threat = await self._analyze_time_anomaly(request_data)
        if time_threat:
            threats.append(time_threat)
        
        return threats
    
    async def _analyze_request_frequency(self, request_data: Dict[str, Any]) -> Optional[ThreatEvent]:
        """Analyze request frequency for anomalies"""
        identifier = request_data.get('user_id') or request_data.get('ip_address')
        if not identifier:
            return None
        
        # Track request frequency
        freq_key = f"request_freq:{identifier}"
        current_time = int(datetime.now().timestamp() // 60)  # Per minute
        
        pipe = self.redis.pipeline()
        pipe.incr(f"{freq_key}:{current_time}")
        pipe.expire(f"{freq_key}:{current_time}", 60)
        results = await pipe.execute()
        
        request_count = results[0]
        
        # Get baseline for comparison
        baseline = await self._get_request_baseline(identifier)
        
        # Detect anomaly
        if request_count > baseline * 5:  # 5x normal rate
            return ThreatEvent(
                id=self._generate_threat_id(),
                threat_type=ThreatType.ANOMALOUS_BEHAVIOR,
                level=ThreatLevel.MEDIUM,
                source_ip=request_data.get('ip_address', 'unknown'),
                user_id=request_data.get('user_id'),
                timestamp=datetime.now(),
                description="Abnormal request frequency detected",
                indicators={
                    'current_rate': request_count,
                    'baseline_rate': baseline,
                    'anomaly_factor': request_count / baseline if baseline > 0 else float('inf')
                },
                raw_data=request_data,
                confidence=min(request_count / baseline / 5, 1.0) if baseline > 0 else 1.0
            )
        
        return None
    
    async def _get_request_baseline(self, identifier: str) -> float:
        """Get request baseline for identifier"""
        baseline_key = f"baseline:{identifier}"
        baseline_data = await self.redis.get(baseline_key)
        
        if baseline_data:
            return float(baseline_data)
        
        # Calculate baseline from historical data
        history_key = f"request_history:{identifier}"
        history = await self.redis.lrange(history_key, 0, 100)
        
        if history:
            values = [float(val) for val in history]
            baseline = np.mean(values)
        else:
            baseline = 10.0  # Default baseline
        
        # Cache baseline
        await self.redis.setex(baseline_key, 3600, baseline)
        
        return baseline
    
    async def _analyze_geographic_anomaly(self, request_data: Dict[str, Any]) -> Optional[ThreatEvent]:
        """Analyze geographic location anomalies"""
        # This would typically use GeoIP services
        # For demo purposes, we'll simulate geographic analysis
        
        user_id = request_data.get('user_id')
        ip_address = request_data.get('ip_address')
        
        if not user_id or not ip_address:
            return None
        
        # Mock geographic analysis
        # In production, you'd use MaxMind or similar GeoIP service
        current_location = "US"  # Mock location
        
        # Get user's typical locations
        locations_key = f"user_locations:{user_id}"
        typical_locations = await self.redis.smembers(locations_key)
        typical_locations = {loc.decode() for loc in typical_locations}
        
        if typical_locations and current_location not in typical_locations:
            return ThreatEvent(
                id=self._generate_threat_id(),
                threat_type=ThreatType.SUSPICIOUS_ACTIVITY,
                level=ThreatLevel.MEDIUM,
                source_ip=ip_address,
                user_id=user_id,
                timestamp=datetime.now(),
                description=f"Access from unusual location: {current_location}",
                indicators={
                    'current_location': current_location,
                    'typical_locations': list(typical_locations),
                    'new_location': True
                },
                raw_data=request_data,
                confidence=0.7
            )
        
        # Add current location to typical locations
        await self.redis.sadd(locations_key, current_location)
        await self.redis.expire(locations_key, 86400 * 30)  # Keep for 30 days
        
        return None
    
    async def _analyze_time_anomaly(self, request_data: Dict[str, Any]) -> Optional[ThreatEvent]:
        """Analyze time-based access patterns"""
        user_id = request_data.get('user_id')
        if not user_id:
            return None
        
        current_hour = datetime.now().hour
        
        # Track user's typical access hours
        hours_key = f"user_hours:{user_id}"
        hour_counts = await self.redis.hgetall(hours_key)
        
        # Convert to integers
        hour_counts = {int(k): int(v) for k, v in hour_counts.items()}
        
        # Increment current hour
        await self.redis.hincrby(hours_key, current_hour, 1)
        await self.redis.expire(hours_key, 86400 * 30)  # Keep for 30 days
        
        # Analyze if this is an unusual time
        if hour_counts:
            total_accesses = sum(hour_counts.values())
            current_hour_percentage = hour_counts.get(current_hour, 0) / total_accesses
            
            # If user has never accessed at this hour and has significant history
            if current_hour_percentage == 0 and total_accesses > 100:
                return ThreatEvent(
                    id=self._generate_threat_id(),
                    threat_type=ThreatType.ANOMALOUS_BEHAVIOR,
                    level=ThreatLevel.LOW,
                    source_ip=request_data.get('ip_address', 'unknown'),
                    user_id=user_id,
                    timestamp=datetime.now(),
                    description=f"Access at unusual time: {current_hour}:00",
                    indicators={
                        'access_hour': current_hour,
                        'typical_hours': [h for h, c in hour_counts.items() if c > 0],
                        'total_historical_accesses': total_accesses
                    },
                    raw_data=request_data,
                    confidence=0.5
                )
        
        return None
    
    async def _detect_rate_abuse(self, ip_address: str, user_id: Optional[str]) -> List[ThreatEvent]:
        """Detect rate limit abuse"""
        threats = []
        
        # Check for rapid requests from IP
        if ip_address:
            ip_threat = await self._check_rapid_requests(ip_address, 'ip')
            if ip_threat:
                threats.append(ip_threat)
        
        # Check for rapid requests from user
        if user_id:
            user_threat = await self._check_rapid_requests(user_id, 'user')
            if user_threat:
                threats.append(user_threat)
        
        return threats
    
    async def _check_rapid_requests(self, identifier: str, identifier_type: str) -> Optional[ThreatEvent]:
        """Check for rapid requests from identifier"""
        rate_key = f"rapid_requests:{identifier_type}:{identifier}"
        current_time = int(datetime.now().timestamp())
        
        # Count requests in last 10 seconds
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(rate_key, 0, current_time - 10)
        pipe.zadd(rate_key, {str(current_time): current_time})
        pipe.zcard(rate_key)
        pipe.expire(rate_key, 60)
        results = await pipe.execute()
        
        request_count = results[2]
        
        # Threshold: more than 50 requests in 10 seconds
        if request_count > 50:
            return ThreatEvent(
                id=self._generate_threat_id(),
                threat_type=ThreatType.RATE_LIMIT_ABUSE,
                level=ThreatLevel.HIGH,
                source_ip=identifier if identifier_type == 'ip' else 'unknown',
                user_id=identifier if identifier_type == 'user' else None,
                timestamp=datetime.now(),
                description=f"Rapid requests detected from {identifier_type}: {identifier}",
                indicators={
                    'request_count': request_count,
                    'time_window': 10,
                    'identifier_type': identifier_type,
                    'identifier': identifier
                },
                raw_data={'identifier': identifier, 'type': identifier_type},
                confidence=min(request_count / 50, 1.0)
            )
        
        return None
    
    async def _analyze_content(self, payload: str, endpoint: str) -> List[ThreatEvent]:
        """Analyze request content for threats"""
        threats = []
        
        if not payload:
            return threats
        
        # Check for malicious content patterns
        malicious_patterns = [
            (r'(?i)(eval\s*\(|exec\s*\(|system\s*\()', ThreatType.MALICIOUS_CONTENT, 0.8),
            (r'(?i)(base64_decode|gzinflate|str_rot13)', ThreatType.MALICIOUS_CONTENT, 0.7),
            (r'(?i)(cmd\.exe|/bin/sh|powershell)', ThreatType.MALICIOUS_CONTENT, 0.9),
            (r'(?i)(wget|curl|nc\s+-l)', ThreatType.MALICIOUS_CONTENT, 0.8)
        ]
        
        for pattern, threat_type, confidence in malicious_patterns:
            matches = re.findall(pattern, payload)
            if matches:
                threat = ThreatEvent(
                    id=self._generate_threat_id(),
                    threat_type=threat_type,
                    level=self._calculate_threat_level(confidence),
                    source_ip='unknown',
                    user_id=None,
                    timestamp=datetime.now(),
                    description=f"Malicious content detected in {endpoint}",
                    indicators={
                        'pattern': pattern,
                        'matches': matches,
                        'endpoint': endpoint
                    },
                    raw_data={'payload': payload, 'endpoint': endpoint},
                    confidence=confidence
                )
                threats.append(threat)
        
        return threats
    
    async def _process_threat(self, threat -> None: ThreatEvent) -> None:
        """Process detected threat"""
        # Store threat
        await self._store_threat(threat)
        
        # Add to history
        self.threat_history.append(threat)
        
        # Determine if automated response is needed
        if threat.level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
            await self._trigger_automated_response(threat)
        
        # Log threat
        logger.warning(f"Threat detected: {threat.description} [{threat.level.value}] from {threat.source_ip}")
    
    async def _store_threat(self, threat -> None: ThreatEvent) -> None:
        """Store threat in Redis"""
        threat_data = {
            'id': threat.id,
            'threat_type': threat.threat_type.value,
            'level': threat.level.value,
            'source_ip': threat.source_ip,
            'user_id': threat.user_id,
            'timestamp': threat.timestamp.isoformat(),
            'description': threat.description,
            'indicators': threat.indicators,
            'confidence': threat.confidence,
            'automated_response': threat.automated_response,
            'response_actions': threat.response_actions
        }
        
        # Store in daily threat log
        date_key = f"threats:{datetime.now().strftime('%Y-%m-%d')}"
        await self.redis.lpush(date_key, json.dumps(threat_data))
        await self.redis.expire(date_key, 86400 * 30)  # Keep for 30 days
        
        # Store in active threats if high severity
        if threat.level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
            await self.redis.hset("active_threats", threat.id, json.dumps(threat_data))
    
    async def _trigger_automated_response(self, threat -> None: ThreatEvent) -> None:
        """Trigger automated response to threat"""
        actions = []
        
        if threat.threat_type == ThreatType.BRUTE_FORCE:
            # Block IP temporarily
            await self._block_ip(threat.source_ip, duration=3600)
            actions.append(f"Blocked IP {threat.source_ip} for 1 hour")
        
        elif threat.threat_type == ThreatType.RATE_LIMIT_ABUSE:
            # Apply stricter rate limits
            await self._apply_strict_rate_limits(threat.source_ip)
            actions.append(f"Applied strict rate limits to {threat.source_ip}")
        
        elif threat.threat_type == ThreatType.SQL_INJECTION:
            # Block IP and alert security team
            await self._block_ip(threat.source_ip, duration=7200)
            await self._alert_security_team(threat)
            actions.append(f"Blocked IP {threat.source_ip} for 2 hours and alerted security")
        
        elif threat.threat_type == ThreatType.MALICIOUS_CONTENT:
            # Quarantine content and block user
            if threat.user_id:
                await self._quarantine_user(threat.user_id)
                actions.append(f"Quarantined user {threat.user_id}")
        
        threat.automated_response = True
        threat.response_actions = actions
    
    async def _block_ip(self, ip_address -> None: str, duration -> None: int) -> None:
        """Block IP address"""
        block_key = f"ip_blocked:{ip_address}"
        await self.redis.setex(block_key, duration, "1")
        logger.info(f"Blocked IP {ip_address} for {duration} seconds")
    
    async def _apply_strict_rate_limits(self, ip_address -> None: str) -> None:
        """Apply stricter rate limits to IP"""
        limit_key = f"strict_limits:{ip_address}"
        await self.redis.setex(limit_key, 3600, "1")
        logger.info(f"Applied strict rate limits to {ip_address}")
    
    async def _alert_security_team(self, threat -> None: ThreatEvent) -> None:
        """Alert security team about critical threat"""
        # This would integrate with your alerting system
        logger.critical(f"SECURITY ALERT: {threat.description} from {threat.source_ip}")
    
    async def _quarantine_user(self, user_id -> None: str) -> None:
        """Quarantine user account"""
        quarantine_key = f"user_quarantined:{user_id}"
        await self.redis.setex(quarantine_key, 86400, "1")
        logger.warning(f"Quarantined user {user_id}")
    
    def _generate_threat_id(self) -> str:
        """Generate unique threat ID"""
        timestamp = str(int(datetime.now().timestamp() * 1000))
        return f"threat_{timestamp}_{hashlib.md5(timestamp.encode()).hexdigest()[:8]}"
    
    def _calculate_threat_level(self, confidence: float) -> ThreatLevel:
        """Calculate threat level based on confidence"""
        if confidence >= 0.9:
            return ThreatLevel.CRITICAL
        elif confidence >= 0.7:
            return ThreatLevel.HIGH
        elif confidence >= 0.5:
            return ThreatLevel.MEDIUM
        elif confidence >= 0.3:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.INFO
    
    async def _update_behavior_baselines(self) -> None:
        """Background task to update behavioral baselines"""
        while self.running:
            try:
                # Update baselines every hour
                await asyncio.sleep(3600)
                
                # This would update ML models and baselines
                logger.debug("Updating behavioral baselines")
                
            except Exception as e:
                logger.error(f"Error updating baselines: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """Background task to cleanup old data"""
        while self.running:
            try:
                # Cleanup every 6 hours
                await asyncio.sleep(21600)
                
                # Remove old active threats
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                active_threats = await self.redis.hgetall("active_threats")
                for threat_id, threat_data in active_threats.items():
                    try:
                        data = json.loads(threat_data)
                        threat_time = datetime.fromisoformat(data['timestamp'])
                        
                        if threat_time < cutoff_time:
                            await self.redis.hdel("active_threats", threat_id)
                    except Exception:
                        continue
                
                logger.debug("Cleaned up old threat data")
                
            except Exception as e:
                logger.error(f"Error cleaning up data: {e}")
    
    # Query methods
    
    async def get_active_threats(self, level: Optional[ThreatLevel] = None) -> List[Dict[str, Any]]:
        """Get active threats"""
        threats_data = await self.redis.hgetall("active_threats")
        threats = []
        
        for threat_id, threat_json in threats_data.items():
            try:
                threat_data = json.loads(threat_json)
                if level is None or threat_data['level'] == level.value:
                    threats.append(threat_data)
            except Exception:
                continue
        
        return sorted(threats, key=lambda t: t['timestamp'], reverse=True)
    
    async def get_threat_stats(self) -> Dict[str, Any]:
        """Get threat detection statistics"""
        # Count threats by type and level
        threats_by_type = defaultdict(int)
        threats_by_level = defaultdict(int)
        
        for threat in self.threat_history:
            threats_by_type[threat.threat_type.value] += 1
            threats_by_level[threat.level.value] += 1
        
        return {
            'total_threats_detected': len(self.threat_history),
            'active_threats': await self.redis.hlen("active_threats"),
            'threats_by_type': dict(threats_by_type),
            'threats_by_level': dict(threats_by_level),
            'patterns_enabled': sum(1 for p in self.threat_patterns.values() if p.enabled),
            'cache_size': len(self.ip_reputation_cache)
        }