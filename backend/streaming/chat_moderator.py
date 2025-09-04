"""Chat Moderation System
=======================

Advanced AI-powered chat moderation system for live streaming with real-time
content filtering, user behavior analysis, and automated moderation actions.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.

PROJECT TEAM SPECIALTIES:
- Lead Dev IA & ML Engineer: Advanced AI/ML algorithms and model integration
- Backend Senior Developer: Enterprise architecture and scalable systems
- DBA & Data Engineer: Database optimization and data pipeline management  
- Security Specialist: Content protection and security validation
- DevOps Engineer: Infrastructure automation and deployment
- Audio/Video Specialist: Multimedia processing and codec optimization
"""

import asyncio
import json
import uuid
import re
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum, IntEnum
import redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()
logger = logging.getLogger(__name__)


class ModerationAction(Enum):
    """Chat moderation actions"""
    ALLOW = "allow"
    WARN = "warn"
    TIMEOUT = "timeout"
    DELETE = "delete"
    BAN_TEMPORARY = "ban_temporary"
    BAN_PERMANENT = "ban_permanent"
    SHADOWBAN = "shadowban"


class ViolationType(Enum):
    """Types of chat violations"""
    SPAM = "spam"
    PROFANITY = "profanity"
    HARASSMENT = "harassment"
    HATE_SPEECH = "hate_speech"
    SEXUAL_CONTENT = "sexual_content"
    VIOLENCE = "violence"
    SELF_PROMOTION = "self_promotion"
    EXCESSIVE_CAPS = "excessive_caps"
    REPETITIVE_MESSAGES = "repetitive_messages"
    SUSPICIOUS_LINKS = "suspicious_links"
    IMPERSONATION = "impersonation"


class SeverityLevel(IntEnum):
    """Violation severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    SEVERE = 4
    CRITICAL = 5


class UserRole(Enum):
    """User roles for moderation"""
    VIEWER = "viewer"
    SUBSCRIBER = "subscriber"
    VIP = "vip"
    MODERATOR = "moderator"
    OWNER = "owner"


@dataclass
class ModerationRule:
    """Individual moderation rule"""
    rule_id: str
    name: str
    description: str
    violation_type: ViolationType
    severity: SeverityLevel
    action: ModerationAction
    patterns: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    regex_patterns: List[str] = field(default_factory=list)
    threshold_count: int = 1
    time_window_minutes: int = 60
    applies_to_roles: List[UserRole] = field(default_factory=lambda: [UserRole.VIEWER])
    is_enabled: bool = True


@dataclass
class ModerationConfig:
    """Chat moderation configuration"""
    enabled: bool = True
    auto_moderation: bool = True
    strict_mode: bool = False
    allow_links: bool = True
    allow_emotes: bool = True
    max_message_length: int = 500
    max_caps_percentage: float = 0.7
    spam_detection_sensitivity: float = 0.8
    timeout_durations: Dict[SeverityLevel, int] = field(default_factory=lambda: {
        SeverityLevel.LOW: 60,      # 1 minute
        SeverityLevel.MEDIUM: 300,  # 5 minutes
        SeverityLevel.HIGH: 1800,   # 30 minutes
        SeverityLevel.SEVERE: 3600, # 1 hour
        SeverityLevel.CRITICAL: 86400  # 24 hours
    })
    trusted_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    custom_rules: List[ModerationRule] = field(default_factory=list)


@dataclass
class ChatMessage:
    """Chat message data structure"""
    message_id: str
    stream_id: str
    user_id: str
    username: str
    user_role: UserRole
    content: str
    timestamp: datetime
    is_deleted: bool = False
    moderation_score: float = 0.0
    violations: List[ViolationType] = field(default_factory=list)
    action_taken: Optional[ModerationAction] = None
    moderator_id: Optional[str] = None


@dataclass
class UserModerationHistory:
    """User's moderation history"""
    user_id: str
    username: str
    total_violations: int = 0
    violation_counts: Dict[ViolationType, int] = field(default_factory=dict)
    last_violation: Optional[datetime] = None
    timeout_count: int = 0
    ban_count: int = 0
    warning_count: int = 0
    is_shadowbanned: bool = False
    shadowban_until: Optional[datetime] = None
    is_banned: bool = False
    ban_until: Optional[datetime] = None
    trust_score: float = 1.0  # 0-1 scale


