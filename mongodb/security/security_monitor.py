"""Security Monitoring for MongoDB
===============================

Real-time security threat detection and monitoring with anomaly detection,
intrusion detection, and automated response capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import threading
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Security threat levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Types of security threats."""
    BRUTE_FORCE = "brute_force"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    INJECTION_ATTACK = "injection_attack"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    MASS_DATA_ACCESS = "mass_data_access"
    UNUSUAL_QUERY_PATTERN = "unusual_query_pattern"

@dataclass
class SecurityAlert:
    """Security alert information."""
    alert_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    description: str
    source_ip: Optional[str]
    user_id: Optional[str]
    timestamp: datetime
    details: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False

class SecurityMonitor:
    """Real-time security monitoring system."""
    
    def __init__(self) -> None:
        """Initialize security monitor."""
        self._running = False
        self._monitor_thread = None
        self._alerts: List[SecurityAlert] = []
        self._alert_handlers: List[Callable] = []
        
        # Tracking data structures
        self._failed_logins: defaultdict = defaultdict(deque)  # IP -> timestamps
        self._user_activity: defaultdict = defaultdict(deque)  # User -> activities
        self._query_patterns: defaultdict = defaultdict(list)  # User -> query patterns
        self._data_access_volume: defaultdict = defaultdict(int)  # User -> bytes accessed
        
        # Thresholds
        self._thresholds = {
            'failed_login_attempts': 5,
            'failed_login_window_minutes': 15,
            'mass_data_threshold_mb': 100,
            'query_rate_per_minute': 100,
            'unusual_query_threshold': 50
        }
        
        self.start_monitoring()
    
    def start_monitoring(self) -> None:
        """Start security monitoring."""
        if not self._running:
            self._running = True
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            logger.info("Security monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop security monitoring."""
        if self._running:
            self._running = False
            if self._monitor_thread:
                self._monitor_thread.join(timeout=5)
            logger.info("Security monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                self._check_threats()
                self._cleanup_old_data()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in security monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def record_login_attempt(self, user_id -> None: str, source_ip -> None: str, success -> None: bool,
                           user_agent -> None: str = None, details -> None: Dict[str, Any] = None) -> None:
        """Record login attempt for monitoring."""
        timestamp = datetime.utcnow()
        
        if not success:
            # Track failed login attempts by IP
            self._failed_logins[source_ip].append(timestamp)
            
            # Check for brute force attack
            self._check_brute_force_attack(source_ip)
        
        # Record user activity
        activity = {
            'type': 'login',
            'timestamp': timestamp,
            'success': success,
            'source_ip': source_ip,
            'user_agent': user_agent,
            'details': details or {}
        }
        self._user_activity[user_id].append(activity)
    
    def record_database_operation(self, user_id -> None: str, operation -> None: str, collection -> None: str,
                                query -> None: Dict[str, Any] = None, result_size_bytes -> None: int = None,
                                execution_time_ms -> None: float = None, source_ip -> None: str = None) -> None:
        """Record database operation for monitoring."""
        timestamp = datetime.utcnow()
        
        # Record query pattern
        query_signature = self._generate_query_signature(query or {})
        self._query_patterns[user_id].append({
            'timestamp': timestamp,
            'operation': operation,
            'collection': collection,
            'signature': query_signature,
            'result_size': result_size_bytes,
            'execution_time': execution_time_ms
        })
        
        # Track data access volume
        if result_size_bytes:
            self._data_access_volume[user_id] += result_size_bytes
        
        # Check for suspicious patterns
        self._check_suspicious_query_patterns(user_id)
        self._check_mass_data_access(user_id, result_size_bytes)
    
    def _check_threats(self) -> None:
        """Check for various security threats."""
        # This method is called periodically to check for threats
        pass  # Individual threat checks are called from specific events
    
    def _check_brute_force_attack(self, source_ip -> None: str) -> None:
        """Check for brute force login attacks."""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self._thresholds['failed_login_window_minutes'])
        
        # Count recent failed attempts
        recent_failures = [
            ts for ts in self._failed_logins[source_ip]
            if ts >= window_start
        ]
        
        if len(recent_failures) >= self._thresholds['failed_login_attempts']:
            self._create_alert(
                threat_type=ThreatType.BRUTE_FORCE,
                threat_level=ThreatLevel.HIGH,
                description=f"Brute force attack detected from IP {source_ip}",
                source_ip=source_ip,
                details={
                    'failed_attempts': len(recent_failures),
                    'time_window_minutes': self._thresholds['failed_login_window_minutes'],
                    'recent_failures': [ts.isoformat() for ts in recent_failures]
                }
            )
    
    def _check_suspicious_query_patterns(self, user_id -> None: str) -> None:
        """Check for suspicious query patterns."""
        if user_id not in self._query_patterns:
            return
        
        user_queries = self._query_patterns[user_id]
        now = datetime.utcnow()
        recent_queries = [
            q for q in user_queries
            if q['timestamp'] >= now - timedelta(minutes=5)
        ]
        
        # Check query rate
        if len(recent_queries) > self._thresholds['query_rate_per_minute']:
            self._create_alert(
                threat_type=ThreatType.UNUSUAL_QUERY_PATTERN,
                threat_level=ThreatLevel.MEDIUM,
                description=f"Unusual query rate detected for user {user_id}",
                user_id=user_id,
                details={
                    'query_count': len(recent_queries),
                    'time_window_minutes': 5,
                    'threshold': self._thresholds['query_rate_per_minute']
                }
            )
        
        # Check for unusual query signatures
        signatures = [q['signature'] for q in recent_queries]
        unique_signatures = len(set(signatures))
        
        if unique_signatures > self._thresholds['unusual_query_threshold']:
            self._create_alert(
                threat_type=ThreatType.ANOMALOUS_BEHAVIOR,
                threat_level=ThreatLevel.MEDIUM,
                description=f"Unusual query diversity detected for user {user_id}",
                user_id=user_id,
                details={
                    'unique_signatures': unique_signatures,
                    'total_queries': len(recent_queries),
                    'threshold': self._thresholds['unusual_query_threshold']
                }
            )
    
    def _check_mass_data_access(self, user_id -> None: str, result_size_bytes -> None: int) -> None:
        """Check for mass data access attempts."""
        if not result_size_bytes:
            return
        
        threshold_bytes = self._thresholds['mass_data_threshold_mb'] * 1024 * 1024
        
        if result_size_bytes > threshold_bytes:
            self._create_alert(
                threat_type=ThreatType.MASS_DATA_ACCESS,
                threat_level=ThreatLevel.HIGH,
                description=f"Mass data access detected for user {user_id}",
                user_id=user_id,
                details={
                    'data_size_mb': result_size_bytes / (1024 * 1024),
                    'threshold_mb': self._thresholds['mass_data_threshold_mb']
                }
            )
    
    def _generate_query_signature(self, query: Dict[str, Any]) -> str:
        """Generate signature for query pattern analysis."""
        # Simplified query signature based on keys and operation types
        if not query:
            return "empty"
        
        keys = sorted(query.keys())
        return f"keys:{':'.join(keys)}"
    
    def _create_alert(self, threat_type -> None: ThreatType, threat_level -> None: ThreatLevel,
                     description -> None: str, source_ip -> None: str = None, user_id -> None: str = None,
                     details -> None: Dict[str, Any] = None) -> None:
        """Create security alert."""
        alert_id = f"{threat_type.value}_{int(datetime.utcnow().timestamp())}"
        
        alert = SecurityAlert(
            alert_id=alert_id,
            threat_type=threat_type,
            threat_level=threat_level,
            description=description,
            source_ip=source_ip,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            details=details or {}
        )
        
        self._alerts.append(alert)
        
        # Notify handlers
        for handler in self._alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error notifying alert handler: {e}")
        
        # Log alert
        log_level = {
            ThreatLevel.LOW: logging.INFO,
            ThreatLevel.MEDIUM: logging.WARNING,
            ThreatLevel.HIGH: logging.ERROR,
            ThreatLevel.CRITICAL: logging.CRITICAL
        }.get(threat_level, logging.WARNING)
        
        logger.log(log_level, f"SECURITY ALERT: {description}")
    
    def _cleanup_old_data(self) -> None:
        """Clean up old monitoring data."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Clean failed login attempts
        for ip in list(self._failed_logins.keys()):
            self._failed_logins[ip] = deque([
                ts for ts in self._failed_logins[ip] if ts > cutoff_time
            ])
            if not self._failed_logins[ip]:
                del self._failed_logins[ip]
        
        # Clean user activity
        for user_id in list(self._user_activity.keys()):
            self._user_activity[user_id] = deque([
                activity for activity in self._user_activity[user_id]
                if activity['timestamp'] > cutoff_time
            ])
            if not self._user_activity[user_id]:
                del self._user_activity[user_id]
        
        # Clean query patterns
        for user_id in list(self._query_patterns.keys()):
            self._query_patterns[user_id] = [
                query for query in self._query_patterns[user_id]
                if query['timestamp'] > cutoff_time
            ]
            if not self._query_patterns[user_id]:
                del self._query_patterns[user_id]
        
        # Reset daily data access counters
        self._data_access_volume.clear()
    
    def add_alert_handler(self, handler -> None: Callable[[SecurityAlert], None]) -> None:
        """Add alert handler function."""
        self._alert_handlers.append(handler)
    
    def get_alerts(self, unresolved_only: bool = True) -> List[SecurityAlert]:
        """Get security alerts."""
        if unresolved_only:
            return [alert for alert in self._alerts if not alert.resolved]
        return self._alerts.copy()
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge a security alert."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a security alert."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                return True
        return False
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            "total_alerts": len(self._alerts),
            "unresolved_alerts": len([a for a in self._alerts if not a.resolved]),
            "alerts_by_type": {
                threat_type.value: len([a for a in self._alerts if a.threat_type == threat_type])
                for threat_type in ThreatType
            },
            "alerts_by_level": {
                level.value: len([a for a in self._alerts if a.threat_level == level])
                for level in ThreatLevel
            },
            "monitored_ips": len(self._failed_logins),
            "monitored_users": len(self._user_activity),
            "is_running": self._running
        }

# Global security monitor instance
_default_monitor: Optional[SecurityMonitor] = None

def get_security_monitor() -> SecurityMonitor:
    """Get or create default security monitor."""
    global _default_monitor
    if _default_monitor is None:
        _default_monitor = SecurityMonitor()
    return _default_monitor

__all__ = ['ThreatLevel', 'ThreatType', 'SecurityAlert', 'SecurityMonitor', 'get_security_monitor']