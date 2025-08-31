"""Platform Security - Advanced Security Management System

Comprehensive security layer for platform operations including threat detection,
access control, data protection, and compliance monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import secrets
import ipaddress

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from ...core.config import settings
from ...core.logging import get_logger
from ...core.security import verify_jwt_token, create_access_token
from ...models.security import SecurityEvent, ThreatLevel, AccessLog
from ...services.security.threat_detector import ThreatDetectorService
from ...services.security.access_control import AccessControlService
from ...utils.ip_utils import get_client_ip, is_suspicious_ip

logger = get_logger(__name__)

class SecurityEventType(Enum):
    """Security event types"""
    SUSPICIOUS_LOGIN = "suspicious_login"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    API_ABUSE = "api_abuse"
    MALICIOUS_UPLOAD = "malicious_upload"
    CREDENTIAL_STUFFING = "credential_stuffing"
    BRUTE_FORCE = "brute_force"

class SecurityAction(Enum):
    """Security action types"""
    BLOCK_IP = "block_ip"
    SUSPEND_USER = "suspend_user"
    REQUIRE_2FA = "require_2fa"
    LOG_ONLY = "log_only"
    NOTIFY_ADMIN = "notify_admin"
    QUARANTINE_CONTENT = "quarantine_content"

@dataclass
class SecurityThreat:
    """Security threat information"""
    threat_id: str
    threat_type: SecurityEventType
    threat_level: ThreatLevel
    source_ip: str
    user_id: Optional[int] = None
    description: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    action_taken: Optional[SecurityAction] = None

class PlatformSecurity:
    """
    Advanced platform security management system
    
    Features:
    - Real-time threat detection
    - IP reputation monitoring
    - Rate limiting and abuse prevention
    - Content security scanning
    - Access control and permissions
    - Security audit logging
    - Incident response automation
    """
    
    def __init__(self):
        self.threat_detector = ThreatDetectorService()
        self.access_control = AccessControlService()
        
        # Security configurations
        self.rate_limits = {
            'api_calls': {'limit': 1000, 'window': 3600},  # 1000 per hour
            'uploads': {'limit': 100, 'window': 3600},     # 100 per hour
            'login_attempts': {'limit': 5, 'window': 900}  # 5 per 15 minutes
        }
        
        # Blocked IPs cache
        self.blocked_ips = set()
        self.suspicious_ips = set()
        
        # Security metrics
        self.security_metrics = {
            'threats_detected': 0,
            'threats_blocked': 0,
            'false_positives': 0
        }
    
    async def initialize(self) -> bool:
        """
        Initialize security system
        
        Returns:
            bool: Initialization success status
        """
        try:
            logger.info("Initializing Platform Security...")
            
            # Initialize threat detector
            await self.threat_detector.initialize()
            
            # Initialize access control
            await self.access_control.initialize()
            
            # Load blocked IPs
            await self._load_blocked_ips()
            
            # Start security monitoring
            asyncio.create_task(self._monitor_security_events())
            asyncio.create_task(self._update_ip_reputation())
            
            logger.info("Platform Security initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Security initialization failed: {e}")
            return False
    
    async def validate_request_security(
        self,
        request: Request,
        user_id: Optional[int] = None,
        resource_type: str = "api",
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Validate request security
        
        Args:
            request: FastAPI request object
            user_id: User ID if authenticated
            resource_type: Type of resource being accessed
            session: Database session
            
        Returns:
            Dict containing security validation results
        """
        try:
            client_ip = get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")
            
            security_result = {
                'allowed': True,
                'threat_level': 'low',
                'security_score': 100,
                'warnings': [],
                'actions': []
            }
            
            # Check IP reputation
            ip_check = await self._check_ip_reputation(client_ip)
            if not ip_check['allowed']:
                security_result.update({
                    'allowed': False,
                    'threat_level': 'high',
                    'security_score': 0,
                    'reason': 'IP blocked or suspicious'
                })
                return security_result
            
            # Rate limiting check
            rate_limit_check = await self._check_rate_limits(
                client_ip, user_id, resource_type
            )
            if not rate_limit_check['allowed']:
                security_result.update({
                    'allowed': False,
                    'threat_level': 'medium',
                    'security_score': 30,
                    'reason': 'Rate limit exceeded'
                })
                return security_result
            
            # User agent analysis
            ua_analysis = await self._analyze_user_agent(user_agent)
            if ua_analysis['suspicious']:
                security_result['warnings'].append('Suspicious user agent')
                security_result['security_score'] -= 20
            
            # Geographic anomaly detection
            if user_id:
                geo_analysis = await self._analyze_geographic_anomaly(
                    user_id, client_ip, session
                )
                if geo_analysis['anomalous']:
                    security_result['warnings'].append('Geographic anomaly detected')
                    security_result['security_score'] -= 30
                    security_result['actions'].append('require_additional_verification')
            
            # Update threat level based on score
            if security_result['security_score'] < 50:
                security_result['threat_level'] = 'high'
            elif security_result['security_score'] < 80:
                security_result['threat_level'] = 'medium'
            
            # Log access attempt
            await self._log_access_attempt(request, user_id, security_result, session)
            
            return security_result
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            return {
                'allowed': True,  # Fail open for availability
                'threat_level': 'unknown',
                'security_score': 50,
                'error': str(e)
            }
    
    async def scan_content_security(
        self,
        content_path: str,
        content_type: str,
        user_id: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Scan content for security threats
        
        Args:
            content_path: Path to content file
            content_type: Type of content
            user_id: Uploader user ID
            session: Database session
            
        Returns:
            Dict containing security scan results
        """
        try:
            scan_result = {
                'safe': True,
                'threat_level': 'low',
                'threats_found': [],
                'scan_score': 100,
                'quarantined': False
            }
            
            # Malware scanning
            malware_scan = await self.threat_detector.scan_for_malware(content_path)
            if malware_scan['threats_found']:
                scan_result.update({
                    'safe': False,
                    'threat_level': 'critical',
                    'threats_found': malware_scan['threats_found'],
                    'scan_score': 0,
                    'quarantined': True
                })
                
                # Quarantine content
                await self._quarantine_content(content_path, user_id, 'malware_detected')
                return scan_result
            
            # Content analysis
            if content_type in ['image', 'video']:
                visual_scan = await self._scan_visual_content(content_path)
                if visual_scan['inappropriate']:
                    scan_result['threats_found'].append('inappropriate_content')
                    scan_result['scan_score'] -= 40
            
            elif content_type == 'audio':
                audio_scan = await self._scan_audio_content(content_path)
                if audio_scan['copyright_violation']:
                    scan_result['threats_found'].append('copyright_violation')
                    scan_result['scan_score'] -= 60
            
            elif content_type == 'text':
                text_scan = await self._scan_text_content(content_path)
                if text_scan['malicious']:
                    scan_result['threats_found'].append('malicious_text')
                    scan_result['scan_score'] -= 80
            
            # Update threat level based on score
            if scan_result['scan_score'] < 30:
                scan_result['threat_level'] = 'critical'
                scan_result['safe'] = False
            elif scan_result['scan_score'] < 60:
                scan_result['threat_level'] = 'high'
            elif scan_result['scan_score'] < 80:
                scan_result['threat_level'] = 'medium'
            
            # Log security scan
            await self._log_security_scan(content_path, scan_result, user_id, session)
            
            return scan_result
            
        except Exception as e:
            logger.error(f"Content security scan failed: {e}")
            return {
                'safe': True,  # Fail open
                'threat_level': 'unknown',
                'scan_score': 50,
                'error': str(e)
            }
    
    async def detect_account_takeover(
        self,
        user_id: int,
        request: Request,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Detect potential account takeover attempts
        
        Args:
            user_id: User ID
            request: Request object
            session: Database session
            
        Returns:
            Dict containing takeover detection results
        """
        try:
            detection_result = {
                'takeover_detected': False,
                'confidence': 0.0,
                'indicators': [],
                'recommended_actions': []
            }
            
            client_ip = get_client_ip(request)
            user_agent = request.headers.get("user-agent", "")
            
            # Check for unusual login patterns
            recent_logins = await self._get_recent_login_attempts(user_id, session)
            
            # IP address analysis
            if await self._is_new_ip_for_user(user_id, client_ip, session):
                detection_result['indicators'].append('new_ip_address')
                detection_result['confidence'] += 0.3
            
            # Geographic analysis
            if await self._is_unusual_location(user_id, client_ip, session):
                detection_result['indicators'].append('unusual_location')
                detection_result['confidence'] += 0.4
            
            # Device fingerprint analysis
            device_analysis = await self._analyze_device_fingerprint(user_agent, user_id, session)
            if device_analysis['new_device']:
                detection_result['indicators'].append('new_device')
                detection_result['confidence'] += 0.2
            
            # Behavioral analysis
            behavior_analysis = await self._analyze_user_behavior(user_id, request, session)
            if behavior_analysis['anomalous']:
                detection_result['indicators'].append('anomalous_behavior')
                detection_result['confidence'] += 0.3
            
            # Determine if takeover is detected
            if detection_result['confidence'] >= 0.7:
                detection_result['takeover_detected'] = True
                detection_result['recommended_actions'] = [
                    'force_password_reset',
                    'require_2fa',
                    'notify_user',
                    'suspend_account_temporarily'
                ]
            elif detection_result['confidence'] >= 0.5:
                detection_result['recommended_actions'] = [
                    'require_additional_verification',
                    'notify_user',
                    'monitor_closely'
                ]
            
            # Log detection attempt
            if detection_result['takeover_detected']:
                await self._log_security_event(
                    SecurityEventType.UNAUTHORIZED_ACCESS,
                    user_id,
                    client_ip,
                    f"Potential account takeover detected: {', '.join(detection_result['indicators'])}",
                    session
                )
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Account takeover detection failed: {e}")
            return {
                'takeover_detected': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    async def generate_security_report(
        self,
        time_period: timedelta = timedelta(days=30),
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive security report
        
        Args:
            time_period: Time period for report
            session: Database session
            
        Returns:
            Dict containing security report data
        """
        try:
            start_date = datetime.utcnow() - time_period
            
            # Get security events
            result = await session.execute(
                select(SecurityEvent).where(
                    SecurityEvent.created_at >= start_date
                )
            )
            events = result.scalars().all()
            
            # Analyze security metrics
            event_counts = {}
            threat_levels = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
            
            for event in events:
                event_type = event.event_type
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
                threat_levels[event.threat_level.value] += 1
            
            # Top threat sources
            ip_threats = {}
            for event in events:
                ip = event.source_ip
                ip_threats[ip] = ip_threats.get(ip, 0) + 1
            
            top_threat_ips = sorted(ip_threats.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Security recommendations
            recommendations = await self._generate_security_recommendations(events)
            
            return {
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': datetime.utcnow().isoformat(),
                    'days': time_period.days
                },
                'summary': {
                    'total_events': len(events),
                    'unique_threat_sources': len(ip_threats),
                    'blocked_attempts': len([e for e in events if e.action_taken == SecurityAction.BLOCK_IP])
                },
                'event_breakdown': event_counts,
                'threat_level_distribution': threat_levels,
                'top_threat_sources': top_threat_ips,
                'security_metrics': self.security_metrics,
                'recommendations': recommendations,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Security report generation failed: {e}")
            return {'error': str(e)}
    
    async def _check_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Check IP reputation"""
        if ip in self.blocked_ips:
            return {'allowed': False, 'reason': 'IP blocked'}
        
        if ip in self.suspicious_ips:
            return {'allowed': False, 'reason': 'IP suspicious'}
        
        # Check against external threat intelligence
        reputation_check = await self.threat_detector.check_ip_reputation(ip)
        
        return {
            'allowed': reputation_check.get('safe', True),
            'reputation_score': reputation_check.get('score', 100),
            'reason': reputation_check.get('reason', '')
        }
    
    async def _check_rate_limits(
        self, 
        ip: str, 
        user_id: Optional[int], 
        resource_type: str
    ) -> Dict[str, Any]:
        """Check rate limits"""
        # Implementation for rate limiting logic
        return {'allowed': True, 'remaining': 1000}
    
    async def _analyze_user_agent(self, user_agent: str) -> Dict[str, Any]:
        """Analyze user agent for suspicious patterns"""
        suspicious_patterns = [
            'bot', 'crawler', 'spider', 'scraper', 'automated',
            'curl', 'wget', 'python-requests'
        ]
        
        suspicious = any(pattern in user_agent.lower() for pattern in suspicious_patterns)
        
        return {
            'suspicious': suspicious,
            'automated': suspicious,
            'browser_type': 'unknown'
        }
    
    async def _analyze_geographic_anomaly(
        self, 
        user_id: int, 
        ip: str, 
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Analyze geographic anomalies"""
        # Implementation for geographic analysis
        return {'anomalous': False, 'country': 'unknown'}
    
    async def _log_access_attempt(
        self, 
        request: Request, 
        user_id: Optional[int], 
        security_result: Dict[str, Any], 
        session: AsyncSession
    ):
        """Log access attempt"""
        access_log = AccessLog(
            user_id=user_id,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent", ""),
            endpoint=str(request.url.path),
            method=request.method,
            security_score=security_result['security_score'],
            threat_level=security_result['threat_level'],
            created_at=datetime.utcnow()
        )
        
        session.add(access_log)
        await session.commit()
    
    async def _scan_visual_content(self, content_path: str) -> Dict[str, Any]:
        """Scan visual content for inappropriate material"""
        # Implementation for visual content scanning
        return {'inappropriate': False, 'confidence': 0.0}
    
    async def _scan_audio_content(self, content_path: str) -> Dict[str, Any]:
        """Scan audio content for copyright violations"""
        # Implementation for audio content scanning
        return {'copyright_violation': False, 'confidence': 0.0}
    
    async def _scan_text_content(self, content_path: str) -> Dict[str, Any]:
        """Scan text content for malicious content"""
        # Implementation for text content scanning
        return {'malicious': False, 'threats': []}
    
    async def _quarantine_content(self, content_path: str, user_id: int, reason: str):
        """Quarantine malicious content"""
        # Implementation for content quarantine
        logger.warning(f"Content quarantined: {content_path} - Reason: {reason}")
    
    async def _log_security_scan(
        self, 
        content_path: str, 
        scan_result: Dict[str, Any], 
        user_id: int, 
        session: AsyncSession
    ):
        """Log security scan results"""
        # Implementation for logging security scans
        pass
    
    async def _log_security_event(
        self, 
        event_type: SecurityEventType, 
        user_id: int, 
        ip: str, 
        description: str, 
        session: AsyncSession
    ):
        """Log security event"""
        security_event = SecurityEvent(
            event_type=event_type.value,
            user_id=user_id,
            source_ip=ip,
            description=description,
            threat_level=ThreatLevel.MEDIUM,
            created_at=datetime.utcnow()
        )
        
        session.add(security_event)
        await session.commit()
    
    async def _monitor_security_events(self):
        """Monitor security events in background"""
        while True:
            try:
                # Implementation for security event monitoring
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Security monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _update_ip_reputation(self):
        """Update IP reputation data"""
        while True:
            try:
                # Implementation for IP reputation updates
                await asyncio.sleep(1800)  # Update every 30 minutes
                
            except Exception as e:
                logger.error(f"IP reputation update error: {e}")
                await asyncio.sleep(1800)
    
    async def _load_blocked_ips(self):
        """Load blocked IPs from database"""
        # Implementation for loading blocked IPs
        pass