class ChatModeration(Base):
    """Database model for chat moderation logs"""
    __tablename__ = "chat_moderation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stream_id = Column(String(255), nullable=False, index=True)
    message_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    username = Column(String(255), nullable=False)
    
    # Message content
    original_content = Column(Text, nullable=False)
    processed_content = Column(Text)
    
    # Moderation details
    violations = Column(ARRAY(String), default=list)
    severity = Column(Integer)
    action_taken = Column(String(50))
    moderation_score = Column(Float, default=0.0)
    
    # Moderator info
    moderator_id = Column(String(255))
    is_automated = Column(Boolean, default=True)
    
    # Metadata
    detection_rules = Column(JSON, default=list)
    additional_data = Column(JSON, default=dict)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UserModerationRecord(Base):
    """Database model for user moderation records"""
    __tablename__ = "user_moderation_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    username = Column(String(255), nullable=False)
    stream_id = Column(String(255), nullable=False, index=True)
    
    # Moderation statistics
    total_violations = Column(Integer, default=0)
    violation_counts = Column(JSON, default=dict)
    timeout_count = Column(Integer, default=0)
    ban_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    
    # Status
    is_shadowbanned = Column(Boolean, default=False)
    shadowban_until = Column(DateTime(timezone=True))
    is_banned = Column(Boolean, default=False)
    ban_until = Column(DateTime(timezone=True))
    trust_score = Column(Float, default=1.0)
    
    # Timestamps
    last_violation = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ChatModerator:
    """Advanced AI-powered chat moderation system"""
    
    def __init__(self, redis_client: Any, db_session: Session):
        self.redis = redis_client
        self.db = db_session
        self.active_streams: Dict[str, ModerationConfig] = {}
        self.user_histories: Dict[str, UserModerationHistory] = {}
        self.message_cache: Dict[str, List[ChatMessage]] = {}
        self.profanity_list = self._load_profanity_list()
        self.spam_patterns = self._load_spam_patterns()
        self.is_running = False
        
    async def start_moderator(self):
        """Start the chat moderation system"""
        self.is_running = True
        logger.info("Chat moderation system started")
        
        # Start background tasks
        asyncio.create_task(self._cleanup_expired_bans())
        asyncio.create_task(self._update_user_trust_scores())
        asyncio.create_task(self._message_analyzer())
        
    async def stop_moderator(self):
        """Stop the chat moderation system"""
        self.is_running = False
        logger.info("Chat moderation system stopped")
        
    async def configure_stream_moderation(
        self,
        stream_id: str,
        config: ModerationConfig
    ) -> bool:
        """Configure moderation for a stream"""
        try:
            self.active_streams[stream_id] = config
            
            # Store configuration in Redis
            await self.redis.hset(
                f"moderation_config:{stream_id}",
                mapping={
                    "config": json.dumps(asdict(config), default=str),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Initialize message cache for stream
            self.message_cache[stream_id] = []
            
            logger.info(f"Moderation configured for stream: {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure moderation for stream {stream_id}: {str(e)}")
            return False
            
    async def moderate_message(
        self,
        stream_id: str,
        message: ChatMessage
    ) -> Tuple[ModerationAction, List[ViolationType], float]:
        """Moderate a chat message and return action, violations, and score"""
        try:
            config = self.active_streams.get(stream_id)
            if not config or not config.enabled:
                return ModerationAction.ALLOW, [], 0.0
                
            # Skip moderation for certain roles
            if message.user_role in [UserRole.OWNER, UserRole.MODERATOR]:
                return ModerationAction.ALLOW, [], 0.0
                
            # Get user history
            user_history = await self._get_user_history(message.user_id, stream_id)
            
            # Analyze message content
            violations, score = await self._analyze_message_content(message, config, user_history)
            
            # Determine action based on violations and user history
            action = await self._determine_moderation_action(
                violations, score, user_history, config
            )
            
            # Execute moderation action
            if action != ModerationAction.ALLOW:
                await self._execute_moderation_action(
                    stream_id, message, action, violations, score
                )
                
            # Update user history
            await self._update_user_history(message.user_id, stream_id, violations, action)
            
            # Log moderation decision
            await self._log_moderation_decision(
                stream_id, message, action, violations, score
            )
            
            # Cache message for pattern analysis
            await self._cache_message(stream_id, message)
            
            return action, violations, score
            
        except Exception as e:
            logger.error(f"Failed to moderate message: {str(e)}")
            return ModerationAction.ALLOW, [], 0.0
            
    async def add_custom_rule(self, stream_id: str, rule: ModerationRule) -> bool:
        """Add a custom moderation rule for a stream"""
        try:
            config = self.active_streams.get(stream_id)
            if not config:
                return False
                
            config.custom_rules.append(rule)
            
            # Update Redis configuration
            await self.redis.hset(
                f"moderation_config:{stream_id}",
                "config", json.dumps(asdict(config), default=str)
            )
            
            logger.info(f"Custom rule added to stream {stream_id}: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add custom rule: {str(e)}")
            return False
            
    async def ban_user(
        self,
        stream_id: str,
        user_id: str,
        duration_minutes: Optional[int] = None,
        moderator_id: Optional[str] = None,
        reason: str = ""
    ) -> bool:
        """Ban a user from the stream"""
        try:
            user_history = await self._get_user_history(user_id, stream_id)
            
            # Set ban status
            user_history.is_banned = True
            if duration_minutes:
                user_history.ban_until = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
            else:
                user_history.ban_until = None  # Permanent ban
                
            user_history.ban_count += 1
            
            # Update database
            await self._update_user_moderation_record(user_history, stream_id)
            
            # Store ban in Redis for quick lookup
            ban_data = {
                "user_id": user_id,
                "banned_at": datetime.now(timezone.utc).isoformat(),
                "banned_until": user_history.ban_until.isoformat() if user_history.ban_until else "",
                "moderator_id": moderator_id or "",
                "reason": reason
            }
            
            await self.redis.hset(
                f"banned_users:{stream_id}",
                user_id, json.dumps(ban_data)
            )
            
            # Publish ban event
            await self.redis.publish(
                f"moderation_events:{stream_id}",
                json.dumps({
                    "type": "user_banned",
                    "user_id": user_id,
                    "duration_minutes": duration_minutes,
                    "reason": reason,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            )
            
            logger.info(f"User banned from stream {stream_id}: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ban user {user_id}: {str(e)}")
            return False
            
    async def unban_user(self, stream_id: str, user_id: str, moderator_id: Optional[str] = None) -> bool:
        """Unban a user from the stream"""
        try:
            user_history = await self._get_user_history(user_id, stream_id)
            
            # Remove ban status
            user_history.is_banned = False
            user_history.ban_until = None
            
            # Update database
            await self._update_user_moderation_record(user_history, stream_id)
            
            # Remove from Redis ban list
            await self.redis.hdel(f"banned_users:{stream_id}", user_id)
            
            # Publish unban event
            await self.redis.publish(
                f"moderation_events:{stream_id}",
                json.dumps({
                    "type": "user_unbanned",
                    "user_id": user_id,
                    "moderator_id": moderator_id or "",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            )
            
            logger.info(f"User unbanned from stream {stream_id}: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unban user {user_id}: {str(e)}")
            return False
            
    async def timeout_user(
        self,
        stream_id: str,
        user_id: str,
        duration_minutes: int,
        moderator_id: Optional[str] = None,
        reason: str = ""
    ) -> bool:
        """Timeout a user for a specified duration"""
        try:
            user_history = await self._get_user_history(user_id, stream_id)
            
            # Set timeout
            timeout_until = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
            user_history.timeout_count += 1
            
            # Store timeout in Redis
            timeout_data = {
                "user_id": user_id,
                "timeout_until": timeout_until.isoformat(),
                "moderator_id": moderator_id or "",
                "reason": reason
            }
            
            await self.redis.hset(
                f"timeouts:{stream_id}",
                user_id, json.dumps(timeout_data)
            )
            
            # Set expiration for automatic cleanup
            await self.redis.expire(f"timeouts:{stream_id}", duration_minutes * 60)
            
            # Update database
            await self._update_user_moderation_record(user_history, stream_id)
            
            # Publish timeout event
            await self.redis.publish(
                f"moderation_events:{stream_id}",
                json.dumps({
                    "type": "user_timeout",
                    "user_id": user_id,
                    "duration_minutes": duration_minutes,
                    "reason": reason,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            )
            
            logger.info(f"User timed out in stream {stream_id}: {user_id} for {duration_minutes} minutes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to timeout user {user_id}: {str(e)}")
            return False
            
    async def is_user_banned(self, stream_id: str, user_id: str) -> bool:
        """Check if a user is currently banned"""
        try:
            ban_data = await self.redis.hget(f"banned_users:{stream_id}", user_id)
            if not ban_data:
                return False
                
            ban_info = json.loads(ban_data)
            
            # Check if temporary ban has expired
            if ban_info.get("banned_until"):
                ban_until = datetime.fromisoformat(ban_info["banned_until"])
                if datetime.now(timezone.utc) > ban_until:
                    await self.unban_user(stream_id, user_id)
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to check ban status for user {user_id}: {str(e)}")
            return False
            
    async def is_user_timed_out(self, stream_id: str, user_id: str) -> bool:
        """Check if a user is currently timed out"""
        try:
            timeout_data = await self.redis.hget(f"timeouts:{stream_id}", user_id)
            if not timeout_data:
                return False
                
            timeout_info = json.loads(timeout_data)
            timeout_until = datetime.fromisoformat(timeout_info["timeout_until"])
            
            if datetime.now(timezone.utc) > timeout_until:
                await self.redis.hdel(f"timeouts:{stream_id}", user_id)
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to check timeout status for user {user_id}: {str(e)}")
            return False
            
    async def get_moderation_stats(self, stream_id: str) -> Dict[str, Any]:
        """Get moderation statistics for a stream"""
        try:
            # Get moderation logs from database
            moderation_logs = self.db.query(ChatModeration).filter(
                ChatModeration.stream_id == stream_id
            ).all()
            
            # Calculate statistics
            total_messages = len(moderation_logs)
            total_violations = sum(1 for log in moderation_logs if log.violations)
            
            violation_counts = {}
            action_counts = {}
            
            for log in moderation_logs:
                if log.violations:
                    for violation in log.violations:
                        violation_counts[violation] = violation_counts.get(violation, 0) + 1
                        
                if log.action_taken:
                    action_counts[log.action_taken] = action_counts.get(log.action_taken, 0) + 1
                    
            # Get current banned/timed out users
            banned_users = await self.redis.hlen(f"banned_users:{stream_id}")
            timed_out_users = await self.redis.hlen(f"timeouts:{stream_id}")
            
            return {
                "stream_id": stream_id,
                "total_messages_processed": total_messages,
                "total_violations": total_violations,
                "violation_rate": total_violations / total_messages if total_messages > 0 else 0,
                "violation_counts": violation_counts,
                "action_counts": action_counts,
                "currently_banned": banned_users,
                "currently_timed_out": timed_out_users,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get moderation stats for stream {stream_id}: {str(e)}")
            return {}
            
    def _load_profanity_list(self) -> Set[str]:
        """Load profanity word list"""
        # Basic profanity list (would be expanded in production)
        return {
            "badword1", "badword2", "inappropriate", "offensive",
            # This would be a comprehensive list in production
        }
        
    def _load_spam_patterns(self) -> List[str]:
        """Load spam detection patterns"""
        return [
            r"(https?://\S+)",  # URLs
            r"(\b\w*\.com\b)",  # Domain names
            r"(\b(?:buy|sell|cheap|free|win|winner)\b.*\b(?:now|today|click|visit)\b)",  # Promotional spam
            r"(.)\1{4,}",  # Repeated characters
            r"(\b\w+\b)(\s+\1){2,}",  # Repeated words
        ]
        
    async def _analyze_message_content(
        self,
        message: ChatMessage,
        config: ModerationConfig,
        user_history: UserModerationHistory
    ) -> Tuple[List[ViolationType], float]:
        """Analyze message content for violations"""
        violations = []
        score = 0.0
        content = message.content.lower()
        
        # Check message length
        if len(message.content) > config.max_message_length:
            violations.append(ViolationType.SPAM)
            score += 0.3
            
        # Check excessive caps
        if message.content:
            caps_ratio = sum(1 for c in message.content if c.isupper()) / len(message.content)
            if caps_ratio > config.max_caps_percentage:
                violations.append(ViolationType.EXCESSIVE_CAPS)
                score += 0.2
                
        # Check profanity
        if any(word in content for word in self.profanity_list):
            violations.append(ViolationType.PROFANITY)
            score += 0.8
            
        # Check spam patterns
        for pattern in self.spam_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(ViolationType.SPAM)
                score += 0.5
                break
                
        # Check for suspicious links
        if not config.allow_links and re.search(r"https?://", content):
            violations.append(ViolationType.SUSPICIOUS_LINKS)
            score += 0.4
            
        # Check for repetitive messages
        if await self._is_repetitive_message(message.stream_id, message.user_id, content):
            violations.append(ViolationType.REPETITIVE_MESSAGES)
            score += 0.3
            
        # Apply custom rules
        for rule in config.custom_rules:
            if not rule.is_enabled:
                continue
                
            if message.user_role not in rule.applies_to_roles:
                continue
                
            # Check keywords
            if any(keyword in content for keyword in rule.keywords):
                violations.append(rule.violation_type)
                score += rule.severity.value * 0.2
                
            # Check regex patterns
            for pattern in rule.regex_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append(rule.violation_type)
                    score += rule.severity.value * 0.2
                    
        # Adjust score based on user trust
        score *= (2.0 - user_history.trust_score)
        
        return violations, min(score, 1.0)
        
    async def _determine_moderation_action(
        self,
        violations: List[ViolationType],
        score: float,
        user_history: UserModerationHistory,
        config: ModerationConfig
    ) -> ModerationAction:
        """Determine appropriate moderation action"""
        if not violations:
            return ModerationAction.ALLOW
            
        # Check for severe violations
        severe_violations = {
            ViolationType.HATE_SPEECH,
            ViolationType.HARASSMENT,
            ViolationType.SEXUAL_CONTENT,
            ViolationType.VIOLENCE
        }
        
        if any(v in severe_violations for v in violations):
            if user_history.total_violations > 2:
                return ModerationAction.BAN_PERMANENT
            else:
                return ModerationAction.BAN_TEMPORARY
                
        # Score-based actions
        if score >= 0.8:
            if user_history.total_violations >= 5:
                return ModerationAction.BAN_TEMPORARY
            else:
                return ModerationAction.TIMEOUT
        elif score >= 0.6:
            if user_history.total_violations >= 3:
                return ModerationAction.TIMEOUT
            else:
                return ModerationAction.DELETE
        elif score >= 0.4:
            if user_history.total_violations >= 2:
                return ModerationAction.DELETE
            else:
                return ModerationAction.WARN
        else:
            return ModerationAction.DELETE if config.strict_mode else ModerationAction.WARN
            
    async def _execute_moderation_action(
        self,
        stream_id: str,
        message: ChatMessage,
        action: ModerationAction,
        violations: List[ViolationType],
        score: float
    ):
        """Execute the moderation action"""
        if action == ModerationAction.DELETE:
            await self._delete_message(stream_id, message.message_id)
            
        elif action == ModerationAction.WARN:
            await self._warn_user(stream_id, message.user_id, violations)
            
        elif action == ModerationAction.TIMEOUT:
            # Determine timeout duration based on severity
            severity = max(SeverityLevel.LOW, SeverityLevel(int(score * 5)))
            config = self.active_streams.get(stream_id)
            duration = config.timeout_durations.get(severity, 300) if config else 300
            await self.timeout_user(stream_id, message.user_id, duration)
            
        elif action in [ModerationAction.BAN_TEMPORARY, ModerationAction.BAN_PERMANENT]:
            duration = 1440 if action == ModerationAction.BAN_TEMPORARY else None  # 24 hours
            await self.ban_user(stream_id, message.user_id, duration)
            
        elif action == ModerationAction.SHADOWBAN:
            await self._shadowban_user(stream_id, message.user_id)
            
    async def _get_user_history(self, user_id: str, stream_id: str) -> UserModerationHistory:
        """Get user moderation history"""
        if user_id in self.user_histories:
            return self.user_histories[user_id]
            
        # Load from database
        record = self.db.query(UserModerationRecord).filter(
            UserModerationRecord.user_id == user_id,
            UserModerationRecord.stream_id == stream_id
        ).first()
        
        if record:
            history = UserModerationHistory(
                user_id=record.user_id,
                username=record.username,
                total_violations=record.total_violations,
                violation_counts=record.violation_counts or {},
                last_violation=record.last_violation,
                timeout_count=record.timeout_count,
                ban_count=record.ban_count,
                warning_count=record.warning_count,
                is_shadowbanned=record.is_shadowbanned,
                shadowban_until=record.shadowban_until,
                is_banned=record.is_banned,
                ban_until=record.ban_until,
                trust_score=record.trust_score
            )
        else:
            history = UserModerationHistory(user_id=user_id, username="")
            
        self.user_histories[user_id] = history
        return history
        
    async def _update_user_history(
        self,
        user_id: str,
        stream_id: str,
        violations: List[ViolationType],
        action: ModerationAction
    ):
        """Update user moderation history"""
        history = self.user_histories.get(user_id)
        if not history:
            return
            
        if violations:
            history.total_violations += len(violations)
            history.last_violation = datetime.now(timezone.utc)
            
            for violation in violations:
                history.violation_counts[violation.value] = history.violation_counts.get(violation.value, 0) + 1
                
        if action == ModerationAction.WARN:
            history.warning_count += 1
        elif action == ModerationAction.TIMEOUT:
            history.timeout_count += 1
        elif action in [ModerationAction.BAN_TEMPORARY, ModerationAction.BAN_PERMANENT]:
            history.ban_count += 1
            
        # Update trust score
        if violations:
            history.trust_score = max(0.0, history.trust_score - 0.1)
        else:
            history.trust_score = min(1.0, history.trust_score + 0.01)
            
        await self._update_user_moderation_record(history, stream_id)
        
    async def _update_user_moderation_record(self, history: UserModerationHistory, stream_id: str):
        """Update user moderation record in database"""
        try:
            record = self.db.query(UserModerationRecord).filter(
                UserModerationRecord.user_id == history.user_id,
                UserModerationRecord.stream_id == stream_id
            ).first()
            
            if record:
                record.total_violations = history.total_violations
                record.violation_counts = history.violation_counts
                record.last_violation = history.last_violation
                record.timeout_count = history.timeout_count
                record.ban_count = history.ban_count
                record.warning_count = history.warning_count
                record.is_shadowbanned = history.is_shadowbanned
                record.shadowban_until = history.shadowban_until
                record.is_banned = history.is_banned
                record.ban_until = history.ban_until
                record.trust_score = history.trust_score
                record.updated_at = datetime.now(timezone.utc)
            else:
                record = UserModerationRecord(
                    user_id=history.user_id,
                    username=history.username,
                    stream_id=stream_id,
                    total_violations=history.total_violations,
                    violation_counts=history.violation_counts,
                    last_violation=history.last_violation,
                    timeout_count=history.timeout_count,
                    ban_count=history.ban_count,
                    warning_count=history.warning_count,
                    is_shadowbanned=history.is_shadowbanned,
                    shadowban_until=history.shadowban_until,
                    is_banned=history.is_banned,
                    ban_until=history.ban_until,
                    trust_score=history.trust_score
                )
                self.db.add(record)
                
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update user moderation record: {str(e)}")
            self.db.rollback()
            
    async def _log_moderation_decision(
        self,
        stream_id: str,
        message: ChatMessage,
        action: ModerationAction,
        violations: List[ViolationType],
        score: float
    ):
        """Log moderation decision to database"""
        try:
            log_record = ChatModeration(
                stream_id=stream_id,
                message_id=message.message_id,
                user_id=message.user_id,
                username=message.username,
                original_content=message.content,
                violations=[v.value for v in violations],
                severity=int(score * 5) if violations else 0,
                action_taken=action.value,
                moderation_score=score,
                is_automated=True,
                timestamp=message.timestamp
            )
            
            self.db.add(log_record)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log moderation decision: {str(e)}")
            self.db.rollback()
            
    async def _cache_message(self, stream_id: str, message: ChatMessage):
        """Cache message for pattern analysis"""
        if stream_id not in self.message_cache:
            self.message_cache[stream_id] = []
            
        self.message_cache[stream_id].append(message)
        
        # Keep only last 100 messages per stream
        if len(self.message_cache[stream_id]) > 100:
            self.message_cache[stream_id] = self.message_cache[stream_id][-100:]
            
    async def _is_repetitive_message(self, stream_id: str, user_id: str, content: str) -> bool:
        """Check if message is repetitive"""
        if stream_id not in self.message_cache:
            return False
            
        user_messages = [
            msg for msg in self.message_cache[stream_id]
            if msg.user_id == user_id and 
            datetime.now(timezone.utc) - msg.timestamp < timedelta(minutes=5)
        ]
        
        # Check for exact duplicates
        duplicate_count = sum(1 for msg in user_messages if msg.content == content)
        if duplicate_count >= 3:
            return True
            
        # Check for similar messages (basic similarity)
        similar_count = sum(
            1 for msg in user_messages
            if self._message_similarity(content, msg.content) > 0.8
        )
        
        return similar_count >= 3
        
    def _message_similarity(self, msg1: str, msg2: str) -> float:
        """Calculate basic message similarity"""
        words1 = set(msg1.lower().split())
        words2 = set(msg2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
        
    async def _delete_message(self, stream_id: str, message_id: str):
        """Delete a chat message"""
        await self.redis.publish(
            f"moderation_events:{stream_id}",
            json.dumps({
                "type": "message_deleted",
                "message_id": message_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        )
        
    async def _warn_user(self, stream_id: str, user_id: str, violations: List[ViolationType]):
        """Send warning to user"""
        await self.redis.publish(
            f"moderation_events:{stream_id}",
            json.dumps({
                "type": "user_warned",
                "user_id": user_id,
                "violations": [v.value for v in violations],
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        )
        
    async def _shadowban_user(self, stream_id: str, user_id: str):
        """Shadowban a user"""
        user_history = await self._get_user_history(user_id, stream_id)
        user_history.is_shadowbanned = True
        user_history.shadowban_until = datetime.now(timezone.utc) + timedelta(hours=24)
        
        await self._update_user_moderation_record(user_history, stream_id)
        
    async def _cleanup_expired_bans(self):
        """Background task to clean up expired bans"""
        while self.is_running:
            try:
                for stream_id in self.active_streams.keys():
                    banned_users = await self.redis.hgetall(f"banned_users:{stream_id}")
                    
                    for user_id, ban_data in banned_users.items():
                        ban_info = json.loads(ban_data)
                        
                        if ban_info.get("banned_until"):
                            ban_until = datetime.fromisoformat(ban_info["banned_until"])
                            if datetime.now(timezone.utc) > ban_until:
                                await self.unban_user(stream_id, user_id)
                                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in cleanup expired bans: {str(e)}")
                await asyncio.sleep(60)
                
    async def _update_user_trust_scores(self):
        """Background task to update user trust scores"""
        while self.is_running:
            try:
                # Implementation would update trust scores based on behavior
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                logger.error(f"Error updating trust scores: {str(e)}")
                await asyncio.sleep(600)
                
    async def _message_analyzer(self):
        """Background task for advanced message analysis"""
        while self.is_running:
            try:
                # Implementation would perform advanced analysis
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in message analyzer: {str(e)}")
                await asyncio.sleep(30)


# Factory function for easy integration
def create_chat_moderator(redis_client: Any, db_session: Session) -> ChatModerator:
    """Create and return a configured ChatModerator instance"""
    return ChatModerator(redis_client, db_session)