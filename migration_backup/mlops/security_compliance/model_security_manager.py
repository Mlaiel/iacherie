"""
Model Security Manager
Enterprise-grade security management for ML models

Features:
- Model vulnerability scanning
- Secure model deployment
- Model access control
- Security policy enforcement
- Model tampering detection
- Secure model serving

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import hashlib
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime, timedelta


class SecurityLevel(Enum):
    """Security levels for model deployment"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Types of security threats"""
    MODEL_POISONING = "model_poisoning"
    ADVERSARIAL_ATTACK = "adversarial_attack"
    DATA_LEAKAGE = "data_leakage"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MODEL_THEFT = "model_theft"


@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    encryption_required: bool = True
    access_control_enabled: bool = True
    audit_logging: bool = True
    vulnerability_scanning: bool = True
    threat_monitoring: bool = True
    max_inference_rate: int = 1000
    allowed_users: List[str] = None
    allowed_ips: List[str] = None


@dataclass
class ModelSecurityConfig:
    """Model security configuration"""
    model_id: str
    security_level: SecurityLevel
    policy: SecurityPolicy
    encryption_key: Optional[str] = None
    checksum: Optional[str] = None


@dataclass
class SecurityEvent:
    """Security event logging"""
    timestamp: datetime
    event_type: str
    threat_type: Optional[ThreatType]
    model_id: str
    user_id: Optional[str]
    ip_address: Optional[str]
    severity: str
    description: str
    metadata: Dict[str, Any]


