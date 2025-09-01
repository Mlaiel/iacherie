"""Session Management Database Components

Enterprise session management with distributed storage, security validation,
and real-time monitoring for multi-format creator authentication.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

import uuid
import json
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


class SessionStatus(Enum):
    """
Session status enumeration"""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class DeviceType(Enum):
    """Device type enumeration"""

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    API = "api"
    EMBEDDED = "embedded"


@dataclass
class SessionInfo:
    """Session information data structure"""
    session_id: str
    user_id: str
    creator_type: str
    device_type: DeviceType
    ip_address: str
    user_agent: str
    location: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    last_activity: datetime = None
    expires_at: datetime = None
    status: SessionStatus = SessionStatus.ACTIVE
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.last_activity is None:
            self.last_activity = datetime.now(timezone.utc)
        if self.expires_at is None:
            self.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)


class SessionStore(Base):
    """
    Database model for session storage with comprehensive tracking
    """
    __tablename__ = "session_store"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(128), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_type = Column(String(50), nullable=False)  # musician, blogger, photographer, etc.
    device_type = Column(String(20), nullable=False)
    device_fingerprint = Column(String(128))
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text)
    location_data = Column(JSON)
    
    # Security tracking
    session_token_hash = Column(String(128), nullable=False)
    csrf_token = Column(String(128))
    security_level = Column(Integer, default=1)
    risk_score = Column(Integer, default=0)
    
    # Session lifecycle
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    renewed_count = Column(Integer, default=0)
    
    # Status and metadata
    status = Column(String(20), default="active", nullable=False)
    termination_reason = Column(String(100))
    session_data = Column(JSON)  # Additional session context
    
    # Performance tracking
    api_calls_count = Column(Integer, default=0)
    data_transfer_mb = Column(Integer, default=0)
    last_api_call = Column(DateTime(timezone=True))
    
    # Audit trail
    login_method = Column(String(50))  # password, oauth, mfa, etc.
    concurrent_sessions = Column(Integer, default=1)
    previous_session_id = Column(String(128))
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_session_user_active', 'user_id', 'status'),
        Index('idx_session_expires', 'expires_at'),
        Index('idx_session_last_activity', 'last_activity'),
        Index('idx_session_creator_type', 'creator_type'),
        Index('idx_session_ip_address', 'ip_address'),
    )


class SessionManager:
    """
    Enterprise session manager with Redis caching and PostgreSQL persistence
    """
    
    def __init__(self, db_session: Session, redis_client: redis.Redis):
        self.db_session = db_session
        self.redis_client = redis_client
        self.session_timeout = timedelta(hours=24)
        self.max_concurrent_sessions = 5
        self.security_config = {
            'max_login_attempts': 5,
            'lockout_duration': timedelta(minutes=30),
            'session_renewal_threshold': timedelta(hours=2)
        }
    
    def create_session(
        self,
        user_id: str,
        creator_type: str,
        device_info: Dict[str, Any],
        security_context: Dict[str, Any]
    ) -> SessionInfo:
        """
        Create new authenticated session with comprehensive tracking
        
        Args:
            user_id: Unique user identifier
            creator_type: Type of creator (musician, blogger, etc.)
            device_info: Device and browser information
            security_context: Security validation context
            
        Returns:
            SessionInfo: Created session information
        """
        # Generate secure session ID
        session_id = self._generate_secure_session_id(user_id)
        
        # Create session token
        session_token = self._generate_session_token(session_id, user_id)
        token_hash = hashlib.sha256(session_token.encode()).hexdigest()
        
        # Check concurrent session limits
        self._enforce_concurrent_session_limits(user_id)
        
        # Create session data
        session_info = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            creator_type=creator_type,
            device_type=DeviceType(device_info.get('type', 'desktop')),
            ip_address=device_info.get('ip_address'),
            user_agent=device_info.get('user_agent'),
            location=device_info.get('location')
        )
        
        # Store in database
        session_record = SessionStore(
            session_id=session_id,
            user_id=user_id,
            creator_type=creator_type,
            device_type=session_info.device_type.value,
            device_fingerprint=device_info.get('fingerprint'),
            ip_address=session_info.ip_address,
            user_agent=session_info.user_agent,
            location_data=session_info.location,
            session_token_hash=token_hash,
            csrf_token=self._generate_csrf_token(),
            security_level=security_context.get('level', 1),
            risk_score=security_context.get('risk_score', 0),
            expires_at=session_info.expires_at,
            login_method=security_context.get('method', 'password'),
            session_data={'token': session_token}
        )
        
        self.db_session.add(session_record)
        self.db_session.commit()
        
        # Cache in Redis for fast access
        self._cache_session_in_redis(session_info, session_token)
        
        return session_info
    
    def validate_session(self, session_id: str, token: str) -> Optional[SessionInfo]:
        """
        Validate session with comprehensive security checks
        
        Args:
            session_id: Session identifier
            token: Session token
            
        Returns:
            SessionInfo if valid, None otherwise
        """
        # First check Redis cache
        cached_session = self._get_cached_session(session_id)
        if cached_session and self._verify_session_token(cached_session, token):
            self._update_activity(session_id)
            return cached_session
        
        # Fallback to database
        session_record = self.db_session.query(SessionStore).filter(
            SessionStore.session_id == session_id,
            SessionStore.status == "active",
            SessionStore.expires_at > datetime.now(timezone.utc),
            SessionStore.is_active == True
        ).first()
        
        if not session_record:
            return None
        
        # Verify token hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if session_record.session_token_hash != token_hash:
            self._log_security_violation(session_id, "Invalid token")
            return None
        
        # Create session info
        session_info = SessionInfo(
            session_id=session_record.session_id,
            user_id=str(session_record.user_id),
            creator_type=session_record.creator_type,
            device_type=DeviceType(session_record.device_type),
            ip_address=session_record.ip_address,
            user_agent=session_record.user_agent,
            location=session_record.location_data,
            created_at=session_record.created_at,
            last_activity=session_record.last_activity,
            expires_at=session_record.expires_at,
            status=SessionStatus(session_record.status)
        )
        
        # Re-cache in Redis
        self._cache_session_in_redis(session_info, token)
        
        # Update activity
        self._update_activity(session_id)
        
        return session_info
    
    def renew_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Renew session expiration with security validation
        
        Args:
            session_id: Session to renew
            
        Returns:
            Updated SessionInfo or None if renewal failed
        """
        session_record = self.db_session.query(SessionStore).filter(
            SessionStore.session_id == session_id,
            SessionStore.status == "active"
        ).first()
        
        if not session_record:
            return None
        
        # Check if renewal is allowed
        time_since_creation = datetime.now(timezone.utc) - session_record.created_at
        if time_since_creation > self.security_config['session_renewal_threshold']:
            # Require re-authentication for old sessions
            return None
        
        # Extend expiration
        new_expiration = datetime.now(timezone.utc) + self.session_timeout
        session_record.expires_at = new_expiration
        session_record.renewed_count += 1
        session_record.last_activity = datetime.now(timezone.utc)
        
        self.db_session.commit()
        
        # Update cache
        session_info = self._build_session_info_from_record(session_record)
        session_token = session_record.session_data.get('token')
        self._cache_session_in_redis(session_info, session_token)
        
        return session_info
    
    def terminate_session(self, session_id: str, reason: str = "user_logout") -> bool:
        """
        Terminate session with cleanup
        
        Args:
            session_id: Session to terminate
            reason: Termination reason
            
        Returns:
            Success status
        """
        session_record = self.db_session.query(SessionStore).filter(
            SessionStore.session_id == session_id
        ).first()
        
        if not session_record:
            return False
        
        # Update database
        session_record.status = "terminated"
        session_record.termination_reason = reason
        session_record.is_active = False
        
        self.db_session.commit()
        
        # Remove from cache
        self.redis_client.delete(f"session:{session_id}")
        
        return True
    
    def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[SessionInfo]:
        """
        Get all sessions for a user
        
        Args:
            user_id: User identifier
            active_only: Return only active sessions
            
        Returns:
            List of user sessions
        """
        query = self.db_session.query(SessionStore).filter(
            SessionStore.user_id == user_id
        )
        
        if active_only:
            query = query.filter(
                SessionStore.status == "active",
                SessionStore.expires_at > datetime.now(timezone.utc)
            )
        
        sessions = query.order_by(SessionStore.last_activity.desc()).all()
        
        return [self._build_session_info_from_record(session) for session in sessions]
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions
        
        Returns:
            Number of sessions cleaned up
        """
        current_time = datetime.now(timezone.utc)
        
        # Update expired sessions in database
        expired_count = self.db_session.query(SessionStore).filter(
            SessionStore.expires_at <= current_time,
            SessionStore.status == "active"
        ).update({
            'status': 'expired',
            'is_active': False
        })
        
        self.db_session.commit()
        
        # Clean up Redis cache
        # This would require scanning keys, implementation depends on Redis setup
        
        return expired_count
    
    def get_session_analytics(
        self,
        time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        Get session analytics for monitoring
        
        Args:
            time_period: Analysis time period
            
        Returns:
            Analytics data
        """
        start_time = datetime.now(timezone.utc) - time_period
        
        # Active sessions
        active_sessions = self.db_session.query(SessionStore).filter(
            SessionStore.status == "active",
            SessionStore.created_at >= start_time
        ).count()
        
        # Sessions by creator type
        creator_type_stats = self.db_session.query(
            SessionStore.creator_type,
            self.db_session.query(SessionStore).filter(
                SessionStore.creator_type == SessionStore.creator_type,
                SessionStore.created_at >= start_time
            ).count().label('count')
        ).group_by(SessionStore.creator_type).all()
        
        # Device type distribution
        device_stats = self.db_session.query(
            SessionStore.device_type,
            self.db_session.query(SessionStore).filter(
                SessionStore.device_type == SessionStore.device_type,
                SessionStore.created_at >= start_time
            ).count().label('count')
        ).group_by(SessionStore.device_type).all()
        
        return {
            'active_sessions': active_sessions,
            'creator_type_distribution': dict(creator_type_stats),
            'device_type_distribution': dict(device_stats),
            'analysis_period': time_period.total_seconds()
        }
    
    def _generate_secure_session_id(self, user_id: str) -> str:
        """Generate cryptographically secure session ID"""
        timestamp = str(datetime.now(timezone.utc).timestamp())
        random_data = uuid.uuid4().hex
        combined = f"{user_id}:{timestamp}:{random_data}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _generate_session_token(self, session_id: str, user_id: str) -> str:
        """Generate secure session token"""
        secret_data = f"{session_id}:{user_id}:{uuid.uuid4().hex}"
        return hashlib.sha256(secret_data.encode()).hexdigest()
    
    def _generate_csrf_token(self) -> str:
        """Generate CSRF protection token"""
        return hashlib.sha256(uuid.uuid4().hex.encode()).hexdigest()[:32]
    
    def _enforce_concurrent_session_limits(self, user_id: str):
        """
Enforce maximum concurrent sessions per user"""
        active_sessions = self.db_session.query(SessionStore).filter(
            SessionStore.user_id == user_id,
            SessionStore.status == "active",
            SessionStore.expires_at > datetime.now(timezone.utc)
        ).order_by(SessionStore.last_activity.desc()).all()
        
        if len(active_sessions) >= self.max_concurrent_sessions:
            # Terminate oldest sessions
            sessions_to_terminate = active_sessions[self.max_concurrent_sessions-1:]
            for session in sessions_to_terminate:
                self.terminate_session(session.session_id, "concurrent_limit_exceeded")
    
    def _cache_session_in_redis(self, session_info: SessionInfo, token: str):
        """Cache session data in Redis"""
        cache_data = asdict(session_info)
        cache_data['token'] = token
        cache_data['created_at'] = session_info.created_at.isoformat()
        cache_data['last_activity'] = session_info.last_activity.isoformat()
        cache_data['expires_at'] = session_info.expires_at.isoformat()
        cache_data['device_type'] = session_info.device_type.value
        cache_data['status'] = session_info.status.value
        
        # Cache with expiration
        ttl = int((session_info.expires_at - datetime.now(timezone.utc)).total_seconds())
        self.redis_client.setex(
            f"session:{session_info.session_id}",
            ttl,
            json.dumps(cache_data)
        )
    
    def _get_cached_session(self, session_id: str) -> Optional[SessionInfo]:
        """Retrieve session from Redis cache"""
        cached_data = self.redis_client.get(f"session:{session_id}")
        if not cached_data:
            return None
        
        try:
            data = json.loads(cached_data)
            return SessionInfo(
                session_id=data['session_id'],
                user_id=data['user_id'],
                creator_type=data['creator_type'],
                device_type=DeviceType(data['device_type']),
                ip_address=data['ip_address'],
                user_agent=data['user_agent'],
                location=data.get('location'),
                created_at=datetime.fromisoformat(data['created_at']),
                last_activity=datetime.fromisoformat(data['last_activity']),
                expires_at=datetime.fromisoformat(data['expires_at']),
                status=SessionStatus(data['status'])
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None
    
    def _verify_session_token(self, session_info: SessionInfo, token: str) -> bool:
        """Verify session token against cached data"""
        cached_data = self.redis_client.get(f"session:{session_info.session_id}")
        if not cached_data:
            return False
        
        try:
            data = json.loads(cached_data)
            return data.get('token') == token
        except json.JSONDecodeError:
            return False
    
    def _update_activity(self, session_id: str):
        """Update last activity timestamp"""
        current_time = datetime.now(timezone.utc)
        
        # Update database
        self.db_session.query(SessionStore).filter(
            SessionStore.session_id == session_id
        ).update({
            'last_activity': current_time,
            'api_calls_count': SessionStore.api_calls_count + 1,
            'last_api_call': current_time
        })
        self.db_session.commit()
        
        # Update cache if exists
        cached_data = self.redis_client.get(f"session:{session_id}")
        if cached_data:
            try:
                data = json.loads(cached_data)
                data['last_activity'] = current_time.isoformat()
                ttl = self.redis_client.ttl(f"session:{session_id}")
                if ttl > 0:
                    self.redis_client.setex(
                        f"session:{session_id}",
                        ttl,
                        json.dumps(data)
                    )
            except json.JSONDecodeError:
                pass
    
    def _build_session_info_from_record(self, record: SessionStore) -> SessionInfo:
        """Build SessionInfo from database record"""
        return SessionInfo(
            session_id=record.session_id,
            user_id=str(record.user_id),
            creator_type=record.creator_type,
            device_type=DeviceType(record.device_type),
            ip_address=record.ip_address,
            user_agent=record.user_agent,
            location=record.location_data,
            created_at=record.created_at,
            last_activity=record.last_activity,
            expires_at=record.expires_at,
            status=SessionStatus(record.status)
        )
    
    def _log_security_violation(self, session_id: str, violation_type: str):
        """
Log security violations for monitoring"""
        # Implementation would integrate with security monitoring system
        pass
