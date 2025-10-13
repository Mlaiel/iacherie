"""
🔐💼 SESSION MANAGER - ENTERPRISE SESSION MANAGEMENT MODULE 💼🔐
Enterprise Session Management for IA Chérie Platform
Copyright (C) 2024 IA Chérie Platform. All Rights Reserved.
"""

import logging
import secrets
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import threading

logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    """📋 Session Status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"

class SessionType(Enum):
    """🔄 Session Types"""
    WEB = "web"
    MOBILE = "mobile"
    API = "api"
    ADMIN = "admin"
    SERVICE = "service"

@dataclass
class SessionData:
    """💼 Session Data Structure"""
    session_id: str = ""
    user_id: str = ""
    username: str = ""
    session_type: SessionType = SessionType.WEB
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = None
    ip_address: str = ""
    user_agent: str = ""
    device_info: Dict[str, str] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    csrf_token: str = ""
    
    def __post_init__(self):
        if self.expires_at is None:
            # Default 24 hour expiration
            self.expires_at = self.created_at + timedelta(hours=24)
        if not self.csrf_token:
            self.csrf_token = secrets.token_urlsafe(32)

@dataclass
class SessionValidationResult:
    """✅ Session Validation Result"""
    is_valid: bool = False
    session_data: Optional[SessionData] = None
    error_message: str = ""
    should_refresh: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class SessionManager:
    """🔐💼 Enterprise Session Manager"""
    
    def __init__(self):
        self.initialized = False
        self.active_sessions: Dict[str, SessionData] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> set of session_ids
        self.session_lock = threading.RLock()
        self.cleanup_thread: Optional[threading.Thread] = None
        self.cleanup_running = False
        self.logger = logging.getLogger(f"{__name__}.SessionManager")
        
        # Session configuration
        self.default_expiration_hours = {
            SessionType.WEB: 24,
            SessionType.MOBILE: 168,  # 7 days
            SessionType.API: 8760,    # 1 year
            SessionType.ADMIN: 8,     # 8 hours
            SessionType.SERVICE: 8760  # 1 year
        }
        
        self.max_sessions_per_user = {
            SessionType.WEB: 5,
            SessionType.MOBILE: 3,
            SessionType.API: 10,
            SessionType.ADMIN: 2,
            SessionType.SERVICE: 1
        }
        
        self.session_refresh_threshold_minutes = 30
        self.cleanup_interval_minutes = 15
        
        self._initialize_manager()
        
    def _initialize_manager(self):
        """🔧 Initialize Session Manager"""
        try:
            # Start cleanup thread
            self._start_cleanup_thread()
            
            # Test session creation
            test_session = self.create_session(
                user_id="test_user",
                username="test",
                session_type=SessionType.WEB,
                ip_address="127.0.0.1"
            )
            
            if test_session and test_session.session_id:
                # Clean up test session
                self.revoke_session(test_session.session_id)
                
                self.initialized = True
                self.logger.info("🔐 Session Manager initialized successfully")
            else:
                raise Exception("Session creation test failed")
            
        except Exception as e:
            self.logger.error(f"❌ Session Manager initialization failed: {e}")
            self.initialized = False
    
    def _start_cleanup_thread(self):
        """🧹 Start Session Cleanup Thread"""
        try:
            if self.cleanup_thread and self.cleanup_thread.is_alive():
                return
            
            self.cleanup_running = True
            self.cleanup_thread = threading.Thread(
                target=self._cleanup_loop,
                daemon=True
            )
            self.cleanup_thread.start()
            
            self.logger.info("🧹 Session cleanup thread started")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup thread start failed: {e}")
    
    def _cleanup_loop(self):
        """🧹 Session Cleanup Loop"""
        while self.cleanup_running:
            try:
                self._cleanup_expired_sessions()
                time.sleep(self.cleanup_interval_minutes * 60)
                
            except Exception as e:
                self.logger.error(f"❌ Cleanup loop error: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def create_session(self, user_id: str, username: str, 
                      session_type: SessionType = SessionType.WEB,
                      ip_address: str = "", user_agent: str = "",
                      device_info: Optional[Dict[str, str]] = None,
                      permissions: Optional[List[str]] = None,
                      custom_expiration: Optional[datetime] = None) -> Optional[SessionData]:
        """🆕 Create New Session"""
        try:
            with self.session_lock:
                # Check session limits
                if not self._check_session_limits(user_id, session_type):
                    self.logger.warning(f"⚠️ Session limit exceeded for user: {user_id}")
                    return None
                
                # Generate session ID
                session_id = self._generate_session_id()
                
                # Calculate expiration
                if custom_expiration:
                    expires_at = custom_expiration
                else:
                    hours = self.default_expiration_hours.get(session_type, 24)
                    expires_at = datetime.utcnow() + timedelta(hours=hours)
                
                # Create session data
                session_data = SessionData(
                    session_id=session_id,
                    user_id=user_id,
                    username=username,
                    session_type=session_type,
                    expires_at=expires_at,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    device_info=device_info or {},
                    permissions=permissions or [],
                    metadata={
                        'created_from_ip': ip_address,
                        'creation_timestamp': time.time()
                    }
                )
                
                # Store session
                self.active_sessions[session_id] = session_data
                
                # Update user sessions index
                if user_id not in self.user_sessions:
                    self.user_sessions[user_id] = set()
                self.user_sessions[user_id].add(session_id)
                
                self.logger.info(f"🆕 Session created for user: {username} ({session_id[:8]}...)")
                return session_data
            
        except Exception as e:
            self.logger.error(f"❌ Session creation failed: {e}")
            return None
    
    def _generate_session_id(self) -> str:
        """🎫 Generate Unique Session ID"""
        while True:
            session_id = secrets.token_urlsafe(48)
            if session_id not in self.active_sessions:
                return session_id
    
    def _check_session_limits(self, user_id: str, session_type: SessionType) -> bool:
        """🔢 Check Session Limits"""
        try:
            if user_id not in self.user_sessions:
                return True
            
            # Count sessions of the same type
            user_session_ids = self.user_sessions[user_id]
            same_type_count = 0
            
            for session_id in user_session_ids:
                if session_id in self.active_sessions:
                    session = self.active_sessions[session_id]
                    if session.session_type == session_type and session.status == SessionStatus.ACTIVE:
                        same_type_count += 1
            
            max_allowed = self.max_sessions_per_user.get(session_type, 5)
            
            if same_type_count >= max_allowed:
                # Revoke oldest session of the same type
                self._revoke_oldest_session(user_id, session_type)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Session limit check failed: {e}")
            return True  # Allow on error
    
    def _revoke_oldest_session(self, user_id: str, session_type: SessionType):
        """🚫 Revoke Oldest Session of Type"""
        try:
            oldest_session = None
            oldest_time = datetime.utcnow()
            
            for session_id in self.user_sessions.get(user_id, set()):
                if session_id in self.active_sessions:
                    session = self.active_sessions[session_id]
                    if (session.session_type == session_type and 
                        session.status == SessionStatus.ACTIVE and
                        session.created_at < oldest_time):
                        oldest_session = session_id
                        oldest_time = session.created_at
            
            if oldest_session:
                self.revoke_session(oldest_session)
                self.logger.info(f"🚫 Revoked oldest session for user: {user_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Oldest session revocation failed: {e}")
    
    def validate_session(self, session_id: str, 
                        ip_address: Optional[str] = None,
                        user_agent: Optional[str] = None) -> SessionValidationResult:
        """✅ Validate Session"""
        try:
            with self.session_lock:
                if session_id not in self.active_sessions:
                    return SessionValidationResult(
                        is_valid=False,
                        error_message="Session not found"
                    )
                
                session = self.active_sessions[session_id]
                
                # Check session status
                if session.status != SessionStatus.ACTIVE:
                    return SessionValidationResult(
                        is_valid=False,
                        error_message=f"Session is {session.status.value}"
                    )
                
                # Check expiration
                if datetime.utcnow() > session.expires_at:
                    session.status = SessionStatus.EXPIRED
                    return SessionValidationResult(
                        is_valid=False,
                        error_message="Session has expired"
                    )
                
                # IP address validation (optional)
                if ip_address and session.ip_address and ip_address != session.ip_address:
                    self.logger.warning(f"⚠️ IP address mismatch for session: {session_id[:8]}...")
                    # Could be a security concern, but not necessarily invalid
                
                # Update last accessed time
                session.last_accessed = datetime.utcnow()
                
                # Check if session should be refreshed
                time_since_creation = datetime.utcnow() - session.created_at
                should_refresh = time_since_creation.total_seconds() > (self.session_refresh_threshold_minutes * 60)
                
                result = SessionValidationResult(
                    is_valid=True,
                    session_data=session,
                    should_refresh=should_refresh,
                    metadata={
                        'time_since_creation': time_since_creation.total_seconds(),
                        'time_until_expiry': (session.expires_at - datetime.utcnow()).total_seconds()
                    }
                )
                
                self.logger.debug(f"✅ Session validated: {session.username} ({session_id[:8]}...)")
                return result
            
        except Exception as e:
            self.logger.error(f"❌ Session validation failed: {e}")
            return SessionValidationResult(
                is_valid=False,
                error_message=f"Validation error: {str(e)}"
            )
    
    def refresh_session(self, session_id: str, 
                       extend_hours: Optional[int] = None) -> bool:
        """🔄 Refresh Session"""
        try:
            with self.session_lock:
                if session_id not in self.active_sessions:
                    return False
                
                session = self.active_sessions[session_id]
                
                if session.status != SessionStatus.ACTIVE:
                    return False
                
                # Extend expiration
                if extend_hours:
                    hours = extend_hours
                else:
                    hours = self.default_expiration_hours.get(session.session_type, 24)
                
                session.expires_at = datetime.utcnow() + timedelta(hours=hours)
                session.last_accessed = datetime.utcnow()
                
                # Generate new CSRF token
                session.csrf_token = secrets.token_urlsafe(32)
                
                self.logger.info(f"🔄 Session refreshed: {session.username} ({session_id[:8]}...)")
                return True
            
        except Exception as e:
            self.logger.error(f"❌ Session refresh failed: {e}")
            return False
    
    def revoke_session(self, session_id: str) -> bool:
        """🚫 Revoke Session"""
        try:
            with self.session_lock:
                if session_id not in self.active_sessions:
                    return False
                
                session = self.active_sessions[session_id]
                session.status = SessionStatus.REVOKED
                
                # Remove from user sessions index
                if session.user_id in self.user_sessions:
                    self.user_sessions[session.user_id].discard(session_id)
                
                # Remove from active sessions
                del self.active_sessions[session_id]
                
                self.logger.info(f"🚫 Session revoked: {session.username} ({session_id[:8]}...)")
                return True
            
        except Exception as e:
            self.logger.error(f"❌ Session revocation failed: {e}")
            return False
    
    def revoke_all_user_sessions(self, user_id: str, 
                                except_session_id: Optional[str] = None) -> int:
        """🚫 Revoke All User Sessions"""
        try:
            with self.session_lock:
                if user_id not in self.user_sessions:
                    return 0
                
                session_ids_to_revoke = list(self.user_sessions[user_id])
                revoked_count = 0
                
                for session_id in session_ids_to_revoke:
                    if session_id != except_session_id:
                        if self.revoke_session(session_id):
                            revoked_count += 1
                
                self.logger.info(f"🚫 Revoked {revoked_count} sessions for user: {user_id}")
                return revoked_count
            
        except Exception as e:
            self.logger.error(f"❌ User sessions revocation failed: {e}")
            return 0
    
    def get_user_sessions(self, user_id: str) -> List[SessionData]:
        """📋 Get User Sessions"""
        try:
            with self.session_lock:
                if user_id not in self.user_sessions:
                    return []
                
                sessions = []
                for session_id in self.user_sessions[user_id]:
                    if session_id in self.active_sessions:
                        sessions.append(self.active_sessions[session_id])
                
                return sessions
            
        except Exception as e:
            self.logger.error(f"❌ User sessions retrieval failed: {e}")
            return []
    
    def _cleanup_expired_sessions(self):
        """🧹 Cleanup Expired Sessions"""
        try:
            with self.session_lock:
                current_time = datetime.utcnow()
                expired_sessions = []
                
                for session_id, session in self.active_sessions.items():
                    if current_time > session.expires_at:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    session = self.active_sessions[session_id]
                    session.status = SessionStatus.EXPIRED
                    
                    # Remove from user sessions index
                    if session.user_id in self.user_sessions:
                        self.user_sessions[session.user_id].discard(session_id)
                    
                    # Remove from active sessions
                    del self.active_sessions[session_id]
                
                if expired_sessions:
                    self.logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
            
        except Exception as e:
            self.logger.error(f"❌ Session cleanup failed: {e}")
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """📊 Get Session Statistics"""
        try:
            with self.session_lock:
                stats = {
                    'total_active_sessions': len(self.active_sessions),
                    'unique_users': len(self.user_sessions),
                    'sessions_by_type': {},
                    'sessions_by_status': {},
                    'average_session_age_minutes': 0
                }
                
                # Count by type and status
                session_ages = []
                
                for session in self.active_sessions.values():
                    # By type
                    session_type = session.session_type.value
                    if session_type not in stats['sessions_by_type']:
                        stats['sessions_by_type'][session_type] = 0
                    stats['sessions_by_type'][session_type] += 1
                    
                    # By status
                    session_status = session.status.value
                    if session_status not in stats['sessions_by_status']:
                        stats['sessions_by_status'][session_status] = 0
                    stats['sessions_by_status'][session_status] += 1
                    
                    # Age calculation
                    age_minutes = (datetime.utcnow() - session.created_at).total_seconds() / 60
                    session_ages.append(age_minutes)
                
                if session_ages:
                    stats['average_session_age_minutes'] = sum(session_ages) / len(session_ages)
                
                return stats
            
        except Exception as e:
            self.logger.error(f"❌ Session statistics generation failed: {e}")
            return {}
    
    def stop_cleanup(self):
        """🛑 Stop Cleanup Thread"""
        try:
            self.cleanup_running = False
            if self.cleanup_thread:
                self.cleanup_thread.join(timeout=5.0)
            
            self.logger.info("🛑 Session cleanup stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup stop failed: {e}")
    
    def is_initialized(self) -> bool:
        """✅ Check Initialization Status"""
        return self.initialized

# Instance globale
session_manager = SessionManager()

if session_manager.is_initialized():
    logger.info("🚀💯🔥 SESSION MANAGER MODULE LOADED - SESSION FOUNDATION! 🔥💯🚀")
    logger.info("✅ Enterprise session management with expiration and cleanup operational!")
    logger.info("🏆 CRITICAL SESSION MODULE FOR 100% SUCCESS ACHIEVED!")

__all__ = [
    'SessionManager',
    'SessionData',
    'SessionValidationResult',
    'SessionStatus',
    'SessionType',
    'session_manager',
]