class ModelSecurityManager:
    """
    Enterprise Model Security Manager
    Comprehensive security management for ML models
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_configs: Dict[str, ModelSecurityConfig] = {}
        self.security_events: List[SecurityEvent] = []
        self.active_monitors: Dict[str, bool] = {}
        
    async def register_model(
        self,
        model_id: str,
        security_level: SecurityLevel,
        policy: SecurityPolicy
    ) -> ModelSecurityConfig:
        """Register a model with security configuration"""
        try:
            # Generate encryption key for high/critical security
            encryption_key = None
            if security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                encryption_key = self._generate_encryption_key()
            
            # Create security configuration
            config = ModelSecurityConfig(
                model_id=model_id,
                security_level=security_level,
                policy=policy,
                encryption_key=encryption_key
            )
            
            self.security_configs[model_id] = config
            
            # Log security registration
            await self._log_security_event(
                event_type="model_registration",
                model_id=model_id,
                severity="info",
                description=f"Model registered with {security_level.value} security level"
            )
            
            self.logger.info(f"Model {model_id} registered with security level {security_level.value}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to register model {model_id}: {str(e)}")
            raise
    
    async def validate_model_integrity(
        self,
        model_id: str,
        model_data: bytes
    ) -> bool:
        """Validate model integrity using checksums"""
        try:
            config = self.security_configs.get(model_id)
            if not config:
                raise ValueError(f"Model {model_id} not registered")
            
            # Calculate current checksum
            current_checksum = hashlib.sha256(model_data).hexdigest()
            
            # Compare with stored checksum
            if config.checksum:
                if current_checksum != config.checksum:
                    await self._log_security_event(
                        event_type="integrity_violation",
                        threat_type=ThreatType.MODEL_POISONING,
                        model_id=model_id,
                        severity="critical",
                        description="Model integrity check failed - potential tampering detected"
                    )
                    return False
            else:
                # Store initial checksum
                config.checksum = current_checksum
                self.security_configs[model_id] = config
            
            return True
            
        except Exception as e:
            self.logger.error(f"Integrity validation failed for model {model_id}: {str(e)}")
            return False
    
    async def authorize_access(
        self,
        model_id: str,
        user_id: str,
        ip_address: str,
        action: str
    ) -> bool:
        """Authorize user access to model"""
        try:
            config = self.security_configs.get(model_id)
            if not config:
                return False
            
            policy = config.policy
            
            # Check if access control is enabled
            if not policy.access_control_enabled:
                return True
            
            # Check allowed users
            if policy.allowed_users and user_id not in policy.allowed_users:
                await self._log_security_event(
                    event_type="access_denied",
                    threat_type=ThreatType.UNAUTHORIZED_ACCESS,
                    model_id=model_id,
                    user_id=user_id,
                    ip_address=ip_address,
                    severity="warning",
                    description=f"Access denied for user {user_id} - not in allowed users list"
                )
                return False
            
            # Check allowed IPs
            if policy.allowed_ips and ip_address not in policy.allowed_ips:
                await self._log_security_event(
                    event_type="access_denied",
                    threat_type=ThreatType.UNAUTHORIZED_ACCESS,
                    model_id=model_id,
                    user_id=user_id,
                    ip_address=ip_address,
                    severity="warning",
                    description=f"Access denied for IP {ip_address} - not in allowed IPs list"
                )
                return False
            
            # Log successful access
            await self._log_security_event(
                event_type="access_granted",
                model_id=model_id,
                user_id=user_id,
                ip_address=ip_address,
                severity="info",
                description=f"Access granted for action: {action}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Authorization failed for model {model_id}: {str(e)}")
            return False
    
    async def scan_for_vulnerabilities(
        self,
        model_id: str
    ) -> Dict[str, Any]:
        """Scan model for security vulnerabilities"""
        try:
            config = self.security_configs.get(model_id)
            if not config:
                raise ValueError(f"Model {model_id} not registered")
            
            vulnerabilities = {
                "model_id": model_id,
                "scan_timestamp": datetime.now().isoformat(),
                "vulnerabilities": [],
                "risk_score": 0,
                "recommendations": []
            }
            
            # Check for common vulnerabilities
            if not config.encryption_key and config.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                vulnerabilities["vulnerabilities"].append({
                    "type": "missing_encryption",
                    "severity": "high",
                    "description": "High security model lacks encryption"
                })
                vulnerabilities["risk_score"] += 30
            
            if not config.policy.access_control_enabled:
                vulnerabilities["vulnerabilities"].append({
                    "type": "weak_access_control",
                    "severity": "medium",
                    "description": "Access control is disabled"
                })
                vulnerabilities["risk_score"] += 20
            
            if not config.policy.audit_logging:
                vulnerabilities["vulnerabilities"].append({
                    "type": "missing_audit_logs",
                    "severity": "medium", 
                    "description": "Audit logging is disabled"
                })
                vulnerabilities["risk_score"] += 15
            
            # Generate recommendations
            if vulnerabilities["risk_score"] > 50:
                vulnerabilities["recommendations"].append("Enable all security features for critical models")
            if vulnerabilities["risk_score"] > 20:
                vulnerabilities["recommendations"].append("Review and strengthen access controls")
            
            # Log vulnerability scan
            await self._log_security_event(
                event_type="vulnerability_scan",
                model_id=model_id,
                severity="info",
                description=f"Vulnerability scan completed - risk score: {vulnerabilities['risk_score']}",
                metadata=vulnerabilities
            )
            
            return vulnerabilities
            
        except Exception as e:
            self.logger.error(f"Vulnerability scan failed for model {model_id}: {str(e)}")
            raise
    
    async def monitor_threats(
        self,
        model_id: str,
        enable: bool = True
    ) -> bool:
        """Enable/disable threat monitoring for model"""
        try:
            config = self.security_configs.get(model_id)
            if not config:
                return False
            
            self.active_monitors[model_id] = enable
            
            if enable:
                # Start monitoring task
                asyncio.create_task(self._threat_monitoring_loop(model_id))
                
            await self._log_security_event(
                event_type="threat_monitoring",
                model_id=model_id,
                severity="info",
                description=f"Threat monitoring {'enabled' if enable else 'disabled'}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure threat monitoring for model {model_id}: {str(e)}")
            return False
    
    async def get_security_metrics(
        self,
        model_id: Optional[str] = None,
        time_window: timedelta = timedelta(hours=24)
    ) -> Dict[str, Any]:
        """Get security metrics for model(s)"""
        try:
            current_time = datetime.now()
            start_time = current_time - time_window
            
            # Filter events by time window and model
            filtered_events = [
                event for event in self.security_events
                if event.timestamp >= start_time and
                (model_id is None or event.model_id == model_id)
            ]
            
            metrics = {
                "time_window": {
                    "start": start_time.isoformat(),
                    "end": current_time.isoformat()
                },
                "total_events": len(filtered_events),
                "events_by_type": {},
                "threats_detected": 0,
                "access_denied_count": 0,
                "vulnerability_scans": 0,
                "models_monitored": len(self.active_monitors)
            }
            
            # Analyze events
            for event in filtered_events:
                event_type = event.event_type
                metrics["events_by_type"][event_type] = metrics["events_by_type"].get(event_type, 0) + 1
                
                if event.threat_type:
                    metrics["threats_detected"] += 1
                
                if event.event_type == "access_denied":
                    metrics["access_denied_count"] += 1
                
                if event.event_type == "vulnerability_scan":
                    metrics["vulnerability_scans"] += 1
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get security metrics: {str(e)}")
            raise
    
    def _generate_encryption_key(self) -> str:
        """Generate encryption key for model security"""
        import secrets
        return secrets.token_hex(32)
    
    async def _log_security_event(
        self,
        event_type: str,
        model_id: str,
        severity: str,
        description: str,
        threat_type: Optional[ThreatType] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log security event"""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            threat_type=threat_type,
            model_id=model_id,
            user_id=user_id,
            ip_address=ip_address,
            severity=severity,
            description=description,
            metadata=metadata or {}
        )
        
        self.security_events.append(event)
        
        # Keep only recent events (last 10000)
        if len(self.security_events) > 10000:
            self.security_events = self.security_events[-10000:]
    
    async def _threat_monitoring_loop(self, model_id: str):
        """Background threat monitoring for a model"""
        while self.active_monitors.get(model_id, False):
            try:
                # Monitor for threats (simplified implementation)
                # In production, this would integrate with SIEM systems
                await asyncio.sleep(60)  # Check every minute
                
                # Example threat detection logic would go here
                # - Monitor inference patterns
                # - Detect anomalous requests
                # - Check for adversarial inputs
                
            except Exception as e:
                self.logger.error(f"Threat monitoring error for model {model_id}: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error


# Global instance
model_security_manager = ModelSecurityManager()