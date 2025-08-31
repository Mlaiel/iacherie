"""
Security Monitor for IA Influencer Agent Platform
================================================

Advanced security monitoring system with real-time threat detection,
behavioral analysis, and automated response for content protection platform.

Security Focus Areas:
- Content protection system security
- API security and rate limiting monitoring
- User authentication and authorization tracking
- Data privacy and GDPR compliance monitoring
- Platform integration security assessment
- AI model security and adversarial attack detection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use, distribution, or modification prohibited
"""

import asyncio
import logging
import hashlib
import ipaddress
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import re
import aioredis
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from collections import defaultdict, deque
import geoip2.database
import user_agents

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class SecurityEventType(Enum):
    """Types of security events"""
    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_VIOLATION = "authorization_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_API_USAGE = "suspicious_api_usage"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    CONTENT_THEFT_ATTEMPT = "content_theft_attempt"
    AI_MODEL_ATTACK = "ai_model_attack"
    PRIVACY_VIOLATION = "privacy_violation"
    PLATFORM_INTEGRATION_BREACH = "platform_integration_breach"
    UNUSUAL_TRAFFIC_PATTERN = "unusual_traffic_pattern"


@dataclass
class SecurityEvent:
    """Security event data structure"""
    id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    false_positive: bool = False


@dataclass
class ThreatPattern:
    """Threat pattern definition"""
    name: str
    pattern_type: str
    indicators: List[str]
    threshold: int
    time_window: int  # seconds
    threat_level: ThreatLevel
    auto_block: bool = False


