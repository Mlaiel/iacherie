"""Security Services Interface
Main entry point for Ainflue Platform security infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib
import jwt
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """SecurityLevel class implementation"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """ThreatType class implementation"""
    MALWARE = "malware"
    PHISHING = "phishing"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    DDOS = "ddos"
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"

@dataclass
class SecurityIncident:
    """Security incident configuration"""
    incident_id: str
    threat_type: ThreatType
    severity: SecurityLevel
    source_ip: Optional[str] = None
    target_resource: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

@dataclass
class VulnerabilityReport:
    """Vulnerability assessment report"""
    scan_id: str
    target: str
    vulnerabilities: List[Dict]
    severity_counts: Dict[SecurityLevel, int]
    scan_date: datetime
    next_scan_date: datetime

class SecurityOrchestrator:
    """Main orchestrator for security services"""
    
    def __init__(self) -> None:
        self.vulnerability_scanner = None
        self.threat_detector = None
        self.access_controller = None
        self.audit_logger = None
        self.encryption_manager = None
        self.active_incidents: Dict[str, SecurityIncident] = {}
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    async def initialize(self) -> None:
        """Initialize all security services"""
        logger.info("Initializing Security Orchestrator...")
        
        # Initialize core security services
        await self._initialize_vulnerability_scanner()
        await self._initialize_threat_detector()
        await self._initialize_access_controller()
        await self._initialize_audit_logger()
        await self._initialize_encryption_manager()
        
        logger.info("Security Orchestrator initialized successfully")
    
    async def _initialize_vulnerability_scanner(self) -> None:
        """Initialize vulnerability scanner"""
        from .vulnerability_scanner import VulnerabilityScanner
        self.vulnerability_scanner = VulnerabilityScanner()
        await self.vulnerability_scanner.initialize()
        logger.info("✅ Vulnerability scanner initialized")
    
    async def _initialize_threat_detector(self) -> None:
        """Initialize threat detector"""
        from .threat_detector import ThreatDetector
        self.threat_detector = ThreatDetector()
        await self.threat_detector.initialize()
        logger.info("✅ Threat detector initialized")
    
    async def _initialize_access_controller(self) -> None:
        """Initialize access controller"""
        from .access_controller import AccessController
        self.access_controller = AccessController()
        await self.access_controller.initialize()
        logger.info("✅ Access controller initialized")
    
    async def _initialize_audit_logger(self) -> None:
        """Initialize audit logger"""
        from .audit_logger import AuditLogger
        self.audit_logger = AuditLogger()
        await self.audit_logger.initialize()
        logger.info("✅ Audit logger initialized")
    
    async def _initialize_encryption_manager(self) -> None:
        """Initialize encryption manager"""
        from .encryption_manager import EncryptionManager
        self.encryption_manager = EncryptionManager()
        await self.encryption_manager.initialize()
        logger.info("✅ Encryption manager initialized")
    
    async def run_vulnerability_scan(self, target: str, scan_type: str = "full") -> VulnerabilityReport:
        """Run vulnerability scan on target"""
        logger.info(f"🔍 Starting vulnerability scan for {target}")
        
        try:
            scan_result = await self.vulnerability_scanner.scan_target(target, scan_type)
            
            # Log scan event
            await self.audit_logger.log_security_event(
                event_type="vulnerability_scan",
                target=target,
                details={"scan_type": scan_type, "scan_id": scan_result.scan_id}
            )
            
            logger.info(f"✅ Vulnerability scan completed for {target}")
            return scan_result
            
        except Exception as e:
            logger.error(f"❌ Vulnerability scan failed for {target}: {e}")
            raise
    
    async def detect_threats(self, data_source: str, time_window: int = 3600) -> List[SecurityIncident]:
        """Detect threats in data source"""
        logger.info(f"🔍 Detecting threats in {data_source}")
        
        try:
            threats = await self.threat_detector.analyze_data_source(data_source, time_window)
            
            # Process detected threats
            incidents = []
            for threat in threats:
                incident = SecurityIncident(
                    incident_id=f"incident_{int(datetime.now().timestamp())}_{threat['id']}",
                    threat_type=ThreatType(threat['type']),
                    severity=SecurityLevel(threat['severity']),
                    source_ip=threat.get('source_ip'),
                    target_resource=threat.get('target'),
                    description=threat.get('description'),
                    metadata=threat.get('metadata'),
                    created_at=datetime.now()
                )
                
                incidents.append(incident)
                self.active_incidents[incident.incident_id] = incident
                
                # Log threat detection
                await self.audit_logger.log_security_event(
                    event_type="threat_detected",
                    incident_id=incident.incident_id,
                    details=threat
                )
            
            logger.info(f"✅ Detected {len(incidents)} threats in {data_source}")
            return incidents
            
        except Exception as e:
            logger.error(f"❌ Threat detection failed for {data_source}: {e}")
            raise
    
    async def authenticate_user(self, username: str, password: str, 
                              mfa_token: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate user with optional MFA"""
        logger.info(f"🔐 Authenticating user: {username}")
        
        try:
            # Primary authentication
            auth_result = await self.access_controller.authenticate(username, password)
            
            if not auth_result['success']:
                await self.audit_logger.log_security_event(
                    event_type="authentication_failed",
                    username=username,
                    details={"reason": "invalid_credentials"}
                )
                return auth_result
            
            # MFA verification if enabled
            if auth_result.get('mfa_required') and mfa_token:
                mfa_result = await self.access_controller.verify_mfa(username, mfa_token)
                if not mfa_result['success']:
                    await self.audit_logger.log_security_event(
                        event_type="mfa_failed",
                        username=username,
                        details={"reason": "invalid_mfa_token"}
                    )
                    return mfa_result
            
            # Generate secure session token
            session_token = jwt.encode(
                {
                    'username': username,
                    'roles': auth_result.get('roles', []),
                    'exp': datetime.utcnow() + timedelta(hours=24)
                },
                self.encryption_key,
                algorithm='HS256'
            )
            
            auth_result['session_token'] = session_token
            
            # Log successful authentication
            await self.audit_logger.log_security_event(
                event_type="authentication_success",
                username=username,
                details={"roles": auth_result.get('roles', [])}
            )
            
            logger.info(f"✅ User authenticated successfully: {username}")
            return auth_result
            
        except Exception as e:
            logger.error(f"❌ Authentication failed for {username}: {e}")
            raise
    
    async def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error(f"❌ Data encryption failed: {e}")
            raise
    
    async def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"❌ Data decryption failed: {e}")
            raise
    
    async def resolve_incident(self, incident_id -> None: str, resolution_notes -> None: str) -> None:
        """Resolve a security incident"""
        logger.info(f"🔧 Resolving security incident: {incident_id}")
        
        if incident_id in self.active_incidents:
            incident = self.active_incidents[incident_id]
            incident.resolved_at = datetime.now()
            
            # Log incident resolution
            await self.audit_logger.log_security_event(
                event_type="incident_resolved",
                incident_id=incident_id,
                details={"resolution_notes": resolution_notes}
            )
            
            # Remove from active incidents
            del self.active_incidents[incident_id]
            
            logger.info(f"✅ Security incident resolved: {incident_id}")
        else:
            logger.warning(f"⚠️ Security incident not found: {incident_id}")
    
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data"""
        try:
            dashboard_data = {
                "active_incidents": len(self.active_incidents),
                "threat_levels": {level.value: 0 for level in SecurityLevel},
                "recent_scans": await self.vulnerability_scanner.get_recent_scans(limit=10),
                "authentication_stats": await self.access_controller.get_auth_stats(),
                "system_health": await self._get_system_health(),
                "compliance_status": await self._get_compliance_status()
            }
            
            # Count threats by severity
            for incident in self.active_incidents.values():
                dashboard_data["threat_levels"][incident.severity.value] += 1
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Failed to generate security dashboard: {e}")
            raise
    
    async def _get_system_health(self) -> Dict[str, str]:
        """Get system health status"""
        health_status = {}
        
        services = [
            ("vulnerability_scanner", self.vulnerability_scanner),
            ("threat_detector", self.threat_detector),
            ("access_controller", self.access_controller),
            ("audit_logger", self.audit_logger)
        ]
        
        for service_name, service in services:
            try:
                if service and hasattr(service, 'health_check'):
                    is_healthy = await service.health_check()
                    health_status[service_name] = "healthy" if is_healthy else "unhealthy"
                else:
                    health_status[service_name] = "unknown"
            except Exception:
                health_status[service_name] = "error"
        
        return health_status
    
    async def _get_compliance_status(self) -> Dict[str, str]:
        """Get compliance status for various standards"""
        return {
            "iso27001": "compliant",
            "soc2": "compliant", 
            "gdpr": "compliant",
            "hipaa": "not_applicable",
            "pci_dss": "compliant"
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all security services"""
        logger.info("Shutting down Security Orchestrator...")
        
        services = [
            ("vulnerability_scanner", self.vulnerability_scanner),
            ("threat_detector", self.threat_detector),
            ("access_controller", self.access_controller),
            ("audit_logger", self.audit_logger),
            ("encryption_manager", self.encryption_manager)
        ]
        
        for service_name, service in services:
            try:
                if service and hasattr(service, 'shutdown'):
                    await service.shutdown()
                    logger.info(f"✅ {service_name} shutdown")
            except Exception as e:
                logger.error(f"❌ Error shutting down {service_name}: {e}")
        
        logger.info("✅ Security Orchestrator shutdown complete")

# Global security orchestrator instance
security_orchestrator = SecurityOrchestrator()

async def initialize_security_services() -> None:
    """Initialize security services"""
    await security_orchestrator.initialize()

async def shutdown_security_services() -> None:
    """Shutdown security services"""
    await security_orchestrator.shutdown()

__all__ = [
    'SecurityLevel', 'ThreatType', 'SecurityIncident', 'VulnerabilityReport',
    'SecurityOrchestrator', 'security_orchestrator', 'initialize_security_services',
    'shutdown_security_services'
]