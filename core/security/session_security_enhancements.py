"""
Session Security Enhancements
Advanced session management with enterprise-grade security features

Features:
- Session fingerprinting and validation
- Advanced session hijacking detection
- Secure session token generation
- Session expiration and rotation
- Geographic and behavioral analysis
- Concurrent session management

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import hashlib
import hmac
import secrets
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
import user_agents

from backend.core.config import get_settings
from backend.core.cache import CacheManager
from backend.core.logging import SecurityLogger


class SessionSecurityLevel(Enum):
    """Session security levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SessionStatus(Enum):
    """Session status values"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPICIOUS = "suspicious"
    LOCKED = "locked"


@dataclass
class SessionFingerprint:
    """Session fingerprint for security validation"""
    user_agent: str
    ip_address: str
    screen_resolution: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    platform: Optional[str] = None
    browser: Optional[str] = None
    device_type: Optional[str] = None
    fingerprint_hash: str = field(init=False)
    
    def __post_init__(self):
        self.fingerprint_hash = self._generate_fingerprint_hash()
    
    def _generate_fingerprint_hash(self) -> str:
        """Generate unique fingerprint hash"""
        fingerprint_data = {
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "screen_resolution": self.screen_resolution,
            "timezone": self.timezone,
            "language": self.language,
            "platform": self.platform,
            "browser": self.browser,
            "device_type": self.device_type
        }
        
        # Create consistent hash
        data_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()


@dataclass
class SecureSession:
    """Secure session with enhanced security features"""
    session_id: str
    user_id: str
    fingerprint: SessionFingerprint
    security_level: SessionSecurityLevel
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    ip_history: List[str] = field(default_factory=list)
    location_changes: int = 0
    suspicious_activity_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class SessionSecurityManager:
    """Enhanced session security management"""
    
    def __init__(self):
        self.logger = SecurityLogger("SessionSecurityManager")
        self.cache = CacheManager()
        self.settings = get_settings()
        
        # Security configuration
        self.max_concurrent_sessions = 5
        self.session_timeout_minutes = 120
        self.suspicious_activity_threshold = 3
        self.max_location_changes = 5
        self.fingerprint_change_threshold = 0.8
        
        # Geographic monitoring
        self.suspicious_countries = {"CN", "RU", "IR", "KP"}  # Example list
        
    async def create_secure_session(
        self,
        user_id: str,
        fingerprint: SessionFingerprint,
        security_level: SessionSecurityLevel = SessionSecurityLevel.MEDIUM
    ) -> SecureSession:
        """Create new secure session with enhanced validation"""
        try:
            # Generate secure session ID
            session_id = self._generate_secure_session_id()
            
            # Check for concurrent session limit
            await self._enforce_concurrent_session_limit(user_id)
            
            # Determine session expiration
            expires_at = datetime.utcnow() + timedelta(minutes=self.session_timeout_minutes)
            
            # Create session
            session = SecureSession(
                session_id=session_id,
                user_id=user_id,
                fingerprint=fingerprint,
                security_level=security_level,
                expires_at=expires_at
            )
            
            # Initialize IP history
            session.ip_history.append(fingerprint.ip_address)
            
            # Perform initial security checks
            await self._perform_initial_security_checks(session)
            
            # Store session
            await self._store_session(session)
            
            self.logger.info(f"Secure session created: {session_id} for user {user_id}")
            return session
            
        except Exception as e:
            self.logger.error(f"Failed to create secure session: {str(e)}")
            raise
    
    async def validate_session(
        self,
        session_id: str,
        current_fingerprint: SessionFingerprint
    ) -> Tuple[bool, Optional[SecureSession]]:
        """Validate session with advanced security checks"""
        try:
            # Retrieve session
            session = await self._get_session(session_id)
            if not session:
                self.logger.warning(f"Session not found: {session_id}")
                return False, None
            
            # Check session status
            if session.status != SessionStatus.ACTIVE:
                self.logger.warning(f"Session not active: {session_id}, status: {session.status}")
                return False, session
            
            # Check expiration
            if session.expires_at and datetime.utcnow() > session.expires_at:
                self.logger.warning(f"Session expired: {session_id}")
                await self._mark_session_expired(session_id)
                return False, session
            
            # Validate fingerprint
            fingerprint_valid = await self._validate_fingerprint(session, current_fingerprint)
            if not fingerprint_valid:
                self.logger.warning(f"Fingerprint validation failed: {session_id}")
                await self._handle_suspicious_activity(session, "fingerprint_mismatch")
                return False, session
            
            # Check for suspicious activity
            if await self._detect_suspicious_activity(session, current_fingerprint):
                self.logger.warning(f"Suspicious activity detected: {session_id}")
                await self._handle_suspicious_activity(session, "suspicious_behavior")
                return False, session
            
            # Update session activity
            await self._update_session_activity(session, current_fingerprint)
            
            return True, session
            
        except Exception as e:
            self.logger.error(f"Session validation error: {str(e)}")
            return False, None
    
    async def rotate_session(self, session_id: str) -> Optional[SecureSession]:
        """Rotate session with new ID for security"""
        try:
            # Get current session
            old_session = await self._get_session(session_id)
            if not old_session:
                return None
            
            # Create new session with same properties
            new_session = await self.create_secure_session(
                user_id=old_session.user_id,
                fingerprint=old_session.fingerprint,
                security_level=old_session.security_level
            )
            
            # Transfer metadata
            new_session.ip_history = old_session.ip_history.copy()
            new_session.location_changes = old_session.location_changes
            new_session.metadata = old_session.metadata.copy()
            
            # Revoke old session
            await self.revoke_session(session_id, "session_rotation")
            
            self.logger.info(f"Session rotated: {session_id} -> {new_session.session_id}")
            return new_session
            
        except Exception as e:
            self.logger.error(f"Session rotation failed: {str(e)}")
            return None
    
    async def revoke_session(self, session_id: str, reason: str = "manual_revocation"):
        """Revoke session"""
        try:
            session = await self._get_session(session_id)
            if session:
                session.status = SessionStatus.REVOKED
                session.metadata["revocation_reason"] = reason
                session.metadata["revoked_at"] = datetime.utcnow().isoformat()
                
                await self._store_session(session)
                
                # Remove from cache
                cache_key = f"session:{session_id}"
                await self.cache.delete(cache_key)
                
                self.logger.info(f"Session revoked: {session_id}, reason: {reason}")
                
        except Exception as e:
            self.logger.error(f"Session revocation failed: {str(e)}")
    
    async def revoke_all_user_sessions(self, user_id: str, except_session: Optional[str] = None):
        """Revoke all sessions for a user"""
        try:
            user_sessions = await self._get_user_sessions(user_id)
            
            for session in user_sessions:
                if except_session and session.session_id == except_session:
                    continue
                
                await self.revoke_session(session.session_id, "revoke_all_sessions")
            
            self.logger.info(f"All sessions revoked for user: {user_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to revoke all user sessions: {str(e)}")
    
    def _generate_secure_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        # Generate 256-bit random token
        random_bytes = secrets.token_bytes(32)
        
        # Add timestamp for uniqueness
        timestamp = str(int(datetime.utcnow().timestamp())).encode()
        
        # Create HMAC for integrity
        hmac_key = secrets.token_bytes(32)
        signature = hmac.new(hmac_key, random_bytes + timestamp, hashlib.sha256).digest()
        
        # Combine and encode
        session_data = random_bytes + signature
        return secrets.token_urlsafe(len(session_data))[:48]  # Truncate to reasonable length
    
    async def _enforce_concurrent_session_limit(self, user_id: str):
        """Enforce maximum concurrent sessions per user"""
        try:
            user_sessions = await self._get_active_user_sessions(user_id)
            
            if len(user_sessions) >= self.max_concurrent_sessions:
                # Revoke oldest session
                oldest_session = min(user_sessions, key=lambda s: s.created_at)
                await self.revoke_session(oldest_session.session_id, "concurrent_limit_exceeded")
                
                self.logger.info(f"Concurrent session limit enforced for user: {user_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to enforce concurrent session limit: {str(e)}")
    
    async def _perform_initial_security_checks(self, session: SecureSession):
        """Perform initial security checks on new session"""
        try:
            # Check for suspicious IP
            if await self._is_suspicious_ip(session.fingerprint.ip_address):
                session.suspicious_activity_count += 1
                session.metadata["suspicious_ip"] = True
                self.logger.warning(f"Suspicious IP detected: {session.fingerprint.ip_address}")
            
            # Check geographic location
            country_code = await self._get_country_from_ip(session.fingerprint.ip_address)
            if country_code in self.suspicious_countries:
                session.suspicious_activity_count += 1
                session.metadata["suspicious_country"] = country_code
                self.logger.warning(f"Login from suspicious country: {country_code}")
            
            # Parse user agent for additional info
            await self._enrich_fingerprint_data(session)
            
        except Exception as e:
            self.logger.error(f"Initial security checks failed: {str(e)}")
    
    async def _validate_fingerprint(
        self,
        session: SecureSession,
        current_fingerprint: SessionFingerprint
    ) -> bool:
        """Validate session fingerprint for consistency"""
        try:
            original_fingerprint = session.fingerprint
            
            # Calculate fingerprint similarity
            similarity = self._calculate_fingerprint_similarity(
                original_fingerprint,
                current_fingerprint
            )
            
            # Allow some variation but not too much
            if similarity < self.fingerprint_change_threshold:
                self.logger.warning(
                    f"Fingerprint change detected: similarity {similarity:.2f}"
                )
                return False
            
            # Check critical components
            if original_fingerprint.ip_address != current_fingerprint.ip_address:
                await self._handle_ip_change(session, current_fingerprint.ip_address)
            
            if original_fingerprint.user_agent != current_fingerprint.user_agent:
                self.logger.warning("User agent change detected")
                # Allow user agent changes but log them
                session.suspicious_activity_count += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Fingerprint validation error: {str(e)}")
            return False
    
    def _calculate_fingerprint_similarity(
        self,
        fp1: SessionFingerprint,
        fp2: SessionFingerprint
    ) -> float:
        """Calculate similarity between two fingerprints"""
        components = [
            "user_agent", "screen_resolution", "timezone",
            "language", "platform", "browser", "device_type"
        ]
        
        matches = 0
        total = 0
        
        for component in components:
            val1 = getattr(fp1, component, None)
            val2 = getattr(fp2, component, None)
            
            if val1 is not None and val2 is not None:
                total += 1
                if val1 == val2:
                    matches += 1
        
        return matches / total if total > 0 else 0.0
    
    async def _handle_ip_change(self, session: SecureSession, new_ip: str):
        """Handle IP address change during session"""
        try:
            # Add to IP history
            if new_ip not in session.ip_history:
                session.ip_history.append(new_ip)
                session.location_changes += 1
                
                self.logger.info(f"IP change detected: {session.session_id}, new IP: {new_ip}")
                
                # Check if too many location changes
                if session.location_changes > self.max_location_changes:
                    await self._handle_suspicious_activity(session, "excessive_location_changes")
                
                # Check if new IP is suspicious
                if await self._is_suspicious_ip(new_ip):
                    await self._handle_suspicious_activity(session, "suspicious_ip_change")
                
        except Exception as e:
            self.logger.error(f"IP change handling failed: {str(e)}")
    
    async def _detect_suspicious_activity(
        self,
        session: SecureSession,
        current_fingerprint: SessionFingerprint
    ) -> bool:
        """Detect suspicious activity patterns"""
        try:
            suspicious_indicators = 0
            
            # Check rapid location changes
            if session.location_changes > 3:
                suspicious_indicators += 1
            
            # Check for automation patterns
            if await self._detect_automation_patterns(session):
                suspicious_indicators += 1
            
            # Check time-based anomalies
            if await self._detect_time_anomalies(session):
                suspicious_indicators += 1
            
            # Update suspicious activity count
            if suspicious_indicators > 0:
                session.suspicious_activity_count += suspicious_indicators
            
            return session.suspicious_activity_count >= self.suspicious_activity_threshold
            
        except Exception as e:
            self.logger.error(f"Suspicious activity detection failed: {str(e)}")
            return False
    
    async def _detect_automation_patterns(self, session: SecureSession) -> bool:
        """Detect automated/bot behavior patterns"""
        # Check user agent for bot indicators
        user_agent = session.fingerprint.user_agent.lower()
        bot_indicators = ["bot", "crawler", "spider", "scraper", "automated"]
        
        return any(indicator in user_agent for indicator in bot_indicators)
    
    async def _detect_time_anomalies(self, session: SecureSession) -> bool:
        """Detect time-based anomalies"""
        # Check for sessions at unusual hours (basic implementation)
        current_hour = datetime.utcnow().hour
        
        # Flag sessions between 2 AM and 5 AM as potentially suspicious
        return 2 <= current_hour <= 5
    
    async def _handle_suspicious_activity(self, session: SecureSession, reason: str):
        """Handle detected suspicious activity"""
        try:
            session.status = SessionStatus.SUSPICIOUS
            session.metadata[f"suspicious_reason"] = reason
            session.metadata[f"flagged_at"] = datetime.utcnow().isoformat()
            
            # Store updated session
            await self._store_session(session)
            
            # Log security event
            self.logger.warning(
                f"Suspicious activity flagged: {session.session_id}, reason: {reason}"
            )
            
            # Optionally revoke session for high-risk scenarios
            if reason in ["fingerprint_mismatch", "excessive_location_changes"]:
                await self.revoke_session(session.session_id, f"security_revocation_{reason}")
            
        except Exception as e:
            self.logger.error(f"Suspicious activity handling failed: {str(e)}")
    
    async def _update_session_activity(
        self,
        session: SecureSession,
        current_fingerprint: SessionFingerprint
    ):
        """Update session activity and extend expiration"""
        try:
            session.last_activity = datetime.utcnow()
            
            # Extend session expiration
            session.expires_at = datetime.utcnow() + timedelta(minutes=self.session_timeout_minutes)
            
            # Update fingerprint if needed
            if current_fingerprint.fingerprint_hash != session.fingerprint.fingerprint_hash:
                session.fingerprint = current_fingerprint
            
            # Store updated session
            await self._store_session(session)
            
        except Exception as e:
            self.logger.error(f"Session activity update failed: {str(e)}")
    
    async def _store_session(self, session: SecureSession):
        """Store session data"""
        try:
            # Cache for quick access
            cache_key = f"session:{session.session_id}"
            session_data = self._serialize_session(session)
            await self.cache.set(cache_key, session_data, expire=7200)  # 2 hours
            
            # Store in file (in production, use database)
            import os
            sessions_file = "/tmp/sessions.json"
            
            # Load existing sessions
            sessions_data = {}
            if os.path.exists(sessions_file):
                with open(sessions_file, 'r') as f:
                    sessions_data = json.load(f)
            
            # Add/update session
            sessions_data[session.session_id] = session_data
            
            # Save back to file
            with open(sessions_file, 'w') as f:
                json.dump(sessions_data, f, default=str)
                
        except Exception as e:
            self.logger.error(f"Session storage failed: {str(e)}")
            raise
    
    async def _get_session(self, session_id: str) -> Optional[SecureSession]:
        """Retrieve session data"""
        try:
            # Check cache first
            cache_key = f"session:{session_id}"
            cached_data = await self.cache.get(cache_key)
            
            if cached_data:
                return self._deserialize_session(cached_data)
            
            # Load from file
            import os
            sessions_file = "/tmp/sessions.json"
            
            if not os.path.exists(sessions_file):
                return None
            
            with open(sessions_file, 'r') as f:
                sessions_data = json.load(f)
            
            session_data = sessions_data.get(session_id)
            if session_data:
                session = self._deserialize_session(session_data)
                
                # Re-cache
                await self.cache.set(cache_key, session_data, expire=7200)
                
                return session
            
            return None
            
        except Exception as e:
            self.logger.error(f"Session retrieval failed: {str(e)}")
            return None
    
    async def _get_user_sessions(self, user_id: str) -> List[SecureSession]:
        """Get all sessions for a user"""
        try:
            import os
            sessions_file = "/tmp/sessions.json"
            
            if not os.path.exists(sessions_file):
                return []
            
            with open(sessions_file, 'r') as f:
                sessions_data = json.load(f)
            
            user_sessions = []
            for session_data in sessions_data.values():
                if session_data.get("user_id") == user_id:
                    session = self._deserialize_session(session_data)
                    user_sessions.append(session)
            
            return user_sessions
            
        except Exception as e:
            self.logger.error(f"Failed to get user sessions: {str(e)}")
            return []
    
    async def _get_active_user_sessions(self, user_id: str) -> List[SecureSession]:
        """Get active sessions for a user"""
        all_sessions = await self._get_user_sessions(user_id)
        return [s for s in all_sessions if s.status == SessionStatus.ACTIVE]
    
    async def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious"""
        try:
            # Check if IP is private/local
            ip = ipaddress.ip_address(ip_address)
            if ip.is_private or ip.is_loopback:
                return False
            
            # In production, check against threat intelligence feeds
            # For now, just return False
            return False
            
        except ValueError:
            return True  # Invalid IP is suspicious
    
    async def _get_country_from_ip(self, ip_address: str) -> str:
        """Get country code from IP address"""
        # In production, use GeoIP service
        # For now, return a mock country
        return "US"
    
    async def _enrich_fingerprint_data(self, session: SecureSession):
        """Enrich fingerprint data with parsed information"""
        try:
            ua_string = session.fingerprint.user_agent
            if ua_string:
                try:
                    ua = user_agents.parse(ua_string)
                    session.fingerprint.browser = f"{ua.browser.family} {ua.browser.version_string}"
                    session.fingerprint.device_type = "mobile" if ua.is_mobile else "desktop"
                    session.fingerprint.platform = ua.os.family
                except:
                    # If user_agents module not available, just log
                    self.logger.info("User agent parsing not available")
                    
        except Exception as e:
            self.logger.error(f"Fingerprint enrichment failed: {str(e)}")
    
    async def _mark_session_expired(self, session_id: str):
        """Mark session as expired"""
        try:
            session = await self._get_session(session_id)
            if session:
                session.status = SessionStatus.EXPIRED
                await self._store_session(session)
                
        except Exception as e:
            self.logger.error(f"Failed to mark session expired: {str(e)}")
    
    def _serialize_session(self, session: SecureSession) -> Dict[str, Any]:
        """Serialize session for storage"""
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "fingerprint": {
                "user_agent": session.fingerprint.user_agent,
                "ip_address": session.fingerprint.ip_address,
                "screen_resolution": session.fingerprint.screen_resolution,
                "timezone": session.fingerprint.timezone,
                "language": session.fingerprint.language,
                "platform": session.fingerprint.platform,
                "browser": session.fingerprint.browser,
                "device_type": session.fingerprint.device_type,
                "fingerprint_hash": session.fingerprint.fingerprint_hash
            },
            "security_level": session.security_level.value,
            "status": session.status.value,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "expires_at": session.expires_at.isoformat() if session.expires_at else None,
            "ip_history": session.ip_history,
            "location_changes": session.location_changes,
            "suspicious_activity_count": session.suspicious_activity_count,
            "metadata": session.metadata
        }
    
    def _deserialize_session(self, data: Dict[str, Any]) -> SecureSession:
        """Deserialize session from storage"""
        fp_data = data["fingerprint"]
        fingerprint = SessionFingerprint(
            user_agent=fp_data["user_agent"],
            ip_address=fp_data["ip_address"],
            screen_resolution=fp_data.get("screen_resolution"),
            timezone=fp_data.get("timezone"),
            language=fp_data.get("language"),
            platform=fp_data.get("platform"),
            browser=fp_data.get("browser"),
            device_type=fp_data.get("device_type")
        )
        
        session = SecureSession(
            session_id=data["session_id"],
            user_id=data["user_id"],
            fingerprint=fingerprint,
            security_level=SessionSecurityLevel(data["security_level"]),
            status=SessionStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None,
            ip_history=data["ip_history"],
            location_changes=data["location_changes"],
            suspicious_activity_count=data["suspicious_activity_count"],
            metadata=data["metadata"]
        )
        
        return session


# Utility functions
async def create_session_fingerprint(
    user_agent: str,
    ip_address: str,
    **kwargs
) -> SessionFingerprint:
    """Create session fingerprint from request data"""
    return SessionFingerprint(
        user_agent=user_agent,
        ip_address=ip_address,
        **kwargs
    )


async def validate_session_security(
    session_id: str,
    fingerprint: SessionFingerprint
) -> Tuple[bool, Optional[SecureSession]]:
    """Validate session security"""
    manager = SessionSecurityManager()
    return await manager.validate_session(session_id, fingerprint)