@dataclass
class SecurityMetrics:
    """Security monitoring metrics"""
    total_events: int
    events_by_type: Dict[SecurityEventType, int]
    events_by_threat_level: Dict[ThreatLevel, int]
    blocked_ips: int
    suspicious_users: int
    false_positives: int
    response_time_avg: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class SecurityMonitor:
    """
    Advanced security monitoring system with real-time threat detection
    and automated response capabilities.
    """
    
    def __init__(
        self,
        redis_client: Optional[aioredis.Redis] = None,
        db_engine: Optional[AsyncEngine] = None,
        monitoring_interval: int = 60,
        retention_days: int = 90
    ):
        self.redis_client = redis_client
        self.db_engine = db_engine
        self.monitoring_interval = monitoring_interval
        self.retention_days = retention_days
        
        # Security state
        self._running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Threat detection
        self._threat_patterns: Dict[str, ThreatPattern] = {}
        self._event_counters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._blocked_ips: Set[str] = set()
        self._suspicious_users: Set[str] = set()
        
        # Rate limiting
        self._rate_limits: Dict[str, Dict[str, int]] = defaultdict(dict)
        self._rate_limit_windows: Dict[str, Dict[str, datetime]] = defaultdict(dict)
        
        # Security analytics
        self._security_metrics: deque = deque(maxlen=1440)  # 24 hours of minutes
        self._behavioral_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Geolocation database (optional)
        self._geoip_db: Optional[Any] = None
        
        # Initialize threat patterns
        self._initialize_threat_patterns()
        
        logger.info("Security Monitor initialized")
        
    async def start(self):
        """Start security monitoring"""
        if self._running:
            logger.warning("Security monitor already running")
            return
            
        try:
            self._running = True
            
            # Load security data
            await self._load_security_data()
            
            # Start monitoring task
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("Security monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start security monitor: {e}")
            self._running = False
            raise
            
    async def stop(self):
        """Stop security monitoring"""
        self._running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
                
        # Save security data
        await self._save_security_data()
        
        logger.info("Security monitoring stopped")
        
    def _initialize_threat_patterns(self):
        """Initialize built-in threat patterns"""
        
        # Authentication failure pattern
        self._threat_patterns["auth_failure_burst"] = ThreatPattern(
            name="Authentication Failure Burst",
            pattern_type="frequency",
            indicators=["authentication_failure"],
            threshold=5,
            time_window=300,  # 5 minutes
            threat_level=ThreatLevel.MEDIUM,
            auto_block=True
        )
        
        # Rate limit violation pattern
        self._threat_patterns["rate_limit_violation"] = ThreatPattern(
            name="Rate Limit Violation",
            pattern_type="frequency",
            indicators=["rate_limit_exceeded"],
            threshold=3,
            time_window=600,  # 10 minutes
            threat_level=ThreatLevel.HIGH,
            auto_block=True
        )
        
        # Content theft pattern
        self._threat_patterns["content_theft_attempt"] = ThreatPattern(
            name="Content Theft Attempt",
            pattern_type="behavioral",
            indicators=["bulk_download", "scraping_detected", "api_abuse"],
            threshold=1,
            time_window=3600,  # 1 hour
            threat_level=ThreatLevel.CRITICAL,
            auto_block=True
        )
        
        # AI model attack pattern
        self._threat_patterns["ai_model_attack"] = ThreatPattern(
            name="AI Model Attack",
            pattern_type="adversarial",
            indicators=["adversarial_input", "model_probing", "extraction_attempt"],
            threshold=1,
            time_window=1800,  # 30 minutes
            threat_level=ThreatLevel.CRITICAL,
            auto_block=True
        )
        
        # Unusual traffic pattern
        self._threat_patterns["unusual_traffic"] = ThreatPattern(
            name="Unusual Traffic Pattern",
            pattern_type="anomaly",
            indicators=["traffic_spike", "geographic_anomaly", "user_agent_anomaly"],
            threshold=2,
            time_window=1800,  # 30 minutes
            threat_level=ThreatLevel.MEDIUM,
            auto_block=False
        )
        
    async def _monitoring_loop(self):
        """Main security monitoring loop"""
        
        while self._running:
            try:
                # Analyze security events
                await self._analyze_security_events()
                
                # Check threat patterns
                await self._check_threat_patterns()
                
                # Update behavioral profiles
                await self._update_behavioral_profiles()
                
                # Monitor rate limits
                await self._monitor_rate_limits()
                
                # Collect security metrics
                await self._collect_security_metrics()
                
                # Cleanup old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in security monitoring loop: {e}")
                await asyncio.sleep(30)  # Backoff on error
                
    async def analyze_security_event(self, event_data: Dict[str, Any]):
        """Analyze a security event in real-time"""



        
        try:
            # Extract event information
            event_type = SecurityEventType(event_data.get('type', 'unusual_traffic_pattern'))
            source_ip = event_data.get('source_ip', 'unknown')
            user_id = event_data.get('user_id')
            timestamp = datetime.utcnow()
            
            # Determine threat level
            threat_level = self._assess_threat_level(event_type, event_data)
            
            # Create security event
            security_event = SecurityEvent(
                id=hashlib.md5(f"{event_type.value}{source_ip}{timestamp}".encode()).hexdigest(),
                event_type=event_type,
                threat_level=threat_level,
                source_ip=source_ip,
                user_id=user_id,
                description=event_data.get('description', 'Security event detected'),
                details=event_data
            )
            
            # Store event
            await self._store_security_event(security_event)
            
            # Check for immediate response
            if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL, ThreatLevel.EMERGENCY]:
                await self._immediate_response(security_event)
                
            # Update counters
            self._event_counters[f"{event_type.value}_{source_ip}"].append(timestamp)
            
            # Check behavioral patterns
            await self._check_behavioral_anomaly(security_event)
            
            logger.info(f"Security event analyzed: {event_type.value} from {source_ip}")
            
        except Exception as e:
            logger.error(f"Error analyzing security event: {e}")
            
    def _assess_threat_level(self, event_type: SecurityEventType, event_data: Dict[str, Any]) -> ThreatLevel:
        """Assess threat level based on event type and context"""
        
        base_threat_levels = {
            SecurityEventType.AUTHENTICATION_FAILURE: ThreatLevel.LOW,
            SecurityEventType.AUTHORIZATION_VIOLATION: ThreatLevel.MEDIUM,
            SecurityEventType.RATE_LIMIT_EXCEEDED: ThreatLevel.MEDIUM,
            SecurityEventType.SUSPICIOUS_API_USAGE: ThreatLevel.MEDIUM,
            SecurityEventType.DATA_BREACH_ATTEMPT: ThreatLevel.CRITICAL,
            SecurityEventType.CONTENT_THEFT_ATTEMPT: ThreatLevel.HIGH,
            SecurityEventType.AI_MODEL_ATTACK: ThreatLevel.CRITICAL,
            SecurityEventType.PRIVACY_VIOLATION: ThreatLevel.HIGH,
            SecurityEventType.PLATFORM_INTEGRATION_BREACH: ThreatLevel.CRITICAL,
            SecurityEventType.UNUSUAL_TRAFFIC_PATTERN: ThreatLevel.LOW
        }
        
        base_level = base_threat_levels.get(event_type, ThreatLevel.MEDIUM)
        
        # Escalate based on context
        escalation_factors = [
            event_data.get('repeated_offender', False),
            event_data.get('sensitive_data_involved', False),
            event_data.get('high_value_target', False),
            event_data.get('automated_attack', False)
        ]
        
        escalation_count = sum(escalation_factors)
        
        if escalation_count >= 3:
            return ThreatLevel.EMERGENCY
        elif escalation_count >= 2:
            return ThreatLevel.CRITICAL
        elif escalation_count >= 1:
            # Escalate one level
            levels = list(ThreatLevel)
            current_index = levels.index(base_level)
            return levels[min(current_index + 1, len(levels) - 1)]
            
        return base_level
        
    async def _immediate_response(self, event: SecurityEvent):
        """Implement immediate response to high-threat events"""



        
        try:
            # Block IP if auto-block is enabled
            if event.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.EMERGENCY]:
                await self._block_ip(event.source_ip, reason=f"High threat event: {event.event_type.value}")
                
            # Disable user account if necessary
            if event.user_id and event.event_type in [
                SecurityEventType.DATA_BREACH_ATTEMPT,
                SecurityEventType.CONTENT_THEFT_ATTEMPT,
                SecurityEventType.AI_MODEL_ATTACK
            ]:
                await self._suspend_user(event.user_id, reason=f"Security violation: {event.event_type.value}")
                
            # Send immediate alert
            await self._send_security_alert(event)
            
            logger.warning(f"Immediate response triggered for event: {event.id}")
            
        except Exception as e:
            logger.error(f"Error in immediate response: {e}")
            
    async def _block_ip(self, ip_address: str, reason: str, duration: Optional[int] = None):
        """Block an IP address"""



        
        try:
            self._blocked_ips.add(ip_address)
            
            # Store in Redis with TTL
            if self.redis_client:
                ttl = duration or 3600  # 1 hour default
                await self.redis_client.setex(
                    f"security:blocked_ip:{ip_address}",
                    ttl,
                    json.dumps({
                        'reason': reason,
                        'blocked_at': datetime.utcnow().isoformat(),
                        'duration': ttl
                    })
                )
                
            # Store in database
            if self.db_engine:
                async with self.db_engine.begin() as conn:
                    await conn.execute(text("""
                        INSERT INTO security_ip_blocks (ip_address, reason, blocked_at, expires_at)
                        VALUES (:ip, :reason, :blocked_at, :expires_at)
                    """), {
                        'ip': ip_address,
                        'reason': reason,
                        'blocked_at': datetime.utcnow(),
                        'expires_at': datetime.utcnow() + timedelta(seconds=duration or 3600)
                    })
                    
            logger.warning(f"IP address blocked: {ip_address} - {reason}")
            
        except Exception as e:
            logger.error(f"Error blocking IP {ip_address}: {e}")
            
    async def _suspend_user(self, user_id: str, reason: str, duration: Optional[int] = None):
        """Suspend a user account"""



        
        try:
            self._suspicious_users.add(user_id)
            
            # Store in Redis
            if self.redis_client:
                ttl = duration or 86400  # 24 hours default
                await self.redis_client.setex(
                    f"security:suspended_user:{user_id}",
                    ttl,
                    json.dumps({
                        'reason': reason,
                        'suspended_at': datetime.utcnow().isoformat(),
                        'duration': ttl
                    })
                )
                
            # Update user status in database
            if self.db_engine:
                async with self.db_engine.begin() as conn:
                    await conn.execute(text("""
                        UPDATE users 
                        SET status = 'suspended', 
                            suspended_reason = :reason,
                            suspended_at = :suspended_at
                        WHERE id = :user_id
                    """), {
                        'user_id': user_id,
                        'reason': reason,
                        'suspended_at': datetime.utcnow()
                    })
                    
            logger.warning(f"User suspended: {user_id} - {reason}")
            
        except Exception as e:
            logger.error(f"Error suspending user {user_id}: {e}")
            
    async def _send_security_alert(self, event: SecurityEvent):
        """Send security alert to administrators"""



        
        try:
            alert_data = {
                'type': 'security_alert',
                'event_id': event.id,
                'event_type': event.event_type.value,
                'threat_level': event.threat_level.value,
                'source_ip': event.source_ip,
                'user_id': event.user_id,
                'description': event.description,
                'timestamp': event.timestamp.isoformat()
            }
            
            # Store alert in Redis for dashboard
            if self.redis_client:
                await self.redis_client.lpush(
                    "security:alerts",
                    json.dumps(alert_data)
                )
                await self.redis_client.ltrim("security:alerts", 0, 999)  # Keep last 1000
                
            # Send to external alert systems (webhook, email, etc.)
            await self._send_external_alert(alert_data)
            
        except Exception as e:
            logger.error(f"Error sending security alert: {e}")
            
    async def _send_external_alert(self, alert_data: Dict[str, Any]):
        """Send alert to external systems"""
        
        # Implementation for external alerting
        # This could include webhooks, email, Slack, PagerDuty, etc.
        logger.info(f"External security alert: {alert_data['event_type']}")
        
    async def _analyze_security_events(self):
        """Analyze recent security events for patterns"""
        
        if not self.db_engine:
            return
            
        try:
            async with self.db_engine.begin() as conn:
                # Analyze events from last hour
                result = await conn.execute(text("""
                    SELECT event_type, source_ip, user_id, COUNT(*) as count
                    FROM security_events 
                    WHERE timestamp > NOW() - INTERVAL '1 hour'
                    GROUP BY event_type, source_ip, user_id
                    HAVING COUNT(*) > 1
                """))
                
                for row in result:
                    event_type, source_ip, user_id, count = row
                    
                    # Check if this indicates a pattern
                    if count >= 5:  # Threshold for suspicious activity
                        await self.analyze_security_event({
                            'type': 'suspicious_api_usage',
                            'source_ip': source_ip,
                            'user_id': user_id,
                            'description': f"Repeated {event_type} events ({count} times)",
                            'repeated_offender': True,
                            'automated_attack': count >= 10
                        })
                        
        except Exception as e:
            logger.error(f"Error analyzing security events: {e}")
            
    async def _check_threat_patterns(self):
        """Check for known threat patterns"""



        
        try:
            current_time = datetime.utcnow()
            
            for pattern_name, pattern in self._threat_patterns.items():
                # Check events within time window
                for event_key, event_times in self._event_counters.items():
                    if any(indicator in event_key for indicator in pattern.indicators):
                        # Count events within time window
                        window_start = current_time - timedelta(seconds=pattern.time_window)
                        recent_events = [t for t in event_times if t >= window_start]
                        
                        if len(recent_events) >= pattern.threshold:
                            # Pattern detected
                            source_ip = event_key.split('_')[-1] if '_' in event_key else 'unknown'
                            
                            await self.analyze_security_event({
                                'type': 'unusual_traffic_pattern',
                                'source_ip': source_ip,
                                'description': f"Threat pattern detected: {pattern.name}",
                                'pattern_name': pattern_name,
                                'event_count': len(recent_events),
                                'time_window': pattern.time_window,
                                'automated_attack': True
                            })
                            
                            # Auto-block if enabled
                            if pattern.auto_block:
                                await self._block_ip(
                                    source_ip, 
                                    reason=f"Threat pattern: {pattern.name}",
                                    duration=3600
                                )
                                
        except Exception as e:
            logger.error(f"Error checking threat patterns: {e}")
            
    async def _update_behavioral_profiles(self):
        """Update user behavioral profiles"""
        
        if not self.db_engine:
            return
            
        try:
            async with self.db_engine.begin() as conn:
                # Analyze user behavior patterns
                result = await conn.execute(text("""
                    SELECT 
                        user_id,
                        source_ip,
                        user_agent,
                        COUNT(*) as request_count,
                        COUNT(DISTINCT source_ip) as ip_count,
                        MIN(timestamp) as first_seen,
                        MAX(timestamp) as last_seen
                    FROM access_logs 
                    WHERE timestamp > NOW() - INTERVAL '24 hours'
                        AND user_id IS NOT NULL
                    GROUP BY user_id, source_ip, user_agent
                """))
                
                for row in result:
                    user_id, source_ip, user_agent, request_count, ip_count, first_seen, last_seen = row
                    
                    # Update behavioral profile
                    if user_id not in self._behavioral_profiles:
                        self._behavioral_profiles[user_id] = {
                            'typical_ips': set(),
                            'typical_user_agents': set(),
                            'request_patterns': [],
                            'last_updated': datetime.utcnow()
                        }
                        
                    profile = self._behavioral_profiles[user_id]
                    profile['typical_ips'].add(source_ip)
                    profile['typical_user_agents'].add(user_agent)
                    profile['last_updated'] = datetime.utcnow()
                    
                    # Check for anomalies
                    if ip_count > 5:  # User from many IPs
                        await self.analyze_security_event({
                            'type': 'unusual_traffic_pattern',
                            'source_ip': source_ip,
                            'user_id': user_id,
                            'description': f"User accessing from {ip_count} different IPs",
                            'behavioral_anomaly': True
                        })
                        
                    if request_count > 1000:  # High request rate
                        await self.analyze_security_event({
                            'type': 'rate_limit_exceeded',
                            'source_ip': source_ip,
                            'user_id': user_id,
                            'description': f"High request rate: {request_count} requests/24h",
                            'high_usage': True
                        })
                        
        except Exception as e:
            logger.error(f"Error updating behavioral profiles: {e}")
            
    async def _check_behavioral_anomaly(self, event: SecurityEvent):
        """Check for behavioral anomalies"""
        
        if not event.user_id:
            return
            
        try:
            profile = self._behavioral_profiles.get(event.user_id)
            if not profile:
                return
                
            anomalies = []
            
            # Check IP anomaly
            if event.source_ip not in profile['typical_ips']:
                anomalies.append("unusual_ip")
                
            # Check geolocation anomaly (if GeoIP available)
            if self._geoip_db:
                try:
                    response = self._geoip_db.city(event.source_ip)
                    current_country = response.country.iso_code
                    
                    # Check if this is a new country for the user
                    typical_countries = {
                        self._geoip_db.city(ip).country.iso_code 
                        for ip in profile['typical_ips']
                    }
                    
                    if current_country not in typical_countries:
                        anomalies.append("unusual_location")
                        
                except Exception:
                    pass  # GeoIP lookup failed
                    
            # If anomalies detected, create security event
            if anomalies:
                await self.analyze_security_event({
                    'type': 'unusual_traffic_pattern',
                    'source_ip': event.source_ip,
                    'user_id': event.user_id,
                    'description': f"Behavioral anomalies detected: {', '.join(anomalies)}",
                    'behavioral_anomaly': True,
                    'anomaly_types': anomalies
                })
                
        except Exception as e:
            logger.error(f"Error checking behavioral anomaly: {e}")
            
    async def _monitor_rate_limits(self):
        """Monitor and enforce rate limits"""



        
        try:
            current_time = datetime.utcnow()
            
            # Check Redis rate limit counters
            if self.redis_client:
                keys = await self.redis_client.keys("rate_limit:*")
                
                for key in keys:
                    key_str = key.decode() if isinstance(key, bytes) else key
                    
                    # Parse key components
                    parts = key_str.split(':')
                    if len(parts) >= 3:
                        limit_type = parts[1]  # api, download, upload, etc.
                        identifier = ':'.join(parts[2:])  # IP or user ID
                        
                        # Get current count
                        count = await self.redis_client.get(key)
                        if count:
                            count = int(count)
                            
                            # Check against limits
                            limit_exceeded = self._check_rate_limit_exceeded(limit_type, count)
                            
                            if limit_exceeded:
                                await self.analyze_security_event({
                                    'type': 'rate_limit_exceeded',
                                    'source_ip': identifier if '.' in identifier else 'unknown',
                                    'user_id': identifier if '.' not in identifier else None,
                                    'description': f"Rate limit exceeded: {count} {limit_type} requests",
                                    'limit_type': limit_type,
                                    'request_count': count
                                })
                                
        except Exception as e:
            logger.error(f"Error monitoring rate limits: {e}")
            
    def _check_rate_limit_exceeded(self, limit_type: str, count: int) -> bool:
        """Check if rate limit is exceeded"""
        
        rate_limits = {
            'api': 1000,  # requests per hour
            'download': 100,  # downloads per hour
            'upload': 50,  # uploads per hour
            'fingerprint': 200,  # fingerprint operations per hour
            'search': 500  # searches per hour
        }
        
        return count > rate_limits.get(limit_type, 1000)
        
    async def _collect_security_metrics(self):
        """Collect security monitoring metrics"""



        
        try:
            current_time = datetime.utcnow()
            
            # Count events by type and threat level
            events_by_type = defaultdict(int)
            events_by_threat_level = defaultdict(int)
            
            # Get recent events from last hour
            if self.db_engine:
                async with self.db_engine.begin() as conn:
                    result = await conn.execute(text("""
                        SELECT event_type, threat_level, COUNT(*)
                        FROM security_events 
                        WHERE timestamp > NOW() - INTERVAL '1 hour'
                        GROUP BY event_type, threat_level
                    """))
                    
                    total_events = 0
                    for row in result:
                        event_type, threat_level, count = row
                        events_by_type[SecurityEventType(event_type)] += count
                        events_by_threat_level[ThreatLevel(threat_level)] += count
                        total_events += count
                        
            # Calculate metrics
            metrics = SecurityMetrics(
                total_events=total_events,
                events_by_type=dict(events_by_type),
                events_by_threat_level=dict(events_by_threat_level),
                blocked_ips=len(self._blocked_ips),
                suspicious_users=len(self._suspicious_users),
                false_positives=0,  # Would be calculated from resolved events
                response_time_avg=0.0,  # Would be calculated from response times
                timestamp=current_time
            )
            
            # Store metrics
            self._security_metrics.append(metrics)
            
            # Store in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"security:metrics:{int(current_time.timestamp())}",
                    3600,  # 1 hour TTL
                    json.dumps({
                        'total_events': metrics.total_events,
                        'events_by_type': {k.value: v for k, v in metrics.events_by_type.items()},
                        'events_by_threat_level': {k.value: v for k, v in metrics.events_by_threat_level.items()},
                        'blocked_ips': metrics.blocked_ips,
                        'suspicious_users': metrics.suspicious_users,
                        'timestamp': current_time.isoformat()
                    })
                )
                
        except Exception as e:
            logger.error(f"Error collecting security metrics: {e}")
            
    async def _cleanup_old_data(self):
        """Cleanup old security data"""



        
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=self.retention_days)
            
            # Cleanup database
            if self.db_engine:
                async with self.db_engine.begin() as conn:
                    # Delete old security events
                    await conn.execute(text("""
                        DELETE FROM security_events 
                        WHERE timestamp < :cutoff_time
                    """), {'cutoff_time': cutoff_time})
                    
                    # Delete old blocked IPs
                    await conn.execute(text("""
                        DELETE FROM security_ip_blocks 
                        WHERE expires_at < :now
                    """), {'now': datetime.utcnow()})
                    
            # Cleanup Redis
            if self.redis_client:
                # Remove expired blocked IPs
                pattern = "security:blocked_ip:*"
                keys = await self.redis_client.keys(pattern)
                
                for key in keys:
                    # Redis will auto-expire, but we can manually check
                    ttl = await self.redis_client.ttl(key)
                    if ttl == -1:  # No TTL set
                        await self.redis_client.delete(key)
                        
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            
    async def _store_security_event(self, event: SecurityEvent):
        """Store security event"""



        
        try:
            # Store in database
            if self.db_engine:
                async with self.db_engine.begin() as conn:
                    await conn.execute(text("""
                        INSERT INTO security_events (
                            id, event_type, threat_level, source_ip, user_id,
                            description, details, timestamp
                        ) VALUES (
                            :id, :event_type, :threat_level, :source_ip, :user_id,
                            :description, :details, :timestamp
                        )
                    """), {
                        'id': event.id,
                        'event_type': event.event_type.value,
                        'threat_level': event.threat_level.value,
                        'source_ip': event.source_ip,
                        'user_id': event.user_id,
                        'description': event.description,
                        'details': json.dumps(event.details),
                        'timestamp': event.timestamp
                    })
                    
            # Store in Redis for real-time access
            if self.redis_client:
                await self.redis_client.setex(
                    f"security:event:{event.id}",
                    86400,  # 24 hours TTL
                    json.dumps({
                        'id': event.id,
                        'event_type': event.event_type.value,
                        'threat_level': event.threat_level.value,
                        'source_ip': event.source_ip,
                        'user_id': event.user_id,
                        'description': event.description,
                        'details': event.details,
                        'timestamp': event.timestamp.isoformat(),
                        'resolved': event.resolved
                    })
                )
                
        except Exception as e:
            logger.error(f"Error storing security event: {e}")
            
    async def _load_security_data(self):
        """Load security data from storage"""



        
        try:
            # Load blocked IPs from Redis
            if self.redis_client:
                keys = await self.redis_client.keys("security:blocked_ip:*")
                for key in keys:
                    ip = key.decode().split(':')[-1]
                    self._blocked_ips.add(ip)
                    
                # Load suspicious users
                keys = await self.redis_client.keys("security:suspended_user:*")
                for key in keys:
                    user_id = key.decode().split(':')[-1]
                    self._suspicious_users.add(user_id)
                    
        except Exception as e:
            logger.error(f"Error loading security data: {e}")
            
    async def _save_security_data(self):
        """Save security data to storage"""
        
        # Data is automatically saved in real-time through Redis and database
        pass
        
    async def get_status(self) -> Dict[str, Any]:
        """Get security monitoring status"""
        
        latest_metrics = self._security_metrics[-1] if self._security_metrics else None
        
        return {
            'monitoring_active': self._running,
            'threat_patterns_loaded': len(self._threat_patterns),
            'blocked_ips': len(self._blocked_ips),
            'suspicious_users': len(self._suspicious_users),
            'latest_metrics': {
                'total_events': latest_metrics.total_events if latest_metrics else 0,
                'critical_events': latest_metrics.events_by_threat_level.get(ThreatLevel.CRITICAL, 0) if latest_metrics else 0,
                'timestamp': latest_metrics.timestamp.isoformat() if latest_metrics else None
            } if latest_metrics else None,
            'behavioral_profiles': len(self._behavioral_profiles),
            'last_update': datetime.utcnow().isoformat()
        }
        
    async def get_recent_events(self, hours: int = 24, threat_level: Optional[ThreatLevel] = None) -> List[SecurityEvent]:
        """Get recent security events"""
        
        events = []
        
        if self.redis_client:
            try:
                keys = await self.redis_client.keys("security:event:*")
                
                for key in keys:
                    value = await self.redis_client.get(key)
                    if value:
                        data = json.loads(value)
                        timestamp = datetime.fromisoformat(data['timestamp'])
                        
                        # Filter by time
                        if (datetime.utcnow() - timestamp).total_seconds() <= hours * 3600:
                            # Filter by threat level if specified
                            if threat_level is None or ThreatLevel(data['threat_level']) == threat_level:
                                events.append(SecurityEvent(
                                    id=data['id'],
                                    event_type=SecurityEventType(data['event_type']),
                                    threat_level=ThreatLevel(data['threat_level']),
                                    source_ip=data['source_ip'],
                                    user_id=data['user_id'],
                                    description=data['description'],
                                    details=data['details'],
                                    timestamp=timestamp,
                                    resolved=data['resolved']
                                ))
                                
                # Sort by timestamp (newest first)
                events.sort(key=lambda x: x.timestamp, reverse=True)
                
            except Exception as e:
                logger.error(f"Error getting recent events: {e}")
                
        return events
        
    async def get_security_metrics(self, hours: int = 24) -> List[SecurityMetrics]:
        """Get security metrics history"""
        
        # Return recent metrics from memory
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            metrics for metrics in self._security_metrics
            if metrics.timestamp >= cutoff_time
        ]
        
    async def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        
        if ip_address in self._blocked_ips:
            return True
            
        # Check Redis for current blocks
        if self.redis_client:
            try:
                result = await self.redis_client.get(f"security:blocked_ip:{ip_address}")
                return result is not None
            except Exception:
                pass
                
        return False
        
    async def is_user_suspended(self, user_id: str) -> bool:
        """Check if user is suspended"""
        
        if user_id in self._suspicious_users:
            return True
            
        # Check Redis for current suspensions
        if self.redis_client:
            try:
                result = await self.redis_client.get(f"security:suspended_user:{user_id}")
                return result is not None
            except Exception:
                pass
                
        return False
        
    async def unblock_ip(self, ip_address: str, reason: str = "Manual unblock"):
        """Unblock an IP address"""



        
        try:
            self._blocked_ips.discard(ip_address)
            
            # Remove from Redis
            if self.redis_client:
                await self.redis_client.delete(f"security:blocked_ip:{ip_address}")
                
            # Update database
            if self.db_engine:
                async with self.db_engine.begin() as conn:
                    await conn.execute(text("""
                        UPDATE security_ip_blocks 
                        SET expires_at = NOW(), unblocked_reason = :reason
                        WHERE ip_address = :ip_address AND expires_at > NOW()
                    """), {
                        'ip_address': ip_address,
                        'reason': reason
                    })
                    
            logger.info(f"IP address unblocked: {ip_address} - {reason}")
            
        except Exception as e:
            logger.error(f"Error unblocking IP {ip_address}: {e}")
            
    async def unsuspend_user(self, user_id: str, reason: str = "Manual unsuspension"):
        """Unsuspend a user account"""



        
        try:
            self._suspicious_users.discard(user_id)
            
            # Remove from Redis
            if self.redis_client:
                await self.redis_client.delete(f"security:suspended_user:{user_id}")
                
            # Update database
            if self.db_engine:
                async with self.db_engine.begin() as conn:
                    await conn.execute(text("""
                        UPDATE users 
                        SET status = 'active',
                            suspended_reason = NULL,
                            suspended_at = NULL,
                            unsuspended_reason = :reason,
                            unsuspended_at = NOW()
                        WHERE id = :user_id
                    """), {
                        'user_id': user_id,
                        'reason': reason
                    })
                    
            logger.info(f"User unsuspended: {user_id} - {reason}")
            
        except Exception as e:
            logger.error(f"Error unsuspending user {user_id}: {e}")
